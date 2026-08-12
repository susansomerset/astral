<!-- linear-archive: AST-898 archived 2026-08-02 -->

## Linear archive (AST-898)

**Archived:** 2026-08-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-898/new-retry-qualify-holding-and-retire-valid-title-retry-new-jobs-are  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-895 — NEW jobs are going to VALID_TITLE_RETRY state  
**Blocked by / blocks / related:** parent: AST-895

### Description

## What this implements

Register **NEW_RETRY** as the qualify retry holding state for jobs that enter `qualify_job_listings` from **NEW**, route recoverable first-attempt failures to **NEW_RETRY** (not **VALID_TITLE_RETRY**), companion-claim **NEW**+**NEW_RETRY** on the primary qualify dispatch row, skip title screening on the second attempt, leave existing **VALID_TITLE_RETRY** jobs to drain, and fully retire **VALID_TITLE_RETRY** for new traffic (state + companions) per parent decisions.

## Acceptance criteria

1. A job that enters `qualify_job_listings` in **NEW** and suffers a recoverable first-attempt failure ends in **NEW_RETRY** (observable on the job record) — never newly transitioned to **VALID_TITLE_RETRY** by that path.
2. A job in **NEW_RETRY** is included in Available / claim for `qualify_job_listings` when the Scheduled Action trigger is **NEW**.
3. A recoverable failure on a job already in **NEW_RETRY** moves it to the configured terminal qualify error state — it does not remain in or re-enter **NEW_RETRY**.
4. A second attempt from **NEW_RETRY** runs the qualify AI hop without re-running title screening.
5. A clean second-attempt succeed/fail grade path from **NEW_RETRY** still reaches the same pass/fail outcomes as a successful first-attempt qualify (no permanent stuck state solely because the job retried).
6. Admin/UI job state lists that surface configured job states include **NEW_RETRY** with a clear label.
7. After cutover, new recoverable first-attempt failures from the **NEW** qualify path do not enter **VALID_TITLE_RETRY**; that holding state is retired for new traffic (existing **VALID_TITLE_RETRY** jobs may remain until they drain).
8. With `debug=True` on the touched qualify / batch-failure routing path: per-job index headers (Style D) show identity and destination state; working detail lines use `|` and include enough context to see **NEW** → **NEW_RETRY** vs **NEW_RETRY** → terminal.

## Boundaries

Does not change qualify grading math or other job retry pairs. Does not migrate existing **VALID_TITLE_RETRY** jobs to **NEW_RETRY**. Does not restore a separate `validate_title` dispatch task.

## Notes for planning

