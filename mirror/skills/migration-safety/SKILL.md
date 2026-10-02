---
name: migration-safety
description: Design restartable, observable and reversible data/schema migrations. Use for backfills, schema changes and format conversions.
---

# migration-safety

## Apply when
Data or schema migrations, backfills and format conversions.

## Method
1. Expand -> backfill -> verify -> contract; never combine them in one step.
2. Batch with explicit, resumable checkpoint state; reruns are idempotent.
3. Check locking and online-ness; plan for partial deployment (old and new code together).
4. Verification queries (counts, checksums, sampling) before and after; dry-run on a copy.
5. Prove the rollback or restore path before running; expose progress and rate.

## Required output
Runbook: preconditions, steps, verification queries, abort/rollback, ownership.

## Do not
Run destructive steps (drop, truncate, delete) without separate operator approval and a proven restore path.

Typical failure modes: `references/failure-modes.md` (read only when the work hits one of them).
