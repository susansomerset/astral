# AST-287 — Per-Agent Model Configuration
**Component:** administrator  
**Children:** — (single ticket)  
**Linear archived:** AST-287 2026-06-03  

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-03-03 16:30 | AST-287 | — | `af274c53e` | ast-287 sub1: add MODELS catalog to config, remove ASTRAL_CONFIG api block |
| 2026-03-03 16:31 | AST-287 | — | `92c12f61a` | ast-287 sub2: agent table migration, new DB functions |
| 2026-03-03 16:31 | AST-287 | — | `4bfad0d59` | ast-287 sub3: cost_calculator model-aware pricing from MODELS config |
| 2026-03-03 16:33 | AST-287 | — | `44eb86215` | ast-287 sub4: thread model params from agent record through anthropic.py |
| 2026-03-03 16:33 | AST-287 | — | `8ec9ebf41` | ast-287 sub5: API endpoints for model listing, agent update/delete |
| 2026-03-03 16:36 | AST-287 | — | `637730897` | ast-287 sub6: Manage Agents UI — model selector, delete action, cost strip |
| 2026-03-03 16:42 | AST-287 | — | `f43789ed7` | ast-287: add plan/review docs and supporting linear-import files |
| 2026-03-03 16:43 | AST-287 | merge | `1b9528a09` | Merge pull request #38 from susansomerset/chuckles/ast-287-per-agent-model-configuration |
| 2026-03-04 07:36 | AST-287 | — | `8e737c7db` | ast-287: update plan doc with Sub 7 (task phase + seq fields) |
| 2026-03-04 08:40 | AST-287 | — | `7ae115356` | ast-287: normalize TASK_CONFIG phases + sequences, reflect task renames |
| 2026-03-04 08:41 | AST-287 | merge | `b5b036c1b` | Merge pull request #39 from susansomerset/chuckles/ast-287-per-agent-model-configuration |

_`f43789ed7` also created the (still-empty) placeholder stubs `ast-283-…`, `ast-284-…`, `ast-288-…` from a Linear CSV import. Era path convention was `ui/…` (not `src/ui/…`). A follow-on ticket `ast-288` (consult uses agent model) was spun off from this plan and lives outside this folder._

## Epic — AST-287
_Archived: 2026-06-03 · Linear URL: https://linear.app/astralcareermatch/issue/AST-287/per-agent-model-configuration · Status at archive: Done · Project: Astral Administrator · Assignee: susan · Priority / estimate: High / 5_

### Original brief

Add model, temperature, and max_tokens to the agent record so each agent carries its own API call parameters. Remove the api block from ASTRAL_CONFIG entirely — these settings no longer belong in code.

**Acceptance Criteria:**

