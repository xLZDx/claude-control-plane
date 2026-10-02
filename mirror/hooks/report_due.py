#!/usr/bin/env python3
"""Stop hook: a finished chunk of work owes an HTML report, and nothing else notices when it doesn't.

Sessions do write reports -- when they think of it. On 2026-08-19 two sessions in this workspace
shipped a closed gate each and moved straight on; both produced the report only after the operator
asked. Measured across six repositories that day, the longest run of consecutive commits without a
single commit touching reports/ was 10 (ERP), 5 (formcoach), 4 (Virtual_marketing_company and
Fitness_App) and 3 (AI_trading_assistance). Only Ferma stayed at 1.

So this hook counts, per repository, the commits made after the most recent commit that touched
reports/. Past the threshold it blocks the turn once with the list, which is what makes the model
act; `stop_hook_active` and a per-HEAD marker keep it from ever nagging twice for the same work.

A second, independent check (added 2026-08-19, same day, different gap): the house format requires
BOTH a local path and a published claude.ai artifact link for the Russian report (skill html-report,
"Two files, one link"). A session in Fitness_App handed a finished report over twice with only the
local path -- no artifact link -- and had to be corrected by the operator by hand. That check reads
`last_assistant_message` for a `reports/...ru.html` (or `_ru.html`) path mention with no
`claude.ai/code/artifact/...` URL anywhere in the same message, and blocks on that alone. It needs
no git state at all, so it runs independently of the commit-count check above.

Program mode (added 2026-08-20, third revision, same shape as report_gate.py): "write a report per
closed gate" plus "stop after every report" adds up to "stop after every sub-gate" once a session is
working a long, already-authorized multi-gate program -- exactly wrong when the operator does not
want to babysit it. A genuine operator message containing the marker phrase (see
`_report_common.program_mode_declared`, e.g. "не останавливаться после каждого сабгейта" / "ОТЧЁТ:
ТОЛЬКО В КОНЦЕ") suspends the commit-count threshold check above for the rest of this transcript.
The artifact-link check is a format rule, not a cadence rule, and stays active regardless -- program
mode changes *when* a report is expected, never *what* a report must contain.

PM mode (added 2026-08-26) does two things here, in opposite directions. It is a second trigger for
the suspension above -- `program_mode_active` -- so a pre-authorized run stops being nagged in EVERY
project, not only in the session the operator typed the marker phrase into. And it adds the one
check in this file that blocks a stop in order to keep a session RUNNING: `pm_continue_reason`,
fired once per handed-over report, because suspending the hooks was never the whole problem. The
sessions that stopped were not blocked at all -- they read the html-report skill's step 6 and
stopped on their own, correctly. Under PM mode that step inverts, and this is where a session is
told so. Once per report, never repeated, so it cannot trap a session that genuinely must stop.

Deliberately quiet when:
  - the turn is already a hook re-entry (`stop_hook_active`);
  - the working tree has fresh report files -- the report is being written right now;
  - the repository has no reports/ directory at all, so the format was never adopted there;
  - anything at all goes wrong. A reminder is worth nothing if it can break a session.

Kill switches: CLAUDE_REPORT_DUE_GATE=off (both checks), CLAUDE_REPORT_LINK_GATE=off (link check
only). The PM continue-nudge has none on purpose: `/pm-bridge-mode off` is its switch, and a lever
that silences a check which STOPS a session must not also silence the one that keeps it going.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _report_common import (  # noqa: E402
    ARTIFACT_URL_RE,
    PLACEHOLDER_MARKERS,
    RU_REPORT_PATH_RE,
    SKILL_HINT,
    _complete_handover,
    git,
    listing,
    over_threshold,
    pm_mode_active,
    program_mode_active,
    report_being_written,
    skill_hint,
    unreported,
)


def state_dir() -> Path:
    override = os.environ.get("CLAUDE_HOOK_STATE_DIR")
    candidates = [Path(override) if override else None, Path(r"D:\tmp"), Path.home() / ".claude" / "tmp"]
    for cand in candidates:
        if cand is None:
            continue
        try:
            target = cand / "claude_report_due"
            target.mkdir(parents=True, exist_ok=True)
            return target
        except OSError:
            continue
    return Path.home() / ".claude_report_due"


def already_fired(root: Path, head: str) -> bool:
    key = hashlib.sha1(str(root).encode("utf-8", "replace")).hexdigest()[:16]
    marker = state_dir() / f"{key}.json"
    try:
        if marker.is_file() and json.loads(marker.read_text(encoding="utf-8")).get("head") == head:
            return True
    except (OSError, ValueError):
        pass
    try:
        marker.write_text(
            json.dumps({"head": head, "root": str(root), "at": int(time.time())}),
            encoding="utf-8",
        )
    except OSError:
        pass
    return False


def reason_for(root: Path, run: list[tuple[str, str, int]], pm_mode: bool = False) -> str:
    return (
        f"ОТЧЁТ ПРОСРОЧЕН: в {root.name} {len(run)} коммит(ов) после последнего, "
        f"который трогал reports/:\n{listing(run)}\n\n"
        "Формат отчётов обязателен для закрытых гейтов, ревью и статусов (правило оператора, "
        f"см. скилл html-report). Сделай отчёт по этой работе:\n{skill_hint(pm_mode)}\n\n"
        "Если эта работа действительно не тянет на отчёт (мелкий фикс, правка комментария) — "
        "скажи это прямо одной строкой и продолжай; хук по этим коммитам больше не сработает."
    )


def missing_artifact_link(message: str) -> str | None:
    """The path of the mentioned Russian report if the handover has no artifact link, else None."""
    if ARTIFACT_URL_RE.search(message):
        return None
    for hit in RU_REPORT_PATH_RE.finditer(message):
        path = hit.group(0)
        if not any(marker in path for marker in PLACEHOLDER_MARKERS):
            return path
    return None


def link_reason_for(report_path: str, pm_mode: bool = False) -> str:
    tail = (
        "  3. ПРОДОЛЖАЙ дальше по программе — ПМ-режим включён, отчёт не точка остановки."
        if pm_mode
        else "  3. ОСТАНОВИСЬ и жди оператора."
    )
    return (
        f"ОТЧЁТ БЕЗ ССЫЛКИ НА АРТЕФАКТ: в ответе назван локальный путь ({report_path}), "
        "но в сообщении нет ссылки на опубликованный артефакт (https://claude.ai/code/artifact/...).\n\n"
        "Правило оператора: обе ссылки обязательны в каждой передаче отчёта — локальный путь И "
        "ссылка на артефакт (скилл html-report, п.1 \"Two files, one link\"). Локальный путь один, "
        "без артефакта, не считается готовой передачей.\n\n"
        "Исправь сейчас:\n"
        "  1. Опубликуй русскую версию через Artifact tool (тот же путь на редеплое сохраняет URL,\n"
        "     если уже публиковал этот файл раньше).\n"
        "  2. Дай в ответе обе ссылки: локальный путь и ссылку на артефакт claude.ai.\n"
        f"{tail}"
    )


# --- PM mode: a report is a checkpoint, not a stopping point -----------------------------------
#
# Suspending the cadence checks (see `_report_common.program_mode_active`) only removes the
# mechanical block. It does not make a session CONTINUE -- and the sessions that stopped were not
# being blocked at all: they read the html-report skill's step 6 ("ОСТАНОВИТЬСЯ и ждать оператора"),
# correctly, and stopped on their own. One of them said so verbatim when asked why:
#
#   "Это не техническое ограничение, а сознательно встроенный чек-пойнт: скилл html-report ...
#    трактует связку «репорт + push» как обязательную точку хендовера."
#
# So under PM mode the instruction itself has to invert, and be delivered at the moment it applies.
# This nudge fires exactly once per handed-over report, on the turn that hands it over, and never
# again for that artifact URL -- it cannot livelock a session, and it cannot fire on an ordinary
# conversational turn, because its trigger is a complete handover (real report path + artifact URL)
# in the session's own last message.
def nudge_state_dir() -> Path:
    override = os.environ.get("CLAUDE_HOOK_STATE_DIR")
    candidates = [Path(override) if override else None, Path(r"D:\tmp"), Path.home() / ".claude" / "tmp"]
    for cand in candidates:
        if cand is None:
            continue
        try:
            target = cand / "claude_pm_continue"
            target.mkdir(parents=True, exist_ok=True)
            return target
        except OSError:
            continue
    return Path.home() / ".claude_pm_continue"


def already_nudged(artifact_url: str) -> bool:
    key = hashlib.sha1(artifact_url.encode("utf-8", "replace")).hexdigest()[:16]
    marker = nudge_state_dir() / f"{key}.marker"
    try:
        if marker.is_file():
            return True
        marker.write_text(artifact_url, encoding="utf-8")
    except OSError:
        # Cannot remember having nudged -> do not nudge, rather than risk repeating it every turn.
        return True
    return False


def pm_continue_reason(report_path: str) -> str:
    return (
        f"ПМ-РЕЖИМ: ОТЧЁТ ПЕРЕДАН, НО ЭТО НЕ КОНЕЦ СЕССИИ ({report_path}).\n\n"
        "PM Bridge orchestrator mode включён — значит прогон уже авторизован целиком, и отчёт в нём "
        "точка фиксации, а не точка хендовера. Шаг 6 скилла html-report («остановиться и ждать») "
        "в этом режиме НЕ действует.\n\n"
        "Инструкция оператора (2026-08-26): «сессия может закончиться только тогда, когда задача "
        "полностью выполнена».\n\n"
        "Что делать сейчас:\n"
        "  1. Продолжай к следующему гейту программы прямо в этом ходе.\n"
        "  2. Закончить ход можно, только если: программа выполнена целиком, ИЛИ ты упёрся в "
        "решение, которое по §4/§14 принимает лично оператор (необратимое, секреты, force-push, "
        "создание ветки, реальные деньги). Во втором случае назови это решение одной строкой.\n"
        "  3. Вопрос, который НЕ из этого списка, идёт к GPT-PM по §16, а не оператору.\n\n"
        "Это напоминание срабатывает один раз на отчёт — следующий Stop пройдёт в любом случае."
    )


def main() -> int:
    global_off = os.environ.get("CLAUDE_REPORT_DUE_GATE", "").lower() == "off"

    data = json.loads(sys.stdin.read() or "{}")
    if data.get("stop_hook_active"):
        return 0

    reasons = []
    last_message = data.get("last_assistant_message") or ""
    pm_mode = pm_mode_active()

    if not global_off and os.environ.get("CLAUDE_REPORT_LINK_GATE", "").lower() != "off":
        missing = missing_artifact_link(last_message)
        if missing:
            reasons.append(link_reason_for(missing, pm_mode))

    # The nudge is independent of CLAUDE_REPORT_DUE_GATE: that switch turns OFF a check that stops
    # a session, and this one exists to keep a session going. Silencing it with the same lever
    # would be backwards. Its own switch is PM mode itself -- /pm-bridge-mode off.
    if pm_mode and not reasons:
        handover = _complete_handover(last_message)
        if handover and not already_nudged(handover[1]):
            reasons.append(pm_continue_reason(handover[0]))

    if not global_off and not program_mode_active(data.get("transcript_path")):
        cwd = Path(data.get("cwd") or os.getcwd())
        root_raw = git(["rev-parse", "--show-toplevel"], cwd)
        if root_raw:
            root = Path(root_raw)
            if (root / "reports").is_dir() and not report_being_written(root):
                run = unreported(root)
                if over_threshold(run):
                    head = git(["rev-parse", "HEAD"], root)
                    if head and not already_fired(root, head):
                        reasons.append(reason_for(root, run, pm_mode))

    if reasons:
        print(json.dumps({"decision": "block", "reason": "\n\n---\n\n".join(reasons)},
                          ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        # A reminder must never be the thing that breaks a session.
        raise SystemExit(0)
