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

---

## Bug: AST-2078 — gunicorn access-log polling noise on prod

Fix child of mini-parent AST-2074. This is the gap this doc's **Functional scope → Out of scope** ("gunicorn/access/third-party loggers that bypass `get_logger`") left open. The AST-1777 console transport itself is not changed.

### As-is

Every open admin tab polls `GET /api/deploy_status` every 30s (`src/ui/frontend/src/components/AdminDeployFooter.tsx` L50, `setInterval(() => fetchStatus(true), 30_000)`). Each poll writes an INFO line to the production Railway log, for example:

```
gunicorn.access: 100.64.0.1 - - [08/Oct/2026:23:11:28 +0000] "GET /api/deploy_status HTTP/1.1" 200 202 "https://astral.up.railway.app/jobs/meteorites" "Mozilla/5.0 …"
```

### To-be

Background polling requests (at minimum `/api/deploy_status`) produce no INFO log line on production. Application logs from `get_logger` and gunicorn error-log lines are unchanged.

### Repro

There is no data fixture; this is process configuration. Steps:

1. With `RAILWAY_ENVIRONMENT=x`, start gunicorn the way prod does, plus the env override prod is suspected to carry. Any log config that routes `gunicorn.access` through propagation reproduces the prefix. A minimal one is `GUNICORN_CMD_ARGS="--log-config-json /tmp/gl.json"` with `/tmp/gl.json` = `{"version": 1}` (gunicorn merges it over its `CONFIG_DEFAULTS`).
2. Open any admin page (or run `curl localhost:$PORT/api/deploy_status`).
3. Stdout shows `{"level": "info", "message": "gunicorn.access: … \"GET /api/deploy_status HTTP/1.1\" 200 …"}` for every request. That is `_RailwayJsonFormatter`'s shape.

### Root cause

- **Repo side.** `railway.toml` `startCommand = "python scripts/start_server.py"` execs `gunicorn server:app --bind --timeout --workers` with no log flags. There is no `gunicorn.conf.py`, `--config`, or log-config file in the repo. With those args alone, gunicorn 26 (`glogging.Logger.access_log_enabled`) emits nothing on `gunicorn.access`.
- **Prod env side (not visible from the repo).** Access logging is therefore enabled by the Railway service environment, most likely `GUNICORN_CMD_ARGS`. The `gunicorn.access:` prefix narrows it down further. A bare `--access-logfile -` gives `gunicorn.access` its own `%(message)s` stdout handler with `propagate = False` (`glogging.Logger.__init__`), and that prints lines **without** the prefix. The prefix only appears when the record propagates to our root handler. That happens on gunicorn's dictConfig/fileConfig path: `--log-config`, `--log-config-json`, or `logconfig_dict` from a config file. All three apply `CONFIG_DEFAULTS` with `"gunicorn.access": {"propagate": True}`. The exact variable must be read off the Railway service; this is an ops step in Proposed change.
- **Consequences (verified locally with gunicorn 26.2.0 and the Repro above).**
  - On the logconfig path, `gunicorn.access` and root share one `console` handler. `_apply_console_formatter` restyles that handler to JSON, so each access line prints **twice**: once on the logger's handler, once via propagation.
  - The record also reaches `_DatabaseLogHandler` on root, so every poll probably writes an `app_log` row too. This is inferred from propagation, not observed against a DB.
- **Load-bearing side finding: prod INFO depends on this env logconfig.** Python's root logger defaults to `WARNING`, not `NOTSET`. So `_ensure_stdout_console_handler`'s `if root.level == logging.NOTSET: root.setLevel(logging.INFO)` never fires, and nothing else in `src/` sets the root level. Local gunicorn runs show:
  - With no env override or with a bare `--access-logfile -`, `get_logger(...).info(...)` lines do **not** reach stdout at all.
  - They appear only when a gunicorn logconfig path applies `CONFIG_DEFAULTS` `"root": {"level": "INFO"}`.

  This is a separate latent AST-1777 defect. It is **not** absorbed here (scope gate); Chuckles should file it as its own bug. It constrains this fix, though: **neither the repo nor the ops step may remove the env logconfig**, or prod loses every INFO app log (AST-2078 AC2 / AST-1777 AC1).

### Proposed change

**DECISION: (b) chosen — gate AST-2080.** Susan closed the gate without replying, so Chuckles proceeded with the recommendation. Launcher and Railway env are untouched. Option (a) is kept below for the record only.

