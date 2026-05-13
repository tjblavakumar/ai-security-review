"""Service for managing risk configuration"""

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.models import Question, RiskRule, RiskThreshold
from app.schemas.risk_schemas import (
    BulkQuestionRiskWeightUpdate,
    QuestionRiskWeightUpdate,
    RiskConfigSummary,
    RiskRuleCreate,
    RiskRuleUpdate,
    RiskThresholdCreate,
    RiskThresholdUpdate,
)


# ---------- Risk Rules ----------

def list_risk_rules(db: Session, active_only: bool = False) -> list[RiskRule]:
    """List all risk rules"""
    query = db.query(RiskRule)
    if active_only:
        query = query.filter(RiskRule.is_active == True)
    return query.order_by(RiskRule.name).all()


def get_risk_rule(db: Session, rule_id: int) -> RiskRule | None:
    """Get a single risk rule by ID"""
    return db.query(RiskRule).filter(RiskRule.id == rule_id).first()


def create_risk_rule(db: Session, data: RiskRuleCreate) -> RiskRule:
    """Create a new risk rule"""
    rule = RiskRule(
        name=data.name,
        description=data.description,
        keywords=json.dumps(data.keywords),
        high_risk_answers=json.dumps(data.high_risk_answers),
        risk_value=data.risk_value,
        is_active=data.is_active,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def update_risk_rule(db: Session, rule_id: int, data: RiskRuleUpdate) -> RiskRule | None:
    """Update an existing risk rule"""
    rule = db.query(RiskRule).filter(RiskRule.id == rule_id).first()
    if not rule:
        return None
    
    if data.name is not None:
        rule.name = data.name
    if data.description is not None:
        rule.description = data.description
    if data.keywords is not None:
        rule.keywords = json.dumps(data.keywords)
    if data.high_risk_answers is not None:
        rule.high_risk_answers = json.dumps(data.high_risk_answers)
    if data.risk_value is not None:
        rule.risk_value = data.risk_value
    if data.is_active is not None:
        rule.is_active = data.is_active
    
    db.commit()
    db.refresh(rule)
    return rule


def delete_risk_rule(db: Session, rule_id: int) -> bool:
    """Delete a risk rule"""
    rule = db.query(RiskRule).filter(RiskRule.id == rule_id).first()
    if not rule:
        return False
    db.delete(rule)
    db.commit()
    return True


# ---------- Risk Thresholds ----------

def list_risk_thresholds(db: Session) -> list[RiskThreshold]:
    """List all risk thresholds"""
    return db.query(RiskThreshold).order_by(RiskThreshold.display_order).all()


def get_risk_threshold(db: Session, threshold_id: int) -> RiskThreshold | None:
    """Get a single risk threshold by ID"""
    return db.query(RiskThreshold).filter(RiskThreshold.id == threshold_id).first()


def create_risk_threshold(db: Session, data: RiskThresholdCreate) -> RiskThreshold:
    """Create a new risk threshold"""
    threshold = RiskThreshold(
        level=data.level,
        min_score=data.min_score,
        max_score=data.max_score,
        color=data.color,
        display_order=data.display_order,
    )
    db.add(threshold)
    db.commit()
    db.refresh(threshold)
    return threshold


def update_risk_threshold(db: Session, threshold_id: int, data: RiskThresholdUpdate) -> RiskThreshold | None:
    """Update an existing risk threshold"""
    threshold = db.query(RiskThreshold).filter(RiskThreshold.id == threshold_id).first()
    if not threshold:
        return None
    
    if data.level is not None:
        threshold.level = data.level
    if data.min_score is not None:
        threshold.min_score = data.min_score
    if data.max_score is not None:
        threshold.max_score = data.max_score
    if data.color is not None:
        threshold.color = data.color
    if data.display_order is not None:
        threshold.display_order = data.display_order
    
    db.commit()
    db.refresh(threshold)
    return threshold


def delete_risk_threshold(db: Session, threshold_id: int) -> bool:
    """Delete a risk threshold"""
    threshold = db.query(RiskThreshold).filter(RiskThreshold.id == threshold_id).first()
    if not threshold:
        return False
    db.delete(threshold)
    db.commit()
    return True


# ---------- Question Risk Weights ----------

def update_question_risk_weight(db: Session, update: QuestionRiskWeightUpdate) -> Question | None:
    """Update risk weight for a single question"""
    question = db.query(Question).filter(Question.id == update.question_id).first()
    if not question:
        return None
    
    question.risk_weight = update.risk_weight
    db.commit()
    db.refresh(question)
    return question


def bulk_update_question_risk_weights(db: Session, data: BulkQuestionRiskWeightUpdate) -> list[Question]:
    """Update risk weights for multiple questions"""
    updated_questions = []
    
    for update in data.updates:
        question = db.query(Question).filter(Question.id == update.question_id).first()
        if question:
            question.risk_weight = update.risk_weight
            updated_questions.append(question)
    
    db.commit()
    for q in updated_questions:
        db.refresh(q)
    
    return updated_questions


def update_category_risk_weights(db: Session, category_id: int, risk_weight: int) -> list[Question]:
    """Update risk weight for all questions in a category"""
    questions = db.query(Question).filter(Question.category_id == category_id).all()
    
    for question in questions:
        question.risk_weight = risk_weight
    
    db.commit()
    for q in questions:
        db.refresh(q)
    
    return questions


# ---------- Configuration Summary ----------

def get_config_summary(db: Session) -> RiskConfigSummary:
    """Get summary of risk configuration"""
    from app.schemas.risk_schemas import RiskThresholdOut
    
    all_rules = db.query(RiskRule).all()
    active_rules = [r for r in all_rules if r.is_active]
    thresholds = list_risk_thresholds(db)
    
    # Convert thresholds to RiskThresholdOut with proper datetime conversion
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
    
    # Calculate average question weight
    questions = db.query(Question).filter(Question.is_active == True).all()
    avg_weight = sum(q.risk_weight for q in questions) / len(questions) if questions else 5.0
    
    return RiskConfigSummary(
        total_rules=len(all_rules),
        active_rules=len(active_rules),
        thresholds=thresholds_out,
        average_question_weight=round(avg_weight, 2),
    )


# ---------- Default Configuration Seeding ----------

def seed_default_risk_config(db: Session) -> None:
    """Seed default risk rules and thresholds if none exist"""
    
    # Check if rules already exist
    existing_rules = db.query(RiskRule).count()
    if existing_rules == 0:
        default_rules = [
            {
                "name": "pii",
                "description": "Personally Identifiable Information and sensitive data",
                "keywords": ["pii", "personally identifiable", "personal data", "sensitive data"],
                "high_risk_answers": ["yes", "true", "contains"],
                "risk_value": 9,
            },
            {
                "name": "encryption",
                "description": "Data encryption controls",
                "keywords": ["encrypt", "encryption", "encrypted"],
                "high_risk_answers": ["no", "false", "not encrypted", "unencrypted"],
                "risk_value": 8,
            },
            {
                "name": "authentication",
                "description": "Authentication and access control",
                "keywords": ["authentication", "access control", "authorized"],
                "high_risk_answers": ["no", "false", "public", "anyone"],
                "risk_value": 9,
            },
            {
                "name": "public_access",
                "description": "Public exposure and external access",
                "keywords": ["public", "publicly accessible", "external access"],
                "high_risk_answers": ["yes", "true", "public"],
                "risk_value": 8,
            },
            {
                "name": "monitoring",
                "description": "Monitoring and audit trails",
                "keywords": ["monitor", "logging", "audit trail"],
                "high_risk_answers": ["no", "false", "not monitored"],
                "risk_value": 6,
            },
        ]
        
        for rule_data in default_rules:
            rule = RiskRule(
                name=rule_data["name"],
                description=rule_data["description"],
                keywords=json.dumps(rule_data["keywords"]),
                high_risk_answers=json.dumps(rule_data["high_risk_answers"]),
                risk_value=rule_data["risk_value"],
                is_active=True,
            )
            db.add(rule)
    
    # Check if thresholds already exist
    existing_thresholds = db.query(RiskThreshold).count()
    if existing_thresholds == 0:
        default_thresholds = [
            {"level": "low", "min_score": 0, "max_score": 25, "color": "#22c55e", "display_order": 1},
            {"level": "medium", "min_score": 26, "max_score": 50, "color": "#eab308", "display_order": 2},
            {"level": "high", "min_score": 51, "max_score": 75, "color": "#f97316", "display_order": 3},
            {"level": "critical", "min_score": 76, "max_score": 100, "color": "#ef4444", "display_order": 4},
        ]
        
        for threshold_data in default_thresholds:
            threshold = RiskThreshold(**threshold_data)
            db.add(threshold)
    
    db.commit()
