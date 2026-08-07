# Admin catalog/API hardcode audit + alphabetical task_key lists

**Linear:** [AST-1214](https://linear.app/astralcareermatch/issue/AST-1214/admin-catalogapi-hardcode-audit-alphabetical-task-key-lists-ui)  
**Parent:** [AST-1185](https://linear.app/astralcareermatch/issue/AST-1185/ui-groupingssequences-alphabetical-task-keyalias-dropdowns-data-driven)  
**Publish ref:** `sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists`

Admin operators need Scheduled Actions (and peer Admin surfaces that consume the same catalog) to offer a **live** task-key picker that includes every current `agent_task` identity — including `fetch_*`, roster gap keys (`gaze`, `prefilter`, …), and alias keys such as `meteorite_grade_do` / `meteorite_grade_get` — sorted **alphabetically by `task_key` string**, with grouping metadata still read from `agent_task` (not parallel phase/seq inventories). Today `GET /api/admin/dispatch_tasks/task_keys` is built from `get_task_keys()` (`TASK_CONFIG` insertion order) plus orphan `dispatch_task` rows, which intentionally omits agent_task-only gap keys (AST-960) and does not guarantee alphabetical JSON key order. This ticket owns that Admin API / enrichment contract only; React section rendering and dropdown polish stay on AST-1215.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_admin.py` | Expand `dispatch_task_keys` membership to live `agent_task` ∪ `TASK_CONFIG` ∪ dispatch orphans; return object with keys inserted in alphabetical `task_key` order; enrich form meta for non-`TASK_CONFIG` catalog keys via existing `_dispatch_*` helpers; no new hard-coded task/section inventories | ui |

**Out of scope (siblings / blockers already User Testing):**

| Owner | What |
|-------|------|
| AST-1215 (Katherine) | React section headers, within-section `task_seq` order, client dropdown UX (may drop redundant `.sort()` once API order is alpha) |
| AST-1183 / AST-1184 | Gaze/Meteorite seed rename; `master_task_key` alias resolve — consume live catalogs only |
| Betty | Component tests that assert AST-960 “gap key absent without dispatch row” (`test_dispatch_task_keys_omits_fetch_jd_gap_excludes_retired`, `test_gap_key_absent_without_db_row`, etc.) — revise at Code Complete; engineer does **not** edit `tests/` |

**Audit findings (pre-plan — do not re-litigate in build):**

- `GET /api/admin/tasks` already lists `agent_task` `current=1` rows `ORDER BY task_key` and attaches DB grouping via `_grouping_from_agent_task_row` — no hard-coded section inventory; leave list order as-is (Manage Tasks re-groups by `task_group_order` / `task_seq` in React).
- `GET /api/admin/vector_feedback/task_keys` returns sorted **rubric owner** keys only — intentional filter, not a full catalog; do not expand.
- `DISPATCH_RETIRED_TASK_KEYS` and `ADMIN_CONFIG` hidden / always-visible lists are config-backed retirement/visibility policy — keep filtering them out of the picker; they are not extraneous section/sequence inventories.
- Jobs UI section configs (`JOBS_*_UI_SECTIONS`, etc.) are non-Admin product pages — out of epic default scope.

## Execution contract

The plan is binding. Execute stages in order. Do not edit React, seed JSON, `TASK_CONFIG` alias contract, or `tests/`. When a step is ambiguous or the codebase has drifted — stop and comment on **AST-1185** (parent) with the Stage N blocked template. No silent file adds.

---

## Stage 1: Live alphabetical Admin task-key catalog

**Done when:** `GET /api/admin/dispatch_tasks/task_keys` (auth admin) returns a JSON object whose keys are the sorted union of (a) every `TASK_CONFIG` key from `get_task_keys()`, (b) every `task_key` from `database.list_candidate_tasks()` (current `agent_task` rows), and (c) non-retired `task_key` values from `list_dispatch_tasks()`, minus `admin_hidden_dispatch_task_keys()` and `DISPATCH_RETIRED_TASK_KEYS`; object key iteration order is alphabetical by `task_key`; payload includes `fetch_jd`, `fetch_culture_pages`, `fetch_job_pages`, `fetch_website`, `gaze`, `prefilter`, `meteorite_grade_do`, and `meteorite_grade_get` when those rows exist in live `agent_task` / `TASK_CONFIG` without requiring a pre-existing `dispatch_task` row; each value still carries `entity_type`, `trigger_state`, `is_scored`, and grouping fields from `_dispatch_task_key_form_meta` / `_catalog_task_grouping_meta`.

1. In `src/ui/api/api_admin.py`, import `_dispatch_trigger_state_for_task_key` from `src.utils.config` alongside the existing `_dispatch_entity_type_for_task_key` import (same import block ~lines 46–88).

2. Immediately above `dispatch_task_keys`, add a module-level helper:

   ```python
   def _admin_dispatch_task_key_catalog() -> dict[str, dict]:
       """Live Admin picker catalog: agent_task ∪ TASK_CONFIG ∪ dispatch orphans, alpha by task_key."""
       membership: set[str] = set(get_task_keys())
       for row in database.list_candidate_tasks():
           tk = (row.get("task_key") or "").strip()
           if tk:
               membership.add(tk)
       for r in list_dispatch_tasks():
           k = (r.get("task_key") or "").strip()
           if k:
               membership.add(k)
       membership -= set(admin_hidden_dispatch_task_keys())
       membership -= set(DISPATCH_RETIRED_TASK_KEYS)
       return {tk: _dispatch_task_key_form_meta(tk) for tk in sorted(membership)}
   ```

3. Replace the body of `dispatch_task_keys()` with:

   ```python
   @admin_bp.route("/dispatch_tasks/task_keys")
   @require_admin
   def dispatch_task_keys():
       """task_key → form meta for Scheduled Actions (and peer Admin pickers).

       Membership is the live union of TASK_CONFIG keys, current agent_task keys
       (including fetch_* and peers), and existing dispatch_task keys — sorted
       alphabetically by task_key. Retired / admin-hidden keys are omitted.
       Grouping fields come from agent_task; no parallel section inventory.
       """
       return jsonify(_admin_dispatch_task_key_catalog())
   ```

4. Do **not** add a frozenset or tuple of gap keys (`fetch_jd`, …) in `api_admin.py` or `config.py` for this membership — live `list_candidate_tasks()` is the source. Do **not** change `get_task_keys()` itself (agent validation stays `TASK_CONFIG`-scoped).

⚠️ **Decision:** Reverse the AST-960 “gap key only if dispatch row exists” picker rule for Admin catalog honesty (parent AC + AST-1214 notes: catalog includes all `agent_task` keys including `fetch_*`). Retirement / hidden filters remain.

---

## Stage 2: Form-meta defaults for agent_task-only catalog keys

**Done when:** For a catalog key present in `agent_task` but absent from `TASK_CONFIG` (e.g. `fetch_jd`), `_dispatch_task_key_form_meta` returns non-empty `entity_type` / `trigger_state` when `_dispatch_entity_type_for_task_key` / `_dispatch_trigger_state_for_task_key` succeed (e.g. `fetch_jd` → `job` / `PASSED_JOBLIST`); keys still in `TASK_CONFIG` keep the existing `dispatch_task_admin_defaults` path; grouping fields still come only from `agent_task` via `dispatch_task_grouping_catalog_key` + `_catalog_task_grouping_meta` (aliases keep their own `agent_task` identity — no React or API alias→master map).

1. In `_dispatch_task_key_form_meta`, after the existing `if task_key in TASK_CONFIG: … dispatch_task_admin_defaults …` block, add a fallback that fills empty fields from the dispatch helpers (no new key lists):

   ```python
   if not entity_type:
       try:
           entity_type = _dispatch_entity_type_for_task_key(task_key) or ""
       except KeyError:
           pass
   if not trigger_state:
       try:
           trigger_state = _dispatch_trigger_state_for_task_key(task_key) or ""
       except KeyError:
           pass
   ```

2. Keep the return shape unchanged (`entity_type`, `trigger_state`, `is_scored`, grouping fields). Do not call `dispatch_task_admin_defaults` for keys outside `TASK_CONFIG` (it raises `KeyError` by design).

3. Do not invent alias→master resolution in this helper — `dispatch_task_grouping_catalog_key` already maps only the known `prefilter` → `prefilter_company` roster split; alias keys use their own `agent_task` row (AST-1184).

⚠️ **Decision:** Prefer existing `_dispatch_*` helpers over copying entity/trigger from a random `dispatch_task` row, so picker defaults stay config-derived even when no schedule row exists yet.

---

## Stage 3: Hardcode audit close-out on touched Admin API paths

**Done when:** Touched paths in `api_admin.py` for this epic contain no new hard-coded task-key membership lists and no hard-coded section/sequence inventories that restate `agent_task` grouping; docstring on `dispatch_task_keys` matches Stage 1 contract; a short Linear comment on AST-1214 lists what was checked and what was intentionally left (retired/hidden config, vector-feedback owner filter, Jobs UI sections).

1. Re-read the Stage 1–2 diff in `src/ui/api/api_admin.py` and confirm there is no new inline set/tuple/list of task keys or section names for membership or display order.

2. Confirm `list_dtasks` still filters retired/hidden via config helpers only (no parallel inventory added).

3. Confirm `list_tasks` / `_enrich_tasks` still attach grouping from the `agent_task` row only (`_grouping_from_agent_task_row`) — no sort/group rewrite in this ticket.

4. Post the audit close-out as the Stage 3 completion comment on **AST-1214** (not parent), including Betty note: existing AST-960 gap-absent assertions must flip to expect live `agent_task` keys present and JSON keys alphabetical.

---

## Self-Assessment

**Scope:** `Single-Component` — one Admin API module (`api_admin.py`); catalog membership + form-meta enrichment only; no React, seed, or core dispatch changes.

**Conf:** `high` — gap is localized to `dispatch_task_keys` / `_dispatch_task_key_form_meta`; helpers and `list_candidate_tasks` already exist; AST-960 tests document the old contract to reverse.

**Risk:** `Medium` — widening the picker to all `agent_task` keys changes operator-visible options and will fail Betty’s AST-960 gap-absent tests until she revises them; alphabetical object key order is a contract sibling UI may rely on.

## CODE_RULES check

- §1.4 / `astral.standards.no-hardcoded-sets` — membership from live catalogs + config retirement/hidden helpers; no new gap-key frozenset.
- §2.1 / `astral.config.config-source-of-truth` — form defaults from existing config `_dispatch_*` / `dispatch_task_admin_defaults`; grouping from DB `agent_task`.
- §2.9 / `astral.patterns.require-auth-on-protected-endpoints` — keep `@require_admin` on `dispatch_task_keys`.
- §3.2 / `astral.layers.ui-config-driven-business-logic` — sort + membership resolved in API before React.
- §3.3 — no new layer violations; continue existing `api_admin` → `database` pattern already used by `_enrich_tasks` / `_catalog_task_grouping_meta`.
- `astral.standards.in-scope-only` — no React (AST-1215), no seed (AST-1183), no alias resolve (AST-1184).
