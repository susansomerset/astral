<!-- linear-archive: AST-1133 archived 2026-08-07 -->

## Linear archive (AST-1133)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1133/qualify-meteorite-for-list-created-meteorites-manage-email-create  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1130 — Manage Email create button for job lists isn't working  
**Blocked by / blocks / related:** parent: AST-1130

### Description

## What this implements

After #1 and #2 produce clean **METEORITE_NEW** Dice (or ATS) rows, owns restoring end-to-end qualify so usable extracts reach **METEORITE_QUALIFIED** with title + `company_job_id` (investigate remaining **METEORITE_ERROR_QUALIFY** vs content **FAILED_QUALIFY**). Does **not** widen gaze_email Ruth parse (AST-1089) or change GDL.

## In scope

- [X] `pattern.batch.entity-claim-process-release` — keep claim → `_run_batch_consult` → process → release; harden id reconciliation only
- [X] `pattern.state.entity-state-transitions` — outcomes stay **METEORITE_QUALIFIED** / **METEORITE_FAILED_QUALIFY** / **METEORITE_ERROR_QUALIFY**
- [X] `astral.agent.do-task-delegation` — Ruth still via `do_task` / consult; no UI LLM
- [X] `astral.state.core-decides-transitions` — core owns QUALIFIED vs FAILED vs ERROR landings
- [X] `astral.standards.debug-contract-gated` — Style D bind/link-source detail only when `debug=True`
- [X] `astral.standards.in-scope-only` — `src/core/consult.py` only; no gazer / gaze_email / GDL
- [X] `astral.layers.import-direction` — `normalize_link` from utils into core
- [X] `astral.standards.dry-and-focused-functions` — second bind helper; leave AST-1076 digit rules intact

## Considered but excluded

* Paste HTML normalize / nested autolink unwrap — **AST-1131** (`src/utils/formatting.py`, inbox/gazer wire)
* Link exclude/allow / non-job Playwright skip / candidate-scoped dedupe — **AST-1132** (`gazer.py`, ingest config)
* `gaze_email` Ruth parse widen (AST-1089) / gaze_email dispatch redesign (AST-1087 / AST-1128) — out of epic boundary
* GDL / Recommended meteorites UI / new job states — parent Boundaries
* Force `batch_size=1` or per-job `do_task` fan-out — invents parallel batch shape; parent forbids
* Widen AST-1076 multi-job non-digit UUID remap for all `_run_batch_consult` callers — listing grades stay digit/empty-only; this ticket adds qualify-only `job_link` bind
* Loosen `job_title` / `jd_text` schema `required` or input-JD title fallback — content FAILED stays content FAILED
* `tests/` / bible — Betty after Code Complete

## Acceptance criteria

- [X] After Create of only the real postings from that email, running `qualify_meteorite` moves each usable job to **METEORITE_QUALIFIED** with non-empty `job_title` and non-empty `company_job_id`; none of those usable rows end on **METEORITE_ERROR_QUALIFY**.
- [X] Multi-job batches where Ruth echoes non-claimed non-digit `astral_job_id` but matching `job_link` still bind and can QUALIFY (not blanket ERROR).
- [X] When Ruth omits/non-http `job_link` but Create stored a clean http(s) ATS URL, process uses the Create link for http gate + UUID resolve + persist (not content FAILED solely for empty Ruth link).
- [X] True content/bogus failures (short title, short jd, no resolvable `company_job_id`) still land **METEORITE_FAILED_QUALIFY**.
- [X] Whole-batch `do_task` envelope/schema failures still land **METEORITE_ERROR_QUALIFY**.

## Boundaries

Does **not** own HTML normalize (AST-1131) or link hygiene create skip (AST-1132). Does not widen gaze_email Ruth parse or change GDL.

## Notes for planning

