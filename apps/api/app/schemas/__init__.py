# Schemas package - exports all Pydantic schemas

from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.organization import OrganizationCreate, OrganizationUpdate, OrganizationResponse
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerImport
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse, CampaignValidate
from app.schemas.call import CallCreate, CallUpdate, CallResponse, CallTranscriptResponse, CallRecordingResponse
from app.schemas.callback import CallbackCreate, CallbackUpdate, CallbackResponse
from app.schemas.integration import IntegrationCreate, IntegrationUpdate, IntegrationResponse, IntegrationTest
from app.schemas.analytics import DashboardMetrics, CampaignAnalytics, OrganizationAnalytics
from app.schemas.webhook import TwilioVoiceWebhook, TwilioStatusWebhook, TwilioRecordingWebhook, TwilioTranscriptionWebhook

__all__ = [
    "UserCreate", "UserUpdate", "UserResponse",
    "OrganizationCreate", "OrganizationUpdate", "OrganizationResponse",
    "CustomerCreate", "CustomerUpdate", "CustomerResponse", "CustomerImport",
    "CampaignCreate", "CampaignUpdate", "CampaignResponse", "CampaignValidate",
    "CallCreate", "CallUpdate", "CallResponse", "CallTranscriptResponse", "CallRecordingResponse",
    "CallbackCreate", "CallbackUpdate", "CallbackResponse",
    "IntegrationCreate", "IntegrationUpdate", "IntegrationResponse", "IntegrationTest",
    "DashboardMetrics", "CampaignAnalytics", "OrganizationAnalytics",
    "TwilioVoiceWebhook", "TwilioStatusWebhook", "TwilioRecordingWebhook", "TwilioTranscriptionWebhook",
]