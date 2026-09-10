---
id: stat.logging.warning
kind: statute
scope: logging
point: >
  Warn per failed item and the batch tally.
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
  - path: src/core/consult.py
    symbol: title too short warning
---

# Abstract

A batch item can miss its happy path without anyone throwing — title too short,
vet reject, score below floor, JD not ready. If that is silent, UAT cannot see
*which* rows failed. If it is an `error` plus a stack, operators treat expected
soft-fails as crashes. The production record is a per-item warning (who + why)
and a batch tally (`failed=` / `errors=`).

# Statement

When a batch item fails its happy path without an exception, emit
`logger.warning` through `get_logger` from `src.utils.logging`: one summary line
per failed item (identifier + reason) and a batch tally of processed / passed /
failed / errors. Do not `print`. Do not use `warning` for thrown exceptions or
for debug payloads.

# Scenario

Ninety-five inflow terms run; three vet-reject. A single `failed=3` at the end
does not tell which slugs died or why. Logging `exception` for "title too
short" trains operators to ignore real crashes. A per-item `aid -> dest [reason]` plus
the tally is the scannable production record, and it still fires when debug is
on — debug adds guts, it does not replace the warning.

# Do

```python
from src.utils.logging import get_logger

logger = get_logger(__name__)

logger.warning("%s -> %s [title too short: %r]", aid, dest, raw_title)
logger.warning("%s skipped — relative job_link: %s", aid, job_link)

logger.warning(
    "batch %s tally processed=%s passed=%s failed=%s errors=%s",
    batch_id,
    processed,
    passed,
    failed,
    errors,
)
```

# Don't

```python
print("failed", aid)                             # no app_log
logger.info("vet reject slug=%s", slug)          # wrong level
logger.exception("title too short")              # no exception was thrown
logger.warning("batch failed=%s", failed)        # tally only — missing who/why
logger.warning("cse raw=%s", page_html)          # payload is debug
```

# Resolution

Unsure whether this miss is a warning or an error.

1. **No exception — configured fail / retry / skip?** Warning, per item + tally.
2. **Something was thrown (or you are in `except Exception`)?**
   `stat.logging.error`.
3. **Need the CSE body or prompt that led here?** Warning stays; the body goes
   on `stat.logging.debug` when the run is debug-gated.
4. **Empty batch, nothing failed?** No warning. That is not a failed item.

# Notes

Warnings stay on when debug is on. Do not wrap them in `if not debug`.
Estelle concern-asides that today use `logger.warning` for an admin-visible
note (not a batch-item fail) are the same level by existing practice — do not
invent a fifth level for them.