Plan: `docs/features/meteorite/ast-1133-qualify-meteorite-for-list-created-meteorites.md` on publish ref below. Related prior: AST-1076 id-bind UAT, AST-1120/1127 company_job_id fallback.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1130-manage-email-create-button-for-job-lists-isnt-working`, child `sub/AST-1130/AST-1133-qualify-meteorite-for-list-created-meteorites`. Created at dispatch-parent.

### Comments

#### radia — 2026-08-02T20:56:47.530Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1133
**Publish ref:** origin/sub/AST-1130/AST-1133-qualify-meteorite-for-list-created-meteorites @ `a38f2a1bd1c497585547ba2daec20bbc96665108`
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | No grade confidence path changes |
| `astral.agent.do-task-delegation` | scoped | conforms | Still one do_task via _run_batch_consult |
| `astral.agent.grade-vector-validation` | scoped | conforms | No grade vector schema changes |
| `astral.batch.batch-id-first` | scoped | conforms | No claim helper signature changes |
| `astral.batch.batch-id-format` | scoped | conforms | No batch_id format changes |
| `astral.batch.claim-process-release` | scoped | conforms | Batch shape unchanged; bind + process field harden only |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | No agent_data RESPONSE inventory changes |
| `astral.config.config-source-of-truth` | scoped | conforms | No new qualify knobs; rollup config from siblings only |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | No scoring threshold changes |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | No secrets/env values |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths miss diff (['artifacts/**', 'scripts/spikes/**']) |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | Combined plans under docs/features — not spike notes |
| `astral.dispatch.run-next-is-chain-authority` | scoped | conforms | No dispatch/run_next changes |
| `astral.dispatch.seed-auto-false` | scoped | conforms | No seed/dispatch_task AUTO changes in this tip |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | One docs/features plan file for AST-1133 |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test/bible only; merge-tests exception ok |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | Product code() is consult.py; tests from Betty |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | Core-only consult harden; no new I/O |
| `astral.layers.import-direction` | scoped | conforms | normalize_link from utils into core |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers ∩ diff empty (['scripts']); paths miss diff (['scripts/**']) |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | No UI rules; config rollup not UI business logic |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | No coat-check keys |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | qualify_meteorite stays on _run_batch_consult path |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/**']) |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | No seed JSON work |
| `astral.seed.archie-catalog-wins` | scoped | conforms | No catalog seed |
| `astral.seed.boot-only-not-hot-path` | scoped | conforms | No boot seed path |
| `astral.seed.define-approved` | scoped | conforms | No seed define work |
| `astral.seed.operator-rows-stay-deleted` | scoped | conforms | No operator seed rows |
| `astral.seed.other-via-coverage-join` | scoped | conforms | No coverage-join seed |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | No data-layer edits in AST-1133 code() |
| `astral.standards.database-header-inventory` | scoped | conforms | Rollup uses existing job/company tables only |
| `astral.standards.debug-contract-gated` | scoped | conforms | Bind/link_source detail only when debug=True |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Second bind helper; AST-1076 digit rules intact |
| `astral.standards.in-scope-only` | scoped | conforms | AST-1133 code() is consult.py only |
| `astral.standards.logging-via-utils` | scoped | conforms | Style D via existing consult debug helpers |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | _bind_response_jobs_by_job_link product-shaped |
| `astral.standards.no-cross-contamination` | scoped | conforms | qualify_meteorite-only call site; listings bind unchanged |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | No new host/state sets; existing http prefix gate |
| `astral.standards.public-then-helpers` | scoped | conforms | New bind helper next to existing bind helper |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | No utils→data import |
| `astral.state.core-decides-transitions` | scoped | conforms | Core still QUALIFIED / FAILED_QUALIFY / ERROR_QUALIFY |
| `astral.state.job-prior-states-enforced` | scoped | conforms | No JOB_STATES registry edits |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | No run_next / daisy-chain |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/frontend/**']) |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/**']) |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | No gunicorn/worker config changes |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | Single merge-tests(AST-1133) SHA on sub tip |
| `orch.git.commit-vocabulary` | universal | needs-discussion | Two docs-only tip stubs used code() not docs() |
| `orch.git.flow-direction-inviolable` | universal | conforms | Publish stays on origin/sub/AST-1130/AST-1133-… |
| `orch.git.ftr-sub-topology` | universal | conforms | Child sub under AST-1130 parent topology |
| `orch.git.merge-on-checkout` | universal | conforms | No illegal merge-on-checkout recipe |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | No cherry-pick/rebase/force on publish ref |
| `orch.git.no-dev-agent-branches` | universal | conforms | Uses sub/AST-1130/AST-1133-… only |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | Review in astral-AST-1130 epic worktree |
| `orch.git.three-permanent-branches` | universal | conforms | No new permanent branch invented |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | No product-decision fork; plan decisions shipped |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–2 match Files Changed and consult.py diff |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Meteorite child only |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Entered at Tests Passed |
| `orch.roles.archie-approves-statutes` | universal | conforms | No canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | tests/bible via test()+merge-tests |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Assignee remains Katherine |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Implementer stays assignee through review |
| `orch.roles.pre-commit-path-bans` | universal | conforms | No banned-path product commits |

## Pattern conformance

- `pattern.batch.entity-claim-process-release` — **conforms**
- `pattern.state.entity-state-transitions` — **conforms**

## Plan adherence

Three-dot vs origin/dev matches Stages 1–2 in consult.py: job-link claim bind (qualify_meteorite-only) + Create http(s) job_link fallback with link_source Style D. Self-Assessment Single-Component holds. AST-1131/1132 / gaze_email / GDL boundaries held. Sibling epic rollup in three-dot is expected, not scope smuggle in AST-1133 product commits.

## Findings

**discuss:** `orch.git.commit-vocabulary` — `59ec6ce3` / `8d01c0c7` are docs-only plan tip fills committed as `code()`. Prefer `docs()` next time. No history rewrite required — ack only.

**discuss (C4 straggler):** `astral.debug.spikes-under-debug-dir` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action — ack only.

**discuss (C4 straggler):** `astral.dispatch.seed-auto-false` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action — ack only.

**discuss (C4 straggler):** `astral.docs.features-single-file-per-ticket` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action — ack only.

**discuss (C4 straggler):** `astral.git.engineer-test-tree-ban` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action — ack only.

**discuss (C4 straggler):** `astral.layers.ui-config-driven-business-logic` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action — ack only.

**discuss (C4 straggler):** `astral.seed.agent-tables-in-repo-json` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action — ack only.

**discuss (C4 straggler):** `astral.seed.archie-catalog-wins` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action — ack only.

**discuss (C4 straggler):** `astral.seed.operator-rows-stay-deleted` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action — ack only.

**discuss (C4 straggler):** `astral.seed.other-via-coverage-join` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action — ack only.

**discuss (C4 straggler):** `astral.standards.database-header-inventory` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action — ack only.

**discuss (C4 straggler):** `astral.standards.utils-data-late-import-only` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action — ack only.

**discuss (C4 straggler):** `astral.ui.single-gunicorn-worker` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action — ack only.

**fix-now:** none

### What's solid

- Unique normalize_link bind map; never overwrites claimed ids; AST-1076 digit bind intact.
- Ruth http link preferred; Create ATS URL fallback for gate + UUID resolve + persist.
- One merge-tests(AST-1133) SHA; product code() is consult.py only.

### Notes

Joan plan-rubric verdict attached (APPROVED). Docs append on plan file.

context_tokens≈48000

#### betty — 2026-08-02T20:53:48.293Z
## QA test manifest

**Publish:** `origin/sub/AST-1130/AST-1133-qualify-meteorite-for-list-created-meteorites` @ `3e01f3dc` (`merge-tests(AST-1133): origin/tests bbb598e4ab9e74627bbb2b72dee8e9e2e523926c`)

### Classification

1. **Existing coverage (bible-backed):** `TestAst1062QualifyMeteorite`, `TestAst1076QualifyMeteoritePlaceholderId`, `TestAst1120CompanyJobIdFallback`, `TestAst1121CompanyJobIdDebugSource` — regression.
2. **Broken / obsolete (revised this pass):** `TestAst1062QualifyMeteorite::test_content_gates_fail_state` relative-link case — Create http input would pass under new fallback; input link cleared for that row.
3. **Gaps (this pass):** `_bind_response_jobs_by_job_link` + multi-job qualify bind + Create `job_link` fallback + `link_source` Style D.

### Manifest (run these)

1. `tests/component/core/test_consult.py::TestAst1133BindResponseJobsByJobLink`
2. `tests/component/core/test_consult.py::TestAst1133QualifyMeteoriteListCreated`
3. `tests/component/core/test_consult.py::TestAst1062QualifyMeteorite`
4. `tests/component/core/test_consult.py::TestAst1076QualifyMeteoritePlaceholderId`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst1133BindResponseJobsByJobLink \
  tests/component/core/test_consult.py::TestAst1133QualifyMeteoriteListCreated \
  tests/component/core/test_consult.py::TestAst1062QualifyMeteorite \
  tests/component/core/test_consult.py::TestAst1076QualifyMeteoritePlaceholderId \
  -q
```

