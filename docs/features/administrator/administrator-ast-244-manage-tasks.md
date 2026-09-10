# AST-244 — Manage Tasks
**Component:** administrator  
**Children:** AST-258, AST-259, AST-260, AST-261, AST-262 (documented inline; no per-ticket commit trail)  
**Linear archived:** AST-244 2026-06-03  

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-03-02 11:52 | AST-244 | — | `a79b75223` | Implement agent task management features |
| 2026-03-02 12:13 | AST-244 | — | `bad867c32` | Enhance task handling and logging in Anthropic integration |
| 2026-03-02 12:14 | AST-244 | merge | `88f51521d` | Merge pull request #31 from susansomerset/chuckles/ast-244-manage-tasks |
| 2026-03-02 12:36 | AST-244 | — | `99440bcca` | Add preview functionality for task prompts |
| 2026-03-02 12:48 | AST-244 | — | `66bd6ab7d` | Refactor prompt handling and enhance candidate preview functionality |
| 2026-03-02 12:48 | AST-244 | — | `962b39372` | Remove candidate context data shapes, context for artifacts, and candidate-related documentation files to streamline project structure |
| 2026-03-02 12:49 | AST-244 | merge | `bf3f45351` | Merge pull request #32 from susansomerset/chuckles/ast-244-manage-tasks |

_Pre-`verb(AST-NNN)` era: feature commits do not name the ticket in the subject; they are reachable via the two named PR merges. PR #32 also bundled a large `docs/old_docs → docs/z-old_docs` cleanup unrelated to this ticket. Path convention was `ui/…`. Sub-issue tickets AST-258–262 have no individual commits (their Linear status stayed "Backlog" in the CSV import even though the parent shipped)._

## Epic — AST-244
_Archived: 2026-06-03 · Linear URL: https://linear.app/astralcareermatch/issue/AST-244/manage-tasks · Status at archive: Done · Project: Astral Administrator · Assignee: susan · Priority / estimate: High / 8_

### Original brief

