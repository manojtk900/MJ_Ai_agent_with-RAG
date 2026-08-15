"""
Database Models — SQLAlchemy async base with pgvector support.
Engine is created lazily to allow the app to boot without a database connection.
"""
from datetime import datetime, timezone
from typing import AsyncGenerator, Optional

from sqlalchemy import Column, DateTime, func, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    """Base for all ORM models."""
    pass


class TimestampMixin:
    """Adds created_at and updated_at to any model."""
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# ── Lazy Engine — created once on first use ───────────────────
_engine = None
_AsyncSessionLocal = None


def get_engine():
    """Return (or create) the async SQLAlchemy engine."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_timeout=settings.db_pool_timeout,
            pool_pre_ping=True,
            echo=settings.debug,
        )
    return _engine


def get_session_factory():
    """Return (or create) the async session factory."""
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        _AsyncSessionLocal = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _AsyncSessionLocal


# Module-level dynamic attribute getter for engine and AsyncSessionLocal
def __getattr__(name: str):
    if name == "engine":
        return get_engine()
    if name == "AsyncSessionLocal":
        return get_session_factory()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")



async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency — yields an async DB session."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables() -> None:
    """Create all tables and enable pgvector extension."""
    eng = get_engine()

    # Try to enable pgvector; skip gracefully if not available
    async with eng.begin() as conn:
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        except Exception:
            pass  # pgvector extension not installed — vector columns won't work
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        except Exception:
            pass

        # Import all models so their metadata is registered
        try:
            import app.models.user          # noqa: F401
            import app.models.conversation  # noqa: F401
            import app.models.memory        # noqa: F401
            import app.models.task          # noqa: F401
        except ImportError:
            pass  # Model files may not exist yet

        await conn.run_sync(Base.metadata.create_all)
