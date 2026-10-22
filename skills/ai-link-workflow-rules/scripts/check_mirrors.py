#!/usr/bin/env python3
"""Compare byte-level manifests for the canonical skill and its mirrors."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


DEFAULT_CANONICAL = Path(__file__).resolve().parents[1]


def file_manifest(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        result[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def tree_hash(manifest: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for relative, file_hash in sorted(manifest.items()):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def diff(expected: dict[str, str], actual: dict[str, str]) -> dict[str, list[str]]:
    expected_paths = set(expected)
    actual_paths = set(actual)
    return {
        "missing": sorted(expected_paths - actual_paths),
        "extra": sorted(actual_paths - expected_paths),
        "changed": sorted(
            path
            for path in expected_paths & actual_paths
            if expected[path] != actual[path]
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical", type=Path, default=DEFAULT_CANONICAL)
    parser.add_argument("--mirror", action="append", type=Path, default=[])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    canonical = args.canonical.resolve()
    if not canonical.is_dir():
        print(f"ERROR: canonical directory not found: {canonical}", file=sys.stderr)
        return 2

    canonical_manifest = file_manifest(canonical)
    report: dict[str, object] = {
        "canonical": str(canonical),
        "hash": tree_hash(canonical_manifest),
        "files": len(canonical_manifest),
        "mirrors": [],
    }
    failed = False

    mirror_reports: list[dict[str, object]] = []
    for mirror_arg in args.mirror:
        mirror = mirror_arg.resolve()
        if not mirror.is_dir():
            mirror_reports.append({"path": str(mirror), "error": "not found"})
            failed = True
            continue
        manifest = file_manifest(mirror)
        differences = diff(canonical_manifest, manifest)
        matches = not any(differences.values())
        mirror_reports.append(
            {
                "path": str(mirror),
                "hash": tree_hash(manifest),
                "files": len(manifest),
                "matches": matches,
                **differences,
            }
        )
        failed = failed or not matches
    report["mirrors"] = mirror_reports

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"canonical {report['hash']}  {canonical}")
        for item in mirror_reports:
            if "error" in item:
                print(f"missing   {'-' * 64}  {item['path']}")
            else:
                label = "match" if item["matches"] else "DIFF"
                print(f"{label:7} {item['hash']}  {item['path']}")
                for key in ("missing", "extra", "changed"):
                    for path in item[key]:
                        print(f"  {key}: {path}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
