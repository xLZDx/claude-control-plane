#!/usr/bin/env python3
"""Mirror the publishable AI control-plane surface from ~/.claude into this repository.

Allowlist only: anything not named in INCLUDE is never copied. Files that vanish from the source
are removed from the mirror, so `git diff` shows exactly what changed in the control plane.
A secret scan runs on the staged result and the export aborts (fail closed) on any hit.

Usage:
    python -s scripts/export_from_claude_home.py [--src DIR] [--dry-run]
Exit codes: 0 ok, 2 secret scan failed, 3 source missing.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MIRROR = REPO / "mirror"

# (relative source path, kind). Directories are copied recursively, minus EXCLUDE_PARTS.
INCLUDE = [
    "CLAUDE.md",
    "agent_routing.json",
    "agents",
    "skills",
    "hooks",
    "commands",
    "core",
    "tools",
    "control-plane/agentctl.py",
    "control-plane/apply_agent_budgets.py",
    "control-plane/build_skills.py",
    "control-plane/normalize_touched_agents.py",
    "control-plane/deprecated_agents.json",
    "control-plane/model_policy.json",
    "control-plane/projects.json",
    "control-plane/tests",
    "control-plane/eval",
    "control-plane/REMEDIATION_STATUS_2026-10-02.md",
]
EXCLUDE_PARTS = {"__pycache__", ".git", "out", "node_modules"}
EXCLUDE_SUFFIXES = {".pyc", ".log", ".lock", ".bak"}
MAX_BYTES = 2_000_000

SECRET_PATTERNS = {
    "github_token": r"gh[pousr]_[A-Za-z0-9]{20,}",
    "generic_secret": r"(?i)(api[_-]?key|secret|token|passw(or)?d)\s*[:=]\s*['\"][^'\"\s]{8,}",
    "private_key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "aws_key": r"AKIA[0-9A-Z]{16}",
    "public_ipv4": r"\b(?!127\.|0\.|10\.|192\.168\.)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    "chatgpt_conversation": r"chatgpt\.com/c/[0-9a-f-]{20,}",
    "real_email": r"[A-Za-z0-9._%+-]+@(?!example\.com)(?!github\.com)[A-Za-z0-9-]+\.[A-Za-z]{2,}",
}


def iter_source_files(src: Path):
    for rel in INCLUDE:
        p = src / rel
        if p.is_file():
            yield rel, p
        elif p.is_dir():
            for f in sorted(p.rglob("*")):
                if not f.is_file():
                    continue
                if EXCLUDE_PARTS & set(f.relative_to(src).parts):
                    continue
                if f.suffix in EXCLUDE_SUFFIXES or f.stat().st_size > MAX_BYTES:
                    continue
                yield f.relative_to(src).as_posix(), f


def scan_text(text: str) -> list[tuple[str, str]]:
    found = []
    for name, rx in SECRET_PATTERNS.items():
        for m in re.finditer(rx, text):
            found.append((name, m.group(0)[:40]))
    return found


def scan_tree(root: Path) -> list[tuple[str, str, str]]:
    bad = []
    for f in root.rglob("*"):
        if f.is_file():
            for name, snippet in scan_text(f.read_text(encoding="utf-8", errors="ignore")):
                bad.append((f.relative_to(root).as_posix(), name, snippet))
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(Path.home() / ".claude"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    src = Path(args.src)
    if not src.is_dir():
        print(f"source missing: {src}", file=sys.stderr)
        return 3

    stage = REPO / ".export-stage"
    if stage.exists():
        shutil.rmtree(stage)
    copied = 0
    for rel, f in iter_source_files(src):
        dest = stage / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest)
        copied += 1

    bad = scan_tree(stage)
    if bad:
        print("SECRET SCAN FAILED - nothing published:", file=sys.stderr)
        for rel, name, snippet in bad[:25]:
            print(f"  {rel}: {name}: {snippet}", file=sys.stderr)
        shutil.rmtree(stage)
        return 2

    if args.dry_run:
        print(f"dry-run ok: {copied} files staged, scan clean")
        shutil.rmtree(stage)
        return 0

    if MIRROR.exists():
        shutil.rmtree(MIRROR)
    stage.rename(MIRROR)
    print(f"exported {copied} files to {MIRROR}; scan clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
