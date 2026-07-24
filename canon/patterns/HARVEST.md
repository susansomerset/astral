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

## Crosswalk

| Status | id | domain | path | source | notes |
|--------|----|--------|------|--------|-------|
| already-landed (AST-925) | `pattern.batch.entity-claim-process-release` | batch | `batch/pattern.batch.entity-claim-process-release.md` | CODE_RULES §2.4 | AC: new batch task |
| pending (AST-969) | `pattern.state.entity-state-transitions` | state | `state/pattern.state.entity-state-transitions.md` | CODE_RULES §2.6 | AC: new entity state transition; propose→approve exercise |
| pending (AST-969) | `pattern.batch.entity-agent-responses` | batch | `batch/pattern.batch.entity-agent-responses.md` | CODE_RULES §2.4.1 | supporting |
| pending (AST-969) | `pattern.config.config-block` | config | `config/pattern.config.config-block.md` | CODE_RULES §2.1 | AC: new config block |
| pending (AST-969) | `pattern.layers.import-discipline` | layers | `layers/pattern.layers.import-discipline.md` | CODE_RULES §2.5 / §3.3 | supporting |
| pending (AST-969) | `pattern.ui.admin-endpoint` | ui | `ui/pattern.ui.admin-endpoint.md` | CODE_RULES §2.9 / §3.2 | AC: new admin endpoint |

Propose→approve lifecycle prose lives in [AUTHORING.md](AUTHORING.md). This ticket exercises it once on `pattern.state.entity-state-transitions`.
