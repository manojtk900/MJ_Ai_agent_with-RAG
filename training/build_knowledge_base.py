"""
Knowledge Base Builder for MJ AI Assistant.
Crawls project markdown files and knowledge/ directory, builds datasets, and precomputes vector embeddings.
"""
import json
import os
import sys
import time
from pathlib import Path

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

from app.agents.intelligence.rag import rag_engine

KNOWLEDGE_DIR = BASE_DIR / "knowledge"
DATASETS_DIR = BASE_DIR / "training" / "datasets"
RAG_DATASET_FILE = DATASETS_DIR / "mj_rag_dataset.jsonl"


def build_knowledge_dataset():
    print("=" * 65)
    print("  MJ AI ASSISTANT — KNOWLEDGE BASE & RAG BUILDER")
    print("=" * 65)

    start_time = time.monotonic()
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Build Vector Index
    print("\n[Step 1] Indexing static knowledge repository...")
    chunk_count = rag_engine.build_index()
    print(f"  -> Successfully indexed {chunk_count} document chunks.")

    # 2. Export to mj_rag_dataset.jsonl
    print("\n[Step 2] Exporting to training/datasets/mj_rag_dataset.jsonl...")
    exported_count = 0
    with open(RAG_DATASET_FILE, "w", encoding="utf-8") as f:
        for chunk in rag_engine.chunks:
            record = {
                "id": chunk.id,
                "text": chunk.text,
                "source_file": chunk.source_file,
                "category": chunk.category,
                "metadata": chunk.metadata,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            exported_count += 1

    print(f"  -> Exported {exported_count} RAG records to {RAG_DATASET_FILE}")

    # 3. Test Retrieval Verification
    print("\n[Step 3] Verifying semantic retrieval accuracy...")
    test_queries = [
        "What is the accuracy of the intent model?",
        "What is the architecture of MJ assistant?",
        "What tools are available for desktop automation?",
        "Explain the transformer architecture",
    ]

    for q in test_queries:
        res = rag_engine.search(q, top_k=2)
        print(f"\n  [Query] \"{q}\"")
        print(f"    Confidence: {res.confidence:.4f}")
        if res.citations:
            print(f"    Top Source: {res.citations[0].source_file}")
            print(f"    Excerpt:    {res.citations[0].excerpt}")

    elapsed = time.monotonic() - start_time
    print("\n" + "=" * 65)
    print(f"  KNOWLEDGE BASE BUILD COMPLETE ({elapsed:.2f}s)")
    print("=" * 65)


if __name__ == "__main__":
    build_knowledge_dataset()
