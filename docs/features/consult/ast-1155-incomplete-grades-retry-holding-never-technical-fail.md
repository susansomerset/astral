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
