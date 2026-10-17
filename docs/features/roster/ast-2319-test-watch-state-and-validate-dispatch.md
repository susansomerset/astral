# AST-2319 — TEST_WATCH state and validate dispatch

- **Linear:** [AST-2319](https://linear.app/astralcareermatch/issue/AST-2319)
- **Parent:** [AST-2318](https://linear.app/astralcareermatch/issue/AST-2318)
- **Publish ref:** `sub/AST-2318/AST-2319-test-watch-state-and-validate-dispatch`

Register company state `TEST_WATCH`, the four company transitions this ticket owns, and a company dispatch task `test_watch` whose trigger is `TEST_WATCH`. The producer only checks that a job list parses. Parse success moves the company to `WATCH`. Any non-hold failure moves it to `WEBSITE_FOUND` so the existing in-process pipeline can pick it up. This ticket does not change Watch List columns, shapes, aggregates, the add-company form, or Ignored-page controls.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `TEST_WATCH` to `COMPANY_STATES` with batch criteria; add the four transitions; add `ROSTER_CONFIG["test_watch"]` and `TASK_CONFIG["test_watch"]`; add `test_watch` to `_DISPATCH_COMPANY_ENTITY_TASK_KEYS`; add paste-only `SEED_CONFIG["dispatch_task-test-watch"]` | utils |
| `src/core/roster.py` | Add `run_test_watch_validate`; call it from `run_company_task` when `input_state == "TEST_WATCH"` | core |

## Stages

### Stage 1: TEST_WATCH registry and dispatch registration

**Done when:** `TEST_WATCH` is a `COMPANY_STATES` key whose `batch_criteria` is `{"limit": 10, "sort_by": "updated_at"}`. `ASTRAL_CONFIG["company_state_transitions"]` contains `("IGNORE", "TEST_WATCH")`, `("TEST_WATCH", "WATCH")`, `("TEST_WATCH", "WEBSITE_FOUND")`, and `("WATCH", "IGNORE")`. `dispatch_task_admin_defaults("test_watch")` returns `entity_type="company"`, `trigger_state="TEST_WATCH"`, `sort_by="updated_at"`, `batch_call_mode=0`. `SEED_CONFIG["dispatch_task-test-watch"]` is one idempotent `INSERT` and is not called from scheduler start.

1. In `src/utils/config.py`, inside `COMPANY_STATES`, insert this entry immediately before the `"WATCH"` entry:

   ```python
   "TEST_WATCH": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
   ```

   Do not set `retry_state` on this entry. Do not add a `TEST_WATCH_RETRY` key.

2. In `ASTRAL_CONFIG["company_state_transitions"]`, immediately after the existing `("WATCH", "GET_UPSHOT")` tuple, add these four tuples and no others:

   ```python
   ("WATCH", "IGNORE"),
   ("IGNORE", "TEST_WATCH"),
   ("TEST_WATCH", "WATCH"),
   ("TEST_WATCH", "WEBSITE_FOUND"),
   ```

   Do not change `build_state_ui_manifest`'s `bulk_company` (`ignored_list_to_state` stays `"TO_WATCH"`, `watch_list_ignore_to_state` stays `"IGNORE"`, `watch_list_ack_to_state` stays `"WEBSITE_FOUND"`). Do not edit `UI_CONFIG` `companies.list.watch_list`.

3. In `ROSTER_CONFIG`, immediately after the `"parse_job_list"` block, add:

   ```python
   "test_watch": {
       "task_key": "test_watch",
       "dispatch_trigger_state": "TEST_WATCH",
       "pass_state": "WATCH",
       "fail_state": "WEBSITE_FOUND",
   },
   ```

4. In `TASK_CONFIG`, immediately after the `"parse_job_list"` entry, add:

   ```python
   "test_watch": {
       "entity_type": "company",
       "requires_candidate_key": True,
       "trigger_state": "TEST_WATCH",
       "pass_state": "WATCH",
       "fail_state": "WEBSITE_FOUND",
   },
   ```

   Do not add `response_schema`, `response_format`, `context_format`, `agent_task`, or `scored`. The LLM call remains `task_key="parse_job_list"`.

5. Add `"test_watch"` to the `_DISPATCH_COMPANY_ENTITY_TASK_KEYS` frozenset. Do not add `"test_watch"` to `_DISPATCH_BATCH_CALL_MODE_ONE`.

6. Immediately after the definition of `dispatch_task_admin_defaults` (it is defined later in this module; do not place this block before that function), add:

   ```python
   assert ROSTER_CONFIG["test_watch"]["pass_state"] == "WATCH"
   assert ROSTER_CONFIG["test_watch"]["fail_state"] == "WEBSITE_FOUND"
   assert ROSTER_CONFIG["test_watch"]["dispatch_trigger_state"] == "TEST_WATCH"
   assert "TEST_WATCH" in COMPANY_STATES
   assert "retry_state" not in COMPANY_STATES["TEST_WATCH"]
   _test_watch_defaults = dispatch_task_admin_defaults("test_watch")
   assert _test_watch_defaults["entity_type"] == "company"
   assert _test_watch_defaults["trigger_state"] == "TEST_WATCH"
   assert _test_watch_defaults["sort_by"] == "updated_at"
   assert _test_watch_defaults["batch_call_mode"] == 0
   ```

7. In `SEED_CONFIG`, add key `"dispatch_task-test-watch"` whose value is a one-tuple. The statement is an idempotent insert for every `candidate` row, same shape as the meteorite seed inserts (column list and `WHERE NOT EXISTS` on `candidate_id` + `task_key` + `trigger_state`). Literals:

   - `task_key` `'test_watch'`
   - `entity_type` `'company'`
   - `trigger_state` `'TEST_WATCH'`
   - `sort_by` `'updated_at'`
   - `batch_call_mode` `0`
   - `freq_hrs` `0`
   - `min_count` `1`
   - `batch_size` `10`
   - `auto_mode` `1`
   - `score_floor` `NULL`

   Do not call this seed from `start_scheduler`, boot, or any other runtime path. `SEED_CONFIG` `dispatch_task-*` entries stay Linear paste-only (existing AST-1496 comment in this file).

⚠️ **Decision:** No `TEST_WATCH_RETRY`. Parent notes say single-shot to `WEBSITE_FOUND` unless a retry hop is required. Parse failure here is the product outcome (enter the normal pipeline at `WEBSITE_FOUND`), not an agent error holding. `patt.task.dispatch-retry` stays unused. `dispatch_claim_states` will still ask for `TEST_WATCH_RETRY` on its own; this ticket does not register that state and does not transition to it.

⚠️ **Decision:** `batch_call_mode` stays `0`. `consult.run_consult_task` only special-cases named company task keys; every other company key falls through to `roster.run_company_task` on `entities[0]`. Mode `0` already calls that once per claimed company. Mode `1` would process only the first row. `consult.py` is outside this ticket's Scope, so the task stays mode `0` and the branch lives in `run_company_task`.

⚠️ **Decision:** Do not change `ignored_list_to_state`. Restore UI and the add-company form belong to sibling tickets. This ticket only adds the transition tuples those tickets will use.

### Stage 2: TEST_WATCH validate producer

**Done when:** A company claimed in `TEST_WATCH` and run under `dispatch_task_key="test_watch"` ends in `WATCH` when job-list parse validation succeeds, and in `WEBSITE_FOUND` on every other attempted failure. A provider hold does not change state. `clear_company_batch` is not called from the new function. A `WEBSITE_FOUND` company is not given a Watch List membership by this code (no view filter edit; destination state is not `WATCH`).

1. In `src/core/roster.py`, add `async def run_test_watch_validate(entity, batch_id, ctx=None, debug=False) -> Dict[str, Any]` immediately after `run_parse_job_list_dispatch`. Read destinations only from `ROSTER_CONFIG["test_watch"]`: `pass_state` and `fail_state`. Read the list-url key from `ROSTER_CONFIG["parse_job_list"]["selected_pjl_url_key"]`.

2. Use the claimed `entity` dict. Do not call `get_company` to re-select the queue. Fields: `short_name`, `company_website`, `job_site`, `state`, `company_data` (treat a non-dict as `{}`). Ignore `batch_id` except that `transition_company_state` already stamps the row's current `batch_id` onto `state_history`. Do not call `clear_company_batch`.

3. If `str(entity.get("state") or "").strip() != "TEST_WATCH"`, do not transition. Return `{"short_name": short_name, "state": <current state>, "error": "unexpected_state"}`.

4. List URL, first non-empty strip wins: `company_data[selected_pjl_url_key]`, else `job_site`, else `company_website`. Job titles: `_normalize_job_titles(company_data.get("job_titles"))`. If the URL is empty or titles are empty, `transition_company_state(short_name, fail_state)` and return `{"short_name": short_name, "state": fail_state}`.

5. Otherwise scrape and parse with the same helpers `run_parse_job_list_dispatch` uses, and different outcomes:

   - Open `create_browser_context()` and call `_scrape_list_page_dom_for_parse(list_url, browser_context, debug=debug, short_name=short_name)`.
   - Empty DOM, or `_culled_dom_for_parse` outcome `"cull_miss"` or blank joined DOM: transition to `fail_state` and return that state.
   - Call `do_task(task_key="parse_job_list", live_content=<culled dom>, index=short_name, ctx=ctx)`. Do not call `_fetch_parse_job_list` (it drops provider-hold details and writes parse notes on failure).
   - If `is_provider_state_hold(response)` is true, do not transition. Return that response unchanged.
   - If the response has `empty_tokens`, or `success` is not true, or `parsed_response` lacks a non-empty `job_container` and `job_tag`: transition to `fail_state` and return that state.
   - Else call `_validate_parse_job_list_raw_job_listings(dom_joined, container, job_tag, parsed_response.get("job_ids", []))`. If it returns an error string, transition to `fail_state` and return that state.
   - Else success: `save_company_data(short_name, {"parse_instructions": {"container": container, "job_tag": job_tag, "container_index": _compute_container_index(dom_html, container, job_titles)}})` using the same container-index inputs `_finalize_parse_dispatch_success` uses (`dom_html` is the scraped DOM, not the culled join). Then `transition_company_state(short_name, pass_state)`. Do not call `_finalize_parse_dispatch_success` or `_save_company` (those write `GET_UPSHOT` / `job_site`). Return `{"short_name": short_name, "state": pass_state, "response_type": "TEST_WATCH_OK"}`.

6. On `PlaywrightInfraError` or any other `Exception` from the scrape/parse attempt, transition to `fail_state` and return that state. Do not leave the company in `TEST_WATCH`. Do not call `_save_parse_dispatch_failure`.

7. In `run_company_task`, add a branch immediately before the `elif input_state == "WATCH":` gaze branch:

   - Condition: `input_state == "TEST_WATCH"`.
   - If `(dispatch_task_key or "").strip() != "test_watch"`: `_warn_company(short_name, "-", ...)` and return `{**zero, "total_errors": 1}`. Do not transition.
   - Else `result = await run_test_watch_validate(entity, batch_id, ctx, debug)`.
   - If `is_provider_state_hold(result)`: return `{**zero, "total_held": 1, "failure_class": result.get("failure_class"), "error": result.get("error")}`.
   - If `result.get("state") == ROSTER_CONFIG["test_watch"]["pass_state"]`: return `{**zero, "total_passed": 1}`.
   - If `result.get("state") == ROSTER_CONFIG["test_watch"]["fail_state"]`: return `{**zero, "total_failed": 1}`.
   - Otherwise: `_warn_company` with `result.get("error")` and return `{**zero, "total_errors": 1}`.

⚠️ **Decision:** `WEBSITE_FOUND` counts as `total_failed`, not `total_errors`. The task finished. Counting it as an error would trip the dispatch circuit breaker on companies that correctly fail the parse check.

⚠️ **Decision:** Provider balance / host-probe hold keeps `TEST_WATCH` and returns `total_held`, matching `select_job_page` in this function. That is not a parse failure and must not enter `WEBSITE_FOUND`.

## Estimate

Confirm Chuckles estimate: 5 — agree