* **JOB_STATES** / companion claim (**dispatch_claim_states**) are config source of truth (ASTRAL_CODE_RULES §2.1).
* Prior art: **AST-797** qualify @ NEW + VALID_TITLE_RETRY companion; **AST-642** per-entity retry vs error; roster **AST-882** one-retry patterns.
* Susan answers: leave existing VALID_TITLE_RETRY to drain; fully retire VALID_TITLE_RETRY for new traffic; NEW_RETRY second attempt = qualify AI only (no title re-screen).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-895-new-retry-qualify-holding`, child `sub/AST-895/<child-segment>`. Created at dispatch-parent.

**Publish ref:** `origin/sub/AST-895/ast-898-new-retry-qualify-holding`

### Comments

#### radia — 2026-07-15T05:27:34.454Z
### AST-898 review (`origin/dev`…`origin/sub/AST-895/ast-898-new-retry-qualify-holding`)

**Product** @ `8d0a865` + `1663671` · publish tip **`f441c0d`** · [review doc](https://github.com/susansomerset/astral/blob/sub/AST-895/ast-898-new-retry-qualify-holding/docs/features/consult/ast-898-new-retry-qualify-holding.md) § Review

#### What's solid

- **Plan fidelity:** Stage 1 registry/UI + Stage 2 AI filter / fail debug match the plan: `NEW`/`VALID_TITLE` `retry_state` → `NEW_RETRY`, `VALID_TITLE_RETRY` drain-only, title screen stays `NEW`-only, AI hop keeps `VALID_TITLE_RETRY` + adds `NEW_RETRY`.
- **§2.1 / §2.6:** Holding dest still via `_consult_batch_fail_dest` + `JOB_STATES` (no parallel qualify dest map). Verified: `VALID_TITLE`→`NEW_RETRY`, `NEW_RETRY`→`ERROR_QUALIFY_JOB_LISTINGS`, `dispatch_claim_states("NEW","job")==["NEW","NEW_RETRY"]`.
- **§1.5.1:** `bad_grades` and short-title fail paths emit Style D `debug_index` + `|` detail only when `debug=True`.
- **Boundaries:** No dispatcher/DB companion-row edits; no migrate of existing `VALID_TITLE_RETRY` jobs.

#### Issues

None — no fix-now / discuss.

#### Recommended actions

| Action | Owner | Notes |
|--------|-------|-------|
| _(none)_ | — | Clean — ready for resolve-child / merge-child rollup |

#### betty — 2026-07-15T05:21:30.404Z
1. `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst898NewRetryQualifyHolding tests/component/utils/test_config.py::TestAst641DispatchClaimStates tests/component/utils/test_config.py::TestAst797ConfigRuntimeCutover tests/component/utils/test_config.py::TestAst882DispatchClaimStates -q`
2. `./scripts/testing/run_component_tests.sh tests/component/core/test_consult.py::TestAst898QualifyNewRetry tests/component/core/test_consult.py::TestConsultBatchFailDest tests/component/core/test_consult.py::TestAst797QualifyInlineValidateTitle tests/component/core/test_consult.py::TestAst642PerEntityBatchRetry -q`
3. `./scripts/testing/run_component_tests.sh tests/component/core/test_dispatcher.py::TestRunUnified::test_ast641_primary_job_trigger_passes_union_claim_states tests/component/core/test_dispatcher.py::TestRunUnified::test_ast641_retry_only_job_trigger_single_claim_state -q`

**Broken / revised:** claim companions `NEW`/`VALID_TITLE` → `NEW_RETRY`; `_consult_batch_fail_dest(VALID_TITLE)` → `NEW_RETRY`; AST-642 rubric_criteria fixture (hydration hard-fail with empty criteria).

`origin/sub/AST-895/ast-898-new-retry-qualify-holding` @ `01f8564` (`merge-tests(AST-898): origin/tests 5219957a5c1ae17b73e456db1feb8b95cafd7e2b`)

- `docs/test-bible/utils/config.md` shasum `40e7d3ac8dc78e4017268574bbab8bc58327e6e9`
- `docs/test-bible/core/consult.md` shasum `697c1db68bff593ff5b77571bb696e862822ba29`

#### hedy — 2026-07-15T05:10:59.503Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-895/ast-898-new-retry-qualify-holding/docs/features/consult/ast-898-new-retry-qualify-holding.md

**Scope:** Single-Component — `config.py` JOB_STATES/UI lists + `consult.py` qualify AI filter and fail-path debug; no dispatcher/DB migration this ticket (drain keeps AST-797 VALID_TITLE_RETRY companions).

**Conf:** high — reuses AST-642 `_consult_batch_fail_dest`, AST-882 registry `retry_state` companion claim, and AST-797 inline title screen; only holding-state name + AI filter membership change.

**Risk:** Medium — wrong priors or dropping VALID_TITLE_RETRY from the AI filter strands drain retries; a wrong `VALID_TITLE.retry_state` either reintroduces VALID_TITLE_RETRY traffic or terminals too early.

Root fix locked in plan: after title screen the entity is VALID_TITLE, so `VALID_TITLE.retry_state` → NEW_RETRY (not a consult special-case). NEW.retry_state → NEW_RETRY for companion claim on the primary qualify row.

---

# AST-898 — NEW_RETRY qualify holding and retire VALID_TITLE_RETRY

- **Linear (this ticket):** [AST-898](https://linear.app/astralcareermatch/issue/AST-898/new-retry-qualify-holding-and-retire-valid-title-retry-new-jobs-are)
- **Parent (coordination only):** [AST-895](https://linear.app/astralcareermatch/issue/AST-895/new-jobs-are-going-to-valid-title-retry-state) — NEW jobs are going to VALID_TITLE_RETRY state
- **Publish ref:** `origin/sub/AST-895/ast-898-new-retry-qualify-holding`

## Summary

After **AST-797**, `qualify_job_listings` claims jobs in **NEW**, runs inline title screening (`NEW` → `VALID_TITLE` / `INVALID_TITLE`), then the qualify AI hop. Recoverable first-attempt AI failures still look up `JOB_STATES["VALID_TITLE"]["retry_state"]` = **VALID_TITLE_RETRY**, so jobs that entered from **NEW** land in the wrong holding state. This ticket registers **NEW_RETRY**, points both **NEW** and **VALID_TITLE** `retry_state` at **NEW_RETRY**, companion-claims **NEW**+**NEW_RETRY** on the primary qualify row (`trigger_state=NEW`), includes **NEW_RETRY** in the AI hop (skip title re-screen), leaves existing **VALID_TITLE_RETRY** jobs + companion dispatch rows to drain, and stops all new qualify-path traffic from entering **VALID_TITLE_RETRY**.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Register **NEW_RETRY**; set `NEW`/`VALID_TITLE` `retry_state` → **NEW_RETRY**; priors on pass/fail + review UI + grades field | utils |
| `src/core/consult.py` | Qualify AI filter includes **NEW_RETRY**; `_INPUT_STATE_TO_TASK` map; §1.5.1 debug_index on fail→dest for qualify retry routing | core |

**Verify only (Betty / qa-child — engineer does not edit in build-child):**

| File | Change |
|------|--------|
| `tests/component/utils/test_config.py` | `dispatch_claim_states("NEW","job") == ["NEW","NEW_RETRY"]`; `_consult_batch_fail_dest` matrix via config (`VALID_TITLE`→`NEW_RETRY`, `NEW_RETRY`→error); **VALID_TITLE_RETRY** still in registry |
| `tests/component/core/test_consult.py` | Qualify: **NEW** recoverable fail → **NEW_RETRY** (not **VALID_TITLE_RETRY**); **NEW_RETRY** second fail → `ERROR_QUALIFY_JOB_LISTINGS`; **NEW_RETRY** jobs skip `validate_title_batch`; pass/fail from **NEW_RETRY** still reaches `PASSED_JOBLIST`/`FAILED_JOBLIST`; drain path: **VALID_TITLE_RETRY** second fail still terminals |
| `docs/test-bible/utils/config.md`, `docs/test-bible/core/consult.md` | Wording: qualify @ **NEW** companions **NEW_RETRY**; **VALID_TITLE_RETRY** drain-only |

**Out of scope:** qualify grading math; other job retry pairs (`JD_READY`/`JD_READY_RETRY`, etc.); restoring `validate_title` dispatch; migrating existing **VALID_TITLE_RETRY** jobs to **NEW_RETRY**; deleting AST-797 **VALID_TITLE_RETRY** companion `dispatch_task` rows (drain needs them until empty — post-drain cleanup is a follow-up, not this ticket).

---

## Stage 1: JOB_STATES + UI config — NEW_RETRY registry and claim companion

**Done when:** `JOB_STATES` contains **NEW_RETRY** with priors that allow transitions from **NEW** and **VALID_TITLE`; `dispatch_claim_states("NEW", "job")` returns `["NEW", "NEW_RETRY"]`; `_consult_batch_fail_dest`-relevant registry reads send first-attempt **VALID_TITLE** failures to **NEW_RETRY** and **NEW_RETRY** failures to the qualify `error_state` path (no nested retry); Jobs In Review UI / admin state lists surface **NEW_RETRY** with label **"New (retry)"**; **VALID_TITLE_RETRY** remains in the registry and UI for drain visibility.

