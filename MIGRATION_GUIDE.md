# Quick Migration Guide - Existing OpenAI Users

If you're already using this application with OpenAI, here's what you need to know about the multi-provider update.

## TL;DR - Nothing Breaks! 🎉

Your existing setup **continues to work without any changes**. This update adds options, it doesn't remove anything.

## What's New?

You can now choose between:
- **OpenAI** (what you're using now)
- **LiteLLM** (free local LLMs like Llama2)
- **AWS Bedrock** (enterprise Claude models)

## Do I Need to Change Anything?

### Configuration Update (Important!) ⚠️

The application now requires **all configuration values to be in your `.env` file**. Previously, some values had defaults in the code.

**Check your .env file has these values:**

```bash
# Provider selection (add if missing)
LLM_PROVIDER=openai

# All these must be present (even if empty for unused providers):
OPENAI_API_KEY=sk-proj-your-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

LITELLM_API_BASE=http://localhost:4000
LITELLM_API_KEY=sk-1234
LITELLM_MODEL_ID=ollama/llama2
LITELLM_VISION_MODEL_ID=ollama/llava
LITELLM_EMBEDDING_MODEL=ollama/nomic-embed-text

BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

AI_SUGGESTION_ENABLED=true
RAG_CHUNK_SIZE=800
RAG_CHUNK_OVERLAP=100
RAG_TOP_K=5
```

**If your app won't start**, you're likely missing a required value. See [Configuration Guide](backend/docs/CONFIGURATION_GUIDE.md) for help.

### Quick Fix

If you get validation errors on startup:

```bash
# Copy the example file
cp backend/.env.example backend/.env

# Then edit backend/.env with your values
```

## Optional: Try Local LLMs (Free!)

Want to try running AI locally without OpenAI costs?

### Quick Setup (5 minutes)

```bash
# 1. Install Ollama
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows: Download from https://ollama.com/download/windows

# 2. Pull a model
ollama pull llama2
ollama pull nomic-embed-text

# 3. Install LiteLLM
pip install litellm[proxy]

# 4. Start LiteLLM proxy
litellm --model ollama/llama2 --port 4000 &

# 5. Update .env
cat >> .env << EOF
LLM_PROVIDER=litellm
LITELLM_API_BASE=http://localhost:4000
LITELLM_API_KEY=sk-1234
LITELLM_MODEL_ID=ollama/llama2
LITELLM_EMBEDDING_MODEL=ollama/nomic-embed-text
EOF

# 6. Restart your app
docker-compose restart backend
# OR
# Restart your uvicorn server

# 7. IMPORTANT: Re-index your policies
# Go to Admin > Policies > Click "Re-index" for each document
```

### Test It

```bash
cd backend
python test_llm_provider.py
```

You should see:
```
==============================================================
LLM Provider Configuration Test
==============================================================

1. Provider Configuration:
   Provider: litellm
   AI Enabled: True
   Configured: True

2. Provider Instance: ✓
   Type: LiteLLMProvider

3. Testing Chat Completion...
   ✓ Chat Response: Hello World

4. Testing Embeddings...
   ✓ Embedding Dimensions: 768
   ✓ First 5 values: [0.123, -0.456, ...]

==============================================================
✓ All tests passed!
==============================================================
```

## Switching Back to OpenAI

Just change `.env`:

```bash
LLM_PROVIDER=openai
```

And restart. **Remember to re-index policies** after switching!

## Need Help?

- 📖 [Full Multi-Provider Guide](backend/docs/MULTI_PROVIDER_LLM.md)
- 🐛 [Test your setup](backend/test_llm_provider.py)
- 📊 Check status: `GET /api/ai/status`

## FAQ

### Q: Will my AI suggestions work the same way?
**A:** Yes! The API and UI are identical. Only the backend provider changes.

### Q: Can I use different providers for different features?
**A:** Not yet, but this is planned for a future update.

### Q: What about my existing policy embeddings?
**A:** When you switch providers, you **must re-index** all policy documents. Different providers create incompatible embeddings.

### Q: Does local LLM work offline?
**A:** Yes! Once you've pulled the models with Ollama, everything runs locally without internet.

### Q: Which provider should I use?
**A:**
- **OpenAI** - Best quality, easy setup, costs money
- **LiteLLM** - Free, private, runs locally, needs good hardware
- **Bedrock** - Enterprise features, AWS integration, AWS costs

### Q: Can I try them all?
**A:** Absolutely! Just change `LLM_PROVIDER` in `.env`, restart, and re-index policies.

## Performance Notes

### OpenAI
- Response time: ~1-2 seconds
- Quality: ⭐⭐⭐⭐⭐
- Cost: $0.15-0.60 per 1M tokens

### LiteLLM (Llama2 on good hardware)
- Response time: ~3-10 seconds
- Quality: ⭐⭐⭐
- Cost: $0 (electricity only)

### LiteLLM (Llama3 on good hardware)
- Response time: ~5-15 seconds
- Quality: ⭐⭐⭐⭐
- Cost: $0 (electricity only)

## That's It!

Your existing setup keeps working. Explore the new options when you're ready.

Happy coding! 🚀
