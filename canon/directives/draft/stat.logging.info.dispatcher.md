---
id: stat.logging.info.dispatcher
kind: statute
scope: logging
point: >
  Dispatcher info is candidate-pipe task and hop lines.
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
    symbol: batch finished
  - path: src/core/agent.py
    symbol: _log_run_next_hop_boundary
---

# Abstract

A dispatch task or hop finishing is what a sysadmin greps for: which
candidate, which entity, which task, the pass/fail/error counts, which
batch. Today's `[%s/%s] batch finished` and `run_next hop:` lines are
call-stack true and scan-useless. Channel and always-on duty are
`stat.logging.info`. This statute is the pipe.

# Statement

When a dispatch task completes, emit one `logger.info` through `get_logger`:

`<candidate_id> | dispatch <entity_type> task completed: <task_key> pass:<passed> fail:<failed> error:<errored> (batch: <batch_id>)`

When a `run_next` hop completes, emit:

`<candidate_id> | dispatch <entity_type> hop completed: <from_task> → <to_task> (batch: <batch_id>)`

Do not gate these lines. Do not use `task_key/batch_id` square-bracket
prefixes or `run_next hop:` as the message.

# Scenario

An AUTO consult task for a candidate finishes 92 passed, 3 failed, 0
errors. With debug off, the scan line must still name the candidate, that
it was a job task, the task key, and the counts. Logging only
`[consult_grade/ledger-id] batch finished COMPLETED …` forces the operator
into source. A hop from consult to search with no info line looks like the
chain stalled.

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
logger.info(
    "%s | dispatch %s hop completed: %s → %s (batch: %s)",
    candidate_id,
    entity_type,
    from_task,
    to_task,
    batch_id,
)
```

# Don't

```python
logger.info("[%s/%s] batch finished COMPLETED | processed=%s passed=%s failed=%s errors=%s",
            task_key, batch_id, processed, passed, failed, errors)
logger.info("run_next hop: %s -> %s batch_id=%s", from_hop, to_hop, batch_id)
if debug:
    logger.info("%s | dispatch %s task completed: %s pass:%s fail:%s error:%s (batch: %s)",
                candidate_id, entity_type, task_key, passed, failed, errored, batch_id)
```

# Resolution

Unsure whether this is info, warning, or error.

1. **Task reached COMPLETED (item fails allowed)?** This info line — the
   counts are the rollup. Per-item who/why is `stat.logging.warning`. Do
   not also warning-tally the same task.
2. **FAILED / INTERRUPTED / thrown?** `stat.logging.error`. Do not emit
   `task completed` for a crash.
3. **Company/job/candidate row progressed inside the task?**
   `stat.logging.info.entity`, not a second dispatch line.
4. **Guts (CSE hits, prompts)?** `stat.logging.debug` when debug is
   activated.

# Notes

`entity_type` is `company`, `job`, or `candidate` as the dispatch task
targets. Hop `from_task` / `to_task` are the task keys operators already
see, not `run_next` internals.
