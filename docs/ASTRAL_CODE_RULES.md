# ASTRAL Code Rules

Mandate for code quality and architecture. This document defines what we build and how. Not a progress report; not a README.

---

## 1. Coding Standards

### 1.1 Scope and Isolation

**Statute:** `astral.standards.in-scope-only`
**Statute:** `astral.standards.database-header-inventory`
**Statute:** `astral.standards.no-cross-contamination`

- **In-scope only:** If it is not explicitly mentioned in this document or in a module's header, it is not in scope. Do not touch it.
- **Database tables:** The data layer may use only the tables listed in the header inventory of `src/data/database.py`. Adding or changing table usage requires a design decision and an update to that header.
- **No cross-contamination:** Do not reference, import from, or depend on any code or data outside the layered structure defined below.

### 1.2 Imports

**Narrative (not a statute):** see `docs/statutes/HARVEST.md` § Narrative leftovers — `code-rules-1.2-imports-pointer`

- All code lives in the layered structure: `src/core/`, `src/data/`, `src/external/`, `src/utils/`, and `src/ui/`.
- Import only as allowed in section 3.3. Never import from outside this structure.

### 1.3 DRY and Function Organization

**Statute:** `astral.standards.dry-and-focused-functions`
**Statute:** `astral.standards.public-then-helpers`

- **DRY:** Before adding code, consider the whole file and honor Don't Repeat Yourself. Extract shared logic.
- **Function size:** Keep functions focused. Extract complex logic into helpers.
- **In-file organization:** Public functions first, then helpers. Do not scatter public and helper functions throughout the file. Group by responsibility with clear section comments.

### 1.4 No Hardcoded Sets or Magic Numbers

**Statute:** `astral.standards.no-hardcoded-sets`

- State lists, enums, and allowed value sets live in `src/utils/config.py`. Use config as the single source of truth. Validate against config; do not define inline.
- Magic numbers: use named constants from config or module-level constants. Document meaning and units where not obvious.

### 1.5 Logging and Error Handling

**Statute:** `astral.standards.logging-via-utils`
**Statute:** `astral.standards.data-raises-caller-logs`
**Statute:** `astral.standards.utils-data-late-import-only`

- Use `src/utils/logging.py` (backend debug contract: **§1.5.1**).
- **`logging.py` and the data layer:** `_DatabaseLogHandler` writes to `app_log` via **`add_log_entry` imported inside `_flush_buffer` only** (late import — keeps `utils` from importing `data` at module load time; avoids cycles). This is the **only** approved runtime `utils → data` path. If buffering or DB write fails, the handler prints a single diagnostic line to **stderr** (must not raise into the caller). See **AST-388**.
- Data layer: raise exceptions; do not log. Let caller decide.
- Core: raise domain exceptions. The dispatcher (`dispatcher.py`) catches and logs at the batch level.
- UI API: return JSON error responses.

#### 1.5.1 Backend debug logging (AST-538 / AST-554)

**Statute:** `astral.standards.debug-contract-gated`

- **Trigger:** Backend functions accept `debug: bool` (default `False`) and pass it through the call chain (including Agent Ad Hoc backend runs). Emit contract lines **only** when `debug=True` via `get_logger(..., debug_flag=debug)` and/or `logger.set_debug_flag(debug)` before calling `debug_index` / `debug_detail` / `debug_detail_block`. **No** new debug-contract lines when `debug=False`.
- **UI/React:** No debug-logging requirement (backend only).
- **Helpers:** Use `_PrefixedLogger.debug_index`, `debug_detail`, `debug_detail_block` from `src/utils/logging.py`; use `truncate_debug_content` for long blobs before emission.
- **Per-index header (style D):** One scannable header per batch item: `format_debug_index_header` shape — function context, universal `index N/M`, primary identifier, ` -> ` outcome. **Not** domain-specific counters in the format string (e.g. avoid `term 3/95`; use `index 3/95`).
- **Working detail:** Substantive trace lines use prefix ` | ` (`DEBUG_DETAIL_PREFIX`) under the current index header.
- **Long content:** Strings longer than **50 lines** → first **15**, line `<n lines omitted>` with **exact** `n = total_lines - 30`, then last **15** (implemented by `truncate_debug_content`).
- **Batch end:** Aggregate `summary={...}` at batch end is allowed but **must not** replace per-index headers + detail for debug runs.
- **Anti-patterns:** New `logger.info("[DEBUG] …")` in files touched for this epic; debug-contract emission without `debug=True`; logging full prompts/responses without truncation; debug noise in `src/data/` (still no log).
- **Grandfather:** Existing `logger.info("[DEBUG] …")` in files **not** otherwise edited for AST-538 work may remain until that file is touched.
- **Coexistence (not debug-gated):** `run_next hop: …` hop boundaries (AST-527/530); `log_llm_batch_summary` when `log_batch_id` is set; normal INFO/WARNING/ERROR for production paths.

---

## 2. Established Patterns

### 2.1 Config as Source of Truth

**Statute:** `astral.config.config-source-of-truth`
**Statute:** `astral.config.secrets-and-env-specific-from-environ`

All behavior-driving values live in `src/utils/config.py`. Config is thoughtfully organized by concern—not a single bag of unrelated keys.

**Config blocks:**

**Narrative (not a statute):** see `docs/statutes/HARVEST.md` § Narrative leftovers — `code-rules-2.1-config-block-catalog`

