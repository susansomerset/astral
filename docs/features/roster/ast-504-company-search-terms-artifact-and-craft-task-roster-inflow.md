<!-- linear-archive: AST-504 archived 2026-06-15 -->

## Linear archive (AST-504)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-504/company-search-terms-artifact-and-craft-task-roster-inflow  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-490 — Roster inflow  
**Blocked by / blocks / related:** parent: AST-490; blocks: AST-505

### Description

## What this implements

Phase 0 of roster inflow: a candidate **artifact** holding line-break-delimited Google discovery search terms, a **craft** AI task to generate them from profile/context, and **Artifacts UI** to regenerate or edit directly (same pattern as other craft artifacts). Phase 0 dispatch is on-demand only.

## Acceptance criteria

1. Phase 0 craft task populates a candidate artifact with a non-empty line-break-delimited search-term list; user can regenerate or edit it in Artifacts UI.
2. Phase 0 dispatch is on-demand only.

## Boundaries

* Does not run Google CSE or create company rows — sibling **Phase 1** ticket.
* Does not change **IMPORTED** manual-import path.
* **AST-497** (company surrogate PK) out of scope.

## Notes for planning

* Mirror existing craft artifact + ArtifactEditor patterns (e.g. company watch criteria).
* Token/artifact keys in config per ASTRAL_CODE_RULES §2.1.
* Parent definition: AST-490.

## Git branch (authoritative)

Per **orientation-astral** § Branch law: parent `ftr/AST-490-roster-inflow`, child `sub/AST-490/<child-segment>`.

### Comments

#### chuckles — 2026-05-28T00:21:59.829Z
`[rollup-child] blocked:` merge `origin/sub/AST-490/AST-504-company-search-terms-artifact-and-craft-task` → `origin/ftr/AST-490-roster-inflow` conflicts in:
- `docs/ASTRAL_TEST_BIBLE.md`
- `tests/component/utils/test_config.py`