### Bible shasums on publish-ref

- `8f81d684578d0db145afb469e50e5d305336b28d03c048c3509f01a74cf0b322` `docs/test-bible/core/consult.md`

— Betty

#### joan — 2026-08-02T20:47:18.268Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1133
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 Create only real job-detail postings; zero SVG/namespace | N/A — boundary (AST-1131 / AST-1132) |
| AC2 Clean ATS `job_link` (no nested auto-link markup) | N/A — boundary (AST-1131); Stage 2 consumes Create-stored clean link |
| AC3 Re-Create candidate-scoped dedupe | N/A — boundary (AST-1132) |
| AC4 After clean Create, `qualify_meteorite` → QUALIFIED with title + `company_job_id`; no usable row on ERROR_QUALIFY | Stages 1–2 — link bind closes multi-job ERROR; Create `job_link` fallback closes false FAILED |
| AC5 `debug=True` Style D found/skipped/recorded on Create/ingest | N/A for ingest — child adds qualify-path Style D bind/`link_source` detail under `debug=True` |
| AC6 Single-link / single-JD Create still succeeds | Stage 2 — Ruth http link still preferred; Create path unchanged |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 `_bind_response_jobs_by_job_link` | Functional scope qualify after clean Create; child AC multi-job non-digit bind |
| Stage 2 Create-time `job_link` fallback | Child AC http gate + UUID resolve from Create link; content FAILED vs technical ERROR preserved |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Publish on sub ref with plan()/code() vocabulary |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/AST-1130/AST-1133-… |
| orch.git.ftr-sub-topology | conforms | Child ref matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | conforms | Uses sub/AST-1130/AST-1133-… only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1130 |
| orch.git.three-permanent-branches | conforms | Does not invent permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Decisions documented; no product fork needing Archie |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed present |
| orch.pipeline.project-scoped-queues | conforms | Single-child Meteorite scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan gate only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | No tests/bible edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Katherine) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer path after approve |
| orch.roles.pre-commit-path-bans | conforms | No banned-path edits |
| astral.agent.confidence-bounds | conforms | No grade confidence path changes |
| astral.agent.do-task-delegation | conforms | Still one do_task via _run_batch_consult; no UI LLM |
| astral.agent.grade-vector-validation | conforms | No grade vector schema changes |
| astral.batch.batch-id-first | conforms | No claim helper signature changes |
| astral.batch.batch-id-format | conforms | No batch_id format changes |
| astral.batch.claim-process-release | conforms | Batch shape unchanged; harden bind + process field selection only |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data RESPONSE inventory changes |
| astral.config.config-source-of-truth | conforms | No new config knobs; existing qualify thresholds untouched |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring threshold changes |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env values |
| astral.dispatch.run-next-is-chain-authority | conforms | No dispatch/run_next changes |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src; Betty excluded |
| astral.layers.core-vs-external-bright-line | conforms | Core-only; no new I/O |
| astral.layers.import-direction | conforms | normalize_link from utils into core — allowed |
| astral.patterns.coat-check-never-store-empty | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | conforms | qualify_meteorite stays on _run_batch_consult / do_task path |
| astral.seed.boot-only-not-hot-path | conforms | No seed/boot path |
| astral.seed.define-approved | conforms | No seed define work |
| astral.standards.data-raises-caller-logs | conforms | No data-layer edits |
| astral.standards.debug-contract-gated | conforms | New bind/link_source detail only when debug=True |
| astral.standards.dry-and-focused-functions | conforms | Second bind helper; AST-1076 digit rules left intact |
| astral.standards.in-scope-only | conforms | consult.py only; no gazer/gaze_email/GDL/normalize |
| astral.standards.logging-via-utils | conforms | Style D via existing consult debug helpers |
| astral.standards.names-not-ticket-ids | conforms | Helper names product-shaped (_bind_response_jobs_by_job_link) |
| astral.standards.no-cross-contamination | conforms | qualify_meteorite-only call site; listings bind unchanged |
| astral.standards.no-hardcoded-sets | conforms | No new host/state sets; uses existing http prefix gate |
| astral.standards.public-then-helpers | conforms | New bind helper next to existing bind helper |
| astral.state.core-decides-transitions | conforms | Core still maps pass→QUALIFIED, content→FAILED, technical→ERROR |
| astral.state.job-prior-states-enforced | conforms | No JOB_STATES registry edits; registered outcomes only |
| astral.state.no-daisy-chain-in-run | conforms | No run_next / daisy-chain |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.dispatch.run-next-is-chain-authority, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.seed.boot-only-not-hot-path, astral.seed.define-approved, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.names-not-ticket-ids, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.dispatch.seed-auto-false — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan {core} empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers {scripts} ∩ plan {core} empty
- astral.layers.ui-config-driven-business-logic — layers {ui,utils} ∩ plan {core} empty
- astral.patterns.require-auth-on-protected-endpoints — layers {ui} ∩ plan {core} empty
- astral.seed.agent-tables-in-repo-json — paths match none of plan paths
- astral.seed.archie-catalog-wins — paths match none of plan paths
- astral.seed.operator-rows-stay-deleted — paths match none of plan paths
- astral.seed.other-via-coverage-join — paths match none of plan paths
- astral.standards.database-header-inventory — layers {data} ∩ plan {core} empty
- astral.standards.utils-data-late-import-only — layers {utils} ∩ plan {core} empty
- astral.ui.frontend-file-placement — layers {ui} ∩ plan {core} empty
- astral.ui.naming-conventions — layers {ui} ∩ plan {core} empty
- astral.ui.single-gunicorn-worker — layers {ui,scripts,utils} ∩ plan {core} empty

