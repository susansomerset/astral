---
id: stat.logging.info
kind: statute
scope: logging
point: >
  Always-on progress is succinct operator-readable logger.info.
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
---

# Abstract

`info` is the everyday production record: the run moved as designed. Those
lines are always on, succinct, and written for a monitoring scan. Parking
that progress on debug makes a quiet run look idle. Dumping search hits or
fail guts onto `info` trains operators to ignore the level. The words on the
line are the surface statute — `stat.logging.info.dispatcher`,
`stat.logging.info.entity`, `stat.logging.info.contact`,
`stat.logging.info.api`. Channel is
`logger.info` via `src.utils.logging.get_logger`.

# Statement

When a backend path makes expected progress, emit a succinct `logger.info`
through `get_logger` from `src.utils.logging`. The line is never gated.
Message shape is the statute for that surface, not function names or
parameter keys. Do not skip it because debug exists. Do not `print`, do not
call stdlib `logging.getLogger`, and do not put payloads or failure detail
on `info`.

# Scenario

A path finishes work with debug off. Execution History should show that it
moved. Leaving the line out because a `debug_index` will fire when debug
mode is activated means a quiet AUTO tick looks idle. `print("done")` never
reaches `app_log`. The pipe template itself lives on the surface statute
for dispatcher, entity, contact, or api.

# Do

```python
from src.utils.logging import get_logger

logger = get_logger(__name__)
# `line` shape: stat.logging.info.dispatcher | .entity | .contact | .api
logger.info(line)
```

# Don't

```python
# progress only when debug is activated
log.debug_index(func="run_next", index=1, total=1, identifier=batch_id, outcome=to_hop)
if debug:
    logger.info(line)  # gated everyday progress
print("starting batch")                          # never reaches app_log
import logging
logging.getLogger(__name__).info("hop done")     # bypasses utils facade
logger.info("[DEBUG] cse hits=%s urls=%s", n, urls)  # payloads are debug
logger.info("vet reject slug=%s reason=%s", slug, reason)  # item failure is warning
```

# Resolution

The line feels like progress but also carries found/recorded guts, or nothing
was logged because debug will cover it.

1. **Success path, one scannable fact?** `info`. Always. Pick the surface
   statute for the words: `stat.logging.info.dispatcher` (task/hop),
   `stat.logging.info.entity` (company/job/candidate),
   `stat.logging.info.contact` (Slack listen + Estelle notes/action),
   `stat.logging.info.api` (route confirmation). Debug does not replace this line.
   `log_llm_batch_summary` success when `log_batch_id` is set stays `info`
   (its wording is that helper's).
2. **The item failed its happy path without throwing?** `stat.logging.warning`.
3. **An exception was thrown?** `stat.logging.error` (and
   `stat.errors.raise-once-log-once`).
4. **Inputs, outputs, CSE hits, prompt/response bodies?** `stat.logging.debug`,
   and only when this run is debug-gated — additive, not instead of `info`.

# Notes

`info` is always on. Debug is additive. Do not gate progress behind the debug
flag. Slack listen + Estelle's intended action and aside are
`stat.logging.info.contact`. Skill/route completion is
`stat.logging.info.api` — do not log both for the same completion.
