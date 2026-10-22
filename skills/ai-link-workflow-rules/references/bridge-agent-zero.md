# Bridge and Agent Zero Workflow

## Source and mirror model

The bridge project is the authoritative source. The installed plugin is a
runtime mirror, and the project skill is a project-scoped mirror.

1. Change canonical source.
2. Run focused parsing, tests, and the skill validator.
3. Synchronize only the intended files into the installed plugin and project
   mirror.
4. Run `scripts/check_mirrors.py` against every mirror.
5. Validate the named Agent Zero runtime after synchronization.

Do not let successful edits in `/a0/usr/plugins` exist only in runtime state.
Do not copy generated caches, runtime data, secrets, or local logs back into
source.

## Plugin proof

A standalone `aiohttp` process proves the bridge core, not Agent Zero plugin
integration. Plugin proof requires:

- Discovery by the current Agent Zero plugin loader.
- A valid manifest and visible configuration surface when one is intended.
- Imports through the installed plugin namespace.
- Clean enable, disable, reload, and shutdown behavior.
- API, WebSocket, tool, or extension registration through supported plugin
  hooks.
- No required patch to updater-managed Agent Zero core.

Use the Agent Zero framework runtime for plugin verification. In the current
container that has been `/opt/venv-a0/bin/python`; rediscover it rather than
assuming the path forever.

## Wire and capability contract

- Keep `ailink.v1` unless a deliberate migration updates client, server,
  documentation, examples, negotiation, and compatibility tests together.
- Treat JSON control messages and binary media framing as one shared contract.
  Verify the implementation and `docs/protocol.md` agree before changing either.
- Reject or diagnose malformed envelopes and unknown media kinds without
  corrupting the session.
- Bound per-session queues and metrics; disconnects must release resources and
  permit a clean reconnect.

Capability responses must describe the deployed path:

- Do not advertise H.264 when only JPEG is implemented.
- Do not advertise task dispatch when the route is a scaffold or acceptance
  stub; expose scaffold state explicitly.
- Do not advertise return audio because client-to-server Opus packets arrive.
- Do not call text, audio, or metrics complete until the headset receives or
  renders them and recovery has been exercised.

## Focused verification ladder

1. Parse bridge Python and validate manifests/configuration.
2. Run the bridge smoke check and focused unit tests.
3. Run a synthetic client through hello, start, media/control traffic, ping,
   stop, malformed input, disconnect, and reconnect.
4. Confirm counters and diagnostics reflect known test traffic.
5. Confirm Agent Zero discovery and lifecycle in the named v2.8-or-current
   runtime.
6. Connect the real Unity client and validate both directions.

An HTTP 200, accepted task request, or incremented frame counter is evidence for
that layer only.
