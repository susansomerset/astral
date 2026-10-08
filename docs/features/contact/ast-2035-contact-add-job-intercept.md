# AST-2035 — Contact command registry + /add-job intercept

**Linear:** [AST-2035](https://linear.app/astralcareermatch/issue/AST-2035)
**Parent:** [AST-2032](https://linear.app/astralcareermatch/issue/AST-2032) — Let Estelle post a meteorite from Slack
**Publish ref:** `origin/sub/AST-2032/AST-2035-contact-add-job-intercept`

This ticket covers the Contact side of `@Estelle /add-job`. It adds a `commands` registry inside `CONTACT_CONFIG`, keyed by command id (handler dotted path, `code`/`agent` mode, description, usage text, ack template). It adds a parse helper in `src/core/contact.py` that recognizes `/<command>` only as the first token after leading `<@U…>` mentions and unwraps Slack link markup. It also adds an intercept in `_handle_slack_event_body` that runs for a bound sender, after recognition and before BOT_BLOCKED paste recovery and the Estelle turn. In `code` mode the intercept posts the fixed ack (or usage) with no LLM turn. In `agent` mode it runs one Estelle turn that sees the command result through a new optional `extra_context` parameter on `run_contact_estelle_turn`. `add-job` resolves to sibling AST-2034's `src.core.meteorite.insert_slack_meteorite` (already on `origin/ftr/AST-2032-estelle-add-job`) and ships in `code` mode. This ticket ships parent AC1–AC7, AC11, and AC12, numbered AC1–AC9 on this ticket. The row insert and the stage hop belong to AST-2034. This ticket does not edit `src/core/meteorite.py`.

## Scope gate

The ticket's `## Scope` names two files: `src/utils/config.py` and `src/core/contact.py`. Every row below is one of them, and every change is a kind the Technical scope names:

- `src/utils/config.py`: the `commands` block inside `CONTACT_CONFIG` plus import-time asserts (shape, mode vocabulary, no collision with `CONTACT_TASK_CONFIG` / `CONTACT_CONFIG["skills"]`).
- `src/core/contact.py`: the parse helper, the intercept in `_handle_slack_event_body`, the mode-driven reply, the optional extra-context parameter on `run_contact_estelle_turn`, and activity/info logging. Extending `_emit_listen_info` so it names the command falls under "activity/info logging".

Reused as-is (no change): `_resolve_contact_task_handler` (generic dotted-path importer), `contact_post_message`, `format_contact_reply_text`, `_contact_listen_info`, and AST-2034's `insert_slack_meteorite(candidate_id, payload, *, source_id, thread_ts=None, debug=False) -> {ok, meteorite_id, error}`. That function soft-fails and already emits the meteorite `NEW` entity info line through `_insert_stage_rows` (AC9's second line).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `CONTACT_CONFIG["commands"]` block with the `add-job` entry. Shape/mode/skills-collision asserts after the existing skills asserts. `CONTACT_TASK_CONFIG` collision assert after that config's assert loop. Docstring index line 62 mention. | utils |
| `src/core/contact.py` | Module docstring line. Two regexes plus public `parse_contact_command`. Private `_run_contact_command`. `run_contact_estelle_turn` gains `extra_context`. `_emit_listen_info` names the command. Intercept in `_handle_slack_event_body`. | core |

No other file is touched. Tests and the bible are Betty's (see **Test impact**).

## Stage 1: Commands registry in `CONTACT_CONFIG`

**Done when:** `python3 -c "from src.utils.config import CONTACT_CONFIG as c; print(c['commands']['add-job']['mode'])"` prints `code`. Temporarily setting that entry's mode to `"bogus"` makes the import fail on an `AssertionError`, and the edit is reverted before commit.

1. In `src/utils/config.py`, inside `CONTACT_CONFIG`, insert this block immediately **after** the closing `},` of the `"skills": { … }` entry and **before** the `# AST-1069: Events API Request URL path` comment:

   ```python
       # AST-2035: Slack commands — `@Estelle /<command id> <payload>`, recognized only as the
       # first token after leading @mentions. handler: sync src.core.* callable
       # (candidate_id, payload, *, source_id, thread_ts, debug) -> {ok, meteorite_id, error}.
       # mode "code": fixed ack/usage post, no LLM turn. mode "agent": one Estelle turn sees the result.
       "commands": {
           "add-job": {
               "handler": "src.core.meteorite.insert_slack_meteorite",
               "mode": "code",
               "description": "Save a job link or pasted job description as a NEW meteorite for staging.",
               "usage_reply_text": "Usage: @Estelle /add-job <job link or pasted job description>",
               # Format with meteorite_id=.
               "ack_reply_template": "Got it. Saved as meteorite {meteorite_id}; I'll stage it from here.",
           },
       },
   ```

2. In `src/utils/config.py`, immediately **after** the existing statement
   `assert set(CONTACT_CONFIG["skills"]["save_candidate_profile"]["allowed_paths"]).issubset(CANDIDATE_LIBRARY_CONFIG["name_columns"])` (ends `)` at ~line 2001) and **before** the `# AST-1049: Manage Email Create` comment, add:

   ```python
   # AST-2035: command registry shape; ids are the bare token after "/" (no whitespace).
   assert isinstance(CONTACT_CONFIG["commands"], dict)
   for _cmd_id, _cmd_meta in CONTACT_CONFIG["commands"].items():
       assert isinstance(_cmd_id, str) and _cmd_id.split() == [_cmd_id] and not _cmd_id.startswith("/"), _cmd_id
       assert isinstance(_cmd_meta, dict), _cmd_id
       assert _cmd_meta.get("mode") in ("code", "agent"), _cmd_id
       for _field in ("handler", "description", "usage_reply_text", "ack_reply_template"):
           assert isinstance(_cmd_meta.get(_field), str) and _cmd_meta[_field].strip(), (_cmd_id, _field)
       assert _cmd_meta["handler"].startswith("src.core.") and _cmd_meta["handler"].count(".") >= 3, _cmd_id
       assert "{meteorite_id}" in _cmd_meta["ack_reply_template"], _cmd_id
       assert _cmd_id not in CONTACT_CONFIG["skills"], _cmd_id
   ```

   (`count(".") >= 3` means `src.core.<module>.<attr>`, which is a module plus an attribute.)

3. In `src/utils/config.py`, immediately **after** the `for _ct_key, _ct_meta in CONTACT_TASK_CONFIG.items():` loop (its last line is `    assert _module_path.startswith("src.core."), _ct_key`), add at module level:

   ```python
   # AST-2035: Contact command ids must not collide with contact-task keys.
   for _cmd_id in CONTACT_CONFIG["commands"]:
       assert _cmd_id not in CONTACT_TASK_CONFIG, _cmd_id
   ```

   ⚠️ **Decision:** This assert lives here and not with the step 2 asserts because `CONTACT_TASK_CONFIG` is defined ~3000 lines after `CONTACT_CONFIG`.

4. In the `src/utils/config.py` module docstring, change line 62 from
   `CONTACT_CONFIG  — Contact listen + debug flags, Slack env-name contracts, skills ACL (AST-1066 / AST-1206; distinct from TASK_CONFIG)`
   to
   `CONTACT_CONFIG  — Contact listen + debug flags, Slack env-name contracts, skills ACL, Slack commands registry (AST-1066 / AST-1206 / AST-2035; distinct from TASK_CONFIG)`.

Compile and lint (see below), then commit: `code(AST-2035): stage 1 — CONTACT_CONFIG commands registry`

## Stage 2: Parse, run, and intercept in `src/core/contact.py`

**Done when:**
- `parse_contact_command("<@UBOT> /add-job <http://www.dice.com/jobs/13234abcd|www.dice.com/jobs/13234abcd>")` returns `("add-job", "http://www.dice.com/jobs/13234abcd")`.
- `parse_contact_command("<@UBOT> /add-job")` returns `("add-job", "")`.
- `parse_contact_command("<@UBOT> can you /add-job this later")` returns `None`.
- With `slack_listen_enabled` / `resolve_slack_user` / `post_message` / `insert_slack_meteorite` patched, `handle_slack_event` on an `app_mention` `/add-job` event for a bound sender returns `estelle_turn.outcome == <command id>` with `slack_post.ok` True. In that run, `do_task` and `try_meteorite_apply_paste_from_slack` are never called.

1. **Module docstring.** In the `src/core/contact.py` module docstring, add this line after the `AST-1515: …` line:
   `AST-2035: leading /<command> intercept via CONTACT_CONFIG["commands"] (code ack or one agent turn).`

2. **Regexes + parse helper.** Directly **after** `strip_contact_task_markup` (before `_resolve_contact_task_handler`), add:

   ```python
   # Leading <@U…> mentions (optional |label), then /<token>, then the rest (may span lines).
   _CONTACT_COMMAND_RE = re.compile(
       r"^(?:\s*<@[A-Z0-9]+(?:\|[^>]*)?>)*\s*/(\S+)(?:\s+(.*))?$",
       re.DOTALL,
   )
   # Slack auto-link markup: <http(s)://…|label> or <http(s)://…> → bare URL.
   _SLACK_LINK_RE = re.compile(r"<(https?://[^|>\s]+)(?:\|[^>]*)?>")


   def parse_contact_command(text: str) -> Optional[Tuple[str, str]]:
       """(command_id, payload) when the first token after mentions is a registered /command; else None."""
       raw = text if isinstance(text, str) else ""
       m = _CONTACT_COMMAND_RE.match(raw)
       logger.debug("Calling parse_contact_command: [text=%r]", raw)
       if not m or m.group(1) not in CONTACT_CONFIG["commands"]:
           logger.debug("Response from parse_contact_command: None")
           return None
       payload = _SLACK_LINK_RE.sub(r"\1", m.group(2) or "").strip()
       logger.debug("Response from parse_contact_command: (%r, %r)", m.group(1), payload)
       return m.group(1), payload
   ```

   ⚠️ **Decision:** Only `http(s)` links are unwrapped (parent Functional scope 2). `<mailto:…>`, `<#C…>`, and `<@U…>` inside the payload stay as-is. HTML entities (`&amp;`, `&lt;`, `&gt;`) are **not** unescaped. The ACs don't ask for it, and adding it would be an unapproved heuristic.

3. **Extra context on the Estelle turn.** In `run_contact_estelle_turn`:
   - Add the keyword parameter `extra_context: Optional[str] = None` after `base_resume_artifact_id` and before `debug`.
   - Add `extra_context=%r` to the existing `Calling run_contact_estelle_turn` debug line (format string and args).
   - In step **b**, immediately **before** `lines.append("## Conversation")`, insert:

     ```python
         # AST-2035: agent-mode command result rides this turn's live content.
         if isinstance(extra_context, str) and extra_context.strip():
             lines.append("## Command result (this inbound event)")
             lines.append(extra_context.strip())
             lines.append("")
     ```

   Nothing else in the function changes. The markup follow-up turn does not carry `extra_context`.

4. **Command runner.** Directly **after** `run_contact_estelle_turn` (before `_emit_listen_info`), add:

   ```python
   def _run_contact_command(
       *,
       command_id: str,
       payload: str,
       text: str,
       channel: str,
       thread_ts: Optional[str],
       message_ts: Optional[str],
       astral_candidate_id: str,
       candidate_state: Optional[str],
       debug: bool = False,
   ) -> dict:
       """Run one registry command and reply per its mode; returns the estelle_turn dict."""
       meta = CONTACT_CONFIG["commands"][command_id]
       reply_thread_ts = thread_ts or message_ts
       summary = {"id": command_id, "mode": meta["mode"], "ok": False, "meteorite_id": None, "error": None}

       # Empty payload: usage reply only, either mode — no handler, no turn.
       if not payload:
           summary["error"] = "empty_payload"
           post = contact_post_message(
               channel=channel,
               text=format_contact_reply_text(meta["usage_reply_text"]),
               thread_ts=reply_thread_ts,
               debug=debug,
           )
           return {"ok": True, "outcome": command_id, "command": summary, "slack_post": post}

       handler = _resolve_contact_task_handler(meta["handler"])
       if handler is None:
           summary["error"] = "handler_unavailable"
           logger.warning(
               "%s | contact command %s handler %s is unavailable\n  This command is not running",
               astral_candidate_id, command_id, meta["handler"],
           )
       else:
           source_id = f"{channel}:{message_ts or ''}"
           logger.debug(
               "Calling %s: [candidate_id=%r, source_id=%r, thread_ts=%r, payload=%r]",
               meta["handler"], astral_candidate_id, source_id, reply_thread_ts, payload,
           )
           out = handler(
               astral_candidate_id, payload,
               source_id=source_id, thread_ts=reply_thread_ts, debug=debug,
           )
           logger.debug("Response from %s: %s", meta["handler"], out)
           if isinstance(out, dict):
               summary.update(ok=bool(out.get("ok")), meteorite_id=out.get("meteorite_id"), error=out.get("error"))

       # agent: one Estelle turn sees the result and replies conversationally.
       if meta["mode"] == "agent":
           turn_out = run_contact_estelle_turn(
               channel=channel,
               text=text,
               thread_ts=thread_ts,
               message_ts=message_ts,
               astral_candidate_id=astral_candidate_id,
               candidate_state=candidate_state,
               extra_context=json.dumps(summary, default=str),
               debug=debug,
           )
           turn_out["command"] = summary
           return turn_out

       # code: fixed ack only on success; a miss posts nothing so the hear-ack fallback fires.
       post = None
       if summary["ok"]:
           post = contact_post_message(
               channel=channel,
               text=format_contact_reply_text(
                   meta["ack_reply_template"].format(meteorite_id=summary["meteorite_id"])
               ),
               thread_ts=reply_thread_ts,
               debug=debug,
           )
       return {"ok": summary["ok"], "outcome": command_id, "command": summary, "slack_post": post}
   ```

   ⚠️ **Decision (source id):** `source_id = "<channel>:<message ts>"` is event-scoped, which matches AST-2034's own plan example (`"C1:1700000000.000100"`). The thread anchor is `thread_ts or message_ts`, the same thread the reply posts into, so a later BOT_BLOCKED nag lands there.

   ⚠️ **Decision (empty payload):** A bare `/add-job` posts the usage text in **both** modes, with no handler call and no turn. Parent Functional scope 5 says "an empty payload gets a fixed usage reply", with no mode exception.

   ⚠️ **Decision (handler miss in `code` mode):** If the handler soft-fails (`ok: False`) or can't be resolved, no ack is posted. `slack_post` stays `None`, so the existing AST-1101 hear-ack fallback ("Heard you — Estelle is listening.") fires. The candidate still gets a reply, and no new reply-text key is invented, because Scope lists only usage and ack texts. The failure is already logged once: `insert_slack_meteorite` warns per miss, and the unavailable-handler warning above covers that case. If Archie wants a dedicated failure text, that is a Scope amendment.

   ⚠️ **Decision (mode vocabulary):** Only `"agent"` is branched on, and everything else is `code`. The config asserts guarantee the value is one of the two. No command id or per-command mode literal appears in `src/core/` (AC8).

5. **Listen info names the command.** In `_emit_listen_info`, immediately **after** the `if isinstance(turn_out, dict):` block's `for row in …skill_results…` loop and still inside that `if`, add:

   ```python
           # AST-2035: command id:mode + meteorite id lead the action list.
           cmd = turn_out.get("command")
           if isinstance(cmd, dict):
               keys[:0] = [f"{cmd.get('id')}:{cmd.get('mode')}", f"meteorite:{cmd.get('meteorite_id') or '-'}"]
   ```

   A `code`-mode success then emits exactly one INFO line through the existing `_contact_listen_info` (stat.logging.info.contact shape):
   `<candidate_id> | contact listen app_mention add-job: action:add-job:code,meteorite:42 (channel: C1) aside: -`.
   That line names the sender (candidate), event, command id (outcome), mode, and meteorite id (AC9). In `agent` mode the outcome is the envelope outcome (`success` / `concern`) and the action starts with `add-job:agent,meteorite:42`.

6. **Intercept.** In `_handle_slack_event_body`, replace the current `else:` arm's opening (the `# AST-1561: paste recovery …` comment through `result["meteorite_apply_paste"] = paste_out`, then `if paste_out.get("applied") and …:`) so the arm starts like this. The paste-applied body, the `else:` turn body, and the trailing listen-info / hear-ack tail stay **byte-identical**:

   ```python
           else:
               # AST-2035: a bound sender's leading /<command> runs the registry handler — never paste recovery.
               command = parse_contact_command(text) if known else None
               if command is None:
                   # AST-1561: paste recovery before Estelle turn (no re-classify).
                   paste_out = try_meteorite_apply_paste_from_slack(
                       astral_candidate_id=result.get("astral_candidate_id"),
                       channel=channel,
                       thread_ts=event.get("thread_ts"),
                       message_ts=msg_ts if isinstance(msg_ts, str) else None,
                       text=text,
                       debug=debug,
                   )
                   result["meteorite_apply_paste"] = paste_out
               if command is not None:
                   try:
                       result["estelle_turn"] = _run_contact_command(
                           command_id=command[0],
                           payload=command[1],
                           text=text,
                           channel=channel,
                           thread_ts=event.get("thread_ts"),
                           message_ts=msg_ts if isinstance(msg_ts, str) else None,
                           astral_candidate_id=result["astral_candidate_id"],
                           candidate_state=result.get("candidate_state"),
                           debug=debug,
                       )
                   except Exception as exc:
                       logger.exception(
                           "%s | contact command %s\n  %s: %s\n  The inbound event is accepted; the command did not complete",
                           result.get("astral_candidate_id") or "-", command[0], type(exc).__name__, exc,
                       )
                       result["estelle_turn"] = {"ok": False, "error": str(exc)}
               elif paste_out.get("applied") and paste_out.get("result", {}).get("ok"):
                   # … existing paste-applied body, unchanged …
               else:
                   # … existing run_contact_estelle_turn body, unchanged …
               # … existing turn_out / _emit_listen_info / hear-ack tail, unchanged …
   ```

   Behavior this guarantees:
   - **Unbound sender** (`resolve_ok and not known`) never reaches this arm. The existing unknown-recognition reply posts and nothing is inserted (AC6).
   - **Resolve error** (`known` False and not `resolve_ok`): `command` is `None`, so today's paste/turn path runs unchanged.
   - **Bound, leading command:** no `try_meteorite_apply_paste_from_slack` call (AC5) and no `do_task` in `code` mode (AC3). The tail's `_emit_listen_info` fires once (`outcome` is set), and the hear-ack is skipped when the ack posted `ok`.
   - **Bound, mid-sentence `/add-job`:** `command` is `None`, so the normal turn runs (AC7).
   - The existing known-recognition post ("I know who that is") still goes out before the intercept. That's unchanged behavior, and the text has no meteorite id, so AC3's "exactly one post containing the id" still holds.

Compile and lint, then commit: `code(AST-2035): stage 2 — /command parse + intercept with code/agent reply`

## Compile and lint (each stage, before commit)

`python3 -m py_compile src/utils/config.py src/core/contact.py` and `ruff check src/utils/config.py src/core/contact.py` (`ruff` is at `~/.local/bin/ruff`; the repo has no ruff config, so defaults apply). Any finding on a line this stage added or changed must be fixed. Pre-existing findings on untouched lines are left alone and noted in the Code Complete comment.

## Test impact (for Betty — engineer does not edit `tests/`)

- No existing Contact test should break. The intercept only fires on a leading registered `/<token>`, `run_contact_estelle_turn`'s new parameter is optional, and `_emit_listen_info` adds keys only when `turn_out["command"]` exists.
- New coverage targets (ticket AC numbering):
  - AC1/AC2: an end-to-end `handle_slack_event` → real `insert_slack_meteorite` against sqlite, for both the link-markup and multi-line-text payloads.
  - AC3: `code` mode with `do_task` patched — zero calls, `outcome == command id`, one post containing the id, no hear-ack.
  - AC4: the registry entry patched to `agent`, with `run_contact_estelle_turn` called once and the id in `extra_context` → live content.
  - AC5: an existing BOT_BLOCKED row is untouched and `apply_paste` is never called.
  - AC6: unbound sender and bare command.
  - AC7: mid-sentence command.
  - AC8: an `rg` assertion.
  - AC9: `caplog` at INFO with debug off. It should show the contact listen line naming command id, mode, and meteorite id, plus the meteorite `NEW` entity line.
- Direct `parse_contact_command` cases: the bare command, `<url>` without a label, a mention with a `|label`, and a DM with no mention.

## Notes for Archie

- `patt.contact.command-intercept` is **proposed** (not in `canon/directives/`). This plan implements its parent-defined shape: a registry keyed by id, handler + mode, a first-token-after-mentions match, an intercept before paste recovery and the LLM turn, and a per-mode reply. It still needs Archie's approval as a directive.
- `agent` mode is not the shipped mode. In `agent` mode, the Estelle turn may still emit `land_calls`, whose existing AST-1531 loop can call `apply_paste` / `contact_land_meteorite`. This plan does not guard that; AC5 is scoped to the shipped `code` mode.
- Adjacent: [AST-1637](https://linear.app/astralcareermatch/issue/AST-1637) reworks `run_contact_estelle_turn`. Whichever lands second rebases the one-parameter change.

## Execution contract

Execute the stages in order, and the steps within each stage in order. Do not add files, helpers, config keys, or reply texts. If a quoted line, anchor, or signature (including `insert_slack_meteorite`'s) has drifted from what is quoted above, stop and comment on the parent [AST-2032](https://linear.app/astralcareermatch/issue/AST-2032) in the `🛑 Stage N blocked:` format. Do not adapt silently.

## Estimate

Confirm Chuckles estimate: 3 — agree


## Joan validate

[plan-rubric]
**Ticket:** AST-2035
**Overall:** APPROVED
**Corpus:** 8fa9f84d0e775852bc529f67faadf7e6f12cd904
**Publish ref:** origin/sub/AST-2032/AST-2035-contact-add-job-intercept @ a61df0f23c20194b73bf6a662462d0d428d96eab

## Canon scores
patt.contact.command-intercept | A | | Registry + first-token parse + pre-paste/pre-turn intercept + mode reply matches parent architectural definition (proposed; Notes for Archie)
stat.logging.info.contact | B | | Command id as `outcome` + id:mode in `action:` keys; aligns with AC3/AC9 and existing `paste_applied`/`unrecognized` extensions
stat.logging.debug | A | | Parse/handler Calling/Response pairs; no `if debug` gating on debug lines
stat.logging.warning | A | | Handler-unavailable warning; insert misses delegated to AST-2034 handler
stat.logging.error | A | | Intercept `logger.exception` on command throw with who/why/next step

## Traceability
AC1 → Stage 2 (`parse_contact_command` unwrap + `_run_contact_command` → `insert_slack_meteorite`). AC2 → Stage 2 (DOTALL payload strip; no `/add-job` in captured tail). AC3 → Stage 2 `_run_contact_command` `code` branch + intercept ordering. AC4 → Stage 2 `agent` branch + `extra_context` on `run_contact_estelle_turn`. AC5 → Stage 2 intercept (no `try_meteorite_apply_paste_from_slack` when `command` set). AC6 → Outer unknown-sender arm + empty-payload usage in runner. AC7 → Stage 2 parse returns `None` for mid-sentence. AC8 → Stage 1 registry only; core uses `CONTACT_CONFIG["commands"]` keys. AC9 → Stage 2 `_emit_listen_info` prefix keys + handler entity line via `_insert_stage_rows`.

## Findings
- **discuss** — `patt.contact.command-intercept` is not yet in `canon/directives/`; plan implements parent shape and flags Archie approval (frozen list item, not a plan gap).
- **discuss** — `code` mode handler soft-fail / unresolved handler: no ack, AST-1101 hear-ack may post without meteorite id — documented Decision; success-path AC3/AC9 still clear for Betty.
- **discuss** — `agent` mode + AC5: plan scopes paste skip to shipped `code` mode; Notes for Archie documents land_calls risk in agent mode.
- **acceptable** — Scope gate: only `config.py` + `contact.py`; no `meteorite.py` edits; handler via config dotted path (AC8).
- **acceptable** — Intercept control flow (`command` vs `paste_out` / turn / shared listen + hear-ack tail) matches current `_handle_slack_event_body` shape; dependency on AST-2034 entry named in Execution contract.

context_tokens≈78000

## Review

- **Branch:** `origin/sub/AST-2032/AST-2035-contact-add-job-intercept`
- **Stage 1:** `bd1e9472d` — `CONTACT_CONFIG["commands"]` registry + asserts
- **Stage 2:** `43f4767df` — `/command` parse + intercept with code/agent reply
- **Build notes:** Two files (`src/utils/config.py`, `src/core/contact.py`), as planned. `py_compile` is clean. Per the plan's lint rule, the UP045/UP006 hits on new annotations were fixed (`str | None`, `tuple[...]`; the module has `from __future__ import annotations`). The one remaining ruff hit on a new line is TRY401 on the intercept's `logger.exception`, which `stat.logging.error`'s Do shape (`type(exc).__name__, exc`) requires; the file already carries 10 of these. A smoke run with Slack, resolve, and insert patched confirmed: link unwrap → `insert_slack_meteorite("cand-1", "http://www.dice.com/jobs/13234abcd", source_id="C1:1.1", thread_ts="1.1")`, one ack containing the id, no paste recovery, no turn, no hear-ack; the bare command posts usage with no insert; mid-sentence takes the normal turn; `agent` mode runs one turn with `"meteorite_id": 42` in `extra_context`. Listen line: `cand-1 | contact listen app_mention add-job: action:add-job:code,meteorite:42 (channel: C1) aside: -`. The AC8 `rg` returns no matches. `tests/component/core/test_contact.py` shows the same 12 failures before and after the build (84 pass), so none are new.


## Radia review

[code-rubric]
**Ticket:** AST-2035
**Publish ref:** 0ea00db4817d6e7b7977224bb96b64fbd77d95f3
**Corpus:** 2344ae3265b15125a8f4a655946fcfe66b3e1def
**Review scope:** `origin/dev...origin/sub/AST-2032/AST-2035-contact-add-job-intercept` limited to AST-2035 product commits on `src/utils/config.py` and `src/core/contact.py` (`bd1e9472d`, `43f4767df`). Sibling AST-2034 carry on the same sub (`src/core/meteorite.py`, etc.) excluded from canon scoring.
**Overall:** CLEAN

## Canon scores
patt.contact.command-intercept | — | | `canon_clerk expand`: unknown id (proposed, not in corpus); plan/parent intercept shape is implemented in the scoped diff — §5.3 ESCALATE gate for Archie to approve and land the directive
stat.logging.info.contact | B | | `outcome` is command id (`add-job`) not envelope `success`/`concern`; `action:` carries `id:mode` + `meteorite:` — matches ticket AC9 and plan; slight variance from typical Estelle outcomes
stat.logging.debug | A | | Parse/handler Calling/Response pairs; no `if debug` gating on those lines
stat.logging.warning | A | | Handler-unavailable warning; insert validation misses stay in `insert_slack_meteorite`
stat.logging.error | A | | Intercept `logger.exception` with who/why/next-step (`type(exc).__name__, exc`)

## Column diff vs plan stage
patt.contact.command-intercept — Joan **A** (parent shape); Radia cannot corpus-score (unknown id) — implementation note only, not a code downgrade
(remaining ids aligned with Joan)

## Frame diff
(none)

## Findings

### fix-now
(none)

### discuss
- **Frozen proposed pattern** — `patt.contact.command-intercept` is on the frozen list but absent from the corpus (`canon_clerk expand` fails). Diff implements the planned registry + first-token parse + pre-paste/pre-turn intercept + `code`/`agent` reply. **Default:** no `resolve-child` canon work; Chuckles/Archie add or approve the directive and reconcile Canon Scope before treating this id as mechanically scoreable on future tickets.
- **`code` mode handler soft-fail** — `ok: False` or unresolved handler posts no ack; AST-1101 hear-ack may still fire (covered in `test_ac3_…` miss path). **Default:** ship as planned unless Susan amends Scope with a dedicated failure reply.
- **`agent` mode vs AC5** — paste skip is on the intercept path; `agent` turn may still hit `land_calls` / paste elsewhere (plan Notes). **Default:** AC5 coverage stays on shipped `code` mode only.

### advisory
- **Sibling carry on publish ref:** full three-dot diff also includes AST-2034 `src/core/meteorite.py`, AST-2034 plan doc, meteorite/agent/frontend tests, and bible updates — expected ftr merge; not AST-2035 product scope.
- **Plan fidelity:** Scoped diff matches Stage 1 registry/asserts and Stage 2 parse, `_run_contact_command`, `extra_context`, intercept control flow, and `_emit_listen_info` extensions. AC8 `rg` pattern has no hits under `src/core/` on tip.
- **Tests:** `tests/component/core/test_contact.py` adds `TestAst2035ContactCommandIntercept` for AC1–AC9 (parse matrix, E2E insert, code/agent modes, paste skip, unknown/bare, mid-sentence, rg, caplog AC9).
- **Status mismatch:** spawn prompt **Tests Passed**; `linear_proxy get-issue` brief shows **Tests Ready** — Chuckles should reconcile Linear before **Review Posted** (Radia did not re-fetch for gate per spawn trust).

## What's solid
- Registry-only command identity (AC8): core reads `CONTACT_CONFIG["commands"]` keys only; `add-job` lives in config.
- Intercept ordering: bound + leading command skips paste recovery, runs handler with `source_id=f"{channel}:{message_ts}"`, `code` mode avoids `do_task`, single ack with meteorite id on success.

## Recommended actions (downstream — not Radia lane)
- Chuckles: append artifact, `docs()` on publish ref, post slim upshot `--as radia`, reconcile **Tests Passed** vs **Tests Ready**, move to **Review Posted**.
- Archie: resolve **ESCALATE** by approving `patt.contact.command-intercept` in corpus or adjusting parent Canon Scope.
- datt: if ESCALATE cleared or accepted as procedural-only, **PROCEED** → **User Testing**; no product fixes indicated on scoped diff.

Gate: ESCALATE (Commit: 0ea00db48) — proposed `patt.contact.command-intercept` not in corpus; no fix-now. Linear state verified Tests Passed at review time (proxy brief was stale).

## Resolution

2026-10-08 — resolve-child (Hedy), against Radia review `0a9348e72`.

- **fix-now:** none.
- **ESCALATE / discuss — `patt.contact.command-intercept` not in corpus:** Resolved by gate [AST-2036](https://linear.app/astralcareermatch/issue/AST-2036) (Done; Susan: "Approved as is"). The directive now lives at `canon/directives/active/patt.contact.command-intercept.md`, written from the shipped code (`CONTACT_CONFIG["commands"]`, `parse_contact_command`, `_run_contact_command`, the `_handle_slack_event_body` intercept, and `_emit_listen_info`), and it has a row in the `canon/docs/CHANGELOG.md` `## Executed` table (`6f3edaa90`). `canon_clerk.py index --kind pattern` lists it, and `canon_clerk.py expand patt.contact.command-intercept` exits 0.
- **discuss — `code`-mode handler soft-fail → hear-ack:** took Radia's Default (ship as planned). The directive's `# Notes` record it.
- **discuss — `agent` mode vs AC5:** took Radia's Default (AC5 covers the shipped `code` mode only). The directive's `# Notes` record it.
- **advisory:** no action. The sibling carry is the expected ftr merge.
- **Product code:** no change in this pass.
