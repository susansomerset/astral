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

1. **Ban new coat-check** — Do not register fetch-if-missing handlers or expand `*_data_keys` maps for greenfield catalog keys.
2. **Batch** — Entity must reach trigger_state with required artifact rows (or explicit empty contract) before claim; component loads rows in pre-dispatch, not inside `do_task`.
3. **Consult** — `_prep_live_content` and token assembly resolve read-current / read-operative bodies before agent entry; no nested `get_*_data` during LLM execution.
4. **Contact** — Pre-load candidate scope and surgical artifact reads at turn start; registered contact-task row loaders are explicit loads, not coat-check — migrate them to read-current as keys land in catalog.
5. **On miss** — Fail visibly, transition to ingestion state, or return user-facing gap — never hide I/O inside an agent tool loop.
6. **Review** — Reject PRs that add runtime `get_job_data` / `get_company_data` / direct `entity["*_data"]` reads for catalog-covered keys outside migration tickets.

# OPEN QUESTIONS / DECISIONS

1. Retirement timeline for existing coat-check maps — tracked on migration epics, not this pattern file.
2. Contact-task row loaders vs artifact read-current — converge on artifact APIs as keys migrate.
