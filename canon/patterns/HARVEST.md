# Pattern harvest register (AST-969)

Crosswalk of every astral recurring-shape pattern under `canon/patterns/`, plus the define-parent AC cite map. Schema and authoring rules live in [SCHEMA.md](SCHEMA.md) and [AUTHORING.md](AUTHORING.md) (AST-925).

## AC → pattern cite map

| define-parent change shape | Pattern id(s) to cite |
|----------------------------|------------------------|
| new batch task | `pattern.batch.entity-claim-process-release` |
| new entity state transition | `pattern.state.entity-state-transitions` |
| new admin endpoint | `pattern.ui.admin-endpoint` |
| new config block | `pattern.config.config-block` |

Supporting harvest packages (also citable):

| Supporting package | Pattern id |
|--------------------|------------|
| entity agent_responses | `pattern.batch.entity-agent-responses` |
| layer / import discipline | `pattern.layers.import-discipline` |
| dispatch score_floor (sole numeric floor) | `pattern.dispatch.score-floor` |
| labeled button roles | `pattern.ui.shared-button-roles` |
| icon-only compact control | `pattern.ui.icon-control` |

## Crosswalk

| Status | id | domain | path | source | notes |
|--------|----|--------|------|--------|-------|
| already-landed (AST-925) | `pattern.batch.entity-claim-process-release` | batch | `batch/pattern.batch.entity-claim-process-release.md` | CODE_RULES §2.4 | AC: new batch task |
| create (AST-969) | `pattern.state.entity-state-transitions` | state | `state/pattern.state.entity-state-transitions.md` | CODE_RULES §2.6 | AC: new entity state transition; propose→approve exercised |
| create (AST-969) | `pattern.batch.entity-agent-responses` | batch | `batch/pattern.batch.entity-agent-responses.md` | CODE_RULES §2.4.1 | supporting |
| create (AST-969) | `pattern.config.config-block` | config | `config/pattern.config.config-block.md` | CODE_RULES §2.1 | AC: new config block |
| create (AST-969) | `pattern.layers.import-discipline` | layers | `layers/pattern.layers.import-discipline.md` | CODE_RULES §2.5 / §3.3 | supporting |
| create (AST-969) | `pattern.ui.admin-endpoint` | ui | `ui/pattern.ui.admin-endpoint.md` | CODE_RULES §2.9 / §3.2 | AC: new admin endpoint |
| create (AST-1110) | `pattern.dispatch.run-next-chain-authority` | dispatch | `dispatch/pattern.dispatch.run-next-chain-authority.md` | AST-1109 | proposed — run_next chain authority; not yet Archie-approved |
| create (AST-1279) | `pattern.dispatch.score-floor` | dispatch | `dispatch/pattern.dispatch.score-floor.md` | AST-1275 / CODE_RULES §2.1 | approved — sole numeric floor; retires pass-threshold statute teaching |
| create (AST-1300) | `pattern.ui.shared-button-roles` | ui | `ui/pattern.ui.shared-button-roles.md` | AST-1166 catalog | approved — labeled `btn` roles + `in-row` size (AST-1317); CSS in `App.css` |
| create (AST-1300) | `pattern.ui.icon-control` | ui | `ui/pattern.ui.icon-control.md` | AST-1166 catalog | approved — icon-only compact actions; CSS in `App.css` |

Propose→approve lifecycle prose lives in [AUTHORING.md](AUTHORING.md). This ticket exercised it once on `pattern.state.entity-state-transitions` (Stage 2 proposed → Stage 3 approved).
