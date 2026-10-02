---
name: html-report
description: Mandatory house format for substantive HTML reports: RU+EN files, Russian handover link, provenance/copy control, and Rosetta planned/DoD/status coverage when applicable.
---

# HTML report — front door

Use for substantive review/audit/status HTML reports. Routine short chat updates do not need a report.

Required output:
- reports/<NAME>.ru.html — Russian, published/linked to the operator.
- reports/<NAME>.html — English durable in-repo record.
- Same structure/content, localized language.
- Real <header> element, project/folder/git provenance immediately below it, and a copy-whole-page control.
- For Rosetta-governed work, every planned item shows Planned / Definition of Done / Status / remaining Tail if partial.

Do not hand-author the provenance/copy block. Conform both files:

    py -3 C:/Users/koros/.claude/tools/report_conform.py <repo>/reports/<NAME>.ru.html <repo>/reports/<NAME>.html
    py -3 C:/Users/koros/.claude/tools/report_conform.py <repo>/reports --check

Handover:
- show only the Russian artifact/link plus its full local path and a short substance summary;
- keep the English file as the durable repository record;
- PM/orchestrator mode: report is a checkpoint, continue the authorized program;
- ordinary mode: follow the current global/report hooks for handover behavior;
- program mode may defer intermediate reports when the operator explicitly authorized one final report.

Hooks are authoritative for due/format/handover checks. If a hook fires, fix the actual missing report/evidence rather than routing around it.

Read references/full-2026-10-02.md only for edge cases, legacy mode semantics, hook kill-switch history, or exact historical rationale.
