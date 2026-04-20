---
name: initializer
description: Synchronize and merge agent capabilities for networked agent-mind systems
metadata:
  {
    "openclaw":
      {
        "emoji": "🔗",
      },
  }
---

# Initializer Skill

This skill enables agents to synchronize and merge their capabilities, creating networked 'agent-mind' systems by synchronizing two agents acting as complementary brain hemispheres.

## Core Use Cases

### 1. Agent Synchronization
- **Two-Agent Synchronization**: Create networked 'agent-mind' by synchronizing two agents acting as complementary brain hemispheres
- **Single Agent Setup**: Can be used on just one agent, so the skill should adapt to this
- **Workflow Merging**: Users can merge two agents with similar or completely different pre-existing workflows
- **Workflow Preservation**: These workflows should not be overwritten during the merge
- **Explicit Permission**: Only if the user gives explicit permission should workflows be changed
- **Seamless Integration**: The merging procedure should integrate both workflows into one streamlined system

### 2. Agent Configuration
- **Setup Mode**: For building new agents from scratch
- **Merging Mode**: For combining existing agents with different workflows
- **Interview-Based Setup**: Three-stage interview process to understand user needs
- **Agent-Agnostic Design**: Works with internal and external agent instances
- **Future-Proof Design**: Adapts to different agent frameworks

### 3. Resource Management
- **Scripts**: Bootstrap browser access, get system permissions, analyze agent frameworks, setup external agents, create sandboxed agents
- **Templates**: General configuration, specialized configuration, brain architecture
- **Framework Analysis**: Analyze other agent codebases or communicate with them
- **Internet Bootstrap**: Help agents get internet access with minimal friction
- **Permission Configuration**: Help configure system permissions properly
- **External Agent Setup**: Allow single agent to bootstrap entire system with minimal friction
- **Resource Collection**: Agents can gather resources from internet or system to finish initialization

## Modes

### Building/Setup Mode
- For creating new agents from scratch
- Focuses on initial configuration and capability setup
- Uses interview questions to understand user requirements
- Provides templates and scripts for agent initialization

### Merging Mode
- For combining existing agents with different workflows
- Preserves existing workflows unless explicitly modified
- Integrates both workflows into one streamlined system
- Requires explicit user permission for any changes

## Interview Stage

### Stage 1: Mode Selection
**Question**: "Are you merging or building a new agent?"
- **Merging**: Proceed to workflow assessment
- **Building**: Proceed to capability setup

### Stage 2: Workflow Assessment
**Question**: "Do you have an existing workflow or stack?"
- **Yes**: Analyze existing workflows for integration
- **No**: Proceed to general needs assessment

### Stage 3: General Needs
**Questions**:
- "What capabilities do you need?"
- "What are your privacy and security requirements?"
- "Do you have any specific preferences or constraints?"

## Trigger Phrases

### Primary Trigger
- `/initializer`

### Secondary Triggers
- "communicate with another agent"
- "creating subagents"
- "setup or creating general workflows"

## Security & Privacy

### Workflow Preservation
- Existing workflows are never overwritten without explicit user permission
- The skill maintains the integrity of pre-existing agent configurations
- Only merges or integrates workflows when explicitly requested

### Permission Model
- All changes require explicit user consent
- The skill acts as a facilitator, not an autonomous modifier
- Users maintain full control over their agent configurations

### Data Handling
- No data is exfiltrated without user consent
- All operations are performed locally by default
- External agent communication requires explicit user approval

## Agent-Agnostic Design

### Compatibility
- Works with any OpenClaw-compatible agent
- Can communicate with external agent instances
- Adapts to different agent frameworks and architectures
- Future-proof design that evolves with agent technology

### Communication
- Standard protocols for agent-to-agent communication
- Plugin-based architecture for different agent types
- Automatic detection and adaptation to agent capabilities

## Resource Requirements

