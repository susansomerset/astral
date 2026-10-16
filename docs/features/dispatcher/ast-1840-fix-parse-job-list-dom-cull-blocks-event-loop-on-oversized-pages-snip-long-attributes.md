# AST-1840 — fix: parse_job_list DOM cull blocks event loop on oversized pages; snip long attributes

<!-- linear-archive: AST-1840 archived 2026-10-07 -->

## Linear archive (AST-1840)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1840/fix-parse-job-list-dom-cull-blocks-event-loop-on-oversized-pages-snip  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-1838 — [✅/Abrams] parse_job_list INTERRUPTED: 1 error(s) / 0 processed | parse_job_list-8b8049ff-bae3-459e-9556-6cd1ffdf1aae  
**Blocked by / blocks / related:** parent: AST-1838; blocks: AST-1838

### Description

## What this implements

A single oversized careers page can't freeze the dispatcher anymore. `find_job_containers` becomes roughly linear: each element's text and title set are computed once, not with `get_text()` per descendant. The three async callers of `_culled_dom_for_parse` in `src/core/roster.py` run it off the event loop with `asyncio.to_thread`. `_cull_html` in `src/external/telescope.py` replaces any attribute value longer than `html_cull.max_html_tag_length` (500) with `html_cull.max_length_placeholder` (`"(snipped)"`), so binary/base64 attribute payloads stop inflating the DOM. Dispatch timeouts and provider budgets then fire on schedule, and sibling companies in the batch still get processed.

## Scope

## Component scope

* `src/utils/formatting.py` (modified): `find_job_containers` is where the quadratic BeautifulSoup walk lives. It needs a single-pass text/title cache.
* `src/core/roster.py` (modified): `_scrape_and_parse` inside `run_parse_job_list_dispatch`, `_finalize_joblist_titles_after_chain`, and `_finalize_joblist_titles_select_only` call `_culled_dom_for_parse` synchronously from async code. They need to offload it to a worker thread. The sync `make_locate_parse_resolver` callback stays sync.
* `src/external/telescope.py` (modified): `_cull_html` snips over-long attribute values to the placeholder; `_in_preserved_svg` becomes identity-based (never hashes a Tag); `extract_page_dom` offloads `_cull_html` to a worker thread. **Susan (2026-09-28): amended as written** — admin workbench `_cull_html` calls (\~629/631) left out.
* `src/utils/config.py` (modified): `ASTRAL_CONFIG["html_cull"]` gains `max_html_tag_length: 500` and `max_length_placeholder: "(snipped)"`.
* `tests/component/utils/test_formatting.py` (modified): add a large-DOM equivalence/performance case next to the existing `find_job_containers` tests.
* `tests/component/core/test_roster.py` (modified): existing tests monkeypatch `find_job_containers` and call `_culled_dom_for_parse` directly. They need to keep passing once the calls become `to_thread`, and they need one new non-blocking assertion.

## Technical scope

* `src/utils/formatting.py`: modified function `find_job_containers`. Replace per-element `get_text()` calls with one post-order pass that caches each Tag's matched-title set, so Phase 1 and Phase 2 run in roughly linear time over the DOM without changing which containers are returned.
* `src/core/roster.py`: modified functions `run_parse_job_list_dispatch` (inner `_scrape_and_parse`), `_finalize_joblist_titles_after_chain`, and `_finalize_joblist_titles_select_only`. Wrap the `_culled_dom_for_parse` call in `asyncio.to_thread` so CPU-bound culling never runs on the dispatcher's event loop. `_culled_dom_for_parse` itself stays a pure sync function.
* `src/external/telescope.py`: modified function `_cull_html`. After existing attribute stripping, replace any remaining attribute value whose length exceeds `html_cull.max_html_tag_length` with `html_cull.max_length_placeholder`; both keys required config (no in-code defaults).
* `src/external/telescope.py` — `_cull_html`: make `_in_preserved_svg` identity-based (return early on an empty set, otherwise compare by `id()`) so it never hashes a Tag. Same output, linear cost.
* `src/external/telescope.py` — `extract_page_dom`: modified to `await asyncio.to_thread(_cull_html, raw_html)` so the html cull never runs on the event loop.
* `src/utils/config.py`: two new keys in `ASTRAL_CONFIG["html_cull"]`.
* Tests: new test cases only, with no new fixtures or tables.

## Boundaries

