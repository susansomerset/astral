---
id: stat.logging.debug
kind: statute
scope: logging
point: >
  Gated debug dumps inputs and outputs.
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
    symbol: debug_index
  - path: src/utils/logging.py
    symbol: debug_detail_block
---

# Abstract

When Susan turns debug on, she means the guts — what was found and what was
recorded, inputs and outputs — so UAT can see data that tests cannot yet pin.
When debug is off, those lines must not appear. `logger.info("[DEBUG] …")` is
always-on noise. `print` never reaches `app_log`. Debug is a gated dump through
the Style D helpers on `get_logger`, not a second `info` dialect.

# Statement

Emit debug-contract lines only when this run is debug-gated. Use `get_logger`
from `src.utils.logging` and `_PrefixedLogger.debug_index` / `debug_detail` /
`debug_detail_block` (long blobs via `truncate_debug_content`). Show found and
recorded inputs/outputs per batch item. No `print`, no stdlib `getLogger`, no
new `logger.info("[DEBUG] …")`, no debug noise in `src/data/`.

# Scenario

An inflow batch of 95 terms runs with debug on so Susan can see CSE hits and
whether ingest wrote the slug. A terminal `summary={failed=3}` without per-index
bodies is useless. The same dump on a quiet AUTO tick fills `app_log` and hides
real `warning`/`error`. Passing `debug=` through every callee is how the flag
gets dropped; the run's debug setting should already be in scope (AST-1625
`log_debug` ContextVar — until that lands, the entry `debug=` sets the flag).

# Do

```python
from src.utils.logging import get_logger

log = get_logger(__name__)
# entry already set the run's debug flag (log_debug / debug=True)

log.debug_index(
    func="roster.vet_inflow_discovery",
    index=12,
    total=95,
    identifier="acme-corp",
    outcome="pass",
)
log.debug_detail('google_cse query="acme corp careers" hits=6')
log.debug_detail("recorded candidate_slug=acme-corp")
log.debug_detail_block(raw_response)
```

# Don't

```python
logger.info("[DEBUG] cse hits=%s urls=%s", n, urls)   # ungated, wrong helper
print(prompt)                                         # no app_log
log.debug_index(...)                                  # when this run is not debug-gated
# src/data/database.py
logger.debug("row missing id=%s", job_id)             # data does not log
logger.debug_index(..., func="term 12/95")            # domain counter; use index N/M
```

# Resolution

The dump is useful but the run might be production.

1. **Debug off?** Do not emit contract lines. Hop `info` and item `warning` still
   fire — those statutes are not gated.
2. **Need who failed in production?** `stat.logging.warning` (per item + tally),
   not an ungated debug dump.
3. **Blob longer than 50 lines?** `debug_detail_block` / `truncate_debug_content`
   (first 15, `<n lines omitted>`, last 15). Do not log the full prompt/response
   untruncated.
4. **Callee has no `debug=` argument?** Read the run flag (ContextVar once
   AST-1625 lands). Do not default to dumping.
5. **`utils → data` for the sink?** Not this statute — the temporary late-import
   lives on `stat.layers.import-rules` until production monitoring exists.

# Notes

Header shape is Style D: `{func} index {N}/{M} {identifier} -> {outcome}`.
Working lines use prefix ` | `. Backend only — no React debug-contract duty.
`run_next hop` and `log_llm_batch_summary` success stay `info`; they are not
contract lines.
