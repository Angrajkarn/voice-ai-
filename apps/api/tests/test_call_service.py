# Call service tests

import pytest
from uuid import uuid4
from datetime import datetime

from app.services.call_service import CallService
from app.schemas.call import CallCreate
from app.models.enums import CallStatus, CallDirection, InterestLevel


@pytest.mark.asyncio
async def test_create_call(db_session):
    """Test call creation"""
    service = CallService(db_session)

    call_data = CallCreate(
        campaign_id=uuid4(),
        customer_id=uuid4(),
        direction=CallDirection.OUTBOUND,
        from_number="+15551234567",
        to_number="+15557654321",
    )
    call = await service.create(call_data)

    assert call.id is not None
    assert call.status == CallStatus.QUEUED
    assert call.direction == CallDirection.OUTBOUND
    assert call.from_number == "+15551234567"
    assert call.to_number == "+15557654321"


@pytest.mark.asyncio
async def test_get_call(db_session):
    """Test getting call by ID"""
    service = CallService(db_session)

    call_data = CallCreate(
        campaign_id=uuid4(),
        customer_id=uuid4(),
        direction=CallDirection.OUTBOUND,
        from_number="+15551234567",
        to_number="+15557654321",
    )
    created = await service.create(call_data)

    retrieved = await service.get_by_id(created.id)
    assert retrieved is not None
    assert retrieved.id == created.id


@pytest.mark.asyncio
async def test_list_calls(db_session):
    """Test listing calls with filters"""
    service = CallService(db_session)

    campaign_id = uuid4()
    customer_id = uuid4()

    # Create multiple calls
    for i in range(5):
        call_data = CallCreate(
            campaign_id=campaign_id,
            customer_id=customer_id,
            direction=CallDirection.OUTBOUND,
            from_number="+15551234567",
            to_number=f"+1555765432{i}",
        )
        await service.create(call_data)

    # List with pagination
    calls, total = await service.list(page=1, page_size=3, campaign_id=campaign_id)
    assert total == 5
    assert len(calls) == 3

    # List with status filter
    calls, total = await service.list(status=CallStatus.QUEUED)
    assert total == 5


@pytest.mark.asyncio
async def test_update_call(db_session):
    """Test call update"""
    service = CallService(db_session)

    call_data = CallCreate(
        campaign_id=uuid4(),
        customer_id=uuid4(),
        direction=CallDirection.OUTBOUND,
        from_number="+15551234567",
        to_number="+15557654321",
    )
    created = await service.create(call_data)

    from app.schemas.call import CallUpdate
    update_data = CallUpdate(
        status=CallStatus.COMPLETED,
        duration=120,
        interest_level=InterestLevel.HOT,
        summary="Customer was very interested",
    )
    updated = await service.update(created.id, update_data)

    assert updated is not None
    assert updated.status == CallStatus.COMPLETED
    assert updated.duration == 120
    assert updated.interest_level == InterestLevel.HOT


@pytest.mark.asyncio
async def test_get_next_queued_call(db_session):
    """Test getting next queued call"""
    service = CallService(db_session)

    campaign_id = uuid4()
    customer_id = uuid4()

    # Create queued calls
    for i in range(3):
        call_data = CallCreate(
            campaign_id=campaign_id,
            customer_id=uuid4(),
            direction=CallDirection.OUTBOUND,
            from_number="+15551234567",
            to_number=f"+1555765432{i}",
        )
        await service.create(call_data)

    # Get next queued
    next_call = await service.get_next_queued_call(campaign_id)
    assert next_call is not None
    assert next_call.status == CallStatus.QUEUED
    assert next_call.campaign_id == campaign_id