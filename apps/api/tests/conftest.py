# Pytest configuration and fixtures

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from typing: AsyncGenerator
import asyncio

from app.core.config import settings
from app.db.session import Base
from app.main import app
from httpx import AsyncClient, ASGITransport


# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/voiceai_test"


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests"""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for API tests"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_campaign_data():
    """Sample campaign data for tests"""
    return {
        "name": "Test Campaign",
        "description": "Test campaign for unit tests",
        "purpose": "Test AI voice calling",
        "ai_instructions": "You are a test AI assistant. Be helpful and polite.",
        "opening_script": "Hello {firstName}, this is a test call from Test Company.",
        "knowledge_base": "Test product information.",
        "voice_id": "alloy",
        "language": "en-IN",
        "supported_languages": ["en-IN", "hi-IN"],
        "max_calls_per_day": 100,
        "max_retry_attempts": 3,
        "delay_between_calls": 30,
        "calling_window_start": "09:00",
        "calling_window_end": "18:00",
        "calling_timezone": "Asia/Kolkata",
        "skip_weekends": True,
    }


@pytest.fixture
def sample_customer_data():
    """Sample customer data for tests"""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+15551234567",
        "company": "Test Corp",
        "location": "New York",
        "language": "en-IN",
        "timezone": "America/New_York",
        "tags": ["test", "lead"],
        "max_call_attempts": 3,
    }