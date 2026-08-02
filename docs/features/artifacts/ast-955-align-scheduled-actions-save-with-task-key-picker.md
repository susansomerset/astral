<!-- linear-archive: AST-955 archived 2026-08-02 -->

## Linear archive (AST-955)

**Archived:** 2026-08-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-955/align-scheduled-actions-save-with-task-key-picker-check-cover-letter  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-856 — check_cover_letter not recognized as a valid task_key  
**Blocked by / blocks / related:** parent: AST-856

### Description

## What this implements

Admin create/update on Scheduled Actions accepts every registered task key the picker already offers (except explicitly retired keys). Fixes Susan's `check_cover_letter` 400; leaves run-time validation as the place misconfigured trigger/entity pairings fail. Does not own Manage Tasks, chain choreography, or dispatcher claim changes.

## Acceptance criteria

1. Susan can create a Scheduled Action dispatch row with `task_key=check_cover_letter` for candidate `somerset` without HTTP 400 — the error from the original brief no longer occurs.
2. Any other registered task key visible in the picker can be saved the same way (no *Unknown or non-schedulable task_key* for registered task keys).
3. Saving `check_job_resume` and `finalize_job_resume` continues to work unchanged.
4. A deliberately misconfigured row (wrong trigger state for the chosen task_key) is rejected or fails at **run** time, not at Save time — observable on first Run, not blocked at Save for merely being outside a separate schedulable allowlist.
5. Automated coverage asserts admin create acceptance for `check_cover_letter` and at least one regression case for an already-schedulable key.

## Boundaries

* Does not change Manage Tasks Run Next authoring.
* Does not remove the task registry or change prompt / run-next content.
* Does not add pipeline step lists or chain choreography.
* May still block explicitly retired dispatch keys.
* Does not change dispatcher claim logic or Execution History beyond honoring saved rows.

## Notes for planning

* Align Save acceptance with the same registered task catalog the Scheduled Actions picker already uses (Code Rules §2.1 — single source of truth). Drop the separate save-time "schedulable" allowlist gate that rejected `check_cover_letter`.
* Form defaults may still derive from the task registry / existing agent-task rows.

## Git branch (authoritative)

Per **orientation** § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at **dispatch-parent**. Publish to `origin/<sub-ref>` only — never Linear `gitBranchName` when it disagrees.

### Comments

#### chuckles — 2026-07-22T23:57:10.773Z
[merge-child] blocked: missing plan(AST-955): on origin/sub/AST-856/AST-955-align-scheduled-actions-save-with-task-key-picker

@Ada Lovelace — plan landed as `docs(AST-955): plan — …`; validate-sub-log requires `plan(AST-955):`. Add a `plan(AST-955):` commit on the publish ref (empty commit OK if plan doc already present) and push. Stay User Testing.

— Chuckles

#### radia — 2026-07-22T23:55:22.452Z
**Radia review — clean**

Diff: `origin/dev...origin/sub/AST-856/AST-955-align-scheduled-actions-save-with-task-key-picker` @ `2646527`

**Plan fidelity:** Stages 1–3 match. Save membership is registered `TASK_CONFIG` (not `DISPATCH_SCHEDULABLE_TASK_KEYS`); optional `trigger_state` flows through defaults on insert/update; schedulable frozenset left for bootstrap / form enrichment; dispatcher claim untouched.

**Rules:** §1.3 / §2.1 — one Save catalog shared with picker source. §3.3 — utils import only for this change. §2.4 / §2.6 / §5f / §5g N/A.

**fix-now / discuss:** none.

Review doc: https://github.com/susansomerset/astral/blob/264652777ea95a11e66e16d00afb0cef287b4640/docs/features/artifacts/ast-955-align-scheduled-actions-save-with-task-key-picker.md

