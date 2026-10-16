# AST-2095 — Batch-unique index decode/assembly/count tests + bible (test gap for AST-2093)

<!-- linear-archive: AST-2095 archived 2026-10-16 -->

## Linear archive (AST-2095)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2095/batch-unique-index-decodeassemblycount-tests-bible-test-gap-for-ast  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-2012 — [✅/Somerset] meteorite_grade_get COMPLETED: 23 error(s) / 52 processed | meteorite_grade_get-a4ec9af6-55e0-4bb6-92a9-2c4754009971  
**Blocked by / blocks / related:** parent: AST-2012

### Description

## What this implements

Test-tree and bible coverage for [AST-2093](https://linear.app/astralcareermatch/issue/AST-2093)'s batch-unique row index and index → entity decode map. Routed here from Betty's fix-board `[board-betty] TESTS: REVISE` on AST-2093 (same shape as AST-2090 for AST-2089). No product source change.

## Scope

## Component scope

* `tests/component/core/test_agent.py` (modified). Add `[bug-repro]` coverage for the `_decode_payload` map path: a chunk-1 reply whose lines all echo `000` no longer collapses onto entity 0, indexes `020`–`039` map to the right entities, an unknown index is skipped (its entity ends up "omitted"), and a duplicate index produces one `decode_failures` row. Positional decode with no map stays unchanged.
* `tests/component/core/test_consult.py` (modified). Add coverage that `_consult_scored_dispatch_batch_encoded` assembles rows as `[index=020]: …` with no `000: ` double prefix, that `render_verdict` carries `batch_index`, and that the index map reaches `do_task` context from `_run_batch_consult`. The existing `[index=000]: jd text` default-position node stays green.
* `tests/component/core/test_dispatcher.py` (modified). Add coverage for `_run_unified` chunk and per-entity index offsets, and for `_run_dispatch_loop`'s `repeat_processed` dedupe (each entity counted once across retry runs). The existing mocked `_run_task` summary nodes stay green.
* `docs/test-bible/core/agent.md`, `docs/test-bible/core/consult.md`, `docs/test-bible/core/dispatcher.md` (modified). New `AST-2093` blocks matching the tests.

## Technical scope

* `tests/component/core/test_agent.py`: new test function(s) for the map-based decode branches (hit, unknown, duplicate, no-map fallback).
* `tests/component/core/test_consult.py`: new test function(s) for single-label assembly, `render_verdict` batch index, and the index map in the `do_task` context.
* `tests/component/core/test_dispatcher.py`: new test function(s) for chunk offsets and the processed-count dedupe.
* Bible files: new manifest rows so the bible matches the tests.

## Acceptance criteria

- [X] The repro tests pass on the AST-2093 tip and would have failed before it (every `000` line collapses onto the first entity, and the rest are "omitted").
- [ ] `agent.py`, `consult.py`, and `dispatcher.py` stay at 100% branch coverage (LOCKED_AT_100).
- [X] Existing nodes Betty reviewed stay green as written.
- [X] Bible blocks match the tests.

## Boundaries

* No `src/` or `data/` change. AST-2093 owns the product fix.
* Pre-existing reds on `ftr` are out of scope.

## Notes for planning

Betty's verdict comment on AST-2093 (`[board-betty] TESTS: REVISE`) names the exact gaps. Doc to patch: `docs/features/agent/response-validation-layers.md`, with a `## Bug: <this id>` block alongside AST-2093's. Blocked by AST-2093 so the tests run against the fix on `ftr`.

## Git branch (authoritative)

Parent `ftr/AST-2012-grade-batch-unique-index`; this child `sub/AST-2012/AST-2095-grade-batch-unique-index-tests`. Registry is authoritative.

### Comments

#### radia — 2026-10-09T06:36:11.684Z
[code-rubric] REVIEW (Commit: 51f234e12) — Tests solid; no fix-now.

- **[bug-repro]:** 8 repro nodes assert AST-2093's to-be (distinct batch indexes, single `[index=NNN]` label, dedupe count 27 not 50) — real locks, not tautologies.
- **What must still hold:** intact — additive `TestAst2093*` classes only; the five qa-handoff dispatcher nodes untouched.
- **Discuss (merge routing):** sub tip carries `src/`/`data/` from `sync(dev)` — not AST-2095 product work; confirm the rollup onto ftr is safe.
- **Discuss (bible):** `agent.md` AST-2095 manifest row 4 scope-gate claim is stale after the dev sync.
- **Advisory:** coverage AC proven at branch level (all AST-2093-added lines/branches covered).

Full findings: `docs/features/agent/response-validation-layers.md` § Radia review — AST-2095.

#### hedy — 2026-10-09T06:33:54.573Z
`origin/sub/AST-2012/AST-2095-grade-batch-unique-index-tests` @ `51f234e12` (pushed the clean sync merge with dev `86bcca2f0` and ftr `759a19247`; no product commit). Repro gate: 8/8 `[bug-repro]` green. test_agent/test_consult/test_dispatcher: base (dev+ftr, without this sub) had 80 failed / 851 passed; tip had 80 failed / 874 passed. The failing ids are identical, with zero new reds, and the +23 passes are Betty's new nodes.

#### hedy — 2026-10-09T05:14:24.371Z
`origin/sub/AST-2012/AST-2095-grade-batch-unique-index-tests` @ `47564e1fd` (synced locally to `51f234e`; no product commit). 8/8 `[bug-repro]` and 23/23 `TestAst2093*` green. The 3-suite run is 80 failed / 874 passed, and none of the failures are in AST-2093/2089/2091 nodes. Branch coverage is 100% on every line AST-2093 added (agent decode block, consult, dispatcher). The LOCKED_AT_100 AC is left unticked: module-wide totals weren't measurable on a run carrying the 80 pre-existing reds (agent.py shows 89% there).

#### betty — 2026-10-09T05:12:28.110Z
[check-linear] Tests Ready — sync conflict resolved, republished (@Hedy Lamarr, make-fix)
`origin/sub/AST-2012/AST-2095-grade-batch-unique-index-tests` @ `47564e1fd` (`sync(dev): origin/dev` on `ff284badc`). The ftr `759a19247` was already contained.
- `tests/component/core/test_consult.py`: kept both classes, dev's `TestAst2089SalvagedBatchSplit` first, then `TestAst2093EncodedDispatchIndex`.
- `docs/test-bible/core/dispatcher.md`: kept both sections, dev's `### AST-2091 · AST-2013` first, then `### AST-2093 · AST-2012`.
Verify with `/home/susan/astral/.venv/bin/python -m pytest` on `test_agent.py`, `test_consult.py` and `test_dispatcher.py`: all 23 `TestAst2093*` pass, and dev's AST-2089/AST-2091 classes pass. The full three-file run has 80 failed / 874 passed, and the 80 failing ids are identical to a dev + ftr base without AST-2095.
Compile is ok. Lint has no new rule codes vs that base.
Manifest unchanged (`docs/test-bible/core/agent.md` § QA test manifest — AST-2095). Your sync-child should now merge clean.

#### hedy — 2026-10-09T05:10:38.419Z
[check-linear] blocked: sync-child merge conflict in test-tree paths (exit 3). No product gap.
@Betty White: `sync-child.sh sub/AST-2012/AST-2095-grade-batch-unique-index-tests --ftr AST-2012-grade-batch-unique-index` stops when it merges `origin/sub/AST-2012/AST-2095-grade-batch-unique-index-tests` (`ff284badc`) into dev + ftr. Your ref predates two additions now on `origin/dev`, and both sides append at the same insertion point:

- `tests/component/core/test_consult.py` (~line 2435): dev's `class TestAst2089SalvagedBatchSplit` vs your `class TestAst2093EncodedDispatchIndex`.
- `docs/test-bible/core/dispatcher.md` (~line 772): dev's `### AST-2091 · AST-2013 (run_task rubric gate)` vs your `### AST-2093 · AST-2012 (…)` block.

Both conflicts are additive, so the resolution is to keep both blocks (dev's first, then yours). They're test-tree paths, so I aborted the merge rather than resolve them. Please merge `origin/dev` into your ref and republish.

Product check: I exported the synced tree (dev + ftr @ `759a19247`) and overlaid your three test files from `ff284badc`. All 23 `TestAst2093*` nodes pass, including all 8 `[bug-repro]` (`-k bug_repro`: 8 passed). No `src/` change is needed. I'll exit Code Complete once the sync is clean.

Status stays Tests Ready. Reassign to me when it's republished.

#### betty — 2026-10-09T05:09:21.190Z
[bug-repro]
`origin/sub/AST-2012/AST-2095-grade-batch-unique-index-tests` @ `ff284badc` · repro red pre-fix, green on ftr
@Hedy Lamarr — 23 new nodes across three classes: `TestAst2093BatchIndexMapDecode` (agent), `TestAst2093EncodedDispatchIndex` (consult), `TestAst2093BatchIndexDispatch` (dispatcher). The manifest and node-by-node table are in `docs/test-bible/core/agent.md` § QA test manifest — AST-2095, with consult/dispatcher rows in their § AST-2093 blocks.
- **Red at pre-fix base** (`git archive 823d37605` + these test files): all 8 `[bug-repro]` nodes fail for the plan's reason. The chunk-1 `000` echo gives 20 rows all on `J20`, global `020`–`039` gives 0 rows, rows read `000: [index=000]: jd`, `batch_index_offset` is absent, `repeat_processed` is missing, and the loop total is 50 instead of 27.
- **Green at the publish tip** (AST-2093 product @ `759a19247`): all 23 pass. The failing set across the three files is identical to the 80 pre-existing reds, and every line and branch AST-2093 added is covered.
- **Unchanged:** the 5 AST-2093 qa-handoff nodes in `test_dispatcher.py` were not touched. There's no `src/` or `data/` diff, so make-fix has nothing to fix; test-fix just reruns the manifest.

#### joan — 2026-10-09T05:01:48.438Z
[board-joan]  CANON: OK

#### betty — 2026-10-09T05:01:26.809Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/agent.md + core/consult.md + core/dispatcher.md (no AST-2093 block yet) — missing coverage — the entire fix is test-tree + bible (plan nodes 1–19 plus three AST-2093 bible blocks), which engineers can't commit. qa-fix (F4) has to land it, and the [bug-repro] nodes 1, 2, 3, 8, 14, 15, 16, 18 must be shown red at 823d37605 and green at the ftr tip 759a19247. Spot-checked the plan against source on both sides, and everything matches: base out-of-range skip (node 2 red = 0 rows), tip duplicate-index reason / unknown-index warning / "bad position field" / "X requires confidence digit 0" strings, and the consult row_indexes / batch_index_offset / render_verdict batch_index plumbing. No product question. make-fix should be no-op or sanity-only once qa-fix exits Tests Ready.

#### hedy — 2026-10-09T02:46:24.194Z
`origin/sub/AST-2012/AST-2095-grade-batch-unique-index-tests` @ `6f2c3d23c` · 19 nodes, bible blocks

---

_Implementation detail may live in git history on `origin/dev`._
