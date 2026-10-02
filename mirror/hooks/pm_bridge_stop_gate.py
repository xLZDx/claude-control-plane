#!/usr/bin/env python3
"""DISABLED 2026-09-17. No longer registered in settings.json's PreToolUse hooks.

This gate denied any Claude-session shell path that switched the shared PM Bridge orchestrator
OFF, per operator instruction 2026-09-13: "запрети его отключать всем ... кроме меня" -- put in
place after the shared daemon vanished cleanly (state file removed, no crash) twice on 2026-09-12,
each time a session decided unilaterally that its own work being done meant everyone else's was
too. The matching MCP-side refusal lived in
D:\\Repo\\pm-bridge\\src\\cli\\orchestratorLifecycle.js (MODE_OFF_REFUSAL).

REVERSED, operator instruction, 2026-09-17, explicit and separately confirmed ("да, снять
ограничение навсегда" -- yes, remove the restriction permanently) -- not folded into the live
incident that triggered the question. During a live ChatGPT account-wide rate-limit emergency,
this restriction meant no Claude session could stop a daemon that was actively still hammering an
already-blocked account every ~20-40s, and `pm_bridge_restart` does not help that failure mode
(the fresh process immediately resumes hitting the same blocked account). The operator was walked
through what reversing this trades away -- the 2026-09-12 incident this gate existed to prevent
can recur -- before confirming. Full incident record: D:\\Repo\\pm-bridge\\core\\DECISION_LOG.md,
2026-09-17.

Kept on disk rather than deleted only because ~/.claude is not a git repository (no blame/history
otherwise) -- this file does nothing; it is not imported or invoked by anything.
"""
