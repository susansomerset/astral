# AST-1033 — Read email admin screen (ingest seed)

**Linear:** [AST-1033](https://linear.app/astralcareermatch/issue/AST-1033/read-email-admin-screen-ingest-seed-receive-email-on-gmail-account-for)
**Parent:** [AST-1031](https://linear.app/astralcareermatch/issue/AST-1031/receive-email-on-gmail-account-for-astral) — Receive email on gmail account for astral
**Publish ref:** `origin/sub/AST-1031/AST-1033-read-email-admin-screen`

Auth-gated admin API + **Read email** nav/screen: list every INBOX message for `GMAIL_USER` (read + unread), click one, show its HTML body in a scrollable modal. Calls AST-1032’s `src.core.inbox` only — UI never imports `src.external.gmail`. Seed surface for a later Meteorite ingest epic; no ingest, persistence, or Gmail credential work here.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add Admin nav item **Read email** → `/admin/read_email` | utils |
| `src/ui/api/api_inbox.py` | New blueprint: list + get-html admin endpoints, `@require_admin` | ui |
| `src/ui/server.py` | Register `inbox_bp` | ui |
| `src/ui/frontend/src/pages/AdminReadEmail.tsx` | New admin page: inbox table + HTML body modal | ui |
| `src/ui/frontend/src/routes.tsx` | Route `admin/read_email` under `AdminRoute` | ui |
| `src/ui/frontend/src/App.css` | `.email-html-frame` so wide-modal iframe fills and scrolls | ui |

## Stage 1: Nav + auth-gated inbox API

**Done when:** `NAV_CONFIG` exposes **Read email**; `GET /api/admin/inbox/messages` and `GET /api/admin/inbox/messages/<message_id>` return JSON from `src.core.inbox` under `@require_admin`; unauthenticated callers get 401 and non-admins get 403; UI module never imports external/data.

1. In `src/utils/config.py`, inside the Admin group of `NAV_CONFIG` (after **Session Cover Letter**), append:

```python
{"label": "Read email", "path": "/admin/read_email"},
```

Keep the existing SYNC comment contract with `routes.tsx` — do not rename the path after this step.

2. Create `src/ui/api/api_inbox.py` with module docstring:

```
Read-email admin API (AST-1033 / Meteorite seed).

Thin Flask wrappers over src.core.inbox. No Gmail I/O here; no persistence.
```

3. In that file, define:

```python
from flask import Blueprint, jsonify

from ui.auth import require_admin
from src.core.inbox import get_message_html, list_inbox_messages
from src.utils.logging import get_logger

logger = get_logger(__name__)

inbox_bp = Blueprint("inbox", __name__, url_prefix="/api/admin/inbox")
```

⚠️ **Decision:** Dedicated `api_inbox.py` blueprint (not more routes stuffed into `api_admin.py`) so this Meteorite seed stays a separable UI surface for the later ingest epic. Prefix stays under `/api/admin/…` so `@require_admin` matches every other admin tool.

4. Add `GET ""` route? No — use explicit paths:

```python
@inbox_bp.route("/messages", methods=["GET"])
@require_admin
def inbox_list_messages():
    try:
        messages = list_inbox_messages()
    except Exception as e:
        logger.warning("[api_inbox] list failed: %s", e)
        return jsonify({"error": str(e)}), 502
    return jsonify({"messages": messages}), 200


@inbox_bp.route("/messages/<message_id>", methods=["GET"])
@require_admin
def inbox_get_message(message_id: str):
    mid = (message_id or "").strip()
    if not mid:
        return jsonify({"error": "message_id is required"}), 400
    try:
        payload = get_message_html(mid)
    except Exception as e:
        logger.warning("[api_inbox] get failed id=%s: %s", mid, e)
        return jsonify({"error": str(e)}), 502
    return jsonify(payload), 200
```

Response contracts (match AST-1032 TypedDicts; do not reshape keys):

- List: `{"messages": [{"id", "thread_id", "subject", "from_address", "date", "unread"}, ...]}`
- Get: `{"id": "<message_id>", "html_body": "<html or empty string>"}`

⚠️ **Decision:** Map core/external failures to **502** (upstream Gmail / controlled-I/O / OAuth), not 500. Empty `html_body` is a successful 200 — do not invent plain-text HTML.

5. In `src/ui/server.py`, after the existing `admin_bp` registration block, register the new blueprint:

```python
from ui.api.api_inbox import inbox_bp  # noqa: E402
app.register_blueprint(inbox_bp)
```

Follow the same `# noqa: E402` style as neighboring blueprint imports.

6. Do **not** import `src.external.gmail` or `src.data.*` from this module. Do **not** add mark-read, archive, delete, label, or persistence.

**Done when (recheck):** Admin JWT can hit both endpoints; missing/invalid session → 401; authenticated non-admin → 403; list returns `messages` array; get returns `id` + `html_body`.

## Stage 2: Read email admin page + modal

**Done when:** Authenticated admin opens **Read email** from nav, sees inbox rows (subject/from/date/read-unread), clicks a row, and a scrollable wide modal shows that message’s HTML body via sandboxed iframe; non-admins cannot reach the route.

1. Create `src/ui/frontend/src/pages/AdminReadEmail.tsx`:

- On mount, `GET /api/admin/inbox/messages` via `api` from `../lib/api`.
- Local state: `messages`, `loading`, `error`, `selectedId`, `htmlBody`, `bodyLoading`, `bodyError`.
- Render a heading **Read email** and a simple HTML `<table>` (not `ListPage` / not `DATA_SHAPES` — inbox is not a persisted entity shape). Columns in order: **Subject**, **From**, **Date**, **Status** where Status is `Unread` if `unread === true` else `Read`.
- Each data row is clickable (`cursor: pointer` via existing table row styling or a class already used on admin lists). On click: set `selectedId`, clear prior body error, `GET /api/admin/inbox/messages/<id>`, store `html_body` into `htmlBody`.
- While the modal is open, show `Modal` from `../components/Modal` with:
  - `open={selectedId !== null}`
  - `onClose` clears `selectedId`, `htmlBody`, `bodyError`
  - `title` = subject of the selected row, or `"Message"` if subject empty
  - `size="wide"`
  - **No** `onSave` prop (footer shows Cancel only)
- Modal body content:
  - If `bodyLoading`: short “Loading…” text
  - Else if `bodyError`: show the error string
  - Else: wrap an iframe:

```tsx
<div className="email-html-frame">
  <iframe title="Email body" sandbox="" srcDoc={htmlBody || ""} />
</div>
```

⚠️ **Decision:** Render Gmail HTML inside a sandboxed iframe (`sandbox=""` — no tokens) so email CSS/scripts cannot break the admin chrome. Do **not** use `dangerouslySetInnerHTML` for the body. Empty `html_body` still opens the modal with a blank iframe (valid Gmail case when no `text/html` part).

- Surface list-load failures with inline error text (and optional `Toast` if the page already imports Toast — either is fine; prefer the same Toast pattern as `AdminSessionResumePaste.tsx` if you add toast).
- Do not invent filters, pagination UI, or mark-as-read controls.

2. In `src/ui/frontend/src/routes.tsx`:

- Import `AdminReadEmail` from `./pages/AdminReadEmail`.
- Under the Admin routes block, add:

```tsx
{ path: "admin/read_email", element: <AdminRoute><AdminReadEmail /></AdminRoute> },
```

Place it after `admin/session_cover_letter` to match `NAV_CONFIG` order.

3. In `src/ui/frontend/src/App.css`, after the wide-modal rules (near `.modal-card--wide .modal-body`), add:

```css
/* AST-1033: Gmail HTML preview fills wide modal and scrolls inside the iframe */
.email-html-frame {
  height: 100%;
  overflow: hidden;
}
.email-html-frame iframe {
  display: block;
  width: 100%;
  height: 100%;
  border: 0;
  background: #fff;
}
```

Wide modal already sets `.modal-card--wide .modal-body { overflow: hidden; padding: 0; }` — the iframe scrolls internally; that satisfies the parent AC “scrollable modal” for HTML bodies.

4. Do **not** add ingest/routing UI, DATA_SHAPES entries, database tables, or Gmail env/config changes.

**Done when (recheck):** Nav shows **Read email**; admin route loads the table; click opens wide modal with sandboxed HTML; `AdminRoute` + `@require_admin` cover AC3 for screen and endpoints.

## Out of scope (do not implement here)

- Gmail OAuth / dual-scope token / `src.external.gmail` changes (AST-1032).
- Ingest, classify, reply, label, delete, archive, or mark-read.
- Persisting email bodies into Astral tables.
- CSE env vars or monitor send contract changes.
- Editing `tests/` or `docs/test-bible/**` (Betty owns those after Code Complete).

## Self-Assessment

**Scope:** `Single-Component` — admin UI surface only: one NAV entry, one thin inbox API blueprint calling existing core, one React page + route + CSS; no external/data/config secrets changes.

**Conf:** `high` — mirrors Session Resume / other `@require_admin` + `AdminRoute` admin seeds; core list/get contracts already shipped on ftr via AST-1032.

**Risk:** `Medium` — auth miss would expose mailbox content; iframe `sandbox=""` and `@require_admin` are the mitigations. Wrong API reshaping would break the React table/modal against AST-1032 TypedDict keys.

## Rules self-review

- **§1.3 DRY / public-then-helpers:** Thin route handlers only; no duplicated Gmail logic in UI.
- **§2.1 secrets-from-environ:** No new secrets; mailbox identity stays in AST-1032 / env.
- **§2.4 batch:** N/A — no entity batch claim.
- **§2.6 state machine:** N/A — display-only seed.
- **§3.2 / §3.3 imports:** `api_inbox.py` → core + utils + `ui.auth` only; React → `/api/admin/inbox/*` only; never ui→external.
- **§3.5 naming:** `AdminReadEmail.tsx`, path `/admin/read_email`, blueprint `inbox`.
- **`astral.patterns.require-auth-on-protected-endpoints`:** `@require_admin` on both endpoints; `AdminRoute` on the screen.
- **`astral.layers.ui-config-driven-business-logic`:** Nav via `NAV_CONFIG`; React renders API payloads without inventing inbox rules.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1031/AST-1033-read-email-admin-screen`
**Plan path:** `docs/features/meteorite/ast-1033-read-email-admin-screen.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `ab21fc2f` | NAV **Read email**; `api_inbox` list/get under `@require_admin`; register `inbox_bp` |
| 2 | `1c3505ce` | `AdminReadEmail` table + sandboxed HTML modal; route + CSS |

**Tip:** `055acb74cebc8493f2f4499dad9a794ab0b2ed03` on `origin/sub/AST-1031/AST-1033-read-email-admin-screen`

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1033
**Publish ref tip (pre-docs):** `a94497cc0cdc6b88c0c0fb08e1f01c3c024f563a`
**Overall:** DISCUSS

### What’s solid
- `@require_admin` on both inbox endpoints; `AdminRoute` on `/admin/read_email`; UI → core only (no external).
- Nav via `NAV_CONFIG`; sandboxed iframe (`sandbox=""`); 502 mapping for upstream failures; Stages 1–2 match plan.

### Issues
- **discuss (straggler ×14):** Joan excluded several statutes at plan time (1033 Files Changed = ui+utils); three-dot vs `origin/dev` also carries AST-1032 core/external/tests/docs, so those statutes score in-scope. All **conforms** on substance; no product fix expected.

### Recommended actions
- Hedy: acknowledge stragglers → resolve-child → User Testing.

## Resolution

**Date:** 2026-07-29
**Review:** Radia @ `18b09a64` — **fix-now:** none; **discuss:** statute straggler ×14 (all substance **conforms**); no advisory product items.

No product changes. Acknowledged discuss stragglers as plan-time Joan exclusions that became in-scope on the three-dot vs `origin/dev` (AST-1032 core/external/tests/docs on the same tip) — no code delta. Advanced to **User Testing**.
