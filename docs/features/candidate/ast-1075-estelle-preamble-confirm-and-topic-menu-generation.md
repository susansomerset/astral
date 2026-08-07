<!-- linear-archive: AST-1075 archived 2026-08-07 -->

## Linear archive (AST-1075)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1075/estelle-preamble-confirm-and-topic-menu-generation-topic-menu  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-953 — Topic Menu Generation  
**Blocked by / blocks / related:** parent: AST-953

### Description

## What this implements

Topic Menu step 1: Estelle confirmable preamble summary (“Anything here you would change?”), then pure-Estelle generation of a valid Topic Menu with informs-coverage confirmation (one ask may inform many). After AST-1074; needs AST-952 handoff packet. Does **not** own the later satisfaction conversation or state hops.

## Acceptance criteria

- [X] After a Valid preamble packet exists, Estelle runs a confirmable “Anything here you would change?” pass; the candidate can accept or correct before Topic Menu generation proceeds.
- [X] Given a confirmed preamble, Estelle produces a persisted Topic Menu (pure Estelle authorship) whose topics each have name, ask, required flag, status (`open` / `ready` / `retired`), and non-empty `informs` drawn only from rubrics, base resume, strengths, priorities, deal breakers, and/or backstory.
- [X] Estelle’s generation confirms informs coverage (one topic may cover multiple informs); topics without an allowed `informs` target are not accepted into the menu.
- [X] Every generated topic is directed and short enough to answer in a few minutes.
- [X] Touched backend `debug=True` confirm/generation paths emit per-step found/recorded debug lines per the contract above.

## Boundaries

Does **not** own Topic Menu model/persistence (AST-1074). Does **not** own later satisfaction conversation or REQUIRED/ALL_TOPICS_READY hops. Does **not** own AST-952 mechanical preamble.

## In scope

- [X] Estelle preamble confirm pass (“Anything here you would change?”) — `topic_menu_preamble_confirm` agent_task + core + API
- [X] Pure-Estelle Topic Menu generation from confirmed preamble — `topic_menu_generate` + `save_topic_menu(revise=True)`
- [X] Informs-coverage confirmation (closed catalog only; invalid topics dropped)
- [X] `TOPIC_MENU_GEN_CONFIG` + `TASK_CONFIG` schemas (`pattern.config.config-block` / `astral.config.config-source-of-truth` / `astral.standards.no-hardcoded-sets`)
- [X] `astral.agent.do-task-delegation` — confirm/generate via `do_task` only
- [X] `astral.standards.debug-contract-gated` — Style D on confirm/generate/mark-confirmed when `debug=True`
- [X] `astral.layers.import-direction` / `astral.layers.ui-config-driven-business-logic` — thin API + IntakeTopicMenuPanel labels from ui_config
- [X] Optional `topic_menu.preamble_confirmed_at` stamp + `CANDIDATE_DATA_MODEL.md`
- [X] CandidateIntake handoff: preamble complete → topic_menu phase (legacy chat only for active-session resume)
- [X] `astral.docs.features-single-file-per-ticket` — plan at `docs/features/candidate/ast-1075-estelle-preamble-confirm-and-topic-menu-generation.md`

## Considered but excluded

- [X] Topic Menu model / `TOPIC_MENU_CONFIG` informs catalog ownership — AST-1074
- [X] Satisfaction conversation / progress UI / REQUIRED_TOPICS_READY / ALL_TOPICS_READY — follow-on epic
- [X] Mechanical preamble / Ruth Valid / PREAMBLE_CONFIG copy — AST-952 family
- [X] Rewriting legacy `intake_initiate_candidate` / `intake_candidate_response` / `intake_build_request` prompts — active-session resume keeps AST-539 chat; new starts use Topic Menu path
- [X] `save_topic_menu(..., revise=False)` — forbidden caller path (AST-1074 contract)
- [X] `tests/` / `docs/test-bible/**` — Betty after Code Complete
- [X] Candidate state-machine vocabulary changes
- [X] Per-rubric informs keys (`like_rubric`, …) — parent closed catalog uses umbrella `rubrics`

## Notes for planning

