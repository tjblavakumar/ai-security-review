from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Review, ReviewComment, Submission, SubmissionStatus, SubmissionResponse, Question, QuestionCategory
from app.schemas import ApproveRequest, ReturnRequest


def get_review_queue(db: Session) -> Sequence[Submission]:
    stmt = (
        select(Submission)
        .where(Submission.status.in_([SubmissionStatus.SUBMITTED, SubmissionStatus.IN_REVIEW, SubmissionStatus.RETURNED]))
        .order_by(Submission.submitted_at.desc())
    )
    return db.scalars(stmt).all()


def get_submission_for_review(db: Session, submission_id: int) -> Submission | None:
    stmt = (
        select(Submission)
        .options(
            joinedload(Submission.responses).joinedload(SubmissionResponse.question).joinedload(Question.category),
            joinedload(Submission.reviews).joinedload(Review.comments),
        )
        .where(Submission.id == submission_id)
    )
    return db.scalars(stmt).first()


def approve_submission(db: Session, submission_id: int, data: ApproveRequest) -> Review | None:
    submission = db.get(Submission, submission_id)
    if submission is None:
        return None

    review = Review(
        submission_id=submission_id,
        reviewer_name=data.reviewer_name,
        reviewer_email=data.reviewer_email,
        overall_comments=data.overall_comments,
        decision="approved",
    )
    db.add(review)
    submission.status = SubmissionStatus.APPROVED
    db.commit()
    db.refresh(review)
    return review


def return_submission(db: Session, submission_id: int, data: ReturnRequest) -> Review | None:
    submission = db.get(Submission, submission_id)
    if submission is None:
        return None

    review = Review(
        submission_id=submission_id,
        reviewer_name=data.reviewer_name,
        reviewer_email=data.reviewer_email,
        overall_comments=data.overall_comments,
        decision="returned",
    )
    db.add(review)
    db.flush()

    for comment_data in data.comments:
        comment = ReviewComment(
            review_id=review.id,
            question_id=comment_data.question_id,
            comment_text=comment_data.comment_text,
        )
        db.add(comment)

    submission.status = SubmissionStatus.RETURNED
    db.commit()
    db.refresh(review)
    return review
