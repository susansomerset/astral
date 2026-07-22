# AST-753 — fetch_job_pages does not fetch nav links

<!-- linear-archive: AST-753 archived 2026-07-22 -->

## Linear archive (AST-753)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-753/fetch-job-pages-does-not-fetch-nav-links  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Susan flagged a **pattern drift** bug, not a one-off company repro: **fetch_job_pages** ([AST-719](https://linear.app/astralcareermatch/issue/AST-719/fetch-job-pages-gazer-batch-and-pjl-ready-state-find-job-page-logic)) appears to use a different scrape shape than the established homepage / **fetch_website** path — visible text without the shared blank-line normalization, and nav links not delivered through the same reusable Playwright + enumerate contract Susan expected. The monolithic find path already assembled page text **with** link material for **select_job_page**; the decomposed hop must not invent a parallel scrape pattern. This epic restores **one shared page-scrape contract** (collapsed visible text + numbered nav-link list) consumed by both homepage fetch and PJL fetch, then wires **fetch_job_pages** through it.

## Functional scope

1. **Single reusable page scrape:** One Playwright-level helper (same entry point for homepage and PJL URL scrapes) returns **collapsed visible text** (AST-710/715 rule — no runs of excess blank lines) **and** all nav links on that page load as a **numbered list** via the product enumerate helper — not two divergent scrape implementations.
2. **fetch_job_pages uses the shared helper:** The **fetch_job_pages** dispatch hop calls that helper for each pending **possible_joblist_links** URL, merges additively, and persists assembled page text **and** merged enumerated nav links for the decomposed PJL pipeline.
3. **Downstream parity:** Stored PJL material and **select_job_page** at **PJL_READY** receive link enumeration consistent with the monolith path — not visible text alone when links were found on the page.
4. **Additive scrape behavior unchanged:** URL ledger skip/append, **PJL_READY** / failure transitions, and no **job_site** write on this hop remain as shipped in [AST-719](https://linear.app/astralcareermatch/issue/AST-719/fetch-job-pages-gazer-batch-and-pjl-ready-state-find-job-page-logic).
5. **Debug traceability (**`debug=True`**):** Per AST-538, logs show per-URL scrape outcomes including normalized visible-text length, nav-link count recorded, and skip vs fresh-scrape — Style D index headers with `|` detail; not batch summary alone.

## Boundaries

* Does not refactor **select_job_page** routing, TRY_LINKS retry logic, or state transitions ([AST-720](https://linear.app/astralcareermatch/issue/AST-720/select-job-page-dispatch-refactor-find-job-page-logic-confirmation) stands).
* Does not remove monolithic **find_job_page** or change **parse_job_list** ([AST-721](https://linear.app/astralcareermatch/issue/AST-721/parse-job-list-dispatch-refactor-and-monolith-removal-find-job-page)).
* Does not change careers-list readiness gating ([AST-689](https://linear.app/astralcareermatch/issue/AST-689/dynamic-careers-list-scrape-readiness-job-site-scrape-is-too-fast)) beyond calling the shared helper after readiness where applicable.
* Does not add Betty log-string tests for debug output.
* Must not regress [AST-718](https://linear.app/astralcareermatch/issue/AST-718/prefilter-routing-company-states-and-pjl-url-hydration-find-job-page) **possible_joblist_links** ledger dedupe or [AST-673](https://linear.app/astralcareermatch/issue/AST-673/preserve-job-site-on-find-job-page-failure-companyjob-site-is) **job_site** non-write on fetch.

## Acceptance criteria

1. Homepage / **fetch_website** and **fetch_job_pages** both invoke the **same** shared page-scrape helper (not parallel one-off scrape code paths).
2. After **fetch_job_pages** on a company with at least one **possible_joblist_links** URL, persisted PJL data includes collapsed visible text per page **and** numbered nav-link enumeration when Playwright finds links (Mitratech careers-style pages are acceptable repro).
3. **select_job_page** at **PJL_READY** receives link material aligned with criterion 2 before the agent call when links were scraped.
4. Stored visible text no longer shows long runs of consecutive blank lines on fresh **fetch_job_pages** runs (same normalization as homepage fetch).
5. With `debug=True` on the same scenario, logs satisfy AST-538 per-index found/recorded trace for each URL scraped.

## Dependencies and blockers

* **fetch_job_pages** / **PJL_READY** shipped ([AST-719](https://linear.app/astralcareermatch/issue/AST-719/fetch-job-pages-gazer-batch-and-pjl-ready-state-find-job-page-logic) — User Testing).
* Decomposed **select_job_page** consumer ([AST-720](https://linear.app/astralcareermatch/issue/AST-720/select-job-page-dispatch-refactor-find-job-page-logic-confirmation) — User Testing).
* Blank-line normalization precedent ([AST-710](https://linear.app/astralcareermatch/issue/AST-710/remove-empty-lines-from-visible-text) / [AST-715](https://linear.app/astralcareermatch/issue/AST-715/uat-fetch-website-saves-skip-blank-line-collapse-at-runtime-remove) — Done).

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-753 (parent) | ftr/AST-753-fetch-job-pages-nav-links |
| AST-759 | sub/AST-753/AST-759-shared-page-scrape-fetch-job-pages-nav-links |
| AST-826 | sub/AST-753/AST-826-dedupe-select-job-page-nav-links |

**Epic worktree:** `astral-AST-753/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Hedy | engineer | 2205a271-2d3f-4c16-9948-33dc6d205515 |
| Betty | qa | 8a77a085-2fb7-4682-8c43-5d4ce7b1efc4 |
| Radia | review | 310cf23f-fb3f-4819-9bef-cd3c3476f6a2 |

## Original brief

Did we add a new function for fetch job pages instead of using the function that scrapes the visible text and enumerates the nav links on the page?  Because I think we're only sending the visible text for the job page, not the links.

This should be a reusable function from playwright, which fetches the visible text (without excess empty space) and all nav links found on the page, using the enumerate list function in [formatting.py](<http://formatting.py>) to return the concise visible text and number link list.

Please note: the excess empty space is still appearing in the output:

```
=== PAGE 1: https://mitratech.com/about-us/careers ===
Search     
	
		
	
	

      
        
        
      
    
  




	
		


			
			
	
		
			
			What We Do

		
	

	
		
			
			At Mitratech

		
	

	
		
			
			Current Openings

		
	

	
		
			
			Our People

		
	

	
		
			
			Built In Austin’s Best Places to Work 2025! Read More

		
	

	
		
			
			Our values shape how we’re leading change

		
	

  
    
      
        
            
        
      
      
        
            TRANSPARENCY
            TRUTHFUL
FORTHRIGHT
OPEN COMMUNICATION
ALL PERSPECTIVES

            
        
      
    
  

  
    
      
        
            
        
      
      
        
            GROWTH
            MOVE FAST, FAIL FAST
NEVER SETTLE
OPEN TO SUGGESTIONS
ROOM FOR IMPROVEMENT

            
        
      
    
  

  
    
      
        
            
        
      
      
        
            INCLUSIVITY
            NO EGO
NO POLITICS
GLOBAL SCOPE
EVERYONE THRIVES

            
        
      
    
  

  
    
      
        
            
        
      
      
        
            TRUST
            EMPATHY
RESPECT
UNDERSTANDING

            
        
      
    
  

  
    
      
        
            
        
      
      
        
            Ownership
            TEAM FIRST
TAKE THE LEAD
NO EXCUSES
BIAS FOR ACTION

            
        
      
    
  

	
		
			
			Jobs that become careers
If you are an individual with a disability and require a reasonable accommodation to complete any part of the application process, or are limited in the ability or unable to access or use this online application process and need an alternative method for applying, you may contact 1-888-784-7224, option 5, for assistance.
View Openings

		
	

	
		
			
			Notification of Equal Employment Opportunity and Affirmative Action Policy
We are an equal opportunity employer that values diversity at all levels. All qualified applicants will receive consideration for employment without regard to race, color, religion, gender, national origin, age, sexual orientation, gender identity, disability or veteran status. To learn more, please visit Equal Opportunity Office at https://www.eeoc.gov/.

		
	

	
		
			
			Mitraperks

		
	

	
		
			
			Lifestyle

Casual Dress Code
Wellness Challenges
Worldwide Parental Leave Policy


		
	

	
		
			
			Professional Development

World-Class Training
Professional Development
Mentor Program
Cross-functional Learning Sessions


		
	

	
		
			
			Benefits

Retirement Plan Funding
Comprehensive Benefits
Extensive Vacation Policies
Additional Voluntary Benefit Options


		
	

	
		
			
			Workplace Culture

Employee Recognition Programs
Company Contests


		
	

	
		
			
			SECURITY NOTE: Increasingly, scammers and fraudulent actors are seeking to profit from unsuspecting job candidates regardless of whether they apply for a position directly with the company or not. Their methods include contacting people directly and passing themselves off as company recruiters using fake profiles on LinkedIn or other sites.
 
Please know that Mitratech will never ask you to do anything that puts your privacy at risk, nor would the company require any form of payment or upfront purchase from you as part of the employment process. We will never ask you to install software of any kind, including the type that facilitates wire transfers or use of any of your personal information.

		
	

	
		
			
			Our clients expect success: you’ll empower it
Our team partners with legal and compliance professionals so they can leverage the world’s most intuitive, adaptable, and flexible software products. So legal and GRC teams become more capable of rising to the challenge of serving the evolving needs of the modern, dynamic enterprise.
See Our Products

		
	

	
		
			

		
	

		
	








  
    
      
        
        
        
          
          EnglishEspañolDeutschEnglish (United Kingdom)Español (América Latina)Français中文 (简体)
        
      
      
        About UsWhy Mitratech?Our TeamCareersPartnersPress CenterCommunity InvolvementClient SuccessOur ClientsProfessional ServicesHostingSupport CenterResourcesBlogResource HubMultimediaTAP Use CasesGRC Use CasesEventsInteractUpcoming Events & WebinarsOn-Demand Webinars
        ©2026 Mitratech, Inc. All rights reserved. Privacy Policy | Modern Slavery Statement | Legal Notice | Cookie Policy | Do Not Sell/Share My Info
      
    
      
      
        
        
        
        
          
          
        
      
      
        About UsWhy Mitratech?Our TeamCareersPartnersPress CenterCommunity InvolvementClient SuccessOur ClientsProfessional ServicesHostingSupport CenterResourcesBlogResource HubMultimediaTAP Use CasesGRC Use CasesEventsInteractUpcoming Events & WebinarsOn-Demand Webinars
        ©2026 Mitratech, Inc. All rights reserved. Privacy Policy | Modern Slavery Statement | Legal Notice | Cookie Policy | Do Not Sell/Share My Info
```

### Comments

#### chuckles — 2026-06-26T18:26:02.586Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-826** | select_job_page live content duplicates nav links |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-826** — _select_job_page live content duplicates nav links_
- **Issue reported:** After AST-759 shipped, **select_job_page** agent live content at **PJL_READY** includes navigation links **twice** — per-page `--- NAV LINKS ---` sections inside assembled PJL page text **and** a trailing global `=== NAV LINKS ===` block from merged `pjl_nav_links`. Susan UAT: "i
- **Should now:** Nav links appear **once** in the material sent to **select_job_page** (token-efficient). Links must still be available for TRY_LINKS index resolution.
- **Quick check (this fix only):**
  1. Run **fetch_job_pages** on a **PREFILTER_PASSED** company with **possible_joblist_links** where Playwright finds nav links (e.g. Mitratech careers).
  2. Confirm company reaches **PJL_READY** with non-empty `pjl_nav_links` and assembled PJL content.
  3. Inspect **select_job_page** live content (Admin ad-hoc preview or debug) — nav enumeration appears twice (per-page block + global block).

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-06-26T18:15:10.372Z
Well, now, for some reason, it's adding nav links TWICE.  Just once is best, for the sake of tokens, please.

#### chuckles — 2026-06-25T02:00:53.212Z
[check-linear] answered (@susan)

Yes — **fetch_job_pages** took a separate scrape path (visible text only) instead of the shared Playwright helper used by **fetch_website** (collapsed text + enumerated nav links). AST-753 / AST-759 exist to merge onto one contract; that is the pattern drift you flagged, not an intentional second design.

#### chuckles — 2026-06-23T19:30:45.531Z
[merge-child] blocked: validate-sub-log — polluted `origin/sub/AST-753/AST-759-shared-page-scrape-fetch-job-pages-nav-links` (foreign AST-741/745/746/747/751 merges + `Merge remote-tracking branch` on sub). @Hedy White republish AST-759 from clean `origin/ftr/AST-753-fetch-job-pages-nav-links` only.

— Chuckles

#### susan — 2026-06-23T19:15:41.357Z
Thank you for the confirmation, @chuckles let's leave `find_job_page` out of scope per your recommendation.

#### chuckles — 2026-06-23T19:11:13.550Z
[check-linear] Discussion — yes, monolith still live until AST-721; decomposed chain is the target workflow this epic fixes (@susan)

#### susan — 2026-06-23T19:08:53.446Z
@chuckles is the "monolithic find_job_page" still relevant in the new workflow?  I think we may have made it unnecessary now that prefilter is already returning PJLs.  Do you recommend a refactor to remove that particulary task as obsolete?

#### chuckles — 2026-06-23T18:54:13.257Z
[check-linear] Discussion — definition updated for pattern/DRY scope (@susan)

#### susan — 2026-06-23T18:47:22.929Z
@chuckles I haven't answered your open questions because at this stage it is not about specific examples. This is asking the question about pattern use. Did we make a different CODE PATTERN for the job page fetch from the website/navlinks fetch? I would have expected playwright.py to have used the same function.

#### chuckles — 2026-06-23T17:58:34.762Z
@susan

1. Which company (**short_name**) and approximate run date showed the text-only output — so UAT can replay the same row?
2. In Admin or DB inspection for that run, was **pjl_nav_links** empty, or populated but not surfaced where you looked?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
