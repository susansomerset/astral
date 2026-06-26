<!-- linear-archive: AST-581 archived 2026-06-23 -->

## Linear archive (AST-581)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-581/uat-preview-materials-button-resumecover-html-preview-tabs-in-jar  
**Status at archive:** Done  
**Project:** Astral Artifacts (inherited from AST-300)  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-300 — Build Resume Artifact  
**Blocked by / blocks / related:** parent: AST-300

### Description

## Bug (AST-300 UAT)

Susan expected a **Preview Materials** (or equivalent) control on the Recommended Job Report that opens **two** render surfaces: job-tailored **resume HTML** and **cover letter HTML**.

## Current

* `GET /candidate/resume/<job_id>` renders **one** combined HTML document (`builder.build_resume` may include cover inline).
* No JAR header/footer button; no dual-tab preview UX in `JobAnalysisReportModal.tsx`.

## Acceptance

1. When `CANDIDATE_REVIEW` (or when resume/cover content exists), JAR shows **Preview Materials**.
2. Opens resume preview + cover letter preview as **separate** tabs or windows (not one bundled page only).
3. Uses saved `job_data.artifacts.resume_content` / `cover_letter` + candidate structure.

## Paths

* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`
* `src/ui/api/api_resume_html.py`
* `src/core/builder.py`

### Comments

#### betty — 2026-06-05T20:08:42.813Z
**[rollup-child] resolved** — merge `origin/sub/AST-300/AST-581-uat-preview-materials-button-resumecover-html-preview-tabs-in-jar` into `origin/ftr/AST-300-build-resume-artifact` completed.

**Conflicts:** `docs/ASTRAL_TEST_BIBLE.md`, `tests/component/ui/api/test_api_jobs.py`

**Resolution:**
- Bible: kept **ftr/AST-300** §7.13zs baseline + **AST-581** narrowed run; dropped duplicate AST-550 block and polluted §7.13zr AST-578/579 rows from dev merge on sub
- `test_api_jobs.py`: kept **ftr** tip (AST-562 routes were dev pollution — AST-581 never touched this file)
- Stripped ~180 dev-only staged paths (docs/features flood, AGENTS.md, etc.); merge landed **13 AST-581 files** only

**Published:** `origin/ftr/AST-300-build-resume-artifact` @ `0e48558e`

**Sub ref:** `origin/sub/…/AST-581` still carries `Merge origin/dev` — recommend Betty republish via `git-store-qa-commit` with `JOAN_SESSION=0ca056cb-ffe4-4797-b7fa-a80108f0895c` stacked on updated ftr before next rollup retry.

#### radia — 2026-06-05T20:03:17.298Z
**Review (Radia)** — diff `origin/dev...origin/sub/AST-300/AST-581-uat-preview-materials-button-resumecover-html-preview-tabs-in-jar` @ `80095676` (product) + review doc @ `67d9fafc`.

**Plan fidelity:** Stage 1 builder split (`include_cover` default false, `build_cover_letter` / `GET /candidate/cover/<job_id>`) and Stage 2 JAR **Preview Materials** + tabbed `MaterialsPreviewModal` match the approved plan and acceptance.

### fix-now
None.

### discuss
- **`recommendedJobReport.tsx` — `materialsPreviewVisible`** — Hardcodes `CANDIDATE_REVIEW` in frontend lib (§3.2 G1 prefers manifest/API-resolved visibility). Plan and acceptance explicitly chose this; same family as `CandidateJobRowActions` state sets. Not blocking for UAT bugfix — flag if we want a manifest `preview_materials` flag per recommended state later.

### advisory
- **`MaterialsPreviewModal.tsx`** — `activeTab` persists across close/reopen; optional reset to `"resume"` on close.
- **`CANDIDATE_REVIEW` + empty artifacts** — Preview button shows per plan; resume iframe may 404 until chain populates content.
- **Job resume route** — `/candidate/resume/<job_id>` is permanently resume-only (combined print removed); documented plan decision.

**Blob:** [plan + review](https://github.com/susansomerset/astral/blob/sub/AST-300/AST-581-uat-preview-materials-button-resumecover-html-preview-tabs-in-jar/docs/features/artifacts/ast-581-uat-preview-materials-button-resumecover-html-preview-tabs-in-jar.md) — proceed to `resolve-astral`.

#### betty — 2026-06-05T19:59:00.807Z
## QA test manifest (AST-581)

**Publish ref:** `origin/sub/AST-300/AST-581-uat-preview-materials-button-resumecover-html-preview-tabs-in-jar` @ `80095676`

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `a8a568fa226dcb46bbfec7633b7f1987942140379c9824ca992ef88fa89f7d26` — §7.13zs row **AST-581** appended.

### 1. Existing coverage revised (builder resume-only default)

- `tests/component/core/test_builder.py::TestBuildResumeFromJob` — resume HTML no longer bundles cover unless `include_cover=True`
- `tests/component/core/test_builder.py::TestBuilderHelpers::test_cover_letter_subject_letter_aliases_render_on_cover_route` — Subject/Letter aliases on cover-only path

### 2. New tests (gaps)

| # | Path | What it proves |
|---|------|----------------|
| 1 | `tests/component/core/test_builder.py::TestAst581ResumeCoverSplit` | `include_cover` flag; `build_cover_letter_from_job` cover-only; `ValueError` without content |
| 2 | `tests/component/ui/api/test_api_resume_html.py::TestAst581CoverRoute` | `GET /candidate/cover/<job_id>` 200/404 |
| 3 | `tests/component/frontend/lib/test_recommendedJobReport.test.tsx` | `materialsPreviewVisible` — CANDIDATE_REVIEW, RECOMMENDED, BUILD_ARTIFACTS |
| 4 | `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` (AST-581 describe) | Preview Materials button visibility; stacked modal; Resume/Cover iframe `src` |

### 3. Run command (narrowed)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst581ResumeCoverSplit \
  tests/component/ui/api/test_api_resume_html.py::TestAst581CoverRoute
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_recommendedJobReport.test.tsx \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx
```

