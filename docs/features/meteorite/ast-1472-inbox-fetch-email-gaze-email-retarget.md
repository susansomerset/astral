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

# Radia review — AST-1472

**Rubric:** code-rubric.v1  
**Ticket:** AST-1472  
**Parent:** AST-1457  
**Publish ref:** `origin/sub/AST-1457/AST-1472-inbox-fetch-email-gaze-email-retarget` @ `43cba47384e7c0eaefa5bea3b180c7e8833f8e99`  
**Baseline:** `origin/dev`  
**Overall:** CLEAN

**Diff summary:** 37 files, +4755/−267 vs `origin/dev`. AST-1472 engineer surface: `src/core/inbox.py` (`run_fetch_email`, `_land_bound_inbox_message`, `land_inbox_message_ids`, create retarget), `src/core/dispatcher.py` (`ensure_fetch_email_dispatch_task` + `_dispatch_one`/`run_task` wire), `src/ui/api/api_inbox.py` (create + land-meteorite → inbox land). Publish ref carries AST-1469/1470/1471 foundation. Betty merge tip adds `TestAst1472*` + retargeted inbox/dispatcher/api tests.

**Engineer commits:** `d7b7b6b5` inbox · `8cfdbfbf` dispatcher · `683f8f85` api_inbox  
**Publish tip:** `43cba473` (merge-tests + Betty `5265ac48`)

**Susan amendment:** honored — no `gaze_email.py` created, `gazer.py` / `meteorite_email.py` untouched.

---

## Statutes checked

64 active statutes scored (retired `astral.config.pass-threshold-vs-score-floor` excluded).

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no agent paths in 1472 engineer diff |
| astral.agent.do-task-delegation | scoped | not-applicable | no do_task changes |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade paths |
| astral.batch.batch-id-first | scoped | not-applicable | fetch_email null-candidate shell — no entity batch claim |
| astral.batch.batch-id-format | scoped | conforms | dispatcher ledger `fetch_email-{uuid}` per run |
| astral.batch.claim-process-release | scoped | not-applicable | no entity claim queue on fetch_email shell |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no agent_data changes |
| astral.config.config-source-of-truth | scoped | conforms | reads `FETCH_EMAIL_CONFIG` / `METEORITE_CONFIG`; no config edits |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no new secrets |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no artifacts dir |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no debug/ spikes |
| astral.dispatch.seed-auto-false | scoped | conforms | `ensure_fetch_email_dispatch_task` inserts `auto_mode=False` |
| astral.dispatch.run-next-is-chain-authority | scoped | conforms | fetch_email runner only; no qualify chain |
| astral.docs.features-single-file-per-ticket | scoped | conforms | issue doc + Susan amendment recorded |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty tests/bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer limited to inbox/dispatcher/api_inbox |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult render |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | `@require_admin` on api_inbox routes unchanged |
| astral.layers.core-vs-external-bright-line | scoped | conforms | inbox→gmail external; land via core meteorite |
| astral.layers.import-direction | scoped | conforms | ui→core; inbox late-imports `land_meteorite`; gazer import removed |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts/ |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | HTTP status from `METEORITE_CONFIG` land keys |
| astral.patterns.coat-check-never-store-empty | scoped | not-applicable | duplicate idiom |
| astral.patterns.render-verdict-orchestrates-consult | scoped | not-applicable | no consult render |
| astral.patterns.require-auth-on-protected-endpoints | scoped | conforms | admin auth on inbox API |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed edits |
| astral.seed.archie-catalog-wins | scoped | conforms | `FETCH_EMAIL_CONFIG` literals from AST-1469 |
| astral.seed.boot-only-not-hot-path | scoped | conforms | ensure at scheduler start only |
| astral.seed.define-approved | scoped | not-applicable | no seed define |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no operator deletes |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage join |
| astral.standards.data-raises-caller-logs | scoped | conforms | dispatcher logs runner failures; no data edits |
| astral.standards.database-header-inventory | scoped | not-applicable | no database.py in 1472 engineer scope |
| astral.standards.debug-contract-gated | scoped | conforms | Style D gated on `debug=True` in inbox/dispatcher paths |
| astral.standards.dry-and-focused-functions | scoped | conforms | helpers scoped; fetch runner mirrors mailbox branch |
| astral.standards.in-scope-only | scoped | conforms | Susan-amended scope; no gazer/gaze_email/meteorite_email |
| astral.standards.logging-via-utils | scoped | conforms | get_logger throughout |
| astral.standards.names-not-ticket-ids | scoped | conforms | domain names (`run_fetch_email`, `land_inbox_message_ids`) |
| astral.standards.no-cross-contamination | scoped | conforms | inbox land path unified; legacy gazer ingest removed from inbox |
| astral.standards.no-hardcoded-sets | scoped | conforms | outcomes/skip keys from config catalogs |
| astral.standards.public-then-helpers | scoped | conforms | public runners; `_land_bound_inbox_message` private |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | utils not edited |
| astral.state.core-decides-transitions | scoped | conforms | land via `land_meteorite`; no inbox state writes |
| astral.state.job-prior-states-enforced | scoped | conforms | no shortcut state updates in adapters |
| astral.state.no-daisy-chain-in-run | scoped | conforms | fetch_email lands only; no qualify transition |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend |
| astral.ui.naming-conventions | scoped | not-applicable | no new UI files |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no worker config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | merge-tests tip at one SHA |
| orch.git.commit-vocabulary | universal | conforms | `code(AST-1472)` + `test(AST-1472)` |
| orch.git.flow-direction-inviolable | universal | conforms | sub vs dev |
| orch.git.ftr-sub-topology | universal | conforms | child sub publish ref |
| orch.git.merge-on-checkout | universal | conforms | n/a |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no cherry-pick/rebase |
| orch.git.no-dev-agent-branches | universal | conforms | proper sub ref |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1457 worktree |
| orch.git.three-permanent-branches | universal | conforms | diff vs origin/dev |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | Susan amendment binding in plan |
| orch.pipeline.plan-is-bible | universal | conforms | Stages 1–3 match amended plan |
| orch.pipeline.project-scoped-queues | universal | conforms | Meteorite ingress slice scoped |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Tests Passed → review-child |
| orch.roles.archie-approves-statutes | universal | conforms | n/a |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty landed fetch_email + admin tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Katherine |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Katherine at Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | engineer honored test-tree ban |

