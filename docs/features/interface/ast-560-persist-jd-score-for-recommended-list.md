<!-- linear-archive: AST-560 archived 2026-06-15 -->

## Linear archive (AST-560)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-560/persist-jd-score-for-recommended-list-the-jd-score-isnt-appearing-in  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-547 — The JD score isn't appearing in the Recommended job list.  
**Blocked by / blocks / related:** parent: AST-547

### Description

## What this implements

Fix missing **JD** phase score on the Recommended jobs list. DO/GET/LIKE show numeric values (including 0.0) but JD shows em dash for all rows. Root cause: `evaluate_jd_batch` persists `jd_grades` but not `jd_score` in `job_data`, while the UI reads `jd_score` per AST-498/522.

## Acceptance criteria

1. Recommended list rows show numeric JD score when consult grading produced a score.
2. Missing JD score still shows em dash.
3. DO/GET/LIKE display unchanged.

## Boundaries

* Does not change consult scoring math or rubrics.
* Does not implement AST-499 report modal.

## Notes for planning

See `evaluate_jd_batch` process() in `src/core/consult.py` (\~926). Compare `_apply_render_verdict_decoded_job` which saves prefix_score. UI: JobsRecommended.tsx + api_jobs.\_flatten_grades.

## Git branch (authoritative)

Parent ftr/AST-547-jd-score-recommended-list, child sub/AST-547/AST-560-persist-jd-score.

### Comments

#### ada — 2026-06-05T20:05:49.338Z
**[fix-uat]** Joan `refresh-ftr` merge conflict resolved on `origin/ftr/AST-547-jd-score-recommended-list` @ `384c0013`. Merged `origin/dev`; kept AST-560 `evaluate_jd_batch` `jd_score` persistence + strict test assertions; plan doc review/resolution sections preserved.

#### ada — 2026-06-05T20:04:45.390Z
**[fix-uat]** UAT recovery verify — `origin/ftr/AST-547-jd-score-recommended-list` @ `e955e789` contains full AST-560 scope for prep-uat.

| Artifact | Status |
|----------|--------|
| Product | `evaluate_jd_batch` `process()` persists `jd_score` (`save_data["jd_score"]` @ consult.py) |
| Tests | `TestEvaluateJdBatch` — 4/4 pass on ftr tip |
| Plan | `docs/features/interface/ast-560-persist-jd-score-for-recommended-list.md` (plan + review + resolve) |
| Bible | §7.13zs manifest present |

All AST-560 commits (`887424a7`…`e955e789`) are ancestors of ftr tip; none cherry-pick needed. Sub ref deleted post-rollup — expected.

**prep-uat:** ftr tip is good.

#### radia — 2026-06-03T01:29:30.110Z
**Review** (`origin/dev...origin/sub/AST-547/AST-560-persist-jd-score` @ `5d6f96dc`, product `0651e2e4`)

**fix-now:** none

**discuss**
- UAT on jobs JD-graded **before** this deploy: `job_data` may still lack `jd_score` (plan excludes backfill). Em dash until re-run `evaluate_jd` or a follow-up backfill — confirm acceptable for AST-547 UAT.

**advisory**
- `tests/component/core/test_consult.py` — optional symmetry: assert `jd_score` on a **failed** JD verdict path (pass + readiness skip already covered).

**What's solid (rules)**
- `src/core/consult.py` `evaluate_jd_batch` `process()`: mirrors `_apply_render_verdict_decoded_job` (~514–518) — `jd_grades` + `jd_score` when `_task_config_scored(task_key)` and `_latest_score_value(score)` not `None`; `0.0` persists; readiness skip unchanged (§1.3 DRY, §2.4 batch, §2.6 transitions).
- `TestEvaluateJdBatch` + bible §7.13zs align with plan Stages 1–2; read path (`api_jobs._flatten_grades`, `JobsRecommended`) untouched per scope.

