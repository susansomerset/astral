# AST-834 — Clear stale select_job_page run_next in Manage Tasks

**Linear:** [AST-834 — Clear stale select_job_page run_next in Manage Tasks (json for manage tasks has a run_next set for select_job_page)](https://linear.app/astralcareermatch/issue/AST-834/clear-stale-select-job-page-run-next-in-manage-tasks-json-for-manage)

**Parent (reference only):** [AST-833 — json for manage tasks has a run_next set for select_job_page](https://linear.app/astralcareermatch/issue/AST-833/json-for-manage-tasks-has-a-run-next-set-for-select-job-page)

**Publish ref:** `origin/sub/AST-833/AST-834-clear-select-job-page-run-next`

**Summary:** AST-720/721 decomposed roster selection and parse into independent Scheduled Actions (`select_job_page` at **PJL_READY**, `parse_job_list` at **JOBLIST_IDENTIFIED**). The **`agent_task`** row for **`select_job_page`** still carries **`run_next: parse_job_list`** from AST-469. When **`run_select_job_page_dispatch`** runs with **`chain_parse=False`** (no **`resolve_run_next_live`**), **`do_task`** still reads DB **`run_next`** and chains **`parse_job_list`** in the same execution — wrong live content and wrong hop boundary. This ticket clears Manage Tasks / DB **`run_next`**, prevents AST-469 from re-seeding it, syncs repo JSON + UAT fixture, and preserves **JOBS_FOUND** terminal outcomes via the existing select-only parse fallback (or explicit roster orchestration if tests prove otherwise).

**Out of scope:** **`dispatch_task`** rows; **`parse_job_list`** dispatch at **JOBLIST_IDENTIFIED**; prompts; removing **`resolve_run_next_live`** / **`make_locate_parse_resolver`** helpers.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Neutralize **`_apply_ast469_select_job_page_run_next_migration`**; add idempotent **`_apply_ast834_clear_select_job_page_run_next_migration`**; call after AST-469 in **`_ensure_agent_task_schema`** | data |
| `data/admin/agent_task.json` | Set **`select_job_page`** **`run_next`** to **`""`** (empty string) | data |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Same **`run_next`** clear — must stay byte-identical to repo JSON per **AST-786** | docs |
| `src/core/roster.py` | **Conditional (Stage 3 only):** explicit select→parse orchestration for **`jobs_found_process_job_site`** when DB **`run_next`** is empty | core |

**Verify only (Betty / qa-child — engineer does not edit in build-child):**

| File | Change |
|------|--------|
| `tests/component/core/test_roster.py` | Assert PJL_READY **`run_select_job_page_dispatch`** does not invoke **`parse_job_list`** in same execution; **JOBS_FOUND** terminal states unchanged |
| `tests/component/core/test_agent.py` | **`TestAst469ResolveRunNextLive`** remains valid (explicit DB **`run_next`** + **`resolve_run_next_live`** in test mocks — not catalog default) |
| `tests/component/core/test_repo_admin_json.py` | **`TestAst786AgentTaskRepoJsonSeed`** still passes after fixture/repo sync |

---

## Stage 1: Confirm stale run_next causes in-process parse on PJL_READY (investigation — no product commit unless regression)

**Done when:** Engineer records that (a) repo JSON and UAT fixture both show **`select_job_page.run_next = "parse_job_list"`**, (b) **`_apply_ast469_select_job_page_run_next_migration`** would re-set that link on blank rows, and (c) **`run_select_job_page_dispatch`** passes **`chain_parse=False`** and strips **`resolve_run_next_live`** but **`do_task`** still chains when DB **`run_next`** is set and response is **`JOBLIST_TITLES`**.

1. Read-only repro of catalog state:

   ```bash
   python3 -c "
   import json; from pathlib import Path
   for p in ('data/admin/agent_task.json', 'docs/uat-fixtures/AST-756/expected-agent_task.json'):
       rows = json.loads(Path(p).read_text())
       r = next(x for x in rows if x.get('task_key')=='select_job_page')
       print(p, 'run_next=', repr(r.get('run_next')))
   "
   ```

   Expect both print **`'parse_job_list'`**.

2. Confirm AST-469 migration still sets link when blank:

   ```bash
   rg -n '_apply_ast469_select_job_page_run_next_migration' src/data/database.py
   sed -n '4550,4575p' src/data/database.py
   ```

   Expect UPDATE sets **`run_next='parse_job_list'`** when current row **`run_next`** is blank.

3. Confirm decomposed select strips resolver but not DB chain:

   ```bash
   rg -n 'chain_parse=False|resolve_run_next_live|run_select_job_page_dispatch' src/core/roster.py
   rg -n 'planned_next|effective_next|resolve_run_next_live' src/core/agent.py
   ```

   Expect **`run_select_job_page_dispatch`** → **`chain_parse=False`**; **`do_task`** reads **`agent_task_row.get("run_next")`** independently of ctx resolver.

4. **Stop gate:** If investigation shows **`select_job_page.run_next`** already empty in repo JSON but Susan still sees parse hop — post 🛑 on **AST-833** with Manage Tasks export + batch_id evidence; do not proceed (different root cause, e.g. dispatch-row **`run_next`** or wrong task key).

---

## Stage 2: Clear agent_task run_next and prevent AST-469 re-apply

**Done when:** Fresh app start / schema ensure leaves **`select_job_page`** current row with **`run_next=''`** even when AST-469 migration runs first; existing DBs with **`run_next='parse_job_list'`** are cleared idempotently.

1. In **`src/data/database.py`**, replace **`_apply_ast469_select_job_page_run_next_migration`** body with an immediate **`return`** and docstring:

   ```python
   """AST-469 superseded by AST-834: decomposed dispatch — select_job_page must not chain parse via Manage Tasks run_next."""
   ```

   ⚠️ **Decision:** Keep the function name and call site (minimal diff; migration history stays grep-friendly) rather than deleting the symbol — AST-834 clear migration owns the new behavior.

2. In the same file, add immediately after that function:

   ```python
   def _apply_ast834_clear_select_job_page_run_next_migration(conn: sqlite3.Connection) -> None:
       """AST-834: clear stale select_job_page → parse_job_list Manage Tasks link (idempotent)."""
       try:
           row = conn.execute(
               "SELECT task_key_uuid, run_next FROM agent_task WHERE task_key = 'select_job_page' AND current = 1 LIMIT 1"
           ).fetchone()
       except sqlite3.Error:
           return
       if not row:
           return
       if (row[1] or "").strip() != "parse_job_list":
           return
       conn.execute(
           "UPDATE agent_task SET run_next = '', updated_at = CURRENT_TIMESTAMP WHERE task_key_uuid = ?",
           (row[0],),
       )
       conn.commit()
   ```

3. In **`_ensure_agent_task_schema`**, immediately after the existing **`_apply_ast469_select_job_page_run_next_migration(conn)`** call, add:

   ```python
   _apply_ast834_clear_select_job_page_run_next_migration(conn)
   ```

4. Manual smoke (engineer, local DB or in-memory test pattern):

   ```bash
   python3 -c "
   from src.data import database as db
   conn = db._get_connection()
   try:
       db._ensure_agent_task_schema(conn)
       row = conn.execute(\"SELECT run_next FROM agent_task WHERE task_key='select_job_page' AND current=1\").fetchone()
       print('run_next after ensure:', repr(row[0] if row else None))
   finally:
       conn.close()
   "
   ```

   Expect **`''`** (empty string).

---

## Stage 3: Sync repo JSON and UAT fixture (byte-identical pair)

**Done when:** **`data/admin/agent_task.json`** and **`docs/uat-fixtures/AST-756/expected-agent_task.json`** match byte-for-byte; **`select_job_page`** row shows **`"run_next": ""`**; **`TestAst786AgentTaskRepoJsonSeed.test_repo_json_matches_uat_fixture_byte_for_byte`** passes.

1. In **`data/admin/agent_task.json`**, locate the current (**`"current": 1`**) object with **`"task_key": "select_job_page"`** and set **`"run_next"`** to **`""`** (empty string — not omitted).

2. Copy the full file bytes to **`docs/uat-fixtures/AST-756/expected-agent_task.json`** so the two files remain identical:

   ```bash
   cp data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json
   ```

3. Verify:

   ```bash
   cmp -s data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json && echo OK
   python3 -c "
   import json; from pathlib import Path
   r = next(x for x in json.loads(Path('data/admin/agent_task.json').read_text()) if x['task_key']=='select_job_page')
   assert r['run_next'] == '', r['run_next']
   print('select_job_page run_next empty OK')
   "
   ```

⚠️ **Decision:** Update repo JSON + fixture together — startup **`apply_agent_task_repo_json_startup`** would otherwise re-import **`parse_job_list`** after Stage 2 migration clears the live DB.

---

## Stage 4 (conditional): Preserve JOBS_FOUND select→parse outcomes without Manage Tasks run_next

**Done when:** **JOBS_FOUND** companies processed via **`jobs_found_process_job_site`** reach the same terminal states as before this change for equivalent page content (parent AC §4), with **`select_job_page.run_next`** empty in catalog.

**Enter this stage only if** targeted roster tests fail after Stages 2–3. **Do not** re-seed Manage Tasks **`run_next`**.

1. Run (test-child / local):

   ```bash
   ./scripts/testing/run_component_tests.sh \
     tests/component/core/test_roster.py::TestJobsFoundProcessJobSite469 \
     tests/component/core/test_roster.py::test_find_joblist_titles_routes_select_only_when_run_next_parent_missing \
     tests/component/core/test_roster.py::TestAst827TitleHandoffDomCull
   ```

   (Fix class path if pytest collection differs — use **`TestAst827TitleHandoffDomCull`** under **`test_roster.py`**.)

2. **If all green:** skip roster edits; document in Linear comment that **`_finalize_joblist_titles_select_only`** + **`_fetch_parse_job_list`** covers **JOBS_FOUND** when DB **`run_next`** is empty (**`chain_parse=True`**, no **`run_next_parent_parsed`**).

3. **If JOBS_FOUND regresses:** in **`src/core/roster.py`**, inside **`_find_job_page_from_assembled`**, in the **`JOBLIST_TITLES`** branch when **`chain_parse`** is **`True`**, **`decomposed`** is **`False`**, and **`res.get("run_next_parent_parsed")`** is **`None`** after **`do_task("select_job_page", …)`**, route to **`_finalize_joblist_titles_select_only(...)`** explicitly (today reached via the final **`return await _finalize_joblist_titles_select_only`** — verify **`chain_parse and pp is not None`** guard is not skipping it incorrectly; adjust only the branch condition, do not re-add DB **`run_next`**).

   Alternative if select-only path is insufficient for ledger/hop tokens: after successful **`select_job_page`** **`do_task`**, when **`chain_parse`** and **`make_locate_parse_resolver`** produced **`rslv`**, call:

   ```python
   parse_res = await do_task(
       "parse_job_list",
       live_content=<culled dom from rslv(parsed_top)[0]>,
       index=short_name,
       ctx=merged_ctx,
       debug=debug,
       chain_context=<JOB_LIST_VISIBLE from rslv when present>,
   )
   ```

   then **`return await _finalize_joblist_titles_after_chain(select_parsed, parse_res, …)`**.

   ⚠️ **Decision:** Prefer **`_finalize_joblist_titles_select_only`** first (existing AST-469 fallback, fewer hop-ledger moving parts); explicit **`do_task("parse_job_list")`** only if select-only terminal states diverge in tests.

4. **Stop gate:** If neither path restores **JOBS_FOUND** outcomes — post 🛑 on **AST-833** with failing test name, expected vs actual state, and batch_id; wait for Susan.

---

## Self-Assessment

**Scope:** `Single-Component` — **`database.py`** migration + repo JSON pair; optional narrow **`roster.py`** branch if **JOBS_FOUND** regresses.

**Conf:** `high` — root cause is catalog **`run_next`** + AST-469 re-seed conflicting with **`chain_parse=False`** decomposed dispatch; fix pattern matches **AST-685** migration supersede and **AST-786** fixture sync.

**Risk:** `Medium` — wrong migration could clear **`run_next`** on unrelated tasks or fail to sync repo JSON (re-import stale link); **JOBS_FOUND** depends on select-only parse fallback — Stage 4 contains explicit regression gate before roster edits.

---

## ASTRAL_CODE_RULES self-review

| Rule | Plan alignment |
|------|----------------|
| §1.3 DRY | Reuses existing **`_finalize_joblist_titles_select_only`** / AST-469 fallback; no duplicate parse pipeline |
| §2.1 config | No **`ROSTER_CONFIG`** / **`dispatch_task`** edits |
| §2.4 batch | No batch claim changes |
| §2.6 state machine | PJL_READY → **JOBLIST_IDENTIFIED** via **`_finalize_joblist_identified`** unchanged; parse hop remains separate dispatch |
| §3.3 imports | Stage 4 optional path stays within **`roster.py`** + existing **`do_task`** — no **`agent` → `roster`** cycle |
| §3.5 naming | New migration **`_apply_ast834_clear_select_job_page_run_next_migration`** follows **`_apply_astNNN_*`** convention |

No conflicts requiring **`conf-!!-NONE`**.

---

## Execution contract (for build-child)

- Execute stages in order; Stage 4 only on test failure after Stages 2–3.
- Do not edit **`tests/`**, **`docs/test-bible/**`**, or **`docs/ASTRAL_TEST_BIBLE.md`** — Betty owns test manifest updates for **`run_next`** catalog assumptions.
- Do not change **`dispatch_task`** seeds, **`parse_job_list`** dispatch entry, or **`select_job_page`** / **`parse_job_list`** prompts.
- Blocking ambiguity → 🛑 comment on **AST-833** parent per plan-child template.

---

## Review stub (Hedy / build)

**Publish ref:** `origin/sub/AST-833/AST-834-clear-select-job-page-run-next`

**Product commits:**

| SHA | Stage | Summary |
|-----|-------|---------|
| `705b840` | 2 | Neutralize AST-469 setter; add `_apply_ast834_clear_select_job_page_run_next_migration` |
| `3ce83b4` | 3 | Clear `select_job_page.run_next` in `data/admin/agent_task.json` + AST-756 fixture (byte-identical) |

**Stage 4:** Skipped — targeted roster/agent/repo tests green; `_finalize_joblist_titles_select_only` covers JOBS_FOUND without Manage Tasks `run_next`.

**Built @ `3ce83b4`**