**Straggler (C4):** Joan APPROVED; no Excluded statute list.

---

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.layers.import-discipline | conforms | inbox→external Gmail; late-import `land_meteorite`; gazer import removed |
| pattern.batch.entity-claim-process-release | discuss | null-candidate fetch_email has ledger + counts but no entity claim — Joan accepted |
| pattern.config.config-block | conforms | `FETCH_EMAIL_CONFIG` / `METEORITE_CONFIG` / mailbox skip keys read from config |
| pattern.state.entity-state-transitions | conforms | transitions owned by `land_meteorite` downstream |

---

## Plan adherence

**Stage 1 — inbox:** `gazer` ingest import removed; `_land_bound_inbox_message` (strip → land); `run_fetch_email` (list → matched land, unbound skip-as-passed, four-count summary); `land_inbox_message_ids` (selected-ids with mailbox skip outcomes); `create_meteorite_job_from_inbox_message` retargeted to `land_meteorite` with land-backed return + `created`/`skipped` mirrors; Style D on touched paths.

**Stage 2 — dispatcher:** `ensure_fetch_email_dispatch_task` idempotent null-candidate CLICK shell; `start_scheduler` ensure + log; `_dispatch_one` fetch_email branch before API-key gate (ledger, summary accumulation, COMPLETED/FAILED/INTERRUPTED); `run_task` `available_count` via bound-inbox sum.

**Stage 3 — api_inbox:** `run_meteorite_email_selected_ids` dropped; create-job HTTP maps via `METEORITE_CONFIG` land keys; land-meteorite calls `land_inbox_message_ids`; `@require_admin` unchanged.

