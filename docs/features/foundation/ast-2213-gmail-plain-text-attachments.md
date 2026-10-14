# AST-2213 — Gmail plain-text attachments

**Parent:** [AST-2207 — Update error reporting from production](https://linear.app/astralcareermatch/issue/AST-2207)
**Ticket:** [AST-2213](https://linear.app/astralcareermatch/issue/AST-2213)
**Publish ref:** `origin/sub/AST-2207/AST-2213-gmail-plain-text-attachments`

`send_email` in `src/external/gmail.py` learns to carry optional plain-text
attachments. When any are given, it sends a `multipart/mixed` message: the
body as a `text/plain` part, then one `text/plain` part per attachment with
`Content-Disposition: attachment; filename="…"`. When none are given, it builds
the same single `MIMEText(body, "plain")` message it builds today. The
return-`True`/`False`, never-raise contract and the
`require_controlled_external_io("gmail.send_email")` gate don't change. The
sibling ticket (parent proposed child #2, `src/core/monitor.py`) consumes the
new parameter to attach the full batch log; this ticket does not touch monitor.

## Scope gate

This ticket's `## Scope` names one product file and one change:
`src/external/gmail.py`, **modified function** `send_email` (optional
attachments parameter, multipart when given, unchanged message when not).
Every row below is that file and that kind of change. Tests and bible
(`tests/component/external/test_gmail.py`, `docs/test-bible/external/gmail.md`)
are listed in Scope but belong to Betty (`qa-child`). The engineer does not
edit them.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/gmail.py` | Add `MIMEMultipart` import; add optional `attachments` param to `send_email`; branch message construction on it; update docstring | external |

No other file is touched. No new dependency (`email.mime.multipart` is stdlib).

## Canon Scope

- `stat.logging.warning`: `send_email` keeps failing quietly. It catches,
  returns `False`, and logs nothing, and its caller (monitor) emits the
  WARNING. This ticket adds no logging to `gmail.py`.

## Stage 1: Attachments on `send_email`

**Done when:** `send_email(to, subject, body, attachments={"b-1.txt": "log"})`
hands the fake Gmail service a `raw` that decodes to `multipart/mixed` with a
`text/plain` body part and a `text/plain` part whose `Content-Disposition` is
`attachment; filename="b-1.txt"`. `send_email(to, subject, body)` (and
`attachments=None` / `{}`) still hands over a single `text/plain` message built
by the identical `MIMEText(body, "plain")` code path.

1. In `src/external/gmail.py`, in the import block, add
   `from email.mime.multipart import MIMEMultipart` on the line directly
   **above** the existing `from email.mime.text import MIMEText`.

2. In `src/external/gmail.py`, change the signature of `send_email` from

   ```python
   def send_email(to: str, subject: str, body: str) -> bool:
   ```

   to

   ```python
   def send_email(to: str, subject: str, body: str, attachments: dict[str, str] | None = None) -> bool:
   ```

   ⚠️ **Decision:** `attachments` is a `dict` keyed by filename, value = the
   attachment's text. The other options were a list of `(filename, text)`
   tuples and a list of `TypedDict` items. A filename-keyed dict follows the
   team convention of indexing collection elements by their id. It is also the
   smallest surface, and two attachments in one email with the same filename
   make no sense. Order is dict insertion order. Callers pass it by keyword
   (`attachments={f"{batch_id}.txt": text}`). The two existing callers in
   `src/core/monitor.py` (lines 65 and 98) pass no attachments and are
   unaffected.

3. Replace the docstring line
   `"""Send a plain-text email via the Gmail API. Returns True on success."""`
   with:

   ```python
   """Send a plain-text email via the Gmail API. Returns True on success.

   ``attachments`` maps filename -> text; each becomes a text/plain attachment
   on a multipart/mixed message. None or empty sends the single-part message.
   """
   ```

4. Inside the `try:` block, replace the single line
   `msg = MIMEText(body, "plain")` with:

   ```python
   if attachments:
       # multipart/mixed: body part first, then one text/plain attachment per file
       msg = MIMEMultipart("mixed")
       msg.attach(MIMEText(body, "plain"))
       for filename, content in attachments.items():
           part = MIMEText(content, "plain")
           # add_header quotes the filename -> attachment; filename="<name>"
           part.add_header("Content-Disposition", "attachment", filename=filename)
           msg.attach(part)
   else:
       # No attachments: same single-part message as before AST-2213
       msg = MIMEText(body, "plain")
   ```

   Leave the following `msg["to"]`, `msg["from"]`, `msg["subject"]`, `raw = …`,
   `service…send(…).execute()`, `return True`, and the
   `except Exception: return False` lines exactly as they are. Leave
   `require_controlled_external_io("gmail.send_email")` as the first statement,
   before `try:`.

   ⚠️ **Decision:** a falsy `attachments` (`None` or `{}`) takes the
   unchanged single-part path. An empty dict is "no attachments," so it must
   not produce a one-part multipart wrapper.

   ⚠️ **Decision:** no charset argument on either `MIMEText`. That matches
   today's body construction. The stdlib picks `us-ascii` when it can and
   falls back to `utf-8` otherwise, so non-ASCII log text survives (verified
   at plan time: an attachment holding `é` decodes back intact).

5. Compile and lint: `python -m py_compile src/external/gmail.py` and the
   repo's configured linter on `src/external/gmail.py`. Both clean.

6. Sanity-run the existing suite without editing it:
   `pytest tests/component/external/test_gmail.py -q`. All existing tests stay
   green. The new multipart assertions (AC 5) are Betty's to add in `qa-child`.

## Integration point (reference only)

Parent proposed child #2 (`src/core/monitor.py`, `auto_run_error`) is blocked
on this ticket. It will call
`send_email(to=…, subject=…, body=…, attachments={f"{batch_id}.txt": full_log})`.
No monitor change is planned here.

## Execution contract

The plan is binding. Execute steps in order. Don't add files, imports, logging,
or parameters beyond those above. If `send_email` on the synced branch no
longer matches the code this plan quotes, or a step fails when executed
literally, stop and post on the parent issue in the `🛑 Stage 1 blocked:`
format, then wait.

## Estimate

Confirm Chuckles estimate: 2 — agree
