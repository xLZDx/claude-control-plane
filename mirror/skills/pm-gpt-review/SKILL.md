---
name: pm-gpt-review
description: Run the PM-GPT review and approve step through PM Bridge. Use at SDLC phase 8 (code gate before push/PR) and optionally at phase 5 (documentation review). Produces an approval bound to the exact git HEAD.
---

# pm-gpt-review

## Apply when
Sprint code is complete, the test agents' evidence is green and reviewer consensus is recorded (phase 7 done), or a document set needs an independent GPT-PM read (phase 5).

## Method
1. Commit everything for the sprint; the tree must be clean. The approval binds to this exact HEAD.
2. Make sure `docs/sdlc/verify-evidence.md` lists exact heads, commands, results, `NOT_RUN` items and the reviewer consensus. This file is the evidence packet sent to the PM.
3. Run `python <framework>/tools/af_cli.py pm-review --kind code --base <sprint base ref>` (use `--kind docs` for phase 5). It builds the packet, calls PM Bridge `review.js --final`, and waits for the correlated verdict. Do not poll or resend; the call is one durable job.
4. APPROVE: the tool writes `gate-approval.md` and `.pm-review/approval.json` with the approval id and head. Run `af_cli.py next`, then push and open ONE PR per sprint.
5. Findings (not APPROVE): fix the complete valid BLOCKER/MAJOR set in one batch, commit, and request one verification round. A GPT objection is a finding to verify against primary evidence, not an automatic prohibition.
6. Any new commit invalidates the approval; re-run step 3 only if code changed.

## Rules
- Claude and GPT sessions use the same command; the approval is tool-agnostic.
- Never hand-write or edit the approval files. Never claim approval without the tool's `APPROVED` output.
- Documentation-only blockers do not hold the code gate.

## Required output
Verdict, approval id, head, request/reply ids, findings by severity, what is still unverified.

## Do not
Send a shortened packet; run reviews under a model outside the allowlist; push before `af_cli.py verify` prints `OK`.
