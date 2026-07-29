<!-- linear-archive: AST-891 archived 2026-07-29 -->

## Linear archive (AST-891)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-891/parse-job-list-browser-pressure-and-batch-completion-parse-job-list  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-890 — parse_job_list error causing infinite loop  
**Blocked by / blocks / related:** parent: AST-890

### Description

## What this implements

Stop production `parse_job_list` batches from thrashing the host and stalling the roster pipeline. Bound simultaneous browser pressure so a claimed batch does not cascade into Firefox launch/crash failures; ensure every claimed company gets a definite outcome (success → `WATCH`, first failure → parse retry holding state, exhausted retry → terminal parse failure) including when the failure is browser/infra; make the batch finish under partial failure without hanging until dispatch timeout; and stop undrainable reclaim of companies that have already exhausted the parse retry contract. Preserve happy-path parse behavior. With `debug=True`, emit AST-538-style per-company observability for the parse hop.

## Acceptance criteria

1. On production, Susan runs `parse_job_list` against a non-trivial `JOBLIST_IDENTIFIED` queue and the batch reaches a normal terminal finish (completed, or INTERRUPTED only on explicit cancel / true wall-clock policy) without sitting for a full dispatch timeout while Firefox launch errors cascade and little or no work progresses.
2. Under induced or natural browser/infra failure mid-batch, every claimed company lands in a verifiable state (`WATCH`, `JOBLIST_IDENTIFIED_RETRY`, or `COULD_NOT_PARSE_JOBLIST` per existing strike rules) — no company remains indefinitely claimed or invisible to the next eligible dispatch.
3. After one parse retry has already been consumed, a further infra or parse failure moves the company to `COULD_NOT_PARSE_JOBLIST` (or equivalent existing terminal) so it stops being reclaimed by `parse_job_list`.
4. Successful parses in the same batch still reach `WATCH`; failures on other companies do not abort or strand the successful ones.
5. With `debug=True`, Susan can scan per-company index headers and substantive `|` detail lines showing attempt outcome and recorded state for the parse hop (AST-538 / AST-554 contract).
6. A follow-up dispatch on the remaining eligible pool does not sit in an endless reclaim of the same already-exhausted companies with no state change.

## Boundaries

* Does not change `select_job_page`, `find_job_page`, prefilter, or gazer job-side tasks.
* Does not redesign successful parse destinations, title/DOM cull semantics, or LLM parse prompt/schema for `parse_job_list`.
* Does not own the sibling `fetch_website` reclaim loop (`AST-889`).
* Does not reopen Playwright launch taxonomy already shipped under `AST-853` / `AST-854` except as reuse of the existing infra-failure signaling contract and config-as-truth rules.
* Does not change Railway host OS / sandbox privileges as a product deliverable.

## Notes for planning

Primary lift: `roster` parse dispatch / company task paths and how `parse_job_list` obtains browser contexts under concurrent claim. Reuse AST-853 Playwright infra classification and AST-854-style fail destinations / batch completion patterns where they fit; respect `ASTRAL_CODE_RULES` §2.1 (config-driven limits) and §1.5.1 debug contract. Do not invent ad-hoc launch constants outside config.

## Git branch (authoritative)

Per **orientation** § Branch law: parent `ftr/AST-890-parse-job-list-infinite-loop`, child `sub/AST-890/<this-id>-parse-job-list-browser-and-batch`. Created at **dispatch-parent**. Engineers publish to `origin/<sub-ref>` — never Linear `gitBranchName` when it disagrees.

### Comments

#### betty — 2026-07-13T21:03:02.228Z
[check-linear]
Cleared `[qa-handoff]` (Radia fix-now / test-tree only).

Deleted on `origin/sub/AST-890/AST-891-parse-job-list-browser-and-batch` @ `fefb15c` (`test(AST-891): remove AST-892 pollution tests (Radia fix-now)`):
1. `tests/component/core/test_dispatcher.py` · `test_ast892_fetch_website_excludes_prefilter_second_strike`
2. `tests/component/core/test_roster.py` · `test_get_new_company_batch_passes_exclude_prefilter_second_strike`