## Findings

None fix-now.

**discuss (non-blocking):** Stage 1 drops ambiguous duplicate normalized claim links from the bind map. Correct conservative choice; if Ruth echoes identical links for two claims, those rows still follow existing MISSING/FABRICATED accounting.

**acceptable:** Self-assessment Single-Component / Conf high / Risk Medium matches mis-pair risk; mitigations (unique map, never overwrite claimed ids, qualify_meteorite-only) are specific. Does not force `batch_size=1` or widen AST-1076 digit remap.

**R6 checklist:** Definition fidelity pass for child #3. Layers/import pass. No new config. Batch claim→process→release shape preserved. State outcomes stay registered. Boundaries vs AST-1131/1132 / gaze_email / GDL respected.

context_tokens≈38000

— Joan

#### katherine — 2026-08-02T20:45:12.438Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1130/AST-1133-qualify-meteorite-for-list-created-meteorites/docs/features/meteorite/ast-1133-qualify-meteorite-for-list-created-meteorites.md

`origin/sub/AST-1130/AST-1133-qualify-meteorite-for-list-created-meteorites` @ `6965f9bf`

**Scope:** Single-Component — `src/core/consult.py` only (job-link claim bind + Create-time `job_link` fallback in `qualify_meteorite` process).

**Conf:** high — tip already has AST-1062 apply, AST-1076 digit bind, AST-1120/1127 UUID resolve; remaining usable-row ERROR/FAILED paths are the two gaps in the plan diagnosis.

