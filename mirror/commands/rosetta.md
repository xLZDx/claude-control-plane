---
description: Open, inspect or close a Rosetta plan -- the Plan -> GO -> Act -> Validate -> Document protocol
argument-hint: [status | close | task description]
---

Thin picker-visible wrapper. The protocol lives in the `rosetta` skill
(`C:\Users\koros\.claude\skills\rosetta\SKILL.md`) and its record lives in PM Bridge
(`D:\Repo\pm-bridge\src\rosetta.js`). Do NOT duplicate either here.

Rosetta is no longer a mode to switch on -- it is always on, recorded by the hooks. This command
only saves typing. The old `/rosetta off` and the session marker it wrote are gone, along with the
`rosetta_reminder.py` hook they drove; that hook was removed in the v4.1 rewrite and this file kept
pointing at it for months. There is nothing to turn off but the kill switch
(`CLAUDE_ROSETTA_GATE=off`, process-level).

On invocation:

1. If `$ARGUMENTS` is `status` (or empty): call `pm_rosetta_status` with this session's
   `$CLAUDE_CODE_SESSION_ID` and the current repository path. Report the plan, whether the session
   is governed, and how many acts ran ungoverned. STOP.
2. If `$ARGUMENTS` starts with `close`: close the active plan with `pm_rosetta_close`. Evidence is
   mandatory for `passed` -- if you do not have it, run the verification the plan itself named
   first. STOP.
3. Otherwise: invoke the `rosetta` skill via the Skill tool and open a plan for `$ARGUMENTS`,
   following the skill's own steps. Get the GO from GPT-PM before acting, not after.

Governance is unchanged: GPT-PM approves plans (CLAUDE.md §16/§17); the operator alone authorizes
the irreversible class in §4/§14.
