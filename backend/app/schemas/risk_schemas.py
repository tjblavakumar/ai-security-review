"""Schemas for risk configuration"""

from pydantic import BaseModel, Field


class RiskRuleBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = None
    keywords: list[str] = Field(..., min_length=1)
    high_risk_answers: list[str] = Field(..., min_length=1)
    risk_value: int = Field(..., ge=1, le=10)
    is_active: bool = True


class RiskRuleCreate(RiskRuleBase):
    pass


class RiskRuleUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    description: str | None = None
    keywords: list[str] | None = None
    high_risk_answers: list[str] | None = None
    risk_value: int | None = Field(None, ge=1, le=10)
    is_active: bool | None = None


class RiskRuleOut(RiskRuleBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class RiskThresholdBase(BaseModel):
    level: str = Field(..., max_length=20)
    min_score: float = Field(..., ge=0, le=100)
    max_score: float = Field(..., ge=0, le=100)
    color: str = Field(..., max_length=50)
    display_order: int = 0


class RiskThresholdCreate(RiskThresholdBase):
    pass


class RiskThresholdUpdate(BaseModel):
    level: str | None = Field(None, max_length=20)
    min_score: float | None = Field(None, ge=0, le=100)
    max_score: float | None = Field(None, ge=0, le=100)
    color: str | None = Field(None, max_length=50)
    display_order: int | None = None


class RiskThresholdOut(RiskThresholdBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class QuestionRiskWeightUpdate(BaseModel):
    question_id: int
    risk_weight: int = Field(..., ge=1, le=10)


class BulkQuestionRiskWeightUpdate(BaseModel):
    updates: list[QuestionRiskWeightUpdate]


class RiskConfigSummary(BaseModel):
    total_rules: int
    active_rules: int
    thresholds: list[RiskThresholdOut]
    average_question_weight: float


class AISuggestionRequest(BaseModel):
    context: str
    suggestion_type: str  # "rule", "weight", "threshold"


class AISuggestionResponse(BaseModel):
    suggestion: str
    explanation: str
    confidence: str
    data: dict | None = None
