# AST-1478 — Report Applied and Skip (Add means to mark job as applied for)

<!-- linear-archive: AST-1478 archived 2026-09-09 -->

## Linear archive (AST-1478)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1478/report-applied-and-skip-add-means-to-mark-job-as-applied-for  
**Status at archive:** Archive  
**Project:** Astral Tracker  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-1464 — Add means to mark job as applied for  
**Blocked by / blocks / related:** parent: AST-1464

### Description

## What this implements

Add labeled Applied and Skip on `JobAnalysisReportModal`, reusing skip + candidate_action / notes plumbing (no parallel POSTs). Keep CLIENT job-link Apply separate. Does not own list-row Applied or Applied list home.

## Citations

`pattern.ui.shared-button-roles`; `astral.state.core-decides-transitions`; `astral.state.job-prior-states-enforced`; `astral.ui.naming-conventions`; `astral.standards.dry-and-focused-functions`

## Scope

- [X] `src/ui/frontend/src/components/JobAnalysisReportModal.tsx` (modified — labeled Applied + Skip)
- [X] `src/ui/frontend/src/pages/JobsRecommended.tsx` (modified — only as needed to supply skip/applied callbacks or shared hook into the modal)

## Acceptance criteria

- [X] 2. On the Job Analysis Report for such a job, labeled Applied runs the same notes + `candidate_action` path and reaches `CANDIDATE_APPLIED`.
- [X] 3. On the Job Analysis Report, labeled Skip transitions the job to `CANDIDATE_SKIPPED` (same outcome as list Skip).
- [X] 4. External job-link “Apply” (manifest `action_key: apply`) is unchanged and does not set `CANDIDATE_APPLIED`.
- [X] 5. Illegal transitions still fail with a visible error (no silent no-op).

## Boundaries

- [X] Does not own Recommended list-row Applied icon.
- [X] Does not own Applied list API/page/nav.

## Notes for planning

Labeled `.btn` roles per shared-button-roles; distinct from CLIENT apply (job_link).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### betty — 2026-08-25T00:49:09.850Z
[check-linear] Cleared [qa-handoff]: moved `describe("JobsRecommended")` close below AST-1057 (suite `beforeEach` restored); restored `AST-1477 mark applied from Recommended` from sibling sub tip. `origin/sub/AST-1464/AST-1478-report-applied-and-skip` @ `c6617b48` · assignee Hedy for resolve-child.

#### hedy — 2026-08-25T00:33:21.726Z
[qa-handoff]
@Betty White

Radia **fix-now** on AST-1478 is test-tree only — engineer cannot patch `tests/` (resolve-child §6). Staying **Review Posted**; assignee → Betty.

## What failed / what is wrong

1. **`tests/component/frontend/pages/test_JobsRecommended.test.tsx` nesting**
   - `describe("JobsRecommended")` closes at **line 335** (right after AST-1478 nested `describe`).
   - AST-1057 `it(...)` blocks at **lines 337–390** sit at file top-level (`d=0`) and **lose the suite `beforeEach`**.
   - Fix: move the closing `})` of `describe("JobsRecommended")` **below** the AST-1057 cases (as Radia wrote).

2. **AST-1477 block dropped on merge-tests tip**
   - Current publish tip lacks `describe("AST-1477 mark applied from Recommended")`.
   - Still present on `origin/sub/AST-1464/AST-1477-mark-applied-from-recommended-list` (~line 286).
   - Restore at epic merge **or** confirm AST-1477 lands separately (Radia recommended actions #2).

## Product / tip

- Product build unchanged: `d4bfa409` (report Applied/Skip via shared hook).
- Radia review docs: `06d1201c` on `origin/sub/AST-1464/AST-1478-report-applied-and-skip`.
- Betty tip cited in review: `43da07a8` merge-tests.

No product fix for me until nesting (+ optional 1477 restore) is on the publish ref and you reassign Hedy.

#### radia — 2026-08-25T00:25:15.471Z
[code-rubric] REVIEW (Commit: 43da07a8) test merge nesting fix

#### chuckles — 2026-08-25T00:25:10.959Z
[agent-busy-timeout] blocked: Cursor conversation still busy after 20m call-wait (spawn=`788a6aed`, attempts=11).
- parent: `AST-1464`
- agent: **Radia** role=review `review-child` on `AST-1478`
- AGENT_SESSION: `c1844f96-104a-48a9-9d58-26432f33d87d`

Do **not** `agent create-chat` and do **not** treat this as `[thread-missing]` — the Thread UUID is fine; another run held it.

#### betty — 2026-08-24T23:59:24.029Z
`origin/sub/AST-1464/AST-1478-report-applied-and-skip` @ `43da07a8` · report Applied Skip covered

#### hedy — 2026-08-24T23:05:55.856Z
origin/sub/AST-1464/AST-1478-report-applied-and-skip @ 4aae3fcfb1b2d3d293477265cc170c2e0ee87ceb · plan ready

#### hedy — 2026-08-24T22:51:17.508Z
`origin/sub/AST-1464/AST-1478-report-applied-and-skip` @ `4aae3fcfb1b2d3d293477265cc170c2e0ee87ceb` · plan ready

---

_Implementation detail may live in git history on `origin/dev`._
