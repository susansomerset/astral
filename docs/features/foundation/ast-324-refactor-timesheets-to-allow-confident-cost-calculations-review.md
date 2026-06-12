# Review: AST-324 — Refactor Timesheets for Confident Cost Calculations

**Branch:** `foundation`
**Commit:** `dfc15f2`
**Reviewed:** 2026-03-16

---

## Compile / Lint

All Python files (`config.py`, `cost_calculator.py`, `database.py`, `anthropic.py`, `api_admin.py`) compile clean with `python3 -m py_compile`. TypeScript diff is syntactically correct.

---

## What's Solid

- **`config.py`** — rename, `cache_min_tokens` values match the Anthropic docs URL cited in the comment, `CHARS_PER_TOKEN` comment is appropriately honest about approximation.
- **`cost_calculator.py`** — `calculate_cost_components()` is tight. `getattr(..., 0) or 0` guard correctly handles `None` attribute values.
- **`database.py` migrations** — detect-and-rename pattern (`PRAGMA table_info` → rename → recreate → copy) is correct for SQLite's lack of DROP COLUMN / DROP PK. Both `timesheets` and `agent_task` migrations follow the same pattern consistently. `_timesheets_schema_ensured` guard protects the hot path.
- **`save_agent_task` versioning** — diff-detect logic is correct: only prompt content changes trigger a new version; `agent_id`-only changes update in place. No accidental double-versioning.
- **`sum_cost_by_batch`** — correctly updated to sum the four cost component columns instead of the old single `est_cost`.
- **`anthropic.py`** — `task_key_uuid` never surfaces outside `anthropic.py`. `batch_size` forwarded from `ctx` with correct default `1`.

---

## Issues

### Issue 1 — `agent_performance` hardcoded `"success"`, `failure_note` always `NULL` ⚠️

**File:** `src/external/anthropic.py`, line ~669

```python
agent_performance="success",
failure_note=None,
```

The timesheet write happens immediately after the API call returns, before any response parsing. Parse failures return early via a different code path and never write a second corrected row. Result: every timesheet row says `success` regardless of whether the parsed response was usable. The `failure_note` column is permanently `NULL` until something populates it.

**Question:** Was capturing parse-level failures in `agent_performance` / `failure_note` explicitly deferred to AST-325, or did it not land? If deferred, worth a note in the plan doc so it doesn't get lost.

---

### Issue 2 — `no_cache_prompt_tokens` includes `user_content` — column name is misleading ⚠️

**File:** `src/external/anthropic.py`, line 766

```python
nocache_chars = len(nocache_content or "") + len(user_content or "")
```

`no_cache_prompt_tokens` bundles the static `nocache_prompt` DB field *and* the `user_prompt` DB field together. `live_content` is correctly separated into `no_cache_live_tokens`. But the column name implies it's only the nocache context block. This makes the two token columns non-independently reconcilable against a Claude Console export.

**Question:** Intentional (treating user_prompt + nocache as a single "static prompt" group)? If so, the column name could be `no_cache_static_tokens` to be less ambiguous. If not intentional, `nocache_chars` should only use `len(nocache_content or "")`.

---

### Issue 3 — Dead variable: `api_key_hint` computed but never used 🔧

**File:** `src/external/anthropic.py`, lines 649–650

```python
raw_key = api_key_override or os.environ.get("ANTHROPIC_API_KEY", "")
api_key_hint = raw_key[-8:] if raw_key else None
```

`api_key_hint` is assigned but not passed to `_add_timesheet_entry` (the new schema dropped that column). Should be deleted — two lines.

---

### Issue 4 — Dead branch in `_ensure_timesheets_schema` 🔧

**File:** `src/data/database.py`, inside the `if cursor.fetchone()[0] == 0:` block

```python
old_exists = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='timesheets_v1'").fetchone()[0]
if not old_exists:
    # Check if the unmigrated old table is still named 'timesheets' via absence — already handled above
    pass
```

This `if not old_exists: pass` block does nothing and was clearly left over from drafting. Harmless but noisy — three lines to delete.

---

## Recommended Actions

| # | Severity | Action |
|---|----------|--------|
| 1 | Discuss | Confirm whether parse-failure capture in `agent_performance` is deferred to AST-325; if yes, add a note to the 325 plan |
| 2 | Discuss | Confirm intent of `no_cache_prompt_tokens` bundling `user_content`; rename or fix accordingly |
| 3 | Fix now | Delete the `api_key_hint` assignment (2 lines, `anthropic.py`) |
| 4 | Fix now | Delete the `if not old_exists: pass` dead branch (3 lines, `database.py`) |