**Common to both — ops step (Railway prod service variables; Susan/ops, not a repo change):** read the platform service's variables for `GUNICORN_CMD_ARGS` (and any `--config` it names). Record the exact value as a Linear comment on AST-2078 before deploy. **Do not remove the logconfig part.** Per Root cause, it is what keeps prod INFO app logs alive today. This narrows the bug Scope's "remove or correct the env override" to "read and record" until the root-level latent bug is fixed separately.

#### Option (a) — no access lines on prod at all

**The CLI pin the bug Scope assumed is unsafe (verified locally):**

- Adding `--log-config ""` / `--log-config-json ""` (empty is falsy, so gunicorn skips dictConfig) silences access lines. But it also drops root back to `WARNING`, so every `get_logger` INFO line vanishes. That breaks AST-2078 AC2.
- Adding `--access-logfile /dev/null` alone does nothing on the logconfig path. dictConfig runs after `_set_handler` and re-attaches `console` with `propagate: True`; both duplicate poll lines still printed.
- `logconfig_dict` (config-file only) and `--log-syslog` (store-true) can't be pinned from the CLI at all.

So the only safe way to deliver (a) from the repo is the same filter mechanism as (b), switched to drop everything:

1. `src/utils/config.py` / `RAILWAY_CONFIG`: add `"access_log_enabled": False` with a one-line comment: "False drops every gunicorn.access record in-process; Railway env cannot re-enable it."
2. `src/utils/logging.py`: same `_QuietAccessFilter` class, attach-once, and late import as (b) step 2. `filter(record)` simply returns `RAILWAY_CONFIG["access_log_enabled"]`. The docstring line becomes: "Telescope console setup is out of scope; gunicorn access lines are dropped when `RAILWAY_CONFIG['access_log_enabled']` is False (AST-2078)."
3. `scripts/start_server.py`: **unchanged**.

**Scope consequence:** the bug Scope allows `src/utils/logging.py` "only if step 3 is chosen". Choosing (a) therefore needs Chuckles to amend Scope so `logging.py` also covers the drop-all filter. This is a small omission, the same kind of change, with no Archie widening. If Susan picks (a), treat that pick as the amendment trigger.

Files: `src/utils/config.py`, `src/utils/logging.py`.

#### Option (b) — keep access lines, drop config-listed quiet polling paths (recommended)

A logger-level filter on `gunicorn.access` runs before **any** handler on that logger and before propagation. It holds no matter which gunicorn setting enabled access logging: `--access-logfile`, `--log-config*`, `logconfig_dict`, or syslog. It also never touches root level or handlers, so prod INFO is unaffected.

1. `src/utils/config.py` / `RAILWAY_CONFIG`: add `"access_log_quiet_paths": ("/api/deploy_status",)` with a comment: "Exact request paths (gunicorn atom `U`, no query string) whose gunicorn.access lines are dropped — background polls." Tuple, per no-hardcoded-sets.
2. `src/utils/logging.py`:
   - New `class _QuietAccessFilter(logging.Filter)`. `filter(record)` returns `False` when `record.args` is a `Mapping` and `record.args.get("U") in RAILWAY_CONFIG["access_log_quiet_paths"]`; otherwise `True`. gunicorn passes its `SafeAtoms` dict as the single log arg, so `record.args` is that mapping and `"U"` is `PATH_INFO`. Verified against installed gunicorn 26.2.0.
   - **Late import** `from src.utils.config import RAILWAY_CONFIG` *inside* `filter()`. `config.py` imports `get_logger` at module top, so a top-level or `get_logger`-time import would be circular. This is the same late-import precedent as `add_log_entry` (B2 / AST-388). Comment it.
   - In `get_logger`, next to the DB-handler attach-once block: attach one `_QuietAccessFilter` to `logging.getLogger("gunicorn.access")` exactly once, guarded by a module flag like `_db_handler_attached`. The worker imports the app, so this runs in the worker process that serves requests (no `--preload`). On SIGHUP the workers restart and re-attach. gunicorn's dictConfig, which runs in the master before the app import, does not clear logger filters.
   - Update the module docstring line "Telescope and gunicorn console setup are out of scope." to: "Telescope console setup is out of scope; gunicorn access lines for `RAILWAY_CONFIG['access_log_quiet_paths']` are dropped (AST-2078)."
3. `scripts/start_server.py`: **unchanged** under (b) too. No CLI arg can safely change access logging (see (a)), and the filter applies on or off Railway. Leaving the launcher untouched is a subset of declared scope.
4. Matching is **exact path, any status code**. A failing `/api/deploy_status` (5xx) still surfaces through Flask's error log, which propagates to root, and through gunicorn.error for crashes or timeouts. Status-aware filtering is not proposed (no heuristics without approval).

