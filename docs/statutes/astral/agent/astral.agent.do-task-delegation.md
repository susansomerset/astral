---
id: astral.agent.do-task-delegation
title: Core delegates AI via do_task
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core"]
  paths: ["src/core/**"]
  change_types: ["add", "modify"]
source_docs:
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-23"
---

# Statement

Core calls `do_task` from `src/core/agent.py` for AI work. Core does not assemble Anthropic call params or perform external I/O itself — config informs decisions; external performs I/O.

## Rationale

Centralizing prompt assembly and API calls keeps agent_data/timesheets consistent.

## Examples

### Conforming

- `roster.prefilter_company` calls `await do_task(task_key=..., live_content=...)`.

### Violating

- Core imports `send_to_anthropic` and builds messages inline.
