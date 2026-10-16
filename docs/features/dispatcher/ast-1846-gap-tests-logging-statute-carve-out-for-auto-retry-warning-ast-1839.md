# AST-1846 — gap: tests + logging statute carve-out for AUTO retry WARNING (AST-1839)

<!-- linear-archive: AST-1846 archived 2026-10-07 -->

## Linear archive (AST-1846)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1846/gap-tests-logging-statute-carve-out-for-auto-retry-warning-ast-1839  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1828 — [✅/Somerset] prefilter_company COMPLETED: 100 error(s) / 500 processed | prefilter_company-ecc678b7-c2c5-4a3b-8c4b-52f704928ccf  
**Blocked by / blocks / related:** parent: AST-1828

### Description

## What this implements

Test and canon gap from fix-board on AST-1839 (both REVISE). Betty: update the tests that hard-assert the old prefilter first strike (`HOMEPAGE_READY` → `WEBSITE_FOUND_RETRY`), and cover the repro: `HOMEPAGE_READY` → `HOMEPAGE_READY_RETRY` → `ERROR_PREFILTER`; envelope failure goes to `WEBSITE_FOUND_RETRY` once (history-gated); `retried` excluded from `total_errors`; WARNING vs ERROR chosen by `retry_base(dest)`; the `do_task` `agent_failure` flag; `parse_job_list_batch` retry/terminal counting; candidate `error_state` → `total_errors: 1`; `log_llm_batch_summary` at WARNING. Joan: amend `stat.logging.warning` / `stat.logging.error` so a caught exception routed to a retry holding logs WARNING (traceback on debug) and only a terminal `error_state` logs ERROR, including Resolution §3's `log_llm_batch_summary` line. She authors the literal patch in validate-plan fix mode and Chuckles applies it verbatim.

## Scope

### Component scope

* `tests/component/core/test_roster.py` (modified): `_prefilter_batch_fail_dest`, `TestAst882PrefilterOneRetryThenError`, and the other `HOMEPAGE_READY` first-strike / `COMPANY_STATES` transition asserts flip to the new routing; new repro nodes for prefilter retry/terminal/envelope routing, the retried count, and `parse_job_list_batch` counting.
* Existing component test files for `src/core/consult.py`, `src/core/agent.py`, `src/core/candidate.py`, `src/utils/config.py`, `src/utils/logging.py` (modified): coverage for the summary-count exclusion, the `agent_failure` flag, candidate `error_state` counting, `HOMEPAGE_READY` `retry_state` / transitions, and `log_llm_batch_summary` level. Betty picks the exact files.
* `docs/test-bible/core/roster.md`, `docs/test-bible/core/consult.md`, `docs/test-bible/core/agent.md`, `docs/test-bible/core/candidate.md`, `docs/test-bible/utils/config.md`, and the logging bible entry (`docs/test-bible/utils/logging_batch.md` or `debug_logging.md`) (modified): bible entries for the above.
* `canon/directives/active/stat.logging.warning.md` and `canon/directives/active/stat.logging.error.md` (modified): destination-based severity carve-out for retry-routed batch failures, and `log_llm_batch_summary` provider errors at WARNING.

### Technical scope

* Tests: modified and new test functions only. No product `src/` change on this ticket; the product fix is sibling AST-1839.
* Bible: modified entries.
* Canon: modified statement / resolution text in the two statutes. No new directive ids.

## Boundaries

No product `src/` edits (sibling AST-1839 owns them). Tests and bible are Betty's. The canon text is Joan's literal patch, which Chuckles applies. Don't touch other `stat.logging.*` directives.

## Notes for planning

Source verdicts: `[board-betty]` and `[board-joan]` on AST-1839, recorded in `docs/features/roster/ast-882-prefilter-one-retry-error.md` § Fix board — AST-1839. Same feature doc for this gap's plan section. Parent bug AST-1828 is authoritative. Sequencing follows AST-1820/AST-1822: the gap's qa-fix runs after AST-1839's product fix is merged on the ftr, and proves repro red against the ftr base (pre-fix) and green on the ftr tip.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1828-auto-retry-warn-then-error`, child `sub/AST-1828/AST-1846-auto-retry-warn-then-error-gap`. Created at bug-fix.

### Comments

#### radia — 2026-09-28T19:59:16.952Z
[code-rubric] PROCEED (Commit: 2b515163) Tests, bible, and the canon carve-out. Clean: [bug-repro] is substantive (red at base on assertions, green at tip), the statutes match the shipped _log_fail_dest / log_llm_batch_summary, and What must still hold holds.

#### ada — 2026-09-28T19:57:00.415Z
`origin/sub/AST-1828/AST-1846-auto-retry-warn-then-error-gap` @ `2b515163` · empty code, no product change

#### betty — 2026-09-28T19:56:09.323Z
[bug-repro]
`origin/sub/AST-1828/AST-1846-auto-retry-warn-then-error-gap` @ `b6207dc6` (`merge-tests(AST-1846): origin/tests 4c8d9999`)