**Why (b):** both options are now the same mechanism and roughly the same lines of code. (b) is fully inside declared Scope, and it keeps real request lines for triage. **Why someone might pick (a):** Susan wants zero access lines on prod and `app_log` free of all access rows, not just polls. It costs one Scope amendment.

**Prototyped locally against gunicorn 26.2.0 + our `get_logger`, env `--log-config-json`:** (b)'s filter dropped `/api/deploy_status` and kept `/api/other`. Under a bare `--access-logfile -` env, (b) still dropped the poll. The filter is logger-level, so it applies before the access logger's own handler too.

**Rejected:**

- The launcher CLI pin, for the reasons under (a).
- Popping `GUNICORN_CMD_ARGS` from `os.environ` in the launcher. It is a different kind of change than Scope, and it drops the logconfig that prod INFO depends on.
- Fixing the root `WARNING` default here. It is a separate bug and must not be absorbed.

### Blast radius

- `scripts/start_server.py` (the only gunicorn launcher per `railway.toml`) is untouched under both options. Telescope (`service/telescope/`) has its own launcher and logging and is not touched.
- `src/utils/logging.py` (both options): every `get_logger` caller passes through the attach-once block. The filter sits only on `gunicorn.access`, so root, the DB handler, and `_apply_console_formatter` are unchanged. Off gunicorn (dispatcher CLI, scripts), `gunicorn.access` never emits, so the filter is inert.
- `app_log`: the poll rows that propagation probably wrote stop under both options. Under (b), non-poll access lines still reach `app_log` if the env path propagates. That is pre-existing behavior and not widened here.
- Tests: no existing test asserts gunicorn access output. Betty decides at fix-board whether the filter needs a component test. A `LogRecord` with a `SafeAtoms`-style mapping arg is enough; gunicorn does not need to run.
- Separate latent bug, not fixed here: root logger `WARNING` default means INFO app logs depend on the Railway env logconfig (Root cause).

### What must still hold

From AST-1777's acceptance criteria:

- AC1–3: `get_logger` info/warning/error still map to Railway `info`/`warn`/`error` JSON on stdout. Console handler stream and formatter are untouched.
- AC4: the off-Railway plain `LEVEL name: message` on stdout is unchanged.
- AC5: `app_log` rows from `get_logger` emits keep the same level, logger_name, and message. Only `gunicorn.access` records are dropped: polls under (b), all of them under (a).
- AC6: no new `logging.getLogger`/`basicConfig` emit paths outside `src/utils/logging.py`. The filter's `logging.getLogger("gunicorn.access")` lives in `logging.py`.
- The Railway env logconfig stays in place, and root level and handlers are not touched by this fix.

From AST-2078's own acceptance criteria:

- Gunicorn error-log lines (boot, timeouts, crashes) still appear.
- The footer poll cadence and the `/api/deploy_status` API are unchanged.

## Joan fix-board — AST-2078

```
[board-joan]  CANON: OK
```

**Reasoning**

Read the plan-fix patch at `origin/sub/AST-2074/AST-2078-gunicorn-polling-logs` @ `2d9170458` (`## Bug: AST-2078` in `docs/features/foundation/ast-1777-logging-levels.md`). `docs/canon-index.md` is not on this ref; roster skim used `canon/docs/DIRECTIVES-DIRECTORY.md` and overlapping active directives/statutes on the epic worktree (`canon/directives/active/stat.logging.*`, `canon/statutes/astral/standards/astral.standards.logging-via-utils.md`, `astral.standards.no-hardcoded-sets`, `astral.ui.single-gunicorn-worker`).

**One question (canon):** Does the proposed change conflict with or require updating any in-force directive?

**No conflict, no required canon edit** for either Susan option **(a)** or **(b)**:

| Overlap | Judgment |
|--------|----------|
| `stat.logging.info` / `.warning` / `.error` / `.debug` (AST-1777 canon list) | Governs `get_logger(__name__)` call-site channels and shapes. The fix filters `gunicorn.access` records before handlers/propagation; it does not gate, demote, or reshape product `info`/`warn`/`error` JSON on stdout. “What must still hold” matches AC1–AC4. |
| `astral.standards.logging-via-utils` | Product code must not bypass the facade; attaching a filter via `logging.getLogger("gunicorn.access")` inside `src/utils/logging.py` is facade infrastructure, consistent with AC6 (“only in `logging.py`”). |
| `astral.standards.no-hardcoded-sets` | Quiet paths / drop-all flag live in `RAILWAY_CONFIG` in `config.py`, not inline in the filter. |
| `stat.config.data-not-behaviour` (registry skim) | New keys are plain config values; filter logic stays in `logging.py`. |
| Late import in `filter()` | Same documented exception family as `add_log_entry` / AST-388 on `stat.layers.import-rules` (per DIRECTIVES-DIRECTORY note); not a new canon gap. |
| `astral.ui.single-gunicorn-worker` | Unchanged; filter is per-worker attach-once, aligned with single-worker prod. |

