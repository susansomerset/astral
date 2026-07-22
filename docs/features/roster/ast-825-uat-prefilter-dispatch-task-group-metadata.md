<!-- linear-archive: AST-825 archived 2026-07-22 -->

## Linear archive (AST-825)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-825/uat-prefilter-dispatch-task-missing-task-group-metadata-in-scheduled  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-821 — Get prefilter_company to work  
**Blocked by / blocks / related:** parent: AST-821

### Description

## What failed

In Scheduled Actions / dispatch admin JSON (`GET /api/admin/dispatch_tasks/task_keys`), the schedulable `prefilter` task key appears without `task_group_order`, `task_group_name`, `task_seq`, and related grouping metadata (empty or missing vs sibling company roster keys). Susan sees `prefilter` ungrouped or out of sequence instead of nested under **Company Roster** between `fetch_website` and `fetch_job_pages`.

## Expected

`prefilter` in `task_keys` (and any dispatch-row JSON that surfaces grouping) carries the same **C. Company Roster** grouping metadata as other company-roster dispatch keys, with sequence ordering **after** `fetch_website` **and before** `fetch_job_pages` in the Company Roster section.

## Repro

1. Open admin **Scheduled Actions** (or `GET /api/admin/dispatch_tasks/task_keys`) on staging after AST-821 ship.
2. Inspect the `prefilter` entry in the JSON response.
3. Observe missing/empty `task_group_*` fields while `fetch_website` and `fetch_job_pages` show **C. Company Roster** grouping and correct relative order.
4. Confirm `prefilter` row does not appear between `fetch_website` and `fetch_job_pages` in the Company Roster group.

## Parent AC (quoted inline)

> 1. Given companies in **HOMEPAGE_READY** with persisted **homepage_text** (and **nav_links** when required for link decode), running the **prefilter** scheduled dispatch task produces no `unhandled input_state=HOMEPAGE_READY` warnings.

(Dispatch admin metadata supports Susan configuring and running that prefilter scheduled action in the Company Roster pipeline.)

## Boundaries

* This bug does **not** change: prefilter consult routing, batch evaluate logic, rubric/decode (**AST-823** scope), or `fetch_website` / `fetch_job_pages` scrape behavior.
* Does **not** re-open AST-823 product routing — grouping/sequencing metadata only.

### Comments

#### radia — 2026-06-26T18:21:29.084Z
### Review — `origin/dev...origin/sub/AST-821/AST-825-uat-prefilter-dispatch-task-group-metadata` @ `59867a0`

**Plan fidelity:** Single-component scope held. `dispatch_task_grouping_catalog_key` maps schedulable **`prefilter`** → **`ROSTER_CONFIG["prefilter"]["task_key"]`** (`prefilter_company`) for admin grouping lookup only. `_dispatch_task_key_form_meta` passes `grouping_key` to `_catalog_task_grouping_meta`; entity/trigger/is_scored remain dispatch-keyed via `dispatch_task_admin_defaults` — matches Susan's UAT gap (empty grouping on Scheduled Actions JSON).

**Rubric (§3 / §1):** Config helper in utils; one new config import in `api_admin`. No core/dispatch/roster execution changes, no layer bends, no silent failures or debug-contract changes.

**Tests:** Betty manifest covers config helper and `GET /api/admin/dispatch_tasks/task_keys` — `prefilter` returns Company Roster seq 5 with `entity_type=company`, `trigger_state=HOMEPAGE_READY`.

**fix-now:** None.

**advisory:** Narrow `prefilter`-only map is intentional (not a general alias table per plan). Future roster dispatch keys that diverge from `agent_task` keys should extend this helper rather than duplicating lookup in UI.

**Doc:** `19ac04f` — `docs/features/roster/ast-825-uat-prefilter-dispatch-task-group-metadata.md` § Review.

#### betty — 2026-06-26T18:20:12.530Z
## QA test manifest (AST-825)

**Publish:** `origin/sub/AST-821/AST-825-uat-prefilter-dispatch-task-group-metadata` @ `59867a0` (`merge-tests(AST-825): origin/tests 4d7bb40`)

**Bible shasums (publish ref):**
- `docs/test-bible/ui/api/api_admin.md` → `018050282b35d8bb2ffdd4b976ec819ceb48938a`

**Manifest (test-child — narrowed run):**

