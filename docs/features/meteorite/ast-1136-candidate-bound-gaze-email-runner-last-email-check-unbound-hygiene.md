# AST-1136 — Candidate-bound gaze_email runner + last_email_check + unbound hygiene

**Linear:** [AST-1136](https://linear.app/astralcareermatch/issue/AST-1136/candidate-bound-gaze-email-runner-last-email-check-unbound-hygiene)
**Parent:** [AST-1128](https://linear.app/astralcareermatch/issue/AST-1128/gaze-email-candidate-bound-dispatch-redesign) — gaze_email — candidate-bound dispatch (redesign)
**Publish ref:** `origin/sub/AST-1128/AST-1136-candidate-bound-gaze-email-runner`

After AST-1134 (candidate-bound rows + `update_candidate_last_email_check`) and AST-1135 (live bind-filtered Avail / AUTO due), redesign the AST-1090 null-shell runner so a `gaze_email` run for candidate A processes only inbox messages whose From binds to A, reuses Ruth/scrape/dedupe/create/archive outcomes for those messages, stamps `candidate.last_email_check` (including zero-match runs), and applies unbound leave-then-Trash after `unbound_retention_days` as shared mailbox hygiene without restoring a null-candidate Avail shell. Style D when `debug=True`. Leaves a callable core ingest path AST-1129 can reuse for selected messages. Does **not** own provision/Avail/Manage Email UI.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/gaze_email.py` | Candidate filter; unbound hygiene under bound run; stamp `last_email_check`; extract callable ingest; Style D run header | core |
| `src/utils/config.py` | Comment-only: runner is candidate-bound (AST-1136); no key/value changes | utils |

No `tests/` / bible / React / dispatcher provision/Avail / Manage Email (AST-1129) / Gmail external API changes. `_dispatch_one` already passes the bound task row into `run_gaze_email` — do **not** edit `src/core/dispatcher.py` unless a literal compile break appears (escalate; do not invent dispatcher scope).

## Stage 1: Candidate filter + callable bound ingest

**Done when:** `run_gaze_email(task)` requires a non-blank `task["candidate_id"]` and only runs bound ingest for messages whose `candidate_match` binds to that id; messages bound only to other candidates are left untouched; a public `process_gaze_email_messages` performs the same bound ingest outcomes on a caller-supplied message list (AST-1129 reuse); unbound leave/Trash still runs inside `run_gaze_email` over the full inbox list.

1. In `src/core/gaze_email.py`, rewrite the module docstring from “null-candidate dispatch row” to candidate-bound runner (AST-1136 / parent AST-1128): list Astral inbox → filter From→selected candidate → unbound age→Trash (shared hygiene) → bound shape route → Ruth/scrape/dedupe/create → archive; stamp `last_email_check`; Style D when `debug=True`; no qualify/GDL.

2. Import `update_candidate_last_email_check` from `src.data.database` alongside the existing `job_link_exists_for_candidate` import (core→data allowed). Do **not** import dispatcher or UI.

3. Add a public async helper **above** `run_gaze_email` (keep existing private helpers where they are — do not reshuffle the whole file for public-first churn):

   ```python
   async def process_gaze_email_messages(
       candidate_id: str,
       messages: list[dict],
       *,
       debug: bool = False,
   ) -> dict[str, int]:
       """Bound-ingest only for messages whose From binds to candidate_id.

       Same Ruth/scrape/dedupe/create/archive outcomes as the dispatch runner.
       Does not list Gmail, does not Trash unbound mail, does not stamp
       last_email_check. AST-1129 Land Meteorite calls this with selected rows.
       """
   ```

   Concrete behavior:
   - `cid = str(candidate_id or "").strip()`; if blank → raise `ValueError("candidate_id is required")`.
   - If `debug`: `logger.set_debug_flag(True)`.
   - `n = len(messages)`; init `processed = passed = failed = errors = 0`.
   - For `i, msg in enumerate(messages, start=1)`:
     - `mid = msg.get("id") or ""`
     - Style D `found` header + `from_address` detail (same helpers `_dbg` / `_detail` as today).
     - `match = msg.get("candidate_match") or {}`
     - If not `match.get("matched")`: `_dbg(..., outcome="skipped-unbound")` + detail that this path does not mutate unbound mail; `processed += 1`; `passed += 1`; continue. (Land Meteorite must not Trash via this helper.)
     - `bound_cid = str(match.get("astral_candidate_id") or "").strip()`
     - If `bound_cid != cid`: `_dbg(..., outcome="skipped-other-candidate")`; `processed += 1`; `passed += 1`; continue. (No archive/trash/create.)
     - Else: `p, pa, fa, er = await _handle_bound(msg, match, debug=debug, index=i, total=n)` and accumulate.
     - Outer `except`: same as today’s per-message error path (errors++, processed++, Style D `error` + truncated detail).
   - Return `{"total_processed", "total_passed", "total_failed", "total_errors"}` (same keys as today).

   ⚠️ **Decision — message dicts, not raw ids:** Manage Email already holds list/get payloads with `candidate_match`. Requiring ids-only would force a second list/get shape inside core. AST-1129 filters selected rows then calls this; dispatch runner builds the list via `list_inbox_messages`.

4. Rewrite `run_gaze_email(task, *, debug=False)`:

   ```python
   async def run_gaze_email(task: dict, *, debug: bool = False) -> dict[str, int]:
       """AST-1136: candidate-bound mailbox run + unbound hygiene + last_email_check stamp."""
   ```

   Concrete behavior:
   - `cid = str((task or {}).get("candidate_id") or "").strip()`; if blank → raise `ValueError("candidate_id is required")` (dispatcher already skips unbound rows; this hard-fails misuse).
   - If `debug`: `logger.set_debug_flag(True)` and emit one Style D run header:
     - `func=GAZE_EMAIL_CONFIG["debug_func"]` (keep config value `gaze_email.run`)
     - `index=1`, `total=1`, `identifier=cid[:80]`, `outcome="run-start"`
     - detail: `account_address` expectation vs `GMAIL_USER` casefold mismatch warning (keep today’s mismatch detail; do not read secrets from config).
   - `messages = list_inbox_messages(debug=debug)`; `n = len(messages)`; `now_ms = int(time.time() * 1000)`.
   - Init summary counters to 0.
   - For each message with Style D `found` + from detail:
     - **Unbound** (`not match.get("matched")`): if `_unbound_is_stale(internal_date_ms, now_ms=now_ms)` → `trash_message(mid)` + outcome `trashed`; else outcome `ignored-unbound`. `processed += 1`; `passed += 1`. Do **not** call `_handle_bound`.
     - **Bound to other** (`bound_cid != cid`): outcome `skipped-other-candidate`; leave inbox untouched; `processed += 1`; `passed += 1`.
     - **Bound to selected** (`bound_cid == cid`): call `_handle_bound` and accumulate (unchanged Ruth/scrape/dedupe/create/archive behavior; still uses **that** candidate’s API key via `get_candidate(cid)` inside `_handle_bound`).
     - Per-message `except`: same as today.
   - Do **not** call `process_gaze_email_messages` from inside the unbound/other branches — keep one clear loop in `run_gaze_email` so hygiene and filter stay visible. Optionally factor only the bound branch through a tiny private call into `_handle_bound` (already exists). `process_gaze_email_messages` is the external reuse surface; DRY with it is optional if it forces awkward double-indexing — prefer a clear loop over forced DRY.

   ⚠️ **Decision — one inbox loop in `run_gaze_email`, separate public ingest for AST-1129:** Forcing hygiene + stamp through `process_gaze_email_messages` would either Trash unbound on Land Meteorite calls or need flag soup. Duplicate Style D headers between the two publics is acceptable; bound outcome logic stays in `_handle_bound` (single pipeline).

5. Leave `_handle_bound`, `_ruth_parse`, `_ingest_link`, `_finalize_archive`, and shape routing **behaviorally unchanged** (still lands **METEORITE_NEW** only; no qualify/GDL; per-candidate `job_link_exists_for_candidate` only). Do **not** call global AST-1061 skip helpers.

6. Do **not** restore null-candidate ledger placeholders or edit Avail/provision code.

**Done when (recheck):** With inbox messages binding to A, B, and unbound: a run for A ingests only A’s bound mail, leaves B’s messages in inbox, trashes only stale unbound, leaves fresh unbound; `process_gaze_email_messages("A", selected)` never trashes unbound.

## Stage 2: Stamp `last_email_check` + debug/config honesty

**Done when:** Every completed `run_gaze_email` for candidate A stamps `candidate.last_email_check` (including zero bound matches); stamp failures surface as runner errors without swallowing; `debug=False` emits no new Style D lines; config comment names AST-1136 as runner owner.

1. At the end of `run_gaze_email`, **after** the message loop and **before** the summary return, call:

   ```python
   update_candidate_last_email_check(cid)
   ```

   Concrete rules:
   - Stamp even when zero messages bound to `cid` and even when the inbox was empty.
   - Stamp after per-message errors that were handled inside the loop (run still completed).
   - If `list_inbox_messages` raises before the loop: do **not** stamp (run did not complete) — let the exception propagate to `_dispatch_one`.
   - If `update_candidate_last_email_check` raises (`ValueError` / `LookupError` / DB): do **not** swallow; let it propagate (ledger FAILED path already exists).
   - Do **not** stamp from `process_gaze_email_messages` (Land Meteorite is not a mailbox check cadence).

   ⚠️ **Decision — stamp only on `run_gaze_email` completion:** Parent AC3 is about the dispatch `gaze_email` run for that candidate. Selected-message Land Meteorite must not pretend the whole mailbox was checked.

2. When `debug=True`, after the stamp succeeds, emit a Style D run footer header:
   - same `func`, `index=1`, `total=1`, `identifier=cid[:80]`, `outcome="run-complete"`
   - detail lines: `last_email_check=stamped` and `summary={total_processed, total_passed, total_failed, total_errors}` (aggregate allowed; must not replace per-message headers).

3. When `debug=False`: no `debug_index` / `debug_detail` from this module (existing `_dbg` / `_detail` gates stay).

4. In `src/utils/config.py`, update the `GAZE_EMAIL_CONFIG` block comment: replace “Runner literals feed AST-1136” deferral with “Runner is candidate-bound (AST-1136): filter From→row candidate_id, stamp last_email_check, unbound Trash hygiene via unbound_retention_days”. Do **not** change any key values, asserts, secrets, or `unbound_retention_days`.

5. Do **not** move Gmail OAuth / `GMAIL_USER` into config. Do **not** edit React or Manage Email.

**Done when (recheck):** After a click-run for A with zero bound messages, `get_candidate(A)["last_email_check"]` is non-null; stale unbound was trashed if present; `debug=False` produces no new debug-contract lines from `gaze_email.py`.

## Self-Assessment

**Scope:** `Single-Component` — core runner redesign in `gaze_email.py` plus a config comment; no Avail/provision/UI surfaces.

**Conf:** `high` — AST-1090 already owns bind/route/Ruth/archive/trash; AST-1134 shipped the stamp helper; this ticket filters by row `candidate_id`, stamps, and extracts the bound ingest entrypoint.

**Risk:** `Medium` — wrong filter would ingest another candidate’s mail or skip real work; wrong hygiene placement could Trash on Land Meteorite or leave stale unbound forever; missed stamp breaks AC3. Mitigated by explicit three-way branch (unbound / other / selected) and stamp-only on `run_gaze_email`.

## Rules check (plan vs ASTRAL_CODE_RULES)

- §1.3 DRY — bound outcomes stay in `_handle_bound`; public AST-1129 path shares that helper; dispatch loop stays explicit for hygiene/stamp.
- §2.1 config — retention days / debug_func / subject schemes remain in `GAZE_EMAIL_CONFIG`; secrets stay environ.
- §2.4 batch — mailbox remains non-claim; no new claim/get/clear.
- §2.6 state machine — still lands **METEORITE_NEW** only; no daisy-chain into qualify/GDL (`astral.state.no-daisy-chain-in-run`).
- §3.3 imports — core→data for stamp + dedupe; Gmail archive/trash stay external; no UI imports.
- §3.5 naming — `process_gaze_email_messages` / `run_gaze_email` / existing `_handle_bound`.
- §1.5.1 debug — Style D only when `debug=True`; run header + per-message headers + run footer.
- Statute `astral.layers.core-vs-external-bright-line` — Gmail I/O external; filter/hygiene/orchestration core.
- Statute `astral.standards.in-scope-only` — no Avail (1135), no provision (1134), no Manage Email UI (1129), no tests tree.

## Review

**Publish ref:** `origin/sub/AST-1128/AST-1136-candidate-bound-gaze-email-runner`
**Tip:** `d4069a010d958fabc65cacfa4639d137b2913992`
**Overall:** DISCUSS

[code-rubric] revision=1 — Radia full-set sweep vs `origin/dev...origin/sub/AST-1128/AST-1136-candidate-bound-gaze-email-runner`.

### What's solid

- Stages 1–2 match plan: three-way unbound / other / selected filter, `process_gaze_email_messages` reuse path (no Trash/stamp), `run_gaze_email` stamps `last_email_check` after completed loop, Style D run+per-message+footer gated on `debug=True`.
- Bound ingest stays in `_handle_bound` (METEORITE_NEW only; no qualify/GDL). Secrets/retention stay config/environ-owned.
- Engineer `code()` is src-only; Betty owns tests/bible.

### Issues

**discuss (straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.standards.database-header-inventory`, `astral.ui.naming-conventions` at plan time; post-sibling/Betty three-dot brings them in-scope. All score **conforms**.

### Recommended actions

- No fix-now product edits from this review. Stragglers are bookkeeping only for resolve.

## Resolution

**Date:** 2026-08-02  
**Review tip:** `78b7cbb6` · **Overall:** DISCUSS (no fix-now)

**discuss (straggler):** Noted — no action; `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.patterns.require-auth-on-protected-endpoints`, `astral.standards.database-header-inventory`, and `astral.ui.naming-conventions` all conform on tip.

**fix-now:** none.
