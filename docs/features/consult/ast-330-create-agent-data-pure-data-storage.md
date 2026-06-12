<!-- linear-archive: AST-330 archived 2026-06-03 -->

## Linear archive (AST-330)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-330/create-agent-data-as-pure-data-storage  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

agent_data table fields:
agent_data_id, entity_type, task_key, batch_id, created_at, block_type, block_data

This table will contain all of the data content passed to and received from anthropic.  

dispatch_ledger fields (add as needed)
batch_id, entity_type, task_key, batch_size, agent_success, agent_note, total_cost, prompt_blocks \[{type:<block_type>, data:<agent_data_id>}\]

Block_type is an enum of

* SYSTEM
* CACHE_A
* CACHE_B
* CACHE_C
* CACHE_D
* NO_CACHE
* TASK

Entity_cost and Total_cost should be calculated after the timesheets are entered for the batch at run time.


This will NOT replace agent_responses, but instead provide multiple foreign keys for the agent_responses content (prompt content becomes id references to agent_data). Agent responses will store the timestamp of the call, list the batch_size and the total_cost, then calculate and store the entity_cost when total_cost > 0.0000000.

This will allow us to manage data for agent prompts cleanly, and reference them from multiple locations (agent_responses, candidate.candidate_data.agent_responses, company.company_data.agent_responses, job.job_data.agent_responses) and we will have one api endpoint to fetch the data by the agent_data_id, which will be used by each source as the universal key to the text.

This will also allow us to manage storage over time, when a whole batch of jobs have completed their lifecycle, their agent_data can be archived.

This resolves the issue of "where is the data" and "how do I get the response data for this specific entity with the context of what was sent?"

We also need an endpoint to parse the content for the specific entity from the agent_data content get_agent_data(<batch_id>, Optional \[<block_type>\], Optional <entity_id>)

So, entities (candidate, job, company) will have batch_id in their agent_responses content, e.g. {"task_key":"prefilter", "created_at":<timestamp>, "batch_id":<batch_id>, "entity_cost":<total_cost>/<batch_size>}

and when the api needs to build a modal, it can pull up the agent data (which will always be read-only) using the batch_id.
When we query for batch_id from agent_data, we will get the blocks of content sent and the block received

Let's not touch the front end for the scope of this work, we will be building an agent_response widget that will conform to all entity types and allow the user to see the full picture.

### Comments

_No comments._

---

# AST-330 Create agent_data as Pure Data Storage

## Plan

### Context

Today, prompt content and responses flow through `src/external/anthropic.py` — a module that has gradually absorbed core-layer responsibilities (schema validation, grade validation, audit logging, prompt resolution from DB). The `do_task` function is the primary orchestrator, but it lives in the external layer while doing business logic. Meanwhile, agent response data is stored in two redundant locations: compressed BLOBs in the `agent_responses` table and inline JSON in entity-level `agent_responses` fields (company, candidate, job).

AST-330 introduces a clean separation:

1. **`agent_data` table** — entity-agnostic, read-only storage of every content block sent to and received from Anthropic. Keyed by batch_id so entities can retrieve "what happened in my batch."
2. **`src/core/agent.py`** — new core module that owns `do_task` (lifted from anthropic.py), agent_data storage, and data retrieval. Consult, roster, and candidate import from here instead of external.
3. **`src/external/anthropic.py`** — reduced to its proper role: raw Anthropic API client (send blocks, receive response, log timesheet).
4. **`dispatch_ledger` enhancements** — adds entity_type, batch_size, prompt_blocks (references to agent_data), total_cost (computed from timesheets on batch completion).
5. **Entity agent_responses content** — lightweight batch_id references (`{task_key, batch_id, created_at, entity_cost}`) instead of inline data.

The front end is **out of scope** for AST-330 per the ticket.

### Design decisions

**D1 — agent_data has NO entity_id.** The agent_data table is entity-agnostic storage. Entities (job, company, candidate) know which batch_id they were processed in and request their data by batch_id. For batch-mode tasks where one API call processes multiple entities, the TASK block contains entity markers (e.g., `[astral_job_id=X]`), and the `get_agent_data` function can parse entity-specific content at retrieval time.

**D2 — One batch_id per dispatch run.** The dispatch batch_id groups all API calls within one dispatch cycle. Shared prompt blocks (SYSTEM, CACHE_A) are stored once per batch. Per-call TASK blocks are stored per API call, all sharing the same batch_id. For Pattern-A tasks (one API call per batch), there's one set of blocks. For per-entity tasks (render_verdict), there are N TASK blocks but one shared SYSTEM/CACHE set.

**D3 — do_task moves to core, not duplicated.** `do_task` lifts from `anthropic.py` to `agent.py` wholesale. `anthropic.py` retains `_send_and_parse` (renamed to `send_to_anthropic`) as its primary export. Block assembly moves to `agent.py`. This fixes the existing layer violation where external was doing core-layer work.

**D4 — ad-hoc endpoint uses agent.py.** `api_admin.py` currently imports `_fetch_response_from_content` directly from external (documented deviation). After refactor, it imports a `run_adhoc` function from `agent.py`, fixing the layer violation.

**D5 — agent_responses table stays.** It continues to store per-call audit records (task_key, entity_type, entity_id, status, failure_note, request_id, created_at). The `runtime_prompt` column changes from a full content BLOB to a JSON array of `{type, agent_data_id}` references. `raw_response` and `parsed_response` stay as-is for now — they're small relative to prompts and useful for debugging.

**D6 — Entity agent_responses content migration.** Entities will store batch references in their agent_responses JSON. The company/job/candidate `agent_responses` fields transition from inline response data to lightweight batch references: `{task_key, batch_id, created_at, entity_cost}`. This happens incrementally — new writes use the new format; old data is readable via the existing `list_agent_responses` query (agent_responses table). No migration of historical inline data needed.

**D7 — total_cost computed on batch completion.** When a dispatch batch finishes, `agent.py` computes total_cost from timesheets (using existing `sum_cost_by_batch`) and stores it on the dispatch_ledger record. entity_cost = total_cost / batch_size, stored in each entity's agent_responses reference.

---

### Step 0: Add BLOCK_TYPES to config.py

**File:** `src/utils/config.py`

