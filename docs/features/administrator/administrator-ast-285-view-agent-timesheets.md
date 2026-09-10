# AST-285 — View Agent Timesheets
**Component:** administrator  
**Children:** — (single ticket)  
**Linear archived:** AST-285 2026-06-03  

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-03-02 15:44 | AST-285 | — | `7427b6fef` | ast-285: View Agent Timesheets — full feature |
| 2026-03-02 15:50 | AST-285 | — | `52c97816c` | ast-285: Address code review feedback |
| 2026-03-02 15:54 | AST-285 | merge | `3e626be6c` | Merge pull request #33 from susansomerset/chuckles/ast-285-view-agent-timesheets |

_The review doc's own SHA (`47f1938`) predates the repo-history migration and does not resolve on `origin/dev`. Era path convention was `ui/…` (not `src/ui/…`)._

## Epic — AST-285
_Archived: 2026-06-03 · Linear URL: https://linear.app/astralcareermatch/issue/AST-285/view-agent-timesheets · Status at archive: Done · Project: Astral Administrator · Assignee: susan · Priority / estimate: Medium / 5_

### Original brief

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

#### Comments

_No comments._

### Plan — ast-285: View Agent Timesheets

#### Subissues (from CSV)

The feature has three subissues, each building on the last:

1. **database.py: query function** (High priority, estimate 1)
2. **API endpoints and nav enable** (High priority, estimate 1)
3. **View Agent Timesheets screen** (Medium priority, estimate 2)

#### Sub 1: database.py — list_timesheets

**Files:** [src/data/database.py](src/data/database.py)

The timesheets table is created in the legacy [src/astral_database.py](src/astral_database.py) — it has no `_ensure_timesheets_schema()` in the modern `database.py`. Current columns:

```
id, tokens_input, cache_read_tokens, tokens_output, est_cost,
session_id, user_prompt_file, request_id, created_at
```

