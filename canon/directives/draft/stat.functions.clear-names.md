---
id: stat.functions.clear-names
kind: statute
scope: functions
point: >
  Names say what the thing does, in language that outlives the ticket.
approved_by: null
approved_at: null
supersedes: null
superseded_by: null
terms: []
applies_when:
  layers: []
  paths: []
  change_types: ["any"]
canonical_refs:
  - path: src/core/tracker.py
    symbol: transition_job_state
---

# Preamble

A name is the only documentation that is read every time. Names that encode the occasion of their creation — a ticket id, a sequence number, a "new" or "v2" — stop meaning anything the moment that occasion is forgotten, which is roughly a month. The reader is then forced back to the issue tracker to understand a line of code. 

# Statement

Identifiers name what the thing does or is, in domain language that remains
accurate after the work that created it is closed. No ticket ids, no sequence
suffixes, no abbreviations that require prior context to expand.

# Scenario

You are fixing a bug filed as AST-1319 and add a handler for it. Naming it
`ast_1319_handler` is honest about where it came from and unambiguous today.
A year later the ticket is archived, the function is still called on every
dispatch cycle, and the only way to learn what it does is to read its body.

# Do

```python
def transition_job_state(job_id: str, to_state: str) -> None:
def retry_stalled_batch(batch_id: str) -> int:
def is_meteorite_company(short_name: str) -> bool:

pending_retries = [...]
```



# Don't

```python
def ast_1319_handler(job_id, to_state):     # names the ticket, not the behaviour
def process_v2(batch_id):                   # v2 relative to what, still?
def do_thing2(short_name):                  # sequence suffix, no meaning
def hndl_pnd_rtry(x):                       # expansion requires prior context

lst2 = [...]
```



# Notes

Renaming an existing identifier is in scope only when the surrounding code is
already being changed. This statute does not license a sweep.