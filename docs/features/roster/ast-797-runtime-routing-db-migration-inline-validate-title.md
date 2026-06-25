# AST-797 — Runtime routing, DB migration, and inline validate_title

- **Linear (this ticket):** [AST-797](https://linear.app/astralcareermatch/issue/AST-797/runtime-routing-db-migration-and-inline-validate-title-3-task-config-updates-to)
- **Parent (coordination only):** [AST-794](https://linear.app/astralcareermatch/issue/AST-794/3-task-config-updates-to-configpy)
- **Publish ref:** `origin/sub/AST-794/ast-797-runtime-routing-db-migration-inline-validate-title`

## Summary

Ship runtime cutover after sibling **AST-796** config catalogs: rename **`scrape_jd` → `fetch_jd`** in gazer/consult/dispatcher routing and coat-check self-heal; idempotent **`dispatch_task`** DB migration (**`scrape_jd` → `fetch_jd`**, purge **`validate_title`** / **`gaze_board`** rows, retarget **`qualify_job_listings`** from **`VALID_TITLE` → `NEW`** with explicit **`VALID_TITLE_RETRY`** companion rows); fold mechanical **`validate_title_batch`** as an inline pre-step inside **`qualify_job_listings`** so **NEW** jobs reach the qualify AI hop without a separate **`validate_title`** dispatch row. Job states, JD scrape behavior, and qualify grading math are unchanged — only task-key strings, dispatch row shapes, and title-screening wiring move.

**Prerequisite (build gate — not a commit stage):** Epic worktree includes **AST-796** config cutover on **`origin/ftr/ast-794-task-config-key-cutover`** — **`fetch_jd`** schedulable, retired keys in **`DISPATCH_RETIRED_TASK_KEYS`**, transitional **`GAZER_CONFIG["scrape_jd"]`** read alias. Merge **`origin/sub/AST-794/ast-796-config-schedulable-key-cutover-fetch-jd-retire-keys`** (or equivalent ftr tip) before **build-child** Stage 2.

⚠️ **Decision:** Retire **`validate_title`** as a **`run_consult_task`** branch entirely — title screening runs only via **`qualify_job_listings`** inline pre-step. **`validate_title_batch`** stays in **`gazer.py`** (not deleted).

⚠️ **Decision:** Change **`qualify_job_listings`** admin default **`trigger_state`** from **`VALID_TITLE`** to **`NEW`**. Today one row at **`VALID_TITLE`** claims **`VALID_TITLE` + `VALID_TITLE_RETRY`** via **`dispatch_claim_states`**. After cutover: primary row at **`NEW`** claims **NEW** only; migration seeds an explicit **`VALID_TITLE_RETRY`** companion row per candidate so retry batches still dispatch without re-running inline title screening.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Idempotent migration: **`scrape_jd` → `fetch_jd`**, DELETE **`validate_title`** / **`gaze_board`**, qualify **`VALID_TITLE` → `NEW`** + seed **`VALID_TITLE_RETRY`** companions | data |
| `src/utils/config.py` | Remove **`GAZER_CONFIG["scrape_jd"]`** alias; **`_dispatch_trigger_state_for_task_key("qualify_job_listings")` → `NEW`**; update header / section comments | utils |
| `src/core/gazer.py` | Rename **`scrape_jd_batch` → `fetch_jd_batch`**; read **`GAZER_CONFIG["fetch_jd"]`**; update module docstring and debug **`func=`** strings | core |
| `src/core/consult.py` | Inline **`validate_title_batch`** in **`qualify_job_listings`**; remove **`validate_title`** / **`scrape_jd`** branches; add **`fetch_jd`** → **`fetch_jd_batch`**; update **`_INPUT_STATE_TO_TASK`** | core |
| `src/core/dispatcher.py` | Comment-only **`scrape_jd` → `fetch_jd`** (no frozenset change — **`fetch_jd`** uses **`batch_call_mode=0`**) | core |
| `src/core/tracker.py` | Coat-check self-heal: **`fetch_jd_batch`** import/call + log strings | core |
| `src/ui/api/api_admin.py` | Remove **`validate_title`** from **`_build_adhoc_live_content`** batch branch | ui |

**Verify only (Betty / qa-child — engineer does not edit in build-child):**

| File | Change |
|------|--------|
| `tests/component/data/database/test_dispatch_tasks.py` | **`TestAst797*`** — scrape_jd→fetch_jd rename + collision delete; validate_title/gaze_board purge; qualify trigger NEW + VALID_TITLE_RETRY seed |
| `tests/component/core/test_consult.py` | **`fetch_jd`** routing; inline validate before qualify; remove **`validate_title`** dispatch routing assertions |
| `tests/component/core/test_gazer.py` | **`fetch_jd_batch`** rename (replace **`scrape_jd_batch`** references) |
| `tests/component/core/test_tracker.py` | Coat-check monkeypatch target **`fetch_jd_batch`** |
| `tests/component/ui/api/test_api_admin.py` | Adhoc preview no longer serves **`validate_title`** |
| `docs/test-bible/core/consult.md`, `gazer.md`, `data/database/dispatch_tasks.md` | Runtime wording **`fetch_jd`**, inline validate, qualify @ **NEW** |

**No changes expected:** **`TASK_CONFIG`** layout, **`api_admin.py`** schedulable/retired-key guards (already **AST-796**), **`agent_task.json`** (already lists **`fetch_jd`**, omits retired keys).

## Stage 1: Database — idempotent dispatch row cutover

**Done when:** `_ensure_dispatch_task_schema` leaves **zero** rows with **`task_key IN ('scrape_jd','validate_title','gaze_board')`**; existing **`scrape_jd`** rows become **`fetch_jd`** with scheduling columns preserved; **`qualify_job_listings`** rows at **`VALID_TITLE`** become **`NEW`**; each migrated candidate has a **`qualify_job_listings` / `VALID_TITLE_RETRY`** row when the pre-migration primary row existed at **`VALID_TITLE`**.

1. In **`src/data/database.py`**, inside **`_ensure_dispatch_task_schema`**, immediately **after** the existing AST-748 **`consult_*` → `grade_*`** block and **before** **`_dispatch_task_schema_ensured = True`**, add:

```python
    # AST-794 / AST-797: retire scrape_jd / validate_title / gaze_board dispatch rows.
    _SCRAPE_TO_FETCH_DISPATCH_KEYS = (("scrape_jd", "fetch_jd"),)
    for retired_key, canonical_key in _SCRAPE_TO_FETCH_DISPATCH_KEYS:
        conn.execute(
            """
            DELETE FROM dispatch_task AS d
            WHERE d.task_key = ?
              AND EXISTS (
                SELECT 1 FROM dispatch_task AS g
                WHERE g.candidate_id = d.candidate_id
                  AND g.task_key = ?
                  AND g.trigger_state = d.trigger_state
              )
            """,
            (retired_key, canonical_key),
        )
        conn.execute(
            "UPDATE dispatch_task SET task_key = ? WHERE task_key = ?",
            (canonical_key, retired_key),
        )
    conn.commit()

    for purge_key in ("validate_title", "gaze_board"):
        conn.execute("DELETE FROM dispatch_task WHERE task_key = ?", (purge_key,))
    conn.commit()

    # qualify @ VALID_TITLE claimed VALID_TITLE + VALID_TITLE_RETRY via dispatch_claim_states;
    # split into explicit NEW + VALID_TITLE_RETRY rows.
    qualify_retry_rows = conn.execute(
        """
        SELECT candidate_id, entity_type, sort_by, batch_call_mode, last_run_at,
               freq_hrs, min_count, batch_size, batch_id, auto_mode, debug,
               skip_cache, max_runs, score_floor, updated_at
        FROM dispatch_task
        WHERE task_key = 'qualify_job_listings' AND trigger_state = 'VALID_TITLE'
        """
    ).fetchall()
    for r in qualify_retry_rows:
        conn.execute(
            """
            INSERT INTO dispatch_task (
                candidate_id, task_key, entity_type, trigger_state, sort_by,
                batch_call_mode, last_run_at, freq_hrs, min_count, batch_size,
                batch_id, auto_mode, debug, skip_cache, max_runs, score_floor, updated_at
            )
            SELECT ?, 'qualify_job_listings', ?, 'VALID_TITLE_RETRY', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM dispatch_task
                WHERE candidate_id = ? AND task_key = 'qualify_job_listings'
                  AND trigger_state = 'VALID_TITLE_RETRY'
            )
            """,
            (
                r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9],
                r[10], r[11], r[12], r[13], r[14],
                r[0],
            ),
        )
    conn.execute(
        "UPDATE dispatch_task SET trigger_state = 'NEW' "
        "WHERE task_key = 'qualify_job_listings' AND trigger_state = 'VALID_TITLE'"
    )
    conn.commit()
```

2. Do **not** import config replacement maps — keep tuples local (same rule as AST-748).

3. Manual verification on throwaway SQLite (do **not** commit):

   - **Case A — scrape rename:** one row **`scrape_jd` / `PASSED_JOBLIST`** with **`freq_hrs=2`**, **`batch_size=5`**, **`auto_mode=1`** → after ensure, **`task_key='fetch_jd'`**, columns unchanged.
   - **Case B — scrape collision:** rows **`scrape_jd`/`PASSED_JOBLIST`** and **`fetch_jd`/`PASSED_JOBLIST`** same **`candidate_id`** → exactly one **`fetch_jd`** row remains (pre-existing **`fetch_jd`** wins).
   - **Case C — purge:** rows for **`validate_title`/`NEW`** and **`gaze_board`/`WATCH`** → deleted.
   - **Case D — qualify split:** one row **`qualify_job_listings`/`VALID_TITLE`** → becomes **`NEW`**; companion **`qualify_job_listings`/`VALID_TITLE_RETRY`** inserted with same scheduling fields.
   - **`SELECT COUNT(*) FROM dispatch_task WHERE task_key IN ('scrape_jd','validate_title','gaze_board')`** → **0**.

⚠️ **Decision:** On scrape_jd/fetch_jd triple collision, **delete the legacy `scrape_jd` row** — canonical **`fetch_jd`** row wins (AST-748 pattern).

## Stage 2: Config — remove transitional alias; qualify claims NEW

**Done when:** **`dispatch_task_admin_defaults("qualify_job_listings")["trigger_state"] == "NEW"`**; **`"scrape_jd" not in GAZER_CONFIG`** (only **`fetch_jd`** key); module header comment no longer says “until AST-797”.

1. In **`src/utils/config.py`**, delete the two lines:

   ```python
   # AST-797 removes after gazer/consult read fetch_jd.
   GAZER_CONFIG["scrape_jd"] = GAZER_CONFIG["fetch_jd"]
   ```

2. In **`_dispatch_trigger_state_for_task_key`**, change the **`qualify_job_listings`** branch (~line 1317) from **`return "VALID_TITLE"`** to **`return "NEW"`**.

3. Update **`GAZER_CONFIG`** section comment (~line 928) to: **`validate_title` inline-only (qualify pre-step); `fetch_jd`; gaze`** — remove “until AST-797” wording.

4. Update file header inventory comment (~line 21) to match: **`validate_title (inline-only), fetch_jd, gaze`**.

5. Run locally:

   ```bash
   python3 -c "
   from src.utils.config import GAZER_CONFIG, dispatch_task_admin_defaults as d
   assert 'scrape_jd' not in GAZER_CONFIG
   assert 'fetch_jd' in GAZER_CONFIG
   assert d('qualify_job_listings')['trigger_state'] == 'NEW'
   print('ok')
   "
   ```

   Expected stdout: **`ok`**.

## Stage 3: Gazer — rename `scrape_jd_batch` → `fetch_jd_batch`

**Done when:** **`grep -n scrape_jd src/core/gazer.py`** returns **zero** matches; **`fetch_jd_batch`** reads **`GAZER_CONFIG["fetch_jd"]`** for pass/fail states; all debug **`func=`** strings use **`gazer.fetch_jd_batch`**.

1. In **`src/core/gazer.py`**, update module docstring line 4: replace **`scrape_jd_batch`** with **`fetch_jd_batch`**.

2. Rename **`async def scrape_jd_batch(...)`** to **`async def fetch_jd_batch(...)`** — function body unchanged except:
   - Connectivity error message: **`fetch_jd_batch: no internet connectivity...`**
   - **`pass_state = GAZER_CONFIG["fetch_jd"]["pass_state"]`**
   - **`fail_state = GAZER_CONFIG["fetch_jd"]["fail_state"]`**
   - Every **`func="gazer.scrape_jd_batch"`** → **`func="gazer.fetch_jd_batch"`**

3. Do **not** add a backward-compat alias function — callers update in Stage 4.

4. Grep **`src/core/gazer.py`** for **`scrape_jd`** — zero matches.

## Stage 4: Runtime — consult inline validate, routing cutover, tracker, admin

**Done when:** **`grep -E 'scrape_jd|validate_title' src/core/consult.py src/core/tracker.py src/ui/api/api_admin.py`** returns **zero** matches (except module docstring historical prose if any — prefer updating docstrings to **`fetch_jd`**); **`run_consult_task(..., dispatch_task_key='fetch_jd')`** routes JD batch; **`qualify_job_listings`** runs inline title screening for **NEW** jobs before AI; retired dispatch branches removed.

### 4a. Inline `validate_title_batch` in `qualify_job_listings`

1. At the top of **`async def qualify_job_listings`** in **`src/core/consult.py`**, immediately after **`cfg = _consult_orchestration(task_key)`** (~line 1230) and **before** rubric/debug setup, insert:

```python
    title_screen_failed = 0
    if any((j.get("state") or "") == "NEW" for j in jobs):
        from src.core.gazer import validate_title_batch

        new_jobs = [j for j in jobs if (j.get("state") or "") == "NEW"]
        tr = await validate_title_batch(batch_id, new_jobs, ctx or {}, debug=debug)
        title_screen_failed = int(tr.get("failed", 0))
        for j in jobs:
            if (j.get("state") or "") == "NEW":
                fresh = tracker.get_job(j["astral_job_id"])
                if fresh:
                    j["state"] = fresh.get("state")
    ai_jobs = [
        j for j in jobs
        if (j.get("state") or "") in ("VALID_TITLE", "VALID_TITLE_RETRY")
    ]
    if not ai_jobs:
        return {
            "passed": 0,
            "failed": title_screen_failed,
            "total": len(jobs),
        }
    jobs = ai_jobs
```

2. After **`result = await _run_batch_consult(...)`** at the end of **`qualify_job_listings`**, before **`return result`**, merge inline title failures into the batch summary:

```python
    if title_screen_failed:
        result = dict(result)
        result["failed"] = int(result.get("failed", 0)) + title_screen_failed
        result["total"] = max(int(result.get("total", 0)), len(jobs) + title_screen_failed)
    return result
```

   Use the **`jobs`** variable as it exists at return time (post-filter **`ai_jobs`**). **`total`** should reflect the original claimed batch size: capture **`claimed_total = len(jobs)`** at function entry (before inline filter) and use that in the empty-**`ai_jobs`** early return and in the merge step:

   - Add **`claimed_total = len(jobs)`** as the first line inside **`qualify_job_listings`** (after the signature/docstring).
   - Empty early return: **`"total": claimed_total`**
   - Merge step: **`result["total"] = claimed_total`**

### 4b. `run_consult_task` routing cutover

3. In **`_INPUT_STATE_TO_TASK`**, replace:

   ```python
   "NEW":                "validate_title",
   ...
   "PASSED_JOBLIST":     "scrape_jd",
   ```

   with:

   ```python
   "NEW":                "qualify_job_listings",
   ...
   "PASSED_JOBLIST":     "fetch_jd",
   ```

4. Delete the entire **`if task_key == "validate_title":`** branch (~lines 1836–1838).

5. Replace the **`elif task_key == "scrape_jd":`** branch with:

   ```python
    elif task_key == "fetch_jd":
        from src.core.gazer import fetch_jd_batch
        r = await fetch_jd_batch(batch_id, entities, debug=debug)
   ```

### 4c. Tracker coat-check

6. In **`src/core/tracker.py`** (~lines 408–417), replace **`scrape_jd_batch`** with **`fetch_jd_batch`** in comments, import, call, and warning log strings.

### 4d. Admin adhoc preview

7. In **`src/ui/api/api_admin.py`** (~lines 1050–1064), change the batch-mode condition from:

   ```python
   if task_key in ("qualify_job_listings", "validate_title"):
   ```

   to:

   ```python
   if task_key == "qualify_job_listings":
   ```

   Remove the **`else`** branch that appended raw listing only for **`validate_title`** — the **`qualify_job_listings`** path (with **`job_site`**) is the sole branch.

### 4e. Dispatcher comment

8. In **`src/core/dispatcher.py`** (~line 160), update comment **`scrape_jd`** → **`fetch_jd`**.

### 4f. Verification grep

9. Run:

   ```bash
   rg 'scrape_jd|validate_title' src/core/consult.py src/core/tracker.py src/ui/api/api_admin.py src/core/dispatcher.py
   ```

   Expected: **no matches** (or docstring-only — update docstrings if found).

## Execution contract

Binding per **plan-child**: stages **1 → 4** in order; **one commit per stage** on epic worktree during **build-child**, publish each to **`origin/sub/AST-794/ast-797-runtime-routing-db-migration-inline-validate-title`**. Do not edit **`tests/`**, **`docs/ASTRAL_TEST_BIBLE.md`**, or **`docs/test-bible/**`**. On ambiguity — **`🛑 Stage N blocked`** on **AST-794** parent; stop.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — **`database.py`** dispatch migration, **`config.py`** qualify trigger + alias removal, **`gazer.py`** batch rename, and **`consult.py`** / **`tracker.py`** / **`api_admin.py`** runtime routing plus inline title screening.

**Conf:** `high` — mirrors AST-748 DELETE-before-UPDATE migration and AST-796 handoff boundaries; inline validate reuses existing **`validate_title_batch`** without new state machine rules.

**Risk:** `HIGH` — incorrect qualify trigger split could strand **VALID_TITLE_RETRY** jobs with no dispatch row; migration **`IntegrityError`** bricks Scheduled Actions; skipping inline validate refresh would run qualify AI on **NEW** jobs that failed title regex.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §1.3 DRY | Inline validate calls existing **`validate_title_batch`**; JD scrape logic stays in one **`fetch_jd_batch`** function |
| §1.4 hardcoded sets | Title pass/fail states read from **`GAZER_CONFIG["validate_title"]`** inside **`validate_title_batch`** — no inline state strings in consult |
| §2.1 config | Retired keys remain config-driven (**AST-796**); migration tuples local to **`database.py`** |
| §2.4 batch | **`fetch_jd`** keeps **`batch_call_mode=0`**; qualify batch summary merges inline title failures into **`failed`/`total`** |
| §2.6 state machine | **`NEW` → `VALID_TITLE`/`INVALID_TITLE`** via existing gazer transitions; qualify AI still requires **`VALID_TITLE`** or **`VALID_TITLE_RETRY`** |
| §2.7 render_verdict | Unchanged — graded hops untouched |
| §3.3 imports | Lazy **`validate_title_batch`** / **`fetch_jd_batch`** imports in consult match existing gazer routing pattern |
| §3.5 naming | Runtime strings align with repo **`fetch_jd`** catalog |

No conflicts requiring `!!-NONE`.

## Integration notes

- **AST-796** (merged on ftr): schedulable/retired catalogs and admin rejection — this ticket does not re-edit those frozensets except qualify trigger default and alias removal.
- **Betty** owns test renames (**`scrape_jd_batch` → `fetch_jd_batch`**, inline qualify manifest) — engineer verify-only per plan.
- **`dispatch_ledger`** historical **`scrape_jd`** / **`validate_title`** strings are not backfilled (parent boundary).

## Review stub (build)

| Field | Value |
|-------|-------|
| Build date | 2026-06-25 |
| Publish ref | `origin/sub/AST-794/ast-797-runtime-routing-db-migration-inline-validate-title` @ `0461cf7` |
| Commits | `ab9cbf4` database migration · `01b1c49` config · `af00bbd` gazer rename · `0461cf7` consult/tracker/admin/dispatcher runtime |

**Built:** All four plan stages — idempotent dispatch migration; config qualify @ **NEW** + alias removal; **`fetch_jd_batch`**; inline **`validate_title_batch`** in **`qualify_job_listings`**; **`fetch_jd`** routing cutover.

**QA note:** Betty manifest for migration tests, **`fetch_jd`** routing, inline qualify, gazer/tracker renames — verify-only per plan.

---

## Radia review (2026-06-25)

**Diff:** `origin/dev...origin/sub/AST-794/ast-797-runtime-routing-db-migration-inline-validate-title` @ `1a14ea5`  
**Product commits:** `ab9cbf4` database · `01b1c49` config · `af00bbd` gazer · `0461cf7` consult/tracker/admin/dispatcher  
**Includes AST-796 config cutover** on publish ref (epic prerequisite — expected rollup, not sibling bleed).

### What's solid

| Area | Notes |
|------|-------|
| Stage 1 — DB migration | DELETE-before-UPDATE **`scrape_jd` → `fetch_jd`** (collision-safe); purge **`validate_title`** / **`gaze_board`**; qualify **`VALID_TITLE` → `NEW`** + **`VALID_TITLE_RETRY`** companion seed; bind tuple / column count verified; idempotent on re-ensure. |
| Stage 2 — Config | Transitional **`GAZER_CONFIG["scrape_jd"]`** alias removed; **`qualify_job_listings`** trigger **`NEW`**; AST-796 schedulable/retired catalogs retained. |
| Stage 3 — Gazer | **`fetch_jd_batch`** rename complete; reads **`GAZER_CONFIG["fetch_jd"]`**; **`func="gazer.fetch_jd_batch"`** on all debug paths (§1.5.1). |
| Stage 4 — Runtime | Inline **`validate_title_batch`** pre-step in **`qualify_job_listings`** with **`claimed_total`** accounting; **`fetch_jd`** routing; retired **`validate_title`** / **`scrape_jd`** branches removed; tracker coat-check + admin adhoc updated. |
| §2.4 / §2.6 | Title screening still via gazer transitions; qualify AI gated on **`VALID_TITLE`** / **`VALID_TITLE_RETRY`** only; batch summary merges inline failures into **`failed`/`total`**. |
| §3.3 | Lazy gazer imports in consult match existing routing pattern; no new cross-layer violations. |
| Tests + bible | **`TestAst797DispatchKeyCutoverMigration`**, **`TestAst797QualifyInlineValidateTitle`**, config/gazer/tracker/dispatcher renames; bible manifest rows updated. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| — | — | None. |

### Recommended actions

| Action | Owner |
|--------|-------|
| None blocking | — |

**Counts:** 0 fix-now · 0 discuss · 0 advisory

**Outcome:** Clean — ship with **AST-796** on epic rollup; do not isolate to **`dev`** without sibling runtime (plan Risk: HIGH).

— Radia
