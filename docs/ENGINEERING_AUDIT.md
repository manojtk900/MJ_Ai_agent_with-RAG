# MJ AI Assistant — Phase 0 Engineering Audit

**Audit Date**: August 2026  
**Auditor**: Lead AI Systems Engineer  
**Repository Path**: `D:\Ai_ajent\mj-ai-assistant`

---

## 1. Current Architecture Overview

MJ AI Assistant is structured as a dual-layer AI operating system assistant:
- **Fast Deterministic Layer ("Brain Stem")**: Fine-tuned DistilBERT models for Intent Classification (`training/exports/mj_intent_model/` / `backend/app/ml_models/mj_intent_model/`) with ~99.45% accuracy and Token Classification NER (`backend/app/ml_models/mj_entity_model/`) with ~1.00 F1 score. Operates locally in ~25-50ms CPU inference time.
- **Workflow & Agent Orchestration**: LangGraph state machine with ReAct loop (`backend/app/core/langgraph/workflow.py`).
- **Tool Registry**: Central tool executor in `backend/app/tools/tool_registry.py` and `backend/app/agents/desktop/tools.py` executing OS app launches, browser URL navigation, Google search, YouTube search, Git actions, Gmail summaries, and task scheduling.
- **FastAPI Backend**: Endpoints under `backend/app/api/` serving chat, agents, tasks, memory, and ML telemetry.
- **React Frontend**: Modern cyber-HUD interface in `frontend/src/` with `HealthPanel`, `MissionLog`, `JarvisOrb`.

---

## 2. Working Components Verified
- **DistilBERT Intent Classifier**: Successfully resident in RAM, predicting intents in ~25ms.
- **DistilBERT Entity Extractor**: Accurately extracting spans (`query`, `app_name`, `email`, `task`, `repo`).
- **Desktop Agent Actions**:
  - `open youtube and search <query>` $\to$ `youtube_search`
  - `google <query>` $\to$ `google_search`
  - `open github`, `open vscode`, `open calculator`, `open notepad`
  - Action chaining (`open youtube and search kannada songs`)
- **Task Scheduling & Memory Agent**: In-memory and tool dispatch working.
- **48 out of 50 backend unit tests**: Passing without regressions.

---

## 3. Diagnosed Failures & Root Causes

### Failure A: Ollama Connection Crash (`Cannot connect to host localhost:11434`)
- **Root Cause**: `backend/app/services/llm.py` defaults to `ChatOllama` on port 11434 with a 300s timeout. When Ollama is not actively running as a daemon on the user's laptop, calling `ainvoke` throws unhandled connection errors.
- **Fix Required**: Multi-tier resilient fallback with circuit breaker. If Ollama fails 3 times, mark as `OFFLINE` and cool down for 30s; seamlessly route to Cloud API (Groq/Gemini if key exists), Local RAG direct extraction, or Offline Deterministic Knowledge Engine.

### Failure B: Conversational / Knowledge Questions Misrouting to `open_app()`
- **Root Cause**: When the Intent model is uncertain or when `DesktopAgent` runs on arbitrary text with `open_desktop_app(clean_cmd)` as a fallback, prompts like *"how to prepare for new AI jobs"* or *"who is Yash"* end up trying to execute `open_app("how to prepare for new AI jobs")`.
- **Fix Required**: An explicit **Query Router Gate ("DO NOT ACT" filter)** that strictly partitions queries into `ACTION`, `KNOWLEDGE_PROJECT`, `KNOWLEDGE_WORLD`, `CODING`, `CONVERSATION`, `PLANNING`, `CONFIRMATION_REQUIRED`, and `CLARIFICATION_REQUIRED`. Only verified application targets can ever trigger `open_desktop_app()`.

### Failure C: Unit Test Failures in `test_desktop_agent.py`
- **Root Cause**: `_launch_url_nonblocking` on Windows used `os.system('start "" ...')` instead of `webbrowser.open()`, bypassing the `patch("webbrowser.open")` mock in tests.
- **Fix Required**: Call `webbrowser.open(url, new=2)` so test mocks capture calls properly across all platforms.

---

## 4. Dependency & Model Status

| Package | Installed Version | Status |
| :--- | :--- | :--- |
| `torch` | 2.13.0+cpu | Verified (CPU inference ready) |
| `transformers` | 4.46.3 | Verified |
| `sentence-transformers` | 3.3.1 | Verified (`all-MiniLM-L6-v2` ready) |
| `pypdf` | 5.1.0 | Verified |
| `fastapi` | 0.115.6 | Verified |
| `pydantic` | 2.13.4 | Verified (V2 schemas supported) |
| `langgraph` | 0.2.67+ | Verified |

---

## 5. Strict Implementation Order

1. **PHASE 1 — Router Gate & Confidence/Risk Matrix** (`backend/app/agents/intelligence/router_gate.py`)
2. **PHASE 2 — Tool Registry Upgrade & Pydantic Schemas** (`backend/app/tools/tool_registry.py`)
3. **PHASE 3 — Intelligence Agent Subsystem** (`backend/app/agents/intelligence/`)
4. **PHASE 4 — Ollama Tool Calling + Circuit Breaker + Multi-Tier Fallback**
5. **PHASE 5 — Local Zero-Cost RAG with MiniLM & Citations** (`knowledge/` & `rag.py`)
6. **PHASE 6 — Web Search vs RAG Query Router**
7. **PHASE 7 — Separation of Static RAG vs Dynamic Memory**
8. **PHASE 8 — Real Interaction Trace Recorder** (`data/traces/`)
9. **PHASE 9 — Partitioned Datasets & 500 Golden Eval Benchmark** (`training/datasets/`)
10. **PHASE 10 — Evaluation & Adversarial Tests** (`tests/`)
11. **PHASE 11 — FastAPI Endpoints & Controller Wiring**
12. **PHASE 12 — Frontend HUD Telemetry Update**
13. **PHASE 13 — Live End-to-End Test & Verification**
14. **PHASE 14 — Automated Failure Correction**
15. **PHASE 15 — Executable LoRA Training Notebook** (`training/MJ_Intelligence_Agent_Training.ipynb`)
