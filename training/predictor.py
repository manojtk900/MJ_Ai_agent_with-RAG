"""
MJ AI Assistant — Real-time Intent Predictor
Load the trained model and predict intent from any user input.

Usage:
    python predictor.py
    python predictor.py --text "open youtube and search kannada songs"
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_PATH = Path(__file__).parent / "exports" / "mj_intent_model"


class MJIntentPredictor:
    """Lightweight wrapper around the trained DistilBERT intent classifier."""

    def __init__(self, model_path: Path = MODEL_PATH):
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {model_path}\n"
                "Run: python train_intent.py first"
            )

        print(f"Loading model from {model_path}...")
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_path))
        self.model = AutoModelForSequenceClassification.from_pretrained(str(model_path))
        self.model.eval()

        # Load label mapping
        mapping_path = model_path / "label_mapping.json"
        with open(mapping_path) as f:
            mapping = json.load(f)
        self.id2label = {int(k): v for k, v in mapping["id2label"].items()}
        self.label2id = mapping["label2id"]

        device_name = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device_name)
        self.model.to(self.device)
        print(f"Model loaded on {device_name}. Ready.")

    def predict(self, text: str, top_k: int = 3) -> dict:
        """Predict intent with confidence scores."""
        start = time.monotonic()
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=128,
            padding=True,
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)[0]

        latency_ms = (time.monotonic() - start) * 1000

        top_indices = torch.argsort(probs, descending=True)[:top_k]
        top_results = [
            {
                "intent": self.id2label[idx.item()],
                "confidence": round(probs[idx].item(), 4),
            }
            for idx in top_indices
        ]

        return {
            "text": text,
            "intent": top_results[0]["intent"],
            "confidence": top_results[0]["confidence"],
            "top_k": top_results,
            "latency_ms": round(latency_ms, 2),
        }

    def predict_batch(self, texts: list[str]) -> list[dict]:
        """Predict intents for a batch of texts."""
        return [self.predict(t) for t in texts]


def interactive_mode(predictor: MJIntentPredictor):
    """Run interactive CLI loop."""
    print("\n" + "="*60)
    print(" MJ Intent Predictor — Interactive Mode")
    print(" Type a command. Press Ctrl+C to exit.")
    print("="*60)

    while True:
        try:
            text = input("\n> ").strip()
            if not text:
                continue

            result = predictor.predict(text)
            print(f"\n  Intent    : {result['intent']}")
            print(f"  Confidence: {result['confidence']:.1%}")
            print(f"  Latency   : {result['latency_ms']:.1f}ms")
            print(f"\n  Top 3:")
            for r in result["top_k"]:
                bar = "█" * int(r["confidence"] * 20)
                print(f"    {r['intent']:<25} {r['confidence']:.1%}  {bar}")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MJ Intent Predictor")
    parser.add_argument("--text", type=str, help="Single text to classify")
    parser.add_argument("--model", type=str, default=str(MODEL_PATH), help="Model path")
    args = parser.parse_args()

    predictor = MJIntentPredictor(model_path=Path(args.model))

    if args.text:
        result = predictor.predict(args.text)
        print(json.dumps(result, indent=2))
    else:
        interactive_mode(predictor)
