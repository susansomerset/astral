# AST-466 — Absorb CONSULT_CONFIG: GAZER_CONFIG and TASK_CONFIG orchestration fields

**Linear:** [AST-466](https://linear.app/astralcareermatch/issue/AST-466/absorb-consult-config-gazer-config-and-task-config-orchestration-fields)  
**Parent:** [AST-376](https://linear.app/astralcareermatch/issue/AST-376/absorb-consult-config-into-gazer-config-task-config-and-dispatch-task-metadata)  
**Feature ref:** `sub/AST-376/AST-466-absorb-consult-config-gazer-config-and-task-config-orchestration-fields` (origin only)

## Summary

Introduce **`GAZER_CONFIG`** as the single source for gazer-only orchestration (**`validate_title`**, **`scrape_jd`**, **`gaze`** error/batch knobs). Extend **`TASK_CONFIG`** entries (**`qualify_job_listings`**, **`evaluate_jd`**, **`grade_do`**, **`grade_get`**, **`grade_like`**) with every orchestration field today read from **`CONSULT_CONFIG`** (states, thresholds, **`save_prefix`**, **`requires_company`**, **`error_states`**, **`min_job_title_length`**, **`min_jd_chars`**, **`not_ready_state`**, **`fallback_batch_size`**, **`rubric_artifact`** remains on **`TASK_CONFIG`** where it already exists). Rebuild **`CONSULT_CONFIG`** as a **shim** dict (same top-level keys and value shapes as today) assembled from **`GAZER_CONFIG`** + **`TASK_CONFIG`** so **`consult.py`**, **`gazer.py`**, and tests keep working without call-site edits in this ticket. Replace **`RUBRIC_ARTIFACT_KEYS`** construction to derive from the five consult **`TASK_CONFIG`** keys that carry **`rubric_artifact`**. Document the three-way split (**`TASK_CONFIG`** vs **`dispatch_task`** vs **`GAZER_CONFIG`**) and **`pass_threshold`** vs **`dispatch_task.score_floor`** in **`docs/ASTRAL_CODE_RULES.md`** §2.1.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | **`GAZER_CONFIG`**; **`TASK_CONFIG`** orchestration literals; **`CONSULT_CONFIG`** shim via **`_build_consult_config_shim()`**; **`RUBRIC_ARTIFACT_KEYS`** from five consult **`TASK_CONFIG`** rows | utils |
| `docs/ASTRAL_CODE_RULES.md` | **`GAZER_CONFIG`**, expanded **`TASK_CONFIG`**, shim narrative, **`pass_threshold`** vs **`score_floor`** bullets | docs |
| `src/core/agent.py` | Caller-chain / seven-segment API alignment (**`TOKEN_SOURCES`**, **`_chain_tokens_for_next_hop`**, **`_store_prompt_blocks`**) so consult + dispatch stacks match **`CALLER_*`** hop tokens (**AST-455** family); unavoidable once config + QA cleared **`[qa-handoff]`** | core |
| `docs/ASTRAL_TEST_BIBLE.md` | Narrowed manifests **§7.13w**, **`CALLER_*` / **`{$CACHE_BLOCK_*}`** regressions surfaced by **`test_config`** (**Betty**) | bible |
| `tests/component/` (agent, candidate admin UI, **`test_config`**, **`test_api_admin`** as surfaced) | **`[qa-handoff]`** alignment to product keyword-only **`agent`** signatures and **`preview_prompt(chain_context=…)`** | tests |

**Boundaries revisit (Radia discuss):** the original boundary line (“no **`src/core/`** … tests”) was the intent for *call-site migrations* (**`consult.py`**, **`gazer.py`**, **`dispatcher.py`**, **`database.py`**, **`api_admin.py`** deferred to sibling tickets). The **actual footprint** deliberately includes **`agent.py`** and focused component tests/Bible edits so the consult config move ships with token/preview reality from **`TOKEN_SOURCES`** and **`manage_tasks`** / chain preview paths — archival scope corrected here vs the pre-flight table.

---

## Stage 1: `GAZER_CONFIG` scaffolding

**Done when:** `GAZER_CONFIG` exists in `config.py` with literal values matching current behavior for gazer-owned steps; `ROSTER_CONFIG["gaze"]` is unchanged in this stage (still holds `error_state` only) — **do not** edit `gazer.py` here; duplication of `ERROR_GAZE` between `ROSTER_CONFIG["gaze"]` and `GAZER_CONFIG["gaze"]` is allowed only if both literals are identical and a one-line comment references the other as the semantic twin (utils cannot import utils in a circle — use mirrored literals + comment).

1. In `src/utils/config.py`, after **`ROSTER_CONFIG`** (before the current **`CONSULT_CONFIG`** header), add **`GAZER_CONFIG`** as a dict with exactly these keys:
   - **`"validate_title"`**: copy **`fallback_batch_size`**, **`pass_state`**, **`fail_state`** from the current **`CONSULT_CONFIG["validate_title"]`** literal values (`30`, **`VALID_TITLE`**, **`INVALID_TITLE`**).
   - **`"scrape_jd"`**: copy **`fallback_batch_size`**, **`pass_state`**, **`fail_state`**, **`error_states`** from current **`CONSULT_CONFIG["scrape_jd"]`**.
   - **`"gaze"`**: **`"error_state": "ERROR_GAZE"`** (same string as **`ROSTER_CONFIG["gaze"]["error_state"]`** today).

⚠️ **Decision:** **`ROSTER_CONFIG["gaze"]`** is left as-is because **`gazer.py`** is out of scope; **`GAZER_CONFIG["gaze"]`** documents the gazer-centric view for future consolidation (**AST-467**).

---

## Stage 2: Merge orchestration into `TASK_CONFIG`

**Done when:** Each listed **`TASK_CONFIG`** entry includes the orchestration keys with **byte-for-byte same values** as today’s **`CONSULT_CONFIG`** for the matching concern (no behavior change).

1. **`TASK_CONFIG["qualify_job_listings"]`** — add keys: **`fallback_batch_size`** (`30`), **`pass_state`** (`PASSED_JOBLIST`), **`fail_state`** (`FAILED_JOBLIST`), **`error_state`** (`ERROR_QUALIFY_JOB_LISTINGS`), **`min_job_title_length`** (`5`). (**`rubric_artifact`** already present — do not duplicate incorrectly.)

2. **`TASK_CONFIG["evaluate_jd"]`** — add: **`fallback_batch_size`** (`10`), **`pass_state`**, **`fail_state`**, **`error_state`**, **`min_jd_chars`**, **`not_ready_state`**.

3. **`TASK_CONFIG["grade_do"]`** — add: **`fallback_batch_size`** (`10`), **`pass_state`**, **`fail_state`**, **`error_state`**, **`save_prefix`** (`do`), **`pass_threshold`** (`6.0`). (**`rubric_artifact`** already present.)

4. **`TASK_CONFIG["grade_get"]`** — add: **`fallback_batch_size`**, **`pass_state`**, **`fail_state`**, **`error_state`**, **`save_prefix`** (`get`), **`pass_threshold`**.

5. **`TASK_CONFIG["grade_like"]`** — add: **`fallback_batch_size`**, **`pass_state`**, **`fail_state`**, **`error_state`**, **`save_prefix`** (`like`), **`pass_threshold`**, **`requires_company`** (`True`). (**`rubric_artifact`** already present.)

---

## Stage 3: `CONSULT_CONFIG` shim (same public shape)

**Done when:** **`CONSULT_CONFIG`** is still a module-level dict with keys **`qualify_job_listings`**, **`validate_title`**, **`scrape_jd`**, **`evaluate_jd`**, **`consult_do`**, **`consult_get`**, **`consult_like`**; each value is a dict exposing the same keys callers use today (including **`agent_task`** for the three consult steps).

1. Remove the large inline **`CONSULT_CONFIG = { ... }`** literal block.

2. Build **`CONSULT_CONFIG`** programmatically **in this file only** (no new modules), e.g. a function **`_build_consult_config_shim() -> dict`** that returns:
   - **`"qualify_job_listings"`**: subset view of **`TASK_CONFIG["qualify_job_listings"]`** including orchestration keys + **`rubric_artifact`** (match previous key set exactly).
   - **`"evaluate_jd"`**: subset from **`TASK_CONFIG["evaluate_jd"]`** (match previous key set).
   - **`"validate_title"`** / **`"scrape_jd"`**: **`dict(GAZER_CONFIG["validate_title"])`** and **`dict(GAZER_CONFIG["scrape_jd"])`** (or equivalent shallow copy).
   - **`"consult_do"`** / **`"consult_get"`** / **`"consult_like"`**: built from **`TASK_CONFIG["grade_do"]`**, **`["grade_get"]`**, **`["grade_like"]`** respectively, **plus** key **`"agent_task"`** set to **`"grade_do"`**, **`"grade_get"`**, **`"grade_like"`** so **`render_verdict`** indirection is unchanged.

3. Assign **`CONSULT_CONFIG = _build_consult_config_shim()`** at module init (after **`TASK_CONFIG`** and **`GAZER_CONFIG`** are fully defined).

⚠️ **Decision:** Shallow copies from **`TASK_CONFIG`** mean future mutation of **`CONSULT_CONFIG`** in tests keeps working if tests replace whole keys (e.g. **`monkeypatch.setitem(CONSULT_CONFIG, "consult_do", cfg)`**); prefer building fresh dicts per key from **`TASK_CONFIG`** slices, not storing references to the live **`TASK_CONFIG`** sub-dicts unless the plan executor verifies test compatibility.

---

## Stage 4: `RUBRIC_ARTIFACT_KEYS` / `RUBRIC_CRITERIA_ARTIFACT_KEYS`

**Done when:** **`RUBRIC_ARTIFACT_KEYS`** equals the same frozenset of artifact string keys as before this change (five consult rubrics); **`RUBRIC_CRITERIA_ARTIFACT_KEYS`** remains **`RUBRIC_ARTIFACT_KEYS | frozenset({"company_prefilter"})`**.

1. Replace the existing **`RUBRIC_ARTIFACT_KEYS`** comprehension over **`CONSULT_CONFIG.values()`** with an explicit derivation from **`TASK_CONFIG`** entries whose keys are **`qualify_job_listings`**, **`evaluate_jd`**, **`grade_do`**, **`grade_get`**, **`grade_like`**, collecting **`cfg["rubric_artifact"]`** when present (must yield exactly the five artifacts: **`joblist_rubric`**, **`jobdesc_rubric`**, **`do_rubric`**, **`get_rubric`**, **`like_rubric`**).

2. Keep **`RUBRIC_CRITERIA_ARTIFACT_KEYS`** definition immediately after, unchanged in meaning.

---

## Stage 5: `ASTRAL_CODE_RULES.md` (§2.1 and cross-refs)

**Done when:** Config section documents the split and the two numeric concepts without contradicting **`render_verdict`** or dispatch code.

1. In **`docs/ASTRAL_CODE_RULES.md`** §2.1 **Config blocks**, add **`GAZER_CONFIG`** bullet: gazer batch steps (**`validate_title`**, **`scrape_jd`**, **`gaze`**) orchestration (states, batch fallbacks, JD scrape error list).

2. Expand **`TASK_CONFIG`** bullet: task specs **and** job consult orchestration fields (pass/fail/error states, **`save_prefix`**, **`pass_threshold`**, readiness keys, **`requires_company`**, **`fallback_batch_size`** as config default before DB override).

3. Update **`CONSULT_CONFIG`** bullet: state it is a **shim** assembled from **`TASK_CONFIG`** + **`GAZER_CONFIG`** for backward compatibility until **AST-467**/**AST-468** remove consumers; **not** an independent source of truth after this ticket.

4. Add a short subsection or bullet **“`pass_threshold` vs `dispatch_task.score_floor`”**:
   - **`pass_threshold`** (on **`TASK_CONFIG`** for scored consult tasks): used by **`render_verdict`** / scoring to decide **pass vs fail grade outcome** after the model returns.
   - **`score_floor`** (on **`dispatch_task`** rows): used only at **batch claim / count** time to require **`latest_score >= score_floor`** for scored dispatch steps (**database** **`claim_job_batch`** / **`count_eligible_for_dispatch_task`** paths).
   - **Precedence:** they apply at **different lifecycle stages** — **neither overwrites the other**. If **`score_floor`** is **`NULL`** in DB, existing code normalizes to **`1.0`** for scored tasks; that is **dispatch eligibility**, not **`pass_threshold`**.

5. Scan §2.7 **render_verdict Pattern** — if it still says “Look up **`CONSULT_CONFIG`**” only, append one sentence: underlying values for job consult steps are authored in **`TASK_CONFIG`** and surfaced through the shim until removal.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — Touches the central config module and mandate doc; reshapes where orchestration literals live while preserving the public **`CONSULT_CONFIG`** shape for unmigrated callers.

**Conf:** `high` — Current **`CONSULT_CONFIG`** literals and **`TASK_CONFIG`** entries are in-repo; this is a structured move + shim with no new algorithms.

**Risk:** `Medium` — A wrong state name or missing key in the shim breaks **`render_verdict`** or gazer transitions; **`RUBRIC_ARTIFACT_KEYS`** drift would break candidate save validation.

---

## Plan vs ASTRAL_CODE_RULES (self-review)

| Section | Alignment |
|---------|-----------|
| §1.3 DRY | Single source in **`GAZER_CONFIG`** / **`TASK_CONFIG`**; **`CONSULT_CONFIG`** is derived, not a second literal source. |
| §2.1 Config | Orchestration literals live in named blocks; env/secrets rule unchanged. |
| §2.6 State machine | No new state names; copy exact strings from current config. |
| §3.3 Imports | No new cross-layer imports. |
| §3.5 Naming | **`GAZER_CONFIG`**, **`_build_consult_config_shim`**, **`CONSULT_CONFIG`** follow existing config naming. |

No conflicts requiring **`conf-!!-NONE`**.

---

## Execution contract (developer agent)

Per Astral workflow: execute stages in order; one commit per stage on **`dev-ada`** during **build-astral**, then cherry-pick to **`origin/sub/AST-376/AST-466-absorb-consult-config-gazer-config-and-task-config-orchestration-fields`** for commits whose subject includes **`AST-466`**. Do not edit **`dispatcher.py`**, **`database.py`**, **`api_admin.py`**, **`consult.py`**, or **`gazer.py`** in this ticket.

---

## Review (build)

- **Publish ref:** `sub/AST-376/AST-466-absorb-consult-config-gazer-config-and-task-config-orchestration-fields`
- **Commits:** `a0588cca` (implement), `2143a201` (plan stub)

## Review

Radia (`review-astral`) · **`git diff origin/dev...origin/sub/AST-376/AST-466-absorb-consult-config-gazer-config-and-task-config-orchestration-fields`** · Tip before this doc-only commit `1e30c65b`

### What's solid

- **`GAZER_CONFIG`** plus TASK orchestration literals on graded rows mirror retired **`CONSULT_CONFIG`** values; **`_build_consult_config_shim()`** returns fresh nested dicts (good for **`monkeypatch.setitem`**).
- **`RUBRIC_ARTIFACT_KEYS`** now derives from the five explicit consult **`TASK_CONFIG`** keys carrying **`rubric_artifact`**.
- **`docs/ASTRAL_CODE_RULES.md`** updates for shim narrative and **`pass_threshold`** vs **`score_floor`** read correctly against **`render_verdict`** / dispatch DB behavior.
- **`docs/ASTRAL_TEST_BIBLE.md`** additions match exercised manifest paths.

### Issues

| Severity | Topic | Detail |
|---------|-------|--------|
| **discuss** | Plan vs footprint | Combined plan declares no **`src/core/`** or **`tests/`** edits; diff includes substantive **`src/core/agent.py`** and multiple **tests/component** suites (prompt slot ABI / **`_chain_tokens_for_next_hop`** legacy compatibility). Probably required to land green tests; reconcile the **ticket/plan wording** (`validate-plan`/Linear) so archival scope stays honest. |
| **advisory** | Config churn | **`config.py`** repositioned **`BOARDS_*`/board helpers** relative to **`origin/dev`** alongside this ticket’s blocks; skim shows consolidation, not duplication—engineer ACK if intentional. |

### Recommended actions

- None **fix-now** against §5a rubric: no new silent **`except`**, **`getLogger`** misuse, UI hardcoding, or layer violations spotted in **`agent.py`/config skim.

### Severity counts

**fix-now:** 0 · **discuss:** 1 · **advisory:** 1

_(Radia Linear comment carries the **`docs(AST-466):`** commit SHA.)_
