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
| Analysis / job surfaces | `AgentAnalysisHeader.tsx`, job pages | `tests/component/frontend/components/test_AgentAnalysisHeader.test.tsx`, `tests/component/frontend/pages/test_ArtifactsCompanyWatchCriteria.test.tsx`, `test_ArtifactsJobListCriteria.test.tsx`, `test_ArtifactsJobDescCriteria.test.tsx`, `test_ArtifactsGetJobCriteria.test.tsx`, `test_ArtifactsDoJobCriteria.test.tsx`, `test_ArtifactsLikeJobCriteria.test.tsx` |

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
| **AST-647** | `UI_CONFIG` defaults; shared `listTableLayout` / `uiConfig` / `ListTableTruncatedCell`; ListPage freeze + truncate; **AdminScheduledActions** bespoke table with `frozenDataColumns={3}` | `src/utils/config.py`, `src/ui/frontend/src/lib/{listTableLayout,uiConfig}.ts`, `ListPage.tsx`, `ListTableTruncatedCell.tsx`, `App.css`, `AdminScheduledActions.tsx` | `tests/component/frontend/lib/test_listTableLayout.test.ts`; `tests/component/frontend/components/test_ListTableTruncatedCell.test.tsx`; `tests/component/frontend/components/test_ListPage_listTableLayout.test.tsx`; `tests/component/frontend/components/test_ListPage.test.tsx` (api mock + `/api/system/ui_config` — **uiConfig** extract regression); `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` — **`AST-647: phase table freezes first three data columns`** + candidate-filter test fixes; `tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_ui_config_includes_list_table_layout_defaults` |
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

**Error toast diagnostics:** **`Toast.tsx`** — error variant defaults to **15s** dismiss, **click-to-copy** multi-line diagnostic bundle (route + optional candidate id from context; optional **`diagnostics`** from **`ApiError`**). Success/info unchanged (~3s, non-interactive). Helpers in **`toastDiagnostics.ts`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Toast UX + copy bundle | `src/ui/frontend/src/components/Toast.tsx`, `src/ui/frontend/src/lib/toastDiagnostics.ts`, `App.css` | `tests/component/frontend/components/test_Toast.test.tsx` — **AST-779** describe (15s error dismiss, 3s success, click-copy + copied feedback, `.toast-error-clickable` hint) |
| Representative ApiError wiring | `AdminAgentPrompts.tsx`, `CandidateProfile.tsx` | Existing page tests cover error toast text paths; **no new page manifest** — Toast auto-context satisfies AC 3–4 for pages passing `{ text, variant: "error" }` only |

**AST-779** narrowed run (Vitest only):

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_Toast.test.tsx
```

---

### AST-783 · AST-756

**`RepoJsonDivergenceBanner`:** fetches **`/api/admin/repo_json/status`**, shows gold warning when `diverged`, **Revert to file** via **`useUserConfirm`** danger dialog → **`POST /api/admin/repo_json/revert/<tableKey>`**; refetches on `refreshToken` prop from parent pages.

| Area | Source | Component tests |
| --- | --- | --- |
| Banner hide/show + revert flow | `src/ui/frontend/src/components/RepoJsonDivergenceBanner.tsx` | `tests/component/frontend/components/test_RepoJsonDivergenceBanner.test.tsx` |

---

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

**AST-1350:** JAR **Print Resume** fetch-then-blob + toast exact API `error` (no `window.open` on failure). Cover Letter print unchanged. Base Resume / Session Open HTML already toast API errors — **`test_ArtifactsBaseResumeContent`** / **`test_AdminSessionResumePaste`**. Core/API: **`docs/test-bible/core/builder.md`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Fetch-then-blob success + unsupported toast | `JobAnalysisReportModal.tsx` | **`test_JobAnalysisReportModal.test.tsx`** — **Print Resume fetch-then-blob…**, **AST-1350: Print Resume unsupported toast — no tab** |

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx \
  --testNamePattern="Print Resume|AST-1350"
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
| Array Save + header + structure Save [bug-repro] | `ArtifactEditor.tsx` | **`test_ArtifactEditor.test.tsx`** — AST-996/1351/1375 revised; **`AST-1382 [bug-repro]: content Save bundles resume_structure…`** |

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
3. Regression (same files): existing Skip / AST-1302 / AST-1410 cases

**AST-1477** narrowed run (Vitest — from `src/ui/frontend/`):

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_CandidateJobRowActions.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx \
  --testNamePattern="AST-1477|AST-1302|AST-1410|Skip"
```

**Pass criterion:** Vitest green on manifest lines — not zero-arg harness / branch-lock gate.

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
