# AST-1557 — meteorite table + claim helpers

**Linear:** [AST-1557](https://linear.app/astralcareermatch/issue/AST-1557/meteorite-table-claim-helpers)  
**Parent:** [AST-1555](https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation) — Meteorite ingress: staging table + inbox/meteorite consolidation  
**Publish ref:** `sub/AST-1555/AST-1557-meteorite-table-claim-helpers`

Add the flat `meteorite` staging table, its config state registry (`prior_states` / transition literals), and data-layer claim / insert / update / retention helpers so later children can fan-out classify results, claim one transition at a time, and purge/list stale rows without inventing schema or hardcoded state sets. No inbox verbs, classify runner, Estelle, Manage Email, monitoring format, or dispatch seed/task-key retirements.

## Scope gate

Ticket **## Scope** (verbatim):

`src/data/database.py` (new table + claim/insert/update/retention helpers + header inventory); `src/utils/config.py` (meteorite state registry / transition literals only — not monitoring format or task-key retirements owned by later children)

All Files Changed / Stages stay inside that set.

**Out of scope (siblings):**

- Inbox candidate verbs / Manage Email / `FETCH_EMAIL_CONFIG` / `INBOX_BIND_CONFIG` / `fetch_email` seeds — **AST-1558**
- `check_inbox` + monitoring log format / mailbox task repoint — **AST-1559**
- stage / scrape / land transition runners in `meteorite.py` — **AST-1560**
- BOT_BLOCKED Estelle notify / `apply_paste` — **AST-1561**
- Retention **runner** wiring + delete `meteorite_email.py` — **AST-1562** (this ticket owns select/delete **helpers** only)

**AC partition (this ticket):** Supplies the durable spine for parent AC1 (N `meteorite` rows on successful classify fan-out; zero rows when classify fails — callers in later children). Does **not** implement archive, classify, or Gmail.

**Depends on:** none (Bang !! — first child).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `METEORITE_STATES` registry + retention state-partition literals + header bullet; asserts lockstep | utils |
| `src/data/database.py` | Header inventory + `_ensure_meteorite_schema` + claim/get/clear + insert fan-out + get/update/list-by-state + retention select/delete helpers | data |

## Stage 1: Config — `METEORITE_STATES` registry

**Done when:** `METEORITE_STATES` is importable from `src.utils.config` with exactly the seven staging keys below, each carrying `prior_states`; retention partition tuples name only those keys; `python3 -m py_compile src/utils/config.py` succeeds (repo venv if needed: `~/astral/.venv/bin/python`). No `database.py` changes yet.

1. In `src/utils/config.py` module header inventory (near other `METEORITE_*` bullets), add a bullet:

   - `METEORITE_STATES` — staging-row state registry for the `meteorite` table (`prior_states` per state); distinct from `JOB_STATES` keys like `METEORITE_NEW` (AST-1557).

2. Immediately **after** the existing `METEORITE_CONFIG` assert block (the block that ends with `assert "METEORITE_NEW" in JOB_STATES["BOT_BLOCKED"]["prior_states"]`) and **before** `SURFER_PACING_CONFIG`, insert:

```python
# AST-1557: flat meteorite staging-row states (table spine). Keys are NOT JOB_STATES
# METEORITE_* job lifecycle labels — core transitions decide targets; data accepts state as param.
METEORITE_STATES = {
    "NEW": {
        "prior_states": None,  # insert-only entry from classify fan-out
    },
    "SCRAPE_LINK": {
        "prior_states": ["NEW", "ERROR"],  # link outcomes; retry from ERROR
    },
    "READY": {
        # text fan-out from NEW; scrape success; Estelle paste recovery (sibling)
        "prior_states": ["NEW", "SCRAPE_LINK", "BOT_BLOCKED"],
    },
    "BOT_BLOCKED": {
        "prior_states": ["SCRAPE_LINK"],
    },
    "ERROR": {
        "prior_states": ["SCRAPE_LINK"],  # retry-holding after Playwright / scrape miss
    },
    "LANDED": {
        "prior_states": ["READY"],
    },
    "ABANDONED": {
        "prior_states": ["BOT_BLOCKED", "ERROR"],  # nag limit / terminal stale
    },
}

# Retention partitions (state literals only — day cutoffs are caller/config for AST-1562).
METEORITE_STATES_RETENTION = {
    "purge_states": ("LANDED",),
    "stale_list_states": ("ERROR", "BOT_BLOCKED", "ABANDONED"),
}
```

⚠️ **Decision:** Registry name is `METEORITE_STATES` (entity-parallel to `JOB_STATES` / `CANDIDATE_STATES`). Keys stay short (`NEW`, `READY`, …) per parent functional scope — they collide as **strings** with some `JOB_STATES` keys (`NEW`, `BOT_BLOCKED`) but live in a separate dict; callers must import `METEORITE_STATES`, never reuse `JOB_STATES` for staging rows. No `SKIPPED` state (parent: no-job outcomes leave zero rows; audit is the monitoring log in AST-1559).

3. Immediately after those dicts, add asserts:

- `set(METEORITE_STATES) == {"NEW", "SCRAPE_LINK", "READY", "BOT_BLOCKED", "ERROR", "LANDED", "ABANDONED"}`
- every value has key `"prior_states"`
- `METEORITE_STATES["NEW"]["prior_states"] is None`
- `set(METEORITE_STATES_RETENTION["purge_states"]) | set(METEORITE_STATES_RETENTION["stale_list_states"])` ⊆ `set(METEORITE_STATES)`
- `set(METEORITE_STATES_RETENTION["purge_states"]).isdisjoint(METEORITE_STATES_RETENTION["stale_list_states"])`
- for every state `s` with non-`None` `prior_states`, every prior ∈ `METEORITE_STATES`

4. Do **not** add monitoring format strings, subject sanitize limits, scrape/land/notify/retention **task_key** literals, or retire `FETCH_EMAIL_CONFIG` / `INBOX_BIND_CONFIG` in this stage (sibling Scope).

## Stage 2: `meteorite` table + claim / insert / update / get helpers

**Done when:** Header inventory lists `meteorite`; `_ensure_meteorite_schema` creates the table idempotently; `claim_meteorite_batch` / `get_meteorite_batch` / `clear_meteorite_batch` match the batch-id-first claim pattern; `insert_meteorite_rows` can insert N rows in one transaction at state `NEW`; `get_meteorite` / `list_meteorites_by_state` / `update_meteorite` exist and accept caller-supplied `state` without choosing the next state; `python3 -m py_compile src/data/database.py` succeeds.

1. In `src/data/database.py` module docstring **Tables used (inventory)**, add a bullet (keep alphabetical-ish peer placement near other entity tables — after `job` / before or after `candidate` is fine if the list is not strictly sorted; match existing style):

   - `meteorite` — Ingress staging spine (AST-1557): one row per prospective job after classify fan-out; `state` from `METEORITE_STATES`; claim via `batch_id` / `batch_created_at`; columns id, candidate_id, source_kind, source_id, source_ref, state, content, classify_outcome, link, astral_job_id, estelle_thread_ts, estelle_notified_at, nag_count, error, batch_id, batch_created_at, created_at, updated_at, state_changed_at.

2. Near other `_foo_schema_ensured` flags at module top, add `_meteorite_schema_ensured = False`.

3. Implement `_ensure_meteorite_schema(conn)` (idempotent, same shape as `_ensure_company_job_scan_schema`):

   - `CREATE TABLE IF NOT EXISTS meteorite` with columns:

     | Column | Type | Notes |
     |--------|------|-------|
     | `id` | `INTEGER PRIMARY KEY AUTOINCREMENT` | writers omit id |
     | `candidate_id` | `TEXT NOT NULL` | |
     | `source_kind` | `TEXT NOT NULL` | email / slack / paste (callers; no hardcoded set in SQL) |
     | `source_id` | `TEXT NOT NULL` | e.g. Gmail mid |
     | `source_ref` | `TEXT` | nullable provenance handle |
     | `state` | `TEXT NOT NULL` | must be a `METEORITE_STATES` key at write time (enforced by callers / update helper validation against config keys only — **not** prior_states) |
     | `content` | `TEXT` | JD / visible text payload |
     | `classify_outcome` | `TEXT` | stage_meteorite outcome literal |
     | `link` | `TEXT` | scrape URL when link outcome |
     | `astral_job_id` | `TEXT` | set on LANDED (1:1) |
     | `estelle_thread_ts` | `TEXT` | sibling Estelle |
     | `estelle_notified_at` | `TIMESTAMP` | |
     | `nag_count` | `INTEGER NOT NULL DEFAULT 0` | |
     | `error` | `TEXT` | last error message |
     | `batch_id` | `TEXT` | null/empty = unclaimed |
     | `batch_created_at` | `TIMESTAMP` | |
     | `created_at` | `TIMESTAMP NOT NULL` | |
     | `updated_at` | `TIMESTAMP NOT NULL` | |
     | `state_changed_at` | `TIMESTAMP NOT NULL` | |

   - Index: `CREATE INDEX IF NOT EXISTS idx_meteorite_state_batch ON meteorite(state, batch_id)`
   - Index: `CREATE INDEX IF NOT EXISTS idx_meteorite_source ON meteorite(source_kind, source_id)`
   - Set `_meteorite_schema_ensured = True` after ensure.
   - Do **not** register `meteorite` in `_UPSERT_LAZY_SCHEMA_HANDLERS` / `_UPSERT_SCHEMA_ENSURE_FLAGS` unless an existing upsert path already requires it — this table is claim/insert/update, not admin upsert. ⚠️ **Decision:** skip upsert registry; lazy ensure is called from meteorite helpers only (same pattern as tables that are helper-gated rather than startup-upserted). If `ensure_all_upsert_registry_schemas_at_startup` is later required for empty-DB create, that is a sibling/follow-up — do not invent it here.

4. Add row helper `_meteorite_row_to_dict(row) -> dict` (plain `_row_to_dict` is enough if no JSON columns).

5. Implement claim trio (signatures mirror `claim_candidate_batch` / `get_candidate_batch` / `clear_candidate_batch`; batch_id **first**):

   - `claim_meteorite_batch(batch_id: str, state: str, limit: int, *, states: Optional[List[str]] = None) -> int`  
     Claim unclaimed rows (`batch_id IS NULL OR batch_id = ''`) in `state` or `states`; set `batch_id`, `batch_created_at`; `ORDER BY rowid`; `LIMIT ?`; return count. Call `_ensure_meteorite_schema`. Use `_state_in_sql` like jobs/candidates.
   - `get_meteorite_batch(batch_id: str) -> List[Dict[str, Any]]`  
     `SELECT * FROM meteorite WHERE batch_id = ?`.
   - `clear_meteorite_batch(batch_id: str) -> int`  
     Null out `batch_id` and `batch_created_at` for that batch; return count.

6. Implement insert fan-out:

   - `insert_meteorite_rows(rows: List[Dict[str, Any]]) -> List[int]`  
     Insert each dict in **one** transaction. Required keys per row: `candidate_id`, `source_kind`, `source_id`. Optional: `source_ref`, `content`, `classify_outcome`, `link`, `error`.  
     Force `state` to `"NEW"` on insert (ignore any caller-supplied state) so classify fan-out cannot invent entry states.  
     Set `nag_count=0`, timestamps (`created_at` / `updated_at` / `state_changed_at`) via `_utc_now()`, leave claim columns null, leave `astral_job_id` / Estelle fields null.  
     Return list of new integer `id`s in insert order (`cursor.lastrowid` per row).  
     Empty `rows` → return `[]` with no write.

7. Implement read/update:

   - `get_meteorite(meteorite_id: int) -> Optional[Dict[str, Any]]`
   - `list_meteorites_by_state(state: str, *, limit: Optional[int] = None) -> List[Dict[str, Any]]` — unfiltered by batch; optional LIMIT.
   - `list_meteorites_by_source(source_kind: str, source_id: str) -> List[Dict[str, Any]]` — for sibling source-ref dedup on re-fetch.
   - `update_meteorite(meteorite_id: int, **fields) -> None`  
     Allowed field names (whitelist): `state`, `content`, `classify_outcome`, `link`, `astral_job_id`, `estelle_thread_ts`, `estelle_notified_at`, `nag_count`, `error`, `source_ref`.  
     Always bump `updated_at`. When `state` is present: require `state in METEORITE_STATES` (import from config); set `state_changed_at` to now; **do not** enforce `prior_states` here (core decides — `astral.state.core-decides-transitions`).  
     Raise `ValueError` on unknown kwargs or unknown state string. No-op kwargs-only empty → still allowed but must not clear required columns.

8. Wire every new public helper through `_run_with_retry` like peer claim/update functions. On failure use `_log_db_failure` before re-raise where peers do.

## Stage 3: Retention select / delete helpers

**Done when:** Callers can list purge candidates and stale-list rows by state set + cutoff timestamp, and delete by id list, without embedding day numbers or state sets in SQL string literals outside parameters; `python3 -m py_compile src/data/database.py src/utils/config.py` succeeds.

1. In `src/data/database.py`, add:

   - `list_meteorites_for_retention(*, states: List[str], older_than: str, limit: Optional[int] = None) -> List[Dict[str, Any]]`  
     Select rows where `state` ∈ `states` AND `state_changed_at < older_than` (ISO/UTC string comparable to stored timestamps). Order by `state_changed_at ASC`. Optional LIMIT.  
     Caller (AST-1562) passes `list(METEORITE_STATES_RETENTION["purge_states"])` or `stale_list_states` and a cutoff computed from config days — **this ticket does not hardcode day counts**.

   - `delete_meteorites_by_ids(ids: List[int]) -> int`  
     Delete rows with `id IN (…)`; return rowcount. Empty list → 0, no execute. Use parameterized placeholders only.

⚠️ **Decision:** Retention day thresholds stay out of `config.py` on this ticket (Scope: state registry / transition literals only). `METEORITE_STATES_RETENTION` holds **which states** purge vs list; AST-1562 adds day literals + runner that calls these helpers.

2. Do not add a dispatcher scheduled-query seed, retention task_key, or core runner in this ticket.

3. Compile both touched modules; fix only syntax/import issues introduced by this plan — no drive-by cleanup.

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that does not exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- Completes each stage on the epic worktree, commits, and publishes to `origin/sub/AST-1555/AST-1557-meteorite-table-claim-helpers` per build-child.

## Estimate

Confirm Chuckles estimate: 5 — agree
