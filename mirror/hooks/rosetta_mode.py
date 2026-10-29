#!/usr/bin/env python3
"""Turn the Rosetta hooks on or off: `rosetta_mode.py on|off|status`.

Writes `~/.claude/state/rosetta_mode.json`, which `_rosetta_common.gate_off()` re-reads on every
hook call, so the switch applies immediately in every session. Absent file = off.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rosetta_common import gate_off, mode_enabled, mode_file  # noqa: E402


def _describe() -> str:
    env = os.environ.get("CLAUDE_ROSETTA_GATE", "")
    state = "OFF" if gate_off() else "ON"
    note = f" (forced by CLAUDE_ROSETTA_GATE={env})" if env.lower() in ("on", "off") else ""
    return f"Rosetta: {state}{note}; switch file enabled={mode_enabled()} at {mode_file()}"


def main(argv: list[str]) -> int:
    action = (argv[1] if len(argv) > 1 else "status").strip().lower()
    if action in ("on", "off"):
        path = mode_file()
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        payload = {"enabled": action == "on", "changed_at": datetime.now(timezone.utc).isoformat()}
        tmp.write_text(json.dumps(payload) + "\n", encoding="utf-8")
        os.replace(tmp, path)
    elif action != "status":
        print("usage: rosetta_mode.py on|off|status", file=sys.stderr)
        return 2
    print(_describe())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
