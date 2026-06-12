# AST-361 — [AST-305] agent_task: system_prompt column + API persistence

**Linear:** [AST-361](https://linear.app/astralcareermatch/issue/AST-361/ast-305-agent_task-system_prompt-column-api-persistence)  
**Parent:** [AST-305](https://linear.app/astralcareermatch/issue/AST-305/add-system-prompt-tab-to-manage-tasks)  
**Feature branch:** `<agent>/ast-361-ast-305-agent_task-system_prompt-column-api-persistence`

## Historical note (ticket tracking)

AST-361 was once described as fully superseded by a single **AST-305** execution doc. **Revision 2** re-opened **AST-361** as the **backend-only** slice (**Stages 1, 2, 4** of `docs/features/artifacts/ast-305-add-system-prompt-tab-to-manage-tasks.md`). **Stage 3** (Manage Tasks **System** tab UI) stays on **AST-305** / **AST-363**. Paired reference: this ticket’s branch vs **AST-305**’s branch for the UI half.

---

## Self-Assessment

**Scope — `minor`**  
Backend-only delta (`database.py`, `api_admin.py`, `agent.py`) — not the full cross-stack **AST-305** footprint.

**Conf — `high`**  
Must stay aligned with parent **AST-305** plan wording and versioning semantics.

**Risk — `low`**  
Column defaults + fallback to agent **`content`** preserve prior runtime when **`system_prompt`** is empty.

---

## Revision 2 — 2026-05-06 (Plan Approved **AST-361** build)

Susan re-opened **AST-361** as the backend execution ticket. Implementation follows **`docs/features/artifacts/ast-305-add-system-prompt-tab-to-manage-tasks.md`** Stages **1** (schema + `save_agent_task`), **2** (`api_admin` load/save + `_enrich_tasks` token estimate), and **4** (`do_task` / `preview_prompt` system source) — **not** Stage 3 UI (remains **AST-305** / **AST-363**).

## Review (stub — b-build-linear)

**Branch:** `<agent>/ast-361-ast-305-agent_task-system_prompt-column-api-persistence`  
**Commit:** (see Linear “Built by Ada” comment on AST-361 — avoids SHA drift if the stub is amended)

**Shipped**

- `agent_task.system_prompt TEXT NOT NULL DEFAULT ''` (+ lazy `ALTER` for existing DBs); versioning treats **`system_prompt`** as **metadata** (same class as `run_next` / `agent_id`): only **user** / **cache** / **nocache** changes retire the row.
- `save_agent_task(..., system_prompt=...)`, `list_candidate_tasks` exposes **`system_prompt_len`**, `sync_agent_tasks` inserts default empty system.
- `PUT /api/admin/tasks/<key>` accepts optional **`system_prompt`**; **`get_agent_task`** JSON includes the column via `SELECT *`.
- **`resolved_task_system`** in `src/core/agent.py`: non-empty trimmed **`agent_task.system_prompt`** → `resolve_tokens`; else agent **`content`** (previous behavior). **`preview_prompt`** matches **`do_task`**.
- **`_enrich_tasks`**: cache-threshold **system** token count uses the same resolution when task + agent rows exist.

## Review (Radia) — 2026-05-07

**Diff:** `origin/dev`…`<agent>/ast-361-ast-305-agent_task-system_prompt-column-api-persistence` @ **`a935f505`**.

**Note:** Linear **`gitBranchName`** shows `radia/ast-361-…` but **`refs/heads/radia/…`** is absent here; review used **`<agent>/ast-361-…`** (Ada’s checkout). Recommend updating Linear to the real branch name.

### What’s solid

- **Schema + migration:** `system_prompt TEXT NOT NULL DEFAULT ''`; lazy **`ALTER`**; v1 migration **`INSERT`** aligns column count with placeholders; **`sync_agent_tasks`** default row includes empty **`system_prompt`** (**§2.4 / INSERT hygiene**).
- **Versioning semantics:** **`content_changed`** still only **user/cache/nocache**; **`system_prompt`** updated in the metadata path or copied on new version rows — matches “metadata like **`run_next`** / **`agent_id`**” in the stub.
- **Runtime:** **`resolved_task_system`** centralizes **trimmed non-empty task system → `resolve_tokens`**, else **agent `content`**; **`do_task`** and **`preview_prompt`** stay aligned.
- **API:** **`PUT`** passes **`system_prompt`** into **`save_agent_task`**; **`get_agent_task`** is **`SELECT *`** so the new column is returned automatically.
- **`list_candidate_tasks`:** **`system_prompt_len`** exposed for admin UI / token UX.

### Issues

| Severity | Topic | Detail |
|----------|--------|--------|
| *Discuss* | **`api_admin` → `_resolved_task_system`** | Private import from **`agent.py`** (alongside existing **`_decode_payload`**). Acceptable if you’re standardizing AST-292-style admin introspection; if you want stricter layering later, expose a small public helper on **`agent`** or **`database`** facade. |
| *Advisory* | Doc contradiction | Top of this file still says “superseded — implement AST-305 only”; **Revision 2** + shipped bullets contradict. Consider trimming the obsolete “cancel 361” block so the doc is single-source for onboarding. |

### Recommended actions

1. Fix **Linear `gitBranchName`** → **`<agent>/ast-361-ast-305-agent_task-system_prompt-column-api-persistence`** (or ensure **`radia/…`** ref exists if that naming is intentional).
2. Quick API smoke: **`PUT`** with only **`system_prompt`** (no user/cache/nocache change) → expect **in-place** update, **`current` still 1**.

**Counts:** fix-now **0** · discuss **1** · advisory **1**

— Radia

## Resolution (f-resolve-linear) — 2026-05-07

**Radia review:** fix-now **0**.

**Discuss — admin import of system resolver**  
Renamed **`_resolved_task_system`** → **`resolved_task_system`** in **`src/core/agent.py`**; **`api_admin._enrich_tasks`** imports the public name (alongside existing AST-292 **`run_adhoc`** / **`_decode_payload`** pattern).

**Advisory — doc contradiction**  
Removed misleading supersession-only framing; added **Historical note** clarifying **Revision 2** backend scope vs **AST-305** UI stages.

**Merge:** **`origin/dev`** merged into this branch before resolve (skill orientation MCP docs landed on **dev**).

**Linear `gitBranchName`:** MCP **`save_issue`** has no branch field — update issue branch name in Linear UI to **`<agent>/ast-361-ast-305-agent_task-system_prompt-column-api-persistence`** if still wrong (Radia note).

**Verify:** `python3 -m py_compile src/core/agent.py src/ui/api/api_admin.py`
