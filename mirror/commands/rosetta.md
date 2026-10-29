---
description: Turn Rosetta on/off, show its mode, or open/inspect/close a Rosetta plan (Plan -> GO -> Act -> Validate -> Document)
argument-hint: [on | off | mode | status | close | task description]
---

Rosetta is OFF by default (operator 2026-10-09). The switch is the file
`C:\Users\koros\.claude\state\rosetta_mode.json`; the hooks re-read it on every call, so `on`/`off`
applies immediately in every session. `CLAUDE_ROSETTA_GATE=on|off` (process env) overrides the file.
The protocol itself lives in the `rosetta` skill and PM Bridge (`D:\Repo\pm-bridge\src\rosetta.js`);
do NOT duplicate it here.

On invocation:

1. If `$ARGUMENTS` is `on`, `off` or `mode`: run
   `C:\Python314\python.exe -s C:\Users\koros\.claude\hooks\rosetta_mode.py <on|off|status>`
   (`mode` maps to `status`) and report its one-line output in Russian. STOP.
2. If Rosetta is OFF (check with `rosetta_mode.py status`) and `$ARGUMENTS` is anything else: say
   Rosetta is off and that `/rosetta on` turns it on. STOP.
3. If `$ARGUMENTS` is `status` (or empty): call `pm_rosetta_status` with this session's
   `$CLAUDE_CODE_SESSION_ID` and the current repository path. Report the plan, whether the session
   is governed, and how many acts ran ungoverned. STOP.
4. If `$ARGUMENTS` starts with `close`: close the active plan with `pm_rosetta_close`. Evidence is
   mandatory for `passed`. STOP.
5. Otherwise: invoke the `rosetta` skill via the Skill tool and open a plan for `$ARGUMENTS`,
   following the skill's own steps.

Turning Rosetta on or off is not itself a GO for any work.
