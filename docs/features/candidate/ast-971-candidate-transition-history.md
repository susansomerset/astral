<!-- linear-archive: AST-971 archived 2026-08-05 -->

## Linear archive (AST-971)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-971/candidate-transition-history-candidate-state-machine  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-871 — Candidate state machine  
**Blocked by / blocks / related:** parent: AST-871

### Description

## What this implements

Persist enter/exit history on each candidate transition with parity to job/company history for time-in-state reporting.

## Acceptance criteria

7. Every successful state change appends candidate transition history usable for prior/new state and time-in-state (feeds AST-869 State Progress later).

## Boundaries

Does **not** own state vocabulary (AST-970) or the Progress UI (AST-869).

## Notes for planning

Mirror job/company transition history shape enough for time-in-state. Depends on AST-970 transition API.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-871-candidate-state-machine`, child `sub/AST-871/<this-id>-candidate-transition-history`. Created at dispatch-parent.

### Comments

#### betty — 2026-07-24T00:59:34.615Z
[merge-child] blocked: git pull merge on sub — `Merge remote-tracking branch` in ftr..sub (47cd26d). Rewrite tip onto `origin/ftr/AST-871-candidate-state-machine`, cherry-pick only AST-971 labeled commits, force-with-lease push `origin/sub/AST-871/AST-971-candidate-transition-history`. @Hedy Lamarr

— Chuckles

#### radia — 2026-07-24T00:22:51.706Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-971
**Publish ref:** `origin/sub/AST-871/AST-971-candidate-transition-history` @ `d2ea15836202c1f588e9e8a231b2c267d104892f`
**Overall:** DISCUSS

Diff: `origin/dev...origin/sub/AST-871/AST-971-candidate-transition-history` — layers `core`/`data`/`utils`/`ui`/`docs` (+ Betty `tests`/`docs/test-bible`; includes blockedBy AST-970).

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | universal | conforms | Single `merge-tests(AST-971)` of `5c1584b` |
| orch.git.commit-vocabulary | universal | conforms | `code`/`docs`/`test`/`merge-tests` / merge blockedBy |
| orch.git.flow-direction-inviolable | universal | conforms | Child publish on `sub/AST-871/…` |
| orch.git.ftr-sub-topology | universal | conforms | Under parent AST-871 |
| orch.git.merge-on-checkout | universal | conforms | `origin/dev` + blockedBy 970 merges on tip |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No rewrite ops |
| orch.git.no-dev-agent-branches | universal | conforms | No agent long-lived branches |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Epic worktree `astral-AST-871` |
| orch.git.three-permanent-branches | universal | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Company-shaped history + null `batch_id` are plan Decisions |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–3 match plan bible |
| orch.pipeline.project-scoped-queues | universal | conforms | Untouched |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | No `canon/statutes/**` edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty `test`/`merge-tests` own bible+tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | Assignee remains Hedy |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Implementer stays assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | Path ownership respected across commits |
| astral.agent.confidence-bounds | scoped | conforms | No graded/confidence surface |
| astral.agent.do-task-delegation | scoped | conforms | No `do_task` path change |
| astral.agent.grade-vector-validation | scoped | conforms | No grade vectors |
| astral.batch.batch-id-first | scoped | conforms | No claim APIs; history `batch_id` null-only |
| astral.batch.batch-id-format | scoped | conforms | No batch_id minting |
| astral.batch.claim-process-release | scoped | conforms | No batch claim |
| astral.batch.entity-agent-responses-latest-only | scoped | conforms | Untouched |
| astral.config.config-source-of-truth | scoped | conforms | Validation stays on AST-970 `prior_states` |
| astral.config.pass-threshold-vs-score-floor | scoped | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | No secrets/env splits |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss |
| astral.debug.spikes-under-debug-dir | scoped | conforms | Feature plan under `docs/features/**` |
| astral.docs.features-single-file-per-ticket | scoped | conforms | AST-971 plan in `docs/features/candidate/` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commits are test-tree only |
| astral.git.engineer-test-tree-ban | scoped | conforms | Engineer `code`/`docs` leave tests/bible to Betty |
| astral.layers.core-vs-external-bright-line | scoped | conforms | Core appends; no external I/O |
| astral.layers.import-direction | scoped | conforms | data + core (+ merged 970 ui/utils) stay legal |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | Tip UI/config from AST-970; history ticket does not hardcode states in UI |
| astral.patterns.coat-check-never-store-empty | scoped | conforms | No coat-check keys |
| astral.patterns.render-verdict-orchestrates-consult | scoped | conforms | No consult orchestration |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | No new open endpoints |
| astral.standards.data-raises-caller-logs | scoped | conforms | Data persists caller history; core appends |
| astral.standards.database-header-inventory | scoped | conforms | Candidate header bullet includes `state_history` |
| astral.standards.debug-contract-gated | scoped | conforms | No new debug-contract emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | One `_append_candidate_state_history` helper |
| astral.standards.in-scope-only | scoped | conforms | Vocabulary/UI/dispatch left to siblings |
| astral.standards.logging-via-utils | scoped | conforms | No print/bare logging on history path |
| astral.standards.no-cross-contamination | scoped | conforms | Layered files only |
| astral.standards.no-hardcoded-sets | scoped | conforms | No new state sets |
| astral.standards.public-then-helpers | scoped | conforms | Private append helper beside initiate/transition |
| astral.standards.utils-data-late-import-only | scoped | conforms | Tip utils from AST-970; no new utils→data |
| astral.state.core-decides-transitions | scoped | conforms | Core appends once on sole transition path |
| astral.state.job-prior-states-enforced | scoped | conforms | Does not weaken job priors |
| astral.state.no-daisy-chain-in-run | scoped | conforms | One history entry per successful write |
| astral.ui.frontend-file-placement | scoped | not-applicable | paths miss (`src/ui/frontend/**`) |
| astral.ui.naming-conventions | scoped | conforms | No new frontend product files |
| astral.ui.single-gunicorn-worker | scoped | conforms | Untouched |

## Pattern conformance

none cited

## Plan adherence

Stages 1–3 match: column + header inventory + parse/save preserve semantics; company-shaped seed + sole-path append inside `transition_candidate_state`; `CANDIDATE_DATA_MODEL` documents column/shape. Self-Assessment Single-Component / high / Medium matches history footprint (tip also carries merged AST-970). Joan APPROVED @ `cb49511`.

## Findings

### discuss
1. **C4 stragglers** — Joan Excluded at plan time; tip includes blockedBy AST-970 + Betty tests so these score in-scope: `astral.git.engineer-test-tree-ban`, `astral.layers.ui-config-driven-business-logic`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.standards.utils-data-late-import-only`, `astral.ui.naming-conventions`, `astral.ui.single-gunicorn-worker`. All scored **conforms**. No product fix — acknowledge on resolve.

### advisory
1. CREATE TABLE candidate still `state … DEFAULT 'NEW'` (legacy default; AST-973 remap/defaults).

### fix-now
None.

## What’s solid

- Header inventory + `state_history` column; initiate seed; single append on validated transition write; delete/admin do not double-count; illegal hops write nothing.

## Notes

Joan Excluded set otherwise still `not-applicable`: `no-repo-root-artifacts-dir`, `scripts-exempt`, `frontend-file-placement`.

— Radia
context_tokens≈98000

#### betty — 2026-07-23T23:46:17.805Z
## QA test manifest — AST-971

`origin/sub/AST-871/AST-971-candidate-transition-history` @ `a7b1926` (`merge-tests(AST-971): origin/tests 5c1584b836ea01b24ee5896f5d035abe60c971da`)

### Run

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst971CandidateTransitionHistory \
  tests/component/core/test_candidate.py::TestInitiateCandidate \
  tests/component/core/test_candidate.py::TestTransitionCandidateStateSuccess \
  tests/component/core/test_candidate.py::TestDeleteCandidate \
  tests/component/core/test_candidate.py::TestAst970CandidateStateMachine \
  tests/component/data/database/test_candidates.py \
  tests/component/data/database/test_candidate_migrations.py \
  -q
```

### Coverage
1. **Create seed** — initiate writes one history entry (`from_state=""`, `to_state=NEW_CANDIDATE`, `batch_id=null`)
2. **Sole-path append** — successful `transition_candidate_state` writes `state` + `state_history` on the same `save_candidate` call (company-shaped entry)
3. **No double-append** — `delete_candidate` → transition once; illegal hops write nothing
4. **Data column** — insert default `[]`; persist list; preserve when omitted; overwrite when provided; bad JSON → `[]`
5. **Obsolete revise** — data-layer fixtures `NEW`/`PROFILE_READY` → `NEW_CANDIDATE`/`INTAKE_INITIATED`; AST-970 save asserts include `state_history`

### Bible shasums (`origin/sub/…`)
- `docs/test-bible/core/candidate.md` `ca12b62271c79a24ec3bf15b6bb7fd7334bfe9b8fa781998860ff8b5890186a5`
- `docs/test-bible/data/database/candidates.md` `858d7731967c890379416679f5b1d9d2f1483ac5bf4c05d6c6afd4f4b8d7bf1e`
- `docs/test-bible/data/database/candidate_migrations.md` `77ab93b6d1bb8ce6ac31b5159481b37a511754c06a7f165c2170e1a0745d340d`

— Betty

#### joan — 2026-07-23T23:22:00.470Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-971
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-871/AST-971-candidate-transition-history` @ `cb49511`
**Implementer:** Hedy Lamarr
**Plan Discuss:** round 1 completed (concern + reply); fix-now closed

## Traceability

### Parent / child AC → plan stages

| AC | Coverage |
| -- | -- |
| Parent/child **#7** — every successful state change appends history (prior/new + timestamps; feeds AST-869) | Stage 1 column + header inventory + parse/save; Stage 2 seed + sole-path append in `transition_candidate_state`; Stage 3 data-model doc |
| Parent AC 1–6, 8–10 | N/A — Boundaries: vocabulary AST-970; Progress UI AST-869; dispatch/migration siblings |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 Data `state_history` + header inventory | Transition history storage; company/job parity; statute header inventory |
| 2 Core append once on sole transition path | AC#7; §2.6; no double-count with AST-970 delete/admin routing |
| 3 CANDIDATE_DATA_MODEL | Contract for AST-869 readers |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge/test SHA work |
| orch.git.commit-vocabulary | conforms | Plan-only |
| orch.git.flow-direction-inviolable | conforms | Child `sub/AST-871/…` publish ref |
| orch.git.ftr-sub-topology | conforms | Under parent ftr AST-871 |
| orch.git.merge-on-checkout | conforms | No merge steps claimed |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrites |
| orch.git.no-dev-agent-branches | conforms | No agent long-lived branches |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree assumed |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Company-shaped history + null batch_id are engineering parity |
| orch.pipeline.plan-is-bible | conforms | Single feature plan file |
| orch.pipeline.project-scoped-queues | conforms | Untouched |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready re-validate after discuss |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | Explicitly no tests/ |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Hedy |
| orch.roles.engineer-assignee-through-resolve | conforms | Returns to Hedy on APPROVED |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No grades |
| astral.agent.do-task-delegation | conforms | No do_task |
| astral.agent.grade-vector-validation | conforms | No vectors |
| astral.batch.batch-id-first | conforms | No claim APIs; batch_id key null-only |
| astral.batch.batch-id-format | conforms | No batch_id minting |
| astral.batch.claim-process-release | conforms | No batch claim |
| astral.batch.entity-agent-responses-latest-only | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | Validation stays on AST-970 prior_states |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets |
| astral.debug.spikes-under-debug-dir | conforms | Feature doc path |
| astral.docs.features-single-file-per-ticket | conforms | Plan under docs/features/candidate/ |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned |
| astral.layers.core-vs-external-bright-line | conforms | No external I/O |
| astral.layers.import-direction | conforms | data + core only |
| astral.patterns.coat-check-never-store-empty | conforms | N/A |
| astral.patterns.render-verdict-orchestrates-consult | conforms | N/A |
| astral.standards.data-raises-caller-logs | conforms | Data persists; core appends |
| astral.standards.database-header-inventory | conforms | Stage 1 step 2 updates candidate header bullet with state_history |
| astral.standards.debug-contract-gated | conforms | No new debug contract |
| astral.standards.dry-and-focused-functions | conforms | One append helper; company-shaped reuse |
| astral.standards.in-scope-only | conforms | Vocabulary/UI/dispatch explicitly out |
| astral.standards.logging-via-utils | conforms | No print/bare logging |
| astral.standards.no-cross-contamination | conforms | Layered files only |
| astral.standards.no-hardcoded-sets | conforms | No new state sets |
| astral.standards.public-then-helpers | conforms | Private append helper + existing public writers |
| astral.state.core-decides-transitions | conforms | Core appends; data does not auto-invent history |
| astral.state.job-prior-states-enforced | conforms | Does not weaken job priors |
| astral.state.no-daisy-chain-in-run | conforms | One history entry per successful write |

## Considered and excluded

**Considered:** all rows above (47).

**Excluded:**
- `astral.debug.no-repo-root-artifacts-dir` — paths miss
- `astral.git.engineer-test-tree-ban` — paths miss
- `astral.layers.scripts-exempt-from-layer-rules` — layers/paths miss
- `astral.layers.ui-config-driven-business-logic` — layers/paths miss
- `astral.patterns.require-auth-on-protected-endpoints` — layers/paths miss
- `astral.standards.utils-data-late-import-only` — layers/paths miss
- `astral.ui.frontend-file-placement` — layers/paths miss
- `astral.ui.naming-conventions` — layers/paths miss
- `astral.ui.single-gunicorn-worker` — layers/paths miss

## Findings

### fix-now
None. Round-1 fix-nows closed: (1) header inventory step for `candidate.state_history`; (2) sole-path append inside `transition_candidate_state` — no double-append on delete/admin.

### discuss (resolved — non-blocking)
1. Validation language points at AST-970 `prior_states` (not retired tuple list).
2. `batch_id: null` = no batch for AST-869 readers.

### acceptable
- Company-shaped entries; no data-layer auto-append; Single-Component / high / Medium honest.

**Self-assessment:** Single-Component / high / Medium — honest.

— Joan
context_tokens≈88000

#### joan — 2026-07-23T23:19:45.272Z
[validate-plan] blocked — assignee gate

Status is **Plan Ready** (post Plan Discuss r1), but assignee is still **Hedy Lamarr**, not Joan.

Chuckles must assign **Joan** before re-validate. Prior note: revise @ `cb49511` addresses both r1 fix-nows and is ready to score once assigned.

— Joan
context_tokens≈82000

#### joan — 2026-07-23T23:18:28.393Z
[validate-plan] blocked — assignee gate

Status is **Plan Ready** (post Plan Discuss r1), but assignee is **Hedy Lamarr**, not Joan.

Chuckles must assign **Joan** before re-validate. Round-1 reply + plan revise @ `cb49511` look ready to score once assigned.

— Joan
context_tokens≈75000

#### hedy — 2026-07-23T23:13:10.642Z
[plan-discuss] round=1 reply

Addressed both fix-now items on `origin/sub/AST-871/AST-971-candidate-transition-history` @ `cb49511` (clean tip: `5f08a35` + this revise only).

**Delta**
1. **Header inventory** — Stage 1 step 2 (same change as the column) extends the `database.py` `candidate — …` inventory bullet to include `state_history` (JSON array); Files Changed row calls it out.
2. **Sole-path append** — Stage 2 rewritten: append exactly once inside `transition_candidate_state` on the same `save_candidate` that writes `state`; seed on initiate only; **do not** re-append in `delete_candidate` / `save_candidate_admin` because AST-970 routes those through transition. Residual direct `save_candidate(..., state=)` only if still present post-970 (else stop/comment). Dropped the soft-delete “validation-bypass” claim.

Also: validation language points at AST-970 `prior_states` (not retired tuple list); `batch_id: null` = no batch for AST-869 readers.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-871/AST-971-candidate-transition-history/docs/features/candidate/ast-971-candidate-transition-history.md

Returning to **Plan Ready** for re-validate.

— Hedy

#### joan — 2026-07-23T23:07:32.361Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-971
**Overall:** REVISE
**Publish ref:** `origin/sub/AST-871/AST-971-candidate-transition-history`
**Implementer:** Hedy Lamarr

## Traceability

### Parent / child AC → plan stages

| AC | Coverage |
| -- | -- |
| Parent/child **#7** — every successful state change appends history (prior/new + timestamps for time-in-state; feeds AST-869) | Stage 1 column + parse/save; Stage 2 seed + append on transition/delete/admin; Stage 3 data-model doc |
| Parent AC 1–6, 8–10 | N/A — Boundaries: vocabulary AST-970; Progress UI AST-869; dispatch/migration siblings |

### Plan stages → definition

| Stage | Maps to |
| -- | -- |
| 1 Data `state_history` | Functional scope transition history; New pattern #2; company/job parity storage |
| 2 Core append on successful state writes | AC#7; §2.6 core records; no Progress UI |
| 3 CANDIDATE_DATA_MODEL | Doc so AST-869 can read the contract |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| orch.git.betty-merge-tests-one-sha | conforms | No Betty merge/test SHA work |
| orch.git.commit-vocabulary | conforms | Plan-only |
| orch.git.flow-direction-inviolable | conforms | Child `sub/AST-871/…` publish ref |
| orch.git.ftr-sub-topology | conforms | Under parent ftr AST-871 |
| orch.git.merge-on-checkout | conforms | No merge steps |
| orch.git.no-cherry-pick-rebase-force | conforms | No rewrites |
| orch.git.no-dev-agent-branches | conforms | No agent long-lived branches |
| orch.git.one-epic-worktree-per-parent | conforms | Epic worktree assumed |
| orch.git.three-permanent-branches | conforms | No new permanent branches |
| orch.pipeline.call-susan-for-product-decisions | conforms | Company-shaped history is an engineering parity choice, not a missing product fork |
| orch.pipeline.plan-is-bible | conforms | Single feature plan file |
| orch.pipeline.project-scoped-queues | conforms | Untouched |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready path |
| orch.roles.archie-approves-statutes | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | conforms | Explicitly no tests/ |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Hedy |
| orch.roles.engineer-assignee-through-resolve | conforms | Returns to Hedy on REVISE |
| orch.roles.pre-commit-path-bans | conforms | No banned paths |
| astral.agent.confidence-bounds | conforms | No grades |
| astral.agent.do-task-delegation | conforms | No do_task |
| astral.agent.grade-vector-validation | conforms | No vectors |
| astral.batch.batch-id-first | conforms | No claim APIs; `batch_id` key null-only |
| astral.batch.batch-id-format | conforms | No batch_id minting |
| astral.batch.claim-process-release | conforms | No batch claim |
| astral.batch.entity-agent-responses-latest-only | conforms | Untouched |
| astral.config.config-source-of-truth | conforms | No new behavior literals outside config; validation stays AST-970 |
| astral.config.pass-threshold-vs-score-floor | conforms | Untouched |
| astral.config.secrets-and-env-specific-from-environ | conforms | No secrets |
| astral.debug.spikes-under-debug-dir | conforms | Feature doc path |
| astral.docs.features-single-file-per-ticket | conforms | Plan under docs/features/candidate/ |
| astral.git.betty-no-src-or-features | conforms | Engineer-owned |
| astral.layers.core-vs-external-bright-line | conforms | No external I/O |
| astral.layers.import-direction | conforms | data + core only |
| astral.patterns.coat-check-never-store-empty | conforms | N/A |
| astral.patterns.render-verdict-orchestrates-consult | conforms | N/A |
| astral.standards.data-raises-caller-logs | conforms | Data persists; core appends |
| astral.standards.database-header-inventory | violates | New `candidate.state_history` column planned without an explicit header-inventory update step |
| astral.standards.debug-contract-gated | conforms | No new debug contract |
| astral.standards.dry-and-focused-functions | conforms | One append helper; company-shaped reuse |
| astral.standards.in-scope-only | conforms | Vocabulary/UI/dispatch explicitly out |
| astral.standards.logging-via-utils | conforms | No print/bare logging |
| astral.standards.no-cross-contamination | conforms | Layered files only |
| astral.standards.no-hardcoded-sets | conforms | No new state sets |
| astral.standards.public-then-helpers | conforms | Private append helper + existing public writers |
| astral.state.core-decides-transitions | conforms | Core appends; data does not auto-invent history |
| astral.state.job-prior-states-enforced | conforms | Does not weaken job priors; candidate validation deferred to AST-970 |
| astral.state.no-daisy-chain-in-run | conforms | One history entry per successful write |

## Considered and excluded

**Considered:** all rows above (47).

**Excluded:**
- `astral.debug.no-repo-root-artifacts-dir` — paths miss
- `astral.git.engineer-test-tree-ban` — paths miss
- `astral.layers.scripts-exempt-from-layer-rules` — layers/paths miss
- `astral.layers.ui-config-driven-business-logic` — layers/paths miss
- `astral.patterns.require-auth-on-protected-endpoints` — layers/paths miss
- `astral.standards.utils-data-late-import-only` — layers/paths miss
- `astral.ui.frontend-file-placement` — layers/paths miss
- `astral.ui.naming-conventions` — layers/paths miss
- `astral.ui.single-gunicorn-worker` — layers/paths miss

## Findings

### fix-now
1. **Location:** Stage 1 / `src/data/database.py` Files Changed
   **Finding:** Plan adds `state_history` to the candidate schema and `save_candidate` but never updates the module **header inventory** (candidate bullet still omits `state_history`). Statute `astral.standards.database-header-inventory` conforming example: column change updates schema helpers **and** header inventory in the same change.
   **Recommendation:** Add an explicit Stage 1 step to extend the `candidate — …` header line to include `state_history` (JSON array).

2. **Location:** Stage 2 steps 7–9 vs blockedBy AST-970
   **Finding:** Plan assumes `delete_candidate` remains a validation-bypass direct DELETED write and that admin state overrides still flow through `save_candidate_admin`. AST-970’s plan routes **both** through `transition_candidate_state`. If 970 lands first (required), appending in transition **and** again in delete/admin double-counts AC#7; step 8’s “validation-bypass” sentence becomes false.
   **Recommendation:** Rewrite Stage 2 so history appends exactly once per successful state change on the **sole** write path AST-970 leaves (append inside `transition_candidate_state`; create seed on initiate). For `delete_candidate` / admin: if they call transition, do **not** append again; if any residual direct `save_candidate(..., state=)` path remains after 970, keep a single guarded append there. Drop the hard claim that soft-delete bypasses validation unless post-970 code still does.

### discuss
1. Step 7 still cites today’s `candidate_state_transitions` tuple list — fine as “current”, but keep the plan’s own stop-rule if AST-970 renames the API (already stated in Dependency).
2. `batch_id` always-null until AST-972 is acceptable; confirm AST-869 readers treat null as “no batch”.

### acceptable
- Company-shaped `{from_state,to_state,timestamp,batch_id}` over job-only `to_state` matches parent prior/new need.
- No auto-append in data layer matches §2.6 and company/job practice.
- Self-assessment Single-Component / high / Medium is honest.

Update the plan on the publish ref, then Plan Ready + Joan for re-validate.

— Joan
context_tokens≈58000

#### joan — 2026-07-23T23:02:50.777Z
[validate-plan] blocked — assignee gate

Status is **Plan Ready**, but assignee is **Hedy Lamarr**, not Joan.

Chuckles must assign **Joan** (`susan+joan@susansomerset.com`) before validate-plan runs. No rubric pass until then.

— Joan
context_tokens≈14000

#### hedy — 2026-07-23T22:57:45.511Z
Plan published on `origin/sub/AST-871/AST-971-candidate-transition-history` @ `5f08a35`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-871/AST-971-candidate-transition-history/docs/features/candidate/ast-971-candidate-transition-history.md

**Self-assessment**
- **Scope:** Single-Component — candidate `state_history` column + core append on transition/delete/admin state writes; no UI/dispatch/vocabulary.
- **Conf:** high — mirrors company/job `transition_*_state` history append; `save_candidate` already bumps `state_changed_at`.
- **Risk:** Medium — missing/wrong history breaks AST-869 time-in-state and future batch anchoring; illegal transitions must still write nothing.

**Binding choices:** company-shaped entries (`from_state`/`to_state`/`timestamp`/`batch_id`); `batch_id` key always present (null until AST-972); history only in core write paths, not auto-append in data layer. Depends on AST-970 transition API — no parallel transition path.

---

# AST-971 — Candidate transition history

**Linear:** [AST-971](https://linear.app/astralcareermatch/issue/AST-971/candidate-transition-history-candidate-state-machine)  
**Parent:** [AST-871](https://linear.app/astralcareermatch/issue/AST-871/candidate-state-machine)  
**Publish ref:** `origin/sub/AST-871/AST-971-candidate-transition-history`

Persist enter/exit history on every successful candidate state change with parity to job/company history so prior state, new state, and timestamps support time-in-state reporting (AST-869 State Progress later). This ticket does **not** own the state vocabulary or transition allow-list (AST-970) and does **not** build the Progress UI (AST-869).

**Dependency:** blockedBy AST-970. Build against the sole validated transition API AST-970 leaves in `src/core/candidate.py` (`transition_candidate_state`, `prior_states` enforcement). Do not invent a parallel transition path. If AST-970 renames/moves that API, stop and comment on AST-871 — do not improvise.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add `candidate.state_history` column (CREATE + idempotent ALTER); update module **header inventory** candidate bullet to include `state_history`; parse JSON in `_parse_candidate_row`; accept optional `state_history` on `save_candidate` (caller-managed overwrite, preserve when omitted) | data |
| `src/core/candidate.py` | Seed history on create; append company-shaped history **once** inside `transition_candidate_state` on success (AST-970 routes delete + admin state overrides through that sole path) | core |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Document `state_history` column + entry shape | docs |

## Stage 1: Data layer — `state_history` on candidate

**Done when:** Fresh and existing candidate DBs expose a parsed `state_history` list on `get_candidate` / `list_candidates`; `save_candidate(..., state_history=[...])` persists the list; omitting `state_history` on update leaves the existing column unchanged; the `database.py` header inventory candidate line lists `state_history`.

1. In `src/data/database.py`, extend `_ensure_candidate_schema`:
   - On **CREATE TABLE candidate**, add column `state_history TEXT DEFAULT '[]'` after `state` (or after `state_changed_at` — either is fine; keep column order consistent with the ALTER list).
   - On existing DBs, add to the idempotent migration loop: `("state_history", "TEXT DEFAULT '[]'")` alongside `candidate_api_key` / `agent_responses`.
2. In the same change, update the module **header inventory** (top-of-file `Tables used (inventory):` block). Extend the `candidate — …` bullet so it includes `state_history` (JSON array), same style as the `job` / `company` bullets that already list `state_history`. Statute: `astral.standards.database-header-inventory`.
3. In `_parse_candidate_row`, parse `state_history` the same way company/job rows do: `json.loads` → `list`; on missing/invalid → `[]`.
4. In `save_candidate`, add keyword-only arg `state_history: Optional[List[Dict[str, Any]]] = None`:
   - **INSERT (new PK):** persist `json.dumps(state_history if state_history is not None else [])` into the new column (include column in the INSERT column list).
   - **UPDATE:** if `state_history is not None`, set `state_history = ?` with `json.dumps(state_history)`; if `None`, do **not** touch the column (preserve existing), matching `save_job` caller-managed overwrite semantics.
   - Do **not** auto-append inside the data layer — core owns append (rules §2.6: data accepts state from caller; history recording stays in core next to transition).
5. Keep existing auto-`state_changed_at` behavior when `state` changes (already present). History append does not replace `state_changed_at`.

⚠️ **Decision:** Column on `candidate`, not a separate history table — mirrors job/company `state_history` JSON arrays so AST-869 can reuse the same read pattern.

## Stage 2: Core — append history once on the sole transition path

**Done when:** Creating a candidate seeds one history entry for the initial state; every successful `transition_candidate_state` appends exactly one entry with prior + new state + timestamp; delete/admin state changes that go through that function do not double-append; illegal transitions still raise and write nothing.

### Entry shape (binding)

Every history entry is a dict:

```json
{
  "from_state": "<prior state string, empty string on create seed>",
  "to_state": "<new state>",
  "timestamp": "<UTC 'YYYY-MM-DD HH:MM:SS' via same clock as other candidate writes>",
  "batch_id": null
}
```

- Use **company** parity (`from_state` + `to_state` + `timestamp` + `batch_id`), not job-only `to_state`. Parent AC requires prior/new for time-in-state; consecutive timestamps give duration in the exited state (`from_state` of entry N = time from entry N-1 `timestamp` to entry N `timestamp`).
- `batch_id`: always include the key. Read `candidate.get("batch_id")` if present; otherwise `null`. **Do not** add a `batch_id` column in this ticket (dispatch claim is AST-972). AST-869 / other readers must treat `null` as “no batch” (not an error). Forward-compatible with later batch anchoring (AST-769 noted candidates lack history today).
- Timestamp format: same UTC string style already used in `transition_job_state` / `transition_company_state` / `_utc_now()` for candidates — pick the existing helper used by `save_candidate` / nearby candidate core code and use it consistently in this module (do not invent a second clock format).

⚠️ **Decision:** Prefer company-shaped entries over job-only `to_state` so prior state is explicit without scanning the previous row. AST-869 can still compute time-in-state from consecutive timestamps.

### Helpers and call sites

6. In `src/core/candidate.py`, add a small private helper (name e.g. `_append_candidate_state_history`) that:
   - Takes `candidate: dict`, `from_state: str`, `to_state: str`, `timestamp: str`.
   - Returns a **new** list = `list(candidate.get("state_history") or [])` + one entry shaped as above.
   - Does not write to the DB itself.
7. **`initiate_candidate`:** seed history for the initial state AST-970 defines (`CANDIDATE_CONFIG["initial_state"]` / `NEW_CANDIDATE`). Prefer a single INSERT that includes both `state` and `state_history` with one seed entry: `from_state=""`, `to_state=<initial>`, `timestamp=now`, `batch_id=null`. Create-then-update is fine if INSERT shape is awkward. Do not double-seed on re-call (if initiate always inserts fresh, keep that).
8. **`transition_candidate_state`:** keep AST-970’s validation (`to_state in CANDIDATE_STATES` + `prior_states` / `_candidate_state_allowed` — not the retired `candidate_state_transitions` tuple list). On success only:
   - `history = _append_candidate_state_history(candidate, from_state, to_state, now)`
   - Pass `state_history=history` on the same `database.save_candidate` call that writes `state=to_state` (AST-970’s plan writes state here; this ticket adds the history kwarg to that write — do not add a second save solely for history).
   - Preserve AST-970 side effects already in that function (e.g. DELETED reap timer start) — history append does not replace them.
   - Do not change validation rules, allow-lists, or vocabulary in this ticket.
9. **`delete_candidate` / admin state overrides (post-AST-970):** AST-970 routes both through `transition_candidate_state` (`delete_candidate` → `transition_candidate_state(..., "DELETED")`; admin API calls `transition_candidate_state` instead of `save_candidate_admin(..., state=...)`). **Do not** append history again in `delete_candidate` or `save_candidate_admin`. History for those hops is recorded exactly once inside `transition_candidate_state` (step 8).
10. **Residual direct state writes:** After merging AST-970, if any call site still does `database.save_candidate(..., state=...)` without going through `transition_candidate_state` (should be none for product state changes), add a single guarded append at that residual site only — or stop and comment on AST-871 if a surprising bypass remains. Do not sprinkle appends “just in case” on every wrapper.
11. Do **not** append history for `candidate_data`-only or `candidate_api_key`-only saves.
12. Do **not** build AST-869 UI, reports, or API endpoints that aggregate time-in-state.

⚠️ **Decision:** Exactly one history append per successful state change, on the sole AST-970 transition write path. Matches job/company (`transition_*_state` appends; wrappers that call transition do not re-append). Soft-delete is **not** a validation bypass after AST-970 (`DELETED.prior_states is None` allows entry via transition).

## Stage 3: Data model doc

**Done when:** `CANDIDATE_DATA_MODEL.md` documents the column and entry shape so AST-869 / future readers do not reverse-engineer from code.

13. In `docs/features/candidate/CANDIDATE_DATA_MODEL.md`, under **Candidate table (columns)**, add:
    - **state_history** — JSON array of `{from_state, to_state, timestamp, batch_id}`; appended by core on successful `transition_candidate_state` (and create seed) (AST-971). `batch_id` may be null until candidate batch claim exists; readers treat null as no batch.
14. In the **State machine** section, add one sentence: successful transitions append `state_history` (prior/new + timestamp) for time-in-state; Progress UI remains AST-869.

## Out of scope (do not do)

- AST-970 vocabulary / `prior_states` / transition allow-list changes
- AST-972 dispatch claim / stale aging / `batch_id` column
- AST-973 legacy row remaps
- AST-869 Progress UI
- Changing company or job history shapes
- Writing or editing `tests/` (Betty owns tests)

## Self-Assessment

**Scope:** `Single-Component` — candidate data column (+ header inventory) + core append inside the sole transition path; no UI, no dispatch, no sibling vocabulary work.

**Conf:** `high` — mirrors existing `transition_company_state` / `transition_job_state` history append; AST-970 already designates `transition_candidate_state` as the sole state-write path for delete/admin; gap is the missing column and core append.

**Risk:** `Medium` — wrong or double appends break future AST-869 time-in-state and agent batch anchoring; illegal transitions must still fail closed with no partial history write. Vocabulary drift from AST-970 is a merge-order risk, not a design unknown.

## Code rules check

- §2.1 / §2.6: no new hardcoded state lists; validation stays on AST-970’s config-backed `prior_states` API.
- §2.6: core decides/records transitions; data layer only persists caller-supplied `state` + `state_history`.
- §1.3 DRY: one append helper; reuse existing UTC timestamp helper; do not fork a second history format.
- §3.3 / §3.5: no new modules; names follow `state_history` / `from_state` / `to_state` already used for company.
- `astral.standards.database-header-inventory`: Stage 1 step 2 updates the candidate header bullet with `state_history`.

## Revisions

### Revision 1 — 2026-07-23

Driven by: Joan `[plan-discuss] round=1 concern` REVISE — (1) missing `database.py` header-inventory update for `candidate.state_history`; (2) Stage 2 double-append risk because AST-970 routes `delete_candidate` + admin state overrides through `transition_candidate_state`.

Changes:
- Stage 1: explicit header-inventory step; Files Changed row mentions it.
- Stage 2: history appends exactly once inside `transition_candidate_state`; create seed on initiate; delete/admin do not re-append when they call transition; residual direct `save_candidate(..., state=)` only if still present post-970.
- Dropped hard claim that soft-delete bypasses validation (false after AST-970).
- Step 8 validation language points at AST-970 `prior_states` (not retired tuple list); Dependency stop-rule unchanged.
- Noted `batch_id: null` means “no batch” for AST-869 readers.

## Review

- **Publish ref:** `origin/sub/AST-871/AST-971-candidate-transition-history`
- **Build:** `2d07385701e59c0f0d98118d568ea0d6a83e1478`

### Radia code-rubric.v1 (revision=1)

**Overall:** DISCUSS  
**Publish tip reviewed:** `47cd26ddc6f36575bc1330f50b8b856811849d83` (`origin/dev...origin/sub/AST-871/AST-971-candidate-transition-history`)

**What’s solid**
- `candidate.state_history` column + header inventory; parse/save preserve-when-omitted; no data-layer auto-append.
- Company-shaped seed on initiate; sole-path append inside `transition_candidate_state` (same `save_candidate` as state); delete/admin do not double-append.
- Data-model docs cover column + entry shape for AST-869.

**Issues**
- **discuss (C4 stragglers):** Joan Excluded several scoped statutes at plan time; tip includes blockedBy AST-970 + Betty tests so these score in-scope: `engineer-test-tree-ban`, `ui-config-driven-business-logic`, `require-auth-on-protected-endpoints`, `utils-data-late-import-only`, `ui.naming-conventions`, `ui.single-gunicorn-worker`. Substance **conforms** (no product fix).
- **advisory:** CREATE TABLE candidate still `state … DEFAULT 'NEW'` (legacy default; remap/defaults are AST-973).

**Recommended actions**
- Engineer: acknowledge C4 stragglers on resolve; no history-path code change required.

## Resolution

**Date:** 2026-07-24  
**Publish tip before resolve:** `d2ea158` (Radia `docs(AST-971): Radia review — findings`)  
**Outcome:** clean — no product code changes

### Radia findings addressed

- **fix-now:** none.
- **discuss (C4 stragglers):** Acknowledged. Joan Excluded those statutes at plan time; tip carries blockedBy AST-970 + Betty tests so Radia scored them in-scope and **conforms**. No history-path or product change required.
- **advisory:** CREATE TABLE `candidate.state … DEFAULT 'NEW'` left as-is — legacy default remaps/defaults are AST-973 scope, not this ticket.

### Commits

- `resolve(AST-971): — clean` — Resolution section only (this commit).

