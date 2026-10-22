#!/usr/bin/env python3
"""Validate the AI-Link workflow skill without third-party dependencies."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("SKILL.md frontmatter is not terminated")
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"invalid frontmatter line: {line!r}")
        data[key.strip()] = value.strip().strip('"\'')
    return data, text[end + 5 :]


def main() -> int:
    issues: list[str] = []
    required = {
        "VERSION",
        "SKILL.md",
        "agents/openai.yaml",
        "references/operating-contract.md",
        "references/unity-client.md",
        "references/bridge-agent-zero.md",
        "references/roadmap-and-ainexus.md",
        "references/validation-and-recovery.md",
        "scripts/validate_skill.py",
        "scripts/check_mirrors.py",
    }

    for relative in sorted(required):
        if not (ROOT / relative).is_file():
            issues.append(f"missing required file: {relative}")

    skill_path = ROOT / "SKILL.md"
    if skill_path.is_file():
        text = skill_path.read_text(encoding="utf-8")
        if not text.endswith("\n"):
            issues.append("SKILL.md must end with a newline")
        try:
            frontmatter, body = parse_frontmatter(text)
        except ValueError as exc:
            issues.append(str(exc))
            frontmatter, body = {}, ""

        if set(frontmatter) != {"name", "description"}:
            issues.append("frontmatter must contain only name and description")
        name = frontmatter.get("name", "")
        description = frontmatter.get("description", "")
        if not NAME_RE.fullmatch(name):
            issues.append("name must use lowercase letters, digits, and hyphens")
        if name != ROOT.name:
            issues.append("frontmatter name must match the skill directory")
        if not description or len(description) > 1024:
            issues.append("description must contain 1-1024 characters")
        if len(body.strip()) < 500:
            issues.append("SKILL.md body is unexpectedly short")

        for raw_target in LINK_RE.findall(body):
            target = raw_target.split("#", 1)[0]
            if not target or "://" in target:
                continue
            resolved = (ROOT / target).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                issues.append(f"link escapes skill directory: {raw_target}")
                continue
            if not resolved.is_file():
                issues.append(f"broken local link: {raw_target}")

    version_path = ROOT / "VERSION"
    if version_path.is_file():
        version = version_path.read_text(encoding="utf-8").strip()
        if not SEMVER_RE.fullmatch(version):
            issues.append("VERSION must be semantic major.minor.patch")

    for markdown in sorted(ROOT.rglob("*.md")):
        relative = markdown.relative_to(ROOT).as_posix()
        text = markdown.read_text(encoding="utf-8")
        if not text.endswith("\n"):
            issues.append(f"{relative} must end with a newline")
        if markdown.name == "SKILL.md" and markdown != ROOT / "SKILL.md":
            issues.append(f"nested active skill is not allowed: {relative}")
        if re.search(r"\b(TODO|TBD|PLACEHOLDER)\b", text, re.IGNORECASE):
            issues.append(f"unfinished marker in {relative}")
        if "AI-54 and AI-56 depend on the prototype being" in text:
            issues.append(f"known truncated draft text in {relative}")

    openai_path = ROOT / "agents" / "openai.yaml"
    if openai_path.is_file():
        text = openai_path.read_text(encoding="utf-8")
        for field in ("display_name:", "short_description:", "default_prompt:"):
            if field not in text:
                issues.append(f"agents/openai.yaml missing {field[:-1]}")
        if "$ai-link-workflow-rules" not in text:
            issues.append("default_prompt must mention $ai-link-workflow-rules")

    if issues:
        for issue in issues:
            print(f"ERROR: {issue}", file=sys.stderr)
        return 1

    print(f"OK: {ROOT} (version {(ROOT / 'VERSION').read_text().strip()})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
