# Statute harvest register (AST-921)

Crosswalk of every enforceable mapping from the astral law docs into `canon/statutes/`, plus narrative leftovers that are **not** statutes. Schema and authoring rules live in [SCHEMA.md](SCHEMA.md) and [AUTHORING.md](AUTHORING.md) (AST-920).

## Crosswalk

| Status | id | tier | checkable | source | path |
|--------|----|------|-----------|--------|------|
| create (AST-921) | `astral.agent.confidence-bounds` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/agent/astral.agent.confidence-bounds.md` |
| create (AST-921) | `astral.agent.do-task-delegation` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/agent/astral.agent.do-task-delegation.md` |
| create (AST-921) | `astral.agent.grade-vector-validation` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/agent/astral.agent.grade-vector-validation.md` |
| already-landed (AST-920) | `astral.batch.batch-id-first` | scoped | ci | docs/ASTRAL_CODE_RULES.md | `astral/batch/astral.batch.batch-id-first.md` |
| create (AST-921) | `astral.batch.batch-id-format` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/batch/astral.batch.batch-id-format.md` |
| create (AST-921) | `astral.batch.claim-process-release` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/batch/astral.batch.claim-process-release.md` |
| create (AST-921) | `astral.batch.entity-agent-responses-latest-only` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/batch/astral.batch.entity-agent-responses-latest-only.md` |
| create (AST-921) | `astral.config.config-source-of-truth` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/config/astral.config.config-source-of-truth.md` |
| create (AST-921) | `astral.config.pass-threshold-vs-score-floor` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/config/astral.config.pass-threshold-vs-score-floor.md` |
| create (AST-921) | `astral.config.secrets-and-env-specific-from-environ` | scoped | ci | docs/ASTRAL_CODE_RULES.md | `astral/config/astral.config.secrets-and-env-specific-from-environ.md` |
| create (AST-921) | `astral.debug.no-repo-root-artifacts-dir` | scoped | hook | docs/ASTRAL_CODE_RULES.md | `astral/debug/astral.debug.no-repo-root-artifacts-dir.md` |
| create (AST-921) | `astral.debug.spikes-under-debug-dir` | scoped | hook | docs/ASTRAL_CODE_RULES.md | `astral/debug/astral.debug.spikes-under-debug-dir.md` |
| create (AST-921) | `astral.docs.features-single-file-per-ticket` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/docs/astral.docs.features-single-file-per-ticket.md` |
| create (AST-921) | `astral.git.betty-no-src-or-features` | scoped | hook | docs/ASTRAL_GIT_WORKFLOW.md | `astral/git/astral.git.betty-no-src-or-features.md` |
| already-landed (AST-920) | `astral.git.engineer-test-tree-ban` | scoped | hook | docs/ASTRAL_TEAM_WORKFLOW.md | `astral/git/astral.git.engineer-test-tree-ban.md` |
| create (AST-921) | `astral.layers.core-vs-external-bright-line` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/layers/astral.layers.core-vs-external-bright-line.md` |
| already-landed (AST-920) | `astral.layers.import-direction` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/layers/astral.layers.import-direction.md` |
| create (AST-921) | `astral.layers.scripts-exempt-from-layer-rules` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/layers/astral.layers.scripts-exempt-from-layer-rules.md` |
| create (AST-921) | `astral.layers.ui-config-driven-business-logic` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/layers/astral.layers.ui-config-driven-business-logic.md` |
| create (AST-921) | `astral.patterns.coat-check-never-store-empty` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/patterns/astral.patterns.coat-check-never-store-empty.md` |
| create (AST-921) | `astral.patterns.render-verdict-orchestrates-consult` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/patterns/astral.patterns.render-verdict-orchestrates-consult.md` |
| create (AST-921) | `astral.patterns.require-auth-on-protected-endpoints` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/patterns/astral.patterns.require-auth-on-protected-endpoints.md` |
| create (AST-921) | `astral.standards.data-raises-caller-logs` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/standards/astral.standards.data-raises-caller-logs.md` |
| create (AST-921) | `astral.standards.database-header-inventory` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/standards/astral.standards.database-header-inventory.md` |
| create (AST-921) | `astral.standards.debug-contract-gated` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/standards/astral.standards.debug-contract-gated.md` |
| create (AST-921) | `astral.standards.dry-and-focused-functions` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/standards/astral.standards.dry-and-focused-functions.md` |
| create (AST-921) | `astral.standards.in-scope-only` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/standards/astral.standards.in-scope-only.md` |
| create (AST-921) | `astral.standards.logging-via-utils` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/standards/astral.standards.logging-via-utils.md` |
| create (AST-921) | `astral.standards.no-cross-contamination` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/standards/astral.standards.no-cross-contamination.md` |
| create (AST-921) | `astral.standards.no-hardcoded-sets` | scoped | ci | docs/ASTRAL_CODE_RULES.md | `astral/standards/astral.standards.no-hardcoded-sets.md` |
| create (AST-921) | `astral.standards.public-then-helpers` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/standards/astral.standards.public-then-helpers.md` |
| create (AST-921) | `astral.standards.utils-data-late-import-only` | scoped | hook | docs/ASTRAL_CODE_RULES.md | `astral/standards/astral.standards.utils-data-late-import-only.md` |
| create (AST-921) | `astral.state.core-decides-transitions` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/state/astral.state.core-decides-transitions.md` |
| create (AST-921) | `astral.state.job-prior-states-enforced` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/state/astral.state.job-prior-states-enforced.md` |
| create (AST-921) | `astral.state.no-daisy-chain-in-run` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/state/astral.state.no-daisy-chain-in-run.md` |
| create (AST-921) | `astral.ui.frontend-file-placement` | scoped | ci | docs/ASTRAL_CODE_RULES.md | `astral/ui/astral.ui.frontend-file-placement.md` |
| create (AST-921) | `astral.ui.naming-conventions` | scoped | ci | docs/ASTRAL_CODE_RULES.md | `astral/ui/astral.ui.naming-conventions.md` |
| create (AST-921) | `astral.ui.single-gunicorn-worker` | scoped | judgment | docs/ASTRAL_CODE_RULES.md | `astral/ui/astral.ui.single-gunicorn-worker.md` |
| create (AST-921) | `orch.git.betty-merge-tests-one-sha` | universal | judgment | docs/ASTRAL_GIT_WORKFLOW.md | `orchestration/git/orch.git.betty-merge-tests-one-sha.md` |
| create (AST-921) | `orch.git.commit-vocabulary` | universal | judgment | docs/ASTRAL_GIT_WORKFLOW.md | `orchestration/git/orch.git.commit-vocabulary.md` |
| create (AST-921) | `orch.git.flow-direction-inviolable` | universal | judgment | docs/ASTRAL_GIT_WORKFLOW.md | `orchestration/git/orch.git.flow-direction-inviolable.md` |
| create (AST-921) | `orch.git.ftr-sub-topology` | universal | judgment | docs/ASTRAL_GIT_WORKFLOW.md | `orchestration/git/orch.git.ftr-sub-topology.md` |
| create (AST-921) | `orch.git.merge-on-checkout` | universal | judgment | docs/ASTRAL_GIT_WORKFLOW.md | `orchestration/git/orch.git.merge-on-checkout.md` |
| create (AST-921) | `orch.git.no-cherry-pick-rebase-force` | universal | hook | docs/ASTRAL_GIT_WORKFLOW.md | `orchestration/git/orch.git.no-cherry-pick-rebase-force.md` |
| create (AST-921) | `orch.git.no-dev-agent-branches` | universal | hook | docs/ASTRAL_GIT_WORKFLOW.md | `orchestration/git/orch.git.no-dev-agent-branches.md` |
| create (AST-921) | `orch.git.one-epic-worktree-per-parent` | universal | judgment | docs/ASTRAL_GIT_WORKFLOW.md | `orchestration/git/orch.git.one-epic-worktree-per-parent.md` |
| create (AST-921) | `orch.git.three-permanent-branches` | universal | judgment | docs/ASTRAL_GIT_WORKFLOW.md | `orchestration/git/orch.git.three-permanent-branches.md` |
| create (AST-921) | `orch.pipeline.call-susan-for-product-decisions` | universal | judgment | docs/ASTRAL_TEAM_WORKFLOW.md | `orchestration/pipeline/orch.pipeline.call-susan-for-product-decisions.md` |
| already-landed (AST-920) | `orch.pipeline.plan-is-bible` | universal | judgment | docs/ASTRAL_TEAM_WORKFLOW.md | `orchestration/pipeline/orch.pipeline.plan-is-bible.md` |
| create (AST-921) | `orch.pipeline.project-scoped-queues` | universal | judgment | docs/ASTRAL_TEAM_WORKFLOW.md | `orchestration/pipeline/orch.pipeline.project-scoped-queues.md` |
| create (AST-921) | `orch.pipeline.status-gates-skill-entry` | universal | judgment | docs/ASTRAL_TEAM_WORKFLOW.md | `orchestration/pipeline/orch.pipeline.status-gates-skill-entry.md` |
| already-landed (AST-920) | `orch.roles.archie-approves-statutes` | universal | judgment | (harness-native) | `orchestration/roles/orch.roles.archie-approves-statutes.md` |
| create (AST-921) | `orch.roles.betty-owns-test-tree` | universal | judgment | docs/ASTRAL_TEAM_WORKFLOW.md | `orchestration/roles/orch.roles.betty-owns-test-tree.md` |
| create (AST-921) | `orch.roles.chuckles-never-ticket-assignee` | universal | judgment | docs/ASTRAL_TEAM_WORKFLOW.md | `orchestration/roles/orch.roles.chuckles-never-ticket-assignee.md` |
| create (AST-921) | `orch.roles.engineer-assignee-through-resolve` | universal | judgment | docs/ASTRAL_TEAM_WORKFLOW.md | `orchestration/roles/orch.roles.engineer-assignee-through-resolve.md` |
| create (AST-921) | `orch.roles.pre-commit-path-bans` | universal | hook | docs/ASTRAL_GIT_WORKFLOW.md | `orchestration/roles/orch.roles.pre-commit-path-bans.md` |

**Counts:** 51 created by AST-921; 5 already-landed (AST-920); 56 total active mappings in this register.

## Narrative leftovers

| Key | Source | Why narrative |
|-----|--------|---------------|
| `code-rules-1.2-imports-pointer` | CODE_RULES §1.2 | Pointer into §3.3; covered by `astral.layers.import-direction` |
| `code-rules-2.1-config-block-catalog` | CODE_RULES §2.1 block bullets | Catalog of current keys — descriptive inventory, not a separate enforceable rule per block |
| `code-rules-2.4-dispatcher-pseudocode` | CODE_RULES §2.4 code sample | Illustrative; claim/process/release + batch-id statutes cover the rule |
| `code-rules-2.6.0-run-next-carveout-detail` | CODE_RULES §2.6.0 | Detailed carve-out prose under `astral.state.no-daisy-chain-in-run` Notes — keep law prose, no extra statute |
| `code-rules-2.6.1-3-entity-examples` | CODE_RULES §2.6.1–2.6.3 | Examples of company/job/candidate flows — illustrative |
| `code-rules-2.7-encoded-consult-detail` | CODE_RULES §2.7 encoded paragraph | Feature-specific detail; pointer to consult feature docs |
| `code-rules-2.8-coat-check-key-table` | CODE_RULES §2.8 table | Current key registry — data, not a rule (rule is never-store-empty) |
| `code-rules-3.1-directory-tree` | CODE_RULES §3.1 | Descriptive tree snapshot |
| `code-rules-3.2-dispatch-pipeline-table` | CODE_RULES §3.2 PW/AI/DB table | Descriptive task matrix |
| `code-rules-3.4-html-cull-config` | CODE_RULES §3.4 | Config location notes; no separate statute beyond config-source-of-truth |
| `code-rules-3.5-dev-workflow-ports` | CODE_RULES §3.5 | Dev port/process how-to |
| `code-rules-3.5-scheduler-endpoint-list` | CODE_RULES §3.5 | Endpoint inventory |
| `code-rules-3.7-boards-sunset` | CODE_RULES §3.7 | Historical sunset archive |
| `code-rules-4.1-stale-branching` | CODE_RULES §4.1 | Stale — superseded by ASTRAL_GIT_WORKFLOW.md; do not harvest as active statutes |
| `code-rules-4.3-state-name-list` | CODE_RULES §4.3 | Name list duplicated from TEAM happy-path table — keep as narrative index |
| `git-reference-graph` | GIT_WORKFLOW Reference graph | Pointer-only |
| `git-skills-map` | GIT_WORKFLOW Skills map | Index into skills |
| `git-chuckles-hygiene-tmp-branches` | GIT_WORKFLOW Chuckles git hygiene | Operator script detail; covered by no-dev-agent / flow statutes at rule level |
| `git-child-strict-sequential-prose` | GIT_WORKFLOW Child sub-issue sequencing | Narrative leftover — do not create orch.git.children-strictly-sequential; cite under Notes of orch.git.ftr-sub-topology if needed |
| `team-orientation-pointer` | TEAM Orientation | Points at orientation skill |
| `team-git-and-branches-pointers` | TEAM Git and branches | Points at orientation / CODE_RULES §3.6 — no new rule |
| `team-happy-path-table` | TEAM Linear status → skill | Table is the index behind orch.pipeline.status-gates-skill-entry — table itself stays narrative |
| `team-roles-table-detail` | TEAM Roles table | Role roster detail behind role statutes |

