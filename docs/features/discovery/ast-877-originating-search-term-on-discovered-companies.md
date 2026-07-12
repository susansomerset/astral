# AST-877 — Originating search term on discovered companies (Foreign key search term to company)

- **Linear:** [AST-877](https://linear.app/astralcareermatch/issue/AST-877/originating-search-term-on-discovered-companies-foreign-key-search)
- **Parent:** [AST-864](https://linear.app/astralcareermatch/issue/AST-864/foreign-key-search-term-to-company)
- **Publish ref:** `origin/sub/AST-864/AST-877-originating-search-term`

When Google CSE discovery records a company from a hit, persist the **exact search-term string** that produced that hit on the company row as a denormalized nullable column. Carry the same string through every Google-hit ingest path. Retain it across later vet/prefilter ignore/reject outcomes. Expose it on existing company list/detail surfaces for UAT. When discovery runs with `debug=True`, include the stored term in per-hit working detail. No true FK to `company_search_terms`, no search-term management UI (AST-865), no historical backfill.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add nullable `originating_search_term` on `company`; migrate existing DBs; preserve through `save_company` INSERT OR REPLACE; header inventory note | data |
| `src/core/roster.py` | Stamp term through CSE→record path; pass into `record_inflow_discovery_hit` / `ingest_new_companies`; debug working detail | core |
| `src/utils/config.py` | Add `originating_search_term` column to companies list shapes (`new_list`, `inactive_list`, `ignored`) | utils |
| `src/ui/frontend/src/components/CompanyDetailModal.tsx` | Read-only Summary row for originating search term | ui |

**Out of scope:** `company_search_terms` FK/UI (AST-865); CSE query/eligibility/dedupe/state-machine changes; CSV import stamping a term; backfill of existing rows; new API routes.

## Stage 1: Company column + save preservation

**Done when:** Fresh and existing SQLite DBs have nullable `company.originating_search_term`. `save_company` can set it on insert and **preserves** it on later INSERT OR REPLACE when the caller omits it (same pattern as `candidate_id` / `last_scan_at`). `get_company` / `list_companies` return it via `SELECT *`. Vet/ignore transitions via `update_company(state=…)` leave the column untouched.

1. In `src/data/database.py` header inventory, extend the `company` bullet to mention `originating_search_term` (nullable TEXT; denormalized CSE discovery origin string; AST-877). Do **not** invent a new table.

2. In `_ensure_company_schema`, add `originating_search_term TEXT` to the `CREATE TABLE company` column list after `state_updated_at` (`candidate_id` stays a separate `_ensure_company_candidate_fk` migration — do not move it into CREATE in this ticket).

3. In the existing-table migration branch of `_ensure_company_schema` (the `PRAGMA table_info` / `cols` block), after the other `ALTER TABLE` migrations, add:
   ```python
   if "originating_search_term" not in cols:
       try:
           conn.execute("ALTER TABLE company ADD COLUMN originating_search_term TEXT")
           conn.commit()
       except sqlite3.OperationalError as e:
           if "duplicate column name" not in str(e).lower():
               raise
   ```
   No backfill UPDATE.

4. Do **not** add `originating_search_term` to `_UPDATE_COMPANY_ALLOWED`. Creation is via `save_company` only; UI PUT must not overwrite the origin string.

5. Update `save_company`:
   - Add keyword arg `originating_search_term: Optional[str] = None`.
   - When reading the existing row before INSERT OR REPLACE, also SELECT `originating_search_term`.
   - Resolve value:
     - if caller passed `originating_search_term is not None` → use that string (allow `""` only if explicitly passed; discovery will pass the real term);
     - else if existing row → preserve existing value;
     - else → `None`.
   - Include `originating_search_term` in the `INSERT OR REPLACE INTO company (…)` column list and VALUES placeholders (same COALESCE/`created_at` pattern as today for other preserved fields).

⚠️ **Decision:** Column name is `originating_search_term` (matches ticket language). Nullable denormalized string — not a FK to `company_search_terms.search_term` / row id.

⚠️ **Decision:** Exclude from `_UPDATE_COMPANY_ALLOWED` so `transition_company_state` / roster `_save_company` / company edit PUT cannot clear or rewrite the origin.

## Stage 2: Stamp term on discovery record + ingest paths

**Done when:** Every company created by `record_inflow_discovery_hit` from `run_inflow_discovery_batch` has `originating_search_term` equal to the stale search-term string whose CSE response produced the kept hit. Cross-term URL dedupe still keeps the **first** hit; that hit’s term is the stored origin. `ingest_new_companies` accepts and persists the same field when provided. CSV/`save_company` callers that omit the arg leave `NULL` (AC #5).

1. In `src/core/roster.py` `run_inflow_discovery_batch`, change the post-CSE accumulator so each kept hit retains its term:
   - Replace `all_hits: List[GoogleCseHit] = []` with `all_hits: List[Tuple[str, GoogleCseHit]] = []` (import `Tuple` already present).
   - Where hits are appended after URL dedupe, append `(term, hit)` instead of `hit` alone.
   - Update the record loop to unpack `(term, hit)` and call:
     ```python
     ok, outcome = record_inflow_discovery_hit(
         candidate_id, hit, index=hit_i, search_term=term,
     )
     ```
   - Do not change CSE call args, `seen_urls` dedupe, `update_company_search_term_last_scan_at`, or return counts.

2. Update `record_inflow_discovery_hit(candidate_id, hit, *, index=0, search_term: str = "") -> Tuple[bool, str]`:
   - After slug resolution succeeds, call `save_company(..., originating_search_term=(search_term or None))` — pass the stripped non-empty term string when present; if `search_term` is empty/whitespace-only, pass `None` (do not invent a placeholder).
   - Keep existing `save_company_data` blurb/notes write unchanged.
   - Outcome string on success: include the term when present, e.g. `recorded NEW slug={slug} term={search_term!r}` (or omit `term=` when empty).

3. Update `ingest_new_companies`:
   - Add keyword arg `originating_search_term: Optional[str] = None`.
   - If `originating_search_term` is None and `source_hit` is a dict, also accept `source_hit.get("originating_search_term")` or `source_hit.get("search_term")` as fallback (strip; empty → None).
   - Pass the resolved value into `save_company(..., originating_search_term=…)`.
   - Do not change dedupe / state (`NEW` vs `WEBSITE_FOUND`) / notes behavior.

⚠️ **Decision:** Prefer `(term, hit)` tuples over mutating `GoogleCseHit` (TypedDict is fixed to title/url/snippet). Keeps external CSE types clean.

⚠️ **Decision:** First-wins URL dedupe implies first-wins originating term — same hit identity as today.

## Stage 3: Debug detail + UAT surfaces

**Done when:** With `debug=True` on discovery, each newly recorded company’s per-hit working detail includes the originating search term that was stored. Company detail modal shows a read-only Originating Search Term row. New List / Inactive / Ignored list shapes include the column so Susan can scan without opening every row. No new routes or search-term management UI.

1. In `run_inflow_discovery_batch` hit loop, when `debug` and after `debug_index` / existing title/url `debug_detail`, add:
   ```python
   log.debug_detail(f"originating_search_term={term!r}")
   ```
   Emit this for every hit index (recorded and skipped) so the term that owned the hit is visible even when the outcome is skip. Do not emit when `debug=False`.

2. In `src/utils/config.py` under the companies list shapes (`STATE_UI` / shapes block that defines `new_list` / `inactive_list` / `ignored`), add after `short_name` (or after `company_name` if that reads cleaner with existing order — **place after `short_name`**):
   ```python
   {"key": "originating_search_term", "label": "Originating Search Term", "sortable": True},
   ```
   to **`new_list`**, **`inactive_list`**, and **`ignored`** only. Do **not** add to `watch_list` or `watch_history`.

3. In `src/ui/frontend/src/components/CompanyDetailModal.tsx` `SummaryTab`, after the Short Name row (or after State), add a read-only `DetailRow`:
   - Label: `Originating Search Term`
   - Value: `data.originating_search_term` when truthy, else `—`
   - Never include in the editable `form` / PUT body.

⚠️ **Decision:** List-shape exposure is limited to pipeline/ignore views where discovery outcomes are inspected during UAT; Watch List stays unchanged.

## Self-Assessment

**Scope:** `Single-Component` — one new nullable company column plus the discovery record/ingest stamp, debug detail, and existing company list/detail surfaces; no new modules or state machine keys.

**Conf:** `high` — schema migrate + `save_company` preserve pattern and `record_inflow_discovery_hit` / `run_inflow_discovery_batch` are established; term association is a mechanical pass-through of the CSE loop variable.

**Risk:** `Medium` — `INSERT OR REPLACE` must preserve the column or every later `save_company` wipe would erase origins; wrong term-on-dedupe association would mis-attribute quality signals, but state transitions themselves are safe via partial `update_company`.

## Rules check (§8)

- **§1.1:** New column only on inventoried `company` table; header updated; no new tables.
- **§1.3 DRY:** Single stamp site in `record_inflow_discovery_hit` / `ingest_new_companies`; discovery loop only supplies the term.
- **§1.5.1:** Debug line gated on `debug=True`; uses existing `debug_detail` under Style D index headers.
- **§2.1:** No new config behavior keys; list shapes only.
- **§2.4 / §2.6:** No batch-claim or state-machine changes.
- **§3.3:** No new layer imports; roster continues to call data `save_company`.

## Review stub (Hedy / build)

**Publish ref:** `origin/sub/AST-864/AST-877-originating-search-term`  
**Product tip:** `3f14381` — `4508696` (column + save preserve) + `4fde7bc` (stamp through discovery/ingest + debug detail) + `3f14381` (list shapes + detail modal)

**Built:** Nullable `company.originating_search_term`; discovery CSE loop keeps `(term, hit)` and stamps via `record_inflow_discovery_hit` / `ingest_new_companies`; debug `originating_search_term=` working detail; New/Inactive/Ignored list columns + CompanyDetailModal read-only row.
