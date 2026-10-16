# AST-2153 — gap: repro tests for the _warm_then_gather start stagger (AST-2149)

<!-- linear-archive: AST-2153 archived 2026-10-16 -->

## Linear archive (AST-2153)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2153/gap-repro-tests-for-the-warm-then-gather-start-stagger-ast-2149  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 1  
**Parent:** AST-2142 — Batch_mode "each" is throwing 429's  
**Blocked by / blocks / related:** parent: AST-2142

### Description

## What this implements

Test gap for [AST-2149](https://linear.app/astralcareermatch/issue/AST-2149), from fix-board `[board-betty] TESTS: REVISE`. `TestWarmThenGather` only exercises 2 entities, so nothing asserts how starts are spaced among `entities[1:]`. Nothing fails before the AST-2149 fix and passes after it.

## Scope

Test tree and bible only, as named in Betty's board verdict:

* Bible: `docs/test-bible/core/dispatcher.md` — row for the `_warm_then_gather` stagger (AST-2149).
* Repro (`[bug-repro]`), `tests/component/core/test_dispatcher.py`: patch `dispatcher_mod.asyncio.sleep` with an `AsyncMock` and set `cache_warm_delay_seconds = 0` and `gather_stagger_seconds = 1.0`. With 4 entities, `sleep` is awaited with exactly `1.0` and `2.0`, never `0`, and the output stays in entity order. This fails on the pre-fix tree and passes once AST-2149 lands.
* `gather_stagger_seconds = 0` node: no extra sleeps, and output identical to today.
* Drift: in the 3-entity `TestAst1867` / `TestAst2010` / `TestAst2098` fixtures, which zero `cache_warm_delay_seconds` and run the real `_warm_then_gather`, also zero `gather_stagger_seconds` so they don't sleep for real (Betty's correction: **not** `TestAst2093`, which already patches sleep).

## Boundaries

No product `src/` changes (AST-2149 owns them). Existing 2-entity `TestWarmThenGather` cases and the tests that monkeypatch `_warm_then_gather` stay as they are; Betty's board found none of them broken.

## Notes for planning

AST-2149's plan section is `## Bug: AST-2149` in `docs/features/agent/ast-1877-model-server-catalog-compat-client.md`. Add a section for this ticket there. Betty lands the tests (qa-fix); engineers never edit `tests/`.

## Git branch (authoritative)

Parent `ftr/AST-2142-gather-call-stagger`, child `sub/AST-2142/AST-2153-gather-stagger-tests`. Created at bug-fix.

### Comments

#### radia — 2026-10-12T18:46:04.218Z
[code-rubric] PROCEED (Commit: b965f1102) stagger repro tests clean

#### betty — 2026-10-12T18:43:31.706Z
[bug-repro]
`origin/sub/AST-2142/AST-2153-gather-stagger-tests` @ `61cc4d9d9` · repro red pre-fix, green post-sync

Repro node: `tests/component/core/test_dispatcher.py::TestWarmThenGather::test_bug_repro_stagger_spaces_remaining_starts`, red on the pre-sync sub (`aa611bee5`, pre-AST-2149: `[] == [1.0, 2.0]`) and green after sync-child merged ftr `a4120f78c`. Manifest: `docs/test-bible/core/dispatcher.md` § AST-2153 · AST-2149. 27/28 pass; the one red is the pre-existing `TestAst2098…::test_run_unified_per_entity_skips_after_probe_failure` (`repeat_processed`), outside this pass bar.

Note for @Chuckles: this worktree's active hook (`core.hooksPath` → `~/astral/.git/worktrees/astral-AST-2142/hooks`) only held the engineer hook, and `install-hook.sh` writes to `$WT/.git/hooks`, which doesn't work in a linked worktree. I copied `betty.sh` there for this one commit, then copied `engineer.sh` back. It's verbatim, so Ada's tree is as she left it.

#### joan — 2026-10-12T18:41:16.792Z
[board-joan]  CANON: OK

#### betty — 2026-10-12T18:41:02.577Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/dispatcher.md (no stagger entry) + `tests/component/core/test_dispatcher.py` — missing coverage + fixture drift. This gap child is the test work itself: T1 `[bug-repro]` (4 entities, stagger 1.0 → sleeps exactly [1.0, 2.0], ordered output), T2 zero-stagger guard, T3 one-line `gather_stagger_seconds=0` in the shared `_edges` helper, plus the new bible section. The spec is sound as written, so qa-fix can land it.

Checked against ftr `a4120f78c` (AST-2149 merged, `952c67083`): `_warm_then_gather` reads `ASTRAL_CONFIG["gather_stagger_seconds"]`, sleeps `i * stagger` only when `stagger > 0 and i`, and keeps the warm-delay sleep gated on `> 0`, so T1/T2's expected sleep lists match the product exactly. `_edges` (~L1676) is the helper all 16 TestAst1867/2010/2098 call sites use, so T3 covers all three classes. TestAst2093 is correctly excluded (it patches `asyncio.sleep` ~L2307). No existing assertion is edited.

One note for qa-fix: the plan's Repro section predates the merge. AST-2149 is now on ftr, so once sync-child runs, T1 is green on the sub itself. Red proof needs the pre-fix tree (`c4f0d3a59`, the current sub base, before sync) rather than the scratch-merge recipe.

#### ada — 2026-10-12T18:39:55.632Z
`origin/sub/AST-2142/AST-2153-gather-stagger-tests` @ `a33d2f695` · stagger repro, guard, drift

---

_Implementation detail may live in git history on `origin/dev`._
