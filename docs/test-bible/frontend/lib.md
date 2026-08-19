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

---

### AST-950 · AST-858

**AST-950 / AST-1327 / AST-1328:** `buildPhaseSectionGradeConfidenceRow(gradesRaw, job, gradesField)` builds Analysis header columns via `buildJobListRubricColumnsForGroup` / job-carried `*_rubric` (grades-only when snapshot absent) — **not** live `jobdesc_rubric` / `candidateArtifacts`. `gradesForHeader` still normalizes body payloads for `AgentAnalysisHeader`.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-950** | Grade+confidence header helper (job-carried arity) | `src/ui/frontend/src/lib/recommendedJobReport.tsx` | **`test_recommendedJobReport.test.tsx`** — **`recommendedJobReport — AST-950 grade+confidence header row`** |
| **AST-1328** | Meteorite mismatch: header cell count follows `jd_rubric` ∩ graded vectors when live gazer artifact underlaps | same | same describe — **`AST-1328: header shows every job-carried vector when live jobdesc_rubric underlaps`** (bug-repro) |

---

### AST-951 · AST-858

**AST-951:** `isArtifactsBuildInProgress`, `artifactsTabPrimaryActions` (compound hop fallback), `anyReportArtifactContent`.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-951** | Artifacts action / content helpers | `src/ui/frontend/src/lib/recommendedJobReport.tsx` | **`test_recommendedJobReport.test.tsx`** — **`recommendedJobReport — AST-951 Artifacts helpers`** |

---

### AST-1086 · AST-1078