Citations: new Estelle preamble-confirm-before-menu pattern; Topic Menu + closed informs; `astral.agent.do-task-delegation`; `astral.standards.debug-contract-gated`. After AST-1074. Needs AST-952 preamble packet.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-953-topic-menu-generation`, child `sub/AST-953/AST-1075-estelle-preamble-confirm-and-topic-menu-generation`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-30T19:10:53.663Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1075
**Publish ref:** `origin/sub/AST-953/AST-1075-estelle-preamble-confirm-and-topic-menu-generation` @ `ac813e90` (product tip was `26b789b5`; docs review appended)
**Baseline:** `origin/dev` (three-dot)
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | no graded agent_task / confidence fields |
| `astral.agent.do-task-delegation` | scoped | conforms | confirm/generate via `_run_intake_task` → `do_task` only |
| `astral.agent.grade-vector-validation` | scoped | conforms | no grade vectors |
| `astral.batch.batch-id-first` | scoped | conforms | on-demand ledger via `_run_intake_task`; no claim batch |
| `astral.batch.batch-id-format` | scoped | conforms | `intake-{task_key}-{uuid}` via existing helper |
| `astral.batch.claim-process-release` | scoped | conforms | no entity batch claim |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | do_task RESPONSE path unchanged |
| `astral.config.config-source-of-truth` | scoped | conforms | TOPIC_MENU_GEN_CONFIG + TASK_CONFIG; packet keys ⊆ library |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | no scoring |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | no secrets/env |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths miss tip |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | production features/docs only |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | one plan file + shared data-model amend |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test SHA touches tests/bible only |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | engineer code/docs omit tests/bible; Betty owns tip tests |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | external only via do_task/agent |
| `astral.layers.import-direction` | scoped | conforms | UI→core; core→agent/candidate/utils; no UI→data |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers ∩ tip empty |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | panel labels via ui_config; validation in core |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | no coat-check |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | no consult |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | conforms | confirm/generate routes `@require_auth` |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | ValueError for missing/incomplete; UI maps HTTP |
| `astral.standards.database-header-inventory` | scoped | not-applicable | no src/data/** |
| `astral.standards.debug-contract-gated` | scoped | conforms | Style D on confirm/generate/mark-confirmed when debug=True |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | reuses `_run_intake_task` / `save_topic_menu` |
| `astral.standards.in-scope-only` | scoped | conforms | no preferred_name; no satisfaction/state hops |
| `astral.standards.logging-via-utils` | scoped | conforms | module logger Style D |
| `astral.standards.no-cross-contamination` | scoped | conforms | named layers only |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | outcomes/keys/informs from config |
| `astral.standards.public-then-helpers` | scoped | conforms | public confirm/generate + private patch helper |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | no new utils→data |
| `astral.state.core-decides-transitions` | scoped | conforms | no candidate state hops |
| `astral.state.job-prior-states-enforced` | scoped | conforms | no job states |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | no dispatch chains |
| `astral.ui.frontend-file-placement` | scoped | conforms | IntakeTopicMenuPanel in components/; page CandidateIntake |
| `astral.ui.naming-conventions` | scoped | conforms | PascalCase panel; snake_case API |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | no worker changes |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | single merge-tests(AST-1075) SHA |
| `orch.git.commit-vocabulary` | universal | conforms | plan/code/docs/test/merge-tests/merge vocabulary |
| `orch.git.flow-direction-inviolable` | universal | conforms | publish only on origin/sub/AST-953/AST-1075-… |
| `orch.git.ftr-sub-topology` | universal | conforms | sub under AST-953 |
| `orch.git.merge-on-checkout` | universal | conforms | tip includes origin/dev merges; BEHIND=0 |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | none in tip for this child |
| `orch.git.no-dev-agent-branches` | universal | conforms | sub/AST-953/AST-1075-… only |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | epic worktree astral-AST-953 |
| `orch.git.three-permanent-branches` | universal | conforms | no new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | Joan round-1 Decisions documented; no new product OQs |
| `orch.pipeline.plan-is-bible` | universal | conforms | stages 1–6 match tip after Revision 1 |
| `orch.pipeline.project-scoped-queues` | universal | conforms | single-child review |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Tests Passed → review-child |
| `orch.roles.archie-approves-statutes` | universal | conforms | no statute corpus edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | test(AST-1075)+merge-tests; engineer omitted tests |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | assignee remains Hedy |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Hedy still assignee at Tests Passed |
| `orch.roles.pre-commit-path-bans` | universal | conforms | no banned path edits by engineer |

## Pattern conformance

| cited | verdict |
|-------|---------|
| `pattern.config.config-block` | conforms — `TOPIC_MENU_GEN_CONFIG` |
| Estelle preamble-confirm-before-menu (proposed) | conforms — confirm task + stamp gate |
| Topic Menu + closed informs | conforms — validate_topic soft-drop + coverage recompute |
| `astral.agent.do-task-delegation` | conforms (statute; via do_task) |
| `astral.standards.debug-contract-gated` | conforms (statute; Style D) |

## Plan adherence

MAJOR-CHANGE footprint matches Self-Assessment. Revision 1 (drop preferred_name; name columns; hopes/interests/concerns; survivor `informs_covered`) implemented. Always `revise=True`. New-start → `topic_menu` phase; active-session resume → chat preserved. Boundaries held (no satisfaction/state hops; no AST-1074 catalog ownership churn beyond stamp).

## Findings

**discuss (C4 straggler):** Joan Excluded `astral.git.engineer-test-tree-ban`; tip three-dot includes Betty tests/bible. Statute row still **conforms**. No product fix.

**advisory:** Confirm path logs `truncate_debug_content(msg)!r` (list repr) instead of iterating truncated lines.

**advisory:** Duplicate topic ids among soft-drop survivors fail at `validate_topic_menu` on save (API ValueError→400) rather than soft-drop.

**fix-now:** none

### What’s solid

Config asserts, do_task-only AI, whitelist patches, coverage recompute, auth on routes, UI labels from ui_config.

### Notes

Joan plan-rubric APPROVED (rev 1) recovered from Linear comment. Active statutes: 56.

context_tokens≈62000

— Radia

#### betty — 2026-07-30T18:49:34.426Z
## QA test manifest — AST-1075

**Publish:** `origin/sub/AST-953/AST-1075-estelle-preamble-confirm-and-topic-menu-generation` @ `b4931946` (`merge-tests(AST-1075): origin/tests 4461f886`)

### 1. Existing coverage (bible-backed)
- AST-1074 Topic Menu persistence/config still applies: `TestAst1074TopicMenuPersistence`, `TestAst1074TopicMenuConfig`

### 2. Broken / obsolete (revised this pass)
1. `test_CandidateIntake.test.tsx` — **preamble Valid handoff opens Estelle chat** → now **Topic Menu confirm** phase (AST-1075 product handoff)

### 3. Gaps (new this pass)
1. `tests/component/utils/test_config.py::TestAst1075TopicMenuGenConfig`
2. `tests/component/core/test_candidate.py::TestAst1075PreambleConfirmedAt`
3. `tests/component/core/test_intake.py::TestAst1075TopicMenuConfirmGenerate`
4. `tests/component/ui/api/test_api_intake.py::TestAst1075TopicMenuRoutes`
5. `tests/component/core/test_repo_admin_json.py::TestAst1075TopicMenuCatalogRows`
6. `tests/component/frontend/components/test_IntakeTopicMenuPanel.test.tsx`
7. Revised `tests/component/frontend/pages/test_CandidateIntake.test.tsx` (§6c routed page)

### Run
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1075TopicMenuGenConfig \
  tests/component/core/test_candidate.py::TestAst1075PreambleConfirmedAt \
  tests/component/core/test_intake.py::TestAst1075TopicMenuConfirmGenerate \
  tests/component/ui/api/test_api_intake.py::TestAst1075TopicMenuRoutes \
  tests/component/core/test_repo_admin_json.py::TestAst1075TopicMenuCatalogRows \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_IntakeTopicMenuPanel.test.tsx \
  ../../../tests/component/frontend/pages/test_CandidateIntake.test.tsx
```

### Bible shasums (`origin/sub/…` tip)
- `a3fedfe1a13179586549d83d53a509cd7c01c0fe585b5d60ffb553d0fdaedf6f` docs/test-bible/utils/config.md
- `fbce06350789f09535d92e0414b7735025d0158e5b05b952c20338c717a289ee` docs/test-bible/core/candidate.md
- `7cf1cba641d9be4a0b6d40c104d37ff00d9c9ca2c449fe1c999e1dafcce73701` docs/test-bible/core/intake.md
- `af5bde38474ea153043764de614b031d955ca208e51c80334a6db87277146cee` docs/test-bible/ui/api/api_intake.md
- `63ddf10a554312f85a757e0273f2cfb5f2a31325cb527f9e74bb3dd1a7112636` docs/test-bible/core/repo_admin_json.md
- `4ff2d4001db1308f93becb79f594d79f206cac4d2c94f5b191c15a90cb495829` docs/test-bible/frontend/pages.md
- `770cb3c9ff9b61d4fec758395274812b5e19091a97b60fdac3c3e50245517624` docs/test-bible/frontend/components.md

— Betty

#### joan — 2026-07-30T16:48:52.637Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1075
**Overall:** APPROVED

