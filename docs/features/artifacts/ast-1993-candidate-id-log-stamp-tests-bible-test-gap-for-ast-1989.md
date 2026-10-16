# AST-1993 — candidate_id log stamp tests + bible (test gap for AST-1989)

<!-- linear-archive: AST-1993 archived 2026-10-13 -->

## Linear archive (AST-1993)

**Archived:** 2026-10-13  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1993/candidate-id-log-stamp-tests-bible-test-gap-for-ast-1989  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** betty  
**Priority / estimate:** None / 2  
**Parent:** AST-1986 — Tokens are unexpectedly empty.  
**Blocked by / blocks / related:** parent: AST-1986

### Description

## What this implements

Test gap from fix-board on [AST-1989](https://linear.app/astralcareermatch/issue/AST-1989) (`[board-betty] TESTS: REVISE`): no existing test exercises any `log_candidate_id` set site — the logging bible entry says nothing sets it yet, and the only candidate-id test (AST-1598) sets the contextvar itself. Lands the `[bug-repro]` and coverage for the AST-1989 fix. Test tree + bible only; product code is AST-1989's.

## Citations

`astral.standards.logging-via-utils` (from ancestor AST-1598).

## Scope

### Component scope

* `tests/component/**` (new/modified, Betty's call on exact files) — each of the five entry points AST-1989 touches (dispatcher `_dispatch_one`, `do_task` via `_with_log_debug` incl. run_next hops, intake runs, UI artifact generate in `candidate.py`, meteorite `_hold_log_batch`) stamps `candidate_id` on `app_log` rows and restores the prior value on exit.
* `tests/component/**` logging console tests (modified) — both console formatters render `name [cid]: message` when a candidate is set; unchanged output when unset.
* `docs/test-bible/**` logging / affected component entries (modified) — drop "nothing sets candidate id yet", describe the new set sites and console shape.

### Technical scope

* New test functions per entry point above (repro-first: red against pre-fix tree, green with AST-1989).
* New/modified console formatter test cases for the `[cid]` prefix.
* Bible entry edits only — no product source change.

## Boundaries

* No product source change (AST-1989 owns it).
* No test for AST-1986 symptom 2 (empty `anticipate_scan` job tokens) — deferred by plan decision D3, pending Susan.

## Notes for planning

Plan section lives in `docs/features/candidate/ast-1598-job-and-app-log-candidate-id.md` (`## Bug: AST-1989`). Runs after AST-1989 merges into `ftr/AST-1986-log-candidate-id`.

## Git branch (authoritative)

Mini-parent `ftr/AST-1986-log-candidate-id`; this child `sub/AST-1986/AST-1993-candidate-id-log-tests`. Seeded by bug-fix.

### Comments

#### betty — 2026-10-06T04:43:12.645Z
@susan — qa-fix on AST-1993 is on hold (scope collision). Nothing committed, worktree untouched. Status stays Plan Discuss.

1. **Two fixes for the same thing.** `ftr/AST-1986-log-candidate-id` (AST-1989) and `ftr/AST-1987-railway-log-batch-candidate-ids` (AST-1988) each wire `log_candidate_id` across the same six files (`src/utils/logging.py`, dispatcher, agent, candidate, intake, meteorite). Neither ftr contains the other, and the designs conflict:
   - Railway console: AST-1989 puts `name [cid]: message` in the message text (D1). AST-1988 adds separate `candidate_id` / `batch_id` JSON keys and leaves the message untouched.
   - `_hold_log_batch`: AST-1989 always returns a `(batch, candidate)` pair and sets the candidate only if no outer candidate is set. AST-1988 returns `None` when a parent batch is set; otherwise it sets both.
   Whichever reaches dev second will conflict, and the tests for one design fail on the other.
2. **Shared tests branch.** AST-1991 (AST-1988's test sibling) is in qa-fix right now in this same `astral-tests` worktree, with uncommitted tests for AST-1988 in the five files AST-1993 also needs to change. Every `merge-tests` publishes all of `origin/tests`. So once AST-1991 commits, its tests reach `sub/AST-1986/...`, and AST-1993's would reach `sub/AST-1987/...`. Each set would go red on the other's product.

Need from you: which ftr is canonical for candidate_id stamping (or whether AST-1986 and AST-1987 should merge into one fix), and which console shape you want. Once you decide, I'll write AST-1993's tests against that design.

#### joan — 2026-10-06T04:42:21.410Z
[board-joan]  CANON: OK

#### betty — 2026-10-06T04:42:11.244Z
[board-betty] TESTS: REVISE
What: docs/test-bible/utils/logging_batch.md + utils/debug_logging.md (+ core/dispatcher|agent|intake|candidate|meteorite.md) — missing coverage — this ticket IS the AST-1989 test gap (test-tree + bible only, Executor = Betty) so it routes to qa-fix (F4), not make-fix. Plan sections 1–7 checked against origin/ftr/AST-1986-log-candidate-id: all five set sites, _candidate_tag/_PlainConsoleFormatter, _hold_log_batch/_release_log_hold present; red baseline cc256733f and green 9404ae9c6 both on ftr. Restore semantics per site (token-reset vs set(None)) match product. No existing test broken; new tests must reset log_candidate_id in finally to protect TestConsoleFormat exact-format asserts. No symptom-2 test (D3).

#### hedy — 2026-10-06T04:41:30.246Z
`origin/sub/AST-1986/AST-1993-candidate-id-log-tests` @ `f91d56e93348e1bb18165ce8bc3435c698f10f41` · plan ready

---

_Implementation detail may live in git history on `origin/dev`._
