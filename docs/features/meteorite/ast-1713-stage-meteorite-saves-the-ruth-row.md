# AST-1713 — stage_meteorite saves the Ruth row

**Linear:** [AST-1713](https://linear.app/astralcareermatch/issue/AST-1713/stage-meteorite-saves-the-ruth-row-rework-meteorite-email)
**Parent:** [AST-1711](https://linear.app/astralcareermatch/issue/AST-1711/rework-meteorite-email)
**Publish ref:** `sub/AST-1711/AST-1713-stage-meteorite-saves-the-ruth-row`

`stage_meteorite` sends any text blob to Ruth through `agent.do_task` (`task_key` `stage_meteorite`) and inserts the meteorite row in the same pass: `SCRAPE_LINK`, `READY`, `NOT_A_JOB`, or `NEW_EMAIL_ERROR`. Consult is not on that path. The candidate-facing source string stays on `link` (http job link, or the email-and-date breadcrumb when there is no job link). Title, employer, description text, and electronic contact are stored on that row. `contact_land_meteorite` keeps the dict it already returns.

## Scope gate

Ticket **## Scope** only. Files in Stages: `src/data/database.py`, `src/core/meteorite.py`, `src/core/consult.py`.

- Database kind: add `job_title` and `employer_name` (migrate-if-missing, same pattern as `electronic_contact`); `INSERT` writes both from the row; state written is the row's state, not hardcoded `"NEW"`.
- Meteorite kind: `stage_meteorite` calls the agent and saves those four states; ingest calls that save instead of consult; `check_inbox` is not the classify/save runner; retention reads `METEORITE_STATES_RETENTION` (set includes `NOT_A_JOB` after AST-1712); `enrich_meteorite_land_packet` plus `_hold_log_batch` and `_resolve_company_job_id` move here; `land_meteorite` drops the consult import.
- Consult kind: delete `invoke_stage_meteorite` and `enrich_meteorite_land_packet`. `_hold_log_batch` moves (its only other caller is the invoke this slice deletes). `_resolve_company_job_id` moves; `qualify_meteorite` keeps calling it via a late import from `meteorite.py`. `meteorite.py` does not import consult.

**Out of scope**

- `src/utils/config.py`, `data/admin/agent_task.json`, `src/core/agent.py` — AST-1712. Do not edit. Do not retarget scrape or land `SCRAPE_ERROR` / `ERROR` writes in `run_scrape_meteorite`, `run_land_meteorite`, or `run_stage_meteorite`.
- Mailbox task key, `inbox.check_email`, dispatcher mailbox branch, `api_admin.py` — sibling #3. Do not edit `src/core/inbox.py`, `src/core/dispatcher.py`, or `src/ui/api/api_admin.py`.
- Do not add a dispatch trigger, claim state, or `_RETRY` sibling for `NOT_A_JOB` or `NEW_EMAIL_ERROR` (`patt.task.dispatch-retry` does not apply to those two; scrape retry stays on `SCRAPE_ERROR` under AST-1712).

**Depends on AST-1712.** After `sync-child.sh`, this must succeed before Stage 2:

```python
from src.utils.config import METEORITE_STATES, METEORITE_STATES_RETENTION, STAGE_METEORITE_CONFIG
for key in ("SCRAPE_LINK", "READY", "NOT_A_JOB", "NEW_EMAIL_ERROR"):
    assert key in METEORITE_STATES
assert "NOT_A_JOB" in METEORITE_STATES_RETENTION["purge_states"]
assert "not_job_content" in STAGE_METEORITE_CONFIG["skip_outcomes"]
assert "not_original_posting" in STAGE_METEORITE_CONFIG["skip_outcomes"]
```

If that raises: stop. Comment parent AST-1711. Do not invent the registry in `config.py`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | `job_title` and `employer_name` columns; insert binds caller state plus those fields | data |
| `src/core/meteorite.py` | Stage classify + save; ingest calls it; move land enrich and two helpers; retention uses the registry set; no consult import | core |
| `src/core/consult.py` | Delete stage invoke and land enrich; `qualify_meteorite` late-imports `_resolve_company_job_id` | core |

## Stage 1: Meteorite columns and caller-state insert

**Done when:** `insert_meteorite_rows` binds `row["state"]` and does not contain the literal `"NEW"` in the function (the next 40 lines after `def insert_meteorite_rows`). New and migrated databases have `job_title TEXT` and `employer_name TEXT`. Existing paste and classify-map inserts still pass `state` `"NEW"` so behavior is unchanged. `python3 -m py_compile src/data/database.py src/core/meteorite.py` succeeds. No consult edits yet.

1. In the `meteorite` bullet of the `database.py` module header inventory, add `job_title` and `employer_name` to the column list (AST-1713; Ruth `stage_meteorite` response keys).

2. In `_UPDATE_METEORITE_ALLOWED`, add the strings `"job_title"` and `"employer_name"`.

3. In `_ensure_meteorite_schema`, add `job_title TEXT` and `employer_name TEXT` to the `CREATE TABLE meteorite` body, after `electronic_contact`. After the existing `electronic_contact` migrate-if-missing block, repeat that same `PRAGMA table_info` / `ALTER TABLE meteorite ADD COLUMN … TEXT` / duplicate-column `OperationalError` pattern once per new column name (`job_title`, then `employer_name`). Do not log.

4. In `insert_meteorite_rows`:
   - Change the docstring from inserting at state `NEW` to inserting at the `state` on each row.
   - Add `job_title, employer_name` to the `INSERT` column list (after `electronic_contact`'s config column, before `nag_count`).
   - Bind `row["state"]` where the SQL currently binds the literal `"NEW"`.
   - Bind `row.get("job_title")` and `row.get("employer_name")` (missing key → NULL). Do not reject a row that omits either key.
   - The function body must not contain the characters `"NEW"`.

5. In `src/core/meteorite.py` `_insert_paste_meteorite_parent`, add `"state": "NEW"` to the dict passed to `insert_meteorite_rows`. Leave the following `update_meteorite(mid, state="READY")` as it is.

6. In `_map_classify_jobs_to_meteorite_rows`, add `"state": "NEW"` to both dicts appended in the text branch and the url branch. Do not change link, content, or electronic-contact mapping in this stage.

⚠️ **Decision:** Stage 1 keeps today's `NEW` then later transition. Stage 2 replaces the state values. Splitting them keeps this commit's insert contract from changing classify outcomes before the save path exists.

## Stage 2: Ruth save path, ingest, land enrich move

**Done when:** `rg -n invoke_stage_meteorite src/` prints nothing. `rg -n consult src/core/meteorite.py` prints nothing. A skip-outcome classify inserts one `NOT_A_JOB` row. A url-scrape outcome inserts one `SCRAPE_LINK` row per job whose `link` is `http://` or `https://`. A text outcome for `source_kind` `email` inserts one `READY` row per job whose `link` is the email-and-date breadcrumb (not empty, not http). `land_meteorite` still calls `enrich_meteorite_land_packet` with the same arguments, and that function is defined in `meteorite.py`. `python3 -m py_compile src/core/meteorite.py src/core/consult.py` succeeds. `run_scrape_meteorite`, `run_land_meteorite`, and `run_stage_meteorite` are not edited.

Run the AST-1712 preflight in **Depends on** first. Stop if it fails.

### Move land enrich off consult

7. In `src/core/meteorite.py`, add `uuid_path_segment_from_url` to the existing `from src.utils.formatting import …` line.

8. Copy `consult._hold_log_batch` into `meteorite.py` unchanged (it already imports `log_batch_id`). Place it after `logger = get_logger(__name__)`.

9. Copy `consult._resolve_company_job_id` into `meteorite.py` unchanged, after `_hold_log_batch`. It uses `TRACKER_CONFIG` (already imported) and `uuid_path_segment_from_url`.

10. Copy `consult.enrich_meteorite_land_packet` into `meteorite.py` after `_land_scrap_body` (that helper already exists here; do not copy consult's duplicate). Keep the signature, the `@_with_log_debug` decorator, and the body, with two mechanical edits only:
    - `uuid4()` → `uuid.uuid4()` (`uuid` is already imported).
    - Immediately inside the function, before the first `do_task` use, `from src.core.agent import do_task`.
    Do not change arguments, warning text, or the returned dict.

11. In `land_meteorite`, delete the comment `Late-import: consult loads is_meteorite_company at module top.` and `from src.core.consult import enrich_meteorite_land_packet`. Leave the `Calling enrich_meteorite_land_packet` / `Response from enrich_meteorite_land_packet` debug lines and the `await enrich_meteorite_land_packet(...)` call. The name is now local.

12. In `src/core/consult.py`:
    - Delete `_hold_log_batch`, consult's `_land_scrap_body`, `enrich_meteorite_land_packet`, and `invoke_stage_meteorite`.
    - Delete the module-docstring sentences that name `enrich_meteorite_land_packet` and `invoke_stage_meteorite`.
    - At the first line of `qualify_meteorite`'s nested `process` function, add `from src.core.meteorite import _resolve_company_job_id`. Do not import it at module top (meteorite must not be imported while consult is still loading). The existing call stays.

⚠️ **Decision:** `qualify_meteorite` imports the helper from meteorite, not the other way around. A module-top import would cycle (`meteorite` → `tracker` is fine, but `consult` ↔ `meteorite` at import time is not). Late import inside `process` runs only when qualify runs.

### Classify and save inside stage_meteorite

13. Add `async def _classify_stage_blob(candidate_id, blob, *, source_kind, source_id, ctx, debug=False)` in `meteorite.py`. Body is the deleted `invoke_stage_meteorite` body, with `uuid4()` → `uuid.uuid4()` and `from src.core.agent import do_task` before the `do_task` call. Same return dict (`success`, `outcome`, `jobs`, `error`, `batch_id`, and `raw` on failure). Keep its `logger.warning` lines. Do not insert rows in this helper. Do not name the function `invoke_stage_meteorite`.

14. Rewrite `stage_meteorite` so it still returns only these keys: `outcome`, `stage_outcome`, `skipped`, `jobs`, `error`, `batch_id`. Do not add `inserted_ids`. `contact_land_meteorite` passes this dict through; do not edit `contact.py`.

    Keep the existing early returns for a blank `candidate_id` (`_warn_item`, `_err`, no insert).

    Require `source_kind` in `STAGE_METEORITE_CONFIG["source_ref_prefixes"]` and a non-empty `source_id` before any insert. If either fails: `_warn_item`, return `_err(...)`, no insert (those columns are `NOT NULL` and an unknown kind is not a stored source).

    If `get_candidate` misses: insert one `NEW_EMAIL_ERROR` row (step 16) with `error` `candidate not found: <cid>`, then return `_err` with that error. One `_warn_item` only (the one already in this function). Do not also warn inside the helper.

    Otherwise build `ctx` exactly as today (`dict(cand)`, `astral_candidate_id`) and `classify = await _classify_stage_blob(...)`. Debug `Calling _classify_stage_blob` / `Response from _classify_stage_blob` with `candidate_id`, `source_kind`, `source_id`.

15. State choice, using config partitions (do not hardcode the six outcome strings):

    - `classify["success"]` and `outcome` in `skip_outcomes`: one row, `state` `"NOT_A_JOB"`, `classify_outcome` that outcome, `content` / `link` / `job_title` / `employer_name` / electronic-contact all `None`, `error` `None`. Return `outcome` and `stage_outcome` set to that outcome, `skipped` `True`, `jobs` `[]`, `error` `None`, `batch_id` from classify.

    ⚠️ **Decision:** Both `not_job_content` and `not_original_posting` are `skip_outcomes`. Both save one `NOT_A_JOB` row. The helper already clears `jobs` on skip, so there is no breadcrumb input. AC4 does not require a link on `NOT_A_JOB`.

    - `classify["success"]` and `outcome` in `text_source_ref_outcomes` or `url_scrape_outcomes`: `row_dicts, map_err = _map_classify_jobs_to_meteorite_rows(...)` with `timezone_key=_candidate_contact_timezone(cid)`. On `map_err`: do not insert those job dicts; insert one `NEW_EMAIL_ERROR` (step 16) whose `error` is `map_err` and whose `classify_outcome` is the outcome; return `_err(map_err, batch_id=..., stage_outcome=outcome)`. On success: set each dict's `state` to `"READY"` when `outcome` is in `text_source_ref_outcomes`, else `"SCRAPE_LINK"`. Remove the Stage 1 `"state": "NEW"` from this function's output (edit the two append sites in `_map_classify_jobs_to_meteorite_rows` so they do not set `state`; the caller sets it). Add to each dict, from that job:
      - `job_title`: stripped string, or `None` if missing / not a string / empty
      - `employer_name`: same for key `employer_name`
      - `content`, `link`, electronic contact: leave the mapper's existing values (description text is `content`; contact is `_electronic_contact_from_job`)
      Insert that list (step 17). Return `outcome` and `stage_outcome` set to the classify outcome, `skipped` `False`, `jobs` the classify `jobs` list, `error` `None`, `batch_id` from classify.

    - Any other result (`success` false, outcome missing, outcome not in those three partitions): one `NEW_EMAIL_ERROR` row (step 16) with `error` `classify.get("error") or "stage failed"` and `classify_outcome` `classify.get("outcome")`. Return `_err` with that error, `batch_id`, and `stage_outcome=classify.get("outcome")`. If the helper already logged `logger.warning`, do not add a second warning.

16. `NEW_EMAIL_ERROR` row dict, always one row, never one per job:

    `candidate_id`, `source_kind`, `source_id`, `state` `"NEW_EMAIL_ERROR"`, `classify_outcome` as given, `content` `None`, `link` `None`, `job_title` `None`, `employer_name` `None`, electronic-contact column `None`, `error` the error string.

17. Insert helper used by steps 15–16. One `insert_meteorite_rows` call. Debug `Calling insert_meteorite_rows` / `Response from insert_meteorite_rows`. Then:

    ```python
    logger.debug("Beginning stage row info loop on %s items", len(ids))
    ```

    For each id and dict, `_meteorite_state_info(row_id, row["state"])` (no `from_state`; this is an insert). Then `End stage row info loop after %s items`. If `len(ids) != len(row_dicts)`: `_warn_item` and return `_err` with `insert_count_mismatch` (do not raise).

    Wrap the `do_task` path: `_classify_stage_blob` already returns a failed dict when `do_task` returns `success` false. If `_classify_stage_blob` or `insert_meteorite_rows` raises: `logger.exception` once, with `candidate_id`, `source_kind`, `source_id`, exception type, and next step `This blob is not being saved as a classified row`. Do not re-raise. If the throw was from classify (no row written yet) and kind/sid are valid, insert one `NEW_EMAIL_ERROR` with `error` `str(exc)`. If that insert also raises, `logger.exception` once more with next step `The error row was not inserted` and return `_err`. Do not `logger.warning(..., exc_info=True)`.

    `src/data/` does not log. No new debug lines in `database.py`.

### Ingest calls the save

18. In `ingest_candidate_email_message`, delete the consult import, the `invoke_stage_meteorite` call, the skip-outcome archive block that treats skip as "no rows", the `_map_classify_jobs_to_meteorite_rows` call, the `insert_meteorite_rows` call, the per-row `_meteorite_state_info(..., "NEW")` loop, and the electronic-contact soft-persist loop. Contact is written by the insert in step 15.

    After the blob is built, call `stage_meteorite(cid, blob, source_kind="email", source_id=mid, debug=debug)` with Calling/Response debug.

    - If `stage["error"]`: do not archive. Return the existing error `_row` (`counter` `"error"`). Do not add another warning if `stage_meteorite` already warned.
    - If `stage["skipped"]`: archive as the old skip path does (`archive_candidate_email`, `logger.exception` on archive failure with the same next-step shape already in this function). Return `_row(stage["outcome"], counter="passed")` on archive success.
    - Else: archive the same way. Return `_row(stage["outcome"], counter="passed", job_count=len(stage["jobs"]))`. Do not put `inserted_ids` on the dict (`api_inbox` does not read it).

    Dedup via `list_meteorites_by_source("email", mid)` stays. A prior `NEW_EMAIL_ERROR` or `NOT_A_JOB` row for that source id is "already ingested" and is not classified again.

⚠️ **Decision:** `check_inbox` stays. Dispatcher still calls it until sibling #3. It is not the classify/save runner: it only fetches and calls `ingest_candidate_email_message`, which calls `stage_meteorite`. Do not delete `check_inbox`. Do not edit `dispatcher.py`. Change its docstring to: fetch, then `stage_meteorite` via ingest, then archive. Not the Ruth classify runner.

### Retention reads the registry

19. In `run_meteorite_retention`, keep `purge_states = list(METEORITE_STATES_RETENTION["purge_states"])`. Do not hardcode `LANDED`. Do not drop the AST-1690 job-link keep (`astral_job_id` still pointing at a job row is not purged).

    Replace hardcoded `from_state="LANDED"` on the retention info lines with the row's `state`. While filtering, remember `str(row.get("state") or "")` per purge id and pass that as `from_state` on both `retention_kept` and `purged`.

    Docstring: purge states come from `METEORITE_STATES_RETENTION["purge_states"]` (includes `NOT_A_JOB` after AST-1712). Stale warn list stays `stale_list_states` (does not include `NOT_A_JOB`).

### Scrub the consult string

20. Rewrite the module docstring sentence that contains the word `consult` (`not Ruth consult hops` → `not Ruth classify hops`). Delete every remaining `consult` comment in this file. `rg -n consult src/core/meteorite.py` must print nothing. `rg -n invoke_stage_meteorite src/` must print nothing. If either still matches inside `meteorite.py` or `consult.py`, fix that hit. If it matches only in a file not in **Files Changed** (for example a comment in `agent.py`), do not edit that file; stop and comment parent AST-1711.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1713
**Overall:** APPROVED
**Corpus:** 751624d7ebdf9bc441fc3d08a51ae751ea8026af
**Publish ref:** 9aa2a45b3acda54d5a33a5c731ebbdc5523d4434

## Canon scores
patt.task.dispatch-retry | A
stat.logging.debug | A
stat.logging.error | A
stat.logging.info | A
stat.logging.info.entity | A
stat.logging.warning | A

## Traceability
AC2 → Stage 2 (delete `invoke_stage_meteorite`, move land enrich + helpers, no `consult` in `meteorite.py`); AC3 → Stage 1 (`insert_meteorite_rows` binds `row["state"]`, no `"NEW"` literal in function body); AC4 → Stage 2 steps 15–16 (`NOT_A_JOB` / `SCRAPE_LINK` / `READY` row saves with link rules)

## Findings
None.

context_tokens≈48000

[plan-rubric] PROCEED (Commit: 9aa2a45b3acda54d5a33a5c731ebbdc5523d4434) Ruth save path ready