- Add `BLOCK_TYPES` list to config:
  ```python
  BLOCK_TYPES = ["SYSTEM", "CACHE_A", "CACHE_B", "CACHE_C", "CACHE_D", "NO_CACHE", "TASK", "RESPONSE"]
  ```
- Maps to the current block structure in `_fetch_response_from_content`:
  - `SYSTEM` → system_prompt (agent content, cached)
  - `CACHE_A` → cached_context (cache_prompt, cached)
  - `CACHE_B–D` → reserved for future additional cached blocks
  - `NO_CACHE` → nocache_context (nocache_prompt, not cached)
  - `TASK` → user prompt + live_content (not cached)
  - `RESPONSE` → parsed response from Anthropic

### Step 1: Create agent_data table in database.py

**File:** `src/data/database.py`

- Add `agent_data` to the table inventory comment at top of file.
- Add schema flag `_agent_data_schema_ensured = False`.
- Add `_ensure_agent_data_schema`:
  ```sql
  CREATE TABLE agent_data (
      agent_data_id TEXT PRIMARY KEY,
      entity_type TEXT NOT NULL,
      task_key TEXT NOT NULL,
      batch_id TEXT NOT NULL,
      created_at TIMESTAMP NOT NULL,
      block_type TEXT NOT NULL,
      block_data BLOB
  )
  CREATE INDEX idx_agent_data_batch ON agent_data(batch_id)
  ```
- `block_data` uses BLOB with the existing `_compress_payload` / `_decompress_payload` helpers (zlib).
- Add CRUD functions:
  - `save_agent_data(agent_data_id, entity_type, task_key, batch_id, created_at, block_type, block_data)` — insert one block. block_data is compressed before storage.
  - `get_agent_data_by_batch(batch_id, block_type=None)` — return all blocks for a batch_id, optionally filtered by block_type. Decompresses block_data transparently. Ordered by created_at ASC.
  - `get_agent_data(agent_data_id)` — return single block by ID.

### Step 2: Add fields to dispatch_ledger in database.py

**File:** `src/data/database.py`

- Add migration columns to `_ensure_dispatch_ledger_schema` for existing tables:
  - `entity_type TEXT`
  - `batch_size INTEGER`
  - `agent_performance TEXT` — agent_performance.status from the API response envelope
  - `agent_note TEXT` — agent_performance.failure_note from the API response envelope
  - `total_cost REAL DEFAULT 0.0`
  - `prompt_blocks TEXT` — JSON array of `[{type: <block_type>, data: <agent_data_id>}]`
- Add these columns to `_LEDGER_UPDATE_COLS` allowlist so `update_dispatch_ledger` can set them.
- Add `entity_type` and `batch_size` as parameters to `save_dispatch_ledger`.

### Step 3: Create src/core/agent.py — the main event

**File:** `src/core/agent.py` (new)

This module becomes the single orchestration point for all agent interactions. Functions that **move here** from `anthropic.py`:

| Function | Current location | Notes |
|----------|-----------------|-------|
| `do_task()` | `anthropic.py` | Primary orchestrator — resolves prompts, assembles blocks, stores to agent_data, calls external, validates, audits |
| `preview_prompt()` | `anthropic.py` | Prompt resolution preview (no API call) |
| `_resolve_task_prompts()` | `anthropic.py` | DB lookup for agent_task + agent records |
| `_validate_response_schema()` | `anthropic.py` | Schema validation against TASK_CONFIG |
| `_validate_grades()` | `anthropic.py` | Grade-level validation for graded tasks |
| `_store_agent_response()` | `anthropic.py` | Audit logging to agent_responses table |
| `_build_context()` | `anthropic.py` | Context string construction from task_config |

Functions that **stay in anthropic.py** (pure external):

| Function | Reason |
|----------|--------|
| `send_to_anthropic()` (renamed `_send_and_parse`) | Raw API call + timesheet logging |
| `_get_client()` | Anthropic client construction |
| `getTimestampPrefix()` | Utility (used by block assembly in agent.py, imported from external) |
| `_parse_api_response()` | Response text extraction |
| `_parse_json_response()` | JSON parsing |
| `_parse_python_code_response()` | Python code parsing |
| `_add_timesheet_entry()` | Timesheet logging (documented exception) |

**New functions in agent.py:**

- `_assemble_blocks(system_content, user_content, cache_content, nocache_content, live_content, model_code, skip_cache)` — builds the system_blocks and user_blocks lists. Extracted from the current `_fetch_response_from_content`. Returns `(system_blocks, user_blocks, runtime_prompt_metadata)`.

- `_store_prompt_blocks(batch_id, entity_type, task_key, system_content, cache_content, nocache_content, task_content)` — stores each non-empty content string as a row in agent_data with the appropriate block_type. Returns `prompt_blocks` list (the `[{type, data}]` references for the ledger). Deduplicates shared blocks within a batch — if a SYSTEM block for this batch_id already exists, reuses the existing agent_data_id instead of inserting a duplicate.

- `get_agent_data(batch_id, block_type=None, entity_id=None)` — public retrieval function. Calls `database.get_agent_data_by_batch(batch_id, block_type)`. When `entity_id` is provided, parses TASK block content to extract the portion relevant to that entity (searches for markers like `[astral_job_id=X]` or `[company_id=X]`).

- `get_entity_response(batch_id, entity_id)` — retrieves the RESPONSE block for a batch, then extracts the element matching `entity_id`. If batch_size == 1 (single-entity call), returns the entire parsed response. If batch_size > 1 (Pattern-A batch call), parses the response JSON and finds the element whose identifier matches `entity_id` (e.g., iterates `response["jobs"]` looking for `astral_job_id == entity_id`). Returns `None` if no match found.

- `run_adhoc(system_content, user_content, cache_content, nocache_content, live_content, model_code, temperature, max_tokens, candidate_id, task_key_uuid, api_key_override)` — thin wrapper for the ad-hoc workbench. Assembles blocks, calls `send_to_anthropic`, returns result. No agent_data storage (ad-hoc calls are ephemeral).

- `compute_batch_cost(batch_id)` — calls `database.sum_cost_by_batch([batch_id])`, returns total cost for the batch.

**Refactored do_task flow:**

