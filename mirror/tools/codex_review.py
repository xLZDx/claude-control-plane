"""
Wrapper for `codex exec` -- the Claude<->Codex consensus-review integration
(global rule, see ~/.claude/CLAUDE.md "Codex Consensus Review").

Codex is review-only here: this script never applies Codex's suggested fixes, it only
surfaces them as structured JSON for Claude to cross-check and fold into its own review.

Uses plain `codex exec` (not the built-in `codex exec review` subcommand) because that
subcommand's --uncommitted/--base/--commit scope flags cannot be combined with a custom
PROMPT, which is required for `--prompt`/`--title`. Scope is instead described in the
prompt text; Codex runs its own git commands to see it, same as it does under the
`review` subcommand.

Usage:
  python codex_review.py --cwd <repo_dir> --uncommitted [--prompt TEXT]
  python codex_review.py --cwd <repo_dir> --base main
  python codex_review.py --cwd <repo_dir> --commit <sha>

Prints one JSON object to stdout: {"summary": str, "findings": [...]} or
{"error": "...", "findings": []} on failure. Exit code 0 on a successful Codex run
(even if findings is empty), non-zero on a wrapper/CLI failure.

No parallel/fan-out mode (removed 2026-08-21, operator instruction): Codex is a single flat
reviewer having one sequential exchange with Claude -- not something that spawns concurrent
instances of itself, same as it must never spawn a Claude agent. An earlier `--parallel N` mode
that ran N concurrent `codex exec` calls over file-group chunks existed briefly and is gone;
see ~/.claude/CLAUDE.md "Codex Consensus Review" §13 for the rule.

Not a panel seat (removed 2026-08-21, operator instruction): an earlier `--extra-context-file`
flag fed Codex other reviewers' findings and asked it to answer AGREE/DISAGREE/REFINE against
them -- i.e. treated Codex as one more seat in an internal Claude review panel instead of an
independent second opinion. That flag and the prompt block it drove are gone. Codex now always
reviews the diff cold, on its own; Claude reconciles Codex's findings with its own view
afterward, one-on-one, never by handing Codex a panel's prior output to react to.

Usage-limit auto-final (2026-08-15): if Codex's own response is a plain-English quota message
("You've hit your usage limit... try again at <date>"), that's a fixed-date external wall, not a
transient failure worth another round in this session -- retrying just re-hits the same message.
The wrapper detects this text (in stdout/stderr/the response body, wherever it landed) and forces
the receipt's `final=True` on THIS call regardless of the `--final` flag the caller passed, so a
single round auto-concludes the consensus loop instead of getting recorded as an open round that
a later retry would just fail identically. `error` is normalized to `"usage_limit_exhausted"` and
the matched notice text (including the reset date, when present) is returned under
`usage_limit_notice` so the caller can report e.g. "Codex: skipped (usage limit, resets <date>)".
"""
import argparse
import json
import os
import re
import ssl
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone

RECEIPTS_DIR = r"D:\tmp\claude_codex_review_gate"
RECEIPTS_PATH = os.path.join(RECEIPTS_DIR, "receipts.jsonl")

# --- API backend -----------------------------------------------------------------
# The `cli` backend spends the ChatGPT subscription's Codex-agent quota, which is a fixed
# weekly wall. The `api` backend spends a pay-as-you-go API balance instead: no wall, just
# a per-call cost, and the operator caps it with a spending limit on their side.
API_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_API_MODEL = "gpt-5.6-terra"
API_KEY_FILE = os.path.join(os.path.expanduser("~"), ".claude", ".secrets", "openai_api_key")
# USD per 1M tokens (input, output), for reporting actual spend on each call. Prices drift --
# a model missing here just reports token counts without a dollar figure rather than lying.
API_PRICING = {
    "gpt-5.6-sol": (5.00, 30.00),
    "gpt-5.6-terra": (2.00, 12.00),
    "gpt-5.6-luna": (0.20, 1.20),
    "gpt-5.5": (5.00, 30.00),
    "gpt-5.4": (2.50, 15.00),
    "gpt-5.4-mini": (0.75, 4.50),
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4.1": (2.00, 8.00),
    "gpt-4.1-mini": (0.40, 1.60),
}
# Hard cap on how much diff text is shipped to the API. Codex CLI reads the repo itself, so
# it never needed this; the API sees only what we send, and an unbounded diff is both a
# context-limit failure and an unbounded bill.
MAX_DIFF_CHARS = 400_000


