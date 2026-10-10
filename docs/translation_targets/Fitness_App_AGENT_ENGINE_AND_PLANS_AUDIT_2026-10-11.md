# Fitness-App — Exact-HEAD Agent Engine and core/plans English Audit

**Date:** October 11, 2026  
**Fitness-App Draft PR:** [#1](https://github.com/xLZDx/Fitness-App/pull/1)  
**Exact project HEAD inspected:** `9eb9a3c93c0cdf3fd3b7cee528478b1d44fa0417`  
**Status:** TWO COMPLETE DIRECTORY COHORTS INSPECTED (30 + 43); not full-repository or independent semantic review.

## Complete source-language inventory for these two folders

| Folder | Original Markdown/TXT inspected | No Cyrillic | Contains literal Cyrillic | Action |
| --- | ---: | ---: | ---: | --- |
| `core/agent-engine-v2.3.1/` | **30/30** | **30** | 0 | Already English. No duplicate translations or agent token spending |
| `core/plans/` | **43/43** | **18** | **25** | Nine substantive Russian plan narratives given English companions; 16 other documents retain attributed source quotes, UI labels or authorization markers |
| **Total** | **73/73** | **48** | **25** | Original blobs intact |

The **30** agent-engine Markdown files were individually fetched by their exact tracked Git blob SHA; no literal Cyrillic. This included the version/contract reviews, governance, recommendation engine specs, test matrix, packaging and tool prompts. Their presence in a separate project directory does not certify the correctness of the deployed agent-engine behavior.

The **43** source plan Markdown/TXT files were also individually fetched and scanned. [Plan language/translation index](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/plans/ENGLISH_TRANSLATION_INDEX.md) lists each of the nine substantial translations plus all **16** source-bound exceptions with the exact original SHA.

## Nine new English translations, verified individually

| Original core/plans path | Original Git blob SHA | English companion Git blob SHA | Contract-sensitive scope preserved |
| --- | --- | --- | --- |
| `core/plans/B1_RECOGNITION_MEASUREMENT_2026-08-07.md` | `36798e93ef805004c32a22fbab7755166dcbdc09` | [`B1_RECOGNITION_MEASUREMENT_2026-08-07.en.md`](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/plans/B1_RECOGNITION_MEASUREMENT_2026-08-07.en.md) — `5717138a72cb7dd01289ace565ee2daebe2a0b91` | Model-v1 OOD measurements; no retraining on owner test photos |
| `core/plans/B3_MEDIA_DIAGNOSIS_2026-08-07.md` | `0ea49a190a776e272c0fc68a0dd60d4f8e8f5f1c` | [`B3_MEDIA_DIAGNOSIS_2026-08-07.en.md`](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/plans/B3_MEDIA_DIAGNOSIS_2026-08-07.en.md) — `d013b0b657b389c7ada9b5875f079ab164501348` | Corrected false-positive media diagnosis |
| `core/plans/B5_DATA_SOURCES_2026-08-07.md` | `3dc76b32737a08b74aecf587e18a86ac37775a5d` | [`B5_DATA_SOURCES_2026-08-07.en.md`](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/plans/B5_DATA_SOURCES_2026-08-07.en.md) — `81801c09e9c7896a88b4474e732258880422c6c0` | Actual data-source measurements and later Roboflow update, no leaked key |
| `core/plans/B5b_TEXT_ANCHOR_2026-08-07.md` | `5a5acff8b439b9caf348af8eb820105daaa5912b` | [`B5b_TEXT_ANCHOR_2026-08-07.en.md`](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/plans/B5b_TEXT_ANCHOR_2026-08-07.en.md) — `1c4dc139aa64286337946ba0cb7fd75c2464bdd4` | Printed-machine-label provenance and original confidence bounds |
| `core/plans/O0_ONBOARDING_SCHEMA_2026-08-12.md` | `937b3b8643f35312209f022efdd09e2c25d9c126` | [`O0_ONBOARDING_SCHEMA_2026-08-12.en.md`](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/plans/O0_ONBOARDING_SCHEMA_2026-08-12.en.md) — `dbf1d504303496f05b32dbb2b070b1f56b790f4d` | Schema proposal ONLY, no user-data migration; source enum-count contradiction flagged |
| `core/plans/PLAN_BUGS_2026-08-13.md` | `a3df2739e696be057421873bd625fde44f356de9` | [`PLAN_BUGS_2026-08-13.en.md`](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/plans/PLAN_BUGS_2026-08-13.en.md) — `43cbd82b9bde51916ae15a7615073273642c97b1` | Dated per-bug gate state, September 16 no-photo-export WONT_BUILD |
| `core/plans/PLAN_R11_DECISIONS_2026-08-12.md` | `365deb5f85deff1f0734bcac7f855fd9db359d4c` | [`PLAN_R11_DECISIONS_2026-08-12.en.md`](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/plans/PLAN_R11_DECISIONS_2026-08-12.en.md) — `0befedc3df80720c57ef1d55c206b37778ff2cd6` | Original owner decisions, P4 cancellation, O-series supersession |
| `core/plans/PLAN_REDESIGN_REMAINDER_2026-08-12.md` | `6627b604530d81cec2a6e6f54a90d551e965bf61` | [`PLAN_REDESIGN_REMAINDER_2026-08-12.en.md`](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/plans/PLAN_REDESIGN_REMAINDER_2026-08-12.en.md) — `b19c8e78f5cb2c7ba3e6c3b11830a03b8e305a46` | Device verification absent at historical checkpoint, photo consent/export boundaries |
| `core/plans/RESUME_O_SERIES_2026-08-12.md` | `e8e3da56dadda1368d12603b168e7518ef733208` | [`RESUME_O_SERIES_2026-08-12.en.md`](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/plans/RESUME_O_SERIES_2026-08-12.en.md) — `6626ba3629686bfc60bb18c0f8238bb97054e474` | O3/O4 completed; O9 skipped; explicit separate signing/package GO |

**Exact-HEAD QA:** All nine companions were re-fetched by their **Git blob SHA**. Each had zero Cyrillic, an unchanged original source blob, zero broken relative Markdown paths and an even number of triple-backtick fence lines. The [plan index](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/plans/ENGLISH_TRANSLATION_INDEX.md) itself had **34 valid local links, zero missing**, and the updated [core index](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/INDEX.md) had **39 local links, zero missing**. The root English README had **12 valid local links**. All navigation files contained zero Cyrillic.

At the tested HEAD, the **Fitness-App PR #1 diff contained 29 Markdown-only changes**. No Flutter, Firebase, source data, tests, private local device, ML training pipeline or historical source files were changed.

## Updated Fitness-App selected-scope arithmetic

Combine this **new disjoint 73-file folder audit** with the preceding [94-file active text audit](Fitness_App_ACTIVE_TEXT_AUDIT_2026-10-11.md):

| Verified selected unique original sources | Count |
| --- | ---: |
| Earlier active agent/command/skill/root/core file cohort | 94 |
| New complete agent-engine and plans folder cohorts | 73 |
| **Total distinct original text paths inspected** | **167** |
| Paths containing zero literal Cyrillic | **121** |
| Source paths containing any Cyrillic | **46** |
| Substantive historical English core companions previously created | 6 |
| New substantive plan English companions created in this pass | 9 |

**Important:** The 46 Cyrillic-positive source files do not all need replacement; approval tokens, signed/dated operator words, and Russian-language app/test evidence are deliberately preserved. The **15** new English companions are isolated proposed draft content, **not merged**.

This covers **167 distinct original Markdown/prompt paths**, not 167 completed semantic reviewer signoffs, and still excludes many Markdown files, code comments, history, non-default branches and GitHub review threads.

## Risk and reviewer perspectives (in chat, not external AI)

- **Source/veracity:** The B3 first diagnosis was incorrect and the corrected source explicitly says so; preserve the retraction. The v1 OOD ML confidence is historical, not certification of current classifier.
- **Security/privacy:** Roboflow source reported an API key once pasted into logs; the new English document includes the rotation warning but **never contains the secret**. Original gym photos are a holdout TEST set and must not be used in model training.
- **Data/schema:** O0 was a **proposal**. Its text says three new enums but names four; this contradiction remains documented, not silently converted into code. Existing user birth-year migration can be approximate.
- **Governance:** Signing/package identity changes require their own named GO; photo export was later governed as **WONT_BUILD**, and earlier unresolved status must not override that later decision. None of the original operator permissions is re-issued.
- **Verification limits:** This was an in-chat multi-perspective structural/source review. No external independent reviewer, Flutter tests, emulator, actual ML device performance, code changes, release or production verification occurred during the translation task.

## Remaining work

- Inspect the other source Markdown directories and unusually large append-only `core/DECISION_LOG.md`; do not rewrite the original record in place.
- Inventory Dart/TypeScript/Python/Kotlin comments and user-facing developer strings, production-locale RU fixtures separately.
- Check release/feature branches, GitHub open issue/PR review comments, source-to-English semantic fidelity and rendered section anchors.
- Obtain independent semantic review and follow authorized PR merge policy. **No branch merged by this translation.**

**Disposition: core/agent-engine 30/30 English; core/plans 43/43 inspected and all nine substantially Russian plan documents have source-linked English versions in draft. Whole Fitness-App GitHub is NOT yet certified English-only.**