1. Look up TASK_CONFIG (unchanged)
2. Resolve candidate context from ctx (unchanged)
3. Fetch agent_task + agent from DB via `_resolve_task_prompts` (moved here)
4. Resolve tokens in all prompt strings (unchanged)
5. **NEW:** Store prompt blocks to agent_data via `_store_prompt_blocks`
6. Assemble system_blocks + user_blocks via `_assemble_blocks`
7. Call `send_to_anthropic()` from external layer (was `_send_and_parse`)
8. Validate response schema (moved here)
9. Validate grades if applicable (moved here)
10. **NEW:** Store parsed response as a RESPONSE block in agent_data
11. Store audit via `_store_agent_response` (moved here, now stores prompt_blocks references instead of full content in runtime_prompt)
12. Unwrap agent_payload (unchanged)
13. Return result

**Imports for agent.py:**
```python
from src.data.database import (
    get_agent_task, get_agent,           # prompt resolution
    add_agent_response_entry,            # audit logging
    save_agent_data, get_agent_data_by_batch, get_agent_data,  # agent_data CRUD
)
from src.external.anthropic import send_to_anthropic, getTimestampPrefix
from src.utils.config import (
    TASK_CONFIG, BASE_SCHEMA, BLOCK_TYPES,
    resolve_tokens, get_model, CHARS_PER_TOKEN,
)
from src.utils.logging import get_logger, log_batch_id
```

This is clean: core imports data + external + utils. No layer violations.

### Step 4: Refactor anthropic.py to pure external

**File:** `src/external/anthropic.py`

- **Remove** (moved to agent.py): `do_task`, `preview_prompt`, `_resolve_task_prompts`, `_validate_response_schema`, `_validate_grades`, `_store_agent_response`, `_build_context`.
- **Remove** (decomposed): `_fetch_response_from_content` — block assembly logic → `_assemble_blocks` in agent.py, orchestration → absorbed into `do_task`, ad-hoc usage → `run_adhoc` in agent.py.
- **Rename** `_send_and_parse` → `send_to_anthropic` and export it (`__all__ = ["send_to_anthropic", "getTimestampPrefix"]`).
- **Remove data-layer imports** that are no longer needed: `add_agent_response_entry`, `get_agent_task`, `get_agent`. Only `_add_timesheet_entry` remains (documented exception).
- `send_to_anthropic` signature stays the same (takes assembled content_blocks, system_blocks, model params, returns result dict with api_response, parsed_response, timesheet).
- Parsing functions (`_parse_api_response`, `_parse_json_response`, `_parse_python_code_response`) stay — they're called by `send_to_anthropic` internally.

After refactor, anthropic.py's only imports from the data layer:
```python
from src.data.database import _add_timesheet_entry  # documented exception
```

### Step 5: Refactor all do_task callers

**5a. `src/core/consult.py`**

- Change import: `from src.external.anthropic import do_task` → `from src.core.agent import do_task`
- Remove import of `add_agent_response_entry` from `src.data.database` entirely.
- Remove the explicit `add_agent_response_entry` call in `render_verdict` (line 145) — `do_task` now handles audit internally, and the RESPONSE block in agent_data preserves the full response.
- Remove both `add_agent_response_entry` calls in `_run_batch_consult` (lines 216, 263) — same reason. Reconciliation metadata (missing/fabricated IDs) is already logged by the dispatcher.
- All other logic (grading, state transitions, job_data saves) stays exactly as-is.

**5b. `src/core/roster.py`**

- Change import: `from src.external.anthropic import do_task` → `from src.core.agent import do_task`
- `prefilter_company`, `_fetch_prefilter_notes`, `_fetch_select_job_page`, `_fetch_parse_job_list` all call `do_task` — import path changes, call signatures unchanged.

**5c. `src/core/candidate.py`**

- Change import: `from src.external.anthropic import do_task, preview_prompt` → `from src.core.agent import do_task, preview_prompt`
- `parse_candidate_resume` calls `do_task` — import path changes, call signature unchanged.
- `preview_task_prompt` calls `preview_prompt` — same.

**5d. `src/ui/api/api_candidate.py`** (fixes layer violation)

- Change import: `from src.external.anthropic import do_task` → `from src.core.agent import do_task`
- This fixes the existing UI → external layer violation. UI → core is correct per §3.3.

**5e. `src/ui/api/api_admin.py`** (fixes layer violation)

- Change import: `from src.external.anthropic import _fetch_response_from_content` → `from src.core.agent import run_adhoc`
- Refactor `adhoc_test()` endpoint to call `run_adhoc(...)` instead of `_fetch_response_from_content(...)`. `run_adhoc` has the same essential contract: takes assembled prompt strings + model params, returns result dict.

**5f. `scripts/migrations/bootstrap_candidate.py`**

- Change import: `from src.external.anthropic import do_task` → `from src.core.agent import do_task`
- Scripts are exempt from layer rules per §3.3, but the import must be updated since `do_task` is removed from `anthropic.py`.

### Step 6: Add API endpoints for agent_data retrieval

**File:** `src/ui/api/api_system.py`

Agent data is a cross-cutting read-only service used by all entity types (job modals, company modals, candidate views, the future agent_response widget). It belongs in system, not admin.

- Add endpoint: `GET /api/agent_data/<batch_id>`
  - Optional query params: `block_type`, `entity_id`
  - Calls `from src.core.agent import get_agent_data`
  - Returns JSON array of agent_data blocks for the batch
  - Protected with `@require_auth`

- Add endpoint: `GET /api/agent_data/<batch_id>/entity/<entity_id>`
  - Calls `from src.core.agent import get_entity_response`
  - Returns the parsed response content for that specific entity within the batch
  - Protected with `@require_auth`

