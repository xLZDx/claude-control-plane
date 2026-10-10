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

## Corrected English Companion Coverage (Later Audit)

**Correction to the initial path-only pending list:** Of the **440 document-like** filenames ending in `.ru.html` or `_RU.md`, **426 already had a conventional English sibling file on the inspected default branch**. Only **14** lacked a separate English sibling: 13 in ERP_MCP and one in PDCC. All fourteen were translated **in place in draft PRs**, without renaming their original paths. Ten actual English siblings were fetched across the ten repos and all ten contained zero Cyrillic.

**Do not infer that 426 translations have been individually verified.** This is an **existence** audit plus a ten-file content sample, not a complete language or semantic review. See the exact SHA tables and outstanding work in [Existing English Counterparts](EXISTING_ENGLISH_COUNTERPARTS_2026_10_10.md). The 452 filename markers below also include twelve non-document Fitness-App locale/data/media files; they are not automatically translation targets.

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

- [ERP_MCP #38](https://github.com/xLZDx/ERP_MCP/pull/38) — fifteen English documents, including all thirteen previously unpaired `_RU.md` guides plus the root README and Phase 2 overview. Existing filenames remain stable until a separate reviewed link migration.
- [AEVE #1](https://github.com/xLZDx/AEVE/pull/1) — English root README with preserved registry-only G0 status.
- [Virtual_marketing_company #1](https://github.com/xLZDx/Virtual_marketing_company/pull/1) — **27 Markdown files** at exact draft HEAD `98e2cfc9910f0aab07bed99f7e1c4d41ed7dd109`: English root README, index, two source-linked founder/channel guides and **23 English historical report companions (23/23 candidate Russian HTML sources)**. Originals and prior English HTML counterparts are preserved, with no executable code or product-localization change. A 60-file selected source cohort was separately classified, but full code-comment/branch and semantic review remain open. See [VMC translation cohort details](translation_targets/Virtual_marketing_company.md).

All proposed replacement content was checked for Cyrillic before submission. Translation fidelity, exact anchors, links, tests and public-facing publication claims still need independent review; the PRs are intentionally drafts.

## October 10 Continuation — Source-Safe Documentation Coverage

- **ERP_MCP:** all **15** translated draft documents on [PR #38](https://github.com/xLZDx/ERP_MCP/pull/38) passed the [exact-HEAD structural/path audit](translation_targets/ERP_MCP_DOCS_QA_2026-10-10.md): zero Cyrillic, 74 valid local file paths, 58 balanced fence delimiter lines in total, no executable code edits. Semantic/command review remains open.
- **Virtual_marketing_company:** [PR #1](https://github.com/xLZDx/Virtual_marketing_company/pull/1) now has **29 Markdown files** at `b45bc052663b813a0e434e72fac68683625d25f9`, including all 23 historical report companions, two existing source-linked guides, an English root README/index, plus [SPTR product](https://github.com/xLZDx/Virtual_marketing_company/blob/docs/english-readme-20261010/products/sptr/product.en.md) and [live validation](https://github.com/xLZDx/Virtual_marketing_company/blob/docs/english-readme-20261010/docs/04_LIVE_VALIDATION_PLAYBOOK.en.md) English explanatory references. Separately [69 selected current-doc/agent files](translation_targets/Virtual_marketing_company_ACTIVE_DOC_AUDIT_2026-10-10.md) were examined: **48 without Cyrillic, 21 with contract-sensitive Russian examples** classified by blob SHA. Canonical source, founder approvals and live product copy were not rewritten.
- **PDCC:** [draft PR #146](https://github.com/xLZDx/Personal_Decision_Command_Center/pull/146) contains **10 Markdown changes** at `f19c3ab94e150d872d2d59646e9302796bd3dd26`, adding an English [September 10 TDD v0.2 adversarial review companion](https://github.com/xLZDx/Personal_Decision_Command_Center/blob/docs/english-handoff-20261010/governance/reviews/02-tdd-v0.2-adversarial-review.en.md). The dated one-blocker/three-major historical NO-GO and later policy-precedence limitations were preserved; original report and implementation remain unchanged.

**Important:** All three PRs are **still open drafts**. Translation companion coverage, absence of literal Cyrillic and valid relative files do **not** certify current implementation, independent semantic fidelity, acceptance gates or account-wide English-only status.

## ERP_MCP English Historical Report Pair Validation

[All six original/English report pairs](translation_targets/ERP_MCP_HISTORICAL_REPORT_AUDIT_2026-10-10.md) were read at exact ERP_MCP draft tree HEAD `8d17448cf2788f48a2b3f26eb70800cefed4d992`. **Six of six English `.html` files exist, four have zero Cyrillic, two detailed real-1C reports carry native-language evidence** (23 / 39,178 Cyrillic characters). Relative real-1C cross-links resolve. Together with the **13** Markdown docs translated in [draft ERP_MCP #38](https://github.com/xLZDx/ERP_MCP/pull/38), the selected Russian-named 19-document cohort now has **19/19 English coverage** (draft or pre-existing), **not** proof of source semantic fidelity, literal English-only content or a merged repo. Native 1C business evidence remains preserved.

## TENDER — Verified English Historical Report Coverage

[Complete TENDER 23-report exact-blob audit](translation_targets/TENDER_HISTORICAL_REPORT_LANGUAGE_AUDIT_2026-10-10.md): all **23** English HTML siblings fetched; **20** contain zero Cyrillic; **three** retain source-attributed operator language. [TENDER Draft PR #1](https://github.com/xLZDx/TENDER/pull/1) adds a complete English navigation index and correct alternative links for **nine archived broken relative references** in G1.6 HTML, plus three source-linked English Markdown historical companions. The two indexes contain **64 verified local links, zero unresolved**. Known Russian-named TENDER historic report cohort **23/23 covered**, semantic signoff and other branches still pending.

## PM Bridge — Complete Existing English Report Review

[Exact SHA audit for all 57 historic report source pairs](translation_targets/PM_Bridge_HISTORICAL_REPORT_LANGUAGE_AUDIT_2026-10-10.md): **57/57** English HTML reports fetched; **50** with zero Cyrillic, **seven** preserving owner/approval language (383 characters). [PM Bridge Draft PR #1](https://github.com/xLZDx/PM_Bridge/pull/1) contains the 57-report English index with working alternatives for two archived Gate P evidence references, README navigation, and two English Markdown historical companions. **120** local links resolved, zero missing; originals untouched. **Historical Russian-named report cohort 57/57 English-covered**, independent semantic review and all-branch migration pending.

## db_test_tool_clean — All Eleven Existing English Historical Reports

[Exact Git blob audit](translation_targets/db_test_tool_clean_HISTORICAL_ENGLISH_AUDIT_2026-10-10.md): the known eleven Russian-named historical report files each have English HTML siblings, and **all 11 contents were fetched and contained zero Cyrillic**. [db_test_tool_clean Draft PR #1](https://github.com/xLZDx/db_test_tool_clean/pull/1) now adds a source-linked English report index and a README link: **28 local Markdown links tested, zero missing**. No original report or code was modified. **Known cohort 11/11 English-covered**, while all other source/branch and independent reviewer checks remain open.

## Additional Exact-HEAD Cohorts and Translation Slices — October 10

### Three fully scanned default-tree Markdown/TXT cohorts

[Complete 115-file language inventory](translation_targets/THREE_REPO_ACTIVE_TEXT_AUDIT_2026-10-10.md) directly inspected **all tracked Markdown and TXT** in `Usefull_agents_and_skils` (49), `PM_Bridge` (34) and `TENDER` (32). **92 files** had no Cyrillic; **23 contained deliberate owner/source quotations, official names, historical gate labels or execution tokens**. Each exception is classified with its Git blob SHA. The global agent/skill repository has only one Cyrillic-positive file: `skills/rosetta/SKILL.md` with the operator's literal bilingual GO marker. **No automatic conversion of this authorization token** is safe. In PM_Bridge, visually confusable Latin/Cyrillic gate labels require separate reference analysis, not a mass replace.

At the reviewed exact drafts, [PM_Bridge #1](https://github.com/xLZDx/PM_Bridge/pull/1) retains two English source-linked historical reports and [TENDER #1](https://github.com/xLZDx/TENDER/pull/1) retains three; all five English Markdown files were re-fetched, free of literal Cyrillic, and linked to their retained originals with zero missing relative paths. These are documentation-only proposals awaiting independent review.

### Two new substantive translation slices

[Translation evidence and exact SHA table](translation_targets/ARBITRAGE_AND_FIGMA_IMPORT_TRANSLATIONS_2026-10-10.md):

- [arbitrage-strategy PR #1](https://github.com/xLZDx/arbitrage-strategy/pull/1) at `d05642f4c8ccd483b491b44934f0f9189a678d2b` adds an English companion translating Russian research passages in the 796-line mixed-language `arbitrage.txt` (77 Cyrillic-bearing lines), and links it from the root README. Conflicting original DuckDB/QuestDB assumptions and unverified market-execution claims remain explicitly qualified.
- [ReviewExistingExamples PR #1](https://github.com/xLZDx/ReviewExistingExamples/pull/1) at `e0b10fa525cab3755a96df8144f1bd2a40601e04` now covers **all 8/8 unique imported Fitness App design-source blobs** with English Markdown companions: the earlier **24-section redesign**, **29-section Figma v1.0**, **29-section master v1.1 plus v1.3 update**, the Decision Registry screen, all **44 questions**, Body Metrics, **20-section Progress Photo Comparison**, and **27-section Technique Coach**. The root README links all eight, historical duplicated originals are untouched, exact old-vs-new version boundaries and D1 STOP/17 DoD, Q19/Q39, under-20/BMI, privacy and on-device-camera limitations are retained. This is complete coverage for the **defined imported Markdown cohort**, not full repo/runtime or global GitHub English-only certification.

Both PRs change **eleven Markdown files combined** (2 arbitrage, 9 design references), with zero Cyrillic in proposed English, no unresolved relative links and no runtime/prototype/trading implementation changes. **Draft, not merged or semantically signed off**. Other substantial Russian imported design references remain open.

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

## October 11 — Fitness-App Active Text and Six New Core Translations

[Fitness-App exact-source audit](translation_targets/Fitness_App_ACTIVE_TEXT_AUDIT_2026-10-11.md) covers **94 selected current Markdown/prompt texts**: 41 agents/commands/skills (all zero-Cyrillic), five root/policy documents (three no-Cyrillic, two literal bilingual GO authorization), and 48 selected core documents (29 zero-Cyrillic, 19 original-language). Six substantial historical Russian/mixed-language core documents now have separate English companions in [Fitness-App Draft PR #1](https://github.com/xLZDx/Fitness-App/pull/1): full August 11 release BLOCK audit, August 14 consent-gate checkpoint, August 7/8 session logs, September 25 handoff, and the proposed favorite-gym/news plan. Exact original source SHAs and local links verified; [core index](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/INDEX.md) links all six.

Previous 88-report / 15-original-redesign-blob English coverage remains separately recorded. This **does not certify all 335 Markdown/TXT files on the current Fitness-App draft tree**, its approximately 4.1 MB immutable decision log, active Dart source comments, non-default branches or historical GitHub discussions. Original user-facing Russian strings and owner approval tokens were preserved, no Flutter/Firebase/user data changed, and independent semantic/merge review remains pending.

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
