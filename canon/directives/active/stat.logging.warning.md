---
id: stat.logging.warning
kind: statute
scope: logging
point: >
  Warn per failed item, who and why.
approved_by: null
approved_at: null
supersedes: null
superseded_by: null
terms: []
applies_when:
  layers: ["core", "external", "utils", "ui"]
  paths: ["src/**"]
  change_types: ["add", "modify"]
canonical_refs:
  - path: src/utils/logging.py
    symbol: get_logger
  - path: src/core/consult.py
    symbol: title too short warning
  - path: src/core/consult.py
    symbol: _log_fail_dest
  - path: src/core/roster.py
    symbol: _log_fail_dest
---

# Abstract

A batch item can miss its happy path without anyone throwing — title too short,
vet reject, score below floor, JD not ready. A handler can also catch an
exception and still take a **configured** fail path (retry holding or terminal
state). If failures are silent, UAT cannot see *which* rows failed. If every
catch logs `exception` at ERROR, operators treat expected first-strike retries
as crashes. The production record is a per-item warning (who + why) when the
destination is a retry holding; terminal outcomes use `stat.logging.error`.
Task pass/fail/error counts are `stat.logging.info.dispatcher`, not a second
warning tally.

# Statement

When a batch item fails its happy path without an exception, emit
`logger.warning` through `get_logger` from `src.utils.logging`: one summary line
per failed item (identifier + reason). When a **dispatch batch handler** catches
an exception and routes the entity to a **retry holding** (`retry_base(dest)` is
not `None` per `src.utils.config`), emit the same per-item warning shape
(`who -> dest [why]`); record the traceback on `logger.debug(..., exc_info=True)`
at that handler — not `logger.exception`. Dispatcher skip, admin kill, circuit
disable, and startup ledger repair are the same warning level: who, why, product
next step. Do not `print`. Do not use `warning` for **unrouted** thrown
exceptions (except admin `CancelledError` on a running dispatch task), debug
payloads, or the task rollup.

# Scenario

Ninety-five inflow terms run; three vet-reject. A rollup `fail:3` does not tell
which slugs died or why. Logging `exception` for "title too short" trains
operators to ignore real crashes. A per-item `aid -> dest [reason]` is the
scannable who/why, and it still fires when debug is on — debug adds guts, it
does not replace the warning. Prefilter hydrate raises `ValueError`, the batch
handler transitions the company to `HOMEPAGE_READY_RETRY`, and operators see
`acme_com -> HOMEPAGE_READY_RETRY [hydrate: …]` at WARNING plus the stack on
debug — not ERROR for a first-strike retry.

# Do

```python
from src.utils.logging import get_logger
from src.utils.config import retry_base

logger = get_logger(__name__)

logger.warning("%s -> %s [title too short: %r]", aid, dest, raw_title)
logger.warning("%s skipped — relative job_link: %s", aid, job_link)

# dispatch batch handler after choosing dest (consult / roster pattern):
(logger.warning if retry_base(dest) else logger.error)(
    "%s -> %s [%s]", entity, dest or "-", reason
)
# on except, when retry_base(dest): logger.debug("...", exc_info=True) — not logger.exception
```

# Don't

```python
print("failed", aid)                             # no app_log
logger.info("vet reject slug=%s", slug)          # wrong level
logger.exception("title too short")              # no exception was thrown
logger.exception("hydrate failed")               # retry holding — warning + debug traceback
logger.warning(
    "batch %s tally processed=%s passed=%s failed=%s errors=%s",
    batch_id, processed, passed, failed, errors,
)  # rollup is stat.logging.info.dispatcher
logger.warning("cse raw=%s", page_html)          # payload is debug
logger.warning("[%s/%s] KILLED by admin — thread cleared from memory",
               task_key, batch_id)               # task/batch brackets
logger.warning("run_task: mailbox available_count failed",
               exc_info=True)                    # unrouted throw is stat.logging.error
```

# Resolution

Unsure whether this miss is a warning or an error.

1. **No exception — configured fail / retry / skip?** Warning, per item.
   Task counts: `stat.logging.info.dispatcher`.
2. **Something was thrown (or you are in `except Exception`)?** Default:
   `stat.logging.error`. **Carve-out — dispatch batch, retry holding:** the
   handler already chose (or applies) a destination whose `retry_base(dest)` is
   not `None` → per-item `stat.logging.warning` (`who -> dest [why]`); traceback
   on `stat.logging.debug` with `exc_info=True`. Do not `logger.exception` or
   `logger.error` for that item. **Terminal or error destination**, re-raise
   after log, or no retry route → `stat.logging.error`. Do not
   `logger.warning(..., exc_info=True)`.
3. **Need the CSE body or prompt that led here?** Warning stays; the body goes
   on `stat.logging.debug` when the run is debug-gated.
4. **Empty batch, nothing failed?** No warning. That is not a failed item.
5. **Admin cancelled the running dispatch task (`CancelledError`)?**
   Warning — operator stop, not a crash. Unexpected throws stay
   `stat.logging.error`.

# Notes

Warnings stay on when debug is on. Do not wrap them in `if not debug`.
Estelle `admin_aside` (listen + intended action) is
`stat.logging.info.contact`, not a warning.

Per-item who/why (`aid -> dest [reason]`) is consult and roster dispatch batch
paths. Dispatcher warnings are skip, cancel, auto-disable, and startup repair —
not a second item pipe and not a task tally. English: candidate, task, why, then
the product consequence (`This task is not starting`, `The batch is stopping`).
Do not `task_key/batch_id` square-bracket prefixes. The next-step line is the
product consequence, not the next statement in the function.
