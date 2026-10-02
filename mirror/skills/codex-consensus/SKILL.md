---
name: codex-consensus
description: Optional read-only Codex second opinion for unresolved major findings, high-risk changes, or explicit operator requests. Not a mandatory commit/push gate.
---

# Codex Second Opinion

Use only when independent-model evidence can change a decision. External Codex runs need the operator's explicit authorization for that run (global contract section 4). One round by default; one rebuttal for a still-contested BLOCKER/MAJOR, then surface the disagreement instead of looping.

## Invoke
`py -3 "$HOME/.claude/tools/codex_review.py" --cwd <repo> --uncommitted` (or `--base <branch>`, `--commit <sha>`). One sequential call; no fan-out mode exists.
Manual, human-in-the-loop path (`--print-prompt` then `--ingest-response`): see the reference. Never wire it into a loop.

## Rules
- Codex is not a panel seat: it reviews the diff cold; never feed it other reviewers' findings. Reconcile afterwards one-on-one.
- Read-only sandbox; it never edits or authorizes git operations.
- Verify every accepted finding against the cited file:line yourself; label unsupported citations `CONFABULATION`.
- `SILENT` is not agreement and majority is not proof. If Codex is unavailable report `skipped(<reason>)`; do not block unrelated work.
- On its own usage-limit message do not retry in this session: report `skipped (usage limit, resets <date>)`.
- Do not spend rounds on settled MINOR/NIT items.

Full text with manual-mode details and dated operator decisions: `references/full-procedure.md`.
