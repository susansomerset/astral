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
