---
name: local-inference-optimizer
description: Autoresearch-style tuning system for llama.cpp llama-server. Optimizes dense and MoE models with architecture-aware branches, smart copy-forward seeding, external tester evidence, and repeatable local validation loops for performance, balance, or capacity goals.
---

# Local Inference Optimizer (repeatable)

## Canonical source

This monorepo skill is the maintained source of truth.
- Canonical: `C:\Users\yepyy\Documents\local-inference-optimizer\SKILL.md`
- Legacy copy in `.cursor/skills` is non-canonical unless explicitly requested.

## When to apply

- A new GGUF or profile needs **stable** settings on a **known VRAM budget**.
- User gave a **VRAM ceiling** (e.g. ≤ 15.5 GiB) and a **goal** (see below): tune **toward that goal**, not a one-size-fits-all default.
- User cares about **vision, audio, or other modalities**: verify capabilities and re-benchmark with representative inputs.
- Tuning should leverage **external tester evidence** without skipping local validation.

## Optimization goals (pick explicitly)

Ask or infer which **primary goal** applies; secondary goals are constraints.

| Goal | User intent | Typical trade-offs | What to maximize / watch |
|------|-------------|--------------------|-------------------------|
| **Balance** | Good t/s and latency **and** use most of the VRAM cap for model weights / ctx | Push `-ngl`, batch, ctx toward cap; sweep MoE CPU experts | VRAM in **\[T−1, T\]**, stable Test A + B |
| **Performance** | **Fastest** decode and lowest latency; context can be smaller | May **leave VRAM slack** on purpose (smaller `ctx-size`, lower batch, fewer layers if prefill-bound) | `predicted_per_second`, `prompt_ms`; do **not** force VRAM to T if it hurts latency |
| **Capacity** | **Largest practical context**, reasoning quality, long chats / agents | VRAM goes to **KV + mmproj + higher ctx**; may lower batch or `-ngl` to fit | `n_ctx`, fit success, reasoning on; Test B and long-context paths |

**Rules:**

- **Balance** uses the **VRAM target band** subsection below aggressively.
- **Performance** prioritizes **timings over VRAM fill**; undertuning VRAM is acceptable if documented.
- **Capacity** prioritizes **`ctx-size` / `--fit` / reasoning** and client alignment; may sacrifice peak t/s.

If the user does not state a goal, **default to balance** and state that assumption in notes.

## Decision gates (required before sweeping)

### Gate A: model class (dense vs MoE)

Determine class from GGUF/log metadata before selecting strategy.

- **Dense branch**
  - Prioritize getting as many layers as possible on GPU (`-ngl`) when VRAM allows.
  - Do not blindly inherit large `ctx-size`; re-size context for this model's VRAM and goal.
  - For performance-focused dense runs, reduce context/batch before leaving many layers on CPU.
- **MoE branch**
  - Tune `-ngl` and `--n-cpu-moe` together; interaction is architecture-specific.
  - Use MoE-specific sweeps and do not copy dense heuristics directly.

### Gate B: architecture family (required)

Detect architecture (for example, Qwen, Nemotron, Llama-family, Mistral-family) from metadata/logs and apply architecture-specific checklist items:
- context and rope defaults,
- tokenizer/template behavior,
- tool-calling and reasoning quirks,
- modality projector behavior and memory profile,
- known architecture-specific knobs from trusted evidence.

Do not proceed with a generic sweep until this checklist is filled.

### Gate C: smart copy-forward seeding (allowed but constrained)

Copy-forward is a **starting cue**, not a final answer.

Allow seeding only if all similarity checks pass:
1. same family and near generation,
2. same class (dense vs MoE),
3. compatible quantization level and modality profile,
4. comparable VRAM tier and hardware envelope.

Rules:
- Treat seeded params as **hypotheses**.
- High-risk carryovers (`ctx-size`, `-ngl`, `n-cpu-moe`) require explicit fit and benchmark confirmation.
- Block blind carryover across incompatible classes/architectures.

## Parameter coverage policy (avoid narrow tuning)

Do not optimize only `ctx-size` / `-ngl` / `n-cpu-moe`.
For each model, complete a model-specific checklist covering, as applicable:
- offload/layout: `-ngl`, split mode, main GPU,
- context/memory: `--ctx-size`, `--fit`, `--fit-ctx`, `--cache-ram`,
- prefill/decode: `--batch-size`, `--threads`, `--threads-batch`,
- reasoning/tool behavior: `--reasoning`, `--reasoning-budget`, template kwargs,
- sampling: `--temp`, `--top-k`, `--top-p`, penalties,
- modality settings: `--mmproj`, image/audio workload mix.

## Modalities (vision, audio, etc.)

