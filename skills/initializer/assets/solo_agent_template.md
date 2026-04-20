# Solo Agent Configuration Template

This template is for **solo agent architecture** when building an agent without initially incorporating another agent. This is a single-agent setup that can later be expanded into a brain architecture.

## Core Configuration

```json
{
  "name": "{{agent_name}}",
  "type": "solo",
  "version": "1.0.0",
  "description": "Single agent configuration (expandable to brain architecture)"
}
```

## Solo Agent Architecture

### Single Agent Design

```json
{
  "brain": {
    "type": "solo",
    "mode": "single_agent",
    "expandable": true,
    "expansion_path": "brain_architecture",
    "architecture": "centralized",
    "agent": {
      "name": "{{agent_name}}",
      "role": "General-purpose agent",
      "capabilities": [],
      "isolation": "configurable",
      "system_access": "configurable",
      "sandbox": "configurable"
    },
    "synchronization": {
      "enabled": false,
      "note": "Synchronization becomes available when expanded to brain architecture"
    }
  }
}
```

### Expansion to Brain Architecture

The solo agent can be expanded to a brain architecture later:

```json
{
  "expansion_options": {
    "to_two_agent_brain": {
      "description": "Convert to secure + utility hemisphere split",
      "steps": [
        "Create secure hemisphere",
        "Create utility hemisphere",
        "Migrate capabilities",
        "Configure synchronization"
      ],
      "automatic": true
    },
    "to_multi_hemisphere_brain": {
      "description": "Convert to multi-sided hemisphere brain",
      "steps": [
        "Define hemisphere roles",
        "Create hemisphere agents",
        "Configure communication",
        "Set up synchronization"
      ],
      "automatic": false
    }
  }
}
```

## Capabilities Configuration

### Standard Solo Agent Capabilities

```json
{
  "capabilities": {
    "web": {
      "enabled": true,
      "browsing": {
        "enabled": true,
        "tools": ["browser"],
        "headless": true,
        "timeout": 30
      },
      "scraping": {
        "enabled": true,
        "tools": ["scraper", "parser"],
        "rate_limiting": true
      }
    },
    "file_system": {
      "enabled": true,
      "operations": {
        "read": {
          "enabled": true,
          "scope": "{{read_scope}}",
          "default": "user_directory"
        },
        "write": {
          "enabled": true,
          "scope": "{{write_scope}}",
          "default": "workspace_only"
        },
        "execute": {
          "enabled": false,
          "note": "Execute requires explicit permission"
        }
      }
    },
    "memory": {
      "enabled": true,
      "type": "persistent",
      "storage": "local",
      "cache": {
        "enabled": true,
        "size": "1GB",
        "strategy": "least_recently_used"
      }
    },
    "automation": {
      "enabled": true,
      "scripts": true,
      "scheduling": false,
      "tasks": true,
      "parallel": false
    },
    "analysis": {
      "enabled": true,
      "depth": "full",
      "frameworks": ["openclaw"],
      "tools": ["analyzer"]
    }
  }
}
```

### Optional Advanced Capabilities

```json
{
  "advanced_capabilities": {
    "ml_processing": {
      "enabled": false,
      "models": [],
      "local": true,
      "note": "Enable for machine learning capabilities"
    },
    "external_apis": {
      "enabled": false,
      "apis": [],
      "rate_limiting": true,
      "note": "Enable for external API integrations"
    },
    "database_access": {
      "enabled": false,
      "databases": [],
      "connection_pooling": true,
      "note": "Enable for database integrations"
    },
    "messaging": {
      "enabled": false,
      "channels": [],
      "notification": false,
      "note": "Enable for messaging capabilities"
    }
  }
}
```

## Security Configuration

### Standard Solo Agent Security

```json
{
  "security": {
    "permission_model": "explicit",
    "encryption": {
      "enabled": true,
      "algorithm": "aes256",
      "key_management": "standard"
    },
    "audit_logging": {
      "enabled": true,
      "events": ["important"],
      "retention": "90d"
    },
    "access_control": {
      "enabled": true,
      "model": "basic",
      "permissions": ["read", "write"]
    },
    "sandbox": {
      "enabled": false,
      "note": "Sandbox can be enabled for enhanced security"
    }
  }
}
```

### Security Levels

#### Level 1: Standard (Default)
```json
{
  "security_level": "standard",
  "isolation": "minimal",
  "system_access": "limited",
  "internet_access": "filtered",
  "sandbox": false
}
```

#### Level 2: Enhanced
```json
{
  "security_level": "enhanced",
  "isolation": "medium",
  "system_access": "restricted",
  "internet_access": "filtered",
  "sandbox": true
}
```

#### Level 3: Maximum
```json
{
  "security_level": "maximum",
  "isolation": "full",
  "system_access": false,
  "internet_access": "restricted",
  "sandbox": true
}
```

## Network Configuration

```json
{
  "network": {
    "internet_access": true,
    "proxy": {
      "enabled": false,
      "host": "",
      "port": 8080
    },
    "firewall": {
      "enabled": true,
      "rules": [
        {
          "name": "allow_web_access",
          "direction": "outbound",
          "protocol": "http"
        }
      ]
    },
    "dns": {
      "servers": ["8.8.8.8", "8.8.4.4"]
    }
  }
}
```

## Integration Configuration

```json
{
  "integration": {
    "mcp_servers": {
      "enabled": false,
      "servers": []
    },
    "external_apis": {
      "enabled": false,
      "apis": []
    },
    "plugins": {
      "enabled": false,
      "channels": []
    }
  }
}
```

