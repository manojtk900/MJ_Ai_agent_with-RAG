# MJ AI Assistant — Machine Learning Models & Training Metrics

## 1. Intent Classification Model
- **Base Architecture**: `distilbert-base-uncased`
- **Output Classes**: 22 native command intents (e.g., `youtube_search`, `google_search`, `open_browser`, `open_github`, `open_vscode`, `open_calculator`, `open_notepad`, `open_application`, `send_email`, `read_email`, `create_task`, `delete_task`, `github_push`, `remember_fact`, `recall_memory`, `chat`).
- **Test Accuracy**: **99.45%** on the validation benchmark.
- **Model Path**: `training/exports/mj_intent_model/` and `backend/app/ml_models/mj_intent_model/`.
- **Inference Latency**: ~20-25 ms on CPU.

## 2. Entity Extraction Model (NER)
- **Base Architecture**: `distilbert-base-uncased` Token Classification
- **Extracted Entity Groups**: `query`, `app_name`, `email`, `task`, `repo`, `file`, `url`.
- **Overall F1 Score**: **1.00** across test evaluation tokens.
- **Model Path**: `training/exports/mj_entity_model/` and `backend/app/ml_models/mj_entity_model/`.
- **Inference Latency**: ~20-25 ms on CPU.

## 3. Combined Local ML Router Benchmark
- **Total Local ML Router Latency**: **~45-50 ms** end-to-end.
- **Model Size**: ~260 MB per model.
- **Memory Footprint**: ~520 MB RAM resident.
