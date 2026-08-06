# AST-1207 — Slack Events + Contact inbound honor durable debug and Style D depth

**Linear:** [AST-1207](https://linear.app/astralcareermatch/issue/AST-1207/slack-events-contact-inbound-honor-durable-debug-and-style-d-depth)  
**Parent:** [AST-1203](https://linear.app/astralcareermatch/issue/AST-1203/need-to-be-able-to-set-the-debug-flag-for-slack-messages) — Need to be able to set the "Debug" flag for Slack messages  
**Publish ref:** `origin/sub/AST-1203/AST-1207-slack-events-contact-inbound-durable-debug`

After foundation sibling [AST-1206](https://linear.app/astralcareermatch/issue/AST-1206): Slack Events / Contact hear path uses the durable Contact debug SoT (`slack_debug_enabled()`, not `ui_llm_debug()` / local auto-debug), passes that `debug` through resolve → turn → reply and configured core callees that already accept `debug`, and fills Style D found/recorded gaps on that Contact Slack path when debug is on. Does **not** own Manage Slack React Debug toggle ([AST-1208](https://linear.app/astralcareermatch/issue/AST-1208)) or listen semantics.

**Depends on:** AST-1206 on the epic trunk (`slack_debug_enabled` / `set_slack_debug_enabled` / `CONTACT_CONFIG["debug_enabled"]` + durable `contact_slack_debug.json`). Already rolled into `origin/ftr/AST-1203-need-to-be-able-to-set-the-debug-flag-for-slack-messages` (User Testing).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_slack.py` | Pass `debug=slack_debug_enabled()` into `receive_slack_events_http`; drop `ui_llm_debug` | ui |
| `src/core/contact.py` | Events ingress hydrates `debug` from `slack_debug_enabled()`; Style D found/recorded depth on Contact Slack inbound/outbound helpers used by that path | core |
| `scripts/slack_socket_mode_dev.py` | Feed `handle_slack_event` with `debug=slack_debug_enabled()` (same SoT as HTTP Events) | scripts |

No edits to: `src/data/contact_debug.py`, admin `/debug` GET/PUT, listen paths, Manage Slack React (`AdminManageSlack.tsx`), `src/external/slack.py` (stays dumb transport), Estelle task schema / skill ACL bodies, Events verify/ack mechanics beyond debug SoT + Style D.

---

## Stage 1: Durable SoT at Events ingress

**Done when:** On staging/production (and local), Slack Events HTTP and Socket Mode use `slack_debug_enabled()` as the sole debug SoT — never `ui_llm_debug()`. That bool is what `receive_slack_events_http` / `handle_slack_event` set on the logger and pass into resolve / context / turn / post / skill callees. With durable debug off, no new debug-contract lines on this path.

1. In `src/ui/api/api_slack.py`:
   - Change imports to:

```python
from src.core.contact import receive_slack_events_http, slack_debug_enabled
from src.utils.config import CONTACT_CONFIG
```

   - Remove `from src.utils.deploy_status import ui_llm_debug`.
   - In `slack_events()`, pass `debug=slack_debug_enabled()` (not `ui_llm_debug()`).

2. In `src/core/contact.py`, update the module docstring to note AST-1207: Events/Socket ingress hydrates debug from Manage Slack durable SoT.

3. At the **first executable line** of both `receive_slack_events_http` and `handle_slack_event` (before `log.set_debug_flag`), rebind:

```python
    # AST-1207: Manage Slack Debug is sole SoT for Contact Slack Events (Archie).
    # Caller kwarg kept for signature compat; durable file wins every call.
    debug = slack_debug_enabled()
```

   Then keep all existing `log.set_debug_flag(debug)` and `debug=` pass-throughs unchanged.

4. In `scripts/slack_socket_mode_dev.py`:
   - Import `slack_debug_enabled` beside `handle_slack_event`.
   - Replace `handle_slack_event(payload, debug=True)` with `handle_slack_event(payload, debug=slack_debug_enabled())`.

⚠️ **Decision — core overwrites caller `debug`:** Archie: Manage Slack Debug is sole SoT for Contact Slack Events (not local `ui_llm_debug`). Re-read every Events entry (same posture as listen AST-1101) so Admin toggles apply mid-process without restart. UI still passes `slack_debug_enabled()` for honesty; core re-bind is defense in depth. Betty tests that need Style D on this path must set durable debug on (or mock `slack_debug_enabled`), not rely on a bare `debug=True` kwarg.

⚠️ **Decision — do not OR with `ui_llm_debug`:** Local auto-debug must not reopen a second SoT on Events. Operators turn Debug on via Manage Slack (API today; React in AST-1208).

**Done when (recheck):** With no durable file / debug off, `POST /api/slack/events` (after signature) does not emit Style D from Contact. After `set_slack_debug_enabled(True)` (or PUT `/api/admin/contact/debug`), the same accepted inbound path emits Style D. `api_slack.py` has zero references to `ui_llm_debug`.

---

## Stage 2: Style D found/recorded gaps on Contact Slack path helpers

**Done when:** Helpers on the hear → resolve → turn → reply path that already accept `debug` but emit only a single summary index (or weaker than agent Ad Hoc found→recorded) emit Style D **found** then **recorded** when `debug=True`, and stay silent when `debug=False`. Long text uses `truncate_debug_content` / `_TEXT_DEBUG_MAX` as today — no full ungated blobs.

Audit (current → required). Edit **only** these functions in `src/core/contact.py`:

1. **`contact_post_message`** (Estelle reply + hear-ack use this; today: one index `ok`/`api_error`):
   - When `debug`: emit `index=1/2` `outcome="found"` with `|` detail for `channel=`, `thread_ts=`, and truncated `text=` lines (`truncate_debug_content`).
   - After `post_message` (+ optional cache append), emit `index=2/2` `outcome="recorded"` with `|` detail `ok=… error=…` (and `ts=` when present). Keep `func="contact.contact_post_message"`, `identifier=channel` (truncated to 80 if needed).
   - Do **not** switch Estelle/hear-ack to `post_contact_reply` (would double-apply `format_contact_reply_text`).

2. **`load_slack_conversation_context`** (today: one index with outcome `cache`/`slack`):
   - When `debug`: `index=1/2` `outcome="found"` — detail `channel=`, `thread_ts=`, `refresh=`.
   - Then `index=2/2` `outcome="recorded"` — detail `source=cache|slack`, `len(messages)=…`. Same `func` / identifier shape as today (`{channel}:{thread or '-'}`).

3. **`append_slack_conversation_message`** (today: one `appended` index):
   - When `debug`: `index=1/2` `outcome="found"` — detail truncated inbound `ts=` / `text=`.
   - Then `index=2/2` `outcome="recorded"` — detail `len(messages)=…` after append/trim. Same `func` / identifier as today.

4. **`run_contact_estelle_turn`** (today: one end-of-turn summary index):
   - Replace the single end index with a **found → recorded** pair (`total=2`) under `func="contact.run_contact_estelle_turn"`:
     - `index=1` `outcome="found"`: detail `channel=`, `thread_ts=`, `astral_candidate_id=`, `candidate_state=`, truncated inbound `text=` (use `_TEXT_DEBUG_MAX` or `truncate_debug_content`).
     - `index=2` `outcome="recorded"`: keep the existing length/count summary line (`outcome=`, `success=`, `reply_len=`, `admin_aside_len=`, `skill_calls=`, `skill_ok=`, `slack_ok=`). Identifier remains candidate id or channel as today.
   - Do **not** duplicate Style D already emitted by `do_task` / `run_contact_skill` / `load_slack_conversation_context` / `contact_post_message` — only this turn bookend.

5. **`handle_slack_event` accepted path bookend** (today: many early-reject single indices + one final `outcome="accepted"`):
   - Keep early-reject Style D blocks as-is (listen_off, duplicate, type_skipped, …) — they already gate on `debug`.
   - Replace the final accepted summary (`outcome="accepted"` only) with found→recorded when the event was accepted and processing finished:
     - `index=1/2` `outcome="found"`: detail `event_type=`, `user=`, `channel=`, truncated `text=`.
     - `index=2/2` `outcome="recorded"`: detail `astral_candidate_id=`, `candidate_state=`, `candidate_created=`, `estelle_turn_ok=` (from `result["estelle_turn"].get("ok")` when dict), `hear_ack=` (True/False/None from whether `hear_ack_post` exists / ok). `identifier=event_id`, `func="contact.handle_slack_event"`.
   - Leave mid-path activity_recorded / hear_ack_posted Style D blocks in place (already gated).

6. **Do not change** (already adequate found/recorded or sibling-owned):
   - `resolve_slack_user` outcomes (`found|matched` / `found|none` / `recorded|created`) — already Style D when `debug` is passed.
   - `run_contact_skill` found→recorded.
   - `post_contact_reply` found→recorded (unused by Estelle turn path; leave alone).
   - `receive_slack_events_http` status indices (signature/challenge/ack) — keep single-index status lines; not found/recorded I/O.
   - `set_slack_debug_enabled` / admin API / data layer — AST-1206.

⚠️ **Decision — fill gaps only on Contact Slack path, not a Contact-wide logging rewrite:** Parent boundary: better logging for this epic stays on the Contact Slack path gated by this flag. No gazer/consult/agent Ad Hoc changes; no redesign of Estelle conversational quality.

⚠️ **Decision — no Betty Style D golden string tests in this ticket:** Parent / AST-1206 precedent: Radia enforces instrumentation on review; do not invent log-string golden tests here.

**Done when (recheck):** With durable debug on and listen on, an accepted DM/`app_mention` produces scannable DEBUG rows in `app_log` with Style D headers + `|` detail covering ingress bookends, context load/append, resolve (existing), turn bookend, and post_message found/recorded. With durable debug off, those debug-contract lines are absent; normal INFO/WARNING/ERROR (e.g. resolve failures, concern aside) still appear.

---

## Self-Assessment

**Scope:** `Single-Component` — Events UI thin wire + Contact core debug hydration and Style D depth on the existing Slack inbound/outbound helpers; no React, no new config keys, no data-layer edits.

**Conf:** `high` — AST-1206 SoT is already on the trunk; path already threads `debug=` end-to-end; this ticket swaps the SoT and upgrades known summary-only Style D sites to found→recorded.

**Risk:** `Medium` — wrong SoT would leave staging Events quiet (or locally always-wordy again); wrong Style D changes could spam `app_log` when Debug is on, but off-path remains gated and listen/Estelle behavior is otherwise untouched.

---

## Code-rules self-review

| Rule | Status |
|------|--------|
| §1.3 DRY / public-then-helpers | Reuse `slack_debug_enabled`; Style D edits stay inside existing public helpers — no new modules. |
| §2.1 config SoT | No new config keys; durable filename/default remain AST-1206. |
| §2.4 batch processing | N/A — no batch claim/dispatch. |
| §2.6 state machine | N/A — no entity state transitions. |
| §3.3 imports | ui→core only (`slack_debug_enabled`); core already owns data/external; UI never imports data/external. |
| §3.5 naming | Keep `debug_enabled` / `slack_debug_enabled` names from foundation. |
| §1.5.1 debug-contract-gated | Style D only when hydrated `debug` is True; no new `logger.info("[DEBUG] …")`; external stays silent. |
| §1.1 in-scope-only | Explicit non-touch: React Manage Slack, listen file/semantics, Events verify redesign, non-Contact modules. |
