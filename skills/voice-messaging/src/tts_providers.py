"""
TTS (Text-to-Speech) provider implementations
"""

import asyncio
import os
from typing import AsyncGenerator, List

from .providers import TTSProvider, ProviderFactory


class KokoroTTS(TTSProvider):
    """Kokoro-82M TTS provider via FastAPI"""

    def __init__(self, base_url: str = "http://localhost:8880/v1",
                 voice: str = "af_bella", format: str = "ogg", **kwargs):
        """
        Initialize Kokoro TTS

        Args:
            base_url: Kokoro FastAPI server URL
            voice: Default voice to use
            format: Output audio format (ogg, mp3, wav, etc.)
        """
        try:
            import requests
        except ImportError:
            raise ImportError("requests not installed. Run: pip install requests")

        self.base_url = base_url
        self.voice = voice
        self.format = format
        self.session = requests.Session()

    def synthesize(self, text: str, output_file: str, **kwargs) -> None:
        """
        Synthesize text to audio file using Kokoro

        Args:
            text: Text to synthesize
            output_file: Path to save audio
            **kwargs: Override default voice, format, etc.
        """
        voice = kwargs.get("voice", self.voice)
        format = kwargs.get("format", self.format)

        response = self.session.post(
            f"{self.base_url}/audio/speech",
            json={
                "model": "kokoro",
                "input": text,
                "voice": voice,
                "response_format": format
            }
        )
        response.raise_for_status()

        with open(output_file, "wb") as f:
            f.write(response.content)

    async def synthesize_stream(self, text: str, **kwargs) -> AsyncGenerator[bytes, None]:
        """
        Synthesize text to audio stream (Kokoro supports streaming)

        Args:
            text: Text to synthesize
            **kwargs: Override defaults

        Yields:
            Audio data chunks
        """
        voice = kwargs.get("voice", self.voice)

        response = self.session.post(
            f"{self.base_url}/audio/speech",
            json={
                "model": "kokoro",
                "input": text,
                "voice": voice,
                "response_format": "pcm"  # PCM for streaming
            },
            stream=True
        )
        response.raise_for_status()

        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                yield chunk

    def get_voices(self) -> List[str]:
        """
        Get list of available Kokoro voices

        Returns:
            List of voice names
        """
        response = self.session.get(f"{self.base_url}/audio/voices")
        response.raise_for_status()
        data = response.json()
        return data.get("voices", [])


class Qwen3TTS(TTSProvider):
    """Qwen3 TTS provider (placeholder - implement when model available)"""

    def __init__(self, model_path: str = None, device: str = "cpu",
                 voice: str = "default", format: str = "wav", **kwargs):
        """
        Initialize Qwen3 TTS

        Args:
            model_path: Path to Qwen3 TTS model
            device: Device to use (cpu, cuda)
            voice: Default voice
            format: Output format
        """
        self.model_path = model_path
        self.device = device
        self.voice = voice
        self.format = format

        # TODO: Initialize Qwen3 model when available
        raise NotImplementedError("Qwen3 TTS implementation pending model release")

    def synthesize(self, text: str, output_file: str, **kwargs) -> None:
        """Synthesize text using Qwen3 (placeholder)"""
        # TODO: Implement when Qwen3 TTS model is available
        raise NotImplementedError("Qwen3 TTS implementation pending model release")

    async def synthesize_stream(self, text: str, **kwargs) -> AsyncGenerator[bytes, None]:
        """Stream synthesis using Qwen3 (placeholder)"""
        raise NotImplementedError("Qwen3 TTS implementation pending model release")

    def get_voices(self) -> List[str]:
        """Get Qwen3 voices (placeholder)"""
        raise NotImplementedError("Qwen3 TTS implementation pending model release")


class OpenAITTS(TTSProvider):
    """OpenAI TTS API provider"""

    def __init__(self, api_key: str, model: str = "tts-1",
                 voice: str = "alloy", format: str = "mp3", **kwargs):
        """
        Initialize OpenAI TTS

        Args:
            api_key: OpenAI API key
            model: TTS model
            voice: Voice to use
            format: Output format
        """
        try:
            import openai
        except ImportError:
            raise ImportError("openai not installed. Run: pip install openai")

        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.voice = voice
        self.format = format

    def synthesize(self, text: str, output_file: str, **kwargs) -> None:
        """
        Synthesize text using OpenAI TTS API

        Args:
            text: Text to synthesize
            output_file: Path to save audio
            **kwargs: Override defaults
        """
        voice = kwargs.get("voice", self.voice)
        model = kwargs.get("model", self.model)
        response_format = kwargs.get("format", self.format)

        response = self.client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            response_format=response_format
        )

        response.stream_to_file(output_file)

    async def synthesize_stream(self, text: str, **kwargs) -> AsyncGenerator[bytes, None]:
        """Stream synthesis using OpenAI TTS"""
        voice = kwargs.get("voice", self.voice)
        model = kwargs.get("model", self.model)
        response_format = kwargs.get("format", self.format)

        response = self.client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            response_format=response_format
        )

        for chunk in response.iter_bytes(chunk_size=4096):
            if chunk:
                yield chunk

    def get_voices(self) -> List[str]:
        """
        Get OpenAI TTS voices

        Returns:
            List of available voices
        """
        return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]


class ElevenLabsTTS(TTSProvider):
    """ElevenLabs TTS API provider"""

    def __init__(self, api_key: str, voice_id: str = "default",
                 model: str = "eleven_multilingual_v2",
                 format: str = "mp3", **kwargs):
        """
        Initialize ElevenLabs TTS

        Args:
            api_key: ElevenLabs API key
            voice_id: Voice ID
            model: TTS model
            format: Output format
        """
        try:
            import requests
        except ImportError:
            raise ImportError("requests not installed. Run: pip install requests")

        self.api_key = api_key
        self.voice_id = voice_id
        self.model = model
        self.format = format
        self.session = requests.Session()

    def synthesize(self, text: str, output_file: str, **kwargs) -> None:
        """
        Synthesize text using ElevenLabs API

        Args:
            text: Text to synthesize
            output_file: Path to save audio
            **kwargs: Override defaults
        """
        voice_id = kwargs.get("voice_id", self.voice_id)

        response = self.session.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            },
            json={
                "text": text,
                "model_id": self.model,
                "output_format": self.format
            }
        )
        response.raise_for_status()

        with open(output_file, "wb") as f:
            f.write(response.content)

    async def synthesize_stream(self, text: str, **kwargs) -> AsyncGenerator[bytes, None]:
        """Stream synthesis using ElevenLabs (not supported in free tier)"""
        raise NotImplementedError("ElevenLabs streaming requires paid tier")

    def get_voices(self) -> List[str]:
        """
        Get ElevenLabs voices

        Returns:
            List of voice IDs
        """
        response = self.session.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": self.api_key}
        )
        response.raise_for_status()
        data = response.json()
        return [voice["voice_id"] for voice in data.get("voices", [])]


# Register providers
ProviderFactory.register_tts("kokoro", KokoroTTS)
ProviderFactory.register_tts("qwen3", Qwen3TTS)
ProviderFactory.register_tts("openai", OpenAITTS)
ProviderFactory.register_tts("elevenlabs", ElevenLabsTTS)


def quick_synthesize(text: str, output_file: str,
                   base_url: str = "http://localhost:8880/v1") -> None:
    """
    Quick synthesize helper (uses Kokoro by default)

    Args:
        text: Text to synthesize
        output_file: Path to save audio
        base_url: Kokoro server URL
    """
    tts = KokoroTTS(base_url=base_url)
    tts.synthesize(text, output_file)
