# Campaign service tests

import pytest
from uuid import uuid4
from datetime import datetime

from app.services.campaign_service import CampaignService
from app.schemas.campaign import CampaignCreate, CampaignUpdate
from app.models.enums import CampaignStatus


@pytest.mark.asyncio
async def test_create_campaign(db_session, sample_campaign_data):
    """Test campaign creation"""
    service = CampaignService(db_session)
    org_id = uuid4()
    owner_id = uuid4()

    campaign_data = CampaignCreate(**sample_campaign_data)
    campaign = await service.create(campaign_data, owner_id, org_id)

    assert campaign.id is not None
    assert campaign.name == sample_campaign_data["name"]
    assert campaign.organization_id == org_id
    assert campaign.owner_id == owner_id
    assert campaign.status == CampaignStatus.DRAFT


@pytest.mark.asyncio
async def test_get_campaign(db_session, sample_campaign_data):
    """Test getting campaign by ID"""
    service = CampaignService(db_session)
    org_id = uuid4()
    owner_id = uuid4()

    campaign_data = CampaignCreate(**sample_campaign_data)
    created = await service.create(campaign_data, owner_id, org_id)

    retrieved = await service.get_by_id(created.id, org_id)
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.name == created.name


@pytest.mark.asyncio
async def test_list_campaigns(db_session, sample_campaign_data):
    """Test listing campaigns with pagination"""
    service = CampaignService(db_session)
    org_id = uuid4()
    owner_id = uuid4()

    # Create multiple campaigns
    for i in range(5):
        data = CampaignCreate(**{**sample_campaign_data, "name": f"Campaign {i}"})
        await service.create(data, owner_id, org_id)

    campaigns, total = await service.list(organization_id=org_id, page=1, page_size=10)
    assert total == 5
    assert len(campaigns) == 5


@pytest.mark.asyncio
async def test_update_campaign(db_session, sample_campaign_data):
    """Test campaign update"""
    service = CampaignService(db_session)
    org_id = uuid4()
    owner_id = uuid4()

    campaign_data = CampaignCreate(**sample_campaign_data)
    created = await service.create(campaign_data, owner_id, org_id)

    update_data = CampaignUpdate(name="Updated Name", max_calls_per_day=200)
    updated = await service.update(created.id, org_id, update_data)

    assert updated is not None
    assert updated.name == "Updated Name"
    assert updated.max_calls_per_day == 200


@pytest.mark.asyncio
async def test_delete_campaign(db_session, sample_campaign_data):
    """Test campaign deletion"""
    service = CampaignService(db_session)
    org_id = uuid4()
    owner_id = uuid4()

    campaign_data = CampaignCreate(**sample_campaign_data)
    created = await service.create(campaign_data, owner_id, org_id)

    success = await service.delete(created.id, org_id)
    assert success is True

    # Verify deleted
    retrieved = await service.get_by_id(created.id, org_id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_campaign_lifecycle(db_session, sample_campaign_data):
    """Test campaign start, pause, stop lifecycle"""
    service = CampaignService(db_session)
    org_id = uuid4()
    owner_id = uuid4()

    campaign_data = CampaignCreate(**sample_campaign_data)
    created = await service.create(campaign_data, owner_id, org_id)

    # Start campaign
    started = await service.start(created.id, org_id)
    assert started.status == CampaignStatus.RUNNING
    assert started.started_at is not None

    # Pause campaign
    paused = await service.pause(started.id, org_id)
    assert paused.status == CampaignStatus.PAUSED
    assert paused.paused_at is not None

    # Stop campaign
    stopped = await service.stop(paused.id, org_id)
    assert stopped.status == CampaignStatus.STOPPED
    assert stopped.stopped_at is not None


@pytest.mark.asyncio
async def test_validate_campaign(db_session, sample_campaign_data):
    """Test campaign validation"""
    service = CampaignService(db_session)
    org_id = uuid4()
    owner_id = uuid4()

    # Valid campaign
    campaign_data = CampaignCreate(**sample_campaign_data)
    created = await service.create(campaign_data, owner_id, org_id)

    result = await service.validate(created.id, org_id)
    assert result["valid"] is True

    # Invalid campaign (missing AI instructions)
    invalid_data = CampaignCreate(**{**sample_campaign_data, "ai_instructions": "Short"})
    invalid = await service.create(invalid_data, owner_id, org_id)

    result = await service.validate(invalid.id, org_id)
    assert result["valid"] is False
    assert len(result["errors"]) > 0