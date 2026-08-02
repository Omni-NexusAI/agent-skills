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

## Configuration intake (required before any sweeping)

Before running any test, sweep, or launcher write, you **must** confirm the configuration with the user. Do not infer or silently default. Present recommended defaults as explicit options and require confirmation for each item.

Required intake checklist (all must be resolved before Round 0):
1. **Primary goal** — explicitly `balance`, `performance`, or `capacity` (see Optimization goals below). Do not assume.
2. **VRAM cap T** and **hardware envelope** — the GiB ceiling and which GPU(s) / machine the server runs on.
3. **Modalities in scope** — text-only, vision, audio; and whether an `--mmproj` (or equivalent) path is available.
4. **Model-launcher target** — where/how to emit the launcher (a `configs` entry in `llama-server-launcher/llama_cpp_launcher_configs.json`, or a standalone `run_*.sh/.bat`), and the naming scheme to use (see Model-launcher naming convention).
5. **Agent / Web UI in scope** — whether an agent framework or Web UI is in play (drives the Test B method).

If the user says "just decide", pick the recommended default for each unresolved item and **record the choices explicitly in the run notes**. Never auto-default without surfacing them.

## Optimization goals (pick explicitly)

Confirm the **primary goal** with the user during intake (see Configuration intake); secondary goals are constraints. Do not infer it silently.

| Goal | User intent | Typical trade-offs | What to maximize / watch |
|------|-------------|--------------------|-------------------------|
| **Balance** | Good t/s and latency **and** use most of the VRAM cap for model weights / ctx | Push `-ngl`, batch, ctx toward cap; sweep MoE CPU experts | VRAM in **\[T−1, T\]**, stable Test A + B |
| **Performance** | **Fastest** decode and lowest latency; context can be smaller | May **leave VRAM slack** on purpose (smaller `ctx-size`, lower batch, fewer layers if prefill-bound) | `predicted_per_second`, `prompt_ms`; do **not** force VRAM to T if it hurts latency |
| **Capacity** | **Largest practical context**, reasoning quality, long chats / agents | VRAM goes to **KV + mmproj + higher ctx**; may lower batch or `-ngl` to fit | `n_ctx`, fit success, reasoning on; Test B and long-context paths |

**Rules:**

- **Balance** uses the **VRAM target band** subsection below aggressively.
- **Performance** prioritizes **timings over VRAM fill**; undertuning VRAM is acceptable if documented.
- **Capacity** prioritizes **`ctx-size` / `--fit` / reasoning** and client alignment; may sacrifice peak t/s.

Goal must be set during the Configuration intake gate. Silent defaulting is not allowed; if the user delegates the choice, record the selected goal explicitly in notes.

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

### 7. Batch-eval sweep procedure

`--batch-size` and `--ubatch-size` directly affect prefill throughput, decode latency, and VRAM pressure. Treat batch as a first-class sweep dimension, not a "tune later" afterthought — especially for MoE models where batch size interacts with expert dispatch across GPU/CPU.

**Sweep procedure:**

1. Sweep `--batch-size` across [256, 512, 1024, 2048, 4096, 8192] at each candidate `-ngl` / `n-cpu-moe` setting (MoE) or at the chosen `-ngl` (dense).
2. For each batch value, set `--ubatch-size` proportionally: `batch / 4` or `batch / 8`, minimum 64.
3. Record `prompt_ms`, `predicted_per_second`, and VRAM at each step on the same medium benchmark prompt (add multimodal prompt if vision/audio in scope).
4. At each step, verify the model loads and generates without OOM before recording timing.

**Goal-aware interpretation:**

- **Performance**: if prefill latency drops (faster) but decode t/s plateaus, stop — smaller batches are already optimal for latency. Do not push batch higher if it only increases VRAM without improving decode.
- **Balance**: raise batch until VRAM hits the **\[T−1, T\]** band. If decode t/s degrades before VRAM is full, stop — throughput has peaked.
- **Capacity**: use the batch value that fits at the target `ctx-size` and reasoning setting. If a larger batch prevents the model from loading at the target ctx, shrink batch first before reducing ctx.

**Dense vs MoE difference:**

