# Summary tab sections (Redesign Recommended Job Modal)

**Linear:** [AST-949](https://linear.app/astralcareermatch/issue/AST-949/summary-tab-sections-redesign-recommended-job-modal)  
**Parent:** [AST-858 — Redesign Recommended Job Modal](https://linear.app/astralcareermatch/issue/AST-858/redesign-recommended-job-modal)  
**Publish ref (origin):** `sub/AST-858/AST-949-summary-tab-sections`  
**Parent integration ref:** `ftr/AST-858-redesign-recommended-job-modal`  
**Blocked by:** [AST-948](https://linear.app/astralcareermatch/issue/AST-948/modal-shell-horizontal-tabs-sticky-header-redesign-recommended-job) (modal shell / `ReportSectionList` / `report_summary_sections`)

Fill the Summary tab section bodies left empty by AST-948: **Job Summary** (`whole_jd_upshot`), **Company Upshot** (`prefilter_company_notes` from the company record), **Noteworthy Caveats** / **Questions to Ask** (`analysis_upshot`), and **Raw Job Description** (`job_data.job_description`, collapsed by default). Graceful empty states when upshot or fields are missing — no crash. Does **not** touch Analysis / Artifacts bodies, shell, or header.

---

## Prerequisite gate (before Stage 1 of build-child)

1. On epic worktree: `git fetch origin`; checkout `sub/AST-858/AST-949-summary-tab-sections`; `git merge origin/dev`; `git merge origin/ftr/AST-858-redesign-recommended-job-modal`; merge-clean gate (`BEHIND=0`, `origin/dev` ancestor of `HEAD`).
2. Merge **`origin/sub/AST-858/AST-948-modal-shell-horizontal-tabs-sticky-header`** (or `origin/ftr/…` after AST-948 is rolled up) so `ReportSectionList`, `report_summary_sections`, and Summary tab `renderSection={() => null}` exist.
3. If `ReportSectionList` or `report_summary_sections` is missing after that merge, **stop** — comment on AST-949 naming the missing symbol/SHA; do not reimplement shell chrome.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | Load company `prefilter_company_notes`; implement Summary `renderSection` bodies; content-aware `default_expanded` for company/caveats/questions | ui |
| `src/ui/frontend/src/App.css` | Only if Summary empty/list body needs a missing class under existing `job-analysis-upshot-*` / `recommended-report-empty` — prefer reuse; no new design system | ui |

**Out of scope:** AST-948 shell/header/tabs; Analysis grade headers (AST-950); Artifacts generate/edit (AST-951); `JobsRecommended` list/Skip; config/manifest section id changes (owned by AST-948); any `tests/` or `docs/test-bible/**` edits (Betty).

**QA note (Betty):** Frontend tests should assert Summary section bodies (job summary text, company notes, caveats/questions lists, collapsed Raw JD) and empty-state copy when `analysis_upshot` / notes / JD are missing.

---

## Stage 1: Company notes on the existing company fetch

**Done when:** Opening the report still fetches `/api/companies/<company>` once; modal state holds both `companyWebsite` and `companyNotes` (`prefilter_company_notes` string or null). No new API route.

1. In `JobAnalysisReportModal.tsx`, extend the existing company `api(`/api/companies/…`)` `.then` (already used for `company_website` per AST-948 / current modal):

   - Read `co?.prefilter_company_notes` (top-level — `api_companies._lift_company_notes` already lifts it from `company_data`).
   - If typeof string and `.trim()`, store trimmed string in new state `companyNotes`; else `null`.
   - Reset `companyNotes` to `null` at the start of `load()` / when `jobId` clears, same as website.

2. Do **not** add a second company request. Do **not** read notes from `job_data`.

---

## Stage 2: Summary `renderSection` bodies + empty states

**Done when:** On the Summary tab, each of the five `report_summary_sections` ids renders real content or a clear empty state; missing/partial `analysis_upshot` does not throw; Raw JD uses existing JD text normalization.

1. Keep using AST-948’s Summary `ReportSectionList` with manifest `report_summary_sections`. Replace `renderSection={() => null}` with a `renderSummarySection(sectionId: string)` that switches on `section_id` exactly:

   | `section_id` | Body |
   |--------------|------|
   | `job_summary` | If `parseAnalysisUpshot(job.job_data.analysis_upshot)` yields a string `whole_jd_upshot.trim()`, render it as a paragraph using existing `.job-analysis-upshot-body` (no extra heading inside the panel — panel label is already **Job Summary**). Else `<p className="recommended-report-empty">No job summary on file.</p>`. |
   | `company_upshot` | If `companyNotes` nonempty, render as `.job-analysis-upshot-body` text. Else `<p className="recommended-report-empty">No company upshot on file.</p>`. |
   | `caveats` | From parsed upshot `caveats` where `text.trim()`; if any, `<ul className="job-analysis-upshot-list">` of those texts. Else empty-state **No noteworthy caveats on file.** |
   | `questions` | Same pattern from `candidate_questions` → **No questions to ask on file.** |
   | `raw_jd` | `String(job.job_data?.job_description ?? "").trim().replace(/\n{3,}/g, "\n\n")`; if nonempty, `<div className="entity-jd-content">…</div>`; else **No job description on file.** |

2. `parseAnalysisUpshot` returns `null` when missing/empty — treat as no upshot: job_summary / caveats / questions all show their empty states (do **not** crash; do **not** hide the section chrome).

3. Reuse existing CSS classes from the pre-redesign summary pane (`job-analysis-upshot-body`, `job-analysis-upshot-list`, `entity-jd-content`, `recommended-report-empty`). Only add App.css rules if a class is truly missing after AST-948 — do not invent a parallel Summary design.

4. Do **not** render Analysis or Artifacts bodies in this ticket. Do **not** restore `SideTabPanel` content.

⚠️ **Decision:** Empty copy is fixed English strings above (match tone of existing `recommended-report-empty` lines). No i18n, no config strings for empty copy.

---

## Stage 3: Content-aware initial expand for Summary sections

**Done when:** First paint of Summary matches parent defaults: Job Summary expanded; Company Upshot / Caveats / Questions expanded **only when** that section has content, else start collapsed; Raw JD always starts collapsed. User can still expand empty sections to read the empty state.

1. When building the `sections` array passed to Summary `ReportSectionList`, map each manifest row to `ReportSectionDef` but **override** `default_expanded` as follows (do not change `config.py` / manifest):

   - `job_summary` → `true` (always; empty state visible when expanded).
   - `company_upshot` → `true` iff `companyNotes` nonempty, else `false`.
   - `caveats` → `true` iff parsed upshot has ≥1 trimmed caveat text, else `false`.
   - `questions` → `true` iff ≥1 trimmed question text, else `false`.
   - `raw_jd` → `false` always.

2. Ensure `ReportSectionList`’s existing `setExpandedKeys` seed (AST-948) re-runs when these effective defaults change (company fetch completes, job load completes). If the AST-948 seed only keys off `section_id` list and static `default_expanded` from manifest, pass the **overridden** defs from this ticket so the seed sees the content-aware flags — do not fork a second expand hook.

3. Confirm `npx tsc -b --noEmit` in `src/ui/frontend` for files touched.

⚠️ **Decision:** Override expand defaults in the modal from live content rather than encoding emptiness in config — emptiness is data-dependent; config keeps the AST-948 chrome defaults as documentation/fallback for shell-only builds.

---

## Self-Assessment

**Scope:** Single-Component — Summary tab bodies inside `JobAnalysisReportModal` (plus optional CSS reuse); depends on AST-948 shell APIs but does not re-own them.

**Conf:** high — reuses `parseAnalysisUpshot`, existing upshot/JD CSS, and company GET that already lifts `prefilter_company_notes`; section ids are fixed by AST-948 plan.

**Risk:** Medium — wrong empty/expand wiring or a missing AST-948 merge would leave Summary blank or crash on partial upshot; company notes path must use the lifted API field, not invent a job_data key.

---

## Code rules check

- **§1.3 DRY:** One `renderSummarySection`; reuse `parseAnalysisUpshot` and existing empty/JD classes — no parallel upshot parser.
- **§1.4 / §2.1:** Section ids/labels stay manifest-driven (AST-948); this ticket only fills bodies + content-aware expand overrides.
- **§2.4 / §2.6:** N/A.
- **§3.3:** Frontend-only; company notes via existing UI API response.
- **§3.5:** No new page file required; optional small helpers stay in the modal or `lib/` only if extraction is needed for clarity — prefer keeping render switch in the modal unless it exceeds readable size.
- **Tests / bible:** Not touched by engineer (Betty).

---

## Review (build)

**Built:** `origin/sub/AST-858/AST-949-summary-tab-sections` @ `4881b863ef3cc20c3046e87e38ffdc9268fed191`

Stages 1–3: company `prefilter_company_notes` on existing company fetch; Summary `renderSummarySection` bodies + empty states for job_summary / company_upshot / caveats / questions / raw_jd; content-aware `default_expanded`. Tests deferred to Betty.
