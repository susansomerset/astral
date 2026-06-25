<!-- linear-archive: AST-605 archived 2026-06-23 -->

## Linear archive (AST-605)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-605/preview-materials-button-resumecover-html-preview-tabs-rebuild-581-git  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-599 — Rebuild 581 (git casualty)  
**Blocked by / blocks / related:** parent: AST-599

### Description

## What this implements

Recreate AST-581 Preview Materials UX lost in git merges.

## Acceptance criteria

1. JAR shows Preview Materials when CANDIDATE_REVIEW or resume/cover content exists.
2. Separate resume and cover letter preview tabs.
3. Uses job_data.artifacts.resume_content and cover_letter.

## Notes for planning

Reference: docs/features/artifacts/ast-581-uat-preview-materials-button-resumecover-html-preview-tabs-in-jar.md

### Comments

#### radia — 2026-06-12T00:17:31.111Z
**Review (Radia)** — diff `origin/dev...origin/sub/AST-599/AST-605-preview-materials-jar-tabs-rebuild-581` @ `b52a9c85` (product @ `b67245f2` + Radia doc append).

### What's solid

- **AC:** `materialsPreviewVisible` gates **Preview Materials** on `CANDIDATE_REVIEW` or non-empty `resume_content` / `cover_letter`; `MaterialsPreviewModal` (pre-existing) serves Resume + optional Cover Letter iframes via `/candidate/resume/<job_id>` and `/candidate/cover/<job_id>`.
- **Backend:** `build_resume_from_job(..., include_cover=False)` default; `build_cover_letter` + cover route mirror AST-581; `@require_auth`, 404 on `ValueError`.
- **Layers / debug:** UI API → core only; no new `debug=` contract paths in diff.
- **Tests:** AST-581 component tests + bible §7.13zx manifest cover this rebuild.

### Issues

| Severity | Location | Finding |
| --- | --- | --- |
| **discuss** | `JobAnalysisReportModal` / `MaterialsPreviewModal` | Cover tab uses `artifactHasContent(cover_letter)` only; server `_resolve_cover_letter` can fall back to candidate `sample_cover_text` — on `CANDIDATE_REVIEW` with sample-only cover, preview opens but Cover tab hidden while cover route may 200. AC names artifact keys only. |
| **advisory** | `builder.py` | `build_cover_letter` duplicates `build_resume` lookup chain — intentional AST-581 mirror. |
| **advisory** | `recommendedJobReport.tsx` | Hardcoded `CANDIDATE_REVIEW` visibility string (AST-581 pattern). |

**fix-now:** none.

### Doc

Combined plan + review: `docs/features/interface/ast-605-preview-materials-button-resumecover-html-preview-tabs-rebuild-581.md` on publish ref @ `b52a9c85`.

**Next:** Katherine — **resolve-astral** (happy path).

#### betty — 2026-06-12T00:13:03.666Z
**Tests Ready** — manifest for `test-astral` (Katherine).

**Coverage class:** Existing bible-backed tests from original **AST-581** ship — manifest-only pass; no new test files.

**Publish ref:** `origin/sub/AST-599/AST-605-preview-materials-jar-tabs-rebuild-581` @ `b67245f2`

**`docs/ASTRAL_TEST_BIBLE.md` shasum** on publish ref: `c6f722b8febe6c424739f58fbe8162c392a7e7c4dd2b604c00e8047add209a1d` (**§7.13zx**)

### Manifest

1. **Builder resume/cover split** — `tests/component/core/test_builder.py::TestAst581ResumeCoverSplit`
2. **Cover HTML route** — `tests/component/ui/api/test_api_resume_html.py::TestAst581CoverRoute`
3. **`materialsPreviewVisible` helper** — `tests/component/frontend/lib/test_recommendedJobReport.test.tsx` (describe **AST-581 materialsPreviewVisible**)
4. **JAR Preview Materials button + tabbed modal iframes** — `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` (describe **JobAnalysisReportModal — AST-581 Preview Materials**)

### Narrowed run

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst581ResumeCoverSplit \
  tests/component/ui/api/test_api_resume_html.py::TestAst581CoverRoute