# Normalised reviewer outcome, written alongside the raw ok/error so downstream readers do not
# have to re-derive "did this actually run?" from an error STRING.
#
# Deliberately NOT PASS/FAIL. A receipt records whether the review RAN, not whether it approved
# anything: findings never reach this function. Writing PASS here would be exactly the substitution
# this field exists to prevent -- a reviewer that did not run must never read as a green one.
STATUS_RAN = "RAN"                                    # the call completed; findings are elsewhere
STATUS_RAN_DEGRADED = "RAN_DEGRADED"                  # reserved; unused since parallel mode was removed
STATUS_NOT_RUN_QUOTA = "NOT_RUN_QUOTA"                # provider refused: usage limit
STATUS_NOT_RUN_TOOL_UNAVAILABLE = "NOT_RUN_TOOL_UNAVAILABLE"
STATUS_NOT_RUN_AUTH = "NOT_RUN_AUTH"
STATUS_ERROR = "ERROR"                                # ran and broke, cause not classified


def classify_review_status(ok, error):
    """Map (ok, error) onto a normalised status. Never returns a green value for a call that
    did not reach the reviewer."""
    e = (error or "").lower()
    if "usage_limit" in e or "usage limit" in e or "quota" in e:
        return STATUS_NOT_RUN_QUOTA
    if any(s in e for s in ("unauthenticated", "unauthorized", "401", "not logged in", "auth")):
        return STATUS_NOT_RUN_AUTH
    if any(s in e for s in ("not found", "enoent", "cannot find", "no such file",
                            "is not recognized")):
        return STATUS_NOT_RUN_TOOL_UNAVAILABLE
    if not ok:
        return STATUS_ERROR
    return STATUS_RAN_DEGRADED if e else STATUS_RAN


def write_receipt(cwd, scope, ok, error, round_num, final):
    """Record that codex_review.py was invoked for `cwd`, regardless of outcome.

    codex_review_gate.py (PreToolUse hook) reads this file for TWO separate checks:
    - `git commit` requires ANY recent receipt for this repo (an attempt happened).
    - `git push` requires the most recent receipt to have final=True (the consensus
      loop for this gate actually CONCLUDED -- consensus reached, or the 3-round
      circuit breaker exhausted and unresolved items were surfaced to the operator).
      See ~/.claude/CLAUDE.md "Codex Consensus Review" -> "No push, no build, before
      Codex's FINAL round". Pass --final on the last invocation of a gate's
      consensus loop; omit it (default False) on every intermediate round.

    A fail-open error (Codex unreachable) still counts as an attempt/round -- only a
    missing/absent invocation blocks the commit, and only a non-final latest receipt
    blocks the push. Never raises -- a receipt-write failure must not break the
    actual review.
    """
    try:
        os.makedirs(RECEIPTS_DIR, exist_ok=True)
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cwd": os.path.abspath(cwd),
            "scope": scope,
            "round": round_num,
            "final": final,
            "ok": ok,
            "error": error,
            "review_status": classify_review_status(ok, error),
        }
        with open(RECEIPTS_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass


REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "severity": {"type": "string", "enum": ["BLOCKER", "MAJOR", "MINOR", "NIT"]},
                    "file": {"type": "string"},
                    "line": {"type": ["integer", "null"]},
                    "claim": {"type": "string"},
                    "suggested_fix": {"type": ["string", "null"]},
                },
                # OpenAI strict structured-output mode requires every key in
                # `properties` to also appear in `required` (nullability is how
                # a field is made "optional" instead) -- verified live: omitting
                # `line`/`suggested_fix` here fails with invalid_json_schema.
                "required": ["severity", "file", "line", "claim", "suggested_fix"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["summary", "findings"],
    "additionalProperties": False,
}


