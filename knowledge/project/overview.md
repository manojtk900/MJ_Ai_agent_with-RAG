# MJ AI Assistant — Project Overview

## 1. Executive Summary
**MJ AI Assistant** (Mind Jarvis) is an offline-capable, high-performance AI Operating System Assistant designed by Manoj. It integrates ultra-fast deterministic machine learning command routing with deep local and cloud reasoning capabilities.

## 2. Core Capabilities
1. **Deterministic OS Command Execution**: Executes desktop actions (YouTube search, Google search, VS Code, Calculator, Notepad, GitHub) in ~25-50ms CPU inference time.
2. **Local Zero-Cost RAG**: Powered by `sentence-transformers/all-MiniLM-L6-v2` embedding project documentation and architecture without paid API overhead.
3. **Multi-Agent Fleet**: Comprises 15 specialized agents orchestrated via LangGraph.
4. **Resilient Intelligence Agent**: Robust question answering, coding assistance, and reasoning that never crashes when external LLMs (Ollama) are offline.
5. **Continuous Learning**: Records anonymized execution traces for future parameter-efficient LoRA fine-tuning.

## 3. Technology Stack
- **Backend**: FastAPI, Python 3.12, LangGraph, PyTorch, Hugging Face Transformers, Sentence-Transformers.
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide Icons.
- **ML Models**: Fine-tuned DistilBERT Sequence Classifier & Token Classifier.
