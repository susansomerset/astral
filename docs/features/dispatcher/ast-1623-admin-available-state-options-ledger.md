# AST-1623 — Admin Available, state_options, ledger, and live-row backfill

- **Linear:** https://linear.app/astralcareermatch/issue/AST-1623
- **Parent:** AST-1620 — Treat meteorite as a first-class dispatch entity_type
- **Publish ref:** `sub/AST-1620/AST-1623-admin-available-state-options-ledger`

Expose `meteorite` on admin `state_options`, stop Available from short-circuiting on missing `candidate_id` for meteorite rows (call AST-1622’s `count_eligible_for_dispatch_task`), confirm create/update validation already accepts `meteorite` via `ENTITY_TYPES` / `dispatch_entity_state_registry` (AST-1621), write ingress/notify ledger rows with `entity_type='meteorite'`, and UPDATE existing NULL `entity_type` live `dispatch_task` rows for those task keys. Depends on AST-1621 (registries + seed literals) and AST-1622 (count helper). Does not own `ENTITY_TYPES` / registry / `SEED_CONFIG` (sibling 1) or `count_eligible` / `get_due_tasks` (sibling 2).

## Explicit scope gate

Ticket **## Scope** covers only:

- `src/ui/api/api_admin.py` — `state_options` meteorite key; list Available path for meteorite without requiring `candidate_id`; validation via `ENTITY_TYPES` / `dispatch_entity_state_registry`.
- `src/core/dispatcher.py` — ingress/notify `save_dispatch_ledger` `entity_type='meteorite'`; live `dispatch_task` UPDATE NULL→`meteorite` for ingress/notify task keys.