507 rolled up cleanly; 504/505/506 rollups paused. @susan — resolve on ftr (union bible + both sides' test_config sections) or say the word and I'll retry after engineer refresh.

— Chuckles

#### radia — 2026-05-28T00:16:41.118Z
**Diff:** `origin/dev...origin/sub/AST-490/AST-504-company-search-terms-artifact-and-craft-task`

### Plan fidelity (AST-504 scope)
- Phase 0 deliverables match plan: `craft_company_search_terms` in `TASK_CONFIG`, `COMPANY_SEARCH_TERMS` token, `NAV_CONFIG` + route, `normalize_company_search_terms_on_save` / `company_search_terms_lines`, Artifacts page with generate/regenerate/autosave, API normalization on PUT.
- No `dispatch_tasks` / scheduler seed for Phase 0 craft — correct on-demand-only boundary.

### ASTRAL_CODE_RULES
- **§3.3 / B2:** UI → core only (`api_candidate` → `candidate`); no layer violations in product diff.
- **§2.1:** Task, token, nav keys live in `config.py` only.
- **§2.6:** No new candidate/company states introduced.
- **D3 (`company_search_terms_lines`):** `(candidate_data or {}).get("artifacts") or {}` returning `[]` when missing is the documented downstream contract for AST-505 eligibility — acceptable read-path default, not a silent write fallback.

### Code quality
- Normalization DRY via `_company_search_terms_lines_from_string`; PUT rejects non-string and all-blank with clear `ValueError` → 400 in API test.
- `ArtifactsCompanySearchTerms.tsx` mirrors existing craft-artifact UX (`artifact_generate_states`, 2s autosave, regen confirm). `handleCancel` fallback to `window.location.reload()` when not in post-generate review is slightly blunt but pre-existing pattern-adjacent — **advisory** only.

### Cross-ticket / harness (§5d)
- Diff includes **test-only** updates for **AST-511** (`test_AdminManageCandidates` middle-name selectors/payload tests) and **AST-457** (`test_CandidateBoardSearches` UserPrompt flow) plus broad **ASTRAL_TEST_BIBLE** sibling rows — not AST-504 product scope. Bible §7.13zg documents this as harness tail; no product smuggling.
- **Discuss:** Confirm parent integration order so full Vitest tail (not just narrowed AST-504 manifest) stays green before UAT — middle-name `it()` blocks expect labels/shapes from AST-511 which is not on this publish tip.

### Self-Assessment
- Stated **Single-Component** / **conf-high** / **risk-low** matches the product footprint.

**Verdict:** No fix-now on AST-504 product code. Proceed to `resolve-astral` unless Susan wants sibling harness merged first.

#### katherine — 2026-05-28T00:14:09.715Z
[check-linear]

- **§0b actionable thread:** Your **`[check-linear]`** @ `2026-05-28` @ **`katherine`** — acknowledged **`[qa-handoff]`** cleared on publish **`origin/sub/AST-490/AST-504-company-search-terms-artifact-and-craft-task`** @ **`847416e8`** (Admin middle-field selectors + BoardSearches confirm pattern).
- **This pass:** Inbox-only — did **not** run **`test-astral`** (manifest items 1–5); that is the next stage skill when Susan/orchestrator names it.
- **§0a:** **`dev-kath`** merged with **`origin/dev`** at pass start.

#### betty — 2026-05-28T00:05:59.057Z
[check-linear]

Cleared **[qa-handoff]** (test-astral return pass):

- **Publish:** `origin/sub/AST-490/AST-504-company-search-terms-artifact-and-craft-task` @ `847416e8` (`test(AST-504): fix harness tail — Admin middle field + BoardSearches confirm`)
- **Tests:** `test_AdminManageCandidates.test.tsx` (AST-511 middle-name selectors); `test_CandidateBoardSearches.test.tsx` (AST-457 `UserPromptProvider` mode switch)
- **Bible:** `docs/ASTRAL_TEST_BIBLE.md` shasum `75c536fc54eca130a2322a36877313db5b4fa337` — §7.13zg harness tail note
- **Assignee:** @katherine — re-run **`test-astral`** manifest (items 1–5); stay **Tests Ready**

#### betty — 2026-05-28T00:05:56.657Z
**Tests updated for [qa-handoff]** — `origin/sub/AST-490/AST-504-company-search-terms-artifact-and-craft-task` @ `847416e8`

`docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `75c536fc54eca130a2322a36877313db5b4fa337` — §7.13zg (+ harness tail note).

**Fixes (harness tail, not AST-504 product):**
- `test_AdminManageCandidates.test.tsx` — label-based field lookup + AST-511 middle payload cases (no brittle textbox indices).
- `test_CandidateBoardSearches.test.tsx` — restored AST-457 coverage; mode switch confirms via **`UserPromptProvider`** (**Continue**), not **`window.confirm`**.

**Manifest (unchanged):**

1. `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst504CompanySearchTermsConfig`
2. `./scripts/testing/run_component_tests.sh tests/component/core/test_candidate.py::TestNormalizeCompanySearchTermsOnSave`
3. `./scripts/testing/run_component_tests.sh tests/component/core/test_candidate.py::TestCompanySearchTermsLines`
4. `./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_update_rejects_blank_company_search_terms`
5. `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx`

Verified locally: manifest item **1** pytest + full Vitest tail **224 passed**.

**Admin prerequisite (Stage 5):** `craft_company_search_terms` task prompt row in Admin → Task Prompts before Generate in UAT.

#### katherine — 2026-05-28T00:01:44.829Z
[qa-handoff]

@Betty White — AST-504 **product scope is green**; manifest items **1–4** fail on the harness tail, not on AST-504 assertions.

**Publish ref:** `origin/sub/AST-490/AST-504-company-search-terms-artifact-and-craft-task` @ `e8e28e1e` (matches fetched tip).

**Green (AST-504 only):**
```bash
.venv/bin/python -m pytest \
  tests/component/utils/test_config.py::TestAst504CompanySearchTermsConfig \
  tests/component/core/test_candidate.py::TestNormalizeCompanySearchTermsOnSave \
  tests/component/core/test_candidate.py::TestCompanySearchTermsLines \
  tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_update_rejects_blank_company_search_terms
# → 10 passed

cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx
# → 2 passed
```

**Red — manifest items 1–4** (`./scripts/testing/run_component_tests.sh <pytest node ids>`): pytest portion passes, then `run_component_tests.sh` always runs **full** `npm run test:component:coverage` (all 68 Vitest files). Three **unrelated** failures:

1. `test_AdminManageCandidates.test.tsx` — add flow uses `getAllByRole("textbox")[1]` for last name, but **AST-511** added a Middle Name field (indices shifted). Tests never reach success toast / second case times out.
2. `test_AdminManageCandidates.test.tsx` — same root cause on validation case.
3. `test_CandidateBoardSearches.test.tsx` **AST-457** mode-switch case — asserts `window.confirm` was called, but product uses `useUserConfirm` via `UserPromptProvider` (`renderWithProviders` wraps provider; `switchMode` calls `confirm()` from context, not `window.confirm`).

**Why this is test/manifest, not product:** All §7.13zg / manifest-listed AST-504 nodes pass in isolation. Failures are stale selectors / wrong confirm mock on **other** page tests pulled in by the harness tail.

**Ask:** Either update those three tests (AST-511 middle-name indices; AST-457 UserPrompt confirm mock/pattern per `test-utils.tsx` note), or document a narrowed manifest that skips full Vitest on pytest-only items (similar to §7.13z / §7.13za bible notes). Reassign me when manifest is green end-to-end.

#### betty — 2026-05-27T23:52:08.497Z
**QA manifest** — `origin/sub/AST-490/AST-504-company-search-terms-artifact-and-craft-task` @ `e8e28e1e`

`docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `edd55ac5fd64f5ab827cac1b11278f98addac047` — see §7.13zg.

1. `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst504CompanySearchTermsConfig`
2. `./scripts/testing/run_component_tests.sh tests/component/core/test_candidate.py::TestNormalizeCompanySearchTermsOnSave`
3. `./scripts/testing/run_component_tests.sh tests/component/core/test_candidate.py::TestCompanySearchTermsLines`
4. `./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_update_rejects_blank_company_search_terms`
5. `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx`

**Admin prerequisite (Stage 5):** `craft_company_search_terms` task prompt row must exist in Admin → Task Prompts before Generate works in UAT (not seeded in product code per plan).

Built by Katherine.

#### katherine — 2026-05-27T23:42:02.516Z
Plan: `docs/features/roster/ast-504-company-search-terms-artifact-and-craft-task-roster-inflow.md`

https://github.com/susansomerset/astral/blob/sub/AST-490/AST-504-company-search-terms-artifact-and-craft-task/docs/features/roster/ast-504-company-search-terms-artifact-and-craft-task-roster-inflow.md

**Self-assessment**
- **Scope:** `Single-Component` — one artifact string key, one craft task, one Artifacts page, small core normalization; no dispatch scheduler row.
- **Conf:** `high` — reuses existing craft generate/save and `company_prefilter` UI patterns with a plain-text payload.
- **Risk:** `low` — main failure mode is wrong storage shape for AST-505; plan locks string + newline contract and tests normalization.

Publish ref verified and merged on `dev-kath`. Plan cherry-picked to `origin/sub/AST-490/AST-504-company-search-terms-artifact-and-craft-task` (`2a4c6648`).

---

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
