# AST-2025 — Qualify routing and click-through runner

- **Ticket:** [AST-2025](https://linear.app/astralcareermatch/issue/AST-2025)
- **Parent:** [AST-2022 — New Fetch task for RELATIVE_JOB_LINK](https://linear.app/astralcareermatch/issue/AST-2022)
- **Publish ref:** `sub/AST-2022/AST-2025-relative-link-runner` (origin only)
- **Canon scope:** `patt.entity.batch-processing`, `astral.batch.claim-process-release`, `stat.logging.debug`, `stat.logging.info.entity`, `stat.logging.warning`, `stat.logging.error`
- **Depends on (already on this ref via `origin/ftr/AST-2022-relative-job-link`):**
  [AST-2023](https://linear.app/astralcareermatch/issue/AST-2023) — `click_through_visible_text(list_url, href) -> (final_url, text)`,
  `PlaywrightInfraError.failure_class == TELESCOPE_CLICK_TARGET_MISSING` on a missing anchor;
  [AST-2024](https://linear.app/astralcareermatch/issue/AST-2024) — task key `fetch_relative_jd`,
  `GAZER_CONFIG["fetch_relative_jd"]` (`trigger_state` `RELATIVE_JOB_LINK`, `pass_state` `JD_READY`,
  `fail_state` `RELATIVE_LINK_FAIL`, `error_states` = the five JD outcomes),
  `TASK_CONFIG["qualify_job_listings"]["relative_link_state"] == "RELATIVE_JOB_LINK"`, dispatch
  `job` / `RELATIVE_JOB_LINK` binding, `agent_task.json` row, and every needed `JOB_STATES` prior.

The product half of AST-2022. `qualify_job_listings` stops throwing away passing jobs whose link
is non-empty but not `http`: it initializes them with the relative link as-is and parks them in
`RELATIVE_JOB_LINK`. A blank link still raises `InvalidJobLinkError` exactly as today. A new gazer
runner, `fetch_relative_jd_batch`, takes the jobs the dispatcher claimed for `fetch_relative_jd`.
For each one it asks Telescope to open the company's `job_site`, click the anchor whose `href`
equals the stored relative link, and return the destination URL and visible text. It then saves
the resolved absolute URL into `job.job_link` and runs the **same** JD gates `fetch_jd_batch`
uses, which this ticket lifts into one shared helper, `_apply_jd_gates`. A click or Telescope
failure sends the job to `RELATIVE_LINK_FAIL` with `job_link` still relative. The job dispatch
router gets a `fetch_relative_jd` branch. Claim and release are the dispatcher's existing generic
job path (`dispatcher.py`: `get_new_job_batch` by the task's `trigger_state`, `clear_job_batch` in
`finally`). The runner processes exactly the entities it is handed and never re-queries by state.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/gazer.py` | New `_apply_jd_gates` helper (JD gate logic lifted out of `fetch_jd_batch`); `fetch_jd_batch` calls it; new `fetch_relative_jd_batch` runner; imports; module docstring | core |
| `src/core/consult.py` | `qualify_job_listings.process()` routes non-empty non-`http` links to `cfg["relative_link_state"]`, raises `InvalidJobLinkError` only for empty; `InvalidJobLinkError` docstring; job dispatch router `fetch_relative_jd` branch | core |

No other files. No config, no `agent_task.json`, no tracker/data changes (the resolved link is
written with the existing `tracker.persist_http_job_link`), no tests, no bible.

⚠️ **Decision — resolved link is written with `tracker.persist_http_job_link`.** It is the
existing link-only column writer (AST-1693): http(s) only, no `initialize_job`, no title needed.
`job_link` has no unique index (the job unique index is the company / title / company_job_id
triple), so overwriting it can't collide. The runner only calls it after confirming `final_url` is
http(s). A non-http `final_url` is treated as a click-through failure (`RELATIVE_LINK_FAIL`), so a
job can never reach a JD destination with `job_link` still relative (AC 4).

⚠️ **Decision — empty / too-short text after a successful click → `JD_SCRAPE_FAIL`.** The shared
helper takes that destination as a parameter (`short_state`). `fetch_jd_batch` passes its own
`fail_state`. `fetch_relative_jd_batch` passes `GAZER_CONFIG["fetch_jd"]["fail_state"]`
(`JD_SCRAPE_FAIL`), because the parent wants "the matching `JD_SCRAPE_FAIL*` state, same as
`fetch_jd`" and AST-2024 put `JD_SCRAPE_FAIL` in this task's `error_states`, not in its
`fail_state`. Classified outcomes (cookie / bot / missing / closed) still come from the one
`_JD_ERROR_STATES` map.

⚠️ **Decision — logging split on a click-through exception.** A missing anchor
(`PlaywrightInfraError` with `failure_class == TELESCOPE_CLICK_TARGET_MISSING`) is the parent's
"click-target miss", a configured fail path, so it gets one `logger.warning` (`who -> dest [why]`)
and no traceback. Any other exception from the click-through call (Telescope timeout, job failed,
queue error) also routes to `RELATIVE_LINK_FAIL` (parent §5 "errors out"). `RELATIVE_LINK_FAIL`
is not a retry holding, so per `stat.logging.error` / `stat.logging.warning` Resolution 2 that
handler logs once with `logger.exception` (live facts plus the next step, `Continuing to the next
job`). The runner is the handler that picks the destination; the client does not log
(AST-2023).

⚠️ **Decision — `check_connectivity` guard mirrors `fetch_jd_batch`.** If the box is offline the
runner raises `ConnectionError` before touching any job, exactly like `fetch_jd_batch`.
Otherwise one network blip would push the whole claimed batch into `RELATIVE_LINK_FAIL`. The
dispatcher still releases the batch in its `finally`.

⚠️ **Decision — no `debug=` parameter on the new runner.** `stat.logging.debug`: the dispatcher
run entry sets the `log_debug` ContextVar (`dispatcher.py` `log_debug.set(debug)`), and callees
don't take `debug=` just to log. The new runner uses plain ungated `_log.debug(...)` joints, not
`debug_index` / `debug_detail` (Style D). `fetch_jd_batch` keeps its `debug` parameter and its
own remaining Style-D lines untouched; only the gate code that moves into the helper is converted.

⚠️ **Decision — concurrency matches `fetch_jd_batch`.** All claimed jobs run through
`asyncio.gather(..., return_exceptions=False)`. Batch size is whatever `dispatch_task.batch_size`
claimed (`patt.entity.batch-criteria` is AST-2024's). The runner adds no cap or limit of its own.

## Notes for every stage

- **Python interpreter:** use `~/astral/.venv/bin/python` for every import / verify command below.
  The system `python3` has no `asyncpg`, so `src.external.telescope` (imported by `gazer`) fails
  to import under it. Prefix import-time commands with `ASTRAL_DB_DIR=$(mktemp -d)` because
  `config.py` reads `os.environ["ASTRAL_DB_DIR"]` at import.
- **Compile + lint before every commit (Susan's rule).**
  - Compile: `~/astral/.venv/bin/python -m py_compile <file>` for each file touched in the stage.
    Must exit 0.
  - Lint: `ruff check src/core/gazer.py src/core/consult.py`. Baseline before this ticket is
    **280** findings across the two files. **No new finding may sit on a line this ticket
    added or changed.** Compare with `ruff check <file> --output-format concise` before and after
    and diff the line-attributed output. The only pre-approved suppression is the one
    `# noqa: BLE001` in Stage 1 step 5. Do not add any other `noqa` and do not `--fix` the file
    (that would rewrite unrelated pre-existing lines).
- Anchor every edit by the **content** quoted below, not by line number.
- **Tests are read-only for engineers.** After Stage 2, run and record (do not edit):
  `ASTRAL_DB_DIR=$(mktemp -d) ~/astral/.venv/bin/python -m pytest tests/component/core/test_gazer.py tests/component/core/test_consult.py -q`.
  Run the same command once **before Stage 1's first edit** to get the baseline, and record both
  counts. Expected by-design break, left for Betty: `test_consult.py::TestAst1895InvalidJobLinkError`
  asserts `"process_fn InvalidJobLinkError: relative job_link: /relative"`. Relative links no
  longer raise (AC 2/3). The empty-link assertion on the same test must still pass, because
  the message stays `f"empty job_link: {job_link}"`.

---

## Stage 1: Shared JD gates + click-through runner (`src/core/gazer.py`)

**Done when:** `fetch_jd_batch` delegates every post-scrape gate to `_apply_jd_gates`, with no
inline `_prune_jd` / `min_chars` / `_classify_jd` left in it. `fetch_relative_jd_batch` exists.
The stubbed verify script in step 7 prints `ok`. `rg -n '_apply_jd_gates' src/core/gazer.py`
shows exactly 3 hits: the `def` and one call in each runner.

1. In `src/core/gazer.py`, module docstring: change the line
   `In-scope: scrape_one, process_gazer_batch, fetch_jd_batch, fetch_culture_pages_batch,`
   to
   `In-scope: scrape_one, process_gazer_batch, fetch_jd_batch, fetch_relative_jd_batch, fetch_culture_pages_batch,`.

2. In `src/core/gazer.py`, imports:
   - Change `from src.core.tracker import ingest_jobs, save_job_data, transition_job_state` to
     `from src.core.tracker import ingest_jobs, persist_http_job_link, save_job_data, transition_job_state`.
   - In the `from src.external.telescope import (` block, add these three names as new lines
     directly after `    run_one_shot,` (before the closing `)`):
     ```python
         click_through_visible_text,
         PlaywrightInfraError,
         TELESCOPE_CLICK_TARGET_MISSING,
     ```

3. In `src/core/gazer.py`, insert this function **directly after** `_classify_jd` (after its
   final `return "ok"`, before `async def fetch_jd_batch(`), separated by two blank lines on each
   side:

   ```python
   def _apply_jd_gates(job: Dict[str, Any], text: str, *, short_state: str, pass_state: str) -> bool:
       """Shared JD gates for fetch_jd_batch and fetch_relative_jd_batch (AST-2025).

       collapse blank lines -> empty check -> prune -> min_chars -> classify. Saves the JD and
       transitions the job. Empty / too-short -> short_state; classified -> _JD_ERROR_STATES;
       ok -> pass_state. Returns True only when the job reached pass_state.
       """
       jd_key = TRACKER_CONFIG.get("job_data_keys", {}).get("job_description", "job_description")
       min_chars = TRACKER_CONFIG.get("jd_min_chars", 200)
       aid = job.get("astral_job_id", "")
       text = collapse_consecutive_blank_lines(text)
       if not text or not text.strip():
           _log.warning("%s -> %s [empty visible text]", aid, short_state)
           transition_job_state([aid], short_state)
           return False
       text = _prune_jd(text, job.get("job_title", ""))
       if len(text) < min_chars:
           _log.warning("%s -> %s [JD too short: %d < %d chars]", aid, short_state, len(text), min_chars)
           transition_job_state([aid], short_state)
           return False
       classification = _classify_jd(text)
       if classification != "ok":
           error_state = _JD_ERROR_STATES[classification]
           # Save the text so the bad capture is inspectable in the DB
           save_job_data(aid, {jd_key: text})
           _log.warning("%s -> %s [JD classified %r]", aid, error_state, classification)
           transition_job_state([aid], error_state)
           return False
       save_job_data(aid, {jd_key: text})
       # Write back into in-memory dict so coat-check is a true no-op if called after this
       if not isinstance(job.get("job_data"), dict):
           job["job_data"] = {}
       job["job_data"][jd_key] = text
       transition_job_state([aid], pass_state)
       return True
   ```

   Check order, saves, and the in-memory write-back are byte-for-byte the semantics of today's
   inline block. Only the log lines change shape (`who -> dest [why]` warnings, no Style-D).

4. In `src/core/gazer.py`, `fetch_jd_batch`:
   - Delete these four lines (they move into the helper or become unused):
     `    cfg = TRACKER_CONFIG`,
     `    jd_key = cfg.get("job_data_keys", {}).get("job_description", "job_description")`,
     `    min_chars = cfg.get("jd_min_chars", 200)`,
     and inside `_scrape_one`, `        title = job.get("job_title", aid)`.
   - Inside `_scrape_one`, replace **everything from** the line
     `        text = collapse_consecutive_blank_lines(text)` **through** the line
     `        passed += 1` (the last line of `_scrape_one`, just before the blank line and
     `    await asyncio.gather(`) with:

     ```python
             _log.debug(
                 "Calling JD gates: [astral_job_id=%s short_state=%s pass_state=%s text=%s]",
                 aid, fail_state, pass_state, text,
             )
             gated = _apply_jd_gates(job, text, short_state=fail_state, pass_state=pass_state)
             _log.debug("Response from JD gates: %s", gated)
             if gated:
                 passed += 1
             else:
                 failed += 1
     ```

     Nothing else in `fetch_jd_batch` changes: the connectivity guard, the no-`job_link` branch,
     the `get_visible_text` try/except, the batch-start / summary Style-D lines, the `gather`, and
     the return shape all stay.

5. In `src/core/gazer.py`, add the runner **directly after** `fetch_jd_batch` (after its
   `return {"passed": passed, "failed": failed, "total": len(jobs)}`, before
   `def _website_content_is_recorded(`), two blank lines on each side:

   ```python
   async def fetch_relative_jd_batch(batch_id: str, jobs: List[Dict[str, Any]]) -> Dict[str, int]:
       """Click-through JD fetch for RELATIVE_JOB_LINK jobs (AST-2025).

       Per claimed job: Telescope opens company job_site, clicks the <a> whose href equals the
       stored relative job_link, returns (final_url, text). The resolved absolute URL replaces
       job_link, then the same JD gates as fetch_jd_batch decide the state. Click / Telescope
       failure -> fail_state with job_link left relative. Processes only `jobs` (dispatcher
       claimed and releases them). Returns {"passed": N, "failed": N, "total": N}.
       """
       if not await check_connectivity():
           raise ConnectionError(
               f"fetch_relative_jd_batch: no internet connectivity, aborting batch {batch_id} ({len(jobs)} jobs)"
           )
       cfg = GAZER_CONFIG["fetch_relative_jd"]
       pass_state = cfg["pass_state"]
       fail_state = cfg["fail_state"]
       # Empty / too-short text after a successful click: same JD_SCRAPE_FAIL as fetch_jd.
       short_state = GAZER_CONFIG["fetch_jd"]["fail_state"]
       passed = failed = 0

       async def _fetch_one(job: Dict[str, Any]) -> None:
           nonlocal passed, failed
           aid = job.get("astral_job_id", "")
           job_site = (job.get("job_site") or "").strip()
           href = (job.get("job_link") or "").strip()
           if not job_site or not href:
               _log.warning("%s -> %s [missing job_site %r or job_link %r]", aid, fail_state, job_site, href)
               transition_job_state([aid], fail_state)
               failed += 1
               return
           try:
               final_url, text = await click_through_visible_text(job_site, href)
           except Exception as e:  # noqa: BLE001 — every Telescope/client failure routes to fail_state (AST-2022 §5)
               if isinstance(e, PlaywrightInfraError) and e.failure_class == TELESCOPE_CLICK_TARGET_MISSING:
                   _log.warning("%s -> %s [click target missing: href=%r list_url=%s]", aid, fail_state, href, job_site)
               else:
                   _log.exception(
                       "%s -> %s [click-through failed: href=%r list_url=%s]\n  %s: %s\n  Continuing to the next job",
                       aid, fail_state, href, job_site, type(e).__name__, e,
                   )
               transition_job_state([aid], fail_state)
               failed += 1
               return
           if not final_url.startswith(("http://", "https://")):
               _log.warning("%s -> %s [click-through returned non-http final_url %r]", aid, fail_state, final_url)
               transition_job_state([aid], fail_state)
               failed += 1
               return
           _log.debug("Calling persist_http_job_link: [astral_job_id=%s job_link=%s]", aid, final_url)
           persist_http_job_link(aid, final_url)
           _log.debug(
               "Calling JD gates: [astral_job_id=%s short_state=%s pass_state=%s text=%s]",
               aid, short_state, pass_state, text,
           )
           gated = _apply_jd_gates(job, text, short_state=short_state, pass_state=pass_state)
           _log.debug("Response from JD gates: %s", gated)
           if gated:
               _log.info("%s | job %s: %s (batch: %s)", aid, "relative link fetched", pass_state, batch_id)
               passed += 1
           else:
               failed += 1

       _log.debug("Beginning fetch_relative_jd loop on %s items", len(jobs))
       await asyncio.gather(*[_fetch_one(j) for j in jobs], return_exceptions=False)
       _log.debug("End fetch_relative_jd loop after %s items", passed + failed)
       return {"passed": passed, "failed": failed, "total": len(jobs)}
   ```

   ⚠️ **Decision:** the `# noqa: BLE001` is the one pre-approved suppression. Ruff flags the
   catch-all because only one branch calls `logger.exception`. Splitting into two `except`
   clauses would duplicate the transition / count / return block. `click_through_visible_text`
   logs its own `Calling` / `Response from` debug joints (AST-2023), so the runner does not repeat
   them. No `Response from persist_http_job_link` line because it returns `None`.

6. Compile + lint `src/core/gazer.py` (see Notes). Then confirm AC 5's grep:
   `rg -n '_apply_jd_gates' src/core/gazer.py` prints exactly 3 lines (the `def` line, the call in
   `fetch_jd_batch`, the call in `fetch_relative_jd_batch`). Also confirm
   `rg -n '_prune_jd\(|_classify_jd\(|min_chars' src/core/gazer.py` hits only inside `_prune_jd` /
   `_classify_jd` / `_apply_jd_gates` and the existing contact / roster callers, and never inside
   `fetch_jd_batch` or `fetch_relative_jd_batch`.

7. Stubbed runner verify (AC 4). Must print `ok`:

   ```bash
   ASTRAL_DB_DIR=$(mktemp -d) ~/astral/.venv/bin/python - <<'EOF'
   import asyncio
   from unittest.mock import AsyncMock, MagicMock, patch
   import src.core.gazer as g
   from src.external.telescope import PlaywrightInfraError, TELESCOPE_CLICK_TARGET_MISSING

   TEXT = "role summary\n" + ("responsibilities include building reliable systems " * 40)
   DEST = "https://co.example/jobs/1"

   async def fake_click(list_url, href):
       if href == "/jobs/miss":
           raise PlaywrightInfraError(TELESCOPE_CLICK_TARGET_MISSING, "no anchor")
       return DEST, TEXT

   for verdict, want in (("ok", "JD_READY"), ("bot", "BOT_BLOCKED"), ("closed", "JD_SCRAPE_FAIL_CLOSED")):
       jobs = [
           {"astral_job_id": "j-hit", "job_site": "https://co.example/jobs", "job_link": "/jobs/1", "job_title": "Eng"},
           {"astral_job_id": "j-miss", "job_site": "https://co.example/jobs", "job_link": "/jobs/miss", "job_title": "Eng"},
       ]
       tr, link, save = MagicMock(), MagicMock(), MagicMock()
       with patch.object(g, "check_connectivity", AsyncMock(return_value=True)), \
            patch.object(g, "click_through_visible_text", fake_click), \
            patch.object(g, "transition_job_state", tr), \
            patch.object(g, "persist_http_job_link", link), \
            patch.object(g, "save_job_data", save), \
            patch.object(g, "_classify_jd", MagicMock(return_value=verdict)):
           out = asyncio.run(g.fetch_relative_jd_batch("b-2025", jobs))
       assert out == {"passed": int(verdict == "ok"), "failed": 2 - int(verdict == "ok"), "total": 2}, out
       moves = {c.args[0][0]: c.args[1] for c in tr.call_args_list}
       assert moves == {"j-hit": want, "j-miss": "RELATIVE_LINK_FAIL"}, moves
       link.assert_called_once_with("j-hit", DEST)  # resolved for every destination; never for the miss
       if verdict == "ok":
           assert save.call_args.args == ("j-hit", {"job_description": jobs[0]["job_data"]["job_description"]})
   print("ok")
   EOF
   ```

8. Commit: `code(AST-2025): shared JD gates + fetch_relative_jd_batch click-through runner`.
   Publish per build-child (`git push origin HEAD:sub/AST-2022/AST-2025-relative-link-runner`).

---

## Stage 2: Qualify routing + dispatch branch (`src/core/consult.py`)

**Done when:** `rg -n 'raise InvalidJobLinkError' src/core/consult.py` returns exactly one hit,
directly under `if not job_link:`. A passing qualify response with `job_link: "/jobs/123"` lands
the job in `RELATIVE_JOB_LINK` with that link. The job dispatch router sends `fetch_relative_jd`
to `gazer.fetch_relative_jd_batch`.

1. In `src/core/consult.py`, change the `InvalidJobLinkError` docstring from
   `"""Model returned an empty or non-absolute job_link for a listing."""` to
   `"""Model returned an empty job_link for a passing listing (relative links route to RELATIVE_JOB_LINK, AST-2025)."""`.

2. In `src/core/consult.py`, inside `qualify_job_listings` → `def process(input_job, response_job, cfg):`,
   replace this exact block:

   ```python
           job_link = (response_job.get("job_link") or "").strip()
           if not job_link.startswith("http"):
               kind = "empty" if not job_link else "relative"
               logger.debug("%s job_link: %r", kind, job_link)
               raise InvalidJobLinkError(f"{kind} job_link: {job_link}")
           if not tracker.initialize_job(aid, input_job["company"], response_job):
               _warn_job(aid, cfg["fail_state"], "identity collision")
               return cfg["fail_state"]
           _save_joblist_result()
           _transition_job_state_for_task(task_key, [aid], to_state, score)
   ```

   with:

   ```python
           job_link = (response_job.get("job_link") or "").strip()
           if not job_link:
               logger.debug("empty job_link: %r", job_link)
               raise InvalidJobLinkError(f"empty job_link: {job_link}")
           if not tracker.initialize_job(aid, input_job["company"], response_job):
               _warn_job(aid, cfg["fail_state"], "identity collision")
               return cfg["fail_state"]
           _save_joblist_result()
           if not job_link.startswith("http"):
               # Relative link kept as-is; fetch_relative_jd clicks it on the company job_site.
               to_state = cfg["relative_link_state"]
           _transition_job_state_for_task(task_key, [aid], to_state, score)
   ```

   The two lines that follow (`_job_consult_info(aid, to_state)` and `return to_state`) are
   unchanged and now emit the entity info line with `RELATIVE_JOB_LINK` for relative links.

   ⚠️ **Decision:** the `startswith("http")` test is the same one used today, so the
   absolute-link path is untouched (`PASSED_JOBLIST`). The empty-link message stays
   `"empty job_link: "` byte-for-byte (pinned by `TestAst1895InvalidJobLinkError`). The relative
   job runs the same `initialize_job` (stores `response_job["job_link"]` as-is) and
   `_save_joblist_result` as an absolute pass. Only the destination differs. `cfg` is
   `TASK_CONFIG["qualify_job_listings"]` (`_consult_orchestration`), where AST-2024 put
   `relative_link_state`.

3. In `src/core/consult.py`, job dispatch router: directly after the `fetch_jd` branch

   ```python
       if task_key == "fetch_jd":
           from src.core.gazer import fetch_jd_batch
           r = await _debug_await(
               "gazer.fetch_jd_batch",
               f"batch_id={batch_id}, n={len(entities)}",
               fetch_jd_batch(batch_id, entities, debug=debug),
           )
   ```

   and before `    elif task_key == "fetch_culture_pages":`, insert:

   ```python
       elif task_key == "fetch_relative_jd":
           from src.core.gazer import fetch_relative_jd_batch
           r = await _debug_await(
               "gazer.fetch_relative_jd_batch",
               f"batch_id={batch_id}, n={len(entities)}",
               fetch_relative_jd_batch(batch_id, entities),
           )
   ```

   The existing tail normalizes `r` (`passed` / `failed` / `total`) into the dispatch summary, so
   nothing else changes. Use the literal `"fetch_relative_jd"`, the key AST-2024 landed (its
   Resolution confirms Radia's default: keep `fetch_relative_jd`).

4. Compile + lint `src/core/consult.py` (see Notes). Verify, each must hold:
   - `rg -n 'raise InvalidJobLinkError' src/core/consult.py` gives exactly 1 line, and the line
     directly above it in the file is `if not job_link:` (plus the `logger.debug` line between).
   - `rg -n '"fetch_relative_jd"' src/core/consult.py` gives exactly 1 line (the router `elif`).
   - Import check:
     `ASTRAL_DB_DIR=$(mktemp -d) ~/astral/.venv/bin/python -c "import src.core.consult, src.core.gazer"` exits 0.
   - Run the Notes pytest command and record pass/fail counts vs the pre-change baseline in the
     build Review stub. Name any new failure other than the expected `TestAst1895` relative
     assertion. Do not edit tests.

5. Commit: `code(AST-2025): qualify routes relative job_link to RELATIVE_JOB_LINK; dispatch fetch_relative_jd`.
   Publish per build-child.

---

## Acceptance trace

| Ticket AC | Covered by |
|-----------|-----------|
| 2. Qualify keeps relative links / blank still fails | Stage 2 step 2 (relative → `cfg["relative_link_state"]` after `initialize_job`; empty → `InvalidJobLinkError` → batch fail destination via the existing `process_fn` exception path) |
| 3. Exactly one `raise InvalidJobLinkError`, under empty-link condition | Stage 2 step 2; verified Stage 2 step 4 |
| 4. Runner outcomes (ok → `JD_READY` + JD + resolved link; blocked → `BOT_BLOCKED`; closed → `JD_SCRAPE_FAIL_CLOSED`; click miss → `RELATIVE_LINK_FAIL`, link relative) | Stage 1 steps 3–5; verified Stage 1 step 7 |
| 5. Shared gates, not copied | Stage 1 steps 3–4 (`_apply_jd_gates`); verified Stage 1 step 6 |
| 6. Dispatch binding / claim only `RELATIVE_JOB_LINK` / `batch_id` NULL after | Picker meta and `job` / `RELATIVE_JOB_LINK` pair landed in AST-2024. Stage 2 step 3 wires the runner. Claim by that pair and `clear_job_batch` in `finally` are the dispatcher's generic job path, and the runner touches only the handed entities. End-to-end manual run is UAT (Telescope redeploy per AST-2023 Ops). |

Canon trace: `patt.entity.batch-processing` / `astral.batch.claim-process-release`: no
claim or select-by-state in the runner; it processes the dispatcher's batch only.
`stat.logging.debug`: ungated `Beginning`/`End` loop and `Calling`/`Response from` joints, no
truncation, no new `debug=`. `stat.logging.info.entity`: `aid | job relative link fetched:
JD_READY (batch: …)` per success, and qualify's existing `_job_consult_info` for
`RELATIVE_JOB_LINK`. `stat.logging.warning`: one `who -> dest [why]` per configured miss.
`stat.logging.error`: one `logger.exception` with facts and next step for unexpected
click-through throws.

## Estimate

Confirm Chuckles estimate: 3 — agree


## Joan validate

[plan-rubric]
**Ticket:** AST-2025
**Overall:** APPROVED
**Corpus:** 2344ae3265b15125a8f4a655946fcfe66b3e1def
**Publish ref:** `sub/AST-2022/AST-2025-relative-link-runner` @ `ef11e798c`

## Canon scores

patt.entity.batch-processing | A | | Runner processes only dispatcher-handed `jobs`; no claim/release or select-by-state in `gazer.py`
astral.batch.claim-process-release | A | | Claim/release stays dispatcher + tracker; `fetch_relative_jd_batch` documents that contract
stat.logging.debug | B | | `_apply_jd_gates` adds Calling/Response joints; new runner has begin/end loop; `fetch_jd_batch` gate path drops per-job `debug_index` on outcomes (Style D retained on scrape errors and batch start)
stat.logging.info.entity | A | | Qualify `_job_consult_info` on `RELATIVE_JOB_LINK`; runner success line matches `id | job event: detail (batch: …)`
stat.logging.warning | A | | `_apply_jd_gates` and click-miss use `who -> dest [why]`; configured misses avoid `logger.exception`
stat.logging.error | A | | Non–click-miss Telescope failures get one `logger.exception` with facts and “Continuing to the next job”

## Traceability

AC2 → Stage 2 step 2; AC3 → Stage 2 steps 2 + 4; AC4 → Stage 1 steps 3–5 + step 7 stub; AC5 → Stage 1 steps 3–4 + step 6 grep; AC6 → Stage 2 step 3 + AST-2024 registration (plan Acceptance trace); parent AC1, AC4 (Telescope), AC7 partial meta, AC8 → N/A or sibling/UAT per Boundaries.

### discuss — Build depends on merged #1/#2 surfaces

- **Location:** Plan header Depends on AST-2023/AST-2024 via `origin/ftr/AST-2022-relative-job-link`.
- **Finding:** `relative_link_state`, `fetch_relative_jd`, `click_through_visible_text`, and `TELESCOPE_CLICK_TARGET_MISSING` must exist on the integration ref before this child builds cleanly.
- **Recommendation:** Chuckles keeps ftr/sub merge order per epic; not a plan rewrite.

### discuss — `fetch_jd_batch(debug=True)` gate observability

- **Location:** Stage 1 step 4 (`_apply_jd_gates` replaces inline gate block including former `debug_index` outcomes).
- **Finding:** Debug-mode operators lose per-job Style-D outcome lines for empty/short/classified gates; scrape failures still use `debug_index`.
- **Recommendation:** Accept as statute-aligned warning shape unless Susan wants Style-D restored around the helper calls.

### acceptable — No `## Self-assessment` block

- **Location:** Plan structure (Estimate confirm only).
- **Finding:** R6 self-assessment checklist has nothing formal to grade; complexity is in staged literals and verify scripts.
- **Recommendation:** Optional self-assessment; not blocking.

### acceptable — AC6 end-to-end manual claim test deferred

- **Location:** Acceptance trace row for AC6.
- **Finding:** Picker pair and `clear_job_batch` behavior are split across AST-2024 and generic dispatcher; plan correctly scopes UAT after Telescope redeploy.
- **Recommendation:** None for AST-2025 plan approval.

**R6 (summary):** Definition fidelity for parent child #3 (qualify route, runner, shared JD gates, dispatch branch). Scope limited to `gazer.py` and `consult.py`. `to_state` overwrite for relative links only on pass path after `initialize_job`. Task key `fetch_relative_jd` matches AST-2024. No scope creep into config/tests. No `fix-now` findings.

context_tokens≈68000

## Review

- **Branch:** `sub/AST-2022/AST-2025-relative-link-runner`
- **Stage 1:** `73107d5c8` — `_apply_jd_gates` shared helper, `fetch_jd_batch` delegates to it, new `fetch_relative_jd_batch`
- **Stage 2:** `7120ce486` — qualify routes non-empty non-http `job_link` to `RELATIVE_JOB_LINK` (only empty raises `InvalidJobLinkError`), router `fetch_relative_jd` branch
- **Build notes:**
  - Deviation (plan self-contradiction): the plan's literal signatures used `Dict` / `List`, which added 5 new ruff `UP006` findings against the plan's "no new findings" rule. The three new signatures (`_apply_jd_gates`, `fetch_relative_jd_batch`, `_fetch_one`) use builtin `dict` / `list` instead. No behavior change. Ruff totals unchanged vs baseline (gazer 62, consult 218); the one `# noqa: BLE001` is the pre-approved suppression.
  - Stage 1 step 7 stubbed verify prints `ok` (ok → `JD_READY`, bot → `BOT_BLOCKED`, closed → `JD_SCRAPE_FAIL_CLOSED`, click miss → `RELATIVE_LINK_FAIL`; `persist_http_job_link` only on reached destinations).
  - `pytest tests/component/core/test_gazer.py tests/component/core/test_consult.py`: baseline 29 failed / 387 passed; after 31 failed / 385 passed. The same 29 pre-existing failures plus two by-design breaks for Betty (both assert a passing `/relative` link fails, which AC 2 reverses; their empty-link halves still hold):
    `test_consult.py::TestAst1895InvalidJobLinkError::test_empty_and_relative_job_link_fail_reason_names_error` and
    `test_consult.py::TestQualifyJobListings::test_fails_short_title_and_relative_link`.
  - Verify commands need `~/astral/.venv/bin/python` (system `python3` lacks `asyncpg`).
