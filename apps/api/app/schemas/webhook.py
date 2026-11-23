# Webhook schemas for Twilio and other providers

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class TwilioVoiceWebhook(BaseModel):
    # Required fields
    CallSid: str
    AccountSid: str
    From: str
    To: str
    CallStatus: str
    Direction: str
    ApiVersion: str

    # Optional fields
    ParentCallSid: Optional[str] = None
    FromFormatted: Optional[str] = None
    ToFormatted: Optional[str] = None
    CallerName: Optional[str] = None
    ForwardedFrom: Optional[str] = None
    ForwardedFromFormatted: Optional[str] = None

    # For Gather/Twiml
    Digits: Optional[str] = None
    SpeechResult: Optional[str] = None
    Confidence: Optional[str] = None
    RecognitionStatus: Optional[str] = None

    # Recording
    RecordingUrl: Optional[str] = None
    RecordingSid: Optional[str] = None
    RecordingDuration: Optional[str] = None
    RecordingChannels: Optional[str] = None
    RecordingSource: Optional[str] = None
    RecordingStatus: Optional[str] = None

    # Transcription
    TranscriptionText: Optional[str] = None
    TranscriptionSid: Optional[str] = None
    TranscriptionStatus: Optional[str] = None


class TwilioStatusWebhook(BaseModel):
    CallSid: str
    AccountSid: str
    CallStatus: str
    ApiVersion: str
    Direction: str
    From: str
    To: str
    CallDuration: Optional[str] = None
    SipResponseCode: Optional[str] = None
    ErrorCode: Optional[str] = None
    ErrorMessage: Optional[str] = None


class TwilioRecordingWebhook(BaseModel):
    AccountSid: str
    ApiVersion: str
    CallSid: str
    RecordingSid: str
    RecordingUrl: str
    RecordingStatus: str
    RecordingDuration: str
    RecordingChannels: str
    RecordingSource: str
    RecordingStartTime: str


class TwilioTranscriptionWebhook(BaseModel):
    AccountSid: str
    ApiVersion: str
    CallSid: str
    TranscriptionSid: str
    TranscriptionText: str
    TranscriptionStatus: str
    TranscriptionUrl: str
    RecordingSid: str
    RecordingUrl: str


class GoogleSheetsWebhook(BaseModel):
    spreadsheetId: str
    sheetId: int
    changes: list


class N8NCallbackWebhook(BaseModel):
    workflowId: str
    executionId: str
    data: Dict[str, Any]
    timestamp: datetime