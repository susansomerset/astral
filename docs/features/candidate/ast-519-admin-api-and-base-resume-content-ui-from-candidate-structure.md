# AST-519: Admin API and Base Resume Content UI from candidate structure

**Linear:** [AST-519](https://linear.app/astralcareermatch/issue/AST-519/admin-api-and-base-resume-content-ui-from-candidate-structure) (child of [AST-477](https://linear.app/astralcareermatch/issue/AST-477/candidate-resume-structure))

**Feature ref:** `sub/AST-477/AST-519-admin-api-and-base-resume-content-ui-from-candidate-structure` on `origin` (parent integration: `ftr/AST-477-candidate-resume-structure`)

**Summary:** Expose a resolved per-candidate resume section catalog through the candidate API and drive **Base Resume Content** tabs from that catalog (enabled sections only, catalog order). Load and save `artifacts.base_resume` content keyed by section ids; strip keys that are not in the candidate structure so the editor never shows orphan tabs or persists orphan fields. Move accent color reads/writes from `artifacts.base_resume.accent_color` to structure (`artifacts.resume_structure.accent_color`). Structure **persistence** and `craft_resume_base` changes remain **AST-517**; builder/job orphan handling remains **AST-518**.

---

## Prerequisite gate (before Stage 1)

AST-519 is **blocked by [AST-517](https://linear.app/astralcareermatch/issue/AST-517)** in Linear. Before any product code:

1. **`git fetch origin`** and merge **`origin/sub/AST-477/AST-517-per-candidate-resume-structure-storage-and-craft-resume-base`** into **`dev-kath`** (after **`origin/dev`** sync per build-astral).
2. Confirm **`candidate_data.artifacts.resume_structure`** exists on disk with the **Integration contract** shape below (read **`src/core/candidate.py`** after AST-517 merge — import **`resolve_resume_structure`** and **`normalize_resume_structure`**; do not re-implement persistence or default resolution).
3. If the blob key, field names, or section record shape differ from this contract, **stop** and post on **AST-477** parent using the execution-contract format in this plan (do not guess).

### Integration contract (AST-517 → AST-519)

**Storage path:** `candidate_data.artifacts.resume_structure`

**Shape** (matches AST-517 approved plan):

```python
{
  "accent_color": "#1A1A2E",  # optional; validated via normalize_resume_structure / BUILD_CONFIG accent_palette
  "sections": {
    "<section_id>": {
      "id": "<section_id>",           # stable string, same as dict key
      "title": "<display title>",     # tab label in UI
      "enabled": True,                # bool; disabled sections omitted from editor tabs
      "order": 0,                     # int; ascending sort for tab rail
      "job_agent_editable": False,    # AST-517 flag; contact trio false — UI shows all enabled sections regardless
    },
    # ... one entry per section in catalog (id-keyed dict, not a list)
  },
}
```

**Core entry point (AST-517 — import, do not duplicate):**

- **`resolve_resume_structure(candidate_data: dict) -> dict`** — returns normalized structure from `artifacts.resume_structure`, or `default_resume_structure()` with legacy accent shim from `artifacts.base_resume.accent_color` when blob missing.
- **`normalize_resume_structure(raw: dict) -> dict`** — validate on accent-only PUT merges.

**Content path:** `candidate_data.artifacts.base_resume` — flat `dict[str, str]` keyed by **section id** only. No `accent_color` on content after this ticket (accent lives on structure per AST-477 Q5). Legacy `base_resume.accent_color` is read only inside AST-517’s resolve shim until regenerate.

**Legacy read shim:** AST-519 does **not** read global `DATA_SHAPES["candidates"]["detail"]["base_resume_structure"]` directly — **`resolve_resume_structure`** already falls back to `default_resume_structure()` (built from that global template in AST-517 config). UI and API consume only the resolved structure.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Add `enabled_resume_structure_sections(resolved: dict) -> list[dict]` and `filter_base_resume_to_structure(content, section_ids) -> dict` (import `resolve_resume_structure` from AST-517; do not add a second resolver) | core |
| `src/ui/api/api_candidate.py` | `GET .../resume_structure`; normalize `artifacts.base_resume` on PUT; validate accent on structure merge via `normalize_resume_structure` | ui |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Optional `useCandidateResumeStructure` mode: fetch per-candidate sections instead of `/api/shapes/candidates` | ui |
| `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` | Wire structure mode; accent from/save to `resume_structure` path | ui |
| `tests/component/ui/api/test_api_candidate.py` | Tests for `resume_structure` GET and base_resume key filtering on PUT | tests |
| `tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx` | Mock structure endpoint; assert tabs, accent path, no orphan display | tests |
| `tests/component/frontend/components/test_ArtifactEditor.test.tsx` | Add one test for `useCandidateResumeStructure` load/save key filter (only if props added) | tests |

---

## Stage 1: Core helpers and candidate API

**Done when:** Authenticated clients can `GET /api/candidates/<candidate_id>/resume_structure` and receive enabled sections in order plus accent; `PUT /api/candidates/<id>/data` with `artifacts.base_resume` persists only keys allowed by that candidate’s structure (orphan keys dropped before merge).

1. In **`src/core/candidate.py`**, import **`resolve_resume_structure`** from AST-517 (already on disk after prerequisite merge). Add **`enabled_resume_structure_sections(resolved: dict) -> list[dict]`**:
   - Input `resolved` is the return value of **`resolve_resume_structure(candidate_data)`** — do not read `artifacts` directly in this helper.
   - From `resolved["sections"]` (dict keyed by section id), collect entries where `enabled` is true.
   - Return a **list** of `{"id": str, "label": str}` using each section’s `id` and `title`, sorted by `order` ascending, then by `id` for ties.
   - Do not mutate `resolved`.

2. In the same file, add **`filter_base_resume_to_structure(content: dict, section_ids: set[str]) -> dict`**:
   - Input `content` must be treated as a dict (if not dict, return `{}`).
   - Return `{k: str(v) for k, v in content.items() if k in section_ids}` — drop `accent_color` and any other non-section keys.
   - Do not add keys that are not in `content`.

3. In **`src/ui/api/api_candidate.py`**, register **`GET /api/candidates/<candidate_id>/resume_structure`** **before** the `/<candidate_id>` catch-all (same pattern as `/states`):
   - Load candidate via `get_candidate`; 404 if missing.
   - `resolved = resolve_resume_structure(cd)`
   - `sections = enabled_resume_structure_sections(resolved)`
   - `accent = resolved.get("accent_color")` — return as JSON string or `null` if absent (already normalized by resolve).
   - Response: `{"sections": sections, "accent_color": "<hex>|null"}`.

4. In **`update_candidate_data`**, when `body.get("artifacts")` is a dict:
   - Load current candidate `cd`.
   - `resolved = resolve_resume_structure(cd)`
   - `section_ids = {s["id"] for s in enabled_resume_structure_sections(resolved)}`
   - If `"base_resume"` present and is a dict: replace `arts["base_resume"]` with `filter_base_resume_to_structure(arts["base_resume"], section_ids)`.
   - If PUT includes `artifacts.resume_structure` (partial merge): merge onto existing `artifacts.resume_structure` from disk, then call **`normalize_resume_structure(merged)`** — on `ValueError`, return 400 with message `"invalid resume_structure"` or `"invalid accent_color"` as appropriate.
   - Keep existing `normalize_rubric_artifacts_on_save` / `normalize_company_search_terms_on_save` calls after filtering.

5. In **`tests/component/ui/api/test_api_candidate.py`**, add:
   - **`test_get_resume_structure_returns_enabled_ordered_sections`**: monkeypatch `get_candidate` with custom `artifacts.resume_structure.sections` (three ids, one disabled); GET `/api/candidates/c1/resume_structure` → 200, two sections in order, labels match titles.
   - **`test_get_resume_structure_uses_resolve_default_when_blob_missing`**: no `resume_structure` blob → sections match `default_resume_structure()` enabled count and order (monkeypatch or import default from config).
   - **`test_put_base_resume_strips_orphan_keys`**: PUT body with extra key `orphan_section`; assert `save_candidate_data` receives filtered dict (monkeypatch capture).

⚠️ **Decision:** Orphan keys are **dropped on save** (not rejected with 400) so autosave in the editor self-heals legacy content without blocking the user. UI never displays orphans; silent strip matches acceptance “no orphan keys in the editor.”

---

## Stage 2: Base Resume Content UI and ArtifactEditor structure mode

**Done when:** With a selected candidate, Base Resume Content shows one collapsible tab per **enabled** structure section in order; content loads from `base_resume` by section id; Save/autosave sends only structure keys; accent bar reads/writes `artifacts.resume_structure.accent_color`; switching candidate reloads tabs independently (candidate B’s catalog does not affect candidate A).

1. In **`src/ui/frontend/src/components/ArtifactEditor.tsx`**, add optional prop **`useCandidateResumeStructure?: boolean`** (default `false`). When `true`:
   - Ignore `shapesKey` for tab definitions (do not call `/api/shapes/candidates` for fields).
   - On `selectedId` change, `GET /api/candidates/${selectedId}/resume_structure`; on failure set `shapeError` true (same UX as shapes failure).
   - Set `shapeFields` from response `sections` mapped to `{ key: id, label }`.
   - Keep existing fixed-tab behavior: non-editable tabs, Save/Cancel, Generate maps `parsed` dict keys to `fixedFields` keys only (ignore extra keys in agent response).

2. In the artifact load `useEffect` (fixed fields branch):
   - When normalizing legacy array saved as `[{label, content}]`, map label → key via `fixedFields` as today.
   - After building tabs from `fixedFields`, **do not** add tabs for keys present in `base_resume` but not in structure (orphans omitted from UI).
   - Empty string for missing keys.

3. In **`buildPayload`** for fixed fields: only include `tab.id` keys from current tabs (already structure-bound); no change to rubric branch.

4. In **`src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx`**:
   - Remove `shapesKey="base_resume_structure"` from `ArtifactEditor`.
   - Pass **`useCandidateResumeStructure={true}`**, keep `artifactKey="base_resume"`, `taskKey="craft_resume_base"`.
   - Replace accent load: from `GET /api/candidates/${selectedId}/resume_structure` field `accent_color`.

   **Concrete approach:** Page `useEffect` calls `/api/candidates/${selectedId}/resume_structure`, sets `accent` from `accent_color`. Pass to `ArtifactEditor` new optional props: **`structureSections?: { id: string; label: string }[] | null`** — when provided, editor skips its own structure fetch and uses prop. Page passes sections from same GET.

5. Accent save in page **`pickSwatch`**: change PUT body to  
   `{ artifacts: { resume_structure: { accent_color: up } } }`  
   (remove `artifacts.base_resume.accent_color`).

6. Update **`ArtifactEditor`** to accept **`structureSections?: { id: string; label: string }[] | null`**: when `useCandidateResumeStructure && structureSections`, use prop instead of fetching; when prop null and loading, show Loading; when `useCandidateResumeStructure && !structureSections && !shapeError`, fetch as in step 1 fallback.

7. In **`tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx`**:
   - Mock `GET /api/candidates/c1/resume_structure` with two enabled sections and accent.
   - Mock `base_resume` dict with three keys including one orphan; assert only two tabs / two fields visible.
   - Assert accent PUT targets `resume_structure.accent_color`, not `base_resume`.

⚠️ **Decision:** Page owns one structure GET for accent + sections passed into editor to avoid duplicate API calls and keep accent bar off the global candidate GET path.

---

## Stage 3: Cross-candidate isolation and component test

**Done when:** Component tests pass; manual spot-check confirms two candidates with different structure mocks show different tab sets when switching selection in the candidate picker.

1. In **`test_ArtifactsBaseResumeContent.test.tsx`**, add test **`second candidate different sections`**: mock candidates list with `c1` and `c2`; structure endpoint returns different section lists per id; switch selection (fire candidate context change if test-utils support, or re-render with updated mock); assert tab labels differ.

2. In **`test_ArtifactEditor.test.tsx`**, add minimal test: render with `useCandidateResumeStructure`, `structureSections={[{id:"a",label:"A"}]}`, mock candidate with `base_resume: { a: "x", orphan: "y" }` → only `"x"` visible, no orphan field.

3. Run frontend tests: `cd src/ui/frontend && npm run test -- --run tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx tests/component/frontend/components/test_ArtifactEditor.test.tsx`

4. Run API tests: `pytest tests/component/ui/api/test_api_candidate.py -q`

---

## Self-Assessment

**Scope:** `Single-Component` — Touches candidate API, two frontend files, and small core filter/format helpers; all in the Base Resume Content vertical slice, no builder or craft task persistence.

**Conf:** `Medium` — Depends on AST-517’s `resolve_resume_structure` / `normalize_resume_structure` (explicit gate); UI pattern reuses existing `ArtifactEditor` fixed-tab mode; no duplicate default-resolution logic in this ticket.

**Risk:** `Medium` — Incorrect key filtering could hide legitimate content or leave stale orphans in DB (mitigated by structure-bound tabs and save-time strip); accent path change could break existing candidates until structure backfill (AST-517 resolve shim reads legacy `base_resume.accent_color` until regenerate).

---

## ASTRAL_CODE_RULES self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuse AST-517 `resolve_resume_structure` / `normalize_resume_structure`; `ArtifactEditor` fixed-tab path; core helpers shared by GET and PUT. |
| §2.1 config | Default/fallback via AST-517 `default_resume_structure()` — not hardcoded lists in React or duplicate DATA_SHAPES reads in API. |
| §2.4 batch | N/A — no batch processing. |
| §2.6 state machine | N/A — no state transitions. |
| §3.3 imports | API imports core only; frontend uses `api()` client. |
| §3.5 naming | Components stay flat in `components/` and `pages/`; no new CSS file. |

No conflicts requiring `conf-!!-NONE`.

---

## Execution contract (for the developer agent)

- Execute stages in order; one commit per stage on `dev-kath`, cherry-pick publish per **build-astral**.
- Do **not** implement structure persistence, default templates, or `craft_resume_base` schema changes (**AST-517**).
- Do **not** change `src/core/builder.py` or job `resume_content` validation (**AST-518**).
- Do **not** remove global `DATA_SHAPES["base_resume_structure"]` — still used as AST-517 default template source; only stop using it as the **primary** tab driver in Base Resume Content.
- Blocking questions → comment on **AST-477** parent with 🛑 format from **plan-astral**.

---

## Revisions

Revision 1 — 2026-05-28  
Driven by: Chuckles REVISE — "AST-519 plan uses `artifacts.base_resume_structure` … but AST-517 persists **`artifacts.resume_structure`** with `resolve_resume_structure()` / `normalize_resume_structure()`."  
Changes: Renamed storage path to `artifacts.resume_structure` throughout (integration contract, prerequisite gate, Stages 1–2, tests, accent PUT). Replaced custom `resolve_resume_structure_sections` with import of AST-517 `resolve_resume_structure` plus thin `enabled_resume_structure_sections(resolved)` formatter. Accent validation defers to `normalize_resume_structure`. Removed direct DATA_SHAPES fallback reads — resolve helper owns defaults.

---

## Review

**Built:** Katherine (build-astral)  
**Branch:** `sub/AST-477/AST-519-admin-api-and-base-resume-content-ui-from-candidate-structure`  
**Status:** Code Complete — awaiting Betty (`qa-astral`)

---

## Resolution

**Katherine** (`resolve-astral`, 2026-05-28): Radia **fix-now** list empty.

| Finding | Action |
|---------|--------|
| **discuss** — `normalize_company_search_terms_on_save` / AST-504 carry-over | **No change.** Plan Stage 1 step 4 explicitly keeps existing PUT normalization hooks; helpers live on `origin/dev` from **AST-504**, not new AST-519 scope. |
| **discuss** — `filter_base_resume_to_structure` vs AST-518 empty-string strip | **Deferred to AST-518.** Base-resume PUT intentionally retains empty-string section values for editor autosave self-heal; builder/job content filtering is AST-518’s contract. |
| **advisory** — `structureSections={[]}` after fetch error | **UAT note.** Default structure via `resolve_resume_structure` when blob missing; manual UAT should cover candidate with no `resume_structure` blob. |

**Verification:** Betty manifest green on publish ref; §9a dry-run clean vs `origin/dev` and `origin/ftr/AST-477-candidate-resume-structure`. Publish tip unchanged for product: `origin/sub/AST-477/AST-519-admin-api-and-base-resume-content-ui-from-candidate-structure` @ `f55fcae5`.
