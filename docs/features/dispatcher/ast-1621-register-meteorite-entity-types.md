# AST-1621 — Register meteorite in ENTITY_TYPES and dispatch registries

- **Linear:** https://linear.app/astralcareermatch/issue/AST-1621
- **Parent:** AST-1620 — Treat meteorite as a first-class dispatch entity_type
- **Publish ref:** `sub/AST-1620/AST-1621-register-meteorite-entity-types`

Register `meteorite` as a first-class member of `ENTITY_TYPES` and wire the shared dispatch state/claim/sort helpers to `METEORITE_STATES`, then flip ingress + BOT_BLOCKED notify seed SQL to store `entity_type='meteorite'` instead of NULL. Leaves count/due/Available runtime and ledger/live-row backfill to siblings AST-1622 / AST-1623.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Append `meteorite` to `ENTITY_TYPES`; map it in `dispatch_entity_state_registry`, `dispatch_claim_states`, and `_dispatch_sort_by_for`; set ingress + bot-blocked `SEED_CONFIG` SQL `entity_type` to `'meteorite'` | utils |
| `docs/ASTRAL_CODE_RULES.md` | ENTITY_TYPES bullet and §2.4 claim-queue member list include `meteorite` | docs |

## Stage 1: ENTITY_TYPES + dispatch registries + sort default

**Done when:** `from src.utils.config import ENTITY_TYPES, METEORITE_STATES, dispatch_entity_state_registry, dispatch_claim_states, _dispatch_sort_by_for` works; `'meteorite' in ENTITY_TYPES`; `set(dispatch_entity_state_registry("meteorite")) == set(METEORITE_STATES)`; `_dispatch_sort_by_for("meteorite", "NEW") == "updated_at"`; `dispatch_claim_states("NEW", "meteorite")` returns a non-empty list whose first element is `"NEW"` (companion `*_RETRY` only if present in `METEORITE_STATES` — today none are).

1. In `src/utils/config.py`, change `ENTITY_TYPES = ["candidate", "company", "job"]` to `ENTITY_TYPES = ["candidate", "company", "job", "meteorite"]`. Keep the existing header comment above the list; do not invent a second entity-type constant elsewhere.
2. In `dispatch_entity_state_registry`, add `"meteorite": METEORITE_STATES` to the local `registries` dict alongside `job` / `company` / `candidate`. Keep the existing `KeyError` for unknown types.
3. In `dispatch_claim_states`, extend the registry resolution so `entity_type == "meteorite"` selects `METEORITE_STATES` (same nested-if / ternary shape already used for job/company/candidate). Leave the retry / companion-`*_RETRY` logic unchanged — it already operates on whichever registry was selected. Do not call `dispatch_entity_state_registry` from this function unless the surrounding code already does (it does not today).
4. In `_dispatch_sort_by_for`, before the final `raise KeyError(f"dispatch sort_by: unknown entity_type …")`, add:

   ```python
   if entity_type == "meteorite":
       return "updated_at"
   ```

   Do not validate `trigger_state` against `METEORITE_STATES` here (job validates; company/candidate do not require a successful registry hit for every trigger before returning a default — meteorite matches the ingress seed default).

⚠️ **Decision:** Meteorite sort default is the literal `"updated_at"`, matching the existing `SEED_CONFIG` ingress / bot-blocked `sort_by` values and the parent technical scope. Do not invent a `batch_criteria.sort_by` block on `METEORITE_STATES` in this ticket.

## Stage 2: SEED_CONFIG entity_type literals for ingress + bot-blocked notify

**Done when:** `grep` of `SEED_CONFIG["dispatch_task-meteorite-ingress"]` and `SEED_CONFIG["dispatch_task-meteorite-bot-blocked-notify"]` string values shows `'meteorite'` in the `entity_type` column position for `stage_meteorite` / `scrape_meteorite` / `land_meteorite` / `meteorite_bot_blocked_notify`, and no longer shows `, NULL, 'NEW'` / `, NULL, 'SCRAPE_LINK'` / `, NULL, 'READY'` / `, NULL, 'BOT_BLOCKED'` in those four INSERT SELECT lists. `dispatch_task-meteorite-retention` still inserts `entity_type` as NULL with `trigger_state` NULL. Job-track `dispatch_task-meteorite` seeds remain `entity_type='job'`.

