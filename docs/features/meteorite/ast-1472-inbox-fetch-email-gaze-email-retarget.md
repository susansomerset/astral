# AST-1472 — Inbox fetch_email → land_meteorite

**Linear:** [AST-1472](https://linear.app/astralcareermatch/issue/AST-1472/inbox-fetch-email-gaze-email-retarget-meteorite-component)  
**Parent:** [AST-1457](https://linear.app/astralcareermatch/issue/AST-1457/meteorite-component) — Meteorite component  
**Publish ref:** `sub/AST-1457/AST-1472-inbox-fetch-email-gaze-email-retarget`

Inbox hosts `fetch_email`: list/bind/fetch/normalize → `land_meteorite` (AST-1470). Dispatcher ensures the null-candidate CLICK shell from AST-1469 `FETCH_EMAIL_CONFIG` / `SEED_CONFIG`. Admin inbox create-job and Land Meteorite selected-ids call inbox helpers that land — not `create_meteorite_job` / gazer ingest.

## Susan / Archie amendment (binding)

Ticket title and original Scope still name `gaze_email` / gazer email ingest retarget. **Susan (ticket Description + spawn):** there is **no** `gaze_email` functionality anymore — **do not resurrect it**; refer **only** to inbox `fetch_email`.

- **`src/core/gaze_email.py`:** does not exist on this tree — do **not** create it.
- **`src/core/gazer.py`:** do **not** edit (no email-ingest retarget in this ticket).
- Files Changed / Stages below **omit** those paths even though dispatch-parent Scope listed them.

## Scope gate

Ticket **## Scope** (dispatch partition) ∩ Susan amendment:

| In this plan | Out (Susan / sibling / not resurrected) |
|--------------|----------------------------------------|
| `src/core/inbox.py` (`fetch_email` → `land_meteorite`; retarget inbox create) | `src/core/gaze_email.py` — do not create |
| `src/core/dispatcher.py` (`fetch_email` ensure + runner wire) | `src/core/gazer.py` — do not edit |
| `src/ui/api/api_inbox.py` | `src/core/meteorite_email.py` — not in Scope; per-candidate mailbox poller stays as-is |
| `tests/component/core/test_inbox.py` — Betty owns test-tree | Contact/API listing (AST-1471); `land_meteorite` core (AST-1470); `config.py` (AST-1469 — `FETCH_EMAIL_CONFIG` already present) |

All Files Changed / Stages stay inside the **In this plan** set. **Depends on:** AST-1470 `land_meteorite` + AST-1469 `FETCH_EMAIL_CONFIG` / `TASK_CONFIG["fetch_email"]` / `SEED_CONFIG["dispatch_task-fetch-email"]` — present after sync with `origin/ftr/AST-1457-meteorite-component` (`--ftr AST-1457-meteorite-component`).

**AC partition:** Parent AC6 inbox half (`fetch_email` → `land_meteorite`); AC8 Land Meteorite / inbox create → `land_meteorite` (not `create_meteorite_job` HTML insert). Gaze_email half of AC8 → **N/A retired** (Susan). Contact half of AC6 → AST-1471.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/inbox.py` | `run_fetch_email`; selected-ids land helper; retarget `create_meteorite_job_from_inbox_message` to `land_meteorite`; drop gazer ingest import | core |
| `src/core/dispatcher.py` | `ensure_fetch_email_dispatch_task` + startup provision; `_dispatch_one` / `run_task` wire for `fetch_email` null-candidate CLICK shell | core |
| `src/ui/api/api_inbox.py` | Land Meteorite + create-job call inbox land helpers (no `run_meteorite_email_selected_ids` / no gazer create path) | ui |
| `tests/component/core/test_inbox.py` | Betty / qa-child | tests |

## Stage 1: Inbox — fetch_email runner + create/land helpers

**Done when:** `run_fetch_email` lists inbox, binds, fetches HTML, strip/extracts, `await land_meteorite` for each matched message, returns explicit rollup counts (never silent). Selected-ids helper lands the same way for admin. `create_meteorite_job_from_inbox_message` no longer imports or calls `ingest_meteorite_jobs_from_email_html_sync` / `create_meteorite_job`. `debug=True` Style D found→recorded on touched paths; `debug=False` no new contract noise. No Gmail archive/trash in this stage (land only).

1. Update `src/core/inbox.py` module docstring: hosts `fetch_email` → `land_meteorite`; create/land admin paths land; no gaze_email; Gmail I/O stays in `external.gmail` via existing list/get.

2. Imports: keep `external.gmail` list/get, bind/strip helpers, `METEORITE_CONFIG`, logging. **Remove** `from src.core.gazer import ingest_meteorite_jobs_from_email_html_sync`. Late-import `land_meteorite` inside land helpers (same cycle caution as Contact).

3. Add **`async def _land_bound_inbox_message(message_id: str, candidate_id: str, *, debug: bool = False) -> dict`**:
   - `get_message_html(message_id)` → subject + `html_body`.
   - `html = strip_extract_email_html(subject, raw_html)`; if empty after strip → return `{ "outcome": METEORITE_CONFIG["land_outcome_error"], "error": "stripped email HTML is empty", "outcomes": [] }` (do not call land).
   - `from src.core.meteorite import land_meteorite` then  
     `return await land_meteorite(candidate_id, text=html, debug=debug)`.
   - Style D (`debug=True` only): index headers under `func` from `FETCH_EMAIL_CONFIG["debug_func"]` or `"inbox.land_bound_message"` with outcome from land rollup; `|` detail: mid, cid, html_len. No new lines when `debug=False`.

4. Add **`async def run_fetch_email(task: Optional[dict] = None, *, debug: bool = False) -> dict`**:
   - Ignore claim/entity fields on `task` (null-candidate shell — no entity queue).
   - `messages = list_inbox_messages(debug=debug)`.
   - Accumulators: `total_processed`, `total_passed`, `total_failed`, `total_errors` (same keys dispatcher mailbox runners return).
   - For each message:
     - Unmatched / no cid → count as processed + passed (skip land; do **not** trash — unbound hygiene stays on `meteorite_email` path, out of Scope).
     - Matched → `await _land_bound_inbox_message(mid, cid, debug=debug)`.
       - Rollup `created` / `duplicate_skip` / `superseded` → `total_passed += 1`.
       - Rollup `error` → `total_failed += 1` (and `total_errors += 1` if land `error` present).
     - Always `total_processed += 1`.
   - Return the four-count summary dict. Never return without processing the list (empty inbox → zeros).

5. Add **`async def land_inbox_message_ids(message_ids: list[str], *, debug: bool = False) -> dict`** for admin Land Meteorite:
   - Normalize ids (strip empties; preserve order) like current selected-ids API.
   - `by_id` from `list_inbox_messages(debug=debug)`.
   - For each id: missing → skip result using existing `METEORITE_EMAIL_MAILBOX_CONFIG["selected_outcome_skipped_not_in_inbox"]`; unbound/unmatched → `selected_outcome_skipped_unbound` / `selected_outcome_skipped_unmatched` (read from config — **do not** edit `config.py`).
   - Matched → `_land_bound_inbox_message`; append `{ "message_id", "outcome": land["outcome"], "astral_candidate_id", "land": land }`.
   - Return `{ "results", "total_processed", "total_passed", "total_failed", "total_errors", "total_skipped" }` with the same counting spirit as today’s selected-ids helper (skipped rows increment `total_skipped` + `total_processed`).

6. **Retarget** `create_meteorite_job_from_inbox_message`:
   - Keep sync signature for API.
   - After bind + strip (same validation: matched candidate, non-empty HTML),  
     `land = asyncio.run(land_meteorite(cid, text=html, debug=debug))` (or call `_land_bound_inbox_message` via `asyncio.run`).
   - Return shape for API compatibility:

```python
{
    "astral_candidate_id": cid,
    "outcome": land.get("outcome"),
    "outcomes": land.get("outcomes") or [],
    "company": land.get("company"),
    "company_inserted": bool(land.get("company_inserted")),
    "error": land.get("error"),
    # Convenience mirrors for older Manage Email UI:
    "astral_job_id": (land.get("outcomes") or [{}])[0].get("astral_job_id") if land.get("outcomes") else None,
    "created": [o for o in (land.get("outcomes") or []) if o.get("outcome") == METEORITE_CONFIG["land_outcome_created"]],
    "skipped": [o for o in (land.get("outcomes") or []) if o.get("outcome") in (
        METEORITE_CONFIG["land_outcome_duplicate_skip"],
        METEORITE_CONFIG["land_outcome_superseded"],
    )],
    "mode": "land_meteorite",
    "state": None,
    "latest_score": None,
}
```

   - If land rollup is `error` and message is validation-like, still return the dict (API maps status); do **not** raise unless programmer misuse (`message_id` empty / unmatched) — keep existing `ValueError` for unmatched / empty mid / empty strip.

   ⚠️ **Decision:** Inbox create returns land-backed fields + thin `created`/`skipped` mirrors so Manage Email does not need a React ticket in this Scope. No `gazer` ingest.

7. Add `import asyncio` at module top if not present.

## Stage 2: Dispatcher — ensure + run `fetch_email`

**Done when:** Startup ensures one null-candidate `fetch_email` CLICK row from `FETCH_EMAIL_CONFIG` (idempotent). Admin/CLICK `run_task` on that row calls `inbox.run_fetch_email` without requiring a candidate API key. `auto_mode` stays false (`astral.dispatch.seed-auto-false`). No `gaze_email` row creation. No edits to `meteorite_email` provision beyond leaving the existing gaze_email purge as-is.

1. Import `FETCH_EMAIL_CONFIG` (and `TASK_CONFIG` if not already) in `src/core/dispatcher.py`.

2. Add **`ensure_fetch_email_dispatch_task() -> dict`**:
   - `tk = FETCH_EMAIL_CONFIG["task_key"]` (`"fetch_email"`).
   - If `tk not in TASK_CONFIG` → return skipped_missing_config.
   - Scan `database.list_dispatch_tasks()` for any row with `task_key == tk` and null/blank `candidate_id`. If found → skipped.
   - Else `database.save_dispatch_task(candidate_id=None, task_key=tk, min_count=…, auto_mode=False, entity_type=None, trigger_state=None, batch_size=…, freq_hrs=…)` using **`FETCH_EMAIL_CONFIG`** literals only.
   - Return `{ task_key, added, skipped, skipped_missing_config, id }` (same spirit as meteorite_email ensure).

3. In `start_scheduler`, after meteorite_email provision try/except, call `ensure_fetch_email_dispatch_task()` and log one info line (task_key + added/skipped). Do **not** remove `provision_meteorite_email_dispatch_tasks` (still owns per-candidate mailbox + gaze_email purge).

4. In `_dispatch_one`, **before** the meteorite_email mailbox branch and **before** candidate API-key gate, add:

```python
if (task_key or "").strip() == FETCH_EMAIL_CONFIG["task_key"]:
    from src.core.inbox import run_fetch_email
    # ledger with candidate_id="" or "fetch_email"; entity_type=None
    # asyncio await run_fetch_email(task, debug=debug)
    # map summary → accumulated; COMPLETED/FAILED/INTERRUPTED same as mailbox branch
    return
```

   ⚠️ **Decision:** Null-candidate is allowed only for `fetch_email`. Do not require `get_candidate` / API key. Ledger `candidate_id` may be empty string — match how other null shells are stored if a precedent exists; otherwise use `""` and document in the commit.

5. In `run_task`, when `task_key == FETCH_EMAIL_CONFIG["task_key"]`, set `available_count` via `len([m for m in list_inbox_messages(debug=False) if (m.get("candidate_match") or {}).get("matched")])` (or `count_inbox_bound_by_candidate` sum) — not `count_eligible_for_dispatch_task` (no entity/trigger). On list failure, `available_count = 0` and log warning.

## Stage 3: api_inbox — admin create + Land Meteorite → inbox land

**Done when:** `POST …/create-job` and `POST …/land-meteorite` call inbox land helpers only. No import of `run_meteorite_email_selected_ids`. `@require_admin` unchanged. Thin JSON only.

1. Update `src/ui/api/api_inbox.py` docstring: create-job and land-meteorite → inbox → `land_meteorite`.

2. Imports: drop `from src.core.meteorite_email import run_meteorite_email_selected_ids`. Import `land_inbox_message_ids` (and keep `create_meteorite_job_from_inbox_message`, list/get).

3. **`inbox_create_job_from_message`:** keep calling `create_meteorite_job_from_inbox_message`. Adapt JSON body to land-backed return from Stage 1:
   - Prefer top-level `outcome`, `outcomes`, `company`, `company_inserted`, `error`, `astral_candidate_id`.
   - Keep optional `created` / `skipped` mirrors if present.
   - HTTP: land `created` → **201**; `duplicate_skip` / `superseded` → **200**; `error` → **400** (or **404** only if error text starts with `candidate not found` — unlikely on this path). Map via `METEORITE_CONFIG` land keys (import from utils.config).

4. **`inbox_land_meteorite`:**  
   `result = asyncio.run(land_inbox_message_ids(message_ids, debug=debug))`  
   Return `jsonify(result), 200` (same status as today). Validation errors → 400; unexpected → 502.

5. Do **not** add React routes. Do **not** touch `api_meteorite.py` (AST-1471).

## Execution contract

- Stages in order; one commit per stage; publish to `origin/sub/AST-1457/AST-1472-inbox-fetch-email-gaze-email-retarget`.
- Do not add files outside Files Changed. Do not edit `tests/` (Betty). Do not create `gaze_email.py`. Do not edit `gazer.py` or `meteorite_email.py`.
- If `land_meteorite` / `FETCH_EMAIL_CONFIG` missing after sync — stop, comment on **parent AST-1457**.
- Ambiguity / drift → Stage blocked comment on parent.

## Estimate

Confirm Chuckles estimate: 5 — agree  
(Susan cut gaze/gazer surface; remaining fetch_email runner + dispatcher ensure + dual admin retarget still matches a 5-point ingress slice.)

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric.v1
**Ticket:** AST-1472
**Overall:** APPROVED
**Publish ref:** `sub/AST-1457/AST-1472-inbox-fetch-email-gaze-email-retarget` @ `8871ff580eb049239185cab3f6b37f0eba922338`

## Traceability
AC6 (inbox `fetch_email` → `land_meteorite`)→Stage 1 `run_fetch_email` + Stage 2 dispatcher ensure/wire; Contact half→N/A AST-1471. AC7 (Land Meteorite / create → `land_meteorite`, not HTML insert)→Stage 1 `create_meteorite_job_from_inbox_message` + `land_inbox_message_ids` retarget + Stage 3 `api_inbox` admin paths; gaze_email half→N/A retired per Susan amendment. Parent AC1 inbox / AC8 admin→this ticket; AC6 Contact / gaze_email→N/A. Stages 1–3→Scope gate “In this plan” set only (`inbox.py`, `dispatcher.py`, `api_inbox.py`).

## Findings

### acceptable — Susan amendment honored
**Location:** Susan / Archie amendment; Scope gate  
**Finding:** Plan explicitly forbids creating `gaze_email.py` or editing `gazer.py`; narrows dispatch-parent Scope to inbox `fetch_email` + admin retarget only. Aligns with ticket Description note and existing tree (`gaze_email.py` absent).  
**Recommendation:** None — proceed.

### discuss — `meteorite_email` poller left on legacy ingest (Scope boundary)
**Location:** Stage 2 step 3; Execution contract (“Do not edit `meteorite_email.py`”)  
**Finding:** Per-candidate `meteorite_email` dispatcher runner and `_handle_bound` ingest remain unchanged while `fetch_email` + admin paths land via `land_meteorite`. Susan retired gaze_email, not `meteorite_email`; dual mailbox tasks may coexist until a future slice retargets the poller.  
**Recommendation:** Accept for this ticket; note in qa-child that AUTO `meteorite_email` vs CLICK `fetch_email` are intentionally separate surfaces.

### discuss — `pattern.batch.entity-claim-process-release` partial apply
**Location:** Ticket ## Citations; Stage 1 `run_fetch_email`  
**Finding:** `fetch_email` is a null-candidate shell with no entity claim queue (`entity_type`/`trigger_state` None). Dispatch ledger + summary counts mirror mailbox runners; standard claim/process/release does not apply.  
**Recommendation:** Citation is directionally fine (dispatch orchestration family); no plan rewrite.

### discuss — Stage 2 `_dispatch_one` branch is template-shaped
**Location:** Stage 2 step 4  
**Finding:** Pseudocode comments delegate ledger/COMPLETED mapping to engineer; peer `meteorite_email` branch (lines 770–861) is the explicit template.  
**Recommendation:** Build should copy that branch structure for `fetch_email` before the API-key gate — already implied.

### discuss — Admin create-job JSON shape change
**Location:** Stage 1 step 6; Stage 3 step 3  
**Finding:** Land-backed return adds `outcome`/`outcomes` + thin `created`/`skipped` mirrors; Manage Email may read new fields. Plan documents HTTP mapping via `METEORITE_CONFIG` land keys.  
**Recommendation:** Betty manifest covers intake + outcome shape; engineer does not edit tests.

## R6 checklist (summary)
Susan-amended scope faithful; no config/meteorite/gazer/gaze_email edits; layer discipline (inbox→external Gmail, ui→core); `FETCH_EMAIL_CONFIG` seed-auto-false; late-import `land_meteorite`; Style D gated; dependencies on ftr (`land_meteorite`, `FETCH_EMAIL_CONFIG`, SEED stub) documented. Self-assessment (estimate 5, ingress slice post-amendment) honest.

context_tokens≈118000

[plan-rubric] PROCEED (Commit: 8871ff5) fetch_email land retarget

## Review

- Branch: `sub/AST-1457/AST-1472-inbox-fetch-email-gaze-email-retarget`
- Tip: `683f8f85565ebb577b0ddd16e45f1f4509aa11e4`
- Stages: `d7b7b6b5` inbox; `8cfdbfbf` dispatcher; `683f8f85` api_inbox

## Radia review


