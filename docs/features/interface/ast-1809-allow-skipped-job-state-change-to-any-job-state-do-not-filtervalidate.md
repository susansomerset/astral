# AST-1809 — Allow Skipped Job state change to ANY job state, do not filter/validate

<!-- linear-archive: AST-1809 archived 2026-10-07 -->

## Linear archive (AST-1809)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1809/allow-skipped-job-state-change-to-any-job-state-do-not-filtervalidate  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

When a job is in a Skipped state, the Job Detail state dropdown only lists the states that the prior-state rules allow from the current state. That list comes from `legal_job_successor_states`, which is built into `fields_editable` / `legal_next_states` on `GET /api/jobs/<id>`. On save, `PUT /api/jobs/<id>` runs through `persist_skipped_job_edits` → `transition_job_state`, which checks `prior_states` again. Any target outside those rules gets a 409 `Invalid transition`. This behavior came from AST-1446 / AST-1453, whose Boundaries said: "Does not waive prior-state law."

## To-be

For a job in a Skipped state, the operator can move it to **any** registered job state (every `JOB_STATES` key other than the current state). The only filter is the entity type: job states only, not candidate or meteorite states, and not runtime dispatch-hop labels. There is no prior-state validation on this path. The move still goes through the normal transition write, so `state_history` and `state_changed_at` are recorded. The prior-state rules stay exactly as they are for every other caller (dispatcher, bulk Retry, Skip, chain graduation).

## Proposed steps

1. In `src/core/tracker.py`, change the successor list used by Skipped-job editing so it returns every `JOB_STATES` key except the current state, with no `_job_state_matches_prior` filter.
2. Give `transition_job_state` a keyword-only opt-out for the prior-state check. It defaults to enforcing, so all current callers are unchanged. The registered-state check (`is_registered_state`) stays on.
3. Have `persist_skipped_job_edits` call `transition_job_state` with that opt-out. The skipped-state gate on the *current* state stays, so non-skipped jobs are still read-only.
4. No UI change should be needed. `JobDetailModal.tsx` already renders whatever `legal_next_states` the API returns. Confirm this and leave it alone.
5. Canon: this deliberately waives `astral.state.job-prior-states-enforced` for one operator path. Expect fix-board (Joan) to flag it. The statute likely needs a narrow, named exception for the operator skipped-job override.

## Component scope

* `src/core/tracker.py` — modified. It owns the successor list that feeds the dropdown, the skipped-edit persist, and the prior-state check in `transition_job_state`, so all three changes live here.
* `src/ui/api/api_jobs.py` — probably untouched. `_attach_skipped_edit_meta` and the PUT handler should pick up the wider list with no changes. Listed only in case the successor function is renamed or split and the import has to follow.

## Technical scope

* `src/core/tracker.py`:
  * **Modified function:** the successor-list function, `legal_job_successor_states` or a new sibling just for skipped editing. It should return every registered job state except the current one, so the dropdown stops filtering.
  * **Modified function:** `transition_job_state` gets a keyword-only flag that skips the `prior_states` check. The default keeps enforcement, so other callers are unaffected.
  * **Modified function:** `persist_skipped_job_edits` passes that flag, so the operator's chosen state is accepted as long as it is a registered job state.
* `src/ui/api/api_jobs.py`: no function-level change expected. At most, an import rename if the successor function is renamed.

## Ancestor candidates

- [ ] AST-1453 — Persist skipped-job field and state edits (`docs/features/interface/ast-1453-persist-skipped-job-field-and-state-edits.md`). Owns `legal_job_successor_states`, `persist_skipped_job_edits`, and the "no waived jumps" decision this bug reverses.
- [ ] AST-1446 — When a job is in a Skipped state, make all fields editable (parent epic, `docs/features/interface/ast-1446-when-a-job-is-in-a-skipped-state-make-all-fields-editable.md`). Its Boundaries line "Does not waive prior-state law" is the product rule being changed.
- [ ] AST-1454 — Job detail skipped field editors (`docs/features/interface/ast-1454-job-detail-skipped-field-editors.md`). The UI state `<select>` over `legal_next_states`. Probably no code change, but it is the visible surface.
- [ ] AST-77 — Record state transitions (`docs/features/tracker/ast-77-record-state-transitions.md`). The origin of `transition_job_state` and its validation contract.

---

**Original brief (Susan):**

Should not be filtered beyond the entity type.

### Comments

#### chuckles — 2026-09-27T01:33:48.430Z
@susan finish-up held — PR #158 carries 3 unlanded `origin/tests` commits via AST-1812's merge-tests (telescope/roster/meteorite suites) that add 53 component reds on dev (0 in tracker/api_jobs; AST-1809's own product diff is `src/core/tracker.py` + the statute). Merge as-is, or land those tests' product first? Move to PR Ready + assign Chuckles to land.

---

_Implementation detail may live in git history on `origin/dev`._