No other files. Do not edit `src/utils/config.py`, `src/data/database.py`, retention seeds, or `meteorite_email` mailbox Avail.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_admin.py` | Add `meteorite` to `state_options`; Available count for meteorite when `entity_type`+`trigger_state` set even if `candidate_id` blank; confirm create/update already accept `meteorite` (no parallel hardcoded set) | ui |
| `src/core/dispatcher.py` | Ingress + bot-blocked notify `save_dispatch_ledger(..., entity_type="meteorite")`; idempotent NULL→`meteorite` correction for those task keys; call correction from `start_scheduler` | core |

## Stage 1: Admin state_options + Available (no candidate_id short-circuit)

**Done when:** `GET /api/admin/dispatch_tasks/state_options` JSON includes `"meteorite"` whose value equals `list(dispatch_entity_state_registry("meteorite").keys())` (same membership as `METEORITE_STATES`). For a `dispatch_task` row with `entity_type='meteorite'`, non-empty `trigger_state`, and NULL/blank `candidate_id`, `list_dtasks` sets `available_count` to `database.count_eligible_for_dispatch_task(row)` (not forced to `0`). Create/update with `entity_type='meteorite'` and a valid `METEORITE_STATES` trigger still succeed via existing `ENTITY_TYPES` checks (no new allowlist). Mailbox Avail path (`is_meteorite_email_mailbox_task_key`) and retention rows (no trigger) unchanged.

1. In `src/ui/api/api_admin.py` `dispatch_task_state_options`, keep the existing `job` / `company` / `candidate` keys. Add:

   ```python
   "meteorite": list(dispatch_entity_state_registry("meteorite").keys()),
   ```

   `dispatch_entity_state_registry` is already imported. Do **not** import `METEORITE_STATES` solely for this endpoint. Do **not** rewrite the endpoint to iterate all of `ENTITY_TYPES` (would reorder / reshuffle existing keys without ticket need).

2. In `list_dtasks`, replace the Available enrichment branch that currently does:

   ```python
   row["available_count"] = (
       database.count_eligible_for_dispatch_task(row) if et and ts and cid else 0
   )
   ```

   with the same gate shape AST-1622 used in `get_due_tasks`:

   - Still skip into the mailbox branch first (`_inbox_avail_task_key`) — unchanged.
   - For the non-mailbox branch: call `count_eligible_for_dispatch_task(row)` when `et` and `ts` are truthy **and** (`cid` is truthy **or** `et == "meteorite"`); otherwise set `available_count` to `0`.
   - Keep the existing `try` / `except` + `logger.warning` around the count call.

   Concrete condition:

   ```python
   if et and ts and (cid or et == "meteorite"):
       row["available_count"] = database.count_eligible_for_dispatch_task(row)
   else:
       row["available_count"] = 0
   ```

   (Preserve the try/except wrapper around the count assignment exactly as today.)

3. **Validation check (no parallel enum):** Confirm `create_dtask` / `update_dtask` / `_dispatch_task_key_trigger_error` already accept `meteorite` because they use `ENTITY_TYPES` and `dispatch_entity_state_registry` (AST-1621 landed on `origin/ftr/AST-1620-treat-meteorite-first-class-entity-type`). Do **not** add a second hardcoded `{"job","company","candidate","meteorite"}` set. If a leftover literal still rejects `meteorite`, remove/replace that literal so membership is only via `ENTITY_TYPES` — still only inside `api_admin.py`.

⚠️ **Decision:** Available mirrors `get_due_tasks`: only `entity_type == "meteorite"` may count with blank `candidate_id`. Other entity types keep the `cid` requirement. Do not special-case by task_key for Available (entity_type is the contract).

⚠️ **Decision:** `state_options` adds one registry-backed key rather than rebuilding the whole map from `ENTITY_TYPES`, so existing client key order for job/company/candidate stays identical.

## Stage 2: Ledger entity_type + live-row NULL→meteorite correction

**Done when:** Grep of the meteorite ingress transition branch and the bot-blocked notify branch in `src/core/dispatcher.py` shows `save_dispatch_ledger(..., entity_type="meteorite")` (no `entity_type=None` on those two calls). After `start_scheduler()` runs (or the correction helper is invoked directly), `list_dispatch_tasks()` rows whose `task_key` is in `{stage_meteorite, scrape_meteorite, land_meteorite, meteorite_bot_blocked_notify}` have non-null `entity_type='meteorite'` — no NULL/`""` left on those keys. Retention and `meteorite_email` rows are not updated by this helper. Second call is a no-op (`updated == 0`).

1. In `src/core/dispatcher.py` `_dispatch_one`, in the `_is_meteorite_ingress_transition_task_key` branch, change the `save_dispatch_ledger` call from `entity_type=None` to `entity_type="meteorite"`. Leave `ledger_cid`, status, and surrounding debug logging unchanged.

2. In the same function, in the `_is_meteorite_bot_blocked_notify_task_key` branch, change that `save_dispatch_ledger` call from `entity_type=None` to `entity_type="meteorite"`. Do **not** change other `save_dispatch_ledger` call sites in this file (mailbox / unified paths stay as they are).

3. Add a public helper near the other meteorite ensure/retire helpers (after `retire_candidate_requested_wrapper_dispatch_tasks` is fine):

   ```python
   def correct_meteorite_ingress_dispatch_entity_types() -> Dict[str, Any]:
   ```

   Behavior:

   - Build the target task_key set from config (already imported in this module):

     ```python
     keys = {
         METEORITE_INGRESS_DISPATCH_CONFIG["stage_task_key"],
         METEORITE_INGRESS_DISPATCH_CONFIG["scrape_task_key"],
         METEORITE_INGRESS_DISPATCH_CONFIG["land_task_key"],
         METEORITE_BOT_BLOCKED_NOTIFY_CONFIG["task_key"],
     }
     ```

     Import `METEORITE_BOT_BLOCKED_NOTIFY_CONFIG` from `src.utils.config` if not already imported alongside `METEORITE_INGRESS_DISPATCH_CONFIG`.

   - Iterate `database.list_dispatch_tasks()` (all rows — global NULL `candidate_id` ingress rows are not visible via `list_dispatch_tasks_for_candidate`).
   - For each row whose stripped `task_key` is in `keys` and whose stripped `entity_type` is empty (`not str(row.get("entity_type") or "").strip()`), call `_db_update_dispatch_task(int(row["id"]), entity_type="meteorite")` (or the module’s `update_dispatch_task` wrapper — same columns whitelist already includes `entity_type`).
   - Return `{"scanned": <int>, "updated": <int>, "task_keys": sorted(keys)}`.
   - Do **not** insert rows, do **not** change `trigger_state` / `auto_mode` / `sort_by`, do **not** touch retention or mailbox keys.

4. In `start_scheduler`, after the stale-ledger INTERRUPTED mark and **before** or **after** the existing AST-1252 retire `try` block (same style), call the correction:

   ```python
   try:
       cstats = correct_meteorite_ingress_dispatch_entity_types()
       _sched_log.info(
           "meteorite ingress/notify entity_type correction scanned=%s updated=%s",
           cstats.get("scanned"),
           cstats.get("updated"),
       )
   except Exception:
       _sched_log.exception("meteorite ingress/notify entity_type correction failed")
   ```

   This is an UPDATE of existing rows, not `save_dispatch_task` provision — it does **not** violate the AST-1496 “no scheduler-start provision” comment. Leave that comment intact; optionally add one line noting this ticket’s correction is UPDATE-only.

⚠️ **Decision:** Correction runs from `start_scheduler` (same pattern as AST-1252 retire), not from `list_dtasks` on every poll. Deploy/restart applies it; the helper remains callable for manual verify. Seed `INSERT … WHERE NOT EXISTS` alone cannot fix live NULL rows (AST-1621 Stage 2 decision).

⚠️ **Decision:** Task keys come from `METEORITE_INGRESS_DISPATCH_CONFIG` / `METEORITE_BOT_BLOCKED_NOTIFY_CONFIG`, not a new hardcoded quartet in dispatcher — `astral.standards.no-hardcoded-sets`.

## Out of scope (siblings / boundaries — do not touch)

- `src/utils/config.py` `ENTITY_TYPES` / registries / `SEED_CONFIG` (AST-1621 — already on ftr)
- `src/data/database.py` `count_eligible_for_dispatch_task` / `get_due_tasks` / new SQL helpers (AST-1622 — already on ftr)
- Rewriting custom meteorite runners into consult / `_run_unified`
- Forcing retention or `meteorite_email` mailbox onto `ENTITY_TYPES` claim semantics
- AST-1616 / AST-1619 modal UX

## Estimate

Confirm Chuckles estimate: 2 — agree

## Traceability

AC3 → Stage 1 (`state_options`); AC4 → Stage 1 (Available); AC5 → Stage 2 (live-row correction); AC6 → Stage 2 (ledger); AC7 → Boundaries / Out of scope (retention + mailbox untouched). Parent AC1–2,4,6 → siblings.

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1623
**Overall:** APPROVED
**Publish ref:** `sub/AST-1620/AST-1623-admin-available-state-options-ledger` @ `3ae3615bc0fa85b1f96226188b6ddeda31e5b658`

### Traceability
AC3→Stage 1 (`state_options`); AC4→Stage 1 (Available gate mirrors AST-1622 `get_due_tasks`); AC5→Stage 2 (`correct_meteorite_ingress_dispatch_entity_types` + `start_scheduler`); AC6→Stage 2 (ingress/notify ledger `entity_type="meteorite"`); AC7→Boundaries (retention + `meteorite_email` mailbox untouched; ledger `entity_type=None` retained on retention path). Parent AC1–2,8–9 N/A (AST-1621); parent AC4,6 partially satisfied here; count/due implementation N/A (AST-1622 on ftr).

### Findings
- **acceptable** — Linear assignee is Katherine, not Joan; Chuckles preflight only.
- **acceptable** — Stage 1 step 3 is verify-only for `ENTITY_TYPES` / `dispatch_entity_state_registry` validation (AST-1621 on ftr); no parallel allowlist if literals are already clean.

context_tokens≈68000

## Review (build stub)

**Publish ref:** `origin/sub/AST-1620/AST-1623-admin-available-state-options-ledger`
**Tip:** `01de74f3`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `2ca13c89` | `state_options` meteorite + Available without candidate_id |
| 2 | `01de74f3` | ledger `entity_type='meteorite'` + live-row NULL→meteorite correction |


## Radia review

# Radia review — AST-1623

**Publish ref:** `origin/sub/AST-1620/AST-1623-admin-available-state-options-ledger` @ `567cd6a6`  
**Baseline:** `origin/dev`  
**Diff:** 15 files, +1311 / −16 (includes AST-1621/1622 sibling rollup on branch)

---

```
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1623
**Publish ref:** 567cd6a6
**Overall:** CLEAN
```

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no agent.py diff |
| astral.agent.do-task-delegation | scoped | not-applicable | no do_task diff |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade-vector diff |
| astral.batch.batch-id-first | scoped | not-applicable | no batch-id format change |
| astral.batch.batch-id-format | scoped | not-applicable | no batch-id format change |
| astral.batch.claim-process-release | scoped | conforms | ledger `entity_type` set; correction UPDATE-only; claim loop unchanged |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no agent_data diff |
| astral.config.config-source-of-truth | scoped | conforms | `state_options` uses `dispatch_entity_state_registry`; task keys from config constants |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets introduced |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no debug paths |
| astral.dispatch.seed-auto-false | scoped | conforms | boot correction is UPDATE-only, not `save_dispatch_task` provision (AST-1496 comment preserved) |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no run_next / chain diff |
| astral.docs.features-single-file-per-ticket | scoped | conforms | AST-1623 issue doc present |
| astral.git.betty-no-src-or-features | scoped | conforms | tests/bible via Betty merge-tests |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer `code(AST-1623)` limited to `api_admin.py` + `dispatcher.py` |
| astral.layers.core-vs-external-bright-line | scoped | conforms | core→data wrappers unchanged; no external imports |
| astral.layers.import-direction | scoped | conforms | no new cross-layer imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts diff |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | `state_options` registry-backed; no hardcoded state lists in UI |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult/render diff |
| astral.idioms.require-auth-on-protected-endpoints | scoped | conforms | existing `@require_admin` on touched endpoints |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed diff in AST-1623 commits |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no catalog reconcile |
| astral.seed.boot-only-not-hot-path | scoped | conforms | scheduler boot runs idempotent UPDATE, not row insert |
| astral.seed.define-approved | scoped | not-applicable | no define surface |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no operator-row reconcile |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage-join paths |
| astral.standards.data-raises-caller-logs | scoped | conforms | data not edited; core logs via `_sched_log` |
| astral.standards.database-header-inventory | scoped | not-applicable | no database.py diff in AST-1623 commits |
| astral.standards.debug-contract-gated | scoped | not-applicable | no debug contract changes |
| astral.standards.dry-and-focused-functions | scoped | conforms | focused helper + two gate relaxations |
| astral.standards.in-scope-only | scoped | conforms | AST-1623 `code()` commits touch only `api_admin.py` + `dispatcher.py` |
| astral.standards.logging-via-utils | scoped | conforms | `_sched_log` only; no new `print()` / raw loggers |
| astral.standards.names-not-ticket-ids | scoped | conforms | domain names only |
| astral.standards.no-cross-contamination | scoped | conforms | retention/mailbox keys excluded from correction set |
| astral.standards.no-hardcoded-sets | scoped | conforms | task keys from `METEORITE_*_CONFIG`; no parallel entity allowlist |
| astral.standards.public-then-helpers | scoped | conforms | public `correct_meteorite_ingress_dispatch_entity_types` |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no utils→data late imports |
| astral.state.core-decides-transitions | scoped | not-applicable | no transition logic diff |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job transition diff |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no runner refactor |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend diff |
| astral.ui.naming-conventions | scoped | not-applicable | no new UI files |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no deploy diff |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1623)` at tip |
| orch.git.commit-vocabulary | universal | conforms | `code` / `docs` / `test` / `merge-tests` |
| orch.git.flow-direction-inviolable | universal | conforms | `sub/AST-1620/AST-1623-*` vs `origin/dev` |
| orch.git.ftr-sub-topology | universal | conforms | child on `sub/<parent>/<child>` |
| orch.git.merge-on-checkout | universal | conforms | `sync(ftr)` in history |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no forbidden git ops observed |
| orch.git.no-dev-agent-branches | universal | conforms | publish ref is `sub/` |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1620 worktree |
| orch.git.three-permanent-branches | universal | conforms | diff vs `origin/dev` |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | plan decisions documented |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–2 match plan |
| orch.pipeline.project-scoped-queues | universal | conforms | explicit scope gate honored |
| orch.pipeline.status-gates-skill-entry | universal | conforms | reviewed at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | Joan APPROVED |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty manifest + component tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Katherine (engineer) |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | engineer still assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path commits observed |

