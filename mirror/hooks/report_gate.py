#!/usr/bin/env python3
"""PreToolUse hook -- blocks `git commit`/`git push` once a report is owed, or was just handed
over and never answered.

Built to the same shape as decision_log_gate.py, at operator request (2026-08-19): the report
format should be enforced the way the decision log is, so no session can forget it. The Stop hook
report_due.py already reminds at the end of a turn; this one enforces at the boundary that
actually matters in a long autonomous run, where turns can be hours apart.

Two independent checks, both suspended by program mode (see below):

1. Unreported work (git commit only). Commits made after the most recent commit that touched
   reports/. Past the shared threshold (see _report_common.py) the next commit is denied until a
   report is written and committed.

2. Unanswered handover (git commit AND git push, added 2026-08-19 same day). The skill says to
   STOP after handing a report over; nothing enforced it. A Fitness_App session handed over a
   stop-the-line report -- dream-team review found the tested APK wasn't even built from the
   branch under test -- got no operator reply (only an automatic context-compaction boundary), and
   kept going: wrote a second report, committed it, pushed. The operator caught it from a VS Code
   "open external website" popup on the first report's link and asked why the session hadn't
   simply stopped. This reads the session's own transcript (see
   `_report_common.unanswered_handover`) for a complete, unanswered handover and denies outright
   if one is found -- independent of what the commit/push actually carries.

Program mode (added 2026-08-19, same day, third revision): "write a report per closed gate" plus
"stop after every report" adds up to "stop after every sub-gate" once a session is working a long,
already-authorized multi-gate program -- exactly wrong when the operator does not want to babysit
it. A genuine operator message containing the marker phrase (see
`_report_common.program_mode_declared`, e.g. "не останавливаться после каждого сабгейта" /
"ОТЧЁТ: ТОЛЬКО В КОНЦЕ") suspends both checks above for the rest of this transcript. Report FORMAT
rules and every other protection (destructive ops, force-push, credentials) are untouched -- this
only changes when a report is expected, not whether one is.

Always allowed, so the gate cannot deadlock:
  - program mode is declared;
  - no unanswered handover, and (for commit) the commit itself carries reports/ files;
  - no unanswered handover, and (for commit) the repository has no reports/ directory;
  - no unanswered handover, and (for commit) report files are fresh on disk (session is mid-write);
  - anything at all goes wrong: git missing, bad stdin, timeout, unreadable transcript. Fail open,
    never crash a session.

Kill switches: CLAUDE_REPORT_GATE=off (everything in this file),
CLAUDE_REPORT_HANDOVER_GATE=off (check 2 only; must be set before the session starts)
Decisions:   D:\\tmp\\claude_report_gate\\decisions.jsonl
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _report_common import (  # noqa: E402
    SKILL_HINT,
    git,
    listing,
    over_threshold,
    pm_mode_active,
    program_mode_declared,
    report_being_written,
    unanswered_handover,
    unreported,
)

COMMIT_RE = re.compile(r"\bgit\s+commit\b", re.IGNORECASE)
PUSH_RE = re.compile(r"\bgit\s+push\b", re.IGNORECASE)
SKIP_RE = re.compile(r"--help\b|(?<!\S)-h\b|--dry-run\b|--amend\b", re.IGNORECASE)
CD_RE = re.compile(r'^\s*cd\s+(?P<path>"[^"]+"|\'[^\']+\'|\S+)\s*$')
GITBASH_DRIVE_RE = re.compile(r"^/([A-Za-z])(?=/|$)")
REPORT_PATH_RE = re.compile(r"(^|[\s\"'/])reports/", re.IGNORECASE)


def state_dir() -> Path:
    override = os.environ.get("CLAUDE_HOOK_STATE_DIR")
    candidates = [Path(override) if override else None, Path(r"D:\tmp"), Path.home() / ".claude" / "tmp"]
    for cand in candidates:
        if cand is None:
            continue
        try:
            target = cand / "claude_report_gate"
            target.mkdir(parents=True, exist_ok=True)
            return target
        except OSError:
            continue
    return Path.home() / ".claude_report_gate"


def log_decision(entry: dict) -> None:
    try:
        entry["ts"] = int(time.time())
        with (state_dir() / "decisions.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


def normalise_shell_path(path: str) -> str:
    path = path.strip().strip("\"'")
    hit = GITBASH_DRIVE_RE.match(path)
    if hit:
        path = f"{hit.group(1)}:" + path[2:]
    return path


def resolve_effective_cwd(command: str, base_cwd: str) -> str:
    """A leading `cd <path> && git commit ...` moves the repo the commit lands in."""
    for part in re.split(r"&&|\|\||;", command):
        hit = CD_RE.match(part)
        if hit:
            candidate = normalise_shell_path(hit.group("path"))
            if Path(candidate).is_dir():
                return candidate
    return base_cwd


def allow(entry: dict | None = None) -> None:
    if entry:
        log_decision(entry)
    sys.exit(0)


def deny(reason: str, entry: dict) -> None:
    entry["decision"] = "deny"
    log_decision(entry)
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            },
            ensure_ascii=False,
        )
    )
    sys.exit(0)


def commit_carries_report(command: str, root: Path) -> bool:
    """True when this commit is itself the report -- staged reports/, or named on the command."""
    staged = git(["diff", "--cached", "--name-only"], root)
    if staged and any(p.replace("\\", "/").startswith("reports/") for p in staged.splitlines()):
        return True
    if REPORT_PATH_RE.search(command):
        return True
    # `git commit -a` / a broad `git add` sweeps up modified report files that are not staged yet.
    if re.search(r"git\s+commit\s+[^&|;]*(-a\b|--all\b)", command, re.IGNORECASE) or re.search(
        r"git\s+add\s+(-A\b|--all\b|\.\s|\.$|-u\b)", command, re.IGNORECASE
    ):
        changed = git(["status", "--porcelain", "--", "reports"], root)
        if changed:
            return True
    return False


def reason_for(root: Path, run: list[tuple[str, str, int]]) -> str:
    return (
        f"КОММИТ ЗАБЛОКИРОВАН: в {root.name} уже {len(run)} коммит(ов) после последнего, "
        f"который трогал reports/:\n{listing(run)}\n\n"
        "Правило оператора: формат отчётов обязателен для закрытых гейтов, ревью и статусов "
        "(скилл html-report). Отчёт пишется ДО следующего коммита, а не когда-нибудь потом.\n\n"
        f"{SKILL_HINT}\n\n"
        "Коммит с файлами reports/ этот гейт пропускает — сделай отчёт, закоммить его, и текущий "
        "коммит пройдёт следующим.\n"
        "Если работа действительно не тянет на отчёт (мелкий фикс, правка комментария) — скажи это "
        "оператору одной строкой и попроси у него разрешение; обходить гейт молча нельзя."
    )


def handover_reason_for(report_path: str, action: str) -> str:
    return (
        f"{action.upper()} ЗАБЛОКИРОВАН: последняя завершённая передача отчёта ({report_path}) "
        "ещё не получила ответа оператора. С тех пор в истории сессии есть только служебные записи "
        "(например, граница сжатия контекста) — ни одного нового сообщения от оператора.\n\n"
        "Правило оператора (скилл html-report, п.5-6): передача отчёта — точка остановки. После "
        "неё сессия ждёт оператора, а не пишет следующий отчёт, не коммитит и не пушит дальше.\n\n"
        "Что делать сейчас:\n"
        "  1. НЕ пытаться обойти это ещё одним коммитом/пушем.\n"
        "  2. Закончить текущий ход одним сообщением: коротко напомнить, какой отчёт передан и что "
        "он требует, и явно попросить решение оператора.\n"
        "  3. Ждать. Автоматическое продолжение контекста (сжатие) — это не ответ оператора.\n\n"
        f"Kill switch на случай, если это ложное срабатывание: CLAUDE_REPORT_HANDOVER_GATE=off "
        "(ставится оператором в окружении до старта сессии, не самой сессией)."
    )


def main() -> None:
    if os.environ.get("CLAUDE_REPORT_GATE", "").lower() == "off":
        allow()

    try:
        payload = json.loads(sys.stdin.read())
    except Exception as exc:
        allow({"decision": "fail-open", "reason": f"bad stdin: {exc}"})

    command = (payload.get("tool_input") or {}).get("command", "") or ""
    is_commit = bool(COMMIT_RE.search(command))
    is_push = bool(PUSH_RE.search(command))
    if not (is_commit or is_push) or SKIP_RE.search(command):
        allow()

    transcript_path = payload.get("transcript_path")
    if program_mode_declared(transcript_path):
        # A genuine operator message pre-authorized the whole enumerated program: sub-gate reports
        # are informational, not synchronization barriers. Both cadence checks below are suspended
        # for the rest of this transcript; report FORMAT rules are untouched.
        allow({"decision": "allow", "reason": "program mode declared by operator"})

    if pm_mode_active():
        # Same suspension, standing rather than per-session: PM Bridge orchestrator mode is a global
        # toggle, and having it on already means a pre-authorized run is under way. Without this,
        # every project except the one the operator typed the marker phrase into kept stopping at
        # its own report handover (operator instruction, 2026-08-26).
        allow({"decision": "allow", "reason": "PM Bridge orchestrator mode is on"})

    if os.environ.get("CLAUDE_REPORT_HANDOVER_GATE", "").lower() != "off":
        pending = unanswered_handover(transcript_path)
        if pending:
            deny(
                handover_reason_for(pending, "push" if is_push and not is_commit else "commit"),
                {"decision": "deny", "reason": "unanswered handover", "report": pending},
            )

    if not is_commit:
        # git push has no equivalent "did this push contain a report" concept, so only the
        # unanswered-handover check above applies to it; the unreported-work threshold below is
        # commit-only.
        allow()

    cwd = resolve_effective_cwd(command, payload.get("cwd") or os.getcwd())
    root_raw = git(["rev-parse", "--show-toplevel"], cwd)
    if not root_raw:
        allow({"decision": "fail-open", "reason": "not a git repo or git error", "cwd": cwd})
    root = Path(root_raw)

    if not (root / "reports").is_dir():
        allow({"decision": "allow", "reason": "no reports/ directory", "repo": str(root)})
    if commit_carries_report(command, root):
        allow({"decision": "allow", "reason": "commit carries the report", "repo": str(root)})
    if report_being_written(root):
        allow({"decision": "allow", "reason": "report files are fresh", "repo": str(root)})

    run = unreported(root)
    if not over_threshold(run):
        allow({"decision": "allow", "reason": f"{len(run)} unreported, under threshold",
               "repo": str(root)})

    deny(reason_for(root, run), {"repo": str(root), "unreported": len(run),
                                 "commits": [short for short, _, _ in run]})


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        # A gate that crashes a session is worse than a gate that misses one commit.
        log_decision({"decision": "fail-open", "reason": f"unhandled: {exc}"})
        sys.exit(0)
