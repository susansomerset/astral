# AST-1135 — Candidate-bound Avail count + dispatch eligibility

**Linear:** [AST-1135](https://linear.app/astralcareermatch/issue/AST-1135/candidate-bound-avail-count-dispatch-eligibility-gaze-email-candidate)
**Parent:** [AST-1128](https://linear.app/astralcareermatch/issue/AST-1128/gaze-email-candidate-bound-dispatch-redesign) — gaze_email — candidate-bound dispatch (redesign)
**Publish ref:** `origin/sub/AST-1128/AST-1135-candidate-bound-avail-dispatch-eligibility`

After AST-1134’s candidate-bound `gaze_email` rows (carve-out emptied), Scheduled Actions Avail and AUTO due selection still treat the mailbox as a fake due signal (`available_count=1` when `freq_hrs` allows) and the admin list never calls that path because `entity_type`/`trigger_state` are null. This ticket makes Avail / eligible count the live API count of current inbox messages whose From binds to the row’s `candidate_id`, and selects candidate-bound rows under normal dispatch without restoring a null-candidate or always-visible carve-out. Does **not** own runner filter / unbound Trash / `last_email_check` stamp (AST-1136) or Manage Email Land Meteorite (AST-1129).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/inbox.py` | Bind-filtered inbox count helpers (single list → per-candidate counts) | core |
| `src/data/database.py` | Retire fake `_gaze_email_available_count`; drop gaze special-case from `count_eligible_for_dispatch_task` / `get_due_tasks`; public `dispatch_task_freq_allows` | data |
| `src/core/dispatcher.py` | AUTO tick merges candidate-bound gaze due rows (live Avail + freq); click-run `available_count` enrichment for gaze | core |
| `src/ui/api/api_admin.py` | `list_dtasks` stamps live bind-filtered `available_count` for gaze rows | ui |
| `src/utils/config.py` | Comment-only: Avail is live bind-filtered (AST-1135) | utils |

No `tests/` / bible / React / `src/core/gaze_email.py` runner body / unbound hygiene / `last_email_check` call site on this ticket.

## Stage 1: Core — live bind-filtered inbox counts

**Done when:** Core can return how many current Astral inbox messages bind to a given `candidate_id` (and a full `{candidate_id: count}` map from one inbox list), reusing `list_inbox_messages` From→candidate enrichment. No admin or dispatcher wiring yet.

1. In `src/core/inbox.py`, add:

   ```python
   def count_inbox_bound_by_candidate(*, debug: bool = False) -> dict[str, int]:
       """One inbox list → {astral_candidate_id: message_count} for matched From binds."""
   ```

   Concrete behavior:
   - Call `list_inbox_messages(debug=debug)` (existing helper; raises on Gmail failure — do not swallow here).
   - Build a `dict[str, int]`: for each message, read `candidate_match`; if `matched` is true and `astral_candidate_id` is a non-empty string after strip, increment that id’s count.
   - Unmatched / unbound messages do not appear in the map (count contribution 0 for every candidate).
   - Return the map (empty dict when inbox empty).

2. In the same module, add:

   ```python
   def count_inbox_messages_bound_to_candidate(
       candidate_id: str, *, debug: bool = False
   ) -> int:
       """Live count of current inbox messages whose From binds to candidate_id."""
   ```

   Concrete behavior:
   - `cid = str(candidate_id or "").strip()`; if blank → return `0` (do not list inbox).
   - `return int(count_inbox_bound_by_candidate(debug=debug).get(cid, 0))`.

   ⚠️ **Decision — count in core/inbox, not database:** Live Avail needs Gmail list + From-bind (already owned by `inbox.py`). Data layer must not import core/external. AST-1090’s data-layer fake `1` was a null-shell due signal; parent AC4 requires the real bind-filtered count.

3. Do **not** fold `freq_hrs` / `last_run_at` into these counts — Avail is the live bind count only (Stage 2/3 gate AUTO cadence separately).
4. Do **not** change `list_inbox_messages` bind rules, Gmail external I/O, or the runner.

**Done when (recheck):** With a mocked/injected inbox of N messages binding to candidate A and M to B, `count_inbox_messages_bound_to_candidate(A) == N` and the map has keys only for matched candidates.

## Stage 2: Data — retire fake gaze avail; expose freq gate

**Done when:** `count_eligible_for_dispatch_task` no longer returns the AST-1090 fake due signal for `gaze_email`; `get_due_tasks` no longer special-cases `gaze_email` (those rows are skipped by the existing `et/ts/cid` gate like other non-claim shells); callers that need cadence use a small public freq helper. Live counting stays in core (Stage 1/3).

1. In `src/data/database.py`, **delete** `_gaze_email_available_count` entirely.

2. In `count_eligible_for_dispatch_task`, **remove** the gaze early branch:

   ```python
   # DELETE:
   tk = (task.get("task_key") or "").strip()
   if tk == GAZE_EMAIL_CONFIG["task_key"]:
       return _gaze_email_available_count(task)
   ```

   After removal, `gaze_email` rows (null `entity_type` / `trigger_state`) fall through to `if not entity_type or not state or not candidate_id: return 0`. That is correct — data no longer owns mailbox Avail.

3. In `get_due_tasks`, **remove** the `gaze_email` special-case block that called `count_eligible_for_dispatch_task` and `continue`d. After removal, AUTO gaze rows are not returned from this function (Stage 3 merges them in the dispatcher). Leave the generic `if not et or not ts or not cid: continue` path unchanged for all other keys.

4. Promote the freq/cooldown check that lived inside `_gaze_email_available_count` to a public helper (keep `_parse_dispatch_last_run_at` private; reuse it):

   ```python
   def dispatch_task_freq_allows(task: Dict[str, Any]) -> bool:
       """True when freq_hrs is 0/absent, or last_run_at is missing/stale vs freq_hrs."""
   ```

   Concrete behavior (same math as the deleted helper):
   - `freq = float(task.get("freq_hrs") or 0)`.
   - If `freq <= 0`: return `True`.
   - `last = _parse_dispatch_last_run_at(task.get("last_run_at"))`; if `last is None`: return `True`.
   - Return `True` iff `(datetime.now(timezone.utc) - last).total_seconds() >= freq * 3600`.

   ⚠️ **Decision — freq gates AUTO due only, not Avail:** Parent AC4 says Avail equals the live bind count. Folding freq into `available_count` would hide real inbox work under Scheduled Actions after a recent run. Cadence stays a separate due predicate in Stage 3.

5. Update module/doc comments that still describe gaze as “available_count=1 when due” / null-candidate due signal (header inventory / `get_due_tasks` docstring) so they no longer claim data-layer gaze Avail.
6. Do **not** import `src.core.inbox` from `database.py`. Do **not** re-add always-visible carve-out keys.

**Done when (recheck):** `count_eligible_for_dispatch_task({task_key: gaze_email, candidate_id: "x", entity_type: None, trigger_state: None}) == 0`; `get_due_tasks()` never includes a gaze row; `dispatch_task_freq_allows` matches the old cooldown math.

## Stage 3: Admin Avail stamp + dispatcher due / click enrichment

**Done when:** `GET /api/admin/dispatch_tasks` shows live bind-filtered Avail on each candidate-bound `gaze_email` row; zero-Avail gaze rows are not kept visible by any gaze-specific carve-out (AST-1134 already emptied the config tuple); AUTO tick can select candidate-bound gaze rows when live Avail ≥ `min_count` and freq allows; click-run enrichment records the same live Avail on the task dict. Runner body unchanged.

1. In `src/ui/api/api_admin.py` `list_dtasks()`, replace the per-row Avail assignment so gaze rows are not stuck at `0` by the `et and ts and cid` gate:

   - Import `GAZE_EMAIL_CONFIG` (if not already) and `count_inbox_bound_by_candidate` from `src.core.inbox`.
   - **Before** the per-row loop (or once when any gaze row with non-blank `candidate_id` exists): try `bound_counts = count_inbox_bound_by_candidate()`; on exception, log a warning (same style as today’s per-row failure log) and set `bound_counts = {}`.
   - Inside the loop, when `(row.get("task_key") or "").strip() == GAZE_EMAIL_CONFIG["task_key"]`:
     - `cid = str(row.get("candidate_id") or "").strip()`
     - `row["available_count"] = int(bound_counts.get(cid, 0)) if cid else 0`
     - Do **not** call `database.count_eligible_for_dispatch_task` for these rows.
   - Else keep the existing `et and ts and cid` → `count_eligible_for_dispatch_task` / else `0` path (including its try/except).
   - Keep stamping `always_visible_under_avail_gt0` from the (now empty) config helper — do not hardcode `gaze_email` into that set.

   ⚠️ **Decision — one inbox list per `list_dtasks`:** Avail for every candidate-bound gaze row is derived from the same current inbox snapshot. Re-listing Gmail once per row would repeat the same external call without changing the AC result.

2. In `src/core/dispatcher.py`, add a focused helper (module-private is fine):

   ```python
   def _gaze_email_due_tasks() -> List[Dict[str, Any]]:
       """AUTO candidate-bound gaze_email rows with live Avail ≥ min_count and freq allowing."""
   ```

   Concrete steps:
   - `tk = GAZE_EMAIL_CONFIG["task_key"]`.
   - Collect `auto_gaze = [t for t in database.list_dispatch_tasks() if (t.get("task_key") or "").strip() == tk and bool(t.get("auto_mode")) and str(t.get("candidate_id") or "").strip()]`.
   - If none: return `[]`.
   - Try `bound_counts = count_inbox_bound_by_candidate()`; on exception, log warning and return `[]` (do not crash the tick).
   - For each task in `auto_gaze`:
     - `cid = str(task["candidate_id"]).strip()`
     - `avail = int(bound_counts.get(cid, 0))`
     - If `avail < (task.get("min_count") or 1)`: skip.
     - If not `database.dispatch_task_freq_allows(task)`: skip.
     - Set `task["available_count"] = avail` and append a copy/`task` to the result list.
   - Return that list.

3. In `_tick_loop`, after `due = database.get_due_tasks()`, merge:

   ```python
   due = list(due) + _gaze_email_due_tasks()
   ```

   Keep existing slot / already-running / `run_task` logic. Update the nearby comment that claims freq is never a task-level cooldown so it notes gaze_email AUTO uses `dispatch_task_freq_allows` as task cadence (mailbox has no claim-queue entity filter).

4. In the click/manual path that sets `task["available_count"]` only when `et and ts` (today ~line that assigns `0` for mailbox shells), when `task_key == GAZE_EMAIL_CONFIG["task_key"]` and `candidate_id` is non-blank: set `available_count` via `count_inbox_messages_bound_to_candidate(candidate_id)` inside try/except → `0` on failure. Leave non-gaze behavior unchanged.

5. In `src/utils/config.py`, update the `GAZE_EMAIL_CONFIG` block comment: remove “live bind-filtered Avail is AST-1135” deferral wording; state that Avail/eligible count is the live bind-filtered inbox count (AST-1135) while `entity_type`/`trigger_state` remain `None` (no claim queue). Do **not** change key values, seed sizes, `auto_mode`, or secrets.

6. Do **not** edit React `AdminScheduledActions.tsx` — with real `available_count` and an empty always-visible set, default Avail > 0 shows rows that have bind work and hides zero-Avail gaze rows (parent AC4).
7. Do **not** change `run_gaze_email` message filtering, unbound Trash, or `update_candidate_last_email_check` (AST-1136).
8. Do **not** restore null-`candidate_id` provision or re-seed `always_visible_under_avail_gt0_dispatch_task_keys`.

**Done when (recheck):** Admin list for candidate A’s `gaze_email` row shows Avail = number of current inbox messages binding to A; with Avail 0 the row is absent under default Avail > 0 (no carve-out); with AUTO on, bind count ≥ `min_count`, and freq allowing, `_tick_loop`’s due set includes that row; with freq blocking, it does not.

## Self-Assessment

**Scope:** `Single-Component` — core inbox count + data fake-avail retirement + dispatcher due merge + thin admin Avail stamp for one task key; no runner rewrite.

**Conf:** `high` — bind enrichment already exists on `list_inbox_messages`; AST-1134 already emptied the carve-out and bound every candidate row; this ticket swaps the known fake due signal for the parent’s live count at the correct layer.

**Risk:** `Medium` — wrong count or due merge would hide/show Scheduled Actions rows or AUTO-fire mailbox tasks with no work / miss real work; mitigated by one shared inbox snapshot and explicit freq-vs-Avail split.

## Rules check (plan vs ASTRAL_CODE_RULES)

- §1.3 DRY — reuse `list_inbox_messages` bind enrichment; one list → many candidate counts; no parallel bind pipeline.
- §2.1 config — task key still from `GAZE_EMAIL_CONFIG`; no new hardcoded gaze sets in React; carve-out tuple stays empty.
- §2.4 batch — still no claim/get/clear for mailbox; Avail is a count, not a claim queue.
- §2.6 state machine — no job/candidate state transitions on this ticket.
- §3.3 imports — ui→core and core→external allowed; data must not import core for Gmail/bind (fake data avail removed).
- §3.5 naming — `count_inbox_messages_bound_to_candidate` / `count_inbox_bound_by_candidate` / `dispatch_task_freq_allows` / `_gaze_email_due_tasks`.
- Statute `astral.layers.core-vs-external-bright-line` / `pattern.layers.import-discipline` — Gmail stays external; bind count orchestration in core; admin stays thin.
- Statute `astral.standards.no-hardcoded-sets` — compare via `GAZE_EMAIL_CONFIG["task_key"]` only.
- Statute `pattern.ui.admin-endpoint` — Avail resolved in API from core count, not React business rules.
- Out of scope: runner / unbound hygiene / Manage Email (AST-1129) / tests tree.

## Review

**Publish ref:** `origin/sub/AST-1128/AST-1135-candidate-bound-avail-dispatch-eligibility`
**Tip:** 
**Overall:** _(pending Radia)_
