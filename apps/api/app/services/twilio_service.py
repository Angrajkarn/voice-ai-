# Twilio Service - Handles all Twilio API interactions

from typing import Any

from app.core.config import settings
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client


class TwilioService:
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.phone_number = settings.TWILIO_PHONE_NUMBER
        self.client = None
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)

    def is_configured(self) -> bool:
        return self.client is not None

    async def make_call(
        self,
        to_number: str,
        from_number: str,
        campaign_id: str,
        call_id: str,
        webhook_base_url: str | None = None,
    ) -> str | None:
        """Make an outbound call"""
        if not self.is_configured():
            raise ValueError("Twilio not configured")

        base_url = webhook_base_url or settings.TWILIO_WEBHOOK_BASE_URL
        if not base_url:
            raise ValueError("Webhook base URL not configured")

        try:
            call = self.client.calls.create(
                to=to_number,
                from_=from_number,
                url=f"{base_url}/webhooks/twilio/voice?campaign_id={campaign_id}&call_id={call_id}",
                status_callback=f"{base_url}/webhooks/twilio/status?campaign_id={campaign_id}&call_id={call_id}",
                status_callback_event=["initiated", "ringing", "answered", "completed", "busy", "failed", "no-answer", "canceled"],
                status_callback_method="POST",
                record=True,
                recording_channels="mono",
                recording_status_callback=f"{base_url}/webhooks/twilio/recording?campaign_id={campaign_id}&call_id={call_id}",
                recording_status_callback_method="POST",
                machine_detection="Enable",
                machine_detection_timeout=5,
                timeout=30,
            )
            return call.sid
        except TwilioRestException as e:
            raise Exception(f"Twilio error: {e.msg}")

    async def end_call(self, call_sid: str) -> bool:
        """End an active call"""
        if not self.is_configured():
            return False

        try:
            self.client.calls(call_sid).update(status="completed")
            return True
        except TwilioRestException:
            return False

    async def get_call_details(self, call_sid: str) -> dict[str, Any] | None:
        """Get call details from Twilio"""
        if not self.is_configured():
            return None

        try:
            call = self.client.calls(call_sid).fetch()
            return {
                "sid": call.sid,
                "status": call.status,
                "duration": call.duration,
                "start_time": call.start_time,
                "end_time": call.end_time,
                "price": call.price,
                "direction": call.direction,
                "from": call.from_,
                "to": call.to,
            }
        except TwilioRestException:
            return None

    async def get_recording(self, recording_sid: str) -> dict[str, Any] | None:
        """Get recording details"""
        if not self.is_configured():
            return None

        try:
            recording = self.client.recordings(recording_sid).fetch()
            return {
                "sid": recording.sid,
                "call_sid": recording.call_sid,
                "duration": recording.duration,
                "channels": recording.channels,
                "source": recording.source,
                "status": recording.status,
                "url": f"https://api.twilio.com{recording.uri.replace('.json', '.mp3')}",
            }
        except TwilioRestException:
            return None

    async def download_recording(self, recording_sid: str) -> bytes | None:
        """Download recording audio"""
        if not self.is_configured():
            return None

        try:
            recording = self.client.recordings(recording_sid).fetch()
            media_url = f"https://api.twilio.com{recording.uri.replace('.json', '.mp3')}"
            # In production, use httpx to download
            return None
        except TwilioRestException:
            return None

    async def send_sms(
        self,
        to_number: str,
        from_number: str,
        body: str,
    ) -> str | None:
        """Send SMS message"""
        if not self.is_configured():
            return None

        try:
            message = self.client.messages.create(
                to=to_number,
                from_=from_number,
                body=body,
            )
            return message.sid
        except TwilioRestException:
            return None

    async def get_phone_numbers(self) -> List[dict[str, Any]]:
        """Get available phone numbers"""
        if not self.is_configured():
            return []

        try:
            numbers = self.client.incoming_phone_numbers.list(limit=50)
            return [
                {
                    "sid": n.sid,
                    "phone_number": n.phone_number,
                    "friendly_name": n.friendly_name,
                    "capabilities": n.capabilities,
                }
                for n in numbers
            ]
        except TwilioRestException:
            return []

    async def validate_webhook_signature(
        self,
        url: str,
        params: dict[str, str],
        signature: str,
    ) -> bool:
        """Validate Twilio webhook signature"""
        if not self.is_configured():
            return False

        from twilio.request_validator import RequestValidator
        validator = RequestValidator(self.auth_token)
        return validator.validate(url, params, signature)