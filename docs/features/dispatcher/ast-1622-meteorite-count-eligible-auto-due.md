# AST-1622 — Meteorite count_eligible and AUTO-due without candidate_id

- **Linear:** https://linear.app/astralcareermatch/issue/AST-1622
- **Parent:** AST-1620 — Treat meteorite as a first-class dispatch entity_type
- **Publish ref:** `sub/AST-1620/AST-1622-meteorite-count-eligible-auto-due`

Extend `count_eligible_for_dispatch_task` and `get_due_tasks` so a dispatch row with `entity_type='meteorite'` and a `trigger_state` counts and AUTO-dues against the global unclaimed meteorite claim pool — including when `candidate_id` is NULL. Depends on AST-1621 (`meteorite` already in `ENTITY_TYPES` / `dispatch_claim_states`). Does not touch admin Available, state_options, ledger, or live-row backfill (AST-1623).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Add `count_meteorites_unclaimed_in_states`; meteorite branch + relaxed `candidate_id` gate in `count_eligible_for_dispatch_task`; include NULL-`candidate_id` meteorite rows in `get_due_tasks`; header inventory note for the new helper | data |

## Stage 1: Unclaimed-meteorite count helper

**Done when:** `from src.data.database import count_meteorites_unclaimed_in_states` works; calling it with `["NEW"]` returns the same integer as `SELECT COUNT(*) FROM meteorite WHERE state = 'NEW' AND (batch_id IS NULL OR batch_id = '')` on that DB; empty `states` raises `ValueError` via `_state_in_sql` (same as other unclaimed-in-states helpers). Header inventory mentions the helper on the `meteorite` bullet.

1. In `src/data/database.py`, immediately after `clear_meteorite_batch` and before `insert_meteorite_rows`, add:

   ```python
   def count_meteorites_unclaimed_in_states(states: List[str]) -> int:
       """Count unclaimed meteorite rows in the given state set (global pool).

       Unclaimed = batch_id IS NULL OR batch_id = '' — same predicate as claim_meteorite_batch.
       """
       state_sql, state_params = _state_in_sql(states)

       def _with_conn() -> int:
           conn = _get_connection()
           try:
               _ensure_meteorite_schema(conn)
               row = conn.execute(
                   f"""SELECT COUNT(*) FROM meteorite
                      WHERE {state_sql} AND (batch_id IS NULL OR batch_id = '')""",
                   tuple(state_params),
               ).fetchone()
               return int(row[0])
           finally:
               conn.close()

       return _run_with_retry(_with_conn)
   ```

2. In the module docstring **Tables used (inventory)** `meteorite` bullet, append a short clause that eligibility counting uses `count_meteorites_unclaimed_in_states` (keep existing column / claim wording intact). Do not add a new table row.

⚠️ **Decision:** Place the helper with the meteorite claim/get/clear cluster (not next to `count_candidates_unclaimed_in_states`) so meteorite batch APIs stay co-located; `count_eligible_for_dispatch_task` will call it the same way it calls the candidate helper.

## Stage 2: count_eligible + get_due_tasks meteorite path

**Done when:** With ≥1 unclaimed meteorite row in `NEW` and a dict `{"entity_type": "meteorite", "trigger_state": "NEW", "candidate_id": None, "task_key": "stage_meteorite", "min_count": 1}`, `count_eligible_for_dispatch_task(task)` returns ≥1. The same task with `auto_mode`-style fields is included by `get_due_tasks` when that row is `auto_mode=1` in DB (or, if verifying via the in-memory gate alone: the `if not et or not ts or not cid` skip no longer drops `entity_type='meteorite'` with NULL `candidate_id`). Job/company/candidate paths still return 0 when `candidate_id` is missing. `count_entities_in_state` is never called for `entity_type='meteorite'`.

1. In `count_eligible_for_dispatch_task`, replace the early gate:

   ```python
   if not entity_type or not state or not candidate_id:
       return 0
   ```

   with:

   ```python
   if not entity_type or not state:
       return 0
   if entity_type != "meteorite" and not candidate_id:
       return 0
   ```

   Keep the subsequent `if entity_type not in ENTITY_TYPES: return 0` unchanged (AST-1621 already put `meteorite` in `ENTITY_TYPES`).

2. Still inside `count_eligible_for_dispatch_task`, after `claim_states` is resolved (including the existing job chain override) and after the `if not claim_states: return 0` check, **before** the `task_key` / score-floor / `candidate` branch, add:

   ```python
   if entity_type == "meteorite":
       return count_meteorites_unclaimed_in_states(claim_states)
   ```

   Do not apply score-floor, company WATCH staleness, or `candidate_id` filtering on this branch. Ignore `task["candidate_id"]` when counting (global pool — matches `claim_meteorite_batch`).

