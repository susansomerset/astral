# AST-872 — Fetch culture pages task is missing?

<!-- linear-archive: AST-872 archived 2026-07-29 -->

## Linear archive (AST-872)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-872/fetch-culture-pages-task-is-missing  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** unassigned  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Consult grades company culture (LIKE) after GET, but culture page content is still pulled lazily inside LIKE prep. That buries fetch work inside grading, blocks clear dispatch gating after PASSED_GET, and makes it hard to see which jobs are culture-ready versus still waiting on page content. Coat-check retrieval for company culture content already exists from earlier prep work; what never shipped is an explicit **fetch_culture_pages** dispatch step with a **CULTURE_READY** holding state. This feature inserts that gate so every job that passes GET advances through a dedicated culture-fetch stage before LIKE runs.

## Functional scope

* Add a dispatchable **fetch_culture_pages** task (gazer-owned batch step, claimed like other post-score consult stages) that selects jobs in **PASSED_GET** with a dispatch **score_floor**.
* Every claimed job that completes the task successfully ends in job state **CULTURE_READY**. Advancement is universal for successful claims: already-present culture content and mid-fetch coat-check returns that resolve successfully are effective no-ops for content and still land **CULTURE_READY**.
* Culture page body retrieval happens only through the existing company coat-check path (request culture/website content via get_company_data). The task does not invent a parallel scrape path; when content is missing, coat-check triggers fetch one company at a time.
* Failure destinations for this task:
  * Scrape / coat-check content failures → **NEED_CULTURE_CONTENT** (investigation holding state).
  * Absence of culture links to explore → **NO_CULTURE_LINKS** (should be rare; ideally never happens once upstream link selection is healthy).
* Rewire the consult pipeline so LIKE grading claims jobs from **CULTURE_READY** (not directly from **PASSED_GET**). **PASSED_GET → CULTURE_READY → LIKE** is the happy-path order.
* When `debug=True` on a fetch_culture_pages batch, emit per-job index headers (universal `index N/M`, job identity, outcome) plus substantive working-detail lines for found vs recorded culture content — not batch pass/fail counts alone (backend debug contract).

## Boundaries

* Does not re-select culture page links (prefilter / culture link identification stays upstream). Does not change LIKE rubric, prompts, or grade scoring.
* Does not replace or remove the coat-check handler for culture/website content; this task orchestrates and state-gates it.
* Does not change homepage fetch (**fetch_website** / **HOMEPAGE_READY**) or JD fetch (**fetch_jd** / **JD_READY**) beyond the job-state graph edges needed for **CULTURE_READY**, **NEED_CULTURE_CONTENT**, and **NO_CULTURE_LINKS**.
* **NEED_WEBSITE_CONTENT** remains for its existing investigation paths; this feature adds **NEED_CULTURE_CONTENT** / **NO_CULTURE_LINKS** for fetch_culture_pages outcomes and must not break either investigation surface.
* Config remains the source of truth for states, task keys, and score floors (no hardcoded state sets outside config).

## Acceptance criteria

1. A job in **PASSED_GET** that meets the task score floor, claimed by **fetch_culture_pages**, ends in **CULTURE_READY** when coat-check returns culture page content (fresh fetch or already stored).
2. A job whose company culture content is already in company_data (or whose in-flight coat-check resolves successfully) still ends in **CULTURE_READY** without requiring a redundant scrape when content is already available.
3. A job whose culture scrape / coat-check fails to produce content ends in **NEED_CULTURE_CONTENT**.
4. A job with no culture links identified ends in **NO_CULTURE_LINKS**.
5. LIKE grading no longer claims jobs solely because they are in **PASSED_GET**; it claims from **CULTURE_READY**.
6. Jobs never skip **CULTURE_READY** on the happy path from GET to LIKE (every successful GET→LIKE path passes through **CULTURE_READY**).
7. With `debug=True` on a fetch_culture_pages batch, Susan can trace each job via distinct index headers and working-detail lines showing what was found and what was recorded for culture content.

## Dependencies and blockers

none.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-872 (parent) | ftr/AST-872-fetch-culture-pages |
| AST-874 | sub/AST-872/AST-874-fetch-culture-pages-culture-ready-gate |
| AST-878 | sub/AST-872/AST-878-uat-fetch-culture-pages-missing-json |