1. In `SEED_CONFIG["dispatch_task-meteorite-ingress"]`, in each of the three INSERT SELECT clauses, replace the third SELECT value `NULL` (the `entity_type` column after `task_key`) with the string literal `'meteorite'`:
   - `stage_meteorite`: `) SELECT NULL, 'stage_meteorite', 'meteorite', 'NEW', 'updated_at', …`
   - `scrape_meteorite`: `) SELECT NULL, 'scrape_meteorite', 'meteorite', 'SCRAPE_LINK', 'updated_at', …`
   - `land_meteorite`: `) SELECT NULL, 'land_meteorite', 'meteorite', 'READY', 'updated_at', …`
2. In `SEED_CONFIG["dispatch_task-meteorite-bot-blocked-notify"]`, same replacement: `) SELECT NULL, 'meteorite_bot_blocked_notify', 'meteorite', 'BOT_BLOCKED', 'updated_at', …`
3. Leave `SEED_CONFIG["dispatch_task-meteorite-retention"]` unchanged (`entity_type` NULL, `trigger_state` NULL). Leave `SEED_CONFIG["dispatch_task-meteorite"]` (job-lifecycle qualify/evaluate/grade seeds) unchanged (`entity_type` `'job'`). Do not change `auto_mode` (stays `0` / false per `astral.dispatch.seed-auto-false`).

⚠️ **Decision:** Seed SQL only — no live-row `UPDATE` of existing NULL `dispatch_task.entity_type` values. That backfill is AST-1623. `INSERT … WHERE NOT EXISTS` will not rewrite rows already present with NULL.

## Stage 3: Code Rules ENTITY_TYPES + §2.4 claim-queue wording

**Done when:** `docs/ASTRAL_CODE_RULES.md` §2.1 ENTITY_TYPES bullet lists `meteorite` with the other members, and the §2.4 sentence that names claim-queue members includes `meteorite`.

1. In `docs/ASTRAL_CODE_RULES.md` §2.1 Config blocks, update the **ENTITY_TYPES** bullet from `(candidate, company, job)` to `(candidate, company, job, meteorite)`. Keep the rest of that bullet's wording (agent_data / dispatch_ledger / retired agent_responses notes) intact.
2. In §2.4 Batch Processing Pattern, update the claim-queue member parenthetical from ``(`candidate`, `company`, `job`)`` to ``(`candidate`, `company`, `job`, `meteorite`)`` in the sentence that begins "Every `ENTITY_TYPES` member used as a dispatch claim queue". Do not rewrite the rest of §2.4 (claim → process → release narrative, batch_id format, dispatcher pseudocode).

## Out of scope (siblings — do not touch)

- `src/data/database.py` `count_eligible_for_dispatch_task` / `get_due_tasks` (AST-1622)
- `src/ui/api/api_admin.py` state_options / Available / validation (AST-1623)
- `src/core/dispatcher.py` ledger `entity_type='meteorite'` and live-row NULL→meteorite UPDATE (AST-1623)
- Rewriting custom meteorite runners into consult / `_run_unified`
- Forcing retention or `meteorite_email` mailbox onto ENTITY_TYPES claim semantics

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1621
**Overall:** APPROVED
**Publish ref:** `sub/AST-1620/AST-1621-register-meteorite-entity-types` @ `1bcee4e9413712d46ad3231186b94303ff6d0da6`

## Traceability
AC1→Stage 1; AC2→Stage 1; AC3→Stage 2; parent AC3–5,7–9 N/A (AST-1622/AST-1623). Stages 1–3→child Scope + parent Purpose (meteorite first-class in ENTITY_TYPES / dispatch registries / ingress seeds).

