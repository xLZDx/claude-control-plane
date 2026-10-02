---
name: reliability-contract
description: Review resilience and recovery of production behavior. Use when retries, timeouts, queues, workers, restart or partial failure change.
---

# reliability-contract

## Apply when
Retries, timeouts, queues, workers, async delivery, restart/recovery or partial-failure semantics.

## Method
1. Every external call has a timeout; retries are bounded with backoff and jitter and apply only to idempotent operations.
2. At-least-once delivery means idempotency keys or deduplication.
3. For each step ask what state remains if it fails, and who completes or rolls back.
4. Queues: poison messages, dead-letter handling, backpressure, bounded concurrency.
5. Kill the process between each pair of steps; check graceful shutdown and resource exhaustion (memory, fds, connections, disk).
6. Silent loss is a defect: failures must be operator-visible.

## Required output
Failure matrix: step x failure -> resulting state -> recovery -> test.

## Do not
Add retries to non-idempotent writes; swallow errors to stay up; call a design resilient without a crash-window analysis.

Typical failure modes: `references/failure-modes.md` (read only when the work hits one of them).
