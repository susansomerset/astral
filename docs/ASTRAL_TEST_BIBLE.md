This is the reference to existing tests, including unit/component and integration testing.

**Owner:** **Betty** — maintained via **`qa-astral`**: use it to decide which **existing** tests apply to an issue (manifest-only is OK when coverage already matches), which tests a change **breaks** and must be revised, and when to **append or correct** this file so the map stays true. **Engineers do not commit** this file or other **test-tree** paths — see **`docs/ASTRAL_TEAM_WORKFLOW.md`** § Test ownership.

## 2. Where tests live

- **Component tests:** `tests/component/` mirrors `src/` (Python under layer folders; React under `tests/component/frontend/`).
- **Integration tests:** `tests/integration/` is a placeholder only until a separate program opens integration work.
- **Data layer carve-out (§4a):** `tests/component/data/database/` holds cluster files for `src/data/database.py`; see `tests/component/data/database/_README.md`.

## 4a. `database.py` cluster tests

- Keep `src/data/database.py` as one module; split the **test tree** under `tests/component/data/database/` (`test_<cluster>.py`, not `test_database_<cluster>.py`).
- Shared real SQLite fixtures live in `tests/component/data/conftest.py` (`sqlite_in_memory`, `seeded_db`, `db_factory`).
- Thin import smoke stays in `tests/component/data/test_database.py`.

## 6. Branch coverage standard

### 6a. Python (backend + Flask UI/API modules under component test)

- Target **100% branch coverage** for each file committed to **`LOCKED_AT_100`** (`scripts/testing/check_per_file_coverage.py`).
- List intended branches in comment blocks above each `class Test…` (see `tests/component/core/test_tracker.py` when present).
- When such a file reaches 100%, update **§7.12**, the **§7.13** tables (branch lock column), and **`LOCKED_AT_100`** in the same commit.
- **`pragma: no cover`** is allowed only with a short in-file note and bible mention when a branch is impractical to hit in component tests (AST-390: `formatting.py` DOM sibling union + JSON heal edge paths; AST-391: `playwright.py` browser session/crawl paths and `anthropic.py` SDK/heal edge paths; AST-394: `api_admin.py` `update_dtask` `score_floor` elif false exit arc; **AST-471**: `gazer.py` `process_gaze_board_batch` debug-only `_log.debug` stanza; `roster.py` unreachable `job_ids` index guard after length parity).

### 6b. Frontend (Vitest + RTL under `tests/component/frontend/`)

- **Risk-based**, not branch-count completeness: Prefer tests that anchor real regressions and user-visible flows over enforcing a percentage per source file (**AST-395**).
- **No** mandated per-file 100% branch targets for `src/ui/frontend/src/**`. **`LOCKED_AT_100` in `scripts/testing/check_frontend_coverage.py` stays intentionally empty** unless Product adopts explicit frontend locks later.
- `./scripts/testing/run_component_tests.sh` still runs Vitest with coverage and invokes `check_frontend_coverage.py`; the gate is **tests passing** plus the checker succeeding with **zero** locked files—not full branch saturation.
- Detailed map: §7.13f.
- **QA manifest rules (Betty — all UI tickets):** §6c.

### 6c. QA manifest rules — routed pages and filter UX (**AST-436** UAT lesson)

Betty applies these when writing the **Tests Ready** manifest (**`qa-astral`** §6). **`test-astral`** must run every manifest line, not only the narrowest path.

**Routed page (required when the ticket changes a top-level React route / page file under `src/ui/frontend/src/pages/`):**

- Manifest **must** include at least one Vitest that **renders that page** via `renderWithProviders` (same pattern as existing `test_*Profile*.tsx`, `test_Admin*.tsx`).
- Mock **every** API the page hits on first paint (typical: `/api/candidates`, `/api/shapes/…`, `/api/ui_config` or `/api/system/ui_config`, route-specific GETs). **Component-only** tests (e.g. `TabbedTextArea.customPanels` alone) **do not** satisfy this rule when the product change is wired on the page.
- **Hooks:** page tests catch Rules-of-Hooks violations that child-only tests miss (conditional `return` before `useMemo` / `useCallback`).

**Filter / date / search-param UX (required when the ticket changes controlled filters bound to URL or immediate refetch):**

- Manifest **must** include interaction coverage, not only “default query string” or “API called with today”:
  - Type a **full** date (multi-digit day/month) without the input resetting mid-keystroke.
  - **Blur** or explicit Apply to commit (when product uses draft-then-commit).
  - **Clear** the default filter and confirm behavior (wide fetch, empty param, or explicit reset — per AC).
- Prefer RTL in `tests/component/frontend/pages/test_<Page>.test.tsx`; manual UAT steps are optional add-ons, not substitutes.

## 7.7 External fixtures

- Shared mocks live in `tests/component/external/conftest.py` (Gmail service, Anthropic client shapes). Core-layer tests should reuse these patterns when external I/O is stubbed.

## 7.7b Core fixtures

- `tests/component/core/conftest.py` sets Gmail env defaults for import-time `gmail.py` checks and provides shared `log_entries` for monitor tests.

## 7.8 Data fixtures

- Real in-memory SQLite files via `tests/component/data/conftest.py` (no sqlite mocks). Set `ASTRAL_DB_DIR` per test and patch `database.DB_PATH` to the temp `astral.db`.
- Component tests run on **Python 3.10+** (see Appendix A).

## 7.12 Per-file branch locks

Python/component modules locked at **100%** branches (enforced by `scripts/testing/check_per_file_coverage.py`). Frontend is out of scope here (**§6b**).

- `src/utils/config.py`
- `src/utils/formatting.py`
- `src/external/anthropic.py`
- `src/external/gmail.py`
- `src/external/playwright.py`
- `src/core/monitor.py`
- `src/core/timesheets.py`
- `src/core/tracker.py`
- `src/core/candidate.py`
- `src/core/gazer.py`
- `src/core/dispatcher.py`
- `src/core/consult.py`
- `src/core/builder.py`
- `src/core/agent.py`
- `src/core/roster.py`
- `src/ui/auth.py`
- `src/ui/server.py`
- `src/ui/api/api_system.py`
- `src/ui/api/api_candidate.py`
- `src/ui/api/api_companies.py`
- `src/ui/api/api_jobs.py`
- `src/ui/api/api_admin.py`

### 7.12b **`LOCKED_AT_100` substrate parity** (**AST-471** handoff)

The full harness **`./scripts/testing/run_component_tests.sh`** (zero args) runs **`check_per_file_coverage.py`** across **`LOCKED_AT_100`**. False reds on hotspots such as **`src/core/agent.py`**, **`src/core/roster.py`**, **`src/utils/config.py`** often mean the engineer’s **`dev-<agent>`** tree holds **different Python substrate** than the **ticket publish replay** (**`orientation-astral` § Integration line discipline**) — e.g. **`origin/dev`** lacks symbols added only on **`dev-<agent>`**, or a **`fix(<Linear-id>):`** commit (**`build-astral`** / **`test-astral`** **§9** replay) was applied only locally and never cherry-picked to **`origin/<publish-ref>`**, while **`qa-astral`** on **`dev-betty`** calibrated branch locks against **`merge origin/sub/…`** plus **`merge origin/dev`**.

Before **`[qa-handoff]`** on missing-test theory alone:

1. **`git fetch origin`**
2. **`git merge origin/dev`**
3. **`git merge origin/<publish-ref>`** for **this** ticket (child **`sub/<parent>/<segment>`**, not **`ftr/<ticket-id>`** unless the authoritative **Git branch** block says standalone **`ftr/`**)
4. Re-run **`./scripts/testing/run_component_tests.sh`**

Cherry-pick any ticket-local **`fix(<same ticket id>):`** product SHAs still missing from **`origin/<publish-ref>`**, then rerun the replay. **`ImportError`** on **`config`** / **`database`** when fast-forwarding **`origin/dev`** toward the **`sub/`** tip means **Susan has not landed prior rollup on `origin/dev`** — unblock integration before treating the harness as flaky.

### 7.12c Prep-uat **`origin/ftr/*`** composite (**AST-539**)

**`prep-uat` §6** runs the **full** harness on a throwaway worktree at **`origin/ftr/<parent-segment>`**. That tip often **trails `origin/dev`** on product APIs while **`tests/component`** on **`dev-betty`** already asserts merged children.

| Symptom on ftr tip | Test-tree response (Betty) |
| --- | --- |
| **`DISPATCH_SCHEDULABLE_TASK_KEYS`**, **`RESUME_SECTION_CATALOG`**, AST-551/552/562 tracker helpers, etc. missing | **`pytest.mark.skipif`** on the asserting class or method (`tests/component/conftest.py` **`_SKIP_UNLESS_DISPATCH_SCHEDULABLE`**, local skips beside the test module) |
| Default **`active_provider`** is **deepseek**; mocks target **`send_to_anthropic`** only | **`tests/component/conftest.py`** env keys; **`tests/component/core/conftest.py`** + **`tests/component/ui/conftest.py`** autouse **`anthropic`** provider |
| Strict **AST-501** envelope on **`evaluate_jd`** / encoded consult mocks | **`_strict_batch_llm_ok`** / **`_llm_failure_envelope`** in **`tests/component/core/test_agent.py`** |
| **`LOCKED_AT_100`** files below 100% branch % on composite product | **`run_component_tests.sh`** sets **`ASTRAL_FTR_COVERAGE_INTEGRATION=1`** when **`HEAD`** is contained in **`origin/ftr/*`**; **`check_per_file_coverage.py`** logs and **does not gate** sub-100 locks (pytest + Vitest still must pass) |

Do **not** weaken **`LOCKED_AT_100`** on **`dev-betty`** / child **`sub/*`** publishes — integration skip is for **parent ftr sanity** only.

## 7.13 Component coverage map (utils)

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/utils/config.py` | `tests/component/utils/test_config.py` | yes |
| `src/utils/formatting.py` | `tests/component/utils/test_formatting.py` | yes |
| `src/utils/auth.py` | `tests/component/utils/test_auth.py` | no |

## 7.13b Component coverage map (external)

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/external/anthropic.py` | `tests/component/external/test_anthropic.py` | yes |
| `src/external/gmail.py` | `tests/component/external/test_gmail.py` | yes |
| `src/external/playwright.py` | `tests/component/external/test_playwright.py` | yes |
| `src/external/stytch.py` | `tests/component/external/test_stytch.py` | no |

**AST-489:** `src/external/google_cse.py` — `tests/component/external/test_google_cse.py` (HTTP mocked; no branch lock). Spike `scripts/spikes/ast489_google_cse_company_search_spike.py` is console-only / live credentials — not a component-test target.

## 7.13c Component coverage map (data)

| Source | Test files | Branch lock |
| --- | --- | --- |
| `src/data/database.py` | `tests/component/data/test_database.py`; clusters under `tests/component/data/database/` | pending |

**AST-524:** `company_search_terms` table cluster — `tests/component/data/database/test_company_search_terms.py` (sync, migration, `last_scan_at` preservation; no branch lock on `database.py`).

**AST-558:** `candidate_intake_session` table — exercised via `tests/component/core/test_intake.py` (real SQLite `seeded_db`; no separate database cluster).

## 7.13d Component coverage map (core)

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/core/monitor.py` | `tests/component/core/test_monitor.py` | yes |
| `src/core/timesheets.py` | `tests/component/core/test_timesheets.py` | yes |
| `src/core/tracker.py` | `tests/component/core/test_tracker.py` | yes |
| `src/core/candidate.py` | `tests/component/core/test_candidate.py` | yes |
| `src/core/gazer.py` | `tests/component/core/test_gazer.py` | yes |
| `src/core/dispatcher.py` | `tests/component/core/test_dispatcher.py` | yes |
| `src/core/consult.py` | `tests/component/core/test_consult.py` | yes |
| `src/core/builder.py` | `tests/component/core/test_builder.py` | yes |
| `src/core/agent.py` | `tests/component/core/test_agent.py` | yes |
| `src/core/roster.py` | `tests/component/core/test_roster.py` | yes |
| `src/core/intake.py` | `tests/component/core/test_intake.py` | yes |

**AST-486 (consult layering):** **`TestTrackerFacades.test_ast486_consult_layer_facades_delegate_to_database`** asserts **`tracker.get_company`**, **`tracker.append_agent_response`**, and **`tracker.list_timesheets`** forward to **`database`** (`consult.py` consumes **`tracker`** only for those paths).

## 7.13e Component coverage map (UI)

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/ui/auth.py` | `tests/component/ui/test_auth.py` | yes |
| `src/ui/server.py` | `tests/component/ui/test_server.py` | yes |
| `src/ui/api/api_system.py` | `tests/component/ui/api/test_api_system.py` | yes |
| `src/ui/api/api_candidate.py` | `tests/component/ui/api/test_api_candidate.py` | yes |
| `src/ui/api/api_companies.py` | `tests/component/ui/api/test_api_companies.py` | yes |
| `src/ui/api/api_jobs.py` | `tests/component/ui/api/test_api_jobs.py` | yes |
| `src/ui/api/api_admin.py` | `tests/component/ui/api/test_api_admin.py` | yes |
| `src/ui/api/api_resume_html.py` | `tests/component/ui/api/test_api_resume_html.py` | yes |
| `src/ui/api/api_intake.py` | `tests/component/ui/api/test_api_intake.py` | yes |

## 7.13f Component coverage map (frontend)

Vitest tests live under **`tests/component/frontend/`** (mirror `components/`, `pages/`, `contexts/`, `lib/`, and higher-level **`test_App`** / **`test_routes`** as needed).

There is **no** per-source-file branch-lock table (**§6b**). Prefer adding or extending tests beside the modules they guard. Coverage artifacts land in **`tests/.coverage/frontend/`** when `./scripts/testing/run_component_tests.sh` runs the Vitest **coverage** target.

## 7.13h Collapsible panels / Manage Tasks (**AST-427**, parent **AST-426**)

**`CollapsiblePanel`** shared by **`AdminTaskPrompts`** (Manage Tasks list + edit modal) and **`ArtifactEditor`** (criteria). Zero expanded sections: list phases and edit modal (`editOpenPanel === null` on collapse, same pattern as criteria `expandedTabId === ""`).

