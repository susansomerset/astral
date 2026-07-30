# AST-1073 — Contact Estelle turn loop over AST-1043 Contact

**Linear:** [AST-1073](https://linear.app/astralcareermatch/issue/AST-1073/contact-estelle-turn-loop-over-ast-1043-contact-contact-estelle)  
**Parent:** [AST-1046](https://linear.app/astralcareermatch/issue/AST-1046/contact-estelle-conversational-envelope)  
**Publish ref:** `sub/AST-1046/AST-1073-contact-estelle-turn-loop`

Wire **AST-1043** Contact plumbing (listen gate, Slack resolve, conversation context, ACL skills, non-prod reply prefix) into a multi-turn Estelle loop that consumes the **AST-1072** conversational envelope via `do_task("contact_estelle_turn")`. Each accepted inbound DM / `@` mention becomes one turn: load context → `do_task` → structured outcome → optional ACL skill writes → Slack reply (prefix when non-prod). Does **not** redefine the envelope schema (sibling AST-1072). Does **not** re-implement Events ingress, Manage Slack UI, resolve-util internals, context cache, or skill ACL registration (AST-1043 children).

**Branch prerequisite (already applied on this sub):** `origin/ftr/AST-1046-…` held AST-1072 without full `CONTACT_CONFIG`; `origin/dev` held Contact without the CHAT envelope. Before Stages below, the sub tip must expose both `CONTACT_CONFIG` (listen / skills / context keys) **and** `CONTACT_ESTELLE_CONFIG` / `is_conversational_task` / `conversational_turn_from_do_task_result`. If a fresh checkout loses the envelope, restore from `origin/sub/AST-1046/AST-1072-conversational-agent-envelope` (or re-graft as in commit `merge(AST-1073): restore AST-1072 envelope…`) — do not re-implement AST-1072.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `CONTACT_ESTELLE_CONFIG` with turn-loop keys; extend `TASK_CONFIG["contact_estelle_turn"]["response_schema"]` with optional `skill_calls` | utils |
| `src/core/contact.py` | Add `run_contact_estelle_turn`; invoke it from `handle_slack_event` after accept + resolve + inbound append; Style D on turn outcomes | core |
| `data/admin/agent_task.json` | Enrich `contact_estelle_turn` prompts: Slack context + ACL skill_calls contract (still Estelle / envelope rules from AST-1072) | data/admin seed |

**Out of plan:** `src/external/slack.py`, Manage Slack UI, `api_slack.py` transport, changing global Estelle `brain_setting`, mutating `BASE_SCHEMA`, new DB transcript tables, astral-faq / activity-summary.

## Stage 1: Config — turn-loop keys + optional `skill_calls` schema

**Done when:** `CONTACT_ESTELLE_CONFIG` exposes the turn-loop keys below; `TASK_CONFIG["contact_estelle_turn"]["response_schema"]` allows optional `skill_calls`; import asserts pass; non-CHAT tasks unchanged.

1. In `src/utils/config.py`, extend the existing `CONTACT_ESTELLE_CONFIG` block (do **not** remove `default_brain_setting` / `task_key` / the `BRAIN_MEDIUM` assert) with:

```python
CONTACT_ESTELLE_CONFIG = {
    "default_brain_setting": "Medium",  # existing; keep assert == BRAIN_MEDIUM
    "task_key": "contact_estelle_turn",
    # Max Slack messages included in live_content (trim from oldest).
    "turn_context_message_limit": 40,
    # Max chars per message text in live_content (truncate with …).
    "turn_context_text_max_chars": 500,
}
```

2. Asserts (next to the existing Medium assert):

```python
assert isinstance(CONTACT_ESTELLE_CONFIG["turn_context_message_limit"], int)
assert CONTACT_ESTELLE_CONFIG["turn_context_message_limit"] > 0
assert isinstance(CONTACT_ESTELLE_CONFIG["turn_context_text_max_chars"], int)
assert CONTACT_ESTELLE_CONFIG["turn_context_text_max_chars"] > 0
```

3. Extend `TASK_CONFIG["contact_estelle_turn"]["response_schema"]` from reply-only to:

```python
"response_schema": {
    "reply": {"type": "str", "required": True},
    "skill_calls": {
        "type": "list",
        "required": False,
        "items_schema": {
            "skill_key": {"type": "str", "required": True},
            "fields": {"type": "object", "required": True},
        },
    },
},
```

⚠️ **Decision — optional `skill_calls` on the CHAT payload (this ticket):** AST-1072 owns envelope performance (`success` \| `failure` \| `concern` + `admin_aside`). ACL invocation is turn-loop scope: the agent may request zero or more allowlisted Contact skills in the same turn. Contact executes them via `run_contact_skill` after a successful envelope parse — never by inventing writes outside `CONTACT_CONFIG["skills"]`.

⚠️ **Decision — trim limits in config, not literals in core:** Context assembly caps live in `CONTACT_ESTELLE_CONFIG` so operators can tune without editing `contact.py`.

## Stage 2: Core — `run_contact_estelle_turn` + hook from `handle_slack_event`

**Done when:** An accepted inbound event (listen on, resolved user when present) runs one Estelle turn: context load → `do_task(contact_estelle_turn)` → `conversational_turn_from_do_task_result` → ACL skill_calls → Slack reply with non-prod prefix + cache append; `debug=True` emits Style D for the turn; listen-off / reject paths still never call `do_task`.

1. In `src/core/contact.py` module docstring, replace the “Estelle turn loop: AST-1046 — not here” line with: turn loop owned here (AST-1073); envelope contract AST-1072.

2. Add imports (lazy `do_task` inside the turn function is OK to avoid import cycles — prefer late import of `do_task` / `conversational_turn_from_do_task_result` from `src.core.agent` inside `run_contact_estelle_turn`, matching other core→agent call sites).

3. Add public helper **above** `handle_slack_event` (public-then-helpers: place with other public Contact APIs):

```python
def run_contact_estelle_turn(
    *,
    channel: str,
    text: str,
    thread_ts: Optional[str] = None,
    message_ts: Optional[str] = None,
    astral_candidate_id: Optional[str] = None,
    candidate_state: Optional[str] = None,
    debug: bool = False,
) -> dict:
    """One Contact Estelle conversational turn (AST-1073).

    Returns a dict with at least:
      ok, outcome, reply, admin_aside, skill_results, slack_post, error
    """
```

4. Behavior (literal order):

   a. **Listen re-check:** If not `slack_listen_enabled()`, return `{"ok": False, "error": "listen_off", ...}` without `do_task` / Slack post. (Defense in depth — `handle_slack_event` already gates.)

   b. **Context:** `ctx = load_slack_conversation_context(channel=channel, thread_ts=thread_ts, debug=debug)`. Build `live_content` as a single string:

      - Header lines: `channel=…`, `thread_ts=…`, `astral_candidate_id=…`, `candidate_state=…`.
      - Section `## Available Contact skills (ACL)` — for each `contact_skills()` entry: `skill_key`, `description`, comma-joined `allowed_paths`. Instruct: only emit `skill_calls` entries whose `skill_key` is listed; `fields` keys must be allowlisted paths; omit `skill_calls` when none.
      - Section `## Conversation` — take the last `CONTACT_ESTELLE_CONFIG["turn_context_message_limit"]` messages from `ctx["messages"]`; each line `[{user or bot_id or "unknown"}] {truncated text}` using `turn_context_text_max_chars`.
      - Section `## Latest inbound` — the current `text` (truncated the same way).

   c. **Candidate raft for tokens:** If `astral_candidate_id` is a non-empty string, `row = get_candidate(astral_candidate_id)` (already imported); build `candidate_data` from `row["candidate_data"]` if present else `{}`. Else `candidate_data = {}`.

   d. **`do_task`:** `import asyncio` at module top if not present. Call:

```python
task_key = CONTACT_ESTELLE_CONFIG["task_key"]
result = asyncio.run(
    do_task(
        task_key,
        live_content=live_content,
        index=astral_candidate_id or channel,
        candidate_data=candidate_data,
        debug=debug,
        store_agent_data=True,
    )
)
turn = conversational_turn_from_do_task_result(result)
```

   e. **Skill calls:** From `result["parsed_response"]` (dict), read optional `skill_calls` (default `[]`). If not a list, treat as `[]`. For each item that is a dict with `skill_key` + `fields` dict: if `astral_candidate_id` is missing/blank, append `{"ok": False, "error": "no_candidate", "skill_key": …}` and continue; else call `run_contact_skill(skill_key, astral_candidate_id=…, fields=fields, debug=debug)` inside try/except — on `ValueError` / other Exception, append `{"ok": False, "error": str(exc), "skill_key": …}` without raising out of the turn. Collect `skill_results`.

   f. **Outbound reply:** Let `reply = turn["reply"]`. Post to Slack only when `turn["success"]` is True **and** `reply` is a non-empty stripped string **and** outcome is `success` or `concern`. Build `reply_thread_ts = thread_ts or message_ts` (nest channel `@` replies under the triggering message when Slack omitted `thread_ts`). Then:

```python
outbound = format_contact_reply_text(reply)
slack_post = contact_post_message(
    channel=channel,
    text=outbound,
    thread_ts=reply_thread_ts,
    debug=debug,
)
```

   Do **not** call `post_contact_reply` here (it posts without cache append). Do **not** put `admin_aside` into the Slack text.

   g. **Admin aside:** When `turn["outcome"] == "concern"` and `admin_aside` is a non-empty string, emit `logger.warning("contact estelle concern aside candidate=%s aside=%s", astral_candidate_id, aside_preview)` with aside truncated to `_TEXT_DEBUG_MAX` — admin-visible via logs, not Slack.

   h. **Debug (only `debug=True`):** After the turn settles, Style D:

      - `debug_index(func="contact.run_contact_estelle_turn", index=1, total=1, identifier=<event channel or candidate id>, outcome=<turn outcome or error>)`
      - `debug_detail` with `outcome=… success=… reply_len=… admin_aside_len=… skill_calls=N skill_ok=M slack_ok=…` (lengths / counts only — no full reply/aside blobs unless passed through `truncate_debug_content`).

   i. **Return** a dict:

```python
{
    "ok": bool(turn["success"]) and error is None,
    "outcome": turn["outcome"],
    "reply": turn["reply"],
    "admin_aside": turn["admin_aside"],
    "skill_results": skill_results,
    "slack_post": slack_post,  # or None if skipped
    "error": result.get("error") if not result.get("success") else None,
}
```

5. Hook into `handle_slack_event` **after** resolve + inbound `append_slack_conversation_message` and **before** the final accept debug block: when `result["accepted"]` is True and `channel` is a non-empty str, call:

```python
turn_out = run_contact_estelle_turn(
    channel=channel,
    text=text,
    thread_ts=event.get("thread_ts"),
    message_ts=msg_ts if isinstance(msg_ts, str) else None,
    astral_candidate_id=result.get("astral_candidate_id"),
    candidate_state=result.get("candidate_state"),
    debug=debug,
)
result["estelle_turn"] = turn_out
```

   Wrap in try/except so a turn failure still returns the accepted ingress result (log exception at ERROR; set `result["estelle_turn"] = {"ok": False, "error": str(exc)}`). Never raise out of the daemon thread uncaught in a way that skips the accept return.

⚠️ **Decision — sync `asyncio.run` on the daemon thread:** `receive_slack_events_http` already acks then runs `handle_slack_event` on a daemon thread (AST-1069). Running `do_task` via `asyncio.run` on that thread keeps the Flask request fast and matches other sync Contact/UI wrappers (`api_intake`, `candidate` paths). Do **not** move ack onto the turn or call `do_task` on the request thread.

⚠️ **Decision — compose `format_contact_reply_text` + `contact_post_message`:** Prefix (AST-1067) + cache append (AST-1070) without double-prefixing. Do not invent a third poster.

⚠️ **Decision — failure / empty reply = no Slack message:** Envelope `failure` or missing reply must not spam Slack; operators still see debug / ERROR logs.

## Stage 3: Prompt seed — context + ACL skill_calls

**Done when:** `data/admin/agent_task.json` row `task_key=contact_estelle_turn` instructs Estelle to use conversation + latest inbound from live_content, emit ternary envelope + optional `skill_calls`, and keep admin asides out of `reply`.

1. Update the existing `contact_estelle_turn` row (do **not** change `agent_id=principal_recruiter_estelle` or mint a new `task_key_uuid`):

   - **system_prompt** (keep AST-1072 envelope rules) and add:
     - User-visible text goes only in `agent_payload.reply`.
     - `admin_aside` only on `concern`, never copied into `reply`.
     - Optional `agent_payload.skill_calls`: list of `{skill_key, fields}` drawn **only** from the ACL section in live_content; `fields` values are strings (or omit nulls); empty / omitted when no save is needed.
     - Prefer one short Slack-appropriate `reply` (no markdown fences around the JSON envelope).

   - **user_prompt** / nocache as needed so live_content (passed as the TASK / live block by `do_task`) is clearly “this turn’s Slack context.” Keep `{$SELECTED_AGENT}` if already present.

2. Do **not** add new TASK_CONFIG keys. Do **not** register Contact skills in `TASK_CONFIG`.

## Self-Assessment

**Scope:** `Single-Component` — Contact core turn orchestration + small config/schema/prompt extensions; consumes AST-1072 `do_task` contract and AST-1043 Contact helpers; no new external/UI modules.

**Conf:** `high` — listen/resolve/context/ACL/post helpers already exist; envelope helper `conversational_turn_from_do_task_result` is shipped; daemon-thread ack pattern already hosts the handler.

**Risk:** `Medium` — a bad turn could post wrong Slack text or write candidate fields via skills; mitigated by listen re-check, ACL path allowlists in `run_contact_skill`, no-post on failure, and debug-gated tracing. Brain override remains AST-1072’s Medium path (not touched here).

## Code rules self-check

- **§1.3 DRY:** Reuse `load_slack_conversation_context`, `run_contact_skill`, `format_contact_reply_text`, `contact_post_message`, `conversational_turn_from_do_task_result` — no second resolver/poster/envelope parser.
- **§2.1 config:** Turn trim limits + task_key from `CONTACT_ESTELLE_CONFIG`; skills ACL remains `CONTACT_CONFIG["skills"]`; no new hardcoded skill key sets in core.
- **§2.4 / §2.6:** No new dispatch batch or candidate state machine transitions in this ticket.
- **§3.3 imports:** UI unchanged (still core-only). Contact may late-import `agent.do_task`; Contact must not import UI. External Slack only via existing Contact helpers.
- **§1.5.1 debug:** New Style D lines only when `debug=True`; lengths/counts in detail lines.
- **§1.1 in-scope:** No Events verify rewrite, no Manage Slack page, no envelope performance schema redesign, no transcript table.

## Execution contract

The plan is binding. Execute stages in order. One commit per stage on the epic worktree, then `git push origin HEAD:sub/AST-1046/AST-1073-contact-estelle-turn-loop`. On ambiguity or codebase drift vs this plan — stop and comment on **parent AST-1046** with the 🛑 Stage N blocked template. Do not invent files outside the Files Changed table.

## Review

| Field | Value |
|-------|-------|
| Status | Code Complete |
| Publish ref | `origin/sub/AST-1046/AST-1073-contact-estelle-turn-loop` |
| Tip | (filled after stage-3 push) |
| Branch | `sub/AST-1046/AST-1073-contact-estelle-turn-loop` |

