<!-- linear-archive: AST-1053 archived 2026-08-07 -->

## Linear archive (AST-1053)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1053/meteorite-gdl-parallel-job-states-processing-meteorites  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1052 — Processing meteorites  
**Blocked by / blocks / related:** parent: AST-1052; blocks: AST-1057; blocks: AST-1056; blocks: AST-1055; blocks: AST-1054

### Description

## What this implements

Owns `JOB_STATES` for **METEORITE_NEW** and **METEORITE_PASSED_JD / DO / GET / LIKE** (plus fail / technical-fail siblings), priors, and UI manifests as needed. Does **not** own dispatch rows, agent_task prompt bodies, Create retarget, or Recommended section.

## Citations

`pattern.state.entity-state-transitions`; `pattern.config.config-block`; `astral.state.job-prior-states-enforced`; `astral.state.core-decides-transitions`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`.

## Acceptance criteria

- [X] 1. Config registers **METEORITE_NEW**, **METEORITE_PASSED_JD**, **METEORITE_PASSED_DO**, **METEORITE_PASSED_GET**, **METEORITE_PASSED_LIKE** (and needed fail / technical-fail siblings) with legal `prior_states`.
- [X] 2. Genuine step failures still land on meteorite fail / technical-fail states; non-meteorite GDL + Recommended behavior unchanged (smoke).

## Boundaries

- [X] Does **not** own dispatch rows (sibling 2), agent_task prompt bodies (sibling 3), Create retarget (sibling 4), or Recommended section (sibling 5).

## Notes for planning

Citations above. Parallel meteorite GDL state track — sibling chain entry **METEORITE_NEW**.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1052-processing-meteorites`, child `sub/AST-1052/AST-NNNN-<slug>`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-07-29T21:46:53.505Z
[thread-missing] Radia Team store.db missing for prior UUID 4d96be2b-0d9c-4387-85d8-0d498478153a on this host; minted and resumed 796b52dd-2830-43c6-a8aa-cf6897426e99 for review-child. — Chuckles

#### radia — 2026-07-29T21:46:01.796Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1053
**Publish ref:** `8392c4c52627b48e5d4b225c26fd23e389210d3c` (`origin/sub/AST-1052/AST-1053-meteorite-gdl-parallel-job-states`)
**Overall:** DISCUSS

