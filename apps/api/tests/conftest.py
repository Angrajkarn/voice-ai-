# Pytest configuration and fixtures

import os
import sys
from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import Base
from app.main import app
from app.models.campaign import Campaign
from app.models.customer import Customer
from app.models.enums import (
    CampaignStatus,
    CustomerStatus,
    InterestLevel,
    OrganizationPlan,
    UserRole,
)
from app.models.organization import Organization
from app.models.user import User
from httpx import ASGITransport, AsyncClient

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/voiceai_test"


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


@pytest_asyncio.fixture
async def test_organization(db_session) -> Organization:
    """Create a test organization"""
    org = Organization(
        name="Test Organization",
        slug=f"test-org-{uuid4().hex[:8]}",
        plan=OrganizationPlan.FREE,
        is_active=True,
        settings={},
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    return org


@pytest_asyncio.fixture
async def test_user(db_session, test_organization) -> User:
    """Create a test user"""
    user = User(
        email="test@example.com",
        name="Test User",
        password_hash="hashed_password",
        role=UserRole.ADMIN,
        organization_id=test_organization.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_campaign(db_session, test_organization, test_user) -> Campaign:
    """Create a test campaign"""
    campaign = Campaign(
        name="Test Campaign",
        description="Test campaign for unit tests",
        purpose="Test AI voice calling",
        ai_instructions="You are a test AI assistant. Be helpful and polite.",
        opening_script="Hello {firstName}, this is a test call from Test Corp in New York.",
        knowledge_base="Test product information.",
        voice_id="alloy",
        language="en-IN",
        supported_languages=["en-IN", "hi-IN"],
        max_calls_per_day=100,
        max_retry_attempts=3,
        delay_between_calls=30,
        calling_window_start="09:00",
        calling_window_end="18:00",
        calling_timezone="Asia/Kolkata",
        skip_weekends=True,
        organization_id=test_organization.id,
        owner_id=test_user.id,
        status=CampaignStatus.DRAFT,
    )
    db_session.add(campaign)
    await db_session.commit()
    await db_session.refresh(campaign)
    return campaign


@pytest_asyncio.fixture
async def test_customer(db_session, test_organization) -> Customer:
    """Create a test customer"""
    customer = Customer(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="+15551234567",
        company="Test Corp",
        location="New York",
        language="en-IN",
        timezone="America/New_York",
        tags=["test", "lead"],
        max_call_attempts=3,
        organization_id=test_organization.id,
        status=CustomerStatus.NEW,
        interest_level=InterestLevel.UNKNOWN,
    )
    db_session.add(customer)
    await db_session.commit()
    await db_session.refresh(customer)
    return customer


@pytest.fixture
def sample_campaign_data():
    """Sample campaign data for tests"""
    return {
        "name": "Test Campaign",
        "description": "Test campaign for unit tests",
        "purpose": "Test AI voice calling",
        "ai_instructions": "You are a test AI assistant. Be helpful and polite.",
        "opening_script": "Hello {firstName}, this is a test call from Test Corp in New York.",
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