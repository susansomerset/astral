# AST-796 — Config schedulable-key cutover: fetch_jd and retire keys

- **Linear (this ticket):** [AST-796](https://linear.app/astralcareermatch/issue/AST-796/config-schedulable-key-cutover-fetch-jd-and-retire-keys-3-task-config)
- **Parent (coordination only):** [AST-794](https://linear.app/astralcareermatch/issue/AST-794/3-task-config-updates-to-configpy)
- **Publish ref:** `origin/sub/AST-794/ast-796-config-schedulable-key-cutover-fetch-jd-retire-keys`

## Summary

Repo **`agent_task.json`** already catalogs **`fetch_jd`** and omits **`validate_title`** and **`gaze_board`**, but **`src/utils/config.py`** still exposes **`scrape_jd`** and **`validate_title`** as schedulable dispatch keys. This ticket aligns config schedulable catalogs, **`GAZER_CONFIG`**, and retired-key validation with the repo catalog: register **`fetch_jd`** at **`PASSED_JOBLIST`**, retire **`scrape_jd`**, **`validate_title`**, and **`gaze_board`** from admin save/create paths, and reject POST/PUT using retired keys with operator-facing errors. Runtime routing, DB row migration, and inline title screening wiring are **AST-797** — not this ticket.

⚠️ **Decision:** Rename the **`GAZER_CONFIG`** orchestration block from **`scrape_jd`** to **`fetch_jd`**, then add a one-line read alias **`GAZER_CONFIG["scrape_jd"] = GAZER_CONFIG["fetch_jd"]`** immediately after the dict literal so existing **`gazer.scrape_jd_batch`** call sites keep working until **AST-797** removes the alias and switches runtime to **`fetch_jd`**. Schedulable/admin surfaces use **`fetch_jd`** only; **`scrape_jd`** is retired for dispatch, not for gazer reads in this pass.

⚠️ **Decision:** Keep **`GAZER_CONFIG["validate_title"]`** orchestration literals in this ticket — mechanical title screening still runs via **`validate_title_batch`** until **AST-797** inlines it before **`qualify_job_listings`**. Only remove **`validate_title`** from schedulable catalogs and admin save eligibility.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | **`GAZER_CONFIG`**: rename **`scrape_jd`** → **`fetch_jd`** (+ transitional **`scrape_jd`** read alias); update module header comment. **`DISPATCH_SCHEDULABLE_TASK_KEYS`**: add **`fetch_jd`**, remove **`scrape_jd`** and **`validate_title`**. **`DISPATCH_RETIRED_TASK_KEYS`**: add **`scrape_jd`**, **`validate_title`**, **`gaze_board`**. Extend **`_RETIRED_DISPATCH_TASK_KEY_REPLACEMENTS`** / retired message helper. **`_dispatch_trigger_state_for_task_key`**, **`_dispatch_entity_type_for_task_key`**: **`fetch_jd`** @ **`PASSED_JOBLIST`**; drop schedulable branches for retired keys. | utils |

**Verify only (Betty / qa-child — engineer does not edit in build-child):**

| File | Change |
|------|--------|
| `tests/component/utils/test_config.py` | New **`TestAst796FetchJdSchedulableCutover`** (or extend **`TestAst471DispatchConfigHelpers`**) — **`fetch_jd`** schedulable defaults; retired keys rejected; **`gaze_board`** / **`validate_title`** / **`scrape_jd`** absent from **`DISPATCH_SCHEDULABLE_TASK_KEYS`** |
| `tests/component/ui/api/test_api_admin.py` | POST **`scrape_jd`** / **`validate_title`** / **`gaze_board`** → 400 retired message; **`task_keys`** includes **`fetch_jd`**, excludes retired keys |

**No changes expected:** `src/ui/api/api_admin.py` (already filters **`DISPATCH_RETIRED_TASK_KEYS`** on **`list_dtasks`**, **`dispatch_task_keys`**, and create/update via **`dispatch_task_key_retired_message`**), `src/core/gazer.py`, `src/core/consult.py`, `src/data/database.py`, **`TASK_CONFIG`** layout.

## Stage 1: Config schedulable cutover — fetch_jd + retired keys

**Done when:** **`dispatch_task_admin_defaults("fetch_jd")`** returns **`entity_type=job`**, **`trigger_state=PASSED_JOBLIST`**, **`batch_call_mode=0`**; **`dispatch_task_admin_defaults("scrape_jd")`**, **`("validate_title")`**, and **`("gaze_board")`** raise **`KeyError`** with retired messaging; **`fetch_jd`** ∈ **`DISPATCH_SCHEDULABLE_TASK_KEYS`**; **`scrape_jd`**, **`validate_title`**, **`gaze_board`** ∉ **`DISPATCH_SCHEDULABLE_TASK_KEYS`**; **`GAZER_CONFIG["fetch_jd"]`** carries today's **`scrape_jd`** orchestration literals unchanged; **`GAZER_CONFIG["scrape_jd"]`** resolves to the same dict object (transitional alias).

1. In **`src/utils/config.py`**, update the file header inventory comment (~line 21) from **`validate_title, scrape_jd, gaze`** to **`validate_title (inline-only), fetch_jd, gaze`**.

2. In **`GAZER_CONFIG`**, rename the dict key **`"scrape_jd"`** to **`"fetch_jd"`** — keep the nested literals identical:
   - **`fallback_batch_size`: 10**
   - **`pass_state`: `"JD_READY"`**
   - **`fail_state`: `"JD_SCRAPE_FAIL"`**
   - **`error_states`**: unchanged list of four **`JD_SCRAPE_FAIL_*`** strings

3. Immediately after the **`GAZER_CONFIG = { ... }`** closing brace, add (single line, with adjacent comment):

   ```python
   # AST-797 removes after gazer/consult read fetch_jd.
   GAZER_CONFIG["scrape_jd"] = GAZER_CONFIG["fetch_jd"]
   ```

4. Update the **`GAZER_CONFIG`** section comment (~line 928) to reference **`fetch_jd`** instead of **`scrape_jd`** for the JD scrape hop; note **`validate_title`** remains for inline screening until **AST-797**.

5. In **`DISPATCH_SCHEDULABLE_TASK_KEYS`**, in the job-pipeline group:
   - **Remove** **`"validate_title"`** and **`"scrape_jd"`**
   - **Add** **`"fetch_jd"`** in the same position (after **`qualify_job_listings`** is wrong — place **`fetch_jd`** where **`scrape_jd`** was: after **`qualify_job_listings`**, before **`evaluate_jd`**)

6. In **`DISPATCH_RETIRED_TASK_KEYS`**, extend the frozenset to include **`"scrape_jd"`**, **`"validate_title"`**, and **`"gaze_board"`** (keep existing **`consult_*`** entries).

7. Extend **`_RETIRED_DISPATCH_TASK_KEY_REPLACEMENTS`** with:

   ```python
   "scrape_jd": "fetch_jd",
   ```

8. Add a module-level dict **`_RETIRED_DISPATCH_TASK_KEY_STATIC_MESSAGES`** (name as shown) mapping keys without replacements:

   ```python
   _RETIRED_DISPATCH_TASK_KEY_STATIC_MESSAGES = {
       "validate_title": (
           "task_key 'validate_title' is retired; title screening runs inline before qualify_job_listings"
       ),
       "gaze_board": (
           "task_key 'gaze_board' is retired; boards are decommissioned"
       ),
   }
   ```

9. Rewrite **`dispatch_task_key_retired_message`** to:
   - Return **`None`** when **`task_key`** ∉ **`DISPATCH_RETIRED_TASK_KEYS`**
   - When **`task_key`** ∈ **`_RETIRED_DISPATCH_TASK_KEY_REPLACEMENTS`**, return **`f"task_key {tk!r} is retired; use {replacement!r}"`**
   - Otherwise return **`_RETIRED_DISPATCH_TASK_KEY_STATIC_MESSAGES[tk]`** (must exist for every retired key without a replacement)

10. In **`_dispatch_trigger_state_for_task_key`**, **delete** the **`if task_key == "validate_title"`** and **`if task_key == "scrape_jd"`** branches. **Add** after the **`qualify_job_listings`** branch:

    ```python
    if task_key == "fetch_jd":
        return "PASSED_JOBLIST"
    ```

11. In **`_dispatch_entity_type_for_task_key`**, in the explicit job-pipeline tuple (~line 1359), **replace** **`"scrape_jd"`** with **`"fetch_jd"`** and **remove** **`"validate_title"`**.

12. Run locally (engineer sanity, not a commit artifact):

    ```bash
    python3 -c "
    from src.utils.config import (
        DISPATCH_SCHEDULABLE_TASK_KEYS,
        dispatch_task_admin_defaults as d,
        dispatch_task_key_retired_message as retired,
    )
    assert 'fetch_jd' in DISPATCH_SCHEDULABLE_TASK_KEYS
    assert 'scrape_jd' not in DISPATCH_SCHEDULABLE_TASK_KEYS
    assert 'validate_title' not in DISPATCH_SCHEDULABLE_TASK_KEYS
    fd = d('fetch_jd')
    assert fd == {'entity_type': 'job', 'trigger_state': 'PASSED_JOBLIST', 'sort_by': 'updated_at', 'batch_call_mode': 0}
    assert 'fetch_jd' in retired('scrape_jd')
    assert retired('validate_title') is not None
    assert retired('gaze_board') is not None
    print('ok')
    "
    ```

    Expected stdout: **`ok`**.

## Self-Assessment

**Scope:** `Single-Component` — only **`src/utils/config.py`** dispatch catalog helpers and **`GAZER_CONFIG`**; no runtime routing, DB migration, or **`TASK_CONFIG`** reorganization.

**Conf:** `high` — follows established **`consult_*` → `grade_*`** retirement pattern (**AST-748** / **AST-749**) and prior schedulable registration tickets (**AST-719**, **AST-774**); explicit boundary defers gazer/consult string cutover to **AST-797**.

**Risk:** `Medium` — admin surfaces flip before runtime executes **`fetch_jd`** rows (**AST-797**); mis-ordered epic merge could leave Susan able to create **`fetch_jd`** dispatch rows that still route to **`scrape_jd`** batch until sibling lands — acceptable within epic, not for isolated ship to **`dev`**.

## ASTRAL_CODE_RULES self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Extends existing **`dispatch_task_key_retired_message`** / **`_RETIRED_DISPATCH_TASK_KEY_REPLACEMENTS`** pattern; no parallel admin validation dict |
| §1.4 hardcoded sets | All schedulable/retired membership stays in **`config.py`** frozensets |
| §2.1 config source of truth | Schedulable and retired catalogs remain config-driven; **`api_admin.py`** unchanged |
| §2.4 batch | **`fetch_jd`** inherits **`batch_call_mode=0`** like **`scrape_jd`** today |
| §2.6 state machine | Job states (**`PASSED_JOBLIST`**, **`JD_READY`**, scrape-fail substates) unchanged — only dispatch **task_key** string |
| §3.3 imports | No new cross-layer imports |
| §3.5 naming | Aligns dispatch vocabulary with repo **`fetch_jd`** / **"Fetch Job Description"** label |

No conflicts requiring plan revision.

## Integration notes (out of scope — AST-797)

- **`consult.py`** state→task map and **`run_consult_task`** branches still use **`scrape_jd`** / **`validate_title`** strings until **AST-797**.
- **`gazer.py`** reads **`GAZER_CONFIG["scrape_jd"]`** via transitional alias; **AST-797** removes alias and renames batch entrypoints.
- **`dispatch_task`** DB rows with **`task_key='scrape_jd'`** migrate in **AST-797**; this ticket does not touch **`database.py`**.
