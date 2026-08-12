---
id: astral.standards.names-not-ticket-ids
title: Identifiers use domain language, not ticket ids
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "data", "external", "utils", "ui", "scripts"]
  paths: ["src/**", "scripts/**"]
  change_types: ["add", "modify"]
source_docs:
  - AST-1108 / seed discussion
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-31"
---

# Statement

Identifiers — functions, methods, variables, constants, classes, and modules — name what the thing *does* or *is* in stable domain language. Do not embed Linear issue ids (`AST-123`, `ast123`, `ast_123`, and the like) in those names. Prefer names that stay readable after the ticket closes; avoid names so ticket-specific they only make sense if you know the issue history.

## Rationale

Ticket ids rot the moment the ticket closes. Domain names survive refactors and do not teach the next reader that a number is the meaning.

## Examples

### Conforming

- `seed_vet_inflow_discovery_prompt`, `clear_select_job_page_run_next`.

### Violating

- `_apply_ast880_vet_inflow_discovery_prompt_migration`, `AST776_MARKER`.

## Notes

Carve-outs: comments, commit messages, feature docs under `docs/features/` (ticket in the path is required elsewhere), git branch names, and Linear prose. Not a rename mandate for every historical symbol on sight — new code and touched code follow this.
