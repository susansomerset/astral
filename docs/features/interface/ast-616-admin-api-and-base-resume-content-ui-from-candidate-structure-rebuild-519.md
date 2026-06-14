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

*(empty — Radia fills after review-child)*

---

## Resolution

*(empty — Katherine fills after resolve-child)*
