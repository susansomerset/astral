# AST-1616 — Make all fields on Add Dispatch Task modal editable

<!-- linear-archive: AST-1616 archived 2026-09-24 -->

## Linear archive (AST-1616)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1616/make-all-fields-on-add-dispatch-task-modal-editable  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Admins cannot set `entity_type` on the Scheduled Actions Add/Edit Task modal — the control is read-only and auto-filled from the task-key catalog — yet a usable dispatch row needs a correct entity type for claim queues and Input State options. This epic makes Entity Type a first-class editable field on that modal (Add and Edit), persists the chosen value through the admin create/update APIs, and keeps Input State / sort derivation aligned with the chosen entity. Candidate on Add stays bound to the page-selected candidate (not part of this unlock).

## Functional scope

* Admin can change Entity Type in the Add Task and Edit Task modals on Scheduled Actions, choosing among the product entity types (candidate, company, job), with the catalog default still pre-filled when Task changes.
* Saving Add or Edit persists the chosen Entity Type on the `dispatch_task` row (not only the catalog-derived default).
* Input State options continue to follow the Entity Type currently shown in the form; changing Entity Type clears an Input State that is invalid for the new entity.
* Create and update validation for Input State uses the submitted Entity Type (not a silent re-derive that ignores the form), and when Entity Type is overridden relative to the task-key catalog, sort/batch defaults for the row follow the chosen entity + trigger pair.
* Out of scope: making Candidate editable on Add; changing scheduler/claim runtime semantics beyond reading the stored `entity_type`; mailbox poller special-cases beyond still allowing a valid save path.

## Component scope