#### betty — 2026-07-22T23:51:05.244Z
1. `./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst955RegisteredKeyDispatchAdminDefaults \
  tests/component/utils/test_config.py::TestAst549DispatchAdminDefaults::test_unknown_task_key_raises \
  tests/component/ui/api/test_api_admin.py::TestAst955AlignScheduledActionsSave \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_create_dispatch_task_paths \
  tests/component/data/database/test_dispatch_tasks.py::TestAst955SaveDispatchTaskRegisteredKeys \
  -q`

2. **Broken / obsolete revised this pass:**
   - `TestAst549DispatchAdminDefaults::test_unknown_task_key_raises` — `anticipate_scan` is registered (hop-derived `BUILD_ARTIFACTS`); now asserts junk key + `unknown task_key`.
   - `TestDispatchTasks::test_create_dispatch_task_paths` — fake `custom`/`WATCH` 400 before save; uses `grade_do`/`PASSED_JD`.

3. **Coverage:** `check_cover_letter` + `CANDIDATE_REVIEW` create 201; `check_job_resume` regression; unknown wording (`Unknown task_key`, not non-schedulable); DB insert + rejected wording; config defaults with optional trigger.

**Publish:** `origin/sub/AST-856/AST-955-align-scheduled-actions-save-with-task-key-picker` @ `5f87d19` (`merge-tests(AST-955): origin/tests a4b8fbb`)

**Bible shasum (publish tip):**
- `docs/test-bible/ui/api/api_admin.md` `eafb1d5799becdbfb3fa48830b9f8916cfcc0804`
- `docs/test-bible/utils/config.md` `0f1253696e20dadbabc0f1a1b1c13e629026dd6e`
- `docs/test-bible/data/database/dispatch_tasks.md` `0337a6e35ab994d442182050bbc5682291947440`

— Betty

#### ada — 2026-07-22T23:42:51.585Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-856/AST-955-align-scheduled-actions-save-with-task-key-picker/docs/features/artifacts/ast-955-align-scheduled-actions-save-with-task-key-picker.md

**Scope:** Single-Component — utils `dispatch_task_admin_defaults` + `save_dispatch_task` + admin `_dispatch_task_key_trigger_error` so Save accepts the same registered `TASK_CONFIG` catalog the picker already lists; retired keys still blocked; no dispatcher/frontend changes.

**Conf:** high — verified `check_cover_letter` is in `TASK_CONFIG` / picker but outside `DISPATCH_SCHEDULABLE_TASK_KEYS`; Save maps that KeyError to the exact 400 Susan hit.

**Risk:** Medium — admin create/update path; existing schedulable keys keep current derivation when no trigger override is needed; bad `sort_by`/`entity_type` only risk for newly accepted registered keys if override is wrong.

---

# AST-955 — Align Scheduled Actions Save with task_key picker (check_cover_letter not recognized as a valid task_key)

