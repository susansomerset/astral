<!-- linear-archive: AST-1111 archived 2026-08-07 -->

## Linear archive (AST-1111)

**Archived:** 2026-08-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1111/anomaly-job-artifact-entry-task-keys-cover-letter-carve-out-hard-coded  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1109 — Hard-coded daisy chain in config.py  
**Blocked by / blocks / related:** parent: AST-1109

### Description

## What this implements

End-to-end against AST-1110: delete `JOB_ARTIFACT_ENTRY_TASK_KEYS` frozenset/wrappers; wire membership to `run_next`; eradicate cover-letter special exclusion; keep §2.6.0 claim/graduation green for this surface.

## In scope

- [X] `astral.dispatch.run-next-is-chain-authority` — delete named shadow; do not replace with another hop-membership list
- [X] `pattern.dispatch.run-next-chain-authority` — bind to statute (pattern remains proposed; do not depend on catalog approval)
- [X] `astral.state.no-daisy-chain-in-run` — keep §2.6.0 claim/match helpers that already use `run_next`
- [X] `astral.standards.no-hardcoded-sets` — config shadow of `run_next` is not a conforming escape; delete rather than relocate
- [X] `astral.standards.in-scope-only` — this anomaly only (`JOB_ARTIFACT_ENTRY_TASK_KEYS` + `build_artifacts_chain_task_keys` cover-letter carve-out)
- [X] `astral.standards.dry-and-focused-functions` — no parallel membership helper; reuse existing `run_next` readers
- [X] `astral.docs.features-single-file-per-ticket` — plan at `docs/features/dispatcher/ast-1111-anomaly-job-artifact-entry-task-keys.md`

## Considered but excluded

- [X] `BUILD_CONFIG.resume_artifact_chain.hop_task_keys` / `_RESUME_ARTIFACT_HOP_TASK_KEYS` — AST-1112
- [X] `CANDIDATE_STAGE_DISPATCH` `craft_task_keys` + boot SQL confirm/correct — AST-1113
- [X] AST-1108 seed-data ghost cleanup — Foundation; related context only
- [X] `astral.standards.database-header-inventory` — no boot SQL in this child
- [X] Approving `pattern.dispatch.run-next-chain-authority` — stays proposed; remediations bind to statute
- [X] `_dispatch_trigger_state_for_task_key` admin defaults for `draft_cover_letter` / cover hops — not the frozenset carve-out
- [X] Engineer edits to `tests/` / `docs/test-bible/**` — Betty owns test-tree revision after Code Complete

## Acceptance criteria

- [X] 2. `JOB_ARTIFACT_ENTRY_TASK_KEYS` is gone; no remaining import or membership check against that name; cover-letter hops follow the same run_next-driven rules (no frozenset-exclusion carve-out).
- [X] 3. This child’s product path does not consult the retired hard-coded list for chain membership; §2.6.0 claim/match helpers that already use `run_next` remain the path for hop-label eligibility.

## Boundaries

Does **not** own hop_task_keys or craft_task_keys remediations (siblings). Does **not** own AST-1108. Does **not** author the statute file.

## Notes for planning

