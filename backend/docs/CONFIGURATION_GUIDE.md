# Environment Configuration Guide

## Overview

All configuration values must be set in your `.env` file. There are **no default values in code** - this ensures explicit configuration and prevents configuration drift.

## Creating Your .env File

### Step 1: Copy the Template

```bash
# From project root
cp backend/.env.example backend/.env

# Or create manually
cd backend
touch .env
```

### Step 2: Configure Based on Your Provider

Choose **ONE** of the three provider configurations below.

---

## Configuration Option 1: OpenAI (Recommended for Getting Started)

**Use when:** You want the easiest setup with cloud-based AI

### Minimal .env Configuration

```env
# Database
DATABASE_URL=sqlite:///./data/ai_security_review.db

# Application
APP_TITLE=AI/GenAI Security Review
APP_VERSION=0.2.0
APP_ENV=development
DEBUG=true
CORS_ORIGINS=http://localhost:3000

# Uploads
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE_MB=10

# LLM Provider Selection
LLM_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-YOUR_API_KEY_HERE
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# LiteLLM (not used, but required)
LITELLM_API_BASE=http://localhost:4000
LITELLM_API_KEY=sk-1234
LITELLM_MODEL_ID=ollama/llama2
LITELLM_VISION_MODEL_ID=ollama/llava
LITELLM_EMBEDDING_MODEL=ollama/nomic-embed-text

# Bedrock (not used, but required)
BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# AI Settings
AI_SUGGESTION_ENABLED=true
RAG_CHUNK_SIZE=800
RAG_CHUNK_OVERLAP=100
RAG_TOP_K=5
```

