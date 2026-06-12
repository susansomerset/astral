# AST-183 — Prep Company Culture Pages

<!-- linear-archive: AST-183 archived 2026-06-03 -->

## Linear archive (AST-183)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-183/prep-company-culture-pages  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** unassigned  
**Priority / estimate:** High / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Implement coat-check pattern for company website_content in roster.get_company_data. When consult_like requests website_content and it doesn't exist in company_data, transparently fetch it: AI analyst selects which pages to scrape from the company's homepage text and nav links (both already in company_data from earlier pipeline steps), gatekeeper scrapes them, content saved to company record, value returned to caller. Same pattern as job_description coat-check in tracker.get_job_data and nav_links coat-check in roster.get_company_data.

**Acceptance Criteria:**

**Coat-Check Pattern:**

roster.get_company_data(company, key) checks company_data\[key\] — if present, returns it. If missing, runs a select/case on the key to dispatch the fetch-on-missing handler. Currently only nav_links has a handler (hardcoded if/else). Refactor to select/case dispatch and add the website_content handler:

```python
# In roster.get_company_data, after happy-path check:
# Select on key:
#   case nav_links_key: existing nav_links fetch logic
#   case website_content_key: AI selects pages, gatekeeper scrapes, save, return
#   default: return None (unregistered key, no handler)
```

Caller (consult_like via \_prep_live_content) just asks for the data and gets it back. No awareness of whether it was cached or freshly fetched.

**Data Dependencies (already available from earlier pipeline steps):**

* Homepage visible text: saved to company_data during prefilter (step a)
* Nav links: saved to company_data\["nav_links"\] during locate_job_page (step b), with its own coat-check fallback

**Fetch-on-Missing Flow (three steps):**

**1. AI Analyst selects pages:**

Grace receives company homepage visible text + nav_links. Returns list of URLs to scrape for culture vibes. Max pages config-driven (e.g. 5).

Pages the analyst considers: Homepage, About Us, Mission/Values, Product/Services, Blog (first page only).
Pages ignored: Careers, Contact, Legal, Privacy, Investors, Press.

**2. Gatekeeper scrapes selected pages:**

For each URL, playwright scrape_visible_text. Collect {url, content}. If individual pages fail (404, bot block), skip and continue with others.

**3. Save and return:**

