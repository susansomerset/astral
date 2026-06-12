# AST-553: Structure-driven resume draft tabs in Job Analysis Report (Build Resume Artifact)

**Linear:** [AST-553](https://linear.app/astralcareermatch/issue/AST-553/structure-driven-resume-draft-tabs-in-job-analysis-report-build) (child of [AST-300](https://linear.app/astralcareermatch/issue/AST-300/build-resume-artifact))

**Publish ref:** `sub/AST-300/AST-553-jar-resume-draft-tabs` on `origin` (parent integration: `ftr/AST-300-build-resume-artifact`)

**Summary:** When a job reaches **CANDIDATE_REVIEW** with populated `job_data.artifacts.resume_content`, the Job Analysis Report modal exposes structure-driven draft tabs (mirroring **AST-519** Base Resume Content): one tab per **job-agent-editable** enabled section from the owning candidate's `artifacts.resume_structure`, loaded from and saved back to `job_data.artifacts.resume_content` via a new jobs API route. Contact/header sections render read-only from the stored snapshot. A print-preview link hits the existing **`GET /candidate/resume/<job_id>`** route so edits appear in HTML output (**AST-518**).

---

## Prerequisite gate (read-only — do not implement sibling scope)

1. **AST-552** (Hedy) owns BUILD_ARTIFACTS gate, chain completion, and first population of `resume_content`. This ticket **consumes** populated `resume_content`; it does not dispatch the chain or transition to **CANDIDATE_REVIEW**.
2. **AST-518** / **AST-519** already landed: `save_job_artifact_resume_content`, `resolve_resume_structure`, `enabled_resume_structure_sections`, and structure-keyed builder rendering. **Import and reuse** — do not duplicate filter/snapshot logic from `tracker._prepare_job_resume_content`.
3. **AST-307** modal shell exists as `JobAnalysisReportModal.tsx`. Extend it; do not create a second modal.

### Integration contract (existing on disk)

**Job blob path:** `job_data.artifacts.resume_content` — flat `dict[str, str]` keyed by section id.

**Structure authority:** Owning candidate's `candidate_data.artifacts.resume_structure` via `resolve_resume_structure(candidate_data)` (job → company → `candidate_id` — same lookup as `tracker._candidate_data_for_job`).

**Save pipeline:** `tracker.save_job_artifact_resume_content(astral_job_id, resume_content)` filters editable keys, re-snapshots contact sections, merges into `job_data.artifacts`.

**UI visibility gate:** Render draft editor only when **`job.state === "CANDIDATE_REVIEW"`** and `resume_content` is a non-empty dict (at least one string value with `.strip()`). All other states: omit the draft block (no empty editor on **RECOMMENDED** / **BUILD_ARTIFACTS** / **BUILD_FAILED**).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Add `job_editable_resume_sections(resolved)` and `contact_resume_snapshot_sections(resolved, resume_content)` | core |
| `src/ui/api/api_jobs.py` | `GET …/resume_draft`; `PUT …/artifacts/resume_content` | ui |
| `src/ui/frontend/src/components/JobResumeDraftEditor.tsx` | New structure-keyed job draft editor (fixed tabs, autosave, read-only contact) | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Mount draft editor + preview link when gate passes | ui |
| `src/ui/frontend/src/App.css` | Styles for draft block inside modal (reuse `.artifact-editor-collapsible-stack`, `.job-analysis-*` patterns) | ui |
| `tests/component/core/test_candidate.py` | Tests for new section helpers | tests |
| `tests/component/ui/api/test_api_jobs.py` | GET/PUT resume draft routes | tests |
| `tests/component/frontend/components/test_JobResumeDraftEditor.test.tsx` | New component tests | tests |
| `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` | Assert draft panel visibility + integration | tests |

**Out of scope:** Dispatch/chain (**AST-552**, Ada tickets), structure catalog definition (**AST-477** Done), builder HTML changes (**AST-518** Done), cover letter tabs (**AST-301** canceled).

---

## Stage 1: Core section helpers and jobs API

**Done when:** Authenticated clients can `GET /api/jobs/<id>/resume_draft` for section metadata + current content, and `PUT /api/jobs/<id>/artifacts/resume_content` persists candidate edits through `save_job_artifact_resume_content` with orphan keys stripped.

1. In **`src/core/candidate.py`**, after **`enabled_resume_structure_sections`**, add **`job_editable_resume_sections(resolved: dict) -> list[dict]`**:
   - Input `resolved` is output of **`resolve_resume_structure`** (do not read artifacts directly).
   - From `resolved["sections"]`, collect entries where `enabled` is true **and** `job_agent_editable` is true.
   - Return `[{"id": spec["id"], "label": spec["title"]}, …]` sorted by `order` ascending, then `id` (same sort as `enabled_resume_structure_sections`).

2. In the same file, add **`contact_resume_snapshot_sections(resolved: dict, resume_content: dict) -> list[dict]`**:
   - Import **`RESUME_STRUCTURE_CONTACT_SECTION_IDS`** from `src.utils.config` (already used in `filter_content_to_resume_structure`).
   - For each contact id that is **enabled** in `resolved["sections"]`, append `{"id": sid, "label": <title>, "content": str(resume_content.get(sid) or "")}`.
   - Preserve config contact id order (tuple order in `RESUME_STRUCTURE_CONTACT_SECTION_IDS`).

3. In **`src/ui/api/api_jobs.py`**, add imports: `get_job_artifacts`, `save_job_artifact_resume_content`, `_candidate_data_for_job` from `src.core.tracker` (or expose a thin public wrapper on tracker if `_candidate_data_for_job` is private — prefer adding **`candidate_data_for_job(astral_job_id) -> dict`** public alias on `tracker.py` that delegates to `_candidate_data_for_job` rather than importing the underscore name from API).
   - Register **`GET /<astral_job_id>/resume_draft`** **before** any catch-all that could shadow it (same file order as existing routes).
   - Handler: `get_job(astral_job_id)` → 404 if missing.
   - `cd = candidate_data_for_job(astral_job_id)`; `resolved = resolve_resume_structure(cd)`.
   - `rc = get_job_artifacts(job).get("resume_content")`; coerce to dict or `{}`.
   - Response JSON:
     ```json
     {
       "resume_content": { "<section_id>": "<string>", ... },
       "editable_sections": [{"id": "...", "label": "..."}],
       "contact_sections": [{"id": "...", "label": "...", "content": "..."}]
     }
     ```
   - `editable_sections = job_editable_resume_sections(resolved)`.
   - `contact_sections = contact_resume_snapshot_sections(resolved, rc)`.

4. Register **`PUT /<astral_job_id>/artifacts/resume_content`**:
   - Body JSON: `{ "resume_content": { "<section_id>": "<string>", ... } }` — 400 if missing or not a dict.
   - 404 if job missing.
   - Call **`save_job_artifact_resume_content(astral_job_id, body["resume_content"])`** (no direct `save_job_data` from API).
   - Return `{ "ok": true, "resume_content": <prepared dict from get_job after save> }` — re-fetch job and return filtered blob so client matches disk.

5. In **`tests/component/core/test_candidate.py`**, add **`TestAst553JobResumeDraftSections`**:
   - **`test_job_editable_sections_excludes_contact`**: structure with contact + experience enabled; only experience in result when `job_agent_editable` true on experience only.
   - **`test_contact_snapshot_sections_read_content`**: pass resume_content dict; assert contact ids return stored strings.

6. In **`tests/component/ui/api/test_api_jobs.py`**, add **`TestAst553ResumeDraftApi`**:
   - Monkeypatch `get_job`, `candidate_data_for_job`, `save_job_artifact_resume_content`.
   - **`test_get_resume_draft_returns_sections`**: 200 with editable + contact arrays.
   - **`test_get_resume_draft_404`**: missing job.
   - **`test_put_resume_content_calls_tracker`**: PUT body `{resume_content: {professional_summary: "x"}}` → save called once; 200.

⚠️ **Decision:** Orphan keys in PUT body are **dropped on save** (via existing `_prepare_job_resume_content`), not rejected with 400 — matches **AST-519** autosave self-heal pattern.

---

## Stage 2: JobResumeDraftEditor component

**Done when:** Component loads draft context from `GET /api/jobs/:id/resume_draft`, renders editable collapsible tabs for `editable_sections`, read-only contact panels, autosaves edits to PUT route, and exposes a working print-preview link.

1. Create **`src/ui/frontend/src/components/JobResumeDraftEditor.tsx`**:
   - Props: `{ jobId: string; onSaved?: () => void }`.
   - On mount / `jobId` change: `GET /api/jobs/${jobId}/resume_draft`.
   - On failure: render `<p className="entity-error">Failed to load resume draft.</p>`.
   - Build **`tabs`** state: one entry per `editable_sections` item `{ id, label, content: resume_content[id] ?? "" }`.
   - Render using existing patterns from **`ArtifactEditor`** fixed-tab mode:
     - Import **`CollapsiblePanel`**, **`LabeledTextArea`**, **`Toast`**.
     - Stack class **`artifact-editor-collapsible-stack`** inside a wrapper **`job-resume-draft-editor`**.
     - Each editable section: **`CollapsiblePanel`** + **`LabeledTextArea`** with `onChange` updating local tabs state.
   - Below editable stack, map **`contact_sections`** to **`CollapsiblePanel`** with **`readOnly`** textarea or `<p className="job-analysis-upshot-body">` — contact content is **not** editable (no `onChange`).
   - Header row inside component:
     - Title: **`Resume draft`** (`h2` with class `entity-section-label`).
     - **`Save`** button (explicit save like ArtifactEditor fixed mode) + dirty indicator.
     - **`Preview`** link: `<a href={\`/candidate/resume/${encodeURIComponent(jobId)}\`} target="_blank" rel="noopener noreferrer" className="modal-btn save">Preview</a>`.
   - **`doSave`**: `PUT /api/jobs/${jobId}/artifacts/resume_content` with body `{ resume_content: Object.fromEntries(tabs.map(t => [t.id, t.content])) }`.
   - On success: clear dirty, toast success, call `onSaved?.()`.
   - Autosave: **`AUTOSAVE_MS = 2000`** debounce on editable tab changes (same as ArtifactEditor); flush pending save on unmount when dirty.
   - **No Generate / Regenerate** controls.

2. Do **not** add Generate, candidate picker, or rubric tab editing to this component.

⚠️ **Decision:** Separate **`JobResumeDraftEditor`** instead of extending **`ArtifactEditor`** props — job-scoped load/save paths and absence of Generate differ enough that coupling would risk regressions on Base Resume Content (**AST-519**).

---

## Stage 3: Wire into Job Analysis Report modal

**Done when:** Opening a **CANDIDATE_REVIEW** job with `resume_content` in the modal shows the draft editor between the job-description block and the Applied footer; saving in the editor updates `job_data.artifacts.resume_content` and the preview link renders edited text.

1. In **`src/ui/frontend/src/components/JobAnalysisReportModal.tsx`**:
   - Import **`JobResumeDraftEditor`**.
   - After JD block, before **`job-analysis-report-footer`**:
     ```tsx
     {job.state === "CANDIDATE_REVIEW" && hasResumeDraft(jobData) && jobId && (
       <JobResumeDraftEditor jobId={jobId} onSaved={load} />
     )}
     ```
   - Add helper **`hasResumeDraft(jobData)`** in same file (not exported):
     - Read `(jobData?.artifacts as Record)?.resume_content`.
     - Return true iff dict with at least one string value where `.trim()` is non-empty.

2. In **`src/ui/frontend/src/App.css`**, add minimal rules:
   - **`.job-resume-draft-editor`**: `margin: 16px 0`, top border using `var(--border-subtle)` (match `.job-analysis-upshot-wrap` spacing).
   - **`.job-resume-draft-editor .entity-section-label`**: margin-bottom 8px.
   - Reuse existing **`.artifact-editor-collapsible-stack`**, **`.modal-btn`**, **`.entity-error`** — no new color tokens.

3. Do **not** change Applied/Skip action wiring (**AST-312**); editor saves independently before candidate clicks Applied.

---

## Stage 4: Frontend and API verification tests

**Done when:** New and updated Vitest/pytest cases pass; `cd src/ui/frontend && npx tsc --noEmit` clean.

1. Create **`tests/component/frontend/components/test_JobResumeDraftEditor.test.tsx`**:
   - Mock `api` GET resume_draft with two editable sections + one contact section.
   - Assert two editable textareas (or labeled areas) and contact panel shows snapshot text.
   - Edit editable field → mock PUT called with updated dict on Save (and optionally after autosave debounce with fake timers).

2. Extend **`tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx`**:
   - **`test_shows_resume_draft_when_candidate_review_with_content`**: job state `CANDIDATE_REVIEW`, `job_data.artifacts.resume_content: { professional_summary: "Draft" }`, mock resume_draft GET → expect "Resume draft" heading.
   - **`test_hides_resume_draft_when_recommended`**: state `RECOMMENDED` → no draft heading.

3. Run:
   ```bash
   pytest tests/component/core/test_candidate.py::TestAst553JobResumeDraftSections tests/component/ui/api/test_api_jobs.py::TestAst553ResumeDraftApi -q
   cd src/ui/frontend && npm run test:component -- \
     ../../../tests/component/frontend/components/test_JobResumeDraftEditor.test.tsx \
     ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx
   cd src/ui/frontend && npx tsc --noEmit
   ```

---

## Execution contract (for the developer agent)

- Execute stages in order; one commit per stage on **`dev-kath`**, publish via **`git-store-code-commit`** / plan was already published separately.
- Do **not** implement BUILD_ARTIFACTS dispatch, chain hops, or **CANDIDATE_REVIEW** transition (**AST-552** / Ada scope).
- Do **not** change **`builder.py`**, **`save_job_artifact_resume_content`** filter rules, or **`craft_resume_base`** (**AST-518** owns persistence semantics).
- Do **not** add cover-letter draft tabs.
- When a step is ambiguous or **`resume_content` is empty on a CANDIDATE_REVIEW job** (data bug from sibling), **stop** and comment on **AST-553** with 🛑 format — do not invent fallback content from `base_resume`.
- Blocking questions → comment on **AST-300** parent per plan-astral execution contract.

---

## Self-Assessment

**Scope:** `Single-Component` — One new React component, small jobs API surface, two core list helpers, and modal wiring; no dispatcher, chain, or builder changes.

**Conf:** `Medium` — Reuses **AST-519** tab UX and existing **AST-518** save/filter pipeline; new job-scoped API is straightforward; depends on **AST-552** populating `resume_content` before UAT but not for building this UI slice.

**Risk:** `Medium` — Incorrect PUT target or bypassing `save_job_artifact_resume_content` could corrupt `job_data` or leak orphan keys; mitigated by routing all saves through tracker helper and structure-bound tabs only.

---

## Self-review vs ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuse `resolve_resume_structure`, `save_job_artifact_resume_content`, CollapsiblePanel stack; helpers shared by GET and PUT. |
| §2.1 config | Section ids/contact set from `RESUME_STRUCTURE_CONTACT_SECTION_IDS` and structure blob — no hardcoded tab lists in React. |
| §2.4 batch | N/A — no batch processing. |
| §2.6 state machine | UI reads `job.state` for visibility only; does not transition states. |
| §3.3 imports | API imports core/tracker only; frontend uses `api()` client. |
| §3.5 naming | New component flat in `components/`; styles in `App.css` only. |

No conflicts requiring `conf-!!-NONE`.
