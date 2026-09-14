---
id: astral.seed.other-via-coverage-join
title: Non-JSON seed coverage joins extant tables
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "data", "utils"]
  paths: ["src/core/dispatcher.py", "src/utils/config.py", "src/data/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/features/foundation/ast-771-seed-audit.md
  - docs/features/foundation/ast-1456-do-not-overwrite-dispatch-task.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-31"
---

# Statement

This statute does **not** authorize `dispatch_task` boot or scheduler-start provision (banned under AST-1456 / AST-1496; see `astral.seed.archie-catalog-wins` carve-out).

**If** Archie later approves a seed path that inserts rows other than the two repo-admin JSON tables (and that path is not the banned `dispatch_task` auto-writer), that path must derive target entities by joining (or selecting from) the environment’s extant tables — for candidate-scoped coverage, that means every row in `candidate`. Hardcoded candidate ids (e.g. `"somerset"`, `"johnson"`) must not define coverage. Coverage-join is **not** a standing requirement to run meteorite/`dispatch_task` provision loops.

## Rationale

Environments differ; naming people in config under-seeds and lies about who is covered. The `dispatch_task` ban removes the old provision loops; this rule survives for any future Archie-approved non-banned seed path.

## Examples

### Conforming

- A future Archie-approved non-`dispatch_task` seed path loops `SELECT … FROM` an extant table for coverage, rather than hardcoding entity ids.
- Product ships with no automatic `dispatch_task` provision; new schedule rows arrive via operator UI or Susan-run Linear SQL.

### Violating

- A seed path (were one approved) covers only `ASTRAL_CONFIG["template_candidate_id"] == "somerset"`, or only ids that already appear in the target table.
- Reintroducing `dispatch_task` boot provision “because coverage-join requires looping candidates.”

## Notes

Candidate-bound mailbox dispatch shapes in config may remain as documentation / Linear paste; they are not a license to auto-insert. Any product-global shells with null `candidate_id` still need Archie naming under define-approved policy, but must not be boot-ensured as `dispatch_task` under the carve-out. `template_candidate_id` may remain for other product uses but must not define seed coverage.
