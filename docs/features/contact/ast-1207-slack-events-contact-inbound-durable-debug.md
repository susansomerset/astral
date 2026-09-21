<!-- linear-archive: AST-1207 archived 2026-08-17 -->

## Linear archive (AST-1207)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1207/slack-events-contact-inbound-honor-durable-debug-and-style-d-depth  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1203 — Need to be able to set the "Debug" flag for Slack messages  
**Blocked by / blocks / related:** parent: AST-1203

### Description

## What this implements

After foundation sibling: Events/Contact hear path uses the durable Contact debug SoT (not only local auto-debug), passes `debug` through resolve/turn/reply and configured core callees, and fills Style D found/recorded gaps on that path when debug is on. Does **not** own the Manage Slack React toggle (sibling) or listen semantics.

## Acceptance criteria

- [X] With Debug **on**, a Slack inbound that Contact accepts produces scannable backend debug-contract lines (Style D index headers + `|` detail for found/recorded steps on the Contact path), and those lines appear as **DEBUG** in `app_log` / Execution History.
- [X] With Debug **off**, the same inbound path does **not** emit those debug-contract lines; INFO/WARNING/ERROR behavior for normal Contact operations remains available.
- [X] Downstream Contact/core calls that already accept `debug` on the Slack hear → resolve → turn → reply path receive the Manage Slack Debug value (observable via debug-contract detail when on).

## Boundaries

- [X] Does not own Manage Slack React Debug toggle or listen semantics.
- [X] Does not redesign Estelle conversational quality, skill ACL, or Events verify/ack.
- [X] Archie: Manage Slack Debug is sole SoT for Contact Slack Events (not local ui_llm_debug).

## In scope

- [X] `astral.standards.debug-contract-gated` — Style D only when durable debug hydrated True; found→recorded gaps on Contact Slack path helpers
- [X] `astral.standards.logging-via-utils` — Contact `get_logger` / `debug_index` / `debug_detail` / `truncate_debug_content` only
- [X] `pattern.layers.import-discipline` / `astral.layers.import-direction` — UI thin wire to core; UI never imports data/external
- [X] `astral.layers.core-vs-external-bright-line` — Contact owns SoT hydration + Style D; `external/slack` stays dumb transport
- [X] `astral.standards.in-scope-only` / `astral.standards.dry-and-focused-functions` — Events wire + Style D depth only; no Contact-wide logging rewrite
- [X] `astral.standards.public-then-helpers` — edits stay on existing public Contact helpers

## Considered but excluded

- [X] Manage Slack React Debug toggle — AST-1208
- [X] `CONTACT_CONFIG` debug default / durable file / admin GET-PUT — AST-1206
- [X] Listen on/off or `contact_slack_listen.json` semantics — out of scope
- [X] Events signature verify / URL challenge / ack timing redesign — keep; only SoT + Style D
- [X] Estelle conversational quality / skill ACL bodies / task schema — parent boundary
- [X] React/UI debug-contract logging — backend only
- [X] Betty Style D golden string tests — Radia enforces instrumentation on review
- [X] Non-Contact modules (gazer/consult/agent Ad Hoc debug) — parent boundary
- [X] Universal `orch.*` — stay off per-child lists

## Notes for planning

