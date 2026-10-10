# English Translation Queue — ERP_MCP

Inspected default branch: `main`; Git tree SHA: `cac886dcfb0d749892c60dc78902dea918196fdd`.

**Status:** PENDING. These 19 items were selected by Russian-language filename markers. Names are not proof of text language. Each candidate requires classification, faithful English translation, linked provenance, and review on a fresh exact HEAD.

## Candidate files

| Path | Blob SHA |
| --- | --- |
| `docs/CHATGPT_PLUGIN_USER_GUIDE_RU.md` | `ac433da1c97efa3d0e103a54c31f51af7efe00ed` |
| `docs/ERP_MCP_CHATGPT_RUNBOOK_RU.md` | `21560bef731df2049e3182deac47b31ae414de94` |
| `docs/INSTALLATION_GUIDE_RU.md` | `ca745ebd506e9eda4b51158c1efbf568f260e25d` |
| `docs/LESSONS_LEARNED_RU.md` | `72a691369993ff1c15ff147a41a508ea1da44749` |
| `docs/NATIVE_REPORT_ACCOUNTANT_REQUEST_RU.md` | `033e702f4541cb06151dbdfff69314d83f5f6a36` |
| `docs/phase2/CONTRACTS_AND_API_RU.md` | `0d77bc2f45a792c76f90a9a3785ec9d2b09f60f1` |
| `docs/phase2/DECISIONS_AND_SOURCES_RU.md` | `6d14e3b04ccbde0f4c6be43ffbd3dc9d94b4c17e` |
| `docs/phase2/NATIVE_REPORT_PROTOCOL_RU.md` | `2d402cc470bc8adc845310b7eb4e1c0fb6bf1a34` |
| `docs/phase2/PACKAGE_COMPLETION_RU.md` | `af2575414d5e5057c59b07c81008ff96f24f8824` |
| `docs/phase2/PLAN_PHASE2_RU.md` | `9bc74554ea229082a0604138c02d5e5be26ca481` |
| `docs/phase2/STORIES_PHASE2_RU.md` | `3006be94f3ae986c03bfa955954033b59150378b` |
| `docs/phase2/TDD_PHASE2_RU.md` | `c9b23e74204208f1d0f512f8577429f536cce81f` |
| `docs/phase2/TEST_PLAN_PHASE2_RU.md` | `75b89f2ce535625eb4afab4bb02b5b76637884a1` |
| `reports/DAD_MATERIALS_AUDIT_2026-10-07.ru.html` | `42d50db0598bdaf81489c0696fe1ce868f8118ff` |
| `reports/ERP_MCP_RC_HANDOFF_2026-10-07.ru.html` | `fd1b749ba01a7bbbfe81157715329f6580cf8ced` |
| `reports/HYBRID_ANALYTICS_ROUTE_2026-10-07.ru.html` | `ddcde063d67bbc8571d695277bfc5f20f90dbbe7` |
| `reports/MACHINE_TWO_SOURCE_521_1_2026-10-08.ru.html` | `e422ce2d20661ace9f94f5c137331b6415cf5a56` |
| `reports/real1c/REAL_1C_818HA_L2_REPORT.ru.html` | `c4ecbce2dd124d91b22a88c5bbe6a7015fe109f4` |
| `reports/real1c/REAL_1C_818HA_L2_TEST_DETAILS.ru.html` | `fb3ac510d507be2513ea07261f3ada8b91e18034` |

## English Draft Validation — October 10, 2026

- [ERP_MCP draft PR #38](https://github.com/xLZDx/ERP_MCP/pull/38), exact draft HEAD `8d17448cf2788f48a2b3f26eb70800cefed4d992`, contains 15 translated Markdown documents.
- All 15 were directly re-fetched from GitHub and checked: zero Cyrillic, **74 relative link targets resolved**, no unbalanced triple-backtick fences (**58 delimiter lines**). See [exact-head QA table](ERP_MCP_DOCS_QA_2026-10-10.md) for every original path/blob SHA.
- `_RU.md` filenames were kept to avoid link breakage, despite draft English contents. This is a compatibility compromise, **not** bilingual source parity.
- Semantic review, Markdown anchor rendering, command correctness on actual 1C hosts and branch merge remain pending. **Do not infer Phase 2 production readiness, a new native 1C test, IAM approvals or a release GO.**

## Complete Known Russian-Named Cohort — October 10

[Six-report exact-SHA review](ERP_MCP_HISTORICAL_REPORT_AUDIT_2026-10-10.md) confirms that **all 19 original Russian-named candidate documents have English coverage**: 13 operational/Phase 2 Markdown documents have English contents proposed in [ERP_MCP #38](https://github.com/xLZDx/ERP_MCP/pull/38) (draft, **not merged**), and six Russian historical HTML reports already had `.html` English companions. All six English HTML files were directly fetched; four contain zero Cyrillic, while two contain native-language 1C/test evidence (**23** and **39,178** literal Cyrillic characters). Both real-1C report links resolve. Do **not** translate the original source/banking data in place. English content and shell exist; semantic/1C/data-field integrity still require review.

**This closes missing-English-counterpart inventory for the 19-file selected cohort only. It does not close the entire ERP_MCP repository or production-readiness program.**

## Constraints

Keep API identifiers, structured content, tests, historical decisions and financial/private source values unchanged. Do not silently translate real 1C metadata identifiers. Translate immutable reviews into separate English companion records with attribution where needed.
