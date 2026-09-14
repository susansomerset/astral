---
id: stat.component.public-then-helpers
kind: statute
scope: component
point: >
  Public surface first, helpers below, grouped by responsibility.
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

A file is read far more often than it is written, and the first question a reader
has is "what does this module offer?" — not "what did its author write first."
Files that grow in authoring order answer the second question. The public surface
ends up scattered between private helpers, and the only way to learn the module's
API is to read all of it.

# Statement

A module presents its public functions first, then its helpers, grouped by
responsibility. New functions are placed by responsibility, not appended.

# Scenario

You add a public `retry_stalled_batch` and the private `_age_of` it needs. The
path of least resistance is both at the bottom of the file, together, where you
were working. That is locally tidy and globally corrosive: the module's public
surface is now split across two places, and the next addition has precedent for a
third.

# Do

```python
# ---- public ------------------------------------------------------------
def claim_batch(...): ...
def retry_stalled_batch(...): ...
def release_batch(...): ...

# ---- claim helpers -----------------------------------------------------
def _claimable(row): ...
def _age_of(row): ...

# ---- release helpers ---------------------------------------------------
def _clear_lock(row): ...
```



# Don't

```python
def claim_batch(...): ...
def _claimable(row): ...           # helper interleaved with public surface
def release_batch(...): ...
def _clear_lock(row): ...
def retry_stalled_batch(...): ...  # appended where the author was working
def _age_of(row): ...
```



# Resolution

The file you are changing does not already follow this shape.

1. **Place your addition correctly anyway.** Put the public function with the
  public surface and the helper with the helpers. A file that is 60% ordered is
   compliant for the part you touched.
2. **No section comments exist?** Add one for the group you are adding to. Do
  not add them throughout the file.
3. **Public surface has no single home to join?** Put yours with the largest
  existing cluster and say so in the plan. Consolidating the rest is a separate
   ticket — `stat.standards.in-scope-only`.
4. **Reordering feels necessary to make your change readable?** It is not.
  Reordering an untouched module inflates the diff and hides the change under  
   the move.

