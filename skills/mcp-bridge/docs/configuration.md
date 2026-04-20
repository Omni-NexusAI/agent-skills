# Configuration Guide

## Overview

Openclaw MCP Bridge uses environment variables for configuration. This allows seamless integration with any MCP client without external configuration files.

## Environment Variables

### Agent Configuration

Configure up to 10 agents using numbered prefixes:

```bash
OPENCLAW_AGENT_{N}_{SETTING}
```

Where `{N}` is a number from 1 to 10.

### Required Settings

For each agent, you must specify:

- `OPENCLAW_AGENT_{N}_NAME`: Unique identifier for the agent (e.g., "docker", "native", "production")
- `OPENCLAW_AGENT_{N}_URL`: Base URL of the Openclaw agent (e.g., "http://host.docker.internal:18789")
- `OPENCLAW_AGENT_{N}_TOKEN`: Authentication token for the agent

### Optional Settings

- `OPENCLAW_AGENT_{N}_ENDPOINT`: API endpoint path (default: `/v1/chat/completions`)
- `OPENCLAW_AGENT_{N}_ENABLED`: Whether the agent is active (default: `true`)
- `OPENCLAW_AGENT_{N}_TIMEOUT`: Request timeout in seconds (default: `120`)

### Global Settings

- `OPENCLAW_MCP_LOG_LEVEL`: Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)

## Configuration Examples

### Example 1: Single Docker Agent

```json
{
  "mcpServers": {
    "openclaw-bridge": {
      "command": "python",
      "args": ["-m", "openclaw_mcp_bridge"],
      "env": {
        "OPENCLAW_AGENT_1_NAME": "docker",
        "OPENCLAW_AGENT_1_URL": "http://host.docker.internal:18789",
        "OPENCLAW_AGENT_1_TOKEN": "docker-token-123",
        "OPENCLAW_AGENT_1_ENABLED": "true"
      }
    }
  }
}
```

### Example 2: Multiple Local Agents

```json
{
  "mcpServers": {
    "openclaw-bridge": {
      "command": "python",
      "args": ["-m", "openclaw_mcp_bridge"],
      "env": {
        "OPENCLAW_AGENT_1_NAME": "docker",
        "OPENCLAW_AGENT_1_URL": "http://host.docker.internal:18789",
        "OPENCLAW_AGENT_1_TOKEN": "docker-token",
        "OPENCLAW_AGENT_1_ENABLED": "true",
        
        "OPENCLAW_AGENT_2_NAME": "native",
        "OPENCLAW_AGENT_2_URL": "http://localhost:19789",
        "OPENCLAW_AGENT_2_TOKEN": "native-token",
        "OPENCLAW_AGENT_2_ENABLED": "true",
        
        "OPENCLAW_AGENT_3_NAME": "experimental",
        "OPENCLAW_AGENT_3_URL": "http://localhost:19790",
        "OPENCLAW_AGENT_3_TOKEN": "experimental-token",
        "OPENCLAW_AGENT_3_ENABLED": "false"
      }
    }
  }
}
```

### Example 3: Remote Agent

```json
{
  "mcpServers": {
    "openclaw-bridge": {
      "command": "python",
      "args": ["-m", "openclaw_mcp_bridge"],
      "env": {
        "OPENCLAW_AGENT_1_NAME": "remote-office",
        "OPENCLAW_AGENT_1_URL": "http://192.168.1.100:18789",
        "OPENCLAW_AGENT_1_TOKEN": "remote-token",
        "OPENCLAW_AGENT_1_ENABLED": "true",
        "OPENCLAW_AGENT_1_TIMEOUT": "300"
      }
    }
  }
}
```

### Example 4: Development Setup with Debug Logging

```json
{
  "mcpServers": {
    "openclaw-bridge": {
      "command": "python",
      "args": ["-m", "openclaw_mcp_bridge"],
      "env": {
        "OPENCLAW_MCP_LOG_LEVEL": "DEBUG",
        
        "OPENCLAW_AGENT_1_NAME": "dev",
        "OPENCLAW_AGENT_1_URL": "http://localhost:18789",
        "OPENCLAW_AGENT_1_TOKEN": "dev-token",
        "OPENCLAW_AGENT_1_ENABLED": "true"
      }
    }
  }
}
```

## Agent Types

### Docker Agent

For Openclaw running in Docker:

```json
"OPENCLAW_AGENT_1_NAME": "docker",
"OPENCLAW_AGENT_1_URL": "http://host.docker.internal:18789",
"OPENCLAW_AGENT_1_TOKEN": "your-token"
```

**Note**: `host.docker.internal` works on Docker Desktop. For Linux, use the container's IP address.

### Native Agent

For Openclaw running directly on the host:

```json
"OPENCLAW_AGENT_1_NAME": "native",
"OPENCLAW_AGENT_1_URL": "http://localhost:19789",
"OPENCLAW_AGENT_1_TOKEN": "your-token"
```

**Note**: Native Windows support is pending. Currently tested on Linux/macOS.

### Remote Agent

For Openclaw on another machine:

```json
"OPENCLAW_AGENT_1_NAME": "remote",
"OPENCLAW_AGENT_1_URL": "http://192.168.1.50:18789",
"OPENCLAW_AGENT_1_TOKEN": "your-token",
"OPENCLAW_AGENT_1_TIMEOUT": "300"
```

## Security Best Practices

1. **Token Storage**: Never commit tokens to version control
2. **Token Rotation**: Regularly rotate authentication tokens
3. **Network Security**: Use HTTPS for remote agents when possible
4. **Least Privilege**: Only enable agents you actively use
5. **Access Control**: Restrict Openclaw agent permissions appropriately

## Validation

The MCP server validates configuration on startup:

- At least one agent must be configured
- At least one agent must be enabled
- Each agent must have a URL and token

If validation fails, the server will start but log warnings.

## Troubleshooting

### "No agents configured"

Ensure your environment variables follow the correct naming pattern:
- ❌ `OPENCLAW_AGENT_NAME` (missing number)
- ❌ `OPENCLAW_AGENT1_NAME` (no underscore before number)
- ✅ `OPENCLAW_AGENT_1_NAME`

### Agent not responding

Check:
1. Agent is running: `curl http://localhost:18789/`
2. Token is correct
3. URL is accessible from MCP client
4. Firewall rules allow connections

### Wrong agent selected

Always specify the agent name explicitly in your requests. The bridge requires the `agent` parameter.
