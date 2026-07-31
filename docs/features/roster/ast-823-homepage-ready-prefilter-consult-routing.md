<!-- linear-archive: AST-823 archived 2026-07-22 -->

## Linear archive (AST-823)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-823/homepage-ready-prefilter-consult-routing-get-prefilter-company-to-work  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-821 — Get prefilter_company to work  
**Blocked by / blocks / related:** parent: AST-821

### Description

## What this implements

Susan's **HOMEPAGE_READY** prefilter dispatch hits `run_company_task` with no handler — every company logs `unhandled input_state=HOMEPAGE_READY` and the batch reports 100% errors. **AST-702** established that the schedulable **prefilter** dispatch task must route through `prefilter_company_batch` (via `consult.run_consult_task`), not the `run_company_task` fallthrough. This ticket restores that routing so batch prefilter evaluate runs and companies advance to pass/fail terminal states per existing semantics.

## Acceptance criteria

1. Given companies in **HOMEPAGE_READY** with persisted **homepage_text** (and **nav_links** when required for link decode), running the **prefilter** scheduled dispatch task produces no `unhandled input_state=HOMEPAGE_READY` warnings.
2. Each company in the batch transitions to an appropriate terminal or retry state (**PREFILTER_PASSED**, **PREFILTER_FAILED**, **NO_PREFILTER_JOBLISTS**, **WEBSITE_FOUND_RETRY**, **CANNOT_READ_WEBSITE**, **TO_WATCH**, or **IGNORE**) — not stuck in **HOMEPAGE_READY** with dispatch errors.
3. Prefilter grades, score, notes, and link fields persist per company matching today's prefilter semantics for inflow vs legacy paths.
4. Companies without **homepage_text** are skipped or failed via the readiness path — not sent to the agent and not counted as unhandled routing errors.
5. Dispatch batch summary shows **total_processed > 0** and **total_errors** reflecting only genuine failures — not 100% errors when eligible companies exist.
6. With **debug=True**, Susan can trace each company's prefilter evaluate step via index headers and substantive detail lines.

## Boundaries

* Does **not** change the **prefilter_company** rubric, encoded output shape, or decode contract (**AST-603**, **AST-697**).
* Does **not** change **fetch_website** scrape behavior or **HOMEPAGE_READY** ingestion (**AST-701**).
* Does **not** change post-prefilter locate / parse / select flows (**AST-716**–**721**, **AST-719**).
* Does **not** reintroduce monolithic **WEBSITE_FOUND** scrape+prefilter inside **run_company_task**.
* Sibling scope on parent covers full epic; this child owns consult/dispatcher routing to the batch runner only unless investigation proves a minimal roster touch is required for the same repro.

## Notes for planning

