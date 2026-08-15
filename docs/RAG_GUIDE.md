# MJ AI Assistant — Local Zero-Cost RAG Guide

## 1. Overview
MJ AI Assistant implements a completely offline, zero-cost Retrieval-Augmented Generation (RAG) pipeline designed to index and retrieve technical documentation, architecture specifications, and training metrics with sub-50ms latency.

---

## 2. Ingestion & Indexing Architecture

### Embedding Model
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Embedding Dimension**: 384-dimensional dense vectors
- **Similarity Metric**: Cosine similarity ($\cos(\theta) = \frac{u \cdot v}{\|u\| \|v\|}$)

### Text Chunking Strategy
- **Chunk Size**: 500 characters
- **Overlap**: 50 characters
- **Metadata Preserved**: `source_file`, `chunk_index`, `category`, `char_start`, `char_end`.

---

## 3. Directory Layout
Static project documentation is stored exclusively in `knowledge/`:
```text
knowledge/
├── project/          # Project overview, requirements, features
├── architecture/     # System design, workflow diagrams, controller specs
├── agents/           # Specifications for all 15 specialized agents
├── tools/            # Tool definitions, parameters, and risk matrices
├── api/              # FastAPI endpoints and WebSocket schemas
├── training/         # ML model metrics (99.45% intent, 1.00 F1 entity)
├── documentation/    # Troubleshooting guides and installation notes
└── academic/         # Core AI concepts, transformers, RAG, and DSA notes
```

> **Note**: Dynamic user memory and personal facts are stored strictly in `app/core/memory/` and are **never** indexed in static project RAG.

---

## 4. How to Update the Knowledge Base
To re-crawl documentation and regenerate vector embeddings:
```powershell
& "D:\Ai_ajent\env312\Scripts\python.exe" training/build_knowledge_base.py
```
Or via FastAPI REST endpoint:
```http
POST /api/v1/intelligence/ingest
```