**Plan Discuss:** round=1 completed (concern + reply). Revision 1 on publish-ref addresses fix-now and both discuss notes.

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Estelle “Anything here you would change?” confirm | Stages 2, 4–6 — confirm task + API + IntakeTopicMenuPanel |
| AC2 persisted Topic Menu with required fields / closed informs | Stages 2, 4 — generate + `validate_topic` + `save_topic_menu(revise=True)` |
| AC3 informs coverage; reject topics without allowed informs | Stage 2 prompt + Stage 4 soft-drop + recompute `informs_covered` from survivors |
| AC4 directed / few-minute topics | Stage 2 generate prompt (Estelle judgment) |
| AC5 revise without wipe | Stage 4 always `revise=True`; forbids `revise=False` |
| AC6 no satisfaction / state hops required | N/A — boundary |
| AC7 debug=True found/recorded on confirm/generation | Stages 3–4 Style D on mark-confirmed / confirm / generate |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 TOPIC_MENU_GEN_CONFIG + TASK_CONFIG | Config-block; confirm/generate orchestration keys |
| Stage 2 Estelle agent_task rows | Preamble confirm + pure-Estelle generation |
| Stage 3 preamble_confirmed_at | Gate between accept and generate |
| Stage 4 core intake orchestration | do_task; packet snapshot (name/context/contact); whitelist patches; save |
| Stage 5 thin API + ui_config | Thin wrappers; labels from config |
| Stage 6 IntakeTopicMenuPanel + CandidateIntake phase | Step-1 UX; new-start vs active-session resume |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Publish on sub ref |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/AST-953/AST-1075-… |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | Build waits for AST-1074 on ftr |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-953/AST-1075-… only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-953 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Round-1 Decisions documented; Open questions none |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed + Revision 1 |
| orch.pipeline.project-scoped-queues | conforms | Single-child scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Discuss re-validate gate |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/bible edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Hedy) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer path after approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded vectors |
| astral.agent.do-task-delegation | conforms | Confirm/generate via do_task only |
| astral.agent.grade-vector-validation | conforms | No grade vectors |
| astral.batch.batch-id-first | conforms | On-demand ledger; no claim batch |
| astral.batch.batch-id-format | conforms | topic-menu-confirm-/generate- prefixes |
| astral.batch.claim-process-release | conforms | No entity batch claim |
| astral.batch.entity-agent-responses-latest-only | conforms | do_task RESPONSE path unchanged |
| astral.config.config-source-of-truth | conforms | Packet keys asserted ⊆ library contact/context/name_columns; preferred_name removed |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.debug.spikes-under-debug-dir | conforms | Production features/docs only |
| astral.docs.features-single-file-per-ticket | conforms | One plan file; shared data-model amend OK |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src/features |
| astral.layers.core-vs-external-bright-line | conforms | External only via do_task/agent |
| astral.layers.import-direction | conforms | UI→core; core→agent/data/utils |
| astral.layers.ui-config-driven-business-logic | conforms | Panel labels via ui_config; validation in core |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult |
| astral.patterns.require-auth-on-protected-endpoints | conforms | New routes @require_auth |
| astral.standards.data-raises-caller-logs | conforms | ValueError for missing/incomplete; UI maps HTTP |
| astral.standards.debug-contract-gated | conforms | Style D only when debug=True |
| astral.standards.dry-and-focused-functions | conforms | Reuse _run_intake_task / save_topic_menu |
| astral.standards.in-scope-only | conforms | No invented contact keys; name via columns; no satisfaction/state hops |
| astral.standards.logging-via-utils | conforms | Module logger Style D |
| astral.standards.no-cross-contamination | conforms | Named layers only |
| astral.standards.no-hardcoded-sets | conforms | Outcomes/keys/informs from config |
| astral.standards.public-then-helpers | conforms | Public confirm/generate + private patch helper |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data |
| astral.state.core-decides-transitions | conforms | Explicitly no state hops |
| astral.state.job-prior-states-enforced | conforms | No job states |
| astral.state.no-daisy-chain-in-run | conforms | No dispatch chains |
| astral.ui.frontend-file-placement | conforms | Component in components/; page CandidateIntake; App.css |
| astral.ui.naming-conventions | conforms | PascalCase panel; snake_case API |
| astral.ui.single-gunicorn-worker | conforms | No worker changes |

## Considered and excluded

**Notes:** Files Changed layer cell `data (repo admin JSON)` → `docs` per matching algorithm (path `data/admin/agent_task.json`).

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.debug.spikes-under-debug-dir, astral.docs.features-single-file-per-ticket, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ plan empty
- astral.standards.database-header-inventory — layers {data} ∩ plan empty (layer cell mapped to docs)

## Findings

None fix-now.

**Round-1 resolution:** `preferred_name` removed; `packet_name_columns` + asserts; hopes/interests/concerns in packet/patch lists; post-soft-drop `informs_covered` recomputed from survivors.

**acceptable:** Self-assessment MAJOR-CHANGE / high / Medium remains honest.

**R6:** Definition fidelity pass after Revision 1. Layer/import/auth/do_task/config patterns sound. No satisfaction/state-hop creep.

context_tokens≈58000

— Joan

#### hedy — 2026-07-30T16:47:01.835Z
[plan-discuss] round=1 reply

Addressed Joan fix-now + discuss notes on `origin/sub/AST-953/AST-1075-estelle-preamble-confirm-and-topic-menu-generation` @ tip after this push.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-953/AST-1075-estelle-preamble-confirm-and-topic-menu-generation/docs/features/candidate/ast-1075-estelle-preamble-confirm-and-topic-menu-generation.md

**Delta (Revision 1)**
1. **fix-now:** Removed fake `contact.preferred_name`. `packet_contact_keys` is now `title_patterns` only. Added `packet_name_columns` (`full`/`first`/`last`) with Stage 1 asserts ⊆ `CANDIDATE_LIBRARY_CONFIG["name_columns"]` and ⊆ `contact_keys` for contact keys. Snapshot puts identity under top-level `name` from table columns.
2. **discuss:** Included `hopes` / `interests` / `concerns` in `packet_context_keys` + `patchable_context_keys`.
3. **discuss:** After soft-drop, recompute authoritative `informs_covered` from surviving topics; Estelle’s `informs_coverage_confirmed is True` stays the hard gate.

Also merged `origin/dev` (BEHIND=0) before the plan patch.

#### joan — 2026-07-30T16:45:06.329Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1075
**Overall:** REVISE

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Estelle “Anything here you would change?” confirm | Stages 2, 4–6 — confirm task + API + IntakeTopicMenuPanel |
| AC2 persisted Topic Menu with required fields / closed informs | Stages 2, 4 — generate + `validate_topic` + `save_topic_menu(revise=True)` (model owned by AST-1074) |
| AC3 informs coverage; reject topics without allowed informs | Stage 2 generate prompt + Stage 4 soft-drop via `validate_topic`; require `informs_coverage_confirmed` |
| AC4 directed / few-minute topics | Stage 2 generate prompt (Estelle judgment); core does not encode duration |
| AC5 revise without wipe | Stage 4 always `revise=True`; forbids `revise=False` |
| AC6 no satisfaction / state hops required | N/A — boundary |
| AC7 debug=True found/recorded on confirm/generation | Stages 3–4 Style D on mark-confirmed / confirm / generate |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 TOPIC_MENU_GEN_CONFIG + TASK_CONFIG | Architectural config-block; confirm/generate orchestration keys |
| Stage 2 Estelle agent_task rows | Functional scope preamble confirm + pure-Estelle generation |
| Stage 3 preamble_confirmed_at | Gate between confirm accept and generate |
| Stage 4 core intake orchestration | do_task delegation; packet snapshot; whitelist patches; save menu |
| Stage 5 thin API + ui_config | UI layer thin wrappers; labels from config |
| Stage 6 IntakeTopicMenuPanel + CandidateIntake phase | Purpose step-1 UX; new-start vs active-session resume Decision |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Publish on sub ref |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/AST-953/AST-1075-… |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | Build waits for AST-1074 on ftr |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-953/AST-1075-… only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-953 |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions documented; Open questions none |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed |
| orch.pipeline.project-scoped-queues | conforms | Single-child scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan gate |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/bible edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Hedy) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer path after approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded vectors in these tasks |
| astral.agent.do-task-delegation | conforms | Confirm/generate via do_task only |
| astral.agent.grade-vector-validation | conforms | No grade vectors |
| astral.batch.batch-id-first | conforms | On-demand ledger prefixes; no claim batch |
| astral.batch.batch-id-format | conforms | Prefixes topic-menu-confirm-/generate- |
| astral.batch.claim-process-release | conforms | No entity batch claim |
| astral.batch.entity-agent-responses-latest-only | conforms | do_task RESPONSE path unchanged |
| astral.config.config-source-of-truth | violates | `packet_contact_keys` includes `preferred_name` — not in library/contact/name vocabulary |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.debug.spikes-under-debug-dir | conforms | Production features/docs only |
| astral.docs.features-single-file-per-ticket | conforms | One plan file; shared data-model amend OK |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src/features |
| astral.layers.core-vs-external-bright-line | conforms | External only via do_task/agent |
| astral.layers.import-direction | conforms | UI→core; core→agent/data/utils |
| astral.layers.ui-config-driven-business-logic | conforms | Panel labels via ui_config; validation in core |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult |
| astral.patterns.require-auth-on-protected-endpoints | conforms | New routes @require_auth |
| astral.standards.data-raises-caller-logs | conforms | ValueError for missing/incomplete; UI maps HTTP |
| astral.standards.debug-contract-gated | conforms | Style D only when debug=True |
| astral.standards.dry-and-focused-functions | conforms | Reuse _run_intake_task / save_topic_menu patterns |
| astral.standards.in-scope-only | violates | Invents `preferred_name` contact field absent from CANDIDATE_LIBRARY_CONFIG / name columns |
| astral.standards.logging-via-utils | conforms | Module logger Style D |
| astral.standards.no-cross-contamination | conforms | Named layers only |
| astral.standards.no-hardcoded-sets | conforms | Outcomes/keys/informs from config blocks |
| astral.standards.public-then-helpers | conforms | Public confirm/generate + private patch helper |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data |
| astral.state.core-decides-transitions | conforms | Explicitly no state hops |
| astral.state.job-prior-states-enforced | conforms | No job states |
| astral.state.no-daisy-chain-in-run | conforms | No dispatch chains |
| astral.ui.frontend-file-placement | conforms | Component in components/; page CandidateIntake; App.css |
| astral.ui.naming-conventions | conforms | PascalCase panel; snake_case API |
| astral.ui.single-gunicorn-worker | conforms | No worker changes |

