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
