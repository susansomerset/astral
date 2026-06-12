# Roster data model

Company schema, JSON blobs, and implementation conventions for the roster pipeline. Implementation uses **snake_case** everywhere (DB columns, config keys, code) even when specs or docs use camelCase.

## Company table (columns)

- **short_name** — Primary key (company short name).
- **state** — UPPERCASE; one of the company state machine values (see README). Batch runners filter by state (e.g. TO_WATCH, TO_PARSE).
- **company_name** — Human-readable name (derived from URL if not provided).
- **company_website** — Original homepage URL.
- **job_site** — URL of job listings page (when found).
- **batch_id** — For locking during batch processing; same concept as posting table. Set when claiming a company; cleared when done.
- **company_data** — One JSON blob; see below.
- **agent_responses** — Second JSON blob; see below.
- **state_history** — JSON array; one entry per state transition. See below.
- **last_search**, **last_stats**, **search_history**, **updated_at** — As needed for Gazer and history.

Do not duplicate in `company_data` (or `agent_responses`) fields that already exist as columns (e.g. company_name, company_website, job_site). Best practice: designated columns for query/filter; blobs for extra structure and agent output.

## company_data (one JSON blob)

Structured data keyed by use. No duplicate of top-level columns.

- **Notes keyed by config prompt index**  
  Example: `"prefilter_company_notes"` → Grace’s explanation or error from the prefilter task. Same idea for other prompts (e.g. website discovery notes, job-site discovery notes, parse failure notes). Config prompt index = key; value = string or small object (e.g. `{ "reason": "...", "explanation": "..." }`).

- **parse_instructions** (when Parse Job Page succeeds)  
  Single JSON object: **container** and **job_tag** only (CSS selectors). No parse_type or metadata; uniform DOM handling.
  ```json
  {
    "container": "div.joblist",
    "job_tag": "li"
  }
  ```

Do not store company_name, company_website, job_site, etc. inside company_data; they live in columns.

## agent_responses (second JSON blob)

Array of objects with consistent shape: one entry per agent call, so we can audit and replay.

- **timestamp** — Unique per call (e.g. ISO or epoch ms).
- **prompt_index** — Config key for the task (e.g. `find_job_site`, `vet_job_site`, `parse_job_list`, `prefilter_company`). Can repeat across entries.
- **raw_response** — Raw response from the API (or a stable serialization of it).

Example:

```json
[
  { "timestamp": "2026-01-30T12:00:00.000Z", "prompt_index": "find_job_site", "raw_response": { ... } },
  { "timestamp": "2026-01-30T12:00:05.000Z", "prompt_index": "vet_job_site", "raw_response": { ... } }
]
```

Implementation: snake_case keys; timestamps unique; prompt_index may repeat.

## Config prompt / task naming (single-layer)

Roster flows use these config keys; roster.py decides which to call in which context. No nested “agent” layer; names are semantic.

- **find_job_site** — “Pick the URL”: rank crawl URLs, return top candidate(s). Used once per company in Locate Job Page.
- **vet_job_site** — “Are you sure?”: analyze page content, return response_type (try_parse, no_jobs_msg, try_link, push_button, no_clue, bot_block). May be used multiple times (e.g. retry after following a link).
- **parse_job_list** — Receives culled DOM (body element) from the confirmed job list page; returns container, job_tag, parse_type, metadata. Used in Parse Job Page.

Use consistent “site” language (job_site, find_job_site, vet_job_site) in config and code. Specs may say “page” out of habit; implementation prefers “site”.

## state_history (JSON array)

Array of objects, one entry per state transition. Same shape as job.state_history (see TRACKER_DATA_MODEL.md). Enables full company lifecycle visibility and which batch processed each transition.

- **to_state** — State after this transition (UPPERCASE from config).
- **timestamp** — When the transition occurred (ISO).
- **batch_id** — The company's current batch_id at transition time (for lineage).

Example:

```json
[
  { "to_state": "TO_PARSE", "timestamp": "2026-02-10T12:00:00Z", "batch_id": "locate-batch-uuid" },
  { "to_state": "WATCH", "timestamp": "2026-02-10T12:05:00Z", "batch_id": "parse-batch-uuid" }
]
```

Append-only. `transition_company_state()` in roster.py is the single entry point (mirrors `tracker.transition_job_state()` for jobs). Data layer preserves state_history on non-transition saves.

## Snake_case

- **DB columns**: short_name, company_name, company_website, job_site, company_data, agent_responses, batch_id, etc.
- **Config keys**: find_job_site, vet_job_site, parse_job_list, prefilter_company, prefilter_company_notes, etc.
- **company_data and agent_responses keys**: container, job_tag, prompt_index, raw_response, timestamp, etc.

If a spec or external doc uses camelCase, implementation still uses snake_case.

## State machine reference

Company states and transitions are **listed and maintained in `src/utils/config.py`**: `company_states` and `company_state_transitions`. Same pattern as job states. README redirects to config as the single source of truth. This file defines the schema and blob shapes only.