def build_instructions(scope_desc, custom_prompt, title):
    parts = []
    if title:
        parts.append(f"Review title: {title}")
    parts.append(
        "You are acting as an independent code reviewer (read-only -- you must not edit "
        "any files). " + scope_desc + " Use git yourself to inspect exactly what changed."
    )
    if custom_prompt:
        parts.append(custom_prompt)
    parts.append(
        "Report findings as BLOCKER/MAJOR/MINOR/NIT. Every finding must cite a real file "
        "and, where applicable, a line number. Do not invent code that is not actually "
        "present in the diff or repository. If there is nothing to flag, return an empty "
        "findings array rather than inventing filler."
    )
    parts.append(
        "Apply a devil's-advocate stance throughout: actively look for reasons this change "
        "is wrong, unsafe, incomplete, or will break something, rather than defaulting to "
        "approval. This does not license inventing problems that aren't real: every "
        "objection still needs the same real file/line evidence required above -- if after "
        "genuinely trying to find a problem there is none, say so plainly rather than "
        "manufacturing a NIT to seem thorough."
    )
    return "\n\n---\n\n".join(parts)


# Matches Codex's own quota-exhausted message, e.g. "You've hit your usage limit...
# try again at Aug 20th, 2026 5:32 PM". A fixed-date external wall, not a transient
# failure -- see the module docstring's "Usage-limit auto-final" note.
USAGE_LIMIT_RE = re.compile(
    r"you'?ve hit your usage limit[^\n]{0,160}|usage limit\b[^\n]{0,160}try again[^\n]{0,80}",
    re.IGNORECASE,
)


def _mark_if_usage_limit(result, *texts):
    """If any of `texts` contains Codex's own usage-limit message, tag `result` so the
    caller forces final=True on this receipt instead of leaving the round open for a
    retry that would just hit the same fixed-date wall again. Mutates and returns
    `result` either way (a no-op when nothing matches)."""
    for t in texts:
        if not t:
            continue
        m = USAGE_LIMIT_RE.search(t)
        if m:
            result["error"] = "usage_limit_exhausted"
            result["usage_limit_notice"] = m.group(0).strip()
            result["force_final"] = True
            break
    return result


def run_codex_once(cwd, model, timeout, instructions):
    """Run one `codex exec` call and return its parsed result dict."""
    with tempfile.TemporaryDirectory() as td:
        schema_path = os.path.join(td, "schema.json")
        out_path = os.path.join(td, "last_message.txt")
        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump(REVIEW_SCHEMA, f)

        cmd = [
            "codex", "exec",
            "-s", "read-only",
            "--skip-git-repo-check",
            "-C", cwd,
            "--output-schema", schema_path,
            "-o", out_path,
        ]
        if model:
            cmd += ["-m", model]
        cmd.append("-")  # read instructions from stdin

        try:
            proc = subprocess.run(
                cmd,
                input=instructions,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                shell=(os.name == "nt"),
            )
        except subprocess.TimeoutExpired:
            return {"error": "codex_timeout", "findings": []}
        except FileNotFoundError:
            return {"error": "codex_not_found", "findings": []}

        if proc.returncode != 0:
            result = {
                "error": "codex_exec_failed",
                "returncode": proc.returncode,
                "stderr": proc.stderr[-4000:],
                "stdout": proc.stdout[-2000:],
                "findings": [],
            }
            return _mark_if_usage_limit(result, proc.stderr, proc.stdout)

        if not os.path.exists(out_path):
            result = {
                "error": "no_output_file",
                "stdout": proc.stdout[-4000:],
                "findings": [],
            }
            return _mark_if_usage_limit(result, proc.stdout)

        with open(out_path, "r", encoding="utf-8") as f:
            last_message = f.read()

    try:
        return json.loads(last_message)
    except json.JSONDecodeError:
        result = {"error": "unparseable_output", "raw": last_message[:4000], "findings": []}
        return _mark_if_usage_limit(result, last_message)


def api_ssl_context():
    """Default TLS context, minus the one check Norton's interception breaks.

    This machine runs Norton, which MITMs TLS with a root whose Basic Constraints extension
    is not marked critical. Python 3.13+ enables VERIFY_X509_STRICT by default, which rejects
    exactly that -- observed live as
    `CERTIFICATE_VERIFY_FAILED: Basic Constraints of CA cert not marked critical`.
    Dropping ONLY that flag keeps chain, hostname and expiry verification fully on; it is not
    `verify=False`, and it is not a blanket "trust anything". Same conclusion as the standing
    note that cert errors on this host are AV interception, not a real network problem.
    """
    ctx = ssl.create_default_context()
    ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
    return ctx


