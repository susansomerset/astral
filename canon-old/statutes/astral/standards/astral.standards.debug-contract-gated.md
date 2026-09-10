---
id: astral.standards.debug-contract-gated
title: Debug contract is debug-gated
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "external", "utils", "ui"]
  paths: ["src/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Emit debug-contract lines only when `debug=True` via `get_logger(..., debug_flag=debug)` / `set_debug_flag`. Use `_PrefixedLogger.debug_index` / `debug_detail` / `debug_detail_block` and `truncate_debug_content` for long blobs. No data-layer debug noise. No new `logger.info("[DEBUG] …")` in files touched for debug work.

## Rationale

Ungated debug spam pollutes production logs and breaks the scannable per-index contract.

## Examples

### Conforming

- A batch runner emits `debug_index` headers only when `debug=True`.

### Violating

- A core path always logs full prompts with `logger.info("[DEBUG] …")` regardless of the flag.