Capabilities affect **VRAM**, **prefill cost**, and **which flags exist** (e.g. `--mmproj`).

1. After load, read **`GET /props`**: `modalities` (e.g. `vision`, `audio`), `model_path`, and whether a **vision projector** is in use (`mmproj` in launch args or logs).
2. **Text-only** models: omit `mmproj`; do not run vision-only benchmarks as pass/fail for quality.
3. **Vision**: keep **`--mmproj`** path correct and **re-run Test A** with at least one **image+text** request (Web UI or multimodal API). Vision prefill is often **heavier** than text-only; peak VRAM can **jump** versus text benchmarks—re-check **Test B** under load with a mix of text-only and multimodal requests if the product uses both.
4. **Audio** (if enabled for the build/model): treat like vision—**representative audio+text** samples and watch VRAM/latency; adjust batch / ctx if prefill spikes.

Document in outputs: **modalities supported**, **whether mmproj (or equivalent) is loaded**, and **which test prompts included non-text inputs**.

## Core principles

### 1. Never assume layer counts across models

**Do not** infer `n_layer`, expert counts, or optimal `-ngl` from another model—even another MoE (e.g. Qwen3 Coder vs Gemma 4 26B differ).

**Always discover topology for *this* GGUF:**

- Read **`llama-server` load logs** (tensor count, layer lines, MoE lines).
- Use **`GET /props`** after load (`model_path`, generation defaults, `n_ctx`).
- If needed, inspect GGUF metadata (e.g. `llama-gguf-dump`, project tools, or docs for that architecture).

Record **`n_layer` (or block count)** and **MoE-specific KV** (experts per layer, shared experts, etc.) in your tuning notes before comparing runs.

### 2. MoE: sweep GPU layers vs CPU experts together

For MoE models, **`--n-gpu-layers` (`-ngl`)** and **`--n-cpu-moe`** interact. The **sweet spot is per-model**: raising VRAM use with more GPU layers may require **adjusting** `n-cpu-moe` (more or fewer experts on CPU) to maximize **tokens/s** without OOM or thrashing.

**Pattern (goal-aware):**

- **Performance**: sweep for **best t/s and prefill ms** first; VRAM secondary unless it hits **T** (thermal/OOM risk).
- **Balance**: sweep while holding VRAM in the **VRAM target band** subsection below.
- **Capacity**: after **`ctx-size`** and non-MoE VRAM are set, sweep **`n-cpu-moe`** so MoE still fits without shrinking context.

Steps:

1. Fix a candidate **`-ngl`** consistent with the chosen goal (VRAM band for balance/capacity; performance may use a lower `-ngl` if decode-bound).
2. **Sweep `n-cpu-moe`** (coarse steps, then refine) while watching **decode t/s** and **prefill latency** on a fixed benchmark prompt (add **multimodal** prompts if vision/audio matters).
3. Repeat for the next **`-ngl`** step if goal and VRAM allow.

Do not copy `n-cpu-moe` from a different architecture.

### 3. Dense models: offload-first within goal constraints

For dense models, prioritize near-full GPU offload when feasible:
- Increase `-ngl` until fit/perf constraints object.
- If slow, first test lower `ctx-size` / batch before accepting heavy CPU layer residency.
- Ensure decisions are goal-aware (performance may trade VRAM fill for latency).

### 4. VRAM target band (user threshold)

When the user states a cap **T** GiB (e.g. **15.5**), apply the **Optimization goals** table above:

**Balance** (and **capacity** when also maximizing weight/KV use):

- **Aim** for utilization during the representative test (model loaded, **typical** context—including **mmproj** if vision—in maybe one concurrent slot) in **\[T − 1, T\]** GiB on the dedicated GPU—e.g. **14.5–15.5 GiB** for **T = 15.5**, unless the model cannot use more, or stability forces lower use.
- **Undertuning** (well **under T − 1** when more VRAM could go to weights or ctx) often leaves **speed or headroom** on the table for balance; for **capacity**, it may mean **ctx or reasoning** was sacrificed unnecessarily.

**Performance**:

- **Do not** require VRAM to hug **T** if the user wants **minimum latency / maximum t/s**. Deliberate slack (lower ctx, smaller batch, fewer layers) can win. Still document peak VRAM and confirm you are **under T** for safety.

**Capacity**:

- VRAM may sit in **\[T−1, T\]** from **large KV + mmproj + high ctx**, not from maxing `-ngl` alone. Prefer **`--fit`** and **`ctx-size`** first, then adjust **`-ngl` / batch** so loads succeed and **reasoning** (if used) stays enabled without OOM.

Confirm with **`nvidia-smi`** (same tool each run) and server logs for projected device memory with **`--fit`**.

### 5. Context, reasoning, and fit

