# Align Jobs below-floor views with dispatch score-floor states

**Linear:** [AST-908](https://linear.app/astralcareermatch/issue/AST-908/align-jobs-below-floor-views-with-dispatch-score-floor-states-we-are)  
**Parent:** [AST-907](https://linear.app/astralcareermatch/issue/AST-907/we-are-not-applying-the-below-dispatched-score-floor-logic-to-all)  
**Publish ref:** `sub/AST-907/AST-908-align-jobs-below-floor-views`

Expand Jobs UI below-floor classification so every In Review state that `dispatch_claim_uses_score_floor` already gates (including **PASSED_JOBLIST**) is excluded from In Review, listed under **Skipped → Below dispatch score floor**, and reflected in nav counts — without changing claim math, DB states, or score-floor storage.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | `score_floor_by_trigger_for_candidate` and `list_jobs_below_dispatch_score_floor` gate on `dispatch_claim_uses_score_floor` instead of `PASSED_SCORE_GATED_STATES` membership | data |
| `src/utils/config.py` | Comment only: document that Jobs UI floors follow `dispatch_claim_uses_score_floor` (includes **PASSED_JOBLIST** via `_TRANSITION_STATES_USED_BY_SCORED_TASKS`), not `PASSED_SCORE_GATED_STATES` alone | utils |

**Out of scope (this ticket):** `src/core/dispatcher.py` claim/count paths; `score_floor` persistence / admin Scheduled Actions editor; `pass_threshold` grading; expanding `PASSED_SCORE_GATED_STATES` (would change `_dispatch_sort_by_for` claim sort for **PASSED_JOBLIST** — claim math boundary); frontend pages (`api_jobs` / `api_system` / `JobsSkipped` already consume the floors helpers); `tests/` and `docs/test-bible/**` (Betty owns those after Code Complete).

---

## Stage 1: Align floors map with claim score-floor gate

**Done when:** For a candidate with a job `dispatch_task` whose `trigger_state` is **PASSED_JOBLIST** and a non-null/`NULL→1.0` `score_floor`, `score_floor_by_trigger_for_candidate(candidate_id)` includes key `"PASSED_JOBLIST"`. `list_jobs_below_dispatch_score_floor` returns **PASSED_JOBLIST** jobs whose `latest_score` is null or below that floor. Existing floors for **PASSED_JD** / **PASSED_DO** / **PASSED_GET** / **CULTURE_READY** / **PASSED_LIKE** are unchanged in membership rules (still claim-gated). `VALID_TITLE` / `JD_READY` still never appear in the floors map. `python3 -m py_compile` passes on the two touched files.

1. In `src/data/database.py`, function `score_floor_by_trigger_for_candidate` (~1912–1929):

   - Keep the candidate_id / `entity_type == "job"` filters and the max-floor-wins merge unchanged.
   - Replace the gate:

     ```python
     if not ts or ts not in PASSED_SCORE_GATED_STATES:
         continue
     task_key = t.get("task_key") or ""
     is_scored = trigger_state_used_by_scored_dispatch_task(ts)
     if not is_scored:
         continue
     ```

     with:

     ```python
     if not ts or not dispatch_claim_uses_score_floor(ts):
         continue
     ```

   - Keep the effective floor line exactly as today:

     ```python
     eff = float(t["score_floor"]) if t.get("score_floor") is not None else 1.0
     floors[ts] = max(floors.get(ts, eff), eff)
     ```

   - Update the function docstring to say floors cover every job trigger where `dispatch_claim_uses_score_floor` is True (not only `PASSED_SCORE_GATED_STATES`).

   - `dispatch_claim_uses_score_floor` is already imported from `src.utils.config` in this module (~84). Do **not** remove the `PASSED_SCORE_GATED_STATES` or `trigger_state_used_by_scored_dispatch_task` imports if other call sites in the file still use them; only drop unused names if a post-edit grep shows they are unused in `database.py`.

2. In `src/data/database.py`, function `list_jobs_below_dispatch_score_floor` (~1970–1979):

   - Replace:

     ```python
     states = [s for s in floors if s in PASSED_SCORE_GATED_STATES]
     ```

     with:

     ```python
     states = list(floors.keys())
     ```

     (`floors` is already claim-gated by step 1; do not re-filter through `PASSED_SCORE_GATED_STATES`.)

   - Update the docstring: below-floor rows are jobs in any claim-gated floor state (including **PASSED_JOBLIST**), not only PASSED_JD / PASSED_DO / PASSED_GET.

3. In `src/utils/config.py`, immediately above `PASSED_SCORE_GATED_STATES` (~1265–1270), extend the existing comment block so it states:

   - `PASSED_SCORE_GATED_STATES` remains the consult PASSED_* / CULTURE_READY set used for claim-sort (`_dispatch_sort_by_for`) and related helpers.
   - Jobs UI below-floor membership (`score_floor_by_trigger_for_candidate`) uses **`dispatch_claim_uses_score_floor`**, which also returns True for transition outcomes such as **PASSED_JOBLIST** via `_TRANSITION_STATES_USED_BY_SCORED_TASKS` (AST-908). Do **not** add **PASSED_JOBLIST** to `PASSED_SCORE_GATED_STATES` in this ticket.

4. Do **not** edit `job_misses_dispatch_score_floor`, `count_jobs_below_dispatch_score_floor`, `api_jobs.py`, `api_system.py`, `tracker.py` facades, or any React file — they already key off the floors map / list helpers.

5. Run:

   ```bash
   /home/susan/astral/.venv/bin/python -m py_compile src/data/database.py src/utils/config.py
   ```

⚠️ **Decision:** Gate the floors map with `dispatch_claim_uses_score_floor(ts)` rather than expanding `PASSED_SCORE_GATED_STATES`. Expanding the frozenset would also flip `_dispatch_sort_by_for("job", "PASSED_JOBLIST")` from `updated_at` to `latest_score`, which is claim-path behavior and is out of ticket Boundaries. UI alignment only needs the floors helper to match the claim gate helper.

⚠️ **Decision:** Drop the nested `trigger_state_used_by_scored_dispatch_task` check inside `score_floor_by_trigger_for_candidate`. It is redundant once the loop uses `dispatch_claim_uses_score_floor` (AST-586 / AST-617 claim semantics), and keeping both would still exclude nothing that claim includes for current In Review states. Verified at plan time: the only In Review state with `dispatch_claim_uses_score_floor` True outside `PASSED_SCORE_GATED_STATES` is **PASSED_JOBLIST**.

⚠️ **Decision:** No frontend or API route changes. `list_view` in_review / skipped and `_get_job_counts` already filter/annotate via `job_misses_dispatch_score_floor` / `list_jobs_below_dispatch_score_floor` / `count_jobs_below_dispatch_score_floor`. Fixing the floors source satisfies AC 1–5 in one place.

---

## Execution contract

- Execute steps in order within the stage; do not skip, reorder, combine, or expand.
- Do not add files, modules, configs, or dependencies not listed above.
- On ambiguity, drift, or literal failure: stop, comment on the **parent** Linear issue (AST-907) with the Stage-blocked template, and wait.

## Self-Assessment

**Scope:** Single-Component — one data-layer floors helper (+ list filter) and a config comment; UI surfaces already wired.

**Conf:** high — root cause is the `PASSED_SCORE_GATED_STATES` membership check in `score_floor_by_trigger_for_candidate`; claim already treats **PASSED_JOBLIST** as score-floor gated via `dispatch_claim_uses_score_floor`.

**Risk:** Medium — wrong floors membership would mis-count nav badges and hide/show In Review rows; mitigated by reusing the existing claim helper and leaving claim/sort code paths untouched.

## Rules check (ASTRAL_CODE_RULES)

- §1.3 DRY: reuse `dispatch_claim_uses_score_floor`; do not duplicate a second state list for UI floors.
- §1.4 / §2.1: config remains source of truth for claim-floor membership; UI floors map reads that helper; pass_threshold vs score_floor stay distinct (no grading changes).
- §2.4 / §2.6: no batch claim, no state-machine transitions, no new DB skip state.
- §3.3 imports: only use already-imported `dispatch_claim_uses_score_floor` in `database.py`; no new cross-layer imports.
- §3.5 naming: keep existing function names; docstring wording only.

No conflicts requiring `conf-!!-NONE`.

## Review (build)

**Built:** `origin/sub/AST-907/AST-908-align-jobs-below-floor-views` @ `6404d4187471454f59f3fbd86d472a9326a5034b`

Stage 1: `score_floor_by_trigger_for_candidate` gates on `dispatch_claim_uses_score_floor` (includes **PASSED_JOBLIST**); `list_jobs_below_dispatch_score_floor` lists all floors keys; config comment documents UI vs `PASSED_SCORE_GATED_STATES`. Tests deferred to Betty.

## Review

**Radia** · `origin/dev`…`origin/sub/AST-907/AST-908-align-jobs-below-floor-views` @ `63dd83a` · product `6404d41` (`src/data/database.py`, `src/utils/config.py` comment)

### What's solid

- **Plan fidelity:** Stage 1 matches. Floors map gates on `dispatch_claim_uses_score_floor(ts)` (drops redundant `PASSED_SCORE_GATED_STATES` + `trigger_state_used_by_scored_dispatch_task`); `list_jobs_below_dispatch_score_floor` uses `list(floors.keys())`; config comment documents UI vs claim-sort set without adding **PASSED_JOBLIST** to `PASSED_SCORE_GATED_STATES`. Unused imports removed. No dispatcher / API / React / claim-math edits.
- **§1.3 / §1.4 / §2.1 / §3.3:** Reuses existing claim helper; config remains membership source of truth; pass_threshold vs score_floor untouched; no new cross-layer imports.
- **Self-Assessment:** Diff footprint matches **Single-Component**; high Conf justified; Medium risk mitigated by shared claim gate.
- **Betty coverage:** `TestAst908BelowDispatchScoreFloorViews` covers PASSED_JOBLIST floors + list/count; legacy VALID_TITLE graded assert rewritten post-AST-898 — bible matches.

### Issues

None (no fix-now / discuss).

### Advisory (not fix-now)

- `count_jobs_below_dispatch_score_floor` docstring still says “PASSED_* jobs”; behavior already iterates all floors keys (including **PASSED_JOBLIST**). Cosmetic only.

### Recommended actions

| Action | Owner | Notes |
|--------|-------|-------|
| _(none)_ | — | Clean — ready for resolve-child / merge-child rollup |

## Resolution

**2026-07-22** · `resolve(AST-908)` — Radia review clean (0 fix-now / 0 discuss).

- **Advisory addressed:** `count_jobs_below_dispatch_score_floor` docstring updated to claim-gated floor states (not “PASSED_*” only) — matches floors-map behavior including **PASSED_JOBLIST**.
- No product logic changes beyond that docstring.
