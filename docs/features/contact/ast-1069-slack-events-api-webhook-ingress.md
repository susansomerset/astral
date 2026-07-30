# AST-1069 — Slack Events API webhook ingress

**Linear:** [AST-1069](https://linear.app/astralcareermatch/issue/AST-1069/slack-events-api-webhook-ingress-external-slack-contact)  
**Parent:** [AST-1043](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent) — Slack Bot Agent  
**Publish ref:** `origin/sub/AST-1043/AST-1069-slack-events-api-webhook-ingress`

Ship production **Slack Events API HTTP Request URL** ingress: verify signing secret, answer URL verification challenge, **ack within ~3s**, dedupe `event_id`, and route Estelle-relevant DMs / `@` mentions into **Contact** when listen is on. Provide **Web API postMessage** for reply plumbing (AST-1046). Keep **Socket Mode** as a **local/dev-only** listener that feeds the same Contact handler. Does **not** own Manage Slack UI, resolve/PROSPECT, conversation cache, CONTACT_CONFIG skills ACL bodies, or Estelle turn loop.

Depends on **AST-1066** (`CONTACT_CONFIG` env-name contracts + `slack_listen_enabled()`).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `CONTACT_CONFIG` with Events path, bot event types, dedupe max, Socket Mode app-token env name | utils |
| `src/external/slack.py` | New module: signature verify, URL challenge parse, `post_message`, Socket Mode connect helper | external |
| `src/core/contact.py` | Inbound event handler: listen gate, event_id dedupe, mention/DM filter, optional `debug=` found/recorded lines; call external only for post | core |
| `src/ui/api/api_slack.py` | Thin blueprint `POST /api/slack/events` (no `@require_auth` — Slack signature is auth) | ui |
| `src/ui/server.py` | Register `slack_bp` | ui |
| `scripts/slack_socket_mode_dev.py` | Local/dev Socket Mode listener → same Contact handler | scripts |
| `requirements.txt` | Add `websocket-client` for Socket Mode local script only | deps |

No frontend pages. No Manage Slack. No `get_candidate_id_for_query` / PROSPECT. No conversation cache table. No Estelle dialogue (AST-1046).

---

## Stage 1: Config — Events + Socket Mode contracts

**Done when:** `CONTACT_CONFIG` exposes ingress path, subscribed bot event types, dedupe capacity, and Socket Mode app-token env name; secrets remain env **names** only; asserts pass.

1. In `src/utils/config.py`, **extend** existing `CONTACT_CONFIG` (do not replace listen/skills/env names from AST-1066) with:

```python
    # AST-1069: Events API Request URL path (Flask route under /api).
    "events_http_path": "/slack/events",
    # Bot events Contact accepts when listen is on (Slack Event Subscriptions must match).
    "bot_event_types": ("app_mention", "message"),
    # Process-local event_id dedupe capacity (single gunicorn worker — AST/Railway).
    "event_id_dedupe_max": 4096,
    # Socket Mode (local/dev only) — app-level token env name (xapp-…).
    "app_token_env": "SLACK_APP_TOKEN",
```

2. Asserts: `events_http_path` starts with `/`; `bot_event_types` non-empty tuple of str; `event_id_dedupe_max` int `> 0`; `app_token_env == "SLACK_APP_TOKEN"`.

3. Module docstring Required env list: add `SLACK_APP_TOKEN — Socket Mode app token (local/dev only; AST-1069)`.

⚠️ **Decision — extend CONTACT_CONFIG here:** Ticket Boundaries say this child does not *own* CONTACT_CONFIG as a product surface, but ingress constants must live in config (§2.1 / no-hardcoded-sets). Only add Events/Socket Mode keys; do not change `listen_enabled`, `skills`, or bot/signing env names.

⚠️ **Decision — process-local dedupe:** Single gunicorn worker (RAILWAY_CONFIG) makes an in-process ring/set sufficient for Slack retries in this epic. Do **not** add a DB table. Document in plan Railway section that multi-worker would need shared dedupe (out of scope).

---

## Stage 2: `src/external/slack.py`

**Done when:** External module verifies signatures, extracts URL challenges, posts chat messages via Web API, and can open a Socket Mode connection for the local script — **no Contact business logic**, no logging of outcomes (caller logs).

1. Create `src/external/slack.py` with module docstring stating: Events HTTP + Web API post for production; Socket Mode helper for local/dev only; secrets from `os.environ[CONTACT_CONFIG[…]]` at **call time** (strict, no `.get`); never read secrets at import (unlike gmail — missing Slack env must not break unrelated processes).

2. Public functions:

| Function | Behavior |
|----------|----------|
| `verify_slack_signature(*, signing_secret: str, timestamp: str, body: bytes, signature: str) -> bool` | Slack v0 HMAC-SHA256 over `v0:{timestamp}:{body}`; reject if timestamp skew > 60s |
| `parse_url_verification(payload: dict) -> Optional[str]` | If `type == "url_verification"`, return `challenge` string; else `None` |
| `post_message(*, channel: str, text: str, thread_ts: Optional[str] = None) -> dict` | `require_controlled_external_io`; `POST https://slack.com/api/chat.postMessage` with `os.environ[CONTACT_CONFIG["bot_token_env"]]`; return JSON; raise on HTTP/transport failure; do not log |
| `open_socket_mode_connection(handler)` | Local/dev: use `SLACK_APP_TOKEN` + bot token to open Socket Mode websocket; invoke `handler(payload_dict)` per Events API-shaped envelope; **must not** be imported by production UI path |

3. Signature verify uses stdlib `hmac` / `hashlib`. HTTP uses existing `requests`. Socket Mode uses `websocket-client`.

4. Core/UI must not reimplement HMAC or Slack HTTP — only call these helpers.

⚠️ **Decision — no `slack_sdk` package:** Prefer `requests` + `websocket-client` + stdlib HMAC to avoid a heavy SDK. If Socket Mode handshake proves underspecified at build time, stop and comment on the parent — do not invent a second HTTP polling path.

---

## Stage 3: Contact inbound handler

**Done when:** `handle_slack_event` (name exact) accepts a verified Events payload, respects listen, dedupes `event_id`, accepts `app_mention` and DM `message` events, and returns a stable result dict siblings can extend; `debug=True` emits Style D found/recorded lines.

1. In `src/core/contact.py`, add:

```python
def handle_slack_event(payload: dict, *, debug: bool = False) -> dict:
    """Route one Slack Events API payload into Contact (listen-gated)."""
```

2. Behavior (literal):

   - If not `slack_listen_enabled()`: return `{"accepted": False, "reason": "listen_off"}` (no external I/O).
   - Read `event_id` from payload; if missing, return `{"accepted": False, "reason": "missing_event_id"}`.
   - Process-local dedupe: module-level ordered set/deque capped by `CONTACT_CONFIG["event_id_dedupe_max"]`; if seen, return `{"accepted": False, "reason": "duplicate_event"}`.
   - `event = payload.get("event") or {}`; `etype = event.get("type")`.
   - Accept only if `etype` in `CONTACT_CONFIG["bot_event_types"]`.
   - For `type == "message"`: ignore `subtype` bot/message_changed/etc.; ignore messages with `bot_id`; require DM channel shape — `event.get("channel_type") == "im"` **or** channel id starting with `D` (document which check in code comment; prefer `channel_type == "im"` when present).
   - For `app_mention`: accept (channel @Estelle).
   - On accept: return `{"accepted": True, "event_id": …, "event_type": etype, "user": event.get("user"), "channel": event.get("channel"), "ts": event.get("ts"), "thread_ts": event.get("thread_ts"), "text": event.get("text")}`.
   - Do **not** call resolve/PROSPECT (AST-1068), do **not** load history (AST-1070), do **not** run Estelle turn (AST-1046), do **not** `post_message` in this handler (reply loop is AST-1046; post helper exists for plumbing tests/siblings).

3. When `debug=True`: use `get_logger` + existing debug helpers (`debug_detail` / Style D index pattern per Code Rules §1.5.1 / AST-538) for found/recorded lines (event_id, type, accepted/reason). Truncate long `text`.

4. UI calls this after signature verify; Socket Mode script calls the same function.

---

## Stage 4: HTTP webhook UI + server register

**Done when:** Slack can POST the Request URL; challenge returns; signed events ack with 200 within the request; Contact runs off the request thread when listen-relevant.

1. Create `src/ui/api/api_slack.py`:

   - Blueprint `slack_bp`, `url_prefix="/api"`.
   - `POST` route = `CONTACT_CONFIG["events_http_path"]` (i.e. `/api` + `/slack/events` → **`/api/slack/events`**).
   - **No** `@require_auth` — Slack cannot send Astral Bearer tokens; **signing secret verification is the auth**.
   - Read **raw** body: `request.get_data()` (required for HMAC).
   - Headers: `X-Slack-Signature`, `X-Slack-Request-Timestamp`.
   - `signing_secret = os.environ[CONTACT_CONFIG["signing_secret_env"]]` (strict; missing → 500).
   - If `not verify_slack_signature(...)`: return `""`, 401.
   - `payload = request.get_json(silent=True) or {}` **after** verify (or `json.loads(body)`).
   - If `challenge := parse_url_verification(payload)`: return `jsonify({"challenge": challenge})`, 200.
   - Else: start `threading.Thread(target=…, daemon=True)` that calls `handle_slack_event(payload, debug=ui_llm_debug())`; **immediately** return `""`, 200 (empty body is fine for Slack event ack).

2. Register blueprint in `src/ui/server.py` next to other API blueprints.

⚠️ **Decision — open route + signature:** This matches webhook norms and Code Rules §2.9 (endpoints without `@require_auth` are open; Slack signature replaces Bearer). Do not put this route behind admin auth.

⚠️ **Decision — ack then process:** Parent requires ack within ~3s; gunicorn single worker still must not block on Contact work. Daemon thread pattern already used in `api_admin` backfill.

---

## Stage 5: Socket Mode local script + Railway docs (in this plan)

**Done when:** Local script exists and plan documents production Request URL wiring; production code path never opens Socket Mode.

1. Add `websocket-client` to `requirements.txt`.

2. Add `scripts/slack_socket_mode_dev.py`:

   - Docstring: **local/dev only**; production must use Events Request URL.
   - Load dotenv; call `open_socket_mode_connection` / equivalent loop; for each event envelope call `handle_slack_event`.
   - Exit non-zero with clear message if `SLACK_APP_TOKEN` / bot token missing.

3. **Railway / Slack app wiring** (operator checklist — keep in this plan file under a short `### Production Request URL` subsection; no separate ops repo file):

   - Slack app → Event Subscriptions → Enable → Request URL = `https://<railway-host>/api/slack/events`
   - Subscribe bot events: `app_mention`, `message.im` (and any needed message events matching `bot_event_types`)
   - Environ on Railway: `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET` (no `SLACK_APP_TOKEN` required in production)
   - Manage Slack listen (AST-1067) must be on before Contact accepts; until then handler returns `listen_off`

### Production Request URL

| Step | Action |
|------|--------|
| 1 | Deploy Astral with `SLACK_BOT_TOKEN` + `SLACK_SIGNING_SECRET` set |
| 2 | Slack app **Event Subscriptions** Request URL → `https://<prod-host>/api/slack/events` |
| 3 | Verify URL (Slack sends `url_verification`; endpoint returns `challenge`) |
| 4 | Subscribe bot events matching `CONTACT_CONFIG["bot_event_types"]` |
| 5 | Install app to Astral Career Match workspace; invite Estelle to channels as needed |
| 6 | Turn Manage Slack listen **on** (AST-1067) per environment |

---

## Out of scope (explicit)

- Manage Slack listen UI / per-env flip (AST-1067) — only **read** `listen_enabled`.
- `get_candidate_id_for_query` / PROSPECT create / Slack user id persist (AST-1068).
- Slack history load/cache (AST-1070).
- CONTACT_CONFIG skill runners (AST-1071).
- Estelle conversational turn + success/failure/concern envelope (AST-1046).
- Using Socket Mode as production ingress.
- Full-exchange DB transcript store.
- Frontend React pages.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — new external Slack module, webhook blueprint, Contact inbound path, Socket Mode dev script, and CONTACT_CONFIG ingress keys.

**Conf:** `high` — AST-1066 left env-name contracts and listen gate; Events verify/ack/post is a well-specified Slack contract; layering matches gmail/playwright external patterns.

**Risk:** `HIGH` — a broken verify/ack can disable Estelle workspace-wide or open an unauthenticated webhook; mitigated by signature check, listen gate, and no Bearer-open data APIs on this route.