| Area | Source | Component tests |
| --- | --- | --- |
| Collapsible primitive | `src/ui/frontend/src/components/CollapsiblePanel.tsx` | `tests/component/frontend/components/test_CollapsiblePanel.test.tsx` |
| Manage Tasks | `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx` |
| Criteria regression | `src/ui/frontend/src/components/ArtifactEditor.tsx` | `tests/component/frontend/components/test_ArtifactEditor.test.tsx` (unchanged gate) |

## 7.13g Consult rubric vector importance (**AST-359**)

Per-vector **`importance`** (1–10), **`ASTRAL_CONFIG["consult_importance"]`** multipliers (consumed later by **AST-358**), **`normalize_rubric_artifacts_on_save`**, and rubric UI labels / editor behavior. Run the full component suite (**Appendix A**); for targeted reruns, use:

| Area | Source (high level) | Component tests |
| --- | --- | --- |
| Multiplier table + accessor | `src/utils/config.py` (`consult_importance`, `importance_multiplier`) | `tests/component/utils/test_config.py` (`TestImportanceMultiplier`, `TestImportanceMultiplierEdges`) |
| Artifact normalization | `src/core/candidate.py` | `tests/component/core/test_candidate.py` (`TestNormalizeRubricArtifactsOnSaveExtended`, `TestNormalizeImportanceValue`) |
| Display helpers | `src/ui/frontend/src/lib/rubricDisplay.ts` | `tests/component/frontend/lib/test_rubricDisplay.test.ts` |
| Editor / rail | `ArtifactEditor.tsx`, `SideTabPanel.tsx` | `tests/component/frontend/components/test_ArtifactEditor.test.tsx`, `tests/component/frontend/components/test_SideTabPanel.test.tsx`, `tests/component/frontend/components/test_LabeledTextArea.test.tsx` |
| Analysis / job surfaces | `AgentAnalysisHeader.tsx`, job pages | `tests/component/frontend/components/test_AgentAnalysisHeader.test.tsx`, `tests/component/frontend/pages/test_ArtifactsCompanyWatchCriteria.test.tsx`, `test_ArtifactsJobListCriteria.test.tsx`, `test_ArtifactsJobDescCriteria.test.tsx`, `test_ArtifactsGetJobCriteria.test.tsx`, `test_ArtifactsDoJobCriteria.test.tsx`, `test_ArtifactsLikeJobCriteria.test.tsx` |

## 7.13i Universal grade values config (**AST-428**, parent **AST-358**)

**`GRADE_VALUES`**, **`RUBRIC_TOTAL`**, **`grade_value()`** in `config.py`; graded consult tasks use encoded batch shapes — **`draft_job_resume`** is structure-keyed per **AST-594** (no `grades` / vectors on that hop).

| Area | Source | Component tests |
| --- | --- | --- |
| Grade constants + accessor | `src/utils/config.py` | `tests/component/utils/test_config.py` (`TestGradeValuesConfig`) |

## 7.13m Artifact pipeline `TASK_CONFIG` registry (**AST-450**, **AST-520**, parent **AST-516**)

Ten Phase E **`task_key`** values replace **`craft_job_*`**. **Dispatch entry** is the row's **`dispatch_task.task_key`** (**AST-534**) — not **`consult._INPUT_STATE_TO_TASK`** (legacy map, tests only). Seeded **`BUILD_ARTIFACTS`** rows still default to **`contemplate_job`**; Susan may add **`anticipate_scan`** @ **`BUILD_ARTIFACTS`** when schema allows. **`CANDIDATE_REVIEW`** uses **`draft_cover_letter`**. Chain order is **`agent_task.run_next`** only — no step arrays in code.

| Area | Source | Component tests |
| --- | --- | --- |
| Registry + BUILD/CANDIDATE entry keys | `src/utils/config.py` (`TASK_CONFIG`, `BUILD_CONFIG` chain `first_task_key`), `src/core/consult.py` `run_consult_task(dispatch_task_key=…)`, `src/core/dispatcher.py`, `src/data/database.py` (`dispatch_task_admin_defaults`) | `tests/component/utils/test_config.py` (`TestAst450ArtifactPipelineTaskKeys`, `TestAst520AnticipateScanTaskKey`, `TestAst309CoverLetterTaskConfig`), `tests/component/core/test_consult.py` (`TestRunConsultTask`, `TestAst369CoverLetterDispatch`, `TestAst371ResumeArtifactDispatch`, `TestAst534DispatchTaskKeyHonesty`), `tests/component/core/test_dispatcher.py` (`test_ast534_forwards_dispatch_task_key_to_consult`), `tests/component/core/test_agent.py` (artifact chain + `do_task` paths using **`draft_job_resume`** / **`draft_cover_letter`**) |
| Agent story phase + display label | `src/core/roster.py` (`get_entity_agent_story`) | `tests/component/core/test_roster.py` (`TestEntityAgentStory::test_ast520_agent_story_phase_and_print_label`) |
| Recommended Job Analysis Report — Phase E hops | `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` | `tests/component/frontend/components/test_JobAnalysisReportModal.test.tsx` (Phase E **`agent_story`** panel — **AST-520**) |

## 7.13k Quickie bugs / Astral Artifacts UI (**AST-436**, children **AST-442**–**444**)

Parent UAT on **`origin/ftr/AST-436-quickie-bugs`** surfaced gaps when manifests tested components or API defaults only. Use **§6c** for all future UI QA.

| Route / page | Source | Minimum component test | Required mocks (first paint) |
| --- | --- | --- | --- |
| Candidate Profile | `src/ui/frontend/src/pages/CandidateProfile.tsx` | `tests/component/frontend/pages/test_CandidateProfile.test.tsx` — must render page + open signature-image tab | `/api/shapes/candidates`, `/api/ui_config`, `/api/candidates/{id}`, `/api/state_ui_manifest` (reject OK) |
| Execution History | `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` | `tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx` — include date blur / clear behavior per **§6c** | `/api/candidates`, `/api/admin/dispatch_ledger`, ledger logs as needed |
| Scheduled Actions | `src/ui/frontend/src/pages/AdminScheduledActions.tsx` | `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` | candidates, dispatch tasks, thread status |
| Signature image tab wiring | `TabbedTextArea.tsx` + `CandidateProfile.tsx` | **Both** `test_TabbedTextArea.test.tsx` (panel slot) **and** `test_CandidateProfile.test.tsx` (routed page) | see Candidate Profile row |

## 7.13j Importance-based scoring engine (**AST-429**, parent **AST-358**)

**`_render_score`** uses AST-358 three-knob math (`RUBRIC_TOTAL / V`, `grade_value` × confidence, `importance_multiplier` per rubric row). **`_rubric_to_weights`** and **`GRADE_QUALITY_LEGACY`** removed. Depends on **AST-428** config on the same sub branch stack.

| Area | Source | Component tests |
| --- | --- | --- |
| Scored grading + importance lookup | `src/core/consult.py` (`_render_score`, `_importance_for_label`) | `tests/component/core/test_consult.py` (`TestRenderScore`, `TestRenderScoreBranches`, `TestRubricHelpers`) |
| V==0 / all no-signal rows | `src/core/consult.py` (`_render_score`) | `tests/component/core/test_consult.py` (`TestRemainingConsultBranches::test_render_score_with_only_no_signal_rows`) |

## 7.13n `agent_task` seven-segment persistence (**AST-454**, parent **AST-453**)

Seven prompt segments on `agent_task`: `system_prompt`; **`cache_prompt`** as Anthropic cache block A; **`cache_prompt_b|c|d`** as blocks B–D; **`nocache_prompt`**; **`user_prompt`**. Segment edits retire the prior `current` row and insert a new `current = 1` version; **`agent_id` / `run_next`**-only edits update `updated_at` without versioning. **`list_candidate_tasks`** surfaces `cache_prompt_b_len|c_len|d_len` for admin task-manager probes (**AST-454** **`_enrich_tasks`**).

| Area | Source | Component tests |
| --- | --- | --- |
| Migration, versioning, round-trip lengths | `src/data/database.py` (**`_ensure_agent_task_schema`**, **`save_agent_task`**, **`get_agent_task`**, **`list_candidate_tasks`**) | `tests/component/data/database/test_agent_tasks.py` (**`TestAst454SevenSegmentPersistence`**, **`TestSaveAgentTask`**) |
| Admin task GET/PUT segment fields | `src/ui/api/api_admin.py` | Covered by `./scripts/testing/run_component_tests.sh` (includes **`test_api_admin`**) |


## 7.13o Caller chain tokens and five cached API blocks (**AST-455**, parent **AST-453**)

Hop-to-hop **`chain_context`** uses **`CALLER_SYSTEM`**, **`CALLER_CACHE_A`**–**`D`**, **`CALLER_RESPONSE`** only ( **`{$CACHE_BLOCK_*}`** retired from **`TOKEN_SOURCES`** — literals pass through unresolved). **`do_task`** / **`preview_prompt`** assemble ≤5 ephemeral **`system`** blocks from resolved system + cache A–D; **`send_to_anthropic`** payloads store distinct **`CACHE_B`**/**`C`**/**`D`** **`agent_data`** rows when exercised.

| Area | Source | Component tests |
| --- | --- | --- |
| Assembly + caller hop dict | `src/core/agent.py` (`_assemble_blocks_seven_segment`, `_chain_tokens_for_next_hop`) | `tests/component/core/test_agent.py` (`TestAst455SevenSegmentAssembly`, `TestChainContext`, `TestPromptHelpers`) |
| **`TOKEN_SOURCES` / Manage Tasks picker** | `src/utils/config.py` | `tests/component/utils/test_config.py` (**`TestManageTasksTokenPickerLookup`**, **`CALLER_*`**, **`get_manage_tasks_chain_tokens`**) |
| Admin chain token list endpoint | `src/ui/api/api_admin.py` | `tests/component/ui/api/test_api_admin.py` (`test_list_tasks_and_tokens` — meta + chain **exactly** `get_tokens()` / `get_manage_tasks_chain_tokens()`) |

## 7.13p Manage Tasks editor: seven panels + merged pickers (**AST-456**, parent **AST-453**)

**`AdminTaskPrompts`** loads **`/api/admin/tasks/meta/tokens`** and **`meta/chain_tokens`**, merges for **`TokenTextarea`** pickers across all segments, and exposes **seven** accordion panels (**System**, **Cache Block A–D**, **No cache**, **User**) plus **`PREVIEW_TABS`** for resolved preview per segment.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed Manage Tasks UX | `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx` (**`AST-456`**), `tests/component/frontend/lib/test_manageTasksTokenPicker.test.ts` (**merged picker**) |

## 7.13q Astral Boards `board_search` REST + DDL + workflow **`state`** (**AST-458**, **AST-471**, parent **AST-379**)

Workflow **`state`**: **`ACTIVE`** | **`INACTIVE`** | **`ERROR`** (literals **`BOARD_SEARCH_STATES`**); claim requires **`ACTIVE`** plus clear **`batch_id`** (§2.4 lock = **`batch_id`** only — **`clear_board_search_batch`** clears **`batch_id`** alone). **`enabled`** removed. **`search_mode`** (API **`mode`**: `criteria` \| `deeplink`), **`deeplink_url`**, **`entry_url`** / deeplink **`netloc`** parity, duplicates per **AST-458**. **`gaze_board`** seed uses **`trigger_state`** **`ACTIVE`**, **`entity_type`** **`board_search`**.

| Area | Source | Component tests |
| --- | --- | --- |
| `board_search` schema + **`claim_board_search_batch`** ACTIVE + clear batch + **`last_scan_at`** cadence (AST-482) | `src/data/database.py` | `tests/component/data/database/test_board_search_integration.py` (**`TestClaimBoardSearchSqlShape`**, **`TestBoardSearchLastScanCadenceAst482`**) |
| Deeplink normalization + duplicate fingerprints | `src/core/boards.py` | `tests/component/data/database/test_board_search_integration.py` (**`TestBoardDeeplinkNormalize`**) |
| REST `/api/boards/searches` (reject legacy **`enabled`**) | `src/ui/api/api_boards.py` | `tests/component/data/database/test_board_search_integration.py` (**`TestBoardSearchRestAst458`**, **`test_list_adopted_boards_for_picker`**) |
| **`ingest_board_listings`** (gaze → jobs) | `src/core/tracker.py` | `tests/component/core/test_tracker.py` (**`TestIngestBoardListings`**) |
| **`process_gaze_board_batch`** + **`set_board_search_state`** | `src/core/gazer.py` | `tests/component/core/test_gazer.py` (**`TestProcessGazeBoardBatch`**) |
| **`run_consult_task`** / **`_run_unified`** `entity_type=board_search` (**`ACTIVE`**) | `src/core/consult.py`, `src/core/dispatcher.py` | `tests/component/core/test_consult.py`, `tests/component/core/test_dispatcher.py` |
| **`board_search_deeplink`** | `src/external/playwright.py` | `tests/component/external/test_playwright.py` (**`TestBoardSearchDeeplink`**) |
| Scheduler **`_tick_loop`** wait → **`clear`** | `src/core/dispatcher.py` | `tests/component/core/test_dispatcher.py` (**`TestScheduler::test_tick_loop_calls_clear_after_wait_then_stops`**) |
| Locked-file branch gate (AST-455 chain preview ripple on **458** handoff) | `src/core/candidate.py`, `src/core/agent.py`, `src/ui/api/api_admin.py` | `tests/component/core/test_candidate.py` (**chain_sim preview**), `tests/component/core/test_agent.py` (**`TestAst455SevenSegmentAssembly`**, **`TestChainContext`**, **`TestStoreBlocks`**), `tests/component/ui/api/test_api_admin.py` (**`test_preview_task_chain_sim_and_chain_tokens`**) |

Manifest default: `./scripts/testing/run_component_tests.sh` (includes this file).

## 7.13r `gaze_board` claim filter — **`state = ACTIVE`** (**AST-471**, supersedes **AST-459** **`enabled`** idea)

Eligible rows for **`claim_board_search_batch`** are **`state = 'ACTIVE'`** with **`batch_id`** cleared. User pause = **`INACTIVE`**; gaze failure sets **`ERROR`** until resume **`ACTIVE`**. Deeplink **`search_mode`** / **`run_board_search_gaze`** URL contract remains **`TestRunBoardSearchGazeAst459`** in **`test_boards.py`** where named.

## 7.13s Manage Candidate Board Searches UI (**AST-457**, **AST-471** UX, parent **AST-379**)

**`CandidateBoardSearches`** — Active / Paused toggles PATCH **`state`** **`ACTIVE`** ↔ **`INACTIVE`**; **`ERROR`** row shows **Resume ACTIVE**. CRUD via **`/api/boards/searches`**, **`GET /api/boards`** picker.

