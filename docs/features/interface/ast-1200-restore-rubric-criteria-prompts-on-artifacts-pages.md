# Restore rubric criteria prompts on Artifacts pages

**Linear:** [AST-1200](https://linear.app/astralcareermatch/issue/AST-1200/restore-rubric-criteria-prompts-on-artifacts-pages-rubric-criteria)
**Parent:** [AST-1198](https://linear.app/astralcareermatch/issue/AST-1198/rubric-criteria-prompts-are-not-appearing-in-ui-artifacts)
**Publish ref:** `sub/AST-1198/AST-1200-restore-rubric-criteria-prompts`

Operators open Artifacts criteria pages (Job List, Company Watch, Job Description, Meteorite, Get, Do, Like) and see header chrome (title + Generate/Regenerate) without criterion **prompt bodies** even when criteria are already loaded. Restore editable prompt visibility on the shared `ArtifactEditor` rubric path without redesigning nav/chrome or touching consult grading.

**Evidence lock (Joan / DOM capture):** the AST-1198 Original brief shows **Regenerate** and the muted autosave `<span>` (not Cancel/Save). That requires `hasData === true` and `inReview === false` in `ArtifactEditor.tsx` — so GET already returned criteria with non-empty `content`, and AST-901 pending-recovery did not populate the tabs. Empty-`rubric_vector` hydrate overwrite cannot be the cause of this report. Prompt bodies are rendered inside `CollapsiblePanel` with `hidden={!expanded}`, and `resolvedExpandedTabId` starts as `""` (expand-one) — so loaded criteria stay collapsed to chevron + label until click. This plan makes **candidate Artifacts criteria** pages expand-all by default so each prompt is visible/editable on open (AC1). Gate is structural (`!jobPersistence && rubricMode`) — not a hardcoded seven-key set — so Recommended Job Modal job-persistence tabs stay expand-one.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `docs/features/interface/ast-1200-restore-rubric-criteria-prompts-on-artifacts-pages.md` | This plan | docs |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Candidate criteria expand-all (`!jobPersistence && rubricMode`); one-shot seed after load | ui |
| `scripts/migrations/backfill_rubric_vectors.py` | Delete local `_ARTIFACT_KEY_TO_TASK_KEY`; import `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY` from config | scripts |

No `src/core/candidate.py` edits. No `App.css` edits. No `config.py` edits. No consult / grade-dot / Manage Tasks / Recommended Job Modal changes. No `tests/` edits (Betty owns the test tree).

## Stage 1: Candidate criteria expand-all so prompt bodies are visible

**Done when:** On candidate Artifacts criteria pages (Job List / Company Watch / Job Description / Meteorite / Get / Do / Like — all use `ArtifactEditor` **without** `jobPersistence`) for a candidate whose GET returns criteria tabs, opening the page shows every criterion's prompt textarea (not `hidden`) under its label — without requiring a chevron click. Fixed-tab / structure modes and **job-persistence** ArtifactEditor uses (Recommended Job Modal Artifacts) keep today's expand-one behavior. Generate/Regenerate, autosave, collapse-one-stays-collapsed while typing, and empty “New Criterion” affordance still work.

1. In `src/ui/frontend/src/components/ArtifactEditor.tsx`, add:

   ```ts
   import { useSectionExpandPolicy } from "../hooks/useSectionExpandPolicy"
   ```

2. After `rubricMode` / `tabsForRail` are defined, add the **structural** expand-all gate (Joan round=2 — do **not** hardcode rubric artifact keys):

   ```ts
   // Candidate Artifacts criteria only — not job-persistence (Recommended Job Modal).
   const criteriaExpandAll = !jobPersistence && rubricMode

   const criteriaSectionKeys = useMemo(
     () => (criteriaExpandAll ? tabsForRail.map(t => t.id) : []),
     [criteriaExpandAll, tabsForRail],
   )
   const {
     isExpanded,
     onExpandedChange,
     expandAllSections,
     setExpandedKeys,
   } = useSectionExpandPolicy({
     expandAll: criteriaExpandAll,
     sectionKeys: criteriaSectionKeys,
   })
   const didSeedCriteriaExpandRef = useRef("")
   ```

   ⚠️ **Decision:** Gate on `!jobPersistence && rubricMode`, not `rubricMode` alone. `rubricMode` is `!fixedFields` and is also true for job-persistence dict tabs with no `shapesKey` (e.g. Recommended Job Modal `proposed_answers`). Parent Boundaries and this plan's Out of scope forbid that surface. Structural check stays config-neutral (no hardcoded seven-key set in React).

3. Wire `CollapsiblePanel` expand state:

   - Keep `expandedTabId` / `resolvedExpandedTabId` for every path where `criteriaExpandAll` is false (fixedFields / structure / **jobPersistence**).
   - On each `CollapsiblePanel` in the stack:

     ```tsx
     expanded={criteriaExpandAll ? isExpanded(tab.id) : resolvedExpandedTabId === tab.id}
     onExpandedChange={next => {
       if (criteriaExpandAll) onExpandedChange(tab.id, next)
       else if (next) setExpandedTabId(tab.id)
       else setExpandedTabId("")
     }}
     ```

4. One-shot expand-all seed after load (mirror `AdminScheduledActions.tsx` `didAutoOpenSectionRef` — Joan round=2). Do **not** list `criteriaSectionKeys` (array) or an unstable `expandAllSections` identity as the sole re-run trigger without a ref guard:

   ```ts
   useEffect(() => {
     if (!criteriaExpandAll || !loaded) return
     if (criteriaSectionKeys.length === 0) return
     const seedKey = `${selectedId ?? ""}:${artifactKey}`
     if (didSeedCriteriaExpandRef.current === seedKey) return
     didSeedCriteriaExpandRef.current = seedKey
     expandAllSections()
   }, [
     criteriaExpandAll,
     loaded,
     selectedId,
     artifactKey,
     criteriaSectionKeys.length,
     expandAllSections,
   ])
   ```

   ⚠️ **Decision:** Seed once per `(selectedId, artifactKey)` load. Re-calling `expandAllSections()` on every `setTabs` (keystroke) would re-open panels the operator collapsed and fail Manual verify #6. Length in the dep array is only so the first non-empty tab set after load can seed; the ref blocks all later runs for that seed key.

5. When `addCriterionTab` runs and `criteriaExpandAll` is true, after `handleChange`, open the new id without re-seeding the whole stack:

   ```ts
   setExpandedKeys(prev => new Set([...prev, t.id]))
   ```

   Keep existing `setExpandedTabId(t.id)` for the expand-one path (`!criteriaExpandAll`).

6. On `selectedId` / `artifactKey` change, reset seed + keys (single effect; ordering is explicit — this runs, then step 4 may seed the new key):

   ```ts
   useEffect(() => {
     didSeedCriteriaExpandRef.current = ""
     setExpandedKeys(new Set())
     setRailOrderFreeze(null)
   }, [selectedId, artifactKey, setExpandedKeys])
   ```

   Replace/extend the existing `setRailOrderFreeze(null)` effect so there is **one** reset effect for these deps (do not leave two competing effects).

7. Do **not** modify `hydrate_rubric_artifacts_for_response`, `apply_rubric_vectors_save`, or any GET handler. Hydrate stays **read-only** overlay from `rubric_criteria_for_task`.

   ⚠️ **Decision (Joan fix-now / `astral.seed.boot-only-not-hot-path`):** No blob→table insert and no `save_candidate_data` from GET/hydrate. Staging blob-but-no-table recovery remains the existing one-shot `scripts/migrations/backfill_rubric_vectors.py` (Stage 2), not an API hot path.

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
6. **Collapse still works:** Collapse one criterion, type in another — the collapsed panel stays closed (one-shot seed; no re-expand on keystroke).
7. **Boundary:** Open Recommended Job Modal → Artifacts → Application Questions (or any `jobPersistence` ArtifactEditor) — still expand-one (bodies `hidden` until expand); not flipped to expand-all.
8. **Out of scope check:** Do **not** ship CSS changes unless this verify finds `.dep-body` computed height `0` while labels/panels are in the DOM — then stop and comment on the parent (do not invent a clip fix in-stage).

## Self-Assessment

**Scope:** `Single-Component` — shared `ArtifactEditor` criteria expand policy + ops backfill map import; seven candidate criteria pages share one component.

**Conf:** `Medium` — evidence from the ticket DOM capture + expand-one path is strong; round=2 gates (`!jobPersistence`, one-shot ref) remove the prior boundary/re-fire risks from the written steps.

**Risk:** `Medium` — missing the `!jobPersistence` gate would leak expand-all into Recommended Job Modal; missing the seed ref would re-open collapsed panels on every keystroke. Both are called out as literal plan gates above.

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

Revision 2 — 2026-08-06
Driven by: Joan `[plan-discuss] round=2 concern` (plan-rubric.v1 REVISE) — `rubricMode` gate leaks into job-persistence Recommended Job Modal; step 4 effect re-opens collapsed panels on every `setTabs`/keystroke.
Changes: Gate is `criteriaExpandAll = !jobPersistence && rubricMode` (structural, no hardcoded key set). Expand-all seed is one-shot per `(selectedId, artifactKey)` via `didSeedCriteriaExpandRef` (AdminScheduledActions precedent). CollapsiblePanel / add-criterion / reset effects use `criteriaExpandAll`. Manual verify #7 boundary check for job-persistence.

## Review

- **Commit:** `b3e810a4`
- **Branch:** `sub/AST-1198/AST-1200-restore-rubric-criteria-prompts`

### Radia — code-rubric.v1 revision=1

**Overall:** FIX-NOW · **Diff:** `origin/dev...HEAD` (`bb43b7ea`), 9 files — matches plan's Files Changed table exactly.

**Full-set sweep:** 64 active leaf statutes scored in-session (18 universal + 46 scoped); zero `violates`. Straggler check (C4) against the plan's own "Considered but excluded" list: `astral.standards.no-cross-contamination`, `astral.standards.no-hardcoded-sets`, `astral.layers.import-direction`, `astral.ui.naming-conventions`, `astral.git.engineer-test-tree-ban` are all in-diff on layer/path predicates (not `not-applicable` as the plan's exclusion note implies) — all five `conforms` on inspection, no functional issue, just an exclusion-bookkeeping mismatch worth tightening next revision.

**fix-now — stale expand-all seed race survives Joan's round=2 discuss item.** `ArtifactEditor.tsx:156-169`: the `[selectedId, artifactKey]` reset effect (156-160) clears `didSeedCriteriaExpandRef` and fires *before* the candidate-load effect (277+) has called `setLoaded(false)` / refetched. In that gap, the one-shot seed effect (163-169) still sees the *previous* page's stale `loaded === true` and stale `criteriaSectionKeys` (old tab ids), claims the new `seedKey`, and seeds `expandedKeys` from the old tab set. When the real fetch resolves, the ref already matches `seedKey`, so it never re-seeds. Because tab ids are index-based (`v_${i}`), this is silent when the new page has the same-or-fewer criteria and visible (extra criteria stay collapsed) when it has more — an AC1/AC2 miss on the second candidate/page an operator visits with a longer criteria list. This is exactly the race Joan's plan-rubric `APPROVED` verdict flagged as `discuss` and asked to "fold in as you wire step 4" (recommended clearing `didSeedCriteriaExpandRef.current = ""` inside the candidate-load effect next to its `setLoaded(false)`); the fix was not present in the Tests Passed diff, and no component test exercises a page/candidate switch with differing criteria counts. Recommend the one-line ref-clear in the load effect before User Testing.

**Pattern conformance:** `pattern.ui.admin-endpoint`, `pattern.config.config-block` — excluded per plan, confirmed no new admin endpoint / config block in diff.

**What's solid:** clean layer discipline (ui stays ui, scripts import from config not a local dict), DRY reuse of `useSectionExpandPolicy` (no parallel expand machine), structural `!jobPersistence && rubricMode` gate avoids a hardcoded seven-key set in React, and Betty's test/bible coverage tracks every stage precisely.

context_tokens≈95000
— Radia
