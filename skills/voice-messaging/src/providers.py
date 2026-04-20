"""
Abstract provider interfaces for STT and TTS.
Allows easy swapping between different providers.
"""

from abc import ABC, abstractmethod
from typing import List, AsyncGenerator


class STTProvider(ABC):
    """Abstract interface for speech-to-text providers"""

    @abstractmethod
    def transcribe(self, audio_path: str) -> dict:
        """
        Transcribe audio file to text

        Args:
            audio_path: Path to audio file

        Returns:
            dict with keys:
                - text: str - Transcribed text
                - language: str - Detected language
                - duration: float - Audio duration in seconds
        """
        pass

    @abstractmethod
    async def transcribe_stream(self, audio_stream) -> AsyncGenerator[dict, None]:
        """
        Transcribe streaming audio (for future realtime support)

        Args:
            audio_stream: Audio data stream

        Yields:
            dict with partial transcription results
        """
        pass


class TTSProvider(ABC):
    """Abstract interface for text-to-speech providers"""

    @abstractmethod
    def synthesize(self, text: str, output_file: str, **kwargs) -> None:
        """
        Synthesize text to audio file

        Args:
            text: Text to synthesize
            output_file: Path to save audio
            **kwargs: Provider-specific options (voice, format, speed, etc.)
        """
        pass

    @abstractmethod
    async def synthesize_stream(self, text: str, **kwargs) -> AsyncGenerator[bytes, None]:
        """
        Synthesize text to audio stream (for future realtime support)

        Args:
            text: Text to synthesize
            **kwargs: Provider-specific options

        Yields:
            Audio data chunks
        """
        pass

    @abstractmethod
    def get_voices(self) -> List[str]:
        """
        Get list of available voices

        Returns:
            List of voice names
        """
        pass


class ProviderFactory:
    """Factory for creating provider instances from config"""

    _stt_providers = {}
    _tts_providers = {}

    @classmethod
    def register_stt(cls, name: str, provider_class):
        """Register an STT provider"""
        cls._stt_providers[name] = provider_class

    @classmethod
    def register_tts(cls, name: str, provider_class):
        """Register a TTS provider"""
        cls._tts_providers[name] = provider_class

    @classmethod
    def create_stt(cls, provider_name: str, config: dict) -> STTProvider:
        """Create STT provider instance from config"""
        if provider_name not in cls._stt_providers:
            raise ValueError(f"Unknown STT provider: {provider_name}")
        provider_class = cls._stt_providers[provider_name]
        return provider_class(**config)

    @classmethod
    def create_tts(cls, provider_name: str, config: dict) -> TTSProvider:
        """Create TTS provider instance from config"""
        if provider_name not in cls._tts_providers:
            raise ValueError(f"Unknown TTS provider: {provider_name}")
        provider_class = cls._tts_providers[provider_name]
        return provider_class(**config)
