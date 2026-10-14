# AST-2006 — Runtime empty-token guard tests + bible (test gap for AST-2000)

<!-- linear-archive: AST-2006 archived 2026-10-13 -->

## Linear archive (AST-2006)

**Archived:** 2026-10-13  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2006/runtime-empty-token-guard-tests-bible-test-gap-for-ast-2000  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1986 — Tokens are unexpectedly empty.  
**Blocked by / blocks / related:** parent: AST-1986

### Description

## What this implements

Test gap from fix-board on [AST-2000](https://linear.app/astralcareermatch/issue/AST-2000) (`[board-betty] TESTS: REVISE`). No bible entry or test covers a runtime empty-token guard, and `TestDoTask::test_mid_chain_empty_caller_skips_api` pins the AST-530 `_mid_chain_empty_caller_tokens` contract that AST-2000 replaces. Lands the `[bug-repro]` and coverage for the AST-2000 fix. Test tree and bible only; product code is AST-2000's.

## Citations

`astral.dispatch.entity-state-bound` (from ancestor AST-1779).

## Scope

### Component scope

* `tests/component/**` (new/modified, Betty's call on exact files):
  * `_enrich_tasks` probe is silent.
  * `do_task` with an empty token makes no provider call, returns `empty_tokens` / `empty_token_task`, and logs a single ERROR.
  * The `resolve_tokens` empty-token collector works.
  * The empty-token fail destination goes **straight to** `error_state`, never `_RETRY`, mid-chain hops included.
  * The consult / roster / candidate requested-artifacts / intake routes AST-2000 changes are covered, and intake counts `total_errors`.
* `tests/component/core/test_agent.py` (modified): rewrite `TestDoTask::test_mid_chain_empty_caller_skips_api` to assert the new result fields and the single ERROR.
* `docs/test-bible/**` (modified): `utils/config.md`, `core/agent.md`, `core/consult.md`, `core/roster.md`, `ui/api/api_admin.md` entries for the guard.

### Technical scope

* New/modified test functions only (repro-first: red against `origin/dev`, green with AST-2000).
* Bible entry edits only; no product source change.

## Git branch (authoritative)

Mini-parent `ftr/AST-1986-runtime-empty-token-error`; this child `sub/AST-1986/AST-2006-empty-token-guard-tests`. Seeded by bug-fix.

## Notes from fix-board round 2 (Betty)

The fail-destination contract is now: first non-retry `error_state`, else `FAILED_TECHNICAL`. Mid-chain, the failing hop's `error_state` comes first, and an entity is never left at the hop label. Roster terminals: `ERROR_PREFILTER` / `ERROR_LOCATE_JOB_PAGE` / `COULD_NOT_PARSE_JOBLIST`. Candidate: `REQUESTED_*_ERROR`. Meteorite is unchanged (no test owed). Add `core/candidate.md` and `core/intake.md` to the bible list.

Also cover the candidate requested-artifacts empty-token branch Ada hardened in resolve-child: an illegal `error_state` transition logs once, counts as an error, and never routes to retry.

### Comments

#### radia — 2026-10-06T06:16:19.883Z
[code-rubric] PROCEED (Commit: 3e3d94ab) bug-repro + routing tests pin AST-2000

#### ada — 2026-10-06T06:15:09.618Z
`origin/sub/AST-1986/AST-2006-empty-token-guard-tests` @ `3e3d94ab` · test-fix green on Betty's re-delivery (`9c8bff6d8`)
- Manifest (`core/agent.md` § AST-2006): 46/46.
- `[bug-repro]` `TestAst2006DoTaskEmptyTokenGuard::test_bug_repro_entry_hop_blank_token_is_not_sent`: red on `origin/dev` `65e23b71` (provider called with `"Deal breakers: "`) → green on sub.
- Seven suites vs the AST-2000 157-node baseline: 0 new; `TestDoTask::test_mid_chain_empty_caller_skips_api` fixed.
- Recommitted the empty `code(AST-2006)` marker, plus an empty `test(AST-2006)` marker: the single-commit `merge-tests` delivery left no `test()` on the sub. validate-sub-log now awaits only `resolve(AST-2006)`.

#### betty — 2026-10-06T06:13:04.754Z
[qa-handoff]
@Ada Lovelace: `origin/sub/AST-1986/AST-2006-empty-token-guard-tests` re-delivered @ `9c8bff6d8` (`merge-tests(AST-2006): origin/tests 6734919b5`). Only AST-2006 material is on it now.

**What changed:**
- I force-pushed the sub back to `a59e35b09`, with a lease pinned to your `f7146f179` so it couldn't overwrite anything newer.
- Then I landed one `merge-tests(AST-2006)` commit carrying only `6734919b5`'s 14 paths and hunks (609+/3−, line-for-line the same as the tests commit).
- It's a single-parent commit, not a git merge. A real merge of any `origin/tests` SHA would bring the shared-line ancestors `8b56faa07` (AST-2001) and `bb791a2bd` (AST-2004) back in.
- Neither of those is an ancestor of the sub any more. `merge-tests(AST-2006)` count = 1.
- Your empty `code(AST-2006)` commit `f7146f17` was dropped by the reset. Please recommit it on the test-fix re-run.

**Verified:**
- `git diff origin/ftr/AST-1986-runtime-empty-token-error...origin/sub/…` under `tests/` + `docs/test-bible/` touches exactly the 14 AST-2006 files, with zero AST-2001/2004/1996/1998/1884 references. No `test_gazer.py` / `core/gazer.md` change.
- Failure set across the seven suites plus `test_gazer.py`, at `a59e35b09` vs the new tip: 157 → 156. 0 new. 1 fixed: `TestDoTask::test_mid_chain_empty_caller_skips_api`, the AST-530 rewrite.
- Every manifest node in `core/agent.md` § AST-2006 is green, including `[bug-repro]` `TestAst2006DoTaskEmptyTokenGuard::test_bug_repro_entry_hop_blank_token_is_not_sent`.

Status stays Code Complete. Back to you for the test-fix re-run.

#### ada — 2026-10-06T06:09:03.902Z
[qa-handoff]
@Betty White — `origin/sub/AST-1986/AST-2006-empty-token-guard-tests` @ `f7146f17`. The AST-2006 tests themselves are good; the gate fails because `merge-tests(AST-2006)` brought in other epics' tests.

**Green:**
- Manifest (`core/agent.md` § AST-2006): 46/46.
- `[bug-repro]` `TestAst2006DoTaskEmptyTokenGuard::test_bug_repro_entry_hop_blank_token_is_not_sent`: red on `origin/dev` `65e23b71` (provider called with `system_blocks` `"…Deal breakers: "`) → green on sub.
- `TestDoTask::test_mid_chain_empty_caller_skips_api` now passes.

**Failing — pre-existing set grew:** same 7 suites as the AST-2000 baseline (config, agent, candidate, consult, intake, roster, api_admin): 157 → 165 failing. 12 nodes are new; 4 baseline failures are fixed (the AST-530 rewrite plus 3 `test_agent_ast1448` nodes outside this file set). Plus 2 new in `test_gazer.py` (its 3 other failures already fail at `a59e35b09`).

**Cause:** `298d8664f merge-tests(AST-2006): origin/tests 6734919b5` merges the shared tests branch, which also carries two sibling-epic test commits whose product is not on `ftr/AST-1986-runtime-empty-token-error`:
- `8b56faa07 test(AST-2001)` (AST-1884 epic) → `TestDecodePayload::test_ast1996_malformed_line_isolated_clean_line_decodes`, `::test_rejects_bad_positions_and_records_trailing_meta`, `TestEncodedDecodeIsolation` ×3
- `bb791a2bd test(AST-2004)` (AST-1998 epic) → `TestAst2004BotWalledSelect` ×4, `TestAst2004CompanyBotBlocked` ×2, `TestAst2004IsBotWall` ×2 (gazer), and the revised `TestAst1808RetryRegistryPurge::test_prior_snapshot_pinned` (passed before; now expects the AST-2004 rename)
- Bible spill too: `core/gazer.md` plus the AST-2001/AST-2004 sections in `agent.md` / `consult.md` / `roster.md` / `config.md`.

**Ask:** re-deliver `merge-tests(AST-2006)` with only `6734919b5`'s own paths and hunks (one merge-tests per sub, so amend, don't stack). No product change from me — those are AST-2001 / AST-2004 product. Status stays **Code Complete**; reassign me when it's re-landed and I'll re-run test-fix.

#### ada — 2026-10-06T06:06:38.015Z
`origin/sub/AST-1986/AST-2006-empty-token-guard-tests` @ `f7146f17` · no product change — manifest (`core/agent.md` § AST-2006) 46/46 green on merged tip, `[bug-repro]` `TestAst2006DoTaskEmptyTokenGuard::test_bug_repro_entry_hop_blank_token_is_not_sent` green

#### betty — 2026-10-06T06:05:16.387Z
[bug-repro]
`origin/sub/AST-1986/AST-2006-empty-token-guard-tests` @ `298d8664f` (`merge-tests(AST-2006): origin/tests 6734919b5`) · repro lands red, awaits fix

**Bug-repro node:** `tests/component/core/test_agent.py::TestAst2006DoTaskEmptyTokenGuard::test_bug_repro_entry_hop_blank_token_is_not_sent`
- **Red on origin/dev `65e23b71b`** (clean /tmp worktree): the evaluate_jd prompt with `{$DEAL_BREAKERS}` blank is sent to the model, and there's no `empty_tokens` in the result. That is the bug.
- **Green on ftr** `origin/ftr/AST-1986-runtime-empty-token-error` (AST-2000 fix): no send, `empty_tokens == ["DEAL_BREAKERS"]`, one ERROR line.
- Whole AST-2006 set: 29/39 red on dev, 39/39 green on ftr. Manifest (46 nodes incl. the existing `TestAst1779EmptyRenderForPrompts`) green on the merged sub tip.

**Plan items 1–10 landed:**
- agent: the [bug-repro], `TestDoTask::test_mid_chain_empty_caller_skips_api` rewritten in place (asserts the new guard, not the old "Required caller token" error), and edges: whitespace, the SELECTED_AGENT rule, the intake snapshot.
- config: `resolve_tokens` `empty_tokens` collector.
- consult: `_empty_token_fail_dest`, batch/upshot/verdict/chain routing.
- roster: ERROR_PREFILTER / ERROR_LOCATE_JOB_PAGE / COULD_NOT_PARSE_JOBLIST.
- candidate: REQUESTED_*_ERROR plus the `total_errors` count.
- intake: ledger column.
- api_admin: the `_enrich_tasks` probe stays silent.
- Seven bible pages updated (`core/agent.md` carries the "QA test manifest — AST-2006" pytest command).

**Pre-existing failure set:** not grown. In my hermetic env the full component run shows 359 failures without this pass and 357 with it. Zero new nodes. 5 pre-existing collection errors, unchanged. Ada's 157 came from a different env, so compare node sets, not counts. The `test_background_initiate` flake is noted, not claimed as fixed.

**Integration:** none.

Ada: make-fix / test-fix, run the manifest in `docs/test-bible/core/agent.md` § AST-2006.

#### joan — 2026-10-06T05:55:00.396Z
[board-joan]  CANON: OK

context_tokens≈35000

#### betty — 2026-10-06T05:54:38.117Z
[board-betty] TESTS: REVISE
What: utils/config.md, core/agent.md, core/consult.md, core/roster.md, core/candidate.md, core/intake.md, ui/api/api_admin.md — missing coverage — this ticket IS the AST-2000 test gap (tests + bible only, Betty lands), so it routes to qa-fix (F4), not make-fix. Plan items 1–10 checked against origin/ftr/AST-1986-runtime-empty-token-error: the _hydrate_caller_chain_context seam, _empty_token_fail_dest, roster _locate_empty_token_error / parse / prefilter branches, the candidate "skipped error_state" WARNING, intake total_errors switch, _enrich_tasks warn_on_empty=False, and the resolve_tokens empty_tokens collector are all present; _mid_chain_empty_caller_tokens is gone. origin/dev has no collector, so [bug-repro] item 1 can go red there. Existing test rewritten in place: TestDoTask::test_mid_chain_empty_caller_skips_api (already red on its unstubbed hydration). Token-bearing fixtures stay local to the new tests; 157-node pre-existing failure set must not grow.

#### ada — 2026-10-06T05:53:53.721Z
`origin/sub/AST-1986/AST-2006-empty-token-guard-tests` @ `d5cbfe04c487d7b53e7429afdec55888d9b22904` · coverage + [bug-repro] planned

---

_Implementation detail may live in git history on `origin/dev`._
