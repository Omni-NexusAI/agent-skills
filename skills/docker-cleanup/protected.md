# Docker Cleanup — Protected Names (Extra Safety Net)

The primary protection mechanism is the "build waste only" philosophy in the skill itself — all containers, named images, and referenced images are kept by default. This file is an **additional safety layer** for edge cases where you want to ensure something is never touched even if it somehow appears as a dangling or orphaned resource.

Claude reads this file before every cleanup run. Any image, container, or volume whose name or tag contains a pattern below (case-insensitive, substring match) will never be removed under any circumstances.

## Protected Patterns

```
a0
agentspine
qwen3tts
qwen-3-tts
qwen3-tts
openclaw
ainexus
ai-nexus
kokoro
open-terminal
open_terminal
```

## How to Update This List

To **add** a new protected item, add its name (or a unique substring) under the Protected Patterns section — one entry per line, inside the code block.

To **remove** protection, delete the line. The change takes effect on the next `/docker-cleanup` run.

**Tip:** Use the shortest unique substring that won't accidentally match unrelated images. For example, `myproject` protects `myproject-api`, `myproject-worker`, and `myproject:latest`.

## Notes

- Patterns are matched against: image repository, image tag, and container name
- Matching is case-insensitive and substring-based (no glob or regex needed)
- This list is a safety net — even without it, the skill never removes stopped containers, named images, or images used by any container
