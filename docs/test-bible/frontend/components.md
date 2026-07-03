# Components

**Test tree:** `tests/component/components/`

### AST-427 · AST-426

**`CollapsiblePanel`** shared by **`AdminTaskPrompts`** (Manage Tasks list + edit modal) and **`ArtifactEditor`** (criteria). Zero expanded sections: list phases and edit modal (`editOpenPanel === null` on collapse, same pattern as criteria `expandedTabId === ""`).

| Area | Source | Component tests |
| --- | --- | --- |
| Collapsible primitive | `src/ui/frontend/src/components/CollapsiblePanel.tsx` | `tests/component/frontend/components/test_CollapsiblePanel.test.tsx` |
| Manage Tasks | `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx` |
| Criteria regression | `src/ui/frontend/src/components/ArtifactEditor.tsx` | `tests/component/frontend/components/test_ArtifactEditor.test.tsx` (unchanged gate) |

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
| Agent story phase + display label | `src/core/roster.py` (`get_entity_agent_story`) | `tests/component/core/test_roster.py` (`TestEntityAgentStory::test_ast520_agent_story_phase_and_print_label`) |
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
| **AST-612** | React Stytch login gate; Bearer **`session_jwt`** on **`api()`**; **`AdminRoute`** on `/admin/*`; non-admin candidate selector lock | `src/ui/frontend/src/lib/api.ts`, `src/ui/frontend/src/contexts/AuthContext.tsx`, `src/ui/frontend/src/components/{RequireAuth,AdminRoute,NavigationShell}.tsx`, `src/ui/frontend/src/contexts/CandidateContext.tsx`, `src/ui/frontend/src/routes.tsx` | `tests/component/frontend/lib/test_api.test.ts`; `tests/component/frontend/contexts/test_AuthContext.test.tsx`; `tests/component/frontend/components/test_RequireAuth.test.tsx`; `tests/component/frontend/components/test_AdminRoute.test.tsx`; `tests/component/frontend/components/test_NavigationShell.test.tsx`; `tests/component/frontend/contexts/test_CandidateContext.test.tsx` |
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