## Findings
(none — no fix-now or discuss)

context_tokens≈38000

```
AST-1621 plan approved.
```

---

**Gate summary:** Plan Ready, assignee Joan — identity OK. Child-only scope respected; siblings and parent remainder out of band.

**R5/R6:** Plan matches the child slice: `ENTITY_TYPES` append, three dispatch helpers wired to `METEORITE_STATES`, ingress/bot-blocked `SEED_CONFIG` literals, Code Rules §2.1/§2.4 — with explicit exclusions for count/due, admin, ledger, and live-row backfill. Stages align with child AC 1–3; parent AC 3–5 and 7–9 correctly deferred. Layer placement (`utils` + `docs`) is clean; cited patterns (`pattern.config.config-block`, `pattern.state.entity-state-transitions`) match the solution shape; retention/mailbox boundaries preserved; `auto_mode` untouched per `astral.dispatch.seed-auto-false`.

**Statute pass (in-session):** Universal orchestration statutes conform (plan review only). Scoped statutes considered for `src/utils/config.py` + `docs/ASTRAL_CODE_RULES.md` (`config-source-of-truth`, `no-hardcoded-sets`, `seed-auto-false`, `in-scope-only`, layer/import standards, etc.) — all conform; batch/UI/data statutes excluded by path/layer. No fix-now findings.

