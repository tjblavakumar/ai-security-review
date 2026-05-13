"""AI suggestion service — generates context-aware suggestions for
questionnaire responses using multiple LLM providers (OpenAI, LiteLLM, Bedrock)
and optional RAG context."""

from __future__ import annotations

import json
from typing import Any

from app.config import settings
from app.services.llm_factory import get_llm_provider, is_llm_configured


# ── Suggestion generation ────────────────────────────────────────────

SUGGESTION_SYSTEM_PROMPT = """\
You are an AI security review assistant helping users complete an information-security
questionnaire about their AI/GenAI project. For each question you will:
1. Provide a clear, concise *suggested answer* that demonstrates good security practices.
2. Explain *why* this answer matters from an infosec perspective.
3. If policy context is provided, reference the relevant policy sections.

Keep the suggestion practical and actionable. If the question is a yes/no or
single-select type, recommend the safest option and explain trade-offs.

Respond in JSON with these keys:
  "suggestion": "<recommended answer text>",
  "explanation": "<1-3 sentence rationale>",
  "confidence": "<high|medium|low>",
  "policy_references": ["<optional list of referenced policy section titles>"]
"""


def generate_suggestion(
    question_text: str,
    question_type: str,
    question_options: str | None,
    category_name: str,
    description: str | None = None,
    previous_responses: list[dict[str, Any]] | None = None,
    policy_context: str | None = None,
) -> dict[str, Any]:
    """Return an AI-generated suggestion for a single question."""
    if not is_llm_configured():
        provider_name = settings.LLM_PROVIDER.upper()
        return {
            "suggestion": "",
            "explanation": f"AI suggestions are not configured. Configure {provider_name} provider in .env to enable.",
            "confidence": "low",
            "policy_references": [],
            "enabled": False,
        }

    user_parts: list[str] = [
        f"Category: {category_name}",
        f"Question: {question_text}",
        f"Type: {question_type}",
    ]
    if description:
        user_parts.append(f"Description: {description}")
    if question_options:
        user_parts.append(f"Options: {question_options}")
    if previous_responses:
        ctx = "\n".join(
            f"  Q: {r['question_text']}  A: {r['response_value']}"
            for r in previous_responses[:10]
        )
        user_parts.append(f"Previous answers for context:\n{ctx}")
    if policy_context:
        user_parts.append(f"Relevant policy context:\n{policy_context}")

    provider = get_llm_provider()
    raw = provider.chat_completion(
        messages=[
            {"role": "system", "content": SUGGESTION_SYSTEM_PROMPT},
            {"role": "user", "content": "\n\n".join(user_parts)},
        ],
        temperature=0.3,
        max_tokens=600,
        response_format={"type": "json_object"},
    )
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {"suggestion": raw, "explanation": "", "confidence": "low", "policy_references": []}

    # Ensure all required fields exist with defaults
    parsed.setdefault("suggestion", "")
    parsed.setdefault("explanation", "")
    parsed.setdefault("confidence", "low")
    parsed.setdefault("policy_references", [])
    
    # Ensure policy_references is always a list
    if not isinstance(parsed.get("policy_references"), list):
        parsed["policy_references"] = []
    
    parsed["enabled"] = True
    return parsed


# ── Chat completion ──────────────────────────────────────────────────

CHAT_SYSTEM_PROMPT = """\
You are an AI security review assistant embedded in a questionnaire for AI/GenAI projects.
Help the user understand each question, suggest best-practice answers, and explain
security/compliance considerations. Be concise and helpful.
If policy context is provided, reference it when relevant.
If the user asks something unrelated to AI security review, politely redirect.
"""


def chat_completion(
    messages: list[dict[str, str]],
    question_context: str | None = None,
    policy_context: str | None = None,
) -> str:
    """Return a chat response given the conversation history."""
    if not is_llm_configured():
        provider_name = settings.LLM_PROVIDER.upper()
        return f"AI chat is not configured. Configure {provider_name} provider in .env to enable."

    system_parts = [CHAT_SYSTEM_PROMPT]
    if question_context:
        system_parts.append(f"Current question context:\n{question_context}")
    if policy_context:
        system_parts.append(f"Relevant policy context:\n{policy_context}")

    system_msg = {"role": "system", "content": "\n\n".join(system_parts)}
    provider = get_llm_provider()
    return provider.chat_completion(
        messages=[system_msg] + messages,
        temperature=0.5,
        max_tokens=800,
    )
