# Plan: AST-324 — Refactor Timesheets for Confident Cost Calculations

**Branch:** `foundation`
**Commit slug:** `<agent>/ast-324-refactor-timesheets-to-allow-confident-cost-calculations`

---

## Goals

1. Rename `MODELS` config block to `AGENT_CONFIG` to match rules doc (and add `cache_min_tokens` while we're there).
2. Add `CHARS_PER_TOKEN` named constant to config (SS 1.4 compliance).
3. Fix cost calculator Bug 1 (already done on current branch — carry forward).
4. Add `calculate_cost_components()` for granular per-component cost breakdown.
5. Overhaul the timesheets schema to store every input/output quantity and cost component needed for Claude Console reconciliation.
6. Add task versioning to `agent_task` (diff-detect; `task_key_uuid` + `current` flag) so timesheet rows link to the exact prompt version that generated them.
7. Update `_send_and_parse` / `_fetch_response_from_content` in `anthropic.py` to populate all new timesheet fields.
8. Update downstream UI (Timesheets page + API columns) to match new schema.
9. Update `database.py` header inventory and `ASTRAL_CODE_RULES.md` to reflect all changes.

---

## Step 1 — Rename MODELS to AGENT_CONFIG

**Files:**

- **`src/utils/config.py`**: Rename `MODELS = {` → `AGENT_CONFIG = {`. Update `get_model()`. Update module header comment (line 15) and section comment above the block. Add `cache_min_tokens` to each model entry:
  - `claude-haiku-4-5`: `"cache_min_tokens": 4096`
  - `claude-sonnet-4-6`: `"cache_min_tokens": 2048`
  - `claude-opus-4-6`: `"cache_min_tokens": 4096`
  - Also add: `CHARS_PER_TOKEN = 4  # rough character-to-token ratio for prompt size estimation`

- **`src/utils/cost_calculator.py`**: Change import and all `MODELS` references to `AGENT_CONFIG`.

- **`src/data/database.py`**: Change `MODELS` import to `AGENT_CONFIG`. Update agent seed reference.

- **`src/ui/api/api_admin.py`**: Change `MODELS` import to `AGENT_CONFIG`. Update agents list endpoint and model_code validation checks.

- **`docs/ASTRAL_CODE_RULES.md`**: In SS 2.1 AGENT_CONFIG (currently named MODELS), update the field list to include `cache_min_tokens`. Rename `MODELS` to `AGENT_CONFIG` throughout.

---

## Step 2 — Add calculate_cost_components()

**`src/utils/cost_calculator.py`** — Add alongside the existing `calculate_cost_with_cache`:

```python
def calculate_cost_components(usage, model_code: str) -> dict:
    """Return individual cost components for granular timesheet storage.
    usage.input_tokens is the non-cached fresh input (Anthropic SDK convention)."""
    m = AGENT_CONFIG.get(model_code)
    if not m:
        raise ValueError(f"Unknown model_code: {model_code!r}")
    cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
    cache_write = getattr(usage, "cache_creation_input_tokens", 0) or 0
    return {
        "calc_cost_cache_write":    (cache_write / 1_000_000) * m["cpm_cache_write"],
        "calc_cost_cache_read":     (cache_read  / 1_000_000) * m["cpm_cache_read"],
        "calc_cost_no_cache_input": (usage.input_tokens / 1_000_000) * m["cpm_input"],
        "calc_cost_output":         (usage.output_tokens / 1_000_000) * m["cpm_output"],
    }
```

---

## Step 3 — Task Versioning (agent_task schema)

**`src/data/database.py`** — `_ensure_agent_task_schema` and `save_agent_task`:

### Schema migration

The current table uses `task_key TEXT PRIMARY KEY`. SQLite cannot drop a PK directly, so recreate the table:

1. Rename `agent_task` → `agent_task_v1`
2. Create new `agent_task`:
   ```sql
   CREATE TABLE agent_task (
       task_key_uuid TEXT PRIMARY KEY,   -- e.g. "qualify_job_listings_<uuid4>"
       task_key TEXT NOT NULL,           -- logical name, non-unique
       current INTEGER NOT NULL DEFAULT 1,
       agent_id TEXT,
       user_prompt TEXT,
       cache_prompt TEXT,
       nocache_prompt TEXT,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   )
   ```
3. Migrate rows from `agent_task_v1`: generate `task_key_uuid = task_key + "_" + uuid4()`, `current = 1` for all.
4. Create indexes:
   ```sql
   CREATE UNIQUE INDEX idx_agent_task_uuid ON agent_task(task_key_uuid);
   CREATE INDEX idx_agent_task_key ON agent_task(task_key, current);
   ```

### save_agent_task (diff-detect versioning)

On save, compare incoming `agent_id`, `user_prompt`, `cache_prompt`, `nocache_prompt` to the current version. If any field changed:
- Set `current = 0` on the old row
- Insert new row with fresh UUID, `current = 1`, same `task_key`

If nothing changed, only update `updated_at` on the existing row.

### get_agent_task / list_agent_tasks

Add `AND current = 1` to all select queries.

### _resolve_task_prompts (anthropic.py)

Versioning is entirely internal to `anthropic.py`. Callers (`consult.py`, `roster.py`, `do_task`) continue to pass `task_key` as always — they never see or handle `task_key_uuid`.

`_resolve_task_prompts` already calls `get_agent_task(task_key)`, which post-migration returns the current version row. It captures `task_key_uuid` from that row and passes it internally down to `_fetch_response_from_content` → `_send_and_parse` → `_add_timesheet_entry`. The full chain:

```
consult/roster → do_task(task_key=...) 
              → _resolve_task_prompts → get_agent_task(task_key) → row with task_key_uuid
              → _fetch_response_from_content(task_key_uuid=...)
              → _send_and_parse(task_key_uuid=...)
              → _add_timesheet_entry(task_key_uuid=...)
```

No `task_key_uuid` ever surfaces outside `anthropic.py`.

---

## Step 4 — Timesheet Schema Overhaul

**`src/data/database.py`** — `_ensure_timesheets_schema` and `add_timesheet_entry`:

### Migration

1. Rename `timesheets` → `timesheets_v1`
2. Create new `timesheets`:
   ```sql
   CREATE TABLE timesheets (
       anthropic_req_id      TEXT UNIQUE,
       task_key_uuid         TEXT,
       model_code            TEXT,
       candidate_id          TEXT,
       batch_id              TEXT,
       batch_size            INTEGER DEFAULT 1,
       cache_write_tokens    INTEGER DEFAULT 0,
       cache_read_tokens     INTEGER DEFAULT 0,
       no_cache_prompt_tokens  INTEGER DEFAULT 0,
       no_cache_live_tokens    INTEGER DEFAULT 0,
       total_no_cache_input_tokens INTEGER DEFAULT 0,
       total_output_tokens   INTEGER DEFAULT 0,
       calc_cost_cache_write   REAL DEFAULT 0,
       calc_cost_cache_read    REAL DEFAULT 0,
       calc_cost_no_cache_input REAL DEFAULT 0,
       calc_cost_output        REAL DEFAULT 0,
       agent_performance     TEXT,
       failure_note          TEXT,
       created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   )
   ```
3. Migrate rows from `timesheets_v1`, mapping:
   - `request_id` → `anthropic_req_id`
   - `user_prompt_file` → `task_key_uuid` (legacy: task_key string, no UUID yet)
   - `tokens_input` → `total_no_cache_input_tokens`
   - `tokens_output` → `total_output_tokens`
   - `cache_creation_tokens` → `cache_write_tokens`
   - `cache_read_tokens` → `cache_read_tokens`
   - `est_cost` → `calc_cost_no_cache_input` (approximation for legacy rows)
   - `batch_id` → `batch_id`
   - `candidate_id` → `candidate_id`
   - All other new fields default to 0/NULL

### add_timesheet_entry signature

`add_timesheet_entry` is only ever called from `src/external/anthropic.py`. As part of this refactor, rename it to `_add_timesheet_entry` (private helper) in `database.py` and update the import in `anthropic.py` accordingly. Also remove it from the `database.py` header inventory's public API list — it's an internal write path, not a function other layers should call.

```python
def _add_timesheet_entry(
    anthropic_req_id: Optional[str],
    task_key_uuid: Optional[str],
    model_code: Optional[str],
    candidate_id: Optional[str],
    batch_id: Optional[str],
    batch_size: int,
    cache_write_tokens: int,
    cache_read_tokens: int,
    no_cache_prompt_tokens: int,
    no_cache_live_tokens: int,
    total_no_cache_input_tokens: int,
    total_output_tokens: int,
    calc_cost_cache_write: float,
    calc_cost_cache_read: float,
    calc_cost_no_cache_input: float,
    calc_cost_output: float,
    agent_performance: Optional[str] = None,
    failure_note: Optional[str] = None,
) -> bool:
```

---

## Step 5 — Update anthropic.py Timesheet Writer

**`src/external/anthropic.py`** — `_fetch_response_from_content` and `_send_and_parse`:

### _fetch_response_from_content

Already tracks all prompt block sizes in `_track()`. Compute token estimates using `CHARS_PER_TOKEN`:
- `no_cache_prompt_tokens` = `len(nocache_text) // CHARS_PER_TOKEN` (nocache context block)
- `no_cache_live_tokens` = `len(live_content) // CHARS_PER_TOKEN` (live content)

Pass these to `_send_and_parse` as new params.

### _send_and_parse

New params: `task_key_uuid`, `no_cache_prompt_tokens`, `no_cache_live_tokens`, `batch_size`.

After response arrives:
- Call `calculate_cost_components(usage, model_code)` for the 4 cost values
- Derive `agent_performance` and `failure_note` from `parsed_response` (check for parse errors)
- Call `add_timesheet_entry(...)` with all fields populated

### do_task

No changes. `do_task` passes `task_key` as before and is unaware of versioning. `batch_size` is passed via `ctx` if provided (e.g. by the dispatcher for batch tasks), defaulting to 1 — this is already in `ctx` and just needs to be forwarded into `_fetch_response_from_content`.

---

## Step 6 — Minimal UI Fixes (break-prevention only; full redesign deferred to AST-325)

The goal here is only to prevent outright breakage when 324 deploys. No new columns, no redesign.

**`src/external/anthropic.py`**: Remove `session_id=context` from the `_add_timesheet_entry` call — `context` was the session/context string, replaced by `batch_id` (already passed via `log_batch_id.get()`).

**`src/data/database.py`**:
- Remove `session_id` column from the new `timesheets` schema (not carried forward from `timesheets_v1`)
- Remove `session_id` param from `list_timesheets()` filter function
- Migration note: `session_id` from `timesheets_v1` is dropped (not mapped to any new column)

**`src/ui/api/api_admin.py`**:
- Remove `session_id` from `_TIMESHEET_CSV_COLUMNS`, `_TIMESHEET_COLUMNS`, and `_timesheet_filters()`
- Replace `id` with `anthropic_req_id` in `_TIMESHEET_CSV_COLUMNS` and `_TIMESHEET_COLUMNS`
- Keep remaining old columns in place — they'll return null/0 for new rows until AST-325 redesigns the page

**`src/ui/frontend/src/pages/AdminAgentTimesheets.tsx`** — minimal changes only:
- Remove `session_id` from `TimesheetRow` interface, `FILTER_KEYS`, the `COLUMNS` array, and the Session filter `<input>`
- Replace `id: string` with `anthropic_req_id: string | null` in `TimesheetRow`
- Pass `idField="anthropic_req_id"` to `ListPage` so row selection doesn't break
- Leave `Totals`, `TotalsBar`, and all other columns untouched — they'll show zeros for new rows until AST-325

---

## Step 7 — Documentation Updates

**`src/data/database.py`** header inventory (SS 1.1):
- Update `agent_task` entry: add `task_key_uuid`, `current` columns
- Update `timesheets` entry: replace all old columns with new schema

**`docs/ASTRAL_CODE_RULES.md`** SS 2.1:
- Rename MODELS → AGENT_CONFIG in all references
- Add `cache_min_tokens` to AGENT_CONFIG field list

---

## Files Changed Summary

| File | Change |
|------|--------|
| `src/utils/config.py` | Rename MODELS→AGENT_CONFIG, add cache_min_tokens, add CHARS_PER_TOKEN |
| `src/utils/cost_calculator.py` | Rename MODELS refs, add calculate_cost_components() |
| `src/data/database.py` | agent_task versioning schema, timesheets schema overhaul, rename add_timesheet_entry→_add_timesheet_entry, header update |
| `src/external/anthropic.py` | Pass task_key_uuid + token estimates to timesheet writer, remove session_id=context |
| `src/ui/api/api_admin.py` | Rename MODELS→AGENT_CONFIG, update timesheet columns/filters |
| `src/core/consult.py` | Update list_timesheets wrapper for new filter params |
| `src/ui/frontend/src/pages/AdminAgentTimesheets.tsx` | Update interface + columns for new schema |
| `docs/ASTRAL_CODE_RULES.md` | MODELS→AGENT_CONFIG rename, cache_min_tokens field |
