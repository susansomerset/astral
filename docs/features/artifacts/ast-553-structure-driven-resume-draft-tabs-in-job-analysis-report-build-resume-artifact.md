# Structure-driven resume draft tabs in Job Analysis Report (Build Resume Artifact)

**Linear:** https://linear.app/astralcareermatch/issue/AST-553/structure-driven-resume-draft-tabs-in-job-analysis-report-build-resume-artifact  
**Publish ref:** `origin/sub/AST-300/AST-553-jar-resume-draft-tabs` (parent integration: `origin/ftr/AST-300-build-resume-artifact`)

**Summary:** Add structure-keyed, editable resume draft panels to **Job Analysis Report** (`JobAnalysisReportModal`), mirroring **AST-519** Base Resume Content: tabs follow the selected candidate's enabled `resume_structure` section ids; content loads from `job_data.artifacts.resume_content` and saves back through a job-scoped API that calls existing `save_job_artifact_resume_content` (structure filter + contact snapshot in **tracker**). Does not run dispatch, chain persistence, or BUILD_ARTIFACTS gating (**AST-552** / Ada). Does not change builder/print (**AST-518** consumes saved blob as-is).

---

## Prerequisite gate (before Stage 1)

1. **`git fetch origin`**; on **`dev-kath`**, **`git merge origin/dev`** and **`git merge origin/ftr/AST-300-build-resume-artifact`** per dispatch manifest (merge-clean gate: **`origin/dev` ancestor of HEAD**, **`BEHIND=0`**).
2. Confirm **`origin/sub/AST-300/AST-553-jar-resume-draft-tabs`** exists (**§4a** — do not create).
3. Read **`src/core/tracker.py`** `save_job_artifact_resume_content` and **`_prepare_job_resume_content`** — **do not** duplicate filtering in the API; delegate to tracker.
4. **Integration with AST-552:** This ticket **blocks** **AST-552** in Linear. Build and manual test may use jobs with pre-seeded `job_data.artifacts.resume_content` (pytest monkeypatch or DB fixture) until **AST-552** lands chain persistence. Do not implement BUILD_ARTIFACTS dispatch or `persist_job_artifact_from_parsed` changes here.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_jobs.py` | `PUT /api/jobs/<astral_job_id>/artifacts/resume_content` → `save_job_artifact_resume_content` | ui |
| `src/ui/frontend/src/components/ArtifactEditor.tsx` | Optional **job persistence** props: load/save job `resume_content` (no Generate) | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Resume draft section: structure fetch + editor; visibility by state/content | ui |
| `src/ui/frontend/src/App.css` | Spacing for draft block inside modal (reuse `.job-analysis-*` / collapsible patterns) | ui |
| `tests/component/ui/api/test_api_jobs.py` | New file or extend if exists: PUT resume_content happy path + 404 | tests |
| `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` | Draft tabs render + save calls job PUT | tests |
| `tests/component/frontend/components/test_ArtifactEditor.test.tsx` | One test for job persistence mode load/save URLs | tests |
| `docs/ASTRAL_TEST_BIBLE.md` | **§7.13zq** manifest row for **AST-553** (Stage 5) | docs |

**Out of scope (do not edit):** `src/core/consult.py`, `src/core/dispatcher.py`, `src/core/agent.py`, `src/core/tracker.py` (unless a blocking bug is found — then stop and comment on **AST-553**), **AST-552** files, builder.py, parent epic plan.

---

## Stage 1: Job API — save `resume_content`

**Done when:** Authenticated `PUT` merges a section-keyed dict into `job_data.artifacts.resume_content` via tracker filtering; GET job detail unchanged (already returns full `job_data`).

1. In **`src/ui/api/api_jobs.py`**, add import: `from src.core.tracker import save_job_artifact_resume_content` (alongside existing tracker imports).

2. Register route **`PUT /api/jobs/<astral_job_id>/artifacts/resume_content`** **after** the existing `/<astral_job_id>` GET route and **before** `/skip` (same blueprint prefix `/api/jobs`):
   - `@require_auth`
   - `job = get_job(astral_job_id)`; if missing → `jsonify({"error": "Not found"}), 404`
   - `data = request.get_json(force=True) or {}`
   - `body = data.get("resume_content")`
   - If `body` is not a `dict` → `jsonify({"error": "resume_content must be a dict"}), 400`
   - Call `save_job_artifact_resume_content(astral_job_id, body)` (tracker coerces values to str and filters keys to candidate structure).
   - Return `jsonify({"ok": True})`.

3. Create **`tests/component/ui/api/test_api_jobs.py`** if missing (mirror **`test_api_candidate.py`** auth monkeypatch pattern used in other API component tests). Add:
   - **`test_put_resume_content_persists_via_tracker`**: monkeypatch `get_job` to return a minimal job dict; monkeypatch `save_job_artifact_resume_content` to capture args; `PUT` with `{"resume_content": {"professional_summary": "x"}}` → 200, capture called with same job id and dict.
   - **`test_put_resume_content_404_when_job_missing`**: `get_job` → `None` → 404.

⚠️ **Decision:** Request body shape is `{"resume_content": {<section_id>: "<string>", ...}}` (not nested under `artifacts`) so the route is explicit and matches a single artifact type.

---

## Stage 2: `ArtifactEditor` job persistence mode

**Done when:** `ArtifactEditor` can render fixed structure tabs for a job id, load content from job artifacts, autosave to the new PUT route, with **no** Generate/Regenerate UI.

1. In **`ArtifactEditor.tsx`**, extend **`ArtifactEditorProps`**:
   ```ts
   jobPersistence?: { jobId: string }
   ```
   When `jobPersistence` is set:
   - Require `useCandidateResumeStructure={true}` and `structureSections` from parent **or** fetch `/api/candidates/${selectedId}/resume_structure` as today (structure mode unchanged).
   - Set `artifactKey` to `"resume_content"` (caller must pass `artifactKey="resume_content"`).
   - **Disable** Generate: treat as `canGenerate === false` when `jobPersistence` is set (do not show Generate/Regenerate controls).
   - **Load effect:** replace candidate GET branch when `jobPersistence` is set:
     - `GET /api/jobs/${jobPersistence.jobId}`
     - Read `(job.job_data?.artifacts ?? {}).resume_content` as dict (same fixed-field tab mapping as candidate `base_resume` branch).
     - Build tabs from `fixedFields` only; omit keys not in structure (same as AST-519 — no orphan tabs).
   - **`doSave`:** when `jobPersistence` is set, `PUT /api/jobs/${jobPersistence.jobId}/artifacts/resume_content` with body `{"resume_content": buildPayload(t)}` (dict payload from `buildPayload` when `fixedFields` is set).
   - Autosave, manual Save, unmount flush, and `beforeunload` guard behave the same as candidate mode.

2. Do **not** add `taskKey` usage in job mode (no POST generate).

3. In **`tests/component/frontend/components/test_ArtifactEditor.test.tsx`**, add **`job persistence mode saves to job artifacts endpoint`**:
   - Render with `useCandidateResumeStructure`, `structureSections={[{id:"professional_summary",label:"Summary"}]}`, `artifactKey="resume_content"`, `taskKey=""` (or dummy), `jobPersistence={{ jobId: "j1" }}`.
   - Mock GET job with `resume_content: { professional_summary: "hello" }`; mock PUT; edit field; assert PUT URL ends with `/artifacts/resume_content` and body contains updated text.

---

## Stage 3: Wire draft panels into `JobAnalysisReportModal`

**Done when:** For jobs in review with resume content (or empty structure tabs in review — see visibility), modal shows collapsible per-section editors; save round-trips to job artifact; existing upshot/JD/footer unchanged.

1. In **`JobAnalysisReportModal.tsx`**:
   - Import `ArtifactEditor` and `useCandidate` from existing paths.
   - `const { selectedId } = useCandidate()` — required for structure endpoint (Recommended list is already candidate-scoped).
   - Add state: `structureSections: { id: string; label: string }[] | null` and load via `useEffect` when `selectedId` is set: `GET /api/candidates/${selectedId}/resume_structure` → map `sections` to `{ id, label }` (same as **ArtifactsBaseResumeContent** / AST-519).
   - Derive `const resumeContent = (jobData?.artifacts as Record<string, unknown> | undefined)?.resume_content`.
   - **Visibility** (render resume draft block only when **all** hold):
     - `job.state === "CANDIDATE_REVIEW"`
     - `selectedId` is truthy
     - `structureSections` loaded and length > 0
   - When visible, render a section **after** upshot block and **before** Phase E agent story panels:
     - Heading: `Resume draft` (use `entity-section-label` class).
     - If `resumeContent` is missing or empty object: show muted line `No resume draft on file yet.` **and still** render `ArtifactEditor` with empty strings (allows paste/edit once **AST-552** populates — optional: hide editor until keys exist; **use editor with empty tabs** so AC #4 "editable" is satisfied when content arrives on reload).
     - `<ArtifactEditor title="Resume draft" artifactKey="resume_content" taskKey="craft_resume_base" useCandidateResumeStructure structureSections={structureSections} jobPersistence={{ jobId }} />` — `taskKey` unused in job mode but satisfies prop type.
   - On successful save inside editor, optional: call `load()` to refresh local `job` state (not required if editor owns tab state; prefer **`load()` after save** so footer/actions see fresh `job_data`).

2. In **`App.css`**, add `.job-analysis-resume-draft { margin: 16px 0; }` (minimal) if modal layout needs separation — only if cramped without it.

⚠️ **Decision:** Draft UI only in **`CANDIDATE_REVIEW`**, not `RECOMMENDED` or `BUILD_ARTIFACTS`, so candidates do not edit before chain completion (AC #4). Reload after save keeps modal consistent with DB.

---

## Stage 4: Component tests for modal

**Done when:** Vitest proves draft section and save path; existing AST-481 upshot tests still pass.

1. In **`tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx`**, extend `paintAndJobMocks` to handle:
   - `GET /api/candidates/c1/resume_structure` → `{ sections: [{ id: "professional_summary", label: "Summary" }], accent_color: null }`
   - `PUT /api/jobs/j-review/artifacts/resume_content` → `{ ok: true }`

2. Add test **`shows resume draft editor in CANDIDATE_REVIEW`**:
   - Job GET: `state: "CANDIDATE_REVIEW"`, `job_data: { analysis_upshot: minimalValidUpshot(), artifacts: { resume_content: { professional_summary: "Draft text" } } }`
   - Mock candidate context `selectedId: "c1"` (use `renderWithProviders` default or override — follow existing test-utils pattern for `CandidateContext`).
   - Assert label `Resume draft` and textarea/value `Draft text` present.

3. Add test **`does not show resume draft on RECOMMENDED`**:
   - Same job blob but `state: "RECOMMENDED"` → assert no `Resume draft` heading.

4. Add test **`PUT resume_content on edit`** (optional debounce: use `userEvent` + fake timers if autosave tested; otherwise rely on ArtifactEditor unit test from Stage 2).

---

## Stage 5: Bible manifest and verify

**Done when:** `§7.13zq` documents tests; `tsc` + narrowed component tests green.

1. In **`docs/ASTRAL_TEST_BIBLE.md`**, after **§7.13zp**, add **§7.13zq Job Analysis resume draft tabs (AST-553)** with table row: API PUT + modal/editor; manifest tests listing the three test modules above; narrowed `run_component_tests.sh` and Vitest commands.

2. Run:
   ```bash
   cd src/ui/frontend && npm run build
   cd src/ui/frontend && npx tsc --noEmit
   ./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_jobs.py
   cd src/ui/frontend && npm run test:component -- \
     ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
     ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx
   ```

3. Manual spot-check (comment on **AST-553** if unable in dev): open Recommended → job in **CANDIDATE_REVIEW** with `resume_content` → edit section → confirm print/preview route shows updated text (**AST-518** path) without code changes in builder.

---

## Execution contract (for the developer agent)

- Execute stages in order; one commit per stage on **`dev-kath`**, then publish product commits per **build-astral** (not in plan-astral).
- If `selectedId` is null in modal context, show no draft block (do not guess candidate).
- If structure fetch fails, show `entity-error` line under Resume draft heading; do not fall back to global `DATA_SHAPES` keys.
- Any ambiguity about **AST-552** persistence shape → stop and comment on **AST-553** with parent **AST-300** linked; do not patch tracker.

---

## Self-Assessment

**Scope — `Single-Component`**  
Touches job API blueprint, two React components, CSS, and tests — reuses tracker persistence and AST-519 editor structure mode without core pipeline changes.

**Conf — `Medium`**  
AST-519 provides the tab/structure pattern; new job PUT and job-mode editor wiring are straightforward but need careful save URL and state gating.

**Risk — `HIGH`**  
Incorrect save target or unfiltered keys would corrupt `job_data.artifacts.resume_content` and job-specific print output; mitigated by delegating to `save_job_artifact_resume_content`.

---

## Self-review vs ASTRAL_CODE_RULES

- **§1.3 DRY:** Reuse `ArtifactEditor` structure mode + tracker save helper; no second filter implementation in API.
- **§2.1 config:** State gate uses literal `CANDIDATE_REVIEW` (job state string from `JOB_STATES` family — matches existing modal/footer patterns); no new config block.
- **§3.3 imports:** API imports tracker only; no data/external from UI.
- **§3.5 naming:** Components remain flat under `components/`; one `App.css`.
- **§3.6 spikes:** None.
- **Conflicts:** None identified; UI visibility is intentionally not config-driven (job report context is fixed). If Susan wants nav-style config later, escalate — do not add in this ticket.

---

## Radia review (AST-553)

**Diff:** `origin/dev...origin/sub/AST-300/AST-553-jar-resume-draft-tabs` (tip `7e904f38`)

### What's solid

- **Plan fidelity:** `PUT /api/jobs/<id>/artifacts/resume_content` delegates to `save_job_artifact_resume_content` — no duplicate structure filter in the API (**§1.3 DRY**, **§3.2**).
- **AST-519 reuse:** `ArtifactEditor` job mode mirrors structure-keyed fixed tabs; Generate suppressed when `jobPersistence` is set.
- **Modal gating:** Resume draft only in `CANDIDATE_REVIEW` with loaded `resume_structure` — matches AC #4 and plan Stage 3.
- **Save round-trip:** `onSaved: load` refreshes job detail after PUT; autosave/manual save target the job artifact route.
- **Tests (AST-553 manifest):** PUT happy/404/400, modal visibility, ArtifactEditor job persistence — aligned with **§7.13zs** AST-553 narrowed run.

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **fix-now** | `tests/component/ui/api/test_api_jobs.py` | Four `test_approve_artifacts_*` cases were added on this publish ref, but `api_jobs.py` on the same tip has **no** `approve_artifacts` route (that is **AST-552** / `origin/sub/AST-300/AST-552-build-artifacts-gate-persistence`). Running those tests against this branch returns 404. Remove them from **AST-553** or land **AST-552** API on the integration line before keeping them here. |
| **discuss** | `ArtifactEditor.tsx` job-load `useEffect` | `GET /api/jobs/...` has no `.catch`; a failed load leaves `loaded=false` with no error toast (structure mode shows shape/loading ambiguity). Candidate mode has the same pattern — acceptable if intentional; otherwise add error surface in **resolve-astral**. |
| **advisory** | `JobAnalysisReportModal.tsx` | Literal `CANDIDATE_REVIEW` gate matches plan self-review (**§2.1**); documented exception to config-driven UI for this modal context. |

### Recommended actions (resolve-astral)

1. Drop `test_approve_artifacts_*` from **AST-553** (keep on **AST-552** sub ref only), or merge **AST-552** `approve_artifacts` into the parent integration branch before prep-uat.
2. Optional: job-load failure UX in `ArtifactEditor` job persistence mode (toast + `entity-error`).
3. No application changes required for core PUT/modal/editor wiring otherwise.

**Review doc commit:** `f3c1c4ae` (Radia review section on publish ref)

---

## Resolution (2026-06-03)

**Product (Katherine):**
- `ArtifactEditor.tsx` — job persistence load effect now `.catch`es failed `GET /api/jobs/<id>` and renders `entity-error` instead of indefinite loading (Radia **discuss** → closed).
- Core PUT / modal / editor wiring unchanged (Radia **advisory** — no changes required).

**Test-tree (Betty via `[qa-handoff]`):**
- Remove four `test_approve_artifacts_*` cases from `tests/component/ui/api/test_api_jobs.py` on **AST-553** publish ref only — they belong on **AST-552** (`approve_artifacts` route not in this ticket’s `api_jobs.py`). Radia **fix-now**.

**Publish:** `origin/sub/AST-300/AST-553-jar-resume-draft-tabs` @ `0e20dccf` (product `782edd7a`, Betty test-tree `0e20dccf`). §9a clean vs `origin/dev` and `origin/ftr/AST-300-build-resume-artifact`.
