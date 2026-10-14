# AST-2211 — Show and save handlers, channel lookup, threaded history

**Linear:** [AST-2211](https://linear.app/astralcareermatch/issue/AST-2211)
**Parent:** [AST-2206](https://linear.app/astralcareermatch/issue/AST-2206) — Contact /draft-<context> skills with /save- and /show-
**Publish ref:** `origin/sub/AST-2206/AST-2211-show-save-handlers-threaded-history`

This ticket ships the data-side pieces the epic's Contact wiring (#3, [AST-2212](https://linear.app/astralcareermatch/issue/AST-2212)) calls. These are three things in `src/core/candidate.py` and one in `src/external/slack.py`:

- A reverse lookup from a Slack channel id to the one candidate whose `contact.slack_channel_id` names it.
- The `/show-<context>` handler. It reads the current saved body (read-current) and replies with it, or with a "nothing saved yet" line.
- The `/save-<context>` handler. It sanitizes the text through the existing Contact `nh3` helper, rejects an empty result, and inserts a new artifact version through `save_candidate_data`. Identical-to-current is a no-op (write-operative). It replies with an ack.
- An opt-in `include_thread_replies` mode on `fetch_full_conversation_history`. It also pulls each thread's replies, in chronological order. Each message keeps its `user` poster field. With the mode off, output is byte-for-byte what it is today, so the admin channel snapshot (AST-1787, ticket AC 4) is unaffected.

Nothing in this ticket calls the handlers or the threaded fetch. #3's runner passes `artifact_key=` and resolves the channel's candidate. #3's draft handler calls the fetch with the flag on.

## Scope gate

The ticket's `## Scope` names two files. Every row below is one of them.

- `src/core/candidate.py`: the channel→candidate reverse lookup and the `/show-` and `/save-` command handlers. Also, by Technical scope: the show handler's "nothing saved yet" line and the save handler's ack reply text. Updating the module docstring inventory and the `src.utils.config` import list documents and enables the same change in the same file.
- `src/external/slack.py`: the opt-in thread-reply mode on the full channel history fetch. The module docstring inventory line is updated to match.

**Not in this ticket:** `src/core/contact.py` (runner `payload_optional` / `artifact_key=` pass-through, channel resolution, refusal, `/draft-` handler, and draft-thread routing are all #3). Also out: `src/utils/config.py` and `data/admin/agent_task.json` (#1, landed). No config text is added. The AST-2210 plan flagged that #1 adds no config text for the show "nothing saved yet" line or the save ack. Parent Technical scope places both strings in the `src/core/candidate.py` handler bullets, so they live there as module constants (see Stage 2 decision).

## Contract with #1 (landed) and #3

From the AST-2210 plan (fixed there; spelled the same here):

| Verb | Handler (dotted path in config) | Pinhole kind |
|------|---------------------------------|--------------|
| `show-` | `src.core.candidate.contact_command_show_context` | `read artifact` |
| `save-` | `src.core.candidate.contact_command_save_context` | `write artifact` |

- **Handler signature** (the runner's call shape plus #1's `artifact_key=`): `(candidate_id, payload, *, source_id, thread_ts=None, artifact_key=None, debug=False) -> dict`. It returns `{ok, meteorite_id, error, reply_text}` like `tracker.contact_command_check_status`. `meteorite_id` is always `None`. The runner posts `reply_text` in code mode.
- `candidate_id` is whatever #3 passes. Once #3 lands, that is the channel's mapped candidate, not the sender's. These handlers act on the id they are given.
- `show-` entries are `payload_optional`, so the handler ignores `payload`. `save-` entries are not, so the runner's empty-payload usage reply covers ticket AC 7 (the parent's AC 7) before the handler runs. The handler separately rejects a payload that is empty **after** sanitize.

⚠️ **Decision: lookup function name and return.** `get_candidate_id_for_slack_channel(channel_id, *, debug=False) -> Optional[str]`. It mirrors `get_candidate_id_for_query` and returns an id only on a unique hit. #3 calls it by this name.

⚠️ **Decision: threaded-fetch flag name.** `fetch_full_conversation_history(*, channel, include_thread_replies=False)`. #3 calls it with `include_thread_replies=True`. The existing caller, `get_admin_slack_channel_snapshot` in `src/core/contact.py`, is not touched, so it keeps the default `False`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/slack.py` | Module docstring inventory: names the opt-in thread replies. `fetch_full_conversation_history` gains a keyword-only `include_thread_replies: bool = False`. When it is `True`, the function pulls `conversations.replies` for every message with `reply_count > 0`, drops each thread's echoed parent, and merges everything into the one ascending sort. | external |
| `src/core/candidate.py` | Module docstring inventory line. Import `CONTACT_CONFIG` and `CONTACT_CONTEXT_COMMAND_CONFIG`. New `_SLACK_CHANNEL_ID_PATH`, `_CONTACT_SHOW_EMPTY_REPLY`, and `_CONTACT_SAVE_ACK_REPLY` constants. New `get_candidate_id_for_slack_channel`, `_contact_context_command`, `contact_command_show_context`, and `contact_command_save_context`. | core |

No other file is touched. `tests/` and `docs/test-bible/**` belong to Betty.

**Plan-time dry run:** the code blocks below were applied to the synced tree, both smokes passed, AC 3's grep was empty, and then everything was reverted. The ruff delta was exactly 8 findings, all UP045/UP006 (`Optional[...]` / `Dict[...]`). They match the 129 existing ones in these two files and the `Optional`/`Dict` style of the neighboring functions. Accept those and nothing else.

**Interpreter:** this worktree has no venv, and system `python3` lacks `nh3`. Every `python` / `pytest` command below runs with `PY=/home/susan/astral/.venv/bin/python`, the main checkout's venv, which imports `src.core.candidate`, `src.core.meteorite`, and `src.external.slack` cleanly (checked at plan time). `ruff` is the system binary (`ruff 0.16.10`).

## Stage 0: Baseline (no commit)

**Done when:** the baseline failure list is saved under `debug/spikes/ast-2211/`.

1. On the clean synced tree, run:

   ```bash
   PY=/home/susan/astral/.venv/bin/python
   mkdir -p debug/spikes/ast-2211
   $PY -m pytest tests/component/external/test_slack.py tests/component/core/test_candidate.py tests/component/utils/test_config.py -q -p no:cacheprovider 2>&1 | grep -E '^(FAILED|ERROR)' | sort > debug/spikes/ast-2211/baseline.txt
   wc -l debug/spikes/ast-2211/baseline.txt
   ```

   At plan time, `test_slack.py` + `test_candidate.py` alone had 25 pre-existing failures (for example `TestAst1576SaveCandidateDataOperative::test_craft_generation_calls_save_artifact`). They are not this ticket's. Stages 1–2 compare against this file.

## Stage 1: `src/external/slack.py`: opt-in thread replies on full history

**Done when:** the smoke check in step 4 prints `HISTORY OK`, and the `comm` in step 5 prints nothing.

1. **Module docstring.** In the module docstring, replace

   ```
   type lookup (``fetch_channel_type``), and full ascending channel history
   (``fetch_full_conversation_history``).
   ```

   with

   ```
   type lookup (``fetch_channel_type``), and full ascending channel history
   (``fetch_full_conversation_history``; opt-in thread replies for Contact drafts, AST-2206).
   ```

2. **Signature + docstring.** Replace the `def` line and docstring of `fetch_full_conversation_history`:

   ```python
   def fetch_full_conversation_history(*, channel: str) -> list[dict]:
       """Paginate conversations.history for one channel; return oldest→newest.

       Complements limited ``fetch_conversation_history`` (single page). Hard-fail
       on ok:false / HTTP — no soft-skip for a stored-channel snapshot.
       """
   ```

   with:

   ```python
   def fetch_full_conversation_history(
       *, channel: str, include_thread_replies: bool = False
   ) -> list[dict]:
       """Paginate conversations.history for one channel; return oldest→newest.

       Complements limited ``fetch_conversation_history`` (single page). Hard-fail
       on ok:false / HTTP — no soft-skip for a stored-channel snapshot.
       ``include_thread_replies`` (AST-2206, off by default so the admin snapshot is
       unchanged): also pull every thread's replies via ``conversations.replies`` and
       merge them into the same ascending order. Each message keeps Slack's ``user``
       (poster) and ``thread_ts`` fields as returned.
       """
   ```

3. **Calling line + reply pull.** Replace

   ```python
       logger.debug("Calling fetch_full_conversation_history: channel=%s", ch)
   ```

   with

   ```python
       logger.debug(
           "Calling fetch_full_conversation_history: channel=%s include_thread_replies=%s",
           ch, include_thread_replies,
       )
   ```

   Then, directly after the line `msgs = messages if isinstance(messages, list) else []` and before `logger.debug("Beginning ascending sort loop on %s items", len(msgs))`, insert:

   ```python
       if include_thread_replies:
           # Thread parents carry reply_count > 0 (same test as _collect_poster_ids_for_channel).
           parents = [
               m for m in msgs
               if isinstance(m.get("reply_count"), int) and m["reply_count"] > 0
               and isinstance(m.get("ts"), str) and m["ts"].strip()
           ]
           logger.debug("Beginning thread replies loop on %s items", len(parents))
           for parent in parents:
               parent_ts = parent["ts"].strip()
               # Same hard-fail as history (soft_skip=False → list or raise).
               replies = _paginate_messages(
                   "conversations.replies",
                   {"channel": ch, "ts": parent_ts, "limit": _PAGE_LIMIT},
                   soft_skip=False,
               ) or []
               # conversations.replies echoes the parent as its first message; history already has it.
               msgs.extend(r for r in replies if r.get("ts") != parent_ts)
           logger.debug("End thread replies loop after %s items", len(parents))
   ```

   ⚠️ **Decision: global chronological order.** Replies merge into the existing single `ts` sort, not grouped under their parent. This is the literal "in chronological order" from Technical scope. Each reply's `thread_ts` still says which thread it belongs to. #3 formats the packet.

   ⚠️ **Decision: no poster enrichment.** "With the poster attached" is met by Slack's own `user` field on every history and reply message, the same field the snapshot already returns. No `users.info` / `users.list` call is added.

   ⚠️ **Decision: hard-fail on replies.** A `conversations.replies` `ok:false` raises, like the history call in this function, instead of being soft-skipped like the poster scan. A draft built on silently missing threads would break parent AC 9.

4. **Compile, lint, smoke.**

   ```bash
   PY=/home/susan/astral/.venv/bin/python
   $PY -m py_compile src/external/slack.py
   ruff check src/external/slack.py
   $PY - <<'EOF'
   import src.external.slack as s
   pages = {
       ("conversations.history", None): [
           {"ts": "2.0", "text": "parent", "user": "U1", "reply_count": 1},
           {"ts": "1.0", "text": "first", "user": "U2"},
       ],
       ("conversations.replies", "2.0"): [
           {"ts": "2.0", "text": "parent", "user": "U1", "reply_count": 1},
           {"ts": "3.0", "thread_ts": "2.0", "text": "ZEBRA-7731", "user": "U2"},
       ],
   }
   s._slack_bot_get = lambda method, params: {"ok": True, "messages": list(pages[(method, params.get("ts"))])}
   off = s.fetch_full_conversation_history(channel="C1")
   on = s.fetch_full_conversation_history(channel="C1", include_thread_replies=True)
   assert [m["ts"] for m in off] == ["1.0", "2.0"], off
   assert [m["ts"] for m in on] == ["1.0", "2.0", "3.0"], on
   assert on[2]["user"] == "U2" and on[2]["text"] == "ZEBRA-7731", on
   print("HISTORY OK")
   EOF
   ```

   Compare ruff findings only on lines this stage added. Pre-existing findings elsewhere in the file are not this ticket's. Expect zero new findings in `slack.py`. Any new finding is a stop.

5. **Regression.**

   ```bash
   $PY -m pytest tests/component/external/test_slack.py tests/component/core/test_candidate.py tests/component/utils/test_config.py -q -p no:cacheprovider 2>&1 | grep -E '^(FAILED|ERROR)' | sort > debug/spikes/ast-2211/after-stage1.txt
   comm -13 debug/spikes/ast-2211/baseline.txt debug/spikes/ast-2211/after-stage1.txt
   ```

   `comm` must print nothing. Any new failure → stop and comment on the parent.

6. Commit: `git add src/external/slack.py && git commit -m "code(AST-2211): opt-in thread replies on full channel history"`, then `git push origin HEAD:sub/AST-2206/AST-2211-show-save-handlers-threaded-history`.

## Stage 2: `src/core/candidate.py`: channel lookup, show and save handlers

**Done when:** the smoke check in step 6 prints `HANDLERS OK`, ticket AC 3's grep prints nothing, and the `comm` in step 7 prints nothing.

1. **Module docstring.** In the module docstring, directly after the two lines

   ```
   Resume structure (candidate.artifacts.resume_structure) uses the same
   operative save + get_candidate_current hydrate path (AST-1679).
   ```

   add:

   ```
   Contact context commands (AST-2206): get_candidate_id_for_slack_channel (channel →
   the one candidate naming it in contact.slack_channel_id), contact_command_show_context
   (read-current reply) and contact_command_save_context (nh3 sanitize → operative save).
   ```

2. **Imports.** In the `from src.utils.config import (` list, directly after `    CANDIDATE_LOOKUP_CONFIG,`, add:

   ```python
       CONTACT_CONFIG,
       CONTACT_CONTEXT_COMMAND_CONFIG,
   ```

3. **Constants + lookup.** Directly after the final `    return None` of `get_candidate_id_for_query` and before `def preview_task_prompt(`, insert (keep two blank lines between top-level definitions):

   ```python
   # AST-2206: Contact context commands. contact.slack_channel_id is not a uniqueness-gated field
   # (CANDIDATE_CONTACT_UNIQUENESS_CONFIG), so two candidates can name one channel — ambiguous → None.
   _SLACK_CHANNEL_ID_PATH = "contact.slack_channel_id"
   # Handler reply texts; {label} is the CONTACT_CONTEXT_COMMAND_CONFIG row label.
   _CONTACT_SHOW_EMPTY_REPLY = "No {label} saved yet for this candidate."
   _CONTACT_SAVE_ACK_REPLY = "Saved. That's now the current {label}."


   def get_candidate_id_for_slack_channel(
       channel_id: str,
       *,
       debug: bool = False,
   ) -> Optional[str]:
       """The one non-deleted candidate whose contact.slack_channel_id is ``channel_id`` (AST-2206).

       None when the channel is empty, unmapped, or named by more than one candidate.
       """
       if debug:
           logger.set_debug_flag(True)
       ch = (channel_id or "").strip()
       if not ch:
           return None
       logger.debug("Calling list_candidates: [include_deleted=False]")
       candidates = list_candidates(include_deleted=False)
       logger.debug("Response from list_candidates: %s items", len(candidates))
       logger.debug("Beginning slack channel lookup loop on %s items", len(candidates))
       hit_ids = sorted(
           {
               (c.get("astral_candidate_id") or "").strip()
               for c in candidates
               if _lookup_path_value(c, _SLACK_CHANNEL_ID_PATH) == ch
           }
           - {""}
       )
       logger.debug("End slack channel lookup loop after %s items", len(candidates))
       if len(hit_ids) > 1:
           logger.warning(
               "%s | slack channel %s is named by %s candidates (%s)\n"
               "  No candidate is mapped to this channel until only one names it",
               hit_ids[0], ch, len(hit_ids), ", ".join(hit_ids),
           )
       return hit_ids[0] if len(hit_ids) == 1 else None


   def _contact_context_command(artifact_key: Optional[str]) -> Optional[Dict[str, Any]]:
       """CONTACT_CONTEXT_COMMAND_CONFIG row whose artifact_key matches; None for any other key."""
       key = (artifact_key or "").strip()
       return next(
           (m for m in CONTACT_CONTEXT_COMMAND_CONFIG.values() if m["artifact_key"] == key), None
       )
   ```

   ⚠️ **Decision: deleted candidates never match.** `list_candidates(include_deleted=False)`, same as `get_candidate_id_for_query`. A deleted candidate's channel is unmapped.

   ⚠️ **Decision: warn on an ambiguous channel.** Technical scope only says "returns none" for more than one match. Since channel ids are not uniqueness-gated, a double mapping would otherwise look exactly like an unmapped channel, and #3 would post the unmapped reply with no clue why. One `warning` names the channel and the candidate ids (`stat.logging.warning`). The line is prefixed with the first id because the statute's `<candidate_id> |` lead needs one. No match and an empty channel log nothing beyond debug.

   ⚠️ **Decision: the handlers only accept the six context keys.** `_contact_context_command` returns the registry row (for its `label`) and also guards both handlers, so a mis-wired entry can never show or save some other catalog key (e.g. `candidate.artifacts.base_resume`) through Contact.

4. **Show handler.** Directly after `_contact_context_command`, insert:

   ```python
   def contact_command_show_context(
       candidate_id: str,
       payload: str,
       *,
       source_id: str,
       thread_ts: Optional[str] = None,
       artifact_key: Optional[str] = None,
       debug: bool = False,
   ) -> dict:
       """CONTACT_CONFIG["commands"] code handler for /show-<context> (AST-2206).

       Read-only (patt.artifact.read-current); payload is ignored (payload_optional entry).
       Returns {ok, meteorite_id (always None), error, reply_text}; Contact posts reply_text.
       """
       cid = (candidate_id or "").strip()
       ctx = _contact_context_command(artifact_key)
       if not cid:
           # No reply_text → Contact's hear-ack path.
           return {"ok": False, "meteorite_id": None, "error": "no_candidate", "reply_text": None}
       if ctx is None:
           logger.warning(
               "%s | contact show handler got artifact_key %r, not a context command key\n"
               "  Nothing was shown",
               cid, artifact_key,
           )
           return {"ok": False, "meteorite_id": None, "error": "unknown_artifact_key", "reply_text": None}
       logger.debug(
           "Calling get_candidate_current: [candidate_id=%s, artifact_key=%s]", cid, ctx["artifact_key"]
       )
       body = get_candidate_current(cid, ctx["artifact_key"])
       logger.debug("Response from get_candidate_current: %r", body)
       reply = body if isinstance(body, str) and body.strip() else _CONTACT_SHOW_EMPTY_REPLY.format(label=ctx["label"])
       return {"ok": True, "meteorite_id": None, "error": None, "reply_text": reply}
   ```

5. **Save handler.** Directly after `contact_command_show_context`, insert:

   ```python
   def contact_command_save_context(
       candidate_id: str,
       payload: str,
       *,
       source_id: str,
       thread_ts: Optional[str] = None,
       artifact_key: Optional[str] = None,
       debug: bool = False,
   ) -> dict:
       """CONTACT_CONFIG["commands"] code handler for /save-<context> <text> (AST-2206).

       nh3-sanitizes payload (Contact's one sanitize helper), then write-operative through
       save_candidate_data — identical-to-current is a no-op there. Contact's only artifact
       write ("write artifact" pinhole kind). Returns {ok, meteorite_id (always None), error,
       reply_text}; Contact posts reply_text.
       """
       cid = (candidate_id or "").strip()
       ctx = _contact_context_command(artifact_key)
       if not cid:
           # No reply_text → Contact's hear-ack path.
           return {"ok": False, "meteorite_id": None, "error": "no_candidate", "reply_text": None}
       if ctx is None:
           logger.warning(
               "%s | contact save handler got artifact_key %r, not a context command key\n"
               "  Nothing was saved",
               cid, artifact_key,
           )
           return {"ok": False, "meteorite_id": None, "error": "unknown_artifact_key", "reply_text": None}
       key = ctx["artifact_key"]
       # Late import: meteorite imports candidate at module level.
       from src.core.meteorite import sanitize_contact_text

       logger.debug("Calling sanitize_contact_text: [payload=%r]", payload)
       body = sanitize_contact_text(payload)
       logger.debug("Response from sanitize_contact_text: %r", body)
       if not body:
           logger.warning(
               "%s | contact save of %s rejected — the text is empty after sanitize\n  Nothing was saved",
               cid, key,
           )
           # Same usage line the runner posts for an empty payload; own entry found by handler + key.
           usage = next(
               m["usage_reply_text"] for m in CONTACT_CONFIG["commands"].values()
               if m["handler"] == f"{__name__}.contact_command_save_context" and m.get("artifact_key") == key
           )
           return {"ok": False, "meteorite_id": None, "error": "empty_after_sanitize", "reply_text": usage}
       logger.debug("Calling save_candidate_data: [candidate_id=%s, artifact_key=%s]", cid, key)
       artifact_uuid = save_candidate_data(cid, key, body, debug=debug)
       logger.debug("Response from save_candidate_data: %s", artifact_uuid)
       return {
           "ok": True, "meteorite_id": None, "error": None,
           "reply_text": _CONTACT_SAVE_ACK_REPLY.format(label=ctx["label"]),
       }
   ```

   ⚠️ **Decision: reply texts are `candidate.py` constants, not config.** Technical scope places the "nothing saved yet" line and the ack in the `src/core/candidate.py` handler bullets, and `src/utils/config.py` is not in this ticket's Scope. The AST-2210 plan named this exact split. The texts carry `{label}` from the registry row, so no command id or suffix literal lands in `src/core/` (ticket AC 3).

   ⚠️ **Decision: one ack for a new version and for the identical no-op.** The parent asks for "an ack". After an identical re-post, the text really is the current version, so "Saved. That's now the current {label}." is true either way. Telling the two apart would need an extra current-uuid read, which nothing asks for.

   ⚠️ **Decision: payload is not re-unwrapped.** `parse_contact_command` already runs `_unwrap_slack_links` on every command payload before the runner sees it, so the handler calls only `sanitize_contact_text`, the parent's "existing Contact `nh3` helper".

   ⚠️ **Decision: no try/except in either handler.** A `save_candidate_data` `ValueError` or a database error propagates to the runner and on to the background event handler, which logs exceptions once (`stat.logging.error`, the parent's rule). The only predictable failure, a payload empty after sanitize, is checked before the write and gets its own warning (`stat.logging.warning`: which candidate and why).

   `source_id` and `thread_ts` are accepted for the runner's call shape and unused, same as `contact_command_check_status`'s `thread_ts`.

6. **Compile, lint, smoke, AC 3.**

   ```bash
   PY=/home/susan/astral/.venv/bin/python
   $PY -m py_compile src/core/candidate.py
   ruff check src/core/candidate.py
   $PY - <<'EOF'
   import src.core.candidate as c
   rows = [
       {"astral_candidate_id": "A", "candidate_data": {"contact": {"slack_channel_id": "C1"}}},
       {"astral_candidate_id": "B", "candidate_data": {"contact": {"slack_channel_id": "C2"}}},
       {"astral_candidate_id": "D", "candidate_data": {"contact": {"slack_channel_id": "C2"}}},
   ]
   c.list_candidates = lambda include_deleted=False: rows
   assert c.get_candidate_id_for_slack_channel(" C1 ") == "A"
   assert c.get_candidate_id_for_slack_channel("C2") is None   # ambiguous (warning logged)
   assert c.get_candidate_id_for_slack_channel("C9") is None   # unmapped
   assert c.get_candidate_id_for_slack_channel("") is None
   store = {}
   c.get_candidate_current = lambda cid, key: store.get((cid, key))
   def fake_save(cid, key, blob, **kw):
       store[(cid, key)] = blob
       return "u1"
   c.save_candidate_data = fake_save
   key = "candidate.context.strengths"
   out = c.contact_command_show_context("A", "", source_id="C1:1", artifact_key=key)
   assert out["ok"] and out["reply_text"] == "No strengths saved yet for this candidate.", out
   out = c.contact_command_save_context("A", "Steady <b>under</b> pressure.", source_id="C1:2", artifact_key=key)
   assert out["ok"] and out["reply_text"] == "Saved. That's now the current strengths.", out
   assert store[("A", key)] == "Steady under pressure.", store
   out = c.contact_command_show_context("A", "", source_id="C1:3", artifact_key=key)
   assert out["reply_text"] == "Steady under pressure.", out
   out = c.contact_command_save_context("A", "<b></b>", source_id="C1:4", artifact_key=key)
   assert not out["ok"] and out["error"] == "empty_after_sanitize" and out["reply_text"].startswith("Usage:"), out
   out = c.contact_command_save_context("A", "x", source_id="C1:5", artifact_key="candidate.artifacts.base_resume")
   assert not out["ok"] and out["error"] == "unknown_artifact_key" and out["reply_text"] is None, out
   out = c.contact_command_show_context("", "", source_id="C1:6", artifact_key=key)
   assert not out["ok"] and out["error"] == "no_candidate", out
   print("HANDLERS OK")
   EOF
   grep -rnE '(draft|save|show)-(strengths|dealbreakers|priorities|ideal-day|bio-summary|backstory)' src/core/
   ```

   The smoke patches module attributes in a throwaway process. It touches no database. The final grep (ticket AC 3) must print nothing. Compare ruff findings only on lines this stage added. Expect exactly 8 new findings: 7 UP045 (`Optional[...]`) and 1 UP006 (`Dict[...]` in `_contact_context_command`). See the dry-run note under Files Changed. Anything else is a stop.

7. **Regression.**

   ```bash
   $PY -m pytest tests/component/external/test_slack.py tests/component/core/test_candidate.py tests/component/utils/test_config.py -q -p no:cacheprovider 2>&1 | grep -E '^(FAILED|ERROR)' | sort > debug/spikes/ast-2211/after-stage2.txt
   comm -13 debug/spikes/ast-2211/after-stage1.txt debug/spikes/ast-2211/after-stage2.txt
   ```

   `comm` must print nothing. Any new failure → stop and comment on the parent.

8. Commit: `git add src/core/candidate.py && git commit -m "code(AST-2211): channel→candidate lookup, /show- and /save- context handlers"`, then `git push origin HEAD:sub/AST-2206/AST-2211-show-save-handlers-threaded-history`.

## Canon alignment (plan-stage)

- **`patt.artifact.write-operative`**: `/save-` validates (sanitize, then a non-empty check) before invoking, and writes only through the entity wrapper `save_candidate_data(candidate_id, artifact_key, body)`. That wrapper does the `plain_text` shape check, the identical-to-current no-op (returns the existing `artifact_uuid`, no retire+insert), and otherwise `save_artifact` retire+insert. No in-place UPDATE, no direct `database` call from the handler.
- **`patt.artifact.read-current`**: `/show-` reads through the entity wrapper `get_candidate_current(candidate_id, artifact_key)`, never a `candidate_data` blob path. A miss (`None`) gives the "nothing saved yet" reply, with no coat-check and no lazy fetch.
- **`stat.logging.debug`**: id-only at plan stage. Placed per the codebase's existing Calling/Response and Beginning/End loop convention (as in `contact_command_check_status` and `slack._collect_poster_ids_for_channel`). Every new callee call (`list_candidates`, `get_candidate_current`, `sanitize_contact_text`, `save_candidate_data`, `conversations.replies` pagination) and the two new loops have them. `build-child` §8 checks the statute text. A conflict there is a stop-and-comment, not a silent adapt.
- **`stat.logging.warning`**: id-only at plan stage. One warning per failed save (empty after sanitize, unknown key), per show with an unknown key, and per ambiguous channel. Each uses the existing `"<candidate_id> | <what> \n  <consequence>"` shape. Same `build-child` §8 rule.

## Acceptance trace

| Ticket AC | Where satisfied |
|-----------|-----------------|
| 3 No command literals in core | Stage 2 steps 3–5 (texts use `{label}`; own entry found by handler path + `artifact_key`); grep in Stage 2 step 6 |
| 4 Snapshot unchanged | Stage 1 step 3 (default `include_thread_replies=False` path is unchanged code); `off` assert in Stage 1 step 4; `test_slack.py` snapshot cases in step 5; `get_admin_slack_channel_snapshot` untouched |

The ticket's "Ships" line (show returns the current body, save inserts a sanitized version with the identical no-op, the lookup maps a channel to exactly one candidate, the fetch can include thread replies) is exercised by the Stage 1 and Stage 2 smokes. The parent's end-to-end Slack ACs 5–9 and 15 go green only once #3 wires these in.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2211
**Overall:** APPROVED
**Corpus:** 0d01e20d2b313a4e35cf3d07434b6cd69f615768
**Publish ref:** `origin/sub/AST-2206/AST-2211-show-save-handlers-threaded-history` @ `7df33a15fdf7e7eaa86d47f7c3c4081e99c42b0d`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.write-operative | A | | |
| patt.artifact.read-current | A | | |
| stat.logging.debug | A | | |
| stat.logging.warning | A | | |

## Traceability

AC3→Stage 2 (3–5, grep in 6); AC4→Stage 1 (default `include_thread_replies=False`, snapshot caller untouched, off-path smoke + regression). Parent Slack AC 5–9 / 15 explicitly deferred to AST-2212; “Ships” line covered by Stage 1–2 smokes.

## Findings

### acceptable

- **Location:** Plan § Contract with #1 / Stage 2 imports  
  **Finding:** Handlers and lookup depend on `CONTACT_CONTEXT_COMMAND_CONFIG` from AST-2210; build assumes #1 is on the integration line before this sub lands.  
  **Recommendation:** Merge/rebase #1 before Stage 2; no plan rewrite.

- **Location:** Stage 2 save handler — identical no-op ack  
  **Finding:** Same ack text after operative no-op and after a real insert.  
  **Recommendation:** Matches parent “an ack” without requiring a distinguishable message; keep as decided.

### discuss

- **Location:** `get_candidate_id_for_slack_channel` ambiguous-channel warning  
  **Finding:** Warning lead uses `hit_ids[0]` when multiple candidates share a channel — correct shape, slightly arbitrary “who” for a non-unique case.  
  **Recommendation:** Fine for ops; optional future tweak only if Susan wants a neutral prefix.

context_tokens≈52000

## Review

**Built:** `origin/sub/AST-2206/AST-2211-show-save-handlers-threaded-history` @ `7550babcf` (Stage 1 `c1fca9095`, Stage 2 `7550babcf`).

**Implementer notes:**
- **§8 self-correction:** `get_candidate_id_for_slack_channel` logs `Response from list_candidates: <full list>` instead of the plan's `%s items` count. `stat.logging.debug` says to log the whole response and never truncate. No contract change.
- **For Radia:** `get_candidate_id_for_slack_channel` keeps the plan's `debug=` kwarg + `logger.set_debug_flag(True)`, the same shape as `get_candidate_id_for_query`, so #3 can pass `debug=` like it does to the sibling lookup. `stat.logging.debug` prefers callees without a logging-only `debug=`. I left it as planned (Joan graded A) instead of changing #3's call contract mid-epic.
- **Lint:** the ruff delta is exactly what the plan predicted. `slack.py` has 0 new findings. `candidate.py` has 8 (7 UP045 `Optional`, 1 UP006 `Dict`), which match the file's existing style.
- **Tests:** no new failures vs the Stage 0 baseline across `test_slack.py`, `test_candidate.py`, and `test_config.py` (53 pre-existing FAILED/ERROR lines, unchanged). Run with `~/astral/.venv/bin/python`, since system `python3` lacks `nh3`.
- **Coverage gaps for Betty (not added; test tree is hers):** `include_thread_replies=True` (parent echo dropped, replies merged in `ts` order, `conversations.replies` ok:false raises); `get_candidate_id_for_slack_channel` unique, ambiguous, unmapped, and deleted cases; show handler (saved body, empty line, unknown key); save handler (sanitized save, empty-after-sanitize gives the usage reply and no write, unknown key gives no write, identical re-save adds no version via `save_candidate_data`).

## Radia review

[code-rubric]
**Ticket:** AST-2211
**Publish ref:** `bc442b2bd6d96ffcad15e294a65bd1953842cc44` (`origin/sub/AST-2206/AST-2211-show-save-handlers-threaded-history`)
**Corpus:** `0d01e20d2b313a4e35cf3d07434b6cd69f615768` (directives read from `canon/directives/active/` at publish tip; no `docs/canon-index.md`)
**Overall:** CLEAN

**Scoring scope:** Product and tests scored on AST-2211-owned paths only (`src/core/candidate.py`, `src/external/slack.py`, `tests/component/core/test_candidate.py`, `tests/component/external/test_slack.py`, and matching bible § AST-2211). AST-2210 config/catalog carry and AST-2209 `telescope_data`→`web_data` merge on the sub are noted as carry, not graded as #2 defects.

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.write-operative | A | | |
| patt.artifact.read-current | A | | |
| stat.logging.debug | A | | |
| stat.logging.warning | A | | |

## Column diff vs plan stage

(aligned) — Joan: all A; code review matches.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Location:** `docs/features/contact/ast-2211-show-save-handlers-threaded-history.md` § Review — implementer “coverage gaps for Betty”  
  **Finding:** Superseded on tip `bc442b2bd`: Betty landed `TestAst2211ContactContextHandlers` and `TestAst2211FullHistoryThreadReplies` covering lookup (unique/ambiguous/unmapped/blank/debug flag), show/save per context key, identical re-save no-op, empty-after-sanitize usage reply, default-off snapshot path, thread merge/sort, and `conversations.replies` hard-fail. No action on that bullet except strike from implementer notes when Chuckles appends this review.

- **Location:** § Review — Hedy question: `get_candidate_id_for_slack_channel(..., debug=)` vs `stat.logging.debug` Resolution #4  
  **Finding:** `debug=` mirrors existing `get_candidate_id_for_query` (`logger.set_debug_flag(True)` at entry). `contact_command_save_context` passes `debug=` through to `save_candidate_data` (operative path, not logging-only). `contact_command_show_context` accepts `debug=` for runner signature parity and does not use it in the body — harmless until #3 wires the runner. **Radia answer:** keep as shipped; not `resolve-child` canon work unless Susan opens an epic-wide “ContextVar-only, drop logging `debug=` on lookups” cleanup.

- **Location:** § Review — Hedy question: `Response from list_candidates: %s` full list vs count  
  **Finding:** Full serialized list matches `stat.logging.debug` (no truncation on callee out). Count still appears on begin/end loop lines. **Radia answer:** implementer self-correction is correct; no change required.

- **Location:** Joan plan discuss — ambiguous-channel warning uses `hit_ids[0]` as lead identifier  
  **Finding:** Warning shape satisfies `stat.logging.warning` (who + why + product next step); lead id is arbitrary when multiple map. Ops-only; optional neutral prefix is a future polish, not blocking #2.

- **Location:** Branch ancestry  
  **Finding:** **Sibling test/bible carry:** `docs/test-bible/utils/config.md`, `docs/test-bible/core/repo_admin_json.md`, `tests/component/utils/test_config.py`, `tests/component/core/test_repo_admin_json.py` changes belong to AST-2210 on this sub; expected after `after AST-2210` + ftr sync. Not cross-ticket product scope.

## What's solid

- **read-current / write-operative:** `contact_command_show_context` uses `get_candidate_current`; empty/miss uses label-templated line, not blobs. `contact_command_save_context` runs `sanitize_contact_text` then `save_candidate_data`; identical re-save adds no version (component test on `seeded_db`).
- **AC 3:** No `(draft|save|show)-<suffix>` literals under `src/core/` on publish ref; save empty-after-sanitize resolves `usage_reply_text` via handler path + `artifact_key` scan.
- **AC 4:** `include_thread_replies=False` default leaves the prior history path; admin snapshot caller untouched; tests prove default-off never calls `conversations.replies` and on-path merges/dedupes parent echo with ascending `ts` sort.
- **Warnings:** Unknown `artifact_key`, empty-after-sanitize, and ambiguous channel each emit a single `logger.warning` with candidate/channel context before a safe no-op return.

## Recommended actions (Chuckles — not Radia)

1. Append this artifact to `docs/features/contact/ast-2211-show-save-handlers-threaded-history.md`, commit `docs(AST-2211): Radia review — clean`, push `origin/sub/AST-2206/AST-2211-show-save-handlers-threaded-history`.
2. Post slim upshot via `linear_proxy.py --as radia save-comment`.
3. **Review Posted** → datt **PROCEED** → **User Testing** (no `resolve-child` canon work expected; parent Slack AC 5–9 / 15 still wait on AST-2212).

context_tokens≈38000
