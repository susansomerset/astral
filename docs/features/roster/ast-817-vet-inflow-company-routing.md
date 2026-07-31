<!-- linear-archive: AST-817 archived 2026-07-22 -->

## Linear archive (AST-817)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-817/vet-inflow-discovery-company-dispatch-routing-get-vet-inflow-discovery  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-815 — get vet_inflow_discovery to work  
**Blocked by / blocks / related:** parent: AST-815

### Description

## What this implements

Fix **vet_inflow_discovery** dispatch execution so it uses the company vet path (read stored **inflow_discovery_blurb**, run Admin **vet_inflow_discovery** task, transition **WEBSITE_FOUND** or **VET_FAILED**) instead of incorrectly invoking the candidate **inflow_discovery** CSE batch. Restores scheduler and manual **Run** parity when **available ≥ 1**.

## Acceptance criteria

1. With candidate **somerset** (or equivalent UAT candidate), **vet_inflow_discovery** **batch_size = 1** / **run_count = 1**, and **available ≥ 1**, a manual **Run** or scheduler tick claims **one** **NEW** company and completes vet processing — logs show company vet activity, **not** `run_inflow_discovery_batch: no stale search terms`.
2. A company row with a non-empty **inflow_discovery_blurb** that passes the mechanical vet ends in **WEBSITE_FOUND** with **company_website** populated; a reject ends in **VET_FAILED**.
3. **inflow_discovery** manual **Run** still uses stale search terms and records **NEW** hits (AST-775 regression guard — no inline vet in discovery batch).
4. **inflow_resolve_website** still processes only **NEW** rows **without** a discovery blurb (eligibility split from AST-776 unchanged).
5. With **debug=True** on a vet dispatch run, Susan can read per-company index headers and outcomes in logs without opening the database.

## Boundaries

* Does **not** change **inflow_discovery** candidate CSE behavior (AST-813/814).
* Does **not** change **inflow_resolve_website** eligibility or execution.
* Does **not** change discovery hit recording (AST-775) or mechanical prompt text (AST-776).
* Does **not** alter **fetch_website** / downstream roster chain beyond correct vet outcomes.

## Notes for planning

* **AST-776** landed **vet_inflow_discovery_company** and **run_company_task** NEW routing by **dispatch_task_key** on roster; repro indicates **consult.run_consult_task** still early-returns **vet_inflow_discovery** into **run_inflow_discovery_batch** — inspect and remove that mis-route.
* Primary files: **src/core/consult.py**; verify **src/core/roster.py** company path unchanged.
* Betty owns tests — document component scenarios in plan review stub.

## Git branch (authoritative)

Per **orientation** § Branch law: parent **ftr/AST-815-vet-inflow-discovery-routing**, child **sub/AST-815/AST-817-vet-inflow-company-routing**. Created at dispatch-parent.

### Comments

#### radia — 2026-06-26T02:55:28.533Z
### Plan fidelity

Product commit `f4281fd`: surgical deletion of stale `vet_inflow_discovery` early-return in `run_consult_task` company branch (`src/core/consult.py` ~2009). Zero `vet_inflow_discovery` references remain in consult; company vet falls through to `run_company_task` → `vet_inflow_discovery_company` (AST-776). Candidate `inflow_discovery` path (`run_inflow_discovery_batch`) unchanged.

### Rubric (ASTRAL_CODE_RULES)

- **§1.3 DRY** — routing-only; no duplicate vet logic in consult.
- **§2.6** — state transitions stay in roster `vet_inflow_discovery_company`.
- **§3.3** — lazy `get_candidate` import removed with deleted block; no new layer violations.

### Issues

None (**fix-now** / **discuss**).

### Advisory

Full `origin/dev...origin/sub/AST-815/AST-817-vet-inflow-company-routing` diff includes AST-815 sibling rollup while parent is unlanded — expected; this ticket's product footprint is `consult.py` only.

