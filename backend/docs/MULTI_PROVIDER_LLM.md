# Multi-Provider LLM Support

## Overview

The AI Security Review application now supports **three LLM providers**:

1. **OpenAI** - Cloud-based GPT models
2. **LiteLLM** - Proxy for local/self-hosted LLMs (Ollama, vLLM, etc.)
3. **AWS Bedrock** - AWS managed AI service (Claude, Titan, etc.)

## Architecture

```
┌─────────────────┐
│  AI Service     │
│  RAG Service    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Factory    │ ◄─── Settings (LLM_PROVIDER)
└────────┬────────┘
         │
    ┌────┴────┬────────┬
    ▼         ▼        ▼
┌────────┐ ┌────────┐ ┌────────┐
│ OpenAI │ │LiteLLM │ │Bedrock │
└────────┘ └────────┘ └────────┘
```

## Configuration

### Environment Variables

Set these in your `.env` file:

#### Provider Selection
```bash
# Choose: openai, litellm, or bedrock
LLM_PROVIDER=openai
```

#### OpenAI Configuration
```bash
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

#### LiteLLM Configuration (Local LLMs)
```bash
LLM_PROVIDER=litellm
LITELLM_API_BASE=http://localhost:4000
LITELLM_API_KEY=sk-1234  # Optional
LITELLM_MODEL_ID=ollama/llama2
LITELLM_VISION_MODEL_ID=ollama/llava
LITELLM_EMBEDDING_MODEL=ollama/nomic-embed-text
```

#### AWS Bedrock Configuration
```bash
LLM_PROVIDER=bedrock
BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v1
AWS_ACCESS_KEY_ID=AKIA...  # Optional if using IAM roles
AWS_SECRET_ACCESS_KEY=...  # Optional if using IAM roles
```

#### General AI Settings
```bash
AI_SUGGESTION_ENABLED=true
RAG_CHUNK_SIZE=800
RAG_CHUNK_OVERLAP=100
RAG_TOP_K=5
```

## Setup Guides

### Option 1: OpenAI (Cloud)

**Pros:** Easy setup, high quality, no infrastructure needed  
**Cons:** Costs per API call, data sent to OpenAI

1. Get API key from https://platform.openai.com/api-keys
2. Set in `.env`:
   ```bash
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-proj-your-key-here
   ```
3. Restart backend

### Option 2: LiteLLM (Local LLMs)

**Pros:** Free, private, runs locally  
**Cons:** Requires setup, may need GPU, lower quality

#### Step 1: Install Ollama
```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download/windows
```

#### Step 2: Pull Models
```bash
# Chat model
ollama pull llama2

# Embedding model
ollama pull nomic-embed-text

# Optional: Vision model
ollama pull llava
```

#### Step 3: Start LiteLLM Proxy
```bash
pip install litellm[proxy]

# Create litellm_config.yaml
cat > litellm_config.yaml << EOF
model_list:
  - model_name: ollama/llama2
    litellm_params:
      model: ollama/llama2
      api_base: http://localhost:11434
      
  - model_name: ollama/nomic-embed-text
    litellm_params:
      model: ollama/nomic-embed-text
      api_base: http://localhost:11434
EOF

# Start proxy
litellm --config litellm_config.yaml --port 4000
```

#### Step 4: Configure Application
```bash
LLM_PROVIDER=litellm
LITELLM_API_BASE=http://localhost:4000
LITELLM_API_KEY=sk-1234
LITELLM_MODEL_ID=ollama/llama2
LITELLM_EMBEDDING_MODEL=ollama/nomic-embed-text
```

### Option 3: AWS Bedrock

**Pros:** Enterprise-grade, managed service, various models  
**Cons:** AWS costs, requires AWS account

#### Step 1: Enable Models in AWS Console
1. Go to AWS Bedrock console
2. Navigate to "Model access"
3. Request access to desired models (e.g., Claude 3 Sonnet)

#### Step 2: Configure AWS Credentials
```bash
# Option A: Use AWS CLI
aws configure

# Option B: Use IAM role (EC2, ECS, Lambda)
# No credentials needed