* `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — **modified** — replace read-only Entity Type with an editable control; include `entity_type` in create and update save payloads; clear invalid Input State when Entity Type changes.
* `src/ui/api/api_admin.py` — **modified** — accept and persist `entity_type` on POST `/dispatch_tasks` and PUT `/dispatch_tasks/<id>`; validate trigger_state against the submitted entity type; when entity_type is supplied or changed, set sort_by (and related insert defaults) from the chosen entity + trigger rather than overwriting from task-key-only defaults.
* `src/data/database.py` — **modified** — on `save_dispatch_task`, when caller supplies `entity_type`, compute `sort_by` for that entity + trigger instead of always using task-key catalog defaults; ensure `update_dispatch_task` continues to accept `entity_type` / `sort_by` updates already in the column whitelist.

## Technical scope

* `AdminScheduledActions.tsx` — change the Entity Type row from a read-only text input to a select (or equivalent) whose options are the entity keys already available from state options / `ENTITY_TYPES`; on Task change, still pre-fill from catalog meta but leave the control editable; on Entity Type change, clear `trigger_state` when it is not in the new entity's option list; include `entity_type` in both POST and PUT JSON bodies in `handleSave`.
* `api_admin.create_dtask` — pass request `entity_type` through to `save_dispatch_task`; reject unknown entity types; run trigger validation against the effective (submitted or catalog) entity type.
* `api_admin.update_dtask` — add `entity_type` to the allowed update set; when `entity_type` and/or `trigger_state` / `task_key` change, recompute `sort_by` for the effective entity + trigger and stop forcing catalog `entity_type` whenever `task_key` alone changes if the client also sent an explicit `entity_type`.
* `api_admin._dispatch_task_key_trigger_error` (or a thin wrapper) — accept an optional entity-type override so validation uses the form value when present.
* `database.save_dispatch_task` — when `entity_type` is provided, keep it and derive `sort_by` via the existing entity/trigger sort helper for that pair (mailbox null-entity path unchanged); when omitted, keep current catalog-default behavior.

## Architectural definition

**Patterns to reuse**

* [`pattern.ui.admin-endpoint`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.admin-endpoint.md>) — keep create/update on the admin blueprint with auth; resolve entity/trigger rules in the API, not only in React.
* [`pattern.ui.shared-button-roles`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.shared-button-roles.md>) — keep existing modal Save/Cancel `btn` roles; no new button vocabulary.
* [`pattern.ui.icon-control`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/ui/pattern.ui.icon-control.md>) — modal × stays an icon-control; unchanged.

**New patterns proposed**

* none

**Applicable statutes**

* [`astral.config.config-source-of-truth`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>) — Entity Type options and claim semantics come from `ENTITY_TYPES` / config registries, not a parallel UI list.
* [`astral.standards.no-hardcoded-sets`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>) — do not invent a second entity-type enum in the modal; bind to config/`ENTITY_TYPES` (or the entity keys already returned by state options).
* [`astral.standards.in-scope-only`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>) — touch only the listed modal + admin create/update + save_dispatch_task sort path.
* [`astral.standards.no-cross-contamination`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-cross-contamination.md>) — UI stays on admin API; no data/external imports from React.
* [`astral.layers.ui-config-driven-business-logic`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.ui-config-driven-business-logic.md>) — trigger validity and sort defaults resolved server-side from config.
* [`astral.idioms.require-auth-on-protected-endpoints`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/idioms/astral.idioms.require-auth-on-protected-endpoints.md>) — existing `@require_admin` on these routes stays.
* [`astral.ui.frontend-file-placement`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/ui/astral.ui.frontend-file-placement.md>) — edit stays in the existing Scheduled Actions page module.
* [`astral.ui.naming-conventions`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/ui/astral.ui.naming-conventions.md>) — follow existing admin form control naming.
* [`astral.standards.dry-and-focused-functions`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.dry-and-focused-functions.md>) — reuse existing entity/trigger helpers rather than duplicating registries.
* [`astral.standards.public-then-helpers`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.public-then-helpers.md>) — keep new helpers grouped under existing admin dispatch helpers.
* [`astral.standards.database-header-inventory`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.database-header-inventory.md>) — no new tables; only existing `dispatch_task` columns.
* [`astral.standards.data-raises-caller-logs`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.data-raises-caller-logs.md>) — data keeps raising; API maps errors.
* [`astral.standards.logging-via-utils`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.logging-via-utils.md>) — any new API logs use utils logging.
* [`astral.standards.utils-data-late-import-only`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.utils-data-late-import-only.md>) — if database calls sort helpers, keep late-import discipline.
* [`astral.standards.names-not-ticket-ids`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.names-not-ticket-ids.md>) — no ticket ids in new identifiers.
* [`astral.standards.debug-contract-gated`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.debug-contract-gated.md>) — no new backend debug-contract surface in this UI-admin epic (N/A beyond not inventing ungated debug lines if touched).

## Acceptance criteria

1. In Scheduled Actions → Add Task, after choosing a Task, the Entity Type control is not `readOnly` / not opacity-locked text — `grep -n 'Entity Type' -A6 src/ui/frontend/src/pages/AdminScheduledActions.tsx` shows an editable control (e.g. `<select>`) rather than `readOnly`. Fail: Entity Type remains `readOnly`.
2. Changing Entity Type in the modal changes the Input State option list to that entity's states (company vs candidate vs job). Fail: Input State options stay tied to the previous entity after Entity Type changes.
3. POST `/api/admin/dispatch_tasks` with an explicit `entity_type` stores that value on the new row (`SELECT entity_type FROM dispatch_task WHERE id=…` matches the body). Fail: row entity_type is only the catalog default or NULL despite a valid body value.
4. PUT `/api/admin/dispatch_tasks/<id>` with `entity_type` updates the row (and does not require a `task_key` change to stick). Fail: entity_type ignored or overwritten solely from task-key defaults when the client sent a value.
5. POST/PUT with `entity_type` + `trigger_state` where the trigger is not in that entity's registry returns 400 with a clear error. Fail: 200/201 with an inconsistent pair, or validation still keyed only to catalog entity while ignoring submitted entity_type.
6. When saved entity_type differs from the task-key catalog default, the stored `sort_by` matches the sort rule for the **chosen** entity + trigger (same helper path as other dispatch rows). Fail: sort_by remains the catalog entity's sort while entity_type was overridden.
7. Candidate on Add remains read-only / context-bound to the selected candidate. Fail: Candidate becomes a free-text rebinding control as part of this epic.

## Open questions

none

## Proposed child tickets

#### 1!: **Persist chosen entity_type on admin create/update - Ada**

Own the API + data path so Add/Edit can save an explicit Entity Type: forward `entity_type` on create, allow it on update, validate trigger_state against the submitted entity, and recompute `sort_by` for the chosen entity + trigger (including when create supplies entity_type). Does not own the React control. After this lands, curl/API can set entity_type even before the UI ships.
**Citations:** `pattern.ui.admin-endpoint`; `astral.config.config-source-of-truth`; `astral.layers.ui-config-driven-business-logic`; `astral.idioms.require-auth-on-protected-endpoints`; `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only`; `astral.standards.no-cross-contamination`; `astral.standards.database-header-inventory`; `astral.standards.data-raises-caller-logs`; `astral.standards.dry-and-focused-functions`; `astral.standards.public-then-helpers`; `astral.standards.utils-data-late-import-only`
**Scope:** `src/ui/api/api_admin.py` — modified — create/update accept entity_type; trigger validation uses submitted entity; recompute sort_by on entity/trigger/task_key changes. `src/data/database.py` — modified — `save_dispatch_task` uses caller entity_type and derives sort_by for that entity + trigger when provided.
**Estimate: 3**

#### 2: **Editable Entity Type control on Scheduled Actions modal - Katherine**

Own the Add/Edit modal UX: replace read-only Entity Type with an editable select bound to product entity types, keep task-key prefill, clear invalid Input State on entity change, and send `entity_type` on Save for both create and update. Does not own API validation (after #1). Candidate stays context-bound.
**Citations:** `pattern.ui.shared-button-roles`; `pattern.ui.icon-control`; `astral.ui.frontend-file-placement`; `astral.ui.naming-conventions`; `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only`; `astral.standards.no-cross-contamination`
**Scope:** `src/ui/frontend/src/pages/AdminScheduledActions.tsx` — modified — editable Entity Type control; include entity_type in create/update payloads; clear invalid trigger_state when entity_type changes.
**Estimate: 2**

---

## Original brief

The entity_type field in the dispatch task modal is not editable and is also required. So. please just make it editable.

### Comments

#### chuckles — 2026-09-10T00:28:28.502Z
[check-linear] answered — filed AST-1620 Discussion → Chuckles for define-parent

AST-1620: treat `meteorite` as a first-class dispatch `entity_type` (ENTITY_TYPES + claim/Avail/AUTO-due + seeds). Description points at AST-1616. Related link set.

AST-1616 stays the editable-Entity-Type modal/API ticket — finishing that implement is outside this check pass (task lane next), not redefined here.

#### susan — 2026-09-10T00:26:52.811Z
@chuckles Create a new ticket with the original brief pointing to this ticket, and set it to discussion assigned to yourself to trigger the define-linear work. Then, finish this ticket for editing the entity type

#### chuckles — 2026-09-10T00:23:51.691Z
[check-linear] answered — agree: `meteorite` should be a first-class dispatch entity_type

You're right. `METEORITE_STATES` + `claim_meteorite_batch` already behave like an entity claim queue; the NULL-`entity_type` shell is a parallel path that leaves Avail/AUTO due blind. Unifying means:

1. Add `meteorite` to `ENTITY_TYPES`
2. Hook `METEORITE_STATES` into `dispatch_claim_states` / state-registry helpers
3. Extend `count_eligible_for_dispatch_task` (+ `get_due_tasks` / admin Avail) to count unclaimed `meteorite` rows by trigger_state (global pool — `candidate_id` NULL still OK if count/claim don't require cid for this entity)
4. Repoint ingress `SEED_CONFIG` / live rows to `entity_type='meteorite'` instead of NULL

That is **beyond** AST-1616's current AC (editable Entity Type among candidate/company/job only). Say the word and I'll expand this ticket's definition to include the fourth entity + count/claim wiring, or file a sibling under Dispatcher/Meteorite — your call on packaging.

#### susan — 2026-09-10T00:22:33.644Z
@chuckles I think you just stated the clear argument that meteorite IS an entity_type.  We need to add it to the set, include batch_id, states, etc., so that they are treated the same as other entities in dispatch_task.

#### chuckles — 2026-09-10T00:20:52.699Z
[check-linear] answered — Avail column is 0; real backlog is `meteorite` rows

Scheduled Actions **Available** for these NULL-`entity_type` / NULL-`candidate_id` ingress rows stays **0**: `count_eligible_for_dispatch_task` (and `list_dtasks`) only count ENTITY_TYPES claim queues (`candidate`/`company`/`job` + trigger + candidate_id). Null-entity shells short-circuit to 0 by design.

Work is not gated on that number. On Click, the meteorite runners claim unclaimed `meteorite` rows in the row's `trigger_state` via `claim_meteorite_batch` (NEW / SCRAPE_LINK / READY / BOT_BLOCKED), up to `batch_size`. That table count is the real backlog; it is not wired into the Avail column yet. Seeds keep `auto_mode=0`; AUTO due also skips null-entity shells.

#### susan — 2026-09-10T00:19:05.612Z
Then how is the availability count determined, @chuckles?

#### chuckles — 2026-09-10T00:18:35.291Z
[check-linear] answered — keep `entity_type` NULL (not `meteorite`)

`ENTITY_TYPES` is only `candidate` / `company` / `job`. Ingress runners (`stage_meteorite` / `scrape_meteorite` / `land_meteorite` / bot-blocked / retention) are table-claim rows: `SEED_CONFIG` and `TASK_CONFIG` both seed/store `entity_type` NULL. Writing `meteorite` would be invalid for claim/state registries and is not what the seeds use.

#### susan — 2026-09-10T00:17:01.446Z
@chuckles should the entity_type be 'meteorite' on this record?

#### chuckles — 2026-09-10T00:00:25.796Z
[check-linear] answered — ingress `dispatch_task` inserts (from `SEED_CONFIG`, auto_mode=0)

Global pool rows (`candidate_id` NULL) — paste/run in admin SQL:

```sql
INSERT INTO dispatch_task (
  candidate_id, task_key, entity_type, trigger_state, sort_by,
  batch_call_mode, freq_hrs, min_count, batch_size, auto_mode, score_floor
) SELECT NULL, 'stage_meteorite', NULL, 'NEW', 'updated_at',
  0, 0.1, 1, 10, 0, NULL
