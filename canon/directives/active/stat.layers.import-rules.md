---
id: stat.layers.import-rules
kind: statute
scope: layers
point: >
  Imports flow one way down the layers; never back up.
---

# Abstract

Layers exist so that a change has a blast radius you can predict. When imports
only flow downward, you can read `utils` without knowing anything about the
product, and you can test `core` without a browser. The moment one arrow points
back up, both properties are gone: the leaf module now depends on the business
logic that was supposed to depend on it, and the cycle it creates has to be
broken by deferring imports into function bodies — which is how the violation
hides.

**This statute governs code dependencies, not data.** A lower layer receiving
a whole entity object as a plain argument from a caller above it is not a
violation, however large that object is — nothing was imported, a value was
passed, and passing costs nothing extra regardless of size (Python hands over
a reference, not a copy). The violation is a lower layer *importing the
higher layer's code* to decide what to do with data it already has. Confusing
these two is how a real fix gets rejected as "but it still needs the data" —
it already has the data; what it doesn't get to have is the logic that
understands what the data means.

# Statement

Imports flow one direction only:

- `ui/frontend` → `api`, `utils`
- `ui/api` → `core`, `utils`
- `core` → `data`, `external`, `utils`
- `external` → `utils`
- `data` → `utils`
- `utils` → `utils`

No module imports from a layer above it. Deferring an import into a function
body does not exempt it.

**Within `core`, entity data goes through the entity component.** A core module
that needs candidate, company, or job data calls `core.candidate`, `core.roster`,
or `core.tracker` — not `data.database` directly. `core → data` is permitted by
the direction rule, but only the entity component exercises it for entity reads
and writes.

# Scenario

You are in `utils/config.py::resolve_tokens`, resolving `{$TOKEN}` patterns
against `candidate_data` — a whole entity dict, handed to you by the caller as
a plain argument. That part is fine on its own: for most tokens you walk a
static `path` string from the `TOKEN_SOURCES` registry through that dict
(`_walk_dot_path`) and return the value. The function never needed to know
what a candidate is; it just followed a path through a dict, the same as it
would for any nested structure.

`{$BASE_RESUME}` is different. Its registry entry adds
`"serialize": "resume_sections_json"` because a plain path walk isn't enough —
the resume needs real formatting logic, and that logic already exists in
`core.candidate::format_base_resume_for_token`. Importing it is one line, and
putting it inside the function avoids the load-time cycle, so nothing crashes.
What you have actually done is make `utils` — the layer everything depends
on — depend on the product. Relocating the formatter into `utils` would not
fix this: it would still need to know what a resume section is and how it
should serialize, which is exactly the product knowledge `utils` isn't
supposed to carry. The data was never the problem. The import was.

# Do

```python
# src/core/roster.py — core may import down
from src.utils.config import EXTERNAL_CONFIG
from src.data import database
from src.external import playwright

# src/core/gazer.py — core needing entity data goes through the entity component
from src.core.candidate import get_candidate

# src/utils/formatting.py — utils imports only utils
from src.utils.config import GRADE_COLORS

# src/utils/config.py — resolving {$BASE_RESUME} by dispatch, not import
# _SERIALIZERS is populated from above (core registers into it); config never
# imports core to fill this table. Same pattern config.py already uses for
# "source": "config" tokens via _CONFIG_RESOLVERS.
def _replace(match):
    spec = TOKEN_SOURCES[match.group(1)]
    if spec.get("serialize"):
        fn = _SERIALIZERS.get(spec["serialize"])   # looked up, not imported
        return fn(candidate_data) if fn else ""
    return _walk_dot_path(candidate_data, spec["path"])
```

# Don't

```python
# src/utils/config.py:5868 — utils importing core, deferred so it loads
def _replace(match):
    from src.core.candidate import format_base_resume_for_token   # utils -> core
    return format_base_resume_for_token(candidate_data)

# src/data/database.py:7682 — data importing core
from src.core.candidate import ensure_company_search_terms_table_synced

# src/ui/api/api_admin.py — ui reaching past core into data
from src.data import database
rows = database.list_dispatch_tasks()      # ui -> data

# a core module going around the entity component for entity data
from src.data import database
row = database.get_candidate(candidate_id)  # legal direction, wrong door
```

# Resolution

You need something that lives in a layer above you.

1. **Does resolving this need product knowledge, or just data you already
   have?** If it's a shape-only operation on data already in hand — a path
   walk, a lookup, a format string — it belongs in `utils` as-is, no import
   needed, because there was never any logic to reach for. If it needs to
   know what the data *means* — what a resume section is, which state
   follows which — that is product logic and it does not become `utils`-safe
   by moving the file. `format_base_resume_for_token` is the second kind:
   moving it to `utils/formatting.py` would still leave it needing to
   understand resumes.
2. **Can the caller pass it in?** Invert the dependency: the upper layer calls
   down with the value or the callable, rather than the lower layer reaching
   up. For one call site, that's a parameter. For a dispatcher with many call
   sites — like `resolve_tokens` handling every token — it's a name-keyed
   registry the upper layer populates (`_SERIALIZERS[name] = fn`, set by
   `core` on import), and the lower layer only ever does `_SERIALIZERS.get(name)`.
   `config.py` already does this for `"source": "config"` tokens via
   `_CONFIG_RESOLVERS` — the same shape closes the `BASE_RESUME` case. Either
   way it needs no new module, and the import disappears because the lower
   layer stopped asking to be handed a name instead of reaching for the code.
3. **Do two layers need the same helper?** Move it to the lowest layer both may
   import — usually `utils`. Moving down is always compliant; reaching up never
   is.
4. **Reaching past a layer, not above one?** `ui → data` is not a shortcut, it
   is a missing core function. Add it to the core module that owns the entity —
   see `stat.core.entity-save`.
5. **In core, and the entity component lacks what you need?** Add it there rather
   than calling `data.database` yourself. One door per entity is what keeps the
   read and write paths findable.
6. **None of the above?** The layer boundary may be wrong, which is a canon
   question, not a code decision. Escalate per the payload instructions.

# Notes

`scripts/` is exempt entirely per `stat.scripts.exempt-from-layer-rules` —
that is a scope boundary, not an exception to this statement.

One real exception exists to the statement above, checked against Resolution
step 2's inversion technique and deliberately left unfixed rather than
inverted:

**EXCEPTION:** `logging.py` may late-import `database.add_log_entry` inside
`_DatabaseLogHandler._flush_buffer` — the one `utils → data` import in the
codebase. Nowhere else in `utils` may copy this.

**REASON:** needed an easy way to pull log content from batch runs in the
local environment.

**UNTIL:** proper console logging and monitoring is implemented, console
logs are filterable by `batch_id`, and log content persists on a real
retention policy instead of being kept forever.

Logged in `canon-v2/docs/EXCEPTIONLOG.md` — that is the list to check when
it's time to pay this down, not this file.