## Considered and excluded

**Notes:** Files Changed layer cell `data (repo admin JSON)` treated as unrecognized → `docs` per matching algorithm (path still `data/admin/agent_task.json`).

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.debug.spikes-under-debug-dir, astral.docs.features-single-file-per-ticket, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.patterns.require-auth-on-protected-endpoints, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.frontend-file-placement, astral.ui.naming-conventions, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ plan empty
- astral.standards.database-header-inventory — layers {data} ∩ plan empty (layer cell mapped to docs)

## Findings

### fix-now
1. **Location:** Stage 1 `TOPIC_MENU_GEN_CONFIG["packet_contact_keys"]` / Stage 4 `build_preamble_packet_snapshot`
2. **Finding:** Plan lists `preferred_name` under contact packet keys. That key does **not** exist in `CANDIDATE_LIBRARY_CONFIG["contact_keys"]`, name columns (`first`/`last`/`full`/`pronouns`), or anywhere on `origin/dev` / ftr tip. Snapshot would always read empty; Stage 1 asserts do not cross-check `packet_contact_keys` against `contact_keys`.
3. **Recommendation:** Drop `preferred_name` **or** populate display name from candidate **name columns** (e.g. `full` / `first`) in the snapshot helper (not as a fake contact key). Add Stage 1 asserts: every `packet_contact_keys` entry ∈ `CANDIDATE_LIBRARY_CONFIG["contact_keys"]` (and keep name columns as a separate snapshot field if needed). `title_patterns` is fine.

### discuss (non-blocking)
- `packet_context_keys` omits `hopes` / `interests` / `concerns` (AST-952 Topic Menu seed fields). Confirm whether Estelle’s confirm summary should include them.
- After soft-dropping invalid generate topics, plan does not re-check that surviving topics still satisfy Estelle’s `informs_covered` claim — acceptable if at least one valid topic remains, but worth a one-line note in Stage 4.

### acceptable
- Self-assessment MAJOR-CHANGE / high / Medium is honest; Medium mitigations (whitelist, validate_topic drop, resume→chat) are specific.
- New-start skips legacy Estelle interview by Decision; active-session resume preserved.

**R6:** Definition largely faithful; fix-now blocks approve. Layer/import/auth/do_task/config patterns otherwise sound. No satisfaction/state-hop creep.

context_tokens≈55000

— Joan

#### hedy — 2026-07-30T16:42:32.082Z
Plan published on `origin/sub/AST-953/AST-1075-estelle-preamble-confirm-and-topic-menu-generation` @ `918a231e`.

**Plan doc:** https://github.com/susansomerset/astral/blob/sub/AST-953/AST-1075-estelle-preamble-confirm-and-topic-menu-generation/docs/features/candidate/ast-1075-estelle-preamble-confirm-and-topic-menu-generation.md

**Self-assessment**
- **Scope:** `MAJOR-CHANGE` — Estelle agent tasks + TASK_CONFIG, core confirm/generate orchestration, intake API, and CandidateIntake phase wiring; AST-1074 helpers only extended for `preamble_confirmed_at`.
- **Conf:** `high` — mirrors AST-1015 Ruth `do_task` + thin API, AST-1074 `save_topic_menu(revise=True)` caller contract, and IntakePreamblePanel handoff already on this tip; parent Open questions: none.
- **Risk:** `Medium` — bad prompts/schemas could yield empty/invalid menus or patch wrong library fields (whitelist + `validate_topic` drop); new-start navigation skips legacy Estelle interview (active-session resume still opens chat).

---

# AST-1075 — Estelle preamble confirm and Topic Menu generation

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1075/estelle-preamble-confirm-and-topic-menu-generation-topic-menu  
**Parent:** https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation  

**Publish ref (origin):** `sub/AST-953/AST-1075-estelle-preamble-confirm-and-topic-menu-generation`  
**Parent integration ref:** `ftr/AST-953-topic-menu-generation`

Ship Topic Menu **step 1**: Estelle presents a confirmable preamble summary (“Anything here you would change?”), the candidate accepts or corrects, then **pure-Estelle** generation persists a valid Topic Menu (closed `informs`, status triad via AST-1074 helpers). This ticket owns Estelle `agent_task`s, `do_task` orchestration, thin API, and the intake UI handoff after mechanical preamble — not the AST-1074 model itself, not later satisfaction turns, not REQUIRED/ALL_TOPICS_READY hops.

**Depends on:** AST-1074 (`TOPIC_MENU_CONFIG` + `get_topic_menu` / `validate_topic` / `save_topic_menu`) already on `origin/ftr/AST-953-topic-menu-generation` (User Testing). Merge that ftr tip before build. AST-952 mechanical preamble packet (raw materials in `context`) is on `origin/dev`.

**Caller contract from AST-1074:** always call `save_topic_menu(..., revise=True)` (default) so regenerated menus retire dropped topic ids instead of wiping history. Never pass `revise=False` unless the incoming list already includes every retired row to keep.

---

## Revisions

