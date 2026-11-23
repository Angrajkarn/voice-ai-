# AI Agent Service - Handles AI conversation logic and call analysis
# Uses OpenAI for AI logic (GPT-4o) but FREE TTS for voice synthesis

from typing: List, Dict, Any, Optional
from datetime: datetime
from uuid: UUID
import json
import openai
from openai import AsyncOpenAI

from app.models.call import Call
from app.models.campaign import Campaign
from app.models.customer import Customer
from app.models.enums import InterestLevel
from app.core.config import settings
from app.services.free_tts_service import FreeTTSService


class AIAgentService:
    def __init__(self):
        # OpenAI for AI reasoning (cheap - only text)
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.realtime_model = settings.OPENAI_REALTIME_MODEL

        # Free TTS for voice synthesis (no cost)
        self.free_tts = FreeTTSService()
        self.tts_engine = settings.FREE_TTS_ENGINE

    async def generate_opening_script(self, campaign: Campaign, customer: Customer) -> str:
        """Generate personalized opening script"""
        script = campaign.opening_script
        script = script.replace("{firstName}", customer.first_name)
        script = script.replace("{lastName}", customer.last_name)
        script = script.replace("{company}", customer.company or "your company")
        script = script.replace("{location}", customer.location or "your area")
        return script

    async def get_realtime_session_config(self, campaign: Campaign, customer: Customer) -> Dict[str, Any]:
        """Get OpenAI Realtime API session configuration"""
        instructions = f"""
{campaign.ai_instructions}

Customer Details:
- Name: {customer.first_name} {customer.last_name}
- Company: {customer.company or 'Not specified'}
- Location: {customer.location or 'Not specified'}
- Language: {customer.language}

Campaign Purpose: {campaign.purpose}

Knowledge Base:
{campaign.knowledge_base}

Guidelines:
1. Always identify yourself as an AI assistant calling on behalf of the company
2. Be polite, professional, and conversational
3. Listen actively to customer responses
4. Answer questions using the knowledge base provided
5. Never make up pricing, features, or promises
6. If customer asks something not in knowledge base, say you'll have a human follow up
7. Respect customer's time and interest level
8. Handle objections gracefully
9. End calls politely with clear next steps
10. Match the customer's language preference: {customer.language}
"""

        return {
            "model": self.realtime_model,
            "voice": campaign.voice_id,  # This will be mapped to free TTS voice
            "instructions": instructions.strip(),
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 500,
            },
            "tools": [
                {
                    "type": "function",
                    "name": "schedule_callback",
                    "description": "Schedule a callback for the customer",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date_time": {"type": "string", "description": "ISO 8601 datetime for callback"},
                            "timezone": {"type": "string", "description": "Customer's timezone"},
                            "notes": {"type": "string", "description": "Reason for callback"},
                        },
                        "required": ["date_time", "timezone", "notes"],
                    },
                },
                {
                    "type": "function",
                    "name": "transfer_to_human",
                    "description": "Transfer call to human agent",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reason": {"type": "string", "description": "Reason for transfer"},
                            "urgency": {"type": "string", "enum": ["low", "medium", "high"]},
                        },
                        "required": ["reason", "urgency"],
                    },
                },
                {
                    "type": "function",
                    "name": "end_call",
                    "description": "End the call politely",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "summary": {"type": "string", "description": "Call summary"},
                            "outcome": {"type": "string", "description": "Call outcome"},
                        },
                        "required": ["summary", "outcome"],
                    },
                },
                {
                    "type": "function",
                    "name": "log_objection",
                    "description": "Log customer objection",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "objection": {"type": "string", "description": "Customer's objection"},
                        },
                        "required": ["objection"],
                    },
                },
            ],
        }

    async def synthesize_speech(
        self,
        text: str,
        language: str = "en-IN",
        voice: Optional[str] = None,
        speed: float = 1.0,
    ) -> bytes:
        """
        Synthesize speech using FREE TTS engine
        Returns WAV audio bytes
        """
        return await self.free_tts.text_to_speech(
            text=text,
            language=language,
            voice=voice,
            speed=speed,
        )

    async def get_tts_voice_for_language(self, language: str) -> str:
        """Get appropriate free TTS voice for language"""
        return self.free_tts.voice_map.get(self.tts_engine, {}).get(
            language,
            self.free_tts.voice_map.get(self.tts_engine, {}).get("default", "en_US-lessac-medium")
        )

    async def analyze_call(self, call: Call) -> Dict[str, Any]:
        """Analyze completed call transcript using AI"""
        if not call.transcript_text:
            return {
                "interest_level": InterestLevel.UNKNOWN,
                "customer_intent": None,
                "objections": [],
                "questions_asked": [],
                "summary": "No transcript available",
                "sentiment": "neutral",
                "requires_human_followup": False,
                "human_followup_reason": None,
                "callback_requested": False,
                "callback_date": None,
                "callback_notes": None,
                "callback_ai_notes": None,
                "opt_out_requested": False,
                "opt_out_reason": None,
            }

        prompt = f"""
Analyze this call transcript and extract structured information.

Transcript:
{call.transcript_text}

Campaign Context:
- Purpose: {call.campaign.purpose if call.campaign else 'Unknown'}
- Knowledge Base: {call.campaign.knowledge_base if call.campaign else 'Not provided'}

Extract the following information as JSON:
{{
    "interest_level": "HOT|WARM|COLD|UNKNOWN",
    "customer_intent": "What the customer wants or is interested in",
    "objections": ["List of customer objections"],
    "questions_asked": ["List of questions customer asked"],
    "summary": "Brief 2-3 sentence summary of the call",
    "sentiment": "positive|neutral|negative",
    "requires_human_followup": true/false,
    "human_followup_reason": "Reason if human followup needed",
    "callback_requested": true/false,
    "callback_date": "ISO 8601 datetime if callback requested",
    "callback_notes": "What customer said about callback",
    "callback_ai_notes": "AI analysis of callback need",
    "opt_out_requested": true/false,
    "opt_out_reason": "Reason if customer opted out"
}}

Be accurate and only use information from the transcript.
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert call analyzer. Extract structured information from call transcripts accurately."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=1000,
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)

            # Validate interest level
            if result.get("interest_level") not in ["HOT", "WARM", "COLD", "UNKNOWN"]:
                result["interest_level"] = "UNKNOWN"

            return result

        except Exception as e:
            return {
                "interest_level": InterestLevel.UNKNOWN,
                "customer_intent": None,
                "objections": [],
                "questions_asked": [],
                "summary": f"Analysis failed: {str(e)}",
                "sentiment": "neutral",
                "requires_human_followup": False,
                "human_followup_reason": None,
                "callback_requested": False,
                "callback_date": None,
                "callback_notes": None,
                "callback_ai_notes": None,
                "opt_out_requested": False,
                "opt_out_reason": None,
            }

    async def generate_call_summary(self, transcript: str, campaign_purpose: str) -> str:
        """Generate a concise call summary"""
        prompt = f"""
