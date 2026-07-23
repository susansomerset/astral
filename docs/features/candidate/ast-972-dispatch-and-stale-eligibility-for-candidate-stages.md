# AST-972 — Dispatch and stale eligibility for candidate stages (Candidate state machine)

**Linear:** [AST-972](https://linear.app/astralcareermatch/issue/AST-972/dispatch-and-stale-eligibility-for-candidate-stages-candidate-state)
**Parent:** [AST-871](https://linear.app/astralcareermatch/issue/AST-871/candidate-state-machine)
**Publish ref:** `origin/sub/AST-871/AST-972-dispatch-stale-eligibility`

Wire REQUESTED_RESUME / REQUESTED_ARTIFACTS so per-candidate dispatch can claim and resolve them to ready / retry / error; invoke AST-970’s stale-aging helper from the dispatcher tick; keep ACTIVE_SEARCH as the sole company/job search dispatch gate. Does not invent vocabulary, craft prompts, daisy-chain `run_next`, Topic Menu, nav remaps, or bulk `dispatch_task` FK migration (AST-973).

---

## Prerequisite (AST-970)

**Blocked by AST-970.** Before Stage 1, merge `origin/sub/AST-871/AST-970-candidate-state-registry` (or parent ftr once Ada’s registry is there) into this sub. Confirm Ada’s plan landed:

| Expectation | Source (AST-970 plan) |
|-------------|----------------------|
| `CANDIDATE_STATES` with `REQUESTED_RESUME` / `REQUESTED_ARTIFACTS` + `retry_state` / `error_state` companions | Stage 1 registry |
| Waiting states with `stale_after_hours` + `stale_state` | Stage 1 registry |
| `ACTIVE_SEARCH` in registry; `INFLOW_CONFIG["discovery"]["dispatch_trigger_state"] == "ACTIVE_SEARCH"` | Stage 1 config-local gate |
| `age_stale_candidate_states(*, now=None) -> int` in `src/core/candidate.py` | Stage 2 (helper only — no tick hook) |

If metadata keys differ from `retry_state` / `error_state` / `stale_after_hours` / `stale_state`, **stop** and comment — do not invent a parallel schema.

⚠️ **Decision:** Do **not** re-set `INFLOW_CONFIG` or re-implement `age_stale_candidate_states` here — AST-970 owns those. This ticket owns claim wiring, stage workers, eligibility split, and the tick call.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `CANDIDATE_STAGE_DISPATCH`; extend `dispatch_claim_states` for candidate; register orchestration task_keys + trigger/entity rules | utils |
| `src/data/database.py` | Branch `count_eligible_for_dispatch_task` for non-inflow candidate triggers; fix inflow eligibility docstring if still says LIVE_PROMPTS | data |
| `src/core/candidate.py` | `run_requested_resume_dispatch` / `run_requested_artifacts_dispatch` workers only (aging helper already AST-970) | core |
| `src/core/dispatcher.py` | Candidate claim gate in `_run_unified`; call `age_stale_candidate_states()` once per tick | core |
| `src/core/consult.py` | Route new candidate dispatch task_keys to stage workers (keep `inflow_discovery` → roster) | core |

**Out of scope:** rewriting `CANDIDATE_STATES` / INFLOW trigger (AST-970); history (AST-971); live DB `dispatch_task` remaps / template row upserts off `LIVE_PROMPTS` (AST-973); craft prompt content; `run_next` daisy-chain; Topic Menu; Betty tests.

---

## Stage 1: Config — stage-dispatch map + claim helpers

**Done when:** `dispatch_claim_states("REQUESTED_RESUME", "candidate")` returns primary + registry `retry_state`; `CANDIDATE_STAGE_DISPATCH` names the two orchestration task_keys and which existing craft keys they call; `_dispatch_trigger_state_for_task_key` / entity-type helpers resolve those keys to REQUESTED_* / `candidate`.

1. In `src/utils/config.py`, add `CANDIDATE_STAGE_DISPATCH` near `INFLOW_CONFIG`:

   ```python
   CANDIDATE_STAGE_DISPATCH = {
       "requested_resume": {
           "task_key": "candidate_requested_resume",
           "trigger_state": "REQUESTED_RESUME",
           "pass_state": "RESUME_READY",
           # Existing craft entry — do not edit craft_resume_base prompts/schema.
           "craft_task_key": "craft_resume_base",
       },
       "requested_artifacts": {
           "task_key": "candidate_requested_artifacts",
           "trigger_state": "REQUESTED_ARTIFACTS",
           "pass_state": "ARTIFACTS_READY",
           # Ordered list of existing craft_* keys already in TASK_CONFIG / UI generate.
           # Sequential fan-in only — not run_next daisy-chain.
           # No craft_job_title_patterns key exists; title patterns stay profile/intake.
           "craft_task_keys": [
               "craft_company_search_terms",
               "craft_joblist_rubric",
               "craft_jobdesc_rubric",
               "craft_do_rubric",
               "craft_get_rubric",
               "craft_like_rubric",
               "craft_prefilter_rubric",
           ],
       },
   }
   ```

   ⚠️ **Decision:** Dedicated orchestration task_keys (`candidate_requested_*`) — not reusing `craft_*` as `dispatch_task.task_key`. If any `craft_task_keys` string is missing from `TASK_CONFIG` at build time, **stop** and comment with actual keys.

2. In `dispatch_claim_states`, when `entity_type == "candidate"`, use `CANDIDATE_STATES` the same way job/company use theirs (prefer `retry_state` on the primary entry, else `{ts}_RETRY` if present, else `[ts]`).

3. In `_dispatch_trigger_state_for_task_key`, map:
   - `candidate_requested_resume` → `CANDIDATE_STAGE_DISPATCH["requested_resume"]["trigger_state"]`
   - `candidate_requested_artifacts` → `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["trigger_state"]`

4. In `_dispatch_entity_type_for_task_key` (or equivalent), map both new keys to `"candidate"`.

5. Add minimal `TASK_CONFIG` entries for both orchestration keys: `entity_type: "candidate"`, `trigger_state` matching step 3, `requires_candidate_key: True`, no response_schema. Ensure `dispatch_task_admin_defaults` works.

⚠️ **Decision:** Do not rewrite live `dispatch_task` rows or template-candidate DB rows — AST-973 remaps FKs / retired state keys.

**Commit message:** `code(AST-972): stage 1 — stage-dispatch config + candidate claim helpers`

---

## Stage 2: Eligibility counts + candidate claim gate

**Done when:** `inflow_discovery` eligibility still uses search-term staleness and compares candidate state to `INFLOW_CONFIG["discovery"]["dispatch_trigger_state"]` (ACTIVE_SEARCH after AST-970). For `candidate_requested_*`, count is `1` iff that candidate’s state ∈ `dispatch_claim_states(trigger, "candidate")`, else `0`. `_run_unified` yields an empty batch when ctx state is not claimable.

1. In `src/data/database.py`, if `count_candidate_inflow_discovery_eligible` docstring still says LIVE_PROMPTS, update it to say the config discovery trigger (ACTIVE_SEARCH). Leave `describe_candidate_inflow_discovery_eligibility` logic alone (already compares to `INFLOW_CONFIG`).

2. In `count_eligible_for_dispatch_task`, replace the blanket `entity_type == "candidate"` → inflow helper with:
   - `task_key == INFLOW_CONFIG["discovery"]["task_key"]` → existing inflow helper
   - `task_key` in the two `CANDIDATE_STAGE_DISPATCH[*]["task_key"]` values → load candidate; return `1` if state in `dispatch_claim_states(trigger_state, "candidate")` else `0`
   - else → `0`

3. In `src/core/dispatcher.py` `_run_unified`, for `entity_type == "candidate"`:
   - `claim_states = dispatch_claim_states(input_state, "candidate")`
   - If ctx missing or `(ctx.get("state") or "").strip()` not in `claim_states` → `entities = []`
   - Else `entities = [ctx]`
   - Keep `_dispatch_one` inflow `freq_hrs` enrichment unchanged.

⚠️ **Decision:** Keep single-candidate-per-task claim (current model). No cross-candidate `claim_candidate_batch` pool.

**Commit message:** `code(AST-972): stage 2 — candidate claim gate + eligibility split`

---

## Stage 3: Stage workers + consult routing (ready / retry / error)

**Done when:** Dispatch with `task_key=candidate_requested_resume` on a candidate in `REQUESTED_RESUME` (or retry companion) transitions to `RESUME_READY` on craft success, to registry `retry_state` on first-strike failure from primary, or to registry `error_state` when already on retry (or hard failure). Same pattern for artifacts → `ARTIFACTS_READY` / retry / error. No craft prompt or schema edits.

1. In `src/core/candidate.py`, add:

   ```python
   async def run_requested_resume_dispatch(candidate_id: str, *, debug: bool = False) -> Dict[str, int]:
   ```

   - Resolve `retry_state` / `error_state` from `CANDIDATE_STATES["REQUESTED_RESUME"]`.
   - Call existing craft path for `CANDIDATE_STAGE_DISPATCH["requested_resume"]["craft_task_key"]` via existing UI-generate / `do_task` helpers — **do not** edit prompts.
   - Success → `transition_candidate_state(candidate_id, pass_state)` (`RESUME_READY`).
   - Failure: primary → `retry_state`; already on retry → `error_state`.
   - Do not rely on `parse_candidate_resume`’s legacy `NEW → PROFILE_READY` side effect for this path — use craft+persist helpers that leave state decisions to this worker.

2. Add:

   ```python
   async def run_requested_artifacts_dispatch(candidate_id: str, *, debug: bool = False) -> Dict[str, int]:
   ```

   - Same retry/error routing from `CANDIDATE_STATES["REQUESTED_ARTIFACTS"]`.
   - For each key in `craft_task_keys` in order, invoke the existing craft runner used by UI generate; stop at first failure → retry/error.
   - All succeed → `ARTIFACTS_READY`.
   - ⚠️ **Decision:** Sequential fan-in over a config list is **not** job `run_next` daisy-chain.

3. In `src/core/consult.py` `run_consult_task`, replace blanket candidate → `run_inflow_discovery_batch` with:
   - `inflow_discovery` → existing roster batch
   - `candidate_requested_resume` → `run_requested_resume_dispatch(...)`
   - `candidate_requested_artifacts` → `run_requested_artifacts_dispatch(...)`
   - else → warning + zero summary

**Commit message:** `code(AST-972): stage 3 — requested resume/artifacts dispatch workers`

---

## Stage 4: Tick hook for AST-970 stale aging

**Done when:** Each dispatcher tick calls `age_stale_candidate_states()` once before spawning due AUTO tasks. No reimplementation of aging logic; no new auto `dispatch_task` for stale.

1. In `src/core/dispatcher.py` `_tick_loop`, at the start of each `try` body (before `get_due_tasks`), call:

   ```python
   from src.core.candidate import age_stale_candidate_states
   age_stale_candidate_states()
   ```

   (or a top-level import if already consistent with file style). Exceptions remain covered by the existing tick `except`.

⚠️ **Decision:** Tick-driven invocation (not a new dispatch task) so waiting stages age even when no REQUESTED_* row exists yet. Hours/companions stay solely on AST-970’s `CANDIDATE_STATES`.

**Commit message:** `code(AST-972): stage 4 — tick invokes candidate stale aging`

---

## Stage 5: Smoke + Code Complete note

**Done when:** Compile/lint clean on touched files; Code Complete comment maps AC5/AC6 and notes AST-973 still owns remapping live `dispatch_task.trigger_state` rows / adding REQUESTED_* rows to template candidates.

1. `python -m compileall` on edited paths; fix any issues introduced here.
2. Code Complete checklist:
   - AC5: claim gate + workers + retry/error for REQUESTED_RESUME / REQUESTED_ARTIFACTS
   - AC6: search eligibility via INFLOW trigger (ACTIVE_SEARCH from AST-970) + claim gate
   - Stale: tick calls AST-970 `age_stale_candidate_states`
   - Not here: DB remaps, nav consumers beyond what AST-970 already flipped in config, craft prompts

**Commit message:** none if Stage 4 is green — else `code(AST-972): stage 5 — lint/compile fixes`

---

## Self-Assessment

**Scope:** Single-Component — config + dispatcher/consult/candidate claim/resolve for candidate entity_type; consumes AST-970 registry; no job/company machine changes; no UI.

**Conf:** high — Ada’s AST-970 plan already names `retry_state` / `error_state` / `stale_after_hours` / `stale_state`, flips INFLOW to ACTIVE_SEARCH, and ships the aging helper; this ticket only wires claim, workers, eligibility split, and the tick call. Residual uncertainty is only which craft helpers to call without the NEW→PROFILE_READY side effect.

**Risk:** Medium — wrong claim gate could starve inflow or fire craft on the wrong state; wrong retry/error hop could strand candidates; mitigated by registry-only transitions and leaving DB remaps to AST-973.

---

## Code rules check

| Rule | Plan alignment |
|------|----------------|
| §1.4 / §2.1 config SSoT | Orchestration keys + craft lists in config; state names/hours from AST-970 registry only |
| §2.4 batch processing | Per-candidate claim; eligibility shared with count helper |
| §2.6 state machine | All hops via `transition_candidate_state`; no ad-hoc state writes in workers |
| §3.3 imports | UI untouched; core ↔ data/config; consult routes to candidate workers |
| DRY | Reuse `dispatch_claim_states`, AST-970 aging helper, existing craft runners; no second INFLOW flip |
