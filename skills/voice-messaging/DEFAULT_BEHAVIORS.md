# Default Behaviors Guide

This guide explains the default behaviors for voice messaging in the agent-voice-messaging library.

---

## Overview

The agent-voice-messaging library is designed with **smart defaults** that make voice messaging intuitive and user-friendly. These defaults are based on how people naturally expect voice messaging systems to behave.

---

## Default Behavior #1: Always Include AI Response Transcription

### The Rule

When a user sends a **voice message**, the agent ALWAYS responds with both:
1. **Voice audio file** - The AI's response synthesized into speech
2. **Text transcription** - The same response as readable text

### Why This Default?

1. **Accessibility** - Users can read the response even in noisy environments
2. **Clarity** - Some words may be unclear in speech; text provides certainty
3. **Reference** - Users can scroll back and read previous responses
4. **Copy-paste** - Text can be easily shared or saved
5. **User expectation** - Voice assistants (Siri, Alexa, Google Assistant) typically show both

### When to Omit Transcription

Only send voice-only response when:
- User explicitly says "voice-only" or "no text"
- User has a preference set for voice-only responses
- The response is very brief and contextual (e.g., "OK", "Got it")

### Example Workflows

#### ✅ Standard Voice Message (Default)

```
User: Sends voice message → "What's the weather today?"

Agent responds with:
  🎤 Voice: "It's 72°F and sunny today!"
  📝 Text: "It's 72°F and sunny today!"
```

#### ✅ Voice-Only Request (Override)

```
User: Sends voice message → "Tell me the weather, voice-only please."

Agent responds with:
  🎤 Voice: "It's 72°F and sunny today!"
  (No text transcription)
```

#### ✅ Brief Response (Contextual)

```
User: Sends voice message → "Are you there?"

Agent responds with:
  🎤 Voice: "Yes, I'm here!"
  📝 Text: "Yes, I'm here!"
  (Note: Still includes transcription by default)
```

---

## Default Behavior #2: Voice-Only on Text Messages (Unless Requested)

### The Rule

When a user sends a **text message**, the agent responds with **TEXT ONLY** by default.

Do NOT send voice output unless the user explicitly asks for it.

### Why This Default?

1. **No jarring surprises** - Voice response to text can be unexpected
2. **Respect user choice** - User chose to type, so respond with text
3. **Noise awareness** - User may be in a quiet environment where voice would be disruptive
4. **Speed** - Text response is faster to read than waiting for voice synthesis
5. **Preference matching** - Match the input modality with the output modality

### When to Send Voice

Only send voice response to text when:
- User explicitly asks: "Can you tell me via voice?" or "Say it out loud"
- User uses voice-related keywords: "speak", "say", "tell me", "read it"
- User has a preference set for voice responses
- The content is naturally suited to voice (e.g., pronunciation guides)

### Example Workflows

#### ✅ Standard Text Message (Default)

```
User: Sends text → "What's the weather today?"

Agent responds with:
  📝 Text: "It's 72°F and sunny today!"
  (No voice)
```

#### ✅ Voice Request (Override)

```
User: Sends text → "What's the weather? Say it out loud."

Agent responds with:
  🎤 Voice: "It's 72°F and sunny today!"
  📝 Text: "It's 72°F and sunny today!"
  (Includes both because it's a voice request)
```

#### ✅ Pronunciation Request

```
User: Sends text → "How do you pronounce 'Worcestershire'?"

Agent responds with:
  📝 Text: "Worcestershire is pronounced 'WUS-ter-sheer'."
  🎤 Voice: "WUS-ter-sheer" (pronunciation only)
```

---

## Summary of Default Behaviors

| User Input | Default Response | When to Override |
|------------|------------------|------------------|
| **Voice message** | Voice + Text transcription | User requests "voice-only" |
| **Text message** | Text only | User asks for voice ("say it", "speak", etc.) |

---

## Configuration

These defaults are configured in `config.toml`:

```toml
[defaults]
# Always include transcription when responding to voice messages
include_transcription_on_voice_response = true

# Do NOT send voice when responding to text messages
voice_response_to_text_message = false
```

### Changing Defaults

You can override these defaults if your use case requires different behavior:

```toml
[defaults]
# Example: Never include transcription
include_transcription_on_voice_response = false

# Example: Always respond with voice (even to text)
voice_response_to_text_message = true
```

**Warning:** Changing these defaults may make the agent less intuitive for users.

---

## Implementing These Defaults

### In Your Agent Code

The VoiceHandler provides helper methods to check these defaults:

