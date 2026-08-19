<!-- linear-archive: AST-1258 archived 2026-08-17 -->

## Linear archive (AST-1258)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1258/candidate-batch-lock-schema-and-pool-claim-apis-candidate-table-does  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1257 — candidate table does not have batch_id  
**Blocked by / blocks / related:** parent: AST-1257; blocks: AST-1259

### Description

## What this implements

Add candidate `batch_id` / `batch_created_at`, inventory/header honesty, and data-layer claim / get / clear with **job/company pool parity** (claim up to limit unclaimed candidates in claim states; batch_id-first) plus eligibility/count over the unclaimed pool. Does not wire dispatcher.

## Acceptance criteria

- [X] 1. Candidate schema (ensure + inventory) exposes `batch_id` and `batch_created_at`; unclaimed rows have null/empty `batch_id`.
- [X] 2. Candidate claim → get → clear can lock multiple unclaimed candidates in claimable states in one `batch_id` (pool), release them all on clear, and refuse a second concurrent claim on already-locked rows.
- [X] 3. Eligibility/count for candidate stage claim tasks reports the unclaimed pool size (0 when none available or all locked / not claimable).

## Boundaries

Does not wire dispatcher or core get_new wrappers. Does not own statute/pattern/docs text (sibling). Does not change job/company claim SQL beyond shared helpers if reused.

## In scope

- [X] `pattern.batch.entity-claim-process-release` — data-layer claim → get → clear peers of job/company (pool, not single-ctx)
- [X] `astral.batch.claim-process-release` — candidate rows get batch locking + pool claim APIs
- [X] `astral.batch.batch-id-first` — `claim_candidate_batch(batch_id, …)` parameter order
- [X] `astral.batch.batch-id-format` — caller-owned golden ticket; no new mint rules in data layer
- [X] `astral.standards.database-header-inventory` — candidate inventory names `batch_id` / `batch_created_at`
- [X] `astral.standards.data-raises-caller-logs` — new data APIs raise; no logging
- [X] `astral.standards.dry-and-focused-functions` — reuse `_state_in_sql` / `_run_with_retry` / `_utc_now` / `_parse_candidate_row`
- [X] `astral.standards.public-then-helpers` — public claim trio grouped in candidate section
- [X] `astral.standards.in-scope-only` — only `src/data/database.py` product surface
- [X] `astral.layers.import-direction` — data keeps existing utils config imports only
- [X] `astral.state.core-decides-transitions` — claim/clear touch lock columns only; never write `candidate.state` (Radia C4: mechanical layer/path match → conforms; plan had excluded)

## Considered but excluded

- [X] `astral.standards.debug-contract-gated` — dispatch/core debug path is AST-1259 (`src/core/dispatcher.py`)
- [X] `astral.layers.core-vs-external-bright-line` — no core/external work this ticket
- [X] `orch.roles.archie-approves-statutes` — statute/pattern/`CANDIDATE_DATA_MODEL` amend is AST-1260
- [X] Dispatcher `finally` clear / `get_new_candidate_batch` — AST-1259

## Notes for planning

Pool parity with job/company — not a single-ctx / one-row-only gate. Overturns AST-972 no-batch carve-out for locking. Stage Avail (non-`inflow_discovery`) counts the cross-candidate unclaimed pool; inflow Avail unchanged. Must not land on `dev` ahead of AST-1259.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

**Publish ref:** `sub/AST-1257/AST-1258-candidate-batch-lock-schema-and-pool-claim-apis`

### Comments

#### radia — 2026-08-07T18:39:57.818Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1258
**Publish ref:** `sub/AST-1257/AST-1258-candidate-batch-lock-schema-and-pool-claim-apis` @ `6f684aff`
**Overall:** DISCUSS

Full active-set sweep run in-session (65 active statutes: 19 universal + 46 scoped — 24 scoped matched the diff and scored, 22 scoped `not-applicable` with layer/path reasons). Full checklist stays off-ticket per rubric.

## Plan adherence

