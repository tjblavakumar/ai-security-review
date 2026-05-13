import json
import re
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Question, QuestionCategory, QuestionCondition, SubmissionResponse
from app.schemas import (
    BulkImportRequest,
    QuestionCategoryCreate,
    QuestionConditionCreate,
    QuestionCreate,
    QuestionExport,
    QuestionUpdate,
    ReorderRequest,
)


# ── Category CRUD ────────────────────────────────────────────────────

def list_categories(db: Session) -> Sequence[QuestionCategory]:
    stmt = select(QuestionCategory).order_by(QuestionCategory.display_order)
    return db.scalars(stmt).all()


def create_category(db: Session, data: QuestionCategoryCreate) -> QuestionCategory:
    category = QuestionCategory(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


# ── Question CRUD ────────────────────────────────────────────────────

def list_questions(db: Session, category_id: int | None = None, active_only: bool = False) -> Sequence[Question]:
    stmt = select(Question).options(joinedload(Question.conditions), joinedload(Question.category))
    if category_id is not None:
        stmt = stmt.where(Question.category_id == category_id)
    if active_only:
        stmt = stmt.where(Question.is_active.is_(True))
    stmt = stmt.order_by(Question.display_order)
    return db.scalars(stmt).unique().all()


def get_question(db: Session, question_id: int) -> Question | None:
    stmt = select(Question).options(joinedload(Question.conditions), joinedload(Question.category)).where(Question.id == question_id)
    return db.scalars(stmt).first()


def create_question(db: Session, data: QuestionCreate) -> Question:
    question = Question(**data.model_dump())
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def update_question(db: Session, question_id: int, data: QuestionUpdate) -> Question | None:
    question = db.get(Question, question_id)
    if question is None:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(question, key, value)
    db.commit()
    db.refresh(question)
    return question


def delete_question(db: Session, question_id: int) -> bool:
    question = db.get(Question, question_id)
    if question is None:
        return False
    db.delete(question)
    db.commit()
    return True


def reorder_questions(db: Session, data: ReorderRequest) -> bool:
    for item in data.items:
        question = db.get(Question, item.id)
        if question is not None:
            question.display_order = item.display_order
    db.commit()
    return True


def get_preview_questions(db: Session) -> list[Question]:
    stmt = (
        select(Question)
        .options(joinedload(Question.conditions), joinedload(Question.category))
        .where(Question.is_active.is_(True))
        .order_by(Question.display_order)
    )
    return list(db.scalars(stmt).unique().all())


# ── Condition CRUD ───────────────────────────────────────────────────

def list_conditions(db: Session, question_id: int) -> list[QuestionCondition]:
    stmt = select(QuestionCondition).where(QuestionCondition.question_id == question_id)
    return list(db.scalars(stmt).all())


def add_condition(db: Session, question_id: int, data: QuestionConditionCreate) -> QuestionCondition:
    condition = QuestionCondition(
        question_id=question_id,
        depends_on_question_id=data.depends_on_question_id,
        operator=data.operator,
        expected_value=data.expected_value,
    )
    db.add(condition)
    db.commit()
    db.refresh(condition)
    return condition


def update_condition(db: Session, condition_id: int, data: QuestionConditionCreate) -> QuestionCondition | None:
    condition = db.get(QuestionCondition, condition_id)
    if condition is None:
        return None
    condition.depends_on_question_id = data.depends_on_question_id
    condition.operator = data.operator
    condition.expected_value = data.expected_value
    db.commit()
    db.refresh(condition)
    return condition


def delete_condition(db: Session, condition_id: int) -> bool:
    condition = db.get(QuestionCondition, condition_id)
    if condition is None:
        return False
    db.delete(condition)
    db.commit()
    return True


def replace_conditions(db: Session, question_id: int, conditions: list[QuestionConditionCreate]) -> list[QuestionCondition]:
    """Delete all existing conditions for a question and create new ones."""
    db.query(QuestionCondition).filter(QuestionCondition.question_id == question_id).delete()
    db.flush()
    result: list[QuestionCondition] = []
    for data in conditions:
        cond = QuestionCondition(
            question_id=question_id,
            depends_on_question_id=data.depends_on_question_id,
            operator=data.operator,
            expected_value=data.expected_value,
        )
        db.add(cond)
        result.append(cond)
    db.commit()
    for c in result:
        db.refresh(c)
    return result


# ── Advanced condition evaluation ────────────────────────────────────

def _evaluate_single_condition(answer: str | None, operator: str, expected: str) -> bool:
    if operator == "is_empty":
        return not answer or answer.strip() == ""
    if operator == "is_not_empty":
        return bool(answer and answer.strip())

    if answer is None:
        return False

    a = answer.strip().lower()
    e = expected.strip().lower()

    if operator == "equals":
        return a == e
    elif operator == "not_equals":
        return a != e
    elif operator == "contains":
        return e in a
    elif operator == "not_contains":
        return e not in a
    elif operator == "greater_than":
        try:
            return float(a) > float(e)
        except ValueError:
            return a > e
    elif operator == "less_than":
        try:
            return float(a) < float(e)
        except ValueError:
            return a < e
    elif operator == "regex":
        try:
            return bool(re.search(expected.strip(), answer.strip(), re.IGNORECASE))
        except re.error:
            return False
    return a == e


def evaluate_conditions(question: Question, responses: dict[int, str | None]) -> bool:
    if not question.conditions:
        return True
    for condition in question.conditions:
        answer = responses.get(condition.depends_on_question_id)
        op = getattr(condition, "operator", "equals") or "equals"
        if not _evaluate_single_condition(answer, op, condition.expected_value):
            return False
    return True


def get_applicable_questions(db: Session, submission_responses: list[SubmissionResponse]) -> list[Question]:
    all_questions = get_preview_questions(db)
    response_map: dict[int, str | None] = {r.question_id: r.response_value for r in submission_responses}
    applicable: list[Question] = []
    for q in all_questions:
        if evaluate_conditions(q, response_map):
            applicable.append(q)
    return applicable


# ── Bulk export / import ─────────────────────────────────────────────

def export_questions(db: Session) -> list[dict]:
    questions = list_questions(db)
    categories = {c.id: c.name for c in list_categories(db)}
    result: list[dict] = []
    for q in questions:
        conditions = []
        for c in q.conditions:
            conditions.append({
                "depends_on_question_id": c.depends_on_question_id,
                "operator": getattr(c, "operator", "equals") or "equals",
                "expected_value": c.expected_value,
            })
        result.append({
            "question_text": q.question_text,
            "description": q.description,
            "category_name": categories.get(q.category_id, "Unknown"),
            "question_type": q.question_type.value,
            "options": q.options,
            "is_required": q.is_required,
            "is_active": q.is_active,
            "allows_attachment": q.allows_attachment,
            "display_order": q.display_order,
            "conditions": conditions,
        })
    return result


def import_questions(db: Session, data: BulkImportRequest) -> dict:
    """Import questions from a bulk payload. If overwrite=True, deletes all existing questions first."""
    if data.overwrite:
        db.query(QuestionCondition).delete()
        db.query(Question).delete()
        db.flush()

    # Ensure categories exist
    cat_map: dict[str, int] = {}
    existing_cats = list_categories(db)
    for c in existing_cats:
        cat_map[c.name.lower()] = c.id

    created = 0
    skipped = 0
    for qdata in data.questions:
        cat_key = qdata.category_name.lower()
        if cat_key not in cat_map:
            new_cat = QuestionCategory(
                name=qdata.category_name,
                display_order=len(cat_map) + 1,
            )
            db.add(new_cat)
            db.flush()
            cat_map[cat_key] = new_cat.id

        q = Question(
            category_id=cat_map[cat_key],
            question_text=qdata.question_text,
            description=qdata.description,
            question_type=qdata.question_type,
            options=qdata.options,
            is_required=qdata.is_required,
            is_active=qdata.is_active,
            allows_attachment=qdata.allows_attachment,
            display_order=qdata.display_order,
        )
        db.add(q)
        db.flush()

        # Note: conditions referencing question IDs from the import payload
        # require the caller to use the new IDs after import. We skip conditions
        # that reference unknown IDs for now.
        created += 1

    db.commit()
    return {"created": created, "skipped": skipped}
