#!/usr/bin/env python3
"""Writes the 20 global engineering skills: a thin SKILL.md front door + references/failure-modes.md.

Idempotent. Never deletes. Supersedes seed_engineering_skills.py (one-shot stubs).
    C:\\Python314\\python.exe build_skills.py [--dry-run]
"""
from __future__ import annotations

import sys
from pathlib import Path

SKILLS = Path.home() / ".claude" / "skills"

S: dict[str, dict] = {}


def skill(name, description, use, method, output, avoid, failures):
    S[name] = dict(description=description, use=use, method=method, output=output, avoid=avoid, failures=failures)


skill(
    "repo-recon",
    "Build a fast, deterministic repository context before reasoning. Use before design, review or edits in an unfamiliar repo or area.",
    "Starting work in a repo/area you have not read this session, before any design or verdict.",
    [
        "Resolve `git rev-parse --show-toplevel`, branch, HEAD and `git status --short`; note linked worktrees and files that are already dirty (never overwrite those blind).",
        "Read the nearest instruction files (CLAUDE.md, AGENTS.md, `.claude/rules`) and the project's source-of-truth index; find the pinned interpreter/toolchain and the canonical test command.",
        "Locate entrypoints, module boundaries, tests, CI definitions and migrations; find the nearest existing analogue of the requested change.",
        "Record unknowns explicitly instead of guessing.",
    ],
    "Fact sheet: root / branch / head / dirty files; stack and commands; boundaries; analogue path; unknowns. Facts and paths only.",
    "Propose architecture or verdicts during recon; infer facts from sibling repos that share a parent folder; trust a status doc over git/CI state.",
    [
        "Bare `python`/`pytest` resolves to a sibling project's venv - use the project-pinned interpreter.",
        "Truncated command output read as absence - re-run with a narrower query.",
        "A status document claims 'done' while git/CI says otherwise - git wins.",
        "A worktree has its own `.claude` copy - it is not a separate project.",
        "Generated or vendored directories dominate search results - exclude them before concluding.",
    ],
)
skill(
    "implementation-workflow",
    "Implement scoped changes with minimal compatible diffs and evidence. Use for an approved feature, fix or refactor whose requirements are known.",
    "Implementing an approved, scoped change (feature, bug fix, refactor).",
    [
        "Restate acceptance criteria as checkable statements; read callers, tests and the existing contract first.",
        "Pick the nearest working pattern; make the smallest compatible diff; no drive-by refactors.",
        "Bug fix: write the regression test first and see it fail for the right reason. Behavior change: add behavior-level verification.",
        "Run targeted checks, then the project's required gate; inspect `git diff` for stray edits and EOL/encoding changes.",
        "Report exactly what ran and what was not verified.",
    ],
    "What changed (paths); evidence (exact commands + results); unverified items; follow-ups left out of scope.",
    "Delete files/data/resources, rewrite history, commit/push or widen scope without explicit approval; call a change done on a green but unrelated suite.",
    [
        "Fixing the symptom at the call site while the root cause stays in the shared helper.",
        "A test that passes before and after the fix (it proves nothing).",
        "Scripted writes that flip CRLF/LF or re-encode the file - diff after every scripted write.",
        "Editing a file another session or agent is concurrently changing - inspect the real worktree first.",
    ],
)
skill(
    "technical-design",
    "Produce implementation-ready technical designs before non-trivial changes. Use when a change crosses modules, data or contracts.",
    "A non-trivial change that crosses files, data ownership or contracts and needs agreement before coding.",
    [
        "State problem, constraints and current behavior with file references.",
        "List real options (at least two when non-trivial) and the decisive criterion between them.",
        "Specify the chosen design: interfaces, data/state ownership, concurrency, failure modes, compatibility, migration and rollback.",
        "Map the verification plan to the risks; list open decisions with an owner.",
    ],
    "One-page note: Goal, Non-goals, Design, Failure modes, Rollout/rollback, Test plan, Unknowns.",
    "Invent requirements; hide uncertainty; design beyond the approved scope.",
    [
        "Designing a new mechanism parallel to an existing working one.",
        "Failure modes written only for the happy dependency set (no partial failure, no restart).",
        "A migration plan with no rollback or no verification query.",
        "'TBD' hidden inside the interface definition instead of listed as an open decision.",
    ],
)
skill(
    "architecture-contract",
    "Review system architecture with consistent boundaries and operational criteria. Use for boundary, ownership, consistency or scalability decisions.",
    "System- or module-level review/design: ownership, dependency direction, consistency, failure domains.",
    [
        "Map who owns each piece of state (single writer) and where invariants are enforced.",
        "Check dependency direction against existing layering and CI-enforced rules; CI rules outrank opinion.",
        "Check consistency and concurrency: ordering, idempotency, transactions, retries.",
        "Check failure domains / blast radius and scalability (measured, or a stated assumption).",
        "Check deployability, migration and rollback. Prefer existing boundaries; a new abstraction needs evidence of at least two real users.",
    ],
    "Findings as: severity | basis | claim | evidence | failure scenario | required change | acceptance test.",
    "Restyle or propose rewrites for taste; duplicate what CI already enforces; cite a pattern name instead of a concrete failure.",
    [
        "Two writers for one fact with no reconciliation.",
        "A synchronous call chain that couples failure domains the design says are independent.",
        "'Scalable' claimed without a number or an assumption.",
        "Abstraction introduced for a single caller.",
    ],
)
skill(
    "functional-testing",
    "Design or review behavioral tests that can falsify the changed contract. Use when writing tests or judging whether tests prove a change.",
    "Writing or reviewing behavior tests for a changed contract.",
    [
        "Name the contract: inputs -> observable outcome and state change.",
        "Cover the matrix that applies: happy, alternate, boundary, invalid, permission, repeated/retry, concurrent, state after restart.",
        "Every assertion must fail if the behavior breaks - mutate or revert the code (mentally or for real) to check.",
        "Keep tests isolated: no order dependence, no shared mutable fixtures, deterministic clocks and ids.",
        "Use the real boundary where a mock would hide the defect.",
    ],
    "Coverage map contract -> tests; ranked gaps; for each weak assertion the mutation that survives it.",
    "Count 'did not raise' as proof; assert implementation details instead of outcomes; accept coverage percentage as evidence.",
    [
        "Mock returns exactly what the code under test expects - the test only proves the mock.",
        "Assertion on a log line or call count instead of the persisted outcome.",
        "Fixture shared between tests so one failure cascades or hides.",
        "Time/randomness not pinned - flaky and unfalsifiable.",
    ],
)
skill(
    "e2e-testing-contract",
    "Verify critical user journeys through real integration boundaries. Use when creating, running or stabilizing end-to-end tests.",
    "End-to-end journeys through real browser/API/DB boundaries, and failing or flaky E2E suites.",
    [
        "Choose a few high-value journeys (money, auth, data loss, core flow) over broad coverage.",
        "Use real boundaries with seeded deterministic data and isolated state per test.",
        "Wait on observable conditions, never fixed sleeps.",
        "Classify each failure with artifacts (trace, screenshot, log, request ids): product bug / test defect / environment / flake.",
        "Flake: reproduce N times; quarantine only with an owner, a ticket and an expiry. Verify cleanup.",
    ],
    "Journey list; run evidence (command, N runs, pass rate); classification of every failure.",
    "Retry until green; delete or skip a failing test to pass; widen waits to mask a product race.",
    [
        "Tests share an account/tenant and corrupt each other.",
        "Selectors bound to styling instead of roles/test ids.",
        "Network or clock nondeterminism treated as 'flaky browser'.",
        "Green run on a stale build or the wrong environment.",
    ],
)
skill(
    "verification-contract",
    "Define evidence required before a change can be called verified. Use before saying fixed/done/pass and when auditing someone else's verification claim.",
    "Before declaring fixed/done/pass, and when reviewing a verification claim.",
    [
        "Map each claim to an evidence class that matches its risk: static, unit, integration, E2E, migration dry-run, runtime/log.",
        "Record exact command, scope, result and git head or artifact id.",
        "Evidence must be able to fail: confirm a broken behavior would turn it red.",
        "State precisely what is not verified. Attempted is not succeeded; skipped/cancelled is not passed.",
        "Never infer absence from truncated output; a reviewer's claim is not your measurement.",
    ],
    "Table: Claim | Evidence | Command/artifact | Head | Result | Not covered.",
    "Cite a green unrelated suite; weaken the claim silently; report a stronger guarantee than the evidence proves.",
    [
        "Suite green because the changed path is excluded or mocked away.",
        "Evidence gathered on an earlier head than the one being approved.",
        "Harness broken in a way that imitates the wanted result - pre-flight the baseline first.",
        "'Looks fine' from reading code where a command would have settled it.",
    ],
)
skill(
    "performance-testing",
    "Measure performance before optimizing and guard regressions. Use for performance claims, hot-path changes and benchmark/profile work.",
    "A performance claim, a regression risk or a hot-path change.",
    [
        "Define workload and SLO from the product budget (percentiles, throughput, memory, I/O).",
        "Baseline before changing anything on representative data; separate warm from cold; same machine.",
        "Profile to find the dominant cost (algorithm, N+1, copies, locks, serialization) before proposing a fix.",
        "Re-measure after with variance (N runs, report spread). Test saturation, soak and recovery for critical paths.",
        "Guard with a regression benchmark or threshold in CI where it is stable.",
    ],
    "Baseline vs after table (percentile, sample size, method); every claim labelled MEASURED or INFERRED.",
    "Optimize cold code; claim a speedup from one noisy run; trade correctness or ordering for speed without tests.",
    [
        "Benchmark on a tiny dataset that hides the quadratic term.",
        "Caching added with no invalidation story.",
        "Averages reported where the tail is the problem.",
        "Optimization measured on a developer machine under unrelated load.",
    ],
)
skill(
    "security-evidence-contract",
    "Review reachable security risk with evidence and realistic actor paths. Use on touched trust boundaries or explicit security review.",
    "A touched trust boundary (auth, tenancy, input parsing, files, network egress, secrets, CI) or an explicit security review.",
    [
        "For each finding name the actor, entry point, trust boundary crossed, sensitive sink and impact.",
        "Check authn/authz, tenant/object isolation (IDOR), injection (SQL/command/template), SSRF and DNS rebinding, secrets in code/logs/artifacts, file/archive/XML import, deserialization, supply chain (pins, lockfiles, CI permissions).",
        "Trace or reproduce a reachable path; rate severity by reachability x impact.",
    ],
    "Finding: attacker precondition, exact path (file:line), impact, fix, regression test.",
    "Report unreachable patterns as high severity; paste secrets into reports; run exploits against live systems without authorization.",
    [
        "Authorization checked on the list endpoint but not on the item/download endpoint.",
        "Tenant id taken from the request body instead of the session.",
        "Input validated after the dangerous operation.",
        "Scanner output pasted as findings with no reachability analysis.",
    ],
)
skill(
    "reliability-contract",
    "Review resilience and recovery of production behavior. Use when retries, timeouts, queues, workers, restart or partial failure change.",
    "Retries, timeouts, queues, workers, async delivery, restart/recovery or partial-failure semantics.",
    [
        "Every external call has a timeout; retries are bounded with backoff and jitter and apply only to idempotent operations.",
        "At-least-once delivery means idempotency keys or deduplication.",
        "For each step ask what state remains if it fails, and who completes or rolls back.",
        "Queues: poison messages, dead-letter handling, backpressure, bounded concurrency.",
        "Kill the process between each pair of steps; check graceful shutdown and resource exhaustion (memory, fds, connections, disk).",
        "Silent loss is a defect: failures must be operator-visible.",
    ],
    "Failure matrix: step x failure -> resulting state -> recovery -> test.",
    "Add retries to non-idempotent writes; swallow errors to stay up; call a design resilient without a crash-window analysis.",
    [
        "Retry storm after a dependency outage (no jitter, no budget).",
        "Message acknowledged before the side effect is durable.",
        "Latest-attempt selection wrong after a retry.",
        "Shutdown drops in-flight work with no record.",
    ],
)
skill(
    "observability-contract",
    "Make critical behavior diagnosable in production. Use when adding or reviewing logging, metrics, tracing, alerts or runbooks.",
    "Behavior that must be diagnosable in production: logs, metrics, traces, alerts, runbooks.",
    [
        "Structured logs at failure-prone boundaries with correlation/request ids; no secrets or PII.",
        "Metrics: rate, errors, latency, saturation, queue depth and age of the oldest item.",
        "Traces across async hops; detection of stuck work, not only errors.",
        "Operationally critical failures get an alert with an owner and a runbook.",
        "Verify by forcing a failure and locating it from telemetry alone.",
    ],
    "Signal table: failure -> signal -> alert -> owner/runbook; gaps.",
    "Log secrets/PII; alert on noise; call coverage 'observable' without the forced-failure check.",
    [
        "Errors logged without an id that joins them to the request.",
        "Metric counts successes only, so a stall looks healthy.",
        "Alert exists but nobody owns it.",
        "High-cardinality labels that take down the metrics store.",
    ],
)
skill(
    "db-change-contract",
    "Review database changes for integrity, concurrency and deployability. Use for schema, SQL, migration, query-plan and transaction changes.",
    "Schema/DDL, SQL, migrations, indexes, transactions, locks or row-level security.",
    [
        "Invariants are expressed as constraints (PK, FK, unique, check, not null), not only in application code.",
        "Multi-statement invariants: transaction scope, isolation level, lock order, long-lock risk.",
        "Query plans (EXPLAIN) at representative cardinality; account for index write cost.",
        "Rollout is backward compatible while old and new code overlap (expand/contract).",
        "Check RLS/permissions and backfill volume; tie every performance claim to a plan or workload.",
    ],
    "Findings with evidence (DDL/SQL/plan) and a rollout order.",
    "Judge performance without a plan; accept a migration with no lock or rollback analysis; trust ORM defaults for concurrency.",
    [
        "Check-then-insert race instead of a unique constraint.",
        "Index added on a hot write table with no write-cost estimate.",
        "Column dropped in the same release that stops writing it.",
        "RLS bypassed by a privileged connection used for ordinary requests.",
    ],
)
skill(
    "migration-safety",
    "Design restartable, observable and reversible data/schema migrations. Use for backfills, schema changes and format conversions.",
    "Data or schema migrations, backfills and format conversions.",
    [
        "Expand -> backfill -> verify -> contract; never combine them in one step.",
        "Batch with explicit, resumable checkpoint state; reruns are idempotent.",
        "Check locking and online-ness; plan for partial deployment (old and new code together).",
        "Verification queries (counts, checksums, sampling) before and after; dry-run on a copy.",
        "Prove the rollback or restore path before running; expose progress and rate.",
    ],
    "Runbook: preconditions, steps, verification queries, abort/rollback, ownership.",
    "Run destructive steps (drop, truncate, delete) without separate operator approval and a proven restore path.",
    [
        "Backfill restarts from zero after a crash.",
        "Verification counts rows but not content.",
        "Rollback assumes data the migration already overwrote.",
        "Migration holds a table lock during peak traffic.",
    ],
)
skill(
    "integration-contract",
    "Review external API, connector and message-boundary behavior. Use for third-party APIs, webhooks, connectors and queues.",
    "External APIs, connectors, webhooks and message boundaries.",
    [
        "Define auth (scopes, rotation), versioning and compatibility, timeouts, retry/idempotency, pagination and rate-limit handling.",
        "Handle malformed, partial, duplicate and out-of-order payloads; define behavior during provider outage.",
        "Preserve provenance across retries and replays.",
        "Contract tests with recorded fixtures plus one live-sandbox smoke where permitted; secrets only via env/secret store.",
    ],
    "Contract table per endpoint/message, failure behavior and the tests that pin it.",
    "Trust the provider's documented schema; assume exactly-once delivery; log credentials or tokens.",
    [
        "Pagination cursor lost on retry, producing gaps or duplicates.",
        "Rate-limit response treated as a hard failure and retried instantly.",
        "Webhook handled before signature verification.",
        "Provider field renamed silently - unknown fields dropped with no alarm.",
    ],
)
skill(
    "ci-release-contract",
    "Verify exact-head CI and release evidence before promotion. Use for merge, release and 'CI is green' claims.",
    "Promotion, merge, release or any 'CI is green' claim.",
    [
        "Bind evidence to the exact head/commit and the required workflow; list required checks with their conclusions.",
        "Attempted is not succeeded; skipped and cancelled are not passed.",
        "If CI did not run (platform or billing), evidence is a local run of the same workflow on the exact head - say so explicitly; it never excuses a real code failure.",
        "Risky releases need migration ordering, environment-specific verification and a rollback plan.",
        "A new commit invalidates earlier evidence and approval.",
    ],
    "Table: Head | Check | Conclusion | Evidence; rollback plan.",
    "Reuse evidence from another head; merge or push without the project's required authority.",
    [
        "Required check missing from branch protection, so 'all green' hides it.",
        "Workflow green on a path filter that excluded the changed files.",
        "Approval recorded for head A, merged head B.",
        "Different dependency versions locally than in CI.",
    ],
)
skill(
    "git-worktree-ops",
    "Operate safely across repositories and worktrees. Use before editing when several checkouts or concurrent sessions exist.",
    "Any edit or git operation where worktrees, sibling projects or concurrent sessions exist.",
    [
        "Resolve `git rev-parse --show-toplevel` and `--git-common-dir`, branch, HEAD and dirty files before editing.",
        "Assume another session may be editing: never stage or commit blind - inspect the diff of exactly the intended paths.",
        "Verify the exact outbound range before any push; one child project per session.",
        "A worktree's `.claude` copy is not a separate agent set; do not index it as one.",
    ],
    "Pre/post snapshot (branch, head, status) and the exact paths touched.",
    "Run `git reset --hard`, `git clean -f*`, force-push, delete branches/refs or remove worktrees without separate operator approval; remove a worktree before checking for junctions that point outside it.",
    [
        "Working in the main checkout while the real work lives in a linked worktree.",
        "`git add -A` sweeping in another session's files.",
        "Worktree removal following a junction into live data.",
        "Same branch checked out in two places, one silently stale.",
    ],
)
skill(
    "ux-design-contract",
    "Review product and UX behavior across the complete user journey. Use when user flows, states or information hierarchy change.",
    "User-facing flows, screens and states.",
    [
        "Trace discoverability and hierarchy; walk the happy path and the alternates.",
        "Cover loading, empty, error, partial, success, destructive-confirm, recovery/undo and offline states.",
        "Check copy and trust cues (what will happen, what happened), consistency with existing patterns, responsive behavior, keyboard and focus order.",
        "Judge task completion, not appearance.",
    ],
    "Journey walk-through with findings per state; severity by task-blocking impact.",
    "Demand redesign without a stated user impact; skip error and empty states.",
    [
        "Destructive action with no confirmation or undo.",
        "Error message that does not say what to do next.",
        "State lost on navigation or refresh.",
        "Pattern differs from the rest of the product for no reason.",
    ],
)
skill(
    "a11y-contract",
    "Review accessibility as task completion, not checklist theater. Use on touched UI, forms, navigation and dynamic content.",
    "Touched UI: forms, navigation, dialogs, dynamic content, media.",
    [
        "Keyboard reachability, focus order and visible focus; no traps.",
        "Semantics, roles, accessible names and labels.",
        "Contrast and reflow at 200-400% zoom; touch target size; reduced motion.",
        "Screen-reader announcement for dynamic updates and errors; locale, RTL and long strings.",
        "Error identification and recovery.",
    ],
    "Barrier list: who is blocked, which task, criterion (WCAG), fix, how to verify (keyboard walk, screen reader, axe).",
    "Treat a passing automated scan as proof of task completion; list barriers without user impact.",
    [
        "Custom control with no role/name/state.",
        "Focus not returned after a dialog closes.",
        "Error shown only by colour.",
        "Live region missing, so a result change is silent.",
    ],
)
skill(
    "context-memory-hygiene",
    "Keep instruction and memory context compact, current and correctly scoped. Use when editing CLAUDE.md, AGENTS.md, memory, agent or skill prompts.",
    "Editing CLAUDE.md, AGENTS.md, memory files, agent or skill prompts.",
    [
        "Global files hold only universal rules; project facts stay project-local; one rule lives in one place (link, do not copy).",
        "Keep durable decisions and canonical pointers, not status history; mark superseded text and move it to a dated history file.",
        "Budgets: global CLAUDE.md <= 6k tokens, project CLAUDE.md + AGENTS.md <= 4k. Procedures go to skills, knowledge to references.",
        "Verify with `agentctl.py --strict`.",
    ],
    "Before/after token counts, what moved where, lint result.",
    "Delete history; duplicate a rule across memory, CLAUDE.md and agents; store branch HEADs or pass counts in memory.",
    [
        "A global rule that only applies to one project.",
        "Status narration accumulating in the memory index.",
        "Two files stating the same rule with slightly different wording.",
        "Compaction that drops a dangerous invariant - diff the rule list, not the line count.",
    ],
)
skill(
    "agent-evaluation",
    "Measure agent quality and token efficiency with regression evidence. Use when changing agent prompts, routing or rosters, or claiming token savings.",
    "Changing an agent prompt, routing rule or roster, or claiming a token saving.",
    [
        "Build fixtures from real past defects with expected severity (seeded defects).",
        "Run the roster before and after; record tokens/run, latency, confirmed BLOCKER/MAJOR, false positives, duplicates, unique findings, escaped seeded defects, unnecessary invocations.",
        "Accept a change only if recall on seeded defects does not drop; prefer the cheapest roster that keeps detection.",
        "Harness and fixtures live under `control-plane/eval/`.",
    ],
    "Metrics before/after and a keep/revert decision.",
    "Measure by the number of agents run; slim a prompt without a recall check; start separately billed model runs without operator authorization.",
    [
        "Fixture leaks the answer in its file names or comments.",
        "Judging a reviewer by volume of findings instead of confirmed ones.",
        "Comparing runs with different effort or turn budgets.",
        "One run treated as a result - variance not measured.",
    ],
)


