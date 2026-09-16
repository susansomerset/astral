# AST-1667 — Workspace poster pool (external)

**Linear:** [AST-1667](https://linear.app/astralcareermatch/issue/AST-1667/workspace-poster-pool-external-bind-new-slack-contacts-to-existing)  
**Parent:** [AST-1636](https://linear.app/astralcareermatch/issue/AST-1636/bind-new-slack-contacts-to-existing-candidates-by-metadata-before) — Bind new Slack contacts to existing candidates by metadata before creating a prospect  
**Publish ref:** `sub/AST-1636/AST-1667-workspace-poster-pool-external`

Child #1 of AST-1636: add one Slack external helper that returns unique workspace users who have **posted a message** somewhere the bot can see (Slack user id + username), excluding bots and deleted users. Does **not** filter against candidate binds, change `resolve_slack_user`, expose an admin GET, or touch Manage Candidates UI (siblings AST-1668 / AST-1669).

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/external/slack.py` — new workspace-poster helper only.

**Out of scope (siblings):** Contact unbound filtering, `resolve_slack_user` / recognition replies, admin GET, Manage Candidates UI, `CONTACT_CONFIG` reply-text keys, `api_contact.py`, `AdminManageCandidates.tsx`, `candidate.py`.

**Depends on:** nothing (wave-1). Sibling AST-1668 will call this helper from core.

**Canon Scope (read in full for plan):** `stat.logging.debug`, `stat.logging.error`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/slack.py` | New public `list_workspace_posters()` (+ private helpers); `require_controlled_external_io`; bot-token Web API; `logger.debug` on loops; export in `__all__`; module docstring update | external |

No other files. Do **not** add config keys, UI, or Contact orchestration.

## Stage 1: Workspace poster pool helper

**Done when:** `list_workspace_posters()` is exported from `src/external/slack.py`, gated by `require_controlled_external_io`, returns a de-duplicated list of `{"slack_user_id", "username"}` for human posters derived from conversation message authors (not channel membership, not raw `users.list` alone), excludes bots/deleted, and raises on hard Slack/transport failures the same way existing helpers do.

1. In `src/external/slack.py`, update the module docstring:
   - Mention the new poster-pool helper alongside existing Web API helpers.
   - Keep the call-time env / `require_controlled_external_io` rules.
   - Clarify logging: **no** `logger.info` outcome lines in this module (parent: no outcome logging in external). **Do** use `logger.debug` at loop joints per `stat.logging.debug`. Fatal failures **raise** (callers / sibling log per `stat.logging.error` at the handler) — do not log-and-re-raise.

2. Add imports:
   - `from src.utils.logging import get_logger`
   - Module logger: `logger = get_logger(__name__)` (same pattern as `src/external/anthropic.py`).

3. Add to `__all__`: `"list_workspace_posters"`.

4. ⚠️ **Decision — Slack method mix:** Contact only has a **bot** token (`CONTACT_CONFIG["bot_token_env"]`). Slack `search.messages` requires a **user** token + `search:read`, so it is **out**. Implement poster discovery as:
   1. Paginate `conversations.list` for types the bot can see: `public_channel,private_channel,im,mpim`, `exclude_archived=true`.
   2. For each conversation id, paginate `conversations.history` and collect every message's `user` field when it is a non-empty `str`.
   3. When a history message has `reply_count` as an `int` `> 0` and a `ts`, paginate `conversations.replies` for that channel+ts and collect `user` the same way (thread-only posters still count as having posted).
   4. Enrich the unique poster id set via paginated `users.list` (`limit` per Slack page only — not a product cap on total users): keep ids that appear in both the poster set and `users.list`, drop entries where `is_bot` is true or `deleted` is true, username = `user.name` (empty string if missing).
   5. **Forbidden as the pool source:** `conversations.members` on any channel; treating `users.list` alone as "has posted" without the message-author set; hardcoding a bind-pool channel id in config.

5. ⚠️ **Decision — pagination / limits:** Use Slack cursor pagination until `next_cursor` is empty. Request page sizes may use Slack-recommended values (e.g. `limit=200` on list/history/replies/users.list). Do **not** add product-side caps such as "only N channels", "only last M messages", or "stop after K posters". Rate-limit retries are not in scope for this ticket — if Slack returns `ratelimited`, raise like other `ok:false` hard failures unless step 8 soft-skips that channel error.

6. ⚠️ **Decision — per-channel soft skip:** If `conversations.history` or `conversations.replies` returns `ok:false` with error in `{channel_not_found, not_in_channel, missing_scope, is_archived, method_not_supported_for_channel}`, **skip that conversation (or that thread)** after a `logger.debug` line naming method, channel id, and error; continue the outer loops. Any other `ok:false`, HTTP/`raise_for_status` failure, or `conversations.list` / `users.list` failure **raises** `RuntimeError` with method + Slack error (mirror `fetch_conversation_history`). Soft skips are not thrown exceptions — do not `logger.exception` for them (`stat.logging.error` is for handled throws).

7. Implement private helpers (names may vary; behavior must match):

   - **`_slack_bot_get(method: str, params: dict) -> dict`**: `require_controlled_external_io` is **not** called here (caller of the public entry gates once). Read `token = os.environ[CONTACT_CONFIG["bot_token_env"]]`. `requests.get(f"{_SLACK_API}/{method}", headers={"Authorization": f"Bearer {token}"}, params=params, timeout=_POST_TIMEOUT_SEC)`. `raise_for_status()`. Return `resp.json()` (caller checks `ok`).

   - **`_iter_conversations() -> list[str]`**: paginate `conversations.list` with `types=public_channel,private_channel,im,mpim`, `exclude_archived=true`, `limit=200`, cursor from `response_metadata.next_cursor`. Collect channel `id` strings. `logger.debug` begin/end with conversation counts. On `ok:false`, raise `RuntimeError`.

   - **`_collect_user_ids_from_messages(messages: list) -> set[str]`**: for each dict message, if `user` is a non-empty `str`, add it. Ignore bot-only shapes that lack `user`.

   - **`_collect_poster_ids_for_channel(channel_id: str) -> set[str]`**: paginate `conversations.history` (`channel`, `limit=200`, cursor). Union user ids from each page. For each message with `reply_count > 0` and `ts`, paginate `conversations.replies` and union those user ids. Apply soft-skip rule (step 6). `logger.debug` begin/end for the channel history loop (channel id + id counts).

   - **`_enrich_posters(poster_ids: set[str]) -> list[dict]`**: paginate `users.list` (`limit=200`). For each user dict whose `id` is in `poster_ids`, skip if `is_bot` or `deleted`; else append `{"slack_user_id": id, "username": str(user.get("name") or "").strip()}`. Sort the list by `(username.lower(), slack_user_id)` for stable sibling dropdowns. `logger.debug` begin/end with poster_ids size and result size. On `ok:false`, raise.

8. Implement public **`list_workspace_posters() -> list[dict]`**:

```python
def list_workspace_posters() -> list[dict]:
    """Return unique human workspace posters (slack_user_id + username).

    Pool = authors of messages the bot can read across conversations.list,
    not conversations.members and not users.list alone. Bots/deleted omitted.
    """
    require_controlled_external_io("slack.list_workspace_posters")
    logger.debug("Calling list_workspace_posters: []")
    channel_ids = _iter_conversations()
    poster_ids: set[str] = set()
    logger.debug("Beginning channel poster scan loop on %s items", len(channel_ids))
    for channel_id in channel_ids:
        poster_ids |= _collect_poster_ids_for_channel(channel_id)
    logger.debug("End channel poster scan loop after %s items", len(channel_ids))
    logger.debug("Calling _enrich_posters: poster_ids=%s", len(poster_ids))
    out = _enrich_posters(poster_ids)
    logger.debug("Response from _enrich_posters: %s", out)
    logger.debug("Response from list_workspace_posters: count=%s", len(out))
    return out
```

   Do **not** wrap the body in `if debug` / `if log_debug.get()`. Do **not** truncate debug payloads. Do **not** catch-and-`logger.exception`-then-re-raise (forbidden by `stat.logging.error` Don't). Propagate exceptions to the caller.

9. Do **not** change `fetch_user_profile`, `fetch_conversation_history`, `post_message`, signature helpers, or Socket Mode. Reuse `_SLACK_API` / `_POST_TIMEOUT_SEC` / `CONTACT_CONFIG["bot_token_env"]` only.

10. Compile/lint check before commit (engineer ritual at build time): `python -m compileall src/external/slack.py` and project lint for that file. Plan-child does not implement code.

## Execution contract

- Stages in order; steps in order; no extra files.
- Ambiguity / drift → comment on **parent** AST-1636 with the Stage blocked template; wait.
- Sibling consumers: return shape is `list[{"slack_user_id": str, "username": str}]` only — no filtering of already-bound candidates here.

## Estimate

Confirm Chuckles estimate: 3 — agree
