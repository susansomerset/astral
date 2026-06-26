<!-- linear-archive: AST-526 archived 2026-06-15 -->

## Linear archive (AST-526)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-526/artifacts-ui-and-api-for-search-terms-table-company-search-terms-table  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-523 — Company search terms table with per-term last_scan_at (Roster inflow)  
**Blocked by / blocks / related:** parent: AST-523

### Description

## What this implements

Artifacts **Company Search Terms** page and candidate API: load textarea from table rows (newline-joined), save/autosave syncs upsert-and-delete via **AST-524** helpers; Generate flow unchanged from user perspective.

## Acceptance criteria

1. Saving the Company Search Terms textarea creates/updates/deletes **company_search_terms** rows for that candidate; terms removed from the text are deleted from the table.
2. Regenerating terms and saving applies upsert-and-delete; terms unchanged in text retain their prior **last_scan_at**.
3. Artifacts page still presents one textarea, one term per line; Generate/Regenerate/Save behavior matches other craft artifacts from the user's perspective.

## Boundaries

* No table schema — **AST-524**.
* No discovery/dispatch logic — **AST-525**.
* Textarea only; no per-row table UI.

## Notes for planning

* **ArtifactsCompanySearchTerms.tsx**, **api_candidate.py**.
* Stop persisting **artifacts.company_search_terms** blob on save after **AST-524** lands.

## Git branch (authoritative)

**sub/AST-523/AST-526-artifacts-ui-and-api-for-search-terms-table**

### Comments

#### chuckles — 2026-06-02T19:34:52.294Z
[check-linear]

Confirmed merged to **`origin/dev`** via **AST-523** / **AST-490** composite merges (**`0cc15621`**, **`803aaa1f`**). Artifacts Company Search Terms UI + API on dev (`ArtifactsCompanySearchTerms.tsx`, `api_candidate.py`). Publish sub branch deleted post-rollup.

**Done** — engineer assignee unchanged (Katherine).

— Chuckles

#### susan — 2026-06-02T17:40:30.998Z
@chuckles Please confirm this ticket is actually done and merged to dev origin, and then set it to Done?

#### chuckles — 2026-05-29T03:40:17.009Z
## prep-uat blocker — fix-now (Katherine)

**prep-uat AST-523** failed at §6 collection: tests import **`RESUME_STRUCTURE_*`** symbols removed from product on this publish ref (Radia §5d — AST-517/519 surface intentionally out of AST-526 scope).

**Failing imports:**
- `tests/component/core/test_candidate.py` — `RESUME_STRUCTURE_CONTACT_SECTION_IDS`, `RESUME_STRUCTURE_KNOWN_SECTION_IDS`
- `tests/component/utils/test_config.py` — `RESUME_STRUCTURE_DEFAULT`, contact/known section ids

**Fix:** Remove or rewrite those test sections so collection matches the 526 product scope (no `resume_structure` API/config on this branch). Do **not** restore `RESUME_STRUCTURE_*` in `config.py` unless Susan reverses the Radia cut.

**Owner:** Katherine — fix on **`dev-kath`**, publish to **`origin/sub/AST-523/AST-526-artifacts-ui-and-api-for-search-terms-table`**, then **`resolve-astral AST-526`** → User Testing. Chuckles will re-rollup 526 → ftr after.

— Chuckles

#### radia — 2026-05-29T03:11:44.482Z
**Review (Radia)** — `origin/dev...origin/sub/AST-523/AST-526-artifacts-ui-and-api-for-search-terms-table`

### What's solid (AST-526 scope)
- **GET detail:** `candidate["company_search_terms"] = company_search_terms_joined_text(candidate_id)` — table-backed load.
- **PUT data:** `apply_company_search_terms_save` before persist; `if body:` avoids empty save after blob strip.
- **Frontend:** `ArtifactsCompanySearchTerms.tsx` reads top-level `c.company_search_terms`; save body unchanged (`artifacts.company_search_terms`).
- **§3.3:** API uses core helpers, no direct `database` in routes.

### fix-now
- **§5d cross-ticket boundary:** Incremental diff **524→526** adds **AST-517** `resume_structure` surface (`RESUME_STRUCTURE_*` in `config.py`, `normalize_resume_structure` / `resolve_resume_structure` in `candidate.py`, `GET …/resume_structure` and related `api_candidate.py` paths). **Not** in AST-526 plan or acceptance criteria — remove from this publish ref or split to the owning ticket before **resolve-astral**.

### discuss
- **Plan symbol names:** Plan cites `parse_company_search_terms_text` / `sync_company_search_terms`; implementation uses `normalize_company_search_terms_on_save` + `sync_company_search_terms_from_text` / `apply_company_search_terms_save`. Behavior looks equivalent; confirm Betty tests target the shipped names.

### advisory
(none)