Summarize this call in 2-3 sentences for a sales manager.

Campaign Purpose: {campaign_purpose}

Transcript:
{transcript}

Focus on: customer interest level, key objections, next steps, and any commitments made.
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional call summarizer for sales teams."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=300,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return "Summary generation failed"

    async def extract_entities(self, transcript: str) -> Dict[str, List[str]]:
        """Extract entities like prices, dates, product names from transcript"""
        prompt = f"""
Extract key entities from this call transcript:

Transcript:
{transcript}

Return JSON with:
{{
    "prices_mentioned": ["list of prices"],
    "dates_mentioned": ["list of dates/times"],
    "products_mentioned": ["list of products/services"],
    "competitors_mentioned": ["list of competitors"],
    "pain_points": ["list of customer pain points"],
    "decision_makers": ["list of decision makers mentioned"],
}}
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Extract entities from sales call transcripts."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=500,
                response_format={"type": "json_object"},
            )
            return json.loads(response.choices[0].message.content)
        except Exception:
            return {
                "prices_mentioned": [],
                "dates_mentioned": [],
                "products_mentioned": [],
                "competitors_mentioned": [],
                "pain_points": [],
                "decision_makers": [],
            }

    async def generate_follow_up_email(self, call: Call) -> str:
        """Generate follow-up email based on call"""
        prompt = f"""
Write a professional follow-up email based on this call.

Customer: {call.customer.first_name} {call.customer.last_name}
Company: {call.customer.company or 'N/A'}
Call Summary: {call.summary or 'No summary available'}
Interest Level: {call.interest_level.value}
Customer Intent: {call.customer_intent or 'Not specified'}
Objections: {', '.join(call.objections) if call.objections else 'None'}

The email should:
1. Thank them for their time
2. Reference specific discussion points
3. Address any objections raised
4. Provide relevant information from knowledge base
5. Include clear next steps or call to action
6. Be concise and professional
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional sales email writer."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
                max_tokens=500,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return "Email generation failed"