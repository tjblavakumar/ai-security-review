"""Seed script: populates categories and sample questions."""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine, Base
from app.models import Question, QuestionCategory, QuestionCondition, QuestionType


CATEGORIES = [
    {"name": "Project Overview", "description": "General information about the AI/GenAI project", "display_order": 1},
    {"name": "Data Classification & Handling", "description": "Data types, sensitivity levels, and handling procedures", "display_order": 2},
    {"name": "Model & Algorithm Details", "description": "Information about AI/ML models and algorithms used", "display_order": 3},
    {"name": "Privacy & PII", "description": "Personal identifiable information and privacy considerations", "display_order": 4},
    {"name": "Third-Party & Vendor Risk", "description": "External services, APIs, and vendor assessments", "display_order": 5},
    {"name": "Infrastructure & Deployment", "description": "Hosting, deployment environments, and infrastructure security", "display_order": 6},
    {"name": "Access Control & Authentication", "description": "User access, roles, and authentication mechanisms", "display_order": 7},
    {"name": "Monitoring & Logging", "description": "Observability, audit trails, and incident response", "display_order": 8},
    {"name": "Compliance & Regulatory", "description": "Regulatory requirements and compliance frameworks", "display_order": 9},
    {"name": "Ethical AI & Bias", "description": "Fairness, bias detection, and ethical considerations", "display_order": 10},
    {"name": "Business Continuity & Risk", "description": "Disaster recovery, risk assessment, and continuity planning", "display_order": 11},
]

