# Validation and Recovery

## Baseline and snapshot

Before risky integration work:

1. Inventory dirty source, untracked files, running containers/processes,
   versions, mounts, ports, plugin state, Unity scene/configuration, and relevant
   logs.
2. Create a targeted, timestamped recovery point containing only the affected
   Unity sources/configuration, bridge/plugin source, runtime configuration,
   and a manifest of original paths and hashes.
3. Exclude secrets, package caches, build output, large generated libraries,
   chat data, and unrelated runtime state.
4. Verify the snapshot can be read before changing the live surface.

Never use a broad reset, clean, prune, overwrite, or replacement as recovery.
Restore only explicitly selected files after comparing them with current state.

## Evidence matrix

| Surface | Minimum evidence |
| --- | --- |
| Skill | Structural validation and identical mirror hashes |
| Bridge core | Parse/tests plus synthetic protocol lifecycle |
| Agent Zero plugin | Discovery, import, configuration, lifecycle, cleanup |
| Unity source | Compile plus focused tests/static checks |
| Serialized Unity state | Editor import, component wiring, saved scene/config |
| Quest Link/device | Observed binocular view, input, media, diagnostics, recovery |
| Roadmap closure | Current acceptance criteria mapped to retained evidence |

Report untested layers explicitly. Do not promote lower-layer evidence into a
claim about the full system.

## Crash and hang discipline

- When Unity or the bridge crashes, preserve the latest log, crash dump, event
  record, configuration, and reproduction sequence before restarting.
- Check that an artifact belongs to the failing run; an older graceful shutdown
  log cannot explain a later native crash.
- Change one plausible lifecycle owner or producer at a time. Re-run the
  smallest reproducer before stacking more fixes.
- Stop a repeated crash loop. Do not keep reopening Play Mode without new
  evidence or a controlled change.
- Distinguish failure to initialize XR from a crash after successful XR startup.

## Network and media failures

Exercise at least:

- Backend absent at startup, late startup, restart, and clean shutdown.
- Disconnect during text or return-audio delivery.
- Malformed control envelope and unknown binary media kind.
- Queue pressure, dropped frames, slow consumer, and bounded recovery.
- Audio device unavailable and playback/capture teardown.
- Protocol or capability mismatch.

The client must expose a useful diagnostic and recover where the contract says
it can, without requiring a Unity restart.

## Rollback record

For each handoff, state:

- Snapshot or recovery point used.
- Canonical files changed and mirrors synchronized.
- Runtime processes or configuration reloaded.
- Commands/tests run and their scope.
- Exact residual risk, especially headset-only or soak-only claims.
- How to restore the prior state without touching unrelated work.

Keep one deliberate recovery point for the active experiment until validation
is accepted. Cleanup is a separate authorized action.
