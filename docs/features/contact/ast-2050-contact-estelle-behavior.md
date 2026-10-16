# AST-2050 — Contact Estelle behavior

<!-- linear-archive: AST-2050 archived 2026-10-16 -->

## Linear archive (AST-2050)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2050/contact-estelle-behavior  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Estelle currently answers every Slack @mention/DM with a canned "I know who that is" before her real reply, and always buries her reply in a thread under the user's message — even when the user posted top-level, so they have to click into the thread to see it. The recognition line was a testing aid from AST-1668 and now reads as noise. This epic makes Estelle's Slack presence feel natural: she answers the prompt itself, and she replies where the conversation is happening (in-thread only when the user was already in a thread), with the placement controlled by one config setting so Susan can switch to "always thread" or "thread + also send to channel" without a code change.

## Functional scope

1. **No canned recognition reply for bound users.** When a Slack user bound to a candidate @'s or DMs Estelle, the only thing she posts is her actual response to their message (turn reply, command ack/usage, or paste ack) — no "I know who that is" preamble.
2. **Config-driven reply placement —** `thread_response`**.** One Contact setting decides where every Estelle reply to an inbound Slack message lands:
   * `threads_only` (default) — reply in the thread only if the user's message was itself in a thread; a top-level message gets a new top-level post in the same channel/DM.
   * `always_no_share` — always reply in a thread (the user's thread, or a new thread under their top-level message). This is today's behavior.
   * `always_with_share` — same threading as `always_no_share`, and every reply is also shared to the channel (Slack "Also send to channel").
3. **Uniform placement.** Every reply Contact posts in response to an inbound event (Estelle turn reply, command usage/ack, paste-saved ack, failure fallback, unknown-sender reply) follows `thread_response`. Estelle-initiated posts that are not replies (e.g. the meteorite BOT_BLOCKED paste request, which posts top-level by design) are out of scope and unchanged.
4. **Thread anchors unchanged.** Where a command handler stores a Slack anchor (e.g. `/add-job` stamping `estelle_thread_ts` on the meteorite), it still receives the user's thread or message ts — reply placement must not change what gets anchored.
5. **Unbound sender reply (config-driven).** A Slack user not bound to any candidate still gets one reply and no Estelle turn; its text is the config string "Sorry, I don't recognize you, yet.  Let's check with @susan" (replaces "I don't recognize you").
6. **Failure fallback (config-driven).** When Estelle's turn errors or posts nothing, the fallback reply stays; its text is the config string "That didn't work as planned.  Let's ask @susan." (replaces "Heard you — Estelle is listening."). Note: plain-text "@susan" in a Slack message does not notify; a real ping needs Susan's `<@U…>` Slack id in the string — a config-value edit, no code change.

## Component scope

* `src/utils/config.py` — **modified** — `CONTACT_CONFIG` gains the `thread_response` setting (+ import-time assert on its vocabulary); `known_recognition_reply_text` and its assert are removed; unknown-sender and failure-fallback reply strings get their new values.
* `src/external/slack.py` — **modified** — `post_message` can request Slack's reply broadcast ("Also send to channel") on a threaded post.
* `src/core/contact.py` — **modified** — inbound path stops posting the known-recognition reply; all reply sites resolve thread placement + broadcast from `thread_response` through one shared helper and pass it through `contact_post_message`.

## Technical scope

* `src/utils/config.py`: new `CONTACT_CONFIG` key for reply placement, string vocabulary `threads_only | always_with_share | always_no_share`, default `threads_only`, with an import-time assert rejecting any other value. Remove the `known_recognition_reply_text` key and its assert (no remaining reader). Modified values (keys and asserts unchanged): `unknown_recognition_reply_text` → "Sorry, I don't recognize you, yet.  Let's check with @susan"; `hear_ack_reply_text` → "That didn't work as planned.  Let's ask @susan."
* `src/external/slack.py`: modified `post_message` — new optional keyword to request reply broadcast; adds Slack's `reply_broadcast: true` to the `chat.postMessage` body only when a `thread_ts` is also present. Default behavior (no broadcast) unchanged for existing callers (e.g. `src/core/meteorite.py` top-level post).
* `src/core/contact.py`:
  * new private helper that, given the inbound event's `thread_ts` and message `ts`, returns the reply `thread_ts` (or none for top-level) and the broadcast flag per `thread_response`;
  * modified `contact_post_message` — passes the broadcast flag through to `post_message`; cache append keys on the thread actually posted to (top-level reply → channel-level cache key);
  * modified `_handle_slack_event_body` — drops the known-recognition post; hear-ack and paste ack use the helper instead of inline `thread_ts or msg_ts`;
  * modified `run_contact_estelle_turn` (outbound reply step) and `_run_contact_command` (usage + code-mode ack posts) — reply placement via the helper; the handler call in `_run_contact_command` keeps passing the anchor (`thread_ts or message_ts`) unchanged.

## Architectural definition

* **Patterns to reuse**
  * `patt.contact.command-intercept` — command replies keep their registry mode semantics (usage on empty payload, code-mode ack only on ok, agent mode = one turn); only *where* they post changes. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.contact.command-intercept.md>)
    **Change requested (Archie approval):** Arc step 3 says `_handle_slack_event_body` "runs known/unknown recognition first", and Arc step 4 says usage/ack post "in-thread". After this epic, known-recognition no longer posts, and command replies post per `CONTACT_CONFIG["thread_response"]` rather than always in-thread — the pattern text needs to say so.