- Set **`--ctx-size`** and **`--fit` / `--fit-ctx`** from VRAM, **goal**, and use case; **`n_ctx`** in **`GET /props`** must match downstream clients (Web UI, agent presets **Advanced → Context length**).
- **`--reasoning` on/off**: part of **capacity vs performance** (reasoning paths can add tokens and latency). Align with user intent; re-run Test A after toggling.
- **Agent frameworks**: default system prompts can be **tens of thousands of tokens**; **`ctx_length` must be ≤ server `n_ctx`**. Tiny local ctx cannot run full agent stacks regardless of t/s.

### 6. Host prompt cache (`--cache-ram` / `-cram`)

llama-server can cap **host DRAM** used for a **RAM-resident prompt / checkpoint cache** (reuse prefixes, reduce re-processing on churn). This is **separate** from KV offload placement.

- **`-cram <MiB>`**: cap in mebibytes (see server `--help` for defaults).
- **`-1`**: no MiB cap; **`0`**: disable.

After changing `-cram`, re-run a short **Test A** on workloads that repeat system/tool prefixes (agents) to see if prefill latency improves without exceeding host RAM budget.

## External evidence policy (autoresearch-inspired)

Before broad sweeps, run a targeted evidence pass:
1. Gather relevant tester reports/benchmarks for exact model or closest siblings.
2. Filter sources by recency, hardware comparability, reproducibility detail, and cross-source agreement.
3. Convert findings into weighted priors for hypotheses.
4. Validate every imported idea locally before adoption.

External evidence can accelerate search, but never replaces local measurements.

## Autoresearch-style tuning loop (v2)

Max rounds: 3 (+ one pre-round evidence pass). Stop early when promotion criteria are met.

- **Round 0**: define objective, constraints, architecture/class decisions, seeded hypotheses.
- **Round 0.5**: collect and score external tester evidence for model-specific priors.
- **Round 1**: broad sweep across key parameter families.
- **Round 2**: targeted gap-fill based on best candidates and failures.
- **Round 3**: contradiction and edge-case reconciliation (including modality/parallel pressure).

### Promote/bail criteria

Promote a candidate only if:
- no OOM/crash under required tests,
- goal-weighted metrics improve against baseline,
- VRAM behavior is consistent with goal and cap,
- required modalities and reasoning/tool paths pass.

Bail or rollback when:
- instability repeats,
- gains are not reproducible,
- constraints are violated (VRAM cap, latency limits, context requirements).

## Repeatable test harness

Use the **same** checks each iteration so results are comparable. **Weight metrics by the active goal** (see **Optimization goals** above): e.g. **performance** cares most about `prompt_ms` and `predicted_per_second`; **capacity** cares about successful long contexts, reasoning, and modality requests without OOM; **balance** requires both to be acceptable.

### Why two test surfaces

Tuning for **one** scenario (e.g. single clean-slate chat) can hide problems that appear under real workloads. Two complementary surfaces catch both ends:

| Surface | What it reveals | Context profile |
|---------|-----------------|-----------------|
| **Non-agentic chat UI** (e.g. llama.cpp Web UI) | Baseline speed, latency, stability with **controllable** context length | Clean slate; you choose prompt length (short / medium / long text) |
| **Agentic / heavy-context load** (e.g. Agent Zero, or parallel chats) | Behavior when context is **large and unpredictable**, concurrency, KV pressure | System prompt + tools + history can fill most of `n_ctx` in one shot |

If no agent framework is available, **simulate the heavy side** by running **multiple concurrent chats** through the Web UI or API so the server handles parallel slots and higher aggregate context.

### Test A — Single chat (baseline)

Measures per-request performance on a **controlled** context.

1. **Load**: **`GET /v1/models`**, **`GET /props`** (`n_ctx`, **`modalities`**, model id).
2. **Short text prompt**: fixed message (e.g. "Reply with one word: OK"), fixed `max_tokens`, `temperature`. Record **`timings`** (`prompt_ms`, `predicted_per_second`, `predicted_per_token_ms`).
3. **Medium text prompt**: ~200–500 tokens of input to stress batch/prefill. Same timing fields.
4. **Long text prompt** (if **capacity** or long-context use): stretch toward a large fraction of **`n_ctx`** in steps; watch fit/OOM and latency collapse.
5. **Vision** (if `modalities.vision` and mmproj): at least one **image + short instruction**; record timings and VRAM (vision prefill often dominates).
6. **Audio** (if applicable to the stack): at least one **audio + text** sample if the user relies on it.
7. **VRAM**: `nvidia-smi` after load and during the **heaviest** Test A request (often vision or long text).

### Test B — Parallel / heavy-context load