1. In `src/utils/config.py` `JOB_STATES`, change the **NEW** entry from unrestricted-only to also carry the retry holding pointer:

   ```python
   "NEW": {"prior_states": None, "retry_state": "NEW_RETRY"},
   ```

2. Change the **VALID_TITLE** entry so first-attempt recoverable failures after inline title screening route to **NEW_RETRY** (this is the cutover that stops new traffic into **VALID_TITLE_RETRY**):

   ```python
   "VALID_TITLE": {"prior_states": ["NEW"], "retry_state": "NEW_RETRY"},
   ```

   ⚠️ **Decision:** Keep `retry_state` on **VALID_TITLE** (pointed at **NEW_RETRY**), do **not** invent special-case fail logic inside `consult.py` for this hop. After title screening the entity's current state is **VALID_TITLE**, and `_consult_batch_fail_dest` already reads `JOB_STATES[current]["retry_state"]` (AST-642). Pointing **VALID_TITLE.retry_state** at **NEW_RETRY** is the minimal, config-driven fix for AC1/AC7.

3. Insert **NEW_RETRY** immediately after **VALID_TITLE_RETRY** (keep **VALID_TITLE_RETRY** in place for drain):

   ```python
   "VALID_TITLE_RETRY": {"prior_states": ["VALID_TITLE"]},  # drain-only; no new writes from NEW qualify path
   "NEW_RETRY": {"prior_states": ["NEW", "VALID_TITLE"]},  # qualify_job_listings retry holding (post-AST-898)
   ```

   ⚠️ **Decision:** Priors include both **NEW** (if a fail path ever sees pre-title state) and **VALID_TITLE** (the real post–title-screen state today). Do **not** list **VALID_TITLE_RETRY** as a prior of **NEW_RETRY** — no migrate-in-place.

