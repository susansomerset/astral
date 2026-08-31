# AST-1560 — stage / scrape / land transitions

**Linear:** [AST-1560](https://linear.app/astralcareermatch/issue/AST-1560/stage-scrape-land-transitions)  
**Parent:** [AST-1555](https://linear.app/astralcareermatch/issue/AST-1555/meteorite-ingress-staging-table-inboxmeteorite-consolidation) — Meteorite ingress: staging table + inbox/meteorite consolidation  
**Publish ref:** `sub/AST-1555/AST-1560-stage-scrape-land-transitions`

After AST-1557 table spine: dispatcher-driven **single-transition** handlers on `meteorite` rows — NEW → SCRAPE_LINK or READY (stage), SCRAPE_LINK → Playwright → READY / BOT_BLOCKED / ERROR (scrape), READY → `METEORITE_NEW` job + `astral_job_id` → LANDED (land). Retires source-ref scrap synthesis and qualify enrich-in-front on the **table path**. Does not own `check_inbox`, monitoring, Estelle, or file delete.

## Scope gate

Ticket **## Scope** (verbatim):

`src/core/meteorite.py` (stage/scrape/land transitions; drop `_map_stage_jobs_to_scraps` synthesis; stop enrich-in-front on this path); `src/utils/config.py` + `data/admin/` + `src/core/dispatcher.py` for scrape/land task keys; `src/core/consult.py` only if cycle trim needed; Playwright via existing `src/external/playwright.py` (unchanged unless gap)

All Files Changed / Stages stay inside that set.

**Out of scope (siblings):**

- `meteorite` table + claim helpers — **AST-1557**
- Inbox verbs / Manage Email / bind retire — **AST-1558**
- `check_inbox` + monitoring log + mailbox repoint — **AST-1559**
- BOT_BLOCKED Estelle notify / `apply_paste` — **AST-1561**
- Retention runner + delete `meteorite_email.py` — **AST-1562**

**AC partition (this ticket):** Parent AC2 (scrape/land per-row claim boundary), AC3 (READY → job `METEORITE_NEW` + `astral_job_id` + LANDED), AC4 (no source-ref synthesis; empty `job_link` / `company_job_id` until qualify OK).

**Depends on:** **AST-1557** merged on the epic line — `METEORITE_STATES`, `claim_meteorite_batch` / `get_meteorite_batch` / `clear_meteorite_batch`, `update_meteorite`, `get_meteorite`. After `sync-child.sh`, if those symbols are missing on HEAD, **stop** and comment on AST-1560 (do not re-implement table layer here).

⚠️ **Decision — dispatch `stage_meteorite` vs Ruth `stage_meteorite`:** Ruth classify stays **inline** in `check_inbox` (AST-1559) via `do_task` / `TASK_CONFIG["stage_meteorite"]` — **no** dispatch row for classify. Parent names the **table transition** dispatch runners `stage_meteorite`, `scrape_meteorite`, `land_meteorite`. Those three keys are **custom dispatcher runners** (`entity_type` None), not consult hops. They must not invoke `consult.run_consult_task`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `METEORITE_INGRESS_DISPATCH_CONFIG` (task keys, trigger states, batch sizes, scrape page_status → row state map, debug_func literals) + header bullet + asserts; `SEED_CONFIG` paste rows for three dispatch tasks | utils |
| `data/admin/dispatch_task.json` | Seed rows for `stage_meteorite` / `scrape_meteorite` / `land_meteorite` transition runners (`auto_mode` false) | catalog |
| `src/core/dispatcher.py` | Route the three task keys to meteorite transition runners (mailbox-style custom branch, not `_run_unified`) | core |
| `src/core/meteorite.py` | `run_stage_meteorite` / `run_scrape_meteorite` / `run_land_meteorite` batch handlers + per-row helpers; remove `_map_stage_jobs_to_scraps`; strip blob `stage_meteorite` map→land enrich chain | core |
| `src/core/consult.py` | **Only if** import cycle remains after Stage 3 — trim late-import / move `is_meteorite_company` import (no new classify path) | core |

## Stage 1: Config + dispatch seeds + dispatcher registration

**Done when:** `METEORITE_INGRESS_DISPATCH_CONFIG` exposes task keys and `METEORITE_STATES` trigger literals; three idempotent `SEED_CONFIG` / admin dispatch rows exist; `dispatcher._dispatch_one` recognizes all three keys and delegates to meteorite runners (stub `{"total_processed": 0}` OK until Stage 2); `python3 -m py_compile src/utils/config.py src/core/dispatcher.py` succeeds.

1. In `src/utils/config.py` header inventory, add:

   - `METEORITE_INGRESS_DISPATCH_CONFIG` — table transition dispatch task keys + trigger states + scrape outcome map (AST-1560).

2. After `METEORITE_STATES` block (AST-1557 — must exist on branch before build), insert:

```python
# AST-1560: dispatcher-driven meteorite row transitions (not Ruth classify — that stays inline in check_inbox).
METEORITE_INGRESS_DISPATCH_CONFIG = {
    "stage_task_key": "stage_meteorite",
    "scrape_task_key": "scrape_meteorite",
    "land_task_key": "land_meteorite",
    # dispatch_task.trigger_state values = METEORITE_STATES keys claimed by each runner
    "stage_trigger_state": "NEW",
    "scrape_trigger_state": "SCRAPE_LINK",
    "land_trigger_state": "READY",
    "batch_size": 10,
    "debug_func_stage": "meteorite.run_stage_meteorite",
    "debug_func_scrape": "meteorite.run_scrape_meteorite",
    "debug_func_land": "meteorite.run_land_meteorite",
    # Playwright scrape contract → staging-row state (METEORITE_STATES keys only)
    "scrape_page_status_states": {
        "blocked": "BOT_BLOCKED",
        "ok": "READY",
        "closed": "ERROR",
        "missing": "ERROR",
    },
}
```

3. Asserts immediately after:

- All three task keys are non-empty distinct strings.
- All three trigger states ∈ `METEORITE_STATES`.
- `set(METEORITE_INGRESS_DISPATCH_CONFIG["scrape_page_status_states"].values())` ⊆ `{"READY", "BOT_BLOCKED", "ERROR"}`.
- `METEORITE_INGRESS_DISPATCH_CONFIG["stage_task_key"] == STAGE_METEORITE_CONFIG["task_key"]` — **same string** as Ruth catalog key; dispatch row uses custom runner, not `TASK_CONFIG` consult hop.

4. Add three `SEED_CONFIG` entries (`dispatch_task-stage-meteorite`, `dispatch_task-scrape-meteorite`, `dispatch_task-land-meteorite`) following existing `dispatch_task-fetch-email` shape:

   - `candidate_id` NULL (global pool — rows carry `candidate_id`; claim is cross-candidate like candidate batch).
   - `task_key` = each config key above.
   - `entity_type` NULL, `trigger_state` = matching trigger state literal.
   - `batch_size` from config, `auto_mode` 0, `freq_hrs` / `min_count` conservative defaults (match peer global tasks: e.g. `freq_hrs=0.1`, `min_count=1`).

5. Add matching rows to `data/admin/dispatch_task.json` (same literals as SEED_CONFIG — admin SSOT).

6. In `src/core/dispatcher.py`, add `_is_meteorite_ingress_transition_task_key(task_key) -> bool` comparing against the three config keys.

7. In `_dispatch_one`, **before** the mailbox `meteorite_email` branch, add a branch for ingress transition keys:

   - Mint `entity_batch_id = f"{task_key}-{uuid4()}"`, ledger with `entity_type=None`, `candidate_id` from row when present else NULL.
   - Late-import `from src.core.meteorite import run_stage_meteorite, run_scrape_meteorite, run_land_meteorite` (exact names from Stage 2).
   - Dispatch to the matching `run_*` with `(task, debug=debug)` signature mirroring `run_meteorite_email(task, debug)`.
   - Accumulate `total_processed` / `total_passed` / `total_failed` / `total_errors` from runner summary dict.

⚠️ **Decision:** Global dispatch rows (NULL `candidate_id`) — meteorite claim SQL is not scoped by dispatch row candidate; row's `candidate_id` column is authoritative at land time.

## Stage 2: Table transition handlers in `meteorite.py`

**Done when:** Each runner claims one batch, processes each row with **one** state write (plus field updates), clears batch in `finally`, and returns a summary dict; scrape uses `get_visible_text` only via existing `_land_fetch_link_text` / Playwright external; land uses `tracker.save_meteorite_job` **without** `enrich_meteorite_land_packet`; `python3 -m py_compile src/core/meteorite.py` succeeds.

### Shared batch pattern (all three runners)

1. Read `task_key`, `batch_size` from dispatch row; read trigger state from `METEORITE_INGRESS_DISPATCH_CONFIG` for this runner.
2. `batch_id = f"{task_key}-{uuid4()}"`; `claim_meteorite_batch(batch_id, trigger_state, limit=batch_size)`.
3. `rows = get_meteorite_batch(batch_id)`; if empty return zero summary.
4. `try:` loop rows; `finally: clear_meteorite_batch(batch_id)`.
5. Per-row failures increment `total_failed` / `total_errors` but **do not** abort sibling rows in the batch.

Import from `src.data.database`: `claim_meteorite_batch`, `get_meteorite_batch`, `clear_meteorite_batch`, `update_meteorite`. Import `METEORITE_INGRESS_DISPATCH_CONFIG`, `METEORITE_STATES`, `STAGE_METEORITE_CONFIG`, `METEORITE_CONFIG`, `TRACKER_CONFIG` from config.

### 2a. `async def run_stage_meteorite(task, *, debug=False) -> dict`

**One transition per row:** `NEW` → `SCRAPE_LINK` or `READY`.

For each claimed row:

1. Read `classify_outcome` (required non-empty string). If missing → `update_meteorite(id, state="ERROR", error="missing classify_outcome")`; count fail; continue.
2. If outcome ∈ `STAGE_METEORITE_CONFIG["skip_outcomes"]` → `update_meteorite(id, state="ERROR", error="skip outcome on row")` (should not happen if check_inbox fan-out correct); continue.
3. If outcome ∈ `STAGE_METEORITE_CONFIG["url_scrape_outcomes"]`:
   - Require `link` non-empty http(s) URL (from row `link` column).
   - `update_meteorite(id, state="SCRAPE_LINK", link=link)` — do **not** synthesize `source_ref` / `company_job_id`.
4. If outcome ∈ `STAGE_METEORITE_CONFIG["text_source_ref_outcomes"]` or other landable text path (`single_jd_no_link`, `multi_jd_inline` with content already on row):
   - Require `content` non-empty.
   - `update_meteorite(id, state="READY")`.
5. Else unhandled outcome → `update_meteorite(id, state="ERROR", error=f"unhandled classify_outcome: {outcome}")`.

⚠️ **Decision:** Stage runner does **not** call Ruth / `invoke_stage_meteorite` — classify already ran in `check_inbox`; this handler only routes fan-out rows by stored `classify_outcome` + fields.

### 2b. `async def run_scrape_meteorite(task, *, debug=False) -> dict`

**One transition per row:** `SCRAPE_LINK` → `READY` | `BOT_BLOCKED` | `ERROR`.

For each claimed row:

1. `link = (row.get("link") or "").strip()` — if not http(s) → `update_meteorite(id, state="ERROR", error="missing link")`; continue.
2. Call existing `_land_fetch_link_text(link, debug=debug)` → `(visible_text, final_url)`.
3. Classify visible text with **existing** gazer JD classifier — late-import `from src.core.gazer import _classify_jd` and map through `_CONTACT_PAGE_STATUS` the same way `contact_task_gazer_scrape` does (do **not** duplicate Playwright stack).
4. Map `page_status` → staging state via `METEORITE_INGRESS_DISPATCH_CONFIG["scrape_page_status_states"]`:
   - `blocked` → `BOT_BLOCKED`
   - `ok` + non-empty visible → `READY`, `update_meteorite(id, state="READY", content=visible_text, link=final_url or link)`
   - `closed` / `missing` / empty visible on ok → `ERROR` with short `error` message.
5. Style D only when `debug=True` (index per row: found link vs recorded state).

⚠️ **Decision:** Reuse gazer classify + contact page_status vocabulary for Playwright outcomes; write **`METEORITE_STATES`** keys on the row, not `JOB_STATES.BOT_BLOCKED`.

### 2c. `async def run_land_meteorite(task, *, debug=False) -> dict`

**One transition per row:** `READY` → `LANDED` + job create.

For each claimed row:

1. `candidate_id = row["candidate_id"]`; `content = (row.get("content") or "").strip()` — if not content → `update_meteorite(id, state="ERROR", error="missing content")`; continue.
2. `ensure_meteorite_company(candidate_id, debug=debug)` — default stem (no Ruth stem on table path unless `classify_outcome` stored employer elsewhere; employer_name optional empty).
3. Call `tracker.save_meteorite_job` with:
   - `company` = ensured short_name
   - `job_data={TRACKER_CONFIG["job_data_keys"]["job_description"]: content}`
   - `job_link=None`, `company_job_id=None` unless row already has real URL/id (do **not** treat `source_ref` as job id)
   - `employer_name` from row optional field if present else None
4. On save outcome `created` (or acceptable duplicate per tracker):
   - `update_meteorite(id, state="LANDED", astral_job_id=save["astral_job_id"])`
5. On save error outcome → `update_meteorite(id, state="ERROR", error=save.get("error") or "land failed")`.

⚠️ **Decision:** No `enrich_meteorite_land_packet` / no qualify pre-AI on table path — AC3 + AC4. Downstream `qualify_meteorite` dispatch on `METEORITE_NEW` unchanged.

## Stage 3: Retire synthesis + enrich-in-front on table path; optional consult trim

**Done when:** `_map_stage_jobs_to_scraps` is removed; public `stage_meteorite()` no longer maps source-ref scraps or calls `land_meteorite` with enrich; legacy `land_meteorite()` enrich path remains for **non-table** callers (`create_contact_meteorite`, admin Land blob) until siblings cut over; import cycle between `meteorite` ↔ `consult` documented or trimmed; `python3 -m py_compile src/core/meteorite.py src/core/consult.py src/core/dispatcher.py src/utils/config.py` succeeds.

1. **Delete** `_map_stage_jobs_to_scraps` and all call sites.

2. **Refactor public `stage_meteorite()`** (blob + source handle entry used by transitional Land API):
   - Keep: candidate validation, `invoke_stage_meteorite` classify, skip-outcome structured return.
   - **Remove:** scrap map + `land_meteorite` call chain.
   - Return classify result shape: `{outcome, stage_outcome, skipped, jobs, batch_id, error}` without `land` / `scraps` / `outcomes` from tracker land (callers moving to table ingress use dispatch rows instead — AST-1558/1559).

3. **Leave `land_meteorite()`** enrich+scrape path intact for legacy contact/create callers — table path uses `run_land_meteorite` only (Stage 2c), not public `land_meteorite()`.

4. **`consult.py` cycle trim (only if still cyclic after step 2–3):**
   - If `consult` top-level `from src.core.meteorite import is_meteorite_company` + meteorite late-import consult creates an import cycle flagged by compile/runtime, move `is_meteorite_company` import inside the functions that need it in `consult.py` OR move `is_meteorite_company` to a tiny shared module — **minimal diff**; if no cycle, **skip** `consult.py` entirely (Scope allows optional).

5. Do **not** add monitoring info lines (AST-1559), Estelle fields beyond what land already writes, or delete `meteorite_email.py`.

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not add files beyond Files Changed.
- Stops and comments on parent AST-1555 when AST-1557 symbols are missing or Playwright/gazer API shape drifted.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Joan validate

[plan-discuss] round=1 concern
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1560
**Overall:** REVISE
**Publish ref:** `sub/AST-1555/AST-1560-stage-scrape-land-transitions` @ `8434867243c5e28c15d839a090d79172c6365b3e`

## Traceability
AC2 → Stages 1–2 (per-row `claim_meteorite_batch` / `clear_meteorite_batch` + single-transition `run_stage_meteorite` / `run_scrape_meteorite` / `run_land_meteorite`); AC3 → Stage 2c (`save_meteorite_job` → `METEORITE_NEW` + `astral_job_id` + `LANDED`, no enrich); AC4 → Stages 2–3 (no `source_ref` synthesis, `job_link`/`company_job_id` null at land). **Gap:** parent functional scope #6 row-transition always-on info lines (`BOT_BLOCKED` / `ERROR` / `LANDED job=`) — partitioned from AST-1559, not staged here.

## Findings

### fix-now
- **Location:** Stage 1 §7 + Stage 2 §Shared batch pattern
- **Finding:** Dispatcher mints `entity_batch_id` for ledger/`log_batch_id`, but each runner mints a **second** `batch_id` for `claim_meteorite_batch`. Entity claim queues must use one golden ticket (`astral.batch.batch-id-first` / `pattern.batch.entity-claim-process-release`).
- **Recommendation:** Pass dispatcher `entity_batch_id` into `run_*` (via `task` or param) and use it for claim/get/clear — do not mint inside runners.

### fix-now
- **Location:** Stages 2–3 (missing stage)
- **Finding:** Parent functional scope #6 requires always-on info row-transition lines; AST-1559 plan explicitly assigned `BOT_BLOCKED` / `ERROR` / `LANDED job=` monitoring to this child. Plan only says “Do not add monitoring info lines (AST-1559)” (inbox classify) with no positive row-transition helper/config formats.
- **Recommendation:** Add config format strings (extend `METEORITE_MONITORING_CONFIG` or sibling keys in `METEORITE_INGRESS_DISPATCH_CONFIG`) + `log_meteorite_row_transition` calls in scrape/land runners on state writes.

### discuss
- **Location:** Stage 1 §3 assert — `stage_task_key == STAGE_METEORITE_CONFIG["task_key"]`
- **Finding:** Same string serves Ruth inline classify (`do_task`) and custom dispatch transition runner; disambiguation relies on dispatcher branch ordering only.
- **Recommendation:** Keep parent-mandated naming; document in module header that dispatch `stage_meteorite` row is **not** a consult hop; ensure branch precedes any `TASK_CONFIG` / `_run_unified` path.

### acceptable
- **Location:** Stage 2b scrape path — `_land_fetch_link_text` + gazer `_classify_jd` / `_CONTACT_PAGE_STATUS`
- **Finding:** Reuses existing Playwright fetch + JD classifier instead of duplicating `contact_task_gazer_scrape` browser stack.
- **Recommendation:** Late-import private gazer helpers as planned; call monitoring helper once scrape path is added.

**In-session statute pass:** Claim/process/clear + one transition per runner — **astral.batch.claim-process-release** / **astral.state.no-daisy-chain-in-run** conform (batch_id propagation excepted). Core-owned state writes via `update_meteorite` — **astral.state.core-decides-transitions** conform. Playwright via existing external helpers — **pattern.layers.import-discipline** conform. Universal orch.* — N/A/conforms.

context_tokens≈72000
