<!-- linear-archive: AST-1140 archived 2026-08-11 -->

## Linear archive (AST-1140)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1140/selected-ids-gaze-email-ingest-entrypoint-manage-email-select-inbox  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1129 — Manage Email — select inbox messages and Land Meteorite  
**Blocked by / blocks / related:** parent: AST-1129; blocks: AST-1141

### Description

## What this implements

Owns wiring Land Meteorite to the shared AST-1128 core callable that ingests an explicit list of Astral inbox message ids through the same bind / route / scrape / dedupe / create / mailbox outcomes as dispatcher `gaze_email` — including skip behavior for unbound/unmatched ids. Does **not** stamp `last_email_check`. Style D debug on the touched path. Does **not** own admin HTTP or Manage Email React (siblings #2/#3). After AST-1128.

## Acceptance criteria

- [X] 3. Clicking **Land Meteorite** processes **only** the selected message ids through the shared `gaze_email` ingest path from AST-1128 (bind / route / scrape / dedupe / **METEORITE_NEW** / archive-or-ignore as established for that path).
- [X] 4. Land Meteorite does **not** call the retired Create strip/extract create-job path for those messages.
- [X] 5. Unbound / unmatched selected messages are skipped with explicit feedback; bound selected messages in the same batch still process.
- [X] 6. A single Land Meteorite action does not advance jobs into qualify/GDL and does not update `candidate.last_email_check`.
- [X] 7. With `debug=True`, each selected message and each create/skip/archive/ignore outcome is visible in Style D (found + recorded); with `debug=False`, no new debug noise from this path.

## Boundaries

Does **not** own admin HTTP or Manage Email React (siblings #2/#3). Does **not** stamp `last_email_check`. Does **not** build a throwaway interim adapter on the null-candidate shell.

## In scope

- [X] `pattern.layers.import-discipline` — Gmail list/get/archive stays external; core owns selected-ids orchestration + bind/route/dedupe
- [X] `pattern.state.entity-state-transitions` — ingest stops at **METEORITE_NEW**; no qualify/GDL hop
- [X] `pattern.config.config-block` — extend `GAZE_EMAIL_CONFIG` for selected-ids Style D + skip outcome vocabulary (no parallel Land-Meteorite block)
- [X] `astral.state.no-daisy-chain-in-run` — single Land Meteorite action does not advance into qualify/GDL
- [X] `astral.standards.debug-contract-gated` — Style D only when `debug=True` on `run_gaze_email_selected_ids`
- [X] `astral.standards.in-scope-only` — selected-ids core entrypoint only; no admin HTTP / React

## Considered but excluded

- [X] Admin Land Meteorite HTTP + outcome payload surface — AST-1141 (`src/ui/api/`)
- [X] Manage Email multi-select + Land Meteorite React + Create retirement — AST-1142 (`src/ui/frontend/`)
- [X] Candidate-bound dispatcher runner rewrite / unbound Trash hygiene / `last_email_check` stamp call site — AST-1136 (`src/core/gaze_email.py` dispatch path)
- [X] Null-shell retirement / every-candidate provision / carve-out — AST-1134
- [X] Live bind-filtered Avail count — AST-1135
- [X] Wrapping `run_gaze_email(task)` as a fake null-shell adapter — forbidden by Boundaries
- [X] `tests/` / bible — Betty

## Notes for planning

Coordinate with AST-1128 callable selected-ids / candidate-bound core entrypoint. No interim fork. Soft merge gate: `origin/ftr/AST-1128-gaze-email-candidate-bound-dispatch-redesign` before Stage 2 build.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1129-manage-email-select-inbox-messages-and-land-meteorite`, child `sub/AST-1129/AST-1140-selected-ids-gaze-email-ingest-entrypoint`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-08-02T21:29:41.470Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

Offending commit on `origin/sub/AST-1129/AST-1140-selected-ids-gaze-email-ingest-entrypoint`: `a231f974` — `Merge remote-tracking branch 'origin/ftr/AST-1128-gaze-email-candidate-bound-dispatch-redesign' into sub/…`.

@Ada Lovelace — rebuild/republish the sub tip so history has no `Merge remote-tracking branch` subjects (merge `origin/ftr/AST-1129-manage-email-select-inbox-messages-and-land-meteorite` / `origin/dev` with proper `merge(AST-1140): …` subjects). Then Chuckles retries merge-child.

— Chuckles

#### chuckles — 2026-08-02T21:29:17.551Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

`validate-sub-log` failed on `origin/sub/AST-1129/AST-1140-selected-ids-gaze-email-ingest-entrypoint` because of:
`a231f974 Merge remote-tracking branch 'origin/ftr/AST-1128-gaze-email-candidate-bound-dispatch-redesign' into sub/AST-1129/AST-1140-…` (Stage 2a soft-merge).

@Ada Lovelace — rewrite/republish the sub tip without a `Merge remote-tracking branch` commit (merge `origin/ftr/AST-1129-…` / `origin/dev` with `merge(AST-1140): …` vocabulary only), then Chuckles will re-run merge-child.

— Chuckles

#### betty — 2026-08-02T21:27:25.353Z
[check-linear] Cleared [qa-handoff] return pass.

- Synced `tests/component/core/test_gaze_email.py` + `docs/test-bible/core/gaze_email.md` to combined AST-1090/1136/1140 surface (from `origin/tests` @ `5bae04d2`)
- AST-1136 `_handle_bound` mocks → 5-tuple `(processed, passed, failed, errors, outcome)`
- Publish tip: `origin/sub/AST-1129/AST-1140-selected-ids-gaze-email-ingest-entrypoint` @ `addec765` (`test(AST-1140): return — AST-1136+1140 gaze_email tree + 5-tuple mocks`)
- Bible sha: `docs/test-bible/core/gaze_email.md` `24966c82fd0f60858047f9cef97b51d46475b568`
- Stayed **Review Posted**; assignee → Ada for resolve resume

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gaze_email.py::TestAst1140RunGazeEmailSelectedIds \
  tests/component/utils/test_config.py::TestAst1140GazeEmailSelectedConfig \
  tests/component/core/test_gaze_email.py::TestAst1090RunGazeEmail \
  tests/component/core/test_gaze_email.py::TestAst1136CandidateBoundGazeEmail \
  -q
```

— Betty

#### betty — 2026-08-02T21:27:06.749Z
[check-linear] Cleared [qa-handoff]: AST-1136 + AST-1140 gaze_email tests/bible on tip; `_handle_bound` mocks are 5-tuple `(processed, passed, failed, errors, outcome)`. Publish tip `origin/sub/AST-1129/AST-1140-selected-ids-gaze-email-ingest-entrypoint` @ `addec765` (`test(AST-1140): return — AST-1136+1140 gaze_email tree + 5-tuple mocks`). Stay **Review Posted** — Ada finishes resolve → User Testing.

— Betty

#### ada — 2026-08-02T21:23:28.410Z
[qa-handoff]
@Betty White — resolve-child merged `origin/dev` (AST-1128/AST-1136 landed). Product tip keeps AST-1140 `run_gaze_email_selected_ids` + `_handle_bound` 5-tuple/`index_dbg`, and now also has AST-1136 `run_gaze_email` (requires `candidate_id`, stamps `last_email_check`) + `process_gaze_email_messages`.

Engineer hook blocked test-tree on the merge commit, so this sub still has the older Betty AST-1140 tip for:
- `tests/component/core/test_gaze_email.py`
- `docs/test-bible/core/gaze_email.md`

`origin/dev` already has the combined AST-1090 (candidate_id) + AST-1136 + AST-1140 coverage. Please `merge-tests` that surface onto `origin/sub/AST-1129/AST-1140-selected-ids-gaze-email-ingest-entrypoint` and adapt any `_handle_bound` mocks to the 5-tuple `(processed, passed, failed, errors, outcome)`.

**Publish tip after resolve (product+plan):** `b3799cb85152c17cae600eb50c5041a6266c400b`
**Stay Review Posted** — Ada resumes after you republish + reassign.

— Ada

#### radia — 2026-08-02T21:20:13.783Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1140
**Publish ref:** `53a66550f5e66bfd1d81de35f41425e294a454b0` (`origin/sub/AST-1129/AST-1140-selected-ids-gaze-email-ingest-entrypoint`)
**Overall:** DISCUSS

Diff: `origin/dev...origin/sub/AST-1129/AST-1140-selected-ids-gaze-email-ingest-entrypoint` (multiple merge bases; git used `1665ec70`). Active statutes enumerated: **65**.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | no graded confidence path |
| `astral.agent.do-task-delegation` | scoped | conforms | Ruth stays in shared `_handle_bound`/`do_task` |
| `astral.agent.grade-vector-validation` | scoped | conforms | no grade-vector path |
| `astral.batch.batch-id-first` | scoped | conforms | selected-ids not a claim_batch path |
| `astral.batch.batch-id-format` | scoped | conforms | no new batch_id minting |
| `astral.batch.claim-process-release` | scoped | conforms | no claim/release rewrite on selected-ids |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | no agent_data latest-ref changes |
| `astral.config.config-source-of-truth` | scoped | conforms | extends `GAZE_EMAIL_CONFIG`; no parallel Land-Meteorite block |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | no scoring/floor changes |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | no new secrets; Gmail stays environ |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths `['artifacts/**', 'scripts/spikes/**']` miss |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | feature plans under `docs/features`; no spike notes committed |
| `astral.dispatch.run-next-is-chain-authority` | scoped | conforms | selected-ids forbids qualify/GDL hop chaining |
| `astral.dispatch.seed-auto-false` | scoped | conforms | `auto_mode` remains False; seed law untouched by 1140 |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | AST-1140 plan at `docs/features/meteorite/ast-1140-…md` |
| `astral.git.betty-no-src-or-features` | scoped | conforms | engineer owns src/features on this tip |
| `astral.git.engineer-test-tree-ban` | scoped | not-applicable | paths `tests/**` / bible / `scripts/test_*` miss |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | mailbox I/O via inbox/gmail; core owns selected-ids |
| `astral.layers.import-direction` | scoped | conforms | core→inbox/gmail/config/logging; no UI imports in `gaze_email` |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers `['scripts']` miss; paths `['scripts/**']` miss |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | config vocabulary for sibling API; no React rules |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | no coat-check changes |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | no consult/render_verdict changes |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | conforms | `list_dtasks` remains `@require_admin` |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | no agent JSON seed edits |
| `astral.seed.archie-catalog-wins` | scoped | conforms | no agent catalog seed edits |
| `astral.seed.boot-only-not-hot-path` | scoped | conforms | selected-ids hot path; no seed pulled into request |
| `astral.seed.define-approved` | scoped | conforms | no define-approved seed surface edits |
| `astral.seed.operator-rows-stay-deleted` | scoped | conforms | no operator-row resurrection |
| `astral.seed.other-via-coverage-join` | scoped | conforms | no coverage-join seed changes |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | data stamp helper raises; selected-ids never calls it |
| `astral.standards.database-header-inventory` | scoped | conforms | candidate/dispatch_task inventory updated with `last_email_check` + cid required |
| `astral.standards.debug-contract-gated` | scoped | conforms | Style D via `_dbg_selected`/`debug_func_selected` only when `debug=True` |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | shares `_handle_bound`; no `run_gaze_email` wrapper fork |
| `astral.standards.in-scope-only` | scoped | conforms | 1140 `code()` = `gaze_email`+`config`; sibling tip surface from Stage 2a soft merge |
| `astral.standards.logging-via-utils` | scoped | conforms | uses utils `get_logger` / `debug_*` helpers |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | `run_gaze_email_selected_ids` + product config keys |
| `astral.standards.no-cross-contamination` | scoped | conforms | 1140 stays on gaze_email/config; no UI Land Meteorite smuggle |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | skip/debug-func strings in `GAZE_EMAIL_CONFIG` |
| `astral.standards.public-then-helpers` | scoped | conforms | selected-ids grouped with public `run_gaze_email`; helpers remain above per existing AST-1090 layout |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | `config.py` has no data import |
| `astral.state.core-decides-transitions` | scoped | conforms | `create_meteorite_job` remains core decision path |
| `astral.state.job-prior-states-enforced` | scoped | conforms | no `JOB_STATES` / prior-state bypass |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | stops at **METEORITE_NEW**; no qualify/GDL |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | paths `['src/ui/frontend/**']` miss |
| `astral.ui.naming-conventions` | scoped | conforms | API route/handler snake_case unchanged |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | config touch; no gunicorn/worker settings |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | merge-tests SHA present on tip history |
| `orch.git.commit-vocabulary` | universal | conforms | `code()`/`docs()`/`merge-tests()` vocabulary used |
| `orch.git.flow-direction-inviolable` | universal | conforms | publish on `origin/sub/AST-1129/AST-1140-…` |
| `orch.git.ftr-sub-topology` | universal | conforms | child sub under parent AST-1129 |
| `orch.git.merge-on-checkout` | universal | conforms | Stage 2a merged `ftr/AST-1128`; later `origin/dev` merge |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | no cherry-pick/rebase/force on tip |
| `orch.git.no-dev-agent-branches` | universal | conforms | uses `sub/AST-1129/AST-1140-…` only |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | review in `astral-AST-1129` |
| `orch.git.three-permanent-branches` | universal | conforms | no new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | no new product ambiguity in selected-ids path |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–3 match tip; forbidden call sites absent |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Meteorite child only |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | no statute corpus edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | no tests/bible edits by engineer on 1140 code |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee Ada through Tests Passed |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Ada remains assignee |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no banned-path product edits by Radia |

## Pattern conformance

| pattern id (from ticket In scope) | verdict |
|-----------------------------------|---------|
| `pattern.layers.import-discipline` | conforms — Gmail list/get/archive stays external/inbox; core owns selected-ids orchestration |
| `pattern.state.entity-state-transitions` | conforms — ingest stops at **METEORITE_NEW** via `create_meteorite_job` |
| `pattern.config.config-block` | conforms — extend `GAZE_EMAIL_CONFIG` only |
| `astral.state.no-daisy-chain-in-run` | conforms — covered in statutes table |
| `astral.standards.debug-contract-gated` | conforms — covered in statutes table |
| `astral.standards.in-scope-only` | conforms — covered in statutes table |

## Plan adherence

Stages 1–3 match tip: config keys + asserts; public `run_gaze_email_selected_ids` with list-once index, skip outcomes, shared `_handle_bound(..., index_dbg=_dbg_selected)`, return aggregates; no Create strip/extract, no `last_email_check` stamp, no unbound Trash on Land Meteorite. Self-Assessment Scope `Single-Component` matches the AST-1140 `code()` footprint (`gaze_email.py` + `config.py`). Stage 2a soft-merge of `ftr/AST-1128` correctly pulled sibling AST-1134/1135 surface onto the tip (expected); AST-1136’s later `process_gaze_email_messages` is **not** an ancestor of this tip, so Ada’s named Land Meteorite entrypoint is the planned reuse path.

## Findings

**fix-now:** none.

**discuss (C4 straggler — excluded at plan time but in-scope on diff):**
1. `astral.debug.spikes-under-debug-dir` — soft-merge added `docs/features/**` (scored conforms).
2. `astral.docs.features-single-file-per-ticket` — same (scored conforms).
3. `astral.patterns.require-auth-on-protected-endpoints` — tip includes `src/ui/api/api_admin.py` Avail stamp (scored conforms; `@require_admin` retained).
4. `astral.standards.database-header-inventory` — tip includes `src/data/database.py` (scored conforms; header updated).
5. `astral.ui.naming-conventions` — tip includes `src/ui/**` (scored conforms).

No product rewrite required for these; they fire because Stage 2a soft-merge widened the three-dot change set beyond Joan’s plan-only Files Changed.

**advisory:** Tip carries AST-1134/1135 dispatcher/avail/database surface while dispatcher `run_gaze_email` on this tip remains AST-1090 null-shell shape. Land Meteorite `run_gaze_email_selected_ids` is isolated and correct; candidate-bound runner coherence stays with AST-1128 / AST-1136 rollup.

## What’s solid

- Skip vocabulary + Style D func in `GAZE_EMAIL_CONFIG`.
- Per-id found→recorded Style D; `debug=False` silent on new contract lines.
- Shared bound ingest via injectable `index_dbg` (dispatcher keeps `_dbg`; selected uses `_dbg_selected`).

## Notes

Joan plan-rubric verdict attached (APPROVED). C4 stragglers listed above.

context_tokens≈52000

#### betty — 2026-08-02T20:50:46.657Z
1. **Existing / new coverage**
   - `tests/component/core/test_gaze_email.py::TestAst1140RunGazeEmailSelectedIds` — selected-ids skips (missing / unbound / unmatched), bound create+archive, non-selected ignored, no Trash/stamp/Create-strip, Style D `debug_func_selected` gate
   - `tests/component/utils/test_config.py::TestAst1140GazeEmailSelectedConfig` — `GAZE_EMAIL_CONFIG` selected-ids vocabulary
   - `tests/component/core/test_gaze_email.py::TestAst1090RunGazeEmail` — dispatcher mailbox regression after `_handle_bound` 5-tuple outcome

2. **Broken / obsolete:** none — additive entrypoint; dispatcher unpack ignores the new outcome string.

3. **Gaps closed this pass:** selected-ids entrypoint + config (above).

**§6c:** N/A — no UI/page changes (admin/React = AST-1141 / AST-1142).

**Run:**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_gaze_email.py::TestAst1140RunGazeEmailSelectedIds \
  tests/component/utils/test_config.py::TestAst1140GazeEmailSelectedConfig \
  tests/component/core/test_gaze_email.py::TestAst1090RunGazeEmail \
  -q
```

**Publish:** `origin/sub/AST-1129/AST-1140-selected-ids-gaze-email-ingest-entrypoint` @ `7584dfb8` (`merge-tests(AST-1140): origin/tests a986cf484b7680c1d8a077521ba4eaa01c18bc7e`)

**Bible shasums on publish tip:**
- `docs/test-bible/core/gaze_email.md` `b8f28e96cd813194ec27146c117ab0fad4466efa`
- `docs/test-bible/utils/config.md` `a8e5e8020879d6eae174b7fda85c821d70d1cfb4`

— Betty

#### joan — 2026-08-02T20:43:49.873Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1140
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 multi-select Manage Email | N/A — boundary (AST-1142) |
| AC2 Land Meteorite availability | N/A — boundary (AST-1142) |
| AC3 selected-ids shared gaze_email ingest | Stages 2a–2c `run_gaze_email_selected_ids` + shared `_handle_bound` |
| AC4 not Create strip/extract path | Stage 2c forbidden `create_meteorite_job_from_inbox_message` |
| AC5 unbound/unmatched skipped; bound still process | Stage 2c skip outcomes + continue; bound → `_handle_bound` |
| AC6 operator-visible batch outcome on Manage Email | N/A — boundary (AST-1141/1142); this child returns `results[]` payload for them |
| AC7 no qualify/GDL; no `last_email_check` stamp | Stage 2c forbids hop chaining + `update_candidate_last_email_check` |
| AC8 retire per-row Create | N/A — boundary (AST-1142) |
| AC9 Style D debug when `debug=True` | Stages 1 + 2c `_dbg_selected` / `debug_func_selected` |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 GAZE_EMAIL_CONFIG extend | Architectural `pattern.config.config-block`; child in-scope config; AC9 debug func |
| Stage 2 selected-ids entrypoint | Functional scope §3 selected-ids ingest; Purpose Land Meteorite shared path; child AC3–7 |
| Stage 3 import smoke + boundary lock | Boundaries / in-scope-only verification |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| astral.agent.confidence-bounds | conforms | No graded confidence path touched |
| astral.agent.do-task-delegation | conforms | Ruth parse stays inside shared _handle_bound/do_task path; no new persona |
| astral.agent.grade-vector-validation | conforms | No grade vector path touched |
| astral.batch.batch-id-first | conforms | No new claim_* signature changes |
| astral.batch.batch-id-format | conforms | No new batch_id minting in selected-ids entrypoint |
| astral.batch.claim-process-release | conforms | Selected-ids is not entity claim-batch dispatch; no claim/release rewrite |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data latest-ref rewrite |
| astral.config.config-source-of-truth | conforms | Extends GAZE_EMAIL_CONFIG; no parallel Land-Meteorite block |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring/dispatch floor changes |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env values introduced; Gmail stays environ via existing external |
| astral.dispatch.run-next-is-chain-authority | conforms | Forbids qualify hop chaining; no parallel hop lists |
| astral.dispatch.seed-auto-false | conforms | Does not flip GAZE_EMAIL_CONFIG auto_mode; keeps existing CLICK seed law |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src/features; Betty excluded |
| astral.layers.core-vs-external-bright-line | conforms | Mailbox I/O via existing external/inbox helpers; core owns selected-ids orchestration |
| astral.layers.import-direction | conforms | core→inbox/gmail/config/logging; utils pure; no UI imports |
| astral.layers.ui-config-driven-business-logic | conforms | Config vocabulary for sibling API; no React business rules here |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check key changes |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult/render_verdict changes |
| astral.seed.agent-tables-in-repo-json | conforms | No agent JSON seed edits |
| astral.seed.archie-catalog-wins | conforms | No agent catalog seed edits |
| astral.seed.boot-only-not-hot-path | conforms | Selected-ids is hot path; does not move seed into request path |
| astral.seed.define-approved | conforms | No seed catalog / define-approved surface edits |
| astral.seed.operator-rows-stay-deleted | conforms | No operator-row resurrection |
| astral.seed.other-via-coverage-join | conforms | No seed coverage-join changes |
| astral.standards.data-raises-caller-logs | conforms | No data-layer authorship |
| astral.standards.debug-contract-gated | conforms | Style D via debug_func_selected / _dbg_selected only when debug=True |
| astral.standards.dry-and-focused-functions | conforms | Share _handle_bound; forbid forked pipeline / run_gaze_email wrapper |
| astral.standards.in-scope-only | conforms | Only config.py + gaze_email.py; admin/React/Create retirement excluded |
| astral.standards.logging-via-utils | conforms | Uses utils logging Style D helpers |
| astral.standards.names-not-ticket-ids | conforms | Public symbol run_gaze_email_selected_ids; config keys product-named |
| astral.standards.no-cross-contamination | conforms | Stays in core/utils gaze_email surface |
| astral.standards.no-hardcoded-sets | conforms | New skip/debug-func strings in GAZE_EMAIL_CONFIG; bound outcomes reuse AST-1090 helper vocabulary |
| astral.standards.public-then-helpers | conforms | Public run_gaze_email_selected_ids above helpers |
| astral.standards.utils-data-late-import-only | conforms | No utils→data changes |
| astral.state.core-decides-transitions | conforms | Create helper remains core decision path; no data deciding next state |
| astral.state.job-prior-states-enforced | conforms | No new JOB_STATES / transition bypass |
| astral.state.no-daisy-chain-in-run | conforms | Stops at METEORITE_NEW via existing create; forbids qualify/GDL |
| astral.ui.single-gunicorn-worker | conforms | Touches config.py but no gunicorn/worker settings |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work in this core/config plan |
| orch.git.commit-vocabulary | conforms | Publish on sub via plan()/code() vocabulary; no illegal verbs |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/…; Stage 2a merges ftr→sub correctly |
| orch.git.ftr-sub-topology | conforms | Child publish ref matches parent Git table |
| orch.git.merge-on-checkout | conforms | Merge-on-checkout / ftr merge gate stated; no cherry-pick recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick/rebase/force proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1129/AST-1140-… only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1129 assumed |
| orch.git.three-permanent-branches | conforms | Does not invent permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions documented; soft AST-1128 gate is build procedure not product ambiguity |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed + forbidden call sites present |
| orch.pipeline.project-scoped-queues | conforms | Single-child Meteorite scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan gate only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | Explicitly no tests/bible edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Ada) owns build; Chuckles orchestration only |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer path after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | No banned-path edits proposed |

## Considered and excluded

**Considered:** astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.dispatch.run-next-is-chain-authority, astral.dispatch.seed-auto-false, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.seed.agent-tables-in-repo-json, astral.seed.archie-catalog-wins, astral.seed.boot-only-not-hot-path, astral.seed.define-approved, astral.seed.operator-rows-stay-deleted, astral.seed.other-via-coverage-join, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.names-not-ticket-ids, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker, orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths ['artifacts/**', 'scripts/spikes/**'] match none of plan paths
- astral.debug.spikes-under-debug-dir — paths ['debug/**', 'docs/features/**', 'scripts/spikes/**'] match none of plan paths
- astral.docs.features-single-file-per-ticket — layers ['docs'] ∩ plan ['core', 'utils'] empty
- astral.git.engineer-test-tree-ban — paths ['tests/**', 'docs/test-bible/**', 'docs/ASTRAL_TEST_BIBLE.md', 'scripts/test_*.py', 'scripts/testing/**'] match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers ['scripts'] ∩ plan ['core', 'utils'] empty
- astral.patterns.require-auth-on-protected-endpoints — layers ['ui'] ∩ plan ['core', 'utils'] empty
- astral.standards.database-header-inventory — layers ['data'] ∩ plan ['core', 'utils'] empty
- astral.ui.frontend-file-placement — layers ['ui'] ∩ plan ['core', 'utils'] empty
- astral.ui.naming-conventions — layers ['ui'] ∩ plan ['core', 'utils'] empty

## Findings

None fix-now.

**discuss (non-blocking):** Stage 2c maps bound success/fail outcomes partly as prose (`archived` / `ignored` / `error` / `failed`) while new skip strings live in `GAZE_EMAIL_CONFIG`. Acceptable because bound outcomes reuse AST-1090 Style D helper vocabulary; if AST-1141 needs a closed selected-ids outcome enum, Ada can add matching config keys in build without rewriting the ingest path.

**acceptable:** Self-assessment Scope Single-Component / Conf Medium / Risk Medium matches the AST-1128 merge/reuse uncertainty and the forbidden-call-site risk list.

**R6 checklist:** Definition fidelity pass for child #1 only. Layer/import pass. Config extend-not-fork pass. File placement N/A (existing modules). No batch claim rewrite. Debug gated. DRY via shared `_handle_bound`. No admin/React/Create-retirement scope creep.

context_tokens≈48000

— Joan

#### ada — 2026-08-02T20:40:18.458Z
Plan: [`docs/features/meteorite/ast-1140-selected-ids-gaze-email-ingest-entrypoint.md`](https://github.com/susansomerset/astral/blob/sub/AST-1129/AST-1140-selected-ids-gaze-email-ingest-entrypoint/docs/features/meteorite/ast-1140-selected-ids-gaze-email-ingest-entrypoint.md) @ `origin/sub/AST-1129/AST-1140-selected-ids-gaze-email-ingest-entrypoint` (`d75d634f`).

- **Scope:** Single-Component — `GAZE_EMAIL_CONFIG` selected-ids literals + `run_gaze_email_selected_ids` sharing bound ingest; no UI/admin.
- **Conf:** Medium — AST-1090 `_handle_bound` is reusable; Stage 2a merges `ftr/AST-1128` and reuses AST-1136’s callable if present so we do not fork ingest.
- **Risk:** Medium — wrong wiring could hit Create strip/extract, stamp `last_email_check`, or process non-selected mail; plan forbids those call sites.

— Ada

---

# AST-1140 — Selected-ids gaze_email ingest entrypoint

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1140/selected-ids-gaze-email-ingest-entrypoint-manage-email-select-inbox  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1129/manage-email-select-inbox-messages-and-land-meteorite  

**Publish ref (origin):** `sub/AST-1129/AST-1140-selected-ids-gaze-email-ingest-entrypoint`  
**Parent integration ref:** `ftr/AST-1129-manage-email-select-inbox-messages-and-land-meteorite`

Core Land Meteorite entrypoint: ingest an **explicit list** of Astral inbox message ids through the **same** bind / shape-route / Ruth parse / scrape / per-candidate dedupe / **METEORITE_NEW** create / archive-or-ignore path used by dispatcher `gaze_email` (AST-1090 helpers today; AST-1136 candidate-bound runner when rolled). Unbound / unmatched / missing-from-inbox selected ids are **skipped** with explicit per-id outcomes; bound siblings in the same batch still process. Does **not** stamp `candidate.last_email_check`. Does **not** call the retired Manage Email Create strip/extract path (`create_meteorite_job_from_inbox_message`). Style D when `debug=True`. Does **not** own admin HTTP (AST-1141) or Manage Email React (AST-1142).

**Depends on (soft merge gate at build):** AST-1128 child work that owns shared per-message ingest — especially AST-1136 (“leaves a callable core path AST-1129 can reuse”). Before Stage 2, `git fetch origin` and merge `origin/ftr/AST-1128-gaze-email-candidate-bound-dispatch-redesign` into this sub when that tip has advanced past the current null-shell runner; if AST-1136 already exported a public selected-ids / shared ingest symbol, **call that** instead of inventing a second pipeline. Do **not** wrap `run_gaze_email(task)` as a fake null-shell adapter.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `GAZE_EMAIL_CONFIG` with selected-ids Style D func name + skip/outcome string vocabulary | utils |
| `src/core/gaze_email.py` | Public `run_gaze_email_selected_ids`; share bound-message ingest with dispatcher path; Style D; no `last_email_check` stamp | core |

No `src/ui/**`, no React, no `src/core/inbox.py` Create path edits, no `src/core/dispatcher.py`, no `src/data/database.py` stamp calls, no `tests/` / bible.

---

## Stage 1: Config — selected-ids debug + outcome vocabulary

**Done when:** `GAZE_EMAIL_CONFIG` exposes the keys below; no runner behavior change yet.

1. In `src/utils/config.py`, extend the existing `GAZE_EMAIL_CONFIG` dict (do **not** invent a parallel Land-Meteorite config block) with:

```python
    # AST-1140 — Style D func= for selected-ids Land Meteorite ingest.
    "debug_func_selected": "gaze_email.selected_ids",
    # Per-id outcome strings returned to AST-1141 / recorded in Style D.
    "selected_outcome_skipped_unbound": "skipped-unbound",
    "selected_outcome_skipped_not_in_inbox": "skipped-not-in-inbox",
    "selected_outcome_skipped_unmatched": "skipped-unmatched",
```

Keep every existing key unchanged (`task_key`, `account_address`, `unbound_retention_days`, runner schemes, `debug_func`, etc.).

2. Asserts next to the existing `GAZE_EMAIL_CONFIG` asserts:

```python
assert GAZE_EMAIL_CONFIG["debug_func_selected"] == "gaze_email.selected_ids"
assert GAZE_EMAIL_CONFIG["selected_outcome_skipped_unbound"] == "skipped-unbound"
assert GAZE_EMAIL_CONFIG["selected_outcome_skipped_not_in_inbox"] == "skipped-not-in-inbox"
assert GAZE_EMAIL_CONFIG["selected_outcome_skipped_unmatched"] == "skipped-unmatched"
```

3. Update the inventory comment line for `GAZE_EMAIL_CONFIG` to mention selected-ids Land Meteorite literals (AST-1140).

⚠️ **Decision — extend `GAZE_EMAIL_CONFIG`, not a new block:** Parent Architectural definition forbids inventing parallel Land-Meteorite config for the same ingest behavior. Skip/outcome strings are product vocabulary for the admin batch payload (sibling AST-1141) and belong beside the task key.

**Done when (recheck):** `python3 -c "from src.utils.config import GAZE_EMAIL_CONFIG; assert GAZE_EMAIL_CONFIG['debug_func_selected']"` succeeds; `python3 -m py_compile src/utils/config.py` succeeds.

---

## Stage 2: Shared bound ingest + `run_gaze_email_selected_ids`

**Done when:** `from src.core.gaze_email import run_gaze_email_selected_ids` works; calling it with message ids processes **only** those ids through bind→route→Ruth/scrape/dedupe/create/archive; unbound/missing ids return explicit skip outcomes; `update_candidate_last_email_check` is never called; `create_meteorite_job_from_inbox_message` is never called; Style D emits only when `debug=True`.

### 2a. Pre-build merge / reuse gate (mandatory before editing the runner)

1. `git fetch origin`.
2. Merge `origin/ftr/AST-1128-gaze-email-candidate-bound-dispatch-redesign` into this sub (resolve conflicts; prefer AST-1128’s candidate-bound runner shape when both touch `gaze_email.py`).
3. Inspect `src/core/gaze_email.py` on the merged tip:
   - If a public selected-ids or shared per-message ingest already exists (names may vary — e.g. `run_gaze_email_selected_ids`, `ingest_gaze_email_message_ids`, `ingest_bound_inbox_message`), **reuse it**: ensure the public Land Meteorite name required by this plan exists (thin alias OK) with the return contract in 2c, and that `stamp_last_email_check` / last-check updates stay **off** for this entrypoint.
   - If only the AST-1090 null-shell `run_gaze_email` + `_handle_bound` exist, continue with 2b (extract/share — this is the callable AST-1129 needs; not an interim adapter around `run_gaze_email`).

⚠️ **Decision — no `run_gaze_email` wrapper:** Parent Boundaries forbid a throwaway adapter on the null-candidate shell. Selected-ids must drive per-message ingest directly (shared helpers), never “list whole inbox then pretend the dispatch row ran.”

### 2b. Share bound-message ingest (when AST-1136 has not already done so)

1. In `src/core/gaze_email.py`, keep `_handle_bound` (or rename to a clear shared helper if AST-1136 already did) as the single path that:
   - loads HTML via `get_message_html`
   - shape-routes (ignore / html_links / subject_url / subject_body)
   - Ruth parse with **bound candidate** API key
   - Playwright scrape + `job_link_exists_for_candidate` dedupe
   - `create_meteorite_job` → **METEORITE_NEW**
   - archive-or-leave via `_finalize_archive`
2. Ensure dispatcher `run_gaze_email` (null-shell or candidate-bound, whichever is on the tip after 2a) still calls that same helper for each in-scope message — do **not** duplicate the decision tree.
3. Do **not** move unbound Trash hygiene into the selected-ids entrypoint. Selected-ids only considers the explicit id list; it does **not** scan the rest of the mailbox for retention Trash.

### 2c. Public entrypoint

1. Add (module public section, above helpers — Code Rules §1.3 public-then-helpers) after any existing public `run_gaze_email`:

```python
async def run_gaze_email_selected_ids(
    message_ids: list[str],
    *,
    debug: bool = False,
) -> dict:
    """Land Meteorite: ingest only these Astral inbox message ids (AST-1140).

    Same bind/route/scrape/dedupe/create/archive outcomes as dispatcher gaze_email.
    Does not stamp candidate.last_email_check. Does not call Create strip/extract.
    """
```

2. Behavior (literal):

   - If `debug`: `logger.set_debug_flag(True)`.
   - Normalize ids: preserve caller order; for each raw id `strip()`; drop empties from processing but do **not** invent ids.
   - Build an index of current inbox once: `by_id = { (m.get("id") or ""): m for m in list_inbox_messages(debug=debug) }` (uses existing From→`candidate_match` enrichment from `src/core/inbox.py`).
   - Initialize `results: list[dict] = []` and aggregate counters `total_processed = total_passed = total_failed = total_errors = total_skipped = 0`.
   - Let `n = len(normalized_ids)`. For each `(i, mid)` in `enumerate(normalized_ids, start=1)`:
     1. Style D index header via `_dbg_selected` (below) with outcome `found` first when `debug` (same “found then recorded” pattern as AST-1090).
     2. If `mid` not in `by_id`: append result `{ "message_id": mid, "outcome": GAZE_EMAIL_CONFIG["selected_outcome_skipped_not_in_inbox"], "astral_candidate_id": None }`; `total_skipped += 1`; `total_processed += 1`; Style D recorded outcome = skipped-not-in-inbox; **continue**.
     3. `msg = by_id[mid]`; `match = msg.get("candidate_match") or {}`.
     4. If not `match.get("matched")` or not `(match.get("astral_candidate_id") or "").strip()`:
        - outcome = `selected_outcome_skipped_unbound` when `matched` is false; else `selected_outcome_skipped_unmatched`
        - append result with that outcome + `astral_candidate_id=None` (or the blank id); increment skip/processed; Style D; **continue** (do **not** Trash — retention hygiene is dispatcher/AST-1136, not Land Meteorite).
     5. Call shared `_handle_bound(msg, match, debug=debug, index=i, total=n)` (or AST-1136 equivalent).
     6. Map helper deltas to a single per-id `outcome` string for the result row:
        - prefer the last Style D / helper recorded outcome when available; otherwise: `error` if errors delta > 0; `failed` if failed delta > 0; else `archived` / `ignored` consistent with `_handle_bound` paths (create+archive → `archived`; ignore shapes → `ignored`).
        - append `{ "message_id": mid, "outcome": <str>, "astral_candidate_id": match["astral_candidate_id"] }`
        - add deltas into aggregates (`total_processed` / `passed` / `failed` / `errors` as today’s runner does).
   - **Forbidden in this function body:** any call to `create_meteorite_job_from_inbox_message`; any call to `update_candidate_last_email_check` (or raw SQL stamp of `last_email_check`); any call to `trash_message` for unbound retention; any call into qualify/GDL / dispatcher hop chaining; listing/processing message ids outside the selected list.
   - Return:

```python
    return {
        "results": results,
        "total_processed": total_processed,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "total_errors": total_errors,
        "total_skipped": total_skipped,
    }
```

3. Style D helpers (selected path only):

```python
def _dbg_selected(debug: bool, *, index: int, total: int, mid: str, outcome: str) -> None:
    if not debug:
        return
    logger.debug_index(
        func=GAZE_EMAIL_CONFIG["debug_func_selected"],
        index=index,
        total=total,
        identifier=(mid or "")[:80],
        outcome=outcome,
    )
```

Reuse existing `_detail` for working lines (`from_address=…`, `astral_candidate_id=…`, create/skip/archive detail). When `debug=False`, emit **no** new debug-contract lines from this path.

4. Module docstring: note AST-1140 selected-ids Land Meteorite entrypoint + “does not stamp `last_email_check`”.

⚠️ **Decision — list-once + index, not per-id Gmail list:** `list_inbox_messages` already carries `candidate_match`. One list call per Land Meteorite action avoids N list RPCs; ids absent from the current inbox become `skipped-not-in-inbox` (explicit feedback for AST-1141).

⚠️ **Decision — skip ≠ Trash on selected unbound:** Parent AC5 / Boundaries: unbound selected messages are skipped with feedback; retention Trash stays on the dispatcher/AST-1136 hygiene path so Land Meteorite does not mutate non-selected mailbox policy.

**Done when (recheck):** `python3 -m py_compile src/core/gaze_email.py src/utils/config.py` succeeds; `rg -n 'create_meteorite_job_from_inbox_message|update_candidate_last_email_check' src/core/gaze_email.py` shows **no** matches inside `run_gaze_email_selected_ids` (and no new imports of those symbols for this ticket).

---

## Stage 3: Import smoke + boundary lock

**Done when:** Import smoke passes; boundaries verified by search.

1. Run:

```bash
python3 -c "from src.core.gaze_email import run_gaze_email_selected_ids; import inspect; assert inspect.iscoroutinefunction(run_gaze_email_selected_ids)"
```

2. Confirm by ripgrep (must be empty hits for this ticket’s additions):

   - `run_gaze_email_selected_ids` body does not reference `create_meteorite_job_from_inbox_message`
   - `run_gaze_email_selected_ids` body does not reference `last_email_check` / `update_candidate_last_email_check`
   - No new files under `src/ui/` or `src/ui/frontend/` on this publish tip for AST-1140

3. No Linear status gymnastics beyond build-child’s normal stage comments — plan publish only moves to Plan Ready (§10).

---

## Self-Assessment

**Scope:** `Single-Component` — `GAZE_EMAIL_CONFIG` literals plus `src/core/gaze_email.py` public selected-ids entrypoint sharing the existing bound-message ingest helper; no UI/admin/dispatcher ownership.

**Conf:** `Medium` — AST-1090 `_handle_bound` path is known and reusable, but AST-1136 may still rewrite the candidate-bound runner on `ftr/AST-1128`; Stage 2a merge/reuse gate is mandatory so we do not fork ingest.

**Risk:** `Medium` — wrong wiring could land jobs via the retired Create path, stamp `last_email_check` on Land Meteorite, or process non-selected inbox mail; the plan forbids those call sites explicitly.

---

## Code Rules self-review

- §1.1 in-scope-only — no admin HTTP / React / dispatcher / Create retirement UI / qualify hop.
- §1.3 DRY / public-then-helpers — one shared bound ingest; public `run_gaze_email_selected_ids` first.
- §1.4 / §2.1 — outcome strings + debug func in `GAZE_EMAIL_CONFIG`; no parallel Land-Meteorite block.
- §1.5.1 Style D — `debug_func_selected` + `_dbg_selected` / `_detail` only when `debug=True`.
- §2.6 / `astral.state.no-daisy-chain-in-run` — stop at **METEORITE_NEW** via existing create helper; no qualify/GDL.
- §3.3 imports — core may use inbox / meteorite / gmail / config / logging as today; no UI imports.

---

## Review

| Field | Value |
|-------|-------|
| Branch | `sub/AST-1129/AST-1140-selected-ids-gaze-email-ingest-entrypoint` |
| Tip | `5c9f62043330c2be1ab3ac25d59402bb72dd08db` |

### Radia — code-rubric.v1 (`[code-rubric] revision=1`)

**Publish ref tip (at review):** `288c11d028ca20f3dc7c532b00ec2f819658ea04`  
**Overall:** DISCUSS (no fix-now on AST-1140 selected-ids path; C4 soft-merge stragglers)

**What’s solid**
- `run_gaze_email_selected_ids` matches Stages 1–2: list-once index, skip unbound/unmatched/not-in-inbox with `GAZE_EMAIL_CONFIG` vocabulary, shared `_handle_bound` + `index_dbg=_dbg_selected`, return contract for AST-1141.
- Forbidden call sites absent in the selected-ids body (`create_meteorite_job_from_inbox_message`, `update_candidate_last_email_check`, unbound `trash_message`, qualify/GDL).
- Style D gated: `_dbg_selected` / `_detail` only when `debug=True`; `debug_func_selected=gaze_email.selected_ids`.
- AST-1140 `code()` commit touches only `src/core/gaze_email.py` + `src/utils/config.py` (+ plan doc).

**Issues / Recommended**
- **discuss (C4 stragglers):** Stage 2a soft-merge of `ftr/AST-1128` put `docs/features/**`, `src/data/**`, and `src/ui/api/**` on the tip, so five Joan-excluded statutes are in-scope on the three-dot diff. Each scored **conforms** (see Linear); no product rewrite required for Land Meteorite itself.
- **advisory:** Tip carries AST-1134/1135 dispatcher/avail/database surface from that soft merge while dispatcher `run_gaze_email` on this tip remains the AST-1090 null-shell shape (AST-1136 candidate-bound `process_gaze_email_messages` is not an ancestor of this tip). Land Meteorite entrypoint is isolated and correct; candidate-bound runner coherence stays with AST-1128/AST-1136 rollup.

Full `## Statutes checked` (65/65) + Pattern / Plan adherence live in the Linear Review Posted comment.

---

## Resolution

**Date:** 2026-08-02  
**Radia tip at review:** `53a66550` (`docs(AST-1140): Radia review — findings`)  
**Resolve publish tip:** see Linear / `origin/sub/AST-1129/AST-1140-selected-ids-gaze-email-ingest-entrypoint` after this commit.

| Finding | Disposition |
|---------|-------------|
| **fix-now** | none |
| **discuss (C4 stragglers)** — Stage 2a soft-merge widened three-dot tip | Acknowledged; each statute already **conforms**; no product rewrite |
| **advisory** — tip still AST-1090 null-shell while carrying AST-1134/1135 surface | Cleared on resolve: mandatory `git merge origin/dev` landed AST-1136 candidate-bound `run_gaze_email` + `process_gaze_email_messages`; kept AST-1140 `run_gaze_email_selected_ids` + `_handle_bound` 5-tuple/`index_dbg` |

**Product merge notes (`origin/dev`):**
- Kept selected-ids entrypoint + injectable Style D helper.
- Took AST-1136 dispatcher runner (requires `candidate_id`, stamps `last_email_check`) and `process_gaze_email_messages` (no stamp/Trash); callers unpack the 5th outcome from `_handle_bound`.
- Engineer hook excludes test-tree from the merge commit — Betty tip on this sub kept AST-1140 tests only; origin/dev carries updated AST-1090 + AST-1136 + AST-1140 tests that need intake via `[qa-handoff]`.

**Betty `[qa-handoff]` return:** tip `addec765` (`test(AST-1140): return — AST-1136+1140 gaze_email tree + 5-tuple mocks`) — combined AST-1090/1136/1140 tests + bible on publish ref; `_handle_bound` mocks are 5-tuple. Manifest re-run green → User Testing.
