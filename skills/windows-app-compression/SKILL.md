---
name: windows-app-compression
description: >-
  Analyze or, after exact approval, compress a specific Windows application or
  runtime subfolder with CompactGUI, NTFS compression, or WOF/compact.exe. Use
  for Windows app compression, CompactGUI assessment, NTFS/WOF compression, or
  recovering space from a named installed app. It shares storage-awareness
  policy and never treats a whole launcher ecosystem, model data, Docker, WSL,
  or VHDX files as eligible.
---

# Windows App Compression

This is a direct application-compression skill, not a cleaner. Use the sibling
`storage-awareness` policy map and helper; do not create a second protection or
approval list. Audit first, and require an exact reviewed target approval for
existing apps and runtimes.

## Boundaries

Hard-exclude model weights, checkpoints, model caches, and linked aliases
(including hardlinks) when content or identity is uncertain. Exclude VHDX,
Docker, and WSL compaction: route those to the Docker specialist. Never compress
an entire Pinokio installation; assess one concrete app/runtime subfolder.

Distinguish logical length, allocated size, and observed post-operation savings.
`compact /q` samples do not establish a tree-wide state or a savings estimate.
Select an algorithm only from measured evidence, existing WOF-aware state, a
bounded test, and application smoke checks. No blanket compression or deletion.

## Workflow

1. Run the shared storage preflight and validate a fresh private map.
2. Run `scripts/windows_app_compression.py analyze` for the exact subfolder.
3. Review exclusions, dependencies, current state, estimate confidence, and a
   concrete rollback/smoke plan with the user.
4. Only then run `execute` with an exact compression grant. Recheck immediately
   before action, make a bounded test first, smoke the affected app, and log
   actual before/after allocation. On a failure, stop—do not broaden scope.

```powershell
python scripts/windows_app_compression.py analyze --target C:\App\runtime --storage-awareness-path ..\storage-awareness
python -m unittest discover -s tests -v
```
