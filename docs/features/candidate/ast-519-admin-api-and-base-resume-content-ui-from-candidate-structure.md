<!-- linear-archive: AST-519 archived 2026-06-15 -->

## Linear archive (AST-519)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-519/admin-api-and-base-resume-content-ui-from-candidate-structure  
**Status at archive:** Done  
**Project:** Astral Candidate  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-477 — Candidate Resume Structure  
**Blocked by / blocks / related:** parent: AST-477; related: AST-518

### Description

## What this implements

Expose per-candidate resume structure via admin/candidate API (`src/ui/api/`) and drive **Base Resume Content** UI: one tab per **enabled** section in catalog order, fields keyed by section ids from the candidate’s structure (not global `DATA_SHAPES["base_resume_structure"]` alone). Editor loads/saves `base_resume` content consistent with structure. No orphan keys in the editor when structure and content disagree.

## Acceptance criteria

2. Base Resume Content shows one tab per enabled section for that candidate, in defined order.
3. When job-level `resume_content` exists, its keys are a subset of the same section ids; builder/UI do not show orphan keys (UI portion — coordinate with [AST-518](https://linear.app/astralcareermatch/issue/AST-518/resume-builder-and-job-artifact-keys-from-candidate-structure) for builder).
4. A second candidate with a different section catalog does not affect the first.

## Boundaries

* Does **not** implement structure persistence or `craft_resume_base` — [AST-517](https://linear.app/astralcareermatch/issue/AST-517/per-candidate-resume-structure-storage-and-craft-resume-base-candidate).
* Does **not** own builder HTML merge — [AST-518](https://linear.app/astralcareermatch/issue/AST-518/resume-builder-and-job-artifact-keys-from-candidate-structure).

## Notes for planning

* `ArtifactsBaseResumeContent.tsx`, `ArtifactEditor.tsx`, `api_candidate.py` / admin shapes endpoints.
* plan-astral: components in `src/ui/frontend/src/` flat per ASTRAL_CODE_RULES.

## Git branch (authoritative)

Parent `ftr/AST-477-candidate-resume-structure`, child `sub/AST-477/<child-segment>`.

### Comments

#### betty — 2026-05-29T00:10:46.042Z
**Betty — rollup bible/test fix (AST-477 sub→ftr unblock)**

Published to `origin/sub/AST-477/AST-519-admin-api-and-base-resume-content-ui-from-candidate-structure` @ `e9ac1a90`.

- **§7.13zl:** single epic section — rows for **AST-517**, **AST-518**, **AST-519** (extends cumulative chain from updated AST-518 sub).
- **`test_candidate.py`:** `TestAst517ResumeStructure`, `TestAst518ResumeStructureProjection`, `TestAst519ResumeStructureUiHelpers` (518 class was missing on sub/519; restored).

`docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref:
```
e1d48e1555a6605a5e3a39ddcc828d65f3ce5804
```

Status unchanged (**User Testing**). Chuckles may retry **rollup-child** AST-519 → ftr after AST-518 rollup.

— Betty

#### radia — 2026-05-28T23:28:16.241Z
**Diff:** `origin/dev...origin/sub/AST-477/AST-519-admin-api-and-base-resume-content-ui-from-candidate-structure` (includes AST-517 merge)

### Plan fidelity
- `GET /api/candidates/<id>/resume_structure` registered **before** `/<id>` — returns enabled sections + accent from `resolve_resume_structure`.
- PUT filters `base_resume` to enabled section ids, merges/normalizes `resume_structure` (including accent-only updates), drives **Base Resume Content** via `useCandidateResumeStructure` + page-owned structure fetch — matches Stages 1–3.
- Frontend accent save targets `artifacts.resume_structure.accent_color` (not `base_resume`) — matches plan Stage 2.

### ASTRAL_CODE_RULES
- **§3.3:** `api_candidate.py` imports core only — good.
- **§3.2 / §3.5:** Tab visibility from server-resolved structure; React renders props — no hardcoded section lists in page — good.
- **§2.1:** Defaults via AST-517 `resolve_resume_structure` / `default_resume_structure` — not duplicate DATA_SHAPES reads in API — good.

### discuss
- **`normalize_company_search_terms_on_save` / `company_search_terms_lines` (`candidate.py` + PUT hook in `api_candidate.py`):** AST-504 scope, not in AST-519 plan — pairs with orphan tests on AST-517/518 publish refs. Confirm intentional carry-over from `dev-kath` or revert and land on AST-504 branch before prep-uat to keep AST-477 diff tight.
- **`filter_base_resume_to_structure` vs AST-518 `filter_content_to_resume_structure`:** PUT path keeps empty-string section values; builder/tracker strip empties — minor inconsistency if orphans are empty strings vs absent keys.

### advisory
- **`ArtifactEditor` structure mode:** When `structureSections={[]}` after fetch error, user sees shape load failure — acceptable; ensure UAT covers candidate with no structure blob yet (should get defaults via API resolve).

#### katherine — 2026-05-28T23:26:21.656Z
[check-linear]

**Session scope:** Parent **AST-477** / Astral Candidate — assigned **AST-519**.

**§0a:** `dev-kath` @ `/Users/susan/chuckles/astral-kath`; `git fetch origin`, `merge origin/dev` — already up to date. Gate: **BEHIND=0**, `origin/dev` ancestor of **HEAD**.

**§0b / §1:** `@katherine` team + Astral Candidate project search; assignee-me in session project (**AST-519**). Full thread on **AST-519** and parent **AST-477** — **0** actionable comments (Chuckles **REVISE** addressed in prior `[check-linear]` @ `422a1404`; Betty QA manifest is informational — ticket already **Tests Passed**).

**Pipeline:** Inbox quiet. **AST-519** awaits **review-astral** (Radia); no engineer stage work from this pass.

#### betty — 2026-05-28T23:20:25.759Z
## QA test manifest (AST-519)

**Publish ref:** `origin/sub/AST-477/AST-519-admin-api-and-base-resume-content-ui-from-candidate-structure` @ `f55fcae5`

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `a655c0005dfe860a8deac067c5072677d73df565`

1. `./scripts/testing/run_component_tests.sh tests/component/core/test_candidate.py::TestAst519ResumeStructureUiHelpers tests/component/core/test_candidate.py::TestAst517ResumeStructure tests/component/ui/api/test_api_candidate.py::TestAst519ResumeStructureApi`

2. `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx`

3. `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx -t "structureSections"`

**Coverage notes:** §6c routed page test mocks `/api/candidates`, `/api/candidates/<id>`, `/api/candidates/<id>/resume_structure`, and `/api/system/ui_config` on first paint. Accent save asserts `artifacts.resume_structure.accent_color` (not `base_resume.accent_color`). Orphan `base_resume` keys are omitted from tabs and stripped on PUT.

**Blocker regression (optional smoke):** AST-517 rows in §7.13zl — item 1 includes `TestAst517ResumeStructure`.

#### katherine — 2026-05-28T23:04:37.322Z
🛑 **Build blocked (prerequisite gate)**

**AST-517** is still **Plan Approved** (not Code Complete). **`origin/sub/AST-477/AST-517-per-candidate-resume-structure-storage-and-craft-resume-base`** has only `docs(AST-517): plan` — no product commits.

After `git fetch`, **`resolve_resume_structure` / `normalize_resume_structure` / `artifacts.resume_structure`** are not present in `src/` on `dev-kath` or the AST-517 ref. AST-519 Stage 1 requires importing those from AST-517; building without them would duplicate persistence logic the plan forbids.

**Unblock:** Ada completes **AST-517** build → **`origin/sub/AST-477/AST-517-...`** carries implementation → re-run **build-astral** on **AST-519** (merge AST-517 ref into `dev-kath` first per plan prerequisite).

Status left at **Plan Approved**.

#### katherine — 2026-05-28T23:02:53.264Z
[check-linear]

Addressed Chuckles **REVISE** (integration contract / blob key mismatch vs **AST-517**):

- **Plan:** `docs/features/candidate/ast-519-admin-api-and-base-resume-content-ui-from-candidate-structure.md`
- **Publish ref:** `origin/sub/AST-477/AST-519-admin-api-and-base-resume-content-ui-from-candidate-structure` @ **`422a1404`**
- **Changes:** Storage path **`artifacts.resume_structure`** everywhere (prerequisite gate, Stages 1–2, tests, accent PUT). Import AST-517 **`resolve_resume_structure()`** / **`normalize_resume_structure()`**; thin **`enabled_resume_structure_sections(resolved)`** only. Removed duplicate `resolve_resume_structure_sections` and direct `DATA_SHAPES` fallback reads. **Revisions** appendix documents this pass.
- **§0a:** `dev-kath` merged with `origin/dev` — BEHIND **0**, ancestor check **ok**.

Ticket stays **Plan Ready** for Chuckles re-validation; did not reset to **Todo** or re-run **plan-astral**.

#### katherine — 2026-05-28T23:02:37.021Z
Plan doc (revision 1): [ast-519-admin-api-and-base-resume-content-ui-from-candidate-structure.md](https://github.com/susansomerset/astral/blob/sub/AST-477/AST-519-admin-api-and-base-resume-content-ui-from-candidate-structure/docs/features/candidate/ast-519-admin-api-and-base-resume-content-ui-from-candidate-structure.md) — commit `422a1404` on publish ref.

**Self-assessment**
- **Scope:** `Single-Component` — candidate API + Base Resume Content UI; thin `enabled_resume_structure_sections` formatter only; imports AST-517 resolve/normalize helpers.
- **Conf:** `Medium` — blocked on AST-517 merge; plan now matches Ada’s `artifacts.resume_structure` blob and `resolve_resume_structure()` contract (no duplicate default logic).
- **Risk:** `Medium` — save-time orphan strip and accent path move; legacy accent read stays in AST-517 resolve shim until regenerate.

Revision 1 addresses Chuckles REVISE: `base_resume_structure` → `resume_structure` everywhere; accent PUT → `artifacts.resume_structure.accent_color`.

#### chuckles — 2026-05-28T23:00:52.050Z
**Verdict: REVISE**

**[fix-now]** — Integration contract § — AST-519 plan uses `artifacts.base_resume_structure` and `GET .../resume_structure` response paths keyed to that name, but **AST-517** (approved) persists **`artifacts.resume_structure`** with `resolve_resume_structure()` / `normalize_resume_structure()`. Update the plan doc (Stages 1–2, tests, accent PUT path) to use **`resume_structure`** everywhere — same blob key, helper names from AST-517 (import/reuse, do not duplicate). API route name `resume_structure` is fine; storage must match Ada’s contract.

— Chuckles

#### katherine — 2026-05-28T22:59:14.008Z
Plan doc: [ast-519-admin-api-and-base-resume-content-ui-from-candidate-structure.md](https://github.com/susansomerset/astral/blob/sub/AST-477/AST-519-admin-api-and-base-resume-content-ui-from-candidate-structure/ast-519-admin-api-and-base-resume-content-ui-from-candidate-structure.md) (path: `docs/features/candidate/ast-519-admin-api-and-base-resume-content-ui-from-candidate-structure.md`, commit `77a280ff` on publish ref).

**Self-assessment**
- **Scope:** `Single-Component` — candidate API + Base Resume Content UI slice only; small core filter helpers; no builder or craft persistence.
- **Conf:** `Medium` — blocked on AST-517 blob contract; plan includes explicit prerequisite gate and DATA_SHAPES fallback so build does not guess Ada’s storage shape.
- **Risk:** `Medium` — save-time orphan stripping and accent path move could hide legacy keys until regenerate; mitigated by structure-bound tabs and documented fallback.

Prerequisite gate: merge `origin/sub/AST-477/AST-517-…` before Stage 1 and verify `artifacts.base_resume_structure` matches the integration contract in the plan.

---

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
