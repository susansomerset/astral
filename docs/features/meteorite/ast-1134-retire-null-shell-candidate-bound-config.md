# AST-1134 — Retire null shell — candidate-bound config, schema, provision, last_email_check

**Linear:** [AST-1134](https://linear.app/astralcareermatch/issue/AST-1134/retire-null-shell-candidate-bound-config-schema-provision-last-email)
**Parent:** [AST-1128](https://linear.app/astralcareermatch/issue/AST-1128/gaze-email-candidate-bound-dispatch-redesign) — gaze_email — candidate-bound dispatch (redesign)
**Publish ref:** `origin/sub/AST-1128/AST-1134-retire-null-shell-candidate-bound-config`

Retires the shared null-`candidate_id` `gaze_email` dispatch shell as the primary design. Moves `GAZE_EMAIL_CONFIG` / `TASK_CONFIG["gaze_email"]` expectations to candidate-bound rows (keep `unbound_retention_days`), adds `candidate.last_email_check` (default null) plus a data-layer stamp helper, provisions one `gaze_email` `dispatch_task` per every `candidate` row via coverage join, and removes the AST-1106 always-visible-under-Avail-gt0 carve-out for this task. Does **not** own live bind-filtered Avail count (AST-1135) or the per-message runner / unbound hygiene / `last_email_check` call site (AST-1136).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Candidate-bound `GAZE_EMAIL_CONFIG` / `TASK_CONFIG["gaze_email"]` comments + keys; empty always-visible tuple | utils |
| `src/data/database.py` | `candidate.last_email_check`; stamp helper; require `candidate_id` on `save_dispatch_task` for `gaze_email` | data |
| `src/core/dispatcher.py` | Coverage-join provision; retire null shell; ledger uses row `candidate_id` | core |

No `tests/` / bible / React / `src/core/gaze_email.py` runner body / live inbox Avail count on this ticket.

## Stage 1: Candidate-bound config + retire Avail carve-out

**Done when:** `GAZE_EMAIL_CONFIG` documents candidate-bound rows (still owns `unbound_retention_days` + seed sizes); `TASK_CONFIG["gaze_email"]` remains a non-claim mailbox shell (`entity_type`/`trigger_state` null) but no longer describes a null-`candidate_id` primary design; `admin_always_visible_under_avail_gt0_dispatch_task_keys()` is empty so Scheduled Actions no longer special-cases `gaze_email` under Avail > 0; Gmail secrets stay environ-only.

1. In `src/utils/config.py`, rewrite the `GAZE_EMAIL_CONFIG` block comment from “shared Astral inbox … null candidate_id row” to candidate-bound dispatch rows (AST-1134 / parent AST-1128). Keep keys that still apply:
   - `task_key`, `account_address`, `unbound_retention_days`, `auto_mode`, `min_count`, `batch_size`, `freq_hrs`
   - `entity_type`: `None` (mailbox poller — no ENTITY_TYPES claim queue; Avail remains task-key special-cased until AST-1135)
   - `trigger_state`: `None`
   - `subject_url_schemes`, `debug_func` (runner literals for AST-1136; do not change values)
2. **Remove** `dispatch_ledger_candidate_id` from `GAZE_EMAIL_CONFIG` (empty-string ledger placeholder for the null shell). Ledger candidate id becomes the `dispatch_task.candidate_id` on the row (Stage 3).
3. Keep existing asserts for `unbound_retention_days`, `task_key`, `subject_url_schemes`, `debug_func`, `auto_mode`. Do **not** add a new assert that requires `dispatch_ledger_candidate_id`.
4. Update `TASK_CONFIG["gaze_email"]` comment from “mailbox dispatch shell” null-shell wording to “candidate-bound mailbox dispatch shell (no claim queue; row binds via `dispatch_task.candidate_id`)”. Keep:
   ```python
   "gaze_email": {
       "entity_type": None,
       "requires_candidate_key": False,
       "trigger_state": None,
   },
   ```
   ⚠️ **Decision — keep null entity/trigger on the shell:** Parent requires candidate-bound **rows**, not an entity claim queue. Live bind-filtered Avail is AST-1135. Setting `entity_type="candidate"` here would route `count_eligible_for_dispatch_task` into inflow-discovery counting and is out of scope.
5. Keep the `dispatch_task_admin_defaults` early return for `GAZE_EMAIL_CONFIG["task_key"]` that returns null entity/trigger/sort_by and `batch_call_mode=0` — still correct for a non-claim mailbox row.
6. In `ADMIN_CONFIG`, set `"always_visible_under_avail_gt0_dispatch_task_keys"` to an empty tuple `()`. Update the comment to note AST-1134 retired the gaze_email mailbox carve-out (helper + API stamp may remain for empty/future keys). Do **not** delete `admin_always_visible_under_avail_gt0_dispatch_task_keys()` or the API/React generic flag plumbing — emptying the config source is enough to remove the special case.
7. Do **not** move Gmail OAuth / `GMAIL_USER` into config. Do **not** change `unbound_retention_days` value. Do **not** edit React `AdminScheduledActions.tsx`.

**Done when (recheck):** `GAZE_EMAIL_CONFIG` has no `dispatch_ledger_candidate_id`; `admin_always_visible_under_avail_gt0_dispatch_task_keys()` is empty; `dispatch_task_admin_defaults("gaze_email")` still returns null entity/trigger.

## Stage 2: `candidate.last_email_check` + require bound `candidate_id` on save

**Done when:** Every `candidate` row has nullable `last_email_check` (default null on create/migrate); `update_candidate_last_email_check` can stamp an ISO timestamp; `save_dispatch_task` rejects null/blank `candidate_id` for `gaze_email` the same as every other task_key.

1. In `src/data/database.py` module header inventory for `candidate`, note `last_email_check` (nullable timestamp; stamped after `gaze_email` runs — AST-1134 column / AST-1136 call site).
2. In `_ensure_candidate_schema`:
   - Add `last_email_check TIMESTAMP` to the fresh `CREATE TABLE candidate` column list (nullable, no DEFAULT needed — SQLite NULL).
   - Add `("last_email_check", "TIMESTAMP")` to the idempotent `ALTER TABLE … ADD COLUMN` migration loop so existing DBs gain the column.
3. Add a focused stamp helper next to other candidate writers (near `clear_candidate_api_key` / similar):

   ```python
   def update_candidate_last_email_check(
       candidate_id: str, when: Optional[str] = None
   ) -> None:
       """Set candidate.last_email_check (UTC). when=None → now. Raises if candidate missing."""
   ```

   Concrete behavior:
   - Strip `candidate_id`; raise `ValueError` if blank.
   - `stamp = when if (when or "").strip() else _utc_now()` (or equivalent existing UTC helper).
   - `_ensure_candidate_schema`; `UPDATE candidate SET last_email_check = ?, updated_at = ? WHERE astral_candidate_id = ?`.
   - If `rowcount == 0`, raise `LookupError` (candidate missing).
   - No logging in data layer.

   ⚠️ **Decision — dedicated stamp helper, not `save_candidate` kwarg:** Runner (AST-1136) needs a one-field write that does not merge `candidate_data`. Matches `update_company_search_term_last_scan_at`-style cadence stamps.

4. In `save_dispatch_task`, **remove** the gaze_email-only null-`candidate_id` allowance:

   ```python
   # DELETE this branch:
   if tk == GAZE_EMAIL_CONFIG["task_key"] and not cid_raw:
       cid_val = None
   ```

   Blank/None `candidate_id` must always raise `ValueError("candidate_id is required")` before INSERT. Update the docstring to drop “NULL only for GAZE_EMAIL_CONFIG”.

5. Leave `dispatch_task.candidate_id` schema nullable and leave `idx_dispatch_task_null_candidate_task_key` in place for this ticket — Stage 3 deletes any residual null shell rows; a full NOT NULL rebuild is not required by AC and is out of scope.

6. Do **not** call `update_candidate_last_email_check` from the runner or `_dispatch_one` here (AST-1136). Do **not** change `_gaze_email_available_count` / live inbox counting (AST-1135).

**Done when (recheck):** Fresh + migrated DBs expose `last_email_check`; stamp helper updates one row; `save_dispatch_task(candidate_id=None, task_key="gaze_email", …)` raises `ValueError`.

## Stage 3: Coverage-join provision + retire null shell + honest ledger cid

**Done when:** Scheduler startup deletes any null-`candidate_id` `gaze_email` row(s), then idempotently ensures one `gaze_email` dispatch row per every row in `candidate` (config seed sizes / `auto_mode` CLICK); `_dispatch_one` ledger writes the row’s `candidate_id` (no empty placeholder).

1. Replace `ensure_gaze_email_dispatch_task` in `src/core/dispatcher.py` with a per-candidate ensure:

   ```python
   def ensure_gaze_email_dispatch_task(candidate_id: str) -> Dict[str, Any]:
       """Idempotent insert of candidate-bound gaze_email dispatch_task (AST-1134)."""
   ```

   Concrete steps:
   - `cid = str(candidate_id or "").strip()`; if blank → raise `ValueError("candidate_id is required")`.
   - `tk = str(GAZE_EMAIL_CONFIG["task_key"]).strip()`.
   - If `tk not in TASK_CONFIG`: return `{candidate_id, task_key, added:0, skipped:0, skipped_missing_config:1, id:None}`.
   - Scan `database.list_dispatch_tasks_for_candidate(cid)` for a row with `task_key == tk` (trigger_state null/empty pair is fine — at most one gaze_email per candidate under current unique key).
   - If found: return `{candidate_id: cid, task_key: tk, added:0, skipped:1, skipped_missing_config:0, id: row["id"]}`.
   - If missing: `database.save_dispatch_task(candidate_id=cid, task_key=tk, min_count=int(GAZE_EMAIL_CONFIG["min_count"]), auto_mode=bool(GAZE_EMAIL_CONFIG["auto_mode"]), entity_type=GAZE_EMAIL_CONFIG["entity_type"], trigger_state=GAZE_EMAIL_CONFIG["trigger_state"], batch_size=GAZE_EMAIL_CONFIG["batch_size"], freq_hrs=float(GAZE_EMAIL_CONFIG["freq_hrs"] or 0))` → return `added:1` + new id.
   - Do **not** reconcile AUTO→CLICK on already-present rows beyond what seed already stores (new inserts use config `auto_mode`; leave existing row `auto_mode` alone unless it is the retired null shell deleted below).

2. Replace `provision_gaze_email_dispatch_task` with plural coverage provision:

   ```python
   def provision_gaze_email_dispatch_tasks() -> Dict[str, Any]:
       """Retire null gaze_email shell; ensure gaze_email for every candidate (AST-1134)."""
   ```

   Concrete steps:
   - `tk = GAZE_EMAIL_CONFIG["task_key"]`.
   - **Retire null shell:** for each row in `database.list_dispatch_tasks()` where `task_key == tk` and (`candidate_id` is None or blank after strip), call `database.delete_dispatch_task(int(row["id"]))`. Count deletions as `retired_null`.
   - **Coverage join:** `candidates = database.list_candidates()` (or equivalent select of every `astral_candidate_id` from `candidate` — must be every row, **not** `list_candidate_ids_with_dispatch_tasks()`).
   - For each candidate id, call `ensure_gaze_email_dispatch_task(cid)` and sum `added` / `skipped` / `skipped_missing_config`; track `candidates_touched`.
   - Return `{task_key, retired_null, candidates_touched, added, skipped, skipped_missing_config}`.

   ⚠️ **Decision — every `candidate` row, not “candidates that already have dispatch rows”:** Statute `astral.seed.other-via-coverage-join` and parent AC require coverage = extant `candidate` table. Meteorite’s `list_candidate_ids_with_dispatch_tasks` under-seeds and is the wrong pattern here.

3. In `start_scheduler`, call `provision_gaze_email_dispatch_tasks()` (plural). Update the info log to include `retired_null` + `candidates_touched` + `added` / `skipped` / `skipped_missing_config`. Keep try/except so provision failure does not crash scheduler startup.

4. In `_dispatch_one`, for the `gaze_email` branch:
   - Set `ledger_cid = (candidate_id or "").strip()` from the task row (the existing `candidate_id = task["candidate_id"]` local).
   - If `ledger_cid` is empty: treat as failure before runner (log + mark ledger failed / return — do not call `run_gaze_email` with an unbound row). Primary design no longer allows null-candidate gaze_email.
   - Pass `ledger_cid` into `save_dispatch_ledger` (replace `GAZE_EMAIL_CONFIG["dispatch_ledger_candidate_id"]`).
   - Do **not** redesign `run_gaze_email` message filtering, unbound Trash, or `last_email_check` stamping (AST-1136). Do **not** change `_gaze_email_available_count` to bind-filtered inbox counts (AST-1135). Leaving the existing task-key due/avail special-case in `get_due_tasks` / `count_eligible_for_dispatch_task` is intentional so candidate-bound rows still have a due signal until AST-1135 lands.

5. Do **not** add `gaze_email` to `METEORITE_DISPATCH_TASKS` or wire template-only coverage. Template candidate is covered because it is a `candidate` row.

**Done when (recheck):** After provision, zero null-`candidate_id` `gaze_email` rows; every `list_candidates()` id has exactly one `gaze_email` row; Click-run ledger for that row uses that candidate id.

## Self-Assessment

**Scope:** `Single-Component` — utils config + data schema/save gate + dispatcher provision/ledger for one task key; no runner rewrite and no Avail API redesign.

**Conf:** `high` — replaces a known null-shell provision with the coverage-join pattern already used for candidate-scoped catalogs; carve-out retirement is emptying an existing config tuple.

**Risk:** `Medium` — wrong coverage loop or leftover null shell would break Scheduled Actions / dispatch UAT for every candidate; ledger cid mistake would orphan batch history. Mitigated by explicit retire-then-ensure steps and by leaving Avail/runner to siblings.

## Rules check (plan vs ASTRAL_CODE_RULES)

- §1.3 DRY — reuse `list_candidates` / `save_dispatch_task` / existing admin-defaults special-case; no parallel provision framework.
- §2.1 config — task key, retention days, seed sizes stay in `GAZE_EMAIL_CONFIG`; secrets stay environ.
- §2.4 batch — no new claim/get/clear; mailbox still non-claim until AST-1135/1136.
- §2.6 state machine — no job/candidate state transitions on this ticket.
- §3.3 imports — dispatcher already imports config + database; no new upward imports.
- §3.5 naming — `provision_gaze_email_dispatch_tasks` (plural) matches meteorite provision naming.
- Statute `astral.seed.other-via-coverage-join` — coverage from every `candidate` row.
- Statute `astral.standards.in-scope-only` — no React / runner / live Avail / Manage Email (AST-1129).

## Review

**Publish ref:** `origin/sub/AST-1128/AST-1134-retire-null-shell-candidate-bound-config`
**Tip:** `89a305cb464aaf66c1f62add928ae143c36efe92`
**Overall:** DISCUSS

[code-rubric] revision=1 — Radia full-set sweep vs `origin/dev...origin/sub/AST-1128/AST-1134-retire-null-shell-candidate-bound-config`.

### What's solid

- Stages 1–3 landed on planned surfaces: candidate-bound `GAZE_EMAIL_CONFIG`, empty always-visible tuple, `last_email_check` + stamp helper, `save_dispatch_task` requires bound cid, coverage-join provision via `list_candidates()`, null shell retired, ledger uses row `candidate_id`.
- Sibling boundaries held (no runner / live Avail / React).
- Engineer `code()` commits are src-only; Betty owns tests/bible via `test()` + `merge-tests`.

### Issues

**discuss:** Stage 3 asked unbound `gaze_email` to "log + mark ledger failed / return"; `_dispatch_one` logs and returns without a FAILED ledger write. Residual path after null-shell retire — confirm whether silent skip is enough once bound cid is mandatory.

**discuss (straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` at plan time; post-Betty diff brings them in-scope. All three score **conforms** (plan doc not a spike; single features file; engineer did not edit test tree).

### Recommended actions

- Ada: confirm unbound early-return is intentional (no FAILED ledger without cid), or add a bounded failure stamp if resolve wants plan literalism.
- No fix-now product edits from this review.

## Resolution

**Date:** 2026-08-02  
**Review tip:** `a5c23ed0` · **Overall:** DISCUSS (no fix-now)

**discuss — unbound `_dispatch_one` early-return (no FAILED ledger):** Confirmed intentional. After null-shell retire, a blank `candidate_id` is a residual/corrupt row, not a supported path. Stamping FAILED with an empty ledger cid would reintroduce the retired null-shell ledger placeholder. Behavior matches the existing no-candidate/API-key skip (log + return, no ledger) and Betty’s `TestAst1090GazeEmailDispatchOne::test_skips_unbound_candidate_id` (`save_ledger` not called). No product change.

**discuss (straggler):** Noted — no action; all three statutes conform on tip.

**fix-now:** none.
