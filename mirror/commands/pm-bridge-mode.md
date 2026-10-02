---
description: Turn PM Bridge orchestrator mode on/off/status -- shared cross-project GPT automation via a single queued broker (Gate 9)
argument-hint: [on|off|status]
---

Thin wrapper: the mechanics live in `D:\Repo\pm-bridge\src\orchestrator.js` (the daemon) and
`D:\Repo\pm-bridge\src\orchestratorClient.js` (start/stop/status), exposed as MCP tools
`pm_bridge_mode_on` / `pm_bridge_mode_off` / `pm_bridge_mode_status`. Do NOT duplicate that logic
here.

On invocation:
1. If $ARGUMENTS is `off` (case-insensitive): call `pm_bridge_mode_off`. State the result. STOP.
2. If $ARGUMENTS is `status` (or empty/omitted): call `pm_bridge_mode_status`. State the result. STOP.
3. Otherwise (`on`, or anything else): call `pm_bridge_mode_on`. State the result plainly -- while
   mode is on, the orchestrator is the SOLE owner of the shared ChatGPT browser for every project
   on this machine, until `/pm-bridge-mode off`. STOP.

Mode is global (one state file, `state/orchestrator.json`), not per-session -- it coordinates
INDEPENDENT Claude Code sessions across different `D:\Repo\*` projects, unlike the per-session
`/rosetta` marker. There is a 4h idle-timeout safety net in the orchestrator itself, but prefer
turning it off explicitly with `/pm-bridge-mode off` once the block of work is done rather than
relying on it.

Governance is UNCHANGED: turning mode on/off is not itself a GO for any implementation gate: only
a literal `GO` / `ГО` in chat authorizes that, per the global operating contract.
