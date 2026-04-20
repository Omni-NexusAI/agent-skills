# Agent Voice Messaging - Quick Reference

## Default Behaviors

The agent-voice-messaging library uses smart defaults for voice messaging interactions:

### Voice Input → Always Dual Output (Voice + Transcription)
When a user sends a voice message, the agent ALWAYS responds with:
- Voice audio file (AI response)
- Text transcription of the AI response

Only send voice-only if user explicitly requests it.

### Text Input → Text Only (Unless Requested)
When a user sends a text message, the agent responds with TEXT ONLY by default.
Do NOT send voice output unless user explicitly asks for it.

**Configuration (config.toml):**
```toml
[defaults]
include_transcription_on_voice_response = true
voice_response_to_text_message = false
```

**Summary:**
| User Input | Default Response | Override |
|------------|------------------|----------|
| Voice | Voice + Text | User requests "voice-only" |
| Text | Text only | User asks for voice |

---

## What You Asked For

1. ✅ **Voice messaging works** - Send voice from Telegram/Discord, receive voice back
2. ✅ **Modular providers** - Swap ANY STT/TTS provider easily (not just Kokoro/Qwen3)
3. ✅ **Simple setup** - Easy to install and use
4. ✅ **Framework-agnostic** - Works with OpenClaw, LangChain, Agent Zero, and generic agents
5. ⏸ **Full modularity/cross-platform** - Future work (for now, keep it simple)

---

## What I Created

**Location:** `voice-messaging-skill/` (or `agent-voice-messaging/`)

### Files

```
agent-voice-messaging/
├─ SKILL.md           # Skill description
├─ README.md          # Complete usage guide
├─ config.toml        # Configuration file (edit this to swap providers)
├─ setup.ps1          # Windows installation script
└─ src/
    ├─ __init__.py
    ├─ providers.py      # Abstract interfaces + factory
    ├─ stt_providers.py # STT implementations (faster-whisper, OpenAI, Google)
    ├─ tts_providers.py # TTS implementations (Kokoro, Qwen3, OpenAI, ElevenLabs)
    ├─ audio_processor.py # Audio format conversion
    └─ voice_handler.py   # Main handler
```

---

## How It Works

### 1. You Send Voice Message
```
Telegram/Discord → Voice Message → Your Agent receives audio file
```

### 2. Library Processes
```
Audio → STT Provider → Transcription → Your Agent Processing
```

### 3. Agent Responds
```
Response Text → TTS Provider → Voice Audio → Send back
```

---

## Framework Support

### OpenClaw
- Install as a skill
- Automatic voice message handling
- Native integration

### LangChain
- Use as a LangChain Tool
- Integrate with LangChain agents
- Chain-based workflows

### Agent Zero
- Direct Python integration
- Custom workflow support
- Agent Zero ecosystem compatibility

### Generic Agents
- Standalone Python module
- Works with any Python code
- No framework dependencies

---

## Supported Providers

### STT (Speech-to-Text)
- `faster-whisper` - Local, fast
- `openai` - OpenAI Whisper API
- `google` - Google Cloud Speech-to-Text

### TTS (Text-to-Speech)
- `kokoro` - Local, production quality
- `qwen3` - Local, customizable (when available)
- `openai` - OpenAI TTS API
- `elevenlabs` - ElevenLabs API

---

## How to Swap Providers

### Example: Swap from Kokoro to Qwen3 (when available)

Edit `config.toml`:

```toml
# Before:
[tts]
provider = "kokoro"

# After:
[tts]
provider = "qwen3"
model_path = "/path/to/qwen3-tts"
device = "cuda"
```

### Example: Swap from faster-whisper to OpenAI

Edit `config.toml`:

```toml
# Before:
[stt]
provider = "faster-whisper"

# After:
[stt]
provider = "openai"
api_key = "${OPENAI_API_KEY}"
```

**No code changes needed!** Just edit config and restart.

---

## Installation (Windows)

### Option 1: Automated (Recommended)

```powershell
cd agent-voice-messaging
.\setup.ps1
```

**Setup script will:**
- ✅ Check Python
- ✅ Install Python dependencies
- ✅ Check/install FFmpeg
- ✅ Check Kokoro TTS
- ✅ Test setup
- ✅ Copy files to OpenClaw skills directory (if using OpenClaw)

### Option 2: Manual

```powershell
# 1. Install dependencies
pip install faster-whisper requests pyav tomli

# 2. Install FFmpeg (if not already installed)
choco install ffmpeg

# 3. Copy to OpenClaw skills (if using OpenClaw)
xcopy agent-voice-messaging C:\Users\yepyy\.openclaw\skills\ /E /I

# 4. Install in OpenClaw (if using OpenClaw)
openclaw skills install C:\Users\yepyy\.openclaw\skills\agent-voice-messaging
```

### For Other Frameworks

```powershell
# Just install dependencies
pip install faster-whisper requests pyav tomli

# Install FFmpeg
choco install ffmpeg

# Use as a standalone Python module
# No framework-specific installation needed!
```

---

## After Installation

### Test 1: Quick Test

```powershell
cd agent-voice-messaging
python -c "from src.voice_handler import quick_test; quick_test()"
```

### Test 2: Send Real Voice Message

1. Go to Telegram/Discord
2. Record a voice message
3. Send to your agent
4. Agent transcribes → processes → responds with voice

---

## Configuration

Edit `config.toml`:

```toml
[stt]
provider = "faster-whisper"
model = "base"
device = "cpu"

[tts]
provider = "kokoro"
base_url = "http://localhost:8880/v1"
voice = "af_bella"
format = "ogg"
```

---

## Common Tasks

### Check Available Voices

```python
from voice_messaging.src.voice_handler import VoiceHandler

handler = VoiceHandler.from_config("config.toml")
voices = handler.get_voices()
print(f"Voices: {voices}")
```

### Test STT Only

```python
from voice_messaging.src.stt_providers import quick_transcribe

text = quick_transcribe("test.wav")
print(f"Transcribed: {text}")
```

### Test TTS Only

```python
from voice_messaging.src.tts_providers import quick_synthesize

quick_synthesize("Hello world!", "output.ogg")
print("✓ TTS test passed")
```

---

## Troubleshooting

### "FFmpeg not found"

Install FFmpeg:
```powershell
choco install ffmpeg
```

### "Kokoro TTS not responding"

Check Docker:
```powershell
docker ps | grep kokoro
docker logs <container_name>
docker restart <container_name>
```

### "Model download slow"

Set cache directory:
```bash
export HF_HUB_CACHE=/path/to/cache
```

---

## What This Solves

✅ **Voice messaging works** - Send voice, receive voice back
✅ **Provider swapping** - Change STT/TTS in config, no code changes
✅ **Platform compatibility** - Telegram and Discord supported
✅ **Local-first** - No cloud APIs required
✅ **Extensible** - Easy to add new providers
✅ **Framework-agnostic** - Works with OpenClaw, LangChain, Agent Zero, and generic agents

---

## Next Steps

1. ✅ Install library (run setup.ps1 or install dependencies manually)
2. ✅ Test with quick_test()
3. ✅ Send real voice message
4. ⏳ Swap providers as needed (edit config.toml)
5. ⏳ Integrate with your preferred framework
6. ⏳ Future: Full modularity and cross-platform support

---

**Status: Ready to use!** Just run `.\setup.ps1` and you're good to go.
