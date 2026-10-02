---
name: observability-contract
description: Make critical behavior diagnosable in production. Use when adding or reviewing logging, metrics, tracing, alerts or runbooks.
---

# observability-contract

## Apply when
Behavior that must be diagnosable in production: logs, metrics, traces, alerts, runbooks.

## Method
1. Structured logs at failure-prone boundaries with correlation/request ids; no secrets or PII.
2. Metrics: rate, errors, latency, saturation, queue depth and age of the oldest item.
3. Traces across async hops; detection of stuck work, not only errors.
4. Operationally critical failures get an alert with an owner and a runbook.
5. Verify by forcing a failure and locating it from telemetry alone.

## Required output
Signal table: failure -> signal -> alert -> owner/runbook; gaps.

## Do not
Log secrets/PII; alert on noise; call coverage 'observable' without the forced-failure check.

Typical failure modes: `references/failure-modes.md` (read only when the work hits one of them).
