<!-- linear-archive: AST-355 archived 2026-06-03 -->

## Linear archive (AST-355)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-355/score-floor-add-score-to-task-dispatch-records  
**Status at archive:** Done  
**Project:** Astral Dispatcher  
**Assignee:** susan  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Run for records with the state AND with latest_score >= {score_floor}

Update batching to include the score floor, and update the "Available" calculation on task dispatcher ui to filter for those that meet the score floor criteria.

Update the task dispatch edit modal to include the score floor as a dropdown list with scores from 1.00 to 10.00 in 0.5 increments (1.00, 1.50, 2.00…)

Add the score floor to the task dispatcher table between the state and the AUTO columns.

If a task is configured to have no score, do not render a score floor, just leave it blank, otherwise.

### Comments

_No comments._

---

# AST-355 — score_floor: Add >= score to task dispatch records

**Linear:** AST-355  
**Title:** score_floor: Add >= score to task dispatch records  
**Project:** Astral Dispatcher (`docs/features/dispatcher/`)

---

## Issue (Linear, verbatim)

**Identifier:** AST-355  

**Description**

- Run for records with the state **and** with `latest_score >= {score_floor}`.
- Update batching to include the score floor, and update the **Available** calculation on task dispatcher UI to filter for those that meet the score floor criteria.
- Update the task dispatch edit modal to include the score floor as a **dropdown** with scores from **1.00 to 10.00 in 0.5 increments** (1.00, 1.50, 2.00…).
- Add the score floor to the task dispatcher **table between the state and the AUTO columns**.
- If a task is configured to have **no score**, do not render a score floor — leave it **blank**.

**Team:** Team Astral  
**Project name:** Astral Dispatcher — *Running astral from the inside…*

---

## a-plan-linear procedure (this run — 2026-04-25)

| Step | Status |
|------|--------|
| **0.** 0-agent-orientation — cursor rules + `docs/ASTRAL_CODE_RULES.md` | Done (mandate: §2.1 dispatch_task table, §2.4 claim/process/release, §3.3 layering) |
| **1.** `git checkout dev` → `git fetch origin` → `git rebase origin/main` | **Done.** Working tree clean; `origin/main` is ancestor of `dev` (rebase no-op / already integrated). |
| **2.** Project folder `docs/features/dispatcher/` | Exists |
| **3.** ASTRAL_CODE_RULES | Applied in Plan + Self-review |
| **4.** Combined doc | This file (`ast-355-score-floor-task-dispatch-records.md`) |
| **5.** Self-review vs code rules | After Plan |
| **6.** Present for review | No implementation in this step |

---

## Plan

**Traceability:** Eligibility = `trigger_state` **and** (when floor active) `latest_score >= score_floor` — implemented in **count** + **claim** so **Available** (`list_dtasks` enrichment), **`get_due_tasks`** (uses same count), and **batching** stay aligned. UI: table column **State | (new) Floor | AUTO**; modal dropdown 1.00–10.00 step 0.5; hide floor when task has no score (`TASK_CONFIG.scored` rule below).

### 1. Schema and data layer (`dispatch_task`)

- **Modify** `src/data/database.py`
  - In `_ensure_dispatch_task_schema`, add migration entry `score_floor` → `REAL` (nullable) in `_migrate_cols` (or equivalent) so existing DBs get the column; new CREATE TABLE is not used on upgrade path—only `ALTER TABLE ADD COLUMN`.
  - Extend `_DISPATCH_TASK_UPDATE_COLS` with `"score_floor"`.
  - **`count_eligible_for_dispatch_task(task)`**  
    For `entity_type == "job"`, after existing state/candidate/batch_id predicates, when the row should honor a floor (see step 2), append  
    `AND latest_score IS NOT NULL AND latest_score >= ?`  
    with bound parameter `task["score_floor"]`.  
    When floor is inactive (NULL, or task does not support scored `latest_score`), keep current SQL behavior unchanged.  
    **Note:** `get_due_tasks()` already gates on this count — no separate change once count is correct.
  - **`claim_job_batch(...)`**  
    Add optional parameter `score_floor: Optional[float] = None` (default `None`). When set, add the same `latest_score` predicate to the inner `SELECT` subquery so claimed rows match the count logic. Preserve `batch_id`-first parameter order; append new arg after existing optional args with a clear docstring.
  - **`count_entities_in_state`** (optional): either extend with optional `score_floor` for the job branch only, or keep eligibility entirely inside `count_eligible_for_dispatch_task` without delegating to `count_entities_in_state` for the job+floor case to avoid signature churn—prefer **one place** for the job filter SQL to stay DRY between count and claim (shared private helper string builder or shared inner WHERE fragment).
  - Update `database.py` header inventory comment for `dispatch_task` if it lists columns.