def read_api_key():
    """Key from the environment, else the on-disk secrets file. None if neither exists."""
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if key:
        return key
    try:
        with open(API_KEY_FILE, "r", encoding="utf-8") as f:
            return f.read().strip() or None
    except OSError:
        return None


def collect_diff(cwd, scope_type, base, commit):
    """The actual diff text for this scope. The API has no repo access -- unlike Codex CLI,
    which runs its own git commands -- so whatever we fail to collect here is simply invisible
    to the reviewer. Returns (text, error_or_None)."""

    def run(args):
        try:
            done = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True,
                                  timeout=60, encoding="utf-8", errors="replace")
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as exc:
            return None, f"git_failed: {exc}"
        if done.returncode != 0:
            return None, f"git_failed: {done.stderr.strip()[:300]}"
        return done.stdout, None

    parts = []
    if scope_type == "uncommitted":
        staged, err = run(["diff", "--cached"])
        if err:
            return None, err
        if staged.strip():
            parts.append("=== STAGED (git diff --cached) ===\n" + staged)

        unstaged, err = run(["diff"])
        if err:
            return None, err
        if unstaged.strip():
            parts.append("=== UNSTAGED (git diff) ===\n" + unstaged)

        untracked, err = run(["ls-files", "--others", "--exclude-standard"])
        if err:
            return None, err
        names = [n for n in untracked.splitlines() if n.strip()]
        if names:
            listing = ["=== UNTRACKED FILES ===\n" + "\n".join(names)]
            for name in names[:40]:
                try:
                    with open(os.path.join(cwd, name), "r", encoding="utf-8",
                              errors="replace") as f:
                        body = f.read(40_000)
                    listing.append(f"--- new file: {name} ---\n{body}")
                except OSError:
                    continue
            parts.append("\n\n".join(listing))
    elif scope_type == "base":
        text, err = run(["diff", f"{base}...HEAD"])
        if err:
            return None, err
        parts.append(f"=== git diff {base}...HEAD ===\n" + text)
    else:
        text, err = run(["show", commit])
        if err:
            return None, err
        parts.append(f"=== git show {commit} ===\n" + text)

    joined = "\n\n".join(parts).strip()
    if not joined:
        return "", None
    if len(joined) > MAX_DIFF_CHARS:
        joined = (joined[:MAX_DIFF_CHARS]
                  + f"\n\n[TRUNCATED at {MAX_DIFF_CHARS} chars -- diff is larger than this "
                    "review can carry; findings below cover only the portion shown]")
    return joined, None


def api_cost(model, usage):
    """(usd, note). Returns (None, reason) when the model has no price on file."""
    prices = API_PRICING.get(model)
    if not prices:
        return None, f"no pricing on file for {model}"
    in_rate, out_rate = prices
    prompt = usage.get("prompt_tokens", 0)
    completion = usage.get("completion_tokens", 0)
    return (prompt * in_rate + completion * out_rate) / 1_000_000, None


def run_api_once(cwd, model, timeout, instructions, scope_type, base, commit):
    """One OpenAI API review call. Same return shape as run_codex_once()."""
    key = read_api_key()
    if not key:
        return {"error": "no_api_key", "findings": [],
                "detail": f"set OPENAI_API_KEY or write the key to {API_KEY_FILE}"}

    diff_text, err = collect_diff(cwd, scope_type, base, commit)
    if err:
        return {"error": "diff_collection_failed", "detail": err, "findings": []}
    if not diff_text:
        return {"summary": "No changes found in the requested scope; nothing to review.",
                "findings": []}

    payload = {
        "model": model,
        "messages": [
            {"role": "system",
             "content": "You are an independent, read-only code reviewer. You cannot edit "
                        "files or run commands -- you only report findings."},
            {"role": "user", "content": instructions + "\n\n---\n\nDIFF UNDER REVIEW:\n\n"
                                        + diff_text},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "review", "strict": True, "schema": REVIEW_SCHEMA},
        },
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, context=api_ssl_context(), timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:2000]
        # 429 covers both "out of money" and "too fast"; they need different operator action,
        # so keep them distinguishable rather than collapsing both into a rate-limit message.
        code = "api_insufficient_quota" if "insufficient_quota" in detail else (
            "api_rate_limited" if exc.code == 429 else f"api_http_{exc.code}")
        return {"error": code, "detail": detail, "findings": []}
    except (urllib.error.URLError, ssl.SSLError, TimeoutError) as exc:
        return {"error": "api_unreachable", "detail": f"{type(exc).__name__}: {exc}",
                "findings": []}

    try:
        content = body["choices"][0]["message"]["content"]
        result = json.loads(content)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        return {"error": "unparseable_output", "detail": str(exc),
                "raw": json.dumps(body)[:4000], "findings": []}

    usage = body.get("usage", {}) or {}
    result["usage"] = usage
    result["model"] = body.get("model", model)
    cost, why = api_cost(result["model"], usage)
    if cost is not None:
        result["cost_usd"] = round(cost, 4)
    elif why:
        result["cost_note"] = why
    return result