- **TASK_CONFIG**: Task definitions (prompts, response_format, context_format, response_schema). For graded tasks, also `grading_mode`, `vectors`, scoring keys (`grades_key`), and **job-consult orchestration**: pass/fail/error states, `save_prefix`, `pass_threshold`, readiness keys (`min_job_title_length`, `min_jd_chars`, `not_ready_state`), `requires_company`, and `fallback_batch_size` as the config default (`dispatch_tasks.batch_size` overrides at runtime). Single source for Anthropic task specs plus those orchestration literals.
- **GAZER_CONFIG**: Orchestration for gazer-batch steps (`validate_title`, `scrape_jd`, `gaze`): states, JD scrape `error_states`, and fallback batch sizes. `ROSTER_CONFIG["gaze"]["error_state"]` remains the gaze hook used by roster code until gazer reads this block (`gaze.error_state` must stay the same string).
- **JOB_STATES**: Job state registry. Each entry has `prior_states` (list of valid predecessor states, or `None` for unrestricted entry) and optionally `retry_state` (name of the holding state for per-job validation failures on the first attempt). Absence of `retry_state` means validation failures go directly to `error_state` with no retry.
- **TRACKER_CONFIG**: Job ingest config and JD processing rules. `job_state_transitions` has been removed — transitions are now validated using `prior_states` in `JOB_STATES`.
- **`dispatch_tasks` DB table**: Sole source of truth for dispatchable batch tasks. Each row carries `entity_type`, `trigger_state`, `sort_by`, `batch_call_mode`, `batch_size`, and scheduling config. Unique constraint: **`(candidate_id, task_key, trigger_state)`** — multiple rows may share a `trigger_state` when `task_key` differs (e.g. TO_WATCH trio: `find_job_page`, `select_job_page`, `parse_job_list`). **Company roster dispatch:** `trigger_state` selects companies; **`task_key` on the row** selects the roster entry (`find_job_page` vs `select_job_page` vs `parse_job_list`), not a hardcoded default. `DISPATCH_TASKS` config block has been removed.
- **COMPANY_STATES**: Company state list and batch criteria per state (limit, sort_by, scan_interval_hours).
- **CANDIDATE_STATES**: Candidate state list (`NEW` → `PROFILE_READY` → `CONTEXT_READY` → `LIVE_PROMPTS`, plus `DELETED`).
- **ROSTER_CONFIG**: Roster flows (prefilter, locate_job_page, parse_job_list), ats_vendor_patterns.
- **AGENT_CONFIG**: Anthropic model catalog — model_code (alias), model_label, cpm_input, cpm_output, cpm_cache_write, cpm_cache_read, default_temperature, default_max_tokens, cache_min_tokens. Keyed by model_code alias for O(1) lookup. Use `get_model(model_code)` helper.
- **ASTRAL_CONFIG**: Paths, company_state_transitions, gazer, tick_rate_minutes, max_auto_threads, dispatch_timeout_seconds, db_retry, html_cull, cookie_dismiss_selectors, support_email (alert recipient for monitor.py), etc.
- **RAILWAY_CONFIG**: Gunicorn deployment settings (workers, timeout, playwright_browsers_path). Read by `scripts/start_server.py` to build the gunicorn command. Single worker required — the in-process scheduler thread runs per-worker.
- **BLOCK_TYPES**: Content block type enum for the `agent_data` table: SYSTEM, CACHE_A-D, NO_CACHE, TASK, RESPONSE. Used by `agent.py` for storage and validation.
- **ENTITY_TYPES**: Valid entity type strings (candidate, company, job). Single source of truth used across `agent_data`, `dispatch_ledger`, `agent_responses`, and config.
- **DISPATCH_TASKS**: Removed. See `dispatch_tasks` DB table above.
- **NAV_CONFIG**: UI navigation structure — sidebar groups, labels, and route paths. Groups may declare `visible` and items may declare `enabled` as candidate state strings or `False` (permanently disabled). The `/api/nav_config` endpoint in `system.py` resolves these against the selected candidate's state before serving. The frontend renders the resolved structure with no additional visibility logic.

#### pass_threshold vs dispatch_task.score_floor

**Statute:** `astral.config.pass-threshold-vs-score-floor`

- **`pass_threshold`** (on **TASK_CONFIG** for scored consult tasks): used by **`render_verdict`** / scoring to decide **pass vs fail** from model output after a run. Do **not** feed **`dispatch_task.score_floor`** into this path.
- **`score_floor`** (on **`dispatch_task`** rows): read only from the DB row for **dispatch eligibility** — batch claim/count (`claim_job_batch`, `count_eligible_for_dispatch_task`, dispatcher orchestration): jobs must satisfy **`latest_score >= score_floor`** before a scored step runs (with existing **`NULL` → 1.0** normalization where applicable).
- **Precedence:** Different lifecycle stages — neither replaces the other. If **`score_floor`** is **`NULL`** for a scored task row, **`1.0`** applies to **dispatch gating**, not **`pass_threshold`** grading math.

Environment variables for secrets (listed at top of `config.py`). Paths, limits, and state machines from config.

**The rule is binary and strict:**
- **Secrets** (API keys, tokens, credentials) → environment variables. Read with `os.environ["KEY"]` — no `.get()`, no fallback. If the var is missing, crash at startup. Never put secrets in config.py.
- **Environment-specific values** (paths, URLs, addresses that differ between local and production) → environment variables. Same rule: `os.environ["KEY"]`, no fallback, crash if missing.
- **Everything else** (limits, state lists, behavior flags, default values that are the same everywhere) → plain literals in config.py. No `os.environ` lookups at all. If a value belongs in config, it lives there as a literal — not split across config and environment.

### 2.2 Core → External: Config + Delegation

**Statute:** `astral.agent.do-task-delegation`

All config blocks live in `src/utils/config.py`, which means any layer that imports utils has access to config values. Core reads config freely for business logic decisions (e.g., grading_mode, vectors, pass_threshold, state transitions). However, core must use external layer functions for technical execution (API calls, page navigation, scraping). Config informs decisions; external performs I/O.

