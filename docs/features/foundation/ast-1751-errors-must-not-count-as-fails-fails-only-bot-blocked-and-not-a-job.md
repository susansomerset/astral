# AST-1751 — Errors must not count as fails; fails only BOT_BLOCKED and NOT_A_JOB

<!-- linear-archive: AST-1751 archived 2026-10-02 -->

## Linear archive (AST-1751)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1751/errors-must-not-count-as-fails-fails-only-bot-blocked-and-not-a-job  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** AST-1721 — Astral Telescope — stateless headless-scraping microservice (per-URL)  
**Blocked by / blocks / related:** parent: AST-1721

### Description

\[bug\] errors are not ALSO fails.  They are only errors.  Fails are only for BOT_BLOCKED and NOT_A_JOB.

## As-is

Scrape outcomes counted as errors are also counted as fails (batch totals show fail and error together for the same rows).

## To-be

Errors are errors only. Fails are reserved for BOT_BLOCKED and NOT_A_JOB (which comes back from the agent stage_meteorite task, not telescope, itself.)

## Suggested engineer

Ada Lovelace

Plan doc: docs/features/foundation/ast-1726-platform-telescope-py-drop-in-playwright-decommission.md (Bug: AST-1751).

## Proposed change

- [X] `run_scrape_meteorite`: ERROR / `SCRAPE_ERROR` arms → `total_errors` only (not also `total_failed`)
- [X] `run_scrape_meteorite`: `BOT_BLOCKED` → `total_failed` only (not pass, not error)
- [X] `run_stage_meteorite`: ERROR / exception double-bumps → errors only
- [X] `run_land_meteorite`: ERROR / exception double-bumps → errors only
- [X] `run_notify_meteorite_bot_blocked`: exception double-bump → errors only (pure fail BOT_BLOCKED arms unchanged)
- [X] No Telescope / `telescope.py` / config / UI / inbox AST-1742 path edits

## QA test manifest

**Publish:** `origin/sub/AST-1721/AST-1751-errors-must-not-count-as-fails` @ `d892d7e349640bf8cd5837f63116e2febdf0753d` (product `code(AST-1751)` + Betty qa-handoff merge-tests)

**Bug-repro:** green on Ada re-run after Betty fixed `candidate_id` + `_row_miss` warning assert.

Primary node: `TestAst1560RunScrapeMeteorite::test_ast1751_error_only_batch_fail_zero_error_n` (fail:0 error:5). Also BOT_BLOCKED → total_failed; stage/land ERROR holds assert total_failed==0. Bible: docs/test-bible/core/meteorite.md § AST-1751.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_meteorite.py::TestAst1560RunScrapeMeteorite::test_ast1751_error_only_batch_fail_zero_error_n \
  tests/component/core/test_meteorite.py::TestAst1560RunScrapeMeteorite::test_blocked_emits_monitoring \
  tests/component/core/test_meteorite.py::TestAst1560RunScrapeMeteorite::test_sibling_rows_do_not_abort_batch \
  tests/component/core/test_meteorite.py::TestAst1703EmailBreadcrumb::test_stage_email_text_blank_link_errors \
  tests/component/core/test_meteorite.py::TestAst1560RunStageMeteorite::test_missing_classify_outcome_errors_with_monitoring \
  tests/component/core/test_meteorite.py::TestAst1560RunLandMeteorite::test_missing_content_errors -q
