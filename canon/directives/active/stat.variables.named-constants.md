---
id: stat.variables.named-constants
kind: statute
scope: variables
point: >
  Meaningful literals get named constants; only self-evident values stay inline.
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
  - path: src/utils/config.py
    symbol: CONFIDENCE_MULTIPLIERS
---

# Abstract

A bare literal in a condition carries a decision nobody recorded. The next reader
cannot tell whether `3` is a considered retry budget or a number someone typed,
and cannot change it safely without reading every call site. The cost is not the
literal — it is that the same decision gets re-made, differently, in three places.

# Statement

A literal that encodes a decision is bound to a named constant before use. Only
values whose meaning is evident from the expression itself may appear inline.

# Scenario

You are adding a retry to a fetch. Three attempts feels right, so `range(3)` goes
in. It reads fine today. Six weeks later a second caller retries twice, a third
retries five times, and there is no answer to "what is our retry budget?" — there
are three answers, none of them wrong.

# Do

```python
MAX_FETCH_ATTEMPTS = 3

for attempt in range(MAX_FETCH_ATTEMPTS):
    ...

if score >= MAX_GRADE_VALUE:      # named, so the bound is discoverable
    ...

for index, row in enumerate(rows, start=1):   # 1 is self-evident, stays inline
    ...
```



# Don't

```python
for attempt in range(3):          # what is 3? is it the same 3 as elsewhere?
    ...

if score >= 4:                    # a grading decision, unrecorded
    ...

if len(name) > 255:               # a schema contract wearing a magic number
    ...
```



# Resolution

You have a literal that needs a name, and it is not obvious where the constant
should live.

1. **Used by one function, describing its own mechanics AND unlikely to need later update?** A `_`-prefixed
  module-local constant is fully compliant. This statute asks for a name, not
   a location.
2. **Used across the module AND unlikely to need later update?** Module-level constant, above the first use.
3. **Read by more than one module, or a value Archie would want to change?**
  It is a knob — `stat.config.single-home` governs where it goes.
4. **Cannot name it because you do not know what it means?** That is the
  finding. Do not name it `THRESHOLD_2`; escalate your question in Plan Discuss until you understand.

