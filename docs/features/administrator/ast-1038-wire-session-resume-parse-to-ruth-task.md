<!-- linear-archive: AST-1038 archived 2026-08-05 -->

## Linear archive (AST-1038)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1038/wire-session-resume-parse-to-ruth-task-simple-resume-parse-function  
**Status at archive:** Archive  
**Project:** Astral Administrator  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1036 — Simple Resume Parse function  
**Blocked by / blocks / related:** parent: AST-1036

### Description

## What this implements

After the Ruth simple session-resume parse task lands: point Admin session resume parse (core + thin Admin route contract) at the new Ruth task instead of `craft_resume_base`. Preserve no-persist / no-candidate-bind behavior, ledger visibility, and Style D debug on the hop. Leave candidate craft on Judith. Prefer no Paste UI change.

## Citations

`pattern.ui.admin-endpoint`; `pattern.layers.import-discipline`; `astral.patterns.require-auth-on-protected-endpoints`; `astral.layers.ui-config-driven-business-logic`; `astral.standards.debug-contract-gated`; `astral.standards.in-scope-only`.

## Acceptance criteria

1. From Admin **Session Resume Paste**, Parse runs a Ruth (Little) task — not Judith craft-base — and still returns structure-keyed JSON the screen already understands.
2. A successful Parse → Open HTML path still works without binding to the selected candidate and without writing candidate/job artifacts for the paste.
3. Dispatch/cost ledger for the Admin session-parse hop still records the run against the session sentinel path (same operational visibility Susan has today).
4. Candidate-bound `craft_resume_base` / Judith craft behavior is unchanged when exercised outside this Admin session path.
5. With debug on, the session-parse hop emits Style D index + detail (found|recorded), not summary-only noise; with debug off, no new debug-contract lines.

## Boundaries

* Does **not** author the Ruth agent_task / TASK_CONFIG entry — sibling owns that.
* Does **not** change Judith `craft_resume_base` for candidate craft.
* Does **not** change Open HTML builder; prefer zero Paste UI change.

## Notes for planning