**Diff:** `origin/dev...origin/sub/AST-1052/AST-1053-meteorite-gdl-parallel-job-states` — layers `{utils, docs}`; paths `src/utils/config.py`, `docs/features/meteorite/ast-1053-…md`, `docs/test-bible/utils/config.md`, `tests/component/utils/test_config.py`.

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| `astral.agent.confidence-bounds` | scoped | conforms | No confidence / CONFIDENCE_MULTIPLIERS edits |
| `astral.agent.do-task-delegation` | scoped | not-applicable | layers miss (['core']); paths miss (['src/core/**']) |
| `astral.agent.grade-vector-validation` | scoped | not-applicable | layers miss (['core']); paths miss (['src/core/**']) |
| `astral.batch.batch-id-first` | scoped | not-applicable | layers miss (['data', 'core']); paths miss (['src/data/**', 'src/core/**']) |
| `astral.batch.batch-id-format` | scoped | not-applicable | layers miss (['core', 'data']); paths miss (['src/core/**', 'src/data/**']) |
| `astral.batch.claim-process-release` | scoped | not-applicable | layers miss (['core', 'data']); paths miss (['src/core/**', 'src/data/**']) |
| `astral.batch.entity-agent-responses-latest-only` | scoped | not-applicable | layers miss (['core', 'data']); paths miss (['src/core/**', 'src/data/**']) |
| `astral.config.config-source-of-truth` | scoped | conforms | JOB_STATES + In Review/Skipped manifests only in config.py |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | PASSED_SCORE_GATED_STATES untouched; no pass_threshold/score_floor mix |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | No secrets or env-specific values |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths miss (['artifacts/**', 'scripts/spikes/**']) |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | Plan doc under docs/features/; no spike notes |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | Single plan file docs/features/meteorite/ast-1053-…md |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test()/merge-tests only; code() owns src; docs() plan |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | test() commit owns tests/ + bible; engineer code() only config.py |
| `astral.layers.core-vs-external-bright-line` | scoped | not-applicable | layers miss (['core', 'external']); paths miss (['src/core/**', 'src/external/**']) |
| `astral.layers.import-direction` | scoped | conforms | utils config registry only; no new imports |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers miss (['scripts']); paths miss (['scripts/**']) |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | Jobs UI via IN_REVIEW/SKIPPED manifests + grade maps |
| `astral.patterns.coat-check-never-store-empty` | scoped | not-applicable | layers miss (['core']); paths miss (['src/core/**']) |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | not-applicable | layers miss (['core']); paths miss (['src/core/**']) |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers miss (['ui']); paths miss (['src/ui/**']) |
| `astral.standards.data-raises-caller-logs` | scoped | not-applicable | layers miss (['data', 'core', 'ui']) |
| `astral.standards.database-header-inventory` | scoped | not-applicable | layers miss (['data']); paths miss (['src/data/**']) |
| `astral.standards.debug-contract-gated` | scoped | conforms | No debug= paths added |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Registry + list appends only |
| `astral.standards.in-scope-only` | scoped | conforms | No dispatch/prompts/create/Recommended; siblings 1054–1057 |
| `astral.standards.logging-via-utils` | scoped | conforms | No logging changes |
| `astral.standards.no-cross-contamination` | scoped | conforms | Config-only; non-meteorite GDL untouched |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | State names only in JOB_STATES + UI list constants |
| `astral.standards.public-then-helpers` | scoped | conforms | No new helpers |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | No utils→data |
| `astral.state.core-decides-transitions` | scoped | not-applicable | layers miss (['core', 'data']); paths miss (['src/core/**', 'src/data/**']) |
| `astral.state.job-prior-states-enforced` | scoped | conforms | Explicit prior graph; METEORITE_NEW None; LIKE from PASSED_GET |
| `astral.state.no-daisy-chain-in-run` | scoped | not-applicable | layers miss (['core']); paths miss (['src/core/**']) |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers miss (['ui']); paths miss (['src/ui/frontend/**']) |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers miss (['ui']); paths miss (['src/ui/**']) |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | No gunicorn/worker edits |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | Single merge-tests(AST-1053) onto tip |
| `orch.git.commit-vocabulary` | universal | conforms | docs/code/test/merge-tests vocabulary used |
| `orch.git.flow-direction-inviolable` | universal | conforms | Work on sub/* only; no reverse merge into dev |
| `orch.git.ftr-sub-topology` | universal | conforms | sub/AST-1052/AST-1053-… under parent ftr |
| `orch.git.merge-on-checkout` | universal | conforms | No conflicting checkout rewrite |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | No rewrite ops in history |
| `orch.git.no-dev-agent-branches` | universal | conforms | Publish ref is ticket sub, not agent/dev-* |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | astral-AST-1052 epic worktree |
| `orch.git.three-permanent-branches` | universal | conforms | No new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | Product call locked in parent AST-1052 definition |
| `orch.pipeline.plan-is-bible` | universal | conforms | Diff matches Stage 1 keys/priors/UI lists; boundaries held |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Meteorite child |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | No canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Betty test() + bible; merge-tests one SHA |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Assignee Ada through Tests Passed |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Assignee remains Ada |
| `orch.roles.pre-commit-path-bans` | universal | conforms | Role-appropriate paths per commit vocabulary |

## Pattern conformance

- `pattern.state.entity-state-transitions` — conforms (parallel track with explicit priors; no culture hop)
- `pattern.config.config-block` — conforms (JOB_STATES + UI list constants)
- Cited statutes (`astral.state.job-prior-states-enforced`, `astral.state.core-decides-transitions`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`) covered in Statutes checked (`core-decides` N/A — utils-only)

## Plan adherence

Stage 1 delivered as written: 14 meteorite `JOB_STATES` keys with planned priors; In Review / Skipped membership, section order/labels, grade maps. Self-Assessment Scope `Single-Component` matches footprint. Boundaries held — no TASK_CONFIG/DISPATCH/create retarget/Recommended/`PASSED_SCORE_GATED_STATES`. Betty tests assert priors + UI + non-meteorite smoke.

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
- Prior graph + UI manifests match plan; AC2 smoke (Recommended / score-gated / create default) held.

### Recommended actions
- Ada: acknowledge stragglers → resolve-child → User Testing.

**Notes:** Joan plan-rubric verdict attached (APPROVED). Docs append on plan file @ `8392c4c5`.

context_tokens≈28000

#### betty — 2026-07-29T21:42:00.742Z
1. `tests/component/utils/test_config.py::TestAst1053MeteoriteGdlJobStates` — meteorite GDL priors; In Review/Skipped membership + UI labels/order + grade maps; score-gated / Recommended / `job_create_state` smoke

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1053MeteoriteGdlJobStates \
  -q
```

**Pass:** pytest green on narrowed args.

**Broken/revised:** none — additive.
**Integration:** none.

**Publish:** `origin/sub/AST-1052/AST-1053-meteorite-gdl-parallel-job-states` @ `e0256021` (`merge-tests(AST-1053): origin/tests 3c4426542ad9f47bd885f6be50159b1061095283`)

**Bible shasums on publish ref:**
- `docs/test-bible/utils/config.md` `47b5e13bebeab9adff3202690b48e84b870f683f`

— Betty

#### joan — 2026-07-29T21:35:36.349Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1053
**Overall:** APPROVED

**Notes:** First Plan Ready pass. Tip `57409ca7`. Publish ref `origin/sub/AST-1052/AST-1053-meteorite-gdl-parallel-job-states`. Parallel meteorite GDL track authorized by parent AST-1052 definition (dispatched; Open questions none).
**Implementer:** Ada (parent Team table / plan author).

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1 Register METEORITE_* pass + fail/technical siblings with legal priors | Stage 1 |
| 2 Meteorite dispatch rows score_floor 0 | N/A — boundary: AST-1054 |
| 3 No culture hop; meteorite_like after PASSED_GET | N/A — states omit CULTURE_READY (Stage 1); prompts AST-1055; dispatch AST-1054 |
| 4 Meteorite upshot after LIKE | N/A — prompts AST-1055; `METEORITE_PASSED_LIKE_RETRY` registered here for lawful hold |
| 5 Recommended Meteorites section | N/A — boundary: AST-1057 |
| 6 Create lands in METEORITE_NEW | N/A — boundary: AST-1056; `prior_states: None` on METEORITE_NEW enables lawful entry |
| 7 Failures land on meteorite fail/technical; non-meteorite unchanged | Stage 1 registers fail/technical siblings; leaves non-meteorite GDL + `RECOMMENDED` / `PASSED_SCORE_GATED_STATES` untouched |
| 8 Style D debug on meteorite GDL paths | N/A — no processing paths in this child (dispatch/debug AST-1054+) |

### Child AC → plan stages

| Child AC | Stages |
| -- | -- |
| 1 Config registers METEORITE_* + priors | Stage 1 |
| 2 Fail/technical siblings exist; non-meteorite smoke unchanged | Stage 1 |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 JOB_STATES + In Review/Skipped UI manifests | Purpose parallel track; Functional scope state registration; AC1/AC7; Boundaries (no dispatch/prompts/create/Recommended) |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Plan `docs(AST-1053):` path |
| orch.git.flow-direction-inviolable | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No conflicting checkout procedure |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | conforms | `astral-AST-1052` |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Parallel-track product call already locked in parent definition |
| orch.pipeline.plan-is-bible | conforms | Stages binding; siblings excluded |
| orch.pipeline.project-scoped-queues | conforms | Single-child Astral Meteorite |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | tests/bible out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign Ada on approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | States + UI manifests only in `config.py` |
| astral.config.pass-threshold-vs-score-floor | conforms | Leaves `PASSED_SCORE_GATED_STATES` unchanged (AST-1054 owns floors) |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned config |
| astral.layers.import-direction | conforms | utils-only change |
| astral.layers.ui-config-driven-business-logic | conforms | Jobs UI via existing config manifests / `build_state_ui_manifest` |
| astral.standards.debug-contract-gated | conforms | No new debug paths |
| astral.standards.dry-and-focused-functions | conforms | Registry + list appends only |
| astral.standards.in-scope-only | conforms | Explicit out-of-scope for 1054–1057 |
| astral.standards.logging-via-utils | conforms | Untouched |
| astral.standards.no-cross-contamination | conforms | Config only |
| astral.standards.no-hardcoded-sets | conforms | State names only in JOB_STATES + UI list constants |
| astral.standards.public-then-helpers | conforms | No new scattered helpers |
| astral.standards.utils-data-late-import-only | conforms | No utils→data |
| astral.state.job-prior-states-enforced | conforms | Explicit prior graph; METEORITE_NEW unrestricted entry; LIKE from PASSED_GET (no culture) |
| astral.ui.single-gunicorn-worker | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.job-prior-states-enforced, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.agent.do-task-delegation — layers/paths miss
- astral.agent.grade-vector-validation — layers/paths miss
- astral.batch.batch-id-first — layers/paths miss
- astral.batch.batch-id-format — layers/paths miss
- astral.batch.claim-process-release — layers/paths miss
- astral.batch.entity-agent-responses-latest-only — layers/paths miss
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — layers/paths miss
- astral.git.engineer-test-tree-ban — paths miss
- astral.layers.core-vs-external-bright-line — layers/paths miss
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.patterns.coat-check-never-store-empty — layers/paths miss
- astral.patterns.render-verdict-orchestrates-consult — layers/paths miss
- astral.patterns.require-auth-on-protected-endpoints — layers/paths miss
- astral.standards.data-raises-caller-logs — layers miss
- astral.standards.database-header-inventory — layers/paths miss
- astral.state.core-decides-transitions — layers `core`/`data` / paths miss (utils-only Files Changed)
- astral.state.no-daisy-chain-in-run — layers/paths miss
- astral.ui.frontend-file-placement — layers/paths miss
- astral.ui.naming-conventions — layers/paths miss

## Findings

### fix-now
(none)

### discuss
(none)

### acceptable
1. `METEORITE_PASSED_LIKE_RETRY` beyond the bare AC name list — mirrors `PASSED_LIKE_RETRY` for upshot technical hold; documented; needed by AST-1055.
2. No meteorite JD retry-hold states — matches parent “pass + fail/technical” and plan decision; AST-1054 owns claim/error wiring.
3. `METEORITE_NEW` with `prior_states: None` while Create retarget stays AST-1056 — correct split.
4. Self-assessment Single-Component / high / Medium — honest.
5. Parent “new pattern” flag satisfied by dispatched parent definition, not a live product open question.

— Joan
context_tokens≈45000

#### ada — 2026-07-29T21:32:59.501Z
Plan published on `origin/sub/AST-1052/AST-1053-meteorite-gdl-parallel-job-states` @ tip (see attachment).

**Plan:** [docs/features/meteorite/ast-1053-meteorite-gdl-parallel-job-states.md](https://github.com/susansomerset/astral/blob/sub/AST-1052/AST-1053-meteorite-gdl-parallel-job-states/docs/features/meteorite/ast-1053-meteorite-gdl-parallel-job-states.md)

**Self-assessment**
- **Scope:** Single-Component — `JOB_STATES` parallel meteorite GDL track + Jobs In Review/Skipped UI manifests in `config.py` only.
- **Conf:** high — mirrors existing GDL prior graph and UI list patterns; no dispatch/create/Recommended.
- **Risk:** Medium — wrong priors block sibling hops or legalize illegal ones; mitigated by explicit prior table and leaving `RECOMMENDED` / `PASSED_SCORE_GATED_STATES` untouched.

---

# AST-1053 — Meteorite GDL parallel job states

**Linear:** [AST-1053](https://linear.app/astralcareermatch/issue/AST-1053/meteorite-gdl-parallel-job-states-processing-meteorites)
**Parent:** [AST-1052](https://linear.app/astralcareermatch/issue/AST-1052/processing-meteorites) — Processing meteorites
**Publish ref:** `origin/sub/AST-1052/AST-1053-meteorite-gdl-parallel-job-states`

Register a **parallel meteorite GDL job-state track** in `JOB_STATES` (entry **METEORITE_NEW**, then **METEORITE_PASSED_JD → DO → GET → LIKE**, plus fail / technical-fail / upshot-retry siblings) and wire those states into the existing Jobs **In Review** / **Skipped** UI manifests so they are visible. Does **not** own dispatch rows, agent_task prompts, Create landing retarget, or the Recommended Meteorites section.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add meteorite `JOB_STATES` keys + priors; extend `IN_REVIEW_STATES` / `SKIPPED_STATES` / `JOBS_IN_REVIEW_UI_SECTIONS` / `JOBS_SKIPPED_*` / grade-field maps | utils |

## Stage 1: Parallel meteorite `JOB_STATES` + Jobs UI manifests

**Done when:** All meteorite GDL states exist in `JOB_STATES` with legal `prior_states`; In Review / Skipped manifests list them; no dispatch / create / Recommended changes.

1. In `src/utils/config.py`, inside `JOB_STATES` (after the existing GDL block that ends around `FAILED_TECHNICAL_LIKE` / before `ERROR_QUALIFY_JOB_LISTINGS` is fine — keep keys contiguous with a short comment header), add:

```python
# AST-1052 / AST-1053: parallel meteorite GDL track (no CULTURE_READY hop).
# Entry METEORITE_NEW is unrestricted (create landing — sibling AST-1056).
"METEORITE_NEW":                  {"prior_states": None},
"METEORITE_PASSED_JD":            {"prior_states": ["METEORITE_NEW"]},
"METEORITE_FAILED_JD":            {"prior_states": ["METEORITE_NEW"]},
"METEORITE_ERROR_EVALUATE_JD":    {"prior_states": ["METEORITE_NEW"]},
"METEORITE_PASSED_DO":            {"prior_states": ["METEORITE_PASSED_JD"]},
"METEORITE_FAILED_DO":            {"prior_states": ["METEORITE_PASSED_JD"]},
"METEORITE_FAILED_TECHNICAL_DO":  {"prior_states": ["METEORITE_PASSED_JD"]},
"METEORITE_PASSED_GET":           {"prior_states": ["METEORITE_PASSED_DO"]},
"METEORITE_FAILED_GET":           {"prior_states": ["METEORITE_PASSED_DO"]},
"METEORITE_FAILED_TECHNICAL_GET": {"prior_states": ["METEORITE_PASSED_DO"]},
# LIKE claimed from METEORITE_PASSED_GET (no CULTURE_READY) — sibling AST-1054/1055.
"METEORITE_PASSED_LIKE":          {"prior_states": ["METEORITE_PASSED_GET"]},
"METEORITE_FAILED_LIKE":          {"prior_states": ["METEORITE_PASSED_GET"]},
"METEORITE_FAILED_TECHNICAL_LIKE":{"prior_states": ["METEORITE_PASSED_GET"]},
# Upshot technical-hold after meteorite LIKE (mirrors PASSED_LIKE_RETRY) — sibling AST-1055.
"METEORITE_PASSED_LIKE_RETRY":    {"prior_states": ["METEORITE_PASSED_LIKE"]},
```

⚠️ **Decision — `prior_states: None` on `METEORITE_NEW`:** Lawful unrestricted entry for Create (sibling AST-1056), mirroring `NEW` rather than expanding `JD_READY` or inventing a carve-out on this ticket. Do **not** change `METEORITE_CONFIG["job_create_state"]` here (still `JD_READY` until AST-1056).

⚠️ **Decision — no `METEORITE_*_RETRY` holding states except `METEORITE_PASSED_LIKE_RETRY`:** Parent AC lists pass + fail/technical siblings only; LIKE upshot needs the retry hold to mirror `PASSED_LIKE_RETRY`. Do **not** add `METEORITE_NEW_RETRY` / scrape-fail siblings / culture states.

⚠️ **Decision — do not extend `RECOMMENDED` / `RECOMMENDED_JOB_STATES` priors:** Meteorite post-upshot membership is AST-1057. Mixing `METEORITE_PASSED_LIKE` into normal `RECOMMENDED` priors would violate parent Boundaries.

⚠️ **Decision — do not add meteorite keys to `PASSED_SCORE_GATED_STATES`:** Score-floor claim wiring is AST-1054 (`score_floor` 0 on meteorite dispatch rows). Leaving the frozenset unchanged keeps non-meteorite claim/UI floor behavior identical.

2. Extend ordered Jobs UI lists (same file) so Jobs In Review / Skipped stay config-driven:

- **`IN_REVIEW_STATES`:** append  
  `"METEORITE_NEW", "METEORITE_PASSED_JD", "METEORITE_PASSED_DO", "METEORITE_PASSED_GET", "METEORITE_PASSED_LIKE", "METEORITE_PASSED_LIKE_RETRY"`.
- **`SKIPPED_STATES`:** append  
  `"METEORITE_FAILED_JD", "METEORITE_ERROR_EVALUATE_JD", "METEORITE_FAILED_DO", "METEORITE_FAILED_TECHNICAL_DO", "METEORITE_FAILED_GET", "METEORITE_FAILED_TECHNICAL_GET", "METEORITE_FAILED_LIKE", "METEORITE_FAILED_TECHNICAL_LIKE"`.
- **`JOBS_IN_REVIEW_UI_SECTIONS`:** append rows (labels):
  - `METEORITE_NEW` → `"Meteorite New"`
  - `METEORITE_PASSED_JD` → `"Meteorite Passed JD"`
  - `METEORITE_PASSED_DO` → `"Meteorite Passed DO"`
  - `METEORITE_PASSED_GET` → `"Meteorite Passed GET"`
  - `METEORITE_PASSED_LIKE` → `"Meteorite Passed LIKE"`
  - `METEORITE_PASSED_LIKE_RETRY` → `"Meteorite LIKE upshot (retry)"`
- **`JOBS_SKIPPED_SECTION_ORDER`:** prepend meteorite fails near the matching normal fails (group with LIKE/GET/DO/JD technical pairs), e.g. after the normal LIKE pair insert the meteorite LIKE pair, etc. — keep order stable and readable; every new skipped state must appear exactly once.
- **`JOBS_SKIPPED_SECTION_LABELS`:** add human labels for each new skipped state (mirror naming: `"Meteorite Failed JD"`, `"Meteorite Error Evaluate JD"`, `"Meteorite Failed DO"`, …).
- **`JOBS_IN_REVIEW_GRADE_FIELD`:** map  
  `METEORITE_PASSED_JD` → `jd_grades`,  
  `METEORITE_PASSED_DO` → `do_grades`,  
  `METEORITE_PASSED_GET` → `get_grades`,  
  `METEORITE_PASSED_LIKE` / `METEORITE_PASSED_LIKE_RETRY` → `like_grades`.  
  (`METEORITE_NEW` needs no grade blob yet.)
- **`JOBS_SKIPPED_GRADE_FIELD`:** map  
  `METEORITE_FAILED_JD` → `jd_grades`,  
  `METEORITE_FAILED_DO` → `do_grades`,  
  `METEORITE_FAILED_GET` → `get_grades`,  
  `METEORITE_FAILED_LIKE` → `like_grades`.  
  (Technical / error states may omit grade fields — same as normal `FAILED_TECHNICAL_*` / `ERROR_EVALUATE_JD` today.)

3. Do **not** edit `TASK_CONFIG` / `DISPATCH_*` / `METEORITE_CONFIG` create defaults / Recommended section lists / frontend TS state enums (manifest is config-driven via `build_state_ui_manifest`). Do **not** edit `tests/` or bible.

**Done when (recheck):** `from src.utils.config import JOB_STATES` loads; every new key is present with the priors above; `METEORITE_NEW` has `prior_states is None`; no `CULTURE_READY` / `NEED_*` meteorite keys; `IN_REVIEW_STATES` / `SKIPPED_STATES` / UI section lists include the new keys; `RECOMMENDED` priors and `PASSED_SCORE_GATED_STATES` unchanged; `python3 -m py_compile src/utils/config.py` succeeds.

## Out of scope (do not implement here)

- Meteorite dispatch_task rows / `score_floor` 0 (AST-1054).
- `meteorite_like` / meteorite upshot agent_task bodies (AST-1055).
- Retarget Create / `METEORITE_CONFIG["job_create_state"]` → `METEORITE_NEW` (AST-1056).
- Recommended page Meteorites section (AST-1057).
- Changing non-meteorite GDL states, culture hop, or score-floor frozenset membership.
- Editing `tests/` or `docs/test-bible/**` (Betty after Code Complete).

## Self-Assessment

**Scope:** `Single-Component` — one file (`config.py`); state registry + Jobs UI manifests only.

**Conf:** `high` — mirrors existing GDL prior graph and In Review / Skipped list patterns; no core/UI code paths required for registration.

**Risk:** `Medium` — wrong priors would block sibling transitions or legalize illegal hops; mitigated by explicit prior table matching the parent chain and leaving `RECOMMENDED` / score-gated sets untouched.

## Rules self-review

- **§2.1 / no-hardcoded-sets:** State names only in `JOB_STATES` + existing UI list constants.
- **§2.6 / job-prior-states-enforced:** Every new state has explicit `prior_states` (or `None` for entry).
- **config-source-of-truth:** UI labels/sections read from the same config maps.
- **In-scope only:** No dispatch / prompts / create / Recommended section.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1052/AST-1053-meteorite-gdl-parallel-job-states`
**Plan path:** `docs/features/meteorite/ast-1053-meteorite-gdl-parallel-job-states.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `46ea8b73` | JOB_STATES meteorite GDL track + In Review/Skipped UI manifests |

**Tip:** `9c6ca1b0a93e0425a162b2da3995899a0f749e92` on `origin/sub/AST-1052/AST-1053-meteorite-gdl-parallel-job-states`

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1053
**Publish ref:** `e025602150895a4b7070a8029c1a831dd0cb9b10` (`origin/sub/AST-1052/AST-1053-meteorite-gdl-parallel-job-states`)
**Overall:** DISCUSS

### What’s solid
- Parallel meteorite GDL `JOB_STATES` priors match the plan table; `METEORITE_NEW` unrestricted; LIKE from `METEORITE_PASSED_GET` (no culture hop).
- In Review / Skipped manifests + grade-field maps config-driven; `RECOMMENDED` priors and `PASSED_SCORE_GATED_STATES` untouched; create default still `JD_READY`.
- Boundaries held vs AST-1054–1057; Betty owns tests/bible.

### Issues
- **discuss (straggler ×3):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` at plan time; three-dot vs `origin/dev` includes `docs/features/**` + Betty tests/bible — all **conforms** on substance.

### Recommended actions
- Ada: acknowledge stragglers → resolve-child → User Testing.

## Resolution

**Date:** 2026-07-29
**Review:** Radia @ `8392c4c5` — **Overall:** DISCUSS; **fix-now:** none; **discuss:** statute straggler ×3 (all substance **conforms**); no advisory.

No product changes. Acknowledged discuss stragglers as plan-time Joan exclusions that became in-scope on the three-dot vs `origin/dev` (`docs/features/**` + Betty tests/bible) — no code delta. Advanced to **User Testing**.

