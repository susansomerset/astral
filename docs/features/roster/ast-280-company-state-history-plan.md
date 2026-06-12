<!-- linear-archive: AST-280 archived 2026-06-03 -->

## Linear archive (AST-280)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-280/company-state-history  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** susan  
**Priority / estimate:** High / 2  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Add state_history tracking to the company table, mirroring the existing pattern on the job table. batch_id is the spine that connects company state transitions to execution sessions, timesheets, and Better Stack logs.

**Acceptance Criteria:**

**company Table Addition:**

* Add `state_history` TEXT column (JSON array, same shape as job.state_history)
* Each entry: `{ "to_state": "...", "timestamp": "...", "batch_id": "..." }`
* Migration: existing rows get `state_history = '[]'`

[**roster.py**](<http://roster.py>)** Changes:**

* Add state_history append pattern to every company state transition, mirroring [tracker.py](<http://tracker.py>):
  * Fetch current company, read state_history array
  * Append new entry with to_state, timestamp, current batch_id
  * Write back via save_company

[**database.py**](<http://database.py>)** Changes:**

* `save_company()` accepts and stores `state_history` (same overwrite pattern as save_job)
* Schema migration adds column to existing databases idempotently

**ROSTER_DATA_MODEL.md:**

* Update to document state_history column and entry shape

**Database:**

* company table: ALTER to add `state_history` TEXT column
* [database.py](<http://database.py>) module docstring updated per ASTRAL_CODE_RULES 1.1

### Comments

_No comments._

---

# ast-280-company-state-history Plan

Add `state_history` tracking to the company table and align job/company state transition patterns: rename `transition_state` → `transition_job_state`, create matching `save_company_data` + `transition_company_state` pair in roster.py, and refactor all call sites to separate data saves from state transitions.

---

## Problem: Structural Misalignment

**Tracker (jobs) — clean separation:**
- `save_job_data()` — data only, no state change
- `transition_state()` — state + state_history only, no data change (should be `transition_job_state`)
- Callers always use `transition_state()` for state changes

**Roster (companies) — currently conflated:**
- `save_company()` (INSERT OR REPLACE) — does everything: state, company_data, agent_responses, job_site
- `_save_company_data()` — builds data AND sets state in the same call
- `_merge_save_company_data()` — ad hoc per-key merge into company_data
- No dedicated state transition function, no dedicated data-save function

---

## Sub 1: Rename `transition_state` → `transition_job_state` — `src/core/tracker.py`, `src/core/consult.py`

Rename for clarity and symmetry with the new `transition_company_state`.

**tracker.py changes:**
- Rename `def transition_state(...)` → `def transition_job_state(...)`
- Update module docstring: `transition_state` → `transition_job_state`
- Update `initialize_job` docstring reference

**consult.py changes (5 call sites):**
- `tracker.transition_state(...)` → `tracker.transition_job_state(...)` at lines 76, 99, 154, 210, 289

**docs/ASTRAL_CODE_RULES.md:**
- Update section 2.6.2 reference

**Files:** `src/core/tracker.py`, `src/core/consult.py`, `docs/ASTRAL_CODE_RULES.md`

---

## Sub 2: Schema & Data Layer — `src/data/database.py`

**Schema:**
- Add `state_history TEXT` to `CREATE TABLE company` in `_ensure_company_schema`
- Add idempotent migration: `ALTER TABLE company ADD COLUMN state_history TEXT`

**`save_company()` changes:**
- Add `state_history: Optional[List[Dict[str, Any]]] = None` parameter
- When provided: serialize and write (for initial company creation with seed entry)
- When not provided: preserve from existing row (same pattern as `last_scan_at`)
- Extend existing SELECT to also read `state_history`; add to INSERT OR REPLACE column list

**`update_company()` changes:**
- Add `state_history` to `_UPDATE_COMPANY_ALLOWED` frozenset
- Add JSON serialization for `state_history` (same handling as `company_data`/`agent_responses`)

**`_parse_company_row()` changes:**
- Parse `state_history` JSON → list (default `[]` when missing/empty)

**Module docstring:** Add `state_history` to company table inventory line.

**Files:** `src/data/database.py`

---

## Sub 3: Add `save_company_data` + `transition_company_state` — `src/core/roster.py`

### 3a: `save_company_data()` — mirrors `tracker.save_job_data()`

```python
def save_company_data(short_name: str, company_data: Dict[str, Any], replace: bool = False) -> None:
    """Update company_data for a company. replace=False: merge keys; replace=True: full overwrite.
    Mirrors tracker.save_job_data. No state change.
    Raises ValueError if company not found (when merging)."""
    if replace:
        update_company(short_name, company_data=company_data)
    else:
        existing = get_company(short_name)
        if not existing:
            raise ValueError(f"Company not found: {short_name}")
        merged = dict(existing.get("company_data") or {})
        merged.update(company_data)
        update_company(short_name, company_data=merged)
```

Replaces `_merge_save_company_data()` (delete it).

### 3b: `transition_company_state()` — mirrors `tracker.transition_job_state()`

```python
def transition_company_state(short_name: str, to_state: str) -> None:
    """Record company state transition (mirrors tracker.transition_job_state).
    Appends to state_history; updates state. Validates to_state against COMPANY_STATES.
    Raises ValueError if invalid or company not found."""
    validate_value(list(COMPANY_STATES.keys()), to_state)
    company = get_company(short_name)
    if not company:
        raise ValueError(f"Company not found: {short_name}")
    history = list(company.get("state_history") or [])
    now = datetime.now(timezone.utc).isoformat()
    history.append({"to_state": to_state, "timestamp": now, "batch_id": company.get("batch_id")})
    update_company(short_name, state=to_state, state_history=history)
```

Add import: `validate_value` from `src.utils.config`.

**Files:** `src/core/roster.py`

---

## Sub 4: Refactor Call Sites — `src/core/roster.py`, `src/core/gazer.py`

### 4a: `_save_company_data()` — separate data from state

**Before:**
```python
save_company(short_name=short_name, state=state, company_website=company_website,
    job_site=page_option_url, company_name=company_name, company_data=company_data)
```

**After:**
```python
update_company(short_name, company_website=company_website,
    job_site=page_option_url, company_name=company_name)
if company_data:
    save_company_data(short_name, company_data)
transition_company_state(short_name, state)
```

Remove inline state validation (now in `transition_company_state`).

### 4b: `_save_parse_job_list_success()`, `_save_parse_problem()`, `_save_parse_job_list_failure()`

All three currently: fetch company → build company_data → `save_company()` echoing ALL fields.

**After** (example: `_save_parse_job_list_success`):
```python
c = get_company(short_name)
company_data = dict(c.get("company_data") or {})
company_data["parse_instructions"] = parse_instructions
save_company_data(short_name, company_data, replace=True)
transition_company_state(short_name, "WATCH")
```

Same pattern for `_save_parse_problem` (→ `"NO_JOB_SITE"`) and `_save_parse_job_list_failure` (→ `"CANNOT_PARSE_JOB_SITE"`).

### 4c: `prefilter_company()`

**Before:**
```python
update_company(short_name, state=new_state, company_data=company_data)
```

**After:**
```python
save_company_data(short_name, {"prefilter_company_notes": notes})
transition_company_state(short_name, new_state)
```

### 4d: `_merge_save_company_data()` callers → `save_company_data()`

Three callers:
- `_fetch_nav_links`: `_merge_save_company_data(short_name, "nav_links", ...)` → `save_company_data(short_name, {"nav_links": ...})`
- `prefilter_company` notes: absorbed into 4c above
- `_fetch_website_content`: `_merge_save_company_data(short_name, "website_content", ...)` → `save_company_data(short_name, {"website_content": ...})`

Delete `_merge_save_company_data()` after migration.

### 4e: `gazer.py` — data-only save, no state transition

**Before:**
```python
save_company(short_name=short_name, state=company.get("state", "WATCH"),
    company_website=..., job_site=..., company_name=..., company_data=company_data,
    agent_responses=..., batch_id=..., batch_created_at=..., last_scan_at=...)
```

**After:**
```python
save_company_data(short_name, {"parse_instructions": parse_instructions})
```

No state change → no `transition_company_state` → no state_history entry. Import `save_company_data` from `src.core.roster`.

**Files:** `src/core/roster.py`, `src/core/gazer.py`

---

## Sub 5: Documentation

**`docs/ROSTER_DATA_MODEL.md`:**
- Add **state_history** to Company table columns
- Add **state_history (JSON array)** section mirroring TRACKER_DATA_MODEL.md
- Note: `transition_company_state()` in roster.py is the single entry point

**`docs/TRACKER_DATA_MODEL.md`:**
- Update `transition_state` → `transition_job_state` reference

**Files:** `docs/ROSTER_DATA_MODEL.md`, `docs/TRACKER_DATA_MODEL.md`

---

## Alignment Summary

| Concern | tracker.py (jobs) | roster.py (companies) |
|---------|------------------|----------------------|
| Data save function | `save_job_data()` | `save_company_data()` |
| State transition function | `transition_job_state()` | `transition_company_state()` |
| State validation | `validate_value(JOB_STATES, ...)` | `validate_value(COMPANY_STATES, ...)` |
| History entry shape | `{to_state, timestamp, batch_id}` | `{to_state, timestamp, batch_id}` |
| History storage | `state_history` TEXT (JSON array) | `state_history` TEXT (JSON array) |
| Data saves touch state? | No | No |
| State saves touch data? | No | No |

## Estimate

5 subs, ~100 lines of code changes. Estimate: 3.