**Core → Agent → Anthropic: do_task pattern.** Core calls `do_task` (from `src/core/agent.py`), which resolves prompts, assembles blocks, stores agent_data, and delegates the API call to `send_to_anthropic` (from `src/external/anthropic.py`). Core does not assemble task params for the AI call.

```python
result = await do_task(
    task_key="grade_get",
    live_content=visible_text,
    index=astral_job_id,
)
```

- **task_key**: From TASK_CONFIG (e.g. `grade_get`, `prefilter_company`).
- **live_content**: Dynamic content for the prompt.
- **index**: Context identifier. Context string from task's `context_format`.

Check `result.get("success")`. On success use `parsed_response`; on failure use `error` and `raw_response`. Core decides how to proceed.

### 2.3 Task Response Schema and Grade Validation

For JSON tasks, TASK_CONFIG defines `response_schema`. Anthropic validates; on failure returns error result (does not raise). Core receives validated shape or error and decides. Grade **confidence** bounds are also enforced in core after schema pass (defense in depth; see §2.3.2).

#### 2.3.1 Grades

**Statute:** `astral.agent.grade-vector-validation`
When a TASK_CONFIG task defines `vectors`, `do_task` performs an additional grade-level validation after schema validation passes: all expected vector names must be present, no unexpected vectors, and all grade values must be in `{A, B, C, D, F, X}`. This catches AI creativity (e.g., "A+" or missing vectors) before it reaches core.

#### 2.3.2 Confidence

**Statute:** `astral.agent.confidence-bounds`
Every graded row carries integer `confidence`: `1`–`5` for letter grades `A`–`F`, and `0` with `X`. Multipliers live in `CONFIDENCE_MULTIPLIERS` in `config.py` and apply to scored consult math. At the scoring boundary, confidence `1` (including `F1`) is treated as no signal (effective `X`); `F` with confidence `2`–`5` remains a dealbreaker. Binary consult steps (`qualify_job_listings`, `evaluate_jd`) fail on `F2+`, all literal `X`, or when no row has confidence `> 1`.

### 2.4 Batch Processing Pattern

**Statute:** `astral.batch.claim-process-release`
**Statute:** `astral.batch.batch-id-format`
**Statute:** `astral.batch.batch-id-first`

All batch jobs that process entities by state use batch locking. The `batch_id` is the **golden ticket** — one ID per dispatch run that ties together row-locking, state transitions, agent_data blocks, entity agent_responses, dispatch_ledger entries, and timesheets.

**batch_id format:** `f"{task_key}-{uuid}"` — prefixed with the task_key for human readability in foreign-key references (e.g. `prefilter-3f8a2b1c-...`). For non-dispatch calls (e.g. artifact generation), the prefix is the function context.

**Pattern: claim → process → release**

1. **Claim:** Dispatcher generates `batch_id`, writes ledger entry, sets `log_batch_id` context var, then passes `batch_id` to the claim function to lock N unclaimed rows.
2. **Process:** Select by batch_id, process each (AI calls store agent_data + entity agent_responses via the batch_id), update state.
3. **Release:** Clear `batch_id` column on entity rows when done. The row lock is temporary; the data trail (agent_data, timesheets, ledger) is permanent.

**Data layer:** `claim_<entity>_batch(batch_id, state, limit, ...)`, `get_<entity>_batch(batch_id)`, `clear_<entity>_batch(batch_id)`. Parameter order: **batch_id first**.

**Core:** `get_new_<entity>_batch(state, limit?, batch_id?)` — resolve criteria from config, use provided batch_id or generate one, claim, get, return `(batch_id, entities)`.

**Dispatcher flow:**

**Narrative (not a statute):** see `docs/statutes/HARVEST.md` § Narrative leftovers — `code-rules-2.4-dispatcher-pseudocode`

```
batch_id = f"{task_key}-{uuid4()}"
save_dispatch_ledger(batch_id, ...)
log_batch_id.set(batch_id)
(bid, entities) = core.get_new_company_batch(state, batch_id=batch_id)
try:
    for entity in entities:
        process(entity)  # do_task uses log_batch_id for agent_data storage
finally:
    database.clear_company_batch(batch_id)
```

Do not select by state and process without batch_id. Use claim / get / clear and batch_id-first order consistently for all entity types.

### 2.4.1 Entity Agent Responses

**Statute:** `astral.batch.entity-agent-responses-latest-only`

Every entity table (company, job, candidate) has an `agent_responses` JSON array column. After each successful `do_task` call, `agent.py` upserts a lightweight reference entry by `task_key` (latest wins):

```json
{
  "batch_id": "prefilter-3f8a2b1c-...",
  "task_key": "prefilter",
  "created_at": "2026-03-19 14:32:00",
  "entity_cost": 0.0042,
  "prompt_blocks": [
    {"type": "SYSTEM", "id": "<agent_data_id>"},
    {"type": "RESPONSE", "id": "<agent_data_id>"}
  ]
}
```

Historical blocks remain in `agent_data`; only the entity-row ref array is latest-only per phase.

The `prompt_blocks` array contains foreign keys into the `agent_data` table. The entity row stays lightweight; full content is retrieved via `GET /api/agent_data/<batch_id>` using the block IDs.

### 2.5 Bright Line: Core vs External

**Statute:** `astral.layers.core-vs-external-bright-line`

**External layer** owns all I/O: page navigation, DOM extraction, HTTP, API calls. It performs operations and returns data.

**Core layer** orchestrates: it imports and calls data, external, and utils. External executes the I/O; core contains the business logic.

### 2.6 State Machine

**Statute:** `astral.state.no-daisy-chain-in-run`
**Statute:** `astral.state.core-decides-transitions`

Every company and every job has a `state`. Entities are processed in batches based on their current state (see 2.4). There is no daisy-chaining — a job does not automatically flow from one state to the next within a single run. Each dispatch cycle claims a batch of entities in a specific state, processes them, and transitions each entity to a new state. The next dispatch cycle picks them up from there in a separate invocation.