**Doc:** [ast-560-persist-jd-score-for-recommended-list.md](https://github.com/susansomerset/astral/blob/sub/AST-547/AST-560-persist-jd-score/docs/features/interface/ast-560-persist-jd-score-for-recommended-list.md) — Radia section @ publish tip `ae1e57d8`.

#### betty — 2026-06-03T01:23:38.639Z
[check-linear]

**Tests updated for `[qa-handoff]`** — manifest item 2 fixed on `origin/sub/AST-547/AST-560-persist-jd-score` @ `5d6f96dc`.

- Dropped **`test_ast522_recommended_manifest_sections_and_phase_columns`** from manifest (removed from integration line in AST-526; not on publish ref).
- Corrected API regression node: **`tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_recommended_and_default`**
- **`docs/ASTRAL_TEST_BIBLE.md`** shasum on publish ref: `96662276d84714b514896eb5e749d06c97a9158a` — §7.13zm + §7.13zs updated.

**Manifest for `test-astral`:**

1. `python3 -m pytest tests/component/core/test_consult.py::TestEvaluateJdBatch -q`
2. `python3 -m pytest tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_recommended_and_default -q`
3. `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx`

Reassigned **Hedy** — stay **Tests Ready**.

#### chuckles — 2026-06-03T00:16:23.000Z
@Betty White — **qa-handoff return pass** on this ticket: fix manifest item 2 per Hedy's `[qa-handoff]` (drop or replace stale `test_ast522_*` from §7.13zm; correct pytest node to `TestJobsRoutes::test_list_recommended_and_default`). Publish to `origin/sub/AST-547/AST-560-persist-jd-score`; reassign Hedy when manifest is green.

#### hedy — 2026-06-02T22:53:48.396Z
**[qa-handoff]**

**Integration line:** `dev-hedy` after `git fetch` → `merge origin/dev` → `merge origin/ftr/AST-547-jd-score-recommended-list` → `merge origin/sub/AST-547/AST-560-persist-jd-score` (publish ref @ `22661c86`).

**Manifest item 1 — GREEN**
```bash
PYTHONPATH=$PWD .venv/bin/python3.12 -m pytest tests/component/core/test_consult.py::TestEvaluateJdBatch -q
# 4 passed
```

**Manifest item 3 — GREEN**
```bash
cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx
# 7 passed
```

**Manifest item 2 — cannot run as written (test/manifest defect, not product)**

```bash
python3 -m pytest tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast522_recommended_manifest_sections_and_phase_columns tests/component/ui/api/test_api_jobs.py::test_list_recommended_and_default -q
```

1. **`test_ast522_recommended_manifest_sections_and_phase_columns`** — **no collector** on publish ref @ `22661c86` or current `dev-hedy` HEAD. Grep/`git show origin/sub/…/test_config.py` empty. Test existed in `d78b57ce` (AST-522) but was removed in `f0cab18c` (AST-526 “drop stale AST-517 config tests”). Bible §7.13zm still cites it.

2. **`test_list_recommended_and_default`** — test **exists** under **`TestJobsRoutes`**; manifest node id is missing the class segment. With corrected path it passes:
   `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_recommended_and_default` → 1 passed.

**Product:** AST-560 `evaluate_jd_batch` `jd_score` persistence covered by item 1. No product fix needed from this run.

@Betty White — please either restore §7.13zm `test_ast522_*` on the publish ref (or drop from manifest if intentionally removed) and fix the `test_list_recommended_and_default` pytest node id, then reassign me.

#### betty — 2026-06-02T22:52:28.581Z
**Tests Ready** — manifest for `test-astral` on `origin/sub/AST-547/AST-560-persist-jd-score` @ `22661c86`.

1. **Primary (new assertions):** `python3 -m pytest tests/component/core/test_consult.py::TestEvaluateJdBatch -q` — `jd_score` persisted on passing JD evaluate; absent on readiness skip (`jd_readiness_skip` only).

2. **Regression (Recommended list — no product/UI diff this ticket):** §7.13zm narrowed run from bible:
   - `python3 -m pytest tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast522_recommended_manifest_sections_and_phase_columns tests/component/ui/api/test_api_jobs.py::test_list_recommended_and_default -q`
   - `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx`

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` on publish ref — shasum `75de85976ca505489f0d14a0feb6a1ee8bf8b340c3867d19e25f40e0492c17cc` (§7.13zs).

— Betty

#### hedy — 2026-06-02T22:32:12.188Z
Plan: `docs/features/interface/ast-560-persist-jd-score-for-recommended-list.md`

https://github.com/susansomerset/astral/blob/sub/AST-547/AST-560-persist-jd-score/docs/features/interface/ast-560-persist-jd-score-for-recommended-list.md

**Scope:** Single-Component — `evaluate_jd_batch` persists `jd_score` alongside `jd_grades` using the same `_latest_score_value` / `_task_config_scored` guard as `_apply_render_verdict_decoded_job`; consult tests updated. No API/UI/config scoring changes.

**Conf:** high — Root cause and mirror pattern are already documented in the ticket; one save-site change.

**Risk:** low — Additive `job_data` field; pass/fail and rubric math untouched.

Publish: `origin/sub/AST-547/AST-560-persist-jd-score` @ `887424a7`

---

# Persist jd_score for Recommended list (AST-560)

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-560/persist-jd-score-for-recommended-list-the-jd-score-isnt-appearing-in  
**Parent:** https://linear.app/astralcareermatch/issue/AST-547/the-jd-score-isnt-appearing-in-the-recommended-job-list  

**Publish ref (origin):** `sub/AST-547/AST-560-persist-jd-score`  
**Parent integration ref:** `ftr/AST-547-jd-score-recommended-list`  

When `evaluate_jd_batch` grades a JD-ready job, it already computes a numeric rubric score for `latest_score` / dispatch sorting (AST-350) but only writes `jd_grades` into `job_data`. The Recommended list reads `jd_score` via `GET /api/jobs?view=recommended` → `_flatten_grades` (AST-522). DO/GET/LIKE columns work because `_apply_render_verdict_decoded_job` persists `{save_prefix}_score` alongside grades; JD batch `process()` does not.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | In `evaluate_jd_batch` → inner `process()`, persist `jd_score` in `tracker.save_job_data` when a numeric score is produced | core |
| `tests/component/core/test_consult.py` | Extend `evaluate_jd_batch` tests to assert `jd_score` is saved when rubric scoring runs | tests |

**Not in scope:** `src/utils/config.py` (no scoring/rubric changes), `api_jobs.py`, `JobsRecommended.tsx`, `StateUiContext.tsx`, consult math in `_render_score` / `_render_pass_fail`, AST-499 report modal, one-time backfill of historical rows missing `jd_score` in `job_data`.

**Verified (plan time):** `_flatten_grades` already lifts `jd_score` from `job_data`; UI `formatPhaseScore` shows em dash when the field is absent. Root cause is write path only (~line 927 in `consult.py`).

---

## Stage 1: Persist `jd_score` in `evaluate_jd_batch`

**Done when:** After a successful JD evaluate with candidate `jobdesc_rubric` present, `tracker.save_job_data` receives both `jd_grades` and `jd_score` (float) for that job; when no numeric score is produced (`score is None`, e.g. empty rubric list), payload remains grades-only; `python3 -m py_compile src/core/consult.py` passes.

1. In `src/core/consult.py`, locate `evaluate_jd_batch` inner function `process` (currently ~919–935).

2. Replace the single-key save:

   ```python
   tracker.save_job_data(aid, {"jd_grades": grades})
   ```

   with the same pattern as `_apply_render_verdict_decoded_job` (~514–523):

   ```python
   save_data: Dict[str, Any] = {"jd_grades": grades}
   normalized_score = _latest_score_value(score)
   if _task_config_scored(task_key) and normalized_score is not None:
       save_data["jd_score"] = normalized_score
   tracker.save_job_data(aid, save_data)
   ```

   Use the outer `task_key` variable (`"evaluate_jd"`) already bound in `evaluate_jd_batch` — do not hardcode a different task key.

3. Do **not** change `_transition_job_state_for_task(task_key, [aid], to_state, score)` — it already receives the same `score` for `latest_score`.

4. Do **not** alter pass/fail logic, rubric validation, readiness skip path (`jd_readiness_skip`), or `_render_score` / `_render_pass_fail` behavior.

5. Run `python3 -m py_compile src/core/consult.py`.

⚠️ **Decision:** Persist `jd_score` only when `_task_config_scored("evaluate_jd")` and `_latest_score_value(score)` is non-`None`, matching `_apply_render_verdict_decoded_job` so `0.0` is stored and displayed (not treated as missing). Key name is literal `jd_score` to align with `TASK_CONFIG["evaluate_jd"]["grades_key"]` → `jd_grades` and `JOBS_RECOMMENDED_PHASE_SCORE_COLUMNS`.

---

## Stage 2: Consult component tests

**Done when:** `python3 -m pytest tests/component/core/test_consult.py -k evaluate_jd_batch -q` passes with updated save assertions.

1. In `tests/component/core/test_consult.py`, class/methods that mock `tracker.save_job_data` for `evaluate_jd_batch` (e.g. `test_saves_grades_on_pass` ~1916–1918):

   - After `save.assert_called_once()`, assert the second argument dict includes `"jd_grades"` (existing).
   - Assert `"jd_score" in saved` and `saved["jd_score"]` is a finite `float` when the test supplies a rubric and the mocked agent returns passing grades (same cases that expect `out["passed"] == 1`).

2. In `test_skips_short_jd_without_agent_call` (~1974): assert saved payload does **not** contain `jd_score` (readiness skip — no agent scoring).

3. Do **not** add new test files or change `docs/ASTRAL_TEST_BIBLE.md` in this ticket (Betty owns bible/manifest updates at Code Complete if needed).

4. Run `python3 -m pytest tests/component/core/test_consult.py -k evaluate_jd_batch -q`.

---

## Self-Assessment

**Scope:** `Single-Component` — One persistence fix in `evaluate_jd_batch`’s `process()` closure plus aligned consult unit assertions; no API or frontend changes.

**Conf:** `high` — Mirrors an existing, proven save path in `_apply_render_verdict_decoded_job`; ticket and codebase already identify the missing field.

**Risk:** `low` — Additive `job_data` field only; pass/fail transitions and scoring math unchanged; worst case is a wrong float in a display column for new JD runs.

---

## Self-review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses `_latest_score_value` and `_task_config_scored` instead of duplicating score normalization. |
| §2.1 config | No new config keys; `evaluate_jd` already `scored: True`. |
| §2.4 batch | No change to claim/process/release; same `save_job_data` call site. |
| §2.6 state machine | Transitions unchanged. |
| §3.3 imports | No new imports if `Dict`, `Any` already imported at module top (verify; add only if missing). |
| §3.5 naming | `jd_score` matches existing flatten keys and phase column `field`. |

No conflicts requiring `conf-!!-NONE`.

---

## Review (build)

**Built:** `origin/sub/AST-547/AST-560-persist-jd-score` @ `0651e2e4` (product: persist `jd_score` in `evaluate_jd_batch` `process()`).

**Out of build scope (Betty / qa-astral):** Plan Stage 2 consult component test assertions per `build-astral` test-tree ban.
