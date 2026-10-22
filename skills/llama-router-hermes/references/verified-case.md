# Historical two-machine case — September 23, 2026

These are recorded observations, not current-state guarantees. Recheck addresses, versions, profiles, keys, and server health before applying them. No credential belongs in this file.

- Windows laptop Tailscale address: `100.75.98.97`; Windows desktop: `100.96.86.99`.
- Desktop router base URL: `http://100.96.86.99:8080/v1`; bearer authentication from `LLAMA_API_KEY`.
- Laptop provider names: local `llama.cpp` and remote `llama.cpp Desktop`. The local provider was preserved separately.
- Laptop Hermes build observed: v0.21.4 (+1066), f80d888. Its agent initialization imposed a 64,000-token minimum for these providers. This was a build-specific observation, not a universal Hermes contract.

## Successful laptop-to-desktop checks

| Router alias | Result |
|---|---|
| `qwen38-27b-apex-mini-vision` | Real laptop GUI text reply; saved provider `custom`, desktop base URL, no OpenRouter fallback. User image turn also completed; selected model called `vision_analyze`, so do not describe this as an auxiliary-tool-free native vision benchmark. |
| `qwen38-27b-apex-mini` | Laptop Hermes CLI text reply `apex-text-laptop-ok`; saved custom desktop provider, one API call. |
| `ornith-1.5-35b-gpukv-128k-vision` | Laptop Hermes CLI text reply `ornith-laptop-ok`; saved custom desktop provider, one API call. No separate image acceptance. |

An earlier GUI reply appeared successful but the saved session showed OpenRouter. Restarting Hermes with the saved key inherited by its process fixed that configuration gap. Correct text alone was misleading.

## Deferred UD profiles

- `qwen38-27b-ud-q4km-vision`: actual router properties reported 32,768 context. Laptop GUI and CLI refused before sending, with zero API calls.
- `qwen38-27b-ud-q4km`: configured context 57,344; laptop preflight refused. That configured number was not independently established as actual served context in the final laptop test.
- Desktop historically displayed a UD Vision short reply, but no retained provider-call evidence or reproducible workaround established that it bypassed this newer laptop guard legitimately. UD text-only had a reported direct API check, not a proven desktop Hermes chat.
- The user explicitly deferred UD changes/tests until larger served context is feasible. Do not set fake 64K card metadata or patch out Hermes safeguards based on this historical reply.

## Useful installation locations from that case

Hermes home: `%LOCALAPPDATA%\hermes`; config: `config.yaml`; saved sessions: `state.db`; CLI: `bin\hermes.exe`. Inspect current paths/schema rather than hardcoding them for other machines.

## Desktop launcher inspection — September 26, 2026

The owning desktop task inspected these files without starting the router or running inference:

- Executable: `C:\llama.cpp\llama-server.exe`; preset header identifies v9626 (header evidence, not a fresh executable-version check).
- Launcher directory: `D:\llama-server\llama router`; `Start-LlamaRouter.bat` invokes `Start-LlamaRouter.ps1`.
- Presets: `codex-qwen-router-presets.ini`, `version = 1`; section names are routable model IDs. This implementation controls child alias/host/port/auth arguments at the router level, so do not put those in child presets.
- Launch command: `--models-preset <preset-file> --models-max 1 --host 0.0.0.0 --port 8080 --sleep-idle-seconds 600 --metrics --slots`. Wildcard exposure depends on a narrow firewall rule; do not reuse this bind as an unconditional default.
- Launcher refuses a second instance when port 8080 already listens. It can decrypt `router-api-key.dpapi` under Windows DPAPI CurrentUser; that file is user-bound, not a portable client credential. Authentication values were not printed.
- The specialized DFlash2 executable is deliberately excluded from these router presets. Do not swap binaries casually.

Inspected preset contexts: Ornith 131072, APEX text 81920, APEX Vision 65536, UD text 57344, UD Vision 32768. These are configured values; verify actual per-slot runtime properties after load. Qwen presets explicitly use one slot; Ornith's inspected section does not explicitly specify `parallel`, so do not infer one-slot context solely from its `c` value.

APEX text/vision share an APEX Mini GGUF; vision adds its matching Qwen3.8 F16 projector. UD text/vision share a UD Q4_K_M GGUF; vision adds the matching projector. Qwen presets use q8_0 KV caches, automatic flash attention, Jinja, and no warmup; APEX and most UD presets use batch 1024/microbatch 256, while UD Vision uses 256/64. GPU split `35,65`, GPU layers `99`, and Ornith `main-gpu=1` reflect this desktop's hardware and are not portable tuning defaults.