cd src/ui/frontend && npx tsc -b --noEmit
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_recommendedJobReport.test.tsx \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx
```

**§6c note:** JAR is a modal component (`JobAnalysisReportModal`), not a routed page — component-level RTL coverage is sufficient.

— Betty

#### katherine — 2026-06-12T00:08:40.160Z
Plan: [ast-605-preview-materials-button-resumecover-html-preview-tabs-rebuild-581.md](https://github.com/susansomerset/astral/blob/sub/AST-599/AST-605-preview-materials-jar-tabs-rebuild-581/docs/features/interface/ast-605-preview-materials-button-resumecover-html-preview-tabs-rebuild-581.md) @ `21d3ca99`

Rebuilds AST-581 Preview Materials UX (2 stages: builder/API split + JAR wiring). Git casualty note: `MaterialsPreviewModal` and tests survive on dev; product wiring and cover route are missing.

**Self-assessment**
- **Scope:** `Single-Component` — JAR header/modal, thin Flask routes, focused `builder.py` split only.
- **Conf:** `high` — AST-581 reference plan + existing tests define exact behavior; proven pattern to re-apply.
- **Risk:** `Medium` — job resume route becomes resume-only; cover moved to `/candidate/cover/<job_id>`.

---

# Preview Materials button + resume/cover HTML preview tabs (Rebuild 581)

**Linear:** https://linear.app/astralcareermatch/issue/AST-605/preview-materials-button-resumecover-html-preview-tabs-rebuild-581-git  
**Parent:** https://linear.app/astralcareermatch/issue/AST-599/rebuild-581-git-casualty  
**Publish ref:** `origin/sub/AST-599/AST-605-preview-materials-jar-tabs-rebuild-581`  
**Reference (original ship):** `docs/features/artifacts/ast-581-uat-preview-materials-button-resumecover-html-preview-tabs-in-jar.md`

**Summary:** Rebuild AST-581 Preview Materials UX lost in git merges. The JAR (Recommended Job Report modal) gets a **Preview Materials** header button and a stacked preview modal with **Resume** and **Cover Letter** tabs, each loading authenticated server-rendered HTML in an `<iframe>`. Backend splits job resume HTML from cover letter HTML via separate Flask routes. Data source: `job_data.artifacts.resume_content` and `job_data.artifacts.cover_letter`.

---

## Prerequisite gate (before Stage 1)

1. On **`dev-kath`**: `git fetch origin && git merge origin/dev` — merge-clean gate (`origin/dev` ancestor of HEAD, `BEHIND=0`).
2. Parent **AST-599** is **In Progress**: `git merge origin/ftr/AST-599-rebuild-581-git-casualty`.
3. Confirm **`origin/sub/AST-599/AST-605-preview-materials-jar-tabs-rebuild-581`** exists; `git merge origin/sub/AST-599/AST-605-preview-materials-jar-tabs-rebuild-581` (empty tip OK).
4. **Git casualty inventory on `origin/dev` (do not re-plan sibling AST-599 children):**
   - **Present:** `MaterialsPreviewModal.tsx`, component tests in `test_JobAnalysisReportModal.test.tsx`, `test_recommendedJobReport.test.tsx`, `test_builder.py`, `test_api_resume_html.py`.
   - **Missing / broken:** `build_resume_from_job` still bundles cover (`include_cover=cover is not None`); no `build_cover_letter` / cover route; no `materialsPreviewVisible`; `RecommendedJobReportHeader` has no preview slot; `JobAnalysisReportModal` does not wire preview; `App.css` lacks `.materials-preview-iframe` flex on header actions.
5. **Out of scope:** dispatch/chain persistence, `config.py` state machine changes, new artifact persistence APIs, React-side HTML rendering, sibling tickets under AST-599.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | Resume-only job render (`include_cover` param); new `build_cover_letter` / `build_cover_letter_from_job` | core |
| `src/ui/api/api_resume_html.py` | Job resume route resume-only; new `GET /candidate/cover/<job_id>` | ui |
| `src/ui/frontend/src/lib/recommendedJobReport.tsx` | Add `materialsPreviewVisible` helper | ui |
| `src/ui/frontend/src/components/RecommendedJobReportHeader.tsx` | Optional **Preview Materials** button slot | ui |
| `src/ui/frontend/src/components/MaterialsPreviewModal.tsx` | Verify only (file exists; no functional change unless drift from spec) | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Wire visibility, open preview modal, pass `jobId` | ui |
| `src/ui/frontend/src/App.css` | Preview modal iframe + header actions flex | ui |

**Tests (already on dev — must pass after build; do not add new test files in this ticket):**

| File | Role |
|------|------|
| `tests/component/core/test_builder.py` | Resume-only vs cover-only HTML |
| `tests/component/ui/api/test_api_resume_html.py` | Cover route + resume route |
| `tests/component/frontend/lib/test_recommendedJobReport.test.tsx` | `materialsPreviewVisible` |
| `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` | Button visibility + preview modal iframes |

---

## Stage 1: Split builder output and Flask HTML routes

**Done when:** `GET /candidate/resume/<job_id>` returns resume body **without** cover letter block; `GET /candidate/cover/<job_id>` returns cover letter HTML only (or 404 when no cover content); both routes stay `@require_auth` and return `text/html`; `tests/component/core/test_builder.py` and `tests/component/ui/api/test_api_resume_html.py` pass for AST-581/605 cases.

1. In **`src/core/builder.py`**, change **`build_resume_from_job`** signature to:
   ```python
   def build_resume_from_job(
       job: Dict[str, Any],
       candidate_data: Dict[str, Any],
       *,
       include_cover: bool = False,
   ) -> str:
   ```
   - Keep existing load/filter/profile/style/marker logic unchanged.
   - After `cover = _resolve_cover_letter(job_data, cd)`, replace `include_cover=cover is not None` in the `_emit_html_document` call with `include_cover=include_cover and cover is not None`.
   - Update module docstring public list to include `build_cover_letter`, `build_cover_letter_from_job`.

2. In **`src/core/builder.py`**, add after **`build_resume`**:
   ```python
   def build_cover_letter(job_id: str) -> str:
   ```
   - Mirror **`build_resume`** job/candidate lookup (`get_job` → `get_company` → `get_candidate`).
   - Delegate to **`build_cover_letter_from_job(job, _coerce_candidate_blob(row))`**.

   ```python
   def build_cover_letter_from_job(job: Dict[str, Any], candidate_data: Dict[str, Any]) -> str:
   ```
   - `cd = _coerce_candidate_blob(candidate_data)`; `job_data = job.get("job_data")` (dict or `{}`).
   - `cover = _resolve_cover_letter(job_data, cd)`; if `cover is None` → `raise ValueError("No cover letter content for job")`.
   - Build header markers from profile only: `render = {}`; `_apply_profile_to_render_dict(render, cd.get("profile") or {})`; `markers = _apply_resume_text_markers(render)`.
   - `style = _merge_effective_style(cd)`.
   - Call **`_emit_html_document`** with:
     - `include_cover=True`
     - `cover_letter=cover`
     - `critical_keywords=None`
     - `emit_prior_experience=False`
     - `body_section_ids=[]`
     - `body_section_titles={}`
     - `cover_profile=cd.get("profile") or {}`

3. In **`src/ui/api/api_resume_html.py`**:
   - Change import to: `from src.core.builder import build_base_resume, build_cover_letter, build_resume`.
   - **`resume_for_job`**: no route body change ( **`build_resume`** → **`build_resume_from_job(..., include_cover=False)`** via default).
   - Add route **`@resume_html_bp.route("/cover/<job_id>")`** with `@require_auth`:
     ```python
     def cover_for_job(job_id: str):
         try:
             html = build_cover_letter(job_id)
         except ValueError as exc:
             return jsonify({"error": str(exc)}), 404
         return Response(html, mimetype="text/html; charset=utf-8")
     ```

4. Run before stage commit:
   ```bash
   python -m pytest tests/component/core/test_builder.py -k "include_cover or build_cover_letter" -q
   python -m pytest tests/component/ui/api/test_api_resume_html.py -q
   ```

⚠️ **Decision:** Job-scoped **`/candidate/resume/<job_id>`** becomes resume-only permanently (default `include_cover=False`). Combined resume+cover in one HTML document is removed for job routes; dual-tab preview is the supported UX. Base resume route **`/candidate/resume/base`** unchanged.

---

## Stage 2: Preview Materials button and tabbed preview modal (JAR)

**Done when:** JAR shows **Preview Materials** when `CANDIDATE_REVIEW` or when `resume_content` / `cover_letter` has content; clicking opens modal with **Resume** and **Cover Letter** tabs; each tab shows server HTML in an iframe; Cover tab omitted when no cover artifact content; frontend component tests pass.

1. In **`src/ui/frontend/src/lib/recommendedJobReport.tsx`**, add after **`artifactHasContent`**:
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

2. **Verify** **`src/ui/frontend/src/components/MaterialsPreviewModal.tsx`** matches spec (do not rewrite if already correct):
   - Props: `{ open, onClose, jobId, hasCover }`.
   - **`TabBar`** from **`./TabbedTextArea`**; tabs `"resume"` | `"cover"`; cover tab only when `hasCover`.
   - Single **`<iframe className="materials-preview-iframe">`** with `src` `/candidate/resume/${encodeURIComponent(jobId)}` or `/candidate/cover/...`.
   - **`Modal`**: `size="wide"`, `title="Preview Materials"`, `stacked`.
   - **`useEffect`**: reset `activeTab` to `"resume"` when `open` becomes false.
   - No `sandbox` on iframe.

3. In **`src/ui/frontend/src/components/RecommendedJobReportHeader.tsx`**:
   - Extend **`Props`** with optional `previewMaterials?: { onClick: () => void }`.
   - Destructure `previewMaterials` in the component params.
   - Replace the `{primaryAction && (` actions block with:
     ```tsx
     {(previewMaterials || primaryAction) && (
       <div className="recommended-report-header-actions">
         {previewMaterials && (
           <button
             type="button"
             className="modal-btn cancel"
             onClick={previewMaterials.onClick}
           >
             Preview Materials
           </button>
         )}
         {primaryAction && (
           <button
             type="button"
             className="modal-btn save"
             disabled={primaryBusy || applyDisabled}
             onClick={onPrimaryAction}
           >
             {primaryBusy ? "Working…" : primaryAction.label}
           </button>
         )}
       </div>
     )}
     ```

4. In **`src/ui/frontend/src/components/JobAnalysisReportModal.tsx`**:
   - Add imports: `MaterialsPreviewModal` from `./MaterialsPreviewModal`; `materialsPreviewVisible` from `../lib/recommendedJobReport`.
   - Add state: `const [previewOpen, setPreviewOpen] = useState(false)`.
   - After job loads, derive:
     ```typescript
     const artifacts = job?.job_data?.artifacts
     const showPreview = !!(job && materialsPreviewVisible(job.state, artifacts))
     const hasCover = artifactHasContent(artifacts, "cover_letter")
     ```
   - Pass to **`RecommendedJobReportHeader`**:
     ```typescript
     previewMaterials={showPreview ? { onClick: () => setPreviewOpen(true) } : undefined}
     ```
   - Render **`MaterialsPreviewModal`** as sibling inside the outer modal when `jobId` is set:
     ```tsx
     {jobId && (
       <MaterialsPreviewModal
         open={previewOpen}
         onClose={() => setPreviewOpen(false)}
         jobId={jobId}
         hasCover={hasCover}
       />
     )}
     ```

5. In **`src/ui/frontend/src/App.css`**, extend existing **`.recommended-report-header-actions`** block (line ~628) to add flex layout:
   ```css
   .recommended-report-header-actions {
     margin-top: 12px;
     display: flex;
     gap: 8px;
     flex-wrap: wrap;
   }
   ```
   Add new rule after that block:
   ```css
   .materials-preview-iframe {
     width: 100%;
     min-height: 480px;
     border: 1px solid var(--border-subtle, #ddd);
     border-radius: 4px;
     background: #fff;
   }
   ```

6. Run before stage commit:
   ```bash
   cd src/ui/frontend && npx tsc -b --noEmit
   python -m pytest tests/component/frontend/lib/test_recommendedJobReport.test.tsx -q
   python -m pytest tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx -k "Preview Materials or preview modal or Cover Letter tab" -q
   ```

⚠️ **Decision:** In-modal iframe preview (stacked `Modal`) instead of `window.open` — keeps review inside JAR while using separate HTML render surfaces per tab (AST-581 UAT choice).

---

## Self-Assessment

**Scope:** `Single-Component` — JAR header/modal (one UI feature), thin Flask routes, focused `builder.py` split; no dispatch, tracker, or config state changes.

**Conf:** `high` — AST-581 plan and tests already define exact behavior; `MaterialsPreviewModal` and test tree survive on dev; rebuild follows proven AST-581 pattern.

**Risk:** `Medium` — Job resume route becomes resume-only; anyone expecting combined print HTML must use cover tab/route; mitigated by explicit `/candidate/cover/<job_id>` and dual-tab UX.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses `_resolve_cover_letter`, `_emit_html_document`, `artifactHasContent`, `TabBar`, `Modal`; no duplicate HTML templates. |
| §2.1 config | Visibility uses job state string + artifact keys already in data — no new config blocks. |
| §3.3 imports | UI API → core only; frontend → lib/components pattern unchanged. |
| §3.5 naming | Components flat in `components/`; CSS classes `materials-preview-*` / existing `recommended-report-*`. |
| §3.6 debug | No spike output; no repo-root artifacts. |

No conflicts requiring `conf-!!-NONE`.

---

## Review (build)

**Branch:** `origin/sub/AST-599/AST-605-preview-materials-jar-tabs-rebuild-581`  
**Tip:** `e77aff10` (Stage 2 publish; Stage 1 @ `4c4026ab`)  
**Built:** Stage 1 — `build_resume_from_job(include_cover=False)` default, `build_cover_letter` / `GET /candidate/cover/<job_id>`. Stage 2 — `materialsPreviewVisible`, JAR **Preview Materials** button + `MaterialsPreviewModal` wiring, CSS. Component tests deferred to Betty per build-astral test-tree ban.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-599/AST-605-preview-materials-jar-tabs-rebuild-581` @ `b67245f2` (8 files: `builder.py`, `api_resume_html.py`, JAR/header/lib/CSS, plan doc, bible §7.13zx).

### What's solid

| Area | Notes |
|------|--------|
| **Plan fidelity (AC)** | (1) `materialsPreviewVisible` — `CANDIDATE_REVIEW` or non-empty `resume_content` / `cover_letter` artifacts; (2) `MaterialsPreviewModal` (unchanged on dev) — Resume + optional Cover Letter tabs with authenticated iframe routes; (3) data from `job_data.artifacts` via existing `_resolve_resume_sections` / `_resolve_cover_letter`. |
| **Stage 1 backend** | `build_resume_from_job(..., include_cover=False)` default splits job resume HTML from cover; `build_cover_letter` / `build_cover_letter_from_job` + `GET /candidate/cover/<job_id>` mirror AST-581 plan; `@require_auth` and 404-on-`ValueError` match resume route. |
| **Stage 2 JAR** | Header slot shows **Preview Materials** when visible; stacked modal; `.materials-preview-iframe` + flex on header actions. |
| **§3.3 layers** | `api_resume_html.py` → `src.core.builder` only; frontend imports lib/components — no `src/data` / `src/external` in UI diff. |
| **§1.5 / §5f debug** | No new `debug=` surfaces or contract logging in touched backend files. |
| **Self-Assessment** | `scope-Single-Component` matches footprint (builder split + thin routes + JAR wiring); no `conf-!!-NONE`. |
| **Tests** | AST-581 component tests on dev cover builder split, cover route, `materialsPreviewVisible`, and JAR button/modal; bible §7.13zx manifest matches Betty's narrowed run. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **discuss** | `JobAnalysisReportModal.tsx` / `MaterialsPreviewModal` | Cover tab visibility uses `artifactHasContent(artifacts, "cover_letter")`; server `_resolve_cover_letter` can still render from candidate `sample_cover_text`. On `CANDIDATE_REVIEW` with sample-only cover, preview opens but Cover tab is hidden while `/candidate/cover/<job_id>` may succeed — edge case; AC names artifact keys only. |
| **advisory** | `builder.py` | `build_cover_letter` duplicates `build_resume` job→company→candidate lookup — intentional AST-581 mirror; optional future `_load_job_candidate_blob(job_id)` helper if a third builder entry point appears. |
| **advisory** | `recommendedJobReport.tsx` | Hardcoded `"CANDIDATE_REVIEW"` for visibility (§3.2 G1 pattern from AST-581); manifest-driven visibility would be a separate refactor. |

### Recommended actions

| Action | Owner |
|--------|--------|
| **resolve-astral:** no **fix-now** items — proceed on happy path. | Katherine |
| **Optional:** align Cover tab with server fallback (`sample_cover_text`) if UAT hits sample-only jobs. | Katherine / Susan |

---

## Resolution

**Resolved:** 2026-06-11  
**Publish ref:** `origin/sub/AST-599/AST-605-preview-materials-jar-tabs-rebuild-581`

### vs Radia review

| Item | Outcome |
|------|---------|
| **fix-now** | None — no product changes required. |
| **discuss** (Cover tab vs `sample_cover_text` fallback) | Left as planned; AC names `job_data.artifacts` keys only. Same AST-581 behavior. Optional UAT follow-up if sample-only cover jobs matter. |
| **advisory** (`build_cover_letter` lookup duplication) | Accepted per AST-581 mirror; no refactor in this rebuild. |
| **advisory** (hardcoded `CANDIDATE_REVIEW` visibility) | Accepted per AST-581 pattern; manifest-driven visibility deferred. |

**§9a:** publish ref merges cleanly into `origin/dev` and `origin/ftr/AST-599-rebuild-581-git-casualty`.
