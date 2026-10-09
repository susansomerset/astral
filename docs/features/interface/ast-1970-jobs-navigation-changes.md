# AST-1970 — Jobs Navigation changes

<!-- linear-archive: AST-1970 archived 2026-10-08 -->

## Linear archive (AST-1970)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1970/jobs-navigation-changes  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The Jobs sidebar still follows the pipeline's internal shape (In Review, Recommended, Skipped, a dead Responded stub) instead of the questions a candidate actually asks: what's ready to send, what should I look at, what have I applied to, what's still cooking, what's been dropped, and what happened to the listings I forwarded. Today's lists also leak. `BUILD_FAILED`, `ERROR_BUILD_ARTIFACTS`, and mid-chain `BUILD_ARTIFACTS.<task>` jobs show on no list, and the Applied view errors for real candidates. This epic re-cuts the Jobs nav into six lists that between them show every job exactly once. The candidate can drop any in-flight job, which also covers cancelling a running build, and the app opens on the first list with something on it.

## Functional scope

1. **Ready** lists the candidate's jobs in `CANDIDATE_REVIEW` (artifacts built, ready to apply).
2. **Review** lists jobs in `RECOMMENDED` (upshot done, candidate decides whether to generate artifacts). Ready and Review keep today's Recommended table: row and bulk actions, the Analysis toggle, phase scores, and Total. Meteorite-track jobs sit inline with the rest, flagged by a new **Source** column; the separate Meteorites sub-section goes away.
3. **Applied** lists `CANDIDATE_APPLIED`, `CANDIDATE_INTERVIEW`, `CANDIDATE_REJECTED`, and `CANDIDATE_GHOSTED`, and loads without error for every candidate.
4. **Processing** lists every job not on Ready, Review, Applied, or Skipped. That covers all in-pipeline states, retry holds, the artifact build (`BUILD_ARTIFACTS`), and its hop-labeled mid-chain states. Rows are grouped by state and open the Job Detail modal, as In Review does today.
5. **Skip from Processing.** The candidate can Skip any Processing job from its Job Detail modal (the existing Skip button), which moves it to `CANDIDATE_SKIPPED`. Skipping a running artifact build is the cancel. A job claimed by an in-flight batch has its claim released on skip.
6. **Skipped** lists the terminal states: today's Skipped set, the below-dispatch-score-floor virtual skips, plus `ERROR_BUILD_ARTIFACTS` and `BUILD_FAILED`. Skipped jobs stay editable (fields + state), as they are today. Resurrect is unchanged (→ `CANDIDATE_REVIEW`). To send a job skipped from Processing back into the pipeline, the candidate edits its state in the Skipped modal.
7. **Meteorites** keeps listing every meteorite staging row in any state. Each landed row also shows its job's **current** job state and a link that opens that job's report modal on the Meteorites page.
8. **Nav.** The order is exactly Ready, Review, Applied, Processing, Skipped, Meteorites. In Review, Recommended, and Responded are removed. All six show count badges, which must match their lists.
9. **Landing page.** `/`, unknown URLs, and every place that used to send the user to Recommended now land on the first Jobs list, in nav order, whose count is above zero. If all six are empty, it lands on Ready.

## Component scope