Vertical anomaly against the new statute. Tip survey: both symbols are dead under `src/` after AST-849; delete-only; Betty revises tests that still assert the frozenset.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1109-hard-coded-daisy-chain-in-configpy`, child `sub/AST-1109/AST-1111-anomaly-job-artifact-entry-task-keys`. Created at dispatch-parent.

### Comments

#### radia — 2026-07-31T19:43:00.230Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1111
**Publish ref:** `origin/sub/AST-1109/AST-1111-anomaly-job-artifact-entry-task-keys` tip `b308809f` (product tip `230c0f4c` + docs review)
**Overall:** DISCUSS

Diff: `origin/dev...origin/sub/.../AST-1111-…` — layers `{docs, utils}`; change_types `{add, modify}` (config delete lands as modify). AST-1111 Stage 1 = delete-only in `src/utils/config.py`; Betty revised tests/bible; tip also carries AST-1110 statute/pattern (blockedBy).

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | conforms | config.py touched; CONFIDENCE_* block untouched |
| astral.agent.do-task-delegation | scoped | not-applicable | layers/paths require src/core |
| astral.agent.grade-vector-validation | scoped | not-applicable | layers/paths require src/core |
| astral.batch.batch-id-first | scoped | not-applicable | layers/paths require data/core |
| astral.batch.batch-id-format | scoped | not-applicable | layers/paths require core/data |
| astral.batch.claim-process-release | scoped | not-applicable | layers/paths require core/data |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | layers/paths require core/data |
| astral.config.config-source-of-truth | scoped | conforms | removes config shadow of DB-owned run_next topology |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | pass-threshold / score-floor untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets/env edits |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths artifacts/spikes unmatched |
| astral.debug.spikes-under-debug-dir | scoped | conforms | feature plans, not spike notes under docs/features |
| astral.dispatch.run-next-is-chain-authority | scoped | conforms | deletes named JOB_ARTIFACT_ENTRY shadow; no replacement list |
| astral.dispatch.seed-auto-false | scoped | conforms | seed AUTO defaults untouched |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single AST-1111 plan under docs/features/dispatcher/ |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits tests/bible only; engineer owns config + plan |
| astral.git.engineer-test-tree-ban | scoped | conforms | test-tree revisions are Betty test/merge-tests |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers/paths require core/external |
| astral.layers.import-direction | scoped | conforms | delete-only; no new imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths require scripts |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | no UI business-logic hardcoding; utils delete only |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | layers/paths require src/core |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | layers/paths require src/core |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers/paths require src/ui |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | layers exclude utils-only |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths require src/data |
| astral.standards.debug-contract-gated | scoped | conforms | no debug= emission changes |
| astral.standards.dry-and-focused-functions | scoped | conforms | no parallel membership helper added |
| astral.standards.in-scope-only | scoped | conforms | only JOB_ARTIFACT_ENTRY + wrapper; siblings untouched |
| astral.standards.logging-via-utils | scoped | conforms | no logging changes |
| astral.standards.no-cross-contamination | scoped | conforms | no cross-entity contamination |
| astral.standards.no-hardcoded-sets | scoped | conforms | deletes shadow rather than relocating set |
| astral.standards.public-then-helpers | scoped | conforms | removes dead public symbols; no reorder violation |
| astral.standards.utils-data-late-import-only | scoped | conforms | no utils→data import added |
| astral.state.core-decides-transitions | scoped | not-applicable | layers/paths require core/data |
| astral.state.job-prior-states-enforced | scoped | conforms | prior-state maps untouched |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layers/paths require src/core |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers/paths require frontend |
| astral.ui.naming-conventions | scoped | not-applicable | layers/paths require src/ui |
| astral.ui.single-gunicorn-worker | scoped | conforms | gunicorn/worker config untouched |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests(AST-1111) one SHA from origin/tests |
| orch.git.commit-vocabulary | universal | conforms | docs/code/test/merge-tests on sub tip |
| orch.git.flow-direction-inviolable | universal | conforms | publish to origin/sub/AST-1109/AST-1111-… |
| orch.git.ftr-sub-topology | universal | conforms | matches parent Git table |
| orch.git.merge-on-checkout | universal | conforms | no illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | none in reviewed history |
| orch.git.no-dev-agent-branches | universal | conforms | sub publish-ref only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | epic worktree astral-AST-1109 |
| orch.git.three-permanent-branches | universal | conforms | no permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | delete-only Decision; no product fork |
| orch.pipeline.plan-is-bible | universal | conforms | Stage 1 matches landed config delete |
| orch.pipeline.project-scoped-queues | universal | conforms | single-child Dispatcher scope |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no new statute body in this child (1110 owns) |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty test + bible + merge-tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Ada implementer through Tests Passed |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Radia docs-only; assignee left Ada |
| orch.roles.pre-commit-path-bans | universal | conforms | engineer Stage 1 = config.py only |

Active-set count: **58**.

## Pattern conformance

- `pattern.dispatch.run-next-chain-authority` — **conforms** (cited; remediations bind statute; pattern remains proposed on tip from AST-1110)

## Plan adherence

Stage 1 delete matches tip: both symbols gone under `src/`; §2.6.0 helpers not in the code commit; no hop_task_keys/craft/boot SQL. Self-Assessment `minor` matches. Betty test retirement expected post–Code Complete.

## Findings

### discuss (C4 stragglers)

Joan excluded scoped statutes using plan `change_types={delete}` (Files Changed wording). Three-dot git status is `modify`/`add`, so these score in-scope here (verdicts `conforms` above):

astral.agent.confidence-bounds, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.config.secrets-and-env-specific-from-environ, astral.debug.spikes-under-debug-dir, astral.dispatch.run-next-is-chain-authority, astral.dispatch.seed-auto-false, astral.docs.features-single-file-per-ticket, astral.git.engineer-test-tree-ban, astral.layers.import-direction, astral.layers.ui-config-driven-business-logic, astral.standards.debug-contract-gated, astral.standards.dry-and-focused-functions, astral.standards.logging-via-utils, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.standards.utils-data-late-import-only, astral.state.job-prior-states-enforced, astral.ui.single-gunicorn-worker

No fix-now. §5a–§5g: delete-only utils; no debug contract / external / silent-failure issues.

### Notes

Plan-rubric verdict attached (Joan APPROVED). Zero `rg` hits for retired names under `src/`; `py_compile` clean.

**What’s solid:** statute-named shadow removed end-to-end for this surface; cover-letter frozenset carve-out eradicated with the wrapper; sibling boundaries held.

context_tokens≈48000

#### betty — 2026-07-31T19:38:41.350Z
## QA test manifest

**Publish:** `origin/sub/AST-1109/AST-1111-anomaly-job-artifact-entry-task-keys` @ `230c0f4c` (`merge-tests(AST-1111): origin/tests fcdca59a3935b8176d4c77a7a05aa7138f5fcf0c`)

**Broken / obsolete (revised this pass):**
- `TestAst740RemoveConfigGrouping::test_job_artifact_entry_task_keys_membership` → `test_job_artifact_entry_task_keys_absent`
- `TestAst844BuildArtifactsChainTaskKeys` → `TestAst1111JobArtifactEntryShadowDeleted`

**Manifest (narrowed run):**

1. `tests/component/utils/test_config.py::TestAst1111JobArtifactEntryShadowDeleted`
2. `tests/component/utils/test_config.py::TestAst740RemoveConfigGrouping`
3. `tests/component/utils/test_config.py::TestAst848DispatchHopLabels` (regression — §2.6.0 hop labels)
4. `tests/component/utils/test_config.py::TestAst849DispatchChainClaimStates` (regression — claim/match still run_next-driven)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1111JobArtifactEntryShadowDeleted \
  tests/component/utils/test_config.py::TestAst740RemoveConfigGrouping \
  tests/component/utils/test_config.py::TestAst848DispatchHopLabels \
  tests/component/utils/test_config.py::TestAst849DispatchChainClaimStates \
  -q
```

