# MJ AI Assistant — Model Setup & Training Guide

## 1. Overview
MJ AI Assistant uses two fine-tuned DistilBERT models for ultra-fast local command routing (~25ms CPU latency):
1. **Intent Classifier (`mj_intent_model`)**: Classifies user queries across 22 intent categories (~99.45% accuracy).
2. **Entity Extractor (`mj_entity_model`)**: Extracts token spans (`query`, `app_name`, `email`, `task`, `repo`, `url`) with 1.00 F1 score.

---

## 2. Recreating / Training Model Weights Locally

The repository includes all tokenizers, configuration files, dataset generators, and training notebooks.

To train the models from scratch:

### A. Intent Classification Model
Open and execute:
```bash
jupyter notebook training/MJ_Intent_Classifier.ipynb
```
Or run the training script:
- Epochs: 3
- Batch Size: 32
- Learning Rate: $2 \times 10^{-5}$
- Export Path: `training/exports/mj_intent_model/` and `backend/app/ml_models/mj_intent_model/`

### B. Named Entity Recognition (NER) Model
Open and execute:
```bash
jupyter notebook training/MJ_Entity_Extractor.ipynb
```
- Epochs: 5
- Batch Size: 16
- Learning Rate: $3 \times 10^{-5}$
- Export Path: `training/exports/mj_entity_model/` and `backend/app/ml_models/mj_entity_model/`

---

## 3. Knowledge Base & Vector Index
To build the local vector database for Local Zero-Cost RAG:
```powershell
& "D:\Ai_ajent\env312\Scripts\python.exe" training/build_knowledge_base.py
```
This indexes all markdown files in `knowledge/` into `training/datasets/mj_rag_dataset.jsonl` using `sentence-transformers/all-MiniLM-L6-v2`.

---

## 4. Hardware Requirements
- **CPU**: Dual-core x86_64 or ARM64 (Intel Core i3+, AMD Ryzen 3+, Apple Silicon).
- **RAM**: Minimum 2 GB free system memory.
- **GPU**: Optional (PyTorch runs with CPU inference in ~25ms per command).
