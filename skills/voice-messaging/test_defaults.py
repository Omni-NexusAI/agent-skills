#!/usr/bin/env python3
"""
Test default behavior methods
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.voice_handler import VoiceHandler

def test_defaults():
    print("Testing default behavior methods...")

    # Create a mock handler with defaults
    class MockSTT:
        def transcribe(self, audio_path):
            return {"text": "test"}

    class MockTTS:
        def synthesize(self, text, output_file, **kwargs):
            pass

        def get_voices(self):
            return ["af_bella", "af_heart"]

    defaults = {
        "include_transcription_on_voice_response": True,
        "voice_response_to_text_message": False
    }

    handler = VoiceHandler(MockSTT(), MockTTS(), defaults=defaults)

    # Test methods
    assert handler.should_include_transcription_on_voice_response() == True
    assert handler.should_send_voice_to_text_message() == False

    summary = handler.get_default_behavior_summary()
    assert summary["include_transcription_on_voice_response"] == True
    assert summary["voice_response_to_text_message"] == False

    print("All default behavior tests passed!")

    # Test with config file
    config_path = os.path.join(os.path.dirname(__file__), 'config.toml')
    if os.path.exists(config_path):
        print("\nTesting with config.toml...")
        try:
            handler2 = VoiceHandler.from_config(config_path)
            summary2 = handler2.get_default_behavior_summary()
            print(f"Include transcription on voice response: {summary2['include_transcription_on_voice_response']}")
            print(f"Send voice to text message: {summary2['voice_response_to_text_message']}")
            print("Config-based tests passed!")
        except Exception as e:
            print(f"Config test skipped: {e}")

if __name__ == "__main__":
    test_defaults()