### Revision 1 — 2026-07-30
Driven by: Joan `[plan-discuss] round=1 concern` — fix-now: `preferred_name` is not in `CANDIDATE_LIBRARY_CONFIG["contact_keys"]` / name columns; Stage 1 lacked contact-key asserts.
Changes:
- Dropped `preferred_name` from `packet_contact_keys` (keep `title_patterns` only).
- Added `packet_name_columns`: `("full", "first", "last")` from `CANDIDATE_LIBRARY_CONFIG["name_columns"]`; snapshot exposes them under a top-level `name` object (not fake contact keys).
- Stage 1 asserts: every `packet_contact_keys` ∈ `contact_keys`; every `packet_name_columns` ∈ `name_columns`.
- Discuss follow-through: include `hopes` / `interests` / `concerns` in `packet_context_keys` + `patchable_context_keys` (library seed fields on tip).
- Discuss follow-through: after soft-dropping invalid generate topics, recompute `informs_covered` from surviving topics (do not trust Estelle’s list for the returned/persisted coverage claim).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `TOPIC_MENU_GEN_CONFIG` (task keys, confirm outcomes, packet field list, UI copy keys); add two `TASK_CONFIG` entries; expose gen config on `ui_config` | utils |
| `data/admin/agent_task.json` | Two new Estelle rows: preamble confirm + Topic Menu generate | data (repo admin JSON) |
| `src/core/candidate.py` | Preserve optional `preamble_confirmed_at` on topic_menu normalize/validate/save path; helper to mark confirmed without wiping topics | core |
| `src/core/intake.py` | `build_preamble_packet_snapshot`, `run_topic_menu_preamble_confirm`, `generate_topic_menu_from_preamble` (+ debug Style D) | core |
| `src/ui/api/api_intake.py` | `POST …/topic-menu/confirm` and `POST …/topic-menu/generate` thin wrappers | ui |
| `src/ui/api/api_system.py` | Include `TOPIC_MENU_GEN_CONFIG` (UI-safe subset) under `ui_config` next to `preamble` | ui |
| `src/ui/frontend/src/components/IntakeTopicMenuPanel.tsx` | New panel: Estelle confirm turn(s) → Accept → generate → show menu summary | ui |
| `src/ui/frontend/src/pages/CandidateIntake.tsx` | After preamble complete → `topic_menu` phase (not auto-open legacy Estelle chat); keep active-session resume → chat | ui |
| `src/ui/frontend/src/App.css` | Minimal styles for the confirm/generate panel (match IntakePreamblePanel density) | ui |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Document optional `preamble_confirmed_at` on `topic_menu` | docs |

No `tests/` / bible edits (Betty after Code Complete). No candidate state-machine hops. No changes to Ruth preamble validate or `PREAMBLE_CONFIG` copy. Do **not** rewrite `intake_initiate_candidate` / `intake_candidate_response` / `intake_build_request` prompts in this ticket — legacy chat remains for **active session resume** only.

---

## Stage 1: Config — `TOPIC_MENU_GEN_CONFIG` + `TASK_CONFIG`

**Done when:** `TOPIC_MENU_GEN_CONFIG` is importable with stable task keys and confirm outcomes; `TASK_CONFIG` has matching entries with response schemas; module asserts bind task keys and outcomes; `get_task_keys()` includes both new keys. No agent_task JSON or core/UI yet.

1. In `src/utils/config.py`, immediately **after** the `TOPIC_MENU_CONFIG` asserts, add:

```python
# AST-1075: Estelle preamble confirm + Topic Menu generation (persistence = AST-1074).
TOPIC_MENU_GEN_CONFIG = {
    "confirm_task_key": "topic_menu_preamble_confirm",
    "generate_task_key": "topic_menu_generate",
    "confirm_outcomes": ("continue", "accepted"),
    "confirm_outcome_field": "outcome",
    # Live packet fields Estelle must see (from candidate_data.context / contact + name columns).
    "packet_context_keys": (
        "raw_resume",
        "raw_profile",
        "raw_sample",
        "bio_summary",
        "backstory",
        "strengths",
        "priorities",
        "deal_breakers",
        "hopes",
        "interests",
        "concerns",
    ),
    # Real contact library keys only — never invent preferred_name (not in contact_keys).
    "packet_contact_keys": (
        "title_patterns",
    ),
    # Candidate table name columns (not contact blob keys) for display identity in the packet.
    "packet_name_columns": (
        "full",
        "first",
        "last",
    ),
    # Library paths Estelle may patch on revise (whitelist only).
    "patchable_context_keys": (
        "raw_resume",
        "raw_profile",
        "raw_sample",
        "bio_summary",
        "backstory",
        "strengths",
        "priorities",
        "deal_breakers",
        "hopes",
        "interests",
        "concerns",
    ),
    "estelle_agent_id": "principal_recruiter_estelle",
    # UI copy (exposed via ui_config).
    "ui": {
        "panel_title": "Confirm preamble with Estelle",
        "accept_label": "Looks good — generate Topic Menu",
        "send_label": "Send to Estelle",
        "placeholder": "Tell Estelle what to change, or accept below.",
        "generating_label": "Estelle is building your Topic Menu…",
        "done_title": "Topic Menu ready",
    },
}
```

2. Asserts immediately after the block:

   - `confirm_task_key` / `generate_task_key` are distinct non-empty `str`.
   - `confirm_outcomes == ("continue", "accepted")`.
   - Every `packet_context_keys` / `patchable_context_keys` entry is in `CANDIDATE_LIBRARY_CONFIG["context_keys"]`.
   - Every `packet_contact_keys` entry is in `CANDIDATE_LIBRARY_CONFIG["contact_keys"]`.
   - Every `packet_name_columns` entry is in `CANDIDATE_LIBRARY_CONFIG["name_columns"]`.
   - `estelle_agent_id == "principal_recruiter_estelle"` (same id as existing intake Estelle `agent_task` rows — do **not** use the stale `INTAKE_CONFIG["estelle_agent_id"]` `X00_estelle_recruiter` literal for new rows).

⚠️ **Decision:** New config block `TOPIC_MENU_GEN_CONFIG` rather than expanding `TOPIC_MENU_CONFIG`. Persistence catalog stays AST-1074-owned; generation/confirm orchestration keys stay here so Ada’s model contract does not churn when prompts/UI copy change.

⚠️ **Decision:** Confirm outcomes are `continue` | `accepted` (not Valid/Try Again). Ruth already owns Valid/Try Again for mechanical preamble; Estelle confirm is a different conversation.

⚠️ **Decision (Joan round=1):** Display name comes from candidate **name columns** (`full` / `first` / `last`) under snapshot key `name`, not from a fabricated `contact.preferred_name`. `packet_contact_keys` stays a subset of real `contact_keys` (`title_patterns` only for this ticket).

3. In `TASK_CONFIG`, after `preamble_validate_response`, add:

```python
"topic_menu_preamble_confirm": {
    "response_schema": {
        "assistant_message": {"type": "str", "required": True},
        "outcome": {"type": "str", "required": True},
        "library_patches": {"type": "dict", "required": False},
    },
    "response_format": "json",
    "context_format": "topic_menu_confirm_{index}",
    "entity_type": "candidate",
    "requires_candidate_key": True,
    "trigger_state": None,
},
"topic_menu_generate": {
    "response_schema": {
        "topics": {"type": "list", "required": True},
        "informs_coverage_confirmed": {"type": "bool", "required": True},
        "informs_covered": {"type": "list", "required": True},
    },
    "response_format": "json",
    "context_format": "topic_menu_generate_{index}",
    "entity_type": "candidate",
    "requires_candidate_key": True,
    "trigger_state": None,
},
```

