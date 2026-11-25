# Free TTS Service - Supports multiple free/open-source TTS engines

from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
import subprocess
import tempfile
import os
import json
import logging
import base64
from pathlib import Path
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class FreeTTSService:
    """
    Free TTS Service supporting multiple open-source engines:
    - Piper TTS (fast, high quality, many voices)
    - Coqui TTS (high quality, multi-lingual)
    - eSpeak NG (lightweight, many languages)
    - System TTS (macOS say, Windows SAPI, Linux festival)
    """

    def __init__(self):
        self.engine = settings.FREE_TTS_ENGINE or "piper"
        self.piper_path = settings.PIPER_PATH or "piper"
        self.coqui_model = settings.COQUI_MODEL or "tts_models/multilingual/multi-dataset/xtts_v2"
        self.cache_dir = Path(settings.FREE_TTS_CACHE_DIR or "./storage/tts_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Voice mappings for different engines
        self.voice_map = {
            "piper": {
                "en-IN": "en_IN-karun-medium",
                "hi-IN": "hi_IN-aryan-medium",
                "en-US": "en_US-lessac-medium",
                "en-GB": "en_GB-alan-medium",
                "default": "en_US-lessac-medium",
            },
            "coqui": {
                "en-IN": "en_IN-karun",
                "hi-IN": "hi_IN-aryan",
                "en-US": "en_US-ljspeech",
                "default": "en_US-ljspeech",
            },
            "espeak": {
                "en-IN": "en-in",
                "hi-IN": "hi",
                "en-US": "en-us",
                "en-GB": "en-gb",
                "default": "en-us",
            }
        }

    async def text_to_speech(
        self,
        text: str,
        language: str = "en-IN",
        voice: Optional[str] = None,
        speed: float = 1.0,
    ) -> bytes:
        """
        Convert text to speech using free TTS engine
        Returns audio bytes (WAV format)
        """
        # Check cache first
        cache_key = self._get_cache_key(text, language, voice, speed)
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        # Generate audio based on engine
        if self.engine == "piper":
            try:
                audio = await self._piper_tts(text, language, voice, speed)
            except Exception:
                if not await self._check_command("espeak-ng"):
                    raise
                logger.warning("Piper TTS failed; falling back to eSpeak NG", exc_info=True)
                audio = await self._espeak_tts(text, language, None, speed)
        elif self.engine == "coqui":
            audio = await self._coqui_tts(text, language, voice, speed)
        elif self.engine == "espeak":
            audio = await self._espeak_tts(text, language, voice, speed)
        elif self.engine == "system":
            audio = await self._system_tts(text, language, voice, speed)
        else:
            # Fallback to Piper
            audio = await self._piper_tts(text, language, voice, speed)

        # Cache the result
        self._save_cache(cache_key, audio)
        return audio

    def _get_cache_key(self, text: str, language: str, voice: Optional[str], speed: float) -> str:
        """Generate cache key for TTS request"""
        import hashlib
        content = f"{text}|{language}|{voice}|{speed}|{self.engine}"
        return hashlib.md5(content.encode()).hexdigest() + ".wav"

    def _get_cached(self, cache_key: str) -> Optional[bytes]:
        """Get cached audio if exists"""
        cache_file = self.cache_dir / cache_key
        if cache_file.exists():
            return cache_file.read_bytes()
        return None

    def _save_cache(self, cache_key: str, audio: bytes):
        """Save audio to cache"""
        cache_file = self.cache_dir / cache_key
        cache_file.write_bytes(audio)

    # ============================================
    # Piper TTS (Recommended - Fast & High Quality)
    # ============================================
    async def _piper_tts(
        self,
        text: str,
        language: str,
        voice: Optional[str],
        speed: float,
    ) -> bytes:
        """Generate speech using Piper TTS"""
        voice_name = voice or self.voice_map["piper"].get(language, self.voice_map["piper"]["default"])

        if not await self._check_command(self.piper_path):
            raise FileNotFoundError(f"Piper executable not found: {self.piper_path}")

        # Check if voice model exists, download if needed
        model_path = await self._ensure_piper_voice(voice_name)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            output_path = tmp.name

        try:
            # Build piper command
            cmd = [
                self.piper_path,
                "--model", model_path,
                "--output_file", output_path,
            ]

            if speed != 1.0:
                cmd.extend(["--length_scale", str(1.0 / speed)])

            # Run piper with text input
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate(input=text.encode())

            if process.returncode != 0:
                raise Exception(f"Piper TTS failed: {stderr.decode()}")

            # Read generated audio
            with open(output_path, "rb") as f:
                audio = f.read()

            return audio

        finally:
            # Cleanup temp file
            if os.path.exists(output_path):
                os.unlink(output_path)

    async def _ensure_piper_voice(self, voice_name: str) -> str:
        """Ensure Piper voice model is downloaded"""
        # Piper models are typically stored in ~/.local/share/piper/voices/
        # or in a local voices directory
        voices_dir = Path.home() / ".local" / "share" / "piper" / "voices"
        voices_dir.mkdir(parents=True, exist_ok=True)

        model_path = voices_dir / f"{voice_name}.onnx"
        config_path = voices_dir / f"{voice_name}.onnx.json"

        if model_path.exists() and config_path.exists():
            return str(model_path)

        # Download voice model
        await self._download_piper_voice(voice_name, voices_dir)
        return str(model_path)

    async def _download_piper_voice(self, voice_name: str, voices_dir: Path):
        """Download Piper voice model from GitHub releases"""
        # Piper voices are hosted at https://github.com/rhasspy/piper/releases
        # For now, we'll use a known working voice
        # In production, implement proper download from Piper's voice repository

        # Common voices that work well:
        # en_US-lessac-medium, en_US-amy-medium, en_GB-alan-medium
        # hi_IN-aryan-medium, en_IN-karun-medium

        base_url = "https://github.com/rhasspy/piper/releases/download/v1.2.0"

        async with httpx.AsyncClient(timeout=120.0) as client:
            # Download model
            model_url = f"{base_url}/{voice_name}.onnx"
            response = await client.get(model_url)
            if response.status_code == 200:
                (voices_dir / f"{voice_name}.onnx").write_bytes(response.content)

            # Download config
            config_url = f"{base_url}/{voice_name}.onnx.json"
            response = await client.get(config_url)
            if response.status_code == 200:
                (voices_dir / f"{voice_name}.onnx.json").write_bytes(response.content)

    # ============================================
    # Coqui TTS (High Quality, Multi-lingual)
    # ============================================
    async def _coqui_tts(
        self,
        text: str,
        language: str,
        voice: Optional[str],
        speed: float,
    ) -> bytes:
        """Generate speech using Coqui TTS"""
        try:
            from TTS.api import TTS

            # Initialize TTS model (cached)
            if not hasattr(self, '_coqui_tts_model'):
                self._coqui_tts_model = TTS(self.coqui_model)

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                output_path = tmp.name

            try:
                # Coqui TTS supports speaker_wav for voice cloning
                # For now, use default speaker
                self._coqui_tts_model.tts_to_file(
                    text=text,
                    file_path=output_path,
                    language=language.split("-")[0],  # en, hi, etc.
                    speed=speed,
                )

                with open(output_path, "rb") as f:
                    audio = f.read()

                return audio

            finally:
                if os.path.exists(output_path):
                    os.unlink(output_path)

        except ImportError:
            # Coqui TTS is optional; use installed eSpeak before trying Piper.
            if await self._check_command("espeak-ng"):
                return await self._espeak_tts(text, language, None, speed)
            return await self._piper_tts(text, language, voice, speed)

    # ============================================
    # eSpeak NG (Lightweight, Many Languages)
    # ============================================
    async def _espeak_tts(
        self,
        text: str,
        language: str,
        voice: Optional[str],
        speed: float,
    ) -> bytes:
        """Generate speech using eSpeak NG"""
        voice_name = voice or self.voice_map["espeak"].get(language, self.voice_map["espeak"]["default"])

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            output_path = tmp.name

        try:
            # Build espeak command
            cmd = [
                "espeak-ng",
                "-v", voice_name,
                "-s", str(int(175 * speed)),  # words per minute
                "-w", output_path,
                text,
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise Exception(f"eSpeak NG failed: {stderr.decode()}")

            with open(output_path, "rb") as f:
                audio = f.read()

            return audio

        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    # ============================================
    # System TTS (Built-in OS TTS)
    # ============================================
    async def _system_tts(
        self,
        text: str,
        language: str,
        voice: Optional[str],
        speed: float,
    ) -> bytes:
        """Generate speech using system TTS (macOS say, Windows SAPI, Linux festival)"""
        import platform

        system = platform.system()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            output_path = tmp.name

        try:
            if system == "Darwin":  # macOS
                cmd = ["say", "-o", output_path, "--data-format=LEF32@22050", text]
                if voice:
                    cmd.extend(["-v", voice])

            elif system == "Windows":
                # Use PowerShell with SAPI
                ps_script = f'''
                Add-Type -AssemblyName System.Speech
                $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
                $synth.SetOutputToWaveFile("{output_path}")
                $synth.Rate = {int((speed - 1) * 10)}
                $synth.Speak("{text.replace('"', '""')}")
                $synth.Dispose()
                '''
                cmd = ["powershell", "-Command", ps_script]

            else:  # Linux - try festival or spd-say
                if await self._check_command("festival"):
                    cmd = ["festival", "--tts", "--output", output_path]
                    # festival reads from stdin
                    process = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdin=asyncio.subprocess.PIPE,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    await process.communicate(input=text.encode())
                    with open(output_path, "rb") as f:
                        return f.read()
                elif await self._check_command("spd-say"):
                    cmd = ["spd-say", "-o", "file", "-f", output_path, text]
                else:
                    raise Exception("No system TTS available")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise Exception(f"System TTS failed: {stderr.decode()}")

            with open(output_path, "rb") as f:
                audio = f.read()

            return audio

        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    async def _check_command(self, command: str) -> bool:
        """Check if a command is available"""
        try:
            process = await asyncio.create_subprocess_exec(
                "which", command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await process.communicate()
            return process.returncode == 0
        except Exception:
            return False

    # ============================================
    # Utility Methods
    # ============================================
    async def get_available_voices(self) -> Dict[str, List[str]]:
        """Get list of available voices for each engine"""
        return {
            "piper": list(self.voice_map["piper"].keys()),
            "coqui": list(self.voice_map["coqui"].keys()),
            "espeak": list(self.voice_map["espeak"].keys()),
        }

    async def test_engine(self, engine: str) -> Dict[str, Any]:
        """Test if a TTS engine works"""
        try:
            test_text = "Hello, this is a test of the free text to speech system."
            audio = await self.text_to_speech(test_text, engine=engine)
            return {
                "success": True,
                "engine": engine,
                "audio_size": len(audio),
                "duration_estimate": len(audio) / 32000,  # rough estimate
            }
        except Exception as e:
            return {
                "success": False,
                "engine": engine,
                "error": str(e),
            }


# Convenience function for easy usage
async def synthesize_speech(
    text: str,
    language: str = "en-IN",
    engine: str = "piper",
    voice: Optional[str] = None,
    speed: float = 1.0,
) -> bytes:
    """Quick function to synthesize speech with free TTS"""
    service = FreeTTSService()
    service.engine = engine
    return await service.text_to_speech(text, language, voice, speed)