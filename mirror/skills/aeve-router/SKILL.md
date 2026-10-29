---
name: aeve-router
description: Select and apply the smallest suitable AEVE agent or skill instruction profile through local MCP tools, then report exact evidence and unsupported scope. Use for repository analysis, coding plans, tests, architecture, security, reliability, documentation and release-evidence questions.
---

# AEVE profile router

Use AEVE as the profile-contract and bounded evidence tool for repository work. You are the model
host and perform the reasoning under the selected profile; AEVE does not start another model or
silently call a provider. An AEVE profile is a reusable instruction set, not an independent AI
worker.

## Route every request

1. Identify the requested outcome, repository root, and whether the user authorized source
   disclosure, writes, test execution, external provider calls, or other side effects. Default to
   read-only and do not send source to a provider without explicit user authorization.
2. Prefer `aeve.profiles.list` and `aeve.routes.list` over MCP. If the host cannot call local MCP but
   can run local commands, use `aeve profile list` and `aeve profile routes`. If neither route is
   available, report `NOT_COVERED: AEVE_PROFILE_TRANSPORT_UNAVAILABLE`; do not pretend to have
   retrieved the local instructions. Treat the 28 roles and 29 skills as two complementary layers:
   select exactly one primary role for the task outcome, then add only relevant skills as method,
   safety and evidence overlays. Do not invoke all 57 profiles as a substitute for deciding what
   the task needs. The selected role is the executor; skills do not create extra workers.
   For that role, load `core_skills` from `composition_contract.role_bindings` and add a
   `conditional_skills` entry only when its `condition_id` matches the controlled
   `conditional_skill_conditions` catalog. Route-level skill arrays are candidates: a skill's
   presence there does not by itself make it required. Record every distinct condition attached to
   the selected role's binding as matched/not-matched with a caller-reported reason naming the task fact supporting the decision; the
   composer requires one result for each bound condition. If AEVE's ledger schema does
   not accept that data, include it in the host's task record and do not claim AEVE stored it.
   Basic `repo-recon` checks such as recording the current branch, HEAD, status and worktrees do not
   by themselves activate `git-worktree-ops`; load that overlay when the requested operation or
   decision materially depends on Git/worktree topology.
3. Prefer the deterministic composer after choosing the intent, primary role, condition results,
   and optional route-skill candidates. Call `aeve.profiles.compose` with those inputs. Its
   `AVAILABLE` result is one ordered packet containing the exact role and selected skill texts,
   paths, hashes and selection origins. `AVAILABLE` means structural validation only; it does not
   prove semantic compatibility among the natural-language contracts or model adherence. Review
   the bundle for conflicting mandatory instructions and report `NOT_COVERED` if they cannot be
   resolved by removing an optional overlay. If MCP composition is unavailable but local commands are
   allowed, write the same request shape to a temporary JSON file and use
   `aeve profile compose --request REQUEST.json`. If neither composer is available, retrieve each
   selected contract with `aeve.profile.get` / `aeve profile get PROFILE_ID` and explicitly label
   the bundle `HOST_ASSEMBLED_NOT_AEVE_VALIDATED`. Never silently recover from a non-green compose
   result by constructing a different bundle. Follow exact returned contracts within the user's
   authorization and higher-priority host policy. Composition and CLI retrieval do not themselves
   create a task ledger, bind a snapshot, or provide source-read evidence; state that limitation.
   When multiple intents match, choose by the requested deliverable and affected artifact, not by
   keyword count. Record why one primary role owns the task; add a second role only for a distinct
   specialist task or independent review. Skills add procedures and evidence criteria but cannot
   grant tools or widen the task. The effective permissions are the intersection of host/platform,
   operator, repository and AEVE server constraints. If selected skills conflict on a mandatory
   action, remove an unnecessary skill or report
   `NOT_COVERED: PROFILE_CONTRACT_CONFLICT` with the conflicting profile IDs; do not silently
   average the instructions.
4. Review every selected contract for incompatible mandatory requirements. If a conflict remains,
   return `NOT_COVERED: PROFILE_CONTRACT_CONFLICT` with the profile IDs and do not begin execution.
   Otherwise, prepare one complete `aeve.task.begin` request with the root, concise task label,
   selected profile IDs, exact `expected_profile_hashes`, the returned `composition_sha256` as
   `expected_composition_sha256`, the exact `composition_request` sent to compose, and a
   `semantic_review` disposition of `COMPATIBLE` bound to that digest and all selected profile IDs.
   This semantic-review value is a host assertion, not proof that review was correct; keep the
   reasoning in the host's evidence record. Then call `aeve.task.begin` exactly once. The server
   recomputes the selection and rejects mismatched profile IDs, instruction hashes, source hashes,
   or composition identity before creating the task. The composition digest binds both
   `contract_sha256` (the returned body) and `source_sha256` (the full provider-native file).