* `src/utils/config.py` — **modified** — Jobs `NAV_CONFIG` items; Ready / Review state lists; Skipped list + section order / labels / bulk-retry targets gain the two build-failure states; a disjointness guard over the four explicit lists; `CANDIDATE_SKIPPED` prior states widened; state-UI manifest jobs block (Processing sections, Ready / Review sections, meteorite sub-section entry removed); Meteorites list columns gain the landed-job state column.
* `src/data/database.py` — **modified** — job list/count can exclude a state set; meteorite list read returns the landed job's current state.
* `src/core/tracker.py` — **modified** — `list_jobs` / `count_jobs` facades pass the exclusion through; candidate skip releases a held batch claim.
* `src/ui/api/api_jobs.py` — **modified** — `view=ready|review|processing` replace `in_review|recommended|responded`; Applied repair-on-read loop removed; skip route calls the core skip.
* `src/ui/api/api_system.py` — **modified** — Jobs nav counts for all six paths.
* `src/ui/api/api_meteorite.py` — **modified** — list projection carries the landed job's state.
* `src/ui/frontend/src/routes.tsx` — **modified** — new Jobs routes, old ones removed, index + catch-all go through the landing redirect.
* `src/ui/frontend/src/components/JobsHomeRedirect.tsx` — **new** — resolves the first non-empty Jobs list and redirects there.
* `src/ui/frontend/src/pages/JobsRecommended.tsx` — **modified** — one list component serving Ready and Review by view, with a Source column.
* `src/ui/frontend/src/pages/JobsProcessing.tsx` — **new** — the Processing list (successor to In Review).
* `src/ui/frontend/src/pages/JobsInReview.tsx` — **deleted** — superseded by Processing.
* `src/ui/frontend/src/pages/JobsResponded.tsx` — **deleted** — dead stub.
* `src/ui/frontend/src/contexts/StateUiContext.tsx` — **modified** — manifest type follows the new jobs block.
* `src/ui/frontend/src/pages/JobsJobDetail.tsx` — **modified** — fallback / close target is the landing route.
* `src/ui/frontend/src/components/AdminRoute.tsx` — **modified** — non-admin redirect target is the landing route.
* `src/ui/frontend/src/pages/CandidateSurferConsent.tsx` — **modified** — post-consent navigate target is the landing route.
* `src/ui/frontend/src/pages/JobsMeteorites.tsx` — **modified** — landed-job state column + in-page job modal link.
* `tests/component/frontend/pages/test_JobsInReview.test.tsx` — **deleted** — covers the deleted page (Betty replaces it with Processing coverage).
* `tests/component/frontend/pages/test_JobsResponded.test.tsx` — **deleted** — covers the deleted stub.
* `docs/test-bible/frontend/pages.md` — **modified** — retire In Review / Responded entries.

## Technical scope

