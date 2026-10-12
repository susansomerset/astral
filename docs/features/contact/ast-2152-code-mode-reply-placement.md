# AST-2152 — Code-mode handler reply + per-command placement

**Linear:** [AST-2152](https://linear.app/astralcareermatch/issue/AST-2152)
**Parent:** [AST-2144](https://linear.app/astralcareermatch/issue/AST-2144) — Add /check-status to Estelle's functions
**Publish ref:** `origin/sub/AST-2144/AST-2152-code-mode-reply-placement`

This ticket is the Contact posting half of `@Estelle /check-status <search string>`. Sibling [AST-2151](https://linear.app/astralcareermatch/issue/AST-2151) (merged into `origin/ftr/AST-2144-check-status`) added the `check-status` registry entry with `reply_placement: "always_with_share"` and no `ack_reply_template`, and a handler that returns `{ok, meteorite_id, error, reply_text}`. Today's `_run_contact_command` ignores both: it places every reply by the global `thread_response`, and on an `ok` result it indexes `meta["ack_reply_template"]`, which raises `KeyError` for `check-status`. This ticket changes two functions in `src/core/contact.py`. `_contact_reply_placement` takes an optional placement mode that overrides `CONTACT_CONFIG["thread_response"]`. `_run_contact_command` passes the entry's `reply_placement` to it (usage reply and every `code`-mode post), and in `code` mode posts the handler's `reply_text` on a hit or a miss, falling back to today's ack-on-`ok` / nothing-on-miss when the handler returns no text. `/add-job` declares no placement and returns no text, so it is unchanged. Ships parent AC 3, AC 5–6, AC 11–15, and the end-to-end posting of AC 4 and AC 7–10.

## Scope gate

The ticket's `## Scope` names one file, `src/core/contact.py`, and two functions in it:

- `_contact_reply_placement` — "accepts an optional placement mode that overrides `CONTACT_CONFIG["thread_response"]` for that call, and stays the single placement rule." Stage 1.
- `_run_contact_command` — "resolves placement with the entry's override … for the usage reply and every `code`-mode post", posts handler reply text on hit or miss, keeps ack / nothing when there is none. Stage 2.

No other function, file, or config changes. `src/utils/config.py` and `src/core/tracker.py` are AST-2151's and are read-only here.

Already true on the tip, no change needed (verified on `8ad567ef2`):

- **AC 3:** `parse_contact_command` matches registry keys, so `"<@UBOT> /check-status Senior Engineer"` → `("check-status", "Senior Engineer")` and the `<https://x.com/j/1|x.com/j/1>` form → `("check-status", "https://x.com/j/1")`.
- **AC 6:** the intercept in `_handle_slack_event_body` runs `_run_contact_command` **instead of** paste recovery and the Estelle turn, and the handler is read-only (AST-2151).
- **AC 13:** `_emit_listen_info` already leads `action:` with `<command id>:<mode>` and is called once per event.
- **AC 14 baseline:** `rg -n "check-status|jobs/detail|RAILWAY_PUBLIC_DOMAIN|always_with_share" src/core` returns only `contact.py:258` (comment) and `contact.py:259` (code), both inside `_contact_reply_placement`. This plan adds no line matching that pattern.

**Contract consumed from AST-2151** (spelling fixed there): the registry field is **`reply_placement`** (values `threads_only` / `always_no_share` / `always_with_share`, import-asserted), and the handler result key is **`reply_text`** (`str`, or `None` when there is nothing to post).

**Existing test constraint (AC 15 / AST-2072):** `TestAst2072ThreadResponsePlacement::test_ac9_placement_logic_only_in_helper_and_anchors` fails if any line in `contact.py` outside the existing three owners contains `thread_ts or message_ts`, `thread_ts or msg_ts`, or `reply_thread_ts = event.get`, and it fails if `_run_contact_command` gains a second such line. No step below writes any of those strings. `test_contact.py:2769` calls `_contact_reply_placement(thread_ts, "5.0")` with two positional args, so the new parameter must default to `None`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/contact.py` | `_contact_reply_placement`: new optional third param `mode`, docstring line, one changed line. `_run_contact_command`: pass `meta.get("reply_placement")` to the placement call; capture the handler's `reply_text`; replace the `code`-mode tail with reply-text-first posting. | core |

No other file is touched. `tests/` and `docs/test-bible/**` are Betty's.

## Stage 1: `_contact_reply_placement` optional override

**Done when:** `_contact_reply_placement("T", "M")` returns the same tuple as before for every `thread_response` value, and `_contact_reply_placement(None, "M", "always_with_share")` returns `("M", True)` while `CONTACT_CONFIG["thread_response"] == "threads_only"`. `pytest tests/component/core/test_contact.py -q` passes unmodified.

1. In `src/core/contact.py`, replace the whole `_contact_reply_placement` function (from `def _contact_reply_placement(` through its final `return (thread_ts or message_ts or None, mode == "always_with_share")`) with:

   ```python
   def _contact_reply_placement(
       thread_ts: Optional[str], message_ts: Optional[str], mode: Optional[str] = None
   ) -> Tuple[Optional[str], bool]:
       """Resolve ``(reply thread_ts, reply_broadcast)`` for a reply to one inbound Slack message.

       Driven by ``CONTACT_CONFIG["thread_response"]`` (AST-2072); ``None`` thread_ts = top-level post.
       ``mode`` (same vocabulary) overrides it for this call — a command entry's ``reply_placement`` (AST-2144).
       The single placement rule for every Contact reply site — no per-site ``thread_ts or …`` copies.
       """
       # Read per call (not at import) so a config change applies without a restart path.
       mode = mode or CONTACT_CONFIG["thread_response"]
       if mode == "threads_only":
           # Thread only when the user was already in one; a top-level message gets a top-level reply.
           return (thread_ts or None, False)
       # always_no_share / always_with_share: the user's thread, or a new thread under their message.
       return (thread_ts or message_ts or None, mode == "always_with_share")
   ```

   The only code differences from today are the new `mode` parameter, the added docstring line, and `mode = mode or CONTACT_CONFIG["thread_response"]` in place of `mode = CONTACT_CONFIG["thread_response"]`. Lines 258–259 (the AC 14 baseline) are byte-identical.

   ⚠️ **Decision:** No vocabulary check on `mode` here. AST-2151's import-time assert already rejects any `reply_placement` outside the `thread_response` vocabulary, and an unknown value would fall through to the "thread under their message, no share" branch exactly as an unknown `thread_response` does today.

2. Compile and lint: `python3 -m py_compile src/core/contact.py && ruff check src/core/contact.py`. Record the ruff count before and after; the change must add no new hits. Run the Done-when check with `~/astral/.venv/bin/python` (system python lacks `asyncpg`) and `~/astral/.venv/bin/python -m pytest tests/component/core/test_contact.py -q`. Commit `code(AST-2152): stage 1 — _contact_reply_placement optional override`, then publish per build-child.

## Stage 2: `_run_contact_command` — per-command placement and handler reply text

**Done when:** with `thread_response == "threads_only"`, a stubbed `post_message`, and `RAILWAY_PUBLIC_DOMAIN=astral.example`, `handle_slack_event` on a bound top-level `app_mention` `/check-status <owned title substring>` makes exactly one `post_message` call, carrying the handler's `reply_text`, `thread_ts` = the inbound `ts`, and `reply_broadcast=True`. A nonsense pattern makes exactly one call with `no_match_reply_text` and the same placement, and no hear-ack. A bare `/check-status` posts `usage_reply_text` with the same placement and never calls the handler. `/add-job <link>` top-level still posts its ack with no `thread_ts` and no `reply_broadcast`. `pytest tests/component/core/test_contact.py -q` passes unmodified (AC 15), and the AC 14 `rg` returns only lines 258–259.

1. In `src/core/contact.py`, in `_run_contact_command`, replace the line

   ```python
       reply_ts, reply_broadcast = _contact_reply_placement(thread_ts, message_ts)
   ```

   with:

   ```python
       # Every reply this command posts (usage, handler reply, ack) uses the entry's reply_placement
       # when declared, else thread_response (AST-2144); the hear-ack fallback keeps thread_response.
       reply_ts, reply_broadcast = _contact_reply_placement(
           thread_ts, message_ts, meta.get("reply_placement")
       )
   ```

   The usage reply (`if not payload:` block) already uses `reply_ts` / `reply_broadcast`, so it picks up the override with no further edit (AC 11).

2. In the same function, replace the line

   ```python
       summary = {"id": command_id, "mode": meta["mode"], "ok": False, "meteorite_id": None, "error": None}
   ```

   with:

   ```python
       summary = {"id": command_id, "mode": meta["mode"], "ok": False, "meteorite_id": None, "error": None}
       # Handler-composed reply (AST-2144); code mode posts it on a hit or a miss. Agent mode ignores it.
       reply_text = None
   ```

3. In the same function, replace the line

   ```python
               summary.update(ok=bool(out.get("ok")), meteorite_id=out.get("meteorite_id"), error=out.get("error"))
   ```

   with:

   ```python
               summary.update(ok=bool(out.get("ok")), meteorite_id=out.get("meteorite_id"), error=out.get("error"))
               reply_text = out.get("reply_text")
   ```

4. In the same function, replace the whole `code`-mode tail — from the comment `# code: fixed ack only on success; a miss posts nothing so the hear-ack fallback fires.` through the closing `)` of its `contact_post_message(...)` call (the line before `return {"ok": summary["ok"], …}`) — with:

   ```python
       # code: the handler's reply_text posts on a hit or a miss (AST-2144). Without one, the fixed
       # ack posts only on success; a miss (or an entry with no ack) posts nothing → hear-ack fallback.
       if not (isinstance(reply_text, str) and reply_text.strip()):
           reply_text = (
               meta["ack_reply_template"].format(meteorite_id=summary["meteorite_id"])
               if summary["ok"] and "ack_reply_template" in meta
               else None
           )
       post = None
       if reply_text:
           post = contact_post_message(
               channel=channel,
               text=format_contact_reply_text(reply_text),
               thread_ts=reply_ts,
               reply_broadcast=reply_broadcast,
               debug=debug,
           )
   ```

   The following `return {"ok": summary["ok"], "outcome": command_id, "command": summary, "slack_post": post}` line is unchanged.

   ⚠️ **Decision:** Handler `reply_text` wins over `ack_reply_template` when both exist. The ticket says the handler's text is posted "whether the result is `ok` or not", and the ack applies "when it returns none". An entry with both is not shipped today; this precedence makes the handler the more specific voice.

   ⚠️ **Decision:** Empty or whitespace-only `reply_text`, or a non-`str` value, counts as "none" (falls back to ack / nothing). Posting a blank Slack message is never the intended reply, and treating it as "none" lets the hear-ack fire.

   ⚠️ **Decision:** An `ok` result with no `reply_text` on an entry with no `ack_reply_template` posts nothing, so the hear-ack fires. AST-2151 made the ack optional; this is the no-`KeyError` reading of "today's behavior holds". No shipped entry hits this case (`add-job` has an ack; `check-status` always returns text when `ok`).

   ⚠️ **Decision:** The hear-ack fallback in `_handle_slack_event_body` (handler raised, handler unavailable, or nothing posted) keeps the global `thread_response` placement. It is outside `_run_contact_command`, the ticket scopes the override to "the usage reply and every `code`-mode post", and on `check-status` the handler always returns text, so the hear-ack only fires on a fault.

   ⚠️ **Decision:** `agent` mode is unchanged: `reply_text` is captured but never read on that branch, and `summary` (the `extra_context` JSON) gains no new key. `anchor_ts` (the handler's `thread_ts=`) is unchanged.

   No new log lines. `contact_post_message` already emits the Calling/Response debug pair, the handler call already has its pair, a raising handler is already logged once by the intercept's `logger.exception` (`stat.logging.error`), and the listen line is unchanged (`stat.logging.info.contact`).

5. Compile and lint: `python3 -m py_compile src/core/contact.py && ruff check src/core/contact.py` (no new hits versus the Stage 1 count). Run `rg -n "check-status|jobs/detail|RAILWAY_PUBLIC_DOMAIN|always_with_share" src/core` (only lines 258–259 of `contact.py`) and `rg -n "thread_ts or message_ts|thread_ts or msg_ts" src/core/contact.py` (same lines as before this ticket). Run the Done-when smoke with `~/astral/.venv/bin/python` (stub `post_message`, the candidate resolver, and the handler's matcher/ownership/timezone the way AST-2151's tests do; no live Slack). Run `~/astral/.venv/bin/python -m pytest tests/component/core/test_contact.py tests/component/core/test_tracker.py -k "Ast2035 or Ast2072 or Ast2151" -q`. Commit `code(AST-2152): stage 2 — code-mode handler reply + per-command placement`, then publish per build-child.

## Test impact (for Betty)

- **AC 4, 5, 7–11 end-to-end:** `handle_slack_event` on a bound `app_mention` with `post_message` patched; assert one post, its `text`, `thread_ts` (inbound `ts` top-level, `T` in-thread), and `reply_broadcast=True` under `threads_only`. AC 9 also asserts no post carries `hear_ack_reply_text`. AC 11 asserts the handler mock is never called.
- **AC 12:** top-level `@Estelle hi` and `/add-job <link>` under `threads_only` → no `thread_ts`, `reply_broadcast=False`.
- **AC 13:** `caplog` INFO, one `contact listen` line containing `check-status:code`.
- **AC 14:** the `rg` one-liner above.
- **AC 15:** `TestAst2035ContactCommandIntercept` and the AST-2072 placement tests (including `test_ac9_placement_logic_only_in_helper_and_anchors` and the 2-arg `_contact_reply_placement` matrix) pass unmodified.
- **Unit:** `_contact_reply_placement(None, "M", "always_with_share") == ("M", True)` regardless of `thread_response`; `mode=None` matches today's matrix.

## Estimate

Confirm Chuckles estimate: 2 — agree


## Joan validate

[plan-rubric]
**Ticket:** AST-2152
**Overall:** APPROVED
**Corpus:** 0d01e20d2b313a4e35cf3d07434b6cd69f615768
**Publish ref:** `origin/sub/AST-2144/AST-2152-code-mode-reply-placement` @ `c54da3712`

## Canon scores

patt.contact.command-intercept | B | | Single placement helper + `_run_contact_command` posts `reply_text` on hit/miss, optional `ack_reply_template`, `reply_placement` on usage and code posts; hear-ack stays global `thread_response` — implements parent pattern change request on Contact runner side
stat.logging.info.contact | A | | Plan leaves `_emit_listen_info` / listen line unchanged; `command id:mode` still leads `action:`
stat.logging.error | A | | Intercept `logger.exception` on command failure unchanged; plan adds no new catch paths

## Traceability

AC3 → Scope gate (registry parse, no code); AC4 → Stage 2 Done-when + Betty E2E; AC5 → Stage 1 override + Stage 2 placement on post; AC6 → Scope gate (intercept ordering); AC7 → Stage 2 + Betty; AC8 → Stage 2 + Betty (handler from #1); AC9 → Stage 2 reply-text on miss + `slack_post` hear-ack gate; AC10 → Stage 2 + Betty (#1 warning); AC11 → Stage 1 usage path uses same `reply_ts`/`reply_broadcast`; AC12 → Stage 2 Done-when `/add-job`; AC13 → Scope gate + Betty caplog; AC14 → Scope gate + Stage 2 `rg`; AC15 → Stage 1–2 pytest unmodified `test_contact.py`.

### discuss — AST-2151 merge prerequisite

- **Location:** Plan header (ftr merge); Boundaries; Stage 2 pytest `-k Ast2151`.
- **Finding:** This plan assumes registry `reply_placement`, optional ack, and `contact_command_check_status` / `reply_text` from sibling #1.
- **Recommendation:** Build/merge order per epic (#1 before #2 on integration ref); not a plan defect.

### discuss — In-force pattern vs epic widening

- **Location:** Parent Architectural definition; Stage 2 code-mode tail.
- **Finding:** Corpus `patt.contact.command-intercept` still describes ack-only code replies and miss → no post; this plan is the Contact half of the widened contract.
- **Recommendation:** Proceed; Archie pattern amendment remains epic-level (paired with #1).

### discuss — Hear-ack placement vs command override

- **Location:** Stage 2 decision bullet on hear-ack in `_handle_slack_event_body`.
- **Finding:** Fault-path hear-ack keeps event-level `_contact_reply_placement` without `reply_placement` override.
- **Recommendation:** Accept per plan (#1 handler normally always returns text); note if Susan wants command placement on fault acks later.

### acceptable — No formal `## Self-assessment`

- **Location:** Plan ends at Estimate confirm.
- **Finding:** AST-2072 `test_ac9` constraints and byte-identical AC 14 lines are explicitly addressed.
- **Recommendation:** Optional; not blocking.

### acceptable — Betty-owned E2E coverage

- **Location:** Test impact vs Stage Done-when “pytest unmodified”.
- **Finding:** Done-when guards existing suite; new AC 4–13 assertions land in Betty’s pass, as expected for this child.
- **Recommendation:** None for plan approval.

**R6 (summary):** One file, two functions, no config/tracker edits. Placement override is centralized; no new `thread_ts or …` copies. `/add-job` and `agent` paths preserved. No scope creep. No `fix-now` findings.

context_tokens≈58000

[plan-rubric] PROCEED (Commit: c54da3712) Contact reply and placement plan


## Review

- **Branch:** `origin/sub/AST-2144/AST-2152-code-mode-reply-placement`
- **Stage 1:** `023eaee3f` — `_contact_reply_placement` optional `mode` override
- **Stage 2:** `a32a49ca8` — `_run_contact_command` per-command placement + handler `reply_text` posting
- **Build notes:** One file (`src/core/contact.py`), code as written in the plan. `py_compile` is clean. Ruff went 85 → 86: the one new hit is UP045 on the new `mode: Optional[str]` param, matching the two `Optional[str]` params on the same line; no F-class hits. The AC 14 `rg` over `src/core` returns only the two existing lines in `_contact_reply_placement` (now 259–260, shifted by the added docstring line). No new `thread_ts or message_ts` copies. `TestAst2035…`, `TestAst2072…`, `TestAst2151…`: 64 passed (run with `~/astral/.venv/bin/python`). Full `test_contact.py` has 7 failures (`TestAst1073…`, `TestAst1101…::test_background_wrapper_logs_exception`, `TestAst1207…` ×3, `TestAst1515…::test_dispatch_debug_style_d`), identical with and without this ticket's change, so they predate it. Running `test_contact.py` rewrites the tracked `data/contact_estelle_activity.json`; restored to HEAD after each run.
- **Smoke** (`handle_slack_event`, `thread_response=threads_only`, `contact_post_message` / matcher / ownership / timezone stubbed, `channel_type` set so no Slack call):
  - Hit: one post, handler text with `https://astral.example/jobs/detail/acme%3Aj%201`, `thread_ts=` inbound ts, `reply_broadcast=True`. In thread `50.5`: `thread_ts=50.5`.
  - Miss: one post, `no_match_reply_text`, same placement, no hear-ack.
  - Bare `/check-status`: one post, `usage_reply_text`, same placement.
  - Origin unset: same text without the link, one WARNING.
  - Non-command `@Estelle hi` (turn stubbed to no post): hear-ack top-level, `reply_broadcast=False`.