**Parent:** [AST-1078 — Small bug: Headers for Job Lists](https://linear.app/astralcareermatch/issue/AST-1078/small-bug-headers-for-job-lists). **Publish:** `origin/sub/AST-1078/AST-1086-compact-vector-codes-grade-dot-tooltips`.

Compact grades-only `headerCode` (`Technical (TE)` → `TE`), clean label tooltips, and grade-dot confidence parenthetical via `formatGradeDotTooltip` / `CONFIDENCE_DESCRIPTIONS` mirror. Page coverage: **`docs/test-bible/frontend/pages.md`** (**AST-1086**).

| Area | Source | Component tests |
| --- | --- | --- |
| Grades-only parse + grade-dot tooltip | `lib/rubricDisplay.ts` | **`test_rubricDisplay.test.ts`** — **`AST-1086 compact headers and grade-dot confidence tooltips`** (+ grades-only expectation in **`AST-1064 job-carried list helpers`**) |

**Broken / obsolete:** grades-only fallback expected `headerCode === "Technical (TE)"` — revised to `"TE"` / tooltip `"Technical (5)"`.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_rubricDisplay.test.ts
```

### AST-1100 · AST-1091

**Parent:** [AST-1091](https://linear.app/astralcareermatch/issue/AST-1091/job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved). **Publish:** `origin/sub/AST-1091/AST-1100-resolve-artifact-agent-data-id`.

`artifactHasContent` treats non-empty pin strings as content. `printResumeVisible` / `materialsPreviewVisible` gate on `job_resume` (+ legacy `resume_content`). Fixture `report_artifact_tabs` keys remapped to pin slots.

| Area | Source | Component tests |
| --- | --- | --- |
| Visibility + fixture keys | `recommendedJobReport.tsx`, `stateUiManifestFixture.ts` | **`test_recommendedJobReport.test.tsx`** — **`recommendedJobReport — AST-1100 pin-slot visibility`** (+ revised AST-581 / AST-951 key asserts) |

**Broken / obsolete:** fixture `artifact_key` `resume_content` / `application_responses` → `job_resume` / `proposed_answers`; `anyReportArtifactContent` assert updated to `job_resume`.

**Integration:** none.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_recommendedJobReport.test.tsx
```

### AST-1215 · AST-1185

**Parent:** [AST-1185 — UI groupings/sequences + alphabetical task key/alias dropdowns](https://linear.app/astralcareermatch/issue/AST-1185/ui-groupingssequences-alphabetical-task-keyalias-dropdowns-data-driven). **Publish:** `origin/sub/AST-1185/AST-1215-admin-ui-grouping-honesty-alphabetical-dropdowns`.

`compareTaskKeys` / `sortedTaskKeys` — plain lexicographic task_key order (Python `sorted` / SQLite `ORDER BY task_key`; not `localeCompare`). Page wiring: **`docs/test-bible/frontend/pages.md`** (**AST-1215**).

| Area | Source | Component tests |
| --- | --- | --- |
| Lexicographic helper | `src/ui/frontend/src/lib/taskKeySort.ts` | **`test_taskKeySort.test.ts`** |

**Broken / obsolete:** none — new helper.

**Integration:** none.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_taskKeySort.test.ts
```

### AST-1311 · AST-1307

**Parent:** [AST-1307 — Please set the page title to Astral - &lt;full_name&gt;](https://linear.app/astralcareermatch/issue/AST-1307/please-set-the-page-title-to-astral-full-name). **Publish:** `origin/sub/AST-1307/AST-1311-browser-tab-title-follows-selected-candidate`.

`browserTabTitle` formats `Astral` or `Astral - <Full Name>` from the list payload `full` column only (trim; no first+last join, no picker label). `CandidateProvider` applies `document.title` on `[selectedId, candidates]` and resets to `Astral` on unmount. §6c N/A (no `pages/` edit; no filter UX).

| Area | Source | Component tests |
| --- | --- | --- |
| Formatter | `src/ui/frontend/src/lib/documentTitle.ts` | **`test_documentTitle.test.ts`** |
| Apply + unmount reset | `src/ui/frontend/src/contexts/CandidateContext.tsx` | **`test_CandidateContext.test.tsx`** — **`CandidateProvider — AST-1311 browser tab title`** |

**Broken / obsolete:** none — existing CandidateContext selection tests stay valid (`full` absent → title `Astral`). `test_Authenticate` only passes `document.title` into `replaceState`, does not assert chrome text.

**Integration:** none — SPA `document.title`; no `tests/integration/` scenario asserts tab chrome.

```bash
cd src/ui/frontend && npx tsc -b --noEmit
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_documentTitle.test.ts \
  ../../../tests/component/frontend/contexts/test_CandidateContext.test.tsx
```

### Extension Surfer libs (moved)

**AST-1254** migrated `test_surfer*.test.ts` from `tests/component/frontend/lib/` → `tests/component/extension/lib/` (WXT Vitest project). Coverage maps live under **`docs/test-bible/extension/lib.md`** (AST-1236–AST-1239) and **`docs/test-bible/extension/scaffold.md`** (AST-1254). Do not re-add Surfer extension-lib manifests here.

### AST-1348 · AST-1346

**Parent:** [AST-1346](https://linear.app/astralcareermatch/issue/AST-1346/add-rubric-score-to-analysis-header). **Publish:** `origin/sub/AST-1346/AST-1348-analysis-header-score-title-chrome`.

`jobScoreBreakdownForGradesField` + `formatPhaseSectionScoreTitle` (round for display; template from manifest). Modal wiring: **`docs/test-bible/frontend/components.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Breakdown lookup + title format | `recommendedJobReport.tsx` | **`test_recommendedJobReport.test.tsx`** — **`recommendedJobReport — AST-1348 phase score header helpers`** |

**Broken / obsolete:** none.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_recommendedJobReport.test.tsx \
  -t "AST-1348"
```

### AST-1374 · AST-1372

**Parent:** [AST-1372 — Extend Stytch sessions](https://linear.app/astralcareermatch/issue/AST-1372). **Publish:** `origin/sub/AST-1372/AST-1374-spa-authenticate-activity-extend`.

SPA consumes AST-1373 `GET /api/auth_session_policy`: authenticate handoff uses configured `session_duration_minutes` (hardcoded `60` removed); `AuthProvider` starts `startSessionExtendLoop` while a Stytch session exists. Does **not** invent policy API (**AST-1373**); does **not** redesign log-off (**AST-624/625**).

| Area | Source | Component tests |
| --- | --- | --- |
| Policy fetch | `authSessionPolicy.ts` | **`test_authSessionPolicy.test.ts`** |
| Extend interval helper | `sessionExtend.ts` | **`test_sessionExtend.test.ts`** |
| Handoff uses policy duration | `stytchAuthenticateHandoff.ts` | revised **`test_stytchAuthenticateHandoff.test.ts`** |
| `/authenticate` page | `Authenticate.tsx` | revised **`test_Authenticate.test.tsx`** (§6c) |
| AuthProvider extend wiring | `AuthContext.tsx` | revised **`test_AuthContext.test.tsx`** (+ `stytchMock` `getSync` / `authenticate`). **AST-1408** keys the loop on `sessionPresent` — see [`contexts.md`](contexts.md). |

**Broken / obsolete this pass:** handoff + Authenticate expected `session_duration_minutes: 60` / unmocked policy fetch — revised to stub `GET /api/auth_session_policy` and assert configured `20`.

**Integration:** no existing scenario asserts SPA session duration or extend cadence — no revision.

## QA test manifest

1. Policy fetch: `tests/component/frontend/lib/test_authSessionPolicy.test.ts`
2. Extend loop helper: `tests/component/frontend/lib/test_sessionExtend.test.ts`
3. Handoff (configured duration + no fallback): `tests/component/frontend/lib/test_stytchAuthenticateHandoff.test.ts`
4. Authenticate page §6c: `tests/component/frontend/pages/test_Authenticate.test.tsx`
5. AuthContext extend start: `tests/component/frontend/contexts/test_AuthContext.test.tsx`

**AST-1374** narrowed run (Vitest — from `src/ui/frontend/`):

```bash
npm run test:component -- \
  ../../../tests/component/frontend/lib/test_authSessionPolicy.test.ts \
  ../../../tests/component/frontend/lib/test_sessionExtend.test.ts \
  ../../../tests/component/frontend/lib/test_stytchAuthenticateHandoff.test.ts \
  ../../../tests/component/frontend/pages/test_Authenticate.test.tsx \
  ../../../tests/component/frontend/contexts/test_AuthContext.test.tsx
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-1441 · AST-1438

**Parent:** [AST-1438 — Disable authentication on localhost](https://linear.app/astralcareermatch/issue/AST-1438/disable-authentication-on-localhost). **Publish:** `origin/sub/AST-1438/AST-1441-local-spa-skip-login-and-session-refresh`.

SPA consumes AST-1440 `GET /api/auth_passthrough`: fail-closed raw `fetch`; when `true`, AuthContext loads `/api/me` with no Stytch session and skips extend; RequireAuth renders children (no Login / Log-off); Authenticate navigates `/` without `authenticateByUrl`. Flask signal = **AST-1440**. Does **not** unwrap `StytchProvider`.

| Area | Source | Component tests |
| --- | --- | --- |
| Public-signal fetch | `authPassthrough.ts` | **`test_authPassthrough.test.ts`** |
| `/api/me` without session; skip extend | `AuthContext.tsx` | **`test_AuthContext.test.tsx`** — **`AST-1441:*`** |
| Skip Login / Log-off | `RequireAuth.tsx` | **`test_RequireAuth.test.tsx`** — **`AST-1441:*`** |
| `/authenticate` page (§6c) | `Authenticate.tsx` | **`test_Authenticate.test.tsx`** — **`AST-1441:*`** |

**Broken / obsolete:** existing AuthContext / RequireAuth / Authenticate suites assumed no `/api/auth_passthrough` wait — revised to `stubAuthPublicFetches(false)` (shared in `test-utils.tsx`). RequireAuth AST-1408 keep-mounted now `waitFor` (passthrough must settle). AdminRoute `useAuth` mocks include `localAuthPassthrough: false`.

**Integration:** no existing scenario asserts SPA Login / extend — no revision. Do not invent new integration coverage.

## QA test manifest

1. Fail-closed fetch helper: `tests/component/frontend/lib/test_authPassthrough.test.ts`
2. AuthContext passthrough `/api/me` + skip extend: `tests/component/frontend/contexts/test_AuthContext.test.tsx`
3. RequireAuth skip Login/Log-off: `tests/component/frontend/components/test_RequireAuth.test.tsx`
4. Authenticate page §6c skip handoff: `tests/component/frontend/pages/test_Authenticate.test.tsx`

**AST-1441** narrowed run (Vitest — from `src/ui/frontend/`):

```bash
npm run test:component -- \
  ../../../tests/component/frontend/lib/test_authPassthrough.test.ts \
  ../../../tests/component/frontend/contexts/test_AuthContext.test.tsx \
  ../../../tests/component/frontend/components/test_RequireAuth.test.tsx \
  ../../../tests/component/frontend/pages/test_Authenticate.test.tsx
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-1421 · AST-1419

**Parent:** [AST-1419 — Create a Copy button on the Job Modal](https://linear.app/astralcareermatch/issue/AST-1419/create-a-copy-button-on-the-job-modal). **Publish:** `origin/sub/AST-1419/AST-1421-job-modal-copy-control`.

`copyJobSnapshotToClipboard` GETs `/api/jobs/<id>/copy` (encoded, no `?debug=`), `JSON.stringify(body, null, 2)`, `navigator.clipboard.writeText`. Returns `true` only on write success; non-OK / parse / clipboard reject return `false` with no throw. Chrome: **`docs/test-bible/frontend/components.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Clipboard helper | `src/ui/frontend/src/lib/copyJobSnapshot.ts` | **`test_copyJobSnapshot.test.ts`** |

**Broken / obsolete:** none.

**Integration:** none.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_copyJobSnapshot.test.ts
```
