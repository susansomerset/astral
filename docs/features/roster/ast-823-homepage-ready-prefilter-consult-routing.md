# AST-823 — HOMEPAGE_READY prefilter consult routing

- **Linear:** [AST-823 — HOMEPAGE_READY prefilter consult routing (Get prefilter_company to work)](https://linear.app/astralcareermatch/issue/AST-823/homepage-ready-prefilter-consult-routing-get-prefilter-company-to-work)
- **Parent:** [AST-821 — Get prefilter_company to work](https://linear.app/astralcareermatch/issue/AST-821/get-prefilter-company-to-work)
- **Publish ref:** `origin/sub/AST-821/AST-823-homepage-ready-prefilter-consult-routing`
- **UAT bug of:** [AST-821](https://linear.app/astralcareermatch/issue/AST-821/get-prefilter-company-to-work) — Susan repro 2026-06-25: **HOMEPAGE_READY** prefilter dispatch logs `run_company_task: unhandled input_state=HOMEPAGE_READY` and batch reports 100% errors
- **Related:** [AST-702](https://linear.app/astralcareermatch/issue/AST-702) (batch prefilter + consult `prefilter` routing — Done on `dev`), [AST-817](https://linear.app/astralcareermatch/issue/AST-817) (surgical consult mis-route removal precedent)

Susan runs the schedulable **prefilter** company dispatch on **HOMEPAGE_READY** companies (homepage scrape already done via **AST-701**). Dispatcher claims rows and calls **`consult.run_consult_task`**, but execution falls through to **`roster.run_company_task`**, which intentionally has **no** **HOMEPAGE_READY** handler (monolithic **WEBSITE_FOUND** scrape+prefilter removed in **AST-702**). Every claimed company logs **`unhandled input_state=HOMEPAGE_READY`** and counts as **`total_errors`** — zero prefilter progress.

**Root cause (expected):** **`dispatch_task_key` on the consult company branch does not equal `"prefilter"`** at runtime, so the existing **`prefilter → prefilter_company_batch`** branch (~`consult.py` line 1996) is skipped. **`run_company_task`** is only correct for company keys like **`fetch_job_pages`**, **`select_job_page`**, **`parse_job_list`**, **`vet_inflow_discovery`**, etc. — not homepage batch evaluate. Common stale-DB patterns: **`task_key='prefilter_company'`** (agent key on the dispatch row), **`batch_call_mode=0`**, or **`trigger_state`** still **`WEBSITE_FOUND`** / **`WEBSITE_FOUND_RETRY`** without **AST-702** / **AST-703** migration completing on Susan's candidate DB.

This ticket restores **AST-702** wiring: **`dispatch_task_key=prefilter`** (and legacy mis-keyed rows) must reach **`roster.prefilter_company_batch`** — consult/dispatcher routing and idempotent dispatch-row migration only; no rubric, decode, scrape, or post-prefilter locate/parse changes.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Route company dispatch when **`dispatch_task_key`** is **`prefilter`** or legacy mis-key **`prefilter_company`** to **`prefilter_company_batch`**; do not fall through to **`run_company_task`** for those keys on **HOMEPAGE_READY** | core |
| `src/data/database.py` | Idempotent migration: retarget legacy **`prefilter_company`** / stale **`prefilter`** dispatch rows to **`task_key='prefilter'`**, **`trigger_state='HOMEPAGE_READY'`**, **`batch_call_mode=1`** (follow **AST-703** delete-before-update order for retry companions) | data |

**Verify only (Betty / qa-child — engineer does not edit in build-child):**

| File | Change |
|------|--------|
| `tests/component/core/test_consult.py` | Extend **`TestRunConsultTaskRoutes`** — legacy **`dispatch_task_key='prefilter_company'`** routes to batch (if missing) |
| `tests/component/data/database/test_dispatch_tasks.py` | Migration coverage for **AST-823** row retarget (if missing) |

**Out of scope:** `prefilter_company` rubric/decode (**AST-603**, **AST-697**), **`fetch_website`** / **HOMEPAGE_READY** scrape (**AST-701**), post-prefilter PJL routing (**AST-716**–**721**, **AST-719**), monolithic **WEBSITE_FOUND** reintroduction, UI, **`dispatcher.py`** logic (unless investigation proves a guard excludes company **`batch_call_mode=1`** — grep-only in Stage 1).

---

## Stage 1: Confirm fallthrough path (investigation — no product commit unless regression)

**Done when:** You can state which **`dispatch_task_key`** value(s) reach **`run_company_task`** for Susan's repro, and confirm the **`prefilter`** consult branch exists on this branch tip.

1. From repo root, confirm **AST-702** consult routing is present (not regressed):
   ```bash
   rg -n 'if task_key == "prefilter"' src/core/consult.py
   rg -n 'prefilter_company_batch' src/core/consult.py
   ```
   Expect exactly one **`prefilter`** batch branch before the **`run_company_task`** company tail.

2. Confirm **`run_company_task`** has **no** **HOMEPAGE_READY** branch (expected — fallthrough is the bug):
   ```bash
   rg -n 'HOMEPAGE_READY' src/core/roster.py | rg 'run_company_task|elif input_state'
   ```
   Expect **no** **`elif input_state == "HOMEPAGE_READY"`** inside **`run_company_task`**.

3. Reproduce the warning in-process (proves consult fallthrough, not a direct roster call):
   ```python
   # One-liner in python REPL or temporary spike under debug/spikes/ — do NOT commit spike
   import asyncio
   from src.core import consult
   asyncio.run(consult.run_consult_task(
       "company", "HOMEPAGE_READY",
       [{"short_name": "stripe", "state": "HOMEPAGE_READY", "company_data": {"homepage_text": "x"}}],
       "batch-repro", {}, debug=False,
       dispatch_task_key="prefilter_company",  # legacy mis-key — expect fallthrough today
   ))
   ```
   Then patch consult locally and re-run with **`dispatch_task_key="prefilter"`** — second run must **not** log **`unhandled input_state=HOMEPAGE_READY`**.

4. On a DB with Susan's candidate (or component-test sqlite after schema ensure), inspect prefilter dispatch rows:
   ```sql
   SELECT id, task_key, trigger_state, batch_call_mode, entity_type, batch_size
   FROM dispatch_task
   WHERE entity_type = 'company'
     AND (task_key IN ('prefilter', 'prefilter_company')
          OR trigger_state IN ('HOMEPAGE_READY', 'WEBSITE_FOUND', 'WEBSITE_FOUND_RETRY'));
   ```
   Record **`task_key`**, **`trigger_state`**, **`batch_call_mode`** for the row Susan runs manually.

5. Grep dispatcher for company batch-mode exclusions (verify-only):
   ```bash
   rg -n 'batch_call_mode' src/core/dispatcher.py
   ```
   Expect company rows with **`batch_call_mode=1`** to call **`run_consult_task(..., entities, ...)`** once — no code change unless a guard explicitly skips company batch mode (fix only if found).

⚠️ **Decision:** If step 1 shows the **`prefilter`** branch is **missing** (regression), restore it per **AST-702 Stage 4** verbatim before Stage 2. If present, Stage 2 addresses **`dispatch_task_key`** mismatch + stale DB rows.

---

## Stage 2: Consult — route prefilter dispatch to batch runner

**Done when:** **`run_consult_task("company", "HOMEPAGE_READY", entities, batch_id, ctx, debug, dispatch_task_key=<prefilter or legacy mis-key>)`** calls **`roster.prefilter_company_batch`** and returns normalized **`{total_processed, total_passed, total_failed, total_errors}`** with **`skipped`** folded into errors; it **never** calls **`run_company_task`** for those keys.

1. Open **`src/core/consult.py`**, function **`run_consult_task`**, **`if entity_type == "company":`** block (~line 1968).

2. Replace the single-key check:
   ```python
   if task_key == "prefilter":
   ```
   with:
   ```python
   if task_key in ("prefilter", "prefilter_company"):
   ```
   Leave the **`prefilter_company_batch`** body unchanged (including **`skipped`** error math).

3. **Do not** add a **`run_company_task`** branch for **HOMEPAGE_READY**. **Do not** change **`fetch_website`**, **`fetch_job_pages`**, or job-side routing.

4. Run **`python3 -m py_compile src/core/consult.py`**.

⚠️ **Decision:** **`prefilter_company`** is the **agent** **`TASK_CONFIG`** key, not a schedulable dispatch key — but mis-seeded legacy **`dispatch_task`** rows may still carry it. Routing them to **`prefilter_company_batch`** is safer than **`run_company_task`** fallthrough; Stage 3 normalizes rows to **`prefilter`**.

---

## Stage 3: Database — idempotent dispatch row retarget (AST-703 order)

**Done when:** Schema ensure migrates legacy company prefilter dispatch rows to **`task_key='prefilter'`**, **`trigger_state='HOMEPAGE_READY'`**, **`batch_call_mode=1`** without UNIQUE triple collisions; admin Scheduled Actions list shows the corrected row for Susan's candidate.

1. In **`src/data/database.py`**, inside **`_ensure_dispatch_task_schema`** (with other one-time migrations, after table exists), append idempotent SQL guarded by a comment **`# AST-823: legacy prefilter dispatch row retarget`**:

   **3a. Delete obsolete retry companions first** (same **AST-703** pattern — avoid triple-unique collapse):
   ```python
   conn.execute(
       "DELETE FROM dispatch_task "
       "WHERE task_key = 'prefilter' AND trigger_state = 'WEBSITE_FOUND_RETRY'"
   )
   ```

   **3b. Collapse legacy agent-key dispatch rows:**
   ```python
   conn.execute(
       "UPDATE dispatch_task SET task_key = 'prefilter', trigger_state = 'HOMEPAGE_READY', batch_call_mode = 1 "
       "WHERE entity_type = 'company' AND task_key = 'prefilter_company'"
   )
   ```

   **3c. Retarget remaining stale base prefilter rows** (covers DBs that missed **AST-702** / **AST-703**):
   ```python
   conn.execute(
       "UPDATE dispatch_task SET trigger_state = 'HOMEPAGE_READY', batch_call_mode = 1 "
       "WHERE task_key = 'prefilter' AND entity_type = 'company' "
       "AND trigger_state IN ('WEBSITE_FOUND', 'WEBSITE_FOUND_RETRY')"
   )
   conn.execute(
       "UPDATE dispatch_task SET batch_call_mode = 1 "
       "WHERE task_key = 'prefilter' AND entity_type = 'company' AND batch_call_mode = 0"
   )
   conn.commit()
   ```

2. **Do not** remove **`fetch_website`** rows or change **`_RETRY_TASK_SEED`** beyond what is already on **`dev`**.

3. Manual verification (Susan or build agent with local DB):
   - Scheduled Actions shows one **`prefilter`** company row: **`trigger_state=HOMEPAGE_READY`**, **`batch_call_mode=1`**, **`entity_type=company`**.
   - Separate **`fetch_website`** row remains **`WEBSITE_FOUND`** (**AST-701**).

---

## Stage 4: Regression verification (no product test edits)

**Done when:** Component tests covering consult prefilter routing and dispatch migration pass; manual UAT checklist documented for Susan.

1. Run **`python3 -m py_compile src/core/consult.py`** (and **`src/data/database.py`** if Stage 3 touched).

2. **Betty test gate (do not edit tests in build):** existing manifest lines must pass at **test-child**:
   - `tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_prefilter_company_batch`
   - `tests/component/core/test_roster.py::TestAst702PrefilterCompanyBatch` (batch outcomes unchanged)
   - `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast641_company_prefilter_passes_union_claim_states`
   - `tests/component/data/database/test_dispatch_tasks.py::TestAst702PrefilterDispatchMigration` (and any **AST-823** migration test Betty adds)

3. If Betty has not added legacy-key coverage, post in Code Complete comment: recommend **`test_routes_prefilter_company_batch_legacy_dispatch_key`** with **`dispatch_task_key='prefilter_company'`** — not blocking if Stage 2 code is correct.

4. **Manual UAT checklist** (Susan, after deploy):
   - Companies in **HOMEPAGE_READY** with **`homepage_text`** (and **`nav_links`** when link decode needed).
   - Run schedulable **`prefilter`** dispatch (**`batch_size`** small, **`run_count=1`**).
   - **No** log lines **`run_company_task: unhandled input_state=HOMEPAGE_READY`**.
   - Batch summary: **`total_processed > 0`**, **`total_errors`** not 100% when eligible companies exist; companies advance to **PREFILTER_PASSED**, **PREFILTER_FAILED**, **NO_PREFILTER_JOBLISTS**, **WEBSITE_FOUND_RETRY**, **CANNOT_READ_WEBSITE**, **TO_WATCH**, or **IGNORE** per path — not stuck in **HOMEPAGE_READY**.
   - Companies missing **`homepage_text`**: readiness skip → **CANNOT_READ_WEBSITE** with notes — not agent call, not routing error.
   - **`debug=True`**: per-company **`prefilter_company_batch`** / decode index headers with substantive detail lines (**AST-538**).

---

## Self-Assessment

**Scope:** `Single-Component` — surgical **`consult.run_consult_task`** company routing plus idempotent **`dispatch_task`** migration; reuses **AST-702** **`prefilter_company_batch`** unchanged.

**Conf:** `high` — Susan's log matches consult fallthrough when **`dispatch_task_key != "prefilter"`**; **AST-702** already defines the correct batch path and an existing component test covers **`dispatch_task_key="prefilter"`**; **AST-817** establishes the same surgical consult-routing fix pattern.

**Risk:** `Medium` — **`run_consult_task`** is on the dispatch hot path, but the change only widens the existing **`prefilter`** branch and normalizes DB rows; **`fetch_website`**, **`fetch_job_pages`**, vet/inflow, and job consult routing are untouched.

---

## ASTRAL_CODE_RULES self-review

| Rule | Plan alignment |
|------|----------------|
| §1.3 DRY | Reuses **`prefilter_company_batch`** / **`_apply_prefilter_decoded_company_outcome`** — no duplicate evaluate logic in consult |
| §2.1 config | Dispatch trigger and **`batch_call_mode`** corrected via DB migration + existing **`dispatch_task_admin_defaults("prefilter")`** |
| §2.4 batch | **`batch_call_mode=1`** restored for company prefilter; summary counts unchanged (**`skipped`** in error math) |
| §2.6 state machine | State transitions remain in roster batch helpers — consult is routing-only |
| §2.8 coat-check | Readiness failures stay **`CANNOT_READ_WEBSITE`** via batch runner — not **`run_company_task`** |
| §3.3 imports | Lazy **`roster`** import already present in **`run_consult_task`** — no new cycles |
| §3.5 naming | Dispatch key stays **`prefilter`**; agent task stays **`prefilter_company`** — migration renames mis-keyed dispatch rows only |

No conflicts requiring plan revision.

---

## Review

**Diff:** `origin/dev...origin/sub/AST-821/AST-823-homepage-ready-prefilter-consult-routing` @ `2105ed4`

**Built:** Stage 2 — consult routes `dispatch_task_key` in `("prefilter", "prefilter_company")` to `prefilter_company_batch`. Stage 3 — idempotent `dispatch_task` migration retargets legacy `prefilter_company` rows and stale `batch_call_mode` / `trigger_state` on company prefilter rows.

**Product commits:** `5c1937d` (Stage 2 — consult routing), `2105ed4` (Stage 3 — dispatch migration)

**Stage 1 investigation:** AST-702 `prefilter` branch present on branch tip; `run_company_task` has no HOMEPAGE_READY handler (expected fallthrough bug). Dispatcher company `batch_call_mode=1` path calls `run_consult_task` once — no exclusion guard found.

**Betty follow-on (non-blocking):** recommend `TestRunConsultTaskRoutes::test_routes_prefilter_company_batch_legacy_dispatch_key` with `dispatch_task_key='prefilter_company'` if not already on manifest.