### What You Need to Change
1. Set `OPENAI_API_KEY` to your actual OpenAI API key
2. Optionally change `OPENAI_MODEL` (gpt-4o, gpt-4o-mini, gpt-3.5-turbo)
3. Leave other provider settings as-is (they won't be used)

---

## Configuration Option 2: LiteLLM (Local/Self-Hosted)

**Use when:** You want free, private, local AI

### Prerequisites
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull llama2
ollama pull nomic-embed-text

# Install and start LiteLLM
pip install litellm[proxy]
litellm --model ollama/llama2 --port 4000
```

### Full .env Configuration

```env
# Database
DATABASE_URL=sqlite:///./data/ai_security_review.db

# Application
APP_TITLE=AI/GenAI Security Review
APP_VERSION=0.2.0
APP_ENV=development
DEBUG=true
CORS_ORIGINS=http://localhost:3000

# Uploads
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE_MB=10

# LLM Provider Selection
LLM_PROVIDER=litellm

# OpenAI (not used, but required)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# LiteLLM Configuration
LITELLM_API_BASE=http://localhost:4000
LITELLM_API_KEY=sk-1234
LITELLM_MODEL_ID=ollama/llama2
LITELLM_VISION_MODEL_ID=ollama/llava
LITELLM_EMBEDDING_MODEL=ollama/nomic-embed-text

# Bedrock (not used, but required)
BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# AI Settings
AI_SUGGESTION_ENABLED=true
RAG_CHUNK_SIZE=800
RAG_CHUNK_OVERLAP=100
RAG_TOP_K=5
```

### What You Need to Change
1. Set `LLM_PROVIDER=litellm`
2. Update `LITELLM_API_BASE` if using different port
3. Change `LITELLM_MODEL_ID` to your preferred model
4. Leave other provider settings as-is

### Alternative Models

```env
# For better quality (slower)
LITELLM_MODEL_ID=ollama/llama3
LITELLM_EMBEDDING_MODEL=ollama/nomic-embed-text

# For code-heavy questions
LITELLM_MODEL_ID=ollama/codellama
LITELLM_EMBEDDING_MODEL=ollama/nomic-embed-text

# For fastest responses
LITELLM_MODEL_ID=ollama/mistral
LITELLM_EMBEDDING_MODEL=ollama/all-minilm
```

---

## Configuration Option 3: AWS Bedrock (Enterprise)

**Use when:** You need enterprise compliance and AWS integration

### Prerequisites
```bash
# Configure AWS credentials
aws configure

# Or set in .env (see below)
```

### Full .env Configuration

```env
# Database
DATABASE_URL=sqlite:///./data/ai_security_review.db

# Application
APP_TITLE=AI/GenAI Security Review
APP_VERSION=0.2.0
APP_ENV=development
DEBUG=true
CORS_ORIGINS=http://localhost:3000

# Uploads
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE_MB=10

# LLM Provider Selection
LLM_PROVIDER=bedrock

# OpenAI (not used, but required)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# LiteLLM (not used, but required)
LITELLM_API_BASE=http://localhost:4000
LITELLM_API_KEY=sk-1234
LITELLM_MODEL_ID=ollama/llama2
LITELLM_VISION_MODEL_ID=ollama/llava
LITELLM_EMBEDDING_MODEL=ollama/nomic-embed-text

# AWS Bedrock Configuration
BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...

# AI Settings
AI_SUGGESTION_ENABLED=true
RAG_CHUNK_SIZE=800
RAG_CHUNK_OVERLAP=100
RAG_TOP_K=5
```

### What You Need to Change
1. Set `LLM_PROVIDER=bedrock`
2. Update `BEDROCK_REGION` to your AWS region
3. Set `BEDROCK_MODEL_ID` to your chosen model
4. Add `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` OR use IAM roles

### Using IAM Roles (Recommended)

If running on AWS (EC2, ECS, Lambda), leave credentials empty:

```env
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
```

The SDK will automatically use the instance/task IAM role.

### Alternative Models

```env
# Claude 3 Haiku (fastest, cheapest)
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

# Claude 3 Sonnet (balanced)
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Claude 3 Opus (highest quality)
BEDROCK_MODEL_ID=anthropic.claude-3-opus-20240229-v1:0

# Claude 2
BEDROCK_MODEL_ID=anthropic.claude-v2:1
```

---

## Configuration Reference

### Required for All Providers

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `DATABASE_URL` | string | SQLite database path | `sqlite:///./data/ai_security_review.db` |
| `APP_TITLE` | string | Application title | `AI/GenAI Security Review` |
| `APP_VERSION` | string | Version number | `0.2.0` |
| `APP_ENV` | string | Environment name | `development`, `staging`, `production` |
| `DEBUG` | boolean | Debug mode | `true`, `false` |
| `CORS_ORIGINS` | string | Allowed CORS origins | `http://localhost:3000` |
| `UPLOAD_DIR` | string | Upload directory | `./uploads` |
| `MAX_UPLOAD_SIZE_MB` | integer | Max upload size | `10` |
| `LLM_PROVIDER` | string | Active provider | `openai`, `litellm`, `bedrock` |

### OpenAI Settings

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `OPENAI_API_KEY` | string | OpenAI API key | `sk-proj-...` |
| `OPENAI_MODEL` | string | Chat model | `gpt-4o-mini`, `gpt-4o` |
| `OPENAI_EMBEDDING_MODEL` | string | Embedding model | `text-embedding-3-small` |

### LiteLLM Settings

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `LITELLM_API_BASE` | string | LiteLLM proxy URL | `http://localhost:4000` |
| `LITELLM_API_KEY` | string | API key (if required) | `sk-1234` |
| `LITELLM_MODEL_ID` | string | Chat model | `ollama/llama2` |
| `LITELLM_VISION_MODEL_ID` | string | Vision model | `ollama/llava` |
| `LITELLM_EMBEDDING_MODEL` | string | Embedding model | `ollama/nomic-embed-text` |

### Bedrock Settings

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `BEDROCK_REGION` | string | AWS region | `us-east-1` |
| `BEDROCK_MODEL_ID` | string | Chat model ID | `anthropic.claude-3-sonnet-...` |
| `BEDROCK_EMBEDDING_MODEL_ID` | string | Embedding model | `amazon.titan-embed-text-v1` |
| `AWS_ACCESS_KEY_ID` | string | AWS access key | `AKIA...` (optional) |
| `AWS_SECRET_ACCESS_KEY` | string | AWS secret key | `...` (optional) |

### AI Settings

| Variable | Type | Description | Default |
|----------|------|-------------|---------|
| `AI_SUGGESTION_ENABLED` | boolean | Enable AI features | `true` |
| `RAG_CHUNK_SIZE` | integer | Document chunk size | `800` |
| `RAG_CHUNK_OVERLAP` | integer | Chunk overlap | `100` |
| `RAG_TOP_K` | integer | Top K results for RAG | `5` |

---

## Why All Settings Are Required

### Design Decision

We removed all default values from `config.py` to ensure:

1. **Explicit Configuration** - No hidden defaults
2. **Environment Parity** - Dev/staging/prod use same config structure
3. **Security** - No hardcoded credentials
4. **Flexibility** - Easy to change any value
5. **Documentation** - All options visible in .env

### Validation

The application will **fail to start** if required values are missing:

```python
# If you forget to set a value, you'll get a clear error:
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
OPENAI_API_KEY
  Field required [type=missing, input_value={...}, input_type=dict]
```

This is **intentional** - better to fail fast than use incorrect defaults.

---

## Testing Your Configuration

### 1. Check Configuration Loads

```bash
cd backend
python -c "from app.config import settings; print('✓ Config loaded')"
```

### 2. Test Provider

```bash
python test_llm_provider.py
```

Expected output:
```
==============================================================
LLM Provider Configuration Test
==============================================================

1. Provider Configuration:
   Provider: openai
   AI Enabled: True
   Configured: True

✓ All tests passed!
```

### 3. Check API Status

```bash
# Start backend
uvicorn app.main:app --reload

# In another terminal
curl http://localhost:8000/api/ai/status
```

---

## Common Mistakes

### ❌ Wrong: Leaving empty when required
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=
```
**Error:** Provider will be "not configured"

### ✅ Correct: Set actual values
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-abc123...
```

### ❌ Wrong: Missing quotes for special characters
```env
APP_TITLE=AI/GenAI Security Review  # May cause issues
```

### ✅ Correct: Use quotes
```env
APP_TITLE="AI/GenAI Security Review"
```

### ❌ Wrong: Spaces around equals
```env
LLM_PROVIDER = openai
```

### ✅ Correct: No spaces
```env
LLM_PROVIDER=openai
```

---

## Switching Providers

To switch from one provider to another:

1. **Change `LLM_PROVIDER`** in `.env`
2. **Update provider-specific settings**
3. **Restart backend**
4. **Re-index policy documents** ⚠️

Example:

```bash
# In .env, change:
# From: LLM_PROVIDER=openai
# To:   LLM_PROVIDER=litellm

# Restart
docker-compose restart backend

# Re-index policies (important!)
# Go to Admin > Policies > Click "Re-index" for each
```

---

## Environment-Specific Configurations

### Development

```env
APP_ENV=development
DEBUG=true
LLM_PROVIDER=litellm  # Use local for dev (free!)
```

### Staging

```env
APP_ENV=staging
DEBUG=false
LLM_PROVIDER=openai  # Use cloud for staging
```

### Production

```env
APP_ENV=production
DEBUG=false
LLM_PROVIDER=bedrock  # Use enterprise for production
```

---

## Security Best Practices

1. **Never commit `.env`** - Add to `.gitignore`
2. **Use environment-specific files** - `.env.dev`, `.env.prod`
3. **Rotate API keys** - Regularly update credentials
4. **Use IAM roles** - When possible (AWS)
5. **Encrypt sensitive files** - Use tools like `git-crypt`
6. **Audit access** - Track who has access to `.env`

---

## Troubleshooting

### Application won't start

```bash
# Check for validation errors
python -c "from app.config import settings"

# Common issues:
# - Missing required field
# - Typo in variable name
# - Wrong boolean value (use true/false, not True/False)
```

### Provider not working

```bash
# Test specific provider
python test_llm_provider.py

# Check API status
curl http://localhost:8000/api/ai/status
```

### Can't find .env file

```bash
# Ensure .env is in backend/ directory
ls -la backend/.env

# If missing, create it
cp backend/.env.example backend/.env
```

---

## Summary

✅ **All configuration in .env** - No defaults in code  
✅ **Explicit is better** - Know what you're configuring  
✅ **Fail fast** - Missing config = clear error  
✅ **Environment parity** - Same structure everywhere  
✅ **Secure by design** - No hardcoded secrets  

**Next:** Copy `.env.example` to `.env` and configure your preferred provider!
