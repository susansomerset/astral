<!-- linear-archive: AST-1099 archived 2026-08-07 -->

## Linear archive (AST-1099)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1099/pin-agent-data-id-on-job-artifact-slots-after-chain-hops-job-resume  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1091 — Job resume artifact, cover letter and suggested responses is not saved in job_data  
**Blocked by / blocks / related:** parent: AST-1091; blocks: AST-1100

### Description

## What this implements

After successful `finalize_job_resume` / `finalize_cover_letter` / `propose_application_responses`, core (existing before/after-`do_task` persist style — not a new TASK_CONFIG field) writes `job_data.artifacts.job_resume` / `cover_letter` / `proposed_answers` as that hop's RESPONSE `agent_data_id`, including mid-chain when `run_next` continues. Debug found/recorded. Does not own JAR/UI resolve (sibling Katherine ticket).

## In scope

- [X] `pattern.batch.entity-agent-responses` — RESPONSE rows in `agent_data` remain the content store; pin writes pointer ids only
- [X] `astral.batch.entity-agent-responses-latest-only` — pin by RESPONSE `agent_data_id`; do not revive entity-row `agent_responses` JSON
- [X] `astral.patterns.coat-check-never-store-empty` — blank/empty id skips write; prior pointer preserved
- [X] `astral.standards.debug-contract-gated` — Style D key + `agent_data_id` (or skip reason) only when `debug=True`
- [X] `astral.standards.dry-and-focused-functions` — one tracker pin helper + config map; extend post-RESPONSE persist, no parallel framework
- [X] `astral.standards.logging-via-utils` — pin debug via `get_logger` / `debug_detail`
- [X] `astral.config.config-source-of-truth` — task_key → slot map in `config.py` (no TASK_CONFIG `persist_in`)
- [X] `astral.layers.import-direction` — core (`agent` / `tracker`) writes; data via existing `save_job_data`

## Considered but excluded

- [X] JAR / Materials Preview / API body resolve from pinned ids — AST-1100 (`src/ui/`, builder readers)
- [X] `JOBS_RECOMMENDED_ARTIFACT_TABS` `artifact_key` remaps — AST-1100
- [X] TASK_CONFIG `persist_in` (or any new task-level destination dialect) — parent forbids
- [X] `save_prefix` grade writes, candidate craft persists, `analysis_upshot` one-offs — parent Boundaries
- [X] Copy full hop JSON into `job_data.artifacts` for the three pin slots — pointer only
- [X] `tests/` / `docs/test-bible/**` — Betty

## Acceptance criteria

- [X] 1. After a successful `finalize_job_resume` hop (chain may continue), `job_data.artifacts.job_resume` equals that hop's RESPONSE `agent_data_id` and that id loads the hop body from `agent_data`.
- [X] 2. After a successful `finalize_cover_letter` hop (chain may continue), `job_data.artifacts.cover_letter` equals that hop's RESPONSE `agent_data_id` and that id loads the hop body from `agent_data`.
- [X] 3. After a successful `propose_application_responses` hop, `job_data.artifacts.proposed_answers` equals that hop's RESPONSE `agent_data_id` and that id loads the hop body from `agent_data`.
- [X] 4. When `debug=True` on the touched persist path, each pin attempt logs key + `agent_data_id` (or skip reason); no new ungated `[DEBUG]` spam.
- [X] 5. Failed or empty hops do not overwrite a good prior pointer with a blank value.

## Boundaries

Does not own JAR/UI resolve of pinned ids (sibling). Does not add TASK_CONFIG `persist_in`. Does not copy full hop JSON into job_data. Does not migrate grade/craft/analysis_upshot persists.

## Notes for planning

