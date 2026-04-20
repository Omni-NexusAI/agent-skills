# Agent Voice Messaging

**Purpose**: Enable voice message communication through Telegram/Discord with local STT/TTS

**Framework Support**: OpenClaw • LangChain • Agent Zero • Generic Agents

**Features**:
- Receive voice messages → transcribe → process → respond with voice
- Modular provider swapping (STT: Whisper, OpenAI, Google; TTS: Kokoro, Qwen3, ElevenLabs)
- Automatic audio format conversion
- Platform-specific output formats
- Framework-agnostic design

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

### Default Behavior #2: Voice-Only on Text Messages (Unless Requested)

When a user sends a **text message**, the agent responds with **text only** by default.

Do NOT send voice output unless the user explicitly asks for it.

**Example workflow:**
```
User: Sends text → "What's the weather?"
Agent: Responds with:
  - Text: "It's 72°F and sunny today!"
  - Voice: (not sent)
```

### Summary of Default Behaviors

| User Input | Default Response | How to Override |
|------------|------------------|-----------------|
| **Voice message** | Voice + Text transcription | User requests "voice-only" |
| **Text message** | Text only | User asks for voice ("say it", "speak", etc.) |

These defaults are designed for intuitive voice messaging. Users expect to see what was said, and voice responses to text messages can be jarring unless explicitly requested.

---

## Quick Start

## Quick Start

### Step 1: Install Dependencies

```bash
pip install faster-whisper requests pyav
```

### Step 2: Configure Providers

Edit `config.toml`:

```toml
[stt]
provider = "faster-whisper"  # Options: faster-whisper, openai, google
model = "base"
device = "cpu"

[tts]
provider = "kokoro"  # Options: kokoro, qwen3, openai, elevenlabs
base_url = "http://localhost:8880/v1"
voice = "af_bella"
```

### Step 3: Install in Your Framework

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

### Step 4: Test

```python
from voice_messaging.src.voice_handler import VoiceHandler

handler = VoiceHandler.from_config("config.toml")

# Test STT
text = handler.transcribe("test.wav")
print(f"Transcribed: {text}")

# Test TTS
handler.synthesize("Hello world!", "output.ogg")
print("✓ TTS test passed")
```

---

## Supported Providers

### STT (Speech-to-Text)
- **faster-whisper**: Local, fast (default)
- **openai**: OpenAI Whisper API
- **google**: Google Cloud Speech-to-Text

### TTS (Text-to-Speech)
- **kokoro**: Local, fast (default)
- **qwen3**: Local, customizable
- **openai**: OpenAI TTS API
- **elevenlabs**: ElevenLabs API

---

## Usage in Your Agent Framework

When you receive a voice message, the library automatically:
1. Transcribes the audio (using configured STT)
2. Processes the text (your agent's normal processing)
3. Generates voice response (using configured TTS)
4. Sends back the audio file

No additional code needed - it works automatically!

---

## Framework-Specific Integration

### OpenClaw
- Works as a native skill
- Automatic voice message handling
- Compatible with Telegram and Discord plugins

### LangChain
- Use as a LangChain Tool
- Integrate with LangChain agents
- Chain-based voice workflows

### Agent Zero
- Direct Python integration
- Custom workflow support
- Agent Zero ecosystem compatibility

### Generic Agents
- Standalone Python module
- Works with any Python code
- No framework dependencies

---

## Example: Multi-Agent Setup

```python
from voice_messaging.src.voice_handler import VoiceHandler

# Initialize with different configs per agent
handler1 = VoiceHandler.from_config("config_agent1.toml")
handler2 = VoiceHandler.from_config("config_agent2.toml")

# Each agent can have different STT/TTS providers
# Agent 1: Local-only (privacy)
# Agent 2: Cloud-only (speed)
```
