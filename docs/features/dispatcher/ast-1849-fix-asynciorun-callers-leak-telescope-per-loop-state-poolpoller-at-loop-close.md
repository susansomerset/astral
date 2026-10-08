# AST-1849 — fix: asyncio.run callers leak Telescope per-loop state (pool/poller) at loop close

<!-- linear-archive: AST-1849 archived 2026-10-07 -->

## Linear archive (AST-1849)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1849/fix-asynciorun-callers-leak-telescope-per-loop-state-poolpoller-at  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1841 — [✅/Abrams] parse_job_list INTERRUPTED: 1 error(s) / 0 processed | parse_job_list-c37707f0-5b75-4ed5-af36-c0148002bea6  
**Blocked by / blocks / related:** parent: AST-1841

### Description

## What this implements

One-shot `asyncio.run(...)` loops that reach Telescope release its per-loop state (asyncpg pool, LISTEN connection, `telescope-result-poller`, wake tasks) before the loop closes, the same guarantee `dispatcher._task_thread_target` already has via `close_loop_resources()` (`c86d8b5c`). A single sync runner in `src/external/telescope.py` wraps `asyncio.run` and always awaits `close_loop_resources()` in a `finally`. The five confirmed Telescope-reaching call sites switch to it (`contact.py` added at the plan-fix scope gate).

## Scope

## Component scope

* `src/external/telescope.py` — modified. It owns the per-loop Telescope state and its teardown (`close_loop_resources`), so the one-shot-loop runner that guarantees that teardown belongs here too.
* `src/ui/api/api_admin.py` — modified. The admin Telescope scrape handler runs `admin_telescope_scrape` under a bare `asyncio.run`.
* `src/ui/api/api_meteorite.py` — modified. `land_meteorite` reaches Telescope (`meteorite.py` → `telescope.get_visible_text`) under a bare `asyncio.run`.
* `src/ui/api/api_inbox.py` — modified. `_land_all` lands meteorites (same Telescope reach) under a bare `asyncio.run`.
* `src/core/gazer.py` — modified. `ingest_meteorite_jobs_from_email_html_sync` is the sync wrapper for Flask/inbox callers and uses a bare `asyncio.run`.
* `src/core/contact.py` — modified (scope amended per AST-1849 \[scope-gate\]). The contact-task dispatch loop runs async handlers (`create_contact_meteorite`, `contact_task_gazer_scrape`) under a bare `asyncio.run` (`asyncio.run(handler(cid, param, debug=debug))`), and those handlers reach Telescope.

Other `asyncio.run` sites (`candidate.py`, the other `contact.py` calls, `intake.py`, `api_intake.py`, and `api_admin.py:1679` workbench) are out of scope unless `plan-fix` shows they reach Telescope. In that case, amend scope before touching them.

## Technical scope

