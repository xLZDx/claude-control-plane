# claude-control-plane

A public, versioned mirror of a personal Claude Code **AI control plane**: global operating contract,
agent roster, skills, hooks, risk-based routing, model/effort policy, and the lint + eval tooling that
keeps them consistent.

It exists so that every change to the policy surface shows up as a reviewable git diff instead of
drifting silently on one machine.

## Layout

| Path | What it is |
| --- | --- |
| `mirror/CLAUDE.md` | Global operating contract (authority, GO, evidence, routing, git discipline) |
| `mirror/agent_routing.json` | Risk tiers R0-R3, effort tiers T1-T4, per-agent tier |
| `mirror/agents/` | Global agent definitions (frontmatter: model, effort, maxTurns, skills) |
| `mirror/skills/` | Reusable skills (thin `SKILL.md` + `references/`) |
| `mirror/hooks/` | PreToolUse/Stop hooks, including the Agent model gate |
| `mirror/commands/`, `mirror/core/`, `mirror/tools/` | Slash commands, decision log, helper tools and their tests |
| `mirror/control-plane/` | `agentctl.py` lint, `model_policy.json`, deprecation rules, tests, offline router eval |
| `scripts/export_from_claude_home.py` | Allowlist exporter with a fail-closed secret scan |

## Model policy (summary)

All automatic agents use the `sonnet` alias, Sonnet 5.5 minimum. Effort is risk-based
(`low`/`medium`/`high`/`xhigh`). Opus is never automatic: only with explicit operator consent for that
run, only at `high`. Haiku and lower families are not permitted for agents.

## Tracking changes

```
python -s scripts/track.py              # tests + export + local commit, only if something changed
python -s scripts/track.py --push       # same, then push to origin/main
python -s scripts/track.py --message "why the policy changed"
```

`track.py` runs the exporter tests and the exporter (which aborts on any secret hit) before it stages
anything, and commits with the GitHub noreply identity. To review by hand instead, run
`scripts/export_from_claude_home.py` and read `git diff` before committing.

The exporter copies only the names listed in `INCLUDE`. It does not copy `settings.json`, memory,
session transcripts, credentials, backups or generated registries. Files deleted at the source are
deleted from the mirror.

## What is deliberately not here

`settings.json` (machine-specific permissions and hook wiring), per-project memory, session history,
backups, and any project repository content. Paths such as `C:\Users\<name>` inside the mirrored files
are the author's real Windows paths; adapt them to your machine.

## English-only GitHub migration

- [English authoring and preservation policy](docs/GITHUB_ENGLISH_AUTHORING_POLICY.md)
- [34-repository inventory and status](docs/OWNER_WIDE_ENGLISH_MIGRATION_2026_10_10.md)
- [Corrected counterpart audit: 426 already paired, 14 translated in draft](docs/EXISTING_ENGLISH_COUNTERPARTS_2026_10_10.md)
- [Current issue and PR description audit](docs/ACTIVE_GITHUB_DISCUSSIONS_LANGUAGE_AUDIT_2026_10_10.md)
- [Global mirror and hook language exceptions](docs/GLOBAL_MIRROR_CYRILLIC_PRESERVATION_2026_10_10.md)
- [Read-only Git HEAD scanner](tools/audit_tracked_language.py) and [synthetic tests](tests/test_language_inventory.py)

**Do not edit `mirror/` just to remove Cyrillic.** It includes active GO/permission parsing, operator quotations and exported source files. Review and translate the upstream canonical files first; preserve literal authorization tokens and regenerate the mirror under its secret-scan rules.

## Status

Personal configuration shared as reference, not a supported product. No warranty. See `LICENSE`.
