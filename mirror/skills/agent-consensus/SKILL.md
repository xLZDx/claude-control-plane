---
name: agent-consensus
description: Cost-aware evidence-based specialist review for non-trivial plans/changes. Selects the minimum relevant agents, runs one independent discovery round, reopens only contested BLOCKER/MAJOR items, and optionally uses an adjudicator. Use when the operator asks for agent review or when a high-risk cross-domain decision genuinely needs independent challenge.
---

# Agent Consensus - evidence, not voting

Goal: find independent failure modes with the smallest useful roster. Agreement count is not truth; evidence is.
Launching separately billed agents needs the operator's authorization unless the session grants it; Opus is never automatic.

## Classify first (routing source: `~/.claude/agent_routing.json` -> `risk_routing`)
- R0 trivial: 0 agents. R1 focused, one domain: 1 specialist. R2 cross-file/domain: 2-4 in parallel.
- R3 high risk (money, auth/tenancy, destructive migration, security, production reliability): every specialist whose domain the change touches; domain intersection selects, not a target count.
- Never use roster size as a quality metric; if one agent can settle it with primary evidence, stop.

## Procedure
1. Recon the real scope; select by domain intersection; pass each agent only task, scope, constraints, output schema. No other agent's opinion in round 1.
2. Round 1, independent and parallel. Findings: `ID | severity | claim | evidence | failure scenario | impact | required change | acceptance test`. Verify load-bearing file:line, merge duplicates by root cause, separate fact from preference.
3. Round 2 only for contested BLOCKER/MAJOR or conflicting evidence: owning specialist plus one counter-role, on the specific disagreement. Max 2 rounds unless the operator asks or evidence is new.
4. One high-reasoning adjudicator only when serious findings remain; classify ACCEPT / MODIFY / REJECT / UNKNOWN, never manufacture consensus.
5. Evidence order: measured behavior > primary docs > reproducible test > code inference > preference > vote count.

## Output
Risk class and agents used; verified BLOCKER/MAJOR first; actionable MINOR only; rejected findings with reason; unresolved decisions; required changes and acceptance tests before GO. Do not dump transcripts.

Full original procedure, including the external second-opinion rules: `references/full-procedure.md`.