4. Extend pass/fail priors so second-attempt grade outcomes can leave **NEW_RETRY**:

   - `PASSED_JOBLIST["prior_states"]`: add `"NEW_RETRY"` (keep existing entries including **NEW**, **VALID_TITLE**, **VALID_TITLE_RETRY**, **JD_READY**, **JD_READY_RETRY**).
   - `FAILED_JOBLIST["prior_states"]`: add `"NEW_RETRY"` alongside **VALID_TITLE** and **VALID_TITLE_RETRY**.

5. In `IN_REVIEW_STATES`, insert `"NEW_RETRY"` immediately after `"VALID_TITLE_RETRY"` (ordered list for Jobs UI / nav counts).

6. In `JOBS_IN_REVIEW_UI_SECTIONS`, insert after the **VALID_TITLE_RETRY** row:

   ```python
   {"state": "NEW_RETRY", "label": "New (retry)"},
   ```

   Keep the **VALID_TITLE_RETRY** row labeled `"Valid Title (retry)"` so operators can still see draining jobs.

7. In `JOBS_IN_REVIEW_GRADE_FIELD`, add `"NEW_RETRY": "joblist_grades"` next to the existing `"VALID_TITLE_RETRY": "joblist_grades"` entry.

8. Do **not** edit `src/data/database.py` in this stage (or later): do **not** delete AST-797 `qualify_job_listings` / `VALID_TITLE_RETRY` companion rows; do **not** seed a **NEW_RETRY** companion row — companion claim is registry-driven via `NEW.retry_state` + existing `dispatch_claim_states` (AST-882 pattern). Admin list of job states (`list(JOB_STATES.keys())` in admin) picks up **NEW_RETRY** automatically — no separate admin hardcoded list edit.

**Manual check (no commit of throwaway notes):** from a Python REPL after the edit, `dispatch_claim_states("NEW", "job") == ["NEW", "NEW_RETRY"]` and `dispatch_claim_states("VALID_TITLE_RETRY", "job") == ["VALID_TITLE_RETRY"]`.

---

## Stage 2: qualify_job_listings — AI hop includes NEW_RETRY + debug destinations

**Done when:** A mixed claim of **NEW** + **NEW_RETRY** runs title screening **only** on **NEW** rows; **NEW_RETRY** jobs go straight to the qualify AI hop; recoverable batch failures from **VALID_TITLE** (post-title) transition to **NEW_RETRY**; recoverable failures from **NEW_RETRY** transition to `TASK_CONFIG["qualify_job_listings"]["error_state"]` (`ERROR_QUALIFY_JOB_LISTINGS`); with `debug=True`, each fail→dest path emits a Style D `debug_index` whose `outcome` names the destination so **NEW/VALID_TITLE → NEW_RETRY** is distinguishable from **NEW_RETRY → ERROR_QUALIFY_JOB_LISTINGS**. Clean pass/fail from **NEW_RETRY** still reaches `PASSED_JOBLIST` / `FAILED_JOBLIST` via existing `process` + priors from Stage 1.

