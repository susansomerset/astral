<!-- linear-archive: AST-1054 archived 2026-08-07 -->

## Linear archive (AST-1054)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1054/meteorite-gdl-dispatch-rows-score-floor-0-processing-meteorites  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1052 — Processing meteorites  
**Blocked by / blocks / related:** parent: AST-1052

### Description

## What this implements

Owns new dispatch_task rows that call the same `evaluate_jd` / `grade_do` / `grade_get` tasks with meteorite input states and `score_floor` = 0, plus dispatch wiring for `meteorite_like` @ **METEORITE_PASSED_GET** and the meteorite upshot trigger (`meteorite_upshot` @ **METEORITE_PASSED_LIKE**). After #1. Does **not** author the agent_task prompt text or TASK_CONFIG twins (sibling 3).

## Acceptance criteria

- [X] 2. New dispatch_task rows claim meteorite GDL hops for `evaluate_jd` / `grade_do` / `grade_get` at the meteorite input states with `score_floor` = 0; those hops do not exclude jobs for low `latest_score`.
- [X] 3. With `debug=True` on meteorite GDL processing, Style D index + `|` detail is present; with `debug=False`, no new debug-contract lines from those paths.

## Boundaries

Does **not** own JOB_STATES registry (sibling 1), agent_task prompt bodies / TASK_CONFIG twins / twin consult routing / RECOMMENDED priors (sibling 3), Create retarget (sibling 4), or Recommended section (sibling 5).

## In scope

- [X] `pattern.batch.entity-claim-process-release`
- [X] `astral.config.pass-threshold-vs-score-floor`
- [X] `astral.batch.claim-process-release`
- [X] `astral.standards.debug-contract-gated`
- [X] `astral.standards.no-hardcoded-sets`
- [X] `astral.config.config-source-of-truth` — `METEORITE_DISPATCH_TASKS` / outcome overlay / score-gated meteorite triggers in config
- [X] `astral.batch.batch-id-first` — provision inserts rows only; claim still batch_id-first via existing dispatcher

## Considered but excluded

- [X] `pattern.state.entity-state-transitions` / `astral.state.job-prior-states-enforced` — JOB_STATES owned by AST-1053
- [X] `pattern.config.config-block` for twin prompts — AST-1055 owns `meteorite_like` / `meteorite_upshot` TASK_CONFIG + agent_task bodies
- [X] `astral.layers.import-direction` UI — no Recommended / Create UI on this ticket (AST-1056/1057)
- [X] `astral.standards.database-header-inventory` — no new tables

## Notes for planning

After AST-1053. Same underlying GDL tasks; new dispatch rows only. Twin dispatch rows insert when AST-1055 TASK_CONFIG keys exist (`skipped_missing_config` until then).

## Git branch (authoritative)

`origin/sub/AST-1052/AST-1054-meteorite-gdl-dispatch-rows-score-floor-0`

### Comments

#### radia — 2026-07-29T22:19:38.532Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1054
**Publish ref:** `c5b816eda0c0ef8c4f0a5ca395fb974841766df7` (`origin/sub/AST-1052/AST-1054-meteorite-gdl-dispatch-rows-score-floor-0`)
**Overall:** DISCUSS

