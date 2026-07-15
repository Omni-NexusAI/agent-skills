#!/usr/bin/env python3
"""vram_gate.py — portable VRAM pre-flight gate for local LLM fallback models.

WHY THIS EXISTS
---------------
A local LLM (llama.cpp / LM Studio / Ollama / any GPU-loaded model) needs VRAM
to load. If the GPU is already busy — a game, another inference server, a
render job — trying to load a local model either thrashes VRAM or OOM-crashes
the box. This script answers one question, cheaply and deterministically:

    "Is there enough free VRAM to safely load a local model RIGHT NOW?"

It is provider-agnostic: it only reads nvidia-smi. No llama.cpp / LM Studio /
Ollama specifics. Any agent on any NVIDIA box can use it.

DECISION
--------
    used_pct = memory.used / memory.total * 100
    used_pct >= threshold  -> GATE CLOSED (exit 1): do NOT load local model
    used_pct <  threshold  -> GATE OPEN   (exit 0): local model may load

Threshold resolution (first match wins):
    1. --threshold N            CLI override
    2. VRAM_GATE_THRESHOLD_PCT  environment variable
    3. optional config file     (see --config / --config-key; agent-specific)
    4. 75.0                     built-in default

If nvidia-smi is unavailable (no NVIDIA GPU / no driver):
    default -> GATE OPEN (exit 0)   (fail-open: don't block on unknown)
    --strict -> GATE CLOSED (exit 1) (treat "no GPU" as "can't run local")

OUTPUT
------
A single JSON line on stdout:
    {"gate":"open|closed","used_pct":38.6,"threshold_pct":50.0,"reason":"..."}
A human summary goes to stderr (suppress with --json).

EXIT CODES
----------
    0  gate open   (local model may load)
    1  gate closed (skip local model / fail over)
    2  usage error (bad args)
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys

DEFAULT_THRESHOLD = 75.0
ENV_THRESHOLD = "VRAM_GATE_THRESHOLD_PCT"


def get_vram() -> tuple[float, float, float] | None:
    """Return (used_mib, total_mib, used_pct) or None if no usable NVIDIA GPU."""
    if shutil.which("nvidia-smi") is None:
        return None
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        line = out.splitlines()[0]
        used_s, total_s = [x.strip() for x in line.split(",")]
        used = float(used_s)
        total = float(total_s)
        if total <= 0:
            return None
        return used, total, used / total * 100.0
    except Exception:
        return None


def load_config_threshold(config_path: str | None, config_key: str | None) -> float | None:
    """Optional: read threshold from a YAML/JSON config file.

    --config /path and --config-key a.b.c . Agent-specific — keep your own
    key convention. Returns None if absent or unreadable.
    """
    if not config_path or not config_key:
        return None
    try:
        from pathlib import Path
        text = Path(config_path).read_text(encoding="utf-8")
        data: object
        if config_path.endswith((".yaml", ".yml")):
            import yaml  # type: ignore
            data = yaml.safe_load(text) or {}
        elif config_path.endswith(".json"):
            import json as _json
            data = _json.loads(text)
        else:
            return None
        # Walk dotted key, e.g. "fallback.vram_gate_threshold_pct"
        cur = data
        for part in config_key.split("."):
            if not isinstance(cur, dict) or part not in cur:
                return None
            cur = cur[part]
        if isinstance(cur, (int, float)):
            return float(cur)
    except Exception:
        pass
    return None


def resolve_threshold(args: argparse.Namespace) -> float:
    if args.threshold is not None:
        return args.threshold
    env_v = os.environ.get(ENV_THRESHOLD)
    if env_v is not None:
        try:
            return float(env_v)
        except ValueError:
            pass
    cfg_v = load_config_threshold(args.config, args.config_key)
    if cfg_v is not None:
        return cfg_v
    return DEFAULT_THRESHOLD


def main() -> int:
    ap = argparse.ArgumentParser(description="VRAM gate for local fallback models")
    ap.add_argument("--threshold", type=float, default=None,
                    help="Override threshold percent (default: env or 75)")
    ap.add_argument("--config", default=None,
                    help="Optional config file (yaml/json) to read threshold from")
    ap.add_argument("--config-key", default=None,
                    help="Dotted key in --config, e.g. fallback.vram_gate_threshold_pct")
    ap.add_argument("--strict", action="store_true",
                    help="If no GPU/driver, treat as CLOSED (exit 1) instead of OPEN")
    ap.add_argument("--json", action="store_true", help="Only emit JSON on stdout")
    args = ap.parse_args()

    threshold = resolve_threshold(args)
    vram = get_vram()

    if vram is None:
        decision = "open" if not args.strict else "closed"
        result = {"gate": decision, "reason": "no-nvidia-smi",
                  "used_pct": None, "threshold_pct": threshold}
        print(json.dumps(result))
        if not args.json:
            print(f"[vram_gate] {'CLOSED' if decision == 'closed' else 'OPEN'}: "
                  f"no nvidia-smi (strict={args.strict})", file=sys.stderr)
        return 0 if decision == "open" else 1

    used, total, pct = vram
    closed = pct >= threshold
    result = {
        "gate": "closed" if closed else "open",
        "used_mib": round(used, 1),
        "total_mib": round(total, 1),
        "used_pct": round(pct, 1),
        "threshold_pct": threshold,
        "reason": "vram-above-threshold" if closed else "vram-ok",
    }
    print(json.dumps(result))
    if not args.json:
        tag = "CLOSED" if closed else "OPEN"
        print(f"[vram_gate] {tag}: {pct:.1f}% used ({used:.0f}/{total:.0f} MiB) "
              f">= {threshold:.0f}% threshold", file=sys.stderr)
    return 1 if closed else 0


if __name__ == "__main__":
    sys.exit(main())