Measures behavior closer to agents or multi-user use; critical for **balance** and **capacity**, still useful for **performance** (contention can crater t/s).

**If an agent framework is available** (e.g. Agent Zero with sufficient `n_ctx` for its system prompt):
- Open **Testing models** (or equivalent), **Nudge** or send a message.
- Note completion, wall-clock, errors (context overflow, timeouts).

**If no agent framework is available** (or system prompt exceeds `n_ctx`):
- Fire **2–4 concurrent** chat completions (API or multiple Web UI chats).
- Mix **short + medium** prompts; if vision matters, include **at least one concurrent multimodal** request where possible.

**In either case**, sample `nvidia-smi` **during** the burst for **peak VRAM**.

### What to record each iteration

Store **per run**: **stated goal**, model id, full flag list (including **`--reasoning`**, **`--mmproj`**, **`--cache-ram`** if set), Test A (short / medium / long / modality as applicable), Test B results, VRAM idle + peak, **`modalities`** from `/props`, and errors.

## Run ledger (required format)

For each candidate run, record at minimum:
- run id and timestamp,
- source of params (seeded/manual/evidence),
- model class and architecture gates,
- full launch flags,
- key metrics (`prompt_ms`, `predicted_per_second`, error rate, latency summary),
- VRAM peak/idle and fit notes,
- modality and reasoning/tool-call pass/fail,
- confidence score (low/medium/high) with rationale,
- decision: promote / hold / reject / rollback.

## Suggested tuning order

1. Confirm **optimization goal** (balance / performance / capacity), constraints, and required modalities.
2. Determine model class and architecture gates; establish topology and VRAM cap T.
3. Evaluate smart copy-forward eligibility and form initial hypotheses.
4. Run external evidence pass (Round 0.5) and weight priors.
5. Follow **one** primary path by goal (merge steps from the others only as constraints):
   - **Capacity-first**: set **`ctx-size`**, **`--fit` / `--fit-ctx`**, **`--reasoning`**, and **`--mmproj`** (if vision) so the model **loads** at the target story; then tune **`-ngl` / batch** to fit **T**.
   - **Performance-first**: start from a **smaller ctx** and lean **batch / threads-batch**; sweep **`-ngl`** and MoE **`n-cpu-moe`** for best **timings**, then grow ctx only if the user needs it.
   - **Balance**: choose ctx + fit, then **raise `-ngl` / batch** until VRAM sits in **\[T−1, T\]** when possible (see **VRAM target band** below).
6. **MoE only**: sweep **`n-cpu-moe`** at the best `-ngl` candidates.
7. **Dense only**: verify offload-first behavior before concluding CPU-heavy settings are acceptable.
8. Tune remaining parameter families (batching, sampling, reasoning budget, cache, modality settings).
9. Run **Test A** and **Test B**; record in run ledger and apply promote/bail rules.
10. Update launcher and final summary.

## Anti-patterns

- Blindly reusing params from another model without class/architecture compatibility checks.
- Assuming two MoE models share **layer counts** or optimal **`-ngl` / `n-cpu-moe`**.
- Copying MoE-oriented assumptions into dense models.
- Leaving dense layers on CPU when VRAM headroom exists and goal does not justify it.
- Reusing inherited `ctx-size` without validating fit, latency, and goal alignment.
- Forcing VRAM to **\[T−1, T\]** when the user asked for **performance** and lower VRAM gives better latency—**match the stated goal**.
- Optimizing **balance** while ignoring **capacity** needs (reasoning, long ctx, vision) or the reverse.
- Stopping with **large unused VRAM** below **T − 1** on a **balance** run without documenting why (OOM, fit, or user request).
- **Capacity** runs that never test **long context** or **reasoning** paths actually used in production.
- **Vision / audio** models tuned **text-only**; missing **mmproj** or never running a **multimodal** Test A.
- Setting agent framework context **above** server **`n_ctx`** or ignoring **system prompt size** vs context.
- **Only Test A** and declaring done—**Test B** still required for load and contention (**Repeatable test harness** above).
- Skipping Test B because "no agent is available"—use **concurrent API / multiple Web UI chats**.

## Outputs

After tuning, leave:

- Executable **launcher** with all flags explicit (**reasoning**, **mmproj** if used, **cache-ram** if tuned).
- **Stated optimization goal** and **which modalities** were validated.
- **Two final candidates**: recommended profile + one fallback profile.
- **One paragraph**: t/s and/or latency (performance), **n_ctx** and long-context behavior (capacity), VRAM band and caveats (balance).
- **Evidence summary**: why the winner won (round-by-round) and what was rejected.
- **Run ledger excerpt** with confidence and promotion decision.
- If **Web UI / agent** are in scope: **API base**, **exact model id**, **`ctx_length` = `n_ctx`**.
