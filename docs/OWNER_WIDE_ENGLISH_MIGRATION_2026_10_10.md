# Owner-wide GitHub English Migration — Inventory and Handoff

**Date:** October 10, 2026  
**Account:** `xLZDx`  
**Scope:** 34 repositories accessible through the owner's connected GitHub account.  
**Status:** **IN PROGRESS — NOT ENGLISH-ONLY YET.**

## Scope and evidence

A read-only scan of the default-branch Git tree was performed for each accessible repository. The scan enumerated tracked paths, detected missing root README files, and flagged filenames with obvious Russian-language suffixes such as `*.ru.html` or `*_RU.md`.

**Important limitations:** Path-based classification does not prove a file contains Cyrillic, and it misses Cyrillic within English-named files. The repository's historical Git objects, issues, PR threads, review comments and non-default branches require separate inventory. This is **not** an all-content translation/compliance scan.

| Metric | Verified result |
| --- | ---: |
| Accessible repositories | 34 |
| Root READMEs already present at audit start | 22 |
| Repositories without a root README at audit start | 12 |
| Non-empty repositories with a new README in an isolated draft PR | 8 |
| Initially empty repositories initialized with an English README | 4 |
| Russian-language root READMEs identified at audit start | 3 |
| Initial Russian-language README translations opened as draft PRs | 3 |
| Tracked files with obviously Russian-named paths on inspected default branches | **452** (filename signal only, not a content audit) |

## Missing README closure

Eight existing projects now have proposed English root READMEs (draft PR, not merged):
- [Fitness-App #1](https://github.com/xLZDx/Fitness-App/pull/1)
- [arbitrage-strategy #1](https://github.com/xLZDx/arbitrage-strategy/pull/1)
- [DB_TEST_TOOL #1](https://github.com/xLZDx/DB_TEST_TOOL/pull/1)
- [db_test_tool_clean #1](https://github.com/xLZDx/db_test_tool_clean/pull/1)
- [crash_bot #1](https://github.com/xLZDx/crash_bot/pull/1)
- [test #1](https://github.com/xLZDx/test/pull/1)
- [Life-Companion #1](https://github.com/xLZDx/Life-Companion/pull/1)
- [ReviewExistingExamples #1](https://github.com/xLZDx/ReviewExistingExamples/pull/1)

Four GitHub repositories were confirmed truly empty (`get_repo.size == 0`), and each default branch was initialized with a first English README commit. Initializing the first commit cannot be proposed as a PR against an unborn default branch:
- `awesome-claude-code` — `42f29a4`
- `remote-rely-v2` — `a16eefef`
- `test_2` — `75767ccb`
- `Figma` — `20d65a9`

No source or deployment code was changed in these README-only operations. Empty repository READMEs explicitly identify the lack of a published implementation.

## Translation work submitted for review

- [ERP_MCP #38](https://github.com/xLZDx/ERP_MCP/pull/38) — English root README, Phase 2 README, Release 1 Lessons Learned, and Step-by-Step Installation Guide (four documents). The `_RU.md` filenames are retained until link migration is approved.
- [AEVE #1](https://github.com/xLZDx/AEVE/pull/1) — English root README with preserved registry-only G0 status.
- [Virtual_marketing_company #1](https://github.com/xLZDx/Virtual_marketing_company/pull/1) — extended English root README covering authorization, privacy, GUI, operational stages and historical milestone evidence.

All proposed replacement content was checked for Cyrillic before submission. Translation fidelity, exact anchors, links, tests and public-facing publication claims still need independent review; the PRs are intentionally drafts.

## Remaining Russian-named file inventory, by repository

The following counts are **path-pattern matches only**, not guaranteed Russian content:

| Repository | Russian-named tracked paths on inspected default branch |
| --- | ---: |
| Fitness-App | 100 |
| ERP | 115 |
| PM_Bridge | 57 |
| Personal_Decision_Command_Center | 44 |
| ERP-Virtual-Economy-Digital-Business-Universe | 31 |
| Remote-Quality-Delivery-Office-Platform | 29 |
| Virtual_marketing_company | 23 |
| TENDER | 23 |
| ERP_MCP | 19 |
| db_test_tool_clean | 11 |
| **Total** | **452** |

All other inspected repositories had zero **filename-pattern matches**; this does not imply their documents or source comments are English. Examples of Cyrillic text in files without a Russian filename were confirmed in the broader GitHub code search.

## Required continuation order

1. Review and merge the eleven draft PRs currently open for English README changes. Do not merge without checking exact HEAD, build links, and repository review rules.
2. Capture current default/release/feature branch heads and enumerate text blobs, including files whose filenames lack `ru` markers. Scan Markdown, MDX, HTML, documentation templates, Python/PowerShell/JS/TS/Dart comments, user-facing CLI text, and generated reports.
3. Classify each match as **translatable prose**, **required native-language business data**, **1C metadata/API identifier**, **legal quotation**, **immutable audit evidence**, or **generated output**. Never translate machine-readable identifiers, accounting amounts, customer source data, or cryptographic evidence in place.
4. Translate current authoritative documents in each repository without removing requirements or mutating runnable commands. Where historical evidence must remain unchanged, add a separately linked English translation and an explicit provenance reference; do not rewrite Git history.
5. Check links and anchors, run appropriate tests and static checks on each exact candidate HEAD, and submit separate documented PRs without clobbering other contributors' dirty worktrees.
6. Update active Issues/PR descriptions and applicable current review threads in English, preserving historically signed decisions and change authorship.
7. Provide an evidence-based per-repository and per-branch completion matrix. **Never claim all GitHub is English until source content, reports, active Issues/PRs and review threads are covered.**

## Language policy

All new GitHub-facing prose, README files, issue/PR bodies, review comments, and human-authored code comments must be **English**. Chat communication may remain Russian. Required 1C field/entity identifiers, source quotations, locale-test fixtures, customer data and immutable historical records must be preserved if translation would change the contract or falsify evidence.

**No forced history rewrites; no destructive cleans, branch resets, or modification of unrelated uncommitted work.**

**Tracking issue:** [Owner-wide English migration](https://github.com/xLZDx/claude-control-plane/issues/1).