def render(name: str, d: dict) -> tuple[str, str]:
    steps = "\n".join(f"{i}. {m}" for i, m in enumerate(d["method"], 1))
    main = (
        f"---\nname: {name}\ndescription: {d['description']}\n---\n\n# {name}\n\n"
        f"## Apply when\n{d['use']}\n\n## Method\n{steps}\n\n## Required output\n{d['output']}\n\n"
        f"## Do not\n{d['avoid']}\n\n"
        f"Typical failure modes: `references/failure-modes.md` (read only when the work hits one of them).\n"
    )
    ref = f"# {name}: failure modes\n\nLoad on demand. Each line is a defect class seen in practice.\n\n" + "\n".join(f"- {f}" for f in d["failures"]) + "\n"
    return main, ref


def main() -> int:
    dry = "--dry-run" in sys.argv
    for name, d in S.items():
        main_txt, ref_txt = render(name, d)
        sdir = SKILLS / name
        if not sdir.is_dir():
            print(f"skip {name}: skill directory missing")
            continue
        if not dry:
            (sdir / "references").mkdir(exist_ok=True)
            (sdir / "SKILL.md").write_text(main_txt, encoding="utf-8", newline="\n")
            (sdir / "references" / "failure-modes.md").write_text(ref_txt, encoding="utf-8", newline="\n")
        print(f"{name}: SKILL ~{len(main_txt)//4} tok, ref ~{len(ref_txt)//4} tok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
