"""Lightweight RAG service — chunks policy documents, generates embeddings
via multiple LLM providers (OpenAI, LiteLLM, Bedrock), stores them in local files,
and retrieves relevant context using cosine similarity (numpy/sklearn, no external vector DB)."""

from __future__ import annotations

import json
import os
from typing import Any

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from app.config import settings
from app.models.models import PolicyDocument
from app.services.llm_factory import get_llm_provider, is_llm_configured

EMBEDDINGS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "embeddings",
)


# ── Chunking ─────────────────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    """Split *text* into overlapping chunks by character count."""
    chunk_size = chunk_size or settings.RAG_CHUNK_SIZE
    overlap = overlap or settings.RAG_CHUNK_OVERLAP
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


# ── Embedding helpers ────────────────────────────────────────────────

def _embed_texts(texts: list[str]) -> list[list[float]]:
    provider = get_llm_provider()
    return provider.get_embeddings(texts)


def _index_path(doc_id: int) -> str:
    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
    return os.path.join(EMBEDDINGS_DIR, f"doc_{doc_id}.json")


def index_document(doc_id: int, title: str, content: str) -> int:
    """Chunk and embed a policy document, persisting to disk.
    Returns number of chunks created."""
    if not is_llm_configured() or not content:
        return 0

    chunks = chunk_text(content)
    if not chunks:
        return 0

    embeddings = _embed_texts(chunks)
    index_data = {
        "doc_id": doc_id,
        "title": title,
        "chunks": chunks,
        "embeddings": embeddings,
    }
    with open(_index_path(doc_id), "w") as f:
        json.dump(index_data, f)

    return len(chunks)


def remove_index(doc_id: int) -> None:
    path = _index_path(doc_id)
    if os.path.exists(path):
        os.remove(path)


def _load_all_indices() -> list[dict[str, Any]]:
    """Load every indexed document from disk."""
    if not os.path.isdir(EMBEDDINGS_DIR):
        return []
    indices: list[dict[str, Any]] = []
    for fname in os.listdir(EMBEDDINGS_DIR):
        if fname.endswith(".json"):
            with open(os.path.join(EMBEDDINGS_DIR, fname)) as f:
                indices.append(json.load(f))
    return indices


# ── Retrieval ────────────────────────────────────────────────────────

def retrieve_context(query: str, top_k: int | None = None) -> list[dict[str, Any]]:
    """Return the top-k most relevant chunks for *query*."""
    if not is_llm_configured():
        return []
    top_k = top_k or settings.RAG_TOP_K

    indices = _load_all_indices()
    if not indices:
        return []

    query_emb = np.array(_embed_texts([query])[0]).reshape(1, -1)

    scored: list[tuple[float, str, str, int]] = []
    for idx in indices:
        if not idx.get("embeddings"):
            continue
        emb_matrix = np.array(idx["embeddings"])
        sims = cosine_similarity(query_emb, emb_matrix)[0]
        for i, sim in enumerate(sims):
            scored.append((float(sim), idx["chunks"][i], idx["title"], idx["doc_id"]))

    scored.sort(key=lambda x: x[0], reverse=True)
    results: list[dict[str, Any]] = []
    for sim, chunk, title, doc_id in scored[:top_k]:
        results.append({
            "score": round(sim, 4),
            "chunk": chunk,
            "document_title": title,
            "document_id": doc_id,
        })
    return results


def get_policy_context_for_question(question_text: str, category_name: str) -> str:
    """Convenience wrapper — builds a context string for the AI suggestion service."""
    query = f"{category_name}: {question_text}"
    results = retrieve_context(query, top_k=3)
    if not results:
        return ""
    parts: list[str] = []
    for r in results:
        parts.append(f"[{r['document_title']}] (relevance {r['score']})\n{r['chunk']}")
    return "\n---\n".join(parts)


# ── Admin helpers ────────────────────────────────────────────────────

def ingest_policy_document(db: Session, doc_id: int) -> int:
    """Index an existing PolicyDocument by its DB id. Returns chunk count."""
    doc = db.query(PolicyDocument).filter(PolicyDocument.id == doc_id).first()
    if not doc or not doc.content:
        return 0
    return index_document(doc.id, doc.title, doc.content)


def get_index_stats() -> dict[str, Any]:
    """Return basic statistics about the RAG index."""
    indices = _load_all_indices()
    total_chunks = sum(len(idx.get("chunks", [])) for idx in indices)
    return {
        "indexed_documents": len(indices),
        "total_chunks": total_chunks,
    }
