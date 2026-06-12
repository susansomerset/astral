# AST-323 — Refactor job page discovery and parsing

<!-- linear-archive: AST-323 archived 2026-06-03 -->

## Linear archive (AST-323)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-323/refactor-job-page-discovery-and-parsing  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

**Refactor job discovery pipeline + dispatcher hardening**

Consolidates the company-to-job-list discovery flow and fixes several correctness issues exposed by running it at scale.

**Job discovery pipeline redesign** (640ad7f)

Replaces three sequential AI calls (find_job_site → vet_job_list → parse_job_list) with a single find_job_page invocation. Prefilter identifies possible_job_links; select_job_page confirms the job page with one TRY_LINKS retry; parse_job_list runs inline to validate selectors. Net: \~930 lines removed, dead states (TO_PARSE, NO_JOB_SITE, JOBSITE_WATCH_ISSUE) retired, state machine simplified to WATCH / HARD_PARSE / CANNOT_PARSE / NO_JOBLIST / NO_OPENINGS.

**Remove select_culture_pages task** (e5e5289)

Culture links are now surfaced by prefilter via culture_links_to_explore — no separate AI call needed.

**Additional fixes shipped on the branch:**

* possible_job_links now accepts full URLs from the prefilter agent, not just integer nav_link IDs (f8b5772)
* Strip hidden elements from visible text and DOM extraction — reduces noise sent to agents (974e0ba)
* Skip DOM narrowing when fewer than 2 job titles are present (490da03)
* Store agent responses on parse failures for troubleshooting (0a21d95)
* Capture runtime_prompt in agent_responses for prompt debugging (1bf2a66)
* Detect redirects in prefilter, fix decision label, remove easy_parse (6114670)
* Move pass/fail state classification into ROSTER_CONFIG — dispatcher reads from config instead of hardcoded arrays (714b2cd)

**Dispatcher hardening** (f984c1d)

* company_job_id made optional in qualify_job_listings schema — jobs without external IDs (e.g. biohub) were validating correctly 846 times then being discarded, burning API credits on infinite retries
* ERROR\_<task_key> states added for all tasks so failed entities transition out of their trigger state instead of being retried forever
* Circuit breaker auto-disables a dispatch task after 3 consecutive completed runs that produce 0 passed and 0 failed

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
