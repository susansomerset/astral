<!-- linear-archive: AST-978 archived 2026-08-05 -->

## Linear archive (AST-978)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-978/backfill-ref-agent-data-id-on-existing-duplicates-add-a-self-reference  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-974 — Add a self-reference key to agent_data  
**Blocked by / blocks / related:** parent: AST-974

### Description

## What this implements

One-time operator-safe dry-run + live pass that sets `ref_agent_data_id` to the earliest twin for existing duplicate `block_data` rows. Does **not** clear or delete any `block_data`. Does **not** change runtime write/read.

## Acceptance criteria

7. Backfill dry-run + live sets refs on existing duplicates to earliest twins and leaves all `block_data` values unchanged.
8. With `debug=True` on touched backend backfill paths, a scannable per-index trail shows match-vs-new and the ids recorded/resolved; with `debug=False`, no new debug-contract noise.

## Boundaries

Does not implement schema or runtime write/read (sibling). Does not reclaim disk space / vacuum. Does not delete historical content.

## Notes for planning

Depends on sibling shipping `ref_agent_data_id` + resolve semantics. Backfill refs only.

## Git branch (authoritative)

Per orientation § Branch law. Created at dispatch-parent. Publish to origin/<sub-ref> only.

### Comments

#### radia — 2026-07-25T19:06:14.751Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-978
**Publish ref:** `origin/sub/AST-974/AST-978-backfill-ref-agent-data-id-duplicates` @ `a6fcf5924b920f425b9638b30911067cddad39b1`
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|---|---|---|---|
| `astral.agent.confidence-bounds` | scoped | conforms | no grade/confidence changes (AST-977 debug only on tip) |
| `astral.agent.do-task-delegation` | scoped | conforms | no Anthropic assembly drift |
| `astral.agent.grade-vector-validation` | scoped | conforms | untouched |
| `astral.batch.batch-id-first` | scoped | conforms | no batch claim APIs |
| `astral.batch.batch-id-format` | scoped | conforms | untouched |
| `astral.batch.claim-process-release` | scoped | conforms | untouched |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | untouched |
| `astral.config.config-source-of-truth` | scoped | conforms | no new config |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | untouched |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | no secrets/env |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths miss artifacts/** / scripts/spikes/** |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | feature plans not spike notes |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | one plan file per ticket (977+978) |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test commit tests/bible only |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | AST-978 engineer commits exclude tests/ |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | no external I/O |
| `astral.layers.import-direction` | scoped | conforms | script→data+utils; data no logging |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | conforms | migration CLI under scripts/ |
| `astral.layers.ui-config-driven-business-logic` | scoped | not-applicable | layers miss (no ui/utils) |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | untouched |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | untouched |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers miss (no ui) |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | no logging in database.py; CLI logs |
| `astral.standards.database-header-inventory` | scoped | conforms | agent_data inventory from AST-977 retained |
| `astral.standards.debug-contract-gated` | scoped | conforms | CLI --debug debug_index N/M; quiet off; AST-977 hydrate index fixed on tip |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | reuses _find_earliest without exclude |
| `astral.standards.in-scope-only` | scoped | conforms | refs-only UPDATE; no vacuum/runtime rewrite in AST-978 commits |
| `astral.standards.logging-via-utils` | scoped | conforms | get_logger in CLI; agent uses utils logging |
| `astral.standards.no-cross-contamination` | scoped | conforms | layered paths only |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | no new enums |
| `astral.standards.public-then-helpers` | scoped | conforms | public backfill_agent_data_refs beside agent_data CRUD |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | layers miss (no utils) |
| `astral.state.core-decides-transitions` | scoped | conforms | untouched |
| `astral.state.job-prior-states-enforced` | scoped | conforms | untouched |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | untouched |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers miss (no ui) |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers miss (no ui) |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | migration script only; no worker change |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | single merge-tests SHA 5cfbd73 from origin/tests bc8378a |
| `orch.git.commit-vocabulary` | universal | conforms | docs/code/test/merge-tests vocabulary only |
| `orch.git.flow-direction-inviolable` | universal | conforms | child sub under AST-974 |
| `orch.git.ftr-sub-topology` | universal | conforms | origin/sub/AST-974/AST-978-… |
| `orch.git.merge-on-checkout` | universal | conforms | merge origin/dev into worktree; no rebase of dev |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | no rewrite ops |
| `orch.git.no-dev-agent-branches` | universal | conforms | epic sub publish-ref |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | astral-AST-974 epic worktree |
| `orch.git.three-permanent-branches` | universal | conforms | no new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | parent AC7–8; Joan round-1 exclude fix |
| `orch.pipeline.plan-is-bible` | universal | conforms | stages 1–2 + Revision 1 match tip |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Foundation child |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | no canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | test()+bible via Betty merge-tests |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | implementer Hedy; Chuckles not assignee |
| `orch.roles.engineer-assignee-through-resolve` | universal | needs-discussion | Linear assignee is Radia; Joan named Hedy |
| `orch.roles.pre-commit-path-bans` | universal | conforms | engineer commits data+scripts only; Betty owns tests |

## Pattern conformance

none cited

## Plan adherence

Stages 1–2 match tip: `backfill_agent_data_refs` without `exclude_agent_data_id` (Revision 1 / Joan round-1); refs-only UPDATE; dry-run default + `--execute`; `--debug` per-index trail; no runtime write/read rewrite (AST-977 sibling). Self-Assessment Single-Component matches AST-978 commits. Three-dot tip also carries AST-977 (+ resolve) — scored in-scope, not re-opened as product findings.

## Findings

**discuss** — `orch.roles.engineer-assignee-through-resolve`: assignee is Radia; Joan named Hedy. review-child does not reassign — restore Hedy through resolve.

**discuss (straggler)** — Joan Excluded but in-scope on three-dot tip (all conforms): `astral.agent.confidence-bounds`, `astral.agent.do-task-delegation`, `astral.agent.grade-vector-validation`, `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.core-vs-external-bright-line`, `astral.patterns.coat-check-never-store-empty`, `astral.patterns.render-verdict-orchestrates-consult`, `astral.standards.debug-contract-gated`, `astral.standards.logging-via-utils`, `astral.state.no-daisy-chain-in-run`.

**advisory** — decompress path uses bare `except Exception` then records `errors` + continues (plan-literal); return counts make the failure visible.

### What’s solid
No-exclude earliest match; canonical never gains ref; refs-only UPDATE; `block_data` untouched; operator-safe dry-run; CLI `debug_index` N/M gated on `--debug`; data layer silent; Joan round-1 concern closed in code.

**Notes:** Joan plan-rubric APPROVED attached. Docs append on plan file @ this tip. No fix-now on AST-978 product.

context_tokens≈42000

#### betty — 2026-07-25T19:01:23.408Z
## QA test manifest

`origin/sub/AST-974/AST-978-backfill-ref-agent-data-id-duplicates` @ `5cfbd73` (`merge-tests(AST-978): origin/tests bc8378a`)

### Gaps (new)
1. Dry-run: `would_set_ref` on later twin; no DB write; canonical `canonical_or_unique`
2. Live: `set_ref` to earliest; `block_data` unchanged; unique stays canonical; second live pass idempotent (`already_ref`)
3. Skip `already_ref`; decompress failure → `error` (pass continues)
4. CLI default dry-run banner + summary JSON; `--execute` → `dry_run=False`
5. `--debug` §1.5.1 index trail; quiet without `--debug`; `errors` → exit 1

### Existing coverage
- AST-977 runtime write/read/resolve suites remain on publish tip (sibling; not re-run required for this ticket)

### Run
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agent_data.py::TestAst978BackfillAgentDataRefs \
  tests/component/scripts/test_backfill_agent_data_refs.py \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

### Bible shasums (publish-ref)
- `docs/test-bible/data/database/agent_data.md` `sha256:c6f56e2ba71dd049ef47fccd0bcaa8064211022f65c101bc4db89a264ae47435`
- `docs/test-bible/dev/backfill_agent_data_refs.md` `sha256:856eb1abb3301fa8061fd24cd856439a5ded98d00c968d7b8476103a75f85b95`

Out of scope: runtime write/read (AST-977); vacuum / clear `block_data`.

#### joan — 2026-07-25T18:56:33.306Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-978
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-974/AST-978-backfill-ref-agent-data-id-duplicates`
**Engineer:** Hedy
**Plan Discuss:** round=1 completed (concern + reply); fix-now on `exclude_agent_data_id` resolved in plan @ `bc62871`

## Traceability

### Parent AC → plan stages

| Parent AST-974 AC | Plan coverage |
|---|---|
| 1–6 Schema / runtime write/read / match / resolve | N/A — boundary; sibling AST-977 |
| 7 Backfill dry-run + live; leave all `block_data` unchanged | Stages 1–2 |
| 8 Debug on touched backfill paths | Stage 2 CLI `--debug` |
| 9 Store-then-retrieve still succeeds | N/A — runtime sibling; preserved by refs-only UPDATE + correct earliest targeting |

### Plan stages → definition

| Stage | Maps to |
|---|---|
| 1 `backfill_agent_data_refs` | Functional scope §5; AC7; Boundaries (no clear/delete); AC4 canonical null via no-exclude match |
| 2 Operator CLI + debug | Functional scope §5–6; AC7–8 |

## Statute verdicts

| id | verdict | one-line |
|---|---|---|
| orch.git.betty-merge-tests-one-sha | conforms | Tests stay Betty |
| orch.git.commit-vocabulary | conforms | No banned commit types |
| orch.git.flow-direction-inviolable | conforms | Child `sub/…` publish-ref |
| orch.git.ftr-sub-topology | conforms | `sub/AST-974/AST-978-…` |
| orch.git.merge-on-checkout | conforms | No contrary guidance |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrites |
| orch.git.no-dev-agent-branches | conforms | Epic sub only |
| orch.git.one-epic-worktree-per-parent | conforms | `astral-AST-974/` |
| orch.git.three-permanent-branches | conforms | No new permanents |
| orch.pipeline.call-susan-for-product-decisions | conforms | Contract fixed by parent AC |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Revision 1 |
| orch.pipeline.project-scoped-queues | conforms | Single child |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Discuss re-validate |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | tests out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Hedy |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign Hedy |
| orch.roles.pre-commit-path-bans | conforms | data + scripts/migrations |
| astral.batch.batch-id-first | conforms | No batch claim APIs |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Untouched |
| astral.batch.entity-agent-responses-latest-only | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | No new config |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src change |
| astral.layers.import-direction | conforms | Script → data + utils; data stays data |
| astral.layers.scripts-exempt-from-layer-rules | conforms | Migration CLI under scripts |
| astral.standards.data-raises-caller-logs | conforms | No logging in database.py |
| astral.standards.database-header-inventory | conforms | Existing `agent_data` only |
| astral.standards.dry-and-focused-functions | conforms | Reuses match helper without exclude on backfill |
| astral.standards.in-scope-only | conforms | Refs-only; no vacuum/runtime rewrite |
| astral.standards.no-cross-contamination | conforms | Layered paths only |
| astral.standards.no-hardcoded-sets | conforms | No new enums |
| astral.standards.public-then-helpers | conforms | Public backfill API |
| astral.state.core-decides-transitions | conforms | Untouched |
| astral.state.job-prior-states-enforced | conforms | Untouched |
| astral.ui.single-gunicorn-worker | conforms | Migration script only |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.scripts-exempt-from-layer-rules, astral.standards.data-raises-caller-logs, astral.standards.database-header-inventory, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.agent.confidence-bounds — layers/paths miss
- astral.agent.do-task-delegation — layers/paths miss
- astral.agent.grade-vector-validation — layers/paths miss
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — layers/paths miss
- astral.git.engineer-test-tree-ban — paths miss
- astral.layers.core-vs-external-bright-line — layers/paths miss
- astral.layers.ui-config-driven-business-logic — layers/paths miss
- astral.patterns.coat-check-never-store-empty — layers/paths miss
- astral.patterns.render-verdict-orchestrates-consult — layers/paths miss
- astral.patterns.require-auth-on-protected-endpoints — layers/paths miss
- astral.standards.debug-contract-gated — layers miss scripts; Stage 2 checked under R6
- astral.standards.logging-via-utils — layers miss scripts
- astral.standards.utils-data-late-import-only — layers/paths miss
- astral.state.no-daisy-chain-in-run — layers/paths miss
- astral.ui.frontend-file-placement — layers/paths miss
- astral.ui.naming-conventions — layers/paths miss

## Findings

None fix-now.

**Round-1 fix verified:** Stage 1 calls `_find_earliest_agent_data_content_match(conn, plain)` without exclude; self-match → `canonical_or_unique`; Done-when / UAT require no canonical row gains a ref. Prior invert/cycle concern closed.

**acceptable** — Dry-run reuses `updated` count for `would_set_ref`; actions list disambiguates.

Definition fidelity, layer/config/placement/pattern/DRY checks: pass. Self-assessment (Single-Component / high / Medium) remains honest.

— Joan
context_tokens≈52000

#### hedy — 2026-07-24T01:37:09.663Z
[plan-discuss] round=1 reply

Addressed Joan fix-now on Stage 1 match call.

**Delta** (`origin/sub/AST-974/AST-978-backfill-ref-agent-data-id-duplicates` @ `bc62871`):
- Stage 1 now calls `_find_earliest_agent_data_content_match(conn, plain)` **without** `exclude_agent_data_id`.
- `match_id is None` **or** `match_id == agent_data_id` → `canonical_or_unique` (no UPDATE); else set/would-set ref to that earlier twin.
- Removed the exclude-era “unreachable self-ref → error” branch.
- Done-when / UAT Correct outcome: updated refs always point at an earlier twin; no earliest/canonical row gains a ref.
- Revision 1 section added in the plan doc.

Plan: https://github.com/susansomerset/astral/blob/sub/AST-974/AST-978-backfill-ref-agent-data-id-duplicates/docs/features/foundation/ast-978-backfill-ref-agent-data-id-duplicates.md

#### joan — 2026-07-24T01:35:03.284Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-978
**Overall:** REVISE
**Publish ref:** `origin/sub/AST-974/AST-978-backfill-ref-agent-data-id-duplicates`
**Engineer:** Hedy

## Traceability

### Parent AC → plan stages

| Parent AST-974 AC | Plan coverage |
|---|---|
| 1–6 Schema / runtime write/read / match / resolve | N/A — boundary; sibling AST-977 |
| 7 Backfill dry-run + live; leave all `block_data` unchanged | Stages 1–2 (intent) — **blocked by fix-now below** |
| 8 Debug on touched backfill paths | Stage 2 CLI `--debug` |
| 9 Store-then-retrieve still succeeds | N/A — runtime sibling; preserved if refs-only UPDATE is correct |

### Plan stages → definition

| Stage | Maps to |
|---|---|
| 1 `backfill_agent_data_refs` | Functional scope §5; AC7; Boundaries (no clear/delete) |
| 2 Operator CLI + debug | Functional scope §5–6; AC7–8 |

## Statute verdicts

| id | verdict | one-line |
|---|---|---|
| orch.git.betty-merge-tests-one-sha | conforms | Tests stay Betty |
| orch.git.commit-vocabulary | conforms | No banned commit types |
| orch.git.flow-direction-inviolable | conforms | Child `sub/…` publish-ref |
| orch.git.ftr-sub-topology | conforms | `sub/AST-974/AST-978-…` |
| orch.git.merge-on-checkout | conforms | No contrary guidance |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrites |
| orch.git.no-dev-agent-branches | conforms | Epic sub only |
| orch.git.one-epic-worktree-per-parent | conforms | `astral-AST-974/` |
| orch.git.three-permanent-branches | conforms | No new permanents |
| orch.pipeline.call-susan-for-product-decisions | conforms | Contract fixed by parent AC |
| orch.pipeline.plan-is-bible | conforms | Binding stages |
| orch.pipeline.project-scoped-queues | conforms | Single child |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready gate |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | tests out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Hedy |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign Hedy |
| orch.roles.pre-commit-path-bans | conforms | data + scripts/migrations |
| astral.batch.batch-id-first | conforms | No batch claim APIs |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Untouched |
| astral.batch.entity-agent-responses-latest-only | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | No new config |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src change |
| astral.layers.import-direction | conforms | Script → data + utils; data stays data |
| astral.layers.scripts-exempt-from-layer-rules | conforms | Migration CLI under scripts |
| astral.standards.data-raises-caller-logs | conforms | No logging in database.py |
| astral.standards.database-header-inventory | conforms | Existing `agent_data` only |
| astral.standards.dry-and-focused-functions | conforms | Reuses match helper (call site wrong — see finding) |
| astral.standards.in-scope-only | conforms | Refs-only; no vacuum/runtime rewrite |
| astral.standards.no-cross-contamination | conforms | Layered paths only |
| astral.standards.no-hardcoded-sets | conforms | No new enums |
| astral.standards.public-then-helpers | conforms | Public backfill API |
| astral.state.core-decides-transitions | conforms | Untouched |
| astral.state.job-prior-states-enforced | conforms | Untouched |
| astral.ui.single-gunicorn-worker | conforms | Migration script only |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.scripts-exempt-from-layer-rules, astral.standards.data-raises-caller-logs, astral.standards.database-header-inventory, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.agent.confidence-bounds — layers/paths miss
- astral.agent.do-task-delegation — layers/paths miss
- astral.agent.grade-vector-validation — layers/paths miss
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — layers/paths miss
- astral.git.engineer-test-tree-ban — paths miss
- astral.layers.core-vs-external-bright-line — layers/paths miss
- astral.layers.ui-config-driven-business-logic — layers/paths miss
- astral.patterns.coat-check-never-store-empty — layers/paths miss
- astral.patterns.render-verdict-orchestrates-consult — layers/paths miss
- astral.patterns.require-auth-on-protected-endpoints — layers/paths miss
- astral.standards.debug-contract-gated — layers miss (scripts not in applies_when); Stage 2 still checked under R6
- astral.standards.logging-via-utils — layers miss scripts
- astral.standards.utils-data-late-import-only — layers/paths miss
- astral.state.no-daisy-chain-in-run — layers/paths miss
- astral.ui.frontend-file-placement — layers/paths miss
- astral.ui.naming-conventions — layers/paths miss

## Findings

### fix-now — Stage 1 match call uses `exclude_agent_data_id` (inverts earliest / can cycle)

**Location:** Stage 1 step 2.3 — `match_id = _find_earliest_agent_data_content_match(conn, plain, exclude_agent_data_id=agent_data_id)`

**Finding:** `exclude_agent_data_id` is correct for **runtime insert** (AST-977: skip the id being written so a PK retry is not a false self-ref). For **backfill**, excluding the current row makes the earliest content row discover a *later* twin as “match,” so the plan would `SET ref_agent_data_id` on the canonical row (and, if both rows are still `ref IS NULL` in the same scan, later twin can point back — cycle). That violates parent Functional scope §1 / AC4 (earliest/canonical always `ref_agent_data_id` null) and AC7 (refs must point at earliest twins).

**Recommendation:** Call `_find_earliest_agent_data_content_match(conn, plain)` **without** exclude. Then:
- if `match_id is None` **or** `match_id == agent_data_id` → `canonical_or_unique` (do not UPDATE)
- else → `would_set_ref` / `set_ref` to `match_id` (always the true earliest)

Remove the “unreachable with exclude” self-ref error branch that assumed exclude was required. Keep refs-only UPDATE and no `block_data` mutation. Re-state Done-when: after live pass, every updated row’s `ref_agent_data_id` is an earlier twin; no earliest/canonical row gains a ref.

### acceptable

- Dry-run increments the same `updated` counter as live for `would_set_ref` — slightly overloaded name; actions list disambiguates.
- Debug contract lives in the migration script behind `--debug` (scripts layer); matches existing migration CLI posture.

— Joan
context_tokens≈48000

#### hedy — 2026-07-24T01:31:03.356Z
Plan: [`docs/features/foundation/ast-978-backfill-ref-agent-data-id-duplicates.md`](https://github.com/susansomerset/astral/blob/sub/AST-974/AST-978-backfill-ref-agent-data-id-duplicates/docs/features/foundation/ast-978-backfill-ref-agent-data-id-duplicates.md) on `origin/sub/AST-974/AST-978-backfill-ref-agent-data-id-duplicates` @ `baf2b73`.

**Self-assessment**
- **Scope:** Single-Component — one `backfill_agent_data_refs` in `database.py` plus one `scripts/migrations/backfill_agent_data_refs.py` CLI; no runtime write/read or UI.
- **Conf:** high — reuses AST-977 `_find_earliest_agent_data_content_match` / decompress / schema-ensure; mirrors existing dry-run migration CLIs; UPDATE is refs-only.
- **Risk:** Medium — wrong earliest twin would mis-point refs after backfill (resolve would follow the wrong canonical); mitigated by not reimplementing match and never mutating `block_data`.

---

# AST-978 — Backfill ref_agent_data_id on existing duplicates

- **Linear:** [AST-978](https://linear.app/astralcareermatch/issue/AST-978/backfill-ref-agent-data-id-on-existing-duplicates-add-a-self-reference)
- **Parent:** [AST-974 — Add a self-reference key to agent_data](https://linear.app/astralcareermatch/issue/AST-974/add-a-self-reference-key-to-agent-data)
- **Publish ref:** `origin/sub/AST-974/AST-978-backfill-ref-agent-data-id-duplicates`
- **Summary:** One-time operator-safe dry-run + live backfill that sets `ref_agent_data_id` on existing duplicate `agent_data` content rows to their earliest identical twin. Reuses AST-977’s `_find_earliest_agent_data_content_match` identity (exact logical plain text; no `block_type` filter). Never clears, nulls, or deletes any `block_data`. Does not change runtime write/read (AST-977). CLI accepts `--debug` for §1.5.1 found/recorded trails; quiet when debug is off.

## UAT fitness

- **AC restored:** Parent AST-974 AC 7–8 (this child): “Backfill dry-run + live sets refs on existing duplicates to earliest twins and leaves all `block_data` values unchanged.” / “With `debug=True` on touched backend backfill paths, a scannable per-index trail shows match-vs-new and the ids recorded/resolved; with `debug=False`, no new debug-contract noise.”
- **Correct outcome:** After live backfill, every non-earliest content duplicate has `ref_agent_data_id` pointing at the earliest canonical twin; every touched row still has the same `block_data` bytes as before; no earliest/canonical row gains a ref (`ref_agent_data_id` stays null); dry-run reports the same set of would-update rows without writing; `--debug` prints per-row match-vs-skip and ids; without `--debug`, no debug-contract lines.
- **Sibling check:** AST-977 (User Testing) owns schema + runtime write/read + resolve. This plan only UPDATEs `ref_agent_data_id` on legacy duplicates and reuses `_find_earliest_agent_data_content_match` / `_decompress_payload` / `_ensure_agent_data_schema` — it does not alter `save_agent_data` or getters. Verified by Boundaries and by not listing write/read files.
- **Not sufficient:** Removing an exception / making the script exit 0 without setting refs on duplicates, or “fixing” by deleting duplicate rows, is **not** done.
- **Wrong fix rejected:** Clearing or nulling `block_data` on backfill (space reclaim is Susan SQL + vacuum outside epic); matching on `(block_type, block_data)`; rewriting runtime write/read; skipping dry-run. Correct path is refs-only UPDATE via earliest twin + leave payloads intact.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add `backfill_agent_data_refs(*, dry_run) -> Dict` (no logging) | data |
| `scripts/migrations/backfill_agent_data_refs.py` | New operator CLI: default dry-run, `--execute`, `--debug` | scripts |

**Out of scope (explicit):**

| Item | Owner |
|------|--------|
| Schema / runtime write/read / resolve | **AST-977** (already shipped) |
| Clear / null / delete / vacuum historical `block_data` | Susan SQL outside epic |
| BLOCK_TYPES, prompt assembly, Anthropic | unchanged |
| UI / admin API wiring | none — local CLI only |
| `tests/` / bible | Betty |

**Dependency:** Blocked by AST-977. Build assumes `ref_agent_data_id` column + `_find_earliest_agent_data_content_match` exist on this branch (already present after merge `origin/ftr/AST-974-…`).

---

## Stage 1: Data-layer backfill function

**Done when:** `backfill_agent_data_refs(dry_run=True)` scans all content-bearing `agent_data` rows, returns counts + per-row actions without writing; `dry_run=False` UPDATEs only `ref_agent_data_id` on non-earliest duplicate rows to the true earliest twin and leaves every `block_data` value unchanged; after the live pass, every updated row’s `ref_agent_data_id` is an earlier twin and **no** earliest/canonical row gains a ref; re-run is idempotent (second live pass updates 0); `python3 -m py_compile src/data/database.py` passes. No logging in `database.py`.

1. In `src/data/database.py`, immediately after `_find_earliest_agent_data_content_match` / near the other `agent_data` helpers, add:

```python
def backfill_agent_data_refs(*, dry_run: bool = True) -> Dict[str, Any]:
    """Set ref_agent_data_id on duplicate content rows to earliest twin; never clear block_data.

    Returns dict with keys:
      scanned, updated, unchanged, skipped_already_ref, errors,
      actions: list of {agent_data_id, outcome, ref_agent_data_id}
    outcome values: "would_set_ref" | "set_ref" | "canonical_or_unique" | "already_ref" | "error"
    """
```

2. Implementation (literal; all work inside `_run_with_retry` + one connection):

   1. `_ensure_agent_data_schema(conn)`.
   2. Load candidate rows:

      ```sql
      SELECT agent_data_id, block_data, ref_agent_data_id, created_at
      FROM agent_data
      WHERE block_data IS NOT NULL
      ORDER BY created_at ASC, agent_data_id ASC
      ```

      Do **not** add LIMIT / OFFSET / batch caps.
   3. For each row:
      - If `ref_agent_data_id` is not null and `str(ref).strip() != ""`: increment `skipped_already_ref`, append action `outcome="already_ref"`, `ref_agent_data_id=<existing>`, continue.
      - Decompress via `_decompress_payload(row.block_data)` to `plain`. On decompress failure: increment `errors`, append `outcome="error"`, continue (do not abort the whole pass).
      - `match_id = _find_earliest_agent_data_content_match(conn, plain)` — **do not** pass `exclude_agent_data_id`. (`exclude` is for AST-977 runtime insert PK-retry only; on backfill it would make the earliest row match a *later* twin and could set a ref on the canonical row or create a cycle.)
      - If `match_id is None` **or** `match_id == agent_data_id`: this row is the earliest canonical (or unique) — increment `unchanged`, append `outcome="canonical_or_unique"`, `ref_agent_data_id=None`, continue. Do **not** UPDATE.
      - Else (`match_id` is a different, earlier twin):
        - If `dry_run`: do **not** UPDATE; increment `updated`; append `outcome="would_set_ref"`, `ref_agent_data_id=match_id`.
        - If not `dry_run`:

          ```sql
          UPDATE agent_data SET ref_agent_data_id = ? WHERE agent_data_id = ?
          ```

          with `(match_id, agent_data_id)`. Do **not** set `block_data` in the UPDATE. Increment `updated`; append `outcome="set_ref"`, `ref_agent_data_id=match_id`.
   4. Always increment `scanned` once per candidate row (including already-ref / error / unchanged).
   5. If not `dry_run`: `conn.commit()` once after the loop. If `dry_run`: never commit ref updates (no writes).
   6. Return the counts dict + full `actions` list (no truncation).
   7. Docstring must state: does not clear `block_data`; identity matches AST-977 (exact logical plain text; `block_type` ignored); calls `_find_earliest` without exclude so the canonical row never gains a ref; data layer does not log.

⚠️ **Decision:** Logic lives in `database.py` (same home as `_find_earliest_agent_data_content_match`) so the script cannot drift from runtime match semantics. Script only orchestrates CLI + debug logging (data raises / does not log — §1.5).

⚠️ **Decision:** Backfill must call `_find_earliest_agent_data_content_match(conn, plain)` with **no** `exclude_agent_data_id`. Self-match (`match_id == agent_data_id`) means canonical — leave ref null. Runtime `save_agent_data` keeps using exclude for PK-retry; that is out of scope here.

⚠️ **Decision:** Only rows with `block_data IS NOT NULL` are candidates. Rows that are already audit-style (null payload + ref) are out of this pass — runtime write already created them correctly.

⚠️ **Decision:** Keep historical `block_data` on rows that gain a ref. Parent AC 7 + Boundaries forbid clearing; Susan reclaim is separate SQL + vacuum.

---

## Stage 2: Operator CLI + debug trail

**Done when:** `python scripts/migrations/backfill_agent_data_refs.py` (no flags) prints a dry-run summary and writes nothing; `--execute` applies UPDATEs; `--debug` emits §1.5.1 per-index found/recorded lines for each action; without `--debug`, no new debug-contract lines; `python3 -m py_compile scripts/migrations/backfill_agent_data_refs.py` passes.

1. Create `scripts/migrations/backfill_agent_data_refs.py` with shebang `#!/usr/bin/env python3` and module docstring covering purpose, safety (default dry-run; never clears `block_data`), and usage:

```
python scripts/migrations/backfill_agent_data_refs.py
python scripts/migrations/backfill_agent_data_refs.py --execute
python scripts/migrations/backfill_agent_data_refs.py --execute --debug
```

2. Bootstrap (mirror `migrate_legacy_candidate_states.py` / `backfill_task_grouping_metadata.py`):

```python
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.data.database import backfill_agent_data_refs
from src.utils.logging import get_logger
```

3. `argparse`:
   - `--execute` — `store_true`; when absent, `dry_run=True` (operator-safe default).
   - `--debug` — `store_true`; default `False`.

4. `main() -> int`:
   1. Print `=== DRY RUN — no DB writes ===` when not `--execute`.
   2. `result = backfill_agent_data_refs(dry_run=not args.execute)`.
   3. If `args.debug`:
      - `log = get_logger(__name__, debug_flag=True)`
      - Let `actions = result["actions"]`, `M = len(actions)`.
      - For each `i, action` in enumerate(actions, start=1): emit one `debug_index` with universal `index {i}/{M}`, primary id `action["agent_data_id"]`, outcome summarizing match-vs-new (`would_set_ref` / `set_ref` / `canonical_or_unique` / `already_ref` / `error`) and `ref_agent_data_id={action.get("ref_agent_data_id")!r}`. Prefer ids/outcome only — do not dump `block_data`. Use `truncate_debug_content` only if any payload excerpt is ever logged (not required).
   4. Always `print(json.dumps({k: result[k] for k in ("scanned", "updated", "unchanged", "skipped_already_ref", "errors")}, indent=2))` (omit full `actions` from the JSON summary unless `--debug`, in which case printing actions is optional; debug-contract lines are the AC trail).
   5. Return `0` if `errors == 0` else `1`.

5. `if __name__ == "__main__": raise SystemExit(main())`.

⚠️ **Decision:** Default dry-run + explicit `--execute` (same safety posture as `migrate_legacy_candidate_states.py`), not default-live with optional `--dry-run`. Parent calls this “operator-safe.”

⚠️ **Decision:** Debug lives only in the script behind `--debug` → `debug=True` on `get_logger`. No logging inside `database.py`. Satisfies AC 8 and “data raises; callers log.”

---

## Self-Assessment

**Scope:** `Single-Component` — one data-layer backfill function plus one migration CLI; no runtime write/read or UI.

**Conf:** `high` — match helper and schema already shipped by AST-977; pattern mirrors existing `scripts/migrations/*` dry-run CLIs; AC forbids payload clearing so the UPDATE surface is a single column.

**Risk:** `Medium` — wrong earliest-twin choice would point refs at the wrong canonical row and change what resolve returns for those ids after backfill; mitigated by reusing `_find_earliest_agent_data_content_match` unchanged and never mutating `block_data`.

## Rules self-review

- **§1.3 DRY:** Reuse `_find_earliest_agent_data_content_match` / `_decompress_payload` / `_ensure_agent_data_schema`; do not reimplement match in the script.
- **§1.5 / data-raises-caller-logs:** No logging in `database.py`; decompress failures recorded in return counts; CLI logs only when `--debug`.
- **§1.5.1:** Index headers with universal `index N/M`, primary id, outcome; quiet when `--debug` absent.
- **§2.1:** No new config keys.
- **§3.3:** Script imports `data` + `utils.logging` only; no UI → data.
- **§3.5:** Names match parent vocabulary (`ref_agent_data_id`, backfill refs).
- **Unauthorized limits:** No row/batch caps on the scan (Susan rule).

## Revisions

### Revision 1 — 2026-07-24

Driven by: Joan `[plan-discuss] round=1 concern` fix-now — Stage 1 match call uses `exclude_agent_data_id` (inverts earliest / can cycle).

Changes:
- Stage 1 step 2.3: call `_find_earliest_agent_data_content_match(conn, plain)` **without** `exclude_agent_data_id`.
- Treat `match_id is None` **or** `match_id == agent_data_id` as `canonical_or_unique` (no UPDATE).
- Removed the “unreachable with exclude” self-ref error branch.
- Done-when / UAT Correct outcome: every updated ref points at an earlier twin; no earliest/canonical row gains a ref.
- Added Decision stating backfill must not use exclude (runtime insert may still use it in AST-977).

## Review (build stub)

**Built:** `origin/sub/AST-974/AST-978-backfill-ref-agent-data-id-duplicates` @ `4e591c4`

**Stages delivered:**
- Stage 1: `backfill_agent_data_refs` in `database.py` (no exclude; refs-only UPDATE) — `b1baa73`
- Stage 2: `scripts/migrations/backfill_agent_data_refs.py` (default dry-run, `--execute`, `--debug`) — `2735020`

**Betty:** manifest at **Code Complete** — dry-run vs execute; earliest twin only (canonical never gains ref); `block_data` unchanged; idempotent re-run; `--debug` trail / quiet without.

## Review (Radia — code-rubric.v1)

`[code-rubric] revision=1` · **Overall:** DISCUSS · tip at docs commit

### What’s solid
- `backfill_agent_data_refs` calls `_find_earliest` **without** exclude (Joan round-1); canonical self-match → `canonical_or_unique`; refs-only UPDATE; no `block_data` mutation; dry-run default; CLI `--debug` emits `debug_index` N/M; data layer silent; AST-977 hydrate `debug_index` already on tip.

### Issues
- **discuss:** Linear assignee is Radia; Joan named Hedy — restore engineer through resolve.
- **discuss (straggler):** Joan Excluded statutes in-scope on three-dot tip (all conforms) — mostly via AST-977 files co-present on this publish-ref.
- **advisory:** bare `except Exception` on decompress records `errors` and continues (plan-literal); fine with return-count visibility.

### Recommended actions
1. Restore Hedy as Linear assignee when resolving (review-child does not reassign).
2. No product fix-now for AST-978 stages 1–2.

## Resolution (2026-07-25)

- **fix-now:** none on AST-978 product.
- **discuss (assignee):** Linear assignee is already Hedy Lamarr at resolve — no reassignment needed.
- **discuss (straggler):** Noted only; Joan-excluded statutes scored conforms by Radia on three-dot tip — no code change.
- **advisory:** Left bare `except Exception` on decompress as plan-literal; failures stay visible via `errors` + actions.
)
