<!-- linear-archive: AST-1076 archived 2026-08-07 -->

## Linear archive (AST-1076)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1076/uat-qualify-meteorite-good-extract-error-astral-job-id-000-response  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1058 — Qualify Meteorite  
**Blocked by / blocks / related:** parent: AST-1058

### Description

## What failed

Dispatch `qualify_meteorite` on a claimed **METEORITE_NEW** job completed with errors. Ruth returned a full extract (`company_job_id`, `job_title`, `job_link`, `jd_text`) that looked correct, but consult logged `MISSING` the real astral id and `FABRICATED` id `000`, then moved the job to **METEORITE_ERROR_QUALIFY**. Same run also logged:

```
NameError: name 'result' is not defined
  File "…/src/core/agent.py", line 1549, in _store_response_block
    f"agent_data_write block_type=RESPONSE outcome={result.get('outcome')} "
```

Observed summary: `processed=1 passed=0 failed=0 errors=1` / batch finished COMPLETED with errors.

## Expected

When Ruth returns a usable title + `job_link` + visible JD for the claimed meteorite job, that job lands on **METEORITE_QUALIFIED** with those fields applied (external id on `company_job_id`). A placeholder / wrong `astral_job_id` in the model JSON must not strand a single-job batch on **METEORITE_ERROR_QUALIFY** when the payload otherwise matches the claim. Debug RESPONSE write must not NameError.

## Repro

1. Have a job in **METEORITE_NEW** with JD text (e.g. from Manage Email Create / gazer ingest).
2. Dispatch `qualify_meteorite` (Admin or scheduler) with `debug=True`.
3. Observe Ruth payload with real fields but `astral_job_id` like `"000"` (or otherwise not the claimed UUID).
4. Confirm job ends **METEORITE_ERROR_QUALIFY** and logs MISSING/FABRICATED + optional NameError in `_store_response_block`.

## Parent AC (quoted inline)

> 4. Batch task `qualify_meteorite` claims **METEORITE_NEW**, returns external job UUID, job title, `job_link`, and visible JD content; on success the job is on **METEORITE_QUALIFIED** with those fields as authoritative content.

> 6. Bogus / 404 / unusable extracts land on **METEORITE_FAILED_QUALIFY** (visible in Jobs skipped manifests).

(ERROR path is for incomplete/unusable batch mapping — not for a complete extract that only mangled the echo id.)

## Diagnosis

* **Hypothesis:** (1) `_ensure_jobs_astral_ids` / batch apply treats placeholder `astral_job_id` `"000"` as a real id, so the claimed UUID is MISSING and the row is FABRICATED → **METEORITE_ERROR_QUALIFY** even though extract fields are good. (2) `_store_response_block` debug path references undefined `result` after `save_agent_data` (NameError).
* **Correct outcome:** Single-job (and ordered) qualify_meteorite batches remap / bind the extract to the claimed job; success → **METEORITE_QUALIFIED** with title/link/jd/`company_job_id`. RESPONSE debug logging does not throw.
* **Wrong fix to avoid:** Swallow NameError and mark success anyway; delete debug logging; accept any fabricated id without binding to claim; move ERROR jobs to QUALIFIED without applying fields; weaken AC so ERROR is OK when payload “looks fine.”
* **Related siblings / contracts:** AST-1062 (qualify apply); AST-1060 (task/schema/states). Must still fail truly unusable extracts to **METEORITE_FAILED_QUALIFY** / error siblings.

## In scope

- [X] Bind placeholder / single-job mismatched `astral_job_id` to claimed jobs before MISSING/FABRICATED (`consult._run_batch_consult`)
- [X] Fix `_store_response_block` debug path NameError (`result = save_agent_data(...)`)
- [X] Parent AC4 restored: usable extract → **METEORITE_QUALIFIED** with fields applied
- [X] `astral.standards.debug-contract-gated` — debug RESPONSE lines work without throw
- [X] `astral.state.core-decides-transitions` / content gates still → **METEORITE_FAILED_QUALIFY** for unusable extracts (AC6)

## Considered but excluded

- [X] Gazer email ingest (AST-1061)
- [X] GDL grading after **METEORITE_QUALIFIED**
- [X] Swallowing NameError / deleting debug logging
- [X] Promoting ERROR without applying fields
- [X] `tests/` / test-bible — Betty after Code Complete

## Boundaries

- [X] This bug does **not** change gazer email ingest (AST-1061) or GDL grading after **METEORITE_QUALIFIED**.
- [X] "No more stacktrace / no more error" alone is **not** done — Parent AC + Correct outcome must hold.

