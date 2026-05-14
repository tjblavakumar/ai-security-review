"""Router for risk scoring endpoints"""

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Submission
from app.schemas import (
    AISuggestionRequest,
    AISuggestionResponse,
    ApiResponse,
    BulkQuestionRiskWeightUpdate,
    QuestionRiskWeightUpdate,
    RiskConfigSummary,
    RiskRuleCreate,
    RiskRuleOut,
    RiskRuleUpdate,
    RiskThresholdCreate,
    RiskThresholdOut,
    RiskThresholdUpdate,
)
from app.services import risk_config_service, risk_service
from app.services.ai_service import generate_suggestion

router = APIRouter(prefix="/api/risk", tags=["Risk"])


@router.get("/submission/{submission_id}", response_model=dict[str, Any])
def get_submission_risk(submission_id: int, db: Session = Depends(get_db)):
    """Get risk score for a submission."""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    risk_data = risk_service.calculate_submission_risk(db, submission)
    
    return {
        "data": risk_data,
        "message": "OK",
        "success": True,
    }


@router.post("/submission/{submission_id}/calculate", response_model=dict[str, Any])
def calculate_and_save_risk(submission_id: int, db: Session = Depends(get_db)):
    """Calculate and save risk score for a submission."""
    risk_data = risk_service.update_submission_risk(db, submission_id)
    
    return {
        "data": risk_data,
        "message": "Risk score updated",
        "success": True,
    }


# ---------- Risk Configuration Endpoints ----------

@router.get("/config/summary", response_model=ApiResponse)
def get_config_summary(db: Session = Depends(get_db)):
    """Get summary of risk configuration"""
    summary = risk_config_service.get_config_summary(db)
    return ApiResponse(data=summary.model_dump(), message="Configuration summary retrieved")


# ---------- Risk Rules ----------

@router.get("/rules", response_model=ApiResponse)
def list_risk_rules(active_only: bool = False, db: Session = Depends(get_db)):
    """List all risk rules"""
    rules = risk_config_service.list_risk_rules(db, active_only=active_only)
    rules_out = []
    for rule in rules:
        rules_out.append(RiskRuleOut(
            id=rule.id,
            name=rule.name,
            description=rule.description,
            keywords=json.loads(rule.keywords),
            high_risk_answers=json.loads(rule.high_risk_answers),
            risk_value=rule.risk_value,
            is_active=rule.is_active,
            created_at=rule.created_at.isoformat(),
            updated_at=rule.updated_at.isoformat(),
        ))
    return ApiResponse(data=rules_out, message="Risk rules retrieved")


