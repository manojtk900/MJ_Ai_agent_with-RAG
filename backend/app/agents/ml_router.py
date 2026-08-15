"""
ML Router — Local Intent Classification & Named Entity Recognition for MJ AI Assistant.
Leverages fine-tuned DistilBERT models for ultra-fast, offline command routing (~25-50ms).
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import structlog
import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    AutoTokenizer,
    pipeline,
)

log = structlog.get_logger(__name__)

# Base directory for ML model artifacts
BASE_DIR = Path(__file__).resolve().parent.parent
INTENT_MODEL_PATH = BASE_DIR / "ml_models" / "mj_intent_model"
ENTITY_MODEL_PATH = BASE_DIR / "ml_models" / "mj_entity_model"

# Fallback paths if training exports are used directly
TRAINING_INTENT_PATH = BASE_DIR.parent / "training" / "exports" / "mj_intent_model"
TRAINING_ENTITY_PATH = BASE_DIR.parent / "training" / "exports" / "mj_entity_model"


class MLRouter:
    """
    Singleton inference engine for Intent Detection and Entity Extraction.
    Loaded once at startup to keep models resident in RAM for zero per-request latency.
    """

    _instance: Optional["MLRouter"] = None

    def __init__(self) -> None:
        self.intent_tokenizer: Optional[Any] = None
        self.intent_model: Optional[Any] = None
        self.entity_tokenizer: Optional[Any] = None
        self.entity_model: Optional[Any] = None
        self.ner_pipeline: Optional[Any] = None
        self._is_loaded: bool = False
        self.device: str = "cuda" if torch.cuda.is_available() else "cpu"

    @classmethod
    def get_instance(cls) -> "MLRouter":
        if cls._instance is None:
            cls._instance = MLRouter()
        return cls._instance

    def _resolve_model_path(self, primary: Path, fallback: Path) -> str:
        if primary.exists() and (primary / "config.json").exists():
            return str(primary)
        if fallback.exists() and (fallback / "config.json").exists():
            return str(fallback)
        return str(primary)

    def load_models(self) -> None:
        """Load Intent & Entity models once into memory."""
        if self._is_loaded:
            return

        start_time = time.monotonic()
        intent_path = self._resolve_model_path(INTENT_MODEL_PATH, TRAINING_INTENT_PATH)
        entity_path = self._resolve_model_path(ENTITY_MODEL_PATH, TRAINING_ENTITY_PATH)

        log.info("Loading ML models for local routing...", intent_path=intent_path, entity_path=entity_path, device=self.device)

        try:
            # 1. Load Intent Classifier
            self.intent_tokenizer = AutoTokenizer.from_pretrained(intent_path)
            self.intent_model = AutoModelForSequenceClassification.from_pretrained(intent_path)
            self.intent_model.to(self.device)
            self.intent_model.eval()

            # 2. Load Entity Extractor
            self.entity_tokenizer = AutoTokenizer.from_pretrained(entity_path)
            self.entity_model = AutoModelForTokenClassification.from_pretrained(entity_path)
            self.entity_model.to(self.device)
            self.entity_model.eval()

            # 3. Build HuggingFace Token Classification Pipeline
            device_id = 0 if self.device == "cuda" else -1
            self.ner_pipeline = pipeline(
                "token-classification",
                model=self.entity_model,
                tokenizer=self.entity_tokenizer,
                aggregation_strategy="simple",
                device=device_id,
            )

            self._is_loaded = True
            load_duration = (time.monotonic() - start_time) * 1000
            log.info("ML Models successfully loaded into RAM", duration_ms=round(load_duration, 2))

        except Exception as e:
            log.error("Failed to load ML models", error=str(e))
            self._is_loaded = False
            raise

    def predict_intent(self, text: str) -> Dict[str, Any]:
        """
        Predict command intent with confidence probability score.
        Returns:
            {"intent": "youtube_search", "confidence": 0.998, "id": 21}
        """
        if not self._is_loaded:
            self.load_models()

        clean_text = text.strip()
        if not clean_text:
            return {"intent": "chat", "confidence": 1.0, "id": 0}

        inputs = self.intent_tokenizer(
            clean_text,
            return_tensors="pt",
            truncation=True,
            max_length=128,
            padding=False,
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.intent_model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
            confidence, predicted_idx = torch.max(probabilities, dim=-1)

        idx = predicted_idx.item()
        score = float(confidence.item())
        label = self.intent_model.config.id2label.get(idx, str(idx))

        return {
            "intent": label,
            "confidence": round(score, 4),
            "id": idx,
        }

    def extract_entities(self, text: str) -> Dict[str, str]:
        """
        Extract named entities (query, app_name, email, task, repo, file, url)
        using exact character spans from the original input text.
        """
        if not self._is_loaded:
            self.load_models()

        clean_text = text.strip()
        if not clean_text or self.ner_pipeline is None:
            return {}

        raw_entities = self.ner_pipeline(clean_text)
        entities: Dict[str, str] = {}

        for item in raw_entities:
            group = item.get("entity_group")
            start = item.get("start")
            end = item.get("end")

            if start is not None and end is not None and 0 <= start <= end <= len(clean_text):
                exact_val = clean_text[start:end].strip()
            else:
                exact_val = item.get("word", "").replace(" ##", "").replace("##", "").strip()

            if group and exact_val:
                if group in entities:
                    entities[group] = f"{entities[group]} {exact_val}".strip()
                else:
                    entities[group] = exact_val

        return entities

    def route_command(self, text: str, confidence_threshold: float = 0.80) -> Dict[str, Any]:
        """
        Main routing function returning intent, confidence score, and extracted entities.
        Includes confidence threshold validation with intelligent fallback.
        """
        intent_info = self.predict_intent(text)
        entities = self.extract_entities(text)

        intent = intent_info["intent"]
        confidence = intent_info["confidence"]

        # Confidence check — fallback to chat if model is uncertain
        if confidence < confidence_threshold and intent not in ("chat", "conversation"):
            log.warning("Low confidence intent detection, falling back to chat", raw_intent=intent, confidence=confidence, text=text)
            intent = "chat"

        return {
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
        }

    def benchmark_latency(self, sample_text: str = "open youtube and search trending yash songs", iterations: int = 5) -> Dict[str, float]:
        """
        Measure inference latency in milliseconds for Intent, Entity, and Total routing.
        """
        if not self._is_loaded:
            self.load_models()

        # Warmup
        _ = self.predict_intent(sample_text)
        _ = self.extract_entities(sample_text)

        intent_times: List[float] = []
        entity_times: List[float] = []

        for _ in range(iterations):
            # Intent timing
            t0 = time.perf_counter()
            _ = self.predict_intent(sample_text)
            t1 = time.perf_counter()
            intent_times.append((t1 - t0) * 1000)

            # Entity timing
            t2 = time.perf_counter()
            _ = self.extract_entities(sample_text)
            t3 = time.perf_counter()
            entity_times.append((t3 - t2) * 1000)

        avg_intent = sum(intent_times) / len(intent_times)
        avg_entity = sum(entity_times) / len(entity_times)
        total_lat = avg_intent + avg_entity

        return {
            "intent_latency_ms": round(avg_intent, 2),
            "entity_latency_ms": round(avg_entity, 2),
            "total_latency_ms": round(total_lat, 2),
        }


# ── Module-Level Helper Functions ──────────────────────────────
_router = MLRouter.get_instance()


def load_models() -> None:
    """Pre-load ML models at application startup."""
    _router.load_models()


def predict_intent(text: str) -> str:
    """Predict top intent label for given text."""
    res = _router.predict_intent(text)
    return res["intent"]


def extract_entities(text: str) -> Dict[str, str]:
    """Extract named entities from text."""
    return _router.extract_entities(text)


def route_command(text: str, confidence_threshold: float = 0.80) -> Dict[str, Any]:
    """
    Route command to intent + entities.
    Returns:
    {
        "intent": "youtube_search",
        "confidence": 0.998,
        "entities": {
            "query": "yash toxic trailer"
        }
    }
    """
    return _router.route_command(text, confidence_threshold=confidence_threshold)


def benchmark_latency(sample_text: str = "open youtube and search trending yash songs", iterations: int = 5) -> Dict[str, float]:
    """Measure inference latency in ms."""
    return _router.benchmark_latency(sample_text=sample_text, iterations=iterations)
