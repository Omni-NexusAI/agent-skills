# Usage Examples

## Basic Usage

### List Available Agents

Ask your MCP client:
```
List available Openclaw agents
```

The agent will call `list_openclaw_agents()` and show:
```
Configured Openclaw Agents:
========================================

docker:
  Status: ✅ enabled
  URL: http://host.docker.internal:18789
  Endpoint: /v1/chat/completions

native:
  Status: ✅ enabled
  URL: http://localhost:19789
  Endpoint: /v1/chat/completions
```

### Send a Simple Message

```
Ask the docker agent to check system status
```

This calls:
```python
call_openclaw(
    instruction="Check system status",
    agent="docker"
)
```

### Use Native Agent

```
Use the native agent to list files in my workspace
```

This calls:
```python
call_openclaw(
    instruction="List files in workspace",
    agent="native"
)
```

## With File Attachments

### Attach a Single File

```
Ask the docker agent to review this file: /path/to/code.py
```

This calls:
```python
call_openclaw(
    instruction="Review this file and suggest improvements",
    agent="docker",
    attachments=["/path/to/code.py"]
)
```

### Attach Multiple Files

```
Compare these two files and tell me the differences:
- /path/to/file1.txt
- /path/to/file2.txt
```

This calls:
```python
call_openclaw(
    instruction="Compare these two files and tell me the differences",
    agent="docker",
    attachments=["/path/to/file1.txt", "/path/to/file2.txt"]
)
```

### Code Review with Context

```
Review my project configuration. I've attached:
- package.json
- requirements.txt
- README.md
```

This calls:
```python
call_openclaw(
    instruction="""Review my project configuration and suggest improvements for:
1. Dependencies - are they up to date?
2. Documentation - is the README clear?
3. Best practices - any security or performance issues?""",
    agent="docker",
    attachments=[
        "/path/to/package.json",
        "/path/to/requirements.txt",
        "/path/to/README.md"
    ]
)
```

## Advanced Usage

### Long-Running Tasks

```
Ask the docker agent to run a comprehensive security audit on my codebase
```

The default timeout is 120 seconds. For longer tasks, increase timeout in configuration:
```json
"OPENCLAW_AGENT_1_TIMEOUT": "600"  // 10 minutes
```

### Switch Between Agents

```
First, ask the docker agent to install Node.js. Then ask the native agent to verify the installation.
```

This demonstrates using different agents for different tasks.

### Error Handling

If an agent is not available:
```
Ask the production agent to deploy the app
```

Response:
```
Error: Agent 'production' not found. Available agents: docker, native
```

## Common Workflows

### Development Workflow

1. **Check environment:**
   ```
   Ask the docker agent to check what tools are installed
   ```

2. **Review code:**
   ```
   Ask the docker agent to review /path/to/myfile.py for bugs
   ```

3. **Run tests:**
   ```
   Ask the docker agent to run the test suite
   ```

4. **Deploy:**
   ```
   Ask the native agent to deploy to staging
   ```

### System Administration

1. **Monitor system:**
   ```
   Ask the native agent to check disk usage and memory
   ```

2. **Update packages:**
   ```
   Ask the docker agent to update all npm packages
   ```

3. **Backup:**
   ```
   Ask the native agent to create a backup of the database
   ```

### Multi-Agent Coordination

```
I need to set up a new project. 

1. First, ask the docker agent to create a new Node.js project structure
2. Then ask the native agent to initialize a git repository
3. Finally, ask the docker agent to install the required dependencies
```

## Tips for Best Results

### Be Specific

❌ **Vague:**
```
Ask the agent to fix my code
```

✅ **Specific:**
```
Ask the docker agent to fix the syntax error in /path/to/file.py at line 45
```

### Provide Context

❌ **Minimal:**
```
Ask the agent to review this
```

✅ **With Context:**
```
Ask the docker agent to review this Python function. I need to ensure it handles edge cases properly and follows PEP 8 style guidelines.
```

### Use Attachments Wisely

- Attach relevant files only
- Text files work best
- Large files may timeout
- Binary files are not supported

### Handle Timeouts

If a task times out:
1. Check if the agent is still running
2. Increase timeout in configuration
3. Break the task into smaller steps

## Example Conversations

### Conversation 1: Code Review

**User:** Ask the docker agent to review my Python script: /home/user/script.py

**Agent:** I'll review that Python script for you.

*[Calls call_openclaw with attachment]*

**Openclaw:** I've reviewed your script. Here are my findings:
- Line 12: Unused import 'json'
- Line 25: Potential division by zero
- Line 40: Consider using list comprehension
...

### Conversation 2: System Check

**User:** Check system resources using the native agent

**Agent:** Let me check your system resources.

*[Calls call_openclaw]*

**Openclaw:** System Status:
- CPU: 45% usage
- Memory: 8.2GB / 16GB (51%)
- Disk: 120GB / 500GB free
- Load average: 0.85
...

### Conversation 3: Multi-step Task

**User:** I need to analyze these logs and create a summary:
- /var/log/app/error.log
- /var/log/app/access.log

**Agent:** I'll analyze both log files and create a summary for you.

*[Calls call_openclaw with both attachments]*

**Openclaw:** Log Analysis Summary:
**Error Log:**
- 45 errors found
- Most common: Connection timeout (23 occurrences)
- Latest error: 2026-02-08 14:30:22

**Access Log:**
- 1,234 requests
- 99.2% success rate
- Peak traffic: 14:00-15:00
...
