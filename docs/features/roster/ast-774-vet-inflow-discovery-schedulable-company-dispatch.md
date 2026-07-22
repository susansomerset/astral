<!-- linear-archive: AST-774 archived 2026-07-22 -->

## Linear archive (AST-774)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-774/vet-inflow-discovery-schedulable-company-dispatch-unable-to-schedule  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-762 — Unable to schedule 'vet_inflow_discovery'  
**Blocked by / blocks / related:** parent: AST-762

### Description

## What this implements

Make `vet_inflow_discovery` a schedulable `dispatch_task` key with **company** entity type and default **NEW** trigger state so Admin → Scheduled Actions can add, save, and run rows for roster inflow vetting. Wire dispatcher/consult so manual Run and AUTO claim **NEW** companies and execute vet work. Preserve `inflow_discovery` ingest creating companies in **NEW** and rejected-link dedupe on company records.

## Acceptance criteria

1. Susan can complete Add Task for `vet_inflow_discovery` without a **not schedulable** error on save.
2. Entity type shown in Add Task and stored on the saved row is **company**; default trigger state is **NEW**.
3. Manual Run and AUTO dispatch `vet_inflow_discovery` against **NEW** companies claim the correct pool and execute vet work.
4. `inflow_discovery` ingest still creates new company records in **NEW** (existing behavior preserved).
5. Rejected discovery links still land on company records for dedupe (relevant tests stay green).
6. Regression: existing `inflow_discovery` and `inflow_resolve_website` scheduled rows still save, display, and dispatch correctly.

## Boundaries

* Does not change vetting prompts, LLM response schemas, or ingest dedupe rules beyond scheduling wiring.
* Does not rework company state machine beyond **NEW** as default claim trigger for this key.
* No debug logging changes (AST-538 / AST-557 / AST-621).
* Admin Task Prompts agent assignment for `vet_inflow_discovery` remains out of scope.

## Notes for planning

* `DISPATCH_SCHEDULABLE_TASK_KEYS`, `dispatch_task_admin_defaults`, `TASK_CONFIG` entity/trigger derivation (**AST-549**).
* Dispatcher/consult/roster inflow paths — `inflow_discovery` batch already invokes `vet_inflow_discovery` via `run_next`; this ticket adds standalone schedulable company dispatch for the same key.
* Admin `GET /api/admin/dispatch_tasks/task_keys` and Scheduled Actions modal read schedulable defaults (`api_admin._dispatch_task_key_form_meta`).
* Primary layers: `src/utils/config.py`, `src/core/consult.py` / `roster.py` / `dispatcher.py`, `src/ui/api/api_admin.py` if modal metadata needs adjustment.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/ast-762-vet-inflow-discovery-schedulable`, child `sub/AST-762/<child-segment>`. Created at **dispatch-parent**.

### Comments

#### betty — 2026-06-23T21:08:38.866Z
[check-linear]

Tests updated for **[qa-handoff]** — stripped **AST-775** bleed from publish ref per Radia fix-now:

- Removed **`TestAst775InflowDiscoveryRecordNew`** and **`test_vet_failed_state_and_transition`**
- Restored **`TestAst505InflowDiscovery::test_run_batch_happy_path`** (and CSE batch tests) to inline-vet **`do_task`** mocks matching product on this ref
- Bible: removed **AST-775** blocks; **AST-774** manifest only

**Publish ref:** `origin/sub/AST-762/AST-774-vet-inflow-discovery-schedulable-company-dispatch` @ `6964818` (`merge-tests(AST-774): origin/tests 3056526`)

**Narrowed run:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_vet_inflow_discovery_task \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_vet_inflow_discovery_dispatch_admin_defaults \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_inflow_config_discovery_literals \
  tests/component/core/test_roster.py::TestAst774VetInflowDiscoveryDispatch \
  tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_happy_path \
  -q
```

**Bible shasum:**
- `docs/test-bible/utils/config.md`: `e318be1f197cf1d17425b2b248c9645bb87d063dafc014c5eb03109845dbf49e`
- `docs/test-bible/core/roster.md`: `70522785513421226fb651e7e047c3daeeffcb5635f90b2d207f8219d7aba96e`

Hedy — **`resolve-child`** can re-run manifest on epic worktree; stay **Review Posted**.

#### hedy — 2026-06-23T21:06:03.809Z
[qa-handoff]

Radia **fix-now** (AST-775 test bleed on publish ref): `merge-tests` added `TestAst775InflowDiscoveryRecordNew` and rewrote `TestAst505InflowDiscovery::test_run_batch_happy_path` for `record_inflow_discovery_hit` / `inflow_discovery_blurb`, but product on this ref still inline-vets in `run_inflow_discovery_batch` (no `record_inflow_discovery_hit`).

**Needed:** Strip AST-775 test delta from `origin/sub/AST-762/AST-774-vet-inflow-discovery-schedulable-company-dispatch`; restore `TestAst505InflowDiscovery::test_run_batch_happy_path` to match inline-vet product (see `origin/dev` version). Republish manifest @ new tip.