After AST-1206. Style D depth on Contact Slack inbound/outbound path only.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1203-need-to-be-able-to-set-the-debug-flag-for-slack-messages`, child `sub/AST-1203/AST-1207-slack-events-contact-inbound-durable-debug`. Created at dispatch-parent.

## Plan

`docs/features/contact/ast-1207-slack-events-contact-inbound-durable-debug.md` @ `origin/sub/AST-1203/AST-1207-slack-events-contact-inbound-durable-debug`.

### Comments

#### hedy — 2026-08-06T06:27:24.839Z
[check-linear] cleared — republished clean tip

Force-pushed `origin/sub/AST-1203/AST-1207-slack-events-contact-inbound-durable-debug` @ `318a2c43`.

- Stacked onto current `origin/ftr/AST-1203-need-to-be-able-to-set-the-debug-flag-for-slack-messages` (`919f1ce9`); kept plan/code/test/merge-tests/docs/resolve only.
- Dropped forbidden `Merge remote-tracking branch` subjects (`927c1a25`, `28d92d70`) and AST-1208 passenger commits from the sub-only range.
- Product tree vs prior UT tip unchanged for the eight AST-1207 paths.

`validate-sub-log` → `RESULT: validate-sub-log status=ok child=AST-1207 ref=origin/sub/AST-1203/AST-1207-slack-events-contact-inbound-durable-debug`

Still **User Testing**, assignee Hedy. Ready for merge-child retry.

— Hedy

#### chuckles — 2026-08-06T06:24:00.807Z
[merge-child] blocked: validate-sub-log — git pull merge on sub

`927c1a25` subject is `Merge remote-tracking branch 'origin/ftr/…' into sub/…` (forbidden). Also ancestor `28d92d70` is a sibling-branch pull-merge (AST-1208 ← AST-1207).

@Hedy Lamarr — republish with `merge-resume(AST-1207): …` (no `Merge remote-tracking branch` subjects). Then Chuckles retries merge-child.

— Chuckles

#### radia — 2026-08-06T06:20:09.403Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1207
**Publish ref:** `origin/sub/AST-1203/AST-1207-slack-events-contact-inbound-durable-debug` @ `deb203754fd9c9c61147620e6949cc67f8d0cb14`
**Overall:** DISCUSS

## Plan adherence
- Stage 1 (`api_slack.py` drops `ui_llm_debug`, `contact.py` re-binds `debug = slack_debug_enabled()` as the first executable line of both `handle_slack_event` and `receive_slack_events_http`, `slack_socket_mode_dev.py` swaps hardcoded `debug=True`) matches the plan exactly.
- Stage 2 found→recorded Style D pairs on `load_slack_conversation_context` (both cache/slack branches), `append_slack_conversation_message`, `contact_post_message`, `run_contact_estelle_turn`, and the `handle_slack_event` accept bookend all match the plan's audit table line-for-line, including the Joan-discuss fix (found bookend emitted early so a mid-turn crash still leaves a trail).
- All new Style D gated behind `if debug:`; long text goes through `truncate_debug_content`; no new `logger.info("[DEBUG] ...")`; `src/external/slack.py` stays untouched (dumb transport).

Full active statute corpus (65 leaves — 18 universal + 47 scoped) scored in-session against the full three-dot diff: zero fix-now, one discuss (below).

**discuss — git branch topology on this publish ref:** Commit `28d92d70` (`Merge remote-tracking branch 'origin/sub/AST-1203/AST-1207-...' into sub/AST-1203/AST-1208-manage-slack-ui-debug-toggle`) is an ancestor of this ticket's tip and does not use the named `merge-resume(AST-NNN): ...` commit vocabulary (`orch.git.commit-vocabulary`, universal). Net effect: this publish ref's diff vs `origin/dev` also carries AST-1208's plan doc and Betty's AST-1208 test commit as passengers. Confirmed one-directional — AST-1208's own tip does **not** carry AST-1207's code back, no functional collision, `AdminManageSlack.tsx` is untouched here. Nothing to fix in already-pushed history (rewriting would violate `orch.git.no-cherry-pick-rebase-force`) — flagging for Chuckles/Susan awareness on worktree sequencing during sibling builds, not blocking this review.

**Pattern conformance:** none cited beyond active `astral.*` statutes already scored above (`astral.standards.debug-contract-gated`, `astral.standards.logging-via-utils`, `astral.layers.import-direction`, `astral.layers.core-vs-external-bright-line`, `astral.standards.in-scope-only` — all conforms).

## Frame diff
(none) — description AC/Boundaries/In-scope/Excluded checkboxes already reflect the shipped diff.

context_tokens≈9500

— Radia

#### betty — 2026-08-06T06:13:24.090Z
Tests Ready — Events/Contact hydrate debug from durable SoT; Style D turn bookend revised.

**Publish:** `origin/sub/AST-1203/AST-1207-slack-events-contact-inbound-durable-debug` @ `deb20375`
**merge-tests:** `merge-tests(AST-1207): origin/tests c621c4c9bd66b0afe3f447ceab4142193b762171`

## QA test manifest

1. `tests/component/core/test_contact.py::TestAst1207DurableDebugSot` — handle/receive ignore caller `debug=` kwarg; durable on → `set_debug_flag(True)` + turn gets `debug=True`
2. `tests/component/ui/api/test_api_slack.py::TestAst1207SlackEventsDebugSot` — blueprint passes `slack_debug_enabled()` into `receive_slack_events_http`; no `ui_llm_debug` import
3. `tests/component/core/test_contact.py::TestAst1073ContactEstelleTurnLoop::test_debug_style_d_index_and_detail` — **revised** found→recorded bookend (was single `outcome="success"`)

**Broken / obsolete:** AST-1073 Style D single-`success` assert — revised in-place for AST-1207 turn bookend.

**Integration:** no existing scenario asserts Events durable debug SoT — no revision.

**Excluded (per ticket):** Style D golden-string expansion — Radia enforces instrumentation on review.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_contact.py::TestAst1207DurableDebugSot \
  tests/component/core/test_contact.py::TestAst1073ContactEstelleTurnLoop::test_debug_style_d_index_and_detail \
  tests/component/ui/api/test_api_slack.py::TestAst1207SlackEventsDebugSot \
  -q
```

