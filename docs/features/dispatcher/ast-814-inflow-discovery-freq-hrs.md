<!-- linear-archive: AST-814 archived 2026-07-22 -->

## Linear archive (AST-814)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-814/wire-inflow-discovery-staleness-to-dispatch-task-freq-hrs-get-inflow  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-813 — Get inflow_discovery to work  
**Blocked by / blocks / related:** parent: AST-813

### Description

## What this implements

Minimal hotfix: wire **inflow_discovery** per-term staleness to `dispatch_task.freq_hrs` on the Scheduled Actions row end-to-end — eligibility (**Available**), dispatch `available_count`, and `run_inflow_discovery_batch` stale-term selection must share one interval. Remove **INFLOW_CONFIG** `scan_interval_hours` / hardcoded **168** from the discovery-inflow path; `freq_hrs = 0` means no staleness gate (all table rows eligible).

## Acceptance criteria

1. **somerset** / **LIVE_PROMPTS** / `freq_hrs = 0` / fourteen `company_search_terms` rows: Scheduled Actions **Available ≥ 1** and manual **Run** does **not** skip for `available=0` or `0 stale (scan_interval_hours=168)`.
2. **Available** on the list and `available_count` at dispatch start match for the same dispatch row (no **1** in admin → **0** at run drift).
3. With `freq_hrs > 0`, a term scanned within that interval is not eligible; lowering `freq_hrs` re-opens terms without redeploy.
4. Auto-mode and manual **Run** share the same eligibility rule (**min_count** unchanged).
5. With `debug=True` and skip, logs emit an `eligibility:` reason citing the applied `freq_hrs` (not config **168**).
6. Component tests cover `freq_hrs = 0` (all terms stale) and `freq_hrs > 0` cadence (Betty manifest).
7. A manual search of the codebase will NOT return a hit for `168` pertaining to discovery inflow — the value is database-driven, not config-driven.

## Boundaries

* No **AST-801** `search_term` entity-type rework.
* No **vet_inflow_discovery** / **inflow_resolve_website** changes unless this fix regresses them.
* No Artifacts UI or CSE tuning.

## Notes for planning