**Sequencing deviation (gap child):** the AST-1839 product was already on the ftr, so the repro was proven both ways using throwaway `git archive` exports of `src/` (not committed):
- **13 repro nodes + branch-lock nodes** (5 classes, 29 runs): **RED at ftr base `31846c28`**, 28 failed, **every one an `AssertionError`** (wrong state / count / level / missing `retried` / missing `agent_failure`), no import or fixture errors. The one base pass is `TestAst1846DoTaskAgentFailureFlag::test_non_rubric_task_does_not_set_agent_failure`, which is a guard that passes at both shas by design. **GREEN at ftr tip `2eac54b5`**: 29/29.
- **19 flipped nodes** (plan §1; `TestAst1155…` renamed to `test_prefilter_company_incomplete_routes_to_homepage_ready_retry`): green at tip (21 runs incl. params). These are exactly the 19 nodes that failed at tip before the flip. At base the flipped versions fail, as expected.
- Manifest (50 runs) re-run on the merged sub tree at `b6207dc6`: **50 passed**.

**Manifest:** `docs/test-bible/core/roster.md` § AST-1846 → `## QA test manifest` (item 1 = flips, item 2 = new classes). Sibling bible blocks are in `core/consult.md`, `core/agent.md`, `core/candidate.md`, `utils/config.md` and `utils/logging_batch.md`. Fixture re-pin: `tests/component/utils/fixtures/ast1806_prior_snapshot.json` (`WEBSITE_FOUND_RETRY` priors drop `HOMEPAGE_READY`).

**Branch lock (board addendum):** I ran the full component suite with `--cov-branch` at `2eac54b5`. **Every line and branch that `36f385a2` added is covered** in roster.py, consult.py, agent.py, candidate.py and config.py (and logging.py): 0 missing lines, 0 missing arcs. The new branch-lock nodes cover the `result["error"]` path, the generic parse exception, the upshot terminal and no-dest ERROR sites, the `failure_note` fallbacks, the store-exception swallow, hop-label hold, unregistered trigger and retry→error_state. **Whole-file coverage on this host does not reach 100%:** roster 78.3, consult 80.4, agent 86.3, candidate 82.4, config 92.6. That gap comes only from pre-existing environment drift: the Python 3.14 host venv gives 322 failures and 21 errors, and 5 modules won't collect, identically at base and tip. None of the uncovered lines are AST-1839 lines.

**For test-fix:** no product change is expected. The fix is already on the ftr, and the flip was verified above. Please re-run manifest items 1–2 on the epic worktree.

**Out of scope, pre-existing, not touched** (red at both shas): `TestAst891ParseJobListBatch::test_scrape_timeout_labeled_infra_and_counts_passed` (stale timeout premise); `test_dispatch_tasks.py::TestAst882HomepageReadyClaimsWfr::test_count_eligible_homepage_ready_unions_wfr` (stale since AST-1810); `TestAst507EncodedPrefilter` inflow pair.

**Lint:** the repo has no linter configured and none is installed in the venv. The gate was `py_compile` on all 6 test files, a JSON parse of the fixture, and green runs.

#### joan — 2026-09-28T19:38:29.461Z
F3 AST-1846: Destination-based severity. Retry holdings log WARNING per item, with the traceback at debug; terminal and unrouted failures stay ERROR; the `log_llm_batch_summary` provider line is WARNING, and callers log ERROR only on terminal landings. Applied verbatim to stat.logging.warning and stat.logging.error.

#### joan — 2026-09-28T19:37:27.416Z
[board-joan]  CANON: REVISE
What: stat.logging.warning + stat.logging.error — AST-1839 destination carve-out (retry holding → WARNING with debug traceback; terminal/unrouted → ERROR; log_llm_batch_summary at WARNING). Literal patch in validate-plan fix mode. No other directive ids.

#### betty — 2026-09-28T19:36:37.372Z
[board-betty] TESTS: REVISE
What: docs/test-bible/README.md §6a/§7.12 (`LOCKED_AT_100`) — missing coverage — the plan's manifest is narrowed node ids only, so `check_per_file_coverage.py` never runs on the five locked files AST-1839 touched (`roster.py`, `consult.py`, `agent.py`, `candidate.py`, `config.py`), and the 13 repro nodes leave new 36f385a2 branches unexercised. Add to §2/§3: a branch-lock check on those five files at `2eac54b5`, plus a node for each uncovered AST-1839 branch it reports. Likely uncovered: `agent.py` `failure_note` fallbacks (non-dict perf / top-level note / no note) and `_should_store` store-exception; `candidate.py` hop-label hold + unregistered-trigger WARNING returns; `consult.py` process_fn-exception `_log_fail_dest`, upshot no-company / no-live-content / non-dict-parse holding-vs-terminal branches, `if error_state else 0` false branch. The rest of the test plan (19 flips verified present at tip, 13 repro nodes, red-at-base-on-assertion gate, bible pages) is right as written.

#### ada — 2026-09-28T19:35:24.989Z
`origin/sub/AST-1828/AST-1846-auto-retry-warn-then-error-gap` @ `1dbe4ede` · plan-fix: tests + carve-out

---

_Implementation detail may live in git history on `origin/dev`._