WHERE NOT EXISTS (
  SELECT 1 FROM dispatch_task d
  WHERE d.candidate_id IS NULL
    AND d.task_key = 'stage_meteorite'
    AND d.trigger_state = 'NEW'
);

INSERT INTO dispatch_task (
  candidate_id, task_key, entity_type, trigger_state, sort_by,
  batch_call_mode, freq_hrs, min_count, batch_size, auto_mode, score_floor
) SELECT NULL, 'scrape_meteorite', NULL, 'SCRAPE_LINK', 'updated_at',
  0, 0.1, 1, 10, 0, NULL
WHERE NOT EXISTS (
  SELECT 1 FROM dispatch_task d
  WHERE d.candidate_id IS NULL
    AND d.task_key = 'scrape_meteorite'
    AND d.trigger_state = 'SCRAPE_LINK'
);

INSERT INTO dispatch_task (
  candidate_id, task_key, entity_type, trigger_state, sort_by,
  batch_call_mode, freq_hrs, min_count, batch_size, auto_mode, score_floor
) SELECT NULL, 'land_meteorite', NULL, 'READY', 'updated_at',
  0, 0.1, 1, 10, 0, NULL
WHERE NOT EXISTS (
  SELECT 1 FROM dispatch_task d
  WHERE d.candidate_id IS NULL
    AND d.task_key = 'land_meteorite'
    AND d.trigger_state = 'READY'
);

