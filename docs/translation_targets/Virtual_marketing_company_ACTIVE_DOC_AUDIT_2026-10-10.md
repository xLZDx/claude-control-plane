# VMC — Active Documentation and Agent Instructions Language Audit

**Audit date:** October 10, 2026  
**Repository:** [Virtual_marketing_company](https://github.com/xLZDx/Virtual_marketing_company)  
**Source inventory HEAD:** `98e2cfc9910f0aab07bed99f7e1c4d41ed7dd109` (before the additional English companions)  
**Companion draft:** [VMC PR #1](https://github.com/xLZDx/Virtual_marketing_company/pull/1) on `docs/english-readme-20261010`  
**Status:** SELECTED CURRENT-DOCUMENT COHORT AUDITED; not an exhaustive all-Git/branch/code-language audit.

## Exact Scope and Method

Read-only inspection through the connected GitHub file API, pinned to the exact source HEAD. The selected **69 text files** were from active project/agent documentation and operational prose (rather than the already translated historical report cohort), including:

- `.claude/` agent and skill Markdown; `AGENTS.md`, `CLAUDE.md`, `MIGRATIONS.md`, package manifests and the root README;
- `company/`, `distribution/`, `evidence/`, `products/`, `docs/`, `collector/`, `gui/`, `warehouse/` and relevant deployment notes;
- the `deploy/collector-vps/docker-compose.yml` instructions.

Excluded by scope: `reports/` (separate 23/23 audit), code modules/tests (separate selected 60-file audit), `scripts/fixtures/`, `.github/` workflows, already added `*.en.md` companion files, non-text blobs, history and non-default branches.

**Result:** **48/69** selected files had no literal Cyrillic lines; **21/69** had one or more. No automatic replacement was applied to the 21 language-dependent/source-evidence files. Cyrillic detection cannot prove English quality, and the classification is not an independent legal or product-i18n signoff.

## The 21 Files Requiring Preservation or Separately Governed Translation

| Git path | Original blob SHA | Classification / action |
| --- | --- | --- |
| `.claude/agents/distribution-operator.md` | `17e08de85ee9b2974409fc39a8323da65ef5277a` | Russian negative examples and banned-claim lexicon used by the safety gate; preserve exact samples |
| `.claude/skills/answer-in-channels/SKILL.md` | `fc8ed8d38ee4a3e466bdfe28d8d38eb47a694edd` | Actual forum/question examples and CLI prompt inputs; language-dependent discovery |
| `.claude/skills/content/SKILL.md` | `4fd36e62aad1738530119ff29fcc0e56afc8cf30` | Universal-claim negative examples; preserve safety examples |
| `.claude/skills/find-channels/SKILL.md` | `cb0555c052e32bfc98010f663cad1e77b125ca91` | Exact user-facing Russian closing sentence; changing it changes agent behavior |
| `.claude/skills/find-humans/SKILL.md` | `88ca7d8024e3a631284f720f25d0923d8cd4d3f1` | Exact Russian user-facing closing sentence; behavior-specific |
| `.claude/skills/rehearse/SKILL.md` | `40aad8986c8c66359e85728bd18d17f9fb77c782` | Role-play user questions/STOP procedure; language-specific interaction |
| `CLAUDE.md` | `f5dfc0502dd70cce391bdca629252d086b5cd866` | Founder-owned literal push-governance markers and verbatim decision; never convert parser tokens |
| `collector/README.md` | `a28fe0f75cd8230f64aaf69f653a6356d0612b67` | Synthetic location and Unicode homoglyph security examples |
| `company/decisions.md` | `3908079a272c766a38dadae1d9f0c58ffd4a7340` | Append-only owner decisions, buyer/offer labels and negative marketing test claims; do not rewrite |
| `company/people.md` | `f356b6697c0dcfdb5062fdcfab50292c2408fb80` | Illustrative identifying-description warning; native-language PII example |
| `company/state.md` | `3febf8067faf6a39f328ad8f11a135de9c4273ac` | Owner-controlled motion hypothesis and recorded prompting instruction; translating in place could change meaning |
| `distribution/ad_targeting_research.md` | `eab6cbfc3245458a772933ece784dd5402e0bab7` | Dated research buyer quote and native platform/category names; separate qualified translation rather than rewriting |
| `distribution/candidates_found.md` | `bcc735c0a55efa1427f8d3ec022ae7f2ee30f434` | Original Russian/English discovered-channel research with names, evidence and counts; existing English companion is an explanatory summary |
| `distribution/claims.md` | `48f76607ee81af517c6ed4d4d0901ce3679c50f0` | Unapproved-claim and added-adverb examples; gate-sensitive |
| `distribution/content.md` | `8ad1c47ec4c3fda6510d441b9e6b0bcd7f987199` | Source-linked claim atoms and marketing drafts, some SHA/approval-sensitive; preserve original |
| `distribution/founder_actions_ready.md` | `15af9748f54ff90fe994dd8fd21fe1ceaf8c5bd9` | Founder-only approval templates; existing English companion, originals not authorization |
| `distribution/policy.md` | `ba5690f5efd6908a7f475335cc817a648cb8008c` | False-claim and Russian universal-quantifier safety examples; preserve the exact lexicon |
| `docs/04_LIVE_VALIDATION_PLAYBOOK.md` | `25b2a9f682d6a10f5b935699afbcb026e9d1f55b` | Original Russian staff-approach wording and false-activation example; new separate English documentary companion |
| `docs/mvp/FIRST_REAL_TEST.md` | `041af852573785584f2a22def95be94d579fe52e` | Canonical research/content consent scripts and participant prompts; never replace with unapproved English consent |
| `products/sptr/product.md` | `79f4fe78646d9eae81e8e2f3b04b84fb45e7adb8` | Founder-confirmed S/H/N source wording, first-value quotes and consent; new non-authoritative English companion |
| `products/vmc/product.md` | `f172bc18bf7d893b9c89b1aab620b615e2053c0f` | Deliberately false/true Russian claim examples for gate behavior; preserve |

## Two New English Companions (Documentation Only)

1. [`products/sptr/product.en.md`](https://github.com/xLZDx/Virtual_marketing_company/blob/docs/english-readme-20261010/products/sptr/product.en.md) — maps all **ten S**, **three H** and **one N** capability IDs into English, preserves the defined first-value protocol, research/content/recording consent separation, the three observed-outcome verdicts, unknown economics and six distribution hypotheses. The [original canonical product source](https://github.com/xLZDx/Virtual_marketing_company/blob/docs/english-readme-20261010/products/sptr/product.md) remains unchanged. The English wording is **not approved live marketing content**, a new ground-truth contract, or a current Fitness-App source verification.
2. [`docs/04_LIVE_VALIDATION_PLAYBOOK.en.md`](https://github.com/xLZDx/Virtual_marketing_company/blob/docs/english-readme-20261010/docs/04_LIVE_VALIDATION_PLAYBOOK.en.md) — translates the intent of the Russian staff-introduction script and retains the baseline / silent test / outcome rules. The original scripts and consent language remain operationally authoritative; the English version is an **unapproved explanatory translation**.

The source-bound English navigation index links both. No marketing approvals, founder signatures, runtime code, customer ledgers, accounting data or permission rules were changed.

## Quality and Risk Review (Independent In-Chat Passes)

- **Source-accuracy lens:** original owner-confirmed claims were not upgraded from H to S, N-01 was not introduced as a feature, and the exercise count remains `UNKNOWN`; exact permission questions remain bound to their canonical source.
- **Security/privacy lens:** preserve direct Russian samples used for claim rejection, identity/homoglyph checks, consent and privacy coverage; no blind Cyrillic ban in code or data.
- **Operational lens:** no owner-held `APPROVED BY`, `VERIFIED BY`, `BODY_SHA`, `RUN MODE` or push-policy marker was rewritten.
- **Reviewer-limits lens:** This is an in-chat multi-perspective review, **not** independent external AI-agent verification or execution of product tests.

## Remaining Program Scope

- Check all other Git text blobs and maintained release/feature branches (not just this selected cohort), non-Markdown templates and historical discussion comments.
- Review complete semantic fidelity, precise internal anchors and rendered Markdown after link verification.
- If the product is to have an English locale, implement it separately with functional tests and a founder-approved mapping from canonical claims, rather than silently activating this English document.
- Keep the draft PR unmerged until repository-specific acceptance and the current owner branch/gate rules are satisfied.

**Outcome:** Current-document inspection 69/69 selected files; **48 without Cyrillic, 21 source/language-specific and classified**; **two non-authoritative English guides** proposed in the VMC documentation PR; **no automatic alteration of live Russian language behavior**.