**Intermediate epic note (acceptable):** After this child lands, `ENTITY_TYPES` and registries accept `meteorite` while `state_options`/Available/ledger/backfill remain sibling work — documented in plan boundaries and stage-2 seed-only decision; not a blocker for AST-1621.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1620/AST-1621-register-meteorite-entity-types`
**Tip:** `2f34fe55`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `fb265adf` | ENTITY_TYPES + registry / claim_states / sort_by for meteorite |
| 2 | `1172951c` | SEED_CONFIG ingress + bot-blocked `entity_type='meteorite'` |
| 3 | `2f34fe55` | Code Rules ENTITY_TYPES + §2.4 claim-queue wording |

## Radia review

# Radia review — AST-1621

**Publish ref:** `origin/sub/AST-1620/AST-1621-register-meteorite-entity-types` @ `d6e5951a`  
**Baseline:** `origin/dev`  
**Diff:** 5 files, +202 / −8 (utils config + Code Rules + Betty tests/bible + issue doc)

---

```
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1621
**Publish ref:** d6e5951a
**Overall:** CLEAN
```

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no `src/core/**` diff |
| astral.agent.do-task-delegation | scoped | not-applicable | no agent/dispatcher diff |
| astral.agent.grade-vector-validation | scoped | not-applicable | no agent/dispatcher diff |
| astral.batch.batch-id-first | scoped | not-applicable | no batch/dispatcher paths changed |
| astral.batch.batch-id-format | scoped | not-applicable | no batch/dispatcher paths changed |
| astral.batch.claim-process-release | scoped | not-applicable | no `dispatcher.py` / claim-loop diff |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no batch/agent_data diff |
| astral.config.config-source-of-truth | scoped | conforms | `ENTITY_TYPES` + dispatch helpers + seeds stay in `config.py` |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets or env fallbacks introduced |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug/artifact paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no debug paths |
| astral.dispatch.seed-auto-false | scoped | conforms | ingress/notify/retention seeds keep `auto_mode` 0; retention boundary tested |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no core/dispatcher diff |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single issue doc under `docs/features/dispatcher/` |
| astral.git.betty-no-src-or-features | scoped | conforms | test/bible changes via Betty merge-tests SHA |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer commits limited to `src/` + docs; tests on `origin/tests` |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | utils/docs only |
| astral.layers.import-direction | scoped | conforms | no new cross-layer imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts diff |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | no UI diff |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult/render paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no API endpoint diff |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no agent-table seed diff |
| astral.seed.archie-catalog-wins | scoped | conforms | `SEED_CONFIG` literals only; no boot reconcile |
| astral.seed.boot-only-not-hot-path | scoped | conforms | seed SQL unchanged except `entity_type` column literals |
| astral.seed.define-approved | scoped | not-applicable | no define/seed approval surface |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no operator-row reconcile |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage-join seed paths |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no `src/data/**` diff |
| astral.standards.database-header-inventory | scoped | not-applicable | no database/migration diff |
| astral.standards.debug-contract-gated | scoped | not-applicable | no debug emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | minimal registry wiring; matches sibling entity pattern |
| astral.standards.in-scope-only | scoped | conforms | no AST-1622/1623 surfaces (`database.py`, `dispatcher.py`, `api_admin.py`) |
| astral.standards.logging-via-utils | scoped | conforms | no new logging |
| astral.standards.names-not-ticket-ids | scoped | conforms | domain names only (`meteorite`, state keys) |
| astral.standards.no-cross-contamination | scoped | conforms | meteorite registry isolated from `JOB_STATES` lifecycle keys |
| astral.standards.no-hardcoded-sets | scoped | conforms | uses `METEORITE_STATES` / `ENTITY_TYPES`; no inline state sets |
| astral.standards.public-then-helpers | scoped | conforms | public dispatch helpers extended; sort helper pre-existing private |
| astral.standards.utils-data-late-import-only | scoped | conforms | no utils→data imports added |
| astral.state.core-decides-transitions | scoped | not-applicable | no core/tracker diff |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job transition logic diff |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no runner/dispatcher diff |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend diff |
| astral.ui.naming-conventions | scoped | not-applicable | no UI diff |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no deploy/config worker diff |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1621)` at tip |
| orch.git.commit-vocabulary | universal | conforms | `code` / `docs` / `test` / `merge-tests` prefixes |
| orch.git.flow-direction-inviolable | universal | conforms | `sub/AST-1620/AST-1621-*` vs `origin/dev` |
| orch.git.ftr-sub-topology | universal | conforms | child on `sub/<parent>/<child>` |
| orch.git.merge-on-checkout | universal | conforms | `sync(dev)` merges present in history |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no evidence of forbidden git ops |
| orch.git.no-dev-agent-branches | universal | conforms | publish ref is `sub/`, not agent branch |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1620 worktree path |
| orch.git.three-permanent-branches | universal | conforms | diff vs `origin/dev` only |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | product choices documented in plan decisions |
| orch.pipeline.plan-is-bible | universal | conforms | implementation matches staged plan |
| orch.pipeline.project-scoped-queues | universal | conforms | child scope respected |
| orch.pipeline.status-gates-skill-entry | universal | conforms | reviewed at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | Joan APPROVED; no new statutes |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty manifest + component tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Ada (engineer) |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | engineer still assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path commits observed |

**Active set:** 65 scored in-session (46 scoped + 19 universal).  
**Straggler (C4):** Joan verdict attached; no explicit Excluded statute list — no straggler rows.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.config.config-block | conforms | `ENTITY_TYPES` append + dispatch registry maps in `config.py`; Code Rules §2.1 updated |
| pattern.state.entity-state-transitions | conforms | `METEORITE_STATES` wired into dispatch registries; no transition logic in data/UI |

## Plan adherence

- **Stage 1:** `ENTITY_TYPES` includes `meteorite`; `dispatch_entity_state_registry`, `dispatch_claim_states`, `_dispatch_sort_by_for` wired to `METEORITE_STATES` with `updated_at` sort default.
- **Stage 2:** Ingress (`stage_meteorite`, `scrape_meteorite`, `land_meteorite`) and `meteorite_bot_blocked_notify` seeds use `'meteorite'`; retention stays `NULL`/`NULL`; job-track `dispatch_task-meteorite` seeds unchanged (`entity_type='job'`).
- **Stage 3:** Code Rules §2.1 ENTITY_TYPES bullet and §2.4 claim-queue parenthetical include `meteorite`.
- **Boundaries:** No `database.py`, `dispatcher.py`, `api_admin.py`, or live-row backfill — correctly deferred to AST-1622/AST-1623.
- **Estimate (2):** Footprint matches (single utils module + docs + focused component tests).

## C6 judgment aids (§5a–§5g)

| Lens | Result |
|------|--------|
| Imports (B1) | OK — no new imports |
| Layer compliance (B2) | OK — utils-only product change |
| Silent failure (D2) | N/A |
| Fallbacks (D3) | N/A |
| Logging (E1) | OK — no new emission |
| Config/state in UI (G1) | N/A — no frontend diff |
| Batch/transitions (H*) | N/A — no dispatcher/tracker diff |
| Debug contract (§5f) | N/A |
| External cleanliness (§5g) | N/A |

## Test / bible alignment

Betty manifest (`TestAst1621MeteoriteEntityTypeRegistry` + AST-1560/1561/1562 regression) matches plan ACs:

- Registry equality with `METEORITE_STATES` (including `SCRAPE_LINK` vs `METEORITE_NEW` guard).
- Claim states for `NEW`, `SCRAPE_LINK`, `BOT_BLOCKED`.
- Seed substring asserts for ingress/notify + negative NULL-shape guards.
- Retention NULL boundary.

Docs-acceptance (Code Rules grep) is manifest line 2 — not pytest — consistent with plan Stage 3.

## Findings

### fix-now
(none)

### discuss
(none)

### advisory

1. **Intermediate epic gap (expected):** `dispatch_task_state_options` still returns only `job` / `company` / `candidate` keys — no `meteorite` list yet (`api_admin.py` ~1049–1053). Admin POST validation will accept `entity_type='meteorite'` via `ENTITY_TYPES` + `dispatch_entity_state_registry`, but the UI dropdown will not offer meteorite states until AST-1623. Plan and Joan intermediate-epic note cover this; flag for UAT awareness only.

2. **`_dispatch_entity_type_for_task_key` unchanged:** Ingress keys (`stage_meteorite`, etc.) still won't auto-default `entity_type='meteorite'` through `dispatch_task_admin_defaults` — operators need explicit `entity_type` or sibling work. Out of AST-1621 scope per plan.

3. **Duplicate registry resolution in `dispatch_claim_states`:** Meteorite follows the existing nested-if pattern rather than calling `dispatch_entity_state_registry` — plan-mandated; pre-existing DRY debt, not introduced here.

## What's solid

- Surgical config change: four dispatch touchpoints + four seed literals, no scope creep.
- Tests explicitly guard JOB_STATES vs `METEORITE_STATES` key confusion (`METEORITE_NEW` not in meteorite registry).
- `auto_mode` and retention NULL semantics preserved with a dedicated boundary test.
- Code Rules kept in sync with runtime `ENTITY_TYPES`.

## Frame diff

Post-Joan (`1bcee4e9`) → tip (`d6e5951a`):

| Area | Change |
|------|--------|
| `src/utils/config.py` | `ENTITY_TYPES` + `dispatch_entity_state_registry` / `dispatch_claim_states` / `_dispatch_sort_by_for` + ingress/notify seed `entity_type` literals |
| `docs/ASTRAL_CODE_RULES.md` | §2.1 ENTITY_TYPES + §2.4 claim-queue wording |
| `tests/component/utils/test_config.py` | `TestAst1621MeteoriteEntityTypeRegistry` |
| `docs/test-bible/utils/config.md` | Betty manifest block |
| `docs/features/dispatcher/ast-1621-*.md` | Plan + Joan validate + build stub |

All deltas are expected post-plan execution; no unplanned product surface.

## Notes

- Joan plan-rubric verdict attached (APPROVED @ `1bcee4e9`); no excluded-statute stragglers.
- Three-dot diff vs `origin/dev` is the correct review surface (5 files); branch history includes `sync(dev)` merges — immaterial to verdict.
- C7 complete: full artifact + frame diff present; recommend **Review Posted**.

context_tokens≈42000

---

```
[code-rubric] PROCEED (Commit: d6e5951a) meteorite registry clean
```
