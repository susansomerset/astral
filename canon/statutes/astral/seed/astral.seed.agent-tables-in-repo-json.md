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
  - docs/features/foundation/ast-842-database-updates-are-not-running-on-production-deployments.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-08-26"
---

# Statement

`agent` and `agent_task` seed content must exist as checked-in JSON under `data/admin/agent.json` and `data/admin/agent_task.json`. Both files must contain Archie-approved non-empty row arrays. Operator-invoked apply (Revert to file and future explicit scripted apply) loads those files repo-wins to the DB. Automatic startup apply via `apply_repo_admin_json_at_startup` is disabled under the AST-1492 deploy content kill-switch until Archie approves a restored boot or seed/ops design. Empty `[]` is not a valid seed.

## Rationale

Empty `agent.json` once wiped every persona on boot. Repo JSON is the only durable, reviewable source for those two tables. During the kill-switch, repo JSON stays authoritative in git; only automatic boot projection is off so operator-managed DB rows survive deploy.

## Examples

### Conforming

- Six persona rows in `agent.json`; operator Revert to file loads them repo-wins.
- Non-empty `agent_task.json` applied repo-wins via Revert to file; export writes live rows back to files.
- `apply_repo_admin_json_at_startup` is a no-op (logs and returns) while the AST-1492 kill-switch is in force.

### Violating

- Ship `agent.json` as `[]`, or seed personas only via a one-off SQL insert with no repo file.
- Re-enable unconditional boot repo-wins apply without Archie-approved seed/ops design.

## Notes

UAT fixture twins may mirror these files; they are not a second source of truth. Fail-loud on empty or missing files applies on explicit load paths (Revert to file, scripted apply), not on the disabled boot apply path. Kill-switch product wiring: `docs/features/foundation/ast-842-database-updates-are-not-running-on-production-deployments.md` § Bug: AST-1497. Complements `astral.seed.operator-rows-stay-deleted` and `astral.seed.define-approved` (no new boot seed catalog without define approval).
