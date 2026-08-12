# AST-907 — We are not applying the "below dispatched score floor" logic to all states

<!-- linear-archive: AST-907 archived 2026-08-02 -->

## Linear archive (AST-907)

**Archived:** 2026-08-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-907/we-are-not-applying-the-below-dispatched-score-floor-logic-to-all  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Jobs that sit under a dispatch **score floor** are not eligible to be claimed for the next processing step, but they still live in a Passed / In Review database state. The Jobs UI already treats those rows as a virtual **Skipped** bucket ("Below dispatch score floor") so Susan can see the backlog that dispatch will ignore. Today that virtual bucket — and the matching exclusion from **In Review** — does not cover every state where dispatch actually applies a score floor (notably **PASSED_JOBLIST**). This epic makes the Jobs views tell the same eligibility story as dispatch: if score floor keeps a job from processing, it belongs under Skipped, not In Review.

## Functional scope

* **Align below-floor classification with dispatch eligibility.** For a selected candidate, any job whose current state is gated by that candidate's dispatch **score floor**, and whose latest score is missing or below that floor, is treated as below-floor — including **PASSED_JOBLIST** and every other In Review state where dispatch already applies a floor.
* **Skipped list.** Those below-floor jobs appear in **Jobs → Skipped** under **Below dispatch score floor**, still carrying their real database state for display context, without changing that state.
* **In Review exclusion.** The same jobs do **not** appear under **Jobs → In Review** (including the Passed Job List section and any other score-gated In Review sections).
* **Nav counts.** The In Review and Skipped nav badge counts stay consistent with the lists above (below-floor rows count toward Skipped, not In Review).

## Boundaries

* Does **not** change how dispatch claims or counts eligible jobs, how **score_floor** is stored on dispatch tasks, or **pass_threshold** grading — those rules already exist; this epic only aligns Jobs UI classification with them.
* Does **not** move jobs into a new database skip state; below-floor remains a virtual Skipped membership while the row stays in its Passed / holding state.
* Does **not** change the Scheduled Actions score-floor editor, floor option catalog, or which dispatch rows are scored vs unscored (e.g. **VALID_TITLE** still has no claim floor).
* Does **not** invent additional "not eligible" reasons beyond score floor (batch locks, empty fields, unrelated claim filters stay out of this Skipped section).
* Must not break existing below-floor behavior for states already covered (e.g. **PASSED_JD** / **PASSED_DO** / **PASSED_GET** / **CULTURE_READY** / **PASSED_LIKE**).

## Acceptance criteria

1. With a candidate that has a scored dispatch row whose trigger is **PASSED_JOBLIST** and a non-zero **score_floor**, jobs in **PASSED_JOBLIST** whose **latest_score** is null or below that floor appear under **Skipped → Below dispatch score floor** and do **not** appear under **In Review → Passed Job List**.
2. The same rule holds for every other In Review job state where that candidate's dispatch already applies a **score_floor**: below-floor jobs are in the virtual Skipped section only, not In Review.
3. Jobs at or above the applicable floor remain in **In Review** under their real state section and are absent from **Below dispatch score floor**.
4. Jobs that fail for non-floor reasons (failed / scrape-fail / candidate-skipped states, etc.) continue to use their existing real Skipped sections — unchanged.
5. In Review and Skipped nav counts match the jobs shown on each page for the selected candidate (below-floor rows counted once, under Skipped).

## Dependencies and blockers

none.

## Open questions

none.

## Proposed child tickets

| # | Working title | What it delivers | Agent | Sequencing |
| -- | -- | -- | -- | -- |
| 1 | Align Jobs below-floor views with dispatch score-floor states | Expand below-floor classification so every In Review state dispatch gates with **score_floor** (including **PASSED_JOBLIST**) is excluded from In Review, listed under **Skipped → Below dispatch score floor**, and reflected in nav counts — without changing claim math or DB states. Single vertical slice: eligibility source + Jobs list/count surfaces. | Ada | — |

**Monolith check:** Functional scope has 4 capabilities; one child is intentional — one eligibility source drives list, exclusion, and counts; splitting would force partial UAT of the same bug.

**New patterns:** none — reuse the existing virtual below-floor Skipped membership; widen which states participate so UI matches dispatch claim floor coverage.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-907 (parent) | ftr/AST-907-below-dispatch-score-floor-all-states |
| AST-908 | sub/AST-907/AST-908-align-jobs-below-floor-views |

**Epic worktree:** `astral-AST-907/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | f5485853-64ed-45e3-9b7c-d341658cfbc1 |
| Betty | qa | 8400f79e-efd4-46f0-ba3a-f328ef3fa4f3 |
| Radia | review | 1bb61f42-8dab-4b94-8910-eac85e969912 |

---

## Original brief

We currently have several jobs in "In Review" that should be in "Skipped" under "Below dispatched score floor" section in state PASSED_JOBLIST.  Score floor applies to multiple states, so the list should include all jobs that are not currently eligible for processing.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
