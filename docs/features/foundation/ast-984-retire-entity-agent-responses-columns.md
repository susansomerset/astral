<!-- linear-archive: AST-984 archived 2026-08-05 -->

## Linear archive (AST-984)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-984/retire-entity-agent-responses-columns-decommission-table-agent  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-975 — Decommission table AGENT_RESPONSES  
**Blocked by / blocks / related:** parent: AST-975

### Description

## What this implements

Drop `agent_responses` JSON columns on job/company/candidate, remove upsert/read paths, and update Code Rules + latest-only statute to the replacement contract. Susan confirmed column retirement as a separate child — empty/confusing columns must not persist.

## Acceptance criteria

5. Entity tables no longer have `agent_responses` columns, no code path reads/writes them, and Code Rules / the latest-only statute are updated to match — and UAT confirms latest-per-task lookup still works via the approved replacement (or is explicitly retired).

## Boundaries

* Does **not** reintroduce the standalone `agent_responses` table.
* Does **not** change `agent_data` block storage beyond whatever the replacement lookup needs.
* Requires mandate/statute revision for `astral.batch.entity-agent-responses-latest-only` / Code Rules §2.4.1.

## Notes for planning

* Columns are named like the retired table but currently hold latest-only refs into `agent_data` — plan must name the replacement lookup before deleting columns.
* Depends on table retirement siblings completing first so docs/runtime are not dual-writing.

## Git branch (authoritative)

Per orientation § Branch law. Publish to `origin/<publish-ref>` only.

### Comments

#### ada — 2026-07-28T00:18:50.803Z
origin/sub/AST-975/AST-984-retire-entity-agent-responses-columns @ `758e16b1` · §9a ftr dry-run clean · dev integration via squash `resolve(AST-984): origin/dev integration` (no Merge remote-tracking subjects on publish ref).

#### radia — 2026-07-28T00:15:36.960Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-984
**Publish ref:** `a9d16cc2142a0666ce7b4b7f84981c41b546deda` (`origin/sub/AST-975/AST-984-retire-entity-agent-responses-columns`)
**Overall:** DISCUSS

Diff baseline: `origin/dev...origin/sub/AST-975/AST-984-retire-entity-agent-responses-columns` (includes AST-981/982/983 ancestors + epic canon on tip).

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | conforms | No confidence/grade validation edits |
| astral.agent.do-task-delegation | scoped | conforms | `do_task` still owns RESPONSE storage; adds `entity_id` tagging |
| astral.agent.grade-vector-validation | scoped | conforms | Grade-vector validation untouched |
| astral.batch.batch-id-first | scoped | conforms | No claim/get/clear signature changes |
| astral.batch.batch-id-format | scoped | conforms | No batch_id format changes |
| astral.batch.claim-process-release | scoped | conforms | No claim→process→release edits |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | Statute amended to `entity_id` + list API before append/column removal |
| astral.config.config-source-of-truth | scoped | conforms | ENTITY_TYPES values unchanged; mandate rewritten in Stage 2 |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Scoring thresholds untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env handling changes |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan doc under `docs/features/`; not misplaced spike |
| astral.docs.features-single-file-per-ticket | scoped | conforms | One features file for AST-984 |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty `test()` touched bible/tests only |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer commits = src/docs/canon/utils; Betty owns tests |
| astral.layers.core-vs-external-bright-line | scoped | conforms | No external persistence; core→data only |
| astral.layers.import-direction | scoped | conforms | Dead `append_agent_response` imports removed with call sites |
| astral.layers.scripts-exempt-from-layer-rules | scoped | conforms | Backfill script retire is scripts one-off |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | UI docstring only (`agent_story`) |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | Coat-check keys untouched |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Consult removes entity-column append; uses batch `entity_id` tagging |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | no ui handler changes |
| astral.standards.data-raises-caller-logs | scoped | conforms | Data API only; no new data-layer logging |
| astral.standards.database-header-inventory | scoped | conforms | Header updated; entity JSON column dropped from inventory |
| astral.standards.debug-contract-gated | scoped | conforms | No new ungated debug-contract emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | One `list_entity_latest_agent_refs` for hop + story |
| astral.standards.in-scope-only | scoped | conforms | No table reintro / AST-974 / engineer test-tree edits |
| astral.standards.logging-via-utils | scoped | conforms | No logging facade changes |
| astral.standards.no-cross-contamination | scoped | conforms | Layered paths respected |
| astral.standards.no-hardcoded-sets | scoped | conforms | No new inline state sets |
| astral.standards.public-then-helpers | scoped | conforms | Public list API; private backfill/drop helpers |
| astral.standards.utils-data-late-import-only | scoped | conforms | Config comment-only in Stage 2 |
| astral.state.core-decides-transitions | scoped | conforms | No state-transition logic changes |
| astral.state.job-prior-states-enforced | scoped | conforms | No JOB_STATES edits |
| astral.state.no-daisy-chain-in-run | scoped | conforms | Hop hydration via `list_entity_latest_agent_refs` |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend file changes |
| astral.ui.naming-conventions | scoped | conforms | Docstring wording only |
| astral.ui.single-gunicorn-worker | scoped | conforms | No gunicorn/start path edits |
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-984): origin/tests 17695ac6…` |
| orch.git.commit-vocabulary | universal | conforms | `code`/`docs`/`test`/`merge-tests` vocab on publish-ref |
| orch.git.flow-direction-inviolable | universal | conforms | Tip on child `sub/` publish-ref |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-975/AST-984-retire-entity-agent-responses-columns` |
| orch.git.merge-on-checkout | universal | conforms | Stage 0 ftr/dev merge before product edits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No cherry-pick/rebase/force in AST-984 commits |
| orch.git.no-dev-agent-branches | universal | conforms | No agent-named publish branch |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Reviewed in `astral-AST-975` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branch |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | OQ1 drop path; replacement named in plan |
| orch.pipeline.plan-is-bible | universal | conforms | Staged cutover + hard rule match delivery |
| orch.pipeline.project-scoped-queues | universal | conforms | Single-child review |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Entered from Tests Passed |
| orch.roles.archie-approves-statutes | universal | needs-discussion | Statute/pattern frontmatter present (`approved_at: 2026-07-27`) but no visible Archie approval reply after Ada gate before Stages 3–5 |
| orch.roles.betty-owns-test-tree | universal | conforms | Tests/bible via Betty `test()` + `merge-tests` |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Implementer Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Review does not flip assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | Docs-only Radia commit |

## Pattern conformance

`pattern.batch.entity-agent-responses` — conforms (amended in `3745d22` with statute; canonical_refs → `list_entity_latest_agent_refs` / `save_agent_data` / `_store_response_block`)

## Plan adherence

Matches replacement lookup header and staged cutover: dual-write (`29cc49b`) → mandate (`ff7f9f7`/`3745d22`) → cut readers/delete append + column DROP (`03c5361`) → Betty tests (`17695ac6`). Parent AC5: entity columns gone; Code Rules §2.4.1 + statute describe `entity_id` list API; hop/story preserved. AST-983 `blockedBy` satisfied via ftr ancestry.

## Findings

**discuss:** `orch.roles.archie-approves-statutes` — Ada `[check-linear]` gate @ `ff7f9f7` asked @susan to approve statute/pattern draft before Stages 3–5; `3745d22` landed with `approved_by: Archie` / `approved_at: 2026-07-27` but thread has no Archie approval reply. Substance matches draft; resolve-child should attach approval artifact or Susan confirms.