@router.get("/rules/{rule_id}", response_model=ApiResponse)
def get_risk_rule(rule_id: int, db: Session = Depends(get_db)):
    """Get a single risk rule"""
    rule = risk_config_service.get_risk_rule(db, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Risk rule not found")
    
    rule_out = RiskRuleOut(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        keywords=json.loads(rule.keywords),
        high_risk_answers=json.loads(rule.high_risk_answers),
        risk_value=rule.risk_value,
        is_active=rule.is_active,
        created_at=rule.created_at.isoformat(),
        updated_at=rule.updated_at.isoformat(),
    )
    return ApiResponse(data=rule_out, message="Risk rule retrieved")


@router.post("/rules", response_model=ApiResponse, status_code=201)
def create_risk_rule(data: RiskRuleCreate, db: Session = Depends(get_db)):
    """Create a new risk rule"""
    rule = risk_config_service.create_risk_rule(db, data)
    rule_out = RiskRuleOut(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        keywords=json.loads(rule.keywords),
        high_risk_answers=json.loads(rule.high_risk_answers),
        risk_value=rule.risk_value,
        is_active=rule.is_active,
        created_at=rule.created_at.isoformat(),
        updated_at=rule.updated_at.isoformat(),
    )
    return ApiResponse(data=rule_out, message="Risk rule created")


@router.put("/rules/{rule_id}", response_model=ApiResponse)
def update_risk_rule(rule_id: int, data: RiskRuleUpdate, db: Session = Depends(get_db)):
    """Update an existing risk rule"""
    rule = risk_config_service.update_risk_rule(db, rule_id, data)
    if not rule:
        raise HTTPException(status_code=404, detail="Risk rule not found")
    
    rule_out = RiskRuleOut(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        keywords=json.loads(rule.keywords),
        high_risk_answers=json.loads(rule.high_risk_answers),
        risk_value=rule.risk_value,
        is_active=rule.is_active,
        created_at=rule.created_at.isoformat(),
        updated_at=rule.updated_at.isoformat(),
    )
    return ApiResponse(data=rule_out, message="Risk rule updated")


@router.delete("/rules/{rule_id}", response_model=ApiResponse)
def delete_risk_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete a risk rule"""
    success = risk_config_service.delete_risk_rule(db, rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Risk rule not found")
    return ApiResponse(data={"deleted": True}, message="Risk rule deleted")


# ---------- Risk Thresholds ----------

@router.get("/thresholds", response_model=ApiResponse)
def list_risk_thresholds(db: Session = Depends(get_db)):
    """List all risk thresholds"""
    thresholds = risk_config_service.list_risk_thresholds(db)
    thresholds_out = [
        RiskThresholdOut(
            id=t.id,
            level=t.level,
            min_score=t.min_score,
            max_score=t.max_score,
            color=t.color,
            display_order=t.display_order,
            created_at=t.created_at.isoformat(),
            updated_at=t.updated_at.isoformat(),
        )
        for t in thresholds
    ]
    return ApiResponse(data=thresholds_out, message="Risk thresholds retrieved")


@router.get("/thresholds/{threshold_id}", response_model=ApiResponse)
def get_risk_threshold(threshold_id: int, db: Session = Depends(get_db)):
    """Get a single risk threshold"""
    threshold = risk_config_service.get_risk_threshold(db, threshold_id)
    if not threshold:
        raise HTTPException(status_code=404, detail="Risk threshold not found")
    
    threshold_out = RiskThresholdOut(
        id=threshold.id,
        level=threshold.level,
        min_score=threshold.min_score,
        max_score=threshold.max_score,
        color=threshold.color,
        display_order=threshold.display_order,
        created_at=threshold.created_at.isoformat(),
        updated_at=threshold.updated_at.isoformat(),
    )
    return ApiResponse(data=threshold_out, message="Risk threshold retrieved")


@router.post("/thresholds", response_model=ApiResponse, status_code=201)
def create_risk_threshold(data: RiskThresholdCreate, db: Session = Depends(get_db)):
    """Create a new risk threshold"""
    threshold = risk_config_service.create_risk_threshold(db, data)
    threshold_out = RiskThresholdOut(
        id=threshold.id,
        level=threshold.level,
        min_score=threshold.min_score,
        max_score=threshold.max_score,
        color=threshold.color,
        display_order=threshold.display_order,
        created_at=threshold.created_at.isoformat(),
        updated_at=threshold.updated_at.isoformat(),
    )
    return ApiResponse(data=threshold_out, message="Risk threshold created")


@router.put("/thresholds/{threshold_id}", response_model=ApiResponse)
def update_risk_threshold(threshold_id: int, data: RiskThresholdUpdate, db: Session = Depends(get_db)):
    """Update an existing risk threshold"""
    threshold = risk_config_service.update_risk_threshold(db, threshold_id, data)
    if not threshold:
        raise HTTPException(status_code=404, detail="Risk threshold not found")
    
    threshold_out = RiskThresholdOut(
        id=threshold.id,
        level=threshold.level,
        min_score=threshold.min_score,
        max_score=threshold.max_score,
        color=threshold.color,
        display_order=threshold.display_order,
        created_at=threshold.created_at.isoformat(),
        updated_at=threshold.updated_at.isoformat(),
    )
    return ApiResponse(data=threshold_out, message="Risk threshold updated")


@router.delete("/thresholds/{threshold_id}", response_model=ApiResponse)
def delete_risk_threshold(threshold_id: int, db: Session = Depends(get_db)):
    """Delete a risk threshold"""
    success = risk_config_service.delete_risk_threshold(db, threshold_id)
    if not success:
        raise HTTPException(status_code=404, detail="Risk threshold not found")
    return ApiResponse(data={"deleted": True}, message="Risk threshold deleted")


# ---------- Question Risk Weights ----------

@router.put("/questions/weight", response_model=ApiResponse)
def update_question_weight(data: QuestionRiskWeightUpdate, db: Session = Depends(get_db)):
    """Update risk weight for a single question"""
    question = risk_config_service.update_question_risk_weight(db, data)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return ApiResponse(data={"question_id": question.id, "risk_weight": question.risk_weight}, message="Risk weight updated")


@router.put("/questions/weight/bulk", response_model=ApiResponse)
def bulk_update_question_weights(data: BulkQuestionRiskWeightUpdate, db: Session = Depends(get_db)):
    """Update risk weights for multiple questions"""
    questions = risk_config_service.bulk_update_question_risk_weights(db, data)
    result = [{"question_id": q.id, "risk_weight": q.risk_weight} for q in questions]
    return ApiResponse(data=result, message=f"{len(questions)} question weights updated")


@router.put("/questions/weight/category/{category_id}", response_model=ApiResponse)
def update_category_weights(category_id: int, risk_weight: int, db: Session = Depends(get_db)):
    """Update risk weight for all questions in a category"""
    if not (1 <= risk_weight <= 10):
        raise HTTPException(status_code=400, detail="Risk weight must be between 1 and 10")
    
    questions = risk_config_service.update_category_risk_weights(db, category_id, risk_weight)
    result = [{"question_id": q.id, "risk_weight": q.risk_weight} for q in questions]
    return ApiResponse(data=result, message=f"{len(questions)} question weights updated")


# ---------- AI Suggestions ----------

@router.post("/ai/suggest", response_model=ApiResponse)
def get_ai_risk_suggestion(request: AISuggestionRequest, db: Session = Depends(get_db)):
    """Get AI suggestions for risk configuration"""
    
    # Build prompt based on suggestion type
    if request.suggestion_type == "rule":
        prompt = f"""Based on the following context, suggest a new risk rule for security questionnaires:

Context: {request.context}

Provide a JSON response with:
- name: short identifier for the rule
- description: what the rule checks for
- keywords: list of keywords to match in questions
- high_risk_answers: list of answer patterns that indicate high risk
- risk_value: score from 1-10 indicating severity

Format as valid JSON."""
    
    elif request.suggestion_type == "weight":
        prompt = f"""Based on the following question, suggest an appropriate risk weight (1-10):

Question: {request.context}

Provide a JSON response with:
- risk_weight: integer from 1-10
- explanation: why this weight is appropriate

Format as valid JSON."""
    
    elif request.suggestion_type == "threshold":
        prompt = f"""Based on the following context, suggest risk threshold adjustments:

Context: {request.context}

Provide a JSON response with threshold suggestions.

Format as valid JSON."""
    
    else:
        raise HTTPException(status_code=400, detail="Invalid suggestion_type")
    
    try:
        # Get AI suggestion using the generate_suggestion function
        ai_response = generate_suggestion(
            question_text=request.context,
            question_type="text",
            question_options=None,
            category_name="Risk Configuration",
            description=f"Generate a {request.suggestion_type} suggestion",
            previous_responses=None,
            policy_context=None,
        )
        
        # Try to parse the suggestion as JSON if it's a string
        suggestion_data = None
        if isinstance(ai_response.get("suggestion"), str):
            try:
                suggestion_data = json.loads(ai_response["suggestion"])
            except json.JSONDecodeError:
                # If it's not JSON, use the raw suggestion
                suggestion_data = {"text": ai_response["suggestion"]}
        else:
            suggestion_data = ai_response.get("suggestion")
        
        response = AISuggestionResponse(
            suggestion=ai_response.get("suggestion", ""),
            explanation=ai_response.get("explanation", ""),
            confidence=ai_response.get("confidence", "low"),
            data=suggestion_data,
        )
        
        return ApiResponse(data=response.model_dump(), message="AI suggestion generated")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate AI suggestion: {str(e)}")
