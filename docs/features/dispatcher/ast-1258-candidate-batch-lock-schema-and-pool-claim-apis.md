# AST-1258 — Candidate batch lock schema and pool claim APIs

**Linear:** [AST-1258](https://linear.app/astralcareermatch/issue/AST-1258/candidate-batch-lock-schema-and-pool-claim-apis-candidate-table-does)
**Parent:** [AST-1257](https://linear.app/astralcareermatch/issue/AST-1257/candidate-table-does-not-have-batch-id) — candidate table does not have batch_id
**Publish ref:** `origin/sub/AST-1257/AST-1258-candidate-batch-lock-schema-and-pool-claim-apis`

Add candidate row `batch_id` / `batch_created_at`, keep the database header inventory honest, and expose data-layer claim → get → clear with the same **pool** shape as job/company (batch_id-first, claim up to `limit` unclaimed candidates in claim states, release all on clear). Stage-task eligibility counts that unclaimed pool. Does **not** wire dispatcher or core wrappers (AST-1259) and does **not** own canon/docs text (AST-1260).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Candidate schema columns; header inventory; `claim_candidate_batch` / `get_candidate_batch` / `clear_candidate_batch`; unclaimed pool count helper; branch `count_eligible_for_dispatch_task` for non-inflow candidate stage tasks | data |

No `src/core/`, `src/utils/config.py`, dispatcher, tests/, bible, or `CANDIDATE_DATA_MODEL.md` in this ticket.

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
   - `SELECT * FROM candidate WHERE batch_id = ?`; parse each row with `_parse_candidate_row` (same as `get_candidate`).
   - Ensure schema; `_run_with_retry`.
4. Implement `clear_candidate_batch(batch_id: str) -> int`:
   - `UPDATE candidate SET batch_id = NULL, batch_created_at = NULL WHERE batch_id = ?`; return rowcount.
   - Ensure schema; `_run_with_retry`.
5. Keep public functions grouped; helpers (if any) below public APIs per §1.3 / public-then-helpers.

⚠️ **Decision:** No optional `candidate_id` filter on claim — parent requires cross-candidate pool parity with job/company claim shape, not a single-row gate. Ada (AST-1259) may pass `states=` from `dispatch_claim_states` and choose `limit` / `batch_size`; this ticket does not add core `get_new_candidate_batch`.

⚠️ **Decision:** Do not touch `claim_job_batch` / `claim_company_batch` / `set_company_batch` SQL. Shared helpers already used (`_state_in_sql`, `_run_with_retry`, `_utc_now`) are fine to call; do not refactor job/company claim bodies.

## Stage 3: Eligibility / count for candidate stage claim tasks

**Done when:** `count_eligible_for_dispatch_task` for `entity_type=candidate` still uses the inflow helper for `task_key=inflow_discovery`, and for every other candidate claim-queue task reports the count of unclaimed candidates in `dispatch_claim_states(trigger_state, "candidate")` (0 when none, all locked, or claim_states empty).

1. Add `count_candidates_unclaimed_in_states(states: List[str]) -> int` in `src/data/database.py` next to the claim APIs (or next to `count_entities_in_state`):
   - Count rows where `{state_sql}` AND `(batch_id IS NULL OR batch_id = '')`.
   - Empty `states` → raise via `_state_in_sql` (same as other count helpers) or return 0 only if the caller already guards; **prefer** matching job/company: caller passes non-empty `claim_states`.
   - Ensure schema; `_run_with_retry`.
2. In `count_eligible_for_dispatch_task`, replace the unconditional candidate branch:
   ```python
   if entity_type == "candidate":
       return count_candidate_inflow_discovery_eligible(...)
   ```
   with:
   - If `(task.get("task_key") or "").strip() == INFLOW_CONFIG["discovery"]["task_key"]` (`"inflow_discovery"`), keep `count_candidate_inflow_discovery_eligible(candidate_id, float(task.get("freq_hrs") or 0), task.get("last_run_at"))`.
   - Else if `not claim_states`: return `0`.
   - Else: return `count_candidates_unclaimed_in_states(claim_states)`.
3. Do **not** change `count_candidate_inflow_discovery_eligible` / `describe_candidate_inflow_discovery_eligibility` predicates (ACTIVE_SEARCH + stale terms).
4. Do **not** extend `count_entities_in_state` to raise-or-handle `"candidate"` unless needed for DRY; the dedicated helper is enough for this ticket. If you reuse `count_entities_in_state`, it must count the **global** unclaimed candidate pool (not filter by `task["candidate_id"]` as an owner).

⚠️ **Decision:** Stage Avail is **pool-wide** (all candidates in claim states with null/empty `batch_id`), not 0/1 for the dispatch row’s `candidate_id`. That matches parent “unclaimed pool size” / cross-candidate claim. Per-candidate dispatch rows may show the same pool size until AST-1259 wires claim; do not invent a per-row 0/1 carve-out here (overturns AST-972 “Avail always inflow for candidate entity” for non-inflow keys).

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

**Risk:** Medium — wrong eligibility branch would show incorrect Avail for candidate stage tasks or break inflow Avail; wrong unclaimed predicate would allow double-claim or leave rows stuck locked. Dispatcher still on the unlocked path until AST-1259, so production claim behavior does not flip in this ticket alone.

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