3. Update the `count_eligible_for_dispatch_task` docstring to state that `entity_type='meteorite'` counts the global unclaimed meteorite pool via `count_meteorites_unclaimed_in_states` and does not require `candidate_id`; keep the existing `meteorite_email` / null-entity notes.

4. In `get_due_tasks`, replace:

   ```python
   if not et or not ts or not cid:
       continue
   ```

   with:

   ```python
   if not et or not ts:
       continue
   if not cid and et != "meteorite":
       continue
   ```

   Leave the `avail = count_eligible_for_dispatch_task(task)` and `min_count` threshold unchanged.

5. Update the `get_due_tasks` docstring so it no longer implies every due row needs a non-null `candidate_id`; note that meteorite AUTO rows may have NULL `candidate_id` and still due when eligible count ≥ `min_count`. Keep the AST-1135 `meteorite_email` core-merge note.

⚠️ **Decision:** Meteorite eligibility is always the global unclaimed pool, even if a future admin row sets a non-null `candidate_id`. `claim_meteorite_batch` does not filter by `candidate_id`; count must match claim. Scoping meteorite Avail by candidate would be a new product rule — out of scope here.

⚠️ **Decision:** No score-floor / `latest_score` path for meteorite. Staging rows are not in `PASSED_SCORE_GATED_STATES`; falling through to `count_entities_in_state` would `ValueError` on unknown entity_type — the explicit meteorite branch prevents that.

## Out of scope (siblings — do not touch)

- `src/utils/config.py` / `docs/ASTRAL_CODE_RULES.md` ENTITY_TYPES registration (AST-1621 — already on `origin/ftr/AST-1620-treat-meteorite-first-class-entity-type`)
- `src/ui/api/api_admin.py` Available short-circuit, `state_options`, create/update validation (AST-1623)
- `src/core/dispatcher.py` ledger `entity_type='meteorite'` and live-row NULL→meteorite UPDATE (AST-1623)
- Rewriting custom meteorite runners into consult / `_run_unified`
- Forcing retention or `meteorite_email` mailbox onto ENTITY_TYPES claim semantics

## Estimate

Confirm Chuckles estimate: 3 — agree

## Traceability

AC4 (parent) / child AC → Stage 2 (count + due); Stage 1 → shared helper named in Scope. Boundaries → Out of scope list.

## Joan validate

```
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1622
**Overall:** APPROVED
**Publish ref:** `sub/AST-1620/AST-1622-meteorite-count-eligible-auto-due` @ `06d21b2b362ff53e96ee89b6f8b46f8dd8e1efd2`

## Traceability
AC4→Stage 2 (relaxed candidate_id gate + meteorite branch in `count_eligible_for_dispatch_task` + `get_due_tasks`); Stage 1→shared `count_meteorites_unclaimed_in_states` helper named in Scope. Parent AC1–3,5–9 N/A (AST-1621 / AST-1623). Stages→parent Purpose (global meteorite pool count/AUTO-due without `candidate_id` gate).

## Findings
- **acceptable** — Linear assignee is Hedy, not Joan; Chuckles preflight only — does not affect plan merit.
- **acceptable** — `get_due_tasks` does not add row-level `dispatch_task_freq_allows` for meteorite; matches existing claim-queue due shape (freq handled entity-level during claim / company WATCH staleness in count path, not a new gap introduced here).

context_tokens≈52000
```

## Review (build stub)

**Publish ref:** `origin/sub/AST-1620/AST-1622-meteorite-count-eligible-auto-due`
**Tip:** `a8a7e0b2`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `2b63c4da` | `count_meteorites_unclaimed_in_states` + header inventory |
| 2 | `a8a7e0b2` | meteorite gate/branch in `count_eligible_for_dispatch_task` + `get_due_tasks` |

## Radia review

# Radia review — AST-1622

**Publish ref:** `origin/sub/AST-1620/AST-1622-meteorite-count-eligible-auto-due` @ `3f86f411`  
**Baseline:** `origin/dev`  
**Diff:** 9 files, +683 / −11 (includes AST-1621 sibling rollup on branch)

---

