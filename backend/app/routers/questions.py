from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    ApiResponse,
    BulkImportRequest,
    QuestionCategoryCreate,
    QuestionCategoryOut,
    QuestionConditionCreate,
    QuestionConditionOut,
    QuestionCreate,
    QuestionOut,
    QuestionUpdate,
    QuestionWithCategoryOut,
    ReorderRequest,
)
from app.services import question_service

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("", response_model=ApiResponse)
def list_questions(category_id: int | None = None, active_only: bool = False, db: Session = Depends(get_db)):
    questions = question_service.list_questions(db, category_id=category_id, active_only=active_only)
    return ApiResponse(
        data=[QuestionOut.model_validate(q) for q in questions],
        message="Questions retrieved successfully",
    )


@router.post("", response_model=ApiResponse, status_code=201)
def create_question(data: QuestionCreate, db: Session = Depends(get_db)):
    question = question_service.create_question(db, data)
    return ApiResponse(
        data=QuestionOut.model_validate(question),
        message="Question created successfully",
    )


@router.get("/preview", response_model=ApiResponse)
def preview_questions(db: Session = Depends(get_db)):
    questions = question_service.get_preview_questions(db)
    return ApiResponse(
        data=[QuestionWithCategoryOut.model_validate(q) for q in questions],
        message="Preview questions retrieved successfully",
    )


@router.get("/categories", response_model=ApiResponse)
def list_categories(db: Session = Depends(get_db)):
    categories = question_service.list_categories(db)
    return ApiResponse(
        data=[QuestionCategoryOut.model_validate(c) for c in categories],
        message="Categories retrieved successfully",
    )


@router.post("/categories", response_model=ApiResponse, status_code=201)
def create_category(data: QuestionCategoryCreate, db: Session = Depends(get_db)):
    category = question_service.create_category(db, data)
    return ApiResponse(
        data=QuestionCategoryOut.model_validate(category),
        message="Category created successfully",
    )


@router.get("/{question_id}", response_model=ApiResponse)
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = question_service.get_question(db, question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return ApiResponse(
        data=QuestionWithCategoryOut.model_validate(question),
        message="Question retrieved successfully",
    )


@router.put("/{question_id}", response_model=ApiResponse)
def update_question(question_id: int, data: QuestionUpdate, db: Session = Depends(get_db)):
    question = question_service.update_question(db, question_id, data)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return ApiResponse(
        data=QuestionOut.model_validate(question),
        message="Question updated successfully",
    )


@router.delete("/{question_id}", response_model=ApiResponse)
def delete_question(question_id: int, db: Session = Depends(get_db)):
    deleted = question_service.delete_question(db, question_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Question not found")
    return ApiResponse(message="Question deleted successfully")


@router.patch("/reorder", response_model=ApiResponse)
def reorder_questions(data: ReorderRequest, db: Session = Depends(get_db)):
    question_service.reorder_questions(db, data)
    return ApiResponse(message="Questions reordered successfully")


# ── Condition CRUD ───────────────────────────────────────────────────

@router.get("/{question_id}/conditions", response_model=ApiResponse)
def list_conditions(question_id: int, db: Session = Depends(get_db)):
    conditions = question_service.list_conditions(db, question_id)
    return ApiResponse(
        data=[QuestionConditionOut.model_validate(c) for c in conditions],
        message="Conditions retrieved",
    )


@router.post("/{question_id}/conditions", response_model=ApiResponse, status_code=201)
def add_condition(question_id: int, data: QuestionConditionCreate, db: Session = Depends(get_db)):
    condition = question_service.add_condition(db, question_id, data)
    return ApiResponse(
        data=QuestionConditionOut.model_validate(condition),
        message="Condition added",
    )


@router.put("/{question_id}/conditions", response_model=ApiResponse)
def replace_conditions(question_id: int, data: list[QuestionConditionCreate], db: Session = Depends(get_db)):
    """Replace all conditions for a question (used by the visual builder)."""
    conditions = question_service.replace_conditions(db, question_id, data)
    return ApiResponse(
        data=[QuestionConditionOut.model_validate(c) for c in conditions],
        message="Conditions replaced",
    )


@router.delete("/conditions/{condition_id}", response_model=ApiResponse)
def delete_condition(condition_id: int, db: Session = Depends(get_db)):
    deleted = question_service.delete_condition(db, condition_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Condition not found")
    return ApiResponse(message="Condition deleted")


# ── Bulk Import/Export ───────────────────────────────────────────────

@router.get("/bulk/export", response_model=ApiResponse)
def export_questions(db: Session = Depends(get_db)):
    data = question_service.export_questions(db)
    return ApiResponse(data=data, message=f"Exported {len(data)} questions")


@router.post("/bulk/import", response_model=ApiResponse)
def import_questions(data: BulkImportRequest, db: Session = Depends(get_db)):
    result = question_service.import_questions(db, data)
    return ApiResponse(
        data=result,
        message=f"Imported {result['created']} questions",
    )
