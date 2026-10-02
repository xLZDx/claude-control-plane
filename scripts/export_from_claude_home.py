#!/usr/bin/env python3
"""Mirror the publishable AI control-plane surface from ~/.claude into this repository.

Allowlist only: anything not named in INCLUDE is never copied. Inside an included directory a file
is copied only if it is plain text (TEXT_SUFFIXES), is not runtime state, and does not live under a
vendor-licensed or vendor-synced skill package. Files that vanish from the source are removed from
the mirror, so `git diff` shows exactly what changed. A secret scan runs on the staged result and
the export aborts (fail closed) on any hit.

Usage:
    python -s scripts/export_from_claude_home.py [--src DIR] [--dry-run]
Exit codes: 0 ok, 2 secret scan failed, 3 source missing.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

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
# Directory names never copied at any depth. `synced` holds vendor-managed skill packages.
EXCLUDE_PARTS = {"__pycache__", ".git", "out", "node_modules", ".pytest_cache", "synced"}
# Plain text only: binaries, fonts, images, archives, logs and *.jsonl runtime state never go public.
TEXT_SUFFIXES = {
    ".md", ".py", ".json", ".txt", ".yaml", ".yml", ".toml", ".ps1", ".sh", ".cmd",
    ".ts", ".tsx", ".js", ".mjs", ".html", ".css",
}
VENDOR_MARKERS = ("LICENSE", "NOTICE", "COPYING")
MAX_BYTES = 2_000_000

SECRET_PATTERNS = {
    "github_token": r"gh[pousr]_[A-Za-z0-9]{20,}",
    "generic_secret": r"(?i)(api[_-]?key|secret|token|passw(or)?d)\s*[:=]\s*['\"][^'\"\s]{8,}",
    "private_key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "aws_key": r"AKIA[0-9A-Z]{16}",
    "public_ipv4": r"\b(?!127\.|0\.|10\.|192\.168\.)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    "chatgpt_conversation": r"chatgpt\.com/c/[0-9a-f-]{20,}",
    "real_email": r"[A-Za-z0-9._%+-]+@(?!example\.com)(?!github\.com)(?!users\.noreply\.github\.com)[A-Za-z0-9-]+\.[A-Za-z]{2,}",
}


def vendor_roots(src: Path) -> list[Path]:
    """Skill directories that ship their own LICENSE/NOTICE are vendor packages, not personal policy."""
    roots = []
    skills = src / "skills"
    if skills.is_dir():
        for f in skills.rglob("*"):
            if f.is_file() and f.name.upper().startswith(VENDOR_MARKERS):
                roots.append(f.parent)
    return roots


def publishable(f: Path, src: Path, vroots: list[Path]) -> bool:
    rel_parts = set(f.relative_to(src).parts)
    if EXCLUDE_PARTS & rel_parts:
        return False
    if f.suffix.lower() not in TEXT_SUFFIXES or f.stat().st_size > MAX_BYTES:
        return False
    if f.name.upper().startswith(VENDOR_MARKERS):
        return False
    return not any(r == f.parent or r in f.parents for r in vroots)


def iter_source_files(src: Path):
    vroots = vendor_roots(src)
    for rel in INCLUDE:
        p = src / rel
        if p.is_file():
            if p.suffix.lower() in TEXT_SUFFIXES:
                yield rel, p
        elif p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.is_file() and publishable(f, src, vroots):
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


def move_dir(stage: Path, mirror: Path) -> None:
    """Rename with a bounded retry (transient WinError 5/32 from short-lived handles), else copy."""
    for _ in range(5):
        try:
            stage.rename(mirror)
            return
        except PermissionError:
            time.sleep(0.4)
    shutil.copytree(stage, mirror)
    shutil.rmtree(stage, ignore_errors=True)


def export(src: Path, repo: Path, dry_run: bool = False) -> int:
    if not src.is_dir():
        print(f"source missing: {src}", file=sys.stderr)
        return 3
    mirror = repo / "mirror"
    stage = repo / ".export-stage"
    if stage.exists():
        shutil.rmtree(stage)
    copied = 0
    for rel, f in iter_source_files(src):
        dest = stage / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest)
        copied += 1

    bad = scan_tree(stage) if stage.exists() else []
    if bad:
        print("SECRET SCAN FAILED - nothing published:", file=sys.stderr)
        for rel, name, snippet in bad[:25]:
            print(f"  {rel}: {name}: {snippet}", file=sys.stderr)
        shutil.rmtree(stage)
        return 2

    if dry_run:
        print(f"dry-run ok: {copied} files staged, scan clean")
        shutil.rmtree(stage, ignore_errors=True)
        return 0

    if mirror.exists():
        shutil.rmtree(mirror)
    if stage.exists():
        move_dir(stage, mirror)
    else:
        mirror.mkdir()
    print(f"exported {copied} files to {mirror}; scan clean")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(Path.home() / ".claude"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    return export(Path(args.src), REPO, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
