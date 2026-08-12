<!-- linear-archive: AST-1089 archived 2026-08-11 -->

## Linear archive (AST-1089)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1089/ruth-little-brain-meteorite-email-parse-task-add-gaze-email-as-a  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1087 — Add gaze_email as a dispatch task  
**Blocked by / blocks / related:** parent: AST-1087; blocks: AST-1090

### Description

## What this implements

Owns the Ruth TASK_CONFIG / agent-task slice that accepts email HTML (and related shape inputs) and returns meteorite job links/metadata and/or a likely JD link + content hints for the subject+body path. **Must use the bound candidate’s API key** for the consult. Does **not** scrape URLs, create jobs, or mutate Gmail (sibling #3).

## In scope

- [X] `pattern.config.config-block` — `METEORITE_EMAIL_PARSE_CONFIG` + `TASK_CONFIG["parse_meteorite_email"]`
- [X] `astral.config.config-source-of-truth` — task key + `parse_modes` literals in config only
- [X] `astral.config.secrets-and-env-specific-from-environ` — no Gmail secrets; candidate API key via `requires_candidate_key` / `ctx` at call time
- [X] `astral.standards.in-scope-only` — TASK_CONFIG + Ruth `agent_task` + AST-756 fixture only
- [X] `astral.standards.no-hardcoded-sets` — parse modes / task key not inlined in prompts as a second source of truth beyond config literals documented for the caller

## Considered but excluded

- [X] `astral.layers.core-vs-external-bright-line` — no Gmail I/O or core runner in this ticket (AST-1088 / AST-1090)
- [X] `pattern.state.entity-state-transitions` / `astral.state.no-daisy-chain-in-run` — no job state transitions here
- [X] `astral.standards.debug-contract-gated` — no new debug paths in this ticket (runner owns Style D)
- [X] Dispatch shell / null `candidate_id` / archive+trash — AST-1088
- [X] Bind / route / scrape / dedupe / create / mailbox outcomes — AST-1090

## Acceptance criteria

- [X] 6. Ruth invocations for bound mail use the bound candidate’s API key (`TASK_CONFIG["parse_meteorite_email"]["requires_candidate_key"]` is True; callers supply `ctx["candidate_api_key"]`). Account address / unbound retention / Gmail secrets remain sibling #1 (AST-1088).

## Boundaries

Does **not** scrape URLs, create jobs, or mutate Gmail (sibling #3). Does **not** own dispatch shell (sibling #1).

## Notes for planning

Plan: `docs/features/meteorite/ast-1089-ruth-little-brain-meteorite-email-parse-task.md` on `origin/sub/AST-1087/AST-1089-ruth-little-brain-meteorite-email-parse-task`.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1087-add-gaze-email-as-a-dispatch-task`, child `sub/AST-1087/AST-1089-ruth-little-brain-meteorite-email-parse-task`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-31T02:10:00.656Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1089
**Publish ref:** `origin/sub/AST-1087/AST-1089-ruth-little-brain-meteorite-email-parse-task` tip `6509f2bf921fdb111be352ec86cfc8739fdab278` (product tip reviewed `1ae256ab`; docs() `6509f2bf`)
**Overall:** FIX-NOW

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1089): origin/tests be56df6d…` on sub |
| orch.git.commit-vocabulary | universal | conforms | plan/code/test/docs/merge-tests vocabulary on sub |
| orch.git.flow-direction-inviolable | universal | conforms | Published to origin/sub only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1087/AST-1089-…` under parent ftr |
| orch.git.merge-on-checkout | universal | conforms | No illegal merge recipe in commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | None in history |
| orch.git.no-dev-agent-branches | universal | conforms | No agent-named epic branch |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review in astral-AST-1087 |
| orch.git.three-permanent-branches | universal | conforms | No permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Decisions documented in plan; no new product ambiguity |
| orch.pipeline.plan-is-bible | universal | conforms | Stages + Files Changed followed except shell creep below |
| orch.pipeline.project-scoped-queues | universal | conforms | Meteorite child only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | tests/bible via Betty test + merge-tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Katherine |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Implementer stays assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | Role path bans respected on commit authorship |
| astral.agent.confidence-bounds | scoped | conforms | `scored: False`; no grade/confidence vectors |
| astral.agent.do-task-delegation | scoped | not-applicable | layers {core} ∩ {docs,utils}=∅ |
| astral.agent.grade-vector-validation | scoped | not-applicable | layers {core} ∩ {docs,utils}=∅ |
| astral.batch.batch-id-first | scoped | not-applicable | layers {data,core} ∩ {docs,utils}=∅ |
| astral.batch.batch-id-format | scoped | not-applicable | layers {core,data} ∩ {docs,utils}=∅ |
| astral.batch.claim-process-release | scoped | not-applicable | layers {core,data} ∩ {docs,utils}=∅ |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | layers {core,data} ∩ {docs,utils}=∅ |
| astral.config.config-source-of-truth | scoped | conforms | Task key + parse_modes in METEORITE_EMAIL_PARSE_CONFIG / TASK_CONFIG |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Not scored; no score_floor / pass_threshold path |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No Gmail secrets; candidate key via requires_candidate_key + ctx |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths {artifacts/**,scripts/spikes/**} no match |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plan docs, not spike findings under docs/features |
| astral.docs.features-single-file-per-ticket | scoped | conforms | AST-1089 plan file present; sibling AST-1088 plan is separate ticket file |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits touch tests/bible only; merge-tests merge ok |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer code commits omit tests/bible |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers {core,external} ∩ {docs,utils}=∅ |
| astral.layers.import-direction | scoped | conforms | No new cross-layer imports; utils/config only in src |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers {scripts} ∩ {docs,utils}=∅ |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | No React; catalog registration only |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | layers {core} ∩ {docs,utils}=∅ |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | layers {core} ∩ {docs,utils}=∅ |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers {ui} ∩ {docs,utils}=∅ |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | layers {data,core,ui} ∩ {docs,utils}=∅ |
| astral.standards.database-header-inventory | scoped | not-applicable | layers {data} ∩ {docs,utils}=∅ |
| astral.standards.debug-contract-gated | scoped | conforms | No new debug emission paths |
| astral.standards.dry-and-focused-functions | scoped | conforms | One task × two parse modes; no duplicate Ruth keys |
| astral.standards.in-scope-only | scoped | violates | `dispatch_task_admin_defaults` GAZE_EMAIL_CONFIG early-return is AST-1088 shell; undefined on this tip |
| astral.standards.logging-via-utils | scoped | conforms | No new logging surface |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in utils + admin seed + fixture (+ Betty tests) |
| astral.standards.no-hardcoded-sets | scoped | conforms | Modes/task key live in named config; prompts reference literals |
| astral.standards.public-then-helpers | scoped | conforms | Catalog registration only |
| astral.standards.utils-data-late-import-only | scoped | conforms | No utils→data module-load import |
| astral.state.core-decides-transitions | scoped | not-applicable | layers {core,data} ∩ {docs,utils}=∅ |
| astral.state.job-prior-states-enforced | scoped | conforms | No job state transitions |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layers {core} ∩ {docs,utils}=∅ |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers {ui} ∩ {docs,utils}=∅ |
| astral.ui.naming-conventions | scoped | not-applicable | layers {ui} ∩ {docs,utils}=∅ |
| astral.ui.single-gunicorn-worker | scoped | conforms | No gunicorn/worker changes |

## Pattern conformance

- `pattern.config.config-block` — **conforms** (`METEORITE_EMAIL_PARSE_CONFIG` named block)
- Active `astral.patterns.*` — covered via statutes table (none applicable on this diff)

## Plan adherence

Self-Assessment Scope `Single-Component` matches intended Ruth catalog footprint. Stages 1–2 delivered. **Breach:** plan Out of scope / Boundaries exclude gaze_email dispatch shell (AST-1088), but `8d6eefe7` added `dispatch_task_admin_defaults` early-return on `GAZE_EMAIL_CONFIG` without defining that config or `TASK_CONFIG["gaze_email"]` on this tip → runtime `NameError` on every successful `dispatch_task_admin_defaults` call. Cross-ticket boundary violation + broken reference.

## Findings

**fix-now:** `src/utils/config.py` ≈L2672–2679 — `if tk == GAZE_EMAIL_CONFIG["task_key"]:` early-return. `GAZE_EMAIL_CONFIG` is **not assigned** on publish tip (`assigned False`, 1 ref). Remove this hunk from AST-1089 (leave shell on AST-1088 with the definition). Statute: `astral.standards.in-scope-only`; plan Out of scope.

**discuss (straggler):** Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`; tip three-dot includes `docs/features/**` + Betty test-tree so sweep scores them in-scope (all still **conforms**). Note: Joan artifact present.

**advisory:** Three-dot vs `origin/dev` also includes sibling `docs/features/meteorite/ast-1088-…md` (ftr-lineage docs) — not product smuggling by itself.

### What’s solid

Ruth `parse_meteorite_email` TASK_CONFIG + `METEORITE_EMAIL_PARSE_CONFIG` + agent_task prompts + AST-756 sync match plan Decisions; `requires_candidate_key: True`; not on `METEORITE_DISPATCH_TASKS`.

### Recommended actions

1. Delete the `GAZE_EMAIL_CONFIG` early-return from this sub.
2. Smoke `dispatch_task_admin_defaults` for an existing dispatch key after the delete.
3. No product change required for straggler discuss rows.

context_tokens≈52000

#### betty — 2026-07-31T02:06:30.980Z
## QA test manifest

`origin/sub/AST-1087/AST-1089-ruth-little-brain-meteorite-email-parse-task` @ `1ae256ab` (`merge-tests(AST-1089): origin/tests be56df6d79d821b5cd83e99325ef8e17d6237fe4`)

### Gaps (new)
1. `tests/component/utils/test_config.py::TestAst1089ParseMeteoriteEmailConfig` — `METEORITE_EMAIL_PARSE_CONFIG` modes/task_key; `TASK_CONFIG["parse_meteorite_email"]` schema + `requires_candidate_key`; not in `METEORITE_DISPATCH_TASKS` / batch-mode-one; trigger helper KeyError
2. `tests/component/core/test_repo_admin_json.py::TestAst1089ParseMeteoriteEmailCatalogRow` — Ruth Job Review row (`task_seq` 2.4), both parse modes in cache_prompt

### Broken / obsolete (revised)
3. `tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed` — catalog **46 → 47** + `parse_meteorite_email` in frozenset / UAT byte lock

### Existing coverage (bible-backed)
- Candidate API key path for `requires_candidate_key` remains covered by existing `do_task` tests in `tests/component/core/test_agent.py` (no new agent call-site in this ticket)

### Run
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1089ParseMeteoriteEmailConfig \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1089ParseMeteoriteEmailCatalogRow \
  -q
```

### Bible shasums on publish-ref
- `docs/test-bible/utils/config.md` `e46d071c475f8788cabd033d1639570ed6743591`
- `docs/test-bible/core/repo_admin_json.md` `3f81fc608ca9095810c5a0d3092630dcfc3d2239`

**Integration:** none revised (no existing scenarios assert this parse task).

— Betty

#### joan — 2026-07-31T01:58:54.980Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1089
**Overall:** APPROVED

**Notes:** Files Changed layer cell `data/admin` is unrecognized by plan-rubric layer enum → treated as `docs` for matching only (path still `data/admin/agent_task.json`).

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 bound shapes → METEORITE_NEW + archive | N/A — boundary (AST-1090 runner) |
| AC2 ignore non-URL subject / empty body | N/A — boundary (AST-1090) |
| AC3 unbound newer stays in inbox | N/A — boundary (AST-1088 retention config + AST-1090 policy) |
| AC4 unbound older → Trash, no job | N/A — boundary (AST-1088 trash API + AST-1090) |
| AC5 per-candidate dedupe / all-duplicate archive | N/A — boundary (AST-1090) |
| AC6 config account/retention + environ secrets + Ruth bound-candidate API key | Stage 1–2: `requires_candidate_key: True` + Ruth catalog; account/retention/Gmail secrets N/A — AST-1088 |
| AC7 no qualify/GDL in same hop | N/A — boundary (AST-1090; this key is not a dispatch claim task) |
| AC8 Style D debug on runner | N/A — boundary (AST-1090); plan adds no new debug paths |
| AC9 null `candidate_id` dispatch schema | N/A — boundary (AST-1088) |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 METEORITE_EMAIL_PARSE_CONFIG + TASK_CONFIG | Parent Functional scope Ruth parse of email HTML / subject+body; Architectural `pattern.config.config-block`; child AC (parent AC6 Ruth key slice) |
| Stage 2 agent_task.json + AST-756 fixture | Ruth agent_task row for parse modes; parent Applicable statutes config-source-of-truth / in-scope-only |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Plan/publish on sub ref only |
| orch.git.flow-direction-inviolable | conforms | Publish to origin/sub/… only |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1087/AST-1089-… |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1087 |
| orch.git.three-permanent-branches | conforms | No permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions documented; no product ambiguity blocking review |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed present |
| orch.pipeline.project-scoped-queues | conforms | Single-child Meteorite scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/bible; Betty after Code Complete |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Katherine) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer path |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | `scored: False`; no grade/confidence vectors |
| astral.config.config-source-of-truth | conforms | Task key + parse_modes in named config; prompts in agent_task.json |
| astral.config.pass-threshold-vs-score-floor | conforms | Not a scored consult; no score_floor path |
| astral.config.secrets-and-env-specific-from-environ | conforms | No Gmail secrets; candidate API key via requires_candidate_key + ctx |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src + admin seed; Betty excluded |
| astral.layers.import-direction | conforms | No new cross-layer imports; utils/config only in src |
| astral.layers.ui-config-driven-business-logic | conforms | No React; config catalog only |
| astral.standards.debug-contract-gated | conforms | No new debug paths; runner owns Style D |
| astral.standards.dry-and-focused-functions | conforms | One task + two parse modes; no duplicate Ruth keys |
| astral.standards.in-scope-only | conforms | Explicitly excludes 1088 shell and 1090 runner |
| astral.standards.logging-via-utils | conforms | No new logging surface |
| astral.standards.no-cross-contamination | conforms | Stays in config + admin seed + UAT fixture |
| astral.standards.no-hardcoded-sets | conforms | Modes/task key in METEORITE_EMAIL_PARSE_CONFIG / TASK_CONFIG |
| astral.standards.public-then-helpers | conforms | No scattered public API; catalog registration only |
| astral.standards.utils-data-late-import-only | conforms | No utils→data module-load import added |
| astral.state.job-prior-states-enforced | conforms | No job state transitions |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.job-prior-states-enforced, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.agent.do-task-delegation — layers {core} ∩ plan {docs, utils} empty
- astral.agent.grade-vector-validation — layers {core} ∩ plan empty
- astral.batch.batch-id-first — layers ∩ plan empty
- astral.batch.batch-id-format — layers ∩ plan empty
- astral.batch.claim-process-release — layers ∩ plan empty
- astral.batch.entity-agent-responses-latest-only — layers ∩ plan empty
- astral.debug.no-repo-root-artifacts-dir — paths match none
- astral.debug.spikes-under-debug-dir — paths match none
- astral.docs.features-single-file-per-ticket — paths {docs/features/**} match none of plan paths
- astral.git.engineer-test-tree-ban — paths match none
- astral.layers.core-vs-external-bright-line — layers ∩ plan empty
- astral.layers.scripts-exempt-from-layer-rules — layers ∩ plan empty
- astral.patterns.coat-check-never-store-empty — layers ∩ plan empty
- astral.patterns.render-verdict-orchestrates-consult — layers ∩ plan empty
- astral.patterns.require-auth-on-protected-endpoints — layers ∩ plan empty
- astral.standards.data-raises-caller-logs — layers ∩ plan empty
- astral.standards.database-header-inventory — layers ∩ plan empty
- astral.state.core-decides-transitions — layers ∩ plan empty
- astral.state.no-daisy-chain-in-run — layers ∩ plan empty
- astral.ui.frontend-file-placement — layers ∩ plan empty
- astral.ui.naming-conventions — layers ∩ plan empty

## Findings

None fix-now.

**acceptable:** Self-assessment Single-Component / Conf high / Risk low matches catalog-only scope; Decisions (one task × two modes, requires_candidate_key, not a dispatch claim) are specific and sibling-handoff ready.

**R6:** Definition fidelity pass for child #2 Ruth slice. Config/secrets pass. No runner/Gmail/shell creep. DRY one-task design pass.

context_tokens≈48000

— Joan

#### katherine — 2026-07-31T01:56:35.398Z
Plan published.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1087/AST-1089-ruth-little-brain-meteorite-email-parse-task/docs/features/meteorite/ast-1089-ruth-little-brain-meteorite-email-parse-task.md

**Self-assessment**
- **Scope:** Single-Component — `config.py` TASK_CONFIG + `METEORITE_EMAIL_PARSE_CONFIG`, one Ruth `agent_task.json` row, AST-756 fixture sync; no core runner / Gmail / dispatch shell.
- **Conf:** high — mirrors AST-1037 / AST-1060 Ruth catalog patterns; candidate API key via existing `requires_candidate_key` + `ctx["candidate_api_key"]`.
- **Risk:** low — catalog-only until AST-1090 calls it; wrong schema would block the runner, not mutate mailbox or jobs here.

#### chuckles — 2026-07-31T01:53:29.381Z
[thread-missing] Katherine Team store.db missing for prior UUID on this host; minted new session `1a68210c-fddf-49fe-91e9-fbe4cfeb0b8f` under epic workspace hash. Parent ## Team Katherine row updated.

— Chuckles

---

# AST-1089 — Ruth little-brain meteorite email parse task

**Linear:** [AST-1089](https://linear.app/astralcareermatch/issue/AST-1089/ruth-little-brain-meteorite-email-parse-task-add-gaze-email-as-a)
**Parent:** [AST-1087](https://linear.app/astralcareermatch/issue/AST-1087/add-gaze-email-as-a-dispatch-task) — Add gaze_email as a dispatch task
**Publish ref:** `origin/sub/AST-1087/AST-1089-ruth-little-brain-meteorite-email-parse-task`

Register Ruth (Little) `TASK_CONFIG` + repo `agent_task` for **`parse_meteorite_email`**: accept email HTML (and related shape inputs) and return meteorite job links/metadata and/or a likely JD link + content for the subject+body path. Config owns the task-key and parse-mode literals. **`requires_candidate_key: True`** so callers must supply the bound candidate’s API key via `ctx`. Does **not** own gaze_email dispatch shell / Gmail mutate (AST-1088), does **not** scrape URLs / create jobs / archive (AST-1090).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `TASK_CONFIG["parse_meteorite_email"]`; add `METEORITE_EMAIL_PARSE_CONFIG` (task key + parse-mode literals); inventory comment | utils |
| `data/admin/agent_task.json` | Add current Ruth `parse_meteorite_email` row (prompts + Job Review grouping) | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Byte-identical copy of repo `agent_task.json` after the new row (AST-786 seed gate) | docs |

**No changes expected:** `src/core/consult.py`, `src/core/agent.py`, `src/core/dispatcher.py`, `src/core/gazer.py`, `src/core/inbox.py`, `src/core/meteorite.py`, Gmail external, frontend, `tests/` / bible (Betty after Code Complete). Do **not** add a `dispatch_task` / `METEORITE_DISPATCH_TASKS` row for this key.

## Stage 1: `METEORITE_EMAIL_PARSE_CONFIG` + `TASK_CONFIG["parse_meteorite_email"]`

**Done when:** Config imports expose `METEORITE_EMAIL_PARSE_CONFIG["task_key"] == "parse_meteorite_email"` and that key exists in `TASK_CONFIG` with the response schema / meta below; `requires_candidate_key is True`; no dispatch trigger / pass_state wiring; `python3 -m py_compile src/utils/config.py` succeeds.

1. In `src/utils/config.py`, update the top-of-file config inventory comment block: add one line for `METEORITE_EMAIL_PARSE_CONFIG` next to the meteorite / email ingest bullets (Ruth email-HTML parse task key + parse-mode literals for gaze_email / AST-1089).

2. Immediately after the existing `METEORITE_EMAIL_INGEST_CONFIG` block (and its surrounding comments; before `METEORITE_DISPATCH_TASKS`), add:

```python
# AST-1087 / AST-1089: Ruth little-brain parse of bound meteorite email HTML.
# Callers (AST-1090 gaze_email runner) pass live_content shaped per parse_modes and
# must supply ctx with the bound candidate’s candidate_api_key (requires_candidate_key).
METEORITE_EMAIL_PARSE_CONFIG = {
    "task_key": "parse_meteorite_email",
    # live_content first line: "PARSE_MODE: <mode>" — see Stage 2 prompts.
    "parse_modes": ("html_links", "subject_body"),
}
```

3. Immediately after that dict, assert the task key will exist once `TASK_CONFIG` is defined — **or** place the assert after `TASK_CONFIG` is fully assigned (same pattern as other late `assert … in TASK_CONFIG` checks). Prefer a late assert near other task-key asserts:

```python
assert METEORITE_EMAIL_PARSE_CONFIG["task_key"] in TASK_CONFIG
assert set(METEORITE_EMAIL_PARSE_CONFIG["parse_modes"]) == {"html_links", "subject_body"}
```

Do **not** invent additional modes. Do **not** put Astral inbox account address or unbound retention days here (AST-1088).

4. In `TASK_CONFIG`, immediately after the `"qualify_meteorite"` block, add:

```python
    # AST-1087 / AST-1089: Ruth parse of bound meteorite email HTML (not a dispatch claim task).
    # AST-1090 calls do_task with METEORITE_EMAIL_PARSE_CONFIG["task_key"] + candidate ctx.
    "parse_meteorite_email": {
        "response_format": "json",
        "output_type": "fields",
        "scored": False,
        "response_schema": {
            "parse_mode": {"type": "str", "required": True},
            "jobs": {
                "type": "list",
                "required": True,
                "items_schema": {
                    "job_link": {"type": "str", "required": True},
                    "job_title": {"type": "str", "required": False},
                    "metadata": {"type": "str", "required": False},
                },
            },
            "jd_link": {"type": "str", "required": False},
            "content_text": {"type": "str", "required": False},
        },
        "context_format": "parse_meteorite_email_{index}",
        "entity_type": None,
        "requires_candidate_key": True,
        "trigger_state": None,
        "agent_task": "parse_meteorite_email",
    },
```

⚠️ **Decision — task key `parse_meteorite_email`:** Matches the Ruth “meteorite email parse” slice (parallel to `qualify_meteorite` / `simple_resume_parse` naming). AST-1090 must call `METEORITE_EMAIL_PARSE_CONFIG["task_key"]` (or this literal via that config) — do not invent a second catalog key.

⚠️ **Decision — one task, two parse modes:** Parent Functional scope needs (a) pure-HTML → multi job links/metadata and (b) subject+body → content + optional likely JD link. One Ruth task with `parse_mode` in schema + live_content avoids duplicate prompts and keeps sibling #3 on a single `do_task` call site.

⚠️ **Decision — unified response schema:**
- **`html_links`:** populate `jobs` (one item per meteorite job URL found); set `parse_mode` to `html_links`; leave `jd_link` / `content_text` empty string or omit (optional fields).
- **`subject_body`:** set `parse_mode` to `subject_body`; put usable email subject+body text into `content_text`; put the single most likely job-description URL into `jd_link` when present (else omit / empty); `jobs` may be `[]` or a one-element list mirroring `jd_link` — prefer `jobs: []` when only `jd_link`/`content_text` apply so the runner does not double-scrape.
- Do **not** invent grade vectors, `astral_job_id`, or qualify fields — this is pre-create parse only.

⚠️ **Decision — `requires_candidate_key: True`:** Parent AC6 / Boundaries — Ruth invocations for bound mail use **that candidate’s** API key. `do_task` reads `ctx["candidate_api_key"]` when this flag is set (see `src/core/agent.py`). Session-style synthetic ctx without a key is **not** a valid caller for this task.

⚠️ **Decision — not a dispatch claim task:** `entity_type: None`, `trigger_state: None`, no `pass_state` / `fail_state` / `error_state`, do **not** add to `METEORITE_DISPATCH_TASKS`, `_DISPATCH_BATCH_CALL_MODE_ONE`, or `_dispatch_trigger_state_for_task_key`. The parent `gaze_email` row is AST-1088; the runner that calls this parse is AST-1090.

⚠️ **Decision — `scored: False` + `output_type: "fields"`:** Same pattern as `qualify_meteorite` — structured extract, not grades-encoded.

5. Do **not** edit `agent.py` normalize gates, consult routes, or dispatcher. Do **not** add Gmail / retention / account keys.

**Done when (recheck):**

```bash
python3 -c "from src.utils import config as c; assert c.METEORITE_EMAIL_PARSE_CONFIG['task_key']=='parse_meteorite_email'; t=c.TASK_CONFIG['parse_meteorite_email']; assert t['requires_candidate_key'] is True; assert t['entity_type'] is None; assert t['agent_task']=='parse_meteorite_email'; assert set(c.METEORITE_EMAIL_PARSE_CONFIG['parse_modes'])=={'html_links','subject_body'}"
python3 -m py_compile src/utils/config.py
```

## Stage 2: Repo `agent_task.json` Ruth row + AST-756 fixture sync

**Done when:** `data/admin/agent_task.json` has a `current: 1` row for `task_key == "parse_meteorite_email"` (`college_intern_ruth`); prompts document both parse modes and the response schema; `docs/uat-fixtures/AST-756/expected-agent_task.json` is byte-identical to the repo file; JSON still parses as a flat-row array.

1. Append one object to `data/admin/agent_task.json` (flat scalars only — no nested JSON objects/arrays as field values), modeled on the existing `qualify_meteorite` / `simple_resume_parse` Ruth rows:

| Field | Value |
|-------|--------|
| `task_key_uuid` | new random UUID4 string |
| `task_key` | `parse_meteorite_email` |
| `current` | `1` |
| `agent_id` | `college_intern_ruth` |
| `task_group_order` | `"4000"` |
| `task_group_name` | `Job Review` |
| `task_seq` | place near meteorite qualify (e.g. `2.4` or next free seq before `qualify_meteorite`’s `2.5`) |
| `task_name` | `Parse Meteorite Email` |
| `system_prompt` / `cache_prompt_b` / `c` / `d` / `nocache_prompt` / `run_next` | `""` |
| `updated_at` | current UTC `YYYY-MM-DD HH:MM:SS` (or ISO-ish UTC string matching neighboring rows) |

2. **`user_prompt`** (short, Ruth-addressed): parse the email CONTENT per `PARSE_MODE`; return JSON matching the schema (`parse_mode`, `jobs`, optional `jd_link` / `content_text`); no scrape, no inventing URLs that are not in the HTML; no grade vectors.

3. **`cache_prompt`** must include all of the following (concrete instruction block):

- This is a **meteorite email parse** for a bound candidate’s inbound mail — mechanical extract, not qualify / grade / rewrite.
- Live CONTENT always starts with a line `PARSE_MODE: html_links` or `PARSE_MODE: subject_body` (literals from `METEORITE_EMAIL_PARSE_CONFIG["parse_modes"]`). Echo that value into response `parse_mode`.
- **`html_links`:** HTML body is the job source (often no useful subject). Extract every distinct http(s) meteorite **job** link worth scraping as its own JD. Skip obvious non-job noise (unsubscribe, mailto, tracking) when clearly not a job posting. For each kept link return `{job_link, job_title?, metadata?}` in `jobs`. Prefer empty `jd_link` / `content_text`.
- **`subject_body`:** CONTENT includes a `SUBJECT:` line and HTML/body after. Return `content_text` = usable subject + body text the runner may use as JD text when no link exists. If the message includes one likely job-description URL, set `jd_link` to that URL; otherwise omit/empty. Prefer `jobs: []` on this mode (runner uses `jd_link` / `content_text`).
- Always return valid JSON only (no markdown fences). Do not invent employer culture, company sites, or links absent from the email HTML.
- Do **not** copy `qualify_meteorite`’s `astral_job_id` / `company_job_id` / `jd_text` enrichment contract — create/scrape/dedupe belong to AST-1090.

⚠️ **Decision — prompts only in `agent_task.json`:** Same as AST-1037 / AST-1055 / AST-1060; startup `apply_repo_admin_json` ships the row. No parallel `_taskprompts` file. Do **not** hand-edit the live DB.

⚠️ **Decision — live_content contract for AST-1090 (document in prompts, not code here):**

```text
PARSE_MODE: html_links

<html>…email body…</html>
```

```text
PARSE_MODE: subject_body
SUBJECT: <subject text>

<html>…email body…</html>
```

Caller builds that string, then:

```python
await do_task(
    task_key=METEORITE_EMAIL_PARSE_CONFIG["task_key"],
    live_content=live,
    index=<message_id or candidate_id>,
    ctx=<candidate row with candidate_api_key>,
    debug=debug,
)
```

This ticket does **not** implement that call site.

4. Sync the UAT fixture byte-for-byte:

```bash
cp data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json
cmp -s data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json && echo OK
python3 -c "import json; json.load(open('data/admin/agent_task.json')); assert any(r.get('task_key')=='parse_meteorite_email' for r in json.load(open('data/admin/agent_task.json')))"
```

**Done when (recheck):** both JSON files identical; Ruth row present; `agent_id` is `college_intern_ruth`; `cache_prompt` mentions both `html_links` and `subject_body` and forbids inventing URLs.

## Out of scope (do not implement here)

- `gaze_email` `TASK_CONFIG` / null-`candidate_id` dispatch_task / Gmail archive+trash / Astral account + retention config (AST-1088).
- Core runner: bind, shape routing, Playwright scrape, per-candidate dedupe, `create_meteorite_job` / **METEORITE_NEW**, mailbox archive/trash, Style D on the runner (AST-1090).
- Calling `do_task` from gazer/inbox/dispatcher in this ticket.
- Editing `qualify_meteorite` / `simple_resume_parse` / Manage Email Create paths.
- `tests/` / `docs/test-bible/**` (Betty after Code Complete).

## Self-Assessment

**Scope:** `Single-Component` — `config.py` TASK_CONFIG + named parse config block, one Ruth `agent_task.json` row, AST-756 fixture sync; no core runner / Gmail / dispatch shell.

**Conf:** `high` — mirrors AST-1037 (Ruth TASK_CONFIG + agent_task seed) and AST-1060 (meteorite Ruth fields task); API-key contract is the existing `requires_candidate_key` + `ctx["candidate_api_key"]` path in `do_task`.

**Risk:** `low` — catalog-only until AST-1090 calls it; wrong schema would block the runner, not mutate mailbox or jobs in this ticket. Mitigation: mode/schema spelled literally for Joan + sibling handoff.

## Code rules self-review

- **§1.3 DRY:** One task + shared schema for both email shapes; no duplicate Ruth keys.
- **§1.4 / no-hardcoded-sets:** Task key and parse-mode strings live in `METEORITE_EMAIL_PARSE_CONFIG` / `TASK_CONFIG` only; prompts reference those literals.
- **§2.1 / config-source-of-truth:** Parse task key + modes in named config; prompts in repo `agent_task.json`.
- **§2.1 / secrets-and-env-specific-from-environ:** No Gmail secrets here; candidate API key remains on candidate row / environ-backed crypto — consumed at call time via `requires_candidate_key`.
- **§2.4 / §2.6:** No batch claim / state machine on this key (not a dispatch task).
- **§3.3 imports:** No new cross-layer imports in this ticket.
- **§3.5 naming:** `parse_meteorite_email` / `METEORITE_EMAIL_PARSE_CONFIG` match meteorite naming.
- **in-scope-only:** Explicitly excludes AST-1088 shell and AST-1090 runner.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1087/AST-1089-ruth-little-brain-meteorite-email-parse-task`
**Plan path:** `docs/features/meteorite/ast-1089-ruth-little-brain-meteorite-email-parse-task.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `66edd249` | `METEORITE_EMAIL_PARSE_CONFIG` + `TASK_CONFIG["parse_meteorite_email"]` |
| 2 | `8d6eefe7` | Ruth `agent_task.json` + AST-756 fixture (+ inventory comment) |

**Tip:** `8d6eefe7a8bd998190d000f8cccd43723b6ef1db` on `origin/sub/AST-1087/AST-1089-ruth-little-brain-meteorite-email-parse-task`

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1089
**Publish ref tip (at review):** `1ae256abc40f6df55a8e32985026d48c238c49ca`
**Overall:** FIX-NOW

### What’s solid

- Stage 1–2 Ruth slice matches plan: `METEORITE_EMAIL_PARSE_CONFIG`, `TASK_CONFIG["parse_meteorite_email"]` with `requires_candidate_key: True`, Ruth `agent_task` row, AST-756 fixture byte-identical.
- Parse modes / schema / prompts align with Decisions; not added to `METEORITE_DISPATCH_TASKS`.
- Betty `test` + single `merge-tests` SHA on the sub.

### Issues

**fix-now:** `src/utils/config.py` `dispatch_task_admin_defaults` early-return references `GAZE_EMAIL_CONFIG["task_key"]` but **`GAZE_EMAIL_CONFIG` is not defined** on this tip (and `gaze_email` is not in `TASK_CONFIG`). Introduced in `8d6eefe7` (AST-1089 code). Every successful call to `dispatch_task_admin_defaults` will `NameError`. Also AST-1088 shell scope smuggled into this ticket (`astral.standards.in-scope-only` / plan Out of scope).

**discuss (straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` at plan time; three-dot tip includes `docs/features/**` + Betty test-tree — scored in-scope on diff (verdicts still conforms).

### Recommended actions

1. Remove the `GAZE_EMAIL_CONFIG` early-return from this sub (belongs on AST-1088 with the config definition), or do not land that hunk here.
2. Re-run a quick import/`dispatch_task_admin_defaults` smoke after the delete.
3. Straggler discuss rows need no product change unless resolve wants Joan re-ack.

### Statutes checked (summary)

56 active statutes swept vs `origin/dev...origin/sub/AST-1087/AST-1089-…`. One **violates** (`astral.standards.in-scope-only`). Full table in Linear review comment.

## Resolution

**2026-07-31** — Radia code-rubric.v1 FIX-NOW addressed.

- **fix-now:** Removed smuggled `dispatch_task_admin_defaults` early-return on `GAZE_EMAIL_CONFIG["task_key"]` from `src/utils/config.py` (AST-1088 shell; undefined on this tip → `NameError`). Belongs on AST-1088 with the config definition.
- **Smoke:** `dispatch_task_admin_defaults("qualify_meteorite")` returns job defaults; Betty AST-1089 manifest still **8 passed**.
- **discuss (straggler):** No product change (Joan / three-dot scoring note only).