**Risk:** Medium — link bind could mis-pair if Ruth returns wrong links; mitigated by unique `normalize_link` map, never overwriting claimed ids, and qualify_meteorite-only call site.

---

# AST-1133 — qualify_meteorite for list-created meteorites

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1133/qualify-meteorite-for-list-created-meteorites-manage-email-create  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1130/manage-email-create-button-for-job-lists-isnt-working  

**Publish ref (origin):** `sub/AST-1130/AST-1133-qualify-meteorite-for-list-created-meteorites`  
**Parent integration ref:** `ftr/AST-1130-manage-email-create-button-for-job-lists-isnt-working`

After AST-1131 / AST-1132 produce clean **METEORITE_NEW** rows from Manage Email list Create (Dice Saved-jobs HTML or newline-delimited ATS links), owns restoring end-to-end `qualify_meteorite` so usable extracts reach **METEORITE_QUALIFIED** with non-empty `job_title` and non-empty `company_job_id`. Investigates remaining **METEORITE_ERROR_QUALIFY** (technical / missing-id) vs content **METEORITE_FAILED_QUALIFY**. Does **not** widen `gaze_email` Ruth parse (AST-1089), change GDL, or re-own paste normalize / link hygiene.

**Diagnosis (code tip after AST-1131+1132 merge — no runtime spike required):**

Create already lands `job_link` + Playwright JD with null title / null `company_job_id` (`create_meteorite_job`). Shipped qualify path already has: Pattern-A batch apply (AST-1062), placeholder `"000"` / `\d{1,3}` bind (AST-1076), optional schema `company_job_id` + UUID-from-`job_link` resolve (AST-1120 / AST-1127). Two remaining gaps still push **usable** list-created rows off the QUALIFIED path:

1. **Multi-job claim-id bind gap → ERROR:** `_bind_response_jobs_to_claimed` only remaps empty/`\d{1,3}` when `len(response) == len(claimed)`. When Ruth echoes a non-digit wrong id (e.g. external UUID, or job URL) into `astral_job_id` on a multi-job batch, every row is treated as FABRICATED and every claim becomes MISSING → **METEORITE_ERROR_QUALIFY**. List Create commonly qualifies 2–N jobs in one batch; single-job bind does not cover that shape.
2. **Create-time `job_link` ignored by http content gate → FAILED:** `qualify_meteorite` process already uses `input_job["job_link"]` for `_resolve_company_job_id` fallback, but the `job_link.startswith("http")` gate and `initialize_job` persist only Ruth’s `job_link`. Empty / non-http Ruth link fails content gate even when Create stored a clean ATS URL — wrong outcome for usable extracts (should QUALIFY with create link, not FAILED/ERROR).

True content failures (short title, short `jd_text`, no AI id and no UUID in any usable link) stay **METEORITE_FAILED_QUALIFY**. Whole-batch `do_task` envelope/schema failures stay **METEORITE_ERROR_QUALIFY** (not reinvented here).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Job-link claim-id bind for `qualify_meteorite` multi-job batches; input `job_link` fallback in `qualify_meteorite` process + Style D source label | core |

No config / gazer / inbox / dispatcher / agent_task / UI / `tests/` / bible changes (Betty after Code Complete). Do **not** edit `_bind_response_jobs_to_claimed` digit rules (AST-1076 stays as-is). Do **not** invent a parallel batch shape or force `batch_size=1`.

---

## Stage 1: Bind multi-job qualify responses by `job_link` when claim ids mismatch

**Done when:** A multi-job `qualify_meteorite` batch whose Ruth rows carry usable title / link / jd / id fields but non-claimed non-digit `astral_job_id` values still bind 1:1 to claimed rows via normalized `job_link`, reach `process_fn`, and can land **METEORITE_QUALIFIED**; equal-count digit/`000` bind (AST-1076) still works first; unmatched / ambiguous links are left for existing MISSING/FABRICATED accounting; `qualify_job_listings` path unchanged; `python3 -m py_compile src/core/consult.py` succeeds.

1. In `src/core/consult.py`, immediately after `_bind_response_jobs_to_claimed`, add:

```python
def _bind_response_jobs_by_job_link(response_jobs: list, claimed_jobs: list) -> None:
    """Bind unmatched response rows to claimed jobs by normalized job_link (AST-1133).

    Used when Ruth puts a non-digit wrong value in astral_job_id on multi-job
    qualify_meteorite batches. Does not overwrite ids already in the claim set.
    """
```

2. Implement literally:

