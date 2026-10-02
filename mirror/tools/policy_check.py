"""Verify that the global policy in ~/.claude is intact, registered and tracked.

Versioning the policy (2026-08-26) made drift VISIBLE in git history. It did not make three
adjacent failures visible, and this closes those:

  1. A hook registered in settings.json whose file does not exist. Claude Code does not stop for
     this -- the gate simply never fires, and a session keeps working with one fewer safety check
     than everyone believes it has. Nothing in git history shows it either, because the deletion
     of a file nobody committed leaves no trace.
  2. A hook file present but NOT tracked by git, i.e. exactly the state the whole repository was
     created to end. A new hook dropped in and never added is untracked policy again.
  3. Uncommitted policy changes. Not an error -- work in progress is normal -- but worth saying
     out loud, because "the policy is versioned" is only true of the committed part.

Usage:
    py -3 policy_check.py           # human-readable report
    py -3 policy_check.py --check   # exit 1 if anything is wrong, for use in a gate
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SETTINGS = ROOT / "settings.json"


def git(*args):
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def registered_hooks():
    """(event, matcher, path) for every hook command in settings.json.

    Reads the file rather than assuming a shape: the settings schema has changed under this
    directory before, and a checker that silently finds nothing is worse than no checker.
    """
    try:
        data = json.loads(SETTINGS.read_text(encoding="utf-8"))
    except Exception as e:
        return None, f"cannot read {SETTINGS}: {e}"

    found = []
    for event, blocks in (data.get("hooks") or {}).items():
        if not isinstance(blocks, list):
            continue
        for block in blocks:
            matcher = (block or {}).get("matcher", "*")
            for hook in (block or {}).get("hooks") or []:
                args = hook.get("args") or []
                paths = [a for a in args if isinstance(a, str) and a.lower().endswith(".py")]
                for p in paths:
                    found.append((event, matcher, Path(p)))
    return found, None


def main():
    strict = "--check" in sys.argv
    problems = []
    notes = []

    code, _, err = git("rev-parse", "--is-inside-work-tree")
    if code != 0:
        print(f"POLICY: {ROOT} is not a git repository -- the global policy is untracked. ({err})")
        return 1 if strict else 0

    hooks, err = registered_hooks()
    if err:
        problems.append(err)
        hooks = []
    if not hooks:
        problems.append("settings.json registers no hooks at all -- every gate is off")

    _, tracked_out, _ = git("ls-files")
    tracked = {(ROOT / line).resolve() for line in tracked_out.splitlines() if line}

    for event, matcher, path in hooks:
        p = path if path.is_absolute() else (ROOT / path)
        if not p.is_file():
            problems.append(f"{event}/{matcher}: registered hook is MISSING -> {p}")
            continue
        if p.resolve() not in tracked:
            problems.append(f"{event}/{matcher}: hook is present but NOT TRACKED by git -> {p}")

    _, dirty, _ = git("status", "--porcelain")
    dirty_lines = [l for l in dirty.splitlines() if l.strip()]
    if dirty_lines:
        notes.append(f"{len(dirty_lines)} uncommitted change(s) -- the committed policy is not the running one")

    print(f"POLICY CHECK  {ROOT}")
    print(f"  registered hooks : {len(hooks)}")
    print(f"  tracked files    : {len(tracked)}")
    for n in notes:
        print(f"  note             : {n}")
    for p in problems:
        print(f"  PROBLEM          : {p}")
    if not problems:
        print("  every registered hook exists and is tracked")

    return 1 if (strict and problems) else 0


if __name__ == "__main__":
    sys.exit(main())
