"""Router for AI suggestion & chat endpoints (Phase 2)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import (
    Question,
    QuestionCategory,
    Submission,
    SubmissionResponse,
)
from app.services import ai_service, rag_service

router = APIRouter(prefix="/api/ai", tags=["AI"])


# ── Schemas ──────────────────────────────────────────────────────────

class SuggestionRequest(BaseModel):
    question_id: int
    submission_id: int | None = None


class SuggestionResponse(BaseModel):
    suggestion: str = ""
    explanation: str = ""
    confidence: str = "low"
    policy_references: list[str] = []
    enabled: bool = False


class ChatMessageIn(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessageIn]
    question_id: int | None = None
    submission_id: int | None = None


class ChatResponse(BaseModel):
    reply: str


class AIStatusResponse(BaseModel):
    enabled: bool
    provider: str
    model: str
    embedding_model: str
    rag_indexed_documents: int
    rag_total_chunks: int


# ── Endpoints ────────────────────────────────────────────────────────

@router.post("/suggest", response_model=dict[str, Any])
def get_suggestion(
    body: SuggestionRequest,
    db: Session = Depends(get_db),
):
    """Generate an AI suggestion for a specific question."""
    question = db.query(Question).filter(Question.id == body.question_id).first()
    if not question:
        return {"data": None, "message": "Question not found", "success": False}

    category = db.query(QuestionCategory).filter(
        QuestionCategory.id == question.category_id
    ).first()
    category_name = category.name if category else "General"

    # Gather prior responses for context
    previous: list[dict[str, Any]] = []
    document_context: str | None = None
    if body.submission_id:
        # Get submission to access uploaded document
        submission = db.query(Submission).filter(Submission.id == body.submission_id).first()
        if submission and submission.uploaded_document_content:
            # Truncate document if too long (keep first 4000 chars)
            doc_content = submission.uploaded_document_content
            if len(doc_content) > 4000:
                doc_content = doc_content[:4000] + "\n\n... (document truncated)"
            document_context = f"Project Document ({submission.uploaded_document_name}):\n{doc_content}"
        
        rows = (
            db.query(SubmissionResponse, Question)
            .join(Question, SubmissionResponse.question_id == Question.id)
            .filter(
                SubmissionResponse.submission_id == body.submission_id,
                SubmissionResponse.response_value.isnot(None),
                SubmissionResponse.response_value != "",
            )
            .all()
        )
        for resp, q in rows:
            previous.append({
                "question_text": q.question_text,
                "response_value": resp.response_value,
            })

    # RAG policy context
    policy_context = rag_service.get_policy_context_for_question(
        question.question_text, category_name
    )

    result = ai_service.generate_suggestion(
        question_text=question.question_text,
        question_type=question.question_type.value,
        question_options=question.options,
        category_name=category_name,
        description=question.description,
        previous_responses=previous,
        policy_context=policy_context or None,
        document_context=document_context,
    )

    return {"data": result, "message": "OK", "success": True}


@router.post("/chat", response_model=dict[str, Any])
def chat(
    body: ChatRequest,
    db: Session = Depends(get_db),
):
    """Conversational chat endpoint for the AI assistant panel."""
    question_context: str | None = None
    if body.question_id:
        question = db.query(Question).filter(Question.id == body.question_id).first()
        if question:
            category = db.query(QuestionCategory).filter(
                QuestionCategory.id == question.category_id
            ).first()
            parts = [f"Question: {question.question_text}"]
            if question.description:
                parts.append(f"Description: {question.description}")
            if category:
                parts.append(f"Category: {category.name}")
            question_context = "\n".join(parts)

    policy_context: str | None = None
    if question_context:
        q = db.query(Question).filter(Question.id == body.question_id).first()
        if q:
            cat = db.query(QuestionCategory).filter(
                QuestionCategory.id == q.category_id
            ).first()
            policy_context = rag_service.get_policy_context_for_question(
                q.question_text, cat.name if cat else "General"
            ) or None

    messages = [{"role": m.role, "content": m.content} for m in body.messages]

    reply = ai_service.chat_completion(
        messages=messages,
        question_context=question_context,
        policy_context=policy_context,
    )

    return {"data": {"reply": reply}, "message": "OK", "success": True}


@router.get("/status", response_model=dict[str, Any])
def ai_status():
    """Return AI feature configuration status."""
    from app.config import settings as cfg
    from app.services.llm_factory import is_llm_configured, get_llm_provider

    stats = rag_service.get_index_stats()
    
    # Determine model and embedding model based on provider
    provider = cfg.LLM_PROVIDER.lower()
    if provider == "openai":
        model = cfg.OPENAI_MODEL
        embedding_model = cfg.OPENAI_EMBEDDING_MODEL
    elif provider == "litellm":
        model = cfg.LITELLM_MODEL_ID
        embedding_model = cfg.LITELLM_EMBEDDING_MODEL
    elif provider == "bedrock":
        model = cfg.BEDROCK_MODEL_ID
        embedding_model = cfg.BEDROCK_EMBEDDING_MODEL_ID
    else:
        model = "unknown"
        embedding_model = "unknown"
    
    return {
        "data": {
            "enabled": is_llm_configured(),
            "provider": cfg.LLM_PROVIDER,
            "model": model,
            "embedding_model": embedding_model,
            "rag_indexed_documents": stats["indexed_documents"],
            "rag_total_chunks": stats["total_chunks"],
        },
        "message": "OK",
        "success": True,
    }
