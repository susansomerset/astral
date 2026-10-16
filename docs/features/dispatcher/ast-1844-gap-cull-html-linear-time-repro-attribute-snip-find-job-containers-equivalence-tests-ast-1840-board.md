# AST-1844 — gap: _cull_html linear-time repro + attribute snip + find_job_containers equivalence tests (AST-1840 board)

<!-- linear-archive: AST-1844 archived 2026-10-07 -->

## Linear archive (AST-1844)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1844/gap-cull-html-linear-time-repro-attribute-snip-find-job-containers  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1838 — [✅/Abrams] parse_job_list INTERRUPTED: 1 error(s) / 0 processed | parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae  
**Blocked by / blocks / related:** parent: AST-1838

### Description

## What this implements

Test gap from \[board-betty\] TESTS: REVISE on AST-1840. Nothing in the suite covers the 2h event-loop freeze or the new attribute snip. Add a `_cull_html` linear-time bug-repro on a synthetic many-row/icon listing that goes red on the quadratic `_in_preserved_svg` and green once AST-1840 lands. Add attribute-snip coverage: 500 chars kept, 501 snipped to `(snipped)`, and a `ValueError` when either new `html_cull` key is missing. Add `find_job_containers` rewrite equivalence, including script/style/template/rt/rp and a large DOM. Add a roster `to_thread` non-blocking assertion. Cover every new branch on the LOCKED_AT_100 files (`telescope.py`, `formatting.py`, `roster.py`).

## Scope

### Component scope

* `tests/component/external/test_telescope.py` (or wherever the `_cull_html` / `TestCullHtmlDefault` / AST-1745 tests live) (modified): linear-time bug-repro, attribute-snip boundary cases, missing-key `ValueError`, and `extract_page_dom` offload.
* `tests/component/utils/test_formatting.py` (modified): `find_job_containers` equivalence on existing fixtures, script/style/template/rt/rp, and a large synthetic DOM, plus the new cache/fallback branches.
* `tests/component/core/test_roster.py` (modified): non-blocking assertion for the three `_culled_dom_for_parse` `to_thread` call sites. Existing monkeypatched tests stay green.
* `docs/test-bible/external/telescope.md`, `docs/test-bible/utils/formatting.md`, `docs/test-bible/core/roster.md` (modified): bible entries for the new coverage.

### Technical scope

* Telescope tests: new cases. The repro must fail against the pre-fix product (quadratic `_in_preserved_svg` / synchronous cull) and pass after AST-1840.
* Formatting tests: new equivalence and branch-coverage cases for the rewritten `find_job_containers`.
* Roster tests: a new non-blocking case, with existing cases unchanged.
* Test bible: modified entries naming the coverage.

## Boundaries

Test and bible only; product code stays on AST-1840. Betty lands the tests (engineers are banned from the test tree). Existing tests (TestCullHtmlDefault, AST-1745, AST-827, TestFindJobContainers) should survive unchanged. No DOM-size guard (Susan, 2026-09-28).

## Notes for planning

Board verdict: \[board-betty\] TESTS: REVISE on AST-1840 (see that comment). Plan doc: docs/features/roster/ast-827-title-handoff-dom-cull.md (AST-1840's plan-fix patch).

## Git branch (authoritative)

Parent `ftr/AST-1838-parse-job-list-event-loop-block`, child `sub/AST-1838/AST-1844-parse-job-list-event-loop-block-tests`.

### Comments

#### chuckles — 2026-09-28T16:58:42.168Z
[merge-child] blocked: validate-sub-log — missing `code(AST-1844):` on origin/sub/AST-1838/AST-1844-parse-job-list-event-loop-block-tests. Recalling Hedy for the make-fix marker commit (test gap, no product src).

#### radia — 2026-09-28T16:58:21.229Z
[code-rubric] PROCEED (Commit: 59b7b03d) Repros pin AST-1840; diff clean

#### betty — 2026-09-28T16:51:43.699Z
[bug-repro]
`origin/sub/AST-1838/AST-1844-parse-job-list-event-loop-block-tests` @ `c1838b28` · 8 repros red→green
Red @ pre-fix 31846c28: 8 failed, right reason — Tag.__hash__ called · no snip · KeyError (keys absent) · cull on loop thread ×4; 24 equivalence/regression passed.
Green @ current ftr (02add16f, fb472a98) merged with tests: 32/32 passed. Sub tip does not carry ftr yet — test-fix: sync-child --ftr AST-1838-parse-job-list-event-loop-block (plan doc conflict: keep both, AST-1840 first).
Nodes + manifest in bible: external/telescope.md, core/roster.md, utils/formatting.md § AST-1840 · AST-1844.

#### joan — 2026-09-28T16:47:38.537Z
[board-joan]  CANON: OK

#### betty — 2026-09-28T16:46:50.311Z
[board-betty] TESTS: REVISE
What: docs/test-bible/{external/telescope,core/roster,utils/formatting}.md — missing [bug-repro] + equivalence coverage — land per Proposed change (TestAst1840CullHtmlLinearAndSnip, TestAst1840CullOffEventLoop, TestAst1840FindJobContainersEquivalence + 3 bible blocks); plan fully answers the AST-1840 REVISE; qa-fix must merge origin/ftr/AST-1838 first (fb472a98 not yet on this sub).

#### hedy — 2026-09-28T16:45:01.228Z
`origin/sub/AST-1838/AST-1844-parse-job-list-event-loop-block-tests` @ `db9755de` · repro + equivalence test nodes

---

_Implementation detail may live in git history on `origin/dev`._
