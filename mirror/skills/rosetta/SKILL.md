---
name: rosetta
description: Workflow for Plan -> GO -> Act -> Validate -> Document, with PM Bridge durable state and hook-backed execution records.
---

# Rosetta — front door

Use Rosetta when the active project or hooks require a governed workflow for non-trivial changes.

Sequence:
1. Inspect the real repository/runtime state.
2. Create a scoped plan with verification defined before implementation.
3. Obtain the approval required by the active project contract and bind it to the current plan version.
4. Execute the approved scope.
5. Validate with real evidence and record the result.

Keep the workflow visible:
- print a readable plan with id/status/version;
- show acceptance criteria and verification;
- compare planned work with actual outcome;
- report each item as done, partial, or not done, with the remaining tail when partial.

If scope changes materially, revise the plan and refresh its approval according to the active project contract. Repository state is the final source for what actually changed.

Rosetta complements the normal project safety and permission rules; it does not replace them.

Implementation and state live in D:\Repo\pm-bridge. Read references/full-2026-10-02.md only when exact tool names, hook behavior, or historical details are needed.
