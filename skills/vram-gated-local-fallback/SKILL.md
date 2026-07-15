---
name: vram-gated-local-fallback
description: |
  Pattern + portable script for preventing local LLM models from loading (or
  continuing to run) when the GPU is already busy. Use whenever an agent has a
  model fallback hierarchy that includes locally-loaded models (llama.cpp /
  LM Studio / Ollama / any VRAM-backed backend) and must avoid OOM / VRAM
  thrash when the GPU is shared with games, renders, or other inference. Two
  layers: (1) gate local entries when SELECTING a fallback, (2) watchdog that
  fails over the ACTIVE local model if VRAM gets eaten mid-session. Drop into
  any agent's skill set; reimplement the core hooks in the agent's own loop.
version: 1.0.0
author: Omni-NexusAI
platforms: [linux, windows, macos]
metadata:
  hermes:
    tags: [vram, fallback, local-model, gpu, oom-prevention, resilience]
    category: infrastructure
    related_skills: []
---

# VRAM-Gated Local Fallback (vendor-neutral pattern)

## Problem

A locally-loaded LLM needs GPU VRAM to load and to serve. If the GPU is already
busy when the model would load — a game, a render job, another inference server
(LM Studio, a second llama.cpp), a cloud-GPU app — one of two bad things
happens:

- **On load:** the local model fails to load, or loads by evicting the other
  workload, thrashing the system.
- **Mid-session (the "vice versa" case):** the local model is already serving,
  then a *different* process grabs VRAM. The next token generation OOM-crashes
  the box or silently corrupts the run.

The fix is a single cheap check — read `nvidia-smi`, compare used VRAM % against
a threshold — applied at two points in the agent's lifecycle.

## Core primitive

The whole thing reduces to one function:

```
vram_used_pct() -> float | None:
    if nvidia-smi absent: return None          # unknown -> fail-open
    (used, total) = query nvidia-smi memory.used,total
    return used / total * 100
```

`None` (no GPU / driver) MUST mean "do not block" (fail-open). Only block when
you actually measured VRAM above threshold.

The portable implementation lives in `scripts/vram_gate.py`. It exits 0 (open)
or 1 (closed) and prints a JSON decision line. Use it directly as a subprocess
gate, or inline the ~10-line logic into your agent's core.

## Configuration

| source (first match wins) | example |
|---|---|
| CLI override | `--threshold 50` |
| env var | `VRAM_GATE_THRESHOLD_PCT=50` |
| config file (agent-specific key) | `--config config.yaml --config-key fallback.vram_gate_threshold_pct` |
| built-in default | `75.0` |

Pick a threshold per your risk tolerance. 50% is conservative (skip local as
soon as half the VRAM is gone). 75% leaves more room but risks eviction under
spiky VRAM. **Default should be ~50 for safety-first agents.**

## Layer 1 — gate local entries when SELECTING a fallback

When the agent walks its fallback chain and reaches a *local-model* entry,
check VRAM first. If busy, skip that entry and fall through to the next
provider instead of loading it.

```
is_local(provider):
    return any(k in provider for k in ("llamacpp", "lmstudio", "ollama"))

for entry in fallback_chain:
    if is_local(entry.provider) and vram_used_pct() >= threshold:
        log("skip local %s: VRAM %.0f%% >= %s%%" % ...)
        mark_unavailable(entry)          # don't retry it this session
        continue                          # try next entry
    # ... normal resolve + use entry ...
```

Cloud providers are NEVER gated (they have no VRAM dependency). Only local
backends are checked. The `mark_unavailable` step matters: without it the loop
would re-pick the same blocked local entry on the next retry and spin.

## Layer 2 — mid-session watchdog (the "vice versa" case)

Layer 1 only guards *selection*. The active model can still be a local one that
loaded fine, then the GPU gets eaten by another process. So, **before each
primary inference call**, if the active model is local and VRAM is now busy,
fail over to the next fallback provider.

