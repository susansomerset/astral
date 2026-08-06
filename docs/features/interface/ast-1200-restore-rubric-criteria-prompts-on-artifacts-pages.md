# Restore rubric criteria prompts on Artifacts pages

**Linear:** [AST-1200](https://linear.app/astralcareermatch/issue/AST-1200/restore-rubric-criteria-prompts-on-artifacts-pages-rubric-criteria)
**Parent:** [AST-1198](https://linear.app/astralcareermatch/issue/AST-1198/rubric-criteria-prompts-are-not-appearing-in-ui-artifacts)
**Publish ref:** `sub/AST-1198/AST-1200-restore-rubric-criteria-prompts`

Operators open Artifacts criteria pages (Job List, Company Watch, Job Description, Meteorite, Get, Do, Like) and see header chrome (title + Generate/Regenerate) without criterion prompt bodies even when the candidate has criteria on file. Restore load + display on the shared `ArtifactEditor` path so those pages show editable criterion prompts when criteria exist, without redesigning nav/chrome or touching consult grading.

Parent Discussion triage (Chuckles): (1) likely — `hydrate_rubric_artifacts_for_response` overwrites GET artifacts from empty `rubric_vector` while the legacy blob still has lists; (2) possible — `.dep-page` `height` + `overflow: hidden` clips `.dep-body`; (3) weaker — expand-one hides textareas until expand (labels should still show). This plan implements (1) and (2); leaves expand-one policy unchanged.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Add blob→table reconcile when current `rubric_vector` rows are missing; call it from hydrate before overlay | core |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Add `dep-page--artifact-editor` modifier class on the page root | ui |
| `src/ui/frontend/src/App.css` | Modifier rules so artifact-editor `.dep-body` / criteria stack cannot collapse to header-only | ui |
| `scripts/migrations/backfill_rubric_vectors.py` | Add `meteorite_jobdesc_rubric` → `evaluate_meteorite` to the artifact→owner map (missing today) | scripts |

No `config.py` edits (`RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY` already lists all seven UI keys). No consult / grade-dot / Manage Tasks changes. No `tests/` edits (Betty owns the test tree).

## Stage 1: Hydrate reconciles legacy blob when `rubric_vector` is empty

**Done when:** For a candidate whose `candidate_data.artifacts.joblist_rubric` (or sibling rubric key) is a non-empty criteria list but `rubric_vector` has **no** `current=1` rows for the matching owner task, `GET /api/candidates/<id>` returns that list under `candidate_data.artifacts.<key>` (not `[]`), and the rows are written into `rubric_vector` so later GETs stay table-backed. When the table already has current rows, hydrate still overlays from the table only (blob ignored). Candidates with neither table rows nor a non-empty blob still get `[]` for that key.

1. In `src/core/candidate.py`, immediately above `hydrate_rubric_artifacts_for_response`, add:

   ```python
   def _legacy_rubric_blob_criteria(arts: dict, artifact_key: str) -> Optional[list]:
       """Return non-empty criteria list from legacy artifacts blob, else None."""
       raw = arts.get(artifact_key) if isinstance(arts, dict) else None
       if not isinstance(raw, list) or len(raw) == 0:
           return None
       usable = [
           item for item in raw
           if isinstance(item, dict) and str(item.get("content") or "").strip()
       ]
       return usable if usable else None


   def ensure_rubric_vectors_table_synced(candidate_id: str, cd: dict) -> None:
       """Import legacy rubric artifact lists into rubric_vector when table has no current rows.

       Mirrors ensure_company_search_terms_table_synced (AST-802): one-way backfill on read,
       then strip imported keys from the persisted artifacts blob so table remains authority.
       """
   ```

   Ensure `Optional` is already imported in `candidate.py` (it is today).

2. Implement `ensure_rubric_vectors_table_synced` body as follows:

   - If `candidate_id` is empty or `cd` is not a dict, return.
   - `arts = cd.get("artifacts")` — if not a dict, return.
   - `stripped: list[str] = []`
   - For each `artifact_key, owner` in `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY.items()`:
     - If `database.list_rubric_vectors(candidate_id, owner, current_only=True)` is non-empty → continue (table already authoritative for this owner).
     - `blob = _legacy_rubric_blob_criteria(arts, artifact_key)` — if `None`, continue.
     - Call `database.sync_rubric_vectors_from_criteria(candidate_id, owner, blob)` inside `try/except ValueError` — on `ValueError` (missing `agent_task`, etc.) **skip that key** (do not raise out of GET). No new logger noise for the skip path.
     - On success, append `artifact_key` to `stripped`.
   - If `stripped` is empty, return.
   - Mutate the in-memory response: `updated_arts = dict(arts)`; `del updated_arts[k]` for each `k in stripped`; `cd["artifacts"] = updated_arts`.
   - Persist strip (same shape as `ensure_company_search_terms_table_synced`):
     - `candidate = get_candidate(candidate_id)` — if missing, return (response overlay already updated).
     - `cd_persist = copy.deepcopy(candidate.get("candidate_data") or {})`
     - `arts_persist = cd_persist.get("artifacts")` — if not a dict, return.
     - `arts_persist = dict(arts_persist)`; delete each `k in stripped` that is present; `cd_persist["artifacts"] = arts_persist`
     - `save_candidate_data(candidate_id, cd_persist, replace=True)` — deep-merge cannot delete nested artifact keys (AST-802).

   ⚠️ **Decision:** Gate on **table emptiness** via `list_rubric_vectors(..., current_only=True)`, **not** on `rubric_criteria_for_task` returning `[]`. `prefilter_company` / `evaluate_jd` / `evaluate_meteorite` merge embedded constants, so `rubric_criteria_for_task` can be non-empty while the table has zero candidate rows — using the merged list as the emptiness check would skip a real blob backfill for those owners.

   ⚠️ **Decision:** Filter blob items to those with non-empty `content` before sync — `sync_rubric_vectors_from_criteria` raises on empty content; skipping empty items avoids failing the whole key when one bad row is present. If no usable items remain, treat as no blob.

   ⚠️ **Decision:** Reconcile + strip on GET (same as company search terms), not a one-off ops-only migration. Staging candidates with blob-but-no-table recover without a separate Railway shell step. Optional `scripts/migrations/backfill_rubric_vectors.py` remains for bulk ops.

3. In `hydrate_rubric_artifacts_for_response`, after ensuring `cd["artifacts"]` is a dict and **before** the overlay loop:

   ```python
   ensure_rubric_vectors_table_synced(candidate_id, cd)
   arts = cd.get("artifacts")
   if not isinstance(arts, dict):
       arts = {}
       cd["artifacts"] = arts
   ```

   Then keep the existing loop:

   ```python
   for artifact_key, owner in RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY.items():
       arts[artifact_key] = rubric_criteria_for_task(candidate_id, owner)
   ```

   Overlay still comes only from `rubric_criteria_for_task` after reconcile — no dual-source read in the UI.

4. Do **not** change `apply_rubric_vectors_save`, consult grading, or `ArtifactEditor` load mapping in this stage. Save path already syncs table and strips blob keys.

## Stage 2: Artifact-editor layout cannot clip criteria to header-only

**Done when:** On an Artifacts criteria page with at least one loaded criterion tab, the criterion collapsible row labels are visible in the viewport under the title/Regenerate header (not clipped to zero-height `.dep-body`). `.dep-page` used by DetailsEditPage / other non-artifact pages keeps existing layout behavior.

1. In `src/ui/frontend/src/components/ArtifactEditor.tsx`, on the root `<div className="dep-page">`, change to:

   ```tsx
   <div className="dep-page dep-page--artifact-editor">
   ```

2. In `src/ui/frontend/src/App.css`, immediately after the existing `.dep-page` block (~line 1107), add:

   ```css
   /* AST-1200: criteria stack must not vanish when % height + overflow:hidden collapses the body */
   .dep-page--artifact-editor {
     height: auto;
     min-height: calc(100% - 40px);
     overflow: visible;
   }

   .dep-page--artifact-editor .dep-body {
     flex: 1 1 auto;
     overflow: visible;
     min-height: 12rem;
   }
   ```

   ⚠️ **Decision:** Modifier class only on `ArtifactEditor` — do not change global `.dep-page` (shared by DetailsEditPage, ProfileTextPage, etc.). Parent scroll remains `.content { overflow-y: auto }`, so a tall criteria stack scrolls with the main content area instead of being clipped inside a zero-flex body.

3. Do **not** change `CollapsiblePanel` expand-one defaults, `resolvedExpandedTabId` initial `""`, or Generate/Regenerate chrome. Criterion **labels** remain visible when collapsed; operators expand a row to edit prompt text (Chuckles triage #3 — weaker; not the fix unless UAT proves labels show and only bodies are “missing”).

## Stage 3: Backfill script includes Meteorite owner

**Done when:** `scripts/migrations/backfill_rubric_vectors.py` maps `meteorite_jobdesc_rubric` → `evaluate_meteorite`, matching `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY`. Dry-run help/docs unchanged aside from the map entry.

1. In `scripts/migrations/backfill_rubric_vectors.py`, in `_ARTIFACT_KEY_TO_TASK_KEY`, add:

   ```python
   "meteorite_jobdesc_rubric": "evaluate_meteorite",
   ```

   next to the existing six artifact keys. Stage 1 hydrate already covers meteorite via config map; this keeps the ops backfill script aligned so bulk `--candidates somerset` imports Meteorite too.

## Manual verify (builder — before Code Complete)

Run against a candidate that reproduces the bug (staging `somerset` or local copy of the AST-1198 dump). Stop and comment on the **parent** if neither path restores criteria.

1. **GET hydrate:** `GET /api/candidates/<id>` → `candidate_data.artifacts.joblist_rubric` length and first item `content` non-empty when blob or table has criteria.
2. **UI:** Artifacts → Job List Criteria shows criterion row label(s) under the header; expand one row → prompt textarea editable; Regenerate still present when content exists.
3. **Sibling keys:** Spot-check Company Watch, Job Description, Meteorite, Get, Do, Like for the same candidate when that key has criteria.
4. **Empty affordance:** Candidate/page with genuinely no criteria still shows the single empty “New Criterion” editor (not a silent pretend-populated page).
5. **Save:** Edit a prompt → wait for autosave / reload → text persists.
6. **CSS:** Computed height of `.dep-body` under `.dep-page--artifact-editor` is not `0` when criteria tabs exist.

## Self-Assessment

**Scope:** `Single-Component` — shared Artifacts criteria wire (core hydrate reconcile + ArtifactEditor layout modifier + backfill map alignment); seven criteria pages share one editor.

**Conf:** `high` — primary path mirrors `ensure_company_search_terms_table_synced`; secondary CSS is a scoped modifier; triage named the exact functions and reproduce checks.

**Risk:** `Medium` — wrong emptiness gate could skip backfill for embedded-merge owners or overwrite table-backed criteria; GET-time `save_candidate_data(replace=True)` must only strip keys that were successfully imported (same footgun class as AST-802).

## Rules check

- §1.3 DRY — one reconcile helper; hydrate calls it; no second blob-read path in React.
- §2.1 / `astral.config.config-source-of-truth` — iterate `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY` only; no hardcoded artifact key set in the new helper.
- `astral.layers.ui-config-driven-business-logic` — restore visibility via server hydrate + thin CSS; no new business rules in React.
- `astral.patterns.require-auth-on-protected-endpoints` — no new endpoints; existing `@require_auth` GET/PUT unchanged.
- §3.3 import direction — core→data for sync/list; UI only className/CSS.
- `astral.ui.frontend-file-placement` — edit existing `ArtifactEditor.tsx` + `App.css`; no new page files.
- `astral.standards.in-scope-only` — no consult, grade-dot, Manage Tasks, or Recommended Job Modal Artifacts tab.
- `astral.git.engineer-test-tree-ban` / `orch.roles.betty-owns-test-tree` — no `tests/` or bible edits in this plan.
- `orch.pipeline.plan-is-bible` — builder follows stages literally; ambiguity → parent comment.

## Out of scope (do not implement)

- Redesign of Artifacts nav, criterion chrome, or Generate/Regenerate UX beyond visibility restore.
- Consult grading, encoded rubric decode, job-list grade-dot displays (AST-1059 family).
- Manage Tasks / admin prompt prose rewrites.
- Inventing criteria for candidates that have none.
- Recommended Job Modal Artifacts tab (job resume / cover letter).
- Changing expand-one / expand-all policy unless Stage 1+2 leave criterion **labels** missing (then stop and comment — do not improvise).
- Engineer-authored tests (Betty).
