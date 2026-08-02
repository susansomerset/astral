# AST-1140 — Selected-ids gaze_email ingest entrypoint

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1140/selected-ids-gaze-email-ingest-entrypoint-manage-email-select-inbox  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1129/manage-email-select-inbox-messages-and-land-meteorite  

**Publish ref (origin):** `sub/AST-1129/AST-1140-selected-ids-gaze-email-ingest-entrypoint`  
**Parent integration ref:** `ftr/AST-1129-manage-email-select-inbox-messages-and-land-meteorite`

Core Land Meteorite entrypoint: ingest an **explicit list** of Astral inbox message ids through the **same** bind / shape-route / Ruth parse / scrape / per-candidate dedupe / **METEORITE_NEW** create / archive-or-ignore path used by dispatcher `gaze_email` (AST-1090 helpers today; AST-1136 candidate-bound runner when rolled). Unbound / unmatched / missing-from-inbox selected ids are **skipped** with explicit per-id outcomes; bound siblings in the same batch still process. Does **not** stamp `candidate.last_email_check`. Does **not** call the retired Manage Email Create strip/extract path (`create_meteorite_job_from_inbox_message`). Style D when `debug=True`. Does **not** own admin HTTP (AST-1141) or Manage Email React (AST-1142).

**Depends on (soft merge gate at build):** AST-1128 child work that owns shared per-message ingest — especially AST-1136 (“leaves a callable core path AST-1129 can reuse”). Before Stage 2, `git fetch origin` and merge `origin/ftr/AST-1128-gaze-email-candidate-bound-dispatch-redesign` into this sub when that tip has advanced past the current null-shell runner; if AST-1136 already exported a public selected-ids / shared ingest symbol, **call that** instead of inventing a second pipeline. Do **not** wrap `run_gaze_email(task)` as a fake null-shell adapter.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `GAZE_EMAIL_CONFIG` with selected-ids Style D func name + skip/outcome string vocabulary | utils |
| `src/core/gaze_email.py` | Public `run_gaze_email_selected_ids`; share bound-message ingest with dispatcher path; Style D; no `last_email_check` stamp | core |

No `src/ui/**`, no React, no `src/core/inbox.py` Create path edits, no `src/core/dispatcher.py`, no `src/data/database.py` stamp calls, no `tests/` / bible.

---

## Stage 1: Config — selected-ids debug + outcome vocabulary

**Done when:** `GAZE_EMAIL_CONFIG` exposes the keys below; no runner behavior change yet.

1. In `src/utils/config.py`, extend the existing `GAZE_EMAIL_CONFIG` dict (do **not** invent a parallel Land-Meteorite config block) with:

```python
    # AST-1140 — Style D func= for selected-ids Land Meteorite ingest.
    "debug_func_selected": "gaze_email.selected_ids",
    # Per-id outcome strings returned to AST-1141 / recorded in Style D.
    "selected_outcome_skipped_unbound": "skipped-unbound",
    "selected_outcome_skipped_not_in_inbox": "skipped-not-in-inbox",
    "selected_outcome_skipped_unmatched": "skipped-unmatched",
```

Keep every existing key unchanged (`task_key`, `account_address`, `unbound_retention_days`, runner schemes, `debug_func`, etc.).

2. Asserts next to the existing `GAZE_EMAIL_CONFIG` asserts:

```python
assert GAZE_EMAIL_CONFIG["debug_func_selected"] == "gaze_email.selected_ids"
assert GAZE_EMAIL_CONFIG["selected_outcome_skipped_unbound"] == "skipped-unbound"
assert GAZE_EMAIL_CONFIG["selected_outcome_skipped_not_in_inbox"] == "skipped-not-in-inbox"
assert GAZE_EMAIL_CONFIG["selected_outcome_skipped_unmatched"] == "skipped-unmatched"
```

3. Update the inventory comment line for `GAZE_EMAIL_CONFIG` to mention selected-ids Land Meteorite literals (AST-1140).

⚠️ **Decision — extend `GAZE_EMAIL_CONFIG`, not a new block:** Parent Architectural definition forbids inventing parallel Land-Meteorite config for the same ingest behavior. Skip/outcome strings are product vocabulary for the admin batch payload (sibling AST-1141) and belong beside the task key.

**Done when (recheck):** `python3 -c "from src.utils.config import GAZE_EMAIL_CONFIG; assert GAZE_EMAIL_CONFIG['debug_func_selected']"` succeeds; `python3 -m py_compile src/utils/config.py` succeeds.

---

## Stage 2: Shared bound ingest + `run_gaze_email_selected_ids`

**Done when:** `from src.core.gaze_email import run_gaze_email_selected_ids` works; calling it with message ids processes **only** those ids through bind→route→Ruth/scrape/dedupe/create/archive; unbound/missing ids return explicit skip outcomes; `update_candidate_last_email_check` is never called; `create_meteorite_job_from_inbox_message` is never called; Style D emits only when `debug=True`.

