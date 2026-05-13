from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Question, Submission, SubmissionResponse, SubmissionStatus
from app.schemas import SaveResponsesRequest, SubmissionCreate, SubmissionProgressOut
from app.services.question_service import get_applicable_questions


def create_submission(db: Session, data: SubmissionCreate) -> Submission:
    submission = Submission(**data.model_dump())
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def get_submission(db: Session, submission_id: int) -> Submission | None:
    stmt = (
        select(Submission)
        .options(joinedload(Submission.responses))
        .where(Submission.id == submission_id)
    )
    return db.scalars(stmt).first()


def list_submissions(db: Session, email: str | None = None, status: SubmissionStatus | None = None) -> Sequence[Submission]:
    stmt = select(Submission).options(joinedload(Submission.responses))
    if email:
        stmt = stmt.where(Submission.submitter_email == email)
    if status:
        stmt = stmt.where(Submission.status == status)
    stmt = stmt.order_by(Submission.updated_at.desc())
    return db.scalars(stmt).unique().all()


def save_responses(db: Session, submission_id: int, data: SaveResponsesRequest) -> Submission | None:
    submission = db.get(Submission, submission_id)
    if submission is None:
        return None

    for resp_data in data.responses:
        stmt = select(SubmissionResponse).where(
            SubmissionResponse.submission_id == submission_id,
            SubmissionResponse.question_id == resp_data.question_id,
        )
        existing = db.scalars(stmt).first()
        if existing:
            existing.response_value = resp_data.response_value
            existing.is_skipped = resp_data.is_skipped
            existing.updated_at = datetime.utcnow()
        else:
            new_resp = SubmissionResponse(
                submission_id=submission_id,
                question_id=resp_data.question_id,
                response_value=resp_data.response_value,
                is_skipped=resp_data.is_skipped,
            )
            db.add(new_resp)

    if data.current_step is not None:
        submission.current_step = data.current_step
    submission.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(submission)
    return submission


def submit_for_review(db: Session, submission_id: int) -> Submission | None:
    submission = db.get(Submission, submission_id)
    if submission is None:
        return None
    submission.status = SubmissionStatus.SUBMITTED
    submission.submitted_at = datetime.utcnow()
    submission.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(submission)
    return submission


def get_progress(db: Session, submission_id: int) -> SubmissionProgressOut | None:
    submission = get_submission(db, submission_id)
    if submission is None:
        return None

    applicable_questions = get_applicable_questions(db, list(submission.responses))
    total = len(applicable_questions)
    answered = 0
    response_map = {r.question_id: r for r in submission.responses}
    for q in applicable_questions:
        resp = response_map.get(q.id)
        if resp and resp.response_value and not resp.is_skipped:
            answered += 1

    return SubmissionProgressOut(
        submission_id=submission_id,
        total_questions=total,
        answered_questions=answered,
        progress_percent=round((answered / total * 100) if total > 0 else 0, 1),
        current_step=submission.current_step,
    )


def delete_submission(db: Session, submission_id: int) -> bool:
    """Delete a submission and all related data.
    
    Args:
        db: Database session
        submission_id: ID of the submission to delete
        
    Returns:
        True if deleted successfully, False if not found
    """
    from app.models.models import Notification
    
    submission = db.get(Submission, submission_id)
    if submission is None:
        return False
    
    # First, delete or nullify related notifications
    # (notifications table allows nullable submission_id)
    notifications = db.query(Notification).filter(
        Notification.submission_id == submission_id
    ).all()
    
    for notification in notifications:
        db.delete(notification)
    
    # Now delete the submission (cascade will handle responses, attachments, reviews)
    db.delete(submission)
    db.commit()
    return True