- **Dense**: batch mostly affects prefill speed. A single sweep at the final `-ngl` is usually sufficient.
- **MoE**: batch changes the compute ratio between dense layers (prefill, attention) and expert dispatch (CPU/GPU split). Repeat the batch sweep at each candidate `-ngl` / `n-cpu-moe` pair — the sweet spot shifts with the offload/expert balance.

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

### Sweep intelligence (educated early termination)

Within a single sweep axis (e.g. sweeping `-ngl`, `n-cpu-moe`, or `--batch-size`), the agent may terminate the remaining unrun parameter combinations early when the trend is clear. This saves time without sacrificing correctness.

**Trigger rule:**
If the agent observes **monotonic degradation** in the goal-weighted primary metric across **3 or more consecutive parameter steps**, terminate the remaining combinations in that sweep axis and proceed to the next parameter family or candidate.

**Goal-aware triggers:**

| Goal | Primary metric | Degradation signal | Early-stop action |
|------|----------------|--------------------|--------------------|
| **Performance** | `predicted_per_second` | 3 consecutive t/s drops from the peak | Stop remaining steps in this batch / ngl / n-cpu-moe sweep; revert to the best step seen |
| **Balance** | VRAM + `predicted_per_second` | 3 consecutive VRAM increases toward T **or** 2 consecutive t/s drops while VRAM is still under T | Stop — the edge is found at the best step; document the ceiling |
| **Capacity** | Load success + `n_ctx` | 2 consecutive OOM or fit failures | Stop immediately — capacity limit is exceeded; use the last successful step |

**Recording:**
Document every early termination in the run ledger: which axis was terminated, the observed trend (metric values at each step), and the step that was selected as the best. Do not silently skip steps.

**Overrides:**
The user can disable early termination for a given sweep if they want exhaustive data. Respect an explicit "sweep all" instruction.

## Repeatable test harness

Use the **same** checks each iteration so results are comparable. **Weight metrics by the active goal** (see **Optimization goals** above): e.g. **performance** cares most about `prompt_ms` and `predicted_per_second`; **capacity** cares about successful long contexts, reasoning, and modality requests without OOM; **balance** requires both to be acceptable.

### Server lifecycle (teardown required)

Each candidate runs against a **fresh** llama-server. After finishing Test A and Test B for a candidate, you **must terminate the server** (stop the process / free the port and GPU memory) before launching the next candidate or declaring done. Do not leave servers running between candidates: a leftover process holds VRAM and will corrupt `nvidia-smi` peak readings and `n_ctx` probes on the next run. Confirm the port is free and VRAM is released before proceeding.

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
- Tuning `--batch-size` as an afterthought rather than a first-class sweep dimension alongside ngl and n-cpu-moe; especially detrimental for MoE architectures.
- For MoE: picking `--batch-size` without re-sweeping at each ngl/n-cpu-moe candidate — the sweet spot shifts with the offload/expert balance.
- Completing every parameter combination in a sweep despite clear monotonic performance degradation — wastes cycles that could go to the next candidate.
- For **performance** sweeps: continuing a batch or ngl sweep after 3+ consecutive t/s drops instead of terminating early at the best step.

## Model-launcher naming convention

The launcher is the artifact the user actually runs. In this repo it lives as a `configs` entry in `llama-server-launcher/llama_cpp_launcher_configs.json` (consumed by `llamacpp-server-launcher.py`); the entry **key is the model-launcher name**. Standalone setups use a `run_*.sh/.bat` script instead.

**Standard scheme (keep it short and self-describing):**

    <ModelName>_<goal>

- `goal` is one of `performance`, `capacity`, `balance` (matches the primary goal).
- Examples: `Qwen35_A3B_performance`, `Gemma4_26b_capacity`, `Qwen3.6-27B_balance`.
- During tuning, evaluate a **recommended + fallback** candidate pair (recorded in the run ledger). Retain only the agreed single production launcher per Launcher retention & cleanup — do not leave the `_fallback` behind unless the user asks.

Portable fallback (no GUI launcher): `run_<ModelName>_<goal>.sh` / `.bat` with all flags explicit.

**Legacy / non-standard:** older verbose keys such as `Qwen3.6-27B-...-Q3_K_M_kv=q4_0_vv=q8_0_th=8_tb=16_b=2048_ub=10` encode params in the name. Prefer the short `<ModelName>_<goal>` form going forward; migrate when convenient.

