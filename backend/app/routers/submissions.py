from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import os
from pathlib import Path

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
from app.services.document_service import extract_text_from_file

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


@router.post("/{submission_id}/upload-document", response_model=ApiResponse)
async def upload_document(submission_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a document (PDF or TXT) for a submission and extract its content."""
    print(f"[DEBUG] Upload document request for submission {submission_id}")
    print(f"[DEBUG] File: {file.filename}, Type: {file.content_type}")
    
    submission = submission_service.get_submission(db, submission_id)
    if submission is None:
        print(f"[ERROR] Submission {submission_id} not found")
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Validate file type
    allowed_types = ["application/pdf", "text/plain"]
    print(f"[DEBUG] Validating file type: {file.content_type}")
    if file.content_type not in allowed_types:
        print(f"[ERROR] Invalid file type: {file.content_type}")
        raise HTTPException(
            status_code=400,
            detail=f"Only PDF and TXT files are allowed. Got: {file.content_type}"
        )
    
    # Create uploads directory if it doesn't exist
    upload_dir = Path("uploads/submissions")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = upload_dir / f"{submission_id}_{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Extract text from file
    print(f"[DEBUG] Extracting text from: {file_path}")
    try:
        extracted_text = extract_text_from_file(str(file_path), file.content_type)
        print(f"[DEBUG] Extracted {len(extracted_text)} characters")
    except Exception as e:
        print(f"[ERROR] Text extraction failed: {str(e)}")
        # Clean up file if extraction fails
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {str(e)}")
    
    # Update submission with document info
    print(f"[DEBUG] Updating submission with document info")
    submission.uploaded_document_path = str(file_path)
    submission.uploaded_document_name = file.filename
    submission.uploaded_document_content = extracted_text
    db.commit()
    db.refresh(submission)
    
    print(f"[SUCCESS] Document uploaded successfully for submission {submission_id}")
    return ApiResponse(
        data=SubmissionOut.model_validate(submission),
        message="Document uploaded and processed successfully"
    )
