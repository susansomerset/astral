---
id: stat.logging.error
kind: statute
scope: logging
point: >
  Log thrown exceptions once at the handler.
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
    symbol: runner crashed
---

# Abstract

An exception means the code did not take a configured fail path — a runner
crashed, a provider blew up, a constraint fired. `print(exc)` never reaches
`app_log`. Logging at the data layer *and* in the dispatcher triples the same
fault. The handler that decides the response logs once, through utils, at
`error` / `exception`.

# Statement

When an exception is thrown, the layer that handles it emits `logger.exception`
or `logger.error` through `get_logger` from `src.utils.logging`. Data raises and
does not log. Do not `print`. Do not log-and-re-raise. Soft-fails with no throw
are `stat.logging.warning`, not `error`.

# Scenario

`run_consult_task` raises mid-batch. The dispatcher catches, marks the ledger
FAILED, and must leave one traceback a human can find. If `database.py` already
logged "row missing" and then raised, Execution History shows three copies and
the batch context is the one that gets lost. If the dispatcher `print`s the
exc, `app_log` never sees it.

# Do

```python
from src.utils.logging import get_logger

logger = get_logger(__name__)

try:
    summary = await runner(task)
except Exception:
    logger.exception("[%s/%s] runner crashed", task_key, batch_id)
    final_status = "FAILED"
    # handle here — do not raise again after logging
```

# Don't

```python
print(exc)                                       # no app_log
logger.info("provider failed: %s", e)            # wrong level
logger.error("job not found: %s", job_id)
raise JobNotFound(job_id)                        # data logs AND raises
try:
    process(job_id)
except Exception as exc:
    logger.error("failed: %s", exc)
    raise                                        # logged, then logged again above
```

# Resolution

The fault looks like both an item fail and a crash.

1. **Configured miss, no throw** (vet reject, score floor, title too short)?
   `stat.logging.warning` — not this statute.
2. **Who logs, who raises?** `stat.errors.raise-once-log-once`. This statute
   only picks the **level** and the **channel** (`get_logger`, not `print`).
3. **LLM call failed and `log_batch_id` is set?** `log_llm_batch_summary(...,
   error=...)` is the error line for that hop — do not add a second `error`
   for the same fault.
4. **Detection site wants to be helpful?** Put facts on the exception; do not
   log there.

# Notes

UI APIs return JSON errors; they do not `print` the traceback to stdout.
`src/data/` does not log. The `logging.py` DB sink's stderr fallback on flush
failure is not product `error` logging — see `stat.layers.import-rules`.
