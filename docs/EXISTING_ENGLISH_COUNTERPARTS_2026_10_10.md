# Existing English Counterparts — Corrected Translation Inventory

**Audit date:** October 10, 2026  
**Scope:** All 10 accessible repositories whose default-branch Git trees contain `*.ru.html` and/or `*_RU.md` documents.  
**Status:** English companion **existence audit complete**; English content equivalence and full repository translation **NOT certified**.

## Correction to the Initial Backlog Estimate

The earlier 34-repository inventory identified **440 document-like files with Russian-language filename markers** and described them as a pending translation queue. That **overstated the number of missing English documents**: most generated reports already had an English sibling.

The new audit matched the exact expected sibling path:
- `reports/example.ru.html` → `reports/example.html`
- `docs/example_RU.md` → `docs/example.md`

Only a **tracked file path match** counts as paired. It does **not** prove the English sibling has equivalent or English-only text.

| Repository | Default branch / inspected tree SHA | Russian-named documents | Already paired on default branch | Lacking that sibling |
| --- | --- | ---: | ---: | ---: |
| ERP_MCP | `main` / `cac886dcfb0d749892c60dc78902dea918196fdd` | 19 | 6 | 13 |
| ERP | `main` / `a1ac7ce121eaa08ef0ad4994069c295a8a4c93cd` | 115 | 115 | 0 |
| Personal_Decision_Command_Center | `main` / `2708b3d4dfc8dbd3eb72a2168da65a13e471bbcf` | 44 | 43 | 1 |
| PM_Bridge | `master` / `214af1ee3d0d847b97c38d84ce89650df3e542ea` | 57 | 57 | 0 |
| Virtual_marketing_company | `main` / `8bbcfb764af4beefd033b83a322fe7f9395d43d5` | 23 | 23 | 0 |
| Fitness-App | `master` / `3da7737e388434250ef61a1e24cd67f8cab5c4ad` | 88 | 88 | 0 |
| Remote-Quality-Delivery-Office-Platform | `g0-foundation` / `e10ee440c9da5d127870a1075939d18ab55ead8b` | 29 | 29 | 0 |
| ERP-Virtual-Economy-Digital-Business-Universe | `main` / `d361fab0c3b251ff3c55f681bd2e192bb36c0019` | 31 | 31 | 0 |
| TENDER | `main` / `90cd8864e380654f215424655aa607e82d2be27a` | 23 | 23 | 0 |
| db_test_tool_clean | `main` / `184e528f00921feee36b33695b72b87263525bff` | 11 | 11 | 0 |
| **Total** | **10 repositories** | **440** | **426** | **14** |

## The Fourteen Unpaired Documents

### ERP_MCP — 13 files

```text
docs/CHATGPT_PLUGIN_USER_GUIDE_RU.md
docs/ERP_MCP_CHATGPT_RUNBOOK_RU.md
docs/INSTALLATION_GUIDE_RU.md
docs/LESSONS_LEARNED_RU.md
docs/NATIVE_REPORT_ACCOUNTANT_REQUEST_RU.md
docs/phase2/CONTRACTS_AND_API_RU.md
docs/phase2/DECISIONS_AND_SOURCES_RU.md
docs/phase2/NATIVE_REPORT_PROTOCOL_RU.md
docs/phase2/PACKAGE_COMPLETION_RU.md
docs/phase2/PLAN_PHASE2_RU.md
docs/phase2/STORIES_PHASE2_RU.md
docs/phase2/TDD_PHASE2_RU.md
docs/phase2/TEST_PLAN_PHASE2_RU.md
```

All thirteen had their **existing contents translated in place** in [draft ERP_MCP PR #38](https://github.com/xLZDx/ERP_MCP/pull/38). Original filenames are intentionally retained until every link/consumer can be migrated. The PR adds two additional English translations of existing README files (fifteen changed files total). This does not mean the changes have been merged.

### Personal_Decision_Command_Center — 1 file

`docs/agents/MVP1_AUTONOMOUS_HANDOFF_PROMPT_RU.md` was translated **in place** in [draft PDCC PR #146](https://github.com/xLZDx/Personal_Decision_Command_Center/pull/146), retaining two literal owner-owned ZIP filenames with Cyrillic, as those are source-file identifiers rather than author prose.

## English Sibling Content — Ten Direct Checks

To validate beyond filenames, **one existing English HTML counterpart from each repository** was fetched through the connected GitHub source and checked for Cyrillic:

1. `ERP_MCP/reports/HYBRID_ANALYTICS_ROUTE_2026-10-07.html`
2. `ERP/reports/tdd_plan_remediation_2026-10-03.html`
3. `Personal_Decision_Command_Center/reports/WQ10_12_13_final_status_2026-09-19.html`
4. `PM_Bridge/reports/COMPOSER_CARD_MARKUP_GATE.html`
5. `Virtual_marketing_company/reports/VMC_FALSE_ALARMS_AND_FIVE_STEPS_2026-09-05.html`
6. `Fitness-App/reports/citation_verification_report.html`
7. `Remote-Quality-Delivery-Office-Platform/reports/R12_CONDITION3_CLOSURE_2026-09-03.html`
8. `ERP-Virtual-Economy-Digital-Business-Universe/reports/erp_proc4_r_shared_1_2_closure_2026-08-21.html`
9. `TENDER/reports/G1_4_review_status_2026-09-04.html`
10. `db_test_tool_clean/db-testing-tool/reports/2026-08-21_r1_false_green_investigation.html`

**Result:** **10/10 fetched English sibling files had zero literal Cyrillic.** This is a **sample**, not a scan of all 426 counterparts or proof of translation fidelity.

## Updated Work Priority

1. **Do not blindly retranslate all 426 already paired reports.** First audit their actual English content, source provenance, links and current applicability.
2. Review and merge the thirteen translated ERP_MCP and one PDCC unpaired document **only after repository-specific governance approval**.
3. Scan files **without** Russian name markers, including source comments, code strings, project-wide notes, non-default release branches and active user-facing templates.
4. Keep native-language application localization, signed/historical data and executable operator tokens byte-exact where required. See the [English authoring policy](GITHUB_ENGLISH_AUTHORING_POLICY.md).
5. Reconcile the earlier path-only queue so `ALREADY_PAIRED_UNVERIFIED` and `TRANSLATED_IN_DRAFT` are never labeled `NOT_STARTED`.

**Conclusion:** The 440-marker estimate remains correct **as a filename count**, but **only 14 lacked a conventional English sibling**, and all 14 have English prose proposed in two draft PRs. **Owner-wide GitHub language migration remains IN PROGRESS** because full content, code, comments, historical discussions and other branches have not been verified.