**(a) vs (b):** Verdict is **the same (OK)** for both. **(b)** is fully inside the bug’s declared file scope without a ticket-scope amendment. **(a)** needs a **Linear scope** tweak (plan already says Chuckles amends scope if Susan picks drop-all), not a statute/pattern update. Dropping all access lines vs only `access_log_quiet_paths` is an operator/ops preference (noise vs triage), not an ambiguous statute or Archie-only precedent under fix-board rules.

Susan’s open **(a)/(b)** choice blocks **make-fix** per the plan; that is **not** Joan `ESCALATE` (no architectural canon call — both paths are specified and prototype-backed).

**Not in scope here:** F3 `validate-plan` fix mode, R1–R7 scoring, or posting to Linear (Chuckles via `linear_proxy --as joan`).

```text
AST-2078 board-joan done — CANON: OK.
```

context_tokens≈18500

## Radia review — AST-2078

[code-rubric]
**Ticket:** AST-2078
**Publish ref:** `2e754b15a0cb0af904feb702317b7b454bc34236` (`origin/sub/AST-2074/AST-2078-gunicorn-polling-logs`)
**Corpus:** `2d1b73da19cf1d14276e5c26f52b37aa8047d159` (`docs/canon-index.md` absent on publish ref; `stat.logging.*` via `canon_clerk expand`; `astral.config.config-source-of-truth` and `astral.standards.no-hardcoded-sets` via `canon/statutes/astral/` mirrors at same index sha)
**Overall:** CLEAN

## Fix-specific checks

- **[bug-repro]** not applicable — clean board opt-out (fix-board Betty `TESTS: REVISE` routed to sibling AST-2079; no qa-fix / no `[bug-repro]` on this ticket per spawn context).
- **`## What must still hold`** — OK (all items traced below).

## Canon scores

| id | grade | effort | one-line |
|----|-------|--------|----------|
| stat.logging.info | A | | |
| stat.logging.warning | A | | |
| stat.logging.error | A | | |
| astral.config.config-source-of-truth | A | | |
| astral.standards.no-hardcoded-sets | A | | |

## Column diff vs plan stage

no plan-stage scores attached (Joan F2 fix-board `CANON: OK` only; no F3 `validate-plan` per-id column on this ticket)

## Frame diff

- [ ] **Linear Description → Scope:** Reflect **option (b)** and **unchanged** `scripts/start_server.py` / Railway env (not launcher pin or env removal).
- [ ] **Linear Description:** Remove or close **Open decision for plan-fix** — plan-fix patch records **DECISION: (b) chosen — gate AST-2080**.

## Findings

### discuss

- **Linear description vs landed plan** — Issue description still lists an open **(a)/(b)** decision and Scope text that implies modifying `scripts/start_server.py` and Railway env in-repo. The diff implements plan-fix **(b)** only (`config.py` + `logging.py`; launcher and env untouched). **Decision:** Chuckles syncs Linear description to the plan-fix patch when appending this review (doc on branch is authoritative). **Default:** Update Linear text only; no `resolve-child` product work.

### advisory

- **sibling test carry:** Three-dot diff vs `origin/ftr/AST-2074-gunicorn-polling-logs` includes unrelated `docs/features/**` epic-registry **Threads** mirror churn only — no `src/**` or `tests/**` from siblings.
- **Deploy / UAT:** Plan **ops step** (record prod `GUNICORN_CMD_ARGS` before deploy; do not remove logconfig) is not verifiable from the repo diff — track at User Testing / deploy checklist.
- **AST-2079:** Component coverage for `_QuietAccessFilter` intentionally deferred per fix-board; not a defect on this ticket.

### fix-now

(none)

## Notes

