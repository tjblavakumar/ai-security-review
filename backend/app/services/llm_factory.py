"""LLM Factory — Abstraction layer for multiple LLM providers
(OpenAI, LiteLLM, AWS Bedrock)"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

from app.config import settings


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.5,
        max_tokens: int = 800,
        response_format: dict[str, str] | None = None,
    ) -> str:
        """Generate a chat completion"""
        pass

    @abstractmethod
    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts"""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the provider is properly configured"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.5,
        max_tokens: int = 800,
        response_format: dict[str, str] | None = None,
    ) -> str:
        client = self._get_client()
        kwargs: dict[str, Any] = {
            "model": settings.OPENAI_MODEL,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            kwargs["response_format"] = response_format

        completion = client.chat.completions.create(**kwargs)
        return completion.choices[0].message.content or ""

    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        client = self._get_client()
        response = client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL, input=texts
        )
        return [item.embedding for item in response.data]

    def is_configured(self) -> bool:
        return bool(settings.OPENAI_API_KEY)


class LiteLLMProvider(LLMProvider):
    """LiteLLM provider for local/self-hosted LLMs"""

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI

            # LiteLLM uses OpenAI-compatible API
            self._client = OpenAI(
                api_key=settings.LITELLM_API_KEY,
                base_url=settings.LITELLM_API_BASE,
            )
        return self._client

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.5,
        max_tokens: int = 800,
        response_format: dict[str, str] | None = None,
    ) -> str:
        client = self._get_client()
        kwargs: dict[str, Any] = {
            "model": settings.LITELLM_MODEL_ID,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            kwargs["response_format"] = response_format

        completion = client.chat.completions.create(**kwargs)
        return completion.choices[0].message.content or ""

    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using LiteLLM.
        
        Important: Make sure LITELLM_EMBEDDING_MODEL is set to an actual
        embedding model (e.g., 'ollama/nomic-embed-text'), not a chat model.
        """
        client = self._get_client()
        
        # Validate embedding model is configured
        if not settings.LITELLM_EMBEDDING_MODEL:
            raise ValueError(
                "LITELLM_EMBEDDING_MODEL is not configured. "
                "Set it to an embedding model like 'ollama/nomic-embed-text' in your .env file."
            )
        
        # Check if user accidentally configured a chat model for embeddings
        chat_model_indicators = ['claude', 'gpt', 'llama2', 'llama3', 'mistral']
        if any(indicator in settings.LITELLM_EMBEDDING_MODEL.lower() for indicator in chat_model_indicators):
            if 'embed' not in settings.LITELLM_EMBEDDING_MODEL.lower():
                raise ValueError(
                    f"LITELLM_EMBEDDING_MODEL appears to be a chat model: {settings.LITELLM_EMBEDDING_MODEL}. "
                    "You need an embedding model. For Ollama, use 'ollama/nomic-embed-text' or 'ollama/all-minilm'. "
                    "Chat models like Claude, GPT, Llama cannot generate embeddings."
                )
        
        try:
            response = client.embeddings.create(
                model=settings.LITELLM_EMBEDDING_MODEL, input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            error_msg = str(e)
            if 'Unable to determine' in error_msg and 'embedding provider' in error_msg:
                raise ValueError(
                    f"The model '{settings.LITELLM_EMBEDDING_MODEL}' is not an embedding model. "
                    "For LiteLLM with Ollama, use: 'ollama/nomic-embed-text' or 'ollama/all-minilm'. "
                    "Claude and other chat models cannot generate embeddings."
                ) from e
            raise

    def is_configured(self) -> bool:
        return bool(settings.LITELLM_API_BASE and settings.LITELLM_MODEL_ID)


class BedrockProvider(LLMProvider):
    """AWS Bedrock provider"""

    def __init__(self):
        self._client = None
        self._embeddings_client = None

    def _get_client(self):
        if self._client is None:
            import boto3

            kwargs: dict[str, Any] = {"region_name": settings.BEDROCK_REGION}
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
                kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY

            self._client = boto3.client("bedrock-runtime", **kwargs)
        return self._client

    def _get_embeddings_client(self):
        if self._embeddings_client is None:
            import boto3

            kwargs: dict[str, Any] = {"region_name": settings.BEDROCK_REGION}
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
                kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY

            self._embeddings_client = boto3.client("bedrock-runtime", **kwargs)
        return self._embeddings_client

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.5,
        max_tokens: int = 800,
        response_format: dict[str, str] | None = None,
    ) -> str:
        client = self._get_client()

        # Convert messages to Claude format
        system_message = ""
        conversation_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                conversation_messages.append(
                    {"role": msg["role"], "content": msg["content"]}
                )

        # Build request body for Claude
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": conversation_messages,
        }
        if system_message:
            body["system"] = system_message

        response = client.invoke_model(
            modelId=settings.BEDROCK_MODEL_ID, body=json.dumps(body)
        )

        response_body = json.loads(response["body"].read())
        return response_body.get("content", [{}])[0].get("text", "")

    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        client = self._get_embeddings_client()
        embeddings = []

        for text in texts:
            body = json.dumps({"inputText": text})
            response = client.invoke_model(
                modelId=settings.BEDROCK_EMBEDDING_MODEL_ID, body=body
            )
            response_body = json.loads(response["body"].read())
            embeddings.append(response_body.get("embedding", []))

        return embeddings

    def is_configured(self) -> bool:
        return bool(settings.BEDROCK_MODEL_ID and settings.BEDROCK_REGION)


# ── Factory Function ─────────────────────────────────────────────────


_provider_instance: LLMProvider | None = None


def get_llm_provider() -> LLMProvider:
    """Get the configured LLM provider instance (singleton)"""
    global _provider_instance

    if _provider_instance is None:
        provider_name = settings.LLM_PROVIDER.lower()

        if provider_name == "openai":
            _provider_instance = OpenAIProvider()
        elif provider_name == "litellm":
            _provider_instance = LiteLLMProvider()
        elif provider_name == "bedrock":
            _provider_instance = BedrockProvider()
        else:
            raise ValueError(
                f"Unknown LLM provider: {provider_name}. "
                f"Must be one of: openai, litellm, bedrock"
            )

    return _provider_instance


def is_llm_configured() -> bool:
    """Check if any LLM provider is configured and enabled"""
    if not settings.AI_SUGGESTION_ENABLED:
        return False

    try:
        provider = get_llm_provider()
        return provider.is_configured()
    except Exception:
        return False