* Precedent: **AST-817** — surgical `consult.py` mis-route removal for company vet dispatch; existing `TestRunConsultTaskRoutes::test_routes_prefilter_company_batch` may already cover happy path — reproduce Susan's fallthrough and lock the fix.
* `dispatch_task_key=prefilter` must reach `roster.prefilter_company_batch` per **AST-702**; `run_company_task` intentionally has no **HOMEPAGE_READY** branch.
* If root cause is stale dispatch row (**task_key** / **batch_call_mode**) rather than consult routing, fix idempotently in `database.py` migration per **AST-703** pattern — keep product diff minimal.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/AST-821-get-prefilter-company-to-work`, child `sub/AST-821/<child-segment>`. Created at **dispatch-parent**. Engineers publish to `origin/<sub-ref>` — never Linear `gitBranchName` when it disagrees.

### Comments

#### radia — 2026-06-26T04:12:32.302Z
### Review — `origin/dev...origin/sub/AST-821/AST-823-homepage-ready-prefilter-consult-routing` @ `823de9a`

**Plan fidelity:** Single-component scope held. Stage 2 widens the existing AST-702 `prefilter` consult branch to `("prefilter", "prefilter_company")` — one line in `run_consult_task`, body unchanged including `skipped` error math. Stage 3 appends idempotent company `dispatch_task` UPDATEs after the existing AST-702/703 DELETE+retarget block; `batch_call_mode=0` fix matches Susan's stale-DB repro.

**Rubric (§3 / §1):** No new imports, layer bends, silent failures, or debug-contract changes on touched paths. Routing-only — batch claim/process/clear and state transitions stay in roster.

**Tests:** Betty manifest covers legacy dispatch key and AST-823 migration (`TestAst823PrefilterDispatchMigration`). Engineer follow-on for legacy-key test is satisfied.

**fix-now:** None.

**discuss:** `database.py` AST-823 migration — if a candidate has both an already-correct `(prefilter, HOMEPAGE_READY)` row and a legacy `(prefilter_company, …)` row, the agent-key UPDATE can hit the triple-unique constraint. UAT repro likely has only the mis-keyed row; if schema ensure errors on migrate, delete the duplicate companion before UPDATE (AST-703 collision precedent).

**advisory:** Doc commit `f92921f` — `docs/features/roster/ast-823-homepage-ready-prefilter-consult-routing.md` § Review.

#### betty — 2026-06-26T04:09:32.164Z
## QA test manifest (AST-823)

**Publish:** `origin/sub/AST-821/AST-823-homepage-ready-prefilter-consult-routing` @ `cf28de3` (`merge-tests(AST-823): origin/tests 01348df`)

**Bible shasums (publish ref):**
- `docs/test-bible/core/consult.md` → `316451e20ca0201fe75a83caaa05983f0d702a55`
- `docs/test-bible/core/roster.md` → `adef7c664672092dfda522d2a577e2df35b83d27`

**Manifest (test-child — narrowed run):**

1. `tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_prefilter_company_batch`
2. `tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_prefilter_company_batch_legacy_dispatch_key`
3. `tests/component/core/test_roster.py::TestAst702PrefilterCompanyBatch`
4. `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast641_company_prefilter_passes_union_claim_states`
5. `tests/component/data/database/test_dispatch_tasks.py::TestAst823PrefilterDispatchMigration`
6. `tests/component/data/database/test_dispatch_tasks.py::TestAst702PrefilterDispatchMigration` (regression)
7. `tests/component/data/database/test_dispatch_tasks.py::TestAst703PrefilterMigrationUniqueCollision` (regression)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_prefilter_company_batch \
  tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_prefilter_company_batch_legacy_dispatch_key \
  tests/component/core/test_roster.py::TestAst702PrefilterCompanyBatch \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast641_company_prefilter_passes_union_claim_states \
  tests/component/data/database/test_dispatch_tasks.py::TestAst823PrefilterDispatchMigration \
  tests/component/data/database/test_dispatch_tasks.py::TestAst702PrefilterDispatchMigration \
  tests/component/data/database/test_dispatch_tasks.py::TestAst703PrefilterMigrationUniqueCollision \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Betty revisions:** legacy `prefilter_company` dispatch-key routing test; AST-823 dispatch migration tests; `TestAst702PrefilterCompanyBatch::test_batch_pass_and_fail_counts` rubric stub (embedded RC + `astral_candidate_id`).

— Betty

#### hedy — 2026-06-26T04:02:29.827Z
origin/sub/AST-821/AST-823-homepage-ready-prefilter-consult-routing @ `29b2d91` — Betty: consider `test_routes_prefilter_company_batch_legacy_dispatch_key` (`dispatch_task_key='prefilter_company'`) on manifest.

#### hedy — 2026-06-26T04:00:59.244Z
Plan doc: https://github.com/susansomerset/astral/blob/sub/AST-821/AST-823-homepage-ready-prefilter-consult-routing/docs/features/roster/ast-823-homepage-ready-prefilter-consult-routing.md @ `8d955a8`

**Self-assessment**
- **Scope:** `Single-Component` — consult company-branch routing widened to catch legacy `prefilter_company` dispatch keys plus idempotent `dispatch_task` row retarget; reuses AST-702 `prefilter_company_batch` without roster evaluate changes.
- **Conf:** `high` — Susan's `unhandled input_state=HOMEPAGE_READY` log matches consult fallthrough when `dispatch_task_key != "prefilter"`; AST-702 batch path and `test_routes_prefilter_company_batch` already specify happy-path routing; AST-817 is the same surgical consult fix pattern.
- **Risk:** `Medium` — `run_consult_task` is dispatch-hot, but only extends the existing prefilter branch and normalizes DB rows; fetch_website, fetch_job_pages, vet/inflow, and job consult paths untouched.

---

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

**Diff:** `origin/dev...origin/sub/AST-821/AST-823-homepage-ready-prefilter-consult-routing` @ `823de9a`

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | Single-component scope held — consult routing widen + idempotent dispatch migration only; no rubric/decode/scrape/dispatcher changes |
| Stage 2 | `run_consult_task` company branch routes `dispatch_task_key in ("prefilter", "prefilter_company")` to `prefilter_company_batch` with unchanged `skipped` error math |
| Stage 3 | AST-823 UPDATEs append after existing AST-702/703 DELETE+retarget; `batch_call_mode=0` fix on company `prefilter` rows addresses Susan's stale-DB repro |
| §2.4 / §2.6 | Batch routing-only; state transitions remain in roster batch helpers |
| §3.3 | No new imports or layer bends; existing lazy `roster` import in consult unchanged |
| Tests | Betty manifest covers legacy dispatch key (`test_routes_prefilter_company_batch_legacy_dispatch_key`) and migration (`TestAst823PrefilterDispatchMigration`) |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| — | — | No fix-now items |

### Recommended actions

| Severity | Location | Action |
|----------|----------|--------|
| **discuss** | `src/data/database.py` AST-823 migration | If a candidate has **both** an already-correct `(prefilter, HOMEPAGE_READY)` row **and** a legacy `(prefilter_company, …)` row, the agent-key UPDATE can hit the triple-unique constraint. Susan's UAT repro likely has only the mis-keyed row; if schema ensure ever errors on migrate, delete the duplicate `prefilter_company` row (or drop the stale companion before UPDATE) per AST-703 collision precedent. |
| **advisory** | `docs/features/roster/ast-823-homepage-ready-prefilter-consult-routing.md` | Engineer review stub noted Betty follow-on for legacy-key test — delivered on manifest tip; no further test gap. |

---

## Resolution (`resolve-child`)

**Date:** 2026-06-26

**Against:** Radia `review-child` on `origin/sub/AST-821/AST-823-homepage-ready-prefilter-consult-routing` @ `823de9a`.

**Product**

- **fix-now:** None — review clean.
- **discuss:** Added `DELETE` of legacy `prefilter_company` company dispatch rows when canonical `(prefilter, HOMEPAGE_READY)` already exists for the same `candidate_id`, before the agent-key `UPDATE` — AST-703 / AST-736 triple-unique collision pattern.
- **advisory:** Betty legacy-key test already on manifest tip — no further test gap.

**§9a dry-run:** Clean sub replay merges into `origin/dev` and `origin/ftr/AST-821-get-prefilter-company-to-work`.
