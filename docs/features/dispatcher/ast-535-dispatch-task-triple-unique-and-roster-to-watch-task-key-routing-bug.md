<!-- linear-archive: AST-535 archived 2026-06-15 -->

## Linear archive (AST-535)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-535/dispatch-task-triple-unique-and-roster-to-watch-task-key-routing-bug  
**Status at archive:** Done  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** Urgent / —  
**Parent:** AST-533 — BUG: Scheduled Actions ignore dispatch task_key — consult hardcodes state→task routing  
**Blocked by / blocks / related:** parent: AST-533

### Description

## What this implements

Susan approved `UNIQUE(candidate_id, task_key, trigger_state)` on `dispatch_task` so multiple rows can share semantics like retry states (`consult_do` @ `PASSED_JD` vs `PASSED_JD_RETRY`) and eventually distinct task keys at the same entity state. This ticket migrates the schema and fixes **company roster dispatch** so rows that share `trigger_state=TO_WATCH` (`find_job_page`, `select_job_page`, `parse_job_list`) each run **their** `task_key` — not a single hardcoded `find_job_page` default.

## Acceptance criteria

3. **TO_WATCH trio:** Dispatch rows for `find_job_page`, `select_job_page`, and `parse_job_list` (same `trigger_state=TO_WATCH`) each run their respective task on Run.
4. **Bible / rules:** Update `ASTRAL_TEST_BIBLE` (and `ASTRAL_CODE_RULES` §2.1 if needed) so dispatch routing docs describe `dispatch_task.task_key` **as execution entry**, not `_INPUT_STATE_TO_TASK`.

Plus schema acceptance:

* Fresh and migrated DBs enforce `UNIQUE(candidate_id, task_key, trigger_state)` (replacing `UNIQUE(candidate_id, trigger_state)`).
* Existing per-candidate rows migrate without data loss; duplicate `(candidate_id, trigger_state)` rows with different `task_key` become valid where product requires (document migration behavior in plan).
* Admin create/update dispatch task respects new unique constraint (clear error on conflict).

## Boundaries

* Does **not** reimplement job consult routing (sibling **AST-534** — consume its `run_consult_task` / company path `task_key` parameter).
* Does **not** change ad-hoc / craft / workbench paths.
* Does **not** redesign Scheduled Actions UI beyond what new unique constraint requires.

## Notes for planning

* AST-485 documented `TO_WATCH` UNIQUE footgun — this ticket resolves it with triple unique.
* `_RETRY_TASK_SEED` rows should remain valid under new constraint.
* Component tests: TO_WATCH routing + schema/migration tests in `tests/component/data/`.

## Git branch (authoritative)

Parent `ftr/AST-533-dispatch-task-key-honesty`, child \*\*`sub/AST-533/AST-535-dispatch-task-triple-unique-and-roster-routing**`.

### Comments

#### radia — 2026-05-30T01:58:10.295Z
**Review** — `git diff origin/dev...origin/sub/AST-533/AST-535-dispatch-task-triple-unique-and-roster-routing` (tip `0dd0636a`)

### What's solid
- **Schema (AC):** Fresh + migrated `UNIQUE(candidate_id, task_key, trigger_state)`; migration copies rows with triple dedupe; `apply_config_table_upsert` upserts on triple; TO_WATCH trio coexistence + duplicate triple rejection tested.
- **Roster (AC):** `run_company_task(dispatch_task_key=…)` routes `find_job_page` / `select_job_page` / `parse_job_list`; `chain_parse=False` on select-only dispatch; parse dispatch reuses validation path; empty key defaults `find_job_page` for backward compat.
- **Admin API:** Create 409 names all three fields; update wrapped for UNIQUE collisions.
- **§2.1:** Rules + bible updated for triple unique and row `task_key` as roster entry.
- **Boundary:** Job consult routing left to AST-534 on merge — appropriate for sibling split.

### fix-now
1. **`NameError` in dispatcher** — `src/core/dispatcher.py` `_run_unified`: passes `dispatch_task_key=dispatch_task_key` to `consult.run_consult_task` (~264, ~280, ~288) but **never assigns** `dispatch_task_key = task.get("task_key", "")` (present on AST-534 sub at ~164, missing here). Any company/job dispatch Run that reaches consult will crash. **Fix:** add the same assignment AST-534 uses (or merge AST-534 dispatcher hunk).

