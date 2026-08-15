"""
Voice Agent — Whisper STT + OpenAI TTS.
"""
from __future__ import annotations
from typing import Any, Dict
import structlog
from app.agents.base import BaseAgent
from app.config import settings
from app.core.langgraph.state import AgentState

log = structlog.get_logger(__name__)


class VoiceAgent(BaseAgent):
    name = "voice_agent"
    description = "Speech-to-text (Whisper) and text-to-speech (OpenAI TTS)"
    supported_intents = ["voice_processing"]

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        action = state.metadata.get("voice_action", "tts")
        if action == "stt":
            return await self._transcribe(state)
        return await self._synthesize(state)

    async def _transcribe(self, state: AgentState) -> Dict[str, Any]:
        audio_path = state.metadata.get("audio_path", "")
        if not audio_path:
            return {"error": "No audio file", "final_response": "Please provide an audio file path."}
        if not settings.openai_api_key:
            return {"error": "OpenAI key missing", "final_response": "OpenAI API key required for STT."}
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            with open(audio_path, "rb") as f:
                transcript = await client.audio.transcriptions.create(model=settings.whisper_model, file=f)
            return {
                "final_response": transcript.text,
                "raw_input": transcript.text,
                "agent_logs": [f"[voice_agent] transcribed {len(transcript.text)} chars"],
            }
        except Exception as e:
            return {"error": str(e), "final_response": f"Transcription failed: {e}"}

    async def _synthesize(self, state: AgentState) -> Dict[str, Any]:
        text = state.final_response or state.raw_input
        if not settings.openai_api_key:
            return {"error": "OpenAI key missing", "final_response": "OpenAI API key required for TTS."}
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            response = await client.audio.speech.create(model="tts-1", voice=settings.tts_voice, input=text[:4096])
            return {
                "final_response": "🔊 Audio synthesized",
                "artifacts": [{"type": "audio_mp3", "data": response.content}],
                "agent_logs": [f"[voice_agent] synthesized {len(text)} chars"],
            }
        except Exception as e:
            return {"error": str(e), "final_response": f"TTS failed: {e}"}
