# General Agent Configuration Template

This is the **DEFAULT** template for agent configuration. It includes the integrated **two-sided hemisphere brain architecture** as the core design.

## Core Configuration

```json
{
  "name": "{{agent_name}}",
  "type": "brain",
  "version": "1.0.0",
  "description": "General-purpose agent brain with secure/utility hemisphere split"
}
```

## Brain Architecture (INTEGRATED - DEFAULT)

### Default Two-Sided Hemisphere Brain

```json
{
  "brain": {
    "type": "hemisphere",
    "architecture": "two-sided",
    "hemispheres": {
      "secure": {
        "name": "Secure Hemisphere",
        "role": "High-freedom processing within sandbox",
        "isolation": "full",
        "system_access": false,
        "internet_access": "restricted",
        "sandbox": true,
        "capabilities": [
          "web_analysis",
          "memory_management",
          "content_generation",
          "data_processing",
          "automation"
        ],
        "permissions": {
          "read": "within_sandbox",
          "write": "within_sandbox",
          "execute": "within_sandbox"
        },
        "environment": {
          "filesystem": "sandboxed",
          "network": "filtered",
          "process": "isolated"
        }
      },
      "utility": {
        "name": "Utility Hemisphere",
        "role": "System operations and external communication",
        "isolation": "none",
        "system_access": true,
        "internet_access": "full",
        "sandbox": false,
        "capabilities": [
          "file_operations",
          "network_access",
          "system_commands",
          "external_api_calls",
          "service_integrations"
        ],
        "permissions": {
          "read": "full",
          "write": "restricted",
          "execute": "restricted"
        },
        "environment": {
          "filesystem": "native",
          "network": "unrestricted",
          "process": "shared"
        }
      }
    },
    "synchronization": {
      "method": "request_response",
      "frequency": "on_demand",
      "consistency": "eventual",
      "message_format": "json",
      "protocol": "http"
    },
    "communication": {
      "pattern": "direct",
      "routing": "hemisphere_to_hemisphere",
      "timeout": 30,
      "retry_policy": {
        "max_retries": 3,
        "backoff": "exponential"
      }
    }
  }
}
```

## Capabilities Configuration

```json
{
  "capabilities": {
    "web": {
      "enabled": true,
      "browsing": {
        "enabled": true,
        "agent": "secure",
        "tools": ["browser", "scraper"]
      },
      "scraping": {
        "enabled": true,
        "agent": "secure",
        "tools": ["scraper", "parser"]
      }
    },
    "file_system": {
      "enabled": true,
      "operations": {
        "read": {
          "enabled": true,
          "agent": "utility",
          "scope": "selected_directories"
        },
        "write": {
          "enabled": true,
          "agent": "utility",
          "scope": "designated_areas"
        },
        "execute": {
          "enabled": true,
          "agent": "utility",
          "scope": "authorized_scripts"
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
      },
      "agent": "secure"
    },
    "automation": {
      "enabled": true,
      "scripts": true,
      "scheduling": true,
      "tasks": true,
      "parallel": true,
      "agent": "secure"
    },
    "analysis": {
      "enabled": true,
      "depth": "full",
      "frameworks": ["openclaw", "langchain", "crewai"],
      "tools": ["analyzer", "inspector"],
      "agent": "secure"
    }
  }
}
```

## Security Configuration

```json
{
  "security": {
    "permission_model": "explicit",
    "encryption": {
      "enabled": true,
      "algorithm": "aes256",
      "key_management": "secure"
    },
    "audit_logging": {
      "enabled": true,
      "events": ["all"],
      "retention": "365d",
      "agent": "utility"
    },
    "access_control": {
      "enabled": true,
      "model": "role_based",
      "permissions": ["read", "write", "execute"]
    },
    "sandbox_configuration": {
      "secure_hemisphere": {
        "enabled": true,
        "isolation_level": "high",
        "network_restrictions": true,
        "filesystem_restrictions": true
      },
      "utility_hemisphere": {
        "enabled": false,
        "native_system_access": true
      }
    }
  }
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
      "port": 8080,
      "authentication": null
    },
    "firewall": {
      "enabled": true,
      "rules": [
        {
          "name": "allow_web_access",
          "direction": "outbound",
          "protocol": "http",
          "agent": "secure"
        },
        {
          "name": "block_internal_networks",
          "direction": "outbound",
          "protocol": "all",
          "agent": "secure"
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
      "enabled": true,
      "servers": []
    },
    "external_apis": {
      "enabled": true,
      "apis": [],
      "rate_limiting": true
    },
    "plugins": {
      "enabled": true,
      "channels": ["telegram", "whatsapp"],
      "actions": {
        "send_message": true
      }
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
      "storage": "centralized",
      "cache": {
        "enabled": true,
        "size": "2GB"
      }
    },
    "processing": {
      "mode": "centralized",
      "parallel": true,
      "limits": {
        "cpu": "80%",
        "memory": "8GB"
      }
    },
    "storage": {
      "type": "hybrid",
      "local": {
        "path": "{{workspace}}/storage",
        "quota": "100GB"
      },
      "cloud": {
        "enabled": false,
        "provider": "",
        "bucket": ""
      }
    }
  }
}
```

## Variables

### Required Variables
- `{{agent_name}}` - Name of your agent brain
- `{{workspace}}` - Path to agent workspace directory

### Optional Variables
- `{{description}}` - Description of agent purpose
- `{{owner}}` - Agent owner/creator
- `{{version}}` - Configuration version

## Usage

### Applying the Template
```bash
# Apply with default settings
initializer template apply --type general --name my_agent_brain

# Apply with custom variables
initializer template apply --type general --name my_agent_brain \
  --variables "agent_name=MyBrain,description=General purpose AI brain"
```

### Customizing the Template
```bash
# Add custom capabilities
initializer template customize --type general --name my_agent_brain \
  --capabilities "custom_tool_1,custom_tool_2"

# Configure security settings
initializer template customize --type general --name my_agent_brain \
  --security "permission_model=strict,encryption=aes256"

# Set up network configuration
initializer template customize --type general --name my_agent_brain \
  --network "proxy_enabled=true,proxy_host=proxy.example.com"
```

## Common Use Cases

### 1. Research Assistant
```json
{
  "name": "Research_Assistant_Brain",
  "brain": {
    "secure": {
      "capabilities": ["web_analysis", "literature_review", "summarization"]
    },
    "utility": {
      "capabilities": ["file_operations", "citation_management"]
    }
  }
}
```

### 2. Content Creator
```json
{
  "name": "Content_Creator_Brain",
  "brain": {
    "secure": {
      "capabilities": ["content_generation", "editing", "quality_check"]
    },
    "utility": {
      "capabilities": ["web_scraping", "social_media_api", "file_operations"]
    }
  }
}
```

### 3. Data Analyst
```json
{
  "name": "Data_Analyst_Brain",
  "brain": {
    "secure": {
      "capabilities": ["data_processing", "analysis", "visualization"]
    },
    "utility": {
      "capabilities": ["database_access", "file_operations", "report_generation"]
    }
  }
}
```

## Notes

- **Brain architecture is integrated by default** - this is the core feature
- **Secure hemisphere** handles high-freedom processing within sandbox
- **Utility hemisphere** handles system operations and external communication
- **Synchronization** between hemispheres is automatic
- **Workflows** are preserved during merges unless explicitly modified
- **Customization** is possible without breaking the brain architecture

## Integration with Other Templates

This template can be combined with:
- **Specialized templates** - for industry-specific configurations
- **Solo agent template** - for single agent setup
- **Custom capabilities** - for additional functionality

The brain architecture remains central and integrated regardless of customizations.
