---
id: astral.standards.database-header-inventory
title: Database header inventory
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["data"]
  paths: ["src/data/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

The data layer may use only tables listed in the header inventory of `src/data/database.py`. Adding or changing table usage requires a design decision and an update to that header.

## Rationale

The header is the contract for which tables exist in product scope; silent new tables fragment the data model.

## Examples

### Conforming

- Adding a column updates both the schema helpers and the header inventory in the same change.

### Violating

- A new query hits an undeclared side table without updating the header inventory.
