---
name: local-inference-optimizer
description: Tunes llama.cpp llama-server for balance, maximum speed, or maximum context/reasoning on the host GPU, including MoE offload, modalities (vision/audio), and repeatable Web UI plus load tests. Use when optimizing local inference, new GGUFs, llama-server, VRAM caps, n-cpu-moe, layer counts, reasoning, or multimodal models.
---

# Local llama-server tuning (repeatable)

## When to apply

- A new GGUF or profile needs **stable** settings on a **known VRAM budget**.
- User gave a **VRAM ceiling** (e.g. ≤ 15.5 GiB) and a **goal** (see below): tune **toward that goal**, not a one-size-fits-all default.
- User cares about **vision, audio, or other modalities**: verify capabilities and re-benchmark with representative inputs.

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

### 3. VRAM target band (user threshold)

When the user states a cap **T** GiB (e.g. **15.5**), apply the **Optimization goals** table above:

**Balance** (and **capacity** when also maximizing weight/KV use):

- **Aim** for utilization during the representative test (model loaded, **typical** context—including **mmproj** if vision—in maybe one concurrent slot) in **\[T − 1, T\]** GiB on the dedicated GPU—e.g. **14.5–15.5 GiB** for **T = 15.5**, unless the model cannot use more, or stability forces lower use.
- **Undertuning** (well **under T − 1** when more VRAM could go to weights or ctx) often leaves **speed or headroom** on the table for balance; for **capacity**, it may mean **ctx or reasoning** was sacrificed unnecessarily.

**Performance**:

- **Do not** require VRAM to hug **T** if the user wants **minimum latency / maximum t/s**. Deliberate slack (lower ctx, smaller batch, fewer layers) can win. Still document peak VRAM and confirm you are **under T** for safety.

**Capacity**:

- VRAM may sit in **\[T−1, T\]** from **large KV + mmproj + high ctx**, not from maxing `-ngl` alone. Prefer **`--fit`** and **`ctx-size`** first, then adjust **`-ngl` / batch** so loads succeed and **reasoning** (if used) stays enabled without OOM.

Confirm with **`nvidia-smi`** (same tool each run) and server logs for projected device memory with **`--fit`**.

### 4. Context, reasoning, and fit

- Set **`--ctx-size`** and **`--fit` / `--fit-ctx`** from VRAM, **goal**, and use case; **`n_ctx`** in **`GET /props`** must match downstream clients (Web UI, agent presets **Advanced → Context length**).
- **`--reasoning` on/off**: part of **capacity vs performance** (reasoning paths can add tokens and latency). Align with user intent; re-run Test A after toggling.
- **Agent frameworks**: default system prompts can be **tens of thousands of tokens**; **`ctx_length` must be ≤ server `n_ctx`**. Tiny local ctx cannot run full agent stacks regardless of t/s.

### 5. Host prompt cache (`--cache-ram` / `-cram`)

llama-server can cap **host DRAM** used for a **RAM-resident prompt / checkpoint cache** (reuse prefixes, reduce re-processing on churn). This is **separate** from KV offload placement.

- **`-cram <MiB>`**: cap in mebibytes (see server `--help` for defaults).
- **`-1`**: no MiB cap; **`0`**: disable.

After changing `-cram`, re-run a short **Test A** on workloads that repeat system/tool prefixes (agents) to see if prefill latency improves without exceeding host RAM budget.

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

## Suggested tuning order

1. Confirm **optimization goal** (balance / performance / capacity) and **modalities** to validate (from user + `/props`).
2. Establish **topology** (layers / MoE facts) and **VRAM cap T**.
3. Follow **one** primary path by goal (merge steps from the others only as constraints):
   - **Capacity-first**: set **`ctx-size`**, **`--fit` / `--fit-ctx`**, **`--reasoning`**, and **`--mmproj`** (if vision) so the model **loads** at the target story; then tune **`-ngl` / batch** to fit **T**.
   - **Performance-first**: start from a **smaller ctx** and lean **batch / threads-batch**; sweep **`-ngl`** and MoE **`n-cpu-moe`** for best **timings**, then grow ctx only if the user needs it.
   - **Balance**: choose ctx + fit, then **raise `-ngl` / batch** until VRAM sits in **\[T−1, T\]** when possible (see **VRAM target band** below).
4. **MoE only**: sweep **`n-cpu-moe`** at the best `-ngl` candidates (goal-aware; see **MoE** subsection above).
5. Tune **`--batch-size`** and **`--threads-batch`** (prefill vs decode; multimodal prefill may need different batch than text-only).
6. If agent-like **prefix reuse** matters, tune **`--cache-ram`** against host RAM budget and re-check Test A prefill.
7. Run **Test A** (include long-text and **modality** cases per **Repeatable test harness** above).
8. Run **Test B**; if peak VRAM exceeds **T**, step back **`-ngl`**, **batch**, or **ctx** depending on goal (performance may prefer dropping batch before ctx).
9. Update **launch script** (`.ps1` / `.sh`) and a **summary**: goal, modalities tested, flags, Test A/B numbers, VRAM idle/peak band.

## Anti-patterns

- Assuming two MoE models share **layer counts** or optimal **`-ngl` / `n-cpu-moe`**.
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
- **One paragraph**: t/s and/or latency (performance), **n_ctx** and long-context behavior (capacity), VRAM band and caveats (balance).
- If **Web UI / agent** are in scope: **API base**, **exact model id**, **`ctx_length` = `n_ctx`**.
