---
name: agentzero-workflow-rules
version: 1.0.0
author: Omni-NexusAI
description: "Agentspine workflow and safety rules for PR-first GitHub flow, plugin-first feature work, updater-safe changes, Docker handling, and repo defaults. Triggers on: /agentzero-workflow-rules, agentzero workflow rules, agentspine workflow rules, Agentspine repo work, Omni-NexusAI/agent-zero, plugin-first Agentspine changes, self-updater-safe changes."
allowed-tools: Read Write Edit Glob Grep Bash
user-invocable: true
---
# Agentspine Workflow Rules (Consolidated)

## Purpose

Apply these rules as hard constraints whenever working in the Agentspine context, including local development, feature implementation, Docker/container workflows, GitHub operations, MCP/tool selection, plugin architecture, self-updater compatibility, and roadmap/documentation alignment.

> **Agentspine** is the user's branded fork of Agent Zero, hosted at `Omni-NexusAI/agent-zero`.

---

## GitHub & Repository Reference Rules

When working with Agentspine:
1. Primary repository (default): `Omni-NexusAI/agent-zero`
2. Default branch (default): `development` (NOT `dev` or `main`)
3. For GitHub operations (PRs/issues/commits), code references, and repository interactions: default to `Omni-NexusAI/agent-zero` and `development`.

Exception cases:
1. Reference `agent0ai/agent-zero` only when the user explicitly requests it.
2. Use branches other than `development` only when specifically requested.
3. Use other forks only when explicitly directed by the user.

Tags and releases:
1. Agentspine uses a two-build versioning scheme. All tags follow one of these patterns:

   | Build type | Release tag             | Pre-release tag             |
   |------------|-------------------------|-----------------------------|
   | Standard   | `v{x}.{x}.{x}-standard` | `v{x}.{x}.{x}-standard-pre` |
   | GPU        | `v{x}.{x}.{x}-gpu`      | `v{x}.{x}.{x}-gpu-pre`      |

   Examples: `v0.9.9-standard`, `v0.9.9-standard-pre`, `v0.9.9-gpu`, `v0.9.9-gpu-pre`

2. There is no hybrid build type. Every release is either `standard` or `gpu` â€” never both combined.
3. The `-custom` suffix was retired. Do NOT use it for new tags. Legacy tags with `-custom` remain in history but are not used going forward.
4. All tags ONLY exist in `Omni-NexusAI/agent-zero`.
5. When cloning by tag, ALWAYS use:
   ```
   git clone -b <tag-name> https://github.com/Omni-NexusAI/agent-zero.git
   ```
6. NEVER use `agent0ai/agent-zero` for tag cloning.

User override:
1. If the user explicitly requests otherwise, their instructions override these defaults.

---

## Core Workflow Rules (PR-First)

1. Use a PR-first workflow for all GitHub repos:
   - Create PR first.
   - Plan the feature/fix.
   - Implement in the environment.
   - Test.
   - Push commits into the PR.
   - Repeat plan/implement/test/push until the user confirms results are satisfactory.
   - Merge only after explicit user approval.
2. Never push or merge directly into a branch without a PR unless the user explicitly allows it.
3. When pulling from a branch within the user's repos, pull a fresh image and fresh environment with the latest code so newest features are available.
4. If something must be pulled from one of the user's repos, always use Omni-NexusAI.

---

## MCP and Tooling Rules

1. Prefer non-Windows MCP tools first. Use Windows MCP only when other MCP tools cannot solve the task.
2. For newly installed MCP servers, set them up at: `C:/Users/yepyy/Documents/MCPs`
3. Use Context7 whenever up-to-date documentation is needed (libraries/frameworks/APIs).
4. Use other available tools that can solve the task before attempting Windows MCP when possible.

---

## Environment and Dependency Rules

1. For non-dockerized localhost packages/dependencies, use a Conda environment when applicable.
2. Default to existing environments (Docker, Conda, etc.).
3. If a new environment instance is required:
   - Back up all instance data for transfer.
   - Migrate previous settings.
   - Start the new environment for testing.

---

## Bind Mount First Workflow (Default)

