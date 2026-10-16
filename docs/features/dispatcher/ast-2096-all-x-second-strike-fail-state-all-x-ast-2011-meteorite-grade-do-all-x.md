# AST-2096 — All-X second strike → fail_state _ALL_X (AST-2011 meteorite_grade_do all-X)

<!-- linear-archive: AST-2096 archived 2026-10-16 -->

## Linear archive (AST-2096)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2096/all-x-second-strike-fail-state-all-x-ast-2011-meteorite-grade-do-all-x  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-2011 — [✅/Somerset] meteorite_grade_do COMPLETED: 2 error(s) / 30 processed | meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e  
**Blocked by / blocks / related:** parent: AST-2011; related: AST-2073

### Description

## What this implements

The `fix` child for orphaned bug [AST-2011](https://linear.app/astralcareermatch/issue/AST-2011) (somerset `meteorite_grade_do` all-literal-X). Susan's direction: an all-literal-`X` scored grade set still gets one retry (primary → `retry_state` holding, unchanged). A second all-`X` strike, when the entity is already on `_RETRY`, transitions it to the task's `fail_state` + `_ALL_X` (e.g. `METEORITE_FAILED_DO_ALL_X`) instead of `error_state`. It counts and logs as a fail, not a technical error. Plain incomplete/extra grade sets keep today's retry → `error_state` route.

## Scope

## Component scope

* `src/utils/config.py` — modified — register the `{fail_state}_ALL_X` job states for scored tasks and add the suffix/name helper beside `RETRY_SUFFIX` / `retry_of`.
* `src/core/consult.py` — modified — route second-strike all-literal-`X` to `fail_state + _ALL_X` at both catch sites (`render_verdict` single-entity apply, `_run_batch_consult` batch apply) and count it as a fail.

## Technical scope

* `src/utils/config.py`: new constant + new function (suffix and name builder, mirroring `retry_of`) so every `_ALL_X` name is derived from its base fail state; new `JOB_STATES` entries (one per scored-task `fail_state`) so the state transition validator accepts the new terminal, with `prior_states` matching the base fail state. Plan-fix decides explicit rows vs an implicit-suffix registration like AST-1804's `_RETRY` — explicit rows are the smaller blast radius (no validator changes in roster / tracker / candidate / database / admin API).
* `src/core/consult.py`: new function — all-X fail destination (primary → `retry_state`, `_RETRY` → `fail_state` + `_ALL_X`), because `_consult_batch_fail_dest` only knows `error_state`; modified function `render_verdict` — `AllLiteralXGradeSetError` branch uses the new destination and fail-level logging; modified function `_run_batch_consult` — split all-X IDs out of `bad_grades`, transition them via the new destination, and tally them as `failed`.

## Boundaries

Does not touch the somerset Do rubric duplicate `TP` warning (separate). Does not change the first-strike retry, `_render_pass_fail`'s binary all-X → `fail_state`, partial-X scoring, or the `IncompleteGradeSetError` route for non-all-X sets.

## Notes for planning

Ancestor: AST-1760 (All-X scored grades → retry holding, archived, built by Hedy). Doc to patch: `docs/features/consult/ast-1760-all-x-scored-grades-retry-holding.md`. Full as-is/to-be lives on [AST-2011](https://linear.app/astralcareermatch/issue/AST-2011).

In-flight overlap: [AST-2073](https://linear.app/astralcareermatch/issue/AST-2073) / [AST-2086](https://linear.app/astralcareermatch/issue/AST-2086) (terminal-state rename) also rewrites `_consult_batch_fail_dest` and adds naming helpers beside `retry_of`. This child runs in parallel on a fresh ftr off dev; the second to land resolves the merge.

## Git branch (authoritative)

Orphaned mini-parent: `ftr/AST-2011-meteorite-grade-do-all-x`, child `sub/AST-2011/AST-2096-all-x-fail-state`. Seeded off `origin/dev` by bug-fix.

### Comments

#### betty — 2026-10-09T02:59:06.586Z
[check-linear] User Testing — sub republished @ `8fa989383` with one `merge-tests(AST-2096)` (squashed test `d02cb3cfb`); tree identical to `72e49fa0d`; validate-sub-log status=ok, merge-child unblocked.

#### radia — 2026-10-09T02:57:34.366Z
[code-rubric] PROCEED (Commit: a135a38e3) all-X second-strike clean

#### hedy — 2026-10-09T02:55:58.242Z
`origin/sub/AST-2011/AST-2096-all-x-fail-state` @ `a135a38e3` · [bug-repro] 5/5 red→green; manifest + TestAst1808 15 passed; full tree 0 new failures vs pre-fix base, all AST-2096 lines/branches covered. Baseline caveat: origin/dev already has 5 import-broken test files, ~346 failures, and consult.py/config.py below LOCKED_AT_100 — out of scope.

#### betty — 2026-10-09T02:53:27.203Z
[check-linear] Code Complete — Tests updated for [qa-handoff], @Hedy Lamarr re-run test-child.
- Fixed: `test_config.py::TestAst1808RetryRegistryPurge::test_prior_snapshot_pinned` now has the AST-2096 block after AST-2069: six `{fail_state}_ALL_X` rows + derived `_RETRY` (your values).
- Manifest delta: add `tests/component/utils/test_config.py::TestAst1808RetryRegistryPurge` to the AST-2096 run.
- Publish: `origin/sub/AST-2011/AST-2096-all-x-fail-state` @ `a135a38e3` (`merge-tests(AST-2096): origin/tests 60582ba30`, +7 lines in one file). On that tree, 15 passed: TestAst1808 + TestAst1760 + TestAst2096.
- Same one-off validate-tests-branch.sh skip as before (pre-existing `9ead623ca`); my commits pass the validator's rules.

#### hedy — 2026-10-09T02:51:54.034Z
[qa-handoff]
@Betty White — one manifest-adjacent test is stale after the AST-2096 fix. It's test-tree, so it's yours. Product is otherwise green.

**Repro gate:** OK. All 5 `[bug-repro]` nodes fail on pre-fix `3b46b42be` and pass on `origin/sub/AST-2011/AST-2096-all-x-fail-state` @ `f2f9f41dd`. The targeted manifest command gives 12 passed.

**What failed:** `tests/component/utils/test_config.py::TestAst1808RetryRegistryPurge::test_prior_snapshot_pinned` → `AssertionError: JOB_STATES`, with 12 extra targets: the six `*_ALL_X` states plus their derived `*_ALL_X_RETRY`.

**Why it's a test problem, not a product bug:** the plan (§ Bug: AST-2096, Proposed change 2) adds six explicit `JOB_STATES` rows. This test pins the AST-1806 prior snapshot and patches in each later state addition by hand (AST-2004 rename, AST-2024 `RELATIVE_*`, AST-2069 company upshot). AST-2096 needs the same translation block. The board note listed `test_config` as unaffected, but this pinned snapshot isn't derived from the registry.

**What to add** (after the AST-2069 block). Each value is exact `state_prior_states` output on the fix tip:

```python
# AST-2096 added six scored-task {fail_state}_ALL_X terminals: priors = base fail_state's trigger (+ _RETRY).
for s, trig in (("FAILED_DO_ALL_X", "PASSED_JD"), ("FAILED_GET_ALL_X", "PASSED_DO"),
                ("FAILED_LIKE_ALL_X", "CULTURE_READY"), ("METEORITE_FAILED_DO_ALL_X", "METEORITE_PASSED_JD"),
                ("METEORITE_FAILED_GET_ALL_X", "METEORITE_PASSED_DO"), ("METEORITE_FAILED_LIKE_ALL_X", "METEORITE_PASSED_GET")):
    js[s] = [trig, f"{trig}_RETRY", f"{s}_RETRY"]
    js[f"{s}_RETRY"] = [s, f"{s}_RETRY"]
```

**Full-tree context (not AST-2096):** the zero-arg harness can't run on this tree. Five files on `origin/dev` fail at import (`test_meteorite_email`, `test_page_intake`, `test_surfer`, `data/database/test_meteorites`, `data/database/test_surfer_batches`: missing `METEORITE_STATES_RETENTION`, `SURFER_BATCH_CONFIG`, …). With those ignored, the pre-fix base has 351 failed and the fix tip has 346 failed. The only new failure at the tip is the snapshot test above. `test_candidate::TestAst1881…::test_craft_prefilter_generate_merges_into_response_and_stash` also shows up, but that's stale `data/astral.db` state (409); it passes with a fresh `ASTRAL_DB_DIR`.

**LOCKED_AT_100:** can't be shown green on this tree, because the pre-fix baseline itself has `consult.py` at 81.0% and `config.py` at 91.7% from the broad pre-existing failures. Relative to base, `consult.py` went 81.0% → 81.1% and `config.py` is unchanged. No missing line or branch falls inside any AST-2096 hunk.

#### betty — 2026-10-09T02:41:29.899Z
[bug-repro]
`origin/sub/AST-2011/AST-2096-all-x-fail-state` @ `ff7efc42c` · repro lands red, awaits fix
One-off validate-tests-branch.sh skip for this push (pre-existing `9ead623ca` on origin/tests; my commits pass `--depth 2`), per Chuckles.

#### betty — 2026-10-09T02:40:06.622Z
@susan qa-fix blocked at publish — repro ready locally, not pushed.

- Repro: `5ead8d25f` (built on `823d37605`, so the AST-2096 sub only gets AST-2096's tests). 5 tests red for the right reason on the sub tree, 7 AST-1760 regressions green. Manifest is in the bible at `core/consult.md` § AST-2096.
- Blocker: `validate-tests-branch.sh` fails because of `9ead623ca` (`sync(publish-ref)` for AST-2091), a two-parent merge already on `origin/tests`. My commits pass with `--depth 2`.
- Needs your call: push anyway, or advance `tests-clean-base` past `9ead623ca`. Until then: no `merge-tests`, no Tests Ready, so make-fix should wait.

#### joan — 2026-10-09T02:36:11.097Z
[board-joan]  CANON: OK

#### betty — 2026-10-09T02:35:24.834Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/consult.md § AST-1760 — broken test + missing coverage — `TestAst1760AllLiteralXRetry::test_render_verdict_meteorite_like_all_x_second_strike` asserts `success is False` / `METEORITE_FAILED_TECHNICAL_LIKE` (must flip to `True` / `METEORITE_FAILED_LIKE_ALL_X`); no test covers the batch second-strike path (`_run_batch_consult` all-X on `*_RETRY` → `fail_state_ALL_X`, `failed += 1`, excluded from `bad_grades`) or the config `_ALL_X` registration (`all_x_of`, six `ALL_X_FAIL_STATES`, `*_RETRY` → `_ALL_X` admitted, in `SKIPPED_STATES`). consult.py + config.py are LOCKED_AT_100, so the new branches need tests anyway. Unaffected: `test_fail_dest_meteorite_like_matrix`, first-strike + mixed-batch tests, the AST-1155 incomplete-grade family, and test_config Processing/Skipped asserts (they use a hardcoded `_FAIL` list or are registry-derived).

#### hedy — 2026-10-09T02:34:30.914Z
`origin/sub/AST-2011/AST-2096-all-x-fail-state` @ `26194ddf9397296f47acc4ba01320c388ad696f0` · plan ready

---

_Implementation detail may live in git history on `origin/dev`._
