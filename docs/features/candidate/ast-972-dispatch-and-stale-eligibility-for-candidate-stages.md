# AST-972 — Dispatch and stale eligibility for candidate stages (Candidate state machine)

**Linear:** [AST-972](https://linear.app/astralcareermatch/issue/AST-972/dispatch-and-stale-eligibility-for-candidate-stages-candidate-state)
**Parent:** [AST-871](https://linear.app/astralcareermatch/issue/AST-871/candidate-state-machine)
**Publish ref:** `origin/sub/AST-871/AST-972-dispatch-stale-eligibility`

Wire REQUESTED_RESUME / REQUESTED_ARTIFACTS so per-candidate dispatch can claim and resolve them to ready / retry / error; provision the matching `dispatch_task` rows so the scheduler can select them; invoke AST-970’s stale-aging helper from the dispatcher tick; keep ACTIVE_SEARCH as the sole company/job search dispatch gate. Does not invent vocabulary, craft prompts, daisy-chain `run_next`, Topic Menu, nav remaps, or remapping retired LIVE_PROMPTS FKs (AST-973).

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

⚠️ **Decision:** Do **not** re-set `INFLOW_CONFIG` or re-implement `age_stale_candidate_states` here — AST-970 owns those. This ticket owns claim wiring, stage workers, eligibility split, **new REQUESTED_* `dispatch_task` row provisioning**, and the tick call. AST-973 remaps **existing** retired-state keys (e.g. LIVE_PROMPTS → ACTIVE_SEARCH) only — it does not own creating the new orchestration rows.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `CANDIDATE_STAGE_DISPATCH`; extend `dispatch_claim_states` for candidate; register orchestration task_keys + trigger/entity rules | utils |
| `src/data/database.py` | Branch `count_eligible_for_dispatch_task` for non-inflow candidate triggers; helper listing candidate_ids that already have any `dispatch_task` row; fix inflow eligibility docstring if still says LIVE_PROMPTS | data |
| `src/core/candidate.py` | `run_requested_resume_dispatch` / `run_requested_artifacts_dispatch` workers only (aging helper already AST-970) | core |
| `src/core/dispatcher.py` | Candidate claim gate in `_run_unified`; `ensure_candidate_stage_dispatch_tasks` + one-time provision call path; tick → `age_stale_candidate_states()` | core |
| `src/core/consult.py` | Route new candidate dispatch task_keys to stage workers (keep `inflow_discovery` → roster) | core |

**Out of scope:** rewriting `CANDIDATE_STATES` / INFLOW trigger (AST-970); history (AST-971); remapping **existing** `dispatch_task.trigger_state` values off retired names like LIVE_PROMPTS (AST-973); craft prompt content; `run_next` daisy-chain; Topic Menu; Betty tests.

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

**Commit message:** `code(AST-972): stage 1 — stage-dispatch config + candidate claim helpers`

---

## Stage 2: Provision `dispatch_task` rows (template + existing schedules)

**Done when:** `template_candidate_id()` has two rows `(candidate_requested_resume, REQUESTED_RESUME)` and `(candidate_requested_artifacts, REQUESTED_ARTIFACTS)` with fields filled from `dispatch_task_admin_defaults`; every other candidate that already had ≥1 `dispatch_task` row also has those two pairs (idempotent upsert — skip if present); candidates with zero dispatch rows are untouched (they get the keys later via Manage Candidates set-from-template once the template is seeded). AST-973 is **not** responsible for these new rows.

1. In `src/data/database.py`, add:

   ```python
   def list_candidate_ids_with_dispatch_tasks() -> List[str]:
       """Distinct candidate_id values that already own ≥1 dispatch_task row."""
   ```

2. In `src/core/dispatcher.py`, add:

   ```python
   def ensure_candidate_stage_dispatch_tasks(candidate_id: str) -> Dict[str, Any]:
   ```

   For each entry in `CANDIDATE_STAGE_DISPATCH`:
   - Resolve `task_key` / `trigger_state` from the entry.
   - If `list_dispatch_tasks_for_candidate(candidate_id)` already contains a row with that `(task_key, trigger_state)`, skip.
   - Else call `save_dispatch_task` with:
     - `candidate_id=candidate_id`
     - `task_key` / `trigger_state` from the entry (defaults fill `entity_type` / `sort_by` / `batch_call_mode` via `dispatch_task_admin_defaults`)
     - `min_count=1`, `auto_mode=True`, `batch_size=1`, `freq_hrs=0`
   - Return counts `{added, skipped}`.

3. Add:

   ```python
   def provision_candidate_stage_dispatch_tasks() -> Dict[str, Any]:
   ```

   - Call `ensure_candidate_stage_dispatch_tasks(template_candidate_id())` first (fail if template candidate missing).
   - For each id in `list_candidate_ids_with_dispatch_tasks()` (including template is fine — idempotent), call `ensure_candidate_stage_dispatch_tasks(id)`.
   - Return aggregate `{template_candidate_id, candidates_touched, added, skipped}`.

4. Invoke `provision_candidate_stage_dispatch_tasks()` once from `start_scheduler()` (same place that marks interrupted ledgers) so production picks up rows on process start without a separate migration script. Idempotent — safe on every restart.

⚠️ **Decision:** One-time-style **ensure upsert** of only the two new keys (not full `set_candidate_dispatch_tasks_from_template`, which would prune non-template extras). Existing candidates with schedules get REQUESTED_* rows; empty candidates stay empty until an operator runs set-from-template (which then copies the seeded template including these keys). AST-973 still remaps LIVE_PROMPTS→ACTIVE_SEARCH on **existing** inflow rows only.

**Commit message:** `code(AST-972): stage 2 — provision REQUESTED_* dispatch_task rows`

---

## Stage 3: Eligibility counts + candidate claim gate

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

**Commit message:** `code(AST-972): stage 3 — candidate claim gate + eligibility split`

---

## Stage 4: Stage workers + consult routing (ready / retry / error)

**Done when:** Dispatch with `task_key=candidate_requested_resume` on a candidate in `REQUESTED_RESUME` (or retry companion) transitions to `RESUME_READY` on craft success, to registry `retry_state` on first-strike failure from primary, or to registry `error_state` when already on retry (or hard failure). Same pattern for artifacts → `ARTIFACTS_READY` / retry / error. No craft prompt or schema edits.

1. In `src/core/candidate.py`, add:

   ```python
   async def run_requested_resume_dispatch(candidate_id: str, *, debug: bool = False) -> Dict[str, int]:
   ```

   Concrete craft/persist path (named — no judgment call):
   - Resolve `retry_state` / `error_state` from `CANDIDATE_STATES["REQUESTED_RESUME"]`.
   - Read `live_content` from `candidate_data.context.starting_resume_text` (same source as `parse_candidate_resume`).
   - `response = await do_task(task_key="craft_resume_base", live_content=..., index=candidate_id, ctx=candidate, debug=debug)`.
   - On success: `structure, content = split_craft_resume_base_payload(parsed)`; `database.save_candidate(..., candidate_data={"artifacts": {"resume_structure": structure, "base_resume": content}}, merge=True)` — same persist shape as the success branch inside `run_candidate_artifact_generation` for `craft_resume_base`.
   - Then `transition_candidate_state(candidate_id, pass_state)` (`RESUME_READY`).
   - On failure: primary → `retry_state`; already on retry → `error_state`.
   - **Do not** call `parse_candidate_resume` (it auto-hops `NEW → PROFILE_READY`). **Do not** call sync `run_candidate_artifact_generation` from this async worker (it uses `asyncio.run` and owns its own ledger — dispatcher already has the outer ledger).

2. Add:

   ```python
   async def run_requested_artifacts_dispatch(candidate_id: str, *, debug: bool = False) -> Dict[str, int]:
   ```

   Concrete path per craft key:
   - Same retry/error routing from `CANDIDATE_STATES["REQUESTED_ARTIFACTS"]`.
   - For each key in `craft_task_keys` in order: `await do_task(task_key=key, live_content="", index=candidate_id, ctx=candidate, debug=debug)` (empty live_content matches UI generate when content comes from tokens/ctx). Persist success the same way `run_candidate_artifact_generation` already does for that key (reuse its post-success persist branches by extracting a shared helper **only if** needed to avoid copy-paste of the craft_resume_base / rubric stash paths — prefer calling a new internal `async def _persist_craft_success(candidate_id, task_key, parsed)` lifted from the existing success block rather than inventing new storage).
   - Stop at first failure → retry/error.
   - All succeed → `ARTIFACTS_READY`.
   - ⚠️ **Decision:** Sequential fan-in of the config craft list in **one** dispatch claim is intentional (engineering cost/runtime tradeoff). Not a product open question unless Archie/Susan objects after UAT — do not split to one craft per tick in this ticket.

3. In `src/core/consult.py` `run_consult_task`, replace blanket candidate → `run_inflow_discovery_batch` with:
   - `inflow_discovery` → existing roster batch
   - `candidate_requested_resume` → `run_requested_resume_dispatch(...)`
   - `candidate_requested_artifacts` → `run_requested_artifacts_dispatch(...)`
   - else → warning + zero summary

**Commit message:** `code(AST-972): stage 4 — requested resume/artifacts dispatch workers`

---

## Stage 5: Tick hook for AST-970 stale aging

**Done when:** Each dispatcher tick calls `age_stale_candidate_states()` once before spawning due AUTO tasks. No reimplementation of aging logic; no new auto `dispatch_task` for stale.

1. In `src/core/dispatcher.py` `_tick_loop`, at the start of each `try` body (before `get_due_tasks`), call:

   ```python
   from src.core.candidate import age_stale_candidate_states
   age_stale_candidate_states()
   ```

   (or a top-level import if already consistent with file style). Exceptions remain covered by the existing tick `except`.

⚠️ **Decision:** Tick-driven invocation (not a new dispatch task) so waiting stages age even when no REQUESTED_* task is due. Hours/companions stay solely on AST-970’s `CANDIDATE_STATES`.

**Commit message:** `code(AST-972): stage 5 — tick invokes candidate stale aging`

---

## Stage 6: Smoke + Code Complete note

**Done when:** Compile/lint clean on touched files; Code Complete comment maps AC5/AC6 including that template + scheduled candidates now have REQUESTED_* `dispatch_task` rows; AST-973 still owns remapping **retired** trigger_state values (LIVE_PROMPTS → ACTIVE_SEARCH) on existing inflow rows only.

1. `python -m compileall` on edited paths; fix any issues introduced here.
2. Code Complete checklist:
   - AC5: provisioned rows + claim gate + workers + retry/error for REQUESTED_RESUME / REQUESTED_ARTIFACTS
   - AC6: search eligibility via INFLOW trigger (ACTIVE_SEARCH from AST-970) + claim gate
   - Stale: tick calls AST-970 `age_stale_candidate_states`
   - Not here: LIVE_PROMPTS→ACTIVE_SEARCH remaps of existing inflow rows (AST-973), craft prompts

**Commit message:** none if Stage 5 is green — else `code(AST-972): stage 6 — lint/compile fixes`

---

## Self-Assessment

**Scope:** Single-Component — config + dispatcher/consult/candidate claim/resolve + dispatch_task provisioning for candidate entity_type; consumes AST-970 registry; no job/company machine changes; no UI.

**Conf:** high — Ada’s AST-970 plan already names companions / stale metadata / INFLOW flip / aging helper; Joan’s fix-now closes the AC#5 gap by owning template + existing-schedule row upserts here; craft path is named (`do_task` + `split_craft_resume_base_payload` / existing persist branches).

**Risk:** Medium — wrong claim gate could starve inflow or fire craft on the wrong state; ensure-upsert with `auto_mode=True` could wake empty REQUESTED_* queues until eligibility returns 0 (acceptable); mitigated by registry-only transitions and leaving retired-key remaps to AST-973.

---

## Code rules check

| Rule | Plan alignment |
|------|----------------|
| §1.4 / §2.1 config SSoT | Orchestration keys + craft lists in config; state names/hours from AST-970 registry only |
| §2.4 batch processing | Per-candidate claim; eligibility shared with count helper; rows via `save_dispatch_task` + admin defaults |
| §2.6 state machine | All hops via `transition_candidate_state`; no ad-hoc state writes in workers |
| §3.3 imports | UI untouched; core ↔ data/config; consult routes to candidate workers |
| DRY | Reuse `dispatch_claim_states`, AST-970 aging helper, existing craft/persist helpers; no second INFLOW flip |

---

## Revisions

### Revision 1 — 2026-07-23

Driven by: Joan `[plan-discuss] round=1 concern` fix-now — plan wired TASK_CONFIG/claim/workers but refused to create live `dispatch_task` rows for `candidate_requested_*`, parking that on AST-973; without rows AC#5 is unmet because `get_due_tasks` never selects the new keys.

Changes:
- Added **Stage 2** provisioning: `ensure_candidate_stage_dispatch_tasks` + `provision_candidate_stage_dispatch_tasks` (template first, then every candidate with an existing schedule); idempotent upsert via `dispatch_task_admin_defaults` / `save_dispatch_task`; invoke from `start_scheduler`.
- Clarified AST-973 owns **retired** trigger remaps only (LIVE_PROMPTS→ACTIVE_SEARCH), not new REQUESTED_* orchestration rows.
- Named concrete craft helpers in Stage 4 (`do_task`, `split_craft_resume_base_payload`, persist shape from `run_candidate_artifact_generation`; no `parse_candidate_resume` / no nested `asyncio.run`).
- Renumbered former stages 2–5 → 3–6; updated Files Changed, Out of scope, Self-Assessment Conf, Stage 6 CC note.

## Review

| Commit | Note |
|--------|------|
| `dfa30c6` on `sub/AST-871/AST-972-dispatch-stale-eligibility` | Code Complete — build-child AST-972 |