Product code only. Admin workbench `_cull_html` calls ([telescope.py](<http://telescope.py>) \~629/631) are out of scope (Susan, 2026-09-28). Tests and the test bible belong to Betty (a gap sibling gets filed if fix-board asks for one). **No DOM-size guard** (Susan, 2026-09-28). Don't add any page/DOM size cap or truncation. The `telescope-result-poller` "Task was destroyed but it is pending" error is investigate-only: note in the plan whether steps 1–3 should remove it, and don't fix it here.

## Notes for planning

Parent bug AST-1838's Description (As-is / To-be / Proposed steps 1–6, Susan's answers 2026-09-28) is authoritative. Susan approved the reading by reassigning. No ancestor box was checked, so there's no related-issue link. Feature doc to patch (Chuckles' best read, the top-ranked candidate): `docs/features/roster/ast-827-title-handoff-dom-cull.md`. `find_job_containers` must return the same containers as today on existing fixtures. Only cost changes, not semantics.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1838-parse-job-list-event-loop-block`, child `sub/AST-1838/AST-1840-parse-job-list-event-loop-block`. Created at bug-fix.

### Comments

#### radia — 2026-09-28T16:45:31.356Z
[code-rubric] PROCEED (Commit: fb472a98) Canon clean; holds OK

#### hedy — 2026-09-28T16:41:02.162Z
`origin/sub/AST-1838/AST-1840-parse-job-list-event-loop-block` @ `fb472a98` · lighter check green (no qa-fix manifest; TESTS: REVISE → gap AST-1844)

- `py_compile` passes on all 4 changed files.
- `pytest tests/component/external/test_telescope.py tests/component/utils/test_formatting.py tests/component/core/test_roster.py`: 54 failed, 331 passed, 17 skipped. The pre-fix tip `f7f8791d` (same `src/` as `origin/dev` `31846c28`) gives the **same 54 failures, by node id**. None are new and none are fixed.
- **The pre-existing failures are 54, not the 4 known ones.** The other 50 are stale tests that reference symbols no longer in the product: `roster.get_page` (11), `telescope._TelescopePool`, `roster.find_job_page`, `roster._is_verified_job_site_distinct`, `telescope.wait_for_careers_list_readiness`, and similar. Three of them sit near the parse path and fail identically before the fix: `TestFinalize469BranchCoverage::test_after_chain_empty_containers_debug_true_logs`, `TestAst891ParseJobListBatch::test_debug_emits_per_company_index`, and `::test_scrape_timeout_labeled_infra_and_counts_passed`. These are candidates for AST-1844 or a separate test-debt ticket.
- Touched-area classes (AST-827 cull, AST-1745 svg, `TestFindJobContainers`, parse dispatch, AST-469 resolver): **30/30 pass**.

#### joan — 2026-09-28T16:36:32.162Z
[board-joan]  CANON: OK

#### betty — 2026-09-28T16:35:46.415Z
[board-betty] TESTS: REVISE
What: no bible entry (external/telescope.md, utils/formatting.md, core/roster.md) — missing coverage — nothing exercises the repro: need a `_cull_html` linear-time bug-repro on the synthetic many-row/icon listing (red on quadratic `_in_preserved_svg`), attr snip 500-kept/501-snipped + missing-key ValueError, `find_job_containers` rewrite equivalence incl. script/style/template/rt/rp + large DOM, and roster `to_thread` non-blocking assertion; existing tests (TestCullHtmlDefault, AST-1745, AST-827, TestFindJobContainers) survive unchanged, but new branches on LOCKED_AT_100 files (telescope/formatting/roster) need coverage.

#### hedy — 2026-09-28T16:34:26.725Z
`origin/sub/AST-1838/AST-1840-parse-job-list-event-loop-block` @ `883cd4b3` · linear culls, off-loop, snip

#### hedy — 2026-09-28T14:54:05.596Z
[scope-gate] @susan — the fix needs work outside AST-1840's declared scope, and the root cause is mostly somewhere else.

**What I measured** (synthetic listing pages, on the real `_cull_html` + `html_cull` config, bs4 4.15):

- `_cull_html` (`src/external/telescope.py`) is **quadratic**: 100 rows took 1.5s, 200 took 5.7s, 400 took 23.5s, and 1000 rows (450KB) took **144s**. A 7MB page didn't finish in 15 min. Profile: almost all the time is `Tag.decode`, which serializes whole subtrees.
- Cause: `_in_preserved_svg` (AST-1745, `a830d0f0`) runs `elem in preserve_root_svgs` and `p in preserve_root_svgs for p in elem.parents`. bs4's `Tag.__hash__` is `hash(str(self))`, so every membership check serializes that ancestor's whole subtree, the document root included, even when the set is empty. It runs once per `<svg>` and once per non-allowed tag in each of the up-to-10 unwrap passes.
- This runs **on the event loop**, on the parse path: `_scrape_list_page_dom_for_parse` → `extract_page_dom` (async) → `_cull_html(raw_html)` synchronously. Volvo's 7.4MB came back raw, SVG and all. That call happens *before* `_culled_dom_for_parse`, and the first Volvo `Response from _culled_dom_for_parse` is logged at 12:33:26, right when the freeze ends.
- `find_job_containers` is only about 1.4s per MB (1.1MB takes 1.4s, depth 5 or 30 alike), so roughly 10s for Volvo. The linear rewrite and the three `to_thread` wraps are still worth doing, but they aren't the 2h freeze.
- The attribute snip runs at the end of `_cull_html`, after the SVG and unwrap loops, so it doesn't reduce `_cull_html`'s own cost. It only shrinks what reaches `find_job_containers` and the LLM.

**What's not covered by `## Scope`:**
1. `src/external/telescope.py` `_cull_html`: scope covers only "snips over-long attribute values". Also needed: make `_in_preserved_svg` identity-based (return `False` immediately when `preserve_root_svgs` is empty; otherwise compare with `id()` against a set of ids), so it never hashes a `Tag`. Same results, linear cost.
2. `src/external/telescope.py` `extract_page_dom`: not named in scope. Needed: `return await asyncio.to_thread(_cull_html, raw_html)`, so the html cull never runs on the event loop.

Without these two, a Volvo-sized page still freezes the loop and the to-be is not met.

**Optional, your call:** the admin workbench path (`telescope.py` ~629/631) also calls `_cull_html` synchronously inside async code. It's not on the dispatcher path, so I'd leave it out unless you want it.

**Poller "Task was destroyed but it is pending" (investigate-only):** this should survive steps 1–3. It fired at 10:25:55, before the freeze, and was paired with an orphaned `to_thread` task. `dispatcher._task_thread_target` does `loop.close()` without cancelling pending tasks. The per-loop `telescope-result-poller` and any AST-1189 budget-timeout orphan are then garbage-collected while still pending. That's a separate bug.

After amending, assign this bug to Chuckles.

---

_Implementation detail may live in git history on `origin/dev`._
