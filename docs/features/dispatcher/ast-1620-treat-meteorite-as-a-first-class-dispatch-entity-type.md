# AST-1620 — Treat meteorite as a first-class dispatch entity_type

<!-- linear-archive: AST-1620 archived 2026-09-24 -->

## Linear archive (AST-1620)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1620/treat-meteorite-as-a-first-class-dispatch-entity-type  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** None / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Meteorite staging rows already have a table, `METEORITE_STATES`, and `batch_id` claim helpers, but dispatch still treats those runners as NULL-`entity_type` shells — so admin Available, `count_eligible_for_dispatch_task`, and AUTO-due never see them the way `candidate` / `company` / `job` do. This epic promotes `meteorite` into `ENTITY_TYPES` and the shared claim/count/Avail/AUTO-due path so Scheduled Actions and the scheduler can operate on meteorite the same way as other product entity queues. AST-1616 keeps owning the editable Entity Type control; this ticket owns making `meteorite` a real member of that set and the machinery behind it.

## Functional scope

* `meteorite` is a first-class product entity type alongside `candidate`, `company`, and `job` — listed in `ENTITY_TYPES` and documented in Code Rules as a dispatch claim queue.
* Dispatch state validation, admin Input State options, and sort defaults for `entity_type=meteorite` resolve from `METEORITE_STATES` (not `JOB_STATES` / `METEORITE_*` job labels).
* Shared eligibility counting, admin Available, and AUTO-due include meteorite dispatch rows that use the existing meteorite `batch_id` claim pool — including global (NULL `candidate_id`) ingress rows, which today are gated out by the candidate-bound count/due path.
* Ingress transition seeds (`stage_meteorite` / `scrape_meteorite` / `land_meteorite`) and the BOT_BLOCKED notify seed store `entity_type='meteorite'` instead of NULL; existing matching NULL rows are corrected. Retention hygiene (NULL trigger) and meteorite_email mailbox shells stay non-claim as today.
* Out of scope: rewriting custom meteorite transition runners into the consult / `_run_unified` path; changing AST-1616 modal UX; per-candidate rebinding of global ingress seeds.

## Component scope

* `src/utils/config.py` — **modified** — add `meteorite` to `ENTITY_TYPES`; map it in `dispatch_entity_state_registry`, `dispatch_claim_states`, and `_dispatch_sort_by_for`; set ingress/notify seed SQL and any catalog defaults that still advertise NULL entity type for those keys.
* `docs/ASTRAL_CODE_RULES.md` — **modified** — ENTITY_TYPES bullet and §2.4 claim-queue wording include `meteorite`.
* `src/data/database.py` — **modified** — `count_eligible_for_dispatch_task` / `get_due_tasks` (and any shared unclaimed-state count helper) support `entity_type=meteorite` for the global pool without requiring `candidate_id`.
* `src/ui/api/api_admin.py` — **modified** — `state_options` exposes `meteorite` → `METEORITE_STATES` keys; Available counting and create/update validation accept meteorite without inventing a parallel enum.
* `src/core/dispatcher.py` — **modified** — meteorite ingress/notify ledger writes use `entity_type='meteorite'` (not NULL) so ledger/Avail language matches the claim queue.

## Technical scope

* `config.ENTITY_TYPES` — append `meteorite` so every `ENTITY_TYPES` membership check and admin option source includes it.
* `config.dispatch_entity_state_registry` — return `METEORITE_STATES` for `meteorite` (fail loud on unknown types unchanged).
* `config.dispatch_claim_states` — resolve retry/companion rules through `METEORITE_STATES` when `entity_type` is `meteorite` (today only job/company/candidate registries are consulted).
* `config._dispatch_sort_by_for` — define a meteorite sort default (existing ingress seeds use `updated_at`).
* `config.SEED_CONFIG` — `dispatch_task-meteorite-ingress` and `dispatch_task-meteorite-bot-blocked-notify` INSERT `entity_type` as `'meteorite'` instead of NULL; leave retention seed as non-claim (NULL trigger).
* `docs/ASTRAL_CODE_RULES.md` — update ENTITY_TYPES list and the §2.4 sentence that names claim-queue members so `meteorite` is included.
* `database.count_eligible_for_dispatch_task` — when `entity_type` is `meteorite` and `trigger_state` is set, count unclaimed meteorite rows in the claim states **without** requiring `candidate_id` (global pool); keep the existing candidate-required gate for other entity types.
* `database.get_due_tasks` — include AUTO meteorite rows that pass the same eligibility/min_count bar even when `candidate_id` is NULL.
* `api_admin.dispatch_task_state_options` — add a `meteorite` key listing `METEORITE_STATES` keys.
* `api_admin` list Available path — when `entity_type` is `meteorite` and trigger is set, call `count_eligible_for_dispatch_task` without requiring `candidate_id`.
* `api_admin` create/update validation — accept `meteorite` via `ENTITY_TYPES` / `dispatch_entity_state_registry` (no parallel hardcoded set).
* `dispatcher` meteorite ingress/notify ledger `save_dispatch_ledger` — pass `entity_type='meteorite'` instead of `None`.
* One-time correction — UPDATE existing `dispatch_task` rows for those ingress/notify task keys from NULL `entity_type` to `meteorite` (seed-only INSERT NOT EXISTS will not fix live rows).

