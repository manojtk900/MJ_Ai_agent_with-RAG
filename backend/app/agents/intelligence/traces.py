"""
Execution Trace Recorder for MJ AI Assistant.
Logs anonymized execution traces to data/traces/mj_traces.jsonl for continuous learning & LoRA dataset building.
"""
from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import structlog

from app.agents.intelligence.schemas import ExecutionTrace

log = structlog.get_logger(__name__)

# Base project directory
DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "data" / "traces"
TRACE_FILE = DATA_DIR / "mj_traces.jsonl"

# Sensitive pattern sanitizer
SECRET_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9]{20,}", re.IGNORECASE),
    re.compile(r"AIza[0-9A-Za-z-_]{35}", re.IGNORECASE),
    re.compile(r"ghp_[a-zA-Z0-9]{36}", re.IGNORECASE),
    re.compile(r"(?:password|passwd|pwd|secret|api_key|token)[\s:=]+([^\s,]+)", re.IGNORECASE),
]


class TraceRecorder:
    """
    Singleton trace recording service.
    """
    _instance: Optional[TraceRecorder] = None
    _counter: int = 1

    def __init__(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if TRACE_FILE.exists():
            try:
                with open(TRACE_FILE, "r", encoding="utf-8") as f:
                    self._counter = sum(1 for _ in f) + 1
            except Exception:
                self._counter = 1

    @classmethod
    def get_instance(cls) -> TraceRecorder:
        if cls._instance is None:
            cls._instance = TraceRecorder()
        return cls._instance

    def _sanitize(self, val: Any) -> Any:
        if isinstance(val, str):
            sanitized = val
            for pat in SECRET_PATTERNS:
                sanitized = pat.sub("[REDACTED_SECRET]", sanitized)
            return sanitized
        elif isinstance(val, dict):
            return {k: self._sanitize(v) for k, v in val.items() if not any(s in k.lower() for s in ("password", "secret", "token", "key"))}
        elif isinstance(val, list):
            return [self._sanitize(item) for item in val]
        return val

    def record(
        self,
        raw_input: str,
        predicted_intent: str,
        confidence: float,
        route: str,
        selected_tool: Optional[str] = None,
        tool_called: Optional[str] = None,
        tool_arguments: Optional[Dict[str, Any]] = None,
        tool_result: Optional[Any] = None,
        success: bool = True,
        error: Optional[str] = None,
        latency_ms: float = 0.0,
        model_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        user_feedback: Optional[str] = None,
    ) -> str:
        """
        Record a single execution trace and return its unique trace_id.
        """
        trace_id = f"mj-2026-{self._counter:06d}"
        self._counter += 1
        effective_tool = selected_tool or tool_called

        trace = ExecutionTrace(
            trace_id=trace_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            raw_input=self._sanitize(raw_input),
            predicted_intent=predicted_intent,
            confidence=round(confidence, 4),
            route=route,
            selected_tool=effective_tool,
            tool_arguments=self._sanitize(tool_arguments),
            tool_result=self._sanitize(str(tool_result)[:500] if tool_result else None),
            success=success,
            error=self._sanitize(error),
            latency_ms=round(latency_ms, 2),
            model_provider=model_provider,
            llm_model=llm_model,
            user_feedback=user_feedback,
        )

        try:
            with open(TRACE_FILE, "a", encoding="utf-8") as f:
                f.write(trace.model_dump_json() + "\n")
            log.info("Execution trace recorded", trace_id=trace_id, route=route)
        except Exception as e:
            log.warning("Failed to write trace to file", error=str(e), trace_id=trace_id)

        return trace_id

    def get_total_traces(self) -> int:
        """Return total number of recorded traces."""
        return max(0, self._counter - 1)

    def get_recent_traces(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch the most recent traces."""
        if not TRACE_FILE.exists():
            return []
        traces = []
        try:
            with open(TRACE_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        traces.append(json.loads(line))
            return traces[-limit:]
        except Exception as e:
            log.error("Failed to read traces", error=str(e))
            return []


# Global helper functions
trace_recorder = TraceRecorder.get_instance()


def record_trace(**kwargs) -> str:
    return trace_recorder.record(**kwargs)