- Import `normalize_link` from `src.utils.formatting` at module top if not already imported (consult already imports `uuid_path_segment_from_url` from the same module — add `normalize_link` to that import).
- Skip if `response_jobs` empty or `claimed_jobs` empty.
- `claimed_ids = [j["astral_job_id"] for j in claimed_jobs if j.get("astral_job_id")]`
- `claimed_set = set(claimed_ids)`
- `claimed_by_link: dict[str, str] = {}` — for each claimed job with both `astral_job_id` and a non-empty `normalize_link(job_link)`, map `norm → astral_job_id`. If two claims normalize to the same key, **drop that key** from the map (ambiguous — do not bind either via link).
- `assigned = { (rj.get("astral_job_id") or "").strip() for rj in response_jobs if isinstance(rj, dict) and (rj.get("astral_job_id") or "").strip() in claimed_set }`
- For each `rj` in `response_jobs` where `isinstance(rj, dict)`:
  - `aid = (rj.get("astral_job_id") or "").strip()`
  - If `aid in claimed_set`: continue
  - `norm = normalize_link(rj.get("job_link") or "")`
  - If not `norm`: continue
  - `target = claimed_by_link.get(norm)`
  - If not `target` or `target in assigned`: continue
  - Set `rj["astral_job_id"] = target`; add `target` to `assigned`

⚠️ **Decision — second helper, do not widen AST-1076 digit remap:** AST-1076 explicitly refuses to overwrite non-digit fabricated UUIDs on multi-job batches (correct for listing grades). List-created meteorites have authoritative Create `job_link`s that Ruth is also asked to echo — link match is a safe second key without promoting arbitrary UUID remaps.

⚠️ **Decision — qualify_meteorite only:** Call this helper only for `task_key == "qualify_meteorite"` so roster `qualify_job_listings` keeps today’s bind surface.

3. In `_run_batch_consult`, immediately after `_bind_response_jobs_to_claimed(response_jobs, jobs)`, add:

```python
    if task_key == "qualify_meteorite":
        _bind_response_jobs_by_job_link(response_jobs, jobs)
```

4. When `debug` and `task_key == "qualify_meteorite"`, after both binds, emit one `debug_detail` listing final `astral_job_id` values on `response_jobs` (compact list). Do **not** emit when `debug=False`.

**Done when (recheck):** Claimed links `L0,L1,L2` with ids `C0,C1,C2`; Ruth returns three jobs with `astral_job_id` = Dice UUIDs (not C*) but `job_link` matching `L0..L2` and usable title/jd/company_job_id → after bind, `received_ids == {C0,C1,C2}`, no MISSING, process runs, states can reach **METEORITE_QUALIFIED**. Ambiguous duplicate normalized links → no link-bind for that key; digit bind still applies when lengths match.

---

## Stage 2: Prefer Create-time `job_link` when Ruth’s link is unusable

**Done when:** `qualify_meteorite` process uses a http(s) `job_link` from the claimed input row when Ruth’s `job_link` is empty or does not start with `"http"`; UUID resolve + `initialize_job` persist that link; content fail for short title / short jd / empty resolved `company_job_id` still → **METEORITE_FAILED_QUALIFY**; Style D records whether link came from AI or input; single-job happy path with good Ruth link unchanged; `python3 -m py_compile src/core/consult.py` succeeds.

1. In `qualify_meteorite`’s `process` closure, replace the current strip + resolve preamble so that after reading Ruth fields:

```python
        ai_company_job_id = (response_job.get("company_job_id") or "").strip()
        job_title = (response_job.get("job_title") or "").strip()
        ruth_link = (response_job.get("job_link") or "").strip()
        input_link = (input_job.get("job_link") or "").strip()
        jd_text = (response_job.get("jd_text") or "").strip()
        if ruth_link.startswith("http"):
            job_link = ruth_link
            link_source = "AI"
        elif input_link.startswith("http"):
            job_link = input_link
            link_source = "input"
        else:
            job_link = ruth_link
            link_source = "neither"
        company_job_id = _resolve_company_job_id(ai_company_job_id, job_link)
```

2. Keep the existing `id_source` labels for `company_job_id` (`AI` / `UUID-from-job_link` / `neither`) based on `ai_company_job_id` vs resolved id — unchanged logic, but pass `job_link` (post-fallback) into `_resolve_company_job_id` (no separate `link_for_id`).

3. Keep content gates in this order: empty `company_job_id` → title too short → `not job_link.startswith("http")` → `jd_text` too short. On fail / pass Style D detail lines, append `link_source={link_source}` next to the existing `found source={id_source}` bits (debug only).

4. Pass path: `parsed_job["job_link"]` must be the post-fallback `job_link` (so Create ATS URL is recorded when Ruth omitted it).

⚠️ **Decision — no jd_text / title fallback from input:** Title is null at Create; Playwright body may be chrome-heavy. Ruth still owns title + authoritative `jd_text`. Only `job_link` is Create-authoritative for list ingest.

⚠️ **Decision — Ruth http link wins when present:** Prefer AI enrich URL when it is a real http(s) link; fall back only when Ruth’s value cannot satisfy the http gate.

**Done when (recheck):** Claimed job with `job_link=https://www.dice.com/job-detail/<uuid>`, Ruth returns title + jd + omit/`null` `company_job_id` + empty `job_link` → resolve UUID from input link, pass http gate, → **METEORITE_QUALIFIED** with non-empty title + `company_job_id` + recorded Dice link. Short title still → **METEORITE_FAILED_QUALIFY**. Envelope `do_task` failure still → **METEORITE_ERROR_QUALIFY** for the batch (unchanged).