## Architectural definition

**Patterns to reuse**

* [`pattern.batch.entity-claim-process-release`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/batch/pattern.batch.entity-claim-process-release.md>) — meteorite joins the claim → process → release shape already used by other ENTITY_TYPES queues; runners keep using existing `claim_meteorite_batch` / clear helpers.
* [`pattern.state.entity-state-transitions`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/state/pattern.state.entity-state-transitions.md>) — trigger validity and transitions stay driven by `METEORITE_STATES`, not a parallel list.
* [`pattern.config.config-block`](<https://github.com/susansomerset/astral/blob/dev/canon/patterns/config/pattern.config.config-block.md>) — registry and seed literals stay in `config.py`.

**New patterns proposed**

* none

**Applicable statutes**

* [`astral.config.config-source-of-truth`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/config/astral.config.config-source-of-truth.md>) — entity membership and state registries live in config, not scattered literals.
* [`astral.standards.no-hardcoded-sets`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-hardcoded-sets.md>) — do not invent a second meteorite entity enum in admin/UI.
* [`astral.batch.batch-id-first`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/batch/astral.batch.batch-id-first.md>) — claim/count stay batch_id-first on the meteorite table.
* [`astral.batch.claim-process-release`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/batch/astral.batch.claim-process-release.md>) — Avail/AUTO-due must reflect the same claim pool the runners lock.
* [`astral.standards.in-scope-only`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>) — no consult rewrite; no mailbox/retention redesign.
* [`astral.standards.dry-and-focused-functions`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.dry-and-focused-functions.md>) — extend shared count/due helpers rather than a one-off meteorite Avail fork.
* [`astral.standards.public-then-helpers`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.public-then-helpers.md>) — keep new count helpers grouped with existing eligibility helpers.
* [`astral.standards.database-header-inventory`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.database-header-inventory.md>) — no new tables; meteorite + dispatch_task columns only.
* [`astral.standards.data-raises-caller-logs`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.data-raises-caller-logs.md>) — data raises; API/dispatcher log.
* [`astral.standards.logging-via-utils`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.logging-via-utils.md>) — any new logs use utils logging.
* [`astral.standards.names-not-ticket-ids`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.names-not-ticket-ids.md>) — no ticket ids in new identifiers.
* [`astral.standards.no-cross-contamination`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.no-cross-contamination.md>) — layer imports stay clean.
* [`astral.layers.ui-config-driven-business-logic`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.ui-config-driven-business-logic.md>) — state options and validation resolve from config registries.
* [`astral.dispatch.seed-auto-false`](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/dispatch/astral.dispatch.seed-auto-false.md>) — seed `auto_mode` stays false on ingress/notify seeds.

## Acceptance criteria

1. `ENTITY_TYPES` contains `meteorite` — `python -c "from src.utils.config import ENTITY_TYPES; assert 'meteorite' in ENTITY_TYPES"` exits 0. Fail: `meteorite` absent from the list.
2. `dispatch_entity_state_registry("meteorite")` returns a mapping whose keys equal `set(METEORITE_STATES)`. Fail: `KeyError`, or keys match `JOB_STATES` / omit staging states like `SCRAPE_LINK`.
3. `GET /api/admin/dispatch_tasks/state_options` JSON includes a `meteorite` array equal to `METEORITE_STATES` keys. Fail: missing key, or options still only `job`/`company`/`candidate`.
4. With unclaimed meteorite rows in `NEW` and a global `stage_meteorite` row with `entity_type='meteorite'`, `trigger_state='NEW'`, NULL `candidate_id`, `count_eligible_for_dispatch_task(row)` returns that unclaimed count (≥1). Fail: returns 0 solely because `candidate_id` is NULL while eligible rows exist.
5. Admin Scheduled Actions Available for that `stage_meteorite` row matches the count helper (non-zero when eligible rows exist). Fail: Available stays 0 while count would be >0, or still short-circuits on missing `candidate_id`.
6. `SEED_CONFIG["dispatch_task-meteorite-ingress"]` SQL inserts `entity_type` as the literal `meteorite` (not NULL) for `stage_meteorite` / `scrape_meteorite` / `land_meteorite`; same for `dispatch_task-meteorite-bot-blocked-notify`. Fail: `grep` of those seed strings still shows `, NULL, 'NEW'` / `, NULL, 'BOT_BLOCKED'` entity_type positions.
7. After the correction path runs (or equivalent UPDATE), live `dispatch_task` rows for those ingress/notify keys have `entity_type='meteorite'` — `SELECT entity_type FROM dispatch_task WHERE task_key IN ('stage_meteorite','scrape_meteorite','land_meteorite','meteorite_bot_blocked_notify')` has no NULL. Fail: NULL entity_type remains on those keys.
8. Meteorite ingress/notify `save_dispatch_ledger` calls pass `entity_type='meteorite'` (grep `entity_type=None` on those branches returns nothing). Fail: ledger still written with `entity_type=None` for those runners.
9. Retention seed and meteorite_email mailbox path remain non-claim (NULL trigger and/or mailbox fold) — not forced onto `ENTITY_TYPES` claim semantics. Fail: retention incorrectly required to have `entity_type='meteorite'` + a METEORITE_STATES trigger to boot.

## Open questions

none

## Proposed child tickets

#### 1!: **Register meteorite in ENTITY_TYPES and dispatch registries - Ada**

Add `meteorite` to `ENTITY_TYPES`; wire `dispatch_entity_state_registry`, `dispatch_claim_states`, and `_dispatch_sort_by_for` to `METEORITE_STATES`; update Code Rules ENTITY_TYPES / §2.4 claim-queue wording; flip ingress + BOT_BLOCKED notify `SEED_CONFIG` SQL to `entity_type='meteorite'`. Does not own count/due/Available runtime or ledger edits (after #2 / #3).
**Citations:** `pattern.config.config-block`; `pattern.state.entity-state-transitions`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.dispatch.seed-auto-false`
**Scope:** `src/utils/config.py` — ENTITY_TYPES append; registry/claim_states/sort_by meteorite branches; SEED_CONFIG ingress + bot-blocked entity_type literals. `docs/ASTRAL_CODE_RULES.md` — ENTITY_TYPES bullet and §2.4 claim-queue member list include meteorite.
**Estimate: 2**

#### 2!: **Meteorite count_eligible and AUTO-due without candidate_id - Hedy**

Extend `count_eligible_for_dispatch_task` and `get_due_tasks` so `entity_type=meteorite` with a trigger_state counts/dues the global unclaimed meteorite pool (NULL `candidate_id` allowed). After #1. Does not own admin Available short-circuit or ledger entity_type (after #3).
**Citations:** `pattern.batch.entity-claim-process-release`; `astral.batch.batch-id-first`; `astral.batch.claim-process-release`; `astral.standards.dry-and-focused-functions`; `astral.standards.public-then-helpers`; `astral.standards.database-header-inventory`; `astral.standards.data-raises-caller-logs`
**Scope:** `src/data/database.py` — meteorite branch in `count_eligible_for_dispatch_task` (no candidate_id required); `get_due_tasks` include AUTO meteorite rows with NULL candidate_id when eligible; any shared unclaimed-meteorite-in-states count helper used by that path.
**Estimate: 3**

#### 3: **Admin Available, state_options, ledger, and live-row backfill - Katherine**

Expose `meteorite` on admin state_options; Available counting skips the candidate_id short-circuit for meteorite; create/update validation accepts meteorite via shared registries; dispatcher ingress/notify ledger uses `entity_type='meteorite'`; UPDATE existing NULL entity_type rows for ingress/notify task keys. After #1 (and uses #2 count helper for Available).
**Citations:** `pattern.batch.entity-claim-process-release`; `astral.layers.ui-config-driven-business-logic`; `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only`; `astral.standards.no-cross-contamination`; `astral.standards.logging-via-utils`; `astral.standards.names-not-ticket-ids`
**Scope:** `src/ui/api/api_admin.py` — state_options meteorite key; list Available path for meteorite without requiring candidate_id; validation via ENTITY_TYPES / dispatch_entity_state_registry. `src/core/dispatcher.py` — ingress/notify `save_dispatch_ledger` entity_type=`meteorite`. Live `dispatch_task` UPDATE NULL→meteorite for ingress/notify task keys (seed INSERT alone insufficient).
**Estimate: 2**

---

## Original brief

Add `meteorite` to `ENTITY_TYPES` and wire it through the same dispatch_task claim / Avail / AUTO-due path as `candidate` / `company` / `job`: `METEORITE_STATES`, `batch_id` claim, `count_eligible_for_dispatch_task`, admin Available, and ingress seeds using `entity_type='meteorite'` instead of NULL.

Spawned from the AST-1616 thread (editable Entity Type on Scheduled Actions). AST-1616 stays the modal/API unlock for choosing Entity Type among product types; this ticket owns promoting `meteorite` into that set and the shared claim/count machinery.

Related: AST-1616

### Comments

#### chuckles — 2026-09-10T01:18:10.970Z
AST-1621 REVIEW — merge-child blocked; recalling @Ada Lovelace to restack sub on origin/ftr/AST-1620-treat-meteorite-first-class-entity-type (ftr refreshed past sub tip) then republish.

#### chuckles — 2026-09-10T01:03:01.354Z
AST-1621 STALE(dev+59) — pausing build; recalling @Ada Lovelace to refresh sub/* (merge origin/dev + origin/ftr/AST-1620 + republish) before build-child.

---

_Implementation detail may live in git history on `origin/dev`._
