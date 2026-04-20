"""
STT (Speech-to-Text) provider implementations
"""

import os
import asyncio
from typing import AsyncGenerator

from .providers import STTProvider, ProviderFactory


class WhisperSTT(STTProvider):
    """OpenAI Whisper (original) STT provider - Local, works reliably on Windows"""

    def __init__(self, model: str = "tiny", device: str = None, **kwargs):
        """
        Initialize original Whisper STT

        Args:
            model: Model size (tiny, base, small, medium, large)
            device: Device to use (None for auto, 'cuda', 'cpu')
        """
        # Fix Windows encoding and OpenMP issues
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

        try:
            import whisper
        except ImportError:
            raise ImportError("whisper not installed. Run: pip install openai-whisper")

        self.model_name = model
        # Only pass device if specified, otherwise let whisper auto-detect
        if device:
            self.model = whisper.load_model(model, device=device)
        else:
            self.model = whisper.load_model(model)

    def transcribe(self, audio_path: str) -> dict:
        """
        Transcribe audio file to text

        Args:
            audio_path: Path to audio file

        Returns:
            dict with transcription results
        """
        result = self.model.transcribe(audio_path)

        return {
            "text": result["text"].strip(),
            "language": result.get("language", "en"),
            "language_probability": 1.0,
            "duration": 0  # Not easily available from whisper
        }

    async def transcribe_stream(self, audio_stream) -> AsyncGenerator[dict, None]:
        """
        Transcribe streaming audio (placeholder for future)
        """
        raise NotImplementedError("Streaming not yet implemented for whisper")


class FasterWhisperSTT(STTProvider):
    """faster-whisper (CTranslate2) STT provider"""

    def __init__(self, model: str = "base", device: str = "cpu",
                 compute_type: str = "int8", **kwargs):
        """
        Initialize faster-whisper STT

        Args:
            model: Model size (tiny, base, small, medium, large-v3)
            device: Device to use (cpu, cuda)
            compute_type: Compute type (int8, float16, float32)
        """
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            raise ImportError("faster-whisper not installed. Run: pip install faster-whisper")

        self.model = WhisperModel(model, device=device, compute_type=compute_type, **kwargs)

    def transcribe(self, audio_path: str) -> dict:
        """
        Transcribe audio file to text

        Args:
            audio_path: Path to audio file

        Returns:
            dict with transcription results
        """
        segments, info = self.model.transcribe(audio_path)

        # Combine all segments
        text = " ".join([segment.text for segment in segments])
        duration = info.duration

        return {
            "text": text.strip(),
            "language": info.language,
            "language_probability": info.language_probability,
            "duration": duration
        }

    async def transcribe_stream(self, audio_stream) -> AsyncGenerator[dict, None]:
        """
        Transcribe streaming audio (placeholder for future)

        For full streaming, use WhisperLive or similar
        """
        # TODO: Implement streaming when needed
        raise NotImplementedError("Streaming not yet implemented for faster-whisper")


class OpenAIWhisperSTT(STTProvider):
    """OpenAI Whisper API STT provider"""

    def __init__(self, api_key: str, model: str = "whisper-1", **kwargs):
        """
        Initialize OpenAI Whisper STT

        Args:
            api_key: OpenAI API key
            model: Whisper model to use
        """
        try:
            import openai
        except ImportError:
            raise ImportError("openai not installed. Run: pip install openai")

        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def transcribe(self, audio_path: str) -> dict:
        """
        Transcribe audio file using OpenAI Whisper API

        Args:
            audio_path: Path to audio file

        Returns:
            dict with transcription results
        """
        with open(audio_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file
            )

        return {
            "text": transcript.text,
            "language": "en",  # OpenAI typically detects
            "language_probability": 1.0,
            "duration": transcript.duration if hasattr(transcript, 'duration') else 0
        }

    async def transcribe_stream(self, audio_stream) -> AsyncGenerator[dict, None]:
        """Streaming not supported by OpenAI Whisper API"""
        raise NotImplementedError("OpenAI Whisper API doesn't support streaming")


class GoogleCloudSTT(STTProvider):
    """Google Cloud Speech-to-Text provider"""

    def __init__(self, api_key: str, language: str = "en-US", **kwargs):
        """
        Initialize Google Cloud STT

        Args:
            api_key: Google Cloud API key
            language: Language code
        """
        try:
            from google.cloud import speech
        except ImportError:
            raise ImportError("google-cloud-speech not installed. Run: pip install google-cloud-speech")

        self.client = speech.SpeechClient()
        self.language = language

    def transcribe(self, audio_path: str) -> dict:
        """
        Transcribe audio file using Google Cloud Speech-to-Text

        Args:
            audio_path: Path to audio file

        Returns:
            dict with transcription results
        """
        with open(audio_path, "rb") as audio_file:
            audio_content = audio_file.read()

        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            language_code=self.language,
            enable_automatic_punctuation=True
        )

        response = self.client.recognize(config=config, audio=audio)

        results = []
        for result in response.results:
            results.append(result.alternatives[0].transcript)

        return {
            "text": " ".join(results),
            "language": self.language,
            "language_probability": 1.0,
            "duration": sum(result.alternatives[0].words[-1].end_time.total_seconds()
                         for result in response.results if result.alternatives[0].words)
        }

    async def transcribe_stream(self, audio_stream) -> AsyncGenerator[dict, None]:
        """Streaming implementation for Google Cloud STT"""
        # TODO: Implement streaming when needed
        raise NotImplementedError("Streaming not yet implemented")


# Register providers
ProviderFactory.register_stt("whisper", WhisperSTT)
ProviderFactory.register_stt("faster-whisper", FasterWhisperSTT)
ProviderFactory.register_stt("openai", OpenAIWhisperSTT)
ProviderFactory.register_stt("google", GoogleCloudSTT)


def quick_transcribe(audio_path: str, model: str = "base", device: str = "cpu") -> str:
    """
    Quick transcribe helper (uses faster-whisper by default)

    Args:
        audio_path: Path to audio file
        model: Model size
        device: Device to use

    Returns:
        Transcribed text
    """
    stt = FasterWhisperSTT(model=model, device=device)
    result = stt.transcribe(audio_path)
    return result["text"]
