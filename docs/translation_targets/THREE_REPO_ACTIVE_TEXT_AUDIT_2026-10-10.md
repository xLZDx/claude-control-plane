# Three-Repositories Markdown/TXT Language Scan — Exact-HEAD Evidence

**Date:** October 10, 2026  
**Scope:** Every tracked `.md` and `.txt` file in the three exact Git trees below.  
**Status:** SELECTED SOURCE-TEXT SCAN COMPLETE; not all-branches, full-code, historical discussion or product-language migration.

## Verified Inventory

| Repository | Git tree SHA | Files read | Zero literal Cyrillic | With Cyrillic |
| --- | --- | ---: | ---: | ---: |
| `Usefull_agents_and_skils` | `52af4dff2b19a351ac77d219d09a9ec7852fd466` | **49** | **48** | **1** |
| `PM_Bridge` | `c1ee188b23fa8a3504ecd633b3f7582d666f49f8` | **34** | **21** | **13** |
| `TENDER` | `212e4a64eb2a45df95ed548d096b3d3078dd198f` | **32** | **23** | **9** |
| **Total** | **3** | **115** | **92** | **23** |

**Method:** Enumerated tracked paths with exact Git trees, read every Markdown/TXT file through the connected GitHub APIs and tested the Unicode Cyrillic range U+0400–U+052F. Full body was inspected programmatically for this literal character class; positive lines were sampled in context for classification. The large PM_Bridge `core/DECISION_LOG.md` was read using its Git blob `2449e9ada773d99b573d98820a5226587c95ca2e` after the normal file-content method returned an empty payload. The full blob has approximately **1.65 million characters and 324 Cyrillic-bearing lines**. The TENDER `core/DECISION_LOG.md` is approximately 453,000 characters and has **91 Cyrillic-bearing lines**. Neither historical record was changed.

A no-Cyrillic result is a **character test only**, not proof of semantic English-language completeness. Non-Markdown code, HTML reports, other refs, archived discussion comments, templates and binary/LFS assets are outside this cohort.

## Global Agents and Skills — 49/49

**48 files** contained zero Cyrillic. The one exception is:

| File | Git blob SHA | Reason to retain exact source literal |
| --- | --- | --- |
| `skills/rosetta/SKILL.md` | `1a3d8a96ae982d3cf374cdd03477f0d0e1d23112` | Authorization rule accepts both Latin `GO` and a two-character Cyrillic variant (U+0413 U+041E). Replacing that variant would change executable authorization semantics. |

This covers all global repository agent Markdown and skill/reference Markdown files on the inspected default tree, without changing prompts or execution policies.

## PM_Bridge — 13 Exact-Blob Source-Language Exceptions

| File | Git blob SHA | Classification |
| --- | --- | --- |
| `config/conversations.md` | `8ccc8f1ab89b08d3f8c07ad4dfe6ec6956ae089f` | User-defined project display name |
| `config/profiles/EXECUTION_AUTHORITY.md` | `0badb4e69a1bdc625bd2e809f1f7b519384b08d0` | Verbatim owner authorization/tool-policy quotation |
| `core/AGENT_HANDOFF_2026-08-27.md` | `c83537e6426c025730afe3e915853d4e7ecdec17` | Exact bilingual execution marker |
| `core/DECISION_LOG.md` | `2449e9ada773d99b573d98820a5226587c95ca2e` | Append-only operator decisions and quotations |
| `core/DESIGN_MULTI_DAEMON.md` | `1b96fba9aba69c3abfe4ef8563dfc4d50ac9d9c4` | Original architecture instructions from owner |
| `core/GATE_2_SCOPE.md` | `4a7654069f65b86ce4509ba3d17e61f3ca2f1398` | Potential mixed-script gate tokens; U+0420 visually resembles Latin P |
| `core/GATE_4_SCOPE.md` | `c1d9105f62b1f67d32004cdb20187208d4d968c4` | Historical review.js no-change quotation |
| `core/GATE_5_SCOPE.md` | `e1f1b1dc46eaff16a68f17f8acb4377c8ffe1542` | Historic identifiers with mixed-script gate references |
| `core/HANDOFF.md` | `c6144935caba4fe1423efbd25891576d3a87527e` | GO/push operator instructions |
| `core/HANDOFF_2026-08-26_superseded.md` | `935a6ce828e471e9e56c2cbb223a5d06be5807db` | Superseded operator quotations |
| `core/HANDOFF_2026-09-13.md` | `7fb1f6cf879402e601527a55f813d077c4eacd19` | Exact stop/go and commit boundary quotations |
| `core/HANDOFF_NEXT_SESSION.md` | `bdf2af0de6c4f0a27a710a60cbbfaf3e7d6a79b0` | Operator stop and transport instructions |
| `core/ROADMAP.md` | `a4a817e2307ae443161b2c5d94043c97532babba` | Dated operator quotations and project plan record |