**Engineer done:** AST-750 sibling bleed reverted from product (`aef50c7`); narrowed manifest green (5 passed).

@Betty White

#### radia — 2026-06-23T21:04:44.352Z
**Diff:** `origin/dev...origin/sub/AST-762/AST-774-vet-inflow-discovery-schedulable-company-dispatch` @ `6916bcb`
**Doc:** `docs/features/roster/ast-774-vet-inflow-discovery-schedulable-company-dispatch.md` § Radia review

### fix-now

- **AST-750 sibling `src/` bleed** — `DISPATCH_SCORE_FLOOR_VALUES`, `dispatch_score_floor_option_labels()`, and `GET /api/admin/dispatch_tasks/score_floor_options` in `api_admin.py` are on the publish ref but not on `origin/dev` and not in the AST-774 plan. Revert from this sub ref; land via AST-750 (same bar as AST-769).

- **AST-775 test bleed without product** — `merge-tests` added `TestAst775InflowDiscoveryRecordNew` and rewrote `TestAst505InflowDiscovery::test_run_batch_happy_path` to expect record-only batch + `record_inflow_discovery_hit`, but product tip still has inline-vet `run_inflow_discovery_batch` and no `record_inflow_discovery_hit`. Manifest cannot pass against product on the same ref. Betty: strip AST-775 test delta from this publish ref (AST-774-only manifest).

### discuss

- Plan Self-Assessment **Scope: Single-Component** vs net diff also carrying AST-750 `src/` + AST-775 tests — confirm rollup intent vs accidental merge-tests bleed before parent UAT.

### advisory

- `consult.py` lazy `get_candidate` import (~1775) — matches `agent.py` grandfather; optional one-line B1 comment if touching again.

### solid (AST-774 core)

Stages 1–3 land as planned: schedulable `vet_inflow_discovery` company/`NEW` defaults; consult routes company dispatch to `run_inflow_discovery_batch`; `run_company_task` `NEW` guard blocks mis-route to `resolve_company_website`. `TestAst774VetInflowDiscoveryDispatch` + config admin-defaults tests match plan.

#### betty — 2026-06-23T21:00:40.684Z
## QA test manifest (AST-774)

**Publish ref:** `origin/sub/AST-762/AST-774-vet-inflow-discovery-schedulable-company-dispatch` @ `ffa0c93` (`merge-tests(AST-774): origin/tests 04ae683`)

1. **Config — schedulable registration + admin defaults**
   - `tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_vet_inflow_discovery_task` — **`entity_type` → `company`** (revised from AST-505 candidate assertion)
   - `::test_vet_inflow_discovery_dispatch_admin_defaults` — company / **`NEW`** / schedulable membership
   - `::test_inflow_config_discovery_literals` — **`vet_dispatch_trigger_state` == `NEW`**

2. **Consult routing — company vet dispatch → inflow batch**
   - `tests/component/core/test_roster.py::TestAst774VetInflowDiscoveryDispatch::test_consult_routes_company_vet_to_inflow_batch`

3. **Roster guard — mis-route must not resolve website**
   - `::TestAst774VetInflowDiscoveryDispatch::test_run_company_task_vet_key_guard_skips_resolve`

4. **Regression (unchanged — run if any fail in narrowed pass)**
   - `::TestAst505InflowDiscovery`, `::TestAst775InflowDiscoveryRecordNew`, `::TestAst506InflowResolve`
   - `tests/component/utils/test_config.py::TestAst506InflowResolveConfig::test_inflow_resolve_website_dispatch_admin_defaults`

**Narrowed run (test-child):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_vet_inflow_discovery_task \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_vet_inflow_discovery_dispatch_admin_defaults \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_inflow_config_discovery_literals \
  tests/component/core/test_roster.py::TestAst774VetInflowDiscoveryDispatch \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate unless you widen deliberately.

**Bible shasum (`origin/sub/…` after merge-tests):**
- `docs/test-bible/utils/config.md`: `3fed8dd34189279ba7a9a5e3850741eab6274e5633cc6933572e5d5d5d9db32c`
- `docs/test-bible/core/roster.md`: `30cec258a426896fb2908ddf79220904e847d288bd91f74f00caf3ab1c414f20`

#### hedy — 2026-06-23T20:56:07.133Z
Plan: `docs/features/roster/ast-774-vet-inflow-discovery-schedulable-company-dispatch.md`

https://github.com/susansomerset/astral/blob/sub/AST-762/AST-774-vet-inflow-discovery-schedulable-company-dispatch/docs/features/roster/ast-774-vet-inflow-discovery-schedulable-company-dispatch.md

**Self-assessment**
- **Scope:** `Single-Component` — config schedulable registration plus consult/roster routing guards; no dispatcher or UI changes.
- **Conf:** `high` — reuses `run_inflow_discovery_batch` and AST-549 `dispatch_task_admin_defaults`; mirrors `fetch_job_pages` consult branch pattern.
- **Risk:** `Medium` — `NEW` trigger is shared with `inflow_resolve_website`; explicit `dispatch_task_key` guards required so vet rows do not fall through to `resolve_company_website`.

