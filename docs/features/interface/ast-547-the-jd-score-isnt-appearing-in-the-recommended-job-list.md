# AST-547 — The JD score isn't appearing in the Recommended job list.

<!-- linear-archive: AST-547 archived 2026-06-15 -->

## Linear archive (AST-547)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-547/the-jd-score-isnt-appearing-in-the-recommended-job-list  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Low / —  
**Parent:** AST-498 — Recommended Jobs List  
**Blocked by / blocks / related:** parent: AST-498

### Description

It's showing — for all JD scores, but correct 0.0 scores for DO, GET, LIKE, so I'm not sure if it's a data issue or a render issue.

### Comments

#### chuckles — 2026-06-06T05:20:15.065Z
finish-up landed `origin/dev` @ `7e3824fd`; deleted `origin/ftr/AST-547-jd-score-recommended-list`.

— Chuckles

#### chuckles — 2026-06-06T05:19:44.599Z
Betty land preflight: CLEAN — merge-tree origin/dev + origin/ftr/AST-547-jd-score-recommended-list @ d00048e6 (no bible/test conflicts).

— Chuckles (Betty gate)

#### chuckles — 2026-06-06T01:12:46.518Z
## Manual test steps

**Prerequisites:** Local `dev` @ `8fcd701b` (land-ftr). Restart app if running. Candidate with jobs in **VALID_TITLE** (no `latest_score` yet).

### AST-586 — qualify dispatch (score_floor)

1. Admin → dispatch tasks: confirm **qualify_job_listings** on trigger **VALID_TITLE** shows **is_scored** / claim behavior without score floor (admin metadata uses claim helper, not legacy scored helper).
2. Run dispatch for **qualify_job_listings** on **VALID_TITLE** — jobs should **claim** (not blocked by missing `latest_score` / default floor 1.0).
3. Confirm **PASSED_JD** / consult dispatch steps still honor **score_floor** when configured.

### AST-560 — JD score on Recommended list

4. After qualify pipeline, run **evaluate_jd** (or full consult path through JD grading).
5. Open **Recommended** jobs list — **JD** column shows numeric score when grading produced one (including **0.0**); missing score still **em dash**.
6. Spot-check DO/GET/LIKE columns unchanged.

`origin/ftr/AST-547-jd-score-recommended-list` @ `d00048e6` · local `dev` merged (§8).

Reset: `git reset --hard origin/dev`

— Chuckles

#### chuckles — 2026-06-05T23:15:55.173Z
## Git (UAT bugs — authoritative)

| Ticket | `origin/…` | Assignee | Status |
|--------|------------|----------|--------|
| AST-586 | sub/AST-547/AST-586-qualify-no-score-floor-valid-title | Hedy | Todo |

— Chuckles

#### susan — 2026-06-05T20:28:32.477Z
This is related to retesting this:  apparently the qualify_job_listings task still thinks it has a score_floor, and it doesn't.  So I can't run qualify_job_listings on "VALID_TITLE" to see if the JD score saves on evaluate_jd.

#### chuckles — 2026-06-05T20:06:17.837Z
## Manual test steps (re-prep after fix-uat)

1. Restart the app (`local dev` @ `384c0013` — `origin/ftr/AST-547-jd-score-recommended-list` merged).
2. Open **Recommended** jobs for a candidate with JD-graded jobs.
3. Confirm **JD** column shows numeric scores (including **0.0**) where grading produced a score.
4. Confirm **DO / GET / LIKE** unchanged.
5. Jobs graded before this deploy may still lack `jd_score` until re-run `evaluate_jd` (no backfill).
6. Optional: `python3 -m pytest tests/component/core/test_consult.py::TestEvaluateJdBatch tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_recommended_and_default -q`

`origin/ftr/AST-547-jd-score-recommended-list` @ `384c0013` · refresh-ftr conflicts resolved (Ada).

— Chuckles

#### susan — 2026-06-05T20:02:45.840Z
@chuckles We've had some serious repo issues clobbering each other.  If there was a fix for this, it has been overwritten in more recent repo activity.  Please work with Ada on the 560 ticket to make sure her changes are reflected in the ftr branch, then give it to Joan to make the ftr branch merge-ready with local dev so  we can prep uat again.

#### chuckles — 2026-06-03T01:33:26.860Z
## Manual test steps

1. Restart the app if it is already running (`local dev` @ merge `1c4eface` from `origin/ftr/AST-547-jd-score-recommended-list`).
2. Open **Recommended** jobs list for a candidate with jobs that have completed **JD** consult grading.
3. Confirm the **JD** column shows a numeric score (including **0.0**) where grading produced a score — not em dash for all rows.
4. Confirm **DO / GET / LIKE** columns unchanged.
5. **Known limitation (AST-560 resolve note):** Jobs JD-graded *before* this deploy may still show em dash until those jobs are re-run through `evaluate_jd` — no backfill in this epic. Re-grade one job and refresh the list to verify persistence.
6. Optional regression: `python3 -m pytest tests/component/core/test_consult.py::TestEvaluateJdBatch tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_list_recommended_and_default -q`

`origin/ftr/AST-547-jd-score-recommended-list` @ `e955e789` · local `dev` merged (§8). Child `sub/AST-547/AST-560-persist-jd-score` deleted from origin.

Reset after UAT: `git reset --hard origin/dev`

— Chuckles

#### susan — 2026-06-03T00:20:01.899Z
This is supposed to be part of the pipeline, Chuckles.  We expect betty to do one round to address qa-handoff issues if the dev can't advance the ticket to tests passed.  Make sense?  Update your skill to make this clear if necessary.

#### chuckles — 2026-06-03T00:16:25.055Z
[check-linear]

Susan — routed **AST-560** to @Betty White for the `[qa-handoff]` manifest fix (item 2); assignee updated on child. Hedy can re-run **test-astral** after Betty clears.

— Chuckles

#### susan — 2026-06-03T00:14:46.163Z
Then you should have betty fix it, please.

#### chuckles — 2026-06-03T00:06:52.793Z
@susan **AST-560** stalled at **Tests Ready** — `[qa-handoff]` on child: manifest item 2 cites removed `test_ast522_*` and wrong pytest node for `test_list_recommended_and_default`; Betty must fix bible/manifest before test-astral can pass.

— Chuckles

#### chuckles — 2026-06-02T22:30:13.043Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-547 (parent) | ftr/AST-547-jd-score-recommended-list |
| AST-560 | sub/AST-547/AST-560-persist-jd-score |

## Epic sessions (headless — Chuckles injects in every spawn; agents do not read Linear)

| Agent | Session id | Ticket | Role |
|-------|------------|--------|------|
| Joan | `5112d559-3ac6-4ff9-9a15-5ce5eb3ffcbf` | AST-547 (parent) | git |
| Hedy | `d4301c9c-d3c0-4d64-803e-990ec60bec67` | AST-560 | engineer |
| Betty | `a0d5df33-d9e2-42e0-ab09-95c9f41c2087` | AST-560 | qa |
| Radia | `c60e2a93-26a7-4327-96a2-514243d07916` | AST-560 | review |

**Parent:** AST-547

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
