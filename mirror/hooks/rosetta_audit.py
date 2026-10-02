#!/usr/bin/env python3
"""PreToolUse + PostToolUse: record every mutation against the Rosetta plan that authorized it.

This is Rosetta R0 -- **audit mode**. It records and it never denies. Not because denying is hard,
but because GPT-PM's design review put a prerequisite in front of it: enforced GO depends on
knowing WHICH project and WHICH GPT-PM conversation authorized a piece of work, and today that
binding still degrades to a folder-name convention (`pm-bridge/src/config.js`). Gate B closes
that; enforcement switches on after it. Turning deny mode on first would mechanically authorize
mutations off an identity mechanism the roadmap is already scheduled to replace.

What R0 does deliver is the thing that was actually missing: a truthful record. Before this,
nothing anywhere knew whether a given edit happened under a reviewed plan or not.

Two phases, because a PreToolUse record is provenance and not truth:

  intent   -- what was about to be attempted, and whether a plan authorized it
  outcome  -- whether it actually succeeded

A command can fail halfway, be a no-op, or touch paths nothing in its input mentioned. Neither
phase is trusted as the changed-set: closure reconstructs that from git (`rosetta.js: changedSet`),
and the two are reconciled there. The journal answers "under what authority", the repository
answers "what changed".

Fail-open, always, in every direction -- but never silently. An absent pm-bridge checkout, an
unreadable state directory, a malformed plan: the call is allowed and, where it still can be, the
event is spooled as `governed: false`. A governance layer that bricks every editor on the machine
when its own state file is malformed is worse than no governance layer; one that forgets what
happened while it was degraded is how a gap becomes invisible.

Kill switch: CLAUDE_ROSETTA_GATE=off (process-level, before the session starts).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _rosetta_common import (  # noqa: E402
    active_plan,
    classify_call,
    gate_off,
    resolve_governance_scope,
    rosetta_dir,
    write_act_event,
)


def intent_key(data: dict, tool_name: str, tool_input: dict) -> str:
    """Correlate an outcome back to its intent.

    Claude Code supplies `tool_use_id` on both PreToolUse and PostToolUse, and it is the exact
    identity wanted here. An earlier version of this function asserted in its own docstring that
    no such id existed and digested the call's input instead -- a claim written as fact without
    ever being checked. The first production spool disproved it: one Edit produced an orphan
    intent AND an orphan outcome, because `tool_input` was not byte-identical across the two
    phases, so the digest of it was not stable. The payload was then dumped and `tool_use_id` was
    sitting in it.

    The digest is kept only as a fallback for a payload that somehow lacks the id. In that mode
    two byte-identical calls in one session collide, which for an audit record is tolerable: same
    command, same authority, and closure reads the repository for what actually changed anyway.
    """
    tool_use_id = data.get("tool_use_id")
    if tool_use_id:
        return str(tool_use_id)
    blob = json.dumps({"t": tool_name, "i": tool_input}, sort_keys=True, ensure_ascii=False)
    return "d:" + hashlib.sha1(blob.encode("utf-8", "replace")).hexdigest()[:16]


def succeeded(response) -> bool | None:
    """Whether the tool call worked, as far as the response shape allows telling. None = unknown."""
    if isinstance(response, dict):
        for key in ("success", "ok"):
            if isinstance(response.get(key), bool):
                return response[key]
        if response.get("is_error") is True or response.get("error"):
            return False
        if response.get("interrupted") is True:
            return False
        return True
    if isinstance(response, str):
        return None
    return None


def main() -> int:
    if gate_off():
        return 0

    try:
        data = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return 0

    tool_name = data.get("tool_name") or ""
    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = {}

    is_mutation, reason, target = classify_call(tool_name, tool_input)
    if not is_mutation:
        # Inspection is free and always was: the Rosetta protocol gates the Act phase, not the
        # Inspect phase. Recording every `cat` would bury the events that matter.
        return 0

    session_id = data.get("session_id")
    cwd = data.get("cwd")
    event_phase = "outcome" if data.get("hook_event_name") == "PostToolUse" else "intent"
    key = intent_key(data, tool_name, tool_input)

    if event_phase == "outcome":
        write_act_event(session_id, {
            "phase": "outcome",
            "intent_key": key,
            "session_id": session_id,
            "tool": tool_name,
            "ok": succeeded(data.get("tool_response")),
        })
        return 0

    scope_class, scope_repo = resolve_governance_scope(tool_name, target, cwd)
    # A resolved repo scope takes priority over cwd -- for Edit/Write/NotebookEdit this is the
    # file's own directory, which is the actually-mutated location, not wherever the tool call
    # happened to run from (see resolve_governance_scope's docstring). Only when no repo could be
    # resolved (UNGOVERNABLE_PATH / GOVERNANCE_SCOPE_AMBIGUOUS) does active_plan fall back to the
    # raw cwd, purely so `plan_scoped_to_other_repo` still reads sensibly in that record.
    plan, plan_reason = active_plan(session_id, scope_repo or cwd)
    governed = plan_reason == "ok"
    write_act_event(session_id, {
        "phase": "intent",
        "intent_key": key,
        "session_id": session_id,
        "cwd": cwd,
        "tool": tool_name,
        "target": target,
        "classified_as": reason,
        "governed": governed,
        "reason": plan_reason,
        "plan_id": (plan or {}).get("plan_id"),
        "review_class_declared": (plan or {}).get("declared_class"),
        "state_dir": str(rosetta_dir()),
        "governance_scope": scope_class,
        "scope_repo": scope_repo,
    })
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        # A governance recorder must never be the thing that breaks a session.
        raise SystemExit(0)
