---
name: ci-release-contract
description: Verify exact-head CI and release evidence before promotion. Use for merge, release and 'CI is green' claims.
---

# ci-release-contract

## Apply when
Promotion, merge, release or any 'CI is green' claim.

## Method
1. Bind evidence to the exact head/commit and the required workflow; list required checks with their conclusions.
2. Attempted is not succeeded; skipped and cancelled are not passed.
3. If CI did not run (platform or billing), evidence is a local run of the same workflow on the exact head - say so explicitly; it never excuses a real code failure.
4. Risky releases need migration ordering, environment-specific verification and a rollback plan.
5. A new commit invalidates earlier evidence and approval.

## Required output
Table: Head | Check | Conclusion | Evidence; rollback plan.

## Do not
Reuse evidence from another head; merge or push without the project's required authority.

Typical failure modes: `references/failure-modes.md` (read only when the work hits one of them).
