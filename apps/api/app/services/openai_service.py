# OpenAI Service - Handles OpenAI API interactions

from typing import Optional, Dict, Any, List
from datetime import datetime
import openai
from openai import AsyncOpenAI

from app.core.config import settings


class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.realtime_model = settings.OPENAI_REALTIME_MODEL
        self.tts_model = settings.OPENAI_TTS_MODEL
        self.tts_voice = settings.OPENAI_TTS_VOICE
        self.whisper_model = settings.OPENAI_WHISPER_MODEL

    async def create_realtime_session(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Realtime API session"""
        try:
            session = await self.client.beta.realtime.sessions.create(**config)
            return {
                "session_id": session.id,
                "client_secret": session.client_secret.value,
                "expires_at": session.client_secret.expires_at,
            }
        except Exception as e:
            raise Exception(f"Failed to create realtime session: {str(e)}")

    async def text_to_speech(self, text: str, voice: Optional[str] = None) -> bytes:
        """Convert text to speech"""
        try:
            response = await self.client.audio.speech.create(
                model=self.tts_model,
                voice=voice or self.tts_voice,
                input=text,
                response_format="mp3",
            )
            return response.content
        except Exception as e:
            raise Exception(f"TTS failed: {str(e)}")

    async def speech_to_text(self, audio_data: bytes, language: str = "en") -> str:
        """Convert speech to text using Whisper"""
        try:
            import io
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"

            response = await self.client.audio.transcriptions.create(
                model=self.whisper_model,
                file=audio_file,
                language=language,
                response_format="text",
            )
            return response
        except Exception as e:
            raise Exception(f"STT failed: {str(e)}")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        response_format: Optional[Dict[str, str]] = None,
    ) -> str:
        """Get chat completion"""
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if response_format:
                kwargs["response_format"] = response_format

            response = await self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Chat completion failed: {str(e)}")

    async def create_embedding(self, text: str) -> List[float]:
        """Create text embedding"""
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Embedding failed: {str(e)}")

    async def moderate_content(self, text: str) -> Dict[str, Any]:
        """Moderate content for safety"""
        try:
            response = await self.client.moderations.create(input=text)
            return response.results[0].model_dump()
        except Exception as e:
            raise Exception(f"Moderation failed: {str(e)}")