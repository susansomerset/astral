# AST-488 — Use "Company Search Criteria" to search for companies using Google CSE

<!-- linear-archive: AST-488 archived 2026-06-15 -->

## Linear archive (AST-488)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-488/use-company-search-criteria-to-search-for-companies-using-google-cse  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** susan  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-180

### Description

## Purpose

Roster today depends heavily on scraping company career sites and job boards, which does not scale as a primary way to discover *new* employers for a candidate. This spike proves a complementary discovery path: use Google Custom Search with candidate-specific **company search criteria** (role keywords plus optional site restrictions such as LinkedIn or Indeed) to surface search hits from which company *names* can be identified. Astral already resolves homepages and job pages once a company is on the roster; this work de-risks the search leg only. A successful spike gives the team confidence to wire criteria generation (Estelle), result parsing, and roster ingest in follow-on tickets.

## Functional scope

* **Google Custom Search integration:** A reusable capability in the external layer that accepts a fully formed search query string, calls Google Custom Search using deployment credentials, and returns a structured list of results (at minimum title, URL, and snippet for each hit).
* **Search criteria concept:** Support building queries from **company search criteria** consisting of free-text keywords (role, skills, industry terms, etc.) and optional **domain/site restrictions** (e.g. limit results to [linkedin.com](<http://linkedin.com>), [indeed.com](<http://indeed.com>), [glassdoor.com](<http://glassdoor.com>)). The spike may use fixed exemplar criteria; persisting criteria on the candidate record is not required for spike completion.
* **Spike exercise script:** A runnable, non-production script that invokes the integration with one or more exemplar searches and prints results in a human-readable form on the console so Susan can judge result quality and noise.
* **Credential handling:** Missing or invalid Google CSE credentials produce a clear, immediate failure (no silent fallback or empty success).

## Boundaries

* **Spike only — no product pipeline:** No dispatcher tasks, batch claiming, company or candidate database writes, or company state transitions (e.g. IMPORTED → WEBSITE_FOUND).
* **No AI in this ticket:** Estelle (or any agent) generating search terms from candidate strengths, priorities, and dealbreakers is out of scope here; only manual or hardcoded exemplar queries for the spike script.
* **No result parsing or roster ingest:** Extracting company names from snippets, deduplicating against companies already tied to the candidate, and creating NEW/IMPORTED company rows are follow-on roster work.
* **Not homepage discovery:** This is not the canceled [AST-35](https://linear.app/astralcareermatch/issue/AST-35/locate-company-website) flow (“given a company name, find its website”). Query intent is discovery of *employers* via job-aggregator domains, not resolving a known name to a homepage.
* **No UI:** Admin or candidate screens for editing search criteria are out of scope.
* **No change to existing roster locate/parse/prefilter behavior** must be required to ship the spike.
* **Secrets:** API key and search engine ID remain environment-only configuration, consistent with product code rules.

## Acceptance criteria

1. With valid `GOOGLE_CSE_API_KEY` and `GOOGLE_CSE_ID` set in the environment, the spike script runs non-interactively and prints at least one page of search results for each exemplar query Susan approves for this spike.
2. The Google Custom Search integration is callable independently of roster code (no import-time coupling to dispatcher or company batch logic).
3. When credentials are missing or the API returns an error, the integration or script surfaces an explicit failure message; it does not return an empty success.
4. Each printed result includes enough fields for a human to judge whether a company name could be inferred later (title, URL, snippet).
5. Exemplar searches collectively exercise at least one LinkedIn-domain restriction and at least one additional job-board or careers-aggregator domain Susan specifies.

## Dependencies and blockers

None for starting the spike. Follow-on roster and Estelle work should treat this ticket’s integration and spike findings as input; adjacent backlog items (e.g. [AST-180](https://linear.app/astralcareermatch/issue/AST-180/revisit-no-job-site-states) web search for NO_JOB_SITE) are related but not blockers.

## Open questions

1. Susan’s brief references using “the following searches” for the spike but does not list them — what are the exact exemplar keyword strings and domain restrictions?
   1. Oops, forgot to include them.

* healthtech SaaS platform "Series B" OR "Series C" remote 
* healthcare software platform integration company 2024 2025 
* clinical data platform SaaS company remote-first
  Domains to search:
* LinkedIn (company pages, not jobs)
* Crunchbase (structured, company names surface cleanly)
* Builtin (curated, often has culture signals)
* Wellfound
* Indeed

1. For the spike, should exemplar criteria be hardcoded in the script only, or should the script also read a sample `company_search_criteria` object shape from a candidate fixture (without persisting to production data)?
   1. Just hardcode in the script for now
2. How many results per query should the integration request and display for review (e.g. top 10)?
   1. Get the first 10 for now, but make it a parameter of how many results to return, where 0 is unlimited.
3. After the spike, should full pipeline work stay on [AST-488](https://linear.app/astralcareermatch/issue/AST-488/use-company-search-criteria-to-search-for-companies-using-google-cse) (remove Spike label) or split into a separate parent epic (Estelle criteria + roster parse/ingest)?
   1. We'll build a new issue to break down the implementation of each piece from search criteria generation to task-key creation, to adding the function to roster to call google, and another task-key to vet the names via AI (using Haiku)

---

## Original brief

We are fairly limited in our ability to scrape job boards at scale, so we need a new method of "scraping" for new companies to watch for the candidates.

By adding "company_search_criteria" with keywords and domains (e.g. "[linkedin.com](<http://linkedin.com>)"), we can use Google CSE to perform searches, parse the results and watch for new-to-candidate companies that can be added to the roster and evaluated as a NEW company.

The Agent (Estelle) would generate the search terms based on all the candidate content (strengths, priorities, dealbreakers, etc.) and can provide a simple string to send to the CSE endpoint to pull all responses found on linkedin and/or indeed or glassdoor or other sites.

All we need are the names of the companies, and we can then search for those website homepages (and job pages if they get to TO_WATCH) on our own.

For this spike, we will use the following "searches", build out google_cse.py in externals/ to set up the endpoint functionality, and roster will (post-spike) own the responsibility of parsing and managing the results.  google_cse.py is the main deliverable for this spike, and it can be part of the src/external codebase even at the spike stage.  The spike part will be a script that calls google_cse.py with search strings and displays the results nicely on the console.

### Comments

#### chuckles — 2026-05-26T21:50:20.603Z
`origin/dev` @ `8e696a4a` — merge into `dev-<agent>`: `git fetch origin && git checkout dev-<agent> && git merge origin/dev`

— Chuckles

#### chuckles — 2026-05-26T02:57:00.943Z
## Manual test steps

**Prerequisites:** `GOOGLE_CSE_API_KEY` and `GOOGLE_CSE_ID` in your shell (see `env.example`). Local `dev` merged for UAT.

1. From repo root on local `dev`, run: `python3 scripts/spikes/ast489_google_cse_company_search_spike.py`
2. Confirm three exemplar query sections print (healthtech Series B/C, healthcare integration 2024–2025, clinical data platform remote-first).
3. Each hit shows **Title**, **URL**, and **Snippet** on separate labeled lines.
4. Confirm at least one run uses LinkedIn company pages (`linkedin.com/company`) and at least one uses another aggregator domain (Crunchbase/Builtin, or Wellfound/Indeed per script `RUNS`).
5. Unset `GOOGLE_CSE_API_KEY` (or both vars) and re-run — script must exit non-zero with an explicit error (not empty success).
6. Component tests: `./scripts/testing/run_component_tests.sh tests/component/external/test_google_cse.py` — 16 passed on `ftr` tip.

`origin/ftr/AST-488-use-company-search-criteria-to-search-for-companies-using-google-cse` @ `7aef0742` · local `dev` merged (`8e696a4a`). Restart app not required (no UI/dispatcher changes).

**Radia audit (§6.5):** Parent acceptance criteria **PASS** on composite `ftr` — external `google_cse` module, spike script, mocked component tests, no roster/dispatcher/DB scope creep. No backlog sub-issues filed.

— Chuckles

#### chuckles — 2026-05-26T02:36:17.473Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-488 (parent) | ftr/AST-488-use-company-search-criteria-to-search-for-companies-using-google-cse |
| AST-489 | sub/AST-488/AST-489-google-cse-integration-and-spike-script |

— Chuckles

#### chuckles — 2026-05-26T02:17:54.926Z
@Susan Somerset — four open questions on the definition (also in Description):

1. What are the exact exemplar keyword strings and domain restrictions for the spike searches you referenced?
2. Hardcoded exemplars in the script only, or also exercise a sample `company_search_criteria` object from a fixture?
3. How many results per query for spike review (e.g. top 10)?
4. After the spike, keep full pipeline on AST-488 or split a follow-on epic (Estelle + roster ingest)?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
