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
