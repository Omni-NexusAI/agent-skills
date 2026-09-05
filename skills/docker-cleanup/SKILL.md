---
name: docker-cleanup
description: >-
  Apply storage awareness whenever a task accesses Docker, including builds,
  pulls, runs, Compose workflows, tests, exports, and sustained container writes.
  Require schedule enrollment, safe pause-clean-resume checkpoints, and explicit
  Windows host-space and compaction follow-through. It preserves active work,
  recovery identities, referenced images, volumes, and protected resources.
---

# Docker Cleanup

Read the sibling `protected.md` at the start of every run. If it is unavailable,
perform an audit only until protection can be established.

## Required scheduling and storage-pressure workflow

### Schedule enrollment

At the first cleanup invocation and on subsequent runs, inspect the available
scheduler for an enabled Docker-cleanup job for the same machine and Docker
context. Verify its scope, cadence, authorization, and next run; never create a
duplicate or silently re-enable a paused job. A skill is not a scheduler.

If no suitable job exists, setup is required onboarding: propose a concrete
cadence (every 6 hours in the user's timezone is the default proposal), the
automatic scope below, and quiet-notification behavior. Obtain any missing
authorization, then create and read back the job using the host's supported
scheduler. In Codex, use a thread heartbeat by default. Reuse existing
authorization. If scheduling is unavailable or declined, persist that
pending/declined disposition with its reason; it does not block urgent,
separately authorized cleanup.

Keep a small durable operational record for the scheduled workflow: machine and
context, cadence, approved scope, last result, next retry, thresholds,
active/recovery identities, and pending compaction with its revisit checkpoint.
Each run reloads this skill and `protected.md`, audits afresh, and never replays
old deletion IDs. Do not create a live schedule merely because this skill was
edited or used in a pull request.

Scheduled runs stay quiet when unchanged or non-actionable; notify only on
meaningful reclamation, critical pressure, failure, or required user action. If
Docker is off, skip without starting it. Use a shared machine/context lock to
prevent overlapping cleanups. An uncertain lock or workload owner means audit
only. A background run must not interrupt builds, pulls, exports, containers,
or other WSL workloads.

### Automatic scope and confirmation

Within an authorized cleanup task or enrolled schedule, no repeated confirmation
is needed only for provably disposable, unprotected, unreferenced dangling
images and eligible unused build cache. Immediately before removal, re-check
container references, `protected.md`, recorded recovery identities, and current
build activity. Unknown provenance or protection means **KEEP**.

Containers, volumes, named images, and custom networks require explicit,
target-specific approval. Do not force removal or broaden pruning after a
failure. Keep useful recent cache: at healthy capacity, prefer old disposable
entries (48 hours is a tunable starting point) and use filters supported by the
actual builder. Under pressure, reclaim only eligible unused cache at an idle
checkpoint and only as far as required. If a builder cannot reliably exclude
protected cache, skip pruning it. Never blanket-prune cache after every build.

### Predict pressure before producing more data

Apply this to Docker-dependent work generally, not only cleanup requests or
builds. For read-only access, make a lightweight capacity check without
interrupting healthy work. For runs, Compose workflows, tests, downloads, logs,
exports, and other sustained writes, budget growth and monitor while work
continues. Carry checkpoints into the owning task or a verified scheduler; a
one-time skill invocation cannot monitor after the task ends.

Measure free bytes on the host volumes containing Docker storage, build context,
temporary files, and outputs before a large build, pull, or export; between
stages where practical; and after image-producing success or failure. Discover
the configured Docker storage location rather than assuming a path. Measure
guest filesystem headroom when available; it is not Windows free capacity.

Estimate the next operation's peak incremental demand from measured growth,
download/unpack overlap, intermediates, outputs, and concurrent writers. Use
configurable starting thresholds: reserve = max(10 GiB, 5% of host volume);
warning floor = max(20 GiB, 10%). Do not start a heavy operation unless host
free space exceeds estimated peak demand plus reserve. Unknown demand near the
warning floor requires a conservative budget or smaller stage.

At warning pressure, plan cleanup for the next safe checkpoint. If the next
operation cannot fit or free space reaches reserve, pause only the affected
storage-producing work at its earliest safe boundary; continue independent work
where practical. Never kill a running operation solely to clean. During long
operations, use bounded free-space checks (about every five minutes when
practical, sooner if measured growth could exhaust reserve).

Audit and perform authorized cleanup, then remeasure host and guest capacity.
Resume the paused work automatically and promptly only once the next operation
plus reserve fits. If Docker's logical usage improves but Windows free space
does not, queue compaction rather than repeatedly retrying the same heavy work.
If safe waste is insufficient, report approval-required candidates or a
reduced-space plan.

### Compaction disposition

After cleanup on a Windows WSL backend, record exactly one disposition:
**not needed** (with measurements), **completed and verified**, **awaiting
permission**, or **deferred** (with a reason and revisit checkpoint). Preserve
unresolved compaction through handoff and scheduled retries. Offer useful WSL
VHDX compaction, but obtain approval for the Docker/WSL interruption. Do not
repeatedly prompt during the same busy period.

Before approved compaction, identify affected Docker and WSL workloads and
verify the current disk path. Restore Docker availability afterward and compare
container presence/status; do not start user workloads without authorization.
Verify separately: Docker logical usage, VHDX file length and physical
allocation when measurable, and actual host-volume free bytes. Sparse-file
length alone is not physical allocation. A Windows restart is an optional,
user-approved last diagnostic, never an automatic or guaranteed remedy.

References: [Docker build-cache GC](https://docs.docker.com/build/cache/garbage-collection/),
[Microsoft compact vdisk](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/compact-vdisk),
and [WSL disk space](https://learn.microsoft.com/en-us/windows/wsl/disk-space).

## Core Philosophy: Continuous Cleanup, Minimal Recovery

Do not defer cleanup until a long project is finished. At each meaningful build checkpoint, remove provable build waste and report the change. Keep only what is needed to run the active work or recover from its most recent known-good state.

The default is **KEEP** for containers, referenced images, mounted volumes, protected resources, and any named image whose purpose has not been classified. A named, unreferenced image is not an automatic deletion target, but it must not accumulate indefinitely: classify it at the next cleanup checkpoint as active, a single recovery image, or a confirmed removal candidate.

**Stopped != unused.** Users stop services they plan to restart. Never treat a stopped container as a cleanup target.

### Development Lifecycle Rules

1. **Before a storage-heavy build**, audit available host/Docker space. If capacity is tight, run the targeted build-waste cleanup before building.
2. **After every successful build, failed build, image replacement, or major experiment**, run a lightweight capacity checkpoint and remove eligible waste only under the automatic scope and cache-retention rules above. Do not wait for project closeout or blindly prune useful cache.
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
| **Build cache** | Eligible unused, unprotected cache under the retention and idle-checkpoint rules above; a reported total is not a removal plan |
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

For the authorized automatic scope above, proceed without repeated confirmation.
For approval-required resources, list exact targets separately and ask:
**"Proceed with these listed targets? (yes / no / adjust)"** Scheduled runs queue
those targets for review and continue only with the automatic scope.

- If **no**: stop, report nothing was changed.
- If **adjust**: let the user specify items to move between lists, then re-show the preview.
- If **yes**: proceed to Phase 5.

---

## Phase 5 - Execute

Remove items from WILL CLEAN only, one category at a time. Use targeted removal commands - never broad prune commands that could overshoot.

```bash
# Dangling images (by ID, one at a time)
docker rmi <image-id>

# Build cache: only at an idle checkpoint and only where the actual builder
# supports this retention filter
docker builder prune -f --filter "until=48h"

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

## Phase 7 - Docker WSL VHDX Compaction

After Docker cleanup, follow the compaction disposition above. Do not silently
omit useful compaction while it awaits validation or an interruption window.

Ask clearly: **"Ready to compact Docker's WSL VHDX now? This will temporarily stop Docker Desktop and WSL. (yes / no)"**

- If **no**: stop and report that Docker cleanup is complete but VHDX compaction was skipped.
- If **yes**: proceed with the compaction flow below.
- If the user already explicitly asked to compact in the same turn, treat that as confirmation, but still report that Docker/WSL will be stopped before running the shutdown step.

### Compaction Flow

1. Record Docker state and the current VHDX size:

```powershell
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.ID}}"
$vhdxPath = '<discovered Docker WSL VHDX path>'
Get-Item $vhdxPath | Select-Object FullName,Length,LastWriteTime
```

2. Stop Docker Desktop and WSL cleanly. Prefer a graceful Docker Desktop quit when available, then run:

```powershell
wsl --shutdown
```

3. Compact the VHDX. Prefer `Optimize-VHD` when the Hyper-V module is available:

```powershell
Optimize-VHD -Path $vhdxPath -Mode Full
```

If `Optimize-VHD` is unavailable, use `diskpart` with `select vdisk`, `attach vdisk readonly`, `compact vdisk`, and `detach vdisk`. Never compact while Docker Desktop or WSL is still running.

4. Restart Docker Desktop, wait for the daemon, then verify:

```powershell
docker info
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.ID}}"
Get-Item $vhdxPath | Select-Object FullName,Length,LastWriteTime
```

5. Report before/after VHDX size, whether Docker is healthy, and whether notable containers are still present.

### Sparse VHD Diagnostic

If compaction completes but the VHDX size does not shrink, check whether the VHDX is sparse:

```powershell
fsutil sparse queryflag $vhdxPath
```

Sparse-mode changes are mutations, not diagnostics. Do not enable sparse mode
or unsafe options automatically. A non-sparse disk alone does not explain a
failed compaction; verify the disk, offline state, trim prerequisites, physical
allocation, and host free bytes before drawing a conclusion.
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
