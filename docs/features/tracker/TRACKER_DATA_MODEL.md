# Tracker data model

Job table schema, JSON blobs, batch primitives, and implementation conventions for the Tracker pipeline (ingest, save_job_data, state transitions, batch processing). Implementation uses **snake_case** everywhere (DB columns, config keys, code) even when specs or docs use camelCase.

## Job table (columns)

- **astral_job_id** — Primary key (UUID). Generated at insert.
- **company** — Company short_name (FK to company.short_name). Set at ingest from Gazer.
- **company_job_id** — Employer’s job ID; NULL at ingest, populated by Consult when parsing the raw_job_listing (e.g. joblist task). Used for dedup: incoming raw_job_listing is duplicate if it contains any existing company_job_id for this company.
- **job_title** — NULL at ingest; populated by Consult.
- **job_data** — One JSON blob; see below.
- **state** — UPPERCASE; one of the job state machine values (see config). Batch runners filter by state (e.g. NEW, PASSED_JOBLIST).
- **state_history** — JSON array; see below.
- **batch_id** — For locking during batch processing (Consult, etc.). Set when claiming a job; cleared when done. Not modified by state transitions.
- **batch_created_at** — When the job was claimed for this batch.
- **created_at**, **updated_at**, **state_changed_at** — Timestamps.

Do not duplicate in `job_data` fields that are columns (e.g. company, state). Best practice: designated columns for query/filter and identity; blob for payload and evaluation output.

## job_data (one JSON blob)

Flexible dict; no schema enforced in the data layer. Core/callers decide keys. Merge (add/update keys) vs replace (full overwrite) is a write option; state and identity stay in columns.

- **At ingest:** `{"raw_job_listing": "<html string>"}`. Single key set by Tracker when inserting from Gazer.
- **After Consult parses joblist:** Caller adds e.g. `company_job_id`, `job_title`, `job_link` via save_job_data (merge).
- **After full JD fetch:** e.g. `job_description`, `scraped_at`.
- **After GET/DO/LIKE evaluation:** e.g. `get_score`, `do_score`, `like_score`.

Implementation: deep merge when replace=False; full overwrite when replace=True. No validation of job_data shape in the data layer.

## state_history (JSON array)

Array of objects, one entry per state transition. Enables full job lifecycle visibility and which batch processed each transition.

- **to_state** — State after this transition (UPPERCASE from config).
- **timestamp** — When the transition occurred (e.g. ISO).
- **batch_id** — The job’s current batch_id at transition time (for lineage). Not the batch that “caused” the transition; the batch that had claimed the job when the transition was recorded.

Example:

```json
[
  { "to_state": "NEW", "timestamp": "2026-02-05T12:00:00Z", "batch_id": "gazer-batch-uuid" },
  { "to_state": "PASSED_JOBLIST", "timestamp": "2026-02-05T12:05:00Z", "batch_id": "consult-batch-uuid" }
]
```

Append-only. Data layer appends one entry on each state transition; state and state_changed_at are updated in the same write. batch_id on the job row is left unchanged by transition (cleared separately by clear_job_batch).

## Batch primitives (data layer)

Same naming and parameter order as company batch (see ASTRAL_CODE_RULES 3c). batch_id first; data layer never generates batch_id.

- **claim_job_batch(batch_id, state, limit, sort_by?)** — Set batch_id and batch_created_at on up to limit rows where state=? AND batch_id IS NULL. ORDER BY sort_by (whitelisted) or rowid. Returns count claimed.
- **get_job_batch(batch_id)** — Return full job records (job_data and state_history parsed) for that batch_id.
- **clear_job_batch(batch_id)** — Set batch_id and batch_created_at to NULL for all jobs in the batch. Returns count released.

Core: get_new_batch(state, limit, sort_by?) generates batch_id, calls claim_job_batch then get_job_batch, returns (batch_id, jobs). Caller processes, then calls clear_job_batch(batch_id).

## Ingest contract (Gazer → Tracker)

- **Input:** company (short_name), batch_id (Gazer’s company batch for lineage), raw_job_listings (list of raw HTML strings). Optional compiled title regexes from the active candidate’s `profile.title_patterns` (same semantics as `validate_title_batch`).
- **Dedup:** For each raw_job_listing, duplicate if it contains any existing company_job_id for that company (inverted pattern match). No parsing of HTML in Tracker; company_job_id is populated later by Consult.
- **Title prefilter (AST-389):** When matchers are present, skip insert when no pattern matches `raw_job_listing`; count in **`invalid_title`** (`ingest_jobs` return dict; legacy notes used **`title_mismatch`**). No matchers (or empty patterns) => no prefilter; **`invalid_title`** is 0.
- **New record:** state from `TRACKER_CONFIG["ingest"]["initial_state"]`; state_history initial entry uses the passed batch_id; job_data = {"raw_job_listing": html}; batch_id/batch_created_at NULL.
- **Output:** `{"new": N, "duplicates": M, "invalid_title": T}`. Per-scan aggregates for mismatched/filtered listings are persisted on **`company_job_scan.title_mismatch`** (DB column name differs from the Python ingest return-key — bridged by **`gazer.process_gazer_batch`**).

## Snake_case

- **DB columns:** astral_job_id, company, company_job_id, job_title, job_data, state, state_history, batch_id, batch_created_at, created_at, updated_at, state_changed_at.
- **Config keys:** job_states, etc.
- **job_data and state_history keys:** raw_job_listing, to_state, timestamp, batch_id, etc.

If a spec or external doc uses camelCase, implementation still uses snake_case.

## State machine reference

Job states and transitions are **listed and maintained in `src/utils/config.py`**: `job_states`. Validation (e.g. transition_job_state) uses config as the single source of truth. This file defines the schema and blob shapes only.
