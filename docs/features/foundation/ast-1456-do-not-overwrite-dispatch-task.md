# AST-1456 — Do not overwrite dispatch_task in any environment ever

Orphaned Bug mini-epic. Stub authorized by Chuckles at bug-fix so plan-fix has a doc to patch (no ancestor checkbox approved; plan-fix never creates a new plan doc).

## Purpose

Operator-curated `dispatch_task` rows must never be created, updated, or recreated by automatic product/boot/scheduler/seed paths. Needed seed SQL is delivered only as Linear comment text for Susan to run after restart.

## Related history (context only)

- AST-741 / AST-745 — stop retry / gaze_board auto-seed; startup inventory
- AST-1108 — SQL-first SEED_CONFIG scaffolding (not an executable auto path for this ban)

## Bug: AST-1496 — Ban automatic dispatch_task seed and provision writers

_(plan-fix fills this section)_