1. Default to implementing code changes through bind mounts so changes reflect quickly in the running environment.
2. Prefer testing against the existing bind-mounted workspace before choosing image rebuilds or replacement environments.
3. Only skip the bind-mount-first approach when bind mounts are not enough for the change to take effect, such as:
   - Dockerfile or base image changes
   - System package or runtime installation changes
   - Dependency installation or lockfile changes that must exist inside the container
   - Startup-time environment, entrypoint, or build-step changes
   - Generated assets or compiled artifacts not refreshed by the current mounted workflow
4. When using Docker Compose, prefer restarting or reloading the existing bind-mounted service before rebuilding its image.
5. When an exception applies, explicitly explain why bind mounts are insufficient before switching to a rebuild-heavy workflow.

---

## Plugin-First Feature Architecture (Default)

1. Default all future Agentspine feature implementations to the plugin system whenever the feature can reasonably be built as a plugin.
2. Treat plugin portability and marketplace/custom-plugin compatibility as part of "done" for new features, not as a later cleanup step.
3. Prefer implementations that live under `/a0/usr/workdir` and load through the plugin system, because changes outside `/a0/usr/workdir` can break the Agentspine self-updater.
4. Before editing core files outside `/a0/usr/workdir`, check whether the same behavior can be implemented through:
   - Plugin manifests and metadata
   - Plugin extensions
   - Plugin tool handlers
   - Plugin API handlers
   - Plugin WebUI assets/hooks
   - Plugin configuration
5. Only modify core application files when the feature cannot be implemented cleanly as a plugin, or when the work is explicitly about core framework/plugin-host behavior.
6. When core edits are unavoidable, keep them minimal, document why a plugin-only approach is insufficient, and preserve updater compatibility.
7. For UI and backend additions, design the core surface as an extension point where possible, then put feature-specific behavior in a plugin.
8. During review and verification, confirm the feature still works as a plugin-loaded capability and does not require patching files that the self-updater is expected to manage.

---

## Docker / Container Deployment & Lifecycle Rules

**Core mandate: No Implicit Deletion**
1. NEVER remove, stop, or overwrite an existing container or image unless the user explicitly commands it (e.g., "replace the old container", "delete the v0.x.y build").
2. "Cleaning up" or "Preparing environment" must NOT involve deleting existing containers unless those containers were explicitly targeted for removal.

**Parallel deployment (default strategy)**
1. When asked to build or deploy a new environment, ALWAYS deploy it alongside existing ones.
2. Implementation:
   - Use a unique project name (e.g., `docker compose -p agentspine-test-run-2 ...`) or ensure the `docker-compose.yml` has a unique `name:` field.
   - Ensure container names do not conflict (e.g., `agentspine-dev-v2` vs `agentspine-dev`).
   - Use unique host ports (check for occupied ports and map them uniquely).

**Migration & replacement**
1. Only replace an environment if the user uses words like "upgrade", "replace", "overwrite", or "update this specific container".
2. Even when replacing, ensure data (memory, knowledge) is preserved or migrated before destruction.

**Testing & temporary builds**
1. Treat test builds as temporary. Do not auto-cleanup before validation is complete; after the user confirms validation or says the reference is no longer required, follow the validation pull/build lifecycle below.
2. Use descriptive names for test builds (e.g., `agentspine-test-pr123`, `agentspine-quick-check`).
**Validation pull/build lifecycle**
1. When pulling or baking an Agentspine image for release or recovery validation, treat the environment as a temporary validation reference unless the user explicitly says to preserve it.
2. Before asking the user to validate, verify prerequisite features that matter for that build type, including health, banner/build identity, plugin loading, WebUI availability, settings exposure, STT, TTS, and GPU/CUDA behavior when applicable.
3. After the user confirms validation is complete or says the reference is no longer required, remove the validation-only container and its validation-only local image by default, unless the user explicitly asks to keep, archive, tag, or repurpose it.
4. Never remove the published remote image/tag, source branch, PR, or any long-running user environment as part of this validation cleanup unless the user explicitly targets those objects.
5. If a validation container/image was recreated only to restore a recoverable reference, and the user later says it is unnecessary, remove it again and record the reason in the final handoff.

