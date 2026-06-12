# UAT: Recommended list row opens Job Detail instead of Job Analysis Report

**Linear:** https://linear.app/astralcareermatch/issue/AST-587/uat-recommended-list-row-opens-job-detail-instead-of-job-analysis-report  
**Parent:** https://linear.app/astralcareermatch/issue/AST-300/build-resume-artifact  
**Publish ref:** `origin/sub/AST-300/AST-587-uat-recommended-list-row-opens-job-detail-instead-of-job-analysis-report`

**Summary:** Susan UAT on **AST-300** found that clicking a row on the **Jobs Recommended** list opens **`JobDetailModal`** (In Review / Skipped rail pattern) instead of **`JobAnalysisReportModal`** (**AST-565**). The regression lives on **`origin/ftr/AST-300-build-resume-artifact`**: row `onClick` calls `setViewingId` and mounts both modals. **AST-565** requires row click → `setReportId` only, with `showViewAnalysis={false}` on row actions (no **Jr** button). This ticket restores that wiring and locks it with a Vitest regression test.

---

## Prerequisite gate (before Stage 1)

1. On **`dev-kath`**: `git fetch origin && git merge origin/dev` — merge-clean gate (`origin/dev` ancestor of HEAD, `BEHIND=0`).
2. Confirm **`origin/sub/AST-300/AST-587-uat-recommended-list-row-opens-job-detail-instead-of-job-analysis-report`** exists (`git ls-remote origin refs/heads/sub/AST-300/AST-587-uat-recommended-list-row-opens-job-detail-instead-of-job-analysis-report`); `git merge origin/sub/AST-300/AST-587-uat-recommended-list-row-opens-job-detail-instead-of-job-analysis-report` onto **`dev-kath`** (empty tip OK).
3. Merge parent integration line when present: `git merge origin/ftr/AST-300-build-resume-artifact` — resolve conflicts on **`dev-kath`** only; **do not** check out **`ftr/*`** locally.
4. Read **`docs/features/interface/ast-565-recommended-job-report-modal-tabs-header-list-entry-recommended-job-modal.md`** § JobsRecommended row-entry steps for intended behavior.
5. If **`JobsRecommended.tsx`** on **`dev-kath`** after merges already matches Stage 1 target **and** Stage 2 test already passes, still run Stage 2 assertion check; skip redundant product edits only when file content is byte-identical to instructions below.

