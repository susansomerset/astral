# AST-2070 — GET_UPSHOT fetch and UPSHOT_READY Estelle hops

- **Ticket:** [AST-2070](https://linear.app/astralcareermatch/issue/AST-2070)
- **Parent:** [AST-2054 — Company Upshot - new task](https://linear.app/astralcareermatch/issue/AST-2054)
- **Publish ref:** `sub/AST-2054/AST-2070-upshot-hops` (origin only)
- **Depends on:** [AST-2069](https://linear.app/astralcareermatch/issue/AST-2069). Its registration is already on this ref (`GET_UPSHOT` / `UPSHOT_READY` / `ERROR_UPSHOT` states, `ROSTER_CONFIG["company_upshot"]`, `ROSTER_CONFIG["company_data_keys"]["company_upshot"]`, `GAZER_CONFIG["fetch_company_culture_pages"]`, `TASK_CONFIG["company_upshot"]`, dispatch registration, both `agent_task` rows).
- **Canon Scope:** `patt.entity.batch-processing`, `patt.entity.batch-criteria`, `patt.task.dispatch-retry`, `stat.batch.claim-process-release`, `stat.logging.debug`, `stat.logging.error`, `stat.logging.warning`, `stat.logging.info.entity`, `stat.logging.info.dispatcher`

This ticket builds the runtime for the two company hops that AST-2069 registered. First, it
switches roster's three locate/parse success writes from a hardcoded `"WATCH"` to the configured
pass state (`GET_UPSHOT`). Next, it adds a telescope batch at `GET_UPSHOT` that scrapes culture
pages into `company_data.website_content` and always advances to `UPSHOT_READY`. Last, it adds an
Estelle batch at `UPSHOT_READY` that makes one `company_upshot` call per batch, saves
`company_data.company_upshot`, and moves each company to `WATCH`. Failures retry once through
`UPSHOT_READY_RETRY`, then go to `ERROR_UPSHOT`. `consult.run_consult_task` routes both task keys.
Display is [AST-2071](https://linear.app/astralcareermatch/issue/AST-2071).

**Claim / release is not in this ticket's code.** `dispatcher._run_unified` already claims the
company pool under one `batch_id` with `dispatch_claim_states(trigger_state)` (trigger +
`_RETRY` companion), passes only the claimed rows to `run_consult_task`, and calls
`clear_company_batch` in `finally`. The claim shape comes from the `dispatch_task` row. The new
batch functions take the claimed `companies` list and process only those rows. They never
re-query, claim, or release (`patt.entity.batch-processing` Arc 3–6,
`patt.entity.batch-criteria`, `stat.batch.claim-process-release`).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/roster.py` | `_finalize_parse_dispatch_success`, `_finalize_joblist_titles_after_chain`, `_finalize_joblist_titles_select_only` write the configured pass state; `_PERSIST_PAGE_OPTION_URL_STATES` keys off those pass states; new section with `_upshot_fail_dest`, `_transition_upshot_failures`, `_upshot_culture_text`, `company_upshot_batch` | core |
| `src/core/gazer.py` | New `fetch_company_culture_pages_batch`; module docstring In-scope list | core |
| `src/core/consult.py` | `run_consult_task` company branch: routes `fetch_company_culture_pages` and `company_upshot` | core |

No other files. No `src/utils/config.py` changes (AST-2069 owns it). No tests and no bible
(`tests/` and `docs/test-bible/**` are Betty's).

**Python for every command below:** run from the epic worktree root with
`PY=/home/susan/.cache/astral-component-venv/bin/python`, invoked as `$PY`.

**Lint gate (every stage):** `ruff check <file> --output-format concise`. Compare against
`git diff -U0 origin/dev -- <file>`. Pass = no finding on a line this ticket added, **except**
`UP006` / `UP045` (the files use `Dict` / `List` / `Optional` throughout, and new code matches
them) and `TRY401` on `logger.exception` / `_log.exception` lines that use the house
`"%s | …\n  %s: %s\n  <next step>"` format from `stat.logging.error`. Plan-time baselines are
`roster.py` 310, `gazer.py` 62, and `consult.py` 218 findings. Don't fix pre-existing findings.
Run it like this (set `f` to the file):

```bash
f=src/core/roster.py
added=$(git diff -U0 origin/dev -- $f | awk '/^@@/{split($3,a,/[+,]/); s=a[2]; n=(a[3]==""?1:a[3]); for(i=0;i<n;i++) print s+i}')
ruff check $f --output-format concise --no-cache --color never | rg '^src/' \
  | while IFS=: read file line col rest; do echo "$added" | rg -qx "$line" && echo "NEW $line:$rest"; done \
  | rg -v ' (UP006|UP045|TRY401) ' && echo 'LINT FAIL' || echo 'lint clean'
```

Expected: `lint clean`. A plan-time dry run of all three stages came back clean on every file.

## Stage 1: Locate/parse success writes the configured pass state

**Done when:** `grep -n 'state="WATCH"' src/core/roster.py` returns nothing, and
`src/core/roster.py` has no `"WATCH"` string literal on any line this stage touched.
The three success paths now write `GET_UPSHOT` and still persist `job_site`.

All edits are in `src/core/roster.py`.

1. **`_finalize_parse_dispatch_success`** (currently around line 1155). Insert this as the first
   line of the body, before `container = …`:

   ```python
       pass_state = ROSTER_CONFIG["parse_job_list"]["pass_state"]
   ```

   Then replace `state="WATCH",` in the `_save_company(...)` call with `state=pass_state,`.
   Replace `"state": "WATCH",` in the returned dict with `"state": pass_state,`.

2. **`_finalize_joblist_titles_after_chain`** (legacy locate success, currently around line
   2832). Replace these lines:

   ```python
       _save_company(short_name=short_name, company_website=company_website,
                          state="WATCH", page_option_url=job_site_url, raw_response=parsed)
       return {"short_name": short_name, "state": "WATCH", "job_site": job_site_url, "response_type": response_type, "parse_instructions": parse_instructions}
   ```

   with:

   ```python
       pass_state = ROSTER_CONFIG["locate_job_page"]["pass_states"][0]
       _save_company(short_name=short_name, company_website=company_website,
                          state=pass_state, page_option_url=job_site_url, raw_response=parsed)
       return {"short_name": short_name, "state": pass_state, "job_site": job_site_url, "response_type": response_type, "parse_instructions": parse_instructions}
   ```

3. **`_finalize_joblist_titles_select_only`** (legacy locate success, currently around line
   2900). Make the same replacement as step 2. The three lines there are textually identical
   to step 2's, so edit them inside this function only.

   ⚠️ **Decision:** the two legacy locate paths read `locate_job_page.pass_states[0]`, not
   `parse_job_list.pass_state`. They run under the locate dispatch (`TO_WATCH` / `JOBS_FOUND` /
   `PREFILTER_PASSED`), and `run_company_task`'s `JOBS_FOUND` branch already counts success as
   `result["state"] in locate_job_page.pass_states`. AST-2069 set that list to
   `["GET_UPSHOT"]`.

4. **`_PERSIST_PAGE_OPTION_URL_STATES`** (currently around line 3043). Replace:

   ```python
   _PERSIST_PAGE_OPTION_URL_STATES = frozenset({
       "WATCH", "NO_OPENINGS", "CANNOT_PARSE_JOB_SITE", "JOBSITE_SCRAPE_ISSUE", "BOT_BLOCKED",
   })
   ```

   with:

   ```python
   # Locate/parse success persists the listings URL as job_site; gaze reads it once the company reaches WATCH.
   _PERSIST_PAGE_OPTION_URL_STATES = frozenset({
       ROSTER_CONFIG["parse_job_list"]["pass_state"], *ROSTER_CONFIG["locate_job_page"]["pass_states"],
       "NO_OPENINGS", "CANNOT_PARSE_JOB_SITE", "JOBSITE_SCRAPE_ISSUE", "BOT_BLOCKED",
   })
   ```

   ⚠️ **Decision:** this step is required, not optional. `_save_company` writes
   `job_site = page_option_url` only when the state is in this set. If the success paths write
   `GET_UPSHOT` while the set still says `"WATCH"`, then `job_site` becomes `""` (or stale) and
   gaze has nothing to scrape once the company reaches `WATCH`. At plan time, no other
   `_save_company` caller passes `WATCH` (the others pass fail, exhausted, identified, or
   scrape-issue states), so `"WATCH"` comes out of the set. This is part of the same "success
   writes the configured pass state" change on `roster.py` in the ticket's Scope.

5. **Verify Stage 1:**

   ```bash
   $PY -m py_compile src/core/roster.py
   grep -n 'state="WATCH"' src/core/roster.py && echo 'FAIL: hardcoded WATCH remains' || echo 'no hardcoded WATCH'
   $PY -c "
   import src.core.roster as R
   assert 'GET_UPSHOT' in R._PERSIST_PAGE_OPTION_URL_STATES and 'WATCH' not in R._PERSIST_PAGE_OPTION_URL_STATES
   assert R._job_site_for_persist(terminal_state='GET_UPSHOT', page_option_url='https://x/jobs', pre_run_job_site='') == 'https://x/jobs'
   print('OK')"
   git diff origin/dev -- src/core/roster.py | grep -nE '^@@.*(_apply_prefilter_decoded_company_outcome|_run_batch_company_prefilter)' && echo 'FAIL: grade fn hunk' || echo 'grades untouched'
   ```

   Expected: `no hardcoded WATCH`, `OK`, `grades untouched`. Then run the lint gate on
   `src/core/roster.py`.

**Commit:** `code(AST-2070): locate/parse success writes configured pass state`

## Stage 2: GET_UPSHOT culture-page fetch batch and routing

**Done when:** the Stage 2 smoke check prints `OK`. That means a `GET_UPSHOT` batch moves every
company (cached, scraped, or nothing found) to `UPSHOT_READY`, a connectivity loss raises before
any transition, and `run_consult_task(..., dispatch_task_key="fetch_company_culture_pages")`
returns the standard summary dict.

1. **`src/core/gazer.py` module docstring:** in the first `In-scope:` line, change
   `fetch_culture_pages_batch,` to `fetch_culture_pages_batch, fetch_company_culture_pages_batch,`.

2. **`src/core/gazer.py`:** insert this function immediately **after**
   `fetch_culture_pages_batch` (after its `return {"passed": passed, "failed": failed, "total": len(jobs)}`)
   and **before** `async def fetch_website_batch(`, with two blank lines on each side:

   ```python
   async def fetch_company_culture_pages_batch(
       batch_id: str,
       companies: List[Dict[str, Any]],
       debug: bool = False,
   ) -> Dict[str, int]:
       """Scrape culture pages into company_data.website_content for GET_UPSHOT companies (AST-2070).

       Every company transitions to UPSHOT_READY whether its content was cached, scraped, or not
       found; this hop never fails a company out. No connectivity aborts before any transition.
       Returns {"passed", "failed", "total"}.
       """
       if not await check_connectivity():
           raise ConnectionError(
               f"fetch_company_culture_pages_batch: no internet connectivity, aborting batch {batch_id} "
               f"({len(companies)} companies)"
           )
       if debug:
           _log.set_debug_flag(True)
       pass_state = GAZER_CONFIG["fetch_company_culture_pages"]["pass_state"]
       company_total = len(companies)
       passed = 0

       # Sequential like fetch_culture_pages_batch: each coat-check scrape opens its own browser context.
       for company_index, company in enumerate(companies, start=1):
           short_name = company.get("short_name") or ""
           cd = company.get("company_data") if isinstance(company.get("company_data"), dict) else {}
           found = cd.get("website_content")
           if _website_content_is_recorded(found):
               outcome = "cached"
           else:
               try:
                   # Coat-check scrapes culture_links_to_explore and saves website_content itself.
                   found = await get_company_data(company, "website_content")
               except ValueError as e:
                   # Only a missing short_name/company_website escapes the coat-check; the hop still advances.
                   _log.exception(
                       "%s | company culture page fetch\n  %s: %s\n  Moving on to %s without culture pages",
                       short_name,
                       type(e).__name__,
                       e,
                       pass_state,
                   )
                   found = None
               outcome = "scraped" if found else "none found"
           transition_company_state(short_name, pass_state)
           passed += 1
           if debug:
               _log.debug_index(
                   func="gazer.fetch_company_culture_pages_batch",
                   index=company_index,
                   total=company_total,
                   identifier=_gazer_company_identifier(company),
                   outcome=f"passed -> {pass_state} ({outcome})",
               )
               _log.debug_detail(f"{_website_content_debug_summary(found)} company={short_name!r}")

       return {"passed": passed, "failed": 0, "total": company_total}
   ```

   ⚠️ **Decision:** cached means `_website_content_is_recorded(company_data.website_content)`.
   That's the same test the job-side `fetch_culture_pages_batch` uses, so the two hops agree on
   what counts as recorded. When nothing is recorded, `get_company_data(company,
   "website_content")` runs the existing `_fetch_website_content` coat-check. That handler
   returns `None` for no links, no URLs, or all-empty scrapes. It persists
   `company_data.website_content` itself whenever at least one page scraped (AC4). The job-side
   hop then finds it cached later. There's no `update_company_last_scan_at` call: no
   `freq_hrs` gates this hop.

   ⚠️ **Decision:** no page-count, size, or time limits are added. The coat-check's existing
   `ROSTER_CONFIG["culture_pages"]["max_pages"]` cap is untouched.

3. **`src/core/consult.py` `run_consult_task`:** insert this branch immediately **after** the
   `if task_key == "fetch_job_pages":` branch (it ends with its `return {...}` /
   `"total_errors": errors,` / `}`) and **before** `from src.utils.config import INFLOW_CONFIG`:

   ```python
           if task_key == "fetch_company_culture_pages":
               from src.core.gazer import fetch_company_culture_pages_batch
               r = await _debug_await(
                   "gazer.fetch_company_culture_pages_batch",
                   f"batch_id={batch_id}, n={len(entities)}",
                   fetch_company_culture_pages_batch(batch_id, entities, debug=debug),
               )
               total = r.get("total", len(entities))
               passed = r.get("passed", 0)
               failed = r.get("failed", 0)
               errors = max(0, total - passed - failed)
               return {
                   "total_processed": total,
                   "total_passed": passed,
                   "total_failed": failed,
                   "total_errors": errors,
               }
   ```

   The dispatcher logs the standard task-completed line from this summary
   (`stat.logging.info.dispatcher`). Nothing else is added.

4. **Verify Stage 2** (smoke check run inline, not committed):

   ```bash
   $PY -m py_compile src/core/gazer.py src/core/consult.py
   $PY - <<'EOF'
   import asyncio
   import src.core.gazer as G
   import src.core.consult as C
   moves = {}
   async def up(): return True
   async def down(): return False
   async def coat(company, key):
       assert key == "website_content"
       return {"b": [{"url": "u", "content": "x"}]}.get(company["short_name"])
   G.check_connectivity = up
   G.get_company_data = coat
   G.transition_company_state = lambda sn, st: moves.update({sn: st})
   rows = [
       {"short_name": "a", "company_data": {"website_content": [{"url": "u", "content": "cached"}]}},
       {"short_name": "b", "company_data": {"culture_links_to_explore": [1]}},
       {"short_name": "c", "company_data": {"culture_links_to_explore": []}},
   ]
   r = asyncio.run(G.fetch_company_culture_pages_batch("smoke", rows))
   assert moves == {"a": "UPSHOT_READY", "b": "UPSHOT_READY", "c": "UPSHOT_READY"}, moves
   assert r == {"passed": 3, "failed": 0, "total": 3}, r
   G.check_connectivity = down
   moves.clear()
   try:
       asyncio.run(G.fetch_company_culture_pages_batch("smoke", rows))
       raise SystemExit("FAIL: no connectivity abort")
   except ConnectionError:
       pass
   assert moves == {}, moves
   G.check_connectivity = up
   s = asyncio.run(C.run_consult_task("company", "GET_UPSHOT", rows[:1], "smoke",
                                      dispatch_task_key="fetch_company_culture_pages"))
   assert s == {"total_processed": 1, "total_passed": 1, "total_failed": 0, "total_errors": 0}, s
   print("OK")
   EOF
   ```

   Expected: `OK`. Then run the lint gate on `src/core/gazer.py` and `src/core/consult.py`.

**Commit:** `code(AST-2070): GET_UPSHOT culture-page fetch batch and consult routing`

## Stage 3: UPSHOT_READY Estelle batch and routing

**Done when:** the Stage 3 smoke check prints `OK`. That means one `do_task(task_key="company_upshot")`
call per batch, returned companies saved and moved to `WATCH`, a missing id going
`UPSHOT_READY → UPSHOT_READY_RETRY` and `UPSHOT_READY_RETRY → ERROR_UPSHOT`, fabricated ids
ignored, and `run_consult_task(..., dispatch_task_key="company_upshot")` returning the standard
summary dict.

1. **`src/core/roster.py`:** insert this section immediately **after** `prefilter_company_batch`
   (after its final `return batch_result`) and **before** the `# ---- Find job page ----`
   comment, with two blank lines on each side. This placement keeps every hunk clear of
   `_apply_prefilter_decoded_company_outcome` and `_run_batch_company_prefilter` (AC8).
   Everything it uses is already imported in `roster.py`: `do_task`, `enumerate_array`,
   `ensure_batch_response_entity_ids`, `is_provider_balance_refusal`, `retry_base`,
   `ROSTER_CONFIG`, `TASK_CONFIG`, `Set`.

   ```python
   # ---- Company upshot (AST-2054) ----

   def _upshot_fail_dest(entity_state: Optional[str], cfg: Dict[str, Any]) -> str:
       """First failure → retry holding; a failure out of the retry holding → terminal error (patt.task.dispatch-retry)."""
       return cfg["error_state"] if (entity_state or "").strip() == cfg["retry_state"] else cfg["retry_state"]


   def _transition_upshot_failures(companies: List[Dict[str, Any]], cfg: Dict[str, Any], reason: str) -> int:
       """Route each company to retry or error with a per-item who -> dest [why]. Returns count sent to retry."""
       retried = 0
       for company in companies:
           dest = _upshot_fail_dest(company.get("state"), cfg)
           transition_company_state(company["short_name"], dest)
           _log_fail_dest(company["short_name"], dest, reason)
           if retry_base(dest):
               retried += 1
       return retried


   def _upshot_culture_text(website_content: Any) -> str:
       """website_content as prompt text: [{url, content}] pages, or a legacy plain string."""
       if isinstance(website_content, str):
           return website_content.strip()
       pages = [
           p for p in (website_content or [])
           if isinstance(p, dict) and str(p.get("content") or "").strip()
       ]
       return "\n\n".join(f"### {p.get('url') or ''}\n{str(p['content']).strip()}" for p in pages)


   async def company_upshot_batch(
       batch_id: str,
       companies: List[Dict[str, Any]],
       ctx: Optional[Dict[str, Any]] = None,
       debug: bool = False,
   ) -> Dict[str, Any]:
       """Pattern-A Estelle upshot batch at UPSHOT_READY: one do_task, decode by company_id,
       save company_data.company_upshot, transition to WATCH. No verdict fail — only technical
       failures route, once to the retry holding and then to the terminal error state."""
       cfg = ROSTER_CONFIG["company_upshot"]
       agent_task_key = cfg["task_key"]
       upshot_key = ROSTER_CONFIG["company_data_keys"]["company_upshot"]
       rows = [
           {
               "company_id": c["short_name"],
               "short_name": c["short_name"],
               "state": c.get("state"),
               "company_data": c.get("company_data") or {},
           }
           for c in companies
       ]
       input_by_id = {r["company_id"]: r for r in rows}

       # One block per company, keyed 000, 001, … to match the agent_task prompt's input contract.
       blocks: List[str] = []
       for r in rows:
           cd = r["company_data"]
           parts = [f"[company_id={r['company_id']}]", f"\n## Homepage Content\n{(cd.get('homepage_text') or '').strip()}"]
           culture = _upshot_culture_text(cd.get("website_content"))
           if culture:
               parts.append(f"\n## Culture Pages\n{culture}")
           grades = [g for g in (cd.get("prefilter_grades") or []) if isinstance(g, dict)]
           if grades:
               lines = "\n".join(f"- {g.get('vector')}={g.get('grade')}: {g.get('reason') or ''}" for g in grades)
               parts.append(f"\n## Prefilter Grades\n{lines}")
           blocks.append("\n".join(parts))
       live_content = enumerate_array(
           "COMPANY UPSHOT ROWS",
           blocks,
           index_key="index",
           index_values=[f"{i:03d}" for i in range(len(rows))],
       )

       task_ctx = {**(ctx or {}), "batch_entities": rows, "batch_size": len(rows)}
       do_index = f"company_upshot_batch_{batch_id}"
       logger.debug("Calling agent.do_task: task_key=%s index=%s", agent_task_key, do_index)
       logger.debug("Calling agent.do_task live_content: %s", live_content)
       result = await do_task(
           task_key=agent_task_key,
           live_content=live_content,
           index=do_index,
           ctx=task_ctx,
           debug=debug,
       )
       logger.debug("Response from agent.do_task: %s", result)

       if not result.get("success"):
           if is_provider_balance_refusal(result):
               # Provider refused for balance: hold state; the dispatcher stops the run and alerts once.
               return {
                   "passed": 0,
                   "failed": 0,
                   "total": len(rows),
                   "failure_class": result.get("failure_class"),
                   "state_held": True,
               }
           if result.get("empty_tokens"):
               # Data defect, not an agent miss: straight to the terminal error, never the retry holding.
               for r in rows:
                   transition_company_state(r["short_name"], cfg["error_state"])
                   _log_fail_dest(r["short_name"], cfg["error_state"], "empty prompt tokens")
               return {"passed": 0, "failed": 0, "total": len(rows), "retried": 0}
           retried = _transition_upshot_failures(rows, cfg, f"do_task: {result.get('error') or 'do_task failed'}")
           return {"passed": 0, "failed": 0, "total": len(rows), "retried": retried, **_rate_limit_tag(result)}

       response_companies = (result.get("parsed_response") or {}).get("companies") or []
       received_ids = {rc.get("company_id") for rc in response_companies}
       missing_rows = [r for cid, r in input_by_id.items() if cid not in received_ids]
       retried = _transition_upshot_failures(missing_rows, cfg, "upshot batch omitted this id")

       passed = 0
       saved: Set[str] = set()
       seen: Set[str] = set()
       for rc in response_companies:
           cid = rc.get("company_id")
           # Fabricated ids never touch a row this batch didn't claim; a repeated id is decoded once.
           if cid not in input_by_id or cid in seen:
               continue
           seen.add(cid)
           upshot = str(rc.get("upshot") or "").strip()
           if not upshot:
               retried += _transition_upshot_failures([input_by_id[cid]], cfg, "empty upshot")
               continue
           try:
               save_company_data(cid, {upshot_key: upshot})
               transition_company_state(cid, cfg["pass_state"])
           except ValueError as e:
               logger.debug(
                   "%s | company upshot save\n  %s: %s\n  Routing to retry or error",
                   cid,
                   type(e).__name__,
                   e,
                   exc_info=True,
               )
               retried += _transition_upshot_failures([input_by_id[cid]], cfg, f"save: {type(e).__name__}: {e}")
               continue
           _entity_info(cid, "company", "upshot saved", f"{len(upshot.split())} words")
           saved.add(cid)
           passed += 1

       agent_ref = result.get("agent_ref")
       if agent_ref and saved:
           try:
               ensure_batch_response_entity_ids(TASK_CONFIG[agent_task_key]["entity_type"], sorted(saved), agent_ref)
           except Exception as stamp_err:
               logger.exception(
                   "%s | company ensure_batch_response_entity_ids\n  %s: %s\n  Continuing without stamping those entity ids",
                   batch_id,
                   type(stamp_err).__name__,
                   stamp_err,
               )

       return {"passed": passed, "failed": 0, "total": len(rows), "retried": retried}
   ```

   ⚠️ **Decision (failure routing):** per `patt.task.dispatch-retry` Arc 4, `_upshot_fail_dest`
   checks whether the company's **current** state is already the retry holding. It doesn't
   count attempts. Every routed failure (`do_task` failure, missing id, empty upshot, save
   `ValueError`) leaves `UPSHOT_READY`, so no failure stays in state (Arc 5). Pre-provider
   `empty_tokens` skips the retry holding and goes straight to the configured terminal
   `error_state` (`ERROR_UPSHOT`), per that pattern's § When this doesn't apply. A
   provider-balance refusal holds state and returns `state_held`, as `_run_batch_company_prefilter`
   does. That's a provider outage, not an entity failure.

   ⚠️ **Decision (logging):** a per-item `who -> dest [why]` goes through the existing
   `_log_fail_dest`. It logs WARNING for the retry holding and ERROR for `ERROR_UPSHOT`
   (`stat.logging.warning` / `stat.logging.error`). The caught save `ValueError` puts its
   traceback on debug, not `logger.exception` (`stat.logging.warning` carve-out). A saved upshot
   logs one `_entity_info` line, `id | company upshot saved: N words`
   (`stat.logging.info.entity`). `transition_company_state` already logs the state move.
   `Calling` / `Response` debug lines wrap `do_task` (`stat.logging.debug`).

   ⚠️ **Decision (prompt input):** the block holds `homepage_text`, `website_content`
   (culture pages, when present), and `prefilter_grades` as `VECTOR=GRADE: reason` lines. That's
   what the AST-2069 `company_upshot` prompt says each block contains. The `{$FIRST_NAME}` /
   `{$BIO_SUMMARY}` / `{$SELECTED_AGENT}` tokens resolve from `ctx` inside `do_task`, as they do
   for `prefilter_company`. No truncation or size cap is applied to any block.

   ⚠️ **Decision (no chunk index):** `company_upshot` isn't in the dispatcher's
   `_CHUNK_EXHAUST_CONSULT_JOB_KEYS` (that's job-only), so `run_consult_task` never receives a
   `batch_chunk_index` for it. One `do_task` covers the whole claimed batch (AC6).

2. **`src/core/consult.py` `run_consult_task`:** insert this branch immediately **after** the
   `if task_key == "prefilter_company":` branch (it ends with `**_rate_limit_tag(r),` / `}`) and
   **before** `if task_key == "vet_inflow_discovery":`:

   ```python
           if task_key == "company_upshot":
               r = await _debug_await(
                   "roster.company_upshot_batch",
                   f"batch_id={batch_id}, n={len(entities)}",
                   roster.company_upshot_batch(batch_id, entities, ctx=ctx, debug=debug),
               )
               total = r.get("total", len(entities))
               passed = r.get("passed", 0)
               failed = r.get("failed", 0)
               # Retry-routed companies are not run errors (same accounting as prefilter_company).
               errors = max(0, total - passed - failed - r.get("retried", 0))
               return {
                   "total_processed": total,
                   "total_passed": passed,
                   "total_failed": failed,
                   "total_errors": errors,
                   **_rate_limit_tag(r),
               }
   ```

3. **Verify Stage 3** (smoke check run inline, not committed):

   ```bash
   $PY -m py_compile src/core/roster.py src/core/consult.py
   $PY - <<'EOF'
   import asyncio
   import src.core.roster as R
   import src.core.consult as C
   calls, moves, saved = [], {}, {}
   async def fake_do_task(**kw):
       calls.append(kw["task_key"])
       assert "[company_id=a]" in kw["live_content"] and "## Culture Pages" in kw["live_content"]
       assert "- V=A: r" in kw["live_content"]
       return {"success": True, "parsed_response": {"companies": [
           {"company_id": "a", "upshot": "Acme builds rockets."},
           {"company_id": "z", "upshot": "fabricated"},
       ]}}
   R.do_task = fake_do_task
   R.save_company_data = lambda sn, d, replace=False: saved.update({sn: d})
   R.transition_company_state = lambda sn, st: moves.update({sn: st})
   rows = [
       {"short_name": "a", "state": "UPSHOT_READY", "company_data": {
           "homepage_text": "hi", "website_content": [{"url": "u", "content": "c"}],
           "prefilter_grades": [{"vector": "V", "grade": "A", "reason": "r"}]}},
       {"short_name": "b", "state": "UPSHOT_READY_RETRY", "company_data": {}},
       {"short_name": "c", "state": "UPSHOT_READY", "company_data": {}},
   ]
   r = asyncio.run(R.company_upshot_batch("smoke", rows))
   assert calls == ["company_upshot"], calls
   assert moves == {"a": "WATCH", "b": "ERROR_UPSHOT", "c": "UPSHOT_READY_RETRY"}, moves
   assert saved == {"a": {"company_upshot": "Acme builds rockets."}}, saved
   assert r == {"passed": 1, "failed": 0, "total": 3, "retried": 1}, r
   calls.clear(); moves.clear(); saved.clear()
   s = asyncio.run(C.run_consult_task("company", "UPSHOT_READY", rows, "smoke",
                                      dispatch_task_key="company_upshot"))
   assert calls == ["company_upshot"], calls
   assert s == {"total_processed": 3, "total_passed": 1, "total_failed": 0, "total_errors": 1}, s
   print("OK")
   EOF
   git diff origin/dev -- src/core/roster.py | grep -nE '^@@.*(_apply_prefilter_decoded_company_outcome|_run_batch_company_prefilter)' && echo 'FAIL: grade fn hunk' || echo 'grades untouched'
   ```

   Expected: `OK`, then `grades untouched`. Also confirm by eye that no `+` / `-` line in
   `git diff origin/dev -- src/core/roster.py` falls inside either prefilter function body.
   Then run the lint gate on `src/core/roster.py` and `src/core/consult.py`.

**Commit:** `code(AST-2070): UPSHOT_READY Estelle company_upshot batch and consult routing`

## Acceptance criteria → stage map

| Ticket AC | Verified in |
|---|---|
| 2. Nothing writes WATCH directly | Stage 1 step 5 (grep); pass-state value is AST-2069 config, already on this ref |
| 3. Parse success lands in GET_UPSHOT | Stage 1 step 1 (`_finalize_parse_dispatch_success` writes `parse_job_list.pass_state`); Betty's tests cover the dispatch end to end |
| 4. GET_UPSHOT always advances | Stage 2 step 4 |
| 5. Upshot written, then WATCH | Stage 3 step 3 |
| 6. One Estelle call per batch | Stage 3 step 3 (`calls == ["company_upshot"]`) |
| 7. Retry then error | Stage 3 step 3 (`c` → `UPSHOT_READY_RETRY`, `b` → `ERROR_UPSHOT`) |
| 8. Grades unchanged | Stage 1 step 5 and Stage 3 step 3 hunk check |

## Out of scope (do not touch)

- `src/utils/config.py` and `data/admin/agent_task.json`: AST-2069 (done).
- `src/ui/**`, including `api_companies.py`: AST-2071.
- `run_company_task` per-entity branches. Both new keys route in `run_consult_task` before its `run_company_task` fallback.
- `src/core/dispatcher.py` claim/release. It's already correct for company pools.
- Live `dispatch_task` schedule rows for the two keys. Susan/admin creates them; this is the prep-uat reminder Joan and Radia raised on AST-2069.
- `_apply_prefilter_decoded_company_outcome`, `_run_batch_company_prefilter`, `prefilter_company`, and the job-side `fetch_culture_pages_batch`.

## Estimate

Confirm Chuckles estimate: 5 — agree


## Joan validate

[plan-rubric]
**Ticket:** AST-2070
**Overall:** APPROVED
**Corpus:** 2d1b73da19cf1d14276e5c26f52b37aa8047d159
**Publish ref:** `origin/sub/AST-2054/AST-2070-upshot-hops` @ `71e1ad85300df465ebe9a71579e5857717409603`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-processing | A | | |
| patt.entity.batch-criteria | A | | |
| patt.task.dispatch-retry | A | | |
| stat.batch.claim-process-release | A | | |
| stat.logging.debug | B | | |
| stat.logging.error | A | | |
| stat.logging.warning | A | | |
| stat.logging.info.entity | A | | |
| stat.logging.info.dispatcher | X | | consult/gazer/roster return summaries; dispatcher still emits task-completed (unchanged) |

## Traceability

AC 2–3 → Stage 1; AC 4 → Stage 2; AC 5–7 → Stage 3; AC 8 → Stage 1/3 hunk guards. Parent AC 1 / 9–14 N/A (registration AST-2069, display AST-2071). Parent AC 10–11 satisfied indirectly via AC 8 + out-of-scope on prefilter bodies.

## Findings

**acceptable** — Claim/release stays in `dispatcher._run_unified`; new batches consume the claimed `companies` list only, matching `fetch_culture_pages_batch` / `_run_batch_company_prefilter` and the plan’s explicit claim/release note.

**acceptable** — Stage 1 `_PERSIST_PAGE_OPTION_URL_STATES` change is correctly tied to `GET_UPSHOT` success writes so `job_site` persists before the upshot pipeline (not an optional extra).

**discuss** — Stage 2 planned docstring line “No connectivity aborts before any transition” contradicts the code (and smoke check): `check_connectivity` raises before the loop. Fix the docstring when implementing; the executable block and AC 4 abort behavior are correct.

**discuss** — `fetch_company_culture_pages` uses `_log.exception` on coat-check `ValueError` then still advances — heavy for an expected “missing website” path, but aligned with “never fail out of GET_UPSHOT”; worth watching in UAT logs, not a plan blocker.

**acceptable** — `company_upshot_batch` mirrors Pattern-A prefilter: one `do_task`, `empty_tokens` → terminal error, provider balance `state_held`, `_log_fail_dest` / `_upshot_fail_dest` for retry vs `ERROR_UPSHOT`, smoke asserts AC 6–7.

**acceptable** — AC 2 grep `state="WATCH"` targets the three locate/parse success paths at plan-time lines ~1171/2833/2901; no other `state="WATCH"` callers in `roster.py` today.

**Definition fidelity (R6):** Scope is three core files only; depends on AST-2069 registration (`fetch_company_culture_pages`, `company_upshot`, states). Out-of-scope list protects prefilter grade functions (AC 8). Estimate 5 — agree.

context_tokens≈52000

## Review

- **Branch:** `sub/AST-2054/AST-2070-upshot-hops`
- **Stage 1:** `7d471237c` — `_finalize_parse_dispatch_success` and both legacy locate-success paths write the configured pass state (`GET_UPSHOT`); `_PERSIST_PAGE_OPTION_URL_STATES` keys off those pass states so `job_site` still persists
- **Stage 2:** `f8d1feabd` — `gazer.fetch_company_culture_pages_batch` (always → `UPSHOT_READY`, connectivity abort before transitions); `run_consult_task` routes `fetch_company_culture_pages`
- **Stage 3:** `732259241` — `roster.company_upshot_batch` (one `do_task`, saves `company_upshot`, → `WATCH`; retry → `UPSHOT_READY_RETRY`, then `ERROR_UPSHOT`; `empty_tokens` → `ERROR_UPSHOT`; balance refusal held) with `_upshot_fail_dest` / `_transition_upshot_failures` / `_upshot_culture_text`; `run_consult_task` routes `company_upshot`
- **Build notes:**
  - All plan verify steps pass (compile, `state="WATCH"` grep empty, persist-set check, both smoke checks, prefilter-function hunk guard, lint gate clean on all three files).
  - Joan discuss 1: Stage 2 docstring reworded to "Lost connectivity raises ConnectionError before any transition." (wording only; code as planned).
  - Joan discuss 2: `_log.exception` on coat-check `ValueError` kept as planned; worth watching in UAT logs.
  - Live `dispatch_task` schedule rows for `fetch_company_culture_pages` / `company_upshot` still need creating (prep-uat reminder carried from AST-2069).
  - No tests touched; coverage is Betty's `qa-child`.


## Radia review

[code-rubric]

**Ticket:** AST-2070  
**Publish ref:** `517c1a3fa75e0f494f48467d32c4359b8a42abf2` (`origin/sub/AST-2054/AST-2070-upshot-hops`)  
**Corpus:** `2d1b73da19cf1d14276e5c26f52b37aa8047d159`  
**Overall:** CLEAN  

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-processing | A | | |
| patt.entity.batch-criteria | A | | |
| patt.task.dispatch-retry | A | | |
| stat.batch.claim-process-release | A | | |
| stat.logging.debug | B | | `fetch_company_culture_pages_batch` uses gazer `debug_index`/`debug_detail` only when `debug=True`, no `logger.debug` begin/end on the company loop |
| stat.logging.error | A | | |
| stat.logging.warning | A | | |
| stat.logging.info.entity | A | | |
| stat.logging.info.dispatcher | X | | |

## Column diff vs plan stage

(aligned) — Joan: same grades including **B** on `stat.logging.debug` and **X** on `stat.logging.info.dispatcher`.

## Frame diff

- [ ] **Boundaries / prep-uat:** Live `dispatch_task` rows for `fetch_company_culture_pages` and `company_upshot` exist before epic UT ticks claim the new hops (carried from AST-2069; still out of scope for this code).

## Findings

**fix-now** — (none)

**discuss**

- **Integrated publish ref (@susan):** Three-dot diff vs `origin/dev` still includes **AST-2069** registration (`config.py`, `agent_task.json`) and **AST-2071** display (`src/ui/**`, `api_companies.py`) plus sibling issue docs — not in AST-2070 plan §Files Changed (three core files only). **Default:** Score runtime hops on `roster.py` / `gazer.py` / `consult.py`; treat stacked epic tip as merge-child norm unless Susan wants child-isolated review surfaces.

**advisory**

- **sibling test carry:** `merge-tests` includes unrelated frontend test edits (e.g. `test_NavigationShell.test.tsx` light-wordmark case removed) with no AST-2070 product touch — note once; not scored.
- **UAT log noise:** `fetch_company_culture_pages_batch` logs `_log.exception` on coat-check `ValueError` (missing website) then still advances to `UPSHOT_READY` — Joan flagged; behavior matches “never fail out of GET_UPSHOT”; watch log volume in UT.
- **Joan docstring discuss:** Stage 2 docstring reworded on tip to match connectivity abort (engineer build notes) — no code defect.

### Plan fidelity (§5.4)

- **Stage 1:** `_finalize_parse_dispatch_success` and legacy locate success paths use `ROSTER_CONFIG` pass state (`GET_UPSHOT`); no `state="WATCH"` literals on publish ref `roster.py`; `_PERSIST_PAGE_OPTION_URL_STATES` keys off configured pass states.
- **Stage 2:** `fetch_company_culture_pages_batch` — connectivity abort before loop; per-company cache/scrape via `get_company_data`; always `transition_company_state` → `UPSHOT_READY`; consult routes `fetch_company_culture_pages`.
- **Stage 3:** `company_upshot_batch` — one `do_task`, decode by `company_id`, save `company_upshot`, → `WATCH`; `_upshot_fail_dest` / `_transition_upshot_failures` for retry vs `ERROR_UPSHOT`; `empty_tokens` → terminal error; provider balance `state_held`; consult routes `company_upshot` with prefilter-style error accounting (`retried` excluded from errors).
- **AC 8:** No hunks inside `_apply_prefilter_decoded_company_outcome` / `_run_batch_company_prefilter` bodies (plan guard intent).
- Betty tests on ref: `test_gazer` / `test_consult` / `test_roster` upshot coverage present in diff (qa-child; not re-read full bible).

### Estimate footprint (§5.4)

Confirm **5** — three core modules, two batch implementations + consult wiring; fits.

## What's solid

- Claim/release stays in dispatcher; new batches only process the claimed `companies` list (matches `fetch_culture_pages_batch` / prefilter Pattern A).
- Retry routing mirrors house `retry_of("UPSHOT_READY")` + `ERROR_UPSHOT` terminal; `empty_tokens` bypasses retry per `patt.task.dispatch-retry` carve-out.
- `company_upshot_batch` preserves grade inputs in prompt blocks without mutating prefilter grade storage paths.

## Recommended actions (downstream — not Radia)

- Chuckles: append artifact, `docs(AST-2070): Radia review — clean`, post slim upshot, **Review Posted** → datt **PROCEED** when epic gates allow.
- Susan/prep-uat: frame-diff `dispatch_task` rows; optional log watch on culture-fetch `ValueError` exceptions during UT.

context_tokens≈45000
