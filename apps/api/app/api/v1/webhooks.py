# Webhook API routes for Twilio and other providers

from uuid import UUID

from app.db.session import get_db
from app.services.call_service import CallService
from app.services.twilio_service import TwilioService
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/twilio/voice")
async def twilio_voice_webhook(
    request: Request,
    campaign_id: UUID = Form(...),
    call_id: UUID = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Handle incoming Twilio voice webhook - returns TwiML"""
    form_data = await request.form()
    data = dict(form_data)

    # Validate webhook signature
    twilio = TwilioService()
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

    # Get AI agent configuration
    campaign = call.campaign
    ai_service = AIAgentService()
    session_config = await ai_service.get_realtime_session_config(campaign, call.customer)

    # For now, use a simple TwiML flow
    # In production, this would connect to OpenAI Realtime API via Media Streams

    gather = Gather(
        input="speech",
        action=f"/webhooks/twilio/gather?campaign_id={campaign_id}&call_id={call_id}",
        method="POST",
        language="en-IN",
        speech_timeout="auto",
        enhanced=True,
    )

    # Generate opening script
    opening = await ai_service.generate_opening_script(campaign, call.customer)
    gather.say(opening, voice="alice", language="en-IN")

    response.append(gather)

    # Fallback if no speech detected
    response.say("I didn't hear anything. Let me try again.", voice="alice", language="en-IN")
    response.redirect(f"/webhooks/twilio/voice?campaign_id={campaign_id}&call_id={call_id}")

    return Response(content=str(response), media_type="application/xml")


@router.post("/twilio/gather")
async def twilio_gather_webhook(
    request: Request,
    campaign_id: UUID = Form(...),
    call_id: UUID = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Handle speech input from customer"""
    form_data = await request.form()
    data = dict(form_data)

    speech_result = data.get("SpeechResult", "")
    confidence = data.get("Confidence", "0")

    # Get call
    service = CallService(db)
    call = await service.get_by_id(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    # In production, this would send to OpenAI Realtime API
    # For now, return a simple response

    from twilio.twiml.voice_response import Gather, VoiceResponse

    response = VoiceResponse()

    # Simple response logic
    if "interested" in speech_result.lower() or "yes" in speech_result.lower():
        response.say("Great! Let me tell you more about our offering.", voice="alice")
    elif "not interested" in speech_result.lower() or "no" in speech_result.lower():
        response.say("I understand. Thank you for your time. Have a great day!", voice="alice")
        response.hangup()
    elif "callback" in speech_result.lower() or "call back" in speech_result.lower():
        response.say("Sure, I can schedule a callback for you. What time works best?", voice="alice")
    else:
        response.say("I see. Could you tell me more about what you're looking for?", voice="alice")

    # Continue gathering
    gather = Gather(
        input="speech",
        action=f"/webhooks/twilio/gather?campaign_id={campaign_id}&call_id={call_id}",
        method="POST",
        language="en-IN",
    )
    response.append(gather)

    return Response(content=str(response), media_type="application/xml")


@router.post("/twilio/status")
async def twilio_status_webhook(
    request: Request,
    campaign_id: UUID = Form(...),
    call_id: UUID = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Handle Twilio call status callbacks"""
    form_data = await request.form()
    data = dict(form_data)

    # Validate signature
    twilio = TwilioService()
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)

    if not twilio.validate_webhook_signature(url, data, signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    call_sid = data.get("CallSid")
    call_status = data.get("CallStatus")
    duration = data.get("CallDuration")

    service = CallService(db)
    await service.handle_twilio_status(call_sid, call_status, duration)

    return {"status": "ok"}


@router.post("/twilio/recording")
async def twilio_recording_webhook(
    request: Request,
    campaign_id: UUID = Form(...),
    call_id: UUID = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Handle Twilio recording callbacks"""
    form_data = await request.form()
    data = dict(form_data)

    # Validate signature
    twilio = TwilioService()
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)

    if not twilio.validate_webhook_signature(url, data, signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    call_sid = data.get("CallSid")
    recording_sid = data.get("RecordingSid")
    recording_url = data.get("RecordingUrl")
    duration = data.get("RecordingDuration")

    service = CallService(db)
    await service.handle_recording(call_sid, recording_sid, recording_url, duration)

    return {"status": "ok"}


@router.post("/twilio/transcription")
async def twilio_transcription_webhook(
    request: Request,
    campaign_id: UUID = Form(...),
    call_id: UUID = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Handle Twilio transcription callbacks"""
    form_data = await request.form()
    data = dict(form_data)

    # Validate signature
    twilio = TwilioService()
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)

    if not twilio.validate_webhook_signature(url, data, signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    call_sid = data.get("CallSid")
    transcription_sid = data.get("TranscriptionSid")
    transcription_text = data.get("TranscriptionText")

    service = CallService(db)
    await service.handle_transcription(call_sid, transcription_sid, transcription_text)

    return {"status": "ok"}