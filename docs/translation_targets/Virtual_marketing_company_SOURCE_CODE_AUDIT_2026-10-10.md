# Virtual Marketing Company — Source-Code Language Classification

**Inspection date:** October 10, 2026  
**Repository:** `xLZDx/Virtual_marketing_company`  
**Source tree pinned to:** `2b6604a1a52f1d8ec67675fada7330b674573bf1`  
**Method:** Connected GitHub `fetch_file` reads of **60 selected application, deployment, warehouse and test files**, with per-file Cyrillic counts. No source file or business record was modified.

## Actual findings

- **60 of 60 selected code/test/deployment files were inspected** at the pinned exact source tree.
- **45** contained no literal Cyrillic characters.
- **15** contained Cyrillic, with the exact Git blob SHAs and character counts in the two tables below.
- This is a full inspection of the 60 specifically enumerated application/test/deployment files, **not** a scan of every tracked text file or all active branches.

| Git path | Blob SHA | Cyrillic chars | Classification and required action |
| --- | --- | ---: | --- |
| `gui/static/app.js` | `0380fc358cd0f4873ccfef0c34d2d500560b4065` | 312 | **ACTIVE RUSSIAN UI LOCALE.** Reply Queue and Progress Posts button names, alerts and metadata. Add an English locale in a scoped UI/i18n change, preserving semantics and selector tests; do not silently translate live UI under a documentation PR. |
| `landing/index.html` | `f7ee1fa5f3bb75801dcecd1fb22035e2491e72bb` | 1,331 | **ACTIVE RUSSIAN PRODUCT COPY.** Headline, product claims, CTA, consent/error text and source-of-truth annotations. Statements are tied to verified `ground-truth:S-xx`; an English campaign needs reviewed equivalence and explicit founder approval, not string replacement. |
| `scripts/distribution_gate.py` | `414d6d553e05f20f999b4fec67bb3b8f2bbf8d1c` | 279 | **LANGUAGE-SPECIFIC SAFETY PATTERNS.** Regex expressions detecting unsupported Russian absolutes, unmeasured claims, pricing/medical promises and trainer replacement; retain them. Removing or translating patterns would weaken moderation checks. |
| `scripts/draft_progress_post_llm.py` | `3e58344c0acc32f9c1aadaf8e7ece3b4219065b2` | 762 | **EXPLICIT RUSSIAN OUTPUT PROMPT.** The LLM system prompt requests a Russian social post tied to source evidence. Introduce a separately tested `language` contract before new English publishing; preserve `ESCALATE` and founder review. |
| `scripts/draft_reply_llm.py` | `18c82a9dc41050cef3e3a8e4eeb1bb9f5923fcb5` | 730 | **RUSSIAN SYSTEM INSTRUCTIONS WITH MULTILINGUAL OUTPUT.** Reply is instructed to match the question's language, identify the developer and refuse unsupported facts. Preserve this behavioral contract and existing Russian question fixtures. |
| `scripts/identity_guard.py` | `05522757e941cae145ba62bbade8df03bafcc37c` | 40 | **IDENTITY/PRIVACY TEST DATA.** Cyrillic personal-name/homoglyph and phone markers are threat-model examples or regex patterns. Translate surrounding prose only after checking negative privacy tests; retain the literal test vectors. |
| `scripts/scan_forum_questions.py` | `2156b78abc1d38aaf102c0330e859532e2043462` | 82 | **LANGUAGE-SPECIFIC DISCOVERY TERMS.** Queries for genuine Russian forum questions. Translation would change targeting; use a separately qualified multilingual query catalog, not blind replacement. |

The absence of literal Cyrillic from the other 45 selected code files does **not** prove that every sentence is English or that the associated product behavior has been validated.

## Additional Test and Deployment File Findings

The remaining 35 files in this selected application/test/deployment cohort were inspected after the initial 25-file assessment. **Twenty-seven had zero literal Cyrillic, and eight contained Cyrillic**, as detailed below. The four historical deployment shell scripts and five BigQuery SQL models inspected contained no Cyrillic.

