---
id: astral.seed.agent-tables-in-repo-json
title: Agent and agent_task seed live in repo JSON
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "data", "utils"]
  paths: ["data/admin/**", "src/core/repo_admin_json.py", "src/utils/config.py", "src/core/bootstrap.py"]
  change_types: ["add", "modify"]
source_docs:
  - docs/features/foundation/ast-771-seed-audit.md
  - docs/features/foundation/ast-787-uat-agent-json-empty-seed-six-agent-personas.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-31"
---

# Statement

`agent` and `agent_task` seed content must exist as checked-in JSON under `data/admin/agent.json` and `data/admin/agent_task.json`. Both files must contain Archie-approved non-empty row arrays. Startup (and Revert to file) apply those files repo-wins to the DB. Empty `[]` is not a valid seed.

## Rationale

Empty `agent.json` once wiped every persona on boot. Repo JSON is the only durable, reviewable source for those two tables.

## Examples

### Conforming

- Six persona rows in `agent.json`; startup upsert loads them.
- Non-empty `agent_task.json` applied repo-wins at boot and via Revert to file.

### Violating

- Ship `agent.json` as `[]`, or seed personas only via a one-off SQL insert with no repo file.

## Notes

UAT fixture twins may mirror these files; they are not a second source of truth. Fail-loud on empty or missing files at boot is the intended implementer behavior.