---

## Self-Assessment

**Scope:** `Single-Component` — one core file (`consult.py`); bind helper + qualify process link fallback only.

**Conf:** `high` — tip after 1131/1132 already has apply + digit bind + UUID resolve; remaining ERROR/FAILED paths for usable list rows are the two concrete gaps above.

**Risk:** `Medium` — over-eager link bind could mis-pair if Ruth returns wrong links; mitigated by unique normalized-link map + never overwriting claimed ids + qualify_meteorite-only call site. Wrong input-link fallback would persist Create URL when Ruth intended a different http link — mitigated by preferring Ruth whenever it starts with `http`.

---

## Self-review vs ASTRAL_CODE_RULES

- **§2.4 claim-process-release / `pattern.batch.entity-claim-process-release`:** Batch shape unchanged; only id reconciliation + process field selection harden.
- **§2.6 / `astral.state.core-decides-transitions`:** Core still maps pass → QUALIFIED, content → FAILED_QUALIFY, technical → ERROR_QUALIFY; no new states.
- **§2.2 / `astral.agent.do-task-delegation`:** Still one `do_task` via `_run_batch_consult`; no UI LLM.
- **§1.5.1 / `astral.standards.debug-contract-gated`:** New detail only under existing `debug` gates.
- **§1.3 DRY:** Second bind helper; digit rules left in AST-1076 helper.
- **§1.1 in-scope-only:** No gazer / gaze_email / GDL / config knobs.
- **§3.3 import-direction:** `normalize_link` from utils into core — already allowed.

No plan conflicts requiring `conf-!!-NONE`.

---

## Review (build stub)

**Publish ref:** `origin/sub/AST-1130/AST-1133-qualify-meteorite-for-list-created-meteorites`  
**Plan path:** `docs/features/meteorite/ast-1133-qualify-meteorite-for-list-created-meteorites.md`