```
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1622
**Publish ref:** 3f86f411
**Overall:** CLEAN
```

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no `src/core/**` diff |
| astral.agent.do-task-delegation | scoped | not-applicable | no agent/dispatcher diff |
| astral.agent.grade-vector-validation | scoped | not-applicable | no agent/dispatcher diff |
| astral.batch.batch-id-first | scoped | not-applicable | no batch-id / dispatcher claim-loop diff |
| astral.batch.batch-id-format | scoped | not-applicable | no batch-id format diff |
| astral.batch.claim-process-release | scoped | conforms | count predicate matches `claim_meteorite_batch` unclaimed filter; no claim-loop change |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no agent_data diff |
| astral.config.config-source-of-truth | scoped | conforms | `dispatch_claim_states` / `ENTITY_TYPES` read from config (sibling AST-1621 on branch) |
| astral.config.secrets-and-env-specific-from-environ | scoped | conforms | no secrets introduced |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no debug paths |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no seed/config diff in AST-1622 commits |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no dispatcher diff |
| astral.docs.features-single-file-per-ticket | scoped | conforms | AST-1622 issue doc present |
| astral.git.betty-no-src-or-features | scoped | conforms | tests/bible via Betty merge-tests |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer `code(AST-1622)` limited to `database.py` |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | data/utils only |
| astral.layers.import-direction | scoped | conforms | data→utils imports pre-existing; no new cross-layer bends |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no scripts diff |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | no UI diff |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult/render diff |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no API endpoint diff |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed diff |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no seed/catalog diff |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no seed diff |
| astral.seed.define-approved | scoped | not-applicable | no define surface |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no operator-row reconcile |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage-join paths |
| astral.standards.data-raises-caller-logs | scoped | conforms | new helper raises via `_state_in_sql`; no data-layer logging |
| astral.standards.database-header-inventory | scoped | conforms | `meteorite` bullet documents `count_meteorites_unclaimed_in_states` |
| astral.standards.debug-contract-gated | scoped | not-applicable | no debug emission |
| astral.standards.dry-and-focused-functions | scoped | conforms | focused helper + two gate relaxations |
| astral.standards.in-scope-only | scoped | conforms | AST-1622 commits touch `database.py` only; no admin/dispatcher/ledger |
| astral.standards.logging-via-utils | scoped | conforms | no new logging |
| astral.standards.names-not-ticket-ids | scoped | conforms | domain names only |
| astral.standards.no-cross-contamination | scoped | conforms | meteorite branch isolated before score-floor / `count_entities_in_state` |
| astral.standards.no-hardcoded-sets | scoped | conforms | uses `_state_in_sql` + `dispatch_claim_states`; no inline state sets |
| astral.standards.public-then-helpers | scoped | conforms | public count helper; existing private gate helpers unchanged |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no utils→data late imports |
| astral.state.core-decides-transitions | scoped | not-applicable | no core/tracker diff |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no transition logic diff |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no runner diff |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend diff |
| astral.ui.naming-conventions | scoped | not-applicable | no UI diff |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no deploy diff |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1622)` at tip |
| orch.git.commit-vocabulary | universal | conforms | `code` / `docs` / `test` / `merge-tests` |
| orch.git.flow-direction-inviolable | universal | conforms | `sub/AST-1620/AST-1622-*` vs `origin/dev` |
| orch.git.ftr-sub-topology | universal | conforms | child on `sub/<parent>/<child>` |
| orch.git.merge-on-checkout | universal | conforms | `sync(ftr)` / `sync(dev)` in history |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no forbidden git ops observed |
| orch.git.no-dev-agent-branches | universal | conforms | publish ref is `sub/` |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1620 worktree |
| orch.git.three-permanent-branches | universal | conforms | diff vs `origin/dev` |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | global-pool / NULL-cid decisions documented in plan |
| orch.pipeline.plan-is-bible | universal | conforms | stages 1–2 match plan |
| orch.pipeline.project-scoped-queues | universal | conforms | child scope respected |
| orch.pipeline.status-gates-skill-entry | universal | conforms | reviewed at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | Joan APPROVED |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty manifest + component tests |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee Hedy (engineer) |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | engineer still assignee |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path commits observed |

**Active set:** 65 scored in-session.  
**Straggler (C4):** Joan verdict attached; no Excluded statute list — no stragglers.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | plan has no "Patterns to reuse" block; data-layer count helper follows existing unclaimed-in-states peer shape |

## Plan adherence

- **Stage 1:** `count_meteorites_unclaimed_in_states` added after `clear_meteorite_batch`; uses `_state_in_sql` + `(batch_id IS NULL OR batch_id = '')` matching `claim_meteorite_batch`; header inventory updated.
- **Stage 2:** `count_eligible_for_dispatch_task` relaxes `candidate_id` gate for `meteorite` only; early meteorite branch calls helper before score-floor / `count_entities_in_state`; `get_due_tasks` allows NULL `candidate_id` when `entity_type='meteorite'`; docstrings updated.
- **Boundaries:** No `api_admin.py`, `dispatcher.py`, ledger/backfill, or config registration in AST-1622 commits.
- **Estimate (3):** Footprint matches (one helper + two function edits + focused component tests).

## C6 judgment aids (§5a–§5g)

| Lens | Result |
|------|--------|
| Imports (B1) | OK — no new imports in diff |
| Layer compliance (B2) | OK — data layer only for AST-1622 product code |
| Silent failure (D2) | OK — no swallowed exceptions |
| Fallbacks (D3) | OK — explicit gates; meteorite branch before fallthrough |
| Logging (E1) | OK — no new emission in data layer |
| Database / raw SQL (plan note) | OK — `_state_in_sql` parameterized; column/bind alignment matches peer helpers |
| Batch/transitions (H*) | N/A — no dispatcher/tracker diff |
| Debug contract (§5f) | N/A |
| External cleanliness (§5g) | N/A |

## Test / bible alignment

`TestAst1622MeteoriteCountEligibleDue` covers:

- Helper count + claim decrement + state filter + empty-states `ValueError`.
- `count_eligible_for_dispatch_task` with NULL `candidate_id` and ignored non-null `candidate_id` on task dict (global pool).
- Job path still returns 0 without `candidate_id`.
- `get_due_tasks` includes AUTO `stage_meteorite` row with NULL `candidate_id` when eligible ≥ `min_count`.

Betty manifest in `docs/test-bible/data/database/dispatch_tasks.md` matches.

## Findings

### fix-now
(none)

### discuss
(none)

### advisory

1. **Three-dot diff includes AST-1621 sibling rollup** (`config.py`, Code Rules, `test_config.py`, ast-1621 issue doc). AST-1622 `code()` commits touch `database.py` only — correct dependency ordering on epic branch; UAT should treat 1621+1622 as coupled until ftr merge.

2. **Admin Available still gated on `candidate_id`** (`api_admin.py` ~943: `if et and ts and cid else 0`). AUTO-due path works via `get_due_tasks` → dispatcher; admin UI Avail for NULL-candidate meteorite rows remains AST-1623.

3. **`get_due_tasks` does not call `dispatch_task_freq_allows`** — Joan closed this at plan validate as matching existing claim-queue due shape; freq for ingress seeds is entity-level during claim. No new gap introduced.

4. **Dispatcher ledger still writes `entity_type=None` for meteorite ingress** (pre-existing AST-1560 path) — AST-1623 ledger backfill; not introduced here.

5. **Cosmetic:** double blank line before `count_meteorites_unclaimed_in_states` (~line 3676) — style only.

## What's solid

- Unclaimed predicate aligned with `claim_meteorite_batch` — count and claim will stay consistent.
- Meteorite branch placed before score-floor / `count_entities_in_state` — prevents `ValueError` on unknown entity_type.
- Tests explicitly assert global-pool semantics (task `candidate_id` ignored) and job gate preservation.
- Header inventory updated per `astral.standards.database-header-inventory`.

## Frame diff

Post-Joan (`06d21b2b`) → tip (`3f86f411`):

| Area | Change | Ticket |
|------|--------|--------|
| `src/data/database.py` | `count_meteorites_unclaimed_in_states` + `count_eligible` / `get_due_tasks` meteorite gates | **AST-1622** |
| `tests/.../test_dispatch_tasks.py` | `TestAst1622MeteoriteCountEligibleDue` | **AST-1622** |
| `docs/test-bible/data/database/dispatch_tasks.md` | Betty manifest | **AST-1622** |
| `docs/features/dispatcher/ast-1622-*.md` | Plan + Joan + build stub | **AST-1622** |
| `src/utils/config.py`, Code Rules, `test_config.py`, ast-1621 doc | ENTITY_TYPES / registry / seeds (sibling rollup) | **AST-1621** |

AST-1622 product surface is database-only; sibling files are expected epic-branch carry.

## Notes

- Joan plan-rubric APPROVED @ `06d21b2b`; acceptable findings on assignee and `dispatch_task_freq_allows` — no re-litigation.
- End-to-end: dispatcher already runs meteorite ingress with NULL `candidate_id` (`ledger_cid = None`); this ticket unblocks AUTO scheduling via `get_due_tasks`.
- C7 complete; recommend **Review Posted**.

context_tokens≈45000
