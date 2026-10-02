# Control-plane eval (agents, routing, token efficiency)

Goal: prove that slimming prompts or changing routing does not lose real defect detection, and measure cost, without
counting "how many agents ran" as quality.

## What runs with no model (default, free, deterministic)

`python run_eval.py --router` routes each fixture's changed files through `route.py`, the code form of
`~/.claude/agent_routing.json` (group A language lens + silent-failure-hunter, group B triggers, group D for tests,
group S flag-only, E/R/T/N/P never automatic), and checks the result against `case.json`:

| Metric | Meaning |
|---|---|
| selection precision / recall | selected agents vs `expected_agents` |
| unnecessary invocations | selected but neither expected nor allowed (router quality) |
| missing invocations | expected but not selected |
| tier | R0 / R1 / R2 / R3 vs expected |
| flagged | security-reviewer flagged for the operator (never spawned) |

Run it after every edit to `agent_routing.json`; exit code 1 means a regression. `tests/test_eval.py` runs it in CI of
the control plane.

## What needs recorded model output (opt-in, billed, operator-authorized)

`python run_eval.py --score run.json` scores reviewer findings from a real run, where `run.json` is
`{"<fixture id>": [{"agent", "severity", "file", "line", "claim", "tokens"?, "latency_s"?}]}`.
Metrics per fixture: recall of the seeded defect, escaped seeded defects, severity adequacy, BLOCKER/MAJOR false
positives, precision, duplicate findings (same defect from several agents), unique findings, tokens, latency.
This tool never launches a model: running agents on the fixtures is a separate, explicitly authorized action.

## Fixtures

`fixtures/<id>/case.json` + `fixtures/<id>/files/<repo-relative path>`. 15 cases drawn from defect classes this
workspace has actually met (Ferma gate F0 false greens, RQDO tenancy / importer / lifecycle audits, AI-trading
look-ahead leakage, db-tool NULL semantics, a gate that scans nothing). `f10` is the negative control: a docs-only
change must select no reviewer. Seeded defects are located by unique code fragments; the files contain no hints.

Adding a fixture: copy a directory, change the code and `case.json` (`seeded_defects[].file/line/keywords`,
`routing.*`). Keep one seeded defect per file so recall stays unambiguous. Never put the answer in a comment or a
file name. Project-specific agents (`project_scope_agents`) are not routed by the global router; they are listed so a
project-level eval can reuse the case.

## Acceptance rule for a prompt-slimming or routing change

1. `--router` still passes every fixture.
2. Recorded runs before and after show no drop in recall on seeded defects and no increase in BLOCKER/MAJOR false positives.
3. Tokens per run go down (or the change is justified by something else).
