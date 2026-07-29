# AST-1041 — Meteorite company config + lazy ensure

**Linear:** [AST-1041](https://linear.app/astralcareermatch/issue/AST-1041/meteorite-company-config-lazy-ensure-support-meteorite-jobs)
**Parent:** [AST-1034](https://linear.app/astralcareermatch/issue/AST-1034/support-meteorite-jobs) — Support meteorite jobs
**Publish ref:** `origin/sub/AST-1034/AST-1041-meteorite-company-config-lazy-ensure`

Config-owned meteorite placeholder company template plus a core **lazy-ensure** helper that inserts `meteorite-<candidate_id>` once when a known candidate needs it (no server-start bulk seed). Placeholders land in **IGNORE** and are hard-excluded from roster/gazer company claim SQL. Leave-in-place lifecycle (no delete when candidate leaves ACTIVE_SEARCH). Does **not** own the job-create API (AST-1042) or email ingest.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `METEORITE_CONFIG` seed template (+ job-create defaults for AST-1042 reuse) | utils |
| `src/core/meteorite.py` | New module: `ensure_meteorite_company(candidate_id, *, debug=False)` | core |
| `src/data/database.py` | On company **claim** (`set_company_batch` clear=False), exclude `short_name` matching meteorite prefix | data |

## Stage 1: `METEORITE_CONFIG` seed template

**Done when:** `METEORITE_CONFIG` is importable from `config.py` with every literal this epic’s ensure/create paths need; no callers yet.

1. In `src/utils/config.py`, add a new block **immediately after** `JOB_STATES` (so both `COMPANY_STATES` and `JOB_STATES` exist for the asserts):

```python
# ---------------------------------------------------------------------------
# METEORITE_CONFIG: per-candidate placeholder employer (AST-1034 / AST-1041).
# Lazy-ensure inserts meteorite-<candidate_id> on demand — never bulk at server start.
# Job-create defaults (JD_READY + score) are consumed by AST-1042; defined here so
# literals stay config-owned (parent Architectural definition).
# ---------------------------------------------------------------------------
METEORITE_CONFIG = {
    "short_name_prefix": "meteorite-",
    "short_name_template": "meteorite-{candidate_id}",  # format with candidate_id=
    "company_name": "meteorite",
    "company_state": "IGNORE",
    "company_data": {
        "note": (
            "The company for this job has not been identified, and cannot be "
            "vetted without a website url."
        ),
    },
    # AST-1042 job-create defaults (unused in AST-1041)
    "job_create_state": "JD_READY",
    "job_create_latest_score": 10.0,
}

assert METEORITE_CONFIG["company_state"] in COMPANY_STATES
assert METEORITE_CONFIG["job_create_state"] in JOB_STATES
```

⚠️ **Decision:** Place the block after `JOB_STATES` (currently ~line 1372+), not after `COMPANY_STATES`, so both registry asserts can run at import time without reordering large config sections.

2. Do **not** add server-start / bootstrap upsert loops. Do **not** seed rows for all ACTIVE_SEARCH candidates.

**Done when (recheck):** `from src.utils.config import METEORITE_CONFIG` works; keys above present; `company_state` is `"IGNORE"`.

## Stage 2: Core lazy-ensure + claim hard-exclusion

**Done when:** `ensure_meteorite_company` inserts once / no-ops when present with Style D debug; `set_company_batch` claim SQL never selects `meteorite-*` short names; no delete/reaper for leave-in-place.

1. Create `src/core/meteorite.py` with module docstring:

```
Meteorite placeholder company ensure (AST-1041).

Lazy-insert meteorite-<candidate_id> from METEORITE_CONFIG. No job create (AST-1042).
No email ingest. Leave-in-place — callers must not delete these rows on candidate exit.
```

2. Implement public API (public-first; helpers below if needed):

```python
def ensure_meteorite_company(candidate_id: str, *, debug: bool = False) -> dict:
    """Ensure meteorite-<candidate_id> exists in IGNORE. Idempotent.

    Returns:
      {"short_name": str, "inserted": bool, "company": dict}
    """
```

Concrete steps inside `ensure_meteorite_company`:

- Strip `candidate_id`; if empty after strip, raise `ValueError("candidate_id is required")`.
- Build `short_name = METEORITE_CONFIG["short_name_template"].format(candidate_id=candidate_id)` (must equal `METEORITE_CONFIG["short_name_prefix"] + candidate_id` — do not invent a second shape).
- `log = get_logger(__name__); log.set_debug_flag(debug)`.
- `existing = get_company(short_name)` from `src.data.database`.
- If `existing` is not None:
  - If `debug`: `log.debug_index(func="meteorite.ensure_meteorite_company", index=1, total=1, identifier=short_name, outcome="already-present")` then `log.debug_detail(f"candidate_id={candidate_id}")`.
  - Return `{"short_name": short_name, "inserted": False, "company": existing}`.
- Else call `save_company(...)` with:
  - `short_name=short_name`
  - `state=METEORITE_CONFIG["company_state"]`  # IGNORE
  - `company_name=METEORITE_CONFIG["company_name"]`
  - `company_data=dict(METEORITE_CONFIG["company_data"])`  # shallow copy
  - `candidate_id=candidate_id`
  - leave `company_website` / `job_site` as default `None`
- Re-fetch with `get_company(short_name)` (must exist after save; if None raise `RuntimeError`).
- If `debug`: `log.debug_index(..., outcome="inserted")` + `log.debug_detail(f"candidate_id={candidate_id}")`.
- Return `{"short_name": short_name, "inserted": True, "company": row}`.

⚠️ **Decision:** New `src/core/meteorite.py` rather than stuffing into `roster.py` — AST-1042 and later ingest call ensure without pulling roster orchestration. Debug uses Style D only when `debug=True`; no `logger.info("[DEBUG]")` lines.

3. Do **not** add hooks that delete `meteorite-*` when a candidate leaves ACTIVE_SEARCH (leave-in-place = absence of reaper code).

4. In `src/data/database.py`:

- Import `METEORITE_CONFIG` alongside the existing `from src.utils.config import (...)` list.
- In `set_company_batch`, inside the **claim** branch (`clear=False`), after building `where_base` / `params` and **before** the `UPDATE ... WHERE short_name IN (SELECT ...)` / order/limit execute, append:

```python
meteorite_prefix = METEORITE_CONFIG["short_name_prefix"]
where_base += " AND short_name NOT LIKE ?"
params.append(meteorite_prefix + "%")
```

- Do **this only for claim** (`clear=False`), never for `clear=True`.
- Update the `set_company_batch` / `claim_company_batch` docstrings with one sentence: claim excludes short names matching `METEORITE_CONFIG["short_name_prefix"]`.

⚠️ **Decision:** Hard exclusion in data claim SQL (not only “IGNORE has no batch_criteria”) so a mistaken `state=IGNORE` claim or future trigger cannot pull meteorite placeholders into roster/gazer batches. Prefix comes from config — no inline `"meteorite-"` string in `database.py`.

5. Do **not** implement AST-1042 HTTP create, job inserts, or UI. Do **not** edit `tests/` / bible.

**Done when (recheck):** Calling ensure twice for the same candidate inserts once then no-ops; claim SQL cannot select `meteorite-*`; `debug=False` emits no new Style D lines from ensure; server start still does not seed meteorite rows.

## Out of scope (do not implement here)

- API create job under meteorite from raw HTML (AST-1042).
- Email ingest / calling ensure from Gmail path (later ingest epic / AST-1031 sibling).
- Admin UI for meteorite job create.
- Bulk seed at server start.
- Deleting or transitioning `meteorite-*` when candidate leaves ACTIVE_SEARCH.
- Editing `tests/` or `docs/test-bible/**` (Betty after Code Complete).

## Self-Assessment

**Scope:** `Single-Component` — one config block, one new core module, one claim-SQL exclusion in `database.py`; no UI/external.

**Conf:** `high` — reuses `save_company` / `get_company` / Style D logging / existing IGNORE registry; claim exclusion mirrors other `where_base` filters in `set_company_batch`.

**Risk:** `Medium` — wrong claim filter could hide real companies (mitigated by config prefix + `NOT LIKE prefix%` only) or miss meteorite rows (prefix must match template); wrong ensure upsert could wipe company fields via `INSERT OR REPLACE` (mitigated by only inserting when missing).

## Rules self-review

- **§2.1 / no-hardcoded-sets:** All meteorite literals in `METEORITE_CONFIG`; claim uses `METEORITE_CONFIG["short_name_prefix"]`.
- **§1.5.1 debug-contract-gated:** Style D only when `debug=True` on ensure.
- **§2.6 / COMPANY_STATES:** Ensure writes registered `IGNORE` only.
- **§3.3 imports:** `meteorite.py` → data + utils; `database.py` → utils only (adds METEORITE_CONFIG import).
- **§1.3 public-then-helpers:** Single public `ensure_meteorite_company`.
- **database-header-inventory:** Uses existing `company` table only; no new tables.
- **In-scope only:** No job create / email / UI.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1034/AST-1041-meteorite-company-config-lazy-ensure`
**Plan path:** `docs/features/meteorite/ast-1041-meteorite-company-config-lazy-ensure.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `b5d968b3` | METEORITE_CONFIG after JOB_STATES (IGNORE template + AST-1042 job-create defaults) |
| 2 | `047be5ff` | ensure_meteorite_company + set_company_batch claim NOT LIKE prefix |

**Tip:** `c49e1711a829850cc8b58c2b0b539ab622f682b9` on `origin/sub/AST-1034/AST-1041-meteorite-company-config-lazy-ensure`

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1041
**Publish ref tip (pre-docs):** `ae062c74123c6c862f676459dc82cfa339c5c5d4`
**Overall:** DISCUSS

### What’s solid
- `METEORITE_CONFIG` owns literals; `ensure_meteorite_company` insert-once / no-op; Style D only when `debug=True`.
- Claim `NOT LIKE` prefix from config in `set_company_batch` clear=False only; no bulk seed / no reaper / no AST-1042 API.

### Issues
- **discuss (straggler ×3):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` at plan time; three-dot now includes `docs/features/**` + Betty tests/bible — all **conforms** on substance.

### Recommended actions
- Ada: acknowledge stragglers → resolve-child → User Testing.