These are the read-only endpoints the front end will use to build agent response modals (future ticket, not AST-330's UI scope).

### Step 7: Wire up dispatch_ledger updates

**File:** `src/core/dispatcher.py`

- Update `_dispatch_task` to pass `entity_type` and `batch_size` to `save_dispatch_ledger`.
- After batch completion (in the `finally` block), call `agent.compute_batch_cost(batch_id)` and store `total_cost` on the ledger via `update_dispatch_ledger`.
- Update `list_dispatch_ledger` enrichment — `total_cost` is now stored on the ledger row directly (from Step 2), so the runtime `sum_cost_by_batch` join can be replaced by reading the stored value. Keep the join as a fallback for legacy rows that don't have `total_cost` populated.

### Step 8: Update ASTRAL_CODE_RULES

**File:** `docs/ASTRAL_CODE_RULES.md`

- Add `agent.py` to the core layer directory listing in §3.1.
- Update §2.2 "Core → External" section to reflect that `do_task` now lives in core (`agent.py`), calling `send_to_anthropic` from external.
- Update §3.2 Layer Rules to note that anthropic.py's documented exception is now reduced to `_add_timesheet_entry` only (no more `add_agent_response_entry`, `get_agent_task`, `get_agent`).
- Add `agent_data` to the table inventory in database.py's module docstring.
- Add `BLOCK_TYPES` to the config blocks section in §2.1.

---

### Files Changed

| File | Action | What changes |
|------|--------|-------------|
| `src/utils/config.py` | Modify | Add `BLOCK_TYPES` list |
| `src/data/database.py` | Modify | Add `agent_data` table schema + CRUD; add `dispatch_ledger` migration columns; update module docstring inventory |
| `src/core/agent.py` | **Create** | New core module: `do_task`, `preview_prompt`, `get_agent_data`, `get_entity_response`, `run_adhoc`, `compute_batch_cost`, `_assemble_blocks`, `_store_prompt_blocks` + moved validation/audit functions |
| `src/external/anthropic.py` | Modify | Remove moved functions; rename `_send_and_parse` → `send_to_anthropic`; reduce data-layer imports to `_add_timesheet_entry` only |
| `src/core/consult.py` | Modify | Change `do_task` import path (external → core agent); remove redundant `add_agent_response_entry` calls |
| `src/core/roster.py` | Modify | Change `do_task` import path (external → core agent) |
| `src/core/candidate.py` | Modify | Change `do_task` + `preview_prompt` import path (external → core agent) |
| `src/ui/api/api_candidate.py` | Modify | Change `do_task` import path (external → core agent); fixes layer violation |
| `src/ui/api/api_admin.py` | Modify | Change `_fetch_response_from_content` import to `run_adhoc` from core agent; fixes layer violation |
| `src/ui/api/api_system.py` | Modify | Add `GET /api/agent_data/<batch_id>` and `GET /api/agent_data/<batch_id>/entity/<entity_id>` endpoints |
| `src/core/dispatcher.py` | Modify | Pass entity_type + batch_size to ledger; store total_cost on completion |
| `docs/ASTRAL_CODE_RULES.md` | Modify | Add agent.py to directory listing; update layer documentation; add agent_data to table inventory |

---

## Review against ASTRAL_CODE_RULES

### §1.1 Scope and Isolation
**Pass.** New table (`agent_data`) is added to the database.py inventory. No tables outside the inventory are touched. The refactor moves existing code between layers — no new external dependencies.

### §1.2 / §3.3 Import Rules
**Pass — and improves compliance.** This refactor fixes two existing layer violations:
- `api_candidate.py` imported `do_task` from external → now imports from core. ✓
- `api_admin.py` imported `_fetch_response_from_content` from external → now imports `run_adhoc` from core. ✓
- `anthropic.py`'s data-layer imports reduce from four (`_add_timesheet_entry`, `add_agent_response_entry`, `get_agent_task`, `get_agent`) to one (`_add_timesheet_entry`). The remaining import stays as a documented exception.
- New `agent.py` imports: data + external + utils — compliant for core layer.

### §1.3 DRY
**Pass.** `do_task` moves once, all callers re-point. No duplication. Block assembly logic extracted once into `_assemble_blocks`. Shared block dedup in `_store_prompt_blocks` avoids storing identical SYSTEM/CACHE content N times per batch.

### §1.4 No Hardcoded Sets
**Pass.** `BLOCK_TYPES` lives in config.py. `agent.py` validates block_type against the config list, not inline constants.

### §2.1 Config as Source of Truth
**Pass.** `BLOCK_TYPES` added to config. No behavior-driving values introduced outside config.

### §2.4 Batch Processing Pattern
**Pass.** agent_data uses `batch_id` consistently — blocks are grouped by the dispatch batch_id. The claim/process/release pattern is unchanged.

### §2.5 Bright Line: Core vs External
**Pass — and improves compliance.** The bright line was blurry before: `anthropic.py` (external) was doing schema validation, grade validation, prompt resolution from DB, and audit logging — all core concerns. After refactor, external owns only I/O (API call + timesheet); core owns orchestration, validation, and audit.

### §2.6 State Machine
**Not affected.** No state transitions change. State machines remain config-driven and managed by the existing core modules.

### §2.8 Coat-Check Pattern
**Not affected.** Coat-check handlers in roster.py and tracker.py continue to call `do_task` — only the import path changes.

### §2.9 Auth
**Pass.** New endpoints `GET /api/agent_data/<batch_id>` and `GET /api/agent_data/<batch_id>/entity/<entity_id>` in `api_system.py` use `@require_auth`.

### §3.2 Layer Rules
**Pass.** After refactor:
- `ui` imports from core + utils only. ✓
- `core (agent.py)` imports from data + external + utils. ✓
- `external (anthropic.py)` imports from utils + one documented data exception. ✓

### §3.5 Naming
**Pass.** `agent.py` follows snake_case convention. New endpoint uses snake_case path. No new frontend files (out of scope).

### §4.1 Branching
**Noted deviation.** Working on `dev-refactor-agent-data` feature branch per Susan's direction (this is a large structural refactor that warrants isolation from day-to-day `dev` work). Will merge back to `dev` when stable.

### Trade-offs and flags

**T1 — Scope.** This is a structural refactor touching 11 files across all layers. The refactor itself is mechanical (move functions, update imports), but the surface area means careful testing is needed. Recommend implementing in sub-steps: Steps 0-2 (data layer), then Steps 3-4 (the big move), then Step 5 (callers), then Steps 6-8 (wiring).

**T2 — Shared block dedup.** `_store_prompt_blocks` checks whether a SYSTEM/CACHE block already exists for this batch_id before inserting. For per-entity tasks (render_verdict), the first call stores the shared blocks; subsequent calls reuse them. This avoids N copies of identical system prompts. The check is a simple SELECT by (batch_id, block_type) — cheap for SQLite.

**T3 — entity_id parsing in get_agent_data.** The `entity_id` parameter on `get_agent_data` is a runtime filter, not a stored field. It searches TASK block content for entity markers. This works because all current live_content formats include entity identifiers (`[astral_job_id=X]`, `[company_id=X]`). If a future task doesn't include markers, entity_id filtering won't work for it — but that's a future concern, not a current one.

**T4 — Ad-hoc calls don't store to agent_data.** The ad-hoc workbench is ephemeral by design. `run_adhoc` sends to Anthropic and returns the result without persisting prompt blocks. Timesheets still log normally.

### No conflicts found. Plan is ready for review.

---

## Review

**Commit:** `0e58a93`
**Branch:** `dev-refactor-agent-data`
**Reviewed:** 2026-03-19

---

## What's Solid

- **Correct diagnosis.** The plan accurately identifies that `do_task` in `anthropic.py` is performing core-layer work (schema validation, grade validation, prompt resolution from DB, audit logging). Moving it to `src/core/agent.py` is the right fix. Verified: `anthropic.py` currently imports `_add_timesheet_entry`, `add_agent_response_entry`, `get_agent_task`, `get_agent` from the data layer — all four confirmed present at line 20.
- **Complete caller inventory (with one exception — see Issue 1).** The plan identifies all five production callers of `do_task`: `consult.py`, `roster.py`, `candidate.py`, `api_candidate.py`, `api_admin.py`. Each gets a specific refactor step with clear before/after import paths. All confirmed by grep.
- **Design decisions are well-reasoned.** D1–D7 lay out architectural choices with clear rationale. The entity-agnostic storage approach (D1), batch_id grouping (D2), and incremental migration strategy (D6) are pragmatic. D3's "move, not duplicate" principle is the right call.
- **Thorough self-audit.** The "Review against ASTRAL_CODE_RULES" section walks through every relevant rule and correctly assesses compliance. The layer violation fixes (api_candidate.py, api_admin.py) are genuine improvements.
- **Block dedup (T2) is well-designed.** Checking for existing SYSTEM/CACHE blocks before inserting avoids N copies per batch. The SELECT by `(batch_id, block_type)` is cheap and correct for SQLite.
- **Scope boundary is clear.** Frontend explicitly out of scope. Agent data endpoints are added as read-only hooks for future UI work without overreaching.

---

## Issues

### Issue 1 — Missing caller: `scripts/migrations/bootstrap_candidate.py` ⚠️ required

`scripts/migrations/bootstrap_candidate.py` line 20 imports `from src.external.anthropic import do_task`. This caller is not listed in Step 5. When `do_task` is removed from `anthropic.py` (Step 4), this import will break.

Scripts are exempt from layer rules per §3.3, so the fix is simply updating the import path. But it needs to be in the plan so the implementer doesn't miss it.

**Recommendation:** Add Step 5f for `scripts/migrations/bootstrap_candidate.py` — change import to `from src.core.agent import do_task`.

**Susan says: Yes, even though bootstrap_candidate.py is currently out of scope, we should update the imports so we don't get confused later.  

### Issue 2 — `entity_type` on `agent_data` vs. D1's "entity-agnostic" claim ℹ️ advisory

D1 says "agent_data has NO entity_id" and describes the table as "entity-agnostic storage." But the Step 1 schema includes `entity_type TEXT NOT NULL`. These aren't contradictory (type != ID), but the wording creates ambiguity:

- For SYSTEM/CACHE blocks shared across a batch, what `entity_type` do they get? The dedup logic in `_store_prompt_blocks` (T2) reuses existing shared blocks — but the first write sets `entity_type` as NOT NULL. For a batch of jobs, the shared SYSTEM block gets entity_type="job", which is fine. But if a future batch mixes entity types, or if SYSTEM content is truly entity-agnostic, the column creates a conceptual misfit.
- Consider: is `entity_type` actually a property of the *batch* (already on dispatch_ledger) rather than the *block*? Storing it per-block may be redundant with the ledger.

**Recommendation:** Either (a) clarify in D1 what entity_type means for shared blocks, or (b) make entity_type nullable on agent_data (shared blocks get NULL) and rely on dispatch_ledger for the authoritative entity_type of the batch.

### Issue 3 — Double-audit: `do_task` internal audit vs. `consult.py` explicit calls ℹ️ advisory

The plan correctly identifies that consult.py's `add_agent_response_entry` calls should be removed (Step 5a). However, the current consult.py calls store *different* data than do_task's internal `_store_agent_response`:

- `render_verdict` (line 145): stores with `entity_type="job"`, `entity_id=astral_job_id` — per-job granularity.
- `_run_batch_consult` (lines 216, 263): stores with `entity_id=f"{task_key}_batch_{batch_id}"` — batch-level granularity, includes reconciled parsed results.
- `do_task`'s internal `_store_agent_response` (lines 503, 519, 539, 550): stores with the `index` parameter as entity context.

The `_run_batch_consult` calls log batch-level audit entries with reconciled per-entity results after do_task's Pattern-A response has been parsed and matched. If do_task only logs the raw response before reconciliation, removing the consult calls would lose the post-reconciliation audit trail.

**Recommendation:** During implementation, verify that do_task's audit captures enough detail that the consult-level audit calls are truly redundant. If not, either (a) keep the consult calls with a comment explaining why, or (b) add a post-processing audit hook to do_task.

### Issue 4 — `getTimestampPrefix` naming and placement ℹ️ advisory

The plan has `agent.py` importing `getTimestampPrefix` from `src.external.anthropic` (Step 3 imports). Two concerns:

1. **Naming:** `getTimestampPrefix` is camelCase, violating §3.5 (Python = snake_case). It's legacy, but this refactor is a natural opportunity to rename it to `get_timestamp_prefix`.
2. **Placement:** This is a pure utility function (returns a formatted timestamp string). Having core import a utility from external is allowed per §3.3 but architecturally odd. It belongs in `src/utils/formatting.py` alongside the other formatting helpers.

**Recommendation:** Move to `src/utils/formatting.py` as `get_timestamp_prefix()` during the refactor. Update the one remaining caller in `anthropic.py` to import from utils.

### Issue 5 — `_fetch_response_from_content` described as "moved" but actually decomposed ℹ️ advisory

Step 4 lists `_fetch_response_from_content` in the "Remove (moved to agent.py)" set. But this function isn't moved wholesale — its block assembly logic is extracted into `_assemble_blocks` (Step 3), and its orchestration is absorbed into the refactored `do_task` flow. The function itself ceases to exist.

Step 3 correctly describes `_assemble_blocks` as "Extracted from the current `_fetch_response_from_content`" and `run_adhoc` as the ad-hoc replacement. But Step 4's "moved" label could mislead the implementer into looking for a 1:1 correspondence.

**Recommendation:** In Step 4, change "moved to agent.py" to "decomposed: block assembly → `_assemble_blocks`, orchestration → `do_task`, ad-hoc → `run_adhoc`".

### Issue 6 — `agent_success` / `agent_note` on dispatch_ledger vs. existing `status` ℹ️ advisory

Step 2 adds `agent_success TEXT` and `agent_note TEXT` to `dispatch_ledger`. The ledger already has a `status` column (RUNNING/COMPLETED/FAILED/INTERRUPTED — set by the dispatcher). Adding `agent_success` (described as "agent_performance.status from the API response") creates two status-like columns on the same table with different semantics.

This is valid (dispatch status ≠ AI performance status), but the naming could confuse consumers. A batch can have `status=COMPLETED` but `agent_success=FAILED` (dispatch finished, but the AI returned an error).

**Recommendation:** Either (a) rename to `ai_status` / `ai_note` for clearer disambiguation, or (b) add an inline comment to the schema clarifying the distinction.

---

## Recommended Actions

| # | Severity | Action | Verdict | Resolution |
|---|----------|--------|---------|------------|
| 1 | Fix now | Add `scripts/migrations/bootstrap_candidate.py` to Step 5 | DO | ✅ Added as Step 5f |
| 2 | Discuss | Clarify `entity_type` semantics on shared blocks | SKIP | Entity_type is understood as candidate/company/job. Shared blocks inherit the batch's entity_type. Codify as config setting if not already (future-proofs for new entity types). |
| 3 | Discuss | Verify consult.py audit calls are redundant | DO | ✅ Confirmed redundant now that RESPONSE block exists in agent_data. Explicit removal calls added to Step 5a. |
| 4 | Advisory | Move `getTimestampPrefix` to utils | SKIP | Only used by agent — stays in anthropic.py, imported by agent.py. Not a universal function. |
| 5 | Advisory | Reword Step 4 re: `_fetch_response_from_content` | DO | ✅ Step 4 updated: "decomposed" with clear mapping to `_assemble_blocks`, `do_task`, `run_adhoc`. |
| 6 | Advisory | Rename `agent_success`/`agent_note` | SKIP | Renamed `agent_success` → `agent_performance` to match the prompt envelope field name. `agent_note` stays. No "AI" terminology in codebase. |




---

## Change Requests

### CR-1 — Add RESPONSE to BLOCK_TYPES ✅ applied

The original plan omitted RESPONSE from the block type enum. The ticket says agent_data stores "content sent AND received." The parsed response from Anthropic must be stored as a RESPONSE block in agent_data so that `get_entity_response` can retrieve it.

**Applied:** RESPONSE added to BLOCK_TYPES in Step 0. do_task flow Step 10 added: store parsed response as RESPONSE block.

### CR-2 — Add `get_entity_response(batch_id, entity_id)` to agent.py ✅ applied

Need a function that retrieves the response for a specific entity from a batch. For batch_size == 1, returns the whole response. For batch_size > 1, parses the response JSON to find the element matching entity_id. Lives in agent.py (core) because it orchestrates across two data sources: the RESPONSE block from agent_data and cost data from the dispatch_ledger (total_cost / batch_size).

**Applied:** `get_entity_response` added to Step 3 new functions list. Corresponding API endpoint added in Step 6.

### CR-3 — Move agent_data endpoint from admin to system ✅ applied

Agent data is a cross-cutting read-only service used by all entity types (job modals, company modals, candidate views, the future agent_response widget). It doesn't belong under `/api/admin/`. Moved to `api_system.py` as `GET /api/agent_data/<batch_id>` with an additional entity-specific endpoint `GET /api/agent_data/<batch_id>/entity/<entity_id>`.

**Applied:** Step 6 updated to target `api_system.py`. Files Changed table updated. §2.9 Auth review updated.

---

## Code Review

**Commits:** `38ba878`, `027e877`
**Branch:** `dev-refactor-agent-data`
**Reviewed:** 2026-03-19

---

## What's Solid

- **anthropic.py is clean.** Reduced from ~800 lines to 319. Pure API client: send blocks, parse response, log timesheet. Single documented exception (`_add_timesheet_entry`). All orchestration/validation/audit correctly removed. `__all__` properly declared.
- **agent.py is well-structured.** Clear section headers, public functions first, helpers grouped by concern. `do_task` flow follows the plan's 13-step sequence faithfully. Block assembly extracted cleanly from the old `_fetch_response_from_content`.
- **All callers updated — none missed.** `consult.py`, `roster.py`, `candidate.py`, `api_candidate.py`, `api_admin.py`, `bootstrap_candidate.py` — all confirmed re-pointed to `src.core.agent`. Layer violations fixed: UI no longer imports from external.
- **consult.py audit calls correctly removed.** Three `add_agent_response_entry` calls removed (render_verdict line 145, _run_batch_consult lines 216 and 263). The RESPONSE block in agent_data + entity agent_responses reference make these genuinely redundant.
- **Golden ticket batch_id.** Consistently implemented: dispatcher generates `f"{task_key}-{uuid}"`, passes through runners into claim functions. One ID per dispatch run ties together row-locking, ledger, agent_data, timesheets, and entity agent_responses. CR-6 delivered as designed.
- **dispatch_ledger migration is clean.** New columns added idempotently — fresh tables get them in CREATE, existing tables get ALTER TABLE. `_LEDGER_UPDATE_COLS` allowlist properly extended.
- **agent_data CRUD is solid.** Proper compression/decompression, INSERT OR IGNORE for deterministic dedup, block_type validated against BLOCK_TYPES, `token_size` estimate included per CR-4.
- **Uniform entity agent_responses.** Job and candidate tables get `agent_responses TEXT DEFAULT '[]'` migration. All three entities now parse the column as JSON on read. `append_agent_response` handles all three tables via `_TABLE_MAP`.
- **api_system.py endpoints are clean.** Lazy imports, `@require_auth`, proper 404 handling.
- **ASTRAL_CODE_RULES updates are thorough.** Golden ticket pattern documented in §2.4, entity agent_responses in §2.4.1, agent.py in directory listing, anthropic.py exception text updated.
- **generate_artifact properly wired through dispatch pattern (CR-5).** Creates ledger entry, sets `log_batch_id`, computes total_cost on completion, returns `batch_id` in response.

---

## Issues

### Issue 1 — `compute_batch_cost` bypasses existing `sum_cost_by_batch` and imports private DB internals 🔧 fix now

`agent.py:compute_batch_cost` (lines 653-672) writes raw SQL and imports private functions `_get_connection` and `_run_with_retry` from `database.py`. But `database.sum_cost_by_batch(batch_ids)` already exists (database.py line 1178) and does the same query.

This violates §1.3 DRY and creates a core→data coupling to private internals. The plan itself said "calls `database.sum_cost_by_batch([batch_id])`".

```python
# Current (agent.py lines 655-672)
from src.data.database import _get_connection, _run_with_retry
# ... raw SQL ...

# Should be:
from src.data.database import sum_cost_by_batch
def compute_batch_cost(batch_id: str) -> float:
    costs = sum_cost_by_batch([batch_id])
    return costs.get(batch_id, 0.0)
```

### Issue 2 — Dead imports in agent.py ℹ️ advisory

Two imports are unused:
- `_add_timesheet_entry` (line 17) — imported but never called in agent.py. Timesheets are logged by `send_to_anthropic` in anthropic.py.
- `ENTITY_TYPES` (line 28) — imported but never referenced. `entity_type` values pass through unvalidated.

### Issue 3 — Three silent `except Exception: pass` blocks in `do_task` ℹ️ advisory

Lines 433-434, 478-479, and 493-494 swallow all exceptions with no logging:

```python
try:
    prompt_blocks = _store_prompt_blocks(...)
except Exception:
    pass  # silent
```

The "best-effort" intent is fine, but silently swallowing exceptions makes debugging impossible. If agent_data storage breaks (e.g., schema issue, disk full, encoding error), there's zero signal. A `logger.debug` or `logger.warning` with `exc_info=True` would preserve the intent while maintaining observability.

### Issue 4 — `run_adhoc` drops `candidate_id`, `api_key_override`, `task_key_uuid` ⚠️ required

The old `_fetch_response_from_content` accepted `candidate_id`, `api_key_override`, and `task_key_uuid` — all of which `api_admin.py:adhoc_test` computed via `_resolve_adhoc` and passed through. The new `run_adhoc` signature doesn't accept these, and the `adhoc_test` endpoint no longer passes them (diff lines 636-638 deleted).

Consequences:
- **Adhoc calls always use the system API key**, even when a candidate with their own key is selected. Previously, `api_key_override` let the adhoc endpoint use the candidate's key.
- **Timesheets for adhoc calls lose `candidate_id` and `task_key_uuid`**, so adhoc costs can't be attributed to a candidate or linked to a task version.
- **`_resolve_adhoc` still computes** `candidate_id`, `task_key_uuid`, and `api_key_override` — they're now dead computed values.

This may be intentional (adhoc is development-only, system key is fine), but it's a behavior regression. If intentional, the dead code in `_resolve_adhoc` should be cleaned up.

### Issue 5 — `user_content` stored as NO_CACHE instead of TASK block type ℹ️ advisory

`_store_prompt_blocks` (lines 168-169) stores `user_content` as a second NO_CACHE block:

```python
if user_content:
    prompt_blocks.append({"type": "NO_CACHE","id": _save("NO_CACHE", user_content, deterministic=False)})
```

The plan (Step 0) mapped TASK = "user prompt + live_content". The implementation splits them: `live_content` → TASK, `user_content` → NO_CACHE. This means `get_agent_data_by_batch(batch_id, block_type="NO_CACHE")` returns multiple blocks (nocache_prompt + user_prompt) with no way to distinguish them.

This may be a deliberate split (user_prompt is static, live_content is entity-specific), but it diverges from the plan's mapping and creates ambiguity in retrieval.

### Issue 6 — `context` parameter on `send_to_anthropic` is dead ℹ️ advisory

`send_to_anthropic` accepts `context: Optional[str] = None` (line 177) but never references it in the function body. It's accepted and ignored. Previously it may have been used for logging or the prompt label, but the current implementation doesn't use it.

### Issue 7 — `get_new_company_batch` / `get_new_job_batch` produce "None-uuid" batch_ids ℹ️ advisory

Commit `027e877` added `context` parameter to prevent orphan UUIDs:

```python
bid = batch_id or f"{context}-{uuid.uuid4()}"
```

But `context` defaults to `None`. If called without either `batch_id` or `context`, the result is `"None-3f8a2b1c-..."` — a string with the literal word "None" as prefix. Currently no callers hit this path (dispatcher always passes batch_id), but it's a latent trap.

### Issue 8 — `import hashlib` inside nested function ℹ️ advisory

`_store_prompt_blocks._save` (line 144) imports `hashlib` inside the inner function body. Standard Python practice is to import at module top level. The import happens on every deterministic block save.

---

## Recommended Actions

| # | Severity | Action | Resolution |
|---|----------|--------|------------|
| 1 | Fix now | Replace `compute_batch_cost` raw SQL with `sum_cost_by_batch([batch_id])` | ✅ Fixed. Uses `database.sum_cost_by_batch([batch_id])`, private imports removed. |
| 2 | Advisory | Remove dead imports: `_add_timesheet_entry`, `ENTITY_TYPES` from agent.py | ✅ Fixed. Both removed. `sum_cost_by_batch` added. |
| 3 | Advisory | Add `logger.debug(... exc_info=True)` to the three silent except blocks in `do_task` | ✅ Fixed. All four except blocks now log with `exc_info=True`. |
| 4 | Discuss | Decide whether `run_adhoc` should accept `candidate_id`/`api_key_override`/`task_key_uuid` | ✅ Fixed. `run_adhoc` now accepts and passes all three to `send_to_anthropic`. `adhoc_test` wires them from `_resolve_adhoc`. Susan's directive: use candidate's API key when available. |
| 5 | Advisory | Consider a dedicated block type (e.g., USER_PROMPT) for user_content, or document the double-NO_CACHE convention | ✅ Documented. Inline comment in `_store_prompt_blocks` explains the intentional split. |
| 6 | Advisory | Remove dead `context` parameter from `send_to_anthropic` | ✅ Fixed. Param removed from signature and all call sites. |
| 7 | Advisory | Add a guard: `if context is None: raise ValueError(...)` | ✅ Fixed. Both `get_new_company_batch` and `get_new_job_batch` raise `ValueError` if neither `batch_id` nor `context` provided. |
| 8 | Advisory | Move `import hashlib` to top of agent.py | ✅ Fixed. Moved to module-level imports. |

---

### CR-6 — Standardize `agent_responses` array across all entity tables ✅ approved

**Current state (inconsistent):**

| Entity | `agent_responses` field? | Where AI results currently land |
|--------|--------------------------|----------------------------------|
| `company` | ✅ Native column `agent_responses TEXT DEFAULT '[]'` — parsed as JSON array on read | `roster.py` writes raw API response blobs directly into this column |
| `job` | ❌ None — AI results go into `job_data` as `*_grades`, `*_score` fields | `consult.py` calls `save_job_data(id, {task_grades: ..., task_score: ...})` |
| `candidate` | ❌ None — AI results go into `candidate_data.artifacts` | `api_candidate.py` returns result to frontend; frontend POSTs to `candidate_data` |

The ticket originally described a lightweight reference pattern for entity-level `agent_responses`:
```json
{ "task_key": "prefilter", "created_at": "<ts>", "batch_id": "<batch_id>", "entity_cost": 0.0042 }
```

**Proposed: Uniform `agent_responses` array on all three entity tables, keyed by `batch_id`, with a prefixed UUID pattern for readability.**

**Schema of each entry:**
```json
{
  "batch_id": "<task_key>-<uuid>",
  "task_key": "prefilter",
  "created_at": "2026-03-19 14:32:00",
  "entity_cost": 0.0042,
  "prompt_blocks": [
    { "type": "SYSTEM",   "id": "<agent_data_id>" },
    { "type": "CACHE_A",  "id": "<agent_data_id>" },
    { "type": "TASK",     "id": "<agent_data_id>" },
    { "type": "RESPONSE", "id": "<agent_data_id>" }
  ]
}
```

`entity_cost` = `total_cost / batch_size` — computed at write time once `total_cost` is known from timesheets.

**`batch_id` prefix convention:** All `batch_id` values generated going forward are prefixed with `<task_key>-` before the UUID for human readability as foreign keys, e.g. `prefilter-3f8a2b1c-...`.

**Changes required:**

1. **`database.py`**: Add `agent_responses TEXT DEFAULT '[]'` column to `job` and `candidate` tables (migration). Standardize the `_parse_row` helpers to JSON-parse it on read for all three. Add `append_agent_response(entity_type, entity_id, entry: dict)` helper that fetches current array, appends, and saves.
2. **`agent.py`**: After `do_task` completes and cost is computed, call `append_agent_response(entity_type, entity_id, entry)`. This is where `entity_cost = total_cost / batch_size` is calculated.
3. **`dispatcher.py`**: `batch_id` generation changes from `str(uuid.uuid4())` → `f"{task_key}-{uuid.uuid4()}"`.
4. **`api_candidate.py`** (CR-5): Same prefixed `batch_id` pattern.
5. **`roster.py`**: Replace direct `agent_responses` blob writes with the new standardized append pattern.

**batch_id is the golden ticket:** One batch_id per dispatch run, used for row-locking, state transitions, agent_data storage, entity agent_responses, dispatch_ledger, and timesheets. Dispatcher generates `f"{task_key}-{uuid}"`, passes it down through runners into `get_new_company_batch` / `get_new_job_batch` for row-locking. No orphaned UUIDs.

**Verdict:** ✅ Approved and applied.

---

### CR-4 — Add `token_size` to `agent_data` table ✅ approved

Each row in `agent_data` stores a potentially large block of text (system prompt, cache context, live content, response). Without `token_size`, there is no way to inspect token consumption per block without decompressing and estimating the content yourself.

**Proposed:** Add `token_size INTEGER` column to the `agent_data` schema, populated at write time by dividing `len(block_data)` by `CHARS_PER_TOKEN` (the same estimate used in `_assemble_blocks`).

**Files touched:** `database.py` (schema + `save_agent_data` signature), `agent.py` (`_store_prompt_blocks` + `_store_response_block` pass estimated token size).

**Risk:** Build is in-progress. The schema has already been written without this column, so we add it now (before first run) or it becomes a migration. Since we haven't committed yet, adding it now is clean.

**Verdict:** ✅ Approved and applied.

---

### CR-5 — Wire artifact Generate button through dispatch pattern ✅ approved

**Current state:** The `ArtifactEditor` component calls `POST /api/candidates/<id>/generate/<task_key>` → `api_candidate.py:generate_artifact()` → `do_task()` directly. No `batch_id` is generated, no `dispatch_ledger` entry is created, no `log_batch_id` context is set, and `agent_data` storage is therefore skipped (the `store_agent_data` path in `do_task` checks `batch_id` from `log_batch_id.get()` — which will be `None`).

**Proposed:** Modify `generate_artifact()` in `api_candidate.py` to:

1. Generate a `batch_id = str(uuid.uuid4())`.
2. Call `save_dispatch_ledger(batch_id, task_key, candidate_id, started_at, entity_type="candidate", batch_size=1)`.
3. Set `log_batch_id.set(batch_id)` before calling `do_task`, then `log_batch_id.set(None)` in a `finally` block.
4. After success, call `update_dispatch_ledger(batch_id, status="COMPLETED", total_processed=1, total_passed=1, total_cost=agent.compute_batch_cost(batch_id))`.
5. On failure, call `update_dispatch_ledger(batch_id, status="FAILED")`.
6. Return `batch_id` in the response payload so the frontend can reference it later (e.g. for the future agent_response widget).

**Entity type:** `"candidate"` — these are craft_* tasks that belong to the candidate entity.

**Files touched:** `src/ui/api/api_candidate.py` only (the `generate_artifact` endpoint). No frontend changes needed — the batch_id is additive to the existing response shape.

**No new imports needed** beyond what's already in the file (`uuid` is stdlib, `save_dispatch_ledger`, `update_dispatch_ledger`, `compute_batch_cost` to be imported from `src.data.database` and `src.core.agent`). Uses prefixed batch_id: `f"{task_key}-{uuid}"`.

**Verdict:** ✅ Approved and applied.



## Susan Note:
Ad-hoc calls are not stored, but they are run on a candidate's behalf.  Please use the context candidate's API key when calling adhoc tasks.  Only if there is somehow NO candidate, use the system API key.

