<!-- linear-archive: AST-990 archived 2026-08-05 -->

## Linear archive (AST-990)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-990/align-integration-nav-scenario-with-current-candidate-states  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-988 — Integration tests are failing on GitHub  
**Blocked by / blocks / related:** parent: AST-988

### Description

## What this implements

Restores a green integration harness: the candidate nav scenario seeds an early-lifecycle candidate state that is **valid in the current registry** and still hides the Jobs nav group. No product behavior change — test-tree / harness alignment only (Betty commits tests via qa).

## Acceptance criteria

1. GitHub Actions **Integration tests** job is green on the landed fix (harness exit 0; no invalid-state errors).
2. The nav scenario still proves: with an early-lifecycle candidate state from the live registry, the Jobs nav group is absent; with the seeded active-search candidate, Jobs / in-review stays enabled.

## Boundaries

* Does **not** change the candidate state registry, transition rules, or nav_config product behavior.
* Does **not** own Betty agent/skills monitoring (AST-989) or Joan operator automation.
* Does **not** expand integration scenario coverage beyond fixing registry drift.

## Notes for planning

* Failure: `tests/integration/scenarios/test_candidate_nav_api.py` still uses retired state `NEW`; registry requires `NEW_CANDIDATE` (or another early-lifecycle state that hides Jobs).
* Entry point: `./scripts/testing/run_integration_tests.sh` (GHA workflow).
* Betty owns `tests/` commits via qa-child; engineer plan/build should avoid inventing product changes.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-988-integration-tests-are-failing-on-github`, child `sub/AST-988/AST-990-align-integration-nav-scenario-with-current-candidate-states`. Created at **dispatch-parent**. Publish with `git push origin HEAD:<publish-ref>` — never Linear `gitBranchName` when it disagrees.

### Comments

#### chuckles — 2026-07-27T22:41:02.875Z
[merge-child] blocked: git pull merge on sub — `Merge remote-tracking branch 'origin/dev' into sub/…` @ eb828a3. Rebuild sub from origin/ftr/AST-988-integration-tests-are-failing-on-github and republish AST-990 sequence only (no merge origin/dev onto sub).

@Ada Lovelace

— Chuckles

#### radia — 2026-07-27T22:39:19.397Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-990
**Publish ref:** `origin/sub/AST-988/AST-990-align-integration-nav-scenario-with-current-candidate-states` @ `3a2fce5d5fd650229c1b67d0acc4d04c2363c7a6`
**Overall:** DISCUSS

**Diff:** `origin/dev...origin/sub/AST-988/AST-990-align-integration-nav-scenario-with-current-candidate-states` — `docs/features/foundation/ast-990-….md` (A) + `tests/integration/scenarios/test_candidate_nav_api.py` (M). Layers: `docs` (+ unmapped `tests/` path). Change types: add, modify. Zero `src/`.

## Statutes checked

| id | tier | verdict | one-line |
| -- | -- | -- | -- |
| astral.agent.confidence-bounds | scoped | not-applicable | layers/paths miss (no core/utils src) |
| astral.agent.do-task-delegation | scoped | not-applicable | layers/paths miss (no src/core) |
| astral.agent.grade-vector-validation | scoped | not-applicable | layers/paths miss (no src/core) |
| astral.batch.batch-id-first | scoped | not-applicable | layers/paths miss (no data/core) |
| astral.batch.batch-id-format | scoped | not-applicable | layers/paths miss (no data/core) |
| astral.batch.claim-process-release | scoped | not-applicable | layers/paths miss (no data/core) |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | layers/paths miss (no data/core) |
| astral.config.config-source-of-truth | scoped | not-applicable | layers/paths miss (no src/**) |
| astral.config.pass-threshold-vs-score-floor | scoped | not-applicable | layers/paths miss |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | layers/paths miss |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | paths miss (no artifacts/** / scripts/spikes) |
| astral.debug.spikes-under-debug-dir | scoped | conforms | docs/features is plan doc, not spike notes; C4 straggler |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single `docs/features/foundation/ast-990-….md`; C4 straggler |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty `test()` touched tests only; features by plan/code/docs; C4 straggler |
| astral.git.engineer-test-tree-ban | scoped | conforms | tests edit via Betty `test(AST-990)` + Ada `merge-tests` only |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | layers/paths miss |
| astral.layers.import-direction | scoped | not-applicable | layers/paths miss |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | layers/paths miss |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | layers/paths miss |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | layers/paths miss |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | layers/paths miss |
| astral.patterns.require-auth-on-protected-endpoints | scoped | not-applicable | layers/paths miss |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | layers/paths miss |
| astral.standards.database-header-inventory | scoped | not-applicable | layers/paths miss |
| astral.standards.debug-contract-gated | scoped | not-applicable | layers/paths miss |
| astral.standards.dry-and-focused-functions | scoped | not-applicable | layers/paths miss |
| astral.standards.in-scope-only | scoped | not-applicable | layers/paths miss (no src/**) |
| astral.standards.logging-via-utils | scoped | not-applicable | layers/paths miss |
| astral.standards.no-cross-contamination | scoped | not-applicable | layers/paths miss |
| astral.standards.no-hardcoded-sets | scoped | not-applicable | layers/paths miss (seed literal is test-tree) |
| astral.standards.public-then-helpers | scoped | not-applicable | layers/paths miss |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | layers/paths miss |
| astral.state.core-decides-transitions | scoped | not-applicable | layers/paths miss |
| astral.state.job-prior-states-enforced | scoped | not-applicable | layers/paths miss |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | layers/paths miss |
| astral.ui.frontend-file-placement | scoped | not-applicable | layers/paths miss |
| astral.ui.naming-conventions | scoped | not-applicable | layers/paths miss |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | layers/paths miss |
| orch.git.betty-merge-tests-one-sha | universal | conforms | one `merge-tests(AST-990)` of `b2e9eef` |
| orch.git.commit-vocabulary | universal | conforms | plan/code/docs/test/merge-tests only |
| orch.git.flow-direction-inviolable | universal | conforms | publish on authoritative sub; no reverse flow |
| orch.git.ftr-sub-topology | universal | conforms | `sub/AST-988/AST-990-…` under parent ftr |
| orch.git.merge-on-checkout | universal | conforms | merge `origin/dev` present; BEHIND=0 at review |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no cherry-pick/rebase/force in tip history |
| orch.git.no-dev-agent-branches | universal | conforms | pushed to `origin/sub/…` only |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review on `astral-AST-988` epic worktree |
| orch.git.three-permanent-branches | universal | conforms | no new permanent branch |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | zero product edits; Boundaries honored |
| orch.pipeline.plan-is-bible | universal | conforms | exact Stage 2 seed + ownership split |
| orch.pipeline.project-scoped-queues | universal | conforms | Foundation child only |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | no canon/statute amendments |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns scenario seed commit |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada remains assignee through Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | path ownership matches role bans |

## Pattern conformance

none cited

## Plan adherence

Self-Assessment Scope `minor` matches footprint (one scenario seed + plan doc; zero `src/`). Stage 2 edit exact (`NEW` → `NEW_CANDIDATE`, comment updated). ACTIVE_SEARCH half and sibling tests unchanged. Bible optional path correctly unused. Cross-ticket: no AST-989 / operator / registry smuggling.

## Findings

**discuss (C4 straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.betty-no-src-or-features` because planned Files Changed omitted `docs/features/**`. Three-dot diff includes the plan file → all three in-scope. Substance verdict for each is **conforms** (plan not spike; one feature file; Betty did not edit features). Acknowledge at resolve — no code change.