## Git branch (authoritative)

`sub/AST-1058/AST-1076-uat-qualify-meteorite-good-extract-error`

### Comments

#### radia — 2026-07-30T18:31:28.705Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1076
**Publish ref:** `45623fa40a9dd2a014f48f4952ad337caba5eaf7` (`origin/sub/AST-1058/AST-1076-uat-qualify-meteorite-good-extract-error`)
**Overall:** CLEAN

**Diff:** `origin/dev...origin/sub/AST-1058/AST-1076-uat-qualify-meteorite-good-extract-error` — layers `{core, docs}`.
**This ticket owns:** `_bind_response_jobs_to_claimed` before MISSING/FABRICATED; `_store_response_block` `result = save_agent_data(...)` NameError fix.

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| `astral.agent.confidence-bounds` | scoped | conforms | No confidence math; id bind only |
| `astral.agent.do-task-delegation` | scoped | conforms | Bind in consult before process; do_task unchanged |
| `astral.agent.grade-vector-validation` | scoped | conforms | No grade-vector changes |
| `astral.batch.batch-id-first` | scoped | conforms | Claim/batch_id surface untouched |
| `astral.batch.batch-id-format` | scoped | conforms | Untouched |
| `astral.batch.claim-process-release` | scoped | conforms | Claim unchanged; process receives claim-keyed rows |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | RESPONSE write restored; entity tagging intact |
| `astral.config.config-source-of-truth` | scoped | conforms | No config edits |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | Content mins unchanged |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | No secrets/env |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths miss (artifacts/**) |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | Plan under docs/features/; no spikes |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | Single AST-1076 plan |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test()/merge-tests; engineer code() |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | test() owns tests/bible |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | Core-only bind + debug fix |
| `astral.layers.import-direction` | scoped | conforms | No new layer edges |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers/paths miss (scripts) |
| `astral.layers.ui-config-driven-business-logic` | scoped | not-applicable | layers/paths miss (ui) |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | Untouched; bind precedes process |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | Still Pattern A via _run_batch_consult |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers/paths miss (ui) |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | No data-layer edits |
| `astral.standards.database-header-inventory` | scoped | not-applicable | layers/paths miss (data) |
| `astral.standards.debug-contract-gated` | scoped | conforms | NameError fix restores gated RESPONSE debug |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | One bind helper; shared via _run_batch_consult |
| `astral.standards.in-scope-only` | scoped | conforms | No gazer/GDL; wrong-fix list avoided |
| `astral.standards.logging-via-utils` | scoped | conforms | Existing debug_detail path |
| `astral.standards.no-cross-contamination` | scoped | conforms | Digit/empty-only multi bind; listing happy-path intact |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | Bind rules are placeholder predicates, not state sets |
| `astral.standards.public-then-helpers` | scoped | conforms | Helper near _ensure_jobs_astral_ids |
| `astral.standards.utils-data-late-import-only` | scoped | not-applicable | layers/paths miss (utils) |
| `astral.state.core-decides-transitions` | scoped | conforms | Core still decides QUALIFIED vs FAILED_QUALIFY |
| `astral.state.job-prior-states-enforced` | scoped | conforms | No prior_states edits |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | Single qualify cycle |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers/paths miss (frontend) |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers/paths miss (ui) |
| `astral.ui.single-gunicorn-worker` | scoped | not-applicable | layers/paths miss |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | Single merge-tests(AST-1076) onto tip |
| `orch.git.commit-vocabulary` | universal | conforms | docs/code/test/merge-tests vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | Work on sub/* only |
| `orch.git.ftr-sub-topology` | universal | conforms | sub/AST-1058/AST-1076-… |
| `orch.git.merge-on-checkout` | universal | conforms | No conflicting checkout rewrite |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | No rewrite ops |
| `orch.git.no-dev-agent-branches` | universal | conforms | Ticket sub publish-ref |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | astral-AST-1058 |
| `orch.git.three-permanent-branches` | universal | conforms | No new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | Bind rules match UAT diagnosis |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stage 1 matches tip |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Meteorite FIX-UAT child |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | No canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | Betty owns tests/bible |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Assignee Hedy |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Assignee remains Hedy |
| `orch.roles.pre-commit-path-bans` | universal | conforms | Role-appropriate paths per vocabulary |

## Pattern conformance

none cited beyond In scope statutes (covered above)

## Plan adherence

Stage 1 matches tip: RESPONSE `result = save_agent_data(...)`; bind before MISSING/FABRICATED; single-job any non-claimed; multi empty/`\d{1,3}` only. Self-Assessment Single-Component matches. Wrong-fix list avoided. Parent AC4 restored path; AC6 content gates retained.

## Findings

### fix-now
(none)

### discuss
(none)

### advisory
(none)

### What’s solid
- Surgical UAT fix: claim-id bind + debug NameError; no swallow/delete-log/promote-without-fields.

### Recommended actions
- Hedy: resolve-child → User Testing.

**Notes:** Joan validate-plan uat-thin APPROVED (no full Excluded list — no C4 straggler callout). Docs append @ `45623fa4`. Product tip before docs: `d71086aa`.

context_tokens≈24000

#### betty — 2026-07-30T18:20:38.683Z
## QA test manifest — AST-1076 (FIX-UAT)

**Publish:** `origin/sub/AST-1058/AST-1076-uat-qualify-meteorite-good-extract-error` @ `d71086aa54b5195038683a7e938d46620cca0ed4`
**Betty delivery:** `merge-tests(AST-1076): origin/tests 5b90e0a4a60b58c8beb7bb26ebfc7a6760ab0146`
**FIX-UAT:** no `docs/test-bible/**` delta on ftr — no full bible re-read.

### 1. Covered paths
1. `_bind_response_jobs_to_claimed` — `TestAst1076BindResponseJobsToClaimed`
2. `"000"` echo + usable fields → QUALIFIED — `TestAst1076QualifyMeteoritePlaceholderId`
3. RESPONSE debug `result = save_agent_data(...)` — `TestAst1076StoreResponseDebugResult` (+ AST-977 emit)

### 2. Broken / obsolete
- none

### 3. Run
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst1076BindResponseJobsToClaimed \
  tests/component/core/test_consult.py::TestAst1076QualifyMeteoritePlaceholderId \
  tests/component/core/test_agent.py::TestAst1076StoreResponseDebugResult \
  tests/component/core/test_agent.py::TestAst977AgentDataDedupeDebug::test_store_response_debug_emits_write_outcome \
  -q
```

### 4. Bible shasums on publish tip
- `docs/test-bible/core/consult.md` `67c14d3b782d7622bcbbdc5781f7ae26814674a5`
- `docs/test-bible/core/agent.md` `d1215d05df1b26d81d2d72e02fa3deaa47e5fc29`

#### joan — 2026-07-30T16:45:17.927Z
[validate-plan uat-thin]
**Ticket:** AST-1076
**Overall:** APPROVED

## UAT-thin checklist

- [x] Plan cites Parent AC (quoted) — AC4 quoted in ## UAT fitness; AC6 retained for unusable extracts
- [x] Stages achieve Correct outcome / Expected — Stage 1 binds placeholder/`000` to claimed id before MISSING/FABRICATED, then process → **METEORITE_QUALIFIED** with fields; NameError fixed by assigning `result = save_agent_data(...)` (not symptom silence)
- [x] Wrong fix to avoid is not implemented — plan rejects swallow NameError, delete debug, unbound fabricated ids, ERROR→QUALIFIED without fields
- [x] No catch-and-ignore / delete-log / empty-success / bypass — debug path restored; content gates still → **METEORITE_FAILED_QUALIFY**
- [x] Sibling check — AST-1062/1060 roles unchanged; listing qualify only via shared digit/empty bind rules
- [x] Boundaries — no gazer (AST-1061), no GDL after QUALIFIED

## Notes

## UAT fitness present and AC-aligned. Medium risk (multi-job remap) mitigated by `\d{1,3}`/empty-only on multi; single-job any non-claimed bind matches diagnosis.

context_tokens≈62000

— Joan

#### hedy — 2026-07-30T16:30:29.686Z
Plan published (FIX-UAT).

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1058/AST-1076-uat-qualify-meteorite-good-extract-error/docs/features/meteorite/ast-1076-uat-qualify-meteorite-good-extract-error.md

**Self-assessment**
- **Scope:** Single-Component — `agent._store_response_block` NameError fix + `consult` claim-id bind before MISSING/FABRICATED.
- **Conf:** high — `"000"` matches assemble `i:03d` echo; debug path missing `result = save_agent_data(...)` is visible in source.
- **Risk:** Medium — multi-job remap limited to empty/`\d{1,3}` placeholders; single-job binds any non-claimed id.

---

# AST-1076 — UAT: qualify_meteorite good extract → ERROR (astral_job_id 000 + RESPONSE NameError)

**Linear:** [AST-1076](https://linear.app/astralcareermatch/issue/AST-1076/uat-qualify-meteorite-good-extract-error-astral-job-id-000-response)
**Parent:** [AST-1058](https://linear.app/astralcareermatch/issue/AST-1058/qualify-meteorite) — Qualify Meteorite
**Publish ref:** `origin/sub/AST-1058/AST-1076-uat-qualify-meteorite-good-extract-error`

UAT fix on the shipped qualify path: Ruth returns usable meteorite enrich fields but echoes assemble line index (`"000"`) as `astral_job_id`, so `_run_batch_consult` treats the claim as MISSING / response as FABRICATED and lands **METEORITE_ERROR_QUALIFY**. Same debug run NameErrors in `_store_response_block` (`result` undefined after `save_agent_data`). Restore Parent AC4 success bind; keep content-fail → **METEORITE_FAILED_QUALIFY**. Does **not** change gazer ingest or post-qualify GDL.

## UAT fitness

- **AC restored:** Parent AC4 — “Batch task `qualify_meteorite` claims **METEORITE_NEW**, returns external job UUID, job title, `job_link`, and visible JD content; on success the job is on **METEORITE_QUALIFIED** with those fields as authoritative content.” (AC6 remains for truly unusable extracts → **METEORITE_FAILED_QUALIFY**, not for complete extracts that only mangled the echo id.)
- **Correct outcome:** Single-job (and ordered) `qualify_meteorite` batches bind the extract to the claimed job; success → **METEORITE_QUALIFIED** with title / link / jd / `company_job_id`. RESPONSE debug logging does not throw.
- **Sibling check:** AST-1062 apply + AST-1060 schema/states unchanged in role; content gates still send blank/short fields to **METEORITE_FAILED_QUALIFY**; roster `qualify_job_listings` behavior unchanged except shared helpers only if the bind is scoped so listing grades paths keep today’s ID rules.
- **Not sufficient:** Removing the stacktrace / exception / ERROR state alone without binding fields onto the claimed job and reaching **METEORITE_QUALIFIED**.
- **Wrong fix rejected:** Swallow NameError and mark success anyway; delete debug logging; accept any fabricated id without binding to claim; move ERROR jobs to QUALIFIED without applying fields; weaken AC so ERROR is OK when payload “looks fine.”

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Capture `save_agent_data` return as `result` in `_store_response_block` debug path | core |
| `src/core/consult.py` | Bind placeholder / single-job mismatched `astral_job_id` to claimed jobs before MISSING/FABRICATED accounting in `_run_batch_consult` (helper + call site) | core |

No gazer / config TASK_CONFIG / dispatcher / frontend / `tests/` / bible (Betty after Code Complete).

## Stage 1: RESPONSE debug NameError + claim-id bind for qualify fields

**Done when:** `_store_response_block(..., debug=True)` never raises `NameError` on `result`; a one-job `qualify_meteorite` batch whose Ruth JSON has usable fields but `astral_job_id` `"000"` (or other non-claimed placeholder) binds to the claimed UUID, runs `process_fn`, and can reach **METEORITE_QUALIFIED**; ordered multi-job batches with `\d{1,3}` / empty echo ids bind by index when lengths match; true content-gate fails still → **METEORITE_FAILED_QUALIFY**; `python3 -m py_compile src/core/agent.py src/core/consult.py` succeeds.

1. In `src/core/agent.py` `_store_response_block`, mirror `_store_prompt_blocks`’s `_save`: assign `result = save_agent_data(...)` then use `result.get("outcome")` / `agent_data_id` / `ref_agent_data_id` in the `debug` `debug_detail` line. Keep the existing `return agent_data_id` (local id string). Do **not** delete the debug block.

2. In `src/core/consult.py`, add a small helper near `_ensure_jobs_astral_ids` (same module, public-then-helpers: helper above call site):

```python
def _bind_response_jobs_to_claimed(response_jobs: list, claimed_jobs: list) -> None:
    """Rewrite placeholder / single-job mismatched astral_job_id to claimed ids (AST-1076).

    Assemble prefixes use 000/001…; fields-output Ruth often echoes that as astral_job_id.
    """
```

Rules (literal):

- Build `claimed_ids = [j["astral_job_id"] for j in claimed_jobs if j.get("astral_job_id")]` and `claimed_set = set(claimed_ids)`.
- Skip if `response_jobs` empty or `claimed_ids` empty.
- **Single-job bind:** if `len(response_jobs) == 1` and `len(claimed_ids) == 1`: if `(response_jobs[0].get("astral_job_id") or "").strip() not in claimed_set`, set `response_jobs[0]["astral_job_id"] = claimed_ids[0]`. Return.
- **Ordered placeholder bind:** if `len(response_jobs) == len(claimed_ids)`: for each index `i`, let `aid = (response_jobs[i].get("astral_job_id") or "").strip()`; if `not aid` or `re.fullmatch(r"\d{1,3}", aid)`, set `response_jobs[i]["astral_job_id"] = claimed_ids[i]`. Do **not** overwrite a response id that is already in `claimed_set`. Do **not** overwrite a non-digit fabricated UUID on multi-job batches (leave for existing FABRICATED drop).

⚠️ **Decision — bind in `_run_batch_consult` before MISSING/FABRICATED:** Fields tasks never hit `_ensure_jobs_astral_ids` (rubric-only). Fixing only `_ensure_jobs_astral_ids` would miss `qualify_meteorite`. Call the helper for every `_run_batch_consult` after `response_jobs = parsed["jobs"]` and after grade-reason hydration, **before** `sent_ids` / `received_ids` / missing transition — so listing qualify also recovers position-echo ids if they ever appear, without changing happy-path when ids already match.

3. In `_run_batch_consult`, immediately after successful hydration of `response_jobs` (and before the `sent_ids` / `received_ids` block), call `_bind_response_jobs_to_claimed(response_jobs, jobs)`.

4. Do **not** change `qualify_meteorite` content gates, `initialize_job` mapping, pass/fail/error states, gazer, or `qualify_job_listings` process_fn. Do **not** auto-promote ERROR rows without applying fields.

**Done when (recheck):** With claimed id `C` and Ruth `{"jobs":[{"astral_job_id":"000","company_job_id":"…","job_title":"…","job_link":"https://…","jd_text":"<≥min chars>"}]}`, after bind `received_ids` contains `C`, process runs, job → **METEORITE_QUALIFIED**. Short/blank fields still → **METEORITE_FAILED_QUALIFY**. `_store_response_block(..., debug=True)` logs outcome without NameError.

## Self-Assessment

**Scope:** `Single-Component` — two core files; claim-id bind + debug write fix only.

**Conf:** `high` — NameError is a clear missing assignment; `"000"` matches assemble `i:03d` echo; diagnosis spells bind rules.

**Risk:** `Medium` — over-eager multi-job remap could mis-bind; mitigated by digit/empty-only remap on multi and single-job-only bind for any non-claimed id.

## Self-review vs ASTRAL_CODE_RULES

- **§1.5.1 debug-contract-gated:** NameError fix restores gated debug lines; no new `debug=False` noise.
- **§2.2 do-task-delegation / §2.6 core-decides-transitions:** Bind happens in consult before process; core still decides QUALIFIED vs FAILED_QUALIFY.
- **§2.4 claim-process-release:** Claim surface unchanged; process receives correctly keyed response rows.
- **§1.3 DRY:** One helper; listing + meteorite share bind via `_run_batch_consult`.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1058/AST-1076-uat-qualify-meteorite-good-extract-error`
**Plan path:** `docs/features/meteorite/ast-1076-uat-qualify-meteorite-good-extract-error.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `9ac88ac7` | bind placeholder astral_job_id + RESPONSE debug NameError |

**Tip:** `9ac88ac762e9816f0e4e74119958e98435236d30` on `origin/sub/AST-1058/AST-1076-uat-qualify-meteorite-good-extract-error`

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1076
**Publish ref:** `d71086aa54b5195038683a7e938d46620cca0ed4` (`origin/sub/AST-1058/AST-1076-uat-qualify-meteorite-good-extract-error`)
**Overall:** CLEAN

### What’s solid
- `_bind_response_jobs_to_claimed` before MISSING/FABRICATED; single-job any non-claimed; multi empty/`\d{1,3}` only.
- `_store_response_block` assigns `result = save_agent_data(...)` — NameError fixed without deleting debug.
- Content gates / QUALIFIED path unchanged; wrong-fix list avoided.

### Issues
(none)

### Recommended actions
- Hedy: resolve-child → User Testing.

## Resolution

**Date:** 2026-07-30  
**Commit:** `resolve(AST-1076): — clean`

### Against Radia review (`45623fa4` / Overall CLEAN)

- **fix-now:** none — no product changes.
- **discuss:** none.
- **advisory:** none.

Stage 1 product + Betty manifest green @ `d71086aa`; Radia docs intake @ `45623fa4` already on publish-ref before this resolve commit.
