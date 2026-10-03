# AST-1777 — Logging levels

<!-- linear-archive: AST-1777 archived 2026-10-02 -->

## Linear archive (AST-1777)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1777/logging-levels  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Railway’s Log Explorer supports severity filters (`debug` / `info` / `warn` / `error`), but Astral’s deploy logs all land as Railway **error** — including healthy `INFO` and `WARNING` lines from `src.core.roster` and the rest of the platform. That makes production triage impossible: every batch looks red. Root cause is transport, not call-site level choice: Python’s console handler defaults to **stderr**, and Railway maps every stderr line to `level.error` unless the line is structured JSON with an explicit `level` field. This epic fixes console transport in the shared logging facade so Railway severity matches the logger level operators already chose, without changing what call sites log or how `app_log` stores rows.

## Functional scope

* **Railway severity fidelity for Astral console logs.** Lines emitted through `src.utils.logging.get_logger` on a Railway deploy show the Railway severity that matches the Python level (`DEBUG`→`debug`, `INFO`→`info`, `WARNING`→`warn`, `ERROR`/`CRITICAL`→`error`), so the Log Explorer filters Susan already has actually separate healthy progress from real failures.
* **Preserve local readability and the DB path.** Off-Railway (local / non-Railway hosts), console lines stay the existing human plain format. `app_log` buffering, columns, batch/candidate contextvars, and fail-visible DB-handler stderr diagnostics stay as they are — this epic is console transport only.
* **Out of scope.** Telescope’s separate `service/telescope/logging_util.py` console setup; gunicorn/access/third-party loggers that bypass `get_logger`; changing which call sites use info vs warning vs error; Execution History UI filters (already ship).

## Component scope

* `src/utils/logging.py` — **modified** — sole platform console/DB logging facade; owns handler stream choice, Railway-structured console emit, and formatter apply path.

## Technical scope

* `src/utils/logging.py` / console setup — **modified**: stop defaulting the stdlib console handler to stderr; attach (or reconfigure) the console handler to **stdout** for product `get_logger` output.
* `src/utils/logging.py` / Railway console emit — **new**: when a Railway environment signal is present (e.g. `RAILWAY_ENVIRONMENT`), emit one JSON object per line on stdout with at least `message` and `level` (Railway’s `debug`/`info`/`warn`/`error` vocabulary, mapping Python `WARNING`→`warn`); when that signal is absent, keep today’s plain `LEVEL name: message` text on stdout.
* `src/utils/logging.py` / `_apply_console_formatter` — **modified**: keep applying the plain formatter only to non-DB console handlers in the non-Railway path; do not restyle the DB handler or the intentional DB-failure stderr writes.
* `src/utils/logging.py` / `_DatabaseLogHandler` + `_db_handler_stderr` — **unchanged behavior**: DB buffer/flush and last-resort stderr failure lines remain; those stderr lines may still appear as Railway error (correct — they are transport failures).

## Architectural definition

* **Patterns to reuse:** no established pattern applies — this is console transport inside the existing logging facade, not an entity/dispatch/artifact arc.
* **New patterns proposed:** none — do not invent a catalog pattern for a one-module Railway emit branch; Telescope already chose stdout-only independently and stays out of scope.
* **Applicable statutes:**
  * [stat.logging.debug](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>) — debug remains ContextVar-gated `logger.debug`; transport must not invent call-site `if debug` or change when debug emits.
  * [stat.logging.info](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.md>) — always-on progress stays succinct `logger.info`; only the console wire format/severity mapping changes.
  * [stat.logging.warning](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md>) — soft-fail warnings stay `logger.warning`; Railway must show them as `warn`, not `error`.
  * [stat.logging.error](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>) — thrown failures stay error-level; transport must not demote real errors or promote healthy info/warning to error via stderr.

## Acceptance criteria

1. On a Railway deploy after this lands, a deliberate `logger.info(...)` from a `get_logger` call site appears in Log Explorer with Railway severity **info** (not error). Fail: that line still filters under `@level:error` only / shows as error while the message text says `INFO`.
2. On the same deploy, a deliberate `logger.warning(...)` appears with Railway severity **warn**. Fail: the line is severity error or info while the Python level was WARNING.
3. On the same deploy, a deliberate `logger.error(...)` (or `exception`) appears with Railway severity **error**. Fail: the line is missing from `@level:error` or is only findable as info.
4. Off-Railway local console for the same call sites still prints the pre-existing plain shape matching `LEVEL name: message` (grep-able; not required to be JSON). Fail: local `flask`/dispatcher console output is JSON-only or still bound to stderr for ordinary info lines.
5. `app_log` rows for the same emits still store level / logger_name / message as today (no schema or column-semantics change). Fail: DB handler dropped, level column wrong, or message format for DB rows changed as part of the console work.
6. Grep gate: no new product call site under `src/` starts using raw `logging.getLogger` / `print` for this fix — console changes live in `src/utils/logging.py` only. Fail: `rg -n 'logging\.getLogger|basicConfig' src/ --glob '!utils/logging.py'` shows new product emit paths added by this epic.

