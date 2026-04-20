"""
Voice Messaging Skill
Modular voice messaging for OpenClaw with swappable STT/TTS providers
"""

from .voice_handler import VoiceHandler, quick_test
from .stt_providers import quick_transcribe
from .tts_providers import quick_synthesize
from .audio_processor import AudioProcessor, check_ffmpeg

__all__ = [
    'VoiceHandler',
    'quick_test',
    'quick_transcribe',
    'quick_synthesize',
    'AudioProcessor',
    'check_ffmpeg',
]
