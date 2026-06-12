# AST-244 — Manage Tasks

<!-- linear-archive: AST-244 archived 2026-06-03 -->

## Linear archive (AST-244)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-244/manage-tasks  
**Status at archive:** Done  
**Project:** Astral Administrator  
**Assignee:** susan  
**Priority / estimate:** High / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

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

# Manage Tasks

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

## Metadata

* URL: [AST-258](https://linear.app/astralcareermatch/issue/AST-258/config-tasks-refactor-and-token-sources-in-configpy)
* Identifier: [AST-258](https://linear.app/astralcareermatch/issue/AST-258/config-tasks-refactor-and-token-sources-in-configpy)
* Status: Backlog
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Administrator](https://linear.app/astralcareermatch/project/astral-administrator-63591e1603e6). The features available to administrative users to manage candidate users and to maintain prompts and view performance.
* Created: 2026-03-02T06:34:23.780Z
* Updated: 2026-03-02T06:34:23.780Z

---

# Manage Tasks

**Scope:** Create agent_task table and CRUD functions with automatic sync on startup.

* CREATE TABLE agent_task: `task_key` TEXT PK (matches CONFIG_TASKS key), `agent_id` TEXT FK to agent (nullable until assigned), `user_prompt` TEXT, `cache_prompt` TEXT, `nocache_prompt` TEXT, `updated_at` TIMESTAMP
* Database functions: `save_agent_task(task_key, ...)`, `get_agent_task(task_key)`, `list_agent_tasks()`
* Startup sync: compare CONFIG_TASKS keys against agent_task rows; auto-create blank records for missing keys (surfaces in UI as unconfigured/red)
* Update [database.py](<http://database.py>) module docstring per ASTRAL_CODE_RULES 1.1

**Layer:** src/data/database.py

## Metadata

* URL: [AST-259](https://linear.app/astralcareermatch/issue/AST-259/agent-task-table-database-functions-and-startup-sync)
* Identifier: [AST-259](https://linear.app/astralcareermatch/issue/AST-259/agent-task-table-database-functions-and-startup-sync)
* Status: Backlog
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Administrator](https://linear.app/astralcareermatch/project/astral-administrator-63591e1603e6). The features available to administrative users to manage candidate users and to maintain prompts and view performance.
* Created: 2026-03-02T06:34:24.950Z
* Updated: 2026-03-02T06:34:24.950Z

---

# Manage Tasks

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

## Metadata

* URL: [AST-260](https://linear.app/astralcareermatch/issue/AST-260/anthropicpy-db-first-prompt-assembly-and-generic-token-resolver)
* Identifier: [AST-260](https://linear.app/astralcareermatch/issue/AST-260/anthropicpy-db-first-prompt-assembly-and-generic-token-resolver)
* Status: Backlog
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Administrator](https://linear.app/astralcareermatch/project/astral-administrator-63591e1603e6). The features available to administrative users to manage candidate users and to maintain prompts and view performance.
* Created: 2026-03-02T06:34:25.955Z
* Updated: 2026-03-02T06:34:25.955Z

---

# Manage Tasks

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

## Metadata

* URL: [AST-261](https://linear.app/astralcareermatch/issue/AST-261/api-endpoints-and-nav-rename)
* Identifier: [AST-261](https://linear.app/astralcareermatch/issue/AST-261/api-endpoints-and-nav-rename)
* Status: Backlog
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Administrator](https://linear.app/astralcareermatch/project/astral-administrator-63591e1603e6). The features available to administrative users to manage candidate users and to maintain prompts and view performance.
* Created: 2026-03-02T06:34:27.186Z
* Updated: 2026-03-02T06:34:27.186Z

---

# Manage Tasks

**Scope:** De-stub TaskPrompts.tsx into a working Manage Tasks screen.

* ListPage driven by get_task_keys(): task_key, agent (agent_id or 'Not set'), user/cache/nocache char counts with green/red coverage indicators
* Row action: tabbed edit modal with 3 tabs:
  * Tab 1 (System/User) — agent dropdown from agent table + user_prompt text input (short field)
  * Tab 2 (Cache) — large textarea for cache_prompt (raw template with merge tokens visible, e.g. `{$FNAME}`)
  * Tab 3 (NoCache) — large textarea for nocache_prompt (same pattern)
* Save commits all four fields (agent_id, user_prompt, cache_prompt, nocache_prompt)
* Rename component file or keep as TaskPrompts.tsx (functional name in nav is what matters)

**Layer:** ui/frontend/src/pages/Admin/TaskPrompts.tsx

## Metadata

* URL: [AST-262](https://linear.app/astralcareermatch/issue/AST-262/manage-tasks-screen)
* Identifier: [AST-262](https://linear.app/astralcareermatch/issue/AST-262/manage-tasks-screen)
* Status: Backlog
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Administrator](https://linear.app/astralcareermatch/project/astral-administrator-63591e1603e6). The features available to administrative users to manage candidate users and to maintain prompts and view performance.
* Created: 2026-03-02T06:34:28.104Z
* Updated: 2026-03-02T06:34:28.104Z

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
