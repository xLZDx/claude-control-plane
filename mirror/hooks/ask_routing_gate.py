"""PreToolUse gate for AskUserQuestion: route decisions to GPT-PM, not to the operator.

Operator instruction, 2026-08-26: "надо чтобы все вопросы отправлялись гпт а не мне (нужно что то
выбрать, ответить на вопросы, принять решение, и так далее) но без диструктивных удалений."

The trigger was a live screenshot: a session hit the push gate and put three options to the
operator -- set a kill switch, wait indefinitely, or mark a review `--final` by hand. None of
those needed a human. They needed a reviewer with the project's context, which is exactly what
GPT-PM is and what PM Bridge exists to reach. Every such question spent on the operator is a
stall in an otherwise autonomous run.

So: a question a session would put to the operator goes to GPT-PM instead, and the session
decides from the answer. What stays with the operator is the class where being wrong is
unrecoverable -- destructive deletion, history rewrite, production/real-money actions, secrets,
external publishing. Those are the operator's under CLAUDE.md 4 regardless of who has context,
and no reviewer's opinion substitutes for that authorization.

Design notes, because the failure modes here are the interesting part:

  - FAIL OPEN on anything unexpected. A hook that hard-blocks a session's only way of asking is
    worse than the stall it removes -- a wrongly-denied question leaves a session with no route
    to anyone at all.
  - ESCAPE HATCH, mandatory. If GPT-PM is unreachable, or has already been asked and its answer
    genuinely does not settle the question, the session includes GPT_ASKED_MARKER in the question
    text and this gate allows it through. Without that, a broken transport plus this gate equals
    a session that can neither ask nor proceed. The marker is a claim by the session, exactly as
    `--final` is in review.js, and carries the same obligation to be true.
  - The destructive check reads the WHOLE payload (questions, headers, options, descriptions),
    not just the header, and errs toward allowing: a false "destructive" costs one question to
    the operator, while a false "safe" routes an irreversible decision to a reviewer who cannot
    authorize it.

Kill switch: CLAUDE_ASK_ROUTING_GATE=off -- process-level, set before the session starts.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path(r"D:\tmp\claude_ask_routing_gate")
DECISIONS_FILE = STATE_DIR / "decisions.jsonl"

GPT_ASKED_MARKER = "[GPT-ASKED]"

# Deciding wrongly here is unrecoverable, so these stay with the operator no matter who has more
# context. Kept deliberately broad, in both languages the operator works in: over-matching costs
# one question, under-matching routes an irreversible decision to someone who cannot authorize it.
DESTRUCTIVE_RE = re.compile(
    r"""
    \b(
        delet\w* | deletion | remov\w* | drop(?:ping|ped)? | wipe\w* | purg\w* | erase\w* |
        destroy\w* | truncat\w* | overwrit\w* | discard\w* |
        rm\s+-rf | reset\s+--hard | git\s+clean | branch\s+-D |
        force[-\s]?push | --force\b | rewrite\s+history | filter-(?:branch|repo) |
        revert\w* | rollback | roll\s+back |
        prod(?:uction)? | deploy\w* | release\s+build | publish\w* |
        migrat\w* | schema\s+change |
        secret\w* | credential\w* | token\w* | api[-\s]?key | password\w* |
        real[-\s]money | live[-\s]trading | withdraw\w* | payment\w*
    )\b
    |
    (?:удал | снос | сноси | уничтож | очист | перезапис | отмен | откат |
       продакш | продакшн | боев | деплой | публик | мигра | секрет | парол |
       креденш | ключ\w*\s+доступ | реальн\w*\s+деньг | форс[-\s]?пуш)
    """,
    re.IGNORECASE | re.VERBOSE,
)


def log(entry):
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        entry["ts"] = datetime.now(timezone.utc).isoformat()
        with open(DECISIONS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def allow(reason=None, extra=None):
    if reason:
        log({"decision": "allow", "reason": reason, **(extra or {})})
    sys.exit(0)


def deny(reason, payload_preview):
    log({"decision": "deny", "reason": "routed to GPT-PM", "question": payload_preview})
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    sys.exit(0)


def collect_text(tool_input):
    """Every operator-visible string in the payload, so the destructive check cannot be dodged
    by putting the dangerous word in an option description instead of the question."""
    parts = []
    for q in tool_input.get("questions") or []:
        if not isinstance(q, dict):
            continue
        parts.append(str(q.get("question", "")))
        parts.append(str(q.get("header", "")))
        for opt in q.get("options") or []:
            if isinstance(opt, dict):
                parts.append(str(opt.get("label", "")))
                parts.append(str(opt.get("description", "")))
    return "\n".join(p for p in parts if p)


DENY_MESSAGE = """This question goes to GPT-PM, not to the operator (operator instruction,
2026-08-26; see ~/.claude/CLAUDE.md "Questions go to GPT-PM").

Ask it through PM Bridge instead -- mcp__pm-bridge__gpt_send_and_await, with the `project` set to
this repo -- then decide from the answer and carry on. Give GPT the same thing you would have
given the operator: the actual options, what each costs, what you recommend, and the evidence.
Its reply is a reviewer's opinion, not an authorization: weigh it, and say plainly in your own
reply what you asked, what came back, and what you decided.

The operator still owns anything irreversible -- destructive deletion, history rewrite,
production or real-money actions, secrets, external publishing. Those are theirs under CLAUDE.md
4 regardless of who has more context, and this gate lets such questions through untouched.

If GPT-PM is genuinely unreachable, or you have already asked it and its answer does not settle
the question, put %s in the question text and ask again -- this gate will allow it. Use that
honestly: it is a claim that you actually tried, in the same way --final is a claim in review.js.
""" % GPT_ASKED_MARKER


def main():
    if os.environ.get("CLAUDE_ASK_ROUTING_GATE", "").lower() == "off":
        allow()

    try:
        data = json.load(sys.stdin)
    except Exception as e:
        log({"decision": "fail-open", "reason": f"bad stdin: {e}"})
        allow()

    if data.get("tool_name") != "AskUserQuestion":
        allow()

    tool_input = data.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        allow("fail-open: tool_input not a dict")

    try:
        text = collect_text(tool_input)
    except Exception as e:
        log({"decision": "fail-open", "reason": f"could not read questions: {e}"})
        allow()

    if not text.strip():
        allow("fail-open: no question text to classify")

    if GPT_ASKED_MARKER.lower() in text.lower():
        allow("session declares GPT-PM was already asked or is unreachable",
              {"question": text[:400]})

    m = DESTRUCTIVE_RE.search(text)
    if m:
        allow("irreversible/authorization class -- stays with the operator",
              {"matched": m.group(0)[:60], "question": text[:400]})

    deny(DENY_MESSAGE, text[:600])


if __name__ == "__main__":
    main()
