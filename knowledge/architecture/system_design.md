# MJ AI Assistant — System Architecture & Design

## 1. Dual-Layer Brain Architecture
MJ operates using a hierarchical two-tier intelligence architecture:
- **Tier 1: Fast Brain Stem (ML Router)**:
  - DistilBERT Sequence Classifier (Intent detection ~99.45% accuracy).
  - DistilBERT Token Classifier (Named Entity Recognition 1.00 F1 score).
  - Executes local deterministic actions in ~25ms on standard laptop CPU.
- **Tier 2: Reasoning & Intelligence Agent**:
  - Activated for knowledge questions, general conversation, coding assistance, and project queries.
  - Combines Local Zero-Cost RAG with multi-tier LLM fallback (Ollama $\to$ Cloud Free API $\to$ Local RAG Synthesis $\to$ Offline Engine).

## 2. Query Routing & "DO NOT ACT" Filter
The `RouterGate` ensures non-action queries are never converted into desktop actions:
- `ACTION`: Direct OS tool execution (confidence $\ge 0.90$ for low risk).
- `KNOWLEDGE_PROJECT`: Local RAG semantic search over `knowledge/` and project documentation.
- `KNOWLEDGE_WORLD`: Real-time information via Web Search + LLM.
- `CODING`: Code generation, review, and debugging.
- `PLANNING`: Career guidance, learning roadmaps, and preparation steps.
- `CONFIRMATION_REQUIRED`: Guarded operations (`git push`, `delete file`, `send email`).

## 3. LangGraph Orchestration Loop
The system uses a bounded ReAct execution graph with a maximum step limit (`MAX_STEPS = 5`) and 30-second request timeout to prevent infinite loops.