The `session_id` column already stores the context identifier (company short_name, task_key, etc.) passed from `anthropic.py`. The original CSV spec called for a new `context_id` column, but this is the same value — no new column needed. *(Reverses the brief's "add `context_id` column" AC — `session_id` already holds it.)*

Changes:

- Add `_ensure_timesheets_schema()` to `database.py` following the existing pattern (global flag, idempotent). No ALTER needed — schema is already correct.
- Call `_ensure_timesheets_schema()` from `add_timesheet_entry()` and `list_timesheets()` (same guard pattern as other tables)
- Add `list_timesheets(date_from=None, date_to=None, user_prompt_file=None, session_id=None)` — all filters optional, dynamic WHERE clause, returns list of dicts ordered by `created_at DESC`
- Update `database.py` module docstring to document `list_timesheets`

No changes to `anthropic.py` — the existing `add_timesheet_entry()` call already passes `session_id=context` correctly.

#### Sub 2: Core wrapper, API endpoints + nav enable

**Files:** [src/core/consult.py](src/core/consult.py), new [src/ui/api/admin_timesheets.py](src/ui/api/admin_timesheets.py), [src/ui/server.py](src/ui/server.py), [src/utils/config.py](src/utils/config.py)

- Add `list_timesheets(...)` to `src/core/consult.py` — thin wrapper that calls `database.list_timesheets(...)`. Consult is the domain that generates timesheets, so the read side lives here too. The Flask API layer imports core (same as CLI), core imports data — compliant with section 3.3.
- New Blueprint `admin_timesheets_bp` with `url_prefix="/api/admin/timesheets"`, following the same thin pattern as [admin_agents.py](src/ui/api/admin_agents.py)
- `GET /api/admin/timesheets` — accepts query params (`date_from`, `date_to`, `user_prompt_file`, `session_id`), calls `consult.list_timesheets(...)`, returns JSON array
- `GET /api/admin/timesheets/export` — same filter params, returns CSV file response (`text/csv`, `Content-Disposition: attachment`)
- Register blueprint in `server.py`
- In NAV_CONFIG: remove `"enabled": False` from the Agent Timesheets item (line ~637 of config.py)

#### Sub 3: View Agent Timesheets screen

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

### Code review (`47f1938`)

De-stubs the Agent Timesheets admin page into a fully functional read-only viewer. Adds a `list_timesheets` query function, API endpoints for JSON and CSV export, and a React page with filterable list, sortable columns, totals bars, checkbox selection, and CSV download.

#### The Good

1. **Clean layering.** `database.list_timesheets` → `consult.list_timesheets` → `admin_timesheets_bp` → frontend. Follows the `ui -> core -> data` pattern called for in the plan.
2. **`_filter_params` helper is well-designed.** Extracts only known filter keys from query params, skipping empty values, and passes them via `**kwargs`. Same dict flows to both the list and export endpoints with no duplication.
3. **URL-driven filters via `useSearchParams`.** Filter state lives in the URL query string, so deep-linking and browser back/forward work correctly. This was explicitly called out in the plan and is delivered.
4. **`TotalsBar` component is reusable.** Clean separation — one component for both the "All" totals and the "Selected" totals, differentiated by a `variant` prop for styling.
5. **CSS is well-organized.** Added to the appropriate section of `App.css` with its own numbered heading. Follows the existing dark-theme conventions with `var()` tokens. The selected totals bar uses `position: sticky; bottom: 0` for pinned visibility.
6. **CSV export uses `DictWriter` with `extrasaction="ignore"`.** Extra fields in the row dicts are silently skipped rather than throwing. Safe and pragmatic.
7. **`_ensure_timesheets_schema` added to both `add_timesheet_entry` and `list_timesheets`.** The table was previously only created by legacy code in `astral_database.py`. Now both read and write paths ensure the schema exists, so either can run first.

#### Issues to Address

##### 1. BUG: CSV export will fail with 401 (auth header not sent)

The export endpoint requires auth (`@require_auth` on `admin_timesheets_bp.route("/export")`), but the frontend triggers it via `window.open()`:

```typescript
// AgentTimesheets.tsx
window.open(`/api/admin/timesheets/export${qs ? `?${qs}` : ""}`, "_blank")
```

`require_auth` checks for a `Bearer` token in the `Authorization` header. `window.open()` is a plain browser navigation — it sends no custom headers. The export request will always get a 401.

**Fix options:**
- Fetch the CSV via `api()` (which adds the auth header), then create a Blob URL and trigger download client-side
- Or add a token query parameter alternative to `require_auth` for download endpoints
- Or make the export endpoint exempt from auth (it's internal tooling behind a VPN)

##### 2. BUG: `date_to` filter excludes entries on the to-date

```python
if date_to:
    clauses.append("created_at <= ?")
    params.append(date_to)
```

`created_at` stores ISO timestamps like `2026-03-02T15:30:00.000000`. If `date_to` is `"2026-03-02"`, the comparison `"2026-03-02T15:30:00" <= "2026-03-02"` is **false** (because `"T" > "2"` in ASCII/lexicographic ordering). So entries on the selected end date are excluded.

**Fix:** Append `T23:59:59` to the `date_to` value, or use `created_at < date(date_to, '+1 day')` in the SQL. *(This same bug + fix pattern was later backported cross-ticket by ast-281's `list_dispatch_ledger` / `list_log_entries`.)*

##### 3. `list_timesheets` doesn't use `_run_with_retry`

Every other query function in `database.py` wraps its logic in `_run_with_retry` (23 uses across the file). Both `list_timesheets` and `add_timesheet_entry` skip it — they manage `conn` directly with try/finally. This means transient SQLite locking errors (common under concurrent access) won't be retried for timesheet operations.

**Fix:** Wrap `list_timesheets` in the `_run_with_retry` pattern like `list_agents`, `list_candidates`, etc. `add_timesheet_entry` is a fast write path where the original pattern is defensible, but `list_timesheets` is a standard read and should follow the standard pattern.

##### 4. No result limit on `list_timesheets`

`SELECT * FROM timesheets{where} ORDER BY created_at DESC` returns every matching row into memory. Over time, the timesheets table will grow unbounded (every API call creates an entry). Without filters, an unfiltered load could return thousands of rows, all sent to the browser and rendered into the DOM.

**Fix:** Add a `LIMIT` with a sensible default (e.g., 500 or 1000), or add pagination. At minimum, the frontend should default the date range filter (e.g., last 7 days) so the initial load is bounded.

##### 5. `session_id` filter uses exact match — partial search won't work

The UI presents a free-text input for session_id, but `if session_id: clauses.append("session_id = ?")` requires an exact match. If the user types a partial value (e.g., `grade_` to find all grading sessions), nothing will match.

**Fix:** Use `LIKE` with wildcards: `clauses.append("session_id LIKE ?"); params.append(f"%{session_id}%")`. Or rename the UI label to clarify it requires an exact value.

#### Minor Notes

- **`taskOptions` derived from loaded rows.** The task dropdown is populated from distinct `user_prompt_file` values in the current result set, so it only shows options that exist in the currently filtered data. Arguably correct; the plan called for "populated from distinct values in the data" which this satisfies.
- **Page doesn't use `ListPage` component.** It builds its own table, sort logic, and selection — reasonable given the unique requirements (filters bar, dual totals bars, checkbox selection with per-row totals), but sort/style behavior won't automatically stay in sync with other list pages if `ListPage` evolves.
- **`consult.list_timesheets` is a pure passthrough.** Correct per the architecture (API layer must not import data layer directly); a comment noting "thin wrapper for layering compliance" would clarify intent.

#### Summary

The feature delivers everything in the plan across all three subissues. The main action items are **#1** (CSV export 401 — broken on click) and **#2** (date_to filtering bug — entries on the end date silently excluded). Both are straightforward fixes. Items #3–#5 are code health / UX improvements worth addressing before merge.

#### Changes Applied (`52c97816c`)

1. **CSV export 401 — fixed.** Replaced `window.open()` with `api()` fetch (sends auth header), then creates a Blob URL and triggers download via a temporary anchor element.
2. **date_to filter — fixed.** Appends `T23:59:59` to the `date_to` value so entries on the end date are included in results.
3. **`_run_with_retry` — fixed.** Wrapped `list_timesheets` in the `_run_with_retry` / `_with_conn` closure pattern, matching `list_agents`, `list_candidates`, etc.
4. **Unbounded initial load — fixed.** Frontend defaults `date_from` to 7 days ago and `date_to` to today when no date filters are present in the URL. Users can still clear/widen the range.
5. **session_id exact match — fixed.** Changed `session_id = ?` to `session_id LIKE ?` with `%` wildcards for partial matching.
6. **Minor: consult wrapper comment — done.** Docstring updated to "Thin wrapper for layering compliance — API layer imports core, not data."

### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/data/database.py` | Sub 1 — `_ensure_timesheets_schema` + `list_timesheets`; docstring; (review) `_run_with_retry`, `date_to` fix, `LIKE` | `7427b6fef` `52c97816c` |
| ✓ | `src/core/consult.py` | Sub 2 — `list_timesheets` thin wrapper | `7427b6fef` `52c97816c` |
| ✓ | `src/ui/api/admin_timesheets.py` (new) | Sub 2 — `admin_timesheets_bp` + `/` + `/export` | `7427b6fef` (`ui/api/…`) |
| ✓ | `src/ui/server.py` | Sub 2 — register blueprint | `7427b6fef` (`ui/server.py`) |
| ✓ | `src/utils/config.py` | Sub 2 — NAV_CONFIG: enable Agent Timesheets | `7427b6fef` |
| ✓ | `src/ui/frontend/src/pages/Admin/AgentTimesheets.tsx` | Sub 3 — de-stub screen; (review) blob download, default date range | `7427b6fef` `52c97816c` |
| ✓ | `src/ui/frontend/src/App.css` | Sub 3 — timesheet styles | `7427b6fef` |
| | _plan/review docs_ | — | `ast-285-view-agent-timesheets-{plan,review}.md` (`7427b6fef` `52c97816c`) |

_Implementation detail may live in git history on `origin/dev`._
