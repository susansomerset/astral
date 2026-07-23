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

Consumers that load “the universal set” include **every** file under `canon/statutes/**` whose frontmatter has:

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

| id | tier | checkable | path |
|----|------|-----------|------|
| `astral.agent.confidence-bounds` | scoped | judgment | `astral/agent/astral.agent.confidence-bounds.md` |
| `astral.agent.do-task-delegation` | scoped | judgment | `astral/agent/astral.agent.do-task-delegation.md` |
| `astral.agent.grade-vector-validation` | scoped | judgment | `astral/agent/astral.agent.grade-vector-validation.md` |
| `astral.batch.batch-id-first` | scoped | ci | `astral/batch/astral.batch.batch-id-first.md` |
| `astral.batch.batch-id-format` | scoped | judgment | `astral/batch/astral.batch.batch-id-format.md` |
| `astral.batch.claim-process-release` | scoped | judgment | `astral/batch/astral.batch.claim-process-release.md` |
| `astral.batch.entity-agent-responses-latest-only` | scoped | judgment | `astral/batch/astral.batch.entity-agent-responses-latest-only.md` |
| `astral.config.config-source-of-truth` | scoped | judgment | `astral/config/astral.config.config-source-of-truth.md` |
| `astral.config.pass-threshold-vs-score-floor` | scoped | judgment | `astral/config/astral.config.pass-threshold-vs-score-floor.md` |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | ci | `astral/config/astral.config.secrets-and-env-specific-from-environ.md` |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | hook | `astral/debug/astral.debug.no-repo-root-artifacts-dir.md` |
| `astral.debug.spikes-under-debug-dir` | scoped | hook | `astral/debug/astral.debug.spikes-under-debug-dir.md` |
| `astral.docs.features-single-file-per-ticket` | scoped | judgment | `astral/docs/astral.docs.features-single-file-per-ticket.md` |
| `astral.git.betty-no-src-or-features` | scoped | hook | `astral/git/astral.git.betty-no-src-or-features.md` |
| `astral.git.engineer-test-tree-ban` | scoped | hook | `astral/git/astral.git.engineer-test-tree-ban.md` |
| `astral.layers.core-vs-external-bright-line` | scoped | judgment | `astral/layers/astral.layers.core-vs-external-bright-line.md` |
| `astral.layers.import-direction` | scoped | judgment | `astral/layers/astral.layers.import-direction.md` |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | judgment | `astral/layers/astral.layers.scripts-exempt-from-layer-rules.md` |
| `astral.layers.ui-config-driven-business-logic` | scoped | judgment | `astral/layers/astral.layers.ui-config-driven-business-logic.md` |
| `astral.patterns.coat-check-never-store-empty` | scoped | judgment | `astral/patterns/astral.patterns.coat-check-never-store-empty.md` |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | judgment | `astral/patterns/astral.patterns.render-verdict-orchestrates-consult.md` |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | judgment | `astral/patterns/astral.patterns.require-auth-on-protected-endpoints.md` |
| `astral.standards.data-raises-caller-logs` | scoped | judgment | `astral/standards/astral.standards.data-raises-caller-logs.md` |
| `astral.standards.database-header-inventory` | scoped | judgment | `astral/standards/astral.standards.database-header-inventory.md` |
| `astral.standards.debug-contract-gated` | scoped | judgment | `astral/standards/astral.standards.debug-contract-gated.md` |
| `astral.standards.dry-and-focused-functions` | scoped | judgment | `astral/standards/astral.standards.dry-and-focused-functions.md` |
| `astral.standards.in-scope-only` | scoped | judgment | `astral/standards/astral.standards.in-scope-only.md` |
| `astral.standards.logging-via-utils` | scoped | judgment | `astral/standards/astral.standards.logging-via-utils.md` |
| `astral.standards.no-cross-contamination` | scoped | judgment | `astral/standards/astral.standards.no-cross-contamination.md` |
| `astral.standards.no-hardcoded-sets` | scoped | ci | `astral/standards/astral.standards.no-hardcoded-sets.md` |
| `astral.standards.public-then-helpers` | scoped | judgment | `astral/standards/astral.standards.public-then-helpers.md` |
| `astral.standards.utils-data-late-import-only` | scoped | hook | `astral/standards/astral.standards.utils-data-late-import-only.md` |
| `astral.state.core-decides-transitions` | scoped | judgment | `astral/state/astral.state.core-decides-transitions.md` |
| `astral.state.job-prior-states-enforced` | scoped | judgment | `astral/state/astral.state.job-prior-states-enforced.md` |
| `astral.state.no-daisy-chain-in-run` | scoped | judgment | `astral/state/astral.state.no-daisy-chain-in-run.md` |
| `astral.ui.frontend-file-placement` | scoped | ci | `astral/ui/astral.ui.frontend-file-placement.md` |
| `astral.ui.naming-conventions` | scoped | ci | `astral/ui/astral.ui.naming-conventions.md` |
| `astral.ui.single-gunicorn-worker` | scoped | judgment | `astral/ui/astral.ui.single-gunicorn-worker.md` |
| `orch.git.betty-merge-tests-one-sha` | universal | judgment | `orchestration/git/orch.git.betty-merge-tests-one-sha.md` |
| `orch.git.commit-vocabulary` | universal | judgment | `orchestration/git/orch.git.commit-vocabulary.md` |
| `orch.git.flow-direction-inviolable` | universal | judgment | `orchestration/git/orch.git.flow-direction-inviolable.md` |
| `orch.git.ftr-sub-topology` | universal | judgment | `orchestration/git/orch.git.ftr-sub-topology.md` |
| `orch.git.merge-on-checkout` | universal | judgment | `orchestration/git/orch.git.merge-on-checkout.md` |
| `orch.git.no-cherry-pick-rebase-force` | universal | hook | `orchestration/git/orch.git.no-cherry-pick-rebase-force.md` |
| `orch.git.no-dev-agent-branches` | universal | hook | `orchestration/git/orch.git.no-dev-agent-branches.md` |
| `orch.git.one-epic-worktree-per-parent` | universal | judgment | `orchestration/git/orch.git.one-epic-worktree-per-parent.md` |
| `orch.git.three-permanent-branches` | universal | judgment | `orchestration/git/orch.git.three-permanent-branches.md` |
| `orch.pipeline.call-susan-for-product-decisions` | universal | judgment | `orchestration/pipeline/orch.pipeline.call-susan-for-product-decisions.md` |
| `orch.pipeline.plan-is-bible` | universal | judgment | `orchestration/pipeline/orch.pipeline.plan-is-bible.md` |
| `orch.pipeline.project-scoped-queues` | universal | judgment | `orchestration/pipeline/orch.pipeline.project-scoped-queues.md` |
| `orch.pipeline.status-gates-skill-entry` | universal | judgment | `orchestration/pipeline/orch.pipeline.status-gates-skill-entry.md` |
| `orch.roles.archie-approves-statutes` | universal | judgment | `orchestration/roles/orch.roles.archie-approves-statutes.md` |
| `orch.roles.betty-owns-test-tree` | universal | judgment | `orchestration/roles/orch.roles.betty-owns-test-tree.md` |
| `orch.roles.chuckles-never-ticket-assignee` | universal | judgment | `orchestration/roles/orch.roles.chuckles-never-ticket-assignee.md` |
| `orch.roles.engineer-assignee-through-resolve` | universal | judgment | `orchestration/roles/orch.roles.engineer-assignee-through-resolve.md` |
| `orch.roles.pre-commit-path-bans` | universal | hook | `orchestration/roles/orch.roles.pre-commit-path-bans.md` |

Full harvest crosswalk and narrative leftovers: [HARVEST.md](HARVEST.md). **56** active statutes in corpus.