```

### Comments

#### radia — 2026-09-21T02:22:39.300Z
[code-rubric] PROCEED (Commit: d892d7e349640bf8cd5837f63116e2febdf0753d) ERROR not also fail

#### ada — 2026-09-21T02:20:57.249Z
`origin/sub/AST-1721/AST-1751-errors-must-not-count-as-fails` @ `d892d7e349640bf8cd5837f63116e2febdf0753d`
[bug-repro] `test_ast1751_error_only_batch_fail_zero_error_n` red→green (pre-fix meteorite.py fails; tip green). Full QA manifest 6 passed.

#### ada — 2026-09-21T02:17:38.226Z
`origin/sub/AST-1721/AST-1751-errors-must-not-count-as-fails` @ `d892d7e349640bf8cd5837f63116e2febdf0753d`

#### betty — 2026-09-21T02:15:58.346Z
[bug-repro]
`origin/sub/AST-1721/AST-1751-errors-must-not-count-as-fails` @ `d892d7e3` · qa-handoff fixed; re-run green

#### ada — 2026-09-21T02:09:04.829Z
[qa-handoff]
Product counter fix published at `origin/sub/AST-1721/AST-1751-errors-must-not-count-as-fails` @ `afe0101121e4a82dc657eb4377e4af06f9e72c2e` — ERROR→errors-only; scrape BOT_BLOCKED→fail-only in `run_scrape_meteorite` / stage / land / notify exception arms.

Cannot flip [bug-repro] green without test edits (Ada must not touch `tests/`):

1. **Primary** `TestAst1560RunScrapeMeteorite::test_ast1751_error_only_batch_fail_zero_error_n` — `_ingress_task(...)` omits required `candidate_id=` (TypeError before counters run). Sibling scrape tests already pass `candidate_id=cid`.
2. **`test_blocked_emits_monitoring`** — counter asserts pass (`total_failed==1`, pass/error 0, state BOT_BLOCKED). Final assert looks for `log.info` containing `"meteorite scrape blocked"`; product uses `_row_miss` → `logger.warning` with `"meteorite {id} for {cid} — scrape blocked at {link}"` (unchanged by this fix; plan keeps `_row_miss`).

Please patch those two nodes on astral-tests / publish merge-tests; leave status Tests Ready for Ada re-run.

#### betty — 2026-09-21T02:04:59.473Z
[bug-repro]
`origin/sub/AST-1721/AST-1751-errors-must-not-count-as-fails` @ `b93fe66c` · repro lands red, awaits fix

#### joan — 2026-09-21T01:59:14.081Z
[plan-rubric] PROCEED (Commit: b1c0ac95) board CANON OK — counter taxonomy is product not canon.

#### joan — 2026-09-21T01:59:13.243Z
[board-joan]  CANON: OK

#### betty — 2026-09-21T01:58:50.209Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/meteorite.md / test_meteorite.py — rewrite TestAst1560RunScrapeMeteorite BOT_BLOCKED total_passed→total_failed; missing ERROR-only fail:0 error:N (sibling assert omits total_failed); stage/land double-bump holds may break

#### ada — 2026-09-21T01:57:40.123Z
`origin/sub/AST-1721/AST-1751-errors-must-not-count-as-fails` @ `b1c0ac95eb3b823acdee546da6a5f873d12a92b2` · ERROR not also fail

#### ada — 2026-09-21T01:52:55.154Z
[scope-gate] Cannot Plan Ready — parent epic scope does not cover the counter change this bug needs.

**Needed:** `src/core/meteorite.py` — change batch-summary counter classification in `run_scrape_meteorite` (and any sibling dispatch runners that still double-bump the same ERROR row): ERROR / `SCRAPE_ERROR` paths must increment `total_errors` only (not also `total_failed`); `total_failed` reserved for `BOT_BLOCKED` and `NOT_A_JOB` from meteorite staging/classify (`stage_meteorite`), not from Telescope HTTP. Observed UAT line: `scrape_meteorite pass:0 fail:5 error:5` for five `scrape_closed` ERROR rows.

**Scope lines that don't cover it** (parent AST-1721 Component / Technical):
- Component: `src/core/meteorite.py` — **modified** — same import-path-only rewire.
- Technical: `meteorite.py` — Change import module to `telescope` only; leave call shapes untouched; … not new core logic.

Counter taxonomy is a different *kind* of change than import-path-only / leave-call-shapes-untouched. AST-1742 already fixed NOT_A_JOB→fail on inbox/ingest and explicitly deferred scrape runners; this ticket is that deferred scrape half.

**Doc to patch once scope is amended:** prefer `docs/features/foundation/ast-1726-platform-telescope-py-drop-in-playwright-decommission.md` (epic owner of `meteorite.py`) — Ada's assignee-matched sibling doc is AST-1725 (service-only); confirm which foundation slug Chuckles wants before re-spawn.

Chuckles can amend parent (or this bug) Scope to allow meteorite dispatch counter classification for ERROR vs fail — same pattern as AST-1742's cleared `[scope-gate]`. Not asking Archie unless the amendment is refused.

---

_Implementation detail may live in git history on `origin/dev`._