#### 2.6.0 Dispatch run_next chains (AST-848)

**Narrative (not a statute):** see `docs/statutes/HARVEST.md` § Narrative leftovers — `code-rules-2.6.0-run-next-carveout-detail`

Within a **single** `do_task` invocation, when `ctx` carries `dispatch_trigger_state`, successful hops may write runtime DB labels `{trigger}.{task_key}` and recurse via `run_next` until the terminal hop. Terminal graduation to a registered `JOB_STATES` key happens in the same invocation when `dispatch_chain_graduate_on_terminal` is true and the last hop's `run_next` is empty. Runtime hop labels are **not** `JOB_STATES` registry keys; batch claim may accept them (see `is_valid_job_batch_claim_state` in `config.py`). This carve-out does **not** apply to roster/consult score transitions (`render_verdict`) or company batches.

State transitions are config-driven and managed by the core layer only. The data layer (`database.py`) and its core wrappers (`tracker.py`, `roster.py`) accept the target state as a parameter from the caller and perform the database update — they do not decide what the next state should be.

#### 2.6.1 Companies

**Narrative (not a statute):** see `docs/statutes/HARVEST.md` § Narrative leftovers — `code-rules-2.6.1-3-entity-examples`

Company states are defined in `COMPANY_STATES` and transitions in `ASTRAL_CONFIG["company_state_transitions"]`. Roster functions (e.g., `prefilter_company`, `find_job_page`) determine the outcome and pass the target state to the data layer.

Example: a company in `NEW` is claimed by the prefilter dispatch task. Core evaluates it and transitions it to `WATCH` or `IGNORE`.

#### 2.6.2 Jobs

**Statute:** `astral.state.job-prior-states-enforced`

Job states are defined in `JOB_STATES`. Each state carries `prior_states` (a list of valid predecessor states, or `None` for unrestricted entry). `tracker.transition_job_state` enforces these — it raises `ValueError` if the job's current state is not in `prior_states`. States with a `retry_state` key support per-job retry routing: when `_run_batch_consult` finds missing or invalid jobs, it transitions them to `retry_state` (rather than the error state) for a dedicated second-attempt dispatch batch. Core functions determine the outcome and call `tracker.transition_job_state` with the target state.

Example: a job in `PASSED_JD` is claimed by the **`grade_do`** dispatch task. `render_verdict` grades it and transitions it to `PASSED_DO`, `FAILED_DO`, or `FAILED_TECHNICAL_DO`.

#### 2.6.3 Candidates

Candidate states are defined in `CANDIDATE_STATES` and transitions in `ASTRAL_CONFIG["candidate_state_transitions"]`. States follow a simple progression:

`NEW` → `PROFILE_READY` → `CONTEXT_READY` → `LIVE_PROMPTS` (plus `DELETED` for logical deletes)

`CONTEXT_READY` is gated by `check_context_complete` — all four context lists (strengths, priorities, deal_breakers, backstory) must have at least one item. Core functions (`initiate_candidate`, `transition_candidate_state`) determine the outcome and pass the target state to the data layer. Example: a candidate in `NEW` saves their profile; core parses the resume via `parse_candidate_resume` and transitions to `PROFILE_READY`.

### 2.7 render_verdict Pattern

**Statute:** `astral.patterns.render-verdict-orchestrates-consult`

`render_verdict(task_type, astral_job_id)` is the standard orchestrator for per-job consult tasks in `src/core/consult.py`. It handles the full lifecycle for one job through one agent task:

1. Resolve orchestration via **`TASK_CONFIG[task_type]`** — dispatch `task_key` and catalog key are the same string for graded consult steps (`grade_do`, `grade_get`, `grade_like`).
2. Fetch job (and company if `requires_company`) from the data layer.
3. Prep live_content via `_prep_live_content` (coat-check pattern for JD and website content).
4. Call `do_task` with the `agent_task` key.
5. Audit the full AI response to the database.
6. Score: `_render_pass_fail` (binary) or `_render_score` (per-vector numeric, 0-10 scale).
7. Save grades and score to job_data via tracker (keyed by `save_prefix`).
8. Transition state via tracker.
9. Return `{"success", "to_state", "score", "grades"}` for dispatcher logging.

**Narrative (not a statute):** see `docs/statutes/HARVEST.md` § Narrative leftovers — `code-rules-2.7-encoded-consult-detail`

For encoded consult agent tasks (`grade_do` / `grade_get` / `grade_like`, `output_type` `grades_encoded_notes`), `render_verdict` passes `batch_entities` and `vector_labels` into `do_task`, flattens decoded `jobs[]`, hydrates `grades[].reason` from the candidate rubric, and may persist `{save_prefix}_notes` when the wire line includes an optional notes tail. See `docs/features/consult/ast-351-convert-consult-to-use-encoded-responses.md`.

Technical failures (job not found, content prep failed, API error, schema validation failed) transition to the `error_state` from config, creating per-step retryable batches. The dispatcher never calls tracker directly — it just loops, calls `render_verdict`, and logs.

### 2.8 Coat-Check Pattern

**Statute:** `astral.patterns.coat-check-never-store-empty`

Some data fields need to be lazily populated — the value may or may not exist in the database when a caller first asks for it. The **coat-check pattern** handles this transparently: the caller asks for a value by key, and the handler either returns the cached value or fetches it on-demand, saves it, and returns it. The caller never knows which path was taken.

**How it works:**

