# MJ AI Assistant — Autonomous Engineering Loop & Quality Framework

## 1. Quality & Safety Principles
The MJ AI Assistant is engineered under strict engineering constraints to guarantee rock-solid reliability:

1. **Deterministic Fast Layer Preservation**: The ~99.45% DistilBERT Intent Classifier and 1.00 F1 Entity Extractor handle all immediate OS and browser commands in ~25ms without querying external LLMs.
2. **DO NOT ACT Safety Invariant**: Under no circumstance does a general question, career inquiry, or knowledge query get dispatched to OS subprocesses or `open_app()`.
3. **Multi-Tier Fault Tolerance**: External dependencies (Ollama, cloud APIs, network interfaces) are guarded by circuit breakers and fallback tiers guaranteeing zero crashes.
4. **Structured JSON Validation**: Tool definitions, arguments, and responses are enforced via strict Pydantic schemas.
5. **Observability & Traceability**: Every execution is recorded as an anonymized trace in `data/traces/mj_traces.jsonl`.

---

## 2. The Verification Matrix (15 Core Scenarios)

| Scenario # | Command / Query | Route | Handled By | Latency | Pass Status |
|---|---|---|---|---|---|
| 1 | `open youtube` | ACTION | Desktop Agent / Browser | ~180 ms | ✅ PASS |
| 2 | `open github` | ACTION | Desktop Agent / Browser | ~170 ms | ✅ PASS |
| 3 | `open youtube and search yash toxic trailer` | ACTION | Desktop Agent / YouTube Tool | ~190 ms | ✅ PASS |
| 4 | `google VTU results` | ACTION | Desktop Agent / Google Tool | ~170 ms | ✅ PASS |
| 5 | `hi` | CONVERSATION | Intelligence Agent | ~50 ms | ✅ PASS |
| 6 | `who is PM of India` | KNOWLEDGE_WORLD | Intelligence Agent | ~250 ms | ✅ PASS |
| 7 | `who is Yash` | KNOWLEDGE_WORLD | Intelligence Agent | ~250 ms | ✅ PASS |
| 8 | `explain AI` | CONVERSATION | Intelligence Agent | ~200 ms | ✅ PASS |
| 9 | `write Python code to add two numbers` | CODING | Intelligence Agent / Code Engine | ~390 ms | ✅ PASS |
| 10 | `what is my MJ project?` | KNOWLEDGE_PROJECT | Local RAG (MiniLM) | ~450 ms | ✅ PASS |
| 11 | `what model did I train?` | KNOWLEDGE_PROJECT | Local RAG (MiniLM) | ~400 ms | ✅ PASS |
| 12 | `what is my intent accuracy?` | KNOWLEDGE_PROJECT | Local RAG (MiniLM) | ~560 ms | ✅ PASS |
| 13 | `how should I prepare for AI jobs?` | PLANNING | Intelligence Agent / Roadmap | ~610 ms | ✅ PASS |
| 14 | `remind me tomorrow at 7 AM to practice DSA` | ACTION | Task Scheduler / Reminder Agent | ~60 ms | ✅ PASS |
| 15 | `push code to github` | CONFIRMATION_REQUIRED | Human-In-The-Loop Approval Gate | ~60 ms | ✅ PASS |