- **Diff base:** `origin/ftr/AST-2074-gunicorn-polling-logs...origin/sub/AST-2074/AST-2078-gunicorn-polling-logs` — product delta is `src/utils/config.py` (+`access_log_quiet_paths`) and `src/utils/logging.py` (`_QuietAccessFilter`, attach-once on `gunicorn.access`).
- **Plan fidelity (product):** Matches plan-fix option **(b)** — quiet-path tuple in `RAILWAY_CONFIG`, logger-level filter on atom `U`, late import in `filter()`, docstring update, `start_server.py` unchanged.
- **Canon Scope:** Joan fix-board discussed `astral.standards.logging-via-utils` at F2; it is **not** on the frozen list. Infrastructure `logging.getLogger("gunicorn.access")` inside `src/utils/logging.py` is consistent with plan AC6 and frozen `stat.logging.*` canonical_refs on `get_logger` — **no ESCALATE** (not a mis-scored off-list violation in the diff).
- **`## What must still hold` trace:** AC1–4 — no changes to `_ensure_stdout_console_handler`, `_apply_console_formatter`, or `_PrefixedLogger` emit paths; filter only on `gunicorn.access`. AC5 — `_DatabaseLogHandler` attach unchanged; dropped records never reach root/`app_log`. AC6 — single new stdlib `getLogger` site in `logging.py` for the access logger. Railway logconfig / root level / handlers not modified in repo. AST-2078 AC — no API or footer changes; `gunicorn.error` untouched by filter.
- **Estimate footprint:** Estimate **2** — fits (~33 LOC product + plan doc).

## What's solid

- Config holds the quiet-path set; filter reads it via late import (cycle-safe, AST-388 precedent).
- Attach-once beside DB handler matches existing `get_logger` side-effect pattern; inert off gunicorn.

## Chuckles — post-review branching

| Gate | Parent shape | Next |
|------|----------------|------|
| **PROCEED** (clean, artifact complete) | Normal (AST-2074, live `ftr`) | **Review Posted** → `do-all-the-things` §3h clean-review shortcut → **User Testing** (`resolve-child` skipped) |

context_tokens≈38000

### Chuckles adjudication

Clean (PROCEED, no fix-now). Discuss item (Linear description stale vs option (b)) handled by Chuckles: AST-2078 description synced. Clean-review shortcut (do-all-the-things §3h) → User Testing.

### Test routing — AST-2078

docs-acceptance: no test-tree delivery on this ticket. fix-board `[board-betty] TESTS: REVISE` was routed to the gap sibling AST-2079 (gunicorn.access quiet-filter tests + bible), which lands its own `test()` / `merge-tests` on ftr.

---

## Bug: AST-2079 — gunicorn.access quiet-filter tests + bible (test gap for AST-2078)

Gap sibling of AST-2078, mini-parent AST-2074. This is the test delivery for fix-board `[board-betty] TESTS: REVISE` on AST-2078, applied to the chosen **option (b)** (gate AST-2080). The plan names the tests; **Betty implements them in qa-fix**. The engineer make-fix pass on this ticket is a **no-product-src marker**.

### As-is

The AST-2078 filter is on `origin/ftr/AST-2074-gunicorn-polling-logs` (`code(AST-2078)` `2e754b15a`) with no test coverage:
- No test exercises the `gunicorn.access` logger or `_QuietAccessFilter`.
- `docs/test-bible/utils/debug_logging.md` § AST-1778 still says "Telescope / gunicorn / call-site rewrites out of scope", and its manifest has no node for the filter.

### To-be

One new component test class in `tests/component/utils/test_debug_logging.py` proves:
- A `gunicorn.access` record with `U="/api/deploy_status"` is dropped.
- A record with `U="/api/other"` is kept.
- The quiet list is read from `RAILWAY_CONFIG`, not hardcoded.
- `get_logger` INFO and the root logger are unaffected.

The bible page records the class and a manifest node for it.

### Repro

There is no data-shape fixture; the fake records are built in the test (astral has no seeded DB here). Red/green reference trees:
- **Pre-fix:** `39bbf7afd`, the tip just before `code(AST-2078)`. No filter exists, so the drop assertions fail.
- **Fixed:** `origin/ftr/AST-2074-gunicorn-polling-logs` @ `0b35bcd2c` or later. Everything passes.

### Root cause

Not a product defect. AST-2078 shipped the filter, and fix-board routed its test coverage here rather than through qa-fix on AST-2078.

### Proposed change

All paths are test-tree, so this is Betty's work in qa-fix. **No `src/` change.**

**1. `tests/component/utils/test_debug_logging.py` — new class `TestAst2078GunicornAccessQuietFilter`.** The name follows the `TestAst1988RailwayJsonIds` precedent of naming the product ticket.

- **Helper:** a module-level `_access_record(path)` (or method). It returns
  `logging.LogRecord("gunicorn.access", logging.INFO, __file__, 0, '%(h)s "%(r)s"', ({"h": "127.0.0.1", "r": f"GET {path} HTTP/1.1", "U": path},), None)`.
  - `LogRecord` unwraps a single-Mapping args tuple, so `record.args` is the dict. That is the same shape gunicorn's `SafeAtoms` produces.
  - Use a **plain dict**; do not import gunicorn, so the test stays hermetic.