Pin pointers only; body stays in `agent_data`. Mid-chain hops with `run_next` must still pin.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/ast-1091-job-artifact-agent-data-pins`, child `sub/AST-1091/AST-1099-pin-agent-data-id`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-07-31T04:58:24.616Z
[merge-child] blocked: git pull merge on sub — use: `git fetch && git merge origin/ftr/ast-1091-job-artifact-agent-data-pins` (no `Merge remote-tracking branch 'origin/dev'|origin/sub…` on publish ref).

`validate-sub-log.sh` failed for `origin/sub/AST-1091/AST-1099-pin-agent-data-id`. Offending subjects include:
- `Merge remote-tracking branch 'origin/sub/AST-1091/AST-1099-pin-agent-data-id' into …`
- `Merge remote-tracking branch 'origin/dev' into …`

@Ada Lovelace — republish a clean sub tip (merge `origin/ftr/…` / `origin/dev` per orientation § Merge integration line; no pull-merge commit subjects), then Chuckles retries merge-child.

— Chuckles

#### chuckles — 2026-07-31T04:58:20.288Z
[merge-child] blocked: git pull merge on sub — use: `git fetch && git merge origin/ftr/ast-1091-job-artifact-agent-data-pins` (no `Merge remote-tracking branch 'origin/dev'|origin/sub…` on publish ref).

`validate-sub-log.sh` failed for `origin/sub/AST-1091/AST-1099-pin-agent-data-id`. Offending subjects include:
- `Merge remote-tracking branch 'origin/sub/AST-1091/AST-1099-pin-agent-data-id' into …`
- `Merge remote-tracking branch 'origin/dev' into …`

@Ada Lovelace — republish a clean sub tip (merge `origin/ftr/…` / `origin/dev` per orientation § Merge integration line; no pull-merge commit subjects), then Chuckles retries merge-child.

— Chuckles

#### radia — 2026-07-31T04:55:52.910Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1099
**Publish ref:** `origin/sub/AST-1091/AST-1099-pin-agent-data-id` @ `3c6d9ff0` (code `76928f73`; merge-tests `fe09931b`)
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | One `merge-tests(AST-1099)` → `449c61cc` |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests vocabulary on sub |
| orch.git.flow-direction-inviolable | universal | conforms | Publish forward on origin/sub only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1091/AST-1099-…` matches Git table |
| orch.git.merge-on-checkout | universal | conforms | No illegal merge recipe in ticket commits |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | None in AST-1099 history |
| orch.git.no-dev-agent-branches | universal | conforms | Child sub only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Reviewed in astral-AST-1091 |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No open product fork in diff |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–3 implemented as planned |
| orch.pipeline.project-scoped-queues | universal | conforms | Single-child review |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Entered from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty test + merge-tests commits |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Implementer path was Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | No assignee change by this review |
| orch.roles.pre-commit-path-bans | universal | conforms | Doc-only Radia commit; engineer stayed off bans |
| astral.agent.confidence-bounds | scoped | conforms | No graded confidence path touched |
| astral.agent.do-task-delegation | scoped | conforms | Pin extends post-RESPONSE path inside `do_task` |
| astral.agent.grade-vector-validation | scoped | conforms | No grade-vector changes |
| astral.batch.batch-id-first | scoped | conforms | No claim/batch API signature changes |
| astral.batch.batch-id-format | scoped | conforms | No batch_id format changes |
| astral.batch.claim-process-release | scoped | conforms | No claim/release changes |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | Pin by RESPONSE id; body stays in `agent_data` |
| astral.config.config-source-of-truth | scoped | conforms | `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` in config.py |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | No scoring/threshold changes |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env literals |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no `artifacts/**` / spikes paths |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Plan under `docs/features/` (not misplaced spike) |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Single `docs/features/artifacts/ast-1099-….md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty did not edit src/features; engineer owns those |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer code commit left tests/bible to Betty |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Core persist only; no external I/O |
| astral.layers.import-direction | scoped | conforms | Core→tracker/config; lazy import; data via `save_job_data` |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no `scripts/**` in ticket change set |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Config map only; no UI business logic |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | Blank/None/whitespace id skips write |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | No consult/`render_verdict` changes |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | no `src/ui/**` in ticket change set |
| astral.standards.data-raises-caller-logs | scoped | conforms | Existing `save_job_data`; core owns pin/debug |
| astral.standards.database-header-inventory | scoped | not-applicable | no `src/data/**` in ticket change set |
| astral.standards.debug-contract-gated | scoped | conforms | Style D `debug_detail` only when `debug=True` |
| astral.standards.dry-and-focused-functions | scoped | conforms | One helper + one map; extend existing persist |
| astral.standards.in-scope-only | scoped | conforms | Three pin slots + write path; AST-1100 excluded |
| astral.standards.logging-via-utils | scoped | conforms | `get_logger` / `debug_detail` |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in core/utils (+ Betty tests) |
| astral.standards.no-hardcoded-sets | scoped | conforms | Task keys/slots in config map |
| astral.standards.public-then-helpers | scoped | conforms | Pin helper beside existing artifact saves |
| astral.standards.utils-data-late-import-only | scoped | conforms | No new utils→data import |
| astral.state.core-decides-transitions | scoped | conforms | No state-machine transition changes |
| astral.state.job-prior-states-enforced | scoped | conforms | No job prior-state changes |
| astral.state.no-daisy-chain-in-run | scoped | conforms | Mid-chain pin under existing `run_next`; no new daisy-chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | no `src/ui/frontend/**` |
| astral.ui.naming-conventions | scoped | not-applicable | no `src/ui/**` |
| astral.ui.single-gunicorn-worker | scoped | conforms | Config touch is pin map only; no worker changes |

## Pattern conformance

| cited | verdict |
|-------|---------|
| pattern.batch.entity-agent-responses | conforms |
| astral.batch.entity-agent-responses-latest-only | conforms |
| astral.patterns.coat-check-never-store-empty | conforms |
| astral.standards.debug-contract-gated | conforms |
| astral.standards.dry-and-focused-functions | conforms |
| astral.standards.logging-via-utils | conforms |
| astral.config.config-source-of-truth | conforms |
| astral.layers.import-direction | conforms |

## Plan adherence

Stages 1–3 match the combined plan: config map + clear keys, tracker pin helper (never-store-empty + Style D), `do_task` pin before `run_next`, terminal body-copy removed for finalize hops. Self-Assessment Single-Component / high / Medium still fits the footprint. Sibling AST-1100 (JAR/UI resolve) untouched.

## Findings

**discuss (C4 straggler):** Joan excluded `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, and `astral.debug.spikes-under-debug-dir`; ticket-scoped diff brings them in-scope. All three **conform** (single features file; Betty owns tests/bible; plan under `docs/features/`). No product fix-now.

**advisory:** Stopping terminal `persist_job_artifact_from_parsed` for finalize hops leaves pointer-string `artifacts.cover_letter` / `job_resume` until AST-1100 — intentional Medium risk already in plan/Joan.

## Notes

- Change set for applies_when + product judgment: AST-1099 commits on publish tip (formal `origin/dev...` three-dot is epic-ancestry polluted / multiple merge bases).
- Plan-rubric verdict attached (Joan APPROVED).
- Docs append: `docs/features/artifacts/ast-1099-pin-agent-data-id.md` @ `3c6d9ff0`.

context_tokens≈42000

— Radia

#### betty — 2026-07-31T04:51:02.394Z
## QA test manifest

`origin/sub/AST-1091/AST-1099-pin-agent-data-id` @ `fe09931b` (`merge-tests(AST-1099): origin/tests 449c61ccdfa86241eadf4f3798504e4d50fab3fc`)

### 1. Existing coverage (bible-backed)

None sufficient alone for the new pin helper / mid-chain path.

### 2. Broken / obsolete

- Any expectation that terminal `do_task` body-copies `finalize_job_resume` / `finalize_cover_letter` into `artifacts.resume_content` / dict `cover_letter` — superseded by pointer pin (AST-1100 remaps readers). No existing component assertion required a rewrite beyond the new suites.

### 3. Gaps (this pass)

1. Config pin map + cancel clear keys — `tests/component/utils/test_config.py::TestAst1099JobArtifactAgentDataPinConfig`
2. Tracker pin helper (write / never-store-empty / debug / clear pin slots) — `tests/component/core/test_tracker.py::TestAst1099PinJobArtifactAgentDataId`
3. `do_task` mid-chain + terminal pins; failure skip; store-fail debug skip; no `persist_job_artifact_from_parsed` on finalize hops — `tests/component/core/test_agent.py::TestAst1099DoTaskArtifactPin`

**Integration:** none (revise-existing only; JAR resolve = AST-1100).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1099JobArtifactAgentDataPinConfig \
  tests/component/core/test_tracker.py::TestAst1099PinJobArtifactAgentDataId \
  tests/component/core/test_agent.py::TestAst1099DoTaskArtifactPin \
  -q
```

### Bible shasums on publish tip

- `docs/test-bible/core/tracker.md` `7c44a935637153dc6f94f57ce39d0ceae83e514d3924d0adf1f9cfa6febfb244`
- `docs/test-bible/core/agent.md` `53781b3e97157fe46f9fc95c641dfa7fd749644d37fb03405d3175ab6e428a95`
- `docs/test-bible/utils/config.md` `af82f09b8d97bb3a53a0fa057befff62483b0a0e739c770c81ff5716aa7b29ba`

— Betty

#### joan — 2026-07-31T04:44:01.910Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1099
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 `finalize_job_resume` → `artifacts.job_resume` = RESPONSE id; id loads body | Stages 1–3 (pin); load via existing `agent_data` by id |
| AC2 `finalize_cover_letter` → `artifacts.cover_letter` = RESPONSE id | Stages 1–3; stop terminal body-copy so pointer not overwritten |
| AC3 `propose_application_responses` → `artifacts.proposed_answers` = RESPONSE id | Stages 1–3 (no existing body-copy for this key) |
| AC4 full chain leaves three pointers; UAT surfaces resolve via ids | Pointers: Stages 1–3. Surface resolve: N/A — boundary (AST-1100) |
| AC5 `debug=True` pin attempt logs key + id or skip; no ungated spam | Stage 2 Style D `debug_detail` |
| AC6 failed/empty hops do not blank a good prior pointer | Stage 2 never-store-empty; Stage 3 no pin on failure stores |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 config pin map + clear keys | Purpose/Architectural — config/convention map; no `persist_in` |
| Stage 2 tracker pin helper | Functional scope core write + coat-check + debug found/recorded |
| Stage 3 do_task pin before run_next; stop finalize body-copy | Functional scope mid-chain pin; Boundaries pointer-only |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests work |
| orch.git.commit-vocabulary | conforms | Publish on sub via plan/code vocabulary |
| orch.git.flow-direction-inviolable | conforms | origin/sub only; no reverse flow |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | sub/AST-1091/AST-1099-… only |
| orch.git.one-epic-worktree-per-parent | conforms | astral-AST-1091 epic worktree |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Explicit Decisions; no open product fork |
| orch.pipeline.plan-is-bible | conforms | Binding stages + Files Changed |
| orch.pipeline.project-scoped-queues | conforms | Single-child scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate only |
| orch.roles.archie-approves-statutes | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | conforms | tests/ out of scope |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Ada) owns build |
| orch.roles.engineer-assignee-through-resolve | conforms | Implementer path after approve |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No graded confidence path touched |
| astral.agent.do-task-delegation | conforms | Extends post-RESPONSE persist inside `do_task`; no bypass |
| astral.agent.grade-vector-validation | conforms | No grade-vector changes |
| astral.batch.batch-id-first | conforms | No claim/batch API signature changes |
| astral.batch.batch-id-format | conforms | No batch_id format changes |
| astral.batch.claim-process-release | conforms | No claim/release changes |
| astral.batch.entity-agent-responses-latest-only | conforms | Pin by RESPONSE `agent_data_id`; body stays in `agent_data` |
| astral.config.config-source-of-truth | conforms | Task→slot map in `config.py`; no TASK_CONFIG `persist_in` |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring/threshold changes |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets/env literals |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src; Betty excluded |
| astral.layers.core-vs-external-bright-line | conforms | Core persist only; no external I/O |
| astral.layers.import-direction | conforms | Core→tracker/config; lazy import for cycle; data via `save_job_data` |
| astral.layers.ui-config-driven-business-logic | conforms | Config map only; no UI logic |
| astral.patterns.coat-check-never-store-empty | conforms | Blank id skips write; prior pointer preserved |
| astral.patterns.render-verdict-orchestrates-consult | conforms | No consult/`render_verdict` changes |
| astral.standards.data-raises-caller-logs | conforms | Data via existing save; core owns pin/debug |
| astral.standards.debug-contract-gated | conforms | Style D only when `debug=True` |
| astral.standards.dry-and-focused-functions | conforms | One helper + one map; extend existing persist |
| astral.standards.in-scope-only | conforms | Three pin slots + write path; AST-1100 excluded |
| astral.standards.logging-via-utils | conforms | `get_logger` / `debug_detail` |
| astral.standards.no-cross-contamination | conforms | Stays in core/utils |
| astral.standards.no-hardcoded-sets | conforms | Task keys/slots in config map |
| astral.standards.public-then-helpers | conforms | Pin helper beside existing artifact saves |
| astral.standards.utils-data-late-import-only | conforms | No new utils→data import |
| astral.state.core-decides-transitions | conforms | No state-machine transitions |
| astral.state.job-prior-states-enforced | conforms | No job state transition changes |
| astral.state.no-daisy-chain-in-run | conforms | Pin mid-chain under existing `run_next`; no new state daisy-chain |
| astral.ui.single-gunicorn-worker | conforms | No gunicorn/worker changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.agent.confidence-bounds, astral.agent.do-task-delegation, astral.agent.grade-vector-validation, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.git.betty-no-src-or-features, astral.layers.core-vs-external-bright-line, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.patterns.coat-check-never-store-empty, astral.patterns.render-verdict-orchestrates-consult, astral.standards.data-raises-caller-logs, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced, astral.state.no-daisy-chain-in-run, astral.ui.single-gunicorn-worker

**Excluded:**
- astral.debug.no-repo-root-artifacts-dir — paths match none of plan paths
- astral.debug.spikes-under-debug-dir — paths match none of plan paths
- astral.docs.features-single-file-per-ticket — layers {docs} ∩ plan {utils,core} empty
- astral.git.engineer-test-tree-ban — paths match none of plan paths
- astral.layers.scripts-exempt-from-layer-rules — layers {scripts} ∩ plan empty
- astral.patterns.require-auth-on-protected-endpoints — layers {ui} ∩ plan empty
- astral.standards.database-header-inventory — layers {data} ∩ plan empty
- astral.ui.frontend-file-placement — layers {ui} ∩ plan empty
- astral.ui.naming-conventions — layers {ui} ∩ plan empty

## Findings

None fix-now.

**discuss (non-blocking):** Stopping terminal `persist_job_artifact_from_parsed` for finalize hops intentionally changes `artifacts.cover_letter` (and stops `resume_content` body-copy from that path) to pointer-string semantics until AST-1100 remaps readers — already called out as Medium risk and blockedBy; not a definition mismatch.

**acceptable:** Self-assessment Single-Component / high / Medium matches plan; mid-chain pin-before-`run_next` is the critical correctness detail and is explicit.

**R6:** Definition fidelity pass (pointer-only, no `persist_in`, no UI). Layer/import pass. Config map in `config.py`. Coat-check + debug-gated pass. DRY pass. Sibling AST-1100 correctly excluded.

context_tokens≈48000

— Joan

#### ada — 2026-07-31T04:41:42.179Z
Plan published on `origin/sub/AST-1091/AST-1099-pin-agent-data-id` @ `2cc10e72`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1091/AST-1099-pin-agent-data-id/docs/features/artifacts/ast-1099-pin-agent-data-id.md

**Approach:** Config map `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` → tracker `pin_job_artifact_agent_data_id` (never store empty) → `do_task` pins after successful RESPONSE store **before** `run_next` (fixes mid-chain gap: `finalize_job_resume`→`draft_cover_letter`, `finalize_cover_letter`→`propose_application_responses`). Stops terminal body-copy for those finalize hops so `cover_letter` is not overwritten by a dict after the pointer string.

**Self-assessment**
- **Scope — Single-Component:** config map + tracker pin helper + `do_task` post-RESPONSE persist only.
- **Conf — high:** reuses `_store_response_block` id + `save_job_data` deep-merge; mid-chain gap is explicit in `agent_task.json` / terminal-only guard.
- **Risk — Medium:** `artifacts.cover_letter` becomes an `agent_data_id` string for chain-written jobs until AST-1100 remaps readers (blockedBy this ticket).

---

# AST-1099 — Pin agent_data_id on job artifact slots after chain hops

**Linear:** [AST-1099](https://linear.app/astralcareermatch/issue/AST-1099/pin-agent-data-id-on-job-artifact-slots-after-chain-hops-job-resume)

**Parent:** [AST-1091](https://linear.app/astralcareermatch/issue/AST-1091/job-resume-artifact-cover-letter-and-suggested-responses-is-not-saved) (AC reference only)

**Publish ref:** `origin/sub/AST-1091/AST-1099-pin-agent-data-id`

After a successful `finalize_job_resume` / `finalize_cover_letter` / `propose_application_responses` hop, core writes that hop's RESPONSE `agent_data_id` into `job_data.artifacts.job_resume` / `cover_letter` / `proposed_answers` — including mid-chain when `run_next` continues. Bodies stay in `agent_data`; this ticket pins pointers only. JAR/UI resolve is AST-1100.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add task_key → artifact slot map; extend `JOB_BUILD_ARTIFACT_CLEAR_KEYS` with pin slots | utils |
| `src/core/tracker.py` | Add `pin_job_artifact_agent_data_id` (non-empty id only; Style D found/recorded when `debug=True`) | core |
| `src/core/agent.py` | After successful RESPONSE store for the three task keys, call pin regardless of `run_next`; stop terminal body-copy via `persist_job_artifact_from_parsed` for `finalize_job_resume` / `finalize_cover_letter` | core |

**Out of scope (do not touch):**

| Item | Owner |
|------|--------|
| JAR / Materials Preview / API readers resolve pinned ids to bodies | AST-1100 |
| `JOBS_RECOMMENDED_ARTIFACT_TABS` `artifact_key` remaps | AST-1100 |
| TASK_CONFIG `persist_in` (or any new destination dialect) | excluded by parent |
| `save_prefix` grade / craft / `analysis_upshot` persists | excluded by parent |
| `tests/` / `docs/test-bible/**` | Betty |

## Stage 1: Config — pin map + cancel clear keys

**Done when:** `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` (exact name below) maps the three task keys to the three slot names; `JOB_BUILD_ARTIFACT_CLEAR_KEYS` includes the three pin slots so cancel does not leave stale pointers; `python3 -m py_compile src/utils/config.py` passes.

1. In `src/utils/config.py`, immediately after `JOB_BUILD_ARTIFACT_CLEAR_KEYS`, add:

```python
# AST-1099: do_task pins RESPONSE agent_data_id under job_data.artifacts[<slot>] (pointer only).
JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK = {
    "finalize_job_resume": "job_resume",
    "finalize_cover_letter": "cover_letter",
    "propose_application_responses": "proposed_answers",
}
```

2. Change `JOB_BUILD_ARTIFACT_CLEAR_KEYS` to include the pin slots while keeping the legacy body keys (manual PUT / older rows still clear on cancel):

```python
JOB_BUILD_ARTIFACT_CLEAR_KEYS = (
    "resume_content",
    "cover_letter",
    "application_responses",
    "job_resume",
    "proposed_answers",
)
```

⚠️ **Decision:** Slot names are exactly `job_resume` / `cover_letter` / `proposed_answers` per parent AC (not `resume_content` / `application_responses`). `cover_letter` becomes a pointer string under this epic; AST-1100 updates readers. Legacy body keys stay in the clear tuple so cancel still wipes old blobs.

## Stage 2: Tracker — pin helper (never store empty)

**Done when:** `pin_job_artifact_agent_data_id` merges a non-empty string id into `job_data.artifacts[slot]`; blank/None/whitespace id skips the write and does not clear a prior value; when `debug=True`, Style D detail logs recorded key+id or skip reason; when `debug=False`, no new debug-contract lines; `python3 -m py_compile src/core/tracker.py` passes.

1. In `src/core/tracker.py`, import `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` only if needed for validation — prefer validating the slot as a non-empty `str` at the call site; the helper accepts `(astral_job_id, artifact_key, agent_data_id, *, debug=False) -> bool` and returns `True` only when a write happened.
2. Implement `pin_job_artifact_agent_data_id` next to the other artifact save helpers (`save_job_artifact_cover_letter` / `persist_job_artifact_from_parsed`):
   - If `astral_job_id` is missing/blank → return `False` (optional debug skip reason `missing_job_id`).
   - If `artifact_key` is missing/blank → return `False` (skip reason `missing_artifact_key`).
   - Coerce `agent_data_id` with `str(...).strip()`; if empty → return `False` without calling `save_job_data` (skip reason `empty_agent_data_id`) — coat-check never-store-empty.
   - On success: `save_job_data(astral_job_id, {"artifacts": {artifact_key: agent_data_id}})` (deep merge; other artifact keys untouched).
   - When `debug=True`: `get_logger(__name__, debug_flag=True)` then `debug_detail` — recorded line `artifact_pin key=<artifact_key> agent_data_id=<id> recorded` or skip line `artifact_pin key=<artifact_key> skipped reason=<reason>`. No ungated `[DEBUG]` spam; no `logger.info("[DEBUG] …")`.
3. Do **not** rewrite `persist_job_artifact_from_parsed` body-merge helpers here — Stage 3 stops calling them for the pin task keys from `do_task`.

⚠️ **Decision:** Pointer value is the bare RESPONSE `agent_data_id` string (same id returned by `_store_response_block`), not a nested `{agent_data_id: …}` object — matches parent AC “equals that hop's RESPONSE `agent_data_id`”.

## Stage 3: Agent — pin after successful RESPONSE store (mid-chain and terminal)

**Done when:** On a successful hop for each of the three task keys, after a RESPONSE row is stored and its id is known, `job_data.artifacts[<slot>]` equals that id whether or not `run_next` continues; failed/empty id paths leave a prior good pointer untouched; terminal `persist_job_artifact_from_parsed` no longer body-copies for `finalize_job_resume` / `finalize_cover_letter`; `python3 -m py_compile src/core/agent.py` passes.

1. In `src/core/agent.py`, import `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` from `src.utils.config` (same import area as other config constants already used in this module).
2. Locate the success RESPONSE store block (~`if _should_store and raw_text:` that assigns `resp_id = _store_response_block(...)`). Immediately after a successful `resp_id` assignment (still inside the success path where `result` is the successful hop — not failure-audit stores earlier in `do_task`):
   - Resolve `slot = JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK.get(task_key)`.
   - If `slot` is set and `index` is truthy and `resp_id` is a non-empty string: lazy-import `pin_job_artifact_agent_data_id` from `src.core.tracker` (same cycle-break style as the existing `persist_job_artifact_from_parsed` lazy import) and call `pin_job_artifact_agent_data_id(index, slot, resp_id, debug=debug)`.
   - If `slot` is set but pin cannot run (no `index`, no `resp_id`, store exception left `resp_id` unset): when `debug=True`, log skip via the pin helper or a single `debug_detail` with reason (`missing_index` / `missing_resp_id` / `store_failed`) — do **not** call `save_job_data` with a blank id.
3. Placement must be **before** the `if not effective_next:` / `run_next` recurse branch so mid-chain pins fire. Repo `data/admin/agent_task.json` has `finalize_job_resume.run_next = draft_cover_letter` and `finalize_cover_letter.run_next = propose_application_responses` — those hops never enter the current terminal-only body persist.
4. In the terminal block that calls `persist_job_artifact_from_parsed` when `not effective_next`, **remove** the `finalize_job_resume` / `finalize_cover_letter` body-copy path (delete or hard-disable `allow_resume` / `allow_cover` for those keys). Pointer pin from step 2 is the sole write for those hops. Leave `persist_job_artifact_from_parsed` and the PUT helpers intact for manual API / other callers.
5. Do not pin on failure RESPONSE stores (schema/API failure paths that call `_store_response_block` then return `success=False`).
6. Do not add TASK_CONFIG fields. Do not edit UI/API files.

⚠️ **Decision:** Stop `do_task` body-copy for the two finalize hops so `artifacts.cover_letter` is not overwritten by a dict after a pointer string pin (same key). `resume_content` body writes from that terminal path are also stopped for `finalize_job_resume`; the authoritative resume pointer is `job_resume`. Manual `PUT …/artifacts/resume_content` remains for editors until AST-1100 remaps surfaces.

## Self-Assessment

**Scope — `Single-Component`**  
Touches config map + tracker pin helper + `do_task` post-RESPONSE persist; no UI, no schema, no TASK_CONFIG dialect.

**Conf — `high`**  
Reuses existing `_store_response_block` id + `save_job_data` deep-merge artifacts pattern; mid-chain gap is explicit in `agent_task.json` `run_next` and the terminal-only `persist_job_artifact_from_parsed` guard.

**Risk — `Medium`**  
`artifacts.cover_letter` type changes from object to `agent_data_id` string for chain-written jobs — JAR/readers stay broken until AST-1100, which is intentional and blockedBy this ticket. A bad pin (wrong id / skipped mid-chain) leaves UAT surfaces empty.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Status |
|------|--------|
| §1.3 DRY | One pin helper; one config map; no parallel persist framework |
| §1.5.1 debug-contract-gated | Style D only when `debug=True`; no new ungated `[DEBUG]` |
| §2.1 config | Slot/task map in `config.py`; no TASK_CONFIG `persist_in` |
| §2.4.1 entity-agent-responses-latest-only | Pin by RESPONSE `agent_data_id`; body stays in `agent_data`; no entity JSON `agent_responses` revival |
| §2.8 coat-check-never-store-empty | Blank id skips write; prior pointer preserved |
| §3.3 imports | Core → tracker/config; lazy import breaks agent↔tracker cycle |

No conflicts requiring `conf-!!-NONE`.

---

## Review

**Branch:** `sub/AST-1091/AST-1099-pin-agent-data-id`  
**Commit (code):** `76928f73`  
**Publish tip reviewed:** `fe09931b` (`merge-tests(AST-1099)`)

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1099  
**Overall:** DISCUSS

### What’s solid
- Config map + clear-key extension match Stage 1 exactly; pointer-only slots.
- `pin_job_artifact_agent_data_id` coat-checks empty/blank ids; Style D `debug_detail` only when `debug=True`.
- `do_task` pins after successful RESPONSE store and **before** `run_next`; terminal `persist_job_artifact_from_parsed` body-copy removed for finalize hops.
- Lazy tracker import keeps the documented agent↔tracker cycle break.
- Betty one-SHA `merge-tests` + component coverage for map / helper / mid-chain pins.

### Issues
**discuss (C4 straggler):** Joan excluded `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, and `astral.debug.spikes-under-debug-dir` at plan time; ticket-scoped diff makes them in-scope. All three **conform** on the code (single features file; Betty owns tests; plan under `docs/features/`). No product fix required.

### Recommended actions
- Engineer: no fix-now. On resolve-child, acknowledge stragglers / move to User Testing if no product disagreement.
- AST-1100 remains the reader/remap sibling (intentional pointer-string gap on UAT surfaces).

### Notes
- Formal `origin/dev...origin/sub/...` three-dot is epic-ancestry polluted (multiple merge bases). Statute applies_when + product judgment used **AST-1099 commit change set** (`2cc10e72` / `76928f73` / `449c61cc` / `fe09931b`).
- Plan-rubric verdict attached (Joan APPROVED).

context_tokens≈42000

— Radia

---

## Resolution

**Date:** 2026-07-31  
**Outcome:** clean — no product fix-now

- **discuss (C4 straggler):** Closed without code change. Radia confirmed the three Joan-excluded statutes **conform** on the tip (`astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.debug.spikes-under-debug-dir`). No disagreement; no product edit.
- **advisory (pointer-string until AST-1100):** Left as planned Medium risk; sibling AST-1100 owns reader remap.

---

## Bug: AST-1428 — Copy job resume onto job blob, keep pin

Parent mini-bug: [AST-1422](https://linear.app/astralcareermatch/issue/AST-1422/finalize-job-resume-isnt-getting-parsed-into-the-job-resume-renderer) / child [AST-1428](https://linear.app/astralcareermatch/issue/AST-1428/copy-job-resume-onto-job-blob-keep-pin-finalize-job-resume-isnt). Approved ancestor: AST-1099 (archived — this file). Binding product contract (Susan): copy the resume from the original `agent_data` RESPONSE onto the job as an editable blob; pin persists; `agent_data` is never edited; do not replace `artifacts.job_resume` with a dict on save.

Original AST-1099 Stages 1–3 stay: pin map, `pin_job_artifact_agent_data_id`, pin after RESPONSE store before `run_next`. This bug walks back only Stage 3's "stop `resume_content` body writes from the terminal path" for `finalize_job_resume` — pin stays; a sibling blob is copied. Cover letter / `proposed_answers` are out of scope.

### As-is

After a successful `finalize_job_resume` hop, `job_data.artifacts.job_resume` is the RESPONSE `agent_data_id` string (pin works). That `agent_data` row has a full `agent_payload.resume`. There is no editable resume blob on the job (`artifacts.resume_content` absent). `artifacts.deviations` was copied. JAR Job Resume fields are blank. Preview/Print is contact-only (no title/sections). AST-1100 `PUT /api/jobs/<id>/artifacts/job_resume` writes a dict onto the pin slot, replacing the id.

### To-be

On successful `finalize_job_resume`, copy the unwrapped `agent_payload.resume` onto the job as `artifacts.resume_content` (sibling of the pin). Keep `artifacts.job_resume` as the RESPONSE id. JAR Job Resume fields and Print/preview read that blob (unwrapped sections). Later editor saves write `resume_content` only. Never update `agent_data`. Never replace the pin string with a dict.

### Repro

Fixture (file/JSON persist — not a SQL row). After `finalize_job_resume` success:

```json
{
  "job_data": {
    "artifacts": {
      "job_resume": "<RESPONSE agent_data_id>",
      "deviations": ["…"]
    }
  }
}
```

Pinned `agent_data.block_data` (same id) is hop JSON whose parsed form has `agent_payload.resume` with section keys (`title`, `professional_summary`, `experience`, …). `artifacts.resume_content` is missing. GET `/api/jobs/<id>` hydrates `artifacts.job_resume` to the `agent_payload` envelope (nested `resume`), so ArtifactEditor `use_resume_structure` looks up section ids at the top level and renders blanks. `build_resume_from_job` has no `resume_content`; pin resolve returns the envelope dict; Print emits contact from candidate snapshot and no job title/sections.

### Root cause

AST-1099 Stage 3 removed `do_task`'s terminal `persist_job_artifact_from_parsed` for `finalize_job_resume` so the pin string would not be overwritten. That also stopped the sibling `resume_content` copy. The pin is the hop envelope id; JAR/Print readers expect a flat section dict. AST-1100 then remapped the Job Resume tab to `artifact_key: "job_resume"` and shipped `PUT …/artifacts/job_resume` as "body dict replaces pin", which is the opposite of the keep-pin contract.

### Proposed change

Sibling blob key is existing `artifacts.resume_content` (not a new slot; not stuffed into `job_resume`). Do **not** re-enable `persist_job_artifact_from_parsed` for finalize hops (that helper also writes `cover_letter` as a dict and would clobber the cover pin).

**1. Copy after pin — `src/core/agent.py` `do_task`**

Immediately after a successful `pin_job_artifact_agent_data_id` for `task_key == "finalize_job_resume"` (same success path: `result.success`, `index` set, `resp_id` stored — **before** `run_next`, so mid-chain hops copy too):

- Lazy-import a tracker helper (same agent↔tracker cycle break as the pin / deviations calls).
- Call it with `index` and the in-memory `parsed` hop JSON already used for `_store_response_block`. Do not re-read `agent_data` to copy. Do not write `agent_data`.
- Best-effort: log and continue if copy raises (mirror `persist_draft_job_resume_deviations`). Pin already recorded; a copy failure must not blank the pin.

**2. Copy helper — `src/core/tracker.py`**

Add `persist_finalize_job_resume_content(astral_job_id, parsed) -> bool` next to `persist_draft_job_resume_deviations` / `save_job_artifact_resume_content`:

- If `parsed_matches_job_resume_content(astral_job_id, parsed)` is false → return `False` without `save_job_data` (coat-check: never store empty; do not clear a prior blob).
- Else `body = _resume_payload_body(parsed)` (already unwraps `agent_payload.resume` then flat section keys; skips nest/metadata keys via `TASK_CONFIG["draft_job_resume"]`).
- `save_job_artifact_resume_content(astral_job_id, body)` — existing prepare filters to candidate structure and snapshots contact. Deep-merge writes only `artifacts.resume_content`; `job_resume` pin untouched.
- Return `True` when a write happened.

**3. GET overlay — `hydrate_job_artifacts_for_display`**

Keep `_JOB_ARTIFACT_PIN_KEYS` iteration. For `job_resume` only (not cover / proposed_answers):

- If `artifacts.resume_content` is a nonempty dict, set in-memory `out["job_resume"]` to that dict (display overlay; disk pin unchanged).
- Else resolve the pin via `resolve_job_artifact_agent_data_body`, then `out["job_resume"] = _resume_payload_body(body)` when that yields a nonempty section dict. (`resolve` already unwraps stored JSON to `agent_payload`; `_resume_payload_body` then unwraps `.resume`. This fills JAR for already-finalized pin-only jobs without regenerate and without persist-on-GET.)
- Do not persist the overlay. Do not write `agent_data`.

**4. Editor save — `src/ui/api/api_jobs.py` `put_job_resume_pin_key`**

`PUT /api/jobs/<id>/artifacts/job_resume` stays the ArtifactEditor URL (`JOBS_RECOMMENDED_ARTIFACT_TABS` `artifact_key` remains `"job_resume"` — do not remap the tab). Change the handler: require `job_resume` dict body as today; call `save_job_artifact_resume_content(astral_job_id, body)` instead of `save_job_data(… {"job_resume": body})`. Never assign a dict to `artifacts.job_resume`. Pin string stays. Existing `PUT …/artifacts/resume_content` is unchanged.

**5. Print — `src/core/builder.py` `_resolve_resume_sections`**

Keep prefer-`resume_content` first. When falling back to a string pin, unwrap with `_resume_payload_body(resolve_job_artifact_agent_data_body(pin))` and use that section dict when nonempty. Do not treat the hop envelope as resume sections. Leave the legacy `pin` dict branch (pre-fix PUT clobber) as a last resort before `base_resume`.

Do not edit `agent_data`. Do not copy full hop JSON into `artifacts.job_resume`. Do not change cover-letter / `proposed_answers` pin, hydrate, or PUT.

### Blast radius

- AST-1099 tests that assert finalize hops do not body-copy into `resume_content` / do not call `persist_job_artifact_from_parsed` — Betty; this ticket restores a sibling copy without reviving that helper for finalize hops.
- AST-1100 tests that `PUT …/job_resume` replaces the pin string with a dict — those must flip: pin remains a string; blob lands in `resume_content`.
- `consult._run_cover_letter_for_job` resume-first gate already keys on `resume_content`; a successful copy makes that standalone path see a blob (main chain still uses `run_next` and is unchanged).
- JAR Job Resume tab still reads `artifacts.job_resume` from GET (hydrated overlay). Cover / application tabs unchanged.
- Cancel still clears both `resume_content` and `job_resume` via `JOB_BUILD_ARTIFACT_CLEAR_KEYS`.
- `_prepare_job_resume_content` contact snapshot from candidate `base_resume` still runs on copy/save.

### What must still hold

- After successful `finalize_job_resume` (mid-chain or terminal), `artifacts.job_resume` **equals** that hop's RESPONSE `agent_data_id` string (AST-1099 AC1). Failed/empty hops do not blank a good prior pin.
- Pin helper never-store-empty; Style D debug only when `debug=True`.
- `agent_data` RESPONSE rows are the content store for the pin; this ticket copies onto the job and never updates those rows.
- Do not copy full hop JSON into the pin slot.
- `artifacts.cover_letter` / `proposed_answers` pin semantics unchanged; this copy path must not write those keys.
- Manual `PUT …/artifacts/resume_content` still merges the section dict into the sibling blob only.
- Config pin map `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` unchanged.

## Joan validate (fix-board AST-1428)

[board-joan] CANON: OK

**Question:** Does the Proposed change conflict with or require updating `canon/statutes/**` or `canon/patterns/**`?

Statutes skimmed (`astral.agent.do-task-delegation`, `astral.idioms.coat-check-never-store-empty`, `astral.batch.entity-agent-responses-latest-only`, `astral.dispatch.run-next-is-chain-authority`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.data-raises-caller-logs`, `astral.standards.dry-and-focused-functions`, `astral.standards.in-scope-only`, `astral.standards.logging-via-utils`, `astral.standards.no-cross-contamination`, `astral.state.no-daisy-chain-in-run`): conforms. `pattern.batch.entity-agent-responses`: conforms (pin stays a pointer; `resume_content` is the pre-existing job blob). No canon file needs updating. Dual pin + sibling blob is not a new Archie precedent.

## Radia review (review-fix AST-1428)

[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1428
**Publish ref:** `origin/sub/AST-1422/AST-1428-copy-job-resume-blob-keep-pin` @ `da1b045b`
**Diff base:** `origin/ftr/AST-1422-finalize-job-resume-not-parsed...origin/sub/AST-1422/AST-1428-copy-job-resume-blob-keep-pin`
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | Betty `merge-tests(AST-1430)` one SHA on merged test tip |
| orch.git.commit-vocabulary | universal | conforms | `code` / `test` / `merge-tests` / `merge-child` / `docs` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | Forward publish on `origin/sub/...` only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1422/AST-1428-...` stacked on live `ftr` |
| orch.git.merge-on-checkout | universal | conforms | `merge-child(AST-1430)` integration; no illegal pull-merge subjects on product tip |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | None in AST-1428 history |
| orch.git.no-dev-agent-branches | universal | conforms | Fix sub only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Reviewed in `astral-AST-1422` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Implements Susan keep-pin + sibling-blob contract from plan |
| orch.pipeline.plan-is-bible | universal | conforms | All five proposed-change items landed |
| orch.pipeline.project-scoped-queues | universal | conforms | Single bug ticket |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Entered from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Tests/bible from AST-1430 merge; engineer `code` commit is `src/` only |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Ada remains assignee |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | No assignee change by this review |
| orch.roles.pre-commit-path-bans | universal | conforms | Doc-only Radia commit expected on sub; engineer stayed on product paths |
| astral.agent.confidence-bounds | scoped | not-applicable | no graded-confidence path in diff |
| astral.agent.do-task-delegation | scoped | conforms | Copy extends post-RESPONSE persist inside `do_task`; no bypass |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade-vector changes |
| astral.batch.batch-id-first | scoped | not-applicable | no claim/batch API signature changes |
| astral.batch.batch-id-format | scoped | not-applicable | no `batch_id` format changes |
| astral.batch.claim-process-release | scoped | not-applicable | no claim/release changes |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | `job_resume` stays RESPONSE id string; body copied to `resume_content` only |
| astral.config.config-source-of-truth | scoped | not-applicable | `src/utils/config.py` not in diff |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets/env literals |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no `artifacts/**` spike paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | plan patch under `docs/features/` only |
| astral.dispatch.run-next-is-chain-authority | scoped | conforms | Copy fires after pin and before `run_next` recurse |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch seed paths |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Plan-fix patch appended to existing `ast-1099-…` file |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits are tests/bible; engineer owns `src/` |
| astral.git.engineer-test-tree-ban | scoped | conforms | `code(AST-1428)` touches `src/` only |
| astral.idioms.coat-check-never-store-empty | scoped | conforms | `parsed_matches_job_resume_content` gate; hydrate/builder skip empty |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult/`render_verdict` paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | `put_job_resume_pin_key` retains `@require_auth` |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Core persist + display overlay; no external I/O |
| astral.layers.import-direction | scoped | conforms | Lazy tracker imports in `agent.py`; builder uses `tracker_mod` |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no `scripts/**` |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | API handler delegates to tracker helper; no business logic in UI |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no `data/admin/**` |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed/catalog paths |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | hot-path `do_task` only; seed statutes N/A |
| astral.seed.define-approved | scoped | not-applicable | no seed define paths |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no seed operator paths |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no seed coverage paths |
| astral.standards.database-header-inventory | scoped | not-applicable | no `src/data/**` |
| astral.standards.data-raises-caller-logs | scoped | conforms | `save_job_data` via existing helpers; core owns copy error log |
| astral.standards.debug-contract-gated | scoped | conforms | No new ungated `[DEBUG]`; pin debug path unchanged |
| astral.standards.dry-and-focused-functions | scoped | conforms | One `persist_finalize_job_resume_content` helper; reuses `_resume_payload_body` / `save_job_artifact_resume_content` |
| astral.standards.in-scope-only | scoped | conforms | Resume sibling blob + keep-pin only; cover/proposed_answers untouched |
| astral.standards.logging-via-utils | scoped | conforms | `logger.error` on copy failure mirrors deviations path |
| astral.standards.names-not-ticket-ids | scoped | conforms | Ticket ids in comments only |
| astral.standards.no-cross-contamination | scoped | conforms | Stays in core/tracker/builder + thin API |
| astral.standards.no-hardcoded-sets | scoped | conforms | No new task/slot literals outside existing config map |
| astral.standards.public-then-helpers | scoped | conforms | Helper beside deviations/resume save helpers |
| astral.standards.utils-data-late-import-only | scoped | conforms | No new utils→data import |
| astral.state.core-decides-transitions | scoped | not-applicable | no state-machine transition edits |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job prior-state edits |
| astral.state.no-daisy-chain-in-run | scoped | conforms | Mid-chain copy under existing `run_next`; no new daisy-chain |
| astral.ui.frontend-file-placement | scoped | not-applicable | no `src/ui/frontend/**` |
| astral.ui.naming-conventions | scoped | not-applicable | no frontend component changes |
| astral.ui.single-gunicorn-worker | scoped | conforms | API touch is handler-only; no worker config |

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.batch.entity-agent-responses | conforms | Pin remains RESPONSE id pointer; `resume_content` is pre-existing job blob sibling, not entity-row mirror |

## Plan adherence

All five plan-fix items are implemented on the isolated fix diff:

1. **`do_task` copy after pin** (`src/core/agent.py`) — lazy-import `persist_finalize_job_resume_content` on `finalize_job_resume` success, before `run_next`; best-effort `logger.error` on failure (matches deviations pattern).
2. **Tracker helper** (`persist_finalize_job_resume_content`) — coat-check via `parsed_matches_job_resume_content`, unwrap via `_resume_payload_body`, write via `save_job_artifact_resume_content` (pin slot untouched).
3. **GET overlay** (`hydrate_job_artifacts_for_display`) — prefers nonempty `resume_content` for `job_resume` display; else resolves pin and unwraps `.resume` for section ids.
4. **Editor save** (`put_job_resume_pin_key`) — routes body to `save_job_artifact_resume_content`; no dict onto `artifacts.job_resume`.
5. **Print** (`_resolve_resume_sections`) — pin fallback unwraps via `_resume_payload_body(resolve…)`; legacy dict pin branch retained.

`persist_job_artifact_from_parsed` not revived. `agent_data` not written. Config pin map unchanged. Cover / `proposed_answers` paths untouched.

## Fix-specific checks

**[bug-repro]:** OK  
Sibling AST-1430 repro merged on tip (`ee5f867c` / `merge-child`):

- `TestAst1430DoTaskResumeContentCopy::test_finalize_copies_resume_content_keeps_pin` — asserts copy helper invoked after pin with concrete parsed `professional_summary`; would fail pre-fix (no copy call). Mocks helper (wiring bar, not end-to-end `resume_content` persist).
- `TestAst1100JobArtifactPinResolveApi::test_put_job_resume_writes_resume_content_keeps_pin` — asserts `save_job_artifact_resume_content` receives edited dict and `save_job_data` never writes a dict onto the pin; would fail pre-fix AST-1100 clobber behavior.

**## What must still hold:** OK

| Item | Verdict |
|------|---------|
| Pin = RESPONSE `agent_data_id` after successful `finalize_job_resume` | Pin path unchanged; copy writes `resume_content` only |
| Failed/empty hops do not blank prior pin | Copy gated on `result.success` + `resp_id`; helper coat-checks |
| Pin never-store-empty; Style D when `debug=True` | `pin_job_artifact_agent_data_id` untouched |
| `agent_data` never updated | Copy uses in-memory `parsed`; hydrate overlay is read-only |
| No full hop JSON in pin slot | `_resume_payload_body` strips envelope; pin slot not written by copy/save |
| `cover_letter` / `proposed_answers` unchanged | Only `finalize_job_resume` triggers copy |
| `PUT …/resume_content` unchanged | Separate route intact |
| `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` unchanged | No `config.py` diff |

## Findings

**advisory:** `TestAst1430DoTaskResumeContentCopy` mocks `persist_finalize_job_resume_content` — locks wiring, not that `artifacts.resume_content` is populated. Helper is thin glue over existing `_resume_payload_body` / `save_job_artifact_resume_content` coverage; acceptable for this tip but hydrate overlay + envelope unwrap paths (plan items 3 & 5) lack dedicated repro tests.

**advisory:** `[bug-repro]` marker is in the Betty commit subject, not the test class first line/docstring; bible cites `TestAst1430…` by name. Hygiene only.

## What’s solid

- Dual contract (pin pointer + sibling editable blob) matches Susan’s binding product language in the plan patch.
- Hydrate overlay fixes pin-only legacy jobs for JAR without persist-on-GET.
- PUT keep-pin directly reverses AST-1100 clobber regression.
- Engineer product commit is tightly scoped to four `src/` files; Betty gap landed via AST-1430 merge.

## Frame diff

Product delta is `origin/ftr/AST-1422-finalize-job-resume-not-parsed...origin/sub/AST-1422/AST-1428-copy-job-resume-blob-keep-pin` (9 files, +278/−22). Parent AST-1422 is a live mini-parent with `ftr` (not Done/orphaned intake shape).

## Recommended actions — Chuckles

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (clean, C7 complete) | Normal (live `ftr`, not orphaned Done) | → **Review Posted** → `do-all-the-things` §3h clean-review shortcut → **User Testing** directly (`resolve-child` skipped) |

context_tokens≈52000

[code-rubric] PROCEED (Commit: da1b045b) keep-pin resume blob copy

## Radia review (review-fix AST-1430)

[code-rubric] revision=2
**Rubric:** code-rubric.v2
**Ticket:** AST-1430
**Publish ref:** `origin/sub/AST-1422/AST-1430-test-gap-resume-content-copy-put-pin` @ `8d35b2ae`
**Reviewed delivery:** `ee5f867c` (`test(AST-1430): bug-repro`) + `c5dd7b40` (`merge-tests(AST-1430)`)
**Diff base:** `origin/ftr/AST-1422-finalize-job-resume-not-parsed...origin/sub/AST-1422/AST-1430-test-gap-resume-content-copy-put-pin` — **empty** (sub tip = ftr tip; tests rolled in via `merge-child` → AST-1428 → ftr)
**Overall:** DISCUSS

## Statutes checked

Reviewed change set = `ee5f867c` (4 files, +132/−12). Diff layers: `docs` only.

| id | tier | verdict | one-line |
|----|------|---------|----------|
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1430)` @ `c5dd7b40` → `ee5f867c` |
| orch.git.commit-vocabulary | universal | conforms | `test` / `merge-tests` vocabulary on gap sub |
| orch.git.flow-direction-inviolable | universal | conforms | Forward publish on `origin/sub/...` only |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-1422/AST-1430-...` gap sibling on live `ftr` |
| orch.git.merge-on-checkout | universal | conforms | `merge-child(AST-1430)` onto AST-1428 for test-fix; no illegal subjects |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | None in AST-1430 history |
| orch.git.no-dev-agent-branches | universal | conforms | Gap sub only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Reviewed in `astral-AST-1422` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Test-only gap; product contract unchanged |
| orch.pipeline.plan-is-bible | universal | conforms | Board REVISE items addressed in delivery commit |
| orch.pipeline.project-scoped-queues | universal | conforms | Single gap ticket |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Entered from Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute edits |
| orch.roles.betty-owns-test-tree | universal | conforms | `ee5f867c` is tests + bible only |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Ada remains assignee |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | No assignee change by this review |
| orch.roles.pre-commit-path-bans | universal | conforms | Doc-only Radia commit expected; Betty stayed on tests/bible |
| astral.agent.confidence-bounds | scoped | not-applicable | no `src/core/**` in delivery |
| astral.agent.do-task-delegation | scoped | not-applicable | no product paths in delivery |
| astral.agent.grade-vector-validation | scoped | not-applicable | no product paths |
| astral.batch.batch-id-first | scoped | not-applicable | no batch API paths |
| astral.batch.batch-id-format | scoped | not-applicable | no batch API paths |
| astral.batch.claim-process-release | scoped | not-applicable | no batch API paths |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no product paths (reinforced by tests) |
| astral.config.config-source-of-truth | scoped | not-applicable | no `src/utils/config.py` |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets/env |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no spike paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | bible-only diff |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no product paths |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no seed paths |
| astral.docs.features-single-file-per-ticket | scoped | not-applicable | no `docs/features/**` in delivery |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commit is tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | No `src/` edits in `ee5f867c` |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no product paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no `src/ui/**` in delivery |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | no product paths |
| astral.layers.import-direction | scoped | not-applicable | no product paths |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no `scripts/**` |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | no product paths |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed paths |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed paths |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no seed paths |
| astral.seed.define-approved | scoped | not-applicable | no seed paths |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no seed paths |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no seed paths |
| astral.standards.database-header-inventory | scoped | not-applicable | no `src/data/**` |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no product paths |
| astral.standards.debug-contract-gated | scoped | not-applicable | no product paths |
| astral.standards.dry-and-focused-functions | scoped | not-applicable | no product paths |
| astral.standards.in-scope-only | scoped | conforms | Gap scoped to board-flagged bible rows + two repro paths |
| astral.standards.logging-via-utils | scoped | not-applicable | no product paths |
| astral.standards.names-not-ticket-ids | scoped | conforms | Ticket ids in comments/class names only |
| astral.standards.no-cross-contamination | scoped | not-applicable | no product paths |
| astral.standards.no-hardcoded-sets | scoped | not-applicable | no product paths |
| astral.standards.public-then-helpers | scoped | not-applicable | no product paths |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no product paths |
| astral.state.core-decides-transitions | scoped | not-applicable | no state paths |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no state paths |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no product paths |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend paths |
| astral.ui.naming-conventions | scoped | not-applicable | no frontend paths |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no worker config |

## Pattern conformance

`none cited` — gap ticket; board REVISE did not cite catalog patterns.

## Plan adherence (board REVISE + AST-1428 blast radius)

**Board source (`[board-betty] TESTS: REVISE`):**
1. Broken `TestAst1100JobArtifactPinResolveApi::test_put_job_resume_writes_body_dict` (dict onto pin) — **fixed** → `test_put_job_resume_writes_resume_content_keeps_pin` asserts `save_job_artifact_resume_content` called and `save_job_data` never writes pin dict.
2. Missing sibling `resume_content` copy after finalize pin (`docs/test-bible/core/agent.md` AST-1099) — **addressed** → `TestAst1430DoTaskResumeContentCopy` + bible § AST-1430; `TestAst1099DoTaskArtifactPin` gets isolation mock for new helper.

**Bible (`ee5f867c`):**
- `docs/test-bible/core/agent.md` § AST-1430 — manifest lines match landed tests; AST-1099 broken/obsolete row revised (pin suite still asserts `persist_job_artifact_from_parsed` unused).
- `docs/test-bible/ui/api/api_jobs.md` § AST-1430 — PUT keep-pin manifest honest; obsolete `test_put_job_resume_writes_body_dict` called out.

**AST-1428 blast radius (test half):** Delivery does not revive `persist_job_artifact_from_parsed` for finalize hops; AST-1099 pin suite preserved with helper swallow mock.

**Not in gap delivery (product AST-1428 owns):** hydrate overlay + builder envelope-unwrap repro tests — acceptable deferral; product paths reviewed on AST-1428.

## Fix-specific checks

**[bug-repro]:** DISCUSS

Betty Linear (`[bug-repro]` @ `c5dd7b40` · "repro lands red, awaits fix"):

| Test | Pre-fix fail? | To-be tie-in | Verdict |
|------|---------------|--------------|---------|
| `TestAst1100JobArtifactPinResolveApi::test_put_job_resume_writes_resume_content_keeps_pin` | Yes — pre-AST-1428 handler wrote dict onto `artifacts.job_resume` | Concrete blob `{"professional_summary": "Edited"}` via `save_job_artifact_resume_content`; `pin_writes == []` with seed `job_resume: "pin-keep"` | **OK** — substantive keep-pin repro |
| `TestAst1430DoTaskResumeContentCopy::test_finalize_copies_resume_content_keeps_pin` | Yes — pre-AST-1428 no `persist_finalize_job_resume_content` call | Asserts pin called (`job-1430`, `job_resume`, nonempty id); `persist_copy` once with parsed `professional_summary == "Summary"`; `persist_parsed` not called | **Partial** — mocks `persist_finalize_job_resume_content`; locks call-order wiring only, does not assert `artifacts.resume_content` populated on job (primary ## Repro symptom). Would pass if helper were broken no-op. |

**Hygiene:** `[bug-repro]` tag appears in Betty Linear comment and commit subject, not on test class/method first line (bible cites `TestAst1430…` by name).

**## What must still hold (AST-1428 §, product on same tree):** OK

Tests reinforce, do not undermine, the seven keep-pin contract items:

| Item | Test impact |
|------|-------------|
| Pin = RESPONSE id after finalize | `TestAst1430` asserts pin called with nonempty id before copy |
| Failed hops do not blank pin | Unchanged AST-1099 failure paths |
| Pin never-store-empty | No pin-helper edits |
| `agent_data` never updated | Tests mock storage; no agent_data writes asserted |
| No hop JSON in pin slot | PUT repro blocks dict-on-pin; copy test asserts `persist_parsed` not called |
| cover/proposed_answers unchanged | Only `finalize_job_resume` path touched in new suite |
| `PUT …/resume_content` unchanged | Not modified |
| Config pin map unchanged | No config tests altered |

`TestAst1099DoTaskArtifactPin` isolation mock prevents new copy path from breaking pin-only assertions.

## Findings

**discuss:** `[bug-repro]` copy path is wiring-only — `TestAst1430DoTaskResumeContentCopy` mocks `persist_finalize_job_resume_content` instead of asserting `job_data.artifacts.resume_content` receives unwrapped section dict after a real helper call. PUT keep-pin repro is strong; together they satisfy Betty's repro-first gate at merge time, but the gap ticket that owns `[bug-repro]` leaves the ## Repro table's missing-`resume_content` symptom unlocked at integration depth. Consider one tracker-level or unmocked `do_task` assertion in a follow-up (resolve-child or Betty pass) — not merge-blocking given thin helper composition and AST-1428 product review.

**advisory:** No `[bug-repro]` first-line source tag on the test method/class (machinery expects qa-fix handoff tag). Bible + commit subject carry intent.

**advisory:** Unique `ftr...sub` three-dot is empty — expected docs-acceptance shape; delivery reviewed at `ee5f867c`.

## What’s solid

- Board's broken PUT test flipped correctly; seed includes existing pin string.
- AST-1099 pin suite stays isolated via `persist_finalize` swallow mock.
- Bible manifest lines are cross-linked and runnable per § AST-1430.
- `merge-tests(AST-1430)` one-SHA discipline on `c5dd7b40`.
- Delivery already on `ftr` with AST-1428 product; no product regression against ## What must still hold.

## Frame diff

Unique range `origin/ftr/AST-1422-finalize-job-resume-not-parsed...origin/sub/AST-1422/AST-1430-test-gap-resume-content-copy-put-pin` is **empty** (both @ `8d35b2ae`). Reviewed artifact = test-gap delivery `ee5f867c` (+ `c5dd7b40`), integrated via `merge-child(AST-1430)` → AST-1428 → ftr.

## Recommended actions — Chuckles

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **REVIEW** (discuss repro depth, C7 complete) | Normal (live `ftr`, not orphaned Done) | → **Review Posted** → `resolve-child` (optional: tracker/integration `[bug-repro]` depth) → **User Testing** |

context_tokens≈38000

[code-rubric] REVIEW (Commit: 8d35b2ae) gap repro wiring-only

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/cb028d939d41dfcd8e478a8c8ee91601/4a0092bc-fdf3-47f6-8865-307221a318f2/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/6756c75f-4c53-4e2b-855b-38d80ad347c8/store.db` |
| Radia | review | `/home/susan/.cursor/chats/cb028d939d41dfcd8e478a8c8ee91601/28e31dc0-4096-4933-950e-8a814e0d5963/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1547 (parent) | ftr/AST-1547-job-resume-content-not-saving |
| AST-1548 | sub/AST-1547/AST-1548-fix-job-resume-body-replica |
| AST-1554 | sub/AST-1547/AST-1554-gap-job-resume-body-replica-tests |

**Epic worktree:** `astral-AST-1547/` — one active sub checked out at a time.

## Bug: AST-1548 — Job resume/cover letter body replica on job (not agent_data pin)

Parent mini-epic: [AST-1547](https://linear.app/astralcareermatch/issue/AST-1547/job-resume-content-is-not-saving-to-the-job-record) (orphaned Bug — own `ftr`). Child: [AST-1548](https://linear.app/astralcareermatch/issue/AST-1548/fix-job-resumecover-letter-body-replica-on-job-not-agent-data-pin). Approved ancestor: AST-1099 (this file). Binding product contract (Susan / AST-1547): `job_data.artifacts.*` for finalize hops **begins as a replica** of the hop response body on the job (same pattern as `candidate.artifacts.base_resume`); operator surfaces read/edit the **job** body only; `agent_data` RESPONSE stays pristine and is never updated by human edits.

Original AST-1099 Stages 1–3 stay as history (pin map + pin helper + pin after RESPONSE). AST-1428 / AST-1430 kept the pin on `job_resume` and copied a sibling `resume_content` blob with hydrate overlay + pin-resolve fallbacks. **This bug walks that pointer-as-operator-store contract back** for `job_resume` and `cover_letter` only: those slots hold the editable body; pin-resolve is not an operator display/edit path. `proposed_answers` pin semantics are unchanged.

### As-is

After successful `finalize_job_resume` / `finalize_cover_letter`, core still drives `pin_job_artifact_agent_data_id` so `job_data.artifacts.job_resume` / `cover_letter` are RESPONSE `agent_data_id` strings (pointer-only on the operator slots). AST-1428 also copies unwrapped resume sections onto sibling `artifacts.resume_content`; hydrate overlays that sibling onto `job_resume` for JAR, and still falls back to `resolve_job_artifact_agent_data_body` when the sibling is missing. Cover letter hydrate / Print still pin-resolve via `cover_letter_artifact_for_display` / builder. Operator Save for the Job Resume tab writes `resume_content` while the pin string remains on `job_resume`. Edits never land as the durable body on the same keys operators treat as the artifact; pin-resolve keeps `agent_data` in the read path.

### To-be

On successful finalize hops, each matching operator slot **begins as a replica** of the parsed hop body on the job record (`artifacts.job_resume` / `artifacts.cover_letter` are content dicts, parallel to `candidate.artifacts.base_resume`). `agent_data` RESPONSE rows stay the unaltered hop store and are **not** updated by later human edits. Hydrate / JAR / Print / editor load for those two artifacts use **job content only** — no `resolve_job_artifact_agent_data_body` (or cover helper pin-resolve) for operator display/edit. Editor Save writes the edited body back onto the job artifact key; never into `agent_data`. Coat-check skips empty replicas; cancel/clear still wipes the job body keys operators use.

### Repro

Fixture (file/JSON persist — not a SQL row). After `finalize_job_resume` + `finalize_cover_letter` success on current tip:

```json
{
  "job_data": {
    "artifacts": {
      "job_resume": "<RESPONSE agent_data_id string>",
      "resume_content": { "title": "…", "professional_summary": "…", "experience": [] },
      "cover_letter": "<RESPONSE agent_data_id string>"
    }
  }
}
```

- Disk `job_resume` / `cover_letter` are pins, not the bodies operators edit.
- GET hydrate may show resume sections only because of `resume_content` overlay or pin→`agent_data` resolve; cover fields come from pin resolve into `agent_data`.
- If `resume_content` is cleared or never written, JAR/Print still reach into `agent_data` via the pin.
- `PUT /api/jobs/<id>/artifacts/job_resume` persists the editor dict to `resume_content` only; `job_resume` stays the id string.

### Root cause

AST-1099 made the operator-facing slots pointer-only (`job_resume` / `cover_letter` / `proposed_answers` = RESPONSE ids; body stays in `agent_data`). AST-1100 taught readers to resolve those pins. AST-1428 restored an editable resume blob as sibling `resume_content` while **keeping** the pin on `job_resume` and leaving cover letter pointer + resolve. That still leaves “what operators save/load” split from “what the slot stores,” and keeps `resolve_job_artifact_agent_data_body` on the operator path — which violates the base_resume pattern Susan named: hop RESPONSE pristine in `agent_data`, durable edits on the entity artifact body.

### Proposed change

Scope gate (AST-1548 `## Scope`): `src/core/agent.py`, `src/core/tracker.py`, `src/utils/config.py` only if pin/clear policy must change, and thin job artifact PUT/GET (tracker + `src/ui/api/api_jobs.py`). Do **not** edit `builder.py` / frontend — once slots hold body dicts, existing Print/JAR dict branches and GET hydrate suffice; do **not** re-enable `persist_job_artifact_from_parsed` for finalize hops (it can still clobber unrelated keys). `proposed_answers` stays pin-only.

**1. Config — stop pinning operator body slots — `src/utils/config.py`**

- Remove `finalize_job_resume` and `finalize_cover_letter` from `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK` (keep `propose_application_responses` → `proposed_answers`).
- Add `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` (config source of truth):

  ```python
  JOB_ARTIFACT_BODY_REPLICA_BY_TASK = {
      "finalize_job_resume": "job_resume",
      "finalize_cover_letter": "cover_letter",
  }
  ```

- Leave `JOB_BUILD_ARTIFACT_CLEAR_KEYS` as-is (`resume_content`, `job_resume`, `cover_letter`, …) so cancel still wipes operator bodies.

**2. Agent — write replica after RESPONSE store — `src/core/agent.py` `do_task`**

On the same post-RESPONSE success path used today for pins (`result.success`, `index` set, `resp_id` stored, **before** `run_next`):

- If `task_key` is in `JOB_ARTIFACT_BODY_REPLICA_BY_TASK` and `index` + `resp_id` present: lazy-import tracker body-persist helper(s); call with `index` and in-memory `parsed` (do not re-read `agent_data`; do not write `agent_data`). Best-effort: log and continue on failure (mirror AST-1428 / deviations — a copy failure must not fail the hop).
- Elif `task_key` is in `JOB_ARTIFACT_AGENT_DATA_PIN_BY_TASK`: keep today’s `pin_job_artifact_agent_data_id` behavior (`proposed_answers` only after the map change).
- Remove the finalize-only `persist_finalize_job_resume_content` call that ran *after* pin; body persist replaces that for `finalize_job_resume`, and cover gets a parallel path.

**3. Tracker — body persist helpers — `src/core/tracker.py`**

**Resume (`finalize_job_resume` → slot `job_resume`):**

- Extend `persist_finalize_job_resume_content(astral_job_id, parsed) -> bool` (or thin wrapper called from agent):
  - If `parsed_matches_job_resume_content` is false → return `False` without `save_job_data` (coat-check: never store empty; do not clear a prior body).
  - Else `body = _resume_payload_body(parsed)` then prepare via existing `_prepare_job_resume_content` / structure filter (same as today’s sibling save).
  - Persist prepared dict onto **`artifacts.job_resume`** (operator slot replica).
  - **Dual-write** the same prepared dict onto `artifacts.resume_content` so out-of-scope readers that still prefer `resume_content` (consult resume-first gate, Print prefer-path) keep working without touching `builder.py` / `consult.py`. Authoritative operator slot is `job_resume`; sibling is compatibility only.
  - Return `True` when a write happened.

**Cover (`finalize_cover_letter` → slot `cover_letter`):**

- Add `persist_finalize_cover_letter_content(astral_job_id, parsed) -> bool` next to the resume helper:
  - Unwrap hop envelope the same way display already does (`agent_payload` / nested cover keys — reuse `_cover_letter_dict_for_normalize` / slice+normalize path).
  - If normalized Subject/Letter/signature are all empty → return `False` without save (coat-check).
  - Else `save_job_artifact_cover_letter(astral_job_id, …)` so `artifacts.cover_letter` is the normalized body dict (overwrites any prior pin string on that key).
  - Do not write `agent_data`.

**4. Hydrate — job body only for operator slots — `hydrate_job_artifacts_for_display`**

For `job_resume` and `cover_letter` only:

- If the on-disk (or shallow-copied) value is a nonempty content dict → use / normalize it for the outbound overlay.
- Else if `job_resume` missing/empty dict but `resume_content` is a nonempty dict → overlay sibling onto `job_resume` (legacy AST-1428 rows).
- If the value is a pin **string** → **do not** call `resolve_job_artifact_agent_data_body` / do not pin-resolve inside `cover_letter_artifact_for_display` for this operator hydrate path (leave string or skip empty overlay — operators must not be served from `agent_data`).
- Keep pin resolve for `proposed_answers` only.
- Never persist the overlay; never write `agent_data`.

Split or gate `cover_letter_artifact_for_display` so operator hydrate cannot resolve pins (e.g. only normalize dicts; pin strings → `None`). Any non-operator caller that still needs resolve is out of this ticket’s operator contract — do not reintroduce resolve on the GET/JAR path.

**5. Editor Save — thin PUT handlers — `src/ui/api/api_jobs.py`**

- `PUT …/artifacts/job_resume` (`put_job_resume_pin_key`): require `job_resume` dict body; persist onto **`artifacts.job_resume`** (prepared/filtered like resume save) and dual-write `resume_content` for the same compat reason as §3. Never assign an `agent_data_id` string; never write `agent_data`.
- `PUT …/artifacts/cover_letter`: keep writing normalized dict via `save_job_artifact_cover_letter` (already body-on-job); confirm it never writes `agent_data`.
- `PUT …/artifacts/resume_content`: leave as explicit sibling merge (unchanged contract for callers that hit that URL).

**6. Explicit non-edits**

- No `builder.py` change: Print already uses nonempty `resume_content`, nonempty `cover_letter` dict, or nonempty `job_resume` dict before any pin fallback; after replica writes, dict/sibling paths hit first. Pin-fallback branches become dead for newly finalized jobs (acceptable; legacy pin-only jobs show empty until regenerate — product contract).
- No frontend change: GET hydrate returns body dicts on the tab keys ArtifactEditor already reads.
- Do not pin `job_resume` / `cover_letter` as non-display metadata in this pass unless a later ticket asks for a separate metadata key — Technical scope allows “instead of”; body-on-slot matching `base_resume` is the chosen reading.

### Blast radius

- AST-1099 AC1/AC2 (“slot equals RESPONSE `agent_data_id` string”) are **intentionally superseded** for `job_resume` / `cover_letter` by this bug; Betty tests that assert pointer-only slots or pin-resolve-on-GET for those keys must flip.
- AST-1428 / AST-1430 tests that require pin-string-on-`job_resume` + sibling-only save / PUT-must-not-clobber-pin must flip to body-on-`job_resume` (pin no longer on that key); dual-write keeps `resume_content` assertions greener during transition.
- AST-1100 / cover (AST-1499) paths that assume hydrate pin-resolve for cover letter will see empty overlay on legacy pin-only rows until regenerate.
- `consult` resume-first gate and Print prefer-`resume_content` keep working via dual-write without scope expansion.
- `proposed_answers` pin + resolve unchanged.
- Cancel clear keys already include both body slots and `resume_content`.

### What must still hold

- `agent_data` RESPONSE rows for finalize hops remain the pristine hop store; human Save never updates them.
- Coat-check: empty/failed hops do not overwrite a good prior job body with blank.
- Mid-chain finalize hops (`run_next` continues) still write the replica before the next hop (same timing as today’s pin/copy).
- Style D debug only when `debug=True` on touched persist paths; logging via utils.
- `propose_application_responses` → `artifacts.proposed_answers` pin semantics unchanged (AST-1099 AC3).
- Cancel / clear still removes operator job body keys in `JOB_BUILD_ARTIFACT_CLEAR_KEYS`.
- Import direction: core writes via existing `save_job_data`; UI PUT stays thin → tracker save.
- Do not copy full hop JSON envelopes into the operator slots — store the unwrapped resume section dict / normalized cover fields only (same shapes JAR already edits).

---

## Radia review — AST-1548 (2026-08-31)

**Overall:** DISCUSS / REVIEW — product matches plan; bible keep-pin suites pending on gap sibling AST-1554.
**Publish:** `origin/sub/AST-1547/AST-1548-fix-job-resume-body-replica` @ `d5113a8b`
**fix-now:** none on product.
**discuss:** Board TESTS:REVISE + AST-1554 gap must land before orphaned finish-up merges to `dev`.
**advisory:** Stale `agent.py` comment still mentions finalize pin; builder pin-fallback left in blast radius.

## Resolution — AST-1548 (2026-08-31)

**Outcome:** advisory addressed in product comment only; discuss acknowledged (tests stay on gap AST-1554).

- **fix-now:** none.
- **discuss (AST-1554 before finish-up):** Closed without product expansion. Keep-pin / bible flips remain on gap sibling AST-1554; this child does not absorb test-tree work. Chuckles must not finish-up / land orphaned parent to `dev` until AST-1554 is User Testing (or Done) alongside this tip.
- **advisory (stale `agent.py` finalize-pin comment):** Updated terminal `do_task` comment so it no longer claims finalize hops pin `agent_data_id`; notes AST-1548 body replicas (+ `proposed_answers` pin) already ran above and forbids re-enabling `persist_job_artifact_from_parsed`.
- **advisory (builder pin-fallback):** Left as planned blast radius — Print dict/`resume_content` paths hit first for new replicas; `builder.py` remains out of AST-1548 scope (plan §6 Explicit non-edits).

