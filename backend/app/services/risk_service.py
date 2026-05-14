"""Risk scoring service for submissions"""

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.models import Question, Submission, SubmissionResponse


# Risk scoring rules based on common patterns
RISK_RULES = {
    # PII/Sensitive Data patterns
    "pii": {
        "keywords": ["pii", "personally identifiable", "personal data", "sensitive data"],
        "high_risk_answers": ["yes", "true", "contains"],
        "risk_value": 9,
    },
    # Security controls
    "encryption": {
        "keywords": ["encrypt", "encryption", "encrypted"],
        "high_risk_answers": ["no", "false", "not encrypted", "unencrypted"],
        "risk_value": 8,
    },
    # Access control
    "authentication": {
        "keywords": ["authentication", "access control", "authorized"],
        "high_risk_answers": ["no", "false", "public", "anyone"],
        "risk_value": 9,
    },
    # Public exposure
    "public_access": {
        "keywords": ["public", "publicly accessible", "external access"],
        "high_risk_answers": ["yes", "true", "public"],
        "risk_value": 8,
    },
    # Monitoring
    "monitoring": {
        "keywords": ["monitor", "logging", "audit trail"],
        "high_risk_answers": ["no", "false", "not monitored"],
        "risk_value": 6,
    },
}


def calculate_answer_risk(question: Question, answer_value: str | None) -> int:
    """Calculate risk score (0-10) for a specific answer.
    
    Args:
        question: The question being answered
        answer_value: The response value (may be JSON for selection types)
        
    Returns:
        Risk score from 0-10
    """
    if not answer_value:
        return 0
    
    # Parse JSON answers to get the actual selection
    actual_answer = answer_value
    try:
        parsed = json.loads(answer_value)
        if isinstance(parsed, dict):
            # New format with comments
            actual_answer = parsed.get("selection", parsed.get("selections", ""))
            if isinstance(actual_answer, list):
                actual_answer = ", ".join(actual_answer)
    except (json.JSONDecodeError, TypeError):
        pass
    
    answer_lower = str(actual_answer).lower()
    question_lower = question.question_text.lower()
    
    # Check against risk rules
    for rule_name, rule in RISK_RULES.items():
        # Check if question matches this rule category
        if any(keyword in question_lower for keyword in rule["keywords"]):
            # Check if answer indicates high risk
            if any(high_risk in answer_lower for high_risk in rule["high_risk_answers"]):
                return rule["risk_value"]
            else:
                # Answer indicates controls in place
                return max(2, rule["risk_value"] - 5)
    
    # Default risk based on question type
    if question.question_type.value == "yes_no":
        # Yes/No questions with "yes" are generally higher risk
        if "yes" in answer_lower:
            return 5  # Medium risk
        return 2  # Low risk
    
    # Default medium-low risk for answered questions
    return 3


def calculate_submission_risk(db: Session, submission: Submission) -> dict[str, Any]:
    """Calculate overall risk score for a submission.
    
    Args:
        db: Database session
        submission: The submission to score
        
    Returns:
        Dict with risk_score (0-100), risk_level, and breakdown
    """
    if not submission.responses:
        return {
            "risk_score": 0.0,
            "risk_level": "low",
            "total_questions": 0,
            "answered_questions": 0,
            "risk_factors": [],
        }
    
    total_weighted_risk = 0.0
    max_possible_risk = 0.0
    answered_count = 0
    risk_factors = []
    
    for response in submission.responses:
        if not response.question or response.is_skipped:
            continue
            
        question = response.question
        weight = question.risk_weight or 5  # Default to medium weight
        
        # Calculate risk for this answer
        answer_risk = calculate_answer_risk(question, response.response_value)
        
        # Track high-risk items
        if answer_risk >= 7:
            risk_factors.append({
                "question": question.question_text,
                "category": question.category.name if question.category else "General",
                "risk_value": answer_risk,
                "weight": weight,
            })
        
        # Accumulate weighted risk
        total_weighted_risk += weight * answer_risk
        max_possible_risk += weight * 10  # Max risk is 10
        answered_count += 1
    
    # Calculate percentage score (0-100)
    if max_possible_risk > 0:
        risk_score = (total_weighted_risk / max_possible_risk) * 100
    else:
        risk_score = 0.0
    
    # Determine risk level
    if risk_score <= 25:
        risk_level = "low"
    elif risk_score <= 50:
        risk_level = "medium"
    elif risk_score <= 75:
        risk_level = "high"
    else:
        risk_level = "critical"
    
    return {
        "risk_score": round(risk_score, 1),
        "risk_level": risk_level,
        "total_questions": len(submission.responses),
        "answered_questions": answered_count,
        "risk_factors": sorted(risk_factors, key=lambda x: x["risk_value"] * x["weight"], reverse=True)[:5],
    }


def update_submission_risk(db: Session, submission_id: int) -> dict[str, Any]:
    """Calculate and save risk score for a submission.
    
    Args:
        db: Database session
        submission_id: ID of the submission
        
    Returns:
        Risk score data
    """
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        return {"risk_score": 0.0, "risk_level": "low"}
    
    risk_data = calculate_submission_risk(db, submission)
    
    # Update submission with risk score
    submission.risk_score = risk_data["risk_score"]
    submission.risk_level = risk_data["risk_level"]
    db.commit()
    
    return risk_data
