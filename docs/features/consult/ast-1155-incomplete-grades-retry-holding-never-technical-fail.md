<!-- linear-archive: AST-1155 archived 2026-08-07 -->

## Linear archive (AST-1155)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1155/incomplete-grades-retry-holding-never-technical-fail-technical-fail  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1150 — Technical fail for Do prompt  
**Blocked by / blocks / related:** parent: AST-1150; blocks: AST-1156

### Description

## What this implements

Shared consult apply path: reject incomplete/extra vector sets before `_render_score`; always route to retry holding for that trigger (standard + meteorite). Technical-fail states reserved for true infra failures. Debug expected-vs-decoded vector detail. Does **not** own prompt copy (sibling Rubric completeness contracts) or Skipped Retry.

## In scope

- [X] `astral.patterns.render-verdict-orchestrates-consult` — scored apply stays on consult verdict / batch process path
- [X] `pattern.batch.entity-claim-process-release` — incompleteness is per-entity process failure inside claim → process → release
- [X] `astral.state.core-decides-transitions` — retry vs technical via `JOB_STATES.retry_state` + `_consult_batch_fail_dest`
- [X] `pattern.state.entity-state-transitions` — new `*_RETRY` holdings and priors for graded triggers
- [X] `pattern.config.config-block` — retry destinations config-owned (no hard-coded technical remap in process_fn)
- [X] `astral.agent.grade-vector-validation` — live-rubric completeness at consult apply (grade_* have no TASK_CONFIG.vectors)
- [X] `astral.standards.debug-contract-gated` — expected vs decoded vector detail only when `debug=True` (Style D)

## Considered but excluded

- [X] `astral.agent.confidence-bounds` — X/0 no-signal contract + prompt hardening owned by AST-1154; this ticket only treats X/0 as present rows
- [X] Skipped Retry / `bulk_retry_to_state` hop landing — AST-1156 (`src/ui` / skipped config)
- [X] Prompt / `{$OUTPUT_INSTRUCTIONS}` / `agent_task.json` completeness copy — AST-1154
- [X] `src/core/agent.py` decode / static TASK_CONFIG.vectors validation — not the live-rubric apply gate
- [X] Scoring math / dealbreaker behavior for complete grade sets — unchanged

## Acceptance criteria

1. [x] Replaying any rubric grading batch (Do/Get/Like/JD/qualify/prefilter and meteorite twins) where the model omits at least one expected vector sends that job to **retry holding**, not `*_FAILED_TECHNICAL_*` / meteorite technical-fail.
2. [x] When every rubric vector is present (including intentional `X`/`0`), pass/fail/dealbreaker/scored behavior matches today’s complete-grade behavior.
3. [x] With `debug=True`, incomplete-grade jobs log missing/unexpected vectors under Style D index + `|` detail.

## Boundaries

- [X] Does **not** own prompt/output-contract copy or Skipped Retry landing. Does **not** change scoring math for complete grade sets.

## Notes for planning

Parent decision: incomplete grades always retry, never technical fail. Statute frame is In scope / Considered but excluded above.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-08-03T01:45:42.129Z
[merge-child] blocked: validate-sub-log — git pull merge on sub (`Merge remote-tracking branch 'origin/dev'…` @ c1301c18; also 8e4c10f2 from origin/dev tip not yet on ftr).

@Hedy Lamarr — restack/republish `origin/sub/AST-1150/AST-1155-incomplete-grades-retry-holding-never-technical-fail` from clean tip `82ce3365` + `git merge origin/ftr/AST-1150-technical-fail-for-do-prompt` only (message `merge(AST-1155): origin/ftr/…`). Do **not** merge origin/dev into the sub. Force-with-lease push the clean tip so `validate-sub-log` passes.

— Chuckles

#### radia — 2026-08-03T01:37:13.154Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1155
**Publish ref:** a220ab12 (doc commit; code tip e6698dd865f900aca45831b8cd9ce82badcbfae9)
**Overall:** DISCUSS