```python
from voice_messaging.src.voice_handler import VoiceHandler

handler = VoiceHandler.from_config("config.toml")

# Check if transcription should be included for voice response
if handler.should_include_transcription_on_voice_response():
    # Send both voice and text
    handler.synthesize(response_text, "response.ogg")
    send_message(response_text)
else:
    # Send voice only
    handler.synthesize(response_text, "response.ogg")

# Check if voice should be sent to text message
if handler.should_send_voice_to_text_message():
    # Send voice + text
    handler.synthesize(response_text, "response.ogg")
    send_message(response_text)
else:
    # Send text only
    send_message(response_text)
```

### Detecting User Intent

Your agent should detect when users explicitly request or avoid certain behaviors:

```python
def detect_user_intent(message: str) -> dict:
    """Detect if user wants voice-only or voice response."""
    message_lower = message.lower()

    # Voice-only indicators
    voice_only_keywords = ["voice-only", "no text", "don't write", "just speak"]
    wants_voice_only = any(keyword in message_lower for keyword in voice_only_keywords)

    # Voice request indicators (for text messages)
    voice_request_keywords = ["say it", "speak", "tell me", "read it", "say out loud"]
    wants_voice = any(keyword in message_lower for keyword in voice_request_keywords)

    return {
        "voice_only": wants_voice_only,
        "voice_response": wants_voice
    }
```

---

## Framework-Specific Examples

### OpenClaw Integration

```python
def handle_voice_message(audio_path: str, platform: str):
    handler = VoiceHandler.from_config("config.toml")

    # Transcribe voice message
    text = handler.transcribe(audio_path)

    # Process text with your agent
    response = process_with_agent(text)

    # Always include transcription by default
    if handler.should_include_transcription_on_voice_response():
        handler.synthesize(response, "response.ogg")
        send_voice("response.ogg", platform)
        send_text(response, platform)
    else:
        handler.synthesize(response, "response.ogg")
        send_voice("response.ogg", platform)

def handle_text_message(text: str, platform: str):
    handler = VoiceHandler.from_config("config.toml")

    # Process text with your agent
    response = process_with_agent(text)

    # Check if user wants voice response
    intent = detect_user_intent(text)

    if intent["voice_response"] or handler.should_send_voice_to_text_message():
        handler.synthesize(response, "response.ogg")
        send_voice("response.ogg", platform)
        send_text(response, platform)
    else:
        send_text(response, platform)
```

### LangChain Integration

```python
from langchain.agents import Tool
from voice_messaging.src.voice_handler import VoiceHandler

handler = VoiceHandler.from_config("config.toml")

def voice_responder(text: str) -> str:
    """Process text and determine if voice response is needed."""
    response = agent.run(text)

    intent = detect_user_intent(text)

    if intent["voice_response"] or handler.should_send_voice_to_text_message():
        handler.synthesize(response, "response.ogg")
        send_voice("response.ogg", platform)
        return f"[VOICE] {response}"
    else:
        return response

voice_tool = Tool(
    name="Voice Messaging",
    func=voice_responder,
    description="Process messages and optionally respond with voice"
)
```

---

## Best Practices

### ✅ DO

1. **Always check defaults** - Use `should_include_transcription_on_voice_response()` and `should_send_voice_to_text_message()`
2. **Detect user intent** - Look for explicit requests like "voice-only" or "say it"
3. **Be consistent** - Follow the defaults unless there's a clear user request to override
4. **Provide context** - When sending voice-only, make it clear in previous messages
5. **Handle errors gracefully** - If TTS fails, fall back to text transcription

### ❌ DON'T

1. **Don't guess preferences** - Only override defaults when user explicitly asks
2. **Don't surprise users** - Voice response to text can be jarring
3. **Don't hide information** - Omitting transcription can make responses inaccessible
4. **Don't ignore configuration** - Respect the settings in `config.toml`
5. **Don't over-optimize** - Defaults are there for a reason - only change if necessary

---

## Troubleshooting

### "Why isn't my agent sending voice to text messages?"

Check your configuration:
```toml
[defaults]
voice_response_to_text_message = false  # This is the default!
```

If you want voice responses to text messages, set this to `true`.

### "Why is my agent sending transcription when I want voice-only?"

The user may not have explicitly requested voice-only. Check their message for keywords like "voice-only" or "no text".

### "How do I change the default behavior?"

Edit `config.toml`:
```toml
[defaults]
include_transcription_on_voice_response = false  # Never include transcription
voice_response_to_text_message = true           # Always respond with voice
```

---

## Questions?

- Review the [main README](README.md) for setup instructions
- Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for provider configuration
- See [SKILL.md](SKILL.md) for framework-specific integration
