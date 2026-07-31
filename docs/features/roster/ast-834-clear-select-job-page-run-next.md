<!-- linear-archive: AST-834 archived 2026-07-22 -->

## Linear archive (AST-834)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-834/clear-stale-select-job-page-run-next-in-manage-tasks-json-for-manage  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-833 — json for manage tasks has a run_next set for select_job_page  
**Blocked by / blocks / related:** parent: AST-833

### Description

## What this implements

Clear the stale `run_next: parse_job_list` link on the `select_job_page` agent_task row (Manage Tasks JSON / `agent_task` table), add an idempotent migration so AST-469 does not re-apply the link, and ensure the PJL_READY decomposed dispatch path does not invoke `parse_job_list` in the same execution. Update UAT fixture and tests that assume the old default. If clearing agent_task `run_next` breaks the JOBS_FOUND `jobs_found_process_job_site` path, restore select→parse orchestration in roster code without re-seeding Manage Tasks `run_next`.

## Acceptance criteria

1. Manage Tasks / `agent_task` export for `select_job_page` shows `run_next` empty (not `parse_job_list`).
2. Running Scheduled Actions `select_job_page` at PJL_READY for a company that returns `JOBLIST_TITLES`: company reaches `JOBLIST_IDENTIFIED`; no `parse_job_list` agent hop in the same batch/execution; `company_data` holds selection fields consumed later by parse dispatch.
3. Running Scheduled Actions `parse_job_list` at JOBLIST_IDENTIFIED still reaches `WATCH` (or existing retry/fail states) using persisted `company_data` — no regression on the decomposed parse hop.
4. JOBS_FOUND companies processed via `jobs_found_process_job_site` still reach the same terminal states as before this change for equivalent page content.
5. Component tests and AST-756 fixture updated; green test run.

## Boundaries

* Does not change `dispatch_task` rows (Scheduled Actions).
* Does not change `parse_job_list` dispatch behavior or `JOBLIST_IDENTIFIED` trigger.
* Does not change `select_job_page` or `parse_job_list` prompts.
* Sibling tickets: none — this is the sole implementation child for AST-833.

## Notes for planning

* Primary files: `src/data/database.py` (migration / schema ensure), `src/core/roster.py` (JOBS_FOUND path if needed), `docs/uat-fixtures/AST-756/expected-agent_task.json`, `tests/component/core/test_agent.py`, `tests/component/core/test_roster.py`.
* AST-469 `_apply_ast469_select_job_page_run_next_migration` must be neutralized or superseded so it does not re-set `run_next`.
* PJL_READY path already uses `chain_parse=False` in `run_select_job_page_dispatch` — verify `do_task` does not still chain via DB `run_next` when `resolve_run_next_live` is absent.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/ast-833-select-job-page-run-next`, child `sub/AST-833/<child-segment>`. Created at **dispatch-parent**. Engineers publish to `origin/<sub-ref>` — never Linear `gitBranchName` when it disagrees.

### Comments

#### radia — 2026-06-27T20:16:09.349Z
### Plan fidelity

Stages 2–3 match plan: AST-469 migration neutralized; `_apply_ast834_clear_select_job_page_run_next_migration` clears stale `select_job_page` → `parse_job_list` link idempotently; repo JSON + AST-756 fixture byte-identical with `run_next=""`. Stage 4 skipped — no `roster.py` edits; JOBS_FOUND covered by existing select-only fallback.

**Diff:** `origin/dev...origin/sub/AST-833/AST-834-clear-select-job-page-run-next` @ `38232b5` (product `705b840` · `3ce83b4`).

### ASTRAL_CODE_RULES

| Rule | Verdict |
|------|---------|
| §2.6 state machine | Decomposed PJL_READY select stays single-hop; parse remains separate JOBLIST_IDENTIFIED dispatch. |
| §3.5 naming | `_apply_ast834_*` follows migration convention; AST-469 supersede matches AST-685 pattern. |
| §1.5 data layer | No new logging; migration swallows `sqlite3.Error` same as adjacent migrations — bounded. |

### Issues

**fix-now:** None.

**discuss:** None.

**advisory:**
- Publish ref rollup includes sibling test/bible commits from `merge-tests` (AST-825–832, AST-830/831) — product diff vs `origin/dev` is AST-834-only (`src/data/database.py` + JSON pair). Expected epic rollup.
- `_apply_ast834_clear_select_job_page_run_next_migration` clears only when stripped `run_next == "parse_job_list"` — whitespace-padded values would not match (unlikely).

### Doc

`docs/features/roster/ast-834-clear-select-job-page-run-next.md` — Radia review section @ `38232b5`.

**Outcome:** 0 fix-now · 0 discuss · 2 advisory — clean; ready for `resolve-child`.

#### betty — 2026-06-27T20:13:03.078Z
## QA test manifest (AST-834)

**Publish:** `origin/sub/AST-833/AST-834-clear-select-job-page-run-next` @ `57e99c7` (`merge-tests(AST-834): origin/tests 828142e`)

**Bible shasum:** `docs/test-bible/data/database/agent_tasks.md` → `f348ffe470abc6e4964b63205aba81b5c76527f3514e0b682aad4ffb311bc0ff`

### Manifest (test-child)

1. **Migration + schema ensure (required):**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agent_tasks.py::TestAst834ClearSelectJobPageRunNextMigration \
  -q
```