**discuss (C4 straggler):** Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` — in-scope on three-dot; substance **conforms**.

**advisory:** `entity_cost` omitted from `list_entity_latest_agent_refs` refs per plan; still computed in batch `agent_ref` for consult tagging only.

### What’s solid

- Replacement lookup concrete and matches plan algorithm.
- Mandate before cutover commit order correct on publish-ref.
- Acceptance rg clean; entity JSON columns dropped on bootstrap.
- One Betty merge-tests SHA; broad regression + AST-984 coverage.

### Recommended actions

1. Link Archie approval (or confirm waiver) for statute gate discuss item.
2. Acknowledge C4 stragglers at resolve-child (no code).

**Notes:** Joan plan-rubric APPROVED (round 1 fix-nows closed in plan). Docs append on plan file @ tip.

context_tokens≈42000

#### betty — 2026-07-28T00:10:51.413Z
## QA test manifest (AST-984)

**Publish:** `origin/sub/AST-975/AST-984-retire-entity-agent-responses-columns` @ `6ec4f369` (`merge-tests(AST-984): origin/tests 17695ac6`)

### 1. Existing coverage (revised this pass)

| # | Path | What it guards |
| --- | --- | --- |
| 1 | `tests/component/data/database/test_agent_responses.py::TestAst984EntityColumnRetired` | `append_agent_response` gone; `list_entity_latest_agent_refs` + `ensure_batch_response_entity_ids`; seeded schemas lack entity `agent_responses` column |
| 2 | `tests/component/core/test_agent.py::TestAst984EntityColumnRetired` | do_task tags RESPONSE `entity_id`; no append |
| 3 | `tests/component/core/test_agent.py::TestAst981StandaloneTableAuditRetired` | table audit path still retired (regression) |
| 4 | `tests/component/core/test_roster.py::TestEntityAgentStory` | story from `list_entity_latest_agent_refs` |
| 5 | `tests/component/core/test_roster.py::TestEntityAgentStoryBranches` | story branches via list API |
| 6 | `tests/component/core/test_roster.py::TestAst726LatestOnlyRosterStory` | dedupe/normalize helpers retired |
| 7 | `tests/component/core/test_roster.py::TestAst727NormalizeAgentResponsesForBackfill` | normalize helper retired |
| 8 | `tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions` | hop hydration via list API mocks |
| 9 | `tests/component/core/test_agent.py::TestAst769GeneralCallerHydration` | general caller hydration via list API |
| 10 | `tests/component/core/test_tracker.py::TestTrackerFacades::test_ast486_consult_layer_facades_delegate_to_database` | tracker facade without append |
| 11 | `tests/component/core/test_consult.py::TestRunBatchConsultBranches::test_handles_missing_fabricated_and_bad_grades` | consult batch without entity-column append |
| 12 | `tests/component/scripts/test_backfill_latest_only_rubric_entity_data.py::TestAst984BackfillEntityColumnsRetired` | CLI exits 2 with AST-984 retired message |
| 13 | `tests/component/data/database/test_agent_responses.py::TestAst981StandaloneTableIoRetired` | standalone table I/O still retired (regression) |
| 14 | `tests/component/data/database/test_agent_responses.py::TestAst982StandaloneTableSunset` | table sunset + entity column drop on bootstrap (regression) |

### 2. Broken / obsolete tests (revised in this pass)

- `TestAst726AppendAgentResponseUpsert` — append API removed
- Roster dedupe/normalize tests — `dedupe_agent_responses_latest` / `normalize_agent_responses_for_backfill` removed
- Tracker/consult append mocks — entity JSON upsert path gone
- Hop/hydrate fixtures reading `entity["agent_responses"]` — now mock `list_entity_latest_agent_refs`
- Backfill script tests — CLI retired (exit 2)

### 3. Gaps

None — plan + bible agree coverage is sufficient for entity column retirement and replacement lookup.

### Re-run (narrowed)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agent_responses.py::TestAst981StandaloneTableIoRetired \
  tests/component/data/database/test_agent_responses.py::TestAst982StandaloneTableSunset \
  tests/component/data/database/test_agent_responses.py::TestAst984EntityColumnRetired \
  tests/component/core/test_agent.py::TestAst981StandaloneTableAuditRetired \
  tests/component/core/test_agent.py::TestAst984EntityColumnRetired \
  tests/component/core/test_roster.py::TestEntityAgentStory \
  tests/component/core/test_roster.py::TestEntityAgentStoryBranches \
  tests/component/core/test_roster.py::TestAst726LatestOnlyRosterStory \
  tests/component/core/test_roster.py::TestAst727NormalizeAgentResponsesForBackfill \
  tests/component/core/test_tracker.py::TestTrackerFacades::test_ast486_consult_layer_facades_delegate_to_database \
  tests/component/core/test_consult.py::TestRunBatchConsultBranches::test_handles_missing_fabricated_and_bad_grades \
  tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions \
  tests/component/core/test_agent.py::TestAst769GeneralCallerHydration \
  tests/component/scripts/test_backfill_latest_only_rubric_entity_data.py \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

### Bible shasums (`origin/sub/AST-975/AST-984-retire-entity-agent-responses-columns`)

- `docs/test-bible/data/database/agent_responses.md`: `b96372bf2987e0b6122fe27f9181babb9ae684235cfabb1c866e4be326f24542`
- `docs/test-bible/core/agent.md`: `4e835ee01d3ef65512d837b8255b1761cee6e9990335a8998a94a86983bfb58b`
- `docs/test-bible/core/roster.md`: `ef2d1a57c698efc76ec9e4b5db83a9590696cff448e188887388a8d8da5ca607`
- `docs/test-bible/core/consult.md`: `bc1b5a8979a8ea58d8dcbda592c2d44bdd21f416b3c0daf5693736930aa7d11b`
- `docs/test-bible/dev/backfill_latest_only_rubric_entity_data.md`: `0a2acea4902b0b73771e9937d3ca8da26f92cdd06ad3accd32f8a306eaa360be`

— Betty

#### ada — 2026-07-25T19:58:24.066Z
[check-linear] blocked: Stage 2 Archie statute gate (`orch.roles.archie-approves-statutes`) — need approval before committing `canon/statutes/**` / `canon/patterns/**` or starting Stage 3 (remove upserts / drop columns).

@susan (Archie)

**Publish tip (dual-write + Code Rules only):** `origin/sub/AST-975/AST-984-retire-entity-agent-responses-columns` @ `ff7f9f7`
- Stage 1: `agent_data.entity_id` + `list_entity_latest_agent_refs` + RESPONSE tagging; `append_agent_response` still dual-writes
- Stage 2 (partial): Code Rules §2.4.1 + ENTITY_TYPES comment rewritten to replacement contract
- **Not done:** canon statute/pattern commit; Stages 3–5

**Ask:** Approve the draft amend below?
1. Keep statute id `astral.batch.entity-agent-responses-latest-only` in place (default), **or**
2. Supersede with a new id (name it if so).

On approval I will commit statute + pattern with `approved_by: Archie` and fresh `approved_at`, then continue Stages 3–5.

---

### Draft — `canon/statutes/astral/batch/astral.batch.entity-agent-responses-latest-only.md`

```yaml
---
id: astral.batch.entity-agent-responses-latest-only
title: Entity latest agent refs via agent_data.entity_id
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "data"]
  paths: ["src/core/**", "src/data/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "<ISO date of your approval>"
---

# Statement

After each `do_task` RESPONSE write when an entity index is known, tag that `agent_data` RESPONSE row with `entity_id`. Latest-per-`task_key` refs are read via `list_entity_latest_agent_refs(entity_type, entity_id)`. Historical blocks remain in `agent_data`. Do not store latest-only refs on entity-row JSON `agent_responses` columns.

## Rationale

Entity rows stay free of confusing mirror columns; full prompt/response history stays queryable by batch; hop hydration and agent_story use one list API.

## Examples

### Conforming

- `_store_response_block` / `save_agent_data` set `entity_id` on RESPONSE when `index` is known.
- Hop / `get_entity_agent_story` call `list_entity_latest_agent_refs`.

### Violating

- Upserting latest-only refs onto entity JSON `agent_responses` columns after column retirement.
- Leaving RESPONSE rows without `entity_id` when an entity index was available.
```

### Draft — `canon/patterns/batch/pattern.batch.entity-agent-responses.md`

```yaml
---
id: pattern.batch.entity-agent-responses
name: Entity latest agent refs (agent_data.entity_id)
status: approved
proposed_in: AST-984
approved_by: Archie
approved_at: "<ISO date of your approval>"
canonical_refs:
  - path: src/core/agent.py
    symbol: _store_response_block
  - path: src/data/database.py
    symbol: list_entity_latest_agent_refs
  - path: src/data/database.py
    symbol: save_agent_data
  - path: docs/ASTRAL_CODE_RULES.md
    symbol: "§2.4.1"
related_statutes:
  - astral.batch.entity-agent-responses-latest-only
supersedes: null
superseded_by: null
---

# Problem

Callers need a lightweight latest-only pointer from an entity to `agent_data` without entity-row JSON mirror columns or unbounded history on the entity.

# Solution shape

Tag RESPONSE rows with `entity_id` on write; reconstruct latest-per-`task_key` refs via `list_entity_latest_agent_refs`. Point at `canonical_refs` — do not paste large code into this catalog entry.

## When not to use

- Persisting full prompt/response blobs on the entity row.
- Reintroducing entity JSON `agent_responses` upserts after AST-984 cutover.
- Inventing a parallel audit/refs table.
```

— Ada

#### joan — 2026-07-25T19:16:33.917Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-984
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-975/AST-984-retire-entity-agent-responses-columns`
**Implementer:** Ada (parent Team table / plan author)
**Plan Discuss:** round=1 completed (concern + reply); re-validate from Plan Ready after revision @ `891fa18`

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| AC1 — standalone table gone | N/A — Stage 0 assumes AST-982 on ftr |
| AC2 — no table create/read/write | N/A — AST-981/982; Stage 0 search gate |
| AC3 — do_task / agent_data without table | N/A — AST-981; agent_data blocks kept + `entity_id` |
| AC4 — mandate table vs column | N/A — AST-983; Stage 2 then retires column contract |
| AC5 — drop columns; update Code Rules/statute; replacement lookup | Stages 1–5: `entity_id` + `list_entity_latest_agent_refs`; Archie-gated statute; then cutover + DROP |
| AC6 — keep columns | N/A — OQ1 drop path |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| Cutover hard rule + Replacement lookup | Parent AC5 + child Notes + parent “no silent drop while mandate requires columns” |
| Stage 0 merge gate | blockedBy AST-983 / ftr ancestors |
| Stage 1 dual-write entity_id + list API | AC5 plumbing; statute still satisfied via append |
| Stage 2 Code Rules + Archie statute/pattern | AC5 mandate update; `orch.roles.archie-approves-statutes` |
| Stage 3 cut readers; delete append | AC5 no read/write of columns |
| Stage 4 DROP columns | AC5 entity tables lack columns |
| Stage 5 scripts/acceptance | Cleanup + rg gates |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| astral.agent.confidence-bounds | conforms | Untouched |
| astral.agent.do-task-delegation | conforms | RESPONSE storage stays in do_task; adds entity_id on RESPONSE |
| astral.agent.grade-vector-validation | conforms | Untouched |
| astral.batch.batch-id-first | conforms | Untouched |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Untouched |
| astral.batch.entity-agent-responses-latest-only | conforms | Stage 2 revises statute before Stage 3 removes entity upserts |
| astral.config.config-source-of-truth | conforms | Comment-only with Code Rules in Stage 2 |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | Untouched |
| astral.git.betty-no-src-or-features | conforms | Engineer src/docs/canon; Betty tests |
| astral.layers.core-vs-external-bright-line | conforms | No external persistence |
| astral.layers.import-direction | conforms | Dead imports removed with call sites |
| astral.layers.scripts-exempt-from-layer-rules | conforms | Script retire one-off |
| astral.layers.ui-config-driven-business-logic | conforms | UI docstring only |
| astral.patterns.coat-check-never-store-empty | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Only removes append after shared batch |
| astral.patterns.require-auth-on-protected-endpoints | conforms | Untouched |
| astral.standards.data-raises-caller-logs | conforms | Data API only |
| astral.standards.database-header-inventory | conforms | Header updated with column drop |
| astral.standards.debug-contract-gated | conforms | Untouched |
| astral.standards.dry-and-focused-functions | conforms | One list API for hop + story |
| astral.standards.in-scope-only | conforms | Table/AST-974/Betty out of scope |
| astral.standards.logging-via-utils | conforms | Untouched |
| astral.standards.no-cross-contamination | conforms | Layered paths |
| astral.standards.no-hardcoded-sets | conforms | Untouched |
| astral.standards.public-then-helpers | conforms | New public list API |
| astral.standards.utils-data-late-import-only | conforms | Comment-only |
| astral.state.core-decides-transitions | conforms | Untouched |
| astral.state.job-prior-states-enforced | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | conforms | Hop hydration via replacement API |
| astral.ui.naming-conventions | conforms | Docstring only |
| astral.ui.single-gunicorn-worker | conforms | Untouched |
| orch.git.betty-merge-tests-one-sha | conforms | No merge-tests |
| orch.git.commit-vocabulary | conforms | Normal engineer commits |
| orch.git.flow-direction-inviolable | conforms | sub publish-ref + ftr gate |
| orch.git.ftr-sub-topology | conforms | Parent Git table |
| orch.git.merge-on-checkout | conforms | Stage 0 |
| orch.git.no-cherry-pick-rebase-force | conforms | None instructed |
| orch.git.no-dev-agent-branches | conforms | sub/ only |
| orch.git.one-epic-worktree-per-parent | conforms | AST-975 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Stage 2 assigns Susan for statute approval |
| orch.pipeline.plan-is-bible | conforms | Hard cutover rule + staged preconditions |
| orch.pipeline.project-scoped-queues | conforms | Single-child |
| orch.pipeline.status-gates-skill-entry | conforms | Validate path |
| orch.roles.archie-approves-statutes | conforms | Stage 2: draft → Susan → stop → commit with refreshed approved_at |
| orch.roles.betty-owns-test-tree | conforms | Betty note |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Returns to Ada |
| orch.roles.pre-commit-path-bans | conforms | No engineer test-tree commits |

## Considered and excluded

**Considered:** astral.agent.confidence-bounds; astral.agent.do-task-delegation; astral.agent.grade-vector-validation; astral.batch.batch-id-first; astral.batch.batch-id-format; astral.batch.claim-process-release; astral.batch.entity-agent-responses-latest-only; astral.config.config-source-of-truth; astral.config.pass-threshold-vs-score-floor; astral.config.secrets-and-env-specific-from-environ; astral.git.betty-no-src-or-features; astral.layers.core-vs-external-bright-line; astral.layers.import-direction; astral.layers.scripts-exempt-from-layer-rules; astral.layers.ui-config-driven-business-logic; astral.patterns.coat-check-never-store-empty; astral.patterns.render-verdict-orchestrates-consult; astral.patterns.require-auth-on-protected-endpoints; astral.standards.data-raises-caller-logs; astral.standards.database-header-inventory; astral.standards.debug-contract-gated; astral.standards.dry-and-focused-functions; astral.standards.in-scope-only; astral.standards.logging-via-utils; astral.standards.no-cross-contamination; astral.standards.no-hardcoded-sets; astral.standards.public-then-helpers; astral.standards.utils-data-late-import-only; astral.state.core-decides-transitions; astral.state.job-prior-states-enforced; astral.state.no-daisy-chain-in-run; astral.ui.naming-conventions; astral.ui.single-gunicorn-worker; orch.git.betty-merge-tests-one-sha; orch.git.commit-vocabulary; orch.git.flow-direction-inviolable; orch.git.ftr-sub-topology; orch.git.merge-on-checkout; orch.git.no-cherry-pick-rebase-force; orch.git.no-dev-agent-branches; orch.git.one-epic-worktree-per-parent; orch.git.three-permanent-branches; orch.pipeline.call-susan-for-product-decisions; orch.pipeline.plan-is-bible; orch.pipeline.project-scoped-queues; orch.pipeline.status-gates-skill-entry; orch.roles.archie-approves-statutes; orch.roles.betty-owns-test-tree; orch.roles.chuckles-never-ticket-assignee; orch.roles.engineer-assignee-through-resolve; orch.roles.pre-commit-path-bans

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — paths miss
- astral.git.engineer-test-tree-ban — paths miss
- astral.ui.frontend-file-placement — paths miss

## Findings

None fix-now.

- **acceptable** — Round-1 fix-nows closed: mandate/Archie before upsert removal/column drop; Archie gate with stop + refreshed frontmatter; `entity_cost` rg check; id vs supersede deferred to Archie.
- **acceptable** — Self-assessment MAJOR-CHANGE / Conf Medium / Risk HIGH remains honest; dual-write held through Stage 2 is the right mitigation.

## R6 checklist (summary)

Definition fidelity: AC5 replacement named; parent boundary respected by Stage 2-before-3/4. Layers OK. Config comment with Code Rules. Patterns: hop/story preserved. Archie statute gate present. Self-assessment honest.

context_tokens≈115000

— Joan

#### ada — 2026-07-25T19:15:15.104Z
[plan-discuss] round=1 reply

Revised plan @ `891fa18`: https://github.com/susansomerset/astral/blob/sub/AST-975/AST-984-retire-entity-agent-responses-columns/docs/features/foundation/ast-984-retire-entity-agent-responses-columns.md

**Delta vs fix-now**
1. **Mandate before upsert removal / column drop:** Reordered to Stage 1 dual-write → **Stage 2 Code Rules + Archie-gated statute/pattern** → Stage 3 cut readers/delete `append_agent_response` → Stage 4 DROP columns → Stage 5 scripts/acceptance. Hard rule: no publishable HEAD may remove entity upserts or drop columns while the live statute still requires them.
2. **Archie statute gate:** Stage 2 step 3 — draft amend → assign Susan → **stop** → commit `canon/statutes/**` (+ matching pattern) only after approval with refreshed `approved_by: Archie` / `approved_at`. Id keep vs supersede deferred to Archie (Joan discuss).

Also: `entity_cost` omission now has an explicit non-UI consumer `rg` check before Stage 3 reader cutover.

#### joan — 2026-07-25T19:13:41.949Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-984
**Overall:** REVISE
**Publish ref:** `origin/sub/AST-975/AST-984-retire-entity-agent-responses-columns`
**Implementer:** Ada (parent Team table / plan author)

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| AC1 — standalone table gone | N/A — boundary / Stage 0 assumes AST-982 already on ftr |
| AC2 — no table create/read/write | N/A — AST-981/982; Stage 0 search gate |
| AC3 — do_task / agent_data without table | N/A — AST-981; this ticket keeps agent_data blocks |
| AC4 — mandate distinguishes table vs column | N/A — AST-983; Stage 4 then retires column language entirely |
| AC5 — drop entity columns; update Code Rules/statute; UAT via replacement or explicit retire | Stages 1–4 name `agent_data.entity_id` + `list_entity_latest_agent_refs` (not explicit retire) — **stage order / Archie gate incomplete (fix-now)** |
| AC6 — keep columns | N/A — OQ1 chose drop; this child is the drop path |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| Replacement lookup header | Parent AC5 “approved replacement”; child Notes “name replacement before deleting” |
| Stage 0 merge gate | Parent sequencing after #3; blockedBy AST-983 |
| Stage 1 entity_id + list API + dual-write | AC5 replacement plumbing; agent_data allowed “whatever lookup needs” |
| Stage 2 cut readers/writers; delete append | AC5 “no code path reads/writes” columns |
| Stage 3 DROP columns | AC5 “entity tables no longer have columns” |
| Stage 4 mandate/canon/scripts | AC5 Code Rules + statute update — **must not trail Stages 2–3** |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| astral.agent.confidence-bounds | conforms | No confidence-bounds changes |
| astral.agent.do-task-delegation | conforms | do_task still owns RESPONSE storage; adds entity_id on RESPONSE only |
| astral.agent.grade-vector-validation | conforms | Untouched |
| astral.batch.batch-id-first | conforms | No claim signature changes |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Untouched |
| astral.batch.entity-agent-responses-latest-only | needs-discussion | Replacement named, but Stage 2 removes entity upserts before Stage 4 revises this statute |
| astral.config.config-source-of-truth | conforms | Comment-only ENTITY_TYPES after mandate change |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | Untouched |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src/docs/canon; Betty owns tests |
| astral.layers.core-vs-external-bright-line | conforms | No external persistence |
| astral.layers.import-direction | conforms | Removes dead imports with call sites |
| astral.layers.scripts-exempt-from-layer-rules | conforms | Script retire is one-off |
| astral.layers.ui-config-driven-business-logic | conforms | UI docstring only |
| astral.patterns.coat-check-never-store-empty | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Only removes append call after shared batch |
| astral.patterns.require-auth-on-protected-endpoints | conforms | Untouched |
| astral.standards.data-raises-caller-logs | conforms | Data API raises; no new data logging |
| astral.standards.database-header-inventory | conforms | Header inventory update planned with column drop |
| astral.standards.debug-contract-gated | conforms | Untouched |
| astral.standards.dry-and-focused-functions | conforms | One list API for hop + story |
| astral.standards.in-scope-only | conforms | Explicit out-of-scope table/AST-974/Betty trees |
| astral.standards.logging-via-utils | conforms | Untouched |
| astral.standards.no-cross-contamination | conforms | Layered paths only |
| astral.standards.no-hardcoded-sets | conforms | No new state sets |
| astral.standards.public-then-helpers | conforms | New list API is public data entrypoint |
| astral.standards.utils-data-late-import-only | conforms | Comment-only in config |
| astral.state.core-decides-transitions | conforms | Untouched |
| astral.state.job-prior-states-enforced | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | conforms | Hop hydration preserved via replacement API |
| astral.ui.naming-conventions | conforms | Docstring only |
| astral.ui.single-gunicorn-worker | conforms | Untouched |
| orch.git.betty-merge-tests-one-sha | conforms | No merge-tests work |
| orch.git.commit-vocabulary | conforms | Normal engineer commits on publish-ref |
| orch.git.flow-direction-inviolable | conforms | Child sub publish-ref + ftr merge gate |
| orch.git.ftr-sub-topology | conforms | Publish ref matches parent Git table |
| orch.git.merge-on-checkout | conforms | Stage 0 merge gate |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | conforms | Uses sub/ publish-ref |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree AST-975 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | OQ1 answered; replacement rejects “no lookup” |
| orch.pipeline.plan-is-bible | needs-discussion | Stages executable but order conflicts with live statute (see fix-now) |
| orch.pipeline.project-scoped-queues | conforms | Single-child |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready path |
| orch.roles.archie-approves-statutes | violates | Stage 4 amends `canon/statutes/**` without Archie approval / `approved_at` refresh step |
| orch.roles.betty-owns-test-tree | conforms | Betty note; engineer test-tree ban |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Returns to Ada |
| orch.roles.pre-commit-path-bans | conforms | No engineer test-tree commits |

## Considered and excluded

**Considered:** astral.agent.confidence-bounds; astral.agent.do-task-delegation; astral.agent.grade-vector-validation; astral.batch.batch-id-first; astral.batch.batch-id-format; astral.batch.claim-process-release; astral.batch.entity-agent-responses-latest-only; astral.config.config-source-of-truth; astral.config.pass-threshold-vs-score-floor; astral.config.secrets-and-env-specific-from-environ; astral.git.betty-no-src-or-features; astral.layers.core-vs-external-bright-line; astral.layers.import-direction; astral.layers.scripts-exempt-from-layer-rules; astral.layers.ui-config-driven-business-logic; astral.patterns.coat-check-never-store-empty; astral.patterns.render-verdict-orchestrates-consult; astral.patterns.require-auth-on-protected-endpoints; astral.standards.data-raises-caller-logs; astral.standards.database-header-inventory; astral.standards.debug-contract-gated; astral.standards.dry-and-focused-functions; astral.standards.in-scope-only; astral.standards.logging-via-utils; astral.standards.no-cross-contamination; astral.standards.no-hardcoded-sets; astral.standards.public-then-helpers; astral.standards.utils-data-late-import-only; astral.state.core-decides-transitions; astral.state.job-prior-states-enforced; astral.state.no-daisy-chain-in-run; astral.ui.naming-conventions; astral.ui.single-gunicorn-worker; orch.git.betty-merge-tests-one-sha; orch.git.commit-vocabulary; orch.git.flow-direction-inviolable; orch.git.ftr-sub-topology; orch.git.merge-on-checkout; orch.git.no-cherry-pick-rebase-force; orch.git.no-dev-agent-branches; orch.git.one-epic-worktree-per-parent; orch.git.three-permanent-branches; orch.pipeline.call-susan-for-product-decisions; orch.pipeline.plan-is-bible; orch.pipeline.project-scoped-queues; orch.pipeline.status-gates-skill-entry; orch.roles.archie-approves-statutes; orch.roles.betty-owns-test-tree; orch.roles.chuckles-never-ticket-assignee; orch.roles.engineer-assignee-through-resolve; orch.roles.pre-commit-path-bans

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — paths miss
- astral.git.engineer-test-tree-ban — paths miss (no tests/** in Files Changed)
- astral.ui.frontend-file-placement — paths miss

## Findings

### fix-now

1. **Location:** Stages 2 → 3 → 4 order; parent Boundary on silent column drop while mandate still requires entity latest-only refs; R3 `astral.batch.entity-agent-responses-latest-only`
   **Finding:** Stage 2 deletes `append_agent_response` while Stage 4 has not yet revised the active statute/Code Rules §2.4.1 that still mandate entity-row latest-only upserts. Stage 3 then drops the columns before Stage 4. Any intermediate publishable HEAD violates the live statute and the parent “no silent drop while mandate still requires columns” boundary.
   **Recommendation:** Reorder so Code Rules §2.4.1 + statute/pattern describe the `entity_id` / `list_entity_latest_agent_refs` contract **before** Stage 2 removes entity JSON upserts and **before** Stage 3 drops columns. Keep Stage 1 dual-write until that mandate cutover is in place (or land mandate + Stage 2 in one atomic commit explicitly).

2. **Location:** Stage 4 steps 2–3; `orch.roles.archie-approves-statutes`
   **Finding:** Plan amends `canon/statutes/astral/batch/astral.batch.entity-agent-responses-latest-only.md` without an Archie approval gate (`approved_by: Archie`, refresh `approved_at`). Statute corpus edits require Archie approval recorded in frontmatter.
   **Recommendation:** Add an explicit Stage step: draft statute amend → assign Susan/Archie for approval → only then commit with updated `approved_at`. Keep statute id if Archie agrees; otherwise supersede per Archie’s call (your Medium-conf note).

### discuss

- In-place statute id rewrite vs supersede — defer to Archie at the approval gate above.
- Omitting `entity_cost` from reconstructed refs — OK for `AgentStoryEntry` if nothing else requires it; confirm no non-UI consumer before drop.

### acceptable

- Replacement lookup is named with rejected alternatives (no new audit table; no “retire lookup entirely”; no rename-column; no AST-974 dependency) — satisfies child Notes / AC5 “approved replacement”.
- Self-assessment MAJOR-CHANGE / Conf Medium / Risk HIGH is honest for hop + agent_story cutover.
- Stage 0 ftr ancestor gate + Betty test-tree ban are correct.

## R6 checklist (summary)

Definition fidelity: replacement named (good); mandate/cutover order incomplete (fix-now). Layers OK. Config comment-only. File placement OK. Patterns: hop/story preserved by design. DRY: one list API. Scope: siblings gated. Self-assessment honest.

context_tokens≈105000

— Joan

#### ada — 2026-07-25T19:03:50.927Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-975/AST-984-retire-entity-agent-responses-columns/docs/features/foundation/ast-984-retire-entity-agent-responses-columns.md

**Replacement lookup (named in plan):** add `agent_data.entity_id` on RESPONSE writes; `list_entity_latest_agent_refs(entity_type, entity_id)` rebuilds latest-per-`task_key` refs from RESPONSE rows + batch prompt blocks; hop hydration + `get_entity_agent_story` switch to that API; then drop entity JSON columns. No new audit table. Build gated on AST-981/982/983 on ftr.

**Self-assessment**
- **Scope:** MAJOR-CHANGE — `agent_data` schema/write path, hop + agent_story readers, DDL drop on company/job/candidate, Code Rules §2.4.1 + canon statute/pattern, retire entity-column backfill script.
- **Conf:** Medium — replacement is concrete and fits “no new audit table,” but OQ1 did not name the lookup; Joan may want statute supersede vs in-place rewrite. Pre-drop backfill required for historical RESPONSE rows.
- **Risk:** HIGH — bad cutover breaks run_next hop tokens and job/company agent_story; mitigated by dual-write stage, ensure-time backfill before DROP, preserved failure-prefix / anchor filters.

---

# AST-984 — Retire entity agent_responses columns

**Linear:** [AST-984 — Retire entity agent_responses columns (Decommission table AGENT_RESPONSES)](https://linear.app/astralcareermatch/issue/AST-984/retire-entity-agent-responses-columns-decommission-table-agent)

**Parent:** [AST-975 — Decommission table AGENT_RESPONSES](https://linear.app/astralcareermatch/issue/AST-975/decommission-table-agent-responses) (AC reference only)

**Publish ref:** `origin/sub/AST-975/AST-984-retire-entity-agent-responses-columns`

**Blocked by:** AST-983 (docs/bible/test table sweep). Build waits until AST-981 + AST-982 + AST-983 are ancestors of `origin/ftr/AST-975-decommission-table-agent-responses`.

Susan confirmed OQ1: drop the entity JSON columns as a separate child. This ticket removes `agent_responses` from company / job / candidate, deletes upsert/read paths, and revises Code Rules §2.4.1 + statute `astral.batch.entity-agent-responses-latest-only` (and its pattern) to the **replacement lookup** named below. Durable blocks stay in `agent_data`. Does not reintroduce the standalone `agent_responses` **table**. Does not implement AST-974 self-reference.

**Cutover order (hard rule):** Code Rules §2.4.1 + Archie-approved statute/pattern amend land **before** any commit that removes `append_agent_response` or drops entity JSON columns. Dual-write (entity JSON upsert + RESPONSE `entity_id`) stays live until that mandate cutover is published. No intermediate publishable HEAD may violate the still-live entity-column statute.

## Replacement lookup (authoritative — decide before any column drop)

**Problem today:** Latest-per-`task_key` pointers live on entity rows as JSON (`append_agent_response`). Callers that need them:

- `_hop_agent_ref_for_parent` / `_hydrate_caller_chain_context` in `src/core/agent.py` (run_next hop tokens)
- `get_entity_agent_story` in `src/core/roster.py` → job/company detail `agent_story` UI

`agent_data` today has `entity_type`, `task_key`, `batch_id` but **no `entity_id`**, so it cannot answer “latest successful run for this entity + task_key” without the entity JSON column.

**Approved replacement (this plan):**

1. Add nullable `entity_id TEXT` to `agent_data` (ensure-time migration + index `(entity_type, entity_id, task_key, created_at)`).
2. On every successful (and failure-audit) **RESPONSE** write from `do_task` when `index` is known, set `entity_id=index` via `save_agent_data`. Shared prompt blocks (SYSTEM / CACHE_* / TASK / NO_CACHE) stay **without** `entity_id` (batch-scoped, shared).
3. New data API `list_entity_latest_agent_refs(entity_type, entity_id) -> List[dict]`:
   - Select RESPONSE rows for that `entity_id` (and matching `entity_type`), order by `created_at` desc.
   - Keep one row per `task_key` (latest wins).
   - For each kept RESPONSE, build a ref shaped like today’s entity entry: `{task_key, batch_id, created_at, prompt_blocks}` where `prompt_blocks` = all non-RESPONSE blocks from `get_agent_data_by_batch(batch_id)` **plus** this RESPONSE’s `{type, id}` only (exclude sibling entities’ RESPONSE rows in the same batch).
4. After mandate cutover (Stage 2): rewrite hop hydration and `get_entity_agent_story` to use that API (load entity id from the row’s PK; do not read `entity["agent_responses"]`).
5. After mandate cutover: stop calling `append_agent_response` from agent / roster / consult; delete `append_agent_response` (data + tracker wrapper).
6. One-time ensure-time **backfill** before column drop: walk existing company/job/candidate `agent_responses` JSON; for each entry’s RESPONSE `prompt_blocks[].id`, `UPDATE agent_data SET entity_id=? WHERE agent_data_id=? AND (entity_id IS NULL OR entity_id='')`. Then drop the entity columns.
7. `entity_cost` on the old JSON refs is **not** required by `AgentStoryEntry` UI — omit from reconstructed refs (do not invent timesheet joins). Before Stage 3 reader cutover, confirm with `rg -n 'entity_cost' src --glob '*.py'` that no non-ledger consumer reads `entity_cost` off entity `agent_responses` JSON entries (dispatcher/ledger `entity_cost` columns are unrelated and stay).

**Rejected alternatives:**

- Explicitly retire latest-per-task lookup with no replacement — breaks hop chains and agent_story; parent AC 5 allows retirement only if approved; Susan asked to drop columns because they are confusing, not to delete hop/UI behavior.
- New parallel audit / refs **table** — parent forbids inventing a replacement audit table.
- Rename entity column (`agent_data_refs`) — still an entity-row JSON mirror; does not remove the confusion Susan called out.
- Depend on AST-974 self-ref — different problem; parent says adjacent, not required.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add `agent_data.entity_id`; extend `save_agent_data`; add `list_entity_latest_agent_refs` + ensure-time backfill; remove `append_agent_response`; drop `agent_responses` from company/job/candidate CREATE + parse/update paths via table rebuild (same pattern as existing `job_next` rebuilds); strip ADD COLUMN migrations that re-add the JSON column; header inventory | data |
| `src/core/agent.py` | Pass `entity_id=index` into RESPONSE `save_agent_data` path; remove `append_agent_response` import/calls and entity-ref build that only fed the column; rewrite `_hop_agent_ref_for_parent` to use `list_entity_latest_agent_refs` | core |
| `src/core/tracker.py` | Remove `append_agent_response` wrapper | core |
| `src/core/roster.py` | Remove batch `append_agent_response` calls; rewrite `get_entity_agent_story` to use `list_entity_latest_agent_refs`; delete or stop exporting `dedupe_agent_responses_latest` / `normalize_agent_responses_for_backfill` if nothing else needs them after column drop | core |
| `src/core/consult.py` | Remove per-job `append_agent_response` calls after shared batch | core |
| `src/ui/api/api_jobs.py` | Docstring only if it still says “agent_responses attached” → “agent_story” | ui |
| `src/utils/config.py` | ENTITY_TYPES comment: remove entity-column `agent_responses` **in the same commit as** the Code Rules §2.4.1 rewrite (Stage 2) | utils |
| `docs/ASTRAL_CODE_RULES.md` | Rewrite §2.4.1 + batch bullets to the agent_data `entity_id` latest-RESPONSE contract **before** removing entity upserts / dropping columns | docs |
| `canon/statutes/astral/batch/astral.batch.entity-agent-responses-latest-only.md` | Draft amend → Archie/Susan approval → commit only with refreshed `approved_by: Archie` + `approved_at` (keep id unless Archie directs supersede) | docs |
| `canon/patterns/batch/pattern.batch.entity-agent-responses.md` | Update problem/solution + `canonical_refs` in the same Archie-gated canon commit as the statute | docs |
| `scripts/migrations/backfill_latest_only_rubric_entity_data.py` | Retire: CLI exits with AST-984 retired message (no entity-column writes) | scripts |

**Out of scope:**

| Item | Owner |
|------|--------|
| Standalone `agent_responses` **table** drop / ensure removal | AST-982 (must already be gone on ftr before build) |
| Table-only docs/bible/test sweep | AST-983 |
| AST-974 `agent_data` self-reference / dedupe | separate epic |
| Engineer commits under `tests/` / `docs/test-bible/**` | Betty qa-child |

**Betty note:** Expect broad test fallout (`test_agent.py` append mocks, roster story/dedupe tests, database append tests, backfill script tests). Engineer does not edit those trees.

## Stage 0: Merge gate (before any product edit)

**Done when:** `origin/ftr/AST-975-decommission-table-agent-responses` contains AST-981 + AST-982 + AST-983 tips (standalone table gone; mandate already distinguishes retired table). Working tree has merged `origin/dev` and that ftr tip; `BEHIND=0` vs `origin/dev`.

1. `git fetch origin && git merge origin/dev && git merge origin/ftr/AST-975-decommission-table-agent-responses`.
2. Confirm by search that standalone-table I/O / ensure from AST-981/982 is already absent on HEAD (no `add_agent_response_entry`, no `_ensure_agent_responses_schema` CREATE path). If still present, **stop** and comment on AST-984 — do not dual-write or drop entity columns while the table path is live.
3. Confirm Linear `blockedBy` AST-983 is Done / rolled into ftr. If not, **stop** (do not start Stage 1).

## Stage 1: agent_data.entity_id + list API + RESPONSE tagging (dual-write)

**Done when:** New DBs and upgraded DBs have `agent_data.entity_id`; `save_agent_data` accepts optional `entity_id`; RESPONSE writes from `do_task` set it when `index` is set; `list_entity_latest_agent_refs` returns latest-per-task_key refs with prompt_blocks as specified; entity JSON columns still exist and `append_agent_response` **still runs** (dual-write). Dual-write must remain until Stage 2 mandate is published.

1. In `src/data/database.py` `_ensure_agent_data_schema`: on CREATE include `entity_id TEXT`; on existing tables `ALTER TABLE agent_data ADD COLUMN entity_id TEXT` if missing; create index `idx_agent_data_entity_task` on `(entity_type, entity_id, task_key, created_at)` if missing.
2. Extend `save_agent_data(..., entity_id: Optional[str] = None)` to INSERT the column (NULL when omitted).
3. Add `list_entity_latest_agent_refs(entity_type: str, entity_id: str) -> List[Dict[str, Any]]` implementing the replacement algorithm in the header (RESPONSE-only index; attach batch non-RESPONSE blocks + this RESPONSE).
4. In `src/core/agent.py` `_store_response_block`, pass `entity_id=index` into `save_agent_data` when `index` is truthy. Do not set `entity_id` on `_store_prompt_blocks` saves.
5. Leave `append_agent_response` call sites in place (still dual-writing). Do **not** rewrite hop/story readers yet; do **not** delete upserts; do **not** drop columns.

⚠️ **Decision:** Dual-write until mandate cutover (Stage 2) so no publishable HEAD removes entity upserts while statute `astral.batch.entity-agent-responses-latest-only` still requires them.

## Stage 2: Mandate + Archie-gated statute/pattern (before any upsert removal)

**Done when:** `docs/ASTRAL_CODE_RULES.md` §2.4.1 and related bullets describe the `entity_id` / `list_entity_latest_agent_refs` contract (not entity JSON upserts); config ENTITY_TYPES comment matches; canon statute + pattern are committed only after Archie approval with refreshed frontmatter; dual-write code from Stage 1 is still present on HEAD.

1. Draft (worktree only, may be uncommitted or on a local WIP commit that is **not** pushed as the sole tip if it includes statute without approval — prefer keep statute/pattern edits unstaged until step 4): rewrite `docs/ASTRAL_CODE_RULES.md` §2.4.1 to document RESPONSE `entity_id` + `list_entity_latest_agent_refs` as the latest-per-task contract; update §2.4 batch bullets that say “entity agent_responses”; update ENTITY_TYPES / External-layer mentions so they do not list entity-column `agent_responses` as the live upsert target. Keep the statute id citation line.
2. Update `src/utils/config.py` ENTITY_TYPES comment in the **same** product/docs commit as the Code Rules rewrite (comment-only).
3. **Archie approval gate (`orch.roles.archie-approves-statutes`) — hard stop:**
   1. Prepare the intended amend text for `canon/statutes/astral/batch/astral.batch.entity-agent-responses-latest-only.md` (Statement / Examples / title as needed for the replacement contract) and the matching `canon/patterns/batch/pattern.batch.entity-agent-responses.md` (`canonical_refs` → `list_entity_latest_agent_refs` / `_store_response_block` or `save_agent_data`; drop deleted symbols).
   2. Post a Linear comment on **AST-984** assigning **Susan** (Archie) with the draft statute/pattern delta and asking for approval. Explicit ask: keep statute id in place vs supersede with a new id.
   3. **Stop.** Do not commit `canon/statutes/**` (or proceed to Stage 3) until Susan/Archie comments approval on AST-984.
   4. On approval: commit statute + pattern with frontmatter `approved_by: Archie` and a fresh `approved_at` (ISO date of approval). If Archie directs supersede, create the new statute file, set `superseded_by` / `supersedes` links, update Code Rules statute citation, and do **not** leave the old statute active without that linkage.
4. Publish Stage 2 commit(s) to `origin/<publish-ref>`: Code Rules + config comment may land in one commit; canon files only in the post-approval commit. After this stage, the **live mandate** matches the replacement; dual-write code may still exist until Stage 3.

⚠️ **Decision:** In-place statute id rewrite vs supersede is **Archie’s call at this gate** (Joan discuss item). Default draft keeps the same id; implementer follows Archie’s reply literally.

## Stage 3: Cut readers/writers to replacement; stop entity JSON upserts

**Done when:** No core path calls `append_agent_response`; hop hydration and `get_entity_agent_story` use only `list_entity_latest_agent_refs`; `append_agent_response` deleted from data + tracker. Stage 2 mandate is already on `origin/<publish-ref>`.

**Precondition:** Stage 2 published (Code Rules rewritten; Archie-approved statute/pattern on publish-ref). If not, **stop**.

1. Confirm `entity_cost` omission: `rg -n 'entity_cost' src --glob '*.py'` — no reader of entity JSON `agent_responses[].entity_cost` outside the soon-deleted append path; ledger/dispatcher `entity_cost` columns unchanged.
2. Run ensure-time backfill function `_backfill_agent_data_entity_id_from_entity_columns(conn)` once per process (flag like other one-shot migrations): for company/job/candidate rows, parse JSON `agent_responses`, for each RESPONSE block id set `agent_data.entity_id` when empty. Invoke from **agent_data ensure** so it runs before readers rely on it.
3. Rewrite `_hop_agent_ref_for_parent` to iterate `list_entity_latest_agent_refs(entity_type, entity_id)` (pass entity type + id into the helper; stop reading `entity.get("agent_responses")`). Preserve anchor_batch_id filter and failure-prefix skip behavior.
4. Rewrite `get_entity_agent_story(entity)` to take entity type from `astral_job_id` / `short_name` / `astral_candidate_id` presence (same detection as today) and call `list_entity_latest_agent_refs`; keep scored-task RESPONSE filtering via `_filter_response_block`.
5. Delete `append_agent_response` calls in `agent.py`, `roster.py`, `consult.py`; remove imports; delete `database.append_agent_response` and `tracker.append_agent_response`.
6. Delete `dedupe_agent_responses_latest` and `normalize_agent_responses_for_backfill` from `roster.py` if unused after the rewrite; if the backfill script still imports them, retire the script in Stage 5 in the same or prior commit so imports do not break.

## Stage 4: Drop entity columns from schema

**Done when:** `PRAGMA table_info` for company, job, and candidate has no `agent_responses`; CREATE paths never add it; parse/update helpers never read/write it; header inventory no longer lists the column.

**Precondition:** Stage 2 mandate + Stage 3 reader/writer cutover are on `origin/<publish-ref>`. If not, **stop** (parent forbids silent column drop while mandate still requires entity latest-only refs — Stage 2 already moved the mandate; Stage 3 removed the last writers).

1. For each of company / job / candidate ensure paths: if column present, rebuild table excluding `agent_responses` (follow existing `job_next` / `dispatch_task_new` rebuild pattern in `database.py` — copy all columns except `agent_responses`, swap tables, restore indexes that still apply). Do **not** use this rebuild to drop unrelated columns (e.g. leave `agent_responses_legacy` on company alone unless a prior sibling already removed it — out of scope).
2. Remove `agent_responses` from CREATE TABLE column lists, ADD COLUMN migration loops, row parsers (`_parse_*`), `create_*` / `update_*` kwargs / INSERT column lists.
3. Update module header inventory bullets accordingly.
4. Verify with `rg -n "agent_responses" src/data/database.py` — remaining hits must be only historical comments about the retired **table** (if any left after AST-982) or none; zero entity-column SQL.

## Stage 5: Scripts + acceptance

**Done when:** Entity-column backfill script is retired; api docstring fixed if needed; searches below are clean for product/scripts.

1. Retire `scripts/migrations/backfill_latest_only_rubric_entity_data.py` (CLI exits with AST-984 retired message; no entity-column UPDATEs).
2. Fix `api_jobs.py` detail docstring if it still says agent_responses attached.
3. Acceptance searches:

```bash
rg -n "append_agent_response|dedupe_agent_responses_latest|normalize_agent_responses_for_backfill" src scripts --glob '*.py'
rg -n "agent_responses" src/data/database.py src/core src/ui/api src/utils/config.py --glob '*.py'
```

Expected: no append/dedupe/normalize symbols; no entity-column read/write in those trees (UI `agent_story` keys OK; frontend types unchanged). Canon + Code Rules describe the replacement only.

## Self-Assessment

**Scope:** MAJOR-CHANGE — `agent_data` schema + write path, hop/UI story readers, entity DDL drop on three tables, Code Rules + Archie-gated canon statute/pattern, script retirement.

**Conf:** Medium — replacement is concrete and fits parent “no new audit table” boundary; Stage 2 now hard-gates Archie on statute id vs supersede; historical RESPONSE rows without backfillable block ids will lack hop/story until re-run.

**Risk:** HIGH — wrong cutover breaks run_next hop token hydration and job/company agent_story; mitigated by Stage 1 dual-write held through Stage 2 mandate, ensure-time backfill before drop, and preserving failure-prefix / anchor_batch_id behavior.

## Code Rules check

- §2.4.1 / statute: this ticket **revises** them in **Stage 2 before** removing upserts or dropping columns (parent boundary + `astral.batch.entity-agent-responses-latest-only` / `orch.roles.archie-approves-statutes`).
- §2.4 batch / agent_data: durable blocks unchanged; only adds `entity_id` for lookup (parent allows “whatever the replacement lookup needs”).
- §1.3 DRY: one list API for hop + story; do not keep parallel JSON upsert after Stage 3.
- §3.3 imports: remove dead `append_agent_response` imports with call sites in Stage 3.
- Layers: data owns schema/API; core owns hop/story; ui docstring only; no external-layer persistence.
- AST-974: not implemented here (no self-ref key).

## Revisions

### Revision 1 — 2026-07-25

Driven by: Joan `[plan-discuss] round=1 concern` fix-now (1) Stages 2→3→4 order violated live statute / parent “no silent drop while mandate still requires columns”; (2) Stage 4 amended `canon/statutes/**` without Archie approval / `approved_at` refresh (`orch.roles.archie-approves-statutes`).

Changes:

- Reordered cutover: Stage 1 dual-write plumbing → **Stage 2 mandate + Archie-gated statute/pattern** → Stage 3 remove upserts/cut readers → Stage 4 drop columns → Stage 5 scripts/acceptance.
- Added hard rule at top: no publishable HEAD may remove entity upserts or drop columns before mandate cutover.
- Added explicit Archie gate: draft → assign Susan → stop → commit statute/pattern only with refreshed `approved_by` / `approved_at` (id vs supersede = Archie).
- Added `entity_cost` non-UI consumer check before reader cutover (Joan discuss).
- Updated Self-Assessment / Code Rules check to match the new stage order.

## Review (build stub)

**Built:** `origin/sub/AST-975/AST-984-retire-entity-agent-responses-columns` @ `03c5361`.

**Stages delivered:**
- Stage 1: `agent_data.entity_id` + `list_entity_latest_agent_refs` + RESPONSE tagging (dual-write) — `29cc49b`.
- Stage 2: Code Rules §2.4.1 + ENTITY_TYPES; Archie-waived statute/pattern amend (`approved_at: 2026-07-27`) — `ff7f9f7` / `3745d22`.
- Stage 3–5: hop/story → list API; batch entity_id tagging; drop entity JSON columns; retire backfill script — `03c5361`.

**Betty:** broad fallout expected — `test_agent.py` append mocks, roster story/dedupe, database append tests, backfill script tests; cover `list_entity_latest_agent_refs` / `entity_id`.


## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-984
**Publish ref tip (pre-docs):** `6ec4f3698f74e4c7768d4747f2eb4f907ec2ea40`
**Overall:** DISCUSS

### What’s solid

- Staged cutover honored: `29cc49b` dual-write → `ff7f9f7` Code Rules → `3745d22` statute/pattern → `03c5361` remove append + drop entity JSON columns + retire backfill script.
- Replacement contract delivered: `agent_data.entity_id` on RESPONSE writes; `list_entity_latest_agent_refs` for hop + `get_entity_agent_story`; `ensure_batch_response_entity_ids` for batch consult/roster paths.
- Acceptance clean: no `append_agent_response` / dedupe / normalize symbols in `src/`/`scripts/`; entity columns dropped via `_drop_entity_agent_responses_column`.
- Betty: one `merge-tests(AST-984)` of `17695ac6`; broad test/bible revision; engineer avoided test-tree.

### Issues

**discuss:** `orch.roles.archie-approves-statutes` — Ada posted Archie gate @ `ff7f9f7` (2026-07-25); statute/pattern committed `3745d22` with `approved_at: 2026-07-27` but no Susan/Archie approval reply visible in AST-984 thread before Stages 3–5. Substance matches draft; resolve-child should link approval artifact or Susan confirms waiver.

**discuss (C4 straggler):** Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.ui.frontend-file-placement`; three-dot scores in-scope (plan docs, Betty tests). Substance **conforms**.

**advisory:** `entity_cost` still computed in batch `agent_ref` dict for consult tagging but omitted from `list_entity_latest_agent_refs` refs per plan — OK for UI; document if any future consumer expects it on list output.

### Recommended actions

1. Link Archie approval (or confirm waiver) in Linear before resolve-child closes discuss on statute gate.
2. Acknowledge C4 straggler rows (no code).

### Pattern conformance

none cited (pattern amended in canon commit `3745d22`)

### Plan adherence

Matches MAJOR-CHANGE scope, replacement lookup header, and hard cutover rule. Parent AC5 satisfied: columns gone, mandate/statute updated, hop/story preserved via list API.

## Resolution

**Date:** 2026-07-28  
**Review tip:** `a9d16cc` (`docs(AST-984): Radia review — findings`)  
**Outcome:** DISCUSS → acknowledged; no fix-now; advancing to User Testing.

### Discuss — Archie statute gate (`orch.roles.archie-approves-statutes`) — acknowledged via parent waiver

Radia flagged that statute/pattern landed @ `3745d22` (`approved_at: 2026-07-27`) without an Archie approval reply on AST-984 before Stages 3–5.

Susan waived the gate on **parent AST-975** (2026-07-27): *"This ticket will be outside the scope of the statutes. Please use best judgment."* — [AST-975 comment](https://linear.app/astralcareermatch/issue/AST-975/decommission-table-agent-responses#comment-cafbb55c-8dc7-4d44-9277-b203072cbb3d).

Chuckles recorded the unblock: `[check-linear] In Progress — statute gate waived; best judgment on entity-column / hard-drop path` — [AST-975 comment](https://linear.app/astralcareermatch/issue/AST-975/decommission-table-agent-responses#comment-4519d7f1-2ad2-42fe-94f1-0f0c299f2797).

Implementer kept statute id `astral.batch.entity-agent-responses-latest-only` in place per draft default; substance matches the replacement contract. No product change for this discuss row.

### Discuss (C4 straggler) — acknowledged

Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.ui.frontend-file-placement` at plan time; code-rubric three-dot sweep scored them in-scope (plan docs + Betty tests). Substance **conforms** for all four — no code change.

### Advisory — acknowledged

`entity_cost` remains on batch `agent_ref` for consult/roster tagging but is omitted from `list_entity_latest_agent_refs` output per plan (UI does not require it). No change.

