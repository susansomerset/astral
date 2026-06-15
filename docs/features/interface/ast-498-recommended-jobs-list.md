# AST-498 — Recommended Jobs List

<!-- linear-archive: AST-498 archived 2026-06-15 -->

## Linear archive (AST-498)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-498/recommended-jobs-list  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** susan  
**Priority / estimate:** Low / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-300; blocks: AST-499

### Description

## Purpose

Candidates landing on Recommended need to triage vetted jobs at a glance — how each job scored across JD, DO, GET, and LIKE — and see where each job sits in the prepare-to-apply journey, before opening the full job report. Today the Recommended page shows LIKE rubric grades and a flat table; it does not surface the consult phase scores or group jobs by candidate-facing state. This ticket delivers that browse-and-triage layer and must land before the full report modal ([AST-499](https://linear.app/astralcareermatch/issue/AST-499/recommended-job-modal)).

## Functional scope

* **State-grouped sections.** The Recommended jobs list is organized into three sections, in order:
  * **Recommended** — jobs in `RECOMMENDED` (Estelle upshot complete; candidate has not started Prepare).
  * **In Progress** — jobs in `BUILD_ARTIFACTS` (artifact pipeline running).
  * **Ready** — jobs in `CANDIDATE_REVIEW` (artifacts built; candidate can review and edit before Apply).
    Jobs appear in exactly one section based on current job state. Empty sections may be hidden or shown as empty — dev plan decides presentation; all three states must be supported when jobs exist.
* **Phase score columns.** Each row shows numeric scores (1–10 scale) for **JD**, **DO**, **GET**, and **LIKE**. Values come from `job_data` (`jd_score`, `do_score`, `get_score`, `like_score`) — the scores persisted when consult grading runs. Display plain numbers; no grade-dot rubric columns on this page for those four phases. Missing score shows an em dash or equivalent empty state.
* **Core row identity.** Each row still shows job title, company, and when the job last changed state (or equivalent “updated” timestamp already used on this page).
* **Skip from Recommended.** A candidate can skip any job from the Recommended screen (existing skip behavior and Skipped-screen unskip remain unchanged).
* **Sort within a section.** Rows within each state section are sortable by at least job title, company, each phase score column, and updated date — consistent with other job list pages.
* **Report entry point preserved.** Row or row action still opens the job report entry point (today a minimal analysis modal). Full report UX is AST-499; this ticket does not implement the tabbed report, Prepare/Apply, or artifact tabs.

## Boundaries

* Does **not** implement the Recommended Job Report modal — that is [AST-499](https://linear.app/astralcareermatch/issue/AST-499/recommended-job-modal) (blocked until this ticket completes).
* Does **not** change consult scoring logic, `analysis_upshot` generation, or Estelle prompt/schema work.
* Does **not** implement Prepare, artifact build, artifact editing, or Apply workflows.
* Does **not** change In Review or Skipped list behavior except shared components reused incidentally.
* Does **not** add visual score gradients or heat-map styling unless Susan revises scope — plain numeric display only for v1.
* State lists and recommended-state membership remain config-driven (not hardcoded in the frontend).

## Acceptance criteria

1. With a candidate who has jobs in `RECOMMENDED`, `BUILD_ARTIFACTS`, and `CANDIDATE_REVIEW`, the Recommended page shows three labeled sections and each job appears in the correct section.
2. Each row displays numeric JD, DO, GET, and LIKE scores sourced from `job_data` when present; absent scores show a clear empty state.
3. LIKE rubric grade-dot columns are not the primary consult summary on this page — the four phase score columns are.
4. Skip from a Recommended-section row moves the job to Skipped; unskip from Skipped restores it to the Recommended list flow.
5. Sorting works within each section on title, company, phase scores, and updated date without breaking section grouping.
6. Opening the report from a row still works via the existing entry point (stub acceptable until [AST-499](https://linear.app/astralcareermatch/issue/AST-499/recommended-job-modal)).

## Dependencies and blockers

* **Upstream (done):** Recommended pipeline and basic report stub — [AST-478](https://linear.app/astralcareermatch/issue/AST-478/synthesize-job-analysis-report-estelle-opus-upshot), [AST-479](https://linear.app/astralcareermatch/issue/AST-479/job-states-passed-like-recommended-and-consult-like-pass-synthesize), [AST-480](https://linear.app/astralcareermatch/issue/AST-480/analysis-upshot-consult-dispatch-and-job-data-persist-synthesize-job), [AST-481](https://linear.app/astralcareermatch/issue/AST-481/job-analysis-report-runtime-render-from-job-data-synthesize-job).
* **Downstream:** [AST-499](https://linear.app/astralcareermatch/issue/AST-499/recommended-job-modal) (Recommended Job Modal) is **blocked by** this ticket.
* **Adjacent (not blocking list):** Artifact build pipeline ([AST-300](https://linear.app/astralcareermatch/issue/AST-300/build-resume-artifact) et al.) — jobs may appear in In Progress / Ready sections before artifact UX is complete elsewhere.

## Open questions

None.

---

## Original brief

For jobs recommended, we need to show a summary of all the analysis for the job before the user clicks on the job to see the full report.

I think the job list will just show the numeric points for each of these categories: JD, DO, GET, LIKE. Scores from 1 to 10 (will always be above each score floor, so very rare low numbers here, no need for visual gradients (BUT YOU NEVER KNOW WITH ME MUHAHA)

We do want to have the Recommended jobs grouped by STATE (I think they are RECOMMENDED, IN PROGRESS (or whatever we said that would be), and READY (i mean it, see the other tickets that talk about supporting these states, I can't remember verbatim.

A candidate can skip any job in the Recommended screen (and unskip on the Skipped screen as already works.)

### Comments

#### chuckles — 2026-06-02T19:47:28.567Z
[check-linear]

**Inbox pass (start AST-498 → full Chuckles queue)**

**§0a (`astral` / `dev`):** `git fetch origin`, `checkout dev`, `merge origin/dev` — **BEHIND=0**, `origin/dev` ancestor of **HEAD**.

**§0b (@chuckles):** Team Astral `@chuckles` / `@Chuckles` search + **14d** fallback; child walk **AST-498** (**AST-522**), **AST-490** family, **AST-538** (**AST-540**–**546**). **0** open @-mentions needing reply after latest Chuckles `[check-linear]` / closure posts.

**§0c (assignee = me, active statuses):** **0** tickets (exclude Done/Canceled/Backlog). Full threads on **AST-498**, **AST-490**, **AST-523**, **AST-538**, **AST-499**, **AST-539** — no teammate comments after Chuckles’ latest replies that expect orchestration action.

**Notable (already closed, no action):**
- **AST-490** / **AST-523** — Susan “wrap up” → **finish-up** landed; Chuckles `[check-linear]` @ `2026-06-02T17:32`.
- **AST-538** — Susan “ready to go” → define-linear + backfill parents **AST-540**–**546**; Chuckles `[check-linear]` @ `2026-06-02T19:35`.
- **AST-499** — waiting on **Open questions** (Chuckles @susan @ `2026-06-02T19:46`).

**Pipeline:** No `plan-astral` / `build-astral` / `test-astral` / `resolve-astral` / `review-astral` from this pass.

**Queue clear:** Reassigning **Done**/**Canceled** Chuckles tickets resolved or finished this cycle → **Susan Somerset** (**AST-498**, **AST-523**, **AST-313**, **AST-320**, **AST-342**, **AST-411**, **AST-412**, **AST-538**). **Keeping Chuckles:** **AST-499** (OQs), **AST-539** (definition backlog).

— Chuckles

#### chuckles — 2026-05-29T00:31:36.870Z
## Manual test steps

**Prerequisites:** App running from local `dev` (restart after merge). Candidate with jobs in `RECOMMENDED`, `BUILD_ARTIFACTS`, and `CANDIDATE_REVIEW` that have `jd_score` / `do_score` / `get_score` / `like_score` in job_data.

1. Open **Jobs → Recommended**. Confirm three sections appear when jobs exist: **Recommended**, **In Progress**, **Ready** — each job in the correct section only.
2. Confirm each row shows plain numeric **JD**, **DO**, **GET**, **LIKE** columns (not LIKE rubric grade dots). Missing scores show em dash.
3. Confirm **Score** / rubric vector columns are gone from this page.
4. **Skip** a job from Recommended → verify it appears on **Skipped**; **unskip** restores it to Recommended flow.
5. Within one section, sort by **Company**, a phase score column, and **Updated** — order changes without breaking grouping.
6. Row click opens job detail; **View Job Analysis** opens the existing analysis modal stub.

`origin/ftr/AST-498-recommended-jobs-list` @ `e678e00c` · local `dev` merged (`9ebb36fa`). Restart app if running.

**Note:** Chuckles auto-stashed unrelated WIP on `dev` before merge — run `git stash list` / `git stash pop` when ready.

— Chuckles

#### ada — 2026-05-29T00:26:21.498Z
[check-linear]

**Session scope:** Parent **AST-498** / **Astral Interface** — assigned child ids **(none)**. Publish ref: **AST-522** → `origin/sub/AST-498/AST-522-state-grouped-recommended-list-with-phase-scores` @ `d78b57ce`.

**§0a (`astral-ada` / `dev-ada`):** `git fetch origin`, `checkout dev-ada`, `merge origin/dev` — **merge-clean** (`BEHIND=0`, `origin/dev` ancestor of `HEAD`). Publish ref tip fetched for alignment (`d78b57ce`).

**§0b:** `@ada` issue search (Team Astral + **Astral Interface** project); **14d** fallback (`updatedAt -P14D`, team 250). Full threads on **AST-498**, **AST-522**, and recent @ada / assignee hits in session project (**AST-520**, **AST-521**, **AST-517**, **AST-513**, **AST-514**). **0** actionable comments — nothing `@ada` or directed at Ada needing reply or small fix after Ada’s prior `[check-linear]` on **AST-522** @ `2026-05-29T00:12`.

**Thread since last Ada pass:** Betty **Tests Ready** manifest on **AST-522** @ `d78b57ce`; Katherine **`[check-linear]`** noting **Tests Passed** — both are **Katherine** / **`test-astral`** pipeline handoffs, not Ada inbox work.

**§1:** Orchestrator assigned ids **(none)**. **AST-522** assignee **Katherine** (**Tests Passed**). Parent **AST-498** assignee **Chuckles** (**In Progress**).

**Pipeline:** Inbox quiet; no `plan-astral` / `build-astral` / `test-astral` / `resolve-astral` from this pass (happy path).

#### hedy — 2026-05-29T00:25:22.648Z
[check-linear]

**Session scope:** Parent **AST-498** / **Astral Interface** — assigned child ids **(none)** for Hedy. Publish ref context: **AST-522** → `origin/sub/AST-498/AST-522-state-grouped-recommended-list-with-phase-scores` (assignee **Katherine**, **Tests Passed**).

**§0a (`astral-hedy` / `dev-hedy`):** `git fetch origin`, `checkout dev-hedy`, `merge origin/dev` — already up to date. Gate: **BEHIND=0**, `origin/dev` ancestor of **HEAD** @ `308e17ad`.

**§0b:** `@hedy` issue search (Team Astral + **Astral Interface** project); **14d** fallback (`updatedAt -P1D`, team 250). Full threads on **AST-498**, child **AST-522**, and recent @-search / roster assignee hits (**AST-505**–**508**, **AST-514** family). **0** actionable comments — nothing `@hedy` or directed at Hedy needing reply or small fix. New since prior pass: Betty **AST-522** Tests Ready manifest @ `d78b57ce` (`2026-05-29T00:17`) — **Katherine** pipeline handoff, not Hedy inbox work.

**§1:** Assignee-me in **Astral Interface**: **0** tickets (**AST-522** → Katherine; parent → Chuckles). Global assignee-me roster UT (**AST-505** / **506** / **508**) — threads unchanged, no new `@hedy`.

**Pipeline:** Inbox quiet; no `plan-astral` / `build-astral` / `test-astral` / `resolve-astral` from this pass (happy path).

#### hedy — 2026-05-29T00:12:41.723Z
[check-linear]

**Session scope:** Parent **AST-498** / **Astral Interface** — assigned child ids **(none)** for Hedy. Publish ref context: **AST-522** → `origin/sub/AST-498/AST-522-state-grouped-recommended-list-with-phase-scores` (assignee **Katherine**).

**§0a (`astral-hedy` / `dev-hedy`):** `git fetch origin`, `checkout dev-hedy`, `merge origin/dev` — already up to date. Gate: **BEHIND=0**, `origin/dev` ancestor of **HEAD** @ `87d54fb8`.

**§0b:** `@hedy` / `@Hedy` issue search (Team Astral + **Astral Interface** project); **14d** fallback (`updatedAt -P14D`, team 250 + session project). Full threads on **AST-498**, **AST-522**, and recent @-search hits (**AST-521**, **AST-477**, **AST-514**, **AST-516**, **AST-513**). **0** actionable comments — nothing `@hedy` or directed at Hedy needing reply or small fix after Katherine’s `[check-linear]` @ `2026-05-29T00:09` on **AST-522**.

**§1:** Assignee-me in **Astral Interface**: **0** tickets (**AST-522** → Katherine, parent **AST-498** → Chuckles). Global assignee-me roster UT tickets (**AST-505** / **506** / **508**) reviewed — no new `@hedy` thread work.

**Pipeline:** Inbox quiet; no `plan-astral` / `build-astral` / `test-astral` / `resolve-astral` from this pass (happy path).

#### chuckles — 2026-05-29T00:05:27.765Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-498 (parent) | ftr/AST-498-recommended-jobs-list |
| AST-522 | sub/AST-498/AST-522-state-grouped-recommended-list-with-phase-scores |

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