Left `Review Posted`; assignee → Hedy for resolve-child → User Testing. Those two methods remain on `origin/tests` under AST-892 corpus (not re-deleted there).

#### hedy — 2026-07-13T21:01:00.622Z
[qa-handoff]
@Betty White

Radia fix-now on AST-891 is test-tree only (engineer ban) — need Betty delete on publish-ref, not AST-892 product:

1. `tests/component/core/test_dispatcher.py` · `test_ast892_fetch_website_excludes_prefilter_second_strike`
2. `tests/component/core/test_roster.py` · `test_get_new_company_batch_passes_exclude_prefilter_second_strike`

Both assert `exclude_prefilter_second_strike` which is not on this branch's claim/API paths. `f207f5b` already cleaned consult/config AST-892 pollution; these two remain. Delete them on `origin/sub/AST-890/AST-891-parse-job-list-browser-and-batch` @ `0c98279`, then reassign Hedy for resolve-child continue to User Testing.

Advisory items left for UAT / optional polish — no product fix this pass.

#### radia — 2026-07-13T21:00:15.295Z
**Diff:** `origin/dev...origin/sub/AST-890/AST-891-parse-job-list-browser-and-batch` @ `0c98279`

Doc: https://github.com/susansomerset/astral/blob/0c98279aa5be886ea137f52f07771692a3a8bfaa/docs/features/roster/ast-891-parse-job-list-browser-and-batch.md

### fix-now
- `tests/component/core/test_dispatcher.py` · `test_ast892_fetch_website_excludes_prefilter_second_strike` and `tests/component/core/test_roster.py` · `test_get_new_company_batch_passes_exclude_prefilter_second_strike` — AST-892 pollution left after `f207f5b` cleaned consult/config only. Both assert `exclude_prefilter_second_strike`, which is not on claim/API paths in this diff. Delete both on resolve (do not implement AST-892 here).

### discuss
None.

### advisory
- Nested debug: batch `index N/M` then dispatch `index 1/1` when `debug=True`.
- Timeout path sets `list_url` only under `debug=True` (non-debug falls back to `company_website` in `_save_parse_dispatch_failure`).
- Gather unhandled exception → `errors` only, no strike write (AST-854 parity; dispatcher `finally` clears claim).

**Counts:** 1 fix-now · 0 discuss · 3 advisory

Product stages 1–3 match plan (batch session, semaphore, infra scrape raise, consult + `use_full_batch`).

#### betty — 2026-07-13T20:55:40.389Z
1. `tests/component/utils/test_config.py::TestAst721ParseJobListConfig::test_parse_job_list_roster_config` — `ROSTER_CONFIG["parse_job_list"]["max_concurrent"] == 3`
2. `tests/component/core/test_roster.py::TestAst891ScrapeListPageInfra` — list-page scrape raises Playwright infra (does not swallow as empty DOM); non-infra rethrows
3. `tests/component/core/test_roster.py::TestAst891ParseDispatchInfraAndBatchSession` — infra → `PARSE_DISPATCH_INFRA` + strike ladder; `batch_session` skips solo `create_browser_context`
4. `tests/component/core/test_roster.py::TestAst891ParseJobListBatch` — shared batch session, scrape-timeout labeling, resilient gather, definite outcomes count as `passed`, debug index
5. `tests/component/core/test_roster.py::TestAst721ParseDispatchHelpers::test_parse_dispatch_failure_state_ladder` — existing strike ladder (reuse)
6. `tests/component/core/test_roster.py::TestAst721ParseJobListDispatch` — existing happy / empty-DOM retry→terminal (reuse)
7. `tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_parse_job_list_batch` — consult routes to `parse_job_list_batch`
8. `tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_parse_job_list_batch_errors_count` — `total_errors` from batch `errors`
9. `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast891_parse_job_list_full_batch_despite_batch_call_mode_zero` — full-list consult when `batch_call_mode=0`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst721ParseJobListConfig::test_parse_job_list_roster_config \
  tests/component/core/test_roster.py::TestAst891ScrapeListPageInfra \
  tests/component/core/test_roster.py::TestAst891ParseDispatchInfraAndBatchSession \
  tests/component/core/test_roster.py::TestAst891ParseJobListBatch \
  tests/component/core/test_roster.py::TestAst721ParseDispatchHelpers::test_parse_dispatch_failure_state_ladder \
  tests/component/core/test_roster.py::TestAst721ParseJobListDispatch \
  tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_parse_job_list_batch \
  tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_parse_job_list_batch_errors_count \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast891_parse_job_list_full_batch_despite_batch_call_mode_zero \
  -q
