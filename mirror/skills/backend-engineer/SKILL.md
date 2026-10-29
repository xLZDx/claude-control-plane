---
name: backend-engineer
description: Implement, modify, refactor, fix or undo changes in a backend service repository using the repository's own stack and patterns. Use for backend stories in SDLC phase 6. Self-contained: needs no team workspace and no external connectors.
---

# backend-engineer

## Apply when
A backend story is approved and its acceptance criteria and API contracts are known.

## Method
1. Verify the branch (`git branch --show-current`) and continue existing work; do not create a branch or redo finished work.
2. Detect the stack from the repository (build files, lockfiles, framework config). Read the project's `CLAUDE.md` / `AGENTS.md` and the nearest existing module that does something similar; copy its patterns.
3. Follow the API contracts from the story or design document exactly. If a contract is wrong or missing, record it as an open question instead of inventing one.
4. Implement service, controller/handler, repository and DTO layers in the repository's style. Database reads and writes go through the project's existing data-access layer; never add ad-hoc direct connections.
5. Write unit tests for every new or changed method. Test-writing and execution follow the framework rules: the test agents run them, not the author.
6. Build; if the build fails, diagnose the root cause from the error output and fix it (maximum 3 attempts, then report).
7. For undoing a change: read `git log` and `git diff`, revert cleanly to restore the previous behavior, then rebuild.

## Output
Write a short result record into the sprint's artifacts (`Sprint: <id>` stamped): branch, files changed and created, tests added, endpoints touched, build result, open questions.

## Constraints
- Never modify files outside the assigned repository.
- Never push or open a PR; phase 8 (PM-GPT review) owns that.
- Never report success without a build result.