1. `tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers::test_dispatch_task_grouping_catalog_key_prefilter_maps_to_company`
2. `tests/component/ui/api/test_api_admin.py::TestAst825PrefilterDispatchTaskKeysGrouping::test_dispatch_task_keys_prefilter_grouping_from_prefilter_company_catalog`
3. `tests/component/ui/api/test_api_admin.py::TestAst739DispatchTaskKeysGrouping` (regression)

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers::test_dispatch_task_grouping_catalog_key_prefilter_maps_to_company \
  tests/component/ui/api/test_api_admin.py::TestAst825PrefilterDispatchTaskKeysGrouping \
  tests/component/ui/api/test_api_admin.py::TestAst739DispatchTaskKeysGrouping \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Betty additions:** `dispatch_task_grouping_catalog_key` config test; `task_keys["prefilter"]` grouping resolves via `prefilter_company` agent_task catalog row.

— Betty

#### katherine — 2026-06-26T18:16:45.620Z
Plan: `https://github.com/susansomerset/astral/blob/sub/AST-821/AST-825-uat-prefilter-dispatch-task-group-metadata/docs/features/roster/ast-825-uat-prefilter-dispatch-task-group-metadata.md`

**Scope:** Single-Component — `dispatch_task_grouping_catalog_key` in config maps dispatch `prefilter` → `prefilter_company` for `_catalog_task_grouping_meta` only; entity/trigger unchanged in `api_admin.py`.

**Conf:** high — seed JSON already has Company Roster seq 5 on `prefilter_company`; API today looks up nonexistent `prefilter` agent_task row.

**Risk:** low — admin JSON grouping only; no consult/dispatch execution path changes.

---

# AST-825 — UAT: prefilter dispatch task missing task_group metadata in Scheduled Actions JSON

