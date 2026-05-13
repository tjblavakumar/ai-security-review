# Multi-Provider LLM Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ AI Suggestion│  │ Chat Panel   │  │ Policy Mgmt  │          │
│  │    Panel     │  │              │  │              │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          │    REST API      │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Backend (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                     API Routers                          │  │
│  │  /api/ai/suggest  │  /api/ai/chat  │  /api/ai/status    │  │
│  └──────────┬──────────────┬──────────────────┬─────────────┘  │
│             │              │                  │                │
│             ▼              ▼                  ▼                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Service Layer                         │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │  │
│  │  │ AI Service   │  │ RAG Service  │  │ Question Svc │   │  │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────────┘   │  │
│  │         │                 │                              │  │
│  │         └─────────┬───────┘                              │  │
│  │                   ▼                                      │  │
│  │         ┌─────────────────────┐                          │  │
│  │         │    LLM Factory      │                          │  │
│  │         │  (get_llm_provider) │                          │  │
│  │         └─────────┬───────────┘                          │  │
│  │                   │                                      │  │
│  │     ┌─────────────┼─────────────┐                        │  │
│  │     │             │             │                        │  │
│  │     ▼             ▼             ▼                        │  │
│  │  ┌──────┐     ┌──────┐     ┌──────┐                     │  │
│  │  │OpenAI│     │LiteLLM│    │Bedrock│                    │  │
│  │  │Provider│   │Provider│   │Provider│                   │  │
│  │  └──┬───┘     └──┬───┘     └──┬───┘                     │  │
│  └─────┼───────────┼────────────┼─────────────────────────┘  │
└────────┼───────────┼────────────┼────────────────────────────┘
         │           │            │
         ▼           ▼            ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│  OpenAI    │  │  LiteLLM   │  │   AWS      │
│    API     │  │   Proxy    │  │  Bedrock   │
│            │  │            │  │            │
│ gpt-4o-mini│  │ http://    │  │ Claude 3   │
│ embeddings │  │ localhost  │  │ Titan      │
└────────────┘  │    :4000   │  └────────────┘
                │            │
                │  ┌──────┐  │
                │  │Ollama│  │
                │  │      │  │
                │  │llama2│  │
                │  │nomic │  │
                └──└──────┘──┘
```

## Provider Selection Flow

```
Application Startup
        │
        ▼
Read LLM_PROVIDER
from settings
        │
        ├─── "openai" ──────────────┐
        │                           │
        ├─── "litellm" ─────────────┤
        │                           │
        └─── "bedrock" ─────────────┤
                                    │
                                    ▼
                          ┌──────────────────┐
                          │  Create Provider │
                          │    Instance      │
                          │   (Singleton)    │
                          └──────────────────┘
                                    │
                                    ▼
                          ┌──────────────────┐
                          │ is_configured()? │
                          └────────┬─────────┘
                                   │
                        ┌──────────┴──────────┐
                        │                     │
                     Yes│                     │No
                        │                     │
                        ▼                     ▼
              ┌──────────────────┐  ┌──────────────────┐
              │  Provider Ready  │  │ Return Disabled  │
              │  for AI calls    │  │     Message      │
              └──────────────────┘  └──────────────────┘
```

## Request Flow: AI Suggestion

```
User clicks "Get AI Suggestion" in UI
        │
        ▼
POST /api/ai/suggest
        │
        ▼
┌─────────────────────┐
│  Suggestion Router  │
│  (ai.py)           │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Load Question      │
│  Load Category      │
│  Load Responses     │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  RAG Service        │
│  retrieve_context() │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  AI Service         │
│  generate_suggestion│
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  LLM Factory        │
│  get_llm_provider() │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Provider Instance  │
│  chat_completion()  │
└────────┬────────────┘
         │
         ▼
  External LLM API
  (OpenAI/LiteLLM/Bedrock)
         │
         ▼
    JSON Response
         │
         ▼
   Parse & Return
         │
         ▼
   Display in UI
```

## Request Flow: RAG Embeddings

```
Admin uploads policy document
        │
        ▼
POST /api/policies
        │
        ▼
┌─────────────────────┐
│  Policy Router      │
│  (policies.py)     │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Save to Database   │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  RAG Service        │
│  index_document()   │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  chunk_text()       │
│  (800 char chunks)  │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  LLM Factory        │
│  get_llm_provider() │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Provider Instance  │
│  get_embeddings()   │
└────────┬────────────┘
         │
         ▼
  External LLM API
  (Embedding models)
         │
         ▼
  Vector Embeddings
  [0.123, -0.456, ...]
         │
         ▼
┌─────────────────────┐
│  Save to JSON File  │
│  data/embeddings/   │
│  doc_123.json       │
└─────────────────────┘
```

## Configuration Flow

```
.env file
    │
    ▼
┌─────────────────────────────────────┐
│         LLM_PROVIDER=openai         │
│                                     │
│         OpenAI Settings:            │
│  ┌─────────────────────────────┐   │
│  │ OPENAI_API_KEY              │   │
│  │ OPENAI_MODEL                │   │
│  │ OPENAI_EMBEDDING_MODEL      │   │
│  └─────────────────────────────┘   │
│                                     │
│         LiteLLM Settings:           │
│  ┌─────────────────────────────┐   │
│  │ LITELLM_API_BASE            │   │
│  │ LITELLM_MODEL_ID            │   │
│  │ LITELLM_EMBEDDING_MODEL     │   │
│  └─────────────────────────────┘   │
│                                     │
│         Bedrock Settings:           │
│  ┌─────────────────────────────┐   │
│  │ BEDROCK_REGION              │   │
│  │ BEDROCK_MODEL_ID            │   │
│  │ BEDROCK_EMBEDDING_MODEL_ID  │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
    │
    ▼
app.config.Settings
    │
    ▼
llm_factory.get_llm_provider()
    │
    ├─── if "openai" ──────────────┐
    │                              │
    ├─── if "litellm" ─────────────┤
    │                              │
    └─── if "bedrock" ─────────────┤
                                   │
                                   ▼
                         Return Provider Instance
```

## Data Flow: Policy Search (RAG)

```
User asks question in chat
        │
        ▼
Extract keywords + context
        │
        ▼
┌─────────────────────────────────┐
│  RAG Service                    │
│  retrieve_context(query, k=5)   │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  1. Generate Query Embedding    │
│     get_llm_provider()          │
│     .get_embeddings([query])    │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  2. Load All Indexed Docs       │
│     from data/embeddings/*.json │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  3. Compute Cosine Similarity   │
│     query_emb vs all chunk_embs │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  4. Sort by Similarity          │
│     Return Top K chunks         │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  5. Format Context String       │
│     [Policy Title] (score)      │
│     Chunk text...               │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  6. Inject into Chat Prompt     │
│     System: "Use this context"  │
│     Context: [retrieved chunks] │
│     User: [question]            │
└────────┬────────────────────────┘
         │
         ▼
   Send to LLM Provider
         │
         ▼
   Context-Aware Response
```

## Class Hierarchy

```
LLMProvider (ABC)
    │
    ├── chat_completion()    [abstract]
    ├── get_embeddings()     [abstract]
    └── is_configured()      [abstract]
    
    │
    ├─── OpenAIProvider
    │       ├── chat_completion()  → OpenAI API
    │       ├── get_embeddings()   → OpenAI Embeddings API
    │       └── is_configured()    → Check OPENAI_API_KEY
    │
    ├─── LiteLLMProvider
    │       ├── chat_completion()  → LiteLLM Proxy (OpenAI-compatible)
    │       ├── get_embeddings()   → LiteLLM Proxy
    │       └── is_configured()    → Check LITELLM_API_BASE
    │
    └─── BedrockProvider
            ├── chat_completion()  → AWS Bedrock (Claude format)
            ├── get_embeddings()   → AWS Bedrock (Titan)
            └── is_configured()    → Check BEDROCK_REGION
```

## Deployment Architectures

### Option 1: Cloud-Only (OpenAI)

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────┐
│  Frontend   │
│  (Next.js)  │
└──────┬──────┘
       │ API
       ▼
┌─────────────┐
│   Backend   │
│  (FastAPI)  │
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────┐
│   OpenAI    │
│     API     │
└─────────────┘

All components can be in cloud
No local infrastructure needed
```

### Option 2: Hybrid (LiteLLM)

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────┐
│  Frontend   │
│  (Cloud)    │
└──────┬──────┘
       │ API
       ▼
┌─────────────┐
│   Backend   │
│  (Cloud)    │
└──────┬──────┘
       │ VPN/Private
       ▼
┌─────────────┐
│   LiteLLM   │
│   (Local)   │
└──────┬──────┘
       │ Local
       ▼
┌─────────────┐
│   Ollama    │
│   (Local)   │
└─────────────┘

Backend connects to local LiteLLM
All AI stays on-premise
```

### Option 3: Enterprise (Bedrock)

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────┐     AWS VPC
│  Frontend   │  ┌──────────────────┐
│   (S3)      │  │                  │
└──────┬──────┘  │  ┌─────────────┐ │
       │         │  │   Backend   │ │
       │ API     │  │   (ECS)     │ │
       └─────────┼──┤             │ │
                 │  └──────┬──────┘ │
                 │         │        │
                 │         │ Private│
                 │         ▼        │
                 │  ┌─────────────┐ │
                 │  │   Bedrock   │ │
                 │  │  (VPC Ept)  │ │
                 │  └─────────────┘ │
                 │                  │
                 └──────────────────┘

All within AWS
Private network
Compliance ready
```

## State Management

```
┌─────────────────────────────────────┐
│      Application Startup            │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  llm_factory.py                     │
│  _provider_instance = None          │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  First call to get_llm_provider()   │
└────────────────┬────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
    None?               Exists?
        │                 │
        ▼                 ▼
┌──────────────┐   ┌──────────────┐
│ Create new   │   │ Return       │
│ instance     │   │ existing     │
│ (Singleton)  │   │ instance     │
└──────┬───────┘   └──────────────┘
       │
       │ Store in
       │ _provider_instance
       │
       ▼
┌──────────────┐
│ Return       │
│ instance     │
└──────────────┘

Singleton pattern ensures:
- One instance per provider
- Configuration cached
- Efficient resource use
```

## Error Handling Flow

```
API Request
     │
     ▼
┌──────────────────┐
│ is_llm_configured│
│     ()?          │
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
  False     True
    │         │
    ▼         ▼
┌────────┐  ┌────────┐
│Return  │  │Get     │
│Disabled│  │Provider│
│Message │  └───┬────┘
└────────┘      │
                ▼
         ┌──────────────┐
         │ Try API Call │
         └──────┬───────┘
                │
         ┌──────┴──────┐
         │             │
      Success       Exception
         │             │
         ▼             ▼
   ┌─────────┐   ┌─────────┐
   │ Return  │   │ Catch & │
   │ Result  │   │ Format  │
   └─────────┘   │ Error   │
                 └────┬────┘
                      │
                      ▼
                 ┌─────────┐
                 │ Return  │
                 │ Error   │
                 │ Response│
                 └─────────┘
```

---

**Legend:**
- `│`, `─`, `┌`, `└`, `┐`, `┘` - Box drawing
- `▼` - Flow direction
- `├`, `┤` - Branches
- Square boxes - Components/Services
- Rounded corners - External services

**Last Updated:** Phase 3  
**Supported Providers:** OpenAI, LiteLLM, AWS Bedrock
