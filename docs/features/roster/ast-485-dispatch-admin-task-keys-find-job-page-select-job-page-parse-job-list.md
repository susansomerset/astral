# AST-485 — Dispatch admin task_keys: find_job_page, select_job_page, parse_job_list

- **Linear (this ticket):** [AST-485](https://linear.app/astralcareermatch/issue/AST-485/dispatch-admin-task-keys-find-job-page-select-job-page-parse-job-list)
- **Publish ref (plan + implementation cherry-picks):** `origin/sub/AST-461/AST-485-roster-dispatch-admin-task-keys` (**child** of AST-461; not `ftr/AST-485`.)
- **Parent (coordination only):** [AST-461](https://linear.app/astralcareermatch/issue/AST-461/split-roster-locate-and-parse-job-list-run-next-job-list-cache)

## Summary

AST-469 split roster locate/select/parse execution, but **dispatch-layer naming** stayed on legacy **`locate_job_page`** in **`_DISPATCH_TASK_SEED`**, **`config._DISPATCH_TASK_TRIGGER_SEED`** / **`DISPATCH_TASK_SEED_KEYS`**, and existing **`dispatch_task`** rows. Admin **Scheduled Actions → Dispatch Task** create flow reads **`GET /api/admin/dispatch_tasks/task_keys`** from **`database.dispatch_task_seed_templates()`**, so the modal still favors the old locate key and omits **`select_job_page`** and **`parse_job_list`** as selectable template rows. This ticket aligns **dispatch seeds**, **config mirror**, **`dispatch_task`** migrations, **adhoc/workbench metadata**, and **`_build_adhoc_live_content`** with the roster pipeline (**find → select → parse**) while keeping **single runtime path** (**`consult.run_company_task`** → **`roster.run_company_task`**, keyed by **`trigger_state`**, not **`task_key`**) untouched in behavior beyond row renames.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Replace **`locate_job_page`** with **`find_job_page`** in **`_DISPATCH_TASK_SEED`**. Add **`select_job_page`** and **`parse_job_list`** seed entries (**same canonical columns as **`find_job_page`**: **`entity_type: company`**, **`trigger_state: TO_WATCH`**, **`sort_by: updated_at`**, **`batch_call_mode: 0`**). In **`_ensure_dispatch_task_schema`**, idempotent **`UPDATE dispatch_task SET task_key = 'find_job_page' WHERE task_key = 'locate_job_page'`** after schema ensure (same staging block family as **`recheck_no_openings`** / **`gaze`** `sort_by` migrations). Optionally add **`get_dispatch_row_or_seed_preview_meta(task_key)`** (private helper or public thin wrapper): **`dispatch_task`** row **`ORDER BY id LIMIT 1`** if exists, else **`dict` from **`dispatch_task_seed_templates().get(task_key)`** augmented with **`batch_call_mode`** so admin adhoc resolves **`entity_type`**, **`trigger_state`** without poisoning templates when one bad row exists. **If** helper lives in **`database.py`**, **`api_admin`** imports it once — no **`utils→data`** violation. | data |
| `src/utils/config.py` | Rename **`locate_job_page`** → **`find_job_page`** in **`_DISPATCH_TASK_TRIGGER_SEED`**. Append **`select_job_page`** and **`parse_job_list`** with **`{"trigger_state": "TO_WATCH"}`** each. Preserve invariant **`DISPATCH_TASK_SEED_KEYS == frozenset(_DISPATCH_TASK_TRIGGER_SEED.keys())`** (**same commit** as **`database._DISPATCH_TASK_SEED`**). | utils |
| `src/ui/api/api_admin.py` | (**1**) **`adhoc_entities`** (and any **`_resolve_adhoc`** branch that reads **`get_dispatch_task_by_key` only`): resolve config via **`get_dispatch_row_or_seed_preview_meta`** (or inlined equivalent) — **`404`** only when **neither** DB row nor seed exists. (**2**) **`_build_adhoc_live_content`** — **`company`** branch: **`select_job_page`**: assemble **offline** preview string **identically** to **`find_job_page` / **`locate_job_page`** (**`enumerate_array('', nav_links)`** from **`company_data`**) — **⚠️ Decision:** PJL enumerated DOM parity with live **`find_job_page`** is intentionally **preview-only**; document one-line limitation in adjacent comment. Keep **`locate_job_page`** tuple for backward compat alongside **`find_job_page`** until obsolete. **`parse_job_list`**: unchanged keys **`job_page_dom` / **`job_listing_html`**. Extend **`if`** ordering so **`select`** does not fall through to **`website_content`** gaze path. | ui |

**Regression tests (planned)**

| File | Change | Layer |
|------|--------|-------|
| `tests/component/utils/test_config.py` | Extend **`DISPATCH_TASK_SEED_KEYS`** / **`_DISPATCH_TASK_TRIGGER_SEED`** parity assertions: **`find_job_page`** present, **`locate_job_page`** absent; **`select_job_page`** + **`parse_job_list`** listed; **`trigger_state`** all **`TO_WATCH`** for roster locate trio seeds. | tests |
| `tests/component/ui/api/test_api_admin.py` | **`dispatch_task_seed_templates`** mocks / **`adhoc_entities`**: **`select_job_page`** returns **`200`** with **`company` / **`TO_WATCH`** using seed fallback when **`get_dispatch_task_by_key`** would be **`None`** (monkeypatch DB side). **`_build_adhoc_live_content`**: **`select_job_page`** with stub company **`nav_links`** matches **`find_job_page`** string. Migrate assertion off bare **`locate_job_page`** if seed removes it (**keep tuple** `(locate, find)` in implementation until dropped). **`task_keys`** response includes new keys (**integration-style GET** against real **`dispatch_task_seed_templates`** if test DB empty). | tests |

## Stage 1: Dispatch seeds + config mirror + migrate existing rows

**Done when:** Fresh DB ensure path creates templates with **`find_job_page`** + **`select_job_page`** + **`parse_job_list`**; **`locate_job_page`** absent from seed dicts; **`config.DISPATCH_TASK_SEED_KEYS`** matches **`len(_DISPATCH_TASK_TRIGGER_SEED)`** roster expansion; **`UPDATE`** migrates legacy **`dispatch_task`** rows; **`dispatch_task_preview_meta`** (**or inlined fallback**) behaves for keys with zero DB rows.

1. **`src/data/database.py` — `_DISPATCH_TASK_SEED`**  
   - Remove key **`locate_job_page`**.  
   - Add **`find_job_page`**: **`{"entity_type": "company", "trigger_state": "TO_WATCH", "sort_by": "updated_at", "batch_call_mode": 0}`** (literal copy from old **`locate_job_page`** row).  
   - Add **`select_job_page`**, **`parse_job_list`**: **identical dict** shallow copy (**`dict(v)`**) acceptable.

2. **`_ensure_dispatch_task_schema`**: Append idempotent **`UPDATE`** (with comment **`AST-485`**) **`SET task_key='find_job_page' WHERE task_key='locate_job_page'`**.

3. **`src/utils/config.py` — `_DISPATCH_TASK_TRIGGER_SEED`**  
   - Replace **`locate_job_page`** with **`find_job_page`**.  
   - Append **`select_job_page`**, **`parse_job_list`**: **`{"trigger_state": "TO_WATCH"}`** each.

4. Verify **`dispatch_task_seed_templates()`** keys drive **`tests/component/ui/api`** expectations where monkeypatched.

⚠️ **Decision — UNIQUE `(candidate_id, trigger_state)`:** Only **one** scheduled **`TO_WATCH`** company dispatch row exists per candidate. **`find_job_page`**, **`select_job_page`**, and **`parse_job_list`** seeds share **defaults** (`TO_WATCH`). Admin operators **rename / recreate** rows — they **cannot** stack three concurrent **`TO_WATCH`** roster rows (**409 UNIQUE**); labels are mutually exclusive bookkeeping for the **same** scheduler slot (**run_time path identical** regardless of **`task_key` string**, see **`consult.run_company_task`**). Document in builder Linear comment (`AST-485` footgun).

⚠️ **Decision — AST-469 / JOBS_FOUND manual row:** Separate **`JOBS_FOUND`** **`find_job_page`** row remains **Susan-created** (**different **`trigger_state`**, UNIQUE OK**). Seeds do **not** auto-insert **`JOBS_FOUND`** rows (**out of AST-485** unless Susan requests migration).

### Self-review (Stage 1 vs ASTRAL_CODE_RULES)

| Rule | Notes |
|------|-------|
| **§2.1 config** | Roster **`ROSTER_CONFIG["locate_job_page"]`** name **unchanged** (ticket boundary — no relocate/parse logic edits). **`_DISPATCH_TASK_SEED`** + **`config` mirror updated same commit**. |
| **§1.3 DRY** | Seed duplication across three roster keys intentional — admins pick label; literals kept adjacent with **one-line** comment pointing to **`find_job_page`** canonical defaults. |

---

## Stage 2: Admin adhoc/workbench resolution + **`_build_adhoc_live_content`**

**Done when:** **`GET /api/admin/adhoc/entities`** works for **`select_job_page`** / **`parse_job_list`** on DBs **without prior scheduled rows** for those keys (**seed fallback shape** mirrors **`dispatch_task`** row **`entity_type`**, **`trigger_state`**, **`batch_call_mode`** as needed); **`select_job_page` adhoc preview** returns non-empty when **`nav_links`** populated (**same shaping as **`find_job_page`**).

1. **`api_admin.adhoc_entities`**: Replace **`get_dispatch_task_by_key`**-only lookup with **`get_dispatch_row_or_seed_preview_meta`** (name as implemented in Stage 1) — **`404`** if **`unknown task_key`** (**neither DB sample row nor seed templates**).

2. **`api_admin._build_adhoc_live_content`**:  
   - Extend **`company`** **`entity_type`** branch **`before`** gaze **`website_content` fallback**: **`if task_key == "select_job_page"`**: same body as **`find_job_page`** / **`locate_job_page`** (**`enumerate_array('', nav_links)`**).  
   - Preserve **`parse_job_list`** branch.

3. Thread **`_resolve_adhoc`** if it independently resolves **`unknown task_key`** — **mirror** fallback (**grep **`get_dispatch_task_by_key`** in **`api_admin.py`** and align all call sites touched by **`AST-485`**).

### Self-review (Stage 2 vs ASTRAL_CODE_RULES)

| Rule | Notes |
|------|------|
| **§3.3 imports** | **`api_admin → data`** only — allowed. |

---

## Stage 3: Tests + **`pytest` sanity**

**Done when:** Targeted **`pytest`** subsets green (**`tests/component/utils/test_config.py`**, **`tests/component/ui/api/test_api_admin.py`**) covering seed parity + **`adhoc_entities`** fallback + **`_build_adhoc_live_content`** for **`select_job_page`**.

1. Run (**engineer adjusts paths**): **`pytest tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers -q`** (or successor class / add **`AST-485`** test class beside it). **`pytest tests/component/ui/api/test_api_admin.py -k "adhoc or dispatch_task_keys or adhoc_live" -q`** (tight **`-k`** per discovered test names).

2. **No frontend file edits** Katherine-only — **explicitly omit** **`AdminScheduledActions.tsx`** unless copy breaks compile (**ticket boundary**).

---

## Execution contract (developer agent)

Follow **plan-astral § Execution contract**. **Stopping rule:** **`run_company_task` / **`dispatcher`** change is **NOT** requested — no PLUMBING **`task_key`** through **`consult.run_company_task`** this ticket. If **`select_job_page` scheduled AUTO** semantics beyond **`trigger_state`** are required discovered mid-build, **`🛑`** comment on **[AST-485](https://linear.app/astralcareermatch/issue/AST-485/dispatch-admin-task-keys-find-job-page-select-job-page-parse-job-list)** with options.

---

## Self-Assessment

**Scope:** `Single-Component` — touch **`dispatch_task` seed**, **`config`** mirror (**keys only**), **`api_admin`** adhoc/workbench helpers (**no roster core** / **dispatcher** branching).

**Conf:** `high` — pattern mirrors **`NO_OPENINGS` → `find_job_page` **` migration + **`adhoc_entities`** bootstrap; **`UNIQUE` footgun documented**.

**Risk:** `low` — mis-seeded **`task_key`** would skew admin defaults / previews; **`locate_job_page` DB migration eliminates silent legacy drift** — runtime roster paths remain **`trigger_state`**-driven.

---

## Self-review vs ASTRAL_CODE_RULES (whole plan)

| Rule | Conflict? |
|------|-----------|
| **§1.3 DRY** | Three roster seed clones — justified + documented (**Stage 1**). |
| **§2.1 config** | **Same-commit **`database`** + **`config`** seed key sync** (`DISPATCH_TASK_SEED_KEYS`). |
| **§2.4 batch processing** | **No changes** **`claim`/clear`** batch envelope. |
| **§2.6 state machine** | **No new company states** (**`TO_WATCH`** default preserves AST-469). |
| **§3.3 imports** | **No new **`utils → data`****; **`ui → data`** helper import only if helper defined **`database.py`.** |
| **§3.5 naming** | **`find_job_page` dispatch **`task_key`** aligns with **`roster.find_job_page`**; **`locate_job_page`** removed from seeds (migrate DB). |

---

## Review stub (post-build — build-astral §11)

No PR opened from this lane per workflow; architect opens PR at **PR Ready** after **UAT**.

| Item | Value |
|------|-------|
| **Integration branch** | `dev-hedy` |
| **Feat commit (`dev-hedy`)** | `5b7625ef07e65fc7e54d7b27dc4295007debbdb4` |
| **Publish ref** | `origin/sub/AST-461/AST-485-roster-dispatch-admin-task-keys` |
| **Notes** | **Betty** landed Stage 3 component tests + `docs/ASTRAL_TEST_BIBLE.md` manifest lines on the publish ref; engineer commits stay **`tests/`**-free (`resolve-astral`). |

## Review

**Diff:** **`git diff origin/dev...224e5040`** (engineering publish tip **`224e5040`** before Radia docs handoff).

Radia scanned plan fidelity (Stages 1–3), **`ASTRAL_CODE_RULES`** (§2.1 config vs DB seed parity, §3.3 layering for **`api_admin → database`**), **`_ensure_dispatch_task_schema`** migrations against legacy **`NO_OPENINGS`/`find_job_page`** remap, plus rubric **B1** import layout on touched UI file.

### What’s solid

- **`_DISPATCH_TASK_SEED`** roster trio **`find_job_page` / `select_job_page` / `parse_job_list`** with **`TO_WATCH`** defaults; **`locate_job_page`** removed from seeds; **`config._DISPATCH_TASK_TRIGGER_SEED`** and **`DISPATCH_TASK_SEED_KEYS`** stay keyed in sync.
- Schema ensure: **`locate_job_page` → `find_job_page`** runs **before** the **`NO_OPENINGS` AND `task_key = 'find_job_page'` → `recheck_no_openings`** update, so **`NO_OPENINGS` + locate** rows remap correctly **and** true roster **`find`** rows in **`NO_OPENINGS`** still migrate to **`recheck_no_openings`**.
- **`get_dispatch_row_or_seed_preview_meta`** + **`api_admin.get_dispatch_task_by_key`** shim restores **`adhoc_entities`** **`200`** for roster keys **without** a sample **`dispatch_task`** row.
- **`_build_adhoc_live_content`** extends **`locate_job_page` / `find_job_page`** nav preview to **`select_job_page`** with an explicit AST-485 comment (preview parity only).
- Component coverage: **`task_keys`** GET omits **`locate_job_page`** from seeded catalog; **`select_job_page`** adhoc **`entities`** monkeypatch path; **`TestAst471DispatchConfigHelpers`** roster trio shape check.

### Issues

| Severity | Topic | Detail |
| --- | --- | --- |
| **fix-now** | **Imports (B1 / §1.2)** | **`src/ui/api/api_admin.py`**: module-level **`def get_dispatch_task_by_key`** sits **between** the **`database` import block** and **`from src.core.consult import …`**. Imports must be contiguous at top; relocate the shim **below** all imports before **`resolve-astral`** re-publish (no behavior change intended). |
| **discuss** | **Ticket purity** | Same **`feat(AST-485)`** commit bundles **`gaze_board`** **`sort_by`**: **`updated_at` → `last_scan_at`** in **`_ensure_dispatch_task_schema`**. Fits **AST-482** lineage; confirm deliberate single-lane hitchhike vs peeled commit so **`git blame`** stays traceable. |
| **discuss** | **Bible appendix scope** | **`test(AST-485)`** introduces **`ASTRAL_TEST_BIBLE.md`** **`§§7.13y–7.13zc`** (**AST-479..483** + **485**). If intentional doc catch-up alongside manifest, OK; otherwise consider ticket-scoped **`§7.13zc`** only. |
| **advisory** | **Plan stub hygiene** | **`## Review stub`** still says **`tests/` untouched** (**Betty**) while branch adds **`pytest`** + bible lines — refresh narrative when archiving the lane so historians aren’t contradicted. |

### Recommended actions

| Priority | Owner | Action |
| --- | --- | --- |
| P1 | Engineer | **`fix-now`**: reorder **`api_admin`** imports (**§1.2**) on **`resolve-astral`**; **`cherry-pick`** Radia doc SHA per **`review-astral`** §6. |
| P2 | Engineer / Betty | **`discuss`**: confirm **`gaze_board`** migrate + bible sibling sections are intentional ride-alongs; annotate in **Linear** or split if purity matters for **AST-482** / QA audit. |

---

## Resolution (`resolve-astral`)

- **Date:** 2026-05-24.
- **`fix-now`**: `src/ui/api/api_admin.py` — moved **`get_dispatch_task_by_key`** below **all** module imports (rubrics **§1.2 / B1**); no behavior change (**Radia** review thread AST-485).
- **`discuss`** (*ticket purity / bible scope*): no separate **`@susan`** directive in-thread; **`gaze_board`** `sort_by` migrate and bible **`§§7.13y–7.13zc`** remain as-delivered with **`feat(AST-485)` / `test(AST-485)`** on the integration line — peel only if backlog requests **`git blame`** isolation for **AST-482** lineage.
- **Plan doc:** **`## Review stub`** narrative updated (**advisory** — tests + bible landed on **`sub/*`** by **Betty**).
