# AST-814 — Wire inflow_discovery staleness to dispatch_task freq_hrs

- **Linear (this ticket):** [AST-814](https://linear.app/astralcareermatch/issue/AST-814/wire-inflow-discovery-staleness-to-dispatch-task-freq-hrs-get-inflow)
- **Parent (coordination only):** [AST-813](https://linear.app/astralcareermatch/issue/AST-813/get-inflow-discovery-to-work)
- **Publish ref:** `origin/sub/AST-813/AST-814-inflow-discovery-freq-hrs`

## Summary

**inflow_discovery** eligibility and batch term selection still read **`INFLOW_CONFIG["discovery"]["scan_interval_hours"]` (168)** while the Scheduled Actions row's **`freq_hrs`** is ignored — Susan's **somerset** repro (`freq_hrs = 0`, fourteen table rows, all recently scanned) shows **Available = 1** in admin but dispatch skips with `0 stale (scan_interval_hours=168.0)`. This ticket wires **`dispatch_task.freq_hrs`** end-to-end: admin **Available**, `count_eligible_for_dispatch_task`, `describe_candidate_inflow_discovery_eligibility`, and `run_inflow_discovery_batch` stale-term selection share one interval. **`freq_hrs <= 0`** means no staleness gate (every table row counts as stale/eligible). Remove discovery-inflow dependence on config **168** literals.

⚠️ **Decision:** **`freq_hrs <= 0` → all `company_search_terms` rows are stale** (opposite of today's `count_stale_company_search_terms` early-return of 0). This matches the parent AC and Susan's **somerset** row; it differs from company WATCH, which falls back to **`COMPANY_STATES`** when row **`freq_hrs`** is unset — inflow has no state-level fallback.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Stale-term helpers take `freq_hrs`; `freq_hrs <= 0` counts/lists all rows; eligibility/describe wired to row `freq_hrs` | data |
| `src/utils/config.py` | Remove `scan_interval_hours` and `dispatch_freq_hrs` from `INFLOW_CONFIG["discovery"]` | utils |
| `src/core/dispatcher.py` | Pass `task["freq_hrs"]` into eligibility describe; inject `inflow_discovery_freq_hrs` into `ctx` before consult | core |
| `src/core/roster.py` | `run_inflow_discovery_batch` reads `freq_hrs` from `ctx`, not config | core |
| `src/core/consult.py` | No signature change if `ctx` carries `inflow_discovery_freq_hrs` from dispatcher (verify call path only) | core |

**Tests:** Betty owns **`tests/`** — engineer does **not** edit test files. Stage 4 documents manifest scenarios for AC 6.

## Stage 1: Data layer — stale-term semantics and eligibility

**Done when:** `count_eligible_for_dispatch_task` on an **inflow_discovery** row with `freq_hrs = 0` and fourteen table rows (all fresh `last_scan_at`) returns **14** (or **1** per existing eligible=0|1 contract — see step 5); with `freq_hrs = 168` and all terms fresh returns **0**; debug reason cites `freq_hrs`, not `scan_interval_hours`.

1. In **`src/data/database.py`**, update **`count_stale_company_search_terms(candidate_id, freq_hrs: float)`**:
   - Rename the second parameter in the docstring to **`freq_hrs`** (dispatch row hours); keep the Python parameter name or rename to **`freq_hrs`** — callers in this ticket must use the new name consistently.
   - When **`freq_hrs <= 0`**: return **`COUNT(*)`** of all **`company_search_terms`** rows for **`candidate_id`** (no `last_scan_at` filter).
   - When **`freq_hrs > 0`**: keep existing SQL (`last_scan_at IS NULL OR last_scan_at < datetime('now', '-' || ? || ' hours')`).

2. In the same file, update **`list_stale_company_search_terms(candidate_id, freq_hrs: float)`** with the same **`freq_hrs <= 0` / `> 0`** split: **`<= 0`** returns all term strings ordered **`search_term ASC`**; **`> 0`** keeps existing stale SQL.

3. Change **`describe_candidate_inflow_discovery_eligibility(candidate_id: str, freq_hrs: float) -> tuple[int, str]`**:
   - Add required **`freq_hrs: float`** parameter (default not allowed — callers must pass the dispatch row value).
   - Remove **`scan_h = float(INFLOW_CONFIG["discovery"]["scan_interval_hours"])`**.
   - After candidate-state and table-empty checks, call **`count_stale_company_search_terms(cid, float(freq_hrs or 0))`**.
   - When **`stale == 0`** and **`total > 0`**, return reason **`f"eligibility: {total} table row(s) but 0 stale (freq_hrs={float(freq_hrs or 0)})"`** — never mention **`scan_interval_hours`**.

4. In **`count_candidate_inflow_discovery_eligible(candidate_id, freq_hrs, last_run_at)`**:
   - Remove **`del freq_hrs, last_run_at`**.
   - Keep **`last_run_at` ignored** (per-term **`last_scan_at`**, not dispatch cadence — AST-525 unchanged).
   - Delegate: **`eligible, _ = describe_candidate_inflow_discovery_eligibility(candidate_id, float(freq_hrs or 0))`**.

5. In **`count_eligible_for_dispatch_task`**, candidate branch — replace:

   ```python
   return count_candidate_inflow_discovery_eligible(candidate_id, 0, None)
   ```

   with:

   ```python
   return count_candidate_inflow_discovery_eligible(
       candidate_id, float(task.get("freq_hrs") or 0), task.get("last_run_at")
   )
   ```

6. Manual verification (REPL):

   ```python
   from src.data import database as db
   db.save_candidate("somerset", state="LIVE_PROMPTS", candidate_data={})
   db.sync_company_search_terms("somerset", ["t1", "t2"])
   for term in ["t1", "t2"]:
       db.update_company_search_term_last_scan_at("somerset", term)
   task = {"entity_type": "candidate", "trigger_state": "LIVE_PROMPTS",
           "candidate_id": "somerset", "task_key": "inflow_discovery", "freq_hrs": 0}
   assert db.count_eligible_for_dispatch_task(task) == 1
   assert db.count_stale_company_search_terms("somerset", 0) == 2
   assert db.list_stale_company_search_terms("somerset", 0) == ["t1", "t2"]
   assert db.count_eligible_for_dispatch_task({**task, "freq_hrs": 168}) == 0
   ```

### Self-review (Stage 1)

| Rule | OK? |
|------|-----|
| §2.1 config | Eligibility reads row **`freq_hrs`**, not **`INFLOW_CONFIG`** interval |
| §2.4 batch | Stale SQL unchanged when **`freq_hrs > 0`** |
| §1.3 DRY | **`describe`** and **`count_*`** share stale helpers |
| §3.3 imports | Lazy **`database → candidate`** import in **`describe`** unchanged |

---

## Stage 2: Config — remove discovery-inflow 168 literals

**Done when:** `INFLOW_CONFIG["discovery"]` has no **`scan_interval_hours`** or **`dispatch_freq_hrs`** keys; a repo search for **`168`** in discovery-inflow paths (eligibility, roster batch, describe) returns no hits.

1. In **`src/utils/config.py`**, **`INFLOW_CONFIG["discovery"]`**, delete keys **`scan_interval_hours`** and **`dispatch_freq_hrs`** and their comments. Leave **`max_results_per_query`**, **`date_restrict_days`**, **`dispatch_trigger_state`**, **`task_key`**, **`vet_task_key`**, **`vet_dispatch_trigger_state`** untouched.

2. Confirm no remaining product-code references to **`INFLOW_CONFIG["discovery"]["scan_interval_hours"]`** or **`["dispatch_freq_hrs"]`**:

   ```bash
   rg 'scan_interval_hours|dispatch_freq_hrs' src/ --glob '*.py'
   ```

   Expected: hits only in **`COMPANY_STATES`**, company batch claim/count, and **`get_new_company_batch`** — **not** inflow discovery paths.

3. Do **not** change **`vet`**, **`resolve`**, or other **`INFLOW_CONFIG`** sections.

### Self-review (Stage 2)

| Rule | OK? |
|------|-----|
| §1.4 magic numbers | Discovery cadence is DB-driven (**`dispatch_task.freq_hrs`**) |
| §2.1 config | CSE limits (`max_results_per_query`, `date_restrict_days`) remain config literals |

---

## Stage 3: Dispatcher and roster — pass freq_hrs through execution

**Done when:** Manual **Run** on **somerset** with `freq_hrs = 0` executes CSE for all fourteen terms (not "no stale search terms"); admin **Available** and dispatch **`available_count`** match for the same row.

1. In **`src/core/dispatcher.py`**, **`_dispatch_one`**, after **`ctx = dict(ctx)`** and before **`ctx["entity_batch_id"] = ...`**, when **`task_key == INFLOW_CONFIG["discovery"]["task_key"]`**:

   ```python
   ctx["inflow_discovery_freq_hrs"] = float(task.get("freq_hrs") or 0)
   ```

   Import **`INFLOW_CONFIG`** from **`src.utils.config`** if not already in scope at that line.

2. In **`_run_dispatch_loop`**, update the **`describe_candidate_inflow_discovery_eligibility`** call to pass row freq:

   ```python
   _eligible, reason = database.describe_candidate_inflow_discovery_eligibility(
       task.get("candidate_id") or "",
       float(task.get("freq_hrs") or 0),
   )
   ```

3. In **`src/core/roster.py`**, **`run_inflow_discovery_batch`**:
   - Remove **`scan_h = float(cfg["scan_interval_hours"])`**.
   - Read **`freq_hrs = float((ctx or {}).get("inflow_discovery_freq_hrs") or 0)`**.
   - Call **`list_stale_company_search_terms(candidate_id, freq_hrs)`**.
   - When debug and no terms, outcome string remains **`"no stale search terms"`** (behavior unchanged; with **`freq_hrs = 0`** and non-empty table, terms list is non-empty).

4. Verify **`src/core/consult.py`** candidate branch (**`entity_type == "candidate"`**) passes **`ctx`** through to **`run_inflow_discovery_batch`** unchanged — no consult edit required if step 1 ran in dispatcher.

5. Do **not** modify **`vet_inflow_discovery`**, **`inflow_resolve_website`**, or company WATCH/gaze **`freq_hrs`** paths.

### Self-review (Stage 3)

| Rule | OK? |
|------|-----|
| §1.5.1 debug | Eligibility reason only on skip; cites **`freq_hrs`** |
| §2.5 bright line | Roster reads interval from dispatch context, not config |
| §2.6 state machine | Candidate **LIVE_PROMPTS** gate unchanged |

---

## Stage 4: QA handoff note (Betty — AC 6)

**Done when:** Linear comment or build review stub documents scenarios below; engineer does **not** commit test files.

Betty manifest additions (update **AST-525** / **AST-802** clusters as needed):

| # | Scenario | Suggested location |
|---|----------|-------------------|
| 1 | **LIVE_PROMPTS**, two table rows, both fresh **`last_scan_at`**, **`freq_hrs = 0`** → **`count_eligible_for_dispatch_task` == 1**; **`list_stale_company_search_terms` returns both terms** | `tests/component/data/database/test_dispatch_tasks.py` (**`TestAst814InflowDiscoveryFreqHrs`**) |
| 2 | Same fixture, **`freq_hrs = 168`** → eligible **0**; reason contains **`freq_hrs=168`**, not **`scan_interval_hours`** | same |
| 3 | **`count_eligible_for_dispatch_task`** with task **`freq_hrs: 0`** vs hardcoded config — eligible when config interval would exclude fresh terms | same |
| 4 | Dispatcher skip **`debug=True`**, **`freq_hrs = 168`**, all fresh → **`eligibility:`** detail cites **`freq_hrs=`** | `tests/component/core/test_dispatcher.py` |
| 5 | Remove or rewrite **`TestAst525InflowDiscoveryConfig.test_scan_interval_hours_literal`** and **`TestAst505InflowDiscoveryConfig`** assertions on **`dispatch_freq_hrs` / `scan_interval_hours`** (keys removed from config) | `tests/component/utils/test_config.py` |
| 6 | **`run_inflow_discovery_batch`** with **`ctx["inflow_discovery_freq_hrs"] = 0`** and fresh terms still selects terms for CSE | `tests/component/core/test_roster.py` |

Existing **AST-525** / **AST-802** tests that pass **`168.0`** to **`count_candidate_inflow_discovery_eligible`** must remain green once **`freq_hrs`** is wired (they already pass the interval explicitly).

---

## Execution contract (for the developer agent)

Execute stages **1 → 4** in order. One commit per stage on epic worktree, then publish each to **`origin/sub/AST-813/AST-814-inflow-discovery-freq-hrs`**. Blocking questions → parent **AST-813** with 🛑 format from **plan-child**.

## Self-Assessment

**Scope:** `Single-Component` — Touches **`database.py`**, **`config.py`**, **`dispatcher.py`**, and **`roster.py`** only; rewires inflow discovery staleness from config **168** to **`dispatch_task.freq_hrs`**.

**Conf:** `high` — Root cause is explicit (ignored **`freq_hrs`** + inverted **`<= 0`** stale helpers); company WATCH **`freq_hrs`** precedent exists in **`count_eligible_for_dispatch_task`** and **`_run_unified`**.

**Risk:** `Medium` — Wrong **`freq_hrs <= 0`** semantics could over-run CSE (all terms every dispatch) or under-run (still gated by **168**); mitigated by shared helper used in count, list, describe, and batch paths.

## Self-review (plan vs ASTRAL_CODE_RULES)

| Rule | OK? |
|------|-----|
| §1.3 DRY | One stale helper pair for count + list + eligibility + batch |
| §2.1 config | Row **`freq_hrs`** is sole cadence source; CSE limits stay in **`INFLOW_CONFIG`** |
| §2.4 batch | **`last_scan_at` bump** after CSE unchanged |
| §2.6 state machine | **LIVE_PROMPTS** trigger unchanged |
| §3.3 imports | No new top-level cycles |
| §3.5 naming | **`inflow_discovery_freq_hrs`** on ctx matches dispatch column semantics |

No conflicts requiring plan revision.

---

## Build Review (Hedy)

**Publish ref:** `origin/sub/AST-813/AST-814-inflow-discovery-freq-hrs` @ `7aa989b`

| Stage | Summary |
|-------|---------|
| 1 | `count_stale`/`list_stale` use `freq_hrs`; `<= 0` returns all table rows; eligibility/describe wired to dispatch row |
| 2 | Removed `scan_interval_hours` and `dispatch_freq_hrs` from `INFLOW_CONFIG["discovery"]` |
| 3 | Dispatcher injects `ctx["inflow_discovery_freq_hrs"]`; debug describe passes row `freq_hrs`; roster batch reads ctx |

**QA (Betty):** Component tests per Stage 4 table — `freq_hrs=0` with fresh terms eligible; `freq_hrs=168` cadence; dispatcher debug cites `freq_hrs=`; config literal tests updated.

**Manual UAT:** Repro **somerset** / **LIVE_PROMPTS** / `freq_hrs=0` — Scheduled Actions **Available ≥ 1**, manual **Run** does not skip for `0 stale (scan_interval_hours=168)`.