* Primary surfaces: `database.py` eligibility/count, `dispatcher.py` pass `freq_hrs` through, `roster.py` `run_inflow_discovery_batch`, `config.py` remove discovery `scan_interval_hours` usage.
* `freq_hrs <= 0`: treat all terms as stale (Susan's **somerset** repro).
* Company WATCH precedent: row `freq_hrs` when **> 0**, else no stale filter — adapt for search terms.
* Debug skip reasons per **AST-538**.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/AST-813-inflow-discovery-freq-hrs`, child `sub/AST-813/AST-814-inflow-discovery-freq-hrs`.

### Comments

#### radia — 2026-06-26T02:38:10.477Z
### Review — AST-814

**Diff:** `origin/dev...origin/sub/AST-813/AST-814-inflow-discovery-freq-hrs` @ `8ef14b1` (includes doc)
**Product:** `6015f9b` · `c9cc9c0` · `7aa989b` · tests `6a36a8a`

#### Plan fidelity (Stages 1–3)

- **Data:** `count_stale` / `list_stale` use `freq_hrs`; `<= 0` counts/lists all table rows (fixes prior inverted early-return). `describe_candidate_inflow_discovery_eligibility(candidate_id, freq_hrs)` wired; ineligible reason cites `freq_hrs=`, not `scan_interval_hours`. `count_eligible_for_dispatch_task` candidate branch passes `task["freq_hrs"]`.
- **Config:** `scan_interval_hours` / `dispatch_freq_hrs` removed from `INFLOW_CONFIG["discovery"]`. Remaining `scan_interval_hours` references are company WATCH/gaze only (expected).
- **Dispatch/roster:** `_dispatch_one` sets `ctx["inflow_discovery_freq_hrs"]`; debug skip passes row `freq_hrs` to describe; `run_inflow_discovery_batch` reads ctx.

#### ASTRAL_CODE_RULES

| Rule | OK |
|------|-----|
| §1.3 DRY | Shared stale helpers for count/list/describe/batch |
| §2.1 config | Row `freq_hrs` sole inflow cadence; CSE limits stay in config |
| §2.4 batch | Stale SQL unchanged when `freq_hrs > 0`; `last_run_at` still ignored |
| §2.6 state | LIVE_PROMPTS gate unchanged |
| §1.5.1 debug | Eligibility `debug_detail` on skip only; cites `freq_hrs=` |
| §3.3 imports | Lazy `database → candidate` in describe unchanged |

#### Tests (Betty manifest)

`TestAst814InflowDiscoveryFreqHrs`, dispatcher debug (`freq_hrs=168`), roster `freq_hrs=0` fresh-term CSE, config literal removal, AST-524 zero-semantics update — align with Stage 4 table.

#### Findings

**fix-now:** none

**discuss:** none

**advisory:** none

**Doc:** [ast-814-inflow-discovery-freq-hrs.md](https://github.com/susansomerset/astral/blob/sub/AST-813/AST-814-inflow-discovery-freq-hrs/docs/features/dispatcher/ast-814-inflow-discovery-freq-hrs.md#radia-review-2026-06-26) @ `8ef14b1`

**Outcome:** Clean — Hedy may proceed `resolve-child` (no product changes expected) or advance to epic UAT on **AST-813** (`somerset` / `freq_hrs=0` repro).

#### betty — 2026-06-26T02:36:15.199Z
## QA test manifest (AST-814)

**Publish:** `origin/sub/AST-813/AST-814-inflow-discovery-freq-hrs` @ `d506465` (`merge-tests(AST-814): origin/tests 6a36a8a`)

1. **`freq_hrs=0`**, LIVE_PROMPTS, two fresh table rows → `count_eligible_for_dispatch_task == 1`; stale helpers return both terms — `tests/component/data/database/test_dispatch_tasks.py::TestAst814InflowDiscoveryFreqHrs::test_freq_hrs_zero_eligible_and_lists_all_fresh_terms`

2. Same fixture, **`freq_hrs=168`** → eligible **0**; reason contains **`freq_hrs=168`**, not **`scan_interval_hours`** — `::test_freq_hrs_168_all_fresh_not_eligible`

3. Row **`freq_hrs: 0`** vs explicit **168** on helper — `::test_dispatch_task_freq_zero_overrides_fresh_exclusion`

4. Dispatcher debug skip cites **`freq_hrs=`** when all terms fresh — `tests/component/core/test_dispatcher.py::TestAst814InflowDiscoveryDebug::test_skip_cites_freq_hrs_when_all_terms_fresh`

5. Config literals removed — `tests/component/utils/test_config.py::TestAst525InflowDiscoveryConfig::test_discovery_config_has_no_scan_interval_literals`; `TestAst505InflowDiscoveryConfig::test_inflow_config_discovery_literals`

6. Roster batch reads ctx — `tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_freq_hrs_zero_searches_fresh_terms`

**Regression (required):** AST-525/802 eligibility + revised AST-524 stale helpers + AST-505 batch tests with **`inflow_discovery_freq_hrs: 168`** in ctx.

**Broken / revised this pass:** `TestAst524CompanySearchTermsTable` (`freq_hrs=0` → all rows); `TestAst525InflowDiscoveryConfig::test_scan_interval_hours_literal` removed; AST-505 batch ctx defaults documented in bible.

**Bible shasums (`origin/sub/...`):**
- `docs/test-bible/core/dispatcher.md` → `7758cb8cb3238f00ab1aac46a3591f71745f3b8dd78c9ad69f46505d40cf78ae`
- `docs/test-bible/core/roster.md` → `9f124af29275dde34035887526084f7e4368045ab484e41ba6379701fa484e5a`
- `docs/test-bible/data/database.md` → `1358bb71085e080232fd8ee4375844a4a4a3fbb0fe273b81f3d6b322e6b74ff0`
- `docs/test-bible/data/database/dispatch_tasks.md` → `bc64511ea0382072929b97c68cac5fd7f36facd634ca92d440ec64d5198445b3`
- `docs/test-bible/utils/config.md` → `6e2239f4a5e1ec3174b87990579b58dd87e520abc3e5d3a47a5f144f8217b3e5`

**Narrowed run:**

```bash
.venv/bin/python -m pytest   tests/component/data/database/test_dispatch_tasks.py::TestAst814InflowDiscoveryFreqHrs   tests/component/data/database/test_dispatch_tasks.py::TestAst802InflowDiscoveryEligible   tests/component/data/database/test_dispatch_tasks.py::TestAst525InflowDiscoveryEligible   tests/component/data/database/test_company_search_terms.py::TestAst524CompanySearchTermsTable::test_count_stale_company_search_terms   tests/component/data/database/test_company_search_terms.py::TestAst524CompanySearchTermsTable::test_list_stale_company_search_terms_ordered   tests/component/utils/test_config.py::TestAst525InflowDiscoveryConfig   tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_inflow_config_discovery_literals   tests/component/core/test_dispatcher.py::TestAst802InflowDiscoveryDebug   tests/component/core/test_dispatcher.py::TestAst814InflowDiscoveryDebug   tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_no_stale_terms_returns_zero_errors   tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_searches_only_stale_terms   tests/component/core/test_roster.py::TestAst505InflowDiscovery::test_run_batch_freq_hrs_zero_searches_fresh_terms   -q
```

Pass criterion: pytest green on manifest — not zero-arg harness / branch-lock gate.

#### hedy — 2026-06-26T02:29:26.377Z
Plan: `docs/features/dispatcher/ast-814-inflow-discovery-freq-hrs.md`
https://github.com/susansomerset/astral/blob/sub/AST-813/AST-814-inflow-discovery-freq-hrs/docs/features/dispatcher/ast-814-inflow-discovery-freq-hrs.md

**Scope:** Single-Component — `database.py`, `config.py`, `dispatcher.py`, `roster.py`; rewire inflow discovery staleness from config 168 to `dispatch_task.freq_hrs`.

**Conf:** high — ignored `freq_hrs` plus inverted `<= 0` stale helpers; WATCH row-freq precedent already in dispatcher/count paths.

**Risk:** Medium — wrong `freq_hrs <= 0` semantics could over- or under-run CSE; mitigated by one shared stale helper across count, list, describe, and batch.

---

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

---

## Radia review (2026-06-26)

**Diff:** `origin/dev...origin/sub/AST-813/AST-814-inflow-discovery-freq-hrs` @ `d506465`  
**Product commits:** `6015f9b` database · `c9cc9c0` config · `7aa989b` dispatcher/roster  
**Tests:** `6a36a8a` manifest + bible (Betty)

### What's solid

| Area | Notes |
|------|-------|
| Stage 1 — data | `count_stale` / `list_stale` take `freq_hrs`; `<= 0` returns all table rows (fixes inverted early-return); `describe_candidate_inflow_discovery_eligibility` requires row `freq_hrs`; reason cites `freq_hrs=`, not `scan_interval_hours`; `count_eligible_for_dispatch_task` candidate branch passes `task["freq_hrs"]`. |
| Stage 2 — config | `scan_interval_hours` and `dispatch_freq_hrs` removed from `INFLOW_CONFIG["discovery"]`; remaining `scan_interval_hours` hits are company WATCH/gaze only (§2.1). |
| Stage 3 — dispatch/roster | `_dispatch_one` injects `ctx["inflow_discovery_freq_hrs"]`; debug skip path passes row `freq_hrs` to describe; `run_inflow_discovery_batch` reads ctx, not config. |
| §1.3 DRY | Single stale-helper pair shared by count, list, describe, and batch. |
| §2.4 / §2.6 | Stale SQL unchanged when `freq_hrs > 0`; LIVE_PROMPTS gate unchanged; `last_run_at` still ignored for per-term cadence. |
| §1.5.1 debug | Eligibility reason on skip only; cites `freq_hrs=` — matches AST-802 narrow exception. |
| §3.3 | Lazy `database → candidate` import in describe unchanged; no new layer violations. |
| Tests + bible | `TestAst814InflowDiscoveryFreqHrs`, dispatcher debug, roster `freq_hrs=0` fresh-term CSE, config literal removal, AST-524 zero-semantics update. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| — | — | None. |

### Recommended actions

| Action | Owner |
|--------|-------|
| None blocking | — |

**Counts:** 0 fix-now · 0 discuss · 0 advisory

**Outcome:** Clean — Susan UAT on parent **AST-813** (`somerset` / `freq_hrs=0` repro).

— Radia

---

## Resolution (Hedy)

**Date:** 2026-06-26  
**Linear:** [AST-814](https://linear.app/astralcareermatch/issue/AST-814) (**Review Posted → User Testing**)

Radia review clean — **0 fix-now**, **0 discuss**, **0 advisory**. No product delta; publish tip @ `8ef14b1` (`docs(AST-814): Radia review — clean`).

**§9a:** `origin/sub/AST-813/AST-814-inflow-discovery-freq-hrs` merges cleanly into **`origin/dev`** and **`origin/ftr/AST-813-inflow-discovery-freq-hrs`**.

— Hedy
