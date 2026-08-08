# 🧠 Agent Skills Monorepo

> Consolidated home for all agent skills — OpenClaw, Agent Zero, and Cursor compatible.

## 📋 Skill Catalog

| Skill | Directory | Description | Platform | Status |
|---|---|---|---|---|
| **Agent Workflow Rules** | `skills/agent-workflow-rules/` | Project-neutral engineering workflow, safety, delivery, and verification rules | Agent/Any | Active |
| **DOX** | `skills/dox/` | Self-documenting AGENTS.md hierarchy with ambient read-before-edit and update-after-edit contracts | Agent/Any | Active |
| **Dynamic Language Learning** | `skills/dynamic-language-learning/` | Adaptive scenario-based language practice with quick assists, deep breakdowns, pronunciation support, and progressive immersion | Agent/Any | Active |
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
    ├── simplemem/               # SimpleMem skill
    ├── voice-messaging/         # Voice Messaging skill
    ├── initializer/             # Initializer skill
    ├── mcp-bridge/              # MCP Bridge server
    ├── dox/                     # AGENTS.md hierarchy framework
    ├── dynamic-language-learning/  # Adaptive scenario-based language tutor
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