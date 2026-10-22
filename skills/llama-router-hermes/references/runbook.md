# Setup and diagnostic runbook

## 1. Establish the server locally

Inspect the existing router command line, launcher/config, listener ownership, GPU workload, and model files. Get the installed executable's help before constructing flags. Coordinate with the owning desktop Codex task when remote server access is available; ask for exact effective settings and evidence, not just a ready/status label.

For each alias, resolve the model file, quantization, vision projector where needed, effective per-slot context, slots, GPU/CPU placement, and backend endpoint. Preserve stable alias identity between router catalog and the client. Verify router process ownership and avoid launching a second instance when a lock is held.

Bind to the approved interface/address that receives remote traffic. Loopback-only binding cannot receive Tailscale requests. A wildcard bind exposes every interface unless firewall policy narrows it; prefer a specific address where supported and operationally suitable. Configure router authentication consistently across workers/front door according to the installed implementation.

Validate loopback or server-local address, authenticated model catalog, then a short text completion for an intended alias. Use a bounded output and timeout suitable for cold model load. Record status/error without secrets. A catalog pass does not prove model loading or inference.

## 2. Verify network layers independently

Discover actual peer addresses and routes; do not copy historical addresses blindly. On Windows use non-mutating checks such as:

```powershell
Get-NetTCPConnection -State Listen -LocalPort $RouterPort
Get-NetConnectionProfile
Test-NetConnection -ComputerName $ServerAddress -Port $RouterPort
```

Use installed Tailscale status/ping/help to verify overlay identity and reachability. An overlay ping does not prove TCP access. ICMP failure does not prove an HTTP outage. A Telnet-style test is only a raw TCP handshake, not authentication or inference; `Test-NetConnection` avoids installing a Telnet client unnecessarily. UDP testing is relevant to Tailscale transport diagnostics, not to an HTTP llama.cpp API itself.

Then use authenticated HTTP against the same address/port/base path the client will use. Bypass a proxy for this single diagnostic if justified, without globally changing VPN/proxy configuration. Classify results:

| Result | Check next |
|---|---|
| Local API fails | Router/worker startup, alias, backend health, auth, capacity |
| Overlay works, TCP fails | Bind address, effective server firewall, client outbound/VPN routes, tailnet policy |
| TCP works, HTTP 401/403 | Correct key source, header scheme, front-door/worker auth contract |
| HTTP 404 | Base path, alias, endpoint compatibility |
| Catalog works, chat stalls | Worker load, queue/lock, prompt ingestion, context, stream lifecycle |
| Direct chat works, agent client fails | Provider selection, environment inheritance, context guard, fallback |

If authorized to repair firewall scope, inspect any existing rule by exact identity, including enabled state, action, direction, profiles, local/remote addresses, port/protocol, program/service/interface filters, and effective ActiveStore policy. Default inbound block is normal; an applicable narrow allow rule permits the intended flow, while explicit blocks or managed-policy restrictions may override it. Match the actual interface profile rather than automatically choosing Private. Restrict to the exact approved peer IP, router TCP port, and server address/interface where possible. Record rule identity and prior settings. Elevate only the scoped change; verify its effective result afterward. Do not add unnecessary client inbound rules.

## 3. Map the agent client's API contract

Discover the chosen framework's installed version, native provider/adapter, configuration location, and supported wire protocol from its current docs/help. Do not assume OpenAI-compatible chat means support for Responses, Anthropic Messages, tools, images, or an entire agent framework.

Record this client adapter contract before editing:

- Base URL and exact API path; avoid accidentally doubling or omitting /v1.
- Authentication scheme and supported secret reference; preserve the client's expected credential source.
- Exact router model alias, actual usable context, output limit, and capabilities.
- Streaming/SSE support, timeouts/cancellation, reasoning format, tool-call schema, and image content encoding.
- Fallback/default behavior and a way to prove the actual endpoint/model used.
- Client network namespace: localhost in a container/VM refers to that environment, not automatically the host. Choose an authorized reachable route without opening unrelated interfaces.

Configure the client's native adapter when supported. If it requires a different protocol, use an explicitly chosen compatible gateway/adapter and validate both hops; do not silently replace the framework or claim compatibility from a catalog response. Distinct local/remote provider labels are a convention, not a requirement on framework-specific syntax.

Read [hermes-agent.md](hermes-agent.md) only when the target client is Hermes Agent. For another framework, map the contract above to its actual configuration rather than reuse Hermes YAML. Store any newly learned adapter recipe separately and mark untested capabilities clearly.

## 4. Acceptance through the owning client

First validate a short authenticated direct text request against the intended alias. Then send a unique bounded prompt through the actual requested agent client and retain its final answer. When GUI testing is requested, a CLI-only pass is not equivalent.

Inspect targeted client request/session evidence and correlate server model activity: actual base URL, alias, authentication success, API call count where available, stream completion, and fallback. Avoid dumping conversations, credentials, or image payloads. Test agent tool calls only when needed by the requested workflow; text completion alone does not prove tool semantics.

Test requested image support separately and distinguish direct model image input from auxiliary vision description tools. Test aliases sequentially for a one-worker router, with bounds appropriate for model swaps and cold loads. Preserve original client defaults and active user work.

Report the framework/version and verified capability level, not universal support. If an adapter is unavailable, identify that boundary and ask before adding a new gateway or changing architecture.