* `config.py`
  * **State lists.** New Ready and Review state lists (`CANDIDATE_REVIEW`; `RECOMMENDED`). The existing Applied and Skipped lists are reused, and Skipped gains `ERROR_BUILD_ARTIFACTS` and `BUILD_FAILED`, with section labels and bulk-retry targets (`RECOMMENDED`, `CANDIDATE_REVIEW` — each state's only legal successor). A module-level assert keeps the four explicit lists pairwise disjoint. **Processing gets no typed-out state list:** it is the complement of the other four.
  * **Skip legality.** `CANDIDATE_SKIPPED`'s `prior_states` widen to every job state outside the Applied and Skipped lists. That list is **derived** from those lists, not typed out, and hop labels already resolve through their base.
  * **Nav and manifest.** The Jobs nav items are replaced. The manifest jobs block carries Processing sections (today's in-review sections plus the build-in-progress state) and Ready / Review sections, and drops the recommended `meteorite_section` entry and its backing constant. The recommended primary-action table keeps its `BUILD_ARTIFACTS` Cancel entry, because the report modal still uses it.
  * **Meteorites columns.** The Meteorites list column config gains one column for the landed job's state.
* `database.py` — job list and count functions gain an optional excluded-state filter, as `list_companies` already has. The candidate meteorite list read also returns each row's landed job's current state, via `astral_job_id`.
* `tracker.py` — job list/count facades forward the new filter. A new core skip function clears the job's batch lock when one is held (as `cancel_artifact_build` does), then transitions to `CANDIDATE_SKIPPED`.
* `api_jobs.py` — the list route's view switch is modified: new `ready`, `review`, `processing` branches (Processing = exclusion of the four lists, minus below-floor rows, which stay Skipped-only), with `in_review`, `recommended`, and `responded` removed. The Applied helper's company-linkage repair loop is deleted. It calls `list_jobs` with no candidate, which raises since AST-1598, and `job.candidate_id` scoping makes it redundant. The skip route delegates to the core skip function instead of transitioning directly.
* `api_system.py` — the Jobs nav-count function is modified to emit counts for all six paths: Ready, Review, Applied, Processing (below-floor subtracted), Skipped (below-floor added), and Meteorites (candidate's meteorite rows).
* `api_meteorite.py` — the list projection's key set is modified to include the landed job's state.
* `routes.tsx` — the Jobs route table is modified, and the index + catch-all render the landing redirect.
* `JobsHomeRedirect.tsx` — a new component. It reads the resolved nav for the selected candidate and navigates to the first Jobs item with `count > 0`, falling back to the first Jobs item. It is the only place the landing choice is made.
* `JobsRecommended.tsx` — the page component is modified to take its view (ready / review) and title from the route, fetch that view, drop the meteorite-prefix sub-section split, and add a sortable Source column showing the job's stored `source` (`—` when null).
* `JobsProcessing.tsx` — a new page component: a state-sectioned list over `view=processing`, sections from the manifest with the existing legacy-state fallback for hop labels, and rows opening `JobDetailModal` (whose existing Skip button now succeeds on these states).
* `StateUiContext.tsx` — the manifest TS interface is modified to match.
* `JobsJobDetail.tsx`, `AdminRoute.tsx`, `CandidateSurferConsent.tsx` — the hard-coded `/jobs/recommended` target is modified to `/`, the landing route.
* `JobsMeteorites.tsx` — the page component is modified: a landed-job state column, and the job cell opens `JobAnalysisReportModal` in place, with the row click still opening `MeteoriteDetailModal`.

## Architectural definition

* **Patterns to reuse** — `no established pattern applies`. None of the 21 in-force directives (`canon_clerk.py index`) is a UI or nav pattern. The draft `patt.ui.*`, `stat.config.derive-dont-restate`, and `stat.core.decides-transitions` are not in force and are not cited as law, though this definition follows their spirit by deriving Processing and skip legality and by putting the skip decision in core.
* **New patterns proposed** — none.
* **Applicable statutes**
  * `stat.logging.info.api` — [canon/directives/active/stat.logging.info.api.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.api.md>) — the changed list / nav / meteorite routes are idempotent GETs and add **no** `logger.info`. The skip POST route is modified, so it emits the one completion line `<candidate_id> | api /api/jobs/<id>/skip completed: POST <status>` at the route, and core adds none.
  * `stat.logging.error` — [canon/directives/active/stat.logging.error.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>) — the meteorite list route's existing exception handler wraps the new landed-state read, and it stays one `logger.exception` with live facts and no re-raise.

**Canon Scope:** `stat.logging.info.api`, `stat.logging.error` — locked at Discussion.

## Acceptance criteria

 1. **Nav shape.** `GET /api/nav_config` Jobs group item labels are exactly `["Ready","Review","Applied","Processing","Skipped","Meteorites"]`, with paths `/jobs/ready`, `/jobs/review`, `/jobs/applied`, `/jobs/processing`, `/jobs/skipped`, `/jobs/meteorites`, and every item carries a `count`. **Fail:** In Review / Recommended / Responded present, any other label or order, or a missing `count`.
 2. **Ready.** `GET /api/jobs?view=ready&candidate_id=X` returns only `state == "CANDIDATE_REVIEW"` rows, and its length equals `SELECT COUNT(*) FROM job WHERE candidate_id='X' AND state='CANDIDATE_REVIEW'`. **Fail:** any other state, or count mismatch.
 3. **Review.** Same check for `view=review` and `RECOMMENDED`. **Fail:** as above.
 4. **Applied loads.** `GET /api/jobs?view=applied&candidate_id=X` for a real candidate returns 200 containing only the four Applied states. `rg -n "candidate_id=None" src/ui/api/api_jobs.py` returns nothing. **Fail:** 500 / ValueError, any other state, or the grep hits.
 5. **Skipped is terminal and editable.** A job in `ERROR_BUILD_ARTIFACTS` appears in `view=skipped`, and `GET /api/jobs/<id>` returns `fields_editable: true` with `RECOMMENDED` in `legal_next_states`. Below-floor virtual rows still appear in Skipped only. **Fail:** the job missing from Skipped, not editable, or a below-floor row also in Processing.
 6. **Every job exactly once.** For candidate X, the union of `astral_job_id`s across the ready, review, applied, processing, and skipped views has no duplicates, and its size equals `SELECT COUNT(*) FROM job WHERE candidate_id='X'`. A job seeded at `BUILD_ARTIFACTS.<any chain task>` appears in Processing. **Fail:** any duplicate, any job on no list, or the hop-labeled job missing.
 7. **Lists can't overlap; nothing typed twice.** Temporarily adding `"CANDIDATE_REVIEW"` to the Skipped list makes `python -c "import src.utils.config"` raise `AssertionError`. The processing branch in `api_jobs.py` fetches by excluding the four lists, not by passing an explicit include-list. `JOB_STATES["CANDIDATE_SKIPPED"]["prior_states"]` is computed from the Applied / Skipped lists. **Fail:** the import succeeds with the overlap, a hand-typed Processing state list exists in `config.py`, or the skip priors are a literal list (a parallel registry instead of the derivation).
 8. **Skip from Processing.** For a job in each of `NEW`, `PASSED_JD`, `METEORITE_QUALIFIED`, `BUILD_ARTIFACTS`, and `BUILD_ARTIFACTS.<chain task>`, `POST /api/jobs/<id>/skip` returns 200, and the job then appears in `view=skipped` as `CANDIDATE_SKIPPED` and not in `view=processing`. A job with a non-null `batch_id` has `batch_id` null after the skip. Skip on a `CANDIDATE_APPLIED` job still returns 409. **Fail:** any 409 on the five Processing states, a lingering `batch_id`, or a 200 on the Applied job.
 9. **Skip route logs once.** A successful skip writes exactly one `app_log` info line matching `| api /api/jobs/<id>/skip completed: POST 200`. `git diff origin/dev -- src/ui/api | rg "^\+.*logger\.info"` shows only that line (no info on the GET routes), and `src/core/tracker.py` adds no `logger.info` for skip. **Fail:** zero or two lines, or an info line on a GET route.
10. **Counts match lists.** For candidate X, the nav `count` on each of the six items equals the row count of its page's list (the `view=` response, or the meteorites list length). **Fail:** any mismatch.
11. **Landing page.** For a candidate with Ready = 0 and Review = 3, loading `/` lands on `/jobs/review`. With all six counts at 0, it lands on `/jobs/ready`. Browsing to `/jobs/recommended` or `/nope` follows the same rule, and so does closing the detail deeplink modal. `rg -n '"/jobs/(recommended|ready|review)"' src/ui/frontend/src --glob '!routes.tsx' --glob '!JobsHomeRedirect.tsx'` returns nothing. **Fail:** a different landing page, a 404 / blank page, or another hard-coded landing target outside the redirect.
12. **Old routes gone.** `rg -n "jobs/in_review|jobs/recommended|jobs/responded" src/ui/frontend/src src/utils/config.py src/ui/api` returns nothing, and `JobsInReview.tsx` and `JobsResponded.tsx` no longer exist. **Fail:** any hit or file present.
13. **Ready / Review behave like Recommended, with Source.** On Review, every row has the Generate Artifacts row action and the bulk bar offers Generate. On Ready, no row does. Both pages keep the Analysis toggle and Total, and their titles read "Ready" / "Review". Each row's Source cell equals the job's `source` (`meteorite` for a meteorite-track job), and no separate "Meteorites" section heading renders. `rg -n "meteorite_section" src` returns nothing. **Fail:** Generate on a `CANDIDATE_REVIEW` row, missing toggle / Total / Source, a meteorite sub-section, or the grep hits.
14. **Meteorites show landed-job state.** For every Meteorites row with an `astral_job_id`, the landed-job state cell equals `GET /api/jobs/<id>` `.state`. Rows without a job show `—`. Clicking the job link opens the Job Analysis Report modal for that id while the URL stays `/jobs/meteorites`, and clicking elsewhere on the row still opens the Meteorite modal. **Fail:** stale or missing state, navigation away, or the wrong modal.
15. **Builds clean.** `python -c "import src.utils.config"` exits 0. In `src/ui/frontend`, `npm run build` exits 0, and `npm run lint` reports no problem absent on `origin/dev`. **Fail:** non-zero exit, or a new lint problem.

## Open questions

none

## Proposed child tickets

#### 1!: **Jobs list partition, views, skip, and nav config - Ada**

Delivers the backend for all six lists:

* Ready / Review state lists; Skipped gaining the two build-failure states; the disjointness guard; Processing as the complement.
* Widened, derived skip legality, plus the core skip that releases batch claims.
* The new `view=` branches and the Applied crash fix.
* Nav items and all six counts.
* The manifest jobs block, with the meteorite sub-section removed.
* The Meteorites landed-job state on the list API.

Does **not** touch any React file (#2, #3).
**Citations:** `stat.logging.info.api` (no info on GETs; one completion line on the skip POST); `stat.logging.error` (meteorite list handler wraps the new read).
**Scope:** `src/utils/config.py`, `src/data/database.py`, `src/core/tracker.py`, `src/ui/api/api_jobs.py`, `src/ui/api/api_system.py`, `src/ui/api/api_meteorite.py`. Technical scope covers the `config.py`, `database.py`, `tracker.py`, `api_jobs.py`, `api_system.py`, and `api_meteorite.py` items above, verbatim.
Estimate: 5

#### 2: **Ready / Review / Processing pages, landing, and Jobs routes - Hedy**

After #1. Delivers the frontend nav re-cut:

* Ready and Review served by the Recommended list component, with the Source column and no meteorite sub-section.
* The new Processing page, whose rows open the Job Detail modal with working Skip.
* The first-non-empty landing redirect.
* Removal of the In Review and Responded pages and routes.
* The manifest type.

Does **not** touch the Meteorites page (#3) or any backend file (#1).
**Citations:** none — every file is under `src/ui/frontend/`, outside both statutes' territory.
**Scope:** `src/ui/frontend/src/routes.tsx`, `src/ui/frontend/src/components/JobsHomeRedirect.tsx` (new), `src/ui/frontend/src/pages/JobsRecommended.tsx`, `src/ui/frontend/src/pages/JobsProcessing.tsx` (new), `src/ui/frontend/src/pages/JobsInReview.tsx` (deleted), `src/ui/frontend/src/pages/JobsResponded.tsx` (deleted), `src/ui/frontend/src/contexts/StateUiContext.tsx`, `src/ui/frontend/src/pages/JobsJobDetail.tsx`, `src/ui/frontend/src/components/AdminRoute.tsx`, `src/ui/frontend/src/pages/CandidateSurferConsent.tsx`, `tests/component/frontend/pages/test_JobsInReview.test.tsx` (deleted), `tests/component/frontend/pages/test_JobsResponded.test.tsx` (deleted), `docs/test-bible/frontend/pages.md`. Technical scope covers the `routes.tsx`, `JobsHomeRedirect.tsx`, `JobsRecommended.tsx`, `JobsProcessing.tsx`, `StateUiContext.tsx`, and landing-target items above, verbatim.
Estimate: 5

#### 3: **Meteorites landed-job state and job link - Katherine**

After #1. Adds the landed-job state column and the in-page Job Analysis Report link to Jobs → Meteorites. Does **not** change the list API (#1) or any other Jobs page (#2).
**Citations:** none — frontend-only, outside both statutes' territory.
**Scope:** `src/ui/frontend/src/pages/JobsMeteorites.tsx`. Technical scope covers the `JobsMeteorites.tsx` item above, verbatim.
Estimate: 2

**New patterns:** none.

**Monolith check:** Functional scope has 9 items across 3 children. The children are split by layer (backend / list pages + landing / Meteorites page), so #2 and #3 can run in parallel once #1 lands.

**Scope partition check:** all 20 Component scope rows are claimed exactly once. #1 claims the 6 backend files, #2 claims 13 rows (10 frontend source files plus the 2 deleted tests and the bible page), and #3 claims 1. Every Technical scope item maps to the child that owns its file.

---

## Original brief

Please change the jobs navigation to the following set of job lists:

* Ready (CANDIDATE_REVIEW)
* Review (RECOMMENDED)
* Applied (CANDIDATE_APPLIED and other post-application states)
* Processing (all non-terminal states other than the above)
* Skipped (all terminal states) - editable
* Meteorites (all states of meteorite jobs with the current state of their landed job, and a link to that job modal)

### Comments

#### chuckles — 2026-10-04T18:42:36.761Z
AST-1975 estimate 5→3 — frontend-only, mostly reuses existing list components.

#### chuckles — 2026-10-04T16:04:45.241Z
@susan

1. **Terminal set.** Confirm that Skipped = today's Skipped states + below-floor virtual skips + `ERROR_BUILD_ARTIFACTS` (chain error hold, currently on no list) + `BUILD_FAILED` (registered but never written). Bulk Retry would send them to `RECOMMENDED` / `CANDIDATE_REVIEW`. Also confirm that `CANDIDATE_REJECTED` / `CANDIDATE_GHOSTED` stay on Applied, not Skipped.
2. **Processing row modal.** `BUILD_ARTIFACTS` rows move from Recommended to Processing, and their Cancel button lives on the Job Analysis Report modal. Recommended: every Processing row opens the Job Analysis Report modal, the same one the detail deeplink and the Meteorites link use. The alternative is keeping In Review's Job Detail modal, which loses Cancel from the nav.
3. **Meteorite jobs on Ready / Review.** Today Recommended pulls meteorite-company jobs into their own "Meteorites" sub-section at the top. Recommended: list them inline with everything else, since the Meteorites page now covers that view. Or keep the sub-section on both pages?
4. **Default landing page.** `/` and unknown URLs go to `/jobs/recommended` today. Recommended: `/jobs/ready`. Or `/jobs/review`?

---

_Implementation detail may live in git history on `origin/dev`._
