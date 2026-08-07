# Admin catalog/API hardcode audit + alphabetical task_key lists

**Linear:** [AST-1214](https://linear.app/astralcareermatch/issue/AST-1214/admin-catalogapi-hardcode-audit-alphabetical-task-key-lists-ui)  
**Parent:** [AST-1185](https://linear.app/astralcareermatch/issue/AST-1185/ui-groupingssequences-alphabetical-task-keyalias-dropdowns-data-driven)  
**Publish ref:** `sub/AST-1185/AST-1214-admin-catalog-api-hardcode-audit-alphabetical-task-key-lists`

Admin operators need Scheduled Actions (and peer Admin surfaces that consume the same catalog) to offer a **live** task-key picker that includes every current `agent_task` identity — including `fetch_*` and other agent_task-only peers, plus alias keys such as `meteorite_grade_do` / `meteorite_grade_get` — sorted **alphabetically by `task_key` string**, with grouping metadata still read from `agent_task` (not parallel phase/seq inventories). Today `GET /api/admin/dispatch_tasks/task_keys` is built from `get_task_keys()` (`TASK_CONFIG` insertion order) plus orphan `dispatch_task` rows, which intentionally omits agent_task-only keys (AST-960). Flask’s `jsonify` already emits sorted object keys by default; this ticket still builds membership with `sorted()` so alphabetical order is an explicit contract, not only a provider default. Catalog keys must be **writable** as first-class options (POST/PUT must not 400 after the form meta fills). This ticket owns that Admin API / config-defaults contract only; React section rendering and dropdown polish stay on AST-1215.

### Product call — scheduling gazer / roster / inflow runtime hops

**Call (this ticket):** Operators **may** create and update Scheduled Actions `dispatch_task` rows for the seven agent_task-only keys that resolve via `_dispatch_*` helpers: `fetch_culture_pages`, `fetch_jd`, `fetch_job_pages`, `fetch_website`, `gaze`, `inflow_discovery`, `recheck_no_openings`.

**Why:** Parent AST-1185 AC requires those identities as first-class catalog options. AST-960’s companion gates (picker omit + `dispatch_task_admin_defaults` `KeyError` + Admin `Unknown task_key`) are reversed for helper-resolvable hops so the form is not a dead end.

**Rejected alternative:** picker-yes / writer-no.

### Product call — `parse_meteorite_email` (Archie / Chuckles [check-linear] 2026-08-07)

**Call:** **No hiding.** Do **not** add `parse_meteorite_email` (or any meteorite mailbox identity) to `ADMIN_CONFIG` hidden dispatch keys. Do **not** filter it out of the picker. It is **not** an eighth gazer/inflow “gap key” to treat like `fetch_*`.

**What it is:** Misnamed live `agent_task` row for the meteorite mailbox / Ruth parse identity. Config already names the TASK_CONFIG key `meteorite_email` (`METEORITE_EMAIL_PARSE_CONFIG["task_key"]`, AST-1212). Archie: fold into `meteorite_email` / rename toward `catch_meteorite_email` — **candidate** entity; **Avail = Gmail inbox ping**; FOR-candidate messages → Ruth. Full seed rename may be absorbed by **AST-1182**; this ticket must not leave a Save dead-end on the live `parse_meteorite_email` row while that rename is pending.

**This ticket’s disposition:** Keep it in the live catalog (eighth agent_task-only key on this tip). Fold Admin defaults / write acceptance onto the meteorite mailbox contract via `METEORITE_EMAIL_PARSE_CONFIG` (canonical `task_key` + `legacy_agent_task_key`), with `admin_entity_type: "candidate"` and mailbox null claim fields parallel to `gaze_email`, plus Avail stamping via the same inbox bind counts as `gaze_email`. Do **not** invent a parallel hard-coded membership set in `api_admin.py`.

**Rejected (Joan escalate options 1 and 3):** Hide via `ADMIN_CONFIG`; ship picker-only 400.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_admin.py` | Expand `dispatch_task_keys` membership to live `agent_task` ∪ `TASK_CONFIG` ∪ dispatch orphans; `sorted(membership)`; form-meta fallback via `_dispatch_*`; align `_dispatch_task_key_trigger_error` for helper-resolvable gap keys + meteorite mailbox fold; preserve `unsupported entity_type` for other in-`TASK_CONFIG` unschedulable keys; Avail for meteorite mailbox keys uses gaze_email inbox bind counts | ui |
| `src/utils/config.py` | Extend `dispatch_task_admin_defaults` for helper-resolvable non-`TASK_CONFIG` keys; extend `METEORITE_EMAIL_PARSE_CONFIG` with legacy agent_task key + admin mailbox fields; mailbox carve-out for canonical + legacy keys (`entity_type=candidate`, null trigger/sort); small `is_meteorite_email_mailbox_task_key` helper | utils |

**Side effects of the `dispatch_task_admin_defaults` change (same function — not new Files Changed rows):**

- `_ensure_dispatch_task_schema` — backfills entity/trigger/sort/batch_call_mode for newly resolvable keys (including folded meteorite mailbox). Expected.
- `get_dispatch_row_or_seed_preview_meta` → `/adhoc/entities` — 404→200 for keys that gain defaults. Betty note.

**Out of scope:**

| Owner | What |
|-------|------|
| AST-1215 (Katherine) | React section headers / dropdown UX |
| AST-1182 | Seed rename `parse_meteorite_email` → `meteorite_email` / `catch_meteorite_email`; AI payload work — may absorb rename; this ticket only folds Admin contract onto live key |
| AST-1183 / AST-1184 | Gaze/Meteorite seed groups; `master_task_key` resolve |
| Betty | Stage 3 contract; engineer does **not** edit `tests/` |

**Audit findings (do not re-litigate):**

- `GET /api/admin/tasks` already `ORDER BY task_key` + DB grouping — leave list order as-is.
- Vector-feedback task_keys = rubric owners only — do not expand.
- Retired / admin-hidden remain config-backed filters — **do not** put `parse_meteorite_email` in hidden.
- Jobs UI sections — out of epic Admin default scope.
- On current tip, **eight** agent_task-only keys (absent from `TASK_CONFIG`): `fetch_culture_pages`, `fetch_jd`, `fetch_job_pages`, `fetch_website`, `gaze`, `inflow_discovery`, `parse_meteorite_email`, `recheck_no_openings`. Of these, seven are helper-resolvable gazer/roster/inflow hops; `parse_meteorite_email` is the meteorite mailbox fold identity (product call above). `prefilter` / `inflow_resolve_website` are not agent_task keys — stay out of picker Done-when; writer may still accept them if POSTed (intentional).

## Execution contract

The plan is binding. Execute stages in order. Do not edit React, seed JSON rename (AST-1182), or `tests/`. Do **not** add `parse_meteorite_email` to `ADMIN_CONFIG` hidden lists. When blocked — comment on **AST-1185** with Stage N template.

---

## Stage 1: Live alphabetical Admin task-key catalog

**Done when:** `GET /api/admin/dispatch_tasks/task_keys` returns the sorted union of `get_task_keys()` ∪ `list_candidate_tasks()` keys ∪ non-retired `list_dispatch_tasks()` keys, minus hidden/retired; built with `sorted(membership)`; on this tip all **eight** agent_task-only keys above are present without a pre-existing `dispatch_task` row; aliases `meteorite_grade_do` / `meteorite_grade_get` present; each value carries form-meta fields.

1. Import `_dispatch_trigger_state_for_task_key` alongside `_dispatch_entity_type_for_task_key` in `api_admin.py`.

2. Add `_admin_dispatch_task_key_catalog()` as previously specified (union + `sorted(membership)` + `_dispatch_task_key_form_meta`).

3. Replace `dispatch_task_keys()` body to `return jsonify(_admin_dispatch_task_key_catalog())` with docstring matching this contract.

4. No frozenset of gap keys for membership. No change to `get_task_keys()`. **No** `ADMIN_CONFIG` hide of `parse_meteorite_email`.

⚠️ **Decision:** Reverse AST-960 picker omit for all current `agent_task` keys (including `parse_meteorite_email`). Keep `sorted(membership)`.

---

## Stage 2: Form-meta + first-class write path (helper-resolvable hops + meteorite mailbox fold)

**Done when:**

- Each of the **seven** helper-resolvable keys: form meta filled; `_dispatch_task_key_trigger_error` returns `None` for a valid trigger (e.g. `fetch_jd`/`PASSED_JOBLIST`, `inflow_discovery`/`ACTIVE_SEARCH`); `dispatch_task_admin_defaults` returns a dict; POST create succeeds for `fetch_jd`.
- `parse_meteorite_email` and `meteorite_email`: `dispatch_task_admin_defaults` returns mailbox defaults with `entity_type == "candidate"` and null `trigger_state` / `sort_by` / `batch_call_mode == 0`; `_dispatch_task_key_trigger_error` does **not** return `Unknown task_key` for either; POST create for `parse_meteorite_email` with a valid candidate succeeds (201); form meta shows `entity_type: "candidate"`.
- Registered-but-unschedulable other `TASK_CONFIG` keys (e.g. craft_*) still get `unsupported entity_type` wording, not `Unknown task_key`.
- `list_dtasks` Avail for a `parse_meteorite_email` / `meteorite_email` row uses the same inbox bind-count path as `gaze_email` (Gmail ping).

1. Form-meta `_dispatch_*` fallback for empty entity/trigger (unchanged from revision 2).

2. `_dispatch_task_key_trigger_error` — after retired check:

   ```python
   # Mailbox identities (gaze_email + meteorite fold) — accept before Unknown.
   if tk == GAZE_EMAIL_CONFIG["task_key"] or is_meteorite_email_mailbox_task_key(tk):
       ts = (trigger_state or "").strip()
       # Mailbox rows use null trigger_state (same as gaze_email seed); empty is OK.
       if ts:
           # If operator supplies a trigger, validate against candidate registry for meteorite
           # mailbox, or existing gaze_email rules if any; otherwise return a clear error.
           ...
       return None

   try:
       et = _dispatch_entity_type_for_task_key(tk)
   except KeyError:
       if tk in TASK_CONFIG:
           return f"task_key {tk!r} has unsupported entity_type"
       return f"Unknown task_key: {tk!r}"
   # … existing trigger required + registry / hop validation …
   ```

   Import `GAZE_EMAIL_CONFIG`, `is_meteorite_email_mailbox_task_key` from config. Concrete empty-vs-supplied trigger validation: empty → accept (mailbox); non-empty → must be in `CANDIDATE_STATES` when `is_meteorite_email_mailbox_task_key(tk)`.

3. In `METEORITE_EMAIL_PARSE_CONFIG` (`config.py`), add config-backed fold fields (no api_admin frozenset):

   ```python
   METEORITE_EMAIL_PARSE_CONFIG = {
       "task_key": "meteorite_email",
       "legacy_agent_task_key": "parse_meteorite_email",  # live seed name until AST-1182 rename
       "admin_entity_type": "candidate",  # Archie: candidate-bound; Avail = Gmail ping
       "parse_modes": ("html_links", "subject_body"),
   }
   ```

   Add:

   ```python
   def is_meteorite_email_mailbox_task_key(task_key: str) -> bool:
       tk = (task_key or "").strip()
       cfg = METEORITE_EMAIL_PARSE_CONFIG
       return tk == cfg["task_key"] or tk == cfg["legacy_agent_task_key"]
   ```

4. In `dispatch_task_admin_defaults`, after retired check:

   - If `is_meteorite_email_mailbox_task_key(tk)`: return  
     `{"entity_type": METEORITE_EMAIL_PARSE_CONFIG["admin_entity_type"], "trigger_state": None, "sort_by": None, "batch_call_mode": 0}`  
     (do this **before** the bare `tk not in TASK_CONFIG` raise, so legacy `parse_meteorite_email` works).
   - Keep existing `gaze_email` carve-out.
   - Then: if `tk not in TASK_CONFIG`, helper-resolvable path (revision 2 snippet) for the seven gazer/inflow hops.
   - Else existing TASK_CONFIG body.

5. In `list_dtasks`, extend the gaze_email Avail branch so `is_meteorite_email_mailbox_task_key(row["task_key"])` also stamps `available_count` from `count_inbox_bound_by_candidate()` (same snapshot). Config-driven key match — do not hardcode `parse_meteorite_email` string in the branch condition.

6. No alias→master map for AST-1184 aliases. No seed rename of `parse_meteorite_email` in this ticket.

⚠️ **Decision:** Helper-resolvable hops = first-class writable. `parse_meteorite_email` = meteorite mailbox fold (config), not hidden, not a gazer gap key. AST-1182 may rename seed to `catch_meteorite_email` / fold fully into `meteorite_email`.

---

## Stage 3: Hardcode audit close-out + Betty contract

**Done when:** No new hard-coded membership/section inventories; no `ADMIN_CONFIG` hide of `parse_meteorite_email`; Stage 3 Linear comment includes Betty set below.

1–3. Diff audit as before (`api_admin.py` + `config.py`).

4. **Betty contract:**

   **A. Picker presence (`test_api_admin.py`):**  
   Flip `test_dispatch_task_keys_omits_fetch_jd_gap_excludes_retired` and `test_gap_key_absent_without_db_row`. Expect the **eight** agent_task-only keys present (seven helper-resolvable + `parse_meteorite_email`). Stay absent from picker: `prefilter`, `inflow_resolve_website`.

   **B. Admin validator:**  
   Flip `test_dispatch_task_key_trigger_error_candidate_paths` for `inflow_discovery` → accept. Add/adjust coverage: `_dispatch_task_key_trigger_error("parse_meteorite_email", None|"" )` does not contain `Unknown task_key`.

   **C. Config defaults (`test_config.py`):**  
   Flip KeyError expectations for helper-resolvable keys (`fetch_jd`, `fetch_job_pages`, `fetch_website`, `fetch_culture_pages`, `inflow_discovery`); `prefilter` / `inflow_resolve_website` → expect defaults dicts. Add: `dispatch_task_admin_defaults("parse_meteorite_email")` and `("meteorite_email")` return candidate mailbox defaults (not KeyError / not unsupported).

   **D. Keepers:** `unsupported entity_type` for craft_* etc.; other `task_keys` endpoint tests.

   **E. Harness:** patch `list_candidate_tasks`; raw-body alphabetical keys; POST `fetch_jd` + POST `parse_meteorite_email`; optional `/adhoc/entities` 200; Avail > 0 path for meteorite mailbox when inbox binds exist (or unit-level stamp assertion).

---

## Self-Assessment

**Scope:** `Single-Component` — Admin catalog + write/defaults in `api_admin.py` / `config.py`; meteorite mailbox fold via `METEORITE_EMAIL_PARSE_CONFIG`; no React; no seed rename (AST-1182).

**Conf:** `high` — Archie/Chuckles product call settles Joan escalate (no hide; fold mailbox identity); eight-key membership measured on tip; helpers already proven for the seven.

**Risk:** `Medium` — schedules gazer/inflow hops + meteorite mailbox under live `parse_meteorite_email` name until AST-1182 rename; Betty breadth spans Admin + config; Avail shares gaze_email inbox counts.

## CODE_RULES check

- §1.4 / no-hardcoded-sets — membership from live catalogs; mailbox fold keys in `METEORITE_EMAIL_PARSE_CONFIG`; **no** ADMIN_CONFIG hide list for parse.
- §2.1 / config-source-of-truth — defaults + mailbox contract in config.
- §2.9 / require-auth — `@require_admin` retained.
- §3.2 / ui-config-driven — membership, alpha, write, Avail resolved in API/config.
- in-scope-only — no React; no AST-1182 seed rename; Ad-hoc 404→200 noted as side effect.
- plan-is-bible — eighth key + no-hide + fold disposition explicit.

## Revisions

Revision 1 — 2026-08-07  
Driven by: Joan `[plan-discuss] round=1 concern`.  
Changes: First-class writable gap keys; seven-key Done-when; alpha premise; Betty pair + patch.

Revision 2 — 2026-08-07  
Driven by: Joan `[plan-discuss] round=2 concern`.  
Changes: Named scheduling product call; Betty breadth (test_config + Admin Unknown); wording keep; side effects; writer>picker note.

Revision 3 — 2026-08-07  
Driven by: Joan `[plan-discuss] escalate` (eighth key `parse_meteorite_email` Save dead-end) + Chuckles `[check-linear]` Archie product call (**no hiding**; misnamed — fold into `meteorite_email` / `catch_meteorite_email`; candidate; Avail=Gmail ping; AST-1182 may absorb rename).  
Changes: Membership corrected to **eight** agent_task-only keys; rejected ADMIN_CONFIG hide and picker-only 400; Stage 2 adds meteorite mailbox fold via `METEORITE_EMAIL_PARSE_CONFIG` (`legacy_agent_task_key`, `admin_entity_type=candidate`) + validator/defaults/Avail; Betty A–E updated for `parse_meteorite_email` / `meteorite_email`; seed rename left to AST-1182.
