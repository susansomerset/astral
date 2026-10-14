# AST-2214 — Alert header, WARNING/ERROR body, log attachment

**Parent:** [AST-2207 — Update error reporting from production](https://linear.app/astralcareermatch/issue/AST-2207)
**Ticket:** [AST-2214](https://linear.app/astralcareermatch/issue/AST-2214)
**Publish ref:** `origin/sub/AST-2207/AST-2214-alert-header-log-attachment`

`auto_run_error` in `src/core/monitor.py` stops dumping the whole batch log
into the support-alias email body. The body opens with a labelled metadata
header (deploy, candidate, task, batch, status, counts). Below it comes a
fenced block that holds only the batch's WARNING and ERROR lines, or a
one-line notice when there are none. The complete log, at every level and
oldest first, rides along as a `<batch_id>.txt` attachment through the
`send_email(..., attachments=...)` parameter that AST-2213 added (already on
`origin/ftr/AST-2207-production-error-report-email`). `provider_balance_outage` moves from
`support_email` to the admin address(es) in `AUTH_CONFIG["admin_emails"]`.
Its subject and body don't change, and it sends no attachment. When no admin
is configured, it logs one WARNING and skips the send. The subject line,
triggers, dispatcher, and `gmail.py` are untouched.

## Scope gate

This ticket's `## Scope` names one product file, `src/core/monitor.py`, with
four change kinds. Each maps to a stage step below:

| Scope line | Plan |
|------------|------|
| **new helper**: metadata header from `task_key`, `batch_id`, `accumulated`, `final_status`, `candidate_id` + `get_deploy_label()` + last-name lookup | `_format_alert_header` (Stage 1, step 3) |
| **modified helper** `_format_log_body`: split into full text + WARNING/ERROR fenced block, one shared fetch, filter in monitor | `_format_log_line`, `_format_full_log`, `_format_warning_error_block` replace `_format_log_body`; the one fetch lives in `auto_run_error` (Stage 1, steps 4 and 5) |
| **modified function** `auto_run_error`: header + body + attachment | Stage 1, step 5 |
| **modified function** `provider_balance_outage`: admin recipient, no-admin WARNING | Stage 1, step 6 |

Tests and bible (`tests/component/core/test_monitor.py`,
`docs/test-bible/core/monitor.md`) are listed in Scope but belong to Betty
(`qa-child`). The engineer does not edit them.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/monitor.py` | Import `AUTH_CONFIG`; new `_format_alert_header`; replace `_format_log_body` with `_format_log_line` / `_format_full_log` / `_format_warning_error_block`; rewire `auto_run_error` body + attachment; route `provider_balance_outage` to admin(s) | core |

No other file is touched. No new dependency. `list_log_entries`,
`send_email`, and the dispatcher's call sites keep their signatures.

## Canon Scope

- `stat.logging.warning`: the two existing `[monitor] ... returned False`
  / `raised unexpectedly` WARNINGs stay exactly as they are. The one new
  WARNING (no admin configured) is a single line that names who (the
  balance alert for `batch_id`) and why (`ASTRAL_ADMIN_EMAILS` empty). Its
  semantics also define half of what the body filter selects.
- `stat.logging.error`: defines the ERROR entries the body filter selects.
  Monitor reports faults that were already logged. It adds no
  `logger.error` / `logger.exception` of its own and doesn't re-log anything
  it puts in the email.

## Stage 1: Alert shape and balance-outage routing

**Done when:** `auto_run_error` with a stubbed `send_email` and seeded
DEBUG/INFO/WARNING/ERROR rows produces three things: a `body` that starts
with the six header lines and is followed by a fence holding only the WARNING
and ERROR lines, a `body` that shows the "no WARNING or ERROR entries" line
when only INFO rows exist, and `attachments == {"<batch_id>.txt": <every row,
oldest first>}`. `provider_balance_outage` sends to
`", ".join(sorted(AUTH_CONFIG["admin_emails"]))` with the unchanged
subject/body and no attachment. With no admins configured, it logs one
WARNING and does not send.

1. In `src/core/monitor.py`, change the import line
   `from src.utils.config import ASTRAL_CONFIG, get_llm_server` to
   `from src.utils.config import ASTRAL_CONFIG, AUTH_CONFIG, get_llm_server`.

2. In the module docstring, replace the sentence
   `The dispatcher calls auto_run_error()
   after any AUTO task run that produces errors, and provider_balance_outage()
   instead when the run was stopped by an LLM provider balance refusal.`
   with
   `The dispatcher calls auto_run_error()
   after any AUTO task run that produces errors (support alias: metadata header,
   WARNING/ERROR body, full log attached), and provider_balance_outage()
   instead when the run was stopped by an LLM provider balance refusal (admin
   address(es), short body, no log).`
   Leave the rest of the docstring as is.

3. In the `# Helpers` section, add this function directly **above**
   `_resolve_candidate_last_name`:

   ```python
   _ALERT_COUNT_KEYS = {
       "Processed": "total_processed",
       "Passed": "total_passed",
       "Failed": "total_failed",
       "Errors": "total_errors",
   }


   def _format_alert_header(
       deploy_label: str,
       candidate_id: str,
       last_name: str | None,
       task_key: str,
       batch_id: str,
       final_status: str,
       accumulated: dict,
   ) -> str:
       """Labelled triage block that opens every support-alias alert (AST-2214).

       Every label is always present; a value the run doesn't have shows '-'.
       """
       cid = (candidate_id or "").strip()
       # "cand-1 (Somerset)" when the last name is known, bare id otherwise, '-' with no candidate
       candidate = f"{cid} ({last_name})" if cid and last_name else (cid or "-")
       # one line, same "Label: n  Label: n" shape as the balance-outage body
       counts = "  ".join(f"{label}: {accumulated.get(key, '-')}" for label, key in _ALERT_COUNT_KEYS.items())
       return "\n".join([
           f"Deploy: {deploy_label or '-'}",
           f"Candidate: {candidate}",
           f"Task: {task_key or '-'}",
           f"Batch: {batch_id or '-'}",
           f"Status: {final_status or '-'}",
           counts,
       ])
   ```

   ⚠️ **Decision:** the header helper takes `deploy_label` and `last_name` as
   arguments instead of calling `get_deploy_label()` /
   `_resolve_candidate_last_name()` itself. `auto_run_error` already computes
   both for the subject, so passing them in keeps one candidate DB read per
   alert and guarantees the header and subject prefix agree. The values still
   come from exactly the sources the Scope names.

   ⚠️ **Decision:** "Batch:" carries `batch_id`. The dispatcher passes its
   `dispatch_ledger_id` as `batch_id` (`dispatcher.py` line 1539 and the
   `auto_run_error` call after it), so this is the "batch / dispatch ledger
   id" the parent definition asks for. No new argument.

   ⚠️ **Decision:** a count key missing from `accumulated` renders `-`, not
   `0`. The parent definition says "Fields that don't exist for a run show
   `-`." The dispatcher always seeds all four keys (`dispatcher.py` line 594),
   so production alerts show numbers. The subject line keeps its existing
   `0` defaults and is not touched.

4. Delete the whole `_format_log_body` function and put these three functions
   in its place, at the top of the `# Helpers` section:

   ```python
   def _format_log_line(entry: dict) -> str:
       """One app_log row in the alert/attachment line format."""
       return f"{entry.get('created_at', '')}  [{entry.get('level', '?')}]  {entry.get('message', '')}"


   def _format_full_log(entries: list[dict]) -> str:
       """Every row at every level, in the order given (chronological), for the .txt attachment."""
       if not entries:
           return "(no log entries found for this batch)"
       return "\n".join(_format_log_line(e) for e in entries)


   def _format_warning_error_block(entries: list[dict]) -> str:
       """WARNING and ERROR rows only, in the order given, in a fenced code block for the email body.

       The fence makes Linear (which files these alert emails as issues) render the log as
       one code block instead of a long description to scroll past. It is one
       backtick longer than any backtick run inside the logs, so a log line can't close it.
       """
       # filter on the stored level name (logging levelname), not on message text
       text = "\n".join(_format_log_line(e) for e in entries if e.get("level") in ("WARNING", "ERROR"))
       if not text:
           return "(no WARNING or ERROR entries for this batch)"
       longest_run = max((len(run) for run in re.findall(r"`+", text)), default=0)
       fence = "`" * max(3, longest_run + 1)
       return f"{fence}\n{text}\n{fence}"
   ```

   ⚠️ **Decision:** the filter keeps exactly `WARNING` and `ERROR`, as the
   ticket and parent definition state. `CRITICAL` rows are excluded from the
   body (they still appear in the attachment). Today nothing in `src/` emits
   `CRITICAL`: the only `.critical(` is the wrapper method in
   `src/utils/logging.py`, which has no callers. Widening the filter is
   Susan's call, not the planner's.

   ⚠️ **Decision:** the helpers take already-fetched, already-chronological
   rows. `auto_run_error` does the single `list_log_entries(batch_id=…)` call
   and the single `reversed(...)`, so the body block and the attachment can't
   drift apart. `_format_log_body` is removed, not kept as a wrapper, because
   it has no callers outside `monitor.py` and `test_monitor.py`.

5. In `auto_run_error`:

   a. Replace the docstring paragraph
      `Fetches log entries for the batch (already flushed to DB at this point),
      formats subject + body, and sends via Gmail. Never raises — a failed alert
      must not surface to the caller.`
      with
      `Fetches log entries for the batch once (already flushed to DB at this point).
      Body = metadata header + WARNING/ERROR-only fenced block; the full log at every
      level goes as a <batch_id>.txt attachment (AST-2214). Never raises — a failed
      alert must not surface to the caller.`

   b. Replace these two lines

      ```python
      logger.info("[monitor] fetching %s log entries for email body...", batch_id)
      body = _format_log_body(batch_id)
      ```

      with

      ```python
      header = _format_alert_header(
          deploy_label, candidate_id, last_name, task_key, batch_id, final_status, accumulated,
      )
      logger.info("[monitor] fetching %s log entries for email body...", batch_id)
      # one fetch feeds both the body block and the attachment; DB returns newest-first
      entries = list(reversed(database.list_log_entries(batch_id=batch_id)))
      body = f"{header}\n\n{_format_warning_error_block(entries)}"
      attachments = {f"{batch_id}.txt": _format_full_log(entries)}
      ```

   c. Replace `ok = send_email(to=to, subject=subject, body=body)` with
      `ok = send_email(to=to, subject=subject, body=body, attachments=attachments)`.

   Leave everything else in `auto_run_error` exactly as it is: the entry
   `logger.info`, `to = ASTRAL_CONFIG["support_email"]`, the subject build,
   the `sending alert` info line, the `ok` / `send_email returned False`
   WARNING branch, and the `except Exception` WARNING.

   ⚠️ **Decision:** the attachment is always sent, even for a batch with no
   log rows. In that case its text is the existing
   `(no log entries found for this batch)` placeholder. Every alert keeps one
   shape, and AC 4 ("exactly one attachment") holds unconditionally.

6. In `provider_balance_outage`:

   a. Replace the docstring
      `"""AST-1867: one alert per AUTO run stopped by an LLM provider balance refusal.
      Short body (no batch log dump). Never raises — a failed alert must not surface to the caller."""`
      with
      `"""AST-1867: one alert per AUTO run stopped by an LLM provider balance refusal.
      AST-2214: sent to the admin address(es) in AUTH_CONFIG["admin_emails"], not the support
      alias; short body, no batch log, no attachment. No admin configured -> one WARNING, no send.
      Never raises — a failed alert must not surface to the caller."""`

   b. As the **first** statements inside its `try:` (before the
      `# The server the refused task's agent actually called` comment), insert:

      ```python
      # sorted: admin_emails is a frozenset, so a multi-admin `to` would otherwise reorder per process
      admins = sorted(AUTH_CONFIG["admin_emails"])
      if not admins:
          logger.warning(
              "[monitor] provider_balance_outage: no ASTRAL_ADMIN_EMAILS configured — balance alert for %s not sent",
              batch_id,
          )
          return
      ```

   c. Replace `if not send_email(to=ASTRAL_CONFIG["support_email"], subject=subject, body="\n".join(lines)):`
      with `if not send_email(to=", ".join(admins), subject=subject, body="\n".join(lines)):`.

   Leave the provider/subject/lines build, the `Held` branch, the
   `send_email returned False` WARNING, and the `except Exception` WARNING
   exactly as they are. Do not pass `attachments`. Do not call
   `list_log_entries`.

   ⚠️ **Decision:** the empty-admin check runs first, so a misconfigured
   deploy does no provider/candidate lookups for an alert it won't send, and
   the one WARNING is the only log line from that path (AC 5). A falsy
   `send_email` return is still reported by the existing WARNING. These are
   two distinct causes, so each gets one line.

7. Compile and lint, both clean on the touched file:
   `python -m py_compile src/core/monitor.py` and
   `ruff check src/core/monitor.py`. At plan time (sync tip `ff2d5c973`),
   the file already has 4 findings: I001 (import block), BLE001 ×2 (the two
   `except Exception` handlers), and ISC004 (implicit string concat in the
   balance-outage `lines` list). These stay as they are and get recorded in
   the build review stub. Any **new** code (rule id not in that set, or the
   same rule on a new line) is fixed before committing.

8. Sanity-run without editing tests:
   `pytest tests/component/core/test_monitor.py -q`. These existing tests
   assert the old shape and **are expected to fail** until Betty revises them
   in `qa-child` (Scope: "existing `TestAutoRunError*` /
   `TestAst1867ProviderBalanceOutage` body assertions are revised to the new
   shape"):
   - `TestAutoRunError::test_sends_alert_with_log_body` (asserts the body is
     only a fence)
   - every `TestFormatLogBody` test (calls the removed `_format_log_body`)
   - `TestAst1867ProviderBalanceOutage` tests that rely on a send happening
     or on `to == support_email`, because `admin_emails` is empty in the test
     env and the alert is now skipped

   Every other test in the file must stay green. Record the actual failing
   node ids in the build review stub. Any failure **outside** that list is a
   stop-and-ask per the execution contract.

## Integration point (reference only)

AST-2213 (on `origin/ftr/AST-2207-production-error-report-email`) provides
`send_email(to, subject, body, attachments: dict[str, str] | None = None)`.
This plan only calls it. `src/external/gmail.py` is not edited.

## Execution contract

The plan is binding. Execute steps in order. Don't add files, imports,
logging, parameters, or levels beyond those above. If `monitor.py` or
`send_email` on the synced branch no longer matches the code this plan
quotes, or a step fails when executed literally, stop and post on the parent
issue in the `🛑 Stage 1 blocked:` format, then wait.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2214
**Overall:** APPROVED
**Corpus:** 0d01e20d2b313a4e35cf3d07434b6cd69f615768
**Publish ref:** `b7c6ade7faa37f1016b3f9131dc4d0c093eb49a7`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.warning | A | | |
| stat.logging.error | A | | |

## Traceability

1→S1:3,5; 2→S1:4–5; 3→S1:4; 4→S1:5; 5→S1:6; 6→parent UAT (manual; no build stage)

## Findings

### acceptable — No `## Self-assessment` block

- **Severity:** acceptable
- **Location:** Plan doc structure
- **Finding:** No self-assessment section; Estimate confirm is present.
- **Recommendation:** Optional; not blocking.

### acceptable — AC 6 not staged

- **Severity:** acceptable
- **Location:** Stage 1 “Done when” vs ticket AC 6
- **Finding:** Live deploy check is parent/ticket UAT, not encoded as an engineer stage (same pattern as other foundation children).
- **Recommendation:** Susan runs UAT after rollup; no plan change required.

### discuss — `CRITICAL` excluded from body filter

- **Severity:** discuss
- **Location:** Stage 1 step 4 (filter decision)
- **Finding:** Plan documents excluding `CRITICAL` from the body while parent AC 2 names only WARNING/ERROR; no current `CRITICAL` emitters in `src/`.
- **Recommendation:** If a future level ever lands in `app_log`, confirm Susan still wants it attachment-only; no plan edit needed for build.

### acceptable — Pre-existing `except Exception` → WARNING in monitor

- **Severity:** acceptable
- **Location:** Stage 1 steps 5–6 (“leave … WARNING … exactly as they are”)
- **Finding:** Unchanged swallow paths still log at WARNING, not ERROR; plan explicitly freezes them per Scope/Canon notes.
- **Recommendation:** Out of this ticket’s plan delta; any statute uplift is a separate fix-lane/architecture item.

## R6 checklist (summary)

- Definition fidelity: matches parent functional scope §§1–3 and §5 (balance outage), technical scope for `monitor.py` only; `gmail.py` and dispatcher untouched.
- Scope gate: single file; helper split + one shared fetch; `send_email(..., attachments=...)` assumes AST-2213 on `origin/ftr/AST-2207-production-error-report-email` (integration section states this).
- DRY / creep: removes `_format_log_body` rather than duplicating fetch paths; no sibling monitor-adjacent files.
- Expected test reds documented for `qa-child`; engineer sanity-run scope is explicit.
- Plan-discuss: **Plan Ready**; **0** completed `[plan-discuss]` rounds.

context_tokens≈42000

## Review (build)

**Built @ `ebf0917f`** — `origin/sub/AST-2207/AST-2214-alert-header-log-attachment`

- Stage 1 as planned, `src/core/monitor.py` only: `_format_alert_header` + `_ALERT_COUNT_KEYS`; `_format_log_body` replaced by `_format_log_line` / `_format_full_log` / `_format_warning_error_block`; `auto_run_error` does one fetch, sends header + WARNING/ERROR block and `{"<batch_id>.txt": full log}`; `provider_balance_outage` sends to `", ".join(sorted(AUTH_CONFIG["admin_emails"]))`, one WARNING + no send when empty.
- Lint: the same 4 pre-existing ruff findings as the plan baseline (I001, BLE001 ×2, ISC004), none new.
- `test_monitor.py` sanity run: 8 failed / 10 passed.
  - **Expected (plan step 8), for `qa-child`:** `TestAutoRunError::test_sends_alert_with_log_body`; `TestFormatLogBody::{test_returns_placeholder_when_no_entries, test_formats_entries_chronologically, test_fence_outruns_backticks_inside_the_logs}`; `TestAst1867ProviderBalanceOutage::test_subject_names_provider_and_body_is_short`.
  - **Pre-existing, red on the plan tip `f86bacdcb` without this diff:** `TestAutoRunErrorSubjectPrefix::{test_local_env_with_candidate_last_name, test_eu_west_preserves_case, test_unset_env_with_candidate_last_name}`. Their `get_candidate` stub returns `candidate_data.profile.last`, while `_resolve_candidate_last_name` reads top-level `last`. Stub/product mismatch predates AST-2214; not touched here — Betty's call.
  - Coverage gap for Betty: the other `TestAst1867ProviderBalanceOutage` tests now pass only because `admin_emails` is empty in the test env (early return), so they no longer exercise the send path.
