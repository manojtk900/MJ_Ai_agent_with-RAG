"""
MJ AI Assistant — Entity Extraction Model Training
Fine-tunes a token classification model (DistilBERT NER) to extract:
  query, app_name, email, task, repo, file

Run:
    python train_entities.py

Output: exports/mj_entity_model/
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

import numpy as np
from datasets import Dataset, DatasetDict
from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    TrainingArguments,
    Trainer,
    DataCollatorForTokenClassification,
)
from seqeval.metrics import classification_report as seq_classification_report
import torch

# ── Config ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATASET_PATH = BASE_DIR / "datasets" / "entities.jsonl"
EXPORT_PATH = BASE_DIR / "exports" / "mj_entity_model"
MODEL_NAME = "distilbert-base-uncased"
MAX_LENGTH = 64
BATCH_SIZE = 32
EPOCHS = 5
SEED = 42

# ── BIO Label Schema ──────────────────────────────────────────────────────────
# B-X = beginning of entity X
# I-X = inside entity X
# O   = outside any entity

ENTITY_TYPES = ["query", "app_name", "email", "task", "repo", "file", "fact"]
LABELS = ["O"] + [f"B-{e}" for e in ENTITY_TYPES] + [f"I-{e}" for e in ENTITY_TYPES]
LABEL2ID = {l: i for i, l in enumerate(LABELS)}
ID2LABEL = {i: l for l, i in LABEL2ID.items()}


def create_bio_labels(text: str, entity_value: str, entity_type: str) -> tuple[list[str], list[str]]:
    """Create word-level BIO labels by locating entity_value in text."""
    words = text.split()
    entity_words = entity_value.lower().split()
    labels = ["O"] * len(words)

    # Find entity span (case insensitive)
    lower_words = [w.lower().strip(".,!?") for w in words]
    for i in range(len(lower_words) - len(entity_words) + 1):
        if lower_words[i:i+len(entity_words)] == entity_words:
            labels[i] = f"B-{entity_type}"
            for j in range(1, len(entity_words)):
                labels[i + j] = f"I-{entity_type}"
            break

    return words, labels


def load_entity_dataset(path: Path) -> list[dict]:
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            # Detect entity key
            for etype in ENTITY_TYPES:
                if etype in r:
                    words, labels = create_bio_labels(r["text"], r[etype], etype)
                    records.append({
                        "tokens": words,
                        "ner_tags": [LABEL2ID[l] for l in labels],
                    })
                    break
    return records


def tokenize_and_align_labels(examples, tokenizer):
    """Tokenize and align BIO labels with wordpiece tokens."""
    tokenized = tokenizer(
        examples["tokens"],
        truncation=True,
        is_split_into_words=True,
        max_length=MAX_LENGTH,
    )

    all_labels = []
    for i, labels in enumerate(examples["ner_tags"]):
        word_ids = tokenized.word_ids(batch_index=i)
        aligned = []
        prev_word_id = None
        for word_id in word_ids:
            if word_id is None:
                aligned.append(-100)
            elif word_id != prev_word_id:
                aligned.append(labels[word_id])
            else:
                # For sub-tokens: convert B- to I- to avoid double B
                raw_label = LABELS[labels[word_id]]
                if raw_label.startswith("B-"):
                    aligned.append(LABEL2ID["I-" + raw_label[2:]])
                else:
                    aligned.append(labels[word_id])
            prev_word_id = word_id
        all_labels.append(aligned)

    tokenized["labels"] = all_labels
    return tokenized


def compute_seqeval_metrics(eval_pred):
    preds, labels = eval_pred
    pred_ids = np.argmax(preds, axis=-1)

    true_seqs = []
    pred_seqs = []
    for pred_row, label_row in zip(pred_ids, labels):
        true_seq = []
        pred_seq = []
        for p, l in zip(pred_row, label_row):
            if l == -100:
                continue
            true_seq.append(ID2LABEL[l])
            pred_seq.append(ID2LABEL[p])
        true_seqs.append(true_seq)
        pred_seqs.append(pred_seq)

    report = seq_classification_report(true_seqs, pred_seqs, output_dict=True)
    return {
        "f1": report.get("weighted avg", {}).get("f1-score", 0),
        "precision": report.get("weighted avg", {}).get("precision", 0),
        "recall": report.get("weighted avg", {}).get("recall", 0),
    }


def train():
    print("\n" + "="*60)
    print(" MJ AI Assistant — Entity Extraction Training")
    print("="*60 + "\n")

    if not DATASET_PATH.exists():
        print(f"ERROR: Entity dataset not found at {DATASET_PATH}")
        print("Run: python generate_dataset.py first")
        return

    records = load_entity_dataset(DATASET_PATH)
    print(f"Loaded {len(records)} entity records")

    # Split
    from sklearn.model_selection import train_test_split
    train_recs, val_recs = train_test_split(records, test_size=0.15, random_state=SEED)
    print(f"Train: {len(train_recs)} | Val: {len(val_recs)}")

    def to_hf(recs):
        return Dataset.from_dict({
            "tokens": [r["tokens"] for r in recs],
            "ner_tags": [r["ner_tags"] for r in recs],
        })

    dataset = DatasetDict({"train": to_hf(train_recs), "validation": to_hf(val_recs)})

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForTokenClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(LABELS),
        id2label=ID2LABEL,
        label2id=LABEL2ID,
    )

    tokenized = dataset.map(
        lambda ex: tokenize_and_align_labels(ex, tokenizer),
        batched=True,
        remove_columns=["tokens", "ner_tags"],
    )

    data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)

    EXPORT_PATH.mkdir(parents=True, exist_ok=True)
    args = TrainingArguments(
        output_dir=str(EXPORT_PATH / "checkpoints"),
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=64,
        learning_rate=2e-5,
        weight_decay=0.01,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        logging_steps=50,
        seed=SEED,
        fp16=torch.cuda.is_available(),
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["validation"],
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_seqeval_metrics,
    )

    print("\nStarting entity extraction training...")
    trainer.train()

    trainer.save_model(str(EXPORT_PATH))
    tokenizer.save_pretrained(str(EXPORT_PATH))

    with open(EXPORT_PATH / "label_mapping.json", "w") as f:
        json.dump({"label2id": LABEL2ID, "id2label": ID2LABEL, "entity_types": ENTITY_TYPES}, f, indent=2)

    print(f"\nEntity model saved to: {EXPORT_PATH}")


if __name__ == "__main__":
    train()
