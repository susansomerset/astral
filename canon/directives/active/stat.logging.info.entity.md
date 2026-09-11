---
id: stat.logging.info.entity
kind: statute
scope: logging
point: >
  Entity progress is id-pipe type and event.
approved_by: null
approved_at: null
supersedes: null
superseded_by: null
terms: []
applies_when:
  layers: ["core"]
  paths:
    - "src/core/roster.py"
    - "src/core/consult.py"
    - "src/core/candidate.py"
    - "src/core/meteorite.py"
  change_types: ["add", "modify"]
canonical_refs:
  - path: src/utils/config.py
    symbol: ENTITY_TYPES
  - path: src/core/roster.py
    symbol: saved nav_links
  - path: src/core/consult.py
    symbol: title to_state
  - path: src/core/meteorite.py
    symbol: meteorite state
---

# Abstract

An `ENTITY_TYPES` member taking its success path is a different grep from a
dispatch task rolling up. Operators look up the entity id, the type, and
what finished. `[short_name] saved 12 nav_links` and `  title -> state` are
close but do not share a scan family. Channel and always-on duty are
`stat.logging.info`. This statute is the pipe.

# Statement

When an entity makes expected progress, emit one `logger.info` through
`get_logger`:

`<entity_id> | <entity_type> <event>: <detail> (batch: <batch_id>)`

`entity_type` is a member of `ENTITY_TYPES` in `src/utils/config.py`. Do not
restate that list here. Do not gate. Do not log I/O guts (page bodies, char
counts, CSE hits) on this line.

# Scenario

Nav links persist for acme-corp on an inflow batch. The scan line should
name the company, that nav links were saved, how many, and the batch.
`[acme-corp] saved 12 nav_links` is almost it, but consult's
`  Software Engineer -> qualified` and candidate state lines will not grep
as the same family. Dumping scrape char counts onto the same line is debug
noise in production.

# Do

```python
from src.utils.logging import get_logger

logger = get_logger(__name__)

logger.info(
    "%s | company %s: %s (batch: %s)",
    short_name,
    "nav_links saved",
    n,
    batch_id,
)
logger.info(
    "%s | job %s: %s (batch: %s)",
    job_id,
    "consult completed",
    to_state,
    batch_id,
)
logger.info(
    "%s | candidate %s: %s -> %s (batch: %s)",
    candidate_id,
    "state",
    from_state,
    to_state,
    batch_id,
)
logger.info(
    "%s | meteorite %s: %s -> %s (batch: %s)",
    row_id,
    "state",
    from_state,
    to_state,
    batch_id,
)
```

# Don't

```python
logger.info("[%s] saved %s nav_links", short_name, n)
logger.info("  %s -> %s", title, to_state)  # job title, no type, no batch
logger.info("[%s] scraped %s (%s chars)", short_name, url, n)  # I/O guts
logger.info("forced candidate state transition: %s %s -> %s", candidate_id, from_state, to_state)
if debug:
    logger.info("%s | company %s: %s (batch: %s)", short_name, "nav_links saved", n, batch_id)
```

# Resolution

Unsure whether this is an entity line, a dispatch rollup, or debug.

1. **This row took the success path?** This info line.
2. **This row missed the happy path, no throw?** `stat.logging.warning`
   (who + why). Not this statute.
3. **The whole dispatch task finished?** `stat.logging.info.dispatcher` —
   do not also write a dispatch-shaped line from the entity caller.
4. **Page HTML, CSE hits, prompt bodies?** `stat.logging.debug` when debug
   is activated.

# Notes

`entity_id` is the operator handle already used in admin/dispatch for that
type. `src/core/tracker` does not log; core callers emit this line. Adding a
type is a config change to `ENTITY_TYPES`; this statute does not need another
edit.
