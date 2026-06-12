# AST-508 — Inflow locate and parse dispatch from PREFILTER_PASSED (Roster inflow)

- **Linear:** [AST-508](https://linear.app/astralcareermatch/issue/AST-508/inflow-locate-and-parse-dispatch-from-prefilter-passed-roster-inflow)
- **Parent (coordination only):** [AST-490](https://linear.app/astralcareermatch/issue/AST-490/roster-inflow)
- **Publish ref:** `origin/sub/AST-490/AST-508-inflow-locate-and-parse-from-prefilter-passed`
- **Blocked by (build gate):** [AST-507](https://linear.app/astralcareermatch/issue/AST-507/encoded-prefilter-and-prefilter-passedfailed-states-roster-inflow) — **`PREFILTER_PASSED`**, **`PREFILTER_FAILED`**, and **`company_data.prefilter_rubric_score`** must exist before this ticket builds.

## Summary

Phases 4–5 roster inflow: wire **`PREFILTER_PASSED`** companies into the **existing** roster locate/parse pipeline (**`find_job_page` → `select_job_page` → `parse_job_list`** via **`do_task` `run_next`**, AST-469) using **schedulable `dispatch_task` rows** whose **`trigger_state`** is **`PREFILTER_PASSED`**. Claim eligibility respects **`dispatch_task.score_floor`** against **`company_data.prefilter_rubric_score`** (same **dispatch-row floor** pattern as scored job consult, not an extra app-level gate). Below-floor companies stay **`PREFILTER_PASSED`** until a lower floor or higher score. Successful parse reaches the same **`WATCH`** terminal set as today's **`TO_WATCH`** manual path. **`IMPORTED`** manual entry unchanged.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | **`COMPANY_STATES["PREFILTER_PASSED"]`** + **`PREFILTER_FAILED`** (if missing); transitions from AST-507; extend **`ROSTER_CONFIG["locate_job_page"]["dispatch_input_states"]`**; **`ROSTER_CONFIG` company_data key** for rubric score; **`INFLOW_CONFIG["locate"]`** floor metadata | utils |
| `src/data/database.py` | Dispatch seeds **`find_job_page` / `select_job_page` / `parse_job_list`** with **`trigger_state: PREFILTER_PASSED`**; **`set_company_batch` / `claim_company_batch` / `count_eligible_for_dispatch_task`** **`score_floor`** for companies | data |
| `src/core/roster.py` | **`get_new_company_batch`** accepts **`score_floor`**; no change to **`find_job_page`/`parse_job_list`** logic if **`dispatch_input_states`** includes **`PREFILTER_PASSED`** | core |
| `src/core/dispatcher.py` | Pass **`score_floor`** into **`get_new_company_batch`** when **`entity_type == "company"`** and task row has non-null **`score_floor`** | core |

**Out of scope:** Reimplement locate/parse (**AST-461/469**); encoded prefilter task (**AST-507**); discovery/resolution (**AST-505/506**).

## Stage 1: Config — states, locate input states, score key

**Done when:** **`run_company_task`** locate branch accepts **`PREFILTER_PASSED`**; rubric score JSON path is documented in config; **`IMPORTED → …`** manual transitions unchanged.

1. **If AST-507 not merged**, add to **`COMPANY_STATES`** (otherwise verify only):

   - **`"PREFILTER_PASSED": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}}`**
   - **`"PREFILTER_FAILED": {}`**

2. Ensure **`ASTRAL_CONFIG["company_state_transitions"]`** includes AST-507 edges at minimum:

   - **`("WEBSITE_FOUND", "PREFILTER_PASSED")`**
   - **`("WEBSITE_FOUND", "PREFILTER_FAILED")`**
   - **`("PREFILTER_PASSED", "WATCH")`** (and other locate terminal states via existing locate/parse routing — **`HARD_PARSE`**, **`NO_OPENINGS`**, etc. — mirror **`TO_WATCH`** terminal set already allowed from **`JOBS_FOUND`** block in config)

   **Do not** remove **`("WEBSITE_FOUND", "TO_WATCH")`** or **`("IMPORTED", …)`** paths.

3. In **`ROSTER_CONFIG["locate_job_page"]`**, set:

```python
"dispatch_input_states": ["TO_WATCH", "JOBS_FOUND", "PREFILTER_PASSED"],
```

4. In **`ROSTER_CONFIG["company_data_keys"]`**, add:

```python
"prefilter_rubric_score": "prefilter_rubric_score",
```

5. Add **`INFLOW_CONFIG["locate"]`** (or extend existing **`INFLOW_CONFIG`**):

```python
"locate": {
    "dispatch_trigger_state": "PREFILTER_PASSED",
    "score_json_path": "prefilter_rubric_score",  # key inside company_data JSON
},
```

⚠️ **Decision:** **`score_floor`** lives only on **`dispatch_task`** rows (admin Scheduled Actions), **not** duplicated in **`INFLOW_CONFIG`**. Susan tunes floor per candidate on the **`PREFILTER_PASSED`** **`find_job_page`** row.

⚠️ **Decision:** **`select_job_page`** and **`parse_job_list`** scheduled rows for **`PREFILTER_PASSED`** share the same **`trigger_state`** as **`find_job_page`** (AST-485 UNIQUE **`(candidate_id, trigger_state)`** footgun) — only **one** concurrent roster dispatch row per **`PREFILTER_PASSED`** per candidate; **`task_key`** label is bookkeeping; runtime path is **`trigger_state`**-driven via **`run_company_task`**. Admin creates **one** row (default **`find_job_page`**) unless Susan adds separate rows by changing **`trigger_state`** on duplicates — document in builder Linear comment.

### Self-review (Stage 1)

| Rule | OK? |
|------|-----|
| §2.6 state machine | Adds inflow states; preserves **`IMPORTED`** |
| §2.1 config | Score key + input states centralized |

---

## Stage 2: Company `score_floor` on claim and count

**Done when:** With **`dispatch_task.score_floor = 7.0`**, a **`PREFILTER_PASSED`** company with **`prefilter_rubric_score = 6.5`** is **not** claimed; score **7.0** is claimed; companies without score JSON are **not** claimed when floor is set.

1. In **`set_company_batch`**, add optional **`score_floor: Optional[float] = None`**. When not **`None`**, append:

```sql
AND CAST(json_extract(company_data, '$.prefilter_rubric_score') AS REAL) >= ?
```

   (Use **`company_data`** column on **`company`** table — same JSON blob as other roster notes.)

2. Thread **`score_floor`** through **`claim_company_batch`**.

3. In **`count_eligible_for_dispatch_task`**, inside **`entity_type == "company"`** branch **before** WATCH stale scan logic, add:

```python
floor_raw = task.get("score_floor")
if floor_raw is not None and str(task.get("trigger_state") or "").strip() == "PREFILTER_PASSED":
    # dedicated COUNT with same predicate as set_company_batch score filter + unclaimed
    ...
```

   Implement **`count_companies_in_state_with_score_floor(candidate_id, state, floor)`** beside other count helpers — mirror job SQL from **`count_entities_in_state`** + JSON extract.

4. In **`roster.get_new_company_batch`**, add **`score_floor: Optional[float] = None`** kwarg; forward to **`claim_company_batch`**.

5. In **`dispatcher._run_unified`** company branch, replace unconditional **`get_new_company_batch(...)`** call with:

```python
floor = None
if task.get("score_floor") is not None:
    floor = float(task["score_floor"])
bid, entities = get_new_company_batch(
    input_state,
    limit=limit,
    candidate_id=candidate_id,
    batch_id=bid,
    context=f"dispatch-{input_state}",
    sort_by=sort_override,
    scan_interval_hours=scan_override,
    score_floor=floor,
)
```

   Apply floor for **any** company dispatch row with **`score_floor` set**, not only **`PREFILTER_PASSED`**, so future rows can reuse the mechanism.

6. **Do not** extend **`trigger_state_used_by_scored_dispatch_task`** — company floor is **explicit numeric JSON**, not graded job consult.

### Self-review (Stage 2)

| Rule | OK? |
|------|-----|
| §2.4 batch | Claim/count SQL stay symmetric |
| §1.4 | No hardcoded floor in Python |

---

## Stage 3: Dispatch seeds for PREFILTER_PASSED locate trio

**Done when:** Fresh DB seed templates include **`find_job_page`**, **`select_job_page`**, **`parse_job_list`** entries with **`trigger_state: PREFILTER_PASSED`** (in addition to existing **`TO_WATCH`** seeds); admin can create scheduled work for inflow locate.

1. In **`database._DISPATCH_TASK_SEED`**, add three keys (shallow-copy dict literals from existing **`TO_WATCH`** roster trio):

```python
"find_job_page_prefilter_passed": {
    "entity_type": "company",
    "trigger_state": "PREFILTER_PASSED",
    "sort_by": "updated_at",
    "batch_call_mode": 0,
},
```

   **Alternatively** (prefer this — fewer admin keys): **do not** add suffixed keys; document that Susan sets **`trigger_state=PREFILTER_PASSED`** on a **new** dispatch row using existing **`find_job_page`** template from admin modal. Seeds for **`TO_WATCH`** remain; **no duplicate seed keys required** if admin creates rows manually.

⚠️ **Decision (final):** **Do not** add new **`task_key`** strings. Reuse **`find_job_page`**, **`select_job_page`**, **`parse_job_list`** seeds only for **`TO_WATCH`**. For **`PREFILTER_PASSED`**, admin **creates dispatch rows** via existing templates changing **`trigger_state`** to **`PREFILTER_PASSED`** (UNIQUE allows one row per trigger). Stage 3 deliverable is **documentation in builder comment + verify admin API accepts **`trigger_state`** override** — **no `_DISPATCH_TASK_SEED` expansion** unless **`dispatch_task_seed_templates()`** lacks **`PREFILTER_PASSED`** preview (then add **comment-only** row in **`api_admin`** template list, not new **`task_key`**).

2. Verify **`run_company_task`** **`elif input_state in frozenset(ROSTER_CONFIG["locate_job_page"]["dispatch_input_states"])`** branch runs **`find_job_page`** for **`PREFILTER_PASSED`** without code change after Stage 1.

3. Verify AST-469 **`run_next`** chain from **`find_job_page`** still reaches **`select_job_page`** and **`parse_job_list`** for **`PREFILTER_PASSED`** entities (read **`roster.find_job_page`** — if **`input_state`** gates exist, extend to include **`PREFILTER_PASSED`** explicitly in any **`if state == "TO_WATCH"`** checks inside locate/parse helpers).

4. Grep **`roster.py`** for hardcoded **`"TO_WATCH"`** inside **`find_job_page`**, **`jobs_found_process_job_site`**, **`parse_job_list`** paths; for each gate that should also allow inflow, replace with membership in **`frozenset(ROSTER_CONFIG["locate_job_page"]["dispatch_input_states"])`**. **Do not** change **`prefilter_company`** (**`WEBSITE_FOUND`** only).

### Self-review (Stage 3)

| Rule | OK? |
|------|-----|
| §1.3 DRY | Reuse AST-469 chain |
| §2.6 | Terminal **`WATCH`** unchanged |

---

## Execution contract (developer agent)

Stop if AST-507 score key or states differ from **`prefilter_rubric_score`** / **`PREFILTER_PASSED`** assumed here — **`🛑`** on **AST-490** with AST-507 plan excerpt. Do **not** change prefilter grading (**AST-507**) or discovery (**AST-505/506**).

## Self-Assessment

**Scope:** `Single-Component` — dispatch claim/count floor + config input states; locate/parse code reused.

**Conf:** `Medium` — depends on AST-507 score persistence shape; grep pass for hardcoded **`TO_WATCH`** may surface edge cases.

**Risk:** `HIGH` — incorrect **`score_floor`** SQL could starve all inflow locate work or claim wrong companies; locate/parse mistakes affect **`WATCH`** job ingestion.

## Self-Assessment justifications

- **Scope:** No new AI tasks; mostly SQL + config + dispatch passthrough.
- **Conf:** AST-507 must land first; hardcoded state checks need audit in **`roster.py`**.
- **Risk:** This gate controls which companies enter job discovery — high impact on roster pipeline.

## Self-review (ASTRAL_CODE_RULES)

| Rule | Notes |
|------|-------|
| §2.4 batch | Claim/count symmetry with **`score_floor`** |
| §2.6 state machine | **`IMPORTED`** untouched |
| §2.1 config | Input states + JSON key in **`ROSTER_CONFIG`** |
| §1.3 DRY | Reuse **`get_new_company_batch`**, AST-469 chain |

No **`conf-!!-NONE`** — if AST-507 uses a different score field name, stop and revise plan (**would** become **`!!-NONE`**).

## Review (build)

- **Branch:** `origin/sub/AST-490/AST-508-inflow-locate-and-parse-from-prefilter-passed`
- **Commit:** `886adf76`
- **Notes:** Score floor uses AST-507 field **`prefilter_score`** (not plan doc **`prefilter_rubric_score`**). Admin creates **`PREFILTER_PASSED`** dispatch rows via existing **`find_job_page`** template with **`trigger_state`** override — no new **`_DISPATCH_TASK_SEED`** keys.

## Resolution (2026-05-27)

Radia review (`886adf76`): **no fix-now**. Plan fidelity confirmed for AC 9–12 — `score_floor` on dispatch row through claim/count SQL, `PREFILTER_PASSED` in locate input states, AST-469 chain unchanged, `IMPORTED` path untouched, no new seed keys.

**Advisory (no code change):**

- Keep **`INFLOW_CONFIG["locate"]["score_json_path"]`** and **`ROSTER_CONFIG["company_data_keys"]["prefilter_score"]`** in sync if either key changes.
- Admin should not set **`score_floor`** on non-scored company dispatch tasks (floor count path applies whenever floor is non-null).

**§9a dry-run:** `origin/sub/AST-490/AST-508-inflow-locate-and-parse-from-prefilter-passed` merges cleanly into **`origin/dev`** and **`origin/ftr/AST-490-roster-inflow`**.

**Betty manifest (886adf76):** config, dispatcher, and roster routing cases pass; DB eligible-count case depends on AST-507 states on integrated **`dev-hedy`** after **`ftr/AST-490`** merge.