1. Caller requests `get_company_data(company, key)` or `tracker.get_job_data(job, key)`.
2. If the value exists in the entity's data dict, return it immediately.
3. If the key is registered as a coat-check key (in `ROSTER_CONFIG["company_data_keys"]` or `TRACKER_CONFIG["job_data_keys"]`), dispatch to the appropriate fetch handler.
4. The handler fetches the data (via playwright, AI, or other means), saves it to the entity's data dict via the data layer, and returns it.
5. On failure, the handler returns `None` and does **not** store empty or failed data — this ensures the coat-check re-triggers on the next attempt after the underlying issue is resolved.

**Current coat-check keys:**

**Narrative (not a statute):** see `docs/statutes/HARVEST.md` § Narrative leftovers — `code-rules-2.8-coat-check-key-table`

| Key | Entity | Handler | Fetch method |
|-----|--------|---------|-------------|
| `nav_links` | company | `roster._fetch_nav_links` | Playwright: scrape homepage link list |
| `prefilter_company_notes` | company | `roster._fetch_prefilter_notes` | AI: run prefilter task, save notes only (no state change) |
| `website_content` | company | `roster._fetch_website_content` | AI: select culture pages + Playwright: scrape each |
| `job_description` | job | `tracker` | Playwright: scrape job posting page |

**Layer ownership:** `roster.get_company_data` handles company coat-checks, `tracker.get_job_data` handles job coat-checks. Both are core-layer functions that may call external (playwright, anthropic) and data (database) layers as needed.

**Key rule:** Never store empty or failed results. A `None` return signals the caller that the data is unavailable. The caller decides how to handle it (e.g., skip, retry, transition to an error state).

### 2.9 Authentication Decorator

**Statute:** `astral.patterns.require-auth-on-protected-endpoints`

UI API endpoints use `@require_auth` to enforce authentication. The decorator checks for an `Authorization: Bearer <token>` header, validates the token, and sets `g.user` with the authenticated user's identity. Endpoints without the decorator are open (e.g., health checks).

**Pattern:**

- `@require_auth` = protected. Returns 401 if no valid Bearer token.
- No decorator = open. No auth check.
- Authenticated user available via `flask.g.user` inside the endpoint function.

**Stub implementation:** Accepts any Bearer token and hardcodes a default user. To be replaced with Auth0 JWT validation. When Auth0 is wired in, only the decorator internals change — no endpoint code changes.

**React side:** All API calls go through a shared `api()` client (`src/ui/frontend/src/api.ts`) that injects the `Authorization` header on every request. The token source is a single constant today (stub); becomes the Auth0 JWT from login flow later.

---

## 3. Codebase Structure

### 3.1 Directory Layout

**Narrative (not a statute):** see `docs/statutes/HARVEST.md` § Narrative leftovers — `code-rules-3.1-directory-tree`

```
astral/
├── src/
│   ├── core/              # Business logic (domain layer)
│   │   ├── agent.py       # AI agent orchestration (do_task, prompt assembly, agent_data storage)
│   │   ├── dispatcher.py  # Batch runners, dispatch orchestration, in-process scheduler
│   │   ├── monitor.py     # Admin alerting and monitoring (auto_run_error, future escalation hooks)
│   │   ├── roster.py      # Company roster orchestration
│   │   ├── gazer.py       # Job board scanning
│   │   ├── consult.py     # Job analysis
│   │   ├── candidate.py   # Candidate lifecycle
│   │   └── tracker.py     # Job tracking/deduplication
│   ├── data/
│   │   └── database.py    # SQLite operations
│   ├── external/
│   │   ├── anthropic.py   # Claude API client
│   │   ├── gmail.py       # Gmail API email sender (send_email)
│   │   └── playwright.py  # Web scraping/automation
│   ├── utils/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── formatting.py
│   └── ui/                    # Web UI (Flask + React)
│       ├── server.py          # Flask app setup, blueprint registration, scheduler start
│       ├── auth.py            # require_auth decorator (imported by blueprint modules)
│       ├── api/               # Flask Blueprints (one module per domain)
│       │   ├── api_system.py      # /api/health, /api/me, /api/nav_config, /api/admin/scheduler
│       │   ├── api_candidate.py   # /api/candidates/*
│       │   ├── api_jobs.py        # /api/jobs/*
│       │   ├── api_companies.py   # /api/companies/*
│       │   └── api_admin.py       # /api/admin/* (agents, tasks, timesheets, dispatch, adhoc, data)
│       └── frontend/          # Vite + React + TypeScript
│           ├── src/
│           │   ├── App.tsx        # App entry point (BrowserRouter, providers)
│           │   ├── main.tsx       # React DOM mount
│           │   ├── routes.tsx     # React Router route definitions
│           │   ├── App.css        # Single stylesheet (all styles, organized with TOC)
│           │   ├── contexts/      # React context providers
│           │   │   └── CandidateContext.tsx
│           │   ├── lib/           # Shared non-component modules
│           │   │   ├── api.ts     # API client (auth header injection)
│           │   │   └── fmt.ts     # Date/time formatting
│           │   ├── components/    # Reusable UI components (flat)
│           │   │   ├── NavigationShell.tsx
│           │   │   ├── ListPage.tsx
│           │   │   ├── ContextPage.tsx
│           │   │   ├── DetailsEditPage.tsx
│           │   │   ├── FormFields.tsx
│           │   │   ├── Modal.tsx
│           │   │   ├── Toast.tsx
│           │   │   ├── Time.tsx           # Timezone-aware timestamp display
│           │   │   ├── TabbedTextArea.tsx  # Horizontal tab bar + textarea (reusable)
│           │   │   ├── SideTabPanel.tsx    # Vertical side tabs + textarea (fixed or editable)
│           │   │   └── TokenTextarea.tsx   # Textarea with {$TOKEN} autocomplete
│           │   ├── pages/         # Page components (flat, section-prefixed names)
│           │   │   ├── AdminScheduledActions.tsx
│           │   │   ├── JobsRecommended.tsx
│           │   │   ├── CompaniesWatchList.tsx
│           │   │   ├── ArtifactsBaseResumeContent.tsx
│           │   │   ├── CandidateProfile.tsx
│           │   │   └── ...          # No subdirectories
│           │   └── assets/        # Static assets (logo, images)
│           ├── dist/              # Build output (gitignored)
│           ├── package.json
│           ├── vite.config.ts
│           └── index.html
├── scripts/               # Build and deployment scripts
│   ├── build_railway.sh   # Build: pip install, playwright, frontend build
│   └── start_server.py    # Start: reads RAILWAY_CONFIG, exec's gunicorn
├── data/                  # Data files (agents, candidate, etc.)
└── docs/
    ├── ASTRAL_CODE_RULES.md
    ├── features/          # One folder per Linear project
    │   ├── <project>/
    │   │   ├── project_description.md   # Project overview for Linear
    │   │   └── <slug>.md                # Single file per feature (plan + notes + review)
    │   └── ...
    └── linear-imports/    # Linear CSV exports
```