5. Use the single returned task ID for `aeve.project.snapshot` and `aeve.source.read` within that
   process lifetime. Provider/model fields are caller-reported, not authenticated. The ledger is
   scoped to the configured root and server process.
6. Request `aeve.source.read` only for tracked clean-HEAD files after the operator explicitly starts
   the process with `--allow-source-disclosure`. This setting authorizes all source and analyzer
   calls in that process lifetime; it is not authenticated per-call human approval. The source tool
   is limited to 128 KiB and blocks if its secret scan finds a
   finding or cannot complete. Do not infer that a blocked scan proves the rest of the repository
   contains no secrets.
7. Use only AEVE tools that exist in `tools/list` and are allowed by the user and host policy.
   Profile instructions guide model behavior but do not grant or restrict server tools; AEVE applies
   its process configuration and root/snapshot bounds uniformly to all selected profiles. Bind
   source observations to the exact task snapshot. Keep each tool result's status, reason,
   paths, line ranges, hashes and unsupported scope intact. Use `aeve.task.get` to review the
   recorded snapshot, contract hashes and hashes/statuses of tool results. Call `aeve.task.finish`
   when the host analysis ends; its final state explicitly remains `HOST_RESPONSE_NOT_VERIFIED`.
8. If no AEVE tool implements a requested action, return `NOT_COVERED` with the missing capability;
   do not simulate a test, build, migration, external call, write or deployment.
9. Report findings with direct evidence. A valid source citation proves location only. Empty findings,
   a successful tool call or `COMPLETE` for a narrow operation does not prove the whole task passed.
   Keep profile states distinct: `RETRIEVED` means the exact contract and hash were obtained;
   `ROUTED` means the host selected it for a task and recorded why; `BEHAVIOR_EXERCISED` requires a
   real model host to consume that exact contract and complete a bounded scenario with retained
   output; `ADJUDICATED` requires assessing that output against explicit criteria. Never describe a
   retrieved or routed profile as behavior-tested. Apply disabled-profile overrides before routing;
   `rosetta` remains unavailable unless the operator explicitly reauthorizes it.

## One composed task, not 57 independent workers

Treat roles and skills as two parts of one task instruction packet. The primary role owns the
deliverable and final response. Its core skills provide the default operating rules; conditional
skills are added only after their catalogued condition matches. Route lists are candidate pools,
not instructions to load every listed profile. This same sequence applies in every provider host.
Workflow lanes and profile families are planning/classification views: role IDs in a lane are
alternatives, not a group to load together. A phase change, separate deliverable or independent
review creates a linked task with its own single primary role.

For each task, assemble and record this packet in the host's task context:

1. Task goal, affected artifact, authorized scope, and matched route intent.
   2. Exactly one primary role ID, its returned instruction-body hash and full source hash, and why it owns the result.
   3. Each selected skill ID, its returned instruction-body hash and full source hash, marked `core`, `conditional`, or `route_candidate`,
   with the reason it contributes a distinct method, boundary, or evidence requirement.
4. Every distinct condition attached to the selected role's binding, with `MATCHED` or
   `NOT_MATCHED` and a short caller-reported reason naming the supporting task fact; list excluded route candidates and why they
   were not needed. The composer requires a result for each bound condition.
5. Effective capability/authorization limits, unresolved conflicts or `NOT_COVERED`, and evidence
   references/statuses.

Use the AEVE task ledger only for fields it actually accepts and returns. Keep any selection reason,
conditional decision, raw model output, or adjudication in the host record if the ledger has no such
field. Do not say AEVE retained data without a returned ledger record proving it.

The role and skills must be supplied together as one composed instruction context: the role carries
the objective and output format; skills contribute procedures and proof obligations without
becoming separate agents or publishing duplicate answers. Add another role only as a separately
scoped linked task or an explicitly requested independent review. If an optional overlay causes a
conflict, remove it; if mandatory requirements still conflict, return
`NOT_COVERED: PROFILE_CONTRACT_CONFLICT` with the profile IDs.

**Example:** for “review this database schema change,” `database-reviewer` is the sole primary role
and `db-change-contract` plus `verification-contract` are its core skills. Add `migration-safety`
only when a migration artifact is actually in scope. The role returns one finding set that follows
both skill checklists; it does not launch a second “migration agent.”

