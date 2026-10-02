#!/usr/bin/env python3
"""Stop hook: a session that mutated code owes a Validate phase, and says so before it ends.

The Rosetta protocol is Plan -> GO -> Act -> Validate -> Document. Everything up to Act is
observable from a tool call; Validate is not -- it is a thing a session does or quietly doesn't.
This hook is where "quietly doesn't" stops being possible.

Two conditions, both read from the act spool that `rosetta_audit.py` writes:

  1. **Ungoverned mutation.** Files were changed with no approved plan authorizing them. In R0 the
     mutation itself was allowed (audit mode -- see that file's header for why enforcement waits
     for Gate B), so this is the point where the debt is surfaced instead of disappearing.
  2. **Unvalidated work.** An approved plan is still `in-progress` while its acts are done. The
     session is asked to close it -- `passed` with evidence, `failed`, or explicitly `blocked`.

GPT-PM's review found the failure mode a naive version of this has, and it is worth stating
because it is not obvious: "block once" alone is not enough. A session blocked once simply stops
again, and the plan is left `in-progress` forever -- indistinguishable, to the next session, from
work that is still actively running. So the debt is recorded as well as reported: a plan may end
unvalidated; it may not end unrecorded.

The record is written at the moment of reporting, not on a later Stop. An earlier version wrote it
in the "already fired" branch, which the standard flow never reaches -- the retry after a block
arrives with `stop_hook_active` set and returns before any of this runs, so block/retry/done left
nothing behind at all. Found in review, and a good example of a guarantee that reads correctly in
the code that states it while living in the one branch that does not execute.

Under PM mode the reminder text changes but the check does not. §18 inverts when a session may
stop, never what it owes -- a checkpoint that skips validation is not a checkpoint.

Kill switch: CLAUDE_ROSETTA_GATE=off, plus CLAUDE_ROSETTA_DUE_GATE=off for this check alone.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _report_common import pm_mode_active  # noqa: E402
from _rosetta_common import (  # noqa: E402
    SCOPE_GOVERNANCE_AMBIGUOUS,
    SCOPE_UNGOVERNABLE_PATH,
    active_plan,
    gate_off,
    migrate_legacy_debt,
    read_acts,
    reclassified_keys,
    rosetta_dir,
    write_act_event,
)

NON_ACTIONABLE_SCOPES = {SCOPE_UNGOVERNABLE_PATH, SCOPE_GOVERNANCE_AMBIGUOUS}


def marker_path(session_id: str, kind: str) -> Path | None:
    try:
        directory = rosetta_dir() / "stopped"
        directory.mkdir(parents=True, exist_ok=True)
        return directory / f"{session_id}.{kind}.json"
    except OSError:
        return None


def already_fired(session_id: str, kind: str) -> bool:
    """True once this session has been told about `kind`. Once per condition, never repeated.

    Keyed by condition rather than by session: a session nudged about ungoverned work, which then
    writes a retrospective plan, must still be told when that plan is left unvalidated. One shared
    marker would swallow the second, more important reminder.

    On a marker I/O error this now answers False -- fire -- where it used to answer True. The old
    direction was found in review to suppress the FIRST reminder, not just repeats: a state
    directory that was briefly unwritable meant a session with ungoverned work was never told at
    all. Firing is the safe direction because it cannot livelock: the reminder makes the model
    continue, and the Stop that follows carries `stop_hook_active`, which returns before reaching
    here. The cost of the new direction is at most one repeated reminder; the cost of the old one
    was silence exactly when the recorder was already degraded.
    """
    path = marker_path(session_id, kind)
    if path is None:
        return False
    try:
        if path.is_file():
            return True
        path.write_text(json.dumps({"session_id": session_id, "kind": kind}), encoding="utf-8")
    except OSError:
        return False
    return False


def ungoverned_reason(count: int, sample: list[str], pm_mode: bool) -> str:
    listing = "\n".join(f"  - {item}" for item in sample[:8])
    tail = (
        "  4. ПМ-режим включён: после этого продолжай к следующему гейту, не останавливайся."
        if pm_mode
        else "  4. После этого можно заканчивать ход."
    )
    return (
        f"РАБОТА ВНЕ ПРОТОКОЛА ROSETTA: {count} изменяющих вызов(ов) прошли без одобренного плана.\n"
        f"{listing}\n\n"
        "Протокол: Plan -> GO -> Act -> Validate -> Document. Плана, одобренного GPT-PM, для этой "
        "работы не было, поэтому изменения записаны как governed=false. Сейчас режим аудита — "
        "вызовы не блокировались, но долг зафиксирован и сам не исчезнет.\n\n"
        "Что сделать:\n"
        "  1. Запиши ретроспективный план: MCP-инструмент pm_rosetta_plan (repo, session_id, "
        "title, scope, steps, verification).\n"
        "  2. Получи GO у GPT-PM и привяжи его: pm_rosetta_go.\n"
        "  3. Закрой валидацией с доказательствами: pm_rosetta_close (для passed evidence "
        "обязателен).\n"
        f"{tail}\n\n"
        "Это напоминание срабатывает один раз за сессию. Kill switch: CLAUDE_ROSETTA_DUE_GATE=off."
    )


def unvalidated_reason(plan: dict, mutations: int, pm_mode: bool) -> str:
    tail = (
        "ПМ-режим включён — закрыв гейт, продолжай к следующему, а не останавливайся."
        if pm_mode
        else "После закрытия можно заканчивать ход."
    )
    return (
        f"ГЕЙТ ROSETTA НЕ ЗАКРЫТ: план \"{plan.get('title')}\" ({plan.get('plan_id')}) всё ещё "
        f"in-progress, а изменяющих вызовов по нему уже {mutations}.\n\n"
        "Фаза Validate — это не «я посмотрел, вроде работает». Закрой план с доказательствами: "
        "что именно запускалось и с каким результатом.\n\n"
        "  pm_rosetta_close(plan_id, result=passed|failed|blocked, evidence=...)\n\n"
        "evidence обязателен для passed. Реально изменённый набор файлов и класс ревью "
        "восстанавливаются из git при закрытии — не из журнала вызовов, — так что расхождение "
        f"между заявленным и сделанным будет видно.\n\n{tail}"
    )


def main() -> int:
    if gate_off() or os.environ.get("CLAUDE_ROSETTA_DUE_GATE", "").lower() == "off":
        return 0

    try:
        data = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        # Same principle as everywhere else here: degrade, but not into silence. There is no
        # session_id in an unparseable payload, so this is the one place with nowhere to record
        # to except stderr.
        print("[rosetta] Stop hook received an unparseable payload; no check performed",
              file=sys.stderr)
        return 0

    session_id = data.get("session_id")
    if not session_id:
        return 0

    # `stop_hook_active` marks the harness's own retry after a previous block, and returning here
    # is what stops a reminder from looping. It used to return BEFORE anything was recorded, which
    # quietly broke this module's own promise: the debt record was written only on some LATER,
    # unrelated Stop that might never arrive, so the standard flow -- block, retry, done -- left
    # nothing behind at all. Found in review. The record is now written at the moment the debt is
    # reported, below, so by the time this branch is reached it already exists.
    if data.get("stop_hook_active"):
        return 0

    acts, acts_ok, acts_reason = read_acts(session_id)
    intents = [a for a in acts if a.get("phase") == "intent"]
    if not intents:
        if not acts_ok:
            # An unreadable spool is not an empty one. Say so rather than passing in silence.
            print(f"[rosetta] act spool for session {session_id} could not be read fully "
                  f"({acts_reason}); no check performed", file=sys.stderr)
        return 0

    # P0 impossible-debt guard (PMB-D-ROSETTA-NONVCS-01). Three things happen here, all decided
    # by GPT-PM's design review and none of them optional pieces of this fix:
    #
    # 1. Migrate this session's pre-fix ungoverned acts (recorded before `governance_scope`
    #    existed) into LEGACY_STATE -- forensic history kept, never relabelled `governed: true`,
    #    never left as debt the session is asked to reconcile through a plan that cannot exist.
    # 2. Acts already reclassified (this call or a prior one) are excluded from actionable debt.
    # 3. Acts whose `governance_scope` is UNGOVERNABLE_PATH or GOVERNANCE_SCOPE_AMBIGUOUS are
    #    likewise excluded -- audit-visible in the spool (`pm_rosetta_status` can still see them),
    #    but never turned into a Stop-hook instruction to run a plan that will fail identically to
    #    how the legacy ones did.
    migrate_legacy_debt(session_id)
    acts, acts_ok, acts_reason = read_acts(session_id)
    intents = [a for a in acts if a.get("phase") == "intent"]
    excluded_keys = reclassified_keys(acts)

    plan, reason = active_plan(session_id, data.get("cwd"))
    pm_mode = pm_mode_active()
    ungoverned = [
        a for a in intents
        if a.get("governed") is False
        and a.get("intent_key") not in excluded_keys
        and a.get("governance_scope") not in NON_ACTIONABLE_SCOPES
    ]

    if ungoverned and reason != "ok":
        if already_fired(session_id, "ungoverned"):
            return 0
        # Record BEFORE blocking, not after: this is the only moment guaranteed to happen.
        write_act_event(session_id, {
            "phase": "debt_reported",
            "session_id": session_id,
            "result": "blocked",
            "note": "ungoverned mutations with no approved plan, reported at Stop",
            "ungoverned_mutations": len(ungoverned),
            "acts_readable": acts_ok,
        })
        sample = [f"{a.get('tool')}: {(a.get('target') or '')[:80]}" for a in ungoverned]
        print(json.dumps({"decision": "block", "reason": ungoverned_reason(len(ungoverned), sample, pm_mode)},
                         ensure_ascii=False))
        return 0

    if reason == "ok" and plan:
        if already_fired(session_id, "unvalidated"):
            return 0
        write_act_event(session_id, {
            "phase": "debt_reported",
            "session_id": session_id,
            "result": "blocked",
            "plan_id": plan.get("plan_id"),
            "note": "in-progress plan with acts and no validation, reported at Stop",
            "mutations": len(intents),
            "acts_readable": acts_ok,
        })
        print(json.dumps({"decision": "block", "reason": unvalidated_reason(plan, len(intents), pm_mode)},
                         ensure_ascii=False))
        return 0

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        # A reminder must never be the thing that breaks a session.
        raise SystemExit(0)
