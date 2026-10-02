"""Behaviour of the full-path-label check, exercised through main() the way the hook is called.

Every case runs against real files in real git repositories, because the rule's minimum
("repo-relative") is only meaningful if the repo root is found the way it is in production.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import sys
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('gate', HERE.parent / 'hooks' / 'evidence_gate.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

REPO = Path(r'D:\Repo\pm-bridge')
CLAUDE = Path(r'C:\Users\koros\.claude')
os.environ['CLAUDE_HOOK_STATE_DIR'] = str(HERE)

failures: list[str] = []


def run(message: str, cwd: Path = REPO) -> dict:
    payload = json.dumps({'last_assistant_message': message, 'cwd': str(cwd),
                          'hook_event_name': 'Stop'})
    stdin, sys.stdin = sys.stdin, io.StringIO(payload)
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            gate.main()
    finally:
        sys.stdin = stdin
    out = buf.getvalue().strip()
    return json.loads(out) if out else {}


def check(name: str, message: str, *, blocked: bool, needle: str = '', cwd: Path = REPO) -> None:
    res = run(message, cwd)
    got = res.get('decision') == 'block'
    if got != blocked:
        failures.append(f'{name}: expected blocked={blocked}, got {blocked is not got and "the opposite" or res}')
        return
    if blocked and needle and needle not in res.get('reason', ''):
        failures.append(f'{name}: reason missing {needle!r} -- {res.get("reason")!r}')
    print(f'  ok  {name}')


print('label rule -- what must block')
check('bare filename label', '[rosetta.js](src/rosetta.js)',
      blocked=True, needle='src/rosetta.js')
check('prose label', 'see [the closure handler](src/rosetta.js) for details',
      blocked=True, needle='full path')
check('filename with line number only', '[rosetta.js:437](src/rosetta.js#L437)',
      blocked=True, needle='src/rosetta.js')
check('repo-root file named bare', '[README.md](README.md)',
      blocked=True, needle='pm-bridge/readme.md')

print('label rule -- what must pass')
check('repo-relative label', '[src/rosetta.js](src/rosetta.js)', blocked=False)
check('absolute label', r'[D:\Repo\pm-bridge\src\rosetta.js](src/rosetta.js)', blocked=False)
check('absolute label with line', r'[D:\Repo\pm-bridge\src\rosetta.js:437](src/rosetta.js#L437)',
      blocked=False)
check('label longer than href', '[pm-bridge/src/rosetta.js](src/rosetta.js)', blocked=False)
check('label inside emphasis', '**[src/rosetta.js](src/rosetta.js)**', blocked=False)
check('repo-root file with its directory', r'[D:\Repo\pm-bridge\README.md](README.md)', blocked=False)

print('links the rule must not touch')
check('https url', '[the docs](https://example.com/src/rosetta.js)', blocked=False)
check('artifact link', '[report](https://claude.ai/code/artifact/abc123)', blocked=False)
check('anchor only', '[jump](#section)', blocked=False)
check('directory link', '[state](state/)', blocked=False)
check('unresolvable href is the other check\'s business',
      '[thing](src/definitely_absent_file.js)', blocked=True, needle='does not resolve')

print('interaction with the existing citation check')
check('both problems reported together',
      '[rosetta.js](src/rosetta.js) and [x](src/also_absent.js)',
      blocked=True, needle='FILE PATH LABELS')
check('line beyond end of file still caught',
      '[src/rosetta.js](src/rosetta.js#L999999)', blocked=True, needle='only')

print('other repositories resolve their own root')
check('claude repo, bare label', '[evidence_gate.py](hooks/evidence_gate.py)',
      blocked=True, needle='hooks/evidence_gate.py', cwd=CLAUDE)
check('claude repo, repo-relative label', '[hooks/evidence_gate.py](hooks/evidence_gate.py)',
      blocked=False, cwd=CLAUDE)

print('kill switches')
os.environ['CLAUDE_PATH_LABEL_GATE'] = 'off'
check('label switch off, citation check still live', '[rosetta.js](src/rosetta.js)', blocked=False)
check('label switch off does not disable citations', '[x](src/also_absent.js)',
      blocked=True, needle='does not resolve')
del os.environ['CLAUDE_PATH_LABEL_GATE']
os.environ['CLAUDE_CITATION_GATE'] = 'off'
check('whole gate off', '[rosetta.js](src/rosetta.js)', blocked=False)
del os.environ['CLAUDE_CITATION_GATE']

print('a normal reply with no file links is untouched')
check('plain prose', 'The lock is held by its real owner, not stale.', blocked=False)

print()
if failures:
    print(f'FAIL ({len(failures)})')
    for f in failures:
        print('  -', f)
    raise SystemExit(1)
print('PASS')
