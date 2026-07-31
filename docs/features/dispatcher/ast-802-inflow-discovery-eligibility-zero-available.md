<!-- linear-archive: AST-802 archived 2026-07-22 -->

## Linear archive (AST-802)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-802/inflow-discovery-eligibility-when-saved-search-terms-present-inflow  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-801 — Inflow discovery is not recognizing candidate ready for scanning  
**Blocked by / blocks / related:** parent: AST-801

### Description

## What this implements

Fix **inflow_discovery** dispatch eligibility and search-term persistence so a **LIVE_PROMPTS** candidate with saved company search terms (Susan confirmed Artifacts **Save** on local for **somerset**) shows **Available > 0** and manual **Run** executes discovery instead of skipping with **0 available (min_count=1)**. Reconcile the **company_search_terms** table with saved term text on the Artifacts save path (and startup migration where applicable) so eligibility reads stale table rows — not a legacy **artifacts.company_search_terms** blob alone. When eligibility is zero at dispatch time with **debug=True**, log an explicit reason per **AST-538**.

## Acceptance criteria

1. Susan's repro (**somerset**, **LIVE_PROMPTS**, fourteen saved terms on local): **inflow_discovery** shows **Available > 0** in Scheduled Actions and manual **Run** executes discovery instead of skipping with **0 available (min_count=1)**.
2. After Artifacts **Save**, the **company_search_terms** table contains the saved term rows for that candidate (not artifact-only), and eligibility returns **1** when at least one row is stale.
3. A component test covers the failure mode (saved terms present in product data but eligibility returning zero before fix) and asserts eligibility returns **1** (or batch proceeds) after the fix.
4. With **debug=True** and **available_count=0** at dispatch time, logs include an explicit eligibility-reason line per the backend debug contract (**AST-538**).
5. Existing **AST-525** per-term eligibility and discovery-batch tests remain green for candidates whose table rows are correctly synced and stale.

## Boundaries

* Does not change CSE query parameters, the discovery/vet split (**AST-775** / **AST-776**), or scan-interval config literals.
* Does not add new dispatch tasks or change **inflow_discovery** trigger state away from **LIVE_PROMPTS**.
* Does not revert per-term **last_scan_at** cadence (**AST-525**).
* Must not break **vet_inflow_discovery** or **inflow_resolve_website** company-dispatch eligibility.
* No React/UI changes unless the root cause is a broken Artifacts save/sync path.

## Notes for planning

