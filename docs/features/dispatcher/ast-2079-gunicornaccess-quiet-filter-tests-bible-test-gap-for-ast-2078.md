# AST-2079 — gunicorn.access quiet-filter tests + bible (test gap for AST-2078)

<!-- linear-archive: AST-2079 archived 2026-10-16 -->

## Linear archive (AST-2079)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2079/gunicornaccess-quiet-filter-tests-bible-test-gap-for-ast-2078  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 1  
**Parent:** AST-2074 — Gunicorn polling logs are still live on production  
**Blocked by / blocks / related:** parent: AST-2074

### Description

## What this implements

Test gap for [AST-2078](https://linear.app/astralcareermatch/issue/AST-2078) (fix-board `[board-betty] TESTS: REVISE`): component coverage proving the new `gunicorn.access` quiet filter drops polling records and leaves product logging untouched. Bible entry for the filter in `docs/test-bible/utils/debug_logging.md` (currently lists gunicorn as out of scope).

## Betty's verdict (verbatim)

\[board-betty\] TESTS: REVISE
What: no bible entry (docs/test-bible/utils/debug_logging.md lists gunicorn as out of scope; no test exercises gunicorn.access) — missing coverage — need a component test in tests/component/utils/test_debug_logging.py that builds a gunicorn.access LogRecord with a SafeAtoms-style Mapping arg, checks the filter drops it, and checks get_logger INFO/root are unaffected.

Option (b): the U="/api/deploy_status" record is dropped and U="/api/other" is kept. Option (a): every gunicorn.access record is dropped while access_log_enabled is False. No existing test breaks under either option.

## Citations

`stat.logging.info`, `astral.standards.no-hardcoded-sets`

## Scope

### Component scope

* `tests/component/utils/test_debug_logging.py` — modified: new test class for the `gunicorn.access` quiet filter (red pre-fix, green on the AST-2078 tip).
* `docs/test-bible/utils/debug_logging.md` — modified: bible entry for the filter, replacing the "gunicorn out of scope" note for this path.

### Technical scope

* `tests/component/utils/test_debug_logging.py`: new test class — fake `gunicorn.access` LogRecords (SafeAtoms-style Mapping args) asserting the drop/keep behavior for the option Susan chooses, plus a root/`get_logger` INFO non-regression check.
* `docs/test-bible/utils/debug_logging.md`: modified section — manifest node for the new class.

## Boundaries

No product `src/` change — the product fix is AST-2078. Test-tree work is Betty's (qa-fix); engineer side is a no-product-src marker plus test-fix verification.

## Git branch (authoritative)

Mini-parent `ftr/AST-2074-gunicorn-polling-logs`, child `sub/AST-2074/AST-2079-gunicorn-polling-logs-tests`. Created at bug-fix.

### Comments

#### radia — 2026-10-09T01:54:18.474Z
[code-rubric] PROCEED (Commit: 26e540ddf) Bug-repro + bible match plan

#### betty — 2026-10-09T01:50:39.324Z
[bug-repro]
`origin/sub/AST-2074/AST-2079-gunicorn-polling-logs-tests` @ `0a4dd6c23` · repro red pre-fix, green on tip

#### joan — 2026-10-09T01:36:05.876Z
[board-joan]  CANON: OK

#### betty — 2026-10-09T01:35:53.925Z
[board-betty] TESTS: REVISE
What: docs/test-bible/utils/debug_logging.md (no AST-2078 entry) — missing coverage — qa-fix lands TestAst2078GunicornAccessQuietFilter (rows 1–6) in tests/component/utils/test_debug_logging.py plus the bible section and manifest item 12.

This ticket is the test delivery itself, so the answer is necessarily yes. I checked the plan against origin/ftr/AST-2074-gunicorn-polling-logs @ 0b35bcd2c: _QuietAccessFilter, the _quiet_access_filter_attached attach-once flag, the isinstance(args, Mapping) guard, and RAILWAY_CONFIG["access_log_quiet_paths"] all match. The pre-fix tree 39bbf7afd is an ancestor of ftr and has no filter, so rows 1, 3 and 5 can go red. No existing test or bible node references AST-2078, and nothing existing breaks. I'll tag [bug-repro] in qa-fix after proving it red against 39bbf7afd.

#### ada — 2026-10-09T01:35:15.944Z
`origin/sub/AST-2074/AST-2079-gunicorn-polling-logs-tests` @ `5081be59b` · six-test class + bible

---

_Implementation detail may live in git history on `origin/dev`._
