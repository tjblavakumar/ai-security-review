import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ---------- Enums ----------

class QuestionType(str, enum.Enum):
    TEXT = "text"
    TEXTAREA = "textarea"
    YES_NO = "yes_no"
    SINGLE_SELECT = "single_select"
    MULTI_SELECT = "multi_select"


class SubmissionStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    RETURNED = "returned"
    APPROVED = "approved"


class ProjectType(str, enum.Enum):
    NEW = "new"
    MODIFICATION = "modification"
    THIRD_PARTY = "third-party"


class ConditionOperator(str, enum.Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    REGEX = "regex"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"


class NotificationType(str, enum.Enum):
    SUBMISSION_CREATED = "submission_created"
    SUBMISSION_SUBMITTED = "submission_submitted"
    SUBMISSION_RETURNED = "submission_returned"
    SUBMISSION_APPROVED = "submission_approved"


# ---------- Question domain ----------

class QuestionCategory(Base):
    __tablename__ = "question_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    questions: Mapped[list["Question"]] = relationship("Question", back_populates="category", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("question_categories.id"), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    question_type: Mapped[QuestionType] = mapped_column(Enum(QuestionType), nullable=False)
    options: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string for select types
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    allows_attachment: Mapped[bool] = mapped_column(Boolean, default=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    risk_weight: Mapped[int] = mapped_column(Integer, default=5)  # 1-10, default 5 (medium)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category: Mapped["QuestionCategory"] = relationship("QuestionCategory", back_populates="questions")
    conditions: Mapped[list["QuestionCondition"]] = relationship("QuestionCondition", back_populates="question", cascade="all, delete-orphan", foreign_keys="[QuestionCondition.question_id]")
    policy_links: Mapped[list["QuestionPolicyLink"]] = relationship("QuestionPolicyLink", back_populates="question", cascade="all, delete-orphan")
    responses: Mapped[list["SubmissionResponse"]] = relationship("SubmissionResponse", back_populates="question")


class QuestionCondition(Base):
    __tablename__ = "question_conditions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"), nullable=False)
    depends_on_question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"), nullable=False)
    operator: Mapped[str] = mapped_column(String(50), default="equals")
    expected_value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    question: Mapped["Question"] = relationship("Question", foreign_keys=[question_id], back_populates="conditions")
    depends_on_question: Mapped["Question"] = relationship("Question", foreign_keys=[depends_on_question_id])


class QuestionPolicyLink(Base):
    __tablename__ = "question_policy_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"), nullable=False)
    policy_document_id: Mapped[int] = mapped_column(Integer, ForeignKey("policy_documents.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    question: Mapped["Question"] = relationship("Question", back_populates="policy_links")
    policy_document: Mapped["PolicyDocument"] = relationship("PolicyDocument")


class QuestionnaireVersion(Base):
    __tablename__ = "questionnaire_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version_number: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


# ---------- Submission domain ----------

class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    project_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitter_name: Mapped[str] = mapped_column(String(255), nullable=False)
    submitter_email: Mapped[str] = mapped_column(String(255), nullable=False)
    team_department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_go_live_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    project_type: Mapped[ProjectType] = mapped_column(Enum(ProjectType), nullable=False)
    status: Mapped[SubmissionStatus] = mapped_column(Enum(SubmissionStatus), default=SubmissionStatus.DRAFT)
    current_step: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-100
    risk_level: Mapped[str | None] = mapped_column(String(20), nullable=True)  # low, medium, high, critical

    responses: Mapped[list["SubmissionResponse"]] = relationship("SubmissionResponse", back_populates="submission", cascade="all, delete-orphan")
    attachments: Mapped[list["SubmissionAttachment"]] = relationship("SubmissionAttachment", back_populates="submission", cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="submission", cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship("Notification", foreign_keys="[Notification.submission_id]", cascade="all, delete-orphan")


class SubmissionResponse(Base):
    __tablename__ = "submission_responses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = mapped_column(Integer, ForeignKey("submissions.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"), nullable=False)
    response_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_skipped: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    submission: Mapped["Submission"] = relationship("Submission", back_populates="responses")
    question: Mapped["Question"] = relationship("Question", back_populates="responses")


class SubmissionAttachment(Base):
    __tablename__ = "submission_attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = mapped_column(Integer, ForeignKey("submissions.id"), nullable=False)
    question_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("questions.id"), nullable=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    submission: Mapped["Submission"] = relationship("Submission", back_populates="attachments")


# ---------- Review domain ----------

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = mapped_column(Integer, ForeignKey("submissions.id"), nullable=False)
    reviewer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    reviewer_email: Mapped[str] = mapped_column(String(255), nullable=False)
    overall_comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision: Mapped[str] = mapped_column(String(50), nullable=False)  # "approved" or "returned"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    submission: Mapped["Submission"] = relationship("Submission", back_populates="reviews")
    comments: Mapped[list["ReviewComment"]] = relationship("ReviewComment", back_populates="review", cascade="all, delete-orphan")


class ReviewComment(Base):
    __tablename__ = "review_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    review_id: Mapped[int] = mapped_column(Integer, ForeignKey("reviews.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"), nullable=False)
    comment_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    review: Mapped["Review"] = relationship("Review", back_populates="comments")


# ---------- Policy domain ----------

class PolicyDocument(Base):
    __tablename__ = "policy_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tags: Mapped[list["DocumentTag"]] = relationship("DocumentTag", back_populates="document", cascade="all, delete-orphan")


class DocumentTag(Base):
    __tablename__ = "document_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("policy_documents.id"), nullable=False)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("master_tags.id"), nullable=False)

    document: Mapped["PolicyDocument"] = relationship("PolicyDocument", back_populates="tags")
    tag: Mapped["MasterTag"] = relationship("MasterTag")


class MasterTag(Base):
    __tablename__ = "master_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ---------- Risk Configuration domain ----------

class RiskRule(Base):
    __tablename__ = "risk_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    keywords: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array of keywords
    high_risk_answers: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array of high-risk answer patterns
    risk_value: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-10
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RiskThreshold(Base):
    __tablename__ = "risk_thresholds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)  # low, medium, high, critical
    min_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0-100
    max_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0-100
    color: Mapped[str] = mapped_column(String(50), nullable=False)  # hex color code
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ---------- Notification domain ----------

class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    notification_type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    submission_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("submissions.id"), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
