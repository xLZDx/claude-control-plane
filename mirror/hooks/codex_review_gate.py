#!/usr/bin/env python3
"""PreToolUse hook -- two independent checks, both via Bash/PowerShell. Operator
GO, 2026-08-14 (commit check) + 2026-08-14 (push check, same day, added same-turn
per operator: "сделай это сразу" rather than waiting for a 4th recurrence).

  1. `git commit` is blocked unless codex_review.py has been invoked (ANY
     receipt, any round/final status) for this repo recently -- proves Codex
     was at least ATTEMPTED for this gate.
  2. `git push` is blocked unless the MOST RECENT receipt for this repo has
     final=True -- proves the gate's Codex consensus loop actually CONCLUDED
     (consensus reached, or the 3-round circuit breaker exhausted with
     unresolved items surfaced to the operator), not just attempted once.
     See ~/.claude/CLAUDE.md "Codex Consensus Review" -> "No push, no build,
     before Codex's FINAL round".

Why this exists (see ~/.claude/CLAUDE.md "Codex Consensus Review"): the rule
is text-only MANDATORY guidance to send every gate's diff to Codex before
committing, and to wait for the FINAL round before pushing/building. The
commit half was proven live to get skipped on 3 consecutive gates/commits in
a row without anyone noticing -- not a deliberate skip, just never invoked.
This mirrors the exact failure mode that "Continuous Decision/Evidence/
Refusal Log Per Project" hit before decision_log_gate.py existed, and gets
the same fix: a mechanical PreToolUse gate, not another paragraph of text.
The push half is added proactively, before it has (yet) been observed
skipped in practice, on the operator's explicit instruction rather than
waiting for a third recurrence of the same failure shape.

What the commit check verifies is ATTEMPT, not SUCCESS. codex_review.py
writes a receipt line to RECEIPTS_FILE on every run, including its own
fail-open error paths (Codex unreachable/timeout/unauthenticated). A receipt
with ok=false still satisfies the commit gate -- the "Codex Consensus
Review" rule's own fail-open policy (never block a gate on Codex being
unavailable) is preserved there. Only a MISSING receipt -- Codex never even
attempted -- blocks the commit.

What the push check verifies is CONCLUSION, not just attempt: the LATEST
receipt for the repo must carry final=True (set via codex_review.py's
--final flag on the last round of that gate's consensus loop). A non-final
latest receipt (intermediate round, loop still open) blocks the push even
though it would satisfy the commit check.

Fixed 2026-08-15 (operator report: "хук проверяет только поле final и
возраст квитанции -- поля ok/error он не смотрит"): a final=True receipt
whose own ok=False (Codex never actually succeeded that round -- unreachable/
timeout/all-chunks-failed -- and the round was marked --final anyway per the
documented fail-open escape hatch, see codex-consensus/SKILL.md "Mark the
FINAL round") still ALLOWS the push, same as before -- that escape hatch is
intentional and this fix does not remove it. What changes: that allow is no
longer silent. It now emits an explicit permissionDecision:"allow" with a
reason stating plainly that the final round did not actually succeed, so the
gap between "loop concluded" and "Codex actually reviewed anything" isn't
lost the way a bare exit(0) would lose it. Operator chose this option
explicitly over the two stricter alternatives (block on ok=false; block only
on wrapper-side errors) -- fail-open behavior for push stays unchanged.

No trivial-commit carve-out is built into either check, deliberately
mirroring decision_log_gate.py's own design: that hook has none either,
despite its governing rule also naming a trivial-change exception. Judging
"is this commit T1-trivial" is a semantic call this hook cannot make
reliably, and a gameable skip mechanism would defeat the point. Calling
codex_review.py once even for a small commit is cheap; forgetting it
entirely is the failure mode this hook exists to close.

Scope, honestly:
- Catches git commit/push invoked through Claude Code's Bash/PowerShell
  tools. Does NOT catch commits/pushes made outside Claude Code, nor git
  merge / rebase --continue / cherry-pick (no literal "git commit" in the
  command), nor a command that `cd`s into another directory first in a way
  this hook's regex-based resolver misparses.
- A compound command containing both `git commit` and `git push` (e.g.
  `git commit -m x && git push`) is held to the STRICTER push requirement
  (final receipt) for the whole command -- satisfying "final" automatically
  satisfies "attempted", so this is never a stricter ask than necessary.
- Fails open on any internal error (git missing, timeout, bad stdin,
  unreadable receipts file) -- logged, never silent, never crashes the
  session.

Kill switch: CLAUDE_CODEX_REVIEW_GATE=off -- like decision_log_gate.py's own
kill switch, this is a SESSION/PROCESS-level env var. It must be set before
this Claude Code process starts; setting it inline in the Bash/PowerShell
command being gated has no effect, because this hook runs as its own
separate process that already decided before that command ever executes.
Covers both checks.

Decision log: D:\\tmp\\claude_codex_review_gate\\decisions.jsonl
Receipts read from: D:\\tmp\\claude_codex_review_gate\\receipts.jsonl
  (written by C:\\Users\\koros\\.claude\\tools\\codex_review.py)
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path(r"D:\tmp\claude_codex_review_gate")
DECISIONS_FILE = STATE_DIR / "decisions.jsonl"
RECEIPTS_FILE = STATE_DIR / "receipts.jsonl"
RECEIPT_MAX_AGE_HOURS = 6
# Push often happens well after the commit (separate push-GO, per Gate-Based
# Development) -- a longer window than the commit check's, so a same-gate
# push hours later doesn't spuriously re-trigger.
PUSH_RECEIPT_MAX_AGE_HOURS = 24

# A quota-exhausted receipt gets auto-marked final=True by codex_review.py so the loop
# doesn't spin forever against a fixed-date wall (see its "Usage-limit auto-final" note) --
# but that means it would otherwise satisfy this gate for the SAME 6h/24h window as a real
# review, silently covering hours of subsequent commits/pushes with zero further Codex
# attempts even once the quota has actually reset. Confirmed live 2026-08-20: an ERP gate's
# 12+ commits/pushes over 3+ hours all rode one stale quota receipt, while a direct probe
# showed the quota had already recovered partway through. A quota receipt gets a much
# shorter validity window instead, so the very next commit/push after this elapses forces a
# real retry -- see ~/.claude/CLAUDE.md "Codex Consensus Review" §13.
QUOTA_RECEIPT_MAX_AGE_HOURS = 0.5

COMMIT_RE = re.compile(r"\bgit\s+commit\b", re.IGNORECASE)
PUSH_RE = re.compile(r"\bgit\s+push\b", re.IGNORECASE)
SKIP_RE = re.compile(r"--help\b|(?<!\S)-h\b|--dry-run\b", re.IGNORECASE)
CD_RE = re.compile(r'^\s*cd\s+(?P<path>"[^"]+"|\'[^\']+\'|\S+)\s*$')

# Git-Bash spells drives as `/d/Repo/x`. Windows Python does NOT read that as absolute --
# `os.path.isabs('/d/Repo/x')` is False here -- so the old resolver fell through to
# `Path(base_cwd) / path`, and pathlib treats a rooted-but-driveless right-hand side by keeping
# the LEFT side's drive: `Path('D:/Repo') / '/d/Repo/x'` -> `D:\d\Repo\x`. That directory does not
# exist, `git rev-parse` failed, and both gates fail-opened -- silently, on every command issued
# through the Bash tool with a POSIX path.
#
# Measured 2026-08-16 before the fix: 20 fail-opens for `D:\d\Repo\db-test-tool-analysis` in this
# hook's own decisions log and 13 in decision_log_gate.py's, plus the same shape for other repos.
# A gate that never runs is worse than no gate: it reports nothing while looking enforced.
_GITBASH_DRIVE_RE = re.compile(r"^/([A-Za-z])(?=/|$)")


def normalise_shell_path(path):
    """`/d/Repo/x` -> `D:\\Repo\\x`; everything else unchanged."""
    m = _GITBASH_DRIVE_RE.match(path)
    if not m:
        return path
    rest = path[2:].replace("/", "\\")
    return f"{m.group(1).upper()}:{rest or chr(92)}"


def resolve_effective_cwd(command, base_cwd):
    """Same approach as decision_log_gate.py: the hook's reported `cwd` is the
    session's static working directory, not any `cd <dir> && ...` prefix
    inside the command itself. Walk &&/;-joined parts and apply `cd` segments."""
    cwd = base_cwd
    for part in re.split(r"&&|;", command):
        m = CD_RE.match(part.strip())
        if not m:
            continue
        path = normalise_shell_path(m.group("path").strip("\"'"))
        if os.path.isabs(path) or re.match(r"^[A-Za-z]:", path) or path.startswith(("/", "\\")):
            cwd = path
        else:
            cwd = str(Path(cwd) / path)
    return cwd


def log_decision(entry):
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        entry["ts"] = datetime.now(timezone.utc).isoformat()
        with open(DECISIONS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def allow():
    sys.exit(0)


def deny(reason, extra=None):
    log_decision({"decision": "deny", "reason": reason, **(extra or {})})
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0


def git(args, cwd=None, timeout=10):
    return subprocess.run(
        ["git"] + (["-C", cwd] if cwd else []) + args,
        capture_output=True, text=True, timeout=timeout,
        creationflags=_NO_WINDOW,
    )


def is_under(path, root):
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
        return True
    except ValueError:
        return str(Path(path).resolve()) == str(Path(root).resolve())


def is_quota_receipt(entry):
    """True if this receipt records a Codex usage-limit refusal, not an actual review."""
    if entry.get("review_status") == "NOT_RUN_QUOTA":
        return True
    error = (entry.get("error") or "")
    return "usage_limit" in error.lower()


def recent_receipt_exists(repo_root):
    if not RECEIPTS_FILE.is_file():
        return False
    now = datetime.now(timezone.utc)
    try:
        with open(RECEIPTS_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return False
    for line in reversed(lines[-500:]):  # newest-last file, cap scan for cheapness
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts_raw = entry.get("timestamp")
        cwd = entry.get("cwd")
        if not ts_raw or not cwd:
            continue
        try:
            ts = datetime.fromisoformat(ts_raw)
        except ValueError:
            continue
        max_age = QUOTA_RECEIPT_MAX_AGE_HOURS if is_quota_receipt(entry) else RECEIPT_MAX_AGE_HOURS
        age_hours = (now - ts).total_seconds() / 3600.0
        if age_hours > max_age:
            continue
        if is_under(cwd, repo_root):
            return True
    return False


def latest_receipt_for_repo(repo_root):
    """Return the most recent receipt dict for this repo (any age), or None.

    "Most recent" is determined by file position (receipts.jsonl is append-only,
    so later lines are later in time), not by re-parsing every timestamp --
    cheaper and avoids a subtle bug where an out-of-order clock could pick the
    wrong entry.
    """
    if not RECEIPTS_FILE.is_file():
        return None
    try:
        with open(RECEIPTS_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return None
    for line in reversed(lines[-500:]):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        cwd = entry.get("cwd")
        if not cwd:
            continue
        if is_under(cwd, repo_root):
            return entry
    return None


def final_receipt_fresh(repo_root):
    """True iff the MOST RECENT receipt for this repo has final=True and is
    within PUSH_RECEIPT_MAX_AGE_HOURS. Returns (passes, reason_if_not_ok, entry).

    `entry` is the matching receipt dict whenever one was found -- returned
    even when `passes` is False, and always returned when it's True -- so the
    caller can inspect ok/error (e.g. to warn on an allowed fail-open push)
    without a second scan of receipts.jsonl.
    """
    entry = latest_receipt_for_repo(repo_root)
    if not entry:
        return False, "no codex_review.py receipt found at all", None
    if not entry.get("final"):
        return False, f"latest receipt is round {entry.get('round', '?')} (not marked --final) -- the consensus loop hasn't concluded yet", entry
    ts_raw = entry.get("timestamp")
    if not ts_raw:
        return False, "latest final receipt has no timestamp", entry
    try:
        ts = datetime.fromisoformat(ts_raw)
    except ValueError:
        return False, "latest final receipt has an unparseable timestamp", entry
    max_age = QUOTA_RECEIPT_MAX_AGE_HOURS if is_quota_receipt(entry) else PUSH_RECEIPT_MAX_AGE_HOURS
    age_hours = (datetime.now(timezone.utc) - ts).total_seconds() / 3600.0
    if age_hours > max_age:
        return False, f"latest final receipt is {age_hours:.1f}h old (> {max_age}h{' -- quota receipts get a short window so a real retry happens once the quota may have reset' if is_quota_receipt(entry) else ''}) -- treat as stale, re-run the review", entry
    return True, None, entry


def main():
    if os.environ.get("CLAUDE_CODEX_REVIEW_GATE", "").lower() == "off":
        allow()

    try:
        payload = json.loads(sys.stdin.read())
    except Exception as e:
        log_decision({"decision": "fail-open", "reason": f"bad stdin: {e}"})
        allow()

    command = (payload.get("tool_input") or {}).get("command", "") or ""
    if SKIP_RE.search(command):
        allow()

    is_push = bool(PUSH_RE.search(command))
    is_commit = bool(COMMIT_RE.search(command))
    if not is_push and not is_commit:
        allow()

    raw_cwd = payload.get("cwd") or os.getcwd()
    cwd = resolve_effective_cwd(command, raw_cwd)

    try:
        toplevel = git(["rev-parse", "--show-toplevel"], cwd=cwd)
        if toplevel.returncode != 0:
            log_decision({"decision": "fail-open", "reason": "not a git repo or git error",
                          "cwd": cwd, "stderr": toplevel.stderr.strip()[:300]})
            allow()
        repo_root = toplevel.stdout.strip()
    except Exception as e:
        log_decision({"decision": "fail-open", "reason": f"git rev-parse failed: {e}", "cwd": cwd})
        allow()

    # Push is checked first and is STRICTER than commit -- a compound command
    # containing both (`git commit -m x && git push`) is held to the push
    # requirement for the whole command, since satisfying "final" automatically
    # satisfies "attempted".
    if is_push:
        try:
            passes, why, entry = final_receipt_fresh(repo_root)
        except Exception as e:
            log_decision({"decision": "fail-open", "reason": f"receipt scan failed: {e}", "repo": repo_root})
            allow()

        if passes:
            receipt_ok = entry.get("ok") if entry else None
            receipt_error = entry.get("error") if entry else None
            if receipt_ok is False:
                # Final round exists and is fresh, but codex_review.py's own call
                # never actually succeeded (Codex unreachable/timeout/all-chunks-
                # failed/etc.) -- it was marked --final anyway per the documented
                # fail-open escape hatch (codex-consensus/SKILL.md "Mark the FINAL
                # round"). Push still proceeds -- that escape hatch is intentional
                # -- but this must not look like a silent, clean allow: surface it
                # via an explicit permissionDecision so the gap between "loop
                # concluded" and "Codex actually reviewed anything" isn't lost.
                warn_reason = (
                    f"CODEX REVIEW gate (push): ALLOWING per fail-open policy, but the latest "
                    f"final receipt for {repo_root} has ok=false (error={receipt_error!r}) -- "
                    f"the last Codex round did NOT actually succeed; it was marked --final to "
                    f"unblock this push per ~/.claude/CLAUDE.md 'Codex Consensus Review' -> "
                    f"'Mark the FINAL round'. This gate may be shipping without a real Codex "
                    f"review. State this plainly in the Codex: line of the stop-and-report "
                    f"(e.g. 'Codex: skipped (<error>), push allowed fail-open') -- do not report "
                    f"it as a clean/consensus review."
                )
                log_decision({"decision": "allow-with-warning", "reason": warn_reason,
                              "repo": repo_root, "command": command[:200],
                              "receipt_ok": receipt_ok, "receipt_error": receipt_error})
                print(json.dumps({
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "allow",
                        "permissionDecisionReason": warn_reason,
                    }
                }))
                sys.exit(0)

            log_decision({"decision": "allow", "reason": "final codex_review.py receipt found (ok)",
                          "repo": repo_root, "command": command[:200]})
            allow()

        reason = (
            f"CODEX REVIEW gate (push): {why} -- repo {repo_root}. Per ~/.claude/CLAUDE.md "
            f"'Codex Consensus Review' -> 'No push, no build, before Codex's FINAL round': push "
            f"waits for this gate's Codex consensus loop to CONCLUDE (consensus reached, or the "
            f"3-round circuit breaker exhausted with unresolved items surfaced to the operator) -- "
            f"not just an attempted round. Continue the codex-consensus loop, then invoke "
            f"`codex_review.py --final` on its last round for this repo, then retry this push. "
            f"CLAUDE_CODEX_REVIEW_GATE=off is a session/process-level kill switch, NOT a per-command "
            f"one: it must be set in the environment BEFORE this Claude Code session/process starts. "
            f"Setting it inline in this Bash/PowerShell command has no effect -- this hook runs as "
            f"its own process and has already decided before that command ever executes."
        )
        deny(reason, {"repo": repo_root, "command": command[:200], "why": why})

    # is_commit only from here on (is_push already returned/exited above).
    try:
        found = recent_receipt_exists(repo_root)
    except Exception as e:
        log_decision({"decision": "fail-open", "reason": f"receipt scan failed: {e}", "repo": repo_root})
        allow()

    if found:
        log_decision({"decision": "allow", "reason": "recent codex_review.py receipt found",
                      "repo": repo_root, "command": command[:200]})
        allow()

    reason = (
        f"CODEX REVIEW gate (commit): no codex_review.py receipt found for {repo_root} in the last "
        f"{RECEIPT_MAX_AGE_HOURS}h. Per ~/.claude/CLAUDE.md 'Codex Consensus Review' (MANDATORY, "
        f"2026-08-14): send this gate's diff to Codex before committing -- run "
        f"`C:\\Python314\\python.exe C:\\Users\\koros\\.claude\\tools\\codex_review.py --cwd {repo_root} "
        f"--uncommitted` (or the codex-consensus skill), then retry this commit. A fail-open error "
        f"from Codex (unreachable/timeout) still writes a receipt and satisfies this gate -- only a "
        f"call that was never attempted blocks it. CLAUDE_CODEX_REVIEW_GATE=off is a session/process-"
        f"level kill switch, NOT a per-command one: it must be set in the environment BEFORE this "
        f"Claude Code session/process starts. Setting it inline in this Bash/PowerShell command has "
        f"no effect -- this hook runs as its own process and has already decided before that command "
        f"ever executes."
    )
    deny(reason, {"repo": repo_root, "command": command[:200]})


if __name__ == "__main__":
    main()