## Resource Configuration

```json
{
  "resources": {
    "memory": {
      "type": "persistent",
      "storage": "local",
      "cache": {
        "enabled": true,
        "size": "1GB"
      }
    },
    "processing": {
      "mode": "single",
      "parallel": false,
      "limits": {
        "cpu": "50%",
        "memory": "4GB"
      }
    },
    "storage": {
      "type": "local",
      "path": "{{workspace}}/storage",
      "quota": "50GB"
    }
  }
}
```

## Variables

### Required Variables
- `{{agent_name}}` - Name of your solo agent
- `{{workspace}}` - Path to agent workspace directory

### Optional Variables
- `{{description}}` - Description of agent purpose
- `{{read_scope}}` - File read scope (user_directory, workspace_only, selected_directories)
- `{{write_scope}}` - File write scope (workspace_only, selected_directories)
- `{{security_level}}` - Security level (standard, enhanced, maximum)

## Usage

### Creating a Solo Agent
```bash
# Create with default settings
initializer template apply --type solo --name my_agent

# Create with custom capabilities
initializer template apply --type solo --name my_agent \
  --capabilities "web,file,memory"

# Create with enhanced security
initializer template apply --type solo --name my_agent \
  --security_level enhanced

# Create with specific file scopes
initializer template apply --type solo --name my_agent \
  --scopes "read=user_directory,write=workspace_only"
```

### Customizing Solo Agent
```bash
# Add advanced capabilities
initializer template customize --type solo --name my_agent \
  --advanced "ml_processing=true,external_apis=true"

# Configure file system access
initializer template customize --type solo --name my_agent \
  --file_access "read=selected_directories,write=workspace_only,execute=false"

# Set up integration
initializer template customize --type solo --name my_agent \
  --integration "mcp_servers=true,external_apis=false"

# Expand to brain architecture (when ready)
initializer template expand --type solo --name my_agent \
  --to "two_agent_brain"
```

## Common Solo Agent Use Cases

### 1. Research Assistant
```json
{
  "name": "Research_Assistant",
  "capabilities": {
    "web": {"enabled": true},
    "memory": {"enabled": true},
    "analysis": {"enabled": true}
  },
  "advanced_capabilities": {
    "ml_processing": {"enabled": true},
    "external_apis": {"enabled": true}
  }
}
```

### 2. Content Writer
```json
{
  "name": "Content_Writer",
  "capabilities": {
    "web": {"enabled": true},
    "file_system": {"enabled": true},
    "automation": {"enabled": true}
  }
}
```

### 3. Data Analyst
```json
{
  "name": "Data_Analyst",
  "capabilities": {
    "file_system": {"enabled": true},
    "memory": {"enabled": true},
    "analysis": {"enabled": true}
  },
  "advanced_capabilities": {
    "ml_processing": {"enabled": true},
    "database_access": {"enabled": true}
  }
}
```

### 4. Chatbot
```json
{
  "name": "Chatbot",
  "capabilities": {
    "memory": {"enabled": true},
    "automation": {"enabled": true}
  },
  "advanced_capabilities": {
    "messaging": {"enabled": true},
    "external_apis": {"enabled": true}
  }
}
```

## Expansion Path

### From Solo Agent to Brain Architecture

When you're ready to expand your solo agent to a brain architecture:

```bash
# Automatically convert to two-agent brain
initializer template expand --type solo --name my_agent \
  --to "two_agent_brain" \
  --automatic

This will:
1. Create secure hemisphere (migrates high-risk capabilities)
2. Create utility hemisphere (migrates system operations)
3. Configure synchronization between hemispheres
4. Preserve all existing configurations
```

### Manual Expansion Steps

If you want more control over the expansion:

```bash
# 1. Design your brain architecture
initializer template design --type brain \
  --hemispheres "secure,utility" \
  --customization true

# 2. Migrate capabilities
initializer capability migrate --from solo --to brain \
  --capability "web_analysis" --to "secure"

# 3. Set up synchronization
initializer synchronization configure --mode "request_response"

# 4. Test the expanded brain
initializer test --type brain --name my_brain_agent
```

## Comparison: Solo vs Brain Architecture

| Feature | Solo Agent | Brain Architecture |
|---------|-------------|-------------------|
| **Agents** | 1 | 2+ |
| **Isolation** | Configurable | Built-in (hemispheres) |
| **Synchronization** | N/A | Automatic |
| **Complexity** | Simple | Advanced |
| **Use Case** | Basic tasks | Complex workflows |
| **Expandability** | Easy to expand | Already expanded |
| **Security** | Single level | Multi-level |

## Notes

- **Solo agent is the starting point** - can be expanded later
- **Expandability is built-in** - designed for future expansion to brain architecture
- **Configurable security** - can be adjusted based on needs
- **All capabilities are optional** - enable only what you need
- **Minimal setup complexity** - fastest path to getting started
- **Preserves investment** - solo agent configuration is not lost during expansion

## When to Use Solo Agent Template

**Use this template when:**
- You're getting started with a single agent
- You want to test basic capabilities
- You need a simple setup quickly
- You plan to expand to brain architecture later
- You want to understand agent capabilities first

**Use brain architecture templates when:**
- You need multiple specialized agents
- You require built-in isolation and synchronization
- You have complex workflow requirements
- You need advanced security separation
- You're building a production system

This template provides a solid foundation for solo agent development with a clear path to brain architecture expansion when needed.
