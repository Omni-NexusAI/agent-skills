---
name: ai-link-workflow-rules
description: Coordinate AI-Link work across the Unity XR client, the portable AI Link bridge, Agent Zero, future AINexus seeding, Linear, and the paired development plan. Use for AI-Link planning, implementation, debugging, protocol or media changes, plugin packaging, runtime validation, roadmap reconciliation, recovery, and cross-environment handoffs.
---

# AI-Link Workflow Rules

Use this skill as the integration workflow for AI-Link. Apply the applicable
project `AGENTS.md` hierarchy as the binding local contract; this skill joins
the client, bridge, runtime, roadmap, and future AINexus surfaces without
replacing their owning documentation.

## Load the relevant guidance

Always read:

- [Operating contract](references/operating-contract.md)
- [Validation and recovery](references/validation-and-recovery.md)

Then read each reference whose surface is in scope:

- [Unity client workflow](references/unity-client.md) for Unity, OpenXR, Meta
  XR, scenes, capture, input, playback, or headset behavior.
- [Bridge and Agent Zero workflow](references/bridge-agent-zero.md) for the
  bridge, protocol, plugin discovery, Agent Zero integration, or mirrors.
- [Roadmap and AINexus workflow](references/roadmap-and-ainexus.md) for Linear,
  the development plan, issue closure, portability, or AINexus seeding.

## Establish current truth

Before substantial work:

1. Read every applicable `AGENTS.md` from each project root to every target.
2. Inspect the real source, dirty state, running processes or containers,
   mounts, ports, package/runtime versions, serialized Unity configuration,
   and installed plugin state. Do not infer them from an image tag or old chat.
3. Identify the live Linear issue and compare it with the paired development
   plan. Linear owns execution state; the plan owns architectural narrative and
   sequence. Treat archived chats and memory as leads that require verification.
4. Classify the change across client, wire contract, bridge, Agent Zero host,
   diagnostics, documentation, and future AINexus portability.
5. Record a targeted recovery point before a risky or cross-runtime change.

Use independent agents in parallel only when their work does not compete for a
shared runtime or shared contract. Keep one owner for protocol and acceptance
decisions, then reconcile all results against live source.

## Work from the contract outward

1. Define the intended user-visible loop and the evidence that will prove it.
2. Inspect both client and backend before changing a shared behavior.
3. Preserve `ailink.v1` unless the user explicitly authorizes a version change.
   When the wire contract changes, update both implementations, protocol docs,
   examples, and compatibility tests together.
4. Keep capture, encoding, transport, session state, diagnostics, and AI/task
   adapters separable. Do not let a prototype shortcut become an implicit API.
5. Build backend behavior plugin-first and updater-safe. Core Agent Zero edits
   require a demonstrated plugin-host limitation and explicit scope.
6. Make the smallest reversible change, validate the narrow layer, synchronize
   the deployed surface, and then validate the complete loop.

## Keep capabilities truthful

- Advertise only codecs, transports, task routes, return media, metrics, and
  recovery behavior that the current deployed path has proven end to end.
- Label scaffolds as scaffolds. An accepted request, incremented counter,
  successful import, or healthy standalone server is not downstream behavior.
- Distinguish render-only passthrough from readable camera frames, client-to-
  server audio from return audio, and plugin source from a discovered/enabled
  plugin instance.
- Do not close a roadmap issue because an adjacent Agent Zero feature exists;
  map its acceptance criteria to concrete equivalent behavior first.

## Validate in layers

1. Static structure, parsing, and focused unit checks.
2. Bridge protocol and synthetic-client lifecycle.
3. Agent Zero plugin discovery, imports, enable/disable, configuration, and
   cleanup in the named runtime.
4. Unity compilation, serialized wiring, and repeated Play/Stop behavior.
5. Quest Link or device behavior, concurrent media/input/diagnostics, recovery,
   and the required soak duration.

If a layer fails, preserve its evidence and repair that layer before escalating
to a more expensive test. Do not consume the user's headset time to find a bug
that a synthetic client or Editor check can expose.

## Keep progress synchronized

After each meaningful implementation, deployment, integration, or headset-test
milestone, record the verified progress and remaining acceptance gaps on the
owning Linear issue. Follow the roadmap reference for authority, deduplication,
and read-back verification. Do not postpone these checkpoints until closeout.
Update the paired development plan when architecture or sequencing changes.
If a write is blocked, retain the checkpoint locally and report synchronization
as pending; never imply that a prepared update was published.

## Close out

1. Re-read the affected DOX chain and update only contracts whose durable
   structure, behavior, ownership, or verification changed.
2. Compare final dirty state with the baseline and exclude unrelated work.
3. Re-run focused checks plus the affected live integration path.
4. Report source and deployed paths, versions, capability truth, evidence,
   residual hardware or soak limits, and exact rollback steps.
5. Add Linear evidence or recommend status changes only when acceptance
   criteria are actually met. Update the development plan only when its durable
   architecture or sequence changed.

The canonical skill source lives with the bridge. Project, installed-plugin,
and Codex copies are mirrors, not independent edit targets. Use
`scripts/validate_skill.py` and `scripts/check_mirrors.py` after any skill
change.
