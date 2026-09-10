<!-- linear-archive: AST-285 archived 2026-06-03 -->

## Linear archive (AST-285)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-285/view-agent-timesheets  
**Status at archive:** Done  
**Project:** Astral Administrator  
**Assignee:** susan  
**Priority / estimate:** Medium / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Admin screen to view, filter, sort and export Anthropic API usage and cost data. The timesheets table already exists and is being written to by add_timesheet_entry. This feature adds the UI and a context_id field to the timesheet record.

**Acceptance Criteria:**

**Timesheet Table Addition:**

* Add `context_id` TEXT column to timesheets table (e.g. `grade_get_acme`, `qualify_job_listings_batch_uuid`)
* `add_timesheet_entry()` in [database.py](<http://database.py>) accepts and stores `context_id`
* All callers of `do_task` pass context_id through — follows existing context pattern in \_build_context()

**View Agent Timesheets Screen (UI — Admin > Agent Timesheets):**

* Sortable, filterable list of all timesheet records
* Columns: created_at, context_id, batch_id, user_prompt_file, request_id, tokens_input, cache_read_tokens, tokens_output, est_cost
* Filter controls: date range, user_prompt_file, batch_id, context_id
* **Header totals row** — sums tokens_input, cache_read_tokens, tokens_output, est_cost across all records matching current filter
* **Selected totals row** — same sums for checked/selected rows only, pinned to bottom of list
* Checkbox selection per row
* **Export to CSV** — exports all columns including metadata for current filter or selection
* Filter params are URL-querystring driven to support deep-linking from Execution History

**API Endpoints:**

* GET /api/admin/timesheets — list with filter params (date_from, date_to, user_prompt_file, batch_id, context_id)
* GET /api/admin/timesheets/export — CSV export with same filter params

**Notes:**

* No delete or edit — timesheets are append-only
* Execution History links to this screen filtered by batch_id

**Database:**

* timesheets table: ALTER to add context_id TEXT column
* [database.py](<http://database.py>) module docstring updated per ASTRAL_CODE_RULES 1.1

### Comments

_No comments._

---

# ast-285: View Agent Timesheets

## Subissues (from CSV)

The feature has three subissues, each building on the last:

1. **database.py: query function** (High priority, estimate 1)
2. **API endpoints and nav enable** (High priority, estimate 1)
3. **View Agent Timesheets screen** (Medium priority, estimate 2)

---

## Sub 1: database.py — list_timesheets

**Files:** [src/data/database.py](src/data/database.py)

The timesheets table is created in the legacy [src/astral_database.py](src/astral_database.py) — it has no `_ensure_timesheets_schema()` in the modern `database.py`. Current columns:

```
id, tokens_input, cache_read_tokens, tokens_output, est_cost,
session_id, user_prompt_file, request_id, created_at
```

The `session_id` column already stores the context identifier (company short_name, task_key, etc.) passed from `anthropic.py`. The original CSV spec called for a new `context_id` column, but this is the same value — no new column needed.

Changes:

- Add `_ensure_timesheets_schema()` to `database.py` following the existing pattern (global flag, idempotent). No ALTER needed — schema is already correct.
- Call `_ensure_timesheets_schema()` from `add_timesheet_entry()` and `list_timesheets()` (same guard pattern as other tables)
- Add `list_timesheets(date_from=None, date_to=None, user_prompt_file=None, session_id=None)` — all filters optional, dynamic WHERE clause, returns list of dicts ordered by `created_at DESC`
- Update `database.py` module docstring to document `list_timesheets`

No changes to `anthropic.py` — the existing `add_timesheet_entry()` call already passes `session_id=context` correctly.

---

## Sub 2: Core wrapper, API endpoints + nav enable

**Files:** [src/core/consult.py](src/core/consult.py), new [src/ui/api/admin_timesheets.py](src/ui/api/admin_timesheets.py), [src/ui/server.py](src/ui/server.py), [src/utils/config.py](src/utils/config.py)

- Add `list_timesheets(...)` to `src/core/consult.py` — thin wrapper that calls `database.list_timesheets(...)`. Consult is the domain that generates timesheets, so the read side lives here too. The Flask API layer imports core (same as CLI), core imports data — compliant with section 3.3.
- New Blueprint `admin_timesheets_bp` with `url_prefix="/api/admin/timesheets"`, following the same thin pattern as [admin_agents.py](src/ui/api/admin_agents.py)
- `GET /api/admin/timesheets` — accepts query params (`date_from`, `date_to`, `user_prompt_file`, `session_id`), calls `consult.list_timesheets(...)`, returns JSON array
- `GET /api/admin/timesheets/export` — same filter params, returns CSV file response (`text/csv`, `Content-Disposition: attachment`)
- Register blueprint in `server.py`
- In NAV_CONFIG: remove `"enabled": False` from the Agent Timesheets item (line ~637 of config.py)

---

## Sub 3: View Agent Timesheets screen

**File:** [src/ui/frontend/src/pages/Admin/AgentTimesheets.tsx](src/ui/frontend/src/pages/Admin/AgentTimesheets.tsx)

De-stub the current one-liner into a full page. Pattern follows [AgentPrompts.tsx](src/ui/frontend/src/pages/Admin/AgentPrompts.tsx) (ListPage + api calls).

- ListPage with columns: `created_at`, `session_id`, `user_prompt_file`, `request_id`, `tokens_input`, `cache_read_tokens`, `tokens_output`, `est_cost`
- Filter controls above the list: date range inputs, `user_prompt_file` dropdown (populated from distinct values in the data), `session_id` text input
- Header totals row: sums of `tokens_input`, `cache_read_tokens`, `tokens_output`, `est_cost` across all filtered rows
- Checkbox selection per row (ListPage already supports `bulkActions` + selection via `idField`)
- Selected totals row: same sums for checked rows only, pinned below list
- Export CSV button: calls `/api/admin/timesheets/export` with current filter params, triggers download
- Filter params driven by URL query string (`useSearchParams`) to support deep-linking from future Execution History page
- Styles added to [App.css](src/ui/frontend/src/App.css) in appropriate section
