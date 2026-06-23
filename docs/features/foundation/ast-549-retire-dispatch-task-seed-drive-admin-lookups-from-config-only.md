<!-- linear-archive: AST-549 archived 2026-06-15 -->

## Linear archive (AST-549)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-549/retire-dispatch-task-seed-drive-admin-lookups-from-config-only  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-484 — Strengthen the relationships between lookup lists in the UI and live values in config  
**Blocked by / blocks / related:** parent: AST-484; blocks: AST-550

### Description

## What this implements

Retire `database._DISPATCH_TASK_SEED` and the `config._DISPATCH_TASK_TRIGGER_SEED` mirror. Derive dispatch admin defaults from `TASK_CONFIG` keys plus `JOB_STATES` / `COMPANY_STATES` tuples only. Fix `GET /api/admin/dispatch_tasks/task_keys` so config keys are authoritative (no seed merge that overrides config). Fix adhoc dispatch preview (`get_dispatch_row_or_seed_preview_meta`) to use config-built metadata instead of dispatch seed templates. Align with parent epic rule: no seeds, defaults, or fallbacks for allowed values — missing config is crash-worthy.

## Acceptance criteria

1. `database._DISPATCH_TASK_SEED` and `config._DISPATCH_TASK_TRIGGER_SEED` are removed; no parallel dispatch seed vocabulary remains in backend.
2. `GET /api/admin/dispatch_tasks/task_keys` returns defaults derived from `TASK_CONFIG` + state tuples only (seed does not win over config).
3. Admin adhoc dispatch preview uses config-derived metadata, not dispatch seed templates.
4. Adding a new key to `TASK_CONFIG` or relevant state tuples surfaces in admin dispatch forms without editing a separate seed list.
5. Existing saved dispatch rows with valid states continue to display and save; API validation remains authoritative on submit.

## Boundaries

* Does **not** change `StateUiContext.tsx` or frontend manifest fallbacks — sibling child ticket (Katherine).
* Does **not** refactor `config.py` into a package (\[AST-346\]).
* Does **not** change dispatch business rules — only how allowed values and form defaults are **surfaced** in admin.
* Does **not** touch board search UI (Boards iceboxed).

## Notes for planning

* Primary files: `src/data/database.py`, `src/utils/config.py`, `src/ui/api/api_admin.py` (dispatch task endpoints).
* Follow existing pattern: `GET /api/admin/dispatch_tasks/state_options` already reads `JOB_STATES` / `COMPANY_STATES` keys — extend same discipline to task keys and preview.
* Parent inventory row: dispatch seed + task_keys + adhoc preview marked **Fix v1**.
* Secondary domain: admin API only; no React in this ticket.

## Git branch (authoritative)

Per **orientation-astral** Branch law: parent `ftr/ast-484-strengthen-lookup-config-ui`, child `sub/AST-484/AST-549-retire-dispatch-task-seed`. Created at **dispatch-linear**. Engineers cherry-pick to `origin/<ftr-ref>` or `origin/<sub-ref>` — never Linear `gitBranchName` when it disagrees.

### Comments

#### radia — 2026-06-02T22:24:15.545Z
**Review** — `origin/dev...origin/sub/AST-484/AST-549-retire-dispatch-task-seed` @ `5cfe5ed8` (product) + doc @ `1f86aa1e`

Combined plan + Radia review: `docs/features/foundation/ast-549-retire-dispatch-task-seed-drive-admin-lookups-from-config-only.md`

### fix-now

- **`docs/ASTRAL_TEST_BIBLE.md`** — §7.13zq (AST-549) **removed** entire §7.13zn (AST-531/532 per-hop `dispatch_ledger` manifest) that still exists on `origin/dev`. Restore §7.13zn; keep §7.13zq additive.

### discuss

- **`src/utils/config.py` `_dispatch_batch_call_mode_for`** — legacy `_DISPATCH_TASK_SEED` had `validate_title` with `batch_call_mode: 1`; plan step 5 omits it from the mode-1 frozenset, so `dispatch_task_admin_defaults("validate_title")` returns `0`. Confirm intentional before resolve (new inserts/backfill only; existing DB rows unchanged).

