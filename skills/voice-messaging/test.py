#!/usr/bin/env python3
"""
Quick test for Voice Messaging Skill
Tests STT and TTS setup
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.voice_handler import VoiceHandler


def main():
    print("🎤 Voice Messaging Skill - Quick Test")
    print("")

    # Check config file
    config_path = os.path.join(os.path.dirname(__file__), 'config.toml')

    if not os.path.exists(config_path):
        print("⚠ config.toml not found")
        print("  Create config.toml first, or edit the example")
        return 1

    # Try to create handler
    try:
        import toml
        with open(config_path, 'r') as f:
            config = toml.load(f)
        print(f"✓ Config loaded")
        print(f"  STT: {config['stt']['provider']}")
        print(f"  TTS: {config['tts']['provider']}")
    except ImportError:
        print("⚠ toml not installed. Run: pip install tomli")
        return 1
    except Exception as e:
        print(f"⚠ Config error: {e}")
        return 1

    # Create handler
    try:
        handler = VoiceHandler.from_config(config_path)
        print("✓ Handler created")
    except Exception as e:
        print(f"⚠ Handler creation failed: {e}")
        print("  This is OK if Kokoro TTS is not running")
        print("  Start Kokoro: docker run --gpus all -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-gpu:latest")
        return 1

    # Test connections
    print("")
    print("Testing connections...")

    results = handler.test_connection()
    print(f"STT: {'✓' if results['stt'] else '✗'}")
    print(f"TTS: {'✓' if results['tts'] else '✗'}")

    if not results['stt']:
        print("")
        print("STT issues:")
        print("  - Make sure faster-whisper is installed: pip install faster-whisper")
        print("  - Make sure model can download (check internet)")

    if not results['tts']:
        print("")
        print("TTS issues:")
        print("  - Make sure Kokoro TTS is running on port 8880")
        print("  - Check Docker: docker ps | grep kokoro")

    # Test voices
    if results['tts']:
        print("")
        print("Available TTS voices:")
        try:
            voices = handler.get_voices()
            if voices:
                for voice in voices[:5]:  # Show first 5
                    print(f"  - {voice}")
                if len(voices) > 5:
                    print(f"  ... and {len(voices) - 5} more")
            else:
                print("  No voices found")
        except Exception as e:
            print(f"  Could not fetch voices: {e}")

    # Test default behaviors
    print("")
    print("Testing default behaviors...")
    defaults = handler.get_default_behavior_summary()
    print(f"Include transcription on voice response: {defaults['include_transcription_on_voice_response']}")
    print(f"Send voice to text message: {defaults['voice_response_to_text_message']}")

    if defaults['include_transcription_on_voice_response']:
        print("  ✓ Voice messages will include transcription")
    else:
        print("  ⚠ Voice messages will NOT include transcription")

    if not defaults['voice_response_to_text_message']:
        print("  ✓ Text messages will NOT receive voice responses")
    else:
        print("  ⚠ Text messages WILL receive voice responses")

    print("")
    print("✓ Test complete!")

    if results['stt'] and results['tts']:
        print("")
        print("🎉 Everything is working!")
        print("  Send a voice message from Telegram/Discord to test.")
        return 0
    else:
        print("")
        print("⚠ Some tests failed. Check the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