- Stages 1–3 implemented exactly as the revised plan specifies: candidate `batch_id`/`batch_created_at` columns + header inventory bullet (Stage 1); `claim_candidate_batch` / `get_candidate_batch` / `clear_candidate_batch` pool trio mirroring `claim_job_batch`'s `_utc_now()`, unclaimed `(NULL OR '')` predicate, subquery `UPDATE … ORDER BY … LIMIT ?`, batch_id-first param order (Stage 2); `count_eligible_for_dispatch_task` candidate branch splits `inflow_discovery` (unchanged helper) vs pool count via new `count_candidates_unclaimed_in_states` (Stage 3), with the dead `not claim_states` arm correctly omitted since the pre-branch guard already covers it.
- Joan's plan-rubric verdict (Plan Approved, revision 1) round-1 fix-now/discuss items are all closed on this tip: Betty contract section present and accurate, Stage 3 deploy-order Decision documents the AUTO volume-gate flip and the "must not land on `dev` ahead of AST-1259" constraint, dead branch dropped.
- Scope held: only `src/data/database.py` touched in the product commit (`e569ada6`); no `src/core/`, dispatcher, `config.py`, or `CANDIDATE_DATA_MODEL.md` edits. Test/bible deltas landed via a separate `merge-tests` commit (`6f684aff`, Betty's tree), keeping engineer and test-tree commits cleanly separated per `orch.roles.betty-owns-test-tree` / `astral.git.engineer-test-tree-ban`.

## Pattern conformance

`pattern.batch.entity-claim-process-release` — conforms (claim → get → clear pool trio is a faithful data-layer peer of the job/company shape; batch_id-first, cross-candidate pool, no owner-scope gate, matching the plan's explicit decision to overturn the AST-972 single-ctx carve-out).

## Findings

**discuss — straggler: `astral.state.core-decides-transitions` excluded at plan time but in-scope on this sweep.** The plan's "Considered but excluded" list drops this statute (reasoning: "no state transitions here"), and content-wise that's correct — `claim_candidate_batch` / `clear_candidate_batch` only touch the lock columns, never `candidate.state`. But the statute's `applies_when` (`layers: [core, data]`, `paths: [src/core/**, src/data/**]`) mechanically matches this diff's `data` layer + `src/data/database.py` path, so this sweep scores it `conforms`, not `not-applicable` — per C4 that's a callout, not a block. No code change needed; flagging so the plan-exclusion reasoning and the mechanical sweep predicate stay reconciled for anyone auditing this ticket later.

**advisory — schema-push script awareness (already surfaced by Joan as acceptable).** `candidate` is in `ALLOWED_CONFIG_TABLES` and `apply_config_table_upsert` compares exact column lists, so `scripts/push_tables_to_prod.py` needs both source and target DBs on the new `batch_id`/`batch_created_at` columns before a push — same shape as the AST-1134 `last_email_check` precedent. Not a blocker for this ticket; noting for whoever runs the next prod push.

## Frame diff

(none)

## What's solid

- `_CANDIDATE_BATCH_SORT_COLUMNS` allowlist mirrors the existing `_JOB_BATCH_SORT_COLUMNS` pattern exactly — no new hardcoded-set exposure, just the established SQL-injection-safe ORDER BY guard.
- No new imports added to `database.py`; all new functions reuse `_state_in_sql`, `_run_with_retry`, `_utc_now`, `_parse_candidate_row`, `_row_to_dict` — clean DRY reuse, public claim trio grouped together per §1.3.
- `count_eligible_for_dispatch_task`'s pre-branch `if not claim_states: return 0` guard was correctly left alone; verified `dispatch_claim_states` is non-empty for all `CANDIDATE_STATES` so the new candidate branch can't fall through unguarded.
- Test/bible delta (Betty, separate commit) precisely revises the one test Stage 3 invalidates (`test_candidate_entity_avail_is_inflow_not_stage` → `test_candidate_stage_avail_is_unclaimed_pool`, expecting `1` not `0`) and adds direct coverage for multi-row claim/get/clear, concurrent-claim refusal, release-all, and locked-pool zero-count — matches the plan's Betty-contract coverage list item-for-item.

context_tokens≈134000

— Radia

#### betty — 2026-08-07T18:33:17.623Z
## QA test manifest

`origin/sub/AST-1257/AST-1258-candidate-batch-lock-schema-and-pool-claim-apis` @ `6f684aff` (`merge-tests(AST-1258): origin/tests 91eae3cf`)

1. `tests/component/data/database/test_candidates.py::TestAst1258CandidateBatchClaim` — schema `batch_id`/`batch_created_at`; save leaves unclaimed; claim → get → clear multi-row pool; concurrent second claim → 0; clear releases all; claim unions primary+retry.
2. `tests/component/data/database/test_dispatch_tasks.py::TestAst972CandidateStageEligibility` — revised `test_candidate_stage_avail_is_unclaimed_pool` (expect pool `1`; was inflow-only `0`); claim-states + list-ids unchanged.
3. `tests/component/data/database/test_dispatch_tasks.py::TestAst1258CandidatePoolEligibility` — pool count `0` when all matching rows locked; `inflow_discovery` still uses inflow helper.

**Broken / obsolete (this pass):** `test_candidate_entity_avail_is_inflow_not_stage` → renamed/revised for AST-1258 pool Avail.

**Integration:** none revised (no existing scenario asserted unlocked/inflow-only candidate stage Avail).

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_candidates.py::TestAst1258CandidateBatchClaim \
  tests/component/data/database/test_dispatch_tasks.py::TestAst972CandidateStageEligibility \
  tests/component/data/database/test_dispatch_tasks.py::TestAst1258CandidatePoolEligibility \
  -q
```

**Bible (on publish-ref):**
- `docs/test-bible/data/database/candidates.md` `6f15870d21e8a4aa281484e6fe889ca4a828250c8e3e3117e949a7b37d293f7a`
- `docs/test-bible/data/database/dispatch_tasks.md` `f11f0bf8803323c5a7e5774d6a814c84d3727d46096806a83194868c44fdb8fa`
- `docs/test-bible/core/candidate.md` `9b57b5533c66ff198ed6bb8d5582630754b21f2604f3df0101bf764d619c168a`

— Betty

#### joan — 2026-08-07T18:28:27.841Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1258
**Overall:** APPROVED
**Publish ref tip:** `sub/AST-1257/AST-1258-candidate-batch-lock-schema-and-pool-claim-apis` @ `952277d8` (doc-only delta from `351e9484`; Files Changed table unchanged, so the statute frame is unchanged)

## Traceability

AC1→S1; AC2→S2 (+S4 verify); AC3→S3 (+S4 verify). No orphan stages; no unmapped AC. R5 pass.

**Considered:** 41 active statutes re-scored in-session (18 universal + 23 scoped considered, 24 scoped excluded). All conform — the three round-1 non-conformances are closed.

## Round 1 items — all cleared

- **fix-now (test invalidation):** closed. The **Tests invalidated (Betty contract)** section names the exact node id, and I confirmed it resolves and passes on this tip: `tests/component/data/database/test_dispatch_tasks.py::TestAst972CandidateStageEligibility::test_candidate_entity_avail_is_inflow_not_stage` (class at line 1343). The before/after values are right — that fixture saves only `c972`, so the pool count after Stage 3 is exactly `1`. The five Betty coverage items match the AC2/AC3 surface, and the Files Changed note now scopes the engineer off `tests/` explicitly rather than implying no test impact. `orch.roles.betty-owns-test-tree` / `orch.pipeline.plan-is-bible` → conforms.
- **discuss (volume gate):** closed. The Risk line no longer claims behavior cannot flip, and the new Stage 3 deploy-order Decision names the gate site and the hard constraint that this child must not reach `dev` ahead of AST-1259. `astral.batch.claim-process-release` → conforms for this child; the residual unlocked path stays AST-1259's to close.
- **discuss (dead branch):** closed. The arm and the "or claim_states empty" Done-when clause are gone, and step 2 now tells the builder *not* to add it back with the reason — better than a silent deletion. Step 1 was tightened to require a non-empty list through `_state_in_sql`. `astral.standards.dry-and-focused-functions` → conforms.
- **nit:** closed — `get_candidate_batch` keeps the `_row_to_dict` hop.

Nothing new introduced by the revision. Everything I verified against the tip in round 1 still holds; the `claim_job_batch` mirror, schema create/migrate split, `save_candidate` lock safety, and sort-column allowlist are unchanged.

Status → Plan Approved. R7 satisfied by this comment (slim artifact, no attachment).

— Joan

context_tokens≈108000

#### katherine — 2026-08-07T18:27:06.703Z
[plan-discuss] round=1 reply

Addressed on `origin/sub/AST-1257/AST-1258-candidate-batch-lock-schema-and-pool-claim-apis` @ `952277d8`.

**Delta**
1. **fix-now:** Added **Tests invalidated (Betty contract)** — names `TestAst972CandidateStageEligibility::test_candidate_entity_avail_is_inflow_not_stage` (expect pool `1` after Stage 3, not inflow `0`) and Betty coverage for multi-row claim/get/clear, second claim → 0, clear releases all, pool 0 when locked, inflow helper unchanged. Engineer still does not edit `tests/` / bible.
2. **discuss (risk / gate):** Corrected Self-Assessment Risk; added Stage 3 Decision that AUTO volume gate flips here while claim stays unlocked until AST-1259 — **this child must not land on `dev` ahead of AST-1259**.
3. **discuss (dead branch):** Dropped `if not claim_states: return 0` from the candidate arm and the "or claim_states empty" Done-when clause (pre-branch empty `claim_states` already returns 0).
4. **nit:** `get_candidate_batch` uses `_parse_candidate_row(_row_to_dict(row))`.

Status stays **Plan Discuss** for Joan re-validate.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1257/AST-1258-candidate-batch-lock-schema-and-pool-claim-apis/docs/features/dispatcher/ast-1258-candidate-batch-lock-schema-and-pool-claim-apis.md

#### joan — 2026-08-07T18:25:26.111Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1258
**Overall:** REVISE
**Publish ref tip:** `sub/AST-1257/AST-1258-candidate-batch-lock-schema-and-pool-claim-apis` @ `351e9484`

## Traceability

AC1→S1; AC2→S2 (+S4 verify); AC3→S3 (+S4 verify). No orphan stages; no unmapped AC. R5 pass.

**Considered:** 41 active statutes scored in-session (18 universal + 23 scoped considered, 24 scoped excluded).

## Findings

### fix-now — Stage 3 breaks a passing component test the plan does not disclose

`tests/component/data/database/test_dispatch_tasks.py::test_candidate_entity_avail_is_inflow_not_stage` (line 1368) passes on this tip and asserts exactly the behavior Stage 3 overturns:

```
task = {entity_type: candidate, trigger_state: REQUESTED_ARTIFACTS,
        candidate_id: c972, task_key: craft_get_rubric}
assert db.count_eligible_for_dispatch_task(task) == 0
```

Candidate `c972` is saved in `REQUESTED_ARTIFACTS` and unclaimed, so after Stage 3 that call returns the unclaimed pool count (1), not 0 — the same non-inflow key Stage 4 uses as its worked example. The plan says only "No `src/core/`, `src/utils/config.py`, dispatcher, tests/, bible, or `CANDIDATE_DATA_MODEL.md` in this ticket", which reads as no test impact. The builder cannot fix it either (`orch.roles.betty-owns-test-tree`, `astral.git.engineer-test-tree-ban`), so build-child lands on a red suite with no sanctioned instruction.

**Recommendation:** add a **Tests invalidated (Betty contract)** section naming that test id and the new expected value, plus the coverage Betty owns for this ticket: claim → get → clear over a multi-row pool, second concurrent claim on locked rows returns 0, clear releases all, pool count is 0 when every row is locked, and `inflow_discovery` still routes to the inflow helper. Statutes: `orch.roles.betty-owns-test-tree` and `orch.pipeline.plan-is-bible` → violates.

### discuss — Self-Assessment risk line is not accurate; Stage 3 alone un-gates the unlocked candidate path

`src/core/dispatcher.py:993` gates the AUTO loop on `available < effective_min` using this same count. Today a candidate stage task gets 0 from the inflow helper (candidate is not in `ACTIVE_SEARCH`), so those loops short-circuit. After Stage 3 the count is the unclaimed pool size, the gate passes, and the work runs on the **still-unlocked** single-ctx candidate branch until AST-1259 lands. So "Dispatcher still on the unlocked path until AST-1259, so production claim behavior does not flip in this ticket alone" is not right — the volume gate flips here.

**Recommendation:** correct that Risk sentence and state the ordering constraint explicitly (this child must not reach `dev` ahead of AST-1259). `astral.batch.claim-process-release` → needs-discussion for this child; the residual violation itself is AST-1259's to close.

### discuss — Stage 3 step 2's `not claim_states` branch is unreachable

`count_eligible_for_dispatch_task` already returns 0 on empty `claim_states` before the candidate branch, and `dispatch_claim_states(state, "candidate")` is non-empty for all 21 `CANDIDATE_STATES` (probed on this tip). The instruction would have the builder add dead code, and the Stage 3 Done-when promises a 0 that no input can produce.

**Recommendation:** drop the branch and the "or claim_states empty" clause from the Done-when. `astral.standards.dry-and-focused-functions` → needs-discussion.

### acceptable — deploy-order note, no plan change

`candidate` is in `ALLOWED_CONFIG_TABLES` and `apply_config_table_upsert` compares exact column lists, so `scripts/push_tables_to_prod.py` needs both ends on the new schema. Same shape as the AST-1134 `last_email_check` precedent — flagging for Radia, not asking for an edit.

### acceptable — nit

Stage 2 step 3: `get_candidate` parses via `_parse_candidate_row(_row_to_dict(row))`; keep the `_row_to_dict` hop in `get_candidate_batch`.

## Verified against the tip (no change needed)

- `save_candidate` is an explicit-column INSERT plus a targeted `SET` UPDATE, so it cannot clobber a lock — Stage 1 step 3 is correct.
- `_ensure_candidate_schema` creates the table in the `if` and migrates in the `else`; Stage 1 naming both sites is required, not belt-and-braces.
- Stage 2 mirrors `claim_job_batch` faithfully: `_utc_now()`, `(batch_id IS NULL OR batch_id = '')`, subquery UPDATE with `ORDER BY … LIMIT ?`, `_run_with_retry`, rowcount return.
- All four `_CANDIDATE_BATCH_SORT_COLUMNS` entries exist on the candidate table (`rowid`, `created_at`, `updated_at`, `state_changed_at`).
- `INFLOW_CONFIG["discovery"]["task_key"] == "inflow_discovery"`; no name collisions for the three new public APIs; candidate inventory bullet is at header line 12.
- Every candidate path in the new branch returns, so it never falls through to `count_entities_in_state`, which raises for `candidate`.
- Pool-wide (no `candidate_id` scope) is right: the count docstring promises what the task would actually claim, and the claim is cross-candidate per parent Functional scope 2.

Status → Plan Discuss. One fix-now; the two discuss items are cheap edits if you want them in the same revision.

— Joan

context_tokens≈94000

#### katherine — 2026-08-07T18:17:21.678Z
Plan on publish ref `origin/sub/AST-1257/AST-1258-candidate-batch-lock-schema-and-pool-claim-apis` @ `351e9484`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1257/AST-1258-candidate-batch-lock-schema-and-pool-claim-apis/docs/features/dispatcher/ast-1258-candidate-batch-lock-schema-and-pool-claim-apis.md

**Self-assessment**
- **Scope:** Single-Component — only `src/data/database.py` (schema + claim/get/clear + eligibility branch); dispatcher/core and canon docs stay with AST-1259 / AST-1260.
- **Conf:** high — mirrors `claim_job_batch` / get / clear and the `(batch_id IS NULL OR batch_id = '')` unclaimed predicate; eligibility splits `inflow_discovery` vs stage pool count on `task_key`.
- **Risk:** Medium — wrong eligibility branch skews Avail for stage vs inflow; wrong unclaimed predicate allows double-claim or stuck locks. Production claim path still unlocked until Ada wires AST-1259.

**Decisions locked in plan:** cross-candidate pool (no `candidate_id` owner filter on claim); stage Avail is pool-wide; `CANDIDATE_DATA_MODEL` / statutes untouched here.

---

# AST-1258 — Candidate batch lock schema and pool claim APIs

**Linear:** [AST-1258](https://linear.app/astralcareermatch/issue/AST-1258/candidate-batch-lock-schema-and-pool-claim-apis-candidate-table-does)
**Parent:** [AST-1257](https://linear.app/astralcareermatch/issue/AST-1257/candidate-table-does-not-have-batch-id) — candidate table does not have batch_id
**Publish ref:** `origin/sub/AST-1257/AST-1258-candidate-batch-lock-schema-and-pool-claim-apis`

Add candidate row `batch_id` / `batch_created_at`, keep the database header inventory honest, and expose data-layer claim → get → clear with the same **pool** shape as job/company (batch_id-first, claim up to `limit` unclaimed candidates in claim states, release all on clear). Stage-task eligibility counts that unclaimed pool. Does **not** wire dispatcher or core wrappers (AST-1259) and does **not** own canon/docs text (AST-1260).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Candidate schema columns; header inventory; `claim_candidate_batch` / `get_candidate_batch` / `clear_candidate_batch`; unclaimed pool count helper; branch `count_eligible_for_dispatch_task` for non-inflow candidate stage tasks | data |

No `src/core/`, `src/utils/config.py`, dispatcher, or `CANDIDATE_DATA_MODEL.md` in this ticket. Engineer does **not** edit `tests/` or bible (`orch.roles.betty-owns-test-tree`); see **Tests invalidated (Betty contract)** below for the suite delta Stage 3 causes.

## Tests invalidated (Betty contract)

Stage 3 changes `count_eligible_for_dispatch_task` for non-`inflow_discovery` `entity_type=candidate` tasks. This **invalidates** a currently green assertion; Betty owns the revision (`qa-child` after Code Complete). Builder does not touch `tests/` or bible.

| Item | Detail |
|------|--------|
| **Broken by tip (after Stage 3)** | `tests/component/data/database/test_dispatch_tasks.py::TestAst972CandidateStageEligibility::test_candidate_entity_avail_is_inflow_not_stage` |
| **Today (pre-Stage 3)** | Task `{entity_type: candidate, trigger_state: REQUESTED_ARTIFACTS, candidate_id: c972, task_key: craft_get_rubric}` → `count_eligible_for_dispatch_task` == `0` (inflow helper; candidate not ACTIVE_SEARCH) |
| **After Stage 3** | Same task → unclaimed pool count for `dispatch_claim_states("REQUESTED_ARTIFACTS", "candidate")` (fixture with one unclaimed `REQUESTED_ARTIFACTS` row → **`1`**, not `0`) |
| **Betty owns** | Revise that test (and bible note if present) to expect pool Avail for non-inflow candidate keys; keep `inflow_discovery` on the inflow helper |

**Coverage Betty must add or extend for this ticket** (component / bible for data claim path):

1. Claim → get → clear over a **multi-row** unclaimed pool (same `batch_id`).
2. Second concurrent `claim_candidate_batch` with a different `batch_id` on already-locked rows returns **0**.
3. `clear_candidate_batch` releases **all** rows in the batch (null/empty `batch_id` again).
4. Pool count is **0** when every matching-state row is locked.
5. `task_key=inflow_discovery` still routes to `count_candidate_inflow_discovery_eligible` (unchanged predicate).

## Stage 1: Candidate lock columns + header inventory

**Done when:** Fresh and existing SQLite DBs expose nullable `candidate.batch_id` and `candidate.batch_created_at` via `_ensure_candidate_schema`; unclaimed rows have NULL (or empty) `batch_id`; module header inventory lists those columns on the candidate bullet.

1. In `src/data/database.py` module docstring **Tables used (inventory)**, update the `candidate` bullet so it names `batch_id` and `batch_created_at` alongside the existing candidate fields (same honesty bar as company/job inventory lines).
2. In `_ensure_candidate_schema`:
   - Add `batch_id TEXT` and `batch_created_at TIMESTAMP` (or `TEXT` — match company CREATE style: `batch_id TEXT`, `batch_created_at TIMESTAMP`) to the `CREATE TABLE candidate` column list.
   - Add `("batch_id", "TEXT")` and `("batch_created_at", "TIMESTAMP")` to the existing idempotent `ALTER TABLE … ADD COLUMN` migration loop so already-created tables gain the columns.
3. Do **not** change `save_candidate` INSERT/UPDATE to set batch columns — claim/clear own those writes. New inserts leave them NULL (unclaimed).
4. Do **not** edit `docs/features/candidate/CANDIDATE_DATA_MODEL.md` (AST-1260 owns “no batch primitives” doc cleanup).

⚠️ **Decision:** Column types and nullability mirror `company` (`batch_id TEXT`, `batch_created_at TIMESTAMP`, NULL = unclaimed). Unclaimed predicate for claim/count matches job/company: `(batch_id IS NULL OR batch_id = '')`.

## Stage 2: Pool claim / get / clear APIs

**Done when:** Data layer can lock N unclaimed candidates in a claim-state set under one `batch_id`, return those rows by `batch_id`, release them all on clear, and a second claim with a different `batch_id` cannot steal already-locked rows. No core or dispatcher calls these yet.

1. Near the other candidate public APIs in `src/data/database.py` (after `get_candidate` / `list_candidates`, before unrelated candidate helpers), add module-level allowlist:
   - `_CANDIDATE_BATCH_SORT_COLUMNS = frozenset({"rowid", "created_at", "updated_at", "state_changed_at"})`
2. Implement `claim_candidate_batch(batch_id: str, state: str, limit: int, sort_by: Optional[str] = None, *, states: Optional[List[str]] = None) -> int`:
   - Parameter order: **`batch_id` first** (caller owns the golden ticket).
   - `claim_states = states if states is not None else [state]`; build `state_sql` / `state_params` via existing `_state_in_sql`.
   - Unclaimed filter: `(batch_id IS NULL OR batch_id = '')`.
   - Cross-candidate **pool**: no `candidate_id` owner scope — claim any matching candidate rows (overturns AST-972 single-ctx / one-row-only gate).
   - Set `batch_id` and `batch_created_at` using `_utc_now()` for the timestamp (same pattern as `claim_job_batch`, not company’s `datetime('now')` SQL).
   - UPDATE via subquery on `astral_candidate_id` (or `rowid`) with `ORDER BY` + `LIMIT ?`, mirroring `claim_job_batch`:
     - If `sort_by` is in `_CANDIDATE_BATCH_SORT_COLUMNS`, `ORDER BY {sort_by} ASC NULLS FIRST`; else `ORDER BY rowid`.
   - `limit` coerced with `int(limit)`; call `_ensure_candidate_schema` inside the connection path; wrap with `_run_with_retry`.
   - Return `cur.rowcount` (claimed count). Raise on DB errors; **do not log** (data layer).
3. Implement `get_candidate_batch(batch_id: str) -> List[Dict[str, Any]]`:
   - `SELECT * FROM candidate WHERE batch_id = ?`; parse each row with `_parse_candidate_row(_row_to_dict(row))` — same hop as `get_candidate` (do not pass the raw sqlite3.Row straight into `_parse_candidate_row`).
   - Ensure schema; `_run_with_retry`.
4. Implement `clear_candidate_batch(batch_id: str) -> int`:
   - `UPDATE candidate SET batch_id = NULL, batch_created_at = NULL WHERE batch_id = ?`; return rowcount.
   - Ensure schema; `_run_with_retry`.
5. Keep public functions grouped; helpers (if any) below public APIs per §1.3 / public-then-helpers.

⚠️ **Decision:** No optional `candidate_id` filter on claim — parent requires cross-candidate pool parity with job/company claim shape, not a single-row gate. Ada (AST-1259) may pass `states=` from `dispatch_claim_states` and choose `limit` / `batch_size`; this ticket does not add core `get_new_candidate_batch`.

⚠️ **Decision:** Do not touch `claim_job_batch` / `claim_company_batch` / `set_company_batch` SQL. Shared helpers already used (`_state_in_sql`, `_run_with_retry`, `_utc_now`) are fine to call; do not refactor job/company claim bodies.

## Stage 3: Eligibility / count for candidate stage claim tasks

**Done when:** `count_eligible_for_dispatch_task` for `entity_type=candidate` still uses the inflow helper for `task_key=inflow_discovery`, and for every other candidate claim-queue task reports the count of unclaimed candidates in `dispatch_claim_states(trigger_state, "candidate")` (0 when none available or all locked).

1. Add `count_candidates_unclaimed_in_states(states: List[str]) -> int` in `src/data/database.py` next to the claim APIs (or next to `count_entities_in_state`):
   - Count rows where `{state_sql}` AND `(batch_id IS NULL OR batch_id = '')`.
   - Use `_state_in_sql(states)` (non-empty list required — same as other count helpers). Callers already have non-empty `claim_states` when they reach this helper (see step 2).
   - Ensure schema; `_run_with_retry`.
2. In `count_eligible_for_dispatch_task`, replace the unconditional candidate branch:
   ```python
   if entity_type == "candidate":
       return count_candidate_inflow_discovery_eligible(...)
   ```
   with:
   - If `(task.get("task_key") or "").strip() == INFLOW_CONFIG["discovery"]["task_key"]` (`"inflow_discovery"`), keep `count_candidate_inflow_discovery_eligible(candidate_id, float(task.get("freq_hrs") or 0), task.get("last_run_at"))`.
   - Else: return `count_candidates_unclaimed_in_states(claim_states)`.
   - Do **not** add an `if not claim_states: return 0` arm inside the candidate branch — `count_eligible_for_dispatch_task` already returns `0` when `claim_states` is empty **before** the entity-type branches; that arm would be dead code for current `CANDIDATE_STATES` / `dispatch_claim_states`.
3. Do **not** change `count_candidate_inflow_discovery_eligible` / `describe_candidate_inflow_discovery_eligibility` predicates (ACTIVE_SEARCH + stale terms).
4. Do **not** extend `count_entities_in_state` to raise-or-handle `"candidate"` unless needed for DRY; the dedicated helper is enough for this ticket. If you reuse `count_entities_in_state`, it must count the **global** unclaimed candidate pool (not filter by `task["candidate_id"]` as an owner).

⚠️ **Decision:** Stage Avail is **pool-wide** (all candidates in claim states with null/empty `batch_id`), not 0/1 for the dispatch row’s `candidate_id`. That matches parent “unclaimed pool size” / cross-candidate claim. Per-candidate dispatch rows may show the same pool size until AST-1259 wires claim; do not invent a per-row 0/1 carve-out here (overturns AST-972 “Avail always inflow for candidate entity” for non-inflow keys).

⚠️ **Decision — deploy / merge order:** Stage 3 alone flips the dispatcher AUTO volume gate (`available < effective_min` at `src/core/dispatcher.py` ~993). Today non-inflow candidate stage tasks get `0` from the inflow helper and short-circuit; after Stage 3 the pool count can pass the gate and work still runs on the **unlocked** single-ctx candidate branch until AST-1259 lands claim → process → release. **This child must not land on `origin/dev` ahead of AST-1259.** Residual unlocked-path violation is AST-1259’s to close; this ticket still ships the data APIs + honest pool count.

## Stage 4: Manual verification (build-child, no product commit required if Stages 1–3 already committed)

**Done when:** Builder has exercised claim → get → clear and eligibility on an in-memory or local DB without touching dispatcher.

1. After Stages 1–3 are committed, verify by hand or a throwaway snippet under `debug/spikes/AST-1258/` (gitignored; do not commit):
   - Ensure schema; insert/update ≥2 candidates into a claimable state (e.g. `REQUESTED_ARTIFACTS`) with null `batch_id`.
   - `claim_candidate_batch("craft_get_rubric-test-uuid", "REQUESTED_ARTIFACTS", 2)` → 2; `get_candidate_batch` returns both; second claim with another batch_id and limit 2 → 0 (locked).
   - `clear_candidate_batch` → 2; rows unclaimed again.
   - `count_eligible_for_dispatch_task` with `entity_type=candidate`, `task_key=craft_get_rubric` (or any non-inflow key), `trigger_state=REQUESTED_ARTIFACTS`, any `candidate_id` → pool size; same task with all rows locked → 0; `task_key=inflow_discovery` still uses inflow helper.
2. No dispatcher run required for Code Complete of this ticket.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1257/AST-1258-candidate-batch-lock-schema-and-pool-claim-apis`.
- Do not add files outside **Files Changed**.
- Do not wire `src/core/dispatcher.py`, `src/core/candidate.py`, or core `get_new_*` wrappers.
- On ambiguity or drift: stop and comment on **parent** AST-1257 with the 🛑 Stage N blocked template.

## Self-Assessment

**Scope:** Single-Component — one data-layer module (`database.py`): schema + claim/get/clear + eligibility branch; no core/UI.

**Conf:** high — copies the existing `claim_job_batch` / `get_job_batch` / `clear_job_batch` and unclaimed `(NULL OR '')` predicate; eligibility split is a narrow branch on `task_key` vs inflow.

**Risk:** Medium — wrong eligibility branch skews Avail or breaks inflow; wrong unclaimed predicate allows double-claim or stuck locks. Stage 3 also un-gates the AUTO volume check for candidate stage tasks while the claim path is still unlocked until AST-1259 — do not merge this child to `dev` ahead of AST-1259.

## Revisions

**Revision 1 — 2026-08-07**  
Driven by: Joan `[plan-discuss] round=1 concern` (REVISE @ `351e9484`)  
Changes: added **Tests invalidated (Betty contract)** (fix-now); corrected Risk / deploy-order Decision for Stage 3 volume-gate flip (discuss); dropped dead `not claim_states` arm and Done-when clause (discuss); `get_candidate_batch` keeps `_row_to_dict` hop (acceptable nit).

## Rules check (plan vs ASTRAL_CODE_RULES)

| Rule | Plan stance |
|------|-------------|
| §2.4 claim-process-release / batch-id-first / batch-id-format | claim/get/clear with batch_id first; caller mints `f"{task_key}-{uuid}"` later (AST-1259); format not reimplemented here |
| §1.5 data-raises-caller-logs | no logging in new data APIs |
| §1.1 database-header-inventory | Stage 1 updates candidate inventory bullet |
| §1.3 DRY / public-then-helpers | reuse `_state_in_sql`, `_run_with_retry`, `_utc_now`, `_parse_candidate_row`; public claim trio grouped |
| §2.1 config SSoT | no new state lists; callers pass `states` from `dispatch_claim_states` / config |
| §3.3 import direction | data stays on utils config imports already present (`INFLOW_CONFIG`, `CANDIDATE_STATES`, `ENTITY_TYPES`) |
| Out of scope | dispatcher finally-clear, core wrappers, debug contract on dispatch path, statute/pattern/`CANDIDATE_DATA_MODEL` — siblings |
| `astral.state.core-decides-transitions` | **In scope / conforms** (resolve): claim/clear touch lock columns only; never `candidate.state` (Radia C4 discuss — plan had excluded; mechanical layer/path match scores conforms) |

## Review (build stub)

**Publish ref:** `origin/sub/AST-1257/AST-1258-candidate-batch-lock-schema-and-pool-claim-apis`
**Tip:** `e569ada6`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–3 | `e569ada6` | Candidate `batch_id`/`batch_created_at`; claim/get/clear pool APIs; stage Avail pool count (`inflow_discovery` unchanged) |
| 4 | (smoke) | Manual in-memory claim → get → clear + eligibility; not committed |

## Radia review — [code-rubric] revision=1

**Publish ref:** `sub/AST-1257/AST-1258-candidate-batch-lock-schema-and-pool-claim-apis` @ `6f684aff`
**Overall:** DISCUSS

Full active-set sweep run in-session (65 active statutes: 19 universal + 46 scoped — 24 scoped matched the diff and scored, 22 scoped `not-applicable` with layer/path reasons; full checklist stays off-ticket per rubric).

**Plan adherence:** Stages 1–3 match the revised plan exactly — candidate lock columns + header inventory (Stage 1); `claim_candidate_batch` / `get_candidate_batch` / `clear_candidate_batch` pool trio mirroring `claim_job_batch` (batch_id-first, `_utc_now()`, unclaimed `(NULL OR '')` predicate, subquery `UPDATE … ORDER BY … LIMIT ?`) (Stage 2); `count_eligible_for_dispatch_task` candidate branch splits `inflow_discovery` vs new `count_candidates_unclaimed_in_states` pool count, dead `not claim_states` arm correctly omitted (Stage 3). Joan's round-1 fix-now/discuss items (Betty contract, deploy-order Decision, dead branch) are all closed on this tip. Scope held to `src/data/database.py` only; test/bible landed on a separate `merge-tests` commit, keeping engineer/test-tree commits cleanly separated.

**Pattern conformance:** `pattern.batch.entity-claim-process-release` — conforms.

**Findings:**
- **discuss** — straggler: `astral.state.core-decides-transitions` was excluded at plan time ("no state transitions here" — content-correct) but this sweep's mechanical `applies_when` match (`layers: [data]`, path `src/data/database.py`) scores it `conforms`, not `not-applicable`. No code change needed; flagged per C4 to reconcile plan-exclusion reasoning with the sweep predicate.
- **advisory** — schema-push script awareness (Joan already flagged as acceptable): `candidate` is in `ALLOWED_CONFIG_TABLES`; `scripts/push_tables_to_prod.py` needs both DBs on the new columns before the next push (AST-1134 `last_email_check` precedent).

**What's solid:** `_CANDIDATE_BATCH_SORT_COLUMNS` mirrors the existing `_JOB_BATCH_SORT_COLUMNS` allowlist pattern; no new imports added; public claim trio grouped per §1.3; Betty's test/bible delta revises exactly the one invalidated assertion and adds direct coverage for multi-row claim/get/clear, concurrent-claim refusal, release-all, and locked-pool zero-count.

context_tokens≈134000

— Radia


## Resolution

**Date:** 2026-08-07  
**Tip before resolve:** `412bd950` (Radia `docs(AST-1258): Radia review — findings`)

| Finding | Action |
|---------|--------|
| **discuss** — `astral.state.core-decides-transitions` plan-excluded vs mechanical `conforms` | No product change. Linear **In scope** now lists the statute (lock columns only; claim/clear never write `candidate.state`). Plan Rules check updated below. |
| **advisory** — `push_tables_to_prod` / `ALLOWED_CONFIG_TABLES` column list | Acknowledged; no code change this ticket (same as Joan acceptable / AST-1134 precedent). |

**fix-now:** none.

## Bug: AST-1432 — Scope candidate-entity Avail to the bound candidate

Overturns AST-1258 Stage 3 **Decision** that stage Avail is pool-wide for Scheduled Actions. Claim/get/clear stay the cross-candidate pool (AST-1258 Stage 2 / AST-1259). Do not rewrite Stages 1–4.

### As-is

On Scheduled Actions, a `entity_type=candidate` dispatch_task row (non-`inflow_discovery`) shows Availability **2+**: `count_eligible_for_dispatch_task` returns `count_candidates_unclaimed_in_states(claim_states)` — every unclaimed candidate in those states, not only this row's `candidate_id`.

### To-be

That row's Availability is always **0 or 1**: whether *this* row's candidate is unclaimed and in `dispatch_claim_states(trigger_state, "candidate")`. Other candidates do not add to the count.

### Repro

In-memory DB (same shape as AST-1258 Stage 3 / Betty's `TestAst972CandidateStageEligibility` fixture):

1. Save two candidates `c-a` and `c-b`, both `state="REQUESTED_ARTIFACTS"`, `batch_id` null.
2. Task row (no DB seed required — pass the dict straight into the count):

```python
task = {
    "entity_type": "candidate",
    "trigger_state": "REQUESTED_ARTIFACTS",
    "candidate_id": "c-a",
    "task_key": "craft_get_rubric",  # CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["task_key"]
}
```

3. **Broken:** `count_eligible_for_dispatch_task(task) == 2`. **Expected:** `1`.
4. Lock `c-a` (`claim_candidate_batch` with `limit=1` that takes `c-a`, or set `c-a.batch_id` non-empty); leave `c-b` unclaimed. **Broken:** count is `1` (the other candidate). **Expected:** `0`.
5. `GET /api/admin/dispatch_tasks` stamps `available_count` from this function (`list_dtasks`); the Scheduled Actions Avail column is that number.

### Root cause

AST-1258 Stage 3 split `count_eligible_for_dispatch_task`'s candidate branch: `inflow_discovery` stayed on `count_candidate_inflow_discovery_eligible` (already 0/1 per `candidate_id`); every other candidate claim-queue key returns the **global** unclaimed pool. That matched parent AST-1257 AC4 ("unclaimed pool size") and the Stage 3 Decision ("not 0/1 for the dispatch row’s `candidate_id`"). Scheduled Actions rows are per-candidate, so the pool count shows as 2+ on each bound row.

The defect is the **count** used for Avail, not batch locking and not `list_dtasks` (it already calls `count_eligible_for_dispatch_task(row)` when `entity_type`, `trigger_state`, and `candidate_id` are set).

### Proposed change

In `src/data/database.py` only.

1. Extend `count_candidates_unclaimed_in_states(states: List[str], candidate_id: Optional[str] = None) -> int`:
   - Keep today's SQL when `candidate_id` is omitted / blank after strip: `COUNT(*)` where `{state_sql}` AND `(batch_id IS NULL OR batch_id = '')`.
   - When `(candidate_id or "").strip()` is non-empty, add `AND astral_candidate_id = ?` (bind the stripped id). Result is **0 or 1** (candidate PK).
   - Same `_state_in_sql` / `_ensure_candidate_schema` / `_run_with_retry` as today. Do not log.

2. In `count_eligible_for_dispatch_task`, candidate non-inflow arm — replace:

   ```python
   return count_candidates_unclaimed_in_states(claim_states)
   ```

   with:

   ```python
   return count_candidates_unclaimed_in_states(claim_states, candidate_id=candidate_id)
   ```

   `candidate_id` is already read from `task` and the function already returns `0` when it is missing. Do **not** add a new empty-`claim_states` arm (pre-branch guard still covers it).

3. Update this function's docstring so candidate non-inflow Avail is described as **this row's candidate** (0/1, unclaimed + in `claim_states`), not "entities this task would actually claim" for the cross-candidate pool. `inflow_discovery` sentence stays (still the inflow helper).

4. Do **not** change `claim_candidate_batch` / `get_candidate_batch` / `clear_candidate_batch` / `get_new_candidate_batch`. Do **not** pass `candidate_id` into claim. Do **not** edit `src/ui/api/api_admin.py` `list_dtasks` (gaze_email / meteorite mailbox bind-count carve-out stays). Do **not** edit job/company branches.

⚠️ **Decision — Avail only; pool claim stays:** Parent step 3 asked whether dispatcher Run must bind to this row's candidate. **No.** AST-1259 cross-candidate `get_new_candidate_batch` is unchanged. Avail-only is sufficient for this ticket's AC (Scheduled Actions shows 0 or 1). Manual Run on a row with Avail=1 can still claim other unclaimed candidates up to `batch_size` — existing pool behavior, out of this bug.

⚠️ **Decision — shared counter, accepted AUTO side effect:** Dispatcher AUTO (`_run_dispatch_loop` `available < effective_min`) and `run_task` `available_count` share `count_eligible_for_dispatch_task`. They will also become 0/1 for candidate stage rows. That is not a claim-scope change. Do not add a second counter for UI vs claim. Candidate stage rows with `min_count > 1` will never AUTO; do not retune `min_count` here.

### Blast radius

- **Touches:** `count_candidates_unclaimed_in_states` signature (optional `candidate_id`); candidate non-inflow arm + docstring of `count_eligible_for_dispatch_task`.
- **Callers of the count (behavior flip for candidate stage keys):** `api_admin.list_dtasks` Avail; `dispatcher._run_dispatch_loop` AUTO volume gate; `dispatcher.run_task` enrichment; `dispatcher._debug_log_auto_off_stage_skips`. Job/company and `gaze_email` mailbox bind-counts do not use this arm.
- **Unchanged claim path:** `dispatcher._run_unified` → `get_new_candidate_batch` → `claim_candidate_batch` (still pool-wide). Job `claim_cap` uses this count only for consult chunk exhaustion (`entity_type=job`).
- **Tests that assume pool Avail on a bound candidate row** (Betty; engineer does not edit `tests/`):
  - `tests/component/data/database/test_dispatch_tasks.py::TestAst972CandidateStageEligibility::test_candidate_stage_avail_is_unclaimed_pool` — fixture one unclaimed `REQUESTED_ARTIFACTS` row expected pool `1` (still `1` if that row **is** the bound `candidate_id`; breaks if a later fixture adds a second candidate and still expects `2`).
  - `tests/component/data/database/test_dispatch_tasks.py::TestAst1258CandidatePoolEligibility` — "pool count 0 when all matching rows locked" still holds for the bound candidate; any assertion that two unclaimed candidates make a single bound row's count `2` is now wrong (expect `1`).
- **inflow_discovery** tests unchanged (different arm).

### What must still hold

- AST-1258 AC1 / AC2: candidate `batch_id` / `batch_created_at`; claim → get → clear still locks a **cross-candidate** unclaimed pool; second concurrent claim on locked rows returns 0; clear releases all.
- `task_key=inflow_discovery` still uses `count_candidate_inflow_discovery_eligible` (ACTIVE_SEARCH + stale terms) — already 0/1 per candidate.
- Job/company pool Avail unchanged (still scoped to the row's owner `candidate_id` as today).
- Mailbox `gaze_email` / meteorite inbox Avail stays `count_inbox_bound_by_candidate` in `list_dtasks`, not this function.
- Unclaimed predicate stays `(batch_id IS NULL OR batch_id = '')`.
- Empty `claim_states` still returns 0 **before** entity-type branches.
- No dispatcher / core wrapper / `CANDIDATE_DATA_MODEL.md` edits in this bug.

### Board (AST-1432)

**Joan (CANON: OK).** Pool claim stays cross-candidate; Avail scoping via optional `candidate_id` on `count_candidates_unclaimed_in_states` is not a statute/pattern change. `astral.batch.claim-process-release` / `pattern.batch.entity-claim-process-release` govern claim → process → release, not Avail display.

**Betty (TESTS: REVISE).** Sibling gap AST-1436: `TestAst1258CandidatePoolEligibility::test_pool_count_zero_when_all_matching_rows_locked` asserts pool 2 on a bound row; missing two-candidate repro (bound Avail 1; lock bound / other unclaimed → 0).

### Review (AST-1432)

**Radia [code-rubric] PROCEED** @ `83575853`. C1–C7 complete. fix-now: none. discuss: none. [bug-repro] OK. What must still hold: OK. Advisory only: `[bug-repro]` tag in commit subject not test docstring; stale "unclaimed pool" comment on inflow helper test.
