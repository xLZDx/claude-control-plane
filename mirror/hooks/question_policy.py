#!/usr/bin/env python3
"""Question policy hook (operator 2026-10-21). One script, three events:

  PreToolUse  (AskUserQuestion): every question must carry >=2 options with a "(Recommended)" option placed
              first. If the operator has been silent for `idle_minutes` when the question is asked, the
              recommended option is accepted automatically (updatedInput.answers) and the decision is logged.
              Irreversible/destructive questions are never auto-accepted (they stay with the operator,
              CLAUDE.md section 3) unless config `include_destructive` is true.
  Stop:       a turn must not end with an open question to the operator written as plain prose; it has to go
              through AskUserQuestion. Blocks at most once per message.
  UserPromptSubmit: tells the assistant which questions were auto-answered while the operator was away.

Replaces ask_routing_gate.py (which routed operator questions to GPT-PM and denied them).
Kill switch: CLAUDE_QUESTION_POLICY=off. Config: D:\\tmp\\claude_question_policy\\config.json. Stdlib only; fails open.
"""
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

STATE = Path(os.environ.get("CLAUDE_QUESTION_POLICY_STATE", r"D:\tmp\claude_question_policy"))
CONFIG = STATE / "config.json"
LEDGER = STATE / "auto_answers.jsonl"
DEFAULTS = {"idle_minutes": 5, "auto_accept": True, "include_destructive": False,
            "only_sessions": None, "stop_gate": True}
REC_RE = re.compile(r"\(\s*(recommended|рекомендую|рекомендуется|рекомендовано)\s*\)\s*$", re.I)
AUTOMATED = ("<task-notification>", "<system-reminder>", "[SYSTEM NOTIFICATION", "[Request interrupted", "Caveat:")

try:
    sys.path.insert(0, str(Path(__file__).parent))
    from ask_routing_gate import DESTRUCTIVE_RE, collect_text  # the old gate stays on disk as a library
except Exception:  # pragma: no cover - fallback if the old file is ever removed
    DESTRUCTIVE_RE = re.compile(r"delet|remov|drop|wipe|purge|force[- ]?push|reset --hard|удал|сн[оё]с|уничтож|очист", re.I)

    def collect_text(ti):
        out = []
        for q in ti.get("questions") or []:
            out += [str(q.get("question", "")), str(q.get("header", ""))]
            for o in q.get("options") or []:
                out += [str(o.get("label", "")), str(o.get("description", ""))]
        return "\n".join(out)


def cfg():
    c = dict(DEFAULTS)
    try:
        c.update(json.loads(CONFIG.read_text(encoding="utf-8")))
    except Exception:
        pass
    return c


def session_in_scope(c, sid):
    only = c.get("only_sessions")
    return True if not only else any(str(sid).startswith(p) for p in only)


def log_ledger(entry):
    try:
        STATE.mkdir(parents=True, exist_ok=True)
        entry["ts"] = datetime.now(timezone.utc).isoformat()
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def tail_rows(path, max_bytes=6_000_000):
    rows = []
    try:
        with open(path, "rb") as fh:
            fh.seek(0, 2)
            size = fh.tell()
            fh.seek(max(0, size - max_bytes))
            data = fh.read()
        lines = data.split(b"\n")
        if size > max_bytes:
            lines = lines[1:]
        for ln in lines:
            if ln.strip():
                try:
                    rows.append(json.loads(ln))
                except Exception:
                    pass
    except Exception:
        pass
    return rows


def is_human(row):
    if row.get("isMeta") or row.get("isSidechain") or row.get("isCompactSummary"):
        return False
    t = row.get("type")
    if t == "user":
        if "toolUseResult" in row:
            return False
        if row.get("turnOrigin") not in (None, "human"):  # scheduled/system turns are not the operator
            return False
        c = (row.get("message") or {}).get("content")
        if isinstance(c, list):
            if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in c):
                return False
            c = " ".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
        if not isinstance(c, str) or not c.strip():
            return False
        return not c.lstrip().startswith(AUTOMATED)
    if t == "attachment":
        a = row.get("attachment") or {}
        return a.get("type") == "queued_command" and (a.get("origin") or {}).get("kind") == "human"
    return False