**Built tip:** `f172b5376185b2842c79f06fd506a0defc148a44` (`f172b537`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–2 | `f172b537` | job-link claim bind + Create-time job_link fallback in qualify_meteorite |

---

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1133
**Publish ref tip:** `3e01f3dc3bf0a7a30557c00fd5871de580995a8c`
**Overall:** DISCUSS

### What's solid

- Stages 1–2 match: `_bind_response_jobs_by_job_link` (unique normalize_link map, no overwrite of claimed ids, qualify_meteorite-only) + Create http(s) `job_link` fallback with `link_source` Style D.
- AST-1076 digit bind left intact; claim→process→release shape unchanged; QUALIFIED / FAILED_QUALIFY / ERROR_QUALIFY outcomes preserved.
- AST-1133 `code()` product touch is `consult.py` only; Betty `test()` + one `merge-tests`.

### Issues

**discuss:** `orch.git.commit-vocabulary` — `59ec6ce3` / `8d01c0c7` are docs-only plan tip fills committed as `code()`. Should have been `docs()`. No rewrite required; ack for future.

**discuss (C4 straggler):** `astral.debug.spikes-under-debug-dir` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.dispatch.seed-auto-false` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.docs.features-single-file-per-ticket` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.git.engineer-test-tree-ban` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.layers.ui-config-driven-business-logic` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.seed.agent-tables-in-repo-json` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.seed.archie-catalog-wins` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.seed.operator-rows-stay-deleted` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.seed.other-via-coverage-join` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.standards.database-header-inventory` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.standards.utils-data-late-import-only` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.
**discuss (C4 straggler):** `astral.ui.single-gunicorn-worker` — Joan excluded; in-scope on three-dot vs origin/dev (epic rollup). Scores **conforms**. No product action.

### Recommended actions

- Engineer: ack vocabulary + C4 stragglers (no src change), then User Testing via `resolve-child`.

### Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | No grade confidence path changes |
| `astral.agent.do-task-delegation` | scoped | conforms | Still one do_task via _run_batch_consult |
| `astral.agent.grade-vector-validation` | scoped | conforms | No grade vector schema changes |
| `astral.batch.batch-id-first` | scoped | conforms | No claim helper signature changes |
| `astral.batch.batch-id-format` | scoped | conforms | No batch_id format changes |
| `astral.batch.claim-process-release` | scoped | conforms | Batch shape unchanged; bind + process field harden only |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | No agent_data RESPONSE inventory changes |
| `astral.config.config-source-of-truth` | scoped | conforms | No new qualify knobs; rollup config from siblings only |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | No scoring threshold changes |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | No secrets/env values |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | not-applicable | paths miss diff (['artifacts/**', 'scripts/spikes/**']) |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | Combined plans under docs/features — not spike notes |
| `astral.dispatch.run-next-is-chain-authority` | scoped | conforms | No dispatch/run_next changes |
| `astral.dispatch.seed-auto-false` | scoped | conforms | No seed/dispatch_task AUTO changes in this tip |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | One docs/features plan file for AST-1133 |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test/bible only; merge-tests exception ok |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | Product code() is consult.py; tests from Betty |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | Core-only consult harden; no new I/O |
| `astral.layers.import-direction` | scoped | conforms | normalize_link from utils into core |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | not-applicable | layers ∩ diff empty (['scripts']); paths miss diff (['scripts/**']) |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | No UI rules; config rollup not UI business logic |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | No coat-check keys |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | qualify_meteorite stays on _run_batch_consult path |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/**']) |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | No seed JSON work |
| `astral.seed.archie-catalog-wins` | scoped | conforms | No catalog seed |
| `astral.seed.boot-only-not-hot-path` | scoped | conforms | No seed/boot path |
| `astral.seed.define-approved` | scoped | conforms | No seed define work |
| `astral.seed.operator-rows-stay-deleted` | scoped | conforms | No operator seed rows |
| `astral.seed.other-via-coverage-join` | scoped | conforms | No coverage-join seed |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | No data-layer edits in AST-1133 code() |
| `astral.standards.database-header-inventory` | scoped | conforms | Rollup uses existing job/company tables only |
| `astral.standards.debug-contract-gated` | scoped | conforms | Bind/link_source detail only when debug=True |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | Second bind helper; AST-1076 digit rules intact |
| `astral.standards.in-scope-only` | scoped | conforms | AST-1133 code() is consult.py only |
| `astral.standards.logging-via-utils` | scoped | conforms | Style D via existing consult debug helpers |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | _bind_response_jobs_by_job_link product-shaped |
| `astral.standards.no-cross-contamination` | scoped | conforms | qualify_meteorite-only call site; listings bind unchanged |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | No new host/state sets; existing http prefix gate |
| `astral.standards.public-then-helpers` | scoped | conforms | New bind helper next to existing bind helper |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | No utils→data import |
| `astral.state.core-decides-transitions` | scoped | conforms | Core still QUALIFIED / FAILED_QUALIFY / ERROR_QUALIFY |
| `astral.state.job-prior-states-enforced` | scoped | conforms | No JOB_STATES registry edits |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | No run_next / daisy-chain |
| `astral.ui.frontend-file-placement` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/frontend/**']) |
| `astral.ui.naming-conventions` | scoped | not-applicable | layers ∩ diff empty (['ui']); paths miss diff (['src/ui/**']) |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | No gunicorn/worker config changes |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | Single merge-tests(AST-1133) SHA on sub tip |
| `orch.git.commit-vocabulary` | universal | needs-discussion | Two docs-only tip stubs used code() not docs() |
| `orch.git.flow-direction-inviolable` | universal | conforms | Publish stays on origin/sub/AST-1130/AST-1133-… |
| `orch.git.ftr-sub-topology` | universal | conforms | Child sub under AST-1130 parent topology |
| `orch.git.merge-on-checkout` | universal | conforms | No illegal merge-on-checkout recipe |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | No cherry-pick/rebase/force on publish ref |
| `orch.git.no-dev-agent-branches` | universal | conforms | Uses sub/AST-1130/AST-1133-… only |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | Review in astral-AST-1130 epic worktree |
| `orch.git.three-permanent-branches` | universal | conforms | No new permanent branch invented |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | No product-decision fork; plan decisions shipped |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stages 1–2 match Files Changed and consult.py diff |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Astral Meteorite child only |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | Entered at Tests Passed |
| `orch.roles.archie-approves-statutes` | universal | conforms | No canon/statutes edits |
| `orch.roles.betty-owns-test-tree` | universal | conforms | tests/bible via test()+merge-tests |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Assignee remains Katherine |
| `orch.roles.engineer-assignee-through-resolve` | universal | conforms | Implementer stays assignee through review |
| `orch.roles.pre-commit-path-bans` | universal | conforms | No banned-path product commits |

### Pattern conformance

- `pattern.batch.entity-claim-process-release` — **conforms**
- `pattern.state.entity-state-transitions` — **conforms**

### Plan adherence

Self-Assessment **Single-Component** matches (`consult.py` only for this ticket). Boundaries vs AST-1131/1132 / gaze_email / GDL held. Three-dot vs origin/dev carries sibling epic rollup — expected, not scope smuggle in AST-1133 product commits.

context_tokens≈48000

---

## Resolution

**Date:** 2026-08-02  
**Commit:** `resolve(AST-1133): — clean`

### Against Radia review (`a38f2a1b` / Overall DISCUSS)

- **fix-now:** none — no product changes.
- **discuss:** `orch.git.commit-vocabulary` — ack; `59ec6ce3` / `8d01c0c7` plan tip fills should have been `docs()`; no history rewrite.
- **discuss (C4 stragglers):** ack; all scored **conforms** / no product action (epic-rollup in-scope noise).
- **advisory:** none.

Product tip remains `f172b537` (`consult.py` Stages 1–2); Betty manifest green @ `3e01f3dc`; Radia docs intake @ `a38f2a1b`.
