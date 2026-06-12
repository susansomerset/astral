<!-- linear-archive: AST-306 archived 2026-06-03 -->

## Linear archive (AST-306)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-306/add-run-next-field-to-manage-tasks  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** Medium / 2  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-313

### Description

Add a Run Next selector to the Manage Tasks UI (TaskPrompts.tsx). Stored as run_next column on the agent_task DB row. Consumed by do_task() to drive self-chaining. UI renders as a dropdown of all configured task keys; empty/unset means end of chain. Also add to AdminTaskPrompts.tsx for admin visibility.

### Comments

#### susan — 2026-05-04T20:48:34.533Z
[check-linear]

- **Radia review:** Resolved via `d-resolve-linear` — appended `## Resolution` to `docs/features/artifacts/ast-306-add-run-next-field-to-manage-tasks.md` (advisory on broad `ValueError` accepted as documented; no code change).
- **Linear:** **Testing**, assignee **Susan**, engineer label **Ada** preserved.
- **Commit:** `f05fcc80ed66e0989d6edcf6d7c9a452c1dfbe16`

#### susan — 2026-05-04T20:47:45.848Z
Review feedback resolved. Branch `chuckles/ast-306-add-run-next-field-to-manage-tasks` is ready for testing. Commit: `f05fcc80ed66e0989d6edcf6d7c9a452c1dfbe16`

#### susan — 2026-05-04T19:56:13.229Z
**Review posted — Radia**

Summary: **0** fix-now, **0** discuss, **1** advisory (`update_task` maps any `ValueError` from `save_agent_task` to HTTP 400 — fine today; narrow if more `ValueError` sources appear).

Diff reviewed: **`origin/dev`…feature branch** (avoids local `dev` skew). Owner back to **Ada** per build handoff. Conf / Risk / Scope labels preserved.

**Combined doc:**  
https://github.com/susansomerset/astral/blob/9a1a27d19117e55a350114796a63d0ba6dcfea68/docs/features/artifacts/ast-306-add-run-next-field-to-manage-tasks.md

— Radia

#### susan — 2026-05-04T19:53:21.846Z
Built by Ada.

Branch: `chuckles/ast-306-add-run-next-field-to-manage-tasks`
Commits: `88eabf1` (implementation), `5da3543` (artifact Review stub SHA).

#### susan — 2026-05-04T19:50:21.599Z
Label review (build agent):

Conf: agree — **conf-Medium** matches the plan (metadata vs prompt versioning + `TASK_CONFIG` validation).
Risk: agree — **risk-Medium** matches (Manage Tasks + downstream **AST-303**).
Scope: agree — **scope-MAJOR-CHANGE** matches (DB + Flask admin + React).

— Ada

#### susan — 2026-05-04T19:48:29.986Z
**Ack** — saw your follow-up. Logged the **`ctx` / parameter-object / no-extra-getters** direction on **AST-303** (comment there) so the daisy-chain plan owns it; **AST-306** stays storage + Manage Tasks only.

— Ada

#### susan — 2026-05-04T19:42:35.259Z
Add a comment to 303 about this, please.  However, I do NOT want to add unnecessary get functions when we can orchestrate the content to pass through on parameter objects.  I guess what I'm saying is, let's reframe build_resume(job_id) to build_resume({job}).  How it gets a {job} is the caller's concern.

#### susan — 2026-05-04T19:37:38.580Z
**Re: `ctx` for daisy-chained tasks**

**AST-306 (this plan)** stops at **`run_next` on `agent_task` + admin API + Manage Tasks UI**. It does **not** change `do_task()` or how `ctx` is threaded — so by itself it neither passes nor withholds `ctx` downstream.

**Where that belongs:** **AST-303** (daisy-chain execution) is where the outer `do_task` would read `run_next`, decide the next `task_key`, and call `await do_task(...)` again. The natural match to your intent is: **reuse the same `ctx` reference** (and the same `candidate_data` / `live_content` / `index` / `debug` / `store_agent_data` defaults already on the call) for each hop unless the **AST-303** plan explicitly narrows or extends `ctx` for chain-specific keys (e.g. merged `chain_context` for `resolve_tokens`). That is the same *idea* as dispatcher passing a stable batch context into work units — but the mechanism is **`do_task`’s existing kwargs**, not dispatcher code paths.

