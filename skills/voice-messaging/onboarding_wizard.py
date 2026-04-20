#!/usr/bin/env python3
"""
Voice Messaging Skill - Onboarding Wizard

Guided setup for integrating voice messaging into your agent framework.
"""

import os
import sys
import json
import shutil
from pathlib import Path

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    print(f"""
{Colors.CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗
║        Voice Messaging Skill - Onboarding Wizard             ║
╚══════════════════════════════════════════════════════════════╝{Colors.RESET}

This wizard will help you set up voice messaging for your agent.
It will detect your environment and generate the right configuration.
""")

def print_step(step_num, title):
    print(f"\n{Colors.BLUE}{Colors.BOLD}[Step {step_num}] {title}{Colors.RESET}\n")

def print_info(msg):
    print(f"{Colors.CYAN}ℹ{Colors.RESET} {msg}")

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")

def ask_question(question, options=None, default=None):
    """Ask a question and get user input."""
    if options:
        print(f"{Colors.BOLD}{question}{Colors.RESET}")
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt}")
        if default:
            print(f"\n  Default: {default}")
        while True:
            try:
                choice = input(f"\n  Enter choice [1-{len(options)}]: ").strip()
                if not choice and default:
                    return default
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return options[idx]
                print(f"{Colors.RED}Invalid choice. Please try again.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Please enter a number.{Colors.RESET}")
    else:
        prompt = f"\n  {question}"
        if default:
            prompt += f" [{default}]"
        prompt += ": "
        answer = input(prompt).strip()
        return answer if answer else default

def detect_environment():
    """Auto-detect available tools and providers."""
    detected = {
        'whisper': False,
        'faster_whisper': False,
        'kokoro': False,
        'ffmpeg': False,
        'openai_key': False,
    }
    
    # Check for whisper
    try:
        import whisper
        detected['whisper'] = True
    except ImportError:
        pass
    
    # Check for faster-whisper
    try:
        import faster_whisper
        detected['faster_whisper'] = True
    except ImportError:
        pass
    
    # Check for Kokoro (via HTTP)
    try:
        import requests
        resp = requests.get('http://localhost:8880/v1/models', timeout=2)
        if resp.status_code == 200:
            detected['kokoro'] = True
    except:
        pass
    
    # Check for ffmpeg
    try:
        import subprocess
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        detected['ffmpeg'] = True
    except:
        pass
    
    # Check for OpenAI key
    if os.environ.get('OPENAI_API_KEY'):
        detected['openai_key'] = True
    
    return detected

def print_detected(detected):
    """Print detected capabilities."""
    print_info("Auto-detected capabilities:")
    
    items = [
        ('whisper', 'OpenAI Whisper (local)', 'pip install openai-whisper'),
        ('faster_whisper', 'Faster-Whisper (local)', 'pip install faster-whisper'),
        ('kokoro', 'Kokoro TTS server', 'Run Kokoro Docker container'),
        ('ffmpeg', 'FFmpeg', 'Install from https://ffmpeg.org'),
        ('openai_key', 'OpenAI API key', 'Set OPENAI_API_KEY env var'),
    ]
    
    for key, name, install_cmd in items:
        status = f"{Colors.GREEN}✓ Found{Colors.RESET}" if detected[key] else f"{Colors.YELLOW}✗ Not found{Colors.RESET}"
        print(f"    {name}: {status}")
        if not detected[key]:
            print(f"      Install: {install_cmd}")

def step1_framework():
    """Ask about the agent framework."""
    print_step(1, "Agent Framework")
    
    frameworks = [
        "OpenClaw",
        "LangChain",
        "Agent Zero",
        "CrewAI",
        "Custom/Generic Python",
    ]
    
    return ask_question("Which agent framework are you using?", frameworks, "OpenClaw")

def step2_message_handling(framework):
    """Ask about message handling."""
    print_step(2, "Message Handling")
    
    print_info(f"For {framework}, how are incoming messages handled?")
    
    if framework == "OpenClaw":
        hooks = [
            "Telegram channel (automatic)",
            "Discord channel (automatic)",
            "WhatsApp channel (automatic)",
            "Custom webhook",
        ]
    else:
        hooks = [
            "Webhook/HTTP endpoint",
            "Message queue (Redis, RabbitMQ)",
            "Direct API calls",
            "Not sure yet",
        ]
    
    return ask_question("How does your agent receive messages?", hooks, hooks[0])

