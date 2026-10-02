#!/usr/bin/env python3
"""PreToolUse hook -- explicitly emits permissionDecision: "allow" for
Bash/PowerShell commands, to test whether that suppresses the separate
auto-mode semantic classifier's own re-prompt. Operator GO, 2026-08-14.

Background (see ~/.claude/CLAUDE.md "Codex Consensus Review" era memory
`feedback_automode_classifier_write_blocks.md`): with permissions.defaultMode
set to "auto", Claude Code runs an LLM-based semantic classifier that can
still prompt the user for a Bash/PowerShell command even when
permissions.allow already matches it (Bash(*)/PowerShell(*) wildcards) and
even when a prose autoMode.allow entry describes exactly that command. Proven
live twice: a plain `git push` re-prompted despite a narrowly-scoped
autoMode.allow entry naming it; a `docker compose down -v` re-prompted despite
the broadest possible autoMode.allow entry ("every Bash/PowerShell command,
without exception"). Two prose-only fixes both failed the same way.

This hook is the untried alternative: a PreToolUse hook returning an EXPLICIT
`permissionDecision: "allow"` (not just "no decision" -- decision_log_gate.py
and codex_review_gate.py only ever emit output when denying; when they have
nothing to say they exit 0 with empty stdout, which leaves the classifier free
to evaluate independently). Confirmed via the Claude Code docs
(https://code.claude.com/docs/en/permissions.md, checked 2026-08-14):
  - deny rules always win regardless of any hook's permissionDecision --
    this hook cannot weaken permissions.deny's hard-blocks (rm -rf,
    git push --force, dd, mkfs, chmod -R 777, docker volume rm, etc.), and it
    does not try to.
  - the docs do NOT state whether a hook's "allow" suppresses the auto-mode
    classifier specifically -- that half is UNVERIFIED and can only be
    confirmed by watching whether the operator still sees a permission
    prompt on a command that used to trigger one. This hook's job is to make
    that observation possible, not to declare victory before it happens.

Because deny rules win unconditionally, this hook's own DENY_MIRROR list
below is NOT a safety mechanism -- it exists purely so this hook's own
decision log doesn't claim "allow" for something permissions.deny was always
going to block anyway, which would misrepresent what actually happened if
anyone reads the log later.

Kill switch: CLAUDE_BASH_AUTOALLOW=off -- session/process-level, set before
this Claude Code process starts (same caveat as every other hook here: an
inline env-var prefix inside the gated command itself has no effect, because
this hook is a separate process that has already decided before that command
runs).
Decision log: D:\\tmp\\claude_bash_autoallow\\decisions.jsonl
"""
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path(r"D:\tmp\claude_bash_autoallow")
LOG_FILE = STATE_DIR / "decisions.jsonl"

# Mirrors permissions.deny in settings.json, approximately -- for honest
# logging only (see module docstring). Deny rules are enforced independently
# and win regardless of what this hook decides.
DENY_MIRROR = re.compile(
    r"rm\s+-rf\s|"
    r"git\s+push\s+(--force|-f\b)|"
    r"git\s+reset\s+--hard|"
    r"git\s+clean\s+-fdx?\b|"
    r"git\s+branch\s+-D\b|"
    r"git\s+checkout\s+--\s|"
    r"git\s+restore\s+--staged|"
    r"\bdd\s+if=|"
    r"\bmkfs|"
    r"chmod\s+-R\s+777|"
    r"chown\s+-R\b|"
    r"\b(shutdown|reboot|halt)\b|"
    r"\|\s*(sh|bash)\b|"
    r"(curl|wget)\s.*\|\s*(sh|bash)\b|"
    r"npm\s+publish|"
    r"pip\s+uninstall\s+-y|"
    r"docker\s+system\s+prune|"
    r"docker\s+volume\s+rm|"
    r"kubectl\s+delete|"
    r"Remove-Item\s+-Recurse\s+-Force|"
    r"rm\s+-r\s+-fo\b|"
    r"Format-Volume|"
    r"Clear-Disk|"
    r"Remove-Partition|"
    r"Stop-Computer|"
    r"Restart-Computer",
    re.IGNORECASE,
)


def log_decision(entry):
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        entry["ts"] = datetime.now(timezone.utc).isoformat()
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def no_decision():
    """Exit with nothing on stdout -- leaves normal permission evaluation
    (including the auto-mode classifier) to run exactly as if this hook
    didn't exist. Used for the deny-mirror carve-out and any internal error."""
    sys.exit(0)


def explicit_allow(command):
    log_decision({"decision": "allow", "command": command[:300]})
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": (
                "bash_autoallow.py: explicit allow, testing whether this "
                "suppresses the auto-mode classifier's independent re-prompt "
                "(see ~/.claude/CLAUDE.md 'Codex Consensus Review' era memory "
                "feedback_automode_classifier_write_blocks.md). permissions.deny "
                "hard-blocks still apply regardless of this decision."
            ),
        }
    }))
    sys.exit(0)


def main():
    if os.environ.get("CLAUDE_BASH_AUTOALLOW", "").lower() == "off":
        no_decision()

    try:
        payload = json.loads(sys.stdin.read())
    except Exception as e:
        log_decision({"decision": "fail-open", "reason": f"bad stdin: {e}"})
        no_decision()

    command = (payload.get("tool_input") or {}).get("command", "") or ""
    if not command:
        no_decision()

    if DENY_MIRROR.search(command):
        log_decision({"decision": "skip-deny-mirror", "command": command[:300]})
        no_decision()

    explicit_allow(command)


if __name__ == "__main__":
    main()