**Active set:** 65 scored in-session.  
**Straggler (C4):** Joan verdict attached; no Excluded statute list — no stragglers.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | plan has no "Patterns to reuse" block; admin Available mirrors AST-1622 `get_due_tasks` gate shape |

## Plan adherence

- **Stage 1:** `state_options` adds registry-backed `"meteorite"` key; `list_dtasks` Available uses `et and ts and (cid or et == "meteorite")`; mailbox branch unchanged; no parallel entity allowlist added.
- **Stage 2:** Ingress + bot-blocked notify `save_dispatch_ledger(..., entity_type="meteorite")`; `correct_meteorite_ingress_dispatch_entity_types` UPDATE-only from config task keys; invoked from `start_scheduler` with try/except + `_sched_log`; retention ledger stays `entity_type=None`.
- **Explicit scope gate:** AST-1623 `code()` commits touch only `api_admin.py` and `dispatcher.py`.
- **Estimate (2):** Footprint matches.

## C6 judgment aids (§5a–§5g)

| Lens | Result |
|------|--------|
| Imports (B1) | OK — no new function-scoped imports |
| Layer compliance (B2) | OK — UI uses existing `database` import; core uses data wrappers |
| Silent failure (D2) | OK — boot correction logs exception via `_sched_log.exception` |
| Fallbacks (D3) | OK — explicit gates; empty `entity_type` treated as blank for correction |
| Logging (E1) | OK — `_sched_log` only |
| Config/state in UI (G1) | OK — `state_options` registry-driven |
| Batch/transitions (H*) | OK — ledger attribution fixed; claim loop unchanged |
| Debug contract (§5f) | N/A |
| External cleanliness (§5g) | N/A |