`profile.get` and `profiles.compose` return only the instruction body after the profile file's YAML
frontmatter. Treat `contract_sha256` as the hash of the exact body sent to the model and
`source_sha256` as the hash of the complete native file. Never send frontmatter fields such as model,
tools, or embedded skill lists as instruction prose or as permission grants. Both hashes are bound to
the composition digest and task ledger.

For Claude, role frontmatter lists core skills only. The router retrieves and adds conditional
skills after evaluating their conditions. A conditional contract listed in frontmatter would load
unconditionally and violate this composition rule.

## Profile selection guide

- Repository structure, call paths, impact: `repo-recon`, `code-explorer`.
- Architecture and interfaces: `architect`, `code-architect`, `architecture-contract`.
- Implementation: `implementation-engineer`, `implementation-workflow`, `delivery-efficiency`;
  select `build-error-resolver` for a concrete build/compiler failure, `code-simplifier` for a
  behavior-preserving simplification, or `refactor-cleaner` for dead/duplicate code only when the
  task calls for it. `dart-build-resolver` and `pytorch-build-resolver` are for their named stacks.
- FastAPI and types: `fastapi-reviewer` for FastAPI-specific behavior; `type-design-analyzer` for
  type invariants and interface design. Keep either as the single primary role when it matches the
  task; add `verification-contract` only when evidence criteria are needed.
- Git workspace operations: use the `git-worktree-ops` contract with a repository-understanding
  role such as `code-explorer`. Follow the operator's exact branch/worktree policy.
- General correctness and silent failures: `code-reviewer`, `python-reviewer`, `fastapi-reviewer`,
  `flutter-reviewer`, `type-design-analyzer`, `silent-failure-hunter`.
- Database: `database-reviewer`, `db-change-contract`, `migration-safety`.
- Security, reliability and integrations: `security-reviewer`, `security-evidence-contract`,
  `reliability-reviewer`, `reliability-contract`, `observability-contract`,
  `integration-contract` as applicable.
- Test planning/design/execution: use `tdd-guide` for requirements-to-test sequencing only when
  repository policy permits its workflow; in AEVE it derives assertions before coding and hands off
  test authoring/execution to `functional-test-reviewer` and `e2e-runner` after coding. Apply
  `functional-testing` and `e2e-testing-contract` only when they match the phase. Test execution is
  available only through an accepted AEVE test adapter and explicit task authorization. A strict
  test-first request that conflicts with repository policy is `NOT_COVERED`, with the policy and
  test-owner handoff stated explicitly.
- Changes: `implementation-engineer`, `build-error-resolver`, `code-simplifier`,
  `refactor-cleaner`, `doc-updater`; writing remains unavailable unless a separately approved
  write capability is exposed.
- Accessibility and UX: `a11y-architect`, `a11y-contract`, `product-ux-reviewer`,
  `ux-design-contract`.
- Machine learning: `ml-engineer`, `pytorch-build-resolver`, `financial-ml-contract`.
- Planning, process, evaluation and reports: choose `planner`, `technical-design`,
  `agent-evaluation`, `agent-consensus`, `codex-consensus`, `pm-bridge`,
  `html-report`, `context-memory-hygiene`, `update-config`, `skill-creator`, or the narrowest
  applicable contract. The `rosetta` route is disabled by the active operator policy unless it is
  explicitly reauthorized.

This guide is only a routing hint. The registry, actual MCP tool list, and retrieved profile
contract are authoritative for available operations. In the initial runtime slice, writing code,
writing tests, running arbitrary tests, live database access, production actions, and provider
calls are not general MCP capabilities. Existing bounded CLI tools remain separate.

The CLI fallback is only profile retrieval. Writing, test execution, source-read evidence and other
operations still require their explicitly implemented AEVE tool and user authorization. A provider
must have either local MCP access or local command execution to read profiles from this machine;
`SKILL.md` alone cannot cross that host boundary. The `aeve` command must be installed in the host
environment; for an uninstalled checkout, invoke `python -m aeve.cli` with the checkout's `src`
directory on `PYTHONPATH`.

## Global memory

Read global AEVE memory only when the user requests it and the operator configured the server with
`--enable-memory`. That setting authorizes all memory reads for the server process lifetime; the
MCP argument cannot prove per-call human consent. Enable it only in a trusted host session. Project
notes require `include_project: true` and the configured root. Memory is local to this user, can influence behavior across repositories, and must
not be treated as project evidence. Project notes and source facts are separate and remain scoped
to their repository. Never save a memory entry from model output without a direct user instruction
and the user-operated AEVE memory command. MCP has no memory write/delete tool.
