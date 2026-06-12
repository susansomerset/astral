<!-- linear-archive: AST-305 archived 2026-06-03 -->

## Linear archive (AST-305)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-305/add-system-prompt-tab-to-manage-tasks  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** susan  
**Priority / estimate:** High / 3  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-306; blocks: AST-313

### Description

Add an editable System tab to the Manage Tasks UI (TaskPrompts.tsx) alongside existing prompt content tabs. Maps to a new system_prompt column on the agent_task DB row. Defaults to {$SELECTED_AGENT} which resolves to the assigned agent's system prompt at runtime. Can be overwritten — required for artifact pipeline tasks where agent persona is placed in the task prompt, freeing the system slot for stable cached content.

### Comments

#### chuckles — 2026-05-18T19:49:44.507Z
## finish-up — Chuckles

Susan requested **finish-up** for **AST-305**.

### Git
- `origin/ftr/AST-305-add-system-prompt-tab-to-manage` was **already contained in** `origin/dev` (prep-uat merge `35b3e424` / child merges present). Merge → *Already up to date*. **No push** to `origin/dev`.
- Deleted `origin/ftr/AST-305-add-system-prompt-tab-to-manage`
- No `sub/AST-305/*` branches on origin (already removed after prep-uat).

### Linear
Parent **AST-305** and children **AST-361**, **AST-363** were already **Done** — left statuses unchanged.

`origin/dev` tip: `f842e065`

— Chuckles

#### chuckles — 2026-05-17T21:01:09.080Z
## UAT Ready — Chuckles

All 2 child workstreams are on the parent branch. Child feature branches cleaned up where they existed.

**Parent branch:** `origin/ftr/AST-305`

**Merged / integrated in order:**
1. **AST-361** — [AST-305] agent_task: system_prompt column + API persistence — already on parent history (no `ftr/AST-361`; backend landed earlier / branch archived)
2. **AST-363** — [AST-305] Manage Tasks: System prompt tab (UI) — merged `origin/ftr/AST-363` → `ftr/AST-305` — **branch deleted**

**Verify on parent:** AST-361 commits (`a935f505`, `036c7f78`) and AST-363 commits (`881c16ce` … `ac9c1088`) plus merge commit `32433d7f`.

**To test locally:**
```bash
git fetch origin
git checkout dev
git merge origin/ftr/AST-305
```

**If testing fails:**
```bash
git reset --hard origin/dev
```

— Chuckles

#### chuckles — 2026-05-16T15:44:26.206Z
## Parent status — Chuckles

Moved parent to **In Progress**: child tickets are in mixed pipeline states. Susan/Chuckles board cleanup 2026-05-16.

— Chuckles

#### susan — 2026-05-04T21:34:35.267Z
**Plan ready (a-plan-linear, queue: Ada)**

**Doc:** `docs/features/artifacts/ast-305-add-system-prompt-tab-to-manage-tasks.md` on `chuckles/ast-305-add-system-prompt-tab-to-manage-tasks`.

**Self-assessment:** Scope **MAJOR-CHANGE**, Conf **Medium**, Risk **Medium** — see doc. **AST-361** / **AST-363** superseded by this single execution plan (per doc **Decision**).

#### susan — 2026-05-04T21:29:55.663Z
[check-linear] (Ada · Astral Artifacts)

- **Inbox:** No new thread items requiring a reply on this issue (only the earlier split note for **AST-361** / **AST-363**).
- **Project scan:** **AST-303** (Plan Ready) and **AST-306** (Testing) unchanged since last `[check-linear]`; other Ada **Todo** rows (**AST-361**, **AST-365**, **AST-368**, **AST-370**) have empty threads.
- **Step 6:** `a-plan-linear` **queue mode** would take **AST-305** next — I did **not** author a new execution doc in this pass (full **a-plan-linear** is its own session). Say to run **`a-plan-linear` AST-305** (or explicit id) when you want the plan. **`e-push-linear`:** no Ada **PR Ready** in this project. **`d-resolve-linear`:** no Ada **Review Posted**. **`b-build-linear`:** no Ada **Plan Approved** (**AST-303** still **Plan Ready**).

#### susan — 2026-04-29T17:47:20.037Z
**Split for label-based assignment** (single Linear seat):
- **AST-361** — `system_prompt` column + API (**Ada**)
- **AST-363** — System tab UI in Manage Tasks (**Katherine**, blocked by **AST-361**)

Labels **Ada** / **Hedy** / **Katherine** on Team Astral mark ownership.

---

# AST-305 — Add System Prompt Tab to Manage Tasks