- **Modify** `src/core/tracker.py` — `get_new_job_batch(...)`  
  Pass `score_floor` through to `database.claim_job_batch` when provided (dispatcher supplies it from the task row).
- **Modify** `src/core/dispatcher.py` — `_run_unified`  
  When `entity_type == "job"`, resolve whether the task is scored using `TASK_CONFIG.scored` (consult tasks via `CONSULT_CONFIG[task_key]["agent_task"]`), then pass `score_floor` into `get_new_job_batch(..., score_floor=...)` only when scored.

### 2. Score relevance rule (use TASK_CONFIG.scored directly)

- **No helper function.** Use existing config directly where needed:
  - Resolve effective task key (`task_key` or consult `agent_task`) and read `TASK_CONFIG[effective_key]["scored"]`.
  - If `scored` is false: `score_floor = NULL`, do not apply score filter in count/claim, and UI renders blank floor.
  - If `scored` is true: default persisted `score_floor = 1.0`, apply `latest_score >= score_floor` in count/claim, and UI renders editable dropdown.

### 3. Admin API

- **Modify** `src/ui/api/api_admin.py`
  - `PUT /dispatch_tasks/<id>`: allow `score_floor` in `allowed` set; accept JSON number or `null` to clear (store SQL NULL).
  - `POST /dispatch_tasks`: optional `score_floor` in body; if omitted, server sets default by scored flag (`1.0` for scored tasks, `NULL` otherwise).
  - **`save_dispatch_task`** in `database.py`: add optional `score_floor: Optional[float] = None` to INSERT (column default NULL when omitted).
  - `list_dtasks` / `dispatch_task_keys`: include enough metadata for UI to compute scored relevance from existing task config mapping, or compute `is_scored` server-side inline (without adding a reusable helper function).
  - If `?req_dict=1` uses `_DISPATCH_TASK_COLUMNS`, add a column entry for the floor (e.g. `score_floor` / label **Score ≥**) so export shape matches the table.

### 4. Config table upsert / prod scripts

- **Modify** `scripts/push_tables_to_prod.py`, `scripts/upsert_tables_from_prod.py`, and any CSV/export that assumes `dispatch_task` column order—**after** schema exists, ensure `score_floor` is included wherever column lists are enumerated.
- **Modify** `src/utils/config_table_upsert.py` — no code change if columns come from `PRAGMA table_info` dynamically; verify callers pass full column list including `score_floor`.

### 5. Task Dispatcher UI (`AdminScheduledActions.tsx`)

- **Modify** `src/ui/frontend/src/pages/AdminScheduledActions.tsx`
  - Extend `DispatchTask` interface with `score_floor: number | null` and an `is_scored` boolean (or derive from existing task metadata in-page).
  - **Table:** Insert a column **between “State” and “AUTO”** (per ticket) — header e.g. **Score ≥** or **Floor**.  
    - If `!is_scored`: render **blank** cell (ticket: no floor UI for non-scored tasks).
    - Else: show formatted value (e.g. two decimals) or blank when `score_floor == null`.
  - **Modal (add/edit):** When `is_scored`, show a **`<select>`** with:
    - Default selected value **`1.00`** on create.
    - Options: **1.00, 1.50, …, 10.00** (generate with a small loop `for (let v = 1; v <= 10; v += 0.5)` to avoid hand-maintained magic lists of business states; values are UX increments, not JOB_STATES).
  - When `!is_scored`, **do not render** the score floor row in the modal.
  - **Save payload:** include `score_floor` only when `is_scored`; otherwise send/keep `null`.
  - On edit for scored tasks, if row has `NULL` (legacy data), initialize control to `1.00` and save back as `1.0`.

### 6. Dispatcher ledger / logging (optional)

- No change required unless you want `score_floor` echoed in ledger metadata; out of scope unless Susan asks.

### 7. Tests / verification (implementation phase)

- Manual: create scored dispatch row (default floor 1.0), mix of jobs with NULL / 0.5 / 1.0 / 7 `latest_score` in `trigger_state`; confirm Avail count + claimed batch include only `>= floor` and non-NULL. Then change floor to 6.5 and re-check.
- Regression: company tasks (prefilter, gaze) unchanged counts; job tasks without floor unchanged.

---

### Files Changed (summary)

