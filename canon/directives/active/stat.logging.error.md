---
id: stat.logging.error
kind: statute
scope: logging
point: >
  Log thrown exceptions once at the handler, with live facts and traceback.
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
  - path: src/core/dispatcher.py
    symbol: _dispatch_one
---

# Abstract

An exception means the code did not take a configured fail path — a runner
crashed, a provider blew up, a constraint fired. `print(exc)` never reaches
`app_log`. Logging at the data layer *and* in the dispatcher triples the same
fault. The handler that decides the response logs once, through utils, at
`logger.exception`: live facts **and** the full traceback, plus what the
code is doing next. Error is never a tally.

# Statement

When an exception is thrown, the layer that handles it emits
`logger.exception` through `get_logger(__name__)` from `src.utils.logging`.
One record: live facts, an affirmative next step, then the traceback
(`exc_info`). Data raises and does not log. Do not `print`. Do not
log-and-re-raise. Soft-fails with no throw are `stat.logging.warning`, not
`error`. Do not emit a pass/fail/error rollup at `error`.

# Scenario

`run_consult_task` raises mid-batch. The dispatcher catches, marks the ledger
FAILED, truncates the batch, and must leave one `app_log` row a human can
debug: who (candidate, entity, task), what blew up, that the batch is being
truncated, and the stack. A `[%s/%s] crashed` line is stack-true and
fact-poor. A second `batch finished FAILED` count line is a summary —
wrong level and a duplicate. If `database.py` already logged "row missing"
and then raised, Execution History shows three copies. If the dispatcher
`print`s the exc, `app_log` never sees it.

# Do

```python
from src.utils.logging import get_logger

logger = get_logger(__name__)

try:
    summary = await runner(task)
except Exception as exc:
    logger.exception(
        "%s | dispatch %s %s\n  %s: %s\n  Truncating the batch",
        candidate_id,
        entity_type,
        task_key,
        type(exc).__name__,
        exc,
    )
    final_status = "FAILED"
    # handle here — do not raise again after logging
```

# Don't

```python
print(exc)                                       # no app_log
logger.info("provider failed: %s", e)          # wrong level
logger.error("job not found: %s", job_id)
raise JobNotFound(job_id)                       # data logs AND raises
try:
    process(job_id)
except Exception as exc:
    logger.error("failed: %s", exc)
    raise                                        # logged, then logged again above
logger.exception("[%s/%s] crashed", task_key, batch_id)  # stack without live facts
logger.exception("Tick loop error")                      # throw without live facts / next step
logger.error(
    "[%s/%s] batch finished FAILED | processed=%s passed=%s failed=%s errors=%s",
    task_key, batch_id, processed, passed, failed, errors,
)  # summary — counts belong on info COMPLETED
```

# Resolution

The fault looks like both an item fail and a crash.

1. **Configured miss, no throw** (vet reject, score floor, title too short,
   skip with no API key)? `stat.logging.warning` — not this statute.
2. **Who logs, who raises?** `stat.errors.raise-once-log-once`. This statute
   picks the **level**, the **channel** (`get_logger`, not `print`), and
   the **body** (facts + next step + traceback).
3. **LLM call failed and `log_batch_id` is set?** `log_llm_batch_summary(...,
   error=...)` is the error line for that hop — do not add a second `error`
   for the same fault.
4. **Detection site wants to be helpful?** Put facts on the exception; do not
   log there.

# Notes

UI APIs return JSON errors; they do not `print` the traceback to stdout.
`src/data/` does not log. The `logging.py` DB sink's stderr fallback on flush
failure is not product `error` logging — see `stat.layers.import-rules`.
The next-step line is the product consequence (`Truncating the batch`,
`Continuing to the next entity`, `The run is over; this batch was not
recorded as finished`, `The scheduler is still running; the next tick
will retry`). Not the next statement in the function.
Admin `CancelledError` on a running dispatch task is `stat.logging.warning`
(killed by admin), not this statute.