**Integration:** none (no existing scenario drift).

**Bible shasums on publish tip:**
- `docs/test-bible/utils/config.md` `ff7b48dfda0a4754ddb173ee915cbf8ff6efdb3d`
- `docs/test-bible/core/consult.md` `c29e65325b44379e8ec549e774dcf92dd5dedf1d`
- `docs/test-bible/core/agent.md` `da3da62af9965d557ab3c325337f8e0b33e35413`

— Betty

#### ada — 2026-07-31T19:35:10.459Z
origin/sub/AST-1109/AST-1111-anomaly-job-artifact-entry-task-keys @ c736c785 — product delete at 88ab9675; `tests/component/utils/test_config.py` still asserts `JOB_ARTIFACT_ENTRY_TASK_KEYS` / `build_artifacts_chain_task_keys` (Betty).

#### joan — 2026-07-31T19:31:51.507Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1111
**Overall:** APPROVED

## Traceability

### Parent AC → plan stages (this child only)

| Parent AC | Plan coverage |
|-----------|---------------|
| AC1 statute + CODE_RULES | N/A — boundary (AST-1110) |
| AC2 JOB_ARTIFACT_ENTRY_TASK_KEYS gone; cover-letter same run_next rules | Stage 1 delete frozenset + wrapper carve-out |
| AC3 resume hop_task_keys | N/A — boundary (AST-1112) |
| AC4 craft_task_keys | N/A — boundary (AST-1113) |
| AC5 craft boot SQL | N/A — boundary (AST-1113) |
| AC6 product path does not consult retired list; §2.6.0 run_next helpers remain | Stage 1 (no new membership list; helpers untouched; rg stop-gate) |

