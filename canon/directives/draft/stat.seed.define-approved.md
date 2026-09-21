---
id: astral.seed.define-approved
title: Seed needs are Archie-approved in define
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "data", "utils", "docs"]
  paths: ["src/**", "data/admin/**", "docs/features/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/features/foundation/ast-771-seed-audit.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-31"
---

# Statement

Before implementation invents or expands product seed, the parent define phase must name the seed need and Archie must approve it: which tables, row shape that matters, coverage rule (join), and CLICK or AUTO at seed. Seed needs must be articulable even when final code design is not final.

## Rationale

Hidden bootstrap is how deleted intent comes back and staging drifts. Define is where coverage and ownership get locked.

## Examples

### Conforming

- Parent Description Seed needs lists a meteorite six-row catalog, coverage = all `candidate` rows, `auto_mode` false; Archie approves before build.

### Violating

- Build adds a new startup ensure catalog with no define Seed needs section or Archie approval.

## Notes

Does not replace `orch.roles.archie-approves-statutes` for statute files; this gates product seed behavior.
