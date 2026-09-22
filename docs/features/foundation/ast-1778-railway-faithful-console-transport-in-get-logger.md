# AST-1778 — Railway-faithful console transport in get_logger

- **Linear:** [AST-1778](https://linear.app/astralcareermatch/issue/AST-1778)
- **Parent:** [AST-1777 — Logging levels](https://linear.app/astralcareermatch/issue/AST-1777)
- **Publish ref:** `sub/AST-1777/AST-1778-railway-faithful-console-transport-in-get-logger`

Console transport fix inside `src/utils/logging.py` so Railway Log Explorer severity matches the Python level already chosen at call sites. Product logs go to **stdout**; on Railway they emit one JSON object per line with an explicit `level` field (`debug` / `info` / `warn` / `error`); off-Railway they keep the existing plain `LEVEL name: message` shape. `app_log` / DB handler / DB-failure stderr are unchanged. No Telescope, gunicorn, or call-site level rewrites.

## UAT fitness

- **AC restored:** Parent AST-1777 AC 1–6 (mirrored on this child): (1) Railway deploy — deliberate `logger.info(...)` from a `get_logger` call site appears in Log Explorer with Railway severity **info** (not error). (2) Same deploy — deliberate `logger.warning(...)` appears with Railway severity **warn**. (3) Same deploy — deliberate `logger.error(...)` / `exception` appears with Railway severity **error**. (4) Off-Railway local console still prints the pre-existing plain shape matching `LEVEL name: message` (grep-able; not JSON-only; not bound to stderr for ordinary info). (5) `app_log` rows for the same emits still store level / logger_name / message as today. (6) Grep gate — no new product call site under `src/` uses raw `logging.getLogger` / `print` for this fix; console changes live in `src/utils/logging.py` only.
- **Correct outcome:** On Railway, healthy `INFO` / soft-fail `WARNING` lines from `get_logger` (e.g. `src.core.roster` inflow progress and duplicate-slug warnings) filter under their true severities in Log Explorer, so operators can separate progress from real failures. Local console remains human-readable plain text on stdout.
- **Sibling check:** This epic has a single child — no sibling transport contracts. Unchanged contracts verified by leaving `_DatabaseLogHandler`, `_db_handler_stderr`, `_PrefixedLogger` level methods, and `log_*` contextvars alone; AC5 is the DB-path hold.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done. The bug is every healthy line tagged Railway `error` because stderr + unstructured text — fixing a single noisy exception does not restore severity fidelity for info/warn.
- **Wrong fix rejected:** Do not remap call-site levels, silence roster warnings, or force all logging through stderr “error” styling. Do not redirect the process’s entire stderr, restyle gunicorn/Telescope, or invent a second logging facade. Root cause is console stream + missing structured `level` on Railway; the fix is transport-only inside `get_logger`’s console path.

## Scope gate

Ticket **## Scope** names only `src/utils/logging.py` (console setup → stdout; Railway JSON emit; `_apply_console_formatter` non-DB path; DB handler / `_db_handler_stderr` behavior unchanged). Every Files Changed row and Stage step stays inside that file and those kinds of change.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/logging.py` | Console handler → stdout; Railway JSON formatter with level map; plain formatter off-Railway; `_apply_console_formatter` respects Railway vs plain; DB path untouched | utils |

## Stage 1: Railway-faithful console transport

**Done when:** With `RAILWAY_ENVIRONMENT` set, a `get_logger` info/warning/error emit prints one JSON line on stdout whose `level` is `info` / `warn` / `error` respectively; without that env var, the same emits print plain `LEVEL name: message` on stdout (not stderr); DB handler still buffers `app_log` rows with the same columns; `_db_handler_stderr` still writes failure lines to stderr only.

1. In `src/utils/logging.py`, add `import json` and `import os` next to the existing stdlib imports.

2. Add a module-level Railway level map and detector after `_CONSOLE_FORMATTER`:
   - `_RAILWAY_LEVEL = {logging.DEBUG: "debug", logging.INFO: "info", logging.WARNING: "warn", logging.ERROR: "error", logging.CRITICAL: "error"}` (any other numeric level → `"error"` via `.get(record.levelno, "error")`).
   - `_on_railway() -> bool` returns `bool(os.environ.get("RAILWAY_ENVIRONMENT"))` — that env key only (ticket signal); do not invent alternate Railway probes.

3. Add class `_RailwayJsonFormatter(logging.Formatter)`:
   - `format(self, record)` builds a single-line JSON object with at least:
     - `"level"`: mapped string from `_RAILWAY_LEVEL` as above
     - `"message"`: the fully formatted record text including logger name for scanability — use `f"{record.name}: {record.getMessage()}"`, and when `record.exc_info` is set append the traceback the same way `logging.Formatter.format` would (call `self.formatException(record.exc_info)` and join with a newline). Do **not** put Python’s `WARNING`/`INFO` tokens into `level`; those stay out of the structured field.
   - Emit via `json.dumps(..., ensure_ascii=False)` with no pretty-print (one object, one line).
   - Do not add extra required keys beyond `level` and `message` in this ticket.

4. Add `_ensure_stdout_console_handler() -> None` that configures the **root** logger’s product console handler (not the DB handler):
   - Walk `logging.getLogger().handlers`. Skip any `isinstance(h, _DatabaseLogHandler)`.
   - Among remaining handlers, treat as “console” any `logging.StreamHandler` whose `stream` is `sys.stdout` or `sys.stderr` (same predicate `_apply_console_formatter` already uses).
   - If a console handler exists on `sys.stderr`, re-point `h.stream = sys.stdout` (do not leave product lines on stderr).
   - If no console StreamHandler exists, `logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))` and set root level to `logging.INFO` when the root level is still `NOTSET` only if needed so INFO records flow (do not raise root to DEBUG).
   - Do **not** call `logging.basicConfig(...)` with its default stderr stream. Replace the current `if not base_logger.handlers: logging.basicConfig(...)` block in `get_logger` with a call to `_ensure_stdout_console_handler()` so first configuration never defaults to stderr.
   - Leave gunicorn / third-party handlers that are not stdout/stderr StreamHandlers alone.

5. Update `_apply_console_formatter()`:
   - Still skip `_DatabaseLogHandler`.
   - Still only touch handlers whose `stream` is `sys.stdout` or `sys.stderr`.
   - If `_on_railway()`: `h.setFormatter(_RailwayJsonFormatter())` (instantiate once at module level as `_RAILWAY_JSON_FORMATTER = _RailwayJsonFormatter()` and reuse, matching `_CONSOLE_FORMATTER`).
   - Else: `h.setFormatter(_CONSOLE_FORMATTER)` (unchanged plain `"%(levelname)s %(name)s: %(message)s"`).
   - Never set a formatter on the DB handler; never change `_db_handler_stderr`.

6. In `get_logger`, keep the existing order after the console ensure: `_apply_console_formatter()`, then the existing one-time `_DatabaseLogHandler` attach / atexit / `_PrefixedLogger` return. Do not alter `_PrefixedLogger.debug` / `info` / `warning` / `error` / `exception` / `critical`, `log_debug`, `log_batch_id`, `log_candidate_id`, `flush_log_buffer`, or `log_llm_batch_summary`.

7. Update the module docstring’s “Log output goes to both stdout and the app_log…” paragraph to state: console is always stdout; on Railway the console line is JSON with `level` + `message`; off-Railway the plain `LEVEL name: message` format remains. Do not claim Telescope or gunicorn are covered.

⚠️ **Decision:** Detect Railway solely via `RAILWAY_ENVIRONMENT` (ticket’s example signal). No secondary env keys — keeps the branch boolean and UAT-reproducible (`RAILWAY_ENVIRONMENT=1` locally proves JSON path without a deploy).

⚠️ **Decision:** Re-point an existing stderr `StreamHandler` to stdout rather than adding a second handler. Avoids duplicate lines if something already called `basicConfig` before `get_logger`.

⚠️ **Decision:** Map `CRITICAL` → Railway `error` (parent Technical scope: `ERROR`/`CRITICAL`→`error`). There is no Railway `critical` severity in the operator filter set.

**Out of scope (do not touch):** `service/telescope/logging_util.py`, gunicorn/access loggers, any call site under `src/` other than this facade, Execution History UI filters, `app_log` schema.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1778
**Overall:** APPROVED
**Corpus:** 2ac86c3f693409c364f8630a97198c8dbfa9c6f3
**Publish ref:** `e498799d4e121fe159ab258269e2e3b335f04156` (`origin/sub/AST-1777/AST-1778-railway-faithful-console-transport-in-get-logger`)

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.debug | A | | |
| stat.logging.info | A | | |
| stat.logging.warning | A | | |
| stat.logging.error | A | | |

## Traceability

AC1–6 → Stage 1 (stdout console ensure, `_RAILWAY_LEVEL` / `_RailwayJsonFormatter`, `_on_railway` branch, `_apply_console_formatter` plain vs JSON, DB handler / `_db_handler_stderr` untouched, single-file scope + out-of-scope grep hold).

## Findings

### acceptable

- **Location:** Stage 1 step 4 — `_ensure_stdout_console_handler` gated on `not base_logger.handlers`
- **Finding:** Same gate as today's `basicConfig` path; idempotent re-entry on every `get_logger` call is consistent with current behavior.
- **Recommendation:** No plan change; implementer keeps handler walk idempotent.

### discuss

- **Location:** Stage 1 — AC6 grep gate
- **Finding:** AC6 (no new `logging.getLogger` / `print` emit paths under `src/`) is enforced by scope but not named as an explicit engineer verification step in Done-when.
- **Recommendation:** Optional one-line in Done-when: run the child AC6 `rg` gate before UT; not blocking — Betty/UT will catch violations.

context_tokens≈28000

---

[plan-rubric] PROCEED (Commit: e498799d) Transport plan faithful

## Review

- **Publish ref:** `sub/AST-1777/AST-1778-railway-faithful-console-transport-in-get-logger`
- **Code tip:** `29ada8206149520e81d63493a9e7faf56620a5cc`