### 2a. Pre-build merge / reuse gate (mandatory before editing the runner)

1. `git fetch origin`.
2. Merge `origin/ftr/AST-1128-gaze-email-candidate-bound-dispatch-redesign` into this sub (resolve conflicts; prefer AST-1128’s candidate-bound runner shape when both touch `gaze_email.py`).
3. Inspect `src/core/gaze_email.py` on the merged tip:
   - If a public selected-ids or shared per-message ingest already exists (names may vary — e.g. `run_gaze_email_selected_ids`, `ingest_gaze_email_message_ids`, `ingest_bound_inbox_message`), **reuse it**: ensure the public Land Meteorite name required by this plan exists (thin alias OK) with the return contract in 2c, and that `stamp_last_email_check` / last-check updates stay **off** for this entrypoint.
   - If only the AST-1090 null-shell `run_gaze_email` + `_handle_bound` exist, continue with 2b (extract/share — this is the callable AST-1129 needs; not an interim adapter around `run_gaze_email`).

⚠️ **Decision — no `run_gaze_email` wrapper:** Parent Boundaries forbid a throwaway adapter on the null-candidate shell. Selected-ids must drive per-message ingest directly (shared helpers), never “list whole inbox then pretend the dispatch row ran.”

### 2b. Share bound-message ingest (when AST-1136 has not already done so)

1. In `src/core/gaze_email.py`, keep `_handle_bound` (or rename to a clear shared helper if AST-1136 already did) as the single path that:
   - loads HTML via `get_message_html`
   - shape-routes (ignore / html_links / subject_url / subject_body)
   - Ruth parse with **bound candidate** API key
   - Playwright scrape + `job_link_exists_for_candidate` dedupe
   - `create_meteorite_job` → **METEORITE_NEW**
   - archive-or-leave via `_finalize_archive`
2. Ensure dispatcher `run_gaze_email` (null-shell or candidate-bound, whichever is on the tip after 2a) still calls that same helper for each in-scope message — do **not** duplicate the decision tree.
3. Do **not** move unbound Trash hygiene into the selected-ids entrypoint. Selected-ids only considers the explicit id list; it does **not** scan the rest of the mailbox for retention Trash.

### 2c. Public entrypoint

1. Add (module public section, above helpers — Code Rules §1.3 public-then-helpers) after any existing public `run_gaze_email`:

```python
async def run_gaze_email_selected_ids(
    message_ids: list[str],
    *,
    debug: bool = False,
) -> dict:
    """Land Meteorite: ingest only these Astral inbox message ids (AST-1140).

    Same bind/route/scrape/dedupe/create/archive outcomes as dispatcher gaze_email.
    Does not stamp candidate.last_email_check. Does not call Create strip/extract.
    """
```

2. Behavior (literal):

   - If `debug`: `logger.set_debug_flag(True)`.
   - Normalize ids: preserve caller order; for each raw id `strip()`; drop empties from processing but do **not** invent ids.
   - Build an index of current inbox once: `by_id = { (m.get("id") or ""): m for m in list_inbox_messages(debug=debug) }` (uses existing From→`candidate_match` enrichment from `src/core/inbox.py`).
   - Initialize `results: list[dict] = []` and aggregate counters `total_processed = total_passed = total_failed = total_errors = total_skipped = 0`.
   - Let `n = len(normalized_ids)`. For each `(i, mid)` in `enumerate(normalized_ids, start=1)`:
     1. Style D index header via `_dbg_selected` (below) with outcome `found` first when `debug` (same “found then recorded” pattern as AST-1090).
     2. If `mid` not in `by_id`: append result `{ "message_id": mid, "outcome": GAZE_EMAIL_CONFIG["selected_outcome_skipped_not_in_inbox"], "astral_candidate_id": None }`; `total_skipped += 1`; `total_processed += 1`; Style D recorded outcome = skipped-not-in-inbox; **continue**.
     3. `msg = by_id[mid]`; `match = msg.get("candidate_match") or {}`.
     4. If not `match.get("matched")` or not `(match.get("astral_candidate_id") or "").strip()`:
        - outcome = `selected_outcome_skipped_unbound` when `matched` is false; else `selected_outcome_skipped_unmatched`
        - append result with that outcome + `astral_candidate_id=None` (or the blank id); increment skip/processed; Style D; **continue** (do **not** Trash — retention hygiene is dispatcher/AST-1136, not Land Meteorite).
     5. Call shared `_handle_bound(msg, match, debug=debug, index=i, total=n)` (or AST-1136 equivalent).
     6. Map helper deltas to a single per-id `outcome` string for the result row:
        - prefer the last Style D / helper recorded outcome when available; otherwise: `error` if errors delta > 0; `failed` if failed delta > 0; else `archived` / `ignored` consistent with `_handle_bound` paths (create+archive → `archived`; ignore shapes → `ignored`).
        - append `{ "message_id": mid, "outcome": <str>, "astral_candidate_id": match["astral_candidate_id"] }`
        - add deltas into aggregates (`total_processed` / `passed` / `failed` / `errors` as today’s runner does).
   - **Forbidden in this function body:** any call to `create_meteorite_job_from_inbox_message`; any call to `update_candidate_last_email_check` (or raw SQL stamp of `last_email_check`); any call to `trash_message` for unbound retention; any call into qualify/GDL / dispatcher hop chaining; listing/processing message ids outside the selected list.
   - Return:

