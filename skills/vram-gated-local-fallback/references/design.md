# Design notes — VRAM-gated local fallback

## Why two layers, not one

A single "check VRAM before loading a local model" guard only covers the moment
of *selection*. It cannot see the future: a local model that loads fine at t=0
can be stranded at t=30 when a game launches and consumes 6 GB of an 8 GB card.
That is the "vice versa" requirement — the gate must also protect an *already
running* local model from a GPU that gets eaten after load. Hence:

- **Layer 1 (selection gate):** cheap, runs only when walking the fallback
  chain. Prevents loading into a busy GPU.
- **Layer 2 (watchdog):** runs before *every primary inference call* when the
  active model is local. Detects the GPU being taken mid-session and fails over.

Together they bound the risk from both directions: don't load when busy, and
stop using it if it becomes busy.

## Threshold semantics

`threshold` = minimum % of VRAM that must be FREE for a local model to be
allowed. Concretely:

```
allowed = vram_used_pct < threshold
```

So `threshold = 50` means "block local if more than half the VRAM is used."
Choosing it:

| threshold | behavior | risk |
|---|---|---|
| 50 | conservative; local skipped as soon as half VRAM gone | rarely evicted; may skip local when there was actually room |
| 75 | default; local allowed until 75% used | more local usage; higher eviction risk under spiky VRAM |
| 90 | aggressive; only blocks when nearly full | most local usage; OOM likely if another process grabs the last GB |

For a **shared/desktop GPU** (games, renders, other inference can appear
anytime) use **50**. For a **dedicated inference GPU** you control, 75–90 is
fine. We ship 75 as the built-in default but recommend 50 for safety-first
agents, which is what was configured in the reference deployment.

## Fail-over-then-restore recovery model

When Layer 2 trips, the agent does NOT terminate the local model or hard-stop
anything. It:

1. Calls the agent's existing `activate_fallback()` to switch the active
   provider/model to the next entry in the chain.
2. Arms a 60s cooldown so subsequent calls don't immediately re-check and
   flip-flop.
3. The fallback provider serves steadily while VRAM stays busy.
4. The agent's existing "restore primary after cooldown" path later re-selects
   the local model once VRAM frees up — no special code needed, because the
   primary is the same local entry that Layer 2 deferred.

This reuses the agent's native fallback machinery; the VRAM gate only *decides
when* to trigger it. The gate is a decision input, not a new control flow.

## Why fail-open on probe error

`nvidia-smi` can fail transiently (driver hiccup, the binary path not on PATH
in some shells, a 10s timeout under load). If the gate treated "probe failed"
as "block", a single driver glitch would wrongly fail over every local call.
So:

```
vram_used_pct() returns None on any failure
vram_busy() returns False when pct is None
```

Unknown = allow. Log the failure at debug level so it's diagnosable without
being harmful. The `--strict` flag on the script inverts this for environments
where "no GPU" should mean "cannot run local" — but the in-core watchdog should
stay fail-open.

## Performance note

`nvidia-smi` is a spawned process (~10–30 ms). Layer 2 runs it before *every*
primary call, which on a high-throughput agent is measurable but small (sub-1%
of a typical 1–3s generation). If latency is critical, cache the reading for a
few seconds or call `nvidia-smi` via its persistent-mode / NVML binding instead
of spawning the binary each time. The portable script spawns the binary for
simplicity and zero dependencies; an inlined NVML version is an optimization,
not a requirement.

## Test matrix (portable, provider-agnostic)

| scenario | expected |
|---|---|
| local entry + VRAM 80% >= 50 | gate CLOSED (skip) |
| local entry + VRAM 38% < 50 | gate OPEN (allow) |
| cloud entry + any VRAM | gate OPEN (never gate cloud) |
| active local + VRAM busy mid-session | fail over to next provider |
| active cloud + VRAM busy | no action (cloud has no VRAM dep) |
| real VRAM 38% < 50, normal use | no false failover |
| nvidia-smi missing | gate OPEN (fail-open) unless --strict |
| threshold=1%, live 39% | gate CLOSED (forced-busy test) |
| threshold=99%, live 39% | gate OPEN (under threshold) |

## Files in this skill

- `SKILL.md` — the pattern, config, two layers, pseudocode, gotchas.
- `scripts/vram_gate.py` — portable gate (stdlib + optional pyyaml). Exit 0/1,
  JSON decision on stdout. Drop-in for any agent; no Hermes-specific code.
- `references/design.md` — this file.
