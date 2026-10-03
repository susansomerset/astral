# AST-1750 — Telescope/meteorite scrape errors lack detail; error/debug logging fails statutes

<!-- linear-archive: AST-1750 archived 2026-10-02 -->

## Linear archive (AST-1750)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1750/telescopemeteorite-scrape-errors-lack-detail-errordebug-logging-fails  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** AST-1721 — Astral Telescope — stateless headless-scraping microservice (per-URL)  
**Blocked by / blocks / related:** parent: AST-1721

### Description

\[bug\] When scraping 5 urls, I get re-produceable errors back, but no detail.  Logging statutes for telescope fails for error and debug logging.

```
[2026-09-21 01:34:46] INFO src.external.telescope: telescope ok path=/telescope final_url=https://www.dice.com/job-detail/c5a9ffeb-c9c9-44a2-b0e4-59668a8d18b3
[2026-09-21 01:34:46] WARNING src.core.meteorite: meteorite 92 for somerset — scrape_closed
  This row is ERROR
[2026-09-21 01:34:46] INFO src.external.telescope: telescope ok path=/telescope final_url=https://www.dice.com/job-detail/b3573283-846b-4863-a592-ab8e6ec18e27
[2026-09-21 01:34:46] WARNING src.core.meteorite: meteorite 96 for somerset — scrape_closed
  This row is ERROR
[2026-09-21 01:34:46] INFO src.external.telescope: telescope ok path=/telescope final_url=https://www.dice.com/job-detail/029332ea-1e6a-44ab-9372-8c74805becd9
[2026-09-21 01:34:46] WARNING src.core.meteorite: meteorite 97 for somerset — scrape_closed
  This row is ERROR
[2026-09-21 01:34:46] INFO src.external.telescope: telescope ok path=/telescope final_url=https://www.dice.com/job-detail/9404cd49-0dc1-42dd-84c0-eee19b48fbb7
[2026-09-21 01:34:46] WARNING src.core.meteorite: meteorite 98 for somerset — scrape_closed
  This row is ERROR
[2026-09-21 01:34:46] INFO src.external.telescope: telescope ok path=/telescope final_url=https://www.dice.com/job-detail/9940908d-3e9b-4111-94ce-7a6d0102baea
[2026-09-21 01:34:46] WARNING src.core.meteorite: meteorite 99 for somerset — scrape_closed
  This row is ERROR
[2026-09-21 01:34:46] INFO src.core.dispatcher: somerset | dispatch meteorite stopping scrape_meteorite — 0 remaining after 1 run(s)
[2026-09-21 01:34:46] INFO src.core.dispatcher: somerset | dispatch meteorite task completed: scrape_meteorite pass:0 fail:5 error:5 (batch: scrape_meteorite-f3d275db-cdb9-4378-8276-f84137831192)
```

## As-is

Batch scrapes return reproducible ERROR rows (scrape_closed) with no diagnostic detail, and Telescope error/debug logging does not meet logging statutes.

## To-be

ERROR outcomes include enough detail to diagnose why the scrape closed, and Telescope error/debug logging satisfies the logging statutes, specifically, debug mode displays the full raw response from the api call, and the api call parameters sent.

## Suggested engineer

Ada Lovelace

## QA test manifest

**qa-fix bug-repro (board REVISE):** confirmed red on pre-fix tree — bare `scrape_closed` (no signal/text_len/final_url); `_post_telescope` info-only (no ungated debug request-body / full response dump).

**Publish:** `origin/sub/AST-1721/AST-1750-telescope-meteorite-scrape-errors-lack-detail-logging` @ `3cf9580f` (`merge-tests` of `origin/tests` `ca385f2c`)

**Bug-repro (must flip red→green after make-fix):**

1. `tests/component/core/test_meteorite.py::TestAst1560RunScrapeMeteorite::test_ast1750_scrape_closed_error_includes_signal_text_len_final_url` — soft-fail ERROR includes `signal=` / `text_len=` / `final_url=`
2. `tests/component/external/test_telescope.py::TestAst1750PostTelescopeDebugDump::test_post_telescope_debug_emits_request_body_and_full_response` — ungated `logger.debug` callee-in (request body) + callee-out (full JSON)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_meteorite.py::TestAst1560RunScrapeMeteorite::test_ast1750_scrape_closed_error_includes_signal_text_len_final_url \
  tests/component/external/test_telescope.py::TestAst1750PostTelescopeDebugDump -q