**Epic worktree:** `astral-AST-872/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Hedy | engineer | acc63ebc-160f-4d49-8806-0e5fdb576e36 |
| Betty | qa | 45c3bfd0-ae5d-4723-8944-cacc24108a62 |
| Radia | review | 56f9e9bc-413f-416f-9dac-9c778ba8d828 |

---

## Original brief

I think we need a fetch culture pages task in gazer.  Did we already implement this once?  Or did we just skip over it with all the recent updates?

fetch culture pages should have a score floor and a job state of "CULTURE_READY".

note that all jobs go from PASSED_GET to CULTURE_READY, but fetch only happens via coatcheck.

So, if acme has culture page links identified but culture content has not been added to company_data, when fetch_culture_pages calls get_company_data for the culture pages it triggers the fetch via gazer, one company at a time.  On successful retrieval of the page content, task completes successfully and sets job_state to "CULTURE_READY".  If the culture pages were already fetched (or are mid-fetch from an asynchronous call), then when the result is returned, the task sets job state to CULTURE_READY with effectively no-op.

### Comments

#### chuckles — 2026-07-22T23:53:42.042Z
[check-linear] Done — fetch_culture_pages in data/admin/agent_task.json (@susan)

#### chuckles — 2026-07-12T22:11:50.341Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-878** | fetch_culture_pages missing from codebase JSON content |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-878** — _fetch_culture_pages missing from codebase JSON content_
- **Issue reported:** On staging/UAT after AST-872 landed, **fetch_culture_pages** does not appear in the codebase JSON content Susan checks for dispatchable tasks (Scheduled Actions / task registry surface). The hop is missing from that JSON view even though the epic was prep-uat'd.
- **Should now:** **fetch_culture_pages** is present in the codebase JSON content for dispatchable tasks (same place other gazer/consult task keys are listed), so it can be scheduled with trigger **PASSED_GET** and score floor like sibling tasks.
- **Quick check (this fix only):**
  1. Open the codebase / admin surface that shows dispatchable task keys as JSON content (the same place Susan reviews after a consult/gazer ship).
  2. Search for **fetch_culture_pages**.
  3. Observe: key is absent from the JSON content.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-07-12T22:01:55.340Z
@chuckles the task has not been added to the codebase json content.

#### susan — 2026-07-12T18:06:26.191Z
Okay that makes sense. We don't need to change that here, this hop just guarantees a the page content is available, rather than burying it in the prep_live_content function.

We still want this as an explicit hop to shorten the cycle time to run the like analysis and preserve the cache usage.  Go ahead and proceed.

#### chuckles — 2026-07-12T18:02:27.786Z
[check-linear] Discussion — answered: LIKE-prep coat-check site

Yes — it is tacked onto **task execution**, not its own dispatch hop. Today, any consult path with `requires_company` (chiefly **grade_like**, also analysis paths that prep company context) calls `_prep_live_content` before the agent run; that helper asks roster `get_company_data(..., "website_content")`, which is the coat-check that scrapes/saves if missing. On None it moves the job to **NEED_WEBSITE_CONTENT** and aborts that LIKE (or sibling) run. So the fetch is a side effect of starting LIKE grading, not a prior scheduled task.

— Chuckles

#### susan — 2026-07-12T17:59:45.644Z
@chuckles But where is the like-prep coat-check called today? Is it specifically tacked on to another task execution?

#### chuckles — 2026-07-12T17:55:41.261Z
[check-linear] Discussion — confirmed not a duplicate fetch path

**NEED_WEBSITE_CONTENT** (UI: Need Website Content) is set today inside LIKE prep when the company coat-check cannot return `website_content`. There is no `fetch_culture_pages` dispatch task and no **CULTURE_READY** state in the live graph yet — culture scrape already runs only via that coat-check, lazily while grading LIKE.

This epic does **not** add a second scrape path: it adds an explicit dispatch hop + **CULTURE_READY** gate *before* LIKE, still calling the same coat-check. A job already in **NEED_WEBSITE_CONTENT** almost certainly failed that existing LIKE-prep coat-check, not a missing dedicated culture task.

— Chuckles

#### susan — 2026-07-12T17:53:45.445Z
@chuckles before we build, please confirm for me that this wasn't already built in to the logical flow?  I have a "NEEDS_WEBSITE_CONTENT" state job and I am not actually sure how it got there.  I think having this as a separate task hop makes sense, but I still want to be sure we are not introducing a second path to an already handled flow.

#### chuckles — 2026-07-12T17:27:24.766Z
@susan

1. When coat-check cannot produce culture content (no culture links identified, all scrapes fail, or coat-check returns empty/None), should **fetch_culture_pages** move the job to **NEED_WEBSITE_CONTENT**, leave it in **PASSED_GET**, or still advance to **CULTURE_READY** so LIKE can run without vibes pages?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
