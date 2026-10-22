# Hermes Agent adapter

Read after the framework-independent router and client contract checks.

## 3. Configure Hermes Agent

Locate the installed Hermes home/config and its version-specific provider schema. Preserve existing settings; patch only the intended provider/model entries. Typical named-provider shape from the verified installation (confirm for a different build):

```yaml
providers:
  llama.cpp Desktop:
    base_url: http://<server-tailnet-address>:<router-port>/v1
    key_env: LLAMA_API_KEY
    models:
      <exact-router-alias>:
        context_length: <actual-served-per-slot-context>
        supports_vision: <true-or-false>
```

Use the installed configuration's required `api` field or alternate endpoint key if applicable; this example is not a complete universal schema. Keep local loopback provider entries unchanged. Check router catalog aliases and actual backend context (for builds that support it, `/props?model=<alias>` may expose effective `n_ctx`). Confirm the context required by this Hermes build before testing; a preflight refusal with zero API calls is not a network failure.

Set the approved matching secret in the client's supported user environment/secret store without exposing it. A running GUI does not automatically inherit newly saved Windows user environment values. With permission and after preserving active work, restart Hermes through a process that actually has the new key in its environment. Verify presence without displaying its value. Do not assume restarting from a stale parent process fixes inheritance.

## 4. Acceptance through the real app

Use the app automation skill when operating Hermes GUI. Create an isolated new session, select the intended provider/alias, and send a short unique text request with a bounded expected answer. Wait for completion while checking the server's load/queue/token activity. Keep reasonable bounds; ask before interrupting an unrelated active request.

Inspect saved session metadata/logs with targeted reads: actual model, provider, base URL, API call count, final reply, and any fallback/error. On the verified Windows build, Hermes `state.db` had these billing/session fields; discover schema before querying another version. Do not dump whole conversations or image payloads. Correlate with server evidence where available. A CLI pass is useful isolation but does not replace an explicitly requested GUI test.

For a requested vision test, use a user-approved image, confirm the outgoing API content actually contains an image attachment, and record whether the selected model receives it directly, calls an auxiliary vision tool, or only gets a textual description. Require a final response and distinguish those paths in the report.

Test remaining aliases one at a time. A first switch may load a different worker. Retain authentic per-model metadata and classify unsupported profiles separately. Restore temporary chat defaults without deleting test history unless requested.
