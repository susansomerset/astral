---
id: stat.errors.raise-once-log-once
kind: statute
scope: errors
point: >
  Raise where detected, log where handled — never both, never neither.
approved_by: null
approved_at: null
supersedes: null
superseded_by: null
terms: []
applies_when:
  layers: []
  paths: []
  change_types: ["any"]
canonical_refs: []
---

# Abstract

Two failures come from the same confusion about who owns an error. Logging and
re-raising produces the same fault three times in the log at three levels of the
stack, so the real cause is buried in its own echo. Catching and continuing
produces nothing at all, and the fault reappears later as corrupt state with no
trace of where it began. The rule is one owner per error: the layer that detects
it raises, the layer that decides what to do about it logs.

# Statement

Raise at the point of detection without logging. Log at the point where the error
is handled and the response is decided. An exception is never both logged and
re-raised, and never swallowed silently.

# Scenario

A data helper hits a missing row. Logging feels responsible — it is the place
that knows the table and the id. So it logs and raises. The caller catches, adds
the batch context it knows, and logs. The dispatcher catches that, and logs. One
missing row, three entries, and the one with the context that matters is the
hardest to find.

# Do

```python
# detection: raise with the facts, no logging
def get_job(job_id: str) -> dict:
    row = _fetch(job_id)
    if row is None:
        raise JobNotFound(job_id)
    return row

# handling: log once, with the context that decides the response
def run_batch(batch_id: str) -> None:
    for job_id in claimed:
        try:
            process(job_id)
        except JobNotFound as exc:
            logger.warning("batch %s skipping missing job: %s", batch_id, exc)
            continue
```



# Don't

```python
def get_job(job_id: str) -> dict:
    row = _fetch(job_id)
    if row is None:
        logger.error("job not found: %s", job_id)   # logs AND raises
        raise JobNotFound(job_id)

def run_batch(batch_id: str) -> None:
    try:
        process(job_id)
    except JobNotFound:
        pass                                         # swallowed, no trace
    except Exception as exc:
        logger.error("failed: %s", exc)
        raise                                        # logged, re-raised, logged again above
```



# Resolution

You need something at the detection site that looks like it requires a log line.

1. **Need context the handler lacks?** Put it in the exception, not a log call.
  `raise JobNotFound(job_id, table="job")` carries further than a log line and
   arrives with the traceback.
2. **Need the fault visible even if a caller swallows it?** Fix the caller.
  A bare `except: pass` upstream is the violation; a defensive log downstream
   just makes two problems.
3. **Translating to a different exception type?** Raise the new one from the old
  (`raise ConfigError(...) from exc`). That is one raise, not two, and needs no
   log at the boundary.
4. **Genuinely need a second record — a metric, an audit row?** That is not
  logging the error, and this statute does not govern it. Say so in the plan so
   the scorer does not read it as a duplicate log.



# Notes

Re-raising a *different* exception to change the abstraction is fine and is not a
second raise. Logging at the point of translation still is.