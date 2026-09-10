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