### 3.2 Layer Rules

**Statute:** `astral.layers.ui-config-driven-business-logic`

**External (`src/external/`):** Integration with external services (Anthropic, Playwright, Gmail). No business logic, no data persistence. API keys and behavior from config or env. External functions return results or a success/failure status — they do not log; the calling core module decides what to log. HTTP request logging for `httpcore`, `httpx`, and `anthropic` is suppressed at WARNING level in `src/external/anthropic.py` at import time. **Timesheet rows:** `send_to_anthropic` accepts an optional `record_timesheet` callback; `src/core/agent.py` passes `src.core.timesheets.record_timesheet_entry` so token/cost rows are written immediately after each API response without `external` importing `data`. All other data-layer interactions (agent_data, agent_responses, prompt resolution) are handled by `src/core/agent.py`.

**Data (`src/data/`):** Database and file I/O only. No business logic, no external API calls, no UI. Exposes focused functions. Paths from config. **`agent_data.block_data` is zlib-compressed on write and decompressed on read — this is handled transparently by `save_agent_data` / `get_agent_data_by_batch`. Callers always receive plain text strings; the compression is invisible above the data layer.**

**Core (`src/core/`):** Domain logic and orchestration. Imports data, external, and utils. No direct file I/O — use data layer. Functions testable in isolation. The dispatcher (`dispatcher.py`) is a documented exception — it calls data-layer functions directly for batch orchestration alongside the thin wrappers it provides for API-layer compliance. `monitor.py` owns admin alerting logic — the dispatcher calls `monitor.auto_run_error()` after any AUTO task run that produces errors; monitor fetches the relevant logs from the data layer and delegates email delivery to `src/external/gmail.py`. Future monitoring features (log scanning, escalation, daily summaries) extend `monitor.py` without touching the dispatcher.

**UI (`src/ui/`):** Flask API server + React frontend. Receives HTTP requests, calls core, returns JSON or serves static files. Thin wrappers. Imports core and utils only — never external, never data. Authentication via `@require_auth` decorator (see 2.9). API routes are organized using Flask Blueprints in `src/ui/api/`, one module per domain. `src/ui/server.py` handles app setup, blueprint registration, and scheduler startup.

**UI business logic lives in the API layer, driven by config.** When the frontend needs conditional behavior — visibility, enablement, filtering, response shaping based on entity state — that logic is config-driven (declared in `src/utils/config.py`) and resolved in `src/ui/api/` endpoints before serving. The frontend renders the resolved response without duplicating the logic. Hardcoded visibility sets, state comparisons, or business rules in React components violate this principle.

**Utils (`src/utils/`):** Shared utilities. Pure; no imports from core, data, external.

