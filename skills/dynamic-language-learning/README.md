# Dynamic Language Learning Skill

A portable `SKILL.md` for scenario-based, adaptive language practice with conversational continuity.

## What it does

The skill gives an AI agent a consistent protocol for:

- realistic role-play scenarios;
- dynamic target-language/support-language switching;
- quick vocabulary assists that do not derail the scene;
- deep phrase/grammar breakdowns when requested;
- pronunciation practice;
- selective correction instead of correcting every error;
- automatic difficulty and speaking-speed progression;
- returning to the exact conversation point after teaching detours;
- recycling new vocabulary and grammar in later turns.

## Portable installation

Place `SKILL.md` in whatever skill/instruction mechanism your agent framework supports. Frameworks that recognize Markdown skills with YAML frontmatter can generally use it directly. Other agents can treat the entire file as a behavior module or system/developer instruction.

If your framework supports per-user or per-language configuration, pair the skill with a learner profile such as the example under `profiles/`. If it does not natively load `SKILL.md` files, use `AGENT_BOOTSTRAP.md` as the small adapter instruction.

## Activation examples

- `Activate dynamic language learning: Russian.`
- `Practice Japanese. Scenario: checking into a hotel.`
- `Continue language mode. More target language, but keep the pace slow.`
- `Break that sentence down.`
- `Quick word: how do I say “release date”?`
- `Resume.`

## ChatGPT Project use

Add `SKILL.md` as a Project source/instruction file, then invoke it by name or by an activation phrase such as `Activate dynamic language learning: <language>`.

The file is intentionally self-contained so the behavioral contract travels with it.
