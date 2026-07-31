<!-- linear-archive: AST-796 archived 2026-07-22 -->

## Linear archive (AST-796)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-796/config-schedulable-key-cutover-fetch-jd-and-retire-keys-3-task-config  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-794 — 3 task_config updates to config.py  
**Blocked by / blocks / related:** parent: AST-794; blocks: AST-797

### Description

## What this implements

Align `src/utils/config.py` schedulable task-key catalogs with repo `agent_task.json`: rename **scrape_jd** → **fetch_jd** in **GAZER_CONFIG** and all dispatch helper paths; remove **gaze_board** and **validate_title** from schedulable/admin catalogs; add retired-key handling so admin save rejects **scrape_jd**, **validate_title**, and **gaze_board** post-cutover.

## Acceptance criteria

1. Susan can create and run a **fetch_jd** dispatch row at **PASSED_JOBLIST**; admin APIs and Scheduled Actions do not offer **scrape_jd** as a schedulable key.
2. Admin **GET /api/admin/dispatch_tasks/task_keys** and Scheduled Actions grouping show **fetch_jd** with correct metadata; retired keys are rejected on save.

## Boundaries

* Does not change gazer/consult runtime routing or DB rows — sibling **Hedy** ticket.
* Does not rename job states or grading orchestration fields on scored tasks.
* Does not reorganize **TASK_CONFIG** layout.

## Notes for planning

* **GAZER_CONFIG**, **DISPATCH_SCHEDULABLE_TASK_KEYS**, **DISPATCH_RETIRED_TASK_KEYS**, `_dispatch_trigger_state_for_task_key`, `_dispatch_entity_type_for_task_key`, and related helpers in `config.py`.
* Admin validation for retired keys likely touches `api_admin.py` if save paths bypass config catalogs — keep changes minimal and config-driven per **ASTRAL_CODE_RULES** §2.1.

## Git branch (authoritative)

Per **orientation** § Branch law: parent `ftr/ast-794-task-config-key-cutover`, child `sub/AST-794/<child-segment>`.

### Comments

#### radia — 2026-06-25T01:33:49.389Z
### Radia review — AST-796

**Diff:** `origin/dev...origin/sub/AST-794/ast-796-config-schedulable-key-cutover-fetch-jd-retire-keys` @ `b68b592` (doc) · product `37b1af3`

**Plan fidelity:** Stage 1 complete — `GAZER_CONFIG` `fetch_jd` + transitional `scrape_jd` read alias; schedulable/retired frozensets; `dispatch_task_key_retired_message` replacement + static paths; trigger/entity helpers for `fetch_jd` @ `PASSED_JOBLIST`. Scope matches Self-Assessment (`config.py` only; runtime deferred AST-797).

**ASTRAL_CODE_RULES:** §1.3 DRY (extends AST-748 retirement pattern); §1.4 catalogs in config; §2.1 admin remains config-driven via existing `api_admin` filters; §3.3 no new cross-layer imports.

**Tests:** `TestAst796FetchJdSchedulableCutover`, `TestAst796FetchJdRetiredDispatchKeys` + bible manifest rows align with plan.

**Doc:** `docs/features/roster/ast-796-config-schedulable-key-cutover-fetch-jd-retire-keys.md` § Radia review

**Counts:** 0 fix-now · 0 discuss · 0 advisory

— Radia

#### betty — 2026-06-25T01:31:02.932Z
## QA test manifest (AST-796)

**Publish ref:** `origin/sub/AST-794/ast-796-config-schedulable-key-cutover-fetch-jd-retire-keys` @ `17f5bce`
**Tests commit:** `43f8a20` on `origin/tests`

**Bible shasums (publish tip):**
- `docs/test-bible/utils/config.md` — `c8efecb4ceb6be915bcd5e42214dccf0bbee2b8c`
- `docs/test-bible/ui/api/api_admin.md` — `0ee255ca68e2e3264d6e08ed868f9c857b5c90c1`

### Manifest (test-child)

1. **Config schedulable cutover (required):**
```bash
./scripts/testing/run_component_tests.sh   tests/component/utils/test_config.py::TestAst796FetchJdSchedulableCutover   -q
```
Expect: `fetch_jd` ∈ `DISPATCH_SCHEDULABLE_TASK_KEYS`; `scrape_jd` / `validate_title` / `gaze_board` ∉; `dispatch_task_admin_defaults("fetch_jd")` → job @ `PASSED_JOBLIST`, `batch_call_mode=0`; retired keys raise `KeyError`; `GAZER_CONFIG["scrape_jd"]` alias to `fetch_jd`.

2. **Admin retirement paths (required):**
```bash
./scripts/testing/run_component_tests.sh   tests/component/ui/api/test_api_admin.py::TestAst796FetchJdRetiredDispatchKeys   -q
```
Expect: `GET /api/admin/dispatch_tasks/task_keys` includes `fetch_jd`, excludes retired keys; `POST` with `scrape_jd` / `validate_title` / `gaze_board` → 400 with retired messaging.

