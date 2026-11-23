# AI Agent service tests

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.ai_agent_service import AIAgentService
from app.models.campaign import Campaign
from app.models.customer import Customer
from app.models.enums import InterestLevel


@pytest.fixture
def sample_campaign():
    """Sample campaign for testing"""
    return Campaign(
        id=uuid4(),
        name="Test Campaign",
        purpose="Test product launch",
        ai_instructions="You are a helpful AI assistant.",
        opening_script="Hello {firstName}, this is a test call.",
        knowledge_base="Test product info.",
        voice_id="alloy",
        language="en-IN",
        supported_languages=["en-IN", "hi-IN"],
    )


@pytest.fixture
def sample_customer():
    """Sample customer for testing"""
    return Customer(
        id=uuid4(),
        first_name="John",
        last_name="Doe",
        company="Test Corp",
        location="New York",
        language="en-IN",
    )


class TestAIAgentService:
    @pytest.mark.asyncio
    async def test_generate_opening_script(self, sample_campaign, sample_customer):
        """Test opening script generation with personalization"""
        service = AIAgentService()
        script = await service.generate_opening_script(sample_campaign, sample_customer)

        assert "John" in script
        assert "Test Corp" in script
        assert "New York" in script

    @pytest.mark.asyncio
    async def test_get_realtime_session_config(self, sample_campaign, sample_customer):
        """Test Realtime API session configuration"""
        service = AIAgentService()
        config = await service.get_realtime_session_config(sample_campaign, sample_customer)

        assert config["model"] == "gpt-4o-realtime-preview"
        assert config["voice"] == "alloy"
        assert "instructions" in config
        assert "tools" in config
        assert len(config["tools"]) > 0

        # Check tool definitions
        tool_names = [tool["name"] for tool in config["tools"]]
        assert "schedule_callback" in tool_names
        assert "transfer_to_human" in tool_names
        assert "end_call" in tool_names
        assert "log_objection" in tool_names

    @pytest.mark.asyncio
    async def test_analyze_call_with_transcript(self, sample_campaign, sample_customer):
        """Test call analysis with transcript"""
        from app.models.call import Call

        service = AIAgentService()
        call = Call(
            id=uuid4(),
            campaign_id=sample_campaign.id,
            customer_id=sample_customer.id,
            transcript_text="Customer: Hello, I'm interested in your product. How much does it cost? AI: Our pricing starts at $99/month. Customer: That sounds good. Can you call me back tomorrow at 2 PM?",
            campaign=sample_campaign,
            customer=sample_customer,
        )

        with patch.object(service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value.choices = [
                MagicMock(message=MagicMock(content='{"interest_level": "HOT", "customer_intent": "Wants pricing info", "objections": [], "questions_asked": ["How much does it cost?"], "summary": "Customer interested in pricing, requested callback", "sentiment": "positive", "requires_human_followup": false, "human_followup_reason": null, "callback_requested": true, "callback_date": "2025-01-15T14:00:00", "callback_notes": "Call back tomorrow at 2 PM", "callback_ai_notes": "Customer explicitly requested callback", "opt_out_requested": false, "opt_out_reason": null}'))
            ]

            result = await service.analyze_call(call)

            assert result["interest_level"] == "HOT"
            assert result["callback_requested"] is True
            assert result["callback_date"] is not None

    @pytest.mark.asyncio
    async def test_analyze_call_without_transcript(self, sample_campaign, sample_customer):
        """Test call analysis without transcript"""
        from app.models.call import Call

        service = AIAgentService()
        call = Call(
            id=uuid4(),
            campaign_id=sample_campaign.id,
            customer_id=sample_customer.id,
            transcript_text=None,
            campaign=sample_campaign,
            customer=sample_customer,
        )

        result = await service.analyze_call(call)

        assert result["interest_level"] == "UNKNOWN"
        assert result["summary"] == "No transcript available"

    @pytest.mark.asyncio
    async def test_generate_call_summary(self):
        """Test call summary generation"""
        service = AIAgentService()

        with patch.object(service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value.choices = [
                MagicMock(message=MagicMock(content="Customer showed high interest in the product and requested a callback for tomorrow."))
            ]

            summary = await service.generate_call_summary(
                "Customer: I'm interested. How much? AI: $99/month. Customer: Call me tomorrow at 2 PM.",
                "Product launch campaign"
            )

            assert "interested" in summary.lower()
            assert "callback" in summary.lower()