---
id: stat.functions.dont-repeat-yourself
kind: statute
scope: functions
point: >
  Find the existing implementation before writing a second one.
approved_by: null
approved_at: null
supersedes: null
superseded_by: null
terms: []
applies_when:
  layers: []
  paths: []
  change_types: ["add", "modify"]
canonical_refs: []
---

# Preamble

The expensive duplication is rarely a copied block — it is a second
implementation of something that already existed, written because nobody looked.
Both work. Both get maintained. Then one gets a bug fix and the other does not,
and the difference surfaces months later as behaviour that depends on which path
the caller happened to take.

# Statement

Before adding logic, search for an existing implementation and call it. Where two
call sites need the same logic, extract one helper both use rather than copying.

# Scenario

You need to normalise a candidate name for comparison. Writing four lines of
`strip().lower()` handling is faster than finding out whether a normaliser already
exists — and it is only four lines. The next person needs the same thing, does the
same reasoning, and writes a fifth line handling a hyphen case yours does not.
Neither is wrong. Now the two disagree on hyphens.

# Do

```python
from src.utils.formatting import normalize_name

if normalize_name(candidate.full) == normalize_name(query):
    ...

# two branches needed the same guard, so it became one helper
def _claimable(row) -> bool:
    return row.batch_id is None and row.state in CLAIMABLE_STATES

fresh  = [r for r in rows if _claimable(r)]
stalled = [r for r in rows if _claimable(r) and r.age > MAX_AGE]
```



# Don't

```python
# a second normaliser, because the first was not looked for
if candidate.full.strip().lower() == query.strip().lower():
    ...

# the same guard, typed twice, already diverging
fresh   = [r for r in rows if r.batch_id is None and r.state in CLAIMABLE_STATES]
stalled = [r for r in rows if r.batch_id is None and r.age > MAX_AGE]
```



# Resolution

You found existing code that looks like what you need, and reuse is awkward.

1. **Does it answer the same question, or merely look alike?** Two blocks that
  happen to share a shape but answer different questions are not duplication.
   Extracting them couples them, and the next change to one silently breaks the
   other. Leaving both is the compliant answer — note why in a comment.
2. **Same question, wrong signature?** Plan to add a parameter to the existing function
  rather than writing a second one. Extending is compliant; forking is not.
3. **Same question, wrong layer?** Plan to move it to the layer both callers may import,
  per `stat.layers.import-rules`. Do not copy it across the boundary.
4. **Only one caller today, second one hypothetical?** Do not extract yet. This
  statute fires on the second real caller, not the imagined one.

