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
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-31"
---

# Statement

Any seed or provision path that inserts rows other than the two repo-admin JSON tables must derive target entities by joining (or selecting from) the environment’s extant tables — for candidate-scoped `dispatch_task` catalogs, that means every row in `candidate`. Hardcoded candidate ids (e.g. `"somerset"`, `"johnson"`) must not define coverage.

## Rationale

Environments differ; naming people in config under-seeds and lies about who is covered.

## Examples

### Conforming

- Provision loops `SELECT candidate_id FROM candidate` (or equivalent), then ensures catalog rows per id.

### Violating

- Provision only `ASTRAL_CONFIG["template_candidate_id"] == "somerset"`, or only ids that already appear in `dispatch_task`.

## Notes

Product-global shells with null `candidate_id` (e.g. `gaze_email`) are not candidate-coverage rows; they still need Archie naming under define-approved and catalog-wins. `template_candidate_id` may remain for other product uses but must not define seed coverage.
