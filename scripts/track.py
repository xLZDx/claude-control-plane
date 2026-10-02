#!/usr/bin/env python3
"""Refresh the mirror, and commit it when (and only when) the control plane actually changed.

    python -s scripts/track.py              # export + local commit if there is a diff
    python -s scripts/track.py --push       # also push the new commit to origin/main
    python -s scripts/track.py --message "why this changed"

Fail-closed boundary (exit codes):
    2  secret scan hit (in the exported tree or in the staged index) - nothing committed or pushed
    3  source directory missing
    4  the worktree has uncommitted changes outside mirror/ - commit or stash them first, because
       tracking must never publish a file the exporter did not produce and scan
Only mirror/ is ever staged. The staged blobs are scanned again before the commit. The commit uses
the GitHub noreply identity so no personal email lands in public history.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import export_from_claude_home as ex  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
IDENT = ["-c", "user.name=xLZDx", "-c", "user.email=25364989+xLZDx@users.noreply.github.com"]
ATTRIBUTION = "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"


def git(repo: Path, *args: str, check: bool = True) -> str:
    r = subprocess.run(["git", *IDENT, "-C", str(repo), *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def dirty_outside_mirror(repo: Path) -> list[str]:
    out = []
    for line in git(repo, "status", "--porcelain", "--untracked-files=all").splitlines():
        path = line[3:].strip().strip('"')
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path.startswith("mirror/"):
            out.append(path)
    return out


def scan_index(repo: Path) -> list[tuple[str, str, str]]:
    bad = []
    for name in git(repo, "diff", "--cached", "--name-only", "--diff-filter=AM").splitlines():
        blob = subprocess.run(["git", "-C", str(repo), "show", f":{name}"], capture_output=True).stdout
        for rule, snippet in ex.scan_text(blob.decode("utf-8", errors="ignore")):
            bad.append((name, rule, snippet))
    return bad


def track(src: Path, repo: Path, push: bool = False, message: str = "") -> int:
    stray = dirty_outside_mirror(repo)
    if stray:
        print("REFUSED: uncommitted changes outside mirror/ (commit or stash them first):", file=sys.stderr)
        for p in stray[:20]:
            print(f"  {p}", file=sys.stderr)
        return 4

    rc = ex.export(src, repo)
    if rc != 0:
        return rc

    git(repo, "add", "-A", "--", "mirror")
    bad = scan_index(repo)
    if bad:
        git(repo, "reset", "-q")
        print("SECRET SCAN FAILED on staged index - nothing committed:", file=sys.stderr)
        for name, rule, snippet in bad[:25]:
            print(f"  {name}: {rule}: {snippet}", file=sys.stderr)
        return 2

    names = [n for n in git(repo, "diff", "--cached", "--name-only").splitlines() if n]
    if not names:
        print("no control-plane changes")
        return 0

    areas = Counter("/".join(n.split("/")[:2]) for n in names)
    top = ", ".join(f"{k} ({v})" for k, v in areas.most_common(4))
    subject = f"Track control-plane changes: {len(names)} files - {top}"[:200]
    body = (message + "\n\n" if message else "") + ATTRIBUTION + "\n"
    msg = repo / ".commitmsg.tmp"
    msg.write_text(subject + "\n\n" + body, encoding="utf-8")
    try:
        git(repo, "commit", "-q", "-F", str(msg))
    finally:
        msg.unlink(missing_ok=True)
    print(git(repo, "log", "--oneline", "-1").strip())
    if push:
        git(repo, "push", "origin", "main")
        print("pushed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(Path.home() / ".claude"))
    ap.add_argument("--push", action="store_true")
    ap.add_argument("--message", default="")
    args = ap.parse_args()
    try:
        return track(Path(args.src), REPO, args.push, args.message)
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
