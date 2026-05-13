from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import SubmissionStatus
from app.schemas import (
    ApiResponse,
    SaveResponsesRequest,
    SubmissionCreate,
    SubmissionDetailOut,
    SubmissionOut,
    SubmissionProgressOut,
    SubmissionResponseOut,
)
from app.services import notification_service, submission_service

router = APIRouter(prefix="/api/submissions", tags=["submissions"])


@router.get("", response_model=ApiResponse)
def list_submissions(email: str | None = None, status: SubmissionStatus | None = None, db: Session = Depends(get_db)):
    submissions = submission_service.list_submissions(db, email=email, status=status)
    return ApiResponse(
        data=[SubmissionOut.model_validate(s) for s in submissions],
        message="Submissions retrieved successfully",
    )


@router.post("", response_model=ApiResponse, status_code=201)
def create_submission(data: SubmissionCreate, db: Session = Depends(get_db)):
    submission = submission_service.create_submission(db, data)
    notification_service.notify_submission_created(db, submission)
    return ApiResponse(
        data=SubmissionOut.model_validate(submission),
        message="Submission created successfully",
    )


@router.get("/{submission_id}", response_model=ApiResponse)
def get_submission(submission_id: int, db: Session = Depends(get_db)):
    submission = submission_service.get_submission(db, submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    return ApiResponse(
        data=SubmissionDetailOut.model_validate(submission),
        message="Submission retrieved successfully",
    )


@router.post("/{submission_id}/responses", response_model=ApiResponse)
def save_responses(submission_id: int, data: SaveResponsesRequest, db: Session = Depends(get_db)):
    submission = submission_service.save_responses(db, submission_id, data)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    return ApiResponse(
        data=SubmissionDetailOut.model_validate(submission),
        message="Responses saved successfully",
    )


@router.post("/{submission_id}/submit", response_model=ApiResponse)
def submit_for_review(submission_id: int, db: Session = Depends(get_db)):
    submission = submission_service.submit_for_review(db, submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    notification_service.notify_submission_submitted(db, submission)
    return ApiResponse(
        data=SubmissionOut.model_validate(submission),
        message="Submission sent for review",
    )


@router.get("/{submission_id}/progress", response_model=ApiResponse)
def get_progress(submission_id: int, db: Session = Depends(get_db)):
    progress = submission_service.get_progress(db, submission_id)
    if progress is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    return ApiResponse(data=progress.model_dump(), message="Progress retrieved successfully")


@router.delete("/{submission_id}", response_model=ApiResponse)
def delete_submission(submission_id: int, db: Session = Depends(get_db)):
    """Delete a submission. Only allows deletion of draft and returned submissions."""
    submission = submission_service.get_submission(db, submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Only allow deletion of draft and returned submissions
    if submission.status not in [SubmissionStatus.DRAFT, SubmissionStatus.RETURNED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete submission with status '{submission.status.value}'. Only draft and returned submissions can be deleted."
        )
    
    # Delete the submission (cascade will handle related data)
    success = submission_service.delete_submission(db, submission_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete submission")
    
    return ApiResponse(
        data={"deleted": True, "submission_id": submission_id},
        message="Submission deleted successfully"
    )
