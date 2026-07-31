<!-- linear-archive: AST-877 archived 2026-07-29 -->

## Linear archive (AST-877)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-877/originating-search-term-on-discovered-companies-foreign-key-search  
**Status at archive:** Archive  
**Project:** Astral Discovery  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-864 — Foreign key search term to company  
**Blocked by / blocks / related:** parent: AST-864

### Description

## What this implements

When Google CSE discovery creates a company from a hit, persist the originating search-term string on that company at record time. Carry the same string through any ingest path that creates a company from a Google search hit. Keep it on the company regardless of later ignore/reject/vet-failed outcomes. Expose it on existing company-readable surfaces for UAT (no new search-term UI). When discovery/ingest runs with debug enabled, include the originating search term in per-company working detail for newly recorded companies.

## Acceptance criteria

1. A company newly recorded from a Google CSE discovery hit has its originating search-term string stored on the company row.
2. A company that is later ignored/rejected/vet-failed (or otherwise discarded as a prospect) still retains that same originating search-term string.
3. Running discovery for a known search term and inspecting a resulting company (including an ignored outcome) shows that exact term as the stored origin.
4. With debug enabled on the discovery/ingest path, each newly recorded company's debug working detail includes the originating search term that was stored.
5. Companies created outside Google CSE discovery are unchanged (no false originating term required).
6. Existing discovery eligibility, CSE search, URL/slug dedupe, and vet transitions continue to behave as they do today aside from the new stored term.

## Boundaries

* Does not implement a true foreign key to company_search_terms (or search-term row ids) — denormalized string only.
* Does not add search-term child-record UI, metrics dashboards, or term-quality reporting (sibling AST-865).
* Does not change CSE query behavior, staleness/freq_hrs eligibility, dedupe rules, or company state machines except to stamp and retain the originating term.
* Does not backfill historical company rows.

## Notes for planning

* Primary surface: roster inflow discovery record/ingest and company row persistence (data-layer inventory update required for any new company column — ASTRAL_CODE_RULES §1.1).
* Backend debug contract: AST-538 / Code Rules §1.5.1 (index headers + `|` working detail when debug=True).
* Sibling AST-865 owns UI for search terms as child records — stay out of that scope.

## Git branch (authoritative)

Per orientation § Branch law: parent ftr/AST-864-foreign-key-search-term-to-company, child sub/AST-864/<child-id>-<slug>. Created at dispatch-parent.

### Comments

#### chuckles — 2026-07-12T21:52:01.401Z
[merge-child] blocked: validate-sub-log missing plan(AST-877): and resolve(AST-877): markers (have docs(AST-877): plan / docs(AST-877): resolution only).

@Hedy Lamarr — on origin/sub/AST-864/AST-877-originating-search-term add empty marker commits matching recent epics, e.g.:
- `plan(AST-877): sub-log marker — plan published as docs(AST-877) 5c45c1d`
- `resolve(AST-877): — clean; no fix-now`
then push origin HEAD:sub/AST-864/AST-877-originating-search-term. Do not git pull on sub.

— Chuckles

#### radia — 2026-07-12T21:37:01.066Z
**Diff:** `origin/dev...origin/sub/AST-864/AST-877-originating-search-term` @ `189f47b` (review doc @ `a6a4756`)

**What's solid:** Stages 1–3 match plan — nullable `company.originating_search_term` (CREATE+ALTER), `save_company` preserve-on-omit, excluded from `_UPDATE_COMPANY_ALLOWED`; CSE `(term, hit)` → `record_inflow_discovery_hit` / `ingest_new_companies`; §1.5.1 `debug_detail` under `if debug:`; New/Inactive/Ignored list shapes + read-only CompanyDetailModal row; §1.1 inventory; no AST-865 scope.

**Issues:** none

**Recommended:** none (ship) — 0 fix-now · 0 discuss · 0 advisory

