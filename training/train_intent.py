"""
MJ AI Assistant — Intent Classification Model Training
Uses DistilBERT for fast, accurate intent classification.

Run:
    pip install transformers datasets torch scikit-learn accelerate
    python train_intent.py

Output: exports/mj_intent_model/
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from collections import Counter

import numpy as np
from datasets import Dataset, DatasetDict, ClassLabel, Value, Features
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding,
)
import torch

# ── Config ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATASET_PATH = BASE_DIR / "datasets" / "intents.jsonl"
EXPORT_PATH = BASE_DIR / "exports" / "mj_intent_model"
MODEL_NAME = "distilbert-base-uncased"
MAX_LENGTH = 128
BATCH_SIZE = 32
EPOCHS = 5
LEARNING_RATE = 2e-5
SEED = 42

# ── Load Data ─────────────────────────────────────────────────────────────────
def load_jsonl(path: Path) -> list[dict]:
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def build_dataset(records: list[dict]) -> tuple[DatasetDict, list[str]]:
    texts = [r["text"] for r in records]
    raw_labels = [r["intent"] for r in records]

    # Build label2id / id2label
    label_names = sorted(set(raw_labels))
    label2id = {l: i for i, l in enumerate(label_names)}
    id2label = {i: l for l, i in label2id.items()}

    label_ids = [label2id[l] for l in raw_labels]

    # Train / val / test split: 80 / 10 / 10
    train_texts, temp_texts, train_labels, temp_labels = train_test_split(
        texts, label_ids, test_size=0.2, random_state=SEED, stratify=label_ids
    )
    val_texts, test_texts, val_labels, test_labels = train_test_split(
        temp_texts, temp_labels, test_size=0.5, random_state=SEED, stratify=temp_labels
    )

    def make_hf_dataset(t, l):
        return Dataset.from_dict({"text": t, "label": l})

    dataset = DatasetDict({
        "train": make_hf_dataset(train_texts, train_labels),
        "validation": make_hf_dataset(val_texts, val_labels),
        "test": make_hf_dataset(test_texts, test_labels),
    })

    print(f"Train: {len(train_texts)} | Val: {len(val_texts)} | Test: {len(test_texts)}")
    print(f"Intents ({len(label_names)}): {label_names}")

    return dataset, label_names, label2id, id2label


# ── Tokenization ──────────────────────────────────────────────────────────────
def tokenize_dataset(dataset: DatasetDict, tokenizer) -> DatasetDict:
    def tokenize(batch):
        return tokenizer(batch["text"], truncation=True, max_length=MAX_LENGTH)

    return dataset.map(tokenize, batched=True, remove_columns=["text"])


# ── Metrics ───────────────────────────────────────────────────────────────────
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    acc = (preds == labels).mean()
    return {"accuracy": acc}


# ── Train ─────────────────────────────────────────────────────────────────────
def train():
    print(f"\n{'='*60}")
    print(" MJ AI Assistant — Intent Classifier Training")
    print(f"{'='*60}\n")

    if not DATASET_PATH.exists():
        print(f"ERROR: Dataset not found at {DATASET_PATH}")
        print("Run: python generate_dataset.py first")
        return

    # Load
    records = load_jsonl(DATASET_PATH)
    print(f"Loaded {len(records)} samples from {DATASET_PATH}")

    # Distribution check
    dist = Counter(r["intent"] for r in records)
    print(f"Intent classes: {len(dist)}")

    dataset, label_names, label2id, id2label = build_dataset(records)

    # Tokenizer + Model
    print(f"\nLoading model: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(label_names),
        id2label=id2label,
        label2id=label2id,
    )

    # Tokenize
    tokenized = tokenize_dataset(dataset, tokenizer)
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    # Training Args
    EXPORT_PATH.mkdir(parents=True, exist_ok=True)
    args = TrainingArguments(
        output_dir=str(EXPORT_PATH / "checkpoints"),
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=64,
        learning_rate=LEARNING_RATE,
        weight_decay=0.01,
        warmup_ratio=0.1,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
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
        compute_metrics=compute_metrics,
    )

    # Train
    print("\nStarting training...")
    trainer.train()

    # Evaluate on test set
    print("\nEvaluating on test set...")
    preds_output = trainer.predict(tokenized["test"])
    preds = np.argmax(preds_output.predictions, axis=-1)
    true_labels = preds_output.label_ids

    report = classification_report(
        true_labels, preds,
        target_names=label_names,
        digits=4,
    )
    print("\nClassification Report:")
    print(report)

    # Save classification report
    report_path = EXPORT_PATH / "classification_report.txt"
    report_path.write_text(report)
    print(f"Report saved to {report_path}")

    # Save model + tokenizer
    print(f"\nSaving model to {EXPORT_PATH}...")
    trainer.save_model(str(EXPORT_PATH))
    tokenizer.save_pretrained(str(EXPORT_PATH))

    # Save label mapping
    mapping = {"label2id": label2id, "id2label": id2label, "intents": label_names}
    with open(EXPORT_PATH / "label_mapping.json", "w") as f:
        json.dump(mapping, f, indent=2)

    print(f"\nTraining complete! Model saved to: {EXPORT_PATH}")
    print("Use predictor.py to run inference.")


if __name__ == "__main__":
    train()
