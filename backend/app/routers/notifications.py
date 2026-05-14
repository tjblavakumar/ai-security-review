from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ApiResponse, NotificationOut, UnreadCountOut
from app.services import notification_service

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=ApiResponse)
def get_notifications(email: str, db: Session = Depends(get_db)):
    notifications = notification_service.get_notifications(db, email)
    return ApiResponse(
        data=[NotificationOut.model_validate(n) for n in notifications],
        message="Notifications retrieved successfully",
    )


@router.patch("/{notification_id}/read", response_model=ApiResponse)
def mark_as_read(notification_id: int, db: Session = Depends(get_db)):
    notification = notification_service.mark_as_read(db, notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return ApiResponse(
        data=NotificationOut.model_validate(notification),
        message="Notification marked as read",
    )


@router.get("/unread-count", response_model=ApiResponse)
def get_unread_count(email: str, db: Session = Depends(get_db)):
    count = notification_service.get_unread_count(db, email)
    return ApiResponse(
        data=UnreadCountOut(count=count).model_dump(),
        message="Unread count retrieved successfully",
    )