| Area | Source | Component tests |
| --- | --- | --- |
| Routed Board Searches page | `src/ui/frontend/src/pages/CandidateBoardSearches.tsx` | `tests/component/frontend/pages/test_CandidateBoardSearches.test.tsx` (**§6c** — **`/api/candidates`**, **`/api/boards`**, **`/api/boards/searches`**) |
| Route registration | `src/ui/frontend/src/routes.tsx` | `tests/component/frontend/test_routes.test.tsx` (`candidate/board_searches`; no `title_patterns`) |
| REST + DDL | `src/ui/api/api_boards.py`, `src/data/database.py` | `tests/component/data/database/test_board_search_integration.py` (**`TestBoardSearchRestAst458`**) |

## 7.13t NO_OPENINGS Playwright recheck + **JOBS_FOUND** (**AST-463**, parent **AST-460**)

**`recheck_no_openings`** dispatch batch: Playwright **`get_visible_text`** on stored **`job_site`** only; substring match on **`company_data.no_jobs_message`** keeps **NO_OPENINGS** + **`last_scan_at`**; absence transitions to **JOBS_FOUND**. **TO_WATCH** **`find_job_page`** path unchanged. Admin adhoc live preview echoes **`job_site`** for **`recheck_no_openings`**.

| Area | Source | Component tests |
| --- | --- | --- |
| **`process_recheck_no_openings`** + **`run_company_task`** **NO_OPENINGS** branch | `src/core/roster.py` | `tests/component/core/test_roster.py` (**`TestProcessRecheckNoOpenings`**, **`TestRunCompanyTask::test_no_openings_routes_to_recheck_not_find_job_page`**, **`TestRunCompanyTask::test_locate_job_page_paths`**) |
| Admin adhoc content for **locate_job_page** (nav_links) + **`recheck_no_openings`** (**`job_site`**) | `src/ui/api/api_admin.py` | `tests/component/ui/api/test_api_admin.py` (**`test_build_adhoc_live_content_remaining_company_and_job_edges`** in **`TestApiAdminBranchGaps`**) |
| Dispatch seed **`recheck_no_openings`** + migration off **`find_job_page`** | `src/data/database.py` | Exercised via full component run / DB harness; roster tests mock I/O |

## 7.13u Administrator table copy upsert — Copy Output merge (**AST-464**, parent **AST-373**)

Generic **`apply_copy_output_table_upsert(table_name, json_payload)`**: parse JSON array, FK pragma on, transactional generic upsert-by-PK or **`agent_task`** import (**`apply_agent_task_copy_upsert`** + **`_save_agent_task_on_connection`**). **AST-464** is core + **`database.py`**; **AST-465** adds Data Management UI + **`POST /api/admin/data/table_copy_upsert`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Orchestrator (**malformed payload, FK rollback, composite PK, nested cell reject**) | `src/core/table_copy_upsert.py` | `tests/component/data/database/test_table_copy_upsert.py` |
| PK enforcement + generic / **`agent_task`** batch paths | `src/data/database.py` (**`primary_key_column_names`**, **`apply_generic_table_copy_upsert`**, **`apply_agent_task_copy_upsert`**, **`save_agent_task`**) | `tests/component/data/database/test_table_copy_upsert.py`; versioning round-trip **`tests/component/data/database/test_agent_tasks.py`**, **`tests/component/ui/api/test_api_admin.py`** |
| Data Management **Table Upsert** + admin route (**AST-465**) | `src/ui/frontend/src/pages/AdminDataManagement.tsx`, `src/ui/api/api_admin.py` (**`admin_table_copy_upsert`**) | `tests/component/frontend/pages/test_AdminDataManagement.test.tsx` (**§6c** — page + modal + toast paths); **`tests/component/ui/api/test_api_admin.py`** (**`test_table_copy_upsert_paths`**) |

## 7.13v Board-sourced qualify + evaluate dispatch (**AST-419**, parent **AST-379**)

Board jobs ingested via **`ingest_board_listings`** (placeholder **`__board__{board_key}`** company, **`board_search_id`**, state **`NEW`**) must reach **`validate_title` → `qualify_job_listings` → `scrape_jd` → `evaluate_jd`** through normal **`claim_job_batch` / `get_new_job_batch`** dispatch — no state-machine bypass. Uses real SQLite (**`seeded_db`**); consult/scrape agent calls mocked.

| Area | Source | Component tests |
| --- | --- | --- |
| Board ingest → **`NEW`** + placeholder company | `src/core/tracker.py` | `tests/component/core/test_board_sourced_qualify_evaluate.py` (**`TestBoardSourcedQualifyEvaluateAst419::test_board_ingest_starts_in_new_with_board_search_id`**) |
| Full qualify/evaluate dispatch chain for board jobs | `src/core/tracker.py`, `src/core/gazer.py`, `src/core/consult.py` | `tests/component/core/test_board_sourced_qualify_evaluate.py` (**`test_board_job_reaches_qualify_and_evaluate_dispatch`**) |

Manifest default: `./scripts/testing/run_component_tests.sh tests/component/core/test_board_sourced_qualify_evaluate.py`.

## 7.13w Consult config absorb — `GAZER_CONFIG` + `TASK_CONFIG` orchestration (**AST-466**, **AST-467**, **AST-468**, parent **AST-376**)

Orchestration literals for gazer steps live in **`GAZER_CONFIG`** (`validate_title`, `scrape_jd`, **`gaze`** error_state). Job consult scored steps carry pass/fail/error, **`save_prefix`**, **`pass_threshold`**, **`requires_company`**, JD/qualify thresholds, and **`fallback_batch_size`** on **`TASK_CONFIG`** (`qualify_job_listings`, **`evaluate_jd`**, **`grade_do`**, **`grade_get`**, **`grade_like`**). **`src/core/consult.py`** and **`src/core/gazer.py`** read **`TASK_CONFIG` / `GAZER_CONFIG` directly** (`consult_*` dispatch keys → **`grade_*`** orchestration via **`_consult_orchestration`** in consult). **`CONSULT_CONFIG`** removed (AST-468 Stage 6). **`RUBRIC_ARTIFACT_KEYS`** derives from the five **`TASK_CONFIG`** **`rubric_artifact`** fields. **`pass_threshold`** vs **`dispatch_task.score_floor`**: see **`docs/ASTRAL_CODE_RULES.md`** §2.1 (different lifecycle — not a numeric override).

| Area | Source | Component tests |
| --- | --- | --- |
| **`GAZER_CONFIG`**, **`RUBRIC_ARTIFACT_KEYS`**, board registry layout | `src/utils/config.py` | `tests/component/utils/test_config.py` (**`TestBoardRegistryAst457`**, **`TestAst309CoverLetterTaskConfig`** where applicable, **`TestAst479LikePassStates`**); branch lock for **`config.py`** via full component run |
| **`TASK_CONFIG` / `GAZER_CONFIG` orchestration (**AST-467**)** | `src/core/consult.py`, `src/core/gazer.py` | `tests/component/core/test_consult.py` ( **`monkeypatch` / assertions on `TASK_CONFIG` — `consult_*` dispatch → **`grade_*`** orch via **`_consult_orchestration`**); `test_gazer.py` for **`validate_title_batch`**, **`scrape_jd_batch`**, **`process_gazer_batch`** ( **`GAZER_CONFIG`** ). **`TestProcessGazeBoardBatch`** is **`§7.13q`** / boards spine (**`process_gaze_board_batch`**) — if that symbol is absent on your tip, rerun gazer narrowly with **`pytest tests/component/core/test_gazer.py -k 'not ProcessGazeBoardBatch'`** alongside consult before asserting full-file green. |
| Dispatch resolution helpers (**AST-468**) | `src/core/dispatcher.py`, `src/data/database.py`, `src/ui/api/api_admin.py` | `tests/component/core/test_dispatcher.py`, `tests/component/ui/api/test_api_admin.py` |
| Board-sourced pipeline still sees same states | `src/core/tracker.py`, consult + gazer | `tests/component/core/test_board_sourced_qualify_evaluate.py` |

Sibling **AST-468** dispatch helpers documented in **§7.13x**.

Manifest default ( **`test-astral`** on publish tip — consult/config scope; avoids unrelated **`origin/dev`** board integration gaps): `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py tests/component/core/test_consult.py tests/component/core/test_gazer.py tests/component/core/test_dispatcher.py tests/component/core/test_agent.py`.

**Harness:** `./scripts/testing/run_component_tests.sh` with trailing paths forwards them to **`pytest`** (narrow selection + same **`--cov=src`** / JSON report wiring). **`check_per_file_coverage.py`** (**`LOCKED_AT_100`**) runs **only** with zero args (full **`tests/component`** selection); narrowed manifest calls skip that gate because branch rows are incomplete for untouched locked modules.

## 7.13x Dispatcher / admin consult resolution (**AST-468**, parent **AST-376**)

**`resolve_dispatch_task_config_key`**, **`dispatch_task_key_is_scored`**, **`dispatch_claim_uses_score_floor`**, **`trigger_state_used_by_scored_dispatch_task`**, **`DISPATCH_SCHEDULABLE_TASK_KEYS`** / **`dispatch_task_admin_defaults`** centralize **`consult_*` → `grade_*`** indirection and admin form defaults for **`dispatcher.py`**, **`database.py`**, and **`api_admin.py`**. **`pass_threshold`** vs **`score_floor`**: **`docs/ASTRAL_CODE_RULES.md`** subsection under §2.1; claim gating vs grading metadata: **§7.13zv** (**AST-586**).

| Area | Source | Component tests |
| --- | --- | --- |
| Resolution helpers | `src/utils/config.py` | `tests/component/utils/test_config.py` (imports exercised via callers); **`tests/component/ui/api/test_api_admin.py`**, **`tests/component/core/test_dispatcher.py`**, `tests/component/data/` dispatch paths |
| Admin dispatch metadata + forms | `src/ui/api/api_admin.py` | `tests/component/ui/api/test_api_admin.py` (**`TestAdhocHelpers::test_trigger_state_helpers`**) |

Manifest default ( **`test-astral`** on publish tip — dispatch/admin resolution scope): `./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_trigger_state_helpers tests/component/core/test_dispatcher.py tests/component/data/database/test_dispatch_tasks.py`.

## 7.13y LIKE → `PASSED_LIKE`, Recommended queue, synthesis handoff (**AST-479** / **AST-480**, parent **AST-478**)

**`consult_like`** success lands in **`PASSED_LIKE`** (not **`BUILD_ARTIFACTS`**). **`RECOMMENDED_JOB_STATES`** lists **`RECOMMENDED`**, **`BUILD_ARTIFACTS`**, **`CANDIDATE_REVIEW`** — pre-upshot **`PASSED_LIKE`** stays in **`IN_REVIEW`** / score-gated consult views. **`analysis_upshot`** dispatch (**AST-480**) runs at **`PASSED_LIKE`** / **`PASSED_LIKE_RETRY`** (scored claim), persists **`job_data["analysis_upshot"]`**, transitions **`PASSED_LIKE` → `RECOMMENDED`** (or **`PASSED_LIKE_RETRY`** on failure).

| Area | Source | Component tests |
| --- | --- | --- |
| `JOB_STATES` / `TASK_CONFIG["grade_like"]` / Recommended vs In-review lists | `src/utils/config.py` | **`TestAst479LikePassStates`** (`test_config.py`) |
| **`analysis_upshot`** task + trigger seed + PASSED_LIKE scored dispatch | `src/utils/config.py`, `src/data/database.py`, `src/core/consult.py` | **`TestAst480AnalysisUpshotConfig`**, **`TestAst471DispatchConfigHelpers`** (`test_config.py`); **`TestRunConsultTaskRoutes::test_routes_passed_like_to_analysis_upshot_batch`** (`test_consult.py`) |
| Jobs API recommended view passes `RECOMMENDED_JOB_STATES` | `src/ui/api/api_jobs.py` | **`test_list_recommended_and_default`** (`test_api_jobs.py`) |
| Recommended page + actions for review-like rows | `JobsRecommended.tsx`, `CandidateJobRowActions.tsx` | **`test_JobsRecommended.test.tsx`** (rubric-era; superseded for phase-score UI by **§7.13zm** **AST-522**) |

## 7.13zm State-grouped Recommended list — phase scores (**AST-522**, parent **AST-498**)

Rebuild **`JobsRecommended.tsx`**: config-driven sections (**Recommended** / **In Progress** / **Ready**), plain numeric **JD / DO / GET / LIKE** from flattened API fields (no LIKE rubric grade-dot columns, no **`latest_score`** column). **`build_state_ui_manifest()["jobs"]["recommended"]`** + **`StateUiContext`** defaults mirror **`JOBS_RECOMMENDED_UI_SECTIONS`** / **`JOBS_RECOMMENDED_PHASE_SCORE_COLUMNS`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Recommended UI manifest | `src/utils/config.py` | **`TestBuildStateUiManifest::test_ast522_recommended_manifest_sections_and_phase_columns`** (`test_config.py`) |
| Routed Recommended page (**§6c**) | `src/ui/frontend/src/pages/JobsRecommended.tsx` | **`tests/component/frontend/pages/test_JobsRecommended.test.tsx`** — three sections, phase headers, score + em dash, per-section Company sort, Skip / View Job Analysis, row → detail modal |
| Jobs API recommended view | `src/ui/api/api_jobs.py` | **`test_list_recommended_and_default`** (`test_api_jobs.py`) — regression |
| **`RECOMMENDED_JOB_STATES`** membership | `src/utils/config.py` | **`TestAst479LikePassStates`** (`test_config.py`) — regression |

**AST-522** narrowed run (Vitest paths are **not** forwarded by `run_component_tests.sh` trailing args — run Vitest explicitly):

```bash
python3 -m pytest tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast522_recommended_manifest_sections_and_phase_columns tests/component/ui/api/test_api_jobs.py::test_list_recommended_and_default -q

cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx
```

## 7.13zv Dispatch claim `score_floor` vs input triggers (**AST-586**, parent **AST-547**)

**`dispatch_claim_uses_score_floor`** gates **`get_new_job_batch`** / admin **`is_scored`** / **`count_eligible_for_dispatch_task`** — distinct from **`trigger_state_used_by_scored_dispatch_task`** (task grading metadata). Input triggers such as **VALID_TITLE** run scored **`qualify_job_listings`** but jobs lack **`latest_score`** until that step completes; claim must pass **`score_floor=None`**. Post-score outcomes (**PASSED_JD**, **PASSED_JOBLIST**, **PASSED_SCORE_GATED_STATES**) keep floor behavior.