* **New patterns proposed:** none
* **Applicable statutes**
  * `stat.logging.info.contact` — the one listen info line per accepted event must still fire for bound and unbound senders after recognition is removed. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.contact.md>)
  * `stat.logging.debug` — `Calling post_message` / `Response from …` debug lines in `src/core/contact.py` carry the resolved thread_ts + broadcast flag. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>)

## Acceptance criteria

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

## Open questions

None.

## Resolved questions (Susan's answers, verbatim)

1. **Unbound Slack senders.** Today a Slack user not bound to any candidate gets "I don't recognize you" and nothing else (Estelle can't run a turn without a candidate). Keep that reply, or remove it so unbound users get silence? My recommendation: keep it — it's their only signal that Estelle heard them.
   1. Agree, yes.  But make it "Sorry, I don't recognize you, yet.  Let's check with @susan" and make it a config-driven response.
2. **Hear-ack fallback.** When Estelle's turn errors or returns no reply, Contact posts "Heard you — Estelle is listening." Is that also test scaffolding to remove, or keep it as the failure fallback? My recommendation: keep.
   1. Keep, another response string for "That didn't work as planned.  Let's ask @susan."
3. `always_with_share` **inside an existing thread.** I read "always" as: every reply is threaded *and* also sent to the channel, including when the user was already in a thread. Confirm — or should share apply only when Estelle starts a new thread under a top-level message?
   1. You read it right.  Always thread (for organization), but share to the channel so the user doesn't have to click.

## Proposed child tickets

#### 1: **Natural Estelle replies + thread_response placement - Hedy**

Removes the canned known-recognition reply, sets the new unknown-sender and failure-fallback reply strings, and adds the `thread_response` setting (`threads_only` default / `always_no_share` / `always_with_share`) so every Estelle reply to an inbound Slack message lands per config, with optional "Also send to channel". Does not change Estelle-initiated top-level posts (meteorite BOT_BLOCKED) or what thread anchor command handlers store.
**Citations:** `patt.contact.command-intercept`, `stat.logging.info.contact`, `stat.logging.debug`.
**Scope:**

* `src/utils/config.py` — **modified** — `CONTACT_CONFIG` gains the `thread_response` setting (+ import-time assert on its vocabulary); `known_recognition_reply_text` and its assert are removed; unknown-sender and failure-fallback reply strings get their new values.
* `src/external/slack.py` — **modified** — `post_message` can request Slack's reply broadcast ("Also send to channel") on a threaded post.
* `src/core/contact.py` — **modified** — inbound path stops posting the known-recognition reply; all reply sites resolve thread placement + broadcast from `thread_response` through one shared helper and pass it through `contact_post_message`.
* Technical scope: all items under `## Technical scope` above (config key + assert + removal + two reply-string values; `post_message` broadcast keyword; contact placement helper, `contact_post_message` pass-through + cache key, `_handle_slack_event_body`, `run_contact_estelle_turn` outbound step, `_run_contact_command` usage/ack posts with handler anchor unchanged).
  Estimate: 3

**Monolith check:** Functional scope N=6, children M=1 — intentional. Recognition removal, reply strings, and reply placement edit the same reply block in `_handle_slack_event_body` and the same `CONTACT_CONFIG` block; splitting would put two children on one function and one config dict (scope partition violation) for a \~3-point change.

**Scope partition check:** all three Component scope files and every Technical scope item sit in child 1 only.

---

## Original brief

Let estelle respond naturally to the user's prompt, do not have her auto respond with "I know who that is" or whatever.  That was for testing purposes only.
Also, have Estelle respond in a thread ONLY if the user has @'d her in a thread, otherwise, create a new post (so the user doesn't have to click into the thread to see her response.  Make this a config driven setting for thread_response: threads_only | always_with_share | always_no_share So that she can reply in the thread but also share the comment in the channel.

### Comments

#### chuckles — 2026-10-08T19:19:44.906Z
@susan dispatch blocked — missing:

- **Linear project** on AST-2050 is empty. Children must inherit the parent's project, and I can't guess it. Astral Contact looks like the right one (all scope is `src/core/contact.py` / Slack). Set it, then move back to Todo + Chuckles.

Your three answers are folded into the definition (Functional scope 5–6, AC 13–14), so nothing else is open.

#### chuckles — 2026-10-08T19:11:30.229Z
@susan

1. **Unbound Slack senders.** Today a Slack user not bound to any candidate gets "I don't recognize you" and nothing else (Estelle can't run a turn without a candidate). Keep that reply, or remove it so unbound users get silence? Recommendation: keep.
2. **Hear-ack fallback.** When Estelle's turn errors or returns no reply, Contact posts "Heard you — Estelle is listening." Test scaffolding to remove, or keep as the failure fallback? Recommendation: keep.
3. **`always_with_share` inside an existing thread.** I read "always" as every reply threaded *and* sent to the channel, including when the user was already in a thread. Confirm — or should share apply only when Estelle starts a new thread under a top-level message?

---

_Implementation detail may live in git history on `origin/dev`._
