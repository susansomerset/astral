---
id: astral.docs.features-single-file-per-ticket
title: Features single file per ticket
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["docs"]
  paths: ["docs/features/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Feature documentation lives in `docs/features/<project>/<slug>.md` (plan + notes + review). Documentation is not stored in `.cursor/plans/`.

## Rationale

One path keeps Linear attachments and git history aligned.

## Examples

### Conforming

- Plan committed at `docs/features/team-chuckles/ast-921-….md`.

### Violating

- Plan only exists under `.cursor/plans/` and never lands in `docs/features/`.
