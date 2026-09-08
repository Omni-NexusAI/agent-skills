---
name: storage-awareness
description: >-
  Safely assess or perform storage-affecting work: cleanup, downloads, builds,
  extraction, cache handling, moves, deletions, or large writes. Use whenever a
  request could materially consume, reclaim, relocate, or overwrite local disk
  data. It supplies a shared fail-closed policy map, capacity preflight, audit
  ledger, and safe-boundary coordination; it never assumes that observed files
  or an approved root are disposable.
---

# Storage Awareness

Use this skill as the shared safety authority for storage mutations. It is
portable: host-specific maps, grants, locks, and ledgers are private runtime
state, never committed to this skill.

## Default posture

Start with an audit. **KEEP** is the default for existing data; missing evidence,
aliases, hardlinks, protection matches, or an unavailable lock make a mutation
ineligible. Observation is not authority. Capacity pressure on one volume is not
authority to stop unrelated read-only work, planning, or writes on another volume.

Before a storage-producing operation, budget the actual peak growth on its target
volume, including the configurable 25% overhead and active reservations. The
default `max(20 GiB, 5% capacity)` is a **soft operating reserve**, not a blanket
project pause. The helper also keeps a smaller configurable hard emergency margin
(default `max(1 GiB, 1%)`):

- `ready`: the write preserves the soft reserve; reserve and continue.
- `warning`: the bounded write fits above the hard margin but crosses the soft
  reserve. Continue the affected bounded work if needed, preferably route new
  scratch/download/extract/build/cache staging to a `ready` approved write root.
- `defer`: the target volume cannot safely cover active reservations plus the
  proposed peak and hard margin. Defer only that write; continue unrelated work
  and inspect approved alternatives.

For an unknown peak, use a bounded probe or estimator—not an indefinite pause—and
then reserve the measured target volume. A multi-step write or move still requires
a private per-volume reservation and fresh `checkpoint` at each safe boundary.
Missing, stale, corrupt, or locked state blocks the destructive/finalization action
that depends on it; it does not halt independent low-write investigation.

Use `plan-write` before creating new task-owned staging. It is read-only and only
selects existing `write_roots` explicitly approved for the requested purpose. It
never moves applications, changes global `TEMP`/cache variables, or changes an app
configuration. Apply tool-supported per-task temp/cache arguments only after a
fresh reservation succeeds.

## Policy-map contract

Begin from `templates/policy-map.example.json`; keep the real map private. It
defines protected paths, approved roots, exact action grants, artifact ownership,
volume reservations, and a freshness limit. Its timestamps are deliberately
expired placeholders: replace `generated_at` and every grant `expires_at` when
instantiating a private map. Run `validate-map` before any mutation. A map must be
fresh, valid JSON, and schema version 1. Protection overrides every grant. Do not
remove a user protection without explicit approval.

Use normalized resolved paths. Treat junctions, symlinks, and hardlink aliases as
the same protected object; if identity cannot be established, keep it. An
approved location alone is never permission to delete or move data.

## Mutations and recovery

Automatic delete or move is limited to positively disposable, agent-owned
artifacts inside an approved root, with an exact live grant and required
history/recovery retained. Existing applications and personal data always need a
concrete reviewed target action. Acquire a per-volume lock and recheck policy,
path identity, capacity, and grant immediately before action.

For cross-volume relocation, budget peak duplicate storage. The executable helper
handles one regular, unlinked file with an exact source-and-destination move grant:
`stage-relocation` copies, hash-verifies, persists a transaction, and retains the
source. A separate reviewed `record-relocation-disposition` step records config and
smoke outcomes; only `finalize-relocation` may delete the source, and only when both
are `passed`. Any other disposition retains both source and verified staged copy.
Application-specific configuration switching
and smoke tests are explicit reviewed adapters, not automated by this helper.
Directory moves, arbitrary process control, and existing app/person data remain
reviewed workflows. Do not pause arbitrary processes. A bounded inventory or
planning subagent may keep searching approved alternatives while the affected
write waits under shared reservation accounting.

Docker/WSL lifecycle remains owned by the Docker specialist. Do not duplicate its
shutdown, pause, or VHDX-compaction policy here.

## Audit output

Use `audit-inventory` to normalize supplied evidence into `keep`,
`compression_analysis`, `relocation_review`, `removal_review`, or `unknown`.
Report exact path, purpose, logical and allocated bytes when actually measured,
compression state and confidence, dependencies, recommended action, and recovery
requirements. Do not infer allocation or savings from a representative file.
Model weights, checkpoints, model caches, and their linked aliases are keep by
default.

## Commands

```powershell
python scripts/storage_guard.py validate-map --map C:\private\storage-policy.json
python scripts/storage_guard.py preflight --path E:\work --estimated-peak-bytes 2147483648
python scripts/storage_guard.py plan-write --map C:\private\storage-policy.json --path C:\agent-work --purpose build --estimated-peak-bytes 2147483648 --candidate-path E:\agent-work
python scripts/storage_guard.py reserve --map C:\private\storage-policy.json --path E:\work --reservation-id build-42 --estimated-peak-bytes 2147483648
python scripts/storage_guard.py checkpoint --map C:\private\storage-policy.json --path E:\work --reservation-id build-42 --estimated-peak-bytes 2147483648
python scripts/storage_guard.py audit-inventory --input inventory.json --output normalized.json
python -m unittest discover -s tests -v
```

`delete-owned` is deliberately limited to one exact, positively disposable,
agent-owned regular file with a live delete grant. `stage-relocation` requires a
prior reservation and exact move grant; release the reservation only after the
transaction's recovery disposition is recorded. A failing reviewed disposition
retains both copies and releases only the future-growth reservation; a successful
finalization deletes only the verified source and releases its reservation. Private
JSONL ledger records are append-only evidence, not authority. These commands are
not a general cleanup tool.