---

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

## Radia review (2026-06-23)

**Diff:** `origin/dev...origin/sub/AST-762/AST-774-vet-inflow-discovery-schedulable-company-dispatch` @ `ffa0c93`  
**Product commits reviewed:** `43ccdf2`, `ab4f64d`, `dc4a99f` (`config.py`, `consult.py`, `roster.py` guard)

### What’s solid

| Area | Notes |
|------|-------|
| Plan Stage 1 | `vet_inflow_discovery` in `DISPATCH_SCHEDULABLE_TASK_KEYS` + `_DISPATCH_COMPANY_ENTITY_TASK_KEYS`; `TASK_CONFIG` `entity_type` → `company`; `INFLOW_CONFIG["discovery"]["vet_dispatch_trigger_state"]` → `NEW`; `_dispatch_trigger_state_for_task_key` branch. |
| Plan Stage 2 | `run_consult_task` company branch routes `vet_inflow_discovery` → `run_inflow_discovery_batch` with `candidate_id` from ctx / entity fallback and `get_candidate` hydration. |
| Plan Stage 3 | `run_company_task` `NEW` guard returns `total_errors=1` without calling `resolve_company_website` when `dispatch_task_key=vet_inflow_discovery`. |
| §2.4 / §2.6 | Dispatcher claim/clear unchanged; no new transitions; mis-route is warning + error summary only. |
| §3.3 layer | `consult → roster` + lazy `candidate.get_candidate` (matches `agent.py` precedent). |
| AST-774 tests | `TestAst774VetInflowDiscoveryDispatch` + `test_vet_inflow_discovery_dispatch_admin_defaults` align with plan matrix. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| **fix-now** | `src/utils/config.py`, `src/ui/api/api_admin.py` | **AST-750 sibling product** on publish ref vs `origin/dev`: `DISPATCH_SCORE_FLOOR_VALUES`, `dispatch_score_floor_option_labels()`, `GET /api/admin/dispatch_tasks/score_floor_options`. Plan **Out of scope** for AST-774. Revert from this sub ref; land via **AST-750** (same pattern as AST-769 review). |
| **fix-now** | Publish ref — `tests/component/` vs `src/core/roster.py` | **AST-775 test bleed** without matching product: `merge-tests` brought `test(AST-775)` (`TestAst775InflowDiscoveryRecordNew`, modified `TestAst505InflowDiscovery::test_run_batch_happy_path`) but product tip has **no** `record_inflow_discovery_hit` and `run_inflow_discovery_batch` still inline-vets (dev behavior). Manifest cannot pass against product on the same ref. Betty must strip AST-775 test delta from this publish ref (or re-sync merge-tests to AST-774-only manifest). |
| **discuss** | Plan Self-Assessment **Scope** | Stated `Single-Component` but net diff vs dev also carries AST-750 `src/` + AST-775 test tree — confirm intentional rollup vs accidental merge-tests bleed before parent UAT. |
| **advisory** | `consult.py` ~1775 | Lazy `from src.core.candidate import get_candidate` without B1 comment — acceptable via `agent.py` grandfather; add one-line lazy-load comment if touching again. |

### Recommended actions

| Action | Owner |
|--------|-------|
| Revert AST-750 `src/` delta (`config.py` score_floor helpers + `api_admin.py` route) from publish ref | Engineer (`resolve-child`) |
| Remove or re-sync AST-775 test manifest off AST-774 publish ref; restore `TestAst505` expectations to match product tip | Betty (`[qa-handoff]`) or engineer after Betty posts AST-774-only manifest |
| Optional: one-line lazy-import comment on `get_candidate` in `consult.py` | Engineer |

**Outcome:** fix-now items block clean merge — core AST-774 routing is sound once bleed is stripped.

## Resolution

**Date:** 2026-06-23  
**Radia review:** @ `6916bcb` (doc § Radia review)

### Product (Hedy)

- **AST-750 sibling bleed stripped:** Removed `DISPATCH_SCORE_FLOOR_VALUES`, `dispatch_score_floor_option_labels()`, and `GET /api/admin/dispatch_tasks/score_floor_options` from this publish ref — land via **AST-750** (same pattern as AST-769).
- **Advisory:** One-line lazy-import comment on `get_candidate` in `consult.run_consult_task` vet branch.

### Test tree (Betty — `[qa-handoff]`)

- **AST-775 test bleed stripped** @ `6964818`: removed `TestAst775InflowDiscoveryRecordNew` and `test_vet_failed_state_and_transition`; restored `TestAst505InflowDiscovery::test_run_batch_happy_path` to inline-vet `do_task` mocks; bible AST-774 manifest only.

### Resolve (Hedy — 2026-06-23)

- **Manifest:** Betty narrowed run — **6 passed** on epic worktree @ `6964818`.
- **§9a:** `origin/sub/AST-762/AST-774-vet-inflow-discovery-schedulable-company-dispatch` merges cleanly into `origin/dev` and `origin/ftr/ast-762-vet-inflow-discovery-schedulable`.
- **Linear:** → **User Testing** (assignee Hedy).