**Linear:** [AST-305](https://linear.app/astralcareermatch/issue/AST-305/add-system-prompt-tab-to-manage-tasks)  
**Feature branch:** `<agent>/ast-305-add-system-prompt-tab-to-manage-tasks`

Add **`system_prompt`** to the **`agent_task`** row (DB + API + Manage Tasks UI) so operators can edit **system**-slot text per task. Default semantics: **empty** or whitespace-only means **use assigned agent’s `content`** (today’s behavior); a literal **`{$SELECTED_AGENT}`** in the stored string resolves via **`TOKEN_SOURCES` / `chain_context`** like other prompts; any other text is resolved with **`resolve_tokens`** and sent as the system block. **`do_task`** must read **system prompt text from `agent_task_row` first**, falling back to **`agent_row["content"]`** when the column is empty, so existing tasks behave unchanged.

⚠️ **Decision:** Linear children **AST-361** (backend) and **AST-363** (UI, Katherine) are **superseded** by this single execution plan — same pattern as **AST-306** superseding **AST-362**/**AST-364**. One PR unless Susan splits later.

⚠️ **Decision:** Linear mentions `TaskPrompts.tsx`; the Manage Tasks implementation is **`src/ui/frontend/src/pages/AdminTaskPrompts.tsx`** (`export default function TaskPrompts`). All UI steps target that file.

---

## Files changed (planned)

| File | Change | Layer |
|------|--------|--------|
| `src/data/database.py` | Header inventory; `_ensure_agent_task_schema` + migration for **`system_prompt TEXT NOT NULL DEFAULT ''`**; `save_agent_task` / `get_agent_task` / `list_candidate_tasks` / `sync_agent_tasks` (mirror **`run_next`** column rollout on `agent_task` — same INSERT/UPDATE audit discipline). | data |
| `src/ui/api/api_admin.py` | `update_task` / `_enrich_tasks` / `get_task` pass **`system_prompt`**; JSON omit vs clear semantics match **`run_next`**. | ui |
| `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | New **System** tab in edit modal (alongside User / Cache / NoCache); table column or token preview for system snippet; `PUT` body field **`system_prompt`**. | ui |
| `src/core/agent.py` | Resolve **system** from **`(agent_task_row.get("system_prompt") or "").strip()`** — if falsy, use **`agent_row.get("content") or ""`**; then existing **`resolve_tokens(..., _chain_context(agent_row))`**. | core |

---

## Stage 1: Schema + `save_agent_task` / reads (`database.py`)

**Done when:** Fresh DBs have column; existing DBs `ALTER` once; blank `system_prompt` round-trips; versioning treats **`system_prompt`** like **`run_next`** / **`agent_id`** (metadata vs prompt-body split — **prompt** fields that bump version: `user_prompt`, `cache_prompt`, `nocache_prompt`; **metadata**: `agent_id`, `run_next`, **`system_prompt`** if you decide system text is metadata-only — **⚠️ Decision:** Treat **`system_prompt`** as **metadata** for versioning: changing only `system_prompt` does **not** retire the row; changing `user`/`cache`/`nocache` still versions. If Susan prefers system text to version like prompts, flip this **Decision** and update the `content_changed` expression accordingly.)

1. Add column + helper validation if needed (e.g. reject impossible sizes only if product requires — default **no** max unless Susan adds one).
2. Extend **`save_agent_task`** signature with **`system_prompt: Optional[str] = None`**; wire SELECT/INSERT/UPDATE tuple positions; audit every **`INSERT`/`UPDATE`** on **`agent_task`** in this file after edit.

---

## Stage 2: Flask admin API (`api_admin.py`)

**Done when:** `GET` list + single task return **`system_prompt`**; `PUT` accepts optional **`system_prompt`** with same key semantics as **`run_next`**.

1. **`_enrich_tasks`:** add **`"system_prompt": t.get("system_prompt") or ""`** (or null policy matching **`run_next`**).
2. **`update_task`:** pass through to **`save_agent_task`** inside existing **`try`/`except ValueError`** → **400** JSON error pattern.

---

## Stage 3: Manage Tasks UI (`AdminTaskPrompts.tsx`)

**Done when:** Modal has **System** tab with **`TokenTextarea`** (or same control as other prompts); save/load wired; table shows short preview or “—” when empty.

1. Extend **`AgentTask`** type with **`system_prompt?: string`**.
2. Add edit state **`editSystem`**; load/save with **`PUT`**.
3. **`preview_task`** path: if preview API includes resolved system, extend only if already supported — **else** skip preview for system in Stage 3 and add **Stage 4** “preview parity” only if product requires.

---

## Stage 4: `do_task` system source (`agent.py`)

**Done when:** With empty **`system_prompt`** on row, behavior matches pre-change Anthropic system block; with **`{$SELECTED_AGENT}`** only, matches assigned agent system string after token resolution.

1. Implement fallback chain documented in header above.
2. **`preview_prompt`** in same file: mirror **`do_task`** system resolution so admin preview matches runtime.

---

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|--------|
| §1.2 / §3.2 | Data layer owns DDL; core reads `get_agent_task` dict only. |
| §2.1 | No new magic strings beyond default `{$SELECTED_AGENT}` literal already in **TOKEN_SOURCES** / chain. |
| §3.3 | No UI imports in core. |
| §3.5 | snake_case **`system_prompt`** end-to-end. |

---

## Self-Assessment

**Scope — `scope-MAJOR-CHANGE`**  
SQLite + versioning + Flask + React + **`do_task`** — crosses layers.

**Conf — `Medium`**  
Versioning classification for `system_prompt` must match product; easy to reverse via **Revision** if wrong.

**Risk — `Medium`**  
Wrong system fallback could change Anthropic caching behavior for all tasks — mitigate with tests on blank vs explicit override.
