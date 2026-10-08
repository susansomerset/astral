# AST-2034 — Raw NEW meteorite insert + stage-hop classify

**Linear:** [AST-2034](https://linear.app/astralcareermatch/issue/AST-2034)
**Parent:** [AST-2032](https://linear.app/astralcareermatch/issue/AST-2032) — Let Estelle post a meteorite from Slack
**Publish ref:** `origin/sub/AST-2032/AST-2034-raw-new-meteorite-stage-classify`

This ticket covers the meteorite side of `@Estelle /add-job`. It adds a sync public entry, `insert_slack_meteorite`, that saves one Slack-sourced raw blob as a `meteorite` row at `NEW` with `classify_outcome` empty. It also teaches the `stage_meteorite` dispatch runner (`run_stage_meteorite`) to Ruth-classify unclassified `NEW` rows in the same pass. Job 1 is written onto the row, which then falls through to today's classified routing. Jobs 2..N are inserted as classified `NEW` siblings. Skip outcomes go to `NOT_A_JOB`, and classify/map failures go to `NEW_EMAIL_ERROR`. Rows that already carry `classify_outcome` route exactly as today. Ships parent AC8, AC9, AC10, plus the AC1/AC2 row shape when the entry is called directly. Slack parsing, the command registry, and replies belong to sibling AST-2035.

## Scope gate

The ticket's `## Scope` names one file: `src/core/meteorite.py`, with two described changes. The first is a new public insert entry. The second is a `run_stage_meteorite` branch that classifies via `_classify_stage_blob` "tied to the claim's entity batch id" and maps via `_map_classify_jobs_to_meteorite_rows`. Every row below is in that file. Changes to existing helpers are limited to the batch-id tie the Scope names.

- `insert_meteorite_rows` (`src/data/database.py`) does **not** persist `estelle_thread_ts`. The entry therefore stamps the anchor with `update_meteorite(..., estelle_thread_ts=...)`, which allows that field. No `database.py` change, matching the existing insert-then-update shape of `_insert_paste_meteorite_parent`.
- `STAGE_METEORITE_CONFIG["source_ref_prefixes"]` already contains `"slack"`. No `config.py` change (that file is owned by AST-2035).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/meteorite.py` | New public `insert_slack_meteorite`. `_classify_stage_blob` gains optional `batch_id` kwarg. New private `_classify_new_stage_row`. `run_stage_meteorite` replaces the "missing classify_outcome → SCRAPE_ERROR" arm with a classify step that falls through. Module docstring line. | core |

No other file is touched. Tests and the bible are Betty's (see **Test impact** below).

## Stage 1: Public Slack raw-insert entry

**Done when:** Calling `insert_slack_meteorite("cand-1", "http://www.dice.com/jobs/13234abcd", source_id="C1:1700000000.000100", thread_ts="1700000000.000100")` against a sqlite DB returns `{"ok": True, "meteorite_id": <int>, "error": None}`. The row has `state = NEW`, `source_kind = slack`, `classify_outcome` NULL, `content` = the URL, and `estelle_thread_ts` = the anchor. An empty payload returns `ok: False` and inserts nothing.

1. In `src/core/meteorite.py`, add this function directly **after** `_insert_stage_rows` (so it sits next to the other insert helpers and before `stage_meteorite`):

   ```python
   @_with_log_debug
   def insert_slack_meteorite(
       candidate_id: str,
       payload: str,
       *,
       source_id: str,
       thread_ts: Optional[str] = None,
       debug: bool = False,
   ) -> Dict[str, Any]:
       """Save one raw Slack blob at NEW, unclassified; Ruth classifies at the stage hop (AST-2034).

       Soft-fails: never raises into Contact. Returns {ok, meteorite_id, error}.
       """
   ```

   Body, in this order:
   1. `cid = (candidate_id or "").strip()`, `body = payload.strip() if isinstance(payload, str) else ""`, `sid = (source_id or "").strip()`, `anchor = (thread_ts or "").strip()`.
   2. Validation, first miss wins. Each miss calls `_warn_item(cid or "insert_slack_meteorite", <why>, "This Slack blob is not being saved")` and returns `{"ok": False, "meteorite_id": None, "error": <why>}`:
      - `not cid` → why `"candidate_id is required"`
      - `not body` → why `"payload is required"`
      - `not sid` → why `"source_id is required"`
   3. Build a single row dict: `{"candidate_id": cid, "source_kind": "slack", "source_id": sid, "state": "NEW", "content": body, "link": None, "classify_outcome": None}`.
   4. `try: ids, mismatch = _insert_stage_rows([row])`. `_insert_stage_rows` already emits the debug Calling/Response lines and the `meteorite state NEW` entity info line (stat.logging.info.entity, parent AC12's meteorite line). On `except Exception as exc`: `logger.exception("%s | insert_slack_meteorite %s\n  %s: %s\n  This Slack blob is not being saved", cid, sid, type(exc).__name__, exc)` and return `{"ok": False, "meteorite_id": None, "error": str(exc)}`.
   5. If `mismatch` or `not ids`: `_warn_item(cid, mismatch or "insert returned no id", "This Slack blob is not being saved")` and return `ok: False` with that error.
   6. `mid = int(ids[0])`.
   7. If `anchor`: in a `try`, call `update_meteorite(mid, estelle_thread_ts=anchor)` wrapped in `logger.debug("Calling update_meteorite: [id=%s, estelle_thread_ts=%s]", mid, anchor)` / `logger.debug("Response from update_meteorite: ok")`. On `except Exception as exc`: `logger.exception("%s | meteorite %s estelle_thread_ts\n  %s: %s\n  The row is saved at NEW without its Slack thread anchor", cid, mid, type(exc).__name__, exc)`. Do **not** return failure.
   8. Return `{"ok": True, "meteorite_id": mid, "error": None}`.

   ⚠️ **Decision:** The entry is **sync**. `handle_slack_event` / `_handle_slack_event_body` in `src/core/contact.py` are sync and already `asyncio.run` their async calls, and this entry does only DB writes, so AST-2035's registry handler can call it directly.

   ⚠️ **Decision:** `content` is `payload.strip()`. Leading/trailing whitespace is dropped, and the interior (including newlines in a pasted JD) is kept verbatim. Removing the mention and command token and unwrapping Slack link markup are AST-2035's job before the call.

   ⚠️ **Decision:** A failed anchor stamp still returns `ok: True`. The row exists at `NEW` and will stage normally. Reporting failure would make Contact tell the candidate nothing was saved when it was. The anchor only matters for later BOT_BLOCKED thread lookups (`find_meteorite_for_estelle_thread`).

   ⚠️ **Decision:** Link vs text is **not** decided here. Ruth decides at the stage hop (parent Decision §1, option B).

2. In the module docstring at the top of `src/core/meteorite.py`, after the line `create_contact_meteorite (AST-1517 contact-task create) wraps scrape-or-text → create.`, add one line:
   `insert_slack_meteorite (AST-2034): raw Slack blob → NEW unclassified; run_stage_meteorite Ruth-classifies it.`

Commit: `code(AST-2034): stage 1 — insert_slack_meteorite raw NEW entry`

## Stage 2: Stage-hop classify for unclassified NEW rows

**Done when:** With `src.core.agent.do_task` patched, `run_stage_meteorite` on a claim holding unclassified `NEW` rows produces these results. A `link_list` row with one job goes to `SCRAPE_LINK` with `link` set. A `single_jd_no_link` row goes to `CHECK_UNIQUE`. `not_job_content` goes to `NOT_A_JOB`. A failed `do_task` leaves the row at `NEW_EMAIL_ERROR` with `error` set. A 3-job `multi_jd_inline` result routes the original and adds 2 classified `NEW` rows with the same `source_id`. `agent_data` rows from the classify step carry the claim's `entity_batch_id`. A row that already had `classify_outcome` gets zero `do_task` calls and routes as before.

1. **`_classify_stage_blob` batch tie.** In `src/core/meteorite.py`, `_classify_stage_blob` signature: add a keyword-only parameter `batch_id: Optional[str] = None` after `ctx` (before `debug`). Replace the line
   `batch_id = f"{task_key}-stage-{uuid.uuid4()}"`
   with
   `batch_id = (batch_id or "").strip() or f"{task_key}-stage-{uuid.uuid4()}"`
   and put the inline comment `# Dispatch hop passes its claim id so agent_data joins the claim (AST-2034); ingress callers mint.` above it. Nothing else in the function changes. `_hold_log_batch(batch_id, cid)` already makes this id the `log_batch_id` that `do_task` writes onto `agent_data` when no parent batch is set. Under the dispatcher, `log_batch_id` is already the claim id (`dispatcher.py` sets `log_batch_id.set(entity_batch_id)`), so both paths join the claim. The existing caller `stage_meteorite` does not pass `batch_id`, so its behavior is unchanged.

2. **New private helper.** Directly **above** `run_stage_meteorite` (after `_row_miss`), add:

   ```python
   async def _classify_new_stage_row(
       row: Dict[str, Any], *, batch_id: str, debug: bool = False
   ) -> Tuple[Optional[Dict[str, Any]], str]:
       """Ruth-classify one raw NEW row in place (AST-2034).

       Returns (routable_row, "") when job 1 was written onto the row, or
       (None, summary_key) when the row reached a terminal state here.
       """
   ```

   Body, in this order:
   1. `row_id = int(row["id"])`, `cid = str(row.get("candidate_id") or "").strip()`, `kind = (row.get("source_kind") or "").strip()`, `sid = (row.get("source_id") or "").strip()`, `blob = row.get("content") if isinstance(row.get("content"), str) else ""`.
   2. Define a local closure `_fail(error: str, outcome: Optional[str] = None) -> Tuple[None, str]` that:
      - calls `update_meteorite(row_id, state="NEW_EMAIL_ERROR", error=error, classify_outcome=outcome)`,
      - calls `_meteorite_state_info(row_id, "NEW_EMAIL_ERROR", from_state="NEW")`,
      - calls `_row_miss(row_id, cid, error, "This row is NEW_EMAIL_ERROR; reset to NEW to retry")`,
      - returns `(None, "total_errors")`.
   3. Candidate context (mirrors `stage_meteorite`): `cand = get_candidate(cid)`. If falsy, `return _fail(f"candidate not found: {cid}")`. Else `ctx = dict(cand) if isinstance(cand, dict) else {}` and `ctx["astral_candidate_id"] = cid`.
   4. Classify:
      ```python
      try:
          logger.debug(
              "Calling _classify_stage_blob: [meteorite_id=%s, source_kind=%s, batch_id=%s]",
              row_id, kind, batch_id,
          )
          classify = await _classify_stage_blob(
              cid, blob, source_kind=kind, source_id=sid, ctx=ctx,
              batch_id=batch_id, debug=debug,
          )
          logger.debug("Response from _classify_stage_blob: %s", classify)
      except Exception as exc:
          logger.exception(
              "%s | meteorite %s classify\n  %s: %s\n  This row is NEW_EMAIL_ERROR",
              cid, row_id, type(exc).__name__, exc,
          )
          update_meteorite(row_id, state="NEW_EMAIL_ERROR", error=str(exc))
          _meteorite_state_info(row_id, "NEW_EMAIL_ERROR", from_state="NEW")
          return None, "total_errors"
      ```
      (The `except` path does not call `_fail`, because `logger.exception` already carries the who/why/next line. `_fail` would log a duplicate warning.)
   5. `outcome = classify.get("outcome")`. If `not classify.get("success")`: `return _fail(classify.get("error") or "stage failed", outcome)`. This covers empty blob, invalid source_kind, `do_task` failure, and invalid outcome. `_classify_stage_blob` already logs its own warning for `do_task` failure and invalid outcome. That warning comes from the classify layer and `_fail`'s comes from the row layer. Both are kept, matching how `stage_meteorite` + `_classify_stage_blob` already double-report today.
   6. Skip outcomes: if `outcome in STAGE_METEORITE_CONFIG["skip_outcomes"]`:
      `update_meteorite(row_id, state="NOT_A_JOB", classify_outcome=outcome)`, `_meteorite_state_info(row_id, "NOT_A_JOB", from_state="NEW")`, `return None, "total_failed"`.
   7. Map:
      ```python
      jobs = [j for j in (classify.get("jobs") or []) if isinstance(j, dict)]
      mapped, map_err = _map_classify_jobs_to_meteorite_rows(
          outcome, jobs, candidate_id=cid, source_kind=kind, source_id=sid,
          timezone_key=_candidate_contact_timezone(cid), ingress_blob=blob,
      )
      if map_err or not mapped:
          return _fail(str(map_err or "classify produced no rows"), outcome)
      ```
   8. Carry Ruth's title/employer onto each mapped dict, same as `stage_meteorite`:
      `for m, job in zip(mapped, jobs): m["job_title"] = _stage_field(job, "job_title"); m["employer_name"] = _stage_field(job, "employer_name")`.
   9. Write job 1 onto the claimed row:
      ```python
      col = METEORITE_CONFIG["electronic_contact_column"]
      first = {k: mapped[0].get(k) for k in (
          "classify_outcome", "content", "link", "job_title", "employer_name", col,
      )}
      update_meteorite(row_id, **first)
      ```
      Inline comment above it: `# Row keeps NEW; the caller's classified branch picks the next state this pass.`
   10. Fan out jobs 2..N as classified `NEW` siblings with the same `source_kind` / `source_id` (`_map_classify_jobs_to_meteorite_rows` already sets both):
       ```python
       siblings = [{**m, "state": "NEW"} for m in mapped[1:]]
       if siblings:
           try:
               _ids, mismatch = _insert_stage_rows(siblings)
           except Exception as exc:
               logger.exception(
                   "%s | meteorite %s fan-out\n  %s: %s\n  The first posting still routes; %s sibling postings were not staged",
                   cid, row_id, type(exc).__name__, exc, len(siblings),
               )
           else:
               if mismatch:
                   _row_miss(row_id, cid, mismatch, "The first posting still routes; some sibling postings may be missing")
       ```
   11. `return {**row, **first}, ""`.

   ⚠️ **Decision:** Job 1's fields **overwrite** the row's raw `content` (for a URL outcome with no `jd_text`, `content` becomes NULL). The routed row then has exactly the shape a classified row from email ingest has, so the downstream scrape/unique/land hops see no new shape. The raw blob is still in the stage `agent_data` prompt (`CONTENT:` block) under the claim batch id.

   ⚠️ **Decision:** Siblings are inserted **after** job 1 is written. If the fan-out insert fails, the first posting still routes, the failure is logged once, and no summary counter changes, because counters are per claimed row and the claimed row did route. Siblings are inserted unclaimed at `NEW` with `classify_outcome` set, so the next `stage_meteorite` tick routes them through the unchanged classified branch.

   ⚠️ **Decision:** Siblings do **not** copy `estelle_thread_ts`. Scope says they share `source_kind` / `source_id` only.

   ⚠️ **Decision:** `NOT_A_JOB` counts as `total_failed` and `NEW_EMAIL_ERROR` as `total_errors`. This matches email ingest (skip → `failed`, AST-1742) and the runner's AST-1751 rule that ERROR arms bump `total_errors` only. `update_meteorite` does not enforce `prior_states`, and both target states are `prior_states: None` (insert-legal) in `METEORITE_STATES`. That is the transition the parent Pipeline flow defines.

3. **Wire into `run_stage_meteorite`.** In the row loop, replace this block exactly:

   ```python
                outcome = (row.get("classify_outcome") or "").strip()
                if not outcome:
                    update_meteorite(row_id, state="SCRAPE_ERROR", error="missing classify_outcome")
                    _row_miss(
                        row_id, cid, "missing classify_outcome", "This row is SCRAPE_ERROR",
                    )
                    # AST-1751: ERROR arms bump total_errors only — not total_failed.
                    summary["total_errors"] += 1
                    continue
   ```

   with:

   ```python
                outcome = (row.get("classify_outcome") or "").strip()
                if not outcome:
                    # AST-2034: raw NEW (e.g. Slack /add-job) — Ruth classifies, then fall through.
                    classified, miss_key = await _classify_new_stage_row(
                        row, batch_id=batch_id, debug=debug,
                    )
                    if classified is None:
                        summary[miss_key] += 1
                        continue
                    row = classified
                    outcome = (row.get("classify_outcome") or "").strip()
   ```

   Every branch below it (skip-on-row, url, text, unhandled) stays **byte-for-byte unchanged**. That is AC9: rows that already have `classify_outcome` never enter the new block and never call `do_task`. The claim/process/`clear_meteorite_batch` in `finally` shape is untouched (patt.entity.batch-processing / astral.batch.claim-process-release). Fan-out siblings are not claimed by this batch, so nothing extra needs releasing.

4. Update the `run_stage_meteorite` docstring to:
   `"""Dispatch runner: NEW → SCRAPE_LINK | CHECK_UNIQUE; unclassified NEW → Ruth classify first (AST-1560 / AST-1774 / AST-2034)."""`

5. Update the module docstring's first paragraph. Replace `rows (AST-1560 / AST-1774 / AST-1775) are table transition runners — not Ruth classify hops; dispatcher` with `rows (AST-1560 / AST-1774 / AST-1775) are table transition runners — stage Ruth-classifies only raw unclassified NEW rows (AST-2034); dispatcher`.

Commit: `code(AST-2034): stage 2 — stage hop Ruth-classifies unclassified NEW rows`

## Compile and lint (each stage, before commit)

`python -m py_compile src/core/meteorite.py` and the repo's configured linter on `src/core/meteorite.py` (`ruff check src/core/meteorite.py` if `ruff` is configured; otherwise whatever `build-child` §7 names). Both must be clean.

## Test impact (for Betty — engineer does not edit `tests/`)

- `tests/component/core/test_meteorite.py::...::test_missing_classify_outcome_errors_with_monitoring` (~line 1221) asserts the old unclassified-row → `SCRAPE_ERROR "missing classify_outcome"` arm. Parent AC8 names that exact outcome as a **Fail**, so this test is intentionally invalidated. It needs to become a classify-path test with `do_task` patched.
- New coverage targets: parent AC8 (five routing bullets), AC9 (existing classified fixtures and `do_task` call count 0), AC10 (`agent_data.batch_id == entity_batch_id` with `log_batch_id` unset in the test, and all rows' `batch_id` NULL after the run), plus direct `insert_slack_meteorite` row-shape checks for AC1/AC2.

## Execution contract

Execute stages in order and steps in order. Do not add files, helpers, or config. If a referenced line or signature has drifted from what is quoted above, stop and comment on the parent [AST-2032](https://linear.app/astralcareermatch/issue/AST-2032) in the `🛑 Stage N blocked:` format. Do not adapt silently.

## Estimate

Confirm Chuckles estimate: 5 — revise to 3 because it is one file reusing the existing classify, map, and insert helpers, with no schema, config, or API contract change. That is new behavior in one area.