New admin screen to manage task definitions and their associated prompt content. Tasks are defined in CONFIG_TASKS in [config.py](<http://config.py>) — the UI renders from that list. The agent_task table stores prompt content for each task. [anthropic.py](<http://anthropic.py>) fetches from agent_task and agent tables at runtime instead of AGENT_CONFIG and file system.

**Acceptance Criteria:**

[**config.py**](<http://config.py>)** Changes:**

* Replace AGENT_CONFIG with CONFIG_TASKS — task key is the index, each entry contains:
  * `response_schema` — dict (programmatic contract, stays in code)
  * `vectors` — list (grading vectors, stays in code)
  * `grading_mode` — string
  * `requires_candidate_key` — bool
  * `trigger_state` — string (the input state this task processes, used by Dispatcher)
* Add `get_task_keys()` — returns list of all task keys for UI rendering
* Add `stringify_response_schema(task_key)` — returns formatted string of response_schema for injection as `{$RESPONSE_SCHEMA}` token in prompt content

`agent_task` Table (new):

* `task_key` — PK, matches CONFIG_TASKS key exactly
* `agent_id` — FK to agent table (nullable until assigned)
* `user_prompt` — TEXT (never-cached user prompt template)
* `cache_prompt` — TEXT (cacheable content block template)
* `nocache_prompt` — TEXT (uncached supporting content template)
* `updated_at` — TIMESTAMP

**Startup Sync:**

* On app startup, compare CONFIG_TASKS keys against agent_task rows
* Any key in CONFIG_TASKS without a row gets a blank agent_task record created automatically
* Surfaces in UI as unconfigured task (all slots empty/red)

**Manage Tasks Screen (UI — Admin > Manage Tasks):**

* ListPage driven by CONFIG_TASKS keys (via get_task_keys())
* Columns: task_key, agent (agent_id or '⚠️ Not set'), user char count, cache char count, nocache char count — all with green/red coverage indicators
* Row action: Edit → tabbed modal with four tabs:
  * **System** — dropdown of existing agents from agent table (select to assign agent_id)
  * **User** — large textarea for user_prompt
  * **Cache** — large textarea for cache_prompt
  * **NoCache** — large textarea for nocache_prompt
* Save commits all four fields to agent_task record

[**anthropic.py**](<http://anthropic.py>)** Changes (prompt assembly refactor):**

* `do_task` fetches agent_task record by task_key from database
* Resolves agent_id → fetches system prompt content from agent table
* Token resolution pass over all content blocks:
  * Candidate tokens (e.g. `{$FNAME}`, `{$LNAME}`, `{$CANDIDATE_UPSHOT}`) resolved from ctx.candidate_data
  * Config tokens (e.g. `{$RESPONSE_SCHEMA}`) resolved via stringify_response_schema(task_key)
* Assembles prompt identically to current structure — same output shape, different source
* Falls back to existing file-based assembly if no agent_task record found (migration safety, remove after cutover)
* [consult.py](<http://consult.py>) requires no changes — interface to do_task unchanged

**API Endpoints:**

* GET /api/admin/tasks — list all tasks with coverage status
* GET /api/admin/tasks/:task_key — get full agent_task record
* PUT /api/admin/tasks/:task_key — save updated content
* GET /api/admin/agents/list — lightweight agent list for dropdown

**Notes:**

* Seed script to migrate existing task prompt .txt files and AGENT_CONFIG entries into agent_task table
* Token resolution is runtime only — admin edits raw templates, never sees resolved content in UI

**Database:**

* agent_task table: CREATE TABLE as above
* [database.py](<http://database.py>) module docstring updated per ASTRAL_CODE_RULES 1.1

#### Comments

_No comments._

### Files changed (plan vs actual)

Sub-issue plans → actual across PRs #31 / #32. Era path convention `ui/…`.

| | file | planned (sub) | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` | 258 — replace `AGENT_CONFIG` with `CONFIG_TASKS` (code-owned fields only), `get_task_keys()`, `stringify_response_schema()`, `TOKEN_SOURCES` mapping (`candidate` / `config` / `company` source types); update all `AGENT_CONFIG` references | `a79b75223` `bad867c32` `66bd6ab7d` (551 lines churned) |
| ✓ | `src/data/database.py` | 259 — `agent_task` table (`task_key` PK, `agent_id` FK nullable, `user_prompt`, `cache_prompt`, `nocache_prompt`, `updated_at`), `save_agent_task` / `get_agent_task` / `list_agent_tasks`, startup sync auto-creating blank rows for missing keys, docstring | `a79b75223` |
| ✓ | `src/external/anthropic.py` | 260 — `do_task` DB-first prompt assembly: fetch `agent_task` by key, resolve `agent_id` → agent content, generic `{$TOKEN}` resolution via `TOKEN_SOURCES` (dot-path into ctx for `candidate`, named resolver for `config`, `company` designed-not-wired), unresolved tokens left as-is, file-based fallback when no row | `a79b75223` `bad867c32` `66bd6ab7d` (489 lines churned) |
| ✓ | `src/core/consult.py` | 260 — plan: "requires no changes"; minor touch only | `a79b75223` `66bd6ab7d` |
| ✓ | `src/ui/api/admin_tasks.py` (new) | 261 — `admin_tasks_bp` (`/api/admin/tasks`), GET list (coverage status) / GET one / PUT, all `@require_auth`; `GET /api/admin/agents/list` lightweight dropdown | `a79b75223` |
| ✓ | `src/ui/api/admin_agents.py` | 261 — `agents/list` lightweight endpoint | `a79b75223` |
| ✓ | `src/ui/server.py` | 261 — register blueprint | `a79b75223` |
| ⚠ not touched | `src/ui/frontend/src/routes.tsx` | 261 — nav rename `Task Prompts` → `Manage Tasks`, route path | — (not in these commits) |
| ✓ | `src/ui/frontend/src/pages/Admin/TaskPrompts.tsx` | 262 — de-stub into Manage Tasks screen: ListPage from `get_task_keys()`, coverage indicators, tabbed edit modal (System/User, Cache, NoCache), save all four fields; `99440bcca` adds prompt-preview | `a79b75223` `99440bcca` `66bd6ab7d` |
| + unplanned | `scripts/migrations/seed_agent_tasks.py` (new) | (brief "Notes" — seed script) | `a79b75223` |
| ✗ do-not-edit | `docs/old_docs/**` → `docs/z-old_docs/**` | — bundled doc-tree cleanup, unrelated to this ticket | `962b39372` (PR #32) |

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-258 — CONFIG_TASKS refactor and TOKEN_SOURCES in config.py
_Linear: https://linear.app/astralcareermatch/issue/AST-258/config-tasks-refactor-and-token-sources-in-configpy · Status: Backlog (stale — shipped with parent) · Priority: High · Assignee: Unassigned · Labels: subissue · Project: Astral Administrator · Created 2026-03-02 · Updated 2026-03-02_

#### What this implements

**Scope:** Replace AGENT_CONFIG with CONFIG_TASKS and add config-driven token resolution mapping.

* Replace `AGENT_CONFIG` with `CONFIG_TASKS` — task key is the index, each entry keeps only code-owned fields:
  * `response_schema` (dict), `vectors` (list), `grading_mode` (string), `requires_candidate_key` (bool), `trigger_state` (string)
* Prompt content fields (system_prompt, task_prompt, cached_blocks, uncached_blocks) removed — now live in agent_task table
* Add `get_task_keys()` — returns list of all task keys for UI rendering
* Add `stringify_response_schema(task_key)` — returns formatted string for `{$RESPONSE_SCHEMA}` token
* Add `TOKEN_SOURCES` mapping — config-driven token-to-data-path definitions:
  * Each token maps to a source type and resolution path
  * Source types: `candidate` (dot-path into candidate dict), `config` (named resolver function), `company` (future — dot-path into company_data, designed for but not yet wired)
  * Adding new tokens is a config change, not a code change
* Update all references to `AGENT_CONFIG` across codebase ([anthropic.py](<http://anthropic.py>), [consult.py](<http://consult.py>), etc.)

**Layer:** src/utils/config.py, all files importing AGENT_CONFIG

#### Files changed (plan vs actual) _(no per-ticket commit trail — folded into the epic table above)_

### AST-259 — agent_task table, database functions, and startup sync
_Linear: https://linear.app/astralcareermatch/issue/AST-259/agent-task-table-database-functions-and-startup-sync · Status: Backlog (stale — shipped with parent) · Priority: High · Assignee: Unassigned · Labels: subissue · Project: Astral Administrator · Created 2026-03-02 · Updated 2026-03-02_

#### What this implements

**Scope:** Create agent_task table and CRUD functions with automatic sync on startup.

* CREATE TABLE agent_task: `task_key` TEXT PK (matches CONFIG_TASKS key), `agent_id` TEXT FK to agent (nullable until assigned), `user_prompt` TEXT, `cache_prompt` TEXT, `nocache_prompt` TEXT, `updated_at` TIMESTAMP
* Database functions: `save_agent_task(task_key, ...)`, `get_agent_task(task_key)`, `list_agent_tasks()`
* Startup sync: compare CONFIG_TASKS keys against agent_task rows; auto-create blank records for missing keys (surfaces in UI as unconfigured/red)
* Update [database.py](<http://database.py>) module docstring per ASTRAL_CODE_RULES 1.1

**Layer:** src/data/database.py

#### Files changed (plan vs actual) _(no per-ticket commit trail — folded into the epic table above)_

### AST-260 — anthropic.py — DB-first prompt assembly and generic token resolver
_Linear: https://linear.app/astralcareermatch/issue/AST-260/anthropicpy-db-first-prompt-assembly-and-generic-token-resolver · Status: Backlog (stale — shipped with parent) · Priority: High · Assignee: Unassigned · Labels: subissue · Project: Astral Administrator · Created 2026-03-02 · Updated 2026-03-02_

#### What this implements

**Scope:** Refactor do_task to fetch prompt content from DB and resolve merge tokens generically via TOKEN_SOURCES.

* `do_task` fetches agent_task record by task_key from database
* Resolves agent_id → fetches system prompt content from agent table
* Generic token resolution: regex finds all `{$TOKEN}` patterns in prompt text, looks each up in `TOKEN_SOURCES` from config, resolves value from the mapped source:
  * `candidate` source: dot-path walk into ctx (the candidate dict on the raft)
  * `config` source: calls named resolver function (e.g. `stringify_response_schema`)
  * `company` source: dot-path walk into company_data (designed for, not yet wired)
  * Unresolved tokens left as-is (no crash on unknown tokens)
* Assembles prompt identically to current shape — same output, different source
* Falls back to existing file-based assembly if no agent_task record found (migration safety)
* [consult.py](<http://consult.py>) requires no changes — do_task interface unchanged

**Layer:** src/external/anthropic.py

#### Files changed (plan vs actual) _(no per-ticket commit trail — folded into the epic table above)_

### AST-261 — API endpoints and nav rename
_Linear: https://linear.app/astralcareermatch/issue/AST-261/api-endpoints-and-nav-rename · Status: Backlog (stale — shipped with parent) · Priority: High · Assignee: Unassigned · Labels: subissue · Project: Astral Administrator · Created 2026-03-02 · Updated 2026-03-02_

#### What this implements

**Scope:** Create API blueprint for task admin and rename nav item.

* New Blueprint with url_prefix="/api/admin/tasks", registered in ui/server.py
* Endpoints (all @require_auth):
  * GET /api/admin/tasks — list all tasks with coverage status (agent set, prompt char counts)
  * GET /api/admin/tasks/:task_key — get full agent_task record
  * PUT /api/admin/tasks/:task_key — save updated content (agent_id, user_prompt, cache_prompt, nocache_prompt)
* GET /api/admin/agents/list — lightweight agent list for dropdown (agent_id only)
* Rename in NAV_CONFIG: `Task Prompts` → `Manage Tasks`
* Update route path in routes.tsx to match

**Layer:** ui/api/, src/utils/config.py, ui/frontend/src/routes.tsx

#### Files changed (plan vs actual) _(no per-ticket commit trail — folded into the epic table above)_

### AST-262 — Manage Tasks screen
_Linear: https://linear.app/astralcareermatch/issue/AST-262/manage-tasks-screen · Status: Backlog (stale — shipped with parent) · Priority: High · Assignee: Unassigned · Labels: subissue · Project: Astral Administrator · Created 2026-03-02 · Updated 2026-03-02_

#### What this implements

**Scope:** De-stub TaskPrompts.tsx into a working Manage Tasks screen.

* ListPage driven by get_task_keys(): task_key, agent (agent_id or 'Not set'), user/cache/nocache char counts with green/red coverage indicators
* Row action: tabbed edit modal with 3 tabs:
  * Tab 1 (System/User) — agent dropdown from agent table + user_prompt text input (short field)
  * Tab 2 (Cache) — large textarea for cache_prompt (raw template with merge tokens visible, e.g. `{$FNAME}`)
  * Tab 3 (NoCache) — large textarea for nocache_prompt (same pattern)
* Save commits all four fields (agent_id, user_prompt, cache_prompt, nocache_prompt)
* Rename component file or keep as TaskPrompts.tsx (functional name in nav is what matters)

**Layer:** ui/frontend/src/pages/Admin/TaskPrompts.tsx

#### Files changed (plan vs actual) _(no per-ticket commit trail — folded into the epic table above)_
