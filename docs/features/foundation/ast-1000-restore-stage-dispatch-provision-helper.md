<!-- linear-archive: AST-1000 archived 2026-08-05 -->

## Linear archive (AST-1000)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1000/restore-stage-dispatch-provision-helper-getting-a-stack-trace-on  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** Urgent / —  
**Parent:** AST-995 — getting a stack trace on localhost boot  
**Blocked by / blocks / related:** parent: AST-995

### Description

## What this implements

Reintroduce the missing data-layer candidate-id listing used by boot-time stage-dispatch provision; confirm localhost boot no longer AttributeErrors on that path. Does **not** own candidate state vocabulary or AST-973 migration logic beyond not regressing it.

## Acceptance criteria

1. Fresh localhost boot no longer prints `AttributeError: module 'src.data.database' has no attribute 'list_candidate_ids_with_dispatch_tasks'` (or equivalent) during scheduler start.
2. Boot no longer prints `AST-972 stage dispatch provision failed` caused by that missing helper.
3. With at least one candidate that already has a dispatch_task row, boot-time provision can enumerate that candidate and run without the AttributeError.
4. With no such candidates, boot still starts the scheduler without a traceback from this path.
5. Existing component coverage that asserts the listing helper / provision path remains meaningful (green for this contract).

## Boundaries

Does **not** redesign the candidate state machine (AST-871) or reopen AST-972 / AST-973 product scope. Does **not** change craft prompts or REQUESTED_* claim/resolve beyond making provision callable again. Does **not** change Stytch, Vite, or unrelated boot messages.

## Notes for planning

