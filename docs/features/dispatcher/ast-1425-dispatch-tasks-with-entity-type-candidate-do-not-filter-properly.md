# AST-1425 — dispatch tasks with entity_type = 'candidate' do not filter properly

<!-- linear-archive: AST-1425 archived 2026-09-09 -->

## Linear archive (AST-1425)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1425/dispatch-tasks-with-entity-type-candidate-do-not-filter-properly  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

On Scheduled Actions, dispatch tasks with `entity_type = 'candidate'` show Availability **2+**. That count includes other candidates in the same trigger state, not only the `candidate_id` bound to that row.

## To-be

A candidate-entity scheduled dispatch task always shows Availability **0 or 1**: whether *this* row's candidate is eligible. Other candidates do not add to the count.

## Proposed steps

1. Trace Scheduled Actions Avail for `entity_type=candidate` to `count_eligible_for_dispatch_task` (AST-1258 split: stage tasks count the cross-candidate unclaimed pool).
2. Scope that count to the row's own `dispatch_task.candidate_id` so Avail is 0 or 1.
3. Confirm whether dispatcher Run (AST-1259 pool claim) should stay bound to this row's candidate as well, or only the Avail number is wrong.
4. Leave job/company pool Avail and mailbox `gaze_email` bind-counts alone.

---

Scheduled dispatch tasks for candidate entity tasks must always have an Availability count of 0 or 1. Currently showing 2+ (other candidates)

### Comments

#### susan — 2026-08-19T00:17:36.389Z
1257

#### chuckles — 2026-08-18T23:55:49.989Z
Ancestor candidates (ranked). Pick one, ask about one, or reject the lot:

1. AST-1257 — candidate table does not have batch_id (Dispatcher, archived). Parent epic; AC4 required candidate stage eligibility/count to report the unclaimed *pool* size. Best match for Avail showing 2+ other candidates.
2. AST-1258 — candidate batch lock schema and pool claim APIs (child of 1257). Landed `count_eligible_for_dispatch_task` counting the cross-candidate unclaimed pool instead of the bound candidate.
3. AST-1259 — dispatcher and core candidate pool claim parity (child of 1257). Run path now pool-claims any eligible candidate; same "other candidates" shape if Run is also wrong.
4. AST-1260 — tighten claim-process-release; remove conflicting candidate law (child of 1257). Canon only — removed the single-candidate carve-out. Not the count itself.
5. AST-972 — dispatch and stale eligibility for candidate stages (Candidate / AST-871, archived). Prior single-candidate eligibility era that 1257 overturned.
6. AST-1128 — gaze_email candidate-bound dispatch (Meteorite, archived). Per-candidate Avail, but counts inbox messages (can be 2+) not other candidates — weaker unless the rows you are looking at are mailbox tasks.

---

_Implementation detail may live in git history on `origin/dev`._
