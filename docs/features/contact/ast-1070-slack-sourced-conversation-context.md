# AST-1070 — Slack-sourced conversation context load and cache

**Linear:** [AST-1070](https://linear.app/astralcareermatch/issue/AST-1070/slack-sourced-conversation-context-load-and-cache)  
**Parent:** [AST-1043](https://linear.app/astralcareermatch/issue/AST-1043/slack-bot-agent) — Slack Bot Agent  
**Publish ref:** `origin/sub/AST-1043/AST-1070-slack-sourced-conversation-context`

Give Contact a way to **load recent Slack thread/channel history** for Estelle turns, with an **optional process-local cache** and **append** of new inbound/outbound messages. **Source of truth remains Slack** (Web API history/replies). Does **not** add a full-exchange DB transcript table. Does **not** own Events verify/ack (AST-1069), Manage Slack (AST-1067), resolve/PROSPECT (AST-1068), skill runners (AST-1071), or the Estelle turn loop (AST-1046).

Depends on **AST-1069** (`src/external/slack.py` + Contact ingress already on `ftr`).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `CONTACT_CONFIG` with history limit, cache capacity, cache TTL | utils |
| `src/external/slack.py` | Add `fetch_conversation_history` (`conversations.history` / `conversations.replies`) | external |
| `src/core/contact.py` | `load_slack_conversation_context`, `append_slack_conversation_message`; append on accepted inbound; optional `contact_post_message` (post + append) | core |

No UI blueprint. No `database.py` schema / transcript table. No Manage Slack / resolve / skills / turn-loop changes beyond inbound append hook on existing `handle_slack_event` accept path.

---

## Stage 1: Config — context load / cache contracts

**Done when:** `CONTACT_CONFIG` exposes history page size, cache conversation capacity, and cache TTL; asserts pass; no secret values in config.

1. Extend `CONTACT_CONFIG` (keep existing listen / skills / Events / Socket keys) with:

```python
    # AST-1070: Slack history page size for context loads (Web API limit param).
    "context_history_limit": 50,
    # Process-local cache: max distinct (channel, thread) keys retained.
    "context_cache_max_conversations": 256,
    # Seconds before a cached conversation is considered stale (force Slack refetch).
    "context_cache_ttl_seconds": 300,
```

2. Asserts: all three are `int` and `> 0`; `context_history_limit` is the Slack `limit` passed to external (no hardcoded limit in core/external call sites).

⚠️ **Decision — process-local cache, not a DB transcript table:** Parent AC6 and Boundaries forbid a separate full-exchange transcript SoT in DB. Single gunicorn worker (RAILWAY_CONFIG) makes an in-process cache sufficient for this epic. Document that multi-worker would need shared cache (out of scope). Do **not** add `CREATE TABLE` / coat-check transcript storage.

---

## Stage 2: External — `fetch_conversation_history`

**Done when:** External can pull recent messages from a channel or thread via Slack Web API; no Contact/cache logic; no outcome logging.

1. In `src/external/slack.py`, add:

```python
def fetch_conversation_history(
    *,
    channel: str,
    thread_ts: Optional[str] = None,
    limit: int,
) -> list[dict]:
    """Fetch recent messages from Slack (SoT). Raise on HTTP/transport / ok:false."""
```

2. Behavior (literal):

   - `require_controlled_external_io("slack.fetch_conversation_history")`.
   - Token: `os.environ[CONTACT_CONFIG["bot_token_env"]]` (strict).
   - If `thread_ts` is set → `POST`/`GET` **`conversations.replies`** with `channel`, `ts=thread_ts`, `limit`.
   - Else → **`conversations.history`** with `channel`, `limit`.
   - Return the `messages` list from the JSON response (each item a Slack message dict). Raise on non-2xx or `ok is not True` (include Slack `error` in exception message; do not log).
   - Do **not** filter bot/subtype here — Contact decides what to keep for context.

3. Keep existing verify / challenge / `post_message` / Socket Mode helpers unchanged.

---

## Stage 3: Contact — load, cache, append

**Done when:** Core loads context (Slack SoT + process-local cache), can append messages, Style D when `debug=True`; UI never imports external.

1. Module-level process-local cache (same spirit as `event_id` dedupe):

   - Key: `(channel, thread_ts or "")`.
   - Value: `{ "messages": list[dict], "fetched_at": float }` (monotonic or `time.time()`).
   - Cap keys by `CONTACT_CONFIG["context_cache_max_conversations"]` (OrderedDict LRU).
   - Thread-safe with a lock.

2. Public functions (names exact):

```python
def load_slack_conversation_context(
    *,
    channel: str,
    thread_ts: Optional[str] = None,
    refresh: bool = False,
    debug: bool = False,
) -> dict:
    """Return recent conversation messages for a channel or thread.

    SoT is Slack. Cache is process-local only — never a DB transcript store.
    """

def append_slack_conversation_message(
    *,
    channel: str,
    thread_ts: Optional[str] = None,
    message: dict,
    debug: bool = False,
) -> None:
    """Append one message into the process-local cache for that conversation key."""

def contact_post_message(
    *,
    channel: str,
    text: str,
    thread_ts: Optional[str] = None,
    debug: bool = False,
) -> dict:
    """Post via external slack.post_message, then append outbound text into cache."""
```

3. `load_slack_conversation_context` behavior:

   - Normalize `channel` (strip); empty → raise `ValueError`.
   - If cache hit and not `refresh` and age `< context_cache_ttl_seconds`: return  
     `{"channel", "thread_ts", "messages", "source": "cache"}`.
   - Else: `messages = fetch_conversation_history(channel=…, thread_ts=…, limit=CONTACT_CONFIG["context_history_limit"])`; store in cache; return  
     `{"channel", "thread_ts", "messages", "source": "slack"}`.
   - Message dicts returned are the Slack API shapes (pass-through); do not invent a parallel transcript schema.
   - `debug=True`: Style D index + detail (`source`, channel, thread_ts, `len(messages)`); truncate long text previews.

4. `append_slack_conversation_message` behavior:

   - If no cache entry for the key yet, create one with `messages=[message]` and `fetched_at=now` (warm without Slack round-trip).
   - Else append `message` and trim to `context_history_limit` (keep newest).
   - `message` must be a `dict` with at least `text` and `ts` (string); raise `ValueError` otherwise.

5. `contact_post_message`: call `post_message`; on success append an outbound message dict using Slack response fields when present (`ts` from the API response; `text` as posted). Placeholder `user`/`bot_id` only for cache-local identity of Estelle’s own outbound — document that load still returns Slack API shapes from history fetches. Return the Web API JSON. AST-1046 should prefer this helper for outbound so cache stays warm.

6. Wire **inbound append** into existing `handle_slack_event`: when result `accepted` is True, call `append_slack_conversation_message` with:
   - `channel=event["channel"]`
   - `thread_ts=event.get("thread_ts")` only — if missing/`None`, normalize to `""` for the cache key (channel-only DM / channel root). **Never** pass message `ts` as the cache-key thread component.
   - `message={"user", "text", "ts"}` from the event (`ts` lives **inside** the message dict only).
   Do **not** fetch history inside `handle_slack_event` (ack path stays light).

⚠️ **Decision — cache key uses Slack thread_ts only:** Key is `(channel, thread_ts or "")`. Channel @-mention threads pass Slack’s `thread_ts`. DMs / channel roots without a thread use `""`. Message `ts` is never the key’s thread component (that would shard one DM into one key per message). Document in code comment.

⚠️ **Decision — no DB table:** Explicit parent boundary. Refresh always available via `refresh=True` / TTL expiry → Slack SoT.

---

## Stage 4: Self-check / no UI

**Done when:** No new blueprint; `api_slack` / `api_contact` unchanged except transitive core behavior; import direction holds (core→external only).

1. Confirm `src/ui/api/*` does not call `fetch_conversation_history`.
2. No frontend. No Manage Slack. No PROSPECT. No Estelle turn.

---

## Out of scope (explicit)

- Events signature verify / URL challenge / daemon ack (AST-1069 — already shipped).
- Manage Slack listen UI / env prefix (AST-1067).
- `get_candidate_id_for_query` / PROSPECT create (AST-1068).
- CONTACT_CONFIG skill runner bodies (AST-1071 — already on ftr).
- Estelle conversational turn + CHAT envelope (AST-1046).
- Full-exchange DB transcript table / coat-check conversation store.
- Multi-worker shared cache.
- Changing Socket Mode script beyond what Contact append provides for free.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — new Slack history external I/O, Contact load/cache/append surface, config contracts, and inbound append hook on accept.

**Conf:** `high` — Slack `conversations.history` / `replies` are fixed APIs; AST-1069 left `post_message` + Contact module; parent forbids transcript SoT so process-local cache is the matching design.

**Risk:** `MEDIUM` — stale/wrong context could mislead Estelle turns (AST-1046); mitigated by TTL + `refresh=True` + Slack as SoT on miss/expiry. No open unauthenticated surface added.

---

## Revisions

### Revision 1 — 2026-07-30

Driven by: Joan `[plan-discuss] round=1 concern` — fix-now Stage 3.6 vs Decision contradict on DM cache key (`ts` vs `""`).

Changes:

- Stage 3 step 6: inbound append passes `thread_ts=event.get("thread_ts")` only; message `ts` stays inside the message dict, never as the cache-key thread component.
- Decision wording aligned: key is `(channel, thread_ts or "")` only.
- Step 5: clarify outbound append prefers Slack response fields; placeholder bot identity is cache-local only (Joan discuss non-blocking).