### Child AC → plan stages

| Child AC | Plan coverage |
|----------|---------------|
| Parent AC2 (JOB_ARTIFACT_ENTRY gone; cover-letter run_next parity) | Stage 1 |
| Parent AC6 slice (no consult of retired list) | Stage 1 |

### Plan stages → definition

| Stage | Maps to |
|-------|---------|
| Stage 1 delete shadow + cover-letter carve-out | Functional scope anomaly job-artifact entry frozenset; Purpose config-as-loophole; child AC |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge-tests in this plan |
| orch.git.commit-vocabulary | conforms | Stage commit on sub publish-ref |
| orch.git.flow-direction-inviolable | conforms | Publish only to origin/sub/… |
| orch.git.ftr-sub-topology | conforms | Matches parent Git table |
| orch.git.merge-on-checkout | conforms | No illegal merge recipe |
| orch.git.no-cherry-pick-rebase-force | conforms | None proposed |
| orch.git.no-dev-agent-branches | conforms | sub/AST-1109/AST-1111-… only |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree astral-AST-1109 |
| orch.git.three-permanent-branches | conforms | No permanent-branch invention |
| orch.pipeline.call-susan-for-product-decisions | conforms | Delete-only Decision documented; stop→parent if consumer appears |
| orch.pipeline.plan-is-bible | conforms | Binding stage + Files Changed present |
| orch.pipeline.project-scoped-queues | conforms | Single-child scope |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready validate-plan only |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits (AST-1110 owns) |
| orch.roles.betty-owns-test-tree | conforms | Explicitly forbids engineer tests/bible edits |
| orch.roles.chuckles-never-ticket-assignee | conforms | Engineer (Ada) build path |
| orch.roles.engineer-assignee-through-resolve | conforms | Engineer implementer after Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | Only config.py delete; no banned paths |
| astral.git.betty-no-src-or-features | conforms | Engineer owns src delete; Betty not author |
| astral.standards.in-scope-only | conforms | Only JOB_ARTIFACT_ENTRY + wrapper; siblings/AST-1108 excluded |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.git.betty-no-src-or-features, astral.standards.in-scope-only

