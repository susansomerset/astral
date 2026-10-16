# AST-1895 — Cover InvalidJobLinkError fail reason + _run_batch_consult debug scope (test gap for AST-1893)

<!-- linear-archive: AST-1895 archived 2026-10-08 -->

## Linear archive (AST-1895)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1895/cover-invalidjoblinkerror-fail-reason-run-batch-consult-debug-scope  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 1  
**Parent:** AST-1888 — [✅/Abrams] qualify_job_listings COMPLETED: 1 error(s) / 1 processed | qualify_job_listings-35ef8081-10be-4cb8-9eb7-9c65d22648c1  
**Blocked by / blocks / related:** parent: AST-1888

### Description

## What this implements

Test gap from fix-board on [AST-1893](https://linear.app/astralcareermatch/issue/AST-1893/restore-invalidjoblinkerror-class-run-batch-consult-decorator-qualify) (`[board-betty] TESTS: REVISE`): regression coverage so the `InvalidJobLinkError` decorator mistake can't come back unnoticed. The existing `test_fails_short_title_and_relative_link` sends a relative link but checks only routing (`bad_grades`), so it passes on the broken tree.

## Scope

### Component scope

* `tests/component/core/test_consult.py` (modified): bug-repro coverage for the empty/relative `job_link` path in `qualify_job_listings` and the `_run_batch_consult` debug scope.
* `docs/test-bible/core/consult.md` (modified): bible entry for the new coverage — today it has no entry for `InvalidJobLinkError` or the `_run_batch_consult` debug scope.

### Technical scope

* `tests/component/core/test_consult.py`: new test function(s) — empty and relative `job_link` reach the same fail destination and the `_log_fail_dest` reason names `InvalidJobLinkError` (never `no signature found`); `InvalidJobLinkError` is a `ValueError` subclass; `_run_batch_consult(debug=True)` sets `log_debug` inside its frame.
* `docs/test-bible/core/consult.md`: new bible row pointing at those tests.

## Acceptance criteria

1. The bug-repro test fails on `origin/dev` (pre-fix tree) and passes once AST-1893's product fix is on the tip.
2. No product code changes on this ticket.

## Boundaries

Tests and bible only. Product fix (decorator move in `src/core/consult.py`) belongs to sibling [AST-1893](https://linear.app/astralcareermatch/issue/AST-1893/restore-invalidjoblinkerror-class-run-batch-consult-decorator-qualify) — it lands on the mini-parent ftr first and reaches this sub via sync-child.

## Notes for planning

Gap child filed by bug-fix from Betty's `[board-betty] TESTS: REVISE` on [AST-1893](https://linear.app/astralcareermatch/issue/AST-1893/restore-invalidjoblinkerror-class-run-batch-consult-decorator-qualify). Plan section home: `docs/features/consult/ast-337-qualified-job-urls.md` (same doc as AST-1893's `## Bug:` block).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1888-invalid-job-link-error-decorator`, child `sub/AST-1888/<child-segment>`. Created at bug-fix gap dispatch.

### Comments

#### radia — 2026-10-02T04:31:10.634Z
[code-rubric] PROCEED (Commit: e39323217) Bug-repro tests+bible OK

#### hedy — 2026-10-02T04:29:55.550Z
`origin/sub/AST-1888/AST-1895-cover-invalid-job-link-error-tests-v2` @ `e39323217` · [bug-repro] green; manifest green

- [bug-repro] `TestAst1895InvalidJobLinkError::test_empty_and_relative_job_link_fail_reason_names_error`: green on the tip.
- Manifest `ASTRAL_PYTHON=/home/susan/astral/.venv/bin/python ./scripts/testing/run_component_tests.sh tests/component/core/test_consult.py::TestAst1895InvalidJobLinkError -q`: 4 passed, exit 0.
- Red re-confirmed with `origin/dev` `src/core/consult.py` swapped in: 3 failed (reason, class, `debug_scope[True]`), and the `debug_scope[False]` guard passes, as designed. Restored afterwards; worktree clean, nothing pushed.

#### hedy — 2026-10-02T04:29:03.392Z
`origin/sub/AST-1888/AST-1895-cover-invalid-job-link-error-tests-v2` @ `e39323217` · no product change; sync clean (src vs `origin/dev` = AST-1893 decorator only); `TestAst1895InvalidJobLinkError` 4/4 green

#### betty — 2026-10-02T04:28:02.237Z
[bug-repro]
`origin/sub/AST-1888/AST-1895-cover-invalid-job-link-error-tests-v2` @ `247d86901` · full merge, green post-fix

#### chuckles — 2026-10-02T04:27:28.898Z
[bug-fix] Publish ref replaced: `sub/AST-1888/AST-1895-cover-invalid-job-link-error-tests` → `sub/AST-1888/AST-1895-cover-invalid-job-link-error-tests-v2` (seeded at `65eb3dcc5`, the old sub's tip before `merge-tests`).

Why: the old sub's `merge-tests(AST-1895)` commit `96d7ba059` has `d0cc98712` (newer `origin/tests`, carrying a dev resync) as a parent but kept the sub's older `src/` tree. Git therefore treats those dev changes as merged-and-dropped. Dry run: merging the old sub into today's `origin/dev` leaves 104 files different, about 10,000 lines deleted. Force-push / cherry-pick are statute-banned (`orch.git.no-cherry-pick-rebase-force`), so this is a new ref instead. The old sub is left untouched and won't be merged.

Back to Plan Discuss so qa-fix can re-publish: Betty does a normal full `merge-tests` of `d0cc98712` onto the v2 sub. The extra content it brings is already on `dev`; dry run into `dev` shows 6 files, nothing reverted.

#### hedy — 2026-10-02T04:26:29.552Z
`origin/sub/AST-1888/AST-1895-cover-invalid-job-link-error-tests` @ `42bd84aac` · no product change; fix landed via AST-1893

- On the tip, `TestAst1895InvalidJobLinkError` passes 4/4 (venv `/home/susan/astral/.venv`). `src/` is identical to `origin/ftr/AST-1888-invalid-job-link-error-decorator`, and `consult.py` compiles. The `42bd84aac` commit is empty and only marks this, following the AST-1894 / AST-1905 precedent.

**History hazard, @Chuckles Cursor @Betty White:** `sync-child.sh` exits 3 on this sub (conflict in `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx`). The merge-tests commit `96d7ba059` lists the tests-branch commit `d0cc98712` as its second parent, and that parent's history includes the AST-1877..1880 / 1875 / 1899 dev work, but `96d7ba059` kept the old sub tree. Git therefore treats that dev work as merged-and-removed. Finishing the sync would have reverted dev content: `src/core/agent.py`, `builder.py`, and `cost_calculator.py` among 29 `src/` files, the AST-1877..1880 plan docs deleted, and `deepseek.md` re-added. I aborted it and pushed nothing from it.

`origin/dev` is not an ancestor of this tip. Expect the same revert when merge-child takes this sub into the ftr once the ftr has newer dev. The three AST-1895 paths (`test_consult.py`, `docs/test-bible/core/consult.md`, plan doc) are correct as content. The history needs repair before rollup, for example by re-landing those paths on a sub rebuilt from the ftr.

#### betty — 2026-10-02T04:24:54.105Z
[bug-repro]
`origin/sub/AST-1888/AST-1895-cover-invalid-job-link-error-tests` @ `96d7ba059` · already green — fix pre-stacked

Stacking deviation: AST-1893's fix was already on the ftr, so this tip is post-fix (4/4 green). Repro-first verified by swapping in `origin/dev` `src/core/consult.py`: 3/4 red for the root-cause reasons (`no signature found` reason, class is a function, `log_debug` `[False]`); the `debug=False` guard passes on both trees. `merge-tests` tree = sub tree + this ticket's 2 paths only (a full merge would have brought 28 dev `src/` files into the sub). Manifest: `docs/test-bible/core/consult.md` § AST-1895.

#### chuckles — 2026-10-02T04:20:01.938Z
[check-linear] Plan Discuss — the publish blocker Betty hit is gone: `origin/tests-clean-base` is back, and `validate-tests-branch.sh` passes on `origin/tests` (`7c9610031`). Her repro `39abb800f` is safe on local `wip/AST-1895-unpublished`, but it isn't on `origin/tests` yet.

What's stuck now is the watcher. Parent AST-1888 still carries **Active/chuckles**, but no session is running, so `[bug-fix]` treats it as busy and won't resume it. This child has no `Bug` label, so assigning it to Chuckles won't wake anything either. Check-linear isn't allowed to touch Active.

@susan to kick it: clear **Active/chuckles** on AST-1888. The next poll resumes the wave loop, and Betty cherry-picks `39abb800f` (no sync merges) and publishes through qa-fix.

#### susan — 2026-10-02T04:17:33.015Z
@chuckles What is blocking this?  Please unblock it and kick the parent job?

#### betty — 2026-09-29T23:14:55.599Z
@susan qa-fix blocked at publish, before any push. `validate-tests-branch.sh` exits 1: `origin/tests-clean-base` (the AST-1574 marker) is missing. Even with the marker, the two-parent `sync(ftr)` / `sync(publish-ref)` commits that `sync-child --stay` creates on `tests` would fail its multi-parent rule, and the AST-1894 pass already pushed commits like that to `origin/tests`. The repro is done but only local (`tests` @ `39abb800f`): `TestAst1895InvalidJobLinkError` passes 4/4 on the synced tip and fails 3/4 against `origin/dev` `src/core/consult.py` for the root-cause reasons. Holding at Plan Discuss until you pick a publish path (restore the marker + cherry-pick without sync merges, or waive the gate).

#### joan — 2026-09-29T23:12:16.485Z
[board-joan]  CANON: OK

#### betty — 2026-09-29T23:12:03.527Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/consult.md (no entry) — missing coverage — this ticket is test-only, so it needs qa-fix, not make-fix. qa-fix should land `TestQualifyJobListings`' sibling `TestAst1895InvalidJobLinkError` in `tests/component/core/test_consult.py` (fail reason naming `InvalidJobLinkError` for empty and relative `job_link`, `ValueError`-subclass class check, `_run_batch_consult` `debug` scope) plus the `### AST-1895 · AST-1888` bible section and manifest. I checked the plan against the sub tip (809f9db4c): the decorator is on `_run_batch_consult` (line 1571), `_pass_grade` / `_rubric_item` / `_consult_batch_fail_dest` / `consult_mod.log_debug` / `TASK_CONFIG` all resolve, and the signature matches. One tweak: with `debug=False` the decorator keeps the ambient `log_debug`, so assert `seen == [debug or before]`. Blast radius touches no existing test.

#### hedy — 2026-09-29T23:11:18.104Z
`origin/sub/AST-1888/AST-1895-cover-invalid-job-link-error-tests` @ `809f9db4c` · Bug-repro tests, verified red/green

---

_Implementation detail may live in git history on `origin/dev`._