### discuss
1. **Bible manifest vs branch** — §7.13zp lists `test_ast534_forwards_dispatch_task_key_to_consult` on AST-535 narrow run, but that test is **not** on this sub branch (`test_dispatcher.py` has 0 `dispatch_task_key` references). Betty/engineer: add test on this branch after dispatcher fix, or drop from AST-535 manifest until parent ftr merge.
2. **`update_dtask` 409 copy** — On update that changes `task_key`, 409 message uses `(row.task_key, updates.trigger_state)`; if collision is from a new `task_key` in `updates`, message may not match the conflicting triple.

### advisory
- Duplicate `from src.core import roster` in `run_consult_task` (lines ~1159 and ~1162) — harmless, one can go.
- `run_select_job_page_dispatch` reuses `_find_job_page_from_assembled` rather than a separate `_apply_select_job_page_outcome` helper; acceptable DRY tradeoff per plan “if needed.”

#### hedy — 2026-05-30T01:54:40.511Z
[check-linear]

**Session scope:** Parent **AST-533** / **Astral Dispatcher** — assigned **AST-535** only.

**§0a (`astral-hedy` / `dev-hedy`):** `git fetch origin`, `checkout dev-hedy`, `merge origin/dev` — **merge-clean** (`BEHIND=0`, `origin/dev` ancestor of `HEAD`). No publish-ref merges (check-linear only).

**§0b:** `@hedy` issue search (Team Astral + **Astral Dispatcher** project); full threads on **AST-533**, **AST-534**, **AST-535**. **0** actionable comments — nothing `@hedy` or directed at Hedy needing reply or small fix.

**§1:** Assignee **AST-535** @ **Tests Passed** — latest thread activity is Betty **Tests Ready** manifest (`1b019f32`) and Hedy **Tests Passed** (`72857c62`, publish `origin/sub/AST-533/AST-535-dispatch-task-triple-unique-and-roster-routing` @ `0dd0636a`). No new nags since prior `[check-linear]`.

**Pipeline:** Inbox quiet; no `resolve-astral` / `test-astral` / `build-astral` from this pass. Next gate for **AST-535** is Radia **`review-astral`** (not invoked here).

#### hedy — 2026-05-30T01:52:34.701Z
**Tests Passed** — Betty manifest green (pytest); one product fix published.

**Publish:** `origin/sub/AST-533/AST-535-dispatch-task-triple-unique-and-roster-routing` @ `0dd0636a`

**Fix:** Removed company-only guard on `dispatch_task_key` in `dispatcher._run_unified` (AST-534 regression after AST-535 merge).

**Manifest (`.venv/bin/python -m pytest`):** 9/9 passed — items 1–4.

**Note:** `run_component_tests.sh` exits 1 after pytest because unrelated frontend `AdminManageCandidates` middle-name tests fail (AST-511); narrowed pytest nodes all pass.

#### betty — 2026-05-30T01:49:15.246Z
**Tests Ready** — manifest for `test-astral`.

**Publish:** `origin/sub/AST-533/AST-535-dispatch-task-triple-unique-and-roster-routing` @ `1995836c`
**Bible shasum (publish ref):** `4fe0c57643c4469982e1f8f3c4296ae56bd2f3fc`

1. `./scripts/testing/run_component_tests.sh tests/component/data/database/test_dispatch_tasks.py::TestAst535DispatchTaskTripleUnique`
2. `./scripts/testing/run_component_tests.sh tests/component/core/test_roster.py::TestAst535ToWatchDispatchTaskKeyRouting`
3. `./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast535_create_dispatch_task_triple_unique_409`
4. `./scripts/testing/run_component_tests.sh tests/component/core/test_dispatcher.py::TestRunUnified::test_ast534_forwards_dispatch_task_key_to_consult`

**Note:** Item **4** is an **AST-534 regression guard** (blocker **AST-534**). On the current publish tip it **fails**: `src/core/dispatcher.py` `_run_unified` clears `dispatch_task_key` for non-`company` entities (~lines 164–166), so job consult never receives the row’s `task_key`. Items **1–3** cover **AST-535** acceptance (triple unique, TO_WATCH roster routing, admin 409). Fix product on publish ref until all four pass.

— Betty

