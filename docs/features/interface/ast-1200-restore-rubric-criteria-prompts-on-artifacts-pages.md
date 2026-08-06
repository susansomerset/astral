# Restore rubric criteria prompts on Artifacts pages

**Linear:** [AST-1200](https://linear.app/astralcareermatch/issue/AST-1200/restore-rubric-criteria-prompts-on-artifacts-pages-rubric-criteria)
**Parent:** [AST-1198](https://linear.app/astralcareermatch/issue/AST-1198/rubric-criteria-prompts-are-not-appearing-in-ui-artifacts)
**Publish ref:** `sub/AST-1198/AST-1200-restore-rubric-criteria-prompts`

Operators open Artifacts criteria pages (Job List, Company Watch, Job Description, Meteorite, Get, Do, Like) and see header chrome (title + Generate/Regenerate) without criterion **prompt bodies** even when criteria are already loaded. Restore editable prompt visibility on the shared `ArtifactEditor` rubric path without redesigning nav/chrome or touching consult grading.

**Evidence lock (Joan / DOM capture):** the AST-1198 Original brief shows **Regenerate** and the muted autosave `<span>` (not Cancel/Save). That requires `hasData === true` and `inReview === false` in `ArtifactEditor.tsx` — so GET already returned criteria with non-empty `content`, and AST-901 pending-recovery did not populate the tabs. Empty-`rubric_vector` hydrate overwrite cannot be the cause of this report. Prompt bodies are rendered inside `CollapsiblePanel` with `hidden={!expanded}`, and `resolvedExpandedTabId` starts as `""` (expand-one) — so loaded criteria stay collapsed to chevron + label until click. This plan makes rubric-mode criteria **expand-all by default** so each prompt is visible/editable on open (AC1).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `docs/features/interface/ast-1200-restore-rubric-criteria-prompts-on-artifacts-pages.md` | This plan | docs |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Rubric-mode criteria stack uses expand-all; seed all sections open after load | ui |
| `scripts/migrations/backfill_rubric_vectors.py` | Delete local `_ARTIFACT_KEY_TO_TASK_KEY`; import `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY` from config | scripts |

No `src/core/candidate.py` edits. No `App.css` edits. No `config.py` edits. No consult / grade-dot / Manage Tasks changes. No `tests/` edits (Betty owns the test tree).

## Stage 1: Rubric-mode criteria expand-all so prompt bodies are visible

**Done when:** On any Artifacts criteria page (`artifactKey` in the seven rubric keys) for a candidate whose GET returns a non-empty criteria list, opening the page shows every criterion's prompt textarea (not `hidden`) under its label — without requiring a chevron click. Fixed-tab / structure modes (Base Resume, etc.) keep today's expand-one behavior. Generate/Regenerate, autosave, and empty “New Criterion” affordance still work.

1. In `src/ui/frontend/src/components/ArtifactEditor.tsx`, add:

   ```ts
   import { useSectionExpandPolicy } from "../hooks/useSectionExpandPolicy"
   ```

2. After `tabsForRail` is defined, add:

   ```ts
   const rubricSectionKeys = useMemo(
     () => (rubricMode ? tabsForRail.map(t => t.id) : []),
     [rubricMode, tabsForRail],
   )
   const {
     isExpanded,
     onExpandedChange,
     expandAllSections,
     setExpandedKeys,
   } = useSectionExpandPolicy({
     expandAll: rubricMode,
     sectionKeys: rubricSectionKeys,
   })
   ```

3. Replace the expand-one state path for **rubric mode only**:

   - Keep `expandedTabId` / `resolvedExpandedTabId` for **non-rubric** modes (`fixedFields` / structure / job persistence dict) exactly as today.
   - On each `CollapsiblePanel` in the stack:

     ```tsx
     expanded={rubricMode ? isExpanded(tab.id) : resolvedExpandedTabId === tab.id}
     onExpandedChange={next => {
       if (rubricMode) onExpandedChange(tab.id, next)
       else if (next) setExpandedTabId(tab.id)
       else setExpandedTabId("")
     }}
     ```

4. After a successful candidate load that sets rubric tabs (the `else` branch of the candidate `useEffect` that maps `arr` → `setTabs`), when `arr.length > 0`, the next paint must open all sections. Add an effect:

   ```ts
   useEffect(() => {
     if (!rubricMode || !loaded) return
     if (rubricSectionKeys.length === 0) return
     expandAllSections()
   }, [rubricMode, loaded, selectedId, artifactKey, rubricSectionKeys, expandAllSections])
   ```

   ⚠️ **Decision:** Expand-all for **rubric mode only** (not Base Resume fixed tabs). AC1 requires each criterion's **prompt text** visible/editable; expand-one with collapsed bodies fails that wording even when labels show. This is visibility restore, not a nav/chrome redesign — Generate/Regenerate/Save chrome unchanged. No Expand/Collapse bulk chrome required (`showBulkChrome` unused).

5. When `addCriterionTab` runs in rubric mode, after `handleChange` / `setExpandedTabId`, also ensure the new id is open under expand-all:

   ```ts
   setExpandedKeys(prev => new Set([...prev, t.id]))
   ```

   (Keep existing `setExpandedTabId(t.id)` for the non-rubric branch if still used; in rubric mode the policy set is authoritative.)

6. On `selectedId` / `artifactKey` change, clear expand-all keys so a stale set does not flash: existing `useEffect` that `setRailOrderFreeze(null)` — extend it with `setExpandedKeys(new Set())` when `rubricMode`.

7. Do **not** modify `hydrate_rubric_artifacts_for_response`, `apply_rubric_vectors_save`, or any GET handler. Hydrate stays **read-only** overlay from `rubric_criteria_for_task`.

   ⚠️ **Decision (Joan fix-now / `astral.seed.boot-only-not-hot-path`):** No blob→table insert and no `save_candidate_data` from GET/hydrate. Staging blob-but-no-table recovery remains the existing one-shot `scripts/migrations/backfill_rubric_vectors.py` (Stage 2), not an API hot path. The AST-802 company-search-terms reconcile is **not** a carve-out for new seed-on-GET work.

## Stage 2: Backfill script reads owner map from config

**Done when:** `scripts/migrations/backfill_rubric_vectors.py` has no local `_ARTIFACT_KEY_TO_TASK_KEY` dict; it resolves owners via `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY` from `src.utils.config`, so `meteorite_jobdesc_rubric` and any future config keys cannot drift. Dry-run / purge behavior unchanged.

1. In `scripts/migrations/backfill_rubric_vectors.py`:

   - Change the config import to:

     ```python
     from src.utils.config import (
         ASTRAL_CONFIG,
         RUBRIC_CRITERIA_ARTIFACT_KEYS,
         RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY,
     )
     ```

   - **Delete** the entire `_ARTIFACT_KEY_TO_TASK_KEY = { ... }` block.

   - Where the script currently does `task_key = _ARTIFACT_KEY_TO_TASK_KEY.get(artifact_key)`, use:

     ```python
     task_key = RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY.get(artifact_key)
     ```

   - Keep the existing skip path when `task_key` is missing (same as today when the local map lacked a key).

   ⚠️ **Decision:** Import the config map rather than adding a seventh literal — `astral.config.config-source-of-truth`; scripts are layer-exempt (`astral.layers.scripts-exempt-from-layer-rules`) so the import is allowed. This is in-scope ops alignment for the same rubric keys the UI uses, not a new migration feature.

## Manual verify (builder — before Code Complete)

Use a candidate that shows **Regenerate** on Job List Criteria (criteria already loaded). Stop and comment on the **parent** if prompt bodies still stay `hidden` after Stage 1.

1. **GET (sanity):** `GET /api/candidates/<id>` → `candidate_data.artifacts.joblist_rubric` length ≥ 1 with non-empty `content` (confirms data path; not the fix).
2. **UI AC1:** Artifacts → Job List Criteria — each criterion's prompt textarea is visible without clicking chevrons; labels still show; Regenerate still present.
3. **Sibling pages:** Spot-check Company Watch, Job Description, Meteorite, Get, Do, Like when that candidate has criteria for those keys — same expand-all visibility.
4. **Empty affordance:** Candidate/page with genuinely no criteria still shows the single empty “New Criterion” editor (expanded is fine).
5. **Save / Generate:** Edit a prompt → autosave / reload persists; Generate/Regenerate still runs for an eligible state; Cancel/Save review mode after Generate still works.
6. **Collapse still works:** Operator can collapse one criterion under expand-all without forcing all closed (expand-all policy allows per-panel toggle).
7. **Out of scope check:** Do **not** ship CSS changes unless this verify finds `.dep-body` computed height `0` while labels/panels are in the DOM — then stop and comment on the parent (do not invent a clip fix in-stage).

## Self-Assessment

**Scope:** `Single-Component` — shared `ArtifactEditor` rubric expand policy + ops backfill map import; seven criteria pages share one component.

**Conf:** `Medium` — evidence from the ticket DOM capture + `ArtifactEditor` expand-one path is strong for Stage 1; Conf is not `high` because staging UAT still has to confirm labels-only vs fully blank chrome, and Chuckles' hydrate hypothesis remains a separate ops concern (backfill script), not this UI fix.

**Risk:** `Medium` — wrong expand wiring could leave fixed-tab modes on expand-all, or fail to re-expand after candidate switch; backfill import mistake could skip owners if the wrong config symbol is used.

## Rules check

- `astral.seed.boot-only-not-hot-path` — hydrate/GET stay read-only; no auto-insert from API.
- `astral.config.config-source-of-truth` — backfill script consumes `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY`.
- `astral.layers.ui-config-driven-business-logic` — no new React business rules for load/source; display expand policy only.
- `astral.patterns.require-auth-on-protected-endpoints` — no new endpoints.
- `astral.ui.frontend-file-placement` — edit existing `ArtifactEditor.tsx` + existing hook; no new page files.
- `astral.standards.in-scope-only` / `astral.standards.dry-and-focused-functions` — reuse `useSectionExpandPolicy`; no parallel expand state machine.
- `astral.git.engineer-test-tree-ban` / `orch.roles.betty-owns-test-tree` — no `tests/` or bible edits.
- `orch.pipeline.plan-is-bible` — builder follows stages literally; ambiguity → parent comment.

## Out of scope (do not implement)

- GET-time / hydrate-time blob→table reconcile or any `save_candidate_data` from `get_candidate_detail` (Joan fix-now; needs Archie/Susan if ever required).
- Speculative `.dep-page` / `.dep-body` CSS clip fix without verified height `0` (Joan discuss).
- Redesign of Artifacts nav, Generate/Regenerate UX, or adding Expand/Collapse bulk chrome.
- Consult grading, encoded rubric decode, job-list grade-dot displays (AST-1059 family).
- Manage Tasks / admin prompt prose; inventing criteria for empty candidates.
- Recommended Job Modal Artifacts tab.
- Engineer-authored tests (Betty).

## Revisions

Revision 1 — 2026-08-06
Driven by: Joan `[plan-discuss] round=1 concern` (plan-rubric.v1 REVISE) — seed-on-GET statute violation; Stage 1 premise contradicted by Regenerate DOM evidence; AC1 unmapped while expand-one left out of scope; Stage 2 CSS unproven; Stage 3 local map duplicates config.
Changes: Dropped hydrate write path and speculative CSS. Primary Stage 1 is rubric-mode expand-all via `useSectionExpandPolicy`. Stage 2 imports `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY` into the backfill script. Files Changed includes this plan doc. Conf lowered to Medium.
