# AST-817 — vet_inflow_discovery company dispatch routing

- **Linear:** [AST-817](https://linear.app/astralcareermatch/issue/AST-817/vet-inflow-discovery-company-dispatch-routing-get-vet-inflow-discovery-to-work)
- **Parent:** [AST-815](https://linear.app/astralcareermatch/issue/AST-815/get-vet-inflow-discovery-to-work)
- **Publish ref:** `origin/sub/AST-815/AST-817-vet-inflow-company-routing`
- **Depends on:** [AST-775](https://linear.app/astralcareermatch/issue/AST-775) (discovery records **NEW** only), [AST-776](https://linear.app/astralcareermatch/issue/AST-776) (**`vet_inflow_discovery_company`** + **`run_company_task`** NEW routing + eligibility split)

Susan's repro: **`vet_inflow_discovery`** dispatch claims **313 available** **NEW** companies, then logs **`run_inflow_discovery_batch: no stale search terms`** — execution took the **candidate discovery** path instead of the **company vet** path. **AST-776** implemented **`vet_inflow_discovery_company`** and **`run_company_task`** routing, but **`consult.run_consult_task`** still intercepts **`task_key == "vet_inflow_discovery"`** on **`entity_type == "company"`** and calls **`roster.run_inflow_discovery_batch`**. This ticket removes that stale branch so company vet dispatch reaches **`run_company_task`** → **`vet_inflow_discovery_company`**.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Remove mis-route: delete **`vet_inflow_discovery`** early-return into **`run_inflow_discovery_batch`** on the company branch | core |

**Out of scope (this ticket):** `src/utils/config.py`, `src/data/database.py`, `src/core/roster.py` (verify unchanged), `src/core/dispatcher.py`, Betty tests, mechanical prompt migration, eligibility counters, **`inflow_discovery`** / **`inflow_resolve_website`** behavior.

## Stage 1: Remove consult mis-route for company vet_inflow_discovery

**Done when:** **`run_consult_task("company", "NEW", [entity], batch_id, ctx, debug, dispatch_task_key="vet_inflow_discovery")`** delegates to **`roster.run_company_task`** with **`dispatch_task_key="vet_inflow_discovery"`**; it never calls **`run_inflow_discovery_batch`**. Existing **`TestAst776VetInflowDiscoveryCompany::test_consult_routes_company_vet_via_run_company_task`** passes.

1. Open **`src/core/consult.py`**, function **`run_consult_task`**, **`entity_type == "company"`** branch (starts ~line 1968).

2. **Delete** the entire block:
   ```python
   if task_key == "vet_inflow_discovery":
       cand_id = _candidate_id_from_ctx(ctx)
       if not cand_id:
           cand_id = str((entities[0] or {}).get("candidate_id") or "").strip()
       if not cand_id:
           logger.warning(
               "run_consult_task: vet_inflow_discovery missing candidate_id in ctx and entity"
           )
           return zero
       # Lazy import — avoids consult ↔ candidate cycle at module load (cf. agent.py).
       from src.core.candidate import get_candidate
       candidate = get_candidate(cand_id) or {}
       if not candidate.get("astral_candidate_id"):
           candidate = {**candidate, "astral_candidate_id": cand_id}
       return await roster.run_inflow_discovery_batch(
           candidate, batch_id, ctx, debug,
       )
   ```
   This block is the bug: it predates the **AST-775/776** split and forces company vet dispatch through the candidate CSE batch.

3. **Do not add** a replacement branch. **`vet_inflow_discovery`** must fall through to the existing tail of the company branch:
   ```python
   return await roster.run_company_task(
       input_state, entities[0], batch_id, ctx, debug,
       dispatch_task_key=dispatch_task_key,
   )
   ```
   Same pattern as **`inflow_resolve_website`** (no special-case in consult).

4. **Leave unchanged** the **`entity_type == "candidate"`** branch (~line 2031) that calls **`roster.run_inflow_discovery_batch`** — that is correct for **`inflow_discovery`** candidate dispatch only.

5. Run **`python3 -m py_compile src/core/consult.py`**.

⚠️ **Decision:** Surgical deletion only — **AST-776** already owns **`vet_inflow_discovery_company`** and **`run_company_task`** NEW routing; consult should not duplicate that logic.

## Stage 2: Regression verification (no product test edits)

**Done when:** Grep confirms no consult path routes company **`vet_inflow_discovery`** to discovery batch; roster company vet path untouched; build agent documents UAT checklist for Susan.

1. From repo root, run:
   ```bash
   rg -n "vet_inflow_discovery" src/core/consult.py
   ```
   Expect **zero** matches after Stage 1 (the deleted block was the only reference).

2. Confirm **`src/core/roster.py`** still contains:
   - **`vet_inflow_discovery_company`** (unchanged)
   - **`run_company_task`** NEW branch routing **`dispatch_task_key == INFLOW_CONFIG["vet"]["task_key"]`** to **`vet_inflow_discovery_company`**
   - **`run_inflow_discovery_batch`** with **no** **`do_task(vet_inflow_discovery)`** (AST-775 guard)

3. **Betty test gate (do not edit tests in build):** existing component test **`tests/component/core/test_roster.py::TestAst776VetInflowDiscoveryCompany::test_consult_routes_company_vet_via_run_company_task`** must pass at **test-child**. Document in Code Complete comment if Betty needs manifest touch-up.

4. **Manual UAT checklist** (Susan, after deploy):
   - Candidate **somerset**, **`vet_inflow_discovery`** **`batch_size=1`** / **`run_count=1`**, **`available ≥ 1`**: manual **Run** or scheduler tick logs company vet activity (**`vet_inflow_discovery_company`** / blurb / **`WEBSITE_FOUND`** or **`VET_FAILED`**), **not** **`no stale search terms`**.
   - **`inflow_discovery`** manual **Run** still searches stale terms and records **NEW** hits (no inline vet).
   - **`inflow_resolve_website`** still targets **NEW** rows **without** **`inflow_discovery_blurb`** only.
   - **`debug=True`** vet run shows Style D index headers for blurb vet, not CSE term traces.

## Self-Assessment

**Scope:** `minor` — one stale conditional block removed from **`src/core/consult.py`**; roster vet execution from **AST-776** is reused unchanged.

**Conf:** `high` — root cause is identified in the ticket and codebase; **AST-776** already implemented the correct company path; an existing component test specifies the expected consult routing.

**Risk:** `Medium` — **`run_consult_task`** is on the dispatch hot path, but the change only removes an incorrect branch; candidate **`inflow_discovery`** and other company task keys (**`prefilter`**, **`fetch_website`**, **`fetch_job_pages`**, **`inflow_resolve_website`**) are untouched.

## ASTRAL_CODE_RULES self-review

| Rule | Plan alignment |
|------|----------------|
| §1.3 DRY | No duplicate vet logic in consult — delegates to **`run_company_task`** |
| §2.1 config | No config changes |
| §2.4 batch | Company **`batch_id`** flows through **`run_company_task`** / dispatcher unchanged |
| §2.6 state machine | State transitions remain in **`vet_inflow_discovery_company`** (roster) |
| §3.3 imports | No new imports; removing lazy **`get_candidate`** import in deleted block |
| §3.5 naming | No new symbols |

No conflicts flagged.

## QA review stub (Betty @ Code Complete)

| Scenario | File | Expected test (existing or new) |
|----------|------|----------------------------------|
| Consult company vet → **`run_company_task`** | `src/core/consult.py` | `tests/component/core/test_roster.py::TestAst776VetInflowDiscoveryCompany::test_consult_routes_company_vet_via_run_company_task` |
| **`vet_inflow_discovery_company`** pass/fail | `src/core/roster.py` | `::TestAst776VetInflowDiscoveryCompany` (unchanged — regression) |
| Discovery batch no inline vet | `src/core/roster.py` | `::TestAst775SplitInflowDiscovery` (unchanged — regression) |
| Config company entity | `src/utils/config.py` | `tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_vet_inflow_discovery_task` |

**Narrowed run (suggested):**
```bash
tests/component/core/test_roster.py::TestAst776VetInflowDiscoveryCompany::test_consult_routes_company_vet_via_run_company_task \
tests/component/core/test_roster.py::TestAst776VetInflowDiscoveryCompany \
tests/component/core/test_roster.py::TestAst775SplitInflowDiscovery
```

## Build review stub

**Publish ref:** `origin/sub/AST-815/AST-817-vet-inflow-company-routing`

**Built:** Removed stale `vet_inflow_discovery` early-return in `consult.run_consult_task` company branch; company vet dispatch now falls through to `run_company_task` → `vet_inflow_discovery_company` (AST-776). Candidate `inflow_discovery` path unchanged.

**Manual UAT (Susan):**
- `vet_inflow_discovery` Run with `available ≥ 1` → company vet logs, not `no stale search terms`
- `inflow_discovery` still records NEW hits (no inline vet)
- `inflow_resolve_website` still targets NEW without blurb only
- `debug=True` vet run → Style D blurb headers, not CSE traces

