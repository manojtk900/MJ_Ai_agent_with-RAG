# MJ AI Assistant — Dataset, Evaluation & LoRA Training Guide

## 1. Dataset Taxonomy
All datasets are partitioned in `training/datasets/`:

1. **`mj_commands.jsonl` (10,000 records)**: Action commands with natural typos, Indian English slang, and compound multi-step chains.
2. **`mj_agent_tool_use.jsonl` (10,000 records)**: Structured Pydantic/JSON tool invocation examples.
3. **`mj_conversation_rag.jsonl` (10,000 records)**: Factual QA, coding problems, career planning, and academic questions.
4. **`mj_eval_500.jsonl` (500 records)**: **Strictly Held-Out Golden Evaluation Benchmark** never used in training.

---

## 2. Generating Datasets
To re-generate the dataset suite:
```powershell
& "D:\Ai_ajent\env312\Scripts\python.exe" training/generate_mj_agent_dataset.py
```

---

## 3. Training & Evaluation Pipeline

### A. Intent & Entity Model Maintenance
- **Intent Classifier**: `training/MJ_Intent_Classifier.ipynb` (DistilBERT ~99.45% accuracy).
- **Entity Extractor**: `training/MJ_Entity_Extractor.ipynb` (DistilBERT 1.00 F1 score).

### B. Intelligence Agent & LoRA Exploration
- **Jupyter Notebook**: `training/MJ_Intelligence_Agent_Training.ipynb`
- **LoRA Hyperparameters**:
  - Rank ($r$): 16
  - Alpha ($\alpha$): 32
  - Target Modules: `["q_proj", "v_proj", "k_proj", "o_proj"]`
  - Dropout: 0.05
  - Target Models: Small parameter models (Llama-3.2-1B, Qwen2.5-1.5B) once sufficient interaction traces are collected in `data/traces/mj_traces.jsonl`.
