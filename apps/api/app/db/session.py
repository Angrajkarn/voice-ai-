# Database session management


from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

# Global variables for engine and session factory
engine = None
AsyncSessionLocal = None

def get_engine():
    """Get or create async engine lazily"""
    global engine
    if engine is None:
        engine = create_async_engine(
            settings.DATABASE_URL,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=True,
            echo=settings.DEBUG,
        )
    return engine

def get_session_factory():
    """Get or create async session factory lazily"""
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        AsyncSessionLocal = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return AsyncSessionLocal

# Base class for models (doesn't require engine)
Base = declarative_base()


async def get_db() -> "AsyncSession":
    """Dependency for getting database session"""
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database - create tables"""
    # Import all models to register them
    from app.models import (  # noqa: F401
        audit_log,
        automation_log,
        call,
        call_recording,
        call_transcript,
        callback,
        campaign,
        campaign_customer,
        consent_record,
        customer,
        integration,
        notification,
        organization,
        suppression_list,
        sync_log,
        user,
    )

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections"""
    global engine
    if engine is not None:
        await engine.dispose()
        engine = None