Save {url, content} array to company_data\["website_content"\] via update_company. Merge with existing company_data (don't clobber nav_links, parse_instructions, etc.). Return the content to the caller.

**Failure Behavior:**

* nav_links missing: coat-check fetches them via existing nav_links handler (same as find_job_page uses). No fake default paths — if we can't get nav_links, we can't select pages.
* AI analyst task fails: cannot blindly scrape without page selection. Return None to caller.
* All page scrapes fail: something is wrong with the process. Return None to caller.
* Individual page scrape failures: skip failed page, continue with remaining. Only fail if ALL selected pages fail.
* Do NOT store empty website_content on failure — that would mask the problem on retry and prevent the coat-check from re-triggering after the issue is fixed.

**Error flow (no exception propagation):** roster.get_company_data returns None on failure → \_prep_live_content receives None → \_prep_live_content calls tracker.transition_state to set job to NEED_WEBSITE_CONTENT → \_prep_live_content returns False → consult_like sees no live_content, returns {success: False} without calling the agent → CLI logs the failure, continues batch.

NEED_WEBSITE_CONTENT is a new state (from PASSED_DO). Jobs in this state need investigation but the coat-check will re-trigger on retry once the underlying issue is resolved.

**Config:**

ROSTER_CONFIG company_data_keys: add "website_content": "website_content" (register as coat-check key).

```python
CONSULT_CONFIG = {
    "culture_pages_max": 5,
}
```

**LIKE Rubric Update:**

The LIKE rubric (207_LIKE_RUBRIC.txt) needs a new vector for company website/culture content analysis so Grace knows how to factor the vibes pages into her grading. **BLOCKED: Susan to provide updated LIKE rubric with website_content vector.** Susan manages rubric prompts in a separate Claude project.

**AGENT_CONFIG:**

```python
"select_culture_pages": {
    "system_prompt": "job_analyst_grace.txt",
    "task_prompt": "220_select_culture_pages.txt",
    "cached_blocks": [],
    "uncached_blocks": [],
    "response_format": "json",
    "context_format": "culture_pages_{index}",
    "response_schema": {
        "selected_pages": {"type": "list", "required": True},
        "reason": {"type": "str", "required": False},
    },
}
```

**Layer:** src/core/roster.py (get_company_data coat-check handler), src/external/playwright.py (scrape), src/external/anthropic.py (do_task), src/utils/config.py (CONSULT_CONFIG + AGENT_CONFIG + ROSTER_CONFIG)

**Dependencies:**

* src/external/anthropic.py (do_task for page selection)
* src/external/playwright.py (scrape_visible_text)
* Nav links coat-check already implemented in roster.get_company_data

# Prep Company Culture Pages

**Scope:** Add "website_content": "website_content" to ROSTER_CONFIG\["company_data_keys"\]. This registers the key so roster.get_company_data knows it's a self-healable key with a fetch-on-missing handler (same pattern as nav_links). Add AGENT_CONFIG task definition for select_culture_pages: system_prompt job_analyst_grace.txt, task_prompt 220_select_culture_pages.txt (to be created), response_schema {selected_pages: list required, reason: str optional}, response_format json. Add CONSULT_CONFIG entry: culture_pages_max (e.g. 5).

**Layer:** src/utils/config.py (ROSTER_CONFIG, AGENT_CONFIG, CONSULT_CONFIG)

## Metadata

* URL: [AST-194](https://linear.app/astralcareermatch/issue/AST-194/sub-register-website-content-as-coat-check-key)
* Identifier: [AST-194](https://linear.app/astralcareermatch/issue/AST-194/sub-register-website-content-as-coat-check-key)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Consult](https://linear.app/astralcareermatch/project/astral-consult-06e1069cc556). Sends content and prompts to an AI agent for analysis, saving the results for each evaluation and graduating those that pass.
* Created: 2026-02-18T22:25:56.326Z
* Updated: 2026-02-20T00:49:47.881Z

---

# Prep Company Culture Pages

**Scope:** Refactor roster.get_company_data from hardcoded nav_links if/else to select/case dispatch on key. Current code: `if key != nav_links_key: return None` — replace with dispatch: case nav_links_key → existing fetch logic, case website_content_key → new handler, default → return None. Website_content handler: (1) get homepage text + nav_links from company_data (nav_links via its own coat-check if needed), (2) call do_task(select_culture_pages) with homepage text + nav_links for AI to pick vibes pages, (3) scrape selected pages via playwright.scrape_visible_text, (4) save \[{url, content}\] array to company_data\["website_content"\], (5) return the content. On any failure, return None (no empty value stored). Caller never knows whether it was cached or freshly fetched.

**Layer:** src/core/roster.py (get_company_data)

## Metadata

* URL: [AST-195](https://linear.app/astralcareermatch/issue/AST-195/sub-refactor-get-company-data-dispatch-website-content-handler)
* Identifier: [AST-195](https://linear.app/astralcareermatch/issue/AST-195/sub-refactor-get-company-data-dispatch-website-content-handler)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Consult](https://linear.app/astralcareermatch/project/astral-consult-06e1069cc556). Sends content and prompts to an AI agent for analysis, saving the results for each evaluation and graduating those that pass.
* Created: 2026-02-18T22:25:57.412Z
* Updated: 2026-02-20T00:49:47.911Z

---

# Prep Company Culture Pages

**Scope:** Create data/agents/\_taskprompts/220_select_culture_pages.txt. Instructions for Grace to select culture-relevant pages from provided homepage text and nav links. Pages to consider: Homepage, About Us, Mission/Values, Product/Services, Blog (first page only). Pages to ignore: Careers, Contact, Legal, Privacy, Investors, Press. Max pages from config. Return selected_pages as list of URLs.

**Layer:** data/agents/\_taskprompts/

## Metadata

* URL: [AST-196](https://linear.app/astralcareermatch/issue/AST-196/sub-create-select-culture-pages-task-prompt)
* Identifier: [AST-196](https://linear.app/astralcareermatch/issue/AST-196/sub-create-select-culture-pages-task-prompt)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Consult](https://linear.app/astralcareermatch/project/astral-consult-06e1069cc556). Sends content and prompts to an AI agent for analysis, saving the results for each evaluation and graduating those that pass.
* Created: 2026-02-18T22:25:58.740Z
* Updated: 2026-02-20T00:49:47.944Z

---

# Prep Company Culture Pages

**Scope:** Failure handling within the fetch-on-missing handler. nav_links missing: coat-check fetches them via existing nav_links handler (same as find_job_page uses) — no fake default paths. AI page selection task fails: return None to caller. Individual page scrape fails (404, bot block): skip that page, continue with remaining. ALL selected page scrapes fail: return None to caller. Do NOT store empty website_content on failure — that would mask the problem on retry and prevent the coat-check from re-triggering after the issue is fixed.

**Error flow (no exception propagation):** roster.get_company_data returns None on any failure → \_prep_live_content receives None → \_prep_live_content calls tracker.transition_state to set job to NEED_WEBSITE_CONTENT → \_prep_live_content returns False → consult_like returns {success: False} → CLI logs and continues batch.

**State machine addition:** Add NEED_WEBSITE_CONTENT to JOB_STATES and job_state_transitions (from PASSED_DO only). Jobs in this state need investigation but the coat-check will re-trigger on retry once the underlying issue is resolved (no empty value stored to block it).

**Layer:** src/core/roster.py (get_company_data handler), src/core/consult.py (\_prep_live_content), src/utils/config.py (JOB_STATES, job_state_transitions)

## Metadata

* URL: [AST-197](https://linear.app/astralcareermatch/issue/AST-197/sub-failure-handling-for-website-content-fetch)
* Identifier: [AST-197](https://linear.app/astralcareermatch/issue/AST-197/sub-failure-handling-for-website-content-fetch)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Consult](https://linear.app/astralcareermatch/project/astral-consult-06e1069cc556). Sends content and prompts to an AI agent for analysis, saving the results for each evaluation and graduating those that pass.
* Created: 2026-02-18T22:25:59.750Z
* Updated: 2026-02-20T00:49:47.972Z

---

# Prep Company Culture Pages

**Scope:** BLOCKED — waiting on Susan. The LIKE rubric (207_LIKE_RUBRIC.txt) needs a new grading vector that instructs the JA (Grace) on how to use the company website_content in her LIKE analysis. Susan manages rubric prompts in a separate Claude project and will provide the updated rubric file. Once received: drop in the updated 207_LIKE_RUBRIC.txt, add the new vector to CONSULT_CONFIG consult_like vectors array with appropriate {name, grade_scores} entry.

**Layer:** data/agents/content/207_LIKE_RUBRIC.txt, src/utils/config.py (CONSULT_CONFIG vectors)

## Metadata

* URL: [AST-198](https://linear.app/astralcareermatch/issue/AST-198/sub-like-rubric-website-content-vector)
* Identifier: [AST-198](https://linear.app/astralcareermatch/issue/AST-198/sub-like-rubric-website-content-vector)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Consult](https://linear.app/astralcareermatch/project/astral-consult-06e1069cc556). Sends content and prompts to an AI agent for analysis, saving the results for each evaluation and graduating those that pass.
* Created: 2026-02-18T22:26:00.797Z
* Updated: 2026-02-20T00:49:48.015Z

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
