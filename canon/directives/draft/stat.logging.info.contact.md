---
id: stat.logging.info.contact
kind: statute
scope: logging
point: >
  Contact info is listen plus Estelle action notes.
approved_by: null
approved_at: null
supersedes: null
superseded_by: null
terms: []
applies_when:
  layers: ["core"]
  paths: ["src/core/contact.py"]
  change_types: ["add", "modify"]
canonical_refs:
  - path: src/core/contact.py
    symbol: handle_slack_event
  - path: src/core/contact.py
    symbol: run_contact_estelle_turn
---

# Abstract

The Slack listener accepted a DM or @mention and Estelle decided what to
do. That is the Contact production record: who, which event, which action
she intends, and her admin note. Today's trail is debug-only plus a
`warning` for `admin_aside` on concern. Skill completion is not this line —
Estelle drives those through `src/ui/api`, and `stat.logging.info.api`
confirms they ran. Channel and always-on duty are `stat.logging.info`.

# Statement

When Contact listen accepts an inbound Slack event and Estelle's turn
returns, emit one `logger.info` through `get_logger`:

`<candidate_id> | contact listen <event_type> <outcome>: action:<skill_keys> (channel: <channel>) aside: <admin_aside>`

If there is no candidate yet, `candidate_id` is `-`. If she called no
skills, `action:-`. If there is no aside, `aside: -`. Do not gate. Do not
put the Slack transcript or skill-completion status on this line.

# Scenario

Listen is on. A DM arrives, Estelle returns `concern` with an aside
("verify this Slack user before saving email") and `skill_calls` for
`save_candidate`. The scan must show the candidate (or `-`), that listen
handled `message`, the outcome, the intended skill, and the aside — with
debug off. Logging only `contact estelle concern aside candidate=…` at
`warning`, or dumping `text=` of the DM, hides the decision in the wrong
level. A later
`cid | api /api/admin/contact/skills/save_candidate completed: POST 200`
is how the operator confirms the action ran.

# Do

```python
from src.utils.logging import get_logger

logger = get_logger(__name__)

# after run_contact_estelle_turn returns — intended action + note, not completion
logger.info(
    "%s | contact listen %s %s: action:%s (channel: %s) aside: %s",
    candidate_id or "-",
    event_type,
    outcome or "-",
    ",".join(skill_keys) if skill_keys else "-",
    channel,
    (admin_aside.strip() if isinstance(admin_aside, str) and admin_aside.strip() else "-"),
)
```

# Don't

```python
# webhook ack is not the Estelle decision (and is not this statute)
logger.info("%s | api %s completed: POST 200", "-", "/api/slack/events")
# skill ran — that confirmation is stat.logging.info.api
logger.info("%s | contact skill completed: %s", candidate_id, skill_key)
logger.warning(
    "contact estelle concern aside candidate=%s aside=%s",
    candidate_id,
    aside,
)  # aside belongs on the info line
logger.info("%s | contact listen %s: text=%s", candidate_id, event_type, slack_text)  # transcript is debug
if debug:
    logger.info("%s | contact listen %s %s: action:%s (channel: %s) aside: %s",
                candidate_id, event_type, outcome, actions, channel, aside)
```

# Resolution

Unsure whether this is contact, api, warning, or debug.

1. **Listen accepted and the turn returned?** This info line (outcome,
   intended `skill_keys`, `admin_aside`).
2. **Listen off, duplicate, skipped type, not a DM?** No info — nothing
   progressed. Debug when debug mode is activated.
3. **Did the skill/route actually complete?** `stat.logging.info.api`.
   Do not log completion here, even if `run_contact_skill` ran in-process.
4. **Turn threw?** `stat.logging.error`. Do not emit a listen-success line.
5. **Inbound Slack body, prompt, full envelope?** `stat.logging.debug`
   when debug is activated.

# Notes

`event_type` is the Slack event (`message`, `app_mention`). `outcome` is
the conversational envelope (`success`, `concern`, `failure`). Aside is
admin-only — never posted to Slack. The Flask `/api/slack/events` 200 is
an immediate ack on another thread; it is not this line and it is not
skill confirmation.