4. Assert `TOPIC_MENU_GEN_CONFIG["confirm_task_key"]` and `["generate_task_key"]` are both in `TASK_CONFIG`.

5. Do **not** add `dispatch_tasks` rows — both tasks are on-demand (API/UI), not scheduler batches.

---

## Stage 2: Repo `agent_task` rows — Estelle only

**Done when:** `data/admin/agent_task.json` has two new objects with the exact task keys from Stage 1, `agent_id` == `TOPIC_MENU_GEN_CONFIG["estelle_agent_id"]`, prompts that force the schemas above and the closed informs vocabulary, and no other agent/persona rows changed.

1. Append two objects to `data/admin/agent_task.json` (fresh `task_key_uuid` each via `uuid.uuid4()`; `updated_at` = current UTC `YYYY-MM-DD HH:MM:SS`; unused cache slots `""`; `current` = `1`; `run_next` = `""`; `system_prompt` = `""` — persona lives on the Estelle agent row).

### Row A — `topic_menu_preamble_confirm`

| Field | Value |
|-------|--------|
| `task_key` | `topic_menu_preamble_confirm` |
| `agent_id` | `principal_recruiter_estelle` |
| `task_name` | `Topic Menu Preamble Confirm` |
| `task_group_name` | `Topic Menu` |
| `task_group_order` | `2000` |
| `task_seq` | `1` |
| `cache_prompt` (or the repo’s primary cache-A field used by other Estelle intake rows) | See prompt body below |
| `user_prompt` | Short turn instruction pointing at CONTENT + requiring the JSON envelope |

**cache_prompt body (required behaviors):**

- You are Estelle confirming the candidate’s **preamble packet** before inventing a Topic Menu.
- Live CONTENT includes a `PREAMBLE_PACKET` JSON snapshot and optional `CANDIDATE_MESSAGE`.
- First turn (empty/absent candidate message): summarize the packet in plain language, then ask exactly: **Anything here you would change?** Set `outcome` to `continue`.
- Later turns: if the candidate accepts (e.g. “looks good”, “nothing to change”), set `outcome` to `accepted` and keep `assistant_message` as a brief acknowledgment.
- If the candidate requests changes: set `outcome` to `continue`, put allowed field updates in `library_patches` as `{"context": {<key>: <str>, ...}}` using **only** keys from the closed patchable list (raw_resume, raw_profile, raw_sample, bio_summary, backstory, strengths, priorities, deal_breakers, hopes, interests, concerns). Omit `library_patches` or use `{}` when nothing to write. Never patch `name` columns or invent contact keys. Re-summarize and re-ask the same confirm question.
- Never invent new library keys. Never generate a Topic Menu in this task.
- `agent_payload.outcome` must be exactly `continue` or `accepted`.

### Row B — `topic_menu_generate`

| Field | Value |
|-------|--------|
| `task_key` | `topic_menu_generate` |
| `agent_id` | `principal_recruiter_estelle` |
| `task_name` | `Generate Topic Menu` |
| `task_group_name` | `Topic Menu` |
| `task_group_order` | `2000` |
| `task_seq` | `2` |

**cache_prompt body (required behaviors):**

- Pure Estelle authorship: invent a directed Topic Menu from the confirmed `PREAMBLE_PACKET` in CONTENT. No config template of seed topics.
- Each topic object **must** include: `id` (stable non-empty string), `name`, `ask`, `required` (boolean), `informs` (non-empty list).
- `informs` entries may **only** be drawn from: `rubrics`, `base_resume`, `strengths`, `priorities`, `deal_breakers`, `backstory`. One topic may list multiple informs. Do not invent target kinds (reject `like_rubric`, `candidate_bio`, etc.).
- Every topic must be directed and answerable in a few minutes (one focused ask — not a multi-hour life story dump).
- Default topic status is applied by code (`open`); Estelle may omit `status`.
- Set `informs_coverage_confirmed` to `true` only after you have checked that every topic has at least one allowed informs target and that the menu as a whole reasonably covers the informs you intend (one ask may cover many). Set `informs_covered` to the unique list of informs targets that appear across topics (subset of the closed catalog).
- Return `topics` as a JSON array (may be empty only if truly impossible — core will reject empty).

2. Do **not** edit Ruth’s `preamble_validate_response` row or legacy intake Estelle chat rows.

---

## Stage 3: Topic Menu envelope — `preamble_confirmed_at`

**Done when:** `normalize_topic_menu` / `validate_topic_menu` / `save_topic_menu` preserve optional `preamble_confirmed_at` (non-empty `str`); a small helper can stamp confirm time without retiring topics; `CANDIDATE_DATA_MODEL.md` documents the field.

1. In `src/core/candidate.py`, extend `normalize_topic_menu`:

   - Keep existing `topics` coercion.
   - If `raw` is a `dict` and `raw.get("preamble_confirmed_at")` is a non-empty `str` after strip, include `"preamble_confirmed_at": <stripped>` on the returned dict; otherwise omit the key (do not invent nulls).

2. Extend `validate_topic_menu` to copy `preamble_confirmed_at` from the normalized menu onto the returned dict when present (topics validation unchanged).

3. Extend `revise_topic_menu` so the returned dict keeps `preamble_confirmed_at` from **existing** when present (incoming may refresh it if provided as non-empty str — prefer incoming when both set).

4. `save_topic_menu` already persists whatever `validate`/`revise` returns — ensure the stored object still includes the meta key when set. No change to default `revise=True`.

5. Add `mark_topic_menu_preamble_confirmed(candidate_id: str, *, when: str | None = None, debug: bool = False) -> dict`:

   - `when` default = UTC `YYYY-MM-DD HH:MM:SS` (same style as intake ledger timestamps).
   - Load via `get_topic_menu`; set `preamble_confirmed_at`; persist with `save_candidate_data(candidate_id, {_topic_menu_key(): menu}, debug=debug)` using the **full** normalized menu (topics list included) so deep-merge cannot drop topics.
   - Style D when `debug=True`: `func="candidate.mark_topic_menu_preamble_confirmed"`, found then recorded (1/2, 2/2), identifier=`candidate_id`.

6. In `CANDIDATE_DATA_MODEL.md` under `### topic_menu`, document optional `preamble_confirmed_at` stamped by AST-1075 after Estelle confirm accepts.

---

## Stage 4: Core orchestration — confirm + generate

**Done when:** `src/core/intake.py` exposes public async callables that build the packet snapshot, run Estelle confirm turns (applying whitelisted patches), gate generation on confirm, validate/filter topics against `TOPIC_MENU_CONFIG`, and `save_topic_menu(..., revise=True)`; `debug=True` emits Style D found/recorded lines on both paths.

1. Imports: `TOPIC_MENU_CONFIG`, `TOPIC_MENU_GEN_CONFIG`; from `src.core.candidate` import `get_topic_menu`, `validate_topic`, `validate_topic_menu`, `save_topic_menu`, `mark_topic_menu_preamble_confirmed`, `save_candidate_data`, `get_candidate`.

2. Add `build_preamble_packet_snapshot(candidate_id: str) -> dict`:

   - Load candidate; raise `ValueError` if missing.
   - Read `candidate_data.context` / `contact` dicts (empty dict if missing).
   - Return:

