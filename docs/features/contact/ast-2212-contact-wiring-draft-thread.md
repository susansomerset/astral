# AST-2212 — Contact wiring, draft, and draft-thread dialog

**Linear:** [AST-2212](https://linear.app/astralcareermatch/issue/AST-2212)
**Parent:** [AST-2206](https://linear.app/astralcareermatch/issue/AST-2206) — Contact /draft-<context> skills with /save- and /show-
**Publish ref:** `origin/sub/AST-2206/AST-2212-contact-wiring-draft-thread`

This ticket wires the epic's Slack experience into `src/core/contact.py`, the only file it touches. Siblings #1 ([AST-2210](https://linear.app/astralcareermatch/issue/AST-2210), config and prompts) and #2 ([AST-2211](https://linear.app/astralcareermatch/issue/AST-2211), show/save handlers, channel lookup, threaded history) are already merged on `origin/ftr/AST-2206-contact-context-draft-commands` and present on this sub after `sync-child.sh`. This ticket adds four things:

- **Command runner.** A `private_channel_only` entry runs only on an @mention in a private channel, and acts on the candidate that channel maps to, not the sender's own candidate. A DM gets the fixed refusal and nothing runs. An unmapped private channel gets the unmapped reply and nothing runs. A `payload_optional` entry runs its handler on an empty payload. An entry's `artifact_key` is passed to its handler as `artifact_key=`.
- **Public-channel refusal.** A `private_channel_only` command @mentioned in a public channel (or group DM) gets the same fixed refusal. Every other public-channel mention keeps dropping silently at the AST-2061 gate.
- **`/draft-` handler.** `contact_command_draft_context` builds the source packet and runs the key's draft task through `agent.do_task` on the candidate's key. The packet holds the mapped channel's full history with thread replies, the candidate's name, context (including `raw_resume` / `raw_profile`), and contact, plus the current saved body. The draft posts under the command message. Nothing is saved.
- **Contact draft thread.** A non-command @mention in a private-channel thread whose root message is a `/draft-<context>` command runs `run_contact_draft_revise_turn` (contact Estelle, the revise task) instead of the normal Estelle turn. Its reply posts in the thread.

## Scope gate

The ticket's `## Scope` names one file: `src/core/contact.py`. Every change below is in it, and each is a kind the Scope names:

- Runner: honors `payload_optional`, passes the artifact key, resolves the channel-mapped candidate, posts the unmapped reply, and posts the outside-private-channel refusal.
- Inbound handling: the refusal at the public-channel gate, and draft-thread routing.
- New `/draft-` handler running the draft task through `agent.do_task`.
- New revise-turn function.
- Module docstring and import list: they document and enable the same change in the same file.

**Not in this ticket:** `src/utils/config.py` and `data/admin/agent_task.json` (#1, landed), `src/core/candidate.py` and `src/external/slack.py` (#2, landed), `src/core/intake.py` (AC 4: untouched). The canon text amendments the parent asks for are also out. Those are the three `patt.contact.command-intercept` amendments (a: payload-optional, b: per-entry artifact key, c: private-channel-only) and the new **Contact draft thread** pattern. No `canon/` file is in this ticket's Scope. This ticket ships the runtime half, the same split #1 used for the config half. Who edits the canon text is Chuckles/Archie's call.

## Contract with #1 and #2 (landed; names verified on the synced tree)

| From | Name | Used here as |
|------|------|--------------|
| #1 config | `CONTACT_CONFIG["commands"][id]["payload_optional" / "artifact_key" / "private_channel_only" / "reply_placement"]` | runner flags; `artifact_key=` kwarg |
| #1 config | `CONTACT_CONFIG["private_channel_only_reply_text"]`, `CONTACT_CONFIG["unmapped_channel_reply_text"]` | fixed replies |
| #1 config | `CONTACT_CONTEXT_COMMAND_CONFIG[suffix]` → `artifact_key`, `draft_task`, `label` | the draft handler finds its row by `artifact_key` |
| #1 config | `CONTACT_DRAFT_THREAD_CONFIG["revise_task_key"]` (`contact_draft_revise`) | revise task |
| #1 config | draft handler path `src.core.contact.contact_command_draft_context` (pinhole kind `read artifact (LLM draft, no artifact write)`) | function defined here |
| #2 candidate | `get_candidate_id_for_slack_channel(channel_id, *, debug=False) -> Optional[str]` | channel → candidate |
| #2 candidate | `contact_command_show_context` / `contact_command_save_context` with `artifact_key=` | called by the runner |
| #2 slack | `fetch_full_conversation_history(*, channel, include_thread_replies=False)` | `include_thread_replies=True` for draft and revise |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/contact.py` | Module docstring line. Imports: `uuid`, `datetime`/`timezone`, `get_candidate_current`, `get_candidate_id_for_slack_channel`, `CANDIDATE_LIBRARY_CONFIG`, `CONTACT_CONTEXT_COMMAND_CONFIG`, `CONTACT_DRAFT_THREAD_CONFIG`, `flush_log_buffer`, `log_batch_id`. New `_SLACK_PRIVATE_CHANNEL_TYPE`, `_post_contact_command_notice`, `_contact_task_ctx`, `_run_contact_ledgered_task`, `_contact_transcript_lines`, `contact_command_draft_context`, `_draft_thread_root_command`, `run_contact_draft_revise_turn`. `_run_contact_command`: `private_channel` param, private-channel-only gate, `payload_optional`, `artifact_key=` pass-through. `_handle_slack_event_body`: public-channel refusal, `private_channel` flag, draft-thread routing. | core |

No other file is touched. `tests/` and `docs/test-bible/**` belong to Betty.

**Plan-time dry run:** every code block below was applied to the synced tree (tip `688d17f77`). It compiled and imported. The smoke script in Stage 0 printed `STAGE 1 OK` / `STAGE 2 OK` / `STAGE 3 OK`. AC 3's grep was empty, and `test_contact.py` + `test_config.py` had **0 new failures** against the baseline. Everything was then reverted. The ruff delta was exactly 8 findings, listed per stage below. Accept those and nothing else.

**Interpreter:** this worktree has no venv. Every `python` / `pytest` command runs with `PY=/home/susan/astral/.venv/bin/python` (the main checkout's venv; system `python3` lacks `asyncpg` / `nh3`), with `PYTHONPATH=.` for scripts. `ruff` is the system binary. Some Contact tests rewrite `data/contact_estelle_activity.json`. Run `git restore data/contact_estelle_activity.json` after every pytest run and before every commit.

## Stage 0: Baseline and smoke script (no commit)

**Done when:** `debug/spikes/ast-2212/baseline.txt` exists and the smoke script is saved.

1. On the clean synced tree:

   ```bash
   PY=/home/susan/astral/.venv/bin/python
   mkdir -p debug/spikes/ast-2212
   $PY -m pytest tests/component/core/test_contact.py tests/component/utils/test_config.py -q -p no:cacheprovider 2>&1 | grep -E '^(FAILED|ERROR)' | sort > debug/spikes/ast-2212/baseline.txt
   wc -l debug/spikes/ast-2212/baseline.txt
   git restore data/contact_estelle_activity.json
   ```

   At plan time this was 36 lines. Seven are `test_contact.py` failures (`TestAst1073ContactEstelleTurnLoop`, `TestAst1101ChannelHearEvidence`, `TestAst1207DurableDebugSot`, `TestAst1515ContactTaskMarkup` debug-style cases). The rest are `test_config.py` (for example `TestAst1955PlainAgentSettings::*`). None of them are this ticket's.

2. Save the smoke script below as `debug/spikes/ast-2212/smoke.py` (gitignored; never committed). If the editor refuses writes under gitignored `debug/`, save it as `/tmp/ast-2212/smoke.py` instead (the AST-2210 precedent) and use that path in every stage. It runs `handle_slack_event` end to end with Slack, the database, and the LLM stubbed, and touches no data. `smoke.py N` runs every section up to stage N. AC numbers are this ticket's.

   ```python
   """AST-2212 smoke: handle_slack_event end to end with Slack / DB / LLM stubbed. Usage: smoke.py <stage 1|2|3>."""
   import sys

   import src.core.agent as agent_mod
   import src.core.candidate as cand_mod
   import src.core.contact as c
   import src.data.contact_estelle_activity as act_mod
   from src.utils.config import CONTACT_CONFIG

   STAGE = int(sys.argv[1])
   CONTACT_CONFIG["listen_enabled"] = True
   c.slack_listen_enabled = lambda: True
   c.slack_debug_enabled = lambda: False
   act_mod.record_estelle_activity = lambda **kw: None  # keep data/contact_estelle_activity.json clean

   posts, turns, ledger, tasks, saved = [], [], [], [], {}
   CTYPES = {"CPRIV": "group", "CUNMAP": "group", "CPUB": "channel"}
   c.fetch_channel_type = lambda ch: CTYPES[ch]
   # The sender (Susan) is bound to her own candidate SUSAN; channel CPRIV maps to candidate X.
   c.resolve_slack_user = lambda u, **kw: {"astral_candidate_id": "SUSAN", "state": "ACTIVE", "created": False}
   c.contact_post_message = lambda **kw: posts.append(kw) or {"ok": True}
   c.try_meteorite_apply_paste_from_slack = lambda **kw: {"applied": False}
   c.run_contact_estelle_turn = lambda **kw: turns.append(kw) or {"ok": True, "outcome": "success", "slack_post": {"ok": True}}
   c.get_candidate_id_for_slack_channel = lambda ch, debug=False: {"CPRIV": "X"}.get(ch)
   cand_mod.get_candidate_current = lambda cid, key: saved.get((cid, key))
   cand_mod.save_candidate_data = lambda cid, key, body, **kw: saved.__setitem__((cid, key), body) or "u1"
   KEY = "candidate.context.strengths"


   def send(channel, text, *, etype="app_mention", ts="9.0", thread_ts=None, channel_type=None):
       posts.clear(); turns.clear(); tasks.clear(); ledger.clear()
       send.n = getattr(send, "n", 0) + 1
       ev = {"type": etype, "user": "U1", "channel": channel, "ts": ts, "text": text}
       if thread_ts:
           ev["thread_ts"] = thread_ts
       if channel_type:
           ev["channel_type"] = channel_type
       return c.handle_slack_event({"event_id": f"Ev{send.n}", "event": ev})


   # --- Stage 1: runner + gates ---
   saved[("X", KEY)] = "X strengths"
   saved[("SUSAN", KEY)] = "SUSAN strengths"
   send("CPRIV", "<@UBOT> /show-strengths")                      # AC 5: channel's candidate, no usage reply
   assert [p["text"] for p in posts] == ["X strengths"], posts
   send("CPRIV", "<@UBOT> /save-strengths Steady under pressure.")  # AC 6: saves on X, not SUSAN
   assert saved[("X", KEY)] == "Steady under pressure." and saved[("SUSAN", KEY)] == "SUSAN strengths", saved
   send("CPRIV", "<@UBOT> /save-strengths")                      # AC 7: usage, no handler
   assert len(posts) == 1 and posts[0]["text"].startswith("Usage:"), posts
   send("CUNMAP", "<@UBOT> /show-strengths")                     # AC 12: unmapped reply only
   assert [p["text"] for p in posts] == [CONTACT_CONFIG["unmapped_channel_reply_text"]], posts
   refusal = [CONTACT_CONFIG["private_channel_only_reply_text"]]
   out = send("CPUB", "<@UBOT> /show-strengths")                 # AC 13: public refusal
   assert [p["text"] for p in posts] == refusal and out["accepted"], (posts, out)
   send("D1", "/show-strengths", etype="message", channel_type="im")  # AC 13: DM refusal
   assert [p["text"] for p in posts] == refusal, posts
   out = send("CPUB", "<@UBOT> hello")                           # AC 13: non-command public mention silent
   assert posts == [] and out == {"accepted": False, "reason": "channel_not_private"}, (posts, out)
   out = send("CPUB", "<@UBOT> /add-job https://x.io/1")         # AST-2061 unchanged for other commands
   assert posts == [] and out["reason"] == "channel_not_private", (posts, out)
   print("STAGE 1 OK")

   if STAGE >= 2:
       row = {"astral_candidate_id": "X", "first": "Dana", "last": "Q", "full": "Dana Q", "pronouns": "she/her",
              "candidate_data": {"contact": {"slack_channel_id": "CPRIV"},
                                 "context": {"raw_resume": "RESUME", "strengths": "STALE BLOB"}}}
       c.get_candidate = lambda cid: row if cid == "X" else None
       c.get_candidate_current = cand_mod.get_candidate_current
       HISTORY = [
           {"ts": "1.0", "user": "U2", "text": "hello", "reply_count": 1},
           {"ts": "2.0", "thread_ts": "1.0", "user": "U2", "text": "ZEBRA-7731"},
           {"ts": "5.0", "user": "U1", "text": "<@UBOT> /draft-strengths", "reply_count": 2},
           {"ts": "6.0", "thread_ts": "5.0", "bot_id": "B1", "text": "draft v1"},
           {"ts": "7.0", "thread_ts": "5.0", "user": "U1", "text": "<@UBOT> is the spitting contest relevant?"},
       ]
       c.fetch_full_conversation_history = lambda *, channel, include_thread_replies=False: list(HISTORY)
       c.load_slack_conversation_context = lambda **kw: {
           "messages": [m for m in HISTORY if kw["thread_ts"] in (m["ts"], m.get("thread_ts"))]
       }
       c.database.save_dispatch_ledger = lambda *a, **kw: ledger.append(("save", a, kw))
       c.database.update_dispatch_ledger = lambda *a, **kw: ledger.append(("update", a, kw))
       agent_mod.compute_batch_cost = lambda b: 0.0

       async def fake_do_task(task_key, *, live_content, index, ctx, debug, store_agent_data):
           tasks.append({"task_key": task_key, "live": live_content, "index": index, "batch": c.log_batch_id.get()})
           if task_key.startswith("draft_context_"):
               return {"success": True, "parsed_response": {"draft": "Steady under pressure.", "note": "Leaned on the channel."}}
           return {"success": True, "parsed_response": {"reply": "Fair, cutting it.", "revised_draft": "Steady."},
                   "agent_performance": {"status": "success"}}
       agent_mod.do_task = fake_do_task

       saved[("X", KEY)] = "X strengths"
       send("CPRIV", "<@UBOT> /draft-strengths", ts="5.0")       # AC 8 / 9
       assert len(tasks) == 1 and tasks[0]["task_key"] == "draft_context_strengths" and tasks[0]["index"] == "X", tasks
       assert tasks[0]["batch"] and tasks[0]["batch"].startswith("contact-draft_context_strengths-"), tasks
       assert "ZEBRA-7731" in tasks[0]["live"] and "(thread reply)" in tasks[0]["live"], tasks[0]["live"]
       assert "STALE BLOB" not in tasks[0]["live"] and "RESUME" in tasks[0]["live"] and "X strengths" in tasks[0]["live"]
       assert [x[0] for x in ledger] == ["save", "update"] and ledger[0][1][2] == "X", ledger
       assert ledger[1][2]["status"] == "COMPLETED", ledger
       assert posts[0]["thread_ts"] == "5.0" and posts[0]["text"] == "Steady under pressure.\n\nLeaned on the channel.", posts
       assert saved[("X", KEY)] == "X strengths" and c.log_batch_id.get() is None  # no save; batch reset
       print("STAGE 2 OK")

   if STAGE >= 3:
       send("CPRIV", "<@UBOT> is the spitting contest relevant?", ts="7.0", thread_ts="5.0")  # AC 10
       assert turns == [] and [t["task_key"] for t in tasks] == ["contact_draft_revise"], (turns, tasks)
       assert "draft v1" in tasks[0]["live"] and "ZEBRA-7731" not in tasks[0]["live"], tasks[0]["live"]
       assert posts[0]["thread_ts"] == "5.0" and posts[0]["text"] == "Fair, cutting it.\n\nSteady.", posts
       send("CPRIV", "<@UBOT> thoughts?", ts="3.0", thread_ts="1.0")  # non-draft thread → normal Estelle turn
       assert len(turns) == 1 and tasks == [], (turns, tasks)
       send("CPRIV", "<@UBOT> /show-strengths", ts="8.0", thread_ts="5.0")  # a command in a draft thread is a command
       assert tasks == [] and posts[0]["text"] == "X strengths", posts
       print("STAGE 3 OK")
   ```

3. **Per-stage check** (run at the end of Stages 1–3 with `N` = the stage number; `HEAD` is the previous stage's commit, so the ruff diff is that stage's delta):

   ```bash
   PY=/home/susan/astral/.venv/bin/python
   $PY -m py_compile src/core/contact.py && $PY -c "import src.core.contact"
   PYTHONPATH=. $PY debug/spikes/ast-2212/smoke.py N
   grep -rnE '(draft|save|show)-(strengths|dealbreakers|priorities|ideal-day|bio-summary|backstory)' src/core/
   strip(){ sed -E 's/\x1b\[[0-9;]*m//g'; }
   git show HEAD:src/core/contact.py > /tmp/ast-2212-head.py
   ruff check /tmp/ast-2212-head.py --output-format concise 2>/dev/null | strip | rg -o ' [A-Z]+[0-9]{3} ' | sort | uniq -c > debug/spikes/ast-2212/ruff-head.txt
   ruff check src/core/contact.py --output-format concise 2>/dev/null | strip | rg -o ' [A-Z]+[0-9]{3} ' | sort | uniq -c > debug/spikes/ast-2212/ruff-now.txt
   diff debug/spikes/ast-2212/ruff-head.txt debug/spikes/ast-2212/ruff-now.txt
   $PY -m pytest tests/component/core/test_contact.py tests/component/utils/test_config.py -q -p no:cacheprovider 2>&1 | grep -E '^(FAILED|ERROR)' | sort > debug/spikes/ast-2212/after-stageN.txt
   comm -13 debug/spikes/ast-2212/baseline.txt debug/spikes/ast-2212/after-stageN.txt
   git restore data/contact_estelle_activity.json
   ```

   The smoke must print `STAGE N OK` (and every lower stage). The AC 3 grep must print nothing, and `comm` must print nothing. The ruff `diff` must show exactly the stage's expected delta, all of them `Optional[...]` / `List[...]` hints matching the file's existing 70+, plus one `TRY401` matching the body's existing 11 `logger.exception` lines. Anything else → stop and comment on the parent.

## Stage 1: Runner and gates: private-channel-only, unmapped, payload-optional, artifact key

**Done when:** the Stage 0 step 3 check passes with `N=1`. Expected ruff delta: `UP045` +2.

1. **Module docstring.** Directly after the two lines

   ```
   AST-1788: admin channel-list / membership / snapshot orchestration for
   Manage Candidates (no Estelle turn-loop changes).
   ```

   add:

   ```
   AST-2206: private_channel_only commands act on the channel's mapped candidate (refusal
   elsewhere, unmapped reply); /draft-<context> handler; Contact draft thread revise turn.
   ```

2. **Import.** In the `from src.core.candidate import (` list, directly after `    get_candidate_id_for_query,`, add `    get_candidate_id_for_slack_channel,`.

3. **Constant + notice helper.** Directly after the final `    return out` of `run_contact_estelle_turn` (the line after `logger.debug("Response from run_contact_estelle_turn: %s", out)`) and before `def _run_contact_command(`, insert (two blank lines between top-level definitions):

   ```python
   # AST-2206: Slack channel_type of a private channel (fetch_channel_type vocabulary: im | mpim | group | channel).
   _SLACK_PRIVATE_CHANNEL_TYPE = "group"


   def _post_contact_command_notice(
       *,
       command_id: str,
       outcome: str,
       text: str,
       channel: str,
       thread_ts: Optional[str],
       message_ts: Optional[str],
       debug: bool = False,
   ) -> dict:
       """Post a fixed reply for a command that does not run (refused / unmapped); returns the estelle_turn dict.

       Placed by the entry's reply_placement like every other reply to that command (AST-2144).
       """
       reply_ts, reply_broadcast = _contact_reply_placement(
           thread_ts, message_ts, CONTACT_CONFIG["commands"][command_id].get("reply_placement")
       )
       post = contact_post_message(
           channel=channel,
           text=format_contact_reply_text(text),
           thread_ts=reply_ts,
           reply_broadcast=reply_broadcast,
           debug=debug,
       )
       summary = {"id": command_id, "mode": outcome, "ok": False, "meteorite_id": None, "error": outcome}
       return {"ok": True, "outcome": command_id, "command": summary, "slack_post": post}
   ```

   ⚠️ **Decision: `"group"` is the private-channel test.** `CONTACT_CONFIG["allowed_channel_types"]` is `("im", "group")`. It names where Estelle acts, not which of those is "the private channel". Config is #1's file, so the Slack vocabulary value lives here as one named constant, next to `_is_dm_message`'s own `"im"`.

   ⚠️ **Decision: refusal and unmapped replies use the entry's `reply_placement`**, like every other reply `_run_contact_command` posts for that command (AST-2144). `/draft-` refusals thread under the command message, and `/show-` / `/save-` follow `thread_response`. `estelle_turn.command` = `{id, mode: "refused"|"unmapped", …}`, so the existing `_emit_listen_info` writes `<command id>:refused` / `<command id>:unmapped` on the one `stat.logging.info.contact` line.

4. **Runner signature + private-channel gate.** In `_run_contact_command`, replace

   ```python
       astral_candidate_id: str,
       candidate_state: str | None,
       debug: bool = False,
   ) -> dict:
       """Run one registry command and reply per its mode; returns the estelle_turn dict."""
       meta = CONTACT_CONFIG["commands"][command_id]
   ```

   with:

   ```python
       astral_candidate_id: str,
       candidate_state: str | None,
       private_channel: bool = False,
       debug: bool = False,
   ) -> dict:
       """Run one registry command and reply per its mode; returns the estelle_turn dict."""
       meta = CONTACT_CONFIG["commands"][command_id]
       # AST-2206: a private_channel_only entry runs only in a private channel, on the candidate that
       # channel maps to (not the sender's). Elsewhere, or unmapped, a fixed reply posts and nothing runs.
       if meta.get("private_channel_only"):
           notice = {"channel": channel, "thread_ts": thread_ts, "message_ts": message_ts, "debug": debug}
           if not private_channel:
               return _post_contact_command_notice(
                   command_id=command_id, outcome="refused",
                   text=CONTACT_CONFIG["private_channel_only_reply_text"], **notice,
               )
           logger.debug("Calling get_candidate_id_for_slack_channel: [channel=%s]", channel)
           mapped = get_candidate_id_for_slack_channel(channel, debug=debug)
           logger.debug("Response from get_candidate_id_for_slack_channel: %s", mapped)
           if mapped is None:
               return _post_contact_command_notice(
                   command_id=command_id, outcome="unmapped",
                   text=CONTACT_CONFIG["unmapped_channel_reply_text"], **notice,
               )
           astral_candidate_id = mapped
   ```

   ⚠️ **Decision: the gate runs before the empty-payload check.** `/save-strengths` with no text in a DM gets the refusal, not the usage line (AC 13: "exactly the configured refusal line").

   ⚠️ **Decision: the bound-sender gate stays.** `_run_contact_command` is still reached only for a bound sender (`known`, pattern Arc step 3). An unbound person in a mapped channel gets the unknown-recognition reply, as today. Susan and candidate X are both bound, which is what AC 5–6 need.

5. **Payload-optional.** Replace

   ```python
       # Empty payload: usage reply only, either mode — no handler, no turn.
       if not payload:
   ```

   with:

   ```python
       # Empty payload: usage reply only, either mode — no handler, no turn. A payload_optional entry
       # (AST-2206) runs its handler on an empty payload instead.
       if not payload and not meta.get("payload_optional"):
   ```

6. **Artifact key pass-through.** Replace

   ```python
           source_id = f"{channel}:{message_ts or ''}"
           logger.debug(
               "Calling %s: [candidate_id=%r, source_id=%r, thread_ts=%r, payload=%r]",
               meta["handler"], astral_candidate_id, source_id, anchor_ts, payload,
           )
           out = handler(
               astral_candidate_id, payload,
               source_id=source_id, thread_ts=anchor_ts, debug=debug,
           )
   ```

   with:

   ```python
           source_id = f"{channel}:{message_ts or ''}"
           # AST-2206: artifact_key= only for entries that declare one (older handlers don't take it).
           extra = {"artifact_key": meta["artifact_key"]} if "artifact_key" in meta else {}
           logger.debug(
               "Calling %s: [candidate_id=%r, source_id=%r, thread_ts=%r, payload=%r, %s]",
               meta["handler"], astral_candidate_id, source_id, anchor_ts, payload, extra,
           )
           out = handler(
               astral_candidate_id, payload,
               source_id=source_id, thread_ts=anchor_ts, debug=debug, **extra,
           )
   ```

   ⚠️ **Decision: `artifact_key=` only when the entry declares it.** `insert_slack_meteorite` and `contact_command_check_status` don't accept the kwarg, so passing it unconditionally would break `/add-job` and `/check-status`.

7. **`ctype` default.** In `_handle_slack_event_body`, replace

   ```python
       # channel_type (and private channels use C… ids), so ask Slack; fail closed.
       if etype == "app_mention":
   ```

   with:

   ```python
       # channel_type (and private channels use C… ids), so ask Slack; fail closed.
       ctype = None
       if etype == "app_mention":
   ```

8. **Public-channel refusal.** Directly inside `if ctype not in CONTACT_CONFIG["allowed_channel_types"]:` and before its existing `logger.debug(` line, insert:

   ```python
               # AST-2206: a private_channel_only command gets the fixed refusal (no resolve, no handler).
               # Anything else, and a failed type lookup (ctype None), still drops silently.
               refused = parse_contact_command(event.get("text") or "") if ctype else None
               if refused is not None and CONTACT_CONFIG["commands"][refused[0]].get("private_channel_only"):
                   turn_out = _post_contact_command_notice(
                       command_id=refused[0], outcome="refused",
                       text=CONTACT_CONFIG["private_channel_only_reply_text"],
                       channel=mention_channel, thread_ts=event.get("thread_ts"),
                       message_ts=event.get("ts"), debug=debug,
                   )
                   result = {
                       "accepted": True, "event_id": event_id, "event_type": etype,
                       "channel": mention_channel, "reason": "private_channel_only", "estelle_turn": turn_out,
                   }
                   _emit_listen_info(result, etype, mention_channel, turn_out)
                   return result
   ```

   ⚠️ **Decision: no sender resolve for the public refusal.** The refusal reveals nothing about any candidate, and the gate sits before `resolve_slack_user` today. Resolving here would add a Slack/DB round trip to public traffic for no behavior. The listen line's candidate is therefore `-`.

   ⚠️ **Decision: a failed channel-type lookup (`ctype` None) stays silent.** It might really be the candidate's private channel, so a "only in the private channel" refusal there would be wrong. The existing exception log covers it. Non-`private_channel_only` commands (`/add-job`, `/check-status`) keep the silent drop, so `TestAst2061PrivateChannelGate` is unaffected.

9. **`private_channel` flag.** Directly after the gate block's `            return {"accepted": False, "reason": "channel_not_private"}` and before `    text = event.get("text") or ""`, insert:

   ```python
       # AST-2206: private_channel_only commands and the draft thread run only on a private-channel @mention.
       private_channel = etype == "app_mention" and ctype == _SLACK_PRIVATE_CHANNEL_TYPE
   ```

   (A `message` event only reaches this point as a DM. Non-DM `message` events already returned at `not_dm`.)

10. **Pass it to the runner.** In the `result["estelle_turn"] = _run_contact_command(` call, directly after `                        candidate_state=result.get("candidate_state"),`, add `                        private_channel=private_channel,`.

11. Run the Stage 0 step 3 check with `N=1`. Commit: `git add src/core/contact.py && git commit -m "code(AST-2212): private-channel-only commands on the channel's candidate, refusal, payload-optional, artifact key"`, then `git push origin HEAD:sub/AST-2206/AST-2212-contact-wiring-draft-thread`.

## Stage 2: `/draft-` handler

**Done when:** the Stage 0 step 3 check passes with `N=2`. Expected ruff delta: `UP006` +1, `UP045` +2.

1. **Imports.**
   - Directly after `import time`, add `import uuid`.
   - Directly after `from collections import OrderedDict`, add `from datetime import datetime, timezone`.
   - In the `from src.core.candidate import (` list, directly after `    get_candidate,`, add `    get_candidate_current,`.
   - In the `from src.utils.config import (` list, add `    CANDIDATE_LIBRARY_CONFIG,` directly before `    CONTACT_CONFIG,`, and add `    CONTACT_CONTEXT_COMMAND_CONFIG,` directly after `    CONTACT_CONFIG,`.
   - Replace `from src.utils.logging import get_logger, log_debug` with `from src.utils.logging import flush_log_buffer, get_logger, log_batch_id, log_debug`.

2. **Draft helpers + handler.** Directly after `_post_contact_command_notice` (its final `    return {"ok": True, "outcome": command_id, "command": summary, "slack_post": post}`) and before `def _run_contact_command(`, insert:

   ```python
   def _contact_task_ctx(cid: str, row: dict) -> dict:
       """do_task ctx on the candidate's key, built like the Estelle turn's (no blob base_resume, AST-1585)."""
       cd = copy.deepcopy(row.get("candidate_data")) if isinstance(row.get("candidate_data"), dict) else {}
       arts = cd.get("artifacts")
       if isinstance(arts, dict) and "base_resume" in arts:
           cd["artifacts"] = {k: v for k, v in arts.items() if k != "base_resume"}
       return {
           "astral_candidate_id": cid,
           "candidate_data": cd,
           "candidate_api_keys": dict(row.get("candidate_api_keys") or {}),
       }


   def _run_contact_ledgered_task(task_key: str, *, cid: str, row: dict, live_content: str, debug: bool) -> dict:
       """One do_task under its own dispatch_ledger batch, so the run lands in agent_data for the candidate.

       list_agent_data_runs joins agent_data to dispatch_ledger on batch_id, and do_task stores prompt
       blocks only under an active batch. Same ledger shape as intake.validate_preamble_answer.
       Returns the do_task result plus batch_id.
       """
       # Late import avoids core→agent cycles at module load.
       from src.core.agent import compute_batch_cost, do_task

       batch_id = f"contact-{task_key}-{uuid.uuid4()}"
       started_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
       logger.debug("Calling save_dispatch_ledger: [batch_id=%s, candidate_id=%s]", batch_id, cid)
       database.save_dispatch_ledger(
           batch_id, f"contact-{task_key}", cid, started_at, entity_type="candidate", batch_size=1
       )
       token = log_batch_id.set(batch_id)
       try:
           logger.debug("Calling agent.do_task: [task_key=%s, index=%s, batch_id=%s]", task_key, cid, batch_id)
           result = asyncio.run(
               do_task(
                   task_key,
                   live_content=live_content,
                   index=cid,
                   ctx=_contact_task_ctx(cid, row),
                   debug=debug,
                   store_agent_data=True,
               )
           )
           logger.debug("Response from agent.do_task: %s", result)
           ok = isinstance(result, dict) and bool(result.get("success"))
           logger.debug("Calling update_dispatch_ledger: [batch_id=%s, ok=%s]", batch_id, ok)
           database.update_dispatch_ledger(
               batch_id,
               status="COMPLETED" if ok else "FAILED",
               completed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
               total_processed=1,
               total_passed=int(ok),
               total_failed=int(not ok),
               total_cost=compute_batch_cost(batch_id),
           )
           return {**(result if isinstance(result, dict) else {}), "batch_id": batch_id}
       finally:
           flush_log_buffer()
           log_batch_id.reset(token)


   def _contact_transcript_lines(messages: list) -> List[str]:
       """`[<poster>] <text>` per Slack message, in the given order; untrimmed (full history / whole thread)."""
       lines = []
       for m in messages:
           if not isinstance(m, dict):
               continue
           who = m.get("user") or m.get("bot_id") or "unknown"
           # A reply carries its parent's thread_ts; a parent's thread_ts (when present) equals its own ts.
           reply = m.get("thread_ts") and m.get("thread_ts") != m.get("ts")
           lines.append(f"[{who}]{' (thread reply)' if reply else ''} {m.get('text') or ''}")
       return lines


   @_with_log_debug
   def contact_command_draft_context(
       candidate_id: str,
       payload: str,
       *,
       source_id: str,
       thread_ts: Optional[str] = None,
       artifact_key: Optional[str] = None,
       debug: bool = False,
   ) -> dict:
       """CONTACT_CONFIG["commands"] code handler for /draft-<context> (AST-2206).

       Principal Estelle drafts the piece from the mapped channel's full history (thread replies
       included), the candidate's name / context / contact, and the current saved body (read-current).
       Never saves. payload is ignored (payload_optional entry); source_id and thread_ts are accepted
       for the runner's call shape. Returns {ok, meteorite_id (always None), error, reply_text}.
       """
       cid = (candidate_id or "").strip()
       key = (artifact_key or "").strip()
       ctx_row = next((m for m in CONTACT_CONTEXT_COMMAND_CONFIG.values() if m["artifact_key"] == key), None)
       row = get_candidate(cid) if cid else None
       cd = row.get("candidate_data") if isinstance(row, dict) else None
       cd = cd if isinstance(cd, dict) else {}
       contact = cd.get("contact") if isinstance(cd.get("contact"), dict) else {}
       channel = str(contact.get("slack_channel_id") or "").strip()
       miss = (
           "unknown_artifact_key" if ctx_row is None
           else "no_candidate" if not isinstance(row, dict)
           else "no_slack_channel" if not channel
           else None
       )
       if miss:
           logger.warning(
               "%s | contact draft of %r not run — %s\n  Nothing was drafted", cid or "-", artifact_key, miss
           )
           return {"ok": False, "meteorite_id": None, "error": miss, "reply_text": None}

       logger.debug("Calling fetch_full_conversation_history: [channel=%s, include_thread_replies=True]", channel)
       history = fetch_full_conversation_history(channel=channel, include_thread_replies=True)
       logger.debug("Response from fetch_full_conversation_history: %s", history)
       logger.debug("Calling get_candidate_current: [candidate_id=%s, artifact_key=%s]", cid, key)
       current = get_candidate_current(cid, key)
       logger.debug("Response from get_candidate_current: %r", current)

       # Context blob minus the six context pieces: their current bodies live in artifacts (read-current),
       # and the one being drafted rides below as its own section.
       piece_fields = {m["artifact_key"].rsplit(".", 1)[-1] for m in CONTACT_CONTEXT_COMMAND_CONFIG.values()}
       context = cd.get("context") if isinstance(cd.get("context"), dict) else {}
       packet = {
           "name": {k: row.get(k) for k in CANDIDATE_LIBRARY_CONFIG["name_columns"]},
           "context": {k: v for k, v in context.items() if k not in piece_fields},
           "contact": contact,
       }
       live_content = "\n".join([
           f"artifact_key={key}",
           "",
           "## Candidate",
           json.dumps(packet, indent=2, ensure_ascii=False, default=str),
           "",
           f"## Currently saved {ctx_row['label']}",
           current if isinstance(current, str) and current.strip() else "(nothing saved yet)",
           "",
           "## Slack channel history (oldest first; every top-level post and thread reply)",
           *_contact_transcript_lines(history),
       ])

       result = _run_contact_ledgered_task(ctx_row["draft_task"], cid=cid, row=row, live_content=live_content, debug=debug)
       parsed = result.get("parsed_response") if isinstance(result.get("parsed_response"), dict) else {}
       draft = parsed.get("draft") if isinstance(parsed.get("draft"), str) else ""
       note = parsed.get("note") if isinstance(parsed.get("note"), str) else ""
       ok = bool(result.get("success")) and bool(draft.strip())
       if not ok:
           logger.warning(
               "%s | contact draft of %s failed — %s\n  No draft was posted unless Estelle returned draft text",
               cid, key, result.get("error") or "no draft text",
           )
       # Estelle's failure status still carries one plain sentence in draft (what is missing) — post it.
       reply = (draft.strip() + (f"\n\n{note.strip()}" if note.strip() else "")) if draft.strip() else None
       return {
           "ok": ok,
           "meteorite_id": None,
           "error": None if ok else (result.get("error") or "no_draft"),
           "reply_text": reply,
       }
   ```

   ⚠️ **Decision: each draft (and revise) run opens its own `dispatch_ledger` batch.** AC 8 counts runs with `list_agent_data_runs(candidate_id="X", task_key=…)`. That joins `agent_data` to `dispatch_ledger` on `batch_id`, and `do_task` stores prompt blocks only when a batch is active (`batch_id = hop_ledger_batch_id or log_batch_id.get()`). The Contact Estelle turn opens none today, so it stores nothing. Without a ledger, AC 8–10 cannot pass. The helper copies `intake.validate_preamble_answer`'s shape (one ledger row on the candidate, `log_batch_id` held for the call, COMPLETED/FAILED + `compute_batch_cost` after, `flush_log_buffer` + reset in `finally`), written in `contact.py` because AC 4 forbids touching `intake.py`. These rows are run audit, not entity writes, so the pinhole kind `read artifact (LLM draft, no artifact write)` still holds: no artifact, candidate, job, or meteorite row is written.

   ⚠️ **Decision: full history, untrimmed.** The packet carries every message `fetch_full_conversation_history(…, include_thread_replies=True)` returns, with no `turn_context_message_limit` / `turn_context_text_max_chars` trim (those are the Estelle turn's knobs). The parent says "full history", and no cap was approved. Thread replies are marked `(thread reply)` so the drafter can tell a side conversation from a top-level post.

   ⚠️ **Decision: the six context pieces come from read-current, not the blob.** `candidate_data["context"]` still has legacy `strengths` / `deal_breakers` / … fields. The packet drops those six leaf names (derived from `CONTACT_CONTEXT_COMMAND_CONFIG`'s artifact keys, no literals) and carries the drafted piece's current body from `get_candidate_current` in its own section (`patt.artifact.read-current`: "never stale blob copies"). `raw_resume`, `raw_profile`, and the other context keys stay.

   ⚠️ **Decision: reply text = the draft, then the note as its own paragraph when Estelle gives one.** #1's prompt addresses `note` "to Susan and the candidate", so it is shown. On Estelle's `failure` status, #1's prompt puts one plain sentence (what is missing) in `draft`, so that still posts, with `ok: False` and a warning. Only an empty `draft` posts nothing, and then the existing hear-ack answers.

   ⚠️ **Decision: no try/except in the handler.** A Slack or DB exception propagates to the runner and is logged once at `_handle_slack_event_body`'s existing command `except` (`stat.logging.error`). Predictable misses (unknown key, no candidate, no channel, no draft) each get one warning naming the candidate and why (`stat.logging.warning`).

   `CANDIDATE_LIBRARY_CONFIG["name_columns"]` is `("first", "last", "full", "pronouns")`. Tokens like `{$FIRST_NAME}` resolve from the DB row through `ctx["astral_candidate_id"]` (`agent._token_view_for_do_task`), the same as the Estelle turn.

3. Run the Stage 0 step 3 check with `N=2`. Commit: `git add src/core/contact.py && git commit -m "code(AST-2212): /draft-<context> handler — full threaded history packet, ledgered principal draft task"`, then `git push origin HEAD:sub/AST-2206/AST-2212-contact-wiring-draft-thread`.

## Stage 3: Contact draft thread: routing and revise turn

**Done when:** the Stage 0 step 3 check passes with `N=3`. Expected ruff delta: `UP045` +2, `TRY401` +1.

1. **Import.** In the `from src.utils.config import (` list, directly after `    CONTACT_CONTEXT_COMMAND_CONFIG,`, add `    CONTACT_DRAFT_THREAD_CONFIG,`.

2. **Root detection + revise turn.** Directly after `contact_command_draft_context` (its final `    }` closing the return dict) and before `def _run_contact_command(`, insert:

   ```python
   def _draft_thread_root_command(channel: str, thread_ts: str, *, debug: bool = False) -> Optional[str]:
       """Command id when the thread's root message is a /draft-<context> command; else None (AST-2206)."""
       # refresh: a cache entry can be append-built (our draft reply, the inbound) and lack the root.
       ctx = load_slack_conversation_context(channel=channel, thread_ts=thread_ts, refresh=True, debug=debug)
       root = next(
           (m for m in ctx.get("messages") or [] if isinstance(m, dict) and m.get("ts") == thread_ts), None
       )
       command = parse_contact_command(root.get("text") or "") if root else None
       # Draft entries are the ones whose handler is this module's draft handler — no command-id literal.
       draft_handler = f"{__name__}.contact_command_draft_context"
       if command is None or CONTACT_CONFIG["commands"][command[0]]["handler"] != draft_handler:
           return None
       return command[0]


   @_with_log_debug
   def run_contact_draft_revise_turn(
       *,
       channel: str,
       text: str,
       thread_ts: str,
       message_ts: Optional[str] = None,
       root_command_id: str,
       debug: bool = False,
   ) -> dict:
       """Contact Estelle's reply to an @mention in a /draft-<context> thread (AST-2206 Contact draft thread).

       Stateless: the thread is identified by its root command. Acts on the channel's mapped candidate.
       Live content is the artifact key, the whole thread transcript, and the current saved body.
       The reply (plus the revised draft when Estelle gives one) posts in-thread. Never saves.
       """
       key = CONTACT_CONFIG["commands"][root_command_id]["artifact_key"]
       label = next(m["label"] for m in CONTACT_CONTEXT_COMMAND_CONFIG.values() if m["artifact_key"] == key)
       logger.debug("Calling get_candidate_id_for_slack_channel: [channel=%s]", channel)
       cid = get_candidate_id_for_slack_channel(channel, debug=debug)
       logger.debug("Response from get_candidate_id_for_slack_channel: %s", cid)
       if cid is None:
           return _post_contact_command_notice(
               command_id=root_command_id, outcome="unmapped",
               text=CONTACT_CONFIG["unmapped_channel_reply_text"],
               channel=channel, thread_ts=thread_ts, message_ts=message_ts, debug=debug,
           )
       row = get_candidate(cid) or {}

       # Whole thread: full channel history with replies, kept to this thread (no page cap).
       logger.debug("Calling fetch_full_conversation_history: [channel=%s, include_thread_replies=True]", channel)
       history = fetch_full_conversation_history(channel=channel, include_thread_replies=True)
       logger.debug("Response from fetch_full_conversation_history: %s", history)
       thread = [m for m in history if isinstance(m, dict) and thread_ts in (m.get("ts"), m.get("thread_ts"))]
       logger.debug("Calling get_candidate_current: [candidate_id=%s, artifact_key=%s]", cid, key)
       current = get_candidate_current(cid, key)
       logger.debug("Response from get_candidate_current: %r", current)
       live_content = "\n".join([
           f"artifact_key={key}",
           "",
           f"## Currently saved {label}",
           current if isinstance(current, str) and current.strip() else "(nothing saved yet)",
           "",
           "## Draft thread (oldest first)",
           *_contact_transcript_lines(thread),
       ])

       # Late import avoids core→agent cycles at module load.
       from src.core.agent import conversational_turn_from_do_task_result

       result = _run_contact_ledgered_task(
           CONTACT_DRAFT_THREAD_CONFIG["revise_task_key"], cid=cid, row=row, live_content=live_content, debug=debug
       )
       turn = conversational_turn_from_do_task_result(result)
       parsed = result.get("parsed_response") if isinstance(result.get("parsed_response"), dict) else {}
       revised = parsed.get("revised_draft") if isinstance(parsed.get("revised_draft"), str) else ""
       reply = turn.get("reply") if isinstance(turn.get("reply"), str) else ""
       outcome = turn.get("outcome")
       slack_post = None
       # Same post rule as the Estelle turn: success/concern with a non-empty reply.
       if turn.get("success") and reply.strip() and outcome in ("success", "concern"):
           reply_ts, reply_broadcast = _contact_reply_placement(thread_ts, message_ts)
           slack_post = contact_post_message(
               channel=channel,
               text=format_contact_reply_text(reply.strip() + (f"\n\n{revised.strip()}" if revised.strip() else "")),
               thread_ts=reply_ts,
               reply_broadcast=reply_broadcast,
               debug=debug,
           )
       else:
           logger.warning(
               "%s | contact draft revise of %s failed — %s\n  Estelle did not reply in the draft thread",
               cid, key, result.get("error") or f"outcome {outcome}",
           )
       ok = bool(turn.get("success"))
       return {
           "ok": ok,
           "outcome": outcome,
           "reply": reply or None,
           "admin_aside": turn.get("admin_aside"),
           "skill_results": [],
           "slack_post": slack_post,
           "error": None if ok else result.get("error"),
           "command": {"id": root_command_id, "mode": "revise", "ok": ok, "meteorite_id": None, "error": None},
       }
   ```

   ⚠️ **Decision: root detection reads one refreshed thread page.** `conversations.replies` returns the root first, so one `load_slack_conversation_context(…, refresh=True)` call (the existing page of `context_history_limit` = 50) always contains it. `refresh=True` is required. `contact_post_message` and the inbound append create the `(channel, thread_ts)` cache entry with only the messages they append, so a cache hit can lack the root. That refetch also re-warms the cache the normal Estelle turn reads for non-draft threads. Draft entries are found by handler path (`f"{__name__}.contact_command_draft_context"`), the same trick #2 used, so `src/core/` holds no command id (AC 3).

   ⚠️ **Decision for Susan: the "whole thread transcript" is the full channel fetch filtered to this thread, with no page cap.** The cheaper option is reusing the detection page, but that is capped at 50 messages oldest-first, so a long thread would silently lose its newest messages, including the @mention being answered. Your rule is no caps without approval, so this plan fetches everything. The cost is one full channel crawl (history pages + one `conversations.replies` per threaded post) per revise turn, the same crawl `/draft-` already does. If you'd rather accept the 50-message page, Stage 3 swaps the `fetch_full_conversation_history` call for the detection page. That is a plan revision, not a build-time change.

   ⚠️ **Decision: reply text = Estelle's reply, then the revised draft as its own paragraph** when `revised_draft` is present, ready for `/save-…` copy. Posting follows the Estelle turn's rule (success/concern with a non-empty reply). Otherwise one warning names the candidate and the reason, and the existing hear-ack answers. No `land_calls` or contact-task markup is processed: the revise task's schema has neither.

   ⚠️ **Decision: an unmapped channel gets the unmapped reply here too.** A `/draft-` root in an unmapped channel already got the unmapped reply, so a mention under it answers the same way rather than running against the sender's own candidate.

3. **Routing.** In `_handle_slack_event_body`, replace

   ```python
               command = parse_contact_command(text) if known else None
               if command is None:
                   # AST-1561: paste recovery before Estelle turn (no re-classify).
   ```

   with:

   ```python
               command = parse_contact_command(text) if known else None
               # AST-2206 Contact draft thread: a non-command @mention in a private-channel thread whose root
               # is a /draft-<context> command runs the revise turn. Un-mentioned replies already drop at not_dm.
               thread_root = event.get("thread_ts")
               draft_root = (
                   _draft_thread_root_command(channel, thread_root, debug=debug)
                   if known and command is None and private_channel
                   and isinstance(thread_root, str) and thread_root and thread_root != msg_ts
                   else None
               )
               if command is None and draft_root is None:
                   # AST-1561: paste recovery before Estelle turn (no re-classify).
   ```

4. **Revise branch.** Directly after the command branch's

   ```python
                       result["estelle_turn"] = {"ok": False, "error": str(exc)}
               elif paste_out.get("applied") and paste_out.get("result", {}).get("ok"):
   ```

   insert the new branch between those two lines, so the code reads:

   ```python
                       result["estelle_turn"] = {"ok": False, "error": str(exc)}
               elif draft_root is not None:
                   try:
                       result["estelle_turn"] = run_contact_draft_revise_turn(
                           channel=channel,
                           text=text,
                           thread_ts=thread_root,
                           message_ts=msg_ts if isinstance(msg_ts, str) else None,
                           root_command_id=draft_root,
                           debug=debug,
                       )
                   except Exception as exc:
                       logger.exception(
                           "%s | contact draft revise turn %s\n  %s: %s\n  The inbound event is accepted; Estelle did not complete this turn",
                           result.get("astral_candidate_id") or "-", draft_root, type(exc).__name__, exc,
                       )
                       result["estelle_turn"] = {"ok": False, "error": str(exc)}
               elif paste_out.get("applied") and paste_out.get("result", {}).get("ok"):
   ```

   ⚠️ **Decision: draft-thread mentions skip paste recovery**, like commands. A reply in the draft discussion is not a pasted job description, and paste recovery would swallow it for a candidate with a BOT_BLOCKED meteorite.

   ⚠️ **Decision: no mention-gate code.** Un-mentioned private-channel replies arrive as `message` events and already return at `not_dm`. Only `app_mention` reaches routing (AC 11). The existing listen line and hear-ack tail run for the revise turn unchanged (`<root command id>:revise` in `action:`).

   ⚠️ **Decision: a Slack error during root detection propagates.** It is logged once by `_run_handle_slack_event_background` (`stat.logging.error`), with no hear-ack. Falling through to the normal Estelle turn instead would run the wrong agent (AC 10's fail case) on the same failing Slack read.

5. Run the Stage 0 step 3 check with `N=3`. Commit: `git add src/core/contact.py && git commit -m "code(AST-2212): Contact draft thread — routing and contact Estelle revise turn"`, then `git push origin HEAD:sub/AST-2206/AST-2212-contact-wiring-draft-thread`.

## Canon alignment (plan-stage)

- **`patt.contact.command-intercept`** (read in full): every context command stays a registry row with a `src.core.*` handler, intercepted before paste recovery and the turn, with no command-id literal in `src/core/` (AC 3: the draft entry is found by handler path, the refusal and unmapped checks by entry flag). Arc step 4 behavior is amended at runtime exactly as the parent requests: (a) `payload_optional` skips the usage short-circuit, (b) `artifact_key=` reaches the handler, (c) `private_channel_only` acts on the channel's candidate with a fixed refusal elsewhere. Arc step 5 still holds: one `_emit_listen_info` per event, with `<command id>:<mode>` leading `action:` for runs, refusals, unmapped replies, and revise turns. The pattern *text* amendment and the new **Contact draft thread** pattern doc are out of this Scope (see Scope gate).
- **`patt.artifact.read-current`** (read in full): the draft packet, the revise packet, and (#2's) `/show-` read the current body through `get_candidate_current`. Blob copies of the six pieces are excluded from the draft packet.
- **`stat.logging.info.contact`**, **`stat.logging.debug`**, **`stat.logging.warning`**, **`stat.logging.error`**: id-only at plan stage. Placement follows the file's existing conventions: Calling/Response around every new callee call (`get_candidate_id_for_slack_channel`, `fetch_full_conversation_history`, `get_candidate_current`, `save_dispatch_ledger`, `do_task`, `update_dispatch_ledger`, handler call with `artifact_key`); one warning per failed draft / revise naming the candidate and why; exceptions logged once (handler and helpers don't catch; the revise branch's `except` mirrors the existing command and turn branches). `build-child` §8 checks the statute text. A conflict there means stop and comment, not adapt silently.

## Acceptance trace

| Ticket AC | Where satisfied |
|-----------|-----------------|
| 3 No command literals in core | All stages (handler-path / flag lookups); grep in every Stage 0 step 3 check |
| 4 No intake | No stage touches `src/core/intake.py`; ledger shape copied, not imported |
| 5 Show | Stage 1 steps 4–6, 9–10 (mapped candidate, payload-optional, `artifact_key=` to #2's handler); smoke stage 1 |
| 6 Save | Stage 1 steps 4, 6 (mapped candidate → #2's sanitize + `save_candidate_data`, identical no-op there); smoke stage 1 |
| 7 Save needs text | Stage 1 step 5 (`save-` entries are not payload-optional); smoke stage 1 |
| 8 Draft | Stage 2 step 2 (ledgered `draft_task` on the mapped candidate, no save) + #1's `always_no_share` placement; smoke stage 2 |
| 9 Draft reads threads | Stage 2 step 2 (`include_thread_replies=True`, untrimmed `live_content` stored as the prompt); smoke stage 2 |
| 10 Revise | Stage 3 steps 2–4 (revise task under its own ledger, in-thread reply, normal turn not run); smoke stage 3 |
| 11 Mention gate | Existing `not_dm` drop; routing only on `app_mention` (Stage 3 step 3) |
| 12 Unmapped channel | Stage 1 step 4 (no handler `Calling` line); smoke stage 1 |
| 13 Refusal outside private channels | Stage 1 steps 4 (DM), 8 (public), non-command public still silent; smoke stage 1 |

Live Slack / DB checks of AC 5–13 (version counts, `list_agent_data_runs`, `get_agent_data`) are Betty's at `qa-child` and Susan's at UAT. The smoke proves the wiring with those edges stubbed.

**Notes for Betty (test tree is hers):** `TestAst2061PrivateChannelGate` keeps passing (it uses `/add-job`, which is not `private_channel_only`). New behavior worth pinning: refusal (public, mpim, DM), unmapped, mapped-candidate substitution, payload-optional run, `artifact_key=` only when declared, draft packet (thread replies, stale-blob exclusion, ledger COMPLETED/FAILED, batch reset), root detection (refresh, non-draft root, command-in-thread), revise post rule, and the paste-recovery skip.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2212
**Overall:** APPROVED
**Corpus:** 0d01e20d2b313a4e35cf3d07434b6cd69f615768
**Publish ref:** `origin/sub/AST-2206/AST-2212-contact-wiring-draft-thread` @ `17ac6412bb63a19ed6caada3fe1b02468e2ef5f1`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.contact.command-intercept | A | | |
| patt.artifact.read-current | A | | |
| stat.logging.info.contact | A | | |
| stat.logging.debug | A | | |
| stat.logging.warning | A | | |
| stat.logging.error | A | | |

## Traceability

AC3→Stages 1–3 + smoke grep; AC4→ledger helper in `contact.py` only; AC5–7→Stage 1 + smoke §1; AC8–9→Stage 2 + smoke §2; AC10–11→Stage 3 + smoke §3; AC12–13→Stage 1 (gate/refusal) + smoke §1. Parent pinhole AC / live DB proofs → qa-child & UAT per plan.

## Findings

### acceptable

- **Location:** Scope gate / Canon alignment  
  **Finding:** Runtime implements intercept amendments (a–c) and draft-thread behavior; `patt.contact.command-intercept` text and **Contact draft thread** pattern doc remain out of file scope (same split as AST-2210).  
  **Recommendation:** Track canon edits on the epic; do not block build.

- **Location:** Stage 0 smoke vs Betty/UAT  
  **Finding:** AC 5–13 integration proofs (versions, `list_agent_data_runs`, `get_agent_data`) are stubbed in smoke; plan assigns live checks to qa-child/UAT.  
  **Recommendation:** Keep; smoke is wiring-only by design.

### discuss

- **Location:** Stage 3 revise turn — full `fetch_full_conversation_history` per mention  
  **Finding:** Plan chooses uncapped full-channel crawl for revise (Susan no-cap rule); cost is explicit vs 50-message cache alternative.  
  **Recommendation:** Build as written unless Susan revises the plan to the cheaper page-only path.

- **Location:** `_SLACK_PRIVATE_CHANNEL_TYPE = "group"`  
  **Finding:** Mapped-candidate substitution applies only to private-channel `app_mention` with Slack `group`; DMs use the refusal gate via `private_channel_only` + `private_channel=False`, which matches AC 13 smoke.  
  **Recommendation:** No change unless mpim/private-channel taxonomy needs a follow-up ticket.

context_tokens≈68000