1. In `src/core/consult.py` `_INPUT_STATE_TO_TASK`, add:

   ```python
   "NEW_RETRY": "qualify_job_listings",
   ```

   Leave the existing `"VALID_TITLE_RETRY": "qualify_job_listings"` entry (drain / legacy map).

2. In `qualify_job_listings`, change the AI-eligible filter from:

   ```python
   if (j.get("state") or "") in ("VALID_TITLE", "VALID_TITLE_RETRY")
   ```

   to:

   ```python
   if (j.get("state") or "") in ("VALID_TITLE", "VALID_TITLE_RETRY", "NEW_RETRY")
   ```

   Do **not** change the title-screen gate — it must remain `state == "NEW"` only (already true). That is what satisfies AC4 (second attempt = qualify AI only).

   ⚠️ **Decision:** Keep **VALID_TITLE_RETRY** in the AI filter so the drain companion row (trigger **VALID_TITLE_RETRY**) still runs qualify AI without re-title-screening. Removing it would strand drain jobs.

3. Fail routing uses existing `_consult_batch_fail_dest` — **do not** fork a qualify-only dest helper. After Stage 1 config, `_consult_batch_fail_dest("VALID_TITLE", error_state)` returns `"NEW_RETRY"` and `_consult_batch_fail_dest("NEW_RETRY", error_state)` returns `error_state`. Confirm by reading the helper; if the helper body has drifted from AST-642 semantics, **stop and comment on the parent** — do not invent a parallel table.

4. Debug contract (AC8) — when `debug=True`, ensure fail→dest emissions exist on the paths that actually write holding/terminal states for this ticket:

   a. In `_run_batch_consult`, immediately **before** `_transition_batch_consult_failures(task_key, bad_rows, error_state)` (the `bad_grades` block near the end), if `debug` and `bad_rows` is non-empty, loop with index `1..len(bad_rows)` and emit:

   ```python
   logger.debug_index(
       func=f"consult._run_batch_consult({task_key})",
       index=bi,
       total=len(bad_rows),
       identifier=_consult_job_identifier(row),
       outcome=f"bad_grades -> {_consult_batch_fail_dest(row.get('state'), error_state)}",
   )
   logger.debug_detail(
       f"astral_job_id={row.get('astral_job_id')!r} from_state={row.get('state')!r}"
   )
   ```

   (Mirror the existing missing-ID `debug_index` block already above it.)

   b. In `qualify_job_listings` `process`, on the short-title branch that already calls `_consult_batch_fail_dest`, when `debug=True` also emit a `debug_index` (same `func="consult.qualify_job_listings"` style as the input-job headers in that function, or `consult._run_batch_consult(qualify_job_listings)` — pick **one** and stay consistent with nearby headers in that function) with `outcome` like `title too short -> {dest}` and a `|` detail line noting `from_state=…`.

   c. Do **not** emit new debug lines when `debug=False`. Do **not** change grade math or `assemble` / `process` pass/fail destinations beyond the dest string now coming from config.

5. No other files in this stage. Dispatcher already uses `dispatch_claim_states` — Stage 1 makes the NEW companion real without dispatcher edits.

---

## Self-Assessment

**Scope:** `Single-Component` — `config.py` job registry/UI lists plus `consult.py` qualify filter and fail-path debug; no dispatcher/data-layer schema change.

**Conf:** `high` — reuses AST-642 `_consult_batch_fail_dest`, AST-882 registry `retry_state` companion claim, and AST-797 inline title screen; only the holding-state name and AI filter membership change.

