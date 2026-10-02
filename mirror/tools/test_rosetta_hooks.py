#!/usr/bin/env python3
"""Rosetta R0 -- the enforcement half (hooks/_rosetta_common.py, rosetta_audit.py, rosetta_due.py).

The shell classifier carries almost all of the risk in this half, so most of this file is spent on
it. Its contract is deliberately lopsided: a command counts as read-only only if EVERY segment has
a recognised read-only head and the whole command is free of redirection, substitution and
heredocs. A false "mutation" costs one spool record nobody reads; a false "read-only" is a hole
straight through the protocol -- so the tests below assert the asymmetry, not just the happy path,
and include the known false positives so that nobody later "fixes" one into a hole.

Run: py -3 C:/Users/koros/.claude/tools/test_rosetta_hooks.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HOOKS = Path(r"C:\Users\koros\.claude\hooks")
sys.path.insert(0, str(HOOKS))

failures = 0


def check(label, condition, detail=""):
    global failures
    if condition:
        print(f"  PASS  {label}")
    else:
        failures += 1
        print(f"  FAIL  {label}{f' -- {detail}' if detail else ''}")


# The module reads PM_BRIDGE_STATE_DIR at call time, not import time, so a temp dir set here
# covers every call below. This machine runs concurrent sessions against the real state
# directory; a test that wrote there would corrupt a live session's plan.
STATE = Path(tempfile.mkdtemp(prefix="rosetta-hooks-"))
os.environ["PM_BRIDGE_STATE_DIR"] = str(STATE)
os.environ.pop("CLAUDE_ROSETTA_GATE", None)

import _rosetta_common as rc  # noqa: E402


# --- 1. Shell classification: things that must be recognised as read-only -------------------
print("shell classifier: inspection stays free")
READ_ONLY = [
    "cat file.txt",
    "head -20 file.txt",
    "tail -n 50 file.txt",
    "sed -n '1,80p' file.txt",
    "grep -n pattern file.txt",
    "rg --files-with-matches pattern",
    "ls -la",
    "wc -l file.txt",
    "find . -name '*.py'",
    "git status -sb",
    "git log --oneline -5",
    "git diff --name-only",
    "git rev-parse HEAD",
    "git show HEAD:file.txt",
    "git ls-files",
    "git branch -a",
    "git tag",
    "git remote -v",
    "git config --get user.name",
    "git worktree list",
    "git -C D:/Repo/pm-bridge status",
    "git -C D:/Repo/pm-bridge log --oneline -3",
    "cat a.txt | grep x | wc -l",
    "ls && git status",
    "env",
    "pwd",
    # `cd` changes the shell's own directory and nothing else. Without it, nearly every Bash call
    # in this workspace -- they almost all open `cd "D:/Repo/<project>" && ...` -- was recorded as
    # a mutation, which is not a hole but does drown the signal. Found by reading the first
    # production spool, not by review.
    "cd /d/Repo/pm-bridge",
    'cd "D:/Repo/pm-bridge" && git status -sb',
    'cd "D:/Repo/pm-bridge" && grep -n pattern src/rosetta.js',
]
for command in READ_ONLY:
    ok, reason = rc.classify_shell(command)
    check(f"read-only: {command}", ok is True, reason)

# --- 2. Things that must be recognised as mutations ------------------------------------------
print("\nshell classifier: everything else is a mutation")
MUTATIONS = [
    ("echo hi > file.txt", "redirection"),
    ("echo hi >> file.txt", "append redirection"),
    ("cat a.txt | tee b.txt", "tee is not an allowlisted head"),
    ("python -c \"open('x','w').write('y')\"", "an inline interpreter writes as easily as it prints"),
    ("py -3 script.py", "a script does anything"),
    ("node build.js", "same"),
    ("sed -i 's/a/b/' file.txt", "in-place edit"),
    ("sed 's/a/b/' file.txt", "a plain sed is not the read-only form"),
    ("rm -rf build", "deletion"),
    ("mkdir -p out", "creation"),
    ("cp a b", "copy"),
    ("mv a b", "move"),
    ("touch f", "not allowlisted"),
    ("git commit -m 'x'", "commit"),
    ("git checkout -- file.txt", "discards work"),
    ("git add -A", "stages"),
    ("git stash", "moves work"),
    ("git reset --hard", "destroys work"),
    ("git config user.name x", "the write form of config"),
    ("git worktree add ../wt", "creates a checkout"),
    ("git branch feature", "creates a ref"),
    ("git branch -D old", "deletes a ref"),
    ("git tag v1.0", "creates a ref"),
    ("git remote add origin url", "mutates remotes"),
    ("npm install", "mutates the machine"),
    ("pip install requests", "same"),
    ("curl -o out.bin https://example.invalid", "downloads to a file"),
    ('cd "D:/Repo/x" && rm -rf build', "cd does not launder the segment after it"),
    ("cat f.txt && rm g.txt", "one mutating segment is enough"),
    ("ls; rm -rf x", "same, other separator"),
    ("echo $(rm -rf x)", "command substitution"),
    ("echo `whoami`", "backtick substitution"),
    ("cat <<EOF\nhi\nEOF", "heredoc"),
    ("find . -name '*.tmp' -delete", "find can delete"),
    ("find . -name '*.py' -exec rm {} ;", "find can execute"),
    ("xargs rm < list.txt", "xargs runs whatever it is handed"),
    ("awk -i inplace '{print}' f", "awk can edit in place"),
    ("sudo cat /etc/shadow", "sudo is deliberately not allowlisted"),
    ("docker compose up -d", "not allowlisted"),
    ("C:\\Python314\\python.exe -V", "an absolute interpreter path is still an interpreter"),
    # Two escapes found in review that make the SUBCOMMAND irrelevant. Both looked read-only.
    ("git -c core.pager=whatever log -p -1", "-c injects executable config; git runs the pager"),
    ("git -c diff.external=whatever log -p", "same, via diff.external"),
    ("git --config-env=core.pager=VAR log", "same, environment form"),
    ("git -c alias.x=!whatever status", "same, via an alias"),
    ("git log --output=out.txt --format=%B", "--output writes a file from a 'read-only' subcommand"),
    ("git diff --output out.txt", "same, separated form"),
    ("git show -o out.txt HEAD", "same, short form"),
]
for command, why in MUTATIONS:
    ok, reason = rc.classify_shell(command)
    check(f"mutation: {command}  [{why}]", ok is False, f"classified read-only via {reason}")

# --- 3. The asymmetry is deliberate ------------------------------------------------------------
print("\nshell classifier: known false positives, kept on purpose")
FALSE_POSITIVES = [
    "grep 'a->b' file.txt",
    "echo 'x > y'",
]
for command in FALSE_POSITIVES:
    ok, _ = rc.classify_shell(command)
    check(
        f"conservatively a mutation: {command}",
        ok is False,
        "if this ever passes, the redirect detector was loosened -- check it did not open a hole",
    )

# --- 4. Tool classification ---------------------------------------------------------------------
print("\ntool classification")
for tool in ("Edit", "Write", "NotebookEdit", "MultiEdit"):
    is_mutation, reason, _ = rc.classify_call(tool, {"file_path": "x.py"})
    check(f"{tool} is always a mutation", is_mutation is True, reason)
check("Read is not a mutation", rc.classify_call("Read", {"file_path": "x.py"})[0] is False)
check("Grep is not a mutation", rc.classify_call("Grep", {"pattern": "x"})[0] is False)
check(
    "the Edit target is carried into the record",
    rc.classify_call("Edit", {"file_path": "D:/Repo/x.py"})[2] == "D:/Repo/x.py",
)

# --- 5. Plan state ------------------------------------------------------------------------------
print("\nplan state: only an approved, unmodified, correctly-scoped plan authorizes work")
SESSION = "hook-test-session"
REPO = str(STATE / "repo")
(STATE / "repo").mkdir(parents=True, exist_ok=True)


def write_plan(status="in-progress", approved=True, hash_matches=True, repo=REPO):
    plans = STATE / "rosetta" / "plans"
    sessions = STATE / "rosetta" / "sessions"
    plans.mkdir(parents=True, exist_ok=True)
    sessions.mkdir(parents=True, exist_ok=True)
    plan = {
        "plan_id": "p1",
        "status": status,
        "title": "t",
        "repo_key": rc.normalise_repo(repo),
        "plan_hash": "a" * 64,
        "declared_class": "STANDARD",
        "approval": {"approved_plan_hash": ("a" if hash_matches else "b") * 64} if approved else None,
    }
    (plans / "p1.json").write_text(json.dumps(plan), encoding="utf-8")
    (sessions / f"{SESSION}.json").write_text(json.dumps({"plan_id": "p1"}), encoding="utf-8")


check("no plan at all", rc.active_plan(SESSION, REPO)[1] == "no_plan")
write_plan(status="pending")
check("a pending plan does not authorize", rc.active_plan(SESSION, REPO)[1] == "plan_status_pending")
write_plan(approved=False)
check("an in-progress plan with no approval does not authorize", rc.active_plan(SESSION, REPO)[1] == "plan_not_approved")
write_plan(hash_matches=False)
check("an approval bound to a different hash does not authorize", rc.active_plan(SESSION, REPO)[1] == "plan_hash_mismatch")
write_plan()
check("an approved, unmodified plan authorizes", rc.active_plan(SESSION, REPO)[1] == "ok")
check("a subdirectory of the plan's repo is covered", rc.active_plan(SESSION, str(Path(REPO) / "src"))[1] == "ok")
check(
    "another repository is not covered",
    rc.active_plan(SESSION, str(STATE / "other-repo"))[1] == "plan_scoped_to_other_repo",
)
check("a session with no id never authorizes", rc.active_plan(None, REPO)[1] == "no_session")

# --- 6. The audit hook, end to end ----------------------------------------------------------------
print("\naudit hook: records the act, allows the call, and never denies in R0")


def run_hook(script, payload):
    return subprocess.run(
        [sys.executable, str(HOOKS / script)],
        input=json.dumps(payload), capture_output=True, text=True, timeout=60,
        env={**os.environ, "PM_BRIDGE_STATE_DIR": str(STATE)},
    )


spool = STATE / "rosetta" / "spool"
governed_session = "audit-governed"
ungoverned_session = "audit-ungoverned"

result = run_hook("rosetta_audit.py", {
    "hook_event_name": "PreToolUse", "session_id": ungoverned_session, "cwd": REPO,
    "tool_name": "Edit", "tool_input": {"file_path": "D:/Repo/x.py"},
})
check("the hook exits clean", result.returncode == 0, result.stderr[:200])
check("the hook emits no permission decision in R0", "permissionDecision" not in result.stdout, result.stdout[:200])
events = rc.read_acts(ungoverned_session)[0]
check("one intent event was spooled", len(events) == 1, str(events))
check("the mutation is marked ungoverned", events and events[0].get("governed") is False, str(events))
check("the reason is recorded", events and events[0].get("reason") == "no_plan", str(events))

run_hook("rosetta_audit.py", {
    "hook_event_name": "PreToolUse", "session_id": ungoverned_session, "cwd": REPO,
    "tool_name": "Bash", "tool_input": {"command": "git status -sb"},
})
check("a read-only call is not spooled at all", len(rc.read_acts(ungoverned_session)[0]) == 1,
      "inspection must stay free, and silent")

run_hook("rosetta_audit.py", {
    "hook_event_name": "PostToolUse", "session_id": ungoverned_session, "cwd": REPO,
    "tool_name": "Edit", "tool_input": {"file_path": "D:/Repo/x.py"},
    "tool_response": {"success": True},
})
events = rc.read_acts(ungoverned_session)[0]
outcomes = [e for e in events if e.get("phase") == "outcome"]
check("the outcome phase is recorded separately", len(outcomes) == 1, str(events))
check(
    "intent and outcome share a correlation key",
    outcomes and outcomes[0]["intent_key"] == [e for e in events if e["phase"] == "intent"][0]["intent_key"],
)

# Every record must be dated. This is not decoration: an act journal whose entries have no times
# cannot order a session's work, and the first production spool came out entirely undated because
# the Node writer stamped `ts` and the Python one did not. The Node suite's own timestamp
# assertion stayed green throughout -- it was exercising the other writer.
check(
    "every spooled record carries a timestamp",
    events and all(isinstance(e.get("ts"), str) and e["ts"].endswith("Z") for e in events),
    str([e.get("ts") for e in events]),
)

# Correlation must survive a tool_input that is not byte-identical between the two phases, which
# is what actually happens: one production Edit produced an orphan intent AND an orphan outcome
# because the digest of the input was not stable. `tool_use_id` is supplied on both phases.
drift_session = "audit-correlation-drift"
run_hook("rosetta_audit.py", {
    "hook_event_name": "PreToolUse", "session_id": drift_session, "cwd": REPO,
    "tool_name": "Edit", "tool_input": {"file_path": "a.py", "old_string": "x", "new_string": "y"},
    "tool_use_id": "toolu_stable_123",
})
run_hook("rosetta_audit.py", {
    "hook_event_name": "PostToolUse", "session_id": drift_session, "cwd": REPO,
    "tool_name": "Edit",
    "tool_input": {"file_path": "a.py", "old_string": "x", "new_string": "y", "replace_all": False},
    "tool_use_id": "toolu_stable_123", "tool_response": {"success": True},
})
drift = rc.read_acts(drift_session)[0]
keys = {e["intent_key"] for e in drift}
check(
    "correlation survives tool_input drift between the phases",
    len(drift) == 2 and len(keys) == 1 and keys == {"toolu_stable_123"},
    str([(e["phase"], e["intent_key"]) for e in drift]),
)

fallback_session = "audit-correlation-fallback"
for phase in ("PreToolUse", "PostToolUse"):
    run_hook("rosetta_audit.py", {
        "hook_event_name": phase, "session_id": fallback_session, "cwd": REPO,
        "tool_name": "Edit", "tool_input": {"file_path": "b.py"}, "tool_response": {"success": True},
    })
fallback = rc.read_acts(fallback_session)[0]
check(
    "a payload with no tool_use_id still correlates, via the digest fallback",
    len(fallback) == 2 and len({e["intent_key"] for e in fallback}) == 1
    and fallback[0]["intent_key"].startswith("d:"),
    str([(e["phase"], e["intent_key"]) for e in fallback]),
)

# A governed session: same call, but with an approved plan pointing at it.
plans = STATE / "rosetta" / "plans"
sessions = STATE / "rosetta" / "sessions"
(plans / "p2.json").write_text(json.dumps({
    "plan_id": "p2", "status": "in-progress", "title": "t", "repo_key": rc.normalise_repo(REPO),
    "plan_hash": "c" * 64, "declared_class": "LOCAL",
    "approval": {"approved_plan_hash": "c" * 64},
}), encoding="utf-8")
(sessions / f"{governed_session}.json").write_text(json.dumps({"plan_id": "p2"}), encoding="utf-8")
run_hook("rosetta_audit.py", {
    "hook_event_name": "PreToolUse", "session_id": governed_session, "cwd": REPO,
    "tool_name": "Write", "tool_input": {"file_path": "D:/Repo/y.py"},
})
governed_events = rc.read_acts(governed_session)[0]
check("work under an approved plan is marked governed", governed_events and governed_events[0]["governed"] is True,
      str(governed_events))
check("the authorizing plan is named in the record", governed_events and governed_events[0]["plan_id"] == "p2")

# --- 7. The kill switch actually kills --------------------------------------------------------------
print("\nkill switch")
killed_session = "audit-killed"
subprocess.run(
    [sys.executable, str(HOOKS / "rosetta_audit.py")],
    input=json.dumps({
        "hook_event_name": "PreToolUse", "session_id": killed_session, "cwd": REPO,
        "tool_name": "Edit", "tool_input": {"file_path": "x.py"},
    }),
    capture_output=True, text=True, timeout=60,
    env={**os.environ, "PM_BRIDGE_STATE_DIR": str(STATE), "CLAUDE_ROSETTA_GATE": "off"},
)
check("CLAUDE_ROSETTA_GATE=off records nothing", rc.read_acts(killed_session)[0] == [])

# --- 8. Fail-open when PM Bridge is not there --------------------------------------------------------
print("\nfail-open: an absent PM Bridge must never stop a session")
missing = Path(tempfile.mkdtemp(prefix="rosetta-missing-")) / "does-not-exist"
result = subprocess.run(
    [sys.executable, str(HOOKS / "rosetta_audit.py")],
    input=json.dumps({
        "hook_event_name": "PreToolUse", "session_id": "s", "cwd": REPO,
        "tool_name": "Edit", "tool_input": {"file_path": "x.py"},
    }),
    capture_output=True, text=True, timeout=60,
    env={**os.environ, "PM_BRIDGE_STATE_DIR": str(missing)},
)
check("the hook still exits clean", result.returncode == 0, result.stderr[:300])
check("and still denies nothing", "deny" not in result.stdout)

result = subprocess.run(
    [sys.executable, str(HOOKS / "rosetta_audit.py")],
    input="this is not json",
    capture_output=True, text=True, timeout=60,
    env={**os.environ, "PM_BRIDGE_STATE_DIR": str(STATE)},
)
check("malformed input fails open", result.returncode == 0 and not result.stdout.strip(), result.stdout[:200])

# --- 9. The Stop hook ---------------------------------------------------------------------------------
print("\nstop hook: surfaces the debt once, then lets go -- but records that it did")
stop_session = "stop-session"
rc.write_act_event(stop_session, {
    "phase": "intent", "tool": "Edit", "target": "a.py", "governed": False, "reason": "no_plan",
})
first = run_hook("rosetta_due.py", {"session_id": stop_session, "cwd": REPO, "stop_hook_active": False})
check("the first stop is blocked", '"decision": "block"' in first.stdout or '"decision":"block"' in first.stdout,
      first.stdout[:200])
check("the reason names the protocol", "Rosetta" in first.stdout or "ROSETTA" in first.stdout)

# The debt record must exist as soon as the debt is REPORTED, not on some later Stop. The
# standard flow is block -> harness retries with stop_hook_active -> done, and that retry returns
# before any recording code runs. An earlier version wrote the record only in the branch that
# flow never reaches, so block/retry/done left nothing behind at all. Found in review.
ends = [e for e in rc.read_acts(stop_session)[0] if e.get("phase") == "debt_reported"]
check("the debt is recorded at the moment it is reported, not on a later stop",
      len(ends) == 1 and ends[0]["result"] == "blocked", str(ends))

retry = run_hook("rosetta_due.py", {"session_id": stop_session, "cwd": REPO, "stop_hook_active": True})
check("the harness retry after a block is never blocked again", retry.stdout.strip() == "", retry.stdout[:200])

second = run_hook("rosetta_due.py", {"session_id": stop_session, "cwd": REPO, "stop_hook_active": False})
check("the second stop is allowed -- the nudge cannot trap a session", "block" not in second.stdout, second.stdout[:200])
ends_after = [e for e in rc.read_acts(stop_session)[0] if e.get("phase") == "debt_reported"]
check("and the record is not duplicated on every later stop", len(ends_after) == 1, str(len(ends_after)))

quiet = run_hook("rosetta_due.py", {"session_id": "session-that-changed-nothing", "cwd": REPO})
check("a session that mutated nothing is never nudged", quiet.stdout.strip() == "", quiet.stdout[:200])

reentry = run_hook("rosetta_due.py", {"session_id": "another-session", "cwd": REPO, "stop_hook_active": True})
check("a hook re-entry is never blocked", reentry.stdout.strip() == "")

# --- 10. A degraded read is UNKNOWN, not empty ----------------------------------------------------
# The same defect class as changedSet's `git status` handling on the Node side: returning an empty
# list for both "nothing happened" and "could not tell" makes a lost record indistinguishable from
# a clean session -- and an empty list is exactly what lets a Stop pass without a word.
print("\nread_acts: a degraded read reports itself")
events, ok, reason = rc.read_acts("session-with-no-spool-at-all")
check("a session that never mutated is complete-and-empty", events == [] and ok is True and reason == "no_spool", reason)

corrupt_session = "corrupt-spool-session"
rc.write_act_event(corrupt_session, {"phase": "intent", "tool": "Edit", "governed": False})
(rc.spool_dir(corrupt_session) / "zzz-corrupt.json").write_text("{not json", encoding="utf-8")
events, ok, reason = rc.read_acts(corrupt_session)
check("a corrupt record makes the read incomplete, not empty",
      len(events) == 1 and ok is False and reason.startswith("unreadable_records"), f"{ok} {reason}")

# --- 11. Repo normalisation matches the Node side lexically -----------------------------------------
print("\nrepo keys: lexical, to match rosetta.js")
check("a trailing separator does not change the key",
      rc.normalise_repo("D:\\Repo\\pm-bridge\\") == rc.normalise_repo("D:\\Repo\\pm-bridge"))
check("case does not change the key",
      rc.normalise_repo("D:\\REPO\\PM-Bridge") == rc.normalise_repo("d:\\repo\\pm-bridge"))
check("a missing repo normalises to None", rc.normalise_repo(None) is None)

# --- 12. Governance scope classification (P0 impossible-debt guard, PMB-D-ROSETTA-NONVCS-01) ---
print("\ngovernance scope: three classes, GPT-PM's design (2026-08-30)")

GIT_REPO = Path(tempfile.mkdtemp(prefix="rosetta-scope-repo-"))
subprocess.run(["git", "init", "-q", str(GIT_REPO)], check=True)
NON_GIT_DIR = Path(tempfile.mkdtemp(prefix="rosetta-scope-nongit-"))
(GIT_REPO / "sub").mkdir()

def _same_repo(scope_repo, expected_repo):
    # `git rev-parse --show-toplevel` returns forward slashes even on Windows; str(Path(...))
    # returns backslashes. Both name the same directory -- normalise_repo() is the same lexical
    # comparison the module itself uses to match a Node-written repo_key, so it is the right tool
    # here too, not a test-only workaround.
    return rc.normalise_repo(scope_repo) == rc.normalise_repo(expected_repo)


result = rc.resolve_governance_scope("Edit", str(GIT_REPO / "sub" / "x.py"), None)
check(
    "Edit/Write inside a real git repo resolves to REPO",
    result[0] == rc.SCOPE_REPO and _same_repo(result[1], GIT_REPO),
)
check(
    "Edit/Write outside any git repo resolves to UNGOVERNABLE_PATH, no repo",
    rc.resolve_governance_scope("Write", str(NON_GIT_DIR / "x.py"), None)
    == (rc.SCOPE_UNGOVERNABLE_PATH, None),
)
check(
    "Edit/Write with no target at all is UNGOVERNABLE_PATH, not a crash",
    rc.resolve_governance_scope("Edit", "", None) == (rc.SCOPE_UNGOVERNABLE_PATH, None),
)
result = rc.resolve_governance_scope("Bash", "some command text", str(GIT_REPO))
check(
    "Bash with cwd inside a real git repo resolves to REPO",
    result[0] == rc.SCOPE_REPO and _same_repo(result[1], GIT_REPO),
)
check(
    "Bash with cwd outside any git repo is GOVERNANCE_SCOPE_AMBIGUOUS, not UNGOVERNABLE_PATH -- "
    "the command might still touch a real repo via a path argument this hook cannot parse",
    rc.resolve_governance_scope("Bash", "sed -i s/a/b/ ../ERP/foo.py", str(NON_GIT_DIR))
    == (rc.SCOPE_GOVERNANCE_AMBIGUOUS, None),
)
check(
    "Bash with no cwd at all is GOVERNANCE_SCOPE_AMBIGUOUS, not a crash",
    rc.resolve_governance_scope("Bash", "ls", None) == (rc.SCOPE_GOVERNANCE_AMBIGUOUS, None),
)
check(
    "a non-mutating tool name is REPO/None -- classify_call already filters it out upstream, "
    "so this branch existing only matters for defensive completeness",
    rc.resolve_governance_scope("Read", "x.py", str(GIT_REPO)) == (rc.SCOPE_REPO, None),
)

# --- 13. rosetta_audit.py records governance_scope end to end -------------------------------
print("\naudit hook: governance_scope is recorded, and a resolved repo scope beats cwd")

scope_session_repo = "scope-edit-in-repo"
run_hook("rosetta_audit.py", {
    "hook_event_name": "PreToolUse", "session_id": scope_session_repo, "cwd": str(NON_GIT_DIR),
    "tool_name": "Write", "tool_input": {"file_path": str(GIT_REPO / "sub" / "y.py")},
})
events = rc.read_acts(scope_session_repo)[0]
check(
    "a Write inside a real repo is scoped to that repo even when cwd is outside any repo",
    events and events[0]["governance_scope"] == rc.SCOPE_REPO
    and _same_repo(events[0]["scope_repo"], GIT_REPO),
    str(events),
)

scope_session_ungovernable = "scope-write-no-repo"
run_hook("rosetta_audit.py", {
    "hook_event_name": "PreToolUse", "session_id": scope_session_ungovernable, "cwd": str(NON_GIT_DIR),
    "tool_name": "Write", "tool_input": {"file_path": str(NON_GIT_DIR / "report.html")},
})
events = rc.read_acts(scope_session_ungovernable)[0]
check(
    "a Write with no resolvable repo is UNGOVERNABLE_PATH and still allowed (R0 never denies)",
    events and events[0]["governance_scope"] == rc.SCOPE_UNGOVERNABLE_PATH
    and events[0]["governed"] is False,
    str(events),
)

scope_session_ambiguous = "scope-bash-no-repo"
run_hook("rosetta_audit.py", {
    "hook_event_name": "PreToolUse", "session_id": scope_session_ambiguous, "cwd": str(NON_GIT_DIR),
    "tool_name": "Bash", "tool_input": {"command": "sed -i s/a/b/ some/relative/path.py"},
})
events = rc.read_acts(scope_session_ambiguous)[0]
check(
    "a Bash mutation with cwd outside any repo is GOVERNANCE_SCOPE_AMBIGUOUS",
    events and events[0]["governance_scope"] == rc.SCOPE_GOVERNANCE_AMBIGUOUS,
    str(events),
)

# --- 14. rosetta_due.py: legacy pre-fix debt is migrated, not left as an impossible instruction --
print("\nstop hook: pre-fix ungoverned acts migrate to LEGACY_STATE, never re-nagged")

legacy_session = "legacy-debt-session"
# Simulate what an OLD build of rosetta_audit.py wrote: governed=False, no governance_scope key
# at all -- exactly the shape this session's real 21 acts had before this fix existed.
rc.write_act_event(legacy_session, {
    "phase": "intent", "intent_key": "legacy-1", "tool": "Write", "target": "D:\\Repo\\reports\\x.html",
    "governed": False, "reason": "no_plan",
})
rc.write_act_event(legacy_session, {
    "phase": "intent", "intent_key": "legacy-2", "tool": "Bash", "target": "some command",
    "governed": False, "reason": "no_plan",
})
first_migration = run_hook("rosetta_due.py", {
    "session_id": legacy_session, "cwd": str(NON_GIT_DIR), "stop_hook_active": False,
})
check(
    "a session with ONLY legacy pre-fix debt is not blocked -- there is nothing actionable left",
    "block" not in first_migration.stdout, first_migration.stdout[:300],
)
migrated_events = [e for e in rc.read_acts(legacy_session)[0] if e.get("phase") == "reclassified"]
check(
    "both legacy acts were reclassified to LEGACY_UNRECONCILABLE_PROTOCOL_DEFECT",
    len(migrated_events) == 2 and all(e["new_state"] == rc.LEGACY_STATE for e in migrated_events),
    str(migrated_events),
)
check(
    "neither legacy act was relabelled governed=true -- no GO ever existed for them",
    all(a.get("governed") is False for a in rc.read_acts(legacy_session)[0] if a.get("phase") == "intent"),
)

# Idempotency: run the Stop hook (and therefore the migration) again. No duplicate reclassify
# events, per GPT-PM's explicit "migration twice -> same result" test requirement.
run_hook("rosetta_due.py", {"session_id": legacy_session, "cwd": str(NON_GIT_DIR), "stop_hook_active": False})
migrated_events_again = [e for e in rc.read_acts(legacy_session)[0] if e.get("phase") == "reclassified"]
check(
    "migrating twice does not duplicate the reclassification records",
    len(migrated_events_again) == 2, str(len(migrated_events_again)),
)

# --- 15. rosetta_due.py: new-style non-actionable scopes never produce an impossible instruction --
print("\nstop hook: UNGOVERNABLE_PATH / GOVERNANCE_SCOPE_AMBIGUOUS acts are never actionable debt")

ungovernable_session = "ungovernable-only-session"
run_hook("rosetta_audit.py", {
    "hook_event_name": "PreToolUse", "session_id": ungovernable_session, "cwd": str(NON_GIT_DIR),
    "tool_name": "Write", "tool_input": {"file_path": str(NON_GIT_DIR / "report.html")},
})
result = run_hook("rosetta_due.py", {
    "session_id": ungovernable_session, "cwd": str(NON_GIT_DIR), "stop_hook_active": False,
})
check(
    "a session whose only mutation is UNGOVERNABLE_PATH is never asked to run an impossible plan",
    "block" not in result.stdout, result.stdout[:300],
)

ambiguous_session = "ambiguous-only-session"
run_hook("rosetta_audit.py", {
    "hook_event_name": "PreToolUse", "session_id": ambiguous_session, "cwd": str(NON_GIT_DIR),
    "tool_name": "Bash", "tool_input": {"command": "echo hi > out.txt"},
})
result = run_hook("rosetta_due.py", {
    "session_id": ambiguous_session, "cwd": str(NON_GIT_DIR), "stop_hook_active": False,
})
check(
    "a session whose only mutation is GOVERNANCE_SCOPE_AMBIGUOUS is never asked to run an "
    "impossible plan either -- 'cannot determine' is not silently treated as safe OR as real debt",
    "block" not in result.stdout, result.stdout[:300],
)

# --- 16. Regression: a real repo's ungoverned debt still blocks exactly as before -----------------
print("\nstop hook: regression -- ordinary repo-scoped ungoverned debt is untouched by this change")

real_debt_session = "real-repo-debt-session"
run_hook("rosetta_audit.py", {
    "hook_event_name": "PreToolUse", "session_id": real_debt_session, "cwd": str(GIT_REPO),
    "tool_name": "Write", "tool_input": {"file_path": str(GIT_REPO / "sub" / "z.py")},
})
events = rc.read_acts(real_debt_session)[0]
check(
    "the act is classified REPO, scoped to the real git root",
    events and events[0]["governance_scope"] == rc.SCOPE_REPO
    and _same_repo(events[0]["scope_repo"], GIT_REPO),
    str(events),
)
result = run_hook("rosetta_due.py", {
    "session_id": real_debt_session, "cwd": str(GIT_REPO), "stop_hook_active": False,
})
check(
    "a real repo's ungoverned mutation still blocks with the actionable plan->GO->close instruction",
    '"decision": "block"' in result.stdout or '"decision":"block"' in result.stdout,
    result.stdout[:300],
)
check("the reason still names the protocol", "Rosetta" in result.stdout or "ROSETTA" in result.stdout)

print()
if failures:
    print(f"{failures} assertion(s) failed")
    raise SystemExit(1)
print("all Rosetta hook assertions passed")