**fix-now:** none

### What’s solid

Harness-only alignment; registry/nav product untouched; ownership split executed.

### Recommended actions

1. resolve-child: acknowledge C4 stragglers; no product/test patch.
2. Keep assignee Ada.

**Notes:** Joan plan-rubric verdict attached (APPROVED). Docs append on plan file @ `3a2fce5`.

context_tokens≈48000

#### betty — 2026-07-27T22:34:39.923Z
1. `./scripts/testing/run_integration_tests.sh`

**Change:** `tests/integration/scenarios/test_candidate_nav_api.py` — early-lifecycle overwrite seed `NEW` → `NEW_CANDIDATE` (Jobs group still absent; ACTIVE_SEARCH half unchanged).

**Bible:** unchanged (no retired-`NEW` note in `docs/test-bible/integration/README.md`).

`origin/sub/AST-988/AST-990-align-integration-nav-scenario-with-current-candidate-states` @ `d0209ba` (`merge-tests(AST-990): origin/tests b2e9eef`)

#### ada — 2026-07-27T22:31:16.342Z
origin/sub/AST-988/AST-990-align-integration-nav-scenario-with-current-candidate-states @ 8fc58d879cc7bbff4a88bfb5bf991f6cf5fa28f3 — Stage 1 verification only (no src/). Betty: Stage 2 `NEW` → `NEW_CANDIDATE` in `tests/integration/scenarios/test_candidate_nav_api.py`; manifest `./scripts/testing/run_integration_tests.sh`.