Doc: [ast-817-vet-inflow-company-routing.md](https://github.com/susansomerset/astral/blob/135fd7eb90bf97bac0c90bbf7adff78fd2a47e83/docs/features/roster/ast-817-vet-inflow-company-routing.md) @ `135fd7e`.

**Verdict:** Clean — `resolve-child` may proceed.

#### betty — 2026-06-26T02:51:25.977Z
## QA test manifest (AST-817)

**Scope:** Surgical removal of stale `vet_inflow_discovery` mis-route in `consult.run_consult_task` company branch. **Manifest-only** — existing **AST-776** / **AST-775** coverage; no new tests this pass.

1. `tests/component/core/test_roster.py::TestAst776VetInflowDiscoveryCompany::test_consult_routes_company_vet_via_run_company_task` — consult company vet delegates to `run_company_task` with `dispatch_task_key=vet_inflow_discovery` (not `run_inflow_discovery_batch`)
2. `tests/component/core/test_roster.py::TestAst776VetInflowDiscoveryCompany` — `vet_inflow_discovery_company` pass/fail + `run_company_task` NEW routing (**AST-776** regression)
3. `tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_no_stale_terms_returns_zero_errors` — discovery batch unchanged; no inline vet (**AST-775** regression)
4. `tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_vet_inflow_discovery_task` — config company entity (**AST-776** regression)

**Narrowed run:**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_roster.py::TestAst776VetInflowDiscoveryCompany::test_consult_routes_company_vet_via_run_company_task \
  tests/component/core/test_roster.py::TestAst776VetInflowDiscoveryCompany \
  tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_no_stale_terms_returns_zero_errors \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_vet_inflow_discovery_task \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Publish:** `origin/sub/AST-815/AST-817-vet-inflow-company-routing` @ `c48bbbe` (`merge-tests(AST-817): origin/tests 73142e7`)

**Bible shasum:** `docs/test-bible/core/consult.md` → `767cbc70a1dbe37386f1b8253d9767d4d43c5acc0cd281d8ef9d83a5fa2b8ded`

— Betty

#### hedy — 2026-06-26T02:45:57.685Z
Plan: `https://github.com/susansomerset/astral/blob/sub/AST-815/AST-817-vet-inflow-company-routing/docs/features/roster/ast-817-vet-inflow-company-routing.md`

**Self-assessment**
- **Scope:** minor — delete one stale `vet_inflow_discovery` branch in `consult.run_consult_task` so company vet reaches `run_company_task` / `vet_inflow_discovery_company` (AST-776).
- **Conf:** high — repro and root cause are explicit; AST-776 already built the company vet path; `test_consult_routes_company_vet_via_run_company_task` specifies expected routing.
- **Risk:** Medium — `run_consult_task` is dispatch-critical, but change is surgical removal only; candidate `inflow_discovery` and other company keys untouched.

---

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

**Test-child (Hedy):** Betty manifest green — 9 passed, no product fixes.

**Manual UAT (Susan):**
- `vet_inflow_discovery` Run with `available ≥ 1` → company vet logs, not `no stale search terms`
- `inflow_discovery` still records NEW hits (no inline vet)
- `inflow_resolve_website` still targets NEW without blurb only
- `debug=True` vet run → Style D blurb headers, not CSE traces

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-815/AST-817-vet-inflow-company-routing` @ `c48bbbe` (product: `f4281fd`)

### What's solid

| Area | Notes |
| --- | --- |
| Plan fidelity | Stage 1 delivered exactly: deleted the stale `vet_inflow_discovery` early-return in `run_consult_task` company branch; no replacement branch added. `rg vet_inflow_discovery src/core/consult.py` → zero matches on publish tip. |
| Routing | Company vet falls through to `roster.run_company_task(..., dispatch_task_key=dispatch_task_key)` → `vet_inflow_discovery_company` (AST-776). Candidate branch still calls `run_inflow_discovery_batch` only. |
| §1.3 DRY | No duplicate vet logic in consult — delegates to roster unchanged. |
| §2.6 state machine | Transitions remain in `vet_inflow_discovery_company`; consult is routing-only. |
| §3.3 imports | Removed lazy `get_candidate` import with deleted block; no new imports. |
| Self-Assessment | Scope `minor` matches footprint (17 lines removed, one file). Conf `high` justified — existing `TestAst776VetInflowDiscoveryCompany::test_consult_routes_company_vet_via_run_company_task` locks the fix. |
| Tests / bible | Betty manifest + `merge-tests` on publish tip; test-bible AST-817 rows document narrowed run. |

### Issues

None.

### Recommended actions

| Severity | Action |
| --- | --- |
| **Advisory** | Full three-dot diff vs `origin/dev` includes AST-815 sibling rollup (config, roster, admin JSON, etc.) — expected while parent epic is unlanded; AST-817 product commit (`f4281fd`) is scoped to `consult.py` only. |
| **Advisory** | Susan UAT checklist in plan remains the gate for confirming runtime logs (`vet_inflow_discovery_company` / blurb vet, not `no stale search terms`). |

**Verdict:** Clean — `resolve-child` may proceed with no Radia fix-now items.

---

## Resolution

**Date:** 2026-06-26  
**Review:** Radia clean — no fix-now / discuss items.

No additional product changes. Publish tip `135fd7e` (`docs(AST-817): Radia review — clean`) already includes Radia's plan-doc review section above. Product commit `f4281fd` (surgical `consult.py` mis-route removal) unchanged.

**§9a dry-run:** `origin/sub/AST-815/AST-817-vet-inflow-company-routing` merges cleanly into `origin/dev` and `origin/ftr/AST-815-vet-inflow-discovery-routing`.

**Handoff:** User Testing — Susan UAT checklist in Build review stub (vet dispatch logs company vet activity, not `no stale search terms`).