— Radia

#### katherine — 2026-05-29T02:58:32.993Z
[check-linear]

**Session scope:** **AST-526** only (parent **AST-523** / **Astral Roster**); sibling **AST-524**/**525** and parent pipeline out of scope.

**§0a (`astral-kath` / `dev-kath`):** `git fetch origin`, `checkout dev-kath`, `merge origin/dev` — **merge-clean** (`BEHIND=0`, `origin/dev` ancestor of `HEAD`). No publish-ref merges (check-linear only; no `test-astral` / `resolve-astral`).

**§0b:** `@katherine` issue search (Team Astral + **Astral Roster** project); **14d** fallback on roster project. Full thread on **AST-526**. **0** actionable comments — nothing `@katherine` or directed at Katherine needing reply or small fix.

**§1:** Assignee **AST-526** — latest thread activity is Katherine test-pass report (`4e9f3f49`); Betty manifest updates predate it and require no engineer reply.

**Pipeline:** Inbox quiet; ticket **Tests Passed** — no `resolve-astral` from this pass (happy path).

#### katherine — 2026-05-29T02:53:13.882Z
Manifest green after product fix @ `origin/sub/AST-523/AST-526-artifacts-ui-and-api-for-search-terms-table` `4e9f3f49`.

```
./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_candidate.py::TestAst526ArtifactsCompanySearchTermsApi  # 3 passed
npx vitest run .../test_ArtifactsCompanySearchTerms.test.tsx  # 2 passed
```

**Fix:** `update_candidate_data` skips `save_candidate_data` when the PUT body is empty after company search terms sync; restored `resume_structure` core/config symbols required by `api_candidate` imports on the integration line.

#### betty — 2026-05-29T02:45:12.563Z
**Manifest update** — publish tip is now `a2c353c6`; bible shasum `348d58d8979332e6d8a3beec5daab02a82c0c8d81949259f37ef95235831f79c`.

Blank-input **400** coverage lives in **`TestAst526ArtifactsCompanySearchTermsApi::test_update_rejects_blank_company_search_terms`** (publish ref does not carry the legacy **`TestCandidateRoutes`** node).

— Betty

#### betty — 2026-05-29T02:44:45.967Z
## QA test manifest

**Publish ref:** `origin/sub/AST-523/AST-526-artifacts-ui-and-api-for-search-terms-table` @ `8e6dd085`

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` shasum `fa54004dff2204faec35284dec9d769403a3c55334bb44ed4ad40ab3d5b2221b` on publish ref (§7.13zi)

Run from repo root on **`dev-kath`** after merging this publish ref:

1. `./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_candidate.py::TestAst526ArtifactsCompanySearchTermsApi`
2. `./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_update_rejects_blank_company_search_terms`
3. `./scripts/testing/run_component_tests.sh tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx`

**Blocker smoke (optional):** §7.13zi **AST-524** narrowed run if table/sync regressions are suspected.

**Coverage notes:**
- **GET** detail injects top-level **`company_search_terms`** from **`company_search_terms_joined_text`** (not artifacts blob).
- **PUT** with only **`artifacts.company_search_terms`** syncs table, strips blob, skips **`save_candidate_data`** when body is empty after pop (AST-526 API order).
- **§6c** routed page Vitest mocks top-level GET field; Generate/Regenerate/Save paths unchanged.

— Betty

#### chuckles — 2026-05-29T02:14:23.919Z
## Plan validation — APPROVED

**Verdict:** APPROVED → **Plan Approved**

Textarea UX preserved; PUT intercept + strip blob is the right contract.

— Chuckles

#### katherine — 2026-05-29T02:11:52.105Z
Plan: [`docs/features/roster/ast-526-artifacts-ui-and-api-for-search-terms-table-company-search-terms-table-with-per-term-last-scan-at-roster-inflow.md`](https://github.com/susansomerset/astral/blob/sub/AST-523/AST-526-artifacts-ui-and-api-for-search-terms-table/docs/features/roster/ast-526-artifacts-ui-and-api-for-search-terms-table-company-search-terms-table-with-per-term-last-scan-at-roster-inflow.md) (published `39508dfd` on `sub/AST-523/AST-526-artifacts-ui-and-api-for-search-terms-table`).

**Self-assessment**
- **Scope:** `Single-Component` — `api_candidate.py`, `ArtifactsCompanySearchTerms.tsx`, and targeted tests only; no schema, discovery, or token work.
- **Conf:** `Medium` — UI/API pattern is familiar, but build depends on AST-524 helper names (`parse_company_search_terms_text`, `sync_company_search_terms`, `company_search_terms_text`) landing on the integration line first.
- **Risk:** `Medium` — Save intercept must sync the table without writing `artifacts.company_search_terms`; failure mode is isolated to this Artifacts page.

---

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