### advisory

- Job `sort_by` via `PASSED_SCORE_GATED_STATES` / artifact triggers (not `JOB_STATES.batch_criteria`) — documented plan deviation; OK.
- Tests + bible in diff despite plan “Betty only” note — acceptable for Tests Passed scope.

### sign-off (no action)

- Stages 1–3: seed dicts removed; `dispatch_task_admin_defaults` wired through `database.py` + `api_admin.py`; TASK_CONFIG-first `task_keys` (acceptance #2–4).
- **§1.4/§2.1** config SSOT, **§3.3** layer imports, **§2.4** batch fields derived in config — clean.
- `save_dispatch_task` → `ValueError` for non-schedulable keys; `COMPANY_STATES["NEW"].batch_criteria` supports inflow resolve sort_by.
- Boundary respected: no frontend / AST-550 scope.

#### ada — 2026-06-02T22:14:55.097Z
**test-astral** — manifest pytest green; product fix published.

**Commands (all 19 nodes pass):**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst549DispatchAdminDefaults \
  tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers \
  tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_inflow_discovery_dispatch_admin_defaults \
  tests/component/utils/test_config.py::TestAst506InflowResolveConfig::test_inflow_resolve_website_dispatch_admin_defaults \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast549_task_keys_config_derivation_authoritative \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast485_dispatch_task_keys_roster_seeds_minus_locate_template \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast485_adhoc_entities_select_job_page_fallbacks_to_config_defaults \
  tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_dispatch_task_keys_includes_task_config_registry \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_list_dispatch_tasks_and_keys
```

**Fixes (`88d7985c` → `origin/sub/AST-484/AST-549-retire-dispatch-task-seed` @ `5cfe5ed8`):**
1. `dispatch_task_keys` now merges schedulable keys outside `TASK_CONFIG` (roster trio `find_job_page` / `select_job_page` / `parse_job_list`).
2. `COMPANY_STATES["NEW"]` gets `batch_criteria.sort_by` so `inflow_resolve_website` and `trigger_state_used_by_scored_dispatch_task` no longer raise on company `NEW`.

**Harness tail:** Vitest still reports 2 failures in `test_AdminManageCandidates.test.tsx` (AST-511 middle-name UI — cross-ticket, not AST-549 scope). Pytest portion of the manifest is fully green.

#### betty — 2026-06-02T22:10:02.886Z
**QA manifest** — `origin/sub/AST-484/AST-549-retire-dispatch-task-seed` @ `59768708`

`docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `00b83a65f8a71981bbca798e74f8e5a96eea4285` — see §7.13zq.

1. `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst549DispatchAdminDefaults`
2. `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst471DispatchConfigHelpers`
3. `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst505InflowDiscoveryConfig::test_inflow_discovery_dispatch_admin_defaults`
4. `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst506InflowResolveConfig::test_inflow_resolve_website_dispatch_admin_defaults`
5. `./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast549_task_keys_config_derivation_authoritative`
6. `./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast485_dispatch_task_keys_roster_seeds_minus_locate_template`
7. `./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_ast485_adhoc_entities_select_job_page_fallbacks_to_config_defaults`
8. `./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_dispatch_task_keys_includes_task_config_registry`
9. `./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_list_dispatch_tasks_and_keys`

**Expected product gaps (manifest red until fixed):**
- **`GET /api/admin/dispatch_tasks/task_keys`** omits roster trio **`find_job_page` / `select_job_page` / `parse_job_list`** — schedulable keys not in **`get_task_keys()`** need listing (plan Stage 3 AC / AST-485 regression).
- **`dispatch_task_admin_defaults("inflow_resolve_website")`** and **`trigger_state_used_by_scored_dispatch_task`** raise **`KeyError`** on company **`NEW`** missing **`batch_criteria.sort_by`** — breaks **`list_dtasks`** and scored-trigger scan.

#### ada — 2026-06-02T22:03:40.504Z
Plan doc: [ast-549-retire-dispatch-task-seed-drive-admin-lookups-from-config-only.md](https://github.com/susansomerset/astral/blob/sub/AST-484/AST-549-retire-dispatch-task-seed/docs/features/foundation/ast-549-retire-dispatch-task-seed-drive-admin-lookups-from-config-only.md)

**Self-assessment**
- **Scope:** Single-Component — `config.py`, `database.py`, and `api_admin.py` dispatch admin defaults only; no frontend (AST-550).
- **Conf:** Medium — Explicit derivation table replaces seed, but schedulable-key boundary and scored-trigger parity need Betty’s test pass.
- **Risk:** Medium — Admin create/preview and schema backfill depend on new `dispatch_task_admin_defaults`; saved DB rows unchanged.

Three stages: (1) config helper + remove trigger seed mirror, (2) delete `_DISPATCH_TASK_SEED` and wire database paths, (3) config-authoritative `task_keys` / adhoc preview.

---

# AST-549 — Retire dispatch task seed; drive admin lookups from config only

- **Linear (this ticket):** [AST-549](https://linear.app/astralcareermatch/issue/AST-549/retire-dispatch-task-seed-drive-admin-lookups-from-config-only)
- **Parent:** [AST-484](https://linear.app/astralcareermatch/issue/AST-484/strengthen-the-relationships-between-lookup-lists-in-the-ui-and-live-values-in-config)
- **Publish ref:** `origin/sub/AST-484/AST-549-retire-dispatch-task-seed` (child of AST-484; not Linear `gitBranchName`)

## Summary

Admin dispatch surfaces still read a parallel vocabulary in `database._DISPATCH_TASK_SEED` and `config._DISPATCH_TASK_TRIGGER_SEED`. That duplicate list can override `TASK_CONFIG` in `GET /api/admin/dispatch_tasks/task_keys` and supplies adhoc preview metadata when no sample `dispatch_task` row exists. This ticket removes both seed dicts and replaces them with **config-built defaults** derived from `TASK_CONFIG`, `ROSTER_CONFIG`, `INFLOW_CONFIG`, `GAZER_CONFIG`, and state registries (`JOB_STATES` / `COMPANY_STATES` / `CANDIDATE_STATES`). Missing derivation for a schedulable key is a **hard error** (no silent fallbacks), matching parent epic AST-484.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `dispatch_task_admin_defaults(task_key)` (+ small private helpers); remove `_DISPATCH_TASK_TRIGGER_SEED` and `DISPATCH_TASK_SEED_KEYS`; refactor `trigger_state_used_by_scored_dispatch_task` to use config defaults + `TASK_CONFIG` scored transitions (no seed loop) | utils |
| `src/data/database.py` | Remove `_DISPATCH_TASK_SEED`, `dispatch_task_seed_templates()`; wire `_ensure_dispatch_task_schema` backfill, `_ensure_gaze_board_dispatch_tasks`, `_RETRY_TASK_SEED` inserts, `save_dispatch_task`, `get_dispatch_row_or_seed_preview_meta` to `config.dispatch_task_admin_defaults` | data |
| `src/ui/api/api_admin.py` | `_dispatch_task_key_form_meta` and `dispatch_task_keys`: **TASK_CONFIG-first**; drop seed merge that overrides config; adhoc preview via config defaults only | ui |

**Out of scope (do not touch):** `StateUiContext.tsx`, frontend manifests (AST-550 / Katherine), `config.py` package refactor (AST-346), `tests/**`, `docs/ASTRAL_TEST_BIBLE.md` (Betty after Code Complete).

## Stage 1: Config — `dispatch_task_admin_defaults` and remove trigger seed mirror

**Done when:** `dispatch_task_admin_defaults("qualify_job_listings")` returns the same `entity_type` / `trigger_state` / `sort_by` / `batch_call_mode` shape the old database seed row used; `_DISPATCH_TASK_TRIGGER_SEED` and `DISPATCH_TASK_SEED_KEYS` are deleted; `trigger_state_used_by_scored_dispatch_task` still classifies scored rows correctly without importing seed keys.

1. In `src/utils/config.py`, add a module-level frozenset `DISPATCH_SCHEDULABLE_TASK_KEYS` listing every `task_key` that may appear on a `dispatch_task` row (the former `_DISPATCH_TASK_SEED` key set — copy the key list once, then delete the seed dict in Stage 2). Include dispatch-only aliases: `prefilter`, `find_job_page`, `select_job_page`, `parse_job_list`, `recheck_no_openings`, `gaze`, `gaze_board`, `inflow_discovery`, `inflow_resolve_website`, plus all job-pipeline / consult keys that were in the seed.

2. Add private helper `_dispatch_trigger_state_for_task_key(task_key: str) -> str` with **explicit, ordered** rules (no `or ""` fallbacks):
   - `prefilter` → `ROSTER_CONFIG["prefilter"]["input_state"]` (`WEBSITE_FOUND`)
   - `find_job_page`, `select_job_page`, `parse_job_list` → first entry of `ROSTER_CONFIG["locate_job_page"]["dispatch_input_states"]` (`TO_WATCH`)
   - `recheck_no_openings` → `"NO_OPENINGS"`
   - `gaze` → `"WATCH"`
   - `gaze_board` → `"ACTIVE"`
   - `inflow_discovery` → `INFLOW_CONFIG["discovery"]["dispatch_trigger_state"]`
   - `inflow_resolve_website` → `INFLOW_CONFIG["resolve"]["dispatch_trigger_state"]`
   - `validate_title` → `"NEW"`
   - `qualify_job_listings` → `"VALID_TITLE"`
   - `scrape_jd` → `"PASSED_JOBLIST"`
   - `evaluate_jd` → `"JD_READY"`
   - `consult_do` → `"PASSED_JD"`
   - `consult_get` → `"PASSED_DO"`
   - `consult_like` → `"PASSED_GET"`
   - `analysis_upshot` → `"PASSED_LIKE"`
   - `contemplate_job` → `"BUILD_ARTIFACTS"`
   - `draft_cover_letter` → `"CANDIDATE_REVIEW"`
   - Any other key in `DISPATCH_SCHEDULABLE_TASK_KEYS`: if `TASK_CONFIG[task_key]` has non-null `trigger_state`, use it; else if `TASK_CONFIG[resolve_dispatch_task_config_key(task_key)]` has `not_ready_state`, use that; else **`raise KeyError`** with `task_key` in the message.

3. Add private helper `_dispatch_entity_type_for_task_key(task_key: str) -> str`:
   - `prefilter` → `"company"`
   - `gaze_board` → `"board_search"`
   - `inflow_discovery` → `"candidate"`
   - Else: read `TASK_CONFIG.get(task_key)` or `TASK_CONFIG.get(resolve_dispatch_task_config_key(task_key))`; require non-empty `entity_type` or **`raise KeyError`**.

4. Add private helper `_dispatch_sort_by_for(entity_type: str, trigger_state: str) -> str`:
   - If `entity_type == "job"`: `JOB_STATES[trigger_state]["batch_criteria"]["sort_by"]`
   - If `entity_type == "company"`: `COMPANY_STATES[trigger_state]["batch_criteria"]["sort_by"]`
   - If `entity_type == "board_search"`: `"last_scan_at"` (same as `gaze_board` / WATCH cadence today)
   - If `entity_type == "candidate"`: `"updated_at"` (inflow discovery)
   - Missing `batch_criteria` or `sort_by` → **`raise KeyError`** (crash-worthy; no default string).

5. Add private helper `_dispatch_batch_call_mode_for(task_key: str) -> int`:
   - `1` when `task_key` is one of `qualify_job_listings`, `evaluate_jd`, `consult_do`, `consult_get`, `consult_like`, `gaze_board`
   - `0` otherwise (matches current seed integers).

6. Add public function:

```python
def dispatch_task_admin_defaults(task_key: str) -> Dict[str, Any]:
    """Admin + DB insert defaults for dispatch_task columns. Raises KeyError if task_key is not schedulable."""
```

Return `{"entity_type", "trigger_state", "sort_by", "batch_call_mode"}` built from helpers above. Reject unknown `task_key` not in `DISPATCH_SCHEDULABLE_TASK_KEYS`.

7. Delete `_DISPATCH_TASK_TRIGGER_SEED` and `DISPATCH_TASK_SEED_KEYS` entirely.

8. Refactor `trigger_state_used_by_scored_dispatch_task`:
   - Remove the `for dk, meta in _DISPATCH_TASK_TRIGGER_SEED.items()` loop.
   - Replace with: for each `dk` in `DISPATCH_SCHEDULABLE_TASK_KEYS`, if `dispatch_task_admin_defaults(dk)["trigger_state"] == ts` and `dispatch_task_key_is_scored(dk)`, return `True`.
   - Keep existing `_TRANSITION_STATES_USED_BY_SCORED_TASKS` branch unchanged.

⚠️ **Decision:** Schedulable keys remain an explicit frozenset (not “every TASK_CONFIG key”) so artifact-only keys like `anticipate_scan` stay out of dispatch admin unless Susan later adds them to `DISPATCH_SCHEDULABLE_TASK_KEYS`. `GET /api/admin/dispatch_tasks/task_keys` still lists **all** `get_task_keys()` per AST-516; only schedulable keys get full four-field defaults.

## Stage 2: Database — remove `_DISPATCH_TASK_SEED` and wire defaults

**Done when:** `grep _DISPATCH_TASK_SEED src` returns no matches; `dispatch_task_seed_templates()` is gone; schema ensure / insert / preview paths call `config.dispatch_task_admin_defaults`.

1. Delete `_DISPATCH_TASK_SEED` dict and `dispatch_task_seed_templates()` from `src/data/database.py`.

2. At top of `database.py` dispatch section, add import: `from src.utils.config import dispatch_task_admin_defaults` (data may import utils per layer rules).

3. `_ensure_gaze_board_dispatch_tasks`: replace `_DISPATCH_TASK_SEED.get("gaze_board")` with `dispatch_task_admin_defaults("gaze_board")`.

4. `_ensure_dispatch_task_schema` — NULL-column backfill loop (~lines 4536–4549): replace `_DISPATCH_TASK_SEED.get(row[1], {})` with `try: defaults = dispatch_task_admin_defaults(row[1])` except `KeyError: continue` (only backfill rows whose `task_key` is schedulable).

5. `_RETRY_TASK_SEED` insert block (~4565–4583): replace `base_seed = _DISPATCH_TASK_SEED.get(base_key, {})` with `dispatch_task_admin_defaults(base_key)`; if `KeyError`, `continue`.

6. `save_dispatch_task`: when `entity_type` or `trigger_state` omitted/blank, call `defaults = dispatch_task_admin_defaults(task_key)` and fill `entity_type`, `trigger_state`, `sort_by`, `batch_call_mode` from defaults. If `task_key` not schedulable, **`raise ValueError`** with clear message (do not insert partial row).

7. `get_dispatch_row_or_seed_preview_meta`: after `get_dispatch_task_by_key` returns `None`, call `dispatch_task_admin_defaults(task_key)` and return that dict. Remove `TASK_CONFIG`-only partial fallback branch (lines 4752–4755). If `KeyError`, return `None` (admin 404 unchanged).

8. Leave idempotent SQL migrations (`locate_job_page` rename, `recheck_no_openings`, triple-unique rebuild) **unchanged**.

## Stage 3: Admin API — config-authoritative `task_keys`

**Done when:** `GET /api/admin/dispatch_tasks/task_keys` never calls `dispatch_task_seed_templates()`; seed cannot override `TASK_CONFIG` defaults; roster trio still returns `company` / `TO_WATCH` from config derivation.

1. Rewrite `_dispatch_task_key_form_meta(task_key: str) -> dict` in `src/ui/api/api_admin.py`:
   - Start from `cfg = TASK_CONFIG.get(task_key) or {}`.
   - Set `entity_type` from `cfg.get("entity_type") or ""`.
   - Set `trigger_state` from `cfg.get("trigger_state")` when not `None`, else `""`.
   - Set `is_scored` from `dispatch_task_key_is_scored(task_key)`.
   - If `task_key in DISPATCH_SCHEDULABLE_TASK_KEYS` (import from config), **merge** `dispatch_task_admin_defaults(task_key)` so schedulable keys get authoritative `entity_type` / `trigger_state` (config derivation wins over bare `TASK_CONFIG` where `trigger_state` was `None` on roster AI keys).

2. Rewrite `dispatch_task_keys()`:
   - Build `seen` from `get_task_keys()` → `_dispatch_task_key_form_meta` (unchanged AST-516 “every TASK_CONFIG key” behavior).
   - **Delete** the loop `for tk, meta in database.dispatch_task_seed_templates().items()` that overwrote config.
   - Keep the `list_dispatch_tasks()` loop for keys that exist only in DB.

3. Update docstring on `_dispatch_preview_meta_for_task_key` wrapper (~line 60): remove “seed defaults (AST-485)” wording; say “config-built defaults via `get_dispatch_row_or_seed_preview_meta`”.

4. Grep `api_admin.py` for `dispatch_task_seed_templates` and `seed` in dispatch context — zero remaining references.

## Self-Assessment

**Scope:** `Single-Component` — Touches three backend modules (`config`, `data`, `ui/api`) but only the dispatch admin defaults path; no frontend, no dispatcher runtime routing.

**Conf:** `Medium` — Derivation rules are explicit and mapped from existing seed behavior, but scored-trigger detection and schedulable-key boundaries need careful parity with today’s `_DISPATCH_TASK_TRIGGER_SEED` tests Betty will update.

**Risk:** `Medium` — Wrong trigger default breaks Scheduled Actions create forms and schema backfill; runtime dispatch still reads DB rows, so saved rows are safe, but new inserts and admin previews regress if derivation drifts.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| **§1.4 / §2.1 config SSOT** | Removes parallel seed vocabulary; allowed values come from config blocks and state registries. |
| **§1.3 DRY** | Single `dispatch_task_admin_defaults` replaces database + config duplicate dicts. |
| **§2.4 batch** | `sort_by` / `batch_call_mode` still sourced from config+state criteria, not invented in API. |
| **§3.3 imports** | `database → utils` and `ui → utils` are allowed; no new `utils → data` import. |

No conflicts requiring `conf-!!-NONE`.

## Betty / test note (not in build commits)

After Code Complete, Betty should update `tests/component/utils/test_config.py` (`TestAst471DispatchConfigHelpers`, seed parity tests) and `tests/component/ui/api/test_api_admin.py` (`test_ast485_dispatch_task_keys_roster_seeds_minus_locate_template`, `test_dispatch_task_keys_includes_task_config_registry`, monkeypatches of `dispatch_task_seed_templates`) to assert `dispatch_task_admin_defaults` instead of removed symbols.

## Radia review

| Field | Value |
|-------|-------|
| Branch | `origin/sub/AST-484/AST-549-retire-dispatch-task-seed` |
| Tip | `5cfe5ed8` |
| Baseline | `origin/dev...origin/sub/AST-484/AST-549-retire-dispatch-task-seed` |

### What's solid

- Plan stages 1–3 delivered: `_DISPATCH_TASK_SEED`, `dispatch_task_seed_templates()`, `_DISPATCH_TASK_TRIGGER_SEED`, and `DISPATCH_TASK_SEED_KEYS` removed; `dispatch_task_admin_defaults` is the single derivation path for database backfill, inserts, adhoc preview, and admin `task_keys`.
- **§1.4 / §2.1 (config SSOT):** Schedulable defaults come from `TASK_CONFIG`, roster/inflow/board config blocks, and state registries — no parallel seed vocabulary.
- **§3.3 (layers):** `database → utils` and `ui/api → utils` only; no new forbidden imports.
- **§2.4 (batch):** `sort_by` / `batch_call_mode` derived in config helpers, not invented in the API layer.
- `save_dispatch_task` raises `ValueError` for non-schedulable `task_key`; schema backfill skips unknown keys via `KeyError` continue (bounded — not request-path swallowing).
- `GET /api/admin/dispatch_tasks/task_keys` is TASK_CONFIG-first; schedulable keys merge config derivation — seed cannot override config (acceptance #2).
- `COMPANY_STATES["NEW"].batch_criteria.sort_by` addition supports `inflow_resolve_website` without silent empty fallback.
- Betty/test-astral manifest updates align with removed symbols; `TestAst549DispatchAdminDefaults` covers core derivation.

### Issues

| Sev | Location | Finding |
|-----|----------|---------|
| **fix-now** | `docs/ASTRAL_TEST_BIBLE.md` | Adding §7.13zq **deleted** entire §7.13zn (AST-531/532 per-hop `dispatch_ledger` manifest) still present on `origin/dev`. Unrelated sibling scope — restore §7.13zn when editing the bible. |
| **discuss** | `src/utils/config.py` `_dispatch_batch_call_mode_for` | Old `_DISPATCH_TASK_SEED` had `validate_title` with `batch_call_mode: 1`; plan step 5 omits it from the mode-1 frozenset, so new defaults return `0`. Confirm intentional before resolve — affects new inserts/backfill only (existing DB rows unchanged). |
| **advisory** | `src/utils/config.py` `_dispatch_sort_by_for` (job) | Job `sort_by` uses `PASSED_SCORE_GATED_STATES` + artifact trigger conventions because `JOB_STATES` lacks `batch_criteria` — documented plan deviation; acceptable. |
| **advisory** | Self-Assessment scope | Diff includes `tests/**` and bible edits despite plan “Betty only” note — fine for Tests Passed; no product scope creep beyond ticket. |

### Recommended actions

| Item | Owner | Action |
|------|-------|--------|
| Bible §7.13zn | Ada (resolve-astral) | Restore AST-531/532 manifest block removed in the AST-549 bible edit; keep §7.13zq additive. |
| `validate_title` batch_call_mode | Ada + Susan if needed | Confirm `0` vs legacy seed `1`; add to `_DISPATCH_BATCH_CALL_MODE_ONE` if parity required. |
| All other findings | — | Sign-off; proceed to resolve-astral after fix-now + discuss cleared. |

## Resolution

| Field | Value |
|-------|-------|
| Date | 2026-06-02 |
| Publish ref | `origin/sub/AST-484/AST-549-retire-dispatch-task-seed` |
| Review baseline | Radia @ `5cfe5ed8`; doc @ `1f86aa1e` |

### fix-now — bible §7.13zn

**`docs/ASTRAL_TEST_BIBLE.md`:** §7.13zn (AST-531/532 per-hop `dispatch_ledger` manifest) restored on publish ref @ `1f86aa1e` (`docs(AST-549): Radia review — … restore bible §7.13zn`). §7.13zq (AST-549 config-authoritative dispatch admin defaults) remains additive after §7.13zp. No further bible edits required for resolve.

### discuss — `validate_title` `batch_call_mode`

**Intentional `0` per plan Stage 1 step 5:** `_DISPATCH_BATCH_CALL_MODE_ONE` lists only `qualify_job_listings`, `evaluate_jd`, `consult_do`, `consult_get`, `consult_like`, `gaze_board`. Legacy seed had `validate_title: 1`; plan explicitly omits it from the mode-1 frozenset. `dispatch_task_admin_defaults("validate_title")["batch_call_mode"]` is **`0`** — affects new inserts and schema backfill only; existing saved `dispatch_task` rows unchanged.

### advisory — signed off

- Job `sort_by` via `PASSED_SCORE_GATED_STATES` / artifact triggers — documented plan deviation; no change.
- Tests + bible in diff — Betty/test-astral scope for Tests Passed; accepted.

### Outcome

All **fix-now** and **discuss** items closed. Ready for **User Testing**.