| File | Action |
|------|--------|
| `src/data/database.py` | Add `score_floor` column migration; update `count_eligible_for_dispatch_task`, `claim_job_batch`, `_DISPATCH_TASK_UPDATE_COLS`, `save_dispatch_task` INSERT, optional `count_entities_in_state` or shared WHERE helper |
| `src/utils/config.py` | No new helper; reuse existing `TASK_CONFIG.scored` (+ consult `agent_task` mapping) |
| `src/core/tracker.py` | `get_new_job_batch` forwards `score_floor` |
| `src/core/dispatcher.py` | Resolve `TASK_CONFIG.scored` inline and pass `score_floor` when applicable |
| `src/ui/api/api_admin.py` | PUT/POST allow `score_floor`; expose/compute `is_scored` inline; optional `_DISPATCH_TASK_COLUMNS` row |
| `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | Table column, modal select, types, save body |
| `scripts/push_tables_to_prod.py` / `scripts/upsert_tables_from_prod.py` | Verify column lists if hardcoded |
| `src/utils/config_table_upsert.py` | Verify only if needed |

---

## Self-review against ASTRAL_CODE_RULES

- **§3.3 Layering:** Data holds SQL; core (`tracker`, `dispatcher`) orchestrates; UI calls API only. No new helper module needed.
- **§2.1 Config as source of truth:** Eligibility rule keyed off existing **`TASK_CONFIG[...]["scored"]`** and **`CONSULT_CONFIG` `agent_task`** indirection in-place—not a new hardcoded list and not a new helper abstraction.
- **§2.4 Batch pattern:** Still `claim_job_batch` → process → `clear_job_batch`; only the claim `WHERE` gains an optional predicate; `batch_id` flow unchanged.
- **§2.6 State machine:** No new transitions; filtering is dispatch eligibility only.
- **§1.3 DRY:** One SQL predicate construction shared by count and claim; scored resolution reused inline in dispatcher/API paths.
- **§3.5 Naming:** `score_floor` snake_case in DB/API; React component stays PascalCase file convention.

**Confirmed rule:** Use `TASK_CONFIG.scored` only. If false → `score_floor = NULL` and blank UI. If true → default `score_floor = 1.0`, user-editable (1.00..10.00 step 0.5).

---

Plan updated with the confirmed scoring rule; **no implementation** in this pass.

---

## Review

**Commit:** `efd0bf3`
**Branch:** `dev`
**Reviewed:** 2026-04-25

---

## What's Solid

- `dispatch_task` schema now includes nullable `score_floor`, with migration + backfill logic and scored-task defaulting to `1.0` for existing rows.
- Job claim filtering and Available counting are aligned: both paths apply `latest_score IS NOT NULL AND latest_score >= score_floor` only when the task resolves to `TASK_CONFIG.scored = true`.
- Core orchestration is wired cleanly: `dispatcher._run_unified` resolves scored status from config and passes `score_floor` through `tracker.get_new_job_batch` into `database.claim_job_batch`.
- Admin API behavior matches the ticket: scored tasks default to `1.0`; non-scored tasks expose blank/no floor (`None`) and do not filter on score.
- UI requirements are met in `AdminScheduledActions`: floor column appears between State and AUTO; scored tasks get a 1.00..10.00 step-0.5 dropdown; non-scored tasks render blank and hide the floor control.
- Layering stays compliant with ASTRAL rules: SQL remains in data layer, orchestration in core, view logic in API/UI.

---

## Issues

### Issue 1 — Plan/file coverage gap for script updates ℹ️ advisory
The plan explicitly called out updates/verification for `scripts/push_tables_to_prod.py`, `scripts/upsert_tables_from_prod.py`, and related table-upsert flow, but this implementation commit does not include those files. If those scripts rely on hardcoded `dispatch_task` column lists in any environment, `score_floor` can be silently omitted during push/pull operations.

Recommendation: verify those scripts in a follow-up and either (a) include `score_floor` in hardcoded column paths or (b) document that they are already schema-driven and need no change.

---

### Issue 2 — Duplicate scored-resolution logic across layers ℹ️ advisory
Scored-task resolution (`CONSULT_CONFIG` -> `agent_task` -> `TASK_CONFIG.scored`) is now repeated in `database.py`, `dispatcher.py`, and `api_admin.py`. Behavior is currently consistent, but this increases drift risk when task config semantics evolve.

Recommendation: if/when this logic changes again, centralize resolution in one shared utility in `utils` and import it where needed. Not a blocker for AST-355, but worth tracking.

---

## Recommended Actions
| # | Severity | Action |
|---|----------|--------|
| 1 | Advisory | Validate script/table upsert flows for `dispatch_task.score_floor` and patch if any column lists are hardcoded. |
| 2 | Advisory | Track a future refactor to centralize scored-task resolution logic to reduce drift risk. |

---

## Resolution

- **Issue 1**: resolved — verified `scripts/push_tables_to_prod.py` and `scripts/upsert_tables_from_prod.py` are schema-driven (`table_columns` / schema compare), so `dispatch_task.score_floor` is already covered without script edits.
- **Issue 2**: deferred — no helper abstraction added per explicit direction; duplicated scored-resolution stays inline for now and can be centralized in a later refactor ticket.
