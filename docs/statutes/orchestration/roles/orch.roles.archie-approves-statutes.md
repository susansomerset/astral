---
id: orch.roles.archie-approves-statutes
title: Archie approves statute add/amend/retire
tier: universal
checkable: judgment
status: active
applies_when:
  layers: ["docs"]
  paths: ["docs/statutes/**"]
  change_types: ["add", "modify", "delete"]
source_docs: []
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-22"
---

# Statement

No statute under `docs/statutes/` may be added, amended, or retired without Archie approval recorded in frontmatter (`approved_by: Archie` and `approved_at` set). Drafts are not committed to this tree.

## Rationale

The corpus is shared law for agents and future mechanical checkers. Unapproved edits would silently change what Joan and rubrics enforce. Archie (architect alias; Linear assignee Susan) is the single approval gate.

## Examples

### Conforming

- An engineer drafts a statute on a branch, Archie approves, and the merged file carries `approved_by: Archie` with today’s `approved_at`.

### Violating

- A statute file is pushed to `docs/statutes/` with no Archie approval fields, or with `approved_by` set to an engineer name.