**If you want the 306 doc to lock that in:** we can add a short **“Contract for AST-303”** note under the header (or a **Revision**) stating: *when `run_next` is consumed, chained invocations receive the same `ctx` as the root call unless AST-303 says otherwise.* Say the word and I’ll add it via **plan-linear** re-run or a doc-only commit on the feature branch.

— Ada

#### susan — 2026-05-04T19:36:38.331Z
I'm not sure what the pattern is for dispatcher and if it makes sense to reuse it, but when the task is called, a ctx object is provided, and I could see a great deal of value having that ctx be passed to the daisy-chained tasks downstream.  Would this plan do that, or would we be solving the context problem by a different method?

#### susan — 2026-05-04T19:25:17.570Z
**Plan (execution doc):** `docs/features/artifacts/ast-306-add-run-next-field-to-manage-tasks.md`  
**Branch:** `chuckles/ast-306-add-run-next-field-to-manage-tasks` (merged `origin/dev`, then plan rewrite commit)

**Self-assessment (labels)**

- **Scope — MAJOR-CHANGE:** SQLite DDL + `save_agent_task` versioning + Flask admin `PUT`/`GET` list + React `AdminTaskPrompts.tsx` — data, API, and UI.
- **Conf — Medium:** `run_next` must follow the same prompt-vs-metadata split as `agent_id`; validation ties to `TASK_CONFIG` keys.
- **Risk — Medium:** Migration or save regressions affect Manage Tasks; bad values feed **AST-303** — server-side validation required.

**Queue mode:** First **Todo** + **Ada** + **Astral Artifacts** by `updatedAt` was **AST-306** (per `list_issues`).

**Note:** Plan follows new **a-plan-linear** contract (stages, **Done when**, full replace on slug, execution binding). Historical **AST-362** / **AST-364** superseded by this doc per skill.

— Ada

#### susan — 2026-05-04T19:25:10.194Z
**Plan (execution doc):** `docs/features/artifacts/ast-306-add-run-next-field-to-manage-tasks.md`  
**Branch:** `chuckles/ast-306-add-run-next-field-to-manage-tasks` (merged `origin/dev`, then plan rewrite commit)

**Self-assessment (labels)**

- **Scope — MAJOR-CHANGE:** SQLite DDL + `save_agent_task` versioning + Flask admin `PUT`/`GET` list + React `AdminTaskPrompts.tsx` — data, API, and UI.
- **Conf — Medium:** `run_next` must follow the same prompt-vs-metadata split as `agent_id`; validation ties to `TASK_CONFIG` keys.
- **Risk — Medium:** Migration or save regressions affect Manage Tasks; bad values feed **AST-303** — server-side validation required.

**Queue mode:** First **Todo** + **Ada** + **Astral Artifacts** by `updatedAt` was **AST-306** (per `list_issues`).

**Note:** Plan follows new **a-plan-linear** contract (stages, **Done when**, full replace on slug, execution binding). Historical **AST-362** / **AST-364** superseded by this doc per skill.

— Ada

#### susan — 2026-04-29T22:17:48.997Z
**Plan doc:** `docs/features/artifacts/ast-306-add-run-next-field-to-manage-tasks.md`  
**GitHub (feature branch):** `chuckles/ast-306-add-run-next-field-to-manage-tasks` — same path.

**Self-assessment (labels)**

- **Scope — MAJOR-CHANGE:** SQLite migration + `save_agent_task` versioning rules + admin API + `AdminTaskPrompts.tsx` (export `TaskPrompts`) — crosses data, API, and UI.
- **Conf — Medium:** `run_next` must follow the same “metadata vs prompt version” split as `agent_id`; child **AST-362** owns the tricky save-path details.
- **Risk — Medium:** Regressions on task save or bad `run_next` values affect all Manage Tasks users and downstream **AST-303**.

**Note:** Linear mentions *TaskPrompts.tsx*; in-repo Manage Tasks UI is `ui/frontend/src/pages/AdminTaskPrompts.tsx` (`export default function TaskPrompts`). Child **AST-364** references that file.

Worktree: branch cut from `origin/dev` (local `dev` lives in another clone).

— Ada

#### susan — 2026-04-29T17:47:20.802Z
**Split for label-based assignment** (single Linear seat):
- **AST-362** — `run_next` column + API (**Ada**)
- **AST-364** — Run next selector UI (**Katherine**, blocked by **AST-362**)

Labels **Ada** / **Hedy** / **Katherine** on Team Astral mark ownership.

---

