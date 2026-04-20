# Interview Stage Templates

This document contains templates for the three-stage interview process used during agent initialization.

## Stage 1: Mode Selection

### Primary Question Template
```
"Are you merging or building a new agent?"

Options:
- Merging: Combining existing agents with different workflows
- Building: Creating new agents from scratch
```

### Follow-up Questions

#### For Merging Mode
- "How many agents are you merging?"
- "What are the primary capabilities you want to preserve?"
- "Do you want to maintain separate agent personalities or merge them?"

#### For Building Mode
- "Are you setting up a single agent or creating a two-agent brain system?"
- "Do you want to start with a solo agent that can later be expanded?"

### Decision Tree
```
Stage 1: Mode Selection
├── Merging
│   ├── Single Agent Merge
│   └── Multi-Agent Merge
└── Building
    ├── Solo Agent
    └── Two-Agent Brain System
        ├── Secure Hemisphere + Utility Hemisphere (Default)
        └── Custom Brain Architecture
```

## Stage 2: Workflow Assessment

### Primary Question Template
```
"Do you have an existing workflow or stack you'd like to use?"

Options:
- Yes: I have existing agents/workflows to integrate
- No: Starting from scratch with no existing workflows
```

### For "Yes" Response

#### Workflow Discovery Questions
```
1. What framework(s) are your existing agents using?
   - OpenClaw
   - LangChain
   - CrewAI
   - Other

2. Where are your existing configurations located?
   - Local filesystem
   - Git repository
   - Cloud storage
   - Provide path/URL

3. What capabilities do your existing agents currently have?
   - Web access
   - File operations
   - Memory management
   - Automation
   - Analysis

4. Are there specific workflows you want to preserve?
   - Yes: List workflows
   - No: Merge everything into unified system
```

#### Compatibility Check
```
Checking compatibility between frameworks...

Compatibility Report:
- Framework A: OpenClaw
- Framework B: LangChain
- Compatibility: High
- Integration Method: Python SDK + MCP

Are you ready to proceed with this integration?
```

### For "No" Response

#### General Needs Assessment
```
Since you're starting from scratch, let's discuss what you need.

1. What are your primary use cases?
   - Data analysis and processing
   - Web automation and scraping
   - Content creation
   - System administration
   - Other: ____________

2. What type of capabilities do you need?
   - Web access (browsing, scraping)
   - File operations (read, write, execute)
   - Memory management (storage, retrieval)
   - Automation (scripts, tasks)
   - Analysis (data processing, insights)

3. What are your scale requirements?
   - Personal use (single user)
   - Team collaboration (2-10 users)
   - Enterprise (10+ users)
   - High throughput (processing large volumes)
```

## Stage 3: General Needs

### Security and Privacy Questions
```
1. What are your privacy and security requirements?
   - High sensitivity (maximum isolation, no external access)
   - Medium security (balanced security and utility)
   - Low security (development/testing, minimal restrictions)

2. Do you need to handle sensitive data?
   - Yes: What types?
     - Personal information (PII)
     - Financial data
     - Healthcare data
     - Intellectual property
     - Other: ____________
   - No: No sensitive data processing

3. What compliance requirements do you have?
   - None
   - GDPR (General Data Protection Regulation)
   - HIPAA (Health Insurance Portability and Accountability Act)
   - SOX (Sarbanes-Oxley Act)
   - Industry-specific regulations
   - Other: ____________
```

### Capability Questions
```
1. What capabilities do you need in your agent(s)?
   Select all that apply:
   ☐ Web browsing and scraping
   ☐ File system operations
   ☐ Memory management (persistent storage)
   ☐ Task automation
   ☐ Data analysis and insights
   ☐ API integrations
   ☐ Database access
   ☐ Cloud services
   ☐ Machine learning/AI
   ☐ Other: ____________

2. What performance requirements do you have?
   - Response time (latency): ______ ms
   - Throughput: ______ requests/second
   - Concurrent users/agents: ______
   - Data volume: ______ GB/TB
```

### Preferences and Constraints
```
1. Do you have any specific preferences?
   - Programming language preference: ______
   - Framework preference: ______
   - Hosting environment: ______
   - Budget constraints: ______
   - Timeline: ______

2. Are there any technical constraints?
   - Hardware limitations: ______
   - Network restrictions: ______
   - Storage limitations: ______
   - Other: ______
```

