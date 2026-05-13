from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # =============================================================================
    # Application Configuration
    # All values should be set in .env file
    # =============================================================================
    
    # Database
    DATABASE_URL: str
    
    # Application
    APP_TITLE: str
    APP_VERSION: str
    APP_ENV: str
    DEBUG: bool
    CORS_ORIGINS: str
    
    # File Upload
    UPLOAD_DIR: str
    MAX_UPLOAD_SIZE_MB: int

    # =============================================================================
    # LLM Provider Configuration
    # Choose one: openai, litellm, or bedrock
    # Only the selected provider's settings are required
    # =============================================================================
    LLM_PROVIDER: str
    
    # -----------------------------------------------------------------------------
    # OpenAI Configuration (required only if LLM_PROVIDER=openai)
    # -----------------------------------------------------------------------------
    OPENAI_API_KEY: Optional[str] = ""
    OPENAI_MODEL: Optional[str] = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: Optional[str] = "text-embedding-3-small"
    
    # -----------------------------------------------------------------------------
    # LiteLLM Configuration (required only if LLM_PROVIDER=litellm)
    # -----------------------------------------------------------------------------
    LITELLM_API_BASE: Optional[str] = "http://localhost:4000"
    LITELLM_API_KEY: Optional[str] = "sk-1234"
    LITELLM_MODEL_ID: Optional[str] = "ollama/llama2"
    LITELLM_VISION_MODEL_ID: Optional[str] = "ollama/llava"
    LITELLM_EMBEDDING_MODEL: Optional[str] = "ollama/nomic-embed-text"
    
    # -----------------------------------------------------------------------------
    # AWS Bedrock Configuration (required only if LLM_PROVIDER=bedrock)
    # -----------------------------------------------------------------------------
    BEDROCK_REGION: Optional[str] = "us-east-1"
    BEDROCK_MODEL_ID: Optional[str] = "anthropic.claude-3-sonnet-20240229-v1:0"
    BEDROCK_EMBEDDING_MODEL_ID: Optional[str] = "amazon.titan-embed-text-v1"
    AWS_ACCESS_KEY_ID: Optional[str] = ""
    AWS_SECRET_ACCESS_KEY: Optional[str] = ""
    
    # -----------------------------------------------------------------------------
    # General AI Settings
    # -----------------------------------------------------------------------------
    AI_SUGGESTION_ENABLED: bool
    RAG_CHUNK_SIZE: int
    RAG_CHUNK_OVERLAP: int
    RAG_TOP_K: int
    
    # Validate that required fields for selected provider are set
    @field_validator('LLM_PROVIDER')
    @classmethod
    def validate_provider(cls, v: str) -> str:
        allowed = ['openai', 'litellm', 'bedrock']
        if v.lower() not in allowed:
            raise ValueError(f"LLM_PROVIDER must be one of {allowed}, got '{v}'")
        return v.lower()
    
    def validate_provider_config(self) -> None:
        """Validate that the selected provider has required configuration.
        Call this after initialization to check provider-specific settings."""
        provider = self.LLM_PROVIDER.lower()
        
        if provider == 'openai':
            if not self.OPENAI_API_KEY:
                raise ValueError(
                    "OPENAI_API_KEY is required when LLM_PROVIDER=openai. "
                    "Get your key from https://platform.openai.com/api-keys"
                )
        elif provider == 'litellm':
            if not self.LITELLM_API_BASE:
                raise ValueError(
                    "LITELLM_API_BASE is required when LLM_PROVIDER=litellm. "
                    "Set it to your LiteLLM proxy URL (e.g., http://localhost:4000)"
                )
            if not self.LITELLM_MODEL_ID:
                raise ValueError(
                    "LITELLM_MODEL_ID is required when LLM_PROVIDER=litellm. "
                    "Set it to your model name (e.g., ollama/llama2)"
                )
        elif provider == 'bedrock':
            if not self.BEDROCK_REGION:
                raise ValueError(
                    "BEDROCK_REGION is required when LLM_PROVIDER=bedrock. "
                    "Set it to your AWS region (e.g., us-east-1)"
                )
            if not self.BEDROCK_MODEL_ID:
                raise ValueError(
                    "BEDROCK_MODEL_ID is required when LLM_PROVIDER=bedrock. "
                    "Set it to your model ID (e.g., anthropic.claude-3-sonnet-20240229-v1:0)"
                )

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

# Validate provider-specific configuration on startup
if settings.AI_SUGGESTION_ENABLED:
    try:
        settings.validate_provider_config()
    except ValueError as e:
        print(f"\n⚠️  Configuration Warning: {e}")
        print("\nThe application will start, but AI features will be disabled.")
        print("To enable AI features, fix the configuration and restart.\n")