| Area | Source | Component tests |
| --- | --- | --- |
| Claim helper | `src/utils/config.py` | **`TestAst586DispatchClaimScoreFloor`** in `tests/component/utils/test_config.py` |
| Dispatcher claim | `src/core/dispatcher.py` | **`TestRunUnified::test_qualify_valid_title_claim_without_score_floor`** |
| Admin list/create | `src/ui/api/api_admin.py` | **`TestDispatchTasks`** + **`TestAdhocHelpers::test_trigger_state_helpers`** in `tests/component/ui/api/test_api_admin.py` |

**AST-586** narrowed run (**`test-astral`** manifest):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst586DispatchClaimScoreFloor \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_qualify_valid_title_claim_without_score_floor \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks \
  tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_trigger_state_helpers
```

## 7.13z Job Analysis Report — `analysis_upshot` runtime render (**AST-481**, parent **AST-478**)

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

## 7.13za Board search **`last_scan_at`** **`gaze_board`** cadence (**AST-482**, parent **AST-379**)

Mirror company **`WATCH` / `gaze`**: nullable **`board_search.last_scan_at`**, **`BOARDS_CONFIG["gaze_board"]["scan_interval_hours"]`** (default **24**), staleness **`AND`** in **`claim_board_search_batch`** matches **`count_eligible_for_dispatch_task`** ( **`freq_hrs` override** when **> 0**). **`dispatch_task`** seed **`sort_by`** **`last_scan_at`** (+ migration **`updated_at` → `last_scan_at`** for legacy rows). **`update_board_search_last_scan_at`** bumps **only success path** after **`run_board_search_gaze`** in **`process_gaze_board_batch`** (no bump on **`except`**). Dispatcher passes **`scan_interval_hours`** + **`sort_by`** into **`claim_board_search_batch`**.

| Area | Source | Component tests |
| --- | --- | --- |
| Claim staleness **`NULL`** / stale / fresh + **`count_eligible`** parity + **`freq_hrs`** tightening | `src/data/database.py` | `tests/component/data/database/test_board_search_integration.py` (**`TestBoardSearchLastScanCadenceAst482`**) |
| Success bump vs failure silent | `src/core/gazer.py` | `tests/component/core/test_gazer.py` (**`TestProcessGazeBoardBatch`**) |
| **`_run_unified`** board_search **`scan_interval_hours`** / **`sort_by`** kwargs | `src/core/dispatcher.py` | `tests/component/core/test_dispatcher.py` (**`TestRunUnified`**) |
| **`BOARDS_CONFIG["gaze_board"]["scan_interval_hours"]`** | `src/utils/config.py` | `tests/component/utils/test_config.py` (**`TestAst471DispatchConfigHelpers::test_gaze_board_boards_config_scan_interval_hours`**) |

Narrow (**`test-astral`** **AST-482** tip):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_board_search_integration.py::TestBoardSearchLastScanCadenceAst482 \
  tests/component/core/test_gazer.py::TestProcessGazeBoardBatch \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_claims_board_search_batch_and_clears \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_board_search_claim_passes_freq_and_sort_kw \
  tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers::test_gaze_board_boards_config_scan_interval_hours
```

## 7.13zb First-segment grade token readability (**AST-483**, parent **AST-472**)

**`_decode_payload`** classifies pipe fields using **`norm`** (drop ASCII space, hyphen, colon before **`_GRADE_SEG.match`**). **`grades_meta`** / **`grades_encoded_notes`** metadata retains the pipe-stripped **original** fragment so **`job_title`** and **`key:value`** tails stay unchanged.

**`test-astral`** gate for **`AST-483`:** Use **only** the narrowed command below. With **no pytest args**, `run_component_tests.sh` runs the full **`tests/component`** tree and **`check_per_file_coverage.py`** (`LOCKED_AT_100`); that gate currently trips on **`src/utils/config.py`**, **`src/core/roster.py`**, and **`src/core/consult.py`** (and similarly on **`origin/dev`**) independently of **`AST-483`** — so listing the zero-arg invocation in the **`Tests Ready`** manifest is **not** a reproducible merge path until those locks regain 100%. Narrow args skip the **`$# == 0`** branch-lock step per `run_component_tests.sh`; Vitest still runs after pytest.

| Area | Source | Component tests |
| --- | --- | --- |
| **`evaluate_jd`** prettified **`grades`** vs compact; **`grades_meta`** title spaces | `src/core/agent.py` (`_decode_payload`) | **`TestDecodePayload::test_decodes_whitespace_inside_grade_tokens_preserves_meta`** (`tests/component/core/test_agent.py`) |

Narrow (**`test-astral`** **AST-483** tip):

```bash
./scripts/testing/run_component_tests.sh tests/component/core/test_agent.py::TestDecodePayload::test_decodes_whitespace_inside_grade_tokens_preserves_meta
```

## 7.13zc Dispatch admin roster **`task_keys`** — find/select/parse (**AST-485**, parent **AST-461**; defaults **AST-549**)

Roster trio **`find_job_page`**, **`select_job_page`**, **`parse_job_list`** (company **TO_WATCH**); **`locate_job_page`** is not schedulable (legacy **`UPDATE`** during schema ensure). **AST-549** retired **`database._DISPATCH_TASK_SEED`** / **`config._DISPATCH_TASK_TRIGGER_SEED`** — schedulable defaults now come from **`dispatch_task_admin_defaults`** (**§7.13zq**). **`get_dispatch_row_or_seed_preview_meta`** supplies admin **`adhoc`** when no sample DB row exists. **`GET /api/admin/dispatch_tasks/task_keys`** lists every **`TASK_CONFIG`** key (**AST-516**); schedulable keys merge config derivation.

| Area | Source | Component tests |
| --- | --- | --- |
| Schedulable roster trio defaults | `src/utils/config.py` | **`TestAst471DispatchConfigHelpers::test_ast485_roster_dispatch_trio_matches_config_defaults`** (`tests/component/utils/test_config.py`) |
| **`task_keys`** roster trio + **`adhoc_entities`** config fallback | `src/ui/api/api_admin.py`, `src/data/database.py` | **`test_ast485_dispatch_task_keys_roster_seeds_minus_locate_template`**, **`test_ast485_adhoc_entities_select_job_page_fallbacks_to_config_defaults`** (`tests/component/ui/api/test_api_admin.py` **`TestApiAdminBranchGaps`**) |
| Nav-links preview (**`find`** / **`select`** / legacy **`locate`**) | `src/ui/api/api_admin.py` | **`TestAdhocHelpers::test_build_adhoc_live_content_company_paths`** (`test_api_admin.py`) |

Narrow (**`test-astral`** **AST-485** / **AST-549** regression tip):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers::test_ast485_roster_dispatch_trio_matches_config_defaults \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast485_dispatch_task_keys_roster_seeds_minus_locate_template \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast485_adhoc_entities_select_job_page_fallbacks_to_config_defaults \
  tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_build_adhoc_live_content_company_paths
```

## 7.13zd LLM provider catalog, `brain_setting` tiers, admin agent CRUD (**AST-492**, **AST-495**, parent **AST-491**)

**`LLM_PROVIDER_CONFIG`**, **`DEEPSEEK_MODEL_PRICING`**, Ada tier helpers (**`resolve_brain_setting_to_anthropic_agent_key`**, **`resolve_brain_setting_to_deepseek_tier_meta`**, **`validate_allowed_brain_setting`**, **`infer_brain_setting_from_legacy_model_code`**); product may keep thin wrappers (**`admin_brain_setting_catalog()`**, **`anthropic_agent_key_for_brain_setting`**). **`component` tests compare admin payloads using resolve + **`get_model`** only. **`save_agent`** / **`get_agent`** / **`list_agents`** **`brain_setting`** column + migration off legacy **`model_code`**. **`do_task`** resolves tiers to **`AGENT_CONFIG`** keys and calls **`send_to_anthropic`** when **`active_provider`** is **`anthropic`**; when **`deepseek`**, **`resolve_brain_setting_to_deepseek_tier_meta`** feeds **`send_to_deepseek`** (**`vendor_model`**, **`tier_meta`**, same block assembly as Anthropic) per **AST-493**. **`GET /api/admin/agents/brain_settings`** returns tier rows (label + default temperature / max tokens from **`AGENT_CONFIG`**) for Manage Agents (**AST-495**). **`AdminAgentPrompts`** loads that catalog and posts **`brain_setting`** on create/update.

| Area | Source | Component tests |
| --- | --- | --- |
| Tier helpers + env gate + DeepSeek tier meta + tier rows vs resolve | `src/utils/config.py` | **`TestAst492LlmBrainTierConfig`** (`tests/component/utils/test_config.py`) |
| Agent persistence + insert requires **`brain_setting`** | `src/data/database.py` | **`tests/component/data/database/test_agents.py`** |
| **`do_task`** — Anthropic (**`send_to_anthropic`**) vs DeepSeek (**`send_to_deepseek`**) | `src/core/agent.py` | **`TestAst492BrainSettingDoTask`** (`tests/component/core/test_agent.py`) |
| Agent CRUD + **`/agents/brain_settings`** catalog; PUT **`model_code`** present but empty after strip skips infer shim when other kwargs update | `src/ui/api/api_admin.py` | **`TestAdminConfigAndAgents`** (`tests/component/ui/api/test_api_admin.py`) |
| Admin **`_resolve_adhoc`** — infer **`Medium`** when **`brain_setting`** / legacy **`model_code`** absent (**`infer_brain_setting_from_legacy_model_code`**); DeepSeek **`tier_meta`** + unknown provider | `src/ui/api/api_admin.py`, `src/utils/config.py` | **`TestAdhocHelpers::test_adhoc_entities_and_resolve`**, **`TestAst492ResolveAdhocApiAdmin`** (`tests/component/ui/api/test_api_admin.py`) |
| **`_enrich_tasks`** — unknown **`LLM_PROVIDER_CONFIG.active_provider`** (neither **`anthropic`** nor **`deepseek`**) skips catalog pricing | `src/ui/api/api_admin.py` | **`TestEnrichTasks::test_enrich_tasks_unknown_llm_provider_skips_tier_catalog_lookups`** |
| Manage Agents page (**`brain_settings`** + **`brain_setting`** column) | `src/ui/frontend/src/pages/AdminAgentPrompts.tsx` | **`AdminAgentPrompts`** (`tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx`) |

Manifest (**`AST-492`** + **`AST-495`** on **`dev-betty`** after merging both publish tips + conflict resolution):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst492LlmBrainTierConfig \
  tests/component/data/database/test_agents.py \
  tests/component/core/test_agent.py::TestAst492BrainSettingDoTask \
  tests/component/ui/api/test_api_admin.py::TestAdminConfigAndAgents \
  tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_adhoc_entities_and_resolve \
  tests/component/ui/api/test_api_admin.py::TestAst492ResolveAdhocApiAdmin \
  tests/component/ui/api/test_api_admin.py::TestEnrichTasks::test_enrich_tasks_unknown_llm_provider_skips_tier_catalog_lookups
```

**`AdminAgentPrompts`** Vitest (**`AST-495`**): from repo root,

`cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_AdminAgentPrompts.test.tsx`

(or rely on the full **`./scripts/testing/run_component_tests.sh`** with no args — that runs all Vitest component tests too).


## 7.13ze DeepSeek client + unified `agent_timesheets` (**AST-493**, **AST-494**, parent **AST-491**)

**AST-491 (parent epic):** **`qa-astral`** treats **`origin/ftr/AST-491-support-other-ai-models-deepseek`** as the definitive tip for **`docs/ASTRAL_TEST_BIBLE.md`** §7.13zd–§7.13ze; **`origin/sub/AST-491/*`** sibling branches take the same blob via Betty publish (**§ Test Bible**).

**`src/external/deepseek.py`** (**`send_to_deepseek`**) implements **AST-493**; mocked **`do_task`** / **`run_adhoc`** contract lives in **`TestAst492BrainSettingDoTask::test_send_to_deepseek_receives_vendor_model_and_tier_meta`**. **`_add_timesheet_entry`** (**AST-494**) mirrors Anthropic rows into **`anthropic_timesheets`** plus **`agent_timesheets`**; listing reads **`agent_timesheets`** with **`agent_req_id`**. **`tests/component/data/database/test_timesheets.py`**, **`tests/component/core/test_timesheets.py`** assert **`record_timesheet_entry(agent_req_id=…)`** and list row shape.

Manifest (narrow **`AST-493`** + **`AST-494`**; includes **`AST-492`** **`do_task`** DeepSeek assertion):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst492LlmBrainTierConfig \
  tests/component/core/test_agent.py::TestAst492BrainSettingDoTask \
  tests/component/data/database/test_timesheets.py \
  tests/component/core/test_timesheets.py
