---
name: pm-bridge
description: Use PM Bridge for GPT-PM communication, gate/decision state, multi-conversation orchestration and escalation without manual copy-paste.
---

# PM Bridge — front door

PM Bridge is the shared D:\Repo orchestration transport and governance state layer.

Core workflow:
- session_start/session_end for multi-message browser work;
- send the exact review/decision payload to the registered project conversation;
- await/peek the reply without impatient resend;
- verify factual claims against current repository/evidence;
- record durable gate/decision state with PM Bridge tools where the project uses them.

Review requests must ask for one complete adversarial sweep of the declared gate/mechanism and its integrations, not one finding at a time. Remediation rounds re-check the current exact state.

Escalation:
- use the delegation matrix when available;
- routine autonomous decisions stay autonomous;
- GPT-PM handles product/governance review where the active project/global contract delegates it;
- operator escalation is reserved for the classes the active contract keeps operator-only or for stable unresolved decisions that genuinely require the operator.

Session discipline:
- one shared browser/orchestrator session at a time;
- do not re-send merely because an await was cancelled or slow; peek/recover current job state first;
- use stable project/conversation identity, not UI titles;
- end the session when the active block is complete.

Reporting mechanics come from the html-report skill.

Read references/full-2026-10-02.md for exact tool inventory, transport/session edge cases, and legacy escalation rationale.