**Susan amendment:** no `gaze_email.py`, no `gazer.py` edits — verified in diff.

**Estimate 5:** fits post-amendment ingress slice.

**Related AST-1320 (Discussion):** plan explicitly retires gaze_email retarget; aligns with Susan amendment — no conflict with this implementation.

---

## Findings

### fix-now

(none)

### discuss

1. **`meteorite_email` poller vs CLICK `fetch_email`** — per-candidate `meteorite_email` AUTO runner unchanged; `fetch_email` null-candidate CLICK lands via `land_meteorite`. Joan accepted dual surfaces until a future retarget slice.

2. **`pattern.batch.entity-claim-process-release` partial apply** — fetch_email uses dispatch ledger + summary counts but no entity claim queue (`entity_type`/`trigger_state` None). Directionally fine per Joan.

### advisory

1. **`run_fetch_email` debug** — may emit two `debug_index` headers per unbound message (`found` then `skipped-unbound`). Noisy but gated on `debug=True`; not blocking.
2. **Nested debug when `debug=True`** — `_land_bound_inbox_message` + `land_meteorite` both emit Style D on matched paths; acceptable for operator traceability.
3. **Create-path behavior change** — removed `raise ValueError("no meteorite jobs created")`; land error rollup now returned as dict and mapped to HTTP 400 by API (plan-intentional).
4. **AST-1320 downstream** — if still open on gaze_email retarget, close or note N/A per Susan amendment so dispatch-parent Scope does not resurrect dead work.
5. **UAT** — exercise CLICK `fetch_email` on staging with bound inbox messages; AUTO `meteorite_email` behavior intentionally unchanged.

---

## What's solid

- Single land path for inbox create, admin land-meteorite, and fetch_email runner — no parallel gazer ingest in inbox.
- Dispatcher ensure honors `astral.dispatch.seed-auto-false` (`auto_mode=False`).
- Null-candidate fetch_email bypasses API-key gate correctly (before candidate gate).
- Admin create JSON adds `outcome`/`outcomes` with thin `created`/`skipped` mirrors for Manage Email compatibility.
- Betty coverage: `run_fetch_email` rollup, `land_inbox_message_ids` skips, `_land_bound_inbox_message` empty-strip guard, `ensure_fetch_email_dispatch_task`, retargeted AST-1049/1141 API tests.

---

## Frame diff

| Field | Issue doc (build stub) | Publish tip under review |
|-------|------------------------|--------------------------|
| Product SHA | `683f8f85` (Stage 3) | `43cba473` (merge-tests) |
| Tests | engineer ban | `TestAst1472RunFetchEmail`, `TestAst1472LandInboxMessageIds`, `TestAst1472EnsureFetchEmailDispatchTask`, retargeted AST-1049/1141 (`5265ac48`) |
| Foundation | AST-1469/1470/1471 on ftr | full meteorite stack in three-dot diff vs dev |

---

## Recommended actions (downstream — not Radia)

- Chuckles: append verdict, `docs(AST-1472): Radia review — clean`, push, post slim upshot, → Review Posted → User Testing.
- Parent UAT: CLICK `fetch_email` + admin create/land on staging inbox with bound candidates.
- AST-1320: resolve Discussion ticket as superseded by Susan amendment if still tracking gaze_email retarget.
- Future slice (out of scope): retarget `meteorite_email` poller to `land_meteorite` if dual-mailbox confusion surfaces in ops.

context_tokens≈52000

---

```
[code-rubric] PROCEED (Commit: 43cba473) fetch_email land retarget clean
```

## Bug: AST-1521 — meteorite_email land_meteorite routing

