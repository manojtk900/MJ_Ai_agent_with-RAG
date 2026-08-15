# MJ Intelligence Agent — Comprehensive Technical Specification

## 1. System Architecture
The **MJ Intelligence Agent** is the reasoning, project knowledge, and conversational core of the MJ AI Operating System Assistant. It sits alongside the fast DistilBERT Machine Learning Router (~25ms CPU inference) to provide resilient, offline-first intelligence.

```text
                                  ┌───────────────┐
                                  │  USER PROMPT  │
                                  └───────┬───────┘
                                          │
                                          ▼
                               ┌─────────────────────┐
                               │  ML ROUTER LAYER    │
                               │ Intent + NER (~25ms)│
                               └──────────┬──────────┘
                                          │
                  ┌───────────────────────┼───────────────────────┐
                  │                       │                       │
                  ▼                       ▼                       ▼
          ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
          │ ACTION INTENT │       │ KNOWLEDGE / QA│       │ CHAT/PLANNING │
          └───────┬───────┘       └───────┬───────┘       └───────┬───────┘
                  │                       │                       │
                  ▼                       ▼                       ▼
      ┌───────────────────────┐   ┌───────────────┐   ┌───────────────────────┐
      │  CONFIDENCE & RISK    │   │  QUERY ROUTER │   │  INTELLIGENCE AGENT   │
      │  GATING MATRIX        │   │ Web vs RAG vs │   │ Structured Reasoning  │
      │  >=0.90: Execute (LOW)│   │    Hybrid     │   │ Memory + Prompts      │
      │  0.70-0.90: Confirm   │   └───────┬───────┘   └───────────┬───────────┘
      │  <0.70: Chat/Clarify  │           │                       │
      └───────────┬───────────┘           ▼                       ▼
                  │               ┌───────────────┐   ┌───────────────────────┐
                  ▼               │   LOCAL RAG   │   │ MULTI-TIER LLM CALLER │
      ┌───────────────────────┐   │ MiniLM Embeds │   │ 1. Ollama (Tool/JSON) │
      │  TOOL REGISTRY        │   │ + Citations   │   │ 2. Groq / Gemini Free │
      │ Pydantic Schemas      │   └───────┬───────┘   │ 3. Local RAG Synthesizer
      │ Desktop, Web, Git...  │           │           │ 4. Offline Fallback   │
      └───────────┬───────────┘           │           └───────────┬───────────┘
                  │                       │                       │
                  └───────────────────────┼───────────────────────┘
                                          │
                                          ▼
                              ┌───────────────────────┐
                              │  TRACE RECORDER       │
                              │  data/traces/*.jsonl  │
                              └───────────────────────┘
```

## 2. Router Gate & "DO NOT ACT" Filtering
The `RouterGate` (`backend/app/agents/intelligence/router_gate.py`) enforces strict separation between imperative OS actions and analytical queries.
- **Conversational Queries**: *"hi"*, *"who is Yash"*, *"who is PM of India"* $\to$ Intelligence Agent.
- **Career & Planning**: *"how to prepare for new AI jobs"*, *"study roadmap for ML"* $\to$ Planning Advisor.
- **Coding Assistance**: *"write Python code to add two numbers"* $\to$ Coding Assistant.
- **Project Knowledge**: *"what model did I train"*, *"what is my intent accuracy"* $\to$ Local RAG.

## 3. Resilient Multi-Tier LLM Caller & Circuit Breaker
- **Circuit Breaker**: Detects when Ollama (`localhost:11434`) is offline. After 3 consecutive timeouts (1.5s check), it marks Ollama as offline and enters a 30-second cooldown period, preventing latency spikes.
- **Tier 1 (Local Ollama)**: Structured JSON tool calling on `http://localhost:11434`.
- **Tier 2 (Cloud Free APIs)**: Groq (`llama-3.3-70b-versatile`) and Google Gemini (`gemini-1.5-flash`).
- **Tier 3 (Local RAG Synthesis)**: Direct factual extraction from top vector-retrieved chunks.
- **Tier 4 (Offline Fallback Engine)**: Formatted responses guaranteeing zero crashes and no raw Python tracebacks.

## 4. Execution Traces & Continuous Learning
All agent interactions are automatically sanitized and logged to `data/traces/mj_traces.jsonl`. This forms the dataset used for future Parameter-Efficient Fine-Tuning (PEFT/LoRA).
