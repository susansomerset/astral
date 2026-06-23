# AST-774 — vet_inflow_discovery schedulable company dispatch

- **Linear (this ticket):** [AST-774](https://linear.app/astralcareermatch/issue/AST-774/vet-inflow-discovery-schedulable-company-dispatch-unable-to-schedule-vet)
- **Parent (coordination only):** [AST-762](https://linear.app/astralcareermatch/issue/AST-762/unable-to-schedule-vet-inflow-discovery)
- **Publish ref:** `origin/sub/AST-762/AST-774-vet-inflow-discovery-schedulable-company-dispatch`

## Summary

Susan cannot save a Scheduled Actions row for **`vet_inflow_discovery`** — **`save_dispatch_task`** raises **`dispatch_task task_key not schedulable`**, and Add Task previews **`entity_type: candidate`** instead of **`company`**. This ticket registers **`vet_inflow_discovery`** in the schedulable dispatch vocabulary with **company** entity type and default trigger **`NEW`**, and wires **`consult.run_consult_task`** so manual Run and AUTO dispatch execute the existing roster inflow vet pipeline (**`run_inflow_discovery_batch`** → **`do_task(vet_inflow_discovery)`** → ingest). **`inflow_discovery`** (candidate / **`LIVE_PROMPTS`**) and **`inflow_resolve_website`** (company / **`NEW`** + empty website) behavior stays unchanged.

⚠️ **Decision:** Standalone **`vet_inflow_discovery`** dispatch claims companies in **`NEW`** (eligibility pool) but executes **`run_inflow_discovery_batch`** for the dispatch row’s **`candidate_id`** — vet operates on deduped CSE hit batches keyed by candidate search terms, not per-company row iteration. Admin surface is company/**`NEW`** because outcomes land on company records; execution reuses the shipped AST-505/525 batch without splitting CSE from vet in this ticket.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add **`vet_inflow_discovery`** to **`DISPATCH_SCHEDULABLE_TASK_KEYS`** and **`_DISPATCH_COMPANY_ENTITY_TASK_KEYS`**; **`_dispatch_trigger_state_for_task_key`** → **`NEW`**; **`TASK_CONFIG["vet_inflow_discovery"]["entity_type"]`** → **`company`**; optional **`INFLOW_CONFIG["discovery"]["vet_dispatch_trigger_state"]`** literal | utils |
| `src/core/consult.py` | Company branch: **`dispatch_task_key == "vet_inflow_discovery"`** → **`run_inflow_discovery_batch`** before **`run_company_task`** fallback | core |
| `src/core/roster.py` | **`run_company_task`** **`NEW`** branch: guard so **`vet_inflow_discovery`** does not fall through to **`resolve_company_website`** | core |

**Verify only (Betty / qa-child — engineer does not edit in build-child):**

| File | Change |
|------|--------|
| `tests/component/utils/test_config.py` | **`TestAst505InflowDiscoveryConfig::test_vet_inflow_discovery_task`** — **`entity_type == "company"`**; new **`test_vet_inflow_discovery_dispatch_admin_defaults`** |
| `tests/component/core/test_consult.py` or `test_dispatcher.py` | Route **`vet_inflow_discovery`** company dispatch to **`run_inflow_discovery_batch`** (Betty picks manifest) |

**No changes expected:** `src/ui/api/api_admin.py` ( **`_dispatch_task_key_form_meta`** already calls **`dispatch_task_admin_defaults`** for schedulable keys), `src/core/dispatcher.py` (generic company **`NEW`** claim; **`require_empty_website`** remains **`inflow_resolve_website`** only).

## Stage 1: Config — schedulable key, admin defaults, TASK_CONFIG entity type

**Done when:** **`dispatch_task_admin_defaults("vet_inflow_discovery")`** returns **`entity_type=company`**, **`trigger_state=NEW`**, **`batch_call_mode=0`**; **`POST /api/admin/dispatch_tasks`** with **`task_key=vet_inflow_discovery`** no longer raises not schedulable; **`GET /api/admin/dispatch_tasks/task_keys`** shows company/**`NEW`** for the key.

1. In **`src/utils/config.py`**, add **`"vet_inflow_discovery"`** to **`DISPATCH_SCHEDULABLE_TASK_KEYS`** (after **`"inflow_resolve_website"`** in the inflow group for readability).

2. Add **`"vet_inflow_discovery"`** to **`_DISPATCH_COMPANY_ENTITY_TASK_KEYS`** (same tuple as **`inflow_resolve_website`**).

3. In **`_dispatch_trigger_state_for_task_key`**, after the **`inflow_resolve_website`** branch, add:

   ```python
   if task_key == "vet_inflow_discovery":
       return INFLOW_CONFIG["discovery"]["vet_dispatch_trigger_state"]
   ```

4. In **`INFLOW_CONFIG["discovery"]`**, add literal (same commit as step 3):

   ```python
   "vet_dispatch_trigger_state": "NEW",
   ```

5. In **`TASK_CONFIG["vet_inflow_discovery"]`**, change **`"entity_type": "candidate"`** to **`"entity_type": "company"`**. Keep **`requires_candidate_key: True`** and the existing **`response_schema`** unchanged.

6. Run locally (engineer sanity, not a commit artifact):

   ```bash
   python3 -c "from src.utils.config import dispatch_task_admin_defaults as d; print(d('vet_inflow_discovery'))"
   ```

   Expected: `{'entity_type': 'company', 'trigger_state': 'NEW', 'sort_by': 'updated_at', 'batch_call_mode': 0}`.

⚠️ **Decision:** **`vet_inflow_discovery`** does **not** use **`require_empty_website`** claim filter — pool is all unclaimed **`NEW`** companies for the candidate (includes slug-ingested rows awaiting Phase 2). **`inflow_resolve_website`** keeps its empty-website filter via existing dispatcher special case.

### Self-review (Stage 1)

| Rule | OK? |
|------|-----|
| §2.1 config | Trigger literal in **`INFLOW_CONFIG`**; schedulable membership in **`config.py`** only |
| §2.6 state machine | No new transitions — **`NEW`** already claimable |
| §3.5 naming | Key string unchanged — **`vet_inflow_discovery`** |

---

## Stage 2: Consult routing — company dispatch executes vet pipeline

**Done when:** Dispatcher **`_run_unified`** with **`entity_type=company`**, **`trigger_state=NEW`**, **`task_key=vet_inflow_discovery`** calls **`run_inflow_discovery_batch`** (not **`resolve_company_website`**); return shape remains **`_SUMMARY_ZERO`**-compatible.

1. In **`src/core/consult.py`**, inside **`run_consult_task`**, in the **`entity_type == "company"`** block, after the **`prefilter`** branch and **before** the **`return await roster.run_company_task(...)`** fallback, add:

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
       candidate = roster.get_candidate(cand_id) or {}
       if not candidate.get("astral_candidate_id"):
           candidate = {**candidate, "astral_candidate_id": cand_id}
       return await roster.run_inflow_discovery_batch(
           candidate, batch_id, ctx, debug,
       )
   ```

   Use **`roster.get_candidate`** already imported via **`from src.core import roster`** at function top — do not add a new top-level **`roster`** import if one already exists in this function’s scope.

2. Do **not** change the **`entity_type == "candidate"`** branch — **`inflow_discovery`** still calls **`run_inflow_discovery_batch`** directly.

### Self-review (Stage 2)

| Rule | OK? |
|------|-----|
| §3.3 imports | Consult → roster only; no UI/data bend |
| §2.4 batch | Dispatcher still owns claim/clear; consult returns summary dict |

---

## Stage 3: run_company_task guard — NEW branch must not resolve for vet key

**Done when:** If **`run_company_task`** is invoked with **`input_state=NEW`** and **`dispatch_task_key=vet_inflow_discovery`**, it logs a warning and returns **`total_errors=1`** without calling **`resolve_company_website`**.

1. In **`src/core/roster.py`**, in **`run_company_task`**, replace the bare **`if input_state == "NEW":`** block opening with dispatch-key guard:

   ```python
   if input_state == "NEW":
       tk = (dispatch_task_key or "").strip()
       if tk == "vet_inflow_discovery":
           logger.warning(
               "run_company_task: vet_inflow_discovery must route via consult.run_consult_task "
               "(dispatch_task_key=%r, short_name=%s)",
               tk, short_name,
           )
           return {**zero, "total_errors": 1}
       r = await resolve_company_website(short_name, entity, ctx=ctx, debug=debug)
   ```

   Keep the existing success/failure handling on **`r`** unchanged below.

⚠️ **Decision:** **`inflow_resolve_website`** and legacy **`NEW`** rows without an explicit **`task_key`** continue to hit **`resolve_company_website`** — only **`vet_inflow_discovery`** is blocked here.

### Self-review (Stage 3)

| Rule | OK? |
|------|-----|
| §2.6 | No new state writes on mis-route — error return only |
| §1.3 DRY | Reuses existing **`resolve_company_website`** path for resolve key |

---

## Execution contract (developer agent)

- Execute stages **1 → 2 → 3** in order; one commit per stage on epic worktree, then publish per **build-child** §6.
- **Stop** and post **`🛑`** on **AST-762** if **`run_inflow_discovery_batch`** signature or **`get_candidate`** import path differs from steps above — list actual signature and propose routing fix; do not improvise a parallel vet runner.
- Do **not** edit **`tests/`**, **`docs/ASTRAL_TEST_BIBLE.md`**, or **`docs/test-bible/**`** — Betty owns test manifest updates for **`entity_type`** assertion changes.
- Do **not** change vet prompts, **`response_schema`**, ingest dedupe, or **`inflow_discovery`** candidate dispatch wiring.

## Self-Assessment

**Scope:** `Single-Component` — config schedulable registration plus two small consult/roster routing branches; no dispatcher schema or UI changes.

**Conf:** `high` — mirrors **`inflow_resolve_website`** / **`fetch_job_pages`** consult branching and AST-549 **`dispatch_task_admin_defaults`** pattern; **`run_inflow_discovery_batch`** already implements vet + ingest.

**Risk:** `Medium` — wrong routing could run **`resolve_company_website`** on a **`vet_inflow_discovery`** row or break **`inflow_resolve_website`** **`NEW`** handling; mis-set **`entity_type`** in admin defaults would show wrong Add Task preview.

## Self-Assessment justifications

- **Scope:** Touches only **`config.py`**, **`consult.py`**, and a guard in **`roster.run_company_task`** — all roster inflow scheduling wiring.
- **Conf:** Existing **`run_inflow_discovery_batch`** and **`dispatch_task_admin_defaults`** are the templates; no new LLM or DB schema work.
- **Risk:** **`NEW`** trigger is shared with **`inflow_resolve_website`** — dispatch-key guards must stay explicit.

## Self-review (ASTRAL_CODE_RULES)

| Rule | Notes |
|------|-------|
| §1.3 DRY | Reuse **`run_inflow_discovery_batch`** — no duplicate vet/ingest loop |
| §2.1 config | Schedulable + trigger literals in **`config.py`** |
| §2.4 batch | Claim/clear unchanged in dispatcher; consult summary shape preserved |
| §2.6 state machine | No transition edits |
| §3.3 imports | **`consult → roster`** only in product paths |
| §3.5 naming | **`vet_inflow_discovery`** string unchanged across TASK_CONFIG and dispatch key |

No **`conf-!!-NONE`** conflicts identified.

## Regression surface (Betty / UAT)

- **`inflow_discovery`**: candidate entity, **`LIVE_PROMPTS`**, **`run_inflow_discovery_batch`** — unchanged consult branch.
- **`inflow_resolve_website`**: company **`NEW`**, **`require_empty_website=True`** at claim, **`resolve_company_website`** via **`run_company_task`** — unchanged.
- **`TestAst505InflowDiscovery`** ingest/dedupe tests — must stay green (**AC 4–5**).
- Admin Add Task for **`vet_inflow_discovery`**: save succeeds; row stores **`entity_type=company`**, **`trigger_state=NEW`**.

## Review stub (Hedy / build)

**Publish ref:** `origin/sub/AST-762/AST-774-vet-inflow-discovery-schedulable-company-dispatch`  
**Product commits:** `43ccdf2` (Stage 1 — schedulable config defaults), `ab4f64d` (Stage 2 — consult routing), `dc4a99f` (Stage 3 — run_company_task guard)
