---
name: docker-cleanup
description: >-
  Safely cleans Docker build waste — dangling images, build cache, orphaned
  volumes, dead containers, and unused networks — using a "build waste only"
  philosophy. Never touches stopped containers, named images, or anything
  referenced by an existing container. The protected.md file is an extra safety
  net, not the primary filter. Use when the user wants to free Docker disk
  space, clean up after failed builds, or prune accumulated Docker build waste.
  Triggers include "docker cleanup", "prune docker", "clean up images",
  "free docker space", "docker taking up space", or "/docker-cleanup".
---

# Docker Cleanup

Read `protected.md` from this same skill directory at the start of every run to load current protected name patterns.

## Core Philosophy: Build Waste Only

This skill only removes artifacts that no user intentionally created. The default for everything is **KEEP**. An item must be provably build waste to be a cleanup candidate.

**Stopped != unused.** Users stop services they plan to restart. Never treat a stopped container as a cleanup target.

---

## Phase 1 — Audit (read-only)

Run all of these before touching anything:

```bash
docker system df
docker images -a --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}"
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.ID}}"
docker images -f dangling=true --format "{{.ID}}\t{{.Size}}"
docker volume ls -f dangling=true --format "{{.Name}}"
docker network ls --format "{{.Name}}\t{{.Driver}}"
docker builder du
```

---

## Phase 2 — Classify

Start with the assumption: **everything is WILL KEEP.** Only move items to WILL CLEAN if they match the build-waste rules below. When in doubt, keep.

### WILL KEEP (default for anything intentional)

An item stays on WILL KEEP if ANY of these are true:
1. It is a **container** in any status — running, stopped, exited, created, paused, restarting. All containers are intentional.
2. It is an **image with a name:tag** — if the repository is not `<none>`, someone or a compose file created it on purpose.
3. It is an **image referenced by any container** (running or stopped), even if the image itself is dangling.
4. It is a **volume mounted by any container** (running or stopped).
5. It **matches any pattern** from `protected.md` (extra safety net).
6. It is a **built-in network**: bridge, host, none.

### WILL CLEAN (only provable build waste)

An item is a cleanup candidate ONLY if ALL of these are true for its category:

| Category | Criteria |
|----------|----------|
| **Dangling images** | Repository AND tag are both `<none>`, AND the image is NOT referenced by any container (running or stopped) |
| **Build cache** | All BuildKit cache entries reported by `docker builder du` |
| **Dead containers** | Container status is `dead` (Docker-marked unrecoverable). NOT `exited`, NOT `created`, NOT `stopped` — only `dead` |
| **Orphaned volumes** | Volume is not mounted by any container (running or stopped) |
| **Orphaned networks** | Custom network with zero connected containers; never bridge, host, or none |

---

## Phase 3 — Preview

Display a formatted summary before doing anything:

```
DOCKER CLEANUP PREVIEW
======================
Space before:  XX GB (from docker system df)

WILL CLEAN:
  Dangling images:   N items  (~X GB)
  Build cache:       ~X GB
  Dead containers:   N items
  Orphaned volumes:  N items
  Orphaned networks: N items

WILL KEEP (summary):
  Containers:        N total (N running, N stopped)
  Named images:      N total
  Protected matches: N items
  Mounted volumes:   N total

Estimated space to reclaim: ~X GB
```

Do NOT list every kept item individually — just show counts. Only list WILL CLEAN items in detail so the user can review what will be removed.

---

## Phase 4 — Confirm

Ask the user explicitly: **"Proceed with cleanup? (yes / no / adjust)"**

- If **no**: stop, report nothing was changed.
- If **adjust**: let the user specify items to move between lists, then re-show the preview.
- If **yes**: proceed to Phase 5.

---

## Phase 5 — Execute

Remove items from WILL CLEAN only, one category at a time. Use targeted removal commands — never broad prune commands that could overshoot.

```bash
# Dangling images (by ID, one at a time)
docker rmi <image-id>

# Build cache
docker builder prune -f

# Dead containers (by ID)
docker rm <container-id>

# Orphaned volumes (by name)
docker volume rm <volume-name>

# Orphaned networks (by name)
docker network rm <network-name>
```

**Never** pass `--all` to any prune command. **Never** use `docker system prune`. **Never** use `docker image prune --all`.

If any single removal fails, log the error and continue with the rest — do not abort.

---

## Phase 6 — Report

Run `docker system df` again and show the before/after delta:

```
CLEANUP COMPLETE
================
Space before:  XX GB
Space after:   XX GB
Reclaimed:     XX GB
```

---

## Safety Rules (non-negotiable)

1. **Never remove any container** unless its status is `dead`. Stopped/exited containers are intentional.
2. **Never remove a named image** (any image where repository is not `<none>`).
3. **Never remove an image referenced by any container** (running or stopped).
4. **Never remove a volume mounted by any container** (running or stopped).
5. **Never remove bridge, host, or none networks.**
6. **Never use `docker system prune`**, `docker image prune --all`, or any prune with `--all`.
7. If Docker daemon is not running, report that and stop.
8. If any removal command fails, log the error and continue — do not abort.
9. `protected.md` is an extra safety net, not the primary filter. Even without it, the rules above protect all intentional resources.