def is_activity(row, gpt_ids=None):
    """Only the operator's own messages reset the silence clock (operator 2026-10-22). Machine traffic -- PM Bridge (GPT)
    replies and errors, scheduled/cron prompts, notifications, tool results -- does not: during a long bridge polling
    loop it used to keep the clock near zero while the operator had been away for hours."""
    return is_human(row)


def _row_time(row):
    try:
        return datetime.fromisoformat(str(row.get("timestamp")).replace("Z", "+00:00"))
    except Exception:
        return None


def idle_minutes(transcript_path):
    """Minutes since the operator's last own message; None if it cannot be determined.

    Only the tail of a large transcript is read. If that tail holds no operator message at all, the operator has been
    silent at least as long as the tail spans, so the age of its first row is returned as a lower bound."""
    rows = tail_rows(transcript_path)
    now = datetime.now(timezone.utc)
    for row in reversed(rows):
        if is_activity(row):
            ts = _row_time(row)
            return None if ts is None else (now - ts).total_seconds() / 60.0
    for row in rows:
        ts = _row_time(row)
        if ts is not None:
            return (now - ts).total_seconds() / 60.0
    return None


def asked_this_turn(transcript_path):
    for row in reversed(tail_rows(transcript_path)):
        if is_human(row):
            return False
        msg = row.get("message") or {}
        if msg.get("role") == "assistant" and isinstance(msg.get("content"), list):
            for b in msg["content"]:
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "AskUserQuestion":
                    return True
    return False


def out_json(obj):
    print(json.dumps(obj, ensure_ascii=False))
    sys.exit(0)


FORMAT_MSG = """Question policy (operator 2026-10-21): every question to the operator must be an AskUserQuestion with
options and a recommendation. Fix and ask again:
  - each question has at least 2 options;
  - exactly one option is your recommendation, it is the FIRST option, and its label ends with "(Recommended)";
  - the question says in words what is being decided, and each option says the concrete consequence.
If the operator does not answer, the recommended option is accepted, so recommend what you would do anyway.
Problems found: %s"""


def destructive_scope(qs):
    """Text the destructive-word check looks at (operator 2026-10-25): only the `header` chip of each
    question. The question text, option labels and descriptions are not scanned (a feature name such
    as "волне W2 (удаление аккаунта)" is not an action)."""
    return " | ".join(str(q.get("header", "")) for q in qs)


def pre(data, c):
    ti = data.get("tool_input") or {}
    qs = ti.get("questions")
    if not isinstance(qs, list) or not qs:
        return
    problems = []
    for i, q in enumerate(qs, 1):
        opts = [o for o in (q.get("options") or []) if isinstance(o, dict)]
        rec = [k for k, o in enumerate(opts) if REC_RE.search(str(o.get("label", "")).strip())]
        if len(opts) < 2:
            problems.append(f"question {i}: fewer than 2 options")
        if not rec:
            problems.append(f"question {i}: no option labelled (Recommended)")
        elif len(rec) > 1 and not q.get("multiSelect"):
            problems.append(f"question {i}: more than one (Recommended) option")
        elif rec[0] != 0:
            problems.append(f"question {i}: the recommended option must be first")
    if problems:
        out_json({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                         "permissionDecisionReason": FORMAT_MSG % "; ".join(problems)}})
    if not c["auto_accept"]:
        return
    idle = idle_minutes(data.get("transcript_path") or "")
    if idle is None or idle < float(c["idle_minutes"]):
        return  # operator is around: show the question normally
    text = destructive_scope(qs)
    if DESTRUCTIVE_RE.search(text) and not c["include_destructive"]:
        log_ledger({"sid": str(data.get("session_id"))[:8], "action": "kept-for-operator-destructive", "q": text[:200]})
        return
    answers = {}
    for q in qs:
        opts = [o for o in (q.get("options") or []) if isinstance(o, dict)]
        answers[q.get("question", "")] = next(str(o["label"]) for o in opts if REC_RE.search(str(o.get("label", "")).strip()))
    log_ledger({"sid": str(data.get("session_id"))[:8], "action": "auto-accepted", "idle_min": round(idle, 1),
                "answers": answers})
    out_json({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "allow",
        "permissionDecisionReason": f"Operator silent for {idle:.0f} min (limit {c['idle_minutes']}): recommended options accepted.",
        "updatedInput": {**ti, "answers": answers}}})


