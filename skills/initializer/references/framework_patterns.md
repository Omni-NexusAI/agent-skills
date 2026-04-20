# Framework Patterns Reference

This document describes common patterns for different agent frameworks to facilitate integration and compatibility.

## OpenClaw Patterns

### Core Architecture
```
Gateway (HTTP/WebSocket)
├── Sessions (agent instances)
├── Skills (extensions)
├── Plugins (channel integrations)
└── MCP Servers (tool integration)
```

### Communication Patterns
- **Session Messaging**: `sessions_send(sessionKey, message)`
- **Agent-to-Agent**: `agentToAgent` tool with `allow` list
- **Heartbeat**: Periodic polling for maintenance tasks
- **Cross-Session**: Inter-agent communication via session keys

### Configuration Patterns
```json
{
  "gateway": {
    "mode": "local|remote",
    "port": 18789,
    "bind": "127.0.0.1"
  },
  "agents": {
    "defaults": {
      "model": "model-id",
      "subagents": {
        "maxConcurrent": 8
      }
    }
  },
  "tools": {
    "agentToAgent": {
      "enabled": true,
      "allow": [""]
    }
  }
}
```

### Tool Integration
- **Native Tools**: Built-in (exec, browser, nodes, etc.)
- **MCP Servers**: External tool servers
- **Skills**: Extension capabilities
- **Plugins**: Channel-specific functionality

### Memory Patterns
- **Daily Notes**: `memory/YYYY-MM-DD.md`
- **Long-term**: `MEMORY.md` (main session only)
- **Workspace**: Project-specific files in `workspace/`

## LangChain Patterns

### Core Architecture
```
LangChain Core
├── Chains (sequence of operations)
├── Agents (decision-making entities)
├── Tools (external functions)
├── Prompts (template management)
└── Memory (context management)
```

### Communication Patterns
- **Chain Execution**: Sequential or parallel
- **Agent Coordination**: Shared memory, explicit routing
- **Tool Calling**: Function calling protocol
- **Streaming**: Incremental output

### Configuration Patterns
```python
from langchain.agents import AgentExecutor, create_openai_agent
from langchain.tools import Tool

tools = [
    Tool(
        name="calculator",
        func=lambda x: eval(x),
        description="Useful for math calculations"
    )
]

agent = create_openai_agent(llm, tools)
executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True
)
```

### Memory Patterns
- **ConversationBufferMemory**: Recent exchanges
- **ConversationSummaryMemory**: Summarized history
- **VectorStoreMemory**: Retrieval-based
- **Shared Memory**: Multi-agent coordination

## CrewAI Patterns

### Core Architecture
```
Crew
├── Agents (specialized workers)
├── Tasks (specific objectives)
├── Tools (agent capabilities)
└── Process (task orchestration)
```

### Communication Patterns
- **Hierarchical**: Manager-agent structure
- **Sequential**: Task-to-task handoff
- **Collaborative**: Shared task context
- **Parallel**: Concurrent task execution

### Configuration Patterns
```python
from crewai import Agent, Task, Crew

researcher = Agent(
    role='Researcher',
    goal='Gather information',
    backstory='Expert in data collection',
    tools=[search_tool, file_tool]
)

task = Task(
    description='Research topic',
    agent=researcher,
    expected_output='Detailed report'
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[task],
    process=Process.sequential
)
```

### Coordination Patterns
- **Task Delegation**: Agents assign tasks
- **Context Sharing**: Shared task context
- **Role Specialization**: Domain-specific agents
- **Process Control**: Sequential vs parallel execution

## Generic Agent Framework Patterns

### Common Patterns Across Frameworks

#### 1. Tool/Function Calling
```json
{
  "tool_calling": {
    "protocol": "openapi|mcp|custom",
    "schema": "json_schema",
    "registration": "auto|manual",
    "execution": "sync|async"
  }
}
```

#### 2. Memory Management
```json
{
  "memory": {
    "type": "short_term|long_term|hybrid",
    "storage": "local|distributed|cloud",
    "retrieval": "vector|keyword|hybrid",
    "persistence": true
  }
}
```

#### 3. Agent Communication
```json
{
  "communication": {
    "mode": "direct|broker|pubsub",
    "protocol": "http|websocket|grpc",
    "message_format": "json|protobuf",
    "routing": "explicit|discovery"
  }
}
```

#### 4. Configuration Management
```json
{
  "configuration": {
    "format": "json|yaml|toml",
    "schema": "openapi|custom",
    "validation": "runtime|loadtime",
    "profiles": ["development", "production"]
  }
}
```

## Integration Patterns

### Pattern 1: HTTP REST API
- **OpenClaw**: Gateway HTTP endpoint
- **LangChain**: Serve via FastAPI/Flask
- **CrewAI**: Task result API

### Pattern 2: WebSocket Real-time
- **OpenClaw**: Gateway WebSocket
- **LangChain**: Streaming responses
- **CrewAI**: Task progress updates

### Pattern 3: Tool Function Calling
- **OpenClaw**: MCP servers
- **LangChain**: Tool definitions
- **CrewAI**: Agent tool assignments

### Pattern 4: Shared Memory
- **OpenClaw**: Session transcripts
- **LangChain**: Shared memory components
- **CrewAI**: Task context sharing

## Migration Patterns

### OpenClaw → LangChain
- **Sessions**: Convert to Agent instances
- **Tools**: Map to LangChain Tools
- **Skills**: Implement as custom tools
- **Memory**: Map to LangChain Memory

### LangChain → OpenClaw
- **Chains**: Convert to agent workflows
- **Tools**: Implement as MCP servers
- **Agents**: Create separate sessions
- **Memory**: Map to OpenClaw memory system

### CrewAI → OpenClaw
- **Crews**: Multi-session coordination
- **Agents**: Separate sessions with roles
- **Tasks**: Agent-assigned objectives
- **Tools**: MCP server implementations

## Anti-Patterns to Avoid

### 1. Tight Coupling
- Avoid framework-specific dependencies
- Use generic communication protocols
- Abstract framework differences

### 2. Direct Database Sharing
- Don't share database connections
- Use API-based communication
- Maintain data isolation

### 3. Blocking Calls
- Avoid synchronous blocking
- Use async communication
- Implement timeouts and retries

### 4. Memory Leaks
- Clean up resources
- Implement TTL for cached data
- Monitor memory usage

## Best Practices

### 1. Protocol Independence
- Support multiple communication protocols
- Allow protocol negotiation
- Implement fallback mechanisms

### 2. Graceful Degradation
- Handle missing capabilities
- Provide sensible defaults
- Document limitations

### 3. Observability
- Log framework interactions
- Track performance metrics
- Monitor error rates

### 4. Security
- Validate all inputs
- Sanitize outputs
- Implement rate limiting
