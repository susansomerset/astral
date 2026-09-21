---
id: stat.logging.info.api
kind: statute
scope: logging
point: >
  API progress logs once at the completing route.
approved_by: null
approved_at: null
supersedes: null
superseded_by: null
terms: []
applies_when:
  layers: ["ui"]
  paths: ["src/ui/api/**"]
  change_types: ["add", "modify"]
canonical_refs:
  - path: src/ui/api/api_contact.py
    symbol: contact_run_skill
---

# Abstract

Work Estelle or the admin UI drives through `src/ui/api` is confirmed here:
one pipe line at the route that completed the work. Slack listen and
Estelle's notes are `stat.logging.info.contact` — this line is how the
operator sees the intended skill actually ran. A second info from
`src/core/contact` for the same completion doubles the scan. Channel and
always-on duty are `stat.logging.info`.

# Statement

When a `src/ui/api` route completes work, emit one `logger.info` through
`get_logger` at that route:

`<candidate_id> | api <route> completed: <method> <status>`

If the route has no candidate, `candidate_id` is `-`. Do not emit a matching
info line from `src/core/contact` for the same completion. Do not gate.
Idempotent GETs that only return current state are not progress — no info.
The Slack Events webhook 200 (ack on another thread) is not this statute.

# Scenario

Estelle's listen line already recorded `action:save_candidate` and an aside.
She POSTs `/api/admin/contact/skills/save_candidate`. The API info line is
the confirmation: candidate, route, POST, 200. Logging completion again
inside `run_contact_skill`, or treating `/api/slack/events` 200 as "Estelle
worked," makes the scan lie. A GET that returns listen state did not
progress.

# Do

```python
from src.utils.logging import get_logger

logger = get_logger(__name__)

logger.info(
    "%s | api %s completed: POST %s",
    candidate_id or "-",
    "/api/admin/contact/skills/" + skill_key,
    status,
)
logger.info(
    "%s | api %s completed: PUT %s",
    "-",
    "/api/admin/contact/listen",
    200,
)
```

# Don't

```python
# src/core/contact.py — completion confirmation belongs at the Flask route
logger.info("%s | contact skill completed: %s", candidate_id, skill_key)
# webhook ack ≠ Estelle turn (stat.logging.info.contact)
logger.info("%s | api %s completed: POST %s", "-", "/api/slack/events", 200)
logger.info("[api_contact] skill ok key=%s", skill_key)  # unstructured
logger.info("%s | api %s completed: GET %s", "-", "/api/admin/contact/listen", 200)  # no progress
if debug:
    logger.info("%s | api %s completed: POST %s", candidate_id, route, status)
```

# Resolution

Unsure who logs, or whether this is info vs warning.

1. **Route completed work (POST/PUT that changed something)?** One info
   line at the Flask handler.
2. **Slack listen accepted / Estelle aside and intended action?**
   `stat.logging.info.contact`.
3. **Core callee behind the route?** No info for the same completion.
   Debug when debug mode is activated (`stat.logging.debug`).
4. **Route threw or returned 5xx?** `stat.logging.warning` or
   `stat.logging.error` as those statutes say — not this pipe.
5. **Dispatch task / entity row, not an HTTP route?**
   `stat.logging.info.dispatcher` / `stat.logging.info.entity`.

# Notes

React (`src/ui/frontend`) does not write `app_log`. There is no
`stat.logging.info.frontend`.
