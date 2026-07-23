# Artifacts tab generate, cancel, edit (Redesign Recommended Job Modal)

**Linear:** [AST-951](https://linear.app/astralcareermatch/issue/AST-951/artifacts-tab-generate-cancel-edit-redesign-recommended-job-modal)  
**Parent:** [AST-858 — Redesign Recommended Job Modal](https://linear.app/astralcareermatch/issue/AST-858/redesign-recommended-job-modal)  
**Publish ref (origin):** `sub/AST-858/AST-951-artifacts-tab-generate-cancel-edit`  
**Parent integration ref:** `ftr/AST-858-redesign-recommended-job-modal`  
**Blocked by:** [AST-948](https://linear.app/astralcareermatch/issue/AST-948/modal-shell-horizontal-tabs-sticky-header-redesign-recommended-job) (Artifacts tab shell / `ReportSectionList` `leading` / `report_artifact_tabs`)

Own the Artifacts tab UX: empty → **Generate Artifacts**; in-flight **BUILD_ARTIFACTS** (including daisy-chain / `BUILD_ARTIFACTS.<hop>`) → yellow **Generating…** with **Cancel** beside it; when artifact blobs exist → collapsible editable **Job Resume** / **Cover Letter** / **Application Questions** via existing `ArtifactEditor` + job persistence (saves to `job_data`). No Reset/Regenerate. Does **not** own Summary/Analysis bodies or header Print controls.

---

## Prerequisite gate (before Stage 1 of build-child)

1. On epic worktree: `git fetch origin`; checkout `sub/AST-858/AST-951-artifacts-tab-generate-cancel-edit`; `git merge origin/dev`; `git merge origin/ftr/AST-858-redesign-recommended-job-modal`; merge-clean gate.
2. Merge **`origin/sub/AST-858/AST-948-modal-shell-horizontal-tabs-sticky-header`** (or rolled-up `origin/ftr/…`) so the Artifacts tab has `ReportSectionList`, optional `leading` action strip, and `report_artifact_tabs` section chrome.
3. If those pieces are missing, **stop** — comment on AST-951; do not rebuild shell/header.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/lib/recommendedJobReport.tsx` | Helpers: build-in-progress state detect; resolve primary actions for base + compound `BUILD_ARTIFACTS.*`; any-artifact / per-key content gates used by the tab | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Artifacts empty / in-flight / populated layouts; wire `ArtifactEditor` bodies; restore resume-structure fetch; fix Generate/Cancel strip labels + close-on-action keys | ui |
| `src/ui/frontend/src/App.css` | Only if Artifacts action strip needs a small flex row class under recommended-report (prefer existing `.recommended-report-header-actions` / `.modal-btn` / `.in-flight`) | ui |

**Out of scope:** new Flask routes; Reset/Regenerate; changing `ArtifactEditor` job-persistence contract; Summary/Analysis (AST-949/950); header Print (AST-948); `tests/` / bible (Betty).

**QA note (Betty):** Empty Generate; in-flight Generating…+Cancel (base + compound state); editable sections with job_data save/reload; Cancel → RECOMMENDED; no Reset/Regenerate.

---

## Stage 1: Artifacts action helpers (in-progress + action resolve)

**Done when:** Helpers exist to detect build-in-progress (including compound states) and to resolve Cancel/Generate actions when `job.state` is `BUILD_ARTIFACTS` or `BUILD_ARTIFACTS.<hop>`.

1. In `src/ui/frontend/src/lib/recommendedJobReport.tsx`, add:

   ```tsx
   /** True for BUILD_ARTIFACTS and legacy daisy-chain BUILD_ARTIFACTS.<hop> (not ERROR_BUILD_ARTIFACTS). */
   export function isArtifactsBuildInProgress(jobState: string): boolean

   /**
    * Primary actions for the Artifacts strip.
    * Looks up manifest.primary_actions_by_state[jobState]; if empty and
    * isArtifactsBuildInProgress(jobState), fall back to actions for "BUILD_ARTIFACTS".
    * Filters out action_key === "apply" (job-title deeplink owns apply).
    */
   export function artifactsTabPrimaryActions(
     manifest: StateUiManifest | null,
     jobState: string,
   ): ReportPrimaryAction[]

   /** True if any report_artifact_tabs artifact_key has content on job artifacts blob. */
   export function anyReportArtifactContent(
     artifacts: unknown,
     artifactTabs: Array<{ artifact_key: string }> | undefined,
   ): boolean
   ```

2. `isArtifactsBuildInProgress`: `jobState === "BUILD_ARTIFACTS"` OR `jobState.startsWith("BUILD_ARTIFACTS.")`. Do **not** treat `ERROR_BUILD_ARTIFACTS` as in-progress chrome (no Generating… strip unless manifest later adds actions for that state).

3. Keep existing `primaryActionsForState` / `artifactHasContent` as-is for other callers.

⚠️ **Decision:** Frontend fallback to `BUILD_ARTIFACTS` actions for compound states — manifest today only keys the base state; duplicating every hop into config is unnecessary for this presentation ticket. Mirror the intent of Python `is_build_artifacts_in_progress` but **exclude** `ERROR_BUILD_ARTIFACTS` from the Generating… chrome.

---

## Stage 2: Empty / in-flight / populated Artifacts layouts

**Done when:** Artifacts tab matches AC #6–8 layout rules; Generate/Cancel use today’s POST paths; in-flight shows yellow **Generating…** + **Cancel**; section list only when at least one artifact blob has content.

1. In `JobAnalysisReportModal.tsx`, replace AST-948’s always-on empty Artifacts `ReportSectionList` with three mutually exclusive layouts:

   **A — In progress** (`isArtifactsBuildInProgress(job.state)`):

   - Render an action row (class reuse: e.g. `recommended-report-header-actions` or `recommended-report-artifacts-actions`):
     - A **disabled** button, `className="modal-btn save in-flight"`, visible label exactly **`Generating…`** (ellipsis character `…`, not three ASCII dots).
     - Beside it, every action from `artifactsTabPrimaryActions` with `action_key === "cancel_build"` (label from manifest, normally **Cancel**), enabled unless `primaryBusy`.
   - Do **not** render the three section panels while in progress (even if partial blobs exist mid-chain).

   **B — Empty** (not in progress AND `!anyReportArtifactContent(artifacts, report_artifact_tabs)`):

   - Render **only** the Generate control from `artifactsTabPrimaryActions` (`action_key === "generate_artifacts"`, label from manifest **Generate Artifacts**).
   - On click: same POST as today (`/api/jobs/<id>/generate_artifacts`); apply `in-flight` + busy while request runs; on success keep AST-591 behavior (`onRefresh` + `onClose`).
   - No section list.

   **C — Populated** (`anyReportArtifactContent(…)` and not in progress):

   - Render `ReportSectionList` with sections = each `report_artifact_tabs` row where `artifactHasContent(artifacts, artifact_key)` (map `section_id=tab_id`, `nav_label` from manifest, `default_expanded: false`).
   - Omit `leading` Generate/Cancel on the populated layout (Print stays in header per AST-948; Apply stays job-title deeplink). If product later needs regenerate, that is out of scope.
   - `renderSection(sectionId)` → `ArtifactEditor` as in the pre-redesign modal:
     - Resume (`use_resume_structure`): restore `/api/candidates/<id>/resume_structure` fetch; show structure error / loading empty lines; pass `structureSections` + `useCandidateResumeStructure` + `jobPersistence={{ jobId, artifactKey, onSaved: load }}`; `taskKey="craft_resume_base"`.
     - Cover: `taskKey="craft_cover_letter"`, `shapesKey` from manifest when set.
     - Application: `taskKey="propose_application_responses"`, `shapesKey` from manifest when set.
   - Do **not** add Reset/Regenerate controls.

2. Fix close-on-action keys when running Cancel: config `action_key` is **`cancel_build`** (path_suffix `cancel_artifact_build`). Close the modal after successful generate **or** cancel when `action_key` is `generate_artifacts` **or** `cancel_build` (today’s modal incorrectly checks `cancel_artifact_build` — correct it in this ticket as part of Artifacts strip wiring).

3. While `primaryBusy` on Generate (before close), show `in-flight` on the Generate button; label may stay **Generate Artifacts** until unmount/close (in-progress chrome on reopen is **Generating…**).

4. `npx tsc -b --noEmit` for touched frontend files.

⚠️ **Decision:** Hide section chrome for empty and in-progress layouts — AC #6 is Generate-only; AC #7 is Generating…+Cancel; AC #8 sections only when blobs exist. This supersedes AST-948’s temporary “always three empty sections” shell decision for the Artifacts tab only.

⚠️ **Decision:** Populated tab does not show Generate again (no Reset/Regenerate in scope). Candidate with artifacts in `CANDIDATE_REVIEW` edits via sections; apply remains the header job-title link.

---

## Self-Assessment

**Scope:** Single-Component — Artifacts tab layout + helpers inside the Recommended report modal; reuses `ArtifactEditor` and existing generate/cancel APIs.

**Conf:** high — generate/cancel paths, `ArtifactEditor` job persistence, AST-645 `.in-flight`, and `report_artifact_tabs` are already shipped; this ticket re-homes and gates them on the Artifacts tab.

**Risk:** Medium — missing compound-state Cancel fallback would strand daisy-chain jobs without Cancel; showing empty section shells during Generate would fail AC #6; wrong `action_key` check would skip close-on-cancel.

---

## Code rules check

- **§1.3 DRY:** One in-progress helper + one action resolver; reuse `artifactHasContent` / `ArtifactEditor`; no second editor.
- **§1.4 / §2.1:** Action labels/paths and artifact section metadata stay manifest-driven; only compound-state **lookup fallback** is frontend (documented Decision).
- **§2.4 / §2.6:** N/A — no dispatch/state-machine changes; POSTs already exist.
- **§3.3 / §3.5:** Frontend only.
- **Tests / bible:** Betty owns.

---

## Review (build)

**Built:** `origin/sub/AST-858/AST-951-artifacts-tab-generate-cancel-edit` @ `e0c6344ee3fd26889f45f5cf57ccb2e034057345`

Stages 1–2: `isArtifactsBuildInProgress` / `artifactsTabPrimaryActions` / `anyReportArtifactContent`; Artifacts empty Generate, in-flight Generating…+Cancel, populated `ArtifactEditor` sections with resume-structure fetch. Tests deferred to Betty.
