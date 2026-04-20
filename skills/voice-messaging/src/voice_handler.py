"""
Main voice handler for OpenClaw integration
Handles voice message processing with modular STT/TTS providers
"""

import os
import re
import tempfile
import logging
from pathlib import Path
from typing import Optional

from .providers import ProviderFactory
from .stt_providers import quick_transcribe
from .tts_providers import quick_synthesize


def _expand_env_vars(config: dict) -> dict:
    """Expand environment variables in config values (e.g., ${OPENAI_API_KEY})"""
    env_pattern = re.compile(r'\$\{([^}]+)\}')
    
    def expand_value(value):
        if isinstance(value, str):
            match = env_pattern.search(value)
            if match:
                env_var = match.group(1)
                env_value = os.environ.get(env_var, "")
                return env_pattern.sub(env_value, value)
            return value
        elif isinstance(value, dict):
            return {k: expand_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [expand_value(v) for v in value]
        return value
    
    return expand_value(config)


class VoiceHandler:
    """
    Main handler for voice messaging

    Supports:
    - Multiple STT providers (faster-whisper, OpenAI, Google)
    - Multiple TTS providers (Kokoro, Qwen3, OpenAI, ElevenLabs)
    - Automatic audio format conversion
    - Platform-specific output (Telegram, Discord)
    """

    def __init__(self, stt_provider, tts_provider, audio_processor=None, defaults=None):
        """
        Initialize voice handler

        Args:
            stt_provider: STT provider instance
            tts_provider: TTS provider instance
            audio_processor: Optional audio processor for format conversion
            defaults: Dict of default behavior settings
        """
        self.stt = stt_provider
        self.tts = tts_provider
        self.processor = audio_processor
        self.defaults = defaults or {}
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_config(cls, config_path: str, audio_processor=None):
        """
        Create VoiceHandler from config file

        Args:
            config_path: Path to config.toml
            audio_processor: Optional AudioProcessor instance

        Returns:
            VoiceHandler instance
        """
        try:
            import toml
        except ImportError:
            raise ImportError("toml not installed. Run: pip install tomli")

        with open(config_path, 'r') as f:
            config = toml.load(f)
        
        # Expand environment variables in config
        config = _expand_env_vars(config)

        # Get STT config
        stt_config = config["stt"].copy()  # Make a copy to avoid modifying original
        stt_provider_name = stt_config.pop("provider")

        # Create STT provider
        stt = ProviderFactory.create_stt(stt_provider_name, stt_config)

        # Get TTS config
        tts_config = config["tts"].copy()  # Make a copy to avoid modifying original
        tts_provider_name = tts_config.pop("provider")

        # Create TTS provider
        tts = ProviderFactory.create_tts(tts_provider_name, tts_config)

        # Get defaults config
        defaults = config.get("defaults", {})

        return cls(stt, tts, audio_processor, defaults)

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe audio file to text

        Args:
            audio_path: Path to audio file

        Returns:
            Transcribed text
        """
        try:
            result = self.stt.transcribe(audio_path)
            self.logger.info(f"Transcribed: {result['text'][:50]}...")
            return result["text"]
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            raise

    def synthesize(self, text: str, output_file: str,
                 voice: Optional[str] = None, format: Optional[str] = None) -> None:
        """
        Synthesize text to audio file

        Args:
            text: Text to synthesize
            output_file: Path to save audio
            voice: Override default voice
            format: Override default format
        """
        try:
            kwargs = {}
            if voice is not None:
                kwargs["voice"] = voice
            if format is not None:
                kwargs["format"] = format

            self.tts.synthesize(text, output_file, **kwargs)
            self.logger.info(f"Synthesized: {text[:50]}... -> {output_file}")
        except Exception as e:
            self.logger.error(f"Synthesis failed: {e}")
            raise

    def get_voices(self) -> list:
        """
        Get list of available TTS voices

        Returns:
            List of voice names
        """
        try:
            return self.tts.get_voices()
        except Exception as e:
            self.logger.error(f"Failed to get voices: {e}")
            return []

    def process_voice_message(self, input_audio: str,
                          output_audio: str,
                          platform: str = "telegram") -> str:
        """
        Process voice message: transcribe -> (you process) -> synthesize

        Args:
            input_audio: Path to input voice message
            output_audio: Path to save response
            platform: Platform (telegram, discord) - determines output format

        Returns:
            Transcribed text
        """
        # Step 1: Transcribe
        text = self.transcribe(input_audio)
        return text  # You'll process this text and call synthesize()

    def test_connection(self) -> dict:
        """
        Test STT and TTS connections

        Returns:
            dict with test results
        """
        results = {"stt": False, "tts": False}

        # Test STT
        try:
            # Create a test audio (1 second of silence)
            test_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            test_audio.close()

            import wave
            with wave.open(test_audio.name, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(16000)
                wav_file.writeframes(b'\x00\x00' * 16000)

            self.stt.transcribe(test_audio.name)
            results["stt"] = True

            os.unlink(test_audio.name)
        except Exception as e:
            self.logger.error(f"STT test failed: {e}")

        # Test TTS
        try:
            test_output = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
            test_output.close()

            self.tts.synthesize("Test", test_output.name)
            results["tts"] = True

            os.unlink(test_output.name)
        except Exception as e:
            self.logger.error(f"TTS test failed: {e}")

        return results

    def should_include_transcription_on_voice_response(self) -> bool:
        """
        Check if transcription should be included when responding to voice messages.

        Default behavior: Always include transcription when responding to voice.
        Only omit if user explicitly requests voice-only response.

        Returns:
            True if transcription should be included, False otherwise
        """
        return self.defaults.get("include_transcription_on_voice_response", True)

    def should_send_voice_to_text_message(self) -> bool:
        """
        Check if voice should be sent when responding to text messages.

        Default behavior: Do NOT send voice to text messages.
        Only send voice if user explicitly asks for it.

        Returns:
            True if voice should be sent, False otherwise
        """
        return self.defaults.get("voice_response_to_text_message", False)

    def get_default_behavior_summary(self) -> dict:
        """
        Get a summary of the default behaviors.

        Returns:
            Dict with default behavior settings
        """
        return {
            "include_transcription_on_voice_response": self.should_include_transcription_on_voice_response(),
            "voice_response_to_text_message": self.should_send_voice_to_text_message()
        }


def quick_test():
    """
    Quick test function for setup verification

    Usage:
        from voice_messaging.src.voice_handler import quick_test
        quick_test()
    """
    print("Testing Voice Messaging Skill...")

    # Test from default config
    handler = VoiceHandler.from_config("config.toml")

    # Test connections
    print("\nTesting connections...")
    results = handler.test_connection()
    print(f"STT: {'✓' if results['stt'] else '✗'}")
    print(f"TTS: {'✓' if results['tts'] else '✗'}")

    # Test voices
    print("\nAvailable TTS voices:")
    voices = handler.get_voices()
    for voice in voices[:5]:  # Show first 5
        print(f"  - {voice}")
    if len(voices) > 5:
        print(f"  ... and {len(voices) - 5} more")

    print("\n✓ Voice Messaging Skill setup complete!")