QUESTIONS: list[dict] = [
    # Category 1: Project Overview
    {"cat_idx": 0, "text": "What is the primary purpose of this AI/GenAI project?", "type": "textarea", "order": 1, "required": True},
    {"cat_idx": 0, "text": "What type of AI/ML technology does this project use?", "type": "multi_select", "order": 2, "required": True,
     "options": json.dumps(["Large Language Model (LLM)", "Computer Vision", "Natural Language Processing", "Predictive Analytics", "Recommendation System", "Robotic Process Automation", "Other"])},
    {"cat_idx": 0, "text": "Is this a customer-facing application?", "type": "yes_no", "order": 3, "required": True},
    {"cat_idx": 0, "text": "Describe the expected user base and scale of the project.", "type": "textarea", "order": 4, "required": False},

    # Category 2: Data Classification & Handling
    {"cat_idx": 1, "text": "What types of data will this project process?", "type": "multi_select", "order": 5, "required": True,
     "options": json.dumps(["Public Data", "Internal Data", "Confidential Data", "Restricted/Regulated Data", "PII", "Financial Data", "Health Data"])},
    {"cat_idx": 1, "text": "Where will the data be stored?", "type": "single_select", "order": 6, "required": True,
     "options": json.dumps(["On-premises only", "Cloud (AWS)", "Cloud (Azure)", "Cloud (GCP)", "Hybrid", "Third-party hosted"])},
    {"cat_idx": 1, "text": "Describe the data retention policy for this project.", "type": "textarea", "order": 7, "required": True},

    # Category 3: Model & Algorithm Details
    {"cat_idx": 2, "text": "Is the model being trained in-house or using a pre-trained model?", "type": "single_select", "order": 8, "required": True,
     "options": json.dumps(["Training in-house", "Pre-trained model (fine-tuned)", "Pre-trained model (as-is)", "Combination"])},
    {"cat_idx": 2, "text": "What training data sources are used?", "type": "textarea", "order": 9, "required": True},
    {"cat_idx": 2, "text": "Does the model generate or create content (generative AI)?", "type": "yes_no", "order": 10, "required": True},

    # Category 4: Privacy & PII
    {"cat_idx": 3, "text": "Does your project process PII (Personally Identifiable Information)?", "type": "yes_no", "order": 11, "required": True},
    {"cat_idx": 3, "text": "What types of PII are processed?", "type": "multi_select", "order": 12, "required": True,
     "options": json.dumps(["Names", "Email addresses", "Phone numbers", "Social Security Numbers", "Financial account numbers", "Health information", "Biometric data", "Location data"]),
     "condition_on": 11, "condition_value": "Yes"},
    {"cat_idx": 3, "text": "How is PII anonymized or pseudonymized before processing?", "type": "textarea", "order": 13, "required": True,
     "condition_on": 11, "condition_value": "Yes"},

    # Category 5: Third-Party & Vendor Risk
    {"cat_idx": 4, "text": "Does this project use any third-party AI/ML services or APIs?", "type": "yes_no", "order": 14, "required": True},
    {"cat_idx": 4, "text": "List all third-party AI services and their vendors.", "type": "textarea", "order": 15, "required": True,
     "condition_on": 14, "condition_value": "Yes"},
    {"cat_idx": 4, "text": "Has a vendor security assessment been completed for each third-party service?", "type": "single_select", "order": 16, "required": True,
     "options": json.dumps(["Yes, all vendors assessed", "Some vendors assessed", "No assessments completed", "Not applicable"]),
     "condition_on": 14, "condition_value": "Yes"},

    # Category 6: Infrastructure & Deployment
    {"cat_idx": 5, "text": "What is the deployment environment?", "type": "single_select", "order": 17, "required": True,
     "options": json.dumps(["Production", "Staging/UAT", "Development", "Proof of Concept"])},
    {"cat_idx": 5, "text": "Is the application containerized?", "type": "yes_no", "order": 18, "required": True},
    {"cat_idx": 5, "text": "Describe the network architecture and any segmentation in place.", "type": "textarea", "order": 19, "required": False},

    # Category 7: Access Control & Authentication
    {"cat_idx": 6, "text": "What authentication mechanism is used?", "type": "single_select", "order": 20, "required": True,
     "options": json.dumps(["SSO/SAML", "OAuth 2.0", "API Keys", "Username/Password", "Certificate-based", "Multiple methods"])},
    {"cat_idx": 6, "text": "Is multi-factor authentication (MFA) enforced?", "type": "yes_no", "order": 21, "required": True},
    {"cat_idx": 6, "text": "Describe the role-based access control (RBAC) model.", "type": "textarea", "order": 22, "required": True},

    # Category 8: Monitoring & Logging
    {"cat_idx": 7, "text": "What monitoring tools are in place?", "type": "multi_select", "order": 23, "required": True,
     "options": json.dumps(["CloudWatch", "Datadog", "Splunk", "ELK Stack", "Prometheus/Grafana", "Custom solution", "None"])},
    {"cat_idx": 7, "text": "Are AI model inputs and outputs logged for audit purposes?", "type": "yes_no", "order": 24, "required": True},
    {"cat_idx": 7, "text": "Describe the incident response process for this system.", "type": "textarea", "order": 25, "required": True},

    # Category 9: Compliance & Regulatory
    {"cat_idx": 8, "text": "Which regulatory frameworks apply to this project?", "type": "multi_select", "order": 26, "required": True,
     "options": json.dumps(["SOC 2", "GDPR", "CCPA", "HIPAA", "PCI-DSS", "NIST AI RMF", "EU AI Act", "FedRAMP", "None identified"])},
    {"cat_idx": 8, "text": "Has a Data Protection Impact Assessment (DPIA) been conducted?", "type": "single_select", "order": 27, "required": True,
     "options": json.dumps(["Yes, completed", "In progress", "Planned", "Not required", "Not sure"])},

    # Category 10: Ethical AI & Bias
    {"cat_idx": 9, "text": "Has a bias assessment been performed on the training data?", "type": "yes_no", "order": 28, "required": True},
    {"cat_idx": 9, "text": "What measures are in place to detect and mitigate bias in model outputs?", "type": "textarea", "order": 29, "required": True},
    {"cat_idx": 9, "text": "Is there a human-in-the-loop review process for AI-generated decisions?", "type": "yes_no", "order": 30, "required": True},

    # Category 11: Business Continuity & Risk
    {"cat_idx": 10, "text": "What is the disaster recovery plan for this AI system?", "type": "textarea", "order": 31, "required": True},
    {"cat_idx": 10, "text": "What is the acceptable downtime (RTO) for this system?", "type": "single_select", "order": 32, "required": True,
     "options": json.dumps(["< 1 hour", "1-4 hours", "4-24 hours", "> 24 hours", "Not critical"])},
    {"cat_idx": 10, "text": "Has a risk assessment been completed for this project?", "type": "single_select", "order": 33, "required": True,
     "options": json.dumps(["Yes, completed", "In progress", "Planned", "No"]),
     "attachment": True},
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing_count = db.query(Question).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} questions. Skipping seed.")
            return

        categories: list[QuestionCategory] = []
        for cat_data in CATEGORIES:
            cat = QuestionCategory(**cat_data)
            db.add(cat)
            categories.append(cat)
        db.flush()

        question_map: dict[int, Question] = {}

        for q_data in QUESTIONS:
            q_type_str = q_data["type"]
            q_type = QuestionType(q_type_str)
            question = Question(
                category_id=categories[q_data["cat_idx"]].id,
                question_text=q_data["text"],
                question_type=q_type,
                options=q_data.get("options"),
                is_required=q_data.get("required", True),
                is_active=True,
                allows_attachment=q_data.get("attachment", False),
                display_order=q_data["order"],
            )
            db.add(question)
            db.flush()
            question_map[q_data["order"]] = question

        for q_data in QUESTIONS:
            if "condition_on" in q_data:
                question = question_map[q_data["order"]]
                depends_on = question_map[q_data["condition_on"]]
                condition = QuestionCondition(
                    question_id=question.id,
                    depends_on_question_id=depends_on.id,
                    expected_value=q_data["condition_value"],
                )
                db.add(condition)

        db.commit()
        print(f"Seeded {len(categories)} categories and {len(QUESTIONS)} questions.")
    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
