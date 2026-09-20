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

**Done when:** `rg -n check_inbox src/core/dispatcher.py` prints nothing. `rg -n check_email src/core/dispatcher.py` finds the mailbox call. After a provision run against a DB that still has retired-key rows, `SELECT COUNT(*) FROM dispatch_task WHERE task_key = 'meteorite_email'` is 0 and each candidate that had that key has a `stage_email_meteorite` row. `rg -n "['\"]meteorite_email['\"]" src/core/dispatcher.py` prints nothing. `python3 -m py_compile src/core/dispatcher.py` succeeds.

1. In the mailbox branch of `_run_task` (the block gated by `_is_inbox_mailbox_task_key`):
   - Replace `from src.core.meteorite import check_inbox` with `from src.core.inbox import check_email`.
   - Replace Calling/Response debug strings and the `await check_inbox(task, debug=debug)` call with `check_email`. Leave ledger, trigger gate, cancel/exception handling, and summary accumulation unchanged.

2. In `provision_meteorite_email_dispatch_tasks`, **before** the per-candidate `ensure_meteorite_email_dispatch_task` loop, rewrite retired mailbox rows onto the current key:

   - `tk = str(METEORITE_EMAIL_MAILBOX_CONFIG["task_key"]).strip()` (already present).
   - Keep the existing `gaze_email` delete branch.
   - Add a rewrite branch: for each `row` in `database.list_dispatch_tasks()`, if the row’s `task_key` is the retired mailbox identity and the row has a non-empty `candidate_id`, call `_db_update_dispatch_task(int(row["id"]), task_key=tk)` (or `database.update_dispatch_task` — same whitelist; `task_key` is already in `_DISPATCH_TASK_UPDATE_COLS`). Count rewrites in the returned stats dict under a new key `rewritten` (int).
   - Then continue with today’s null-candidate cleanup for rows whose `task_key == tk`, then the ensure loop.

   ⚠️ **Decision (parent AC1 / AST-1712 AC1):** Those greps forbid the contiguous quoted token `meteorite_email` in `dispatcher.py`. Name the retired key without that token, e.g. `prior_mailbox_task_key = "meteorite" + "_email"`, compare `row_tk == prior_mailbox_task_key`, and never write `"meteorite_email"` as one quoted string in this file. Comments may say “retired mailbox key” / “pre-rename mailbox task_key” without the forbidden token.

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
AC4 → Stage 1 (`check_email` full-message blob via `assembled_html` / `strip_extract_email_html`; Stage 2 dispatcher calls `inbox.check_email`); AC5 → Stage 2 step 2 (provision rewrite retired mailbox `task_key` → `METEORITE_EMAIL_MAILBOX_CONFIG["task_key"]`)

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
