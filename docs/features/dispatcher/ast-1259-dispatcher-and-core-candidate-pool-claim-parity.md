# AST-1259 — Dispatcher and core candidate pool claim parity

**Linear:** [AST-1259](https://linear.app/astralcareermatch/issue/AST-1259/dispatcher-and-core-candidate-pool-claim-parity-candidate-table-does)
**Parent:** [AST-1257](https://linear.app/astralcareermatch/issue/AST-1257/candidate-table-does-not-have-batch-id) — candidate table does not have batch_id
**Publish ref:** `origin/sub/AST-1257/AST-1259-dispatcher-and-core-candidate-pool-claim-parity`

After AST-1258’s data-layer claim / get / clear, add core `get_new_candidate_batch` / `clear_candidate_batch` wrappers and replace the unlocked single-ctx candidate branch in `dispatcher._run_unified` with claim → process → release using the same `batch_size` / `dispatch_claim_states` pool mechanics as job/company (always clear in `finally` and on empty-batch early exit; Style D debug on the touched claim path). Does **not** own schema/data APIs (AST-1258) or statute/pattern/docs text (AST-1260).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Add `get_new_candidate_batch` / `clear_candidate_batch` (batch_id-first wrappers over AST-1258 data APIs); extend module docstring | core |
| `src/core/dispatcher.py` | Candidate branch of `_run_unified`: claim via those wrappers; empty-batch clear; `finally` clear; force per-entity process for candidate so pool claims are not dropped by `batch_call_mode=1` + `entities[0]`-only consult | core |

No `src/data/database.py`, `src/utils/config.py`, consult runners, gaze_email mailbox path, statute/canon, or `CANDIDATE_DATA_MODEL.md`. Engineer does **not** edit `tests/` or bible (`orch.roles.betty-owns-test-tree`); see **Tests invalidated (Betty contract)** below for the suite delta Stage 2 causes.

## Tests invalidated (Betty contract)

Stage 2 deletes the unlocked `[ctx]` candidate arm in `_run_unified`. These two component tests pass on tip `ded4e05e` and assert that arm; after Stage 2 they fail. Builder does not touch `tests/` or bible — Betty owns the revision (`qa-child` after Code Complete).

| Item | Detail |
|------|--------|
| **Broken by tip (after Stage 2)** | `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast505_candidate_entity_routes_ctx_without_company_clear` |
| **Today (pre-Stage 2)** | `run_consult_task` awaited with entity list `[ctx]` (unlocked single-ctx path) |
| **After Stage 2** | Entity list comes from `get_new_candidate_batch`; without a claim stub the await may not happen / args are claimed rows, not raw `ctx` |
| **Broken by tip (after Stage 2)** | `tests/component/core/test_dispatcher.py::TestAst972CandidateStageDispatch::test_run_unified_candidate_claim_gate` |
| **Today (pre-Stage 2)** | `bad` ctx state → `run.assert_not_called()`; `good` → `run.await_args.args[2] == [good]` (exact `entities = [ctx] if … else []` gate) |
| **After Stage 2** | Gate is pool claim via wrappers + `dispatch_claim_states` / `batch_size`; stub `get_new_candidate_batch` (or DB claim) instead of mutating ctx state alone |

**Coverage Betty must add or extend for this ticket** (component / bible for dispatcher claim path):

1. Claim through `get_new_candidate_batch` honors `batch_size` and `dispatch_claim_states` (multi-row unclaimed pool → claimed under one `batch_id`).
2. Empty-batch path calls `clear_candidate_batch(bid)` (same early-exit site as job clear).
3. `finally` calls `clear_candidate_batch` (no more `pass`); locks released after process.
4. Multi-row claim → one `run_consult_task` call per claimed row (`use_full_batch=False`).
5. Candidate path does **not** call `clear_job_batch` / `clear_company_batch`.

## Stage 1: Core claim wrappers

**Done when:** `src/core/candidate.py` exposes `get_new_candidate_batch` and `clear_candidate_batch` with the same call shape as `tracker.get_new_job_batch` / `clear_job_batch` (minus job-only score_floor / candidate_id / claim_cap), calling `database.claim_candidate_batch` / `get_candidate_batch` / `clear_candidate_batch`. No dispatcher wiring yet.

1. In `src/core/candidate.py`, add `List` to the existing `typing` import (`Any, Dict, List, Optional, Tuple`).
2. Update the module docstring so the in-scope list names `get_new_candidate_batch` and `clear_candidate_batch` (batch claim wrappers; AST-1259).
3. After `list_candidates` (before state-transition helpers), add a `# ---- Batch API ----` section with:
   - `get_new_candidate_batch(state: str, limit: Optional[int] = None, sort_by: Optional[str] = None, batch_id: Optional[str] = None, context: Optional[str] = None, *, states: Optional[List[str]] = None) -> Tuple[str, List[Dict[str, Any]]]`:
     - Allowed states = `list(CANDIDATE_STATES.keys())`. If `states is None`, require `state in allowed` else raise `ValueError` naming the allowed list. If `states` is provided, validate **each** entry the same way (mirror `get_new_company_batch`).
     - `limit_val = limit if limit is not None else 10`.
     - If not `batch_id` and not `context`: raise `ValueError("batch_id or context is required for batch_id generation")`.
     - `bid = batch_id or f"{context}-{uuid.uuid4()}"` (uuid already imported).
     - Call `database.claim_candidate_batch(bid, state, limit_val, sort_by=sort_by, states=states)`.
     - Return `(bid, database.get_candidate_batch(bid))`.
   - `clear_candidate_batch(batch_id: str) -> int`: return `database.clear_candidate_batch(batch_id)`.
4. Do **not** add `candidate_id` / `score_floor` / `claim_cap` parameters — AST-1258 pool claim is cross-candidate; job/company scoping knobs do not apply.
5. Do **not** import these from `dispatcher.py` at module top (candidate already imports dispatcher; keep wrappers callable via late import from `_run_unified`).

⚠️ **Decision:** Wrappers live in `candidate.py` (entity owner), parallel to job→`tracker` and company→`roster`, not a new module and not inside `dispatcher.py`.

## Stage 2: Dispatcher claim → process → release

**Done when:** `_run_unified` for `entity_type=candidate` claims via `get_new_candidate_batch` (using `dispatch_claim_states` + `batch_size`), processes claimed rows, clears the lock on empty early-exit (like job) and in `finally` (no more `pass`), and never uses the unlocked `entities = [ctx] if ctx and cur in claim_states` branch.

1. In `src/core/dispatcher.py` `_run_unified`, keep the existing late imports of job/company helpers. Add a late import: `from src.core.candidate import get_new_candidate_batch, clear_candidate_batch` (same block / adjacent lines — late, not module-top).
2. Replace the candidate claim arm:
   ```python
   if entity_type == "candidate":
       claim_states = dispatch_claim_states(input_state, "candidate")
       cur = (ctx.get("state") or "").strip() if ctx else ""
       entities = [ctx] if ctx and cur in claim_states else []
   ```
   with:
   ```python
   if entity_type == "candidate":
       claim_states = dispatch_claim_states(input_state, "candidate")
       bid, entities = get_new_candidate_batch(
           input_state,
           limit=limit,
           sort_by=sort_by,
           batch_id=bid,
           states=claim_states,
       )
   ```
   Keep the job / company arms unchanged.
3. Empty-batch early exit (today clears job only): extend so candidate also clears when `bid` is set:
   ```python
   if not entities:
       if entity_type == "job" and bid:
           clear_job_batch(bid)
       elif entity_type == "candidate" and bid:
           clear_candidate_batch(bid)
       ...
   ```
   Leave company empty-path behavior unchanged (still no clear on empty).
4. In the existing `finally` block, replace `elif entity_type == "candidate": pass` with `clear_candidate_batch(bid)` (same position — after job, before company).
5. After `use_full_batch` is computed (`batch_call_mode or dispatch_task_key == "parse_job_list"`), force per-entity processing for candidate so pool claims are not silently reduced to `entities[0]` inside `consult.run_consult_task`:
   ```python
   if entity_type == "candidate":
       use_full_batch = False
   ```
   Do **not** edit `consult.py` / inflow / `run_requested_artifacts_dispatch` in this ticket.
6. Do **not** change `_dispatch_one` ledger mint (`f"{task_key}-{uuid4()}"`), gaze_email mailbox early-return, network skip, or AUTO eligibility / `count_eligible_for_dispatch_task` (AST-1258 already flipped stage Avail to the unclaimed pool).

⚠️ **Decision:** `inflow_discovery` uses the same pool claim path (ACTIVE_SEARCH via `dispatch_claim_states`). Avail still uses the inflow eligibility helper (AST-1258). Claimed ACTIVE_SEARCH rows without stale terms already no-op inside `run_inflow_discovery_batch` (“no stale search terms”) and still release in `finally` — do not invent an inflow-only claim filter here. **Accepted cross-candidate ctx:** a dispatch row owned by candidate A may claim/process candidate B; `run_inflow_discovery_batch` still reads `inflow_discovery_freq_hrs` from the row’s `ctx` (A’s cadence) while search terms come from B — cadence-only mismatch; no-stale no-op limits blast radius. Do **not** scope inflow claim to the row’s `candidate_id` in this ticket.

⚠️ **Decision:** Force `use_full_batch = False` for candidate so `_warm_then_gather` runs `run_consult_task` once per claimed row. Expanding consult to multi-entity candidate batches is out of scope; this keeps pool claim correct without touching consult.

## Stage 3: Debug contract on the claim path + smoke

**Done when:** With `debug=True`, the existing `_run_unified` Style D claim headers/details fire for candidate the same way they do after a job/company claim (found/recorded: claimed count, per-entity identifiers via `_dispatch_entity_identifier`, batch end summary). Manual smoke confirms claim → clear without editing tests. **Release logging:** Stage 2’s empty-batch and `finally` `clear_candidate_batch` sites emit nothing — same as job/company clear (AC4 / parent “recorded per step” is satisfied by the shared claim-side Style D block, not by new clear-side lines).

1. Confirm (do not duplicate) the existing post-claim debug block in `_run_unified` (claimed N / per-entity `debug_index` + `debug_detail` with Style D ` | ` prefix) runs for candidate after Stage 2 — it already keys off `entities` / `entity_type` and does not special-case candidate away. If Stage 2 somehow skips it, restore the shared path; do not add a parallel `logger.info("[DEBUG] …")` style.
2. Do **not** add gated `debug_detail` on `clear_candidate_batch` at the empty-batch or `finally` sites — release stays at job/company parity (silent clear).
3. Empty-batch debug already emits `outcome="no entities claimed"` with `batch_id={bid}` — leave it; after Stage 2 `bid` is the golden ticket used for claim.
4. Manual smoke under `debug/spikes/AST-1259/` (gitignored; do not commit) or equivalent local check:
   - ≥2 unclaimed candidates in `REQUESTED_ARTIFACTS`; run a candidate `entity_type` dispatch path (or call `get_new_candidate_batch` + `clear_candidate_batch` then a thin `_run_unified` exercise) with `batch_size=2` and `debug=True`.
   - Assert rows locked under one `batch_id`, then unlocked after clear / `finally`.
   - Empty claim (`limit` with no matching unclaimed rows) still calls `clear_candidate_batch` and does not leave locks.
5. No product commit required for smoke-only if Stages 1–2 already committed; smoke findings that need code fixes stay in Stage 2’s files.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1257/AST-1259-dispatcher-and-core-candidate-pool-claim-parity`.
- Do not add files outside **Files Changed**.
- Do not edit `src/data/database.py`, statutes, pattern catalog, CODE_RULES §2.4 wording, or `CANDIDATE_DATA_MODEL.md`.
- On ambiguity or drift: stop and comment on **parent** AST-1257 with the 🛑 Stage N blocked template.

## Self-Assessment

**Scope:** Single-Component — core only (`candidate.py` wrappers + `dispatcher.py` claim/release parity); no data/UI/config.

**Conf:** high — mirrors `get_new_job_batch` / `get_new_company_batch` and replaces a named unlocked branch; AST-1258 APIs and empty/finally clear sites are already visible in `_run_unified`.

**Risk:** Medium — wrong claim wiring can double-process or leave locks; forcing per-entity process avoids silent drop of pool rows but changes behavior vs a theoretical `batch_call_mode=1` full-batch consult path for candidate (consult was never multi-entity-aware).

## Rules check (plan vs ASTRAL_CODE_RULES)

| Rule | Plan stance |
|------|-------------|
| §2.4 claim-process-release / batch-id-first / batch-id-format | Core wrappers call data claim with batch_id first; dispatcher mints `f"{task_key}-{uuid}"` already; finally + empty clear |
| §1.5.1 debug-contract-gated | Reuse existing `_run_unified` Style D index/detail; emit only when `debug=True` |
| §3.3 import-direction | Late import core→core inside `_run_unified`; candidate wrappers call data only |
| §1.3 DRY / public-then-helpers | Wrappers grouped under Batch API; no duplicated claim SQL |
| §2.1 config SSoT | `dispatch_claim_states` + `CANDIDATE_STATES` validation; no new state lists |
| §2.6 core-decides-transitions | Claim/clear touch lock columns only; state transitions stay in existing craft/inflow runners |
| Out of scope | Data schema/eligibility (AST-1258); statute/pattern/`CANDIDATE_DATA_MODEL` (AST-1260); gaze_email non-ENTITY_TYPES mailbox; consult multi-entity rewrite |
| Betty contract / engineer test-tree ban | Stage 2 invalidates two dispatcher component tests; plan discloses node ids + after-expectation; engineer does not patch `tests/` |

## Revisions

**Revision 1 — 2026-08-07**  
Driven by: Joan `[plan-discuss] round=1 concern` (REVISE @ `ded4e05e`)  
Changes: added **Tests invalidated (Betty contract)** (fix-now — both unlocked-`[ctx]` node ids + Betty coverage list); Stage 3 states release logging stays at job/company parity / no clear-side `debug_detail` (discuss); Stage 2 inflow Decision records accepted cross-candidate `ctx` cadence for inflow (discuss).

## Review (build stub)

**Publish ref:** `origin/sub/AST-1257/AST-1259-dispatcher-and-core-candidate-pool-claim-parity`
**Tip:** `e0d18dab`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `35265641` | `get_new_candidate_batch` / `clear_candidate_batch` in `candidate.py` |
| 2 | `e0d18dab` | `_run_unified` pool claim; empty + finally clear; force per-entity process |
| 3 | (smoke) | Temp-DB claim → clear + empty clear; Style D claim path unchanged (no product delta) |
