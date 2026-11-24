# Webhook schemas for Twilio and other providers

from datetime import datetime
from typing import Any

from pydantic import BaseModel


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
    ParentCallSid: str | None = None
    FromFormatted: str | None = None
    ToFormatted: str | None = None
    CallerName: str | None = None
    ForwardedFrom: str | None = None
    ForwardedFromFormatted: str | None = None

    # For Gather/Twiml
    Digits: str | None = None
    SpeechResult: str | None = None
    Confidence: str | None = None
    RecognitionStatus: str | None = None

    # Recording
    RecordingUrl: str | None = None
    RecordingSid: str | None = None
    RecordingDuration: str | None = None
    RecordingChannels: str | None = None
    RecordingSource: str | None = None
    RecordingStatus: str | None = None

    # Transcription
    TranscriptionText: str | None = None
    TranscriptionSid: str | None = None
    TranscriptionStatus: str | None = None


class TwilioStatusWebhook(BaseModel):
    CallSid: str
    AccountSid: str
    CallStatus: str
    ApiVersion: str
    Direction: str
    From: str
    To: str
    CallDuration: str | None = None
    SipResponseCode: str | None = None
    ErrorCode: str | None = None
    ErrorMessage: str | None = None


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
    data: dict[str, Any]
    timestamp: datetime