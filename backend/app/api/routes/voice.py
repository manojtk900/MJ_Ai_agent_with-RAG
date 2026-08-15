"""
Voice API Route — STT (Whisper) and TTS endpoints.
"""
import io
from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter(prefix="/voice")


class TTSRequest(BaseModel):
    text: str
    voice: str = "alloy"  # alloy | echo | fable | onyx | nova | shimmer


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(..., description="Audio file (mp3, wav, webm, m4a)"),
    language: Optional[str] = Form(default=None),
):
    """
    Speech-to-Text using OpenAI Whisper.
    Upload an audio file and receive the transcription.
    """
    from app.config import settings
    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="OpenAI API key not configured. Set OPENAI_API_KEY in .env")

    allowed = {".mp3", ".wav", ".webm", ".m4a", ".ogg", ".flac"}
    import os
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}. Allowed: {allowed}")

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        audio_bytes = await file.read()
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = file.filename or f"audio{ext}"

        transcript = await client.audio.transcriptions.create(
            model=settings.whisper_model,
            file=audio_file,
            language=language,
        )
        return {
            "text": transcript.text,
            "language": language or "auto-detected",
            "filename": file.filename,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@router.post("/synthesize")
async def synthesize_speech(request: TTSRequest):
    """
    Text-to-Speech using OpenAI TTS.
    Returns audio as MP3 stream.
    """
    from app.config import settings
    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="OpenAI API key not configured")

    if len(request.text) > 4096:
        raise HTTPException(status_code=400, detail="Text exceeds 4096 character limit")

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.audio.speech.create(
            model="tts-1",
            voice=request.voice,
            input=request.text,
        )
        audio_bytes = response.content
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")
