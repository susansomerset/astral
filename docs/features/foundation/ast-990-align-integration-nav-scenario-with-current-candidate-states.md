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