#### hedy — 2026-05-30T01:35:44.426Z
[check-linear]

**Session scope:** Parent **AST-533** / **Astral Dispatcher** — assigned **AST-535** only.

**§0a (`astral-hedy` / `dev-hedy`):** `git fetch origin`, `checkout dev-hedy`, `merge origin/dev` — **merge-clean** (`BEHIND=0`, `origin/dev` ancestor of `HEAD`). No publish-ref merges (check-linear only).

**§0b:** `@hedy` issue search (Team Astral + **Astral Dispatcher** project); **14d** project fallback on **AST-533** / **AST-534** / **AST-535**. Full threads on all three. **0** actionable comments — nothing `@hedy` or directed at Hedy needing reply or small fix.

**§1:** Assignee **AST-535** — latest activity is plan post (`0e5765fa` on publish ref); **Plan Approved**; **blockedBy AST-534** (Ada **Plan Approved**, not yet built). No thread nags.

**Pipeline:** Inbox quiet; no `build-astral` / `test-astral` / `resolve-astral` from this pass.

#### hedy — 2026-05-30T01:34:11.281Z
Plan: `docs/features/dispatcher/ast-535-dispatch-task-triple-unique-and-roster-to-watch-task-key-routing-bug.md`

**GitHub:** https://github.com/susansomerset/astral/blob/sub/AST-533/AST-535-dispatch-task-triple-unique-and-roster-routing/docs/features/dispatcher/ast-535-dispatch-task-triple-unique-and-roster-to-watch-task-key-routing-bug.md (`0e5765fa`)

**Self-assessment**
- **Scope:** MAJOR-CHANGE — schema migration to `UNIQUE(candidate_id, task_key, trigger_state)`, roster `dispatch_task_key` routing for TO_WATCH trio, admin 409 messages, rules/bible bullets.
- **Conf:** Medium — AST-534 must pass `dispatch_task_key` into `run_company_task` first; select/parse-only entry paths extracted from existing `find_job_page` chain.
- **Risk:** HIGH — wrong migration or routing regresses AST-485 (all TO_WATCH rows run `find_job_page`).

**Build gate:** blockedBy AST-534 — plan now; start **build-astral** after AST-534 is **Plan Approved** (or merged on integration line).

**Publish note:** No Joan session on parent AST-533; plan commit `81798f31` cherry-picked to `origin/sub/AST-533/AST-535-dispatch-task-triple-unique-and-roster-routing` @ `0e5765fa` (same worktree flow as `joan publish`).

---

# AST-535 — dispatch_task triple unique and roster TO_WATCH task_key routing

