---
name: frontend-engineer
description: Implement, modify, refactor, fix or undo changes in a frontend application using the repository's own UI stack and component patterns. Use for UI stories in SDLC phase 6. Self-contained: needs no team workspace and no external connectors.
---

# frontend-engineer

## Apply when
A UI story is approved, its acceptance criteria are known, and the screens/states come from a UI design (see `ui-design-contract`) or an equivalent description.

## Method
1. Verify the branch (`git branch --show-current`) and continue existing work; do not create a branch or redo finished work.
2. Detect the frontend stack from the repository (package manifest, framework config, component library). Read the nearest existing components and copy their structure, naming, state handling and styling approach.
3. Use the project's established UI library and design tokens; do not introduce a second one.
4. Implement every state from the design: loading, empty, error, success, and keyboard/focus behavior. Call backend APIs exactly as contracted.
5. Write component or unit tests for new behavior; the test agents run them (and any end-to-end journeys), not the author.
6. Build and lint; if they fail, diagnose the root cause and fix it (maximum 3 attempts, then report).
7. For undoing a change: read `git log` and `git diff`, revert cleanly, rebuild.

## Output
Write a short result record into the sprint's artifacts (`Sprint: <id>` stamped): branch, files changed and created, tests added, build result, open questions.

## Constraints
- Never modify files outside the assigned repository.
- Never push or open a PR; phase 8 (PM-GPT review) owns that.
- Never report success without a build result.
