---
name: technical-design
description: Produce implementation-ready technical designs before non-trivial changes. Use when a change crosses modules, data or contracts.
---

# technical-design

## Apply when
A non-trivial change that crosses files, data ownership or contracts and needs agreement before coding.

## Method
1. State problem, constraints and current behavior with file references.
2. List real options (at least two when non-trivial) and the decisive criterion between them.
3. Specify the chosen design: interfaces, data/state ownership, concurrency, failure modes, compatibility, migration and rollback.
4. Map the verification plan to the risks; list open decisions with an owner.

## Required output
One-page note: Goal, Non-goals, Design, Failure modes, Rollout/rollback, Test plan, Unknowns.

## Do not
Invent requirements; hide uncertainty; design beyond the approved scope.

Typical failure modes: `references/failure-modes.md` (read only when the work hits one of them).