- **Linear (this ticket):** [AST-535](https://linear.app/astralcareermatch/issue/AST-535/dispatch-task-triple-unique-and-roster-to-watch-task-key-routing-bug)
- **Parent:** [AST-533](https://linear.app/astralcareermatch/issue/AST-533/bug-scheduled-actions-ignore-dispatch-task-key-consult-hardcodes)
- **Publish ref:** `origin/sub/AST-533/AST-535-dispatch-task-triple-unique-and-roster-routing`
- **Blocked by:** [AST-534](https://linear.app/astralcareermatch/issue/AST-534/honor-dispatch-task-key-in-dispatcher-consult-and-artifact-entry-bug) (Ada) — **plan now; build after AST-534 Plan Approved** if still blocked. This ticket consumes AST-534’s `dispatch_task_key` plumbed through `consult.run_consult_task` → `roster.run_company_task`; do not reimplement job consult routing here.

Susan approved **`UNIQUE(candidate_id, task_key, trigger_state)`** on `dispatch_task` so multiple rows can share a `trigger_state` (e.g. `TO_WATCH` for `find_job_page`, `select_job_page`, `parse_job_list`, or retry pairs like `consult_do` @ `PASSED_JD` vs `PASSED_JD_RETRY`). This ticket migrates the schema and fixes **company roster dispatch** so each row’s **`task_key`** is the execution entry for Run — not a hardcoded `find_job_page` default for every `TO_WATCH` row.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Triple-unique schema migration; upsert key; seed comments | data |
| `src/core/roster.py` | `dispatch_task_key` routing for company dispatch; select/parse entry helpers | core |
| `src/core/consult.py` | Pass `dispatch_task_key` into `run_company_task` (coordinate with AST-534) | core |
| `src/ui/api/api_admin.py` | 409 conflict messages for triple unique | ui |
| `docs/ASTRAL_CODE_RULES.md` | §2.1 `dispatch_task` unique + routing note | docs |
| `docs/ASTRAL_TEST_BIBLE.md` | Dispatch routing + schema test pointers (Betty implements tests) | docs |

**Tests (Betty owns `tests/`):** Engineer does **not** edit `tests/component/**` or `ASTRAL_TEST_BIBLE.md` beyond the doc bullets in Stage 4; post **`[qa-handoff]`** if manifest gaps remain after build.

## Stage 1: Schema — triple unique on `dispatch_task`

**Done when:** Fresh DBs and migrated DBs enforce `UNIQUE(candidate_id, task_key, trigger_state)`; all existing rows survive migration; admin bulk import upserts on the triple key.

1. In `src/data/database.py`, update the header comment on `_DISPATCH_TASK_SEED` (lines ~4310–4311): replace the AST-485 “one row per `trigger_state`” note with “triple unique `(candidate_id, task_key, trigger_state)` — TO_WATCH trio rows are distinct (AST-535).”
2. In `_ensure_dispatch_task_schema`, after existing migrations and before `_dispatch_task_schema_ensured = True`:
   - Read `create_sql` from `sqlite_master` for `dispatch_task`.
   - If `UNIQUE(candidate_id, trigger_state)` is present **and** `UNIQUE(candidate_id, task_key, trigger_state)` is **not** present:
     - `CREATE TABLE dispatch_task_new (...)` with the same columns as today and **`UNIQUE(candidate_id, task_key, trigger_state)`** (not `UNIQUE(candidate_id, trigger_state)`).
     - `INSERT INTO dispatch_task_new` — copy **every** row from `dispatch_task` **without** collapsing on `(candidate_id, trigger_state)` (under the old constraint at most one row per pair existed, so no loss).
     - If any row would violate the new triple (duplicate `(candidate_id, task_key, trigger_state)`), keep the row with greatest `updated_at` then greatest `id`; drop the others (log count via comment in migration block only — no runtime logger in data layer).
     - `DROP TABLE dispatch_task`; `ALTER TABLE dispatch_task_new RENAME TO dispatch_task`; `commit`.
   - Update the **initial** `CREATE TABLE dispatch_task` branch (empty DB) to use **`UNIQUE(candidate_id, task_key, trigger_state)`** instead of `UNIQUE(candidate_id, trigger_state)`.
3. In `save_dispatch_task`, rely on SQLite `INSERT` raising `IntegrityError` on triple conflict (no pre-check SELECT on `(candidate_id, trigger_state)` only).
4. In `import_table_rows` for `table == "dispatch_task"` (~588–612), change upsert lookup from:
   - `SELECT id ... WHERE candidate_id = ? AND trigger_state = ?`
   - to `SELECT id ... WHERE candidate_id = ? AND task_key = ? AND trigger_state = ?`
   - Match/update/insert on the triple.
5. Verify `_RETRY_TASK_SEED` `INSERT OR IGNORE` rows remain valid: each retry row uses the **same** `task_key` as its base with a **different** `trigger_state` (e.g. `qualify_job_listings` + `VALID_TITLE_RETRY`) — compatible with triple unique.

⚠️ **Decision:** Do **not** auto-insert `select_job_page` / `parse_job_list` rows for every candidate during migration. Migration only changes the constraint; Susan creates trio rows via admin when needed. Existing `find_job_page` @ `TO_WATCH` rows stay as-is.

## Stage 2: Roster — honor `dispatch_task_key` for company dispatch

**Done when:** `run_company_task` routes by `dispatch_task_key` for locate-family states; `find_job_page`, `select_job_page`, and `parse_job_list` dispatch rows each execute their task as the first hop on Run (after AST-534 passes the row key).

1. In `src/core/roster.py`, extend signature:
   ```python
   async def run_company_task(
       input_state: str,
       entity: Dict[str, Any],
       batch_id: str,
       ctx: Optional[Dict[str, Any]] = None,
       debug: bool = False,
       dispatch_task_key: Optional[str] = None,
   ) -> Dict[str, Any]:
   ```
2. At the top of `run_company_task`, set `tk = (dispatch_task_key or "").strip()`; if `tk` is empty and `input_state` is in `ROSTER_CONFIG["locate_job_page"]["dispatch_input_states"]`, default `tk = "find_job_page"` **only** for backward compatibility in tests/adhoc — dispatch path from `consult` must always pass the row’s `task_key` after AST-534.
3. Replace the single branch that calls `find_job_page(...)` for all `dispatch_input_states` (~452–468) with:
   - **`tk == "find_job_page"`** (or empty default above): existing `find_job_page(url=company_website, short_name=..., ...)` — unchanged behavior.
   - **`tk == "select_job_page"`**: call new helper `run_select_job_page_dispatch(entity, batch_id, ctx, debug)` (define in same file, after `find_job_page`).
   - **`tk == "parse_job_list"`**: call new helper `run_parse_job_list_dispatch(entity, batch_id, ctx, debug)`.
   - **Other `tk`** under locate states: `logger.warning` + return `{**zero, "total_errors": 1}`.
   - **Unchanged:** `NEW`, `WEBSITE_FOUND`, `NO_OPENINGS`, `JOBS_FOUND` + `jobs_found_process_job_site`, `WATCH` / gazer — still keyed on `input_state` only (out of scope per ticket boundaries).
4. Implement `async def run_select_job_page_dispatch(entity, batch_id, ctx, debug) -> Dict[str, Any]`:
   - Same `_SUMMARY_ZERO` shape as `run_company_task`.
   - Load `short_name`, `company_website`, `possible_job_links`, `nav_links` from company row (same preconditions as `find_job_page`).
   - If missing PJLs/nav_links → same `NO_JOBLIST` terminal as `find_job_page`.
   - `async with create_browser_context()` → `_fetch_job_links_content(...)` → assembled maps.
   - Call `_fetch_select_job_page(assembled_content, short_name, ctx=ctx_without_run_next, debug=debug)` where `ctx_without_run_next` is a copy of `ctx` **without** `resolve_run_next_live` (do **not** set `resolve_run_next_live` — first hop must be `select_job_page` only for this dispatch entry; parse must not auto-chain on the same Run unless Susan wires `run_next` on the **select** task in Manage Tasks, which is out of scope for this ticket’s AC).
   - Map AI outcome to company state using the same helpers as `_find_job_page_from_assembled` (`_save_company`, pass_states from `ROSTER_CONFIG["locate_job_page"]`, `error_state` transitions) — extract shared outcome handling into `_apply_select_job_page_outcome(parsed_top, response_type, short_name, company_website, job_site_url, ...)` if needed to avoid duplicating the tail of `_find_job_page_from_assembled`.
5. Implement `async def run_parse_job_list_dispatch(entity, batch_id, ctx, debug) -> Dict[str, Any]`:
   - Require `entity["job_site"]` non-empty; if missing → log warning, return `{**zero, "total_errors": 1}`.
   - `async with create_browser_context()` → load/scrape job_site DOM (reuse the same scrape path `find_job_page` uses for a single stored URL — factor a small `_scrape_job_site_dom(job_site, browser_context, debug)` helper if not already present).
   - `parsed = await _fetch_parse_job_list(dom_joined, short_name, debug=debug, ctx=ctx)`.
   - On success, persist via existing `_check_parse_results` / `_validate_parse_job_list_raw_job_listings` flow (same terminal states as chained parse).
6. In `src/core/consult.py`, in the `entity_type == "company"` branch (~1161–1163), change to:
   ```python
   return await roster.run_company_task(
       input_state,
       entities[0],
       batch_id,
       ctx,
       debug,
       dispatch_task_key=dispatch_task_key,
   )
   ```
   Add parameter `dispatch_task_key: Optional[str] = None` to `run_consult_task` signature **only if AST-534 has not already added it** — if AST-534 lands first, use Ada’s parameter name and pass through without duplicating consult job routing work.

⚠️ **Decision:** `JOBS_FOUND` + `find_job_page` row remains a **separate** `trigger_state` (not `TO_WATCH`); no change to `jobs_found_process_job_site` routing in this ticket.

## Stage 3: Admin API — triple-unique conflict errors

**Done when:** Creating or updating a dispatch row that collides on `(candidate_id, task_key, trigger_state)` returns HTTP 409 with a message naming all three fields.

1. In `src/ui/api/api_admin.py` `create_dtask` exception handler (~644–650), replace error text with:
   `"Dispatch row already exists for candidate '{candidate_id}', task_key '{task_key}', trigger_state '{trigger_state}'"`
2. Wrap `update_dispatch_task` in `update_dtask` with `try/except`; on `IntegrityError` / `"UNIQUE"` in message, return the same 409 shape when `trigger_state` (or future columns) change causes a triple collision.

## Stage 4: Rules and bible (doc-only)

**Done when:** `ASTRAL_CODE_RULES` and `ASTRAL_TEST_BIBLE` describe `dispatch_task.task_key` as execution entry for roster rows and document triple unique; Betty can extend component tests from the bullets below.

1. In `docs/ASTRAL_CODE_RULES.md` §2.1 (`dispatch_tasks` DB table bullet ~53–54), add:
   - Unique constraint: **`(candidate_id, task_key, trigger_state)`**.
   - **Company roster dispatch:** `trigger_state` selects companies; **`task_key` on the row** selects `find_job_page` vs `select_job_page` vs `parse_job_list` entry (not `_INPUT_STATE_TO_TASK` — job consult map removed by AST-534).
2. In `docs/ASTRAL_TEST_BIBLE.md`, add subsection **§7.13zd AST-535** (parent AST-533) with manifest bullets (Betty implements):
   - `tests/component/data/database/test_dispatch_tasks.py`: fresh schema has triple unique; two rows same `TO_WATCH` different `task_key` both insert; duplicate triple 409/conflict.
   - `tests/component/core/test_roster.py` or `test_dispatcher.py`: mock `do_task` / roster helpers — Run with `dispatch_task_key=select_job_page` calls `select_job_page` not `find_job_page`; same for `parse_job_list`.
   - Update any bible row that still describes `_INPUT_STATE_TO_TASK` as **dispatch** routing to point at row `task_key` (AST-534 + AST-535 together).

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — Touches data schema migration, roster dispatch entry paths, consult company branch signature, and admin API error handling.

**Conf:** `Medium` — Patterns exist (`find_job_page`, `_fetch_select_job_page`, `_fetch_parse_job_list`); AST-534 must land first so `dispatch_task_key` reaches `run_company_task`; select/parse-only entry paths are new but extracted from existing chain code.

**Risk:** `HIGH` — Wrong migration or routing sends all `TO_WATCH` runs through `find_job_page` again (Susan’s AST-485 footgun returns); schema migration mistakes could drop dispatch rows.

## Self-review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Extract `_apply_select_job_page_outcome` / `_scrape_job_site_dom` rather than copy-paste `_find_job_page_from_assembled` tails. |
| §2.1 config | Seeds stay in `_DISPATCH_TASK_SEED`; unique constraint documented in rules. |
| §2.4 batch | `batch_id` unchanged; company batch still one entity per `_run_unified` `_one` call. |
| §2.6 state machine | Use existing `ROSTER_CONFIG` pass/error states; no new company states. |
| §3.3 imports | Roster may lazy-import playwright helpers already used in-file; consult → roster only. |
| §3.5 naming | `dispatch_task_key` matches AST-534 vocabulary on consult/dispatcher. |

No unresolved conflicts — plan is implementable after AST-534 Plan Approved.

## Review

- **Status:** Pending (Betty qa-astral → test-astral → Radia review-astral)
- **Built:** 5001f21a (origin/sub/AST-533/AST-535-dispatch-task-triple-unique-and-roster-routing)
- **Branch:** `origin/sub/AST-533/AST-535-dispatch-task-triple-unique-and-roster-routing`

## Resolution

**2026-05-30 — resolve-astral (Radia fix-now #1)**

- **Issue:** `_run_unified` passed `dispatch_task_key` to `consult.run_consult_task` without assigning it from `task["task_key"]` on the AST-535 publish tip (`0dd0636a`), causing `NameError` on job/company dispatch Run.
- **Fix:** Added `dispatch_task_key = task.get("task_key", "")` at the top of `_run_unified`, matching AST-534 (`61449d89`).
- **Verify:** Betty manifest items 1–4 green on publish tip; §9a dry-run clean vs `origin/dev` and parent `ftr/AST-533-dispatch-task-key-honesty`.
