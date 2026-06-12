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