**Diff:** `origin/dev...origin/sub/AST-1052/AST-1054-meteorite-gdl-dispatch-rows-score-floor-0` — layers `{core, docs, utils}`. Tip restored to clean `f195665b` lineage + docs review (prior polluted tip cleared by Chuckles).

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| `astral.agent.confidence-bounds` | scoped | conforms | No confidence math changes |
| `astral.agent.do-task-delegation` | scoped | conforms | Reuses existing GDL tasks; no new do_task shape |
| `astral.agent.grade-vector-validation` | scoped | conforms | Rubrics unchanged |
| `astral.batch.batch-id-first` | scoped | conforms | Provision inserts only; claim via existing dispatcher |
| `astral.batch.batch-id-format` | scoped | conforms | No batch_id format change |
| `astral.batch.claim-process-release` | scoped | conforms | Claim→consult→release unchanged; new rows only |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | No agent_data latest-ref edits |
| `astral.config.config-source-of-truth` | scoped | conforms | METEORITE_DISPATCH_TASKS + outcome map + gated states in config |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | score_floor 0 on gated rows; pass_threshold untouched |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | No secrets/env |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths miss (['artifacts/**', 'scripts/spikes/**']) |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | Plan docs under docs/features/; no spikes |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | Single AST-1054 plan (+ stacked 1053 plan in tip) |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test()/merge-tests; engineer code() owns src+features |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | test() owns tests/bible; engineer code() product only |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | No external I/O |
| `astral.layers.import-direction` | scoped | conforms | utils config ← core consult/dispatcher |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers miss (['scripts']); paths miss (['scripts/**']) |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | No UI edits |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | No coat-check path changes |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | Overlay in render_verdict + batch consult |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers miss (['ui']); paths miss (['src/ui/**']) |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | No data-layer logging |
| `astral.standards.database-header-inventory` | scoped | not-applicable | layers miss (['data']); paths miss (['src/data/**']) |
| `astral.standards.debug-contract-gated` | scoped | conforms | Reuses existing debug= gates; no new ungated Style D |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Mirrors AST-972 ensure/provision; thin overlay helper |
| `astral.standards.in-scope-only` | scoped | conforms | No twin prompts/Create/Recommended UI |
| `astral.standards.logging-via-utils` | scoped | conforms | Scheduler provision via existing _sched_log |
| `astral.standards.no-cross-contamination` | scoped | conforms | METEORITE_ prefix overlay; vetted path untouched |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | Row specs + outcome map in config |
| `astral.standards.public-then-helpers` | scoped | conforms | Public ensure/provision + private overlay helpers |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | No utils→data |
| `astral.state.core-decides-transitions` | scoped | conforms | Overlay outcomes applied in core consult |
| `astral.state.job-prior-states-enforced` | scoped | conforms | Overlay targets AST-1053 JOB_STATES; asserts membership |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | No run_next daisy-chain |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers miss (['ui']); paths miss (['src/ui/frontend/**']) |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers miss (['ui']); paths miss (['src/ui/**']) |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | config.py path only; no worker change |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | Single merge-tests(AST-1054) onto tip |
| `orch.git.commit-vocabulary` | universal | conforms | docs/code/test/merge-tests vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | Work on sub/* only |
| `orch.git.ftr-sub-topology` | universal | conforms | sub/AST-1052/AST-1054-… |
| `orch.git.merge-on-checkout` | universal | conforms | No conflicting checkout rewrite |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | No rewrite ops |
| `orch.git.no-dev-agent-branches` | universal | conforms | Ticket sub publish-ref |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | astral-AST-1052 |
| `orch.git.three-permanent-branches` | universal | conforms | No new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | score_floor None entry hop documented; locked in plan |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–3 match tip; twin skip until 1055 |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Meteorite child |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | No canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Betty owns tests/bible |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Assignee Hedy |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Assignee remains Hedy |
| `orch.roles.pre-commit-path-bans` | universal | conforms | Role-appropriate paths per vocabulary |

## Pattern conformance

- `pattern.batch.entity-claim-process-release` — conforms (provision inserts rows; claim still existing dispatcher path)
- Cited statutes covered in Statutes checked

## Plan adherence

Stages 1–3 match tip: `METEORITE_DISPATCH_TASKS` + outcome map + `PASSED_SCORE_GATED_STATES` meteorite hops; consult `METEORITE_` overlay; ensure/provision on scheduler start. Twin rows `skipped_missing_config` until AST-1055. No TASK_CONFIG twin shells / agent_task / Create / Recommended UI. Self-Assessment Single-Component matches.

## Findings

### fix-now
(none)

### discuss
1. **straggler ×3** — Joan excluded at plan time; in-scope on three-dot vs `origin/dev` (all substance **conforms**):
   - `astral.debug.spikes-under-debug-dir`
   - `astral.docs.features-single-file-per-ticket`
   - `astral.git.engineer-test-tree-ban`

### advisory
(none)

### What’s solid
- score_floor 0 gated hops; entry `METEORITE_NEW` ungated; overlay keeps meteorite outcomes off vetted chain; Style D reuses existing `debug=` gates.

### Recommended actions
- Hedy: acknowledge stragglers → resolve-child → User Testing.

**Notes:** Joan plan-rubric APPROVED. Docs append @ `c5b816ed`. Prior `[review-handoff]` pollution cleared.

context_tokens≈32000

#### chuckles — 2026-07-29T22:18:23.137Z
[review-handoff] cleared — Chuckles restored `origin/sub/AST-1052/AST-1054-meteorite-gdl-dispatch-rows-score-floor-0` to `f195665b` (force-with-lease). Re-spawning Radia review-child.

— Chuckles

#### radia — 2026-07-29T22:17:41.421Z
[review-handoff] Radia — **blocked**; leaving **Tests Passed** (no Review Posted).

**What happened:** Mid `docs(AST-1054)` publish, the epic worktree branch drifted (local tip was on the AST-1055 line). A merge of `origin/sub/.../AST-1054-…` into that tip was then pushed to `origin/sub/AST-1052/AST-1054-meteorite-gdl-dispatch-rows-score-floor-0`.

**Damage:** Publish-ref tip is now `c07bc931` and includes AST-1055 product history (`meteorite_like` TASK_CONFIG, `agent_task.json`, etc.) that this child must not own. Pre-pollution tip was `f195665b` (merge-tests + 1054 code only).

**Radia review (substance, not posted as C7 gate):** Stages 1–3 on the *clean* tip looked good — DISCUSS only for Joan straggler ×3 (spikes / features-single-file / engineer-test-tree-ban), no fix-now. Cannot complete C7 against the polluted tip.

**Needs force-with-lease restore (Susan/Chuckles):**
```bash
git fetch origin
git push origin f195665b:sub/AST-1052/AST-1054-meteorite-gdl-dispatch-rows-score-floor-0 --force-with-lease
```
Then re-run `review-child` for AST-1054 (docs append + Review Posted).

Assignee left Hedy. Radia will not force-push without explicit approval.

#### betty — 2026-07-29T22:14:15.852Z
## QA test manifest (AST-1054)

**Publish:** `origin/sub/AST-1052/AST-1054-meteorite-gdl-dispatch-rows-score-floor-0` @ `f195665b` (`merge-tests` of `origin/tests` `bc352fb0`)

### Gaps (new)
1. `tests/component/utils/test_config.py::TestAst1054MeteoriteGdlDispatch` — `METEORITE_DISPATCH_TASKS` floors, overlay JOB_STATES, score-floor gating, twin trigger defaults
2. `tests/component/core/test_consult.py::TestAst1054MeteoriteGdlOutcomeOverlay` — meteorite entity overlay vs vetted-company outcomes
3. `tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision` — ensure/provision/scheduler; twins `skipped_missing_config` until TASK_CONFIG present

### Broken / obsolete (revised)
4. `TestAst1053MeteoriteGdlJobStates::test_non_meteorite_gdl_and_recommended_untouched` — ungated set only (`METEORITE_NEW` / `METEORITE_PASSED_LIKE_RETRY` / fails); pass hops gated by this ticket
5. `TestAst972CandidateStageDispatch::test_start_scheduler_invokes_stage_provision` — stubs `provision_meteorite_dispatch_tasks`

### Existing coverage
6. `TestRenderPassFail` — non-meteorite `_render_pass_fail` unchanged
7. `TestScheduler` — scheduler start still green with meteorite provision try-path

### Integration
none

### Narrowed run
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1053MeteoriteGdlJobStates \
  tests/component/utils/test_config.py::TestAst1054MeteoriteGdlDispatch \
  tests/component/core/test_consult.py::TestAst1054MeteoriteGdlOutcomeOverlay \
  tests/component/core/test_consult.py::TestRenderPassFail \
  tests/component/core/test_dispatcher.py::TestAst1054MeteoriteDispatchProvision \
  tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch::test_start_scheduler_invokes_stage_provision \
  tests/component/core/test_dispatcher.py::TestScheduler \
  -q
```
Betty local: **25 passed**.

### Bible shasums (`git show origin/sub/…:<path> | shasum -a 256`)
- `docs/test-bible/utils/config.md` `7e0f3840692ccffc826f0e9f9fcb6792f592b2a00ec5b5089133b1296094a7d6`
- `docs/test-bible/core/dispatcher.md` `043eeef0ea5b95e8f8e764067cf972cffc1a18e8565e01ba7ac6dc4dff0c1165`
- `docs/test-bible/core/consult.md` `f273e1d68d78f3877f626269fa7c8de94e8013d37ad164fac37d7174d175b07e`

— Betty

#### joan — 2026-07-29T22:01:49.727Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1054
**Overall:** APPROVED
**Plan tip:** `467bbe89230aa922c4a81302dd79d2df1419d815` @ `origin/sub/AST-1052/AST-1054-meteorite-gdl-dispatch-rows-score-floor-0`
**Layers:** utils, core | **Change types:** modify

## Traceability

### Parent AC → plan stages

| Parent AC | Mapping |
|-----------|---------|
| AC1 METEORITE_* JOB_STATES | N/A — boundary (AST-1053) |
| AC2 dispatch rows score_floor 0 for evaluate_jd/grade_do/grade_get | Stages 1 + 3 (`METEORITE_DISPATCH_TASKS`; gated hops `0.0`; entry `METEORITE_NEW` ungated/`None` mirrors `JD_READY`) |
| AC3 no CULTURE; meteorite_like @ METEORITE_PASSED_GET | Stage 1 dispatch wiring + trigger default; prompts/TASK_CONFIG N/A (AST-1055) |
| AC4 meteorite upshot after LIKE | Stage 1 `meteorite_upshot` @ `METEORITE_PASSED_LIKE` wiring; prompts N/A (AST-1055) |
| AC5 Recommended Meteorites | N/A — AST-1057 |
| AC6 Create → METEORITE_NEW | N/A — AST-1056 |
| AC7 fail/tech-fail + non-meteorite unchanged | Stage 2 overlay fail/error states; Stage 3 leaves vetted rows/culture alone |
| AC8 Style D debug gated | Stage 2 — reuse existing `debug` paths; no new ungated contract lines |

### Child AC → plan stages

| Child AC | Stages |
|----------|--------|
| AC2 meteorite GDL hops score_floor 0; no low-score exclusion | 1, 3 |
| AC3 debug Style D gated | 2 |

### Plan stages → definition

| Stage | Definition |
|-------|------------|
| 1 Config specs/overlay/gated states/twin triggers | Purpose parallel track + Functional dispatch score_floor 0 + like/upshot triggers; config SoT |
| 2 Consult METEORITE_ overlay | Shared GDL keys must land on METEORITE_* (not vetted chain); debug contract |
| 3 Dispatcher ensure/provision | claim-process-release shape; batch_id-first claim unchanged; twin skip until AST-1055 |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | Plan excludes test-tree edits (Betty later) |
| orch.git.commit-vocabulary | conforms | No commit authored in plan path |
| orch.git.flow-direction-inviolable | conforms | Publish ref is sub under AST-1052 |
| orch.git.ftr-sub-topology | conforms | Child publish ref matches Git table |
| orch.git.merge-on-checkout | conforms | No alternate merge strategy proposed |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite/force ops |
| orch.git.no-dev-agent-branches | conforms | Uses sub/* publish ref |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree AST-1052 |
| orch.git.three-permanent-branches | conforms | No permanent-branch mutation |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions documented; no Archie product gap |
| orch.pipeline.plan-is-bible | conforms | Stages are implementation bible |
| orch.pipeline.project-scoped-queues | conforms | Meteorite project child only |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validation path |
| orch.roles.archie-approves-statutes | conforms | No statute authorship |
| orch.roles.betty-owns-test-tree | conforms | Explicit Betty/tests out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | N/A to plan content |
| orch.roles.engineer-assignee-through-resolve | conforms | Implementer Hedy per parent Team |
| orch.roles.pre-commit-path-bans | conforms | No banned paths in Files Changed |
| astral.agent.confidence-bounds | conforms | No confidence math changes |
| astral.agent.do-task-delegation | conforms | Reuses existing GDL tasks; no new do_task shape |
| astral.agent.grade-vector-validation | conforms | Rubrics unchanged (boundary) |
| astral.batch.batch-id-first | conforms | Provision inserts only; claim via existing dispatcher |
| astral.batch.batch-id-format | conforms | No batch_id format change |
| astral.batch.claim-process-release | conforms | Claim→consult→release unchanged; new rows only |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data latest-ref edits |
| astral.config.config-source-of-truth | conforms | Specs/overlay/gated states/triggers in config |
| astral.config.pass-threshold-vs-score-floor | conforms | score_floor on rows; pass_threshold untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env literals |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src + feature plan |
| astral.layers.core-vs-external-bright-line | conforms | No external I/O in plan |
| astral.layers.import-direction | conforms | utils config ← core consult/dispatcher |
| astral.layers.ui-config-driven-business-logic | conforms | Config change only; no UI logic |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check path |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Overlay applied in render_verdict + batch consult |
| astral.standards.data-raises-caller-logs | conforms | No data-layer edits |
| astral.standards.debug-contract-gated | conforms | Style D only via existing debug gates |
| astral.standards.dry-and-focused-functions | conforms | Mirrors AST-972 ensure/provision |
| astral.standards.in-scope-only | conforms | Twins/Create/Recommended explicitly deferred |
| astral.standards.logging-via-utils | conforms | Scheduler log lines via existing logger |
| astral.standards.no-cross-contamination | conforms | Overlay keyed by METEORITE_ prefix; vetted path untouched |
| astral.standards.no-hardcoded-sets | conforms | Row specs + outcome map in config |
| astral.standards.public-then-helpers | conforms | Public ensure/provision + private overlay helpers |
| astral.standards.utils-data-late-import-only | conforms | No utils→data imports proposed |
| astral.state.core-decides-transitions | conforms | Overlay outcomes applied in core consult |
| astral.state.job-prior-states-enforced | conforms | Overlay targets AST-1053 JOB_STATES; asserts membership |
| astral.state.no-daisy-chain-in-run | conforms | No run_next daisy-chain added |
| astral.ui.single-gunicorn-worker | conforms | Touches config.py path only; no worker change |

## Considered and excluded

**Considered:** all rows in Statute verdicts (18 universal + 29 scoped).

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss (no artifacts/**)
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — layers/paths docs only
- astral.git.engineer-test-tree-ban — paths miss tests/**
- astral.layers.scripts-exempt-from-layer-rules — layers scripts miss
- astral.patterns.require-auth-on-protected-endpoints — ui paths miss
- astral.standards.database-header-inventory — data layer miss (no new tables)
- astral.ui.frontend-file-placement — ui paths miss
- astral.ui.naming-conventions — ui paths miss

## Findings

None fix-now.

- **acceptable** — `evaluate_jd` @ `METEORITE_NEW` uses `score_floor: None` (not `0.0`), kept out of `PASSED_SCORE_GATED_STATES`, mirroring `JD_READY`. Child/parent AC “score_floor = 0” still holds for gated hops; entry hop remains non-excluding for low `latest_score` via ungated claim. Documented Decision in Stage 1.
- **acceptable** — Twin `meteorite_like` / `meteorite_upshot` rows skip via `skipped_missing_config` until AST-1055 `TASK_CONFIG` exists; matches child Notes and boundaries.

## R6 checklist (abbrev)

Definition fidelity OK; layers utils/core OK; config SoT + score_floor vs pass_threshold OK; batch claim-process-release OK; no UI/file-placement creep; self-assessment Scope/Conf/Risk honest (Medium overlay contamination risk mitigated).

— Joan
context_tokens≈62000

#### joan — 2026-07-29T21:59:33.188Z
[plan-rubric] revision=1

**STOPPED — worktree AGENTS.md identity gate**

Joan MCP identity OK (`susan+joan@susansomerset.com`). Ticket is **Plan Ready**, assignee Joan.

Epic worktree `/home/susan/astral-AST-1052/AGENTS.md` header is **`# Hedy — Dev Agent`**, not **`# Joan — Statute Validator`**. Per validate-plan Agent identity: stop — worktree corruption; do not run plan-rubric as engineer-seeded worktree.

**Ask Chuckles:** seed `joan-AGENTS.md` into this epic worktree (`seed-agents-md` / handoff), then re-spawn Joan for AST-1054. Plan tip fetched but **not** evaluated: `467bbe89230aa922c4a81302dd79d2df1419d815` @ `origin/sub/AST-1052/AST-1054-meteorite-gdl-dispatch-rows-score-floor-0`.

Status left **Plan Ready**; assignee Joan unchanged.

— Joan
context_tokens≈42000

#### chuckles — 2026-07-29T21:58:56.319Z
[thread-missing] Hedy Team chat reminted — prior UUID e662e9ef identified as Katherine (AGENTS.md race). New Hedy AGENT_SESSION=`32a0c6c0-2099-4b97-baa8-e48095b506b3` (store.db on epic hash). Parent ## Team Hedy row updated.

— Chuckles

#### hedy — 2026-07-29T21:58:01.472Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1052/AST-1054-meteorite-gdl-dispatch-rows-score-floor-0/docs/features/meteorite/ast-1054-meteorite-gdl-dispatch-rows-score-floor-0.md

**Scope:** Single-Component — config dispatch specs + consult outcome overlay for shared GDL keys + dispatcher ensure/provision; no UI/tables/twin prompts.

**Conf:** high — reuses unique (candidate_id, task_key, trigger_state), AST-972 provision pattern, and an explicit METEORITE_* state-prefix overlay; twin rows wait on AST-1055 TASK_CONFIG.

**Risk:** Medium — a missed overlay would shove meteorite jobs onto vetted-company pass/fail states (illegal priors); mitigated by prefix detection + outcome map.

---

# AST-1054 — Meteorite GDL dispatch rows (score_floor 0)

**Linear:** [AST-1054](https://linear.app/astralcareermatch/issue/AST-1054/meteorite-gdl-dispatch-rows-score-floor-0-processing-meteorites)
**Parent:** [AST-1052](https://linear.app/astralcareermatch/issue/AST-1052/processing-meteorites) — Processing meteorites
**Publish ref:** `origin/sub/AST-1052/AST-1054-meteorite-gdl-dispatch-rows-score-floor-0`

Add **new `dispatch_task` rows** that claim the meteorite GDL track for the **same** underlying tasks `evaluate_jd` / `grade_do` / `grade_get` (meteorite trigger states, `score_floor` **= 0**), plus **dispatch wiring** for `meteorite_like` @ **METEORITE_PASSED_GET** and `meteorite_upshot` @ **METEORITE_PASSED_LIKE**. Overlay meteorite pass/fail/error outcomes in consult so shared GDL task keys land on **METEORITE_*** states (not the vetted-company chain). Does **not** author `agent_task` prompt text or `TASK_CONFIG` twins (AST-1055), Create landing (AST-1056), or Recommended Meteorites UI (AST-1057).

Depends on AST-1053 `JOB_STATES` (already on `origin/ftr/AST-1052-processing-meteorites` / this sub). Pairs with AST-1055: twin `TASK_CONFIG` + consult routes + `RECOMMENDED` priors land on that sibling; this ticket seeds the matching dispatch rows and trigger defaults.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `METEORITE_DISPATCH_TASKS` row specs; `METEORITE_GDL_OUTCOME_BY_TASK` overlay; extend `PASSED_SCORE_GATED_STATES`; `_dispatch_trigger_state_for_task_key` for `meteorite_like` / `meteorite_upshot` | utils |
| `src/core/consult.py` | Apply meteorite outcome overlay for shared GDL keys (`evaluate_jd` / `grade_do` / `grade_get`) from entity state | core |
| `src/core/dispatcher.py` | `ensure_meteorite_dispatch_tasks` + `provision_meteorite_dispatch_tasks`; call from `start_scheduler` | core |

## Stage 1: Config — dispatch specs, score-floor gating, outcome overlay, twin trigger defaults

**Done when:** Config loads with meteorite dispatch row specs (`score_floor` 0 on gated hops), outcome overlay map for the three shared GDL keys, meteorite pass triggers in `PASSED_SCORE_GATED_STATES` (entry `METEORITE_NEW` stays ungated like `JD_READY`), and `_dispatch_trigger_state_for_task_key` returns meteorite triggers for `meteorite_like` / `meteorite_upshot`. No `TASK_CONFIG` twin shells here (AST-1055). No DB writes yet.

1. In `src/utils/config.py`, near `METEORITE_CONFIG`, add:

```python
# AST-1054: meteorite dispatch_task row specs (unique per candidate on task_key+trigger_state).
# score_floor 0 on score-gated triggers — claim never excludes for low latest_score.
# Twin keys meteorite_like / meteorite_upshot match AST-1055 TASK_CONFIG + agent_task names.
METEORITE_DISPATCH_TASKS = (
    {
        "task_key": "evaluate_jd",
        "trigger_state": "METEORITE_NEW",
        "score_floor": None,  # ungated entry (mirrors JD_READY / evaluate_jd)
        "auto_mode": False,
        "batch_size": 10,
        "min_count": 1,
        "freq_hrs": 0,
    },
    {
        "task_key": "grade_do",
        "trigger_state": "METEORITE_PASSED_JD",
        "score_floor": 0.0,
        "auto_mode": False,
        "batch_size": 10,
        "min_count": 1,
        "freq_hrs": 0,
    },
    {
        "task_key": "grade_get",
        "trigger_state": "METEORITE_PASSED_DO",
        "score_floor": 0.0,
        "auto_mode": False,
        "batch_size": 10,
        "min_count": 1,
        "freq_hrs": 0,
    },
    {
        "task_key": "meteorite_like",
        "trigger_state": "METEORITE_PASSED_GET",
        "score_floor": 0.0,
        "auto_mode": False,
        "batch_size": 10,
        "min_count": 1,
        "freq_hrs": 0,
    },
    {
        "task_key": "meteorite_upshot",
        "trigger_state": "METEORITE_PASSED_LIKE",
        "score_floor": 0.0,
        "auto_mode": False,
        "batch_size": 1,
        "min_count": 1,
        "freq_hrs": 0,
    },
)

# Shared GDL task_keys → meteorite pass/fail/error (consult overlay; prompts unchanged).
METEORITE_GDL_OUTCOME_BY_TASK = {
    "evaluate_jd": {
        "pass_state": "METEORITE_PASSED_JD",
        "fail_state": "METEORITE_FAILED_JD",
        "error_state": "METEORITE_ERROR_EVALUATE_JD",
    },
    "grade_do": {
        "pass_state": "METEORITE_PASSED_DO",
        "fail_state": "METEORITE_FAILED_DO",
        "error_state": "METEORITE_FAILED_TECHNICAL_DO",
    },
    "grade_get": {
        "pass_state": "METEORITE_PASSED_GET",
        "fail_state": "METEORITE_FAILED_GET",
        "error_state": "METEORITE_FAILED_TECHNICAL_GET",
    },
}
```

⚠️ **Decision — `evaluate_jd` @ `METEORITE_NEW` keeps `score_floor: None`:** Entry hop mirrors normal `JD_READY` (not in `PASSED_SCORE_GATED_STATES`). AC “score_floor = 0” applies to the score-gated meteorite hops (`grade_do` / `grade_get` / like / upshot). Do **not** put `METEORITE_NEW` in `PASSED_SCORE_GATED_STATES`.

⚠️ **Decision — task keys `meteorite_like` and `meteorite_upshot`:** Exact strings agreed with AST-1055 plan. Do not invent `meteorite_analysis_upshot` / `meteorite_grade_like`.

⚠️ **Decision — no `TASK_CONFIG` twins on this ticket:** AST-1055 owns `meteorite_like` / `meteorite_upshot` TASK_CONFIG shells, `RECOMMENDED` prior extension, agent_task prompts, and twin consult routing. This ticket only lists them in `METEORITE_DISPATCH_TASKS` + trigger defaults.

2. Extend `PASSED_SCORE_GATED_STATES` to include:
   `"METEORITE_PASSED_JD", "METEORITE_PASSED_DO", "METEORITE_PASSED_GET", "METEORITE_PASSED_LIKE"`.
   Do **not** add fail/error/retry states. Do **not** add `METEORITE_NEW`.

3. In `_dispatch_trigger_state_for_task_key`, add:
   - `meteorite_like` → `"METEORITE_PASSED_GET"`
   - `meteorite_upshot` → `"METEORITE_PASSED_LIKE"`
   Leave `evaluate_jd` / `grade_do` / `grade_get` defaults on the vetted-company triggers (`JD_READY` / `PASSED_JD` / `PASSED_DO`) — meteorite rows pass `trigger_state=` into `save_dispatch_task` / `dispatch_task_admin_defaults(..., trigger_state=...)`.

4. Assert every `METEORITE_DISPATCH_TASKS[*]["trigger_state"]` is in `JOB_STATES` and every overlay pass|fail|error state is in `JOB_STATES`.

**Done when (recheck):** `from src.utils.config import METEORITE_DISPATCH_TASKS, METEORITE_GDL_OUTCOME_BY_TASK, PASSED_SCORE_GATED_STATES` works; `dispatch_claim_uses_score_floor("METEORITE_PASSED_JD")` is True and `("METEORITE_NEW")` is False; `_dispatch_trigger_state_for_task_key("meteorite_like")` == `"METEORITE_PASSED_GET"`; `python3 -m py_compile src/utils/config.py` succeeds.

## Stage 2: Consult — meteorite outcome overlay for shared GDL keys

**Done when:** Running `evaluate_jd` / `grade_do` / `grade_get` on jobs whose current state starts with `METEORITE_` transitions to meteorite pass/fail/error states from the overlay (not `PASSED_JD` / …). Style D remains gated on `debug=True` only (reuse existing consult debug paths; no new ungated contract lines). Twin routing for `meteorite_like` / `meteorite_upshot` is **not** added here (AST-1055).

1. In `src/core/consult.py`, add helpers (near `_consult_orchestration`):

```python
def _entity_state_is_meteorite(state: Optional[str]) -> bool:
    return bool(state) and str(state).startswith("METEORITE_")

def _consult_orchestration_for_entity(task_key: str, entity_state: Optional[str] = None) -> Dict[str, Any]:
    """TASK_CONFIG row, with meteorite pass/fail/error overlay for shared GDL keys."""
    cfg = dict(_consult_orchestration(task_key))
    overlay = METEORITE_GDL_OUTCOME_BY_TASK.get((task_key or "").strip())
    if overlay and _entity_state_is_meteorite(entity_state):
        cfg.update(overlay)
    return cfg
```

Import `METEORITE_GDL_OUTCOME_BY_TASK` from config.

2. Apply the overlay at every place that currently does `cfg = _consult_orchestration(task_key)` (or equivalent) **for job consult paths that transition state on the three shared GDL keys**, using a representative entity state:
   - `_run_batch_consult`: after loading `cfg`, set `entity_state` from `jobs[0].get("state")` when `jobs` non-empty; use `_consult_orchestration_for_entity(task_key, entity_state)`.
   - `render_verdict`: after `job = tracker.get_job(...)`, use `_consult_orchestration_for_entity(task_type, job.get("state"))`.
   - Any thin wrappers (`evaluate_jd_batch`, `grade_do_batch`, `grade_get_batch`, scored single-job path in `run_consult_task`) that read `pass_state` for summary counts must use the same overlaid cfg when the entity is meteorite.

⚠️ **Decision — detect meteorite via `METEORITE_` state prefix:** Claim rows already segregate by trigger; overlay must not invent parallel TASK_CONFIG keys for JD/DO/GET. Vetted-company `evaluate_jd` @ `JD_READY` stays on normal pass/fail.

3. Do **not** add `run_consult_task` branches for `meteorite_like` / `meteorite_upshot` (AST-1055). Do **not** edit `_prep_live_content` culture behavior beyond what the overlay paths already do.

4. Debug: only emit Style D via existing `if debug:` / `logger.set_debug_flag(True)` paths. When touching meteorite overlay paths, do not add ungated contract lines. With `debug=False`, no new contract lines from this change.

**Done when (recheck):** Overlay maps `evaluate_jd` from `METEORITE_NEW` → `METEORITE_PASSED_JD` (pass path) in `_run_batch_consult` / `render_verdict`; non-meteorite jobs unchanged; `python3 -m py_compile src/core/consult.py` succeeds.

## Stage 3: Dispatcher — provision meteorite dispatch_task rows

**Done when:** Idempotent ensure adds meteorite `(task_key, trigger_state)` rows per candidate (with `score_floor` as specified); twin rows are inserted only when `TASK_CONFIG` already has the key (AST-1055); scheduler start provisions template + candidates that already have dispatch rows; non-meteorite GDL rows unchanged.

1. In `src/core/dispatcher.py`, mirror `ensure_candidate_stage_dispatch_tasks`:

```python
def ensure_meteorite_dispatch_tasks(candidate_id: str) -> Dict[str, Any]:
    """Idempotent insert of AST-1054 meteorite GDL dispatch_task rows for one candidate."""
```

- Load existing `(task_key, trigger_state)` pairs for the candidate.
- For each entry in `METEORITE_DISPATCH_TASKS`:
  - If `entry["task_key"]` not in `TASK_CONFIG`, skip and count as `skipped_missing_config` (twins until AST-1055 merges). Do **not** raise.
  - Else if pair already present: `skipped += 1`.
  - Else `database.save_dispatch_task(candidate_id=..., task_key=..., trigger_state=..., score_floor=entry["score_floor"], auto_mode=..., batch_size=..., min_count=..., freq_hrs=...)`.
- Return `{candidate_id, added, skipped, skipped_missing_config}`.

Import `METEORITE_DISPATCH_TASKS` and `TASK_CONFIG` from config.

2. Add `provision_meteorite_dispatch_tasks()` mirroring `provision_candidate_stage_dispatch_tasks` (template first via `template_candidate_id()`, then every id from `list_candidate_ids_with_dispatch_tasks()`). Aggregate `skipped_missing_config` across candidates.

3. In `start_scheduler`, after the existing AST-972 provision try/except block, call `provision_meteorite_dispatch_tasks()` in its own try/except with a distinct log line (`AST-1054 meteorite dispatch provision ...` / `... failed`). Do not let meteorite provision failure block scheduler start.

4. Do **not** add `meteorite_like` to `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` here (AST-1055). Do **not** change non-meteorite claim SQL, culture `fetch_culture_pages` dispatch, or vetted-company `score_floor` defaults.

⚠️ **Decision — skip twin rows until TASK_CONFIG exists:** `save_dispatch_task` → `dispatch_task_admin_defaults` requires the key in `TASK_CONFIG`. Shared GDL rows (`evaluate_jd` / `grade_do` / `grade_get`) always insert. After AST-1055 lands on `ftr`, a later ensure/provision (scheduler restart or re-run) fills the twin rows — no migration script.

**Done when (recheck):** Calling `ensure_meteorite_dispatch_tasks` twice on a candidate adds the three shared-GDL meteorite rows then skips them; with AST-1055 keys present, adds five then skips five; `grade_do`/`METEORITE_PASSED_JD`/`score_floor=0.0` present; `python3 -m py_compile src/core/dispatcher.py` succeeds.

## Out of scope (do not implement here)

- `TASK_CONFIG` / `agent_task` / consult routing / `RECOMMENDED` priors for `meteorite_like` / `meteorite_upshot` (AST-1055).
- Create landing / `METEORITE_CONFIG["job_create_state"]` → `METEORITE_NEW` (AST-1056).
- Recommended Meteorites section (AST-1057).
- Changing non-meteorite GDL dispatch rows, culture hop, or vetted-company `score_floor` defaults.
- Editing `tests/` or `docs/test-bible/**` (Betty after Code Complete).

## Self-Assessment

**Scope:** `Single-Component` — config + consult overlay for shared GDL + dispatcher provision; no UI, no new tables, no twin prompt authorship.

**Conf:** `high` — reuses `(candidate_id, task_key, trigger_state)` uniqueness, AST-972 ensure/provision pattern, existing Style D gates; overlay is the one new consult seam and is explicitly mapped; twin row insert gated on AST-1055 `TASK_CONFIG`.

**Risk:** `Medium` — wrong overlay or missing overlay would push meteorite jobs onto vetted-company states (illegal priors / track contamination); mitigated by prefix detection + explicit outcome map + assertions. Twin dispatch rows appear only after AST-1055 keys exist (documented skip path).

## Rules self-review

- **§2.1 / pass-threshold-vs-score-floor:** `score_floor` 0 on gated meteorite dispatch rows only; `pass_threshold` on TASK_CONFIG unchanged for shared GDL grading math.
- **§2.4 / claim-process-release:** Provision inserts rows only; claim still goes through existing dispatcher → consult batch path.
- **§1.4 / no-hardcoded-sets:** Row specs + outcome map + gated states live in config.
- **§1.5.1 / debug-contract-gated:** No new ungated Style D lines; reuse existing `debug` flags.
- **In-scope only:** No Create / Recommended UI / twin prompt authorship; no duplicate AST-1055 TASK_CONFIG shells.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1052/AST-1054-meteorite-gdl-dispatch-rows-score-floor-0`
**Plan path:** `docs/features/meteorite/ast-1054-meteorite-gdl-dispatch-rows-score-floor-0.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `45097232` | METEORITE_DISPATCH_TASKS + outcome map + score-gated meteorite triggers |
| 2 | `6e36b273` | Consult METEORITE_ outcome overlay for shared GDL keys |
| 3 | `3d4ee03c` | ensure/provision meteorite dispatch_task rows on scheduler start |

**Tip:** `3d4ee03c198238ca09202b6ac87f08ac0826d21a` on `origin/sub/AST-1052/AST-1054-meteorite-gdl-dispatch-rows-score-floor-0`

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1054
**Publish ref:** `f195665b8df22f7b4ae67c45ae6a94b81f8b0608` (`origin/sub/AST-1052/AST-1054-meteorite-gdl-dispatch-rows-score-floor-0`)
**Overall:** DISCUSS

### What’s solid
- `METEORITE_DISPATCH_TASKS` + `METEORITE_GDL_OUTCOME_BY_TASK` + `PASSED_SCORE_GATED_STATES` meteorite hops; entry `METEORITE_NEW` ungated (`score_floor: None`).
- Consult overlay via `METEORITE_` prefix on shared GDL keys; twin rows skip until AST-1055 `TASK_CONFIG`.
- Scheduler provision mirrors AST-972; Style D reuses existing `debug=` gates.

### Issues
- **discuss (straggler ×3):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` at plan time; three-dot vs `origin/dev` includes `docs/features/**` + Betty tests/bible — all **conforms** on substance.

### Recommended actions
- Hedy: acknowledge stragglers → resolve-child → User Testing.

## Resolution

**Date:** 2026-07-29
**Review:** Radia @ `c5b816ed` — **Overall:** DISCUSS; **fix-now:** none; **discuss:** statute straggler ×3 (all substance **conforms**); no advisory.

No product changes. Acknowledged discuss stragglers as plan-time Joan exclusions that became in-scope on the three-dot vs `origin/dev` (`docs/features/**` + Betty tests/bible) — no code delta. Advanced to **User Testing**.
