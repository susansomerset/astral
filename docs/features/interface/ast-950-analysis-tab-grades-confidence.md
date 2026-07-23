# Analysis tab grades and confidence (Redesign Recommended Job Modal)

**Linear:** [AST-950](https://linear.app/astralcareermatch/issue/AST-950/analysis-tab-grades-and-confidence-redesign-recommended-job-modal)  
**Parent:** [AST-858 — Redesign Recommended Job Modal](https://linear.app/astralcareermatch/issue/AST-858/redesign-recommended-job-modal)  
**Publish ref (origin):** `sub/AST-858/AST-950-analysis-tab-grades-confidence`  
**Parent integration ref:** `ftr/AST-858-redesign-recommended-job-modal`  
**Blocked by:** [AST-948](https://linear.app/astralcareermatch/issue/AST-948/modal-shell-horizontal-tabs-sticky-header-redesign-recommended-job) (shell / `ReportSectionList` / `report_phase_tabs` as Analysis sections)

Fill Analysis tab phase sections (no Overview): **JD Analysis** default expanded; **DO / GET / LIKE Analysis**. Each section header shows a **horizontal** grade-icon row **with confidence dots** for every graded vector (visible collapsed or expanded). Expanded body shows that phase’s Estelle upshot (`take_jd` / `take_do` / `take_get` / `take_like`) **above** the hydrated per-vector rubric display (`AgentAnalysisHeader`). Does **not** own Summary/Artifacts bodies, shell/header, or consult scoring.

---

## Prerequisite gate (before Stage 1 of build-child)

1. On epic worktree: `git fetch origin`; checkout `sub/AST-858/AST-950-analysis-tab-grades-confidence`; `git merge origin/dev`; `git merge origin/ftr/AST-858-redesign-recommended-job-modal`; merge-clean gate.
2. Merge **`origin/sub/AST-858/AST-948-modal-shell-horizontal-tabs-sticky-header`** (or rolled-up `origin/ftr/…`) so Analysis `ReportSectionList` exists with empty `renderSection`, sections from `report_phase_tabs` (`section_id` = `tab_id`), and `phase_jd` default expanded.
3. If `ReportSectionList` / `report_phase_tabs` wiring is missing, **stop** — comment on AST-950; do not rebuild shell.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/ReportSectionList.tsx` | Optional `renderMetadata?(sectionId) => ReactNode` → `CollapsiblePanel` `metadata` | ui |
| `src/ui/frontend/src/lib/recommendedJobReport.tsx` | Add horizontal grade+confidence header-row helper (importance order; includes `ConfidenceBullets`) | ui |
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Wire Analysis `renderMetadata` + `renderSection` (upshot above `AgentAnalysisHeader`); restore grades helpers as needed | ui |
| `src/ui/frontend/src/App.css` | Compact horizontal grade+confidence row under recommended-report / analysis header (reuse `--confidence-*` / `.grade-dot`) | ui |

**Out of scope:** Summary bodies (AST-949); Artifacts (AST-951); shell/header (AST-948); changing `AgentAnalysisHeader` public API unless a one-line prop is required for layout; scoring/dispatch; `tests/` / bible (Betty).

**QA note (Betty):** Assert four Analysis sections (no Overview); JD default expanded; header grade+confidence visible when collapsed; expanded body shows `take_*` above rubric rows; missing upshot/grades → empty states, no crash.

---

## Stage 1: `ReportSectionList` metadata slot

**Done when:** Callers may pass optional `renderMetadata`; each panel sets `CollapsiblePanel` `metadata={renderMetadata?.(section_id)}`. Summary/Artifacts callers unchanged when omitted.

1. In `ReportSectionList.tsx`, extend props:

   ```tsx
   renderMetadata?: (sectionId: string) => ReactNode
   ```

2. Pass through to `CollapsiblePanel`: `metadata={renderMetadata?.(section.section_id)}` (omit / undefined when callback absent or returns null/undefined — CollapsiblePanel already skips null/false).

3. Do **not** change expand policy, `leading`, or `renderSection` contracts from AST-948.

---

## Stage 2: Horizontal grade + confidence header helper

**Done when:** A shared helper returns a horizontal row of grade-dot + `ConfidenceBullets` for every graded vector in rubric importance order (or raw grade order when rubric missing). Letter-only `buildPhaseTabGradeDots` is **not** used for this header (it lacks confidence).

1. In `src/ui/frontend/src/lib/recommendedJobReport.tsx`, add (name exact):

   ```tsx
   export function buildPhaseSectionGradeConfidenceRow(
     gradesRaw: unknown,
     rubricArtifactKey: string | undefined,
     candidateArtifacts: Record<string, unknown>,
   ): ReactNode
   ```

2. Behavior:

   - Build ordered rubric columns the same way as `buildPhaseTabGradeDots` (`buildJobListRubricColumnsFromArtifact` + `sortJobListRubricColumns`) when `rubricArtifactKey` resolves to an array on `candidateArtifacts`.
   - For each column, resolve grade + confidence from `gradesRaw` (array rows include `confidence`; object map form → confidence omitted / bullets dim — same as list pages).
   - Skip columns with no grade letter.
   - Each cell: wrap `<span className="grade-dot …">` + `<ConfidenceBullets confidence={…} />` in a compact block (class `recommended-report-phase-grade-cell`); tooltip via `formatGradeDotTooltip` on the grade-dot.
   - If rubric artifact missing/empty but `gradesRaw` is a nonempty array, fall back to array order (vector/grade/confidence) so headers still render.
   - Return `null` when no graded cells.

3. In `App.css`, add a horizontal flex row for the metadata slot, e.g. `.recommended-report-phase-grade-row` (flex, wrap, gap) and `.recommended-report-phase-grade-cell` (column align center — grade above bullets, matching `.analysis-grade-block` density but tighter for headers). Do not invent new grade colors.

⚠️ **Decision:** New helper instead of overloading `buildPhaseTabGradeDots` — old helper is letter-only rail labels; Analysis header AC explicitly requires confidence. Leave `buildPhaseTabGradeDots` in place if still referenced elsewhere; if unused after AST-948, do not delete in this ticket.

---

## Stage 3: Wire Analysis tab bodies + header metadata

**Done when:** Analysis tab shows only JD/DO/GET/LIKE sections; JD expanded by default (AST-948 seed); each header shows the confidence grade row when grades exist; expanded body = phase `take_*` (if any) above `AgentAnalysisHeader`; missing upshot/grades → empty copy, no crash; no Overview section.

1. In `JobAnalysisReportModal.tsx` Analysis `ReportSectionList`:

   - Keep sections from `manifest.jobs.recommended.report_phase_tabs` with `section_id = tab_id`, `nav_label` from manifest, `default_expanded = (tab_id === "phase_jd")` (unchanged from AST-948).
   - Always render all four phase sections from the manifest (do **not** gate the section list on `parseAnalysisUpshot` truthiness — empty bodies handle missing data).
   - `renderMetadata(sectionId)`: find phase row; `gradesRaw = jobGradesForField(job, phase.grades_field)`; `rubricKey = manifest.jobs.grade_rubric_by_field[phase.grades_field]`; return `buildPhaseSectionGradeConfidenceRow(gradesRaw, rubricKey, candidateArtifacts)` (or null).
   - `renderSection(sectionId)`:
     - Resolve phase + `parseAnalysisUpshot(job.job_data?.analysis_upshot)`.
     - Upshot block: `takeBody = parsed?.[phase.take_key]` when string + trim; render with existing `.job-analysis-upshot-body` (no duplicate section heading inside the panel). If missing/empty, omit the upshot block (do not fail the section).
     - Rubric block: build grades via the same `gradesForHeader`-style normalization already used pre-redesign (vector/grade/confidence/reason). If `grades.length > 0`, render `<AgentAnalysisHeader grades={grades} rubricArtifact={rubricKey} />`. Else `<p className="recommended-report-empty">No consult detail on file.</p>`.
     - If both upshot and grades are empty, still show the empty consult line (header metadata may also be empty).

2. Re-import `AgentAnalysisHeader`, `jobGradesForField`, and restore a local `gradesForHeader` helper (or move it to `recommendedJobReport.tsx` if that keeps the modal thinner — prefer lib if the function is >~15 lines and shared with the header helper’s array parsing).

3. Do **not** add an Overview section. Do **not** put `AgentAnalysisHeader` in the collapsed header — header is the compact grade+confidence row only; body owns the full rubric list with reasons / “show rubric”.

4. `npx tsc -b --noEmit` for touched frontend files.

⚠️ **Decision:** Compact header row ≠ `AgentAnalysisHeader`. Header = glanceable grade+confidence; body = Estelle take + full colorful rubric (`AgentAnalysisHeader`). Matches parent AC split and avoids duplicating reason text in the sticky section chrome.

---

## Self-Assessment

**Scope:** Single-Component — Analysis tab wiring in the Recommended report modal plus a small `ReportSectionList` metadata hook and a grade+confidence row helper/CSS.

**Conf:** high — reuses `ConfidenceBullets`, rubric column sort, `AgentAnalysisHeader`, `jobGradesForField`, and AST-948 section ids; ticket explicitly points at these patterns.

**Risk:** Medium — wrong header helper (letter-only) would miss AC #4; putting full `AgentAnalysisHeader` only in the header would hide reasons when expanded or bloat collapsed chrome; gating sections on upshot would hide DO/GET/LIKE when partial.

---

## Code rules check

- **§1.3 DRY:** One metadata helper; reuse rubric sort / tooltip / `ConfidenceBullets`; do not fork a second AgentAnalysisHeader.
- **§1.4 / §2.1:** Phase section ids/labels/grades_field/take_key stay manifest-driven (`report_phase_tabs`).
- **§2.4 / §2.6:** N/A — presentation only.
- **§3.3 / §3.5:** Frontend components + `App.css` only.
- **Tests / bible:** Betty owns.
