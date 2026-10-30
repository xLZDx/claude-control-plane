# Lessons log (append-only)

## 2026-10-31 - dangerous_command_gate: separators, leaders, wrapper options

- Kind: FAILURE (found by an external reporter, public issues #3 and #4 on xLZDx/claude-control-plane).
- Facts: `classify()` checked only the first token of a segment. A lone `&`, `(`, `{`, `then`/`do`, git global options (`git -C d reset --hard`) and sudo/timeout options that take a value (`sudo -u root rm -rf /`) all hid the destructive command. GPT-PM round 1 then found two more bypasses in the first fix: sudo long options with a separate value (`sudo --user root ...`) and the `--` option terminator.
- Root cause: command normalization modelled only flags, not options that consume an argument; original tests covered spellings, not wrapper grammar.
- Missed by: author and tests (no grammar-level cases); caught by an outside reporter, then by the GPT-PM reviewer on the first fix.
- Rule: when normalizing a wrapper command, enumerate its options that take values and its `--` terminator, and pin each with a blocked and an allowed test before asking for review.
