export type QuestionType = "text" | "textarea" | "yes_no" | "single_select" | "multi_select";
export type SubmissionStatus = "draft" | "submitted" | "in_review" | "returned" | "approved";
export type ProjectType = "new" | "modification" | "third-party";
export type NotificationType = "submission_created" | "submission_submitted" | "submission_returned" | "submission_approved";
export type RiskLevel = "low" | "medium" | "high" | "critical";

export interface QuestionCategory {
  id: number;
  name: string;
  description: string | null;
  display_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export type ConditionOperator =
  | "equals"
  | "not_equals"
  | "contains"
  | "not_contains"
  | "greater_than"
  | "less_than"
  | "regex"
  | "is_empty"
  | "is_not_empty";

export interface QuestionCondition {
  id: number;
  question_id: number;
  depends_on_question_id: number;
  operator: ConditionOperator;
  expected_value: string;
}

export interface QuestionConditionCreate {
  depends_on_question_id: number;
  operator: ConditionOperator;
  expected_value: string;
}

export interface Question {
  id: number;
  category_id: number;
  question_text: string;
  description: string | null;
  question_type: QuestionType;
  options: string | null;
  is_required: boolean;
  is_active: boolean;
  allows_attachment: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
  conditions: QuestionCondition[];
  category?: QuestionCategory;
}

export interface Submission {
  id: number;
  project_name: string;
  project_description: string | null;
  submitter_name: string;
  submitter_email: string;
  team_department: string | null;
  target_go_live_date: string | null;
  project_type: ProjectType;
  status: SubmissionStatus;
  current_step: number;
  created_at: string;
  updated_at: string;
  submitted_at: string | null;
  risk_score: number | null;
  risk_level: RiskLevel | null;
}

export interface SubmissionResponse {
  id: number;
  submission_id: number;
  question_id: number;
  response_value: string | null;
  is_skipped: boolean;
  created_at: string;
  updated_at: string;
}

export interface SubmissionDetail extends Submission {
  responses: SubmissionResponse[];
}

export interface SubmissionProgress {
  submission_id: number;
  total_questions: number;
  answered_questions: number;
  progress_percent: number;
  current_step: number;
}

export interface Review {
  id: number;
  submission_id: number;
  reviewer_name: string;
  reviewer_email: string;
  overall_comments: string | null;
  decision: string;
  created_at: string;
  comments: ReviewComment[];
}

export interface ReviewComment {
  id: number;
  review_id: number;
  question_id: number;
  comment_text: string;
  created_at: string;
}

export interface Notification {
  id: number;
  recipient_email: string;
  notification_type: NotificationType;
  title: string;
  message: string;
  submission_id: number | null;
  is_read: boolean;
  created_at: string;
}

// Phase 2 — AI types

export interface AISuggestion {
  suggestion: string;
  explanation: string;
  confidence: "high" | "medium" | "low";
  policy_references: string[];
  enabled: boolean;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface AIStatus {
  enabled: boolean;
  model: string;
  embedding_model: string;
  rag_indexed_documents: number;
  rag_total_chunks: number;
}

export interface PolicyDocument {
  id: number;
  title: string;
  content: string | null;
  version: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  tags: string[];
  chunk_count: number;
}

export interface RAGSearchResult {
  score: number;
  chunk: string;
  document_title: string;
  document_id: number;
}

// Risk Scoring types

export interface RiskFactor {
  question: string;
  category: string;
  risk_value: number;
  weight: number;
}

export interface RiskScore {
  risk_score: number;
  risk_level: RiskLevel;
  total_questions: number;
  answered_questions: number;
  risk_factors: RiskFactor[];
}

// Risk Configuration types

export interface RiskRule {
  id: number;
  name: string;
  description: string | null;
  keywords: string[];
  high_risk_answers: string[];
  risk_value: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RiskRuleCreate {
  name: string;
  description: string | null;
  keywords: string[];
  high_risk_answers: string[];
  risk_value: number;
  is_active: boolean;
}

export interface RiskRuleUpdate {
  name?: string;
  description?: string | null;
  keywords?: string[];
  high_risk_answers?: string[];
  risk_value?: number;
  is_active?: boolean;
}

export interface RiskThreshold {
  id: number;
  level: string;
  min_score: number;
  max_score: number;
  color: string;
  display_order: number;
  created_at: string;
  updated_at: string;
}

export interface RiskThresholdCreate {
  level: string;
  min_score: number;
  max_score: number;
  color: string;
  display_order: number;
}

export interface RiskThresholdUpdate {
  level?: string;
  min_score?: number;
  max_score?: number;
  color?: string;
  display_order?: number;
}

export interface RiskConfigSummary {
  total_rules: number;
  active_rules: number;
  thresholds: RiskThreshold[];
  average_question_weight: number;
}

export interface QuestionRiskWeightUpdate {
  question_id: number;
  risk_weight: number;
}

export interface AIRiskSuggestion {
  suggestion: string;
  explanation: string;
  confidence: string;
  data: any;
}
