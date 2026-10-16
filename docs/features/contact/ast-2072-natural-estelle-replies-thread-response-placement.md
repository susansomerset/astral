<!-- linear-archive: AST-2072 archived 2026-10-16 -->

## Linear archive (AST-2072)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2072/natural-estelle-replies-thread-response-placement-contact-estelle  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-2050 — Contact Estelle behavior  
**Blocked by / blocks / related:** parent: AST-2050; related: AST-2055

### Description

## What this implements

Removes the canned known-recognition reply, sets the new unknown-sender and failure-fallback reply strings, and adds the `thread_response` setting (`threads_only` default / `always_no_share` / `always_with_share`) so every Estelle reply to an inbound Slack message lands per config, with optional "Also send to channel". Does not change Estelle-initiated top-level posts (meteorite BOT_BLOCKED) or what thread anchor command handlers store.

## Citations

`patt.contact.command-intercept`, `stat.logging.info.contact`, `stat.logging.debug`.

## Scope

* `src/utils/config.py` — **modified** — `CONTACT_CONFIG` gains the `thread_response` setting (+ import-time assert on its vocabulary); `known_recognition_reply_text` and its assert are removed; unknown-sender and failure-fallback reply strings get their new values.
* `src/external/slack.py` — **modified** — `post_message` can request Slack's reply broadcast ("Also send to channel") on a threaded post.
* `src/core/contact.py` — **modified** — inbound path stops posting the known-recognition reply; all reply sites resolve thread placement + broadcast from `thread_response` through one shared helper and pass it through `contact_post_message`.
* Technical scope: all items under `## Technical scope` above (config key + assert + removal + two reply-string values; `post_message` broadcast keyword; contact placement helper, `contact_post_message` pass-through + cache key, `_handle_slack_event_body`, `run_contact_estelle_turn` outbound step, `_run_contact_command` usage/ack posts with handler anchor unchanged).

Parent `## Technical scope` (all items — this child owns the full slice):

* `src/utils/config.py`: new `CONTACT_CONFIG` key for reply placement, string vocabulary `threads_only | always_with_share | always_no_share`, default `threads_only`, with an import-time assert rejecting any other value. Remove the `known_recognition_reply_text` key and its assert (no remaining reader). Modified values (keys and asserts unchanged): `unknown_recognition_reply_text` → "Sorry, I don't recognize you, yet.  Let's check with @susan"; `hear_ack_reply_text` → "That didn't work as planned.  Let's ask @susan."
* `src/external/slack.py`: modified `post_message` — new optional keyword to request reply broadcast; adds Slack's `reply_broadcast: true` to the `chat.postMessage` body only when a `thread_ts` is also present. Default behavior (no broadcast) unchanged for existing callers (e.g. `src/core/meteorite.py` top-level post).
* `src/core/contact.py`:
  * new private helper that, given the inbound event's `thread_ts` and message `ts`, returns the reply `thread_ts` (or none for top-level) and the broadcast flag per `thread_response`;
  * modified `contact_post_message` — passes the broadcast flag through to `post_message`; cache append keys on the thread actually posted to (top-level reply → channel-level cache key);
  * modified `_handle_slack_event_body` — drops the known-recognition post; hear-ack and paste ack use the helper instead of inline `thread_ts or msg_ts`;
  * modified `run_contact_estelle_turn` (outbound reply step) and `_run_contact_command` (usage + code-mode ack posts) — reply placement via the helper; the handler call in `_run_contact_command` keeps passing the anchor (`thread_ts or message_ts`) unchanged.

## Acceptance criteria

All parent ACs (single child):

 1. **Recognition text gone.** `git grep -n "known_recognition_reply_text\|I know who that is" -- src` returns nothing. Fail: any hit.
 2. **Setting exists with the right default.** `python -c "from src.utils.config import CONTACT_CONFIG as C; print(C['thread_response'])"` prints `threads_only`. Fail: KeyError or any other value. Setting it to any string outside the three values fails at import (assert). Fail: import succeeds with e.g. `"sometimes"`.
 3. **Bound user, one message.** Listen on, a bound user posts top-level `@Estelle hi` in a channel: Slack shows exactly one Estelle message, which is her turn reply — no "I know who that is". In component terms: `handle_slack_event` with a bound user calls `post_message` exactly once for a successful turn. Fail: two posts, or a post with the recognition text.
 4. `threads_only`**, top-level inbound.** Event without `thread_ts`: the `chat.postMessage` body has no `thread_ts` and no `reply_broadcast`. In Slack, the reply appears in the channel, not as "1 reply". Fail: body carries `thread_ts` (= message ts).
 5. `threads_only`**, in-thread inbound.** Event with `thread_ts=T`: body has `thread_ts=T`, no `reply_broadcast`. Fail: top-level post or broadcast set.
 6. `always_no_share`**.** Top-level inbound with `ts=M`: body `thread_ts=M`, no `reply_broadcast`; in-thread inbound: `thread_ts=T`, no `reply_broadcast`. Fail: any top-level post or broadcast.
 7. `always_with_share`**.** Same `thread_ts` as AC 6, and body carries `reply_broadcast: true` for both cases. In Slack the reply shows in the thread and in the channel. Fail: `reply_broadcast` missing.
 8. **Every reply site obeys the setting.** Under `threads_only` with a top-level inbound, each of: Estelle turn reply, `/add-job` usage reply (empty payload), `/add-job` code-mode ack, paste-saved ack, hear-ack fallback — posts with no `thread_ts`. Fail: any of them threaded.
 9. **One placement helper, no per-site logic (negative check).** `grep -n "thread_ts or message_ts\|thread_ts or msg_ts\|reply_thread_ts = event.get" src/core/contact.py` matches only inside the placement helper and the command-handler anchor in `_run_contact_command` (AC 10). Fail: inline placement logic at any reply site — a per-site copy is the wrong shape even if each copy behaves correctly.
