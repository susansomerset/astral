---
id: stat.logging.info.dispatcher
kind: statute
scope: logging
point: >
  Dispatcher info is a candidate-pipe task-completed line.
approved_by: null
approved_at: null
supersedes: null
superseded_by: null
terms: []
applies_when:
  layers: ["core"]
  paths: ["src/core/dispatcher.py", "src/core/agent.py"]
  change_types: ["add", "modify"]
canonical_refs:
  - path: src/core/dispatcher.py
    symbol: _log_dispatch_task_completed
---

# Abstract

A dispatch task finishing is what a sysadmin greps for: which candidate,
which entity, which task, the pass/fail/error counts, which batch. Today's
`[%s/%s] batch finished` and `run_next hop:` lines are call-stack true and
scan-useless. Channel and always-on duty are `stat.logging.info`. This
statute is the pipe. Chained `run_next` is the next `task_key`, not a
second kind of log.

# Statement

When a dispatch task completes, emit one `logger.info` through
`get_logger(__name__)`:

`<candidate_id> | dispatch <entity_type> task completed: <task_key> pass:<passed> fail:<failed> error:<errored> (batch: <batch_id>)`

If the finishing task has a `run_next` successor, append
` run_next: <run_next_task_key>` on that same line. The following info is
that `task_key` running normally — same Dispatching / `task completed`
shape. Do not gate these lines. Do not use `task_key/batch_id`
square-bracket prefixes or `run_next hop:` as the message.

# Scenario

An AUTO consult task for a candidate finishes 92 passed, 3 failed, 0
errors. With debug off, the scan line must still name the candidate, that
it was a job task, the task key, and the counts. Logging only
`[consult_grade/ledger-id] batch finished COMPLETED …` forces the operator
into source. A successor `run_next` with no suffix on the finishing line
looks like the chain stalled; a separate “hop completed A → B” line is the
wrong dialect.

# Do

```python
from src.utils.logging import get_logger

logger = get_logger(__name__)

logger.info(
    "%s | dispatch %s task completed: %s pass:%s fail:%s error:%s (batch: %s)",
    candidate_id,
    entity_type,
    task_key,
    passed,
    failed,
    errored,
    batch_id,
)
# when the task row has a successor:
# "... (batch: %s) run_next: %s"  + run_next_task_key
```

# Don't

```python
logger.info("[%s/%s] batch finished COMPLETED | processed=%s passed=%s failed=%s errors=%s",
            task_key, batch_id, processed, passed, failed, errors)
logger.info("run_next hop: %s -> %s batch_id=%s", from_task, to_task, batch_id)
logger.info("%s | dispatch %s hop completed: %s → %s (batch: %s)",
            candidate_id, entity_type, from_task, to_task, batch_id)
if debug:
    logger.info("%s | dispatch %s task completed: %s pass:%s fail:%s error:%s (batch: %s)",
                candidate_id, entity_type, task_key, passed, failed, errored, batch_id)
```

# Resolution

Unsure whether this is info, warning, or error.

1. **Task reached COMPLETED (item fails allowed)?** This info line — the
   counts are the rollup. Per-item who/why is `stat.logging.warning`. Do
   not also warning-tally the same task.
2. **FAILED / timeout INTERRUPTED / thrown?** `stat.logging.error` — one
   `logger.exception` with live facts, what is happening next, and the
   traceback. Admin `CancelledError` is `stat.logging.warning`. Do not emit
   `task completed`. Do not emit a `batch finished FAILED` count tally.
3. **Company/job/candidate row progressed inside the task?**
   `stat.logging.info.entity`, not a second dispatch line.
4. **Guts (CSE hits, prompts)?** `stat.logging.debug` when debug is
   activated.

# Notes

`entity_type` is whatever the dispatch task row carries (including
`meteorite`). Empty → `-` in the pipe only, not a reject. Do not allowlist
or coerce types. Chained tasks are the next `task_key`; the finishing line
may add `run_next: <run_next_task_key>`; the following info is that task
running normally.
