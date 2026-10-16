# AST-2097 — Unblock AST-2094: pick who owns "empty rubric → Invalid" (AST-2092 vs AST-2091) and how Betty publishes the tests

<!-- linear-archive: AST-2097 archived 2026-10-16 -->

## Linear archive (AST-2097)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2097/unblock-ast-2094-pick-who-owns-empty-rubric-invalid-ast-2092-vs-ast  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** unassigned  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-2019; related: AST-2013

### Description

## What's needed

Two picks for [AST-2019](https://linear.app/astralcareermatch/issue/AST-2019) (Abrams' `qualify_job_listings` dumped 10 jobs into `ERROR_QUALIFY_JOB_LISTINGS` because `{$RUBRIC_VECTORS}` was empty and Scheduled Actions didn't flag it). The product fix [AST-2092](https://linear.app/astralcareermatch/issue/AST-2092) is done, reviewed clean, and merged on `ftr/AST-2019-rubric-empty-render-gate`. Its test-gap sibling [AST-2094](https://linear.app/astralcareermatch/issue/AST-2094) is blocked.

### 1. Overlap with [AST-2091](https://linear.app/astralcareermatch/issue/AST-2091/scheduled-actions-block-autorun-on-duplicate-or-empty-rubric-ast-2013) — who owns "empty rubric → Invalid"?

[AST-2091](https://linear.app/astralcareermatch/issue/AST-2091) (Hedy, Plan Discuss, under [AST-2013](https://linear.app/astralcareermatch/issue/AST-2013)) also marks a Scheduled Actions row Invalid when the candidate's rubric is **empty**, alongside **duplicate codes**. It uses a new helper in `candidate.py`, plus a refusal inside `dispatcher.run_task`. [AST-2092](https://linear.app/astralcareermatch/issue/AST-2092/fix-score-rubric-tokens-in-the-scheduled-actions-empty-render-gate-ast) already covers the empty case through the token gate (`empty_render_for_prompts` now scores `{$RUBRIC_VECTORS}` and the pinned rubric tokens). If both ship, the same rule lives in two places, and an empty rubric shows two reasons in the tooltip.

One gap [AST-2092](https://linear.app/astralcareermatch/issue/AST-2092/fix-score-rubric-tokens-in-the-scheduled-actions-empty-render-gate-ast) does **not** close: AUTO is only forced off when the Scheduled Actions page loads. A sweep that is already on AUTO can still fire before anyone opens the page. AST-2091's `run_task` refusal is what closes that.

* **(A) — recommended:** keep [AST-2092](https://linear.app/astralcareermatch/issue/AST-2092/fix-score-rubric-tokens-in-the-scheduled-actions-empty-render-gate-ast) for empty. [AST-2091](https://linear.app/astralcareermatch/issue/AST-2091/scheduled-actions-block-autorun-on-duplicate-or-empty-rubric-ast-2013) narrows to **duplicate codes**, plus a `run_task` refusal that reuses the same `empty_render` check, so scheduled sweeps are covered for both cases.
* **(B):** keep both as planned and accept the duplicate rule.
* **(C):** drop [AST-2092](https://linear.app/astralcareermatch/issue/AST-2092/fix-score-rubric-tokens-in-the-scheduled-actions-empty-render-gate-ast) and let [AST-2091](https://linear.app/astralcareermatch/issue/AST-2091/scheduled-actions-block-autorun-on-duplicate-or-empty-rubric-ast-2013) own empty ([AST-2019](https://linear.app/astralcareermatch/issue/AST-2019/abrams-qualify-job-listings-completed-10-errors-10-processed-qualify) would close without landing).

### 2. How Betty publishes AST-2094's tests

Betty's tests are written and green (`5d0cc5aaa`, 9/9 in the class). But `origin/tests` currently carries an [AST-2091](https://linear.app/astralcareermatch/issue/AST-2091/scheduled-actions-block-autorun-on-duplicate-or-empty-rubric-ast-2013) plan doc and 7 AST-2081/AST-2088 tests whose product code isn't on `dev`. A plain merge-tests would drag all of that onto AST-2094's sub.

* **(i) — recommended:** the AST-2079/AST-2090 precedent. Betty re-lands `test(AST-2094)` on a branch based on the ftr base (`823d37605`), merges that into `tests`, then merge-tests that SHA, so the sub carries only [AST-2094](https://linear.app/astralcareermatch/issue/AST-2094/rubric-empty-render-gate-tests-bible-test-gap-for-ast-2092).
* **(ii):** merge-tests as-is, accepting the leaked doc and the 7 extra failures on this sub.

Also from Betty: her local `tests` branch held an unpublished [AST-2090](https://linear.app/astralcareermatch/issue/AST-2090/salvaged-batch-split-routing-tests-bible-test-gap-for-ast-2089) qa-fix pass sitting on a forbidden merge. She tagged it `backup/ast-2090-qa-fix` (`8f51ba95a`) and reset local `tests` to `origin/tests`, so [AST-2090](https://linear.app/astralcareermatch/issue/AST-2090/salvaged-batch-split-routing-tests-bible-test-gap-for-ast-2089) still needs its own clean publish.

## How to answer

Reply here with your two picks (e.g. **A + i**) and move this ticket to **Done**. Neither [AST-2019](https://linear.app/astralcareermatch/issue/AST-2019/abrams-qualify-job-listings-completed-10-errors-10-processed-qualify) nor [AST-2094](https://linear.app/astralcareermatch/issue/AST-2094/rubric-empty-render-gate-tests-bible-test-gap-for-ast-2092) is assigned to you. The agents pick them up when this is Done.

### Comments

#### susan — 2026-10-09T02:49:46.019Z
A + i

---

_Implementation detail may live in git history on `origin/dev`._
