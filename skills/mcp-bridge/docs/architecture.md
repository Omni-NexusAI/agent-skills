# Architecture

## Overview

Openclaw MCP Bridge is a lightweight MCP server that translates between the Model Context Protocol and Openclaw's HTTP API.

```
┌─────────────────┐     MCP (stdio)      ┌──────────────────┐     HTTP/JSON      ┌─────────────────┐
│  MCP Client     │ ◄──────────────────► │  MCP Bridge      │ ◄────────────────► │  Openclaw       │
│  (Claude/A0)    │                      │  (this server)   │                    │  Agent          │
└─────────────────┘                      └──────────────────┘                    └─────────────────┘
```

## Components

### 1. MCP Server (`server.py`)

The main entry point that exposes MCP tools:

- **`call_openclaw`**: Send messages to Openclaw agents
- **`list_openclaw_agents`**: List configured agents

Uses [FastMCP](https://github.com/jlowin/fastmcp) for MCP protocol handling.

### 2. Agent Manager (`AgentManager`)

Manages configuration for multiple Openclaw agents:

- Loads agent configs from environment variables
- Validates configuration on startup
- Provides agent lookup by name
- Supports up to 10 agents

Configuration format:
```
OPENCLAW_AGENT_{N}_{SETTING}
```

### 3. HTTP Client (`OpenclawClient`)

Handles communication with Openclaw agents:

- Uses `httpx` for async HTTP requests
- Supports OpenAI-compatible `/v1/chat/completions` endpoint
- Implements proper authentication headers
- Handles timeouts and connection errors
- Masks tokens in logs for security

### 4. Protocol Handler

Translates between MCP and Openclaw formats:

**MCP → Openclaw:**
```python
{
  "instruction": "Check system status",
  "agent": "docker",
  "attachments": ["/path/to/file.txt"]
}
↓
{
  "model": "openclaw:main",
  "messages": [
    {"role": "user", "content": "Check system status\n\n[file content...]"}
  ],
  "stream": False
}
```

**Openclaw → MCP:**
```python
{
  "choices": [
    {
      "message": {
        "content": "System is healthy..."
      }
    }
  ]
}
↓
"System is healthy..."
```

## Data Flow

### Request Flow

1. **User Request**: "Ask the docker agent to check status"

2. **MCP Client**: Calls `call_openclaw(instruction="...", agent="docker")`

3. **MCP Server**: 
   - Validates agent exists
   - Creates `OpenclawClient` instance
   - Processes attachments (if any)

4. **HTTP Client**:
   - Constructs request payload
   - Adds authentication headers
   - Sends POST to Openclaw

5. **Openclaw Agent**:
   - Processes the message
   - Generates response
   - Returns JSON

6. **Response Chain**:
   - HTTP Client extracts content
   - MCP Server returns to client
   - User sees the response

### Error Handling

```
User Request
    ↓
[MCP Tool]
    ↓
Agent Exists? ──No──► Return "Agent not found"
    ↓ Yes
Agent Enabled? ──No──► Return "Agent disabled"
    ↓ Yes
[HTTP Request]
    ↓
Connection Error? ──Yes──► Return "Cannot connect"
    ↓ No
Timeout? ──Yes──► Return "Request timed out"
    ↓ No
HTTP Error? ──Yes──► Return "HTTP Error X"
    ↓ No
[Extract Response]
    ↓
Return content to user
```

## Security

### Authentication

- Tokens are passed via environment variables
- Never logged in full (masked as `abcd...wxyz`)
- Multiple auth headers for compatibility:
  - `Authorization: Bearer <token>`
  - `X-API-Key: <token>`

### Input Validation

- Agent names must be configured
- URLs are validated (must be non-empty)
- File attachments are checked for existence
- Timeouts prevent indefinite hangs

### Logging

- INFO: Agent calls, responses
- WARNING: Errors, timeouts
- DEBUG: Full request/response (optional)
- Tokens are always masked in logs

## Protocol Support

### Supported: OpenAI Chat Completions

Primary endpoint: `POST /v1/chat/completions`

**Advantages:**
- Synchronous request/response
- Standard format
- No callback complexity
- Widely supported

**Format:**
```json
{
  "model": "openclaw:main",
  "messages": [{"role": "user", "content": "Hello"}],
  "stream": false
}
```

### Not Supported: Tools Invoke (sessions_send)

Could be added as fallback if needed, but adds complexity:
- Asynchronous (fire-and-forget)
- Requires polling for response
- More error prone

## File Attachments

### Implementation

1. Read file as text (UTF-8)
2. Format as markdown code block
3. Append to message content
4. Send combined message

**Limitations:**
- Text files only
- No binary support
- Size limited by Openclaw
- Must be accessible from MCP server

### Example Transformation

```python
# Input
instruction="Review this file"
attachments=["/path/to/code.py"]

# Transformed to
"""Review this file

[Attached file: code.py]
```python
def hello():
    print("Hello World")
```
"""
```

## Multi-Agent Support

The bridge supports multiple agents simultaneously:

```python
agents = {
    "docker": AgentConfig(url="...", token="..."),
    "native": AgentConfig(url="...", token="..."),
    "remote": AgentConfig(url="...", token="...")
}
```

Each agent:
- Has independent configuration
- Can be enabled/disabled
- Has its own timeout
- Can use different endpoints

## Performance Considerations

### Timeouts

- Default: 120 seconds
- Configurable per agent
- Must accommodate Openclaw response time
- Includes network latency

### Concurrency

- HTTP client creates new connection per request
- No connection pooling (simple but slower)
- Async/await for non-blocking

### Resource Usage

- Minimal memory footprint
- No persistent state
- Stateless design

## Extensibility

### Adding New Protocols

To support a different Openclaw endpoint:

1. Add protocol handler in `protocol.py`
2. Update `OpenclawClient.send_message()`
3. Add configuration option

### Custom Attachment Handlers

```python
class AttachmentHandler(ABC):
    @abstractmethod
    async def process(self, file_path: str) -> str:
        pass

# Example: PDF support
class PDFHandler(AttachmentHandler):
    async def process(self, file_path: str) -> str:
        # Extract text from PDF
        return extracted_text
```

## Future Enhancements

### Potential Improvements

1. **Connection Pooling**: Reuse HTTP connections
2. **Streaming**: Support SSE for real-time responses
3. **Caching**: Cache agent responses
4. **Metrics**: Track request latency/error rates
5. **WebSocket**: Support WebSocket transport
6. **Plugin System**: Allow custom protocol handlers

### Not Planned

- Bidirectional WebSocket (complex, callback issues)
- Built-in rate limiting (use external solutions)
- Persistent storage (keep it stateless)

## Dependencies

### Required

- `fastmcp`: MCP protocol implementation
- `httpx`: Async HTTP client

### Python Version

- 3.10+ (type hints, dataclasses, async/await)

## Testing Strategy

### Unit Tests (Future)

- Mock HTTP responses
- Test configuration loading
- Validate error handling

### Integration Tests (Manual)

- Test with real Openclaw agents
- Verify file attachments
- Test timeout behavior

### End-to-End Tests

- Full MCP client → Bridge → Openclaw flow
- Multiple agent scenarios
- Error condition testing
