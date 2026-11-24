# Schemas package - exports all Pydantic schemas

from app.schemas.analytics import (
    CampaignAnalytics,
    DashboardMetrics,
    OrganizationAnalytics,
)
from app.schemas.call import (
    CallCreate,
    CallRecordingResponse,
    CallResponse,
    CallTranscriptResponse,
    CallUpdate,
)
from app.schemas.callback import CallbackCreate, CallbackResponse, CallbackUpdate
from app.schemas.campaign import (
    CampaignCreate,
    CampaignResponse,
    CampaignUpdate,
    CampaignValidate,
)
from app.schemas.customer import (
    CustomerCreate,
    CustomerImport,
    CustomerResponse,
    CustomerUpdate,
)
from app.schemas.integration import (
    IntegrationCreate,
    IntegrationResponse,
    IntegrationTest,
    IntegrationUpdate,
)
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.schemas.webhook import (
    TwilioRecordingWebhook,
    TwilioStatusWebhook,
    TwilioTranscriptionWebhook,
    TwilioVoiceWebhook,
)

__all__ = [
    "CallCreate",
    "CallRecordingResponse",
    "CallResponse",
    "CallTranscriptResponse",
    "CallUpdate",
    "CallbackCreate",
    "CallbackResponse",
    "CallbackUpdate",
    "CampaignAnalytics",
    "CampaignCreate",
    "CampaignResponse",
    "CampaignUpdate",
    "CampaignValidate",
    "CustomerCreate",
    "CustomerImport",
    "CustomerResponse",
    "CustomerUpdate",
    "DashboardMetrics",
    "IntegrationCreate",
    "IntegrationResponse",
    "IntegrationTest",
    "IntegrationUpdate",
    "OrganizationAnalytics",
    "OrganizationCreate",
    "OrganizationResponse",
    "OrganizationUpdate",
    "TwilioRecordingWebhook",
    "TwilioStatusWebhook",
    "TwilioTranscriptionWebhook",
    "TwilioVoiceWebhook",
    "UserCreate",
    "UserResponse",
    "UserUpdate",
]