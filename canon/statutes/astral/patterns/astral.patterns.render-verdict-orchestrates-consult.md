---
id: astral.patterns.render-verdict-orchestrates-consult
title: render_verdict orchestrates consult
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

Per-job consult lifecycle goes through `render_verdict` in `consult.py`. The dispatcher loops and calls `render_verdict` — it does not call tracker directly for consult outcomes.

## Rationale

One orchestrator owns fetch/prep/do_task/score/save/transition for consult steps.

## Examples

### Conforming

- Dispatcher consult batch calls `render_verdict(task_type, astral_job_id)` per job.

### Violating

- Dispatcher writes job state after interpreting grades itself.
