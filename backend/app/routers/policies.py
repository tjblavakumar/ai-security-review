"""Router for policy document management (Phase 2)."""

from __future__ import annotations

import io
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import DocumentTag, MasterTag, PolicyDocument
from app.services import rag_service

router = APIRouter(prefix="/api/policies", tags=["Policies"])


# ── Schemas ──────────────────────────────────────────────────────────

class PolicyDocumentCreate(BaseModel):
    title: str
    content: str | None = None
    version: str | None = None
    is_active: bool = True
    tags: list[str] = []


class PolicyDocumentUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    version: str | None = None
    is_active: bool | None = None
    tags: list[str] | None = None


class PolicyDocumentOut(BaseModel):
    id: int
    title: str
    content: str | None = None
    version: str | None = None
    is_active: bool
    created_at: str
    updated_at: str
    tags: list[str] = []
    chunk_count: int = 0

    class Config:
        from_attributes = True


class RAGSearchRequest(BaseModel):
    query: str
    top_k: int = 5


class RAGSearchResult(BaseModel):
    score: float
    chunk: str
    document_title: str
    document_id: int


# ── Helpers ──────────────────────────────────────────────────────────

def _get_or_create_tag(db: Session, name: str) -> MasterTag:
    tag = db.query(MasterTag).filter(MasterTag.name == name).first()
    if not tag:
        tag = MasterTag(name=name)
        db.add(tag)
        db.flush()
    return tag


def _sync_tags(db: Session, doc: PolicyDocument, tag_names: list[str]) -> None:
    # Remove existing
    db.query(DocumentTag).filter(DocumentTag.document_id == doc.id).delete()
    db.flush()
    # Add new
    for name in tag_names:
        master = _get_or_create_tag(db, name.strip())
        db.add(DocumentTag(document_id=doc.id, tag_id=master.id))
    db.flush()


def _doc_to_out(doc: PolicyDocument) -> dict[str, Any]:
    tags = [dt.tag.name for dt in doc.tags if dt.tag] if doc.tags else []
    stats = rag_service.get_index_stats()
    # Approx chunk count for this doc
    import os, json
    chunk_count = 0
    path = rag_service._index_path(doc.id)
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
            chunk_count = len(data.get("chunks", []))
    return {
        "id": doc.id,
        "title": doc.title,
        "content": doc.content,
        "version": doc.version,
        "is_active": doc.is_active,
        "created_at": doc.created_at.isoformat() if doc.created_at else "",
        "updated_at": doc.updated_at.isoformat() if doc.updated_at else "",
        "tags": tags,
        "chunk_count": chunk_count,
    }


# ── Endpoints ────────────────────────────────────────────────────────

@router.post("/upload", response_model=dict[str, Any])
async def upload_policy(
    file: UploadFile = File(...),
    title: str = Form(None),
    version: str = Form(None),
    tags: str = Form(""),
    db: Session = Depends(get_db)
):
    """Upload a PDF or text file and automatically extract content, index for RAG."""
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_ext = file.filename.lower().split('.')[-1]
    if file_ext not in ['pdf', 'txt', 'md']:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, TXT, and MD files are supported"
        )
    
    # Read file content
    content_bytes = await file.read()
    
    # Extract text based on file type
    if file_ext == 'pdf':
        try:
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content_bytes))
            content = ""
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract PDF content: {str(e)}"
            )
    else:
        # Text or markdown file
        try:
            content = content_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                content = content_bytes.decode('latin-1')
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to decode file: {str(e)}"
                )
    
    if not content.strip():
        raise HTTPException(
            status_code=400,
            detail="File appears to be empty or could not extract text"
        )
    
    # Use filename as title if not provided
    if not title:
        title = file.filename.rsplit('.', 1)[0]
    
    # Create policy document
    doc = PolicyDocument(
        title=title,
        content=content,
        version=version,
        is_active=True,
    )
    db.add(doc)
    db.flush()

    # Handle tags
    if tags:
        tag_list = [t.strip() for t in tags.split(',') if t.strip()]
        _sync_tags(db, doc, tag_list)

    db.commit()
    db.refresh(doc)

    # Index for RAG
    chunk_count = rag_service.ingest_policy_document(db, doc.id)

    return {
        "data": {
            **_doc_to_out(doc),
            "chunks_indexed": chunk_count,
        },
        "message": f"Policy uploaded and indexed ({chunk_count} chunks)",
        "success": True,
    }


@router.get("", response_model=dict[str, Any])
def list_policies(db: Session = Depends(get_db)):
    docs = db.query(PolicyDocument).order_by(PolicyDocument.title).all()
    return {
        "data": [_doc_to_out(d) for d in docs],
        "message": "OK",
        "success": True,
    }


@router.get("/{doc_id}", response_model=dict[str, Any])
def get_policy(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(PolicyDocument).filter(PolicyDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Policy document not found")
    return {"data": _doc_to_out(doc), "message": "OK", "success": True}


@router.post("", response_model=dict[str, Any])
def create_policy(body: PolicyDocumentCreate, db: Session = Depends(get_db)):
    doc = PolicyDocument(
        title=body.title,
        content=body.content,
        version=body.version,
        is_active=body.is_active,
    )
    db.add(doc)
    db.flush()

    if body.tags:
        _sync_tags(db, doc, body.tags)

    db.commit()
    db.refresh(doc)

    # Index for RAG
    if doc.content:
        rag_service.ingest_policy_document(db, doc.id)

    return {"data": _doc_to_out(doc), "message": "Policy created", "success": True}


@router.put("/{doc_id}", response_model=dict[str, Any])
def update_policy(doc_id: int, body: PolicyDocumentUpdate, db: Session = Depends(get_db)):
    doc = db.query(PolicyDocument).filter(PolicyDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Policy document not found")

    if body.title is not None:
        doc.title = body.title
    if body.content is not None:
        doc.content = body.content
    if body.version is not None:
        doc.version = body.version
    if body.is_active is not None:
        doc.is_active = body.is_active
    if body.tags is not None:
        _sync_tags(db, doc, body.tags)

    db.commit()
    db.refresh(doc)

    # Re-index
    rag_service.remove_index(doc_id)
    if doc.content and doc.is_active:
        rag_service.ingest_policy_document(db, doc.id)

    return {"data": _doc_to_out(doc), "message": "Policy updated", "success": True}


@router.delete("/{doc_id}", response_model=dict[str, Any])
def delete_policy(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(PolicyDocument).filter(PolicyDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Policy document not found")

    rag_service.remove_index(doc_id)
    db.delete(doc)
    db.commit()
    return {"data": None, "message": "Policy deleted", "success": True}


@router.post("/{doc_id}/index", response_model=dict[str, Any])
def index_policy(doc_id: int, db: Session = Depends(get_db)):
    """Manually trigger RAG indexing for a policy document."""
    doc = db.query(PolicyDocument).filter(PolicyDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Policy document not found")

    rag_service.remove_index(doc_id)
    count = rag_service.ingest_policy_document(db, doc.id)
    return {
        "data": {"chunks_indexed": count},
        "message": f"Indexed {count} chunks",
        "success": True,
    }


@router.post("/search", response_model=dict[str, Any])
def search_policies(body: RAGSearchRequest):
    """Search indexed policy documents via RAG."""
    results = rag_service.retrieve_context(body.query, top_k=body.top_k)
    return {"data": results, "message": "OK", "success": True}


@router.get("/index/stats", response_model=dict[str, Any])
def index_stats():
    """Return RAG index statistics."""
    stats = rag_service.get_index_stats()
    return {"data": stats, "message": "OK", "success": True}