### Brain Architecture Questions (if two-agent system)
```
Since you're creating a two-agent brain system:

1. What security/utility split do you prefer?
   - Default: Secure hemisphere (sandboxed) + Utility hemisphere (system access)
   - Custom: Specify your preferred configuration

2. How should the hemispheres synchronize?
   - Real-time (continuous communication)
   - Event-driven (communicate on state changes)
   - Request-response (explicit communication)
   - Other: ____________

3. What communication pattern do you prefer?
   - Secure ↔ Utility (direct communication)
   - Secure → Utility → Secure (through coordinator)
   - Pub/sub (event-based)
   - Other: ____________
```

## Integration Templates

### Solo Agent Interview Flow
```
Stage 1: Mode Selection
→ Building → Solo Agent

Stage 2: Workflow Assessment
→ No existing workflows → General needs

Stage 3: General Needs
→ Capabilities, security, preferences

Result: Solo agent configuration
```

### Two-Agent Brain Interview Flow
```
Stage 1: Mode Selection
→ Building → Two-Agent Brain System

Stage 2: Workflow Assessment
→ No existing workflows → General needs

Stage 3: General Needs
→ Brain architecture questions
→ Security/utility split
→ Synchronization pattern

Result: Two-agent brain configuration
```

### Agent Merging Interview Flow
```
Stage 1: Mode Selection
→ Merging

Stage 2: Workflow Assessment
→ Yes existing workflows
→ Framework compatibility check
→ Workflow preservation

Stage 3: General Needs
→ Integration preferences
→ Security consolidation

Result: Merged agent configuration
```

## Question Bank

### General Purpose Questions
- What problem are you trying to solve with this agent system?
- Who will be using this agent system?
- What are your success criteria?
- How do you plan to maintain and update this system?

### Technical Questions
- What infrastructure are you running on?
- Do you have existing databases or services to integrate?
- What programming languages and frameworks are you comfortable with?
- Do you need support for specific protocols or APIs?

### Business Questions
- What is your budget for this project?
- What is your timeline for implementation?
- Are there regulatory or compliance requirements?
- How do you plan to measure success?

### Risk Management Questions
- What are your biggest concerns with this implementation?
- What happens if the system goes down?
- How will you handle data loss or corruption?
- What are your disaster recovery plans?

## Adaptive Interview Logic

### Branching Logic
```
IF user selects "Merging":
    → Ask about existing frameworks
    → Check compatibility
    → Preserved workflows question
    → Integration method

IF user selects "Building":
    → Ask about agent count (solo vs brain)
    IF "Two-Agent Brain":
        → Ask about brain architecture
        → Security/utility split
        → Synchronization pattern
    ELSE "Solo Agent":
        → Skip brain questions
        → Proceed to general needs

IF user has existing workflows:
    → Ask about workflow preservation
    → Customization preferences
    → Integration strategy

IF user has no existing workflows:
    → General needs assessment
    → Capability requirements
    → Security requirements
```

### Adaptive Difficulty
```
Beginner Mode:
- Simplified language
- Fewer technical questions
- Recommended defaults

Intermediate Mode:
- Standard questions
- Some technical details
- Customization options

Expert Mode:
- Detailed technical questions
- Full customization
- Advanced features
```

## Response Templates

### Confirmation Template
```
Great! Based on your answers, I'll configure your agent system with the following:

Configuration Summary:
- Mode: [Merging/Building]
- Agent Type: [Solo/Two-Agent Brain]
- Capabilities: [List]
- Security Level: [High/Medium/Low]
- Estimated Setup Time: [Time]

Does this look correct?
- Yes: Proceed with setup
- No: Let me adjust
```

### Progress Template
```
Setting up your agent system...

Progress:
[█░░░░░░░░░] 10% - Analyzing requirements
[███░░░░░░░] 30% - Configuring agents
[█████░░░░░] 50% - Setting up capabilities
[███████░░░░] 70% - Configuring security
[██████████░░] 90% - Finalizing configuration
[███████████] 100% - Complete!

Your agent system is ready to use.
```

### Error Template
```
I encountered an issue during setup:

Error: [Description]
Location: [Where it occurred]
Impact: [What this affects]

Options:
- Retry: Try this step again
- Skip: Skip this optional step
- Manual: I'll provide manual instructions
- Abort: Cancel the setup

What would you like to do?
```

## Best Practices

### 1. Clear and Concise
- Use simple language
- Avoid technical jargon
- Provide examples

### 2. Progressive Disclosure
- Start with high-level questions
- Drill down to details as needed
- Don't overwhelm the user

### 3. Flexibility
- Allow users to skip questions
- Provide sensible defaults
- Enable easy modifications

### 4. Validation
- Check for completeness
- Validate user responses
- Catch errors early

### 5. Feedback
- Show progress
- Provide confirmation
- Explain next steps
