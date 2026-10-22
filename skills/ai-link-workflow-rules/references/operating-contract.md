# Operating Contract

## Authority and sources

Apply sources in this order unless the user explicitly changes it:

1. Current user instructions and granted authority.
2. The applicable `AGENTS.md` chain for every target.
3. Live source, serialized configuration, runtime state, and current primary
   documentation for installed libraries or SDKs.
4. Live Linear issue state and acceptance criteria.
5. The paired AI-Link development plan for architecture and sequencing.
6. Project notes, stored chats, and memory as historical leads.

When sources disagree, preserve the live execution state, surface the mismatch,
and avoid broad implementation until the architectural intent is clear.

## Durable boundaries

- **Unity client:** XR lifecycle, capture, input, playback, UI, diagnostics, and
  client-side transport.
- **Wire contract:** `ailink.v1` control envelopes, binary framing, negotiation,
  ordering, failure responses, and compatibility behavior.
- **AI Link bridge:** transport ingress/egress, validation, sessions, metrics,
  adapters, and portable plugin packaging.
- **Agent Zero:** plugin discovery, lifecycle, settings, APIs/tools, and actual
  AI or task integration.
- **AINexus:** a later consumer of the validated portable plugin and contract,
  not a reason to couple prototype code to one current Agent Zero layout.

Assign one source owner to each behavior. Avoid parallel implementations whose
differences are hidden behind the same capability name.

## Canonical and deployed paths

Verify paths before use. The current intended layout is:

- Unity source: `C:\Users\yepyy\Documents\Unity Projects\AI_Link_Unity`
- Bridge source: `/a0/usr/projects/ai-link/backend_plugins/ai_link_bridge`
- Installed plugin: `/a0/usr/plugins/ai_link_bridge`
- Project skill mirror:
  `/a0/usr/projects/ai-link/.a0proj/skills/ai-link-workflow-rules`
- Canonical skill source:
  `/a0/usr/projects/ai-link/backend_plugins/ai_link_bridge/skills/ai-link-workflow-rules`

Edit canonical source, validate it, and synchronize outward. Never repair a
deployed copy without also reconciling the canonical source.

## Tool routing

- Use Unity-aware tooling when scene serialization, object references, console
  state, or Play Mode matters; use filesystem inspection for source truth.
- Use the current connected Linear capability for roadmap state. Do not require
  Hermes, a particular MCP, or browser automation when a more direct verified
  route exists.
- Use container tools for Agent Zero and bridge runtime state, and host tools
  only for host-owned files, processes, desktop UI, or device connectivity.
- Fetch current primary documentation for changing Unity, Meta XR, OpenXR,
  Agent Zero, or plugin APIs before version-sensitive implementation.

## Change discipline

- Preserve dirty trees, named containers, volumes, user data, and live services.
- Prefer bind-mounted or reloadable iteration when it represents the target
  runtime accurately; rebuild only for image, dependency, startup, or generated
  layers that require it.
- Use a dedicated branch and pull request when the owning repository has a
  collaboration workflow. Do not commit, push, merge, publish, replace, or
  delete without the required authority.
- Never store secrets in the skill, repository, logs, snapshots, or examples.