**Review finding, not a proposed direct edit:** Some old scope documents mix Latin `P` and Cyrillic U+0420 in visually similar gate labels. Do not normalize by find-and-replace: first identify whether the literal strings are parsed contract values, historic references or only typography. Track normalization separately with all consumers/tests.

The [existing PM_Bridge draft PR #1](https://github.com/xLZDx/PM_Bridge/pull/1) has two English historical Markdown companions. Both were directly checked at HEAD `c1ee188b23fa8a3504ecd633b3f7582d666f49f8`: zero Cyrillic, two resolving original-report links, original `.ru.html` files retained and Markdown-only PR changes.

## TENDER — 9 Exact-Blob Source-Language Exceptions

| File | Git blob SHA | Classification |
| --- | --- | --- |
| `core/DECISION_LOG.md` | `83af42ea61ea694b77e6c766cd5fb1d7a46286f2` | Append-only original financing/scope decisions |
| `core/PLAN_MASTER_GATES.md` | `b04cbbfcd6bc5fa1f337cfbca49b73444d7913f0` | Original owner instruction and official program terms |
| `core/PROJECT_CHARTER.md` | `3c711cfd020dda0646b81e8cc4a2cf6a932fb2db` | Exact owner taxonomy and geography; English explanations present |
| `docs/architecture/G2_DECISION_PACK_MODEL.md` | `6a4ea53c129aba60fa70ae4dc4ffb78716762803` | Literal gate GO message |
| `docs/compliance/CTIF_MF_FOLLOWUP_DRAFT.md` | `f0c521621777d21d7301b7f8a781d47bb13986e3` | Quoted, explicitly unverified source publication-date statement |
| `docs/product/FUNDING_SOURCE_CANDIDATES.md` | `ff578ae5e3d62d01f0b7a2c4ff54d6dcccd86946` | Named Russian funding programs and quoted evidence |
| `docs/product/G1_SCOPE_BOUNDARY.md` | `ecac15d9f6c2784f5f4ea94e9670f9436982f138` | Verbatim owner categories/geography |
| `docs/product/PORTFOLIO_INTEGRATION_INTENT.md` | `a0276be34fa46b596751c4be1f1720267d48ec43` | Original quoted project-unification instruction |
| `docs/product/Q10B_SHORTLIST_RECOMMENDATION.md` | `31e2c75f885de1ec170d687136d66ae674eb8f54` | Original program names and verified eligibility evidence |

The [existing TENDER draft PR #1](https://github.com/xLZDx/TENDER/pull/1) contains three English historical companions. On exact HEAD `212e4a64eb2a45df95ed548d096b3d3078dd198f`, all three had zero Cyrillic and a valid original-report relative link. Only those three Markdown files changed; original Russian HTML and economic/source terms remain unchanged.

Official funding-program names and statutory source text should retain their source-language spelling. Operator quotes may have English glosses, but the original wording must remain attributable; translation alone is not current legal eligibility verification.

## Independent In-Chat Review Perspectives

- **Source/provenance:** Record all 23 exception blob SHAs; leave append-only decisions and original operator quotes intact.
- **Security/functional:** Bilingual approval markers and visually confusable gate IDs are **contract-sensitive**, not safely normalized through a broad language filter.
- **Documentation:** Checking local links and literal Cyrillic is necessary, but does not establish complete line-level English translation fidelity.
- **Independence:** These are separately reasoned perspectives **inside this conversation**, not external AI reviews and not executed runtime tests.

## Disposition

All **115/115 tracked Markdown/TXT files in these three pinned default trees** have now been read for literal Cyrillic. **92** have no such characters, **23** need intentional source preservation or separately reviewed normalization. **No original source, approved content, runtime, Git history, current branch or actual publishing authority was changed.**

Owner-wide English migration remains **IN PROGRESS**, and other branches, code comments, historic discussion posts, HTML and remaining repositories still require verification.
