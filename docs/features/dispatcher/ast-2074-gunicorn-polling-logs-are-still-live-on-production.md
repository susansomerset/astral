# AST-2074 — Gunicorn polling logs are still live on production

<!-- linear-archive: AST-2074 archived 2026-10-16 -->

## Linear archive (AST-2074)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2074/gunicorn-polling-logs-are-still-live-on-production  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Still seeing INFO logs like this on prod:
gunicorn.access: 100.64.0.1 - - \[08/Oct/2026:23:11:28 +0000\] "GET /api/deploy_status HTTP/1.1" 200 202 "[https://astral.up.railway.app/jobs/meteorites](<https://astral.up.railway.app/jobs/meteorites>)" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36"

## As-is

Every open admin tab polls `GET /api/deploy_status` every 30s (`AdminDeployFooter.tsx` `setInterval(..., 30_000)`), and each poll writes an INFO `gunicorn.access` line to the production Railway log. The `gunicorn.access: ...` prefix is our own `_RailwayJsonFormatter` shape (`"<logger name>: <message>"`), so the access records are reaching the root console handler installed by `src/utils/logging.py`. Our launcher (`scripts/start_server.py`) passes no `--access-logfile` / `--log-config`, and gunicorn 26 emits access lines only when one of those is set — so access logging is almost certainly being switched on from the Railway service environment (e.g. `GUNICORN_CMD_ARGS`), which is not visible from the repo.

## To-be

Background polling requests (at minimum `/api/deploy_status`) produce no INFO log lines on production. Real application logs and gunicorn error-log lines are unchanged.

## Proposed steps

1. Confirm on the Railway prod service whether `GUNICORN_CMD_ARGS` (or similar) enables `--access-logfile` / `--log-config`. **Susan decision:** do we want *any* access lines on prod, or none?
2. **If none:** remove that env override, and make `scripts/start_server.py` pin access logging off so an env var can't silently re-enable it (CLI args win over `GUNICORN_CMD_ARGS`).
3. **If we keep access logs but drop the polling noise:** add a `logging.Filter` on the `gunicorn.access` logger that drops a config-listed set of quiet polling paths (starting with `/api/deploy_status`), attached once at server start.
4. Deploy and verify in Railway Log Explorer that the 30s `deploy_status` lines are gone while normal request and error lines remain.

## Component scope

* `scripts/start_server.py` — modified: the single place the gunicorn command is built; pins access-log behavior so prod env can't drift it.
* `src/utils/config.py` — modified: `RAILWAY_CONFIG` holds the access-log on/off setting and, if step 3 is chosen, the quiet-path list (no hardcoded sets outside config).
* `src/utils/logging.py` — modified only if step 3 is chosen: attaches the polling-path filter to the `gunicorn.access` logger, since this facade already owns the root console handler those records land on.
* Railway prod service variables — ops change, not a repo file: remove or correct the env override that turned on access logging.

## Technical scope

* `scripts/start_server.py`: modified launcher — adds the access-log argument(s) read from `RAILWAY_CONFIG` to the `gunicorn` exec list, so behavior comes from config, not from Railway env.
* `src/utils/config.py`: new field(s) on `RAILWAY_CONFIG` — an access-log toggle and (step 3 only) a list of quiet polling paths, per config-source-of-truth.
* `src/utils/logging.py` (step 3 only): new filter class plus a modified console-setup path that installs it on `gunicorn.access` once, so polling requests are dropped before the Railway JSON formatter sees them.

## Ancestor candidates

- [X] AST-1777 — Logging levels (`docs/features/foundation/ast-1777-logging-levels.md`): built the Railway JSON console transport these lines flow through; its Boundaries explicitly left gunicorn/access loggers out of scope, which is the gap this bug falls into.
- [ ] AST-1778 — Railway-faithful console transport in get_logger (`docs/features/foundation/ast-1778-railway-faithful-console-transport-in-get-logger.md`): the child that implemented the root stdout handler + `_RailwayJsonFormatter`; same "does not own gunicorn/access" boundary.
- [ ] AST-646 — Deploy status API and admin nav footer (`docs/features/interface/ast-646-deploy-status-api-and-admin-nav-footer.md`): introduced `/api/deploy_status` and the 30s footer poll that generates the noise.
- [ ] AST-1093 — Gnarly looking deploy logs on Railway (`docs/features/foundation/ast-1093-gnarly-looking-deploy-logs-on-railway.md`): earlier Railway log-noise cleanup (gaze_email tick spam); related intent, but a different noise source.

### Comments

#### chuckles — 2026-10-09T00:49:58.416Z
AST-2078 gated on [AST-2080](https://linear.app/astralcareermatch/issue/AST-2080) — Susan picks (a) drop all access lines or (b) drop polling paths only; test gap [AST-2079](https://linear.app/astralcareermatch/issue/AST-2079) follows AST-2078.

---

_Implementation detail may live in git history on `origin/dev`._