## Open questions

none

## Proposed child tickets

#### 1: **Railway-faithful console transport in get_logger - Ada**

Owns the `src/utils/logging.py` console handler/formatter change: stdout for product logs; Railway-env structured JSON with correct `level` mapping; plain format off-Railway; DB handler and DB-failure stderr left alone. Does **not** own Telescope logging, gunicorn, or call-site level rewrites.
**Citations:** `stat.logging.debug`, `stat.logging.info`, `stat.logging.warning`, `stat.logging.error`
**Scope:** `src/utils/logging.py` — **modified** — sole platform console/DB logging facade; owns handler stream choice, Railway-structured console emit, and formatter apply path. / `src/utils/logging.py` / console setup — **modified**: stop defaulting the stdlib console handler to stderr; attach (or reconfigure) the console handler to **stdout** for product `get_logger` output. / `src/utils/logging.py` / Railway console emit — **new**: when a Railway environment signal is present (e.g. `RAILWAY_ENVIRONMENT`), emit one JSON object per line on stdout with at least `message` and `level` (Railway’s `debug`/`info`/`warn`/`error` vocabulary, mapping Python `WARNING`→`warn`); when that signal is absent, keep today’s plain `LEVEL name: message` text on stdout. / `src/utils/logging.py` / `_apply_console_formatter` — **modified**: keep applying the plain formatter only to non-DB console handlers in the non-Railway path; do not restyle the DB handler or the intentional DB-failure stderr writes. / `src/utils/logging.py` / `_DatabaseLogHandler` + `_db_handler_stderr` — **unchanged behavior**: DB buffer/flush and last-resort stderr failure lines remain; those stderr lines may still appear as Railway error (correct — they are transport failures).
**Estimate: 3**

**Monolith check:** Functional scope has 2 in-scope capabilities (+ explicit out-of-scope). Single child is intentional — one inseparable vertical slice in one facade module (stream + Railway JSON branch + plain path) must ship together for UAT.

---

## Original brief

There are four levels of logging supported in Railway (see picture) "debug" "info" "warn" "error", but all our logging content is showing as error level (see picture)

```
2026-09-22T16:00:40.113482082Z [err]  WARNING src.core.roster: https://theladders.com/job/human-factors-scientist-ph-d-exponent-philadelphia-pa_88905229 -> - [duplicate slug 'theladders_com_4']
2026-09-22T16:00:40.113486273Z [err]  INFO src.core.roster: zocdoc_com_2 | company inflow recorded: DISCOVERED (batch: inflow_discovery-30a8c55d-7f67-4809-84e0-aa1d609f5107)
2026-09-22T16:00:40.191000156Z [err]  INFO src.core.roster: engineering_nyu_edu | company inflow recorded: DISCOVERED (batch: inflow_discovery-30a8c55d-7f67-4809-84e0-aa1d609f5107)
2026-09-22T16:00:40.287546929Z [err]  WARNING src.core.roster: https://onlinelibrary.wiley.com/doi/10.1002/acn3.70518 -> - [duplicate slug 'onlinelibrary_wiley_com_4']
2026-09-22T16:00:40.393590163Z [err]  INFO src.core.roster: morulaa_com | company inflow recorded: DISCOVERED (batch: inflow_discovery-30a8c55d-7f67-4809-84e0-aa1d609f5107)
2026-09-22T16:00:40.486205692Z [err]  WARNING src.core.roster: https://medpagetoday.com/neurology/dementia/123047 -> - [skipped duplicate url 'https://www.medpagetoday.com/neurology/dementia/123047']
2026-09-22T16:00:40.595573561Z [err]  INFO src.core.roster: usuk_bookimed_com | company inflow recorded: DISCOVERED (batch: inflow_discovery-30a8c55d-7f67-4809-84e0-aa1d609f5107)
2026-09-22T16:00:40.683638045Z [err]  WARNING src.core.roster: https://completefamilycareny.com/PatientPortal/MyPractice.aspx?UAID={2F9F56E9-A172-4A93-9A0B-26748504C001}&TabID={X}&ArticleID=NW-854695 -> - [duplicate slug 'completefamilycareny_com']
```

![Screenshot 2026-09-22 at 1.47.05 PM.png](https://uploads.linear.app/6d08b154-c90f-497b-8dae-9a0bb7b7b5cd/c1e88cc2-99cc-4f98-82b3-717285c420d7/7528bf64-2028-48f1-abe7-4f92b1914cbf)

![Screenshot 2026-09-22 at 1.47.19 PM.png](https://uploads.linear.app/6d08b154-c90f-497b-8dae-9a0bb7b7b5cd/4a419525-adb6-405a-a907-5a161b7ebd9b/65b4b480-7abe-46c0-8cc2-05d6f0075370)

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
