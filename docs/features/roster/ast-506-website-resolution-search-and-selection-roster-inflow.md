# AST-506 — Website resolution search and selection (Roster inflow)

- **Linear:** [AST-506](https://linear.app/astralcareermatch/issue/AST-506/website-resolution-search-and-selection-roster-inflow)
- **Parent (coordination only):** [AST-490](https://linear.app/astralcareermatch/issue/AST-490/roster-inflow)
- **Publish ref:** `origin/sub/AST-490/AST-506-website-resolution-search-and-selection`
- **Blocked by (build gate):** [AST-505](https://linear.app/astralcareermatch/issue/AST-505/discovery-search-vet-slugs-and-ingest-new-companies-roster-inflow) — company **`NEW`** state and ingest path must exist first.

## Summary

Phase 2 roster inflow: for each **`NEW`** company **without** a **`company_website`**, a schedulable company dispatch task runs a **Google CSE** resolution query (up to **20** results, **no date restrict**), calls the existing **`find_company_website`** AI task pattern to pick a site or decline, and transitions the company to **`WEBSITE_FOUND`** or **`NO_WEBSITE`**. Companies that already have a URL from Phase 1 (**AST-505**) remain **`WEBSITE_FOUND`** and never enter this queue.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend **`INFLOW_CONFIG["resolve"]`** literals; ensure **`NEW`** / transitions present (if AST-505 not merged yet, mirror AST-505 Stage 1 state entries in same commit) | utils |
| `src/data/database.py` | **`_DISPATCH_TASK_SEED["inflow_resolve_website"]`**; extend **`set_company_batch` / `claim_company_batch`** with **`require_empty_website: bool`** filter | data |
| `src/core/roster.py` | **`resolve_company_website`**, **`get_new_company_batch`** passthrough for empty-website filter; **`run_company_task`** branch for **`input_state == "NEW"`** | core |
| `src/core/dispatcher.py` | No structural change if **`trigger_state NEW`** flows through existing company branch — verify **`get_new_company_batch("NEW", ...)`** picks up filter | core |

## Stage 1: Config and dispatch seed

**Done when:** **`INFLOW_CONFIG["resolve"]`** exists; **`inflow_resolve_website`** seed + config mirror added; **`NEW`** claim only selects rows with empty website.

1. In **`src/utils/config.py`**, extend **`INFLOW_CONFIG`** (create block if AST-505 not landed):

```python
"resolve": {
    "max_results": 20,
    "date_restrict_days": None,
    "task_key": "inflow_resolve_website",
    "ai_task_key": "find_company_website",
    "dispatch_trigger_state": "NEW",
},
```

2. Ensure **`COMPANY_STATES`** includes **`"NEW": {}`** and transitions **`("NEW", "WEBSITE_FOUND")`**, **`("NEW", "NO_WEBSITE")`** (skip if AST-505 already added).

3. In **`database._DISPATCH_TASK_SEED`**, add:

```python
"inflow_resolve_website": {
    "entity_type": "company",
    "trigger_state": "NEW",
    "sort_by": "updated_at",
    "batch_call_mode": 0,
},
```

4. Mirror in **`config._DISPATCH_TASK_TRIGGER_SEED`**: **`"inflow_resolve_website": {"trigger_state": "NEW"}`**.

5. In **`set_company_batch`**, add keyword-only parameter **`require_empty_website: bool = False`**. When **`True`**, append to **`where_base`**:

```sql
AND (company_website IS NULL OR TRIM(company_website) = '')
```

6. Thread **`require_empty_website`** through **`claim_company_batch`** signature (forward to **`set_company_batch`**).

7. In **`count_entities_in_state`**, **do not** add the empty-website filter globally — only claim path uses it (eligible count for AUTO must match claim).

8. Add **`count_company_new_without_website(candidate_id: str) -> int`** in **`database.py`**: **`COUNT(*)`** from **`company`** where **`state='NEW'`**, **`candidate_id=?`**, unclaimed batch, and empty website predicate — use in **`count_eligible_for_dispatch_task`** when **`task_key == "inflow_resolve_website"`** (or when **`entity_type==company`**, **`trigger_state==NEW`**, and **`require_empty_website`** flag on task — simplest: special-case **`task.get("task_key") == "inflow_resolve_website"`**).

⚠️ **Decision:** Reuse existing **`TASK_CONFIG["find_company_website"]`** ( **`task_success` + `website`** ) rather than a new task key — admin prompt already exists; Phase 2 only changes **context assembly** (CSE hit list + company slug).

### Self-review (Stage 1)

| Rule | OK? |
|------|-----|
| §2.1 config | Limits in **`INFLOW_CONFIG["resolve"]`** |
| §2.6 | **`NO_WEBSITE`** terminal for this phase |

---

## Stage 2: Resolution runner and state transitions

**Done when:** A **`NEW`** company with empty website, when dispatched, ends **`WEBSITE_FOUND`** with populated **`company_website`** or **`NO_WEBSITE`**; CSE called with **`max_results=20`**, **`days=None`**; companies with URL never claimed.

1. In **`roster.get_new_company_batch`**, add optional kwarg **`require_empty_website: bool = False`**; pass through to **`claim_company_batch`**.

2. In **`dispatcher._run_unified`** company **`else`** branch, when **`task.get("task_key") == INFLOW_CONFIG["resolve"]["task_key"]`**, call **`get_new_company_batch(..., require_empty_website=True)`**.

3. Add **`async def resolve_company_website(short_name: str, entity: Dict, ctx: Optional[Dict], debug: bool) -> Dict`** in **`roster.py`** returning **`{success, state, error}`**:
   - Assert **`company_website`** empty on entry; if not, return **`{success: True, state: "WEBSITE_FOUND", error: None}`** without work (defensive).
   - Build search query from **`entity.get("company_name") or short_name`** — string **`f"{name} official website"`** (literal format in one place in function; not config — single query template).
   - **`hits = search_google_cse(query, max_results=cfg["max_results"], site_filters=None, days=None)`**.
   - If **`hits`** empty: **`transition_company_state(short_name, "NO_WEBSITE")`**; return success.
   - Build **`live_content`**: line **`0|{short_name}|`** then for each hit **`{i+1}|{title}|{url}|{snippet}`** (1-based index matches legacy **`find_company_website`** expectations — verify admin prompt; if prompt expects 0-based **`selected`**, match prompt doc in **`task_prompt`** table and document index base in code comment).
   - **`do_task(task_key=cfg["ai_task_key"], live_content=..., index=short_name, ctx=ctx)`**.
   - Parse response:
     - If **`task_success`** is falsy or **`website`** blank after strip → **`transition_company_state(short_name, "NO_WEBSITE")`**.
     - Else **`update_company(short_name, company_website=website.strip())`** then **`transition_company_state(short_name, "WEBSITE_FOUND")`**.
   - On exception, log and return **`{success: False, error: str(e)}`** without state change.

4. In **`run_company_task`**, add **`elif input_state == "NEW":`** **before** the **`WEBSITE_FOUND`** prefilter branch:

```python
elif input_state == "NEW":
    r = await resolve_company_website(short_name, entity, ctx=ctx, debug=debug)
    if r.get("error"):
        return {**zero, "total_errors": 1}
    if r.get("state") in ("WEBSITE_FOUND", "NO_WEBSITE"):
        return {**zero, "total_passed": 1}
    return {**zero, "total_failed": 1}
```

5. **Do not** add **`NEW`** handling to prefilter or locate paths.

⚠️ **Decision:** Phase 1 URL shortcut means **`NEW`** rows with URL should not exist; empty-website claim filter is the primary guard. Defensive early exit in **`resolve_company_website`** avoids double work if data drifts.

### Self-review (Stage 2)

| Rule | OK? |
|------|-----|
| §2.4 batch | Standard per-company **`run_company_task`** dispatch |
| §2.5 external | CSE via **`search_google_cse`** only |

---

## Execution contract (developer agent)

Execute stages in order. **Stop** if **`find_company_website`** admin prompt index semantics contradict the live_content numbering — post **`🛑`** on **AST-490** with prompt excerpt and two indexing options. Do **not** implement discovery ingest (**AST-505**) or prefilter/locate (**AST-507/508**).

## Self-Assessment

**Scope:** `Single-Component` — roster resolution path + dispatch seed + claim filter; reuses existing AI task key.

**Conf:** `high` — mirrors AST-489 CSE + existing **`find_company_website`** JSON schema; claim filter is straightforward SQL.

**Risk:** `Medium` — wrong **`NEW`** claim filter could run resolution on companies that already have URLs or skip eligible rows.

## Self-Assessment justifications

- **Scope:** Core work is **`roster.resolve_company_website`** plus batch claim predicate and one dispatch seed row.
- **Conf:** **`find_company_website`** already in **`TASK_CONFIG`**; pattern matches other roster **`do_task`** calls.
- **Risk:** State transition mistakes strand companies in **`NEW`** or assign bad **`company_website`** values.

## Self-review (ASTRAL_CODE_RULES)

| Rule | Notes |
|------|-------|
| §1.3 DRY | Reuse **`find_company_website`**, **`search_google_cse`**, **`transition_company_state`** |
| §2.1 config | **`max_results`** in **`INFLOW_CONFIG`** |
| §2.4 batch | Company batch claim with explicit WHERE |
| §2.6 | **`NEW → WEBSITE_FOUND | NO_WEBSITE`** only |
| §3.3 imports | **`roster → external`** OK |

No **`conf-!!-NONE`** conflicts identified.

## Review stub (Hedy / build)

**Publish ref:** `origin/sub/AST-490/AST-506-website-resolution-search-and-selection`  
**Product tip:** `5fb33ac9` — INFLOW resolve config + `resolve_company_website` / `inflow_resolve_website` dispatch (2 product commits; publish ref includes merged AST-505 sibling)

## Review

Radia (`review-astral`, 2026-05-28): no fix-now on AST-506 resolution implementation. Advisory: merged AST-505 `consult.run_consult_task` lazy-import note (sibling). Discuss: AST-507 test classes on publish ref excluded from narrowed manifest — parent merge order for UAT.

## Resolution

**Date:** 2026-05-28  
**Engineer:** Hedy (`resolve-astral`)

No product code changes required — Radia’s review found AST-506 Phase 2 resolution path, claim filter, and dispatch wiring meet plan and **ASTRAL_CODE_RULES**. Resolution pass appended this section and re-published **`origin/sub/AST-490/AST-506-website-resolution-search-and-selection`** for User Testing.

**Publish ref tip:** see Linear **User Testing** transition (§9a dry-run clean vs **`origin/dev`** and **`origin/ftr/AST-490-roster-inflow`**).
