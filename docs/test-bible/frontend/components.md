# Components

**Test tree:** `tests/component/components/`

Local-deploy RequireAuth skip Login / Log-off: **`docs/test-bible/frontend/lib.md`** § AST-1441.

### AST-427 · AST-426

**`CollapsiblePanel`** shared by **`AdminTaskPrompts`** (Manage Tasks list + edit modal) and **`ArtifactEditor`** (criteria). Zero expanded sections: list phases and edit modal (`editOpenPanel === null` on collapse, same pattern as criteria `expandedTabId === ""`).

| Area | Source | Component tests |
| --- | --- | --- |
| Collapsible primitive | `src/ui/frontend/src/components/CollapsiblePanel.tsx` | `tests/component/frontend/components/test_CollapsiblePanel.test.tsx` |
| Manage Tasks | `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx` |
| Criteria regression | `src/ui/frontend/src/components/ArtifactEditor.tsx` | `tests/component/frontend/components/test_ArtifactEditor.test.tsx` (unchanged gate) |

No-snapshot Cancel without `window.location.reload` is **AST-1410** — primary block in [`pages.md`](pages.md).

---

### AST-893 · AST-886

**`SectionExpandChrome`** — **Expand all** / **Collapse all** row for Expand All pages. Group coordination lives in **`useSectionExpandPolicy`** (parents own Expand One vs Expand All); `CollapsiblePanel` remains the per-panel controlled API.

| Area | Source | Component tests |
| --- | --- | --- |
| Bulk chrome | `src/ui/frontend/src/components/SectionExpandChrome.tsx` | `tests/component/frontend/components/test_SectionExpandChrome.test.tsx` |
| Policy hook | `src/ui/frontend/src/hooks/useSectionExpandPolicy.ts` | `docs/test-bible/frontend/hooks.md` (**AST-893**) |
| Routed pages | Manage Tasks / In Review / Skipped / Scheduled Actions | `docs/test-bible/frontend/pages.md` (**AST-893**) |

**AST-893** narrowed Vitest (chrome):

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_SectionExpandChrome.test.tsx
```

---

### AST-359

Per-vector **`importance`** (1–10), **`ASTRAL_CONFIG["consult_importance"]`** multipliers (consumed later by **AST-358**), **`normalize_rubric_artifacts_on_save`**, and rubric UI labels / editor behavior. Run the full component suite (**Appendix A**); for targeted reruns, use:

| Area | Source (high level) | Component tests |
| --- | --- | --- |
| Multiplier table + accessor | `src/utils/config.py` (`consult_importance`, `importance_multiplier`) | `tests/component/utils/test_config.py` (`TestImportanceMultiplier`, `TestImportanceMultiplierEdges`) |
| Artifact normalization | `src/core/candidate.py` | `tests/component/core/test_candidate.py` (`TestNormalizeRubricArtifactsOnSaveExtended`, `TestNormalizeImportanceValue`) |
| Display helpers | `src/ui/frontend/src/lib/rubricDisplay.ts` | `tests/component/frontend/lib/test_rubricDisplay.test.ts` |
| Editor / rail | `ArtifactEditor.tsx`, `SideTabPanel.tsx` | `tests/component/frontend/components/test_ArtifactEditor.test.tsx`, `tests/component/frontend/components/test_SideTabPanel.test.tsx`, `tests/component/frontend/components/test_LabeledTextArea.test.tsx` |
| Analysis / job surfaces | `AgentAnalysisHeader.tsx`, `RubricModal.tsx`, job pages | `tests/component/frontend/components/test_AgentAnalysisHeader.test.tsx`, `tests/component/frontend/components/test_RubricModal.test.tsx`, `tests/component/frontend/pages/test_ArtifactsCompanyWatchCriteria.test.tsx`, `test_ArtifactsJobListCriteria.test.tsx`, `test_ArtifactsJobDescCriteria.test.tsx`, `test_ArtifactsGetJobCriteria.test.tsx`, `test_ArtifactsDoJobCriteria.test.tsx`, `test_ArtifactsLikeJobCriteria.test.tsx` |

---

### AST-450 · AST-520 · AST-516

Ten Phase E **`task_key`** values replace **`craft_job_*`**. **Dispatch entry** is the row's **`dispatch_task.task_key`** (**AST-534**) — not **`consult._INPUT_STATE_TO_TASK`** (legacy map, tests only). Seeded **`BUILD_ARTIFACTS`** rows still default to **`contemplate_job`**; Susan may add **`anticipate_scan`** @ **`BUILD_ARTIFACTS`** when schema allows. **`CANDIDATE_REVIEW`** uses **`draft_cover_letter`**. Chain order is **`agent_task.run_next`** only — no step arrays in code.

| Area | Source | Component tests |
| --- | --- | --- |
| Registry + BUILD/CANDIDATE entry keys | `src/utils/config.py` (`TASK_CONFIG`, `BUILD_CONFIG` chain `first_task_key`), `src/core/consult.py` `run_consult_task(dispatch_task_key=…)`, `src/core/dispatcher.py`, `src/data/database.py` (`dispatch_task_admin_defaults`) | `tests/component/utils/test_config.py` (`TestAst450ArtifactPipelineTaskKeys`, `TestAst520AnticipateScanTaskKey`, `TestAst309CoverLetterTaskConfig`), `tests/component/core/test_consult.py` (`TestRunConsultTask`, `TestAst369CoverLetterDispatch`, `TestAst371ResumeArtifactDispatch`, `TestAst534DispatchTaskKeyHonesty`), `tests/component/core/test_dispatcher.py` (`test_ast534_forwards_dispatch_task_key_to_consult`), `tests/component/core/test_agent.py` (artifact chain + `do_task` paths using **`draft_job_resume`** / **`draft_cover_letter`**) |
| Agent story phase + display label | `src/core/agent.py` (`get_entity_agent_story`) | `tests/component/core/test_agent.py` (`TestEntityAgentStory::test_ast520_agent_story_phase_and_print_label`) |
| Recommended Job Analysis Report — Phase E hops | `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` (Phase E **`agent_story`** panel — **AST-520**) |

---

### AST-551 · AST-552 · AST-300

Post-**AST-477** resume **`do_task`** chain: terminal hop JSON keyed to enabled **`artifacts.resume_structure`** section ids; **`run_resume_artifact_chain_for_job`** seeds **`candidate_data`** / **`astral_candidate_id`**; **`{$RESUME_SECTION_CATALOG}`** in **`build_job_token_context`**; terminal persist only on **`finalize_job_resume`** (not global **`artifact_shapes.resume_content`** required-key gate). **AST-552:** candidate **`POST …/approve_artifacts`** (**RECOMMENDED → BUILD_ARTIFACTS** only); structure-aware **`parsed_matches_job_resume_content`** / **`job_has_persisted_resume_body`** persist gates; post-batch **`CANDIDATE_REVIEW`** or **`BUILD_FAILED`** with **`clear_job_artifact_resume_content`** rollback. JAR approve UI is **AST-553**.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-551** | **`parsed_matches_resume_content_shape`** subset match; **`persist_job_artifact_from_parsed`** structure path; chain **`candidate_data`** seed; **`RESUME_SECTION_CATALOG`** token | `src/core/tracker.py`, `src/core/agent.py`, `src/core/consult.py`, `src/utils/config.py` | `tests/component/core/test_tracker.py::TestAst551StructureAlignedResumeChain`; `tests/component/core/test_agent.py::TestRunResumeArtifactChainForJob::test_run_resume_artifact_chain_seeds_candidate_data`; `tests/component/core/test_consult.py::TestAst513JobTokenContext::test_build_job_token_context_resume_section_catalog`; `tests/component/utils/test_config.py::TestAst513JobTokens::test_resume_section_catalog_token_source`; regression **`tests/component/core/test_tracker.py::{TestAst518JobResumeArtifacts,TestPersistJobArtifactFromParsed}`** |
| **AST-552** | Approve API; structure persist gate; batch transitions; resume rollback | `src/ui/api/api_jobs.py`, `src/core/tracker.py`, `src/core/consult.py` | `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_from_recommended`; `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_wrong_state_returns_409`; `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_invalid_transition_returns_409`; `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_missing_job_returns_404`; `tests/component/core/test_tracker.py::TestAst552BuildArtifactsGate`; `tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_artifact_entry_batch_runs_chain_then_cover_letter_for_contemplate_job`; `tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_artifact_entry_batch_errors_skip_cover_letter`; `tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_artifact_entry_batch_empty_persist_build_failed` |
| **AST-553** | JAR structure-keyed resume draft tabs; job `PUT …/artifacts/resume_content`; `ArtifactEditor` job persistence (no Generate) | `src/ui/api/api_jobs.py`, `src/ui/frontend/src/components/ArtifactEditor.tsx`, `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_put_resume_content_persists_via_tracker`; `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_put_resume_content_404_when_job_missing`; `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_put_resume_content_400_when_not_dict`; `tests/component/frontend/components/test_ArtifactEditor.test.tsx` (job persistence mode); `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` (AST-553 resume draft describe) |

**AST-551** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_tracker.py::TestAst551StructureAlignedResumeChain \
  tests/component/core/test_agent.py::TestRunResumeArtifactChainForJob::test_run_resume_artifact_chain_seeds_candidate_data \
  tests/component/core/test_consult.py::TestAst513JobTokenContext::test_build_job_token_context_resume_section_catalog \
  tests/component/utils/test_config.py::TestAst513JobTokens::test_resume_section_catalog_token_source \
  tests/component/core/test_tracker.py::TestAst518JobResumeArtifacts \
  tests/component/core/test_tracker.py::TestPersistJobArtifactFromParsed
```

**AST-552** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_from_recommended \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_wrong_state_returns_409 \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_invalid_transition_returns_409 \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_missing_job_returns_404 \
  tests/component/core/test_tracker.py::TestAst552BuildArtifactsGate \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_artifact_entry_batch_runs_chain_then_cover_letter_for_contemplate_job \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_artifact_entry_batch_errors_skip_cover_letter \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_artifact_entry_batch_empty_persist_build_failed
```

**AST-553** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_put_resume_content_persists_via_tracker \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_put_resume_content_404_when_job_missing \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_put_resume_content_400_when_not_dict
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx
```

---

### AST-610 · AST-611 · AST-609

**AST-609 (parent):** Swap-friendly authentication — Stytch B2C session JWT in **`src/external/stytch.py`**, provider-agnostic **`src/utils/auth.py`** with registerable **`TokenAuthenticator`** (AST-611 wires **`register_token_authenticator(stytch.authenticate_session_jwt)`** via **`src/core/auth_bootstrap.py`**). **`AUTH_CONFIG`** admin lists from env.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-610** | Stytch JWT validate + user dict mapping; **`normalize_user`** / **`is_admin`** / **`validate_bearer_token`** | `src/external/stytch.py`, `src/utils/auth.py`, `src/utils/config.py` (`AUTH_CONFIG`) | `tests/component/external/test_stytch.py::TestAuthenticateSessionJwt`; `tests/component/utils/test_auth.py::{TestIsAdmin,TestNormalizeUser,TestValidateBearerToken}` |
| **AST-611** | Flask **`@require_auth`** / **`@require_admin`**; admin API enforcement; **`/api/me`** + nav filter | `src/core/auth_bootstrap.py`, `src/ui/auth.py`, `src/ui/server.py`, `src/ui/api/api_admin.py`, `src/ui/api/api_candidate.py`, `src/ui/api/api_system.py` | `tests/component/ui/test_auth.py::{TestRequireAuth,TestRequireAdmin}`; `tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::{test_me_requires_bearer,test_me_non_admin_includes_is_admin_false,test_nav_config_omits_admin_group_for_non_admin}`; `tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_non_admin_cannot_create_delete_or_override_state`; `tests/component/ui/test_server.py::TestServeReact::test_serves_index_when_ip_allowlist_restricted` |
| **AST-612** | React Stytch login gate; Bearer **`session_jwt`** on **`api()`**; **`AdminRoute`** on `/admin/*`; non-admin candidate selector lock | `src/ui/frontend/src/lib/api.ts`, `src/ui/frontend/src/contexts/AuthContext.tsx`, `src/ui/frontend/src/components/{RequireAuth,AdminRoute,NavigationShell}.tsx`, `src/ui/frontend/src/contexts/CandidateContext.tsx`, `src/ui/frontend/src/routes.tsx` | `tests/component/frontend/lib/test_api.test.ts`; `tests/component/frontend/contexts/test_AuthContext.test.tsx`; `tests/component/frontend/components/test_RequireAuth.test.tsx`; `tests/component/frontend/components/test_AdminRoute.test.tsx`; `tests/component/frontend/components/test_NavigationShell.test.tsx`; `tests/component/frontend/contexts/test_CandidateContext.test.tsx`. Silent revalidation / keep-mounted: **AST-1408** in [`contexts.md`](contexts.md). |
| **AST-613** | Canonical Stytch magic-link + OAuth redirect URL (`VITE_STYTCH_REDIRECT_URL` with **`/authenticate`** fallback) | `src/ui/frontend/src/lib/stytchRedirect.ts`, `src/ui/frontend/src/pages/Login.tsx` | `tests/component/frontend/lib/test_stytchRedirect.test.ts`; `tests/component/frontend/pages/test_Login.test.tsx` |
| **AST-614** | `launch.sh --vite` auto-runs `npm install --include=dev` when `node_modules/@stytch/react` missing | `launch.sh` (`_ensure_frontend_deps`, `run_vite`) | `tests/component/dev/test_launch_frontend_deps.py::TestLaunchFrontendDeps` |
| **AST-831** | Backend live-project JWT validation — **`max_token_age_seconds=0`**, startup project env log, **`session_not_found`** ops hint | `src/external/stytch.py`, `src/core/auth_bootstrap.py`, `src/utils/auth.py` | **`docs/test-bible/external/stytch.md`** (**AST-831**) |
| **AST-830** | OAuth/magic-link **`/authenticate`** handoff helper + hardened callback page (init gate, single-flight, in-app error) | `src/ui/frontend/src/lib/stytchAuthenticateHandoff.ts`, `src/ui/frontend/src/pages/Authenticate.tsx` | `tests/component/frontend/lib/test_stytchAuthenticateHandoff.test.ts`; `tests/component/frontend/pages/test_Authenticate.test.tsx` — manifest detail **`docs/test-bible/frontend/lib.md`** (**AST-830**) |

**AST-610** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/external/test_stytch.py::TestAuthenticateSessionJwt \
  tests/component/utils/test_auth.py::TestIsAdmin \
  tests/component/utils/test_auth.py::TestNormalizeUser \
  tests/component/utils/test_auth.py::TestValidateBearerToken
```

**AST-611** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/test_auth.py::TestRequireAuth \
  tests/component/ui/test_auth.py::TestRequireAdmin \
  tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_me_requires_bearer \
  tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_me_non_admin_includes_is_admin_false \
  tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_nav_config_omits_admin_group_for_non_admin \
  tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_non_admin_cannot_create_delete_or_override_state \
  tests/component/ui/test_server.py::TestServeReact::test_serves_index_when_ip_allowlist_restricted
```

**AST-612** narrowed run (Vitest — from `src/ui/frontend/`):

```bash
npm run test:component -- \
  ../tests/component/frontend/lib/test_api.test.ts \
  ../tests/component/frontend/contexts/test_AuthContext.test.tsx \
  ../tests/component/frontend/components/test_RequireAuth.test.tsx \
  ../tests/component/frontend/components/test_AdminRoute.test.tsx \
  ../tests/component/frontend/components/test_NavigationShell.test.tsx \
  ../tests/component/frontend/contexts/test_CandidateContext.test.tsx
```

**AST-613** narrowed run (Vitest — from `src/ui/frontend/`):

```bash
npm run test:component -- \
  ../tests/component/frontend/lib/test_stytchRedirect.test.ts \
  ../tests/component/frontend/pages/test_Login.test.tsx
```