After AST-1037. Wire `run_session_resume_parse` (+ Admin route) to the new task key.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-29T16:12:34.376Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1038
**Publish ref:** `1c62a5ea` on `origin/sub/AST-1036/AST-1038-wire-session-resume-parse-to-ruth-task`
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | conforms | No confidence math changes |
| astral.agent.do-task-delegation | scoped | conforms | Still only via `do_task`; key swap only |
| astral.agent.grade-vector-validation | scoped | conforms | Untouched |
| astral.batch.batch-id-first | scoped | conforms | Existing session batch_id path unchanged |
| astral.batch.batch-id-format | scoped | conforms | Untouched |
| astral.batch.claim-process-release | scoped | conforms | Untouched |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | Untouched |
| astral.config.config-source-of-truth | scoped | conforms | Selects AST-1037 `TASK_CONFIG` key; no new schema |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | Untouched |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths artifacts/** / scripts/spikes/** miss |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plan docs only — not spike dumps |
| astral.docs.features-single-file-per-ticket | scoped | conforms | One feature file per ticket (1037 + 1038) |
| astral.git.betty-no-src-or-features | scoped | conforms | Engineer `code()` owns src; Betty owns tests |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer `2cf538f4` is candidate+api only; Betty `test()` |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Wire in core; no external I/O |
| astral.layers.import-direction | scoped | conforms | ui → core; Admin stays thin |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths scripts/** miss |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Task choice in core; React untouched |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Untouched |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | `@require_admin` retained on `/session_resume/parse` |
| astral.standards.data-raises-caller-logs | scoped | conforms | Untouched |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths src/data/** miss |
| astral.standards.debug-contract-gated | scoped | conforms | Style D still gated on `debug=True`; no new ungated lines |
| astral.standards.dry-and-focused-functions | scoped | conforms | Single call-site swap; reuse split/normalize |
| astral.standards.in-scope-only | scoped | conforms | No Judith craft / HTML / catalog authoring |
| astral.standards.logging-via-utils | scoped | conforms | Existing logger path |
| astral.standards.no-cross-contamination | scoped | conforms | Session wire only |
| astral.standards.no-hardcoded-sets | scoped | conforms | One catalog-key literal at existing call site |
| astral.standards.public-then-helpers | scoped | conforms | Public signatures unchanged |
| astral.standards.utils-data-late-import-only | scoped | conforms | No utils→data import added on tip |
| astral.state.core-decides-transitions | scoped | conforms | Untouched |
| astral.state.job-prior-states-enforced | scoped | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | scoped | conforms | Untouched |
| astral.ui.frontend-file-placement | scoped | not-applicable | paths src/ui/frontend/** miss |
| astral.ui.naming-conventions | scoped | conforms | No new routes/files |
| astral.ui.single-gunicorn-worker | scoped | conforms | Untouched |
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1038)` tip |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | universal | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | Tip carries AST-1037 via ftr lineage |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | Linear history |
| orch.git.no-dev-agent-branches | universal | conforms | Ticket sub ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | `astral-AST-1036/` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No open product Q |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–2 match `code()` |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Administrator |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Entered from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty `test(AST-1038)` |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada through Review Posted |
| orch.roles.pre-commit-path-bans | universal | conforms | Engineer code off Betty paths |

## Pattern conformance

| id | verdict |
| -- | -- |
| pattern.ui.admin-endpoint | conforms — thin route; docstring only |
| pattern.layers.import-discipline | conforms — ui → core |
| astral.patterns.require-auth-on-protected-endpoints | conforms — `@require_admin` kept |
| astral.layers.ui-config-driven-business-logic | conforms — task key chosen in core |
| astral.standards.debug-contract-gated | conforms — Style D preserved gated |
| astral.standards.in-scope-only | conforms — wire only |

## Plan adherence

`code(AST-1038)` is exactly Stage 1–2: `task_key` swap + error/docstring strings in `candidate.py` / `api_admin.py`. Self-Assessment Single-Component / high / low fits. Boundaries vs AST-1037 catalog and Judith craft held.

## Findings

### fix-now
(none)

### discuss
1. **C4 straggler** — Joan Excluded `astral.debug.spikes-under-debug-dir`; tip includes `docs/features/**` → in-scope; substance conforms.
2. **C4 straggler** — Joan Excluded `astral.docs.features-single-file-per-ticket`; tip includes feature docs → in-scope; substance conforms.
3. **C4 straggler** — Joan Excluded `astral.git.engineer-test-tree-ban`; tip includes Betty tests/bible → in-scope; substance conforms.
4. **C4 straggler** — Joan Excluded `astral.standards.utils-data-late-import-only`; tip includes `src/utils/config.py` (rolled AST-1037) → in-scope; substance conforms.

### advisory
(none product)

## What's solid
Thin Ruth wire, auth + Style D + sentinel ledger preserved, Judith craft untouched in this child's code SHA.

## Recommended actions
Ada: acknowledge the four C4 straggler discusses (no product edit expected), then `resolve-child`.

— Radia
context_tokens≈26000

#### betty — 2026-07-29T16:09:47.290Z
1. `tests/component/core/test_candidate.py::TestAst1038SessionResumeWire` — `run_session_resume_parse` → `simple_resume_parse`; Judith craft paths still `craft_resume_base`
2. `tests/component/core/test_candidate.py::TestAst986SessionResumeParse` — revised `task_key` + non-dict error string; session sentinel / no-persist / Style D unchanged
3. `tests/component/ui/api/test_api_admin.py::TestAst986SessionResumeParseApi` — thin Admin route contract unchanged (docstring-only product)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1038SessionResumeWire \
  tests/component/core/test_candidate.py::TestAst986SessionResumeParse \
  tests/component/ui/api/test_api_admin.py::TestAst986SessionResumeParseApi \
  -q
```

`origin/sub/AST-1036/AST-1038-wire-session-resume-parse-to-ruth-task` @ `772afdc4` (`merge-tests(AST-1038): origin/tests b088c35d`)

Bible shasum on publish tip:
- `docs/test-bible/core/candidate.md` `bc5bf0948d71c3f1a733a448a912fa2e327978d9`

#### joan — 2026-07-29T16:05:28.333Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1038
**Overall:** APPROVED

**Notes:** First Plan Ready pass. Tip `a81c4939`. Publish ref `origin/sub/AST-1036/AST-1038-wire-session-resume-parse-to-ruth-task`. Blocked-by AST-1037 Plan Approved; merge-on-checkout precondition stated.
**Implementer:** Ada (parent Team table / plan author).

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1 Session Paste Parse runs Ruth + familiar JSON | Stage 1 (`do_task` key swap) + Stage 2 (route still thin) |
| 2 Parse → Open HTML no bind / no artifact write | Stage 1 preserves AST-986 sentinel / no-persist path |
| 3 Dispatch/cost ledger on session sentinel | Stage 1 keeps existing ledger (`user-session-parse-resume` / `candidate_id="session"`) |
| 4 Paste-faithful mechanics in prompt | N/A — boundary: AST-1037 (Ruth prompt); this child only selects that task |
| 5 Judith `craft_resume_base` unchanged outside session | Stage 1 forbids craft-path edits; grep gate |
| 6 Style D debug gated on session-parse hop | Stage 1 preserves existing Style D; no new ungated lines |

### Child AC → plan stages

| Child AC | Stages |
| -- | -- |
| 1 Ruth not Judith; familiar JSON | 1–2 |
| 2 No bind / no artifact write | 1 |
| 3 Ledger sentinel visibility | 1 |
| 4 Judith craft unchanged | 1 |
| 5 Style D on/off | 1 |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 Core wire `run_session_resume_parse` → `simple_resume_parse` | Functional scope session parse uses Ruth; AC1–3,5–6 |
| 2 Admin docstring only | Thin admin-endpoint / require-auth unchanged |
| 3 Compile check | Build hygiene |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Plan `docs(AST-1038):` path |
| orch.git.flow-direction-inviolable | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | Prerequisite merge of 1037 via ftr stated |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | conforms | `astral-AST-1036` |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | No open product Q; key authored in AST-1037 |
| orch.pipeline.plan-is-bible | conforms | Stages binding; catalog owned by sibling |
| orch.pipeline.project-scoped-queues | conforms | Astral Administrator |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | No `tests/` edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign Ada on approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | Untouched |
| astral.agent.do-task-delegation | conforms | Still only via `do_task` |
| astral.agent.grade-vector-validation | conforms | Untouched |
| astral.batch.batch-id-first | conforms | Untouched |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Untouched |
| astral.batch.entity-agent-responses-latest-only | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | Selects existing TASK_CONFIG key; no new schema |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | Untouched |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned src |
| astral.layers.core-vs-external-bright-line | conforms | Wire in core; no external I/O change |
| astral.layers.import-direction | conforms | ui → core only |
| astral.layers.ui-config-driven-business-logic | conforms | Task choice in core; React unchanged |
| astral.patterns.coat-check-never-store-empty | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Untouched |
| astral.patterns.require-auth-on-protected-endpoints | conforms | `@require_admin` kept |
| astral.standards.data-raises-caller-logs | conforms | Untouched |
| astral.standards.debug-contract-gated | conforms | Preserve existing `debug=True` Style D only |
| astral.standards.dry-and-focused-functions | conforms | Single call-site swap; reuse split/normalize |
| astral.standards.in-scope-only | conforms | Explicit forbids craft/catalog/UI/HTML |
| astral.standards.logging-via-utils | conforms | Existing logger path |
| astral.standards.no-cross-contamination | conforms | Layered structure |
| astral.standards.no-hardcoded-sets | conforms | One catalog-key literal at existing call site; no new membership set |
| astral.standards.public-then-helpers | conforms | Public entry signatures unchanged |
| astral.state.core-decides-transitions | conforms | Untouched |
| astral.state.job-prior-states-enforced | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | conforms | Untouched |
| astral.ui.naming-conventions | conforms | No new routes/files |
| astral.ui.single-gunicorn-worker | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — layers/paths miss
- astral.git.engineer-test-tree-ban — paths miss
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.standards.database-header-inventory — layers/paths miss
- astral.standards.utils-data-late-import-only — layers/paths miss
- astral.ui.frontend-file-placement — paths miss (`src/ui/frontend/**`; plan touches `src/ui/api/**` only)

## Findings

### fix-now
(none)

### discuss
(none)

### acceptable
1. Single `task_key="simple_resume_parse"` literal at the existing call site — same pattern as prior `craft_resume_base`; catalog key authored in AST-1037 (not a growing membership set).
2. Reuse `split_craft_resume_base_payload` / normalize frozenset — shared schema keeps Paste/Open HTML contract.
3. Docstring-only Admin change — zero Paste UI.
4. Self-assessment Single-Component / high / low — honest.

— Joan
context_tokens≈52000

#### ada — 2026-07-29T16:02:17.551Z
Plan: [`docs/features/administrator/ast-1038-wire-session-resume-parse-to-ruth-task.md`](https://github.com/susansomerset/astral/blob/sub/AST-1036/AST-1038-wire-session-resume-parse-to-ruth-task/docs/features/administrator/ast-1038-wire-session-resume-parse-to-ruth-task.md) @ `a81c4939` on `origin/sub/AST-1036/AST-1038-wire-session-resume-parse-to-ruth-task`.

**Scope:** Single-Component — `run_session_resume_parse` `do_task` key → `simple_resume_parse` (+ docstring/error string); Admin parse route docstring only; no Paste UI / Judith craft / catalog edits.

**Conf:** high — AST-1037 already landed Ruth task + shared schema + normalize frozenset; AST-986 session sentinel/response contract stays put.

**Risk:** low — candidate craft stays on `craft_resume_base`; session JSON shape unchanged for Parse → Open HTML.

---

# AST-1038 — Wire Session Resume Parse to Ruth task

**Linear:** [AST-1038](https://linear.app/astralcareermatch/issue/AST-1038/wire-session-resume-parse-to-ruth-task-simple-resume-parse-function)  
**Parent:** [AST-1036](https://linear.app/astralcareermatch/issue/AST-1036/simple-resume-parse-function) — Simple Resume Parse function  
**Publish ref:** `sub/AST-1036/AST-1038-wire-session-resume-parse-to-ruth-task`

Point Admin Session Resume Paste parse at the Ruth `simple_resume_parse` task delivered by **AST-1037**, instead of Judith `craft_resume_base`. Keep the existing no-persist / no-candidate-bind response contract, session-sentinel ledger, and Style D debug on the hop. Prefer zero Paste UI change. Do **not** author task/schema/seed (sibling owns that). Do **not** change candidate-bound Judith craft.

**Prerequisite:** This sub must already include AST-1037 product tip via `origin/ftr/ast-1036-simple-resume-parse-function` (merge-on-checkout). `TASK_CONFIG["simple_resume_parse"]`, Ruth `agent_task` seed, and `_CRAFT_RESUME_NORMALIZE_TASK_KEYS` must exist before Stage 1.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | In `run_session_resume_parse` only: `do_task` uses `task_key="simple_resume_parse"`; update docstring + non-dict error string; leave ledger / synthetic ctx / Style D / split helpers as they are | core |
| `src/ui/api/api_admin.py` | Docstring on `session_resume_parse` only — still thin `@require_admin` → `run_session_resume_parse`; no request/response shape change | ui |

**No changes expected:** `src/utils/config.py` / `data/admin/agent_task.json` (AST-1037), `parse_candidate_resume`, `run_candidate_artifact_generation`, Judith `craft_resume_base` row/meta, `AdminSessionResumePaste.tsx`, Open HTML / `session_resume/html`, `src/core/agent.py` normalize gate (already covers both keys).

## Stage 1: Core wire — `run_session_resume_parse` → Ruth

**Done when:** `run_session_resume_parse` calls `do_task` with `simple_resume_parse`; success/error JSON shapes and ledger sentinel behavior are unchanged; `parse_candidate_resume` / `run_candidate_artifact_generation` still use `craft_resume_base`.

1. In `src/core/candidate.py`, locate `run_session_resume_parse` (AST-986 session paste path). Keep validation, `default_resume_structure()`, synthetic `ctx` (no `astral_candidate_id`), ledger (`ledger_task_key = "user-session-parse-resume"`, `candidate_id="session"`), `log_batch_id`, `asyncio.run(do_task(...))`, `split_craft_resume_base_payload`, Style D `debug_index` / `debug_detail` / `_debug_experience_jobs`, and `finally` flush — **do not** redesign those.

2. Change the `do_task` call from:

```python
task_key="craft_resume_base",
```

to:

```python
task_key="simple_resume_parse",
```

Keep `live_content=paste`, `index=batch_id`, `ctx=ctx`, `debug=debug` unchanged.

⚠️ **Decision:** Use the literal TASK_CONFIG key `"simple_resume_parse"` at this single call site (same pattern as the prior `"craft_resume_base"` literal). Do **not** add a new config block for one caller; do **not** invent a second session-parse entrypoint. Shared schema + normalize membership already live in config from AST-1037.

⚠️ **Decision:** Keep reusing `split_craft_resume_base_payload` / `normalize_craft_resume_base_agent_payload` (via do_task normalize frozenset). Shared schema identity means the session response contract (`resume_structure` / `base_resume` / `parsed_response`) does not change for the Paste UI or Open HTML.

3. Update the function docstring to say paste is parsed via `simple_resume_parse` (Ruth / Little), not `craft_resume_base`.

4. Update the non-dict failure string from `"craft_resume_base returned non-dict parsed_response"` to `"simple_resume_parse returned non-dict parsed_response"` (same HTTP 500 shape).

5. **Forbidden in this stage:** editing `parse_candidate_resume`, `run_candidate_artifact_generation`, `_persist_craft_dispatch_success`, `TASK_CONFIG`, `agent_task` seeds, or any React file. Grep after edit must still show `task_key="craft_resume_base"` in those candidate craft paths.

## Stage 2: Admin route docstring (thin contract unchanged)

**Done when:** `POST /api/admin/session_resume/parse` still validates body, calls `run_session_resume_parse`, returns `(body, status)` unchanged; docstring no longer claims craft-base.

1. In `src/ui/api/api_admin.py`, update the `session_resume_parse` docstring from “paste → craft_resume_base …” to “paste → simple_resume_parse (Ruth) …” (or equivalent one-liner). Do **not** change route path, `@require_admin`, request fields, or response handling.

⚠️ **Decision:** Prefer zero Paste UI change — React already posts `resume_text` and consumes `success` / `resume_structure` / `base_resume` / `parsed_response`; the wire is core-only.

## Stage 3: Compile check (plan-owned files only)

**Done when:** Touched Python modules compile; no edits under `tests/` (Betty owns the test tree).

```bash
python3 -m compileall -q src/core/candidate.py src/ui/api/api_admin.py
```

Optional sanity (venv):

```bash
python3 -c "from src.utils import config as c; assert 'simple_resume_parse' in c.TASK_CONFIG"
```

## Self-Assessment

**Scope:** `Single-Component` — one core call-site swap (+ docstring/error string) and a thin Admin docstring; no catalog/seed/UI work.

**Conf:** `high` — AST-1037 already delivered the Ruth task, shared schema, and normalize membership; AST-986 established the session sentinel / response contract this ticket only re-keys.

**Risk:** `low` — candidate Judith craft paths stay on `craft_resume_base`; session response shape unchanged; wrong key would fail `do_task` / schema immediately rather than silently corrupt candidates.

## Code Rules check

- **§1.1 / in-scope-only:** No Judith craft / Open HTML / Paste chrome / sibling catalog edits.
- **§1.4 / no-hardcoded-sets:** No new membership frozensets; single task-key literal at the existing call site (catalog key authored in AST-1037 config).
- **§2.1 / config source of truth:** Task meta/schema remain in `TASK_CONFIG` from AST-1037; this ticket only selects that key.
- **§2.2 / do-task delegation:** Still reaches the model only via `do_task`.
- **§1.5.1 / debug-contract-gated:** Preserve existing Style D gated on `debug=True`; no new ungated debug lines.
- **§3.3 imports:** UI stays ui → core; no new data imports in Admin route.
- **pattern.ui.admin-endpoint / require-auth:** Route stays thin + `@require_admin`.

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1038  
**Publish ref tip:** 054d26cf `origin/sub/AST-1036/AST-1038-wire-session-resume-parse-to-ruth-task`  
**Overall:** DISCUSS

### What's solid
- Thin wire: `run_session_resume_parse` → `task_key="simple_resume_parse"`; Admin docstring only; `@require_admin` kept.
- Style D / sentinel ledger / no-bind contract preserved; Judith craft call sites untouched in this ticket's `code()` SHA.
- Matches plan Stages 1–2; Self-Assessment Single-Component still accurate.

### Findings
**discuss (C4 straggler):** Joan Excluded `spikes-under-debug-dir`, `docs.features-single-file-per-ticket`, `engineer-test-tree-ban`, `utils-data-late-import-only`; tip three-dot (includes rolled AST-1037 + this child) makes them in-scope. Substance **conforms**. Acknowledge on resolve — no product edit expected.

### Recommended
Ada: acknowledge C4 stragglers → `resolve-child`.

## Resolution

**Date:** 2026-07-29 — Ada (`resolve-child`)

- **fix-now:** none.
- **discuss (C4 stragglers):** Acknowledged — Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, and `astral.standards.utils-data-late-import-only` on plan tip; code-rubric correctly brought them in-scope once feature docs / Betty tests / rolled AST-1037 `config.py` landed on the three-dot tip. Substance already **conforms**. No product or test-tree edits.
- **Product tip:** unchanged from review tip (`1c62a5ea`); this commit is Resolution appendix only.
