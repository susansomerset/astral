# AST-671 — company.job_site is overwritten with company.company_website

<!-- linear-archive: AST-671 archived 2026-06-23 -->

## Linear archive (AST-671)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-671/companyjob-site-is-overwritten-with-companycompany-website  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-180; related: AST-318

### Description

## Purpose

Susan runs **find_job_page** from dispatch on companies that already have a **verified careers URL** stored in **job_site**. When the run does not successfully confirm a new listings page, the roster pipeline must not corrupt that column by copying **company_website** into **job_site** or by treating the homepage as the job listings URL. Today a failed or early-exit **find_job_page** run can overwrite a good **job_site** with **company_website** and move the company to a terminal failure state — destroying data Susan already validated and breaking downstream gaze and parse paths that depend on the stored careers URL.

## Functional scope

* **Preserve verified job_site on failure:** When a company row already has a non-empty **job_site** before **find_job_page** runs, any outcome that does **not** successfully identify or confirm a **new** careers listings URL must leave **job_site** unchanged (still the pre-run value).
* **Distinct columns:** **company_website** (homepage) and **job_site** (careers / listings page) remain separate fields. Failure or early-exit paths must not write **company_website** into **job_site** as a stand-in.
* **Successful discovery still updates:** When **find_job_page** successfully confirms a careers listings URL (including redirect to a final URL), **job_site** updates to that confirmed URL as today.
* **Companies without job_site:** Behavior for rows with no pre-existing **job_site** stays semantically the same — terminal states and empty **job_site** handling are unchanged except that failure paths must not invent a **job_site** from **company_website** unless product rules explicitly require it (see Open questions).
* **Dispatch entry points:** Fix applies wherever **find_job_page** is invoked from scheduled dispatch (**TO_WATCH**, **JOBS_FOUND**, **PREFILTER_PASSED** trigger states per roster config).

## Boundaries

* Does **not** fix Execution History / agent-data visibility for **find_job_page** batches — [AST-669](https://linear.app/astralcareermatch/issue/AST-669/find-job-page-job-doesnt-display-the-agent-content).
* Does **not** decide whether **komodohealth** (0 possible job links) should have invoked **select_job_page** — that is [AST-669](https://linear.app/astralcareermatch/issue/AST-669/find-job-page-job-doesnt-display-the-agent-content) scope unless Susan answers Open question 2 here.
* Does **not** add websearch fallback for companies with no careers page — [AST-180](https://linear.app/astralcareermatch/issue/AST-180/revisit-no-job-site-states) (Backlog).
* Does **not** change **company_website** cleanup, redirect recording, or deeplink normalization — [AST-318](https://linear.app/astralcareermatch/issue/AST-318/update-redirected-website-domains) (Backlog).
* Must not break **jobs_found_process_job_site** redirect updates, **NO_OPENINGS** / **recheck_no_openings** flows, or successful **WATCH** transitions when **find_job_page** genuinely finds a new listings URL.

## Acceptance criteria

1. **Repro:** Company in a **find_job_page** dispatch trigger state with a verified **job_site** URL distinct from **company_website** → run **find_job_page** from dispatch → if the run ends in **NO_JOBLIST** (or any other terminal failure state from this path), **job_site** in the company table still equals the pre-run verified URL; **company_website** is unchanged.
2. **No homepage substitution:** After any failed or early-exit **find_job_page** dispatch on a company that had a non-empty **job_site** before the run, **job_site** is never equal to **company_website** unless they were already equal before the run.
3. **Success path:** When **find_job_page** successfully confirms a careers listings URL, **job_site** updates to that confirmed URL (including redirect final URL when applicable).
4. **No job_site baseline:** Company with empty **job_site** before the run — failure behavior is unchanged from Susan's expectation for "no listings found" (terminal state appropriate to the outcome); this ticket does not require inventing a **job_site** from **company_website** on failure unless Susan answers Open question 3.
5. **Regression:** **JOBS_FOUND** re-parse path and **parse_job_list** dispatch on stored **job_site** still work for companies whose **job_site** was preserved by this fix.

## Dependencies and blockers

* [AST-469](https://linear.app/astralcareermatch/issue/AST-469/roster-locateparse-split-run-next-job-list-visible-jobs-found-path) (locate/parse split, **JOBS_FOUND** path) — Done.
* [AST-535](https://linear.app/astralcareermatch/issue/AST-535/dispatch-task-triple-unique-and-roster-to-watch-task-key-routing-bug) (**find_job_page** / **select_job_page** / **parse_job_list** dispatch routing) — coordinate if routing changes overlap.
* [AST-669](https://linear.app/astralcareermatch/issue/AST-669/find-job-page-job-doesnt-display-the-agent-content) — related sibling (agent-data inspection); not a blocker.

## Open questions

1. Your brief says **NO_JOBSITE** — the product state today is **NO_JOBLIST**. Confirm **NO_JOBLIST** is the state you saw (or name the state if different).
   1. [komodohealth] company state TO_WATCH -> NO_JOBLIST
   2. Sorry, that was my bad.
2. When a company already has a verified **job_site** but is claimed by **find_job_page** at **TO_WATCH** (or **PREFILTER_PASSED**), should the run **use the stored job_site** (like the **JOBS_FOUND** path) instead of PJL-from-prefilter discovery — or should it still attempt PJL discovery and only **preserve job_site on failure**?
   1. Yes.
3. For companies with **no** pre-existing **job_site**, should failure paths ever set **job_site** to **company_website**, or should **job_site** stay empty on failure?
   1. job_site stays empty, please.  No point giving us false hopes!  ;-D

---

## Original brief

When I run find_job_page from dispatch for a test company record that has a verified job_site url, it is set to "NO_JOBSITE", and the table's field for job_site now holds the company_website.

### Comments

#### chuckles — 2026-06-15T17:48:28.895Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-671 (parent) | `ftr/AST-671-company-job-site-overwritten` |
| AST-673 | `sub/AST-671/AST-673-preserve-job-site-on-find-job-page-failure` |

**Epic worktree:** `astral-AST-671/` — one active sub checked out at a time.

**Parent:** AST-671

— Chuckles

#### chuckles — 2026-06-15T17:04:13.785Z
@susan — open questions on the Description (numbered 1–3). Key product fork: preserve **job_site** only on failure vs route existing **job_site** companies through the stored-URL path instead of PJL discovery.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
