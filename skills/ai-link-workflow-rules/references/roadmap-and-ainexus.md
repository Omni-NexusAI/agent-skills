# Roadmap and AINexus Workflow

## Reconcile the planning pair

For substantial work, inspect both:

- **Linear:** live status, priority, dependencies, acceptance criteria,
  comments, and execution evidence.
- **AI-Link development plan:** architectural intent, broad phases, sequencing,
  and the relationship between the client, backend, and AINexus.

Do not hardcode current issue status into this skill. Identify the active issue
from Linear each run and map the requested behavior to its current acceptance
criteria. If Linear and the plan diverge, preserve live execution state, record
the discrepancy, and ask only when the difference changes implementation.

## Continuous evidence checkpoints

After each meaningful implementation, deployment, integration, or physical-test
milestone:

1. Re-read the owning issue and recent comments. Identify what changed since
   the last checkpoint; do not create duplicate progress comments.
2. Within the user's authorized roadmap scope, publish concise evidence that
   separates source work, isolated tests, installed behavior, and physical
   acceptance. Include failures and unrun gates without sensitive payloads.
3. Read the published comment or changed fields back and confirm they match.
   A successful local edit or prepared payload is not synchronization evidence.
4. Update the development plan when durable architecture, dependencies, or
   phase sequencing changes. Do not duplicate every test log into that plan.
5. If authorization, connectivity, or a write fails, keep a local pending
   checkpoint and report it. Continue independent work; do not claim the
   roadmap is current until the remote update is verified.

Evidence comments do not automatically authorize closing issues or moving
dates. Reconcile those decisions against the live acceptance criteria and the
paired plan; record the rationale before an authorized status or scope change.

## Completion audit

- A capability already present in Agent Zero can satisfy an AI-Link issue only
  when its externally visible behavior and constraints match the issue.
- Work underway in another plugin, such as speech-to-speech, is a dependency or
  parallel effort until the AI-Link integration path is verified.
- Partial prototype evidence belongs in a comment or sub-criterion; it does not
  justify closing a broader issue.
- Attach behavior-level evidence before recommending or applying a status
  change. Do not update Linear or the plan without authority for that write.
- Add a new issue or phase only when the work cannot fit an existing broad
  milestone without obscuring ownership or acceptance.

## AINexus transition gate

Treat AINexus seeding as a later portability test, not an automatic copy of the
current Agent Zero container. Begin it only when the user authorizes the phase
and the required prototype loop has passed its live acceptance gate.

The transfer package should contain:

- Portable plugin source with a truthful manifest and compatibility statement.
- Versioned `ailink.v1` schema, examples, and client/server contract tests.
- Configuration defaults with secrets excluded and migration notes for user
  settings.
- Plugin discovery/lifecycle tests and an end-to-end client validation path.
- Capability and known-limit matrix.
- Install, rollback, and source-to-deployed synchronization procedure.
- This workflow skill and the applicable stable DOX contracts.

Validate the seed in a new, parallel, clearly named repository/container with
unique ports. Preserve the source Agent Zero environment, installed plugins,
volumes, and recovery image until the user approves a switch or cleanup.

After the seed proves its own plugin loader and conventions, revise this skill
to replace provisional Agent Zero-specific routing with the verified AINexus
workflow. Consolidate only useful, current general workflow clauses; do not
carry obsolete fork, release, container, or tool assumptions forward.