```

## 7.13zf Encoded batch consult — qualify / evaluate / dispatcher / exhaustion / DO·GET·LIKE (**AST-501** … **503**, parent **AST-500**)

**Parent:** **`origin/ftr/AST-500-high-volume-encoded-batch-consult-migrate-all-stages-cache-first-exhaustion-runs`** is assembled by **`rollup-child`** from **`origin/sub/AST-500/*`** in dependency order; Betty publishes bible manifests to **`sub/*` only**.

| Child | Behavior | Sources | Manifest tests (extend per child as Betty publishes) |
| --- | --- | --- | --- |
| **AST-501** — single-call batches for **`qualify_job_listings`** + **`evaluate_jd`**, envelope-first decode | **`_run_unified`** `batch_call_mode=1`; **`do_task`** strict envelope (**`_strict_encoded_batch_consult_envelope_err`**) | `src/core/dispatcher.py`, `src/core/agent.py`, `src/core/consult.py`, `src/utils/config.py` | `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast501_job_batch_call_mode_single_run_consult_with_all_claimed_entities`; **`TestDoTask`**: **`test_ast501_rejects_evaluate_jd_when_api_returns_bare_encoded_lines_without_envelope`**, **`test_ast501_rejects_evaluate_jd_when_agent_payload_is_structured_json_object`** |
| **AST-502** | Multi-chunk cache-warm exhaustion / parallel follow-on chunks + **`batch_chunk_index`** dedupe suffix | `src/core/dispatcher.py`; `consult.py`; `database.py`; `tracker.py` | `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast502_chunked_evaluate_await_chunk0_sleep_once_then_gather_tails`; **`test_ast502_two_chunks_skips_sleep_when_delay_zero`** |
| **AST-503** | DO / GET / LIKE batch `_run_batch_consult` parity; `grade_*` strict envelope parity with AST-501 | `src/core/consult.py`, `src/core/dispatcher.py`, `src/core/agent.py` | `tests/component/core/test_agent.py::TestDoTask::{test_ast503_rejects_grade_do_when_api_returns_bare_encoded_lines_without_envelope,test_ast503_rejects_grade_do_when_agent_payload_is_structured_json_object}`; `tests/component/core/test_consult.py::TestRunConsultTask::test_ast503_routes_two_passed_jd_jobs_to_consult_do_batch` |

**AST-501** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast501_job_batch_call_mode_single_run_consult_with_all_claimed_entities \
  tests/component/core/test_agent.py::TestDoTask::test_ast501_rejects_evaluate_jd_when_api_returns_bare_encoded_lines_without_envelope \
  tests/component/core/test_agent.py::TestDoTask::test_ast501_rejects_evaluate_jd_when_agent_payload_is_structured_json_object
```

**AST-501 + AST-502** dispatcher slice:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast501_job_batch_call_mode_single_run_consult_with_all_claimed_entities \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast502_chunked_evaluate_await_chunk0_sleep_once_then_gather_tails \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast502_two_chunks_skips_sleep_when_delay_zero \
  tests/component/core/test_agent.py::TestDoTask::test_ast501_rejects_evaluate_jd_when_api_returns_bare_encoded_lines_without_envelope \
  tests/component/core/test_agent.py::TestDoTask::test_ast501_rejects_evaluate_jd_when_agent_payload_is_structured_json_object
```

**AST-503** graded batch envelope + PASSED_JD routing (extends AST-501 DO path):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestDoTask::test_ast503_rejects_grade_do_when_api_returns_bare_encoded_lines_without_envelope \
  tests/component/core/test_agent.py::TestDoTask::test_ast503_rejects_grade_do_when_agent_payload_is_structured_json_object \
  tests/component/core/test_consult.py::TestRunConsultTask::test_ast503_routes_two_passed_jd_jobs_to_consult_do_batch
```

## 7.13zg Roster inflow — search terms + discovery ingest (**AST-504**, **AST-505**, **AST-506**, parent **AST-490**)

Phase 0: newline-delimited **`artifacts.company_search_terms`**, **`craft_company_search_terms`** (on-demand generate only — no **`dispatch_tasks`** row), Artifacts page + save normalization. Phase 1 (**AST-505**): weekly **`inflow_discovery`** candidate dispatch, Google CSE per term, **`vet_inflow_discovery`**, **`ingest_new_companies`** with candidate-scoped URL dedupe, **`NEW`** / **`WEBSITE_FOUND`** company states. Phase 2 (**AST-506**): **`inflow_resolve_website`** company dispatch for **`NEW`** rows with empty **`company_website`**; CSE resolution (20 results, no date restrict) + **`find_company_website`** → **`WEBSITE_FOUND`** or **`NO_WEBSITE`**.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-504** | String artifact + craft task config; normalize on PUT; Artifacts UI generate/regenerate/edit | `src/utils/config.py`, `src/core/candidate.py`, `src/ui/api/api_candidate.py`, `src/ui/frontend/src/pages/ArtifactsCompanySearchTerms.tsx`, `src/ui/frontend/src/routes.tsx` | `tests/component/utils/test_config.py::TestAst504CompanySearchTermsConfig`; `tests/component/core/test_candidate.py::{TestNormalizeCompanySearchTermsOnSave,TestCompanySearchTermsLines}`; `tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_update_rejects_blank_company_search_terms`; `tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx` |
| **AST-505** | Candidate dispatch eligibility; CSE + vet + ingest; **`NEW`** / **`WEBSITE_FOUND`** | `src/utils/config.py`, `src/data/database.py`, `src/core/dispatcher.py`, `src/core/consult.py`, `src/core/roster.py` | `tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig`; `tests/component/data/database/test_dispatch_tasks.py::TestAst505InflowDiscoveryEligible`; `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast505_candidate_entity_routes_ctx_without_company_clear`; `tests/component/core/test_roster.py::TestAst505InflowDiscovery` |
| **AST-505** | CSE + vet + ingest; **`NEW`** / **`WEBSITE_FOUND`** (eligibility cadence → **AST-525** when table is source of truth) | `src/utils/config.py`, `src/data/database.py`, `src/core/dispatcher.py`, `src/core/consult.py`, `src/core/roster.py` | `tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig`; `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast505_candidate_entity_routes_ctx_without_company_clear`; `tests/component/core/test_roster.py::TestAst505InflowDiscovery` |
| **AST-506** | Empty-website claim filter; CSE resolution + **`find_company_website`**; **`NEW → WEBSITE_FOUND \| NO_WEBSITE`** | `src/utils/config.py`, `src/data/database.py`, `src/core/dispatcher.py`, `src/core/roster.py` | `tests/component/utils/test_config.py::TestAst506InflowResolveConfig`; `tests/component/data/database/test_dispatch_tasks.py::TestAst506InflowResolveEligible`; `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast506_inflow_resolve_claims_empty_website_only`; `tests/component/core/test_roster.py::TestAst506InflowResolve` |

**AST-504** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst504CompanySearchTermsConfig \
  tests/component/core/test_candidate.py::TestNormalizeCompanySearchTermsOnSave \
  tests/component/core/test_candidate.py::TestCompanySearchTermsLines \
  tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_update_rejects_blank_company_search_terms \
  tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx
```

**Harness tail (items 1–4):** `run_component_tests.sh` always runs full Vitest coverage after pytest. Cross-ticket page tests must stay green — notably **`test_AdminManageCandidates.test.tsx`** (AST-511 middle-name field selectors) and **`test_CandidateBoardSearches.test.tsx`** (AST-457 mode switch via **`UserPromptProvider`**, not **`window.confirm`**).

**AST-505** narrowed run (blocker **AST-504** tests optional smoke — terms artifact must exist for dispatch eligibility):
**AST-505** narrowed run (blocker **AST-504** tests optional smoke — terms artifact must exist for legacy artifact path; per-term eligibility → **AST-525**):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig \
  tests/component/data/database/test_dispatch_tasks.py::TestAst505InflowDiscoveryEligible \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast505_candidate_entity_routes_ctx_without_company_clear \
  tests/component/core/test_roster.py::TestAst505InflowDiscovery
```

**AST-506** narrowed run (blocker **AST-505** tests optional smoke — **`NEW`** ingest path must exist):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst506InflowResolveConfig \
  tests/component/data/database/test_dispatch_tasks.py::TestAst506InflowResolveEligible \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast506_inflow_resolve_claims_empty_website_only \
  tests/component/core/test_roster.py::TestAst506InflowResolve
```

**Admin prerequisite (Stage 5):** **`craft_company_search_terms`** task prompt row must exist in Admin → Task Prompts before Generate works in UAT (not seeded in product code). **`vet_inflow_discovery`** prompt row required before Phase 1 vet runs in UAT. **Blocker:** **AST-504** (`company_search_terms` artifact) must be on the integration line before dispatch eligibility and discovery batch run in UAT.

## 7.13zi Roster inflow — `company_search_terms` table (**AST-524**, **AST-525**, **AST-526**, parent **AST-523**)

Replaces Phase 0 artifact blob as **source of truth**: one SQLite row per candidate per search term with nullable **`last_scan_at`**, upsert-and-delete sync, legacy artifact migration (**AST-524**). **AST-525** retargets inflow discovery cadence; **AST-526** Artifacts UI/API wiring.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-524** | Table DDL + migration; sync preserves **`last_scan_at`**; core/API sync helpers; stop persisting artifact on save | `src/data/database.py`, `src/core/candidate.py`, `src/ui/api/api_candidate.py`, `src/utils/config.py` (comment only) | `tests/component/data/database/test_company_search_terms.py::TestAst524CompanySearchTermsTable`; `tests/component/core/test_candidate.py::{TestNormalizeCompanySearchTermsOnSave,TestCompanySearchTermsLines,TestAst524CompanySearchTermsTable}`; `tests/component/ui/api/test_api_candidate.py::{TestCandidateRoutes::test_update_rejects_blank_company_search_terms,TestAst524CompanySearchTermsSync}` |
| **AST-525** | Per-term **`last_scan_at`** cadence; CSE only for stale terms; bump after successful CSE; **`COMPANY_SEARCH_TERMS`** from table overlay | `src/utils/config.py`, `src/data/database.py`, `src/core/roster.py`, `src/core/candidate.py`, `src/core/agent.py` | `tests/component/utils/test_config.py::TestAst525InflowDiscoveryConfig`; `tests/component/data/database/test_company_search_terms.py::TestAst524CompanySearchTermsTable::test_list_stale_company_search_terms_ordered`; `tests/component/data/database/test_dispatch_tasks.py::TestAst525InflowDiscoveryEligible`; `tests/component/core/test_roster.py::TestAst505InflowDiscovery::{test_run_batch_no_stale_terms_returns_zero_errors,test_run_batch_happy_path,test_run_batch_cse_failure_continues,test_run_batch_searches_only_stale_terms}`; `tests/component/core/test_candidate.py::{TestCompanySearchTermsLines,TestAst525CompanySearchTermsTokenOverlay}` |

| **AST-526** | Artifacts GET injects table-backed **`company_search_terms`**; PUT intercept syncs table, strips artifact blob; page loads top-level field (**§6c**) | `src/ui/api/api_candidate.py`, `src/ui/frontend/src/pages/ArtifactsCompanySearchTerms.tsx` | `tests/component/ui/api/test_api_candidate.py::TestAst526ArtifactsCompanySearchTermsApi`; `tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx` |


**AST-524** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_company_search_terms.py::TestAst524CompanySearchTermsTable \
  tests/component/core/test_candidate.py::TestNormalizeCompanySearchTermsOnSave \
  tests/component/core/test_candidate.py::TestCompanySearchTermsLines \
  tests/component/core/test_candidate.py::TestAst524CompanySearchTermsTable \
  tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_update_rejects_blank_company_search_terms \
  tests/component/ui/api/test_api_candidate.py::TestAst524CompanySearchTermsSync
```

**AST-525** narrowed run (blocker **AST-524** tests optional smoke):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst525InflowDiscoveryConfig \
  tests/component/data/database/test_company_search_terms.py::TestAst524CompanySearchTermsTable::test_list_stale_company_search_terms_ordered \
  tests/component/data/database/test_dispatch_tasks.py::TestAst525InflowDiscoveryEligible \
  tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_no_stale_terms_returns_zero_errors \
  tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_happy_path \
  tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_cse_failure_continues \
  tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_searches_only_stale_terms \
  tests/component/core/test_candidate.py::TestCompanySearchTermsLines \
  tests/component/core/test_candidate.py::TestAst525CompanySearchTermsTokenOverlay
```


**AST-526** narrowed run (blocker **AST-524** tests optional smoke):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_candidate.py::TestAst526ArtifactsCompanySearchTermsApi \
  tests/component/frontend/pages/test_ArtifactsCompanySearchTerms.test.tsx
```


## 7.13zh Roster inflow — prefilter + PREFILTER_PASSED locate (**AST-507**, **AST-508**, parent **AST-490**)

Phase 3 (**AST-507**): **`prefilter_company`** uses **`grades_encoded`** decode shape (`jobs[0].grades`), dealbreaker-only **F** with confidence ≥ 2, **`prefilter_score`** on pass, inflow **`NEW → WEBSITE_FOUND`** history → **PREFILTER_PASSED** / **PREFILTER_FAILED**; legacy manual path → **TO_WATCH** / **IGNORE**. Phase 4–5 (**AST-508**): **`PREFILTER_PASSED`** companies enter existing **`find_job_page` → `select_job_page` → `parse_job_list`** via dispatch with **`score_floor`** on the **`dispatch_task`** row (JSON **`company_data.prefilter_score`**); below-floor rows stay unclaimed. Depends on **AST-506** (**WEBSITE_FOUND**). Blocker bible: **AST-506** (**§7.13zg**); **AST-508** build gate **AST-507**.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-507** | Encoded rubric prefilter; dual state targets via `state_history`; config states/transitions | `src/utils/config.py`, `src/core/roster.py` | `tests/component/utils/test_config.py::TestAst507EncodedPrefilterConfig`; `tests/component/core/test_roster.py::{TestPrefilterCompany::test_pass_and_fail_grades_persist_data,TestAst507EncodedPrefilter,TestRunCompanyTask::test_prefilter_pass_and_fail}` |
| **AST-508** | **`dispatch_input_states`** + **`INFLOW_CONFIG.locate`**; company **`score_floor`** claim/count; dispatcher passthrough; **`PREFILTER_PASSED → find_job_page`** | `src/utils/config.py`, `src/data/database.py`, `src/core/dispatcher.py`, `src/core/roster.py` | `tests/component/utils/test_config.py::TestAst508InflowLocateConfig`; `tests/component/data/database/test_dispatch_tasks.py::TestAst508PrefilterPassedEligible`; `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast508_prefilter_passed_dispatch_passes_score_floor`; `tests/component/core/test_roster.py::TestRunCompanyTask::test_prefilter_passed_routes_to_find_job_page` |

**AST-507** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst507EncodedPrefilterConfig \
  tests/component/core/test_roster.py::TestPrefilterCompany::test_pass_and_fail_grades_persist_data \
  tests/component/core/test_roster.py::TestAst507EncodedPrefilter \
  tests/component/core/test_roster.py::TestRunCompanyTask::test_prefilter_pass_and_fail
```

**AST-508** narrowed run (blocker **AST-507** tests optional smoke — **`PREFILTER_PASSED`** + **`prefilter_score`** must exist):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst508InflowLocateConfig \
  tests/component/data/database/test_dispatch_tasks.py::TestAst508PrefilterPassedEligible \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast508_prefilter_passed_dispatch_passes_score_floor \
  tests/component/core/test_roster.py::TestRunCompanyTask::test_prefilter_passed_routes_to_find_job_page
```

## 7.13zk Ad hoc workbench Test in Execution History (**AST-515**, parent **AST-514**)

Workbench **Test** (`POST /api/admin/adhoc/test`) creates **`dispatch_ledger`** rows with **`task_key`** `adhoc-<workbench_task_key>`, **`log_batch_id`**, and **`agent_data`** blocks via **`run_adhoc_workbench_test`** in **`agent.py`**. **Preview** stays ledger-free. Execution History UI (**`AdminPerformanceMonitor`**) unchanged — list/expand/inspect use existing ledger + **`/api/agent_data/<batch_id>`** APIs.
## 7.13zk Execution History — UI agent call prefixes (**AST-515**, **AST-521**, parent **AST-514**)

Parent **AST-514** labels non-dispatch UI provider calls in **`dispatch_ledger`**. **AST-515**: Ad Hoc workbench **Test** → **`adhoc-<workbench_task_key>`**. **AST-521**: Artifacts **Generate / Regenerate** and Board Searches craft **Generate** → **`user-<task_key>`** with prefixed **`batch_id`**; **`do_task`** still uses the real craft key for **`agent_data`**. **Preview** paths stay ledger-free. **Dispatch** / Scheduled Actions **Run** keep plain **`task_key`**. Execution History UI (**`AdminPerformanceMonitor`**) unchanged — list/expand/inspect use existing ledger + **`/api/agent_data/<batch_id>`** APIs.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-515** | Ledger + agent_data wrapper; **`adhoc_test`** route swap | `src/core/agent.py` (`run_adhoc_workbench_test`), `src/ui/api/api_admin.py` (`adhoc_test`) | `tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger`; `tests/component/ui/api/test_api_admin.py::{TestAdhocRoutes,TestApiAdminBranchGaps}` (adhoc preview/test paths) |
| **AST-521** | **`user-`** ledger prefix on candidate artifact + board search craft generate | `src/core/candidate.py` (`run_candidate_artifact_generation`), `src/core/boards.py` (`run_board_search_generation`), `src/ui/api/api_candidate.py`, `src/ui/api/api_boards.py` (delegates only) | `tests/component/core/test_candidate.py::TestRunCandidateArtifactGeneration`; `tests/component/core/test_boards_generate_ast521.py::TestRunBoardSearchGenerationAst521`; optional API smoke: `tests/component/ui/api/test_api_boards.py::TestBoardSearchRoutes::test_generate_delegates_to_core` |

**AST-515** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst515AdhocWorkbenchLedger \
  tests/component/ui/api/test_api_admin.py::TestAdhocRoutes \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_adhoc_test_decodes_encoded_payload \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_adhoc_test_hydrates_encoded_payload_with_entities \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_adhoc_test_skips_decode_without_response_text
```

Dispatch-only Execution History regression (no UI diff this child): **`tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx`** per **§7.13k** when parent UAT runs full epic.
**AST-521** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestRunCandidateArtifactGeneration \
  tests/component/core/test_boards_generate_ast521.py::TestRunBoardSearchGenerationAst521
```

Dispatch-only Execution History regression (no UI diff these children): **`tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx`** per **§7.13k** when parent UAT runs full epic.

## 7.13zl Candidate resume structure — per-candidate catalog + craft_resume_base, builder + job keys, base resume UI (**AST-517**, **AST-518**, **AST-519**, parent **AST-477**)

**`artifacts.resume_structure`** holds the candidate-owned section catalog (id, title, enabled, order, **`job_agent_editable`**); **`artifacts.base_resume`** holds string content keyed by enabled section ids. **`craft_resume_base`** response schema requires **`resume_structure`**; **`parse_candidate_resume`** persists both blobs. Legacy global **`base_resume_structure`** and **`base_resume.accent_color`** are read shims only. **AST-518** drives **`builder.py`** body emission and **`tracker.py`** job **`resume_content`** filtering to catalog subset + contact snapshot; cover letter stored as **`Subject`** / **`Letter`** with legacy **`re_line`** / **`body`** read shims. **AST-519** exposes **`GET …/resume_structure`**, filters **`base_resume`** keys on PUT, and drives **Base Resume Content** tabs + accent from per-candidate structure (not global shapes).

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-517** | Config defaults + normalize/resolve/split helpers; parse persistence; candidate isolation | `src/utils/config.py`, `src/core/candidate.py` | `tests/component/utils/test_config.py::TestAst517ResumeStructureConfig`; `tests/component/utils/test_config.py::TestStringifyResponseSchema::test_builds_schema_example_envelope`; `tests/component/core/test_candidate.py::TestAst517ResumeStructure`; `tests/component/core/test_candidate.py::TestParseCandidateResume`; `tests/component/core/test_candidate.py::TestParseCandidateResumeExtended` |
| **AST-518** | Structure-ordered builder HTML; accent from structure; job **`resume_content`** orphan strip + contact snapshot; cover letter **`Subject`**/**`Letter`** | `src/core/builder.py`, `src/core/candidate.py`, `src/core/tracker.py`, `src/utils/config.py` | `tests/component/core/test_candidate.py::TestAst518ResumeStructureProjection`; `tests/component/core/test_builder.py::TestAst518BuilderResumeStructure`; `tests/component/core/test_tracker.py::TestAst518JobResumeArtifacts`; `tests/component/core/test_builder.py::TestBuilderHelpers`; `tests/component/core/test_tracker.py::{TestAst302JobArtifacts,TestAst309CoverLetterArtifact,TestPersistJobArtifactFromParsed}` |
| **AST-519** | **`enabled_resume_structure_sections`** / **`filter_base_resume_to_structure`**; **`GET /api/candidates/<id>/resume_structure`**; PUT orphan strip + structure accent merge; Base Resume Content page + **`useCandidateResumeStructure`** | `src/core/candidate.py`, `src/ui/api/api_candidate.py`, `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx`, `src/ui/frontend/src/components/ArtifactEditor.tsx` | `tests/component/core/test_candidate.py::TestAst519ResumeStructureUiHelpers`; `tests/component/ui/api/test_api_candidate.py::TestAst519ResumeStructureApi`; `tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx` (**§6c** routed page); `tests/component/frontend/components/test_ArtifactEditor.test.tsx` (structureSections mode) |

