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

## Joan validate

[plan-rubric]
**Ticket:** AST-1667
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `sub/AST-1636/AST-1667-workspace-poster-pool-external` @ `45e6f058efec34bf61e3a377fa73c5f44628a1ac`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.debug | B | | Loop/callee debug contract spelled out; outer `list_workspace_posters` response uses count while `_enrich_posters` logs full payload |
| stat.logging.error | A | | Raises propagate; no log-and-re-raise; soft skips stay debug; handler logging deferred to sibling |

## Traceability

7 → Stage 1 (`list_workspace_posters` in `src/external/slack.py` only; `require_controlled_external_io`; no UI/API) · 8 → Stage 1 steps 4.4 & 7 (`is_bot` / `deleted` filtered in `_enrich_posters`) · 9 → Stage 1 steps 4.1–4.5 & 5 (message-author set via `conversations.list` + history/replies; forbids `conversations.members` and `users.list`-alone pool)

## Findings

### acceptable — Scope gate & partition
**Location:** Plan `## Scope gate`, `## Files Changed`
**Finding:** Single-file footprint matches ticket `## Scope` verbatim; siblings explicitly excluded.
**Recommendation:** None — proceed as written.

### acceptable — Parent technical scope fidelity
**Location:** Stage 1 decisions (Slack method mix, pagination, soft-skip)
**Finding:** Plan implements parent external slice: bot-token workspace poster discovery, bots/deleted excluded, no bind-pool channel id, no product-side caps on channels/messages/posters (Susan no-limits rule honored in step 5).
**Recommendation:** None.

### acceptable — stat.logging.debug outer response line
**Location:** Stage 1 step 8 (`Response from list_workspace_posters: count=%s`)
**Finding:** Slight variance from callee-out full-string idiom; mitigated because step 7 logs full `_enrich_posters` output and step 8 forbids gating/truncation elsewhere.
**Recommendation:** At build, prefer full `out` on the outer response line too, or drop the redundant outer line — not blocking.

## R6 checklist (summary)

- Definition fidelity: pass — implements child slice only; no Contact/UI/config creep.
- AC coverage: pass — child AC 7–9 mapped to Stage 1.
- DRY / scope creep: pass — new helpers justified; no duplicate of sibling orchestration.
- Self-assessment: pass — estimate 3 with detailed stage/decision markers is honest.

context_tokens≈32000

## Review (build stub)

| Field | Value |
|-------|-------|
| Status | Code Complete |
| Publish ref | `origin/sub/AST-1636/AST-1667-workspace-poster-pool-external` |
| Tip | `eb152ca2` |
| Branch | `sub/AST-1636/AST-1667-workspace-poster-pool-external` |

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `eb152ca2` | `list_workspace_posters` + helpers in `src/external/slack.py` |

**Betty note:** component coverage for poster pool (history/replies authors, soft-skip, bots/deleted filter, gate) deferred to qa-child.

## Radia review

[code-rubric]
**Ticket:** AST-1667
**Publish ref:** `2a813ef9c003d7452687df8bfe19b939446bc0dd` (`origin/sub/AST-1636/AST-1667-workspace-poster-pool-external`)
**Corpus:** `fc0c368e5927a57f1561c057ce9a0ff4abe1fb13`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.debug | A | | |
| stat.logging.error | A | | |

## Column diff vs plan stage

- `stat.logging.debug`: Joan **B** → Radia **A** — build logs full `out` on outer `Response from list_workspace_posters` (Joan’s callee-out note addressed).

## Frame diff

(none)

## Findings

### advisory — Branch diff carries sibling test/bible union
**Location:** `merge-tests(AST-1667)` tip vs `origin/dev`
**Finding:** Three-dot diff includes AST-1659/AST-1662 candidate/API test suites and bible sections from `origin/tests` union, not AST-1667 product work. **Product `src/` footprint is clean** — only `src/external/slack.py` changed.
**Recommendation:** Note in issue doc for downstream; no product fix required. Expected Betty merge-tests workflow.

### advisory — Bible shasum placeholder
**Location:** `docs/test-bible/external/slack.md` § AST-1667
**Finding:** Publish-tip bible entry still shows `*(filled after publish)*` while Linear manifest cites `5fba8ad2…`.
**Recommendation:** Chuckles/test-child housekeeping on doc pushback — not a canon or plan blocker.

## What's solid

- `list_workspace_posters()` matches Stage 1 plan: `conversations.list` → history/replies message authors → `users.list` enrichment; bots/deleted dropped; sorted stable output; `require_controlled_external_io` gate; soft-skip set matches plan; hard `ok:false` raises without logging.
- No `conversations.members`; lurker in `users.list` who never posted correctly excluded (AC 9).
- `TestAst1667WorkspacePosterPool` covers gate, author pool + thread replies, soft-skip, bots/deleted filter, and hard-failure raises — aligns with Betty manifest and bible intent.
- `stat.logging.error`: raises propagate; no `logger.exception` / log-and-re-raise in new external helpers; soft-skips stay at `debug`.
- Estimate 3 fits the single-file external helper + focused component suite.

## Recommended actions (Chuckles downstream — not Radia lane)

- Append this artifact to `docs/features/contact/ast-1667-workspace-poster-pool-external.md`, commit `docs(AST-1667): Radia review — clean`, push sub ref.
- Post slim upshot via `linear_proxy --as radia save-comment`; move **Review Posted** → **User Testing** (PROCEED, no fix-now items).

---

**Slim Linear upshot (Chuckles posts):**

```
[code-rubric] PROCEED (Commit: 2a813ef9) poster pool clean
```

context_tokens≈52000

