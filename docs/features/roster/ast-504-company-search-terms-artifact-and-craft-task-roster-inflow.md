# AST-504 — Company search terms artifact and craft task (Roster inflow)

- **Linear:** [AST-504](https://linear.app/astralcareermatch/issue/AST-504/company-search-terms-artifact-and-craft-task-roster-inflow)
- **Parent (coordination only):** [AST-490](https://linear.app/astralcareermatch/issue/AST-490/roster-inflow)
- **Publish ref:** `origin/sub/AST-490/AST-504-company-search-terms-artifact-and-craft-task`

## Summary

Phase 0 of roster inflow: persist a candidate **artifact** `company_search_terms` as a single newline-delimited string of Google discovery queries, add **`craft_company_search_terms`** (JSON `{ search_terms: string }`) to generate from profile/context, and ship an **Artifacts** page with Generate/Regenerate, direct edit, and autosave — same UX contract as other craft artifacts (e.g. Company Watch Criteria) but **plain text**, not rubric criteria. **On-demand only:** no `dispatch_tasks` / scheduler row for this craft task; generation is **`POST /api/candidates/<id>/generate/craft_company_search_terms`** from the UI (existing craft pattern). Out of scope: Google CSE, company row creation (**AST-505**), **IMPORTED** path, **AST-497**.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add **`craft_company_search_terms`** to **`TASK_CONFIG`**; **`COMPANY_SEARCH_TERMS`** in **`TOKEN_SOURCES`**; **`NAV_CONFIG`** Artifacts item; optional **`DATA_SHAPES`** note in comment only if not needed | utils |
| `src/core/candidate.py` | **`normalize_company_search_terms_on_save(artifacts)`**; call from save path; optional **`company_search_terms_lines(candidate_data) -> list[str]`** helper (strip empty lines) for stable downstream contract | core |
| `src/ui/api/api_candidate.py` | Invoke normalization when **`artifacts.company_search_terms`** present in PUT body | ui |
| `src/ui/frontend/src/pages/ArtifactsCompanySearchTerms.tsx` | **New** thin page: single textarea, Generate/Regenerate/Cancel, autosave | ui |
| `src/ui/frontend/src/routes.tsx` | Route **`artifacts/company_search_terms`** | ui |
| `tests/component/utils/test_config.py` | Assert **`craft_company_search_terms`** in **`TASK_CONFIG`**, token registry | tests |
| `tests/component/core/test_candidate.py` | Normalization: accept multiline string, reject non-string, reject all-blank after trim | tests |
| `tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx` | **New** — heading, load string, generate button visibility stub | tests |
| `docs/ASTRAL_TEST_BIBLE.md` | Row for new page + core helper (Betty may refine at **qa-astral**) | docs |

**Spike / investigation:** none.

## Stage 1: Config and token registry

**Done when:** `TASK_CONFIG["craft_company_search_terms"]` exists with JSON **`search_terms`** string schema; **`TOKEN_SOURCES["COMPANY_SEARCH_TERMS"]`** resolves **`artifacts.company_search_terms`**; no **`_DISPATCH_TASK_SEED`** / **`dispatch_task`** row added for this key.

1. In **`src/utils/config.py`**, inside **`TASK_CONFIG`**, after **`craft_like_rubric`** (Phase **B. Candidate Artifacts**), append **`craft_company_search_terms`**:
   - **`phase`**: `"B. Candidate Artifacts"`
   - **`seq`**: next integer after **`craft_like_rubric`** (currently **7** → use **8**)
   - **`response_schema`**: `{ "search_terms": { "type": "str", "required": True } }`
   - **`response_format`**: `"json"`
   - **`entity_type`**: `None`
   - **`requires_candidate_key`**: `True`
   - **`trigger_state`**: `None`
2. In **`TOKEN_SOURCES`**, after **`COMPANY_PREFILTER`**, add:
   - **`"COMPANY_SEARCH_TERMS": {"source": "candidate", "path": "artifacts.company_search_terms"}`**
3. In **`NAV_CONFIG`**, under **Artifacts** **`items`**, after **Company Watch Criteria**, add:
   - **`{"label": "Company Search Terms", "path": "/artifacts/company_search_terms"}`**
4. **Do not** add **`craft_company_search_terms`** to **`database._DISPATCH_TASK_SEED`**, **`_DISPATCH_TASK_TRIGGER_SEED`**, or **`DISPATCH_TASK_SEED_KEYS`**.

⚠️ **Decision:** Storage is a **single string** at **`candidate_data.artifacts.company_search_terms`**, not a rubric list and not **`profile.title_patterns`**. Phase 1 (**AST-505**) reads this string and splits on newlines; keep sibling contract stable.

⚠️ **Decision:** Phase 0 “on-demand only” = **UI/craft generate path only** (same as **`craft_company_prefilter`**), **not** a weekly **`dispatch_tasks`** row. Susan configures Phase 1 weekly search separately on **AST-505**.

### Self-review (Stage 1)

| Rule | OK? |
|------|-----|
| §2.1 config | Task + token in **`config.py`** only |
| §1.4 magic numbers | No inline limits |
| §2.6 state machine | No new candidate/company states |

---

## Stage 2: Core normalization and save contract

**Done when:** PUT **`artifacts.company_search_terms`** accepts only a normalized non-empty string (after user save); empty/whitespace-only rejected with **400**; helper returns trimmed non-empty lines for tests.

1. In **`src/core/candidate.py`**, add **`normalize_company_search_terms_on_save(artifacts: dict) -> None`**:
   - If **`"company_search_terms"`** not in **`artifacts`**, return.
   - If value is **`None`**, return (allow clear via explicit null only if existing save patterns allow — otherwise skip null handling).
   - Require **`isinstance(val, str)`**; else **`ValueError("Artifact 'company_search_terms' must be a string.")`**
   - Normalize: split on **`"\n"`**, strip each line, drop empty lines, rejoin with **`"\n"`** (no trailing newline required).
   - If result is empty string, **`ValueError("Artifact 'company_search_terms' must contain at least one non-empty search term.")`**
2. Add **`company_search_terms_lines(candidate_data: dict) -> list[str]`** in the same module: read **`(candidate_data or {}).get("artifacts") or {}`**, get **`company_search_terms`**, if missing/empty return **`[]`**, else return normalized split list (reuse same line-split logic as normalization).
3. In **`src/ui/api/api_candidate.py`**, in **`update_candidate_data`**, after **`normalize_rubric_artifacts_on_save(arts)`**, call **`normalize_company_search_terms_on_save(arts)`** when **`arts`** is a dict.

### Self-review (Stage 2)

| Rule | OK? |
|------|-----|
| §3.3 imports | **`api → core`** only |
| §1.3 DRY | Single normalization function reused by helper |

---

## Stage 3: Artifacts UI page and route

**Done when:** With candidate in **`artifact_generate_states`**, user opens **Company Search Terms**, clicks **Generate**, sees populated textarea, **Save** persists string; **Regenerate** confirms when data exists; manual edit autosaves (same **2s** debounce pattern as rubric artifacts).

1. Create **`src/ui/frontend/src/pages/ArtifactsCompanySearchTerms.tsx`** (flat **`pages/`**, one default export):
   - Use **`useCandidate`**, **`useStateUi`**, **`api`**, **`Toast`**, **`LabeledTextArea`** from existing imports (mirror **`ArtifactsCompanyWatchCriteria`** header/actions layout classes: **`dep-page`**, **`dep-header`**, **`dep-actions`**, **`dep-btn`**).
   - State: **`text`** (string), **`dirty`**, **`saving`**, **`generating`**, **`confirmRegen`**, **`snapshot`** (string | null for cancel-after-generate).
   - Load: **`GET /api/candidates/${selectedId}`** → **`artifacts.company_search_terms`**; coerce non-string loaded values to **`""`** (defensive).
   - **Generate / Regenerate:** **`POST /api/candidates/${selectedId}/generate/craft_company_search_terms`**; on success set **`text`** from **`parsed_response.search_terms`** (stringify if needed); set **`dirty` true**; toast “Generated — review and Save or Cancel”.
   - **Regenerate** when **`text.trim()`** non-empty: confirm dialog like **`ArtifactEditor`**.
   - **Save:** **`PUT /api/candidates/${selectedId}/data`** with body **`{ artifacts: { company_search_terms: text } }`** (normalization runs server-side).
   - **Autosave:** when **`dirty`** and not in post-generate review (**`snapshot === null`**), debounce **2000ms** to Save (same as **`ArtifactEditor`**).
   - **Cancel** after generate: restore **`snapshot`** string.
   - **`canGenerate`**: **`stateUi.candidate.artifact_generate_states.has(candidateState)`** (copy **`ArtifactEditor`** logic).
   - No **`ArtifactEditor`** / rubric tabs for this page.
2. In **`src/ui/frontend/src/routes.tsx`**: import page; add **`{ path: "artifacts/company_search_terms", element: <CompanySearchTerms /> }`** under Artifacts block (keep **SYNC** comment with **`NAV_CONFIG`**).
3. **Do not** add styles to a new CSS file — use existing **`App.css`** / **`dep-*`** / **`LabeledTextArea`** only.

### Self-review (Stage 3)

| Rule | OK? |
|------|-----|
| §3.5 naming | Flat **`pages/ArtifactsCompanySearchTerms.tsx`**, snake route |
| §3.2 UI logic | Generate gating from **`stateUi`**, not hardcoded states in component |

---

## Stage 4: Tests and bible row

**Done when:** Targeted pytest + vitest pass; bible lists new coverage.

1. **`tests/component/utils/test_config.py`**: assert **`"craft_company_search_terms" in TASK_CONFIG`** and **`"COMPANY_SEARCH_TERMS" in TOKEN_SOURCES`**.
2. **`tests/component/core/test_candidate.py`**: tests for **`normalize_company_search_terms_on_save`** (valid multiline, strips blanks, rejects non-string, rejects all-blank); **`company_search_terms_lines`** returns expected list.
3. **`tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx`**: render with mocked candidate + **`artifact_generate_states`**; expect heading **Company Search Terms**; optional mock generate response.
4. Add **`ASTRAL_TEST_BIBLE.md`** row under frontend artifacts / config as appropriate (one line each).

---

## Stage 5: Admin task prompt (manual prerequisite)

**Done when:** **Admin → Task Prompts** has a configured agent + task row for **`craft_company_search_terms`** (Susan/Chuckles — not created in product code in this ticket). Engineer verifies in build by preview/generate smoke or **`🛑`** comment on **AST-504** if prompts missing.

1. **Do not** seed prompt text in **`database.py`** in this ticket.
2. In build completion comment, note whether **`craft_company_search_terms`** prompt exists or is blocked on Susan.

---

## Execution contract (developer agent)

Follow **plan-astral** execution contract. Blocking ambiguity → **`🛑 Stage N blocked:`** comment on **[AST-504](https://linear.app/astralcareermatch/issue/AST-504/company-search-terms-artifact-and-craft-task-roster-inflow)** with step, issue, options. Do **not** implement **AST-505**, CSE wiring, or parent **AST-490** remainder. Do **not** add **`dispatch_tasks`** row for Phase 0 craft.

---

## Self-Assessment

**Scope:** `Single-Component` — one new artifact key, one craft task, one frontend page, small core validation; touches **`config.py`**, **`candidate.py`**, **`api_candidate.py`**, routes only.

**Conf:** `high` — mirrors **`craft_company_prefilter`** + **`ArtifactEditor`** generate/save flow with a simpler string payload; no new DB tables or dispatch machinery.

**Risk:** `low` — wrong storage shape would break **AST-505** reader; mitigation is documented string contract + normalization tests.

---

## Self-review vs ASTRAL_CODE_RULES

| Rule | Conflict? |
|------|-----------|
| §1.3 DRY | Reuse generate endpoint + ledger pattern unchanged |
| §2.1 config | All keys in **`TASK_CONFIG`** / **`TOKEN_SOURCES`** / **`NAV_CONFIG`** |
| §2.4 batch | Generate uses existing **`run_candidate_artifact_generation`** ledger (**batch_size=1**) — no new batch claim |
| §2.6 state machine | No registry changes |
| §3.3 imports | UI → core → data unchanged |
| §3.5 naming | Flat page, snake route, **`company_search_terms`** artifact key |

No **`conf-!!-NONE`** flags.

## Review stub (Katherine / build)

**Publish ref:** `origin/sub/AST-490/AST-504-company-search-terms-artifact-and-craft-task`  
**Product tip:** `54f529ca` — config + normalization + Artifacts UI (3 commits)

**Admin prerequisite (Stage 5):** `craft_company_search_terms` task prompt row must exist in Admin → Task Prompts before Generate works in UAT (not seeded in product code per plan).

## Review

**Radia** (`review-astral`, 2026-05-28): Diff `origin/dev...origin/sub/AST-490/AST-504-company-search-terms-artifact-and-craft-task`. Plan fidelity and ASTRAL_CODE_RULES clean; **no fix-now** on AST-504 product code. **Discuss:** parent integration order so full Vitest tail stays green before UAT (AST-511 middle-name shapes) — Betty addressed harness tail @ `847416e8`. **Advisory:** `handleCancel` reload fallback — pre-existing pattern-adjacent only.

## Resolution

**Katherine** (`resolve-astral`, 2026-05-28): No product code changes — Radia **fix-now** list empty. Publish tip unchanged for product: `origin/sub/AST-490/AST-504-company-search-terms-artifact-and-craft-task` @ `847416e8` (includes Betty harness tail `test(AST-504):`). §9a dry-run clean vs `origin/dev` and `origin/ftr/AST-490-roster-inflow`. **User Testing** — assignee Katherine; Admin **craft_company_search_terms** prompt prerequisite per Stage 5.