```
before each primary inference call:
    if is_local(active.provider) and vram_used_pct() >= threshold:
        if not already_failed_over and now >= cooldown_until:
            if try_activate_fallback():       # switch active to next provider
                cooldown_until = now + 60s    # don't thrash every call
                continue                      # re-issue on new provider
```

Key details that prevent bugs:

- **Cooldown (60s) after a failover.** Without it, every single call would
  re-check VRAM and flip-flop between local and fallback. The cooldown lets the
  fallback provider serve steadily while the GPU stays busy.
- **Fail over, then restore later.** The fallback system should already have a
  "try the primary again after a cooldown" path. Reuse it: when VRAM frees up,
  the active local model is re-selected automatically. This is the behavior we
  chose — do NOT hard-stop the local model and notify; let the hierarchy recover.
- **Only gate the ACTIVE local model.** Cloud-active primaries are never checked
  (no VRAM dependency, and checking them is wasted work + false-failover risk).
- **Wrap in try/except → fail open.** If the VRAM probe throws (driver hiccup),
  treat as "unknown" and proceed. A broken probe must never wedge the agent.

## Pseudocode (agent-agnostic core)

```
THRESHOLD = read_threshold()        # env > config > 75
LOCAL_KEYS = ("llamacpp", "lmstudio", "ollama")

def vram_busy() -> bool:
    pct = vram_used_pct()
    return pct is not None and pct >= THRESHOLD

# ---- Layer 1: fallback selection ----
def pick_fallback(chain, unavailable):
    for entry in chain:
        key = (entry.provider, entry.model)
        if key in unavailable: continue
        if is_local(entry.provider) and vram_busy():
            unavailable.add(key); log skip; continue
        return resolve(entry)
    return None

# ---- Layer 2: pre-call watchdog ----
def before_primary_call(agent):
    if is_local(agent.provider) and vram_busy() \
       and not agent.fallback_active and now() >= agent.cooldown_until:
        if activate_fallback():
            agent.cooldown_until = now() + 60
            return RETRY_ON_NEW_PROVIDER
    return PROCEED
```

## Integration checklist (for assimilating into a mesh peer)

1. Copy `scripts/vram_gate.py` into the peer, or inline the `vram_used_pct`
   logic into its core. (Inline is preferred for hot paths — a subprocess
   call per inference adds latency.)
2. Add `LOCAL_KEYS` matching the peer's local-provider naming.
3. Hook Layer 1 into the peer's fallback-chain walk (wherever it iterates
   `fallback_providers` / equivalent).
4. Hook Layer 2 into the peer's primary inference loop, right before the model
   call, reusing the peer's existing `activate_fallback()` + cooldown machinery.
5. Set `VRAM_GATE_THRESHOLD_PCT` (or the peer's config key) to your risk level.
6. Test: force threshold to 1% and confirm (a) a busy-GPU local fallback entry
   is skipped, (b) a busy-GPU active local model fails over, (c) a cloud primary
   is NEVER gated, (d) with real VRAM < threshold nothing false-triggers.

## Gotchas learned the hard way

- **Import the deps you use inside the function.** A helper that referenced
  `yaml` without importing it threw `NameError`, which was swallowed by a broad
  `except: pass`, so the gate silently never fired. Keep each VRAM helper
  self-contained (`import shutil, subprocess, yaml` inside the try).
- **`except: pass` is a silent-killer.** Wrap only the probe; let real bugs
  surface. Fail-open on probe error, but log it at debug level.
- **Don't gate cloud providers.** Checking VRAM for an API-backed model is
  wrong and risks false failover. Gate ONLY local/`LOCAL_KEYS` providers.
- **Cooldown is mandatory for Layer 2.** Without it the agent oscillates
  local↔fallback every call.
- **Threshold default 75 is too loose for shared GPUs.** 50 is safer when a
  game or another inference server might grab VRAM at any moment.

## Reference

- `references/design.md` — deeper design notes, threshold math, and the
  fail-over-then-restore recovery model.
- `scripts/vram_gate.py` — the portable, provider-agnostic gate (stdlib +
  optional pyyaml for config-file lookup).