## Test / bible alignment

- **`TestAst1623AdminMeteoriteStateOptionsAvail`:** `state_options` membership/order; Available for NULL-cid meteorite; job still 0 without cid; create accepts `entity_type='meteorite'`.
- **`TestAst1623MeteoriteLedgerAndBackfill`:** ingress + notify ledger kwargs; correction scans/updates/idempotency; retention/grade_do skipped; `start_scheduler` invokes correction; boot stub updated.

Betty manifest in `docs/test-bible/ui/api/api_admin.md` matches.

## Findings

### fix-now
(none)

### discuss
(none)

### advisory

1. **`run_task` logging enrichment still gates on `cid`** (`dispatcher.py` ~1470: `count_eligible… if et and ts else 0`). `list_dtasks` and `_run_dispatch_loop` are fixed; this path only affects log `available_count` for UI-initiated runs, not execution. Out of AST-1623 explicit scope gate — optional follow-up if operators rely on that log line.

2. **Boot correction scans all `dispatch_task` rows** on every `start_scheduler` — acceptable at current scale; note if row count grows materially.

3. **Three-dot diff includes AST-1621/1622 sibling rollup** (`config.py`, `database.py`, sibling issue docs/tests). AST-1623 product commits are `api_admin.py` + `dispatcher.py` only — epic-branch coupling expected until ftr merge.