- **Setup:** each test calls `get_logger(__name__)` first to guarantee the attach-once has run.
  - Do **not** reset `logging_mod._quiet_access_filter_attached`. Resetting would stack a second filter on the process-global logger and leak into other tests.
  - Check results by truthiness, `bool(logger.filter(rec))`. On Python 3.12+ `Logger.filter` returns the record or `False`, not `True`/`False`.

| # | Test | Assertion | Pre-fix (`39bbf7afd`) |
|---|------|-----------|------------------------|
| 1 | `test_deploy_status_access_record_dropped` | `not logging.getLogger("gunicorn.access").filter(_access_record("/api/deploy_status"))` | **red** (no filter → record passes) — bug-repro |
| 2 | `test_other_access_record_kept` | `logging.getLogger("gunicorn.access").filter(_access_record("/api/other"))` is truthy | green (guard against over-dropping) |
| 3 | `test_quiet_paths_read_from_railway_config` | `monkeypatch.setitem(src.utils.config.RAILWAY_CONFIG, "access_log_quiet_paths", ("/api/other",))`, then `/api/other` is dropped and `/api/deploy_status` is kept. Proves config is the source of truth (`astral.standards.no-hardcoded-sets`). | **red** |
| 4 | `test_non_mapping_args_kept` | A `gunicorn.access` record with `args=("x",)` (not a Mapping) is kept. This guards the `isinstance(args, Mapping)` branch so a non-atoms emit never raises or drops. | green |
| 5 | `test_filter_attached_once` | After two more `get_logger(...)` calls, exactly one filter on `logging.getLogger("gunicorn.access").filters` is an instance of `logging_mod._QuietAccessFilter` | **red** (`AttributeError`) |
| 6 | `test_product_info_and_root_unaffected` | With `caplog.set_level(logging.INFO)`, (a) `get_logger("src.test_ast2079").info("ping")` lands in `caplog.records` at INFO; (b) a record named `src.test_ast2079` whose args mapping has `U="/api/deploy_status"` passes `logging.getLogger("src.test_ast2079").filter(...)`, because the filter is only on `gunicorn.access`; (c) no `_QuietAccessFilter` is on `logging.getLogger().filters` or on any root handler's `.filters`; (d) `logging.getLogger().level` is the same before and after a `get_logger` call. Covers `stat.logging.info`. | (a, b, d) green; (c) **red** (`AttributeError`) |

Tests 1, 3 and 5 are the red-pre-fix set. Betty tags whichever she proves red against `39bbf7afd` as `[bug-repro]`; test 1 is the minimum.

**2. `docs/test-bible/utils/debug_logging.md`**

- § AST-1778 · AST-1777 prose: change "Telescope / gunicorn / call-site rewrites out of scope." to "Telescope / call-site rewrites out of scope; gunicorn is out of scope except the `gunicorn.access` quiet filter (§ AST-2078)."
- New section `### AST-2078 · AST-2074 (gap sibling AST-2079 — gunicorn.access quiet filter)`, after § AST-1988. It needs:
  - A one-paragraph summary: logger-level `_QuietAccessFilter` drops `gunicorn.access` records whose atom `U` is in `RAILWAY_CONFIG["access_log_quiet_paths"]`; attached once in `get_logger`; root and handlers are untouched.
  - An `Area | Source | Component tests` table mapping rows 1–6 above to `src/utils/logging.py` (row 3 also `src/utils/config.py`).
  - `**Broken / obsolete:** none`.
  - `**Integration:** none — no integration scenario runs gunicorn.`
- `## QA test manifest`:
  - Add item `12. AST-2078 gunicorn.access quiet filter (bug-repro): tests/component/utils/test_debug_logging.py::TestAst2078GunicornAccessQuietFilter`.
  - Add the same node to the pytest command block.
  - Change the pass criterion to "items 1–9, 11, 12".

### Blast radius

- Test-tree only. The new class runs in the same file as `TestAst1778RailwayConsoleTransport` and `TestAst1988RailwayJsonIds`. It never resets the attach-once flag and restores config via `monkeypatch`, so existing classes are unaffected.
- `caplog` usage matches the existing `TestPrefixedLoggerDebugGating` pattern.
- No product file changes, so AST-2078's verified behavior and its Tests Passed state are not reopened.
- This ticket's make-fix will be a no-product-src marker.

