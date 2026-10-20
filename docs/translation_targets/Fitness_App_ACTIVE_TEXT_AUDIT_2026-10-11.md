# Fitness-App — Selected Current Documentation Exact-Blob Language Audit

**Audit date:** October 11, 2026  
**Repository:** [xLZDx/Fitness-App](https://github.com/xLZDx/Fitness-App)  
**English documentation draft HEAD:** `9fdfe74e4807e5e9e9415c1ee5bf0fb4d072d018`  
**Status:** SELECTED 94-FILE MARKDOWN/PROMPT COHORT INSPECTED; not the entire 329-file Markdown/TXT tree, Dart source, or all maintained Git refs.

## Coverage accounting

| Inspected cohort | Original tracked text files read | Zero literal Cyrillic | With literal Cyrillic |
| --- | ---: | ---: | ---: |
| `.claude/agents/*.md` | **30** | **30** | 0 |
| `.claude/commands/*.md` | **3** | **3** | 0 |
| `.claude/skills/*/SKILL.md` | **8** | **8** | 0 |
| Root/authoring prompts: `AGENTS.md`, `CLAUDE.md`, `FITNESS_APP_TASK_LIST.md`, `README.md`, `.github/prompts/rosetta.prompt.md` | **5** | **3** | **2** |
| Selected `core/*.md` engineering/history documents | **48** | **29** | **19** |
| **Total** | **94** | **73** | **21** |

All 94 contents were read through exact Git blob or path-versioned GitHub source. One originally malformed manually transcribed blob SHA for `core/OBS1_G3_REBASELINE_2026-08-27.md` was recovered with a direct path-versioned read, original SHA `6a735573b28de87b6a53afd3b97a86b81999e2be`; it contained zero Cyrillic. This count is **not** a claim that all repository documentation has been read.

The **two root/prompt exceptions** are `AGENTS.md` (blob `f08dca27c96e6b9e5441149479b364ea2d63ec17`) and `.github/prompts/rosetta.prompt.md` (blob `a65835598f864219f2f4845c981db9338925f2fb`): they accept an exact bilingual **GO** operator authorization marker using Cyrillic codepoints U+0413/U+041E. **Preserve byte-for-byte; replacing it would alter permission matching.**

## Exact-SHA classification of 19 Cyrillic-bearing core documents

| Core path | Original Git blob SHA | Reason for presence / separate handling |
| --- | --- | --- |
| `core/AUDIT_REPORT_2026-08-11.md` | `68361ea2042b9b46e7b4f19c59f22ce067a7bcdd` | Historical full Russian release-blocker audit; English companion added |
| `core/BACKLOG_2026-07-31.md` | `5481f6060e896ab8b2ca4f356a3bd541e258920d` | Russian UI error and screenshot strings, source-verbatim failure explanations |
| `core/CATALOG_STATE_2026-08-03.md` | `297ec65cb3074853b8fae7872c7f628189dc97e7` | Original operator request quotation |
| `core/CLIP_LICENCE_AUDIT_2026-08-03.md` | `da92bedd3f06ca0b688ba8ead3f0ed4585544e6b` | Original operator quotations on media/license behavior |
| `core/DATA_INVENTORY_2026-08-11.md` | `207db2c0c492fd206f7eae2bed3dd63eddeea218` | Verbatim original privacy concern |
| `core/EQUIPMENT_REGISTRY_EXPANSION_2026-08-03.md` | `bff118e418114cb94eb2440ced6f10e47653849b` | Operator quotation about unresolved vendor exercises |
| `core/G17_SCOPE.md` | `2a2e5ccc962335a98cc01bc538a148edf3a6f476` | Historical owner requirement for silhouette reference |
| `core/G4_STEP7_PRODUCT_E2E_2026-08-29.md` | `74350b372b63033b688d4b75df03807a8d4fabb3` | Real source UI prompts, recognition labels and live E2E observations |
| `core/HANDOFF_2026-09-25.md` | `29472e7f1d331b82d6b42d37c8d8ee481ac52976` | English companion translates Russian intro and original quote glosses |
| `core/LEGACY_CATALOG_REMOVED_2026-08-04.md` | `92f4acb3f6756844a62adb27d163cad1a7a4a0dc` | Original user decision on catalogue size/removal |
| `core/ML_PLATFORM_ARCHITECTURE.md` | `e7277f066e1c38c171ae52bb3a3aaff49dbb5580` | Original equipment/comment sample retained for ML data attribution |
| `core/PLAN_GYMS_AND_NEWS_2026-08-01.md` | `92ddfa5d66c357f7f4a2b12c1b38af576cd6c179` | Unapproved gym/news proposal, translated in source-bound companion |
| `core/PLATFORM_SCOPE.md` | `8ffc20f0421ccb4d168bf805b9835546fd547c53` | Attributed Russian phrase in prior release-status quote |
| `core/RESUME_2026-08-14.md` | `43369a4242c770d24ebcaea5a2debcf30fae996d` | Russian session-state report with strict consent/push rights, English companion |
| `core/RESUME_PROMPT_2026-08-04.md` | `61bc00eeb3e91941e755e6cac96f8002df52c5d3` | Literal bilingual operator GO token and quoted prior deferral |
| `core/SCAN_G1_SCOPE.md` | `9d055d6e60ea4435db2f9f5673be9e068573197d` | Source-verbatim operator scanner reference requirement |
| `core/SESSION_STATE_2026-08-07.md` | `14316c66ef2bb32c7662a3e8402291f1733d55a5` | Full Russian scanner/model session report, English companion |
| `core/SESSION_STATE_2026-08-08.md` | `858bcea21c5a491462c65bedad5c04e1faf2ef30` | Rolling Russian engineering session log, detailed chronological English companion |
| `core/STATE_H_GATES_2026-08-03.md` | `7b12f2ea9212cf701455ccbd50936b54df834294` | Canonical source UI labels and translated visual examples |

The other 29 checked core Markdown files had **zero Cyrillic**. Of the 19 source-positive core documents, six had substantive Russian narratives or historical chat handoff material requiring a **new source-linked English companion**; the remaining matches were principally quoted original operator decisions, exact UI/locale, historical test excerpts and preserved execution tokens. Their presence is **not** permission to replace machine-readable or user-supplied evidence.

## Six new English historical companions in Fitness-App Draft PR #1

| Original core document | Original blob SHA | English companion blob SHA | Key fidelity boundary |
| --- | --- | --- | --- |
| [`core/AUDIT_REPORT_2026-08-11.md`](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/AUDIT_REPORT_2026-08-11.md) | `68361ea2042b9b46e7b4f19c59f22ce067a7bcdd` | [`8e6e7603d3fb0e618f798fdcde8743ba44afd35e`](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/AUDIT_REPORT_2026-08-11.en.md) | Original Aug 11 historical release BLOCK, 1,886+107 test counters, privacy, Stripe, ML and adversarial correction |
| [`core/HANDOFF_2026-09-25.md`](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/HANDOFF_2026-09-25.md) | `29472e7f1d331b82d6b42d37c8d8ee481ac52976` | [`e5a107a9be1bd63d72ee0c5165cc5af651be0676`](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/HANDOFF_2026-09-25.en.md) | Dated owner/device handoff, permissions and camera cue glosses |
| [`core/PLAN_GYMS_AND_NEWS_2026-08-01.md`](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/PLAN_GYMS_AND_NEWS_2026-08-01.md) | `92ddfa5d66c357f7f4a2b12c1b38af576cd6c179` | [`9d30ad5620af67e2dd542448286b2d0a2385ce3a`](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/PLAN_GYMS_AND_NEWS_2026-08-01.en.md) | Unapproved gym-news proposal, six sections; historical vendor prices explicitly not revalidated |
| [`core/RESUME_2026-08-14.md`](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/RESUME_2026-08-14.md) | `43369a4242c770d24ebcaea5a2debcf30fae996d` | [`6980893c6e66cf70bdb7010f4429ec588efb6ed0`](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/RESUME_2026-08-14.en.md) | Historical uncommitted consent gate, 2,337/99 passing tests, open 1 MAJOR and 2 MINOR |
| [`core/SESSION_STATE_2026-08-07.md`](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/SESSION_STATE_2026-08-07.md) | `14316c66ef2bb32c7662a3e8402291f1733d55a5` | [`6ac6e9ed8cebb6280096a1ef7c5c69119c878b72`](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/SESSION_STATE_2026-08-07.en.md) | Scanner text provenance and protected 30-photo holdout; personal tester email deliberately not recopied |
| [`core/SESSION_STATE_2026-08-08.md`](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/SESSION_STATE_2026-08-08.md) | `858bcea21c5a491462c65bedad5c04e1faf2ef30` | [`f904f105299ca77236647a391e0fef3c551e53e9`](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/SESSION_STATE_2026-08-08.en.md) | Full chronological Aug 8 gate log, original GO/push and IAM boundaries, 1,741 final reported tests |

**Direct exact-HEAD validation:** All **6/6** English documents were re-fetched; **zero literal Cyrillic**, **all source blob SHA values unchanged**, **all local relative Markdown links resolve**, and code fences are balanced. [Core navigation index](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/core/INDEX.md) links all six English documents and their original source records.

The August 11 historical **BLOCK**, August 14 **uncommitted code and review findings**, August 8 **chronological changing push states**, screenshot-source labels, and original consent/deletion/GO boundaries are **not** overwritten or translated into a current permission.

## Additional Fitness-App documentation coverage from the previous pass

- [English redesign docs index](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/docs/Redisign/ENGLISH_DOCUMENTATION_INDEX.md) covers all **15 unique original design-document blobs** in the original 22-file `docs/Redisign` cohort: seven new English companions and eight originally English materials, with duplicate SHA sources not redundantly translated.
- [English historic HTML report index](https://github.com/xLZDx/Fitness-App/blob/docs/add-english-readme-20261010/reports/ENGLISH_HISTORICAL_REPORTS_INDEX.md) covers **88 of 88** original Russian-named reports with existing English HTML companions. Its separate SHA/content audit is maintained in `Fitness_App_88_REPORT_AND_REDESIGN_AUDIT_2026-10-10.md`, noting source-language UI/owner quotations embedded in twenty of the English HTML reports.

## Boundaries and remaining work

- Exact source/translation **semantic equivalence** and rendering need fresh independent review. Cyrillic checks and link checks are necessary but not sufficient.
- The active repository has far more than this selected cohort: **Dart/TypeScript/Python code comments and other uninspected Markdown/docs**, real app localization, multi-branch history, GitHub review discussions and generated content remain open.
- Preserve genuine Russian user interface, user health data, native exercise names, test strings, source screenshots, and owner-held approval tokens. **Do not** change training corpus, Flutter features, Firebase, Stripe, physical devices or CI through documentation translation.
- The English historical companions provide **no new execution, push, deletion, consent, external service access or release authority**.
- [Fitness-App PR #1](https://github.com/xLZDx/Fitness-App/pull/1) and [central migration PR #2](https://github.com/xLZDx/claude-control-plane/pull/2) remain **Draft / not merged**. Previous/current project acceptance rules and independent semantic review still apply.

**Disposition:** 94 selected active Markdown/agent source documents characterized; six additional English historical companions submitted in isolated draft; no project-wide or 34-repository English-only conclusion.
