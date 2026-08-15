"""
LLM Service — Multi-provider LLM factory supporting OpenAI, Gemini, Claude, Ollama.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal, Optional

import structlog
from langchain_core.language_models import BaseChatModel

from app.config import settings

log = structlog.get_logger(__name__)

LLMProvider = Literal["openai", "gemini", "claude", "ollama"]


def get_llm(
    provider: Optional[LLMProvider] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    streaming: bool = False,
) -> BaseChatModel:
    """
    Factory function — returns the appropriate LangChain LLM.
    Priority: Ollama (local) → Gemini → Claude → OpenAI
    """
    provider = provider or settings.default_llm_provider
    selected_model = model or (settings.ollama_default_model if provider == "ollama" else settings.openai_default_model)

    print(f"\n=======================================================")
    print(f"[CHAT REQUEST RECEIVED] Provider: {provider} | Model: {selected_model}")
    print(f"=======================================================\n")
    log.info("CHAT REQUEST RECEIVED", provider=provider, model=selected_model)

    if provider == "ollama":
        print(f"[CALLING OLLAMA] Base URL: {settings.ollama_base_url} | Model: {selected_model}")
        log.info("CALLING OLLAMA", base_url=settings.ollama_base_url, model=selected_model)
        llm = _get_ollama(model, temperature, streaming)
        print(f"[OLLAMA RESPONSE RECEIVED] LLM initialized successfully with 300s timeout\n")
        log.info("OLLAMA RESPONSE RECEIVED")
        return llm
    elif provider == "gemini":
        return _get_gemini(model, temperature, streaming)
    elif provider == "claude":
        return _get_claude(model, temperature, streaming)
    elif provider == "openai":
        return _get_openai(model, temperature, streaming)
    else:
        print(f"[CALLING OLLAMA (DEFAULT)] Base URL: {settings.ollama_base_url}")
        log.info("Defaulting provider to Ollama", base_url=settings.ollama_base_url)
        return _get_ollama(model, temperature, streaming)


def _get_openai(model: Optional[str], temperature: float, streaming: bool) -> BaseChatModel:
    from langchain_openai import ChatOpenAI
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY not set")
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=model or settings.openai_default_model,
        temperature=temperature,
        streaming=streaming,
        organization=settings.openai_org_id or None,
        request_timeout=300.0,  # 5 minutes (300 seconds)
    )


def _get_gemini(model: Optional[str], temperature: float, streaming: bool) -> BaseChatModel:
    from langchain_google_genai import ChatGoogleGenerativeAI
    if not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY not set")
    return ChatGoogleGenerativeAI(
        google_api_key=settings.google_api_key,
        model=model or settings.gemini_default_model,
        temperature=temperature,
        streaming=streaming,
        request_timeout=300.0,  # 5 minutes (300 seconds)
    )


def _get_claude(model: Optional[str], temperature: float, streaming: bool) -> BaseChatModel:
    from langchain_anthropic import ChatAnthropic
    if not settings.anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")
    return ChatAnthropic(
        api_key=settings.anthropic_api_key,
        model=model or settings.claude_default_model,
        temperature=temperature,
        streaming=streaming,
        default_request_timeout=300.0,  # 5 minutes (300 seconds)
    )


def _get_ollama(model: Optional[str], temperature: float, streaming: bool) -> BaseChatModel:
    from langchain_community.chat_models import ChatOllama
    log.info("Configuring ChatOllama with 300s timeout", base_url=settings.ollama_base_url, model=model or settings.ollama_default_model)
    return ChatOllama(
        base_url=settings.ollama_base_url,
        model=model or settings.ollama_default_model,
        temperature=temperature,
        request_timeout=300.0,  # 5 minutes (300 seconds)
    )


class EmbeddingService:
    """Embedding service for pgvector storage."""

    async def embed(self, text: str) -> list[float]:
        """Generate embedding vector for text."""
        from openai import AsyncOpenAI
        if not settings.openai_api_key:
            # Fallback: zero vector
            return [0.0] * settings.embedding_dimensions

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.embeddings.create(
            input=text[:8192],  # Token limit
            model=settings.embedding_model,
        )
        return response.data[0].embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Batch embed multiple texts."""
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.embeddings.create(
            input=[t[:8192] for t in texts],
            model=settings.embedding_model,
        )
        return [d.embedding for d in response.data]
