<!-- linear-archive: AST-616 archived 2026-06-23 -->

## Linear archive (AST-616)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-616/admin-api-and-base-resume-content-ui-from-candidate-structure-rebuild  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-601 — Rebuild 519 (git casualty)  
**Blocked by / blocks / related:** parent: AST-601

### Description

## What this implements

Recreate [AST-519](https://linear.app/astralcareermatch/issue/AST-519) per-candidate **Base Resume Content** behavior lost in git merges: candidate admin API exposes each candidate's enabled resume section catalog; **Base Resume Content** shows one tab per enabled section in catalog order (not global shapes alone); editor loads/saves `artifacts.base_resume` keyed by section ids with orphan keys stripped on save; accent reads/writes `artifacts.resume_structure.accent_color`.

## Acceptance criteria

1. Authenticated `GET` for a candidate's resume structure returns enabled sections in catalog order with labels and accent color (or null when absent).
2. **Base Resume Content** shows one tab per enabled section for the selected candidate, in defined order — not tabs from the global template alone.
3. Saving base resume content persists only keys allowed by that candidate's structure; orphan keys in the request body are dropped before merge.
4. Accent picker reads initial value from structure and saves to `artifacts.resume_structure.accent_color`.
5. A second candidate with a different section catalog shows different tabs; switching between candidates does not leak one catalog into the other.
6. No orphan section keys appear as editor tabs when structure and stored content disagree.
7. Component tests covering the AST-519 API and Base Resume Content UI contract pass on the merged branch.

## Boundaries

* Does **not** implement structure persistence or `craft_resume_base` — [AST-517](https://linear.app/astralcareermatch/issue/AST-517) (Done on dev).
* Does **not** own resume builder HTML merge or job artifact key filtering — [AST-518](https://linear.app/astralcareermatch/issue/AST-518).
* Does **not** implement job-scoped resume draft tabs in JAR — [AST-553](https://linear.app/astralcareermatch/issue/AST-553) lineage.

## Notes for planning

Reference: `docs/features/candidate/ast-519-admin-api-and-base-resume-content-ui-from-candidate-structure.md` (approved plan from original ship). Partial backend helpers may remain on dev; verify GET route and Base Resume Content wiring against plan.

## Git branch (authoritative)

Per **orientation** § Branch law: parent `ftr/AST-601-rebuild-519-git-casualty`, child `sub/AST-601/<child-segment>`. Created at **dispatch-parent**.

### Comments

#### radia — 2026-06-14T04:13:41.434Z
**Review** — `origin/dev...origin/sub/AST-601/AST-616-base-resume-content-ui-rebuild-519` @ `be1c3618`

Plan: [ast-616 plan doc](https://github.com/susansomerset/astral/blob/sub/AST-601/AST-616-base-resume-content-ui-rebuild-519/docs/features/interface/ast-616-admin-api-and-base-resume-content-ui-from-candidate-structure-rebuild-519.md)

### Solid (AST-616 scope)

- **`GET …/resume_structure`** — route before catch-all; 404; `enabled_resume_structure_sections` + accent null when non-string (`api_candidate.py`).
- **Imports** — structure helpers restored; duplicate `company_search_terms_*` lines removed.
- **`ArtifactsBaseResumeContent.tsx`** — structure GET drives tabs + accent; `useCandidateResumeStructure` + `structureSections`; accent PUT → `artifacts.resume_structure.accent_color`.
- **Tests / bible** — page tests mock structure GET, hide orphans, assert accent PUT, candidate switch; §7.13zzd manifest matches.
- **Layers** — API → core only; no §5f debug touched.

### fix-now

1. **`src/data/database.py` + `src/ui/api/api_admin.py`** (commit `6e5f2e17`, AST-617 label) — **§5d cross-ticket scope.** Replaces `dispatch_claim_uses_score_floor` with `trigger_state_used_by_scored_dispatch_task` on claim count/backfill/admin `is_scored`. **`origin/dev` already has the correct `dispatch_claim_uses_score_floor` call sites** (`config.py`: VALID_TITLE input triggers must not score-gate claim). This branch **reverts AST-586** — qualify on VALID_TITLE would incorrectly apply `score_floor`. Revert both files to match `origin/dev`.

2. **`docs/features/interface/ast-617-dispatch-claim-without-score-floor-valid-title-rebuild-586.md`** — deleted on branch; exists on `origin/dev`. Restore from dev (sibling AST-617 doc, not this ticket).

### Recommended actions

| Action | Notes |
| --- | --- |
| Revert `database.py` + `api_admin.py` to `origin/dev` | Keep AST-616: `api_candidate.py`, `ArtifactsBaseResumeContent.tsx`, tests, bible |
| Restore AST-617 plan doc from `origin/dev` | `git checkout origin/dev -- docs/features/interface/ast-617-…` |
| Re-run §7.13zzd narrowed manifest | After revert |

#### betty — 2026-06-14T04:11:43.529Z
[check-linear] Cleared epic **`origin/dev`** merge blocker on **`docs/ASTRAL_TEST_BIBLE.md`**: **`astral-tests`** merged **`origin/dev`** @ **`718bd68d`** — **§7.13zzd** (AST-616) retained alongside dev cumulative sections. Sub publish ref unchanged bible-wise (**§7.13zzd** already present); **`merge-tests`** records delivery @ **`26bb967e`**.

**Tests lane:** `origin/tests` @ **`44554e56`** (`docs(AST-616): tests origin/dev merge clean`)

**Publish:** `origin/sub/AST-601/AST-616-base-resume-content-ui-rebuild-519` @ **`26bb967e`** (`merge-tests(AST-616): origin/tests 44554e56`)

**`docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref:** `31df000bef9567aec8bbc0ed3abdd65cd9165b15642ae3be536ecd62d8ba888e`

Epic worktree **`git merge origin/dev`** should reconcile bible using **`origin/tests`** (post-**`718bd68d`**) as reference for **§7.13zzd**. Reassigned **Katherine Johnson**.

#### betty — 2026-06-14T04:08:49.212Z
[check-linear] Cleared [qa-handoff]: `test_ArtifactEditor.test.tsx` now uses `importOriginal` partial api mock (preserves `setAuthTokenGetter` for `AuthProvider`). Vitest manifest `-t "structureSections|Base Resume Content|resume_structure"` green locally.

**Publish:** `origin/sub/AST-601/AST-616-base-resume-content-ui-rebuild-519` @ `a2feddd7` (`merge-tests(AST-616): origin/tests ee5a83e2`)

Reassigned **Katherine Johnson** for **test-child**.

#### katherine — 2026-06-14T04:07:42.777Z
[qa-handoff]

@Betty White — manifest run on `origin/sub/AST-601/AST-616-base-resume-content-ui-rebuild-519` @ `31829dc8` (epic worktree merge-clean).

**Pytest (green):**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst519ResumeStructureUiHelpers \
  tests/component/ui/api/test_api_candidate.py::TestAst519ResumeStructureApi
```
→ 11 passed

**Vitest (1 fail):**
```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  -t "structureSections|Base Resume Content|resume_structure"
```
→ `test_ArtifactsBaseResumeContent.test.tsx` passed (1 run, 2 skipped)
→ `ArtifactEditor > loads fixed tabs from structureSections without shapes fetch` **failed**

**Failure (test harness, not product):**
```
[vitest] No "setAuthTokenGetter" export is defined on the "../../../../src/ui/frontend/src/lib/api" mock.
```
`renderWithProviders` mounts `AuthProvider`, which calls `setAuthTokenGetter` in `useLayoutEffect`. `test_ArtifactEditor.test.tsx` still uses a bare `vi.mock(..., () => ({ default: vi.fn() }))` without `setAuthTokenGetter`.

**Fix:** Match `test_ArtifactsBaseResumeContent.test.tsx` / `test_App.test.tsx` — partial mock via `importOriginal`:
```ts
vi.mock("../../../../src/ui/frontend/src/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../../../src/ui/frontend/src/lib/api")>()
  return { ...actual, default: vi.fn() }
})
```

Product code unchanged; no `src/` fix needed. Please republish manifest tip and reassign me when green locally.

#### betty — 2026-06-14T04:06:36.071Z
## QA test manifest (AST-616)

**Publish:** `origin/sub/AST-601/AST-616-base-resume-content-ui-rebuild-519` @ `31829dc8` (`merge-tests(AST-616): origin/tests 9d18d74e`)

**`docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref:** `899690bc876fc9b0312dd406ae9cf53bd605ebd5`

### 1. Existing coverage (bible-backed — AST-519 contract)

1. `./scripts/testing/run_component_tests.sh tests/component/core/test_candidate.py::TestAst519ResumeStructureUiHelpers`
2. `./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_candidate.py::TestAst519ResumeStructureApi`
3. `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx -t "structureSections"`

### 2. Revised this pass

4. **`tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx`** — mocks `GET …/resume_structure` (not shapes); asserts orphan `base_resume` key hidden; accent PUT to `artifacts.resume_structure.accent_color`; candidate switch isolation (**§6c** routed page).
5. **`tests/component/ui/api/test_api_candidate.py::TestAst519ResumeStructureApi`** — PUT tests monkeypatch `apply_company_search_terms_save` (AST-524 API path; replaces stale `normalize_company_search_terms_on_save` on module).

### 3. Gaps

None — manifest matches plan AC + **§7.13zzd**.

### Narrowed run (all manifest lines)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst519ResumeStructureUiHelpers \
  tests/component/ui/api/test_api_candidate.py::TestAst519ResumeStructureApi
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  -t "structureSections|Base Resume Content|resume_structure"
```

#### katherine — 2026-06-14T04:03:27.333Z
[qa-handoff] Page tests still mock legacy shapes/accent — update `test_ArtifactsBaseResumeContent.test.tsx` to AST-519 contract (`GET …/resume_structure`, accent PUT to `resume_structure`). API + ArtifactEditor structure tests should pass after Stage 1–2.

`origin/sub/AST-601/AST-616-base-resume-content-ui-rebuild-519` @ `842b6dda`

#### katherine — 2026-06-14T04:00:09.940Z
Plan: [ast-616-admin-api-and-base-resume-content-ui-from-candidate-structure-rebuild-519.md](https://github.com/susansomerset/astral/blob/sub/AST-601/AST-616-base-resume-content-ui-rebuild-519/docs/features/interface/ast-616-admin-api-and-base-resume-content-ui-from-candidate-structure-rebuild-519.md) on `origin/sub/AST-601/AST-616-base-resume-content-ui-rebuild-519` @ `591cc4cd`.

**Self-assessment**
- **Scope:** `Single-Component` — API route/import restore plus `ArtifactsBaseResumeContent.tsx` rewire; core helpers and `ArtifactEditor` structure mode already on branch.
- **Conf:** `Medium` — Rebuild tracks approved AST-519 spec; casualty inventory shows partial merge (missing GET route, page still on global shapes) but JAR already uses structure mode.
- **Risk:** `Medium` — Wrong catalog could hide content or leak orphans; accent path change affects styling until structure backfill (AST-517 shim covers legacy read).

**Casualty highlights:** `GET …/resume_structure` and API imports missing; Base Resume Content page still uses `shapesKey` and `base_resume.accent_color`. Page component tests still assert legacy behavior — Betty qa update called out in plan Stage 3.

---

# Admin API and Base Resume Content UI from candidate structure (Rebuild 519)

**Linear:** https://linear.app/astralcareermatch/issue/AST-616/admin-api-and-base-resume-content-ui-from-candidate-structure-rebuild-519  
**Parent:** https://linear.app/astralcareermatch/issue/AST-601/rebuild-519-git-casualty  
**Publish ref:** `origin/sub/AST-601/AST-616-base-resume-content-ui-rebuild-519`  
**Reference (original ship):** `docs/features/candidate/ast-519-admin-api-and-base-resume-content-ui-from-candidate-structure.md`

**Summary:** Rebuild [AST-519](https://linear.app/astralcareermatch/issue/AST-519) per-candidate **Base Resume Content** behavior lost in git merges. Restore authenticated `GET /api/candidates/<id>/resume_structure`, wire **Base Resume Content** to per-candidate enabled sections (not global `DATA_SHAPES`), load/save `artifacts.base_resume` keyed by section ids with orphan keys stripped on save, and move accent reads/writes to `artifacts.resume_structure.accent_color`. Structure persistence remains **AST-517** (Done on dev); builder/job filtering remains **AST-518**.

---

## Prerequisite gate (before Stage 1)

1. On **`worktree/AST-601`**: `git fetch origin && git merge origin/dev` — merge-clean gate (`BEHIND=0`, `origin/dev` ancestor of `HEAD`).
2. Parent **AST-601** is **In Progress**: `git merge origin/ftr/AST-601-rebuild-519-git-casualty`.
3. Confirm **`origin/sub/AST-601/AST-616-base-resume-content-ui-rebuild-519`** exists; `git merge origin/sub/AST-601/AST-616-base-resume-content-ui-rebuild-519` (empty tip OK).
4. Confirm **AST-517** helpers on disk: `resolve_resume_structure`, `normalize_resume_structure`, `default_resume_structure` in `src/core/candidate.py` — import only; do not re-implement persistence.
5. **Git casualty inventory on merged branch (do not re-plan sibling AST-601 children):**

| Area | Present on branch | Missing / broken |
|------|-------------------|------------------|
| `src/core/candidate.py` | `enabled_resume_structure_sections`, `filter_base_resume_to_structure`, `resolve_resume_structure` | — |
| `src/ui/api/api_candidate.py` | PUT path calls structure helpers for `base_resume` / `resume_structure` merge | **Missing imports** for structure helpers; **no `GET …/resume_structure` route** (PUT would `NameError` when `artifacts` sent without test monkeypatches) |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | `useCandidateResumeStructure`, `structureSections` prop, structure fetch fallback | — (JAR already uses structure mode) |
| `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` | Accent swatch bar | Still uses `shapesKey="base_resume_structure"`; accent reads/writes **`base_resume.accent_color`** (legacy) |
| `tests/component/ui/api/test_api_candidate.py` | `TestAst519ResumeStructureApi` (GET + PUT contract) | Fails until Stage 1 restores GET route + imports |
| `tests/component/frontend/components/test_ArtifactEditor.test.tsx` | Structure-mode tests with `structureSections` | Should pass unchanged after UI wire |
| `tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx` | Basic render + accent save | Still mocks **`/api/shapes/candidates`** and asserts **`base_resume.accent_color`** PUT — **Betty updates in qa-child** to AST-519 contract (see Tests section) |

6. **Out of scope:** `craft_resume_base` schema, `src/core/builder.py`, job `resume_content` filtering (**AST-518**), JAR draft tabs (**AST-553**), global `DATA_SHAPES` template removal.

### Integration contract (AST-517 → AST-616)

**Storage path:** `candidate_data.artifacts.resume_structure`

**Shape:**

```python
{
  "accent_color": "#1A1A2E",  # optional; validated via normalize_resume_structure
  "sections": {
    "<section_id>": {
      "id": "<section_id>",
      "title": "<display title>",
      "enabled": True,
      "order": 0,
      "job_agent_editable": False,
    },
  },
}
```

**Core entry points (import, do not duplicate):**

- `resolve_resume_structure(candidate_data) -> dict`
- `normalize_resume_structure(raw: dict) -> dict`
- `enabled_resume_structure_sections(resolved: dict) -> list[dict]` — `{id, label}` enabled only, sorted by `order` then `id`
- `filter_base_resume_to_structure(content, section_ids) -> dict` — section-id keys only; drops `accent_color`

**Content path:** `artifacts.base_resume` — flat `dict[str, str]` keyed by section id.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_candidate.py` | Add missing imports; register `GET /api/candidates/<id>/resume_structure` before `/<candidate_id>` catch-all; remove duplicate `company_search_terms_*` import lines | ui |
| `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` | Structure-driven tabs via `ArtifactEditor`; accent from structure GET; accent PUT to `resume_structure` | ui |

**Verify only (no functional change expected unless drift):**

| File | Role |
|------|------|
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Structure mode already implemented — confirm `mapFixedFieldsFromRaw` does not add orphan tabs |

**Tests (on dev — engineer does not edit `tests/`):**

| File | Role |
|------|------|
| `tests/component/ui/api/test_api_candidate.py` | `TestAst519ResumeStructureApi` — green after Stage 1 |
| `tests/component/frontend/components/test_ArtifactEditor.test.tsx` | Structure-mode load — green after Stage 2 |
| `tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx` | **Betty (qa-child):** replace shapes/accent mocks with `resume_structure` contract per original AST-519 plan Stage 2 step 7 |

---

## Stage 1: Restore candidate API GET route and PUT imports

**Done when:** Authenticated `GET /api/candidates/<candidate_id>/resume_structure` returns 200 with enabled sections in catalog order plus `accent_color` (string or `null`); missing candidate returns 404; `PUT …/data` with `artifacts.base_resume` no longer raises `NameError` (imports present); `pytest tests/component/ui/api/test_api_candidate.py -q -k resume_structure` passes.

1. In **`src/ui/api/api_candidate.py`**, extend the `from src.core.candidate import (` block to add:
   - `resolve_resume_structure`
   - `normalize_resume_structure`
   - `enabled_resume_structure_sections`
   - `filter_base_resume_to_structure`

2. In the same file, remove the **duplicate** lines importing `company_search_terms_joined_text` and `company_search_terms_lines_for_candidate` (each appears twice today — keep one pair only).

3. In **`src/ui/api/api_candidate.py`**, register **`GET /api/candidates/<candidate_id>/resume_structure`** immediately **after** the `/states` route and **before** `@candidate_bp.route("/<candidate_id>")`:
   - Load candidate via `get_candidate(candidate_id)`; if missing → `404` with `{"error": "Candidate not found: <id>"}`.
   - `cd = candidate.get("candidate_data") or {}`
   - `resolved = resolve_resume_structure(cd)`
   - `sections = enabled_resume_structure_sections(resolved)`
   - `accent = resolved.get("accent_color")`; if not `isinstance(accent, str)` → set `accent = None` (matches `test_get_resume_structure_null_accent_when_not_string`).
   - Return `jsonify({"sections": sections, "accent_color": accent})`.

4. Do **not** change the existing PUT merge logic in `update_candidate_data` except that it now resolves imports from step 1 (behavior unchanged: orphan `base_resume` keys dropped, partial `resume_structure` merged through `normalize_resume_structure`).

⚠️ **Decision:** Orphan keys are **dropped on save** (not 400) — matches original AST-519 and parent AST-601 acceptance criteria.

---

## Stage 2: Wire Base Resume Content UI to per-candidate structure

**Done when:** With a selected candidate, **Base Resume Content** shows one tab per **enabled** structure section in order (labels from structure titles); content loads from `base_resume` by section id without orphan tabs; accent bar reads initial value from `GET …/resume_structure` and saves via `PUT …/data` with `{ artifacts: { resume_structure: { accent_color: "<hex>" } } }`; switching candidates reloads tabs independently.

1. In **`src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx`**, add state:
   ```typescript
   const [structureSections, setStructureSections] = useState<{ id: string; label: string }[] | null>(null)
   ```

2. Replace the accent `useEffect` that calls `GET /api/candidates/${selectedId}` (reads `base_resume.accent_color`) with a structure fetch:
   - When `!selectedId`: `setStructureSections(null)`; `setAccent(null)`; return.
   - `GET /api/candidates/${selectedId}/resume_structure`
   - On success: `setStructureSections(Array.isArray(data.sections) ? data.sections : [])`; `setAccent(normalizeHex(data.accent_color))`
   - On failure: `setStructureSections([])`; `setAccent(null)` (editor shows structure error via empty sections)

3. In **`pickSwatch`**, change PUT body from:
   ```json
   { "artifacts": { "base_resume": { "accent_color": "<hex>" } } }
   ```
   to:
   ```json
   { "artifacts": { "resume_structure": { "accent_color": "<hex>" } } }
   ```
   Keep existing toast success/error handling unchanged.

4. Replace the **`ArtifactEditor`** props:
   - **Remove:** `shapesKey="base_resume_structure"`
   - **Add:** `useCandidateResumeStructure={true}`
   - **Add:** `structureSections={structureSections}` (pass `null` while loading, `[]` on error — editor already handles both)
   - **Keep:** `artifactKey="base_resume"`, `taskKey="craft_resume_base"`, `title="Base Resume Content"`

5. In **`src/ui/frontend/src/components/ArtifactEditor.tsx`**, **read-only verify** (change only if behavior drifted):
   - `mapFixedFieldsFromRaw` builds tabs **only** from `fixedFields` (structure-bound keys) — does not append tabs for orphan keys in stored `base_resume`.
   - If orphans still render, fix by ensuring step 5 in `mapFixedFieldsFromRaw` uses only `fixedFields.map(...)` without iterating extra dict keys (do not add new props).

⚠️ **Decision:** Page owns one structure GET for accent + sections passed into editor — avoids duplicate API calls and keeps accent off the global candidate GET path (same as original AST-519).

---

## Stage 3: Cross-candidate isolation verification

**Done when:** Manual spot-check or existing component tests confirm two candidates with different structure catalogs show different tab sets when switching selection; no code change required if Stage 2 is correct and `ArtifactEditor` resets on `selectedId` change (existing `useEffect` dependency).

1. After Stage 2 commit, run frontend tests Betty delivered:
   ```bash
   cd src/ui/frontend && npm run test -- --run \
     tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx \
     tests/component/frontend/components/test_ArtifactEditor.test.tsx
   ```
2. Run API tests:
   ```bash
   pytest tests/component/ui/api/test_api_candidate.py -q -k resume_structure
   ```
3. If **`test_ArtifactsBaseResumeContent.test.tsx`** still asserts legacy shapes/accent and fails after Stage 2, **stop at Code Complete** — post `[qa-handoff]` on **AST-616** for Betty to update page tests per original AST-519 Stage 2 step 7 (mock `GET …/resume_structure`, assert accent PUT to `resume_structure`, orphan key not visible). Do **not** edit `tests/` in build-child.

---

## Self-Assessment

**Scope:** `Single-Component` — One API module route/import fix and one page component rewire; core helpers and `ArtifactEditor` structure mode already exist on the branch.

**Conf:** `Medium` — Rebuild follows an approved AST-519 plan and existing tests define the contract; casualty inventory shows partial merge (API route missing, page still on global shapes) but patterns are established elsewhere (JAR uses structure mode today).

**Risk:** `Medium` — Incorrect tab catalog could hide legitimate content or show orphans (mitigated by structure-bound tabs and PUT strip); accent path regression affects styling until structure backfill (AST-517 resolve shim still reads legacy `base_resume.accent_color` when blob missing).

---

## ASTRAL_CODE_RULES self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuse AST-517 `resolve_resume_structure` / `normalize_resume_structure`; reuse `ArtifactEditor` structure mode; no second resolver in API or React. |
| §2.1 config | Tab catalog from resolved structure / `default_resume_structure()` — not hardcoded section lists in React. |
| §2.4 batch | N/A |
| §2.6 state machine | N/A |
| §3.3 imports | API imports core only; frontend uses `api()` client. |
| §3.5 naming | No new files; flat `pages/` + `components/`. |

No conflicts requiring `conf-!!-NONE`.

---

## Execution contract (for the developer agent)

- Execute stages in order; one commit per stage on **`worktree/AST-601`**, then publish to **`origin/sub/AST-601/AST-616-base-resume-content-ui-rebuild-519`** per **build-child** §6.
- Do **not** implement structure persistence or `craft_resume_base` schema changes (**AST-517** scope).
- Do **not** change `src/core/builder.py` or job `resume_content` validation (**AST-518**).
- Do **not** edit `tests/` or `docs/ASTRAL_TEST_BIBLE.md` — Betty owns test updates for page contract drift.
- Blocking questions → comment on **AST-601** parent with 🛑 format from **plan-child**.

---

## Review

**Built:** Katherine (build-child)  
**Branch:** `sub/AST-601/AST-616-base-resume-content-ui-rebuild-519`  
**Tip:** `842b6dda` — `code(AST-616)` stages 1–2 (GET route + Base Resume Content structure mode)  
**Status:** Code Complete — awaiting Betty (`qa-child`)

**Note for qa:** `test_ArtifactsBaseResumeContent.test.tsx` still asserts legacy `/api/shapes/candidates` and `base_resume.accent_color` PUT — update to `resume_structure` contract per plan Stage 3.

### Radia review (`origin/dev...origin/sub/AST-601/AST-616-base-resume-content-ui-rebuild-519` @ `26bb967e`)

**What's solid**

- Stage 1: `GET /api/candidates/<id>/resume_structure` registered before the `/<candidate_id>` catch-all; 404 shape, enabled sections via `enabled_resume_structure_sections`, non-string accent → `null` — matches plan and `TestAst519ResumeStructureApi`.
- Stage 1: Core imports restored (`resolve_resume_structure`, `normalize_resume_structure`, `enabled_resume_structure_sections`, `filter_base_resume_to_structure`); duplicate `company_search_terms_*` import lines removed (§1.3 DRY).
- Stage 2: `ArtifactsBaseResumeContent.tsx` fetches structure for tabs + accent, passes `useCandidateResumeStructure` + `structureSections`, accent PUT targets `artifacts.resume_structure.accent_color` — matches acceptance criteria 2–4.
- `ArtifactEditor.tsx` unchanged (verify-only per plan); page tests now mock structure GET, hide orphan keys, assert accent PUT path, candidate switch — Betty manifest §7.13zzd aligned.
- Layer compliance (§3.3): API → core only; frontend uses `api()` client. No §5f debug surfaces touched.

**Issues**

| Severity | Location | Finding |
| --- | --- | --- |
| **fix-now** | `src/data/database.py`, `src/ui/api/api_admin.py` (commit `6e5f2e17`, labeled AST-617) | **Cross-ticket scope (§5d):** Swaps `dispatch_claim_uses_score_floor` → `trigger_state_used_by_scored_dispatch_task` on claim/count/backfill/admin `is_scored` paths. That is **AST-617 / AST-586** dispatch-claim territory, not AST-616. **`origin/dev` already uses `dispatch_claim_uses_score_floor`** on those call sites (see `config.py` docstring: VALID_TITLE input triggers must not score-gate claim). This branch **reverts** the AST-586 fix — qualify on VALID_TITLE would incorrectly apply `score_floor` when merged. Revert both files to match `origin/dev`. |
| **fix-now** | `docs/features/interface/ast-617-dispatch-claim-without-score-floor-valid-title-rebuild-586.md` (deleted on branch) | Sibling **AST-617** plan doc removed; file exists on `origin/dev`. Restore from dev — out of AST-616 scope. |

**Recommended actions**

| Action | Owner | Notes |
| --- | --- | --- |
| Revert `database.py` + `api_admin.py` to `origin/dev` for score-floor helpers | Katherine (`resolve-child`) | Keep only AST-616 files: `api_candidate.py`, `ArtifactsBaseResumeContent.tsx`, tests, bible §7.13zzd, this plan doc |
| Restore deleted AST-617 plan doc from `origin/dev` | Katherine | `git checkout origin/dev -- docs/features/interface/ast-617-dispatch-claim-without-score-floor-valid-title-rebuild-586.md` |
| Re-run §7.13zzd narrowed manifest after revert | Katherine | API + frontend page tests |

---

## Resolution

**2026-06-14 — Katherine (`resolve-child`)**

Addressed Radia **fix-now** @ `be1c3618`:

1. **`src/data/database.py` + `src/ui/api/api_admin.py`** — reverted to `origin/dev` (`dispatch_claim_uses_score_floor` call sites). Removes AST-617/586 cross-ticket delta (commit `6e5f2e17`) that incorrectly swapped score-gate helpers on claim paths.
2. **`docs/features/interface/ast-617-dispatch-claim-without-score-floor-valid-title-rebuild-586.md`** — restored from `origin/dev` (sibling plan doc accidentally deleted on branch).

AST-616 scope unchanged: `api_candidate.py` GET `resume_structure`, `ArtifactsBaseResumeContent.tsx` structure mode, Betty §7.13zzd tests/bible.

**Verify:** §7.13zzd narrowed manifest green post-revert; §9a publish ref merges cleanly into `origin/dev`.
