# AST-822 — UAT: vet_inflow_discovery batch NEW companies with 000/001/002 indices

- **Linear:** [AST-822](https://linear.app/astralcareermatch/issue/AST-822/uat-vet-inflow-discovery-batch-new-companies-with-000001002-indices)
- **Parent:** [AST-815](https://linear.app/astralcareermatch/issue/AST-815/get-vet-inflow-discovery-to-work)
- **Publish ref:** `origin/sub/AST-815/AST-822-uat-vet-inflow-batch-indices`
- **UAT bug of:** [AST-815](https://linear.app/astralcareermatch/issue/AST-815/get-vet-inflow-discovery-to-work) — Susan re-test 2026-06-26 03:55 after AST-819 fix-uat
- **Related:** [AST-776](https://linear.app/astralcareermatch/issue/AST-776) (single-company vet), [AST-817](https://linear.app/astralcareermatch/issue/AST-817) / [AST-819](https://linear.app/astralcareermatch/issue/AST-819) (routing + IPv6 dedupe)

Susan re-tested **vet_inflow_discovery** after AST-819. With **batch_size > 1**, the dispatcher claims multiple eligible **NEW** companies but executes **one isolated `do_task` per slug** (`batch_call_mode=0` → per-entity `_warm_then_gather`; consult tail uses `entities[0]` only). Parent AC requires **one** Admin task assembling discovery blurbs with **`000|`**, **`001|`**, **`002|`** index prefixes and **`hit_index`** decode back to company rows.

**Root cause (two defects):**

1. **`batch_call_mode=0`** on **`vet_inflow_discovery`** dispatch rows (AST-776 default) — dispatcher never passes the full claimed entity list in one consult call.
2. **No batch vet runner** — `vet_inflow_discovery_company` always builds single-line live content and takes the first `results` row only; consult has no `vet_inflow_discovery` branch (unlike **`prefilter`** → **`prefilter_company_batch`**).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add **`vet_inflow_discovery`** to **`_DISPATCH_BATCH_CALL_MODE_ONE`** | utils |
| `src/data/database.py` | Idempotent **`UPDATE dispatch_task SET batch_call_mode = 1 WHERE task_key = 'vet_inflow_discovery'`**; AST-822 prompt migration for multi-hit **`results`** envelope | data |
| `src/core/roster.py` | **`vet_inflow_discovery_company_batch`**, blurb renumber helper, shared per-row outcome helper; thin single-company wrapper | core |
| `src/core/consult.py` | Company branch: **`dispatch_task_key == vet_inflow_discovery`** → batch runner (before **`run_company_task`** fallback) | core |

**Out of scope:** `src/core/dispatcher.py` (already honors DB **`batch_call_mode`**), **`inflow_discovery`** candidate CSE, **`inflow_resolve_website`**, Betty **`tests/`** / **`docs/test-bible/**`** (manifest only).

## Stage 1: Enable batch consult mode for vet_inflow_discovery (config)

**Done when:** **`dispatch_task_admin_defaults("vet_inflow_discovery")["batch_call_mode"] == 1`**; **`test_config`** vet dispatch defaults test updated expectation from **`0`** → **`1`**.

1. In **`src/utils/config.py`**, add **`"vet_inflow_discovery"`** to **`_DISPATCH_BATCH_CALL_MODE_ONE`** (~line 1282), same frozenset as **`prefilter`**.

2. Run:
   ```bash
   python3 -c "from src.utils import config as c; d=c.dispatch_task_admin_defaults('vet_inflow_discovery'); assert d['batch_call_mode']==1; print('ok')"
   ```

⚠️ **Decision:** Company vet batching uses **single consult pass for all claimed rows** (AST-702 prefilter pattern), **not** per-company **`_warm_then_gather`**. No consult chunk-exhaust split in this ticket.

## Stage 2: Migrate existing dispatch_task rows + multi-hit prompt (database)

**Done when:** Local DBs with **`vet_inflow_discovery`** dispatch rows have **`batch_call_mode=1`**; current **`vet_inflow_discovery`** agent prompt describes **N** pipe lines and **N** **`results`** rows keyed by **`hit_index`**.

1. In **`src/data/database.py`**, inside **`_ensure_dispatch_task_schema`** after the AST-702 prefilter block (~line 5718), add idempotent:
   ```sql
   UPDATE dispatch_task SET batch_call_mode = 1
   WHERE task_key = 'vet_inflow_discovery'
   ```
   (No **`trigger_state`** filter — all vet rows.)

2. Add module constants (after **`_AST776_VET_INFLOW_*`** block):
   - **`_AST822_VET_INFLOW_BATCH_MARKER = "MULTI-HIT VET BATCH (AST-822)"`**
   - **`_AST822_VET_INFLOW_USER_PROMPT_SEED`** — multiline string stating:
     - Live content: header **`Discovery hits (index|title|url|snippet)`** (or singular **`Discovery hit`** when one line) followed by one or more pipe lines **`000|title|url|snippet`**, **`001|…`**, etc.
     - Mechanical link-type scope unchanged from AST-776 (no fit/industry filtering).
     - **`agent_payload.results`** is an array with **one object per input line**, each **`{ "hit_index": <int matching 000→0, 001→1, …>, "action": "slug"|"ignore", "website": "…" }`**.
     - Include **`_AST822_VET_INFLOW_BATCH_MARKER`** in the seed text.

3. Add **`_apply_ast822_vet_inflow_discovery_prompt_migration(conn)`** (pattern **`_apply_ast776_vet_inflow_discovery_prompt_migration`**):
   - Load current **`agent_task`** row **`task_key = 'vet_inflow_discovery' AND current = 1`**.
   - If no row or **`user_prompt`** already contains **`_AST822_VET_INFLOW_BATCH_MARKER`**, return (idempotent).
   - Version forward via **`_save_agent_task_on_connection`**, replacing **`user_prompt`** with **`_AST822_VET_INFLOW_USER_PROMPT_SEED`** (preserve other prompt fields, **`run_next`**, **`agent_id`**).

4. Call **`_apply_ast822_vet_inflow_discovery_prompt_migration(conn)`** from **`_ensure_agent_task_schema`** alongside **`_apply_ast776_*`**.

5. Run **`python3 -m py_compile src/data/database.py`**.

⚠️ **Decision:** Prompt migration is **required** — AST-776 seed instructs a **one-element** **`results`** array; batch decode cannot work without multi-hit prose. Mechanical scope text stays; only input/output shape widens.

## Stage 3: Batch vet runner in roster.py

**Done when:** **`vet_inflow_discovery_company_batch(batch_id, companies, ctx, debug)`** issues **one** **`do_task(vet_inflow_discovery)`** for all ready companies, renumbers blurbs **`000`…`N-1`**, maps **`hit_index`** → per-company **`WEBSITE_FOUND`** / **`VET_FAILED`**; **`vet_inflow_discovery_company`** remains a thin single-entity wrapper (AST-776 regression).

1. In **`src/core/roster.py`**, add helper **`_renumber_vet_blurb_line(blurb: str, batch_index: int) -> str`** immediately after **`_discovery_blurb_line`** (~line 232):
   ```python
   def _renumber_vet_blurb_line(blurb: str, batch_index: int) -> str:
       parts = blurb.split("|", 3)
       if len(parts) >= 4:
           return f"{batch_index:03d}|{parts[1]}|{parts[2]}|{parts[3]}"
       return f"{batch_index:03d}|{blurb}"
   ```

2. Extract per-row outcome logic from **`vet_inflow_discovery_company`** into **`_apply_vet_inflow_result_row(short_name, row, cfg, debug, *, index: int, total: int) -> Dict[str, Any]`** returning **`{success, state, error}`** with the same transitions as today (**`ignore`/`reject` → VET_FAILED**; **`slug`/`accept` + website → WEBSITE_FOUND**; missing website / unknown action → failure dict). Keep existing **`debug_index`** / **`debug_detail`** calls, using **`index`/`total`** args.

3. Refactor **`vet_inflow_discovery_company`** to:
   - Build single-line live content unchanged (**`Discovery hit (index|title|url|snippet)\n{blurb}`**).
   - On success path, call **`_apply_vet_inflow_result_row`** instead of inline transition code.
   - Behavior and return shape **unchanged** for **`batch_size=1`** / direct unit tests.

4. Add **`async def vet_inflow_discovery_company_batch(batch_id, companies, ctx=None, debug=False) -> Dict[str, Any]`** (pattern **`prefilter_company_batch`** + **`_run_batch_company_prefilter`**):
   - **`cfg = INFLOW_CONFIG["vet"]`**; split **`ready`** (non-empty **`inflow_discovery_blurb`**) vs **`not_ready`**.
   - For each **`not_ready`**: log warning, count as error (no state transition) — mirror single-company missing-blurb behavior.
   - If **`not ready`**: return **`{"passed": 0, "failed": 0, "skipped": 0, "total": len(companies)}`** when all not ready; else proceed with **`ready`** only.
   - **`if debug`**: **`debug_index`** batch start with **`identifier=batch_id`**, **`outcome=f"batch start n={len(ready)}"`**; **`debug_detail`** listing **`short_names`**.
   - Assemble **`live_content`**:
     - Header: **`Discovery hit (index|title|url|snippet)`** when **`len(ready)==1`**, else **`Discovery hits (index|title|url|snippet)`**.
     - Body: **`"\n".join(_renumber_vet_blurb_line(blurb, i) for i, blurb in enumerate(ready_blurbs))`** where each blurb is read from **`company_data[cfg["blurb_data_key"]]`**.
   - **`if debug`**: **`debug_detail_block(live_content)`**.
   - **`do_task(task_key=cfg["task_key"], live_content=live_content, index=f"vet_inflow_discovery_batch_{batch_id}", ctx={**(ctx or {}), "batch_entities": ready, "batch_size": len(ready)}, debug=debug)`**.
   - On **`do_task`** failure: return **`passed=0, failed=0, skipped=0, total=len(companies)`** and count all **`ready`** as errors in consult math (no transitions).
   - Parse **`parsed_response.results`** list; build **`index_by_hit: Dict[int, dict]`** from rows with int **`hit_index`**.
   - For each **`i, company` in enumerate(ready)`**: look up **`row = index_by_hit.get(i)`**; if missing, log warning, increment error count, continue; else **`_apply_vet_inflow_result_row(short_name, row, cfg, debug, index=i+1, total=len(ready))`** and tally **`passed`** when **`state == cfg["pass_state"]`**, **`failed`** when **`state == cfg["fail_state"]`**, else error.
   - Return **`{"passed": passed, "failed": failed, "skipped": 0, "total": len(companies)}`**.

5. Run **`python3 -m py_compile src/core/roster.py`**.

## Stage 4: Consult routing for vet batch

**Done when:** **`run_consult_task(entity_type="company", dispatch_task_key="vet_inflow_discovery", entities=[…N…])`** invokes **`vet_inflow_discovery_company_batch`** with the **full** entity list and normalized summary counts (same error math as **`prefilter`**).

1. In **`src/core/consult.py`**, in the **`entity_type == "company"`** branch, **before** the **`return await roster.run_company_task(...)`** tail (~line 2009), add:

   ```python
   if (dispatch_task_key or "").strip() == "vet_inflow_discovery":
       r = await roster.vet_inflow_discovery_company_batch(
           batch_id, entities, ctx=ctx, debug=debug,
       )
       total = r.get("total", len(entities))
       passed = r.get("passed", 0)
       failed = r.get("failed", 0)
       skipped = r.get("skipped", 0)
       errors = max(0, total - passed - failed - skipped)
       return {
           "total_processed": total,
           "total_passed": passed,
           "total_failed": failed,
           "total_errors": errors,
       }
   ```

   Use **`(dispatch_task_key or "").strip()`** — same style as the **`prefilter`** guard (no new config import required).

2. **Do not** remove **`run_company_task`** vet routing — it remains the fallback when consult is invoked with a single entity via legacy paths; batch dispatch uses the new branch.

3. Run **`python3 -m py_compile src/core/consult.py`**.

## Stage 5: Regression verification + UAT checklist

**Done when:** Grep guards pass; manual batch assembly sanity passes; Betty manifest documented in review stub.

1. Confirm dispatcher needs **no code change**:
   ```bash
   rg -n "batch_call_mode" src/core/dispatcher.py | head -5
   ```
   With DB **`batch_call_mode=1`**, **`_run_unified`** already calls **`run_consult_task(..., entities, ...)`** once (~line 363).

2. Confirm consult company vet does **not** fall through to **`run_inflow_discovery_batch`**:
   ```bash
   rg -n "vet_inflow_discovery" src/core/consult.py
   ```
   Expect matches only in the new batch branch import path / guard (not candidate CSE).

3. Shell batch assembly sanity (build agent, before commit):
   ```bash
   python3 -c "
   from src.core.roster import _renumber_vet_blurb_line as r
   assert r('000|A|https://a|s', 2) == '002|A|https://a|s'
   assert r('bad', 1) == '001|bad'
   print('ok')
   "
   ```

4. **Betty test gate (do not edit tests in build):** document component scenarios:
   - **`TestAst776VetInflowDiscoveryCompany`** single-company paths (unchanged via wrapper)
   - **Update** **`test_consult_routes_company_vet_via_run_company_task`** → expect **`vet_inflow_discovery_company_batch`** (not **`run_company_task`**) when consult routes company vet
   - **New** batch test: mock **`do_task`** returns two **`results`** rows with **`hit_index` 0/1** → two transitions
   - **`test_config::test_vet_inflow_discovery_dispatch_admin_defaults`** → **`batch_call_mode == 1`**

5. **Susan UAT (after deploy):**
   - Candidate **somerset**, **vet_inflow_discovery** **`available ≥ 3`**, **`batch_size = 3`**, **`debug=True`**
   - Manual **Run** or AUTO tick
   - Logs: **one** vet Admin call with live content **`000|…`**, **`001|…`**, **`002|…`** — **not** three separate per-slug vet calls
   - Each company transitions **WEBSITE_FOUND** or **VET_FAILED** per model row
   - **`batch_size = 1`**: single **`000`** line, same outcomes as AST-817/819

## Self-Assessment

**Scope:** `Single-Component` — config default, one DB migration block, roster batch runner, consult guard; no dispatcher or CSE changes.

**Conf:** `high` — AST-702 prefilter batch pattern is the template; **`TASK_CONFIG["vet_inflow_discovery"]`** already declares **`hit_index`** in **`results`**; Susan's repro matches **`batch_call_mode=0`** + missing batch runner.

**Risk:** `Medium` — wrong **`hit_index`** mapping would transition the wrong company; **`batch_call_mode`** migration must land on staging DB before UAT; consult test expectation changes.

## ASTRAL_CODE_RULES self-review

| Rule | Plan alignment |
|------|----------------|
| §1.3 DRY | Shared **`_apply_vet_inflow_result_row`**; single wrapper delegates to same outcome helper |
| §2.1 config | **`batch_call_mode`** from **`_DISPATCH_BATCH_CALL_MODE_ONE`** + DB migration |
| §2.4 batch | One **`do_task`** per claim slice; **`batch_entities`** in ctx; index renumber **`000`… |
| §2.6 state machine | Transitions only in **`_apply_vet_inflow_result_row`** — **`NEW→WEBSITE_FOUND`** / **`NEW→VET_FAILED`** |
| §3.3 imports | No new cross-layer imports |
| §3.5 naming | **`vet_inflow_discovery_company_batch`** mirrors **`prefilter_company_batch`** |

No conflicts flagged.

## QA review stub (Betty @ Code Complete)

| Scenario | File | Expected test |
|----------|------|---------------|
| Single-company vet unchanged | `src/core/roster.py` | `::TestAst776VetInflowDiscoveryCompany::test_vet_*` |
| Consult routes vet batch | `src/core/consult.py` | Update `::test_consult_routes_company_vet_via_run_company_task` → batch mock |
| Multi-hit decode by index | `src/core/roster.py` | New `::TestAst822VetInflowDiscoveryBatch::test_batch_two_hits` (suggested) |
| Dispatch defaults batch_call_mode=1 | `src/utils/config.py` | `::test_vet_inflow_discovery_dispatch_admin_defaults` |

**Narrowed run (suggested):**
```bash
tests/component/core/test_roster.py::TestAst776VetInflowDiscoveryCompany \
tests/component/core/test_roster.py -k "Ast822 or consult_routes_company_vet" \
tests/component/utils/test_config.py -k "vet_inflow_discovery_dispatch"
```

## Build review stub

**Publish ref:** `origin/sub/AST-815/AST-822-uat-vet-inflow-batch-indices`

**Built:** @ `8580c9d` — `batch_call_mode=1` for `vet_inflow_discovery` (config + DB migration); AST-822 multi-hit prompt migration; `vet_inflow_discovery_company_batch` with `000/001/002` blurb renumber and `hit_index` decode; consult company branch routes vet before `run_company_task` fallback.

**Test-child (Hedy):** _(fill on test-child)_

**Susan UAT:**
- **`batch_size=3`** → one vet call, **`000/001/002`** live content
- Per-company **WEBSITE_FOUND** / **VET_FAILED** from **`hit_index`**
- **`batch_size=1`** → no regression from AST-817/819

Binding per **plan-child**: stages **1 → 5** in order; **one commit per stage** on epic worktree during **build-child**, publish each to **`origin/sub/AST-815/AST-822-uat-vet-inflow-batch-indices`**. Do not edit **`tests/`** or **`docs/test-bible/**`**. On ambiguity — **`🛑 Stage N blocked`** on **AST-815** parent; stop.
