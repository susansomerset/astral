# AST-2078 — fix: silence gunicorn access-log polling noise on prod (AST-2074)

<!-- linear-archive: AST-2078 archived 2026-10-16 -->

## Linear archive (AST-2078)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2078/fix-silence-gunicorn-access-log-polling-noise-on-prod-ast-2074  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-2074 — Gunicorn polling logs are still live on production  
**Blocked by / blocks / related:** parent: AST-2074; blocks: AST-2079

### Description

## What this implements

Fix for [AST-2074](https://linear.app/astralcareermatch/issue/AST-2074): stop the 30s `GET /api/deploy_status` admin-footer poll from writing INFO `gunicorn.access` lines to the production Railway log, without losing real application logs or gunicorn error-log lines.

## As-is

Every open admin tab polls `GET /api/deploy_status` every 30s (`AdminDeployFooter.tsx`), and each poll writes an INFO `gunicorn.access` line to the production Railway log. The `gunicorn.access: ...` prefix is our own `_RailwayJsonFormatter` shape, so the access records reach the root console handler from `src/utils/logging.py`. `scripts/start_server.py` passes no `--access-logfile` / `--log-config`, and gunicorn 26 emits access lines only when one is set — so access logging is most likely enabled from the Railway service environment (e.g. `GUNICORN_CMD_ARGS`).

## To-be

Background polling requests (at minimum `/api/deploy_status`) produce no INFO log lines on production. Real application logs and gunicorn error-log lines are unchanged.

## Decision

**(b) chosen — gate** [AST-2080](https://linear.app/astralcareermatch/issue/AST-2080)**.** Drop only `RAILWAY_CONFIG`-listed quiet polling paths (starting with `/api/deploy_status`) from `gunicorn.access`; every other access line still logs. Launcher and Railway env are untouched — the Railway log config also carries prod INFO app logs (see plan-fix § Bug: AST-2078).

## Citations

`stat.logging.info`, `stat.logging.warning`, `stat.logging.error`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`

## Scope

### Component scope (as landed — option (b))

* `src/utils/config.py` — modified: `RAILWAY_CONFIG` holds the quiet polling-path list (no hardcoded sets outside config).
* `src/utils/logging.py` — modified: attaches the polling-path filter to the `gunicorn.access` logger, since this facade already owns the root console handler those records land on.
* `scripts/start_server.py` — unchanged (launcher pin not used: it would also silence prod INFO logs).
* Railway prod service variables — unchanged; ops step is record-only (do not remove the log config).

### Technical scope (as landed)

* `src/utils/config.py`: new field `RAILWAY_CONFIG["access_log_quiet_paths"]`, per config-source-of-truth.
* `src/utils/logging.py`: new filter class `_QuietAccessFilter` plus attach-once on `gunicorn.access` inside `get_logger`, so polling requests are dropped before the Railway JSON formatter sees them.

## Acceptance criteria

1. On a Railway deploy after this lands, admin-footer `/api/deploy_status` polls produce no INFO `gunicorn.access` lines in Log Explorer.
2. `logger.info` / `logger.warning` / `logger.error` from `get_logger` call sites still appear on Railway at info / warn / error (AST-1777 behavior unchanged).
3. Gunicorn error-log lines (worker boot, timeouts, crashes) still appear.

## Boundaries

Does not change the footer poll cadence or the `/api/deploy_status` API. Does not touch Telescope logging (`service/telescope/logging_util.py`).

## Notes for planning

Ancestor (checked by Susan): AST-1777 — Logging levels, doc `docs/features/foundation/ast-1777-logging-levels.md` (child AST-1778, `docs/features/foundation/ast-1778-railway-faithful-console-transport-in-get-logger.md`). Both left gunicorn/access loggers explicitly out of scope — this bug is that gap.

## Git branch (authoritative)

Mini-parent `ftr/AST-2074-gunicorn-polling-logs`, child `sub/AST-2074/AST-2078-gunicorn-polling-logs`. Created at bug-fix.

### Comments

#### radia — 2026-10-09T01:02:37.810Z
[code-rubric] PROCEED (Commit: 2e754b15a) Option (b) filter matches plan

#### joan — 2026-10-09T00:49:10.145Z
[board-joan]  CANON: OK

#### betty — 2026-10-09T00:48:28.363Z
[board-betty] TESTS: REVISE
What: no bible entry (docs/test-bible/utils/debug_logging.md lists gunicorn as out of scope; no test exercises gunicorn.access) — missing coverage — need a component test in tests/component/utils/test_debug_logging.py that builds a gunicorn.access LogRecord with a SafeAtoms-style Mapping arg, checks the filter drops it, and checks get_logger INFO/root are unaffected.

Both options get the same verdict. (b) red/green: the U="/api/deploy_status" record is dropped and U="/api/other" is kept. (a) red/green: every gunicorn.access record is dropped while access_log_enabled is False. Blast radius check: no existing test pins RAILWAY_CONFIG key sets, gunicorn.access filters, or attach-once flags, so nothing breaks under either option. The AC6 grep gate exempts utils/logging.py. Prod env logconfig / the root WARNING default are ops/separate-bug concerns, not test scope here.

#### ada — 2026-10-09T00:47:30.707Z
`origin/sub/AST-2074/AST-2078-gunicorn-polling-logs` @ `2d9170458` · decision needed: (a)/(b)

---

_Implementation detail may live in git history on `origin/dev`._
