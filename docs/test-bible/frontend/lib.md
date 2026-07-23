# Lib

**Test tree:** `tests/component/lib/`

### AST-481 · AST-478

**`JobAnalysisReportModal`** loads **`GET /api/jobs/:id`** and parses **`job_data.analysis_upshot`** via **`parseAnalysisUpshot`** (`analysisUpshot.ts`; mirrors **`TASK_CONFIG["analysis_upshot"]["response_schema"]`**). Upshot renders above the JD preview; empty/invalid payloads show **No analysis upshot on file.**

| Area | Source | Component tests |
| --- | --- | --- |
| Parser + title helper | `src/ui/frontend/src/lib/analysisUpshot.ts` | `tests/component/frontend/lib/test_analysisUpshot.test.ts` |
| Modal + API wiring | `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` |

Narrow (**`test-astral`** on **AST-481** tip): Vitest only — `./scripts/testing/run_component_tests.sh` forwards trailing paths to **pytest**, so **`.ts` / `.tsx`** Vitest specs are **`ERROR: file or directory not found`**. Run:

```bash
cd src/ui/frontend && npx vitest run --config vite.config.ts ../../../tests/component/frontend/lib/test_analysisUpshot.test.ts ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx
```

When **pytest** is green, full **`./scripts/testing/run_component_tests.sh`** reaches Vitest with the harness’s frontend pass.

---

### AST-581 · AST-605 · AST-599

**AST-599 (parent):** Recreate **AST-581** Preview Materials UX lost in git merges. Job **`/candidate/resume/<job_id>`** is resume-only (`include_cover=False` default); **`GET /candidate/cover/<job_id>`** serves cover HTML only. JAR (**`JobAnalysisReportModal`**) shows **Preview Materials** when **`CANDIDATE_REVIEW`** or artifact content exists; **`MaterialsPreviewModal`** tabbed iframes load server HTML. Component tests were authored for original **AST-581** — manifest-only this pass (no new test files).

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-605** | Builder split + cover route; **`materialsPreviewVisible`**; JAR preview button/modal wiring | `src/core/builder.py`, `src/ui/api/api_resume_html.py`, `src/ui/frontend/src/lib/recommendedJobReport.tsx`, `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`, `RecommendedJobReportHeader.tsx`, `MaterialsPreviewModal.tsx`, `src/ui/frontend/src/App.css` | `tests/component/core/test_builder.py::TestAst581ResumeCoverSplit`; `tests/component/ui/api/test_api_resume_html.py::TestAst581CoverRoute`; `tests/component/frontend/lib/test_recommendedJobReport.test.tsx` (**AST-581** describe); `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` — **JobAnalysisReportModal — AST-581 Preview Materials** describe |

**AST-605** narrowed run (JAR is a modal component — **§6c** routed-page rule N/A):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst581ResumeCoverSplit \
  tests/component/ui/api/test_api_resume_html.py::TestAst581CoverRoute
cd src/ui/frontend && npx tsc -b --noEmit
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_recommendedJobReport.test.tsx \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx
```

---

### AST-625 · AST-624

**AST-624 (parent):** Dedicated log-off screen when the SPA detects a prior Stytch session is gone (timeout) or Flask returns **401** while the user was authenticated — distinct copy per reason, **Refresh** clears tab-scoped marks and reloads for **Login** recovery. First-time visitors still see **`Login`**. Frontend-only; no Flask or Stytch Dashboard changes.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-625** | `sessionStorage` had-session + log-off reason; centralized **`api()`** 401 hook; **`RequireAuth`** routes **`LogOffScreen`** vs **`Login`** vs children; reason-specific copy + **Refresh** | `src/ui/frontend/src/lib/sessionAuthMark.ts`, `src/ui/frontend/src/lib/api.ts`, `src/ui/frontend/src/contexts/AuthContext.tsx`, `src/ui/frontend/src/components/RequireAuth.tsx`, `src/ui/frontend/src/pages/LogOffScreen.tsx` | `tests/component/frontend/lib/test_sessionAuthMark.test.ts`; `tests/component/frontend/lib/test_api.test.ts`; `tests/component/frontend/contexts/test_AuthContext.test.tsx`; `tests/component/frontend/components/test_RequireAuth.test.tsx`; `tests/component/frontend/components/test_LogOffScreen.test.tsx` |

**AST-625** narrowed run (Vitest — from `src/ui/frontend/`):

```bash
npm run test:component -- \
  ../tests/component/frontend/lib/test_sessionAuthMark.test.ts \
  ../tests/component/frontend/lib/test_api.test.ts \
  ../tests/component/frontend/contexts/test_AuthContext.test.tsx \
  ../tests/component/frontend/components/test_RequireAuth.test.tsx \
  ../tests/component/frontend/components/test_LogOffScreen.test.tsx
```

**Regression guard (unchanged AST-612/613):** After manifest green, spot-check **`test_Login.test.tsx`**, **`test_AdminRoute.test.tsx`**, **`test_NavigationShell.test.tsx`** — no auth-gate regressions.

---

### AST-830 · AST-829

**AST-829 (parent):** Production Google OAuth on Railway fails after redirect — Stytch **SessionsGet** succeeds but browser lands on Stytch Login Error. **AST-830** hardens SPA **`/authenticate`** OAuth/magic-link handoff: init gate, single-flight **`authenticateByUrl`**, in-app error + **Try again** (no hosted Stytch error page). **`env.example`** documents live-project checklist; Flask JWT validation is sibling **AST-831**.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-830** | **`completeAuthenticateFromUrl`** outcomes; **`Authenticate`** page loading / redirect / error UI | `src/ui/frontend/src/lib/stytchAuthenticateHandoff.ts`, `src/ui/frontend/src/pages/Authenticate.tsx` | `tests/component/frontend/lib/test_stytchAuthenticateHandoff.test.ts`; `tests/component/frontend/pages/test_Authenticate.test.tsx` |

**AST-830** narrowed run (Vitest — from `src/ui/frontend/`; **§6c** routed page):

```bash
npx tsc -b --noEmit
npm run test:component -- \
  ../../../tests/component/frontend/lib/test_stytchAuthenticateHandoff.test.ts \
  ../../../tests/component/frontend/pages/test_Authenticate.test.tsx
```

**Regression guard:** **`test_stytchRedirect.test.ts`**, **`test_Login.test.tsx`** — redirect URL wiring unchanged.

---

### AST-948 · AST-858

**AST-858 (parent):** Recommended Job Report redesign. **AST-948** adds **`printResumeVisible`** / **`printCoverVisible`** (wrap **`artifactHasContent`**) for sticky-header Print buttons; JAR no longer wires **`materialsPreviewVisible`** / Preview Materials (helper retained for now).

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-948** | Print visibility helpers; fixture `report_top_tabs` / `report_summary_sections` | `src/ui/frontend/src/lib/recommendedJobReport.tsx`, `tests/component/frontend/fixtures/stateUiManifestFixture.ts` | **`test_recommendedJobReport.test.tsx`** — **`recommendedJobReport — AST-948 print helpers`** (+ retained AST-581 `materialsPreviewVisible` unit cases) |

**AST-948** narrowed lib run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_recommendedJobReport.test.tsx
```