**AST-517** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst517ResumeStructureConfig \
  tests/component/utils/test_config.py::TestStringifyResponseSchema::test_builds_schema_example_envelope \
  tests/component/core/test_candidate.py::TestAst517ResumeStructure \
  tests/component/core/test_candidate.py::TestParseCandidateResume \
  tests/component/core/test_candidate.py::TestParseCandidateResumeExtended
```

**AST-518** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst518ResumeStructureProjection \
  tests/component/core/test_builder.py::TestAst518BuilderResumeStructure \
  tests/component/core/test_tracker.py::TestAst518JobResumeArtifacts \
  tests/component/core/test_builder.py::TestBuilderHelpers \
  tests/component/core/test_tracker.py::TestAst302JobArtifacts \
  tests/component/core/test_tracker.py::TestAst309CoverLetterArtifact \
  tests/component/core/test_tracker.py::TestPersistJobArtifactFromParsed
```

**AST-519** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst519ResumeStructureUiHelpers \
  tests/component/ui/api/test_api_candidate.py::TestAst519ResumeStructureApi
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx \
  ../../../tests/component/frontend/components/test_ArtifactEditor.test.tsx \
  -t "structureSections|Base Resume Content|resume_structure"
```

## 7.13zj Job-scoped artifact prompt tokens (**AST-513**, parent **AST-313**)

Five **`{$VISIBLE_JD}`** / **`{$ANALYSIS_*}`** tokens register in **`TOKEN_SOURCES`** with **`source: job`**. Values are precomputed in **`build_job_token_context`** (`consult.py`) and threaded as **`job_context`** through **`resolve_tokens`**, **`do_task`**, **`preview_task_prompt`**, admin preview, and Ad-hoc **`_resolve_adhoc`** when **`entity_type === job`**. Single-job scope only (**`_single_job_in_scope`**).

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-513** | Registry + formatter + single-job threading + Manage Tasks preview job id | `src/utils/config.py`, `src/core/consult.py`, `src/core/agent.py`, `src/core/candidate.py`, `src/ui/api/api_admin.py`, `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | `tests/component/utils/test_config.py::TestAst513JobTokens`; `tests/component/core/test_consult.py::TestAst513JobTokenContext`; `tests/component/core/test_agent.py::TestAst513JobContext`; `tests/component/ui/api/test_api_admin.py::{TestTaskRoutes::test_preview_task_forwards_astral_job_id,TestAdhocHelpers::test_resolve_adhoc_job_entity_resolves_visible_jd_token}`; `tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx` (job preview **`astral_job_id`**) |

**AST-513** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst513JobTokens \
  tests/component/core/test_consult.py::TestAst513JobTokenContext \
  tests/component/core/test_agent.py::TestAst513JobContext \
  tests/component/ui/api/test_api_admin.py::TestTaskRoutes::test_preview_task_forwards_astral_job_id \
  tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_resolve_adhoc_job_entity_resolves_visible_jd_token
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminTaskPrompts.test.tsx \
  -t "astral_job_id"
```

## 7.13zi Candidate profile — middle name data and display name (**AST-510**, **AST-511**, parent **AST-509**)

Optional **`profile.middle`** on candidate data contract (**AST-510**); **`{$MIDDLE_NAME}`** token; **`profile_display_name`** composes **`First Middle Last`** for resume HTML header (**AST-510**). **AST-511** wires shape-driven Candidate Profile contact grid and Admin Manage Candidates add/edit modals. No migration.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-510** | DATA_SHAPES + TOKEN_SOURCES; display helper; builder wiring; merge round-trip | `src/utils/config.py`, `src/utils/formatting.py`, `src/core/builder.py`, `src/core/candidate.py` | `tests/component/utils/test_formatting.py::TestProfileDisplayName`; `tests/component/utils/test_config.py::{TestGetTokens,TestResolveTokens::test_resolves_middle_name_token,TestAst510MiddleNameConfig}`; `tests/component/core/test_builder.py::TestBuilderHelpers::{test_applies_profile_middle_to_candidate_name,test_build_resume_from_job_emits_middle_name_in_html}`; `tests/component/core/test_candidate.py::TestAst510ProfileMiddleRoundTrip` |
| **AST-511** | Candidate Profile shape-driven middle field + save; Admin create/edit **`profile.middle`** | `src/ui/frontend/src/pages/AdminManageCandidates.tsx`, `src/ui/frontend/src/pages/CandidateProfile.tsx` (verify only) | `tests/component/frontend/pages/test_CandidateProfile.test.tsx` (**§6c** — routed page + middle save payload); `tests/component/frontend/pages/test_AdminManageCandidates.test.tsx` (middle in POST/PUT; empty middle create) |

**AST-510** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_formatting.py::TestProfileDisplayName \
  tests/component/utils/test_config.py::TestGetTokens \
  tests/component/utils/test_config.py::TestResolveTokens::test_resolves_middle_name_token \
  tests/component/utils/test_config.py::TestAst510MiddleNameConfig \
  tests/component/core/test_builder.py::TestBuilderHelpers::test_applies_profile_middle_to_candidate_name \
  tests/component/core/test_builder.py::TestBuilderHelpers::test_build_resume_from_job_emits_middle_name_in_html \
  tests/component/core/test_candidate.py::TestAst510ProfileMiddleRoundTrip
```

**AST-511** narrowed run (Vitest — run from repo root; **`run_component_tests.sh`** with only these paths skips pytest and may not invoke Vitest):

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_CandidateProfile.test.tsx \
  ../../../tests/component/frontend/pages/test_AdminManageCandidates.test.tsx
```

## 7.13zn Per-hop `dispatch_ledger` for `run_next` chains (**AST-531**, **AST-532**, parent **AST-528**)

**AST-528 (parent):** Execution History lists **one `dispatch_ledger` row per executed LLM hop** in a **`run_next`** chain — distinct **`batch_id`**, hop **`task_key`**, scoped **`agent_data`** and app logs per hop (reverses **AST-303** single-batch-across-hops for history only). **AST-531**: backend — hop open/close in **`do_task`**, dispatcher **`entity_batch_id`** (entity claim) vs hop audit **`batch_id`**, craft/board outer-ledger skip when **`run_next`** is set. **AST-532**: Execution History UI verification (sibling). Does **not** cover hop debug logging (**AST-530**, **AST-527**) or caller-token propagation (**AST-529**).

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-531** | Per-hop ledger rows; dispatch-level ledger skipped when chain planned | `src/core/agent.py`, `src/core/dispatcher.py`, `src/core/candidate.py`, `src/core/boards.py` | `tests/component/core/test_agent.py::TestAst531RunNextHopLedger`; `tests/component/core/test_dispatcher.py::TestDispatchOne::test_run_next_chain_skips_dispatch_level_ledger` |
| **AST-532** | Execution History UI — one row per hop; batch_id-scoped logs + agent_data inspect; adhoc/user/dispatch regression | `src/ui/frontend/src/pages/AdminPerformanceMonitor.tsx` (no source diff expected — **AST-515** batch scoping) | `tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx` — **`AST-532 per-hop execution history UI`** describe |

**AST-531** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst531RunNextHopLedger \
  tests/component/core/test_dispatcher.py::TestDispatchOne::test_run_next_chain_skips_dispatch_level_ledger
```

**AST-532** narrowed run:

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx \
  -t "AST-532 per-hop"
```

Dispatch-only Execution History regression when parent UAT runs full epic: full **`test_AdminPerformanceMonitor.test.tsx`** per **§7.13k**.

## 7.13zo Daisy-chain hop debug logging (**AST-530**, parent **AST-527**)

Structured **`run_next`** hop observability: parent → child **`task_key`**, **`batch_id`**, per-**`CALLER_*`** populated/empty + length; chain-entry vs mid-chain warning shape in **`resolve_tokens`**; mid-chain fail-fast when a referenced **`{$CALLER_*}`** resolves empty (no LLM call). Debug on the dispatch entry hop propagates to recursive hops. Does **not** fix caller propagation (**AST-529**) or Execution History rows (**AST-528**).

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-530** | **`CALLER_HOP_TOKEN_NAMES`**; hop-boundary INFO logs; chain-entry marker; mid-chain empty-caller guard | `src/utils/config.py` (`resolve_tokens`, `CALLER_HOP_TOKEN_NAMES`), `src/core/agent.py` (`do_task` hop helpers) | `tests/component/utils/test_config.py::TestAst530ChainHopResolveTokens`; `tests/component/core/test_agent.py::TestDoTask::{test_chain_entry_log,test_hop_boundary_log_on_run_next,test_mid_chain_empty_caller_skips_api,test_debug_flag_passed_to_child}` |

**AST-530** narrowed run (include daisy-chain regression from parent AC #5). Chain-hop **`TestDoTask`** cases pin **`get_active_llm_provider`** to **`anthropic`** and use the AST-501 envelope in mocks — no **`ASTRAL_LLM_PROVIDER`** export required for pytest-only runs:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst530ChainHopResolveTokens \
  tests/component/core/test_agent.py::TestDoTask::test_chain_entry_log \
  tests/component/core/test_agent.py::TestDoTask::test_hop_boundary_log_on_run_next \
  tests/component/core/test_agent.py::TestDoTask::test_mid_chain_empty_caller_skips_api \
  tests/component/core/test_agent.py::TestDoTask::test_debug_flag_passed_to_child \
  tests/component/core/test_agent.py::TestDoTask::test_chains_run_next_when_configured \
  tests/component/core/test_agent.py::TestChainContext
```