4. **Create test uses `grade_do` + `entity_type='meteorite'`** — validates `ENTITY_TYPES` path, not a recommended admin combo; sufficient for step-3 verify-only.

## What's solid

- Available gate mirrors AST-1622 `get_due_tasks` contract exactly.
- Correction uses config task keys, skips retention/mailbox, idempotent, UPDATE-only (AST-1496 safe).
- Retention ledger deliberately left `entity_type=None` per plan AC7.
- Tests cover ledger kwargs, correction boundaries, boot wiring, and admin paths.

## Frame diff

Post-Joan (`3ae3615b`) → tip (`567cd6a6`):

| Area | Change | Ticket |
|------|--------|--------|
| `src/ui/api/api_admin.py` | `state_options` meteorite + Available gate | **AST-1623** |
| `src/core/dispatcher.py` | ledger `entity_type="meteorite"` + correction + boot hook | **AST-1623** |
| `tests/.../test_api_admin.py`, `test_dispatcher.py` | AST-1623 test classes + boot stub | **AST-1623** |
| `docs/test-bible/ui/api/api_admin.md` | Betty manifest | **AST-1623** |
| `config.py`, `database.py`, sibling docs/tests | AST-1621/1622 rollup | siblings |

AST-1623 product surface is admin + dispatcher only.

## Notes

- Joan APPROVED @ `3ae3615b`; assignee + verify-only validation findings closed — no re-litigation.
- Completes parent epic admin/ledger/backfill slice; pairs with AST-1621 registries and AST-1622 count/due.
- C7 complete; recommend **Review Posted**.

context_tokens≈48000

---

```
[code-rubric] PROCEED (Commit: 567cd6a6) admin ledger backfill clean
```
