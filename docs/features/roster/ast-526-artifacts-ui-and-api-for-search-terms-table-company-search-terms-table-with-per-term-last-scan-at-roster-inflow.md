# AST-526 — Artifacts UI and API for search terms table (Company search terms table with per-term last_scan_at (Roster inflow))

- **Linear:** [AST-526](https://linear.app/astralcareermatch/issue/AST-526/artifacts-ui-and-api-for-search-terms-table-company-search-terms-table)
- **Parent (coordination only):** [AST-523](https://linear.app/astralcareermatch/issue/AST-523/company-search-terms-table-with-per-term-last-scan-at-roster-inflow)
- **Publish ref:** `origin/sub/AST-523/AST-526-artifacts-ui-and-api-for-search-terms-table`
- **Blocked by:** [AST-524](https://linear.app/astralcareermatch/issue/AST-524/company-search-terms-table-and-sync-company-search-terms-table-with) (table + sync helpers — **must be on `origin/dev` or merged into `dev-kath` before build-astral Stage 1**)

## Summary

Retarget the existing **Company Search Terms** Artifacts page and **`api_candidate`** save/load paths so the textarea reads and writes the **`company_search_terms`** table (via **AST-524** core helpers) instead of persisting **`artifacts.company_search_terms`**. UX stays identical: one textarea, one term per line, Generate/Regenerate/Cancel, 2s autosave. Saving performs upsert-and-delete sync so removed lines delete rows and unchanged terms keep **`last_scan_at`**. No schema, migration, discovery, or token changes in this ticket.

## AST-524 dependency contract (read-only — do not implement here)

**build-astral must stop with a Linear comment on AST-523** if any of these symbols are missing or renamed on **`dev-kath`** after merging **`origin/dev`** and **AST-524** publish ref.

| Symbol | Module | Contract |
|--------|--------|----------|
| `parse_company_search_terms_text(text: str) -> list[str]` | `src/core/candidate.py` | Require `str`; split on `\n`, strip each line, drop empties; if result empty, raise `ValueError` with message containing **`non-empty search term`** (same user-facing contract as today). |
| `sync_company_search_terms(candidate_id: str, terms: list[str]) -> None` | `src/core/candidate.py` | Upsert one row per term; delete rows for terms not in `terms`; **preserve `last_scan_at`** on rows whose term text is unchanged. |
| `company_search_terms_text(candidate_id: str) -> str` | `src/core/candidate.py` | Return newline-joined term text from table (stable order — use AST-524’s table read order, typically `term ASC` or `rowid ASC`). Empty string if no rows. |

⚠️ **Decision:** UI/API use the **existing PUT body shape** `{ artifacts: { company_search_terms: "<text>" } }` so autosave and Generate→Save flows need no route changes. **`api_candidate`** intercepts that key, syncs the table, and **strips** it before **`save_candidate_data`** — the artifact blob is never written on save.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_candidate.py` | Inject table text on GET detail; intercept PUT `artifacts.company_search_terms` → sync + strip blob | ui |
| `src/ui/frontend/src/pages/ArtifactsCompanySearchTerms.tsx` | Load from top-level `company_search_terms` on GET response | ui |
| `tests/component/ui/api/test_api_candidate.py` | Assert sync path: sync called, blob not persisted | tests |
| `tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx` | Mock GET with top-level `company_search_terms` | tests |

**Spike / investigation:** none.

## Stage 1: API — read path (table → client)

**Done when:** `GET /api/candidates/<id>` includes a top-level string field **`company_search_terms`** built from the table; artifact blob is not used for this field.

1. In **`src/ui/api/api_candidate.py`**, import from **`src.core.candidate`**: **`company_search_terms_text`** (AST-524).
2. In **`get_candidate_detail`**, after **`get_candidate`** succeeds and before **`jsonify`**, call **`company_search_terms_text(candidate_id)`** and set on the outbound dict: **`candidate["company_search_terms"] = <that string>`** (do not mutate stored **`candidate_data.artifacts`** for this).
3. **Do not** add **`company_search_terms`** to **`list_candidates`** / list endpoint responses (list view does not need term text).
4. **Do not** change **`GET /api/candidates/<id>/generate/...`** or craft generate handlers in this stage.

### Self-review (Stage 1)

| Rule | OK? |
|------|-----|
| §3.3 imports | **`api → core`** only |
| §3.5 naming | snake_case API field matches existing artifact key name |

---

## Stage 2: API — write path (client → table sync, no blob)

**Done when:** `PUT /api/candidates/<id>/data` with `artifacts.company_search_terms` syncs the table and does **not** persist that key in **`candidate_data.artifacts`**; blank/whitespace-only input still returns **400** with the same error semantics.

1. In **`src/ui/api/api_candidate.py`**, import **`parse_company_search_terms_text`** and **`sync_company_search_terms`** from **`src.core.candidate`**.
2. In **`update_candidate_data`**, inside the **`if isinstance(arts, dict):`** block, **before** **`normalize_rubric_artifacts_on_save(arts)`**:
   - If **`"company_search_terms" in arts`**:
     - Let **`raw = arts.pop("company_search_terms")`** (always pop so it never reaches **`save_candidate_data`**).
     - If **`raw is None`**, skip sync (no-op for this field — same as current normalize early-return for null).
     - Else try **`terms = parse_company_search_terms_text(raw)`**; on **`ValueError`**, return **`jsonify({"error": str(e)})`**, **400**.
     - Call **`sync_company_search_terms(candidate_id, terms)`**.
3. **Remove** the call to **`normalize_company_search_terms_on_save(arts)`** in **`update_candidate_data`** (AST-524 owns validation via **`parse_company_search_terms_text`**).
4. If **`arts`** is empty after pop, **`body.pop("artifacts", None)`** so **`save_candidate_data`** is not invoked solely for an empty artifacts dict (when the PUT body had only search terms).
5. Leave all other artifact normalization (**rubrics**, resume structure, cover letter signature) unchanged.

⚠️ **Decision:** Sync runs **even when** the PUT also updates other **`candidate_data`** fields in the same request — table is updated first, then remaining body merges as today.

### Self-review (Stage 2)

| Rule | OK? |
|------|-----|
| §1.3 DRY | Reuse AST-524 parse/sync; no duplicate SQL in API |
| §2.4 batch | N/A — single-candidate sync |

---

## Stage 3: Frontend — load from table-backed API field

**Done when:** Page loads textarea from **`company_search_terms`** on the GET candidate response; Generate/Regenerate/Save/autosave behavior unchanged from the user’s perspective; vitest passes.

1. In **`src/ui/frontend/src/pages/ArtifactsCompanySearchTerms.tsx`**, in the **`useEffect`** load handler for **`GET /api/candidates/${selectedId}`**:
   - Replace **`(c.candidate_data?.artifacts ?? {}).company_search_terms`** with **`c.company_search_terms`** (top-level on candidate JSON from Stage 1).
   - Coerce non-string to **`""`**: **`const raw = c.company_search_terms; setText(typeof raw === "string" ? raw : "")`**.
   - Keep **`everSaved`** logic: **`typeof raw === "string" && raw.trim() !== ""`**.
2. **Do not** change **`doSave`** PUT body — keep **`{ artifacts: { company_search_terms: value } }`** (Stage 2 intercept).
3. **Do not** change Generate URL, task key, snapshot/review UX, autosave timing, or layout classes.
4. **Do not** add per-row table UI or new routes.

### Self-review (Stage 3)

| Rule | OK? |
|------|-----|
| §3.5 naming | Flat **`pages/ArtifactsCompanySearchTerms.tsx`**, no new CSS file |
| §3.2 UI logic | Generate gating still from **`stateUi.candidate.artifact_generate_states`** |

---

## Stage 4: Tests

**Done when:** Targeted pytest + vitest for this ticket pass.

1. **`tests/component/ui/api/test_api_candidate.py`**:
   - Update **`test_update_rejects_blank_company_search_terms`**: monkeypatch **`parse_company_search_terms_text`** to raise **`ValueError("... non-empty search term ...")`** OR let real parser run if AST-524 is merged; assert **400** unchanged.
   - Add **`test_update_company_search_terms_syncs_table_not_artifact_blob`**: monkeypatch **`parse_company_search_terms_text`** → `["alpha", "beta"]`, **`sync_company_search_terms`**, **`save_candidate_data`**, **`get_candidate`**; PUT **`{"artifacts": {"company_search_terms": "alpha\nbeta"}}`**; assert **`sync_company_search_terms`** called once with **`("cand-1", ["alpha", "beta"])`**; assert **`save_candidate_data`** was **not** called with an **`artifacts`** dict containing **`company_search_terms`** (either not called at all when body empty after pop, or called with artifacts lacking that key).
   - Add **`test_get_candidate_detail_includes_company_search_terms`**: monkeypatch **`get_candidate`** → minimal candidate dict; monkeypatch **`company_search_terms_text`** → `"line one\nline two"`; GET detail; assert JSON **`company_search_terms == "line one\nline two"`**.
2. **`tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx`**:
   - Change GET **`/api/candidates/c1`** mock payloads to set top-level **`company_search_terms: "Series B fintech\nremote-first"`** and **omit** **`artifacts.company_search_terms`** (table is source of truth).
   - Empty-load test: **`company_search_terms: ""`** or omit field; expect **Generate** button.
3. **Do not** edit **`tests/component/core/test_candidate.py`** normalization tests — those belong to **AST-524**.
4. **Do not** add **`ASTRAL_TEST_BIBLE.md`** rows in this ticket (Betty at **qa-astral** if needed).

---

## Execution contract (for the developer agent)

- Execute stages **1 → 4** in order; one commit per stage on **`dev-kath`**, then cherry-pick publish per **build-astral**.
- If **AST-524** symbols are missing after sync with **`origin/dev`**, stop and comment on **AST-523** with the 🛑 blocked format — do not reimplement table/sync in this ticket.
- If **`parse_company_search_terms_text`** error messages differ from current UI expectations, stop and comment — do not reword errors locally in the API layer.
- Do not change **`COMPANY_SEARCH_TERMS`** token path (**AST-525**), **`inflow_discovery`** (**AST-525**), or database schema (**AST-524**).

---

## Self-Assessment

**Scope:** `Single-Component` — Touches only **`api_candidate.py`**, **`ArtifactsCompanySearchTerms.tsx`**, and their component tests; no schema, discovery, or token registry.

**Conf:** `Medium` — Pattern matches existing Artifacts save/load, but exact AST-524 helper names must exist on the integration line before implementation starts.

**Risk:** `Medium` — Wrong save intercept could still write the legacy artifact blob or skip sync; regression is confined to Company Search Terms save/load, not global candidate saves.

## Self-Review vs ASTRAL_CODE_RULES

| Section | Assessment |
|---------|------------|
| §1.3 DRY | API delegates parse/sync to **AST-524** core — no SQL in UI layer |
| §2.1 config | No new config keys |
| §2.4 batch | N/A |
| §2.6 state machine | No candidate/company state changes |
| §3.3 imports | **`api_candidate → core.candidate`** only |
| §3.5 naming | Flat page file; snake_case JSON field |

No conflicts requiring **`conf-!!-NONE`**.

## Resolution

**2026-05-28 — Radia review (`Review Posted`)**

- **fix-now (§5d):** Removed AST-517/519 `resume_structure` surface from this publish ref — `RESUME_STRUCTURE_*` in `config.py`, helpers in `candidate.py`, `GET …/resume_structure` and PUT merge/normalize paths in `api_candidate.py`, and `TestAst519ResumeStructureApi`. AST-526 keeps only table-backed GET `company_search_terms`, PUT sync via `apply_company_search_terms_save`, empty-body skip after blob strip, and `ArtifactsCompanySearchTerms.tsx`.
- **discuss (symbol names):** Betty manifest targets shipped AST-524 helpers (`apply_company_search_terms_save`, `company_search_terms_joined_text`); plan names were aspirational — no product change.

## Review

- **Branch:** `origin/sub/AST-523/AST-526-artifacts-ui-and-api-for-search-terms-table`
- **Tip:** `50b135f9`
- **Built:** 2026-05-28 — stages 1–3 complete (tests deferred to Betty per build-astral test-tree ban).
