#!/usr/bin/env python3
"""Refresh the mirror, and commit it when (and only when) the control plane actually changed.

    python -s scripts/track.py              # export + tests + local commit if there is a diff
    python -s scripts/track.py --push       # also push the new commit to origin/main
    python -s scripts/track.py --message "why this changed"

Safety: the exporter's secret scan aborts the run before anything is staged. The commit uses the
GitHub noreply identity so no personal email lands in public history. The commit subject lists the
top-level areas that changed; the full diff is the record.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PY = sys.executable
IDENT = ["-c", "user.name=xLZDx", "-c", "user.email=25364989+xLZDx@users.noreply.github.com"]
ATTRIBUTION = "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"


def git(*args: str, check: bool = True) -> str:
    r = subprocess.run(["git", *IDENT, "-C", str(REPO), *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def run(*cmd: str) -> None:
    r = subprocess.run([PY, "-s", *cmd], cwd=REPO)
    if r.returncode != 0:
        raise SystemExit(f"{' '.join(cmd)} exited {r.returncode}; nothing committed")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--push", action="store_true")
    ap.add_argument("--message", default="")
    args = ap.parse_args()

    run("scripts/test_export.py")
    run("scripts/export_from_claude_home.py")
    git("add", "-A")
    names = [n for n in git("diff", "--cached", "--name-only").splitlines() if n]
    if not names:
        print("no control-plane changes")
        return 0

    areas = Counter("/".join(n.split("/")[:2]) if n.startswith("mirror/") else n for n in names)
    top = ", ".join(f"{k} ({v})" for k, v in areas.most_common(4))
    subject = f"Track control-plane changes: {len(names)} files - {top}"[:200]
    body = (args.message + "\n\n" if args.message else "") + ATTRIBUTION + "\n"
    msg = REPO / ".commitmsg.tmp"
    msg.write_text(subject + "\n\n" + body, encoding="utf-8")
    try:
        git("commit", "-q", "-F", str(msg))
    finally:
        msg.unlink(missing_ok=True)
    print(git("log", "--oneline", "-1").strip())
    if args.push:
        git("push", "origin", "main")
        print("pushed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
