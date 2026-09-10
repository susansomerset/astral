# AST-243 — Manage Agents
**Component:** administrator  
**Children:** AST-255, AST-256, AST-257 (documented inline; no per-ticket commit trail)  
**Linear archived:** AST-243 2026-06-03  

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-03-02 08:46 | AST-243 | — | `6a611eef7` | Implement Agent Management UI and API Integration |
| 2026-03-02 09:23 | AST-243 | merge | `ff876438d` | Merge pull request #28 from susansomerset/chuckles/ast-243-manage-agents |

_Pre-`verb(AST-NNN)` era: the feature commit does not name the ticket in its subject; it is reachable via the named PR merge. Path convention was `ui/…`. Sub-issue tickets AST-255–257 have no individual commits._

## Epic — AST-243
_Archived: 2026-06-03 · Linear URL: https://linear.app/astralcareermatch/issue/AST-243/manage-agents · Status at archive: Done · Project: Astral Administrator · Assignee: susan · Priority / estimate: High / 3_

### Original brief

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

#### Comments

_No comments._

### Files changed (plan vs actual)

Sub-issue plans → actual in PR #28 (`6a611eef7`). Era path convention `ui/…`.

| | file | planned (sub) | actual |
|---|---|---|---|
| ✓ | `src/data/database.py` | 255 — `agent` table (`agent_id` PK, `content`, `updated_at`), idempotent `_ensure_*_schema`, `save_agent` / `get_agent` / `list_agents` (id, char count, updated_at), no delete in v1, docstring | `6a611eef7` |
| ✓ | `src/ui/api/admin_agents.py` (new) | 256 — `admin_agents_bp` (`/api/admin/agents`), GET list / GET one / PUT / POST, all `@require_auth` | `6a611eef7` (`ui/api/admin_agents.py`) |
| ✓ | `src/ui/server.py` | 256 — register blueprint | `6a611eef7` (`ui/server.py`) |
| ✓ | `src/utils/config.py` | 256 — NAV_CONFIG rename `Agent Prompts` → `Manage Agents` | `6a611eef7` |
| ⚠ not touched | `src/ui/frontend/src/routes.tsx` | 256 — update route path to match | — (not in this commit) |
| ✓ | `src/ui/frontend/src/pages/Admin/AgentPrompts.tsx` | 257 — de-stub into Manage Agents screen: ListPage, Edit → textarea → PUT, Add New Agent modal → POST, no delete v1 | `6a611eef7` (`ui/frontend/…`) |

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-255 — Agent table and database functions
_Linear: https://linear.app/astralcareermatch/issue/AST-255/agent-table-and-database-functions · Status: Done · Priority: High · Assignee: Unassigned · Labels: subissue · Project: Astral Administrator · Created 2026-03-02 · Updated 2026-03-02_

#### What this implements

**Scope:** Create agent table and CRUD functions in [database.py](<http://database.py>).

* CREATE TABLE agent: `agent_id` TEXT PK (human-readable, e.g. `job_analyst_grace`), `content` TEXT (system prompt template, may include merge tokens), `updated_at` TIMESTAMP
* Idempotent schema creation following existing `_ensure_*_schema` pattern
* Database functions: `save_agent(agent_id, content)`, `get_agent(agent_id)`, `list_agents()` (returns agent_id, char count of content, updated_at)
* No delete in v1 (agents are referenced by agent_task records)
* Update [database.py](<http://database.py>) module docstring per ASTRAL_CODE_RULES 1.1

**Layer:** src/data/database.py

#### Files changed (plan vs actual) _(no per-ticket commit trail — folded into the epic table above)_

### AST-256 — API endpoints and nav rename
_Linear: https://linear.app/astralcareermatch/issue/AST-256/api-endpoints-and-nav-rename · Status: Done · Priority: High · Assignee: Unassigned · Labels: subissue · Project: Astral Administrator · Created 2026-03-02 · Updated 2026-03-02_

#### What this implements

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

#### Files changed (plan vs actual) _(no per-ticket commit trail — folded into the epic table above)_

### AST-257 — Manage Agents screen
_Linear: https://linear.app/astralcareermatch/issue/AST-257/manage-agents-screen · Status: Done · Priority: High · Assignee: Unassigned · Labels: subissue · Project: Astral Administrator · Created 2026-03-02 · Updated 2026-03-02_

#### What this implements

**Scope:** De-stub AgentPrompts.tsx into a working Manage Agents screen.

* ListPage showing all agents from GET /api/admin/agents
* Columns: agent_id, char count of content, updated_at
* Row action: Edit → full-page textarea with content, save writes back via PUT
* Add New Agent button → modal with agent_id input + content textarea, creates via POST
* No delete in v1
* Rename component file or keep as AgentPrompts.tsx (functional name in nav is what matters)

**Layer:** ui/frontend/src/pages/Admin/AgentPrompts.tsx

#### Files changed (plan vs actual) _(no per-ticket commit trail — folded into the epic table above)_