### Scripts
- **Browser Access**: Bootstrap browser capabilities for web interaction
- **Permission Management**: Configure system permissions and access rights
- **Framework Analysis**: Analyze and understand different agent frameworks
- **External Agent Setup**: Configure communication with external agents
- **Sandboxed Agent Creation**: Create isolated agent instances for testing

### Templates
- **General Configuration**: Basic agent setup templates
- **Specialized Configuration**: Industry-specific or use-case specific templates
- **Brain Architecture**: Templates for creating networked agent-mind systems

### Framework Support
- **Internal Analysis**: Analyze OpenClaw agent codebases
- **External Communication**: Communicate with non-OpenClaw agents
- **Protocol Translation**: Translate between different agent communication protocols

## Internet Bootstrap

### Connectivity
- **Minimal Friction**: Help agents get internet access with minimal setup
- **Configuration Management**: Handle proxy settings, authentication, and network configuration
- **Error Recovery**: Automatic recovery from connectivity issues

### Security
- **Secure Connection**: Use encrypted channels for internet communication
- **Authentication**: Handle API keys, tokens, and authentication mechanisms
- **Firewall Management**: Configure firewall rules for agent internet access

## Permission Configuration

### System Access
- **User Permissions**: Configure user-level permissions and access rights
- **System Integration**: Set up integration with system services and APIs
- **Security Context**: Maintain proper security context for agent operations

### External Access
- **API Keys**: Manage API keys and authentication tokens
- **Service Integration**: Configure access to external services and APIs
- **Data Privacy**: Ensure compliance with data privacy regulations

## External Agent Setup

### Single Agent Bootstrap
- **Minimal User Input**: Allow single agent to bootstrap entire system
- **Automatic Discovery**: Discover and configure external agent instances
- **Configuration Sync**: Synchronize configurations across agent instances

### Resource Collection
- **Internet Resources**: Gather resources from internet for agent initialization
- **System Resources**: Collect system resources for agent setup
- **Configuration Files**: Manage and distribute configuration files

## Use Cases

### New Agent Setup
1. User initiates `/initializer`
2. Skill asks interview questions
3. Skill provides appropriate templates and scripts
4. Agent is configured and ready for use

### Workflow Merging
1. User initiates `/initializer` with merging intent
2. Skill analyzes existing workflows
3. Skill integrates workflows with user permission
4. Unified workflow is created and tested

### Agent-Mind Creation
1. User initiates `/initializer` for brain creation
2. Skill sets up two complementary agents
3. Skill synchronizes capabilities and workflows
4. Networked agent-mind is operational

### Tool Integration
1. User initiates `/initializer` for tool setup
2. Skill analyzes available tools and APIs
3. Skill configures tool integration
4. Agent gains new capabilities

## Installation

### Prerequisites
- Agent system with skill/extension support
- Network connectivity for external agent communication
- Sufficient permissions for system integration

### Installation Command
```bash
openclaw skills install https://github.com/Omni-NexusAI/initializer.git
```

### Configuration
- Edit `CONFIG.md` for custom settings
- Configure `TEMPLATES/` for organization-specific templates
- Set up `SCRIPTS/` for custom automation

## Documentation

### Main Documentation
- [README.md](README.md) - This file
- [CONFIG.md](CONFIG.md) - Configuration options
- [EXAMPLES.md](EXAMPLES.md) - Usage examples

### Technical Documentation
- [SCRIPTS/](SCRIPTS/) - Available scripts and their usage
- [TEMPLATES/](TEMPLATES/) - Configuration templates
- [API.md](API.md) - API documentation for external integration

## Support

### Issues
- Report issues on the GitHub repository
- Include detailed error messages and reproduction steps
- Check existing issues before creating new ones

### Community
- Join the OpenClaw Discord for community support
- Participate in discussions and share experiences
- Contribute to the skill development

## Contributing

### Development
- Fork the repository
- Create a feature branch
- Add tests for new functionality
- Submit a pull request

### Documentation
- Update documentation for new features
- Add examples for different use cases
- Maintain clear and comprehensive documentation

## License

This skill is released under the MIT License. See [LICENSE](LICENSE) for details.