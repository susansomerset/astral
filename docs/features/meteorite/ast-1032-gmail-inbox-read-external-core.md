# AST-1032 — Gmail inbox read (external + core)

**Linear:** [AST-1032](https://linear.app/astralcareermatch/issue/AST-1032/gmail-inbox-read-external-core-receive-email-on-gmail-account-for)
**Parent:** [AST-1031](https://linear.app/astralcareermatch/issue/AST-1031/receive-email-on-gmail-account-for-astral) — Receive email on gmail account for astral
**Publish ref:** `origin/sub/AST-1031/AST-1032-gmail-inbox-read`

Extend the existing Gmail external module so callers can list every inbox message (read and unread) for `GMAIL_USER` and fetch a selected message’s HTML body, orchestrated through a thin core wrapper. One dual-scope OAuth refresh token (`gmail.send` + `gmail.readonly`) keeps monitor alert send working. Live Gmail I/O honors `require_controlled_external_io` the same way send already does. Does **not** own admin nav, list UI, HTML modal, persistence, or CSE env vars (sibling AST-1033 owns the admin surface).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/gmail.py` | Dual-scope credential helper; `list_inbox_messages`; `get_message_html`; keep `send_email` on shared credentials | external |
| `src/core/inbox.py` | New thin orchestrator: list + get HTML, log failures, re-raise | core |

## Stage 1: External — dual-scope credentials + list/get

**Done when:** `src/external/gmail.py` can list every INBOX message with identifying metadata and return a selected message’s HTML body; `send_email` builds credentials from the same dual-scope set; every live Gmail call (send, list, get) invokes `require_controlled_external_io` before network I/O; module still fails import-time if required env vars are missing.

1. In `src/external/gmail.py`, update the module docstring to state that this module owns Gmail **send and inbox read** via one dual-scope OAuth client, and that required env vars remain `GMAIL_USER`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` (optional `GOOGLE_TOKEN_URI`). Do **not** read or write `GOOGLE_CSE_API_KEY` / `GOOGLE_CSE_ID`.

2. Add a module-level constant immediately after the existing env reads:

```python
_GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
]
_LIST_PAGE_SIZE = 500  # Gmail API page size only — not a result cap; paginate until exhausted
```

⚠️ **Decision:** One shared `_GMAIL_SCOPES` list for **all** credential builds (send and read). Parent AC requires a single dual-scope `GOOGLE_REFRESH_TOKEN`; listing both scopes on every call matches that contract. Ops remint of the refresh token (both scopes) is a parent dependency before live UAT — not this ticket’s code change.

3. Add TypedDict return shapes (import `TypedDict` from `typing`) near the top after imports:

```python
class GmailInboxMessage(TypedDict):
    id: str
    thread_id: str
    subject: str
    from_address: str
    date: str
    unread: bool


class GmailMessageHtml(TypedDict):
    id: str
    html_body: str
```

Export them via module `__all__` if the file already uses `__all__`; otherwise leave public by name (same style as current `send_email`). Prefer adding:

```python
__all__ = [
    "GmailInboxMessage",
    "GmailMessageHtml",
    "send_email",
    "list_inbox_messages",
    "get_message_html",
]
```

4. Add helpers **below** public functions (public-first rule §1.3). Implement:

- `_build_credentials() -> Credentials` — same fields as today’s `send_email` credential block, but `scopes=_GMAIL_SCOPES` (not send-only).
- `_build_service()` — `build("gmail", "v1", credentials=_build_credentials())`.
- `_header_map(payload_headers) -> dict[str, str]` — lowercased name → value for Gmail `payload.headers` list entries.
- `_decode_b64url(data: str) -> str` — `base64.urlsafe_b64decode` with padding fix; decode UTF-8 with `errors="replace"`.
- `_extract_html_body(payload: dict) -> str` — depth-first walk of `payload` / `parts`: if `mimeType == "text/html"` and `body.data` is present, return decoded string; recurse into `parts`; if no HTML part exists, return `""` (do **not** invent HTML from `text/plain`).
- `_message_metadata(raw: dict) -> GmailInboxMessage` — from a `users.messages.get` resource (`format="metadata"`): `id`, `thread_id` from `threadId` (empty string if missing), `subject` / `from_address` / `date` from headers `Subject` / `From` / `Date` (empty string if missing), `unread` = `"UNREAD" in (raw.get("labelIds") or [])`.

5. Refactor `send_email` to call `require_controlled_external_io("gmail.send_email")` then `_build_service()` instead of inlining Credentials/build. Keep the existing success/`except Exception: return False` contract unchanged (still never raises to monitor).

6. Add public `list_inbox_messages() -> list[GmailInboxMessage]`:
   - Call `require_controlled_external_io("gmail.list_inbox_messages")` first.
   - Build service via `_build_service()`.
   - Paginate `users().messages().list(userId="me", labelIds=["INBOX"], maxResults=_LIST_PAGE_SIZE, pageToken=...)` until `nextPageToken` is absent. Collect every message id from every page. **Do not** stop early after N messages — page size is only the Gmail API page parameter.
   - For each message id, call `users().messages().get(userId="me", id=message_id, format="metadata", metadataHeaders=["Subject", "From", "Date"])` and append `_message_metadata(...)`.
   - Preserve Gmail list order (do not re-sort).
   - On any exception after the controlled-I/O gate, **raise** (do not swallow like `send_email`). Empty inbox → `[]`.

⚠️ **Decision:** Raise on list/get failures (unlike `send_email`’s bool). Inbox callers need the payload or a hard failure for admin HTTP mapping; monitor’s “never raise” contract stays local to `send_email`.

7. Add public `get_message_html(message_id: str) -> GmailMessageHtml`:
   - Call `require_controlled_external_io("gmail.get_message_html")` first.
   - `users().messages().get(userId="me", id=message_id, format="full")`.
   - Return `{"id": message_id, "html_body": _extract_html_body(raw.get("payload") or {})}`.
   - On any exception after the gate, **raise**.

**Done when (recheck):** Importing the module still validates the four required env vars; `send_email` uses `_GMAIL_SCOPES`; list paginates INBOX to completion; get returns HTML-or-empty; both new entry points gate through `require_controlled_external_io` with distinct caller strings.

## Stage 2: Core — inbox orchestrator for AST-1033

**Done when:** `src/core/inbox.py` exposes list + get helpers that call external, log failures, and re-raise — ready for AST-1033’s admin API without UI importing external.

1. Create `src/core/inbox.py` with module docstring:

```
Inbox read orchestration for Meteorite seed (AST-1032).

Thin core wrapper over src.external.gmail list/get. No persistence, no admin HTTP.
AST-1033 owns the Read email admin surface and calls these functions.
```

2. Imports (allowed: external + utils only for this module — no data layer):

```python
from src.external.gmail import (
    GmailInboxMessage,
    GmailMessageHtml,
    get_message_html as external_get_message_html,
    list_inbox_messages as external_list_inbox_messages,
)
from src.utils.logging import get_logger

logger = get_logger(__name__)
```

3. Public functions (no helpers needed unless DRY requires them):

```python
def list_inbox_messages() -> list[GmailInboxMessage]:
    """Return every INBOX message metadata row for GMAIL_USER (read + unread)."""
    try:
        return external_list_inbox_messages()
    except Exception as e:
        logger.warning("[inbox] list_inbox_messages failed: %s", e)
        raise


def get_message_html(message_id: str) -> GmailMessageHtml:
    """Return HTML body payload for one Gmail message id."""
    try:
        return external_get_message_html(message_id)
    except Exception as e:
        logger.warning("[inbox] get_message_html failed id=%s: %s", message_id, e)
        raise
```

4. Do **not** add Flask routes, React files, NAV_CONFIG entries, database tables, or CSE config. Do **not** mutate mailbox state (no mark-read, archive, delete, label).

**Done when (recheck):** Core callers can `from src.core.inbox import list_inbox_messages, get_message_html` and receive the TypedDict shapes; failures are logged once then re-raised; no UI/data imports.

## Out of scope (do not implement here)

- AST-1033 admin nav / list screen / HTML modal / auth-gated HTTP.
- Persisting email bodies or ingest/routing.
- Reminting `GOOGLE_REFRESH_TOKEN` in any environment (ops / parent dependency).
- Changing CSE env vars or `GOOGLE_CSE_CONFIG`.
- Editing `tests/` or `docs/test-bible/**` (Betty owns those after Code Complete).

## Self-Assessment

**Scope:** `Single-Component` — extends one external module and adds one thin core orchestrator; no UI, data, or config.py changes.

**Conf:** `high` — reuses the existing Gmail OAuth + `require_controlled_external_io` pattern with a clear dual-scope constant and TypedDict returns matching `google_cse`-style external shapes.

**Risk:** `Medium` — wrong scopes or credential helper regression would break monitor alert send; list/get raises change the failure mode vs send’s bool, but send’s public contract is explicitly preserved.

## Rules self-review

- **§1.3 DRY / public-then-helpers:** Shared `_build_credentials` / `_build_service`; public `send_email` / `list_inbox_messages` / `get_message_html` first, helpers below.
- **§2.1 secrets-from-environ:** No new secrets in config; continue `os.environ[...]` for OAuth; CSE keys untouched.
- **§2.4 batch:** N/A — no entity batch claim.
- **§2.5 / §2.6:** External owns Gmail I/O; core orchestrates/logs; no state machine.
- **§3.3 imports:** `gmail.py` → utils only; `inbox.py` → external + utils only; UI never imports external.
- **§3.5 naming:** snake_case Python module `inbox.py`.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1031/AST-1032-gmail-inbox-read`
**Plan path:** `docs/features/meteorite/ast-1032-gmail-inbox-read-external-core.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `0fc6531f` | Dual-scope credentials; `list_inbox_messages` / `get_message_html` in `src/external/gmail.py` |
| 2 | `69750f7d` | Thin `src/core/inbox.py` orchestrator (log + re-raise) |

**Tip:** `ac6addfd` on `origin/sub/AST-1031/AST-1032-gmail-inbox-read`

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1032
**Publish ref tip (pre-docs):** `1241834f0eaac855ac04cfcbab647c8b3f23ee49`
**Overall:** DISCUSS

### What’s solid
- Dual-scope `_GMAIL_SCOPES` shared by send/list/get; `send_email` bool contract preserved; list/get raise after `require_controlled_external_io`.
- Thin `src/core/inbox.py` logs then re-raises; no UI/data/CSE bleed; public-then-helpers in `gmail.py`.
- Diff matches plan Stages 1–2 and Self-Assessment Single-Component.

### Issues
- **discuss (straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` at plan time; three-dot diff now includes `docs/features/**` + Betty `tests/**` / `docs/test-bible/**` so they score in-scope (all **conforms** on substance).

### Recommended actions
- Ada: acknowledge stragglers (no product change expected) then proceed resolve-child → User Testing.
