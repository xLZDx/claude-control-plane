---
name: task-status-continue
description: Write a short task status and keep working while any item is doable. Use at every checkpoint, before any final answer, and when a prohibition (tests, checks, migrations) is in force.
---

# task-status-continue

## Apply when
At each checkpoint and before ending a turn. Also whenever a prohibition (tests, checks, migrations) is active: it blocks only that action, not development.

## Method
1. Write a status block (Russian to the operator): `DONE | DOABLE-NOW | BLOCKED`, one line per item.
2. Classify BLOCKED strictly. Allowed causes only:
   - OPERATOR: needs the operator's decision, manual action, or an operator-only action (irreversible deletion, real money, live trading).
   - EXTERNAL: needs a setting, credential, app, service or tool outside the repository that is not available (name it and the verified symptom).
   - PROHIBITED: the item itself requires a forbidden action (tests, checks, migrations).
   Anything else - uncertainty, size, "needs review", "recommend next" - is DOABLE-NOW.
3. If any DOABLE-NOW item exists, do it immediately. Do not end the turn, ask permission, or hand over recommendations.
4. A blocked dependent part is recorded and the independent parts continue.
5. Re-write the status after each batch. Stop only when every remaining item is BLOCKED with an allowed cause; then state each cause and what unblocks it.

## Required output
Status table: Item | State | Blocker class (OPERATOR/EXTERNAL/PROHIBITED) | Verified cause | Next action.
Final line: "Блокеры: <class + verified cause + what unblocks it>" for each remaining item, or "Выполнимых задач не осталось". Never phrase it as "Остановился, потому что ..." (blacklisted by the keep-going hook).