— Betty

#### chuckles — 2026-06-05T19:54:12.473Z
## [validate-plan] APPROVED

Plan matches AST-581 UAT acceptance: separate resume/cover HTML surfaces + JAR Preview Materials control. Scope stays UI/builder/routes; no chain or persistence changes. Layer table respects §3.3.

**Verdict:** APPROVED → Plan Approved.

— Chuckles

#### katherine — 2026-06-05T19:53:59.131Z
Plan: [`docs/features/artifacts/ast-581-uat-preview-materials-button-resumecover-html-preview-tabs-in-jar.md`](https://github.com/susansomerset/astral/blob/sub/AST-300/AST-581-uat-preview-materials-button-resumecover-html-preview-tabs-in-jar/docs/features/artifacts/ast-581-uat-preview-materials-button-resumecover-html-preview-tabs-in-jar.md) on **`origin/sub/AST-300/AST-581-uat-preview-materials-button-resumecover-html-preview-tabs-in-jar`** @ `05bdccbe`.

**Scope:** `Single-Component` — JAR header + stacked preview modal, thin Flask cover route, and `builder.py` resume/cover split; no chain or tracker changes.

**Conf:** `high` — AST-298 HTML route pattern, existing `TabBar`/`Modal`/`artifactHasContent`; cover-only render reuses `_emit_html_document`.

**Risk:** `Medium` — job `/candidate/resume/<job_id>` becomes resume-only (combined HTML removed); mitigated by new `/candidate/cover/<job_id>` and dual-tab preview Susan asked for in UAT.

Two build stages: (1) builder + API split, (2) Preview Materials button + iframe tab modal in `JobAnalysisReportModal`.

---

# UAT: Preview Materials button + resume/cover HTML preview tabs in JAR

**Linear:** https://linear.app/astralcareermatch/issue/AST-581/uat-preview-materials-button-resumecover-html-preview-tabs-in-jar  
**Parent:** https://linear.app/astralcareermatch/issue/AST-300/build-resume-artifact  
**Publish ref:** `origin/sub/AST-300/AST-581-uat-preview-materials-button-resumecover-html-preview-tabs-in-jar`

**Summary:** Susan UAT on **AST-300** found no way to preview job-tailored **resume** and **cover letter** HTML separately from the Recommended Job Report. Today `GET /candidate/resume/<job_id>` renders one combined document (resume body plus inline cover when cover content exists). This bug adds a **Preview Materials** control on the JAR header and a small preview modal with **Resume** and **Cover Letter** tabs, each loading the existing authenticated HTML routes in an `<iframe>` (AST-298 pattern — server-rendered HTML, not React print layout).

---

## Prerequisite gate (before Stage 1)

1. On **`dev-kath`**: `git fetch origin && git merge origin/dev` — merge-clean gate (`origin/dev` ancestor of HEAD, `BEHIND=0`).
2. Confirm **`origin/sub/AST-300/AST-581-uat-preview-materials-button-resumecover-html-preview-tabs-in-jar`** exists; `git merge origin/sub/AST-300/AST-581-uat-preview-materials-button-resumecover-html-preview-tabs-in-jar` (empty tip OK).
3. Parent **AST-300** is in UAT; do **not** implement sibling scope (**AST-552**, **AST-553**, chain persistence). Consume existing `job_data.artifacts.resume_content` / `cover_letter` and `builder.py` render paths only.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | Resume-only job render; new `build_cover_letter` / `build_cover_letter_from_job` | core |
| `src/ui/api/api_resume_html.py` | Job resume route resume-only; new `GET /candidate/cover/<job_id>` | ui |
| `src/ui/frontend/src/lib/recommendedJobReport.tsx` | `materialsPreviewVisible` helper | ui |
| `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` | Optional **Preview Materials** button slot | ui |
| `src/ui/frontend/src/components/MaterialsPreviewModal.tsx` | New modal: TabBar + iframe previews | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Wire visibility, open preview modal, pass `jobId` | ui |
| `src/ui/frontend/src/App.css` | Preview modal + iframe layout | ui |
| `tests/component/core/test_builder.py` | Resume-only vs cover-only HTML assertions | tests |
| `tests/component/ui/api/test_api_resume_html.py` | Cover route + resume route no longer bundles cover | tests |
| `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` | Button visibility + opens preview with tabs | tests |
| `tests/component/frontend/lib/test_recommendedJobReport.test.tsx` | `materialsPreviewVisible` cases | tests |

**Out of scope:** `ArtifactEditor` edits, dispatch/chain, `config.py` state machine changes, new artifact persistence APIs, React-side HTML rendering of resume sections.

---

## Stage 1: Split builder output and Flask HTML routes

**Done when:** `GET /candidate/resume/<job_id>` returns resume body **without** cover letter block; `GET /candidate/cover/<job_id>` returns cover letter HTML only (or 404 when no cover content); both routes stay `@require_auth` and return `text/html`.

1. In **`src/core/builder.py`**, add optional parameter to **`build_resume_from_job`**:
   ```python
   def build_resume_from_job(job: Dict[str, Any], candidate_data: Dict[str, Any], *, include_cover: bool = False) -> str:
   ```
   - Keep existing load/filter/profile/style/marker logic unchanged.
   - Replace `include_cover=cover is not None` with `include_cover=include_cover and cover is not None` (only embed cover when caller requests it **and** cover content resolves).
   - **`build_resume(job_id)`** continues to call `build_resume_from_job(..., include_cover=False)` (resume-only for job-scoped print/preview).

2. In **`src/core/builder.py`**, add public cover builders after **`build_resume`**:
   ```python
   def build_cover_letter(job_id: str) -> str:
   ```
   - Mirror **`build_resume`** job/candidate lookup (same `get_job` → `get_company` → `get_candidate` chain).
   - Delegate to **`build_cover_letter_from_job(job, candidate_row)`**.

   ```python
   def build_cover_letter_from_job(job: Dict[str, Any], candidate_data: Dict[str, Any]) -> str:
   ```
   - `cover = _resolve_cover_letter(job_data, cd)`; if `cover is None` → `raise ValueError("No cover letter content for job")`.
   - Build minimal header markers from profile only (reuse `_apply_profile_to_render_dict({}, cd.get("profile") or {})` on an empty render dict).
   - Call **`_emit_html_document`** with `include_cover=True`, `cover_letter=cover`, `critical_keywords=None`, `emit_prior_experience=False`, `body_section_ids=[]`, `body_section_titles={}`, `cover_profile=cd.get("profile") or {}`.
   - Set document `<title>` via markers: pass `candidate_name` in render dict so title is sensible (existing `_emit_html_document` uses render for title — ensure name is populated from profile step above).

3. In **`src/ui/api/api_resume_html.py`**:
   - Import `build_cover_letter` from `src.core.builder`.
   - **`resume_for_job`**: unchanged path except builder now returns resume-only (no code change beyond import if `build_resume` already delegates).
   - Add route **`@resume_html_bp.route("/cover/<job_id>")`** with `@require_auth`:
     - `html = build_cover_letter(job_id)`
     - `ValueError` → 404 JSON (same pattern as resume route)
     - Success → `Response(html, mimetype="text/html; charset=utf-8")`

4. In **`tests/component/core/test_builder.py`**, add:
   - **`test_build_resume_from_job_omits_cover_when_include_cover_false`**: job with both `resume_content` and `cover_letter`; call `build_resume_from_job(..., include_cover=False)`; assert returned HTML contains resume section markup and does **not** contain `class="cover-block"`.
   - **`test_build_resume_from_job_includes_cover_when_include_cover_true`**: same fixtures with `include_cover=True`; assert `cover-block` present.
   - **`test_build_cover_letter_from_job_emits_cover_only`**: cover dict with `Letter` body; assert HTML has `cover-block`, lacks resume `<h2>` body sections (e.g. no `professional_summary` section id from `_KEY_TO_SECTION_ID`).
   - **`test_build_cover_letter_raises_without_content`**: empty artifacts, no `sample_cover_text` → `ValueError`.

5. In **`tests/component/ui/api/test_api_resume_html.py`**, add:
   - **`test_job_cover_returns_html`**: monkeypatch `build_cover_letter` → `"<html>cover</html>"` → 200.
   - **`test_job_cover_value_error_is_404`**: monkeypatch raises `ValueError` → 404.
   - Update **`test_job_resume_returns_html`** monkeypatch expectation if test asserts combined output (resume-only is correct).

⚠️ **Decision:** Job-scoped **`/candidate/resume/<job_id>`** becomes resume-only permanently. Combined resume+cover in one HTML document is removed for job routes; dual-tab preview is the supported UX. Base resume route **`/candidate/resume/base`** unchanged.

---

## Stage 2: Preview Materials button and tabbed preview modal (JAR)

**Done when:** JAR shows **Preview Materials** when `CANDIDATE_REVIEW` or when `resume_content` / `cover_letter` has content; clicking opens a modal with **Resume** and **Cover Letter** tabs; each tab shows server HTML in an iframe; Cover tab disabled when no cover artifact content.

1. In **`src/ui/frontend/src/lib/recommendedJobReport.tsx`**, add:
   ```typescript
   export function materialsPreviewVisible(
     jobState: string,
     artifacts: unknown,
   ): boolean {
     if (jobState === "CANDIDATE_REVIEW") return true
     return (
       artifactHasContent(artifacts, "resume_content")
       || artifactHasContent(artifacts, "cover_letter")
     )
   }
   ```

2. Create **`src/ui/frontend/src/components/MaterialsPreviewModal.tsx`**:
   - Props: `{ open: boolean; onClose: () => void; jobId: string; hasCover: boolean }`
   - Import **`TabBar`** from **`./TabbedTextArea`** (same pattern as **`AdminTaskPrompts.tsx`**).
   - Tab keys: `"resume"` | `"cover"`.
   - State: `activeTab` default `"resume"`.
   - Tabs array: always `{ key: "resume", label: "Resume" }`; include `{ key: "cover", label: "Cover Letter" }` only when `hasCover` is true.
   - Render **`Modal`** (`size="wide"`, `title="Preview Materials"`, `stacked` so it layers above JAR).
   - Below TabBar, render one **`<iframe>`** (not two hidden — swap `src` on tab change):
     - Resume: `src={/candidate/resume/${encodeURIComponent(jobId)}}`
     - Cover: `src={/candidate/cover/${encodeURIComponent(jobId)}}`
   - iframe attributes: `title` matching active tab, `className="materials-preview-iframe"`, full width, fixed min-height (~480px) for readable preview.
   - No `sandbox` attribute (same-origin auth cookies must reach Flask).

3. In **`src/ui/frontend/src/components/RecommendedJobReportHeader.tsx`**:
   - Extend props with optional:
     ```typescript
     previewMaterials?: { onClick: () => void }
     ```
   - When `previewMaterials` is set, render a second button in **`recommended-report-header-actions`** **before** the primary action button:
     - `className="modal-btn cancel"` (secondary style, matches admin preview buttons)
     - Label: **`Preview Materials`**
     - `type="button"`, `onClick={previewMaterials.onClick}`

4. In **`src/ui/frontend/src/components/JobAnalysisReportModal.tsx`**:
   - Import **`MaterialsPreviewModal`** and **`materialsPreviewVisible`**.
   - State: `previewOpen: boolean` (default `false`).
   - Derive:
     ```typescript
     const artifacts = job?.job_data?.artifacts
     const showPreview = job && materialsPreviewVisible(job.state, artifacts)
     const hasCover = artifactHasContent(artifacts, "cover_letter")
     ```
   - Pass to **`RecommendedJobReportHeader`**:
     ```typescript
     previewMaterials={showPreview ? { onClick: () => setPreviewOpen(true) } : undefined}
     ```
   - Render **`MaterialsPreviewModal`** sibling inside the modal shell when `jobId` is set:
     ```tsx
     <MaterialsPreviewModal
       open={previewOpen}
       onClose={() => setPreviewOpen(false)}
       jobId={jobId}
       hasCover={hasCover}
     />
     ```

5. In **`src/ui/frontend/src/App.css`**, add (flat file, no new CSS modules):
   ```css
   .materials-preview-iframe {
     width: 100%;
     min-height: 480px;
     border: 1px solid var(--border-subtle, #ddd);
     border-radius: 4px;
     background: #fff;
   }
   .recommended-report-header-actions {
     display: flex;
     gap: 8px;
     flex-wrap: wrap;
   }
   ```
   (Extend existing `.recommended-report-header-actions` only if rule already exists — merge gap/flex into existing block rather than duplicate selector.)

6. Run **`cd src/ui/frontend && npx tsc -b --noEmit`** before stage commit.

7. In **`tests/component/frontend/lib/test_recommendedJobReport.test.tsx`**, add **`materialsPreviewVisible`** cases:
   - `CANDIDATE_REVIEW` + empty artifacts → `true`
   - `RECOMMENDED` + no artifacts → `false`
   - `BUILD_ARTIFACTS` + `resume_content` with text → `true`

8. In **`tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx`**, add:
   - **`shows Preview Materials on CANDIDATE_REVIEW`**: job state `CANDIDATE_REVIEW`, artifacts with `resume_content`; expect button **Preview Materials** visible.
   - **`hides Preview Materials on RECOMMENDED without artifacts`**: no button.
   - **`opens preview modal with Resume tab iframe`**: click button; expect modal title **Preview Materials**; expect iframe `src` containing `/candidate/resume/` and job id.
   - **`shows Cover Letter tab when cover_letter has content`**: artifacts include cover; after open, click **Cover Letter** tab; iframe `src` contains `/candidate/cover/`.

⚠️ **Decision:** In-modal iframe preview (stacked `Modal`) instead of `window.open` two tabs — keeps Susan inside JAR during UAT review while still using separate HTML render surfaces per tab. Matches acceptance “separate tabs” without losing report context.

---

## Self-Assessment

**Scope:** `Single-Component` — Touches JAR header/modal (one UI feature), thin Flask routes, and focused `builder.py` split; no dispatch, tracker, or config state changes.

**Conf:** `high` — Reuses AST-298 HTML routes, existing `TabBar`, `Modal`, and `artifactHasContent`; builder cover/resume split follows established `_emit_html_document` helpers.

**Risk:** `Medium` — Changing job resume route to resume-only alters print HTML shape for anyone bookmarking combined output; mitigated by explicit cover route and dual-tab UX Susan requested.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses `_resolve_cover_letter`, `_emit_html_document`, `artifactHasContent`; no duplicate HTML templates. |
| §2.1 config | Visibility uses job state string + artifact keys already in manifest/data — no new config blocks. |
| §3.3 imports | UI API → core only; frontend → lib/api pattern unchanged. |
| §3.5 naming | New component flat in `components/`; CSS classes prefixed `materials-preview-` / existing `recommended-report-*`. |
| §3.6 debug | No spike output; no repo-root artifacts. |

No conflicts requiring `conf-!!-NONE`.

---

## Review (build)

**Branch:** `origin/sub/AST-300/AST-581-uat-preview-materials-button-resumecover-html-preview-tabs-in-jar`  
**Tip:** `c768602c`  
**Built:** Stage 1 — `build_resume_from_job(include_cover=False)` default, `build_cover_letter` / `GET /candidate/cover/<job_id>`. Stage 2 — `materialsPreviewVisible`, `MaterialsPreviewModal`, JAR **Preview Materials** button. Component tests deferred to Betty per build-astral test-tree ban.

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-300/AST-581-uat-preview-materials-button-resumecover-html-preview-tabs-in-jar` @ `8009567651c04849d84c69d1c84d3ef869bbd99c`  
**Reviewed:** 2026-06-05

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | Stage 1 builder split + cover route and Stage 2 JAR button/modal match the approved plan and AST-581 acceptance. |
| Layering (§3.3) | `api_resume_html.py` → `src.core.builder` only; new UI pieces stay in `components/` + `lib/`; CSS merged into existing `.recommended-report-header-actions`. |
| DRY (§1.3) | Cover/resume render reuses `_resolve_cover_letter`, `_emit_html_document`, `artifactHasContent`, `TabBar`, `Modal` — no parallel HTML templates. |
| Tests | Builder split, cover route, `materialsPreviewVisible`, and JAR modal/iframe paths covered; existing AST-518 cover-alias test retargeted to cover-only builder. |
| Auth | Both `/candidate/resume/<job_id>` and new `/candidate/cover/<job_id>` keep `@require_auth`; iframe omits `sandbox` so session cookies reach Flask (plan decision). |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **discuss** | `recommendedJobReport.tsx` — `materialsPreviewVisible` | Hardcodes `CANDIDATE_REVIEW` in frontend lib (§3.2 G1 prefers manifest/API-resolved visibility). Plan and acceptance explicitly chose this; same family as `CandidateJobRowActions` state sets. Not blocking for UAT bugfix — flag if we want a manifest `preview_materials` flag per recommended state later. |
| **advisory** | `MaterialsPreviewModal.tsx` | `activeTab` persists across close/reopen (`useState` not reset on `onClose`). Low UX impact. |
| **advisory** | `materialsPreviewVisible` + iframe | `CANDIDATE_REVIEW` shows Preview even with empty artifacts (per plan); resume iframe may 404 until chain populates content. |
| **advisory** | `build_resume` / job resume route | Job-scoped resume HTML is permanently resume-only; combined print removed. Documented plan decision — confirm Susan UAT expectation. |

### Recommended actions

| Action | Owner |
|--------|-------|
| Proceed to `resolve-astral` — no fix-now items | Katherine |
| Optional: reset `activeTab` to `"resume"` when preview modal closes | Katherine (resolve) |
| Optional: manifest-driven preview visibility in a follow-up | Susan / dispatch |

---

## Resolution

**Resolved:** 2026-06-05  
**Publish ref:** `origin/sub/AST-300/AST-581-uat-preview-materials-button-resumecover-html-preview-tabs-in-jar`

### vs Radia review

| Item | Outcome |
|------|---------|
| **fix-now** | None — no product changes required for UAT acceptance. |
| **discuss** (`materialsPreviewVisible` + `CANDIDATE_REVIEW`) | Left as planned; plan and acceptance explicitly chose frontend state check. Follow-up manifest flag deferred. |
| **advisory** (tab reset on close) | `MaterialsPreviewModal` resets `activeTab` to `"resume"` when `open` becomes false (`useEffect`). |
| **advisory** (empty artifacts / 404 iframe) | Accepted per plan — Preview visible in `CANDIDATE_REVIEW` before chain populates content. |
| **advisory** (resume-only job route) | Documented plan decision; dual-tab preview is the supported UX. |
