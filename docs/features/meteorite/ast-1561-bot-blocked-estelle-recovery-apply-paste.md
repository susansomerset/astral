# AST-1561 — BOT_BLOCKED Estelle recovery + apply_paste

**Linear:** [AST-1561](https://linear.app/astralcareermatch/issue/AST-1561/bot-blocked-estelle-recovery-apply-paste)  
**Parent:** [AST-1555](https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation) — Meteorite ingress: staging table + inbox/meteorite consolidation  
**Publish ref:** `sub/AST-1555/AST-1561-bot-blocked-estelle-recovery-apply-paste`

After AST-1560 scrape can land staging rows in `BOT_BLOCKED`: scheduled notify scan → Estelle DM (paste request + blocked link) → stamp `estelle_notified_at` / `estelle_thread_ts`; candidate paste in that thread (or unprompted `paste` source_kind) → `apply_paste` replaces `content` and moves row to `READY` **without re-classify**; nag budget exhausted → `ABANDONED`. Scrape/Playwright never posts to Slack. Does not own retention purge or delete `meteorite_email.py`.

## Scope gate

Linear child **## Scope** / **## Citations** headings are empty (dispatch template gap). Authoritative partition is parent **Proposed child tickets → #5**:

- `src/core/meteorite.py` — `apply_paste` + notify/abandon helpers + dispatch notify runner
- `src/core/contact.py` — inbound Slack paste → `apply_paste` (thread match + unprompted `paste` source_kind)
- `src/utils/config.py` + `src/core/dispatcher.py` + `data/admin/dispatch_task.json` — notify task key, nag limits, message templates, seed row

**Citations (parent #5):** `pattern.state.entity-state-transitions`, `astral.agent.do-task-delegation` (no re-classify on paste recovery), `astral.layers.core-vs-external-bright-line` (scrape never Slack; Slack I/O via contact → external only)

**Out of scope (siblings):** AST-1557 table/claim helpers (consume only); AST-1558 inbox/Manage Email; AST-1559 `check_inbox` + inbox monitoring; AST-1560 stage/scrape/land (consume `BOT_BLOCKED` rows from scrape); AST-1562 retention + delete `meteorite_email.py`. Do **not** edit `src/data/database.py` (no new SQL helpers — filter in core over `list_meteorites_by_state`), `src/external/slack.py`, `tests/`, or `docs/test-bible/**`.

**AC partition (this ticket):** Parent AC4 — `BOT_BLOCKED` rows get an Estelle DM once; candidate paste in that thread moves the row to `READY` without re-classify; exceeding nag limit moves the row to `ABANDONED`.

**Depends on:** **AST-1557** (`meteorite` table, `get_meteorite` / `update_meteorite` / `list_meteorites_by_state`, `METEORITE_STATES`) and **AST-1560** (scrape → `BOT_BLOCKED` + `log_meteorite_row_transition`) on the epic line. After `sync-child.sh`, if `METEORITE_INGRESS_DISPATCH_CONFIG` or `run_scrape_meteorite` is missing on HEAD, **stop** and comment on AST-1561 — do not re-implement table/scrape slices here.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `METEORITE_BOT_BLOCKED_NOTIFY_CONFIG` (task key, batch size, nag limit, DM message templates, debug_func); header inventory + asserts | utils |
| `data/admin/dispatch_task.json` | Idempotent dispatch row for notify runner (`auto_mode` false) | catalog |
| `src/core/dispatcher.py` | Custom branch for notify task key → `run_notify_meteorite_bot_blocked` (mailbox-style `entity_batch_id` + ledger) | core |
| `src/core/meteorite.py` | `apply_paste`, paste lookup helpers, `run_notify_meteorite_bot_blocked`, `_resolve_slack_dm_channel_for_candidate` | core |
| `src/core/contact.py` | Pre-turn paste hook in `handle_slack_event`; unprompted-`paste` guard on `land_calls` → `apply_paste` instead of `stage_meteorite` | core |

## Stage 1: Config + dispatch seed + dispatcher registration

**Done when:** `METEORITE_BOT_BLOCKED_NOTIFY_CONFIG` exposes notify task key, batch size, nag limit, and DM template strings; one `SEED_CONFIG` entry + matching `data/admin/dispatch_task.json` row exist; `dispatcher._dispatch_one` recognizes the notify key and delegates to `run_notify_meteorite_bot_blocked` with minted `entity_batch_id` (stub runner returning `_ZERO_SUMMARY` OK until Stage 2); `python3 -m py_compile src/utils/config.py src/core/dispatcher.py` succeeds.

1. In `src/utils/config.py` module header inventory, add bullet for `METEORITE_BOT_BLOCKED_NOTIFY_CONFIG` — BOT_BLOCKED Estelle notify + nag limits (AST-1561).

2. After `METEORITE_INGRESS_DISPATCH_CONFIG` block (AST-1560 — must exist on branch), insert:

```python
# AST-1561: scheduled BOT_BLOCKED → Estelle DM + nag → ABANDONED (no scrape/Slack in scrape path).
METEORITE_BOT_BLOCKED_NOTIFY_CONFIG = {
    "task_key": "meteorite_bot_blocked_notify",
    "trigger_state": "BOT_BLOCKED",  # dispatch_task.trigger_state literal (claim filter)
    "batch_size": 10,
    "nag_limit": 3,  # max outbound DMs per row (first notify + nags); 4th pass → ABANDONED
    "debug_func": "meteorite.run_notify_meteorite_bot_blocked",
    "dm_first_template": (
        "That job link hit a bot block. Please paste the full job description text here "
        "(copy from the listing page). Blocked link: {link}"
    ),
    "dm_nag_template": (
        "Still waiting on the job description paste for the blocked listing. "
        "Link: {link} ({nag_count}/{nag_limit})"
    ),
}
```

3. Asserts immediately after the block:

- `task_key` is non-empty str; `trigger_state == "BOT_BLOCKED"` and ∈ `METEORITE_STATES`
- `batch_size` is int ≥ 1; `nag_limit` is int ≥ 1
- Both templates are non-empty str containing `{link}`; nag template also contains `{nag_count}` and `{nag_limit}`
- `debug_func` is non-empty str

4. Add `SEED_CONFIG["dispatch_task-meteorite-bot-blocked-notify"]` following peer global dispatch rows (NULL `candidate_id`, `task_key` from config, `entity_type` NULL, `trigger_state` = `BOT_BLOCKED`, `batch_size` from config, `auto_mode` 0, conservative `freq_hrs` / `min_count` like AST-1560 transition seeds).

5. Add matching row to `data/admin/dispatch_task.json` (same literals as SEED_CONFIG).

6. In `src/core/dispatcher.py`, add `_is_meteorite_bot_blocked_notify_task_key(task_key) -> bool` comparing to `METEORITE_BOT_BLOCKED_NOTIFY_CONFIG["task_key"]`.

7. In `_dispatch_one`, add branch **after** AST-1560 ingress transition branch and **before** mailbox `meteorite_email` branch:

   - Mint one `entity_batch_id = f"{task_key}-{uuid4()}"`; `save_dispatch_ledger(...)`; `log_batch_id.set(entity_batch_id)`; set `task["entity_batch_id"] = entity_batch_id`.
   - Late-import `from src.core.meteorite import run_notify_meteorite_bot_blocked`.
   - `summary = await run_notify_meteorite_bot_blocked(task, debug=debug)` — **do not** `asyncio.run` here (`_dispatch_one` is already async; nested `asyncio.run` breaks the loop — mirror `run_meteorite_email` / AST-1560 ingress `await` branches).
   - Accumulate summary counts from runner dict; clear `log_batch_id` in `finally`.

⚠️ **Decision:** Notify uses the same global NULL-`candidate_id` dispatch row shape as scrape/land — row `candidate_id` column is authoritative at DM time.

⚠️ **Decision:** `nag_limit` counts **outbound** DM attempts per row (first notify = 1). When `nag_count >= nag_limit` on a scheduled pass, transition `ABANDONED` instead of sending another DM.

## Stage 2: `meteorite.py` — `apply_paste` + notify runner

**Done when:** `apply_paste` moves a `BOT_BLOCKED` row to `READY` with replaced normalized content and no classify/scrape calls; `run_notify_meteorite_bot_blocked` claims `BOT_BLOCKED` rows, sends first DM or nag via contact-layer post helper, stamps Estelle fields or abandons; lookup helpers resolve rows by Estelle thread or unprompted `paste` source_kind; `python3 -m py_compile src/core/meteorite.py` succeeds.

1. Extend `src/core/meteorite.py` imports:

   - From `src.data.database`: add `list_meteorites_by_state` if not already imported.
   - From `src.utils.formatting`: `normalize_pasted_list_email_html` (paste normalize SSOT — AST-1131).

2. Add **`_normalize_apply_paste_content(raw: str) -> str`**:

   - `text = (raw or "").strip()`; empty → return `""`.
   - If `"<" in text and ">" in text`, run `normalize_pasted_list_email_html(text)` then strip tags crudely: reuse existing plain-text extraction pattern from contact land blob assembly (strip HTML to visible text — if no shared helper, use `strip_extract_email_html` from inbox **only when** input looks like email HTML wrapper; else after normalize take text with a minimal tag-strip regex `\n` join of text nodes is **not** required — call `normalize_pasted_list_email_html` then `re.sub(r"<[^>]+>", " ", text)` and collapse whitespace).
   - Else return collapsed whitespace single newlines preserved between paragraphs (`"\n\n".join(line.strip() for line in text.splitlines() if line.strip())`).

3. Add **`find_meteorite_for_estelle_thread(*, candidate_id: str, thread_ts: str) -> Optional[dict]`**:

   - Require non-empty `candidate_id` and `thread_ts`.
   - `rows = list_meteorites_by_state("BOT_BLOCKED")` — filter where `row["candidate_id"] == candidate_id` and `(row.get("estelle_thread_ts") or "").strip() == thread_ts.strip()`.
   - Return the sole match if exactly one; if multiple, return the one with highest `id`; if zero, return `None`.
   - Do **not** add DB queries beyond existing list helper.

4. Add **`find_meteorite_bot_blocked_paste_source(*, candidate_id: str) -> Optional[dict]`** (unprompted `paste` source_kind):

   - Filter `list_meteorites_by_state("BOT_BLOCKED")` where `candidate_id` matches and `(row.get("source_kind") or "").strip() == "paste"`.
   - Return sole row if exactly one; if multiple, return highest `id`; else `None`.

5. Add **`apply_paste(meteorite_id: int, pasted_text: str, *, debug: bool = False) -> dict`**:

   - Load row via `get_meteorite(meteorite_id)`; missing → `{"ok": False, "error": "not_found"}`.
   - Require `row["state"] == "BOT_BLOCKED"` else `{"ok": False, "error": "invalid_state", "state": row["state"]}`.
   - `content = _normalize_apply_paste_content(pasted_text)`; if not content → `{"ok": False, "error": "empty_paste"}`.
   - `update_meteorite(meteorite_id, content=content, state="READY", error=None)` — **no** `invoke_stage_meteorite`, **no** Playwright, **no** classify.
   - Do **not** call `log_meteorite_row_transition` for `READY` — AST-1560 helper only formats `BOT_BLOCKED` / `ERROR` / `LANDED` lines; paste recovery is silent at info (Joan acceptable).
   - Return `{"ok": True, "meteorite_id": meteorite_id, "state": "READY"}`.

6. Add **`_resolve_slack_dm_channel_for_candidate(candidate_id: str) -> Optional[str]`**:

   - Load candidate via `get_candidate(candidate_id)`; read `candidate_data.contact.slack_user_id` (walk dict safely).
   - If no slack user id → return `None`.
   - Load `contact_estelle_activity` store via `load_estelle_activity_store()`; read `by_slack_user_id[uid].last_channel` when present and channel id starts with `"D"` (DM).
   - Return channel id or `None` (no new `conversations.open` — external/slack.py is out of Scope).

7. Add **`_format_bot_blocked_dm(row: dict, *, nag_count: int, nag_limit: int, first: bool) -> str`**:

   - `link = (row.get("link") or "").strip() or "(no link)"`.
   - Pick template from `METEORITE_BOT_BLOCKED_NOTIFY_CONFIG`; `.format(link=link, nag_count=nag_count, nag_limit=nag_limit)`.

8. Add **`async def run_notify_meteorite_bot_blocked(task: dict, *, debug: bool = False) -> dict`**:

   - Mirror `run_scrape_meteorite` batch pattern: read `entity_batch_id`, `batch_size`, `task_key` from task + config; `claim_meteorite_batch(batch_id, "BOT_BLOCKED", limit=batch_size)`; `rows = get_meteorite_batch(batch_id)`; `finally: clear_meteorite_batch(batch_id)`.
   - Initialize `summary = dict(_ZERO_SUMMARY)`.
   - For each row:
     - `summary["total_processed"] += 1`
     - `nag_limit = int(METEORITE_BOT_BLOCKED_NOTIFY_CONFIG["nag_limit"])`
     - `nag_count = int(row.get("nag_count") or 0)`
     - If `nag_count >= nag_limit`: `update_meteorite(row_id, state="ABANDONED", error="nag limit exceeded")`; call `log_meteorite_row_transition` with `state="ABANDONED"` if available; `summary["total_passed"] += 1`; continue.
     - Resolve DM channel via `_resolve_slack_dm_channel_for_candidate(cid)`; if missing: `update_meteorite(row_id, error="no slack dm channel")`; `summary["total_failed"] += 1`; continue (leave state `BOT_BLOCKED` for retry when activity exists).
     - `first = row.get("estelle_notified_at") is None`
     - Build message via `_format_bot_blocked_dm(..., nag_count=nag_count + 1, first=first)`.
     - Late-import `from src.core.contact import contact_post_message`; `resp = contact_post_message(channel=channel, text=message, thread_ts=None, debug=debug)`.
     - If not `resp.get("ok")`: set `error` from resp; increment failures; continue.
     - `thread_ts = str(resp.get("ts") or resp.get("message", {}).get("ts") or "").strip()` (accept Slack response shapes contact already uses).
     - `update_meteorite(row_id, estelle_notified_at=<utc now iso>, estelle_thread_ts=thread_ts or row.get("estelle_thread_ts"), nag_count=nag_count + 1, error=None)` — on first notify, **set** `estelle_thread_ts` to outbound message `ts` (top-level thread anchor for paste replies).
     - `summary["total_passed"] += 1`
   - Return summary.

⚠️ **Decision:** Paste recovery never calls Ruth / `stage_meteorite` — `astral.agent.do-task-delegation` satisfied by content replace + state transition only.

⚠️ **Decision:** DM channel comes from Estelle activity `last_channel` only — if candidate never DM'd Estelle, notify fails soft (`error` column) until activity exists; no new Slack API wrapper in this ticket.

## Stage 3: `contact.py` — paste routing to `apply_paste`

**Done when:** Inbound Slack DM/app_mention events attempt paste recovery before Estelle turn; matching Estelle notify thread or unprompted `paste` source_kind row calls `apply_paste`; successful apply skips `land_calls` → `stage_meteorite` for that message; no Gmail/inbox imports; `python3 -m py_compile src/core/contact.py` succeeds.

1. Update `src/core/contact.py` module docstring: AST-1561 BOT_BLOCKED paste recovery via `apply_paste` (no re-classify).

2. Add **`try_meteorite_apply_paste_from_slack(*, astral_candidate_id: Optional[str], channel: str, thread_ts: Optional[str], message_ts: Optional[str], text: str, debug: bool = False) -> dict`**:

   - If no `astral_candidate_id` or empty `text.strip()` → `{"applied": False}`.
   - Late-import lookup helpers from meteorite.
   - **Thread path (first):** When `(thread_ts or message_ts)` is non-empty, set `anchor = (thread_ts or message_ts).strip()` and `row = find_meteorite_for_estelle_thread(candidate_id=astral_candidate_id, thread_ts=anchor)`.
   - **Unprompted `paste` source_kind (second):** If `row` is still `None`, `row = find_meteorite_bot_blocked_paste_source(candidate_id=astral_candidate_id)` — runs regardless of whether `anchor` was set (candidate may paste in the main DM without threading to the notify `ts`; match is by `source_kind=paste` + `BOT_BLOCKED` only).
   - If no row → `{"applied": False}`.
   - Call `apply_paste(int(row["id"]), text, debug=debug)`; return `{"applied": True, "result": ...}`.

3. In **`handle_slack_event`**, after inbound cache append and **before** `run_contact_estelle_turn`:

   - `paste_out = try_meteorite_apply_paste_from_slack(astral_candidate_id=result.get("astral_candidate_id"), channel=channel, thread_ts=event.get("thread_ts"), message_ts=msg_ts, text=text, debug=debug)`
   - Store on `result["meteorite_apply_paste"] = paste_out`.
   - If `paste_out.get("applied")` and `paste_out.get("result", {}).get("ok")`:
     - Post short ack via existing `contact_post_message` + `format_contact_reply_text`: use `CONTACT_CONFIG["hear_ack_reply_text"]` or fixed one-liner `"Got it — pasted job description saved for review."` (inline string in contact.py — **do not** add config block).
     - Set `result["estelle_turn"] = {"ok": True, "outcome": "paste_applied", "meteorite_apply_paste": paste_out}` and **skip** `run_contact_estelle_turn` for this event (no `land_calls` classify).

4. In **`run_contact_estelle_turn`** `land_calls` loop, **before** each `contact_land_meteorite` call:

   - If candidate has `find_meteorite_bot_blocked_paste_source(candidate_id=astral_candidate_id)` and inbound `text` non-empty (pass `text` param through turn — already available): call `apply_paste` instead of `contact_land_meteorite`; append to `land_results` as `{"ok": True, "result": apply_out, "via": "apply_paste"}`; **continue** loop without staging classify.

   - Extend `run_contact_estelle_turn` signature only if `text` is not already in scope — it is (`text` param exists); use it for unprompted paste detection when Estelle emits empty `land_calls` but user pasted body text (guard: only when `source_kind` would have been `paste` — i.e. when paste-source row exists).

5. Do **not** import Playwright, inbox, or Gmail. Do **not** edit `handle_slack_event` signature.

⚠️ **Decision:** Successful thread paste short-circuits the Estelle LLM turn — paste is operational recovery, not a consult hop.

## Execution contract

- Execute stages in order; one commit per stage on epic worktree; publish each to `origin/sub/AST-1555/AST-1561-bot-blocked-estelle-recovery-apply-paste`.
- Do not add files outside Files Changed. Do not edit `tests/` (Betty).
- If table helpers or AST-1560 scrape runner missing after sync, stop and comment on AST-1561.
- On ambiguity: stop, comment on parent with Stage blocked template.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Revisions

Revision 1 — 2026-08-31  
Driven by: Joan `[plan-rubric]` REVISE @ `116ca135` (Plan Discuss)  
Changes: Stage 1 §7 — notify branch uses `await run_notify_meteorite_bot_blocked` (no nested `asyncio.run`). Stage 2 §5 — drop `READY` monitoring log (AST-1560 helper has no format). Stage 3 §2 — unprompted paste: thread lookup first, then `find_meteorite_bot_blocked_paste_source` when no thread match (anchor optional).

## Joan validate

**Rubric:** plan-rubric
**Ticket:** AST-1561
**Overall:** REVISE
**Publish ref:** `sub/AST-1555/AST-1561-bot-blocked-estelle-recovery-apply-paste` @ `116ca1352f65a3aa937b52ff00c450df1856fd08`

### Traceability
Parent AC4 → Stages 2–3 (`run_notify_meteorite_bot_blocked` first DM + nag/abandon stamps; `apply_paste` `BOT_BLOCKED`→`READY` without classify; `contact.py` thread + unprompted `paste` routing); parent functional scope #4 (Estelle notify, paste recovery, nag→`ABANDONED`, scrape never Slack) mapped to Stages 1–3.

### Findings

#### fix-now
- **Location:** Stage 1 §7 — dispatcher notify branch
- **Finding:** Plan calls `asyncio.run(run_notify_meteorite_bot_blocked(...))` inside `_dispatch_one`, which is already `async` and peers use `await` (`run_meteorite_email`, ingress transition runners). Nested `asyncio.run` will break the event loop.
- **Recommendation:** `summary = await run_notify_meteorite_bot_blocked(task, debug=debug)` — mirror mailbox/AST-1560 ingress branches.

#### acceptable
- **Location:** Linear ticket — empty `## Citations` / `## Scope`
- **Finding:** Dispatch template gap; plan Scope gate mirrors parent proposed child #5.
- **Recommendation:** Chuckles backfill Linear fields when appending; plan content is scoped.

#### acceptable
- **Location:** Stage 2 §5 — `log_meteorite_row_transition(..., state="READY")`
- **Finding:** AST-1560 helper logs only `BOT_BLOCKED` / `ERROR` / `LANDED`; `READY` is a no-op log.
- **Recommendation:** Drop READY log call or accept silent paste recovery; not blocking AC4.

#### discuss
- **Location:** Stage 3 §2 — unprompted paste guard
- **Finding:** Unprompted path runs only when `no row and anchor`; wording is easy to mis-implement vs "if no row after thread lookup."
- **Recommendation:** Clarify: thread match first; else `find_meteorite_bot_blocked_paste_source` when `source_kind=paste` row exists (anchor optional).

**In-session statute pass:** `entity_batch_id` golden ticket + claim/clear — **astral.batch.batch-id-first** conforms. Paste without `do_task`/classify — **astral.agent.do-task-delegation** conforms. Slack via `contact_post_message` only — **astral.layers.core-vs-external-bright-line** conforms. `BOT_BLOCKED`→`READY` / `ABANDONED` via core `update_meteorite` — **pattern.state.entity-state-transitions** conforms. Universal orch.* — N/A/conforms.

## Joan validate (round 2)

**Rubric:** plan-rubric
**Ticket:** AST-1561
**Overall:** APPROVED
**Publish ref:** `sub/AST-1555/AST-1561-bot-blocked-estelle-recovery-apply-paste` @ `fa4b19353058dfeb606ad7e44f2132a1a4bda826`

### Traceability
Parent AC4 → Stages 2–3 (`run_notify_meteorite_bot_blocked` Estelle DM + nag/abandon stamps; `apply_paste` `BOT_BLOCKED`→`READY` without classify; `contact.py` thread-first then unprompted `paste` routing); parent functional scope #4 (notify, paste recovery, nag→`ABANDONED`, scrape never Slack).

### Findings

#### acceptable
- **Location:** Linear ticket — empty `## Citations` / `## Scope`
- **Finding:** Dispatch template gap; plan Scope gate mirrors parent proposed child #5.
- **Recommendation:** Chuckles backfill Linear fields when appending.

#### acceptable
- **Location:** Stage 2 §8 — `log_meteorite_row_transition` on `ABANDONED`
- **Finding:** AST-1560 helper has no `ABANDONED` format (no-op if called).
- **Recommendation:** Harmless; optional drop in build.

**Round=1 resolution:** `await` notify runner, unprompted-paste ordering clarified, READY monitoring log dropped — revision @ `fa4b1935`.

**In-session statute pass:** `entity_batch_id` claim/clear — **astral.batch.batch-id-first** conforms. No re-classify on paste — **astral.agent.do-task-delegation** conforms. Slack via `contact_post_message` only — **astral.layers.core-vs-external-bright-line** conforms. State transitions via core `update_meteorite` — **pattern.state.entity-state-transitions** conforms. Universal orch.* — N/A/conforms.