Helper was introduced under AST-972 and dropped on the AST-973 land into the composite tree; restore the listing contract the dispatcher already calls. Data layer raises; dispatcher logs. Keep AST-973 migration behavior intact.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-995-localhost-boot-stack-trace`, child `sub/AST-995/AST-1000-restore-stage-dispatch-provision-helper`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-07-28T15:04:24.980Z
[check-linear] User Testing — already on ftr

#### ada — 2026-07-28T14:46:07.091Z
Tip rebuilt for `[merge-child]` validate-sub-log.

`origin/sub/AST-995/AST-1000-restore-stage-dispatch-provision-helper` @ `9fff225c` — stacked on `origin/ftr/AST-995-localhost-boot-stack-trace` (`f18aded5`).

```
plan(AST-1000) → code(AST-1000) → merge-tests(AST-1000): origin/tests 11509597 → test(AST-1000): — green (no product fixes) → docs(AST-1000) → resolve(AST-1000)
```

Removed `Merge remote-tracking branch 'origin/dev'…` and foreign AST-996/997/998 history from the scoped log. Product/bible/test blobs unchanged vs prior tip. Single `merge-tests` re-applied from Betty’s `origin/tests` `11509597` (no second Betty pass needed unless she wants to re-verify).

`./scripts/git/validate-sub-log.sh sub/AST-995/AST-1000-restore-stage-dispatch-provision-helper AST-1000 ftr/AST-995-localhost-boot-stack-trace` → **ok**. Dry-run clean vs `origin/dev` and `origin/ftr`.

@Chuckles Cursor — ready for merge-child.

#### betty — 2026-07-28T14:41:02.862Z
Duplicate `merge-tests(AST-1000)` collapsed to one.

- `origin/tests` squashed → `11509597` (`test(AST-1000): listing helper coverage + narrowed manifest bible`)
- `origin/sub/AST-995/AST-1000-restore-stage-dispatch-provision-helper` @ `cc7e9115` — single `merge-tests(AST-1000): origin/tests 11509597…`, then Radia `docs` + Ada `resolve` replayed; bible/tests tip content unchanged.

Chuckles can re-run `merge-child`.

— Betty

#### chuckles — 2026-07-28T14:38:46.355Z
[merge-child] blocked: duplicate merge-tests(AST-1000) on sub — count=2 (amend on tests, one merge-tests only)

```
ffe47510 merge-tests(AST-1000): origin/tests b9dd9e35…
0425993e merge-tests(AST-1000): origin/tests 4c9d0dcf…
```

@Betty White — tests hygiene: collapse to a single `merge-tests(AST-1000)` on `origin/sub/AST-995/AST-1000-restore-stage-dispatch-provision-helper`, then Chuckles can re-run merge-child.

— Chuckles

#### radia — 2026-07-28T14:36:56.840Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1000
**Publish ref:** `8178edbd3d82c915d7d18c67f64eefa55207e56e` (`origin/sub/AST-995/AST-1000-restore-stage-dispatch-provision-helper`)
**Overall:** DISCUSS

**Diff:** `origin/dev...origin/sub/AST-995/AST-1000-restore-stage-dispatch-provision-helper`
**Change set:** layers=`data,docs`; paths=`src/data/database.py` (M), `docs/features/foundation/ast-1000-restore-stage-dispatch-provision-helper.md` (A), `docs/test-bible/data/database/dispatch_tasks.md` (M), `tests/component/data/database/test_dispatch_tasks.py` (M); change_types=`add,modify`.

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | layers/paths miss data+docs change set |
| astral.agent.do-task-delegation | scoped | not-applicable | layers/paths miss core |
| astral.agent.grade-vector-validation | scoped | not-applicable | layers/paths miss core |
| astral.batch.batch-id-first | scoped | conforms | listing helper only; no claim/get/clear batch API |
| astral.batch.batch-id-format | scoped | conforms | no batch_id generation or format change |
| astral.batch.claim-process-release | scoped | conforms | no select-and-process without claim; DISTINCT list only |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | no agent_data / latest-refs surface |
| astral.config.config-source-of-truth | scoped | conforms | no new config keys or state vocab |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | no scoring/dispatch floor changes |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | layers miss data |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss artifacts/** / spikes |
| astral.debug.spikes-under-debug-dir | scoped | conforms | plan doc under docs/features; not a debug spike (C4 straggler vs Joan exclude) |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single `ast-1000-…` features file (C4 straggler vs Joan exclude) |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty merge-tests touched bible/tests only; src/features via engineer/plan |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer `code()` is src-only; tests/bible via Betty merge-tests (C4 straggler) |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers/paths miss core/external |
| astral.layers.import-direction | scoped | conforms | additive data helper; no new cross-layer imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss scripts |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | layers/paths miss ui/config |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | layers/paths miss core |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | layers/paths miss core |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers/paths miss ui |
| astral.standards.data-raises-caller-logs | scoped | conforms | no logging in restored helper; dispatcher already logs provision failures |
| astral.standards.database-header-inventory | scoped | conforms | queries existing inventoried `dispatch_task`; header unchanged |
| astral.standards.debug-contract-gated | scoped | not-applicable | layers miss data |
| astral.standards.dry-and-focused-functions | scoped | conforms | reuses `_ensure_dispatch_task_schema` / `_get_connection` / `_run_with_retry` |
| astral.standards.in-scope-only | scoped | conforms | exact AST-972 restore; no AST-973/871/Stytch/Vite scope creep |
| astral.standards.logging-via-utils | scoped | not-applicable | layers miss data |
| astral.standards.no-cross-contamination | scoped | conforms | stays in data-layer dispatch_task helpers |
| astral.standards.no-hardcoded-sets | scoped | conforms | no new hardcoded state/magic sets |
| astral.standards.public-then-helpers | scoped | conforms | public API between peer public list helpers |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | layers/paths miss utils |
| astral.state.core-decides-transitions | scoped | conforms | no state transitions; listing only |
| astral.state.job-prior-states-enforced | scoped | conforms | no job prior-state / hop changes |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layers/paths miss core |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers/paths miss ui frontend |
| astral.ui.naming-conventions | scoped | not-applicable | layers/paths miss ui |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | layers/paths miss ui/scripts/config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests SHAs on publish-ref for bible/tests |
| orch.git.commit-vocabulary | universal | conforms | `code` / `docs` / `merge-tests` vocabulary used |
| orch.git.flow-direction-inviolable | universal | conforms | child publish on `sub/AST-995/…` only |
| orch.git.ftr-sub-topology | universal | conforms | sub under parent AST-995 ftr topology |
| orch.git.merge-on-checkout | universal | conforms | `origin/dev` merge present on tip history |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | normal commits; no cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | universal | conforms | authoritative sub ref; not Linear agent branch |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in `astral-AST-995/` |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branch |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | restore-not-redesign; no product fork |
| orch.pipeline.plan-is-bible | universal | conforms | Stage 1 body restored byte-exact to plan |
| orch.pipeline.project-scoped-queues | universal | conforms | Astral Foundation child |
| orch.pipeline.status-gates-skill-entry | universal | conforms | entered at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | no statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | test/bible via Betty merge-tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada stays assignee through Review Posted |
| orch.roles.pre-commit-path-bans | universal | conforms | engineer product commit src-only |

## Pattern conformance

none cited

## Plan adherence

Self-Assessment Scope **minor** matches footprint: one public data-layer listing function. Plan Stage 1 SQL/`_run_with_retry` body matches tip exactly; placement between `list_dispatch_tasks_for_candidate` and `count_dispatch_tasks_by_candidate`; dispatcher / AST-973 paths untouched. Conf high / Risk low still honest. Cross-ticket: no AST-871/973/Stytch/Vite smuggling.

## Findings

**discuss (C4 straggler):** `astral.debug.spikes-under-debug-dir` — Joan excluded (plan Files Changed = data only); three-dot includes `docs/features/**`. Re-score **conforms** (not a spike).

**discuss (C4 straggler):** `astral.docs.features-single-file-per-ticket` — Joan excluded; plan file in diff. Re-score **conforms** (single ticket features file).

**discuss (C4 straggler):** `astral.git.engineer-test-tree-ban` — Joan excluded (plan: engineer does not touch tests); three-dot includes tests/bible from Betty `merge-tests`. Re-score **conforms** (engineer `code()` src-only).

No fix-now. No product code change expected for these stragglers.

## Notes

Joan plan-rubric verdict attached (APPROVED). C4 stragglers above are pipeline docs/tests paths vs plan-time product Files Changed — not product defects.

### What’s solid

Exact AST-972 restore; data raises / caller logs preserved; header inventory already lists `dispatch_task`.

### Recommended actions

`resolve-child`: acknowledge C4 stragglers; proceed without product edits unless Archie asks to refine plan-time exclusions.

context_tokens≈48000

#### betty — 2026-07-28T04:56:07.164Z
[check-linear]

Cleared Ada `[qa-handoff]`: narrowed AST-1000 green gate to listing + dispatcher provision (eligibility stage_keys asserts stay in suite, out of this child — product restore beyond Files Changed).

**Updated manifest (test-child):**
1. `./scripts/testing/run_component_tests.sh tests/component/data/database/test_dispatch_tasks.py::TestAst972CandidateStageEligibility::test_list_candidate_ids_with_dispatch_tasks -q`
2. `./scripts/testing/run_component_tests.sh tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch -q`

**Publish:** `origin/sub/AST-995/AST-1000-restore-stage-dispatch-provision-helper` @ `ffe47510` (`merge-tests(AST-1000): origin/tests b9dd9e35`)
**Bible:** `docs/test-bible/data/database/dispatch_tasks.md` shasum `8fb36bc488b31eef1f4d7cccf9f545abaf748af8`

Assignee → Ada for `test-child`.

— Betty

#### ada — 2026-07-28T04:54:36.364Z
[qa-handoff]

@Betty White

**Commands (manifest as posted):**
1. `ASTRAL_PYTHON=/home/susan/astral/.venv/bin/python ./scripts/testing/run_component_tests.sh tests/component/data/database/test_dispatch_tasks.py::TestAst972CandidateStageEligibility -q` → **2 failed / 2 passed**
2. same runner `…/test_dispatcher.py::TestAst972CandidateStageDispatch -q` → **6 passed**

**Failures (not listing helper):**
- `test_stage_resume_eligible_when_state_matches` — `count_eligible_for_dispatch_task` returns `0` for `candidate_requested_resume` / `REQUESTED_RESUME`
- `test_stage_artifacts_eligible_includes_retry` — same for `candidate_requested_artifacts` / `REQUESTED_ARTIFACTS_RETRY`

**Listing contract (this ticket) is green on the same class:** `test_list_candidate_ids_with_dispatch_tasks` (incl. your empty-list AC4 assert) and `test_unknown_candidate_task_key_returns_zero` passed; dispatcher provision/scheduler class is green.

**Why test/manifest, not product fix here:** AST-1000 plan Files Changed is only restore of `list_candidate_ids_with_dispatch_tasks`. Current `count_eligible_for_dispatch_task` candidate branch routes *all* candidate tasks through inflow discovery (`return count_candidate_inflow_discovery_eligible(...)`) — the AST-972 stage_keys split is gone (same composite drop pattern as the listing helper). Fixing eligibility would expand beyond the plan bible without a new stage / Files Changed row.

**Please:** narrow manifest line 1 to the listing node(s) for AST-1000 (e.g. `…::TestAst972CandidateStageEligibility::test_list_candidate_ids_with_dispatch_tasks`), **or** open/expand product scope if Chuckles wants the stage eligibility branch restored on this child. Reassign Ada when the manifest matches plan scope.

`origin/sub/AST-995/AST-1000-restore-stage-dispatch-provision-helper` @ `0425993e`

#### betty — 2026-07-28T04:51:53.927Z
## QA test manifest — AST-1000

**Publish:** `origin/sub/AST-995/AST-1000-restore-stage-dispatch-provision-helper` @ `0425993e` (`merge-tests(AST-1000): origin/tests 4c9d0dcf6ca6ebdc79e06e9eb75288a469b3d92b`)

### Classification

1. **Existing coverage (bible-backed):** AST-972 listing + provision/scheduler paths remain the contract for the restored helper.
2. **Broken / obsolete:** none — attribute restore; no scenario weakened.
3. **Gaps closed this pass:** empty DISTINCT assert on `test_list_candidate_ids_with_dispatch_tasks` (AC4).

### Manifest (test-child)

1. `./scripts/testing/run_component_tests.sh tests/component/data/database/test_dispatch_tasks.py::TestAst972CandidateStageEligibility -q`
2. `./scripts/testing/run_component_tests.sh tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch -q`

**Pass criterion:** pytest green on both lines — not zero-arg harness / branch-lock gate.

**Bible (publish tip):**
`docs/test-bible/data/database/dispatch_tasks.md` shasum `e4038bf2f9a8a712a2fd08f0458dda191eecdfc2`

— Betty

#### joan — 2026-07-28T04:42:40.668Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1000
**Overall:** APPROVED

## Traceability

| Parent AC | Plan stage(s) |
|-----------|---------------|
| 1. No AttributeError for `list_candidate_ids_with_dispatch_tasks` on boot | Stage 1 — restore public attribute |
| 2. No `AST-972 stage dispatch provision failed` from missing helper | Stage 1 — provision call succeeds / empty loop; dispatcher try/except unchanged |
| 3. With ≥1 candidate owning dispatch_task, provision enumerates without AttributeError | Stage 1 — DISTINCT listing returns those ids; existing `ensure_*` iterates |
| 4. Empty candidate set: scheduler starts, no traceback from this path | Stage 1 — empty list → empty for-loop; no dispatcher edits |
| 5. Existing component coverage for listing/provision remains meaningful | Stage 1 — restores contract named by existing tests; Betty/test-child own green |

| Plan stage | Parent Purpose / Functional scope / AC |
|------------|----------------------------------------|
| Stage 1: Restore listing helper | Purpose: clean boot without AttributeError; Functional: listing contract restored + provision without AttributeError + scheduler continues; AC 1–5 |

## Statute verdicts

| id | verdict | one-line |
|----|---------|----------|
| orch.git.betty-merge-tests-one-sha | conforms | Plan leaves `tests/`/bible to Betty; no engineer merge-tests invent |
| orch.git.commit-vocabulary | conforms | Planned commit `code(AST-1000): …` matches vocabulary |
| orch.git.flow-direction-inviolable | conforms | Child publish-ref only; no reverse-flow proposed |
| orch.git.ftr-sub-topology | conforms | Work on `sub/AST-995/AST-1000-…` under parent ftr |
| orch.git.merge-on-checkout | conforms | Plan assumes normal sub checkout/merge workflow; no bypass |
| orch.git.no-cherry-pick-rebase-force | conforms | Exact restore via normal commit; no cherry-pick/rebase/force |
| orch.git.no-dev-agent-branches | conforms | Uses authoritative sub ref, not Linear agent branch |
| orch.git.one-epic-worktree-per-parent | conforms | Scoped to epic worktree `astral-AST-995/` |
| orch.git.three-permanent-branches | conforms | No new permanent branch proposed |
| orch.pipeline.call-susan-for-product-decisions | conforms | Restore-not-redesign; no product fork open |
| orch.pipeline.plan-is-bible | conforms | Single stage + exact SQL/body; actionable as bible |
| orch.pipeline.project-scoped-queues | conforms | Astral Foundation child; no cross-project queue abuse |
| orch.pipeline.status-gates-skill-entry | conforms | Presented at Plan Ready for validate-plan |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | Explicitly out of scope for engineer; existing coverage cited |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer remains Ada through build |
| orch.roles.engineer-assignee-through-resolve | conforms | Reassign to Ada on Plan Approved |
| orch.roles.pre-commit-path-bans | conforms | Touches only `src/data/database.py` (allowed for engineer) |
| astral.batch.batch-id-first | conforms | No new claim/get/clear API; listing helper only |
| astral.batch.batch-id-format | conforms | No batch_id generation/format change |
| astral.batch.claim-process-release | conforms | Does not select-and-process without claim; listing only |
| astral.batch.entity-agent-responses-latest-only | conforms | No agent_data / latest-refs surface |
| astral.config.config-source-of-truth | conforms | No new config keys/state sets |
| astral.config.pass-threshold-vs-score-floor | conforms | No scoring/dispatch floor changes |
| astral.git.betty-no-src-or-features | conforms | Engineer owns this `src/` restore; Betty not directed to edit src/features |
| astral.layers.import-direction | conforms | Data-layer-only edit; no new cross-layer imports |
| astral.standards.data-raises-caller-logs | conforms | Explicit no logging in data; dispatcher already logs |
| astral.standards.database-header-inventory | conforms | Uses existing `dispatch_task` (already inventoried); header unchanged |
| astral.standards.dry-and-focused-functions | conforms | Reuses `_ensure_dispatch_task_schema` / `_get_connection` / `_run_with_retry` |
| astral.standards.in-scope-only | conforms | Single helper restore; AST-973/871/Stytch/Vite excluded |
| astral.standards.no-cross-contamination | conforms | Stays inside data layer patterns |
| astral.standards.no-hardcoded-sets | conforms | No new state/magic sets |
| astral.standards.public-then-helpers | conforms | Public API placed between peer public list helpers |
| astral.state.core-decides-transitions | conforms | No state transitions introduced |
| astral.state.job-prior-states-enforced | conforms | No job state hop changes |

## Considered and excluded

**Considered:** orch.git.betty-merge-tests-one-sha, orch.git.commit-vocabulary, orch.git.flow-direction-inviolable, orch.git.ftr-sub-topology, orch.git.merge-on-checkout, orch.git.no-cherry-pick-rebase-force, orch.git.no-dev-agent-branches, orch.git.one-epic-worktree-per-parent, orch.git.three-permanent-branches, orch.pipeline.call-susan-for-product-decisions, orch.pipeline.plan-is-bible, orch.pipeline.project-scoped-queues, orch.pipeline.status-gates-skill-entry, orch.roles.archie-approves-statutes, orch.roles.betty-owns-test-tree, orch.roles.chuckles-never-ticket-assignee, orch.roles.engineer-assignee-through-resolve, orch.roles.pre-commit-path-bans, astral.batch.batch-id-first, astral.batch.batch-id-format, astral.batch.claim-process-release, astral.batch.entity-agent-responses-latest-only, astral.config.config-source-of-truth, astral.config.pass-threshold-vs-score-floor, astral.git.betty-no-src-or-features, astral.layers.import-direction, astral.standards.data-raises-caller-logs, astral.standards.database-header-inventory, astral.standards.dry-and-focused-functions, astral.standards.in-scope-only, astral.standards.no-cross-contamination, astral.standards.no-hardcoded-sets, astral.standards.public-then-helpers, astral.state.core-decides-transitions, astral.state.job-prior-states-enforced

**Excluded:**
- astral.agent.confidence-bounds — layers/paths miss data/`src/data/database.py`
- astral.agent.do-task-delegation — layers/paths miss data/`src/data/database.py`
- astral.agent.grade-vector-validation — layers/paths miss data/`src/data/database.py`
- astral.config.secrets-and-env-specific-from-environ — layers miss data
- astral.debug.no-repo-root-artifacts-dir — paths miss `src/data/database.py`
- astral.debug.spikes-under-debug-dir — paths miss `src/data/database.py`
- astral.docs.features-single-file-per-ticket — layers/paths miss data/`src/data/database.py`
- astral.git.engineer-test-tree-ban — paths miss test-tree (plan correctly does not touch tests)
- astral.layers.core-vs-external-bright-line — layers/paths miss data/`src/data/database.py`
- astral.layers.scripts-exempt-from-layer-rules — layers/paths miss scripts
- astral.layers.ui-config-driven-business-logic — layers/paths miss ui
- astral.patterns.coat-check-never-store-empty — layers/paths miss core
- astral.patterns.render-verdict-orchestrates-consult — layers/paths miss core
- astral.patterns.require-auth-on-protected-endpoints — layers/paths miss ui
- astral.standards.debug-contract-gated — layers miss data
- astral.standards.logging-via-utils — layers miss data
- astral.standards.utils-data-late-import-only — layers/paths miss utils
- astral.state.no-daisy-chain-in-run — layers/paths miss core
- astral.ui.frontend-file-placement — layers/paths miss ui
- astral.ui.naming-conventions — layers/paths miss ui
- astral.ui.single-gunicorn-worker — layers/paths miss ui/scripts/config

## Findings

None (fix-now / discuss / acceptable).

Self-assessment honest: Scope minor · Conf high · Risk low — matches single additive data-layer restore of known AST-972 body between `list_dispatch_tasks_for_candidate` and `count_dispatch_tasks_by_candidate` (helper currently absent on publish-ref).

— Joan
context_tokens≈45000

#### ada — 2026-07-28T03:10:36.072Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-995/AST-1000-restore-stage-dispatch-provision-helper/docs/features/foundation/ast-1000-restore-stage-dispatch-provision-helper.md

`origin/sub/AST-995/AST-1000-restore-stage-dispatch-provision-helper` @ `da6f591d`

**Scope:** minor — restore one public data-layer listing helper next to existing `dispatch_task` list APIs; dispatcher/config/AST-973 migration untouched.

**Conf:** high — AST-972 caller + SQL contract still present; git history (`2ce7a744`) has the exact body dropped by AST-973’s `database.py` rewrite.

**Risk:** low — additive attribute restore; empty DISTINCT result keeps boot scheduler start safe; wrong listing would only affect which scheduled candidates get REQUESTED_* upsert at boot.

---

# AST-1000: Restore stage-dispatch provision helper (getting a stack trace on localhost boot)

**Linear:** [AST-1000](https://linear.app/astralcareermatch/issue/AST-1000/restore-stage-dispatch-provision-helper-getting-a-stack-trace-on)
**Parent:** [AST-995](https://linear.app/astralcareermatch/issue/AST-995/getting-a-stack-trace-on-localhost-boot)
**Publish ref:** `sub/AST-995/AST-1000-restore-stage-dispatch-provision-helper`

Boot-time stage-dispatch provisioning (AST-972) still calls `database.list_candidate_ids_with_dispatch_tasks()` from `provision_candidate_stage_dispatch_tasks`, but that data-layer helper was dropped when AST-973 rewrote `src/data/database.py`. Restore the listing contract so localhost scheduler start no longer AttributeErrors / logs `AST-972 stage dispatch provision failed` for a missing attribute.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Restore public `list_candidate_ids_with_dispatch_tasks()` between `list_dispatch_tasks_for_candidate` and `count_dispatch_tasks_by_candidate` | data |

**Not touched:** `src/core/dispatcher.py` (caller + `start_scheduler` try/except already correct), `src/utils/config.py`, AST-973 migration helpers / `CANDIDATE_LEGACY_*`, craft/claim/resolve paths, Stytch/Vite, `tests/` / bible (Betty owns those; existing component tests already assert this contract).

## Stage 1: Restore listing helper

**Done when:** `hasattr(database, "list_candidate_ids_with_dispatch_tasks")` is true; calling it returns a `list[str]` of distinct non-empty `dispatch_task.candidate_id` values ordered ASC (empty list when none); `python -m compileall` on the touched file is clean. No dispatcher edits.

1. In `src/data/database.py`, immediately after `list_dispatch_tasks_for_candidate` and before `count_dispatch_tasks_by_candidate`, add exactly this public function (AST-972 contract from commit `2ce7a744` / `ae2d18ab` — restore, do not redesign):

   ```python
   def list_candidate_ids_with_dispatch_tasks() -> List[str]:
       """Distinct candidate_id values that already own ≥1 dispatch_task row."""
       def _with_conn() -> List[str]:
           conn = _get_connection()
           try:
               _ensure_dispatch_task_schema(conn)
               rows = conn.execute(
                   "SELECT DISTINCT candidate_id FROM dispatch_task "
                   "WHERE candidate_id IS NOT NULL AND TRIM(candidate_id) != '' "
                   "ORDER BY candidate_id ASC"
               ).fetchall()
               return [str(r[0]) for r in rows if r[0] is not None]
           finally:
               conn.close()
       return _run_with_retry(_with_conn)
   ```

2. Do **not** change the header table inventory unless `dispatch_task` is somehow missing (it is already listed). Do **not** add logging in the data layer (§1.5 — raise only; dispatcher already logs provision failures).

3. Do **not** edit `ensure_candidate_stage_dispatch_tasks`, `provision_candidate_stage_dispatch_tasks`, or `start_scheduler` — they already call this helper and catch exceptions with `_sched_log.exception("AST-972 stage dispatch provision failed")`.

4. Do **not** alter AST-973 behavior: leave `_legacy_candidate_migrate_conn`, `hard_delete_candidate`, `CANDIDATE_LEGACY_STATE_MAP` / trigger remaps, and ensure-time BC migration untouched.

5. Compile check: `python -m compileall -q src/data/database.py`. Fix only syntax/import errors introduced by this restore.

⚠️ **Decision:** Exact restore of the AST-972 SQL + `_run_with_retry` / `_ensure_dispatch_task_schema` wrapper rather than deriving ids from `count_dispatch_tasks_by_candidate().keys()`. Matches existing component contract (`tests/component/data/database/test_dispatch_tasks.py::test_list_candidate_ids_with_dispatch_tasks`) and the dispatcher monkeypatch surface; no new API shape.

**Commit message:** `code(AST-1000): restore list_candidate_ids_with_dispatch_tasks`

## Out of scope

- Redesigning candidate state machine (AST-871) or reopening AST-972 / AST-973 product scope
- Changing REQUESTED_* claim/resolve, craft prompts, or eligibility counts
- Stytch, Vite, unrelated boot messages
- Writing or patching `tests/` / `docs/test-bible/**` (engineer does not own the test tree; existing coverage already names this helper)

## Acceptance mapping

| AC | How this plan satisfies it |
|----|----------------------------|
| 1–2 | Attribute restored → provision path no longer AttributeErrors → no provision-failed traceback from that cause |
| 3 | Helper returns candidates that own ≥1 `dispatch_task` row; provision iterates them via existing `ensure_*` |
| 4 | Empty DISTINCT result → empty for-loop; scheduler thread still starts after the try/except |
| 5 | Existing tests that call / monkeypatch `list_candidate_ids_with_dispatch_tasks` regain a real attribute (Betty/test-child verify green) |

## Self-Assessment

**Scope:** minor — one public data-layer listing function restored next to existing `dispatch_task` list helpers; no core/UI/config changes.

**Conf:** high — caller and SQL contract already shipped under AST-972; git history preserves the exact implementation dropped by AST-973’s `database.py` rewrite.

**Risk:** low — additive restore of a missing attribute; wrong SQL would only affect which candidates get REQUESTED_* upsert at boot, not claim/resolve paths; empty DB remains safe.

## Code rules check

| Rule | Plan alignment |
|------|----------------|
| §1.3 DRY | Reuse `_ensure_dispatch_task_schema`, `_get_connection`, `_run_with_retry`; no parallel query helpers |
| §1.5 data raises / caller logs | No logging in restore; dispatcher provision try/except unchanged |
| §2.1 config SSoT | No new state sets or config keys |
| §2.4 batch | Listing only; claim/clear patterns untouched |
| §2.6 state machine | No state transitions |
| §3.3 imports | Data layer only; no new cross-layer imports |
| §3.5 / public-then-helpers | Placed with other public `dispatch_task` list APIs |

## Review (build stub)

**Built:** `origin/sub/AST-995/AST-1000-restore-stage-dispatch-provision-helper` @ `64a30851e469613f3e8e7e0b36e644d951afed54`.

**Stages delivered:**
- Stage 1: restore `list_candidate_ids_with_dispatch_tasks` in `src/data/database.py` — `64a30851e469613f3e8e7e0b36e644d951afed54`.

## Review (Radia — code-rubric.v1)

`[code-rubric] revision=1`

**Rubric:** code-rubric.v1  
**Ticket:** AST-1000  
**Publish ref:** `ffe47510942ce0acd50098fc02f6eadb0724c590` (`origin/sub/AST-995/AST-1000-restore-stage-dispatch-provision-helper`)  
**Overall:** DISCUSS

**Diff change set:** `src/data/database.py` (modify/data); `docs/features/foundation/ast-1000-restore-stage-dispatch-provision-helper.md` (add/docs); `docs/test-bible/data/database/dispatch_tasks.md` + `tests/component/data/database/test_dispatch_tasks.py` (modify/docs via Betty `merge-tests`).

### What’s solid

- Exact AST-972 body restored between `list_dispatch_tasks_for_candidate` and `count_dispatch_tasks_by_candidate` (byte-match to plan Stage 1).
- Data raises only — no data-layer logging; dispatcher provision caller untouched.
- Header inventory already lists `dispatch_task`; no new table.
- Engineer `code()` touched only `src/data/database.py`; bible/tests arrived via `merge-tests`.

### Findings

**discuss (C4 straggler):** `astral.debug.spikes-under-debug-dir` — Joan excluded (plan Files Changed = data only); three-dot diff includes `docs/features/**`. Re-score: **conforms** (plan doc is not a spike under `debug/`).

**discuss (C4 straggler):** `astral.docs.features-single-file-per-ticket` — Joan excluded; plan file is in the diff. Re-score: **conforms** (single `ast-1000-…` features file).

**discuss (C4 straggler):** `astral.git.engineer-test-tree-ban` — Joan excluded (plan said engineer would not touch tests); three-dot includes `tests/**` + `docs/test-bible/**` from Betty `merge-tests`. Re-score: **conforms** (engineer `code()` commit is src-only).

No fix-now. No product action required for the stragglers unless Archie wants plan-time exclusion notes refined for pipeline docs/tests paths.

### Recommended actions

- Implementer (`resolve-child`): acknowledge stragglers; no code change expected for CLEAN product restore.

## Resolution (2026-07-28 — resolve-child, Ada)

**Radia Overall:** DISCUSS (C4 stragglers only). **fix-now:** 0.

**Discuss handled:**
- Acknowledged three C4 stragglers (`astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`) — already re-scored **conforms** in Radia review; pipeline docs/tests paths vs plan-time product Files Changed, not product defects.
- No product code changes; no plan-time exclusion refinements (Archie did not ask).

**Publish tip after resolve:** see commit subject `resolve(AST-1000): — clean`.

**Tip rebuild (2026-07-28):** Restacked on `origin/ftr/AST-995-localhost-boot-stack-trace` for validate-sub-log (removed `Merge remote-tracking` / foreign AST-996..998 history; `plan()` subject; single `merge-tests` from `1150959778d4cfe0301a40cd280decb0a15ea0da`; empty `test()` — no product fixes).
