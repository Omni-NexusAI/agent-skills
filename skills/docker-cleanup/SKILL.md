---
name: docker-cleanup
description: >-
  Safely manages Docker disk during active development. It reclaims build
  waste continuously, retains only the minimal explicitly chosen recovery
  state, and never removes containers, referenced images, mounted volumes, or
  protected resources without confirmation. Use when the user wants to free up
  Docker disk space, clean up after failed builds, prevent build-image growth,
  or prune accumulated WSL Docker cache at C:\Users\yepyy\AppData\Local\Docker\wsl. Triggers include
  "docker cleanup", "prune docker", "clean up images", "free docker space",
  "docker taking up space", or "/docker-cleanup".
---

# Docker Cleanup

Read `C:/Users/yepyy/.claude/skills/docker-cleanup/protected.md` at the start of every run to load the current protected name patterns.

## Core Philosophy: Continuous Cleanup, Minimal Recovery

Do not defer cleanup until a long project is finished. At each meaningful build checkpoint, remove provable build waste and report the change. Keep only what is needed to run the active work or recover from its most recent known-good state.

The default is **KEEP** for containers, referenced images, mounted volumes, protected resources, and any named image whose purpose has not been classified. A named, unreferenced image is not an automatic deletion target, but it must not accumulate indefinitely: classify it at the next cleanup checkpoint as active, a single recovery image, or a confirmed removal candidate.

**Stopped != unused.** Users stop services they plan to restart. Never treat a stopped container as a cleanup target.

### Development Lifecycle Rules

1. **Before a storage-heavy build**, audit available host/Docker space. If capacity is tight, run the targeted build-waste cleanup before building.
2. **After every successful build, failed build, image replacement, or major experiment**, run a lightweight checkpoint: inspect Docker usage, remove unreferenced dangling images, and prune build cache. Do not wait for project closeout.
3. **Recovery limit:** retain at most one explicitly identified known-good rollback image per active service or experiment, in addition to images required by existing containers. Tag or record its purpose before treating it as retained.
4. **Superseded named images:** if an unreferenced image is replaced by a newer build and is neither active nor the one recorded recovery image, show it as a removal candidate at the next checkpoint and ask for confirmation. Never silently delete it.
5. **No speculative archives:** do not preserve multiple old images "just in case." If a rollback image is not necessary to continue or recover active work, offer to remove it.
6. **Space pressure wins:** when free space threatens the current task, pause further image-producing work, present the recovery plan and projected reclamation, and obtain confirmation before deleting named recovery candidates.

---

## Phase 1 - Audit (read-only)

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

## Phase 2 - Classify

Start with the assumption: **everything is WILL KEEP.** Only move items to WILL CLEAN if they match the build-waste rules below. When in doubt, keep.

### WILL KEEP (default for anything intentional)

An item stays on WILL KEEP if ANY of these are true:
1. It is a **container** in any status - running, stopped, exited, created, paused, restarting. All containers are intentional.
2. It is an **image with a name:tag** whose purpose is not yet classified, or it is the single recorded active/recovery image for its service.
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
| **Dead containers** | Container status is `dead` (Docker-marked unrecoverable). NOT `exited`, NOT `created`, NOT `stopped` - only `dead` |
| **Orphaned volumes** | Volume is not mounted by any container (running or stopped) |
| **Orphaned networks** | Custom network with zero connected containers; never bridge, host, or none |
| **Superseded named images** | Explicitly confirmed by the user, unreferenced by every container, not protected, and not the one recorded recovery image for active work |

---

## Phase 3 - Preview

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

Do NOT list every kept item individually - just show counts. Only list WILL CLEAN items in detail so the user can review what will be removed.

---

## Phase 4 - Confirm

Ask the user explicitly: **"Proceed with cleanup? (yes / no / adjust)"**

- If **no**: stop, report nothing was changed.
- If **adjust**: let the user specify items to move between lists, then re-show the preview.
- If **yes**: proceed to Phase 5.

---

## Phase 5 - Execute

Remove items from WILL CLEAN only, one category at a time. Use targeted removal commands - never broad prune commands that could overshoot.

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

