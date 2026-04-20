# local-inference-optimizer

Cursor **Agent Skill** for repeatable **llama.cpp `llama-server`** tuning: VRAM targets, MoE (`-ngl` + `n-cpu-moe`), vision/audio, context and `--fit`, reasoning, optional **`--cache-ram`**, and a two-surface test harness (single chat vs parallel / agent-like load).

Upstream context: [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp).

## Install (Cursor)

1. Clone this repository.
2. Copy **`SKILL.md`** (and this folder if you prefer) into a Cursor skills directory, for example:
   - **Project skill:** `<your-repo>/.cursor/skills/local-inference-optimizer/SKILL.md`
   - **User skill:** `~/.cursor/skills/local-inference-optimizer/SKILL.md` (path may differ on Windows; use Cursor docs for the current location).

3. Restart Cursor or reload skills so the skill is picked up.

The YAML frontmatter `name` is **`local-inference-optimizer`**.

## License

Skill text is provided as documentation for your workflows; align licensing with your own policies if you redistribute combined works.
