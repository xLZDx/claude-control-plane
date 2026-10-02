# Development Environment + AI Control Plane Remediation - Status 2026-10-02

## Verdict

**PASS WITH DEFERRED P2.** Every P0/P1 item that can be done without deletion or operator-only authority is implemented and
mechanically verified. Nothing was deleted, committed or pushed. No external AI (Codex, ChatGPT, GPT-PM, other Claude sessions)
and no subagent was launched during this run; all reviewer roles were performed by the orchestrating session.

What this program did NOT achieve, stated plainly: it does not lower tokens per agent run. Global agent prompt bytes grew ~5%
(11 102 -> 11 635 tokens) because skills are now preloaded through `skills:` frontmatter. The measured wins are elsewhere:
hook latency (-84%), always-on context (global CLAUDE.md 36 898 -> 3 797 tokens), routing precision (offline eval 15/15),
a 83 KB memory note cut to 4.5 KB, and project isolation (no project agents in workspace scope).

## What changed (this run, on top of the earlier agent's work)

| Area | Change |
|---|---|
| Lint | `control-plane/agentctl.py` rewritten (v3): fails on model/effort/turn violations, unresolved or deprecated routes, duplicate names, non-agent files in `agents/`, workspace leaks, dangling `skills:`, oversized contexts, missing gate; separates canonical / worktree / temporary / historical |
| Gate | `hooks/agent_model_gate.py` rewritten: Sonnet >= 5.5 only (alias or full id), Opus never automatic (no consent receipt exists -> fail closed), invalid effort, `deprecated` agents, data-driven path rules, fail-closed on malformed payload/rules; fixed a UTF-16-with-BOM decoding defect |
| Routing | `agent_routing.json`: `risk_routing` (R0-R3, effort tiers T1-T4, per-agent tier), `cpp-reviewer` slot disabled, 3 stale stack profiles marked historical |
| Agents | effort/maxTurns re-tiered for 28 global agents (max turns 25 -> 20 for the executor, none > 25); `skills:` wired for 27 global + 49 project agents; project budgets re-applied (the earlier script had 9 policy names that matched no file, so the RQDO tenancy and privacy auditors and 6 Fitness clinical roles had silently fallen back to the default tier) |
| Skills | 20 global engineering skills rewritten from ~90-token stubs to 230-310 token front doors + `references/failure-modes.md`; `agent-consensus` / `codex-consensus` split into thin front door + verbatim `references/full-procedure.md` |
| RQDO | 16 workspace copies archived (moved) to `D:\Repo\.claude\archive\rqdo-workspace-agent-copies-2026-10-02\`; `sync-rqdo-workspace.ps1` agent sync made opt-in (`-IncludeAgents`) so it cannot re-create them or delete anything |
| PDCC | 9 legacy duplicate reviewers marked `deprecated: true` + `superseded_by`; `USAGE_POLICY.md` moved from `agents/` to `.claude/references/` (it is not an agent definition) |
| Ferma | CLAUDE.md 4 226 -> ~1 150 tokens by moving the gate chronology verbatim to `.claude/references/HISTORY_2026-08-gates.md` |
| Hooks | all 18 Python hook commands run with `-s` (see Hook audit) |
| Memory | 37 child-project memory files sharded into `projects/D--Repo-<project>/memory/`; 83 KB go-gate note split; old `D:\test 2` memory marked historical |
| Eval | `control-plane/eval/` (router, scorer, 15 seeded-defect fixtures, README) + `tests/test_eval.py` |
| Trust | 2 stale Codex trust entries removed (backup kept) |
| Contract | global CLAUDE.md: +4 lines (risk_routing/deprecation, test commands, `-s` hook flag, project-agent scope, memory scope) |

## Model policy

Canonical: `C:\Users\koros\.claude\control-plane\model_policy.json`. Automatic agents: `sonnet` alias, minimum Sonnet 5.5, a newer Sonnet
is accepted. Effort low/medium/high/xhigh by risk (default medium). Opus: never automatic, per-run operator consent only, `high` only, `xhigh` forbidden.
Haiku/Fable/lower denied. Enforced in three places: `settings.json` (`model`, `CLAUDE_CODE_SUBAGENT_MODEL`, Opus `modelSettings`), the PreToolUse `Agent` hook, and `agentctl.py --strict`.
No Opus consent-token mechanism exists, so the gate denies every explicit Opus request (fail closed); an operator who wants Opus runs it manually (`/model`).
Real inventory: 0 runnable non-Sonnet declarations; 3 historical non-runnable `opus` declarations in `ivan-ai-company` (immutable snapshot, see below).

## Canonical agent inventory

178 canonical definitions (28 global, 150 project) of which 169 runnable and 9 deprecated (PDCC legacy aliases); 3 historical (`ivan-ai-company`).
All 28 global agents have description (trigger), tools, model, effort, maxTurns <= 20, effort tier in `risk_routing`, and skills. Per-project counts:
`PROJECT_AI_COMPONENTS.json`. Registry: `C:\Users\koros\.claude\control-plane\agent_registry.json` (+ `GLOBAL_AGENTS.json`).

## Canonical skill inventory

92 canonical (28 global, 64 project), 9 historical. Registry: `skill_registry.json` (+ `GLOBAL_SKILLS.json`), each with tokens, reference count and `agents_using_it`.
Remaining lint warnings (29, all P2): 27 domain skills above 800 tokens without `references/` (Fitness 5, Virtual_marketing_company 10, db-test-tool-analysis 6, ERP 4, AI trading 1, PDCC 1) and 2 `*.agent.md` file names in db-test-tool-analysis.

## Worktree counts (not independent agent sets)

48 linked worktrees + 3 temporary copies hold 1 431 agent definitions and 73 skill definitions; they are counted in `all_discovered_*` only
(`worktree_summary.json`). Discovered total 1 612 agents / 174 skills vs canonical 178 / 92 + 9 historical.

## Context before / after

| Item | Before | After |
|---|---|---|
| Global CLAUDE.md (+history file kept) | 36 898 tokens (`CLAUDE.history-2026-10-02.md`) | 3 797 |
| Project CLAUDE.md + AGENTS.md | Ferma 4 226 (over); ERP/PDCC already within limit when measured by the final lint (ERP 2 059, PDCC ~2 700) | all canonical <= 4 000 (Fitness 3 917, Life_Companion 3 961 are the largest) |
| Workspace memory | 160 files; index 1 776 tokens; one 83 KB note | 124 files; index 1 914 tokens (sharding note added); that note 1 134 tokens + verbatim history file |

## Hook audit

FACT: one Python interpreter start costs ~1 350-1 800 ms on this machine; with `-s` (no user site) 117 ms. Cause: user-site `.pth` files
(`pip_system_certs`, `pywin32`, `distutils-precedence`, 5 editable ERP_MVP1_WORKTREE paths) run on every start. The PreToolUse chain for one Bash/PowerShell
call (6 gates measured) took 9 727 ms median and now takes 1 583 ms (-84%). Verification: all 16 hook scripts + 4 local helpers import only stdlib (AST check);
parity on 203 cases (9 gates x corpus, incl. 5 go_gate DENY and 2 allow on a synthetic no-GO transcript) -> 0 mismatches. The dispatcher consolidation was NOT done
(remaining 170-385 ms per hook; safety over milliseconds) -> P2.

## Toolchain

PowerShell 7.6.6, ripgrep 15.2.0 (winget, already installed and on the user PATH), uv (winget, already installed), Git, gh, Node, Docker present. `pnpm` not installed:
no canonical repository uses it. No Python/Node version changed. Bare `python` in this session resolves to `D:\Repo\ERP\.venv` because the session was started from an
activated ERP shell (process PATH only; it is not in the user or machine PATH); hooks and the AI-trading hook use absolute interpreters (venv312 verified, Python 3.12.10).

## Project-specific changes

- AI_trading_assistance: project hook already uses `venv312\Scripts\python.exe` (no bare `python`); skills wired to the financial-ML agents; budgets applied.
- ERP: HEAD `skills:` lists preserved and extended (see Incidents); dirty work untouched.
- PDCC: legacy duplicates deprecated; `USAGE_POLICY.md` relocated and 2 references updated; `REVIEW_ORCHESTRATION_PROTOCOL.md` untouched.
- RQDO: workspace copies archived; project agents (with uncommitted earlier edits) untouched except budget + skills.
- Fitness: classification below, no mass conversion. db-test-tool-analysis: classification below.
- ivan-ai-company: not modified. SHA256SUMS: 49 of 50 entries verify; `CLAUDE.md` differs and was last modified 2026-08-17 04:10 (before this program,
  next to `VERSIONING_DECISION_2026-08-17.md`); no original copy exists anywhere, so it cannot be restored byte-identical. The three agent files match.

### Roster analysis (measured, not converted)

Shared-line boilerplate across agents of one project: AI trading 0%, ERP 0%, Fitness 0%, PDCC 1%, TENDER 6%, VMC 0%, RQDO 5%, **db-test-tool-analysis 31%** (13.6k tokens:
the read-only preamble and the 20-line YAML output contract repeated in 31 agents). Moving shared text into a preloaded skill does not reduce tokens per run (the skill is
loaded whole), so the db-tool extraction is a maintenance gain only, deferred. RQDO auditors are module-specific `file:line` checklists, not boilerplate: compressing them would
delete evidence. Fitness: keep as agents the roles with veto or independent reasoning (clinical-safety-gate, recommendation-adversary, recommendation-engine-architect,
fitness-recommendation-orchestrator, biomechanics-technique-analyst, evidence-guideline-reviewer, fitness-data-scientist, fitness-flutter-reviewer, regulatory-compliance-reviewer);
the ~20 coach/specialist personas (~11k tokens) are knowledge lenses and the candidates for `fitness-prescription-reference` entries once a Fitness eval corpus exists.

## Mechanical verification

- `agentctl.py --strict`: exit 0, errors 0, warnings 29; model violations 0; unresolved routes 0; settings policy PASS; gate installed PASS.
- Unit tests: `C:\Python314\python.exe -m unittest discover -s C:\Users\koros\.claude\control-plane\tests` -> 43 tests OK (34 gate/lint + 9 eval).
- Offline eval `eval\run_eval.py --router`: 15/15, precision 1.0, recall 1.0, 0 unnecessary / 0 missing invocations, 2.87 agents per change.
- All hooks and control-plane scripts compile; `settings.json`, `agent_routing.json`, `model_policy.json`, `projects.json`, `deprecated_agents.json` parse; `sync-rqdo-workspace.ps1` parses and `-Check` says IN SYNC.
- `git diff --check`: 0 findings in AI_trading_assistance, ERP, Fitness_App, Personal_Decision_Command_Center, RQDO, TENDER, Virtual_marketing_company, db-test-tool-analysis, Ferma and `~/.claude`.

## Negative-test results

Gate (fixture homes, real config never modified): Sonnet alias and `claude-sonnet-5-5/5-6/6-0` -> allow; `opus`, `claude-opus-5-5`, `haiku`, `fable`, `claude-sonnet-5`, `claude-sonnet-4-5`, `claude-sonnet-5-4`, `gpt-5` -> deny;
agent file declaring Opus -> deny; project-local override precedence both directions; missing agent -> allowed with a stated note, but denied when the inherited model is not Sonnet; deprecated agent -> deny with successor;
path rule hits a worktree copy without the flag and does not leak to other projects; malformed payload / malformed rules file -> exit 2 for Agent calls only; non-Agent tools untouched; UTF-16 payload decoded.
Lint: fake routed agent -> exit 2, restored -> exit 0; deprecated route, turn cap (and `turnException`), invalid effort, Opus without high, workspace leak, duplicate name, non-agent file, oversized context, missing gate,
non-Sonnet subagent env, dangling skill -> all exit 2; worktree counted separately. Eval: removing a trigger -> MISSING detected; over-broad trigger -> UNNECESSARY/FORBIDDEN detected; empty router -> recall drop detected.

## Incidents during this run (reported, fixed)

1. My `skills:` wiring script replaced pre-existing `skills:` lists on 20 project agents (e.g. ERP `erp-review-contract`). Detected by `git diff`, repaired by merging HEAD lists back; repair is idempotent (0 remaining);
   `agentctl` now fails on dangling skills. 2. A heredoc inside a heredoc corrupted a scratch script (known gotcha); redone with the Write tool. 3. The memory shard script aborted halfway on a name clash; made idempotent, no overwrite
   (the AI-trading `project_trading_bot_oot_harness_resume` kept both versions), one file (`G-UNIFY-0`) mapped to the wrong project and moved to TENDER. 4. The earlier agent's `apply_agent_budgets.py` had stale names (fixed + now a hard error).

## Rollback path

Pre-change snapshot: `C:\Users\koros\.claude\remediation-backup\20261002-205303-control-plane\` (CLAUDE.md, settings.json, agent_routing.json, agents, skills, hooks, control-plane, commands, workspace `.claude`, workspace memory),
plus `settings.json.before-hook-nous-flag`, `codex-config.toml.before-stale-trust`, the earlier `2026-10-02-control-plane-v2\` backup, `CLAUDE.history-2026-10-02.md`, `MEMORY.history-2026-10-02.md`,
`REMEDIATION_STATUS_2026-10-02.prev-agent.md`. Moves are reversible: `memory_shard_manifest_2026-10-02.json` (move each `to` back to `from`); RQDO copies -> move back from `D:\Repo\.claude\archive\...`;
old registries/seeds in `control-plane\superseded\`. Project edits are working-tree changes (uncommitted) and revert with `git checkout -- <path>` only on separate operator approval.

## Deferred P2 (not done, with reason)

1. Hook dispatcher (one process, N checks): only ~1 s left per call; needs full parity corpus incl. Rosetta; not worth the safety risk now.
2. Remove the editable ERP `.pth` files and the stale scratch path from user site-packages (global contamination of every Python 3.14 process; `pip uninstall` is deny-listed and `pip_system_certs` must stay): operator decision.
3. Trust roots: Desktop Commander `allowedDirectories: []` (unrestricted; measured use over 3 303 calls: `D:\Repo`, `D:\Temp`, `C:\Users\koros\.claude`, a little `C:\Python314`/`C:\Windows`; `D:\secrets`/`secure*` never touched) - DC rewrites its own config and is shared with ChatGPT workflows, so set it through DC's own config tool;
   Codex trust of `c:\` and `sandbox = "elevated"` - narrowing needs the operator's list of non-D:\Repo Codex working directories.
4. db-test-tool-analysis shared-boilerplate extraction (31%), Fitness persona-to-reference migration, 27 fat domain-skill front doors (VMC, Fitness, db-tool, ERP): need project eval corpora first.
5. VMC / ivan-ai-company canonical shared package (ivan is an immutable snapshot).
6. Per-run token telemetry: the offline eval measures routing; billed model runs on the fixtures need explicit operator authorization.
7. Document registries (`governance/DOCUMENT_REGISTRY.md`) were not regenerated for PDCC/Ferma (only `.claude/` files and references moved).

## Operator-only / not done

No deletion, `git reset --hard`, `git clean`, force push, branch deletion, commit or push. Opus consent-token mechanism not created (would be an authority mechanism the operator should design).
Uncommitted work remains in the canonical repositories (earlier agent + this run); commits were deliberately not made because they would mix projects.

## Key paths

- Status: `C:\Users\koros\.claude\control-plane\REMEDIATION_STATUS_2026-10-02.md`
- Model policy: `C:\Users\koros\.claude\control-plane\model_policy.json`
- Agent registry: `C:\Users\koros\.claude\control-plane\agent_registry.json`
- Skill registry: `C:\Users\koros\.claude\control-plane\skill_registry.json`
- Lint report: `C:\Users\koros\.claude\control-plane\LINT_REPORT.md` (+ `lint_report.json`)
- Backup: `C:\Users\koros\.claude\remediation-backup\20261002-205303-control-plane\`