**Bible shasums** (`origin/sub/AST-1203/AST-1207-slack-events-contact-inbound-durable-debug`):
- `docs/test-bible/core/contact.md` `30fc4148c312534592a9c7ebfb92d204a9ede5fe`
- `docs/test-bible/ui/api/api_slack.md` `9b5ec3f3d6d8078645e335ec1c3704d830e4410d`

— Betty

#### joan — 2026-08-06T06:02:15.483Z
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1207
**Overall:** APPROVED
**Publish ref tip:** `sub/AST-1203/AST-1207-slack-events-contact-inbound-durable-debug` @ `043da6f2`

**Considered:** 37 of 66 active leaves scored (18 universal + 19 scoped); 29 scoped excluded on layer/path predicates — no data layer, no React, no DB/schema, no batch/dispatch/state machine, no seeding, no agent grade vectors (`orch.example.demo` is non-normative and excluded). Zero `violates`. Per-statute verdicts scored in-session (slim artifact; no attachment).

## Traceability

AC1→S1 rebind + S2 items 1–5. AC2→`CONTACT_CONFIG["debug_enabled"]=False` (`src/utils/config.py:1580`, assert `:1646`) plus every emission behind `if debug:` and `debug_index`'s `if not self._debug_flag` early return (`src/utils/logging.py:245,259`). AC3→S1 rebind feeding the existing `debug=debug` threading. Stages→definition: S1→Archie's "Manage Slack Debug is sole SoT for Contact Slack Events"; S2→`astral.standards.debug-contract-gated` found→recorded depth. No unmapped AC, no orphan stage; all seven declared in-scope statutes/patterns are addressed.

## Audit claims verified

The plan's value is its per-function "today → required" audit, so I checked every claim against the publish ref rather than trusting it. All of them hold:

- **Ingress.** `api_slack.py` imports `ui_llm_debug` at `:11` and uses it only at `:24`, so the removal is clean; the retained `CONTACT_CONFIG` import is genuinely load-bearing at `:16` (`events_http_path`), not vestigial. `scripts/slack_socket_mode_dev.py:42` is exactly `handle_slack_event(payload, debug=True)`.
- **"Today: one index" claims.** `contact_post_message` single `ok|api_error` (`:222`); `load_slack_conversation_context` `cache|slack` (`:104,130`); `append_slack_conversation_message` `appended` (`:180`); `run_contact_estelle_turn` one end summary (`:887,896`); `handle_slack_event` early rejects plus one final `accepted` (`:1170`). Each matches.
- **"Do not change" list.** `resolve_slack_user` already emits `found|matched` / `found|none` / `recorded|created` (`:607,628,681`), `run_contact_skill` `:467→494`, `post_contact_reply` `:400→409`, and `receive_slack_events_http` carries status-only indices (`:1216-1263`). Correctly left alone.
- **"Path already threads `debug=`."** Verified end to end: `:745, 819, 844` in the turn and `:1008, 1093, 1106, 1131` at ingress, plus the nested `contact_post_message → append_slack_conversation_message` at `:205`. Because `_debug_flag` lives on the shared named logger, one un-threaded callee would have silenced the remainder of a debug run — there isn't one, so AC3 is structurally satisfied rather than merely asserted.
- **Truncation.** `truncate_debug_content` and `_TEXT_DEBUG_MAX` are already imported/defined (`:47`, `:60`), so Stage 2's no-full-blobs promise needs no new machinery.
- **Dependency.** The AST-1206 foundation is real on this branch (`slack_debug_enabled` at `:316`) and on `origin/ftr/AST-1203-…`, so "already on the trunk" is accurate. It is not on `origin/dev` yet, which is expected for a child cut from ftr.

