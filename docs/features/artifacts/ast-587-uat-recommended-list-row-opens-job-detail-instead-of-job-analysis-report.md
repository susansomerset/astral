<!-- linear-archive: AST-587 archived 2026-06-23 -->

## Linear archive (AST-587)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-587/uat-recommended-list-row-opens-job-detail-instead-of-job-analysis  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Bug (AST-300 UAT)

Susan: land-ftr regressed Recommended list — row click opens JobDetailModal instead of JobAnalysisReportModal (AST-565).

## Expected

Row click on Jobs Recommended opens JobAnalysisReportModal (setReportId).

## Actual

Row click opens JobDetailModal (setViewingId) — regression from integration fix bee17675.

## Fix

Restore onClick setReportId; remove JobDetailModal from JobsRecommended if unused.

## Boundaries

Do not change AST-581 Preview Materials or AST-553 draft tabs.

## Acceptance

1. Recommended row click opens JobAnalysisReportModal.
2. Vitest asserts report modal on row click.

### Comments

#### chuckles — 2026-06-16T19:27:52.894Z
[check-linear] Done — already on origin/dev (@susan)

#### betty — 2026-06-12T18:43:30.046Z
Betty land preflight: CLEAN — AST-587 @ 87614941 already on origin/dev @ 9cf9e2e4; no ftr ref (prior land)

#### susan — 2026-06-12T18:42:14.570Z
I think this one got skipped, @chuckles.  Please wrap it up?

#### katherine — 2026-06-06T01:42:00.733Z
**FIX-UAT rollup unblock:** `origin/ftr/AST-300-build-resume-artifact` @ **`87614941`**

- Merged `origin/sub/…/AST-587-…` @ `90d177fd`; conflicts resolved sub side for `JobsRecommended.tsx`, `test_JobsRecommended.test.tsx`, `ASTRAL_TEST_BIBLE.md`
- Follow-up **`87614941`**: `CandidateJobRowActions`, `analysisUpshot`, `stateUiManifestFixture`, `page-mocks` (AST-565 deps for Skip-without-Jr + report modal Vitest)
- Vitest: **8/8** `test_JobsRecommended.test.tsx` on resolved ftr tree

#### radia — 2026-06-06T01:13:56.935Z
**Review** (`origin/dev...origin/sub/AST-300/AST-587-uat-recommended-list-row-opens-job-detail-instead-of-job-analysis-report`) · plan: [ast-587 doc @ d2fe5ec9](https://github.com/susansomerset/astral/blob/sub/AST-300/AST-587-uat-recommended-list-row-opens-job-detail-instead-of-job-analysis-report/docs/features/artifacts/ast-587-uat-recommended-list-row-opens-job-detail-instead-of-job-analysis-report.md)

### Solid
- Vitest **`opens the report modal from a row click`** — **`Summary`**, **Job Summary** on **`.side-tab-list`**, negative **State History** / **Skip This Job** (would catch ftr regression).
- Test bible §6c + AST-587 row match; AST-581 / AST-553 untouched.
- **`JobsRecommended.tsx`** on **`origin/dev`** / publish ref: AST-565 wiring (`setReportId`, `showViewAnalysis={false}`, no **`JobDetailModal`**).

### fix-now
- **`JobsRecommended.tsx`** — **no product diff** on publish ref vs **`origin/dev`**. Susan's UAT bug is on **`origin/ftr/AST-300-build-resume-artifact`** (`setViewingId` + **`JobDetailModal`**). Three-way merge into ftr: base = correct wiring, ftr = regression, sub = file unchanged → git keeps **ftr**'s handler. **`rollup-child` of this sub tip does not satisfy AC1.** Resolve: land plan Stage 1 steps 1–5 on **`dev-kath`**, publish, re-run **`test_JobsRecommended.test.tsx`** against ftr merge.

### discuss
- Plan **Scope** lists page change; ship is test + bible only — OK if intentional; still need explicit ftr product fix (don't assume rollup).

### advisory
- Test uses **`querySelector(".side-tab-list")!`**; plan suggested **`getByText("Job Summary")`** if rail DOM shifts.

**§3.3 / §3.5:** UI-only test delta — no layer violations. **§5f:** N/A.

#### betty — 2026-06-05T23:27:28.734Z
## QA test manifest

**Publish ref:** `origin/sub/AST-300/AST-587-uat-recommended-list-row-opens-job-detail-instead-of-job-analysis-report` @ `8659e192`

**`docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref:** `386b662f0a437558a1057823d84aea7098ce5ac3`

### 1. Existing coverage (bible-backed — §6c routed page + §7.13zs AST-587)

Run from repo root after `git fetch origin && git merge origin/sub/AST-300/AST-587-uat-recommended-list-row-opens-job-detail-instead-of-job-analysis-report`:

```bash
cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx
```

**Required cases:**

1. **`opens the report modal from a row click`** — row click shows report upshot (**Summary**), **Job Summary** tab in side rail; **`State History`** and **Skip This Job** (detail modal markers) must be absent.
2. **`shows Skip without Jr on Recommended rows (AST-565)`** — Skip present; **View Job Analysis** absent.
3. **Regression (§7.13zm):** **`groups jobs into state sections with JD/DO/GET/LIKE phase scores`**, **`sorts by company within a section`**, skip-action tests — full file green.

### 2. Broken / obsolete tests

None — engineer strengthened `opens the report modal from a row click` on publish ref (`92eecc67`).

### 3. Gaps

None this pass.

— Betty

#### chuckles — 2026-06-05T23:22:23.054Z
## Validate-plan — APPROVED

Plan restores AST-565 row-click → `JobAnalysisReportModal` with minimal `JobsRecommended.tsx` diff + Vitest regression. Scope matches bug description; no config/API churn; boundaries respected.

**Verdict:** APPROVED → Plan Approved.

— Chuckles

#### katherine — 2026-06-05T23:22:00.104Z
Plan: [`docs/features/artifacts/ast-587-uat-recommended-list-row-opens-job-detail-instead-of-job-analysis-report.md`](https://github.com/susansomerset/astral/blob/sub/AST-300/AST-587-uat-recommended-list-row-opens-job-detail-instead-of-job-analysis-report/docs/features/artifacts/ast-587-uat-recommended-list-row-opens-job-detail-instead-of-job-analysis-report.md) on **`origin/sub/AST-300/AST-587-uat-recommended-list-row-opens-job-detail-instead-of-job-analysis-report`** @ `ad46347b`.

**Scope:** `Single-Component` — restores **`JobsRecommended`** row click → **`JobAnalysisReportModal`** only (reverts **`ftr/AST-300`** regression that wired **`JobDetailModal`** / `setViewingId`).

**Conf:** `high` — fix matches **AST-565** and **`origin/dev`**; diff is explicit in plan.

**Risk:** `low` — isolated list click wiring; no API or chain changes.

---

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