#### joan — 2026-07-27T22:29:20.196Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-990
**Overall:** APPROVED

**Notes:** Files Changed Layer cells `tests` and `bible` are unrecognized by plan-rubric layer enum → treated as `docs` for matching. Publish ref from parent Git table: `sub/AST-988/AST-990-align-integration-nav-scenario-with-current-candidate-states`. Implementing engineer: Ada (parent Team table + plan author).

## Traceability

### Parent AC → plan stages

| Parent AC | Plan stage(s) |
| -- | -- |
| AC1 — GHA Integration tests green (harness exit 0; no invalid-state errors) | Stage 2 (Betty seed fix + harness exit 0); Stage 3 (Ada Tests Ready manifest green) |
| AC2 — Nav scenario still proves Jobs absent under early-lifecycle registry state; Jobs / in-review enabled under ACTIVE_SEARCH | Stage 2 steps 1–2 (keep ACTIVE_SEARCH half; overwrite to `NEW_CANDIDATE` for hide-Jobs half) |

### Plan stages → parent definition

| Plan stage | Maps to |
| -- | -- |
| Stage 1 — Confirm product unchanged (Ada) | Purpose (harness-only); Boundaries (no registry/nav/product edits); Functional scope fidelity check before Betty edit |
| Stage 2 — Align scenario seed (Betty) | Functional scope §1; AC1–AC2; Boundaries (no coverage expand; Betty owns tests) |
| Stage 3 — Engineer harness confirm (Ada) | Functional scope §2; AC1; `[qa-handoff]` / parent Stage-blocked paths honor Boundaries |

## Statute verdicts

| id | verdict | one-line |
| -- | -- | -- |
| astral.git.engineer-test-tree-ban | conforms | Ada stages forbid `tests/` / bible edits; Stage 3 `[qa-handoff]` if harness test defect |
| orch.git.betty-merge-tests-one-sha | conforms | Stage 2 defers to qa-child single `test()` publish — no duplicate merge-tests invented |
| orch.git.commit-vocabulary | conforms | Stage 2 names `test()` publish; Ada verification-only avoids rogue `feat`/`fix` vocabulary |
| orch.git.flow-direction-inviolable | conforms | Child publish ref → parent `ftr` merge path only; no reverse-flow steps |
| orch.git.ftr-sub-topology | conforms | Uses dispatch `sub/AST-988/AST-990-…` and parent `ftr/AST-988-…` |
| orch.git.merge-on-checkout | conforms | Stages 1 and 3 require merge `origin/dev` + parent `ftr` before work |
| orch.git.no-cherry-pick-rebase-force | conforms | No cherry-pick / rebase / force proposed |
| orch.git.no-dev-agent-branches | conforms | Publishes only to authoritative `sub/…` ref |
| orch.git.one-epic-worktree-per-parent | conforms | Stages run on epic worktree with one active sub checkout |
| orch.git.three-permanent-branches | conforms | No new permanent branch; stays on `dev`/`ftr`/`sub` topology |
| orch.pipeline.call-susan-for-product-decisions | conforms | Product change out of Boundaries — stop + parent comment; no invented nav/registry fix |
| orch.pipeline.plan-is-bible | conforms | Stages bind Ada/Betty/test-child to exact seed edit and ownership split |
| orch.pipeline.project-scoped-queues | conforms | Single-child Foundation ticket; no cross-project queue improvisation |
| orch.pipeline.status-gates-skill-entry | conforms | Plan Ready→build; Code Complete→qa; Tests Ready→test-child sequence explicit |
| orch.roles.archie-approves-statutes | conforms | No statute / canon amendments in Files Changed |
| orch.roles.betty-owns-test-tree | conforms | Stage 2 Betty-only edit of scenario (+ optional bible); Ada banned from tests |
| orch.roles.chuckles-never-ticket-assignee | conforms | Implementer Ada; Chuckles not assigned as builder |
| orch.roles.engineer-assignee-through-resolve | conforms | Ada remains engineer through build/test; Betty owns only test-tree commit |
| orch.roles.pre-commit-path-bans | conforms | Plan states engineer pre-commit blocks `tests/`; ownership matches hook bans |

