---
name: delivery-efficiency
description: The operator's canonical development workflow for all projects: docs first, code complete before tests, actual reviewer agents, one PR per sprint, short commit messages, and GPT-PM code approval before push/PR.
---

# Canonical development workflow

This skill is the detailed workflow source referenced by `C:\Users\koros\.claude\CLAUDE.md`,
`C:\Users\koros\.codex\AGENTS.md`, and `D:\Repo\AGENTS.md`. If a project process document
conflicts, apply this workflow and update the stale document; retain real product, security,
privacy, tenant-isolation, legal, data-integrity, deletion, money, and platform safeguards.

## 1. Documentation and scope

- New project: first prepare TDD, design, master plan, sprint plan with sprints and tasks (epics/gates only as documentation grouping of tasks,
  no stories), DoD, and test coverage derived from requirements/tasks. Functional-test-reviewer and e2e-runner own acceptance
  coverage. Run several actual internal-agent review rounds to consensus, fix findings, then obtain
  GPT review before implementation.
- Existing project: review the existing docs and code once to establish current state and next
  work. Make one focused local-agent review/fix pass if needed. Do not repeatedly rewrite accepted
  material.
- If product documentation is explicitly deferred, queue it for the post-release documentation
  gate. Updating these operating instructions when requested is still in scope.

## 2. Implementation and commits

- Implement the accepted plan and all code for one sprint before starting tests or checks. Do not
  run checks during coding or divert into unrelated tasks. Commit coherent changes as development
  proceeds. A sprint produces one PR.
- Commit messages are at most two sentences. No pre-commit change-record file and no link to one
  (operator 2026-10-30). Preserve commit history; do not rewrite old commits.
- After push and PR creation: update existing documents only where needed, record identified
  problems in the retrospective, and add a short PR description to the decision log.
  Documentation never blocks commit, push or merge. No new documentation after kickoff.
- Two planning levels only: sprint and tasks. Epics or gates exist only as documentation labels
  grouping tasks logically; never execution units or blockers. One task at a time; GPT-PM reviews code deltas only.
- Resolve ordinary technical/sequencing questions independently. Put nonblocking unresolved items
  in the backlog for sprint end; investigate earlier only when they block other in-scope work.

## 3. Testing after coding

- Only after every sprint story is implemented, actually launch `functional-test-reviewer` and
  `e2e-runner`. They define falsifiable acceptance criteria, author and execute focused functional
  tests, fix defects with the implementer, and repeat relevant regression cycles until green.
- Operator rule 2026-10-15 (GLOBAL): test-writing agents (`tdd-guide` as test-engineer,
  `performance-optimizer` as data-engineer/perf-tuning, `e2e-runner`, `functional-test-reviewer`) write detailed
  functional scripts for every task and run the COMPLETE set of tests they wrote (all files, not a
  sample) after each task, and everything they wrote once more after the last task. The
  coordinator never runs tests itself; repo-wide legacy suites/lint/CI stay prohibited.
- Never weaken tests to manufacture a pass. Record exact commands/results. Unavailable runtime or
  provider evidence is `NOT_RUN` with its concrete dependency or error.
- Required test suites are selected from accepted tasks and gates, then authored and executed by
  `functional-test-reviewer` and `e2e-runner` after coding completes. Delegate other requested
  verification to the relevant specialist. Record exact commands, revisions, results and limits.

## 4. Specialist review and GPT gate

- After functional/E2E results, launch separate actual reviewer agents only for roles relevant to
  the changed risks. Typical roles include `silent-failure-hunter`, `database-reviewer`, `architect`,
  `code-explorer`, `build-error-resolver`, `refactor-cleaner`, `doc-updater`, `python-reviewer`, and
  `code-reviewer`. Add other specialists as needed. Reviewer specs/checklists do not count as an
  agent run; in-chat role simulation does not substitute for launching agents.
- Freeze the exact diff/head and provide it to reviewers. Reach evidence-based consensus; fix every
  valid BLOCKER/MAJOR in one focused batch; then targeted recheck those findings and direct
  regressions. Backlog unrelated MINOR/INFO items.
- **Allowed reviewer models only:** Claude Sonnet 5.5 at medium effort or GPT-5.6 Luna at low or
  medium effort. **GPT-5.6 Sol is prohibited for reviews.** Never substitute another model. If no
  allowed model is actually available, do not launch the reviewer under a different model; state
  the exact limitation and continue independent work. Report the model/effort actually used.
- After functional evidence and reviewer consensus, send GPT the exact final code diff, test
  evidence, reviewer results, and commit/head identity. Record the correlated reply. Push and open
  the sprint PR only after GPT approves that exact code; any later code change requires a new
  approval.

## 5. Closure and next sprint

- Close the code gate when code and required focused functional evidence are green and no valid
  code BLOCKER/MAJOR remains. Stale documentation, unnecessary governance, and process gates that
  contradict this workflow do not block code closure. Required reviewer consensus and final GPT
  approval still apply before push/PR. Real product/security/privacy/legal/data-integrity/platform
  gates remain in force.
- When a sprint enters test/review, delegate next-sprint documentation review and implementation
  preparation to available reviewers in parallel. Do not let that work delay current-sprint fixes,
  reviews, GPT approval, or delivery.
- Report the final code, actual tests, actual agent/model runs, exact GPT verdict, delivery state,
  and each remaining item as complete, blocked by a named dependency, or out of scope.