## Plan adherence
- Stage 1 (`src/utils/config.py`): all 7 planned `*_RETRY` holdings registered with `retry_state` on the correct primaries, priors extended exactly per the plan's per-state table, `IN_REVIEW_STATES`/`JOBS_IN_REVIEW_UI_SECTIONS` insert holdings immediately after their primary, `JOBS_IN_REVIEW_GRADE_FIELD` correctly *omits* `CULTURE_READY_RETRY` / `METEORITE_QUALIFIED_RETRY` (primaries absent from that map today — plan explicitly forbids inventing a speculative entry). `PASSED_LIKE_RETRY` / `METEORITE_PASSED_LIKE_RETRY` correctly untouched (out of scope).
- Stage 2 (`src/core/consult.py`): `_grade_set_vector_diff` / `_require_complete_grade_set` / `_debug_incomplete_grade_set` match the plan verbatim; `_render_score` refactored to call the shared helper (DRY, as preferred); gate added before `_render_score` in `_apply_render_verdict_decoded_job`, before `_render_pass_fail` in both `qualify_job_listings.process` and `evaluate_jd_batch.process`; `_run_batch_consult`'s except-block emits the new debug path only on message match, falls through to the old generic debug path otherwise — confirmed no double-logging (process_fn never logs itself, only raises). `_INPUT_STATE_TO_TASK` gets exactly the 2 planned companions, no meteorite expansion.
- Stage 3 (`consult.render_verdict`, `roster._apply_prefilter_decoded_company_outcome`): `render_verdict` keeps the `Unknown grading_mode:` re-raise, routes `missing vectors`/`unknown vectors` through `_consult_batch_fail_dest` instead of `_fail`, returns without touching `error_state` directly. Roster gate re-raises after debug (matches Joan's plan-time discuss-3 resolution — both real callers already catch `ValueError` into their existing `_prefilter_fail` retry paths; confirmed unchanged in this diff). Prep-failure branches (`_consult_scored_dispatch_batch_encoded` no-company / no-live-content) untouched — still go straight to `error_state` as required.
- **Live-ran all three of the plan's own verification scripts against the actual publish tip** (not just prose): Stage 1 `retry_state`/`dispatch_claim_states` pairs, Stage 2 `_require_complete_grade_set` behavior incl. `X`/`0` counting as present, Stage 3 `_consult_batch_fail_dest` first-strike/second-strike routing incl. meteorite overlay error state. All three passed clean on this tree.
- Full active statute set (65) scored in-session — 0 fix-now, 2 discuss carried from Joan's plan-rubric verdict (confirmed still accurate against the shipped diff, not just the plan), 3 trivially-clean C4 stragglers (see Notes).

## Pattern conformance
- `pattern.batch.entity-claim-process-release` — conforms. Incompleteness stays a per-entity process failure inside the existing claim→process→release scaffold; no new claim/clear signature.
- `pattern.state.entity-state-transitions` — conforms. New holdings registered in `JOB_STATES` with real priors; core (`consult.py`/`roster.py`) decides the destination and passes it to tracker/data; retry is a separate dispatch-cycle claim, not an in-run hop.
- `pattern.config.config-block` — conforms. Retry destinations live in `JOB_STATES.retry_state`; Decision 1 explicitly forbids a hard-coded technical→retry remap in `process_fn`, and the diff honors that.

## Findings

**discuss — `astral.dispatch.run-next-is-chain-authority`.** Carried from Joan's plan-rubric verdict, confirmed unchanged in the shipped diff: Stage 2 step 7 extends the legacy `_INPUT_STATE_TO_TASK` state→task map with `PASSED_JD_RETRY`→`grade_do` / `PASSED_DO_RETRY`→`grade_get`. This is explicitly a non-dispatch-routing legacy map per the code's own comment, and the diff correctly declines to expand it with meteorite keys (AST-1055: dispatch uses explicit `task_key`). Non-blocking; flagging for visibility only.

**discuss — `astral.standards.no-hardcoded-sets`.** Carried from Joan's plan-rubric verdict, confirmed unchanged in the shipped diff: `render_verdict`'s incompleteness branch keys off `"missing vectors" in es or "unknown vectors" in es` — literal exception-message substring matching. Retry destinations themselves are correctly config-owned; only the *routing trigger* is string-based. Joan's suggested alternative (a dedicated `ValueError` subclass caught by type) would remove the coupling for about the same cost, since Stage 2 authors the raiser in the same file. Engineer's call, exercised — kept the substring match with the message prefix preserved for stability. Not fix-now.

## Frame diff
(none) — description already reflects the shipped diff via the plan doc's Files Changed table, Decisions, and Review stub section; no adds/moves applied to the Linear description itself.

## Notes
- Accepted-risk note carried from Joan (not a new finding): once `retry_state` exists on the seven primaries, *any* `process_fn` exception on those triggers first-strikes to the retry holding, not just incomplete grade sets — this is the established AST-642 behavior `NEW`/`JD_READY` already have, and the infra-failure paths the parent Boundary protects (missing company, prep failure, provider error) all occur outside `process_fn` and still route straight to `error_state` (confirmed unchanged in `_consult_scored_dispatch_batch_encoded`'s prep-skip branches). Second strike from a holding still lands technical — no loop.
- C4 straggler check: 3 statutes Joan's plan-rubric verdict scored not-applicable/excluded (`astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`) score `conforms` on this diff-based sweep — same structural cause as AST-1154's review: the actual diff includes both plan-doc files (this ticket's own, plus AST-1154's via shared `ftr/AST-1150` ancestry) and the pipeline's later test/test-bible commits, neither of which sit in the plan's Files-Changed table by convention. All clean; not scope creep. Per-commit role separation verified: `code()` commits (`64ce12d2`, `4d735e94`, `47974f81`) touch only `src/utils/config.py` / `src/core/consult.py` / `src/core/roster.py`; `test()`/`merge-tests()` commits (`88de69a2`, `e6698dd8`) touch only `tests/**` and `docs/test-bible/**`.
- `docs/test-bible/{core/builder,core/candidate,frontend/pages,ui/api/api_system}.md` and matching test files carry unrelated sibling-ticket entries (AST-1147/1148/1149/1152/1154) — bleed-in from the shared `origin/tests` branch via `merge-tests`, not authored by this ticket.

## What's solid
- Root-cause diagnosis was correct and the fix addresses it directly: the actual repro path (`_consult_scored_dispatch_batch_encoded` → `_apply_render_verdict_decoded_job` → raise → caught by `_run_batch_consult`) now resolves through `_consult_batch_fail_dest`, which already understood `retry_state` (AST-642) — the only missing piece really was the registry entries, and that's exactly what Stage 1 supplies.
- DRY: `_render_score` now calls the shared `_require_complete_grade_set` instead of duplicating set math; `qualify_job_listings`'s old swallowed-exception path no longer double-duties as the completeness gate.
- Debug emission is single-sourced per code path (no double logging), gated correctly behind `debug=True`, Style D shape.
- Clean boundary discipline: no prompt/`agent_task.json` touch (AST-1154's territory), no Skipped Retry / `bulk_retry_to_state` touch (AST-1156's territory), no scoring-math change for complete sets — verified live via the `X`/`0`-counts-as-present assertion in the Stage 2 script.

context_tokens≈195000

— Radia

#### betty — 2026-08-03T01:29:27.228Z
## QA test manifest — AST-1155

**Publish:** `origin/sub/AST-1150/AST-1155-incomplete-grades-retry-holding-never-technical-fail` @ `e6698dd8`
**tests SHA:** `88de69a2` (`test(AST-1155): incomplete grades retry holding never technical fail`)
**merge-tests:** `merge-tests(AST-1155): origin/tests 88de69a2d6d9768cd0abdcad0c626a2edc0dd46b`

### Classification

1. **Existing coverage (bible-backed)**
   - `tests/component/core/test_consult.py::TestRenderScore::test_x_excluded_from_v` — complete sets with intentional `X`/`0` still score.
   - `tests/component/core/test_consult.py::TestConsultBatchFailDest` — AST-642 fail-dest helper still holds for qualify/evaluate paths.

2. **Broken / obsolete (revised this pass)**
   - `TestAst874FetchCulturePagesConfig::test_job_states_and_like_priors` — LIKE priors include `CULTURE_READY_RETRY`.
   - `TestAst1053MeteoriteGdlJobStates` — meteorite GDL priors + In Review `_PASS` include new `*_RETRY` holdings.

3. **Gaps (new this pass)**
   1. `tests/component/utils/test_config.py::TestAst1155GradedRetryHoldings` — seven primary→holding claim companions, In Review labels/order, grade-field maps.
   2. `tests/component/core/test_consult.py::TestAst1155IncompleteGradeRetry` — completeness helper (`X0` present); graded fail-dest matrix; `render_verdict` first strike → retry / second → technical; meteorite holding; batch incomplete → `PASSED_JD_RETRY`.
   3. `tests/component/core/test_roster.py::TestAst1155PrefilterIncompleteRetry` — apply raises on incomplete set; `prefilter_company` → `WEBSITE_FOUND_RETRY`.

**Integration:** none — no existing scenario asserts incomplete→technical vs retry.

### Run

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst1155IncompleteGradeRetry \
  tests/component/core/test_roster.py::TestAst1155PrefilterIncompleteRetry \
  tests/component/utils/test_config.py::TestAst1155GradedRetryHoldings \
  tests/component/utils/test_config.py::TestAst874FetchCulturePagesConfig \
  tests/component/utils/test_config.py::TestAst1053MeteoriteGdlJobStates \
  -q
```

### Bible (on publish-ref)

- `docs/test-bible/core/consult.md` shasum `64514ce4c2ccd69770967acdd1bc4d1e43d7db6f`
- `docs/test-bible/utils/config.md` shasum `c232e0df922e9572831835f4ec4180f0c799a355`

— Betty

#### joan — 2026-08-03T01:11:53.946Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1155
**Overall:** APPROVED

Publish ref confirmed against parent Git table: `sub/AST-1150/AST-1155-incomplete-grades-retry-holding-never-technical-fail` @ `85f598b0`.

Self-assessed Risk is `HIGH`, so this got the deeper pass the rubric asks for: I verified every state name, helper, and call site the plan depends on against the worktree rather than taking the plan's word. It held up. Notes on why HIGH risk did not trigger escalation are at the end.

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 incomplete/extra vectors → retry holding, never `*_FAILED_TECHNICAL_*` | Stage 1 (`retry_state` on seven graded triggers) + Stage 2 (gate before `_render_score`) + Stage 3 (`render_verdict` + prefilter routing) |
| AC2 complete sets incl. `X`/`0` behave as today | Stage 2 Decision — exact set equality on stripped labels, `X`/`0` count as present; dealbreaker/threshold math untouched |
| AC3 `debug=True` logs missing/unexpected vectors Style D | Stage 2 `_debug_incomplete_grade_set` (index header + `\|` detail), one emission per job |
| AC4 Skipped Retry hop-correct landing | N/A — boundary (AST-1156); Non-goals name it |
| AC5 (parent AC5 = debug) | Same as AC3 above; child AC list renumbers it 3 |

Parent AC3 (model-facing prompt contracts) is AST-1154's, correctly excluded here.

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 `JOB_STATES` `*_RETRY` holdings + priors + In Review wiring | Functional scope 2 "Incomplete grades always retry — never technical fail"; Architectural definition `pattern.state.entity-state-transitions` and `pattern.config.config-block` |
| Stage 2 completeness helper + apply gates + Style D debug | Functional scope 1 (enforcement half) and 5 (debug visibility); `astral.agent.grade-vector-validation` |
| Stage 3 `render_verdict` routing + prefilter gate | Functional scope 2 for the single-job and company paths; parent Boundary "technical fail stays for true infra failures" |

No orphan stages.

## Adversarial verification (plan claims checked against the worktree)

| Plan claim | Result |
|------------|--------|
| Seven graded primaries exist and lack `retry_state` | Verified — `PASSED_JD`, `PASSED_DO`, `CULTURE_READY`, `METEORITE_QUALIFIED`, `METEORITE_PASSED_JD`, `METEORITE_PASSED_DO`, `METEORITE_PASSED_GET` all defined; none carries `retry_state` |
| The seven `*_RETRY` holding names are free | Verified — zero occurrences of any proposed holding name anywhere in `config.py` |
| `JD_READY_RETRY` is the shape to mirror | Verified — exists as a registered holding with the In Review / grade-field wiring the plan copies |
| `dispatch_claim_states`, `IN_REVIEW_STATES`, `JOBS_IN_REVIEW_UI_SECTIONS`, `JOBS_IN_REVIEW_GRADE_FIELD` exist | Verified in `config.py` |
| `grade_*` TASK_CONFIG rows omit static `vectors`, so `do_task._validate_grades` cannot gate completeness | Verified — `grade_do` / `grade_get` / `grade_like` / `evaluate_jd` / `qualify_job_listings` all have no `vectors` key; consult apply really is the enforcement point |
| Root cause: `bad_grades` → `_consult_batch_fail_dest` → `error_state` when no `retry_state` | Verified at `consult.py:1130-1141` and the `bad_grades` block at `1319-1396` |
| First strike → holding, second strike → technical, no loop | Verified — `_consult_batch_fail_dest` returns `retry_state` when set; from a holding with no `retry_state` it falls through to `error_state`. Holdings are specified without `retry_state`, so the second strike terminates |
| `render_verdict._fail` always uses `error_state`, so incompleteness needs a separate dest | Verified at `consult.py:1026-1032`; job-not-found / company-not-found / prep-failure branches all go through `_fail` and the plan leaves them alone |
| All Stage 2/3 symbols exist | Verified — `_strip_code`, `_render_score`, `_apply_render_verdict_decoded_job`, `render_verdict`, `_consult_job_identifier`, `_INPUT_STATE_TO_TASK`, `_run_batch_consult`; roster `_prefilter_fail`, `_prefilter_batch_fail_dest`, `_apply_prefilter_decoded_company_outcome` |
| roster already imports consult helpers (no new layer edge) | Verified — `roster.py` already does `from src.core.consult import ...` inside the apply function; core → core, no layer breach |
| Stage 3 step 2's unresolved fork | Resolved by inspection — see discuss finding 3; both callers already catch, so only the plan's first branch is live |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | One `code()` commit per stage on the sub ref |
| orch.git.flow-direction-inviolable | conforms | Publishes to `origin/sub/...` only |
| orch.git.ftr-sub-topology | conforms | Publish ref matches the parent Git table row |
| orch.git.merge-on-checkout | conforms | No merge recipe proposed |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | Sub branch only |
| orch.git.one-epic-worktree-per-parent | conforms | Executes on `astral-AST-1150` |
| orch.git.three-permanent-branches | conforms | Invents no permanent branch |
| orch.pipeline.call-susan-for-product-decisions | conforms | Stage-blocked template escalates to parent AST-1150 |
| orch.pipeline.plan-is-bible | conforms | Binding contract + Files Changed table; the one conditional step resolves deterministically against the code (discuss 3) |
| orch.pipeline.project-scoped-queues | conforms | Single child, Astral Consult |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready entry |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | Test and bible files sit in a separate "Verify only (Betty / qa-child — engineer does not edit)" table, outside Files Changed — exactly the right shape |
| orch.roles.chuckles-never-ticket-assignee | conforms | Hedy implements |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer path after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | No banned-path edits |
| astral.agent.confidence-bounds | conforms | `X`/`0` rows count as present; plan invents no grades for omissions |
| astral.agent.do-task-delegation | conforms | No change to `do_task` call shape or task_key resolution |
| astral.agent.grade-vector-validation | conforms | Enforces the full live-rubric set at consult apply, which is the only available gate given `grade_*` has no static `vectors` |
| astral.batch.batch-id-first | conforms | No claim/get/clear signature change |
| astral.batch.batch-id-format | conforms | No batch_id construction change |
| astral.batch.claim-process-release | conforms | Incompleteness stays a per-entity process failure inside the existing claim → process → release scaffold |
| astral.batch.entity-agent-responses-latest-only | conforms | RESPONSE entity_id tagging untouched |
| astral.config.config-source-of-truth | conforms | Retry destinations are `JOB_STATES.retry_state`; Decision 1 explicitly forbids a hard-coded remap in `process_fn` |
| astral.config.pass-threshold-vs-score-floor | conforms | Neither value touched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets or env lookups |
| astral.dispatch.run-next-is-chain-authority | needs-discussion | Stage 2 step 7 extends the legacy `_INPUT_STATE_TO_TASK` state→task shadow map — see discuss 2 |
| astral.dispatch.seed-auto-false | conforms | Step 6 explicitly declines to seed `dispatch_task` companion rows; claim is registry-driven |
| astral.git.betty-no-src-or-features | conforms | Engineer owns `src/`; Betty's files are verify-only |
| astral.layers.core-vs-external-bright-line | conforms | No external I/O moved into core |
| astral.layers.import-direction | conforms | core → core helper reuse on an import edge that already exists; no new data/external imports |
| astral.layers.ui-config-driven-business-logic | conforms | In Review labels/sections resolved from config, not React |
| astral.patterns.coat-check-never-store-empty | conforms | Stage 2 gates *before* persist, so incomplete sets are never stored |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Scored apply stays on the `render_verdict` / `_run_batch_consult` path; no parallel router introduced |
| astral.seed.agent-tables-in-repo-json | conforms | No `data/admin/**` edits |
| astral.seed.archie-catalog-wins | conforms | State registry change is a committed config edit |
| astral.seed.boot-only-not-hot-path | conforms | No new seed execution path |
| astral.seed.define-approved | conforms | New `*_RETRY` states are state-registry entries, not a new seed catalog or coverage rule; parent Functional scope 2 names the retry-holding need |
| astral.seed.operator-rows-stay-deleted | conforms | Step 6 declines to insert dispatch rows |
| astral.seed.other-via-coverage-join | conforms | No candidate-scoped seed inserts; no hardcoded candidate ids |
| astral.standards.data-raises-caller-logs | conforms | Data layer untouched; core raises and the batch scaffold logs |
| astral.standards.debug-contract-gated | conforms | Incomplete detail only under `debug=True`, Style D index header + `\|` detail, one emission per job |
| astral.standards.dry-and-focused-functions | conforms | One `_grade_set_vector_diff` / `_require_complete_grade_set`; `_render_score` refactored to call it rather than duplicate the set math |
| astral.standards.in-scope-only | conforms | Explicit out-of-scope list covers `agent_task.json`, `agent.py`, `src/ui/**`, Skipped `bulk_retry_to_state`, tests |
| astral.standards.logging-via-utils | conforms | Uses `logger.debug_index` / `debug_detail` from utils logging, no `print` |
| astral.standards.names-not-ticket-ids | conforms | `{PRIMARY}_RETRY`, `_grade_set_vector_diff`, `_require_complete_grade_set` are domain names; AST-1155 appears only in a docstring |
| astral.standards.no-cross-contamination | conforms | Stays within core + utils config |
| astral.standards.no-hardcoded-sets | needs-discussion | Retry destinations are correctly config-owned, but Stage 3 routes on inline exception-message substrings — see discuss 1 |
| astral.standards.public-then-helpers | conforms | Helpers placed adjacent to `_render_score`, consistent with file organization |
| astral.standards.utils-data-late-import-only | conforms | No `utils → data` import added |
| astral.state.core-decides-transitions | conforms | Core decides the destination and passes it to the data layer; the policy itself lives in `JOB_STATES` |
| astral.state.job-prior-states-enforced | conforms | Stage 1 step 2 extends `prior_states` for every new holding's outbound edges, with an explicit instruction not to invent new hop edges |
| astral.state.no-daisy-chain-in-run | conforms | Retry is a separate dispatch cycle claim, not an in-run hop |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn or worker change |

## Considered and excluded

**Considered (56):** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.dispatch.run-next-is-chain-authority, astral.dispatch.seed-auto-false, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.seed.agent-tables-in-repo-json, astral.seed.archie-catalog-wins, astral.seed.boot-only-not-hot-path, astral.seed.define-approved, astral.seed.operator-rows-stay-deleted, astral.seed.other-via-coverage-join, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.names-not-ticket-ids, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded (9):**
- astral.debug.no-repo-root-artifacts-dir — paths [artifacts/**, scripts/spikes/**] match no plan path
- astral.debug.spikes-under-debug-dir — paths [debug/**, docs/features/**, scripts/spikes/**] match no plan path
- astral.docs.features-single-file-per-ticket — layers [docs] does not intersect plan layers [core, utils]
- astral.git.engineer-test-tree-ban — paths [tests/**, docs/test-bible/**, ...] match no plan path; the plan's test references are in a verify-only Betty table, not Files Changed
- astral.layers.scripts-exempt-from-layer-rules — layers [scripts] does not intersect plan layers
- astral.patterns.require-auth-on-protected-endpoints — layers [ui] does not intersect plan layers
- astral.standards.database-header-inventory — layers [data] does not intersect plan layers
- astral.ui.frontend-file-placement — layers [ui] does not intersect plan layers
- astral.ui.naming-conventions — layers [ui] does not intersect plan layers

## Findings

**No fix-now findings.**

**discuss 1 — retry routing is wider than incompleteness, and the plan does not say so.** `_run_batch_consult` catches `except Exception` from `process_fn` into `bad_grades` (`consult.py:1326-1340`) and routes the whole set through `_consult_batch_fail_dest`. Once Stage 1 puts `retry_state` on the seven primaries, *every* `process_fn` failure on those triggers first-strikes to the retry holding — a save error or an unexpected `KeyError`, not just an incomplete grade set. I do not think this breaks the parent Boundary "does not turn genuine technical failures into retry-hold": the infra failures that Boundary names (missing company, prep failure, provider error) all occur outside `process_fn` and still go straight to `error_state`, which I confirmed in `render_verdict._fail` and which Stage 3 step 3 explicitly preserves. The second strike from the holding still lands technical, so nothing loops. It is also the established AST-642 behavior that `NEW` / `JD_READY` already have. Flagging it because it is a real behavior change the plan never states, and Radia and Betty should be looking for it rather than discovering it. Worth one sentence in the plan.

**discuss 2 — Stage 3's incompleteness routing keys off exception-message substrings.** `render_verdict` will branch on `str(e)` containing `missing vectors` / `unknown vectors`, and Stage 2 deliberately preserves the `_render_score:` message prefix to keep that working. This is the one place where the fix for a mis-routing bug depends on prose staying stable; if anyone reworded those raises later, incompleteness would silently fall back to technical fail — the exact bug being fixed here. Two things keep it off the fix-now list: the batch path that produced the repro does not use substrings at all (any `process_fn` exception is already routed by state), so only the single-job `render_verdict` path is exposed; and the plan narrows the match deliberately and says so. Since Stage 2 is authoring the raiser anyway, a dedicated `ValueError` subclass caught by type would cost about the same and remove the coupling — `_render_score`'s own defense-in-depth raises are in the same file and in scope. Engineer's call, and `astral.standards.no-hardcoded-sets` is scored needs-discussion on that basis.

**discuss 3 — Stage 3 step 2 leaves a fork open; here is the answer so nobody improvises.** The step says to re-raise so the caller's existing `_prefilter_fail` path runs, then adds a fallback for "if the current caller does not catch apply-outcome errors" and tells the builder to inspect the live caller. I inspected it: both callers already catch. `prefilter_company` wraps the apply call in `except ValueError as outcome_err: return _prefilter_fail(...)` (`roster.py:1979-1994`), and `_run_batch_company_prefilter` wraps it in `except Exception` → `bad_grades` → `_prefilter_batch_fail_dest` (`roster.py:2207-2228`). So the plan's first branch is the live one, the fallback branch is dead, and no third router is needed. Under the plan's own "stop when a step is ambiguous" contract this could have cost a round trip; recording the resolution here instead.

**acceptable — self-assessment honesty.** Scope `Single-Component`, Conf `high`, Risk `HIGH` are all honest. The Risk justification is specific rather than generic — wrong priors or holding names would break claim and transition across every rubric hop, and an over-broad `render_verdict` except could retry real infra failures. That second concern is exactly the right thing to have worried about, and Stage 3's narrow carve-out plus step 3's "do not change those branches" instruction is a real mitigation, not a hand-wave.

**Why HIGH risk did not escalate.** The rubric escalates HIGH risk only when I am not confident the plan handles it. Every load-bearing fact the plan asserts checked out against the tree: the seven primaries exist and lack `retry_state`, the seven holding names are unused, `JD_READY_RETRY` gives a working precedent for all four registry touch points, `grade_*` genuinely has no static `vectors`, the second-strike path terminates, and every named helper exists where the plan says. The residual risk is concentrated in prior-state wiring, which Stage 1 step 2 handles edge by edge with an explicit "do not invent new hop edges" guard and a runnable assertion in step 7. That is a plan I am confident in.

**R6 checklist.** Definition fidelity pass — implements Functional scope 2 and 5, nothing more. Boundaries pass — no prompt copy, no Skipped landing, no scoring-math change for complete sets. Layer and import pass. Config-as-source-of-truth pass. Placement pass. Batch pattern respected. Debug gating correct. DRY pass. No sibling scope creep into AST-1154 or AST-1156, and the plan correctly states it does not depend on AST-1154 landing first.

context_tokens≈120000

— Joan

#### hedy — 2026-08-03T01:04:07.753Z
Plan published on `origin/sub/AST-1150/AST-1155-incomplete-grades-retry-holding-never-technical-fail` @ `85f598b0`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1150/AST-1155-incomplete-grades-retry-holding-never-technical-fail/docs/features/consult/ast-1155-incomplete-grades-retry-holding-never-technical-fail.md

**Root cause:** `bad_grades` → `_consult_batch_fail_dest`, but `PASSED_JD` / meteorite graded triggers have no `retry_state`, so incompleteness lands on `*_FAILED_TECHNICAL_*`.

**Self-assessment**
- **Scope:** Single-Component — `JOB_STATES` retry holdings + consult/roster apply gate; no prompts, no Skipped UI.
- **Conf:** high — AST-642/AST-898 pattern; missing `retry_state` is the first-touch technical path; live call sites enumerated.
- **Risk:** HIGH — wrong priors/holding names would break claim/transition across every rubric hop; over-broad `render_verdict` except handling could retry real infra failures.

— Hedy

---

# AST-1155 — Incomplete grades → retry holding (never technical fail)

**Linear:** [AST-1155](https://linear.app/astralcareermatch/issue/AST-1155/incomplete-grades-retry-holding-never-technical-fail-technical-fail)  
**Parent:** [AST-1150](https://linear.app/astralcareermatch/issue/AST-1150/technical-fail-for-do-prompt) — Technical fail for Do prompt  
**Project:** Astral Consult  
**Publish ref:** `sub/AST-1150/AST-1155-incomplete-grades-retry-holding-never-technical-fail`

Shared consult apply path: reject incomplete/extra grade sets against the **live rubric** before `_render_score`; on first attempt always route to the trigger’s **retry holding** state (standard + meteorite). Technical-fail states stay reserved for true infra/apply failures (missing company, prep failure, provider errors, second-strike after `*_RETRY`). Debug expected-vs-decoded vector detail under Style D when `debug=True`.

**Non-goals:** Prompt / `{$OUTPUT_INSTRUCTIONS}` completeness copy (AST-1154). Skipped Retry landing (AST-1156). Scoring math for complete grade sets. Inventing grades for omitted vectors. Betty test-tree / bible edits.

---

## Root cause (locked)

Repro (`grade_do` meteorite batch): agent decode succeeded with an omitted rubric vector; `_render_score` raised `missing vectors ['Healthcare Domain Expertise']`; `process_fn` failure entered `_run_batch_consult` `bad_grades` → `_consult_batch_fail_dest`.

`JOB_STATES["METEORITE_PASSED_JD"]` (and regular `PASSED_JD` / `PASSED_DO` / `CULTURE_READY` / `METEORITE_PASSED_DO` / `METEORITE_PASSED_GET` / `METEORITE_QUALIFIED`) have **no** `retry_state`. AST-642 helper then returns `TASK_CONFIG` / meteorite overlay `error_state` → `*_FAILED_TECHNICAL_*` / `METEORITE_ERROR_EVALUATE_JD`.

Qualify (`NEW`/`JD_READY`) already have retry holdings; Do/Get/Like + meteorite GDL twins do not. `grade_*` TASK_CONFIG rows also omit static `vectors`, so `do_task._validate_grades` never gates live-rubric completeness — consult apply is the enforcement point.

---

## Decisions (locked for build)

1. **Config owns retry destinations.** Add `*_RETRY` holdings + `retry_state` pointers on every graded job trigger that lacks them. Do **not** hard-code technical→retry remaps inside `process_fn`. `_consult_batch_fail_dest` + `dispatch_claim_states` already companion-claim when `retry_state` is set (AST-642 / AST-882 / AST-898).
2. **Shared completeness helper before score.** One consult helper compares live rubric labels (via `_strip_code`) to decoded grade vectors; incomplete/extra raises before `_render_score`. `_render_score` keeps its existing missing/extra raises as defense-in-depth (same message family).
3. **First strike → retry; second strike → technical/error.** Unchanged AST-642 semantics once `retry_state` exists: primary → holding; entity already in holding → `error_state`.
4. **`render_verdict` must not `_fail` incompleteness to technical.** Single-job path today maps almost every `ValueError` from apply to `error_state`. Incomplete/extra messages route through `_consult_batch_fail_dest` instead; true infra messages (missing job/company, missing rubric artifact key, prep) stay on `_fail` / technical.
5. **Qualify must not swallow incompleteness.** `qualify_job_listings.process` currently wraps `_render_score` in `try/except` and continues pass/fail — incompleteness must raise into `bad_grades` like evaluate_jd / grade_*.
6. **Prefilter uses company retry path.** Incomplete/extra on `prefilter_company` calls existing `_prefilter_fail` / `_prefilter_batch_fail_dest` (HOMEPAGE_READY → WEBSITE_FOUND_RETRY already). Do not invent a new company state.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Register graded-trigger `*_RETRY` holdings; `retry_state` on primaries; priors + In Review UI / grade-field maps | utils |
| `src/core/consult.py` | Completeness helper; gate before `_render_score` on scored apply + binary graded process paths; `render_verdict` incompleteness → retry dest; Style D debug; `_INPUT_STATE_TO_TASK` companions for states already in that legacy map | core |
| `src/core/roster.py` | Prefilter apply: completeness gate → `_prefilter_fail` (retryable) before score/persist | core |

**Out of scope:** `data/admin/agent_task.json`, `src/core/agent.py` prompt/decode, `src/ui/**`, Skipped `bulk_retry_to_state`, `tests/**`, `docs/test-bible/**`.

**Verify only (Betty / qa-child — engineer does not edit in build-child):**

| File | Change |
|------|--------|
| `tests/component/utils/test_config.py` | `dispatch_claim_states` companions for new primary→retry pairs |
| `tests/component/core/test_consult.py` | Incomplete grade set on `grade_do` / meteorite overlay → retry holding not technical; second strike → technical; complete set with `X`/`0` unchanged; `render_verdict` incompleteness → retry |
| `tests/component/core/test_roster.py` (or existing prefilter tests) | Incomplete prefilter grades → company retry dest |
| `docs/test-bible/core/consult.md` (and utils/config if needed) | Wording: graded triggers companion-claim `*_RETRY`; incompleteness never first-touch technical |

---

## Stage 1: JOB_STATES — graded-trigger retry holdings

**Done when:** Every graded job trigger below has `retry_state` → a registered holding; `dispatch_claim_states(<primary>, "job")` returns `[primary, holding]`; pass/fail/technical priors accept the holding; In Review UI lists + grade-field maps include the new holdings; `python3 -c "from src.utils.config import JOB_STATES, dispatch_claim_states; …"` asserts listed pairs.

1. In `src/utils/config.py` `JOB_STATES`, add **holding** entries (priors = primary trigger only) and set `retry_state` on each primary:

   | Primary | Holding | Notes |
   |---------|---------|--------|
   | `PASSED_JD` | `PASSED_JD_RETRY` | regular `grade_do` |
   | `PASSED_DO` | `PASSED_DO_RETRY` | regular `grade_get` |
   | `CULTURE_READY` | `CULTURE_READY_RETRY` | regular `grade_like` |
   | `METEORITE_QUALIFIED` | `METEORITE_QUALIFIED_RETRY` | meteorite `evaluate_jd` |
   | `METEORITE_PASSED_JD` | `METEORITE_PASSED_JD_RETRY` | meteorite `grade_do` |
   | `METEORITE_PASSED_DO` | `METEORITE_PASSED_DO_RETRY` | meteorite `grade_get` |
   | `METEORITE_PASSED_GET` | `METEORITE_PASSED_GET_RETRY` | `meteorite_like` |

   Do **not** add a new holding for `JD_READY` / `NEW` / `VALID_TITLE` (already covered). Do **not** add `PASSED_LIKE_RETRY` / `METEORITE_PASSED_LIKE_RETRY` changes (upshot technical-hold — out of scope).

2. Extend **outcome** `prior_states` so a job can leave each new holding into the hop’s pass / scored-fail / technical-error states (mirror how `JD_READY_RETRY` is listed on `PASSED_JD` / `FAILED_JD`):

   - From `PASSED_JD_RETRY`: `PASSED_DO`, `FAILED_DO`, `FAILED_TECHNICAL_DO` (and any other states that today list only `PASSED_JD` as prior for this hop).
   - From `PASSED_DO_RETRY`: `PASSED_GET`, `FAILED_GET`, `FAILED_TECHNICAL_GET`, plus culture-gate priors that already include `PASSED_GET` if they must accept a job that retried GET (only if today’s transitions from `PASSED_DO` already allow those targets — do not invent new hop edges).
   - From `CULTURE_READY_RETRY`: `PASSED_LIKE`, `FAILED_LIKE`, `FAILED_TECHNICAL_LIKE`.
   - From `METEORITE_QUALIFIED_RETRY`: `METEORITE_PASSED_JD`, `METEORITE_FAILED_JD`, `METEORITE_ERROR_EVALUATE_JD`.
   - From `METEORITE_PASSED_JD_RETRY`: `METEORITE_PASSED_DO`, `METEORITE_FAILED_DO`, `METEORITE_FAILED_TECHNICAL_DO`.
   - From `METEORITE_PASSED_DO_RETRY`: `METEORITE_PASSED_GET`, `METEORITE_FAILED_GET`, `METEORITE_FAILED_TECHNICAL_GET`.
   - From `METEORITE_PASSED_GET_RETRY`: `METEORITE_PASSED_LIKE`, `METEORITE_FAILED_LIKE`, `METEORITE_FAILED_TECHNICAL_LIKE`.

3. Insert each new holding into `IN_REVIEW_STATES` immediately after its primary (same pattern as `JD_READY_RETRY` after `JD_READY`).

4. Insert matching rows into `JOBS_IN_REVIEW_UI_SECTIONS` with labels:
   - `"Passed JD (retry)"`, `"Passed DO (retry)"`, `"Culture Ready (retry)"`
   - `"Meteorite Qualified (retry)"`, `"Meteorite Passed JD (retry)"`, `"Meteorite Passed DO (retry)"`, `"Meteorite Passed GET (retry)"`

5. In `JOBS_IN_REVIEW_GRADE_FIELD`, map each holding to the same grades key as its primary’s **incoming** grade blob (mirror `JD_READY_RETRY` → `jd_grades`):

   - `PASSED_JD_RETRY` → `jd_grades` (same as `PASSED_JD`)
   - `PASSED_DO_RETRY` → `do_grades`
   - `CULTURE_READY_RETRY` → `get_grades` (LIKE has not persisted yet; column shows prior hop — if `CULTURE_READY` has no grade-field entry today, omit rather than invent; only add keys for holdings whose primary already appears in this map or that parallel `JD_READY_RETRY`)
   - Meteorite holdings → same keys as their primary rows already use (`jd_grades` / `do_grades` / `get_grades`)

   ⚠️ **Decision:** Prefer matching the nearest existing primary’s grade-field entry. If `CULTURE_READY` is absent from `JOBS_IN_REVIEW_GRADE_FIELD` today, **do not** add a speculative LIKE grades mapping for `CULTURE_READY_RETRY` — UI column wiring is not this ticket’s AC.

6. Do **not** seed new `dispatch_task` companion rows in `database.py` / `SEED_CONFIG` — companion claim is registry-driven via `dispatch_claim_states`.

7. Verify:

   ```bash
   python3 -c "
   from src.utils.config import JOB_STATES, dispatch_claim_states
   pairs = [
       ('PASSED_JD', 'PASSED_JD_RETRY'),
       ('PASSED_DO', 'PASSED_DO_RETRY'),
       ('CULTURE_READY', 'CULTURE_READY_RETRY'),
       ('METEORITE_QUALIFIED', 'METEORITE_QUALIFIED_RETRY'),
       ('METEORITE_PASSED_JD', 'METEORITE_PASSED_JD_RETRY'),
       ('METEORITE_PASSED_DO', 'METEORITE_PASSED_DO_RETRY'),
       ('METEORITE_PASSED_GET', 'METEORITE_PASSED_GET_RETRY'),
   ]
   for primary, holding in pairs:
       assert JOB_STATES[primary]['retry_state'] == holding, primary
       assert holding in JOB_STATES
       assert dispatch_claim_states(primary, 'job') == [primary, holding], primary
       assert dispatch_claim_states(holding, 'job') == [holding], holding
   print('ok')
   "
   ```

⚠️ **Decision:** Holding names follow `{PRIMARY}_RETRY` so meteorite family stays `METEORITE_*` (overlay + `_entity_state_is_meteorite` keep working). No plain-NEW fallback.

---

## Stage 2: Completeness helper + scored/binary apply gates + debug

**Done when:** Incomplete/extra sets never call into scoring math on the happy path; batch `grade_do` (regular + meteorite state) first-strike incompleteness lands on the Stage 1 holding; complete sets including intentional `X`/`0` still score/pass/fail as today; with `debug=True`, Style D index + `|` detail names missing and unexpected vectors; `python3 -m py_compile src/core/consult.py` passes.

1. In `src/core/consult.py`, immediately above `_render_score`, add:

   ```python
   def _grade_set_vector_diff(
       rubric_criteria: list,
       grades: list,
   ) -> tuple[set, set]:
       """Return (missing_labels, unexpected_labels) using _strip_code on rubric labels vs grade vectors."""
       expected = {
           _strip_code(str(item.get("label") or "").strip())
           for item in (rubric_criteria or [])
           if item.get("label")
       }
       actual = {
           _strip_code(str(g.get("vector") or "").strip())
           for g in (grades or [])
           if isinstance(g, dict) and g.get("vector")
       }
       return expected - actual, actual - expected


   def _require_complete_grade_set(rubric_criteria: list, grades: list) -> None:
       """Raise ValueError when grades are not an exact match to live rubric labels (AST-1155)."""
       missing, extra = _grade_set_vector_diff(rubric_criteria, grades)
       if missing:
           raise ValueError(f"_render_score: missing vectors {sorted(missing)}")
       if extra:
           raise ValueError(f"_render_score: unknown vectors {sorted(extra)}")
   ```

   Keep the message prefix `_render_score: missing vectors` / `unknown vectors` so Stage 3 and existing log scrapers stay stable. Optionally refactor `_render_score` body to call `_require_complete_grade_set` instead of duplicating the set math (DRY — preferred).

2. Add a small debug helper (same file) used by apply/process paths:

   ```python
   def _debug_incomplete_grade_set(
       *,
       func: str,
       identifier: str,
       rubric_criteria: list,
       grades: list,
       dest: Optional[str],
       index: int = 1,
       total: int = 1,
   ) -> None:
       missing, extra = _grade_set_vector_diff(rubric_criteria, grades)
       logger.debug_index(
           func=func,
           index=index,
           total=total,
           identifier=identifier,
           outcome=f"incomplete grade set -> {dest or '?'}",
       )
       logger.debug_detail(
           f"missing={sorted(missing)} | unexpected={sorted(extra)} | "
           f"decoded_vectors={sorted(_strip_code(str(g.get('vector') or '')) for g in (grades or []) if isinstance(g, dict))}"
       )
   ```

   Call **only** when `debug=True` and incompleteness is detected (before transition).

3. In `_apply_render_verdict_decoded_job`, for `grading_mode == "scored"`, after rubric_criteria / threshold resolution and **before** `_render_score(...)`:

   - Call `_require_complete_grade_set(rubric_criteria, grades)`.
   - Do not change dealbreaker / threshold math for complete sets.

4. In `evaluate_jd_batch.process`, replace the bare `_render_score` informational call path: when `rubric_list` is non-empty, call `_require_complete_grade_set(rubric_list, grades)` **before** `_render_pass_fail` / score / save (incompleteness must not persist pass/fail). On raise, let `_run_batch_consult` `bad_grades` handle routing. When `debug=True`, log via `_debug_incomplete_grade_set` in the `except` path inside `process` **or** immediately before re-raise (builder’s choice — one place only).

5. In `qualify_job_listings.process`, when `rubric_list` is non-empty, call `_require_complete_grade_set(rubric_list, grades)` **before** `_render_pass_fail` / title checks / save. Remove reliance on the swallowed `_score_from_grades` try/except for incompleteness detection (that helper may remain for score-only failures **after** completeness passes, or be deleted if unused — do not leave incompleteness silently `None`).

6. In `_run_batch_consult`, when `process_fn` fails and `debug=True`, if `str(e)` contains `missing vectors` or `unknown vectors`, also emit `_debug_incomplete_grade_set` (func=`consult._run_batch_consult({task_key})`, identifier from `_consult_job_identifier`, dest from `_consult_batch_fail_dest`). Avoid double-logging if `process` already logged — prefer **one** debug emission per job (batch wrapper is enough if process re-raises without logging).

7. In `src/core/consult.py` `_INPUT_STATE_TO_TASK` (legacy map — not dispatch routing), add companions only for keys already present:

   - `PASSED_JD_RETRY` → `grade_do`
   - `PASSED_DO_RETRY` → `grade_get`

   Do **not** expand the map with meteorite keys (AST-1055: dispatch uses explicit `task_key`).

8. Verify:

   ```bash
   python3 -m py_compile src/core/consult.py
   python3 -c "
   from src.core.consult import _require_complete_grade_set, _grade_set_vector_diff
   rubric = [{'label': 'Healthcare Domain Expertise'}, {'label': 'Remote-First Requirement'}]
   grades = [{'vector': 'Remote-First Requirement', 'grade': 'A', 'confidence': 5}]
   missing, extra = _grade_set_vector_diff(rubric, grades)
   assert missing == {'Healthcare Domain Expertise'} and not extra
   try:
       _require_complete_grade_set(rubric, grades)
       raise SystemExit('expected raise')
   except ValueError as e:
       assert 'missing vectors' in str(e)
   _require_complete_grade_set(rubric, grades + [{'vector': 'Healthcare Domain Expertise', 'grade': 'X', 'confidence': 0}])
   print('ok')
   "
   ```

⚠️ **Decision:** Completeness is exact set equality on stripped labels — intentional `X`/`0` rows count as present. Empty `rubric_criteria` skips the gate (same as today’s evaluate_jd `if rubric_list` guard); missing rubric artifact on scored apply still raises the existing `Candidate missing rubric artifact` error (infra — technical via `_fail` / error_state).

---

## Stage 3: `render_verdict` incompleteness routing + prefilter gate

**Done when:** Single-job `render_verdict` incompleteness transitions to the entity’s retry holding (not `FAILED_TECHNICAL_*` on first strike); prefilter incompleteness uses `_prefilter_fail` retryable path; genuine missing-company / prep failures still use technical/error; `python3 -m py_compile src/core/consult.py src/core/roster.py` passes.

1. In `consult.render_verdict`, change the `except ValueError as e` around `_apply_render_verdict_decoded_job`:

   - Keep re-raise for `Unknown grading_mode:`.
   - If `str(e)` contains `missing vectors` or `unknown vectors`:
     - `dest = _consult_batch_fail_dest(job.get("state"), error_state)`
     - If `debug`: `_debug_incomplete_grade_set(...)` with grades from the decoded row when available (if the exception happened before grades were bound, log `missing`/`unexpected` from the exception string and `grades=[]`).
     - If `dest`: `_transition_job_state_for_task(agent_task, [astral_job_id], dest)`
     - Return `{"success": False, "to_state": dest, "error": str(e)}` — **do not** call `_fail` (which always uses `error_state`).
   - All other `ValueError`s: keep existing `_fail(es)` behavior.

2. In `roster._apply_prefilter_decoded_company_outcome`, after grades/rubric hydration and **before** `_render_pass_fail` / `_render_score` / persist:

   - If `grades` and `rubric_list`: call `consult._require_complete_grade_set(rubric_list, grades)`.
   - On `ValueError` for missing/unknown vectors: do **not** transition to pass/fail inside this function — re-raise so the caller’s existing `except` → `_prefilter_fail(..., error=str(e))` path runs (retryable when `api_result is None`). If the current caller does not catch apply-outcome errors, wrap the completeness call in this function and invoke `_prefilter_fail` then `return` the fail dict’s state / raise a dedicated signal — **inspect the live caller** (`prefilter_company` / batch) and use the path that already routes decode/apply failures through `_prefilter_fail` without inventing a third router.
   - When `debug=True`, emit Style D incomplete detail (roster func name + `short_name`) before fail routing.

3. Confirm (read-only during build): prep failures in `_consult_scored_dispatch_batch_encoded` (no company / no live_content) still transition with `error_state` directly — **do not** change those branches to retry holdings.

4. Verify:

   ```bash
   python3 -m py_compile src/core/consult.py src/core/roster.py
   python3 -c "
   from src.core import consult as c
   from src.utils.config import TASK_CONFIG, JOB_STATES
   assert c._consult_batch_fail_dest('METEORITE_PASSED_JD', TASK_CONFIG['grade_do']['error_state']) == 'METEORITE_PASSED_JD_RETRY'
   assert c._consult_batch_fail_dest('METEORITE_PASSED_JD_RETRY', 'METEORITE_FAILED_TECHNICAL_DO') == 'METEORITE_FAILED_TECHNICAL_DO'
   assert c._consult_batch_fail_dest('PASSED_JD', TASK_CONFIG['grade_do']['error_state']) == 'PASSED_JD_RETRY'
   # meteorite overlay error_state still used on second strike
   overlay_err = 'METEORITE_FAILED_TECHNICAL_DO'
   assert c._consult_batch_fail_dest('METEORITE_PASSED_JD_RETRY', overlay_err) == overlay_err
   print('ok')
   "
   ```

⚠️ **Decision:** Message-substring routing for incompleteness is intentional and narrow (`missing vectors` / `unknown vectors` only). Do not classify confidence/`Candidate missing rubric` errors as incompleteness.

---

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each tip to `origin/sub/AST-1150/AST-1155-incomplete-grades-retry-holding-never-technical-fail`.
- Do not edit files outside the Files Changed table.
- If a step is ambiguous, contradicts the codebase, or fails when followed literally — stop and comment on **parent AST-1150** with the Stage N blocked template. No improvisation.
- After Stage 3: hand-confirm with a local replay mental checklist — meteorite `grade_do` job in `METEORITE_PASSED_JD` with one omitted vector → `METEORITE_PASSED_JD_RETRY` (Avail > 0 on meteorite Do row); complete grade set with `X0` still dealbreaks/scores as today; second incomplete attempt from the holding → `METEORITE_FAILED_TECHNICAL_DO`.

---

## Self-Assessment

**Scope:** `Single-Component` — `JOB_STATES` retry registry plus consult/roster apply routing for incomplete grade sets; no prompt catalog and no Skipped UI.

**Conf:** `high` — root cause is the missing `retry_state` on Do/Get/Like (+ meteorite) triggers; AST-642 / AST-898 patterns already define the fix shape; live call sites for completeness are enumerated.

**Risk:** `HIGH` — wrong prior_states or holding names would block transitions or mis-claim batches across every rubric hop; a too-broad `render_verdict` except change could turn real infra failures into retry loops.

---

## Self-review vs `ASTRAL_CODE_RULES.md`

| Section | Check |
|---------|--------|
| §1.3 DRY | One `_grade_set_vector_diff` / `_require_complete_grade_set`; `_render_score` reuses it |
| §2.1 config | Retry destinations live in `JOB_STATES.retry_state`; no hard-coded NEW/technical remap in process_fn |
| §2.3.1 grade-vector-validation | Live-rubric completeness enforced at consult apply (TASK_CONFIG `vectors` absent on grade_*); omission rejected, not invented |
| §2.3.2 confidence-bounds | Unchanged; `X`/`0` still valid complete rows |
| §2.4 batch | Incompleteness stays per-entity inside claim→process→release via existing `bad_grades` + `_consult_batch_fail_dest` |
| §2.6 state machine | New holdings registered with priors; companion claim via `dispatch_claim_states` |
| §1.5.1 debug-contract-gated | Incomplete detail only when `debug=True`; Style D index + `\|` detail |
| §3.3 imports | roster imports consult helper (already imports `_render_score`); no new data-layer imports |
| §3.5 naming | `{PRIMARY}_RETRY` holdings; helpers `_grade_set_*` / `_require_complete_grade_set` |

**Conflicts:** None. Sibling AST-1154 must not be required to land first for this routing fix (prompts reduce omission rate; this ticket makes omission non-technical).

---

## Review stub (build)

**Publish ref:** `sub/AST-1150/AST-1155-incomplete-grades-retry-holding-never-technical-fail`  
**Tip:** `47974f81`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `64ce12d2` | `JOB_STATES` retry holdings for graded triggers + In Review maps |
| 2 | `4d735e94` | Completeness gate before score + Style D incomplete debug |
| 3 | `47974f81` | `render_verdict` + prefilter incomplete → retry holding |

---

## Radia review

**[code-rubric] revision=1** · **Publish ref:** `e6698dd865f900aca45831b8cd9ce82badcbfae9` · **Overall:** DISCUSS

Full active statute set (65) scored in-session — 0 fix-now. Live-ran all three plan verification scripts against the actual publish tip (not just prose): Stage 1 `retry_state`/`dispatch_claim_states` pairs, Stage 2 `_require_complete_grade_set` (incl. `X`/`0` counts as present), Stage 3 `_consult_batch_fail_dest` first/second-strike routing incl. meteorite overlay. All three green. Confirmed the actual repro path (`_consult_scored_dispatch_batch_encoded` → `_apply_render_verdict_decoded_job` → raise → `_run_batch_consult` → `_consult_batch_fail_dest`) now resolves correctly now that Stage 1 supplies the missing registry entries.

**discuss — `astral.dispatch.run-next-is-chain-authority`** and **discuss — `astral.standards.no-hardcoded-sets`.** Both carried from Joan's plan-rubric verdict and confirmed unchanged in the shipped diff: `_INPUT_STATE_TO_TASK` legacy-map extension (non-dispatch-routing, explicitly scoped) and `render_verdict`'s exception-message-substring routing (`"missing vectors"` / `"unknown vectors"`) for the incompleteness branch. Both non-blocking, engineer's call exercised as Joan anticipated. Neither is fix-now.

**Notes:** accepted-risk carried from Joan — any `process_fn` exception on the seven graded triggers now first-strikes to retry holding, not just incomplete grades (established AST-642 behavior); infra-failure paths (missing company, prep failure) stay on `error_state`, confirmed unchanged. 3 trivially-clean C4 stragglers (plan-doc + test-tree diff inclusion vs Files-Changed-table convention) — not scope creep.

— Radia

---

## Resolution

**2026-08-03** · resolve-child after Radia DISCUSS (`a220ab12` docs tip; code tip was `e6698dd8`).

| Finding | Disposition |
|---------|-------------|
| discuss `astral.standards.no-hardcoded-sets` (substring routing) | **Addressed in product** — `_require_complete_grade_set` raises `IncompleteGradeSetError` (subclass of `ValueError`); `render_verdict` and batch debug catch by type. Message text kept for logs/tests. |
| discuss `astral.dispatch.run-next-is-chain-authority` (`_INPUT_STATE_TO_TASK`) | **Accepted as-is** — legacy non-dispatch map; only the two planned companions; meteorite stays on explicit `task_key`. |
| Joan/Radia note: any `process_fn` failure first-strikes to retry | **Documented** — intentional AST-642 behavior once `retry_state` exists; infra paths outside `process_fn` still use `error_state`. |

No fix-now items. No test-tree edits.

---

## Bug: AST-1996 — Isolate malformed encoded grade lines → per-entity retry, not hop error

**Linear:** [AST-1996](https://linear.app/astralcareermatch/issue/AST-1996) · **Mini-parent:** [AST-1884](https://linear.app/astralcareermatch/issue/AST-1884) · **Publish ref:** `sub/AST-1884/AST-1996-decode-line-retry` · **Project:** Astral Dispatcher

**Canon (resolved @ corpus `e1f2699fad`):** `patt.task.dispatch-retry` (read — invalid response for an entity → retry or error by *current* state; a failure never persists in state), `patt.entity.batch-processing` (read — process only claimed rows; release unchanged). Id-only for make-fix: `astral.batch.claim-process-release`, `stat.logging.warning`, `stat.logging.error`, `stat.logging.debug`.

### As-is

`evaluate_meteorite` / `evaluate_jd` (`output_type: "grades_encoded"`, grades-only) decode every line of the batch in one `_decode_payload` call. When **any** line carries a token that fails `_GRADE_SEG` (e.g. `DEC35` — two confidence digits), that token lands in `meta`, and `_decode_payload` raises `ValueError: unexpected trailing content in grades-only line` for the **whole payload**. `do_task` returns `success=False`, so `_run_batch_consult` sends **every** claimed job through `_transition_batch_consult_failures` — clean lines are thrown away with the bad one, and every job in the batch burns one of its two strikes.

Second path, same class: `_should_decode_as_encoded_line` inspects only the **first** non-empty line. If that line has *no* valid segment at all (e.g. `000|DEC35|ECC35`, no `X0` to match), the payload skips the decoder, falls into `_job_from_letter_pipe`, and comes back as one job with no `astral_job_id` → schema validation fails → whole batch to fail dest again.

### To-be

A format slip on one encoded line is a per-entity miss: that line's job routes through the existing `_consult_batch_fail_dest` (first strike → `*_RETRY` holding, already-in-holding → `error_state`), and every well-formed line in the same response still decodes, scores, and transitions normally. No coercion of the bad token, no `_GRADE_SEG` widening.

### Repro

Fixture (no DB — `batch_entities` + raw `agent_payload`, as `_run_batch_consult` passes them):

```python
from src.core.consult import _normalize_rubric_task_response
from src.utils.config import TASK_CONFIG
cfg = TASK_CONFIG["evaluate_meteorite"]
ents = [{"astral_job_id": "J0", "state": "METEORITE_QUALIFIED"},
        {"astral_job_id": "J1", "state": "METEORITE_QUALIFIED"}]
# A — malformed line carries a valid X0 segment (the AST-1884 production shape)
_normalize_rubric_task_response("evaluate_meteorite", cfg,
    {"agent_payload": "000|DEC35|ECC35|ORX0\n001|DEC3|ECC3|ORX0"}, {"batch_entities": ents})
# today: ValueError unexpected trailing content … '000|DEC35|ECC35|ORX0'  (J1 lost)
# B — malformed line is first and has no valid segment at all
_normalize_rubric_task_response("evaluate_meteorite", cfg,
    {"agent_payload": "000|DEC35|ECC35\n001|DEC3|ECC3"}, {"batch_entities": ents})
# today: {'jobs': [{'grades': [], 'possible_job_links': []}]}  — no astral_job_id, J1 lost
```

Production log (AST-1884): `000|DEC35|ECC35|EFA45|…|ORX0|…` on a batch of 1 → `METEORITE_ERROR_EVALUATE_JD`.

### Root cause

1. `src/core/agent.py::_decode_payload` treats a per-line format error (grades-only trailing content) as a payload-level failure — `raise` instead of recording the line and continuing. The decode loop already has a per-line skip precedent (out-of-range `pos` → `continue`), but the trailing-content branch never adopted it.
2. `src/core/consult.py::_should_decode_as_encoded_line` routes on the first line only, so a fully malformed first line misroutes the whole payload away from the decoder.

**Why the AST-1884 job hit `*_ERROR_*` and not the holding:** `METEORITE_QUALIFIED` already has `retry_state` → `METEORITE_QUALIFIED_RETRY` (AST-1155; resolved via `retry_of` since AST-1806), and the whole-hop failure path already routes per entity through `_consult_batch_fail_dest`. The logged run shows `error:1` and an `[ERROR]` fail-dest line — since AST-1839 (2026-09-28) retry-routed jobs log WARNING and are subtracted from `total_errors`. So that job was almost certainly already in `METEORITE_QUALIFIED_RETRY` (second strike — DeepSeek repeated the slip), and `METEORITE_ERROR_EVALUATE_JD` was the correct AST-1155 terminal. The real defect is the **batch blast radius** (and the lost per-line reason), not a missing holding. **No `src/utils/config.py` change is needed** — `evaluate_meteorite` (`METEORITE_QUALIFIED`) and `evaluate_jd` (`JD_READY`) both already resolve to a retry holding:

```text
_consult_batch_fail_dest('METEORITE_QUALIFIED', 'METEORITE_ERROR_EVALUATE_JD')       -> METEORITE_QUALIFIED_RETRY
_consult_batch_fail_dest('METEORITE_QUALIFIED_RETRY', 'METEORITE_ERROR_EVALUATE_JD') -> METEORITE_ERROR_EVALUATE_JD
_consult_batch_fail_dest('JD_READY', 'ERROR_EVALUATE_JD')                            -> JD_READY_RETRY
```

### Proposed change

Two files, three edits. One `code(AST-1996)` commit.

**1. `src/core/agent.py::_decode_payload` — isolate the bad line (job/company decode loop, not the vet branch).**

- Before the loop, add `decode_failures: List[Dict[str, Any]] = []`.
- Replace the trailing-content `raise` with a record + `continue`:

  ```python
  if meta and not with_meta and not with_notes:
      # One malformed line must not sink the batch — caller routes this entity retry/error (AST-1996).
      decode_failures.append({
          id_key: batch_entities[pos][id_key],
          "pos": pos,
          "reason": f"[{task_key}] unexpected trailing content in grades-only line: {line!r}",
      })
      continue
  ```

  The reason string is the exact text of today's `ValueError` so existing log greps keep matching.
- Return: build `out = {array_key: result_rows}`; add `out["decode_failures"] = decode_failures` **only when non-empty** (clean payloads keep today's exact `{"jobs": [...]}` shape).
- Docstring: replace "trailing non-grade content raises ValueError for grades-only types" with "trailing non-grade content on a grades-only line is recorded in `decode_failures` (id, pos, reason) and the line is skipped; other per-line errors still raise".
- **Unchanged (still raise for the whole payload):** bad position field, duplicate vector code (AST-1513), X-with-nonzero / non-X-out-of-1–5 confidence, the entire `grades_encoded_vet_meta` branch. Only the trailing-content branch changes. `_GRADE_SEG` untouched.

**2. `src/core/consult.py::_should_decode_as_encoded_line` — scan every line, not just the first.**

Change the single `line = next(...)` lookup into a loop over all non-empty lines; return `True` on the first `_GRADE_SEG` match in any line, `False` after all lines. Body per line is unchanged (strip leading `\d{1,3}` pos field, normalize `" -:"`, match). Single-letter letter-pipe payloads still never match a 4-char segment, so their routing is unchanged. If **no** line anywhere has a valid segment, routing is unchanged (letter-pipe → schema failure → whole batch to fail dest — correct, every line is bad).

`_normalize_rubric_task_response` itself needs no edit — it already returns the decoded dict as-is, so `decode_failures` passes through to `do_task`'s `parsed_response`. `_validate_response_schema` ignores unknown keys and accepts an empty `jobs` list, so an all-lines-failed payload (`{"jobs": [], "decode_failures": [...]}`) still reaches `_run_batch_consult`.

**3. `src/core/consult.py::_run_batch_consult` — route decode failures per entity.**

Immediately after `missing = sent_ids - received_ids` / `fabricated = …`:

```python
# Per-line decode slips (AST-1996) — a clean row for the same entity wins.
decode_failed = {
    f["astral_job_id"]: f["reason"]
    for f in (parsed.get("decode_failures") or [])
    if f.get("astral_job_id") and f["astral_job_id"] not in received_ids
}
missing -= decode_failed.keys()
```

Then, after the existing `retried = 0` and before the existing `if missing:` transition block:

```python
for aid, reason in decode_failed.items():
    retried += _transition_batch_consult_failures(
        task_key, [input_by_id[aid]], error_state, reason=f"decode: {reason}",
    )
```

One call per entity so each fail-dest log line carries its own malformed line; `_transition_batch_consult_failures` → `_log_fail_dest` already emits WARNING on a retry holding / ERROR on terminal (AST-1839) — **no new log calls**.

Return dict: add `"decode_failed": sorted(decode_failed) if decode_failed else None`; `success` becomes `not fabricated and not bad_grades and not decode_failed`; when non-empty append `f"decode failed on {len(decode_failed)} IDs: {sorted(decode_failed)}"` to `errors`. `run_consult_task`'s `errors = total - passed - failed - retried` then counts a first-strike decode failure as retried (0 errors) and a second-strike one as 1 error — no dispatcher change.

⚠️ **Decision — first strike vs second strike.** AC1 "lands in its retry holding state" is the **first-strike** outcome. An entity already in `*_RETRY` that slips again goes to `error_state` — unchanged `patt.task.dispatch-retry` / AST-1155 contract (one retry, no loop). A batch-of-1 replay of the exact AST-1884 log from `METEORITE_QUALIFIED_RETRY` will still land `METEORITE_ERROR_EVALUATE_JD`; that is correct, not a regression.

⚠️ **Decision — clean row wins.** If a response carries both a malformed line and a clean line for the same `pos`, the clean row is processed and the decode failure is ignored (the entity received a valid grade set; `process_fn`'s `_require_complete_grade_set` still guards it).

⚠️ **Decision — no `src/utils/config.py` edit.** Scope allowed one only if the retry holding was missing; it isn't (see Root cause).

### Blast radius

- **`_decode_payload` callers:** `consult._normalize_rubric_task_response` (rubric-encoded `do_task` path — the fix target); `agent.do_task` non-rubric `_encoded` branch and `api_admin` ad-hoc test hydrate. The changed branch is reachable only for plain `grades_encoded` — today exactly `evaluate_jd` and `evaluate_meteorite`. `grades_encoded_notes` (grade_do/get/like/meteorite_like), `grades_encoded_meta` (qualify), `grades_encoded_prefilter_links` (company prefilter — roster) and `grades_encoded_vet_meta` never enter it. Admin ad-hoc test on a malformed line now shows partial `jobs` + `decode_failures` instead of `{"error": …}` — read-only debug view, acceptable, no edit.
- **`_should_decode_as_encoded_line`:** called only from `_normalize_rubric_task_response` — shared by every rubric-encoded consult task and the prefilter company path. Scanning all lines can only flip a payload *into* the decoder when some later line has a valid segment; letter-pipe single-letter grades cannot match.
- **`_run_batch_consult` callers:** `evaluate_jd_batch` / `evaluate_meteorite_batch`, `qualify_job_listings`, `grade_*_batch`, `_consult_scored_dispatch_batch_encoded`. Non-`grades_encoded` tasks never produce `decode_failures`, so `decode_failed` is empty and behavior is byte-identical.
- **Roster prefilter batch:** untouched (never produces `decode_failures`).
- **Tests that assume today's behavior (Betty's tree — make-fix does not edit):** `tests/component/core/test_agent.py::…::test_rejects_bad_positions_and_trailing_meta` asserts `_decode_payload("task", "grades", "0|CRA2|extra", …)` raises `unexpected trailing content` — **flips** (now returns `{"jobs": [], "decode_failures": [{astral_job_id: "job-1", pos: 0, reason: …}]}`); its bad-position and X-confidence asserts still hold. `test_should_decode_as_encoded_line_routing` uses single-line inputs only — still green. fix-board / qa-fix own the rewrite.

### What must still hold

- **AST-1155 AC1–AC3:** incomplete/extra vector sets still raise `IncompleteGradeSetError` in `process_fn` and route first strike → holding, second → technical; complete sets incl. `X`/`0` score as before; Style D incomplete debug unchanged.
- **`patt.task.dispatch-retry`:** exactly one retry; routing decided by current state via `_consult_batch_fail_dest`; a decode-failed entity always transitions (never left in its trigger state).
- **`_GRADE_SEG` strictness (AST-357 / AST-483):** regex unchanged; `DEC35` is never coerced to `DEC3`/`DEC5`.
- **Duplicate-code rejection (AST-1513)** and confidence-bound errors still fail the whole payload — out of scope here.
- **Clean payload shape:** no `decode_failures` key unless a line failed.
- **Envelope / provider failures** (`do_task` `success=False`, provider balance hold) keep their existing whole-batch handling.
- **Claim/release:** no change to claim, batch_id, or `finally` release.


### Joan fix-board — AST-1996

```
[board-joan]  CANON: OK

context_tokens≈12000
```

```text
AST-1996 board-joan done — CANON: OK.
```

**Triage (read-only):** Against the AST-1996 plan-fix patch and the six ids at corpus `e1f2699fad` (`patt.task.dispatch-retry`, `patt.entity.batch-processing`, `astral.batch.claim-process-release`, `stat.logging.warning` / `error` / `debug`), the proposed change **implements** dispatch-retry per entity (malformed line → `_consult_batch_fail_dest`, clean lines still process) without widening `_GRADE_SEG`, without claim/release edits, and reusing `_log_fail_dest` for WARNING/ERROR. No active directive requires payload-level `ValueError` on trailing grades-only content or forbids a `decode_failures` side channel; that behavior lived in product/tests, not canon. **F3 (`validate-plan` fix mode) not indicated** from this board pass.
```