| Git path | Blob SHA | Cyrillic chars | Classification and handling |
| --- | --- | ---: | --- |
| `gui/tests/test_gui.py` | `b23288880a90a6cb764e8c7aeca3b1e3c596236f` | 194 | **Synthetic Russian UI and privacy fixtures.** Tests use realistic lead questions, phone/name examples, decisions and Russian reply text. Keep exact assertions until separately changing the UI locale contract. |
| `scripts/test-business-os.py` | `e52154ea22291c0d2d0e939946d5b7cdd480ceb9` | 257 | **Marketing gate and product ground-truth assertions.** The tests search for actual Russian-language rules, unsupported prices, false technique claims and landing-page disclosure. Do not translate fixture assertions without migrating the source and maintaining negative protection. |
| `scripts/test-collector.py` | `37dc7e9363a9a8c9b815fd69c6501296420e5b64` | 63 | **Synthetic location/PII and legal-text regression fixtures.** Exact Cyrillic input verifies collector data classification and landing copy; preserve privacy coverage. |
| `scripts/test-distribution-slice.py` | `0c47008df622de6d1e289dd3126b3bc34bdaba38` | 1,352 | **Security/consent enforcement fixtures.** Russian content atoms, unsupported claims, identity leakage, prices and real approval-gate hashes test the actual language-specific safety contract. |
| `scripts/test-draft-progress-post-llm.py` | `d784e37c5cd25f01788c8179442c7a1b3e1526d3` | 82 | **Language-specific LLM response fixtures.** Sample drafts are deliberately Russian; do not replace until input/output language handling is tested. |
| `scripts/test-draft-reply-llm.py` | `f106e4cda1bfaf5b8af893a725e555f0c46c80ab` | 110 | **Multilingual reply-test fixtures.** Original Russian questions/replies verify pass-through, developer disclosure and output expectations; not GitHub prose. |
| `scripts/test-identity-guard.py` | `55278d67551d6f9b38319d6593e4a680ae19506f` | 10 | **Privacy attack vector.** The Cyrillic telephone marker tests leak detection; preserve the exact fixture. |
| `scripts/test-scan-forum-questions.py` | `52803990beebaa7f570373972ffe50a81ab8050b` | 162 | **Russian forum matching fixtures.** Cases cover relevant vs irrelevant equipment questions and body content; translation would change discovery semantics. |

**Method limitation:** This classification is from read-only GitHub blob content and inspection of the matched lines. No tests for these application modules were run during the language audit. Preserving the original text is safer than converting a real negative test into a passing but meaningless English-only assertion.

## Functional and Security Decision

**Do not rewrite the seven source files in this English-documentation PR.** These strings are either deliberate end-user localization, approved-language content, language-sensitive detection rules, or privacy test vectors. They fall under the exceptions in [English Authoring Policy](../GITHUB_ENGLISH_AUTHORING_POLICY.md).

Recommended future product work is a properly scoped multilingual-content feature, separately reviewed:
1. Add English translations for UI labels without replacing Russian UX; test both locales and selectors.
2. Prepare English landing copy with an exact claim-to-ground-truth mapping, approved by the founder before activation. Recompute post/campaign hashes and permissions for any changed text.
3. Parameterize prompt language explicitly, preserving identity disclosure and `ESCALATE` semantics; add paired Russian/English behavior tests.
4. Keep existing Russian-language regex detection and examples, and add English patterns only through security-reviewed new cases.
5. Record content provenance and deployment separately; translation evidence is not permission to launch a new campaign.

## Incomplete Scope

The audit does not cover every Markdown/HTML report, all files under hidden agent directories or the operational ledgers, GitHub comments, release branches or encrypted/local artifacts. Remaining text should be inventoried on exact Git HEADs. Binary and LFS assets are not asserted to be English.

**Disposition:** Targeted source/test audit **DONE (60 files: 45 with no Cyrillic, 15 requiring language-specific preservation/review)**; full language migration **NOT COMPLETE**. No source change, secret exposure, marketing approval, or production deployment was carried out.