**Regression reference (do not ship):** On **`origin/ftr/AST-300-build-resume-artifact`**, `JobsRecommended.tsx` imports **`JobDetailModal`**, keeps `viewingId` state, row `onClick={() => setViewingId(...)}`, passes `onViewAnalysis={() => setReportId(...)}` without `showViewAnalysis={false}`, and renders `<JobDetailModal jobId={viewingId} … />`.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/JobsRecommended.tsx` | Row click → `setReportId`; remove `JobDetailModal` import/state/render; `showViewAnalysis={false}` on actions | ui |
| `tests/component/frontend/pages/test_JobsRecommended.test.tsx` | Strengthen row-click test: report modal markers present, detail modal markers absent | tests |

**Out of scope:** `JobAnalysisReportModal.tsx`, `JobDetailModal.tsx`, `CandidateJobRowActions.tsx` (already supports `showViewAnalysis`), **AST-581** Preview Materials, **AST-553** draft tabs, `config.py`, API routes, `docs/ASTRAL_TEST_BIBLE.md` (Betty after **Code Complete**).

---

## Stage 1: Restore AST-565 Recommended list row → report modal

**Done when:** `JobsRecommended.tsx` has no `JobDetailModal` import or mount; table row click sets `reportId`; `JobAnalysisReportModal` receives `jobId={reportId}`; `CandidateJobRowActions` uses `showViewAnalysis={false}` and no `onViewAnalysis` prop; `npm run test -- tests/component/frontend/pages/test_JobsRecommended.test.tsx` passes including the strengthened row-click test.

1. In **`src/ui/frontend/src/pages/JobsRecommended.tsx`**, remove the import line:
   ```typescript
   import JobDetailModal from "../components/JobDetailModal"
   ```
   Keep `import JobAnalysisReportModal from "../components/JobAnalysisReportModal"`.

2. In the component body, remove:
   ```typescript
   const [viewingId, setViewingId] = useState<string | null>(null)
   ```
   Keep `const [reportId, setReportId] = useState<string | null>(null)`.

3. In the `<tbody>` row map, change the `<tr>` opener from:
   ```tsx
   <tr key={job.astral_job_id} className="clickable" onClick={() => setViewingId(job.astral_job_id)}>
   ```
   to:
   ```tsx
   <tr key={job.astral_job_id} className="clickable" onClick={() => setReportId(job.astral_job_id)}>
   ```

4. On **`CandidateJobRowActions`** inside that row, set props to:
   ```tsx
   <CandidateJobRowActions
     state={job.state}
     showViewAnalysis={false}
     onSkip={() => actions.skipJob(job.astral_job_id)}
     onAction={a => actions.requestAction(job.astral_job_id, a)}
   />
   ```
   Remove **`onViewAnalysis`** entirely (do not pass `onViewAnalysis={() => setReportId(...)}`).

5. Remove the **`JobDetailModal`** JSX block:
   ```tsx
   <JobDetailModal jobId={viewingId} onClose={() => { setViewingId(null); load() }} />
   ```
   Keep the existing **`JobAnalysisReportModal`** block unchanged:
   ```tsx
   <JobAnalysisReportModal
     jobId={reportId}
     onClose={() => setReportId(null)}
     onRefresh={load}
   />
   ```

6. In **`tests/component/frontend/pages/test_JobsRecommended.test.tsx`**, replace the test **`opens the report modal from a row click`** body with assertions that distinguish report vs detail modal:
   - Keep existing API mock: list `sectionedJobs[0]`; `GET /api/jobs/j-rec` returns `job_data.analysis_upshot` with `whole_jd_upshot: "Summary"` (and minimal `take_*` strings as today).
   - After `userEvent.click(screen.getByText("Rec Role"))`, `await waitFor`:
     - `expect(screen.getByText("Summary")).toBeInTheDocument()` (report upshot body).
     - `expect(screen.getByText("Job Summary")).toBeInTheDocument()` (AST-565 report tab label — not present in **`JobDetailModal`**).
   - Add negative assertions (detail modal must not open):
     - `expect(screen.queryByText("State History")).not.toBeInTheDocument()`
     - `expect(screen.queryByRole("button", { name: "Skip This Job" })).not.toBeInTheDocument()`
   - Do not change other tests in this file.

7. From repo root, run:
   ```bash
   npm run test -- tests/component/frontend/pages/test_JobsRecommended.test.tsx
   ```
   All tests in that file must pass before stage completion.

⚠️ **Decision:** Row click opens **only** **`JobAnalysisReportModal`** — matching **AST-565** and **`origin/dev`**. **`JobDetailModal`** remains on **In Review** / **Skipped** lists; Recommended list does not offer a second path to the report via **Jr**.

---

## Self-Assessment

**Scope:** `Single-Component` — One page component (`JobsRecommended.tsx`) plus its page-level Vitest file; no backend or shared modal refactors.

**Conf:** `high` — Regression is documented on **`ftr/AST-300`**; correct target is already on **`origin/dev`** and **AST-565** plan; fix is a straight revert of row/modal wiring.

**Risk:** `low` — Isolated list click handler; wrong modal does not affect dispatch, persistence, or other job list pages.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses existing modals and `CandidateJobRowActions`; no duplicate modal logic. |
| §2.1 config | No new config; uses existing manifest-driven list sections. |
| §2.4 batch | N/A — UI-only. |
| §2.6 state machine | N/A — no state transitions. |
| §3.3 imports | Imports stay within `src/ui/frontend`; removes unused `JobDetailModal` import. |
| §3.5 naming | No new files; page stays `JobsRecommended.tsx` in `pages/`. |

No conflicts flagged.

---

## Review

**Built:** `dev-kath` → Joan `store-code-commit` → `origin/sub/AST-300/AST-587-uat-recommended-list-row-opens-job-detail-instead-of-job-analysis-report` — Vitest regression only vs **`origin/dev`**; **`JobsRecommended.tsx`** byte-identical to AST-565 on dev line.

**Diff reviewed:** `origin/dev...origin/sub/AST-300/AST-587-uat-recommended-list-row-opens-job-detail-instead-of-job-analysis-report` — plan doc, **`ASTRAL_TEST_BIBLE.md`**, **`test_JobsRecommended.test.tsx`**; **no** **`JobsRecommended.tsx`** delta vs **`origin/dev`**. **`origin/ftr/AST-300-build-resume-artifact`** still regressed (`setViewingId`, **`JobDetailModal`**).

### What's solid

- Vitest **`opens the report modal from a row click`** asserts report markers (**`Summary`**, **Job Summary** on **`.side-tab-list`**) and rejects detail-modal markers (**State History**, **Skip This Job**).
- Test bible §6c + AST-587 manifest row align; boundaries respected (no AST-581 / AST-553).
- **`origin/dev`** / publish-ref **`JobsRecommended.tsx`**: row → **`setReportId`**, **`showViewAnalysis={false}`**, no **`JobDetailModal`**.

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **fix-now** | `JobsRecommended.tsx` (missing product commit) | Sub tip does not change **`JobsRecommended.tsx`** vs **`origin/dev`**. UAT bug is on **`origin/ftr/AST-300`**. Three-way merge (base = AST-565 wiring, ftr = regression, sub = file unchanged): git keeps **ftr**'s version — **`rollup-child` alone does not fix AC1**. Resolve must land Stage 1 product edits and publish. |
| **discuss** | Plan Scope vs diff | Scope lists page component change; diff is test + bible only. Documented skip is OK; do not assume rollup replaces explicit ftr fix. |
| **advisory** | `test_JobsRecommended.test.tsx` | **`querySelector(".side-tab-list")!`** — consider **`screen.getByText("Job Summary")`** per plan if rail DOM shifts. |

### Recommended actions (resolve-astral)

| Action | Detail |
|--------|--------|
| Land Stage 1 on **`dev-kath`** | Plan steps 1–5 on **`JobsRecommended.tsx`**, Vitest file green, **`store-code-commit`**. |
| Re-verify on ftr merge | Run **`test_JobsRecommended.test.tsx`** with **`dev-kath`** merged against **`origin/ftr/AST-300`**. |

**Radia:** **`Review Posted`** 2026-06-06 · commit on publish ref via Joan.

---

## Resolution

**2026-06-06 (Katherine, resolve-astral):** Addressed Radia **fix-now** — explicit **`JobsRecommended.tsx`** product commit on publish ref so **`rollup-child`** does not silently keep **`origin/ftr/AST-300`** regression (sub tip matched merge-base **`699c5d04`**; three-way merge preferred ftr’s **`setViewingId`** / **`JobDetailModal`** wiring).

**Product:** Restored AST-565 row entry on **`JobsRecommended.tsx`**: row click → **`openJobReport`** → **`setReportId`**; **`showViewAnalysis={false}`** on **`CandidateJobRowActions`**; no **`JobDetailModal`** import/state/mount.

**Tests:** Betty manifest **`test_JobsRecommended.test.tsx`** re-run green after publish.

**vs review:** Resolves missing product delta on publish ref; Vitest regression from build pass unchanged.
