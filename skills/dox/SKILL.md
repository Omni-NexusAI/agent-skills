---
name: dox
description: Self-documenting AGENTS.md hierarchy (agent0ai/dox). Use when initializing, maintaining, or working inside projects that use AGENTS.md as a living instruction hierarchy. Enforces read-before-edit and update-after-edit while keeping DOX ambient rather than a separately narrated task mode.
---

# DOX - Self-Documenting AGENTS.md Framework

**Source:** [agent0ai/dox](https://github.com/agent0ai/dox)
**Core file:** `AGENTS.md` is the canonical project contract.

DOX is a lightweight hierarchy of `AGENTS.md` files that keeps agent-facing project instructions close to the code, docs, assets, and workflows they govern. Treat DOX as project operating discipline, not as a runtime dependency or separate tool that must be announced on every task.

## When to Apply

- The user asks to set up, initialize, add, evaluate, or update DOX.
- The user asks for an `AGENTS.md` hierarchy or self-documenting project instructions.
- The project already has `AGENTS.md` files and the task may touch project files.
- A project has two or more durable domains, ownership boundaries, workflows, or intention-tracking needs.
- A meaningful change affects structure, contracts, workflows, ownership, verification, or durable user preferences.

## Ambient Contract Behavior

When DOX is already installed, it should feel like normal project context:

- Read the applicable `AGENTS.md` chain before editing.
- Follow the closest applicable `AGENTS.md` plus every parent contract.
- After meaningful changes, do a closeout pass over the affected `AGENTS.md` files.
- Update only the contract files whose scope actually changed.
- Keep narration practical: say you are reading the instruction chain, checking the closeout docs, or updating affected `AGENTS.md` contract files.

Avoid redundant ceremony:

- Do not treat DOX as a separate mode to activate inside a DOX-installed project.
- Do not repeatedly announce that you are "updating DOX" for routine local contract maintenance.
- Do not add an extra planning step when the root `AGENTS.md` already makes the needed behavior clear.
- Do not duplicate stable instructions across parent and child files just to show DOX activity.
- Do not update `AGENTS.md` files for small edits that do not change behavior, structure, contracts, workflows, or durable expectations.

## Read Before Editing

For every path you expect to touch:

1. Read the root `AGENTS.md` if one exists.
2. Walk from the repository root to each target path.
3. Read every `AGENTS.md` file encountered along that route.
4. If a parent `AGENTS.md` indexes a child whose scope contains the path, read that child and continue.
5. Use the nearest `AGENTS.md` as the local contract.
6. Use parent files for broader repository rules.
7. If docs conflict, the closer doc controls local details, but no child may weaken the DOX contract.

Do not rely on memory for the instruction chain. Re-read the applicable files in the current session before editing.

## Update After Editing

Every meaningful change requires a DOX closeout pass before the task is done.

Update the closest owning `AGENTS.md` when a change affects:

- Purpose, scope, ownership, or responsibilities.
- Durable structure, contracts, workflows, or operating rules.
- Required inputs, outputs, permissions, constraints, side effects, or artifacts.
- Durable user preferences about behavior, communication, process, organization, or quality.
- `AGENTS.md` creation, deletion, movement, naming, or child index contents.

Update parent docs when parent-level structure, ownership, workflow, or child indexes change. Update child docs when parent changes alter local rules. Remove stale or contradictory text immediately.

Small edits that do not change behavior or contracts may leave docs unchanged, but the closeout pass still happens: check the chain, decide no doc update is needed, and report that briefly when useful.

## Initialization Workflow

Before initializing, scan the project and choose the lightest useful hierarchy.

Scope levels:

| Level | When to use | Structure |
| --- | --- | --- |
| Root-only | Small projects or single-purpose repos | One root `AGENTS.md` |
| Shallow | Medium projects with a few durable areas | Root plus one child per area |
| Deep | Large multi-domain projects | Root plus nested children matching real boundaries |

Ask or infer:

- Scope level.
- Sections to include.
- Folders to exclude, such as `.git`, `node_modules`, `venv`, `dist`, and generated output.
- Naming convention, normally `AGENTS.md`.
- Existing verification commands.
- Existing docs or instruction files to merge rather than overwrite.

Recommended flow:

1. Scan top-level structure and identify durable boundaries.
2. Propose the scope and child breakdown.
3. Generate or merge the root `AGENTS.md`.
4. Generate child `AGENTS.md` files only for real boundaries.
5. Verify the hierarchy is concise, indexed, and operational.
6. Commit DOX initialization separately when the repo workflow expects commits.

## Root AGENTS.md Shape

```markdown
# DOX Framework

## Core Contract

- AGENTS.md files are binding work contracts for their subtrees.
- Work products, source materials, instructions, records, assets, and durable docs must stay understandable from the nearest applicable AGENTS.md plus every parent AGENTS.md above it.

## Read Before Editing

1. Read the root AGENTS.md.
2. Identify every file or folder you expect to touch.
3. Walk from the repository root to each target path.
4. Read every AGENTS.md found along each route.
5. If a parent AGENTS.md lists a child AGENTS.md whose scope contains the path, read that child and continue from there.
6. Use the nearest AGENTS.md as the local contract and parent docs for repo-wide rules.
7. If docs conflict, the closer doc controls local work details, but no child doc may weaken DOX.

Do not rely on memory. Re-read the applicable DOX chain in the current session before editing.

## Update After Editing

Every meaningful change requires a DOX pass before the task is done.

Update the closest owning AGENTS.md when a change affects:

- purpose, scope, ownership, or responsibilities
- durable structure, contracts, workflows, or operating rules
- required inputs, outputs, permissions, constraints, side effects, or artifacts
- user preferences about behavior, communication, process, organization, or quality
- AGENTS.md creation, deletion, move, rename, or index contents

Update parent docs when parent-level structure, ownership, workflow, or child index changes. Update child docs when parent changes alter local rules. Remove stale or contradictory text immediately. Small edits that do not change behavior or contracts may leave docs unchanged, but the DOX pass still must happen.

## Child DOX Index

<!-- List child AGENTS.md files and the scope each one owns. -->
```

## Child AGENTS.md Shape

```markdown
# [Folder Name]

## Purpose

<!-- What this folder/domain contains and why it exists. -->

## Ownership

<!-- Who or what system owns this area. -->

## Local Contracts

<!-- Binding rules for this subtree. -->

## Work Guidance

<!-- How to work in this area; current standards. -->

## Verification

<!-- How to verify changes in this area. -->

## Child DOX Index

<!-- List child AGENTS.md files if this folder has sub-domains. -->
```

## Style

- Keep docs concise, current, and operational.
- Document stable contracts, not diary entries.
- Put broad rules in parent docs and concrete details in child docs.
- Prefer direct bullets with explicit names.
- Do not duplicate rules across many files unless each scope needs a local version.
- Delete stale notes instead of explaining history.
- Trim obvious statements, repeated rules, misplaced detail, and warnings for risks that no longer exist.
- Leave empty optional sections out unless the project has real content for them.

## Pitfalls

- Over-nesting: every level adds reading overhead; only create child docs for real boundaries.
- Changelog drift: DOX documents current contracts, not task history.
- Skipped read phase: the contract only works if the current chain is read before edits.
- Empty boilerplate: omit optional sections that have no useful content.
- Overwriting existing instructions: merge existing `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, or similar files.
- Ceremonial narration: avoid making DOX sound like a separate process when it is just the repo's instruction system.
