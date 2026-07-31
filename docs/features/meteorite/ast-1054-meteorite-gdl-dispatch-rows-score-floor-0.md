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
