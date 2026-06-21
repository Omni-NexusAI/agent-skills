---
name: cursor-workflow-rules
description: Archived platform-specific workflow rules retained for historical reference. Do not use for new work; use agent-workflow-rules instead.
---

# Archived: Cursor Workflow Rules

This legacy skill is retained as an archive. Use `agent-workflow-rules` for active work.

## Purpose

Apply these rules as hard constraints whenever working for this user.

## Core Workflow Rules

1. Use PR-first workflow for GitHub repos:
   - Create PR first.
   - Plan feature/fix.
   - Implement in environment.
   - Test.
   - Push commits into PR.
   - Repeat plan/implement/test/push until user verifies results are satisfactory.
   - Merge only after explicit user approval.
2. Never push or merge directly into a branch without a PR unless the user explicitly allows it.
3. When pulling from a branch in the user's repos, pull fresh image(s) and fresh environment(s) with latest code so newest implemented features are available.
4. If something must be pulled from one of the user's repos, always use Omni-NexusAI.

## MCP and Tooling Rules

1. Prefer non-Windows MCP tools first. Use Windows MCP only when other MCP tools cannot solve the task due to limitations.
2. For newly installed MCP servers, set them up at:
   - `C:/Users/yepyy/Documents/MCPs`
3. Use Context7 whenever up-to-date documentation is needed.

## Environment and Dependency Rules

1. If installing non-dockerized localhost packages/dependencies, use a Conda environment when applicable.
2. Default to existing environments (Docker, Conda, etc.).
3. If a new environment instance is required:
   - Back up all instance data for transfer.
   - Migrate previous settings.
   - Start the new environment for testing.

## Bind Mount First Workflow (Default)

For Dockerized development and debugging, default to a bind-mount-first iteration loop whenever source-level changes can be tested from the host workspace.

1. Inspect the current container or Compose service first to see whether useful bind mounts already exist.
2. If useful bind mounts do not exist, prefer one-time container/service recreation with bind mounts over repeated image rebuilds.
3. Iterate by editing host files, then using the lightest effective refresh path: browser reload, app reload, process restart, or container/service restart.
4. Rebuild images only when the change must live in an image layer, such as:
   - Dockerfile or base image changes.
   - System package or runtime installation changes.
   - Dependency installs or lockfile changes that must exist inside the image.
   - Startup-time environment, entrypoint, or build metadata changes.
   - Generated or compiled assets that cannot be refreshed from mounted source.
5. When skipping the bind-mount-first loop, briefly explain why a rebuild is required.

## Docker Image Update Rules

When updating requested Docker images:

1. Ensure data from previous environment is carried over to the new image(s).
2. Clean up only older unused images related to that requested environment.
3. Do not touch containers outside the relevant environment(s).

## Trigger Scenarios

Apply this skill whenever the task involves any of the following:

- GitHub repos, branching, PRs, commits, pushing, merging, or pulling.
- Environment setup, migration, or dependency installation.
- Dockerized development, bind mounts, local container testing, image rebuilds, Docker image updates, or iterative debugging.
- MCP server/tool selection.
- Documentation lookup for libraries/frameworks/APIs.

## Conflict Resolution Priority

If instructions conflict:

1. Follow explicit direct user instructions in the current request.
2. Otherwise apply these workflow rules.
3. If uncertainty remains, ask a focused clarifying question before acting.