- **Linear:** [AST-955](https://linear.app/astralcareermatch/issue/AST-955/align-scheduled-actions-save-with-task-key-picker-check-cover-letter)
- **Parent:** [AST-856](https://linear.app/astralcareermatch/issue/AST-856/check-cover-letter-not-recognized-as-a-valid-task-key)
- **Publish ref:** `origin/sub/AST-856/AST-955-align-scheduled-actions-save-with-task-key-picker`

Susan’s Scheduled Actions picker lists every registered `TASK_CONFIG` key (minus retired/hidden), but Save rejects keys outside `DISPATCH_SCHEDULABLE_TASK_KEYS` via `dispatch_task_admin_defaults` → `_dispatch_task_key_trigger_error` (`Unknown or non-schedulable task_key: 'check_cover_letter'`). This plan makes create/update accept the same registered catalog the picker already uses, while still blocking retired keys and leaving dispatcher claim logic alone.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `dispatch_task_admin_defaults` to registered `TASK_CONFIG` keys (optional `trigger_state`); drop schedulable-only gate in `_dispatch_trigger_state_for_task_key` fallthrough | utils |
| `src/data/database.py` | `save_dispatch_task` passes request `trigger_state` into defaults; clarify KeyError → ValueError wording | data |
| `src/ui/api/api_admin.py` | `_dispatch_task_key_trigger_error` accepts any non-retired `TASK_CONFIG` key; `update_dtask` passes effective trigger into defaults | ui |

**Out of scope (do not touch):** Manage Tasks / `run_next`, `DISPATCH_SCHEDULABLE_TASK_KEYS` membership set contents (keep for bootstrap / form enrichment), dispatcher claim paths, frontend picker (`GET …/task_keys` already correct), `tests/` / bible (Betty owns AC5 coverage).

## Root cause (verified on this branch)

1. `GET /api/admin/dispatch_tasks/task_keys` builds the picker from `get_task_keys()` / `TASK_CONFIG` (`dispatch_task_keys` in `api_admin.py`).
2. `POST`/`PUT` Save calls `_dispatch_task_key_trigger_error`, which calls `dispatch_task_admin_defaults(tk)` and maps `KeyError` → `Unknown or non-schedulable task_key`.
3. `dispatch_task_admin_defaults` raises when `tk not in DISPATCH_SCHEDULABLE_TASK_KEYS`.
4. `check_cover_letter` is in `TASK_CONFIG` and `JOB_ARTIFACT_ENTRY_TASK_KEYS`, but **not** in `_RESUME_ARTIFACT_HOP_TASK_KEYS` / `DISPATCH_SCHEDULABLE_TASK_KEYS` (unlike `check_job_resume` / `finalize_job_resume`).
5. Even if the API helper were bypassed, `save_dispatch_task` also calls `dispatch_task_admin_defaults` and would raise `ValueError: … not schedulable`.

## Stage 1: Config — registered-key admin defaults

**Done when:** `dispatch_task_admin_defaults("check_cover_letter", trigger_state="CANDIDATE_REVIEW")` returns `entity_type="job"`, that `trigger_state`, a non-empty `sort_by`, and `batch_call_mode` (0). `dispatch_task_admin_defaults("grade_do")` (no override) is unchanged vs today. `dispatch_task_admin_defaults("consult_do")` still raises via retired messaging. Calling `dispatch_task_admin_defaults("check_cover_letter")` with no override still raises `KeyError` (no invented default trigger — see Decision).

1. In `src/utils/config.py`, change `dispatch_task_admin_defaults` signature to:

```python
def dispatch_task_admin_defaults(
    task_key: str,
    trigger_state: Optional[str] = None,
) -> Dict[str, Any]:
```

2. Replace the body membership gate as follows (keep retired check first, order matters):
   - `tk = (task_key or "").strip()`
   - `retired = dispatch_task_key_retired_message(tk)`; if set → `raise KeyError(retired)` (unchanged)
   - If `tk not in TASK_CONFIG` → `raise KeyError(f"dispatch_task_admin_defaults: unknown task_key {tk!r}")`
   - **Delete** the `if tk not in DISPATCH_SCHEDULABLE_TASK_KEYS: raise KeyError(... not schedulable)` branch
   - `entity_type = _dispatch_entity_type_for_task_key(tk)` (already resolves `check_cover_letter` via `TASK_CONFIG["entity_type"]`)
   - Resolve effective trigger:
     - `override = (trigger_state or "").strip()`
     - If `override`: use it as `effective_ts`
     - Else: `effective_ts = _dispatch_trigger_state_for_task_key(tk)` (may KeyError — do not catch)
   - Return dict with `entity_type`, `trigger_state=effective_ts`, `sort_by=_dispatch_sort_by_for(entity_type, effective_ts)`, `batch_call_mode=_dispatch_batch_call_mode_for(tk)`
   - Update the docstring: defaults for any registered non-retired `TASK_CONFIG` key; optional `trigger_state` required when the key has no derived default trigger rule.

3. In `_dispatch_trigger_state_for_task_key`, **delete** only this gate (leave all explicit branches and the final `TASK_CONFIG` / `not_ready_state` fallthrough unchanged):

```python
if task_key not in DISPATCH_SCHEDULABLE_TASK_KEYS:
    raise KeyError(f"dispatch trigger_state: unknown task_key {task_key!r}")
```

After deletion, keys with `TASK_CONFIG[task_key]["trigger_state"] is None` and no explicit branch (e.g. `check_cover_letter`) still hit the final `raise KeyError(f"dispatch trigger_state: no rule for task_key {task_key!r}")` when called without an override — that is intentional.

⚠️ **Decision:** Do **not** add `check_cover_letter` / `finalize_cover_letter` / `propose_application_responses` to `DISPATCH_SCHEDULABLE_TASK_KEYS`, and do **not** hardcode new per-key trigger branches for them. Parent + child forbid retaining a second curated allowlist for Save acceptance. Form / POST already supply Input State; defaults take that override for column derivation (`sort_by`).

⚠️ **Decision:** Leave `DISPATCH_SCHEDULABLE_TASK_KEYS` itself intact for bootstrap inventory and `_dispatch_task_key_form_meta` enrichment of schedulable keys. This ticket only stops using that frozenset as the Save membership gate.

## Stage 2: Data layer — insert uses request trigger for defaults

**Done when:** `save_dispatch_task(..., task_key="check_cover_letter", trigger_state="CANDIDATE_REVIEW", ...)` no longer raises `ValueError: … not schedulable` solely because the key is outside `DISPATCH_SCHEDULABLE_TASK_KEYS`. Existing schedulable inserts (`grade_do`, `check_job_resume`, `finalize_job_resume`) still derive columns when `trigger_state` is omitted.

1. In `src/data/database.py` `save_dispatch_task`, replace the defaults call:

```python
try:
    defaults = dispatch_task_admin_defaults(task_key, trigger_state=trigger_state)
except KeyError as e:
    raise ValueError(f"dispatch_task task_key rejected: {task_key!r}") from e
```

(Keep the subsequent “fill entity_type / trigger_state from defaults when omitted” logic unchanged; with override passed, `defaults["trigger_state"]` matches the request when provided.)

2. Do **not** change `get_dispatch_row_or_seed_preview_meta` beyond what falls out of Stage 1 (still `dispatch_task_admin_defaults(task_key)` with no override; returns `None` on KeyError for keys without a derived trigger — acceptable for adhoc preview). Do **not** change schema backfill’s `try/except KeyError: continue`.

## Stage 3: Admin API — Save membership = registered catalog

**Done when:** `POST /api/admin/dispatch_tasks` with `task_key=check_cover_letter`, a valid job `trigger_state` (e.g. `CANDIDATE_REVIEW`), and required fields for candidate `somerset` returns **201** (not 400 with `Unknown or non-schedulable`). Same for `PUT` changing `task_key` to `check_cover_letter`. `check_job_resume` / `finalize_job_resume` still save. Retired keys still 400. Completely unknown strings still 400 with `Unknown task_key: …` (no “non-schedulable” wording).

1. In `src/ui/api/api_admin.py` `_dispatch_task_key_trigger_error`, replace the `try/except KeyError` around `dispatch_task_admin_defaults` with an explicit registered-key check. Concrete body:

```python
def _dispatch_task_key_trigger_error(task_key: str, trigger_state: str | None) -> str | None:
    tk = (task_key or "").strip()
    if not tk:
        return "task_key is required"
    retired = dispatch_task_key_retired_message(tk)
    if retired:
        return retired
    if tk not in TASK_CONFIG:
        return f"Unknown task_key: {tk!r}"
    ts = (trigger_state or "").strip()
    if not ts:
        return "trigger_state is required"
    try:
        et = _dispatch_entity_type_for_task_key(tk)
    except KeyError:
        return f"task_key {tk!r} has unsupported entity_type"
    if et not in ENTITY_TYPES:
        return f"task_key {tk!r} has unsupported entity_type {et!r}"
    try:
        registry = dispatch_entity_state_registry(et)
    except KeyError:
        return f"task_key {tk!r} has unsupported entity_type {et!r}"
    registry_ts = ts
    parsed_registry = parse_dispatch_hop_label(ts)
    if parsed_registry:
        registry_ts = parsed_registry[0]
    if registry_ts not in registry:
        return f"task_key {tk!r} ({et}) is not valid for trigger_state {ts!r}"
    if is_dispatch_chain_trigger(registry_ts):
        parsed = parse_dispatch_hop_label(ts)
        if parsed and parsed[1] != tk:
            return f"task_key {tk!r} does not match hop in trigger_state {ts!r}"
    return None
```

2. Import `_dispatch_entity_type_for_task_key` from `src.utils.config` in `api_admin.py` (add to the existing config import block). `TASK_CONFIG` is already imported.

3. In `update_dtask`, when `"task_key" in data`, change the defaults line to pass the effective trigger already computed for validation:

```python
defaults = dispatch_task_admin_defaults(
    (data["task_key"] or "").strip(),
    trigger_state=effective_trigger_state,
)
```

(`effective_trigger_state` is already `data.get("trigger_state", row.get("trigger_state"))` immediately above.)

4. Do **not** change `create_dtask` field list, retired pre-check, or UNIQUE 409 handling. Do **not** change `dispatch_task_keys` / `_dispatch_task_key_form_meta` (picker already lists registered keys).

⚠️ **Decision:** Keep trigger_state **registry** + hop-label matching at Save (existing behavior for `grade_do` + compound hops). Parent AC4’s “not blocked at Save for merely being outside a separate schedulable allowlist” is satisfied by dropping the schedulable membership gate. Completely invalid state strings still 400; a valid registry state that claim/eligibility will not run for still surfaces on first Run — matching “misconfigured pairing fails at run.” Do **not** remove registry checks in this ticket (would expand scope and churn Betty’s existing helper tests without fixing Susan’s repro).

## Stage 4: Manual verification (engineer, before Code Complete)

**Done when:** Local or staging admin can Save `check_cover_letter` for `somerset` without the original 400 string; regression Saves for `check_job_resume` and `finalize_job_resume` still work.

1. After Stages 1–3 compile clean, exercise (or document for UAT) `POST /api/admin/dispatch_tasks` JSON shaped like:

```json
{
  "candidate_id": "somerset",
  "task_key": "check_cover_letter",
  "trigger_state": "CANDIDATE_REVIEW",
  "min_count": 1
}
```

Expect **201** and a new `dispatch_task` row. Confirm response body is not `{"error": "Unknown or non-schedulable task_key: 'check_cover_letter'"}`.

2. Confirm `POST` with `task_key=check_job_resume` and `task_key=finalize_job_resume` still **201** with their usual triggers (`BUILD_ARTIFACTS` defaults via existing schedulable rules when trigger omitted or when form sends the picker default).

3. Confirm `POST` with `task_key=consult_do` still **400** retired messaging.

**Betty note (not engineer work):** AC5 automated coverage (`check_cover_letter` create acceptance + one already-schedulable regression) lands via `qa-child` / `tests/` — do not edit `tests/` or `docs/test-bible/**` on this ticket.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree sub-branch; publish to `origin/sub/AST-856/AST-955-align-scheduled-actions-save-with-task-key-picker` after each stage per `build-child`.
- Do not add files outside the Files Changed table.
- If `dispatch_task_admin_defaults` call sites elsewhere break because of the new optional arg, only keyword-optional use is allowed — positional callers of `(task_key,)` must keep working.
- On ambiguity or codebase drift → stop, comment on parent AST-856 with the blocking template, wait.

## Self-Assessment

**Scope:** Single-Component — utils defaults + data insert + admin Save validation for one admin surface; no dispatcher/core/frontend.

**Conf:** high — root cause is a single membership gate (`DISPATCH_SCHEDULABLE_TASK_KEYS`) duplicated on API + `save_dispatch_task`; picker path already shows the correct catalog.

**Risk:** Medium — admin create/update is critical for Susan’s ops; wrong defaults could write bad `sort_by`/`entity_type` for newly accepted keys, but existing schedulable keys keep the same derivation path when no override is needed.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|--------|
| §1.3 DRY | One membership notion for Save (`TASK_CONFIG`) shared with the picker source (`get_task_keys` / `TASK_CONFIG`); no new parallel allowlist |
| §2.1 config | Defaults and entity/trigger derivation stay in `config.py`; Save stops using a second frozenset as acceptance |
| §2.4 batch | Untouched |
| §2.6 state machine | No new states; registry validation on trigger_state retained |
| §3.3 imports | `api_admin` already imports config; add `_dispatch_entity_type_for_task_key` only |
| §3.5 naming | Keep `dispatch_task_admin_defaults` name; optional `trigger_state` is additive |

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-856/AST-955-align-scheduled-actions-save-with-task-key-picker`  
**Tip:** `0efa2bb` (`0efa2bba`)

**Stages delivered:**
- Stage 1 — `dispatch_task_admin_defaults` accepts registered `TASK_CONFIG` keys + optional `trigger_state`; dropped schedulable-only gate in `_dispatch_trigger_state_for_task_key`
- Stage 2 — `save_dispatch_task` passes request `trigger_state` into defaults
- Stage 3 — `_dispatch_task_key_trigger_error` membership = `TASK_CONFIG` (not `DISPATCH_SCHEDULABLE_TASK_KEYS`); `update_dtask` passes effective trigger into defaults

**Manual:** `check_cover_letter` + `CANDIDATE_REVIEW` helper returns `None` (no `Unknown or non-schedulable`); retired `consult_do` still blocked. AC5 tests → Betty.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-856/AST-955-align-scheduled-actions-save-with-task-key-picker` @ `5f87d19`

### What's solid

| Area | Notes |
| --- | --- |
| Plan fidelity | Stages 1–3 match: `dispatch_task_admin_defaults` membership = `TASK_CONFIG` + optional `trigger_state`; schedulable gate removed from `_dispatch_trigger_state_for_task_key`; `save_dispatch_task` passes request trigger; `_dispatch_task_key_trigger_error` + `update_dtask` use registered-key / effective-trigger path. `DISPATCH_SCHEDULABLE_TASK_KEYS` left for bootstrap / form enrichment. |
| Root cause | Save no longer maps KeyError from schedulable-only defaults to `Unknown or non-schedulable`; unknown strings use `Unknown task_key`; retired keys still blocked. |
| Scope / Self-Assessment | Single-Component footprint (utils + data insert + admin Save). No dispatcher claim, frontend picker, or Manage Tasks / `run_next` churn. Conf high / Risk Medium still fit. |
| Rules | §1.3 DRY / §2.1 config — one Save membership notion (`TASK_CONFIG`) shared with picker source. §3.3 — `api_admin` imports utils only for this change (`_dispatch_entity_type_for_task_key` per plan). §2.4 / §2.6 / §5f / §5g N/A. |
| Tests (Betty) | AC5 create acceptance + schedulable regression present on tip via `merge-tests`; bible notes updated — out of Radia edit scope. |

### Issues

None (**fix-now** / **discuss**).

### Recommended actions

| Severity | Item |
| --- | --- |
| — | None. |

**Verdict:** Clean — `resolve-child` may proceed (no product fixes required beyond this `docs()` commit).


## Resolution (2026-07-22, resolve-child)

**Radia:** clean — **fix-now** / **discuss** none (`docs(AST-955): Radia review — clean` @ `2646527`).

**Product:** no code changes this pass. Stages 1–3 from build remain the ship; Betty `merge-tests` @ `5f87d19` unchanged.

**Outcome:** `resolve(AST-955): — clean` → **User Testing** (assignee Ada).
