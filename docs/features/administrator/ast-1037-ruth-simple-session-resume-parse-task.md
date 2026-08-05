<!-- linear-archive: AST-1037 archived 2026-08-05 -->

## Linear archive (AST-1037)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1037/ruth-simple-session-resume-parse-task-simple-resume-parse-function  
**Status at archive:** Archive  
**Project:** Astral Administrator  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1036 — Simple Resume Parse function  
**Blocked by / blocks / related:** parent: AST-1036; blocks: AST-1038

### Description

## What this implements

* Ruth/Little agent task + `TASK_CONFIG` entry for paste→JSON only (mechanical field mapping; no craft/translate)
* Seed repo `agent_task` so Manage Tasks / startup apply pick it up
* Same response contract the session paste path already expects

## Acceptance criteria

- [X] From Admin Session Resume Paste, Parse can run a Ruth (Little) task — not Judith craft-base — and return structure-keyed JSON the screen already understands *(this child: Ruth task + schema; wiring → AST-1038)*
- [X] Paste-faithful mechanics on a known fixture: `__` / `~~` survive into content; competencies not pipe-joined; specialty/keyword text in tagline (not mashed into title); `<no bullet>` leads remain lead markers
- [X] Candidate-bound `craft_resume_base` / Judith craft behavior unchanged outside this Admin session path

## Boundaries

- [X] Does not wire Admin Session Resume Parse / `run_session_resume_parse` → AST-1038
- [X] Does not change Judith `craft_resume_base` persona or candidate craft path
- [X] Does not change Open HTML builder or paste-page chrome

## In scope

- [X] pattern.config.config-block
- [X] astral.config.config-source-of-truth
- [X] astral.agent.do-task-delegation
- [X] astral.standards.no-hardcoded-sets
- [X] astral.docs.features-single-file-per-ticket
- [X] astral.git.engineer-test-tree-ban

## Considered but excluded