**Risk:** `Medium` — wrong priors or dropping **VALID_TITLE_RETRY** from the AI filter would strand retries or break drain; a bug in `VALID_TITLE.retry_state` would either reintroduce **VALID_TITLE_RETRY** traffic or terminal too early.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|-------|
| §1.4 / §2.1 config source of truth | State names and retry pairing live only in `JOB_STATES`; no new hardcoded dest strings in consult beyond existing helper. |
| §2.6 state machine | One-retry: primary (`NEW`/`VALID_TITLE`) → `NEW_RETRY`; holding → `error_state`. Tracker still enforces `prior_states`. |
| §1.5.1 debug | New lines gated on `debug=True`; Style D `debug_index` + `|` detail; no `[DEBUG]` info spam. |
| §1.3 DRY | Reuse `_consult_batch_fail_dest` / `dispatch_claim_states`; no parallel dest map. |
| §3.3 imports | No new cross-layer imports. |

No rule conflicts that would force `conf-!!-NONE`.

## Build

- **Publish tip:** `origin/sub/AST-895/ast-898-new-retry-qualify-holding` @ `1663671370ba8b4d52724be7d41635f1ac87b510`
- Stage 1: `8d0a865` — NEW_RETRY registry + NEW companion claim
- Stage 2: `1663671` — qualify AI hop includes NEW_RETRY + fail-path debug

## Review

**Radia** · `origin/dev`…`origin/sub/AST-895/ast-898-new-retry-qualify-holding` @ `01f8564` · product `8d0a865` + `1663671`

### What's solid

- **Plan fidelity:** Stage 1 registry/UI + Stage 2 AI filter / fail debug match the plan line-for-line: `NEW`/`VALID_TITLE` `retry_state` → `NEW_RETRY`, `VALID_TITLE_RETRY` drain-only, title screen stays `NEW`-only, AI hop keeps `VALID_TITLE_RETRY` + adds `NEW_RETRY`.
- **§2.1 / §2.6:** Holding dest still via `_consult_batch_fail_dest` + `JOB_STATES` (no parallel qualify dest map). Verified: `VALID_TITLE`→`NEW_RETRY`, `NEW_RETRY`→`ERROR_QUALIFY_JOB_LISTINGS`, `dispatch_claim_states("NEW","job")==["NEW","NEW_RETRY"]`.
- **§1.5.1:** `bad_grades` and short-title fail paths emit Style D `debug_index` + `|` detail only when `debug=True`.
- **Boundaries:** No dispatcher/DB companion-row edits; no migrate of existing `VALID_TITLE_RETRY` jobs.

### Issues

None (no fix-now / discuss).

### Recommended actions

| Action | Owner | Notes |
|--------|-------|-------|
| _(none)_ | — | Clean — ready for resolve-child / merge-child rollup |

## Resolution

**2026-07-15** — Radia clean sign-off (`docs(AST-898): Radia review — clean` @ `f441c0d`). No fix-now / discuss items. No product delta this resolve pass.

- **Publish tip after resolve:** `origin/sub/AST-895/ast-898-new-retry-qualify-holding` (this commit)
- §9a dry-run vs `origin/dev` and `origin/ftr/AST-895-new-retry-qualify-holding` — clean

---

## Bug: AST-1338 — Register METEORITE_NEW_RETRY qualify holding (mirror AST-898)

Pattern twin of this doc's AST-898 stages for meteorite qualify only. Ancestor AST-898 stays archived; do not re-parent. Parent mini-bug: [AST-1319](https://linear.app/astralcareermatch/issue/AST-1319). Publish ref: `origin/sub/AST-1319/AST-1338-register-meteorite-new-retry-qualify-holding`.

### As-is

`JOB_STATES["METEORITE_NEW"]` has no `retry_state`. Recoverable `qualify_meteorite` batch failures (missing IDs / bad response rows / envelope failure routed through `_consult_batch_fail_dest` → `_transition_batch_consult_failures`) therefore land straight on `TASK_CONFIG["qualify_meteorite"]["error_state"]` = **METEORITE_ERROR_QUALIFY** on the first strike. `dispatch_claim_states("METEORITE_NEW", "job")` returns only `["METEORITE_NEW"]` — no companion holding to reclaim.

### To-be

