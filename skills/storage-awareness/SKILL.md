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

Start with an audit. **KEEP** is the default; missing evidence, stale/corrupt
state, unknown growth, aliases, hardlinks, protection matches, or an unavailable
lock all make mutation ineligible. Observation is not authority.

Before any storage-producing operation, run `scripts/storage_guard.py preflight`
for every affected volume. The default reserve is `max(20 GiB, 5% capacity)` plus
`estimated_peak_growth * 1.25`. An unknown expensive peak defers that operation.
Recheck before each safe boundary and after failure or a cross-volume stage.

## Policy-map contract

Begin from `templates/policy-map.example.json`; keep the real map private. It
defines protected paths, approved roots, exact action grants, artifact ownership,
volume reservations, and a freshness limit. Run `validate-map` before any
mutation. A map must be fresh, valid JSON, and schema version 1. Protection
overrides every grant. Do not remove a user protection without explicit approval.

Use normalized resolved paths. Treat junctions, symlinks, and hardlink aliases as
the same protected object; if identity cannot be established, keep it. An
approved location alone is never permission to delete or move data.

## Mutations and recovery

Automatic delete or move is limited to positively disposable, agent-owned
artifacts inside an approved root, with an exact live grant and required
history/recovery retained. Existing applications and personal data always need a
concrete reviewed target action. Acquire a per-volume lock and recheck policy,
path identity, capacity, and grant immediately before action.

For cross-volume relocation, budget peak duplicate storage. Copy, hash-verify,
switch configuration, smoke-test, then delete the original only after all checks
pass; retain rollback until the new location is proven. Pause/resume only jobs
owned by this workflow and only at known safe boundaries—never arbitrary
processes.

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
python scripts/storage_guard.py audit-inventory --input inventory.json --output normalized.json
python -m unittest discover -s tests -v
```

The helper is a gate and audit normalizer, not a deletion tool. Record each
reviewed operation in the private ledger with evidence, outcome, and rollback
state.
