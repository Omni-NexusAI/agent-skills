# 🧠 Agent Skills Monorepo

> Consolidated home for all agent skills — OpenClaw, Agent Zero, and Cursor compatible.

## 📋 Skill Catalog

| Skill | Directory | Description | Platform | Status |
|---|---|---|---|---|
| **SimpleMem** | `skills/simplemem/` | Local memory storage with key-value persistence | OpenClaw | ✅ Stable |
| **Voice Messaging** | `skills/voice-messaging/` | Modular voice messaging with swappable STT/TTS providers | OpenClaw | ✅ Stable |
| **Initializer** | `skills/initializer/` | Agent synchronization and capability merging | Agent | ✅ Stable |
| **MCP Bridge** | `skills/mcp-bridge/` | Generic MCP server for communicating with OpenClaw agents | MCP/Any | ✅ Stable |
| **Local Inference Optimizer** | `skills/local-inference-optimizer/` | Repeatable llama-server tuning (VRAM, MoE, modalities, load tests) | Cursor | ✅ Stable |

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
    └── local-inference-optimizer/  # Inference Optimizer skill
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