2. **Repo/fixture parity + empty catalog `run_next` (required):**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  -q
```

3. **Decomposed PJL_READY select — no in-process parse hop (required):**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestAst834SelectJobPageRunNextClear \
  tests/component/core/test_agent.py::TestAst834SelectJobPageEmptyRunNext \
  -q
```

4. **Regression — AST-469 explicit chain + JOBS_FOUND select-only fallback (required):**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst469ResolveRunNextLive \
  tests/component/core/test_roster.py::test_find_joblist_titles_routes_select_only_when_run_next_parent_missing \
  -q
```

**Pass criterion:** pytest green on items 1–4 — not zero-arg harness / branch-lock gate.

**Stage 4 (roster.py):** skipped — narrowed manifest green without product roster edits.

#### hedy — 2026-06-27T20:08:54.790Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-833/AST-834-clear-select-job-page-run-next/docs/features/roster/ast-834-clear-select-job-page-run-next.md

**Scope:** `Single-Component` — `database.py` migration to neutralize AST-469 re-seed and clear `select_job_page.run_next`, plus byte-identical sync of `data/admin/agent_task.json` and `docs/uat-fixtures/AST-756/expected-agent_task.json`; optional narrow `roster.py` branch only if JOBS_FOUND regresses after catalog clear.

**Conf:** `high` — PJL_READY dispatch already passes `chain_parse=False` but `do_task` still chains via stale DB `run_next`; fix is migration + repo JSON sync, matching AST-685 supersede / AST-786 fixture patterns.

**Risk:** `Medium` — JOBS_FOUND today relies on AST-469 `run_next` chain or `_finalize_joblist_titles_select_only` fallback; Stage 4 is gated on component tests before any roster orchestration change.

---

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

---

## Radia review (2026-06-27)

**Diff:** `origin/dev...origin/sub/AST-833/AST-834-clear-select-job-page-run-next` @ `57e99c7`  
**Product commits:** `705b840` database migration · `3ce83b4` repo JSON + AST-756 fixture  
**Tests:** `828142e` AST-834 manifest · `57e99c7` merge-tests rollup (sibling manifests on branch — product footprint AST-834 only)

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | Stages 2–3 delivered as specified; Stage 4 correctly skipped — no `roster.py` edits; review stub documents green targeted roster/agent tests. |
| Migration (§3.5) | `_apply_ast469_select_job_page_run_next_migration` neutralized (early return + supersede docstring); `_apply_ast834_clear_select_job_page_run_next_migration` clears only `select_job_page` current row when `run_next='parse_job_list'`; wired after AST-469 in `_ensure_agent_task_schema`; parameterized UPDATE; idempotent on empty/other values. |
| Catalog sync (AST-786) | `data/admin/agent_task.json` and `docs/uat-fixtures/AST-756/expected-agent_task.json` byte-identical with `select_job_page.run_next=""` — prevents startup re-import of stale link. |
| State machine (§2.6) | Decomposed PJL_READY select remains single-hop (`chain_parse=False`); parse dispatch at JOBLIST_IDENTIFIED unchanged; JOBS_FOUND select-only fallback preserved without Manage Tasks `run_next`. |
| Layering / logging | Data-layer only; no new logging; no cross-layer imports. |
| Tests + bible | Betty manifest (`TestAst834ClearSelectJobPageRunNextMigration`, `TestAst834SelectJobPageRunNextClear`, `TestAst834SelectJobPageEmptyRunNext`, repo JSON assertion) matches plan AC; AST-469 live-resolver regression retained. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **advisory** | Publish ref rollup | Branch includes sibling test/bible commits from `merge-tests` (AST-825–832, AST-830/831) — **product diff vs `origin/dev` is AST-834-only** (`database.py` + JSON pair). Expected epic worktree rollup; not scope smuggling into `src/`. |
| **advisory** | `_apply_ast834_clear_select_job_page_run_next_migration` | Clears only when stripped `run_next == "parse_job_list"` — whitespace-padded variants would not match (unlikely given AST-469 seeded exact value). |

### Recommended actions

| Item | Action |
|------|--------|
| fix-now | None — ready for `resolve-child`. |
| discuss | None. |
| advisory | Parent **AST-833** UAT: confirm PJL_READY select no longer chains parse in-process on staging after deploy. |

**Counts:** 0 fix-now · 0 discuss · 2 advisory

**Outcome:** Clean — ship.

— Radia

---

## Resolution (Hedy / resolve — 2026-06-27)

**Review:** Radia @ `38232b5` — 0 fix-now · 0 discuss · 2 advisory (rollup scope note; whitespace edge on migration guard — no change).

**Product changes:** None — review clean; Stages 2–3 already shipped (`705b840`, `3ce83b4`); Stage 4 skipped per plan.

**Verification:** Betty manifest items 1–4 green (13/13) on publish ref @ `38232b5`; §9a dry-run clean vs `origin/dev` and `origin/ftr/ast-833-select-job-page-run-next`.

**Resolved @ `38232b5`**
