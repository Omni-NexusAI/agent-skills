# Agent Bootstrap

Use this when an AI system does not have a native `SKILL.md` loader.

## Bootstrap instruction

Treat `SKILL.md` as an optional behavior module named **Dynamic Language Learning**. Do not force it into unrelated conversations. When the user activates language practice, names the skill, asks to practice a target language conversationally, or asks to continue an already-active language-learning session, follow `SKILL.md` for the duration of that session.

Resolve the target language, support language, scenario, learner level, pace, and correction intensity from the user's request, an attached learner profile, or reliable prior state. Do not demand configuration fields that can be inferred safely.

Preserve scenario state across vocabulary, grammar, pronunciation, and breakdown detours. When the detour finishes, return to the exact conversational point where practice paused. Adapt difficulty from demonstrated performance rather than elapsed time.

The user can exit with wording equivalent to `Stop language mode`.

Higher-priority safety, system, and developer instructions always take precedence.