## Recommended sampling defaults

The launcher must ship with an explicit, reproducible sampling block. Include these recommended defaults unless the model/goal requires otherwise (then document the deviation in the run ledger):

- `--temp 0.7`
- `--top-p 0.9`
- `--top-k 40`
- `--min-p 0.05`
- `--repeat-penalty 1.1`

These are starting values, not sacred; per-architecture quirks (e.g. reasoning models that prefer low temp) override them. Always record the final sampling flags in the launcher and run ledger.

## Completion gate (do not finish until all pass)

This is a **hard stop**, not advice. Do not emit the final launcher(s) or summary until **every** item is satisfied:

- **Test A** recorded: short + medium (long if capacity/long-context; modality test if vision/audio in scope).
- **Test B** executed: real agent framework OR 2–4 simulated concurrent chats; peak VRAM sampled during the burst.
- **Server terminated** after tests (see Server lifecycle).
- **Run ledger** complete for every candidate with no missing required fields; promotion decision recorded.
- **Launcher(s)** written with all flags explicit — including `--reasoning`, `--mmproj` (if used), `--cache-ram` (if tuned), and the **sampling defaults** above — and named per the Model-launcher naming convention.
- **Anti-pattern** checks performed and signed off.
- **Knowledge consolidated** into the Obsidian wiki (when reachable) and `llama-server-launcher/PROFILES.md`.
- **Trial launchers pruned**; only the one agreed production launcher remains (see Launcher retention & cleanup).

If any item fails, return to the relevant tuning round. Never declare done with gaps.

## Knowledge consolidation (required)

The durable record of a tuning run is **knowledge, not the trial launchers**. After the completion gate passes, write the result up before pruning launchers:

- **Obsidian wiki (primary when the vault is reachable):** update `wiki/concepts/llama.cpp Local Inference.md`, adding or updating an entry under its existing **Optimized Models** table — match its format (model, goal, Recommended/Capacity rows with quant, ngl, n-cpu-moe, ctx, speed, reasoning, sampling, KV cache, notes). Also touch `wiki/index.md` (new entity if needed), `wiki/hot.md` (one-liner), and append `wiki/log.md`. Skip this step if the vault path is unknown/unavailable.
- **Portable reference doc (always):** write or update `llama-server-launcher/PROFILES.md` with the same structure. This is the fallback for machines without the vault (e.g. a desktop hermes setup).
- The note must capture: the final production launcher name (per the Model-launcher naming convention), key metrics, a run-ledger excerpt, rejected candidates and why (evidence summary), and any non-obvious findings.

## Launcher retention & cleanup (required)

At the end of a run, decide with the user which launcher is the **single production launcher** (default: the recommended profile).

- **Prune all trial launchers:** remove their entries from `llama_cpp_launcher_configs.json` (the `configs` object), keeping only the one retained launcher. If standalone `.ps1` / `.bat` / `.sh` scripts were used, delete the trial scripts and keep only the production one.
- The `_fallback` launcher is **not** retained by default; its parameters live on in PROFILES.md / the wiki note, so nothing is lost. Regenerate it later if the user asks.
- Run one final smoke **Test A** on the retained launcher to confirm it loads cleanly before sign-off.

## Outputs

After tuning, leave:

- The single retained **production launcher** with all flags explicit (**reasoning**, **mmproj** if used, **cache-ram** if tuned, **sampling defaults**), named per the Model-launcher naming convention. All other trial launchers are pruned (see Launcher retention & cleanup).
- **Stated optimization goal** and **which modalities** were validated.
- **Two candidate profiles recorded in the ledger** (recommended + fallback) for analysis and future regeneration; only the agreed single production launcher is retained as an artifact.
- **One paragraph**: t/s and/or latency (performance), **n_ctx** and long-context behavior (capacity), VRAM band and caveats (balance).
- **Evidence summary**: why the winner won (round-by-round) and what was rejected.
- **Run ledger excerpt** with confidence and promotion decision.
- If **Web UI / agent** are in scope: **API base**, **exact model id**, **`ctx_length` = `n_ctx`**.