def step3_stt_provider(detected):
    """Configure STT provider."""
    print_step(3, "Speech-to-Text (STT) Provider")
    
    # Build options based on what's detected
    options = []
    if detected['whisper']:
        options.append("Whisper (local) - Detected ✓")
    else:
        options.append("Whisper (local) - Will install")
    
    if detected['faster_whisper']:
        options.append("Faster-Whisper (local) - Detected ✓")
    else:
        options.append("Faster-Whisper (local) - Will install")
    
    if detected['openai_key']:
        options.append("OpenAI Whisper API - Key detected ✓")
    else:
        options.append("OpenAI Whisper API - Cloud (requires API key)")
    
    options.append("Google Cloud Speech (requires API key)")
    
    choice = ask_question("Which STT provider do you want to use?", options, options[0])
    
    # Extract provider name
    if "Whisper (local)" in choice and "Faster" not in choice:
        return "whisper"
    elif "Faster-Whisper" in choice:
        return "faster-whisper"
    elif "OpenAI" in choice:
        return "openai"
    else:
        return "google"

def step4_tts_provider(detected):
    """Configure TTS provider."""
    print_step(4, "Text-to-Speech (TTS) Provider")
    
    options = []
    
    if detected['kokoro']:
        options.append("Kokoro (local) - Detected ✓")
    else:
        options.append("Kokoro (local) - Requires Docker")
    
    if detected['openai_key']:
        options.append("OpenAI TTS - Key detected ✓")
    else:
        options.append("OpenAI TTS - Cloud (requires API key)")
    
    options.append("ElevenLabs (cloud, premium quality)")
    options.append("Qwen3 TTS (local, requires Docker)")
    
    choice = ask_question("Which TTS provider do you want to use?", options, options[0])
    
    if "Kokoro" in choice:
        return "kokoro"
    elif "OpenAI TTS" in choice:
        return "openai"
    elif "ElevenLabs" in choice:
        return "elevenlabs"
    else:
        return "qwen3"

def step5_voice_settings(tts_provider):
    """Configure voice settings."""
    print_step(5, "Voice Settings")
    
    # Voice options based on provider
    voice_options = {
        'kokoro': ['am_michael', 'af_bella', 'af_nova', 'af_alloy', 'am_onyx'],
        'openai': ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'],
        'elevenlabs': ['custom (you provide voice_id)'],
        'qwen3': ['default'],
    }
    
    voices = voice_options.get(tts_provider, ['default'])
    voice = ask_question(f"Select a voice for {tts_provider}:", voices, voices[0])
    
    # Format options
    formats = ['opus', 'mp3', 'wav', 'flac']
    audio_format = ask_question("Output audio format:", formats, 'opus')
    
    return voice, audio_format

def generate_config(framework, message_handler, stt_provider, tts_provider, voice, audio_format, detected):
    """Generate the config.toml content."""
    
    config = f'''# Voice Messaging Configuration
# Generated by onboarding wizard for {framework}
# ==============================

[defaults]
auto_process_voice = true
include_transcription_on_voice_response = true
voice_response_to_text_message = false

# ==============================================================================
# STT (Speech-to-Text) Configuration
# ==============================================================================

[stt]
provider = "{stt_provider}"
'''
    
    if stt_provider == "whisper":
        config += '''
# Whisper (Local, Original OpenAI Whisper)
model = "base"              # tiny, base, small, medium, large
device = ""                 # empty for auto, or 'cuda', 'cpu'
'''
    elif stt_provider == "faster-whisper":
        config += '''
# Faster-Whisper (Local, CTranslate2)
model = "base"              # tiny, base, small, medium, large-v3
device = "cpu"              # cpu, cuda
compute_type = "int8"       # int8, float16, float32
'''
    elif stt_provider == "openai":
        config += '''
# OpenAI Whisper API (Cloud)
model = "whisper-1"
api_key = "${OPENAI_API_KEY}"
'''
    elif stt_provider == "google":
        config += '''
# Google Cloud Speech-to-Text
api_key = "${GOOGLE_API_KEY}"
language = "en-US"
'''
    
    config += f'''
# ==============================================================================
# TTS (Text-to-Speech) Configuration
# ==============================================================================

[tts]
provider = "{tts_provider}"
'''
    
    if tts_provider == "kokoro":
        config += f'''
# Kokoro TTS (Local)
base_url = "http://localhost:8880/v1"
voice = "{voice}"
format = "{audio_format}"
speed = 1.0
'''
    elif tts_provider == "openai":
        config += f'''
# OpenAI TTS (Cloud)
api_key = "${{OPENAI_API_KEY}}"
model = "tts-1"
voice = "{voice}"
format = "{audio_format}"
'''
    elif tts_provider == "elevenlabs":
        config += '''
# ElevenLabs TTS (Cloud)
api_key = "${ELEVENLABS_API_KEY}"
voice_id = "YOUR_VOICE_ID"    # Get from https://elevenlabs.io
model = "eleven_multilingual_v2"
'''
    elif tts_provider == "qwen3":
        config += '''
# Qwen3 TTS (Local)
base_url = "http://localhost:8890"
voice = "default"
format = "wav"
'''
    
    config += '''
# ==============================================================================
# Audio Processing
# ==============================================================================

[audio]
temp_dir = ""              # Empty for system default

[platforms]
telegram_format = "ogg"
discord_format = "mp3"
'''
    
    return config