[**config.py**](<http://config.py>)** Changes:**

* Remove the `api` block from ASTRAL_CONFIG entirely
* Add a top-level `models` list to [config.py](<http://config.py>) with the following shape per entry:
  * `model_label` — human-readable name (e.g. "Haiku", "Sonnet", "Opus")
  * `model_code` — Anthropic API string (e.g. `claude-haiku-4-5-20251001`)
  * `cpm_input` — cost per million input tokens (float)
  * `cpm_output` — cost per million output tokens (float)
  * `default_temperature` — sensible default for this model (float)
  * `default_max_tokens` — sensible default for this model (int)
* Seed with current Haiku, Sonnet, and Opus models and their published pricing

[**database.py**](<http://database.py>)** / agent Table Changes:**

* ALTER agent table to add three columns:
  * `model_code` — TEXT (FK by convention to models list in config)
  * `temperature` — REAL
  * `max_tokens` — INTEGER
* `get_agent()` returns all three new fields alongside existing fields
* Schema migration adds columns to existing databases idempotently

**cost_calculator.py Changes:**

* Remove hardcoded Sonnet 4.5 pricing constants
* `calculate_cost_with_cache(usage, model_code)` — looks up cpm_input and cpm_output from config models list by model_code
* `calculate_cost(usage, model_code)` — same, simple variant
* Raises ValueError if model_code not found in config

**Manage Agents Screen (UI — Admin > Manage Agents):**

* Add model selector to agent edit form — dropdown populated from config models list
* On model selection, pre-populate temperature and max_tokens from config defaults (editable)
* Display current model, temperature, max_tokens in agent list columns
* Add delete agent action to list (row action: Delete → confirmation modal → DELETE endpoint)
* Save writes model_code, temperature, max_tokens back to agent record

**API Endpoints:**

* GET /api/admin/models — returns config models list (for dropdown population)
* PUT /api/admin/agents/:agent_id — updated to accept and save model_code, temperature, max_tokens
* DELETE /api/admin/agents/:agent_id — delete agent record

**Notes:**

* No fallback model anywhere — if an agent record is missing model_code the system should surface an error, not silently default
* Chuckles to seed existing agent records with appropriate model_code, temperature, max_tokens as part of migration

**Database:**

* agent table: ALTER to add model_code, temperature, max_tokens columns
* [database.py](<http://database.py>) module docstring updated per ASTRAL_CODE_RULES 1.1

#### Comments

_No comments._

### Plan — ast-287: Per-Agent Model Configuration

#### Overview

Move API call parameters (model, temperature, max_tokens) from the global `ASTRAL_CONFIG["api"]` block to per-agent records in the database. Each agent carries its own model configuration, eliminating the single-model assumption. A new `MODELS` list in `config.py` becomes the catalog of available models with pricing and defaults.

**Already built (relevant to this feature):**
- `agent` table with `agent_id TEXT PK`, `content TEXT`, `updated_at TIMESTAMP`
- `save_agent(agent_id, content)`, `get_agent(agent_id)`, `list_agents()` in `database.py`
- `_ensure_agent_schema()` with idempotent create (no migration logic yet)
- `ASTRAL_CONFIG["api"]` block consumed in `_send_and_parse()` in `anthropic.py`
- `cost_calculator.py` with hardcoded Sonnet 4.5 pricing
- `AgentPrompts.tsx` — Manage Agents screen with list + edit/add modals
- `admin_agents_bp` — Flask blueprint with GET list, GET single, POST create, PUT update
- Five seeded agents: `ats_expert_atlas`, `job_analyst_grace`, `gate_keeper_danny`, `400_judith_copywriter`, `X00_estelle_recruiter`

#### Design decisions

**`MODELS` is a config list, not a DB table.** Models are code-owned constants (like states or vectors). They change when Anthropic ships new models — a developer action, not an admin action. Keeping them in `config.py` avoids schema drift and keeps pricing authoritative in code.

**`model_code` on the agent record, not on agent_task.** The ticket says "each agent carries its own API call parameters." This matches the domain: an agent *is* a persona backed by a specific model. Different tasks assigned to the same agent share that agent's model settings. If we ever need per-task model overrides, that's a future enhancement — not this ticket.

**`save_agent` signature expands** to accept optional `model_code`, `temperature`, `max_tokens`. The existing `save_agent(agent_id, content)` call sites continue to work unchanged (new params default to `None` = no update on existing rows).

**`_send_and_parse` reads model params from agent record** instead of `ASTRAL_CONFIG["api"]`. The `do_task` flow already calls `_resolve_task_prompts(task_key)` which returns the agent row. We thread model_code/temperature/max_tokens from that row down to `_send_and_parse`. The `ASTRAL_CONFIG["api"]` block is removed entirely.

**No fallback.** If an agent record has `NULL` model_code, `do_task` raises ValueError. The system should not silently default — that's the whole point of this feature.

**Delete agent** is a simple hard delete. No cascade concerns — `agent_task.agent_id` is a convention reference, not a real FK. The UI will show a confirmation modal.

#### Sub 1: `MODELS` config list + remove `api` block

**Files:** `src/utils/config.py`

Add a top-level `MODELS` list after the existing config blocks, before `NAV_CONFIG`. Remove the `ASTRAL_CONFIG["api"]` block entirely.

```python
MODELS = {
    "claude-haiku-4-5": {
        "model_label": "Haiku",
        "cpm_input": 1.00,
        "cpm_output": 5.00,
        "cpm_cache_write": 1.25,
        "cpm_cache_read": 0.10,
        "default_temperature": 0.3,
        "default_max_tokens": 8192,
    },
    "claude-sonnet-4-5": {
        "model_label": "Sonnet",
        "cpm_input": 3.00,
        "cpm_output": 15.00,
        "cpm_cache_write": 3.75,
        "cpm_cache_read": 0.30,
        "default_temperature": 0.3,
        "default_max_tokens": 16000,
    },
    "claude-opus-4-6": {
        "model_label": "Opus",
        "cpm_input": 5.00,
        "cpm_output": 25.00,
        "cpm_cache_write": 6.25,
        "cpm_cache_read": 0.50,
        "default_temperature": 0.3,
        "default_max_tokens": 16000,
    },
}
```

Dict keyed by `model_code` (alias form — auto-upgrades with Anthropic releases). Each value has `model_label`, `cpm_input`, `cpm_output`, `cpm_cache_write`, `cpm_cache_read`, `default_temperature`, `default_max_tokens`.

Add helper:

```python
def get_model(model_code: str) -> dict:
    """Return model config by model_code. Raises ValueError if not found."""
    m = MODELS.get(model_code)
    if not m:
        raise ValueError(f"Unknown model_code {model_code!r}. Valid: {list(MODELS.keys())}")
    return m
```

Remove `ASTRAL_CONFIG["api"]` block (lines 504–509). Update the module docstring: add `MODELS` and remove "API" from the `ASTRAL_CONFIG` description line.

Update `ASTRAL_CODE_RULES.md`: add `MODELS` to section 2.1 config blocks, remove "API settings" from the ASTRAL_CONFIG bullet, clarify section 3.3 that utils modules may import from each other (intra-layer). *(Historical — `docs/ASTRAL_CODE_RULES.md` was later deleted in `44b7d102b`, 2026-09-10.)*

#### Sub 2: Agent table migration + database functions

**Files:** `src/data/database.py`

##### Schema migration

Add three columns to `_ensure_agent_schema()` migration block (same pattern as company's `batch_created_at` migration): `model_code TEXT`, `temperature REAL`, `max_tokens INTEGER`.

After the CREATE TABLE block, add idempotent ALTER:

```python
cols = {row[1] for row in conn.execute("PRAGMA table_info(agent)").fetchall()}
for col_name, col_def in [
    ("model_code", "TEXT"),
    ("temperature", "REAL"),
    ("max_tokens", "INTEGER"),
]:
    if col_name not in cols:
        try:
            conn.execute(f"ALTER TABLE agent ADD COLUMN {col_name} {col_def}")
            conn.commit()
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e).lower():
                raise
```

##### Seed existing agents

After the column migration, seed existing agents that have NULL model_code with Sonnet defaults:

```python
conn.execute("""
    UPDATE agent SET model_code = 'claude-sonnet-4-5',
                     temperature = 0.3,
                     max_tokens = 16000
    WHERE model_code IS NULL
""")
conn.commit()
```

This runs inside `_ensure_agent_schema` so it fires once on first connection after deploy.

##### `save_agent` signature expansion

Current: `save_agent(agent_id: str, content: str)`. New: `save_agent(agent_id: str, content: str, *, model_code: Optional[str] = None, temperature: Optional[float] = None, max_tokens: Optional[int] = None)`.

On INSERT: use provided values (or NULL if not provided — seeding migration covers existing rows). On UPDATE: only set columns that are not None (same partial-update pattern as `save_job`). The `content` param continues to always update (existing behavior).

##### `update_agent` — new function

Add `update_agent(agent_id: str, **kwargs)` following the `update_company` pattern with an allowlist: `_UPDATE_AGENT_ALLOWED = frozenset({"content", "model_code", "temperature", "max_tokens"})`. This is what the PUT endpoint will call to update individual fields without requiring all fields.

##### `delete_agent` — new function

```python
def delete_agent(agent_id: str) -> bool:
    """Delete an agent by agent_id. Returns True if deleted, False if not found."""
```

Simple DELETE WHERE. Returns `cur.rowcount > 0`.

##### `count_agent_task_refs` — new function

```python
def count_agent_task_refs(agent_id: str) -> int:
    """Return number of agent_task rows referencing this agent_id."""
```

`SELECT COUNT(*) FROM agent_task WHERE agent_id = ?`. Used by the API to gate delete eligibility and by `list_agents` to populate `task_count` in the list response.

##### `get_agent` / `list_agents` changes

`get_agent` already does `SELECT *` — the new columns come back automatically. `list_agents` currently selects only `agent_id, LENGTH(content), updated_at`. Expand to include `model_code, temperature, max_tokens`, and add a `task_count` column via a correlated subquery:

```sql
SELECT agent_id, LENGTH(content) AS content_length, model_code, temperature, max_tokens, updated_at,
       (SELECT COUNT(*) FROM agent_task WHERE agent_task.agent_id = agent.agent_id) AS task_count
FROM agent ORDER BY agent_id
```

##### Module docstring update

```
- agent    — Agent: agent_id TEXT PK, content TEXT, model_code TEXT, temperature REAL, max_tokens INTEGER, updated_at TIMESTAMP.
```

#### Sub 3: `cost_calculator.py` — model-aware pricing

**Files:** `src/utils/cost_calculator.py`

Remove hardcoded Sonnet 4.5 pricing constants. Both functions gain a `model_code` parameter.

```python
from src.utils.config import MODELS

def calculate_cost(usage, model_code: str) -> float:
    """Calculate cost in USD. Looks up pricing from MODELS by model_code."""
    m = MODELS.get(model_code)
    if not m:
        raise ValueError(f"Unknown model_code for cost calc: {model_code!r}")
    input_cost = (usage.input_tokens / 1_000_000) * m["cpm_input"]
    output_cost = (usage.output_tokens / 1_000_000) * m["cpm_output"]
    return input_cost + output_cost

def calculate_cost_with_cache(usage, model_code: str) -> float:
    """Calculate cost with prompt caching using explicit cache pricing from MODELS."""
    m = MODELS.get(model_code)
    if not m:
        raise ValueError(f"Unknown model_code for cost calc: {model_code!r}")
    regular_input_cost = (usage.input_tokens / 1_000_000) * m["cpm_input"]
    cache_read_cost = (getattr(usage, 'cache_read_input_tokens', 0) / 1_000_000) * m["cpm_cache_read"]
    cache_write_cost = (getattr(usage, 'cache_creation_input_tokens', 0) / 1_000_000) * m["cpm_cache_write"]
    output_cost = (usage.output_tokens / 1_000_000) * m["cpm_output"]
    return regular_input_cost + cache_read_cost + cache_write_cost + output_cost
```

**Note:** Utils modules are pure (no imports from core, data, external) but may import from each other within the utils layer. `cost_calculator.py` importing `MODELS` from `config.py` is intra-utils — the alternative would be hardcoding pricing, which is worse. Update ASTRAL_CODE_RULES section 3.3 to clarify: "utils: nothing outside utils (intra-utils imports allowed)".

##### Caller update

`src/external/anthropic.py` line 733 currently calls `calculate_cost_with_cache(usage)`. Update to `calculate_cost_with_cache(usage, model_code)` where `model_code` comes from the agent record threaded through `_send_and_parse`.

#### Sub 4: `anthropic.py` — read model params from agent record

**Files:** `src/external/anthropic.py`

##### `_send_and_parse` signature change

Add `model_code`, `temperature`, `max_tokens` as required parameters:

```python
async def _send_and_parse(
    content_blocks, *,
    model_code: str,
    temperature: float,
    max_tokens: int,
    context=None, response_format=None, prompt_label="(unknown)",
    enable_web_search=False, api_key_override=None,
) -> Dict[str, Any]:
```

Remove the `ASTRAL_CONFIG.get("api")` lookup (lines 686–688) and the `api_config[...]` references (lines 700–702). Replace with direct use of the params:

```python
api_kwargs = {
    "model": model_code,
    "max_tokens": max_tokens,
    "temperature": temperature,
    "messages": [{"role": "user", "content": content_blocks}],
}
```

Update `calculate_cost_with_cache(usage)` call to `calculate_cost_with_cache(usage, model_code)`.

##### `do_task` threading

`do_task` already calls `_resolve_task_prompts(task_key)` which returns `(agent_row, agent_task_row)`. The agent_row now carries `model_code`, `temperature`, `max_tokens`. Extract and validate before calling `_fetch_response_from_content`. No magic numbers — fall back to config defaults for the model if temperature/max_tokens are NULL:

```python
from src.utils.config import get_model

agent_model_code = agent_row.get("model_code")
if not agent_model_code:
    raise ValueError(f"Agent '{agent_row.get('agent_id')}' has no model_code configured")
model_config = get_model(agent_model_code)
agent_temperature = agent_row.get("temperature") or model_config["default_temperature"]
agent_max_tokens = agent_row.get("max_tokens") or model_config["default_max_tokens"]
```

Thread these into `_fetch_response_from_content` and on to `_send_and_parse`.

##### `_fetch_response_from_content` signature

Add the same three params, pass through to `_send_and_parse`.

##### Remove `ASTRAL_CONFIG["api"]` import

The only consumer of `ASTRAL_CONFIG["api"]` is `_send_and_parse`. Once replaced, remove the import of `ASTRAL_CONFIG` from anthropic.py if no other references remain. Actually, `ASTRAL_CONFIG` is still used for `data_dir` in `_resolve_file_path` — so the import stays, but the `"api"` key is no longer consumed.

#### Sub 5: API endpoints

**Files:** `src/ui/api/admin_agents.py`, `src/ui/server.py`

##### `GET /api/admin/agents/models`

New endpoint returning the `MODELS` config for dropdown population and read-only cost display. UI → utils is allowed; the data lives in config.

```python
from src.utils.config import MODELS

@admin_agents_bp.route("/models")
@require_auth
def list_models():
    result = [
        {"model_code": code, **info}
        for code, info in MODELS.items()
    ]
    return jsonify(result)
```

Response includes all MODELS fields per entry. The UI displays the cost metrics read-only when a model is selected, and uses the defaults to pre-populate temperature/max_tokens.

**Route ordering note:** This must be registered before the `/<agent_id>` route to avoid Flask matching "models" as an agent_id. Move the `/models` route above the `/<agent_id>` route in the file.

##### `PUT /api/admin/agents/<agent_id>` — update

Already exists. Expand to accept and save `model_code`, `temperature`, `max_tokens`:

```python
@admin_agents_bp.route("/<agent_id>", methods=["PUT"])
@require_auth
def update_agent(agent_id):
    body = request.get_json(silent=True) or {}
    database.update_agent(agent_id, **{
        k: body[k] for k in ("content", "model_code", "temperature", "max_tokens")
        if k in body
    })
    return jsonify(database.get_agent(agent_id))
```

##### `DELETE /api/admin/agents/<agent_id>`

New endpoint. Checks task_count first — refuses if the agent is still referenced:

```python
@admin_agents_bp.route("/<agent_id>", methods=["DELETE"])
@require_auth
def delete_agent(agent_id):
    if not database.get_agent(agent_id):
        return jsonify({"error": f"Agent not found: {agent_id}"}), 404
    if database.count_agent_task_refs(agent_id) > 0:
        return jsonify({"error": f"Agent '{agent_id}' is still assigned to tasks — unassign first"}), 409
    database.delete_agent(agent_id)
    return jsonify({"deleted": agent_id})
```

No changes to `server.py` — the blueprint is already registered.

#### Sub 6: Manage Agents UI

**Files:** `src/ui/frontend/src/pages/Admin/AgentPrompts.tsx`, `src/ui/frontend/src/App.css`

##### List columns

Add model info to the list. New columns after `agent_id`: Agent ID (`agent_id`), Model (`model_code`), Temp (`temperature`), Max Tok (`max_tokens`), Tasks (`task_count`), Chars (`content_length`), Updated (`updated_at`) — all sortable. Display `model_code` using the `model_label` from config (fetched via `/api/admin/agents/models` on load) for readability. Fallback to raw code if label not found.

##### Edit modal changes

When opening the edit modal for an agent:
1. Fetch the models list from `GET /api/admin/agents/models` (cache on first load)
2. Show a `<select>` dropdown for Model, populated from the models list, current value from agent record
3. On model selection, display read-only cost metrics for the selected model: input $/M, output $/M, cache write $/M, cache read $/M
4. Show `temperature` as a number input (step 0.1)
5. Show `max_tokens` as a number input
6. On model selection change, pre-populate temperature and max_tokens from the selected model's defaults (but keep them editable — don't overwrite if user already tweaked)
7. Keep the existing System Prompt Content textarea

Save sends `content`, `model_code`, `temperature`, `max_tokens` in the PUT body.

##### Add modal changes

Same model/temperature/max_tokens fields. Model defaults to the first entry in the models list (or empty — require selection).

##### Delete action

`list_agents` returns `task_count` per agent. The Delete button is rendered disabled (with a tooltip "Agent is assigned to N tasks") when `task_count > 0`, enabled when `task_count === 0`. On click (enabled only): confirmation modal → `DELETE /api/admin/agents/{agent_id}` → reload list + toast. The API also enforces the same check server-side (409 if task_count > 0), so the guard is defense-in-depth.

##### Styles

Add any needed styles to `App.css` — likely minimal since the edit modal already has field styling via `dep-field` / `dep-input` classes.

#### Sub 7: Task phase + sequence fields (Manage Tasks UI) — _added post-plan_

**Files:** `src/utils/config.py`, `src/ui/api/admin_tasks.py`, `src/ui/frontend/src/pages/Admin/TaskPrompts.tsx`

Add `phase` (string) and `seq` (integer) to every `TASK_CONFIG` entry so tasks can be sorted by execution phase and order. These fields are config-owned and read-only in the UI — managed directly in `config.py`. Each task gets `phase` and `seq` as the first two keys in its config dict. Phases: `onboard`, `roster`, `tracker`, `consult`. Sequence numbers leave gaps for future inserts without renumbering.

| task_key | phase | seq |
|----------|-------|-----|
| parse_resume | onboard | 1 |
| bootstrap_candidate | onboard | 2 |
| prefilter_company | roster | 1 |
| find_job_site | roster | 3 |
| vet_job_list | roster | 4 |
| select_culture_pages | roster | 5 |
| parse_job_list | roster | 6 |
| qualify_job_listings | tracker | 3 |
| evaluate_jd | tracker | 4 |
| grade_get | consult | 1 |
| grade_do | consult | 2 |
| grade_like | consult | 3 |

`admin_tasks.py` merges `phase` + `seq` from `TASK_CONFIG` into both `list_tasks` and `get_task` responses via a shared `_enrich()` helper (falls back to `None` if a task key has no config entry). `TaskPrompts.tsx`: Phase and Seq added as the first two sortable columns; read-only phase/seq displayed at the top of the edit modal (no inputs). No database changes, no write endpoints, no changes to `save_agent_task` or `update_task`.

#### File change summary (from plan, updated)

| File | Change type |
|------|-------------|
| `src/utils/config.py` | Remove `api` block, add `MODELS` dict + `get_model()` helper, add `phase`/`seq` to all `TASK_CONFIG` entries, update module docstring |
| `src/data/database.py` | Migrate agent table (3 cols), seed existing agents, expand `save_agent`, add `update_agent`, add `delete_agent`, update `list_agents` SELECT, update module docstring |
| `src/utils/cost_calculator.py` | Add `model_code` param to both functions, remove hardcoded pricing, import `MODELS` from config |
| `src/external/anthropic.py` | Thread model params from agent record through `do_task` → `_fetch_response_from_content` → `_send_and_parse`, remove `ASTRAL_CONFIG["api"]` usage |
| `src/ui/api/admin_agents.py` | Add `GET /models`, expand `PUT`, add `DELETE` |
| `src/ui/api/admin_tasks.py` | Merge `phase`/`seq` from `TASK_CONFIG` into list and get responses |
| `src/ui/frontend/src/pages/Admin/AgentPrompts.tsx` | Add model/temp/max_tokens to list + edit + add, add delete action |
| `src/ui/frontend/src/pages/Admin/TaskPrompts.tsx` | Add Phase + Seq sortable columns, read-only display in edit modal |
| `src/ui/frontend/src/App.css` | Danger button, cost strip, row-actions styles |
| `docs/ASTRAL_CODE_RULES.md` | Add `MODELS` to section 2.1, remove "API settings" from ASTRAL_CONFIG description, clarify section 3.3 utils intra-layer imports |

#### Resolved questions

1. **Cache pricing** — Added explicit `cpm_cache_write` and `cpm_cache_read` fields to each MODELS entry. `cost_calculator.py` uses these directly instead of deriving from ratios.
2. **Seed model** — All existing agents seed to `claude-sonnet-4-5` with default temperature 0.3 and max_tokens 16000.
3. **Model codes** — Use alias form (`claude-sonnet-4-5`, not `claude-sonnet-4-5-20250929`). Auto-upgrades with Anthropic releases as long as pricing holds.

### Code review — Chuckles (6 commits, sub1–sub6)

**Overall Assessment: Ship it.** The implementation matches the plan closely, the commit sequence is logical, and there are no obvious correctness bugs. A few issues worth flagging — two real (one small functional gap, one style consistency miss), the rest observations or follow-up suggestions.

#### Sub 1 — `MODELS` catalog + remove `api` block (`config.py`)

**Clean.** MODELS dict keyed by `model_code` alias, `get_model()` helper raises `ValueError` on unknown code. The `api` block removal is complete and the module docstring update is accurate. **Observation:** `get_model()` uses `MODELS.get(model_code)` and checks for falsy, which would also raise on a hypothetically empty-dict model entry. `if m is None` would be more precise (low priority).

#### Sub 2 — Agent table migration + DB functions (`database.py`)

**Solid migration pattern.** The idempotent `ALTER TABLE` with `PRAGMA table_info` + duplicate-column catch mirrors the company `batch_created_at` pattern. Seeding existing agents to Sonnet defaults on first connection is correct. A concern about `_agent_schema_ensured` being set only in the new-table path was re-checked and withdrawn — the flag is set after both branches, so it fires in both cases. **Good catch in `list_agents`:** calling `_ensure_agent_task_schema(conn)` before the correlated subquery prevents a schema-not-yet-created crash on a fresh DB. **`update_agent` silently drops unknown kwargs** — by design (the allowlist is the point), but the caller gets no signal; acceptable for an internal function.

#### Sub 3 — `cost_calculator.py`

**Clean reduction.** Hardcoded Sonnet 4.5 constants gone; both functions now accept `model_code`. The `getattr(usage, "cache_read_input_tokens", 0) or 0` double-safety pattern is smart. **Style note:** `calculate_cost` uses a backslash line continuation while `calculate_cost_with_cache` uses parenthesized multi-line; the parenthesized form is preferred in this codebase.

#### Sub 4 — `anthropic.py`

**The critical path.** Highest-risk change and it looks right. **`do_task` fallback logic** uses `if agent_row.get("temperature") is not None` correctly — important because `temperature=0.0` is a valid value and falsy. Same for `max_tokens`. **`_send_and_parse` guard** uses `if not model_code:` — also raises on empty string `""`, which is correct. **`_fetch_response` (legacy path) defaults** hardcode `"claude-sonnet-4-5"` string literal three times; a single `_DEFAULT_MODEL` constant would make this one edit instead of three. Low priority for a legacy path.

#### Sub 5 — API endpoints (`admin_agents.py`)

**Route ordering is correct** — `/models` registered before `/<agent_id>`, with a comment documenting why. **`create_agent` temperature/max_tokens** are passed through without type coercion; `request.get_json()` gives Python `float`/`int` for numeric JSON so this is fine, but a string `"0.3"` from curl would be stored as a string and blow up downstream. A `float()/int()` cast at the boundary would be robust. **`update_agent` does an extra `get_agent` round-trip** for the 404 check; readability is better this way, minor.

#### Sub 6 — Manage Agents UI (`AgentPrompts.tsx`, `ListPage.tsx`, `App.css`)

- `renderedAgents` replaces `model_code` with `model_label` for display, so a clicked row's `model_code` is the label not the code — but `openEdit` looks up the original agent from `agents` (`agents.find(a => a.agent_id === row.agent_id) ?? row`), so this is handled. The `?? row` fallback is benign.
- `rowActions` delete button uses `agent?.task_count ?? 1` as the disabled guard — if the agent isn't found (shouldn't happen), default to `1` keeps the button disabled. Correct defensive choice.
- `applyModelDefaults` **always overwrites** temp/max_tokens on model-dropdown change, even if the user already edited them — a minor deviation from the plan's "don't overwrite if user already tweaked". In practice fine (changing model is intentional).
- `eslint-disable-next-line react-hooks/exhaustive-deps` suppresses the missing `addModel` dependency in the models-fetch `useEffect` (run once on mount). Correct, but the comment should say *why*.
- `ModelFields` is a plain function, not `React.FC` with `memo` — fine at this scale.
- `ListPage.tsx` `rowActions` prop typed `(row: T) => ReactNode`; `onClick={e => e.stopPropagation()}` on the `<td>` prevents the delete click bubbling to `onRowClick`. Correct.

#### Cross-cutting concerns

- **No tests added.** The plan didn't mention tests and there are none in the existing codebase pattern for these layers — not a gap relative to the standard.
- **`MODELS` pricing is hardcoded** from Anthropic's published rates. Alias model codes auto-upgrade on Anthropic's side; pricing changes are a manual code update — a documented human process dependency.
- **`agent_task.agent_id` is a convention reference, not a real FK.** Delete guard is enforced in the API layer (`count_agent_task_refs`), not at the DB level. If an agent is deleted via direct DB access, orphaned `agent_task` rows won't cascade. Fine for the current operational model.

#### Summary of actionable items

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | Low | `cost_calculator.py` | `calculate_cost` return uses backslash continuation; prefer parenthesized form for consistency |
| 2 | Low | `anthropic.py` `_fetch_response` | `"claude-sonnet-4-5"` literal appears 3x in the legacy default block — a single constant would be cleaner |
| 3 | Low | `admin_agents.py` `create_agent` | `temperature`/`max_tokens` from JSON not type-coerced; string input would store silently and fail at call time |
| 4 | Note | `AgentPrompts.tsx` `useEffect` | `eslint-disable` comment should explain the intent |
| 5 | Note | `AgentPrompts.tsx` `applyModelDefaults` | Overwrites temp/max_tokens on every model change (minor spec deviation — likely desired behavior anyway) |

None of these are blockers. Items 1–3 are minor polish; items 4–5 are informational.

### Files changed (plan vs actual)

Era path convention was `ui/…`. Plan "File change summary" → actual across sub1–sub6 + the post-plan Sub 7 work (`8e737c7db` plan doc, `7ae115356` config normalize).

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` | Remove `api` block, add `MODELS` + `get_model()`, add `phase`/`seq` to `TASK_CONFIG`, docstring | `af274c53e` (sub1); `7ae115356` (phase/seq normalize) |
| ✓ | `src/data/database.py` | Agent table migration (3 cols), seed, `save_agent` expand, `update_agent`, `delete_agent`, `count_agent_task_refs`, `list_agents` SELECT, docstring | `92c12f61a` |
| ✓ | `src/utils/cost_calculator.py` | `model_code` param on both functions, remove hardcoded pricing, import `MODELS` | `4bfad0d59` |
| ✓ | `src/external/anthropic.py` | Thread model params `do_task` → `_fetch_response_from_content` → `_send_and_parse`; drop `ASTRAL_CONFIG["api"]` | `44eb86215` |
| ✓ | `src/ui/api/admin_agents.py` | Add `GET /models`, expand `PUT`, add `DELETE` | `8ec9ebf41` (`ui/api/…`) |
| ⚠ not touched | `src/ui/api/admin_tasks.py` | Sub 7 — merge `phase`/`seq` into list/get responses | — (not in these commits; config carries phase/seq) |
| ✓ | `src/ui/frontend/src/pages/Admin/AgentPrompts.tsx` | Sub 6 — model/temp/max_tokens in list + edit + add; delete action | `637730897` (`ui/frontend/…`) |
| ⚠ not touched | `src/ui/frontend/src/pages/Admin/TaskPrompts.tsx` | Sub 7 — Phase + Seq columns, read-only modal display | — (not in these commits) |
| ✓ | `src/ui/frontend/src/App.css` | Danger button, cost strip, row-actions styles | `637730897` |
| + unplanned | `src/ui/frontend/src/components/ListPage.tsx` | — | `637730897` — `rowActions` prop |
| + unplanned | `scripts/call_anthropic.py` | — | `44eb86215` — legacy caller passes model params |
| ✗ do-not-edit | `docs/ASTRAL_CODE_RULES.md` | Post-ship: §2.1 `MODELS`, §3.3 intra-utils imports | `af274c53e` (touched — small edit; file since deleted `44b7d102b`) |
| | _plan/review + linear-import docs_ | — | `ast-287-…-{plan,review}.md`, `docs/linear-imports/{features,model_issues}.csv`, ast-283/284/288 stubs (`f43789ed7` `8e737c7db`) |

_Implementation detail may live in git history on `origin/dev`._