```python
    return {
        "results": results,
        "total_processed": total_processed,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "total_errors": total_errors,
        "total_skipped": total_skipped,
    }
```

3. Style D helpers (selected path only):

```python
def _dbg_selected(debug: bool, *, index: int, total: int, mid: str, outcome: str) -> None:
    if not debug:
        return
    logger.debug_index(
        func=GAZE_EMAIL_CONFIG["debug_func_selected"],
        index=index,
        total=total,
        identifier=(mid or "")[:80],
        outcome=outcome,
    )
```

Reuse existing `_detail` for working lines (`from_address=…`, `astral_candidate_id=…`, create/skip/archive detail). When `debug=False`, emit **no** new debug-contract lines from this path.

4. Module docstring: note AST-1140 selected-ids Land Meteorite entrypoint + “does not stamp `last_email_check`”.

⚠️ **Decision — list-once + index, not per-id Gmail list:** `list_inbox_messages` already carries `candidate_match`. One list call per Land Meteorite action avoids N list RPCs; ids absent from the current inbox become `skipped-not-in-inbox` (explicit feedback for AST-1141).

⚠️ **Decision — skip ≠ Trash on selected unbound:** Parent AC5 / Boundaries: unbound selected messages are skipped with feedback; retention Trash stays on the dispatcher/AST-1136 hygiene path so Land Meteorite does not mutate non-selected mailbox policy.

**Done when (recheck):** `python3 -m py_compile src/core/gaze_email.py src/utils/config.py` succeeds; `rg -n 'create_meteorite_job_from_inbox_message|update_candidate_last_email_check' src/core/gaze_email.py` shows **no** matches inside `run_gaze_email_selected_ids` (and no new imports of those symbols for this ticket).

---

## Stage 3: Import smoke + boundary lock

**Done when:** Import smoke passes; boundaries verified by search.

1. Run:

```bash
python3 -c "from src.core.gaze_email import run_gaze_email_selected_ids; import inspect; assert inspect.iscoroutinefunction(run_gaze_email_selected_ids)"
```

2. Confirm by ripgrep (must be empty hits for this ticket’s additions):

   - `run_gaze_email_selected_ids` body does not reference `create_meteorite_job_from_inbox_message`
   - `run_gaze_email_selected_ids` body does not reference `last_email_check` / `update_candidate_last_email_check`
   - No new files under `src/ui/` or `src/ui/frontend/` on this publish tip for AST-1140

3. No Linear status gymnastics beyond build-child’s normal stage comments — plan publish only moves to Plan Ready (§10).

---

## Self-Assessment

**Scope:** `Single-Component` — `GAZE_EMAIL_CONFIG` literals plus `src/core/gaze_email.py` public selected-ids entrypoint sharing the existing bound-message ingest helper; no UI/admin/dispatcher ownership.

**Conf:** `Medium` — AST-1090 `_handle_bound` path is known and reusable, but AST-1136 may still rewrite the candidate-bound runner on `ftr/AST-1128`; Stage 2a merge/reuse gate is mandatory so we do not fork ingest.

**Risk:** `Medium` — wrong wiring could land jobs via the retired Create path, stamp `last_email_check` on Land Meteorite, or process non-selected inbox mail; the plan forbids those call sites explicitly.

---

## Code Rules self-review

- §1.1 in-scope-only — no admin HTTP / React / dispatcher / Create retirement UI / qualify hop.
- §1.3 DRY / public-then-helpers — one shared bound ingest; public `run_gaze_email_selected_ids` first.
- §1.4 / §2.1 — outcome strings + debug func in `GAZE_EMAIL_CONFIG`; no parallel Land-Meteorite block.
- §1.5.1 Style D — `debug_func_selected` + `_dbg_selected` / `_detail` only when `debug=True`.
- §2.6 / `astral.state.no-daisy-chain-in-run` — stop at **METEORITE_NEW** via existing create helper; no qualify/GDL.
- §3.3 imports — core may use inbox / meteorite / gmail / config / logging as today; no UI imports.

---

## Review

| Field | Value |
|-------|-------|
| Branch | `sub/AST-1129/AST-1140-selected-ids-gaze-email-ingest-entrypoint` |
| Tip | _(filled at Code Complete)_ |