## Considered and excluded

**Considered:** astral.git.engineer-test-tree-ban; orch.git.betty-merge-tests-one-sha; orch.git.commit-vocabulary; orch.git.flow-direction-inviolable; orch.git.ftr-sub-topology; orch.git.merge-on-checkout; orch.git.no-cherry-pick-rebase-force; orch.git.no-dev-agent-branches; orch.git.one-epic-worktree-per-parent; orch.git.three-permanent-branches; orch.pipeline.call-susan-for-product-decisions; orch.pipeline.plan-is-bible; orch.pipeline.project-scoped-queues; orch.pipeline.status-gates-skill-entry; orch.roles.archie-approves-statutes; orch.roles.betty-owns-test-tree; orch.roles.chuckles-never-ticket-assignee; orch.roles.engineer-assignee-through-resolve; orch.roles.pre-commit-path-bans

**Excluded:**
- astral.agent.confidence-bounds — layers miss (need core/utils); paths miss
- astral.agent.do-task-delegation — layers miss; paths miss
- astral.agent.grade-vector-validation — layers miss; paths miss
- astral.batch.batch-id-first — layers miss; paths miss
- astral.batch.batch-id-format — layers miss; paths miss
- astral.batch.claim-process-release — layers miss; paths miss
- astral.batch.entity-agent-responses-latest-only — layers miss; paths miss
- astral.config.config-source-of-truth — layers miss; paths miss (plan does not edit `src/**`)
- astral.config.pass-threshold-vs-score-floor — layers miss; paths miss
- astral.config.secrets-and-env-specific-from-environ — layers miss; paths miss
- astral.debug.no-repo-root-artifacts-dir — paths miss
- astral.debug.spikes-under-debug-dir — paths miss
- astral.docs.features-single-file-per-ticket — paths miss (planned Files Changed has no `docs/features/**` edit)
- astral.git.betty-no-src-or-features — paths miss
- astral.layers.core-vs-external-bright-line — layers miss; paths miss
- astral.layers.import-direction — layers miss; paths miss
- astral.layers.scripts-exempt-from-layer-rules — layers miss; paths miss
- astral.layers.ui-config-driven-business-logic — layers miss; paths miss
- astral.patterns.coat-check-never-store-empty — layers miss; paths miss
- astral.patterns.render-verdict-orchestrates-consult — layers miss; paths miss
- astral.patterns.require-auth-on-protected-endpoints — layers miss; paths miss
- astral.standards.data-raises-caller-logs — layers miss; paths miss
- astral.standards.database-header-inventory — layers miss; paths miss
- astral.standards.debug-contract-gated — layers miss; paths miss
- astral.standards.dry-and-focused-functions — layers miss; paths miss
- astral.standards.in-scope-only — layers miss; paths miss
- astral.standards.logging-via-utils — layers miss; paths miss
- astral.standards.no-cross-contamination — layers miss; paths miss
- astral.standards.no-hardcoded-sets — layers miss; paths miss (literal seed is test-tree; config registry unchanged)
- astral.standards.public-then-helpers — layers miss; paths miss
- astral.standards.utils-data-late-import-only — layers miss; paths miss
- astral.state.core-decides-transitions — layers miss; paths miss
- astral.state.job-prior-states-enforced — layers miss; paths miss
- astral.state.no-daisy-chain-in-run — layers miss; paths miss
- astral.ui.frontend-file-placement — layers miss; paths miss
- astral.ui.naming-conventions — layers miss; paths miss
- astral.ui.single-gunicorn-worker — layers miss; paths miss

## Findings

None (zero fix-now / discuss).

R6 checklist: definition fidelity pass; no layer/import/product edits; no new config keys; no new `src/` files; Betty owns test-tree; self-assessment minor/high/low honest and specific.

