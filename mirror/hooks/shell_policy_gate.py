#!/usr/bin/env python3
"""Combined PreToolUse policy gate for Bash and PowerShell.

Policies:
1. block high-confidence destructive/external-side-effect command shapes;
2. restrict shell-capable review-only subagents to a narrow role-aware allowlist.

Important Claude Code contract: command PreToolUse hooks are *not* intrinsically fail-closed.
Exit 1 and hook timeouts are non-blocking. This script therefore converts sibling-import and
runtime policy errors to exit 2 once the script itself has started. A failure to launch this
script, a syntax error in this file itself, or a timeout is still fail-open by Claude Code's
documented hook semantics; static deny rules remain defense in depth, not a complete sandbox.
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback

_IMPORT_ERROR: str | None = None
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import dangerous_command_gate as dangerous
    import reviewer_shell_gate as reviewer
except BaseException:
    dangerous = None  # type: ignore[assignment]
    reviewer = None  # type: ignore[assignment]
    _IMPORT_ERROR = traceback.format_exc()


def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False))


def _evaluate(data: dict) -> int:
    if _IMPORT_ERROR is not None:
        raise RuntimeError("shell policy sibling module failed to import:\n" + _IMPORT_ERROR)
    tool_name = str(data.get("tool_name") or "")
    if tool_name not in {"Bash", "PowerShell"}:
        return 0
    tool_input = data.get("tool_input") or {}
    command = tool_input.get("command") or tool_input.get("script") or ""
    if not isinstance(command, str) or not command.strip():
        return 0

    hits = dangerous.find_hits(command)
    if hits or os.environ.get("CLAUDE_SHELL_POLICY_AUDIT", "").lower() in {"1", "true", "on"}:
        dangerous.log({
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "tool": tool_name,
            "agent_type": data.get("agent_type"),
            "cwd": data.get("cwd"),
            "command": command[:600],
            "hits": hits,
            "verdict": "deny" if hits else "pass",
        })
    if hits:
        detail = "; ".join(f"{h['reason']} -> `{h['segment']}`" for h in hits)
        deny(
            "Blocked by shell_policy_gate: " + detail + ". "
            "Use a non-destructive alternative, or obtain explicit operator authorization for the exact destructive action."
        )
        return 0

    agent_type = str(data.get("agent_type") or "")
    if agent_type in reviewer.REVIEWERS and not reviewer.allowed(command, tool_name, agent_type):
        dangerous.log({
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "tool": tool_name,
            "agent_type": agent_type,
            "cwd": data.get("cwd"),
            "command": command[:600],
            "hits": [{"segment": command[:300], "reason": "review-only shell policy"}],
            "verdict": "deny",
        })
        deny(
            f"Review-only agent `{agent_type}` may use {tool_name} only for role-relevant inspection, "
            "tests/static checks, and narrowly allowed read-only database/infra/profiling commands. "
            "This command is outside that policy; hand it to the parent/implementer if required."
        )
    return 0


def main() -> int:
    try:
        data = json.loads(sys.stdin.read() or "{}")
        if not isinstance(data, dict):
            raise ValueError("hook input must be a JSON object")
        return _evaluate(data)
    except Exception:
        # For a policy hook, exit 2 is the documented process-level blocking signal. Use it
        # for internal errors rather than relying on a JSON decision that might never be emitted.
        traceback.print_exc(file=sys.stderr)
        try:
            if dangerous is not None:
                dangerous.log({
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "verdict": "hook-error-block",
                    "traceback": traceback.format_exc(),
                })
        except Exception:
            pass
        print("Shell policy hook failed internally; blocking this shell call until the hook is fixed.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