### What must still hold

- AST-2078's **What must still hold** stands; these tests encode it: only `gunicorn.access` records listed in the quiet paths are dropped, and get_logger INFO, root level and handlers are unchanged.
- Existing `test_debug_logging.py` classes and `test_logging_batch.py` stay green with the same results as today.
- No assertion depends on gunicorn being importable or installed.
- Scope: only `tests/component/utils/test_debug_logging.py` and `docs/test-bible/utils/debug_logging.md`. AST-2079's own Scope is test-tree + bible, so there is no `[scope-gate]`.

### QA test manifest (make-fix, publish tip after merge-tests `0a4dd6c23`)

- `[bug-repro]` `tests/component/utils/test_debug_logging.py::TestAst2078GunicornAccessQuietFilter`: 6 passed. Betty proved tests 1, 3 and 5 red on `39bbf7afd`.
- Bible manifest items 1–9, 11, 12 (the `debug_logging.md` pytest block): 33 passed.
- AC6 grep gate (`--glob '!**/utils/logging.py'`): same 4 `src/` hits as `origin/dev`, so no new emit paths.
- No product `src/` change. The product fix is AST-2078 (`2e754b15a`), on this tip via ftr.

**Bible shasum (publish tip):**
- `docs/test-bible/utils/debug_logging.md` — `6028074e43f9b5257b7bd23bcbdfa868146177fa9b471ac4446d925208e63cd2`

## Joan fix-board — AST-2079

```
[board-joan]  CANON: OK
```

**Reasoning**

Skimmed fix-board § Joan pass against `## Bug: AST-2079` on `origin/sub/AST-2074/AST-2079-gunicorn-polling-logs-tests` @ `5081be59b`. Scope is **test-tree + bible only** (`tests/component/utils/test_debug_logging.py`, `docs/test-bible/utils/debug_logging.md`); **no `src/`** on this ticket.

**Canon question:** Does the proposed change conflict with or require updating any in-force directive?

**No.** The patch **documents and asserts** behavior already landed for AST-2078 option (b); it does not change product logging or introduce new policy.

| Touchpoint | Judgment |
|------------|----------|
| `stat.logging.info` / sibling logging statutes | `applies_when` is `src/**`. Tests call `get_logger` and build fake `gunicorn.access` records to prove INFO and non-access loggers are unchanged — encoding AC, not a new call-site pattern in product code. |
| `astral.standards.logging-via-utils` | No new product bypass of the facade; tests exercise the existing filter on `gunicorn.access` inside the utils test module. |
| `astral.standards.no-hardcoded-sets` | Test 3 monkeypatches `RAILWAY_CONFIG["access_log_quiet_paths"]` to prove config sourcing; aligns with the statute, does not amend it. |
| Bible prose (gunicorn “out of scope” → quiet-filter exception) | Test-bible alignment with shipped AST-2078 behavior; not a `canon/directives/active` or statute file change. |

No new carve-out, exception record, or Archie-level precedent is implied — Betty’s qa-fix lands tests/manifest; make-fix here is a no-product-src marker per the plan.

```text
AST-2079 board-joan done — CANON: OK.
```

context_tokens≈22000

## Radia review — AST-2079

[code-rubric]
**Ticket:** AST-2079
**Publish ref:** `26e540ddf274880d426141d7ec7b936b37e1f4a8` (`origin/sub/AST-2074/AST-2079-gunicorn-polling-logs-tests`)
**Corpus:** `2d1b73da19cf1d14276e5c26f52b37aa8047d159` (`stat.logging.info` via `canon_clerk expand`; `astral.standards.no-hardcoded-sets` via `canon/statutes/astral/standards/`)
**Overall:** CLEAN

## Fix-specific checks