**AST-614** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/dev/test_launch_frontend_deps.py::TestLaunchFrontendDeps
```

---

### AST-643 · AST-638

**AST-638 (parent):** Shared **`TokenTextarea`** portaled autocomplete menu appears below the active **`{$`** trigger line (scroll-adjusted), flips above when insufficient viewport room below, and preserves AST-636 portal + open/filter/dismiss/keyboard behavior. All consumers (Manage Tasks, Manage Agents, Anthropic Ad Hoc) inherit from the component — no per-page manifest.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-643** | `menuAnchor` subtracts `scrollTop`; viewport flip; `triggerCharIndex` wiring | `src/ui/frontend/src/components/TokenTextarea.tsx` | Full **`tests/component/frontend/components/test_TokenTextarea.test.tsx`** — **`AST-643`** placement (`menu` fixed `top` strictly below textarea origin on first-line trigger); **`AST-636`** portal; existing open/filter/dismiss/keyboard rows |

**AST-643** narrowed run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_TokenTextarea.test.tsx
```

---

### AST-645 · AST-635

**AST-635 (parent):** Shared **UI-call-to-AI** primary actions (artifact craft **Generate** / **Regenerate**, **Company Search Terms**, Recommended Job Report **Generate Artifacts** / **Working…**) use a shared `.in-flight` CSS modifier on existing `.dep-btn.save` / `.modal-btn.save` buttons — yellow/gold while `generating` / `primaryBusy`, green when idle. **Save** / **Cancel** unchanged.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-645** | Shared `.in-flight` in `App.css`; wire `generating` / `primaryBusy` on three generate controls | `src/ui/frontend/src/App.css`, `ArtifactEditor.tsx`, `ArtifactsCompanySearchTerms.tsx`, `RecommendedJobReportHeader.tsx` | `tests/component/frontend/components/test_ArtifactEditor.test.tsx` — **`AST-645: Generate/Regenerate button uses in-flight class while generating`**; `tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx` — **`AST-645: Generate button uses in-flight class while generating`** (§6c routed page); `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` — **`AST-645: Generate Artifacts primary action uses in-flight class while Working`** |

**AST-645** narrowed run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  ../../../tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx
```

---

### AST-902 · AST-900

**AST-902:** Shared **`ArtifactEditor`** craft-rubric mode — empty **`criteria`** on live Generate is a user-visible error (clears review); page-return **`GET …/generate/<task_key>/pending`** (AST-901) loads recovered criteria into review-then-Save; network interrupt toast points at recovery; **`jobPersistence`** / fixed-field modes skip pending. Six rubric pages inherit via the shared component (no page-file diff — §6c routed-page rule N/A). Backend stash/API: sibling **AST-901**.

| Area | Source | Component tests |
| --- | --- | --- |
| Empty criteria / pending recovery / network interrupt / jobPersistence skip | `src/ui/frontend/src/components/ArtifactEditor.tsx` | **`tests/component/frontend/components/test_ArtifactEditor.test.tsx`** — **`AST-902:*`** cases; revised mocks for pending 404; existing regenerate/save + AST-645 + AST-553 rows |

**AST-902** narrowed run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx
```

---

### AST-904 · AST-900 (UAT fix)

**AST-904:** Save failure toast shows server **`error`** (not hardcoded `"Save failed"`); review mode (`snapshot`) retained. API re-stash/clear ordering: **`docs/test-bible/ui/api/api_candidate.md`** § AST-904.

| Area | Source | Component tests |
| --- | --- | --- |
| Save error toast + keep review | `src/ui/frontend/src/components/ArtifactEditor.tsx` | **`test_ArtifactEditor.test.tsx`** — **`AST-904: Save failure shows server error and keeps review mode`** |

**AST-904** narrowed Vitest:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  -t 'AST-904'
```

---

### AST-905 · AST-900 (UAT fix)

**AST-905:** Page-return pending recovery applies **only when loaded criterion content is empty** — if any tab has non-empty `content` (trim), skip pending fetch/apply (never overwrite existing edits). Backend empty-only gate: **`docs/test-bible/core/candidate.md`** § AST-905. Empty load still recovers via **AST-902** pending path.

| Area | Source | Component tests |
| --- | --- | --- |
| Skip recovery when content exists | `ArtifactEditor.tsx` | **`test_ArtifactEditor.test.tsx`** — **`AST-905: skips pending recovery when loaded criteria already have content`** |
| Empty still recovers | `ArtifactEditor.tsx` | **AST-902** pending recovery case (unchanged) |

**AST-905** narrowed Vitest:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  -t 'AST-905'
```

---

### AST-646 · AST-651 · AST-653 · AST-679 · AST-640

**AST-640 (parent):** Admin-only read-only strip at the bottom of the left nav — environment label when `ASTRAL_DEPLOY_ENV` is any non-empty string (after strip) and server-formatted uptime (AST-679 removed commit hash/tooltip). Non-admins keep the existing footer spacer; no deploy API call.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-646** | `GET /api/deploy_status` (`@require_admin`); `deploy_status.py` payload builder; `AdminDeployFooter` + admin gate in `NavigationShell` | `src/utils/deploy_status.py`, `src/ui/api/api_system.py`, `src/ui/frontend/src/components/{AdminDeployFooter,NavigationShell}.tsx` | `tests/component/utils/test_deploy_status.py`; `tests/component/ui/api/test_api_system.py::TestDeployStatus`; `tests/component/frontend/components/test_AdminDeployFooter.test.tsx`; `tests/component/frontend/components/test_NavigationShell.test.tsx` (admin footer visible; non-admin absent) |
| **AST-651** | UAT: drop `DEPLOY_STATUS_CONFIG` allowlist — `_resolve_environment()` returns stripped raw `ASTRAL_DEPLOY_ENV`; whitespace-only omits label | `src/utils/deploy_status.py`, `src/utils/config.py`, `env.example` | **`tests/component/utils/test_deploy_status.py::TestResolveEnvironment`** — **`test_non_allowlisted_value_returns_raw`** (`eu-west`), **`test_whitespace_only_returns_none`**; keep **`test_valid_local`**, **`test_unset_returns_none`**, payload tests unchanged. No UI/API test edits (mocks unchanged). |
| **AST-653** | UAT: on `ASTRAL_DEPLOY_ENV=local`, UI-initiated LLM paths auto-enable debug via `is_local_deploy_env()` / `ui_llm_debug()`; non-local unchanged | `src/utils/deploy_status.py`, `src/ui/api/{api_intake,api_admin,api_candidate}.py`, `src/core/{dispatcher,candidate}.py` | **`tests/component/utils/test_deploy_status.py::TestLocalDeployDebug`** — local/staging/unset OR semantics for `is_local_deploy_env` and `ui_llm_debug`; existing **`TestResolveEnvironment`** + payload tests unchanged. No log-string golden tests (AST-538 gating only). |
| **AST-679** | AST-658: drop commit tip from deploy status API + admin footer — env (when set) and uptime only; no git subprocess | `src/utils/deploy_status.py`, `AdminDeployFooter.tsx`, `App.css` | **`TestGetDeployStatusPayload`** — renamed **`test_includes_uptime_without_environment`**; drop `_git_head_info` mocks/assertions. **`TestDeployStatus`** — expected JSON without commit keys. **`test_AdminDeployFooter.test.tsx`** — env + uptime only; no commit text/tooltip. **`test_NavigationShell.test.tsx`** — deploy_status mocks without commit fields |
| **AST-682** | AST-675 child: env label native `title` lists up to **20** `merge_tickets` — **superseded by AST-691** (hover tooltip); manifest rows below retained for historical pytest names only | `AdminDeployFooter.tsx` | *(see **AST-691**)* |
| **AST-690** | AST-675 UAT bug: click-to-toggle popup on env label — **superseded by AST-691** (hover tooltip + pointer cursor); historical pytest names only | `AdminDeployFooter.tsx`, `App.css` | *(see **AST-691**)* |
| **AST-691** | AST-675 UAT fix: replace AST-690 click popup with **500ms hover** tooltip on env label when `merge_tickets` non-empty — up to **20** plain lines (`ticket_id` + `fmtTime(recorded_at)`), most recent first; `span` + `nav-deploy-env-interactive` (`cursor: pointer`) when interactive; static span when empty/missing; wrapper hover keeps tooltip open; no `title`; no backend/API changes | `AdminDeployFooter.tsx`, `App.css` | **`test_AdminDeployFooter.test.tsx`** — **`test_shows_merge_ticket_tooltip_after_500ms_hover_on_env_wrap_when_merge_tickets_present`**; **`test_hides_merge_ticket_tooltip_before_500ms_hover_and_on_mouse_leave`**; **`test_renders_static_environment_span_when_merge_tickets_empty_or_missing`**; **`test_caps_merge_ticket_tooltip_at_20_lines`**; existing env/uptime/error tests unchanged. **`test_NavigationShell.test.tsx`** unchanged (non-admin gate) |
| **AST-798** | UAT FIX: static env label (empty `merge_tickets`) uses **default** cursor — `.nav-deploy-env { cursor: default; user-select: none; }`; interactive class unchanged. Linear key env precedence in `external/linear.py` (rollcall names) — see **`external/linear.md` AST-798** | `App.css`, `src/external/linear.py`, `env.example` | **`test_AdminDeployFooter.test.tsx`** — extend **`test_renders_static_environment_span_when_merge_tickets_empty_or_missing`**: `nav-deploy-env` class, **App.css source contract** (`cursor: default`, `user-select: none` on `.nav-deploy-env`), no interactive class. **`tests/component/external/test_linear.py::TestResolveLinearApiKey`** (3 tests) |

**AST-798** narrowed run:

```bash
.venv/bin/python -m pytest tests/component/external/test_linear.py -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_AdminDeployFooter.test.tsx
```

**AST-691** narrowed run:

```bash
cd src/ui/frontend && npx tsc -b --noEmit

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_AdminDeployFooter.test.tsx \
  ../../../tests/component/frontend/components/test_NavigationShell.test.tsx
```

**AST-690** narrowed run:

```bash
cd src/ui/frontend && npx tsc -b --noEmit

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_AdminDeployFooter.test.tsx
```

**AST-682** narrowed run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_AdminDeployFooter.test.tsx
```

**AST-646** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_deploy_status.py \
  tests/component/ui/api/test_api_system.py::TestDeployStatus

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_AdminDeployFooter.test.tsx \
  ../../../tests/component/frontend/components/test_NavigationShell.test.tsx
```

**AST-651** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_deploy_status.py::TestResolveEnvironment
```

**AST-653** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_deploy_status.py::TestLocalDeployDebug
```

**AST-679** narrowed run (same surface as AST-646; commit keys removed):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_deploy_status.py::TestGetDeployStatusPayload \
  tests/component/ui/api/test_api_system.py::TestDeployStatus

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_AdminDeployFooter.test.tsx \
  ../../../tests/component/frontend/components/test_NavigationShell.test.tsx
```

---

### AST-647 · AST-652 · AST-633

**AST-633 (parent):** Shared list-table presentation for **ListPage** and bespoke grouped tables: **N** frozen left data columns (default **2** from `UI_CONFIG` via `/api/system/ui_config`), checkbox and row-action columns always frozen in addition to **N**, sticky header in the table scroll region, horizontal scroll for wide tables, long cells truncated to **30** chars with full value in hover tooltip (`title`).

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-647** | `UI_CONFIG` defaults; shared `listTableLayout` / `uiConfig` / `ListTableTruncatedCell`; ListPage freeze + truncate; **AdminScheduledActions** bespoke table with `frozenDataColumns={3}` *(AST-1818: page override now `1`, Task only)* | `src/utils/config.py`, `src/ui/frontend/src/lib/{listTableLayout,uiConfig}.ts`, `ListPage.tsx`, `ListTableTruncatedCell.tsx`, `App.css`, `AdminScheduledActions.tsx` | `tests/component/frontend/lib/test_listTableLayout.test.ts`; `tests/component/frontend/components/test_ListTableTruncatedCell.test.tsx`; `tests/component/frontend/components/test_ListPage_listTableLayout.test.tsx`; `tests/component/frontend/components/test_ListPage.test.tsx` (api mock + `/api/system/ui_config` — **uiConfig** extract regression); `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — **`AST-647: phase table freezes only the Task column`** (renamed **AST-1818**) + candidate-filter test fixes; `tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_ui_config_includes_list_table_layout_defaults` |
| **AST-652** | UAT: drop force-fit (`table-layout: fixed` / `width: 100%`); default `.list-page-table` autosize; remove `horizontalScrollable` gate and redundant `--auto` / inline overrides; Scheduled Actions phase tables drop `%` column widths | `App.css`, `ListPage.tsx`, `AdminAgentTimesheets.tsx`, `AdminCostReconciliation.tsx`, `AdminScheduledActions.tsx`, `JobsInReview.tsx`, `JobsRecommended.tsx`, `JobsSkipped.tsx` | `tests/component/frontend/components/test_ListPage_listTableLayout.test.tsx` — **`AST-652: default list-page-table uses autosize layout`**; `tests/component/frontend/components/test_ListPage.test.tsx` (drop obsolete `horizontalScrollable` prop); re-run **AST-647** manifest rows above (freeze/truncate unchanged) |

**AST-652** narrowed run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_ListPage_listTableLayout.test.tsx \
  ../../../tests/component/frontend/components/test_ListPage.test.tsx
```

**AST-647** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_ui_config_includes_list_table_layout_defaults

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_listTableLayout.test.ts \
  ../../../tests/component/frontend/components/test_ListTableTruncatedCell.test.tsx \
  ../../../tests/component/frontend/components/test_ListPage_listTableLayout.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx
```

---

### AST-779 · AST-770

**Error toast diagnostics:** **`Toast.tsx`** — error variant defaults to **15s** auto-dismiss; **click-to-copy** is limited to the message / “Click to copy” region (`.toast-copy-target.toast-error-clickable`); dedicated dismiss (`icon-control` ×, `aria-label="Dismiss"`) closes without clipboard write; status glyph is warning `\u26A0` (not ✗). Success/info unchanged (~3s, non-interactive). Helpers in **`toastDiagnostics.ts`**. Product split dismiss vs copy = **AST-1549**; tests/bible alignment = **AST-1553**.

| Area | Source | Component tests |
| --- | --- | --- |
| Toast UX + copy bundle + dismiss | `src/ui/frontend/src/components/Toast.tsx`, `src/ui/frontend/src/lib/toastDiagnostics.ts`, `App.css` | `tests/component/frontend/components/test_Toast.test.tsx` — **AST-779** (15s error / 3s success, copy-target click-copy + copied feedback); **AST-1553** dismiss-without-copy; glyph `\u26A0` |
| Representative ApiError wiring | `AdminAgentPrompts.tsx`, `CandidateProfile.tsx` | Existing page tests cover error toast text paths; **no new page manifest** — Toast auto-context satisfies AC 3–4 for pages passing `{ text, variant: "error" }` only |

**AST-779** / **AST-1553** narrowed run (Vitest only):

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_Toast.test.tsx
```

### AST-1553 · AST-1543 (gap)

**Gap sibling of AST-1549.** Retarget Toast click-copy / glyph assertions to AST-1549 hit targets; land dismiss-without-copy coverage. Product UI is AST-1549 — this ticket is tests/bible only.

## QA test manifest

1. **Bug-repro (must flip red→green with AST-1549 product):** `tests/component/frontend/components/test_Toast.test.tsx` — **`AST-1553: dismiss closes error toast without copying`** (Dismiss → no `clipboard.writeText`; `onDone` after 300ms)
2. Retargeted click-copy: same file — **`AST-779: error toast is clickable and copies diagnostic bundle`** (`.toast-copy-target.toast-error-clickable`, not root)
3. Glyph: variants smoke — error status `\u26A0`
4. Duration contracts unchanged: **`AST-779: error toast defaults to 15000ms dismiss`**, **`AST-779: success toast still dismisses at 3000ms default`**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_Toast.test.tsx \
  --testNamePattern="AST-1553|AST-779|shows success"
```

---

### AST-783 · AST-756

**`RepoJsonDivergenceBanner`:** fetches **`/api/admin/repo_json/status`**, shows gold warning when `diverged`, **Revert to file** via **`useUserConfirm`** danger dialog → **`POST /api/admin/repo_json/revert/<tableKey>`**; refetches on `refreshToken` prop from parent pages. **AST-1506** adds **Show Differences** (`GET /compare/<tableKey>` modal) and **Update file with table version** (`POST /write/<tableKey>` + status refetch / `onReverted`).

| Area | Source | Component tests |
| --- | --- | --- |
| Banner hide/show + revert flow | `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` | `tests/component/frontend/components/test_RepoJsonDivergenceBanner.test.tsx` (**AST-783**) |
| Show Differences + Update file + copy rewrite | same | same (**AST-1506** describe block) |

Routed pages (unchanged wiring — regression only): **`docs/test-bible/frontend/pages.md`** § AST-783.

---

### AST-1506 · AST-1455

**Parent:** [AST-1455 — Show Differences and Update file with table version](https://linear.app/astralcareermatch/issue/AST-1455). **Publish:** `origin/sub/AST-1455/AST-1506-show-differences-update-file-divergence-banner`. **Depends:** sibling **AST-1505** compare/write admin routes.

Wires **Show Differences** modal and **Update file with table version** confirm/write into shared **`RepoJsonDivergenceBanner`**; rewrites warning copy (no restart/deploy overwrite claim). **`AdminAgentPrompts`** / **`AdminTaskPrompts`** unchanged — `tableKey` prop isolates agent vs agent_task.

| Area | Source | Component tests |
| --- | --- | --- |
| Copy + compare modal + write/cancel | `RepoJsonDivergenceBanner.tsx` | **`test_RepoJsonDivergenceBanner.test.tsx`** — **`RepoJsonDivergenceBanner — AST-1506`** |
| Routed page banner mount (regression) | `AdminAgentPrompts.tsx`, `AdminTaskPrompts.tsx` | **`test_AdminAgentPrompts.test.tsx`**, **`test_AdminTaskPrompts.test.tsx`** — existing **AST-783** nodes |

**Broken / obsolete this pass:** none — **AST-783** revert test still valid; page tests unchanged.

**Integration:** none revised; do not invent new integration coverage.

## QA test manifest

1. Banner Show/Update/copy: `tests/component/frontend/components/test_RepoJsonDivergenceBanner.test.tsx` — **`RepoJsonDivergenceBanner — AST-1506`**
2. Revert regression: `tests/component/frontend/components/test_RepoJsonDivergenceBanner.test.tsx` — **`AST-783`** nodes
3. Routed page banner regression: `tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx` — **`AST-783: shows agent repo JSON divergence banner on routed page`**; `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx` — **`AST-783: shows task repo JSON divergence banner on routed page`**

**AST-1506** narrowed run:

```bash
cd src/ui/frontend && npx tsc -b --noEmit
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_RepoJsonDivergenceBanner.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx \
  -t "AST-783|AST-1506"
```

**Pass criterion:** Vitest green on manifest lines + `tsc -b --noEmit` — not zero-arg harness / branch-lock gate.

### AST-1511 · AST-1455 (fix lane — modal scroll)

**Parent:** [AST-1455](https://linear.app/astralcareermatch/issue/AST-1455). **Publish:** `origin/sub/AST-1455/AST-1511-show-differences-modal-does-not-scroll`. **Fix:** inner scroll wrapper on **Show Differences** wide modal (`RepoJsonDivergenceBanner.tsx` only).

| Area | Source | Component tests |
| --- | --- | --- |
| Modal body scroll for tall compare payload | `RepoJsonDivergenceBanner.tsx` | **`test_RepoJsonDivergenceBanner.test.tsx`** — **`[bug-repro] AST-1511: Show Differences modal scrolls to later changed rows`** |

**Broken / obsolete this pass:** none — **AST-1506** Show/Update/Revert tests unchanged.

**Integration:** none revised.

## QA test manifest

1. **[bug-repro]** modal scroll reachability (≥4 `changed_rows`): `tests/component/frontend/components/test_RepoJsonDivergenceBanner.test.tsx` — **`RepoJsonDivergenceBanner — AST-1511`**
2. **AST-1506** regression: same file — **`RepoJsonDivergenceBanner — AST-1506`** + **`AST-783`** nodes

**AST-1511** narrowed run:

```bash
cd src/ui/frontend && npx tsc -b --noEmit
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_RepoJsonDivergenceBanner.test.tsx \
  -t "AST-1511|AST-1506|AST-783"
```

**Pass criterion:** `[bug-repro]` red on pre-fix product, green after make-fix; Vitest green on regression nodes post-fix.

### AST-1767 · AST-1754 (gap — shared Modal shell scroll)

**Parent:** [AST-1754 — All modals must be vertically scrollable](https://linear.app/astralcareermatch/issue/AST-1754). **Publish:** `origin/sub/AST-1754/AST-1767-gap-modal-shell-scroll-tests`. **Gap from** `[board-betty] TESTS: REVISE` on **AST-1764** — product shell scroll is **AST-1764**; this ticket is bible + component test only.

| Area | Source | Component tests |
| --- | --- | --- |
| Shared wide Modal shell scroll for tall direct children | `Modal.tsx` + `App.css` (product: **AST-1764**) | **`test_Modal.test.tsx`** — **`[bug-repro] AST-1767: wide Modal body scrolls tall direct children`** |

**Does not obsolete AST-1511** — call-site Show Differences wrapper remains covered separately in `test_RepoJsonDivergenceBanner.test.tsx`.

**Broken / obsolete this pass:** none — existing `test_Modal` AST-1301 / AST-1302 / AST-1334 nodes unchanged.

**Integration:** none.

## QA test manifest

1. **[bug-repro]** wide shell scroll (tall direct children, no call-site wrapper): `tests/component/frontend/components/test_Modal.test.tsx` — **`Modal — AST-1767`**
2. Modal regression: same file — **`AST-1301`** / **`AST-1302`** / **`AST-1334`** nodes

**AST-1767** narrowed run:

```bash
cd src/ui/frontend && npx tsc -b --noEmit
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_Modal.test.tsx \
  -t "AST-1767"
```

**Pass criterion:** `[bug-repro]` red against pre-AST-1764 product (`overflow: hidden` on `.modal-card--wide .modal-body`); green once AST-1764 shell scroll (`overflow-y: auto` + `min-height: 0`) is present. Vitest green on Modal regression nodes.

### AST-948 · AST-858

**AST-858 (parent):** Redesign Recommended Job Report — horizontal **Summary** / **Analysis** / **Artifacts** tabs, collapsible section chrome, sticky header (deeplinks, copy, Print Resume/Cover). **AST-948** owns shell/header only; section bodies are siblings **AST-949** / **AST-950** / **AST-951**.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-948** | Horizontal `TabBar` shell; `ReportSectionList` empty chrome; sticky header deeplinks + Copy Application Email / LinkedIn + Print Resume/Cover; Generate/Cancel on Artifacts `leading` strip; drop JAR `SideTabPanel` / Preview Materials | `JobAnalysisReportModal.tsx`, `RecommendedJobReportHeader.tsx`, `ReportSectionList.tsx`, `App.css`, `StateUiContext.tsx`, `recommendedJobReport.tsx` | **`test_JobAnalysisReportModal.test.tsx`** — **`JobAnalysisReportModal — AST-948 horizontal shell`**; **`test_ReportSectionList.test.tsx`** — **`ReportSectionList — AST-948`**; revised **`test_JobsRecommended.test.tsx`** row-click (horizontal tabs — AC3 list entry) |

**Obsolete / revised this pass:** left-rail `.side-tab-list` / upshot body / Preview Materials / Apply-button / ArtifactEditor-in-JAR asserts in **`test_JobAnalysisReportModal.test.tsx`** (AST-565 / AST-581 / AST-553 body paths). **AST-645** Generate in-flight coverage kept — switch to Artifacts tab first.

**AST-948** narrowed run (JAR is a modal — **§6c** routed-page rule N/A for modal-only; list entry regression is the JobsRecommended page row):

```bash
cd src/ui/frontend && npx tsc -b --noEmit
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  ../../../tests/component/frontend/components/test_ReportSectionList.test.tsx \
  ../../../tests/component/frontend/lib/test_recommendedJobReport.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast565_recommended_report_manifest_tabs
```

---

### AST-949 · AST-858

**AST-858 (parent):** Recommended Job Report redesign. **AST-949** fills Summary tab section bodies left empty by **AST-948**: Job Summary (`whole_jd_upshot`), Company Upshot (`prefilter_company_notes` from company GET), Noteworthy Caveats / Questions to Ask, Raw JD (collapsed); content-aware `default_expanded`; graceful empty states.

> **AST-2071:** Company Upshot now reads `company_upshot` (not `prefilter_company_notes`); AST-949 Summary cases revised — see § AST-2071 below.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-949** | Summary `renderSummarySection` bodies + company notes lift + content-aware expand | `JobAnalysisReportModal.tsx` | **`test_JobAnalysisReportModal.test.tsx`** — **`JobAnalysisReportModal — AST-949 Summary tab sections`**; revised AST-948 empty-upshot shell case for new empty copy |

**AST-949** narrowed run (modal — §6c N/A):

```bash
cd src/ui/frontend && npx tsc -b --noEmit
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx
```

---

### AST-950 · AST-858

**AST-858 (parent):** Recommended Job Report redesign. **AST-950** fills Analysis tab: JD/DO/GET/LIKE sections (no Overview); header **grade + confidence** row via `ReportSectionList` `renderMetadata` + `buildPhaseSectionGradeConfidenceRow`; expanded body = phase `take_*` above `AgentAnalysisHeader`.

**AST-1327 / AST-1328:** Analysis metadata uses job-carried flatten (`jd_rubric` et al. on job payload), not `grade_rubric_by_field` live lookup for header identity. **All four Analysis sections start collapsed** (Summary / Artifacts expand rules unchanged). AST-948 shell case that asserted JD default-expanded revised to collapse-all.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-950** | Analysis metadata + bodies; `renderMetadata` slot | `JobAnalysisReportModal.tsx`, `ReportSectionList.tsx`, `recommendedJobReport.tsx`, `App.css` | **`test_JobAnalysisReportModal.test.tsx`** — **`JobAnalysisReportModal — AST-950 Analysis tab grades and confidence`**; **`test_ReportSectionList.test.tsx`** — **`ReportSectionList — AST-950 renderMetadata`**; **`test_recommendedJobReport.test.tsx`** — **`AST-950 grade+confidence header row`** |
| **AST-1328** | Job-carried meteorite header + collapse-all; revise obsolete live-artifact / JD-expanded asserts | same JAR + lib | JAR **`AST-1328: Analysis header uses job-carried jd_rubric when live jobdesc_rubric underlaps`** (bug-repro); lib **`AST-1328: header shows every job-carried vector…`**; AST-948 chrome **`all phases collapsed by default`** |

**Sibling note:** AST-949 Summary body tests live in the same JAR file — run with `--testNamePattern="AST-950|AST-1328"` (plus ReportSectionList / lib files) so parallel tips without Summary bodies stay green.

**AST-950 / AST-1328** narrowed run:

```bash
cd src/ui/frontend && npx tsc -b --noEmit
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  ../../../tests/component/frontend/components/test_ReportSectionList.test.tsx \
  ../../../tests/component/frontend/lib/test_recommendedJobReport.test.tsx \
  --testNamePattern="AST-950|AST-1328"
```

---

### AST-951 · AST-858

**AST-858 (parent):** Recommended Job Report redesign. **AST-951** owns Artifacts tab layouts: empty → **Generate Artifacts**; in-flight `BUILD_ARTIFACTS` / `BUILD_ARTIFACTS.<hop>` → **Generating…** + **Cancel**; populated → editable Job Resume / Cover / Application Questions via `ArtifactEditor` (no Reset/Regenerate).

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-951** | Empty / in-flight / populated Artifacts; helpers; revise AST-948 empty-chrome / Working… asserts | `JobAnalysisReportModal.tsx`, `recommendedJobReport.tsx` | **`test_JobAnalysisReportModal.test.tsx`** — **`JobAnalysisReportModal — AST-951 Artifacts tab layouts`** (+ revised AST-948 Artifacts cases); **`test_recommendedJobReport.test.tsx`** — **`AST-951 Artifacts helpers`** |

**Sibling note:** Run with `--testNamePattern="AST-951|AST-948"` so Summary/Analysis sibling bodies are not required on this tip.

**AST-951** narrowed run:

```bash
cd src/ui/frontend && npx tsc -b --noEmit
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  ../../../tests/component/frontend/lib/test_recommendedJobReport.test.tsx \
  --testNamePattern="AST-951|AST-948"
```

---

### AST-996 · AST-994

**AST-996:** `ArtifactEditor` round-trips non-string section values (experience job array) as pretty JSON on load/Generate and parses JSON on Save (`experience_jobs` type or `key === "experience"` in structure mode). Invalid JSON → toast **Experience must be valid JSON** and abort PUT. Primary core/config coverage: **`docs/test-bible/core/candidate.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| JSON load / Save / invalid toast | `ArtifactEditor.tsx` | **`test_ArtifactEditor.test.tsx`** — **`AST-996: experience job array loads as JSON and Saves as parsed array`**, **`AST-996: invalid experience JSON shows toast and aborts Save`** |

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  --testNamePattern="AST-996"
```

### AST-1064 · AST-1059

**Publish:** `origin/sub/AST-1059/AST-1064-group-by-aligned-rubric-jobs-list-tables`.

`jobCarriedRubricKey` / fingerprint / `groupJobsByAlignedRubric` / `buildJobListRubricColumnsForGroup` / `analysisTimeScoreForJob` — list pages never read live candidate artifacts for columns. Page coverage: **`docs/test-bible/frontend/pages.md`** (**AST-1064**).

| Area | Source | Component tests |
| --- | --- | --- |
| Job-carried list helpers | `lib/rubricDisplay.ts` | **`test_rubricDisplay.test.ts`** — **`AST-1064 job-carried list helpers`** |

**Broken / obsolete:** none — `buildJobListRubricColumns` live-artifact path retained for non-list callers.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_rubricDisplay.test.ts \
  --testNamePattern="AST-1064"
```


---

### AST-1075 · AST-953

**Parent:** [AST-953 — Topic Menu Generation](https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation). **Publish:** `origin/sub/AST-953/AST-1075-estelle-preamble-confirm-and-topic-menu-generation`.

`IntakeTopicMenuPanel` — ui_config `topic_menu_gen.ui` labels; first-turn Estelle confirm (“Anything here you would change?”); Accept → generate → menu summary; Send posts revise message without generate until `accepted`. Page handoff: **`docs/test-bible/frontend/pages.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Confirm / accept / generate panel | `IntakeTopicMenuPanel.tsx` | **`test_IntakeTopicMenuPanel.test.tsx`** |

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_IntakeTopicMenuPanel.test.tsx
```


---

### AST-1081 · AST-1065

**Parent:** [AST-1065 — Update candidate ui for contact info](https://linear.app/astralcareermatch/issue/AST-1065/update-candidate-ui-for-contact-info). **Publish:** `origin/sub/AST-1065/AST-1081-contact-shapes-websites-full`.

FormFields `string_list`: ordered text inputs + Remove + Add (label `Add`); value round-trips as `string[]`; non-array → `[]`. Profile page host = **AST-1082** (§6c page tests there). Core/config: **`docs/test-bible/core/candidate.md`**, **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| string_list Add / edit / Remove / non-array | `FormFields.tsx` | **`test_FormFields.test.tsx`** — **`FormFields string_list (AST-1081)`** |

**Broken / obsolete:** none — additive field type.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_FormFields.test.tsx
```

---

### AST-1200 · AST-1198

**Parent:** [AST-1198 — Rubric criteria prompts are not appearing in UI Artifacts](https://linear.app/astralcareermatch/issue/AST-1198/rubric-criteria-prompts-are-not-appearing-in-ui-artifacts). **Publish:** `origin/sub/AST-1198/AST-1200-restore-rubric-criteria-prompts`.

Candidate Artifacts criteria pages share **`ArtifactEditor`** without `jobPersistence`: expand-all via `useSectionExpandPolicy` (`criteriaExpandAll = !jobPersistence && rubricMode`) so criterion prompt textareas are visible on load; one-shot seed per `(selectedId, artifactKey)` (collapse stays closed while typing). **jobPersistence** dict tabs (Recommended Job Modal) stay expand-one. Structure mode sets `fixedFields` → `rubricMode` false → stays expand-one. Backfill ops map: **`docs/test-bible/dev/backfill_rubric_vectors.md`**. Job List page smoke: **`docs/test-bible/frontend/pages.md`**. No page-file product diff — §6c routed-page rule N/A; Job List assert is additive AC1 smoke.

| Area | Source | Component tests |
| --- | --- | --- |
| Expand-all prompt bodies | `ArtifactEditor.tsx` | **`test_ArtifactEditor.test.tsx`** — **`AST-1200: candidate criteria expand-all shows prompt bodies without chevron click`** |
| One-shot seed (collapse survives typing) | same | **`AST-1200: collapse one criterion stays closed while typing in another`** |
| Empty New Criterion affordance | same | **`AST-1200: empty criteria page still shows New Criterion editor expanded`** |
| jobPersistence expand-one boundary | same | **`AST-1200: jobPersistence dict tabs stay expand-one (bodies hidden until expand)`** |
| Structure mode expand-one boundary | same | **`AST-1200: structure mode stays expand-one (not criteria expand-all)`** |

**Broken / obsolete:** none — additive expand policy; existing AST-902 / AST-553 / AST-996 rows stay.

**Integration:** no existing scenario asserts CollapsiblePanel expand policy on Artifacts criteria — no revision; do not invent new integration coverage.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  --testNamePattern="AST-1200"
```

### AST-1253 · AST-1243

**Parent:** [AST-1243 — Candidate Artifacts now daisy chain](https://linear.app/astralcareermatch/issue/AST-1243/candidate-artifacts-now-daisy-chain). **Publish:** `origin/sub/AST-1243/AST-1253-generate-regenerate-handoff`.

Chain `ArtifactEditor` pages: empty **Generate** / **Regenerate** (Yes/No modal listing `artifacts_chain_hop_labels`) → `POST …/generate_artifacts`. Non-chain / `craft_resume_base` keep ad-hoc generate. Fixture: **`stateUiManifestFixture.ts`** chain fields. Search Terms page: **`docs/test-bible/frontend/pages.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Empty Generate + Regenerate Yes/No | `ArtifactEditor.tsx` | **`test_ArtifactEditor.test.tsx`** — **`AST-1253:*`** |
| AST-904 Save-after-regen stays non-chain | same | revised **`AST-904`** (`craft_rubric`) |

**Broken / obsolete:** per-page ad-hoc regenerate→review for chain `taskKey`s (AST-677 Watch Criteria; Search Terms populate-from-craft).

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  --testNamePattern="AST-1253|AST-904"
```

### AST-1286 · AST-1284

**Parent:** [AST-1284 — Make left nav responsive](https://linear.app/astralcareermatch/issue/AST-1284/make-left-nav-responsive). **Publish:** `origin/sub/AST-1284/AST-1286-responsive-left-nav-hamburger-shell`.

`NavigationShell` collapses below 1024px into hamburger + overlay drawer (backdrop dismiss, close on pathname change); narrow mode uses a checked candidate list; wide mode keeps the native `<select>`. Admin deploy footer gate unchanged. jsdom `matchMedia` stub lives in `tests/component/frontend/test-utils.tsx` (`stubNavViewport`) — default wide so existing shell mounts keep the combobox. No page-file product diff — §6c routed-page rule N/A.

| Area | Source | Component tests |
| --- | --- | --- |
| Wide native select + existing nav/footer | `NavigationShell.tsx` | **`test_NavigationShell.test.tsx`** — existing cases + **`AST-1286 responsive shell` → wide viewport keeps native candidate select** |
| Narrow drawer open / backdrop dismiss | same + `App.css` | **`narrow: hamburger opens drawer; backdrop dismisses without route change`** |
| Close on navigate | same | **`narrow: enabled nav destination navigates and closes drawer`** |
| Narrow checked candidate list (admin) | same | **`narrow: admin checked candidate list selects and marks current`** |
| Narrow non-admin lock + no deploy footer | same | **`narrow: non-admin cannot change candidate; deploy footer omitted`** |
| AST-709 nav-escape (shell mount) | `NavigationShell` under routes | **`test_AdminAgentTimesheets.test.tsx`** — **`nav click away from Agent Timesheets stays on destination`** (revised via `stubNavViewport` default) |

**Broken / obsolete:** prior `test_NavigationShell` + AST-709 shell mount crashed on missing `window.matchMedia` after product Stage 1 — fixed by `stubNavViewport` in test-utils (wide default) + narrow overrides in AST-1286 cases.

**Integration:** `tests/integration/scenarios/test_candidate_nav_api.py` asserts API nav_config/candidates only — no shell/CSS contract; no revision. Do not invent new integration coverage.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_NavigationShell.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminAgentTimesheets.test.tsx
```

---

### AST-1369 · AST-1361

**Parent:** [AST-1361 — Freeze the Astral Logo and the candidate selection](https://linear.app/astralcareermatch/issue/AST-1361/freeze-the-astral-logo-and-the-candidate-selection). **Publish:** `origin/sub/AST-1361/AST-1369-pin-left-nav-logo-and-candidate-chrome`.

`NavigationShell` + `App.css` split the left nav into `.sidebar-chrome` (logo + candidate control, `flex-shrink: 0`) and `.sidebar-scroll` (loading/error/groups + admin footer/spacer, `flex: 1; min-height: 0; overflow-y: auto`). `.sidebar` uses `overflow: hidden` (no whole-pane scroll). No sticky positioning; admin deploy footer stays in the scroll region. AST-1286 responsive shell (wide select / narrow drawer+menu) unchanged. No page-file product diff — §6c routed-page rule N/A.

| Area | Source | Component tests |
| --- | --- | --- |
| Chrome / scroll DOM split (wide) | `NavigationShell.tsx` + `App.css` | **`test_NavigationShell.test.tsx`** — **`AST-1369 pinned left-nav chrome` → wide: logo + candidate live in sidebar-chrome; groups + footer in sidebar-scroll** |
| Same split on narrow + menu in chrome | same | **`narrow: same chrome/scroll split; candidate menu stays in chrome`** |
| Loading/error in scroll region | same | **`loading/error messages render inside sidebar-scroll, not chrome`** |
| Responsive shell regression (AC4–5) | same | **`AST-1286 responsive shell`** block (hamburger/backdrop/navigate/candidate lock) — re-run |

**Broken / obsolete:** none — existing shell selectors (combobox, hamburger, nav groups, deploy footer) still resolve after the wrapper divs.

**Integration:** `tests/integration/scenarios/test_candidate_nav_api.py` — API-only; no shell/CSS contract; no revision. Do not invent new integration coverage.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_NavigationShell.test.tsx
```

---

### AST-1302 · AST-1166 (list icon-control remediation)

**Parent:** [AST-1166 — Button consistency](https://linear.app/astralcareermatch/issue/AST-1166/button-consistency). **Publish:** `origin/sub/AST-1166/AST-1302-list-icon-control-remediation`.

Consume landed `pattern.ui.icon-control`: list row actions + modal × + CollapsiblePanel chevron use `className="icon-control"`; cramped two-letter labels become single initials (`Sk`→`S`, `Jr`→`J`, `Re`→`R`, `In`→`I`, `Gh`→`G`); Manage Candidates Set dispatch tasks → `T`; Agents row Delete → `D`. Retire leftover `.job-list-icon-btn` / `.list-page-edit-btn` / `.modal-close` / `.collapsible-panel-chevron-btn`. Handlers / `disabled` / `aria-label` unchanged. Labeled sweep (including Scheduled Actions Run/Stop and modal Skip This Job) stays **AST-1301**.

| Area | Source | Component tests |
| --- | --- | --- |
| Job-list row actions | `CandidateJobRowActions.tsx` + `App.css` | **`test_CandidateJobRowActions.test.tsx`** — existing Skip/Resurrect handlers; **`CandidateJobRowActions — AST-1302 icon-control`** (initials + class + leftover CSS retired + post-applied `R/I/X/G` handlers) |
| Manage Candidates row column (**§6c**) | `AdminManageCandidates.tsx` | **`test_AdminManageCandidates.test.tsx`** — **`AST-1302: row actions are icon-control`** |
| Manage Agents row Delete (**§6c**) | `AdminAgentPrompts.tsx` | **`test_AdminAgentPrompts.test.tsx`** — **`AST-1302: row Delete is icon-control with D`** |
| Scheduled Actions modal × (**§6c**) | `AdminScheduledActions.tsx` | **`test_AdminScheduledActions.test.tsx`** — **`AST-1302: Add Task and Kill Running × are icon-control`** |
| Shared Modal × | `Modal.tsx` | **`test_Modal.test.tsx`** — **`AST-1302: header close is icon-control`** |
| CollapsiblePanel chevron | `CollapsiblePanel.tsx` | **`test_CollapsiblePanel.test.tsx`** — **`AST-1302: chevron is icon-control`** |

**Existing coverage (re-run):** `test_JobsRecommended.test.tsx` Skip-by-aria-label cases (page file not edited); `test_JobDetailModal.test.tsx` **Skip This Job** / `entity-skip-btn` (excluded).

**Broken / obsolete:** none — existing tests use `aria-label` / role names that this ticket kept.

**Integration:** no existing scenario asserts list-row / modal-close class names — no drift.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_CandidateJobRowActions.test.tsx \
  ../../../tests/component/frontend/components/test_Modal.test.tsx \
  ../../../tests/component/frontend/components/test_CollapsiblePanel.test.tsx

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageCandidates.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  -t "AST-1302"

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx \
  -t "Skip"
```

---

### AST-1301 · AST-1166 (labeled-button remediations)

**Parent:** [AST-1166 — Button consistency](https://linear.app/astralcareermatch/issue/AST-1166/button-consistency). **Publish:** `origin/sub/AST-1166/AST-1301-full-frontend-audit-labeled-button-remediation`.

Consume landed `pattern.ui.shared-button-roles`: labeled actions move onto `btn primary` / `secondary` / `danger` / `primary in-flight`. Leftover `.modal-btn` / `.dep-btn` / `.list-page-bulk-btn` / `.timesheet-export-btn` / `.entity-skip-btn` / `.dispatch-log-copy-btn` / `.recommended-report-copy-link` / `.section-expand-chrome button` / `.manage-email-toolbar button` deleted. Handlers / `disabled` / labels unchanged (Land Meteorite still `disabled={!landEnabled}`). Icon-control files stay **AST-1302** (`modal-close`, `list-page-edit-btn`, `job-list-icon-btn`, `sql-hist-btn`).

| Area | Source | Component tests |
| --- | --- | --- |
| Shared Modal footer | `Modal.tsx` | **`test_Modal.test.tsx`** — **`AST-1301: footer Cancel/Save use catalog classes`** (do **not** run **`AST-1302:`** close case on this tip — × stays `modal-close`) |
| ListPage bulk | `ListPage.tsx` + `App.css` | **`test_ListPage.test.tsx`** — Archive/Delete catalog classes; **`AST-1301: App.css retires leftover labeled families`** |
| Skip This Job | `JobDetailModal.tsx` | **`test_JobDetailModal.test.tsx`** — Skip is `btn secondary` |
| Generate in-flight (**AST-645** revised) | `ArtifactEditor.tsx`, `ArtifactsCompanySearchTerms.tsx`, `JobAnalysisReportModal.tsx` | idle `btn primary`; busy still `in-flight` — drop obsolete `toHaveClass("save")` |
| Manage Email toolbar (**§6c**) | `AdminManageEmail.tsx` | **`test_AdminManageEmail.test.tsx`** — Select all / Clear / Land Meteorite classes + existing Land gate/POST |
| Scheduled Actions (**§6c**) | `AdminScheduledActions.tsx` | **`test_AdminScheduledActions.test.tsx`** — **`AST-1301: labeled actions use catalog classes`** (do **not** run **`AST-1302:`** × case on this tip) |
| JobsSkipped Retry (**§6c**) | `JobsSkipped.tsx` | **`test_JobsSkipped.test.tsx`** — Retry is `btn primary` |
| Intake / Profile (**§6c**) | `CandidateIntake.tsx`, `CandidateProfile.tsx` | Continue `btn primary`; Save/Cancel catalog |
| Expand chrome / LogOff | `SectionExpandChrome.tsx`, `LogOffScreen.tsx` | Expand/Collapse `btn secondary`; Refresh `btn primary` |

**Existing coverage (bible-backed §6c page renders — handlers unchanged):** `test_AdminAgentPrompts.test.tsx`, `test_AdminAgentTimesheets.test.tsx`, `test_AdminAnthropicAdHoc.test.tsx`, `test_AdminCostReconciliation.test.tsx`, `test_AdminDataManagement.test.tsx`, `test_AdminManageCandidates.test.tsx`, `test_AdminManageSlack.test.tsx`, `test_AdminPerformanceMonitor.test.tsx`, `test_AdminScheduledQueries.test.tsx`, `test_AdminSessionCoverLetter.test.tsx`, `test_AdminSessionResumePaste.test.tsx`, `test_AdminTaskPrompts.test.tsx`, `test_CandidateSurfer.test.tsx`, `test_CandidateSurferConsent.test.tsx`, `test_CompaniesNewList.test.tsx`.

**Broken / obsolete (revised this pass):** `test_ArtifactEditor.test.tsx` AST-645 `toHaveClass("save")` → `btn` + `primary`. `[qa-handoff]` harness: AuthContext setter stubs; Agent Prompts GET `ok: true`; AST-634 top-level `first`; `JobDetailModal` already-skipped needs `/api/state_ui_manifest` (`STATE_UI_MANIFEST_FIXTURE`). After ftr/1302 merge-resume, glyph rows are `icon-control` — still do **not** run **`AST-1302:`** names on this ticket.

**Integration:** no existing scenario asserts labeled-button class catalogs — no drift. Do not invent integration coverage.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_Modal.test.tsx \
  ../../../tests/component/frontend/components/test_ListPage.test.tsx \
  ../../../tests/component/frontend/components/test_JobDetailModal.test.tsx \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  ../../../tests/component/frontend/components/test_SectionExpandChrome.test.tsx \
  ../../../tests/component/frontend/components/test_LogOffScreen.test.tsx \
  -t "AST-1301|AST-645|Skip This Job|filters, sorts|Expand all|timeout copy"

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminManageEmail.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminScheduledActions.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsSkipped.test.tsx \
  ../../../tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx \
  ../../../tests/component/frontend/pages/test_CandidateIntake.test.tsx \
  ../../../tests/component/frontend/pages/test_CandidateProfile.test.tsx \
  -t "AST-1301|AST-1142|AST-645|Retry|Continue resumes|pronoun"
```

---

### AST-1334 · AST-1329 (hide Recommended Job Report modal footer)

**Parent:** [AST-1329 — Remove Cancel/footer from Recommended Job Modal](https://linear.app/astralcareermatch/issue/AST-1329/remove-the-cancel-button-and-footer-from-the-recommended-job-modal). **Publish:** `origin/sub/AST-1329/AST-1334-remove-recommended-job-report-modal-footer`.

`Modal` gains optional `showFooter` (default `true`). `JobAnalysisReportModal` passes `showFooter={false}` so Summary / Analysis / Artifacts content is not covered by a footer Cancel strip. Header × dismiss and Artifacts-tab in-flight Cancel (`cancel_build`) stay. Other Modal call sites unchanged. No page-file product diff — §6c routed-page rule N/A.

| Area | Source | Component tests |
| --- | --- | --- |
| Shared Modal `showFooter` | `Modal.tsx` | **`test_Modal.test.tsx`** — **`AST-1334: showFooter false omits footer; header Close still closes`** (+ default footer regression via existing Cancel/Save cases) |
| Recommended Job Report shell | `JobAnalysisReportModal.tsx` | **`test_JobAnalysisReportModal.test.tsx`** — **`JobAnalysisReportModal — AST-1334 footer opt-out`** (no `.modal-footer` / no footer Cancel; header Close; BUILD_ARTIFACTS strip Cancel only) |

**Existing coverage (bible-backed):** AST-951 Artifacts Generating… + Cancel / `cancel_build` POST; AST-1301 footer catalog classes; AST-1302 header `icon-control`.

**Broken / obsolete:** none — default `showFooter=true` keeps prior Modal Cancel/Save asserts; JAR Artifacts Cancel cases already scope `within(strip)`.

**Integration:** no existing scenario asserts `.modal-footer` on Recommended Job Report — no drift. Do not invent integration coverage.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_Modal.test.tsx \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  -t "AST-1334|AST-1301|AST-1302|shows Generating|Cancel closes modal after cancel_build"
```

### AST-1348 · AST-1346

**Parent:** [AST-1346](https://linear.app/astralcareermatch/issue/AST-1346/add-rubric-score-to-analysis-header). **Publish:** `origin/sub/AST-1346/AST-1348-analysis-header-score-title-chrome`.

Analysis-tab section `nav_label` uses formatted score title when `jobScoreBreakdownForGradesField` returns a trio; plain `report_phase_tabs` label otherwise. No page-file product diff — §6c routed-page rule N/A (modal component). Helpers: **`docs/test-bible/frontend/lib.md`**. API derive: **`docs/test-bible/ui/api/api_jobs.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Analysis header score chrome | `JobAnalysisReportModal.tsx` | **`test_JobAnalysisReportModal.test.tsx`** — **`JobAnalysisReportModal — AST-1348 Analysis score title chrome`** |
| Fixture template | `stateUiManifestFixture.ts` | same + lib helpers |

**Broken / obsolete:** none — AST-950 cases stay on plain labels (mocks lack `*_score_breakdown`).

**Integration:** none.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  ../../../tests/component/frontend/lib/test_recommendedJobReport.test.tsx \
  -t "AST-1348|AST-950"
```

### AST-1350 · AST-1345

**AST-1350:** JAR **Print Resume** fetch-then-blob + toast exact API `error` (no `window.open` on failure). **AST-1489:** structure auto-persist before resume GET when candidate selected. Cover Letter print unchanged. Base Resume / Session Open HTML already toast API errors — **`test_ArtifactsBaseResumeContent`** / **`test_AdminSessionResumePaste`**. Core/API: **`docs/test-bible/core/builder.md`**.

**AST-1546 (gap · AST-1542):** Blob Print Resume opens with `window.open(url, "_blank")` then `opener = null` (no features string — AST-1545 product). Success must **not** toast `Popup blocked — allow popups to open the HTML tab.` Cover Letter URL open keeps `"noopener,noreferrer"`.

| Area | Source | Component tests |
| --- | --- | --- |
| Fetch-then-blob success + unsupported toast | `JobAnalysisReportModal.tsx` | **`test_JobAnalysisReportModal.test.tsx`** — **AST-1546: Print Resume success — two-arg open…** (bug-repro), **AST-1350: Print Resume unsupported toast — no tab** |
| Print without Save sections (bug-repro) | same | **`AST-1489:`** — structure PUT before resume GET (blob open two-arg) |

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  --testNamePattern="AST-1546|Print Resume|AST-1350"
```

### AST-1546 · AST-1542 (gap)

**Gap sibling of AST-1545.** Align four validate-then-blob success opens with AST-1545 shape (`window.open(url, "_blank")` + `opener = null`; no popup-blocked toast on success). Product UI is AST-1545 — this ticket is tests/bible only.

## QA test manifest

1. **Bug-repro (must flip red→green with AST-1545 product):** `test_JobAnalysisReportModal.test.tsx` — **`AST-1546: Print Resume success — two-arg open, opener null, no popup-blocked toast; Cover still noopener (AST-1350)`**
2. Base Print success: `test_ArtifactsBaseResumeContent.test.tsx` — **`AST-1337: … success opens blob tab`** (two-arg + opener null + no blocked toast)
3. Session Resume Open HTML success: `test_AdminSessionResumePaste.test.tsx`
4. Session Cover Open HTML success: `test_AdminSessionCoverLetter.test.tsx` — Open HTML posts fields…
5. JAR AST-1489 / AST-1490 Print Resume blob spies: two-arg open (Cover non-blob noopener unchanged)

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  ../../../tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminSessionResumePaste.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminSessionCoverLetter.test.tsx \
  --testNamePattern="AST-1546|AST-1337: Print disabled|Open HTML posts|Open HTML posts fields"
```

### AST-1351 · AST-1345

**Parent:** [AST-1345](https://linear.app/astralcareermatch/issue/AST-1345/clarify-candidate-data-artifacts-base-resume-experience-node). **Publish:** `origin/sub/AST-1345/AST-1351-experience-array-ui-render-print-parity`.

Base Resume / job structureMode experience uses **`ExperienceJobsEditor`** (job-array template) via **`ArtifactEditor`**. Legacy non-array → read-only + unsupported message; Save aborts with that toast. Config/API spine: **`docs/test-bible/utils/config.md`**, **`docs/test-bible/ui/api/api_system.md`**. Builder Style D: **`docs/test-bible/core/builder.md`**. Does **not** own prompts (AST-1349) or Print toast/no-tab (AST-1350).

| Area | Source | Component tests |
| --- | --- | --- |
| Per-role add/remove/reorder | `ExperienceJobsEditor.tsx` | **`test_ExperienceJobsEditor.test.tsx`** — AST-1351 |
| Array load/Save + legacy abort | `ArtifactEditor.tsx` | **`test_ArtifactEditor.test.tsx`** — **AST-996/AST-1351**, **AST-1351: legacy string…** |

**Broken / obsolete this pass:** AST-996 experience pretty-printed JSON textarea asserts — flipped to ExperienceJobsEditor / unsupported notice.

**§6c:** Base Resume Content mounts ArtifactEditor — no separate page file in product diff; component coverage above is the UI gate.

## QA test manifest

1. ExperienceJobsEditor add/remove/reorder: `tests/component/frontend/components/test_ExperienceJobsEditor.test.tsx`
2. ArtifactEditor array Save + legacy abort: `test_ArtifactEditor.test.tsx` AST-996/AST-1351 + AST-1351 legacy
3. Config field spine: `TestAst1351ExperienceJobUiFields`
4. ui_config exposure: `TestAst1351ExperienceJobUiConfig`
5. Builder Style D debug jobs: `TestAst1351ExperienceDebugJobs`

**AST-1351** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1351ExperienceJobUiFields \
  tests/component/ui/api/test_api_system.py::TestAst1351ExperienceJobUiConfig \
  tests/component/core/test_builder.py::TestAst1351ExperienceDebugJobs \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_ExperienceJobsEditor.test.tsx \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  --testNamePattern="AST-1351|AST-996"
```

### AST-1382 · AST-1362 (gap — board-betty REVISE)

**Parent:** [AST-1362 — Base Resume Issues](https://linear.app/astralcareermatch/issue/AST-1362/base-resume-issues). **Publish:** `origin/sub/AST-1362/AST-1382-gap-base-resume-tests`. Product sibling: **AST-1381**.

Retarget AST-1351/996 fixtures: job `accomplishments` is **`string[]`**; collapsible role header is `{company}, {title} / {dates}` (not `Role N`). **[bug-repro]** content Save with structure authoring bundles `artifacts.resume_structure` (e.g. `prior_experience.format = free_prose`). Emit / `|`→`•` repros: **`docs/test-bible/core/builder.md`** § AST-1382. Schema/sample spine: **`docs/test-bible/core/candidate.md`**, **`docs/test-bible/utils/config.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| string[] + collapsible header | `ExperienceJobsEditor.tsx` | **`test_ExperienceJobsEditor.test.tsx`** — AST-1351/1382 |
| Array Save + header + structure Save [bug-repro] | `ArtifactEditor.tsx` | **`test_ArtifactEditor.test.tsx`** — AST-996/1351/1375 revised; **`AST-1382 [bug-repro]: content autosave bundles resume_structure…`** (AST-2056 retarget) |

**Broken / obsolete this pass:** Role N / `accomplishments: str` asserts under AST-1351/996/1375 — retargeted.

## QA test manifest

1. ExperienceJobsEditor string[] + header: `tests/component/frontend/components/test_ExperienceJobsEditor.test.tsx`
2. ArtifactEditor retarget + structure Save repro: `test_ArtifactEditor.test.tsx` — `AST-1351|AST-996|AST-1375|AST-1382`
3. Builder [bug-repro] emit/markers/format: `TestAst1382BugReproBaseResumeIssues` (primary: **`docs/test-bible/core/builder.md`**)
4. Candidate/config fixture retarget: `TestAst1349ExperienceArrayContract` + `TestAst996ExperienceJobArrayConfig`

```bash
cd src/ui/frontend && ./node_modules/.bin/vitest run \
  ../../../tests/component/frontend/components/test_ExperienceJobsEditor.test.tsx \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  --testNamePattern="AST-1351|AST-996|AST-1375|AST-1382"
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_builder.py::TestAst1382BugReproBaseResumeIssues \
  tests/component/core/test_candidate.py::TestAst1349ExperienceArrayContract \
  tests/component/utils/test_config.py::TestAst996ExperienceJobArrayConfig \
  -q
```

### AST-1375 · AST-1371

**Parent:** [AST-1371 — Regenerate resume button does not appear for resumes with unsupported content](https://linear.app/astralcareermatch/issue/AST-1371/regenerate-resume-button-does-not-appear-for-resumes-with-unsupported). **Publish:** `origin/sub/AST-1371/AST-1375-regenerate-affordance-unsupported-experience`.

Base Resume Content (`artifactKey === "base_resume"`, not `jobPersistence`): when experience parse fails (same failure as the unsupported notice), `canGenerate` is true unless candidate state is in config-owned `artifact_generate_inflight_hide_states` (`REQUESTED_ARTIFACTS` / `REQUESTED_ARTIFACTS_RETRY`). Click still confirms-when-regenerating and POSTs `craft_resume_base`. Valid job-array experience stays allowlist-only. Config/API spine: **`docs/test-bible/utils/config.md`**, **`docs/test-bible/ui/api/api_system.md`**. Does **not** reopen Print/no-emit or migrate legacy experience.

| Area | Source | Component tests |
| --- | --- | --- |
| Escape hatch + inflight hide + craft path | `ArtifactEditor.tsx` | **`test_ArtifactEditor.test.tsx`** — **`AST-1375:*`** |
| Fixture hide list | `stateUiManifestFixture.ts` | same (fixture feeds all ArtifactEditor mounts) |

**Broken / obsolete:** none — additive escape hatch; AST-1351 legacy notice + Save abort unchanged. Fixture gains `artifact_generate_inflight_hide_states`.

**§6c:** no page-file product diff — ArtifactEditor is the UI gate (same as AST-1351).

**Integration:** no existing scenario asserts Generate visibility vs unsupported experience — no revision.

## QA test manifest

1. Inflight hide membership + generate allowlist unchanged: `tests/component/utils/test_config.py::TestAst1375ArtifactGenerateInflightHideStates`
2. Manifest key on `GET /api/state_ui_manifest`: `tests/component/ui/api/test_api_system.py::TestAst1375InflightHideStatesManifest`
3. ArtifactEditor escape / hide / craft / allowlist-only: `tests/component/frontend/components/test_ArtifactEditor.test.tsx` — `--testNamePattern="AST-1375"`

**AST-1375** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1375ArtifactGenerateInflightHideStates \
  tests/component/ui/api/test_api_system.py::TestAst1375InflightHideStatesManifest \
  -q
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  --testNamePattern="AST-1375"
```

**Pass criterion:** pytest + Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-1421 · AST-1419

**Parent:** [AST-1419 — Create a Copy button on the Job Modal](https://linear.app/astralcareermatch/issue/AST-1419/create-a-copy-button-on-the-job-modal). **Publish:** `origin/sub/AST-1419/AST-1421-job-modal-copy-control`.

Labeled **Copy** (`btn secondary`) on Job Detail Info (above Skip) and Recommended Job Report header. Click fetches AST-1420 snapshot via `copyJobSnapshotToClipboard`, writes pretty-printed JSON, shows **Copied** 2000ms. Silent on helper `false`. Email / LinkedIn / Skip unchanged. Helper: **`docs/test-bible/frontend/lib.md`**. No page-file product diff — §6c routed-page rule N/A.

| Area | Source | Component tests |
| --- | --- | --- |
| Job Detail Copy | `JobDetailModal.tsx` | **`test_JobDetailModal.test.tsx`** — **`JobDetailModal — AST-1421 snapshot Copy`** (+ existing Skip) |
| Recommended header Copy | `RecommendedJobReportHeader.tsx` | **`test_RecommendedJobReportHeader.test.tsx`** — **`RecommendedJobReportHeader — AST-1421 snapshot Copy`** |
| JAR wiring | `JobAnalysisReportModal.tsx` | **`test_JobAnalysisReportModal.test.tsx`** — **`JobAnalysisReportModal — AST-1421 snapshot Copy`** |

**Broken / obsolete:** none — additive control; existing Skip / Copy Application Email / Copy LinkedIn asserts still hold.

**Integration:** no existing jobs-modal scenario — no revision.

## QA test manifest

1. Clipboard helper: `tests/component/frontend/lib/test_copyJobSnapshot.test.ts`
2. Job Detail Copy ↔ Copied + Skip unchanged: `test_JobDetailModal.test.tsx` — `AST-1421|loads job details`
3. Header Copy without email/linkedin + coexistence: `test_RecommendedJobReportHeader.test.tsx`
4. JAR click wiring, no `copyFeedback` span: `test_JobAnalysisReportModal.test.tsx` — `AST-1421`

**AST-1421** narrowed run (Vitest — from `src/ui/frontend/`):

```bash
npx tsc -b --noEmit
npm run test:component -- \
  ../../../tests/component/frontend/lib/test_copyJobSnapshot.test.ts \
  ../../../tests/component/frontend/components/test_JobDetailModal.test.tsx \
  ../../../tests/component/frontend/components/test_RecommendedJobReportHeader.test.tsx \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  --testNamePattern="AST-1421|loads job details|sticky header"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-1450 · AST-1444

**Parent:** [AST-1444 — Remove navigation filter for selected candidate](https://linear.app/astralcareermatch/issue/AST-1444/remove-navigation-filter-for-selected-candidate). **Publish:** `origin/sub/AST-1444/AST-1450-show-selected-candidate-state-under-picker`.

Pinned chrome shows the selected candidate’s stored `state` string as a read-only `.sidebar-candidate-state` line under the wide `<select>` and under the narrow picker toggle. Exact stored name (including retry/error companions); omit when blank or when the candidate list is empty. No nav gating, no state editor, no display aliases. No page-file product diff — §6c routed-page rule N/A.

| Area | Source | Component tests |
| --- | --- | --- |
| Wide: line under select; exact string; not editable; updates on picker change | `NavigationShell.tsx` + `App.css` | **`test_NavigationShell.test.tsx`** — **`AST-1450 selected candidate state under picker` → wide: read-only stored state sits under the select and updates on change** |
| Omit blank stored state | same | **`wide: omits the line when stored state is blank`** |
| Narrow: same line under toggle (stays under it when menu open); updates on select | same | **`narrow: same read-only line under the toggle; stays under it when the menu opens`** |
| Empty list | same | **`empty candidate list omits the state line`** |
| Chrome / responsive regression | same | **`AST-1369 pinned left-nav chrome`** + **`AST-1286 responsive shell`** (existing) |

**Broken / obsolete:** shared `candidatesFixture` in `test_NavigationShell.test.tsx` — `c2.state` is `REQUESTED_RESUME_RETRY` so picker-change can assert a different stored name; existing cases do not assert state text.

**Integration:** `tests/integration/scenarios/test_candidate_nav_api.py` — API/nav membership only; this child does not change `NAV_CONFIG` or `/api/candidates`. No revision. Do not invent new integration coverage.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_NavigationShell.test.tsx
```

**Pass criterion:** Vitest green on the NavigationShell file (AST-1450 + existing shell cases) — not zero-arg harness / branch-lock gate.

---

---

### AST-1477 · AST-1464

**Parent:** [AST-1464 — Add means to mark job as applied for](https://linear.app/astralcareermatch/issue/AST-1464). **Publish:** `origin/sub/AST-1464/AST-1477-mark-applied-from-recommended-list`.

Recommended list rows in legal `CANDIDATE_APPLIED` priors (`RECOMMENDED` / `BUILD_ARTIFACTS` / `CANDIDATE_REVIEW`) show an Applied `icon-control` (`A`) that calls `onAction("applied")`. Notes modal + `POST …/candidate_action` + list refresh already wired on `JobsRecommended` via `useCandidateJobActions`. `PASSED_LIKE` stays Skip-only (not a prior). Report Applied/Skip and Applied list home are siblings.

| Area | Source | Component tests |
| --- | --- | --- |
| Applied icon on legal priors; hide on `PASSED_LIKE` / no `onAction` | `CandidateJobRowActions.tsx` | **`test_CandidateJobRowActions.test.tsx`** — **`CandidateJobRowActions — AST-1477 Applied mark`** |
| Routed Recommended mark-applied (**§6c**) | `JobsRecommended.tsx` | **`test_JobsRecommended.test.tsx`** — **`AST-1477 mark applied from Recommended`** (icon present; notes → `candidate_action` applied → row gone; 409 toast) |

**Broken / obsolete:** none — additive Applied control; existing Skip / AST-1302 / AST-1410 asserts still hold.

**Integration:** no existing scenario asserts Recommended list Applied mark — no revision. Do not invent new integration coverage.

## QA test manifest

1. Row Applied icon-control: `tests/component/frontend/components/test_CandidateJobRowActions.test.tsx` — `--testNamePattern="AST-1477"`
2. Recommended list Applied path (**§6c**): `tests/component/frontend/pages/test_JobsRecommended.test.tsx` — `--testNamePattern="AST-1477"`
3. Regression (same files): **AST-1302** icon-control + **AST-1410** silent Skip refetch — do **not** use bare `Skip` in the Vitest pattern (it also matches sibling **AST-1478** report Skip/Applied cases in the same page file)

**AST-1477** narrowed run (Vitest — from `src/ui/frontend/`):

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_CandidateJobRowActions.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx \
  --testNamePattern="AST-1477|AST-1302|AST-1410"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

---

---

### AST-1478 · AST-1464

**Parent:** [AST-1464 — Add means to mark job as applied for](https://linear.app/astralcareermatch/issue/AST-1464). **Publish:** `origin/sub/AST-1464/AST-1478-report-applied-and-skip`.

Job Analysis Report gains labeled **Skip** (`.btn.secondary`) and **Applied** (`.btn.primary`) when parent passes `onSkip` / `onRequestApplied`. No parallel POSTs in the modal — Recommended wires shared `skipJob` / `requestAction(..., "applied")`. CLIENT job-link **Apply** stays absent. Page close-when-job-leaves-list: **`docs/test-bible/frontend/pages.md`** § AST-1478.

| Area | Source | Component tests |
| --- | --- | --- |
| Callback strip; omit when no callbacks; no `window.open` / **Apply** | `JobAnalysisReportModal.tsx` | **`test_JobAnalysisReportModal.test.tsx`** — **`JobAnalysisReportModal — AST-1478 Applied and Skip`** |

**Broken / obsolete:** none — additive strip; AST-948 sticky-header **no Apply** (exact name) still holds. List-row Applied is sibling **AST-1477**.

**Integration:** no existing scenario asserts report Applied/Skip — no revision. Do not invent new integration coverage.

## QA test manifest

1. JAR labeled Skip/Applied + callback / no job_link: `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` — `--testNamePattern="AST-1478"`
2. Recommended page wiring (**§6c**): `tests/component/frontend/pages/test_JobsRecommended.test.tsx` — `--testNamePattern="AST-1478"` (see **pages.md**)
3. Regression: sticky header / open-report / AST-1410 Skip in the same files

**AST-1478** narrowed run (Vitest — from `src/ui/frontend/`):

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx \
  --testNamePattern="AST-1478|sticky header|opens the report|AST-1410"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.


### AST-1454 · AST-1446

**AST-1975:** `JobsInReview.tsx` became `JobsProcessing.tsx` and `test_JobsInReview.test.tsx` was renamed `test_JobsProcessing.test.tsx` (`view=processing`). Paths below that name `test_JobsInReview.test.tsx` now mean `test_JobsProcessing.test.tsx`.

**Parent:** [AST-1446 — When a job is in a Skipped state, make all fields editable](https://linear.app/astralcareermatch/issue/AST-1446/when-a-job-is-in-a-skipped-state-make-all-fields-editable). **Publish:** `origin/sub/AST-1446/AST-1454-job-detail-skipped-field-editors`.

When GET `fields_editable` is true: Info title/link inputs, state `<select>` from `legal_next_states` (+ No change), always-on Job Description textarea (empty JD ok), Modal Save → `PUT /api/jobs/<id>` + `onRefresh`. Non-editable stays display-only (no Save / no empty JD tab). Copy / Skip This Job unchanged. Persist: **AST-1453** / **`docs/test-bible/ui/api/api_jobs.md`**. Page `onRefresh={load}`: **`docs/test-bible/frontend/pages.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Editors + Save + empty JD + locked | `JobDetailModal.tsx` | **`test_JobDetailModal.test.tsx`** — **`JobDetailModal — AST-1454 skipped-field editors`** |

**Broken / obsolete:** none — additive; AST-1421 Copy + Skip suites still hold.

**Integration:** none.

## QA test manifest

1. Job Detail editors / Save / locked / 409: `tests/component/frontend/components/test_JobDetailModal.test.tsx` — pattern **`AST-1454`**
2. Routed Skipped + In Review `onRefresh` after Save (**§6c**): `test_JobsSkipped.test.tsx` + `test_JobsInReview.test.tsx` — **`AST-1454`**

```bash
cd src/ui/frontend && npx vitest run \
  ../../../tests/component/frontend/components/test_JobDetailModal.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsSkipped.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsInReview.test.tsx \
  --testNamePattern="AST-1454|loads job details|AST-1421"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-1476 · AST-1462

**Parent:** [AST-1462 — Create and position page break](https://linear.app/astralcareermatch/issue/AST-1462/create-and-position-page-break). **Publish:** `origin/sub/AST-1462/AST-1476-structure-editor-page-break-dropdown-base-and-job`.

Catalog-driven page-break `<select>` on structure authoring headers (`aria-label="Page break"`); content Save and **Save sections** always include `page_break_policy`. Base page Save sections: **`docs/test-bible/frontend/pages.md`** § AST-1476. Schema/print: **AST-1474** / **AST-1475**.

| Area | Source | Component tests |
| --- | --- | --- |
| Dropdown + content Save + Save sections | `ArtifactEditor.tsx` | **`test_ArtifactEditor.test.tsx`** — **`AST-1476:`**; revised **AST-1382** fixture (catalog/rows carry policy) |
| JAR Job Resume Save sections → candidate | `JobAnalysisReportModal.tsx` | **`test_JobAnalysisReportModal.test.tsx`** — **`AST-1476:`** |

**Broken / obsolete this pass:** AST-1382 structure fixture lacked `page_break_*` catalog/row fields — extended so content Save still bundles structure (now with policy).

**Integration:** none — do not invent new integration coverage.

## QA test manifest

1. ArtifactEditor dropdown + Saves: `tests/component/frontend/components/test_ArtifactEditor.test.tsx` — `--testNamePattern="AST-1476"`
2. JAR structure Save: `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` — `--testNamePattern="AST-1476"`
3. Base Resume Content (**§6c**): `tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx` — `--testNamePattern="AST-1476|AST-1306"`
4. Regression: AST-1382 structure Save still bundles format: same ArtifactEditor file — `--testNamePattern="AST-1382"`

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  ../../../tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx \
  --testNamePattern="AST-1476|AST-1382|AST-1306"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-1480 · AST-1459

**Parent:** [AST-1459 — Resume editor is not working properly](https://linear.app/astralcareermatch/issue/AST-1459/resume-editor-is-not-working-properly). **Publish:** `origin/sub/AST-1459/AST-1480-restore-structure-mode-resume-section-body-edit-loop`.

Restores structure-mode section **body** load → edit → Save on shared `ArtifactEditor` (Base Resume Content + JAR Job Resume). Product: chrome vs body editability split (`tabChromeEditable` / `bodiesEditable` — rubric free-form + structure/shapes/job fixed tabs; never during Generate review), stable `fixedFieldKeys` so label-only structure header churn does not re-GET / wipe tabs, dict coerce rejects pin strings, `job_resume` GET overlays empty/pin with `resume_content` sibling. Stage 2 skipped (ArtifactEditor-only) — §6c routed-page rule N/A.

| Area | Source | Component tests |
| --- | --- | --- |
| Label-churn keeps body + Save | `ArtifactEditor.tsx` | **`test_ArtifactEditor.test.tsx`** — **`AST-1480: structure title rename keeps hydrated body and autosave still works`** (AST-2056 retarget) |
| JAR `job_resume` overlay | same | **`AST-1480: job_resume pin overlays resume_content sibling bodies`** |
| bodiesEditable / chrome off | same | **`AST-1480: structure mode bodies stay editable; tab chrome stays off`** |
| Rubric free-form body edit PUT | same | **`AST-1480: rubric free-form body edit PUTs edited content`** (Radia fix-now / resolve) |
| Regression structure + jobPersistence | same | existing structureSections load; **AST-553** job `resume_content` Save; **AST-1410** Cancel |

**Broken / obsolete this pass:** none — additive repro coverage for failure modes (A)/(B) from Code Complete; queue-C return adds rubric `bodiesEditable` lock after resolve.

**Integration:** none — frontend-only; do not invent new integration coverage.

## QA test manifest

1. ArtifactEditor AST-1480 repro + chrome/body + rubric free-form: `tests/component/frontend/components/test_ArtifactEditor.test.tsx` — `--testNamePattern="AST-1480"`
2. Regression structure hydrate + job Save + Cancel: same file — `--testNamePattern="job persistence mode loads|AST-1410"`

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  --testNamePattern="AST-1480|job persistence mode loads|AST-1410"
```

---

### AST-1490 · AST-1483 (bug — Print contact-only after section reorder)

**Parent:** [AST-1483 — Resume page break settings don't work](https://linear.app/astralcareermatch/issue/AST-1483/resume-page-break-settings-dont-work). **Publish:** `origin/sub/AST-1483/AST-1490-print-resume-only-contact-after-section-reorder`. Order-insensitive `fixedFieldKeys` + tab reorder without spurious candidate/job re-GET; Print after Up/Down must emit full body (AST-1489 auto-persist unchanged).

| Area | Source | Component tests |
| --- | --- | --- |
| Reorder no re-GET guard | `ArtifactEditor.tsx` | **`test_ArtifactEditor.test.tsx`** — **`AST-1490: structure reorder does not re-GET candidate artifact`** |
| Base reorder + Print full body (bug-repro) | `ArtifactsBaseResumeContent.tsx` | **`test_ArtifactsBaseResumeContent.test.tsx`** — **`AST-1490:`** |
| JAR reorder + Print full body (bug-repro) | `JobAnalysisReportModal.tsx` | **`test_JobAnalysisReportModal.test.tsx`** — **`AST-1490:`** |
| AST-1480 label-churn regression | `ArtifactEditor.tsx` | **`AST-1480: structure title rename keeps hydrated body and Save still works`** |

**Broken / obsolete this pass:** none — additive repro; AST-1480 rename guard must stay green after sorted-key signature.

**Integration:** none — do not invent new integration coverage.

## QA test manifest

1. Reorder no re-GET (bug-repro): `tests/component/frontend/components/test_ArtifactEditor.test.tsx` — `--testNamePattern="AST-1490: structure reorder"`
2. Base reorder + Print: `tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx` — `--testNamePattern="AST-1490"`
3. JAR reorder + Print: `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` — `--testNamePattern="AST-1490"`
4. AST-1480 label-churn regression: `tests/component/frontend/components/test_ArtifactEditor.test.tsx` — `--testNamePattern="AST-1480: structure title rename"`

**AST-1490** narrowed run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  ../../../tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  --testNamePattern="AST-1490|AST-1480: structure title rename"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.


### AST-1551 · AST-1541

**Parent:** [AST-1541](https://linear.app/astralcareermatch/issue/AST-1541/add-discussion-tab-to-recommended-job-modal). **Publish:** `origin/sub/AST-1541/AST-1551-discussion-pane-recommended-job-report`. **Gap revise:** **AST-1612** — product pane filter on **AST-1609**.

`JobDiscussionPane` — RESPONSE-only stack via `ReportSectionList` / `entity-story-content` (JSON pretty-print / raw text). Pane filters to sections with non-empty RESPONSE; empty `agentStory` → **0** headers (no always-on empty hop panels). `JobAnalysisReportModal` wires Discussion from `report_discussion_sections` + `agent_story` (no hardcode); header count follows the filtered pane, not raw catalog length. Fixture catalog keys lockstep with **AST-1550** `TestAst1550ReportDiscussionSections._NINE` (+ optional `anticipate_scan` when covering unique-parent). Config/manifest/`task_name`: sibling **AST-1550**. No page-file product diff — §6c routed-page rule N/A.

| Area | Source | Component tests |
| --- | --- | --- |
| Pane RESPONSE-only / formatting / empty-story filter | `JobDiscussionPane.tsx` | **`test_JobDiscussionPane.test.tsx`** — **`JobDiscussionPane — AST-1551`** |
| Modal Discussion tab + RESPONSE-only headers | `JobAnalysisReportModal.tsx` | **`test_JobAnalysisReportModal.test.tsx`** — **`JobAnalysisReportModal — AST-1551 Discussion tab`**; revised AST-948 top-tab assert |
| Manifest fixture Discussion | `stateUiManifestFixture.ts` | consumed by JAR / pane tests |

**Broken / obsolete:** AST-948 three-tab shell assert — Discussion added; tip Toast tests realigned to `origin/dev` (product already has AST-1549 dismiss). Pre-AST-1609 “nine collapsed empty panels” / “empty hops stay panels” asserts — revised (AST-1612). Empty-RESPONSE product gap (first blank RESPONSE hid later body) — shipped; coverage kept.

**Integration:** none — do not invent.

## QA test manifest

1. Pane: `tests/component/frontend/components/test_JobDiscussionPane.test.tsx`
2. Modal Discussion: `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` — `--testNamePattern="AST-1551|AST-948 horizontal shell"`
3. Toast align (product on tip): `tests/component/frontend/components/test_Toast.test.tsx`

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobDiscussionPane.test.tsx \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  ../../../tests/component/frontend/components/test_Toast.test.tsx \
  --testNamePattern="AST-1551|AST-948 horizontal shell|Toast"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-1612 · AST-1607

**Parent:** [AST-1607](https://linear.app/astralcareermatch/issue/AST-1607/artifacts-discussion-is-incomplete). **Publish:** `origin/sub/AST-1607/AST-1612-gap-revise-discussion-tests`. Product: **AST-1609**.

Test-gap: empty `agentStory` → 0 Discussion headers; `anticipate_scan` header when sections + story have RESPONSE; JAR partial story → header count = hops with RESPONSE (not catalog length). Hop-walk pytest: **`docs/test-bible/utils/config.md`** § AST-1612.

| Area | Source | Component tests |
| --- | --- | --- |
| Empty story / anticipate_scan RESPONSE | `JobDiscussionPane.tsx` | **`test_JobDiscussionPane.test.tsx`** — hides all headers; shows anticipate_scan when RESPONSE |
| JAR empty / partial story | `JobAnalysisReportModal.tsx` | **`test_JobAnalysisReportModal.test.tsx`** — AST-1551 Discussion tab (0 / 1 Expand) |

**Broken / obsolete:** nine Expand buttons with empty/partial story.

**Integration:** none.

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobDiscussionPane.test.tsx \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  --testNamePattern="AST-1551|hides all headers|anticipate_scan"
```

**Pass criterion:** Vitest green against AST-1609 product; red on pre-filter pane (always-nine headers).

---

### AST-1692 · AST-1685

**Parent:** [AST-1685](https://linear.app/astralcareermatch/issue/AST-1685/view-related-meteorite-record-data-on-recommended-job-modal). **Publish:** `origin/sub/AST-1685/AST-1692-meteorite-pane-recommended-modal`.

`JobMeteoritePane` — read-only staging-row sections via `ReportSectionList` from `report_meteorite_sections` (timestamps / http(s)-gated link / AI `classify_outcome`+content / provenance). `JobAnalysisReportModal` filters Meteorite top tab when `related_meteorite` is null; does not hardcode tab label/order. Manifest/API shapes: sibling **AST-1691**. No page-file product diff — §6c routed-page rule N/A.

| Area | Source | Component tests |
| --- | --- | --- |
| Pane timestamps / link / AI / provenance | `JobMeteoritePane.tsx` | **`test_JobMeteoritePane.test.tsx`** — **`JobMeteoritePane — AST-1692`** |
| Modal Meteorite tab filter + render | `JobAnalysisReportModal.tsx` | **`test_JobAnalysisReportModal.test.tsx`** — **`JobAnalysisReportModal — AST-1692 Meteorite tab`**; revised AST-1551 null-filter assert |
| Manifest fixture Meteorite | `stateUiManifestFixture.ts` | consumed by JAR / pane tests |

**Broken / obsolete:** AST-1551 “Discussion is last top tab” wording — Meteorite is last in fixture/`report_top_tabs` but filtered out when `related_meteorite` null (gazed jobs keep four tabs).

**Integration:** none — do not invent.

## QA test manifest

1. `tests/component/frontend/components/test_JobMeteoritePane.test.tsx`
2. `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` — `--testNamePattern="AST-1692|AST-1551 Discussion"`
3. Fixture: `tests/component/frontend/fixtures/stateUiManifestFixture.ts` (`report_meteorite_sections` + Meteorite top tab)

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobMeteoritePane.test.tsx \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  --testNamePattern="AST-1692|AST-1551 Discussion|AST-948 horizontal shell"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-1695 · AST-1686

**Parent:** [AST-1686](https://linear.app/astralcareermatch/issue/AST-1686/hyperlink-to-job-with-meteorite-http-link). **Publish:** `origin/sub/AST-1686/AST-1695-job-ui-listing-href`.

Recommended report title + CLIENT Apply path, and Job Detail listing control, navigate via AST-1694 `listing_href` (http(s) only). Raw `job_link` is not a fallback for `<a>` / `window.open`. Apply remains filtered from Artifacts strip (`artifactsTabPrimaryActions`); navigable surface is the title link. API writers: siblings **AST-1694** / **AST-1693**. No page-file product diff — §6c routed-page rule N/A.

| Area | Source | Component tests |
| --- | --- | --- |
| Title from `listing_href` | `JobAnalysisReportModal.tsx`, `RecommendedJobReportHeader.tsx` | **`JobAnalysisReportModal — AST-1695 listing_href title`**; **`RecommendedJobReportHeader — AST-1695 listing title`**; revised AST-948 sticky/deeplink fixtures (`listing_href` on job GET mock) |
| Job Detail Link / Open listing | `JobDetailModal.tsx` | **`JobDetailModal — AST-1695 listing_href`** |

**Broken / obsolete this pass:** AST-948 “job title deeplink replaces Apply” asserted `job_link` as title href — revised to `listing_href` (Apply still absent from Artifacts).

**Integration:** none — do not invent.

## QA test manifest

1. `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` — `--testNamePattern="AST-1695|job title deeplink|sticky header: deeplinked"`
2. `tests/component/frontend/components/test_RecommendedJobReportHeader.test.tsx` — `--testNamePattern="AST-1695"`
3. `tests/component/frontend/components/test_JobDetailModal.test.tsx` — `--testNamePattern="AST-1695"`

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  ../../../tests/component/frontend/components/test_RecommendedJobReportHeader.test.tsx \
  ../../../tests/component/frontend/components/test_JobDetailModal.test.tsx \
  --testNamePattern="AST-1695|job title deeplink|sticky header: deeplinked"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

---

### AST-1577 · AST-1569

**Publish:** `origin/sub/AST-1569/AST-1577-ui-consistency-base-resume-editor`.

`bodyShape === "resume_content"` is structure-dict mode (JAR keeps `useCandidateResumeStructure`). Primary: **`docs/test-bible/frontend/pages.md`** § AST-1577.

| Area | Source | Component tests |
| --- | --- | --- |
| bodyShape without legacy prop | `ArtifactEditor.tsx` | **`test_ArtifactEditor.test.tsx`** — **`AST-1577:`** |
| JAR / legacy structure still holds | same | **`loads fixed tabs from structureSections without shapes fetch`** |

**Broken / obsolete:** none.

**Integration:** none.

---

### AST-1585 · AST-1571

**Publish:** `origin/sub/AST-1571/AST-1585-ui-contact-pilot-base-resume-operative-resolve`.

JAR Artifacts pane **Source base resume** block: gap when no `job_data.base_resume_artifact_id`; fetch via operative API when pin present; error class on fail; never candidate detail blob for this panel. Helpers: **`docs/test-bible/frontend/lib.md`** § AST-1585. §6c routed-page N/A (component only).

| Area | Source | Component tests |
| --- | --- | --- |
| Source base resume panel | `JobAnalysisReportModal.tsx` | **obsolete AST-1599** — panel removed; see § AST-1599 |

**Broken / obsolete under AST-1599:** JAR Source base resume Vitest describe removed; Contact + operative API coverage below stays.

**Integration:** none.

## QA test manifest (AST-1585)

1. Contact resolve/dispatch/raft: `tests/component/core/test_contact.py::TestAst1585ContactPinnedBaseResume`
2. Operative GET API: `tests/component/ui/api/test_api_candidate.py::TestAst1585OperativeBaseResumeApi`
3. Contact + operative API only (JAR panel / lib helpers retired under **AST-1599**)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_contact.py::TestAst1585ContactPinnedBaseResume \
  tests/component/ui/api/test_api_candidate.py::TestAst1585OperativeBaseResumeApi \
  -q
```

**Pass criterion:** pytest green on lines 1–2 — not zero-arg harness / branch-lock gate.

---

### AST-1593 · AST-1588

**Publish:** `origin/sub/AST-1588/AST-1593-inventory-rewire-job-artifact-consumers`.

ArtifactEditor job-mode load trusts hydrated leaf `job_resume` / `cover_letter`; does not promote `resume_content` sibling as SoT. Save still PUTs leaf URL. Builder: **`docs/test-bible/core/builder.md`** § AST-1593.

| Area | Source | Component tests |
| --- | --- | --- |
| No resume_content fallback | `ArtifactEditor.tsx` | **`AST-1593: empty job_resume leaf does not fall back…`** |
| Hydrated leaf load + save | same | **`AST-1593: job_resume load uses hydrated current leaf body`** |

**Broken / obsolete this pass:** `AST-1480: job_resume pin overlays resume_content sibling bodies`.

---

### AST-1599 · AST-1588 (bug)

**Publish:** `origin/sub/AST-1588/AST-1599-job-modal-hides-resume-cover`.

Remove JAR Artifacts **Source base resume** provenance panel (and related fetch/state). Artifacts tab after finished build shows job_resume / cover_letter editors (or Generate when empty) — never pin-gap / operative JSON. [bug-repro] must flip red→green under `test-fix`.

| Area | Source | Component tests |
| --- | --- | --- |
| No Source base resume on populated Artifacts | `JobAnalysisReportModal.tsx` | **`[bug-repro]`** `JobAnalysisReportModal — AST-1599` · populated |
| No Source base resume on empty Generate | same | **`[bug-repro]`** · empty Generate |

**Broken / obsolete this pass:** `JobAnalysisReportModal — AST-1585 Source base resume` (deleted); lib `AST-1585 operative base_resume helpers` (deleted — exports removed with panel). Contact/API AST-1585 stays.

**Integration:** none.

## QA test manifest (AST-1599)

1. **[bug-repro]** `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` — `--testNamePattern="AST-1599"`

```bash
cd src/ui/frontend && npx vitest run \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  --testNamePattern="AST-1599"
```

**Pass criterion (test-fix):** [bug-repro] flips red→green after make-fix removes the panel — not zero-arg harness / branch-lock gate.

---

### AST-1696 · AST-1687

**Parent:** [AST-1687 — Copy single page access link from recommended job modal](https://linear.app/astralcareermatch/issue/AST-1687/copy-single-page-access-link-from-recommended-job-modal). **Publish:** `origin/sub/AST-1687/AST-1696-copy-detail-deeplink-from-report-header`.

Labeled **Copy Link** (`.btn secondary`) on Recommended Job Report header. Click writes absolute `origin + /jobs/detail/<jobId>` via `navigator.clipboard.writeText`, shows **Copied** ~2s (same feedback pattern as diagnostic Copy — not the email/LinkedIn `copyFeedback` span). Diagnostic Copy / email / LinkedIn / print unchanged. Deeplink host (`JobsJobDetail`) untouched — AC3 relies on existing AST-1463/AST-1481. No page-file product diff — §6c routed-page rule N/A.

| Area | Source | Component tests |
| --- | --- | --- |
| Header Copy Link alone + Copied prop + coexistence | `RecommendedJobReportHeader.tsx` | **`test_RecommendedJobReportHeader.test.tsx`** — **`RecommendedJobReportHeader — AST-1696 Copy Link`** |
| JAR absolute URL clipboard + idle restore; other header actions | `JobAnalysisReportModal.tsx` | **`test_JobAnalysisReportModal.test.tsx`** — **`JobAnalysisReportModal — AST-1696 Copy Link`** |

**Broken / obsolete:** none — additive control; existing AST-1421 snapshot Copy / email / LinkedIn asserts still hold.

**Integration:** no existing jobs-modal clipboard scenario — no revision. Do not invent new integration coverage.

## QA test manifest

1. Header Copy Link alone + coexistence + Copied prop: `tests/component/frontend/components/test_RecommendedJobReportHeader.test.tsx` — `AST-1696`
2. JAR absolute `/jobs/detail/<id>` clipboard + Copied→idle; diagnostic/email/LinkedIn stay: `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` — `AST-1696`
3. Regression (coexistence): same files — `AST-1421` (header + JAR snapshot Copy)

**AST-1696** narrowed run (Vitest — from `src/ui/frontend/`):

```bash
npx tsc -b --noEmit
npm run test:component -- \
  ../../../tests/component/frontend/components/test_RecommendedJobReportHeader.test.tsx \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  --testNamePattern="AST-1696|AST-1421"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

### AST-1704 · AST-1640

**Parent:** [AST-1640 — Job source_entity parent](https://linear.app/astralcareermatch/issue/AST-1640). **Publish:** `origin/sub/AST-1640/AST-1704-track-routing-job-detail-jobs-api-consumers`.

Job Detail / JAR chrome: `job_link` is an href / `window.open` target only for `http(s)`; non-http inherited text still shown. Routed page align: **`docs/test-bible/frontend/pages.md`** § AST-1704. Primary manifest: **`docs/test-bible/core/consult.md`** § AST-1704.

| Area | Source | Component tests |
| --- | --- | --- |
| Header title href + breadcrumb text | `RecommendedJobReportHeader.tsx` | **`test_RecommendedJobReportHeader.test.tsx`** — **`AST-1704`** |
| Info Link row | `JobDetailModal.tsx` | **`test_JobDetailModal.test.tsx`** — **`AST-1704`** |
| JAR header composition | `JobAnalysisReportModal.tsx` | **`test_JobAnalysisReportModal.test.tsx`** — **`AST-1704`** |

**Broken / obsolete this pass:** none — existing https deeplink cases remain.

**Integration:** none.

### AST-1749 · AST-1741

**Parent:** [AST-1741](https://linear.app/astralcareermatch/issue/AST-1741/add-meteorites-to-the-jobs-navigation). **Publish:** `origin/sub/AST-1741/AST-1749-jobs-meteorites-nav-list-page-detail-modal`.

`MeteoriteDetailModal.tsx` — read-only detail (sections from API): http(s) link gate, job deeplink gate, 404 honesty, no Save footer. Page wiring: **`docs/test-bible/frontend/pages.md`** § AST-1749.

| Area | Source | Component tests |
| --- | --- | --- |
| Link / deeplink / 404 / closed | `MeteoriteDetailModal.tsx` | **`test_MeteoriteDetailModal.test.tsx`** |

**Broken / obsolete:** none — new component. Does not revise `JobMeteoritePane` tests.

**Integration:** none revised.

## QA test manifest

See **`docs/test-bible/frontend/pages.md`** § AST-1749 (shared numbered manifest).

---

### AST-1771 · AST-1770

**Parent:** [AST-1770 — Vector Icons are out of sequence](https://linear.app/astralcareermatch/issue/AST-1770/vector-icons-are-out-of-sequence). **Publish:** `origin/sub/AST-1770/AST-1771-recommended-analysis-vector-order-and-tooltips`.

`AgentAnalysisHeader` + JAR Analysis tab: detail rows and header grade dots share importance-then-grade order; header tooltips prefix vector label. Helpers: **`docs/test-bible/frontend/lib.md`** § AST-1771.

| Area | Source | Component tests |
| --- | --- | --- |
| Detail vector order | `AgentAnalysisHeader.tsx` | **`test_AgentAnalysisHeader.test.tsx`** — **`AST-1771: detail rows match importance+grade order`** (+ api mock importOriginal keeper) |
| JAR header + expanded order | `JobAnalysisReportModal.tsx` | **`test_JobAnalysisReportModal.test.tsx`** — extends **`AST-1328: Analysis header uses job-carried jd_rubric…`** with QC-before-EFW + tooltip + `.analysis-vector` order |

**Broken / obsolete:** none beyond api mock repair above. **Integration:** none revised. §6c N/A (modal/component, not routed page).

## QA test manifest

1. Detail: `tests/component/frontend/components/test_AgentAnalysisHeader.test.tsx` — `--testNamePattern="AST-1771"`
2. JAR e2e: `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` — `--testNamePattern="AST-1328"`
3. Lib helpers + header unit: see **`docs/test-bible/frontend/lib.md`** § AST-1771

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_rubricDisplay.test.ts \
  ../../../tests/component/frontend/lib/test_recommendedJobReport.test.tsx \
  ../../../tests/component/frontend/components/test_AgentAnalysisHeader.test.tsx \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  --testNamePattern="AST-1771|AST-1328|sortRubricColumnsByImportanceAndGrade|formatGradeDotTooltipWithVectorLabel|gradeRank|sortJobListRubricColumns"
```

**Bible shasum (after publish):** fill — `git show origin/sub/AST-1770/AST-1771-recommended-analysis-vector-order-and-tooltips:docs/test-bible/frontend/components.md | shasum`

---

### AST-1865 · AST-1853 (clickable job state history opens the run)

**Parent:** [AST-1853 — Execution History for job modals](https://linear.app/astralcareermatch/issue/AST-1853). **Publish:** `origin/sub/AST-1853/AST-1865-clickable-job-state-history-opens-run`. Reads sibling **AST-1864**'s `run_id` (`docs/test-bible/core/tracker.md` § AST-1864), falling back to `batch_id`.

`StateTimeline` rows are clickable (`role="button"`, `title="Open run <id>"`, Enter/Space) only when `onSelectRun` is passed **and** the row resolves `run_id || batch_id`. `JobDetailModal` passes it only when `useAuth().isAdmin`, and stacks `BatchExecutionModal` (reused `BatchAgentDataPanes` + new shared `BatchLogViewer`). `AdminPerformanceMonitor`'s private `LogViewer` moved to `BatchLogViewer` (routed page §6c satisfied by the unedited page suite).

| Area | Source | Component tests |
| --- | --- | --- |
| AC4 admin click `run_id` row → `/api/admin/dispatch_ledger/R/logs` + `/api/agent_data/R?entity_id=<job>` (scoped since **AST-2031**), log + block rendered; claim `batch_id` never opened | `JobDetailModal.tsx`, `BatchExecutionModal.tsx` | **`test_JobDetailModal.test.tsx`** — **`AST-1865 … AC4`** |
| AC5 non-admin → no clickable rows, zero `/api/admin/` calls (asserted after `/api/me` settles) | `JobDetailModal.tsx` | **`… AC5`** |
| AC6 `batch_id`-only row opens `B`; neither → inert | `StateTimeline.tsx`, `JobDetailModal.tsx` | **`… AC6`**; **`test_StateTimeline.test.tsx`** — **`StateTimeline — AST-1865 run selection`** (no-callback inert, run_id > batch_id, keyboard) |
| AC8 Execution History unchanged | `AdminPerformanceMonitor.tsx`, `BatchLogViewer.tsx` | **`test_AdminPerformanceMonitor.test.tsx`** (unedited) |
| AC9 Company modal unchanged / not clickable | `CompanyDetailModal.tsx` (no `onSelectRun`) | **`test_CompanyDetailModal.test.tsx`** (unedited) |
| Panes reuse regression | `BatchAgentDataModal.tsx` | **`test_BatchAgentDataModal.test.tsx`** (unedited) |

**Broken / obsolete (revised this pass):** `test_StateTimeline.test.tsx` `lib/api` mock lacked `setAuthTokenGetter` / `setUnauthorizedHandler` (AuthProvider setup) — both existing cases were red before this ticket; stubs added. **Pre-existing red, not this ticket:** `JobDetailModal — AST-1695 listing_href > read-only: null listing_href → no Link <a> even when job_link is http(s)` (identical on the pre-AST-1865 tree; follows `origin/dev` `82fcbd6c` null-`job_link` change) — excluded by name below, not revised here.

**Integration:** none — do not invent.

## QA test manifest

1. **AC4–AC6, AC8, AC9 + regressions (Vitest):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_StateTimeline.test.tsx \
  ../../../tests/component/frontend/components/test_JobDetailModal.test.tsx \
  ../../../tests/component/frontend/components/test_BatchAgentDataModal.test.tsx \
  ../../../tests/component/frontend/components/test_CompanyDetailModal.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx \
  --testNamePattern='^(?!.*null listing_href)'
```

2. **AC7 (one log viewer):** `grep -rn "dispatch-log-table" src/ui/frontend/src --include=*.tsx` → only `components/BatchLogViewer.tsx`; `grep -n "function LogViewer" src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` → nothing.
3. **AC8 / AC9 unedited:** `git diff origin/dev...HEAD -- tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx tests/component/frontend/components/test_CompanyDetailModal.test.tsx` empty.
4. **AC10:** `git diff origin/dev...origin/sub/AST-1853/AST-1865-clickable-job-state-history-opens-run -- src/ui/api/ src/data/` empty.

**Pass criterion:** item 1 all green (52 pass, 1 name-skipped) + items 2–4 hold — narrowed run, not zero-arg harness.

**Bible shasum (after publish):** fill — `git show origin/sub/AST-1853/AST-1865-clickable-job-state-history-opens-run:docs/test-bible/frontend/components.md | shasum`

### AST-1873 · AST-1862 (report header title row, job-link line, labels, Skip)

`RecommendedJobReportHeader`: title always plain `<span>`; job-link line directly below it (display `jobLinkText` → fallback `jobLink`; `<a target="_blank">` only when `jobLink` is http(s)); copy/skip row shares `.recommended-report-header-row` with `.recommended-report-title-block`; labels **Copy Job Link** / **Copy Job JSON** (→ **Copied**); optional `onSkip` / `skipBusy` → **Skip this Job** last `.btn secondary`. `App.css`: two-column title row, report-modal-only title bar via `.modal-card:has(.recommended-report-shell)`. Modal wiring (`jobLinkText`, `onSkip` from `can_skip`, default tab, `{score}` headers) is sibling **AST-1874**.

| Area | Source | Component tests |
| --- | --- | --- |
| AC6 Skip last in row / absent without `onSkip` / `skipBusy` disables / Skip-only row renders | `RecommendedJobReportHeader.tsx` | **`RecommendedJobReportHeader — AST-1873 title row, job-link line, Skip`** (first two cases) |
| AC8 DOM: button row + title block both direct children of the header row | same | **`…AST-1873…`** › `button row and title block are children of the same header row` |
| AC9 title no `<a>` ancestor; http line `<a target=_blank>` after title; `jobLinkText` plain when no http href; text+href combo; neither → no line | same | **`…AST-1873…`** (four link-line cases) |
| AC7 labels (revised) | same | **`AST-1421 snapshot Copy`**, **`AST-1696 Copy Link`** (header + modal); Job Detail **Copy** (`test_JobDetailModal` AST-1421) unedited, still green |
| AC9 title→line (revised) | `RecommendedJobReportHeader.tsx` via modal | header **`AST-1695 listing title`**, **`AST-1704 http(s)-only href`**; modal **`AST-948`** sticky header + CANDIDATE_REVIEW case, **`AST-1695 listing_href title`** |

**Broken / obsolete (revised this pass):** 13 asserts tied to the linked title `<a>` or **Copy Link** / **Copy** labels — header file (AST-1421 ×3, AST-1695, AST-1696 ×3, AST-1704 http) and modal file (AST-948 sticky header, AST-948 CANDIDATE_REVIEW title, AST-1421, AST-1696, AST-1695 listing_href). Supersedes the title-`<a>` wording in the AST-1695 / AST-1704 blocks above.

**Pre-existing reds (not this ticket; identical on `origin/ftr/AST-1862` before AST-1873):** modal `AST-1546: Print Resume success…`, `AST-1350: Print Resume unsupported toast…` (no **Print Resume** button rendered), modal `AST-1704 … breadcrumb text…` (needs AST-1874 `jobLinkText` = raw `job_link`), `JobDetailModal — AST-1695 … null listing_href → no Link <a>…` (dev drift, see AST-1865 block). Name-excluded below.

**Out of scope:** AC6 modal half (`test_JobAnalysisReportModal` Skip visibility from `can_skip`) and AC10 UAT visual — **AST-1874** / Susan UAT. CSS computed layout is not asserted in jsdom; AC8 CSS + AC10 are grep checks.

**Integration:** none — do not invent.

## QA test manifest

1. **AC6–AC9 + regressions (Vitest):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_RecommendedJobReportHeader.test.tsx \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  ../../../tests/component/frontend/components/test_JobDetailModal.test.tsx \
  --testNamePattern='^(?!.*(no Link <a> even when|AST-1546: Print Resume|AST-1350: Print Resume unsupported|breadcrumb text))'
```

2. **AC6 / AC7 greps (expect nothing):** `grep -n "CANDIDATE_REVIEW\|REVIEW_LIKE" src/ui/frontend/src/components/JobAnalysisReportModal.tsx src/ui/frontend/src/components/RecommendedJobReportHeader.tsx`; `grep -n '"Copy Link"\|>Copy<\|"Copy"' src/ui/frontend/src/components/RecommendedJobReportHeader.tsx`.
3. **AC8 CSS:** `.recommended-report-title-block` has `min-width: 0` + `overflow-wrap`/`word-break`; `.recommended-report-links` has `flex-shrink: 0`; no `white-space: nowrap` on the title block.
4. **AC10:** `git diff origin/dev -- src/ui/frontend/src/App.css` has no hunk inside the existing `.modal-title` / `.modal-header` / `.modal-body` blocks; a `.modal-card:has(.recommended-report-shell) .modal-title` rule sets `font-size` < `18px`.

**Pass criterion:** item 1 green (73 pass, 4 name-skipped) + items 2–4 hold — narrowed run, not zero-arg harness.

**Bible shasum (publish tip):**
- `docs/test-bible/frontend/components.md` — *(filled after publish)*

### AST-1874 · AST-1862 (modal wiring — Analysis default, list score in headers, Skip)

`JobAnalysisReportModal`: active top tab starts `""` and the fallback effect picks `topTabs[0]` (manifest order → **Analysis**), on open and on every `jobId` change — no tab literal. Analysis headers pass `<prefix>_score` (from `grades_field`) into `formatPhaseSectionScoreTitle`. `can_skip` (AST-1872) gates `onSkip` → `postSkipJob` → `onRefresh?.()` + `onClose()`; failure → error toast, modal stays open. Header gets `jobLinkText` = http `listing_href` else raw `job_link`. `formatPhaseScore` moved to `lib/recommendedJobReport.tsx` (shared with `JobsRecommended`). Fixture **`tests/component/frontend/fixtures/stateUiManifestFixture.ts`** now mirrors config: `report_top_tabs` Analysis-first, `phase_score_header_title_template` with ` - {score}` (deferred from AST-1872).

| Area | Source | Component tests |
| --- | --- | --- |
| AC1 Analysis default + order Analysis/Summary/Artifacts/Discussion | `JobAnalysisReportModal.tsx` | **`AST-948 horizontal shell`** › `…with Analysis default (AST-1874)` (revised) |
| AC1 jobId switch after Summary → Analysis | same | **`JobAnalysisReportModal — AST-1874 Analysis default, list score, Skip`** › `switching jobId…` |
| AC3 `JD Analysis - 3.7 - score: …` / absent score drops segment | same + `recommendedJobReport.tsx` | **`…AST-1874…`** › two JD header cases; **`recommendedJobReport — AST-1874 list score in phase header`**; **`AST-1348 Analysis score title chrome`** (revised to `- 8.5 -`) |
| AC4 one formatter; list cells unchanged | `recommendedJobReport.tsx`, `JobsRecommended.tsx` | **`recommendedJobReport — AST-1874…`** › `formatPhaseScore…`; `test_JobsRecommended.test.tsx` score-column cases unedited |
| AC5 Skip shown iff `can_skip` true, last in row | `JobAnalysisReportModal.tsx` | **`…AST-1874…`** › `can_skip=%s…` (true / false / absent); header half **AST-1873** |
| AC6 POST `/skip` 200 → `onRefresh` ×1 + `onClose` ×1; 409 → server-message toast, no close | same | **`…AST-1874…`** › `Skip success…`, `Skip 409…` |
| `jobLinkText` raw `job_link` when no http `listing_href` | same | **`AST-1704 non-http job_link chrome`** (revised fixture: `listing_href: null`) — now green |

**Broken / obsolete (revised this pass):** modal — AST-948 Summary-default (now Analysis + waits for the post-paint default effect), AST-948 no-upshot shell + AST-949 ×4 (select Summary via `openSummaryTab()`), AST-1348 title (fixture template now has `{score}`), AST-1551 / AST-1692 ×2 tab-order arrays, AST-1704 breadcrumb fixture; pages — `test_JobsRecommended` `opens the report modal from a row click` and `test_JobsJobDetail` AST-1481 ×2 asserted the Summary pane on open. **AC4 note:** the JobsRecommended edit is the modal default-tab assert only (AC1 by design); no list-column assert changed.

**Fixture ripple check:** every other `STATE_UI_MANIFEST_FIXTURE` / `page-mocks` consumer run with and without the fixture change — identical failure sets (24 pre-existing reds, `lib/api` mock missing `setAuthTokenGetter` et al.; not this ticket).

**Pre-existing reds (not this ticket):** modal `AST-1546: Print Resume success…`, `AST-1350: Print Resume unsupported toast…` (see AST-1873 block). Name-excluded below.

**Integration:** none — do not invent.

## QA test manifest

1. **AC1, AC3–AC6 + regressions (Vitest):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  ../../../tests/component/frontend/components/test_RecommendedJobReportHeader.test.tsx \
  ../../../tests/component/frontend/lib/test_recommendedJobReport.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsJobDetail.test.tsx \
  ../../../tests/component/frontend/contexts/test_StateUiContext.test.tsx \
  --testNamePattern='^(?!.*(AST-1546: Print Resume|AST-1350: Print Resume unsupported))'
```

2. **AC2 / AC4 / AC5 greps (expect nothing):** `grep -n 'useState("summary")\|setActiveTopTab("summary")' src/ui/frontend/src/components/JobAnalysisReportModal.tsx`; `grep -rn "toFixed(1)" src/ui/frontend/src/pages/JobsRecommended.tsx`; `grep -n "CANDIDATE_REVIEW\|REVIEW_LIKE" src/ui/frontend/src/components/JobAnalysisReportModal.tsx src/ui/frontend/src/components/RecommendedJobReportHeader.tsx`.
3. **AC1 config half:** AST-1872 manifest (`docs/test-bible/core/tracker.md` § AST-1872) — `TestBuildStateUiManifest::test_ast565_recommended_report_manifest_tabs`.
4. **Boundaries:** `git diff origin/ftr/AST-1862-recommended-job-modal-changes...HEAD -- src/ui/frontend/src/components/{Modal,CandidateJobRowActions,JobDetailModal,RecommendedJobReportHeader}.tsx src/ui/frontend/src/pages/JobsJobDetail.tsx src/ui/frontend/src/App.css src/utils src/ui/api src/core` empty.

**Pass criterion:** item 1 green (115 pass, 2 name-skipped) + items 2–4 hold — narrowed run, not zero-arg harness.

**Bible shasum (publish tip):**
- `docs/test-bible/frontend/components.md` — *(filled after publish)*

**AST-1968 (pointer):** `CandidateJobRowActions` takes an optional `onGenerate` that adds a **G** `icon-control` (`title="Generate Artifacts"`) in the review-like branch, passed only by Recommended for manifest-eligible rows — **`CandidateJobRowActions — AST-1968 Generate`**. Manifest: **`docs/test-bible/frontend/pages.md`** § AST-1968.

### AST-1973 · AST-1972 (Job Detail Info-tab analysis via shared PhaseAnalysisLines)

**AST-1975:** `JobsInReview.tsx` became `JobsProcessing.tsx` and `test_JobsInReview.test.tsx` was renamed `test_JobsProcessing.test.tsx` (`view=processing`). Run `test_JobsProcessing.test.tsx` where the manifest below says `test_JobsInReview.test.tsx`.

**Parent:** [AST-1972](https://linear.app/astralcareermatch/issue/AST-1972). **Publish:** `origin/sub/AST-1972/AST-1973-job-modal-info-tab-analysis`.

New **`components/PhaseAnalysisLines.tsx`** owns the phase-lines block that AST-1968 had inline in `JobsRecommended.tsx`: it takes one job record and derives lines from manifest `report_phase_tabs` (order + `grades_field`) with short labels from `phase_score_columns`, falling back to `nav_label`. Each line renders `buildPhaseListGradeRow(job, gradesField) ?? "—"`. Recommended's analysis row now renders `<PhaseAnalysisLines job={job} />`, with the row, `colSpan`, click and toggle unchanged. `JobDetailModal` `InfoTab` right column renders an **Analysis** `entity-section-label` plus the component before **State History**, not gated on state. `JobDetail` gains `[key: string]: unknown`. No dedicated `test_PhaseAnalysisLines` file: both hosts exercise it.

| AC | Source | Component tests |
| --- | --- | --- |
| 1 Analysis label → lines → State History, right column | `JobDetailModal.tsx` | **`test_JobDetailModal.test.tsx`** › **`JobDetailModal — AST-1973 Info-tab analysis > AC1/AC2…`** |
| 2 one line per `report_phase_tabs`, JD/DO/GET/LIKE | `PhaseAnalysisLines.tsx` | **`… > AC1/AC2…`**; list side **`test_JobsRecommended`** › **`AST-1968 … AC9`** (unedited) |
| 3 partial → em dash; no grades → four em dashes, modal renders; skipped state ungated | `PhaseAnalysisLines.tsx`, `JobDetailModal.tsx` | **`… > AC3: no phase grades…`**, **`… > AC3: JD + DO graded…`** |
| 4 count / `dot-*` / order / `title` equal the list | `PhaseAnalysisLines.tsx` → `buildPhaseListGradeRow` | **`… > AC4…`** (modal line vs list row builder on AST-1771 fixture); builder ↔ modal-report parity **`recommendedJobReport — AST-1968 letterless list grade row`** (unedited) |
| 5 letterless, no confidence, display-only | same | **`… > AC5…`**; list side **`AST-1968 … AC10`** (unedited) |
| 6 one shared component | source | greps below |
| 7 Recommended list unchanged | `JobsRecommended.tsx` | **`test_JobsRecommended.test.tsx`** whole file (unedited; AC9 / AC10 assert the moved markup) |
| 8 no backend / 9 build + lint | source | diff stat + build/lint below |

**Broken / obsolete:** none. No existing test queries the modal's right column or the `Analysis` text inside it.

**Pre-existing red (not this ticket):** `JobDetailModal — AST-1695 listing_href > read-only: null listing_href → no Link <a>…` (see AST-1865 block). Name-excluded below.

**Integration:** none. Frontend only, so do not invent one.

## QA test manifest

1. **AC1–AC5, AC7 + host regressions (Vitest, all green):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobDetailModal.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx \
  ../../../tests/component/frontend/lib/test_recommendedJobReport.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsSkipped.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsInReview.test.tsx \
  --testNamePattern='^(?!.*null listing_href)'
```

2. **AC6 greps:** `rg -n "PhaseAnalysisLines" src/ui/frontend/src/pages/JobsRecommended.tsx src/ui/frontend/src/components/JobDetailModal.tsx` gives one or more hits in **each** file. `rg -n "report_phase_tabs|buildPhaseListGradeRow" src/ui/frontend/src/pages/JobsRecommended.tsx src/ui/frontend/src/components/JobDetailModal.tsx` prints **nothing**.
3. **AC8:** `git diff origin/dev...origin/sub/AST-1972/AST-1973-job-modal-info-tab-analysis --stat -- src/ui/api src/core src/data src/utils` prints nothing.
4. **AC9:** in `src/ui/frontend`, `npm run build` exits 0 and `npx tsc -b --noEmit` exits 0. `npm run lint` lists no problem that `origin/dev` does not already report.

**Pass criterion:** item 1 green (88 pass, 1 name-skipped) and items 2–4 hold. Use the narrowed run, not the zero-arg harness.

**Bible shasum (publish tip):**
- `docs/test-bible/frontend/components.md`: filled after publish
- `docs/test-bible/frontend/pages.md`: filled after publish

### AST-1982 · AST-1981 (shared job-title renderer + list tables)

**Parent:** [AST-1981](https://linear.app/astralcareermatch/issue/AST-1981). **Publish:** `origin/sub/AST-1981/AST-1982-job-title-renderer`.

New **`components/JobTitleText.tsx`** cuts a title through `truncateForDisplay` at `resolveJobTitleTruncateChars(getUiConfig())` (`lib/uiConfig.ts`, fallback 50), served from **`UI_CONFIG["job_title_truncate_chars"] = 50`**. A short title renders as bare text. A cut title renders a `<span>`; hovering it portals a `role="tooltip"` `.job-title-tooltip` with the full title to `document.body`. Mouse-out or any scroll closes it. Empty title renders the caller's required `fallback`. Used by the Job Title `<td>` on `JobsRecommended` (Ready + Review), `JobsProcessing`, `JobsSkipped` (every table variant), `JobsApplied`, and by the Meteorites `job_title` column `render`. That element bypasses `ListPage`'s 30-char string cut, so other columns keep 30. Modal / report headers are sibling **AST-1983**.

Shared page helper **`tests/component/frontend/pages/job-title-cell.ts`** (`jobTitleJobs`, `expectJobTitleCells`) seeds a 79-char title (word `Zanzibar` past char 50) and an exactly-50-char title, then checks AC 1–3 on one rendered table.

| AC | Source | Component tests |
| --- | --- | --- |
| 1 long titles cut at 50 + `…` on every list | `JobTitleText.tsx`, five pages | **`test_JobTitleText`** › **`long title cut via the config length…`**; **`AST-1982`** tests in **`test_JobsRecommended`** (review + ready), **`test_JobsProcessing`**, **`test_JobsSkipped`** (below-floor + regular), **`test_JobsApplied`**, **`test_JobsMeteorites`** |
| 2 ≤ 50 exact; no tooltip, no `title` | `JobTitleText.tsx` | **`test_JobTitleText`** › **`50-char title renders exactly…`**; every page test above (helper hovers the 50-char cell) |
| 3 tooltip = full title, under `body`, outside table, wraps at fixed px width, gone on mouse-out | `JobTitleText.tsx`, `App.css` | **`test_JobTitleText`** › **`hover opens one tooltip…`**, **`any scroll closes…`**, **`tooltip style wraps…`** (reads the `.job-title-tooltip` rule; jsdom loads no CSS); every page test above. Multi-line `offsetHeight` for titles over 100 chars needs a real browser, so it is UAT only |
| 4 Meteorites title 50, other columns 30 | `JobsMeteorites.tsx` | **`JobsMeteorites — AST-1982 Job Title cut`** › **`Title cut at 50…; other columns still cut at 30`** |
| 5 one source for 50, one cut path | `config.py`, `uiConfig.ts` | **`test_api_system.py::TestSystemAuthRoutes::test_ui_config_includes_job_title_truncate_chars`**; **`test_uiConfig`** › **`resolveJobTitleTruncateChars…`**; **`test_JobTitleText`** › **`cut length follows UI_CONFIG…`** (served 20 → cut at 20); greps below |
| 6 every surface uses the component | five pages | greps below |
| 7 sort / search read the full title | `JobsRecommended.tsx`, `ListPage` | **`JobsRecommended — AST-1982 Job Title cut`** › **`ready: Job Title sort orders by the full title…`** (titles equal for 50 chars); **`JobsMeteorites — AST-1982`** › **`search for a word past char 50…`** |
| 8 build / lint | source | item 4 below |

**Broken / obsolete:** none. Every existing page fixture title is under 50 chars. No test asserted the raw `{job.job_title || "—"}` markup.

**Pre-existing red (not this ticket; also red with `dev` product and no AST-1982 tests):** the **`AST-1979 Created column` › `…Created left of…`** tests in the four hand-built page files need **AST-1971** product, which is not on `origin/dev`. **`JobsApplied — AST-1479 › Interview → notes modal → candidate_action interview`** times out. **`test_api_system.py::TestAst1375InflightHideStatesManifest::test_manifest_includes_inflight_hide_states`** also fails. All are name-excluded below.

**Integration:** none. Frontend plus one served config key, so do not invent one.

## QA test manifest

1. **AC 1–4, AC 5 component side, AC 7 (Vitest, all green):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobTitleText.test.tsx \
  ../../../tests/component/frontend/lib/test_uiConfig.test.ts \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsProcessing.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsSkipped.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsApplied.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsMeteorites.test.tsx \
  --testNamePattern='^(?!.*(Created left of|candidate_action interview))'
```

2. **AC 5 served key (pytest):**

```bash
.venv/bin/python -m pytest tests/component/ui/api/test_api_system.py -q -k "ui_config"
```

3. **AC 5 / AC 6 greps:**
   - `rg -l "JobTitleText" src/ui/frontend/src/pages` lists `JobsRecommended.tsx`, `JobsProcessing.tsx`, `JobsSkipped.tsx`, `JobsApplied.tsx`, `JobsMeteorites.tsx`.
   - `rg -n '\{job\.job_title \|\| "\\u2014"\}' src/ui/frontend/src/pages` prints nothing.
   - `rg -n "\.slice\(" src/ui/frontend/src/components/JobTitleText.tsx` prints nothing.
   - `git diff origin/dev -- src/ui/frontend/src/pages src/ui/frontend/src/components | rg "^\+.*(\b50\b|job_title.*\.slice\()"` prints nothing.
4. **AC 8:** `python -c "import src.utils.config"` exits 0. In `src/ui/frontend`, `npm run build` exits 0. `npm run lint` lists no problem that `origin/dev` does not already report.

**Pass criterion:** items 1–2 green with the name exclusions above, and items 3–4 hold. Use the narrowed run, not the zero-arg harness.

**Bible shasum (publish tip):**
- `docs/test-bible/frontend/components.md`: filled after publish

### AST-1983 · AST-1981 (job headers use the shared renderer)

**Parent:** [AST-1981](https://linear.app/astralcareermatch/issue/AST-1981). **Publish:** `origin/sub/AST-1981/AST-1983-job-title-headers`. Consumes **AST-1982**'s `JobTitleText` as-is.

`Modal`'s `title` prop widens from `string` to `ReactNode`. It is still rendered only inside `<h2 className="modal-title">`. `JobDetailModal` passes `<JobTitleText title={job?.job_title} fallback={job?.company || "Job Detail"} />`. `MeteoriteDetailModal.modalTitle` returns `JobTitleText` for the title part plus a plain ` — <employer>` suffix (employer-only and id fallbacks unchanged). `RecommendedJobReportHeader` wraps `.recommended-report-title` content in `JobTitleText`. The Info-tab Title field (`<span>{job.job_title || "—"}</span>`) and edit input are untouched.

`tests/component/frontend/pages/job-title-cell.ts` now exports **`expectFullTitleTooltip(span, host)`**: one tooltip, full title, direct child of `body`, outside `host`, gone on mouse-out. AST-1982's `expectJobTitleCells` calls it, and the header tests below reuse it with the `.modal-overlay` or header row as `host`.

| AC | Source | Component tests |
| --- | --- | --- |
| 5 headers cut at 50 + `…`, employer suffix whole, AC-3 tooltip | `JobDetailModal.tsx`, `MeteoriteDetailModal.tsx`, `RecommendedJobReportHeader.tsx`, `Modal.tsx` | **`JobDetailModal — AST-1983 header title cut`** › **`AC5…`**, **`empty title keeps the company / Job Detail header fallback`**; **`MeteoriteDetailModal — AST-1983 header title cut`** (title + employer, title only, employer only); **`RecommendedJobReportHeader — AST-1983 title cut`** (long, 50-char) |
| 6 Info-tab Title field and edit input full | `JobDetailModal.tsx` | **`JobDetailModal — AST-1983 …`** › **`AC5…; AC6: read-only Title field is full`**, **`AC6: editable Title input holds the full title…`** |
| 7 every in-scope surface uses the component | source | grep below |
| 8 build / lint | source | item 3 below |

**Broken / obsolete:** none. Existing modal and header fixtures use short titles. `Modal`'s `title` is used only in the `<h2>`. The Meteorite `"Staff Eng — Acme"` lookup still matches, because both text nodes sit in one `<h2>`.

**Pre-existing red (not this ticket; also red with the `ftr` versions of the four product files):** **`JobDetailModal — AST-1695 › read-only: null listing_href…`** (see AST-1865 / AST-1973). **`JobAnalysisReportModal — AST-948 › AST-1350: Print Resume unsupported toast…`** and **`… › AST-1546: Print Resume success…`**. All are name-excluded below.

**Integration:** none. Frontend only, so do not invent one.

## QA test manifest

1. **AC 5–6 + host regressions (Vitest, all green):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobDetailModal.test.tsx \
  ../../../tests/component/frontend/components/test_MeteoriteDetailModal.test.tsx \
  ../../../tests/component/frontend/components/test_RecommendedJobReportHeader.test.tsx \
  ../../../tests/component/frontend/components/test_Modal.test.tsx \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  ../../../tests/component/frontend/components/test_JobTitleText.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsMeteorites.test.tsx \
  --testNamePattern='^(?!.*(null listing_href|Print Resume unsupported toast|Print Resume success))'
```

2. **AC 7 grep:** `rg -l "JobTitleText" src/ui/frontend/src/components` lists `JobDetailModal.tsx`, `MeteoriteDetailModal.tsx`, `RecommendedJobReportHeader.tsx` (plus `JobTitleText.tsx` itself).
3. **AC 8:** in `src/ui/frontend`, `npm run build` exits 0 and `npx tsc -b --noEmit` exits 0. `npm run lint` lists no problem that `origin/dev` does not already report.

**Pass criterion:** item 1 green with the name exclusions above, and items 2–3 hold. Use the narrowed run, not the zero-arg harness.

**Bible shasum (publish tip):**
- `docs/test-bible/frontend/components.md`: filled after publish

### AST-2031 · AST-2028 (job run modal requests entity-scoped agent data)

**Parent:** [AST-2028](https://linear.app/astralcareermatch/issue/AST-2028). **Publish:** `origin/sub/AST-2028/AST-2031-job-run-modal-entity-scoped`. `BatchAgentDataPanes` takes optional `entityId` → `?entity_id=<encoded>` on `/api/agent_data/…` only (timesheets + dispatch ledger stay batch-wide; refetch on change). `BatchExecutionModal` forwards `entityId`; `JobDetailModal` passes `job?.astral_job_id`. `BatchAgentDataModal` (Execution History / Vector Feedback) has no `entityId` prop; Ad Hoc renders the panes without it. Backend slicing: **`core/agent.md`** § AST-2030.

| Area | Source | Component tests |
| --- | --- | --- |
| AC8 job modal run → `/api/agent_data/R?entity_id=j1`, never the unscoped URL | `JobDetailModal.tsx`, `BatchExecutionModal.tsx` | **`test_JobDetailModal.test.tsx`** — **`AST-1865 … AC4`**, **`… AC6`** (revised) |
| `entityId` scopes agent data only, URL-encoded; timesheets + ledger unscoped | `BatchAgentDataModal.tsx` (`BatchAgentDataPanes`) | **`test_BatchAgentDataModal.test.tsx`** — **`BatchAgentDataPanes — AST-2031 … entityId → encoded entity_id on agent data only`** |
| No `entityId` → whole-batch URL | same | **`… no entityId → whole-batch agent data URL`** |
| `entityId` change refetches | same | **`… changing entityId refetches the scoped agent data`** |
| AC9 batch-wide callers unchanged | `AdminPerformanceMonitor.tsx` | **`test_AdminPerformanceMonitor.test.tsx`** (unedited) |

**Broken / obsolete (revised in place):** `test_JobDetailModal.test.tsx` **`AST-1865 … AC4`** / **`… AC6`** asserted the unscoped `/api/agent_data/<run>` — now assert `?entity_id=j1` and the absence of the unscoped URL; the AST-1865 `mockRunApis` agent-data route regex now ignores the query string (it captured `hop-R?entity_id=j1` as the run id). AST-1865 AC4 table row above updated to match.

**AC9 grep note:** the ticket's literal check (`grep -n "entity_id"` over the three admin pages) can never pass — `AdminAnthropicAdHoc.tsx` already carries 8 `entity_id` hits on `origin/dev` (ad hoc run entity fields, unrelated to the agent-data fetch). Manifest item 2 checks the intent instead: no page passes `entityId={…}` to the panes, and those pages are unchanged vs `origin/dev`.

**Red / green:** AC4, AC6 and the two scoped pane tests are red on `origin/ftr/AST-2028-…` (pre-AST-2031); the no-`entityId` guard is green there.

**Pre-existing red, not this ticket:** `JobDetailModal — AST-1695 listing_href > read-only: null listing_href → no Link <a> even when job_link is http(s)` — also red on the ftr tip; name-skipped below (same exclusion as § AST-1865).

**Integration:** none — do not invent.

## QA test manifest — AST-2031

1. **AC8, AC9 + regressions (Vitest):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobDetailModal.test.tsx \
  ../../../tests/component/frontend/components/test_BatchAgentDataModal.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx \
  --testNamePattern='^(?!.*null listing_href)'
```

2. **AC9 batch-wide callers:** `rg -n "entityId=\{" src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx src/ui/frontend/src/pages/AdminVectorFeedback.tsx src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` → nothing; `git diff origin/dev...HEAD -- src/ui/frontend/src/pages/ tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx` empty.
3. **No backend change:** `git diff origin/dev...origin/sub/AST-2028/AST-2031-job-run-modal-entity-scoped -- src/ui/api/ src/data/` empty.

**Pass criterion:** item 1 all green (54 pass, 1 name-skipped) + items 2–3 hold. `npx tsc -b --noEmit` clean. Not the zero-arg harness.

---

### AST-2056 · AST-2041 (gap — resume editor autosave; product AST-2051)

> **Superseded by AST-2068** (blur-save replaced the `AUTOSAVE_MS` timer): the timer rows below are historical. Current names and contract: § AST-2068.

**Parent:** [AST-2041](https://linear.app/astralcareermatch/issue/AST-2041) (orphaned mini-parent). **Publish:** `origin/sub/AST-2041/AST-2056-resume-autosave-tests`. **Gap from** `[board-betty] TESTS: REVISE` on **AST-2051** (`origin/sub/AST-2041/AST-2051-resume-autosave`) — test tree + bible only. Plan: `docs/features/artifacts/ast-1459-resume-editor-is-not-working-properly.md` § Bug: AST-2051 / § Bug: AST-2056.

Contract (AST-2051, reverses the AST-1459 explicit-Save line): resume editors (structure mode via `useCandidateResumeStructure` or `bodyShape="resume_content"`, incl. JAR Job Resume under `jobPersistence`) **autosave section bodies after `AUTOSAVE_MS` (2000)**; header shows status text ("Unsaved changes" / "All changes saved"); **Save/Cancel only during Generate review**. `shapesKey` job editors (cover letter / application responses) keep explicit Save/Cancel. Guards: queued timer no-ops while `snapshot !== null` (AST-905); `dirty` clears only when the saved tabs are still current; autosave ticks skip `jobPersistence.onSaved` (unmount flush still calls it).

**Harness:** `startAutosaveClock()` = `vi.useFakeTimers({ shouldAdvanceTime: true })` (keeps RTL polling + userEvent delays live); `advanceAutosave()` = `act(vi.advanceTimersByTimeAsync(AUTOSAVE_MS))`; `afterEach(vi.useRealTimers)`. Retargeted cases assert `expectNoHeaderSaveCancel()` then advance the clock in place of the old Save click; PUT payload assertions unchanged except where the case had no edit (an edit is now required to trigger autosave — payload asserts the edited body).

| Area | Source | Component tests (`test_ArtifactEditor.test.tsx`) |
| --- | --- | --- |
| Structure body autosave, debounce, status text **[bug-repro]** | `ArtifactEditor.tsx` | new **`AST-2051 [bug-repro]: structure body edit autosaves after AUTOSAVE_MS…`** |
| Job Resume (`jobPersistence`) autosave **[bug-repro]** | same | new **`AST-2051 [bug-repro]: jobPersistence Job Resume body edit autosaves PUT…`** |
| Review keeps Save/Cancel, no autosave in review | same | new **`AST-2051: Generate review keeps header Save/Cancel and never autosaves (AST-905)`** (guard — green pre-fix) |
| Pre-Generate timer no-op during review | same | new **`AST-2051: autosave timer queued before Generate does not fire during review (AST-905)`** (guard — green pre-fix; red if the `snapshotRef` check is dropped) |
| In-flight autosave keeps dirty; unmount flushes newer edit **[bug-repro]** | same | new **`AST-2051 [bug-repro]: in-flight autosave keeps dirty…`** |
| Autosave skips `onSaved`; unmount flush calls it **[bug-repro]** | same | new **`AST-2051 [bug-repro]: jobPersistence autosave skips onSaved…`** |
| Retargeted Save-click → autosave | same | **`job persistence mode … autosaves PUT (AST-553 / AST-2051)`**, **`AST-996/AST-1351 … autosaves as array`**, **`AST-1351: legacy … autosave aborts`** (no PUT + error toast + "Unsaved changes"), **`AST-1382 [bug-repro]: content autosave bundles…`**, **`AST-1476: … content autosave and Save sections…`**, **`AST-1480: … autosave still works`**, **`AST-1593: job_resume load uses hydrated current leaf body`**, **`AST-1480: structure mode bodies stay editable…`**, **`AST-1577: bodyShape resume_content…`** |
| AST-1410 non-review Cancel re-GET | same | **`AST-1410: no-snapshot Cancel re-GETs…`** — retargeted to a `shapesKey="cover_letter"` + `jobPersistence` editor (only non-review Cancel path left) |

Page case: **`docs/test-bible/frontend/pages.md`** § AST-2056.

**Broken / obsolete (revised in place):** the ten header-Save/Cancel cases above (they encoded the pre-AST-2051 explicit-Save contract). Unaffected: L228 `shapesKey` fixed-shape Cancel, rubric/criteria review-mode Save cases, `test_JobAnalysisReportModal.test.tsx`.

**Red / green:** on the pre-fix tree (`origin/ftr/AST-2041-resume-autosave` product) 13 `test_ArtifactEditor` cases are red — header Save still renders (`expectNoHeaderSaveCancel`) or no autosave PUT fires; the two AST-905 guard cases and AST-1410 are green. With AST-2051 `ArtifactEditor.tsx` (`9fb7b99b1`) overlaid in scratch (not committed), all green.

**Pre-existing red, not this ticket (name-skipped below):** `test_ArtifactsBaseResumeContent` **`AST-1577: page and draft follow ui-consistency`** reads `canon/directives/draft/patt.artifact.ui-consistency.md`, which now lives under `canon/directives/active/`; `test_JobAnalysisReportModal` **`AST-1546: Print Resume success…`** and **`AST-1350: Print Resume unsupported toast…`** (no "Print Resume" button). All three red on the pre-fix tree too.

**Integration:** none — frontend-only; do not invent.

## QA test manifest — AST-2056

1. **Repro + retargets + JAR regression (Vitest):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  ../../../tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  --testNamePattern='^(?!.*(page and draft follow ui-consistency|Print Resume success|Print Resume unsupported toast))'
```

2. **[bug-repro] flip (test-fix):** `--testNamePattern="AST-2051 \[bug-repro\]"` on `test_ArtifactEditor.test.tsx` — 4 red on pre-fix, 4 green after AST-2051.

**Pass criterion:** item 1 all green (105 pass, 3 name-skipped). `npx tsc -b --noEmit` clean. Not the zero-arg harness.

**AST-2049 (pointer):** inline colors in `ArtifactEditor`, `ContextTextPage`, `NavigationShell`, `ProfileTextPage`, `RepoJsonDivergenceBanner`, `StateTimeline`, `TabbedTextArea` moved onto `App.css` tokens — no color asserted by their tests; AC9 source-wide guard lives in `tests/component/frontend/test_AppCss.test.tsx` (moved from the retired `pages/test_AdminThemeExamples.test.tsx` by AST-2122; [`root.md`](root.md) § AST-2122). Manifest: [`pages.md`](pages.md) § AST-2049.

---

### AST-2065 · AST-2042 (UI config URL) — pointer

`lib/uiConfig.ts` `[bug-repro]` URL guard (`test_uiConfig.test.ts` › **`uiConfig URL — AST-2065`**) and the `/api/system/ui_config` → `/api/ui_config` mock retarget in `test_ArtifactEditor`, `test_ContextTextPage`, `test_JobTitleText`, `test_ListPage`, `test_ListPage_listTableLayout`, `test_ListPage_ui_config_fail`. Map + manifest: **`docs/test-bible/frontend/pages.md`** § AST-2065.

### AST-2060 · AST-2058 (show rubric reads hydrated detail content; gap — product AST-2059)

**Parent:** [AST-2058](https://linear.app/astralcareermatch/issue/AST-2058) (orphaned mini-parent). **Publish:** `origin/sub/AST-2058/AST-2060-show-rubric-tests`. **Gap from** `[board-betty] TESTS: REVISE` on **AST-2059** (`61f1f40ea`, on `ftr/AST-2058-show-rubric-content`) — test tree + bible only. Plan: `docs/features/interface/ast-1063-job-carried-rubric-hydration-for-list-columns.md` § Bug: AST-2059 / § Bug: AST-2060.

Contract (AST-2059): **show rubric** content comes from `GET /api/candidates/<id>` (hydrated `rubric_vector` overlay); the `GET /api/candidates` list payload carries **no** rubric rows. `RubricModal` shows `Loading rubric…` until the fetch settles (no not-found flash); `!r.ok` / rejected fetch → `No rubric found for this vector.`. Labels/order unchanged (`rubricItems`, then list fallback).

**Harness:** `mockApiRoutes({ list, detail })` routes the `api` mock by URL — `/api/candidates/c1` → `detail` (function form invoked per call, so rejections stay lazy); every other path → the list response (providers unchanged). Default list = production shape (`artifacts: {}`).

| Area | Source | Component tests |
| --- | --- | --- |
| Content from hydrated detail, loading no-flash **[bug-repro]** | `AgentAnalysisHeader.tsx` | `test_AgentAnalysisHeader.test.tsx` — new **`AST-2059: show rubric reads content from hydrated candidate detail, not the list payload`** |
| Failed detail fetch → fallback, not stuck loading | same | new **`AST-2059: failed detail fetch ends on the fallback, not stuck loading`** (`!r.ok` + rejection; guard — green pre-fix) |
| Retargeted to detail-sourced content | same | **`renders grades with rubric links and opens the modal`**, **`matches rubric rows by code and handles missing modal content`**, **`opens the rubric modal with no matching row (null content)`** (`findByText`) |
| Modal loading state | `RubricModal.tsx` | `test_RubricModal.test.tsx` — new **`shows loading text instead of the fallback while loading`** |

**Broken / obsolete (revised in place):** header fixtures carried list-payload `content` (pre-AST-723 shape) — stayed green post-fix only via the `labelRow` fallback. Unaffected: AST-1771 order test, `falls back to raw vector labels…`, `normalizes an empty vector key…`, RubricModal null-content fallback, `test_JobAnalysisReportModal.test.tsx` (never clicks show rubric).

**Red / green:** pre-fix `06df211db` — 4 red (bug-repro at `Loading rubric…`; two retargeted header cases find no content; RubricModal loading), 7 green. Post-fix `origin/ftr/AST-2058-show-rubric-content` @ `4ee1d7029` + this publish — 11/11 green.

**Integration:** none — frontend-only; do not invent.

## QA test manifest — AST-2060

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_AgentAnalysisHeader.test.tsx \
  ../../../tests/component/frontend/components/test_RubricModal.test.tsx
```

**[bug-repro] flip (test-fix):** `--testNamePattern="AST-2059: show rubric reads content"` — red on `06df211db`, green on ftr tip.

**Pass criterion:** 11/11 green. `npx tsc -b --noEmit` clean. Not the zero-arg harness.

---

### AST-2071 · AST-2054 (company upshot in report + company detail)

**Parent:** [AST-2054](https://linear.app/astralcareermatch/issue/AST-2054). **Publish:** `origin/sub/AST-2054/AST-2071-upshot-display`. Plan: `docs/features/roster/ast-2071-show-the-company-upshot-in-the-report-and-company-detail.md`. API side: [`../ui/api/api_companies.md`](../ui/api/api_companies.md) § AST-2071.

Recommended report Summary **Company Upshot** renders top-level `company_upshot` from `GET /api/companies/<short_name>` (trimmed; empty → `No company upshot on file.`; `default_expanded` follows presence). `prefilter_company_notes` is no longer read there. `CompanyDetailModal` adds an **Upshot** `DetailRow` only when `company_upshot.trim()` is non-empty; Notes row unchanged. Modal-only product diff — §6c routed-page rule N/A.

| Area | Source | Component tests |
| --- | --- | --- |
| AC13 Company Upshot prose only (grade notes decoy hidden) | `JobAnalysisReportModal.tsx` | `test_JobAnalysisReportModal.test.tsx` — **`AST-949 Summary tab sections`** revised: **`fills Summary section bodies from upshot, company upshot, and JD`**, **`content-aware expand: …`**, **`shows empty-state copy when upshot and company upshot are missing`**, **`company upshot comes from company API, not job_data`** |
| AC14 Upshot row present / absent; Notes unchanged | `CompanyDetailModal.tsx` | `test_CompanyDetailModal.test.tsx` — new **`AST-2071: shows an Upshot row only when company_upshot is non-empty; Notes row unchanged`** |

**Broken / obsolete (revised in place):** the four AST-949 Summary cases mocked `prefilter_company_notes` as the Company Upshot body — would go red on this product. Now mock `company_upshot`, with `prefilter_company_notes: "GRADE_NOTES_DECOY"` asserted absent.

**Known pre-existing red (not this ticket):** `AST-1546: Print Resume success …` and `AST-1350: Print Resume unsupported toast — no tab` in the same file fail identically with `origin/dev`'s `JobAnalysisReportModal.tsx` — untouched here.

**Integration:** none — no `tests/integration/` scenario reads company detail; do not invent.

## QA test manifest — AST-2071

```bash
./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_companies.py -q
cd src/ui/frontend && npx tsc -b --noEmit
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  ../../../tests/component/frontend/components/test_CompanyDetailModal.test.tsx
# AC13 grep gate — expect no output
rg -n prefilter_company_notes src/ui/frontend/src/components/JobAnalysisReportModal.tsx
```

**Pass criterion:** pytest 16/16; Vitest 57 pass + the 2 known pre-existing Print Resume reds above (59 total); `tsc` clean; grep empty. Not the zero-arg harness.

### AST-2068 · AST-2043 (blur-save + version arrows)

**Publish:** `origin/sub/AST-2043/AST-2068-version-ui`. `ArtifactEditor` blur-saves bodies (a focusout on `dep-body` after an edit → one PUT; an unchanged blur → none; no PUT while typing; never during Generate review). `AUTOSAVE_MS` is gone. The shared **`ArtifactVersionNav`** ("Previous version" / "N of M" / "Next version") orders by `position` only. It appears artifact-level on fixed-field editors (Base Resume Content, JAR cover letter / job resume), per criterion on candidate criteria pages, and artifact-level on `ContextTextPage`. A move flushes unsaved edits first, then steps from the new current and re-hydrates via the current-read GET.

**Broken → revised (15, all `test_ArtifactEditor.test.tsx` + 1 page):** the fake-clock `startAutosaveClock` / `advanceAutosave` helpers were replaced by **`blurToSave()`** (`.blur()` inside `act`; jsdom fires a bubbling `focusout`). Debounce tests now assert "no PUT while typing, one PUT on blur": **`AST-2051 / AST-2068: structure body edit saves one PUT on blur…`** and **`AST-2051 / AST-2068: jobPersistence Job Resume body edit saves one PUT on blur…`**. The pre-Generate timer test became **`AST-2068: edit typed before Generate saves once on the Regenerate blur; review never saves (AST-905)`**. Clicking Regenerate is itself a blur, so the user's own edit lands before review opens, and a review blur still saves nothing (plan § Verification AC 1/2). The other 11 keep their names with `blurToSave()` in place of the timer.

**Also fixed (pre-existing reds on this file set):** `AST-1577: page and draft follow ui-consistency` now reads `canon/directives/active/patt.artifact.ui-consistency.md` (moved from `draft/`; test name kept for the AST-1628 manifest filter). `test_ArtifactsDoJobCriteria.test.tsx` `api` mock gains `setAuthTokenGetter` / `setUnauthorizedHandler`, and the handlers gain `/api/state_ui_manifest` + `/api/ui_config` (the page showed "State UI manifest unavailable").

| Area | Source | Component tests |
| --- | --- | --- |
| `versionNavState` position order, empty / no-current, disabled ends, `disabled` prop | `ArtifactVersionNav.tsx` | new **`test_ArtifactVersionNav.test.tsx`** (5) |
| AC1 / AC2 on the routed page (typing → 0 PUT, blur → 1 PUT, unchanged blur → 0) | `ArtifactEditor.tsx` via `ArtifactsBaseResumeContent` | **`AST-1577 / AST-2068: wires bodyShape resume_content; blur PUTs base_resume leaf once (§6c AC1/AC2)`** — [`pages.md`](pages.md) § AST-2068 |
| AC4 Base Resume Content arrows (3 of 3 → 1 of 3, re-hydrate, ends disabled, no body PUT) | same | **`AST-2068 AC4: Base Resume Content arrows…`** |
| AC4 JAR cover letter via job route + failed move → toast, body unchanged | `ArtifactEditor.tsx` (`shapesKey` + `jobPersistence`) | **`AST-2068 AC4: JAR cover letter arrows step back via the job route…`** |
| AC4 + AC2 Do Job Criteria: V01 steps alone, V02 untouched; unchanged blur → no PUT | `ArtifactEditor.tsx` (rubric criteria) | **`AST-2068 AC4/AC2: one criterion steps back alone…`** (`test_ArtifactsDoJobCriteria.test.tsx`) |
| AC4 Bio Summary + save-before-move (draft → save v3 → step back to v2) | `ContextTextPage.tsx` | **`AST-2068 AC4: Bio Summary unsaved draft saves before a move…`** (`test_CandidateBioSummary.test.tsx`) |

**Baseline:** the full Vitest run shows 51 failures, against 52 on this tree with AST-2068's three components reverted. None of the 51 is in this file set. AC3 (`AUTOSAVE_MS` gone) is a grep gate. Frontend has no branch locks (§6b).

**Manifest (test-child):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_ArtifactVersionNav.test.tsx \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  ../../../tests/component/frontend/components/test_ContextTextPage.test.tsx \
  ../../../tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx \
  ../../../tests/component/frontend/pages/test_ArtifactsDoJobCriteria.test.tsx \
  ../../../tests/component/frontend/pages/test_CandidateBioSummary.test.tsx
cd src/ui/frontend && npx tsc -b --noEmit
# AC3 grep gate — expect no output
git grep -n "AUTOSAVE_MS" -- src/ui/frontend/src/components/ArtifactEditor.tsx
```

**Pass criterion:** Vitest 77/77 on the six files; `tsc` clean; grep empty. Not the zero-arg harness.

### AST-2075 · AST-2028 (bug — skipped job's run panels show only RESPONSE)

**Parent:** [AST-2028](https://linear.app/astralcareermatch/issue/AST-2028). **Publish:** `origin/sub/AST-2028/AST-2075-skipped-job-run-panels`. Plan: `docs/features/agent/ast-2031-job-run-modal-requests-entity-scoped-agent-data.md` § Bug: AST-2075. With `entityId`, `BatchAgentDataPanes` always shows SYSTEM / NO_CACHE / TASK / RESPONSE tabs, a single `CACHE` stand-in only when SYSTEM and every `CACHE_*` row are missing (D1-2075), opens on SYSTEM, and fills missing tabs with `No agent_data found for this part of the call — it has aged out or was never stored.`; batch-wide (no `entityId`) tabs and empty state unchanged.

| Area | Source | Component tests |
| --- | --- | --- |
| **[bug-repro]** RESPONSE-only entity run → `SYSTEM, CACHE, NO_CACHE, TASK, RESPONSE`, placeholder text, real RESPONSE content | `BatchAgentDataModal.tsx` (`BatchAgentDataPanes`) | **`test_BatchAgentDataModal.test.tsx`** — **`BatchAgentDataPanes — AST-2075 … [bug-repro] RESPONSE-only entity run …`** |
| SYSTEM present + no `CACHE_*` → no CACHE tab · zero rows → five placeholder tabs, no batch empty state | same | **`… present SYSTEM with no CACHE_* rows …`** · **`… entity run with no rows at all …`** |
| Guards: real `CACHE_*` rows keep their tabs · batch-wide tabs + empty state unchanged | same | **`… real CACHE_* rows keep their own tabs …`** · **`… batch-wide (no entityId) unchanged …`** |

**Broken / obsolete (rewritten):** the § AST-2031 `BatchAgentDataPanes` mock returned a single `NO_CACHE` row and read it through the active pane; entity mode now opens on SYSTEM (placeholder when absent). The mock row is now `SYSTEM`, so `entityId → encoded entity_id on agent data only` and `changing entityId refetches the scoped agent data` keep asserting the scoped URL before and after the fix.

**Red / green:** 3 AST-2075 nodes red on the pre-fix tree (`bef2597c1`, tabs built only from present rows); 2 guards + rewritten AST-2031 nodes green there. Item 1 all green (59 pass, 1 name-skipped) against the plan's Proposed change applied in a throwaway tree (not committed — `test-fix` confirms on the real fix).

## QA test manifest — AST-2075

1. **Repro + regressions (Vitest):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_BatchAgentDataModal.test.tsx \
  ../../../tests/component/frontend/components/test_JobDetailModal.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx \
  --testNamePattern='^(?!.*null listing_href)'
```

2. **[bug-repro] flip:** `BatchAgentDataPanes — AST-2075 missing-row placeholder tabs > [bug-repro] RESPONSE-only entity run → SYSTEM/CACHE/NO_CACHE/TASK placeholders + RESPONSE` — red pre-fix, green after `make-fix`.
3. **Scope gate:** `git diff origin/dev...origin/sub/AST-2028/AST-2075-skipped-job-run-panels -- src/core/ src/data/ src/ui/api/` shows no AST-2075 change; `npx tsc -b --noEmit` clean.

### AST-2082 · AST-2046 (split pane, print preview / thumbnail, fullscreen modal)

**Publish:** `origin/sub/AST-2046/AST-2082-split-pane-preview`. These are primitives only, and nothing mounts them yet (wiring belongs to **AST-2084**). New `SplitPanePage.tsx` lays out left | 6 px divider | right and fills its parent; the left panel starts at `calc(50% - 3px)`. Dragging uses `mousedown` on the divider plus `mousemove`/`mouseup` on `window`. The width is clamped to `[0, container − 6]`, and while dragging the panels get `pointer-events: none` and the root gets `user-select: none`. Unmounting mid-drag removes the listeners. New `PrintPreview.tsx` shows a `srcDoc` iframe of the builder print HTML, the builder's error text on failure, and an 816×1056 page scaled to 0.25 in thumbnail mode (204×264, `pointer-events: none`, clicks go to `onClick`). It refetches once per `refreshKey` change, but not when the caller passes a new target object with the same `kind`/`id`. `Modal` gains `size="fullscreen"`: inline styles make the card 100vw × 100vh and borderless, and the body unpadded with `overflow: hidden`. The `wide` and default sizes have no inline styles.

| Area | Component tests |
| --- | --- |
| AC2 divider drag (+100 px → left +100 px; right panel `flex: 1`); clamp; release; listener cleanup | new **`tests/component/frontend/components/test_SplitPanePage.test.tsx`** (5). jsdom has no layout, so `getBoundingClientRect` is stubbed (root 1000 px, left 497 px). |
| AC3 iframe `srcDoc` equals the GET body for all three targets; error text; refetch rules; stale response after unmount; thumbnail | new **`tests/component/frontend/components/test_PrintPreview.test.tsx`** (8). Mocks `lib/api`, so it goes through the real `printHtml.ts`. |
| Fullscreen modal size; wide/default unchanged | **`test_Modal.test.tsx`** + 2 (`AST-2082: …`). The existing 8 are unchanged and green. |
| Route table / errors / popup helper | [`lib.md`](lib.md) § AST-2082 |

**AC1 (spans the content area):** jsdom can't measure layout. This ticket covers what it can: the root is `100%`×`100%`, and the fullscreen card is `100vw` with no border. Proving it end to end on the mounted surfaces is **AST-2084**'s job.

**Broken / obsolete:** none. A full Vitest diff against the dev-product baseline gives the same 50 failures on both trees; they predate this ticket and include the modal/page suites. No routed page is touched, so §6c doesn't apply. No integration scenario covers the frontend.

## QA test manifest — AST-2082

1. **New + revised (Vitest, 31 tests):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/lib/test_printHtml.test.ts \
  ../../../tests/component/frontend/components/test_PrintPreview.test.tsx \
  ../../../tests/component/frontend/components/test_SplitPanePage.test.tsx \
  ../../../tests/component/frontend/components/test_Modal.test.tsx
```

2. **Regression:** in the full `npm run test:component`, AST-2082 must add **no** new failure. The baseline has 50 failures on the `origin/tests` + dev-product tree, all from other tickets.
3. **Build gates:** `cd src/ui/frontend && npx tsc -b --noEmit` and `npm run lint` must be clean on the four product files.

**Pass criterion:** item 1 is 31 passed, and items 2–3 hold. This is a narrowed run, not the zero-arg harness.

### AST-2083 · AST-2046 (resume content editor — rows, autosave, compare, print)

> **AST-2122:** the theme-token gate moved to **`tests/component/frontend/test_AppCss.test.tsx`** (5 cases; page cases deleted). Use that path in place of `pages/test_AdminThemeExamples.test.tsx` below.

**Publish:** `origin/sub/AST-2046/AST-2083-resume-editor`. New `ResumeContentEditor.tsx` (base or job target) and `ResumeSectionRow.tsx`; App.css §10e2; the experience job header gets `resume-section-title`. Nothing mounts the editor yet (that's **AST-2084**), so tests render it directly. Structure comes from the `resume_structure` GET and bodies from the entity GET hydrate. Saves send only the half that changed. Base saves are one `PUT /api/candidates/<id>/data`. Job saves are a `job_resume_structure` PUT, then a `job_resume` PUT. Saves are serialized, and a failed save stays dirty and retries on the next field exit.

| Area | Component tests |
| --- | --- |
| AC4/AC5: typing sends nothing; field exit sends one PUT and one `onSaved`; nothing dirty → no PUT; no Save/Cancel; a failed save toasts, then retries; unmount flushes; load error | new **`tests/component/frontend/components/test_ResumeContentEditor.test.tsx`** (37 total) |
| AC6/AC8/AC13: collapsed `Label: value`; tooltip, label and font from `body_format_details`; flow glyph tooltip from the catalog (incl. `hidden_flow_label`); contact row has no format; arrows disabled at the ends; delete only on non-required rows; search over title and content (incl. experience text) | same file. The catalog fixture uses `FX …` strings that exist nowhere in `src/`, so any label on screen proves it is config-driven |
| AC9/AC12: format options from the catalog (incl. `line`); experience format locked; `line` → `<input>`, prose → `<textarea>`; format/flow/Job Edit/accent save immediately; Hidden ↔ policy; required rows have no Hidden; label saves on field exit | same file |
| AC7/AC10/AC11: Add Section (bottom, expanded, default format, content locked, search cleared); a blank new row is never sent; labeled → saved last, adopts the server's slug id and unlocks; delete confirm cancel/OK; arrow and drag reorder | same file (`window.confirm` fallback; no `UserPromptProvider`) |
| AC14 (job only): differs / NEW SECTION / SECTION REMOVED placement after the nearest kept base row; base refetched on every toggle-on; Add → structure PUT then `job_resume` PUT with base content; compare error toast; job body-only and structure-only saves | same file |
| AC15 Print: flushes before `fetchPrintHtml`; base vs `job_resume` target; fetch error and blocked popup toast | same file (`lib/printHtml` mocked; route table in [`lib.md`](lib.md) § AST-2082) |
| AC16: job header color equals the section header color | same file. It injects the two App.css rules (`--heading` pinned) and checks the role label rule sets no color of its own |
| Theme-token gate on the new §10e2 rules | existing **`pages/test_AdminThemeExamples.test.tsx`** (8). **2 red: product bug.** See below |

**Product bug (returned to the engineer):** §10e2 in `354a93fa4` uses `var(--accent-gold)` on `.resume-section-new` and `.print-preview-thumb:hover`. Current dev retired that token in favor of `--accent-contrast`, so it's undefined there. §10e2 also hard-codes `background: #fff` on `.print-preview-thumb` outside the token blocks. The existing AST-2047/AST-2049 gates fail on the synced tree: `no hex or non-black rgba outside token blocks…` (`#fff`) and `AST-2049: no hex in .ts/.tsx source and every var(--x)…` (`App.css: --accent-gold`). These are App.css-only fixes. The tests are correct and stay as they are.

**Broken / obsolete:** none from the tests' side. A full Vitest diff (dev-product `origin/tests` vs the synced sub) shows only the two theme gates above as new failures, plus `test_CandidateContext` › *restores the persisted selection's Full Name after load*. That test also fails alone on the baseline tree, so it's order-dependent and predates this ticket. Mutation check: switching body or label edits to save per keystroke turns 3 tests red, and dropping the format font turns 1 red. No routed page is touched (wiring is AST-2084), so §6c doesn't apply. The retired `.structure-authoring-*` CSS has no CSS assertions. The markup tests (`test_ArtifactEditor`, `test_ArtifactsBaseResumeContent`) are unchanged and green.

## QA test manifest — AST-2083

1. **New + affected (Vitest, 47 tests):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_ResumeContentEditor.test.tsx \
  ../../../tests/component/frontend/components/test_ExperienceJobsEditor.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminThemeExamples.test.tsx
```

2. **Regression:** in the full `npm run test:component`, AST-2083 must add **no** new failure beyond item 1's two theme reds before the fix (`test_CandidateContext` title-restore is pre-existing/order-dependent).
3. **Build gates:** `cd src/ui/frontend && npx tsc -b --noEmit` and `npm run lint` must be clean on the four product files.

**Pass criterion:** item 1 is 47 passed (the two `test_AdminThemeExamples` reds turn green once the App.css token fix lands), and items 2–3 hold. This is a narrowed run, not the zero-arg harness.

### AST-2114 · AST-2046 (bug: search shows every Experience job, not just the matches)

**Publish:** `origin/sub/AST-2046/AST-2114-search-experience-subelements`. Fix lane: a qa-fix repro after fix-board said TESTS: REVISE. In the plan-fix (`docs/features/interface/ast-2083-resume-editor.md` § Bug: AST-2114), `ResumeContentEditor` computes a per-job match set (`visibleJobs`) and passes it through `ResumeSectionRow` to a new `ExperienceJobsEditor` `visible` prop. This is view-only: the body array, the indexes and the saves are untouched. Add role hides while the filter is on. A section-title match or an empty query shows every job. `ArtifactEditor` passes no `visible`, so it's unchanged.

| Behavior | Test |
| --- | --- |
| Two-job base: `acme` → only "Acme, Lead"; `BILLING` (accomplishment) → only Globex; `exper` (title hit) and empty → both; Add role hidden only while filtered; no PUT | **`test_ResumeContentEditor.test.tsx`** `AST-2114 … [bug-repro] a job-text match shows only matching jobs…` (new) |
| Editing a filtered job saves the full array, the hidden job included; filtering alone sends nothing (AC4 still holds) | same file, `editing a filtered job saves the full array…` (new guard; green before and after) |
| `visible={new Set([1])}`: only index 1 renders; edit / Move up / Remove act on the original index 1 in the full list; no Add role | **`test_ExperienceJobsEditor.test.tsx`** `AST-2114 … [bug-repro] renders only visible indexes…` (new; props cast so it compiles before the fix) |

**Repro status:** on the pre-fix sub, exactly the 2 `[bug-repro]` cases are red. One fails with `expected ['Acme, Lead', 'Globex, Engineer'] to deeply equal ['Acme, Lead']`, the other because First still renders. The other 40 are green. With the plan's change temporarily applied to the three product files, then reverted (not committed), all 42 pass. `test-fix` must confirm the same flip on Katherine's real fix. The existing AST-2083 search case checks rows only, with a one-job fixture, and is unaffected.

## QA test manifest — AST-2114

1. **Repro + neighbors (Vitest, 42 tests):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_ResumeContentEditor.test.tsx \
  ../../../tests/component/frontend/components/test_ExperienceJobsEditor.test.tsx
```

2. **Build gates:** `cd src/ui/frontend && npx tsc -b --noEmit` and `npm run lint` are clean on the three product files.

**Pass criterion:** item 1 is 42 passed, including both `AST-2114 [bug-repro]` cases, and item 2 holds.

### AST-2084 · AST-2046 (wire resume surfaces — base page, job edit modal, thumbnails; ArtifactEditor resume mode retired)

**Publish:** `origin/sub/AST-2046/AST-2084-wire-resume-surfaces`. Base Resume Content is now `SplitPanePage` with `ResumeContentEditor` (base) on the left and `PrintPreview` (base) on the right. The preview refreshes on the editor's `onSaved`. New `JobArtifactEditModal` is a stacked full-screen `Modal` holding a split pane: the job resume uses `ResumeContentEditor` (job) + the `job_resume` preview, and the cover letter uses `ArtifactEditor` (shapes + job persistence, `craft_cover_letter`) + the `cover` preview. JAR's Artifacts tab shows a `PrintPreview` thumbnail for each `preview_thumbnail` tab that has content (click → modal), plus Edit on the job resume. Closing the modal reloads the report. Print Resume goes through `printHtml` with no structure persist. `ArtifactEditor`'s resume structure mode is removed.

| Area | Component tests |
| --- | --- |
| AC4: thumbnails only for generated artifacts; no inline editors; click / Edit → stacked modal over the report; cover thumbnail → cover editor + cover preview; close reloads; nothing generated → no thumbnails and no print fetches | **`test_JobAnalysisReportModal.test.tsx`**: 4 new `AST-2084:` cases replace AST-1476 / AST-1489 / AST-1490 and the old "populated Artifacts shows editable Job Resume" case. The empty-Artifacts case gains the no-thumbnail assert |
| Print Resume via the shared helper, no candidate `resume_structure` GET/PUT | same file, `AST-2084: Print Resume…`. AST-1546 / AST-1350 now seed `job_resume` (AST-1593 key). They were red before this ticket and are green now |
| Modal wiring: closed when `tab` is null; resume vs cover branch; preview `refreshKey` bumps on each editor's `onSaved`; stacked, no footer (width: 80vw overlay since **AST-2115**, below); Close → `onClose` | new **`tests/component/frontend/components/test_JobArtifactEditModal.test.tsx`** (4). Children are stubbed because they have their own suites |
| Base page (§6c render, AC2/AC3/AC5 source gates) | [`pages.md`](pages.md) § AST-2084 |
| `ArtifactEditor` rubric/criteria/shapes paths unchanged | **`test_ArtifactEditor.test.tsx`**: 22 remaining cases green |

**Fixture drift fixed:** `fixtures/stateUiManifestFixture.ts` `report_artifact_tabs` now carries `preview_thumbnail` (resume/cover `true`, application `false`), mirroring `JOBS_RECOMMENDED_ARTIFACT_TABS` since AST-2081. Without it every JAR test silently stayed on the inline-editor path.

**Retired (behavior removed by this ticket; replacement coverage in `test_ResumeContentEditor` § AST-2083 and the cases above):**
- `test_ArtifactEditor.test.tsx`: 19 resume-structure-mode cases (`useCandidateResumeStructure` / `structureSections` / `bodyShape` renders): AST-1200 expand-one, AST-1351 ×2, AST-1375 ×4, AST-1382, AST-1476, AST-1480 ×2, AST-1490, AST-1577, AST-1593, AST-2051 ×3 (base structure), AST-2068 Regenerate-blur, AST-996/1351 experience array, plus "loads fixed tabs from structureSections". The now-unused helpers went with them (`mockBaseResumeStructure`, `renderBaseResumeStructure`, `generateHandler`, `clickRegenerateAndConfirm`, `deferred`). The three surviving job-persistence cases had the dead resume-mode props stripped; they exercise generic key-driven autosave.
- `test_JobAnalysisReportModal.test.tsx`: AST-1476 structure authoring, AST-1489 print auto-persist, AST-1490 reorder-then-print.
- `test_ArtifactsBaseResumeContent.test.tsx`: all 15 old cases (structure tabs, accent bar, structure authoring, the page's own Print and Generate). See [`pages.md`](pages.md) § AST-2084.

**Regression:** comparing the full Vitest suite against ftr product shows **0 new** failures (1093 tests, 46 failing, all pre-existing) and 2 fixed (AST-1546 / AST-1350). Mutation check: dropping the page's preview bump, the JAR thumbnail branch, or the modal's `stacked` flag turns 6 cases red. **AC1** (edge-to-edge layout) can't be measured in jsdom. What it can show: the split pane root is `100%` (AST-2082 `test_SplitPanePage`). The job edit modal's card width is now pinned by **AST-2115** (80vw overlay, not edge-to-edge). No integration scenario covers these surfaces.

## QA test manifest — AST-2084

1. **New + revised (Vitest, 89 tests):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx \
  ../../../tests/component/frontend/components/test_JobArtifactEditModal.test.tsx \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx
```

2. **Regression:** in the full `npm run test:component`, AST-2084 must add **no** new failure (46 pre-existing on the synced sub, from other tickets).
3. **Build gates:** `cd src/ui/frontend && npx tsc -b --noEmit` and `npm run lint` must be clean on the four product files.

**Pass criterion:** item 1 is 89 passed, and items 2–3 hold. This is a narrowed run, not the zero-arg harness.

### AST-2115 · AST-2046 (bug: job edit modal 80% width, over the page)

**Publish:** `origin/sub/AST-2046/AST-2115-job-modal-80-width`. Fix lane: a qa-fix repro after fix-board said TESTS: REVISE. In the plan-fix (option B, `docs/features/interface/ast-2084-wire-resume-surfaces.md` § Bug: AST-2115), `Modal` gains `size="overlay"`: the card is inline 80vw × 90vh (`max*` matching), with no border or radius override, so the `.modal-card` chrome stays and it reads as sitting over the page. The body uses the same unpadded, `overflow: hidden` style as fullscreen. `JobArtifactEditModal` switches from `fullscreen` to `overlay`, and keeps `stacked` and no footer. The `fullscreen` size itself is unchanged, and so is its AST-2082 case.

| Behavior | Test |
| --- | --- |
| `size="overlay"` card is 80vw × 90vh; border and radius not overridden; body unpadded and `overflow: hidden`; no `--wide` class | **`test_Modal.test.tsx`** `AST-2115 [bug-repro]: size="overlay"…` (new) |
| Job resume modal card is 80vw × 90vh, border kept, body unpadded (it replaces the AST-2084 `100vw` assert) | **`test_JobArtifactEditModal.test.tsx`** `AST-2115 [bug-repro]: job resume opens a stacked 80%-width…` (rewritten AST-2084 case) |

**Repro status:** on the pre-fix sub, exactly these 2 cases are red (`expected '100vw' to be '80vw'` and `expected '' to be '80vw'`); the other 13 are green. With the plan's change temporarily applied to `Modal.tsx` and `JobArtifactEditModal.tsx`, then reverted (not committed), all 15 pass. `test-fix` must confirm the same flip on Ada's real fix. jsdom can't measure the visual "over the page" read; the inline style plus the kept card chrome is the proxy.

## QA test manifest — AST-2115

1. **Repro + neighbors (Vitest, 15 tests):**

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_Modal.test.tsx \
  ../../../tests/component/frontend/components/test_JobArtifactEditModal.test.tsx
```

2. **Gate:** `git grep -n 'size="fullscreen"' -- src/ui/frontend/src` is empty (plan-fix gate).
3. **Build gates:** `cd src/ui/frontend && npx tsc -b --noEmit` and `npm run lint` are clean.

**Pass criterion:** item 1 is 15 passed, including both `AST-2115 [bug-repro]` cases, and items 2–3 hold.

### AST-2128 · AST-2101 (shared GradeMark — one grade mark, hidden shape SVG)

**Publish:** `origin/sub/AST-2101/AST-2128-shared-grade-mark`. A new `components/GradeMark.tsx` replaces the three local `gradeDot` helpers (`lib/recommendedJobReport.tsx`, `pages/JobsProcessing.tsx`, `pages/JobsSkipped.tsx`) and the inline span in `AgentAnalysisHeader.tsx`. The mark is `span.grade-dot.dot-<g>[.grade-dot-letterless][role=img][aria-label=<grade>]`. It holds an `svg[viewBox="0 0 100 100"][aria-hidden][display=none] > path[d]` with the brief's shape for its grade, followed by the bare letter text, which is omitted when letterless. No CSS changes in this ticket, so there's no visual change. Sibling **AST-2129** reveals the SVG in the Shapes themes.

| Behavior | Test |
| --- | --- |
| A/B/C/D/F/X × lettered/letterless: `getByRole("img", { name: <g> })` finds the mark; the SVG is `aria-hidden="true"` and has `display="none"`; its one path `d` equals the **brief literal** (pinned in the test, not imported) (AC 6) | **`test_GradeMark.test.tsx`** `GradeMark — AST-2128` `… img role named by the grade …` (new, 12 cases) |
| `textContent` is the single letter (lettered) or `""` (letterless) (AC 7) | **`test_GradeMark.test.tsx`** `… textContent is the single letter …` (new, 12 cases) |
| `grade-dot dot-<g>` classes kept; `grade-dot-letterless` only when letterless | **`test_GradeMark.test.tsx`** `… keeps the grade-dot classes …` (new, 12 cases) |
| Tooltip becomes `title`; an empty or missing tooltip leaves no `title`; lowercase grade looks up the shape case-insensitively; an unknown grade renders with no SVG | **`test_GradeMark.test.tsx`** (new, 3 cases) |
| Call sites are unchanged for markup readers (AC 7) | Existing, **unedited**: `lib/test_recommendedJobReport`, `pages/test_JobsProcessing`, `pages/test_JobsSkipped`, `pages/test_JobsRecommended`, `components/test_JobAnalysisReportModal`, `components/test_JobDetailModal`, `components/test_AgentAnalysisHeader` |

jsdom ignores the SVG `display` presentation attribute, so the test pins the attribute, not visibility. Computed `display: none` on Light/Dark is parent AC 9, owned by **AST-2129**.

**Routed pages (§6c):** `JobsProcessing.tsx` and `JobsSkipped.tsx` changed render only. Their existing page Vitests render the page with first-paint mocks and stay in the manifest. There are no filter or date changes.

**Broken / obsolete this pass:** none caused by this diff. **Pre-existing red, not this ticket** (identical on pre-change tip `9a267a790` and on `origin/dev`), excluded by name below and **not revised here**:
- `test_AppCss` `no hex or non-black rgba outside token blocks… (AC5, App.css half)` and `AST-2049: no hex in .ts/.tsx source… (AC9, epic-wide)` both fail on `--tp-lvl`. That property came from `origin/dev` `5f4850a20` (Task Performance page). It's declared on `.tp-*` classes with `hsla()` tints, not in a token block. The `test_AppCss` revision is sibling **AST-2129**'s scope ("selector-list blocks and twin exemptions"), and the product fix would be an `App.css` change, which this child's Boundaries forbid. **Child AC 9's `test_AppCss` clause is held open on this** until Susan picks one: a test exemption for locally declared properties, or tints moved into the token blocks.
- `test_JobDetailModal` `AST-1695 listing_href > read-only: null listing_href → no Link <a>…`: this is the same obsolete AST-1695 expectation already logged at **AST-1865**. It's superseded by **AST-1704** (http(s) `job_link` is a link) and the `origin/dev` `82fcbd6c` fix.

**Integration:** none. No scenario reads grade-mark markup.

## QA test manifest — AST-2128

1. **New + AC 7 call-site suites (Vitest, 220 tests: 217 run, 3 excluded by name):**

```bash
cd src/ui/frontend && T=../../../tests/component/frontend && npx vitest run --config vite.config.ts \
  $T/components/test_GradeMark.test.tsx \
  $T/lib/test_recommendedJobReport.test.tsx \
  $T/pages/test_JobsProcessing.test.tsx \
  $T/pages/test_JobsSkipped.test.tsx \
  $T/pages/test_JobsRecommended.test.tsx \
  $T/components/test_JobAnalysisReportModal.test.tsx \
  $T/components/test_JobDetailModal.test.tsx \
  $T/components/test_AgentAnalysisHeader.test.tsx \
  $T/test_AppCss.test.tsx \
  -t '^(?!.*(null listing_href → no Link|no hex or non-black rgba outside token blocks|AST-2049: no hex in \.ts/\.tsx source)).*$'
```

2. **Pytest (AC 9):** `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst2047ThemeRegistry` (5 passed) and `python -c "import src.utils.config"`.
3. **One mark (AC 8):** `git grep -n 'grade-dot dot-' -- src/ui/frontend/src` hits only `components/GradeMark.tsx`, and `git grep -n 'gradeDot(' -- src/ui/frontend/src` is empty.
4. **Build (AC 9):** `cd src/ui/frontend && npx tsc -b --noEmit` exits 0.

**Pass criterion:** item 1 shows 217 passed and 3 skipped, with all 39 `GradeMark — AST-2128` cases green, and items 2–4 hold. Run without `-t`, item 1 shows exactly the 3 pre-existing failures named above and no others.
