# 🧠 Agent Skills Monorepo

> Consolidated home for all agent skills — OpenClaw, Agent Zero, and Cursor compatible.

## 📋 Skill Catalog

| Skill | Directory | Description | Platform | Status |
|---|---|---|---|---|
| **Agent Workflow Rules** | `skills/agent-workflow-rules/` | Project-neutral engineering workflow, safety, delivery, and verification rules | Agent/Any | Active |
| **AI-Link Workflow Rules** | `skills/ai-link-workflow-rules/` | Cross-surface planning, implementation, and validation for the Unity XR client, bridge, and Agent Zero | Agent/Unity XR | Active |
| **3D Printing Workflow** | `skills/3d-printing-workflow/` | Prepare functional FDM prints, verify CAD-to-slicer handoffs, and deliver organized project files | Agent/3D Printing | Active |
| **Llama Router Hermes** | `skills/llama-router-hermes/` | Set up llama.cpp routers and connect agent frameworks through native API adapters, including Hermes Agent | Agent/Any | Active |
| **Storage Awareness** | `skills/storage-awareness/` | Assess storage impact and coordinate bounded writes, cleanup, and recovery safely | Agent/Any | Active |
| **DOX** | `skills/dox/` | Self-documenting AGENTS.md hierarchy with ambient read-before-edit and update-after-edit contracts | Agent/Any | Active |
| **Cursor Workflow Rules** | `skills/cursor-workflow-rules/` | Legacy platform-specific workflow rules | Cursor | Archived |
| **AgentZero Workflow Rules** | `skills/agentzero-workflow-rules/` | Legacy project-specific workflow rules | Agent Zero | Archived |
| **SimpleMem** | `skills/simplemem/` | Local memory storage with key-value persistence | OpenClaw | ✅ Stable |
| **Voice Messaging** | `skills/voice-messaging/` | Modular voice messaging with swappable STT/TTS providers | OpenClaw | ✅ Stable |
| **Initializer** | `skills/initializer/` | Agent synchronization and capability merging | Agent | ✅ Stable |
| **MCP Bridge** | `skills/mcp-bridge/` | Generic MCP server for communicating with OpenClaw agents | MCP/Any | ✅ Stable |
| **Local Inference Optimizer** | `skills/local-inference-optimizer/` | Repeatable llama-server tuning (VRAM, MoE, modalities, load tests) | Cursor | ✅ Stable |
| **Docker Cleanup** | `skills/docker-cleanup/` | Safe cleanup of Docker build waste without deleting intentional resources | Cursor/Any | ✅ Stable |

## 📁 Repository Structure

```
agent-skills/
├── README.md                    # This file
├── .gitignore
└── skills/
    ├── agent-workflow-rules/   # Project-neutral engineering workflow and safety
    ├── ai-link-workflow-rules/ # AI-Link cross-surface engineering workflow
    ├── 3d-printing-workflow/   # Functional FDM print preparation and delivery workflow
    ├── llama-router-hermes/    # llama.cpp router setup and agent framework adapters
    ├── storage-awareness/      # Storage impact, safety, and recovery workflow
    ├── simplemem/               # SimpleMem skill
    ├── voice-messaging/         # Voice Messaging skill
    ├── initializer/             # Initializer skill
    ├── mcp-bridge/              # MCP Bridge server
    ├── dox/                     # AGENTS.md hierarchy framework
    ├── local-inference-optimizer/  # Inference Optimizer skill
    └── docker-cleanup/          # Docker cleanup skill
```

## 🚀 Usage

Each skill is self-contained in its own directory. To use a skill:

1. Navigate to the skill directory
2. Read the `SKILL.md` for setup instructions
3. Follow the skill-specific configuration steps

```bash
# Example: Set up SimpleMem
cd skills/simplemem
cat SKILL.md
```

## 📝 Skill Standard

Skills follow the [agentskills.io](https://agentskills.io) standard:

- `SKILL.md` — Core skill definition, metadata, and instructions
- `CONFIG.md` — Configuration options and environment variables
- `EXAMPLES.md` — Usage examples and patterns
- `scripts/` — Executable scripts and tools
- `src/` — Source code for complex skills

## 📜 License

Individual skills may have their own license files. See each skill's directory for details.

---

*Migrated from individual repositories on 2026-04-20*
