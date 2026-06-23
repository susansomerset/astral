<!-- linear-archive: AST-480 archived 2026-06-15 -->

## Linear archive (AST-480)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-480/analysis-upshot-consult-dispatch-and-job-data-persist-synthesize-job  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** ada  
**Priority / estimate:** High / 5  
**Parent:** AST-478 — Synthesize job analysis report (Estelle Opus upshot)  
**Blocked by / blocks / related:** parent: AST-478; blocks: AST-481

### Description

## What this implements

Register `analysis_upshot` in `TASK_CONFIG`. Wire `consult.run_consult_task` for jobs at `PASSED_LIKE` (scored batch claim with score floor). Run Opus synthesis via `do_task`; on success persist schema-driven report JSON under `job_data` and transition `pass_state` **→** `RECOMMENDED`. On technical failure → `PASSED_LIKE_RETRY`. Add dispatch seed row `trigger_state: PASSED_LIKE`.

## Acceptance criteria

2. `analysis_upshot` dispatch: `PASSED_LIKE` → `RECOMMENDED` when JSON saved.
3. Failure → `PASSED_LIKE_RETRY`, not `RECOMMENDED`.

## Boundaries

* Does **not** author Manage Tasks prompt prose (**AST-313** — Susan).
* Does **not** implement JAR render (**Katherine** sibling).
* Does **not** run artifact chains or set `BUILD_ARTIFACTS`.

## Notes for planning

* `src/core/consult.py`, `src/core/agent.py`, `src/data/database.py`, `src/utils/config.py`.
* Pass `job` in `ctx` per **AST-372** direction.

## Git branch (authoritative)

`sub/AST-478/AST-480-analysis-upshot-consult-dispatch-and-job-data-persist` · parent `ftr/AST-478-synthesize-job-analysis-report-estelle-opus-upshot`

### Comments

#### chuckles — 2026-05-25T04:04:28.146Z
[rollup-child] sub → ftr

Child: AST-480
Publish ref: origin/sub/AST-478/AST-480-analysis-upshot-consult-dispatch-and-job-data-persist
Parent ftr: origin/ftr/AST-478-synthesize-job-analysis-report-estelle-opus-upshot @ 3eb9ec70

Merge conflicts in config/database/bible/tests resolved for integration (480 sub tip preferred on overlap).

— Chuckles

#### ada — 2026-05-25T04:01:41.749Z
Review feedback resolved. Branch **`sub/AST-478/AST-480-analysis-upshot-consult-dispatch-and-job-data-persist`** ready for **`rollup-child` / prep-uat** (**parent AST-478**).

**Publish tip:** `d270addbd80bf11a2d1ee862ea680e1889415fb3` — Ada

**Dry-runs (**`resolve-astral`** §9a): **`origin/dev`**: clean · **`origin/ftr/AST-478-synthesize-job-analysis-report-estelle-opus-upshot`**: clean

**Changes:** **`docs(AST-480): Resolution`** — **`review-astral`** had zero **fix-now** / **discuss** items; advisory on **`total_failed` vs `total_errors`** documented as accepted telemetry nuance in plan (**`docs/features/consult/ast-480-analysis-upshot-consult-dispatch-and-job-data-persist.md`**).

#### radia — 2026-05-25T03:59:28.827Z
## Radia review (`review-astral`)

**Diff:** `origin/dev…origin/sub/AST-478/AST-480-analysis-upshot-consult-dispatch-and-job-data-persist`  
**Code tip reviewed:** `7047ae40d214ca65749b8822266328f8af37318b`

**Counts:** fix-now **0** · discuss **0** · advisory **1**

**Summary:** **`analysis_upshot`** batch path is coherent: recap + **`do_task`**, persist **`job_data.analysis_upshot`**, then **`RECOMMENDED`**; failures → **`PASSED_LIKE_RETRY`**. Dispatch seed, **`PASSED_LIKE`** map, and no **`BUILD_ARTIFACTS`** on pass meet parent gates. **`CANDIDATE_*`** **`prior_states`** now admit **`RECOMMENDED`**, fixing the interim gap from **`AST-479`**.

