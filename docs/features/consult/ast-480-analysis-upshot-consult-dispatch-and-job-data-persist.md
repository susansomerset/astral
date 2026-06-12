# AST-480 — analysis_upshot consult dispatch and job_data persist

**Parent:** [AST-478 — Synthesize job analysis report (Estelle Opus upshot)](https://linear.app/astralcareermatch/issue/AST-478/synthesize-job-analysis-report-estelle-opus-upshot)  
**Publish ref (origin only):** `sub/AST-478/AST-480-analysis-upshot-consult-dispatch-and-job-data-persist`  
**Linear:** [AST-480](https://linear.app/astralcareermatch/issue/AST-480/analysis-upshot-consult-dispatch-and-job-data-persist-synthesize-job)

This ticket implements the **`analysis_upshot`** task: register it in **`TASK_CONFIG`**, add dispatch seeding for jobs in **`PASSED_LIKE`** (scored batch claim with **score floor**), route **`consult.run_consult_task`** to **`do_task`** for synthesis, persist the validated JSON report under **`job_data`**, transition **`PASSED_LIKE`** → **`RECOMMENDED`** on success, and **`PASSED_LIKE_RETRY`** on technical failure. It does **not** author Manage Tasks prompt prose (**AST-313**), JAR UI (**AST-481**), or artifact chains.

## Prerequisite (sibling blocker)

**AST-479** (**Hedy**) must land first on the integration line you merge under: **`JOB_STATES`** gains valid **`PASSED_LIKE_RETRY`** → **`PASSED_LIKE`** / **`PASSED_LIKE`** entry, **`RECOMMENDED`** with legal priors from **`PASSED_LIKE`**, **`grade_like.pass_state` → `PASSED_LIKE`**, and **`BUILD_ARTIFACTS`** is **not** reachable from **`consult_like`**. If those invariants are missing, `tracker.transition_job_state` will reject targets or the pipeline will violate parent AC1/AC4.

**Before first implementation commit:** `grep` / config review confirms **`grade_like`** pass is **`PASSED_LIKE`** and **no** task **`pass_state`** is **`BUILD_ARTIFACTS`**. If not, stop and comment on **AST-480** — do not re-implement **AST-479** here.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add **`TASK_CONFIG["analysis_upshot"]`** (schema, phase/seq, entity_type, `requires_candidate_key`, `scored: True` for dispatch score-floor gating per **ASTRAL_CODE_RULES** pass_threshold vs score_floor; **no** `grading_mode` / grades). Add **`error_state`: `PASSED_LIKE_RETRY`**, **`pass_state`: `RECOMMENDED`** (success transition target after persistence). Add **`_DISPATCH_TASK_TRIGGER_SEED["analysis_upshot"]`** with **`trigger_state`: `PASSED_LIKE`**, **`entity_type`: `job`**. Extend **`DISPATCH_TASK_SEED_KEYS`** / seed mirror rules with **`analysis_upshot`**. If **AST-479** adds **`PASSED_LIKE`** to score-gated UI helpers, update **`PASSED_SCORE_GATED_STATES`** only as that ticket defines — **do not** duplicate **AST-479** edits. | utils |
| `src/data/database.py` | Add **`analysis_upshot`** row to **`_DISPATCH_TASK_SEED`**: `entity_type: job`, **`trigger_state`: `PASSED_LIKE`**, **`sort_by`: `latest_score`**, **`batch_call_mode`: 0** (same pattern as **`consult_like`** for scored claim). | data |
| `src/core/consult.py` | Extend **`_INPUT_STATE_TO_TASK`**: **`PASSED_LIKE`** and **`PASSED_LIKE_RETRY`** → **`analysis_upshot`**. Implement **`async def _run_analysis_upshot_batch(...)`** (or equivalent name) invoked from **`run_consult_task`** when **`task_key == "analysis_upshot"`**: for each entity, build live content, call **`do_task`**, on success merge write **`job_data`** then transition to **`RECOMMENDED`**; on **`do_task`** / prep / persistence failure transition **`PASSED_LIKE_RETRY`**. **`resolve_dispatch_task_config_key`**: identity for **`analysis_upshot`** is already handled if key not in consult map — **do not** add a bogus **`consult_*`** mapping. | core |

**Spikes / prompts:** Prompt text and Manage Tasks rows are **AST-313 / Susan**; this plan only fixes **`TASK_CONFIG`** structure and placeholders consistent with **`response_schema`**.

---

## Stage 1: Config + dispatch seed

**Done when:** `TASK_CONFIG["analysis_upshot"]` exists with a complete **`response_schema`** (top-level object types), **`error_state`**, **`pass_state`**, **`scored: True`**, `entity_type: job`, `requires_candidate_key: True`, phase/seq after **`grade_like`**. **`_DISPATCH_TASK_TRIGGER_SEED`** and **`database._DISPATCH_TASK_SEED`** both include **`analysis_upshot`** with **`trigger_state: PASSED_LIKE`** and **`sort_by: latest_score`**. **`_INPUT_STATE_TO_TASK`** maps **`PASSED_LIKE`** and **`PASSED_LIKE_RETRY`** to **`analysis_upshot`** (waiting on **AST-479** retry state name — must match **`JOB_STATES`** exactly).

1. In **`src/utils/config.py`**, add **`TASK_CONFIG["analysis_upshot"]`**:
   - **`response_format`**: `"json"`; define **`response_schema`** as an object dict (not **`jobs`** array — single-job synthesis). Minimum top-level keys, all required unless noted:
     - **`take_get`** / **`take_do`** / **`take_like`**: `{ "type": "str", "required": True }` — Estelle narrative for each consult phase (G/D/L “takes”).
     - **`whole_jd_upshot`**: `{ "type": "str", "required": True }`.
     - **`segment_upshots`**: `{ "type": "list", "required": True, "items_schema": { "segment_key": {"type": "str", "required": True}, "upshot": {"type": "str", "required": True} } }`.
     - **`candidate_questions`**: `{ "type": "list", "required": True, "items_schema": { "text": {"type": "str", "required": True} } }` — **items must be objects** (`_validate_response_schema` rejects bare strings in lists).
     - **`caveats`**: `{ "type": "list", "required": True, "items_schema": { "text": {"type": "str", "required": True} } }`.
   - Set **`pass_state`: `RECOMMENDED`**, **`error_state`: `PASSED_LIKE_RETRY`** (must match **AST-479** spellings).
   - Set **`scored`: `True`** so **`dispatch_task_key_is_scored`** applies **score_floor** at claim time (reuse LIKE **`latest_score`**; this task does **not** write a new score in **`transition_job_state`**).
   - Set **`entity_type`: `job`**, **`requires_candidate_key`: `True`**, **`agent_task`: `analysis_upshot`** (same string as dispatch key so **`do_task`** resolves this **`TASK_CONFIG`** entry).
   - Omit **`grading_mode`**, **`vectors`**, **`grades_key`**, **`rubric_artifact`**, **`pass_threshold`** (not used for grading; optional doc comment that score gating uses **DB** **`score_floor`** only).

2. In **`src/utils/config.py`**, add **`_DISPATCH_TASK_TRIGGER_SEED["analysis_upshot"]`** = `{ "trigger_state": "PASSED_LIKE", "entity_type": "job" }` per existing shape for job consult rows.

3. In **`src/data/database.py`**, add **`"analysis_upshot"`** to **`_DISPATCH_TASK_SEED`** mirroring **`consult_like`** scored pattern: **`"entity_type": "job"`, `trigger_state": "PASSED_LIKE"`, `sort_by": "latest_score"`, `batch_call_mode": 0**`.

4. In **`src/core/consult.py`**, set **`_INPUT_STATE_TO_TASK["PASSED_LIKE"] = "analysis_upshot"`** and **`_INPUT_STATE_TO_TASK["PASSED_LIKE_RETRY"] = "analysis_upshot"`** (retry state string must match **AST-479**).

⚠️ **Decision (Chuckles validation):** Persist validated `parsed_response` as a single merge into **`job_data`** under the key **`analysis_upshot`** (not `job_analysis_report`). **AST-481** consumes this key.

---

## Stage 2: Runner — live content, `do_task`, persist, transitions

**Done when:** For a job in **`PASSED_LIKE`** (or **`PASSED_LIKE_RETRY`**), **`run_consult_task`** runs **`analysis_upshot`**, calls **`do_task`** with **`ctx`** including **`job`**, merges **`analysis_upshot`** JSON into **`job_data`** on success, transitions to **`RECOMMENDED`**, and on technical failure transitions to **`PASSED_LIKE_RETRY`** without persisting upshot JSON.

1. In **`src/core/consult.py`**, add **`async def _run_analysis_upshot_batch(batch_id, entities, ctx, debug) -> Dict[str, int]`** following the summary shape **`_run_craft_job_resume_batch`** uses (`total_processed`, `total_passed`, `total_failed`, `total_errors`):
   - For **each** job dict in **`entities`** (batch size typically 1 for `batch_call_mode: 0` — keep loop for dispatcher contract):
     - `aid = job["astral_job_id"]`; re-fetch **`get_job(aid)`** if required for freshness.
     - Build **`live_content`** with a dedicated helper **`_prep_analysis_upshot_live_content(job, company, ctx)`** (same module, **async** if it uses coat-check reads):
       - Include **plain-text sections** derived from **`job["job_data"]`** (via **`tracker.get_job_data`** where coat-check applies): raw listing / joblist context, **`job_description`**, serialized **DO / GET / LIKE** grades+scores+notes using the same prefixes as **`render_verdict`** (`do`, `get`, `like` from **`TASK_CONFIG`** save_prefixes / known keys — list the exact keys read in code comments if non-obvious).
       - Append company website context via **`roster.get_company_data(company, "website_content")`** when company exists; if **required** website is missing and LIKE already required company, mirror **`render_verdict`** path: transition to **`NEED_WEBSITE_CONTENT`** and count as failure for this entity (or reuse existing guard — pick one code path and document in a one-line comment; do not silently send empty website).
     - **`task_cfg = TASK_CONFIG["analysis_upshot"]`**; build **`task_ctx = {**(ctx or {}), **"batch_entities": [job], "job": job, "batch_size": 1**}`** so **`do_task`** / chain resolution match **AST-372** job-first context.
     - **`result = await do_task(task_key="analysis_upshot", live_content=live_content, index=aid, ctx=task_ctx, debug=debug)`**.
     - If **`not result.get("success")`**: **`_transition_job_state_for_task("analysis_upshot", [aid], task_cfg["error_state"])`**; increment **errors**.
     - Else: let Anthropic/schema validation enforce shape; **`parsed = result["parsed_response"]`**. If **`parsed`** is not a **`dict`**, treat as failure → **`error_state`**.
     - On success: **`tracker.save_job_data(aid, {"analysis_upshot": parsed})`** then **`_transition_job_state_for_task("analysis_upshot", [aid], task_cfg["pass_state"])`** — **persist before transition** so **`RECOMMENDED`** only exists when JSON is saved. Increment **passed**.
   - Return aggregated summary counts.

2. In **`run_consult_task`**, add **`elif task_key == "analysis_upshot": return await _run_analysis_upshot_batch(batch_id, entities, ctx, debug)`** before the final **`else: unhandled`** branch.

⚠️ **Decision:** **`_transition_job_state_for_task`** is used with **`task_key`** **`"analysis_upshot"`**; with **`scored: True`** in **`TASK_CONFIG`** but **no** new score, pass **`score=None`** so **`tracker.transition_job_state`** does not overwrite **`latest_score`** (see **`_transition_job_state_for_task`** implementation — **verified** path for `normalized_score is None`).

---

## Stage 3: Verification pass (no test-tree edits)

**Done when:** `python3 -m py_compile` passes on all changed **`.py`** files; manual grep confirms **`analysis_upshot`** appears in both seed maps and **`DISPATCH_TASK_SEED_KEYS`** / trigger aggregation stays consistent with **`database.dispatch_task_seed_templates()`** (same-commit invariant per **AST-468** advisory).

1. Run **`python3 -m py_compile`** on **`src/utils/config.py`**, **`src/data/database.py`**, **`src/core/consult.py`**.
2. Grep **`BUILD_ARTIFACTS`** in **`src/utils/config.py`** and **`consult.py`** relevant paths — **`analysis_upshot`** must **not** introduce a new **`pass_state`** to **`BUILD_ARTIFACTS`**.

---

## Execution contract (for the developer agent)

Per **plan-astral**: execute stages in order; one commit per stage on **`dev-ada`** during **build-astral**, then cherry-pick commits whose subject includes **`AST-480`** to **`origin/sub/AST-478/AST-480-analysis-upshot-consult-dispatch-and-job-data-persist`**. Do not add files outside the table. **No** edits under **`tests/`** or **`ASTRAL_TEST_BIBLE`** (Betty).

---

## Self-Assessment

**Scope:** `Single-Component` — Delivers one dispatchable consult task and runner path across **config**, **dispatch seed**, and **`consult.py`**, without UI or artifact chain.

**Conf:** `Medium` — Pattern reuse from **`render_verdict`** / **`_run_craft_job_resume_batch`** is clear, but **AST-479** ordering and **`job_data`** key contract with **AST-481** need board-visible alignment.

**Risk:** `Medium` — Wrong state transitions or persistence order could strand jobs in **`PASSED_LIKE`** / **`RECOMMENDED`** incorrectly or violate the **BUILD_ARTIFACTS** UI-only gate from parent **AST-478**.

---

## Self-review against ASTRAL_CODE_RULES

- **§1.3 DRY:** Reuse **`do_task`**, **`tracker.save_job_data`**, **`_transition_job_state_for_task`**, coat-check readers — no second Anthropic entry point.
- **§2.1 config:** All literals in **`TASK_CONFIG`** / seeds; no env fallbacks.
- **§2.4 batch:** Dispatcher provides **`batch_id`**; use per-entity processing consistent with other **`batch_call_mode: 0`** paths; clear batch via dispatcher’s existing **`clear_job_batch`** flow (no bypass).
- **§2.6 state machine:** Only transitions defined in **`JOB_STATES`** after **AST-479**.
- **§3.3 imports:** Keep **`consult` ↔ `agent`** cycle discipline; no new upward imports from **data** into **external**.
- **§3.5 naming:** Verb-led helper **`_prep_analysis_upshot_live_content`**; dispatch key **`analysis_upshot`** matches **`TASK_CONFIG`** key.

---

## Review (AST-480 build)

- Branch: `sub/AST-478/AST-480-analysis-upshot-consult-dispatch-and-job-data-persist`
- Code + tests tip (**`review-astral`**): **`7047ae40`**
- Plan appendix (**Radia doc** cherry-picked to publish ref): **`452a7fd8`**

## Review

**Radia** · 2026-05-24 · three-dot diff `origin/dev…origin/sub/AST-478/AST-480-analysis-upshot-consult-dispatch-and-job-data-persist`

| | |
|--|--|
| **Tip reviewed** | `7047ae40d214ca65749b8822266328f8af37318b` |

**What’s solid**

- **`_run_analysis_upshot_batch`** prepends contextual listing + DO/GET/LIKE recap, calls **`do_task`**, validates **`parsed_response`**, **`tracker.save_job_data(..., {"analysis_upshot": parsed})`** before **`pass_state` → `RECOMMENDED`**; technical/schema failures funnel to **`PASSED_LIKE_RETRY`** via **`TASK_CONFIG["analysis_upshot"]["error_state"]`**.
- Dispatch **`_DISPATCH_TASK_SEED`** row and **`PASSED_SCORE_GATED`** / **`PASSED_LIKE`** trigger alignment match the scored consult pattern; **`_INPUT_STATE_TO_TASK`** maps **`PASSED_LIKE`** / **`PASSED_LIKE_RETRY`** → **`analysis_upshot`** without touching **`BUILD_ARTIFACTS`**.
- **`JOB_STATES`** **`prior_states`** now include **`RECOMMENDED`** on **`CANDIDATE_REVIEW`**, **`CANDIDATE_APPLIED`**, and **`CANDIDATE_SKIPPED`**, completing the candidate graph deferred from isolated **AST-479**.
- Dispatcher **`finally`** clears **`job_batch`** (**`consult.py`** path does not bypass §2.4).
- Layers: **`json`** module import at top fits **§1.2**; no **`print`** / swallowed **`except`** in the reviewed hunks.

**Issues**

| Sev | Topic | Notes |
|-----|--------|--------|
| advisory | Batch summary **`total_failed`** | **`_run_analysis_upshot_batch`** always returns **`total_failed: 0`**; errors increment **`total_errors`**. Telemetry-only; clarify or align naming if dashboards care. |

**Recommended actions**

- None blocking for **`resolve-astral`**.

**Radia doc commit:** see tip of `origin/sub/AST-478/AST-480-analysis-upshot-consult-dispatch-and-job-data-persist` after push.

---

## Resolution

**Ada** · **2026-05-24** (`resolve-astral`, parent **AST-478**).

- **`review-astral`:** **fix-now** and **discuss** counts were **zero**. No product changes required from review.
- **Advisory · batch summary (`total_failed` vs `total_errors`):** Accepted as telemetry nuance — callers that need failure counts read **`total_errors`**; **`total_failed`** stays aligned with batch runner summary shape documented in Stage&nbsp;2. No code change unless a dashboard explicitly requires renaming (not gated for this ticket).
- **Verification:** Ada **`test-astral`** re-ran Betty’s narrowed manifest on **`7047ae40`** (pytest subset + frontend harness); **`452a7fd8`** is doc-only afterward.
- **Publish ref:** **`origin/sub/AST-478/AST-480-analysis-upshot-consult-dispatch-and-job-data-persist`** — **§9a** dry-runs vs **`origin/dev`** and **`origin/ftr/AST-478-synthesize-job-analysis-report-estelle-opus-upshot`** documented in Linear as **clean** before **User Testing**.