```python
{
    "name": {
        k: str(candidate.get(k) or "")
        for k in TOPIC_MENU_GEN_CONFIG["packet_name_columns"]
    },
    "context": {k: str(context.get(k) or "") for k in TOPIC_MENU_GEN_CONFIG["packet_context_keys"]},
    "contact": {k: str(contact.get(k) or "") for k in TOPIC_MENU_GEN_CONFIG["packet_contact_keys"]},
}
```

   - Gate for “Valid preamble packet exists”: require `context["raw_resume"].strip()` non-empty (same bar as CandidateIntake before Estelle). If empty, raise `ValueError("preamble packet incomplete: raw_resume required")`.
   - Do **not** invent contact keys; name identity is only under `name` from table columns.

3. Add `_apply_library_patches(candidate_id: str, patches: Any, *, debug: bool = False) -> list[str]`:

   - If `patches` is not a `dict`, return `[]`.
   - Only honor `patches.get("context")` when it is a `dict`.
   - For each key/value: key must be in `TOPIC_MENU_GEN_CONFIG["patchable_context_keys"]`; value must be `str`; skip empty after strip only if you are clearing — **Decision:** allow non-empty strings only (reject empty wipe via Estelle patch); collect applied keys.
   - `save_candidate_data(candidate_id, {"context": applied_map}, debug=debug)`.
   - Return list of applied keys.

4. Add `async def run_topic_menu_preamble_confirm(candidate_id: str, candidate_message: str | None = None, *, debug: bool = False) -> dict`:

   - Build packet via `build_preamble_packet_snapshot`.
   - `live_content` = JSON string:

```json
{"PREAMBLE_PACKET": <snapshot>, "CANDIDATE_MESSAGE": <str or "">}
```

   - Ledger + `do_task` pattern: mirror `validate_preamble_answer` / `_run_intake_task` (batch_id prefix `topic-menu-confirm-`, entity_type `candidate`, `task_key=TOPIC_MENU_GEN_CONFIG["confirm_task_key"]`, `ctx=candidate`, `index=candidate_id`, `debug=debug`).
   - On failure: return `{"success": False, "error": <str>, "batch_id": ..., "outcome": None, "assistant_message": None, "applied_patches": []}`.
   - On success: parse `parsed_response`; require non-empty `assistant_message` str; require `outcome` in `TOPIC_MENU_GEN_CONFIG["confirm_outcomes"]`.
   - If `library_patches` present, apply via `_apply_library_patches`.
   - If `outcome == "accepted"`: call `mark_topic_menu_preamble_confirmed(candidate_id, debug=debug)`.
   - Debug Style D (`func="run_topic_menu_preamble_confirm"`): found with outcome token; detail lines for message trunc + applied patch keys; recorded on accept stamp.
   - Return `{"success": True, "outcome": outcome, "assistant_message": msg, "applied_patches": [...], "batch_id": ..., "error": None, "packet": <snapshot after patches re-read or pre-patch — Decision: re-read snapshot after patches so UI can show updated packet>}`.

5. Add `async def generate_topic_menu_from_preamble(candidate_id: str, *, debug: bool = False) -> dict`:

   - Require `get_topic_menu(candidate_id).get("preamble_confirmed_at")` — if missing, raise `ValueError("preamble not confirmed; run confirm accept first")` (do not call Estelle).
   - Build packet snapshot (post-confirm library).
   - `live_content` = JSON `{"PREAMBLE_PACKET": <snapshot>, "INFORMS_CATALOG": list(TOPIC_MENU_CONFIG["informs"])}`.
   - `do_task` with `TOPIC_MENU_GEN_CONFIG["generate_task_key"]` (ledger prefix `topic-menu-generate-`).
   - On agent failure: return success False with error/batch_id.
   - Parse: require `informs_coverage_confirmed is True` (bool); require `informs_covered` is a `list` (Estelle’s claim is advisory only after filtering — see next bullets).
   - For each element of `topics`:
     - If not a `dict`, skip (debug_detail count).
     - Ensure `status` defaults to `TOPIC_MENU_CONFIG["default_status"]` when missing.
     - Try `validate_topic(topic)`; on `ValueError`, skip that topic and debug_detail the reason (do **not** accept topics with empty/illegal informs).
   - If zero topics survive: return success False, error `"no valid topics after informs validation"`.
   - **After soft-drop:** recompute `informs_covered_effective` as the unique union of `informs` across surviving validated topics (order = first-seen walk of `TOPIC_MENU_CONFIG["informs"]` then any remaining). Do **not** persist Estelle’s raw `informs_covered` list if it disagrees with survivors; return `informs_covered_effective` in the API payload for transparency. Estelle’s `informs_coverage_confirmed is True` remains a hard gate (she must assert she checked coverage before return); survivor recomputation is the authoritative coverage set after filtering.
   - Build `{"topics": <validated list>}` (preserve existing `preamble_confirmed_at` by loading current menu and setting it on the outgoing dict before save).
   - `saved = save_topic_menu(candidate_id, outgoing, revise=True, debug=debug)`.
   - Debug Style D (`func="generate_topic_menu_from_preamble"`): found (raw topic count / coverage flag); recorded (stored open/ready/retired counts via saved menu + rejected_topic_count + effective informs_covered).
   - Return `{"success": True, "menu": saved, "batch_id": ..., "rejected_topic_count": N, "informs_covered": informs_covered_effective, "error": None}`.

⚠️ **Decision:** Generation is gated on persisted `preamble_confirmed_at`, not on a UI-only flag — regenerations after refresh still require a prior accept (caller may re-run confirm).  

⚠️ **Decision:** Soft-drop invalid Estelle topics rather than failing the whole menu when at least one valid topic remains; hard-fail only when none remain or coverage flag is not true. After soft-drop, coverage list is recomputed from survivors (Joan round=1 discuss).  

⚠️ **Decision:** Do **not** call `save_topic_menu(..., revise=False)`.

---

## Stage 5: Thin API + ui_config

**Done when:** Two authenticated intake routes exist; `GET` ui_config includes UI copy + task key names needed by the panel; no business logic in the blueprint beyond validation/HTTP mapping.

1. In `src/ui/api/api_system.py`, where `preamble` is already exposed, add:

```python
"topic_menu_gen": {
    "ui": TOPIC_MENU_GEN_CONFIG["ui"],
    "confirm_outcomes": list(TOPIC_MENU_GEN_CONFIG["confirm_outcomes"]),
},
```

   (Import `TOPIC_MENU_GEN_CONFIG`. Do **not** expose full prompts.)

2. In `src/ui/api/api_intake.py`:

   - Import the two new core callables.
   - `POST /<candidate_id>/topic-menu/confirm`  
     Body JSON: optional `{"message": "<str>"}` (absent/empty = first Estelle turn).  
     `asyncio.run(run_topic_menu_preamble_confirm(..., candidate_message=..., debug=_debug_flag()))`.  
     Map `ValueError` → 400; missing candidate → 404; success False with agent error → 500 + `error` / `batch_id` (same shape as preamble validate).  
     200 body: success payload from core (assistant_message, outcome, applied_patches, packet, batch_id).

   - `POST /<candidate_id>/topic-menu/generate`  
     No body required.  
     `asyncio.run(generate_topic_menu_from_preamble(..., debug=_debug_flag()))`.  
     Same error mapping; 200 returns `{success, menu, batch_id, rejected_topic_count}`.

