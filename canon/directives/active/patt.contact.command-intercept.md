---
id: patt.contact.command-intercept
kind: pattern
scope: contact
point: >
  A leading Slack /command runs its registry handler before paste recovery and the LLM turn, then replies per its configured mode.
---

# Abstract

Some Slack requests need a deterministic result, not a judgment call. When a
candidate types `@Estelle /add-job <link>`, the job must land as a meteorite.
Hoping Estelle's LLM turn chooses the right action is not enough. A Contact
command is that deterministic path. The command id, the code that runs, and
whether Estelle also talks about the result are all declared in config. Contact
recognizes the command, runs it before any other inbound handling, and replies
the way the registry says. Without this, every new command would grow its own
string match, its own ordering against paste recovery, and its own reply rules
somewhere in `src/core/contact.py`.

# Arc

1. **Config declares the command.** `CONTACT_CONFIG["commands"]` in
   `src/utils/config.py` is keyed by command id, the bare token after `/`.
   Each entry declares:
   - `handler`, a dotted path under `src.core.` to a sync callable
     `(candidate_id, payload, *, source_id, thread_ts, debug)` that returns an
     `{ok, meteorite_id, error}` dict
   - `mode`, either `code` or `agent`
   - `description`
   - `usage_reply_text`
   - `ack_reply_template`, which carries a `{meteorite_id}` placeholder

   Import-time asserts guard the shape, the mode vocabulary, and id
   collisions with `CONTACT_CONFIG["skills"]` and `CONTACT_TASK_CONFIG`.
2. **Contact parses only the first token.** `parse_contact_command` in
   `src/core/contact.py` strips leading `<@U…>` mentions (an optional
   `|label` is allowed). It then matches `/<token>` against the registry and
   nothing else. On a hit it unwraps Slack `<http(s)://…|label>` and
   `<http(s)://…>` markup in the payload and returns `(command_id, payload)`.
   It returns `None` when the message doesn't start with a registered command,
   including a command mentioned mid-sentence.
3. **Contact intercepts before paste recovery and the turn.**
   `_handle_slack_event_body` runs known/unknown recognition first. An unbound
   sender gets the unknown-recognition reply and no command runs. For a bound
   sender with a parsed command, it calls `_run_contact_command` **instead of**
   `try_meteorite_apply_paste_from_slack` and the normal
   `run_contact_estelle_turn`. A command event never enters BOT_BLOCKED paste
   recovery.
4. **The runner replies per mode.** `_run_contact_command` resolves the handler
   with `_resolve_contact_task_handler` and returns the `estelle_turn` dict.
   - An empty payload, in either mode, gets `usage_reply_text` through
     `contact_post_message` in-thread. No handler runs and no turn runs.
   - `code` runs the handler, then posts the formatted `ack_reply_template`
     in-thread only when the handler returns `ok`. No LLM turn runs.
     `estelle_turn.outcome` is the command id.
   - `agent` runs the handler, then calls `run_contact_estelle_turn` exactly
     once. That call passes the command result as JSON in `extra_context`,
     which renders under `## Command result (this inbound event)` in live
     content. Estelle's turn is the reply.
5. **Contact records it once.** The shared tail of `_handle_slack_event_body`
   calls `_emit_listen_info`. That function puts `<command id>:<mode>` and
   `meteorite:<id>` at the front of the `action:` list on the single
   `stat.logging.info.contact` line. If no reply posted `ok`, the existing
   hear-ack fallback fires.

# Canonical implementation

- Registry: `CONTACT_CONFIG["commands"]` and its asserts in `src/utils/config.py`.
  The `CONTACT_TASK_CONFIG` collision assert sits after that config's own assert
  loop, because `CONTACT_TASK_CONFIG` is defined later in the file.
- Parse: `parse_contact_command`, `_CONTACT_COMMAND_RE`, and `_SLACK_LINK_RE` in
  `src/core/contact.py`.
- Run and reply: `_run_contact_command`, plus the `extra_context` parameter on
  `run_contact_estelle_turn`, in `src/core/contact.py`.
- Intercept: the `command = parse_contact_command(text) if known else None`
  branch in `_handle_slack_event_body`.
- First consumer: `add-job` → `src.core.meteorite.insert_slack_meteorite`, `code` mode.

`src/core/` holds no command-id or mode-per-command literals. Adding a command
means one registry row plus a `src.core.*` handler, and nothing else.

# Data coupling

The handler owns its own writes. `insert_slack_meteorite` inserts through the
meteorite insert path. Contact only supplies the inputs:
- `candidate_id` (the bound candidate)
- the unwrapped `payload`
- `source_id = "<channel>:<message ts>"`
- `thread_ts`, which is the reply thread (`thread_ts or message ts`), so later
  nags land in the same Slack thread

The handler's `meteorite_id` is the only result field the reply and the listen
line read.

# Configuration

`CONTACT_CONFIG["commands"]` is the single source for which commands exist,
what runs, and how Estelle replies. A command's mode is a config edit, not a
code edit. Reply texts (`usage_reply_text`, `ack_reply_template`) live on the
entry. A command id must not collide with `CONTACT_CONFIG["skills"]` keys or
`CONTACT_TASK_CONFIG` keys.

# Related Directives

- `stat.logging.info.contact`
- `stat.logging.debug`
- `stat.logging.warning`
- `stat.logging.error`

# When this doesn't apply

- Contact tasks that Estelle emits as `~~/<task_key> …~~` reply markup. Those are
  `CONTACT_TASK_CONFIG` items dispatched after her turn, not inbound commands.
- Contact skills (`CONTACT_CONFIG["skills"]`): ACL-gated entity saves that
  Estelle requests through `skill_calls`.
- Registered Slack slash commands (Slack's own `/command` API). This pattern
  covers mention-first text in channels and DMs only.
- Free-text job sharing without a command. That path still runs through the
  Estelle turn and `land_calls`.

# Notes

- In `code` mode a handler soft-fail posts no ack. The AST-1101 hear-ack is the
  candidate's reply. The handler logs the miss itself.
- In `agent` mode the Estelle turn can still emit `land_calls`. Their existing
  loop may call `apply_paste` or `contact_land_meteorite`, so the
  "no paste recovery" guarantee in Arc step 3 holds only up to the turn. `add-job`
  ships in `code` mode.