## 7.13zp Dispatch row `task_key` honesty (**AST-534**, **AST-535**, parent **AST-533**)

**AST-533 (parent):** Scheduled Actions **Run** must execute the **`dispatch_task.task_key`** on the row — **`trigger_state`** claims entities only. **AST-534**: job consult + artifact entry via row **`task_key`**. **AST-535**: triple unique **`(candidate_id, task_key, trigger_state)`** and company roster **`TO_WATCH`** trio routing (`find_job_page`, `select_job_page`, `parse_job_list` each run their task). **`_INPUT_STATE_TO_TASK`** is not dispatch routing.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-534** | Row **`task_key`** drives first hop; **`anticipate_scan`** @ **`BUILD_ARTIFACTS`** does not enter **`contemplate_job`** / cover letter when unlinked | `src/core/dispatcher.py`, `src/core/consult.py`, `src/core/agent.py` | `tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty`; `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast534_forwards_dispatch_task_key_to_consult`; `tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch` |
| **AST-535** | Triple unique schema; **`TO_WATCH`** rows route by row **`task_key`**; admin 409 names triple | `src/data/database.py`, `src/core/roster.py`, `src/core/consult.py`, `src/ui/api/api_admin.py` | `tests/component/data/database/test_dispatch_tasks.py::TestAst535DispatchTaskTripleUnique`; `tests/component/core/test_roster.py::TestAst535ToWatchDispatchTaskKeyRouting`; `tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast535_create_dispatch_task_triple_unique_409` |

**AST-534** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast534_forwards_dispatch_task_key_to_consult
```

**AST-535** narrowed run (includes **AST-534** job forward regression — `test_ast534_forwards_dispatch_task_key_to_consult` must stay green after product fix on **`dispatcher._run_unified`**):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_dispatch_tasks.py::TestAst535DispatchTaskTripleUnique \
  tests/component/core/test_roster.py::TestAst535ToWatchDispatchTaskKeyRouting \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast535_create_dispatch_task_triple_unique_409 \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast534_forwards_dispatch_task_key_to_consult
```

## 7.13zq Config + UI manifest — lookup lists track live config (**AST-549**, **AST-550**, parent **AST-484**)

**AST-484 (parent):** Admin dispatch and job/company UI vocabulary must track live config — no parallel seed dicts or hardcoded frontend manifest. **AST-549** removes **`_DISPATCH_TASK_SEED`**, **`dispatch_task_seed_templates()`**, and **`_DISPATCH_TASK_TRIGGER_SEED`** / **`DISPATCH_TASK_SEED_KEYS`**. **`dispatch_task_admin_defaults(task_key)`** derives **`entity_type`**, **`trigger_state`**, **`sort_by`**, **`batch_call_mode`** from **`TASK_CONFIG`**, roster/inflow/board config blocks, and state registries; **`DISPATCH_SCHEDULABLE_TASK_KEYS`** bounds schedulable rows (artifact-only keys like **`anticipate_scan`** stay out). **`GET /api/admin/dispatch_tasks/task_keys`** is **TASK_CONFIG-first** with schedulable merge — seed cannot override config. **AST-550** deletes **`StateUiContext.EMPTY`** (duplicate of **`build_state_ui_manifest()`**); runtime vocabulary from **`GET /api/state_ui_manifest`** only; **`loadState`** loading/error guards on manifest consumers; legacy sections for row states absent from the current manifest.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-549** | Config defaults; scored-trigger scan without seed loop; admin **`task_keys`** + adhoc preview | `src/utils/config.py`, `src/data/database.py`, `src/ui/api/api_admin.py` | **`TestAst549DispatchAdminDefaults`**; **`TestAst471DispatchConfigHelpers`** (updated); **`TestAst505InflowDiscoveryConfig::test_inflow_discovery_dispatch_admin_defaults`**; **`TestAst506InflowResolveConfig::test_inflow_resolve_website_dispatch_admin_defaults`**; **`TestApiAdminBranchGaps::test_ast549_task_keys_config_derivation_authoritative`**; **`TestDispatchTasks::test_list_dispatch_tasks_and_keys`** |
| **AST-550** | API-only **`StateUiContext`**; legacy job sections; shared test fixture (not production seed) | `StateUiContext.tsx`, `lib/stateUiSections.ts`, `JobsInReview.tsx`, `JobsSkipped.tsx`, `JobsRecommended.tsx`, company pages + modals | **`tests/component/frontend/contexts/test_StateUiContext.test.tsx`** (loading → ready; error → null manifest); **`tests/component/frontend/pages/test_JobsInReview.test.tsx`** (legacy unmapped state section); **`tests/component/frontend/pages/test_JobsRecommended.test.tsx`** (§6c routed page regression); **`tests/component/frontend/fixtures/stateUiManifestFixture.ts`** + **`page-mocks.ts`** (`installBaseApiMocks` serves fixture) |

**AST-549** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst549DispatchAdminDefaults \
  tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_inflow_discovery_dispatch_admin_defaults \
  tests/component/utils/test_config.py::TestAst506InflowResolveConfig::test_inflow_resolve_website_dispatch_admin_defaults \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast549_task_keys_config_derivation_authoritative \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast485_dispatch_task_keys_roster_seeds_minus_locate_template \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast485_adhoc_entities_select_job_page_fallbacks_to_config_defaults \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_dispatch_task_keys_includes_task_config_registry \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_list_dispatch_tasks_and_keys
```

**AST-550** narrowed run (Vitest paths are **not** forwarded by `run_component_tests.sh` trailing args — run Vitest explicitly):

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/contexts/test_StateUiContext.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsInReview.test.tsx \
  ../../../tests/component/frontend/pages/test_JobsRecommended.test.tsx \
  ../../../tests/component/frontend/test_App.test.tsx
```

## 7.13zs Structure-aligned resume chain + BUILD_ARTIFACTS gate (**AST-551**, **AST-552**, parent **AST-300**)

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

## 7.13zt Backend debug logging contract and shared helper (**AST-554**, parent **AST-538**)

**AST-538 (parent):** Mandatory backend debug contract in **`docs/ASTRAL_CODE_RULES.md`** §1.5.1, shared emission API on **`_PrefixedLogger`** (`debug_index`, `debug_detail`, `debug_detail_block`), pure **`truncate_debug_content`** / **`format_debug_index_header`**. Parent AC **7** — Betty tests **gating + truncation math only** (no log-string golden files). Operational backfill (**inflow_discovery** per-index traces, AC 2/4 spot-check) is **AST-557**; nav rename **AST-555**; **review-astral** rubric **AST-556**.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-554** | Constants, truncation helper, index header formatter, debug-gated INFO emission | `src/utils/logging.py`, `docs/ASTRAL_CODE_RULES.md` §1.5.1 | **`TestTruncateDebugContent`**, **`TestFormatDebugIndexHeader`**, **`TestPrefixedLoggerDebugGating`** in **`test_debug_logging.py`**; regression **`test_logging_batch.py`** |

**AST-554** narrowed run (pytest-only — python-only child; avoids Vitest tail / **AST-511** cross-ticket noise on engineer worktrees):

```bash
.venv/bin/python -m pytest tests/component/utils/test_debug_logging.py tests/component/utils/test_logging_batch.py -q
```

**`[qa-handoff]` return (2026-06-03):** Ada **`test-astral`** — `run_component_tests.sh` with trailing paths still invoked full Vitest on **`dev-ada`**; manifest uses direct **`pytest`** gate (13 tests). Harness on **`dev-betty`** skips Vitest when trailing paths are set (**Appendix A**).

## 7.13zr Candidate intake chat session (**AST-539**)

Estelle-led intake: **`candidate_intake_session`** store (resume-after-close), REST under **`/api/candidates/<id>/intake/…`**, three **`do_task`** keys with ledger prefix **`intake-{task_key}`**, interview JSON validation, one **`build_request`** per session, build persistence via **`save_candidate_data`** + **`sync_company_search_terms_from_text`** + **`check_context_complete`**. Katherine modal UI (**AST-559**) consumes Ada's API (**AST-558**) — UI mocks must match **`IntakeSessionDto`** (`session_id`, `transcript[].text`, `can_build`, `build_completed`).

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-558** | Session CRUD + turns + build; source material persistence; ledger parity | `src/utils/config.py` (`INTAKE_CONFIG`, three `TASK_CONFIG` rows), `src/data/database.py`, `src/core/intake.py`, `src/core/agent.py` (snapshot hook), `src/ui/api/api_intake.py`, `src/ui/server.py` | `tests/component/core/test_intake.py`; `tests/component/ui/api/test_api_intake.py` |
| **AST-559** | Intake nav confirm gate; auto-start from persisted `context.*` (no modal paste / Start interview); thread, `can_build` gate, one build per session, resume-after-close | `src/utils/config.py` (`NAV_CONFIG`), `src/ui/frontend/src/routes.tsx`, `src/ui/frontend/src/pages/CandidateIntake.tsx`, `src/ui/frontend/src/components/IntakeChatModal.tsx`, `src/ui/frontend/src/App.css` | `tests/component/frontend/pages/test_CandidateIntake.test.tsx` (§6c routed page — confirm gate; modal — auto-start, gate, build-once) |
| **AST-578** | UAT: hide `initiate_candidate` user payload; hold copy while loading / when active session lacks visible assistant message | `src/ui/frontend/src/components/IntakeChatModal.tsx` | `tests/component/frontend/pages/test_CandidateIntake.test.tsx` — `IntakeChatModal` describe: transcript filter, hold on empty / assistant-less resume |
| **AST-579** | UAT: force `ready_to_build` false on initiate turn (never enable Generate Profile on turn 1) | `src/core/intake.py` (`create_intake_session_and_start`) | `tests/component/core/test_intake.py` — `test_initiate_turn_forces_ready_to_build_false_when_model_returns_true` |

**AST-558** narrowed run (pytest-only — harness skips Vitest when trailing paths are set):

```bash
./scripts/testing/run_component_tests.sh tests/component/core/test_intake.py
./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_intake.py
```

Equivalent direct gate:

```bash
.venv/bin/python -m pytest tests/component/core/test_intake.py tests/component/ui/api/test_api_intake.py -q
```

**AST-559** narrowed run (merge **`origin/sub/AST-539/AST-558-intake-session-api`** on engineer tree before replay if API symbols missing):

```bash
cd src/ui/frontend && npx tsc -b --noEmit
cd src/ui/frontend && npm run test:component -- --run tests/component/frontend/pages/test_CandidateIntake.test.tsx
```

**AST-578** narrowed run (Vitest — transcript filter + hold regressions only; merge this **`sub/*`** tip on engineer tree):

```bash
cd src/ui/frontend && npx tsc -b --noEmit
cd src/ui/frontend && npm run test:component -- --run tests/component/frontend/pages/test_CandidateIntake.test.tsx
```

**AST-579** narrowed run (pytest-only — initiate turn readiness gate; merge this **`sub/*`** tip on engineer tree):

```bash
.venv/bin/python -m pytest tests/component/core/test_intake.py::TestIntakeSessionFlow::test_initiate_turn_forces_ready_to_build_false_when_model_returns_true -q
```

**`[qa-handoff]` return (2026-06-03):** **AST-559** mocks updated for AST-558 REST paths (`/intake/sessions`, `/sessions/active`, `…/turns`, `…/build`); materials sent in session **POST** body (no **`PUT …/data`** on start).

**UAT UX delta (2026-06-05):** Page **Start Intake** confirm before modal; **`IntakeChatModal`** receives persisted **`materials`** + **`autoStart`** — no in-modal paste or **Start interview**; session **POST** fires after active **GET** when no session. **AST-578:** hide synthetic **`initiate_candidate`** user row; show **`INTAKE_HOLD_COPY`** until a visible assistant bubble exists.

**Rollup reconcile (AST-578):** Betty publish ref **`origin/sub/AST-539/AST-578-uat-intake-hold-on-resume-estelle-first-transcript-empty`** — one **§7.13zr** table row; **`rollup-child`** merges into **`origin/ftr/ast-539-candidate-intake-chat-session`**.

**Rollup reconcile (AST-579):** Betty publish ref **`origin/sub/AST-539/AST-579-uat-force-ready-to-build-false-on-initiate-candidate-turn`** — one **§7.13zr** table row; **`rollup-child`** merges into **`origin/ftr/ast-539-candidate-intake-chat-session`**. **Stale sub reconcile (2026-06-05):** bible base from **`origin/ftr/ast-539-candidate-intake-chat-session`** **AST-578** rows; kept **AST-579** manifest rows only.

## 7.13zu Improve debug logging — Agent Ad Hoc nav rename (**AST-555**, parent **AST-538**)

**`NAV_CONFIG`** Admin item and **`AdminAnthropicAdHoc`** page **`<h1>`** show **Agent Ad Hoc** (path unchanged **`/admin/anthropic_ad_hoc`**). No API route or component rename.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-555** | Sidebar + page title label rename | `src/utils/config.py` (`NAV_CONFIG`), `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` | `tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_nav_config_admin_agent_ad_hoc_label`; `tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx` (**§6c** routed page) |