# --- Manual mode (added 2026-08-20, operator instruction) -----------------------------
# For the operator to drive a round by hand -- pasting into their own already-open ChatGPT
# tab and pasting the reply back -- without that becoming an unattended loop. This is NOT
# the default path for any of the 6 concurrently running gate sessions; `codex exec`
# (the `cli` backend, unchanged above) stays what they call automatically. This mode only
# runs when a human explicitly invokes it for one specific gate, and only produces a
# receipt once a human has actually pasted a real reply back in -- there is no automated
# send or automated fetch anywhere in this path. See ~/.claude/CLAUDE.md "Codex Consensus
# Review" §13 and the codex-consensus skill for why an automated bridge to the chat UI
# does not exist and will not: this is the accessibility-respecting alternative -- one
# hotkey/command per message, a human decides every send.


def clipboard_write(text):
    try:
        subprocess.run(["clip"], input=text.encode("utf-8"), check=True)
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def clipboard_read():
    try:
        # -Raw preserves newlines; without it PowerShell returns a line array.
        done = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Get-Clipboard -Raw"],
            capture_output=True, text=True, timeout=10,
        )
        return done.stdout if done.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def extract_json_object(text):
    """Best-effort {"summary","findings"} extraction from a human-pasted chat reply.

    A pasted ChatGPT answer is not guaranteed to be bare JSON -- it may carry a ```json
    fence, a sentence before/after, or stray whitespace. Take the widest {...} span and
    parse that, rather than requiring the paste to be exactly clean.
    """
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


def cmd_print_prompt(args, instructions):
    """Build the review prompt and put it on the clipboard for the operator to paste."""
    diff_text, err = collect_diff(args.cwd, args.scope_type, args.base, args.commit)
    if err:
        print(json.dumps({"error": "diff_collection_failed", "detail": err}))
        return 1
    if not diff_text:
        print(json.dumps({"summary": "No changes in scope -- nothing to send.", "findings": []}))
        return 0

    full_prompt = instructions + "\n\n---\n\nDIFF UNDER REVIEW:\n\n" + diff_text
    on_clipboard = clipboard_write(full_prompt)
    print(json.dumps({
        "mode": "print-prompt",
        "clipboard": on_clipboard,
        "chars": len(full_prompt),
        "next_step": (
            "Prompt is on the clipboard -- paste it into your ChatGPT tab and send. "
            "When the reply comes back, copy it, then run this same command with "
            "--ingest-response (same --cwd/--round/--final) to record the receipt."
            if on_clipboard else
            "Could not reach the clipboard (clip.exe unavailable) -- printing the prompt "
            "below instead; copy it manually."
        ),
        **({} if on_clipboard else {"prompt": full_prompt}),
    }, ensure_ascii=False))
    return 0


