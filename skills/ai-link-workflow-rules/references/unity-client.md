# Unity Client Workflow

## Preflight

1. Read the Unity project root `AGENTS.md` and the closest child contract for
   every source, scene, settings, or documentation target.
2. Capture the dirty-state baseline without resetting it. Treat modified,
   untracked, generated, and serialized assets as user-owned.
3. Read `ProjectVersion.txt`, `Packages/manifest.json`, the package lock,
   OpenXR settings, build targets, scene wiring, and runtime configuration
   rather than relying on dated roadmap versions.
4. Determine whether the test uses Editor simulation, Quest Link, or an Android
   build. These paths do not prove one another.

## Unity control

- Load and follow Unity's official [`unity-cli` skill](https://github.com/Unity-Technologies/skills/blob/main/skills/unity-cli/SKILL.md)
  for CLI installation, project and Editor lifecycle, licensing, and Pipeline
  command syntax. Keep this reference authoritative instead of copying its
  changing command guide into the AI-Link skill.
- Target the exact AI-Link project and the Editor version pinned by
  `ProjectVersion.txt`.
- When the Editor is stopped, open the project with Unity CLI. When a running
  Editor reports healthy Pipeline status and command responses, use Pipeline
  for readiness, Play/Stop, logs, screenshots, tests, and repeat cycles.
- Use direct Windows control only for Unity Hub, licensing, Safe Mode, a focus
  click needed to reload, or another blocking dialog. Use Unity MCP for richer
  scene-aware work only when its existing server is active.
- If Unity CLI is unavailable, launch the exact Editor executable with
  `-projectPath` and a dedicated `-logFile`. A responsive Editor with an
  unresponsive Pipeline connection is a failed automation state; preserve its
  logs and obtain a safe graceful-restart boundary before continuing.
- Do not configure Unity CLI's additional MCP server while the existing Unity
  MCP overlaps it or before the current stability gate passes.
- After an Editor restart, poll Pipeline until it is ready and verify Play/Stop,
  log retrieval, screenshot capture, and automatic reconnection without
  depending on manually re-enabling Unity MCP.

## Client architecture

Keep these responsibilities separable:

- Capture source and frame metadata.
- Preprocessing and encoder.
- WebSocket or later transport.
- Protocol/session orchestration.
- Audio capture and return playback.
- Input and tracking.
- HUD, logs, and operator diagnostics.

Preserve Unity main-thread requirements. Queue network callbacks for main-thread
state and object changes, bound queues, and clean up subscriptions, encoders,
audio sources, sockets, and XR-owned resources on every exit path.

## Passthrough and XR

- Verify the official API against the installed Meta XR/MRUK and Unity package
  versions before coding. Do not confuse a composition layer with readable
  camera imagery or assume an old `WebCamTexture` route remains supported.
- Keep desktop or simulated capture available so protocol work can proceed
  without headset access, but never present simulation as device proof.
- Preserve the XR Origin and the components required for controller and hand
  input. Disable only the AR or spatial-visualization producer responsible for
  an overlay; do not solve a visual defect by removing all tracking.
- Make passthrough-layer ownership deterministic. A "first object found" rule
  is not deterministic when multiple layers or prefabs can instantiate.
- Keep the simulated environment world-anchored when it is used as a comparison
  reference.

## Scene and asset edits

- Prefer Unity/editor-aware changes for scenes, prefabs, materials, and
  serialized references. If a text edit is unavoidable, verify GUIDs, file IDs,
  enable states, and the resulting Editor import.
- Preserve `.meta` files and GUID identity. Do not regenerate packages or
  rewrite broad scene YAML to change one component.
- Treat warnings about modified package-cache or package assets as state drift
  to investigate, not harmless noise.

## Verification

- Compile and inspect the current console before Play Mode.
- Verify each input mode independently: controller tracking and hand tracking.
- Exercise video, audio, input, text, diagnostics, and reconnect concurrently;
  isolated success can hide queue starvation or cleanup faults.
- For the current prototype recovery gate, use five clean Play/Stop cycles
  (three Editor-only and two Quest Link) followed by a ten-minute development
  soak. Use the live Linear acceptance duration, such as a longer stream soak,
  before recommending issue closure.
- Record what the user sees in both eyes, not only what the Unity console says.
