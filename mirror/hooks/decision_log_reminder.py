#!/usr/bin/env python3
"""UserPromptSubmit hook -- reminds (never blocks) that this project tracks
a decision/evidence/refusal log, whenever core/DECISION_LOG.md exists in the
current repo. Complements decision_log_gate.py (commit-time hard check) for
turns that produce no commit at all -- cannot save a turn that ends with no
further prompt ever arriving; only mitigates "moved on and forgot" within an
ongoing session. Operator GO, 2026-08-09.

Session-repo fallback (2026-08-16 addendum): a session opened at a
multi-project container root (e.g. D:\\Repo, which holds many independent
repos and is not itself one -- see D:\\Repo\\CLAUDE.md) reports that
container as its static cwd for every UserPromptSubmit event; that path is
never a git repo, so the reminder always no-opped there even while real work
was happening one level down in a child project. Unlike decision_log_gate.py
(PreToolUse), this event carries no shell command to parse a `cd` prefix out
of, so there is nothing to re-derive cwd from directly. Fallback: read
D:\\tmp\\claude_decision_log_gate\\session_repo\\<session_id>.json, written by
decision_log_gate.py the last time THIS session ran a `git commit` and
resolved a real repo_root from its command's own `cd` prefix. Session-scoped
by session_id, so it stays correct with multiple parallel Claude Code
sessions each open on a different sibling repo under the same container --
a plain "most recently touched repo under D:\\Repo" heuristic was tried and
rejected for exactly this reason (a live check found sibling sessions in
AI_trading_assistance/ERP/db-test-tool-analysis more recently active than
this session's own Fitness_App). Only used when the direct cwd lookup fails;
never overrides a real repo found at the reported cwd.

Kill switch: CLAUDE_DECISION_LOG_REMINDER=off
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SESSION_REPO_DIR = Path(r"D:\tmp\claude_decision_log_gate\session_repo")


def session_repo_fallback(session_id):
    if not session_id:
        return None
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", str(session_id))
    marker = SESSION_REPO_DIR / f"{safe}.json"
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
        repo_root = data.get("repo_root")
        return repo_root if repo_root and Path(repo_root).is_dir() else None
    except Exception:
        return None


def main():
    if os.environ.get("CLAUDE_DECISION_LOG_REMINDER", "").lower() == "off":
        sys.exit(0)

    try:
        payload = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)

    cwd = payload.get("cwd") or os.getcwd()

    repo_root = None
    try:
        result = subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        if result.returncode == 0:
            repo_root = result.stdout.strip()
    except Exception:
        pass

    if repo_root is None:
        repo_root = session_repo_fallback(payload.get("session_id"))
        if repo_root is None:
            sys.exit(0)

    log_path = Path(repo_root) / "core" / "DECISION_LOG.md"
    if not log_path.is_file():
        sys.exit(0)

    context = (
        "[Decision log reminder] This project tracks decisions/evidence/refusals in "
        "core/DECISION_LOG.md (per ~/.claude/CLAUDE.md 'Continuous Decision/Evidence/"
        "Refusal Log Per Project'). If your previous turn included a non-trivial "
        "decision, piece of evidence, or refusal not yet logged, add it now -- in the "
        "same commit as the related code where a commit applies."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
