# Webhook API routes for Twilio and other providers

from uuid import UUID
from datetime import datetime
import json

from sqlalchemy import and_, or_, select
from app.core.crypto import decrypt_secret
from app.models.campaign import Campaign
from app.models.enums import CustomerStatus, IntegrationType
from app.models.integration import Integration

from app.db.session import get_db
from app.services.ai_agent_service import AIAgentService
from app.services.call_service import CallService
from app.services.twilio_service import TwilioService
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


async def _twilio_for_campaign(db: AsyncSession, campaign_id: UUID) -> TwilioService:
    campaign = await db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    integration = await db.scalar(select(Integration).where(and_(
        Integration.organization_id == campaign.organization_id,
        Integration.type == IntegrationType.TWILIO,
        Integration.is_active.is_(True),
        or_(Integration.campaign_id == campaign.id, Integration.campaign_id.is_(None)),
    )).order_by((Integration.campaign_id == campaign.id).desc()).limit(1))
    if not integration:
        return TwilioService()
    config = integration.config
    if isinstance(config, str):
        config = json.loads(config)
    return TwilioService(
        account_sid=config.get("account_sid"),
        auth_token=decrypt_secret(config.get("auth_token", "")),
        phone_number=config.get("phone_number"),
    )


@router.post("/twilio/voice")
async def twilio_voice_webhook(
    request: Request,
    campaign_id: UUID = Query(...),
    call_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Handle incoming Twilio voice webhook - returns TwiML"""
    form_data = await request.form()
    data = {key: value for key, value in form_data.items() if isinstance(value, str)}

    # Validate webhook signature
    twilio = await _twilio_for_campaign(db, campaign_id)
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)

    if not twilio.validate_webhook_signature(url, data, signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    # Get call
    service = CallService(db)
    call = await service.get_by_id(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    # Generate TwiML response
    from twilio.twiml.voice_response import Gather, VoiceResponse

    response = VoiceResponse()

    campaign = call.campaign
    ai_service = AIAgentService()

    language = "en-IN" if campaign.language == "hinglish" else campaign.language
    voice = campaign.voice_id or "Google.en-IN-Wavenet-D"
    gather = Gather(
        input="speech",
        action=f"/webhooks/twilio/gather?campaign_id={campaign_id}&call_id={call_id}",
        method="POST",
        language=language,
        speech_timeout="auto",
        enhanced=True,
    )
    opening = await ai_service.generate_opening_script(campaign, call.customer)
    gather.say(opening, voice=voice, language=language)

    response.append(gather)

    # Fallback if no speech detected
    response.say("I didn't hear anything. Let me try again.", voice=voice, language=language)
    response.redirect(f"/webhooks/twilio/voice?campaign_id={campaign_id}&call_id={call_id}")

    return Response(content=str(response), media_type="application/xml")


@router.post("/twilio/gather")
async def twilio_gather_webhook(
    request: Request,
    campaign_id: UUID = Query(...),
    call_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Handle speech input from customer"""
    form_data = await request.form()
    data = {key: value for key, value in form_data.items() if isinstance(value, str)}

    speech_result = data.get("SpeechResult", "")
    confidence = data.get("Confidence", "0")

    # Get call and validate the signed Twilio request.
    service = CallService(db)
    call = await service.get_by_id(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    twilio = await _twilio_for_campaign(db, campaign_id)
    if not twilio.validate_webhook_signature(str(request.url), data, request.headers.get("X-Twilio-Signature", "")):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    from twilio.twiml.voice_response import Gather, VoiceResponse

    response = VoiceResponse()
    language = "en-IN" if call.campaign.language == "hinglish" else call.campaign.language
    voice = call.campaign.voice_id or "Google.en-IN-Wavenet-D"
    normalized = speech_result.lower()
    opt_out_phrases = ("stop calling", "do not call", "don't call", "remove me", "unsubscribe", "stop")
    if any(phrase in normalized for phrase in opt_out_phrases):
        call.customer.do_not_call = True
        call.customer.status = CustomerStatus.OPTED_OUT
        call.customer.opted_out_at = datetime.utcnow()
        call.customer.opt_out_reason = speech_result
        await db.commit()
        response.say("I understand. We will not call you again. Goodbye.", voice=voice, language=language)
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    ai_service = AIAgentService()
    history = call.transcript_text or ""
    reply = await ai_service.generate_response(call.campaign, call.customer, speech_result, history)
    call.transcript_text = (history + f"\\nCustomer: {speech_result}\\nAgent: {reply}").strip()
    await db.commit()
    response.say(reply, voice=voice, language=language)

    gather = Gather(
        input="speech",
        action=f"/webhooks/twilio/gather?campaign_id={campaign_id}&call_id={call_id}",
        method="POST",
        language=language,
        speech_timeout="auto",
    )
    response.append(gather)

    return Response(content=str(response), media_type="application/xml")


@router.post("/twilio/status")
async def twilio_status_webhook(
    request: Request,
    campaign_id: UUID = Query(...),
    call_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Handle Twilio call status callbacks"""
    form_data = await request.form()
    data = {key: value for key, value in form_data.items() if isinstance(value, str)}

    # Validate signature
    twilio = await _twilio_for_campaign(db, campaign_id)
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)

    if not twilio.validate_webhook_signature(url, data, signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    call_sid = data.get("CallSid")
    call_status = data.get("CallStatus")
    duration = data.get("CallDuration")
    if not call_sid or not call_status:
        raise HTTPException(status_code=400, detail="Missing Twilio call status fields")

    service = CallService(db)
    await service.handle_twilio_status(call_sid, call_status, duration)

    return {"status": "ok"}


@router.post("/twilio/recording")
async def twilio_recording_webhook(
    request: Request,
    campaign_id: UUID = Query(...),
    call_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Handle Twilio recording callbacks"""
    form_data = await request.form()
    data = {key: value for key, value in form_data.items() if isinstance(value, str)}

    # Validate signature
    twilio = await _twilio_for_campaign(db, campaign_id)
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)

    if not twilio.validate_webhook_signature(url, data, signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    call_sid = data.get("CallSid")
    recording_sid = data.get("RecordingSid")
    recording_url = data.get("RecordingUrl")
    duration = data.get("RecordingDuration")
    if not call_sid or not recording_sid or not recording_url or not duration:
        raise HTTPException(status_code=400, detail="Missing Twilio recording fields")

    service = CallService(db)
    await service.handle_recording(call_sid, recording_sid, recording_url, duration)

    return {"status": "ok"}


@router.post("/twilio/transcription")
async def twilio_transcription_webhook(
    request: Request,
    campaign_id: UUID = Query(...),
    call_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Handle Twilio transcription callbacks"""
    form_data = await request.form()
    data = {key: value for key, value in form_data.items() if isinstance(value, str)}

    # Validate signature
    twilio = await _twilio_for_campaign(db, campaign_id)
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)

    if not twilio.validate_webhook_signature(url, data, signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    call_sid = data.get("CallSid")
    transcription_sid = data.get("TranscriptionSid")
    transcription_text = data.get("TranscriptionText")
    if not call_sid or not transcription_sid or not transcription_text:
        raise HTTPException(status_code=400, detail="Missing Twilio transcription fields")

    service = CallService(db)
    await service.handle_transcription(call_sid, transcription_sid, transcription_text)

    return {"status": "ok"}