- **[bug-repro]** OK — `TestAst2078GunicornAccessQuietFilter::test_deploy_status_access_record_dropped` is the minimum repro: asserts `/api/deploy_status` `gunicorn.access` records fail `Logger.filter` (dropped) after `get_logger` attach-once, matching AST-2078 **To-be** (poll path silent). Would fail on pre-fix `39bbf7afd` (no filter → truthy pass). Not tautological; uses concrete path `U` and logger name `gunicorn.access`. Tests 3 and 5 strengthen config-sourcing and attach-once (also red pre-fix per qa-fix). **Note:** file uses the same convention as `TestAst1988RailwayJsonIds` (class docstring “#1 is the bug-repro” + inline comment), not a first-line `[bug-repro]` marker — acceptable here.
- **`## What must still hold`** — OK (see trace below).

## Canon scores

| id | grade | effort | one-line |
|----|-------|--------|----------|
| stat.logging.info | A | | |
| astral.standards.no-hardcoded-sets | A | | |

## Column diff vs plan stage

no plan-stage scores attached (Joan F2 fix-board `CANON: OK` only)

## Frame diff

(none)

## Findings

### discuss

(none)

### advisory

- **Three-dot vs `ftr` stack noise:** `origin/ftr/AST-2074-gunicorn-polling-logs...origin/sub/.../AST-2079-...` also lists `src/core/contact.py`, `AdminManageSlack.tsx`, `tests/component/core/test_contact.py`, and several non-`debug_logging` bible pages — from `code(AST-2085)` (`e48c8e613`) on the sub branch, not from qa-fix/test commits. **`git diff origin/dev origin/sub/AST-2074/AST-2079-gunicorn-polling-logs-tests`** is **empty** for those paths; vs `dev` the ticket only adds AST-2078 product (`config.py`/`logging.py` from ftr stack) plus `test_debug_logging.py` and `docs/test-bible/utils/debug_logging.md`. Not an AST-2079 scope or canon finding.
- **sibling product carry in three-dot:** AST-2078 `logging.py`/`config.py` appear in `origin/dev...sub` because ftr carries the fix ahead of `dev` — already reviewed on AST-2078; this ticket asserts it.
- **Recommended action (Chuckles, merge-child):** When rolling `sub/.../AST-2079` into `ftr`, expect the branch tip to include **AST-2085** contact changes already on `origin/dev` but not yet on `ftr` — confirm rollup intent so ftr does not accidentally ship unrelated product without Susan’s merge plan.

### fix-now

(none)

## Notes

- **AST-2079 delivery (vs `origin/dev`):** `tests/component/utils/test_debug_logging.py` (+`TestAst2078GunicornAccessQuietFilter`, 6 tests), `docs/test-bible/utils/debug_logging.md` (§ AST-2078, manifest item 12, AC6 glob `!**/utils/logging.py`). Engineer tip `code(AST-2079)` `26e540ddf` is plan-doc marker only — matches Boundaries.
- **Plan fidelity:** Implements plan-fix table rows 1–6, bible edits, and manifest; option **(b)** only (deploy_status dropped, other kept, config monkeypatch, non-Mapping guard, attach-once, product INFO/root).
- **Estimate footprint:** Estimate **1** — fits.
- **`## What must still hold` trace:** (1) AST-2078 AC encoded in tests 1–2, 6 — only quiet paths on `gunicorn.access` dropped; (2) test-fix reported manifest/bible green — existing classes unchanged in diff intent; (3) no `import gunicorn`; (4) scoped files on `dev` delta are test + `debug_logging` bible only.
- **Non-canon:** Cross-ticket AST-2085 in branch history — not smuggled as AST-2079 work (dev-aligned). Raw SQL / migrations: n/a.

## What's solid

- Hermetic `_access_record` with Mapping unwrap matches gunicorn 26 `access_log.info(format, safe_atoms)` shape.
- Truthiness checks on `Logger.filter` are correct for 3.12+.
- Bible manifest and AC6 glob fix are aligned with shipped filter location.

## Chuckles — post-review branching

| Gate | Parent shape | Next |
|------|----------------|------|
| **PROCEED** (clean, artifact complete) | Normal (AST-2074) | **Review Posted** → clean-review shortcut → **User Testing** (`resolve-child` skipped). Sibling AST-2078 already UT on ftr @ `0b35bcd2c`; merge this test branch per epic rollup when ready. |

context_tokens≈42000

### Chuckles adjudication

Clean (PROCEED, no fix-now / discuss). AST-2085 rollup advisory: those commits are already on origin/dev (diff vs dev empty), so landing ftr adds nothing from them. Clean-review shortcut (do-all-the-things §3h) → User Testing.

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/1ef3ec512ecbaa911ec14e2b725fddc6/ac334f46-d2ac-42a5-acae-2ac767e2c10a/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/44acd650-fb24-4d52-997e-13d3503d3e31/store.db` |
| Radia | review | `/home/susan/.cursor/chats/1ef3ec512ecbaa911ec14e2b725fddc6/4f3b11ff-27f8-4f55-8ac0-e1589c976f3a/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-2074 (parent) | ftr/AST-2074-gunicorn-polling-logs |
| AST-2078 | sub/AST-2074/AST-2078-gunicorn-polling-logs |
| AST-2079 | sub/AST-2074/AST-2079-gunicorn-polling-logs-tests |

**Epic worktree:** `astral-AST-2074/` — one active sub checked out at a time.