Same one-retry shape as AST-898's `NEW` → `NEW_RETRY` → `ERROR_QUALIFY_JOB_LISTINGS`:

1. Recoverable first-attempt failure from **METEORITE_NEW** → **METEORITE_NEW_RETRY**.
2. `dispatch_claim_states("METEORITE_NEW", "job")` == `["METEORITE_NEW", "METEORITE_NEW_RETRY"]` so the existing `qualify_meteorite` @ **METEORITE_NEW** dispatch row companion-claims the holding (registry-driven; no new DB companion row).
3. Recoverable failure already on **METEORITE_NEW_RETRY** → **METEORITE_ERROR_QUALIFY** (no nested retry).
4. Clean second-attempt pass/fail from the holding still reaches **METEORITE_QUALIFIED** / **METEORITE_FAILED_QUALIFY** (and bot → **BOT_BLOCKED**) via existing `qualify_meteorite` `process` + updated priors.
5. Jobs In Review UI / admin state lists surface **METEORITE_NEW_RETRY** with label **"Meteorite New (retry)"**.

### Repro

Fixture shape (no DB seed — file/JSON persistence): a job dict with `state="METEORITE_NEW"` entering `qualify_meteorite` / `_run_batch_consult` where the agent response omits that job's `astral_job_id` (or otherwise routes the row through `_consult_batch_fail_dest`).

- **Broken today:** `_consult_batch_fail_dest("METEORITE_NEW", "METEORITE_ERROR_QUALIFY")` returns `"METEORITE_ERROR_QUALIFY"`; job transitions to **METEORITE_ERROR_QUALIFY** on first strike.
- **After fix:** same call returns `"METEORITE_NEW_RETRY"`; a second identical miss from `state="METEORITE_NEW_RETRY"` returns `"METEORITE_ERROR_QUALIFY"`.

### Root cause

Absence of `retry_state` on **METEORITE_NEW**. `_consult_batch_fail_dest` (AST-642) already implements primary → `retry_state` / holding → `error_state`; meteorite qualify never wired the primary pointer. AST-1053 explicitly deferred `METEORITE_NEW_RETRY`; AST-1319 / this bug supersedes that deferral for the qualify hop only. Content-gate fails inside `qualify_meteorite.process` that write `cfg["fail_state"]` (**METEORITE_FAILED_QUALIFY**) or `bot_blocked_state` are intentional outcomes — not this retry path.

### Proposed change

Config-driven mirror of AST-898 Stage 1; **no** VALID_TITLE intermediate and **no** qualify AI-filter membership edit (meteorite has no inline title-screen split — every claimed row already runs the same `process`).

1. In `src/utils/config.py` `JOB_STATES`, point the primary at the new holding:

   ```python
   "METEORITE_NEW": {"prior_states": None, "retry_state": "METEORITE_NEW_RETRY"},
   ```

2. Insert **METEORITE_NEW_RETRY** immediately after **METEORITE_NEW** (before **METEORITE_QUALIFIED**):

   ```python
   "METEORITE_NEW_RETRY": {"prior_states": ["METEORITE_NEW"]},  # qualify_meteorite retry holding (AST-1338)
   ```

   No `retry_state` on the holding (second strike → `error_state` via `_consult_batch_fail_dest`).

3. Extend leave-holding / terminal priors so a second attempt can graduate or fail cleanly:

   - `METEORITE_QUALIFIED["prior_states"]`: add `"METEORITE_NEW_RETRY"` (keep existing **METEORITE_NEW**, **METEORITE_FAILED_JD**, **METEORITE_ERROR_EVALUATE_JD**).
   - `METEORITE_FAILED_QUALIFY["prior_states"]`: `["METEORITE_NEW", "METEORITE_NEW_RETRY"]`.
   - `METEORITE_ERROR_QUALIFY["prior_states"]`: `["METEORITE_NEW", "METEORITE_NEW_RETRY"]`.
   - `BOT_BLOCKED["prior_states"]`: add `"METEORITE_NEW_RETRY"` alongside existing **PASSED_JOBLIST** / **METEORITE_NEW** (bot classification on a second attempt must still transition).