Review doc: https://github.com/susansomerset/astral/blob/a6a47566c08ced2f4793fb94426a44af1b9084c1/docs/features/discovery/ast-877-originating-search-term-on-discovered-companies.md

#### betty — 2026-07-12T21:12:31.327Z
## QA test manifest — AST-877

**Publish:** `origin/sub/AST-864/AST-877-originating-search-term` @ `189f47b` (`merge-tests(AST-877): origin/tests 2cefda2e8c8c94455933124ad4a2385107138d59`)

1. **Column store + preserve + state update leaves term + non-CSE null** — `tests/component/data/database/test_companies.py::TestAst877OriginatingSearchTerm`
2. **Record/ingest stamp; retain after VET_FAILED; batch CSE term; debug detail** — `tests/component/core/test_roster.py::TestAst877OriginatingSearchTerm`
3. **New/Inactive/Ignored shapes include column; watch shapes omit** — `tests/component/utils/test_config.py::TestAst877OriginatingSearchTermShapes`
4. **Detail modal shows term / em dash; PUT excludes column** — `tests/component/frontend/components/test_CompanyDetailModal.test.tsx`

**Broken / obsolete (Betty revision):** `test_CompanyDetailModal.test.tsx` api mock — rewired via `pages/page-mocks` `installBaseApiMocks` (+ auth token/unauthorized exports).

**Narrowed run:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_companies.py::TestAst877OriginatingSearchTerm \
  tests/component/core/test_roster.py::TestAst877OriginatingSearchTerm \
  tests/component/utils/test_config.py::TestAst877OriginatingSearchTermShapes \
  -q
```

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_CompanyDetailModal.test.tsx
```

**Bible shasum:** `docs/test-bible/data/database/companies.md` `580848aadd5635f439d4e45b0f229c8b8de944bd`

— Betty

#### hedy — 2026-07-12T20:43:55.210Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-864/AST-877-originating-search-term/docs/features/discovery/ast-877-originating-search-term-on-discovered-companies.md

**Self-assessment**
- **Scope:** Single-Component — one nullable `company.originating_search_term` column, discovery/ingest stamp, debug detail, existing company list/detail surfaces.
- **Conf:** high — migrate + `save_company` preserve pattern and `record_inflow_discovery_hit` / CSE loop are established; term is a mechanical pass-through.
- **Risk:** Medium — `INSERT OR REPLACE` must preserve the column or later saves wipe origins; first-wins dedupe correctly owns the stored term.

---

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

## Radia review

**Diff:** `origin/dev...origin/sub/AST-864/AST-877-originating-search-term` @ `189f47b`

### What’s solid

- Plan stages 1–3 match the tip: nullable `company.originating_search_term` (CREATE + ALTER), `save_company` preserve-on-omit (same pattern as `candidate_id`), excluded from `_UPDATE_COMPANY_ALLOWED`.
- Discovery stamps via `(term, hit)` accumulator → `record_inflow_discovery_hit(..., search_term=term)` → `save_company`; `ingest_new_companies` accepts kwarg + `source_hit` fallback; empty/whitespace → `None`.
- §1.5.1: `log.debug_detail(f"originating_search_term={term!r}")` only under the existing `if debug:` hit loop (recorded and skipped).
- §2.1 / G1: list column only on `new_list` / `inactive_list` / `ignored`; CompanyDetailModal read-only Summary row; PUT body does not include the field.
- §1.1 inventory updated; no new tables; no AST-865 FK/UI; INSERT column/`?`/bind counts align. Self-Assessment Scope `Single-Component` matches the footprint.

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| — | — | None |

### Recommended actions

| Action | Item |
|--------|------|
| none (ship) | 0 fix-now · 0 discuss · 0 advisory |

**Outcome:** Clean — ready for `resolve-child`.

## Resolution

**2026-07-12 — Hedy / resolve-child**

Radia review clean (0 fix-now · 0 discuss · 0 advisory). No product delta. Publish tip already includes Radia’s `docs(AST-877): Radia review — clean` @ `a6a4756`.
