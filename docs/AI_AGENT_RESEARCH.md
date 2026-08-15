# AI Agent Research & Open-Source Benchmark Study

## 1. Executive Summary
This document summarizes current state-of-the-art agent architectures, tool-use datasets, and open-source personal AI systems surveyed for the development of MJ AI Assistant.

---

## 2. Key GitHub Repositories & Architectural References

### A. OpenJarvis & Desktop Assistants
- **Repository**: `open-jarvis/OpenJarvis` / `kishanrajput23/Jarvis-Desktop-Voice-Assistant`
- **License**: MIT / Apache 2.0
- **Purpose**: Local-first voice & desktop automation assistants.
- **Architectural Takeaways for MJ**: Fast deterministic voice/intent parsing paired with local LLM function execution and background task queues.

### B. Agent S & Computer Use Frameworks
- **Repository**: `simular-ai/Agent-S` / `microsoft/fara`
- **License**: Apache 2.0
- **Purpose**: Autonomous GUI interaction and Computer-Use Agents (CUA).
- **Architectural Takeaways for MJ**: Safe abstraction boundaries between OS subprocess execution and LLM tool planning.

### C. Smolagents & Lightweight Agent Loops
- **Repository**: `huggingface/smolagents`
- **License**: Apache 2.0
- **Purpose**: Minimalist code-first and tool-calling agent framework.
- **Architectural Takeaways for MJ**: Keep agent step loops strictly bounded (`MAX_STEPS = 5`) with clear Pydantic schemas.

---

## 3. Function & Tool-Use Datasets Surveyed
1. **Salesforce xLAM Dataset**: Comprehensive benchmark for structured function calling and API parameter extraction.
2. **NousResearch Hermes Tool-Calling Data**: Multi-turn tool invocation and result reflection traces.
3. **NVIDIA Nemotron Agentic Tool Use**: High-precision reasoning and safety-gated execution examples.
4. **MJ Synthetic & Real Trace Sets**:
   - `training/datasets/mj_commands.jsonl` (10,000 OS commands)
   - `training/datasets/mj_agent_tool_use.jsonl` (10,000 tool calling records)
   - `training/datasets/mj_conversation_rag.jsonl` (10,000 QA pairs)
   - `training/datasets/mj_eval_500.jsonl` (500 golden eval items)
   - `data/traces/mj_traces.jsonl` (Real execution traces)