INSERT INTO dispatch_task (
  candidate_id, task_key, entity_type, trigger_state, sort_by,
  batch_call_mode, freq_hrs, min_count, batch_size, auto_mode, score_floor
) SELECT NULL, 'meteorite_bot_blocked_notify', NULL, 'BOT_BLOCKED', 'updated_at',
  0, 0.1, 1, 10, 0, NULL
WHERE NOT EXISTS (
  SELECT 1 FROM dispatch_task d
  WHERE d.candidate_id IS NULL
    AND d.task_key = 'meteorite_bot_blocked_notify'
    AND d.trigger_state = 'BOT_BLOCKED'
);

INSERT INTO dispatch_task (
  candidate_id, task_key, entity_type, trigger_state, sort_by,
  batch_call_mode, freq_hrs, min_count, batch_size, auto_mode, score_floor
) SELECT NULL, 'meteorite_retention', NULL, NULL, 'updated_at',
  0, 24, 0, 200, 0, NULL
WHERE NOT EXISTS (
  SELECT 1 FROM dispatch_task d
  WHERE d.candidate_id IS NULL
    AND d.task_key = 'meteorite_retention'
);
```

Mailbox fan-in (`meteorite_email` → `check_inbox`) is **per-candidate**, not NULL — use existing provision / candidate row, not these global inserts. AST-1616 (editable Add Dispatch Task modal) still unblocked for later.

#### susan — 2026-09-09T23:58:01.807Z
@chuckles Please provide an insert statement for dispatch_task I can run from the admin tool to insert the needed meteorite ingress tasks to run, before you implement this issue.

---

_Implementation detail may live in git history on `origin/dev`._
