# Admin catalog/API hardcode audit + alphabetical task_key lists

**Linear:** [AST-1214](https://linear.app/astralcareermatch/issue/AST-1214/admin-catalogapi-hardcode-audit-alphabetical-task-key-lists-ui)  
**Parent:** [AST-1185](https://linear.app/astralcareermatch/issue/AST-1185/ui-groupingssequences-alphabetical-task-keyalias-dropdowns-data-driven)  
**Publish ref:** `sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists`

Admin operators need Scheduled Actions (and peer Admin surfaces that consume the same catalog) to offer a **live** task-key picker that includes every current `agent_task` identity — including `fetch_*` and other agent_task-only gap peers, plus alias keys such as `meteorite_grade_do` / `meteorite_grade_get` — sorted **alphabetically by `task_key` string**, with grouping metadata still read from `agent_task` (not parallel phase/seq inventories). Today `GET /api/admin/dispatch_tasks/task_keys` is built from `get_task_keys()` (`TASK_CONFIG` insertion order) plus orphan `dispatch_task` rows, which intentionally omits agent_task-only gap keys (AST-960). Flask’s `jsonify` already emits sorted object keys by default; this ticket still builds membership with `sorted()` so alphabetical order is an explicit contract, not only a provider default. New catalog keys must also be **writable** as first-class options (POST/PUT must not 400/`Unknown task_key` after the form meta fills). This ticket owns that Admin API / config-defaults contract only; React section rendering and dropdown polish stay on AST-1215.

### Product call — scheduling gazer / roster / inflow runtime hops

**Call (this ticket):** Operators **may** create and update Scheduled Actions `dispatch_task` rows for the seven agent_task-only keys that resolve via `_dispatch_*` helpers: `fetch_culture_pages`, `fetch_jd`, `fetch_job_pages`, `fetch_website`, `gaze`, `inflow_discovery`, `recheck_no_openings`.

**Why:** Parent AST-1185 AC requires those identities as first-class catalog options (alphabetical dropdowns covering all `agent_task` keys including `fetch_*`). They already have live `agent_task` rows, working dispatch runners when a row exists, and resolvable entity/trigger/sort defaults. AST-960’s companion gates (picker omit + `dispatch_task_admin_defaults` `KeyError` + Admin `Unknown task_key`) treated them as “runtime-only / not TASK_CONFIG catalog”; this epic **intentionally reverses both the picker rule and the defaults/write gate** so the form is not a dead end.

**Rejected alternative:** picker-yes / writer-no (display-only + known 400) — contradicts “first-class options” and leaves a filled Save that fails.

**Not escalated to Archie:** the product call is named here so build/Betty/Joan share one reading; if Archie overrides to writer-no, reopen Plan Discuss — do not invent a third shape mid-build.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_admin.py` | Expand `dispatch_task_keys` membership to live `agent_task` ∪ `TASK_CONFIG` ∪ dispatch orphans; build with `sorted(membership)`; enrich form meta for non-`TASK_CONFIG` catalog keys via `_dispatch_*` helpers; align `_dispatch_task_key_trigger_error` so helper-resolvable gap keys are accepted while preserving `unsupported entity_type` wording for in-`TASK_CONFIG` unschedulable keys | ui |
| `src/utils/config.py` | Extend `dispatch_task_admin_defaults` so keys absent from `TASK_CONFIG` but resolvable via `_dispatch_entity_type_for_task_key` / `_dispatch_trigger_state_for_task_key` return the same defaults shape (entity/trigger/sort_by/batch_call_mode) | utils |

**Side effects of the `dispatch_task_admin_defaults` change (same function — not new Files Changed rows):**

- `_ensure_dispatch_task_schema` (`src/data/database.py`) — today `except KeyError: continue` leaves NULL columns on any gap-key row; after this change, schema-ensure **backfills** entity/trigger/sort/batch_call_mode for those rows. Expected and correct once rows exist; no separate stage.
- `get_dispatch_row_or_seed_preview_meta` → `get_dispatch_task_by_key` → `/adhoc/entities` — today 404s for the seven keys (defaults raised); after this change returns 200 with resolved meta. Ad-hoc already lists them via `/api/admin/tasks`; this fixes that dead end. Parent epic scopes Admin grouping/dropdown honesty; treat the 404→200 as an intentional consequence of shared defaults, not React work. Betty: expect 200 not 404 for those keys on `/adhoc/entities` when form meta resolves.

**Out of scope (siblings / blockers already User Testing):**

| Owner | What |
|-------|------|
| AST-1215 (Katherine) | React section headers, within-section `task_seq` order, client dropdown UX. Do **not** drop client `.sort()` solely because Flask sorts — keep or drop based on product preference; API still uses `sorted(membership)` |
| AST-1183 / AST-1184 | Gaze/Meteorite seed rename; `master_task_key` alias resolve — consume live catalogs only |
| Betty | See Stage 3 Betty contract (full invalidation set); engineer does **not** edit `tests/` |

**Audit findings (pre-plan — do not re-litigate in build):**

- `GET /api/admin/tasks` already lists `agent_task` `current=1` rows `ORDER BY task_key` and attaches DB grouping via `_grouping_from_agent_task_row` — no hard-coded section inventory; leave list order as-is (Manage Tasks re-groups by `task_group_order` / `task_seq` in React).
- `GET /api/admin/vector_feedback/task_keys` returns sorted **rubric owner** keys only — intentional filter, not a full catalog; do not expand.
- `DISPATCH_RETIRED_TASK_KEYS` and `ADMIN_CONFIG` hidden / always-visible lists are config-backed retirement/visibility policy — keep filtering them out of the picker; they are not extraneous section/sequence inventories.
- Jobs UI section configs (`JOBS_*_UI_SECTIONS`, etc.) are non-Admin product pages — out of epic default scope.
- On current tip, the **seven** agent_task-only keys that join the picker (absent from `TASK_CONFIG`) are exactly: `fetch_culture_pages`, `fetch_jd`, `fetch_job_pages`, `fetch_website`, `gaze`, `inflow_discovery`, `recheck_no_openings`. `prefilter` and `inflow_resolve_website` are **not** current `agent_task` keys (roster ships `prefilter_company`, already in `TASK_CONFIG`) — they must **not** appear in picker Done-when expectations. After Stage 2 they **can** pass the writer gate if somehow POSTed (helpers resolve) — intentional reverse asymmetry vs round-1; do not add them to the picker without an `agent_task` / `TASK_CONFIG` row.

## Execution contract

The plan is binding. Execute stages in order. Do not edit React, seed JSON, `TASK_CONFIG` alias contract, or `tests/`. When a step is ambiguous or the codebase has drifted — stop and comment on **AST-1185** (parent) with the Stage N blocked template. No silent file adds.

---

## Stage 1: Live alphabetical Admin task-key catalog

**Done when:** `GET /api/admin/dispatch_tasks/task_keys` (auth admin) returns a JSON object whose keys are the sorted union of (a) every `TASK_CONFIG` key from `get_task_keys()`, (b) every `task_key` from `database.list_candidate_tasks()` (current `agent_task` rows), and (c) non-retired `task_key` values from `list_dispatch_tasks()`, minus `admin_hidden_dispatch_task_keys()` and `DISPATCH_RETIRED_TASK_KEYS`; the Python dict is built with `sorted(membership)` (alphabetical by `task_key`); with live seed on this tip the seven agent_task-only keys above are present **without** requiring a pre-existing `dispatch_task` row, and aliases `meteorite_grade_do` / `meteorite_grade_get` are present via `TASK_CONFIG` / `agent_task`; each value still carries `entity_type`, `trigger_state`, `is_scored`, and grouping fields from `_dispatch_task_key_form_meta` / `_catalog_task_grouping_meta`.

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
       alphabetically by task_key via sorted(membership). Retired / admin-hidden
       keys are omitted. Grouping fields come from agent_task; no parallel
       section inventory.
       """
       return jsonify(_admin_dispatch_task_key_catalog())
   ```

4. Do **not** add a frozenset or tuple of gap keys (`fetch_jd`, …) in `api_admin.py` or `config.py` for this membership — live `list_candidate_tasks()` is the source. Do **not** change `get_task_keys()` itself (agent validation stays `TASK_CONFIG`-scoped).

⚠️ **Decision:** Reverse the AST-960 “gap key only if dispatch row exists” **picker** rule for Admin catalog honesty (parent AC + AST-1214 notes). Retirement / hidden filters remain. Keep `sorted(membership)` even though Flask `jsonify` currently sorts keys — alphabetical order is an explicit product contract.

---

## Stage 2: Form-meta defaults + first-class write path for gap keys

**Done when:** For each of the seven agent_task-only keys, `_dispatch_task_key_form_meta` returns non-empty `entity_type` / `trigger_state` from `_dispatch_*` helpers (e.g. `fetch_jd` → `job` / `PASSED_JOBLIST`); `_dispatch_task_key_trigger_error("fetch_jd", "PASSED_JOBLIST")` returns `None`; `_dispatch_task_key_trigger_error("inflow_discovery", "ACTIVE_SEARCH")` returns `None` (not `Unknown task_key`); `dispatch_task_admin_defaults("fetch_jd")` returns a defaults dict (does not raise); POST `/api/admin/dispatch_tasks` with a valid candidate + `task_key=fetch_jd` + `trigger_state=PASSED_JOBLIST` succeeds (201); a registered-but-unschedulable `TASK_CONFIG` key that fails entity resolve (e.g. `gaze_email` with a dummy trigger) still returns wording containing `unsupported entity_type`, not `Unknown task_key`; keys still in `TASK_CONFIG` with resolvable defaults keep the existing happy path; grouping fields still come only from `agent_task` via `dispatch_task_grouping_catalog_key` + `_catalog_task_grouping_meta`.

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

2. In `_dispatch_task_key_trigger_error` (`src/ui/api/api_admin.py` ~1055), **replace** the hard `if tk not in TASK_CONFIG: return f"Unknown task_key: …"` gate (retired check stays first) with helper-first acceptance that **preserves** known-but-unschedulable wording:

   ```python
   # After retired check:
   try:
       et = _dispatch_entity_type_for_task_key(tk)
   except KeyError:
       if tk in TASK_CONFIG:
           return f"task_key {tk!r} has unsupported entity_type"
       return f"Unknown task_key: {tk!r}"
   ts = (trigger_state or "").strip()
   if not ts:
       return "trigger_state is required"
   if et not in ENTITY_TYPES:
       return f"task_key {tk!r} has unsupported entity_type {et!r}"
   # … keep the existing registry / hop-label validation that follows today
   # (dispatch_entity_state_registry, parse_dispatch_hop_label, is_dispatch_chain_trigger).
   # Delete the duplicate `try: et = _dispatch_entity_type_for_task_key` block that
   # currently sits after the old TASK_CONFIG membership check.
   ```

3. In `src/utils/config.py`, extend `dispatch_task_admin_defaults` so that when `tk not in TASK_CONFIG`, it still returns defaults if the `_dispatch_*` helpers succeed — same shape as the registered path (no frozenset of gap keys). This **reverses the AST-960 defaults gate** for helper-resolvable runtime hops (product call above):

   ```python
   # After retired check, replace bare `if tk not in TASK_CONFIG: raise KeyError(...)`
   # with:
   if tk not in TASK_CONFIG:
       try:
           entity_type = _dispatch_entity_type_for_task_key(tk)
           override = (trigger_state or "").strip()
           effective_ts = override if override else _dispatch_trigger_state_for_task_key(tk)
           return {
               "entity_type": entity_type,
               "trigger_state": effective_ts,
               "sort_by": _dispatch_sort_by_for(entity_type, effective_ts),
               "batch_call_mode": _dispatch_batch_call_mode_for(tk),
           }
       except KeyError as exc:
           raise KeyError(f"dispatch_task_admin_defaults: unknown task_key {tk!r}") from exc
   # Existing TASK_CONFIG body (gaze_email carve-out, etc.) unchanged below.
   ```

4. Keep `_dispatch_task_key_form_meta` return shape unchanged. Do not invent alias→master resolution — `dispatch_task_grouping_catalog_key` already maps only the known `prefilter` → `prefilter_company` roster split; alias keys use their own `agent_task` row (AST-1184).

⚠️ **Decision (Joan round=1 + round=2):** Gap keys are **first-class writable** Scheduled Actions options (product call). Align picker, form meta, `_dispatch_task_key_trigger_error`, and `dispatch_task_admin_defaults` / `save_dispatch_task` on the same helper-resolvable contract. Preserve `unsupported entity_type` for in-`TASK_CONFIG` unschedulable keys.

---

## Stage 3: Hardcode audit close-out + Betty contract

**Done when:** Touched paths contain no new hard-coded task-key membership lists and no hard-coded section/sequence inventories that restate `agent_task` grouping; docstring on `dispatch_task_keys` matches Stage 1; Linear Stage 3 comment on **AST-1214** includes the exact Betty invalidation set below.

1. Re-read the Stage 1–2 diff in `api_admin.py` + `config.py` and confirm there is no new inline set/tuple/list of task keys or section names for membership or display order.

2. Confirm `list_dtasks` still filters retired/hidden via config helpers only (no parallel inventory added).

3. Confirm `list_tasks` / `_enrich_tasks` still attach grouping from the `agent_task` row only — no sort/group rewrite in this ticket.

4. Post the audit close-out on **AST-1214** with this **Betty contract** (exact — not “etc.”):

   **A. Admin picker / `task_keys` endpoint (`tests/component/ui/api/test_api_admin.py`) — flip presence:**

   - `TestAst796FetchJdRetiredDispatchKeys::test_dispatch_task_keys_omits_fetch_jd_gap_excludes_retired`
   - `TestAst960TaskKeysNoFrozensetInventory::test_gap_key_absent_without_db_row`

   Seven keys present without a dispatch row (live/`list_candidate_tasks`):  
   `fetch_culture_pages`, `fetch_jd`, `fetch_job_pages`, `fetch_website`, `gaze`, `inflow_discovery`, `recheck_no_openings`  
   Stay absent from picker: `prefilter`, `inflow_resolve_website`

   **B. Admin write validator (`tests/component/ui/api/test_api_admin.py`) — flip `Unknown task_key`:**

   - `TestAst804CandidateDispatchAdminValidation::test_dispatch_task_key_trigger_error_candidate_paths` — today asserts `_dispatch_task_key_trigger_error("inflow_discovery", "ACTIVE_SEARCH")` contains `Unknown task_key`; after Stage 2 it must return `None` (or otherwise accept). Keep other assertions in that test that still apply.

   **C. Config defaults KeyError (`tests/component/utils/test_config.py`) — flip `pytest.raises(KeyError, match="unknown task_key")` on `dispatch_task_admin_defaults` for helper-resolvable keys:**

   | Class :: test | Key |
   |---|---|
   | `TestAst796FetchJdSchedulableCutover::test_fetch_jd_gazer_hop_not_task_config_catalog` | `fetch_jd` |
   | `TestAst719FetchJobPagesConfig::test_dispatch_registry_and_pjl_data_keys` | `fetch_job_pages` |
   | `TestAst701FetchWebsiteConfig::test_dispatch_registry_and_homepage_text_key` | `fetch_website` |
   | `TestAst874FetchCulturePagesConfig::test_gazer_and_dispatch_registry` | `fetch_culture_pages` |
   | `TestAst505InflowDiscoveryConfig::test_inflow_discovery_dispatch_admin_defaults` | `inflow_discovery` |

   **Still raise `unknown task_key` (not agent_task / not helper-as-catalog on this tip — keep KeyError unless the test’s other assertions require a rewrite):**

   - `TestAst702PrefilterBatchConfig::test_prefilter_dispatch_batch_mode_and_defaults` for `prefilter` — defaults may now **succeed** if helpers resolve; Betty must update this assertion to expect a defaults dict (writer more permissive than picker — intentional).
   - `TestAst506InflowResolveConfig::test_inflow_resolve_website_dispatch_admin_defaults` for `inflow_resolve_website` — same: helpers resolve → expect defaults dict, not KeyError.

   **D. Keep passing (unless assertion text ties to old wording):** other `dispatch_tasks/task_keys` endpoint tests in `test_api_admin.py` (including `test_ast485_dispatch_task_keys_roster_seeds_minus_locate_template`); `test_helper_unknown_task_key_wording` / registered-but-unschedulable paths that expect `unsupported entity_type`.

   **E. Harness / new coverage:**

   - Patch `admin_mod.database.list_candidate_tasks` (not only `list_dispatch_tasks`) for picker membership determinism.
   - Raw-body assertion that JSON object key order is alphabetical.
   - Write-path: POST create accepts at least one gap key (e.g. `fetch_jd` + `PASSED_JOBLIST`).
   - Optional: `/adhoc/entities` for a gap key returns 200 (was 404) — consequence of shared defaults.

---

## Self-Assessment

**Scope:** `Single-Component` — Admin catalog + write-validator alignment in `api_admin.py`, plus `dispatch_task_admin_defaults` in `config.py` so gap keys are first-class; no React, seed, or dispatch runner changes.

**Conf:** `high` — product call named (schedule runtime hops: yes); Betty invalidation spans Admin + config files explicitly; known-but-unschedulable wording preserved.

**Risk:** `Medium` — widens picker + allows creating schedule rows for gazer/inflow hops that AST-960 blocked; schema-ensure backfill and Ad-hoc entities 404→200 are intentional side effects; Betty revises ~9+ assertions across two files.

## CODE_RULES check

- §1.4 / `astral.standards.no-hardcoded-sets` — membership from live catalogs + config retirement/hidden helpers; no new gap-key frozenset; defaults via helpers not a parallel map.
- §2.1 / `astral.config.config-source-of-truth` — form/write defaults from config `_dispatch_*` / extended `dispatch_task_admin_defaults`; grouping from DB `agent_task`.
- §2.9 / `astral.patterns.require-auth-on-protected-endpoints` — keep `@require_admin` on `dispatch_task_keys` and mutate routes.
- §3.2 / `astral.layers.ui-config-driven-business-logic` — membership + alpha order + write acceptance resolved in API/config before React.
- §3.3 — no new layer violations; continue existing `api_admin` → `database` catalog reads.
- `astral.standards.in-scope-only` — no React (AST-1215), no seed (AST-1183), no alias resolve (AST-1184); Ad-hoc 404→200 noted as shared-defaults consequence only.
- `orch.pipeline.plan-is-bible` — write-path + product call + Betty breadth documented so the executor does not ship a picker that 400s on Save or under-count Betty work.

## Revisions

Revision 1 — 2026-08-07  
Driven by: Joan `[plan-discuss] round=1 concern` (fix-now: Stage 1 widens picker to 7 keys the writer rejects; discuss: gap-key list off by two / Betty exact pair; discuss: alphabetical already true via Flask; nit: patch `list_candidate_tasks`).  
Changes: Chose first-class writable gap keys — extend `_dispatch_task_key_trigger_error` + `dispatch_task_admin_defaults` (adds `config.py` to Files Changed); corrected Done-when to the exact seven agent_task-only keys (dropped `prefilter` / `inflow_resolve_website`); corrected alphabetical premise (Flask already sorts; keep `sorted()` as contract); pinned Betty invalidation to two tests + seven-key list + `list_candidate_tasks` patch + raw-body key-order + write-path coverage.

Revision 2 — 2026-08-07  
Driven by: Joan `[plan-discuss] round=2 concern` (fix-now: Betty contract understates invalidation — `test_config.py` KeyError sites + Admin `Unknown task_key` for `inflow_discovery`; product call on scheduling runtime hops; discuss: other `dispatch_task_admin_defaults` call sites; discuss: `unsupported entity_type` wording; discuss: writer more permissive than picker for `prefilter` / `inflow_resolve_website`).  
Changes: Named product call — operators **may** schedule the seven gazer/roster/inflow agent_task hops (reverse AST-960 defaults gate with picker); expanded Betty contract sections A–E (Admin picker pair, Admin validator, five+ config KeyError flips including `prefilter`/`inflow_resolve_website` now succeeding, wording keepers, harness); preserved `unsupported entity_type` for in-`TASK_CONFIG` unschedulable keys; documented schema-ensure backfill + `/adhoc/entities` 404→200 as intentional side effects; noted writer>picker for non-agent_task helper keys as intentional.