**Pass criterion:** items 1–2 green — narrowed run only (not zero-arg harness / branch-lock gate).

**Broken / obsolete:** none — extends AST-747/749 retirement pattern for new retired keys.

**Out of scope (AST-797):** runtime consult/gazer routing, DB row migration, inline validate_title wiring.

#### ada — 2026-06-25T01:26:12.457Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-794/ast-796-config-schedulable-key-cutover-fetch-jd-retire-keys/docs/features/roster/ast-796-config-schedulable-key-cutover-fetch-jd-retire-keys.md

**Scope:** Single-Component — `src/utils/config.py` only: register `fetch_jd` @ `PASSED_JOBLIST`, retire `scrape_jd` / `validate_title` / `gaze_board` from schedulable catalogs, rename `GAZER_CONFIG` JD hop with transitional `scrape_jd` read alias until AST-797.

**Conf:** high — mirrors AST-748/749 retired-key pattern and prior schedulable registration tickets; runtime/DB cutover explicitly deferred to AST-797.

**Risk:** Medium — admin can create `fetch_jd` rows before AST-797 runtime routing lands; acceptable within epic merge order, not for isolated dev ship.

---

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

## Review stub (build)

**Publish ref:** `origin/sub/AST-794/ast-796-config-schedulable-key-cutover-fetch-jd-retire-keys`  
**Product tip:** `37b1af3`

**Built:** Stage 1 — **`GAZER_CONFIG`** **`fetch_jd`** + transitional **`scrape_jd`** read alias; **`DISPATCH_SCHEDULABLE_TASK_KEYS`** / **`DISPATCH_RETIRED_TASK_KEYS`** cutover; **`dispatch_task_key_retired_message`** extended for **`scrape_jd`**, **`validate_title`**, **`gaze_board`**.

**QA note:** Betty manifest for **`fetch_jd`** schedulable defaults, retired-key POST rejection, **`task_keys`** includes **`fetch_jd`** — verify-only per plan.

---

## Radia review (2026-06-25)

**Diff:** `origin/dev...origin/sub/AST-794/ast-796-config-schedulable-key-cutover-fetch-jd-retire-keys` @ `17f5bce`  
**Product commit:** `37b1af3` (`src/utils/config.py` only)

### What's solid

| Area | Notes |
|------|-------|
| Plan Stage 1 (all 12 steps) | **`GAZER_CONFIG["fetch_jd"]`** carries prior **`scrape_jd`** literals; transitional **`GAZER_CONFIG["scrape_jd"]`** alias; header + section comments updated. |
| Schedulable / retired catalogs | **`fetch_jd`** ∈ **`DISPATCH_SCHEDULABLE_TASK_KEYS`** @ **`PASSED_JOBLIST`**; **`scrape_jd`**, **`validate_title`**, **`gaze_board`** ∈ **`DISPATCH_RETIRED_TASK_KEYS`** and excluded from schedulable set. |
| Retirement messaging | **`dispatch_task_key_retired_message`** extended per AST-748 pattern — replacement for **`scrape_jd`**, static messages for **`validate_title`** / **`gaze_board`**; **`dispatch_task_admin_defaults`** raises **`KeyError(retired)`** before schedulable check. |
| Trigger / entity helpers | **`_dispatch_trigger_state_for_task_key`** / **`_dispatch_entity_type_for_task_key`** updated; retired branches removed. |
| Scope boundary | No **`gazer.py`**, **`consult.py`**, **`database.py`**, or **`api_admin.py`** product changes — matches plan and Self-Assessment **`Single-Component`**. |
| §1.3 / §1.4 / §2.1 | DRY extension of existing retirement helpers; frozenset catalogs remain config-driven. |
| Tests + bible | **`TestAst796FetchJdSchedulableCutover`**, **`TestAst796FetchJdRetiredDispatchKeys`**; manifest rows in **`docs/test-bible/utils/config.md`** and **`docs/test-bible/ui/api/api_admin.md`**. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| — | — | None. |

### Recommended actions

| Action | Owner |
|--------|-------|
| None blocking | — |

**Counts:** 0 fix-now · 0 discuss · 0 advisory

**Outcome:** Clean — ready for **`resolve-child`** / epic rollup with **AST-797** for runtime cutover.

— Radia

## Resolution (2026-06-25)

**Review:** Radia @ `b68b592` — 0 fix-now · 0 discuss · 0 advisory (clean).

**Product changes:** None — Stage 1 delivered as reviewed (`37b1af3`).

**Verification:** Betty manifest green on publish tip (`TestAst796FetchJdSchedulableCutover`, `TestAst796FetchJdRetiredDispatchKeys`). §9a dry-run: publish ref merges cleanly into `origin/dev` and `origin/ftr/ast-794-task-config-key-cutover`.

**Handoff:** Runtime routing, DB migration, and inline `validate_title` wiring remain **AST-797**.