```

`origin/sub/AST-890/AST-891-parse-job-list-browser-and-batch` @ `d9f1fed` (`merge-tests(AST-891): origin/tests f207f5bfaceeca334d87461982e0cf2d90580506`)

Bible shasums on publish-ref:
- `docs/test-bible/core/roster.md` `5116de2bc7e7e324d5f8ae9a757781e654bd7821`
- `docs/test-bible/core/consult.md` `97a443e621eb1fbc302789231506f8caa7a3ccd8`
- `docs/test-bible/core/dispatcher.md` `d9d5074a37b84635f2fd9ef86e815139e2e6b40f`
- `docs/test-bible/utils/config.md` `7caf8c01ae47e4591231c39cb569c49f41a66016`

#### hedy — 2026-07-13T20:45:39.527Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-890/AST-891-parse-job-list-browser-and-batch/docs/features/roster/ast-891-parse-job-list-browser-and-batch.md

**Scope:** Single-Component — `ROSTER_CONFIG` concurrency key, roster scrape/dispatch/batch, thin consult + dispatcher route for `parse_job_list` only.
**Conf:** high — reuses AST-853 `BatchBrowserSession` / `[playwright:]` taxonomy and AST-854 resilient gather; existing `_parse_dispatch_failure_state` already owns the three strike destinations.
**Risk:** Medium — production parse hot path + dispatcher full-batch special-case for this `task_key`; mitigated by preserving happy-path finalize helpers and not touching sibling hops.

Approach in short: stop `_warm_then_gather` Firefox fan-out for this task; one recoverable batch session + `max_concurrent: 3`; infra failures still hit `JOBLIST_IDENTIFIED_RETRY` then `COULD_NOT_PARSE_JOBLIST` so exhausted companies leave the reclaim pool.

---

# AST-891 — parse_job_list browser pressure and batch completion

**Linear:** [AST-891 — parse_job_list browser pressure and batch completion](https://linear.app/astralcareermatch/issue/AST-891/parse-job-list-browser-pressure-and-batch-completion-parse-job-list)

**Parent (reference only — orchestration AC):** [AST-890 — parse_job_list error causing infinite loop](https://linear.app/astralcareermatch/issue/AST-890/parse-job-list-error-causing-infinite-loop)

**Publish ref:** `origin/sub/AST-890/AST-891-parse-job-list-browser-and-batch` (origin only)

## Summary

Production `parse_job_list` claims up to 20 `JOBLIST_IDENTIFIED` / `JOBLIST_IDENTIFIED_RETRY` companies and, with `batch_call_mode=False`, fans them through `_warm_then_gather` so each company opens its own Firefox via `create_browser_context()`. That unconstrained launch storm collapses into SIGSEGV / sandbox EACCES / spawn EAGAIN, while `_scrape_list_page_dom_for_parse` swallows every Playwright exception as an empty DOM — so the batch crawls or sits until dispatch wall-clock timeout and exhausted companies keep getting reclaimed. This ticket converts `parse_job_list` to an AST-853/854-style **batch browser runner**: one recoverable `BatchBrowserSession`, a config-driven concurrency semaphore, per-company scrape timeout, infra-labeled failure notes, and definite strike routing (`JOBLIST_IDENTIFIED` → `JOBLIST_IDENTIFIED_RETRY` → `COULD_NOT_PARSE_JOBLIST`) so every claimed company finishes and leaves the claim pool when retry is exhausted. Happy-path parse destinations and LLM parse prompt/schema stay unchanged.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `max_concurrent` under `ROSTER_CONFIG["parse_job_list"]` | utils |
| `src/core/roster.py` | Propagate Playwright infra from DOM scrape; accept `batch_session`; add `parse_job_list_batch` (session + semaphore + resilient gather + timeout + debug) | core |
| `src/core/consult.py` | Route `task_key == "parse_job_list"` to `parse_job_list_batch` (mirror `fetch_website`) | core |
| `src/core/dispatcher.py` | When `dispatch_task_key == "parse_job_list"`, always pass the full claimed entity list in one `run_consult_task` call (do not use `_warm_then_gather` fan-out) | core |

**Out of scope:** `select_job_page`, `find_job_page`, prefilter, gazer job-side tasks, parse prompt/schema, successful parse destinations / title/DOM cull semantics, AST-889 `fetch_website` reclaim loop, Railway OS/sandbox privileges, dispatch UI default `batch_size` knobs, inventing new launch constants outside existing `PLAYWRIGHT_CONFIG`.

**Read-only reuse (do not duplicate):**

| Symbol | Location | Use |
|--------|----------|-----|
| `create_batch_browser_session`, `BatchBrowserSession`, `PlaywrightInfraError`, `classify_playwright_failure`, `is_playwright_infra_failure` | `src/external/playwright.py` | AST-853 session + taxonomy |
| `PLAYWRIGHT_CONFIG["company_scrape_timeout_seconds"]` | `src/utils/config.py` | Per-company scrape wall timeout (reuse; do not add a second timeout constant) |
| `_parse_dispatch_failure_state`, `_save_parse_dispatch_failure`, `_finalize_parse_dispatch_success`, `run_parse_job_list_dispatch` | `src/core/roster.py` | Existing strike routing + per-company parse body |
| `fetch_website_batch` semaphore + `return_exceptions=True` gather | `src/core/gazer.py` | Pattern reference only |

---

## Stage 1: Config concurrency limit

**Done when:** `ROSTER_CONFIG["parse_job_list"]` exposes an integer `max_concurrent` readable by the batch runner; no other modules changed yet.

1. In `src/utils/config.py`, extend `ROSTER_CONFIG["parse_job_list"]` to:

```python
"parse_job_list": {
    "dispatch_trigger_state": "JOBLIST_IDENTIFIED",
    "retry_trigger_state": "JOBLIST_IDENTIFIED_RETRY",
    "pass_state": "WATCH",
    "retry_state": "JOBLIST_IDENTIFIED_RETRY",
    "terminal_fail_state": "COULD_NOT_PARSE_JOBLIST",
    "selected_pjl_url_key": "selected_pjl_url",
    "max_concurrent": 3,
},
```

⚠️ **Decision:** Concurrency lives on `ROSTER_CONFIG["parse_job_list"]` (not a silent shrink of DB `batch_size`, not a hardcoded `Semaphore(3)` like grandfathered gazer paths). Value `3` matches the production-proven `fetch_website` / `fetch_jd` cap; claim width (e.g. 20) stays on the dispatch row. Launch/retry/timeout literals continue to come only from existing `PLAYWRIGHT_CONFIG`.

---

## Stage 2: DOM scrape infra signaling + session-aware single-company path

**Done when:** A Playwright launch/context failure during list-page DOM reload surfaces as a `[playwright:<failure_class>] …` error string to the caller (and a non-debug WARNING log), instead of returning `""`; `run_parse_job_list_dispatch` can use an optional shared `batch_session` the same way `scrape_company_homepage_content` does.

1. In `src/core/roster.py`, add imports from `src.external.playwright`: `create_batch_browser_session` (keep existing `PlaywrightInfraError` / classify helpers already imported).

2. Change `_scrape_list_page_dom_for_parse` signature to:

```python
async def _scrape_list_page_dom_for_parse(
    url: str,
    browser_context: Optional[BrowserSession] = None,
    debug: bool = False,
    *,
    batch_session=None,
    short_name: str = "",
) -> str:
```

   Behavior:
   - Resolve page via `get_page(batch_session=batch_session, url=url)` when `batch_session` is set; else `get_page(browser_context, url)` as today.
   - On success: keep readiness wait + `extract_page_dom` + `close_page` (unchanged).
   - On exception: do **not** return `""`. Mirror `scrape_company_homepage_content`:
     - If `PlaywrightInfraError`: `fc = scrape_err.failure_class`, `msg = scrape_err.detail`.
     - Else: `fc = classify_playwright_failure(scrape_err)`, `msg = str(scrape_err)`.
     - If `is_playwright_infra_failure(fc)`: log `logger.warning("[%s] playwright infra failure failure_class=%s %s", short_name or url, fc, msg)` and **raise** `PlaywrightInfraError(fc, msg)` if not already that type (or re-raise existing).
     - Else: re-raise the original exception.
   - Empty DOM after a successful navigation still returns `""` (content failure path unchanged).

3. Update `run_parse_job_list_dispatch`:
   - Add optional kwarg `batch_session=None`.
   - When `batch_session` is not None: call `_scrape_list_page_dom_for_parse(list_url, debug=debug, batch_session=batch_session, short_name=short_name)` (no `create_browser_context`).
   - When `batch_session` is None: keep today’s `async with create_browser_context() as browser_context:` path for any non-batch caller (tests / adhoc), passing `short_name=short_name` into the scrape helper.
   - Wrap the scrape+cull+parse+validate body in a try/except:
     - On `PlaywrightInfraError` as `ex`: call `_save_parse_dispatch_failure(..., notes=f"[playwright:{ex.failure_class}] {ex.detail}", response_type="PARSE_DISPATCH_INFRA")` and return that result.
     - On other Exception as `ex`: call `_save_parse_dispatch_failure(..., notes=str(ex), response_type="PARSE_DISPATCH_ERROR")` and return that result (definite outcome — never leave the company claimed without a state write).
   - Empty-DOM / cull-miss / LLM / validation failures keep existing `_save_parse_dispatch_failure` response types and strike routing via `_parse_dispatch_failure_state` (no change to which states are chosen).

⚠️ **Decision:** Infra vs content both use the **existing** strike helper (`JOBLIST_IDENTIFIED` → `JOBLIST_IDENTIFIED_RETRY`, `JOBLIST_IDENTIFIED_RETRY` → `COULD_NOT_PARSE_JOBLIST`). Do **not** add a separate infra-only destination — parent AC reuses those three states. Infra is distinguished only by `[playwright:…]` notes / `PARSE_DISPATCH_INFRA` for observability.

---

## Stage 3: `parse_job_list_batch` + consult/dispatcher wiring

**Done when:** A claimed batch of N companies runs under one `create_batch_browser_session`, at most `ROSTER_CONFIG["parse_job_list"]["max_concurrent"]` companies scrape at once, every company reaches `WATCH` / `JOBLIST_IDENTIFIED_RETRY` / `COULD_NOT_PARSE_JOBLIST` (or counts toward `errors` if an unexpected exception escapes), scrape wall-clock timeout uses `PLAYWRIGHT_CONFIG["company_scrape_timeout_seconds"]`, and production `batch_call_mode=False` still hits the batch runner (not `_warm_then_gather` fan-out). With `debug=True`, each company emits AST-538 `debug_index` + `|` detail for attempt / outcome / recorded state.

1. In `src/core/roster.py`, add:

```python
async def parse_job_list_batch(
    batch_id: str,
    companies: List[Dict[str, Any]],
    ctx: Optional[Dict[str, Any]] = None,
    debug: bool = False,
) -> Dict[str, int]:
```

   Implementation requirements:
   - Read `parse_cfg = ROSTER_CONFIG["parse_job_list"]`, `max_concurrent = int(parse_cfg["max_concurrent"])`, `scrape_timeout = PLAYWRIGHT_CONFIG["company_scrape_timeout_seconds"]` (import `PLAYWRIGHT_CONFIG` from `src.utils.config` if not already imported in this module).
   - Counters: `passed = failed = errors = 0` (names match `fetch_website_batch` return shape). For summary semantics matching today’s `run_company_task` parse branch: any company that lands in `{pass_state, retry_state, terminal_fail_state}` increments **`passed`** (definite progress); only unhandled exceptions increment **`errors`**. Do **not** invent a new “failed means terminal only” split — Betty/manifests already treat definite retry/terminal as processed progress for this hop.
   - `async with create_batch_browser_session() as batch_session:`
     - Define inner `_one(company, company_index)` that:
       - Sets debug flag when `debug`.
       - Emits `debug_index` with `func="roster.parse_job_list_batch"`, `index=company_index`, `total=len(companies)`, `identifier=short_name`, outcome preview (`state=… url=…` or similar short string).
       - Runs `await asyncio.wait_for(run_parse_job_list_dispatch(company, batch_id, ctx, debug, batch_session=batch_session), timeout=scrape_timeout)`.
       - On `asyncio.TimeoutError`: treat as infra — call `_save_parse_dispatch_failure` with `notes=f"[playwright:scrape_timeout] company scrape exceeded {scrape_timeout}s"`, `response_type="PARSE_DISPATCH_INFRA"`, using the company’s current `state` as `input_state`; log warning with `failure_class=scrape_timeout`; count as `passed` if resulting state is in the ok frozenset.
       - On success return from dispatch: if `result.get("error")` or state not in ok frozenset → increment `errors` (mirror `run_company_task`); else increment `passed`. Emit `debug_detail` with `response_type=… -> state=…`.
     - `sem = asyncio.Semaphore(max_concurrent)`; wrap each `_one` with `async with sem`.
     - `results = await asyncio.gather(*[...], return_exceptions=True)`.
     - For each `BaseException` in results: `errors += 1`, `logger.exception("parse_job_list_batch unhandled error batch_id=%s: %s", batch_id, r, exc_info=r)`. **Do not** abort remaining companies.
   - If `debug`: emit batch-end `debug_detail` `summary={passed, failed, errors, total}` (set `failed=0` unless you use it; keep key present for parity with gazer: either always `failed=0` or omit and document — **prefer** `return {"passed": passed, "failed": 0, "total": len(companies), "errors": errors}` so consult can read the same keys as `fetch_website`).
   - Return that dict.

2. In `src/core/consult.py`, inside the `entity_type == "company"` block, **before** the final `return await roster.run_company_task(...)`, add:

```python
if task_key == "parse_job_list":
    r = await roster.parse_job_list_batch(batch_id, entities, ctx=ctx, debug=debug)
    total = r.get("total", len(entities))
    passed = r.get("passed", 0)
    failed = r.get("failed", 0)
    errors = r.get("errors", max(0, total - passed - failed))
    return {
        "total_processed": total,
        "total_passed": passed,
        "total_failed": failed,
        "total_errors": errors,
    }