— Joan
context_tokens≈52000

#### ada — 2026-07-27T22:23:25.535Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-988/AST-990-align-integration-nav-scenario-with-current-candidate-states/docs/features/foundation/ast-990-align-integration-nav-scenario-with-current-candidate-states.md

`origin/sub/AST-988/AST-990-align-integration-nav-scenario-with-current-candidate-states` @ `38ce6b65787b12404b0114db6ad9d4275fc6f4c3`

**Scope:** minor — one integration scenario seed (`NEW` → `NEW_CANDIDATE`); zero product modules.

**Conf:** high — GHA traceback, registry keys, and Jobs `visible: ACTIVE_SEARCH` gate already proven on `dev`; replacement state named in ticket Notes.

**Risk:** low — wrong seed keeps CI red or weakens the hide-Jobs assert; `src/` stays untouched so product nav cannot regress from this ticket.

Ownership: Ada verifies product unchanged → Code Complete; Betty lands the `tests/` edit via qa-child.

---

# AST-990 — Align integration nav scenario with current candidate states

- **Linear (this ticket):** [AST-990](https://linear.app/astralcareermatch/issue/AST-990/align-integration-nav-scenario-with-current-candidate-states)
- **Parent:** [AST-988](https://linear.app/astralcareermatch/issue/AST-988/integration-tests-are-failing-on-github) — Integration tests are failing on GitHub
- **Publish ref:** `origin/sub/AST-988/AST-990-align-integration-nav-scenario-with-current-candidate-states`

## Summary

GitHub Actions Integration tests fail because `tests/integration/scenarios/test_candidate_nav_api.py` still seeds retired candidate state `NEW`. The live registry (AST-970+) requires `NEW_CANDIDATE` (or another early-lifecycle key). This ticket restores a green harness by aligning that one seed to `NEW_CANDIDATE`, which still sits below the Jobs group `visible: "ACTIVE_SEARCH"` gate. **No product behavior change** — test-tree / harness alignment only. Ada confirms product is already correct; Betty lands the `tests/` edit via `qa-child`.

## Ownership split (mandatory)

| Role | Owns |
|------|------|
| Ada (`build-child`) | Confirm no `src/` / CI / harness product edits; Code Complete with zero product commits if verification holds |
| Betty (`qa-child`) | Edit `tests/integration/scenarios/test_candidate_nav_api.py` (and bible only if she judges a one-line note needed); publish `test()` to this publish ref |

Engineer pre-commit blocks `tests/` — Ada must **not** patch the scenario file.

## Files Changed (planned)

| File | Change | Layer | Owner |
|------|--------|-------|-------|
| `tests/integration/scenarios/test_candidate_nav_api.py` | Replace retired `NEW` seed with `NEW_CANDIDATE`; update adjacent comment | tests | Betty (qa-child) |
| `docs/test-bible/integration/README.md` | Optional one-line note that early-lifecycle seed is `NEW_CANDIDATE` — only if Betty finds the scenario doc still implies `NEW` | bible | Betty (qa-child) |

**Explicitly unchanged (do not edit):**

| File / area | Why |
|-------------|-----|
| `src/utils/config.py` (`CANDIDATE_STATES`, `NAV_CONFIG`) | Registry and Jobs `visible: "ACTIVE_SEARCH"` already correct on `dev` |
| `src/ui/api/api_system.py` | `_is_at_or_past` / `_resolve_nav` already hide Jobs when `progress_rank` is below `ACTIVE_SEARCH` |
| `src/data/database.py` | `save_candidate` correctly rejects non-registry states — that is the failure under test |
| `scripts/testing/run_integration_tests.sh` | Entry point already correct; no harness change |
| `.github/workflows/*` | CI already invokes the harness; green after scenario fix |
| AST-989 / Joan operator / Betty monitoring skills | Out of scope (parent boundaries) |

## Evidence (planner read — do not re-litigate at build)

1. GHA failure (parent Original brief): `save_candidate(..., state="NEW")` → `ValueError: Invalid candidate state 'NEW'. Must be one of: ['NEW_CANDIDATE', ...]`.
2. Scenario file line 43: `seeded_candidate.save_candidate("cand-1", state="NEW", ...)`.
3. `CANDIDATE_STATES["NEW_CANDIDATE"]` has `progress_rank: 0`; Jobs group in `NAV_CONFIG` has `"visible": "ACTIVE_SEARCH"`.
4. Component proof already exists: `tests/component/ui/api/test_api_system.py` asserts `_is_at_or_past("NEW_CANDIDATE", "ACTIVE_SEARCH") is False`.
5. `save_candidate` update path validates membership in `CANDIDATE_STATES.keys()` only (no `prior_states` transition check on overwrite) — seeding `ACTIVE_SEARCH` then overwriting to `NEW_CANDIDATE` is valid for this scenario.

⚠️ **Decision:** Use literal `NEW_CANDIDATE` (not `INTAKE_INITIATED` or another pre-`ACTIVE_SEARCH` state). Ticket Notes name it; it is `CANDIDATE_CONFIG["initial_state"]`; component nav tests already use it for the same gate. Alternatives would also hide Jobs but add ambiguity for Betty.

⚠️ **Decision:** Ada's build stage is verification-only — no empty product commit required. Move to **Code Complete** so Betty can land the test edit. If Ada discovers product must change to satisfy AC, **stop** and comment on the parent (product change is out of Boundaries).

## Stage 1: Confirm product unchanged (Ada — build-child)

**Done when:** Ada has verified on the epic worktree tip (after merge `origin/dev` + `origin/ftr/AST-988-integration-tests-are-failing-on-github`) that no product file listed under "Explicitly unchanged" needs an edit for AC; ticket is **Code Complete** with no Ada `src/` commit.

1. On epic worktree with `sub/AST-988/AST-990-align-integration-nav-scenario-with-current-candidate-states` checked out, confirm `git merge-base --is-ancestor origin/dev HEAD` and `BEHIND=0` vs `origin/dev`.
2. Read-only verify:
   - `CANDIDATE_STATES` contains `NEW_CANDIDATE` and does **not** contain `NEW`.
   - `NAV_CONFIG` Jobs group still has `"visible": "ACTIVE_SEARCH"`.
   - `tests/integration/scenarios/test_candidate_nav_api.py` still has `state="NEW"` on the early-lifecycle overwrite (Betty's target).
3. Do **not** edit `tests/`, `docs/test-bible/**`, `src/`, harness scripts, or GHA workflows.
4. Publish nothing new unless a merge commit was required for the merge-clean gate (already handled in plan-child if needed). Proceed to Linear **Code Complete**.

## Stage 2: Align scenario seed (Betty — qa-child)

**Done when:** `./scripts/testing/run_integration_tests.sh` exits 0 on the publish-ref tip; the nav scenario still proves Jobs visible under `ACTIVE_SEARCH` and absent under `NEW_CANDIDATE`; no invalid-state errors.

1. In `tests/integration/scenarios/test_candidate_nav_api.py`, inside `test_nav_config_reflects_seeded_candidate_state`, change the early-lifecycle overwrite from:

```python
    # ACTIVE_SEARCH satisfies Jobs group visible gate; NEW would hide the whole group.
    seeded_candidate.save_candidate("cand-1", state="NEW", candidate_data={"name": "Integration Test"})
```

to:

```python
    # ACTIVE_SEARCH satisfies Jobs group visible gate; NEW_CANDIDATE hides the whole group.
    seeded_candidate.save_candidate(
        "cand-1", state="NEW_CANDIDATE", candidate_data={"name": "Integration Test"}
    )
```

2. Leave the first half of the test unchanged: `ACTIVE_SEARCH` seed → Jobs group present → `/jobs/in_review` `enabled is True`.
3. Leave `test_list_candidates_returns_seeded_row` and `test_unauthenticated_nav_config_returns_401` unchanged.
4. Do **not** add new scenarios or expand coverage.
5. Optionally update `docs/test-bible/integration/README.md` only if it still documents the retired `NEW` seed for this scenario; otherwise leave bible alone.
6. Commit on Betty's tests worktree and publish `test()` to `origin/sub/AST-988/AST-990-align-integration-nav-scenario-with-current-candidate-states` per `qa-child`.
7. Manifest for `test-child`: at minimum `./scripts/testing/run_integration_tests.sh` (full default target).

## Stage 3: Engineer harness confirm (Ada — test-child)

**Done when:** Betty's Tests Ready manifest is green on the epic worktree publish tip; ticket moves to **Tests Passed**.

1. After Betty sets **Tests Ready**, run her manifest on the epic worktree with this sub checked out (merge `origin/dev` + parent `ftr` first).
2. If the harness fails because the scenario still uses `NEW` or any other test defect: **`[qa-handoff]`** first line on AST-990, assign Betty, stay **Tests Ready** — do not patch `tests/`.
3. If the harness fails because product nav/registry behavior changed: stop and comment on **parent AST-988** with the Stage-blocked template — do not invent product fixes outside Boundaries.
4. On green: **Tests Passed**.

## Self-Assessment

**Scope:** `minor` — one integration scenario seed string (+ optional bible note); zero product modules.

**Conf:** `high` — failure traceback, registry keys, and Jobs `visible` gate are already proven on `dev`; replacement state is named in the ticket Notes.

**Risk:** `low` — wrong seed string would keep CI red or weaken the hide-Jobs assertion; cannot regress product nav if `src/` stays untouched.

## Rules self-review

- §1.1 in-scope only: plan touches only the drifted scenario seed; no registry/nav product edits.
- §1.4 / §2.1 config as source of truth: scenario uses a live `CANDIDATE_STATES` key (`NEW_CANDIDATE`), not a hardcoded retired alias; does not invent a parallel state list.
- §2.6 state machine: no transition-rule changes; test uses `save_candidate` overwrite already used by the scenario.
- Engineer test-tree ban honored: Ada stages do not edit `tests/` or bible; Betty owns Stage 2.
- No conflicts requiring `conf-!!-NONE`.

## Review (build stub)

**Built:** `origin/sub/AST-988/AST-990-align-integration-nav-scenario-with-current-candidate-states` @ `f28fd82` (merge `origin/dev` into sub; no Ada `src/` commit)

**Stages delivered:**
- Stage 1: Product unchanged confirmed — `CANDIDATE_STATES` has `NEW_CANDIDATE` not `NEW`; Jobs `visible: ACTIVE_SEARCH`; scenario still seeds `state="NEW"` (Betty Stage 2 target)

**Betty:** replace `NEW` → `NEW_CANDIDATE` in `tests/integration/scenarios/test_candidate_nav_api.py` per Stage 2; manifest `./scripts/testing/run_integration_tests.sh`.

## Radia review (code-rubric.v1)

`[code-rubric] revision=1`

**Overall:** DISCUSS (C4 stragglers only — no product/test fix-now)

**Publish ref tip reviewed:** `d0209ba43d0bc97b28c707d215a9c85c52957066`

**Diff:** `origin/dev...origin/sub/AST-988/AST-990-align-integration-nav-scenario-with-current-candidate-states` — plan doc add + one integration scenario seed (`NEW` → `NEW_CANDIDATE`). Zero `src/`.

### What’s solid

- Plan fidelity exact: Betty `test(AST-990)` + Ada `merge-tests` landed the Stage 2 seed; ACTIVE_SEARCH half untouched; no coverage expand; bible left alone per Betty.
- Ownership: Ada Stage 1 verification-only (docs stub); Betty owns `tests/`; no engineer test-tree edit.
- Acceptances still encoded: early-lifecycle `NEW_CANDIDATE` hides Jobs; prior ACTIVE_SEARCH enables `/jobs/in_review`.

### Issues

**discuss (C4 straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.betty-no-src-or-features` (plan Files Changed had no `docs/features/**`). Three-dot diff includes the plan file → all three in-scope. Substance: **conforms** (single feature file; content is plan not spike; Betty `test()` did not touch `docs/features/`). No product action — acknowledge at resolve.

### Recommended actions

1. resolve-child: acknowledge the three C4 stragglers (no code change).
2. Leave assignee Ada; no fix-now.

## Resolution (2026-07-27)

- **fix-now:** none — no product or test patch.
- **discuss (C4 straggler):** Acknowledged. Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.betty-no-src-or-features` because planned Files Changed omitted `docs/features/**`; three-dot diff brought the plan file in-scope. Substance remains **conforms** (single plan file; not spike notes; Betty `test()` did not edit features). No code change.
- **Assignee:** Ada Lovelace unchanged through User Testing.