# AST-306 — Add Run Next Field to Manage Tasks

**Linear parent:** [AST-306](https://linear.app/astralcareermatch/issue/AST-306/add-run-next-field-to-manage-tasks)  
**Feature branch:** `<agent>/ast-306-add-run-next-field-to-manage-tasks`

After this work, each current `agent_task` row carries optional **`run_next`** (a `task_key` string). Empty means no follow-on task. **AST-303** reads `run_next` from `get_agent_task()` after a successful hop to recurse `do_task()`. Manage Tasks UI (`src/ui/frontend/src/pages/AdminTaskPrompts.tsx`, default export `TaskPrompts`) exposes a dropdown so operators set the chain edge without SQL.

⚠️ **Decision:** Linear mentions `TaskPrompts.tsx`; the only Manage Tasks implementation is **`AdminTaskPrompts.tsx`** with `export default function TaskPrompts`. All UI steps target that file.

⚠️ **Decision:** Historical Linear children **AST-362** / **AST-364** are superseded by this single execution plan — no separate child PRs unless Susan splits later.

---

## Files changed (planned)

| File | Change | Layer |
|------|--------|--------|
| `src/data/database.py` | Header inventory line for `agent_task`; `_ensure_agent_task_schema` adds `run_next`; `save_agent_task` / `get_agent_task` / `list_candidate_tasks` / `sync_agent_tasks` | data |
| `src/ui/api/api_admin.py` | `update_task` passes `run_next`; `get_task` returns it; `_enrich_tasks` includes `run_next` in each row dict | ui (Flask) |
| `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | Type + state + modal Run Next `<select>` + table column + `PUT` body | ui (React) |

---

## Stage 1: Schema and persistence (`database.py`)

**Done when:** Fresh DBs create `agent_task` with `run_next`; existing DBs gain column via `ALTER TABLE`; `save_agent_task` persists and versions correctly; `get_agent_task` / `list_candidate_tasks` / `sync_agent_tasks` read/write `run_next`; invalid `run_next` raises `ValueError` before commit.

1. In `src/data/database.py` module docstring **Tables used** list, extend the **`agent_task`** bullet to include: `run_next TEXT` (chain target `task_key`, empty string = none).

2. In `_ensure_agent_task_schema`, after the block that ensures `task_key_uuid` / versioned schema exists (the `else` branch where `cols = PRAGMA table_info`), add a **second** column check: if `"run_next" not in cols`, execute `ALTER TABLE agent_task ADD COLUMN run_next TEXT NOT NULL DEFAULT ''` then `conn.commit()`. Re-read `cols` only if needed for clarity (single ALTER per startup is enough).

3. In the **CREATE TABLE agent_task** branch used when the table does not exist (the `if cursor.fetchone()[0] == 0` path), add column **`run_next TEXT NOT NULL DEFAULT ''`** to the column list and mirror it in both CREATE variants if two CREATE strings exist (empty DB path + post-rename path — only the paths that define full table DDL).

4. Add a module-level helper **`_validate_run_next(task_key: str, run_next: Optional[str]) -> None`** after imports are available (same file, near other private helpers). Behavior:
   - If `run_next` is `None`: return (caller means “omit / no change” at Python API level — see step 8 for JSON semantics).
   - Let `s = (run_next or "").strip()`.
   - If `s == ""`: return (clear chain).
   - If `s == task_key`: `raise ValueError("run_next cannot equal task_key (self-loop)")`.
   - If `s not in TASK_CONFIG`: `raise ValueError(f"run_next must be a configured task_key, got {s!r}")`.

5. Extend **`save_agent_task`** signature with keyword-only parameter **`run_next: Optional[str] = None`**.

6. Change the **current-row SELECT** inside `save_agent_task` from selecting five columns to selecting **six**: add **`run_next`** (same row as today: `task_key_uuid, agent_id, user_prompt, cache_prompt, nocache_prompt, run_next`).

7. **Insert path when `existing is None`:** extend INSERT column list and VALUES to include **`run_next`**. Use `(run_next.strip() if run_next is not None else "")` only after calling `_validate_run_next(task_key, run_next if run_next is not None else "")` — for new row with explicit None, treat as `""`.

8. **Update path when row exists — compute** `new_up`, `new_cp`, `new_np` exactly as today. Compute `new_rn = (run_next if run_next is not None else existing[5])` (index 5 = `run_next` from extended SELECT — adjust tuple index if column order differs; document in code comment next to SELECT).

9. **`content_changed`:** set to `True` when **any** of `new_up`, `new_cp`, `new_np` differ from `existing[2]`, `existing[3]`, `existing[4]` respectively — **do not** include `run_next` in `content_changed` (same rule as `agent_id`: metadata-only edits must not mint a new `task_key_uuid`).

10. **When `content_changed` is `True`:** before retiring the old row, call **`_validate_run_next(task_key, new_rn if (new_rn or "") != "" else None)`** with the resolved `new_rn` string (stripped for validation). Then `UPDATE agent_task SET current = 0 WHERE task_key_uuid = ?`, then `INSERT` the new version row including columns **`task_key_uuid` (new uuid), `task_key`, `current=1`, `agent_id`**, prompts **`new_up, new_cp, new_np`**, **`run_next=new_rn`**, **`updated_at=now`**. Use `agent_id` resolution exactly as today’s insert branch (`agent_id or existing[1] or ""` pattern from current code).

11. **When `content_changed` is `False`:** extend the existing “metadata only” UPDATE branch: start `sets, params` as today. If **`run_next is not None`**, call **`_validate_run_next(task_key, run_next)`**, then append **`run_next = ?`** to `sets` and bound stripped value (or `""`) to `params`. Keep existing **`agent_id`** handling unchanged. Execute `UPDATE agent_task SET ... WHERE task_key_uuid = ?` as today.

12. **`get_agent_task`:** no SQL change needed if it uses `SELECT *` — confirm `_row_to_dict` exposes `run_next` once column exists.

13. **`list_candidate_tasks`:** extend the SELECT list to include **`run_next`** (e.g. `t.run_next` alias or bare column) so each returned dict has **`run_next`** for API/UI.

14. **`sync_agent_tasks`:** extend the INSERT for missing keys to set **`run_next`** to **`''`** explicitly in the column list (match number of placeholders).

15. Run **`python3 -m py_compile src/data/database.py`** from repo root; fix until clean.

---

## Stage 2: Admin API (`api_admin.py`)

**Done when:** `GET /api/admin/tasks/<task_key>` JSON includes `run_next`; `PUT` with `run_next` updates DB; list rows from `GET /api/admin/tasks` include `run_next`; invalid `run_next` returns **400** with `{"error": "<message>"}`.

1. In **`update_task`** (`@admin_bp.route("/tasks/<task_key>", methods=["PUT"])`), after `body = request.get_json(silent=True) or {}`, determine **`rn = body["run_next"]` if `"run_next" in body else `None`** (distinguish absent key vs explicit `null`/empty string).

2. Pass **`run_next=rn`** into **`database.save_agent_task(...)`** alongside existing `agent_id`, `user_prompt`, `cache_prompt`, `nocache_prompt` kwargs.

3. Wrap **`database.save_agent_task`** call in **`try` / `except ValueError as e`:** return **`jsonify({"error": str(e)}), 400`** on validation failure.

4. In **`_enrich_tasks`**, inside the dict passed to **`rows.append({...})`**, add key **`"run_next": t.get("run_next") or ""`** so the task list API exposes the field without an extra DB round-trip per row.

5. **`get_task`** returns `database.get_agent_task` dict as JSON — no change if `run_next` is on the row dict; verify one manual trace that key appears.

6. Run **`python3 -m py_compile src/ui/api/api_admin.py`**.

---

## Stage 3: Manage Tasks UI (`AdminTaskPrompts.tsx`)

**Done when:** Edit modal shows Run Next dropdown; table shows run next target; Save persists via API; empty selection clears chain; invalid server error surfaces in toast.

1. Extend **`AgentTask`** interface with **`run_next?: string`** (optional for rows before load).

2. Add React state **`editRunNext`** as **`useState("")`**.

3. In **`openEdit`**, after `setEditNocache`, add **`setEditRunNext((full.run_next as string) || "")`**.

4. Add **`useMemo`** **`taskKeyOptions`**: sorted unique **`tasks.map(t => t.task_key)`** ascending (reuse existing **`tasks`** from load).

5. In the modal JSX, **after** the Agent `<select>` block and **before** the **`TabBar`**, add a **`div.dep-field`**:
   - **`<label className="dep-field-label">Run next</label>`**
   - **`<select className="dep-input" value={editRunNext} onChange={e => setEditRunNext(e.target.value)}>`**
   - First **`<option value="">`**: label text **`— none —`**
   - Then **`taskKeyOptions.map(k => <option key={k} value={k}>{k}</option>)`**

6. In **`handleSave`**, extend **`JSON.stringify`** body with **`run_next: editRunNext`** (always send string; empty string clears).

7. In the table **`<thead>`**, add a **`<th>`** after **Task Key** (or after **Agent** — pick **after Task Key**): label **`Run next`**.

8. In each **`<tbody>`** row, add **`<td>`** showing **`row.run_next || "—"`** with secondary text color like **`agent_id`** column.

9. From repo root, run **`cd src/ui/frontend && npx tsc -b --noEmit`** — fix type errors until clean.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — One DDL-touching migration path, data-layer versioning logic, Flask admin contract, and React Manage Tasks surface; four primary files across data / API / UI.

**Conf:** `Medium` — Versioning split (prompt vs metadata) mirrors existing `agent_id` behavior but must stay perfectly aligned or operators lose `run_next` on prompt edits; validation depends on `TASK_CONFIG` keys staying the task universe.

**Risk:** `Medium` — A migration bug bricks Manage Tasks saves; a bad `run_next` leaks to **AST-303** and could recurse wrong — server validation mitigates.

---

## Self-review vs `ASTRAL_CODE_RULES.md`

| Section | Check |
|---------|--------|
| §1.2 / §3.3 | Data + Flask + React only; no core `do_task` change in this ticket. |
| §2.1 config | `run_next` values are dynamic `task_key` strings, not new literals in `config.py`. |
| §2.4 batch | `run_next` is configuration only; no `batch_id` / claim pattern changes. |
| §3.5 naming | Column and JSON field **`run_next`** (snake_case); TS uses same string keys in `PUT` body. |

**Conflicts:** None identified.

---

## Review

**Branch:** `<agent>/ast-306-add-run-next-field-to-manage-tasks`  
**Diff reviewed:** `origin/dev`…`origin/<agent>/ast-306-add-run-next-field-to-manage-tasks` (merge-base `50aed96`)  
**Implementation commit (code):** `88eabf190f29247056a2fe68d3433d8f8f9f0853`  
**Reviewed:** 2026-05-04 — Radia (`e-review-linear`). Radia’s narrative below may land in a later doc-only commit on this branch.

### What's solid

- **Plan fidelity (Stages 1–3):** `agent_task.run_next` in header inventory, CREATE/ALTER/migration paths, `_validate_run_next` (self-loop + `TASK_CONFIG` membership), `save_agent_task` versioning excludes `run_next` from `content_changed` while still persisting it on new versions, metadata-only UPDATE path, `list_candidate_tasks` / `sync_agent_tasks` wiring — matches the execution doc.
- **§1.2 / §3.2–§3.3:** Data layer owns DDL + upsert; `TASK_CONFIG` import for validation is already established for this module; no `do_task` / dispatcher edits (scope stays storage + admin surface per plan).
- **§3.5:** `run_next` snake_case end-to-end; React `PUT` sends `run_next` with the same semantics as the plan (`""` clears).
- **API:** `update_task` distinguishes absent `run_next` vs explicit body value; `ValueError` from validation maps to **400** + `{"error": ...}` as specified.
- **UI:** Modal `<select>` + table column + `openEdit` / `handleSave` wiring; `taskKeyOptions` matches the plan’s `useMemo` over loaded `tasks`.

### Issues

| Severity | Topic | Notes |
|----------|--------|--------|
| — | — | No fix-now items. |
| — | — | No discuss items. |
| Advisory | Broad `except ValueError` in `update_task` | Any `ValueError` raised inside `save_agent_task` becomes a client **400**. Fine while validation is the only `ValueError` source; if more raises appear later, consider narrowing or structured errors. |

### Recommended actions

| Priority | Action | Owner |
|----------|--------|-------|
| Advisory | When **AST-303** reads `run_next`, add an integration test that exercises a two-hop chain after this column ships (this ticket correctly stops short of chaining). | Ada / Hedy |

---

## Resolution

**Date:** 2026-05-04 (`check-linear` / `f-resolve-linear`)

- **Fix-now / discuss:** none from Radia’s review.
- **Advisory (`update_task` + `ValueError`):** left as-is — Radia noted it is acceptable while validation is the only `ValueError` source inside `save_agent_task`; a dedicated typed error can wait until additional `ValueError` paths appear.