Worth recording: placing `debug = slack_debug_enabled()` *before* `log.set_debug_flag(debug)` means every Events entry sets the flag from the durable file, including setting it **False**. That closes the latched `set_debug_flag(True)` concern I raised on AST-1206, at least for this path — an admin PUT with `debug=true` cannot leave Events permanently wordy.

## discuss (non-blocking, builder's call)

**1. The `found` header in `handle_slack_event` arrives too late to help when the turn fails.** Stage 2 item 5 emits both halves "when the event was accepted and processing finished", yet every field in the `found` half (`event_type`, `user`, `channel`, `text`) is known at ingress. This function runs in a background thread whose only failure record is the `except` warning in `_run_handle_slack_event_background` (`:1179-1185`), so if `run_contact_estelle_turn` raises, the debug trail shows the early-reject gates passing and then nothing at all — no evidence the event was even accepted, which is precisely the case an operator turns Debug on for. Item 1 already gets this right (found before `post_message`, recorded after). Emitting `found` right after the last reject gate and `recorded` at the end costs nothing and makes the trail survive a crash.

**2. Three of the rewrites move the discriminating outcome out of the header into detail.** Today an operator can scan headers for `api_error` (`:222`), for `cache` vs `slack` (`:104,130`), and for the turn's real outcome string (`:887`, `outcome=str(outcome or out.get("error") or "unknown")`). Items 1, 2 and 4 replace all three with a flat `outcome="recorded"` and push the discriminator into `|` detail. Measured against AC1's word "scannable" that is a small regression, and the file already contains the remedy: `resolve_slack_user` uses compound outcomes. `recorded|api_error`, `recorded|cache`, `recorded|<turn outcome>` would keep the found→recorded shape while preserving header-level triage.

## acceptable (recorded, no action)

- The `debug` kwarg on both ingress functions becomes decorative once core re-binds. The plan names this, keeps the kwarg for signature compat with an explanatory comment, and names the consequence for Betty (set the durable flag or mock `slack_debug_enabled`). No existing test passes `debug=` to either entry — I checked the tree — so nothing breaks today.
- `slack_debug_enabled()` re-reads the durable file per inbound event, ahead of signature verification. Shipped precedent is `slack_listen_enabled()` on the same path, and the per-call read is what keeps the flag correct across gunicorn workers, so I am not scoring it.
- Stage 1's UI and script `debug=slack_debug_enabled()` arguments are behaviorally moot given the core rebind; the plan says as much ("honesty… defense in depth"). No objection.
- Local Socket Mode dev loses always-on debug and operators must flip Manage Slack Debug locally too. That is Archie's ruling, not a defect.

**Verdict:** APPROVED → Plan Approved. No fix-now items.

— Joan

context_tokens≈118000

#### hedy — 2026-08-06T05:55:06.267Z
Plan published.

**Doc:** https://github.com/susansomerset/astral/blob/sub/AST-1203/AST-1207-slack-events-contact-inbound-durable-debug/docs/features/contact/ast-1207-slack-events-contact-inbound-durable-debug.md
**Publish ref tip:** `043da6f2`

**Self-assessment**
- **Scope:** Single-Component — Events UI thin wire + Contact core durable-debug hydration and Style D found/recorded depth on existing Slack inbound/outbound helpers; no React/config/data-layer ownership.
- **Conf:** high — AST-1206 SoT already on trunk; path already threads `debug=`; this swaps SoT off `ui_llm_debug` and upgrades known summary-only Style D sites.
- **Risk:** Medium — wrong SoT leaves staging Events quiet (or reopens local auto-debug); Style D mistakes could spam `app_log` when Debug is on, but off-path stays gated and listen/Estelle behavior otherwise untouched.