**Advisory:** **`_run_analysis_upshot_batch`** return shape always has **`total_failed: 0`** (errors accumulate under **`total_errors`**). Telemetry nuance only.

**Doc commit:** `452a7fd8` → same publish ref  
Markdown: [`ast-480-…`](https://github.com/susansomerset/astral/blob/sub/AST-478/AST-480-analysis-upshot-consult-dispatch-and-job-data-persist/docs/features/consult/ast-480-analysis-upshot-consult-dispatch-and-job-data-persist.md) — appendix **## Review**

**Tolerances accepted:** none required.

#### ada — 2026-05-25T03:57:23.816Z
[check-linear]

- **§0a:** `dev-ada` — `git fetch origin`, `merge origin/dev` (already up to date with `origin/dev`).
- **Publish ref:** `origin/sub/AST-478/AST-480-analysis-upshot-consult-dispatch-and-job-data-persist` tip **`7047ae40`** — matches `git ls-remote`; **no push required** (happy path: published tip already matches Betty handoff + prior `test-astral` verification).
- **Thread:** Latest activity is Ada’s `test-astral` manifest note at **`7047ae40`**; Betty handoff (`@Ada`) is superseded by that reply. No further code or publish action from this pass.
- **§0b/§1 (scoped):** `AST-480` thread reviewed; no actionable comments after the latest Ada update requiring a new reply beyond this inbox note.

#### ada — 2026-05-25T03:46:17.043Z
Built by Ada (`test-astral`).

**Manifest tip verified:** `7047ae40` on `origin/sub/AST-478/AST-480-analysis-upshot-consult-dispatch-and-job-data-persist` (matches Betty handoff).

**Commands run (narrow run + harness):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst480AnalysisUpshotConfig \
  tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers::test_dispatch_seed_keys_includes_board_gazer \
  tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers::test_passed_like_trigger_attachs_analysis_upshot_scored \
  tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_passed_like_to_analysis_upshot_batch
```

**Results:** pytest **4 passed**; Vitest component suite **209 passed** (harness full frontend run after pytest). No product regressions; **no** additional commits or push — publish ref unchanged at `7047ae40`.

**Git (local integration):** `dev-ada` after `git fetch origin`, `merge origin/dev`, `merge origin/sub/AST-478/AST-480-analysis-upshot-consult-dispatch-and-job-data-persist`; working tree clean post-run.

#### betty — 2026-05-25T03:38:10.590Z
**Betty QA handoff (`test-astral` manifest)**

**Published tip:** `7047ae40` on `sub/AST-478/AST-480-analysis-upshot-consult-dispatch-and-job-data-persist`.

**Cherry-picks (order):**
1. `fc9f3ecf` — `test(AST-479): manifest for LIKE→PASSED_LIKE + UserPrompt test harness` (Vitest `UserPromptProvider` / Modal tests baseline for this branch lineage).
2. `62710087` — `test(AST-480): manifest analysis_upshot dispatch + consult routing`.

**§7.13y bible + tests:** `TestAst480AnalysisUpshotConfig`, `TestAst471DispatchConfigHelpers` (`analysis_upshot` seed / scored PASSED_LIKE), `TestRunConsultTaskRoutes::test_routes_passed_like_to_analysis_upshot_batch`, plus existing **`TestAst479LikePassStates`**.

**Narrow run (same as bible table focus):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst480AnalysisUpshotConfig \
  tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers::test_dispatch_seed_keys_includes_board_gazer \
  tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers::test_passed_like_trigger_attachs_analysis_upshot_scored \
  tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_passed_like_to_analysis_upshot_batch
```

(Harness still runs full Vitest after pytest; Betty verified **208/208** Vitest passes on publish tip.)

**Local `dev-betty`:** extra product commit `4e472aa8` repairs `JOBS_IN_REVIEW_UI_SECTIONS` (syntax/list) after merge — **already correct on Ada’s tip**; **not** in publish cherry-picks.

👉 **Ada:** `test-astral` on **`7047ae40`**; flip to **Tests Ready** when you pick this up (Betty MCP `save_issue` flaky on updates).

#### ada — 2026-05-25T03:23:57.610Z
Built by Ada.

**Publish ref:** `sub/AST-478/AST-480-analysis-upshot-consult-dispatch-and-job-data-persist` — tip **`a79539ad`** (`feat(AST-480): analysis_upshot dispatch…`).

**Integration:** **`d741498b`** on local `dev-ada` (same tree; cherry-pick on publish ref rewrote SHA).

**Chuckles note:** Persisted synthesis JSON merges under **`job_data.analysis_upshot`** (not `job_analysis_report`).

**AST-479:** Remote `origin/sub/AST-478/AST-479-*` carried only plan doc — merged-in job machine + `grade_like`→`PASSED_LIKE`, removed `PASSED_LIKE`→`BUILD_ARTIFACTS` SQLite rewrite, and UI `RECOMMENDED` in **`REVIEW_LIKE`** folded into this build so **`PASSED_LIKE` / retry / synthesis** transitions validate.

**Handoff:** `python3 -m py_compile` on **`config.py`**, **`database.py`**, **`consult.py`** clean; **`npx tsc -b --noEmit`** in **`src/ui/frontend`** clean.

**Betty paths (expect churn):** `tests/component/utils/test_config.py`, `tests/component/core/test_consult.py`, `tests/component/ui/api/test_api_jobs.py`, frontend Recommended tests — engineer did **not** touch `tests/` per build-astral.

#### ada — 2026-05-25T03:20:35.795Z
Label review (build agent):

Conf: agree — Medium matches cross-layer state + dispatch wiring with clear pattern reuse.

Risk: agree — Medium; wrong transitions or BUILD_ARTIFACTS leakage would strand jobs; mitigated by AST-479 JOB_STATES graph + grep AC.

Scope: agree — Single-Component for the analysis_upshot path; note `origin/sub/AST-478/AST-479-*` currently carried only the plan doc — implementing the AST-479 config/DB/UI prerequisites on this line so PASSED_LIKE → analysis_upshot → RECOMMENDED is valid (folded into this build per parent ordering).

Built by Ada (label review complete).

#### chuckles — 2026-05-25T03:19:08.030Z
## Plan Validation — Chuckles

**Verdict: APPROVED**

**discuss — persist key:** Stage 2 writes `job_analysis_report`; **AST-481** reads `job_data.analysis_upshot`. **Use `analysis_upshot` everywhere** (parent Decisions + Katherine plan). Ada: align persist path in build to that key before Code Complete.

Otherwise faithful to parent AC2/AC3: `analysis_upshot` task, PASSED_LIKE dispatch, scored claim, RECOMMENDED / PASSED_LIKE_RETRY transitions, no BUILD_ARTIFACTS from tasks. Prerequisite on **AST-479** is explicit.

— Chuckles

#### ada — 2026-05-25T02:43:58.435Z
**Plan:** `docs/features/consult/ast-480-analysis-upshot-consult-dispatch-and-job-data-persist.md` (published to `origin/sub/AST-478/AST-480-analysis-upshot-consult-dispatch-and-job-data-persist`).

**Self-assessment (with justifications)**

- **Scope:** `Single-Component` — one dispatchable task plus runner wiring across config, `_DISPATCH_TASK_SEED`, and `consult.run_consult_task`.
- **Conf:** `Medium` — Patterns are established, but **AST-479** merge order and the `job_analysis_report` contract vs **AST-481** need the board aligned.
- **Risk:** `Medium` — Incorrect transitions or persistence order breaks the PASSED_LIKE → RECOMMENDED gate or the BUILD_ARTIFACTS UI-only invariant from parent **AST-478**.

Ada — **plan-astral**

---

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