QUESTION_TRIGGERS = re.compile(
    r"(скажите|подтвердите|выберите|решите|ответьте|нужно ваше решение|ваш выбор|как поступить|что выбрать|"
    r"хотите ли|хотите,? чтобы|согласны|давать ли|осталось в вашей части|"
    r"do you want|should i\b|shall i\b|let me know|please confirm|your call)", re.I)

STOP_MSG = """Question policy (operator 2026-10-21): your reply ends with an open question to the operator written as plain
text. Questions to the operator must go through AskUserQuestion with options and a recommendation (recommended option
first, label ends with "(Recommended)"; each option states its consequence). Call AskUserQuestion now instead of
asking in prose. If the operator stays silent, the recommended options are accepted, so choose them with that in mind.
Irreversible actions (deletion, history rewrite, production, real money) still wait for the operator."""


def stop(data, c):
    if not c["stop_gate"] or data.get("agent_type") or data.get("stop_hook_active"):
        return
    msg = data.get("last_assistant_message") or ""
    tail = msg[-700:]
    lines = [ln.strip() for ln in tail.strip().splitlines() if ln.strip()]
    last = lines[-1] if lines else ""
    if not (last.rstrip("»)\"'` ").endswith("?") or QUESTION_TRIGGERS.search(tail)):
        return
    if asked_this_turn(data.get("transcript_path") or ""):
        return
    key = hashlib.sha1(msg.encode("utf-8", "replace")).hexdigest()[:16]
    seen_file = STATE / "stop_seen.json"
    try:
        seen = json.loads(seen_file.read_text(encoding="utf-8"))
    except Exception:
        seen = []
    if key in seen:
        return
    try:
        STATE.mkdir(parents=True, exist_ok=True)
        seen_file.write_text(json.dumps((seen + [key])[-50:]), encoding="utf-8")
    except Exception:
        pass
    out_json({"decision": "block", "reason": STOP_MSG})


def prompt(data, c):
    sid = str(data.get("session_id"))[:8]
    marker = STATE / f"reported_{sid}.txt"
    try:
        last = marker.read_text(encoding="utf-8").strip()
    except Exception:
        last = ""
    new = []
    try:
        for ln in LEDGER.read_text(encoding="utf-8").splitlines():
            e = json.loads(ln)
            if e.get("sid") == sid and e.get("action") == "auto-accepted" and e.get("ts", "") > last:
                new.append(e)
    except Exception:
        return
    if not new:
        return
    try:
        marker.write_text(new[-1]["ts"], encoding="utf-8")
    except Exception:
        pass
    lines = []
    for e in new:
        for q, a in e["answers"].items():
            lines.append(f"- {q[:120]} -> {a}")
    ctx = ("[Question policy] While the operator was silent, these questions were auto-answered with the recommended "
           "option. Say so in your next reply and revert if the operator disagrees:\n" + "\n".join(lines))
    out_json({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": ctx}})


def main():
    if os.environ.get("CLAUDE_QUESTION_POLICY", "").lower() == "off":
        return
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except Exception:
        return
    c = cfg()
    if not session_in_scope(c, data.get("session_id")):
        return
    ev = data.get("hook_event_name") or ("PreToolUse" if "tool_input" in data else
                                         "UserPromptSubmit" if "prompt" in data else "Stop")
    if ev == "PreToolUse" and data.get("tool_name") == "AskUserQuestion":
        pre(data, c)
    elif ev == "Stop":
        stop(data, c)
    elif ev == "UserPromptSubmit":
        prompt(data, c)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        pass  # fail open
    sys.exit(0)
