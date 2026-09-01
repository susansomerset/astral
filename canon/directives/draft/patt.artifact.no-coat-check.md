---
id: patt.artifact.no-coat-check
kind: pattern
scope: [src/core/tracker.py, src/core/roster.py, src/core/candidate.py, src/core/consult.py]
point: >
  Do not lazy-fetch missing entity blob fields at LLM call time — ingest in component state first.
---

# Abstract

**Coat-check** (async fetch-if-missing on first key access during an agent call) is **obsolete** for entity data. Missing content must be resolved by **component/state ingestion** — a defined trigger state, dispatch task, or contact handler loads data **before** the LLM turn — so cache windows stay intact and reads use artifacts-table patterns. Lazy dotted-path fetches spaced across LLM rounds are an anti-pattern.

# Arc

1. **Before** — Runtime needs entity content that is not yet in memory or artifacts table.
2. **During (forbidden)** — Caller invokes `get_<entity>_data(entity, key)` and silently hydrates from external I/O mid-prompt.
3. **During (required)** — Upstream component transitions entity state, runs batch claim, or executes registered contact-task handler that loads the row or artifact explicitly; then passes hydrated context into `do_task`.
4. **After** — Reads use read-current or read-operative; no second-chance fetch inside token resolution.

# Applications

1. Code review flagging new `get_job_data` / `get_company_data` / coat-check handler calls outside migration.
2. Replacing direct `entity["*_data"]` reads that assumed a prior coat-check ran in the same process.
3. Designing Contact Estelle flows: pre-load candidate scope, surgical artifact fetch — not markup-driven lazy fill.

# Exceptions

1. **Registered contact-task handlers** that deliberately load a full entity row synchronously for Estelle markup — intentional boundary, not coat-check (AST-1518 class). Still migrate toward artifact reads where catalog covers the key.
2. **Migration scripts** — out of runtime scope.

# Implementation

1. Do not add new coat-check registrations or expand `*_data_keys` fetch maps for greenfield keys — use artifacts catalog + ingestion states.
2. Batch paths: entity must reach trigger state with required artifact rows or explicit empty contract before claim.
3. Consult grading: `_prep_live_content` and peers assemble pinned/current bodies **before** `do_task`, not via nested get during agent execution.
4. When content is missing at dispatch, fail visibly or queue ingestion — never hide latency inside an LLM tool loop.
5. Audits (job/company/candidate data) document legacy dual paths; new work closes gaps toward this anti-pattern, not grandfather them.

# OPEN QUESTIONS / DECISIONS

1. Retirement timeline for existing coat-check maps — tracked on migration epics, not this pattern file.
2. Contact-task row loaders vs artifact read-current — converge on artifact APIs as keys migrate.
