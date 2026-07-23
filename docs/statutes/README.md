# Statute corpus

Discrete, id’d, scoped, citable rules for the Astral pipeline — the statute harness. Adding a rule means adding a statute; validating a plan means running the relevant statutes against it.

- **Schema (fields + enums):** [SCHEMA.md](SCHEMA.md)
- **Authoring + lifecycle:** [AUTHORING.md](AUTHORING.md)
- **Harvest crosswalk + narrative leftovers:** [HARVEST.md](HARVEST.md)

## Namespaces

| Path prefix | Namespace id | Meaning |
|-------------|--------------|---------|
| `orchestration/` | `orch` | Generic pipeline / team-orchestration statutes |
| `astral/` | `astral` | Astral product-specific statutes |

Domains are folders under a namespace; one file per statute. See AUTHORING for layout rules.

## Universal set

Consumers that load “the universal set” include **every** file under `docs/statutes/**` whose frontmatter has:

- `tier: universal`
- `status: active`

Scope fields on universals do not exclude them from that set. Matching for `scoped` statutes is owned by AST-916.

## Exemplars

| id | tier | checkable | path |
|----|------|-----------|------|
| `orch.pipeline.plan-is-bible` | universal | judgment | `orchestration/pipeline/orch.pipeline.plan-is-bible.md` |
| `orch.roles.archie-approves-statutes` | universal | judgment | `orchestration/roles/orch.roles.archie-approves-statutes.md` |
| `astral.layers.import-direction` | scoped | judgment | `astral/layers/astral.layers.import-direction.md` |
| `astral.git.engineer-test-tree-ban` | scoped | hook | `astral/git/astral.git.engineer-test-tree-ban.md` |
| `astral.batch.batch-id-first` | scoped | ci | `astral/batch/astral.batch.batch-id-first.md` |

## Harvested corpus

Populated in AST-921 Stages 2–4 — see [HARVEST.md](HARVEST.md) for the full crosswalk while statutes land.
