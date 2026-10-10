# AST-2131 — telescope_data table and config

**Parent:** [AST-2130 — Create a new table telescope_data](https://linear.app/astralcareermatch/issue/AST-2130)
**Ticket:** [AST-2131](https://linear.app/astralcareermatch/issue/AST-2131)
**Publish ref:** `origin/sub/AST-2130/AST-2131-telescope-data-table`

Ships the storage half of the epic: a `telescope_data` table in `astral.db` (uuid row id, `candidate_id`, `url`, free-text `data_type`, compressed `content`, `created_at`), its idempotent schema-ensure wired into the bootstrap registry, a save function that returns the new row id, and read-by-id(s) functions that return plain content. Config gains the content-type key names, the list of `company_data` keys that will hold row ids, and the job-data key for the scraped-JD reference. Nothing calls the new functions yet — gazer (AST-2132), JD composition (AST-2133), roster (AST-2134) and the data move (AST-2135) consume them.

## Scope check

Every row below is named in this ticket's `## Scope`: `src/data/database.py` (table, index, save, read by id / ids, schema-ensure + registry, header inventory) and `src/utils/config.py` (content-type block, id-holding company keys + assert, `TRACKER_CONFIG["job_data_keys"]` entry). No other files.

## Canon

`stat.logging.debug`, `stat.logging.warning`, `stat.logging.error`. Binding consequence for this ticket: **`src/data/` does not log.** The new data functions raise on bad input / DB errors and never call a logger; `config.py` changes are constants + asserts only. No log lines are added anywhere in this ticket.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Header inventory line; `_ensure_telescope_data_schema` + flag; registry entry; `save_telescope_data`, `get_telescope_data_for_ids`, `get_telescope_data` | data |
| `src/utils/config.py` | Docstring section line; `TELESCOPE_DATA_CONFIG` block + assert; `TRACKER_CONFIG["job_data_keys"]["jd_telescope_data_id"]` | utils |

## Stage 0: Drift check (no commit)

**Done when:** every `database.py` symbol below is confirmed present with the described behavior, or the builder has stopped and commented.

The `database.py` symbols this plan mirrors were taken from the AST-843 and AST-977 plan docs (the planner's read tool was blocked on `database.py`). Before editing, confirm in `src/data/database.py`:

1. `_get_connection()` returns a sqlite3 connection.
2. `_compress_payload(plain: str)` and `_decompress_payload(blob)` exist and are what `save_agent_data` / `get_agent_data` use for `agent_data.block_data`.
3. `_ensure_agent_data_schema(conn)` exists and is guarded by a module-level `_agent_data_schema_ensured` flag.
4. `_UPSERT_LAZY_SCHEMA_HANDLERS` is a dict keyed by table name, and `ensure_table_schema_for_upsert(conn, table)` resets the per-table `_*_schema_ensured` flag before calling the handler.
5. `get_agent_data_for_ids(ids)` exists and returns a dict keyed by `agent_data_id`.
6. The module docstring carries a per-table inventory that includes an `agent_data` bullet.

If any item does not hold, **stop** and post the 🛑 comment on AST-2130 (format in build-child). Do not adapt.

## Stage 1: `telescope_data` table, schema-ensure, registry, inventory

**Done when:** on a fresh temp DB and on an existing `astral.db`, `ensure_all_upsert_registry_schemas_at_startup()` creates `telescope_data` and its index; running it again is a no-op; `sqlite3 <db> ".schema telescope_data"` shows `telescope_data_id`, `candidate_id`, `url`, `data_type`, `content`, `created_at` (AC 1).

1. In the `src/data/database.py` module docstring inventory, directly after the `agent_data` bullet, add one bullet in the same style:
   `telescope_data — scraped Telescope content, one row per capture (telescope_data_id uuid PK, candidate_id, url, data_type free text e.g. VISIBLE_TEXT / PAGE_LINKS, content zlib-compressed like agent_data.block_data, created_at); index (candidate_id, created_at). Owned by gazer (AST-2130).`
2. Directly after `_ensure_agent_data_schema`, add a module-level flag `_telescope_data_schema_ensured = False` (place it beside `_agent_data_schema_ensured` if the flags are grouped elsewhere) and a function `_ensure_telescope_data_schema(conn)` that mirrors `_ensure_agent_data_schema`'s flag-guard / commit shape and runs:
   ```sql
   CREATE TABLE IF NOT EXISTS telescope_data (
       telescope_data_id TEXT PRIMARY KEY,
       candidate_id TEXT,
       url TEXT,
       data_type TEXT NOT NULL,
       content BLOB NOT NULL,
       created_at TIMESTAMP NOT NULL
   );
   CREATE INDEX IF NOT EXISTS idx_telescope_data_candidate_created
       ON telescope_data (candidate_id, created_at);
   ```
   No ALTER/legacy-migration block — the table is new.
3. Add `"telescope_data": _ensure_telescope_data_schema` to `_UPSERT_LAZY_SCHEMA_HANDLERS`, keeping the dict's existing ordering convention. If `ensure_table_schema_for_upsert` resets flags through an explicit per-table map or branch, add the `telescope_data` → `_telescope_data_schema_ensured` entry there in the same shape as `agent_data`.
4. `python3 -m py_compile src/data/database.py`.

⚠️ **Decision:** Primary key column is `telescope_data_id` (parallels `agent_data_id`); value is `str(uuid.uuid4())` generated in `save_telescope_data`.

⚠️ **Decision:** `candidate_id` and `url` are nullable. Every pipeline caller will pass both, but AST-2135's export of legacy companies must not fail on a company row that predates `company.candidate_id`. `data_type` and `content` are `NOT NULL`.

⚠️ **Decision:** No foreign key on `candidate_id` — rows outlive / precede entity edits and are culled by plain SQL (parent Purpose).

## Stage 2: save and read functions

**Done when:** `save_telescope_data(...)` returns a uuid string and inserts exactly one row; saving with `data_type="JSON"` succeeds and `SELECT data_type FROM telescope_data WHERE telescope_data_id=?` returns `JSON` (AC 2); `get_telescope_data(id)` returns the original string; `get_telescope_data_for_ids([id, "missing"])` returns `{id: <content>}` only; `get_telescope_data("missing")` returns `None`.

1. If `uuid` is not already imported at the top of `src/data/database.py`, add `import uuid` to the stdlib import group.
2. Directly after `get_agent_data_for_ids` (keep telescope functions together, in this order), add:
   ```python
   def save_telescope_data(candidate_id, url, data_type, content):
       """Insert one telescope_data row and return its new telescope_data_id.

       data_type is free text — deliberately no allow-list (new content types
       need no code gate). content is plain text; compressed at rest."""
   ```
   Body: `conn = _get_connection()`; `try:` `_ensure_telescope_data_schema(conn)`; `new_id = str(uuid.uuid4())`; `INSERT INTO telescope_data (telescope_data_id, candidate_id, url, data_type, content, created_at) VALUES (?, ?, ?, ?, ?, ?)` with `_compress_payload(content)` and `_utc_now()` (same timestamp source `save_agent_data` uses); `conn.commit()`; `return new_id`; `finally: conn.close()`. No `try/except`, no logging — errors propagate.
3. Add:
   ```python
   def get_telescope_data_for_ids(telescope_data_ids):
       """Return {telescope_data_id: plain content} for the ids that exist; missing ids are omitted."""
   ```
   Body: return `{}` immediately for an empty input. Otherwise open/ensure as above, `SELECT telescope_data_id, content FROM telescope_data WHERE telescope_data_id IN (<one ? per id>)`, build `{row[0]: _decompress_payload(row[1])}`, close in `finally`. No chunking / limit on the id list.
4. Add:
   ```python
   def get_telescope_data(telescope_data_id):
       """Return plain content for one row, or None if the row does not exist."""
       return get_telescope_data_for_ids([telescope_data_id]).get(telescope_data_id)
   ```
5. `python3 -m py_compile src/data/database.py`.
6. Manual check (scratch script under `debug/spikes/AST-2131/`, not committed): point `ASTRAL_DB_DIR` at a temp dir, call `ensure_all_upsert_registry_schemas_at_startup()` twice, save `("cand", "https://x", "JSON", '{"a":1}')`, verify the Stage 1 and Stage 2 "Done when" lines; repeat the ensure step once against a copy of the local `data/astral.db`.

⚠️ **Decision:** `None` on a missing single id (not raise). Parent AC 11 requires a deleted row to fall back to the coat-check fetch rather than raise; that decision belongs to gazer/roster callers, so the data layer just reports absence.

⚠️ **Decision:** `content` is `str`. PAGE_LINKS serialization (e.g. `json.dumps` of the link list) is the caller's job (AST-2132), consistent with `agent_data` storing plain text.

## Stage 3: config

**Done when:** `python3 -c "import src.utils.config as c; print(c.TELESCOPE_DATA_CONFIG, c.TRACKER_CONFIG['job_data_keys'])"` prints the new block and key, and importing config still succeeds (the new assert passes).

1. In the `src/utils/config.py` module docstring "Config sections" list, after the `ROSTER_CONFIG` line, add:
   `  TELESCOPE_DATA_CONFIG — telescope_data content-type keys + company_data keys that hold telescope row ids (AST-2131)`
2. Directly after the `roster_scrape_readiness_config` function (i.e. after `ROSTER_CONFIG` is defined, before the `INFLOW_CONFIG` comment block), add:
   ```python
   # AST-2131: scraped Telescope content lives in telescope_data (owned by gazer); entity blobs hold row ids.
   TELESCOPE_DATA_CONFIG = {
       # data_type values written to telescope_data.data_type — free text, not validated in code.
       "data_types": {
           "VISIBLE_TEXT": "VISIBLE_TEXT",
           "PAGE_LINKS": "PAGE_LINKS",
           "DOM_CONTENT": "DOM_CONTENT",  # reserved name only — DOM is not stored
       },
       # company_data keys whose values are telescope row ids (or [{url, id}] for multi-page keys).
       "company_data_id_keys": (
           "homepage_text",
           "nav_links",
           "website_content",
           "job_list_visible",
           "pjl_scrape_pages",
       ),
   }
   # Each id-holding key must still be a declared company_data key.
   assert all(
       k in ROSTER_CONFIG["company_data_keys"] for k in TELESCOPE_DATA_CONFIG["company_data_id_keys"]
   ), TELESCOPE_DATA_CONFIG["company_data_id_keys"]
   ```
3. In `TRACKER_CONFIG["job_data_keys"]`, after the `job_description` entry, add:
   ```python
   "jd_telescope_data_id": "jd_telescope_data_id",  # AST-2130: telescope_data row id of the scraped JD; no coat-check handler
   ```
4. `python3 -m py_compile src/utils/config.py` and the import check in **Done when**.

⚠️ **Decision:** Block name `TELESCOPE_DATA_CONFIG` (matches the table name) and job key `jd_telescope_data_id`. Siblings AST-2132 / AST-2133 / AST-2134 read these names; changing them later is a cross-ticket edit.

⚠️ **Decision:** `data_types` is a dict keyed by the type id (same id→value shape as `company_data_keys`), so callers index `TELESCOPE_DATA_CONFIG["data_types"]["VISIBLE_TEXT"]`.

## Lint / compile gate (every stage commit)

- `python3 -m py_compile src/data/database.py src/utils/config.py`
- `ruff check src/data/database.py src/utils/config.py` — finding count must not exceed the count on `origin/dev` for the same files (record the baseline once before Stage 1). Fix any new finding in lines this ticket touched; do not clean up pre-existing findings.

## Boundaries

No gazer functions or callers (AST-2132), no JD composition (AST-2133), no roster / admin paths (AST-2134), no data move (AST-2135). No tests or bible edits (Betty).

## Estimate

Confirm Chuckles estimate: 3 — revise to 2 because this is a known pattern (mirror `agent_data` schema-ensure + compressed save/read) across two files with no callers yet.

Gap to flag: the planner's read tool was blocked on `src/data/database.py` (reported as `.cursorignore` / permission denied; no matching ignore rule found in the repo). Stage 0 exists for that reason. If the builder hits the same block, Susan must lift it before build-child.

## Joan validate

[plan-rubric]
**Ticket:** AST-2131
**Overall:** APPROVED
**Corpus:** 26c4e86a4d08addcefdbc3be68116703fedf6762 (canon tree at publish tip; `docs/canon-index.md` absent on ref)
**Publish ref:** `origin/sub/AST-2130/AST-2131-telescope-data-table` @ `0f16fb099035705e9f58e1fc4c7e56b9c4b1aac3`

## Canon scores

stat.logging.debug | A |
stat.logging.warning | A |
stat.logging.error | A |

## Traceability

AC1 → Stage 1 (schema-ensure, registry, inventory, `.schema telescope_data`); AC2 → Stage 2 (`save_telescope_data` + manual scratch verify); ticket Scope config slice → Stage 3 (`TELESCOPE_DATA_CONFIG`, assert, `jd_telescope_data_id`); parent epic AC3–11 N/A (this child Boundaries).

### acceptable — Stage 0 mirror wording vs `get_agent_data_for_ids`

- **Location:** Stage 0 item 5.
- **Finding:** Checklist says the symbol returns a dict keyed by id; live `get_agent_data_for_ids` returns `{agent_data_id: row_dict}` with resolved `block_data`, not plain string content. Stage 2 correctly targets plain content for telescope reads.
- **Recommendation:** Builder uses Stage 0 only to confirm symbol presence and compression/schema patterns; no plan rewrite required.

### acceptable — No `## Self-assessment` block

- **Location:** Plan structure (`## Estimate` confirm only).
- **Finding:** R6 self-assessment axes are implicit; work is a documented `agent_data` mirror across two files with Stage 0 drift gate for the planner’s `database.py` read block.
- **Recommendation:** Optional self-assessment for parity with larger tickets; not blocking.

### discuss — Canon Scope vs config/registry statutes

- **Location:** Ticket Citations (three `stat.logging.*` only) vs Stage 3 `TELESCOPE_DATA_CONFIG` / `TRACKER_CONFIG` keys.
- **Finding:** New named keys and id lists in `config.py` align with parent Technical scope and registry-not-literals intent, but no `config.config-source-of-truth` / `stat.general.registry-not-literals` on the frozen child list.
- **Recommendation:** Archie may amend parent Canon Scope on a future child if explicit config statutes should be scored; do not widen AST-2131’s list in flight.

**R6 (summary):** Definition fidelity matches child `## Scope` and Boundaries (no gazer, roster, migration). Files Changed ⊆ ticket Scope. Stage 0 matches live `database.py` (`_compress_payload`, `_decompress_payload`, `_UPSERT_LAZY_SCHEMA_HANDLERS`, `_UPSERT_SCHEMA_ENSURE_FLAGS`, `_ensure_agent_data_schema`, `ensure_all_upsert_registry_schemas_at_startup`). DRY: explicit mirror of `agent_data` lazy ensure + compressed blob I/O. No sibling creep. No `fix-now` gaps.

## Revisions

Revision 1 — 2026-10-10
Driven by: Ada's build-child Stage 2 stop on AST-2130 (`created_at` "column default" vs live `agent_data.created_at TIMESTAMP NOT NULL` with no DEFAULT); Chuckles decision: option 1.
Changes: Stage 1 step 2 — `created_at TIMESTAMP NOT NULL` written out (mirrors `agent_data`; no DEFAULT). Stage 2 step 2 — `save_telescope_data` INSERT now lists `created_at` and passes `_utc_now()`, same timestamp source as `save_agent_data`; removed "take the column default".

## Joan validate (Revision 1)

[plan-rubric]
**Ticket:** AST-2131
**Overall:** APPROVED
**Corpus:** 26c4e86a4d08addcefdbc3be68116703fedf6762 (canon tree at `1f7bae1`; `docs/canon-index.md` absent on ref)
**Publish ref:** `origin/sub/AST-2130/AST-2131-telescope-data-table` @ `1f7bae1c4afe4e3016576bc7640ed2f9109a1f06`

## Canon scores

stat.logging.debug | A |
stat.logging.warning | A |
stat.logging.error | A |

## Traceability

AC1 → Stage 1 (`created_at TIMESTAMP NOT NULL` in DDL, registry, inventory, `.schema telescope_data`); AC2 → Stage 2 (`save_telescope_data` + `_utc_now()` on INSERT, manual scratch verify); ticket Scope config slice → Stage 3; parent epic AC3–11 N/A (Boundaries).

### acceptable — Revision 1 closes `created_at` drift

- **Location:** `## Revisions` Revision 1; Stage 1 step 2; Stage 2 step 2.
- **Finding:** Prior plan text implied column default on `created_at`; live `agent_data` uses `TIMESTAMP NOT NULL` with no DEFAULT and `save_agent_data` sets `ts = created_at or _utc_now()`. Revision 1 aligns telescope DDL and INSERT with that pattern.
- **Recommendation:** None; builder may proceed past the reported Stage 2 stop.

### acceptable — Stage 0 mirror wording vs `get_agent_data_for_ids`

- **Location:** Stage 0 item 5.
- **Finding:** Checklist is about symbol presence; return shape is row dicts, not plain content — Stage 2 still correctly specifies plain content for telescope reads.
- **Recommendation:** Use Stage 0 for mirror patterns only.

### acceptable — No `## Self-assessment` block

- **Location:** Plan structure.
- **Finding:** Complexity is implicit (`agent_data` mirror + Stage 0 drift gate); not blocking.

### discuss — Canon Scope vs config/registry statutes

- **Location:** Citations vs Stage 3.
- **Finding:** `TELESCOPE_DATA_CONFIG` / `jd_telescope_data_id` match parent Technical scope; frozen list is logging-only — no config/registry directive ids to score.
- **Recommendation:** Parent Canon Scope amendment only if Archie wants those scored on a later child; do not widen AST-2131’s list in flight.

**R6 (summary):** Revision 1 is definition-faithful and fixes the only substantive plan/code mismatch raised at build. Scope, Boundaries, and DRY mirror unchanged. No `fix-now` gaps.

context_tokens≈38000