**Docker image update rules**
1. Carry over all data from the previous environment to the new image(s).
2. Clean up only older unused images related to the requested environment.
3. Do not touch containers outside the relevant environment(s).

**Protected existing containers and name-conflict habits**
1. When the user names a container, image ID, long hash, port, or existing environment, treat that exact object as protected. Inspect it first, and do not stop, restart, rename, recreate, remove, or rebuild it unless the user explicitly targets that object or asks for a restore/repair of it.
2. Before starting any new Agentspine test container, list existing containers, images, names, and occupied host ports. Choose a unique container name, Compose project name, and host port so the new test stack runs alongside current environments.
3. Never reuse or steal names from existing containers such as `agentspine-standard-pre`, `agentspine-standard-pre-source-target`, or `agentspine-v099pre-target` for a new GPU/standard test stack. Use descriptive adjacent names such as `agentspine-gpu-pre-test`, `agentspine-gpu-pre`, or another non-conflicting name.
4. If a name conflict means a rename is technically correct, explain it clearly before or as part of the action: name the conflicting container, the requested/new name, the chosen replacement name, and why the rename or alternate name is needed. Do not hide name changes inside a broader deployment step.
5. If localhost stops loading, inspect container metadata, image presence, logs, process state, listening sockets, and port mappings before assuming the image is missing or recreating the environment. Prefer the smallest repair, such as restarting the failed in-container service, and only restart the whole target container when the user has asked to restore that target.
6. If restoring one environment would require stopping, renaming, recreating, or removing a sibling container, ask the user first. Preserve long-running user containers even when their names are inconvenient.
7. When starting a GPU image for user testing, keep the standard container untouched, publish the chosen URL/port, and mention any port/name difference from previous containers.
---

## Documentation & Roadmap Alignment

1. Reference the AI-Link Development Plan architecture and 2026 development PDF and Linear AI-Link project roadmaps as you work through the project to avoid conflicts across project handlers and stay on track.
2. Regularly reference and update the AI-Link Linear roadmap issues so all agents and users know what is happening.

---

## Conflict Resolution Priority

1. Follow explicit direct user instructions in the current request.
2. Otherwise apply these scope/workflow rules.
3. If uncertainty remains, ask a focused clarifying question before acting.

## v0.9.9-pre Bake and Self-Updater Compatibility Rules

When preparing or baking the Agentspine v0.9.9-pre line, follow these rules unless the user explicitly changes the release target:

- Treat `C:\agent-zero-v099pre-target` and the running `agentspine-v099pre-target` container as the source of truth until the hotpatch branch is merged.
- Bake from the hotpatched target tree, not from the older `C:\agent-zero` checkout, when the user references the v0.9.9-pre target container.
- Preserve `.git` in the baked source so `/a0` is a real Git worktree. Verify `git describe --tags --always`, `git rev-parse`, branch detection, and self-update version detection inside the rebuilt container.
- Set the baked `/a0` Git origin to `https://github.com/Omni-NexusAI/agent-zero.git` for this release path.
- Keep Agentspine-specific behavior in built-in overlay plugins whenever possible. The preserved overlay set for self-update compatibility is `_agentspine_identity`, `_enhanced_speech`, `_enhanced_mcp_config`, and `_multi_source_updater`.
- Do not include `plugins_custom/*` or runtime marketplace installs under `usr/plugins/*` in release images.
- Use visible banner prefix `D` for development/pre builds and reserve `M` for main/full release builds. For v0.9.9-pre standard builds, the banner should render as `D v0.9.9-standard-pre <timestamp>`.
- Do not bake `_provider_profiles` as a built-in plugin. Provider/model profile restore behavior belongs in `_model_config` and must preserve provider model, API base, and context length.
- Treat the main Agentspine image and Kokoro worker image as separate artifacts. Verify the worker sidecar and remote TTS discovery before release promotion.
- Do not push GHCR images until the corrected local image and sidecar stack pass verification and the user approves promotion.



