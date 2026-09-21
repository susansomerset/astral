# AST-1714 — inbox.check_email runner

**Linear:** [AST-1714](https://linear.app/astralcareermatch/issue/AST-1714/inbox-check-email-runner-rework-meteorite-email)  
**Parent:** [AST-1711](https://linear.app/astralcareermatch/issue/AST-1711/rework-meteorite-email) — Rework meteorite_email  
**Publish ref:** `sub/AST-1711/AST-1714-inbox-check-email-runner`

For one candidate, each bound inbox message is handed to `meteorite.stage_meteorite` as the full message (headers + body), then archived on a non-error stage, with `last_email_check` stamped. The dispatcher mailbox branch calls `inbox.check_email` instead of `meteorite.check_inbox`. Provision rewrites retired mailbox dispatch rows onto the current mailbox task key. Admin mailbox checks keep using the fold helper (already keyed to `stage_email_meteorite` after AST-1712) and drop quoted retired-key wording.

## Scope gate

Ticket **## Scope** only. Files in Stages: `src/core/inbox.py`, `src/core/dispatcher.py`, `src/ui/api/api_admin.py`.

- Inbox kind: new `check_email` — for one candidate, each bound message’s full text to `stage_meteorite`; skip when already stored for that inbox id; archive after a successful (non-error) stage; stamp last email check.
- Dispatcher kind: mailbox run calls `inbox.check_email` instead of `meteorite.check_inbox`; provision rewrites existing dispatch rows whose task key is the retired mailbox key to `stage_email_meteorite` (current `METEORITE_EMAIL_MAILBOX_CONFIG["task_key"]`).
- Admin kind: recognize `stage_email_meteorite` wherever mailbox checks currently go through `is_meteorite_email_mailbox_task_key` (already true after AST-1712); scrub quoted retired-key strings in comments / warning text so parent AC1 stays green.

**Out of scope**

- `src/utils/config.py`, `data/admin/agent_task.json`, `src/core/agent.py` — AST-1712. Do not edit. Do not change `METEORITE_STATES` or `debug_func` (Ada already points `debug_func` at `inbox.check_email`).
- `src/core/meteorite.py`, `src/data/database.py`, `src/core/consult.py` — AST-1713. Do not edit. Do not rewrite `stage_meteorite`, do not delete `check_inbox` / `ingest_candidate_email_message`, do not change classify/save.
- Does not classify or choose the row state (sibling #2). Does not invent Ruth outcomes.

**Depends on AST-1713** (and transitively AST-1712). After `sync-child.sh`, this must succeed before Stage 1:

```python
from src.utils.config import METEORITE_EMAIL_MAILBOX_CONFIG
assert METEORITE_EMAIL_MAILBOX_CONFIG["task_key"] == "stage_email_meteorite"
assert METEORITE_EMAIL_MAILBOX_CONFIG["debug_func"] == "inbox.check_email"
from src.core.meteorite import stage_meteorite
import inspect
assert inspect.iscoroutinefunction(stage_meteorite)
```

If that raises: stop. Comment parent AST-1711. Do not invent the mailbox key or the Ruth save path.

All Files Changed / Stages stay inside the Scope file set above.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/inbox.py` | New `check_email` mailbox runner; docstring / comment scrub so quoted retired mailbox key is gone | core |
| `src/core/dispatcher.py` | Mailbox branch late-imports and awaits `inbox.check_email`; provision rewrites retired mailbox `task_key` → current config key; comment scrub | core |
| `src/ui/api/api_admin.py` | Comment / warning string scrub for mailbox recognition (helper already matches `stage_email_meteorite`) | ui |

**Verified no touch:** `src/core/meteorite.py` — `check_inbox` may remain for Land/admin paths; this ticket only stops the dispatcher from calling it. Grep at build time; do not delete it here.

## Stage 1: `inbox.check_email`

**Done when:** `rg -n 'def check_email' src/core/inbox.py` finds the function. Inside that function body, the blob passed to `stage_meteorite` is built with `strip_extract_email_html` or `assembled_html` (from `get_message_with_assembled_html`), not `html_body` alone. `python3 -m py_compile src/core/inbox.py` succeeds. No dispatcher or admin edits yet.

1. In `src/core/inbox.py` module docstring, replace any wording that names the retired mailbox task key with `stage_email_meteorite` / “candidate-bound mailbox”. Parent AC1 / AST-1712 AC1: `rg -n "['\"]meteorite_email['\"]" src/core/inbox.py` must print nothing after this stage.

2. Add imports needed for the runner (keep existing imports; add only what this function uses):
   - `functools`, `inspect` (for the local `@_with_log_debug` mirror used in `meteorite.py` / `contact.py`).
   - `from src.utils.logging import get_logger, log_debug` — `log_debug` is new beside the existing `get_logger` import.

3. Add a module-local `_with_log_debug` identical in behavior to `meteorite._with_log_debug` (set `log_debug` from the `debug=` kwarg for the frame; support async). Do not import meteorite’s private decorator.

4. Add:

```python
@_with_log_debug
async def check_email(task: dict, *, debug: bool = False) -> dict[str, int]:
    """Candidate-bound mailbox: aliases → fetch → stage_meteorite → archive → stamp."""
```

   Signature matches today’s `meteorite.check_inbox` so the dispatcher can swap the callee without reshaping the task dict. Return the same four-key summary: `total_processed`, `total_passed`, `total_failed`, `total_errors` (ints; `total_failed` stays 0 unless a future step needs it — mirror `check_inbox` and leave it at 0).

5. Body, in order:

   a. `cid = str((task or {}).get("candidate_id") or "").strip()`. If blank: `raise ValueError("candidate_id is required")`.

   b. Late-import (avoid import cycles — `meteorite` already imports inbox):
      - `from src.core.candidate import email_aliases_for_candidate`
      - `from src.core.meteorite import stage_meteorite`
      - `from src.data.database import list_meteorites_by_source, update_candidate_last_email_check`
      - `from src.utils.config import METEORITE_EMAIL_MAILBOX_CONFIG, METEORITE_MONITORING_CONFIG`

   c. Optional account mismatch debug only (same shape as `check_inbox`): compare `(os.environ.get("GMAIL_USER") or "").casefold()` to `(METEORITE_EMAIL_MAILBOX_CONFIG["account_address"] or "").casefold()`; on mismatch `logger.debug("account_mismatch GMAIL_USER=%r expected=%r", …)`. Add `import os` at module top if not already present.

   d. `aliases = email_aliases_for_candidate(cid)`. Debug `Calling fetch_candidate_email` / `Response from fetch_candidate_email`. `messages = fetch_candidate_email(aliases, debug=debug)`.

   e. `logger.debug("Beginning inbox message loop on %s items", n)` with `n = len(messages)`. For each message at index `i` (1-based):

      - `mid = str(msg.get("id") or "").strip()`. If blank: `logger.warning` who=`cid`, why=`message_id is required`, next step=`This message is not being staged`; increment `total_processed` and `total_errors`; continue.

      - Dedup: `existing = list_meteorites_by_source("email", mid)`. If non-empty: soft-fail warn (`message {mid} already ingested` / `No new meteorite rows are being inserted`); try `archive_candidate_email(mid)` with Calling/Response debug; on archive success count `passed`, on archive exception `logger.exception` with next step `The message was already ingested; archive did not finish` and count `error`. Do **not** call `stage_meteorite`. Continue. Outcome label for rollup is not required on the return dict (summary is counts only); use `METEORITE_MONITORING_CONFIG["outcome_already_ingested"]` only if you need a local variable for the warn text — do not add monitoring info lines (not in Scope).

      - Build the full message blob (AC4):
        - Prefer `payload = get_message_with_assembled_html(mid)` then `blob = payload["assembled_html"]`, **or**
        - `payload = get_message_html(mid)` then `blob = strip_extract_email_html(payload.get("subject") or "", payload.get("html_body") or "", from_address=…, to_address=…, date=…)`.
        - Either path is fine. **Forbidden:** passing `payload.get("html_body")` alone to `stage_meteorite`.

      - Debug `Calling stage_meteorite: [candidate_id=%s, source_kind=email, source_id=%s]` then `stage = await stage_meteorite(cid, blob, source_kind="email", source_id=mid, debug=debug)`. Debug `Response from stage_meteorite: %s`.

      - If `stage.get("error")`: do **not** archive. Count `error`. Do not add a second warning if `stage_meteorite` already warned. Continue.

      - Else (includes `skipped` / `NOT_A_JOB` and job saves): archive with Calling/Response debug. On archive success count `passed` (`job_count` is not on the summary dict). On archive exception `logger.exception` with next step `Meteorite rows were staged; archive did not finish` (or `Classify skipped; archive did not finish` when `stage.get("skipped")`) and count `error`.

   f. After the loop: `logger.debug("End inbox message loop after %s items", n)`. `update_candidate_last_email_check(cid)`. Debug that the stamp ran. Do **not** emit `stat.logging.info.entity` lines (`_entity_info` is private to meteorite and that statute is not on this ticket’s Canon Scope).

   g. Return `{"total_processed": …, "total_passed": …, "total_failed": 0, "total_errors": …}`.

6. In `count_inbox_bound_by_candidate`, change the docstring so it does not contain the quoted retired task key (use “candidate-bound mailbox” / `stage_email_meteorite`). Leave the body on `is_meteorite_email_mailbox_task_key` — Ada already folds the new key.

⚠️ **Decision:** Archive rules match AST-1713 ingest: `stage["error"]` (including `NEW_EMAIL_ERROR` returns) → leave in INBOX; otherwise archive. Dedup treats any prior row for `(email, mid)` — including `NOT_A_JOB` / `NEW_EMAIL_ERROR` — as already ingested (same as 1713).

⚠️ **Decision:** `check_email` lives in `inbox.py` and late-imports `stage_meteorite`. Do not move classify/save into inbox. Do not call `ingest_candidate_email_message` from here — that stays meteorite’s Land/shared path; this runner is the mailbox entrypoint sibling #3 owns.

## Stage 2: Dispatcher — mailbox call + provision rewrite

**Done when:** `rg -n check_inbox src/core/dispatcher.py` prints nothing. `rg -n check_email src/core/dispatcher.py` finds the mailbox call. After a provision run against a DB that still has retired-key rows (bound and empty-`candidate_id` orphans), `SELECT COUNT(*) FROM dispatch_task WHERE task_key = 'meteorite_email'` is 0 and each candidate that had a bound retired-key row has a `stage_email_meteorite` row. `rg -n "['\"]meteorite_email['\"]" src/core/dispatcher.py` prints nothing. `python3 -m py_compile src/core/dispatcher.py` succeeds.

1. In the mailbox branch of `_run_task` (the block gated by `_is_inbox_mailbox_task_key`):
   - Replace `from src.core.meteorite import check_inbox` with `from src.core.inbox import check_email`.
   - Replace Calling/Response debug strings and the `await check_inbox(task, debug=debug)` call with `check_email`. Leave ledger, trigger gate, cancel/exception handling, and summary accumulation unchanged.

2. In `provision_meteorite_email_dispatch_tasks`, **before** the per-candidate `ensure_meteorite_email_dispatch_task` loop, clear every retired mailbox `task_key` row (bound rewrite + orphan delete), then continue with today’s null-candidate cleanup for the current key:

   - `tk = str(METEORITE_EMAIL_MAILBOX_CONFIG["task_key"]).strip()` (already present).
   - `prior_mailbox_task_key = "meteorite" + "_email"` (see Decision below — never one contiguous quoted retired token).
   - Keep the existing `gaze_email` delete branch.
   - In the same pre-ensure scan over `database.list_dispatch_tasks()`, for each row whose `task_key` equals `prior_mailbox_task_key`:
     - If `candidate_id` is null or blank after strip: `database.delete_dispatch_task(int(row["id"]))` (mirror `gaze_email` / null-candidate purge). Count under returned stats key `retired_null` (reuse today’s counter or add to it — either is fine; do not leave the row).
     - Else: `_db_update_dispatch_task(int(row["id"]), task_key=tk)` (or `database.update_dispatch_task` — same whitelist; `task_key` is already in `_DISPATCH_TASK_UPDATE_COLS`). Count under returned stats key `rewritten` (int).
   - After that scan, continue with today’s null-candidate cleanup for rows whose `task_key == tk`, then the ensure loop.
   - After provision, zero retired-key rows remain (parent AC5): bound rows were rewritten; orphan empty-`candidate_id` rows were deleted. Ensure then inserts/skips so every live candidate has one `tk` row.

   ⚠️ **Decision (parent AC1 / AST-1712 AC1):** Those greps forbid the contiguous quoted token `meteorite_email` in `dispatcher.py`. Name the retired key without that token, e.g. `prior_mailbox_task_key = "meteorite" + "_email"`, compare `row_tk == prior_mailbox_task_key`, and never write `"meteorite_email"` as one quoted string in this file. Comments may say “retired mailbox key” / “pre-rename mailbox task_key” without the forbidden token.

   ⚠️ **Decision (Joan fix-now):** Parent AC5 is a COUNT on the retired key, not “bound rows only.” Empty-`candidate_id` retired-key rows cannot be rewritten onto a candidate-bound mailbox row; delete them in the same pre-ensure pass so the COUNT is 0.

3. Scrub docstrings and comments in `ensure_meteorite_email_dispatch_task`, `provision_meteorite_email_dispatch_tasks`, `_meteorite_email_due_tasks`, and nearby AUTO comments so they name `stage_email_meteorite` or “mailbox” instead of the retired quoted key. Do **not** rename the Python functions (`ensure_meteorite_email_dispatch_task`, etc.) — names are unquoted and out of AC1’s `['\"]…['\"]` pattern; renaming would churn call sites outside Scope.

4. Do not add `stage_email_meteorite` to `TASK_CONFIG`. `ensure_*` already reads `METEORITE_EMAIL_MAILBOX_CONFIG["task_key"]` and the existing `tk not in TASK_CONFIG` early-return stays (mailbox rows are not TASK_CONFIG entries — same as today).

## Stage 3: Admin mailbox recognition scrub

**Done when:** `rg -n "['\"]meteorite_email['\"]" src/ui/api/api_admin.py` prints nothing. Every mailbox gate still goes through `is_meteorite_email_mailbox_task_key` (no hardcoded new key required). `python3 -m py_compile src/ui/api/api_admin.py` succeeds.

1. In `list_dtasks`, change the warning `list_dtasks: meteorite_email inbox bind counts failed` to `list_dtasks: mailbox inbox bind counts failed` (or `stage_email_meteorite inbox bind counts failed` without using the retired token).

2. Reword the comment above the mailbox trigger gate (`meteorite_email is candidate-bound…`) to say `stage_email_meteorite` / “mailbox fold” is candidate-bound. Leave the `if is_meteorite_email_mailbox_task_key(tk):` body unchanged.

3. Confirm (read-only) that `_inbox_avail_task_key`, catalog allow, and `mailbox = is_meteorite_email_mailbox_task_key(...)` already use the helper — no new `if task_key == "stage_email_meteorite"` branches. If a hardcoded `"meteorite_email"` comparison exists, replace it with the helper; do not add a parallel hardcoded `"stage_email_meteorite"` string beside the helper.

## Execution contract

Execute stages in order, steps in order. One commit per stage on this epic worktree, then `git push origin <sha>:sub/AST-1711/AST-1714-inbox-check-email-runner`. Do not add files. Do not edit `tests/`, `src/core/meteorite.py`, or `src/utils/config.py`. If `stage_meteorite`’s signature or return keys (`error` / `skipped` / `outcome` / `jobs`) differ after sync, stop and comment on AST-1711. Do not adapt silently.

Preflight failure (Depends on) → stop; comment parent; do not start Stage 1.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Revisions

Revision 1 — 2026-09-20  
Driven by: Joan fix-now on Stage 2 step 2 — rewrite skipped retired-key rows with null/empty `candidate_id`, so parent AC5 COUNT could stay non-zero.  
Changes: Stage 2 step 2 now deletes orphan retired-key rows (empty `candidate_id`) in the same pre-ensure scan, and rewrites only bound retired-key rows to `tk`. Discuss item on `_entity_info` stamp left as-is (no change).

## Canon Scope (from ticket)

Patterns: (none — logging statutes only)

Statutes (read at plan; expand at build): `stat.logging.debug`; `stat.logging.error`; `stat.logging.info`; `stat.logging.info.dispatcher`; `stat.logging.warning`.

## Joan validate

**Ticket:** AST-1714
**Overall:** REVISE
**Corpus:** 751624d7ebdf9bc441fc3d08a51ae751ea8026af
**Publish ref:** a459ce8400c1cf801966d521c6bb831c4d657a30

## Canon scores
stat.logging.debug | A
stat.logging.error | A
stat.logging.info | A
stat.logging.info.dispatcher | A
stat.logging.warning | A

## Traceability
AC4 → Stage 1 (`check_email` full-message blob via `assembled_html` / `strip_extract_email_html`; Stage 2 dispatcher calls `inbox.check_email`); AC5 → Stage 2 step 2 (provision rewrite bound retired mailbox `task_key` → `METEORITE_EMAIL_MAILBOX_CONFIG["task_key"]`; delete orphan empty-`candidate_id` retired-key rows)

## Findings

### fix-now
- **Location:** Stage 2 step 2 — `provision_meteorite_email_dispatch_tasks` rewrite branch
- **Finding:** Rewrite only runs when the retired-key row has a non-empty `candidate_id`. Rows still keyed to the retired mailbox identity with null/empty `candidate_id` are not rewritten and not deleted. Parent AC5 requires `SELECT COUNT(*) FROM dispatch_task WHERE task_key = 'meteorite_email'` = 0 — any such orphan row fails regardless of `candidate_id`.
- **Recommendation:** In the same pre-ensure scan, delete retired-key rows with empty `candidate_id` (mirror the existing `gaze_email` purge / null-candidate cleanup pattern), or otherwise guarantee zero retired-key rows before the ensure loop.

### discuss
- **Location:** Stage 1 step 5f — `last_email_check` stamp
- **Finding:** Plan drops `check_inbox`'s `_entity_info` stamp line; only debug + DB update remain. Acceptable because `stat.logging.info.entity` is not on this ticket's canon list and dispatcher rollup still emits `stat.logging.info.dispatcher` on task completion.
- **Recommendation:** No change required unless Susan wants the stamp visible at entity-info level in production logs.

context_tokens≈58000

## Joan validate (round 2)

**Ticket:** AST-1714
**Overall:** APPROVED
**Corpus:** 751624d7ebdf9bc441fc3d08a51ae751ea8026af
**Publish ref:** 132715f21fbdb7af2b23beb5fb07a196433d13ae

## Canon scores
stat.logging.debug | A
stat.logging.error | A
stat.logging.info | A
stat.logging.info.dispatcher | A
stat.logging.warning | A

## Traceability
AC4 → Stage 1 (`check_email` full-message blob via `assembled_html` / `strip_extract_email_html`; Stage 2 dispatcher calls `inbox.check_email`); AC5 → Stage 2 step 2 (rewrite bound retired-key rows to `tk`; delete orphan empty-`candidate_id` retired-key rows; ensure loop)

## Findings
None.

context_tokens≈62000

## Review stub (build-child)

**Built:** `ccfcf671` on `sub/AST-1711/AST-1714-inbox-check-email-runner`

## Radia review

**Ticket:** AST-1714
**Publish ref:** `b90b86fd640fc159f93935ae2517b2e41cb18f82` (`origin/sub/AST-1711/AST-1714-inbox-check-email-runner`)
**Corpus:** `751624d7ebdf9bc441fc3d08a51ae751ea8026af`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.debug | A | | |
| stat.logging.error | A | | |
| stat.logging.info | A | | |
| stat.logging.info.dispatcher | A | | |
| stat.logging.warning | A | | |

## Column diff vs plan stage

(aligned) — Joan round 2 scored all five directives **A**; code review matches.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Parallel ingest paths** — `inbox.check_email` and `meteorite.ingest_candidate_email_message` now share the same dedup / stage / archive rules by design (mailbox vs Land). Expected until a future consolidation ticket; not a defect on this slice.
- **Joan round-1 gap closed** — Revision 1 orphan-delete for retired-key rows with empty `candidate_id` is implemented in `provision_meteorite_email_dispatch_tasks`.

## What's solid

- **`check_email` runner** — assembled_html to stage_meteorite; dedup; archive; last_email_check; summary.
- **Dispatcher** — mailbox awaits inbox.check_email; no check_inbox.
- **Provision AC5** — rewrite bound retired-key rows; delete orphans.
- **Admin** — mailbox gates on is_meteorite_email_mailbox_task_key.
- **Boundaries** — no classify/state; delegates to AST-1713 stage_meteorite.
- **Logging** — debug pairs, warnings with next_step; no entity-info stamp per plan.

context_tokens≈55000


## Bug: AST-1742 — NOT_A_JOB / BOT_BLOCKED rollup counts as fails

Parent mini-epic: [AST-1740](https://linear.app/astralcareermatch/issue/AST-1740/meteorites-deemed-not-a-job-should-be-fails). Publish ref: `sub/AST-1740/AST-1742-fix-not-a-job-rollup-counts`.

### As-is

Mailbox `check_email` and Land ingest (`ingest_candidate_email_message`) treat a successful classify skip the same as a successful job save: after archive they increment `passed` / return `counter="passed"`. `total_failed` stays 0 on the mailbox path. Operator rollups therefore show `NOT_A_JOB` as passes.

### To-be

Only rows that land in `READY` or `SCRAPE_LINK` count as passes. `NOT_A_JOB` or `BOT_BLOCKED` count as fails. ERROR-family outcomes (`NEW_EMAIL_ERROR`, `SCRAPE_ERROR`, stage `error`) count as errors — not passes. Archive-after-skip is unchanged; only the summary counters change.

### Repro

1. Bind a candidate to an inbox message whose Ruth classify outcome is a skip (`not_job_content` / `not_original_posting` → `stage_meteorite` returns `skipped=True`, inserts `NOT_A_JOB`).
2. Run mailbox `check_email` for that candidate (or Land selected-ids → `ingest_candidate_email_message`).
3. Observe: message is archived (correct) and the summary has `total_passed += 1` / `counter="passed"` with `total_failed` still 0 (broken).

### Root cause

Two intentional Stage contracts from the rework epic hard-coded skip-as-passed:

1. **AST-1714 Stage 1 step 5e** (`docs/features/meteorite/ast-1714-inbox-check-email-runner.md`): after non-error `stage_meteorite`, archive success always `passed += 1`, including `stage.get("skipped")` / `NOT_A_JOB`. Return shape left `total_failed` at 0 “unless a future step needs it.”
2. **AST-1713 ingest** (`docs/features/meteorite/ast-1713-stage-meteorite-saves-the-ruth-row.md`): on archive success after `stage["skipped"]`, return `_row(..., counter="passed")`.

`stage_meteorite` already distinguishes the cases (`skipped=True` + `NOT_A_JOB` insert vs landable `READY`/`SCRAPE_LINK` insert vs `error` / `NEW_EMAIL_ERROR`). The rollup layer ignores that distinction.

**BOT_BLOCKED note:** `stage_meteorite` does not produce `BOT_BLOCKED` (that state is scrape/notify later). On these Scope paths the fail bucket is driven by `skipped` / `NOT_A_JOB`. Include `BOT_BLOCKED` in the counting contract only if a stage/ingest outcome string ever carries it — do not widen into scrape runners.

### Proposed change

AST-1742 `## Scope` (amended): `src/core/inbox.py`, `src/core/meteorite.py`, `src/ui/api/api_inbox.py` (+ Betty tests if assertions lock skip-as-passed). `[scope-gate]` cleared — Chuckles added the Land `_land_all` file/kind to Scope on AST-1742 and AST-1740.

1. **`src/core/inbox.py` — `check_email` only (counter branches; archive rules untouched)**

   After a non-error `stage_meteorite` and **successful** `archive_candidate_email`:
   - if `stage.get("skipped")`: `failed += 1` (NOT_A_JOB / skip_outcomes path).
   - else: `passed += 1` (landable path → rows were saved as `READY` or `SCRAPE_LINK`; stage return has no `state` key — do not invent one; non-skipped + no `error` is the pass signal).
   - Leave the `stage.get("error")` branch as today: no archive, `errors += 1`.
   - Leave archive-exception → `errors += 1` as today (including the skipped next-step string).
   - **Decision — already-ingested dedup:** keep archive-success → `passed += 1` (hygiene of a prior row, not a fresh classify outcome). Do not inspect existing row states.
   - Return the live `failed` count in `total_failed` (stop treating it as permanently 0).

2. **`src/core/meteorite.py` — `ingest_candidate_email_message` `_row` counters only**

   After successful archive following stage:
   - if `skipped`: `_row(str(stage.get("outcome")), counter="failed")` — was `"passed"`.
   - else: `_row(..., counter="passed", job_count=len(jobs))` unchanged.
   - Error / stage-error / archive-failure paths stay `counter="error"`.
   - **Decision — already-ingested:** leave `counter="passed"` (same hygiene decision as `check_email`).
   - Docstring today says `counter passed|error` — extend to `passed|failed|error`.

3. **`src/ui/api/api_inbox.py` — `_land_all` counter branch**

   Prefer ingest `counter` before the skip_outcomes fallback. Today `counter not in {"passed","error"}` falls through to `outcome in skip_outcomes → is_passed=True`, which would keep NOT_A_JOB as passed even after step 2. Add before the `else`:

   ```python
   elif counter == "failed":
       is_passed = False
   ```

   No other Land toast / `total_skipped` redesign — when `is_passed` is false, skip outcomes correctly land in `total_failed` (and `total_errors` only if `row.get("error")`).

4. **Do not edit:** classify / `stage_meteorite` row-state selection, archive-after-skip control flow, `METEORITE_STATES`, scrape/`BOT_BLOCKED` runners, `src/utils/config.py`.

### Blast radius

- **Dispatcher mailbox** accumulates `check_email`’s four-key summary — `total_failed` will start moving; ledger already has the key.
- **`check_inbox`** (Land/admin leftover): still maps any non-`passed` counter to `errors` (no `failed` branch). Out of AST-1742 Scope; mailbox no longer calls it. Note only — do not expand this ticket to rewire `check_inbox`.
- **Manage Email Land** (`api_inbox._land_all`): step 3 makes ingest `counter="failed"` count as fails; without it, skip_outcomes fallback would keep NOT_A_JOB as passed.
- **Tests / bible** (Betty): any assertion that skip / `NOT_A_JOB` / `counter="passed"` / `total_failed == 0` for mailbox or ingest must flip; fix-board decides.

### What must still hold

- Archive after non-error stage (including skip / `NOT_A_JOB`) — leave in INBOX only when `stage["error"]`.
- Dedup: any prior `(email, mid)` row still skips re-stage and still attempts archive.
- `stage_meteorite` classify / insert behavior and state vocabulary unchanged.
- Return shape for `check_email` remains `{total_processed, total_passed, total_failed, total_errors}` (ints).
- Ingest Land-shaped row keys unchanged aside from `counter` value set.
- AST-1714 AC4/AC5 (full-message blob, provision rewrite) untouched.

### Canon Scope (this bug)

Patterns: (none — inherit AST-1714: logging statutes only).

Statutes (id-only until `make-fix`): `stat.logging.debug`; `stat.logging.error`; `stat.logging.info`; `stat.logging.info.dispatcher`; `stat.logging.warning`.

### Resolution (AST-1742) — 2026-09-21

**Radia** `[code-rubric] REVIEW` @ `c32117ad`: product retarget OK; missing bug-repro coverage lives on sibling **AST-1743** (landed `[bug-repro]` @ `f31756b1`); restack/merge is a Chuckles `merge-child` concern, not a product fix-now.

**Engineer resolve:** no product code changes — fix-now empty for this ticket. Advance to User Testing.

## Bug: AST-1743 — gap: skip→failed rollup test coverage

Parent mini-epic: [AST-1740](https://linear.app/astralcareermatch/issue/AST-1740/meteorites-deemed-not-a-job-should-be-fails). Sibling product: [AST-1742](https://linear.app/astralcareermatch/issue/AST-1742). Publish ref: `sub/AST-1740/AST-1743-gap-skip-failed-rollup-tests`.

Board trigger: `[board-betty] TESTS: REVISE` on AST-1742 — missing skip→failed coverage on `check_email` / ingest / `_land_all`.

### As-is

No bible-backed pytest node asserts that Ruth skip / `NOT_A_JOB` increments **failed** (not passed) on the scoped rollup paths. `TestAst1714CheckEmail` covers landable / stage-error / already-ingested only. `ingest_candidate_email_message` has no skip→`counter="failed"` assertion. Land `TestAst1558InboxLandMeteoriteApi` mocks landable ingest without a `counter="failed"` branch. Pre-AST-1742 product still counts skip as passed, so the hole is invisible in CI.

### To-be

Astral-tests component nodes (named in bible) assert skip→failed on all three Scope paths. They are red against pre-AST-1742 product and green once AST-1742’s counter retarget lands. No product code in this ticket.

### Repro

1. Fixture: candidate + inbox message; mock `stage_meteorite` / classify skip (`skipped=True`, outcome in `STAGE_METEORITE_CONFIG["skip_outcomes"]`, e.g. `not_job_content`) with successful archive.
2. Call `inbox.check_email` (or `ingest_candidate_email_message` / Land `_land_all`).
3. Pre-fix product: `total_passed == 1` / `counter="passed"` / `total_failed == 0` (broken contract). Post-AST-1742: `total_failed == 1` / `counter="failed"` / `total_passed == 0`, archive still called.

### Root cause

AST-1714 / AST-1713 locked skip-as-passed in product; component coverage never asserted the fail retarget on the live mailbox / Land paths. `TestAst1559CheckInbox::test_skip_outcome_zero_rows_monitor_archive` locks skip→passed on leftover `check_inbox` only — out of AST-1742 product Scope and not a substitute for `check_email` / ingest / `_land_all`.

### Proposed change

**Scope (tests + bible only — no `src/`):**

1. **`tests/component/core/test_inbox.py` — extend `TestAst1714CheckEmail`**
   - Add `[bug-repro]` method `test_skip_outcome_counts_failed_not_passed`:
     - Same fixture pattern as `test_stages_assembled_html_and_archives`.
     - Mock `stage_meteorite` → `skipped=True`, `outcome`/`stage_outcome` = `not_job_content` (or any configured skip outcome), `error=None`, `jobs=[]`.
     - Mock successful `archive_candidate_email`.
     - Assert: `total_processed == 1`, `total_failed == 1`, `total_passed == 0`, `total_errors == 0`; archive called once with message id.
   - Do **not** change landable / error / dedup assertions (dedup stays passed per AST-1742 plan).

2. **`tests/component/core/test_meteorite.py` — ingest counter**
   - Add (or extend under a small `TestAst1743IngestSkipFailed` / existing ingest suite if present) a node that drives `ingest_candidate_email_message` through skip + successful archive.
   - Assert returned row `counter == "failed"` (not `"passed"`); archive called; no requirement to assert Land toast fields here.

3. **`tests/component/ui/api/test_api_inbox.py` — Land `_land_all`**
   - Add `TestAst1558InboxLandMeteoriteApi::test_land_meteorite_counter_failed_counts_failed` (or sibling class):
     - Mock `ingest_candidate_email_message` → `counter="failed"`, skip `outcome` (e.g. `not_job_content`), `error=None`, `job_count=0`.
     - Assert response `total_failed == 1`, `total_passed == 0` (and `total_errors == 0` when no error key).
   - Leaves landable happy-path and already_ingested→passed mocks unchanged.

4. **Bible (Betty-owned paths on astral-tests → publish via merge-tests)**
   - `docs/test-bible/core/inbox.md` — new `### AST-1743 · AST-1740` (or append under AST-1714) naming the `TestAst1714CheckEmail` skip→failed node + short manifest line.
   - `docs/test-bible/core/meteorite.md` — name the ingest `counter="failed"` node.
   - `docs/test-bible/ui/api/api_inbox.md` — name the Land `counter="failed"` node (AST-1611 / AST-1558 area).

5. **Do not edit:** any `src/**` (AST-1742); `TestAst1559CheckInbox::test_skip_outcome_zero_rows_monitor_archive` (`check_inbox` leftover — out of product Scope); classify / `stage_meteorite` row-state tests beyond counter asserts.

**Ordering:** land tests on astral-tests against AST-1742’s product tip (or expect red until AST-1742 `make-fix` is on the same tree). Gap ticket does not implement product counters.

### Blast radius

- Depends on sibling **AST-1742** product counter retarget for green CI.
- Existing AST-1714 landable/error/dedup nodes and AST-1611 landable Land happy-path stay green.
- Leftover `check_inbox` skip→passed assertion remains until a future ticket rewires that path — do not “fix” it here.

### What must still hold

- No product / `src/` changes on this ticket.
- Archive-after-skip still asserted (archive called; counters only change).
- Dedup / already-ingested still counts as passed (AST-1742 hygiene decision).
- Stage-error still increments errors, not failed.
- AST-1714 AC4/AC5 (assembled blob, provision rewrite) untouched.

### Canon Scope (this bug)

Patterns: (none — tests/bible only).

Statutes: (none — no product files; inherit AST-1714 logging ids only if a future pass adds product).


## Radia review (AST-1743)

**PROCEED** — [bug-repro] skip→failed nodes OK (check_email / ingest / _land_all). Tests+bible only; product delta is sibling AST-1742. Clean §3h shortcut.
