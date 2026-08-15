# MJ AI Assistant

> **Agentic Operating System** — Not a chatbot. An autonomous, multi-agent AI platform.

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-FF6B35?style=flat)](https://langchain-ai.github.io/langgraph/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL+pgvector-17-336791?style=flat&logo=postgresql)](https://pgvector.github.io)

---

## What is MJ AI Assistant?

MJ AI Assistant is a **production-grade Agentic Operating System** powered by 15 specialized AI agents and a fast machine learning brain stem:

```
User Input → ML Router (~25ms) → Router Gate → Tool Registry (Actions)
                                       └──→ Intelligence Agent (RAG + Multi-Tier LLM)
```

## ✨ Features

- **Fast ML Command Router**: Fine-tuned DistilBERT Intent Classifier (~99.45% accuracy) & Entity Extractor (1.00 F1) with ~25ms CPU latency.
- **MJ Intelligence Agent**: Robust conversational intelligence, coding assistance, and career planning that never crashes when external LLMs are offline.
- **Local Zero-Cost RAG**: Powered by `sentence-transformers/all-MiniLM-L6-v2` with dense cosine indexing and exact source citations.
- **Router Gate & "DO NOT ACT" Filter**: Guarantees conversational and planning queries never mistakenly execute desktop tools like `open_app()`.
- **Structured Tool Registry**: Pydantic schema validation, risk tiers (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), and human confirmation gating.
- **Multi-Tier LLM Fallback & Circuit Breaker**: Ollama $\to$ Free Cloud API (Groq/Gemini) $\to$ Local RAG Direct Synthesis $\to$ Offline Engine.
- **15 Specialized Agents Fleet**: Controller, Intelligence, Desktop, Planner, Search, Research, Memory, System, Browser, Email, Reminder, File, Voice, Execution, Scheduler.
- **Continuous Learning**: Records anonymized execution traces to `data/traces/mj_traces.jsonl` for parameter-efficient LoRA fine-tuning.
- **Categorized Dataset Suite**: 30,500 records across commands, tool use, conversation RAG, and a held-out 500 Golden Eval benchmark.

## 🚀 Quick Start

```bash
# 1. Clone and configure
git clone <repo-url> mj-ai-assistant
cd mj-ai-assistant
cp .env.example .env
# Edit .env — add your API keys

# 2. Start infrastructure
docker compose -f docker/docker-compose.yml up -d postgres redis

# 3. Backend
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# 4. Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## 📁 Project Structure

```
mj-ai-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI entry point
│   │   ├── config.py             # Settings (pydantic-settings)
│   │   ├── agents/               # All 15 + 1 agents
│   │   │   ├── base.py           # BaseAgent (ReAct loop)
│   │   │   ├── controller/       # Intent detection
│   │   │   ├── planner/          # Goal decomposition
│   │   │   ├── chat/             # Conversation
│   │   │   ├── search/           # Web search
│   │   │   ├── research/         # Deep research
│   │   │   ├── memory/           # pgvector memory
│   │   │   ├── system/           # OS operations
│   │   │   ├── browser/          # Playwright
│   │   │   ├── email/            # SMTP/IMAP
│   │   │   ├── reminder/         # Reminders
│   │   │   ├── file/             # PDF/DOCX/PPTX
│   │   │   ├── voice/            # Whisper + TTS
│   │   │   ├── execution/        # GitHub + coding
│   │   │   ├── scheduler/        # Cron jobs
│   │   │   ├── project_manager/  # Projects
│   │   │   └── reflection/       # Quality eval
│   │   ├── core/
│   │   │   ├── langgraph/        # Workflow + state + nodes
│   │   │   ├── mcp/              # MCP gateway + registry + servers
│   │   │   ├── memory/           # short_term (Redis) + long_term (pgvector)
│   │   │   ├── context/          # Context Engineering Engine
│   │   │   ├── a2a/              # Agent-to-Agent protocol
│   │   │   └── observability/    # OpenTelemetry setup
│   │   ├── api/
│   │   │   ├── routes/           # chat, agents, memory, voice, tasks, health
│   │   │   └── middleware/       # auth, audit
│   │   ├── models/               # SQLAlchemy models (pgvector)
│   │   ├── services/             # llm.py, embedding.py, background.py
│   │   └── skills/               # Skill marketplace
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/                # Dashboard, Chat, Memory, Tasks, Projects, Settings
│   │   ├── components/           # Layout, Chat, Agents, Workflow
│   │   ├── store/                # Zustand state (chat, agents)
│   │   ├── hooks/                # useChat, useVoice
│   │   └── services/             # api.js, websocket.js
│   └── package.json
├── docker/
│   └── docker-compose.yml        # Full stack (PG+pgvector, Redis, Backend, Frontend, OTel, Prometheus, Grafana)
├── .env.example                  # All environment variables documented
└── prd.md                        # Full Product Requirements Document
```

## 🤖 Agent Architecture

| Agent | Trigger Intent | Key Tools |
|-------|---------------|-----------|
| Controller | All | Intent detection, Context Engine |
| Planner | Complex tasks | LLM goal decomposition |
| Chat | conversation, coding | GPT-4o/Gemini/Claude |
| Search | web_search | Tavily, DuckDuckGo |
| Research | deep_research | Multi-source + synthesis |
| Memory | memory_store/retrieve | pgvector cosine search |
| System | system_operation | subprocess, filesystem |
| Browser | browser_automation | Playwright |
| Email | email_read/send | IMAP, SMTP |
| Reminder | reminder | NLP date parsing |
| File | pdf_analysis, file_write | pypdf, python-docx, pptx |
| Voice | voice_processing | Whisper STT, OpenAI TTS |
| Execution | code_generation, github | PyGithub, subprocess |
| Scheduler | schedule_task | Celery Beat, croniter |
| Project Manager | project_management | LLM planning |
| Reflection | (internal) | Quality scoring, retry |

## 🔧 Configuration

Key `.env` settings:

```bash
# Choose your LLM provider
DEFAULT_LLM_PROVIDER=openai   # openai | gemini | claude | ollama
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
ANTHROPIC_API_KEY=sk-ant-...

# Search tools
TAVILY_API_KEY=tvly-...

# GitHub automation
GITHUB_TOKEN=ghp_...

# Autonomy (0=chat, 1=ask, 2=auto safe, 3=full auto)
DEFAULT_AUTONOMY_LEVEL=1
```

## 📊 Observability Stack

| Tool | Purpose | URL |
|------|---------|-----|
| FastAPI Docs | API exploration | http://localhost:8000/docs |
| Prometheus | Metrics | http://localhost:9090 |
| Grafana | Dashboards | http://localhost:3001 |
| Flower | Celery workers | http://localhost:5555 |
| LangSmith | LangGraph traces | https://smith.langchain.com |

## 🗺️ Roadmap

- **Phase 1** (Current): Controller, Chat, Search, Memory, Execution agents
- **Phase 2**: Planner, Reflection, System, File agents
- **Phase 3**: Browser, Email, Reminder, Scheduler, Voice agents
- **Phase 4**: Research agent, A2A protocol, Observability
- **Phase 5**: Production security, Kubernetes
- **Phase 6**: AgriGuard expansion (Disease, Weather, Agriculture, Finance, Government agents)

## 📄 License

MIT — Built for AgriGuard AI ecosystem