- [X] astral.ui.naming-conventions — no `src/ui/**`
- [X] astral.ui.frontend-file-placement — no frontend
- [X] astral.standards.database-header-inventory — no `src/data/**` schema inventory
- [X] astral.patterns.require-auth-on-protected-endpoints — no UI routes
- [X] astral.debug.spikes-under-debug-dir — plan/feature doc only, not a spike dump

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-29T15:56:42.378Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1037
**Publish ref:** `151cd9a8` on `origin/sub/AST-1036/AST-1037-ruth-simple-session-resume-parse-task`
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | conforms | do_task normalize gate only; no confidence math |
| astral.agent.do-task-delegation | scoped | conforms | No new LLM assembly; normalize stays inside `do_task` |
| astral.agent.grade-vector-validation | scoped | conforms | No grade-vector paths touched |
| astral.batch.batch-id-first | scoped | conforms | No batch-id changes |
| astral.batch.batch-id-format | scoped | conforms | No batch-id changes |
| astral.batch.claim-process-release | scoped | conforms | No claim/process/release changes |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | No agent_responses write path changes |
| astral.config.config-source-of-truth | scoped | conforms | Shared schema + normalize frozenset + TASK_CONFIG in config |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Untouched thresholds |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env additions |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths artifacts/** / scripts/spikes/** miss diff |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan feature doc only — not a committed spike under docs/features |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `docs/features/administrator/ast-1037-….md` |
| astral.git.betty-no-src-or-features | scoped | conforms | `code()` owns src + features; Betty owns tests/bible |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer `80ea40e7` avoids tests/bible; Betty authored `test()`/`merge-tests` |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Core keeps normalize; no external I/O in diff |
| astral.layers.import-direction | scoped | conforms | agent ← config; lazy candidate import retained |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths scripts/** miss diff |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | config touch only; no UI business logic |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | Untouched coat-check |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | Untouched consult orchestration |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers/paths src/ui/** miss diff |
| astral.standards.data-raises-caller-logs | scoped | conforms | No new data-layer logging pattern |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths src/data/** miss diff |
| astral.standards.debug-contract-gated | scoped | conforms | No new debug= surfaces |
| astral.standards.dry-and-focused-functions | scoped | conforms | Shared schema object + reused normalize helper |
| astral.standards.in-scope-only | scoped | conforms | No Admin wire / Judith craft prompt / HTML chrome |
| astral.standards.logging-via-utils | scoped | conforms | No new logging |
| astral.standards.no-cross-contamination | scoped | conforms | Catalog + seed only; sibling owns wire |
| astral.standards.no-hardcoded-sets | scoped | conforms | Normalize membership is `_CRAFT_RESUME_NORMALIZE_TASK_KEYS` in config |
| astral.standards.public-then-helpers | scoped | conforms | Module layout unchanged |
| astral.standards.utils-data-late-import-only | scoped | conforms | No utils→data import added |
| astral.state.core-decides-transitions | scoped | conforms | No state transitions |
| astral.state.job-prior-states-enforced | scoped | conforms | No job-state edits |
| astral.state.no-daisy-chain-in-run | scoped | conforms | `run_next` empty on new seed |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers/paths frontend miss diff |
| astral.ui.naming-conventions | scoped | not-applicable | layers/paths src/ui/** miss diff |
| astral.ui.single-gunicorn-worker | scoped | conforms | Untouched worker config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1037)` tip SHA |
| orch.git.commit-vocabulary | universal | conforms | `docs`/`code`/`test`/`merge-tests` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Published to child `sub/*` only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1036/AST-1037-…` matches Git table |
| orch.git.merge-on-checkout | universal | conforms | No evidence of skipped ftr/dev merge discipline |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | Linear history; no rewrite ops in tip |
| orch.git.no-dev-agent-branches | universal | conforms | Ticket sub ref; ignore Linear gitBranchName |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review on `astral-AST-1036/` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Task key + Ruth decided in plan |
| orch.pipeline.plan-is-bible | universal | conforms | Diff matches Stages 1–3; Stage 4 compile hygiene |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Administrator |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Entered from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute file edits |
| orch.roles.betty-owns-test-tree | universal | conforms | `test(AST-1037)` + bible by Betty |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada through Tests Passed → Review Posted |
| orch.roles.pre-commit-path-bans | universal | conforms | Engineer code commit stays off Betty paths |

## Pattern conformance

| id | verdict |
| -- | -- |
| pattern.config.config-block | conforms — `TASK_CONFIG["simple_resume_parse"]` |
| astral.config.config-source-of-truth | conforms — schema/normalize keys in config (also statute) |
| astral.agent.do-task-delegation | conforms — no parallel LLM path |
| astral.standards.no-hardcoded-sets | conforms — frozenset in config |

## Plan adherence

Diff matches Files Changed + Stages 1–3: shared schema, normalize frozenset, Ruth seed + AST-756 fixture sync, `agent.py` membership gate. Self-Assessment Single-Component / high / low still fits. Boundaries held vs AST-1038 wire and Judith craft. Scope match OK.

## Findings

### fix-now
(none)

### discuss
1. **C4 straggler** — Joan Excluded `astral.debug.spikes-under-debug-dir` but tip adds `docs/features/administrator/ast-1037-….md` so applies_when matches; substance **conforms** (plan doc, not a spike dump).
2. **C4 straggler** — Joan Excluded `astral.docs.features-single-file-per-ticket`; tip includes that feature file → in-scope; substance **conforms** (single file).
3. **C4 straggler** — Joan Excluded `astral.git.engineer-test-tree-ban`; tip includes Betty `tests/**` + bible → in-scope; substance **conforms** (engineer `code()` SHA clean; Betty owns test SHAs).

### advisory
- Leading-underscore `_CRAFT_RESUME_NORMALIZE_TASK_KEYS` imported across modules matches existing `_CRAFT_*` schema constants in config — acceptable per plan.

## What's solid
Shared schema identity, config-owned normalize membership (Joan round-1 fix), paste-faithful Ruth prompt, Judith row untouched, no Admin wire smuggle.

## Recommended actions
Ada: acknowledge the three C4 straggler discusses (no product edit expected), then `resolve-child`.

— Radia
context_tokens≈28000

#### betty — 2026-07-29T15:52:09.747Z
1. `tests/component/utils/test_config.py::TestAst1037SimpleResumeParseConfig` — shared schema object identity, `requires_candidate_key` False, craft-base meta unchanged, `_CRAFT_RESUME_NORMALIZE_TASK_KEYS`
2. `tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed` — revised frozenset includes `simple_resume_parse`; fixture byte-identical; startup apply 39
3. `tests/component/core/test_repo_admin_json.py::TestAst1037SimpleResumeParseCatalogRow` — Ruth seed + paste-faithful prompt rules; Judith `craft_resume_base` unchanged
4. `tests/component/core/test_agent.py::TestAst1037NormalizeGateMembership` — `do_task` gate uses config frozenset (not inline craft-only)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1037SimpleResumeParseConfig \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1037SimpleResumeParseCatalogRow \
  tests/component/core/test_agent.py::TestAst1037NormalizeGateMembership \
  -q
```

`origin/sub/AST-1036/AST-1037-ruth-simple-session-resume-parse-task` @ `46e493a9` (`merge-tests(AST-1037): origin/tests 545225d4`)

Bible shasums on publish tip:
- `docs/test-bible/core/agent.md` `22eb8effe9ce52bc033a6f3dd5024c40a5384117`
- `docs/test-bible/core/repo_admin_json.md` `7ae32692f9d0f80fd06c9d6e80cb1dc6beb76886`
- `docs/test-bible/utils/config.md` `1deede1ce9de9dbfc56f5b4a5a7b2c9516fb3c5d`
- `docs/test-bible/data/database/agent_tasks.md` `bc9982144153ff1aaf89de064e37be04d95a5b1b`

#### joan — 2026-07-29T15:21:52.983Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1037
**Overall:** APPROVED

**Notes:** Plan Discuss round=1 completed (concern + reply). Tip `fd31b3b4`. Prior fix-now (inline normalize membership in `agent.py`) addressed — `_CRAFT_RESUME_NORMALIZE_TASK_KEYS` in `config.py`.
**Implementer:** Ada (parent Team table).

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1 Session Paste Parse runs Ruth + familiar JSON | Stages 1–2 deliver Ruth task + shared schema; wire = N/A — AST-1038 |
| 2 Parse → Open HTML no bind / no artifact write | N/A — AST-1038 |
| 3 Dispatch/cost ledger on session sentinel | N/A — AST-1038 |
| 4 Paste-faithful mechanics | Stage 2 prompt rules |
| 5 Judith `craft_resume_base` unchanged outside session | Stages 1–2 (schema ref only) |
| 6 Style D debug on session-parse hop | N/A — AST-1038 |

### Child AC → plan stages

| Child AC | Stages |
| -- | -- |
| 1 Ruth task + schema (wiring sibling) | 1–3 |
| 2 Paste-faithful rules in prompt | 2 |
| 3 Judith craft unchanged | 1–2 |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 Shared schema + normalize-key frozenset + `TASK_CONFIG["simple_resume_parse"]` | Dedicated simple parse task; §2.1 / §1.4 |
| 2 `agent_task` seed + AST-756 fixture | Ruth seed; paste-faithful prompt |
| 3 `do_task` normalize via config membership | Shared JSON shape before validation |
| 4 Compile check | Build hygiene |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Plan `docs(AST-1037):` path |
| orch.git.flow-direction-inviolable | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No skip of ftr merge |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | conforms | `astral-AST-1036` |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Task key + Ruth decided |
| orch.pipeline.plan-is-bible | conforms | Stages binding; wire deferred |
| orch.pipeline.project-scoped-queues | conforms | Astral Administrator |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready re-check |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | No `tests/` edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign Ada on approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | Untouched |
| astral.agent.do-task-delegation | conforms | Reachable only via `do_task` once wired |
| astral.agent.grade-vector-validation | conforms | Untouched |
| astral.batch.batch-id-first | conforms | Untouched |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Untouched |
| astral.batch.entity-agent-responses-latest-only | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | Schema, task meta, normalize keys in config |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned src |
| astral.layers.core-vs-external-bright-line | conforms | Normalize in core |
| astral.layers.import-direction | conforms | utils/core/data-admin/docs |
| astral.layers.ui-config-driven-business-logic | conforms | No UI |
| astral.patterns.coat-check-never-store-empty | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Untouched |
| astral.standards.data-raises-caller-logs | conforms | Untouched |
| astral.standards.debug-contract-gated | conforms | No new debug in this child |
| astral.standards.dry-and-focused-functions | conforms | Shared schema + reused normalize |
| astral.standards.in-scope-only | conforms | Excludes Admin wire / Judith prompt / HTML |
| astral.standards.logging-via-utils | conforms | Untouched |
| astral.standards.no-cross-contamination | conforms | Layered structure |
| astral.standards.no-hardcoded-sets | conforms | Normalize membership is `_CRAFT_RESUME_NORMALIZE_TASK_KEYS` in config |
| astral.standards.public-then-helpers | conforms | Untouched |
| astral.standards.utils-data-late-import-only | conforms | Untouched |
| astral.state.core-decides-transitions | conforms | Untouched |
| astral.state.job-prior-states-enforced | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | conforms | Untouched |
| astral.ui.single-gunicorn-worker | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — paths miss (`docs/uat-fixtures/**`, not `docs/features/**`)
- astral.git.engineer-test-tree-ban — paths miss
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.patterns.require-auth-on-protected-endpoints — layers/paths miss
- astral.standards.database-header-inventory — paths miss
- astral.ui.frontend-file-placement — layers/paths miss
- astral.ui.naming-conventions — layers/paths miss

## Findings

### fix-now
(none)

### discuss
(none)

### acceptable
1. Wire deferred to AST-1038 — clear Boundaries.
2. Shared schema object identity — contract cannot drift.
3. `requires_candidate_key: False` for session sentinel.
4. AST-756 fixture byte-sync.
5. Self-assessment Single-Component / high / low — honest.

— Joan
context_tokens≈48000

#### ada — 2026-07-29T15:20:16.100Z
[plan-discuss] round=1 reply

Delta @ `fd31b3b4` on `origin/sub/AST-1036/AST-1037-ruth-simple-session-resume-parse-task`:

- Stage 1: add `_CRAFT_RESUME_NORMALIZE_TASK_KEYS = frozenset({"craft_resume_base", "simple_resume_parse"})` in `config.py` next to the shared schema constant.
- Stage 3: gate normalize with `if task_key in _CRAFT_RESUME_NORMALIZE_TASK_KEYS:` (import from config) — no inline membership tuple in `agent.py`.
- Files Changed + Code Rules §1.4 / §2.1 updated to match.

Plan: https://github.com/susansomerset/astral/blob/sub/AST-1036/AST-1037-ruth-simple-session-resume-parse-task/docs/features/administrator/ast-1037-ruth-simple-session-resume-parse-task.md

#### joan — 2026-07-29T15:18:21.824Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1037
**Overall:** REVISE

**Notes:** First Plan Ready pass. Tip `4f35545b`. Publish ref `origin/sub/AST-1036/AST-1037-ruth-simple-session-resume-parse-task`. Files Changed layers: utils/data/docs/core.
**Implementer:** Ada (parent Team table / plan author).

## Traceability

### Parent AC → plan stages

| Parent AC | Plan coverage |
| -- | -- |
| 1 Session Paste Parse runs Ruth (not Judith) + familiar JSON | Stages 1–2 deliver Ruth task + shared schema; **wire to Admin Parse = N/A — AST-1038** (child note + Boundaries) |
| 2 Parse → Open HTML no candidate bind / no artifact write | N/A — boundary: AST-1038 |
| 3 Dispatch/cost ledger on session sentinel | N/A — boundary: AST-1038 |
| 4 Paste-faithful mechanics (`__`/`~~`, competencies, tagline, `<no bullet>`) | Stage 2 prompt rules |
| 5 Judith `craft_resume_base` unchanged outside session path | Stages 1–2 (schema ref only; no Judith prompt/meta edits) |
| 6 Style D debug on session-parse hop | N/A — boundary: AST-1038 |

### Child AC → plan stages

| Child AC | Stages |
| -- | -- |
| 1 Ruth task + schema (wiring sibling) | 1–3 |
| 2 Paste-faithful rules in prompt | 2 |
| 3 Judith craft unchanged | 1–2 |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 Shared schema + `TASK_CONFIG["simple_resume_parse"]` | Functional scope dedicated simple parse task; config-source-of-truth |
| 2 `agent_task` seed + AST-756 fixture | Ruth seed; paste-faithful prompt; AC4/child AC2 |
| 3 `do_task` normalize gate for new key | Shared JSON shape usability before schema validation |
| 4 Compile check | Build hygiene only |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests |
| orch.git.commit-vocabulary | conforms | Plan `docs(AST-1037):` path |
| orch.git.flow-direction-inviolable | conforms | Child `sub/*` only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No skip of ftr merge |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | conforms | Ticket sub only |
| orch.git.one-epic-worktree-per-parent | conforms | `astral-AST-1036` |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | `simple_resume_parse` key + Ruth agent decided; no open product Q |
| orch.pipeline.plan-is-bible | conforms | Stages binding; wire deferred to sibling |
| orch.pipeline.project-scoped-queues | conforms | Astral Administrator child only |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | No `tests/` edits; fixture sync under docs/uat-fixtures only |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Ada |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign Ada after this pass |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | Untouched |
| astral.agent.do-task-delegation | conforms | Task only reachable via `do_task` once sibling wires it |
| astral.agent.grade-vector-validation | conforms | Untouched |
| astral.batch.batch-id-first | conforms | Untouched |
| astral.batch.batch-id-format | conforms | Untouched |
| astral.batch.claim-process-release | conforms | Untouched |
| astral.batch.entity-agent-responses-latest-only | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | Schema + task meta in `config.py`; prompts in agent_task seed |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned src/features |
| astral.layers.core-vs-external-bright-line | conforms | Normalize stays in core; no external I/O |
| astral.layers.import-direction | conforms | utils/core/data-admin/docs only |
| astral.layers.ui-config-driven-business-logic | conforms | No UI; task choice remains core/config |
| astral.patterns.coat-check-never-store-empty | conforms | Untouched |
| astral.patterns.render-verdict-orchestrates-consult | conforms | Untouched |
| astral.standards.data-raises-caller-logs | conforms | No data-layer logging |
| astral.standards.debug-contract-gated | conforms | No new debug paths in this child |
| astral.standards.dry-and-focused-functions | conforms | Shared schema + reused normalize |
| astral.standards.in-scope-only | conforms | Explicitly excludes Admin wire / Judith prompt / HTML |
| astral.standards.logging-via-utils | conforms | Untouched |
| astral.standards.no-cross-contamination | conforms | Layered structure |
| astral.standards.no-hardcoded-sets | **violates** | Stage 3 adds inline `task_key in ("craft_resume_base", "simple_resume_parse")` while Code Rules check claims no new inline membership sets — see fix-now |
| astral.standards.public-then-helpers | conforms | No public/helper reorder required |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data |
| astral.state.core-decides-transitions | conforms | No state machine |
| astral.state.job-prior-states-enforced | conforms | Untouched |
| astral.state.no-daisy-chain-in-run | conforms | Untouched |
| astral.ui.single-gunicorn-worker | conforms | Untouched |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — paths miss (plan Files Changed uses `docs/uat-fixtures/**`, not `docs/features/**`)
- astral.git.engineer-test-tree-ban — paths miss
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss
- astral.patterns.require-auth-on-protected-endpoints — layers/paths miss
- astral.standards.database-header-inventory — paths miss (`src/data/**`)
- astral.ui.frontend-file-placement — layers/paths miss
- astral.ui.naming-conventions — layers/paths miss

## Findings

### fix-now
1. **Location:** Stage 3 step 2 + Code Rules check §1.4 claim
   **Finding:** Stage 3 changes both `agent.py` sites to `if task_key in ("craft_resume_base", "simple_resume_parse"):` — an inline allowed-value membership set. The plan’s own Code Rules check says “no new inline frozensets for membership,” and `astral.standards.no-hardcoded-sets` / ASTRAL_CODE_RULES §1.4 require allowed value sets to live in `config.py`. Growing this set later will re-touch `agent.py`.
   **Recommendation:** In Stage 1, next to `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA`, add a config constant (e.g. `_CRAFT_RESUME_NORMALIZE_TASK_KEYS = frozenset({"craft_resume_base", "simple_resume_parse"})`). Stage 3 becomes `if task_key in _CRAFT_RESUME_NORMALIZE_TASK_KEYS:` (import from config / already imported). Update the Code Rules check line to match.

### discuss
(none blocking)

### acceptable
1. Child AC1 / parent AC1 wire portion deferred to AST-1038 — Boundaries + plan “No changes expected” for `run_session_resume_parse` are clear.
2. Shared schema object identity — prevents contract drift; good DRY.
3. `requires_candidate_key: False` for session sentinel — correct vs Judith True.
4. AST-756 fixture byte-sync — required seed gate pattern.
5. Self-assessment Single-Component / high / low — honest for an unused catalog key until sibling wires it.

— Joan
context_tokens≈45000

#### ada — 2026-07-29T15:15:16.733Z
Plan: [`docs/features/administrator/ast-1037-ruth-simple-session-resume-parse-task.md`](https://github.com/susansomerset/astral/blob/sub/AST-1036/AST-1037-ruth-simple-session-resume-parse-task/docs/features/administrator/ast-1037-ruth-simple-session-resume-parse-task.md) @ `4f35545b` on `origin/sub/AST-1036/AST-1037-ruth-simple-session-resume-parse-task`.

**Scope:** Single-Component — shared craft-resume schema constant + `TASK_CONFIG["simple_resume_parse"]`, Ruth `agent_task` seed (+ AST-756 byte-identical fixture), and `agent.py` normalize gate for the new key; no Admin wire / Judith craft edits.

**Conf:** high — reuses craft-base response contract, existing `college_intern_ruth`, AST-786 fixture sync, and the established normalize hook; AST-1038 owns the parse wire.

**Risk:** low — unused catalog key until sibling wires it; shared schema object prevents contract drift; Judith `craft_resume_base` stays put.

---

# AST-1037 — Ruth simple session-resume parse task

**Linear:** [AST-1037](https://linear.app/astralcareermatch/issue/AST-1037/ruth-simple-session-resume-parse-task-simple-resume-parse-function)  
**Parent:** [AST-1036](https://linear.app/astralcareermatch/issue/AST-1036/simple-resume-parse-function) — Simple Resume Parse function  
**Publish ref:** `sub/AST-1036/AST-1037-ruth-simple-session-resume-parse-task`

Add a dedicated Ruth (Little) agent task and matching `TASK_CONFIG` entry whose only job is paste→JSON mechanical field mapping for the Admin Session Resume Paste contract. Seed the repo `agent_task` row so Manage Tasks / startup apply pick it up. Do **not** wire `run_session_resume_parse` / Admin parse (sibling **AST-1038**). Do **not** change Judith `craft_resume_base` persona, prompts, or candidate craft path.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extract shared craft-resume response schema constant; add `_CRAFT_RESUME_NORMALIZE_TASK_KEYS` frozenset; add `TASK_CONFIG["simple_resume_parse"]` with identical schema and session-oriented meta | utils |
| `data/admin/agent_task.json` | Add current `simple_resume_parse` row (`college_intern_ruth`, mechanical prompt, paste-faithful rules) | data |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Byte-identical copy of repo `agent_task.json` after the new row (AST-786 seed gate) | docs |
| `src/core/agent.py` | Gate `normalize_craft_resume_base_agent_payload` via `_CRAFT_RESUME_NORMALIZE_TASK_KEYS` (covers `craft_resume_base` + `simple_resume_parse`) | core |

**No changes expected:** `src/core/candidate.py` (`run_session_resume_parse`, `parse_candidate_resume`, Judith craft path), `src/ui/api/api_admin.py`, React Session Resume Paste / Open HTML, `data/admin/agent.json` (Ruth already exists), Judith `craft_resume_base` `agent_task` row.

## Stage 1: Shared schema + `TASK_CONFIG["simple_resume_parse"]`

**Done when:** `TASK_CONFIG` exposes `simple_resume_parse` with the same response field set as `craft_resume_base`, keyed from one shared schema constant; `craft_resume_base` behavior/meta unchanged except the schema dict is referenced via that constant.

1. In `src/utils/config.py`, immediately above the `TASK_CONFIG = {` assignment (after `_RESUME_ARTIFACT_HOP_TASK_KEYS`), introduce a module-level constant named `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` whose value is **exactly** the current `craft_resume_base["response_schema"]` dict body (same keys, types, required flags, and `experience: _EXPERIENCE_JOB_ARRAY_FIELD`).

2. Immediately after `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA`, add:

```python
_CRAFT_RESUME_NORMALIZE_TASK_KEYS = frozenset({
    "craft_resume_base",
    "simple_resume_parse",
})
```

⚠️ **Decision:** Allowed normalize-gate membership lives in `config.py` (§1.4 / `astral.standards.no-hardcoded-sets`). Growing the set later is a config-only change — not another `agent.py` edit.

3. Change `TASK_CONFIG["craft_resume_base"]["response_schema"]` to reference `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` (no field edits; no meta edits — keep `response_format`, `context_format`, `entity_type`, `requires_candidate_key`, `trigger_state` as they are today).

4. Insert a new `TASK_CONFIG` entry **immediately after** `"craft_resume_base"`:

```python
"simple_resume_parse": {
    "response_schema": _CRAFT_RESUME_BASE_RESPONSE_SCHEMA,
    "response_format": "json",
    "context_format": "simple_resume_parse_{index}",
    "entity_type": None,
    "requires_candidate_key": False,
    "trigger_state": None,
},
```

⚠️ **Decision:** `task_key` is **`simple_resume_parse`** (matches epic “Simple Resume Parse function”). Sibling **AST-1038** will call this key from `run_session_resume_parse`.

⚠️ **Decision:** `requires_candidate_key: False` — this task is for the Admin session sentinel path (no candidate bind). Callers still may pass synthetic `ctx.candidate_data` for token resolution; they are not required to supply `astral_candidate_key`. Judith `craft_resume_base` stays `requires_candidate_key: True`.

⚠️ **Decision:** Share one schema object with `craft_resume_base` so the session paste / Open HTML contract cannot drift between the two catalog keys (§1.3 DRY / §2.1).

## Stage 2: Repo `agent_task` seed + AST-756 fixture sync

**Done when:** `data/admin/agent_task.json` contains a current `simple_resume_parse` row for Ruth; `docs/uat-fixtures/AST-756/expected-agent_task.json` is byte-identical to the repo file; Judith `craft_resume_base` row is unchanged.

1. In `data/admin/agent_task.json`, append one new object (keep existing rows untouched) with these fields:

| Field | Value |
|-------|--------|
| `task_key_uuid` | `046ffb1c-9708-49af-9380-56d85136066b` |
| `task_key` | `simple_resume_parse` |
| `current` | `1` |
| `agent_id` | `college_intern_ruth` |
| `run_next` | `""` |
| `system_prompt` | `""` |
| `cache_prompt_b` / `c` / `d` | `""` |
| `task_group_order` | `"2000"` |
| `task_group_name` | `Candidate Artifacts` |
| `task_seq` | `6` |
| `task_name` | `Simple Resume Parse` |
| `updated_at` | ISO UTC timestamp at edit time |

2. Write **`user_prompt`** (short, Ruth-addressed) that states: map the pasted resume text into the JSON schema only; no rewrite, enrichment, LinkedIn synthesis, or “improve the resume”; respond with valid JSON only (no markdown fences / preamble).

3. Write **`cache_prompt`** as the mechanical instruction block. It **must** include all of the following paste-faithful rules (lift wording from the current `craft_resume_base` `cache_prompt` where those rules already live — do not invent new markers):

   - Preserve typography digraphs `__` and `~~` literally in every section string (including nested experience fields); do not expand/replace them (HTML builder expands later).
   - `core_competencies` (and `prior_experience` when present): single string; separators are `•` / paste forms such as `__•__` — **never** `|` pipes.
   - Specialty / keyword / focus lines → `candidate_tagline`, **not** folded into `candidate_title`.
   - When the paste has a `<no bullet>…` role lead, copy that line into `accomplishments` **including** the literal `<no bullet>` prefix; do not invent the prefix when absent.
   - Field inventory matches the shared schema: `resume_structure`, `candidate_name`, `candidate_title`, `candidate_contact_detail`, optional `candidate_tagline`, `professional_summary`, `core_competencies`, `experience` (job array), optional `prior_experience`, optional `education_certifications`, optional `technical_skills`.
   - For `resume_structure`: if the paste does not imply a custom catalog, return the default structure shape the session path already uses (same keys the craft-base prompt expects) — do not invent unrelated section ids.
   - Explicitly **forbid** synthesis behaviors that belong to Judith craft-base: do not blend LinkedIn/bio/backstory; do not invent competencies, roles, or taglines; empty string / omit optional fields when the paste has no material.

4. Write **`nocache_prompt`** as:

```text
RESUME PASTE TEXT:
{$STARTING_RESUME_TEXT}
```

(Callers / sibling wire pass `starting_resume_text` via synthetic `ctx` the same way session parse already does for craft-base; `live_content` may also carry the paste — prompt truth is the nocache block.)

5. Sync the UAT fixture byte-for-byte:

```bash
cp data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json
cmp -s data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json && echo OK
```

⚠️ **Decision:** Group under **Candidate Artifacts** / order `2000` / seq `6` (sits next to `craft_resume_base` seq `5`) so Manage Tasks shows the pair together without inventing a new task group.

## Stage 3: `do_task` normalize hook via config membership set

**Done when:** Both `agent.py` sites that special-case `task_key == "craft_resume_base"` before schema validation run `normalize_craft_resume_base_agent_payload` when `task_key` is in `_CRAFT_RESUME_NORMALIZE_TASK_KEYS` (imported from config with the existing `TASK_CONFIG` import).

1. In `src/core/agent.py`, extend the existing `from src.utils.config import …` (or equivalent) that already pulls `TASK_CONFIG` so it also imports `_CRAFT_RESUME_NORMALIZE_TASK_KEYS`.

2. Find every occurrence of:

```python
if task_key == "craft_resume_base":
    from src.core.candidate import normalize_craft_resume_base_agent_payload
    normalize_craft_resume_base_agent_payload(parsed)
```

(There are two today — sync + async validation paths around the craft-base normalize calls.)

3. Change each condition to:

```python
if task_key in _CRAFT_RESUME_NORMALIZE_TASK_KEYS:
```

Keep the same lazy import and function call. Do **not** rename `normalize_craft_resume_base_agent_payload` in this ticket. Do **not** inline `("craft_resume_base", "simple_resume_parse")` in `agent.py`.

⚠️ **Decision:** This is catalog usability for the shared JSON shape, **not** Admin Session Resume Parse wiring. `run_session_resume_parse` still calls `craft_resume_base` until **AST-1038**.

## Stage 4: Compile check (plan-owned files only)

**Done when:** Touched Python modules compile; no edits under `tests/` (Betty owns the test tree).

1. From the epic worktree root:

```bash
python3 -m compileall -q src/utils/config.py src/core/agent.py
```

2. Confirm `craft_resume_base` still present in `TASK_CONFIG` and that `simple_resume_parse` is listed via a one-liner import check (venv if needed):

```bash
python3 -c "from src.utils import config as c; assert 'simple_resume_parse' in c.TASK_CONFIG; assert c.TASK_CONFIG['simple_resume_parse']['response_schema'] is c.TASK_CONFIG['craft_resume_base']['response_schema']"
```

## Self-Assessment

**Scope:** `Single-Component` — utils shared schema + normalize-key frozenset + `TASK_CONFIG` entry, repo `agent_task` seed/fixture, and `agent.py` membership gate against that frozenset; no Admin route or Judith craft path edits.

**Conf:** `high` — reuses the existing craft-base response contract, Ruth agent row, AST-786 fixture sync pattern, and the established normalize hook; sibling owns the parse wire.

**Risk:** `low` — new catalog key is unused until AST-1038; shared schema reference cannot silently diverge; Judith `craft_resume_base` prompts and meta stay put.

## Code Rules check

- **§1.1 / in-scope-only:** No Admin wire, no Open HTML, no Judith prompt edits.
- **§1.3 DRY:** One `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` shared by both task keys; normalize function reused.
- **§1.4 / no-hardcoded-sets:** Task key lives in `TASK_CONFIG` + `agent_task` seed; normalize membership is `_CRAFT_RESUME_NORMALIZE_TASK_KEYS` in `config.py` — `agent.py` does not grow an inline tuple/frozenset.
- **§2.1 config source of truth:** Schema, task meta, and normalize membership in `config.py`; prompts in `agent_task` seed.
- **§2.2 / do-task delegation:** Task is only reachable via `do_task` once a caller (sibling) invokes it — no new direct LLM calls.
- **§3.3 imports:** `agent.py` imports `_CRAFT_RESUME_NORMALIZE_TASK_KEYS` with `TASK_CONFIG`; keeps the existing lazy import of `normalize_craft_resume_base_agent_payload`.

## Revisions

Revision 1 — 2026-07-29  
Driven by: Joan `[plan-discuss] round=1 concern` — Stage 3 inline `task_key in ("craft_resume_base", "simple_resume_parse")` violates `astral.standards.no-hardcoded-sets` / §1.4.  
Changes: Stage 1 adds `_CRAFT_RESUME_NORMALIZE_TASK_KEYS` in `config.py`; Stage 3 gates normalize via that constant; Files Changed + Code Rules check updated to match.

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1037  
**Publish ref tip:** `151cd9a8` (`origin/sub/AST-1036/AST-1037-ruth-simple-session-resume-parse-task`)  
**Overall:** DISCUSS

### What's solid
- Shared `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` identity for `craft_resume_base` + `simple_resume_parse`; normalize membership in `_CRAFT_RESUME_NORMALIZE_TASK_KEYS` (Joan Plan Discuss fix).
- Ruth `agent_task` seed with paste-faithful rules (`__`/`~~`, `•` not `|`, tagline vs title, `<no bullet>` leads); Judith craft row untouched in the diff.
- Boundaries held: no Admin Session wire / Open HTML / UI; `requires_candidate_key: False` for session sentinel.
- Git vocabulary + Betty one-SHA merge-tests; engineer `code()` did not touch `tests/**`.

### Findings
**discuss (C4 straggler):** Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`; code-rubric sweep scores them in-scope on the three-dot tip (plan doc under `docs/features/**`; Betty `tests/` + bible in tip). Substance still **conforms** — not product fix-now. Acknowledge on resolve; no code change required.

### Recommended actions
1. Ada: acknowledge the three C4 straggler discusses, then proceed resolve-child (no src/tests edits expected from this review).

## Resolution

**Date:** 2026-07-29 — Ada (`resolve-child`)

- **fix-now:** none.
- **discuss (C4 stragglers):** Acknowledged — Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` on plan tip; code-rubric correctly brought them in-scope once the feature doc / Betty test tip landed. Substance already **conforms** (plan doc not a spike; single feature file; engineer `code()` clean of test-tree). No product or test-tree edits.
- **advisory:** Leading-underscore `_CRAFT_RESUME_NORMALIZE_TASK_KEYS` cross-module import left as planned.
- **Product tip:** unchanged from review tip (`151cd9a8` / Radia docs tip `5f14c5e7`); this commit is Resolution appendix only.
