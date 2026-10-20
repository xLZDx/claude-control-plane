# English-Only GitHub Authoring Policy

**Scope:** All repositories currently accessible under the GitHub account `xLZDx`, including their active development branches, human-authored documentation, code comments and collaborative GitHub discussions.

**Default rule:** All **new or edited human-authored GitHub prose** must be in **English**.

## Covered Material

- Repository and nested READMEs, installation/runbook/architecture/product documentation.
- Human-authored prose in Markdown, HTML, MDX, text files, diagrams, explanatory labels and user-facing examples.
- Code comments, docstrings, test descriptions, developer log explanations and new human-facing diagnostic messages where internationalization is not intended.
- Commit messages, PR and issue titles/descriptions, reviews, release notes and new discussion comments.

Messages exchanged with the repository owner outside GitHub can use another language. Translating a file should not silently alter its original factual claims.

## Mandatory Exceptions and Preservation Rules

| Content | Required handling |
| --- | --- |
| 1C metadata names, customer chart-of-accounts labels, API/SQL/XML/JSON keys, IDs, source object references | Keep byte-exact if used for lookup, mapping, signatures, database relations or external interoperability; explain in English nearby. |
| User-entered financial, medical, legal or personal information; source text from external providers | Preserve as source data, protect access and provenance; never turn translation into a data mutation. |
| Deliberate localization: `app_ru.arb`, `equipment.ru.json`, approved multilingual test corpus | Keep locale values and keys intact. English docs can describe these. Do not disable a Russian product locale just to comply with a GitHub prose policy. |
| Signed/hash-bound content, marketing claims and approvals | Preserve original text and hashes; any translation that would become active content requires renewed human authorization and a new digest. |
| Historical audit evidence, immutable reviews, dated `*.ru.html` reports and archived decisions | Preserve the original. Add a linkable `*.en.md`/English companion with a source reference, exact historical SHA and limitations rather than rewriting evidence or Git history. |
| Names or established terms containing “Russian” in English, such as the **Russian twist** exercise | Do not rename existing asset filenames or application references. |
| Commands and existing technical paths | Keep executable syntax intact and test their equivalence; translation must not change the target environment or enabled permissions. |

## Repository Migration Checklist

1. Inventory every repository's current and maintained release/feature HEADs; do not infer a content language from its filename or root README.
2. Scan committed text blobs with the [read-only HEAD scanner](../tools/audit_tracked_language.py). Classify findings rather than applying blind search-and-replace. Missing LFS content, oversized blobs and unsupported text encodings mean **INCOMPLETE**.
3. Record source path/blob SHA, whether the material is current or historical, owner, proposed English destination and exception rationale.
4. Translate **without shortening acceptance criteria, changing model status, or strengthening old `NOT_RUN`/`PARTIAL`/NO-GO evidence**.
5. Preserve schema and API identifiers, commands, filenames and internal links until a separate, reviewed migration can update all consumers.
6. Validate English prose, relative/anchor links, Markdown fences, renderer output and relevant tests. If executable code, CLI output or templates change, run appropriate product regression.
7. Submit isolated draft PRs per repository. Do not overwrite dirty worktrees or merge against an unreviewed moving branch.
8. For current issues/PRs, translate the active description where ownership/policy permits. For historical signed decisions, add an attributed English explanation instead of rewriting the record.
9. Record exact PR HEAD and actual review/merge status in the [owner-wide tracker](https://github.com/xLZDx/claude-control-plane/issues/1). Do not claim the whole owner account is English-only until all in-scope content and maintained branches have been inspected.

## Evidence and Review Quality

- A zero-Cyrillic scan proves only the absence of that character range, **not semantic translation quality or completeness**.
- File-name indicators such as `_RU` and `.ru.html` are only candidates; not all are documentation, and many Russian strings appear in English-named files.
- Every translated operational step must preserve current approval gates, security scope, time windows, exact settings and safe rollback requirements.
- A successful unit test is not release approval, and a historical report must not be presented as a live current-state check.
- A documentation PR may still require rendering and link checks before merge.
- Never include private source excerpts, credentials, local secret values, customer data or proprietary code in a public translation ticket.

## Current Program

The owner-wide migration is **in progress**, not yet complete. The authoritative plan, initial 34-repository inventory, draft PRs and outstanding exceptions are tracked in [Issue #1](https://github.com/xLZDx/claude-control-plane/issues/1) and the [migration inventory](OWNER_WIDE_ENGLISH_MIGRATION_2026_10_10.md).
