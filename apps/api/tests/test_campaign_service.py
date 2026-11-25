# Campaign service tests


import pytest
from app.core.config import settings
from app.models.integration import Integration
from app.models.consent_record import ConsentRecord
from app.models.campaign_customer import CampaignCustomer
from app.models.enums import CampaignStatus, ConsentMethod, ConsentStatus, IntegrationType
from app.schemas.campaign import CampaignCreate, CampaignUpdate
from app.services.campaign_service import CampaignService


@pytest.mark.asyncio
async def test_create_campaign(db_session, test_organization, test_user, sample_campaign_data):
    """Test campaign creation"""
    service = CampaignService(db_session)

    campaign_data = CampaignCreate(**sample_campaign_data)
    campaign = await service.create(campaign_data, test_user.id, test_organization.id)

    assert campaign.id is not None
    assert campaign.name == sample_campaign_data["name"]
    assert campaign.organization_id == test_organization.id
    assert campaign.owner_id == test_user.id
    assert campaign.status == CampaignStatus.DRAFT


@pytest.mark.asyncio
async def test_get_campaign(db_session, test_organization, test_user, test_campaign):
    """Test getting campaign by ID"""
    service = CampaignService(db_session)

    retrieved = await service.get_by_id(test_campaign.id, test_organization.id)
    assert retrieved is not None
    assert retrieved.id == test_campaign.id
    assert retrieved.name == test_campaign.name


@pytest.mark.asyncio
async def test_list_campaigns(db_session, test_organization, test_user, sample_campaign_data):
    """Test listing campaigns with pagination"""
    service = CampaignService(db_session)

    # Create multiple campaigns
    for i in range(5):
        data = CampaignCreate(**{**sample_campaign_data, "name": f"Campaign {i}"})
        await service.create(data, test_user.id, test_organization.id)

    campaigns, total = await service.list(organization_id=test_organization.id, page=1, page_size=10)
    assert total == 5
    assert len(campaigns) == 5


@pytest.mark.asyncio
async def test_update_campaign(db_session, test_organization, test_user, test_campaign):
    """Test campaign update"""
    service = CampaignService(db_session)

    update_data = CampaignUpdate(name="Updated Name", max_calls_per_day=200)
    updated = await service.update(test_campaign.id, test_organization.id, update_data)

    assert updated is not None
    assert updated.name == "Updated Name"
    assert updated.max_calls_per_day == 200


@pytest.mark.asyncio
async def test_delete_campaign(db_session, test_organization, test_user, test_campaign):
    """Test campaign deletion"""
    service = CampaignService(db_session)

    success = await service.delete(test_campaign.id, test_organization.id)
    assert success is True

    # Verify deleted
    retrieved = await service.get_by_id(test_campaign.id, test_organization.id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_campaign_lifecycle(db_session, test_organization, test_user, test_campaign, test_customer, monkeypatch):
    """Test campaign start, pause, stop lifecycle"""
    service = CampaignService(db_session)
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setattr(settings, "TWILIO_WEBHOOK_BASE_URL", "https://voice.example.test")
    db_session.add(Integration(
        type=IntegrationType.TWILIO,
        name="Test Twilio",
        config={"phone_number": "+15551234567"},
        organization_id=test_organization.id,
        is_active=True,
    ))
    db_session.add(CampaignCustomer(campaign_id=test_campaign.id, customer_id=test_customer.id))
    db_session.add(ConsentRecord(
        phone=test_customer.phone,
        status=ConsentStatus.GRANTED,
        method=ConsentMethod.WEB_FORM,
        organization_id=test_organization.id,
        customer_id=test_customer.id,
        granted_at=__import__("datetime").datetime.utcnow(),
    ))
    await db_session.commit()

    # Start campaign
    started = await service.start(test_campaign.id, test_organization.id)
    assert started.status == CampaignStatus.RUNNING
    assert started.started_at is not None

    # Pause campaign
    paused = await service.pause(started.id, test_organization.id)
    assert paused.status == CampaignStatus.PAUSED
    assert paused.paused_at is not None

    # Stop campaign
    stopped = await service.stop(paused.id, test_organization.id)
    assert stopped.status == CampaignStatus.STOPPED
    assert stopped.stopped_at is not None


@pytest.mark.asyncio
async def test_validate_campaign(db_session, test_organization, test_user, test_campaign):
    """Test campaign validation"""
    service = CampaignService(db_session)

    # Valid campaign
    result = await service.validate(test_campaign.id, test_organization.id)
    assert result["valid"] is True

    # Invalid campaign (missing AI instructions)
    test_campaign.ai_instructions = "Short"
    await db_session.commit()

    result = await service.validate(test_campaign.id, test_organization.id)
    assert result["valid"] is False
    assert len(result["errors"]) > 0