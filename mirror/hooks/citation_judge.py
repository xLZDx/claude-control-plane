#!/usr/bin/env python3
"""Citation judge -- Claude Code SubagentStop hook (gate 'llm-judge').

evidence_gate.py checks that citations EXIST. This checks that they SAY what the
agent claims they say: it reads the cited lines and asks a small model whether the
code actually supports the claim, blocking on an outright contradiction.

SubagentStop only, on purpose: it costs a model call and ~15-40s, which is fine
for an audit or review report but not for every conversational turn.

Cost control -- the judge exits before spending anything unless the message has at
least one citation that resolves to a real file AND names a line.

Kill switches: CLAUDE_CITATION_JUDGE=off, or CLAUDE_EVIDENCE_GATE=off (both gates).
Recursion guard: the child `claude -p` runs with both switches off, otherwise its
own SubagentStop/Stop hooks would spawn another judge, forever.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import time
import traceback
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parent
STATE_DIR = Path(r"D:\tmp\claude_evidence_gate")
LOG_PATH = STATE_DIR / "decisions.jsonl"
CLAUDE_CMD = r"D:\npm-global\claude.cmd"
MODEL = "claude-haiku-4-5-20251001"

MAX_CITES = 6          # bound prompt size and latency
CONTEXT_LINES = 6      # lines of code shown either side of the cited line
MAX_CLAIM_CHARS = 4000
CALL_TIMEOUT = 90      # seconds for the child claude call

PROMPT = """You are verifying citations in an engineering report. For each citation \
below you get the exact source lines it points at. Decide whether those lines actually \
support what the report says about them.

Verdicts:
  supports    - the cited lines back the claim
  unrelated   - the lines are real but say nothing about the claim
  contradicts - the lines state something incompatible with the claim

Be conservative: answer "supports" unless you are confident. Judge ONLY the claim-to-code \
match, never code quality.

Reply with a JSON array and nothing else:
[{{"id": 1, "verdict": "supports", "why": "one short sentence"}}]

=== REPORT ===
{claim}