- **Linear:** [AST-825 — UAT: prefilter dispatch task missing task_group metadata in Scheduled Actions JSON](https://linear.app/astralcareermatch/issue/AST-825/uat-prefilter-dispatch-task-missing-task-group-metadata-in-scheduled)
- **Parent:** [AST-821 — Get prefilter_company to work](https://linear.app/astralcareermatch/issue/AST-821/get-prefilter-company-to-work)
- **Publish ref:** `origin/sub/AST-821/AST-825-uat-prefilter-dispatch-task-group-metadata`
- **UAT bug of:** [AST-821](https://linear.app/astralcareermatch/issue/AST-821/get-prefilter-company-to-work) — Susan staging re-test after AST-823 ship
- **Related:** [AST-739](https://linear.app/astralcareermatch/issue/AST-739) (DB grouping on `task_keys`), [AST-736](https://linear.app/astralcareermatch/issue/AST-736) (dispatch vs consult key alignment), [AST-823](https://linear.app/astralcareermatch/issue/AST-823) (prefilter consult routing — out of scope here)

Susan opens Admin → **Scheduled Actions** (or `GET /api/admin/dispatch_tasks/task_keys`) after AST-821 ship. The schedulable **`prefilter`** entry lacks **`task_group_order`**, **`task_group_name`**, **`task_seq`**, and **`task_name`** (empty strings / null) while sibling company-roster keys **`fetch_website`** and **`fetch_job_pages`** show **Company Roster** grouping and sort between them. **`prefilter`** therefore renders ungrouped or out of sequence instead of between **Fetch Website** (seq 4) and **Fetch Job Pages** (seq 6).

**Root cause (expected):** Dispatch schedulable key is **`prefilter`**; consult/agent catalog key is **`prefilter_company`** (`ROSTER_CONFIG["prefilter"]["task_key"]`). `_dispatch_task_key_form_meta` passes **`catalog_key = task_key`** into `_catalog_task_grouping_meta`, which reads **`database.get_agent_task("prefilter")`** — no such row. Grouping lives on the current **`prefilter_company`** **`agent_task`** row in `data/admin/agent_task.json` (`task_group_order=3000`, `task_group_name=Company Roster`, `task_seq=5`, `task_name=Prefilter Company`). **AST-736** retired consult→grade alias resolution for grouping; this roster dispatch→consult split was not wired for admin metadata.

**Boundaries:** Grouping/sequencing metadata for **`prefilter`** in admin JSON only. Does **not** change prefilter consult routing (**AST-823**), batch evaluate, rubric/decode, **`fetch_website`** / **`fetch_job_pages`** scrape behavior, or dispatch execution.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add **`dispatch_task_grouping_catalog_key(task_key)`** — map dispatch key **`prefilter`** → **`prefilter_company`** for admin grouping lookup only | utils |
| `src/ui/api/api_admin.py` | Use grouping catalog key in **`_dispatch_task_key_form_meta`** (entity/trigger/is_scored unchanged) | ui |

**Verify only (Betty / qa-child — engineer does not edit in build-child):**

| File | Change |
|------|--------|
| `tests/component/ui/api/test_api_admin.py` | Assert **`task_keys["prefilter"]`** grouping matches **`prefilter_company`** agent_task row (Company Roster, seq 5) |

**No changes expected:** `src/data/database.py`, `src/core/consult.py`, `src/core/roster.py`, `src/core/dispatcher.py`, `data/admin/agent_task.json` (seed already correct on **`prefilter_company`**), frontend React (consumes `task_keys` payload as-is).

---

## Stage 1: Confirm grouping lookup gap (investigation — no product commit unless regression)

**Done when:** Engineer records that **`task_keys["prefilter"]`** returns empty grouping while **`task_keys["fetch_website"]`** and **`task_keys["fetch_job_pages"]`** return Company Roster metadata, and **`get_agent_task("prefilter_company")`** (or repo JSON) holds seq **5** between fetch_website **4** and fetch_job_pages **6**.

1. Confirm seed grouping on repo JSON (read-only):
   ```bash
   python3 -c "
   import json; from pathlib import Path
   rows = {r['task_key']: r for r in json.loads(Path('data/admin/agent_task.json').read_text()) if r.get('current')==1}
   for k in ('fetch_website','prefilter_company','fetch_job_pages','prefilter'):
       r = rows.get(k, {})
       print(k, r.get('task_group_name'), r.get('task_seq'))
   "
   ```
   Expect: **`prefilter`** key absent; **`prefilter_company`** → **`Company Roster`**, seq **5**; **`fetch_website`** seq **4**; **`fetch_job_pages`** seq **6**.

2. Confirm admin API uses direct dispatch key for grouping lookup today:
   ```bash
   rg -n '_dispatch_task_key_form_meta|_catalog_task_grouping_meta|catalog_key' src/ui/api/api_admin.py
   ```
   Expect **`catalog_key = (task_key or "").strip()`** with no roster dispatch→agent resolution.

3. Optional smoke (local app or component-test pattern): call **`GET /api/admin/dispatch_tasks/task_keys`** and inspect **`prefilter`** vs **`fetch_website`** — reproduces Susan's empty grouping before Stage 2.

4. **Stop gate:** If investigation shows **`prefilter`** **`agent_task`** row exists with correct grouping but API still returns empty — post 🛑 on **AST-821** with evidence; do not proceed (different root cause).

---

## Stage 2: Resolve dispatch→agent catalog key for grouping metadata

**Done when:** **`GET /api/admin/dispatch_tasks/task_keys`** returns for **`prefilter`**: `task_group_order="3000"`, `task_group_name="Company Roster"`, `task_seq=5.0`, `task_name="Prefilter Company"` (values from current **`prefilter_company`** **`agent_task`** row); **`entity_type`**, **`trigger_state`**, and **`is_scored`** for **`prefilter`** unchanged (`company`, **`HOMEPAGE_READY`**, scored per existing helpers).

1. In **`src/utils/config.py`**, immediately after **`resolve_dispatch_task_config_key`** (~line 1294), add:

   ```python
   def dispatch_task_grouping_catalog_key(task_key: str) -> str:
       """Agent_task row key for admin grouping metadata when dispatch key differs from consult key."""
       tk = (task_key or "").strip()
       if tk == "prefilter":
           return ROSTER_CONFIG["prefilter"]["task_key"]
       return tk
   ```

   ⚠️ **Decision:** Narrow map for **`prefilter`** only — not a general alias table (**AST-736**). Other company roster schedulable keys already share dispatch and **`agent_task`** strings.

2. In **`src/ui/api/api_admin.py`**, update **`_dispatch_task_key_form_meta`**:
   - Add **`dispatch_task_grouping_catalog_key`** to the existing import from **`src.utils.config`** (same block as **`DISPATCH_SCHEDULABLE_TASK_KEYS`**, etc.).
   - Replace grouping lookup only:
     ```python
     grouping_key = dispatch_task_grouping_catalog_key(task_key)
     ...
     **_catalog_task_grouping_meta(grouping_key),
     ```
   - Keep **`catalog_key = (task_key or "").strip()`** for **`TASK_CONFIG`** entity/trigger reads (unchanged).
   - Update docstring: grouping reads **`agent_task`** via **`dispatch_task_grouping_catalog_key`**; entity/trigger still keyed by dispatch **`task_key`**.

3. Do **not** change **`dispatch_task_keys`** orphan fallback branch, **`list_dtasks`**, or **`_catalog_task_grouping_meta`** signature.

4. Compile check:
   ```bash
   python3 -m py_compile src/utils/config.py src/ui/api/api_admin.py
   ```

5. Manual sanity (engineer): reload **`task_keys`** JSON — **`prefilter`** sorts between **`fetch_website`** and **`fetch_job_pages`** in Scheduled Actions **Company Roster** section; **`prefilter_company`** Manage Tasks entry unchanged.

---

## Self-Assessment

**Scope:** `Single-Component` — Two files at utils/ui boundary: one config helper and one admin metadata resolver; no core dispatch or roster execution.

**Conf:** `high` — Root cause matches existing **`prefilter` / `prefilter_company`** split and **`agent_task.json`** seed; fix mirrors established DB-grouping pattern from **AST-739** with a single roster-specific catalog resolution.

**Risk:** `low` — Wrong grouping key would only mis-bucket Scheduled Actions / Add Task form defaults for **`prefilter`**; dispatch run path and consult routing are untouched.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single helper in config; admin calls it once — no duplicated map in UI layer. |
| §2.1 Config as source of truth | Roster dispatch→consult mapping stays in **`ROSTER_CONFIG`**; admin reads via helper — no inline magic strings in **`api_admin.py`**. |
| §2.4 Batch processing | Not touched. |
| §2.6 State machine | Not touched. |
| §3.3 Imports | **`api_admin`** already imports config; add one symbol — no new cross-layer violations. |
| §3.5 Naming | Helper name describes purpose; **`prefilter`** dispatch key preserved for execution paths. |

No conflicts requiring plan revision.

---

## Review

**Diff:** `origin/dev...origin/sub/AST-821/AST-825-uat-prefilter-dispatch-task-group-metadata` @ `59867a0`

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | Single-component scope held — admin grouping metadata only; no consult routing, dispatch execution, or roster changes |
| Stage 2 | `dispatch_task_grouping_catalog_key` in config maps `prefilter` → `ROSTER_CONFIG["prefilter"]["task_key"]`; `_dispatch_task_key_form_meta` uses `grouping_key` only for `_catalog_task_grouping_meta` — entity/trigger/is_scored still keyed by dispatch `task_key` |
| §2.1 | Roster dispatch→consult split resolved via config helper, not inline UI magic strings |
| §3.3 | One new config import in `api_admin`; no new cross-layer violations |
| Tests | Betty manifest covers config helper and `task_keys["prefilter"]` grouping (Company Roster, seq 5) with entity/trigger regression assertions |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| — | — | No fix-now items |

### Recommended actions

| Severity | Location | Action |
|----------|----------|--------|
| **advisory** | `src/utils/config.py` | Narrow `prefilter`-only map is intentional per plan (not a general alias table). If future roster dispatch keys diverge from `agent_task` keys, extend this helper rather than duplicating lookup in UI — same pattern as `_dispatch_trigger_state_for_task_key`. |

---

## Resolution

**Date:** 2026-06-26  
**Review:** Radia clean — no fix-now items @ `59867a0`; review doc @ `19ac04f`.

**Product:** Unchanged since `e58e30d` — `dispatch_task_grouping_catalog_key` + `_dispatch_task_key_form_meta` grouping lookup only. Betty `merge-tests` @ `59867a0`.

**§9a dry-run:** publish ref merges cleanly into `origin/dev` and `origin/ftr/AST-821-get-prefilter-company-to-work`.

**Handoff:** User Testing — Susan confirms `GET /api/admin/dispatch_tasks/task_keys` shows `prefilter` under Company Roster between `fetch_website` and `fetch_job_pages`.
