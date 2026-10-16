# AST-2043 — Artifact Edit Enhancements

<!-- linear-archive: AST-2043 archived 2026-10-16 -->

## Linear archive (AST-2043)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2043/artifact-edit-enhancements  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 8  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-2046

### Description

## Purpose

Every artifact and rubric edit already writes version rows, but the operator can't see them. Autosave also fires every 2 seconds while typing, so the history fills up with keystroke-level noise. This epic makes that history usable. Back and forward arrows move the *current* version along the chronological list, like undo/redo through saved history. A new version is saved only when a field loses focus, so each version is one meaningful edit. Stepping back and then editing never rewrites history: the edit is appended as the newest version, and the "abandoned" later versions stay in the list.

## Functional scope

1. **Save on blur, not on a timer.** In editors that autosave today (Base Resume Content sections, the six Criteria pages), a version is saved when a field loses focus and its text changed. The 2-second typing timer goes away. Leaving the page with unsaved changes still saves, as today. Editors that already use an explicit Save button (job Cover Letter, the seven profile context pages) keep it, and each Save is one version. No time-based coalescing and no in-place body updates: every saved change is a new version row.
2. **Unchanged saves add nothing.** A blur or Save whose body is identical to the current version writes no row. This covers candidate keys (already true), job catalog keys, and rubric vectors (already fingerprint-gated).
3. **Version arrows on artifacts.** Each editor for a catalog artifact shows back/forward arrows and a position indicator (e.g. "3 of 7"). This covers Base Resume Content, Job Resume, Cover Letter, and the seven profile context pages. Back is disabled on the oldest version and forward on the newest. On Base Resume Content the arrows step `base_resume` only, and `resume_structure` has no arrows.
4. **Version arrows on rubric criteria.** On the six Criteria pages, each criterion gets its own arrows that step that criterion's content history (its `rubric_vector` rows sharing a code). Importance is not versioned.
5. **Arrows move the current version.** An arrow makes the chronologically previous or next row the current one, so every consumer of "current" (editors, prompt tokens, print, job builds, grading) sees it. Unsaved edits are saved before the move, and the editor reloads to show the moved-to version.
6. **Edits after moving back append, never fork.** An edit made after stepping back saves as a brand-new version at the end of the list. The later versions stay in place, in chronological order.
7. **Out of scope:** Company Search Terms (keeps its current save behavior and storage), and the JAR Application Questions tab (agent-recommended responses, not an artifact: keeps its existing pin/blob storage and gets no arrows).

## Component scope

* `src/data/database.py` — **modified** — move-current primitives for `artifact` rows and for `rubric_vector` rows, plus chronological history listing for one rubric criterion.
* `src/core/candidate.py` — **modified** — list versions / set current version for candidate catalog keys and for one rubric criterion.
* `src/core/tracker.py` — **modified** — list versions / set current version for job catalog keys. Identical-to-current no-op in `save_job_artifact`.
* `src/ui/api/api_candidate.py` — **modified** — new authenticated routes: version list + set-current for candidate catalog keys and for a rubric criterion.
* `src/ui/api/api_jobs.py` — **modified** — new authenticated routes: version list + set-current for job catalog keys.
* `src/ui/frontend/src/components/ArtifactVersionNav.tsx` — **new** — shared back/forward arrows + position indicator control.
* `src/ui/frontend/src/components/ArtifactEditor.tsx` — **modified** — blur-save replaces the autosave timer. Artifact-level nav for catalog keys, per-criterion nav in rubric mode. Flush unsaved edits before a move, reload after.
* `src/ui/frontend/src/components/ContextTextPage.tsx` — **modified** — artifact-level nav for the seven `candidate.context.*` pages, and reload after a move.

## Technical scope

