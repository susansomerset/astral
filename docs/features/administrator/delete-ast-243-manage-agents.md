# AST-243 — Manage Agents

<!-- linear-archive: AST-243 archived 2026-06-03 -->

## Linear archive (AST-243)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-243/manage-agents  
**Status at archive:** Done  
**Project:** Astral Administrator  
**Assignee:** susan  
**Priority / estimate:** High / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

New admin screen to manage named system prompt templates. System prompts are reusable across multiple tasks and define agent persona, voice, and standing instructions. They are prose templates with candidate and config merge tokens.

**Acceptance Criteria:**

`agent` Table (new):

* `agent_id` — PK, human-readable string (e.g. `job_analyst_grace`, `gate_keeper_atlas`)
* `content` — TEXT, the system prompt template (may include merge tokens e.g. `{$FNAME}`, `{$CANDIDATE_UPSHOT}`, `{$RESPONSE_SCHEMA}`)
* `updated_at` — TIMESTAMP

**Manage Agents Screen (UI — Admin > Manage Agents):**

* ListPage showing all agents
* Columns: `agent_id`, char count of content, `updated_at`
* Row action: Edit → full-page textarea with content, save writes back to `agent` table
* Add New Agent button → modal with `agent_id` input + content textarea
* No delete in v1 (agents are referenced by agent_task records)

**API Endpoints:**

* GET /api/admin/agents — list all agents (agent_id, char count, updated_at)
* GET /api/admin/agents/:agent_id — get full content
* PUT /api/admin/agents/:agent_id — save updated content
* POST /api/admin/agents — create new agent

**Notes:**

* agent_id is stable and referenced by agent_task records — renaming is out of scope for v1
* Content is a template; token resolution happens at runtime in [anthropic.py](<http://anthropic.py>), not here
* Seed script to migrate existing system prompt .txt files from data/agents/\_systemprompts/ into agent table on first run

**Database:**

* agent table: CREATE TABLE as above
* [database.py](<http://database.py>) module docstring updated per ASTRAL_CODE_RULES 1.1

# Manage Agents

**Scope:** Create agent table and CRUD functions in [database.py](<http://database.py>).

* CREATE TABLE agent: `agent_id` TEXT PK (human-readable, e.g. `job_analyst_grace`), `content` TEXT (system prompt template, may include merge tokens), `updated_at` TIMESTAMP
* Idempotent schema creation following existing `_ensure_*_schema` pattern
* Database functions: `save_agent(agent_id, content)`, `get_agent(agent_id)`, `list_agents()` (returns agent_id, char count of content, updated_at)
* No delete in v1 (agents are referenced by agent_task records)
* Update [database.py](<http://database.py>) module docstring per ASTRAL_CODE_RULES 1.1

**Layer:** src/data/database.py

## Metadata

* URL: [AST-255](https://linear.app/astralcareermatch/issue/AST-255/agent-table-and-database-functions)
* Identifier: [AST-255](https://linear.app/astralcareermatch/issue/AST-255/agent-table-and-database-functions)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Administrator](https://linear.app/astralcareermatch/project/astral-administrator-63591e1603e6). The features available to administrative users to manage candidate users and to maintain prompts and view performance.
* Created: 2026-03-02T06:34:20.300Z
* Updated: 2026-03-02T20:06:08.666Z

---

# Manage Agents

**Scope:** Create API blueprint for agent CRUD and rename nav item from Agent Prompts to Manage Agents.

* New Blueprint ui/api/admin_agents.py with url_prefix="/api/admin/agents", registered in ui/server.py
* Endpoints (all @require_auth):
  * GET /api/admin/agents — list all agents (agent_id, char count, updated_at)
  * GET /api/admin/agents/:agent_id — get full content
  * PUT /api/admin/agents/:agent_id — save updated content
  * POST /api/admin/agents — create new agent (agent_id + content)
* Rename in NAV_CONFIG: `Agent Prompts` → `Manage Agents`
* Update route path in routes.tsx to match

**Layer:** ui/api/admin_agents.py, ui/server.py, src/utils/config.py, ui/frontend/src/routes.tsx

## Metadata

* URL: [AST-256](https://linear.app/astralcareermatch/issue/AST-256/api-endpoints-and-nav-rename)
* Identifier: [AST-256](https://linear.app/astralcareermatch/issue/AST-256/api-endpoints-and-nav-rename)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Administrator](https://linear.app/astralcareermatch/project/astral-administrator-63591e1603e6). The features available to administrative users to manage candidate users and to maintain prompts and view performance.
* Created: 2026-03-02T06:34:21.672Z
* Updated: 2026-03-02T20:06:08.619Z

---

# Manage Agents

**Scope:** De-stub AgentPrompts.tsx into a working Manage Agents screen.

* ListPage showing all agents from GET /api/admin/agents
* Columns: agent_id, char count of content, updated_at
* Row action: Edit → full-page textarea with content, save writes back via PUT
* Add New Agent button → modal with agent_id input + content textarea, creates via POST
* No delete in v1
* Rename component file or keep as AgentPrompts.tsx (functional name in nav is what matters)

**Layer:** ui/frontend/src/pages/Admin/AgentPrompts.tsx

## Metadata

* URL: [AST-257](https://linear.app/astralcareermatch/issue/AST-257/manage-agents-screen)
* Identifier: [AST-257](https://linear.app/astralcareermatch/issue/AST-257/manage-agents-screen)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Administrator](https://linear.app/astralcareermatch/project/astral-administrator-63591e1603e6). The features available to administrative users to manage candidate users and to maintain prompts and view performance.
* Created: 2026-03-02T06:34:22.832Z
* Updated: 2026-03-02T20:06:08.578Z

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
