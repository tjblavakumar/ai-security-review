from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Notification, NotificationType, Submission


def create_notification(
    db: Session,
    recipient_email: str,
    notification_type: NotificationType,
    title: str,
    message: str,
    submission_id: int | None = None,
) -> Notification:
    notification = Notification(
        recipient_email=recipient_email,
        notification_type=notification_type,
        title=title,
        message=message,
        submission_id=submission_id,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_notifications(db: Session, email: str) -> Sequence[Notification]:
    stmt = (
        select(Notification)
        .where(Notification.recipient_email == email)
        .order_by(Notification.created_at.desc())
    )
    return db.scalars(stmt).all()


def mark_as_read(db: Session, notification_id: int) -> Notification | None:
    notification = db.get(Notification, notification_id)
    if notification is None:
        return None
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


def get_unread_count(db: Session, email: str) -> int:
    stmt = (
        select(func.count())
        .select_from(Notification)
        .where(Notification.recipient_email == email, Notification.is_read.is_(False))
    )
    result = db.execute(stmt).scalar()
    return result or 0


def notify_submission_created(db: Session, submission: Submission) -> None:
    create_notification(
        db=db,
        recipient_email=submission.submitter_email,
        notification_type=NotificationType.SUBMISSION_CREATED,
        title="Submission Created",
        message=f'Your submission "{submission.project_name}" has been created.',
        submission_id=submission.id,
    )


def notify_submission_submitted(db: Session, submission: Submission) -> None:
    create_notification(
        db=db,
        recipient_email=submission.submitter_email,
        notification_type=NotificationType.SUBMISSION_SUBMITTED,
        title="Submission Sent for Review",
        message=f'Your submission "{submission.project_name}" has been sent for review.',
        submission_id=submission.id,
    )


def notify_submission_returned(db: Session, submission: Submission) -> None:
    create_notification(
        db=db,
        recipient_email=submission.submitter_email,
        notification_type=NotificationType.SUBMISSION_RETURNED,
        title="Submission Returned",
        message=f'Your submission "{submission.project_name}" has been returned with comments. Please revise and resubmit.',
        submission_id=submission.id,
    )


def notify_submission_approved(db: Session, submission: Submission) -> None:
    create_notification(
        db=db,
        recipient_email=submission.submitter_email,
        notification_type=NotificationType.SUBMISSION_APPROVED,
        title="Submission Approved",
        message=f'Your submission "{submission.project_name}" has been approved!',
        submission_id=submission.id,
    )