```

3. In `src/core/dispatcher.py` `_run_unified`, change the branch that chooses batch vs `_warm_then_gather` so `parse_job_list` always uses the full-list consult call even when the DB row has `batch_call_mode=0`:

   - Compute a local flag after `batch_call_mode` is read, e.g. `use_full_batch = batch_call_mode or (dispatch_task_key == "parse_job_list")`.
   - Use `if use_full_batch:` for the existing batch_call_mode body (chunk split still only applies to the existing job chunk keys — `parse_job_list` is company and will take the non-chunk `run_consult_task(..., entities, ...)` path).
   - Else keep `_warm_then_gather`.

⚠️ **Decision:** Production logs show `batch_call_mode=False` for `parse_job_list`. Relying on a silent admin DB flip would leave the fan-out bug in place. Code owns full-batch orchestration for this `task_key` only — adjacent hops (`select_job_page`, etc.) stay on `_warm_then_gather`. Do **not** change other task keys.

4. Confirm (audit only — no code unless a one-line gap): dispatcher `finally` still calls `clear_company_batch(bid)` so interrupted/admin-killed runs do not leave companies stuck claimed. If a gap exists that is not a one-line `finally` guarantee, **stop** and comment on **AST-890** — do not expand scope.

---

## Execution contract

The plan is binding. The developer agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- When the codebase has drifted from what the plan assumes — **stops and comments.** Does not adapt silently.
- Completes each stage with one commit on the epic worktree line, then publishes to `origin/sub/AST-890/AST-891-parse-job-list-browser-and-batch` via build-child publish rules.

Blocking comment format (on **AST-890**):

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

---

## Self-Assessment

**Scope:** `Single-Component` — `ROSTER_CONFIG` concurrency key, roster parse scrape/dispatch/batch, thin consult + dispatcher route; no external Playwright redesign and no sibling-task ownership.

**Conf:** `high` — reuses shipped AST-853 `BatchBrowserSession` / `[playwright:]` taxonomy and AST-854 resilient gather + strike routing already present as `_parse_dispatch_failure_state`; production failure mode in the Original brief matches unconstrained per-company `create_browser_context` under `_warm_then_gather`.

**Risk:** `Medium` — production `parse_job_list` hot path and dispatcher routing change; mitigated by preserving existing strike states / happy-path finalize helpers and by scoping the full-batch consult special-case to this `task_key` only.

---

## ASTRAL_CODE_RULES self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses `_save_parse_dispatch_failure` / `_parse_dispatch_failure_state` / `run_parse_job_list_dispatch`; batch wrapper mirrors `fetch_website_batch` without copying Playwright launch logic. |
| §2.1 config | `max_concurrent` is a config literal; scrape timeout and launch prefs stay in `PLAYWRIGHT_CONFIG`; no new env lookups. |
| §2.4 batch | Claim/clear remain dispatcher-owned; batch function processes claimed rows by `batch_id` and returns summary counts. |
| §2.6 state machine | Destinations remain `WATCH` / `JOBLIST_IDENTIFIED_RETRY` / `COULD_NOT_PARSE_JOBLIST` via existing transitions — no new transition edges. |
| §3.3 imports | `create_batch_browser_session` imported in core from external; config from utils; no layer violations. |
| §3.5 naming | `parse_job_list_batch` matches `fetch_website_batch` / `prefilter_company_batch` naming. |
| §1.5.1 debug | Per-company `debug_index` + `|` detail + batch summary only when `debug=True`; infra WARNING is always-on (same as AST-853 homepage scrape). |

---

## Review (build stub)

**Publish ref:** `origin/sub/AST-890/AST-891-parse-job-list-browser-and-batch`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `fb3d51c` | `max_concurrent` on `ROSTER_CONFIG["parse_job_list"]` |
| 2 | `eba17d3` | DOM scrape infra signaling + `batch_session` on `run_parse_job_list_dispatch` |
| 3 | `e8e9a42` | `parse_job_list_batch` + consult route + dispatcher `use_full_batch` |

**Dispatcher audit:** `dispatcher._run_unified` `finally` always calls `clear_company_batch(bid)` for company batches — no code change.

**Tip:** `e8e9a42`

---

## Radia review (2026-07-13)

**Diff:** `origin/dev...origin/sub/AST-890/AST-891-parse-job-list-browser-and-batch` @ `d9f1fed`  
**Product commits:** `fb3d51c` config · `eba17d3` scrape infra + `batch_session` · `e8e9a42` batch + consult + dispatcher  
**Tests:** `a086c95` / `f207f5b` (partial AST-892 decontamination) · `d9f1fed` merge-tests

### What’s solid

| Area | Notes |
|------|-------|
| Plan fidelity | Stages 1–3 match: `max_concurrent=3`, scrape raises infra instead of `""`, `parse_job_list_batch` + shared session/semaphore/`wait_for`/resilient gather, consult route, dispatcher `use_full_batch` for this task key only. |
| Strike / AC | Infra + generic errors use existing `_save_parse_dispatch_failure` → `JOBLIST_IDENTIFIED` → `JOBLIST_IDENTIFIED_RETRY` → `COULD_NOT_PARSE_JOBLIST`; definite outcomes count as `passed`. |
| §2.1 / §2.4 / §2.6 | Concurrency from `ROSTER_CONFIG`; claim/clear stay dispatcher-owned (`finally` clear unchanged); no new transition edges. |
| §1.5.1 / §5f | Batch `debug_index` / `|` detail / end `summary` gated on `debug=True`; infra WARNING always-on (AST-853 parity). |
| Layers (§3.3) | `create_batch_browser_session` imported in core from external; no UI/`data` bend. |
| Self-Assessment | Scope Single-Component matches footprint; Conf high still fits. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **fix-now** | `tests/component/core/test_dispatcher.py` · `test_ast892_fetch_website_excludes_prefilter_second_strike`; `tests/component/core/test_roster.py` · `test_get_new_company_batch_passes_exclude_prefilter_second_strike` | AST-892 pollution left on the AST-891 publish ref after `f207f5b` cleaned consult/config only. Both assert `exclude_prefilter_second_strike`, which is **not** on `get_new_company_batch` / dispatcher claim paths in this diff (or `origin/dev`). Manifest-scoped AST-891 nodeids stay green; class/module runs or full suite will fail. Out of AST-891 scope — delete these two tests on resolve (same decontam Betty started). |
| **advisory** | `parse_job_list_batch` → `run_parse_job_list_dispatch` when `debug=True` | Batch emits correct `index N/M`, then dispatch still emits `index 1/1` — noisy dual headers; pattern inherits single-company debug. Optional: skip inner index when `batch_session` is set. |
| **advisory** | `parse_job_list_batch` timeout path · `list_url` | `list_url` is resolved only inside `if debug:`; non-debug timeout saves with `list_url=""` (falls back to `company_website` in `_save_parse_dispatch_failure`). Notes still carry `[playwright:scrape_timeout]`. |
| **advisory** | gather unhandled `BaseException` | Increments `errors` only — no strike write for that company; claim cleared in dispatcher `finally` (AST-854 parity). Rare after dispatch try/except + timeout handler. |

### Recommended actions

| Item | Action |
|------|--------|
| fix-now | Delete the two AST-892 `exclude_prefilter_second_strike` tests from this publish ref (do not implement AST-892 product here). |
| discuss | None. |
| advisory | Optional debug/timeout polish; UAT: mid-batch infra → retry/terminal per strike; siblings continue. |

**Counts:** 1 fix-now · 0 discuss · 3 advisory

**Outcome:** Findings — product path ships; clear test pollution before User Testing.

— Radia

---

## Resolution (2026-07-13)

**Radia review tip:** `0c98279` · **Betty clear:** `fefb15c` (`test(AST-891): remove AST-892 pollution tests (Radia fix-now)`)

| Item | Disposition |
|------|-------------|
| **fix-now** — AST-892 `exclude_prefilter_second_strike` tests on dispatcher/roster | Cleared by Betty via `[qa-handoff]` — deleted on publish-ref @ `fefb15c`. No product change. |
| **discuss** | None. |
| **advisory** — nested debug indices / timeout `list_url` / gather `errors`-only | Left as-is for UAT; optional polish, not blocking. |

**§9a:** dry-run `origin/sub/AST-890/AST-891-parse-job-list-browser-and-batch` into `origin/dev` and `origin/ftr/AST-890-parse-job-list-infinite-loop` — recorded at resolve commit.
