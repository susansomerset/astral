---
id: astral.standards.utils-data-late-import-only
title: Utils→data late-import only
tier: scoped
checkable: hook
status: active
applies_when:
  layers: ["utils"]
  paths: ["src/utils/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

The only approved runtime `utils → data` path is a late import of `add_log_entry` inside `_DatabaseLogHandler._flush_buffer` in `logging.py`. Do not copy this pattern elsewhere in utils.

## Rationale

Module-level utils→data imports create import cycles; the logging sink is the documented exception (AST-388).

## Examples

### Conforming

- `logging.py` late-imports database only inside `_flush_buffer`.

### Violating

- `formatting.py` imports `src.data.database` at module top for a convenience lookup.