3. Both routes: `@require_auth`; use existing `_debug_flag()`.

---

## Stage 6: Intake UI — confirm → generate after preamble

**Done when:** Completing mechanical preamble opens Estelle confirm (not legacy `IntakeChatModal`); Accept runs generate and shows a short Topic Menu summary; active-session **Continue** still opens legacy chat unchanged.

1. Add `src/ui/frontend/src/components/IntakeTopicMenuPanel.tsx`:

   - Props: `candidateId`, `onDone: () => void`, `onCancel: () => void`.
   - On mount: `POST …/topic-menu/confirm` with empty body; show `assistant_message` (loading + error toast patterns from `IntakePreamblePanel`).
   - Text area + **Send** → confirm with `{message}`; append/replace Estelle message from response; if `outcome === "accepted"`, enable/auto-run generate (see next).
   - **Looks good — generate Topic Menu** button: if last outcome is not `accepted`, call confirm with message `"Looks good — nothing to change."` (or empty accept path — **Decision:** button first POSTs confirm with that fixed accept phrase if needed, then always POSTs generate once `outcome === "accepted"` / after confirm returns accepted). Simpler path: Accept button POSTs `{message: "Looks good — nothing to change."}`; if response `outcome !== "accepted"`, show Estelle’s reply and do not generate; if accepted, immediately POST generate.
   - While generating, show `ui.generating_label`.
   - On generate success: list topic `name` + `required` + `informs.join(", ")` (read-only); primary button closes via `onDone`.
   - Read labels from `ui_config.topic_menu_gen.ui` (fetch once via existing ui_config load pattern used by preamble — if CandidateIntake/App already caches config, reuse; else `GET /api/ui_config` once in the panel).

2. Update `CandidateIntake.tsx`:

   - Extend `IntakePhase` with `"topic_menu"`.
   - `handlePreambleComplete`: keep materials state for possible legacy use, but `setPhase("topic_menu")` instead of `"chat"`.
   - Render `IntakeTopicMenuPanel` inside the same wide Modal when `phase === "topic_menu"`.
   - `onDone` / cancel → `goProfile()`.
   - Leave `handleResumeContinue` → `chat` unchanged (AST-539 resume path).

3. `App.css`: add a small block (`.intake-topic-menu-panel`, message bubble, topic list) consistent with preamble panel spacing — no new design system, no card soup.

⚠️ **Decision:** New starts after AST-952 preamble go Topic Menu confirm/generate; they do **not** auto-enter the legacy Estelle interview that fills bio via `ready_to_build`. Active session resume still uses legacy chat so AST-539 surfaces do not regress mid-flight. Optional later ticket can retire legacy chat entirely.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — new Estelle agent tasks + TASK_CONFIG, core confirm/generate orchestration, intake API, and CandidateIntake phase wiring; persistence helpers only extended for confirm meta.

**Conf:** `high` — mirrors AST-1015 Ruth `do_task` + thin API, AST-1074 `save_topic_menu(revise=True)` caller contract, and IntakePreamblePanel handoff patterns already on this tip; parent Open questions: none.

**Risk:** `Medium` — bad prompts/schemas could produce empty/invalid menus or patch the wrong library fields (mitigated by whitelist + `validate_topic` drop); changing post-preamble navigation away from legacy chat could surprise UAT that still expects Estelle interview (mitigated by keeping active-session resume → chat and documenting the new-start path).

---

## Code Rules check

- **§2.1 / config-source-of-truth / no-hardcoded-sets:** task keys, confirm outcomes, patchable keys, informs catalog (via `TOPIC_MENU_CONFIG`) live in config; core reads config, not inline frozensets of informs.
- **§2.2 / do-task-delegation:** confirm + generate call `do_task` only; no direct Anthropic from intake/UI.
- **§3.3 import direction:** UI → core callables; core → agent/candidate/data/utils; no UI → database.
- **§3.2 ui-config-driven:** panel labels from `TOPIC_MENU_GEN_CONFIG["ui"]` via ui_config; no business validation in React beyond empty-message UX.
- **debug-contract-gated:** Style D only when `debug=True` on confirm/generate/mark-confirmed paths.
- **§1.3 DRY:** reuse `_run_intake_task` ledger pattern or extract shared helper if duplication exceeds ~15 lines — prefer calling existing `_run_intake_task` for generate/confirm with the new task keys rather than a third copy of ledger code.
- **Out of scope enforced:** no satisfaction turns, no state hops, no AST-1074 informs catalog edits, no `tests/` edits, no rewrite of legacy intake chat prompts.

---

## Review

**Publish ref:** `sub/AST-953/AST-1075-estelle-preamble-confirm-and-topic-menu-generation`

**Build tip:** `a730b5d5` (`code(AST-1075): Stages 5–6 — topic-menu API and intake UI handoff`)

**Reviewed tip:** `26b789b5` (`merge(AST-1075): origin/dev`) vs `origin/dev`

**Overall:** DISCUSS (C4 straggler only; no product fix-now)

### What’s solid

- Stages 1–6 match tip: `TOPIC_MENU_GEN_CONFIG` + TASK_CONFIG, Estelle agent_task rows, `preamble_confirmed_at`, confirm/generate via `_run_intake_task`/`do_task`, thin `@require_auth` API, IntakeTopicMenuPanel + new-start `topic_menu` phase (resume → chat kept).
- Revision 1 landed: no `preferred_name`; name columns under snapshot `name`; hopes/interests/concerns in packet/patch; `informs_covered` recomputed from survivors; always `save_topic_menu(..., revise=True)`.
- Style D present on confirm / generate / mark-confirmed when `debug=True`.

### Findings

**discuss (C4):** Joan Excluded `astral.git.engineer-test-tree-ban` (plan paths); tip three-dot includes Betty `tests/**` + bible. Statute still **conforms** (engineer SHAs omit test tree). No engineer action required.

**advisory:** Confirm debug logs `assistant_message={truncate_debug_content(msg)!r}` (list repr) instead of iterating truncated lines like `save_topic_menu` — still gated; polish only.

**advisory:** Soft-drop validates topics one-by-one; duplicate ids among survivors surface as `validate_topic_menu` ValueError on save (API → 400) rather than soft-drop. Rare Estelle failure mode.

### Recommended actions

None for resolve-child product code. Acknowledge discuss/advisory or leave for follow-on polish.

---

## Resolution

**Date:** 2026-07-30  
**Review:** Radia `[code-rubric] revision=1` Overall DISCUSS @ `ac813e90` (product tip `26b789b5`).

**fix-now:** none — no product code changes.

**discuss (C4 straggler):** Acknowledged. Joan Excluded `astral.git.engineer-test-tree-ban` on plan paths; post–Tests Ready tip includes Betty `tests/**` + bible. Statute remains conforms (engineer SHAs omit test tree). No Archie re-score requested; no plan-rubric rewrite.

**advisory (debug truncate repr):** Acknowledged; leave for follow-on polish — still Style D gated and contract-complete.

**advisory (duplicate topic ids on save):** Acknowledged; rare Estelle failure mode; `validate_topic_menu` reject → 400 is acceptable without soft-drop expansion this ticket.

**Outcome:** resolve clean → User Testing.
