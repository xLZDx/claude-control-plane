---
name: a11y-contract
description: Review accessibility as task completion, not checklist theater. Use on touched UI, forms, navigation and dynamic content.
---

# a11y-contract

## Apply when
Touched UI: forms, navigation, dialogs, dynamic content, media.

## Method
1. Keyboard reachability, focus order and visible focus; no traps.
2. Semantics, roles, accessible names and labels.
3. Contrast and reflow at 200-400% zoom; touch target size; reduced motion.
4. Screen-reader announcement for dynamic updates and errors; locale, RTL and long strings.
5. Error identification and recovery.

## Required output
Barrier list: who is blocked, which task, criterion (WCAG), fix, how to verify (keyboard walk, screen reader, axe).

## Do not
Treat a passing automated scan as proof of task completion; list barriers without user impact.

Typical failure modes: `references/failure-modes.md` (read only when the work hits one of them).
