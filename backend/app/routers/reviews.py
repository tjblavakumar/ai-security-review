from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ApiResponse, ApproveRequest, ReturnRequest, ReviewOut, SubmissionDetailOut
from app.services import notification_service, review_service

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.get("/queue", response_model=ApiResponse)
def get_review_queue(db: Session = Depends(get_db)):
    submissions = review_service.get_review_queue(db)
    from app.schemas import SubmissionOut

    return ApiResponse(
        data=[SubmissionOut.model_validate(s) for s in submissions],
        message="Review queue retrieved successfully",
    )


@router.get("/submission/{submission_id}", response_model=ApiResponse)
def get_submission_for_review(submission_id: int, db: Session = Depends(get_db)):
    submission = review_service.get_submission_for_review(db, submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    return ApiResponse(
        data=SubmissionDetailOut.model_validate(submission),
        message="Submission retrieved for review",
    )


@router.post("/submission/{submission_id}/approve", response_model=ApiResponse)
def approve_submission(submission_id: int, data: ApproveRequest, db: Session = Depends(get_db)):
    review = review_service.approve_submission(db, submission_id, data)
    if review is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    submission = review_service.get_submission_for_review(db, submission_id)
    if submission:
        notification_service.notify_submission_approved(db, submission)
    return ApiResponse(
        data=ReviewOut.model_validate(review),
        message="Submission approved",
    )


@router.post("/submission/{submission_id}/return", response_model=ApiResponse)
def return_submission(submission_id: int, data: ReturnRequest, db: Session = Depends(get_db)):
    review = review_service.return_submission(db, submission_id, data)
    if review is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    submission = review_service.get_submission_for_review(db, submission_id)
    if submission:
        notification_service.notify_submission_returned(db, submission)
    return ApiResponse(
        data=ReviewOut.model_validate(review),
        message="Submission returned with comments",
    )