* `src/external/telescope.py` — new function: a sync runner that wraps `asyncio.run` and always awaits `close_loop_resources()` before the loop closes. This gives one-shot loops the same teardown guarantee `dispatcher._task_thread_target` already has.
* `src/ui/api/api_admin.py` — modified function (the Telescope scrape endpoint handler): call the new runner instead of `asyncio.run`, so the admin scrape releases its pool and poller.
* `src/ui/api/api_meteorite.py` — modified function (the land-meteorite endpoint handler): call the new runner instead of `asyncio.run`, for the same reason.
* `src/ui/api/api_inbox.py` — modified function (the inbox land-all handler): call the new runner instead of `asyncio.run`, for the same reason.
* `src/core/gazer.py` — modified function `ingest_meteorite_jobs_from_email_html_sync`: call the new runner instead of `asyncio.run`, for the same reason.
* `src/core/contact.py` — modified function (the contact-task dispatch loop, `asyncio.run(handler(...))` site only): call the new runner instead of `asyncio.run`, for the same reason. Other `asyncio.run` calls in `contact.py` stay as-is (they don't reach Telescope).

## Boundaries

Product code only. Tests and the test bible belong to Betty (a gap sibling gets filed if fix-board asks for one). Leave `dispatcher._task_thread_target` alone; it's already fixed on dev (`c86d8b5c`). Other `asyncio.run` sites (`candidate.py`, the other `contact.py` calls, `intake.py`, `api_intake.py`, `api_admin.py:1679` workbench) stay out unless plan-fix shows they reach Telescope. In that case, raise a scope gate and don't touch them silently. The stall half of the parent report is already fixed on dev (AST-1840) and isn't part of this ticket.

## Notes for planning

Parent bug AST-1841's Description (As-is item 3 / To-be / Proposed steps 1–3) is authoritative. Susan approved it by reassigning from Todo. No ancestor box was checked, so there's no related-issue link. Feature doc to patch (Chuckles' best read, the top-ranked candidate): `docs/features/foundation/ast-1726-platform-telescope-py-drop-in-playwright-decommission.md`, which introduced the Telescope client and its per-loop queue. Existing teardown entry point: `close_loop_resources()` → `_TelescopeQueue.aclose_current_loop()` in `src/external/telescope.py`.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1841-asyncio-run-telescope-loop-teardown`, child `sub/AST-1841/AST-1849-asyncio-run-telescope-loop-teardown`. Created at bug-fix.

### Comments

#### radia — 2026-09-28T21:43:13.122Z
[code-rubric] PROCEED (Commit: bf470756) Five-site run_one_shot clean

#### hedy — 2026-09-28T21:38:53.123Z
`origin/sub/AST-1841/AST-1849-asyncio-run-telescope-loop-teardown` @ `bf470756` · lighter check green (no qa-fix manifest; tests → AST-1850).

Ran 7 touched-area component suites (telescope, contact, gazer, api_admin, api_admin_telescope, api_inbox, api_meteorite): 423 passed, 28 failed. The same 28 fail with the six fix files reverted to pre-fix (src/tests identical to origin/dev `3998536e`) — pre-existing, not AST-1849, not fixed here:

- `tests/component/core/test_contact.py::TestAst1071ContactSkillRunners::test_contact_skill_meta_and_unknown`
- `tests/component/core/test_contact.py::TestAst1071ContactSkillRunners::test_run_debug_false_skips_style_d`
- `tests/component/core/test_contact.py::TestAst1071ContactSkillRunners::test_run_debug_true_emits_style_d`
- `tests/component/core/test_contact.py::TestAst1071ContactSkillRunners::test_run_rejects_non_allowlisted_and_unknown_skill`
- `tests/component/core/test_contact.py::TestAst1071ContactSkillRunners::test_run_writes_allowlisted_profile_path`
- `tests/component/core/test_contact.py::TestAst1073ContactEstelleTurnLoop::test_concern_posts_and_logs_aside`
- `tests/component/core/test_contact.py::TestAst1073ContactEstelleTurnLoop::test_debug_style_d_index_and_detail`
- `tests/component/core/test_contact.py::TestAst1101ChannelHearEvidence::test_background_wrapper_logs_exception`
- `tests/component/core/test_contact.py::TestAst1207DurableDebugSot::test_handle_hydrates_on_and_passes_debug_to_turn`
- `tests/component/core/test_contact.py::TestAst1207DurableDebugSot::test_handle_ignores_kwarg_when_durable_off`
- `tests/component/core/test_contact.py::TestAst1207DurableDebugSot::test_receive_ignores_kwarg_when_durable_off`
- `tests/component/core/test_contact.py::TestAst1515ContactTaskMarkup::test_dispatch_debug_style_d`
- `tests/component/core/test_gazer.py::TestFetchJdBatch::test_collapses_consecutive_blank_lines_before_save`
- `tests/component/core/test_gazer.py::TestFetchJdBatch::test_passes_with_existing_job_data`
- `tests/component/core/test_gazer.py::TestFetchJobPagesBatch::test_additive_skips_already_scraped_url`
- `tests/component/core/test_gazer.py::TestFetchJobPagesBatch::test_all_scrapes_empty_fails_with_notes`
- `tests/component/core/test_gazer.py::TestFetchJobPagesBatch::test_missing_possible_joblist_links_fails`
- `tests/component/core/test_gazer.py::TestFetchJobPagesBatch::test_success_transitions_pjl_ready_and_persists`
- `tests/component/core/test_gazer.py::TestFetchWebsiteBatch::test_scrape_timeout_fails_with_labeled_infra_error`
- `tests/component/external/test_telescope.py::TestAst1750PostTelescopeDebugDump::test_post_telescope_debug_emits_request_body_and_full_response`
- `tests/component/external/test_telescope.py::TestTelescopePoolHttp::test_5xx_retries_other_node_then_ok`
- `tests/component/external/test_telescope.py::TestTelescopePoolHttp::test_missing_bearer_raises_connectivity`
- `tests/component/external/test_telescope.py::TestTelescopePoolHttp::test_timeout_raises_telescope_timeout`
- `tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_dispatch_task_keys_db_row_adds_orphan_key`
- `tests/component/ui/api/test_api_admin.py::TestAst1214AdminCatalogAlphabeticalWritable::test_mailbox_trigger_null_only_and_unsupported_craft_wording`
- `tests/component/ui/api/test_api_admin.py::TestAst781ListDtasksRetiredEntityType::test_list_dtasks_legacy_board_search_row_returns_zero_available_count`
- `tests/component/ui/api/test_api_admin.py::TestAst783RepoJsonApi::test_repo_json_revert_invalid_table_key`
- `tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_list_dispatch_tasks_and_keys`

Note: the contact suite writes tracked `data/contact_estelle_activity.json` as a side effect (restored, not committed).

#### joan — 2026-09-28T21:35:38.097Z
[board-joan]  CANON: OK

#### betty — 2026-09-28T21:35:01.952Z
[board-betty] TESTS: REVISE
What: docs/test-bible/external/telescope.md (no entry for loop teardown) — missing coverage — zero tests reference close_loop_resources / aclose_current_loop / _LoopState / _pool._states; plan Repro cases 1–4 (leak → run_one_shot cleans _states + awaits pool.close once + poller done; exception path re-raises with cleanup; no-touch coroutine returns 42 with _states unchanged) have no existing node. Blast radius checked: no test patches asyncio.run or the asyncio attribute on api_admin/api_meteorite/api_inbox/gazer/contact, so no existing test breaks.

#### hedy — 2026-09-28T21:34:08.273Z
`origin/sub/AST-1841/AST-1849-asyncio-run-telescope-loop-teardown` @ `2d10791f` · five-site one-shot runner planned

#### chuckles — 2026-09-28T21:32:36.999Z
[scope-gate] answered — `src/core/contact.py` (contact-task dispatch loop `asyncio.run(handler(...))` site only) added to Component/Technical scope on AST-1841 and AST-1849. Other `contact.py` `asyncio.run` calls stay out.

#### hedy — 2026-09-28T21:31:56.665Z
[scope-gate] `src/core/contact.py` reaches Telescope under a bare `asyncio.run` — needs to be in AST-1849's Component/Technical scope.

**Needed:** `src/core/contact.py` — modified, the contact-task dispatch loop (`asyncio.run(handler(cid, param, debug=debug))`, line 994): call the new Telescope one-shot runner instead of `asyncio.run`. Same kind of change as the four declared sites. No other file or approach change.

**Why it reaches Telescope** (verified on `origin/sub/AST-1841/AST-1849-asyncio-run-telescope-loop-teardown` @ `3998536e`):
- `src/utils/config.py:4958` and `:4966` register contact-task handlers `src.core.gazer.contact_task_gazer_scrape` and `src.core.meteorite.create_contact_meteorite`. Both are `async`, so `contact.py:993` sends them through `asyncio.run`.
- `create_contact_meteorite` calls `contact_task_gazer_scrape` for a URL param (`meteorite.py:466-470`).
- `contact_task_gazer_scrape` calls `telescope.check_connectivity` → `_get_healthz` → `_pool.healthy()` → `_get_db()`. That creates the per-loop asyncpg pool and the `telescope-result-poller` task, then `get_page` / `extract_page_scrape_contract` enqueue scrapes. This is the same per-loop state leak the four declared sites have.

**Scope lines that don't cover it** (AST-1849 `## Scope` / `## Boundaries`):
> Other `asyncio.run` sites (`candidate.py`, `contact.py`, `intake.py`, `api_intake.py`, and `api_admin.py:1679` workbench) are out of scope unless `plan-fix` shows they reach Telescope. In that case, amend scope before touching them.

**Checked and staying out:** other `asyncio.run` calls in `contact.py` (`:572` `stage_meteorite` only classifies and inserts rows; `:1153`/`:1202` `do_task`), `candidate.py:3729`/`:3903` (`do_task`), `intake.py:739`, `api_intake.py` (six sites), and `api_admin.py:1679` workbench. None of them imports or reaches `src.external.telescope`, `gazer`, or `roster`.

Plan doc not patched yet. The four-site plan is ready and I'll publish it together with the `contact.py:994` line once scope is amended. After amending, assign this bug to Chuckles.

---

_Implementation detail may live in git history on `origin/dev`._
