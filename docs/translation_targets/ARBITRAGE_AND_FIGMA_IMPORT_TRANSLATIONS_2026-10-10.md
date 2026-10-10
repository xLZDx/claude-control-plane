# English Translation Continuation — Arbitrage Research and Fitness Design Imports

**Date:** October 10, 2026  
**Status:** NEW SOURCE-LINKED DOCUMENTATION IN TWO OPEN DRAFT PRS; not a release or product-design gate closure.

## 1. Arbitrage Strategy — Previously Mixed-Language Research

**PR:** [arbitrage-strategy #1](https://github.com/xLZDx/arbitrage-strategy/pull/1)  
**Exact draft HEAD:** `d05642f4c8ccd483b491b44934f0f9189a678d2b`

| Path | Blob SHA at reviewed HEAD | Change |
| --- | --- | --- |
| `README.md` | `7c677ccbde930e8656b195d254b43d2e3fff6901` | Add English navigation and historical research boundary |
| `docs/ARBITRAGE_RUSSIAN_PASSAGES_EN_2026-10-10.md` | `6523cf20c5248d8f6b77fd3df92c0648cff53eea` | English translation of the Russian-language parts of `arbitrage.txt` |

**Original source:** `arbitrage.txt`, Git blob **`41bcce07db11edc2f1256ea723d3f5ed4d9253c4`**, 796 lines including **77 lines with Cyrillic**. The original is unchanged.

The English translation covers the source's Weighted Multi-Level OBI explanation and illustrative Python docstrings/comments; HistGBT/TFT/DRL use cases; ghost-liquidity QA heuristic; English-only code/documentation decision; historical DuckDB and QuestDB architecture notes; and the proposed integration of streaming, forecasting, Web3 execution and strategy plugins.

**Safety and consistency qualifications retained:** Historical QuestDB/DuckDB statements conflict and are not silently reconciled; suggestions of guaranteed fills, zero gas, deterministic market advantage and spoofing detection are **not verified facts**; illustrative model thresholds remain untested hypotheses; no live-trading GO is implied.

The exact-HEAD GitHub diff contains **two Markdown files only**. Re-fetch QA: zero Cyrillic in proposed English files, **zero missing relative links**, and balanced fenced illustrative Python. No runtime, models, orders, credentials, deployment or exchange state changed.

## 2. ReviewExistingExamples — Russian Imported Fitness/Figma Prompts

**PR:** [ReviewExistingExamples #1](https://github.com/xLZDx/ReviewExistingExamples/pull/1)  
**Exact draft HEAD:** `a872a15690462f6841b84adca69b6ae69411c71c`

| English artifact | Git blob SHA at reviewed HEAD | Original source blob | Fidelity boundary |
| --- | --- | --- | --- |
| `src/imports/FIGMA_FULL_APP_REFACTOR_PROMPT_v1.3.en.md` | `e1acd2e34e9a329c75ae5fbe3aa2afe906b5254e` | `81538d09cb23d2c6acc8b84b61da5450128ca4cb` | Master historical v1.1 refactor brief + appended v1.3 update: all **29** numbered design sections, **17** DoD criteria, D1–D9 stop/review gates and 44-question internal Decision Registry governance; unverified app-feature assertions are explicitly qualified |
| `src/imports/FIGMA_DECISION_REGISTRY_SCREEN_PROMPT_v1.3.en.md` | `338807ec0e0627ac4eb9a31ef867aae964a75a62` | `230fc80a994c11c324f3b97f0c212590dd754525` | Fourth internal ResearchScreen tab; 44 decisions, filters, D6 blockers and Q39/Q19 corrections |
| `src/imports/OPEN_DECISIONS_REGISTER_v1.3.en.md` | `76c715450c3f59e09801337e88ec2705670b6d98` | `b39a24ae56d569e764388a701c17c50a2b51c26c` | All 44 historical questions/owners/options; 22/8/14 counts; hard blockers and duplicates retained |
| `src/imports/pasted_text/body-metrics-onboarding.en.md` | `aacb88196036708b61375cbf3cbf759e4d469084` | `6de60f3ffc1e346ea3dda8f039571e6785346e9b` | Eight requirement areas, adult/under-20 BMI behavior, Health Connect consent, accessibility, complete eight-deliverable request |
| `src/imports/pasted_text/progress-photo-compare.en.md` | `a6c24c07053988e4a3b58fdfd1c516811f494229` | `fef2d61026a0c87076cc12e1607411d31d7f2061` | All **20** photo progress design sections: capture, angle consistency, privacy, compare modes, explicit export and prohibited body/medical claims |
| `src/imports/pasted_text/tech-coach-module.en.md` | `518a6835f225cc6d0a9d1a97f6dce31e89ea3e27` | `bbd4d788052834a62d82f64aa6015f8095faed5d` | All **27** Technique Coach requirement sections, quality gates, live cues, privacy, open product questions and 18 DoD deliverables |
| `README.md` | `0e5c3847e7394ca0c915c8ebd64a72df8f694b52` | New draft English root | Links all six translations and describes them as unapproved source materials |

The original Figma screen prompt and open decision register each have **two identically hashed source copies**; only one English companion was created for each pair, with both originals linked. The original Russian inputs remain byte-exact.

QA on exact HEAD: **7 Markdown-only changed files**, zero Cyrillic in proposed English files, zero broken relative links, and unchanged original source blob SHAs.

**Important:** This is not a Flutter implementation, an approved copy rewrite, a signed stakeholder choice, medical advice, a new health-data permission or evidence that any of the 44 decisions have been closed. The translated requirements need independent semantic and design-governance review before becoming active product scope.

## 3. Independent In-Chat Adversarial Checks

- **Translation fidelity reviewer:** Compare all source line/range anchors and counts to the original blobs. No original evidence was overwritten and all status markers were retained.
- **Functional/product reviewer:** Imported prompts are design proposals, not requirements accepted by a running app. No current implementation evidence was fabricated.
- **Security and safety reviewer:** Financial execution models, user health information, consent flows and original programmatic identifiers are preserved; the English docs do not activate real-world workflows.
- **Limitations:** Code samples and user-facing texts were **not executed, rendered, medically validated or externally independently reviewed**. Working relative paths and a no-Cyrillic scan are not equivalent to semantic signoff.

## Disposition

**Two additional source-language documentation targets translated in existing isolated draft branches:** one arbitrage-research file's Russian passages and **six** unique imported Fitness App design requirements. Proposed changes cover **9 Markdown files** across the two PRs, while all original Russian sources and runtime artifacts remain unchanged.

**Not merged.** Owner-wide GitHub English migration remains open, and other imported Russian Figma prompts in `ReviewExistingExamples/src/imports/` still require individual translation.


### Master Figma refactor v1.1 + v1.3 source-version caveat

The file named `FIGMA_FULL_APP_REFACTOR_PROMPT_v1.3.md` begins with an internal `v1.1` heading and ends with a separate `UPDATE v1.3 — Decision Registry`. Its English companion preserves **both version markers**, all 29 numbered master sections and the appended governance contract, including **D1 STOP until review**, 17 historic acceptance criteria, Q19/Q20/Q21/Q23/Q26 hard blockers and the operator's locked Flutter selection (Q39). The original and `-1` duplicate share exact source blob `81538d09cb23d2c6acc8b84b61da5450128ca4cb` and were not altered.

At exact branch HEAD `a872a15690462f6841b84adca69b6ae69411c71c`, the new master English file has zero Cyrillic, **29 numbered sections**, valid original references, and the README links it without broken relative paths. The original brief claimed features such as 1,887 exercises and on-device form detection; those claims remain **unverified design premises**, never current source/runtime proofs.


## Structural fidelity cross-check — additional review of four imported sources

At exact `ReviewExistingExamples` draft HEAD `a872a15690462f6841b84adca69b6ae69411c71c`, the original and English counterpart blobs were individually re-fetched and compared for explicit scope markers:

| Imported source | Measured English coverage | Key negative-gate preservation |
| --- | --- | --- |
| Figma master refactor v1.1 + appended v1.3 | **29/29** numbered master sections; appended v1.3 decision update present | D1 STOP/required review and all **17** DoD criteria retained |
| Open Decisions Register v1.3 | **44/44** Q1–Q44 identifiers present in English | Hard blockers, provisional status and locked Flutter Q39 retained |
| Progress Photo Comparison | **20** numbered English sections, matching 20 original requirements | Explicit share preview, private photo use, no body score/medical claim |
| Technique Coach v1.2 | **27** numbered English sections | Open product decisions, low-confidence/pose loss, privacy constraints, complete DoD |

All associated original Git blob SHAs remained unchanged. These are **structural coverage checks**, not a word-by-word certified translation, UI rendering, independently executed product test or current Flutter feature validation.
