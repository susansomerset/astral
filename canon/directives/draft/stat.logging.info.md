---
id: stat.logging.info
kind: statute
scope: logging
point: >
  Log expected progress through utils logger.info.
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
  - path: src/core/agent.py
    symbol: run_next hop
---

# Abstract

Production logs should show that the run is moving as designed — a hop fired, a
batch finished, an item took the success path. Dumping search hits, prompts, or
fail guts onto `info` either hides real progress or trains operators to ignore
the level. Expected progress is `logger.info` via `src.utils.logging.get_logger`.

# Statement

When a backend path makes expected progress, emit `logger.info` through
`get_logger` from `src.utils.logging`. Do not `print`, do not call stdlib
`logging.getLogger`, and do not put payloads or failure detail on `info`.

# Scenario

A consult hop completes and the next `run_next` label is written. You want that
visible in Execution History without turning debug on. Putting the CSE hit list
or the raw model body on the same `info` line makes every quiet production run
as noisy as a debug dump, and `print("hop done")` never reaches `app_log`.

# Do

```python
from src.utils.logging import get_logger

logger = get_logger(__name__)

logger.info(
    "run_next hop: %s -> %s batch_id=%s",
    from_hop,
    to_hop,
    batch_id,
)
logger.info(
    "[%s/%s] completed processed=%s passed=%s",
    task_key,
    batch_id,
    processed,
    passed,
)
```

# Don't

```python
print("starting batch")                          # never reaches app_log
import logging
logging.getLogger(__name__).info("hop done")     # bypasses utils facade
logger.info("[DEBUG] cse hits=%s urls=%s", n, urls)  # payloads are debug
logger.info("vet reject slug=%s reason=%s", slug, reason)  # item failure is warning
```

# Resolution

The line feels like progress but also carries found/recorded guts.

1. **Success path, one scannable fact?** `info`. Hop boundaries and
   `log_llm_batch_summary` success when `log_batch_id` is set stay here.
2. **The item failed its happy path without throwing?** `stat.logging.warning`.
3. **An exception was thrown?** `stat.logging.error` (and
   `stat.errors.raise-once-log-once`).
4. **Inputs, outputs, CSE hits, prompt/response bodies?** `stat.logging.debug`,
   and only when this run is debug-gated.

# Notes

`info` is always on. Debug is additive; do not gate hop/`info` progress behind
the debug flag.