**Excluded:**
- astral.agent.confidence-bounds — change_types ∩ {delete} empty
- astral.agent.do-task-delegation — layers ∩ {utils} empty
- astral.agent.grade-vector-validation — layers ∩ {utils} empty
- astral.batch.* — layers ∩ {utils} empty or change_types ∩ {delete} empty
- astral.config.config-source-of-truth — change_types ∩ {delete} empty
- astral.config.pass-threshold-vs-score-floor — change_types ∩ {delete} empty
- astral.config.secrets-and-env-specific-from-environ — change_types ∩ {delete} empty
- astral.debug.* — paths match none
- astral.dispatch.run-next-is-chain-authority — change_types ['add','modify'] ∩ {delete} empty
- astral.dispatch.seed-auto-false — change_types ∩ {delete} empty
- astral.docs.features-single-file-per-ticket — paths match none
- astral.git.engineer-test-tree-ban — paths match none
- astral.layers.* — layers empty or change_types ∩ {delete} empty
- astral.patterns.* — layers empty or change_types ∩ {delete} empty
- astral.standards.data-raises-caller-logs — layers ∩ {utils} empty
- astral.standards.database-header-inventory — layers ∩ {utils} empty
- astral.standards.debug-contract-gated — change_types ∩ {delete} empty
- astral.standards.dry-and-focused-functions — change_types ∩ {delete} empty
- astral.standards.logging-via-utils — change_types ∩ {delete} empty
- astral.standards.no-cross-contamination — change_types ∩ {delete} empty
- astral.standards.no-hardcoded-sets — change_types ∩ {delete} empty
- astral.standards.public-then-helpers — change_types ∩ {delete} empty
- astral.standards.utils-data-late-import-only — change_types ∩ {delete} empty
- astral.state.* — layers empty or change_types ∩ {delete} empty
- astral.ui.* — layers empty or change_types ∩ {delete} empty

**Notes:** Files Changed Change=`Delete…` → plan change_types `{delete}` only. Binding statute `astral.dispatch.run-next-is-chain-authority` is matching-excluded by its applies_when change_types, but Stage 1 still remediates its named violating example (delete-only, no replacement list). Tip survey confirms symbols live only in `config.py` (+ Betty tests).

## Findings

None fix-now.

**acceptable:** Ticket “wire membership to run_next” satisfied by leave-existing §2.6.0 path + delete dead shadow (Decision + tip survey + step-5 stop-gate). Self-assessment minor / Conf high / Risk low honest. Betty owns frozenset test revision — engineer correctly banned from tests/.

**R6:** Definition fidelity pass for this anomaly. Layer utils delete-only. No new config sets. No batch/state-machine edits. DRY (no parallel helper). No sibling creep.

context_tokens≈42000

— Joan

#### ada — 2026-07-31T19:29:10.751Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1109/AST-1111-anomaly-job-artifact-entry-task-keys/docs/features/dispatcher/ast-1111-anomaly-job-artifact-entry-task-keys.md

**Scope:** `minor` — delete unused `JOB_ARTIFACT_ENTRY_TASK_KEYS` + `build_artifacts_chain_task_keys()` in `config.py`; no core routing edits on tip (AST-849 already routes via `run_next`).

**Conf:** `high` — zero `src/` consumers; statute/parent AC name this exact shadow; siblings explicitly out of scope.

**Risk:** `low` — product ignores these symbols today; step-5 `rg` gate stops if a hidden consumer appears; Betty owns test assertions that still lock the frozenset.

#### chuckles — 2026-07-31T19:24:16.895Z
[thread-missing] Cursor chat `5caa0d32-de54-49fd-aa93-62460d7ac8f5` has no local `store.db` on this host. Minted Ada Team thread `e25b8e8b-59ef-45c0-8661-36eb6b1ce817` and updated parent ## Team.

— Chuckles

---

# Anomaly — JOB_ARTIFACT_ENTRY_TASK_KEYS + cover-letter carve-out

