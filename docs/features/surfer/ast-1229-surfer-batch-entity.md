# AST-1229 — Surfer batch entity and candidate pointer

**Linear:** [AST-1229](https://linear.app/astralcareermatch/issue/AST-1229/surfer-batch-entity-and-candidate-pointer-surfer-batch-durable)
**Parent:** [AST-1169](https://linear.app/astralcareermatch/issue/AST-1169/surfer-batch-durable-worklist-state-and-batch-scoped-intake) — Surfer batch — durable worklist state and batch-scoped intake
**Publish ref:** `origin/sub/AST-1169/AST-1229-surfer-batch-entity`

Durable Surfer batch record on a **new** `surfer_batch` table (not `dispatch_ledger`): status, readable start time, target URL worklist with per-URL outcomes, batch-owned job association, registered status transitions in core, and a `candidate_data.lifecycle` pointer to any non-terminal batch. Introduces the externally resumable, client-driven batch shape. Does **not** wire search-page creation, batch-scoped page posts, remaining-work HTTP, cancel/discard UX, or dispatcher claim/release.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `SURFER_BATCH_CONFIG` (statuses, URL outcomes, id prefix, candidate_data pointer key); document in module header | utils |
| `src/data/database.py` | Header inventory line for `surfer_batch`; `_ensure_surfer_batch_schema`; insert/get/update/list helpers | data |
| `src/core/surfer.py` | **New** module: create/get, status transitions, URL outcome writes + auto-complete, candidate pointer set/clear, job association | core |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Document `lifecycle.active_surfer_batch_id` meta key | docs |

No UI routes, no `dispatcher.py` / `claim_*_batch` / `clear_*_batch` changes, no `tests/` or bible (Betty after Code Complete). Do **not** add a permanent `surfer_batch_id` column on `job`. Do **not** reuse or extend `dispatch_ledger`.

## Stage 1: `SURFER_BATCH_CONFIG`

**Done when:** `SURFER_BATCH_CONFIG` is importable from `src.utils.config` with the keys below; module docstring lists the block; `python3 -m py_compile src/utils/config.py` succeeds; no other config blocks changed.

1. In `src/utils/config.py` module docstring `Config sections:`, add:
   `SURFER_BATCH_CONFIG — Surfer client-driven batch statuses, URL outcomes, id prefix, candidate pointer key (AST-1229)`.
2. After `METEORITE_CONFIG` (before `METEORITE_EMAIL_INGEST_CONFIG`), add:

```python
# AST-1229: durable Surfer run (client-driven). Not a dispatcher ledger row.
SURFER_BATCH_CONFIG = {
    "batch_id_prefix": "surfer",  # ids: f"{prefix}-{uuid4()}"
    "candidate_data_lifecycle_key": "active_surfer_batch_id",  # under candidate_data.lifecycle
    # Batch-level statuses (core transitions only).
    "statuses": {
        "RUNNING": {"terminal": False},
        "COMPLETED": {"terminal": True},
        "CANCELLED": {"terminal": True},
    },
    "initial_status": "RUNNING",
    # Per-URL outcome vocabulary on the worklist (not job JOB_STATES).
    "url_outcomes": {
        "pending": {"terminal": False},    # never visited
        "delivered": {"terminal": False},  # posted / attributed; classification not resolved
        "success": {"terminal": True},
        "failed": {"terminal": True},
    },
    "initial_url_outcome": "pending",
}
```

3. Immediately after the block, assert:

```python
assert SURFER_BATCH_CONFIG["initial_status"] in SURFER_BATCH_CONFIG["statuses"]
assert SURFER_BATCH_CONFIG["initial_url_outcome"] in SURFER_BATCH_CONFIG["url_outcomes"]
assert all(
    isinstance(v.get("terminal"), bool)
    for v in SURFER_BATCH_CONFIG["statuses"].values()
)
assert all(
    isinstance(v.get("terminal"), bool)
    for v in SURFER_BATCH_CONFIG["url_outcomes"].values()
)
```

⚠️ **Decision — no staleness / expiry keys:** Parent settled no staleness window. Do not add `stale_after_hours`, expiry sweep, or a third terminal status.

⚠️ **Decision — URL outcomes stay four values:** `pending` / `delivered` / `success` / `failed` cover AC4 (delivered-but-unresolved and never-visited stay non-terminal). A separate `claimed` URL state is **out of scope** here; siblings that need visit-in-flight locking add it later via config + plan change, not invent ad hoc strings.

## Stage 2: `surfer_batch` table and data helpers

**Done when:** A fresh DB creates `surfer_batch` via ensure; header inventory documents it; the helpers below round-trip a row; `mark_stale_ledger_interrupted` and `claim_job_batch` / `clear_job_batch` are **untouched**; `python3 -m py_compile src/data/database.py` succeeds.

1. In `src/data/database.py` module docstring **Tables used (inventory):**, add after `company_job_scan` (keep inventory style):
   `- surfer_batch — Surfer: durable client-driven run (batch_id PK, candidate_id, status, started_at, urls JSON worklist, job_ids JSON association, created_at, updated_at) (AST-1229).`
2. Near other `_…_schema_ensured` flags, add `_surfer_batch_schema_ensured = False`.
3. Implement `_ensure_surfer_batch_schema(conn)` (idempotent, same pattern as `_ensure_company_job_scan_schema`):

```sql
CREATE TABLE surfer_batch (
    batch_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    urls TEXT NOT NULL,
    job_ids TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
```

   No ALTER migrations beyond CREATE IF NOT EXISTS for v1.

4. Add parsers/helpers (private as needed): `_parse_surfer_batch_row` — `json.loads` `urls` and `job_ids` into lists; raise/propagate JSON errors to caller (data raises, caller logs — do not swallow).

5. Public data API (batch_id-first where an id is required; no status/outcome business rules):

| Function | Behavior |
|----------|----------|
| `insert_surfer_batch(batch_id, candidate_id, status, started_at, urls, job_ids)` | Insert one row. `urls` / `job_ids` are Python lists; serialize with `json.dumps`. Set `created_at` / `updated_at` via existing `_utc_now()`. Return `True` on insert, `False` on duplicate PK (`INSERT OR IGNORE` or catch integrity — match `save_dispatch_ledger` style). |
| `get_surfer_batch(batch_id)` | Row dict with parsed `urls` / `job_ids`, or `None`. |
| `list_surfer_batches_for_candidate(candidate_id)` | All rows for candidate, newest `started_at` first. |
| `update_surfer_batch(batch_id, *, status=None, urls=None, job_ids=None)` | Update only provided fields; always bump `updated_at`. Raise `ValueError` if no fields to update. No-op fields omitted. Do **not** change `started_at` or `candidate_id`. If row missing, raise `ValueError`. |

6. Do **not** add claim/clear helpers that touch `job.batch_id` or `company.batch_id`. Do **not** teach `mark_stale_ledger_interrupted` about `surfer_batch`.

⚠️ **Decision — association lives on the batch row as `job_ids` JSON:** Parent forbids using dispatcher `job.batch_id` (claim lock, cleared on release). A join table is unnecessary for AC6; append-only JSON id list on the batch survives claim/release. Do not add `surfer_batch_id` on `job`.

⚠️ **Decision — study `company_job_scan` for ensure/insert shape only:** That table is insert-only scan outcomes keyed by dispatcher `batch_id`. Surfer batch is a mutable entity row; do not overload `company_job_scan` or `dispatch_ledger`.

## Stage 3: Core `surfer.py` — transitions, pointer, jobs

**Done when:** Creating a batch yields a RUNNING row with `started_at` set and readable via `get_surfer_batch`; candidate `lifecycle.active_surfer_batch_id` is set; URL outcome updates can leave the batch non-terminal when any URL is `pending` or `delivered`; when every URL outcome is terminal and status is RUNNING, core moves the batch to COMPLETED and clears the pointer; CANCELLED clears the pointer without requiring all URLs terminal; `list_surfer_batch_jobs` returns jobs by the batch's `job_ids` after `clear_job_batch` would have wiped a dispatcher claim; `python3 -m py_compile src/core/surfer.py` succeeds; `CANDIDATE_DATA_MODEL.md` documents the lifecycle key.

1. Create `src/core/surfer.py` with module docstring noting AST-1229 and that HTTP / page_intake wiring is siblings AST-1230 / AST-1231.

2. Helpers (use `SURFER_BATCH_CONFIG` only — no hardcoded status/outcome string sets in branches):

   - `_status_cfg(name) -> dict` — raise `ValueError` if unknown.
   - `_url_outcome_cfg(name) -> dict` — raise `ValueError` if unknown.
   - `_is_terminal_status(name) -> bool` / `_is_terminal_url_outcome(name) -> bool` from config `terminal` flags.
   - `_new_batch_id() -> str` — `f"{SURFER_BATCH_CONFIG['batch_id_prefix']}-{uuid4()}"`.
   - `_lifecycle_pointer_key() -> str` — `SURFER_BATCH_CONFIG["candidate_data_lifecycle_key"]`.
   - `_read_active_pointer(candidate_id) -> Optional[str]` — from `get_candidate` → `candidate_data.lifecycle[key]`.
   - `_set_active_pointer(candidate_id, batch_id: Optional[str]) -> None` — `save_candidate_data(candidate_id, {"lifecycle": {key: batch_id}})` when setting; when clearing, merge `lifecycle` with that key set to `None` **or** delete the key via read-modify-write of the lifecycle dict then `save_candidate_data` so other lifecycle fields (`reap_*`) are preserved. Prefer read-modify-write of the full `lifecycle` object so deep-merge cannot leave a stale id.

3. `create_surfer_batch(candidate_id: str, urls: List[str]) -> Dict[str, Any]`:
   - Require non-empty `candidate_id`; `get_candidate` must exist or raise `ValueError`.
   - Require `urls` is a non-empty list of non-empty stripped strings; raise `ValueError` otherwise. Deduplicate **preserving order** (first wins) so the worklist has unique URLs.
   - If `_read_active_pointer` returns an id whose `get_surfer_batch` exists and status is non-terminal → raise `ValueError` (at most one non-terminal Surfer batch per candidate).
   - If pointer is set but batch missing or already terminal → clear the stale pointer, then proceed.
   - `batch_id = _new_batch_id()`; `started_at =` UTC `YYYY-MM-DD HH:MM:SS` (same format as `_utc_now` / candidate transitions).
   - Build `url_entries = [{"url": u, "outcome": initial_url_outcome, "updated_at": None}, ...]`.
   - `insert_surfer_batch(..., status=initial_status, urls=url_entries, job_ids=[])`; on duplicate failure raise `RuntimeError`.
   - `_set_active_pointer(candidate_id, batch_id)`.
   - Return `get_surfer_batch(batch_id)` (must include `started_at` as stored).

4. `get_surfer_batch(batch_id: str) -> Optional[Dict[str, Any]]` — thin wrap of data `get_surfer_batch`.

5. `get_active_surfer_batch(candidate_id: str) -> Optional[Dict[str, Any]]` — read pointer; if unset return `None`; load batch; if missing or terminal, clear pointer and return `None`; else return batch.

6. `transition_surfer_batch_status(batch_id: str, to_status: str) -> Dict[str, Any]`:
   - Load batch or raise.
   - Validate `to_status` via `_status_cfg`.
   - If `to_status == COMPLETED` (the config key whose name is `"COMPLETED"`): require every URL entry's `outcome` is terminal; else raise `ValueError` with a clear message (AC4).
   - If `to_status == from_status`, return batch unchanged.
   - Allowed edges (encode as data from config, not a scattered if-forest):
     - From non-terminal → any other status in `statuses` (RUNNING→COMPLETED, RUNNING→CANCELLED).
     - From terminal → raise `ValueError` (no reopen in this ticket).
   - `update_surfer_batch(batch_id, status=to_status)`.
   - If `_is_terminal_status(to_status)`: clear pointer when it equals this `batch_id`.
   - Return updated batch.

7. `set_surfer_batch_url_outcome(batch_id: str, url: str, outcome: str) -> Dict[str, Any]`:
   - Validate outcome via `_url_outcome_cfg`.
   - Find entry where `entry["url"] == url` (exact match to stored string); raise `ValueError` if missing.
   - Set `outcome` and `updated_at` to now; `update_surfer_batch(..., urls=...)`.
   - If batch status is non-terminal **and** every URL outcome is terminal: call `transition_surfer_batch_status(batch_id, "COMPLETED")` (auto-complete).
   - Else return updated batch (still non-terminal when any `pending` or `delivered` remains — AC4).

8. `add_surfer_batch_job(batch_id: str, astral_job_id: str) -> Dict[str, Any]`:
   - Validate non-empty `astral_job_id`.
   - Append to `job_ids` if not already present (idempotent); `update_surfer_batch`.
   - Return updated batch. Does **not** write `job.batch_id`.

9. `list_surfer_batch_jobs(batch_id: str) -> List[Dict[str, Any]]`:
   - Load batch or raise.
   - For each id in `job_ids` order, `database.get_job(id)`; skip missing ids (do not raise). Return list of job dicts. This answer must not depend on `job.batch_id` (AC6 / AC7).

10. In `docs/features/candidate/CANDIDATE_DATA_MODEL.md`, under meta / lifecycle documentation, add that `candidate_data.lifecycle.active_surfer_batch_id` (key name from `SURFER_BATCH_CONFIG["candidate_data_lifecycle_key"]`) holds the id of the candidate's non-terminal Surfer batch when one exists, and is cleared when that batch reaches a terminal status (AST-1229). Keep it a sibling of `reap_*` under `lifecycle`, not inside contact/context/artifacts.

⚠️ **Decision — core owns auto-COMPLETE:** Data layer never decides COMPLETED. URL writers call `set_surfer_batch_url_outcome`; that function asks core transition when the worklist is fully terminal (`astral.state.core-decides-transitions`).

⚠️ **Decision — one active non-terminal batch per candidate:** AC5 is singular. `create_surfer_batch` refuses a second concurrent RUNNING batch rather than silently overwriting the pointer.

⚠️ **Decision — no HTTP in this ticket:** AST-1230 creates batches from search-page classification; AST-1231 posts batch-scoped pages and remaining-work queries. They call these core functions. Do not add Flask routes here.

## Self-Assessment

**Scope:** Single-Component — one new table + config block + new `src/core/surfer.py`, plus a lifecycle meta-key doc note; no dispatcher or UI surface.

**Conf:** high — settled parent decisions (new table, no staleness, `candidate_data` pointer); precedents in `company_job_scan` ensure/insert, intake-session durable row, and `lifecycle.reap_*` pointer neighborhood.

**Risk:** Medium — wrong COMPLETED rules or pointer handling would break resume/cancel siblings and lie about unfinished work; dispatcher claim paths are explicitly untouched so regression there is low if the plan is followed.

## Rules check (plan-child §8)

- **§1.3 DRY:** Status/outcome vocabularies live only in `SURFER_BATCH_CONFIG`; core reads flags, does not restate string sets.
- **§2.1 config:** Named config block; no env for these literals; no expiry keys.
- **§2.4 batch:** `batch_id` format `surfer-{uuid}`; batch_id-first data updates; Surfer association does **not** use entity claim locks on `job`/`company` (AC7). Claim/process/release for dispatcher jobs unchanged.
- **§2.6 state:** Transitions decided in `src/core/surfer.py`; data `update_surfer_batch` only applies the status core passes.
- **§3.3 imports:** `surfer.py` (core) → data + utils only; no ui shortcut.
- **§3.5 naming:** snake_case module/functions; table `surfer_batch`.
- **Header inventory:** Stage 2 amends the database module docstring (statute `astral.standards.database-header-inventory`).
