# 🎤 Agent Voice Messaging

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![STT](https://img.shields.io/badge/STT-Whisper%20%7C%20OpenAI%20%7C%20Google-orange.svg)](#supported-stt-providers)
[![TTS](https://img.shields.io/badge/TTS-Kokoro%20%7C%20Qwen3%20%7C%20OpenAI%20%7C%20ElevenLabs-purple.svg)](#supported-tts-providers)

**Modular voice messaging for agents** - Send voice messages through Telegram/Discord and receive voice responses with swappable local and cloud STT/TTS providers.

**Framework Support:** OpenClaw • LangChain • Agent Zero • Generic Agents

---

## 🎯 Default Behaviors

The agent-voice-messaging library uses smart defaults for voice messaging interactions:

### Default Behavior #1: Always Include AI Response Transcription

When a user sends a **voice message**, the agent ALWAYS responds with:
- ✅ **Voice audio file** (the AI response synthesized)
- ✅ **Text transcription** of the AI response

The transcription is included by default. Only send voice-only if the user explicitly requests it.

**Example workflow:**
```
User: Sends voice message → "What's the weather?"
Agent: Responds with:
  - Voice: "It's 72°F and sunny today!"
  - Text: "It's 72°F and sunny today!"
```

**When to omit transcription:**
- User explicitly says "voice-only" or "no text"
- User has a preference set for voice-only responses

---

### Default Behavior #2: Voice-Only on Text Messages (Unless Requested)

When a user sends a **text message**, the agent responds with **text only** by default.

Do NOT send voice output unless the user explicitly asks for it. This is the opposite of the previous behavior.

**Example workflow:**
```
User: Sends text → "What's the weather?"
Agent: Responds with:
  - Text: "It's 72°F and sunny today!"
  - Voice: (not sent)
```

**When to send voice:**
- User explicitly asks: "Can you tell me via voice?"
- User says: "speak it" or "say it out loud"
- User has a preference set for voice responses

---

### Summary of Default Behaviors

| User Input | Default Response | How to Override |
|------------|------------------|-----------------|
| **Voice message** | Voice + Text transcription | User requests "voice-only" |
| **Text message** | Text only | User asks for voice ("say it", "speak", etc.) |

---

### Configuration

These defaults can be configured in `config.toml`:

```toml
[defaults]
include_transcription_on_voice_response = true  # Always include transcription for voice responses
voice_response_to_text_message = false         # Don't send voice to text messages
```

**Note:** These defaults are designed for intuitive voice messaging. Users expect to see what was said, and voice responses to text messages can be jarring unless explicitly requested.

---

## 🎯 What This Library Does

Agent Voice Messaging enables seamless voice communication in your agent applications:

1. **Receive voice messages** from Telegram or Discord
2. **Transcribe to text** using your preferred STT provider
3. **Process the text** with your agent's normal workflow
4. **Generate voice responses** using your preferred TTS provider
5. **Send back audio** in the platform-appropriate format

All of this happens automatically - no additional code needed!

**Compatible with:**
- **OpenClaw** - Install as a skill
- **LangChain** - Use as a tool or callback
- **Agent Zero** - Integrate with agent workflows
- **Generic Agents** - Import as a Python module

---

## ✨ Key Features

✅ **Zero configuration voice messaging** - Just install and go
✅ **Swappable providers** - Change STT/TTS with a single config edit
✅ **Local-first architecture** - Privacy, no cloud APIs required
✅ **Automatic format conversion** - OGG, MP3, WAV, M4A, FLAC handled seamlessly
✅ **Platform-aware** - Telegram (OGG) and Discord (MP3) supported out-of-the-box
✅ **Docker-ready** - Pre-configured for local STT/TTS endpoints
✅ **GPU acceleration** - CUDA support for faster processing
✅ **Extensible design** - Easy to add new providers
✅ **Framework-agnostic** - Works with OpenClaw, LangChain, Agent Zero, and any Python agent

---

## 📦 Supported Providers

### STT (Speech-to-Text)

| Provider | Type | Performance | Privacy | Cost |
|----------|------|-------------|---------|------|
| **faster-whisper** | Local | 2-60x real-time | ✅ High | Free |
| **OpenAI Whisper** | Cloud | Fast | ⚠️ Medium | Pay-as-you-go |
| **Google Speech-to-Text** | Cloud | Fast | ⚠️ Medium | Pay-as-you-go |

### TTS (Text-to-Speech)

| Provider | Type | Quality | Voice Selection | Privacy | Cost |
|----------|------|---------|----------------|---------|------|
| **Kokoro** | Local | Production | 10+ voices | ✅ High | Free |
| **Qwen3** | Local | High | Customizable | ✅ High | Free |
| **OpenAI TTS** | Cloud | High | 6 voices | ⚠️ Medium | Pay-as-you-go |
| **ElevenLabs** | Cloud | Premium | 90+ voices | ⚠️ Medium | Subscription |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- FFmpeg (for audio conversion)
- Docker (for local STT/TTS endpoints, optional)

### Step 1: Install Dependencies

```bash
# Python packages
pip install faster-whisper requests pyav toml

# FFmpeg (required for audio conversion)
# Windows:
choco install ffmpeg

# macOS:
brew install ffmpeg

# Linux:
sudo apt install ffmpeg
```

### Step 2: Choose Your Setup

**Option A: Local-only (Recommended for privacy)**
- STT: faster-whisper
- TTS: Kokoro (via Docker)

**Option B: Cloud-based**
- STT: OpenAI Whisper
- TTS: OpenAI TTS or ElevenLabs

**Option C: Hybrid**
- STT: Local (faster-whisper)
- TTS: Cloud (ElevenLabs for premium voices)

### Step 3: Configure

Edit `config.toml` with your preferred providers:

```toml
[stt]
provider = "faster-whisper"  # faster-whisper, openai, google
model = "base"               # tiny, base, small, medium, large-v3
device = "cpu"               # cpu, cuda
compute_type = "int8"        # int8, float16, float32

[tts]
provider = "kokoro"          # kokoro, qwen3, openai, elevenlabs
base_url = "http://localhost:8880/v1"
voice = "af_bella"           # Default voice
format = "ogg"               # ogg, mp3, wav, opus, flac, m4a
speed = 1.0
```

### Step 4: Test Your Setup

```bash
# Navigate to library directory
cd agent-voice-messaging

# Test the setup
python -c "from src.voice_handler import quick_test; quick_test()"
```

### Step 5: Install in Your Framework

#### For OpenClaw
```bash
# Copy to OpenClaw skills directory
cp -r agent-voice-messaging ~/.openclaw/skills/

# Install
openclaw skills install ~/.openclaw/skills/agent-voice-messaging
```

#### For LangChain
```python
from langchain.agents import Tool
from voice_messaging.src.voice_handler import VoiceHandler

# Initialize voice handler
handler = VoiceHandler.from_config("config.toml")

# Create LangChain tool
voice_tool = Tool(
    name="Voice Messaging",
    func=lambda text: handler.synthesize(text, "response.ogg"),
    description="Convert text to voice and send back to user"
)
```

#### For Agent Zero
```python
from agent_zero import Agent
from voice_messaging.src.voice_handler import VoiceHandler

# Initialize voice handler
handler = VoiceHandler.from_config("config.toml")

# Use in agent workflow
def process_voice_message(audio_path: str) -> str:
    # Transcribe
    text = handler.transcribe(audio_path)
    # Process with your agent
    response = your_agent.process(text)
    # Synthesize response
    handler.synthesize(response, "response.ogg")
    return response
```

#### For Generic Python Agents
```python
from voice_messaging.src.voice_handler import VoiceHandler

# Initialize
handler = VoiceHandler.from_config("config.toml")

# Use in your agent code
text = handler.transcribe("user_voice.ogg")
response = your_agent.process(text)
handler.synthesize(response, "response.ogg")
```

### Step 6: Send a Voice Message!

That's it! Send a voice message in Telegram or Discord and receive a voice response.

---

## 🐳 Docker Setup for Local Providers

### Kokoro TTS (Local, Production Quality)

Kokoro provides excellent voice quality with low latency. Here's how to set it up:

#### Quick Start (Docker)

```bash
# Pull the image
docker pull ghcr.io/omni-nexusai/agent-zero-kokoro-worker:v0.9.8-custom-pre-hybrid-gpu

# Run the container
docker run -d \
  --name kokoro-tts \
  --gpus all \
  -p 8880:8880 \
  ghcr.io/omni-nexusai/agent-zero-kokoro-worker:v0.9.8-custom-pre-hybrid-gpu

# Verify it's running
curl http://localhost:8880/v1/health
```

#### Configuration

Update `config.toml`:

```toml
[tts]
provider = "kokoro"
base_url = "http://localhost:8880/v1"
voice = "af_bella"
format = "ogg"
speed = 1.0
```

#### Available Voices

```
af_bella, af_heart, af_sky, af_michael, am_michael, bm_george, bm_lewis, bf_emma, bf_isabella
```

#### Troubleshooting Kokoro

```bash
# Check logs
docker logs kokoro-tts

# Restart container
docker restart kokoro-tts

# Check port is accessible
curl http://localhost:8880/v1/health

# Without GPU (slower)
docker run -d \
  --name kokoro-tts \
  -p 8880:8880 \
  ghcr.io/omni-nexusai/agent-zero-kokoro-worker:v0.9.8-custom-pre-hybrid-gpu
```

### Qwen3 TTS (Local, Customizable)

Qwen3 offers high-quality TTS with customizable voices.

#### Setup

```bash
# Pull the image
docker pull qwen3-tts-openai-fastapi-qwen3-tts-gpu

# Run the container
docker run -d \
  --name qwen3-tts \
  --gpus all \
  -p 8890:8000 \
  qwen3-tts-openai-fastapi-qwen3-tts-gpu

# Verify it's running
curl http://localhost:8890/health
```

#### Configuration

Update `config.toml`:

```toml
[tts]
provider = "qwen3"
base_url = "http://localhost:8890"
voice = "default"
format = "wav"
speed = 1.0
```

---

## ☁️ Cloud Provider Setup

### OpenAI STT + TTS

```toml
[stt]
provider = "openai"
api_key = "${OPENAI_API_KEY}"
model = "whisper-1"

[tts]
provider = "openai"
api_key = "${OPENAI_API_KEY}"
model = "tts-1"
voice = "alloy"  # alloy, echo, fable, onyx, nova, shimmer
format = "mp3"
```

### ElevenLabs TTS (Premium Quality)

```toml
[tts]
provider = "elevenlabs"
api_key = "${ELEVENLABS_API_KEY}"
voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel (example)
model = "eleven_multilingual_v2"
format = "mp3"
```

Get your API key and voice ID from [elevenlabs.io](https://elevenlabs.io).

### Google Cloud STT

```toml
[stt]
provider = "google"
api_key = "${GOOGLE_API_KEY}"
language = "en-US"
```

---

## 🔧 Advanced Configuration

### STT Provider Options

#### faster-whisper

```toml
[stt]
provider = "faster-whisper"
model = "base"              # tiny, base, small, medium, large-v3
device = "cpu"              # cpu, cuda
compute_type = "int8"       # int8 (fastest), float16, float32 (best quality)
```

**Model Sizes:**
- `tiny`: 39 MB, fastest, lower accuracy
- `base`: 74 MB, good balance (recommended)
- `small`: 244 MB, better accuracy
- `medium`: 769 MB, high accuracy
- `large-v3`: 1550 MB, best accuracy

#### OpenAI Whisper

```toml
[stt]
provider = "openai"
api_key = "${OPENAI_API_KEY}"
model = "whisper-1"         # whisper-1 only
language = "en"             # Optional: auto-detect if omitted
```

#### Google Cloud Speech-to-Text

```toml
[stt]
provider = "google"
api_key = "${GOOGLE_API_KEY}"
language = "en-US"          # Language code
profanity_filter = false    # Optional
```

### TTS Provider Options

#### Kokoro

```toml
[tts]
provider = "kokoro"
base_url = "http://localhost:8880/v1"
voice = "af_bella"          # See available voices below
format = "ogg"              # ogg, mp3, wav, opus, flac, m4a, pcm
speed = 1.0                 # 0.5 to 2.0
```

#### Qwen3

```toml
[tts]
provider = "qwen3"
base_url = "http://localhost:8890"
voice = "default"
format = "wav"
speed = 1.0
```

#### OpenAI TTS

```toml
[tts]
provider = "openai"
api_key = "${OPENAI_API_KEY}"
model = "tts-1"             # tts-1, tts-1-hd (slower, better quality)
voice = "alloy"             # alloy, echo, fable, onyx, nova, shimmer
format = "mp3"              # mp3, opus, aac, flac, wav, pcm
speed = 1.0                 # 0.25 to 4.0
```

#### ElevenLabs

```toml
[tts]
provider = "elevenlabs"
api_key = "${ELEVENLABS_API_KEY}"
voice_id = "21m00Tcm4TlvDq8ikWAM"  # Your voice ID
model = "eleven_multilingual_v2"   # eleven_monolingual_v1, eleven_multilingual_v2
format = "mp3"
stability = 0.5             # 0-1, higher = more stable
similarity_boost = 0.5      # 0-1, higher = more similar to original
```

### Audio Processing

```toml
[audio]
temp_dir = "/tmp/voice-messaging"
sample_rate = 16000         # For STT (Whisper expects 16kHz)
channels = 1                # Mono
```

### Platform-Specific Formats

```toml
[platforms]
telegram_format = "ogg"
discord_format = "mp3"
```

---

## 🎮 Usage Examples

### Basic Usage

```python
from voice_messaging.src.voice_handler import VoiceHandler

# Load from config
handler = VoiceHandler.from_config("config.toml")

# Transcribe voice message
text = handler.transcribe("user_voice.ogg")
print(f"User said: {text}")

# Generate voice response
handler.synthesize("I understand! How can I help you today?", "response.ogg")
print("✓ Response ready")
```

### Swap Providers Without Code Changes

Just edit `config.toml` and restart:

```toml
# Switch from local to cloud
[tts]
provider = "openai"  # Was "kokoro"
api_key = "${OPENAI_API_KEY}"
voice = "alloy"
```

No code changes needed!

### List Available Voices

```python
from voice_messaging.src.voice_handler import VoiceHandler

handler = VoiceHandler.from_config("config.toml")
voices = handler.get_voices()
print(f"Available voices: {voices}")
```

### Custom Voice Settings

```python
# Use specific voice for this synthesis only
handler.synthesize(
    "Hello!",
    "output.ogg",
    voice="af_heart",
    speed=1.2,
    format="mp3"
)
```

---

## 📊 Performance Benchmarks

### With GPU (CUDA)

| Task | Provider | Performance |
|------|----------|-------------|
| STT | faster-whisper (base) | 30-60x real-time (~30s audio in 0.5s) |
| STT | OpenAI Whisper | ~1-2s latency (network-dependent) |
| TTS | Kokoro | 100x real-time (~30s audio in 0.3s) |
| TTS | OpenAI TTS | ~1-2s latency (network-dependent) |
| **Total (local)** | - | **< 2 seconds** |

### CPU-only

| Task | Provider | Performance |
|------|----------|-------------|
| STT | faster-whisper (base) | 2-3x real-time (~30s audio in 10-15s) |
| STT | OpenAI Whisper | ~1-2s latency (network-dependent) |
| TTS | Kokoro | 10-35x real-time (~30s audio in 1-3s) |
| TTS | OpenAI TTS | ~1-2s latency (network-dependent) |
| **Total (local)** | - | **5-15 seconds** |

**Recommendation:** Use GPU for production, CPU is acceptable for casual use.

---

## 🐛 Troubleshooting

### Issue: "FFmpeg not found"

**Symptom:** Error about missing FFmpeg during audio conversion

**Solutions:**

```bash
# Windows:
choco install ffmpeg

# macOS:
brew install ffmpeg

# Linux:
sudo apt install ffmpeg

# Verify installation:
ffmpeg -version
```

---

### Issue: "faster-whisper model download failed"

**Symptom:** Can't download Whisper model from Hugging Face

**Solutions:**

```bash
# Set Hugging Face cache directory
export HF_HUB_CACHE=/path/to/cache

# Or manually download model:
python -c "from faster_whisper import WhisperModel; WhisperModel('base')"
```

---

### Issue: "Kokoro TTS not responding"

**Symptom:** Connection refused or timeout when calling Kokoro endpoint

**Solutions:**

```bash
# Check if container is running
docker ps | grep kokoro

# If not running, start it:
docker start kokoro-tts

# Check logs
docker logs kokoro-tts

# Verify port is accessible
curl http://localhost:8880/v1/health

# Restart container
docker restart kokoro-tts

# Check if port is in use
netstat -an | grep 8880
```

**If container won't start:**

```bash
# Check Docker logs for errors
docker logs kokoro-tts --tail 100

# Remove and recreate container
docker stop kokoro-tts
docker rm kokoro-tts
docker run -d --name kokoro-tts --gpus all -p 8880:8880 \
  ghcr.io/omni-nexusai/agent-zero-kokoro-worker:v0.9.8-custom-pre-hybrid-gpu
```

---

### Issue: "Audio format not supported"

**Symptom:** Error when processing audio file

**Solution:** AudioProcessor handles conversion automatically, but verify:

```python
from voice_messaging.src.audio_processor import AudioProcessor

processor = AudioProcessor()

# Check supported formats
print(processor.get_supported_formats())

# Convert manually if needed
converted = processor.convert_for_stt("input.ogg")
```

---

### Issue: "CUDA out of memory"

**Symptom:** GPU memory error when processing audio

**Solutions:**

```toml
# Use smaller model
[stt]
model = "base"  # Instead of large-v3

# Use int8 quantization
compute_type = "int8"

# Or fall back to CPU
device = "cpu"
```

---

### Issue: "OpenAI API key not found"

**Symptom:** Error about missing API key when using cloud providers

**Solutions:**

```bash
# Set environment variable
export OPENAI_API_KEY="your-key-here"

# Or add to .bashrc / .zshrc
echo 'export OPENAI_API_KEY="your-key-here"' >> ~/.bashrc

# Or use ${OPENAI_API_KEY} in config.toml (recommended)
```

---

### Issue: "ElevenLabs quota exceeded"

**Symptom:** Error about character limit or quota

**Solutions:**

- Check your quota at [elevenlabs.io](https://elevenlabs.io)
- Upgrade your plan for more characters
- Or switch to a different provider temporarily

---

### Issue: "Slow transcription on CPU"

**Symptom:** Transcription takes 30+ seconds for short audio

**Solutions:**

```toml
# Use smaller model
[stt]
model = "tiny"  # Fastest, lower accuracy

# Use int8 quantization
compute_type = "int8"

# Or switch to cloud provider
provider = "openai"  # Faster but costs money
```

---

### Issue: "Voice response quality is poor"

**Symptom:** Robotic or low-quality voice output

**Solutions:**

```toml
# Try different voice
[tts]
voice = "af_sky"  # Or other voice

# For OpenAI TTS, use tts-1-hd model
model = "tts-1-hd"  # Slower but better quality

# For ElevenLabs, adjust parameters
stability = 0.7      # Higher = more stable
similarity_boost = 0.75  # Higher = more similar to original
```

---

## 🔒 Privacy & Security

### Local Providers (Recommended)

- **STT:** faster-whisper runs entirely on your machine
- **TTS:** Kokoro runs entirely on your machine
- **Data:** Never leaves your system
- **Privacy:** 100% - no cloud communication

### Cloud Providers

- **STT:** Audio sent to OpenAI/Google for processing
- **TTS:** Text sent to OpenAI/ElevenLabs for generation
- **Data:** Processed on third-party servers
- **Privacy:** Review provider's privacy policy

**Recommendation:** Use local providers for sensitive conversations, cloud providers for general use.

---

## 📚 Additional Documentation

- **[Quick Reference](QUICK_REFERENCE.md)** - Quick lookup of all providers and options
- **[Setup Guide](setup.ps1)** - Automated setup script (Windows PowerShell)
- **[Test Script](test.py)** - Test your installation and configuration

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Additional STT/TTS providers
- More voice options for existing providers
- Performance optimizations
- Better error handling and logging
- Additional platform support (Slack, Matrix, etc.)
- Framework-specific integrations (OpenClaw, LangChain, Agent Zero, etc.)

---

## 📄 License

MIT License - See LICENSE file for details.

---

## 🙏 Acknowledgments

- **faster-whisper** - Whisper implementation by Guillaime
- **Kokoro** - TTS by Hexgrad
- **OpenAI** - Whisper and TTS APIs
- **ElevenLabs** - Premium TTS service

---

## ❓ Questions?

- Check the [Troubleshooting](#troubleshooting) section
- Review the [Quick Reference](QUICK_REFERENCE.md)
- Run the test script: `python test.py`
- Open an issue on GitHub

---

**Enjoy voice messaging! 🎤**