4. UI / ordered lists (AC5):

   - `IN_REVIEW_STATES`: insert `"METEORITE_NEW_RETRY"` immediately after `"METEORITE_NEW"`.
   - `JOBS_IN_REVIEW_UI_SECTIONS`: insert `{"state": "METEORITE_NEW_RETRY", "label": "Meteorite New (retry)"}` immediately after the **METEORITE_NEW** row.

5. Do **not** add a `JOBS_IN_REVIEW_GRADE_FIELD` entry — **METEORITE_NEW** has none (fields output, not grades); holding matches.

6. Do **not** edit `JOBS_SKIPPED_BULK_RETRY_TO_STATE` / operator Skipped Retry maps (boundary: AST-1156). Leave **METEORITE_ERROR_QUALIFY** → **METEORITE_NEW**.

7. Do **not** edit `src/data/database.py` / seed a **METEORITE_NEW_RETRY** companion `dispatch_task` row — companion claim is registry-driven via `METEORITE_NEW.retry_state` + existing `dispatch_claim_states` (same AST-882 / AST-898 decision). Do **not** change `qualify_job_listings` / **NEW_RETRY**. Do **not** change `qualify_meteorite` content-gate → `fail_state` / bot → `bot_blocked_state` routing.

8. `src/core/consult.py`: **no product delta required** if `_consult_batch_fail_dest` + existing `_run_batch_consult` Style D `debug_index` on `bad_grades` / missing-ID paths already emit `outcome=… -> {dest}` when `debug=True`. Confirm after config; if meteorite-specific fail→dest debug is missing on a path that actually writes holding/terminal for this ticket, add Style D `debug_index` + `|` detail gated on `debug=True` only (mirror AST-898 Stage 2 AC8) — do **not** fork a qualify-meteorite-only dest helper.

**Manual check (no commit of throwaway notes):** after the edit, `dispatch_claim_states("METEORITE_NEW", "job") == ["METEORITE_NEW", "METEORITE_NEW_RETRY"]`, `_consult_batch_fail_dest("METEORITE_NEW", "METEORITE_ERROR_QUALIFY") == "METEORITE_NEW_RETRY"`, `_consult_batch_fail_dest("METEORITE_NEW_RETRY", "METEORITE_ERROR_QUALIFY") == "METEORITE_ERROR_QUALIFY"`.

### Blast radius

- Shared `_consult_batch_fail_dest` / `dispatch_claim_states` — behavior change is registry-scoped to **METEORITE_NEW** only; other job retry pairs untouched.
- `qualify_meteorite` @ **METEORITE_NEW** Available/claim counts gain the companion holding (dispatcher already unions claim states).
- Tracker `prior_states` enforcement: without step 3, second-attempt pass/fail/error/bot transitions raise `ValueError`.
- Downstream evaluate hops (**METEORITE_QUALIFIED** / **METEORITE_QUALIFIED_RETRY**) unchanged.
- Tests that assert `METEORITE_NEW` has no `retry_state`, or that first-strike qualify errors terminal immediately, will need Betty revise (fix-board / qa-fix) — engineer does not edit `tests/` or bible in make-fix.
- AST-1053 plan text that deferred `METEORITE_NEW_RETRY` is historical; this bug is the superseding cutover for qualify only.

### What must still hold

- AST-898 / regular track: `NEW` → `NEW_RETRY` → `ERROR_QUALIFY_JOB_LISTINGS`, `VALID_TITLE_RETRY` drain-only, title screen stays **NEW**-only — unchanged.
- Content-gate / bot outcomes inside `qualify_meteorite.process` still write `fail_state` / `bot_blocked_state` (not the retry holding).
- `_consult_batch_fail_dest` remains the sole fail→dest helper (§2.1 / §2.6) — no parallel meteorite dest map.
- One-retry only: holding has no `retry_state`; second recoverable failure terminals at **METEORITE_ERROR_QUALIFY**.
- No reopen/re-parent of archived AST-898; Skipped operator Retry maps stay AST-1156's lane.
- With `debug=True`, fail→dest emissions remain Style D `debug_index` + `|` detail only (§1.5.1).
