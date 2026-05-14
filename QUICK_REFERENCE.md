# Multi-Provider LLM - Quick Reference

## Configuration Patterns

### OpenAI (Cloud)
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### LiteLLM (Local)
```env
LLM_PROVIDER=litellm
LITELLM_API_BASE=http://localhost:4000
LITELLM_API_KEY=sk-1234
LITELLM_MODEL_ID=ollama/llama2
LITELLM_EMBEDDING_MODEL=ollama/nomic-embed-text
```

### AWS Bedrock (Enterprise)
```env
LLM_PROVIDER=bedrock
BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v1
```

## Code Usage

### Get Provider
```python
from app.services.llm_factory import get_llm_provider, is_llm_configured

# Check if configured
if is_llm_configured():
    provider = get_llm_provider()
```

### Chat Completion
```python
response = provider.chat_completion(
    messages=[
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=0.5,
    max_tokens=800,
    response_format={"type": "json_object"}  # Optional
)
```

### Get Embeddings
```python
texts = ["Document 1", "Document 2"]
embeddings = provider.get_embeddings(texts)
# Returns: list[list[float]]
```

## API Endpoints

### Check Status
```http
GET /api/ai/status
```
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
  }
}
```

### Get Suggestion
```http
POST /api/ai/suggest
{
  "question_id": 1,
  "submission_id": 123
}
```

### Chat
```http
POST /api/ai/chat
{
  "messages": [
    {"role": "user", "content": "What is PII?"}
  ],
  "question_id": 1
}
```

## Testing

### Test Provider
```bash
cd backend
python test_llm_provider.py
```

### Test via API
```bash
curl http://localhost:8000/api/ai/status
```

## Common Commands

### Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### Ollama Setup (for LiteLLM)
```bash
# Install
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull llama2
ollama pull nomic-embed-text
ollama pull llava

# List models
ollama list
```

### LiteLLM Proxy
```bash
# Simple
litellm --model ollama/llama2 --port 4000

# With config file
litellm --config litellm_config.yaml --port 4000
```

### AWS Credentials
```bash
# Configure
aws configure

# Verify
aws sts get-caller-identity
```

## Switching Providers Checklist

- [ ] Update `LLM_PROVIDER` in `.env`
- [ ] Configure provider-specific settings
- [ ] Restart backend
- [ ] Run test: `python test_llm_provider.py`
- [ ] **Re-index all policy documents** ⚠️
- [ ] Verify: `GET /api/ai/status`

## Re-indexing Policies

### Via API
```bash
curl -X POST http://localhost:8000/api/policies/1/index
curl -X POST http://localhost:8000/api/policies/2/index
# ... for each policy
```

### Via Admin UI
1. Go to `http://localhost:3000/admin/policies`
2. Click "Re-index" button for each policy

## Troubleshooting

### OpenAI: Invalid API Key
```bash
# Check key is set
echo $OPENAI_API_KEY

# Verify key at: https://platform.openai.com/api-keys
```

### LiteLLM: Connection Refused
```bash
# Check if proxy is running
curl http://localhost:4000/health

# Check if Ollama is running
ollama list

# Start LiteLLM
litellm --model ollama/llama2 --port 4000
```

### Bedrock: Access Denied
```bash
# Check credentials
aws sts get-caller-identity

# Check model access in Bedrock console
aws bedrock list-foundation-models --region us-east-1
```

### Wrong Provider Loaded
```bash
# Check .env
cat .env | grep LLM_PROVIDER

# Restart backend
docker-compose restart backend
```

## Model Recommendations

| Use Case | Provider | Model | Notes |
|----------|----------|-------|-------|
| Production | OpenAI | gpt-4o-mini | Best balance |
| Development | LiteLLM | llama2 | Free, fast |
| High Quality | OpenAI | gpt-4o | More expensive |
| Privacy | LiteLLM | llama3 | Stays local |
| Enterprise | Bedrock | claude-3-sonnet | Compliance |

## Performance Tips

### OpenAI
- Use `gpt-4o-mini` for cost efficiency
- Batch embeddings when possible
- Monitor usage in OpenAI dashboard

### LiteLLM
- Use GPU for faster inference
- Consider `llama2` (7B) vs `llama3` (8B)
- Adjust `max_tokens` for speed

### Bedrock
- Choose appropriate region
- Use `claude-3-haiku` for speed
- Use `claude-3-opus` for quality

## Security Best Practices

### OpenAI
- Rotate API keys regularly
- Use environment variables, never hardcode
- Monitor usage for anomalies

### LiteLLM
- Secure proxy with authentication
- Use firewall to restrict access
- Keep Ollama updated

### Bedrock
- Use IAM roles instead of keys
- Enable CloudTrail logging
- Use VPC endpoints for isolation

## Files to Review

| File | Purpose |
|------|---------|
| `backend/app/config.py` | Configuration settings |
| `backend/app/services/llm_factory.py` | Provider implementations |
| `backend/app/services/ai_service.py` | AI suggestion logic |
| `backend/app/services/rag_service.py` | RAG embeddings |
| `backend/docs/MULTI_PROVIDER_LLM.md` | Complete guide |
| `backend/test_llm_provider.py` | Test script |

## Support

- 📖 Full Guide: `backend/docs/MULTI_PROVIDER_LLM.md`
- 🧪 Test: `python backend/test_llm_provider.py`
- 🔍 Status: `GET /api/ai/status`
- 📊 Logs: `docker-compose logs backend`

---

**Last Updated:** Phase 3  
**Providers Supported:** OpenAI, LiteLLM, AWS Bedrock