```

**Bible:** `docs/test-bible/core/meteorite.md` (AST-1750), `docs/test-bible/external/telescope.md` (AST-1750)

## Proposed change

- [X] `src/external/telescope.py` — `_post_telescope` / `_post_telescope_html` ungated debug callee-in (path + full request body) and callee-out (full JSON); 4xx debug-dumps `resp.text` before raise; info one-liner unchanged
- [X] `src/core/meteorite.py` — soft-fail ERROR `error`/warning why includes `scrape_<status> signal=… text_len=… final_url=…`; debug logs full `visible_text`; fail/error tallies unchanged (AST-1751 out of scope)

### Comments

#### radia — 2026-09-21T02:24:15.601Z
[code-rubric] PROCEED (Commit: b45b8c70c46b6ea4e56de44df704d422bc09e866) Scrape diagnostics + debug dump

#### betty — 2026-09-21T02:21:43.650Z
[bug-repro]
`origin/sub/AST-1721/AST-1750-telescope-meteorite-scrape-errors-lack-detail-logging` @ `b45b8c70` · scrape_closed diagnostics only

#### ada — 2026-09-21T02:19:47.811Z
[qa-handoff]
@Betty White

**Passed (AST-1750 product):**
- `TestAst1750PostTelescopeDebugDump::test_post_telescope_debug_emits_request_body_and_full_response` — green
- scrape_closed diagnostic string — green in the same run: warning/error show `signal='no longer available' text_len=120 final_url=…`

**Still red:**
`tests/component/core/test_meteorite.py::TestAst1560RunScrapeMeteorite::test_ast1750_scrape_closed_error_includes_signal_text_len_final_url`

**Command:**
```bash
python3 -m pytest \
  tests/component/core/test_meteorite.py::TestAst1560RunScrapeMeteorite::test_ast1750_scrape_closed_error_includes_signal_text_len_final_url -q --tb=short
```

**Error:** `assert out["total_failed"] == 0` (got 1) at the AST-1751 comment block in the AST-1750 node.

**Why test/manifest, not product:** plan-fix AST-1750 `## What must still hold` / blast radius: do **not** change `total_failed`/`total_errors` — that is sibling **AST-1751**. Product tip `6c9f86be0a491c9a77637a39c8d2ac37dbdd82de` correctly still bumps both on soft-fail ERROR. The `total_failed == 0` lines were added in `test(AST-1751): bug-repro` (5b2cdee7) onto this shared node; original AST-1750 repro (ca385f2c) only asserted diagnostics + `total_errors == 1`.

**Please fix:** remove the AST-1751 `total_failed == 0` assert (and its comment) from the AST-1750 node — leave diagnostic asserts. AST-1751 owns fail:0 via `test_ast1751_error_only_batch_fail_zero_error_n`.

`origin/sub/AST-1721/AST-1750-telescope-meteorite-scrape-errors-lack-detail-logging` @ `6c9f86be0a491c9a77637a39c8d2ac37dbdd82de`

#### betty — 2026-09-21T02:17:19.090Z
[bug-repro]
`origin/sub/AST-1721/AST-1750-telescope-meteorite-scrape-errors-lack-detail-logging` @ `de846e69` · candidate_id on scrape_closed

#### ada — 2026-09-21T02:10:19.539Z
[qa-handoff]
@Betty White

**Failed:** `tests/component/core/test_meteorite.py::TestAst1560RunScrapeMeteorite::test_ast1750_scrape_closed_error_includes_signal_text_len_final_url`

**Command:**
```bash
python3 -m pytest tests/component/core/test_meteorite.py::TestAst1560RunScrapeMeteorite::test_ast1750_scrape_closed_error_includes_signal_text_len_final_url -q --tb=short
```

**Error:** `TypeError: _ingress_task() missing 1 required keyword-only argument: 'candidate_id'`

**Why test/manifest, not product:** After `sync-child` merged `origin/dev` (entity-state-bound), `_ingress_task` requires `candidate_id=` (sibling scrape tests already pass it). The AST-1750 [bug-repro] call still omits it, so the suite never reaches the diagnostic assertions. Product at `5008ac20` already emits `signal=` / `text_len=` / `final_url=` on soft-fail ERROR — verified green when the call includes `candidate_id=cid`. Telescope [bug-repro] `TestAst1750PostTelescopeDebugDump` is already green.

**Please fix:** add `candidate_id=cid` to the `_ingress_task(...)` in that node (assert body unchanged). Stay on `origin/sub/AST-1721/AST-1750-telescope-meteorite-scrape-errors-lack-detail-logging`.

#### ada — 2026-09-21T02:05:38.770Z
`origin/sub/AST-1721/AST-1750-telescope-meteorite-scrape-errors-lack-detail-logging` @ `5008ac20c0d878bfddf63b115898e98ee9aa461c` · repro needs candidate_id=cid

#### betty — 2026-09-21T01:59:53.029Z
[bug-repro]
`origin/sub/AST-1721/AST-1750-telescope-meteorite-scrape-errors-lack-detail-logging` @ `3cf9580f` · repro lands red, awaits fix

#### joan — 2026-09-21T01:55:09.345Z
[plan-rubric] PROCEED (Commit: cd5ae0ab) board CANON OK — logging compliance is code not canon.

#### joan — 2026-09-21T01:55:08.337Z
[board-joan]  CANON: OK

#### betty — 2026-09-21T01:54:39.168Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/meteorite.md (+ external/telescope.md) — missing scrape_closed ERROR with signal=/text_len=/final_url; missing _post_telescope debug request-body + full response dump; no existing soft-fail diagnostic coverage

#### ada — 2026-09-21T01:53:31.458Z
`origin/sub/AST-1721/AST-1750-telescope-meteorite-scrape-errors-lack-detail-logging` @ `cd5ae0ab04a557774d651bb472cb4aa2b1a4bd92` · scrape ERROR + debug dump

---

_Implementation detail may live in git history on `origin/dev`._