10. **Anchor unchanged.** Under `threads_only` with a top-level `@Estelle /add-job <link>` (`ts=M`), `insert_slack_meteorite` receives `thread_ts=M` and the new meteorite's `estelle_thread_ts` is `M`. Fail: `None`/empty anchor.
11. **Broadcast never on top-level.** `slack.post_message(channel=…, text=…, broadcast requested, thread_ts=None)` sends a body without `reply_broadcast`. Fail: `reply_broadcast` present without `thread_ts`.
12. **Listen info line intact.** With debug off, a bound-user turn still emits exactly one `contact listen <event_type> <outcome>` info line. Fail: line missing.
13. **Unbound sender text.** `handle_slack_event` for an unbound Slack user posts exactly one message whose text (after the non-prod prefix) is `CONTACT_CONFIG["unknown_recognition_reply_text"]` == "Sorry, I don't recognize you, yet.  Let's check with @susan", placed per `thread_response`; no Estelle turn runs. Fail: old text, a second post, or a turn.
14. **Failure fallback text.** A bound-user turn that raises (or returns no reply) posts exactly one message whose text is `CONTACT_CONFIG["hear_ack_reply_text"]` == "That didn't work as planned.  Let's ask @susan.", placed per `thread_response`. `git grep -n "Heard you" -- src` returns nothing. Fail: old text present, or no fallback post.

## Boundaries

Single child — no siblings. Does not change Estelle-initiated top-level posts (meteorite BOT_BLOCKED in `src/core/meteorite.py`) or the thread anchor command handlers store. No Manage Slack UI toggle — `thread_response` is config-only.

## Notes for planning

