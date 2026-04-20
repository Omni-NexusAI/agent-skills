# Openclaw MCP Bridge

A generic Model Context Protocol (MCP) server that enables any MCP-compatible agent (Claude, A0, Continue, etc.) to communicate with [Openclaw](https://openclaw.ai) agents running locally or remotely.

## Features

- **Multi-Agent Support**: Connect to multiple Openclaw agents (Docker, Native, Remote)
- **Simple Configuration**: Environment variable-based configuration
- **File Attachments**: Send text files along with your messages
- **Standard MCP**: Works with any MCP-compatible client
- **Timeout Handling**: Configurable timeouts for long-running operations
- **Secure**: Token masking in logs, no hardcoded secrets

## Quick Start

### 1. Install

**Option A: Via pip**
```bash
pip install openclaw-mcp-bridge
```

**Option B: Standalone**
```bash
git clone https://github.com/Omni-NexusAI/openclaw-mcp-bridge.git
cd openclaw-mcp-bridge
pip install -r requirements.txt
```

### 2. Configure

Add to your MCP client's configuration:

```json
{
  "mcpServers": {
    "openclaw-bridge": {
      "command": "python",
      "args": ["-m", "openclaw_mcp_bridge"],
      "env": {
        "OPENCLAW_AGENT_1_NAME": "docker",
        "OPENCLAW_AGENT_1_URL": "http://host.docker.internal:18789",
        "OPENCLAW_AGENT_1_TOKEN": "your-docker-token",
        "OPENCLAW_AGENT_1_ENABLED": "true"
      }
    }
  }
}
```

### 3. Use

Ask your agent to use Openclaw:

```
"Ask the docker agent to check system status"
"Use the native agent to list files in my workspace"
```

## Documentation

- [Installation Guide](docs/installation.md)
- [Configuration Guide](docs/configuration.md)
- [Usage Examples](docs/usage.md)
- [Architecture](docs/architecture.md)

## Supported Agents

- ✅ Docker Openclaw (Linux/WSL containers)
- ⚠️ Native Openclaw (Windows - pending full support)
- ✅ Remote Openclaw (any accessible instance)

## License

MIT License - see [LICENSE](LICENSE) file.

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md).
