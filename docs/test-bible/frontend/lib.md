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

**AST-950:** `buildPhaseSectionGradeConfidenceRow` + `gradesForHeader` for Analysis section headers / `AgentAnalysisHeader` payloads.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-950** | Grade+confidence header helper | `src/ui/frontend/src/lib/recommendedJobReport.tsx` | **`test_recommendedJobReport.test.tsx`** — **`recommendedJobReport — AST-950 grade+confidence header row`** |

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

### AST-1236 · AST-1174

**Parent:** [AST-1174 — Human-paced fan-out over the batch worklist](https://linear.app/astralcareermatch/issue/AST-1174/human-paced-fan-out-over-the-batch-worklist). **Publish:** `origin/sub/AST-1174/AST-1236-pacing-config`.

Extension pacing helpers under `src/ui/extension/src/lib/` (not SPA `frontend/src/lib/`): `fetchPacingConfig` / cache, shared `dwell()` (ordinary `setTimeout`, MV3 ceiling from config), `createTabBudget` slot transfer so `max_tabs` cannot be exceeded under interleaved acquire/release. Config + GET: **`docs/test-bible/utils/config.md`**, **`docs/test-bible/ui/api/api_surfer.md`**. §6c routed-page rule N/A (no `pages/` change).

| Area | Source | Component tests |
| --- | --- | --- |
| Cache + fetch injection | `src/ui/extension/src/lib/pacingConfig.ts` | **`test_surferPacingConfig.test.ts`** |
| Randomized dwell + MV3 reject | `src/ui/extension/src/lib/dwell.ts` | same |
| One-at-a-time slot transfer | `createTabBudget` in `pacingConfig.ts` | same |

**Broken / obsolete:** none — new modules.

**Integration:** none revised.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_surferPacingConfig.test.ts
```


### AST-1237 · AST-1173

**Parent:** [AST-1173 — Consent — install disclosure, affirmative opt-in, and off-switch](https://linear.app/astralcareermatch/issue/AST-1173/consent-install-disclosure-affirmative-opt-in-and-off-switch). **Publish:** `origin/sub/AST-1173/AST-1237-install-disclosure-and-affirmative-opt-in`.

Extension consent helpers under `src/ui/extension/src/lib/`: `needsDisclosure` / `fetchSurferConsent` / `optInSurferConsent` (injected fetch); `mountSurferDisclosure` plain-DOM panel (shadow root when available; affirmative + decline handlers; no network). Web page: **`docs/test-bible/frontend/pages.md`**. §6c N/A for these lib modules (routed page covered separately).

| Area | Source | Component tests |
| --- | --- | --- |
| needsDisclosure + injected GET/PUT | `surferConsent.ts` | **`test_surferConsent.test.ts`** |
| DOM mount / handlers / unmount | `surferDisclosureDom.ts` | same |

**Broken / obsolete:** none — new modules.

**Integration:** none.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_surferConsent.test.ts
```


### AST-1238 · AST-1173

**Parent:** [AST-1173 — Consent — install disclosure, affirmative opt-in, and off-switch](https://linear.app/astralcareermatch/issue/AST-1173/consent-install-disclosure-affirmative-opt-in-and-off-switch). **Publish:** `origin/sub/AST-1173/AST-1238-off-switch-and-pre-consent-no-op`.

Extension helpers: `mayCapture` / `fetchConsent` / `assertMayCapture` (`surferConsentGate.ts`); `optOutSurfer` (`surferOffSwitch.ts`). Wire notes: `docs/features/surfer/ast-1238-extension-consent-wiring.md` (AST-1170 / AST-1228). Web off-switch page: **`docs/test-bible/frontend/pages.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Gate + assertMayCapture | `surferConsentGate.ts` | **`test_surferConsentGate.test.ts`** |
| Opt-out PUT | `surferOffSwitch.ts` | same |

**Broken / obsolete:** none.

**Integration:** none (capture route not yet present).

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_surferConsentGate.test.ts
```