**AST-555** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_nav_config_admin_agent_ad_hoc_label
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx
```

## 7.13zv `draft_job_resume` schema alignment + validation surfacing (**AST-594**, parent **AST-592**)

Retire **AST-450** graded-consult contract on **`draft_job_resume`**: metadata-only **`TASK_CONFIG`** with **`resume_section_payload: True`**; runtime catalog whitelist via **`normalize_draft_job_resume_agent_payload`** / **`validate_draft_job_resume_payload`** (**AST-536**-style flatten); hop failures surface **`Validation failed:`** RESPONSE bodies + ERROR logs (**AST-531** ledger unchanged).

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-594** | Structure-keyed section JSON; reject `grades` / unknown keys; validation message on hop row | `src/utils/config.py`, `src/core/candidate.py`, `src/core/agent.py` | `tests/component/utils/test_config.py::TestAst594DraftJobResumeSchema`; `tests/component/core/test_candidate.py::TestAst594DraftJobResumePayload`; `tests/component/core/test_agent.py` — `-k "draft_job_resume"` (acceptance, unknown key, disallowed `grades`, RESPONSE **`Validation failed:`** prefix) |
| **AST-604** | Section key aliases (`candidate_contact` → `candidate_contact_detail`) before catalog whitelist | `src/core/candidate.py` | `tests/component/core/test_candidate.py::TestAst594DraftJobResumePayload::test_normalize_renames_candidate_contact_alias` |
| **AST-607** | `{$BASE_RESUME}` token emits section-id-keyed JSON (not markdown `###` sections); legacy label/content arrays map via structure title | `src/core/candidate.py` (`format_base_resume_for_token`), `src/utils/config.py` (`resume_sections_json` serialize) | `tests/component/core/test_candidate.py::TestAst607BaseResumeToken`; `tests/component/utils/test_config.py::TestResolveTokens::test_base_resume_token_emits_section_json_not_markdown` |

**AST-594** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst594DraftJobResumeSchema \
  tests/component/core/test_candidate.py::TestAst594DraftJobResumePayload \
  tests/component/core/test_agent.py -k "draft_job_resume"
```

## 7.13zw Prefilter consult-parity hydration (**AST-603**, parent **AST-602**)

**AST-603** routes **`prefilter_company`** model responses through shared **`consult._normalize_rubric_task_response`** (dict JSON, letter-pipe, JSON string, compact encoded + **`JOB:`** / **`CULT:`** tails) before **`do_task`** schema validation; roster hydrates grade **`reason`** via **`_hydrate_grade_reasons_from_rubric`**. Preserves **AST-507** pass/fail/score semantics and inflow **PREFILTER_*** vs legacy **TO_WATCH** / **IGNORE** mapping. Output type **`grades_encoded_prefilter_links`**.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-603** | Shared rubric normalizer; **`do_task`** pre-decode skip for rubric encoded tasks; roster hydration + link list persistence | `src/core/consult.py`, `src/core/agent.py`, `src/core/roster.py`, `src/utils/config.py` | `tests/component/core/test_agent.py::TestAst603RubricNormalize`; `tests/component/core/test_roster.py::TestAst603ConsultParityHydration`; `tests/component/utils/test_config.py::TestAst507EncodedPrefilterConfig::test_prefilter_company_grades_encoded`; **AST-507** regression rows in **§7.13zh** |

**AST-603** narrowed run (includes **AST-507** prefilter smoke):

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst603RubricNormalize \
  tests/component/core/test_roster.py::TestAst603ConsultParityHydration \
  tests/component/core/test_roster.py::TestAst507EncodedPrefilter \
  tests/component/core/test_roster.py::TestPrefilterCompany::test_pass_and_fail_grades_persist_data \
  tests/component/utils/test_config.py::TestAst507EncodedPrefilterConfig
```

## 7.13zx Rebuild AST-581 Preview Materials JAR (**AST-605**, parent **AST-599**)

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

## 7.13zy Prefilter retry routing (**AST-606**, parent **AST-602**)

**AST-606** replaces **`PREFILTER_UNKNOWN`** on active prefilter failure paths with **`WEBSITE_FOUND_RETRY`** (decode/hydration/missing-parse / API body retryable) vs **`ERROR_PREFILTER`** (bare API failure). **`ROSTER_CONFIG["prefilter"]`** uses **`retry_state`**; dispatch seeds **`prefilter`** from **`WEBSITE_FOUND_RETRY`**. **`run_company_task`** treats **`WEBSITE_FOUND_RETRY`** like **`WEBSITE_FOUND`**.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-606** | **`_prefilter_fail`** retry vs error routing; **`WEBSITE_FOUND_RETRY`** state + transitions; dispatch retry seed | `src/core/roster.py`, `src/utils/config.py`, `src/data/database.py` | `tests/component/core/test_roster.py::TestPrefilterCompany::test_api_failure_and_missing_parsed_response`; `tests/component/utils/test_config.py::TestAst507EncodedPrefilterConfig::test_company_states_and_transitions` |

**AST-606** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestPrefilterCompany::test_api_failure_and_missing_parsed_response \
  tests/component/utils/test_config.py::TestAst507EncodedPrefilterConfig::test_company_states_and_transitions
```

## 7.13zz Compound BUILD_ARTIFACTS hop states (**AST-595** · **AST-596** · **AST-597**, parent **AST-593**)

**AST-593 (parent):** Mid-chain artifact resume — replace flat **`BUILD_ARTIFACTS`** with compound **`BUILD_ARTIFACTS.<task_key>`** per resume hop; explicit **`hop_task_keys`** order in **`BUILD_CONFIG`**; **Generate Artifacts** / **approve_artifacts** → first compound state (**`BUILD_ARTIFACTS.anticipate_scan`** v1). Per-hop success transitions (**AST-597**) and **`agent_data`** caller hydration are siblings — manifest rows below split registry/entry, claim/release, and transition/hydration.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-595** | Compound **`JOB_STATES`** + helpers; **`RECOMMENDED_JOB_STATES`** / UI manifest; dispatch **`trigger_state`** per hop; generate/cancel/approve entry | `src/utils/config.py`, `src/core/tracker.py`, `src/ui/api/api_jobs.py` | `tests/component/utils/test_config.py::TestAst595CompoundBuildArtifactsHopStates`; `tests/component/utils/test_config.py::TestAst479LikePassStates::test_recommended_job_states_post_synthesis_exclude_passed_like`; `tests/component/utils/test_config.py::TestAst520AnticipateScanTaskKey::test_build_artifacts_entry_unchanged`; `tests/component/utils/test_config.py::TestBuildStateUiManifest::{test_ast522_recommended_manifest_sections_and_phase_columns,test_ast562_recommended_primary_actions_by_state,test_ast562_recommended_prior_states_allow_cancel_from_build}`; `tests/component/utils/test_config.py::TestAst549DispatchAdminDefaults::test_contemplate_job_artifact_trigger_sort`; `tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions::{test_start_artifact_build_from_recommended,test_cancel_from_mid_hop_compound_state,test_cancel_rejects_wrong_state}`; `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::{test_list_recommended_and_default,test_approve_artifacts_from_recommended,test_approve_artifacts_wrong_state_returns_409,test_approve_artifacts_missing_job_returns_404}`; `tests/component/ui/api/test_api_jobs.py::TestAst562GenerateCancelRoutes::{test_generate_artifacts_happy_path,test_cancel_artifact_build_happy_path,test_cancel_artifact_build_409_wrong_state}` |
| **AST-596** | Mid-chain dispatch claim: resume hop **`task_key`** must match compound **`trigger_state`**; hop failure **`release_job_dispatch_claim`** (no **`BUILD_FAILED`**, no resume wipe) | `src/core/consult.py`, `src/core/dispatcher.py`, `src/core/tracker.py` | `tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::{test_routes_build_artifacts_to_artifact_entry_batch,test_artifact_entry_batch_runs_chain_then_cover_letter_for_contemplate_job,test_artifact_entry_batch_errors_skip_cover_letter,test_artifact_entry_batch_empty_persist_releases_claim}`; `tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty::{test_anticipate_scan_entry_skips_contemplate_job_and_cover_letter,test_build_artifacts_state_does_not_imply_contemplate_job_without_dispatch_key,test_mid_chain_compound_trigger_claims_matching_entry,test_dispatch_row_mismatch_skips_artifact_entry}`; `tests/component/core/test_consult.py::TestAst596MidChainDispatchClaimRelease::test_release_job_dispatch_claim_delegates_to_database`; `tests/component/core/test_dispatcher.py::TestRunUnified::{test_ast534_forwards_dispatch_task_key_to_consult,test_ast596_resume_hop_mismatch_skips_claim}` |
| **AST-597** | Per-hop **`BUILD_ARTIFACTS.<task_key>`** transition after successful resume hop; mid-chain entry hydrates **`{$CALLER_*}`** from stored **`agent_data`** (no upstream LLM re-run); Style D **`caller_source`** debug on resume hops | `src/core/agent.py` | `tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions`; `tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_artifact_entry_batch_runs_chain_then_cover_letter_for_contemplate_job` (terminal **`CANDIDATE_REVIEW`** regression) |

**AST-595** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst595CompoundBuildArtifactsHopStates \
  tests/component/utils/test_config.py::TestAst479LikePassStates::test_recommended_job_states_post_synthesis_exclude_passed_like \
  tests/component/utils/test_config.py::TestAst520AnticipateScanTaskKey::test_build_artifacts_entry_unchanged \
  tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast522_recommended_manifest_sections_and_phase_columns \
  tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast562_recommended_primary_actions_by_state \
  tests/component/utils/test_config.py::TestBuildStateUiManifest::test_ast562_recommended_prior_states_allow_cancel_from_build \
  tests/component/utils/test_config.py::TestAst549DispatchAdminDefaults::test_contemplate_job_artifact_trigger_sort \
  tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions::test_start_artifact_build_from_recommended \
  tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions::test_cancel_from_mid_hop_compound_state \
  tests/component/core/test_tracker.py::TestAst562ArtifactBuildTransitions::test_cancel_rejects_wrong_state \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_recommended_and_default \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_from_recommended \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_wrong_state_returns_409 \
  tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_approve_artifacts_missing_job_returns_404 \
  tests/component/ui/api/test_api_jobs.py::TestAst562GenerateCancelRoutes::test_generate_artifacts_happy_path \
  tests/component/ui/api/test_api_jobs.py::TestAst562GenerateCancelRoutes::test_cancel_artifact_build_happy_path \
  tests/component/ui/api/test_api_jobs.py::TestAst562GenerateCancelRoutes::test_cancel_artifact_build_409_wrong_state
```

**AST-596** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch \
  tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty \
  tests/component/core/test_consult.py::TestAst596MidChainDispatchClaimRelease \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast534_forwards_dispatch_task_key_to_consult \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast596_resume_hop_mismatch_skips_claim
```

**AST-597** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_artifact_entry_batch_runs_chain_then_cover_letter_for_contemplate_job
```

## 7.13zza Stytch auth client and swappable utils (**AST-610**, **AST-611**, parent **AST-609**)

**AST-609 (parent):** Swap-friendly authentication — Stytch B2C session JWT in **`src/external/stytch.py`**, provider-agnostic **`src/utils/auth.py`** with registerable **`TokenAuthenticator`** (AST-611 wires **`register_token_authenticator(stytch.authenticate_session_jwt)`** via **`src/core/auth_bootstrap.py`**). **`AUTH_CONFIG`** admin lists from env.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-610** | Stytch JWT validate + user dict mapping; **`normalize_user`** / **`is_admin`** / **`validate_bearer_token`** | `src/external/stytch.py`, `src/utils/auth.py`, `src/utils/config.py` (`AUTH_CONFIG`) | `tests/component/external/test_stytch.py::TestAuthenticateSessionJwt`; `tests/component/utils/test_auth.py::{TestIsAdmin,TestNormalizeUser,TestValidateBearerToken}` |
| **AST-611** | Flask **`@require_auth`** / **`@require_admin`**; admin API enforcement; **`/api/me`** + nav filter | `src/core/auth_bootstrap.py`, `src/ui/auth.py`, `src/ui/server.py`, `src/ui/api/api_admin.py`, `src/ui/api/api_candidate.py`, `src/ui/api/api_system.py` | `tests/component/ui/test_auth.py::{TestRequireAuth,TestRequireAdmin}`; `tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::{test_me_requires_bearer,test_me_non_admin_includes_is_admin_false,test_nav_config_omits_admin_group_for_non_admin}`; `tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_non_admin_cannot_create_delete_or_override_state`; `tests/component/ui/test_server.py::TestServeReact::test_serves_index_when_ip_allowlist_restricted` |
| **AST-612** | React Stytch login gate; Bearer **`session_jwt`** on **`api()`**; **`AdminRoute`** on `/admin/*`; non-admin candidate selector lock | `src/ui/frontend/src/lib/api.ts`, `src/ui/frontend/src/contexts/AuthContext.tsx`, `src/ui/frontend/src/components/{RequireAuth,AdminRoute,NavigationShell}.tsx`, `src/ui/frontend/src/contexts/CandidateContext.tsx`, `src/ui/frontend/src/routes.tsx` | `tests/component/frontend/lib/test_api.test.ts`; `tests/component/frontend/contexts/test_AuthContext.test.tsx`; `tests/component/frontend/components/test_RequireAuth.test.tsx`; `tests/component/frontend/components/test_AdminRoute.test.tsx`; `tests/component/frontend/components/test_NavigationShell.test.tsx`; `tests/component/frontend/contexts/test_CandidateContext.test.tsx` |
| **AST-613** | Canonical Stytch magic-link + OAuth redirect URL (`VITE_STYTCH_REDIRECT_URL` with **`/authenticate`** fallback) | `src/ui/frontend/src/lib/stytchRedirect.ts`, `src/ui/frontend/src/pages/Login.tsx` | `tests/component/frontend/lib/test_stytchRedirect.test.ts`; `tests/component/frontend/pages/test_Login.test.tsx` |

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

## Appendix A — Run component tests

From repo root:

```bash
./scripts/testing/run_component_tests.sh
```

Requires **Python 3.10+** (creates `.venv` on first run). `ASTRAL_DB_DIR` defaults to `data/` in the harness. Install deps via `requirements.txt` when using `ASTRAL_PYTHON` instead of the default venv.

With zero arguments the harness selects **`tests/component`** wholesale. Passing paths, node IDs, or **`pytest`** flags after the script name forwards them verbatim as the **`pytest`** target list (narrow manifest runs without silently expanding to the full tree). Only the default full selection runs **`check_per_file_coverage.py`**.

When `src/ui/frontend/package.json` is present, the script also runs Vitest component tests under `tests/component/frontend/` — **only** when invoked with **zero** trailing arguments (narrowed pytest paths skip Vitest).
