# Batch prefilter evaluate phase (prefilter as batch process)

**Linear:** [AST-702](https://linear.app/astralcareermatch/issue/AST-702/batch-prefilter-evaluate-phase-prefilter-as-batch-process)  
**Parent:** [AST-700](https://linear.app/astralcareermatch/issue/AST-700/prefilter-as-batch-process)  
**Publish ref:** `origin/sub/AST-700/AST-702-batch-prefilter-evaluate-phase`  
**Depends on:** [AST-701](https://linear.app/astralcareermatch/issue/AST-701/fetch-website-scrape-phase-and-homepage-ready-state-prefilter-as-batch-process) (**`HOMEPAGE_READY`**, **`homepage_text`**, **`fetch_website`** scrape phase on **`origin/ftr/AST-700`** before **build-child** here)

Phase 2 of the AST-700 two-phase company prefilter pipeline: the existing **`prefilter`** dispatch task claims companies in **`HOMEPAGE_READY`**, assembles many prepared companies into **one** **`prefilter_company`** agent call (position-indexed rows, one response line per company), and applies per-company outcomes using today's rubric, encoded decode, inflow vs legacy routing, retries, and link persistence. Fully supersedes the monolithic **`WEBSITE_FOUND` → `prefilter_company`** scrape+evaluate path for **all** companies (Susan confirmed). Does **not** change rubric, prompt schema, or decode — orchestration and cutover only.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | **`ROSTER_CONFIG["prefilter"]["input_state"]` → `HOMEPAGE_READY`**; add evaluate-outcome transitions from **`HOMEPAGE_READY`**; add **`prefilter`** to **`_DISPATCH_BATCH_CALL_MODE_ONE`**; optional **`retry_state`** on **`HOMEPAGE_READY`** in **`COMPANY_STATES`** | utils |
| `src/core/roster.py` | Extract **`_apply_prefilter_decoded_company_outcome`** from **`prefilter_company`** post-decode logic; add **`_run_batch_company_prefilter`** (Pattern A scaffold) + **`prefilter_company_batch`**; remove monolithic **`WEBSITE_FOUND`/`WEBSITE_FOUND_RETRY` → `prefilter_company`** path from **`run_company_task`** | core |
| `src/core/consult.py` | Route **`entity_type == "company"`** + **`dispatch_task_key == "prefilter"`** to **`prefilter_company_batch`** (all claimed entities, **`batch_call_mode=1`**) | core |
| `src/data/database.py` | Migrate existing **`prefilter`** dispatch rows: **`trigger_state=HOMEPAGE_READY`**, **`batch_call_mode=1`**; remove obsolete **`prefilter`/`WEBSITE_FOUND_RETRY`** companion rows; drop **`("prefilter", "WEBSITE_FOUND_RETRY")`** from **`_RETRY_TASK_SEED`** | data |

**Out of scope:** homepage scrape (**AST-701**), rubric/prompt/decode changes, job-side batch consult, UI, tests (Betty manifest during **qa-child**).

---

## Stage 1: Config — dispatch trigger, batch mode, state graph

**Done when:** Admin defaults for new **`prefilter`** dispatch rows use **`trigger_state=HOMEPAGE_READY`** and **`batch_call_mode=1`**, and the company state graph lists all evaluate exits from **`HOMEPAGE_READY`**.

1. In **`src/utils/config.py`**, **`ROSTER_CONFIG["prefilter"]`**, change:
   ```python
   "input_state": "HOMEPAGE_READY",
   ```
   (Leave **`pass_state`**, **`fail_state`**, **`legacy_*`**, **`retry_state`**, **`error_state`**, **`pass_states`** unchanged.)

2. In **`src/utils/config.py`**, **`COMPANY_STATES`**, on the **`HOMEPAGE_READY`** entry added by **AST-701**, add:
   ```python
   "retry_state": "WEBSITE_FOUND_RETRY",
   ```
   (Mirrors **`JD_READY` → `JD_READY_RETRY`** — batch envelope / per-row technical failures from **`HOMEPAGE_READY`** route to re-scrape via **`fetch_website`**.)

3. In **`src/utils/config.py`**, **`ASTRAL_CONFIG["company_state_transitions"]`**, append:
   - `("HOMEPAGE_READY", "PREFILTER_PASSED")`
   - `("HOMEPAGE_READY", "PREFILTER_FAILED")`
   - `("HOMEPAGE_READY", "TO_WATCH")`
   - `("HOMEPAGE_READY", "IGNORE")`
   - `("HOMEPAGE_READY", "WEBSITE_FOUND_RETRY")`
   - `("HOMEPAGE_READY", "ERROR_PREFILTER")`
   - `("HOMEPAGE_READY", "CANNOT_READ_WEBSITE")`

4. In **`src/utils/config.py`**, add **`"prefilter"`** to **`_DISPATCH_BATCH_CALL_MODE_ONE`** so **`dispatch_task_admin_defaults("prefilter")`** sets **`batch_call_mode=1`**.

   ⚠️ **Decision:** Company prefilter batching uses **single consult pass for all claimed rows** (like **`evaluate_jd`** with **`batch_call_mode=1`**), **not** per-company **`_warm_then_gather`**. No consult chunk-exhaust split in this ticket — one API call per dispatch claim slice.

---

## Stage 2: Extract shared outcome application (roster)

**Done when:** A single helper performs everything **`prefilter_company`** does **after** successful decode (grades hydrated, pass/fail verdict, inflow vs legacy state pick, **`company_data`** persist, **`transition_company_state`**) and returns the final company state string.

1. In **`src/core/roster.py`**, add **`def _apply_prefilter_decoded_company_outcome(short_name: str, flat: Dict[str, Any], cfg: Dict[str, Any], ctx: Optional[Dict[str, Any]], *, nav_links_from_data: str = "") -> str`** immediately above **`async def prefilter_company`**.

2. Move logic from **`prefilter_company`** steps after **`flat = _flatten_prefilter_parsed(...)`** into the helper (unchanged semantics):
   - Import/consult calls: **`_render_pass_fail("prefilter_company", grades)`**, **`_hydrate_grade_reasons_from_rubric`**, **`_render_score`**, **`_company_used_inflow_prefilter`**, inflow vs **`legacy_pass_state`/`legacy_fail_state`** routing.
   - Build **`notes`**, **`data_to_save`** (`prefilter_grades`, `prefilter_company_notes`, optional **`prefilter_score`**, **`possible_job_links`**, **`culture_links_to_explore`**).
   - **`nav_links`**: persist **`nav_links_from_data`** when non-empty (batch path reads existing **`company_data.nav_links`** from **AST-701**; do not re-scrape).
   - **`save_company_data`**, **`transition_company_state(short_name, new_state)`**, **`return new_state`**.

3. On **`ValueError`** from hydration/score steps, **raise** (batch runner catches and routes via retry/error — same as **`process_fn`** exceptions in **`_run_batch_consult`**).

4. Refactor **`prefilter_company`** to call the helper after decode instead of inline step 5 — behavior unchanged for any remaining callers (coat-check **`_fetch_prefilter_notes`**, scripts).

   ⚠️ **Decision:** Keep **`prefilter_company`** as a public symbol for coat-check/adhoc paths; **cutover removes dispatch** from calling it on **`WEBSITE_FOUND`**, not delete the function.

---

## Stage 3: Readiness gating + batch runner (roster)

**Done when:** **`prefilter_company_batch(batch_id, companies, ctx, debug)`** splits not-ready companies before **`do_task`**, runs one encoded batch for the ready remainder, and returns **`{passed, failed, total, skipped?}`** with per-company **`debug_index`** lines on the agent hop.

1. In **`src/core/roster.py`**, add helpers:

   **`def _company_homepage_ready(company: Dict[str, Any]) -> bool`**
   - Read **`company_data.homepage_text`** (via nested dict on claimed row); return **`True`** when stripped length **> 0**.

   **`def _prefilter_batch_fail_dest(entity_state: Optional[str], cfg: Dict[str, Any]) -> Optional[str]`**
   - **`HOMEPAGE_READY`** (or state with **`COMPANY_STATES[st].retry_state`**) → **`cfg["retry_state"]`** (`**WEBSITE_FOUND_RETRY**`).
   - States already on **`WEBSITE_FOUND_RETRY`** → **`cfg["error_state"]`** (`**ERROR_PREFILTER**`).
   - Default → **`cfg["error_state"]`**.

   **`def _transition_prefilter_batch_failures(companies, cfg)`**
   - Group by **`_prefilter_batch_fail_dest(c.get("state"), cfg)`**; call **`transition_company_state(short_name, dest)`** per row (no job batch API).

2. Add **`async def _run_batch_company_prefilter(batch_id, companies, ctx, debug, batch_chunk_index=None)`** modeled on **`consult._run_batch_consult`**:
   - **`agent_task_key = "prefilter_company"`**; **`cfg = ROSTER_CONFIG["prefilter"]`**; **`orchestration = TASK_CONFIG["prefilter_company"]`** for pass/fail states used in counting.
   - Normalize **`batch_entities`**: for each company dict **`c`**, ensure **`{"astral_job_id": c["short_name"], "short_name": c["short_name"], "state": c.get("state"), "company_data": c.get("company_data") or {}}`**.
   - **`assemble(companies)`**:
     ```python
     blocks = []
     for c in companies:
         sn = c["short_name"]
         cd = c.get("company_data") or {}
         homepage = (cd.get("homepage_text") or "").strip()
         nav = cd.get("nav_links") or ""
         parts = [f"[company_id={sn}]", f"\n## Homepage Content\n{homepage}"]
         if nav:
             parts.append(f"\n## Navigation Links\n{nav}")
         blocks.append("\n".join(parts))
     return enumerate_array(
         "COMPANY PREFILTER ROWS", blocks,
         index_key="index", index_values=[f"{i:03d}" for i in range(len(companies))],
     )
     ```
   - **`do_task(task_key="prefilter_company", live_content=..., index=f"prefilter_company_batch_{batch_id}"` + optional **`_c{chunk}`**, **`ctx`** with **`batch_entities`**, **`batch_size`**, **`vector_labels=_vector_labels_from_ctx(ctx)`**, **`debug=debug`)**.
   - On **`do_task` envelope failure**: **`_transition_prefilter_batch_failures(companies, cfg)`** for all input rows; return **`{passed:0, failed:0, total:len(companies)}`**.
   - Decode path: use **`parsed["jobs"]`** from **`do_task`** result; reconcile **`astral_job_id`** (position = **`short_name`**) — same missing/fabricated/bad-grade handling as **`_run_batch_consult`**, but:
     - **`process_fn`**: call **`_apply_prefilter_decoded_company_outcome(short_name, response_job, cfg, ctx, nav_links_from_data=(input_company.get("company_data") or {}).get("nav_links") or "")`**; return **`new_state`**.
     - Missing/fabricated/bad-grade rows: **`_transition_prefilter_batch_failures`** on affected input companies.
   - **`debug_index`**: func **`roster.prefilter_company_batch`** / **`roster._run_batch_company_prefilter`**, identifier **`short_name`**, outcomes include decode state, grade count, persisted links count.
   - **`append_agent_response("company", short_name, agent_ref)`** for successfully processed companies (mirror job batch audit).
   - **Pass/fail counts**: **`passed`** when returned state ∈ **`cfg["pass_states"]`** (`**PREFILTER_PASSED**`, **`TO_WATCH`**); else **`failed`** (includes **`PREFILTER_FAILED`**, **`IGNORE`**).

3. Add **`async def prefilter_company_batch(batch_id, companies, ctx=None, debug=False) -> Dict[str, Any]`**:
   - Split **`not_ready`** = companies failing **`_company_homepage_ready`**.
   - For each **`not_ready`** row: **`transition_company_state(short_name, "CANNOT_READ_WEBSITE")`**, **`save_company_data(short_name, {prefilter_company_notes: "No homepage_text in company_data"})`**, **`debug_index`** outcome **`readiness skip -> CANNOT_READ_WEBSITE`** (mirror **`evaluate_jd_batch`** not-ready split).
   - If no ready companies: return **`{passed:0, failed:0, total:len(companies), skipped:len(not_ready)}`**.
   - Else **`await _run_batch_company_prefilter(batch_id, ready, ctx, debug)`**; merge **`skipped`** into return dict; **`total=len(companies)`**.

---

## Stage 4: Consult dispatch routing (cutover wiring)

**Done when:** Dispatcher **`batch_call_mode=1`** **`prefilter`** runs invoke **`prefilter_company_batch`** with the **full claimed entity list** and normalized summary counts.

1. In **`src/core/consult.py`**, **`run_consult_task`**, replace the bare **`run_company_task`** company branch with:

   ```python
   if entity_type == "company":
       tk = (dispatch_task_key or "").strip()
       if tk == "fetch_website":
           ...  # AST-701 (no-op here if not yet merged — do not implement in AST-702)
       if tk == "prefilter":
           r = await roster.prefilter_company_batch(batch_id, entities, ctx=ctx, debug=debug)
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
       return await roster.run_company_task(
           input_state, entities[0], batch_id, ctx, debug,
           dispatch_task_key=dispatch_task_key,
       )
   ```

2. Confirm dispatcher **`_run_unified`**: for **`entity_type != "job"`** with **`batch_call_mode=1`**, it already calls **`run_consult_task(..., entities, ...)`** once with all rows (no chunk split) — no **`dispatcher.py`** change unless a guard explicitly excludes company batch mode (grep and fix only if present).

---

## Stage 5: Remove monolithic dispatch path (roster cutover)

**Done when:** No dispatch path claims **`WEBSITE_FOUND`** for agent prefilter; scrape-only **`fetch_website`** (**AST-701**) owns **`WEBSITE_FOUND`** / **`WEBSITE_FOUND_RETRY`**.

1. In **`src/core/roster.py`**, **`run_company_task`**, **delete** the branch:
   ```python
   elif input_state in ("WEBSITE_FOUND", "WEBSITE_FOUND_RETRY"):
       result = await prefilter_company(...)
   ```
   Replace with a **`logger.warning`** + **`total_errors=1`** return if **`dispatch_task_key == "prefilter"`** and input_state is still **`WEBSITE_FOUND`** / **`WEBSITE_FOUND_RETRY`** (misconfigured row after migration) — do **not** silently call **`prefilter_company`**.

   ⚠️ **Decision:** AC7 **no ambiguous dual paths** — monolithic scrape+evaluate is dead for dispatch; coat-check may still call **`prefilter_company`** until a follow-on removes it.

---

## Stage 6: Database migration — dispatch rows

**Done when:** Existing candidates' **`prefilter`** dispatch rows claim **`HOMEPAGE_READY`** with **`batch_call_mode=1`**, and legacy **`prefilter`/`WEBSITE_FOUND_RETRY`** rows are gone.

1. In **`src/data/database.py`**, **`_RETRY_TASK_SEED`**, **remove** the tuple:
   ```python
   ("prefilter", "WEBSITE_FOUND_RETRY"),
   ```
   (**WEBSITE_FOUND_RETRY** is **`fetch_website`** territory after cutover.)

2. In **`_ensure_dispatch_task_schema`** (after table exists, with other one-time migrations), add idempotent SQL:
   ```python
   conn.execute(
       "UPDATE dispatch_task SET trigger_state = 'HOMEPAGE_READY', batch_call_mode = 1 "
       "WHERE task_key = 'prefilter' AND trigger_state IN ('WEBSITE_FOUND', 'WEBSITE_FOUND_RETRY')"
   )
   conn.execute(
       "DELETE FROM dispatch_task WHERE task_key = 'prefilter' AND trigger_state = 'WEBSITE_FOUND_RETRY'"
   )
   conn.commit()
   ```

3. Manual verification: for one candidate, confirm admin dispatch list shows **`prefilter`** → **`HOMEPAGE_READY`**, **`batch_call_mode=1`**, and **`fetch_website`** → **`WEBSITE_FOUND`** (**AST-701**).

---

## Self-Assessment

### Scope — **MAJOR-CHANGE**

Config cutover, new company batch runner, consult routing, dispatch DB migration, and removal of the **`WEBSITE_FOUND`** monolithic prefilter dispatch path — orchestration across roster + consult + data layers.

### Conf — **Medium**

Pattern is **`evaluate_jd_batch` / `_run_batch_consult`** with a company-specific batch scaffold; depends on **AST-701** landing **`HOMEPAGE_READY`/`homepage_text`** on **`ftr`** before implementation.

### Risk — **HIGH**

Wrong batch ID reconciliation, state routing, or cutover timing would mis-grade companies or leave **`WEBSITE_FOUND`** rows unroutable; contained to company prefilter pipeline, not job consult.

---

## Plan vs ASTRAL_CODE_RULES cross-check

- **§1.3 DRY:** Outcome logic centralized in **`_apply_prefilter_decoded_company_outcome`**; batch and legacy single-call paths share it.
- **§2.1 config:** Dispatch trigger, batch mode, and transitions live in **`config.py`** / DB migration — not hard-coded in dispatcher.
- **§2.4 batch processing:** Claim/release unchanged; batch function returns pass/fail/skip counts; **`batch_call_mode=1`** for multi-entity agent call.
- **§2.6 state machine:** Core chooses targets; **`transition_company_state`** only from roster helpers.
- **§2.8 coat-check:** Readiness failures do not store empty **`homepage_text`**; **`CANNOT_READ_WEBSITE`** with explicit notes.
- **§3.5 naming:** Dispatch key **`prefilter`**, agent task **`prefilter_company`**, holding state **`HOMEPAGE_READY`** — consistent with existing registry.

No conflicts requiring plan revision.

---

## Review

**Diff:** `origin/dev...origin/sub/AST-700/AST-702-batch-prefilter-evaluate-phase` @ `ba3ccc9`

**Built:** four `code(AST-702)` commits + `test(AST-702)` manifest on stacked AST-701 base (`merge-resume` from `origin/ftr/AST-700`). Evaluate phase: config cutover (`HOMEPAGE_READY` prefilter trigger, `batch_call_mode=1`, state graph), `_apply_prefilter_decoded_company_outcome` + `prefilter_company_batch` / `_run_batch_company_prefilter`, consult `prefilter` routing, monolithic `WEBSITE_FOUND` dispatch removal, dispatch DB migration + retry seed swap.

### What's solid

- **Plan fidelity:** All six stages — config (`input_state=HOMEPAGE_READY`, `retry_state`, transitions, `_DISPATCH_BATCH_CALL_MODE_ONE`), shared outcome helper, readiness split + Pattern-A batch runner, consult routing with `skipped` in error math, monolithic cutover (warning + `total_errors` on misconfigured `WEBSITE_FOUND`), DB migration + `_RETRY_TASK_SEED` swap to `fetch_website`.
- **§1.3 DRY:** Post-decode outcome centralized in `_apply_prefilter_decoded_company_outcome`; `prefilter_company` and batch path share it.
- **§2.1 / §2.6:** Dispatch trigger/batch mode from config; `_dispatch_trigger_state_for_task_key("prefilter")` reads `ROSTER_CONFIG["prefilter"]["input_state"]`; core owns transitions via roster helpers.
- **§2.4 batch:** `batch_call_mode=1` + full-entity consult pass; pass/fail/skip counts normalized; dispatcher test confirms `HOMEPAGE_READY`-only claim states.
- **§2.8 coat-check:** Not-ready rows → `CANNOT_READ_WEBSITE` with explicit notes; no empty `homepage_text` persistence.
- **§1.5.1 debug:** Batch start, per-company index lines, missing-ID detail, summary — gated on `debug=True`; mirrors job batch patterns.
- **§5d boundaries:** AST-701 scrape (`fetch_website`) preserved; no rubric/decode changes; AC7 dual-path removal enforced.

### Issues

| Severity | Location | Finding |
| --- | --- | --- |
| — | — | **None (fix-now / discuss).** |

### Recommended actions

| Priority | Action |
| --- | --- |
| — | Proceed to **resolve-child** — no engineer changes required. |
| Advisory | Diff vs `origin/dev` includes full AST-701 stack (expected on stacked sub branch before ftr→dev merge). |
| Advisory | `_run_batch_company_prefilter` parallels `_run_batch_consult` rather than calling it — plan-approved; future refactor could DRY if company/job batch scaffolds converge. |
| Advisory | `TestAst698PrefilterDebugPassthrough::test_prefilter_company_batch_forwards_debug_to_do_task` self-mocks `prefilter_company_batch` (tautological); Betty may want a real `do_task` debug assert in a follow-on — not blocking. |

## Resolution (`resolve-child`)

**Date:** 2026-06-16

**Against:** Radia `review-child` on `origin/sub/AST-700/AST-702-batch-prefilter-evaluate-phase` @ **`f747284`**.

**Product / plan**

- **fix-now:** None — review clean; no product commits in this pass.
- **Advisory (stacked AST-701 diff):** Expected on sub branch before ftr→dev merge; no change.
- **Advisory (parallel batch scaffold vs `_run_batch_consult`):** Plan-approved; no refactor in this ticket.
- **Advisory (tautological debug test):** Accepted; Betty may tighten in a follow-on — not blocking.

**§9a dry-run:** `origin/sub/AST-700/AST-702-batch-prefilter-evaluate-phase` merges cleanly into **`origin/dev`** and **`origin/ftr/AST-700-prefilter-as-batch-process`**.

**Manifest:** Betty manifest (15 tests) green @ **`ba3ccc9`** — no `[qa-handoff]`.
