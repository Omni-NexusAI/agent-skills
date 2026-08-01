---
name: agent-workflow-rules
description: Apply generalized agent engineering workflow rules across repositories and environments. Use when planning, implementing, testing, reviewing, committing, opening pull requests, deploying, migrating environments, managing dependencies, selecting tools, or operating containers. Enforces scope discipline, PR-first delivery, preservation of user state, reversible iteration, evidence-based validation, and explicit approval for destructive or irreversible actions.
---

# Agent Workflow Rules

## Operating priorities

1. Follow the user's current explicit instructions first.
2. Respect the exact project, repository, environment, and artifact boundaries in scope.
3. Preserve user data, unrelated work, and existing environments.
4. Prefer reversible, inspectable changes and the smallest effective intervention.
5. Ask a focused question when ambiguity would materially change the result or required authority.

## Inspect before changing

1. Inspect repository status, applicable agent instructions, existing environments, and relevant runtime state before editing.
2. Treat uncommitted or untracked work as user-owned. Do not overwrite, discard, reformat, or include unrelated changes.
3. Establish the source of truth for code, configuration, generated artifacts, and deployed behavior.
4. Diagnose the cause before implementing a repair when the request is investigative or failure-oriented.
5. Re-check assumptions that are time-sensitive or inexpensive to verify.

## Plan relative to the current state

1. Build the plan from the actual state and requested outcome, not from an assumed clean baseline.
2. Identify dependencies, boundaries, risks, verification, and rollback before high-impact changes.
3. Keep implementation proportional to the request. Do not expand scope for adjacent improvements.
4. Reuse established project conventions and existing environments unless they block the required result.
5. Surface conflicts and weak assumptions early with a concrete recommended path.

## PR-first repository workflow

For repositories with a remote collaboration workflow:

1. Default to a dedicated branch and pull request.
2. Keep commits intentional and limited to the requested scope.
3. Push iterative, tested changes to the pull request and keep it draft until ready for review.
4. Do not push directly to protected or shared branches, merge, or publish a release without explicit authorization.
5. Reconcile current remote state before relying on a branch, build, or deployment as current.
6. Follow the project's established owner, remote, and contribution process; do not assume a vendor or organization.

## Environment and dependency handling

1. Prefer an existing isolated environment appropriate to the project.
2. Manage dependencies through the project's declared package and lockfile workflow.
3. Avoid global installation when an isolated project environment is available.
4. Before replacing or migrating an environment, inventory and preserve its data, configuration, secrets references, and required state.
5. Start replacement environments alongside existing ones when practical, verify them, and switch only with authorization.

## Fast, reversible iteration

1. Use the lightest effective refresh path: reload, process restart, service restart, then rebuild.
2. For containerized source development, inspect mounts and prefer bind-mounted iteration when it represents the target runtime accurately.
3. Rebuild when a change belongs in an image or dependency layer, build step, startup configuration, or generated artifact that mounts cannot reproduce.
4. Explain why a heavier rebuild or recreation path is required when it is not obvious.
5. Keep temporary and test instances clearly named and isolated from production or user-owned instances.

## Non-destructive container operations

1. Do not stop, remove, overwrite, prune, or replace containers, images, volumes, networks, or persisted data unless the user explicitly authorizes that target and action.
2. Use unique project names, instance names, and host ports for parallel validation.
3. Restrict cleanup to artifacts created by the task or explicitly placed in scope.
4. Preserve and verify persistent data before any authorized replacement.
5. Retain temporary resources until cleanup is requested or explicitly approved.

## Tool and documentation selection

1. Prefer the most direct, reliable tool for the target system and data source.
2. Prefer project-local tools and authoritative documentation over inferred behavior.
3. Use current primary documentation when libraries, frameworks, APIs, standards, or operational behavior may have changed.
4. Escalate privileges, network access, or external writes only when required and explain the need.
5. Do not install new tooling when an existing capability can complete the task safely.

## Verification and delivery

1. Verify at the narrowest useful layer first, then at the affected integration or runtime layer.
2. Use evidence appropriate to risk: focused tests, static checks, builds, logs, health checks, runtime inspection, or user-visible behavior.
3. Validate the running result when the task changes live behavior; code changes alone are insufficient evidence.
4. Report what changed, what was verified, and any remaining limitation or decision.
5. Do not claim completion while required validation, publication, migration, or authorization remains outstanding.

## Documentation continuity

1. Read the applicable repository instruction hierarchy before editing.
2. Write the GitHub repository description and README introduction for the person deciding whether to use the project, not for someone already developing it. For the short GitHub description, name the user-facing product or workflow, its main outcome, and a meaningful differentiator in one plain-language sentence. Lead the README with what it enables, who it is for, and the practical outcome; introduce internal architecture, implementation history, and maintenance details only when they help that reader get started or make an informed choice.
3. Treat the repository front page as product-facing onboarding: make the first screen understandable without prior project context, define unavoidable technical terms in plain language, and state important capabilities and limits truthfully.
4. Structure README content in reader order: purpose and outcome, key user-visible capabilities, the quickest supported way to try it, then installation, configuration, operational detail, API/reference material, development, and contribution guidance as applicable.
5. Before finalizing documentation, perform a newcomer read-through: verify that a prospective user can answer "What is this?", "What can it do for me?", "Is it suitable for my use case?", and "How do I begin?" without needing to inspect source code or infer developer jargon.
6. Keep documentation concise and current; record stable intent rather than task history. Do not overstate experimental, scaffolded, unavailable, or developer-only functionality.

