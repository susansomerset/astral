# AST-1312 — Mailbox To on list and get payloads

**Linear:** [AST-1312](https://linear.app/astralcareermatch/issue/AST-1312/mailbox-to-on-list-and-get-payloads-email-bind-where-email-is-in-the)
**Parent:** [AST-1308](https://linear.app/astralcareermatch/issue/AST-1308/email-bind-where-email-is-in-the-to-field-alone) — Email bind where email is in the To: field (alone)
**Publish ref:** `origin/sub/AST-1308/AST-1312-mailbox-to-on-list-and-get-payloads`

Inbox list and get payloads already carry the raw **From** header as `from_address`. This ticket adds the raw **To** header the same way so sibling **AST-1313** (From-then-To bind) can see it. This ticket does **not** decide bind order, ignore the Astral inbox address, emit bind-source debug, or change Manage Email chrome.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/gmail.py` | Add `to_address` on `GmailInboxMessage` and `GmailMessageHtml`; request `To` on list metadata; copy the raw To header on list and get (empty string if missing) | external |

**No changes expected:** `src/core/inbox.py` (`list_inbox_messages` already does `row = dict(msg)` so `to_address` passes through; `get_message_html` already returns the external TypedDict as-is), `src/ui/api/api_inbox.py` (jsonify already forwards those dicts), `src/core/gaze_email.py`, `src/core/candidate.py`, `src/utils/config.py`, `src/ui/frontend/src/pages/AdminManageEmail.tsx` (extra JSON keys are ignored; chrome is out of scope), `tests/` / `docs/test-bible/**` (Betty after Code Complete).

**Do not add files.** If a step below cannot be executed in `src/external/gmail.py` alone, stop and comment on **AST-1308** with the stage-blocked template.

## Stage 1: Raw To on Gmail list and get shapes

**Done when:** `list_inbox_messages()` rows and `get_message_html()` payloads include `to_address` as the raw `To` header string (empty string when the header is missing or unreadable), using the same `_header_map` path as `from_address`; list metadata get requests include `"To"` so the header is actually present on `format="metadata"` responses; From bind / `candidate_match` / create rematch / archive / trash / Manage Email chrome are unchanged. `python3 -m py_compile src/external/gmail.py` succeeds (repo venv: `~/astral/.venv/bin/python` if present, else `python3`).

1. In `src/external/gmail.py`, extend `GmailInboxMessage` — insert `to_address: str` immediately after `from_address` (keep `date` / `unread` / `internal_date_ms` where they are):

```python
class GmailInboxMessage(TypedDict):
    id: str
    thread_id: str
    subject: str
    from_address: str
    to_address: str
    date: str
    unread: bool
    internal_date_ms: int
```

2. In the same file, extend `GmailMessageHtml` — insert `to_address: str` immediately after `from_address`:

```python
class GmailMessageHtml(TypedDict):
    id: str
    html_body: str
    subject: str
    from_address: str
    to_address: str
```

3. In `list_inbox_messages`, change the metadata get to request To as well:

```python
                metadataHeaders=["Subject", "From", "Date", "To"],
```

Add a one-line comment on that list: list `format="metadata"` only returns named headers — without `"To"`, `to_address` would always be empty on list rows.

4. In `_message_metadata`, after the existing `from_address` line, set:

```python
        "to_address": headers.get("to", ""),
```

Do **not** parse, split, lowercase, or strip display names. Do **not** drop the Astral inbox address. The value is the raw header string Gmail returned (same contract as `from_address`, which today can be `"Ada <ada@ex.com>"`).

5. In `get_message_html`, add `"to_address": headers.get("to", "")` to the returned dict (after `from_address`). Update the function docstring from “HTML body + Subject/From” to “HTML body + Subject/From/To”. `format="full"` already returns all headers; do **not** add a second Gmail get.

⚠️ **Decision — raw `to_address` string, not a parsed address list:** Ticket notes say this child only exposes the raw To field. Parent AC 2 (single remaining address after ignoring the Astral inbox) and bind-source debug belong to **AST-1313**. Parsing here would invent the sibling’s contract and risk two To-normalizers.

⚠️ **Decision — external-only; no core/API/React edits:** Core list already copies every external key; core get already returns `GmailMessageHtml`; the admin API already jsonifies those dicts. A core wrapper that re-sets `to_address` would be duplicate. Changing `_candidate_match_for_from`, `create_meteorite_job_from_inbox_message` rematch, or Manage Email columns would absorb **AST-1313** / chrome that this ticket forbids.

6. Do **not** change `_candidate_match_for_from`, `count_inbox_bound_by_candidate`, `create_meteorite_job_from_inbox_message`, gaze_email bind consumers, or any `debug=` Style D lines. Existing From-only bind must keep behaving exactly as today.

7. Compile: `python3 -m py_compile src/external/gmail.py`.

### Betty will need (not this ticket’s commit)

Exact-equality fixtures in `tests/component/external/test_gmail.py` (`TestListInboxMessages.test_paginates_and_preserves_order`, `test_non_dict_metadata_payload_yields_empty_fields`, `TestGetMessageHtml` exact dicts) will fail until they include `"to_address"`. `test_includes_subject_and_from_headers` should also assert a To header when Betty adds one to that fixture. Engineer does **not** edit `tests/` or `docs/test-bible/**`.

## Execution contract

The plan is binding. The agent:

- Executes steps in order within the stage.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- When the codebase has drifted from what the plan assumes — **stops and comments.** Does not adapt silently.
- Completes the stage on the epic worktree, commits, and publishes to `origin/sub/AST-1308/AST-1312-mailbox-to-on-list-and-get-payloads`.

Blocking comment format (parent **AST-1308**):

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

## Self-Assessment

**Scope:** Single-Component — one external module (`src/external/gmail.py`); TypedDict + header copy only; core/UI/bind untouched.

**Conf:** high — identical to the existing `from_address` / `_header_map` / `metadataHeaders` pattern from AST-1032 / AST-1049.

**Risk:** low — additive field with empty-string missing behavior; From bind and ingest consumers keep reading `from_address` / `candidate_match` as they do today. Wrong header name on `metadataHeaders` would leave list `to_address` empty and stall AST-1313, which is why step 3 is explicit.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Verdict |
|------|---------|
| §1.3 DRY | Reuse `_header_map` and the From empty-string missing path; no second To parser. |
| §2.1 config | No new config. Inbox identity / bind-header order are AST-1313. Header name `"To"` sits next to existing `"From"` in the Gmail API call, not a behavior set. |
| §2.4 batch | N/A — no claim/process/release. |
| §2.6 state | N/A — no entity state. |
| §3.3 imports | No new imports; external still imports utils only. |
| §3.5 naming | `to_address` matches `from_address`; snake_case. |

No conflicts. Conf remains **high**.