Parent mini-epic: [AST-1520](https://linear.app/astralcareermatch/issue/AST-1520/emailed-job-description-parsed-as-html) (orphaned fix lane). Completes the gap this ticket’s Scope gate explicitly deferred: **`src/core/meteorite_email.py` stays as-is** while inbox `fetch_email` / admin land already call `land_meteorite` (see Scope gate table + Joan discuss on dual mailbox surfaces above).

### As-is

Bound `meteorite_email` still forks inside `_handle_bound` on four Ruth-era shapes (`html_links` / `subject_url` / `subject_body` / ignore). A bound message with **no subject + JD text body** takes `html_links`: Ruth `do_task(meteorite_email)` first, then `_ingest_link` only for Ruth `jobs[]` rows that carry a `job_link`. When Ruth returns success with zero scrapeable links, outcomes stay empty → `_finalize_archive([])` returns **pass** (`ignored-empty`) **without** archiving — the reported failure. No path calls `land_meteorite`; scrape-short/fail in `_ingest_link` becomes `"skipped"` / `"error"` with **no** `BOT_BLOCKED` job; URL-subject+body still goes through Ruth.

### To-be

`_handle_bound` follows Susan’s decision tree (AST-1520 Description, preserved on the parent). JD-text ingress uses **`await land_meteorite(...)`** (same public API AST-1472 / AST-1470 established — late-import inside the mailbox module; do **not** fork enrich). Playwright scrape success → land with link + visible text (or append-scrape-to-body then land); scrape failure → create a meteorite job with `job_link` and transition to **`BOT_BLOCKED`** (no JD). Multi-link inspector paste → one land/BOT_BLOCKED per link. After successful land (or acceptable duplicate/supersede) **or** successful BOT_BLOCKED create → **archive** Gmail; on error → **leave inbox** and fail the run. Ruth / “heckaroony” runs **after** a job row exists (qualify), not inside `_handle_bound`. Unbound Trash / `last_email_check` stamp stay owned here (not `fetch_email`).

### Repro

1. Candidate has a bound From address and an active `meteorite_email` dispatch row.
2. Send (or fixture) an inbox message: **empty/missing subject**, body = plain JD text (no `http(s)` job links), From = that candidate.
3. Run `run_meteorite_email` for that candidate (AUTO/CLICK).
4. **Broken today:** Ruth `html_links` path runs; no job created; message remains in inbox; runner still counts the message as **passed** (`ignored-empty`).
5. **Expected after fix:** `land_meteorite(cid, text=<visible body>)` creates/dedupes a meteorite job; Gmail message is **archived**; runner **passed** only when land (or archive) succeeds — land error leaves inbox and fails.

Fixture shape (no DB seed — file/JSON persistence): a message dict as returned by `list_inbox_messages` / `get_message_html` with `subject=""`, non-empty `html_body` whose visible text is ≥ `METEORITE_EMAIL_INGEST_CONFIG["min_jd_chars"]` / qualify min, `candidate_match.matched` + matching `astral_candidate_id`.

### Root cause

AST-1472 retargeted inbox `fetch_email` + admin create/land to `land_meteorite` and **explicitly excluded** `meteorite_email.py`. The per-candidate mailbox runner still uses the pre-land Ruth-first shape table. That table’s no-subject branch assumes “HTML links to scrape,” so plain JD text never reaches a text-blob land ingress; empty ingest is treated as an intentional pass without archive.

### Proposed change

**Scope (binding — AST-1521 `## Scope`):** major edit `src/core/meteorite_email.py`; consume `land_meteorite` / `ensure_meteorite_company` from `src/core/meteorite.py` **read-only** (no meteorite.py edits); **do not** edit `inbox.py` / `gazer.py` (tree + archive differ from `_land_bound_inbox_message` strip→land — no shared-helper extraction this pass); optional literals only in `METEORITE_EMAIL_*_CONFIG` / existing `TASK_CONFIG["qualify_meteorite"]["bot_blocked_state"]`; Betty owns tests.

**Susan tree → `_handle_bound` (after existing candidate/API-key + `get_message_html` gates):**

Outer parent item “2. if no (but it is bound…)” is **not** a separate code path here — `run_meteorite_email` already filters to this candidate before `_handle_bound` (AST-1520 fork-logic answer). Implement the **subject / URL / body / inspector** branches only.

Keep intentional **ignore** (leave inbox, count pass) for: non-URL subject + empty body; subject empty + empty body.

1. **Helpers (same file)**  
   - Late-import `land_meteorite`, `ensure_meteorite_company` from `src.core.meteorite`; import `save_meteorite_job` + `transition_job_state` from `src.core.tracker` for the BOT_BLOCKED-only path.  
   - Drop `_handle_bound` use of `do_task` / `_ruth_parse` / `_ensure_html_links_jobs_complete` / `create_meteorite_job` for JD ingest (remove dead Ruth-first branches; delete unused helpers/imports in the same change if nothing else calls them).  
   - Reuse existing `_ruth_candidate_links` (or rename to a neutral `_body_http_links`) + `_meteorite_email_body_text` / `_meteorite_fetch_link_visible_text` for links + scrape.  
   - **`_land_outcome_token(land: dict) -> str`:** map `METEORITE_CONFIG` land keys → archive tokens: `created`→`created`; `duplicate_skip` / `superseded`→`skipped`; `error`→`error`.  
   - **`async def _land_jd(cid, *, text, job_link=None, debug) -> str`:** `await land_meteorite(cid, text=text, job_link=job_link, debug=debug)` → token via mapper. Empty text after strip → `error` (do not call land).  
   - **`async def _scrape_land_or_bot_blocked(cid, url, *, jd_suffix=None, debug) -> str`:** scrape via `_meteorite_fetch_link_visible_text`; if visible length ≥ `METEORITE_EMAIL_INGEST_CONFIG["min_jd_chars"]`, land with `text=(visible + optional suffix)` and `job_link=final_url or url`; if scrape empty/short/raises → **BOT_BLOCKED create** (below) and return `created` on success / `error` on failure. Dedupe: if `job_link_exists_for_candidate` (or land returns `duplicate_skip`) treat as `skipped` — do not create a second BOT_BLOCKED.  
   - **`_create_bot_blocked_job(cid, job_link, *, debug) -> str`:** `ensure_meteorite_company(cid)` → `save_meteorite_job(cid, company=short_name, job_link=link, job_data={})` (empty JD; create carve-out into `METEORITE_NEW`) → on `land_outcome_created`, `transition_job_state([astral_job_id], TASK_CONFIG["qualify_meteorite"]["bot_blocked_state"])` (`BOT_BLOCKED` priors already include `METEORITE_NEW` — AST-1195/1197). On `duplicate_skip` / `superseded` return `skipped` (no second transition). On save error → `error`. **Do not** change `meteorite.py` / `land_meteorite` for this — land has no BOT_BLOCKED API today.  
   - **`_body_looks_like_inspector_html(html) -> bool`:** config-driven structural-tag density (see config step). Used only on the **no-subject** branch.

2. **Config (optional — only if statute forces literals out of code)** in `METEORITE_EMAIL_INGEST_CONFIG` (or mailbox block if clearer): e.g. `inspector_structural_tags` (tuple of tag names) + `inspector_min_structural_tags` (int). Assert types/non-empty. No new job states. Reuse `min_jd_chars`, `subject_url_schemes`, `link_schemes` / allow+exclude substrings already present. Read `bot_blocked_state` from `TASK_CONFIG["qualify_meteorite"]` — do not hardcode `"BOT_BLOCKED"`.

3. **Rewrite `_handle_bound` branch table** (replace html_links / subject_url / subject_body):

| Condition | Action |
|-----------|--------|
| Subject is pure URL (`_subject_is_url`) **and** body non-empty | `_land_jd(cid, text=visible_body, job_link=subject)` — subject is `job_link`, body is JD (no scrape required). |
| Subject is pure URL **and** body empty | `_scrape_land_or_bot_blocked(cid, subject)`. |
| Subject non-empty, **not** URL, body non-empty, body has ≥1 http(s) link | Scrape **first** document-order link; on scrape ok → `_land_jd` with `text=f"{subject}\\n\\n{visible_body}\\n\\n{scraped}"` (append scraped visible text to email body; `job_link=that link`); on scrape fail → `_land_jd` with `text=f"{subject}\\n\\n{visible_body}"` (no link required). |
| Subject non-empty, **not** URL, body non-empty, **no** links | `_land_jd(cid, text=f"{subject}\\n\\n{visible_body}")`. |
| **No** subject, body non-empty, `_body_looks_like_inspector_html` **and** ≥1 link | For **each** link: `_scrape_land_or_bot_blocked(cid, link)` (one job per link). Collect outcome tokens. |
| **No** subject, body non-empty, inspector **but** no links | `_land_jd(cid, text=visible_body)`. |
| **No** subject, body non-empty, **not** inspector (reported JD-text case) | `_land_jd(cid, text=visible_body)`. |

After the branch, always `_finalize_archive(mid, outcomes, ...)` when the branch produced an outcomes list.

4. **`_finalize_archive`**  
   - **Change:** `if not outcomes:` → treat as **error** (leave inbox; `passed=0`, `errors=1`, outcome e.g. `error` / `ignored-empty` retired as a pass). No more pass-without-ingest after a land attempt.  
   - **Keep:** ≥1 `created` **or** all-`skipped` with zero `error` → `archive_message`; only-`error` → leave inbox.  
   - Map land `duplicate_skip` / `superseded` through the `skipped` token so acceptable dedupe still archives (same spirit as today’s AC5 all-skip archive).

5. **`run_meteorite_email` / `process_meteorite_email_messages` / `run_meteorite_email_selected_ids`**  
   - List/bind/filter/unbound Trash / `last_email_check` unchanged.  
   - Outcomes driven solely by new `_handle_bound` returns.  
   - Module docstring: bound path → Susan tree + `land_meteorite` / BOT_BLOCKED; Ruth not invoked pre-land.

6. **Explicit non-goals**  
   - No `inbox.py` shared helper. No `gazer.py` / `api_inbox.py` / `dispatcher.py` edits. No qualify/`do_task` from this runner. No new `JOB_STATES` keys.

### Blast radius

- **Same helper:** `run_meteorite_email_selected_ids` (admin Land Meteorite selected-ids) and `process_meteorite_email_messages` share `_handle_bound` — behavior flips with the runner.  
- **Dual mailbox:** `fetch_email` (AST-1472) already lands via `inbox._land_bound_inbox_message` without Gmail archive in that stage; this ticket owns archive on the **candidate-bound** AUTO path. Ops may still see both task keys until product consolidates.  
- **Tests:** existing Ruth `html_links` / `subject_body` / `_ingest_link` / `ignored-empty` expectations under `tests/component/core/` for meteorite_email will break — Betty owns replacements (no-subject JD → land + archive; URL+body; scrape-fail → BOT_BLOCKED; multi-link inspector). Do not edit `tests/` in make-fix.  
- **Ruth task `meteorite_email`:** no longer called from this runner; qualify / other callers of the agent task are untouched.  
- **`create_meteorite_job`:** removed from this module’s ingest path; other call sites unchanged.

### What must still hold

- Unbound retention Trash + bound-only ingest + `last_email_check` stamp ownership on `meteorite_email` (not moved into `fetch_email`).  
- `land_meteorite` remains the sole JD-text enrich→Tracker ingress (AST-1470/1472) — no parallel Ruth pre-parse for land.  
- Tracker meteorite dedupe / `duplicate_skip` / `superseded` semantics unchanged; acceptable dedupe still archives.  
- `BOT_BLOCKED` only via existing registry + `TASK_CONFIG["qualify_meteorite"]["bot_blocked_state"]`; priors already allow `METEORITE_NEW` → `BOT_BLOCKED`.  
- Style D only when `debug=True`; `debug=False` no new contract noise.  
- Layer rules: core orchestrates; Gmail archive/trash via `external.gmail`; Playwright via existing gazer fetch helper; no ui/data imports from this module beyond current database stamp/dedupe helpers.  
- AST-1472 inbox `fetch_email` / admin land paths remain as shipped — this bug does not regress them.