def generate_integration_code(framework, message_handler):
    """Generate framework-specific integration code."""
    
    if framework == "OpenClaw":
        return f'''# OpenClaw Integration
# Add to your agent's message handler

import os
import sys
sys.path.insert(0, os.path.expanduser('~/.openclaw/skills/agent-voice-messaging'))
from src.voice_handler import VoiceHandler

# Initialize handler
handler = VoiceHandler.from_config('config.toml')

# In your message handler:
async def handle_voice_message(audio_path: str) -> tuple:
    """
    Process incoming voice message.
    Returns (transcription, audio_response_path)
    """
    # 1. Transcribe user's voice
    text = handler.transcribe(audio_path)
    
    # 2. Generate your LLM response (your code here)
    response_text = await your_llm.generate(text)
    
    # 3. Synthesize response to voice
    output_path = '/tmp/voice_response.opus'
    handler.synthesize(response_text, output_path)
    
    return text, output_path
'''
    
    elif framework == "LangChain":
        return '''# LangChain Integration
# Add as a custom tool

from langchain.tools import Tool
from voice_handler import VoiceHandler

class VoiceMessagingTool(Tool):
    name = "voice_messaging"
    description = "Process voice messages and synthesize responses"
    
    def __init__(self, config_path: str):
        self.handler = VoiceHandler.from_config(config_path)
    
    def _run(self, audio_path: str) -> str:
        """Transcribe audio file."""
        return self.handler.transcribe(audio_path)
    
    def synthesize(self, text: str, output_path: str):
        """Convert text to speech."""
        self.handler.synthesize(text, output_path)

# Usage:
# voice_tool = VoiceMessagingTool("config.toml")
# transcription = voice_tool._run("user_voice.ogg")
'''
    
    elif framework == "Agent Zero":
        return '''# Agent Zero Integration
# Add to your agent's capabilities

from voice_handler import VoiceHandler

class VoiceCapability:
    def __init__(self, config_path: str = "config.toml"):
        self.handler = VoiceHandler.from_config(config_path)
    
    def process_voice(self, audio_path: str) -> str:
        """Transcribe voice message."""
        return self.handler.transcribe(audio_path)
    
    def speak(self, text: str, output_path: str = "response.opus"):
        """Synthesize speech from text."""
        self.handler.synthesize(text, output_path)
        return output_path
'''
    
    else:
        return '''# Generic Python Integration

from voice_handler import VoiceHandler

# Initialize
handler = VoiceHandler.from_config("config.toml")

# Transcribe
text = handler.transcribe("user_voice.ogg")
print(f"User said: {text}")

# Synthesize
handler.synthesize("Your response text", "response.opus")
'''

def run_wizard():
    """Run the onboarding wizard."""
    print_header()
    
    # Detect environment
    detected = detect_environment()
    print_detected(detected)
    
    # Ask questions
    framework = step1_framework()
    message_handler = step2_message_handling(framework)
    stt_provider = step3_stt_provider(detected)
    tts_provider = step4_tts_provider(detected)
    voice, audio_format = step5_voice_settings(tts_provider)
    
    # Generate files
    print_step(6, "Generating Configuration")
    
    config = generate_config(framework, message_handler, stt_provider, tts_provider, voice, audio_format, detected)
    integration = generate_integration_code(framework, message_handler)
    
    # Write files
    config_path = Path("config.toml")
    integration_path = Path(f"integration_{framework.lower().replace(' ', '_')}.py")
    
    with open(config_path, 'w') as f:
        f.write(config)
    print_success(f"Created {config_path}")
    
    with open(integration_path, 'w') as f:
        f.write(integration)
    print_success(f"Created {integration_path}")
    
    # Summary
    print(f"""
{Colors.GREEN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗
║                    Setup Complete!                           ║
╚══════════════════════════════════════════════════════════════╝{Colors.RESET}

{Colors.BOLD}Configuration:{Colors.RESET}
  Framework:     {framework}
  STT Provider:  {stt_provider}
  TTS Provider:  {tts_provider}
  Voice:         {voice}
  Audio Format:  {audio_format}

{Colors.BOLD}Generated Files:{Colors.RESET}
  - config.toml              (Main configuration)
  - {integration_path}  (Integration code)

{Colors.BOLD}Next Steps:{Colors.RESET}
  1. Install dependencies: pip install openai-whisper requests
  2. Start Kokoro TTS (if using local): docker run -d -p 8880:8880 kokoro-tts
  3. Add the integration code to your agent
  4. Test with: python -c "from voice_handler import VoiceHandler; print('OK')"

{Colors.CYAN}Need help? See SKILL.md for detailed documentation.{Colors.RESET}
""")

if __name__ == "__main__":
    run_wizard()
