---
name: db-change-contract
description: Review database changes for integrity, concurrency and deployability. Use for schema, SQL, migration, query-plan and transaction changes.
---

# db-change-contract

## Apply when
Schema/DDL, SQL, migrations, indexes, transactions, locks or row-level security.

## Method
1. Invariants are expressed as constraints (PK, FK, unique, check, not null), not only in application code.
2. Multi-statement invariants: transaction scope, isolation level, lock order, long-lock risk.
3. Query plans (EXPLAIN) at representative cardinality; account for index write cost.
4. Rollout is backward compatible while old and new code overlap (expand/contract).
5. Check RLS/permissions and backfill volume; tie every performance claim to a plan or workload.

## Required output
Findings with evidence (DDL/SQL/plan) and a rollout order.

## Do not
Judge performance without a plan; accept a migration with no lock or rollback analysis; trust ORM defaults for concurrency.

Typical failure modes: `references/failure-modes.md` (read only when the work hits one of them).