If any single removal fails, log the error and continue with the rest - do not abort.

---

## Phase 6 - Report

Run `docker system df` again and show the before/after delta:

```
CLEANUP COMPLETE
================
Space before:  XX GB
Space after:   XX GB
Reclaimed:     XX GB
```

After an image-producing task, also report the retained recovery image by service and whether any superseded image awaits a user decision.

## Phase 7 - Docker WSL VHDX Compaction (Confirmed Default)

After Docker cleanup has completed and the user has validated the result, default to asking whether they are ready to compact Docker Desktop's WSL virtual disk unless they explicitly opted out earlier.

Ask clearly: **"Ready to compact Docker's WSL VHDX now? This will temporarily stop Docker Desktop and WSL. (yes / no)"**

- If **no**: stop and report that Docker cleanup is complete but VHDX compaction was skipped.
- If **yes**: proceed with the compaction flow below.
- If the user already explicitly asked to compact in the same turn, treat that as confirmation, but still report that Docker/WSL will be stopped before running the shutdown step.

### Compaction Flow

1. Record Docker state and the current VHDX size:

```powershell
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.ID}}"
Get-Item 'C:\Users\yepyy\AppData\Local\Docker\wsl\disk\docker_data.vhdx' | Select-Object FullName,Length,LastWriteTime
```

2. Stop Docker Desktop and WSL cleanly. Prefer a graceful Docker Desktop quit when available, then run:

```powershell
wsl --shutdown
```

3. Compact the VHDX. Prefer `Optimize-VHD` when the Hyper-V module is available:

```powershell
Optimize-VHD -Path 'C:\Users\yepyy\AppData\Local\Docker\wsl\disk\docker_data.vhdx' -Mode Full
```

If `Optimize-VHD` is unavailable, use `diskpart` with `select vdisk`, `attach vdisk readonly`, `compact vdisk`, and `detach vdisk`. Never compact while Docker Desktop or WSL is still running.

4. Restart Docker Desktop, wait for the daemon, then verify:

```powershell
docker info
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.ID}}"
Get-Item 'C:\Users\yepyy\AppData\Local\Docker\wsl\disk\docker_data.vhdx' | Select-Object FullName,Length,LastWriteTime
```

5. Report before/after VHDX size, whether Docker is healthy, and whether notable containers are still present.

### Sparse VHD Diagnostic

If compaction completes but the VHDX size does not shrink, check whether the VHDX is sparse:

```powershell
fsutil sparse queryflag "C:\Users\yepyy\AppData\Local\Docker\wsl\disk\docker_data.vhdx"
wsl --manage docker-desktop --set-sparse true
```

If WSL reports that sparse VHD support requires `--allow-unsafe`, do not run the unsafe command without explicit user approval. Report that the VHDX is non-sparse and that normal `fstrim`/`diskpart` compaction may not reclaim host space even after Docker data is removed.
### Compaction Safety Rules

1. Compaction is separate from cleanup. Do not delete extra Docker objects as part of compaction.
2. Always record the before/after VHDX size.
3. Always stop Docker Desktop/WSL before compacting the VHDX.
4. If neither `Optimize-VHD` nor a safe `diskpart` path is available, report the blocker instead of improvising.
5. Do not manually restart protected or user containers unless the user asks; only report their post-restart status.
---

## Safety Rules (non-negotiable)

1. **Never remove any container** unless its status is `dead`. Stopped/exited containers are intentional.
2. **Never remove a named image automatically.** A named image may be removed only after it is shown as superseded, confirmed unreferenced and unprotected, and explicitly approved by the user.
3. **Never remove an image referenced by any container** (running or stopped).
4. **Never remove a volume mounted by any container** (running or stopped).
5. **Never remove bridge, host, or none networks.**
6. **Never use `docker system prune`**, `docker image prune --all`, or any prune with `--all`.
7. If Docker daemon is not running, report that and stop.
8. If any removal command fails, log the error and continue - do not abort.
9. The protected.md list is an extra safety net, not the primary filter. Even without it, the rules above protect all intentional resources.



