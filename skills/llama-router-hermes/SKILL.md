---
name: llama-router-hermes
description: Set up or troubleshoot llama.cpp routers locally or over LAN/Tailscale and connect agent frameworks through their native API adapters, with authentication, scoped firewall access, and verified inference. Includes a Hermes Agent adapter.
---

# Framework-independent llama.cpp router setup

Deliver a working selected-model chat through the user's chosen agent framework, not merely a listening port, populated model card, or successful fallback reply. Router setup must not depend on Hermes being installed. The historical skill identifier is retained for existing invocations; its router procedure is framework-independent.

## Discover the topology

Record server/client machines, operating systems, installed router and chosen client versions, executable/config paths, model aliases, intended transport, and authorization for changes. Inspect existing launchers and providers before editing. Preserve host-local models separately from remote models; use distinct labels where the client supports them. Example addresses are not defaults.

Read [references/runbook.md](references/runbook.md) for shared server/network setup and the generic client adapter contract. Read [references/hermes-agent.md](references/hermes-agent.md) only for Hermes configuration and tests. Read [references/verified-case.md](references/verified-case.md) only for this user's September 2026 two-Windows-machine example; recheck its facts before reuse.

## Required invariants

- Establish a local router inference baseline before diagnosing a remote agent client. Discover installed router flags/config format from its own help and existing launchers; do not assume all llama.cpp builds use the same router schema.
- Advertise actual served per-slot context and capabilities. A model's theoretical maximum or total context divided across slots is not necessarily its usable request window. Never increase client metadata just to bypass a minimum-context guard; client-specific minimums are not universal router requirements.
- Treat API keys as secrets: use an environment-variable reference or supported secret store, never embed them in the skill, model cards, logs, command-line arguments, or cross-task messages. Compare authentication without printing credentials.
- Scope network exposure to the chosen interface and authorized peers. Do not disable firewall/VPNs, open all profiles/addresses, change Tailscale ACLs, or start competing GPU workers merely to get a pass.
- Normal client-to-server inference usually needs inbound access on the server and outbound access on the client, not a mirrored client inbound rule. Add client inbound rules only for an identified reverse connection/service requirement.
- Model swaps, cold loading, prompt ingestion, and generation are different phases. Verify activity before restarting; avoid concurrent benchmark requests against a single-slot router.
- Verify the saved session's provider/base URL/model and correlated server activity. Model self-identification and correct-looking output do not establish provenance.
- Text first. Test images only when requested and supported; distinguish native image input from an auxiliary image-description tool and from final-answer generation.

## Finish

For another agent architecture, reuse the server/network/authentication gates, then discover that client's actual API adapter and context/tool/image requirements. Do not copy Hermes YAML into another client or assume OpenAI-compatible transport implies agent/tool compatibility. Keep client-specific instructions separate and validate an actual owning-client chat before claiming support.

Report what changed, which local and remote owning-client chats passed, any fallback, image/tool involvement, and unsupported models or protocols. Preserve or restore the user's original new-chat default where a temporary selection was used. Leave a compact non-secret topology and evidence record, with rollback details for any changed configuration or firewall rule.