**Dispatch pipeline (happy path):** All batch runners live in `src/core/dispatcher.py`. The scheduler runs them automatically per the `dispatch_task` configuration. PW = Playwright, AI = Anthropic, DB = Database. `/` = PW used conditionally (coat-check: called only when data doesn't already exist).

| Task | PW | AI | DB |
|------|----|----|-----|

**Narrative (not a statute):** see `docs/statutes/HARVEST.md` § Narrative leftovers — `code-rules-3.2-dispatch-pipeline-table`

| prefilter | X | X | X |
| locate_job_page | X | X | X |
| parse_job_list | X | X | X |
| gaze | X | | X |
| qualify_job_listings | | X | X |
| scrape_jd | X | | X |
| evaluate_jd | | X | X |
| grade_do | | X | X |
| grade_get | | X | X |
| grade_like | / | X | X |

### 3.3 Import Rules

**Statute:** `astral.layers.import-direction`
**Statute:** `astral.layers.scripts-exempt-from-layer-rules`

**Rule 1 — Allowed imports by layer:**

| Layer | May import |
|-------|------------|
| ui | core, utils only |
| core | data, external, utils |
| external | utils only |
| data | utils only |
| utils | nothing (pure) — *exception:* `logging.py` DB sink, see §1.5 |

**Rule 2 — Diagram:**

```
ui       ──► core, utils
core     ──► data, external, utils
data     ──► utils
external ──► utils
utils    ──► (nothing)
```

**Rule 3 — One-line per layer:**
- **ui:** core + utils. Never external. Never data.
- **core:** data + external + utils. Never ui.
- **external:** utils only. Never core, data, ui.
- **data:** utils only. Never core, external, ui.
- **utils:** nothing outside utils (intra-utils imports are allowed — e.g. `cost_calculator` importing from `config`). **Exception:** `src/utils/logging.py` may late-import `src.data.database` inside the DB log handler flush path only (§1.5 / AST-388); do not copy this pattern elsewhere in utils.
- **scripts:** Exempt from layer rules. Scripts are never runtime concerns — they may import from any layer (data, external, core, utils) as needed for one-off operations, builds, and deployment.

### 3.4 Playwright and HTML Culling

**Narrative (not a statute):** see `docs/statutes/HARVEST.md` § Narrative leftovers — `code-rules-3.4-html-cull-config`

`src/external/playwright.py` provides navigation, DOM extraction, cookie dismissal, vendor detection. Core invokes playwright, obtains content, and processes it.

HTML culling is configured in `ASTRAL_CONFIG["html_cull"]`: `allowed_tags`, `banner_patterns`, `strip_attributes`, `strip_on_attrs`. ATS vendor patterns in `ROSTER_CONFIG["ats_vendor_patterns"]`.

### 3.5 UI Stack and Deployment

**Statute:** `astral.ui.frontend-file-placement`
**Statute:** `astral.ui.naming-conventions`
**Statute:** `astral.ui.single-gunicorn-worker`

**Stack:** React + TypeScript (Vite) frontend, served as static files from Flask. Single Flask process handles both API routes (`/api/`) and the built React app.

**Dev workflow:** Two processes running in parallel:

**Narrative (not a statute):** see `docs/statutes/HARVEST.md` § Narrative leftovers — `code-rules-3.5-dev-workflow-ports`
- Flask API server: `cd src/ui && python server.py` (port 5001)
- Vite dev server: `cd src/ui/frontend && npm run dev` (port 5173)

Vite proxies `/api/` requests to Flask during development (configured in `vite.config.ts`). In production, Flask serves the built React output directly from `src/ui/frontend/dist/`.

**Client-side routing:** Flask catch-all route serves `index.html` for any non-API, non-file path. React Router handles all navigation client-side.

**Deployment:** Single Railway service. Flask + React + SQLite on one persistent volume. Single gunicorn worker (required — the scheduler thread runs per-worker).

- `railway.toml`: configures nixpacks builder, build command (`scripts/build_railway.sh`), start command (`scripts/start_server.py`)
- `scripts/build_railway.sh`: installs Python deps, Playwright browsers, builds React frontend
- `scripts/start_server.py`: reads `RAILWAY_CONFIG` from `config.py`, sets environment (e.g. `PLAYWRIGHT_BROWSERS_PATH`), exec's gunicorn
- `nixpacks.toml`: declares providers (python, node) for the nixpacks builder
- SQLite path points to Railway's persistent volume mount (survives redeploys)

**In-process dispatch scheduler:**

**Narrative (not a statute):** see `docs/statutes/HARVEST.md` § Narrative leftovers — `code-rules-3.5-scheduler-endpoint-list`

The dispatcher (`src/core/dispatcher.py`) runs as per-task daemon threads inside the web server. No external cron service. All batch runner logic and dispatch orchestration live in `dispatcher.py`.

- `start_scheduler()` is called at server startup in `src/ui/server.py`. It spawns a lightweight tick daemon thread that wakes every `tick_rate_minutes` (from `ASTRAL_CONFIG`) to check which `auto_mode=1` tasks are due.
- Each dispatch task gets its own daemon thread with its own asyncio event loop. AUTO tasks are spawned by the tick thread up to `max_auto_threads` concurrent threads (FIFO when at cap). CLICK tasks are spawned on demand via the admin UI.
- Each task thread runs the batch runner loop for that task, records a single consolidated ledger entry, and cleans itself from the registry on exit.
- Per-task timeout is `dispatch_timeout_seconds` (from `ASTRAL_CONFIG`, default 1200s). Stuck tasks are killed via `asyncio.CancelledError` and logged as INTERRUPTED.
- The Admin > Task Dispatcher screen provides per-row controls: AUTO mode toggle, Run button (CLICK mode), Stop button (kill active thread), and a Stop All button with confirmation modal listing active threads.
- Scheduler and task control is exposed via endpoints in `api_admin.py`: `POST /api/admin/dispatch_tasks/<id>/run`, `POST /api/admin/dispatch_tasks/<id>/stop`, `POST /api/admin/scheduler/stop_all`, `GET /api/admin/scheduler/thread_status`.
- Batch locking (section 2.4) guarantees safety — the state machine and claim/process/release pattern handle concurrency without conflicts.

**Naming convention:**
- React component files: PascalCase (`ManageCandidates.tsx`, `ListPage.tsx`)
- Route paths: snake_case (`/admin/manage_candidates`, `/candidate/base_resume`)
- API endpoints: snake_case (`/api/candidates`, `/api/health`)
- Python code: snake_case (unchanged)

**Frontend file placement:**

| File type | Location | Rule |
|-----------|----------|------|
| Entry points | `src/` root | `App.tsx`, `main.tsx`, `routes.tsx` only |
| React contexts | `src/contexts/` | One file per context provider |
| Shared modules | `src/lib/` | API client, future hooks, utilities |
| Reusable components | `src/components/` | Flat directory — no subdirectories |
| Page components | `src/pages/` | Flat directory — section-prefixed names (e.g. `AdminScheduledActions.tsx`, `JobsRecommended.tsx`) |
| Static assets | `src/assets/` | Logo, images |
| Styles | `src/App.css` | Single file, organized by numbered section with a TOC comment at the top |

### 3.6 Local debug and spike output (R&D)

**Statute:** `astral.debug.spikes-under-debug-dir`
**Statute:** `astral.debug.no-repo-root-artifacts-dir`

**`debug/`** at the repository root holds **worktree-local** material that must **never** be committed: Playwright dumps, spike JSON, screenshots, ad-hoc review scorecards, and other scratch output.

**Spikes are R&D.** Spike deliverables do **not** belong in **`docs/features/`** (no run notes, no `a16z-*.md`, no spike schemas, no spike handoff markdown in the repo). Record spike findings on the **Linear issue** (description updates, comments) and attach files there.

| Kind of output | Where it goes | Committed? |
|----------------|---------------|------------|
| Spike captures, inventories, draft JSON, run notes | **`debug/spikes/<issue-id>/…`** (e.g. `debug/spikes/AST-414/`) | **No** — `debug/` is gitignored |
| Same spike files for Susan / team review | **Linear issue attachments** on the spike ticket | **No** — not in git |
| Local code-review rubric notes | `debug/` (e.g. `debug/code_review_notes.md`) | No |
| **Production** feature plans (build tickets) | `docs/features/<project>/*.md` | Yes (on `ftr/<ticket-id>`) |
| Spike helper scripts (runnable CLIs) | `scripts/spikes/` | Yes — scripts only, not their output |
| Product code and tests | `src/`, `tests/` | Yes |

**Spike path rule:** one directory per **Linear issue id** (`AST-NNN`), not per board nickname. Subfolders (`phase1/`, `phase2/`, …) are optional inside that issue folder.

**Do not** create a top-level **`artifacts/`** directory. That name is reserved for the **Astral Artifacts** program and **`docs/features/artifacts/`** (production markdown plans only). Spike scripts must default **`--out`** / **`--out-dir`** to **`debug/spikes/<issue-id>/…`**, not `artifacts/…` or `docs/…`.

### 3.7 Sunset — Astral Boards (AST-757)

**Narrative (not a statute):** see `docs/statutes/HARVEST.md` § Narrative leftovers — `code-rules-3.7-boards-sunset`

The **Astral Boards** channel is **removed** from production. Roster cultivation via Google CSE and company/job dispatch replaced the boards ingest + gaze workflow. Epic siblings **AST-765** (product removal) and **AST-766** (schema drop) deleted board modules, API routes, tables, and board-only tests; **AST-767** retires active test-bible manifests.

| Label | SHA | Notes |
|-------|-----|-------|
| Pre-removal `dev` tip at dispatch | `8d9b01e5e75ace9c04c32711488430503075e0c3` | Last boards-capable tree before AST-757 removal |
| First removal commit | `e8fe8143f7b0b73a703238af1c31a39252b65992` | `code(AST-765): delete boards modules and unregister API` — equivalent `f64c3c0` on AST-765 republish line |

**Revival hints:**

- `git diff 8d9b01e5..e8fe814` — start of product removal
- `git show 8d9b01e5:<path>` — last known contents of removed board files (e.g. `src/core/boards.py`, `src/ui/api/api_boards.py`)

**Archive pointers:**

- Design history: **`docs/features/boards/`**
- No active component-test obligations for boards — see monolith **`docs/ASTRAL_TEST_BIBLE.md`** §7.13 boards (sunset) and decomposed **`docs/test-bible/**`** sunset stubs

---

## 4. Branching and Project Management

### 4.1 Branching Strategy

**Narrative (not a statute):** see `docs/statutes/HARVEST.md` § Narrative leftovers — `code-rules-4.1-stale-branching`

> **Stale:** The branching instructions in this section are superseded by `docs/ASTRAL_GIT_WORKFLOW.md` and the `orch.git.*` statutes (`orch.git.three-permanent-branches`, `orch.git.flow-direction-inviolable`, `orch.git.ftr-sub-topology`, `orch.git.commit-vocabulary`, `orch.git.merge-on-checkout`, `orch.git.no-cherry-pick-rebase-force`, `orch.git.no-dev-agent-branches`). Keep the prose below as historical narrative only.

All day-to-day work happens on a single `dev` branch. Per-project feature branches are retired — no more `roster`, `gazer`, `tracker`, etc. The only exception is `artifacts`, which will get its own long-lived branch when that project begins.

**Workflow:**

1. Check out `dev`: `git checkout dev`
2. Rebase with main: `git fetch origin && git rebase origin/main`
3. Implement the ticket. Commit messages use the Linear-generated slug as the subject: `feat(ast-326-batch-scrape-jds): add dedicated scrape_jd task`
4. When `dev` reaches a stable, tested milestone, merge to main via PR
5. Continue working on `dev` for the next set of tickets

**Linear-generated slugs:** Linear auto-generates per-ticket branch names of the form `<agent>/ast-NNN-slug` (e.g., `<agent>/ast-326-batch-scrape-jds`), where **`<agent>`** is the assignee’s **Linear username** (first segment of **`gitBranchName`** for that user’s MCP). These are **not used as actual git branches** — we work on `dev` only. The Linear-generated slug is used as:
- The commit message subject (ticket ID + slug)
- The plan and review filename prefix in `docs/features/<project>/` (e.g., `ast-326-batch-scrape-jds-plan.md`)

This keeps Linear ticket traceability in the git log and documentation without fragmenting the branch history.

### 4.2 Documentation

**Statute:** `astral.docs.features-single-file-per-ticket`

Each project's documentation lives in `docs/features/<project>/`:
- `project_description.md` — project overview (synced to Linear project description)
- `<slug>.md` — single file per feature: plan, implementation notes, and review findings combined

Documentation is **not** stored in `.cursor/plans/`. The `docs/features/` directory is the single source for project documentation.

### 4.3 Linear Workflow States

**Narrative (not a statute):** see `docs/statutes/HARVEST.md` § Narrative leftovers — `code-rules-4.3-state-name-list`

Feature-level PRs. Sub-issues track implementation; parent features track PR lifecycle.

**States (Team Chuckles pipeline names):** Backlog → Discussion → Todo → In Progress → Plan Ready → Plan Discuss → Plan Approved → Code Complete → Tests Ready → Tests Passed → Review Posted → User Testing → PR Ready → Done (plus Canceled/Cancelled, Archive, Duplicate as terminal taxonomy). Name-only — never Linear state ids.

**Blocked** is a label, not a state. Use when stuck on clarification, dependency, or external blocker.

**Done** = merged to main, not merely "code works."
