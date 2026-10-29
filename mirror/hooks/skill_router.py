#!/usr/bin/env python3
"""UserPromptSubmit hook (DRAFT, not installed) -- injects the body of a global
skill into the context when the operator's prompt matches that skill's trigger.
Each skill is injected at most once per session (state file), at most MAX_PER_PROMPT
skills per prompt, so the token cost is bounded and paid only when the task needs it.
Never blocks. Kill switch: CLAUDE_SKILL_ROUTER=off. stdlib only (hooks run with -s).
"""
import json
import os
import re
import sys
from pathlib import Path

SKILLS_DIR = Path(os.environ.get("CLAUDE_SKILLS_DIR", str(Path.home() / ".claude" / "skills")))
STATE_DIR = Path(os.environ.get("CLAUDE_SKILL_ROUTER_STATE", r"D:\tmp\claude_skill_router"))
TOKEN_BUDGET = 1600      # bodies are injected best-first until this many tokens (chars/4); the rest are named
HEAD_CHARS, TAIL_CHARS = 600, 300   # match only the operator's own words: start + end, pasted blocks removed
TEST_WORD = r"\bтест|\btest|тестир"
TEST_TRIO = ["functional-testing", "e2e-testing-contract", "performance-testing"]
MIN_PROMPT_LEN = 25  # skip "да", "ГО", acknowledgements

# Order = priority when more than MAX_PER_PROMPT match. Patterns are RU+EN.
TRIGGERS = [
    ("delivery-efficiency", r"спринт|sprint|гейт|\bgate\b|\bPR\b|pull request|план разработки|epic|DoD|(?-i:(?<!\w)(?:ГО|GO)(?!\w))"),
    ("migration-safety", r"миграци|migration|backfill|бэкфил|alembic|schema change"),
    ("db-change-contract", r"\bSQL\b|схем[аыу] бд|schema|индекс|index|query plan|транзакци|transaction|postgres"),
    ("security-evidence-contract", r"безопасн|security|уязвим|vulnerab|auth\b|авторизац|injection|SSRF|secret|секрет"),
    ("reliability-contract", r"retry|ретра|timeout|таймаут|queue|очеред|worker|restart|рестарт|idempoten|идемпотент"),
    ("observability-contract", r"логир|logging|metric|метрик|tracing|трейс|alert|алерт|runbook"),
    ("integration-contract", r"webhook|вебхук|\bAPI\b|коннектор|connector|интеграци|integration|third-party"),
    ("performance-testing", r"производительн|performance|benchmark|бенчмарк|latency|медленн|profil|профил"),
    ("e2e-testing-contract", r"e2e|end-to-end|playwright|cypress|сценари[йя] пользовател|user journey"),
    ("a11y-contract", r"a11y|accessib|доступност|screen reader|скринридер|контраст"),
    ("ux-design-contract", r"\bUX\b|\bUI\b|интерфейс|user flow|экран|форм[аы] ввода|дизайн интерфейса"),
    ("architecture-contract", r"архитектур|architecture|границ[аы] модул|boundary|масштабир|scalab"),
    ("technical-design", r"спроектир|design doc|технический дизайн|technical design|план изменени|затрагивает несколько"),
    ("git-worktree-ops", r"worktree|воркtree|несколько checkout|параллельн\w+ сесси|concurrent session"),
    ("functional-testing", r"\bтест|\btest|регресс|regression|покрыти|coverage"),
    ("implementation-workflow", r"реализуй|исправ|почини|чини\b|добавь|implement|\bfix\b|\bbug\b|баг|ошибк|рефактор|refactor|сделай|допиши|доработ|закоммит"),
    ("repo-recon", r"разберись|как устроен|найди где|explore the repo|unfamiliar|незнаком|обзор репозитор"),
    ("verification-contract", r"готово ли|работает ли|проверь,? что|убедись|подтверди|докажи|\bverify that\b|\bis it done\b|\bdone\?|прежде чем сказать"),
]


def load_body(name):
    p = SKILLS_DIR / name / "SKILL.md"
    try:
        t = p.read_text(encoding="utf-8")
    except Exception:
        return None
    m = re.match(r"---\s*\n.*?\n---\s*\n?(.*)", t, re.S)
    return (m.group(1) if m else t).strip()


AUTOMATED_MARKERS = ("<task-notification>", "<<autonomous-loop", "[SYSTEM NOTIFICATION", "<system-reminder>")


def log(event):
    """Append-only trace of every invocation so we can see what the hook actually receives."""
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        with (STATE_DIR / "router.log.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass


def main():
    import time
    if os.environ.get("CLAUDE_SKILL_ROUTER", "").lower() == "off":
        sys.exit(0)
    try:
        payload = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)
    prompt = (payload.get("prompt") or "").strip()
    base = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "sid": str(payload.get("session_id"))[:8],
            "len": len(prompt), "head": prompt[:90]}
    if len(prompt) < MIN_PROMPT_LEN:
        log({**base, "action": "skip-short"})
        sys.exit(0)
    if any(m in prompt[:400] for m in AUTOMATED_MARKERS):
        log({**base, "action": "skip-automated"})
        sys.exit(0)
    sid = re.sub(r"[^A-Za-z0-9_.-]", "_", str(payload.get("session_id") or "nosession"))
    state_file = STATE_DIR / f"{sid}.json"
    try:
        done = set(json.loads(state_file.read_text(encoding="utf-8")))
    except Exception:
        done = set()
    # Match only the operator's own words: drop pasted blocks, keep the start and the end of a long message.
    text = re.sub(r"<pasted_content.*?</pasted_content[^>]*>", " ", prompt, flags=re.S)
    if len(text) > HEAD_CHARS + TAIL_CHARS:
        text = text[:HEAD_CHARS] + " " + text[-TAIL_CHARS:]
    # Rank every matching, not-yet-injected skill by how many times its trigger hits (then list order);
    # inject bodies best-first until TOKEN_BUDGET, and name the rest in one line so nothing is silently dropped.
    scored = []
    test_word = re.search(TEST_WORD, text, re.I) is not None
    for idx, (name, pat) in enumerate(TRIGGERS):
        if name in done:
            continue
        n = len(re.findall(pat, text, re.I))
        if test_word and name in TEST_TRIO:
            # operator rule 2026-10-10: the word "test" gives the test block priority over every other skill
            scored.append((-(1000 + n), TEST_TRIO.index(name), name))
        elif n:
            scored.append((-n, 100 + idx, name))
    scored.sort()
    ranked = [s[2] for s in scored]
    hits, rest, parts, used = [], [], [], 0
    for name in ranked:
        body = load_body(name)
        if not body:
            continue
        cost = len(body) // 4
        if hits and used + cost > TOKEN_BUDGET:
            rest.append(name)          # over budget: named, not loaded, stays eligible for the next message
            continue
        parts.append(f"## Skill: {name}\n{body}")
        hits.append(name)
        used += cost
        done.add(name)
    if not parts:
        log({**base, "action": "no-match"})
        sys.exit(0)
    if rest:
        parts.append("## Also matched, NOT loaded (call the Skill tool for any that apply): " + ", ".join(rest))
    log({**base, "action": "inject", "skills": hits, "also": rest})
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps(sorted(done)), encoding="utf-8")
    except Exception:
        pass  # state is best-effort; worst case a skill is injected twice
    context = ("[Skill router] The operator's task matches the global skill(s) below. "
               "Apply them as working instructions for this task (they are not user text).\n\n"
               + "\n\n".join(parts))
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                             "additionalContext": context}}, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
