"""
MJ AI Assistant — Application Configuration
Uses pydantic-settings for type-safe env var management.
"""
from functools import lru_cache
from typing import List, Literal, Optional
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ───────────────────────────────────────────
    app_name: str = "MJ AI Assistant"
    app_env: Literal["development", "staging", "production"] = "development"
    app_version: str = "1.0.0"
    debug: bool = True
    secret_key: str = "change-me-in-production-min-32-chars!!"
    api_v1_prefix: str = "/api/v1"

    # ── Server ────────────────────────────────────────────────
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # ── Database ──────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://mj_user:mj_secure_password@localhost:5433/mj_ai_assistant"
    db_pool_size: int = 20
    db_max_overflow: int = 40
    db_pool_timeout: int = 30

    # ── Redis ─────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"
    redis_ttl_short: int = 3600          # 1 hour
    redis_ttl_session: int = 86400       # 24 hours

    # ── LLM Providers ─────────────────────────────────────────
    default_llm_provider: Literal["openai", "gemini", "claude", "ollama"] = "ollama"
    openai_api_key: Optional[str] = None
    openai_org_id: Optional[str] = None
    openai_default_model: str = "gpt-4o"
    google_api_key: Optional[str] = None
    gemini_default_model: str = "gemini-2.0-flash"
    anthropic_api_key: Optional[str] = None
    claude_default_model: str = "claude-sonnet-4-5"
    ollama_base_url: str = "http://localhost:11434"
    ollama_default_model: str = "gemma:2b"

    # ── Embeddings ────────────────────────────────────────────
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    # ── MCP ───────────────────────────────────────────────────
    mcp_gateway_port: int = 9000
    mcp_github_token: Optional[str] = None
    mcp_filesystem_root: str = "/workspace"

    # ── Tool APIs ─────────────────────────────────────────────
    tavily_api_key: Optional[str] = None
    serper_api_key: Optional[str] = None
    brave_search_api_key: Optional[str] = None

    # ── Voice ─────────────────────────────────────────────────
    whisper_model: str = "whisper-1"
    tts_voice: str = "alloy"

    # ── Email ─────────────────────────────────────────────────
    email_host: str = "smtp.gmail.com"
    email_port: int = 587
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    imap_host: str = "imap.gmail.com"
    imap_port: int = 993

    # ── GitHub ────────────────────────────────────────────────
    github_token: Optional[str] = None
    github_username: Optional[str] = None

    # ── Observability ─────────────────────────────────────────
    langchain_tracing_v2: bool = False
    langchain_api_key: Optional[str] = None
    langchain_project: str = "mj-ai-assistant"
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    otel_service_name: str = "mj-ai-assistant"

    # ── Security / Auth ───────────────────────────────────────
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 30
    bcrypt_rounds: int = 12

    # ── Agent Behaviour ───────────────────────────────────────
    default_autonomy_level: int = 1      # 0–3
    max_agent_retries: int = 3
    agent_timeout_seconds: int = 300     # 5 minutes (300 seconds)

    # ── Background Workers ────────────────────────────────────
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # ── File Storage ──────────────────────────────────────────
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 50

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def active_llm_model(self) -> str:
        mapping = {
            "openai": self.openai_default_model,
            "gemini": self.gemini_default_model,
            "claude": self.claude_default_model,
            "ollama": self.ollama_default_model,
        }
        return mapping[self.default_llm_provider]


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — import this everywhere."""
    return Settings()


settings = get_settings()
