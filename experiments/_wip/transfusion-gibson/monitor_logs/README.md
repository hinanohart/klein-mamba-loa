# monitor_logs/

Append-only outputs from audit / monitor subagents.

Each run writes one file named `<agent>-<UTC-iso>.md`. Do NOT delete files —
delete-and-rewrite would defeat the audit trail (cf. blueprint section 7's
R8 + reproducibility requirement).

The 2026-05-17 R14 audit found that a previous session's monitor agents
reported "OK" against an empty filesystem because they took a snapshot
before parallel Writes completed. The fix going forward is to (a) only
launch monitor agents AFTER all Writes return, and (b) persist their raw
output here so post-hoc verification is possible.
