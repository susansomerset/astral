# AST-1229 — Surfer batch entity and candidate pointer

**Linear:** [AST-1229](https://linear.app/astralcareermatch/issue/AST-1229/surfer-batch-entity-and-candidate-pointer-surfer-batch-durable)
**Parent:** [AST-1169](https://linear.app/astralcareermatch/issue/AST-1169/surfer-batch-durable-worklist-state-and-batch-scoped-intake) — Surfer batch — durable worklist state and batch-scoped intake
**Publish ref:** `origin/sub/AST-1169/AST-1229-surfer-batch-entity`

Durable Surfer batch record on a **new** `surfer_batch` table (not `dispatch_ledger`): status, readable start time, target URL worklist with per-URL outcomes, batch-owned job association, registered status transitions in core, and a `candidate_data.lifecycle` pointer to any non-terminal batch. Introduces the externally resumable, client-driven batch shape. Does **not** wire search-page creation, batch-scoped page posts, remaining-work HTTP, cancel/discard UX, or dispatcher claim/release.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `SURFER_BATCH_CONFIG` (statuses with `requires_all_urls_terminal`, URL outcomes, id prefix, candidate_data pointer key); document in module header | utils |
| `src/data/database.py` | Header inventory; `_ensure_surfer_batch_schema`; register in upsert lazy-ensure registries; insert/get/update/list helpers each calling ensure | data |
| `src/core/surfer.py` | **New** module: create/active-get, status transitions, URL outcome writes + auto-complete, candidate pointer set/clear, job association; `debug` threaded; `get_logger(__name__)` | core |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Document `lifecycle.active_surfer_batch_id` meta key (stored value `None` = cleared) | docs |

No UI routes, no `dispatcher.py` / `claim_*_batch` / `clear_*_batch` changes, no `tests/` or bible (Betty after Code Complete). Do **not** add a permanent `surfer_batch_id` column on `job`. Do **not** reuse or extend `dispatch_ledger`.

## Stage 1: `SURFER_BATCH_CONFIG`

**Done when:** `SURFER_BATCH_CONFIG` is importable from `src.utils.config` with the keys below; module docstring lists the block; asserts pass; `python3 -m py_compile src/utils/config.py` succeeds; no other config blocks changed.

1. In `src/utils/config.py` module docstring `Config sections:`, add:
   `SURFER_BATCH_CONFIG — Surfer client-driven batch statuses, URL outcomes, id prefix, candidate pointer key (AST-1229)`.
2. After `METEORITE_CONFIG` (before `METEORITE_EMAIL_INGEST_CONFIG`), add:

```python
# AST-1229: durable Surfer run (client-driven). Not a dispatcher ledger row.
SURFER_BATCH_CONFIG = {
    "batch_id_prefix": "surfer",  # ids: f"{prefix}-{uuid4()}"
    "candidate_data_lifecycle_key": "active_surfer_batch_id",  # under candidate_data.lifecycle
    # Batch-level statuses (core transitions only).
    # requires_all_urls_terminal: True only on the status used for worklist-complete auto-transition.
    "statuses": {
        "RUNNING": {"terminal": False, "requires_all_urls_terminal": False},
        "COMPLETED": {"terminal": True, "requires_all_urls_terminal": True},
        "CANCELLED": {"terminal": True, "requires_all_urls_terminal": False},
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
    and isinstance(v.get("requires_all_urls_terminal"), bool)
    for v in SURFER_BATCH_CONFIG["statuses"].values()
)
assert all(
    isinstance(v.get("terminal"), bool)
    for v in SURFER_BATCH_CONFIG["url_outcomes"].values()
)
# Exactly one auto-complete target (worklist-complete → that status).
assert sum(
    1 for v in SURFER_BATCH_CONFIG["statuses"].values() if v["requires_all_urls_terminal"]
) == 1
assert all(
    SURFER_BATCH_CONFIG["statuses"][name]["terminal"]
    for name, v in SURFER_BATCH_CONFIG["statuses"].items()
    if v["requires_all_urls_terminal"]
)
```

⚠️ **Decision — no staleness / expiry keys:** Parent settled no staleness window. Do not add `stale_after_hours`, expiry sweep, or a third terminal status.

⚠️ **Decision — URL outcomes stay four values:** `pending` / `delivered` / `success` / `failed` cover AC4 (delivered-but-unresolved and never-visited stay non-terminal). A separate `claimed` URL state is **out of scope** here; siblings that need visit-in-flight locking add it later via config + plan change, not invent ad hoc strings.

⚠️ **Decision — `requires_all_urls_terminal` on status entries:** COMPLETED needs a fully terminal worklist; CANCELLED does not. Core selects the auto-complete target by finding the unique status with this flag True — never by comparing to the literal `"COMPLETED"`.

## Stage 2: `surfer_batch` table and data helpers

**Done when:** A fresh DB creates `surfer_batch` via ensure (including startup upsert registry + each public helper); header inventory documents it; the helpers below round-trip a row; `mark_stale_ledger_interrupted` and `claim_job_batch` / `clear_job_batch` are **untouched**; `python3 -m py_compile src/data/database.py` succeeds.

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

4. **Lazy-ensure registry (required — same as `company_job_scan`):**
   - Add `"surfer_batch": ("_surfer_batch_schema_ensured",)` to `_UPSERT_SCHEMA_ENSURE_FLAGS`.
   - Add `"surfer_batch": _ensure_surfer_batch_schema` to `_UPSERT_LAZY_SCHEMA_HANDLERS`.
   - That registers the table with `ensure_all_upsert_registry_schemas_at_startup()` (`src/core/bootstrap.py`).

5. Add parsers/helpers (private as needed): `_parse_surfer_batch_row` — `json.loads` `urls` and `job_ids` into lists; raise/propagate JSON errors to caller (data raises, caller logs — do not swallow).

6. Public data API (batch_id-first where an id is required; no status/outcome business rules). **Each** public helper's `_with_conn` body must call `_ensure_surfer_batch_schema(conn)` before SQL (mirror `list_company_job_scans` / `record_to_company_job_scan` at lines that call ensure on the open connection):

| Function | Behavior |
|----------|----------|
| `insert_surfer_batch(batch_id, candidate_id, status, started_at, urls, job_ids)` | Ensure schema; insert one row. `urls` / `job_ids` are Python lists; serialize with `json.dumps`. Set `created_at` / `updated_at` via existing `_utc_now()`. Return `True` on insert, `False` on duplicate PK (`INSERT OR IGNORE` or catch integrity — match `save_dispatch_ledger` style). |
| `get_surfer_batch(batch_id)` | Ensure schema; row dict with parsed `urls` / `job_ids`, or `None`. |
| `list_surfer_batches_for_candidate(candidate_id)` | Ensure schema; all rows for candidate, newest `started_at` first. |
| `update_surfer_batch(batch_id, *, status=None, urls=None, job_ids=None)` | Ensure schema; update only provided fields; always bump `updated_at`. Raise `ValueError` if no fields to update. No-op fields omitted. Do **not** change `started_at` or `candidate_id`. If row missing, raise `ValueError`. |

7. Do **not** add claim/clear helpers that touch `job.batch_id` or `company.batch_id`. Do **not** teach `mark_stale_ledger_interrupted` about `surfer_batch`.

⚠️ **Decision — association lives on the batch row as `job_ids` JSON:** Parent forbids using dispatcher `job.batch_id` (claim lock, cleared on release). A join table is unnecessary for AC6; append-only JSON id list on the batch survives claim/release. Do not add `surfer_batch_id` on `job`.

⚠️ **Decision — study `company_job_scan` for ensure/insert + registry shape only:** That table is insert-only scan outcomes keyed by dispatcher `batch_id`. Surfer batch is a mutable entity row; do not overload `company_job_scan` or `dispatch_ledger`.

## Stage 3: Core `surfer.py` — transitions, pointer, jobs

**Done when:** Creating a batch yields a RUNNING row with `started_at` set and readable via `database.get_surfer_batch`; candidate `lifecycle.active_surfer_batch_id` is set; clearing uses `{key: None}` overwrite so the stored record no longer identifies the batch (AC5); URL outcome updates can leave the batch non-terminal when any URL is `pending` or `delivered`; when every URL outcome is terminal and status is non-terminal, core moves the batch to the config auto-complete status and clears the pointer; CANCELLED clears the pointer without requiring all URLs terminal; `list_surfer_batch_jobs` returns jobs by the batch's `job_ids` independent of `job.batch_id`; public functions accept `debug: bool = False`; `python3 -m py_compile src/core/surfer.py` succeeds; `CANDIDATE_DATA_MODEL.md` documents the lifecycle key.

**File layout (build order vs source order):** Implement helpers when needed while coding stages, but the **finished** `src/core/surfer.py` must place **public entrypoints first**, then a helpers section (`astral.standards.public-then-helpers`). Do not ship helpers above public defs.

1. Create `src/core/surfer.py` with module docstring noting AST-1229 and that HTTP / page_intake wiring is siblings AST-1230 / AST-1231.
2. Imports: `from src.data import database`; `from src.core.candidate import get_candidate, save_candidate_data`; `from src.utils.config import SURFER_BATCH_CONFIG`; `from src.utils.logging import get_logger`. Module logger: `logger = get_logger(__name__)` (same as `candidate.py`).
3. **No core function named `get_surfer_batch`.** Every data-layer call in this module is module-qualified: `database.get_surfer_batch`, `database.insert_surfer_batch`, `database.update_surfer_batch`, `database.get_job`, etc. Read-by-id for callers outside this module is `database.get_surfer_batch` (or a future thin UI/core wrapper with a **different** name). This avoids import shadowing / accidental recursion.

### Public API (signatures — all take `debug: bool = False`)

Thread `debug` into `save_candidate_data(..., debug=debug)` and any Style-D logging this module adds. Emission of per-URL found/recorded detail for parent AC8 remains AST-1231's job; threading the flag **now** is the contract so AST-1231 does not amend these signatures.

4. `create_surfer_batch(candidate_id: str, urls: List[str], *, debug: bool = False) -> Dict[str, Any]`:
   - Require non-empty `candidate_id`; `get_candidate` must exist or raise `ValueError`.
   - Require `urls` is a non-empty list of non-empty stripped strings; raise `ValueError` otherwise. Deduplicate **preserving order** (first wins) so the worklist has unique URLs.
   - If `_read_active_pointer` returns an id whose `database.get_surfer_batch` exists and status is non-terminal → raise `ValueError` (at most one non-terminal Surfer batch per candidate).
   - If pointer is set but batch missing or already terminal → clear the stale pointer (`_set_active_pointer(..., None, debug=debug)`), then proceed.
   - `batch_id = _new_batch_id()`; `started_at =` UTC `YYYY-MM-DD HH:MM:SS` (same format as database `_utc_now` / candidate transitions).
   - Build `url_entries = [{"url": u, "outcome": SURFER_BATCH_CONFIG["initial_url_outcome"], "updated_at": None}, ...]`.
   - `database.insert_surfer_batch(..., status=SURFER_BATCH_CONFIG["initial_status"], urls=url_entries, job_ids=[])`; on duplicate failure raise `RuntimeError`.
   - `_set_active_pointer(candidate_id, batch_id, debug=debug)`.
   - Return `database.get_surfer_batch(batch_id)` (must include `started_at` as stored).

⚠️ **Decision — one active non-terminal batch per candidate:** Derived from AC5 (pointer holds one id; overwrite would orphan a RUNNING batch). `create_surfer_batch` raises `ValueError` rather than overwriting. **Hand-off to AST-1230:** that error is user-visible when a search page tries to start a second batch; the page_intake / envelope copy and HTTP mapping for this failure belong to AST-1230 — this ticket only defines the core `ValueError`.

5. `get_active_surfer_batch(candidate_id: str, *, debug: bool = False) -> Optional[Dict[str, Any]]` — read pointer; if unset/`None` return `None`; `database.get_surfer_batch`; if missing or terminal, clear pointer and return `None`; else return batch.

6. `transition_surfer_batch_status(batch_id: str, to_status: str, *, debug: bool = False) -> Dict[str, Any]`:
   - Load via `database.get_surfer_batch` or raise.
   - Validate `to_status` via `_status_cfg`.
   - If `_status_cfg(to_status)["requires_all_urls_terminal"]`: require every URL entry's `outcome` is terminal (`_is_terminal_url_outcome`); else raise `ValueError` with a clear message (AC4). Do **not** branch on the string `"COMPLETED"`.
   - If `to_status == from_status`, return batch unchanged.
   - Allowed edges: from non-terminal → any other status in `statuses`; from terminal → raise `ValueError` (no reopen in this ticket).
   - `database.update_surfer_batch(batch_id, status=to_status)`.
   - If `_is_terminal_status(to_status)`: clear pointer when it equals this `batch_id`.
   - Return `database.get_surfer_batch(batch_id)`.

7. `set_surfer_batch_url_outcome(batch_id: str, url: str, outcome: str, *, debug: bool = False) -> Dict[str, Any]`:
   - Validate outcome via `_url_outcome_cfg`.
   - Find entry where `entry["url"] == url` (exact match to stored string); raise `ValueError` if missing.
   - Set `outcome` and `updated_at` to now; `database.update_surfer_batch(..., urls=...)`.
   - If batch status is non-terminal **and** every URL outcome is terminal: call `transition_surfer_batch_status(batch_id, _auto_complete_status(), debug=debug)` where `_auto_complete_status()` returns the unique status name with `requires_all_urls_terminal` True.
   - Else return updated batch (still non-terminal when any `pending` or `delivered` remains — AC4).

8. `add_surfer_batch_job(batch_id: str, astral_job_id: str, *, debug: bool = False) -> Dict[str, Any]`:
   - Validate non-empty `astral_job_id`.
   - Append to `job_ids` if not already present (idempotent); `database.update_surfer_batch`.
   - Return updated batch. Does **not** write `job.batch_id`.

9. `list_surfer_batch_jobs(batch_id: str, *, debug: bool = False) -> List[Dict[str, Any]]`:
   - Load batch or raise.
   - For each id in `job_ids` order, `database.get_job(id)`; skip missing ids (do not raise). Return list of job dicts. This answer must not depend on `job.batch_id` (AC6 / AC7).

10. In `docs/features/candidate/CANDIDATE_DATA_MODEL.md`, under meta / lifecycle documentation, add that `candidate_data.lifecycle.active_surfer_batch_id` (key name from `SURFER_BATCH_CONFIG["candidate_data_lifecycle_key"]`) holds the id of the candidate's non-terminal Surfer batch when one exists, and is cleared to JSON `null` (`None` in Python) when that batch reaches a terminal status (AST-1229). Readers treat `None` and absent identically. Keep it a sibling of `reap_*` under `lifecycle`, not inside contact/context/artifacts.

### Helpers (below public API in the finished file)

11. Helpers (config-driven — no hardcoded status/outcome string sets in branches):

   - `_status_cfg(name) -> dict` — raise `ValueError` if unknown.
   - `_url_outcome_cfg(name) -> dict` — raise `ValueError` if unknown.
   - `_is_terminal_status(name) -> bool` / `_is_terminal_url_outcome(name) -> bool` from config `terminal` flags.
   - `_auto_complete_status() -> str` — the unique `statuses` key with `requires_all_urls_terminal` True (config assert guarantees uniqueness).
   - `_new_batch_id() -> str` — `f"{SURFER_BATCH_CONFIG['batch_id_prefix']}-{uuid4()}"`.
   - `_lifecycle_pointer_key() -> str` — `SURFER_BATCH_CONFIG["candidate_data_lifecycle_key"]`.
   - `_read_active_pointer(candidate_id) -> Optional[str]` — from `get_candidate` → `candidate_data.lifecycle[key]`. Treat missing key, `None`, and empty string as no pointer (`return None`).
   - `_set_active_pointer(candidate_id, batch_id: Optional[str], *, debug: bool = False) -> None` — **single prescribed path for set and clear:**

```python
save_candidate_data(
    candidate_id,
    {"lifecycle": {_lifecycle_pointer_key(): batch_id}},
    debug=debug,
)
```

     Pass the real id string to set; pass `None` to clear. `_deep_merge` overwrites nested values for overlay keys, so `{key: None}` stores JSON null and clears the pointer for every reader (AC5). **Do not** read-modify-write the lifecycle dict and omit the key — `_deep_merge` only walks overlay keys, so omission leaves a stale id. **Do not** use `replace=True` (that would wipe contact/context/artifacts). There is no in-repo precedent for clearing a `lifecycle` key (`_start_candidate_reap_timer` only sets `reap_*`); this overwrite-with-`None` path is the contract.

⚠️ **Decision — core owns auto-complete via config flag:** Data layer never decides the target status. `set_surfer_batch_url_outcome` calls `transition_surfer_batch_status` with `_auto_complete_status()` when the worklist is fully terminal (`astral.state.core-decides-transitions`).

⚠️ **Decision — no HTTP in this ticket:** AST-1230 creates batches from search-page classification; AST-1231 posts batch-scoped pages and remaining-work queries. They call these core functions. Do not add Flask routes here.

⚠️ **Decision — `debug` threaded now:** Parent AC8 / `astral.standards.debug-contract-gated` emission is AST-1231, but §1.5.1 requires `debug: bool = False` on the backend call chain. All public functions in this module take and forward `debug` so AST-1231 inherits the contract without signature churn.

## Self-Assessment

**Scope:** Single-Component — one new table + config block + new `src/core/surfer.py`, plus a lifecycle meta-key doc note; no dispatcher or UI surface.

**Conf:** Medium — parent decisions remain settled; Joan round-1 fixed the pointer-clear mechanism against real `_deep_merge` behavior and tightened config/registry/`debug` contracts that were underspecified.

**Risk:** Medium — wrong COMPLETED rules or pointer handling would break resume/cancel siblings and lie about unfinished work; dispatcher claim paths are explicitly untouched so regression there is low if the plan is followed.

## Rules check (plan-child §8)

- **§1.3 DRY:** Status/outcome vocabularies live only in `SURFER_BATCH_CONFIG`; core reads `terminal` / `requires_all_urls_terminal` flags, does not restate string sets or branch on `"COMPLETED"`.
- **§2.1 config:** Named config block; no env for these literals; no expiry keys; auto-complete target selected from config.
- **§2.4 batch:** `batch_id` format `surfer-{uuid}`; batch_id-first data updates; Surfer association does **not** use entity claim locks on `job`/`company` (AC7). Claim/process/release for dispatcher jobs unchanged.
- **§2.6 state:** Transitions decided in `src/core/surfer.py`; data `update_surfer_batch` only applies the status core passes.
- **§3.3 imports:** `surfer.py` (core) → data + utils (+ candidate core for pointer) only; no ui shortcut; data calls always `database.*`.
- **§3.5 naming:** snake_case module/functions; table `surfer_batch`; no core name collision with data `get_surfer_batch`.
- **Header inventory + upsert registry:** Stage 2 amends the database module docstring and registers `surfer_batch` in `_UPSERT_*` maps (`astral.standards.database-header-inventory`).
- **public-then-helpers / debug:** Finished module layout and `debug: bool = False` on public entrypoints.

## Revisions

### Revision 1 — 2026-08-07
Driven by: Joan `[plan-discuss] round=1 concern` (plan-rubric.v1 REVISE) — fix-now on `_set_active_pointer` clear path; discuss items on name shadowing, upsert registry, `requires_all_urls_terminal`, `debug` threading / logger, public-then-helpers layout, AST-1230 error hand-off.
Changes:
- Pointer clear is only `save_candidate_data(..., {"lifecycle": {key: None}})`; `_read_active_pointer` treats `None`/absent/empty as unset; dropped read-modify-write omit-key option.
- No core `get_surfer_batch`; all data access is `database.*`.
- `surfer_batch` registered in `_UPSERT_SCHEMA_ENSURE_FLAGS` / `_UPSERT_LAZY_SCHEMA_HANDLERS`; each public helper calls `_ensure_surfer_batch_schema(conn)`.
- Status entries gain `requires_all_urls_terminal`; auto-complete uses `_auto_complete_status()`; transition precondition uses that flag (not `"COMPLETED"` literal).
- All public core functions take `debug: bool = False`; module uses `get_logger(__name__)`.
- Finished file layout: public then helpers; one-batch `ValueError` flagged as AST-1230 envelope hand-off.
- Self-assessment Conf → Medium.

## Review

**Publish ref:** `origin/sub/AST-1169/AST-1229-surfer-batch-entity`
**Tip (pre-review):** `aa14988c`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `1dfd377f` | `SURFER_BATCH_CONFIG` |
| 2 | `156cbe65` | `surfer_batch` table + data helpers + upsert registry |
| 3 | `55d45854` | `src/core/surfer.py` + lifecycle pointer doc |

### Radia review — code-rubric.v1

[code-rubric] revision=1
**Publish ref:** `origin/sub/AST-1169/AST-1229-surfer-batch-entity` @ `f819b685ba3e216fac04b31e1fe6119475fb3ebd`
**Overall:** CLEAN

Full active set (65 statutes: 18 universal + 47 scoped) scored in-session against `git diff origin/dev...origin/sub/AST-1169/AST-1229-surfer-batch-entity`. No `violates`, no `needs-discussion`. Joan's `plan-rubric.v1` verdict (APPROVED) is attached as a Linear comment; her final sweep already moved `astral.standards.debug-contract-gated` / `astral.layers.import-direction` / `astral.standards.data-raises-caller-logs` to `conforms` in-scope rather than excluded, matching this sweep — no C4 straggler.

**What's solid:** pointer clear is the single `save_candidate_data(..., {"lifecycle": {key: None}})` overwrite path (verified against real `_deep_merge`); no core `get_surfer_batch` name shadow — every data call is `database.*`; `surfer_batch` is registered in both `_UPSERT_SCHEMA_ENSURE_FLAGS` / `_UPSERT_LAZY_SCHEMA_HANDLERS` and each public data helper calls `_ensure_surfer_batch_schema(conn)`; auto-complete keys off `requires_all_urls_terminal` (config asserts guarantee exactly one such status, and that it's terminal) rather than a `"COMPLETED"` literal; `src/core/surfer.py` is public-then-helpers cleanly; `debug: bool = False` threaded on all nine public functions; test-tree changes arrived via a single `merge-tests(AST-1229)` commit — engineer commits never touch `tests/` or `docs/test-bible/**`.

**Advisory:** `transition_surfer_batch_status` checks `to_status == from_status` before the `requires_all_urls_terminal` precondition (plan lists the precondition first). This makes a same-status no-op call idempotent even from a fully-terminal batch instead of raising — safer than a literal reading of the plan step order, no AC or statute impact.

## Frame diff

(none) — implementation matches the approved plan; no description drift to reconcile.

context_tokens≈95000

— Radia