**Linear:** [AST-1111](https://linear.app/astralcareermatch/issue/AST-1111/anomaly-job-artifact-entry-task-keys-cover-letter-carve-out-hard-coded)  
**Parent:** [AST-1109](https://linear.app/astralcareermatch/issue/AST-1109/hard-coded-daisy-chain-in-configpy) — Hard-coded daisy chain in config.py  
**Publish ref:** `sub/AST-1109/AST-1111-anomaly-job-artifact-entry-task-keys`

Delete the config shadow `JOB_ARTIFACT_ENTRY_TASK_KEYS` and its wrapper `build_artifacts_chain_task_keys()` (cover-letter frozenset carve-out) end-to-end against statute `astral.dispatch.run-next-is-chain-authority` (AST-1110). Product chain membership for this surface already comes from `agent_task.run_next` via §2.6.0 helpers — do not invent a replacement membership frozenset. Leave hop_task_keys / craft_task_keys / AST-1108 to siblings.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Delete `JOB_ARTIFACT_ENTRY_TASK_KEYS` and `build_artifacts_chain_task_keys()` (comment + frozenset + wrapper) | utils |

## Stage 1: Delete job-artifact entry shadow + cover-letter carve-out

**Done when:** Neither `JOB_ARTIFACT_ENTRY_TASK_KEYS` nor `build_artifacts_chain_task_keys` exists in `src/`; `rg` over `src/` for both names returns zero matches; `python3 -m py_compile src/utils/config.py` succeeds; §2.6.0 helpers (`_agent_task_parents_with_run_next`, `dispatch_chain_row_matches_job`, `dispatch_chain_claim_states_for_row`, `is_dispatch_chain_trigger`, `is_valid_job_batch_claim_state`) are unchanged by this stage.

1. In `src/utils/config.py`, locate the block immediately after `is_conversational_task` (currently ~lines 932–949):

   - Comment: `# Dispatch consult hops that enter the job-artifact chain…` / `# Excludes draft_cover_letter…`
   - Constant: `JOB_ARTIFACT_ENTRY_TASK_KEYS = frozenset({…})`
   - Function: `build_artifacts_chain_task_keys()` whose body is `frozenset(JOB_ARTIFACT_ENTRY_TASK_KEYS) - frozenset({"draft_cover_letter"})`

2. Delete that entire block (comment + constant + function). Leave the preceding `is_conversational_task` and the following `CONFIDENCE_*` section adjacent with a single blank line between them (match neighboring style).

3. Do **not** add a replacement frozenset, helper, or cached set of “entry keys” derived from `run_next`. Membership authority for this surface is already:

   - `is_dispatch_chain_trigger` + `task_key in TASK_CONFIG` → `_run_dispatch_chain_job_batch` in `src/core/consult.py`
   - `dispatch_chain_row_matches_job` / `dispatch_chain_claim_states_for_row` / `_agent_task_parents_with_run_next` (read live `agent_task.run_next`)
   - `_current_agent_task_run_next` for hop succession inside `do_task`

4. Do **not** edit `src/core/consult.py`, `src/core/dispatcher.py`, `src/core/agent.py`, or any other `src/**` file in this stage unless step 5 forces a stop.

5. Verify on epic worktree:

   ```bash
   rg -n 'JOB_ARTIFACT_ENTRY_TASK_KEYS|build_artifacts_chain_task_keys' src/
   python3 -m py_compile src/utils/config.py
   ```

   Expect zero `rg` hits under `src/`. If any `src/` consumer still imports either name, **stop** and comment on parent AST-1109 with the Stage N blocked template (do not invent a shim).

6. Do **not** touch:

   - `BUILD_CONFIG.resume_artifact_chain.hop_task_keys` / `_RESUME_ARTIFACT_HOP_TASK_KEYS` / `resume_artifact_hop_task_keys` (AST-1112)
   - `CANDIDATE_STAGE_DISPATCH` `craft_task_keys` or boot SQL (AST-1113)
   - `_dispatch_trigger_state_for_task_key` defaults for `draft_cover_letter` / cover hops (admin Save defaults — not this frozenset carve-out)
   - `tests/**`, `docs/test-bible/**`, `docs/ASTRAL_TEST_BIBLE.md` (Betty owns; expect existing assertions on these symbols to fail until Betty revises)
   - Statute / pattern / CODE_RULES files (already landed by AST-1110)

⚠️ **Decision:** Delete-only remediation. Tip survey shows both symbols are defined in `config.py` and referenced only from `tests/component/utils/test_config.py` — consult already routes job-artifact / cover hops through `is_dispatch_chain_trigger` + `TASK_CONFIG` (AST-848/849), so “wire membership to `run_next`” is already the live path; replacing the frozenset with another config set would re-violate `astral.dispatch.run-next-is-chain-authority`. Cover-letter special exclusion lives only in that dead comment + wrapper subtraction — deleting the block eradicates it without a new carve-out.

## Execution contract

- Stages in order; one commit per stage on the epic worktree sub branch; publish to `origin/<publish-ref>` after each stage per build-child.
- No files outside the Files Changed table.
- Ambiguity or codebase drift → stop and comment on **parent** AST-1109 with the Stage N blocked template.
- Leave hop_task_keys, craft_task_keys, boot SQL, Manage Tasks UI, AST-1108, and Betty’s test tree untouched.

## Self-Assessment

**Scope:** `minor` — delete one unused frozenset and its cover-letter-subtraction wrapper in `src/utils/config.py`; no core/UI routing edits required on tip.

**Conf:** `high` — symbols have zero `src/` consumers after AST-849; statute + parent AC name this exact shadow; sibling surfaces are explicitly out of scope.

**Risk:** `low` — product path already ignores these symbols; wrong delete would only matter if a hidden consumer appears (step 5 stop gate). Betty must revise tests that still assert membership / carve-out — engineer must not patch `tests/`.

## Self-review vs ASTRAL_CODE_RULES

- **§2.6.0 / `astral.dispatch.run-next-is-chain-authority`:** Removes the named violating example; does not replace it with another hop-membership list; leaves claim/graduation helpers that read `run_next` intact.
- **§1.4 / no-hardcoded-sets:** Does not “fix” by moving the set elsewhere in config — deletes the shadow.
- **§1.1 / in-scope-only:** No hop_task_keys, craft_task_keys, boot SQL, or AST-1108.
- **§1.3 DRY:** No new parallel membership helper.
- **§3.3 imports:** No new imports; unused import cleanup N/A (symbols were not imported elsewhere under `src/`).
- **Betty test-tree ban:** Plan forbids engineer edits under `tests/` / bible.
- **No conflict requiring conf-!!-NONE.**

## Review

**Publish ref:** `origin/sub/AST-1109/AST-1111-anomaly-job-artifact-entry-task-keys`
**Tip:** `88ab9675`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `88ab9675` | delete JOB_ARTIFACT_ENTRY_TASK_KEYS + build_artifacts_chain_task_keys |

### Radia — code-rubric.v1 (AST-1111)

`[code-rubric] revision=1` · tip reviewed `230c0f4c` · **Overall: DISCUSS** (C4 stragglers only; deliverable conforms)

**What's solid**

- Delete-only: `JOB_ARTIFACT_ENTRY_TASK_KEYS` + `build_artifacts_chain_task_keys()` gone; zero `src/` hits; no replacement membership list.
- §2.6.0 helpers untouched; hop_task_keys / craft_task_keys / boot SQL left to siblings.
- Betty owns test/bible retirement of frozenset asserts; engineer Stage 1 is `config.py` only.

**Discuss (C4 stragglers)** — Joan excluded many scoped statutes via plan `change_types={delete}`; three-dot git status is `modify`/`add`, so they are in-scope here (scores themselves `conforms`). See Linear comment for the full list.

## Resolution

**Date:** 2026-07-31  
**Publish tip before resolve:** `b308809f` (`docs(AST-1111): Radia review — findings`)

Radia overall **DISCUSS** — no fix-now product or plan-doc edits. Deliverable statutes all **conforms**.

| Finding | Disposition |
|---------|-------------|
| discuss (Joan Excluded C4 stragglers on three-dot tip; full list in Radia Linear comment) | Accepted as non-blocking; each scored **conforms** in Radia’s sweep; no product change. Files Changed left as engineer delete-only `config.py` (Betty bible/tests stay Betty-owned). |

No product commits on this resolve pass.
