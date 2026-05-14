"""Test script to verify LLM provider configuration"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.services.llm_factory import get_llm_provider, is_llm_configured


def test_provider():
    """Test the configured LLM provider"""
    print("=" * 60)
    print("LLM Provider Configuration Test")
    print("=" * 60)
    
    print(f"\n1. Provider Configuration:")
    print(f"   Provider: {settings.LLM_PROVIDER}")
    print(f"   AI Enabled: {settings.AI_SUGGESTION_ENABLED}")
    print(f"   Configured: {is_llm_configured()}")
    
    if not is_llm_configured():
        print("\n❌ Provider not properly configured!")
        print(f"   Please check your .env file for {settings.LLM_PROVIDER.upper()} settings")
        return False
    
    try:
        provider = get_llm_provider()
        print(f"\n2. Provider Instance: ✓")
        print(f"   Type: {type(provider).__name__}")
        
        # Test chat completion
        print(f"\n3. Testing Chat Completion...")
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello World' and nothing else."}
        ]
        
        response = provider.chat_completion(
            messages=messages,
            temperature=0.1,
            max_tokens=50
        )
        
        print(f"   ✓ Chat Response: {response[:100]}")
        
        # Test embeddings
        print(f"\n4. Testing Embeddings...")
        texts = ["This is a test sentence."]
        embeddings = provider.get_embeddings(texts)
        
        print(f"   ✓ Embedding Dimensions: {len(embeddings[0])}")
        print(f"   ✓ First 5 values: {embeddings[0][:5]}")
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def show_provider_config():
    """Display current provider configuration"""
    provider = settings.LLM_PROVIDER.lower()
    
    print("\n" + "=" * 60)
    print("Current Configuration")
    print("=" * 60)
    
    if provider == "openai":
        print(f"Provider: OpenAI")
        print(f"Model: {settings.OPENAI_MODEL}")
        print(f"Embedding Model: {settings.OPENAI_EMBEDDING_MODEL}")
        print(f"API Key: {'✓ Set' if settings.OPENAI_API_KEY else '✗ Not Set'}")
        
    elif provider == "litellm":
        print(f"Provider: LiteLLM")
        print(f"API Base: {settings.LITELLM_API_BASE}")
        print(f"Model ID: {settings.LITELLM_MODEL_ID}")
        print(f"Embedding Model: {settings.LITELLM_EMBEDDING_MODEL}")
        print(f"API Key: {'✓ Set' if settings.LITELLM_API_KEY else '✗ Not Set'}")
        
    elif provider == "bedrock":
        print(f"Provider: AWS Bedrock")
        print(f"Region: {settings.BEDROCK_REGION}")
        print(f"Model ID: {settings.BEDROCK_MODEL_ID}")
        print(f"Embedding Model: {settings.BEDROCK_EMBEDDING_MODEL_ID}")
        print(f"AWS Credentials: {'✓ Set' if settings.AWS_ACCESS_KEY_ID else '✗ Using IAM/Default'}")
        
    else:
        print(f"Unknown provider: {provider}")
    
    print("=" * 60)


if __name__ == "__main__":
    show_provider_config()
    success = test_provider()
    sys.exit(0 if success else 1)
