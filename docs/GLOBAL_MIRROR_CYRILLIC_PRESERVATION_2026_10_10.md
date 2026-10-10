# Global Claude Control-Plane Mirror — Cyrillic Audit and Preservation Plan

**Date:** October 10, 2026  
**Repository:** `xLZDx/claude-control-plane`  
**Evidence:** [GitHub Actions run 38044181336](https://github.com/xLZDx/claude-control-plane/actions/runs/38044181336), exact tested commit `bdc1655dde459a29dbb9784dc3667415365fdee2`.

## Verified Content Scan

The read-only Git-blob scanner inspected **186 recognized text blobs** in the exact CI checkout. **20 contained Cyrillic**. All six scanner unit tests passed. The scan was complete **for recognized text paths** in that commit; it does not certify unrecognized extensions, other Git branches or issue/review history.

**Critical classification:** All 20 matches belong to `mirror/`, which is the exported global Claude Code control plane. This is an **authoritative behavior mirror**, not merely a set of Markdown guides. Changing literal Cyrillic `GO` equivalents, regex fixtures, decision quotes or approved policy text without evaluating the upstream contract can change authorization behavior.

## Findings and Migration Disposition

| Source in mirror | Classification | Safe next action |
| --- | --- | --- |
| `mirror/CLAUDE.md` | Live global operating contract; includes literal operator `ГО` and historical text | Review upstream canonical `~/.claude/CLAUDE.md`; translate prose only in a **separately approved change**, preserve accepted authorization tokens and test gate behavior |
| `mirror/commands/pm-bridge-mode.md` | Active operator slash command with literal `GO / ГО` | Preserve command inputs; use English surrounding explanation |
| `mirror/core/DECISION_LOG.md` | Immutable historical governance quotations and recorded decision evidence | Preserve exact original quotes; add source-linked English companion explanations rather than rewriting decisions |
| `mirror/hooks/_report_common.py` | Hook source with Cyrillic strings/comments; exact role not yet independently inspected | Identify all programmatic vs explanatory occurrences and test before any upstream edit |
| `mirror/hooks/ask_routing_gate.py` | Hook source; possible multilingual invocation logic | Classify literal triggers and tests, not blanket translation |
| `mirror/hooks/codex_review_gate.py` | Hook source; potential approval/review parsing | Preserve original trust boundaries; independently test any English-comment-only change |
| `mirror/hooks/dangerous_command_gate.py` | Safety-critical command guard | Treat Cyrillic command input and adversarial fixtures as behavioral data |
| `mirror/hooks/go_gate.py` | **Critical authorization gate**; contains actual `ГО` logic and historical operator quotes | **Never translate runtime literals or approved quotes in place**; requires threat review and regression on the real upstream hook |
| `mirror/hooks/gpt_review_gate.py` | Independent review/approval guard | Verify parser and signature semantics before altering strings |
| `mirror/hooks/plan_approval_gate.py` | Plan authorization guard | Protect operator input tokens and review receipts |
| `mirror/hooks/pm_bridge_stop_gate.py` | Emergency/STOP behavior | Retain recognized commands and negative test cases; no behavioral change without approval |
| `mirror/hooks/report_due.py` | Hook/report orchestration | Classify executable strings vs documentation |
| `mirror/hooks/report_gate.py` | Reporting gate | Preserve contract strings until checked |
| `mirror/hooks/rosetta_due.py` | Rosetta workflow | Preserve workflow command inputs |
| `mirror/skills/html-report/references/full-2026-10-02.md` | Active skill reference copied from upstream | English companion or approved upstream source translation, then re-export and verify exact diff |
| `mirror/skills/rosetta/references/full-2026-10-02.md` | Active workflow reference | Same treatment; never weaken permissions or downgrade explicit GO |
| `mirror/skills/update-config/references/full-2026-10-02.md` | Active configuration-change skill reference | Same treatment; verify resulting config operations |
| `mirror/tools/report_conform.py` | Program-generated report text and helper code | Translate commentary or supported UI localization separately; do not alter parsing |
| `mirror/tools/session_digest.py` | Session parsing and summaries | Keep literal input patterns and audit provenance |
| `mirror/tools/test_pm_mode_gates.py` | Tests encoding historical/native-language authorization inputs | Preserve test fixtures; English docstrings are a separate reviewed change |

## Required Workflow

1. Inspect the actual upstream `~/.claude` sources, exporter allowlist, current SHA and dirty state. The mirror's source-of-truth may be a different worktree; do not overwrite it from this documentation PR.
2. Determine **which occurrences are programmatic data, quotes, fixtures, or prose**. Only the last class is a routine translation target.
3. For live governance/hooks, create semantic-diff tests showing unchanged acceptance/rejection of both English `GO` and Cyrillic `ГО`, including spoofing, stale receipts, unapproved plans, STOP and negative access cases.
4. Translate prose in the **canonical upstream source**, not just the exported mirror. Re-export through `scripts/export_from_claude_home.py` using its fail-closed secret scan and review the full resulting diff.
5. Capture exact HEAD, test/CI evidence and authorized review. Historic decision quotes stay byte-exact, with an English companion where useful.
6. If source access or tests are refused, record `BLOCKED`; do not use another tool to evade the policy.

## Why the Findings Are Not Automatically Violations

English-only **authoring** rules govern newly written descriptions, documentation and comments. An essential original language token such as the literal command `ГО`, a signed decision quotation, or an internationalization/negative-test fixture is **structured source data**, not an untranslated author comment. Erasing it would reduce functionality or falsify evidence.

**Disposition:** `20 DETECTED / 20 CLASSIFIED FOR CONTROLLED REVIEW / 0 MIRROR FILES ALTERED`. This is a classification plan, **not** proof that all comment text in the mirror is already English.