* Eligibility helper: **count_candidate_inflow_discovery_eligible** / **count_stale_company_search_terms** (**AST-524**, **AST-525**). Save path: **apply_company_search_terms_save** in [**candidate.py**](<http://candidate.py>); Artifacts UI uses **PUT /data** with **artifacts.company_search_terms**.
* Susan's dump showed fourteen terms in **candidate_data** artifact blob while **available_count=0** — likely table desync or broken save sync.
* Primary layers: **data** (eligibility), **core/candidate** (sync), **core/dispatcher** (debug reason when zero).

## Git branch (authoritative)

Per **orientation** § Branch law: parent **ftr/AST-801-inflow-discovery-eligibility-zero-available**, child **sub/AST-801/<child-id>-<slug>**. Created at **dispatch-parent**.

### Comments

#### radia — 2026-06-25T05:20:03.718Z
### Review (`origin/dev...origin/sub/AST-801/AST-802-inflow-discovery-eligibility-zero-available` @ `e651c45`)

**fix-now:** none

**discuss:** none

**advisory:** none

**Plan fidelity:** Stages 1–3 match combined plan — per-candidate `reconcile_company_search_terms_from_artifact` (migration delegates); `ensure_company_search_terms_table_synced` on table reads + eligibility path; `describe_candidate_inflow_discovery_eligibility` with `eligibility:` reason strings; dispatcher `debug_detail` on `inflow_discovery` skip when `debug=True` and `run_count==0`. `replace=True` on artifact strip is justified in-code (deep-merge cannot delete nested keys).

**Rules:** §3.3 lazy import cycle break OK; §1.5.1 debug contract gated on `debug=True`; §2.4 stale predicate unchanged; no cross-layer violations in touched files.

**Tests:** Betty manifest covers Stage 4 — artifact-only reconcile → eligible, blob strip, dispatch count, wrong-state reason, PUT sync, dispatcher debug substring.

**Doc:** `docs/features/dispatcher/ast-802-inflow-discovery-eligibility-zero-available.md` § Radia review (2026-06-25)

**Counts:** 0 fix-now · 0 discuss · 0 advisory — clean.

#### betty — 2026-06-25T05:16:20.787Z
## QA test manifest (AST-802)

**Publish:** `origin/sub/AST-801/AST-802-inflow-discovery-eligibility-zero-available` @ `1d5b42c` (`merge-tests(AST-802): origin/tests 002e891`)

**Scope:** Legacy `artifacts.company_search_terms` → table reconcile at eligibility/read; `describe_candidate_inflow_discovery_eligibility`; dispatcher `debug_detail` on `inflow_discovery` zero-available skip.

### Manifest (test-child)

1. **Artifact reconcile eligibility** — `tests/component/data/database/test_dispatch_tasks.py::TestAst802InflowDiscoveryEligible` (4 tests): artifact-only → eligible + table rows; dispatch count path; describe reason string.

2. **PUT table sync** — `tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_put_company_search_terms_populates_table_without_persisting_blob`

3. **Dispatcher debug reason** — `tests/component/core/test_dispatcher.py::TestAst802InflowDiscoveryDebug::test_skip_emits_eligibility_reason_when_debug_true`

4. **Regression (required)** — `tests/component/data/database/test_dispatch_tasks.py::TestAst525InflowDiscoveryEligible`

```bash
.venv/bin/python -m pytest \
  tests/component/data/database/test_dispatch_tasks.py::TestAst802InflowDiscoveryEligible \
  tests/component/data/database/test_dispatch_tasks.py::TestAst525InflowDiscoveryEligible \
  tests/component/core/test_dispatcher.py::TestAst802InflowDiscoveryDebug \
  tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_put_company_search_terms_populates_table_without_persisting_blob \
  -q
```

**Pass criterion:** pytest green on manifest — not zero-arg harness / branch-lock gate.

**Note for test-child:** `TestAst802InflowDiscoveryEligible::test_reconcile_strips_legacy_artifact_blob` documents Stage 2 AC (strip blob after reconcile). On current publish ref it **fails**: `save_candidate_data` deep-merge retains `artifacts.company_search_terms` — fix `ensure_company_search_terms_table_synced` persistence in `src/core/candidate.py`.

**Bible shasums (`origin/sub/...` @ `1d5b42c`):**
- `docs/test-bible/data/database/dispatch_tasks.md`: `bbf5e652a4ccffb5ac60721766a31556fd02993e0a1a0eb05af40fb06ff73836`
- `docs/test-bible/ui/api/api_candidate.md`: `d66d1b97931b8185ee6b4da60b5bd35fa3b9fa0c9c1a575e924528defe9e4673`
- `docs/test-bible/core/dispatcher.md`: `5ba76d0c65962061908366b8ce03713aa51246284f65ba8c6fd6f56cfe273397`

— Betty

#### chuckles — 2026-06-25T05:10:11.634Z
Plan: [`docs/features/dispatcher/ast-802-inflow-discovery-eligibility-zero-available.md`](https://github.com/susansomerset/astral/blob/sub/AST-801/AST-802-inflow-discovery-eligibility-zero-available/docs/features/dispatcher/ast-802-inflow-discovery-eligibility-zero-available.md)

**Self-Assessment**
- **Scope:** Single-Component — `database.py`, `candidate.py`, and `dispatcher.py` only; artifact→table reconcile on eligibility/read paths plus `inflow_discovery` zero-available debug reason.
- **Conf:** Medium — reuses AST-524 migration insert shape and AST-525 stale-term predicates; Susan's repro points to artifact/table desync rather than cadence config.
- **Risk:** Medium — reconcile guarded by existing table rows; company vet/resolve eligibility paths untouched.

---

# AST-802 — inflow_discovery eligibility when saved search terms present

- **Linear (this ticket):** [AST-802](https://linear.app/astralcareermatch/issue/AST-802/inflow-discovery-eligibility-when-saved-search-terms-present-inflow)
- **Parent (coordination only):** [AST-801](https://linear.app/astralcareermatch/issue/AST-801/inflow-discovery-is-not-recognizing-candidate-ready-for-scanning)
- **Publish ref:** `origin/sub/AST-801/AST-802-inflow-discovery-eligibility-zero-available`

## Summary

Susan's repro (**somerset**, **LIVE_PROMPTS**, fourteen saved company search terms) shows **`inflow_discovery`** **Available = 0** and manual **Run** skips with **`0 available (min_count=1)`** even though **`candidate_data.artifacts.company_search_terms`** still holds term text. Shipped **AST-524/525** eligibility reads the **`company_search_terms`** table only; a legacy artifact blob without matching table rows yields zero stale terms. This ticket reconciles artifact → table on read and eligibility paths, strips the legacy blob after successful reconcile, and logs an explicit eligibility reason under **AST-538** when dispatch skips with **`debug=True`**.

⚠️ **Decision:** Reconcile at **eligibility count time** and **table-backed read time** (not only the one-time startup migration sweep), so candidates like **somerset** become eligible without manual DB surgery or a no-op re-save. **`vet_inflow_discovery`** / **`inflow_resolve_website`** company paths are untouched.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Per-candidate **`reconcile_company_search_terms_from_artifact`**; refactor startup migration to call it; **`describe_candidate_inflow_discovery_eligibility`** helper | data |
| `src/core/candidate.py` | **`ensure_company_search_terms_table_synced`** orchestration (reconcile + strip legacy artifact); call from table-backed read + before eligibility | core |
| `src/core/dispatcher.py` | When **`inflow_discovery`** skips for **`available < min_count`** with **`debug=True`**, emit eligibility reason via **`debug_detail`** | core |

**Tests:** Betty owns **`tests/`** — engineer does **not** edit test files. Stage 4 documents the component scenario for Betty's manifest (**AC 3**).

## Stage 1: Per-candidate artifact → table reconcile (data layer)

**Done when:** A candidate with legacy **`artifacts.company_search_terms`** text and **zero** **`company_search_terms`** table rows gets rows imported with **`last_scan_at = NULL`**; candidates who already have table rows are unchanged; startup migration still sweeps all candidates once per process.

1. In **`src/data/database.py`**, locate **`_search_term_lines_from_string`** (or equivalent line-split helper used by **`_migrate_company_search_terms_from_artifacts`**) — reuse it; do not duplicate split logic.

2. Add **`reconcile_company_search_terms_from_artifact(candidate_id: str) -> int`**:
   - Return **0** immediately if **`candidate_id`** is blank.
   - If **`COUNT(*)`** from **`company_search_terms`** for **`candidate_id`** is **> 0**, return **0** (table already authoritative).
   - Load candidate via **`get_candidate(candidate_id)`**; return **0** if missing.
   - Read **`(candidate.get("candidate_data") or {}).get("artifacts") or {}`**, key **`company_search_terms`**.
   - If not a non-empty string after strip, return **0**.
   - Split into normalized unique term lines (same rules as migration).
   - For each term, **`INSERT`** into **`company_search_terms`** with **`last_scan_at = NULL`**, **`created_at`/`updated_at = now`** (same SQL shape as **`_migrate_company_search_terms_from_artifacts`**).
   - Return count of rows inserted.

3. Refactor **`_migrate_company_search_terms_from_artifacts(conn)`** to iterate candidates and call **`reconcile_company_search_terms_from_artifact(cid)`** instead of inlining duplicate insert logic. Keep the one-time **`_company_search_terms_migration_swept`** flag behavior unchanged.

4. Manual verification (REPL, no commit dependency):

   ```python
   from src.data import database as db
   # seed candidate with artifact blob only, empty table, state LIVE_PROMPTS
   n = db.reconcile_company_search_terms_from_artifact("somerset")
   assert n > 0
   assert db.count_stale_company_search_terms("somerset", 168.0) > 0
   ```

### Self-review (Stage 1)

| Rule | OK? |
|------|-----|
| §2.4 batch | Stale predicate unchanged — reconcile sets **`last_scan_at = NULL`** |
| §1.3 DRY | Migration and runtime reconcile share one function |
| §3.3 imports | **`database → config`** only; no core imports |

---

## Stage 2: Core sync orchestration and eligibility wiring

**Done when:** **`count_candidate_inflow_discovery_eligible`** returns **1** for **LIVE_PROMPTS** candidates with legacy artifact-only terms after any code path that counts or displays terms; legacy **`artifacts.company_search_terms`** is removed from **`candidate_data`** after a successful reconcile import; **`apply_company_search_terms_save`** behavior unchanged.

1. In **`src/core/candidate.py`**, add **`ensure_company_search_terms_table_synced(candidate_id: str) -> None`**:
   - Call **`database.reconcile_company_search_terms_from_artifact(candidate_id)`**.
   - If return value **> 0**, load candidate, deep-copy **`candidate_data`**, delete **`artifacts.company_search_terms`** if present (create **`artifacts`** dict if needed), and persist with **`save_candidate_data(candidate_id, {"artifacts": updated_artifacts}, replace=False)`** — only when the key existed. Do not wipe other artifact keys.

2. At the top of **`count_candidate_inflow_discovery_eligible`** in **`database.py`**, add a lazy import and call:

   ```python
   from src.core.candidate import ensure_company_search_terms_table_synced
   ensure_company_search_terms_table_synced(candidate_id)
   ```

   ⚠️ **Decision:** Lazy import avoids **`database ↔ candidate`** cycle at module load (same pattern as **`agent.py`** / **`consult.py`**). **`database`** must not import **`candidate`** at top level.

3. In **`company_search_terms_joined_text`** and **`company_search_terms_lines_for_candidate`** in **`candidate.py`**, call **`ensure_company_search_terms_table_synced(candidate_id)`** before reading the table so Artifacts GET shows reconciled terms.

4. Do **not** change **`apply_company_search_terms_save`**, **`sync_company_search_terms_from_text`**, or **`api_candidate`** PUT order — they already sync table and strip blob on save.

5. Confirm **`count_eligible_for_dispatch_task`** candidate branch still delegates to **`count_candidate_inflow_discovery_eligible`** only (no **`freq_hrs`/`last_run_at`** gating for **`inflow_discovery`**).

### Self-review (Stage 2)

| Rule | OK? |
|------|-----|
| §2.1 config | Trigger state still **`INFLOW_CONFIG["discovery"]["dispatch_trigger_state"]`** |
| §2.6 state machine | No transition changes |
| §3.3 imports | Lazy import for cycle break |

---

## Stage 3: Eligibility reason helper + dispatcher debug (AST-538)

**Done when:** With **`debug=True`** on the dispatch task row and **`available_count=0`** at first loop iteration, logs include one **` | `** detail line naming the eligibility reason; with **`debug=False`**, no new contract lines.

1. In **`src/data/database.py`**, add **`describe_candidate_inflow_discovery_eligibility(candidate_id: str) -> tuple[int, str]`**:
   - Call **`ensure_company_search_terms_table_synced`** via the same lazy import as Stage 2 step 2.
   - If blank **`candidate_id`**: return **`(0, "eligibility: missing candidate_id")`**.
   - Load candidate; if missing: **`(0, "eligibility: candidate not found")`**.
   - Let **`trigger = INFLOW_CONFIG["discovery"]["dispatch_trigger_state"]`**.
   - If **`(cand.get("state") or "").strip() != trigger`**: return **`(0, f"eligibility: candidate state {(cand.get('state') or '').strip()!r} != {trigger!r}")`**.
   - Let **`scan_h = float(INFLOW_CONFIG["discovery"]["scan_interval_hours"])`**.
   - **`total = COUNT(*)`** from **`company_search_terms`** for candidate (add a small query or reuse **`list_company_search_terms`** length).
   - If **`total == 0`**: return **`(0, "eligibility: company_search_terms table empty")`**.
   - **`stale = count_stale_company_search_terms(candidate_id, scan_h)`**.
   - If **`stale == 0`**: return **`(0, f"eligibility: {total} table row(s) but 0 stale (scan_interval_hours={scan_h})")`**.
   - Return **`(1, "")`**.

2. Refactor **`count_candidate_inflow_discovery_eligible`** to call **`describe_candidate_inflow_discovery_eligibility`** and return the int half (keep existing signature).

3. In **`src/core/dispatcher.py`** **`_run_dispatch_loop`**, inside the block **`if available < effective_min:`** when **`run_count == 0`** and **`debug`**:
   - If **`task_key == INFLOW_CONFIG["discovery"]["task_key"]`** (import **`INFLOW_CONFIG`** from **`src.utils.config`** if not already available in scope):
     - Call **`database.describe_candidate_inflow_discovery_eligibility(task.get("candidate_id") or "")`**.
     - **`logger.debug_detail(reason_string)`** when reason string is non-empty (after the existing **`debug_index`** / first **`debug_detail`** for skip — append as additional **` | `** line, do not replace **`available=`** detail).

4. Do **not** add eligibility debug for other task keys in this ticket.

### Self-review (Stage 3)

| Rule | OK? |
|------|-----|
| §1.5.1 debug | Contract lines only when **`debug=True`** |
| §1.4 magic numbers | **`scan_interval_hours`** from **`INFLOW_CONFIG`**, not inline **168** |

---

## Stage 4: QA handoff note (Betty — AC 3)

**Done when:** Linear comment or build review stub documents the component scenario below; engineer does **not** commit test files.

Post **[qa-handoff]** only if Betty's existing **AST-525** manifest does not cover this scenario after product land. Intended new coverage (Betty):

| # | Scenario | Suggested location |
|---|----------|-------------------|
| 1 | Candidate **LIVE_PROMPTS**, **`artifacts.company_search_terms`** populated, **`company_search_terms`** table **empty** → **`count_eligible_for_dispatch_task`** returns **0** before reconcile helper is wired, **1** after **`ensure_company_search_terms_table_synced`** / eligibility count | `tests/component/data/database/test_dispatch_tasks.py` (new **`TestAst802InflowDiscoveryEligible`**) |
| 2 | Same fixture → **`PUT /api/candidates/:id/data`** with **`artifacts.company_search_terms`** still populates table and does not persist blob | `tests/component/ui/api/test_api_candidate.py` |
| 3 | Dispatcher skip with **`debug=True`**, **`task_key=inflow_discovery`**, **`available_count=0`** emits eligibility reason substring (e.g. **`eligibility:`**) | `tests/component/core/test_dispatcher.py` |

Existing **AST-525** roster/dispatch tests must remain green (**AC 5**).

---

## Execution contract (for the developer agent)

Execute stages **1 → 4** in order. One commit per stage on epic worktree, then publish each to **`origin/sub/AST-801/AST-802-inflow-discovery-eligibility-zero-available`**. Blocking questions → parent **AST-801** with 🛑 format from **plan-child**.

## Self-Assessment

**Scope:** `Single-Component` — Touches **`database.py`**, **`candidate.py`**, and **`dispatcher.py`** only; reconciles search-term storage desync and adds **`inflow_discovery`** zero-available debug reason.

**Conf:** `Medium` — Reuses **AST-524** migration insert shape and **AST-525** eligibility predicates; lazy-import cycle break is established pattern; Susan's repro strongly suggests artifact/table desync rather than cadence misconfiguration.

**Risk:** `Medium` — Incorrect reconcile could duplicate terms (mitigated by **`COUNT(*) > 0`** guard) or strip artifact before table write (mitigated by strip-only-after-**`insert_count > 0`**); company inflow dispatch paths are not modified.

## Self-review (plan vs ASTRAL_CODE_RULES)

| Rule | OK? |
|------|-----|
| §1.3 DRY | Single reconcile function shared by migration + runtime |
| §2.1 config | **`INFLOW_CONFIG`** literals only |
| §2.4 batch | Stale term SQL unchanged |
| §2.6 state machine | Read-only on candidate/company states |
| §3.3 imports | Lazy **`database → candidate`** import |
| §3.5 naming | Existing helper names extended, no new task keys |

No conflicts requiring plan revision.

---

## Build Review (Hedy)

**Publish ref:** `origin/sub/AST-801/AST-802-inflow-discovery-eligibility-zero-available`

| Stage | Summary |
|-------|---------|
| 1 | `reconcile_company_search_terms_from_artifact` in `database.py`; migration sweep delegates per candidate |
| 2 | `ensure_company_search_terms_table_synced` in `candidate.py`; table reads + eligibility count reconcile before stale check |
| 3 | `describe_candidate_inflow_discovery_eligibility`; dispatcher `debug_detail` reason on `inflow_discovery` skip |

**QA (Betty):** Component tests per Stage 4 table — artifact-only terms → eligible after reconcile; PUT sync; dispatcher debug reason line.

**Manual UAT:** Repro **somerset** / **LIVE_PROMPTS** — Scheduled Actions **Available > 0** after reload; manual **Run** executes discovery; **debug=True** skip shows `eligibility:` reason when still zero.

---

## Radia review (2026-06-25)

**Diff:** `origin/dev...origin/sub/AST-801/AST-802-inflow-discovery-eligibility-zero-available` @ `473cffe`  
**Product commits:** `16d9c36` reconcile + eligibility + dispatcher debug · `473cffe` strip-after-reconcile fix  
**Tests:** Betty manifest @ `002e891` / `merge-tests` @ `1d5b42c`

### What's solid

| Area | Notes |
|------|-------|
| Stage 1 — reconcile | `reconcile_company_search_terms_from_artifact` shares insert shape with migration; `COUNT(*) > 0` guard prevents duplicates; startup sweep delegates per candidate. |
| Stage 2 — sync | `ensure_company_search_terms_table_synced` on table reads + via `describe`; lazy `database → candidate` import avoids load-time cycle (§3.3). |
| Stage 3 — debug | `describe_candidate_inflow_discovery_eligibility` returns structured `eligibility:` reasons; dispatcher emits extra `debug_detail` only when `debug=True`, `run_count==0`, and `task_key=inflow_discovery` (§1.5.1). |
| Config / batch | `INFLOW_CONFIG` for trigger state, scan interval, task key — no inline magic numbers; stale-term SQL unchanged (§2.4). |
| Scope | No vet/resolve company paths touched; `apply_company_search_terms_save` unchanged. |
| Tests + bible | Stage 4 scenarios covered — artifact-only → eligible, blob strip, dispatch-task count, wrong-state reason, PUT sync, dispatcher debug substring. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| — | — | None. |

### Recommended actions

| Action | Owner |
|--------|-------|
| None blocking | — |

**Counts:** 0 fix-now · 0 discuss · 0 advisory

**Outcome:** Clean — Susan UAT on **somerset** / **LIVE_PROMPTS** repro per plan.

— Radia

---

## Resolution (Hedy)

**Date:** 2026-06-25  
**Linear:** [AST-802](https://linear.app/astralcareermatch/issue/AST-802) (**Review Posted → User Testing**)

Radia review clean — **0 fix-now**, **0 discuss**, **0 advisory**. No product delta; publish tip @ `e651c45` (`docs(AST-802): Radia review — clean`).

**§9a:** `origin/sub/AST-801/AST-802-inflow-discovery-eligibility-zero-available` merges cleanly into **`origin/dev`** and **`origin/ftr/AST-801-inflow-discovery-eligibility-zero-available`**.

— Hedy