def cmd_ingest_response(args):
    """Read the operator's pasted reply (clipboard, or --response-file) and write a receipt.

    This is the only place in manual mode a receipt gets written -- and only once real
    pasted text is in hand, so codex_review_gate.py cannot be satisfied by print-prompt
    alone (that would be indistinguishable from "asked, never got an answer").
    """
    if args.response_file:
        try:
            with open(args.response_file, "r", encoding="utf-8") as f:
                raw = f.read()
        except OSError as exc:
            print(json.dumps({"error": "response_file_unreadable", "detail": str(exc)}))
            return 1
    else:
        raw = clipboard_read()
        if raw is None:
            print(json.dumps({"error": "clipboard_unreadable",
                              "detail": "Get-Clipboard failed; pass --response-file instead"}))
            return 1
        if not raw.strip():
            print(json.dumps({"error": "clipboard_empty",
                              "detail": "Nothing on the clipboard -- copy the reply first"}))
            return 1

    parsed = extract_json_object(raw)
    if parsed is None:
        print(json.dumps({"error": "unparseable_response", "raw": raw[:4000]}))
        write_receipt(args.cwd, args.scope_str, ok=False, error="unparseable_response",
                      round_num=args.round_num, final=args.final)
        return 1

    write_receipt(args.cwd, args.scope_str, ok=True, error=None,
                  round_num=args.round_num, final=args.final)
    print(json.dumps(parsed, ensure_ascii=False))
    return 0


def main():
    ap = argparse.ArgumentParser()
    scope = ap.add_mutually_exclusive_group(required=True)
    scope.add_argument("--uncommitted", action="store_true", help="Review staged+unstaged+untracked changes")
    scope.add_argument("--base", help="Review current tree against this base branch")
    scope.add_argument("--commit", help="Review the changes introduced by this commit SHA")
    ap.add_argument("--cwd", default=".", help="Repo working directory")
    ap.add_argument("--title", help="Optional title included in the prompt for context")
    ap.add_argument("--prompt", help="Additional custom review instructions")
    ap.add_argument("--model", help="Override the Codex model")
    ap.add_argument("--timeout", type=int, default=3000)
    ap.add_argument("--round", type=int, default=1, dest="round_num",
                     help="Which round of the consensus loop this call represents (default 1)")
    ap.add_argument("--final", action="store_true",
                     help="Mark this as the LAST round of the gate's consensus loop -- "
                          "consensus reached, or the 3-round circuit breaker exhausted and "
                          "unresolved items surfaced to the operator. codex_review_gate.py "
                          "requires this before allowing `git push` for this repo.")
    manual = ap.add_mutually_exclusive_group()
    manual.add_argument("--print-prompt", action="store_true",
                         help="Manual mode, step 1: put the review prompt on the clipboard "
                              "for the operator to paste into their own chat tab. Writes no "
                              "receipt. One human-triggered command, one message -- not a loop.")
    manual.add_argument("--ingest-response", action="store_true",
                         help="Manual mode, step 2: read the operator's pasted reply (from "
                              "the clipboard, or --response-file) and write the receipt.")
    ap.add_argument("--response-file", help="With --ingest-response: read the reply from this "
                                            "file instead of the clipboard.")
    args = ap.parse_args()

    if args.uncommitted:
        scope_desc = (
            "Review the repository's current uncommitted changes -- staged, unstaged, "
            "and untracked files (`git status`, `git diff`, `git diff --cached`)."
        )
        scope_str = "uncommitted"
        scope_type = "uncommitted"
    elif args.base:
        scope_desc = (
            f"Review the changes on the current branch relative to base branch "
            f"'{args.base}' (`git diff {args.base}...HEAD`)."
        )
        scope_str = f"base:{args.base}"
        scope_type = "base"
    else:
        scope_desc = f"Review the changes introduced by commit {args.commit} (`git show {args.commit}`)."
        scope_str = f"commit:{args.commit}"
        scope_type = "commit"
    args.scope_str, args.scope_type = scope_str, scope_type

    if args.print_prompt:
        instructions = build_instructions(scope_desc, args.prompt, args.title)
        return cmd_print_prompt(args, instructions)
    if args.ingest_response:
        return cmd_ingest_response(args)

    instructions = build_instructions(scope_desc, args.prompt, args.title)
    result = run_codex_once(args.cwd, args.model, args.timeout, instructions)
    write_receipt(args.cwd, scope_str, ok=("error" not in result), error=result.get("error"),
                  round_num=args.round_num, final=(args.final or bool(result.get("force_final"))))
    print(json.dumps(result))
    return 0 if "error" not in result else 1


if __name__ == "__main__":
    sys.exit(main())
