<!-- linear-archive: AST-340 archived 2026-06-03 -->

## Linear archive (AST-340)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-340/retry-bad-responses  
**Status at archive:** Done  
**Project:** Astral Agent  
**Assignee:** susan  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

If a response is invalid when normally fine, retry the api call (pay extra, it's worth it in situ) once.

Context: We validate the response for parsability and completeness.  If the parse fails but the agent thinks it was successful, run the same prompt again, because the agent may have just biffed it.  

If the response is complete or the agent says it failed in the envelope, don't rerun it.

Actually, in the case of batched responses, we need to have a {state}\_retry state and a task set up in dispatch to run those separately, otherwise we would rerun the entire full batch and waste tokens.

So, we run 100 jobs

agent_performance = success
87 are valid -> {pass_state}/{fail_state}
3 have errors -> {error_state}
10 are invalid (incomplete/unparsable) -> {retry_state}

Or, we run 100 jobs
agent_performance = failure
100 -> {error_state}

### Comments

#### susan — 2026-04-23T21:07:17.208Z
## [AST-340](https://linear.app/astralcareermatch/issue/AST-340/retry-bad-responses) **Design Notes — Parked for Backlog**

### **What this is about**

Occasional API responses come back structurally valid JSON but with envelope-level problems — not payload content failures, but something wrong at the `agent_performance` / `agent_payload` wrapper level. When that happens, the current behavior is: log it, return `success: False`, let the entity fall to an error state, and pick it up on the next dispatch cycle. That's a lot of overhead for what might be a one-off glitch that a single retry would fix.

The ticket proposes: retry the API call once, in-place, before giving up.

---

### **Open design questions**

**1. What exactly triggers the retry?** The instinct is *envelope failures* — cases where the response parsed as valid JSON but the `agent_performance` / `agent_payload` structure is wrong, absent, or self-reported as failure — not schema validation failures deep inside the payload, and not network or parse errors. Those feel like different problems.

One interesting angle: the agent could signal retryability itself with a `recommend_retry` flag inside the envelope. That would let the model communicate "I know this response is suspect, please try again" rather than the caller guessing from the outside.

**2. Config flag vs. envelope flag** Two approaches on the table:

* `retry_on_invalid: True` in `TASK_CONFIG` — caller-side, opt-in per task. Simple, predictable, easy to reason about.
* `recommend_retry` in the response envelope — model-side signal. More nuanced, but requires prompt engineering and trust in the model's self-assessment.

These aren't mutually exclusive — config flag could gate whether we even look at the envelope signal.

**3. Which tasks should opt in?** Single-entity consult tasks (`grade_get`, `consult_do`, `consult_like`) are the obvious candidates — high-value, occasional envelope weirdness, worth one extra call. Batch tasks (`qualify_job_listings`, `evaluate_jd`) probably should not — their error state is already the retry mechanism.

**4. Audit trail on retry** If the first call fails and the retry succeeds, do we store the bad first response in `agent_data`? Storing both adds noise; storing only the success loses evidence a retry happened. No decision yet.

**5.** `skip_cache` on retry Cache-read tokens will still be charged on retry (the cached blocks haven't changed). Cache-write would be suppressed. Low stakes either way.

---

### **Why it's parked**

Nothing is on fire. The error-state dispatch cycle already handles these cases — slower, but functional. The design needs a clearer picture of the actual failure instances before committing to an approach (envelope flag vs. config flag, which tasks, what audit trail). Worth revisiting when a concrete failure case surfaces.

---

---
name: AST-340 Retry Bad Responses
overview: Adds per-job retry routing to batch consult tasks, plus JOB_STATES housekeeping that consolidates config and establishes prior_states validation.
todos:
  - id: config-job-states
    content: "config.py: restructure JOB_STATES (prior_states, retry_state, rename JD_SCRAPE states, drop LEGACY, remove batch_criteria, add VALID_TITLE_RETRY + JD_READY_RETRY, update SKIPPED/IN_REVIEW_STATES)"
    status: pending
  - id: config-consult
    content: "config.py: CONSULT_CONFIG — add fallback_batch_size to scrape_jd; remove input_state"
    status: pending
  - id: config-dispatch-tasks
    content: "config.py: remove DISPATCH_TASKS entirely — DB is sole source of truth"
    status: pending
  - id: config-tracker
    content: "config.py: delete job_state_transitions from TRACKER_CONFIG"
    status: pending
  - id: db-migration
    content: "database.py: add sort_by and batch_call_mode columns to dispatch_task table; seed values for existing rows; remove DISPATCH_TASKS config references"
    status: pending
  - id: tracker-prior-states
    content: "tracker.py: enforce prior_states validation in transition_job_state"
    status: pending
  - id: consult-run-task
    content: "consult.py: add run_consult_task(entity_type, input_state, entities, batch_id, ctx, debug); add per-job validation + retry routing in _run_batch_consult"
    status: pending
  - id: roster-run-task
    content: "roster.py: add run_company_task(input_state, entities, batch_id, ctx, debug)"
    status: pending
  - id: dispatcher-cleanup
    content: "dispatcher.py: replace _RUNNERS + _run_* functions with unified runner using run_consult_task; remove DISPATCH_TASKS config references; use DB sort_by + batch_call_mode"
    status: pending
  - id: gazer-rename
    content: "gazer.py: rename SCRAPE_ERROR_STATES and inline references to match new JD_SCRAPE_FAIL_* names"
    status: pending
  - id: docs-update
    content: "ASTRAL_CODE_RULES.md: update §2.1 config block descriptions; update §2.6.2 for prior_states"
    status: pending
isProject: false
---

# AST-340: Retry Bad Responses

**File:** `docs/features/agent/ast-340-retry-bad-responses.md`

---

## Plan

## Part 1 — JOB_STATES Housekeeping (`config.py`)

### Step 1: JOB_STATES restructure

Each entry gets two new optional keys: `prior_states` (list or None) and `retry_state` (string or absent).

- `prior_states: None` = unrestricted entry (NEW, CANDIDATE_SKIPPED, ERROR_* states)
- `prior_states: [...]` = enforced predecessor list
- `retry_state` only on `VALID_TITLE` and `JD_READY` — the two batch AI states that support per-job retry

```python
"VALID_TITLE": {"prior_states": ["NEW"],           "retry_state": "VALID_TITLE_RETRY"},
"JD_READY":    {"prior_states": ["PASSED_JOBLIST"], "retry_state": "JD_READY_RETRY"},
```

Add two new retry states (visible — `IN_REVIEW_STATES`). No `retry_state` — absence is the off-switch:
```python
"VALID_TITLE_RETRY": {"prior_states": ["VALID_TITLE"]},
"JD_READY_RETRY":    {"prior_states": ["JD_READY"]},
```

Also:
- Rename `FAILED_JD_SCRAPE/COOKIE/BOT/MISSING/CLOSED` → `JD_SCRAPE_FAIL/FAIL_COOKIE/FAIL_BOT/FAIL_MISSING/FAIL_CLOSED`
- Drop `LEGACY`
- Remove `batch_criteria` entirely from all JOB_STATES entries
- Update `SKIPPED_STATES` for renamed states

### Step 2: CONSULT_CONFIG

- Add `fallback_batch_size: 10` to `scrape_jd` (currently missing — falls back to JOB_STATES today)
- Remove `input_state` from all entries — dispatcher passes it as a parameter; no duplication needed

CONSULT_CONFIG retains: `agent_task`, `pass_state`, `fail_state`, `error_state`, `fallback_batch_size`, `pass_threshold`, `save_prefix`, `rubric_artifact`, `save_fields`, `requires_company`, `min_job_title_length`.

### Step 3: Remove DISPATCH_TASKS

Delete `DISPATCH_TASKS` from `config.py` entirely. The DB `dispatch_task` table is the sole source of truth. All references in `dispatcher.py` and `database.py` switch to reading from the DB row.

### Step 4: TRACKER_CONFIG

Delete `job_state_transitions` list. Superseded by `prior_states` in JOB_STATES.

---

## Part 2 — DB migration (`database.py`)

Add two columns to `dispatch_task`:

| Column | Type | Purpose |
|---|---|---|
| `sort_by` | TEXT | Order to claim entities (e.g. `updated_at`, `latest_score`) |
| `batch_call_mode` | INTEGER (0/1) | 1 = all entities in one API call; 0 = one entity per call (warm-then-gather applies) |

Seed values for existing rows on migration. Remove all `DISPATCH_TASKS` config lookups in `database.py` — read `entity_type`, `trigger_state`, `sort_by`, `batch_call_mode` from the DB row directly.

Add retry task rows for `VALID_TITLE_RETRY` and `JD_READY_RETRY` in the seed/migration.

---

## Part 3 — Enforce `prior_states` in `tracker.py`

[`src/core/tracker.py`](src/core/tracker.py) — `transition_job_state`:

```python
prior = JOB_STATES[to_state].get("prior_states")
if prior is not None and job["state"] not in prior:
    raise ValueError(f"Invalid transition: {job['state']} -> {to_state}")
```

`prior_states: None` = unrestricted, no check.

---

## Part 4 — `consult.py`: `run_consult_task` + validation + retry routing

[`src/core/consult.py`](src/core/consult.py) gets a new public entry point:

```python
async def run_consult_task(entity_type: str, input_state: str, entities: list, batch_id: str, ctx, debug) -> Dict:
```

Dispatcher passes pre-claimed entities. Consult routes on `entity_type` and `input_state`:
- `"company"` → `roster.run_company_task(input_state, entities, batch_id, ctx, debug)`
- `"job"` batch tasks (qualify_job_listings, evaluate_jd) → `_run_batch_consult(...)` (private)
- `"job"` single tasks (consult_do/get/like) → `render_verdict(...)` (unchanged)

### 4a. New per-job validation in `_run_batch_consult`

After `do_task` returns success, `_run_batch_consult` runs an independent validation pass before `process_fn`. Agent.py is the delivery driver; consult checks the contents.

Read the retry state from the input state's config:
```python
retry_state = JOB_STATES.get(input_state, {}).get("retry_state")
```

For each job in the response:

1. **Missing jobs** (in sent_ids but not received_ids — truncated or bad output):
   - If `retry_state` → transition to `retry_state`
   - Else → `error_state`

2. **Per-job data validation** — fails if:
   - Grade set is incomplete or contains unexpected vectors
   - `qualify_job_listings`: `job_title` absent or too short; `job_link` not http when no F grades
   - `evaluate_jd`: grades array empty or incomplete
   - If `retry_state` → `retry_state`; else → `error_state`

3. **Fabricated IDs** (received but not sent): silently dropped, unchanged.

`do_task` returning `success: False` (envelope failure) is unchanged — whole batch → `error_state`.

### 4b. Routing summary

| Condition | retry_state set | retry_state absent |
|---|---|---|
| Envelope failure (do_task success=False) | error_state | error_state |
| Missing job | retry_state | error_state |
| Invalid job data | retry_state | error_state |
| Fabricated ID | dropped | dropped |

---

## Part 5 — `roster.py`: `run_company_task`

[`src/core/roster.py`](src/core/roster.py) gets a new public entry point:

```python
async def run_company_task(input_state: str, entity: dict, batch_id: str, ctx, debug) -> Dict:
```

Processes a single company (dispatcher handles concurrency via `_warm_then_gather`). Routes on `input_state`:

| input_state | function |
|---|---|
| `WEBSITE_FOUND` | `prefilter_company(short_name, website, ctx)` |
| `TO_WATCH` | `find_job_page(url, short_name, ...)` |
| `WATCH` | `process_gazer_batch(bid, [entity])` |

Returns the same `_SUMMARY_ZERO`-shaped dict as today.

---

## Part 6 — `dispatcher.py` simplification

[`src/core/dispatcher.py`](src/core/dispatcher.py):

Replace `_RUNNERS` and all `_run_*` functions with a single unified runner:

```python
# For each due task from DB:
batch_id = f"{task_key}-{uuid4()}"
save_dispatch_ledger(batch_id, ...)
entities = claim_batch(entity_type, input_state, limit, sort_by, batch_id)

if batch_call_mode:
    # All entities in one API call (qualify, evaluate_jd)
    await consult.run_consult_task(entity_type, input_state, entities, batch_id, ctx, debug)
else:
    # One entity at a time with cache warming (prefilter, locate_job_page, consult_do/get/like)
    await _warm_then_gather(
        lambda e: consult.run_consult_task(entity_type, input_state, [e], batch_id, ctx, debug),
        entities, _SUMMARY_ZERO
    )
```

`_warm_then_gather` stays in dispatcher. Remove all `DISPATCH_TASKS` config imports and references.

---

## Part 7 — `gazer.py` rename

[`src/core/gazer.py`](src/core/gazer.py) — update `SCRAPE_ERROR_STATES` dict values and any inline references to match renamed states.

---

## Part 8 — Docs

Update [`docs/ASTRAL_CODE_RULES.md`](docs/ASTRAL_CODE_RULES.md):
- §2.1: update CONSULT_CONFIG description (remove `input_state`); remove DISPATCH_TASKS block entry; note `dispatch_task` DB table as source of truth for task registry
- §2.6.2: replace `job_state_transitions` reference with `prior_states`

---

## Part 9 — `api_admin.py`: remove DISPATCH_TASKS references

Three places in [`src/ui/api/api_admin.py`](src/ui/api/api_admin.py) use `DISPATCH_TASKS`:

1. **`GET /api/admin/dispatch_tasks`** — enriches rows with `entity_type` + `trigger_state` from config for `available_count`. With those as DB columns, reads directly from the row. Remove the config merge.

2. **`GET /api/admin/dispatch_tasks/task_keys`** — currently returns the full `DISPATCH_TASKS` config dict as the "add new task" dropdown options. Replace with a query returning distinct `task_key` values from the DB table (all valid task types will be seeded by the migration).

3. **`_build_adhoc_live_content`** — does `DISPATCH_TASKS.get(task_key)` to look up `entity_type`. Switch to reading from the DB dispatch task row for the current candidate.

Remove `DISPATCH_TASKS` from the import in `api_admin.py`.

---

## Files Changed

- `src/utils/config.py` — JOB_STATES, CONSULT_CONFIG, TRACKER_CONFIG, remove DISPATCH_TASKS
- `src/data/database.py` — add sort_by + batch_call_mode columns; seed retry task rows; remove DISPATCH_TASKS references
- `src/core/tracker.py` — prior_states enforcement
- `src/core/consult.py` — run_consult_task entry point; per-job validation + retry routing in _run_batch_consult
- `src/core/roster.py` — run_company_task entry point (single-entity)
- `src/core/dispatcher.py` — replace _RUNNERS/_run_* with unified runner; remove DISPATCH_TASKS imports
- `src/core/gazer.py` — rename SCRAPE_ERROR_STATES
- `src/ui/api/api_admin.py` — remove DISPATCH_TASKS references; update task_keys endpoint to query DB
- `docs/ASTRAL_CODE_RULES.md` — §2.1 + §2.6.2

---

## Review

**Commit:** `fd74c014352acd6ad6903270204a23008e931a97`  
**Branch:** `dev`  
**Reviewed:** 2026-04-25

---

## What's Solid

- **Dispatcher consolidation:** `_run_unified` reads `entity_type`, `trigger_state`, `sort_by`, `batch_call_mode`, and `batch_size` from the DB task row and branches job vs company claim/clear correctly. This matches the plan to retire per-task `_run_*` functions and `DISPATCH_TASKS` config.
- **`prior_states` in `tracker.transition_job_state`:** Matches the spec (validate `to_state`, then enforce `JOB_STATES[to_state]["prior_states"]` when not `None`). Aligns with ASTRAL_CODE_RULES §2.6.2.
- **Retry routing in `_run_batch_consult`:** Missing response IDs and `process_fn` failures (caught exceptions → `bad_grades`) route to `retry_state` when the batch’s jobs are in a state that defines `retry_state` in `JOB_STATES`, else `error_state`. Envelope `do_task` failure still moves the whole batch to `error_state`. Fabricated IDs are skipped and logged as before.
- **`run_consult_task` + `_INPUT_STATE_TO_TASK`:** Clear routing for job states through batch helpers or `render_verdict`; company path delegates to `roster.run_company_task` with one entity, consistent with warm-then-gather.
- **`api_admin`:** `list_dtasks` uses row `entity_type` / `trigger_state` for counts; `dispatch_task_keys` builds options from DB rows; `_build_adhoc_live_content` uses `get_dispatch_task_by_key` — all per Part 9.
- **DB migration shape in `database.py`:** Seeds for `sort_by`, `batch_call_mode`, retry dispatch rows (`VALID_TITLE_RETRY`, `JD_READY_RETRY`), and backfill logic are present and readable.
- **`ASTRAL_CODE_RULES.md`:** Config bullets and job state machine narrative were updated consistently with implementation.
- **`gazer` / scrape error state renames:** Renames align with the new `JD_SCRAPE_FAIL_*` naming in config.

---

## Issues

### Issue 1 — `qualify_job_listings` “short title” path bypasses retry routing ⚠️ Discuss

The plan (Part 4a) groups **missing jobs**, **invalid per-job data** (including title too short and bad link when not an F fail), and routes those to `retry_state` when configured, else `error_state`. In `qualify_job_listings`’s `process` closure, a title shorter than `min_job_title_length` calls `tracker.transition_job_state([aid], cfg["error_state"])` directly instead of raising (which would land the job in `bad_grades` and then `retry_state or error_state`). A relative `job_link` still raises `ValueError`, so that path **does** get retry routing.

**Recommendation:** If product intent matches the written plan, refactor the short-title branch to use the same retry vs hard-error decision as other validation failures (e.g. raise a dedicated error and let `_run_batch_consult` transition, or compute `dest = retry_state or error_state` using `JOB_STATES` like missing/bad_grades). If intentional (title too short is always terminal), update the plan doc so review and code stay aligned.

---

### Issue 2 — Company dispatch ignores DB `sort_by` ℹ️ Advisory

`_run_unified` parses `sort_by` from the task row for jobs and passes it into `get_new_job_batch`. For companies it calls `get_new_company_batch(...)` without a `sort_by` argument; `roster.get_new_company_batch` still derives `sort_by` only from `COMPANY_STATES[state]["batch_criteria"]`. So the new `sort_by` column on `dispatch_task` rows is authoritative for jobs but not for company tasks unless extended (e.g. optional `sort_by` on `get_new_company_batch`).

**Recommendation:** Either thread DB `sort_by` into company claim (small API change) or document that company ordering remains config-driven by design.

---

### Issue 3 — Misleading log label when no transition for missing IDs (fixed)

In `_run_batch_consult`, when there are missing IDs and both `retry_state` and `error_state` are falsy, the else branch used a non-f-string and logged the literal `(left in {input_state})`. **Resolved:** `consult.py` now uses `f"(left in {input_state})"`.

---

### Issue 4 — `migrate_agent_data` entity type map is “all job” for CONSULT_CONFIG ℹ️ Advisory

`_AGENT_TASK_ENTITY` now maps every `CONSULT_CONFIG` entry’s `agent_task` to `"job"`. That matches today’s CONSULT-only tasks. If a future consult-style task targets companies through `CONSULT_CONFIG`, this migration helper would need to be revisited.

---

## Recommended Actions

| # | Severity | Action |
|---|----------|--------|
| 1 | Discuss | Decide whether short-title failures on qualify should use `retry_state` like other invalid per-job data; align code or plan. |
| 2 | Advisory | Thread DB `sort_by` into company batch claims, or explicitly document that company `sort_by` on `dispatch_task` is informational only. |
| 3 | Done | `dest_label` else branch uses an f-string in `consult.py`. |
| 4 | Advisory | When adding non-job consult entries, revisit `_AGENT_TASK_ENTITY` in `migrate_agent_data.py`. |
