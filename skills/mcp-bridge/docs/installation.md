# Installation Guide

## Prerequisites

- Python 3.10 or higher
- An Openclaw agent running (Docker, Native, or Remote)

## Installation Options

### Option A: Install via pip (Recommended)

```bash
pip install openclaw-mcp-bridge
```

This installs the package globally and makes the `openclaw-mcp` command available.

### Option B: Standalone Installation

For development or if you prefer not to install via pip:

```bash
# Clone the repository
git clone https://github.com/Omni-NexusAI/openclaw-mcp-bridge.git
cd openclaw-mcp-bridge

# Install dependencies
pip install -r requirements.txt

# Run directly
python src/server.py
```

## MCP Client Configuration

After installation, configure your MCP client to use the bridge.

### Claude Desktop

Edit `%APPDATA%\Claude\settings.json` (Windows) or `~/Library/Application Support/Claude/settings.json` (macOS):

```json
{
  "mcpServers": {
    "openclaw-bridge": {
      "command": "python",
      "args": ["-m", "openclaw_mcp_bridge"],
      "env": {
        "OPENCLAW_AGENT_1_NAME": "docker",
        "OPENCLAW_AGENT_1_URL": "http://host.docker.internal:18789",
        "OPENCLAW_AGENT_1_TOKEN": "your-token-here",
        "OPENCLAW_AGENT_1_ENABLED": "true"
      }
    }
  }
}
```

### A0 (Agent Zero)

Add to your A0 MCP configuration:

```json
{
  "mcpServers": {
    "openclaw-bridge": {
      "description": "Bridge to Openclaw agents",
      "command": "/usr/bin/python3",
      "args": ["-m", "openclaw_mcp_bridge"],
      "env": {
        "OPENCLAW_AGENT_1_NAME": "docker",
        "OPENCLAW_AGENT_1_URL": "http://host.docker.internal:18789",
        "OPENCLAW_AGENT_1_TOKEN": "your-token-here",
        "OPENCLAW_AGENT_1_ENABLED": "true"
      }
    }
  }
}
```

### Continue.dev

Add to your `.continue/config.json`:

```json
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
          "command": "python",
          "args": ["-m", "openclaw_mcp_bridge"],
          "env": {
            "OPENCLAW_AGENT_1_NAME": "docker",
            "OPENCLAW_AGENT_1_URL": "http://host.docker.internal:18789",
            "OPENCLAW_AGENT_1_TOKEN": "your-token-here",
            "OPENCLAW_AGENT_1_ENABLED": "true"
          }
        }
      }
    ]
  }
}
```

## Verification

After configuration, test the connection:

1. Restart your MCP client
2. Ask your agent: "List available Openclaw agents"
3. You should see a list of configured agents

## Troubleshooting

### "No agents configured" error

Ensure environment variables are properly set in the MCP configuration. The variables must be prefixed with `OPENCLAW_AGENT_` followed by a number (1-10).

### "Cannot connect" errors

- Verify the Openclaw agent is running
- Check the URL is accessible from the MCP client
- For Docker agents, ensure `host.docker.internal` resolves correctly
- For remote agents, verify network connectivity

### Timeout errors

Increase the timeout:
```bash
OPENCLAW_AGENT_1_TIMEOUT=300  # 5 minutes
```

## Next Steps

- Read the [Configuration Guide](configuration.md) to set up multiple agents
- See [Usage Examples](usage.md) for common tasks
- Check [Architecture](architecture.md) for technical details
