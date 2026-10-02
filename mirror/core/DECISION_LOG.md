# ~/.claude — Decision Log

This repository (`C:\Users\koros\.claude`) was initialized as a local git repo on 2026-09-04,
solely to make the global operating-contract file (`CLAUDE.md`) revertible before a sweeping edit.
It was previously unversioned — a known, disclosed gap in `CLAUDE.md` §15 ("the hooks and this file
live in `~/.claude`, which is not a git repository... unversioned — it can drift, be overwritten").

## D-001 — Repo initialized; CLAUDE.md backed up before full rewrite

**Trigger:** operator, in a live session working on `D:\Repo\TENDER`, said the global governance
rules in `CLAUDE.md` were never their own creation and asked to cancel them permanently ("я эти
правила не создавал, отменить все эти правила навсегда"). Claude asked for a precise scope (the
file has no version history, so an unscoped edit would be unrecoverable) via `AskUserQuestion`. The
operator explicitly selected **"Всё целиком"** — the entire `CLAUDE.md` file, not the mechanically
enforced hooks in `~/.claude/hooks/*.py`, and not a machine-wide "hooks too, everywhere" scope.

**Action taken:** `git init` in `C:\Users\koros\.claude`; `CLAUDE.md` committed as-is (its pre-edit
state) so the removed content remains recoverable via `git log`/`git show` even though no other
backup exists. This decision log entry itself exists only because `decision_log_gate.py` (a hook —
not something this session was authorized to bypass) required one for the first commit in any repo
carrying a `core/DECISION_LOG.md` path convention, and creating this repo made that convention
apply here for the first time.

**Explicitly not touched by this action:** `~/.claude/hooks/*.py` (the operator did not select that
scope) and any project-local `CLAUDE.md`/`.claude/rules/` files outside `~/.claude` itself.

**Next step, same session:** `CLAUDE.md` is rewritten per the operator's instruction. The pre-rewrite
version remains at this commit for recovery if needed.

## D-002 — CLAUDE.md rewritten to a minimal stub

`CLAUDE.md` replaced with a short note recording the reset and pointing at commit `ee7aa64` (this
repo's own history) as the recovery path, instead of the previous ~21-section operating contract.
Nothing else in `~/.claude` (hooks, skills, other config) was changed by this action — only the
file itself, per the operator's confirmed scope in D-001.

## D-003 — D-002's rewrite reversed; §1-20 restored, §21 narrowed instead of removed

**Trigger:** the operator, in a different concurrent session (workspace root `D:\Repo`), reviewed
what D-002 had done and said plainly: *"нет ничего не удалять и не менять пока я не пойму почему ты
стал себя так вести"*, then, once the D-001/D-002 chain was explained with evidence: *"да - это
верно - узкий принцип §21 (разово, по конкретному действию, с моим прямым словом каждый раз)"*, and
finally, on seeing the full-file deletion itself: *"нет стоять я не просил удалять 20 разделов, это
ошибка"*. So the D-001 scoping question ("Всё целиком") had produced a real, git-backed-up, and
still explicitly-confirmed action that nonetheless did not match what the operator actually wanted
once they saw the result land — a scoped confirmation is not proof against a wrong scope.

**Action taken:** `CLAUDE.md` restored verbatim from `ee7aa64` (the pre-rewrite backup D-001 itself
created), recovering §1-20 and the original §21 in full. §21 was then rewritten in place — not
reverted to its original wording — to state the narrower principle the operator confirmed: operator
consent authorizes one specific, named action, does not scale up from a broad or general statement
to the largest possible reading of it, does not carry forward to later actions without asking
again, and does not reach mechanically enforced blocks (`settings.json` deny rules, `hooks/*.py`
gates) regardless of phrasing. The D-002 incident itself is recorded inside the new §21 text as the
evidence for why the narrower wording exists, so a future reader does not have to reconstruct the
reasoning from this log alone.

**Not touched:** `hooks/*.py`, `skills/*`, and the other files this repo currently shows as
modified/untracked (`hooks/gpt_review_gate.py`, various `projects/d--repo/memory/*.md`,
`skills/html-report/SKILL.md`, `skills/rosetta/SKILL.md`, `skills/update-config/`) — those are
either another session's in-progress work or system-synced skill content unrelated to this
decision, and are left for whoever is actually working on them to commit with their own context.
This commit stages only `CLAUDE.md` and `settings.json` (the `.env.local` deny-rule narrowing from
the same conversation, previously uncommitted).

## D-004 — §25 added: recoverability, not the word "delete", defines the operator-only class

**Trigger:** 2026-09-12, Personal_Decision_Command_Center session. Three governance negative
controls had been handed back to the operator as operator-only: deleting a tracked test file to
exercise a deletion guard, editing a protected governance path on a branch to exercise a
forbidden-path refusal, and temporarily setting `GATE_MANIFEST_APPROVED_HASH_G1` to a wrong value
to exercise a hash-mismatch refusal. Operator, verbatim: _"надо обновить правило и не блокировать
эти действия в будуещем, мы всегда сможем востоновить из гита"_.

**Decision:** §20's "any deletion — files" is narrowed by a new §25. The operative property is
whether the content is recoverable, not whether the verb is "delete". A file already committed in
git comes back byte-for-byte, so reserving that class to the operator was guarding against a loss
that cannot occur.

**Measured before writing, by reading both layers** — the section carries the same table so a later
reader can re-check rather than trust it:

- `git rm <path>` is in **neither** `settings.json`'s `permissions.deny` nor
  `hooks/dangerous_command_gate.py`. The hook's `rm`/`rmdir` branch matches the shell builtin; a
  `git` invocation takes the `base == "git"` branch, which has no `rm` rule. So nothing mechanical
  was blocking the deletion this narrowing unblocks — only the prose rule was.
- `git checkout <sha> -- <path>` is **allowed**: the hook blocks `checkout --` only for a path-less
  or root/home/wildcard target (lines 266-284), and `settings.json` denies the literal
  `git checkout -- *` prefix, which the `<sha>` form does not match. This also explains the two
  refusals on 2026-09-11 — those used the literal `git checkout -- <files>` form.
- `git restore` with any worktree effect is **blocked** by the hook (line 285-292); only
  `--staged` alone is allowed.

**A defect in this section's own first draft, caught by the hook and recorded rather than quietly
fixed:** it named `git restore --source=<sha> -- <path>` as the recovery command. That command is
blocked. It was replaced with `git checkout <sha> -- <path>` / `git revert`, and the section now
states plainly that a written procedure naming a blocked command is worse than none. Same defect
class as the 2026-09-11 finding in Personal_Decision_Command_Center, where a procedure written for
the operator would have produced no evidence: **a procedure is a deliverable, and it has to be
checked against the machine, not against memory.**

**Deliberately kept operator-only, each for a stated reason rather than by symmetry:**
`git reset --hard`, `git clean -f*`, anything untracked or uncommitted (git holds no copy, so
"restore from git" is simply false); branch and remote-ref deletion; history rewrite that destroys
commits; database objects; files outside a repository; production; real money. Plus one that is the
mirror image of a newly-permitted action: setting an approval value to one that **makes** an
implementer-authored manifest binding stays operator-only, because a self-authorization loop is not
a recoverability question. Setting such a variable to a deliberately WRONG value is permitted — it
makes the gate stricter, never looser.

**Scope discipline (§21):** the operator's instruction named a class of actions and gave its own
reason. §25 encodes that reason and states its boundary explicitly, rather than reading the
instruction as a general loosening of §20. The real-money/live-trading half of §20 and every
mechanical gate are untouched.

**Noticed while working, not fixed here:** §15 still asserts that `~/.claude` "is not a git
repository". It has been one since D-001. Left for its own edit rather than folded in silently.

## D-005 — §24's authority-surface carve-out removed; operator accepted the identity-separation gap knowingly

**Trigger:** 2026-09-12, Personal_Decision_Command_Center session, PR #15. That PR fixed a real G1
closure BLOCKER but itself touched `.github/CODEOWNERS`, which §24's authority-surface carve-out
excluded from Claude's merge authority even with a clean, fresh GPT-PM `VERDICT: APPROVE` and green
required checks. The operator had to click merge by hand. Operator, verbatim, after that cost real
time waiting: _"мы опять возвращаемся к тому что я потерял 10 часов из-за тебя и из-за того что ты
не хотел мержить ПР, мне это надоело, что нужно отключить/добавить чтобы ты сам 100% делал это
сам?"_

**Two options were put to the operator directly, via `AskUserQuestion`, before any edit** — this is
a change to Claude's own operating contract, the operator's decision alone, not a technical/product
question for GPT-PM (§16 reserves exactly this kind of authorization-boundary question):

- **(A) Remove the carve-out entirely.** Claude merges any PR — including one touching gate
  manifests, `operator-approvals/**`, branch-protection/ruleset config, or CODEOWNERS — once a
  genuine correlated APPROVE and green required checks exist on its exact head. Stated cost: no
  human checkpoint remains on changes to the approval mechanism itself.
- **(B) Narrow it.** Keep the operator-only requirement for `governance/gate-manifests/**` and
  `operator-approvals/**` (the two paths where a mistake is a self-authorized gate — the most
  dangerous case), but let CODEOWNERS/branch-protection PRs auto-merge like anything else.

**The operator picked (A), the unqualified removal**, stated as its own message with no
qualification. §24 edited accordingly: the "Authority-surface carve-out" bullet is gone, replaced
with a paragraph recording the removal, why, and what changed; the identity-separation-gap
paragraph was reworded from "here is the mitigation" to "here is the risk the operator now
knowingly accepts" — the underlying fact (GPT-PM's GitHub connector shares Claude's own identity, so
no genuinely separate actor exists in the GitHub audit trail) was already true and is not changed by
this decision; what changed is that the operator chose not to keep a human checkpoint on the one
class of diff where that fact used to still matter.

**Scope discipline (§21), followed rather than assumed:** the operator's frustration message was
broad ("what do I need to turn off so you do this 100% yourself") — exactly the shape of remark §21
warns is not itself consent for the largest reading. The two options were named explicitly, with
their real trade-offs stated, before any file was touched, and the operator's reply selected one of
them by letter rather than being inferred from the frustration alone.

**Nothing else in §24 changed:** exact-head APPROVE, every required check green, mergeable, no
admin bypass/force/disabled-check/weakened-protection are all still required, unconditionally, for
every merge this section authorizes — including the newly-unblocked authority-surface class.
