# Virtual Marketing Company — Source-Code Language Classification

**Inspection date:** October 10, 2026  
**Repository:** `xLZDx/Virtual_marketing_company`  
**Source tree pinned to:** `2b6604a1a52f1d8ec67675fada7330b674573bf1`  
**Method:** Connected GitHub `fetch_file` reads of **25 selected non-test application/source files**, with per-file Cyrillic counts. No source file or business record was modified.

## Actual findings

- **25 of 25 selected application/source files were inspected.**
- **18** contained no literal Cyrillic characters.
- **7** contained Cyrillic, with the exact Git blob SHAs and character counts below.
- Roughly 35 other detected code/test/deployment files in the repository **were not inspected in this targeted pass**. Do not claim a completed whole-repository scan.

| Git path | Blob SHA | Cyrillic chars | Classification and required action |
| --- | --- | ---: | --- |
| `gui/static/app.js` | `0380fc358cd0f4873ccfef0c34d2d500560b4065` | 312 | **ACTIVE RUSSIAN UI LOCALE.** Reply Queue and Progress Posts button names, alerts and metadata. Add an English locale in a scoped UI/i18n change, preserving semantics and selector tests; do not silently translate live UI under a documentation PR. |
| `landing/index.html` | `f7ee1fa5f3bb75801dcecd1fb22035e2491e72bb` | 1,331 | **ACTIVE RUSSIAN PRODUCT COPY.** Headline, product claims, CTA, consent/error text and source-of-truth annotations. Statements are tied to verified `ground-truth:S-xx`; an English campaign needs reviewed equivalence and explicit founder approval, not string replacement. |
| `scripts/distribution_gate.py` | `414d6d553e05f20f999b4fec67bb3b8f2bbf8d1c` | 279 | **LANGUAGE-SPECIFIC SAFETY PATTERNS.** Regex expressions detecting unsupported Russian absolutes, unmeasured claims, pricing/medical promises and trainer replacement; retain them. Removing or translating patterns would weaken moderation checks. |
| `scripts/draft_progress_post_llm.py` | `3e58344c0acc32f9c1aadaf8e7ece3b4219065b2` | 762 | **EXPLICIT RUSSIAN OUTPUT PROMPT.** The LLM system prompt requests a Russian social post tied to source evidence. Introduce a separately tested `language` contract before new English publishing; preserve `ESCALATE` and founder review. |
| `scripts/draft_reply_llm.py` | `18c82a9dc41050cef3e3a8e4eeb1bb9f5923fcb5` | 730 | **RUSSIAN SYSTEM INSTRUCTIONS WITH MULTILINGUAL OUTPUT.** Reply is instructed to match the question's language, identify the developer and refuse unsupported facts. Preserve this behavioral contract and existing Russian question fixtures. |
| `scripts/identity_guard.py` | `05522757e941cae145ba62bbade8df03bafcc37c` | 40 | **IDENTITY/PRIVACY TEST DATA.** Cyrillic personal-name/homoglyph and phone markers are threat-model examples or regex patterns. Translate surrounding prose only after checking negative privacy tests; retain the literal test vectors. |
| `scripts/scan_forum_questions.py` | `2156b78abc1d38aaf102c0330e859532e2043462` | 82 | **LANGUAGE-SPECIFIC DISCOVERY TERMS.** Queries for genuine Russian forum questions. Translation would change targeting; use a separately qualified multilingual query catalog, not blind replacement. |

The absence of literal Cyrillic from the other 18 selected code files does **not** prove that all their content is English or that their full product workflows are validated.

## Functional and Security Decision

**Do not rewrite the seven source files in this English-documentation PR.** These strings are either deliberate end-user localization, approved-language content, language-sensitive detection rules, or privacy test vectors. They fall under the exceptions in [English Authoring Policy](../GITHUB_ENGLISH_AUTHORING_POLICY.md).

Recommended future product work is a properly scoped multilingual-content feature, separately reviewed:
1. Add English translations for UI labels without replacing Russian UX; test both locales and selectors.
2. Prepare English landing copy with an exact claim-to-ground-truth mapping, approved by the founder before activation. Recompute post/campaign hashes and permissions for any changed text.
3. Parameterize prompt language explicitly, preserving identity disclosure and `ESCALATE` semantics; add paired Russian/English behavior tests.
4. Keep existing Russian-language regex detection and examples, and add English patterns only through security-reviewed new cases.
5. Record content provenance and deployment separately; translation evidence is not permission to launch a new campaign.

## Incomplete Scope

The audit did not scan every test and CI file, GitHub comments, release branches or encrypted/local artifacts. Remaining text should be inventoried on exact Git HEADs. Binary and LFS assets are not asserted to be English.

**Disposition:** Targeted source audit **DONE (25 files)**; full language migration **NOT COMPLETE**. No source change, secret exposure, marketing approval, or production deployment was carried out.
