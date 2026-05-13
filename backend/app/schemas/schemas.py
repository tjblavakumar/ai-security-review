from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.models import (
    ConditionOperator,
    NotificationType,
    ProjectType,
    QuestionType,
    SubmissionStatus,
)


# ---------- Generic response wrapper ----------

class ApiResponse(BaseModel):
    data: object | None = None
    message: str = ""
    success: bool = True


# ---------- Question Category ----------

class QuestionCategoryCreate(BaseModel):
    name: str
    description: str | None = None
    display_order: int = 0
    is_active: bool = True


class QuestionCategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ---------- Question ----------

class QuestionCreate(BaseModel):
    category_id: int
    question_text: str
    description: str | None = None
    question_type: QuestionType
    options: str | None = None
    is_required: bool = True
    is_active: bool = True
    allows_attachment: bool = False
    display_order: int = 0


class QuestionUpdate(BaseModel):
    category_id: int | None = None
    question_text: str | None = None
    description: str | None = None
    question_type: QuestionType | None = None
    options: str | None = None
    is_required: bool | None = None
    is_active: bool | None = None
    allows_attachment: bool | None = None
    display_order: int | None = None


class QuestionConditionCreate(BaseModel):
    depends_on_question_id: int
    operator: str = "equals"
    expected_value: str = ""


class QuestionConditionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_id: int
    depends_on_question_id: int
    operator: str
    expected_value: str


class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    question_text: str
    description: str | None = None
    question_type: QuestionType
    options: str | None = None
    is_required: bool
    is_active: bool
    allows_attachment: bool
    display_order: int
    created_at: datetime
    updated_at: datetime
    conditions: list[QuestionConditionOut] = []


class QuestionWithCategoryOut(QuestionOut):
    category: QuestionCategoryOut


class ReorderItem(BaseModel):
    id: int
    display_order: int


class ReorderRequest(BaseModel):
    items: list[ReorderItem]


# ---------- Submission ----------

class SubmissionCreate(BaseModel):
    project_name: str
    project_description: str | None = None
    submitter_name: str
    submitter_email: str
    team_department: str | None = None
    target_go_live_date: str | None = None
    project_type: ProjectType


class SubmissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_name: str
    project_description: str | None = None
    submitter_name: str
    submitter_email: str
    team_department: str | None = None
    target_go_live_date: str | None = None
    project_type: ProjectType
    status: SubmissionStatus
    current_step: int
    created_at: datetime
    updated_at: datetime
    submitted_at: datetime | None = None


class SubmissionResponseCreate(BaseModel):
    question_id: int
    response_value: str | None = None
    is_skipped: bool = False


class SubmissionResponseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    submission_id: int
    question_id: int
    response_value: str | None = None
    is_skipped: bool
    created_at: datetime
    updated_at: datetime


class SubmissionDetailOut(SubmissionOut):
    responses: list[SubmissionResponseOut] = []


class SubmissionProgressOut(BaseModel):
    submission_id: int
    total_questions: int
    answered_questions: int
    progress_percent: float
    current_step: int


class SaveResponsesRequest(BaseModel):
    responses: list[SubmissionResponseCreate]
    current_step: int | None = None


# ---------- Review ----------

class ReviewCommentCreate(BaseModel):
    question_id: int
    comment_text: str


class ReviewCommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    review_id: int
    question_id: int
    comment_text: str
    created_at: datetime


class ApproveRequest(BaseModel):
    reviewer_name: str
    reviewer_email: str
    overall_comments: str | None = None


class ReturnRequest(BaseModel):
    reviewer_name: str
    reviewer_email: str
    overall_comments: str | None = None
    comments: list[ReviewCommentCreate] = []


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    submission_id: int
    reviewer_name: str
    reviewer_email: str
    overall_comments: str | None = None
    decision: str
    created_at: datetime
    comments: list[ReviewCommentOut] = []


# ---------- Notification ----------

class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recipient_email: str
    notification_type: NotificationType
    title: str
    message: str
    submission_id: int | None = None
    is_read: bool
    created_at: datetime


class UnreadCountOut(BaseModel):
    count: int


# ---------- Bulk Import/Export ----------

class QuestionExport(BaseModel):
    question_text: str
    description: str | None = None
    category_name: str
    question_type: QuestionType
    options: str | None = None
    is_required: bool = True
    is_active: bool = True
    allows_attachment: bool = False
    display_order: int = 0
    conditions: list[dict] = []


class BulkImportRequest(BaseModel):
    questions: list[QuestionExport]
    overwrite: bool = False