* `database.py`: a new function that moves `current=1` to a named `artifact_uuid` within its natural key `(entity_type, entity_id, artifact_type)`, in one transaction. It rejects a uuid from another key and never touches `artifact_data`. A twin function does the same for `rubric_vector` within `(candidate_id, task_key, code)`. Rubric criterion history is listed oldest `created_at` first, either through a new function or an extension of `list_rubric_vectors` (which currently sorts by code). Artifact history reuses `list_artifacts`.
* `candidate.py`: list-versions (uuid, created_at, current, position) and set-current functions for candidate catalog keys, with `ARTIFACT_CONFIG` resolution matching `get_candidate_current`. The same pair for one rubric criterion, resolving the owner task via `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY`. Saves after a move need no change: retire+insert (artifacts) and fingerprint retire+insert (`sync_rubric_vectors_from_criteria`) already append at the end.
* `tracker.py`: list-versions / set-current for job catalog keys, mirroring `get_job_current`. `save_job_artifact` gains the identical-to-current no-op (`patt.artifact.write-operative` Implementation #4).
* `api_candidate.py` / `api_jobs.py`: new routes use `@require_auth`, return 400 for unknown or non-versioned keys and for a uuid outside the key, and 404 for a missing entity.
* `ArtifactVersionNav.tsx`: presentational control (props: position, total, onBack, onForward, disabled).
* `ArtifactEditor.tsx`: remove `AUTOSAVE_MS` and the debounce timer. Save on field blur when dirty, keeping the existing unmount save and the "no silent save while reviewing Generate" rule. Fetch version lists on load and after each save, render the nav, call set-current, then re-run the existing GET hydrate.
* `ContextTextPage.tsx`: the same nav fetch / move / reload. Its explicit Save stays.

## Architectural definition

**Patterns to reuse**

* [`patt.artifact.write-operative`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.artifact.write-operative.md>) — every saved change is a retire+insert, with no in-place body UPDATE. The job wrapper adopts the identical-to-current no-op (pattern Open decision #3, resolved yes for this epic).
* [`patt.artifact.read-current`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.artifact.read-current.md>) — after an arrow move, editors re-hydrate through the existing current-read GET.
* [`patt.artifact.read-operative`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.artifact.read-operative.md>) — moving `current` never alters a row body, so existing pins keep resolving to the body as it was.
* [`patt.artifact.traceability`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.artifact.traceability.md>) — set-current never edits `source_artifact_ids`. An edit after stepping back inserts through the normal write path.
* [`patt.artifact.ui-consistency`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.artifact.ui-consistency.md>) — one shared nav control for every editor surface, with no per-key forks.

**New patterns proposed**

* none. Version listing and set-current sit inside the read-current / write-operative arc.

**Applicable statutes**

* [`stat.logging.error`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>) — new API routes log a caught exception once, at the handler.
* [`stat.logging.info.api`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md>) — set-current routes log progress once, at the completing route.
* [`stat.logging.info.entity`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md>) — core set-current events use the id-pipe entity log format.

## Acceptance criteria

1. **Blur saves exactly one version.** On Base Resume Content, type 20+ characters into one section without leaving it. `list_artifacts("candidate", <id>, "base_resume")` row count is unchanged while typing. After blur it grows by exactly 1. *Fail:* growth before blur, or more than 1 after.
2. **Unchanged blur saves nothing.** Focus a section and blur it without editing. The row count is unchanged. Repeat on a Criteria page: `list_rubric_vectors(<id>, <task>, current_only=False)` count is unchanged. *Fail:* any growth.
3. **Timer is gone.** `git grep -n "AUTOSAVE_MS" -- src/ui/frontend/src/components/ArtifactEditor.tsx` returns nothing. *Fail:* any match.
4. **Back arrow moves current.** With versions v1, v2, v3 (v3 current), set-current to v2. `get_current_artifact` returns v2's uuid, exactly one row for the key has `current=1`, and no row count or body changed. *Fail:* zero or two current rows, a new row, or a body change.
5. **Edit after back appends.** From #4, save body Z. v4 is created with `created_at` greater than v3's and is current. v2 and v3 are unchanged, and the order is v1, v2, v3, v4. *Fail:* v2 or v3 body changed, or no new row.
6. **Rubric criterion steps alone.** Save criterion V01 with content A, then B (two blurs). Set-current V01 to A's `rubric_vector_uuid`. `list_rubric_vectors(<id>, <task>)` returns A's uuid for V01, exactly one current row per code, and every other code's current uuid is unchanged. *Fail:* other codes changed, or V01 has 0 or 2 current rows.
7. **Cross-key guard.** Set-current with a uuid from a different artifact key, entity, or rubric code returns 400, and current is unchanged. *Fail:* 200 or a current change.
8. **Job identical no-op.** PUT the same cover letter body twice to `/api/jobs/<id>/artifacts/cover_letter`. `list_artifacts("job", <id>, "cover_letter")` grows by 1, not 2. *Fail:* 2.
9. **UI arrows.** On Base Resume Content, JAR Cover Letter, Bio Summary, and one criterion on Do Job Criteria: back is disabled at 1 of N, forward is disabled at N of N, and pressing back shows the previous body with the indicator reading N-1 of N. *Fail:* body unchanged, wrong indicator, or arrows missing on any listed surface.

## Open questions

**Resolved (round 1, Susan):** no time-based window. Versions save on blur. Scope = catalog artifacts + rubric_vector content, Company Search Terms exempt. The `write-operative` amendment is moot because there are no in-place updates.

**Resolved (round 2, Susan):** Application Questions (recommended responses) are not artifacts, so no port and no backfill. The write-source marker column is dropped.

**Resolved (round 3, Susan):** Application Questions tab stays as it is — no code change (not a hot topic).

None open.

## Proposed child tickets

#### 1!!: **Versioning: data/core - Ada**

Ships all backend behavior: the move-current primitives and history listing for artifacts and rubric criteria, plus the job identical no-op. Does not own HTTP routes (#2) or UI (#3).
**Citations:** `patt.artifact.write-operative`, `patt.artifact.read-current`, `patt.artifact.read-operative`, `patt.artifact.traceability`, `stat.logging.info.entity`.
**Scope:** `src/data/database.py` — move-current primitives for `artifact` rows and for `rubric_vector` rows, plus chronological history listing for one rubric criterion. `src/core/candidate.py` — list versions / set current version for candidate catalog keys and for one rubric criterion. `src/core/tracker.py` — list versions / set current version for job catalog keys. Identical-to-current no-op in `save_job_artifact`.
Estimate: 3

#### 2!: **Version API routes - Hedy**

After #1. Version list / set-current routes for candidate keys, job keys, and rubric criteria. Does not own UI (#3).
**Citations:** `patt.artifact.read-current`, `patt.artifact.write-operative`, `stat.logging.error`, `stat.logging.info.api`.
**Scope:** `src/ui/api/api_candidate.py` — new authenticated routes: version list + set-current for candidate catalog keys and for a rubric criterion. `src/ui/api/api_jobs.py` — new authenticated routes: version list + set-current for job catalog keys.
Estimate: 2

#### 3: **Blur-save + version arrows in the editors - Katherine**

After #2. Blur-save replaces the 2-second timer. One shared arrow control, mounted artifact-level and per-criterion in `ArtifactEditor` and artifact-level in `ContextTextPage`. Saves unsaved edits before a move and re-hydrates after it. Does not own backend behavior.
**Citations:** `patt.artifact.ui-consistency`, `patt.artifact.read-current`.
**Scope:** `src/ui/frontend/src/components/ArtifactVersionNav.tsx` — shared back/forward arrows + position indicator control. `src/ui/frontend/src/components/ArtifactEditor.tsx` — blur-save replaces the autosave timer. Artifact-level nav for catalog keys, per-criterion nav in rubric mode. Flush unsaved edits before a move, reload after. `src/ui/frontend/src/components/ContextTextPage.tsx` — artifact-level nav for the seven `candidate.context.*` pages, and reload after a move.
Estimate: 3

**New patterns:** none.

**Monolith check:** Functional scope N=7, children M=3. Split by layer (data/core → API → UI).

**Scope partition check:** all 8 Component scope files are claimed exactly once (#1: database, candidate, tracker; #2: api_candidate, api_jobs; #3: ArtifactVersionNav, ArtifactEditor, ContextTextPage).

---

## Original brief

Add a forward and back arrow on all artifacts that "move" the current value chronologically through the changes. New changes are put in at the end, not forked from the middle (that is, the abandoned versions are still in the list.

Change the autosave to only create a new record every 60 seconds, meaning current = 1 record saves in place for all the seconds between 00 and 59.

### Comments

#### katherine — 2026-10-09T00:12:55.085Z
AST-2068 move-target blocker resolved with the recommended option (step from current after the save-before-move flush; matches Stage 4 Done-when). `origin/sub/AST-2043/AST-2068-version-ui` @ `e24fd4e0c`. Reverse: pass the render-time back/forward uuid again.

#### katherine — 2026-10-09T00:12:06.534Z
🛑 AST-2068 Stage 3/4 blocked: plan contradicts itself on where an arrow lands after saving an unsaved edit (@susan)
Step: Stage 4 step 4 `handleMove` + step 6 `onBack={() => void handleMove(nav.backUuid)}`; Stage 3 step 7 `renderVersionNav` (`go(nav.backUuid)`)
Issue: The planned code picks the arrow's target uuid at render time, before the save-before-move flush. Stage 4's Done-when says: "Typing an edit and then pressing back saves the edit first (N+1), then moves to N of N+1." The code as written lands on **N-1 of N+1** instead. It skips the version you were looking at before you typed, and your new edit is saved as the newest version but is not shown. Stages 1–4 are built and published (`origin/sub/AST-2043/AST-2068-version-ui` @ `44e32dc85`); this is the only open item. tsc and eslint are clean.
Proposed resolutions:
1. (Recommended) Step from the freshly saved version. When a flush happened, re-read the version map and pick back/forward from the new current. So back after an edit returns to the version you were viewing (undo-like), and forward is disabled at the newest. About 5 lines in each editor's move function, no new files. This matches the Done-when.
2. Keep the code as written (target picked before the edit) and change the Done-when to "N-1 of N+1".
3. Disable the arrows while there are unsaved edits (no flush on arrow). This contradicts parent Functional scope #5 ("Unsaved edits are saved before the move").

#### hedy — 2026-10-08T23:53:33.953Z
✅ AST-2067 Stage 2 unblocked — Susan said continue; option 1 taken (statute-shaped log lines kept, TRY401 allowed on the six AST-2067 `logger.exception` lines only). Build complete @ `ffa2e12b0`.

#### hedy — 2026-10-08T23:52:33.320Z
🛑 Stage 2 blocked: AST-2067 plan contradicts itself — logging code vs lint gate
Step: Verification — "ruff check … The count must not go up, and no finding may point at an AST-2067 line." vs every route's `logger.exception("…%s: %s…", …, type(exc).__name__, exc)` block (Stages 1–3).
Issue: ruff TRY401 ("Redundant exception object included in `logging.exception` call") fires on each planned `logger.exception` that passes `exc`. That shape is copied from `stat.logging.error`'s Do example (and the existing `update_candidate_data` handler, which carries the same TRY401). `str(exc)` also trips it. Stage 1 (`03eebc50b`) is built to the plan literally and verified by hand; it adds 2 TRY401 (2 more F401s are the Stage 2 rubric imports and clear when Stage 2 lands). All six routes would add 6 TRY401 in total.
Proposed resolutions:
1. (Recommended) Keep the statute-shaped log lines. Amend the Verification gate to allow TRY401 on the AST-2067 `logger.exception` lines only. No code change.
2. Drop `%s: %s` / `type(exc).__name__, exc` from the six messages (the traceback still carries the exception). Lint-clean, but the log line loses the live facts that `stat.logging.error` asks for.
3. Keep the code and add `# noqa: TRY401` on the six `exc,` lines.

#### chuckles — 2026-10-08T22:37:26.995Z
@susan

Removed the Application Responses port and the marker column.

1. **Application Questions are editable today.** The JAR Application Questions tab is not read-only right now: it renders in the editable `ArtifactEditor` and autosaves to `job_data.artifacts.proposed_answers`. After this epic it would blur-save there instead (no versions, no arrows). Leave it editable as-is (my default; out of scope here), or make it read-only as part of this epic?

#### chuckles — 2026-10-08T22:31:46.503Z
@susan

Updated the definition: blur-save instead of a timer, per-criterion rubric arrows, and Application Responses ported to the `artifact` table.

1. **Existing Application Questions data.** Jobs already built carry their answers as an agent-data pin or a `job_data` blob. After the port they'd show empty. Options: (a) a one-time migration script copies each job's existing body into a first artifact row (my recommendation); (b) start fresh, so old jobs stay blank until regenerated.
2. **Write-source marker column.** You picked (a) on coalescing, a column marking agent vs operator rows. With blur-save there's no in-place overwrite left to protect, so the column has no job here. Drop it (my default), or keep it anyway for future traceability?

#### chuckles — 2026-10-08T18:17:35.873Z
@susan

1. **Which window?** Does "seconds between 00 and 59" mean a **wall-clock minute** (a save at 12:00:58 and one at 12:01:02 land in two rows) or a **rolling 60 seconds from when the row was created** (those two saves share one row)? I lean rolling, so no version ever covers less than a minute.
2. **Which artifacts get arrows?** Only artifacts stored in the `artifact` table have a history: Base Resume (+ structure), Job Resume, Cover Letter, and the seven profile context pages. The six Criteria pages, Company Search Terms, and Application Responses live in the old blobs with no versions. Should this epic **exclude** them (my default), or bring them into the catalog first? That would roughly double the epic.
3. **Coalescing over generated content.** The table doesn't currently record whether a row came from an agent or an operator, so an operator edit made seconds after Generate/Draft lands would overwrite the agent's version in place. Options: (a) add a write-source marker column and coalesce only into operator rows (my recommendation); (b) coalesce only into rows the editor itself just saved in this session; (c) accept the overwrite.
4. **Canon amendment.** `patt.artifact.write-operative` currently bans every in-place body UPDATE. Coalescing needs a scoped exception (operator save into the newest current row inside the window). Approve it inside this epic, or as its own canon ticket first?

---

_Implementation detail may live in git history on `origin/dev`._