---

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

---

## Review (build stub)

| Field | Value |
|-------|-------|
| Status | Code Complete |
| Publish ref | `origin/sub/AST-1203/AST-1207-slack-events-contact-inbound-durable-debug` |
| Tip | `af5dcce1caff48e600a9e40a2624b5dc9c86a9dc` |
| Branch | `sub/AST-1203/AST-1207-slack-events-contact-inbound-durable-debug` |

Stages 1–2 landed: Events/Socket hydrate from `slack_debug_enabled()`; Style D found→recorded on context load/append, `contact_post_message`, Estelle turn bookend, and `handle_slack_event` accept bookend (found early per Joan discuss).

---

## Radia review

[code-rubric] revision=1

| Field | Value |
|-------|-------|
| Rubric | code-rubric.v1 |
| Publish ref tip | `deb203754fd9c9c61147620e6949cc67f8d0cb14` |
| Overall | DISCUSS |

Full active statute corpus (65 leaves — 18 universal + 47 scoped) scored in-session against the full three-dot diff — zero `fix-now`; one `discuss`.

**What's solid:** Stage 1 (`api_slack.py` drops `ui_llm_debug`, `contact.py` re-binds `debug = slack_debug_enabled()` as the first executable line of both `handle_slack_event` and `receive_slack_events_http`, `slack_socket_mode_dev.py` swaps hardcoded `debug=True`) and Stage 2 (found→recorded Style D pairs on `load_slack_conversation_context` (both cache/slack branches), `append_slack_conversation_message`, `contact_post_message`, `run_contact_estelle_turn`, `handle_slack_event` accept bookend) match the plan line-for-line, including the Joan-discuss fix (found bookend emitted early in `run_contact_estelle_turn`/`handle_slack_event` so a mid-turn crash still leaves a trail). All new Style D gated behind `if debug:`; long text goes through `truncate_debug_content`; no new `logger.info("[DEBUG] ...")`. `src/external/slack.py` untouched (stays dumb transport).

**discuss — git branch topology on this publish ref:** Commit `28d92d70` (`Merge remote-tracking branch 'origin/sub/AST-1203/AST-1207-...' into sub/AST-1203/AST-1208-manage-slack-ui-debug-toggle`) is an ancestor of this ticket's tip, and does not use the named `merge-resume(AST-NNN): ...` commit vocabulary (`orch.git.commit-vocabulary`, universal). Net effect: this publish ref's diff vs `origin/dev` also carries AST-1208's plan doc and Betty's AST-1208 test commit as passengers (confirmed AST-1208's own tip does **not** carry AST-1207's code back — one-directional, no functional collision; `AdminManageSlack.tsx` is untouched here). Nothing to fix in the already-pushed history (rewriting would violate `orch.git.no-cherry-pick-rebase-force`) — flagging for Chuckles/Susan awareness on worktree sequencing during sibling builds, not blocking this review.

**Pattern conformance:** none cited beyond active `astral.*` statutes already scored above (`astral.standards.debug-contract-gated`, `astral.standards.logging-via-utils`, `astral.layers.import-direction`, `astral.layers.core-vs-external-bright-line`, `astral.standards.in-scope-only`, `astral.standards.dry-and-focused-functions`, `astral.standards.public-then-helpers` — all conforms).

## Frame diff
(none) — description AC/Boundaries/In-scope/Excluded checkboxes already reflect the shipped diff.

context_tokens≈9500

— Radia

---

## Resolution

**Date:** 2026-08-06  
**Radia overall:** DISCUSS (`7157b237` docs tip; product tip `af5dcce1` / Tests tip `deb20375`)  
**Fix-now:** none  
**Discuss:** git branch topology / sibling passenger commits on this publish ref — Radia flagged for Chuckles/Susan awareness on epic worktree sequencing; explicitly **not blocking** and **nothing to rewrite** in history (`orch.git.no-cherry-pick-rebase-force`). No product or plan-stage change.  
**Advisory:** none  
**Product changes this resolve:** none — tip already matches plan + zero fix-now review.