Citations above. Requested canon change (Archie): `patt.contact.command-intercept` Arc steps 3–4 wording ("known/unknown recognition first", "in-thread") — flag in plan, do not edit canon. In-flight [AST-2055](https://linear.app/astralcareermatch/issue/AST-2055) / [AST-2061](https://linear.app/astralcareermatch/issue/AST-2061) (not yet on dev) edits the same three files in other hunks: public-channel gate at the top of `_handle_slack_event_body`, `fetch_channel_type` in `slack.py`, `CONTACT_CONFIG["allowed_channel_types"]`, and removal of `CONTACT_CONFIG["skills"]` entries / `land_calls` in `run_contact_estelle_turn`. Keep edits local to reply sites to minimize merge surface.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### hedy — 2026-10-08T23:50:19.895Z
`origin/sub/AST-2050/AST-2072-estelle-thread-response` @ `a4a7ce600` · §9a clean · ftr dry-run clean (`ftr/AST-2050-estelle-behavior` — spawn `--ftr AST-2050` misses it)

#### radia — 2026-10-08T23:47:55.620Z
[code-rubric] PROCEED (Commit: e9e30e065) placement helper, canon B

#### betty — 2026-10-08T23:44:57.268Z
`origin/sub/AST-2050/AST-2072-estelle-thread-response` @ `e9e30e065` · placement tests + 5 revised

#### hedy — 2026-10-08T23:06:59.131Z
`origin/sub/AST-2050/AST-2072-estelle-thread-response` @ `221def8f6` · AC 1 grep is substring-unsafe (`unknown_…` matches) — see plan `## Review`

#### joan — 2026-10-08T23:05:05.551Z
[plan-rubric] PROCEED (Commit: c968b6df) placement helper, three files

#### hedy — 2026-10-08T23:03:21.174Z
`origin/sub/AST-2050/AST-2072-estelle-thread-response` @ `c968b6dfa` · plan ready, two stages

---

# AST-2072 — Natural Estelle replies + thread_response placement

**Linear:** [AST-2072](https://linear.app/astralcareermatch/issue/AST-2072)
**Parent:** [AST-2050](https://linear.app/astralcareermatch/issue/AST-2050) — Contact Estelle behavior
**Publish ref:** `origin/sub/AST-2050/AST-2072-estelle-thread-response`

Estelle stops posting the canned "I know who that is" before her real reply to a bound Slack user. The unbound-sender reply and the failure fallback get Susan's new wording. A new `CONTACT_CONFIG["thread_response"]` setting decides where every Estelle reply to an inbound Slack message lands. `threads_only` (default) threads only when the user was already in a thread. `always_no_share` always threads, which is today's behavior. `always_with_share` always threads and also sets Slack's "Also send to channel" (`reply_broadcast`). One private helper in `src/core/contact.py` resolves placement for every reply site. `slack.post_message` gains the broadcast keyword. This is the single child of the epic, so it ships parent AC 1–14. It does not change Estelle-initiated top-level posts (meteorite BOT_BLOCKED in `src/core/meteorite.py`) or the thread anchor that command handlers store.

## Scope gate

The ticket's `## Scope` names three files. Every row below is one of them, and every change is a kind its Technical scope names:

- `src/utils/config.py`: the new `thread_response` key and its vocabulary assert; removal of `known_recognition_reply_text` and its assert; new values for `unknown_recognition_reply_text` and `hear_ack_reply_text`.
- `src/external/slack.py`: `post_message` gains an optional broadcast keyword. `reply_broadcast: true` goes into the body only when `thread_ts` is also present.
- `src/core/contact.py`: the new private placement helper; `contact_post_message` passes the broadcast flag through (cache key = thread actually posted to); `_handle_slack_event_body` drops the known-recognition post, and the unknown reply, paste ack, and hear-ack use the helper; the outbound step of `run_contact_estelle_turn` and the usage/ack posts in `_run_contact_command` use the helper; the handler anchor in `_run_contact_command` is unchanged.

Reused as-is (no change): `format_contact_reply_text`, `append_slack_conversation_message`, `_context_cache_key`, `_emit_listen_info`, `_contact_listen_info`, `try_meteorite_apply_paste_from_slack`, `post_contact_reply` (it has no callers and is not a reply site this ticket names), and `src/core/meteorite.py`'s `contact_post_message(..., thread_ts=None)` top-level BOT_BLOCKED post. That post never calls the helper, so it stays top-level under every `thread_response` value.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `CONTACT_CONFIG["thread_response"]` + vocabulary assert. New values for `unknown_recognition_reply_text` / `hear_ack_reply_text`. Remove `known_recognition_reply_text` + its assert. | utils |
| `src/external/slack.py` | `post_message(..., reply_broadcast=False)` adds `reply_broadcast: true` only inside the `thread_ts` branch. | external |
| `src/core/contact.py` | New `_contact_reply_placement`. `contact_post_message` gains `reply_broadcast` (debug line + pass-through). Reply sites in `run_contact_estelle_turn`, `_run_contact_command`, `_handle_slack_event_body` use the helper. Known-recognition post removed. | core |

No other file is touched. Tests and the bible are Betty's (see **Test impact**).

## Stage 1: Config values + Slack broadcast keyword (no behavior change)

**Done when:** `python3 -c "from src.utils.config import CONTACT_CONFIG as C; print(C['thread_response'])"` prints `threads_only`. Temporarily setting the value to `"sometimes"` makes the import fail with `AssertionError`, and that edit is reverted before commit. `post_message` still sends the same body for every existing caller. `known_recognition_reply_text` is still present in this stage because `contact.py` still reads it until Stage 2.

1. In `src/utils/config.py`, inside `CONTACT_CONFIG`, replace these two lines:

   ```python
       # AST-1101: fallback Slack text when Contact accepts @/DM but Estelle turn posts nothing.
       "hear_ack_reply_text": "Heard you — Estelle is listening.",
   ```

   with:

   ```python
       # AST-1101 / AST-2072: fallback Slack text when Contact accepts @/DM but Estelle's turn
       # posts nothing (turn raised, failed, or returned no reply).
       "hear_ack_reply_text": "That didn't work as planned.  Let's ask @susan.",
   ```

   Keep the two spaces after each period exactly as written. They are Susan's verbatim wording, and AC 14 compares the string exactly.

2. In `src/utils/config.py`, inside `CONTACT_CONFIG`, change only the value of `unknown_recognition_reply_text` from `"I don't recognize you"` to `"Sorry, I don't recognize you, yet.  Let's check with @susan"`. Keep the double space after `yet.` and add no trailing period, per Susan's verbatim answer and AC 13. Leave the `known_recognition_reply_text` line and the `# AST-1668` comment above it alone in this stage. Stage 2 removes them.

3. In `src/utils/config.py`, inside `CONTACT_CONFIG`, insert immediately **after** the `"unknown_recognition_reply_text": …,` line and **before** the `# Environ name contracts` comment:

   ```python
       # AST-2072: where every Estelle reply to an inbound Slack message lands.
       #   threads_only      — in-thread only when the user posted in a thread; else a new top-level post.
       #   always_no_share   — always in a thread (the user's thread, or a new one under their message).
       #   always_with_share — always_no_share + Slack "Also send to channel" (reply_broadcast).
       # Estelle-initiated posts (meteorite BOT_BLOCKED) are not replies and ignore this.
       "thread_response": "threads_only",
   ```

4. In `src/utils/config.py`, immediately **after** the line
   `assert isinstance(CONTACT_CONFIG["unknown_recognition_reply_text"], str) and CONTACT_CONFIG["unknown_recognition_reply_text"].strip()`
   add:

   ```python
   assert CONTACT_CONFIG["thread_response"] in ("threads_only", "always_no_share", "always_with_share"), CONTACT_CONFIG["thread_response"]
   ```

5. In `src/external/slack.py`, change `post_message` to the following. Only the signature, docstring, and the `thread_ts` branch change. Token, request, timeout, and return lines stay as they are.

   ```python
   def post_message(
       *,
       channel: str,
       text: str,
       thread_ts: Optional[str] = None,
       reply_broadcast: bool = False,
   ) -> dict:
       """POST chat.postMessage; raise on HTTP/transport failure. Does not log.

       ``reply_broadcast`` ("Also send to channel") only applies to a threaded post;
       without ``thread_ts`` it is ignored so a top-level post never carries it.
       """
       require_controlled_external_io("slack.post_message")
       token = os.environ[CONTACT_CONFIG["bot_token_env"]]
       body: Dict[str, Any] = {"channel": channel, "text": text}
       if thread_ts:
           body["thread_ts"] = thread_ts
           if reply_broadcast:
               body["reply_broadcast"] = True
       # … unchanged requests.post / raise_for_status / return …
   ```

   ⚠️ **Decision:** The keyword is named `reply_broadcast`, the same as Slack's `chat.postMessage` field, and `contact_post_message` uses the same name in Stage 2. One name end to end means nothing needs translating. Nesting it under `if thread_ts:` is what makes AC 11 hold. The default `False` leaves `meteorite.py`'s top-level call and every other existing caller unchanged.

6. `python3 -m py_compile src/utils/config.py src/external/slack.py`, then run the Done-when checks above.

## Stage 2: Placement helper, reply sites, recognition removal

**Done when:** With the default `threads_only`, a bound user's top-level `@Estelle hi` produces exactly one `post_message` call (the turn reply) with no `thread_ts` and no `reply_broadcast`. An unbound user gets exactly one post with the new unknown text. `git grep -n "known_recognition_reply_text\|I know who that is\|Heard you" -- src` returns nothing. The AC 9 grep matches only the helper, the `_run_contact_command` handler anchor, and the pre-existing paste-recovery lookup anchor described in step 7.

1. In `src/core/contact.py`, insert this function immediately **above** the `@_with_log_debug` decorator of `contact_post_message`:

   ```python
   def _contact_reply_placement(
       thread_ts: Optional[str], message_ts: Optional[str]
   ) -> Tuple[Optional[str], bool]:
       """Resolve ``(reply thread_ts, reply_broadcast)`` for a reply to one inbound Slack message.

       Driven by ``CONTACT_CONFIG["thread_response"]`` (AST-2072); ``None`` thread_ts = top-level post.
       The single placement rule for every Contact reply site — no per-site ``thread_ts or …`` copies.
       """
       # Read per call (not at import) so a config change applies without a restart path.
       mode = CONTACT_CONFIG["thread_response"]
       if mode == "threads_only":
           # Thread only when the user was already in one; a top-level message gets a top-level reply.
           return (thread_ts or None, False)
       # always_no_share / always_with_share: the user's thread, or a new thread under their message.
       return (thread_ts or message_ts or None, mode == "always_with_share")
   ```

   ⚠️ **Decision:** The helper returns a `(thread_ts, reply_broadcast)` tuple, not a kwargs dict for `**` splatting. That is exactly what the Technical scope describes ("returns the reply thread_ts … and the broadcast flag"), and call sites stay greppable for `thread_ts=` / `reply_broadcast=`. The `or None` turns an empty-string `thread_ts` into a real top-level post instead of passing `""` through.

2. In `src/core/contact.py`, change `contact_post_message`:
   - Add `reply_broadcast: bool = False,` to the keyword-only parameters, right after `thread_ts: Optional[str] = None,`.
   - Replace the debug call and the `post_message` call with:

     ```python
         logger.debug(
             "Calling post_message: [channel=%r, thread_ts=%r, reply_broadcast=%s, text=%r]",
             channel, thread_ts, reply_broadcast, text,
         )
         resp = post_message(
             channel=channel, text=text, thread_ts=thread_ts, reply_broadcast=reply_broadcast
         )
     ```
   - Leave the cache append exactly as it is (`thread_ts=thread_ts`). That argument is already the thread the message was posted to. A top-level reply (`thread_ts=None`) appends under the channel-level key `(channel, "")`, the same key the inbound top-level message warmed. This satisfies the Technical scope's "cache append keys on the thread actually posted to", so the line needs no edit. Add this comment directly above the `append_slack_conversation_message(` call:

     ```python
             # Key on the thread actually posted to — a top-level reply lands on (channel, "").
     ```

3. In `src/core/contact.py`, `run_contact_estelle_turn`, step `# f. Outbound reply`: replace

   ```python
           reply_thread_ts = thread_ts or message_ts
           outbound = format_contact_reply_text(reply_for_slack)
           slack_post = contact_post_message(
               channel=channel,
               text=outbound,
               thread_ts=reply_thread_ts,
               debug=debug,
           )
   ```

   with

   ```python
           reply_ts, reply_broadcast = _contact_reply_placement(thread_ts, message_ts)
           outbound = format_contact_reply_text(reply_for_slack)
           slack_post = contact_post_message(
               channel=channel,
               text=outbound,
               thread_ts=reply_ts,
               reply_broadcast=reply_broadcast,
               debug=debug,
           )
   ```

   Nothing else in `run_contact_estelle_turn` changes. The context load (`load_slack_conversation_context(..., thread_ts=thread_ts)`) still uses the inbound `thread_ts`. The source-ref loop over `(message_ts, thread_ts, channel)` is not reply placement.

4. In `src/core/contact.py`, `_run_contact_command`: replace the line

   ```python
       reply_thread_ts = thread_ts or message_ts
   ```

   with

   ```python
       # Handler anchor stays the inbound thread (or message) so later nags find this thread,
       # independent of where thread_response puts our replies (AST-2072 AC 10).
       anchor_ts = thread_ts or message_ts
       reply_ts, reply_broadcast = _contact_reply_placement(thread_ts, message_ts)
   ```

   Then:
   - In the empty-payload `contact_post_message(...)` (usage reply), replace `thread_ts=reply_thread_ts,` with `thread_ts=reply_ts,` and add `reply_broadcast=reply_broadcast,` on the next line.
   - In the handler `logger.debug("Calling %s: [...thread_ts=%r...]", ...)`, replace the argument `reply_thread_ts` with `anchor_ts`.
   - In `handler(astral_candidate_id, payload, source_id=source_id, thread_ts=reply_thread_ts, debug=debug)`, replace `thread_ts=reply_thread_ts` with `thread_ts=anchor_ts`.
   - In the code-mode ack `contact_post_message(...)`, replace `thread_ts=reply_thread_ts,` with `thread_ts=reply_ts,` and add `reply_broadcast=reply_broadcast,` on the next line.
   - The agent-mode `run_contact_estelle_turn(..., thread_ts=thread_ts, message_ts=message_ts, ...)` call stays unchanged. It resolves placement itself in step 3.

   After this step, no `reply_thread_ts` identifier remains in `_run_contact_command`.

   ⚠️ **Decision:** The variable is renamed from `reply_thread_ts` to `anchor_ts`. Under `threads_only` it is no longer the reply thread, and leaving the old name would mislabel the AC 10 anchor. Its value (`thread_ts or message_ts`) is unchanged, so `insert_slack_meteorite` still receives `thread_ts=M` for a top-level `/add-job` (AC 10).

5. In `src/core/contact.py`, `_handle_slack_event_body`, replace the whole block from the comment `# AST-1668: known/unknown recognition, then Estelle only when bound.` down to (but not including) the line `        else:` that follows `_emit_listen_info(result, etype, channel, result["estelle_turn"])`. That is, replace the recognition `if resolve_ok:` post block and the `if resolve_ok and not known:` header/body with:

   ```python
       # AST-1668 / AST-2072: unbound sender gets the unknown reply only; a bound sender gets no
       # recognition post — Estelle's own reply (turn / command / paste ack / hear-ack) is the answer.
       if result.get("accepted") and isinstance(channel, str) and channel:
           user_ok = isinstance(user, str) and bool(user.strip())
           resolve_ok = user_ok and not result.get("resolve_error")
           known = isinstance(result.get("astral_candidate_id"), str) and bool(
               result.get("astral_candidate_id")
           )
           # One placement decision for every reply this event can produce (thread_response).
           reply_ts, reply_broadcast = _contact_reply_placement(
               event.get("thread_ts"), msg_ts if isinstance(msg_ts, str) else None
           )

           # Unknown bound miss: unknown reply only — do not run Estelle as if bound.
           if resolve_ok and not known:
               try:
                   result["recognition_post"] = contact_post_message(
                       channel=channel,
                       text=format_contact_reply_text(
                           str(CONTACT_CONFIG["unknown_recognition_reply_text"])
                       ),
                       thread_ts=reply_ts,
                       reply_broadcast=reply_broadcast,
                       debug=debug,
                   )
               except Exception as exc:
                   logger.exception(
                       "%s | contact recognition post\n  %s: %s\n  Recognition reply was not posted",
                       result.get("astral_candidate_id") or "-", type(exc).__name__, exc,
                   )
                   result["recognition_post"] = {"ok": False, "error": str(exc)}
               result["estelle_turn"] = {
                   "ok": True,
                   "outcome": "unrecognized",
                   "skipped": True,
               }
               _emit_listen_info(result, etype, channel, result["estelle_turn"])
   ```

   The `else:` branch that follows (command / paste / turn / hear-ack) keeps its current structure, with steps 6 below as its only edits.

   ⚠️ **Decision:** The unknown-sender post moves inside the existing `if resolve_ok and not known:` branch, and the `text_key` ternary goes away. Only one text key is left, so there's nothing to choose between. The `result["recognition_post"]` key and the exception log wording stay the same, since they still describe the unknown-recognition reply, and keeping them avoids churn in the result shape existing tests read. Behavior when resolve raised (`resolve_error`) is unchanged: no recognition post, and the flow falls to the `else:` branch as today.

   ⚠️ **Decision:** Placement is resolved once per event, right after `known`, and reused by the unknown reply, paste ack, and hear-ack. All three answer the same inbound message, so one call gives one answer. Calling the helper again at each site would repeat the same arguments three times for no behavioral difference. Command and turn replies resolve inside `_run_contact_command` / `run_contact_estelle_turn` (steps 3–4), because those functions receive `thread_ts` / `message_ts` and not the resolved pair.

6. In the same `else:` branch of `_handle_slack_event_body`:
   - **Paste ack:** delete the three lines

     ```python
                       reply_thread_ts = event.get("thread_ts")
                       if not reply_thread_ts and isinstance(msg_ts, str):
                           reply_thread_ts = msg_ts
     ```

     and in that block's `contact_post_message(...)`, replace `thread_ts=reply_thread_ts,` with `thread_ts=reply_ts,` and add `reply_broadcast=reply_broadcast,` on the next line. The literal ack text `"Got it — pasted job description saved for review."` is unchanged.
   - **Hear-ack:** delete the same three `reply_thread_ts = event.get("thread_ts")` / `if not reply_thread_ts …` / `reply_thread_ts = msg_ts` lines in the hear-ack `try:` block, and in its `contact_post_message(...)` replace `thread_ts=reply_thread_ts,` with `thread_ts=reply_ts,` and add `reply_broadcast=reply_broadcast,` on the next line.
   - Do **not** touch the cache warm above (`append_slack_conversation_message(..., thread_ts=event.get("thread_ts"), ...)`). It keys the inbound message, not a reply.

   After this step, `rg -n "reply_thread_ts" src/core/contact.py` returns nothing.

7. In `src/utils/config.py`:
   - Delete the line `"known_recognition_reply_text": "I know who that is",`.
   - Replace the comment `# AST-1668: recognition replies after resolve (known bind vs unbound Slack user).` with `# AST-1668 / AST-2072: reply to an unbound Slack sender (bound senders get no recognition post).`
   - Delete the line `assert isinstance(CONTACT_CONFIG["known_recognition_reply_text"], str) and CONTACT_CONFIG["known_recognition_reply_text"].strip()`.

   ⚠️ **Decision (AC 9 grep and the paste-recovery anchor):** The literal AC 9 grep (`thread_ts or message_ts\|thread_ts or msg_ts\|reply_thread_ts = event.get`) will also match the existing `anchor = (thread_ts or message_ts or "").strip()` in `try_meteorite_apply_paste_from_slack`. That line is the BOT_BLOCKED paste-recovery **lookup** anchor (`find_meteorite_for_estelle_thread`). It is not a reply site and does not decide where anything posts, so it is the same kind of line as the `_run_contact_command` handler anchor AC 9 already allows. `try_meteorite_apply_paste_from_slack` is not in this ticket's Technical scope, so it stays untouched. AC 9's intent (no inline *placement* logic at any reply site) holds. The expected grep hits after Stage 2 are exactly three: the helper's return line, `anchor_ts = thread_ts or message_ts` in `_run_contact_command`, and the paste-recovery lookup anchor.

8. `python3 -m py_compile src/core/contact.py src/utils/config.py src/external/slack.py`, then:
   - `git grep -n "known_recognition_reply_text\|I know who that is\|Heard you" -- src` → no output (AC 1, AC 14).
   - `rg -n "reply_thread_ts" src/core/contact.py` → no output.
   - `grep -n "thread_ts or message_ts\|thread_ts or msg_ts\|reply_thread_ts = event.get" src/core/contact.py` → exactly the three lines named in step 7's decision.
   - `python3 -c "from src.utils.config import CONTACT_CONFIG as C; print(C['thread_response'], '|', C['unknown_recognition_reply_text'], '|', C['hear_ack_reply_text'])"` prints `threads_only | Sorry, I don't recognize you, yet.  Let's check with @susan | That didn't work as planned.  Let's ask @susan.`

## AC map

| AC | Where |
|----|-------|
| 1 | Stage 2 step 5 (post removed), step 7 (key + assert removed) |
| 2 | Stage 1 steps 3–4 |
| 3 | Stage 2 step 5: bound path makes no recognition post; turn reply is the only post |
| 4–7 | Stage 2 step 1 (helper rules) + Stage 1 step 5 (`reply_broadcast` in body) + step 3 (turn reply passes both) |
| 8 | Stage 2 steps 3 (turn), 4 (usage + code ack), 6 (paste ack + hear-ack) |
| 9 | Stage 2 steps 1, 4, 6 + step 7 decision (expected grep hits) |
| 10 | Stage 2 step 4: `anchor_ts = thread_ts or message_ts` feeds the handler |
| 11 | Stage 1 step 5: broadcast nested under `if thread_ts:` |
| 12 | Unchanged `_emit_listen_info` calls on both bound and unbound paths (Stage 2 step 5 keeps the unbound one) |
| 13 | Stage 1 step 2 + Stage 2 step 5 |
| 14 | Stage 1 step 1 + Stage 2 step 6 (hear-ack placement) |

## Canon notes

- **`patt.contact.command-intercept`, change requested (Archie): flagged, not edited.** After this ticket, Arc step 3's "`_handle_slack_event_body` runs known/unknown recognition first" no longer matches the code. Only an unbound sender gets a recognition-style reply, and a bound sender gets none. Arc step 4's "usage … in-thread" and "ack … in-thread" become "per `CONTACT_CONFIG["thread_response"]` (via `_contact_reply_placement`)". Data coupling's "`thread_ts`, which is the reply thread (`thread_ts or message ts`)" should read "the inbound thread anchor (`thread_ts or message ts`), independent of reply placement". This plan does not edit canon. The wording change is Archie's call.
- **`stat.logging.info.contact`:** No change to `_emit_listen_info` / `_contact_listen_info`. Bound users still get one listen line from the shared tail. Unbound users still get one from the `unrecognized` branch (AC 12).
- **`stat.logging.debug`:** `contact_post_message`'s `Calling post_message` line now carries the resolved `thread_ts` and `reply_broadcast` (Stage 2 step 2), and every reply site goes through it. No call site checks a debug flag. `slack.post_message` stays non-logging (`external` layer, existing docstring contract).

## Notes

- Susan's two new strings contain plain-text `@susan`. In Slack `chat.postMessage` text, a real user ping needs `<@U…>` markup, so plain `@susan` shows as text and does not notify. The strings ship verbatim per the resolved questions. Turning them into a real mention would be a config-value edit later and is not part of this ticket.
- In-flight AST-2055 / AST-2061 edit other hunks of the same three files (public-channel gate at the top of `_handle_slack_event_body`, `fetch_channel_type`, `allowed_channel_types`, `skills` / `land_calls`). Every edit here stays at reply sites, the recognition block, `post_message`'s body build, and the reply-text keys. The new config key sits next to the reply-text keys, not near `skills`.

## Test impact (Betty — informational, not this plan's work)

`tests/component/core/test_contact.py` and `tests/component/utils/test_config.py` reference the recognition/hear-ack texts and/or the always-threaded reply shape, and will need updating for removed `known_recognition_reply_text`, the new string values, and `threads_only` top-level placement.

## Execution contract

The plan is binding. Execute steps in order within a stage and stages in order. Do not add files, keys, or helpers beyond the plan. If a step is ambiguous, a referenced line has drifted, or a Done-when check fails when executed literally, stop and post on the parent issue:

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

## Estimate

Confirm Chuckles estimate: 3 — agree


## Joan validate

[plan-rubric]
**Ticket:** AST-2072
**Overall:** APPROVED
**Corpus:** 2d1b73da19cf1d14276e5c26f52b37aa8047d159
**Publish ref:** `origin/sub/AST-2050/AST-2072-estelle-thread-response` @ `c968b6dfab648de9161be48d3f0b6e5d2fbb379a`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.contact.command-intercept | B | | Intercept ordering, modes, and `anchor_ts` preserved; Arc 3–4 wording lags until Archie (plan Canon notes). |
| stat.logging.info.contact | A | | |
| stat.logging.debug | A | | |

## Traceability

AC1→S2.5,7 · AC2→S1.3–4 · AC3→S2.5 · AC4–7→S2.1,S1.5,S2.3 · AC8→S2.3–4,6 · AC9→S2.1,4,6,7 · AC10→S2.4 · AC11→S1.5 · AC12→S2.5 · AC13→S1.2,S2.5 · AC14→S1.1,S2.6 · Parent Purpose/Functional scope 1–6→Stages 1–2 + AC map; no orphan stages.

## Findings

- **acceptable** · Plan `## Scope gate` / Files Changed · Three-file footprint matches ticket `## Scope` and parent Component/Technical scope; meteorite top-level post explicitly out of scope.
- **acceptable** · Stage 1 / Stage 2 ordering · Staged removal of `known_recognition_reply_text` avoids half-migrated config reads; Done-when checks are executable.
- **discuss** · AC 9 vs plan step 7 · Parent AC 9 text names two allowed grep sites; plan expects a third hit (`try_meteorite_apply_paste_from_slack` lookup anchor, not placement). Intent matches AC 9; if Betty keys tests to the two-site literal, align AC wording or test expectation with the carve-out in plan step 7.
- **acceptable** · `## Canon notes` · `patt.contact.command-intercept` drift flagged for Archie, not edited in-flight — matches parent Architectural definition.

## R6 (summary)

Definition fidelity, DRY, and scope: no creep into AST-2055/AST-2061 hunks (plan Notes). Self-assessment: Estimate confirm 3 is proportionate; Decision callouts are specific. No `!!-NONE` gaps.

**Gate:** Plan Ready · assignee Joan · 0 completed Plan Discuss rounds.

context_tokens≈28000

---

[plan-rubric] PROCEED (Commit: c968b6df) placement helper, three files

## Review

Built on `origin/sub/AST-2050/AST-2072-estelle-thread-response`:

- `08074ef9d` code(AST-2072): Stage 1 — `thread_response` config + assert, new reply strings, `post_message` `reply_broadcast`
- `134981e6d` code(AST-2072): Stage 2 — `_contact_reply_placement`, known-recognition post removed, every reply site per `thread_response`

Build notes:

- **AC 1 grep is substring-unsafe.** `known_recognition_reply_text` is a substring of `unknown_recognition_reply_text` (which AC 13 keeps), so the literal `git grep -n "known_recognition_reply_text\|I know who that is" -- src` still prints the three `unknown_…` lines. Whole-word `git grep -nw "known_recognition_reply_text" -- src` returns nothing, and `I know who that is` / `Heard you` return nothing. Tests should match on the whole word.
- AC 9 grep hits are exactly the three named in Stage 2 step 7's decision: the helper's return line, `anchor_ts` in `_run_contact_command`, and the paste-recovery lookup anchor.
- Ruff: no new findings beyond the `Optional`/`Tuple` annotation style on the helper's signature, which matches every other signature in `contact.py`.
- `origin/ftr/AST-2050` is not published yet; `validate-sub-log.sh --stage=build` was scoped against `dev` instead (status=ok).


## Radia review

[code-rubric]
**Ticket:** AST-2072
**Publish ref:** `e9e30e065de6a828d7ef92143f71cf308b3e2ff8` (`origin/sub/AST-2050/AST-2072-estelle-thread-response`)
**Corpus:** `9b1648f5f15106be183d31aadfb04054c937378f`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.contact.command-intercept | B | | Arc 3–4 / Data coupling text still describe known+unknown recognition and “in-thread” replies; code matches ticket (unknown-only recognition, `_contact_reply_placement`, `anchor_ts` for handler). |
| stat.logging.info.contact | A | | |
| stat.logging.debug | A | | |

## Column diff vs plan stage

(aligned) — Joan: `patt.contact.command-intercept` B, `stat.logging.info.contact` A, `stat.logging.debug` A.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

- **Cross-ticket product on publish ref** · `git log` / three-dot diff vs `origin/dev` · Commit `9ac088ef7` (`resync(tests): merge origin/dev (non-test paths only)`) carries **AST-2061-class** product outside AST-2072’s three-file plan: `src/core/meteorite.py` (sanitize, pinhole removals), `src/utils/config.py` (`allowed_channel_types`, empty `skills`, `_CONTACT_PINHOLE_HANDLERS`), `src/core/contact.py` (public-channel gate, `_unwrap_slack_links`, skill_calls removal), `src/external/slack.py` (`fetch_channel_type`), `requirements.txt` (nh3). AST-2072’s own code commits (`08074ef9d`, `134981e6d`) stay within the planned footprint. **@susan:** For single-child epic UAT, is this composite sub tip intentional, or should 2061 product ride only on its own sub before `ftr/AST-2050`? **Default:** Treat as intentional combined Contact slice for parent UAT; parent UAT notes should list which sibling behaviors ship on this ref.

- **Parent AC 1 grep vs tests** · Linear AC 1 vs `tests/component/core/test_contact.py` · Parent AC uses substring `known_recognition_reply_text`, which still matches `unknown_recognition_reply_text`. Tests correctly use `\bknown_recognition_reply_text\b`. **Default:** Keep tests as-is; adjust parent AC wording on next definition touch to whole-word grep (build notes already flag this).

### advisory

- **sibling test carry:** `docs/features/contact/ast-1517-create-contact-meteorite.md`, `tests/component/core/test_candidate.py`, `test_tracker.py`, `tests/component/data/database/test_artifacts.py`, `test_rubric_vectors.py`, `tests/component/ui/api/test_api_companies.py`, `tests/component/frontend/components/test_CompanyDetailModal.test.tsx`, `test_JobAnalysisReportModal.test.tsx`, `docs/test-bible/core/candidate.md`, `tracker.md`, `data/database/*`, `frontend/components.md`, `ui/api/api_companies.md` — from `merge-tests` / `origin/tests`, not AST-2072 product scope.
- **Plan fidelity (2072 hunks):** Stage 1–2 behavior matches the issue doc: `_contact_reply_placement`, helper-only + `anchor_ts` + paste-recovery lookup for AC 9 grep, `reply_broadcast` nested under `thread_ts`, known-recognition post removed, reply strings verbatim, `contact_post_message` cache comment and pass-through.
- **AC 11:** `post_message` ignores `reply_broadcast` without `thread_ts`; covered in `tests/component/external/test_slack.py` (`TestAst2072PostMessageReplyBroadcast`).
- **Canon doc lag:** `patt.contact.command-intercept` Arc steps 3–4 and Data coupling `thread_ts` wording remain stale until Archie’s requested edit (plan Canon notes; not in-flight on this ticket).

## What's solid

- Single placement helper wired through turn, command usage/ack, unknown reply, paste ack, and hear-ack; bound path no longer double-posts recognition.
- Listen info: `_emit_listen_info` on unrecognized and on completed turn/command paths unchanged in structure.
- Debug: `contact_post_message` logs resolved `reply_broadcast` without `if debug` gating at the call site.

## Recommended actions (downstream — not executed in this session)

- Chuckles: append this artifact to `docs/features/contact/ast-2072-natural-estelle-replies-thread-response-placement.md`, commit `docs(AST-2072): Radia review — clean`, push sub ref, post slim upshot `--as radia`, move to **Review Posted**.
- If Susan rejects the 2061 composite on this sub: revert or re-base the `9ac088ef7` non-test paths before **User Testing** / `ftr` rollup (product decision above).
- Archie: schedule `patt.contact.command-intercept` Arc/Data coupling refresh when convenient.

context_tokens≈52000

## Resolution

2026-10-08 — resolve pass on Radia review (`d21ab82e7`, Overall CLEAN). No product change.

- **fix-now:** none.
- **discuss #1 (cross-ticket AST-2061 product on publish ref): false alarm, no action.** `_unwrap_slack_links`, `allowed_channel_types`, `fetch_channel_type`, `_CONTACT_PINHOLE_HANDLERS`, and `nh3` in `requirements.txt` are all already on `origin/dev`. They showed up in the three-dot diff only because the tests resync `9ac088ef7` is not a dev-ancestry merge. Verified on the synced tip: `origin/dev` is an ancestor of HEAD, and `git diff origin/dev HEAD -- src` is three files (+75/−41), line-for-line identical to `git diff 08074ef9d^ 134981e6d -- src` (AST-2072's two code commits). Chuckles confirmed the same independently.
- **discuss #2 (parent AC 1 substring grep): Radia's default taken.** Tests keep the whole-word `\bknown_recognition_reply_text\b` match. Parent AC 1 wording is Archie's to adjust on the next definition touch.
- **advisory:** sibling test carry and plan-fidelity notes are informational only. The `patt.contact.command-intercept` Arc 3–4 / Data coupling refresh stays with Archie (plan Canon notes).