# Option C: Set in .env
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
```

#### Step 3: Configure Application
```bash
LLM_PROVIDER=bedrock
BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v1
```

## API Endpoint

### Check AI Status

**GET** `/api/ai/status`

Response:
```json
{
  "data": {
    "enabled": true,
    "provider": "litellm",
    "model": "ollama/llama2",
    "embedding_model": "ollama/nomic-embed-text",
    "rag_indexed_documents": 5,
    "rag_total_chunks": 42
  },
  "message": "OK",
  "success": true
}
```

## Switching Providers

To switch between providers:

1. Update `LLM_PROVIDER` in `.env`
2. Configure provider-specific settings
3. Restart the backend

Example:
```bash
# Switch from OpenAI to LiteLLM
sed -i 's/LLM_PROVIDER=openai/LLM_PROVIDER=litellm/' .env
docker-compose restart backend
```

## Troubleshooting

### LiteLLM: Connection Refused
```bash
# Check if LiteLLM proxy is running
curl http://localhost:4000/health

# Start proxy if not running
litellm --config litellm_config.yaml --port 4000
```

### Bedrock: Access Denied
- Check IAM permissions include `bedrock:InvokeModel`
- Verify model access is enabled in Bedrock console
- Confirm region matches your configuration

### Embeddings Mismatch
If switching providers, **re-index policy documents**:

```bash
# Via API
POST /api/policies/{id}/index

# Or via admin UI
Go to Admin > Policies > Click "Re-index" button
```

⚠️ **Important:** Different providers generate incompatible embeddings. Always re-index when switching.

## Model Recommendations

### Chat Models

| Provider | Model | Quality | Speed | Cost |
|----------|-------|---------|-------|------|
| OpenAI | gpt-4o-mini | ⭐⭐⭐⭐⭐ | Fast | Low |
| OpenAI | gpt-4o | ⭐⭐⭐⭐⭐ | Medium | Medium |
| LiteLLM | llama2 | ⭐⭐⭐ | Fast | Free |
| LiteLLM | llama3 | ⭐⭐⭐⭐ | Medium | Free |
| Bedrock | Claude 3 Sonnet | ⭐⭐⭐⭐⭐ | Fast | Medium |

### Embedding Models

| Provider | Model | Dimensions | Quality |
|----------|-------|------------|---------|
| OpenAI | text-embedding-3-small | 1536 | ⭐⭐⭐⭐⭐ |
| LiteLLM | nomic-embed-text | 768 | ⭐⭐⭐⭐ |
| Bedrock | titan-embed-text-v1 | 1536 | ⭐⭐⭐⭐ |

## Performance Comparison

### Response Time (avg)
- OpenAI: ~1-2s
- LiteLLM (local): ~3-10s (depends on hardware)
- Bedrock: ~1-3s

### Cost (per 1M tokens)
- OpenAI (gpt-4o-mini): ~$0.15-0.60
- LiteLLM (local): $0 (electricity only)
- Bedrock (Claude 3): ~$3.00-15.00

## Security Considerations

### OpenAI
- ✅ Data encrypted in transit
- ⚠️ Data sent to third party
- 📝 Review OpenAI's data usage policy

### LiteLLM (Local)
- ✅ All data stays local
- ✅ Complete control
- ⚠️ Secure your infrastructure

### Bedrock
- ✅ Data stays in your AWS account
- ✅ Compliant with AWS compliance programs
- ✅ VPC support available

## Advanced: Custom Provider

To add a new provider:

1. Create class in `backend/app/services/llm_factory.py`:
```python
class CustomProvider(LLMProvider):
    def chat_completion(self, messages, temperature, max_tokens, response_format):
        # Your implementation
        pass
    
    def get_embeddings(self, texts):
        # Your implementation
        pass
    
    def is_configured(self):
        return bool(settings.CUSTOM_API_KEY)
```

2. Add to factory:
```python
elif provider_name == "custom":
    _provider_instance = CustomProvider()
```

3. Add settings in `config.py`

## Support

For issues or questions:
- Check logs: `docker-compose logs backend`
- Test API status: `GET /api/ai/status`
- Review provider documentation

## References

- [OpenAI API Docs](https://platform.openai.com/docs)
- [LiteLLM Docs](https://docs.litellm.ai/)
- [AWS Bedrock Docs](https://docs.aws.amazon.com/bedrock/)
- [Ollama Docs](https://ollama.com/docs)
