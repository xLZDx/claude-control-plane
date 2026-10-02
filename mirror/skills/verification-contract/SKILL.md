---
name: verification-contract
description: Define evidence required before a change can be called verified. Use before saying fixed/done/pass and when auditing someone else's verification claim.
---

# verification-contract

## Apply when
Before declaring fixed/done/pass, and when reviewing a verification claim.

## Method
1. Map each claim to an evidence class that matches its risk: static, unit, integration, E2E, migration dry-run, runtime/log.
2. Record exact command, scope, result and git head or artifact id.
3. Evidence must be able to fail: confirm a broken behavior would turn it red.
4. State precisely what is not verified. Attempted is not succeeded; skipped/cancelled is not passed.
5. Never infer absence from truncated output; a reviewer's claim is not your measurement.

## Required output
Table: Claim | Evidence | Command/artifact | Head | Result | Not covered.

## Do not
Cite a green unrelated suite; weaken the claim silently; report a stronger guarantee than the evidence proves.

Typical failure modes: `references/failure-modes.md` (read only when the work hits one of them).