=== CITATIONS ===
{snippets}
"""


def load_gate():
    spec = importlib.util.spec_from_file_location("eg", HOOKS_DIR / "evidence_gate.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def log(record: dict) -> None:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


def already_fired(key: str) -> bool:
    marker = STATE_DIR / f"judge_{key}.fired"
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        if marker.exists():
            return True
        marker.write_text(str(time.time()), encoding="utf-8")
    except OSError:
        return False
    return False


def build_snippets(gate, message: str, cwd: Path) -> list[dict]:
    """Resolve citations to (path, line, source window). Empty list => nothing to judge."""
    out = []
    for c in gate.extract(message):
        if c["line"] is None:
            continue
        resolved, whole = gate.resolve(c["path"], cwd)
        if resolved is None or not whole:
            continue
        try:
            lines = resolved.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        n = c["line"]
        if n > len(lines):
            continue                       # evidence_gate R3 already blocks this
        lo, hi = max(1, n - CONTEXT_LINES), min(len(lines), n + CONTEXT_LINES)
        window = "\n".join(
            f"{i:>6}{'>' if i == n else ' '} {lines[i - 1]}" for i in range(lo, hi + 1)
        )
        out.append({"id": len(out) + 1, "raw": c["raw"], "path": str(resolved),
                    "line": n, "window": window})
        if len(out) >= MAX_CITES:
            break
    return out


def ask_judge(claim: str, snippets: list[dict]) -> list[dict] | None:
    blocks = "\n\n".join(
        f"[{s['id']}] cited as: {s['raw']}\n{s['path']} around line {s['line']}:\n{s['window']}"
        for s in snippets
    )
    prompt = PROMPT.format(claim=claim[:MAX_CLAIM_CHARS], snippets=blocks)

    env = dict(os.environ)
    env["CLAUDE_EVIDENCE_GATE"] = "off"      # child must not re-enter either gate
    env["CLAUDE_CITATION_JUDGE"] = "off"

    proc = subprocess.run(
        ["cmd", "/c", CLAUDE_CMD, "-p", "--model", MODEL,
         "--disallowed-tools", "Read", "Write", "Edit", "Bash", "Glob", "Grep",
         "WebFetch", "WebSearch", "Agent"],
        input=prompt, capture_output=True, text=True, encoding="utf-8",
        errors="replace", env=env, timeout=CALL_TIMEOUT,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    raw = (proc.stdout or "").strip()
    m = re.search(r"\[.*\]", raw, re.DOTALL)      # tolerate ```json fences / preamble
    if not m:
        return None
    try:
        parsed = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, list) else None


REASON = (
    "CITATION JUDGE -- {n} citation(s) do not say what you claim:\n{items}\n\n"
    "~/.claude/CLAUDE.md \"Empiricism over Poetry\", step 2: verify that the cited line "
    "actually does what you say it does; a citation whose content contradicts the claim "
    "is a confabulation and must be labelled, not passed on.\n\n"
    "Re-read those lines, then correct the claim or the citation and answer again."
)


def evaluate(gate, data: dict) -> tuple[str | None, dict]:
    message = data.get("last_assistant_message") or ""
    if not message.strip():
        return None, {"judge": "empty"}

    cwd = Path(data.get("cwd") or os.getcwd())
    snippets = build_snippets(gate, message, cwd)
    if not snippets:
        return None, {"judge": "no-verifiable-citations"}      # free path, no model call

    verdicts = ask_judge(message, snippets)
    if verdicts is None:
        return None, {"judge": "call-failed", "checked": len(snippets)}

    by_id = {s["id"]: s for s in snippets}
    bad, unrelated = [], []
    for v in verdicts:
        s = by_id.get(v.get("id"))
        if not s:
            continue
        verdict = str(v.get("verdict", "")).lower()
        entry = f"{s['raw']} -- {v.get('why', '(no reason given)')}"
        if verdict == "contradicts":
            bad.append(entry)
        elif verdict == "unrelated":
            unrelated.append(entry)

    detail = {"judge": "ran", "checked": len(snippets),
              "contradicts": bad, "unrelated": unrelated}

    # Block only on outright contradiction. "unrelated" is logged, not enforced:
    # it is the verdict a judge most often gets wrong, and a false block costs a
    # whole turn. Revisit once the log shows how often it would have been right.
    if bad:
        return REASON.format(n=len(bad), items="\n".join(f"  - {b}" for b in bad)), detail
    return None, detail


def main() -> int:
    if os.environ.get("CLAUDE_CITATION_JUDGE", "").lower() in {"off", "0", "false"}:
        return 0
    if os.environ.get("CLAUDE_EVIDENCE_GATE", "").lower() in {"off", "0", "false"}:
        return 0

    raw = sys.stdin.read()
    data = json.loads(raw) if raw.strip() else {}

    if data.get("hook_event_name") != "SubagentStop":
        return 0

    reason, detail = evaluate(load_gate(), data)

    record = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "event": "CitationJudge",
        "agent_type": data.get("agent_type"),
        "session_id": data.get("session_id"),
        "prompt_id": data.get("prompt_id"),
        "verdict": "block" if reason else "pass",
        "excerpt": (data.get("last_assistant_message") or "")[:300],
        **detail,
    }

    if not reason:
        log(record)
        return 0

    key = re.sub(r"[^A-Za-z0-9_.-]", "_", "-".join([
        str(data.get("session_id", "nosess")),
        str(data.get("prompt_id", "noprompt")),
        str(data.get("agent_id", "noagent")),
    ]))
    if already_fired(key):
        record["verdict"] = "pass-guard"
        log(record)
        return 0

    log(record)
    sys.stdout.write(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    try:
        sys.exit(main())
    except Exception:
        log({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "event": "CitationJudge",
             "verdict": "hook-error", "traceback": traceback.format_exc()})
        sys.stderr.write("citation_judge: internal error, see the decision log\n")
        sys.exit(0)
