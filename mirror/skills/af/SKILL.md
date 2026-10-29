---
name: af
description: "Toggle and inspect the Agentic_Framework SDLC orchestration: on, off, status, next, pm-review, verify."
disable-model-invocation: true
argument-hint: on|off|status|next|verify
---

Toggle and inspect the Agentic_Framework SDLC auto-orchestration for the current project.

Arguments: `on [hard|soft] ["<sprint title>"]`, `off`, `status`, `next`, `pm-review --kind code|docs --base <ref>`, `verify`.

Run exactly one command with the shell, from the project root, and report its output:

- `on`  : `python D:/Repo/Agentic_Framework/tools/af_cli.py on [--mode hard|soft] [--title "<title>"]` - enables the framework (creates the sprint state at phase 1, or resumes a paused one).
- `off` : `python D:/Repo/Agentic_Framework/tools/af_cli.py off` - pauses it: no phase injection, no push gate. State and approvals are kept.
- `status`, `next`, `verify`, `pm-review ...` : pass through to `python D:/Repo/Agentic_Framework/tools/af_cli.py <command>`.

After `on`, follow the injected phase line and launch the listed roles as real agents. Never run `pm-review` or `next` on your own initiative unless the phase flow calls for it, and never hand-write the approval files. With no argument, run `status`.
