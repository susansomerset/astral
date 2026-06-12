# AST-524 — Company search terms table and sync

- **Linear:** [AST-524](https://linear.app/astralcareermatch/issue/AST-524/company-search-terms-table-and-sync-company-search-terms-table-with)
- **Parent (coordination only):** [AST-523](https://linear.app/astralcareermatch/issue/AST-523/company-search-terms-table-with-per-term-last-scan-at-roster-inflow)
- **Publish ref:** `origin/sub/AST-523/AST-524-company-search-terms-table-and-sync`
- **Blocked by:** none (first child in epic split)
- **Blocks:** [AST-525](https://linear.app/astralcareermatch/issue/AST-525/per-term-inflow-discovery-cadence-company-search-terms-table-with-per), [AST-526](https://linear.app/astralcareermatch/issue/AST-526/artifacts-ui-and-api-for-search-terms-table-company-search-terms-table)

## Summary

Replace the Phase 0 **artifact blob** (`candidate_data.artifacts.company_search_terms`) as the **source of truth** for discovery search terms with a **`company_search_terms`** SQLite table: one row per candidate per trimmed term, each row carrying nullable **`last_scan_at`**. Ship **upsert-and-delete sync** from a newline-delimited line list (same normalization rules as AST-504), a **one-time migration** from legacy artifact strings, and **core + REST sync** helpers. **Does not** change Artifacts UI (**AST-526**) or inflow discovery cadence (**AST-525**). After sync, **stop persisting** `artifacts.company_search_terms` on save.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Header inventory; `_ensure_company_search_terms_table`; CRUD/sync/migrate helpers | data |
| `src/core/candidate.py` | Table-backed `company_search_terms_lines`, `company_search_terms_joined_text`; sync wrapper; save hook helper | core |
| `src/ui/api/api_candidate.py` | `PUT …/company_search_terms/sync` endpoint; call sync on existing `PUT …/data` when terms present | ui |
| `src/utils/config.py` | Comment on `TOKEN_SOURCES["COMPANY_SEARCH_TERMS"]` — path unchanged; **AST-525** retargets resolution at runtime | utils |

**Tests:** Betty owns **`tests/`** and **`ASTRAL_TEST_BIBLE.md`** — engineer does **not** add test files in **build-astral** unless Betty’s manifest already lists them.

## Stage 1: Schema, inventory, and data-layer helpers

**Done when:** Table exists with correct columns; migration imports legacy artifact strings once per candidate; `sync_company_search_terms`, `list_company_search_terms`, and `update_company_search_term_last_scan_at` work in isolation (manual SQLite / REPL).

1. In **`src/data/database.py`** header inventory (after **`board_search_run`** bullet), add:

   ```
   - company_search_terms — Per-candidate Google discovery queries (candidate_id, search_term TEXT, nullable last_scan_at,
     created_at, updated_at). Composite PRIMARY KEY (candidate_id, search_term). Source of truth for discovery terms (AST-524).
   ```

2. Add module-level guard `_company_search_terms_schema_ensured = False` near other `_ensure_*` guards.

3. Implement **`_ensure_company_search_terms_table(conn: sqlite3.Connection) -> None`** following **`_ensure_board_search_table`** pattern:

   ```sql
   CREATE TABLE company_search_terms (
       candidate_id TEXT NOT NULL,
       search_term TEXT NOT NULL,
       last_scan_at TIMESTAMP,
       created_at TIMESTAMP NOT NULL,
       updated_at TIMESTAMP NOT NULL,
       PRIMARY KEY (candidate_id, search_term)
   );
   ```

   - Create index **`idx_company_search_terms_candidate`** on **`(candidate_id)`** for list/count queries.
   - On first ensure after create, call **`_migrate_company_search_terms_from_artifacts(conn)`** once per process (set flag after migration sweep).

4. Implement **`_migrate_company_search_terms_from_artifacts(conn)`**:
   - **`SELECT astral_candidate_id, candidate_data FROM candidate`** (reuse existing list/get patterns; skip **`DELETED`** if list helper filters — migration may use raw SQL).
   - For each row, parse **`candidate_data` JSON**; read **`artifacts.company_search_terms`** string.
   - If string is non-empty after strip **and** **`SELECT COUNT(*) … WHERE candidate_id = ?` == 0**, call internal sync with normalized lines (same split/strip/drop-empty as **`_company_search_terms_lines_from_string`** — duplicate small helper in data layer; do **not** import **`src.core.candidate`**).
   - **Do not** delete artifact field during migration (read-only import).

5. Implement **`list_company_search_terms(candidate_id: str) -> List[Dict[str, Any]]`**:
   - Return rows ordered by **`search_term ASC`** with keys: **`search_term`**, **`last_scan_at`**, **`created_at`**, **`updated_at`**.
   - Empty list if **`candidate_id`** blank or no rows.

6. Implement **`sync_company_search_terms(candidate_id: str, terms: List[str]) -> None`** (upsert-and-delete):
   - Normalize input: strip each string, drop empties, **dedupe preserving first-seen order** (if duplicate lines in input, keep first).
   - **`DELETE FROM company_search_terms WHERE candidate_id = ? AND search_term NOT IN (...)`** — use parameterized placeholders; when **`terms`** empty after normalize, delete **all** rows for candidate (explicit clear).
   - For each term in final list, **`INSERT INTO company_search_terms (candidate_id, search_term, last_scan_at, created_at, updated_at) VALUES (?, ?, NULL, ?, ?) ON CONFLICT(candidate_id, search_term) DO UPDATE SET updated_at = excluded.updated_at`** — **do not** overwrite **`last_scan_at`** on conflict (preserve existing scan timestamp).
   - Set **`created_at`** only on insert (use **`excluded.created_at`** guard or subquery — on conflict, leave **`created_at`** unchanged).
   - Use **`_utc_now()`** for timestamps; wrap in **`_run_with_retry`**.

7. Implement **`update_company_search_term_last_scan_at(candidate_id: str, search_term: str) -> None`**:
   - Mirror **`update_board_search_last_scan_at`**: **`UPDATE company_search_terms SET last_scan_at = ? WHERE candidate_id = ? AND search_term = ?`** — update **`last_scan_at` only** (no **`updated_at`** bump; term text edits are user sync, scan cadence is separate).

8. Implement **`count_stale_company_search_terms(candidate_id: str, scan_interval_hours: float) -> int`** (used by **AST-525**; define here so table API is complete):
   - Return **0** if **`candidate_id`** blank or **`scan_interval_hours <= 0`**.
   - **`SELECT COUNT(*) FROM company_search_terms WHERE candidate_id = ? AND (last_scan_at IS NULL OR last_scan_at < datetime('now', '-' || ? || ' hours'))`**.

⚠️ **Decision:** Composite PK **`(candidate_id, search_term)`** — term text is the stable identity; renames are delete+insert (loses **`last_scan_at`**, acceptable for v1). Matches upsert-and-delete save contract.

⚠️ **Decision:** Data layer duplicates line-split helper (already mirrored as **`_candidate_search_term_lines`**) — **§3.3** forbids **`database → core`** imports.

### Self-review (Stage 1)

| Rule | OK? |
|------|-----|
| §1.1 table inventory | Header updated |
| §2.4 batch | N/A — not batch-claimed rows |
| §3.3 imports | Data-only; no core imports |

---

## Stage 2: Core helpers and save-path sync

**Done when:** `company_search_terms_lines` reads the table; saving terms via **`PUT /data`** or sync API updates table rows; artifact blob is **not** written on save; unchanged terms keep **`last_scan_at`**.

1. In **`src/core/candidate.py`**, add **`_normalize_search_term_lines(val: str) -> list[str]`** by renaming/reusing **`_company_search_terms_lines_from_string`** (keep existing name as alias or inline — single implementation).

2. Add table-backed helpers (**do not** change **`company_search_terms_lines(candidate_data)`** — **AST-525** retargets that function and roster call sites):

   - **`company_search_terms_lines_for_candidate(candidate_id: str) -> list[str]`** → **`[row["search_term"] for row in database.list_company_search_terms(candidate_id)]`**.
   - **`company_search_terms_joined_text(candidate_id: str) -> str`** → **`"\n".join(company_search_terms_lines_for_candidate(candidate_id))`**.
   - **`sync_company_search_terms_from_text(candidate_id: str, text: str) -> None`**: build throwaway **`{"company_search_terms": text}`**, call **`normalize_company_search_terms_on_save`**, then **`database.sync_company_search_terms(candidate_id, _company_search_terms_lines_from_string(normalized))`** using lines from normalized string in artifacts dict after normalize.

3. **`normalize_company_search_terms_on_save`**: **unchanged** validation (still used before sync).

4. Add **`apply_company_search_terms_save(candidate_id: str, artifacts: dict) -> None`**:
   - If **`"company_search_terms" not in artifacts`**, return.
   - Call **`normalize_company_search_terms_on_save(artifacts)`**.
   - Call **`sync_company_search_terms_from_text(candidate_id, artifacts["company_search_terms"])`**.
   - **`del artifacts["company_search_terms"]`** — stop writing artifact blob (table is source of truth).

5. In **`src/ui/api/api_candidate.py`** **`update_candidate_data`**:
   - Replace direct **`normalize_company_search_terms_on_save(arts)`** with **`apply_company_search_terms_save(candidate_id, arts)`** when **`arts`** is dict.

### Self-review (Stage 2)

| Rule | OK? |
|------|-----|
| §3.3 imports | **`api → core → data`** |
| §1.3 DRY | Single normalize + sync path |

---

## Stage 3: Dedicated sync REST endpoint

**Done when:** `PUT /api/candidates/<candidate_id>/company_search_terms/sync` accepts `{ "search_terms": "<multiline string>" }`, returns **200** with `{ "search_terms": "<joined canonical text>", "terms": ["line", ...] }`; **400** on validation errors.

1. In **`src/ui/api/api_candidate.py`**, add route:

   ```python
   @candidate_bp.route("/<candidate_id>/company_search_terms/sync", methods=["PUT"])
   @require_auth
   def sync_company_search_terms(candidate_id):
   ```

2. Body: **`{"search_terms": "<string>"}`** required.
3. Load candidate; **404** if missing.
4. Build **`artifacts = {"company_search_terms": body["search_terms"]}`**; call **`apply_company_search_terms_save(candidate_id, artifacts)`** inside try/except → **400** on **`ValueError`**.
5. Response JSON: **`search_terms`** = joined text from **`company_search_terms_joined_text(candidate_id)`**, **`terms`** = **`company_search_terms_lines_for_candidate(candidate_id)`**.

⚠️ **Decision:** **AST-526** may switch Artifacts UI to this endpoint or continue **`PUT /data`** — both hit the same **`apply_company_search_terms_save`** helper.

### Self-review (Stage 3)

| Rule | OK? |
|------|-----|
| §3.5 naming | snake_case URL segment matches artifact key |
| UI layer | JSON errors only |

---

## Stage 4: Config comment (no token retarget in this ticket)

**Done when:** `TOKEN_SOURCES` documents that runtime resolution moves to table in AST-525.

1. In **`src/utils/config.py`**, above **`COMPANY_SEARCH_TERMS`** entry, add one-line comment: `# AST-524 table is source of truth; AST-525 overlays token at do_task from table.`
2. **Do not** change **`path`** or **`resolve_tokens`** in this ticket.

---

## Execution contract (developer agent)

Execute stages **1 → 4** in order. One commit per stage on **`dev-hedy`**, then cherry-pick to **`origin/sub/AST-523/AST-524-company-search-terms-table-and-sync`**. Do **not** modify **`run_inflow_discovery_batch`**, **`count_candidate_inflow_discovery_eligible`**, Artifacts frontend, or **`TOKEN_SOURCES` path**. Blocking questions → parent **AST-523** with 🛑 format from **plan-astral**.

## Self-Assessment

**Scope:** `Single-Component` — Touches **`database.py`**, **`candidate.py`**, and **`api_candidate.py`** only; no discovery or UI pages.

**Conf:** `Medium` — Mirrors **`board_search`** table + **`last_scan_at`** patterns already in codebase; migration path is straightforward but upsert SQL must preserve timestamps exactly.

**Risk:** `Medium` — Bad sync/migration could drop terms or reset **`last_scan_at`**; contained to roster inflow data, not job/consult paths.

## Self-review vs ASTRAL_CODE_RULES

| Section | Assessment |
|---------|------------|
| §1.3 DRY | Shared normalize + sync; data-layer line split mirrors existing **`_candidate_search_term_lines`** |
| §2.1 config | No new config literals; scan interval deferred to AST-525 |
| §2.4 batch | Table rows are not batch-claimed |
| §2.6 state machine | No state transitions |
| §3.3 imports | Respected |
| §3.5 naming | snake_case table/columns/API |

## Review

- **Branch:** `origin/sub/AST-523/AST-524-company-search-terms-table-and-sync`
- **Tip:** `616bb428`
- **Built:** 2026-05-28 — stages 1–4 complete; Betty manifest pending.

## Resolution

- **2026-05-28 (Radia review):** No **fix-now** or **discuss** items. **Advisory:** migration sweep includes all `candidate` rows (no `DELETED` filter) — intentional for one-time artifact import; table sync on save uses normal candidate paths.
- **Outcome:** No product changes at resolve; publish ref unchanged aside from Resolution doc commit.
