# AST-181 — Fetch Grades

<!-- linear-archive: AST-181 archived 2026-06-03 -->

## Linear archive (AST-181)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-181/fetch-grades  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** susan  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Refactor [consult.py](<http://consult.py>) grade functions to follow established patterns, call the correct agents with proper content and cached candidate context, and receive validated grade arrays back. Each function takes a job dict (+ company dict for LIKE), uses a shared content-prep helper, calls do_task, audits the response, and returns validated grades. No grade interpretation, no state transitions — just clean grades from the agents.

**Acceptance Criteria:**

**Function Signatures:**

```python
async def consult_get(job: Dict) -> Dict
async def consult_do(job: Dict) -> Dict
async def consult_like(job: Dict, company: Dict) -> Dict
```

**Agent Assignments:**

Each consult task uses a different agent based on what value it returns beyond grades:

* consult_get — Atlas, ATS expert (ats_expert_atlas.txt). Returns grades + resume optimization recommendations reusable by resume editor agent post-LIKE. Rename 300_atlas_atswonk.txt to ats_expert_atlas.txt to match {role}\_{name}.txt convention.
* consult_do — Grace, job analyst (job_analyst_grace.txt). Returns grades + cover letter topic recommendations.
* consult_like — Grace, job analyst (job_analyst_grace.txt). Returns grades (pending rubric update with website_content vector from Susan).

**Cache Strategy (Cache = Money):**

Each task escalates cached candidate content. Cached blocks are loaded once per prompt and reused across calls with the same content.

* GET: resume_base.txt + linkedinprofile.txt (cached). JD is live_content (uncached).
* DO: everything from GET + job_requirements.txt (cached). JD is live_content (uncached).
* LIKE: everything from DO + private_history.txt (cached). JD + company website_content are live_content (uncached — company vibes change per job).

**Shared Content Prep:**

\_prep_live_content(job, company=None) helper assembles live_content for the agent call. JD is obtained via tracker.get_job_data coat-check (state machine guarantees it exists at PASSED_JD, but we always go through tracker — no end-runs around tracker to access job data). For LIKE, company website_content is obtained via roster.get_company_data coat-check (transparently fetches if missing — see Prep Company Culture Pages feature). If website_content fetch fails, \_prep_live_content calls tracker.transition_state to set job to NEED_WEBSITE_CONTENT and returns False. All three functions use this helper — DRY without over-abstracting.

**AI Response Shape (common pattern):**

All three return the same shape with a generic grades key:

```json
{
    "jobid": "str",
    "company": "str",
    "title": "str",
    "grades": [{"vector": "str", "grade": "A-F or X", "reason": "10-20 words"}, ...],
    "dealbreakers": "str",
    "clarifications": "str",
    "overall_assessment": "str",
    "ja_notes": "str"
}
```

The quantity and names of vectors are config-driven (defined in CONSULT_CONFIG per task). Code never hardcodes vector counts.

**AGENT_CONFIG Updates:**

Rename task keys from score_get/score_do/score_like to consult_get/consult_do/consult_like. Update context_format accordingly.

* consult_get: system_prompt to ats_expert_atlas.txt; response_schema with grades items_schema (vector/grade/reason); cached_blocks: CANDIDATE_RESUME + LINKEDIN_PROFILE
* consult_do: response_schema with grades items_schema; cached_blocks: add JOB_REQUIREMENTS (candidate/job_requirements.txt)
* consult_like: response_schema with grades items_schema; cached_blocks: add JOB_REQUIREMENTS + PRIVATE_HISTORY (candidate/private_history.txt); review whether CANDIDATE_PREFERENCES (preferences_template.txt) still needed alongside private_history

**Task Prompt Updates:**

* GET (211_GET-(((SCORE))).txt): update voice for Atlas (ATS expert)
* DO (212_DO-(((SCORE))).txt): reference JOB_REQUIREMENTS cached block
* LIKE (213_LIKE-(((SCORE))).txt): replace {{{companies/<company>\_website.json}}} with language indicating company context is in the job data section below; reference PRIVATE_HISTORY block

**Audit Rule:** Agent response audited immediately after do_task, before any grade interpretation.

**Cleanup:** Remove score_job_full (premature pipeline logic — pipeline orchestration belongs in CLI).

**Layer:** src/core/consult.py, src/utils/config.py (AGENT_CONFIG), data/agents/\_taskprompts/, data/agents/\_systemprompts/

**Dependencies:**

* src/external/anthropic.py (do_task, items_schema validation already implemented)
* src/core/tracker.py (get_job_data coat-check for JD, transition_state for NEED_WEBSITE_CONTENT on LIKE failure)
* src/core/roster.py (get_company_data coat-check for website_content — Prep Company Culture Pages feature)

# Fetch Grades

**Scope:** Rename data/agents/*systemprompts/300_atlas_atswonk.txt to ats_expert_atlas.txt. Matches {role}*{name}.txt convention used by job_analyst_grace.txt and gate_keeper_danny.txt. No content changes to the prompt itself.

**Layer:** data/agents/\_systemprompts/

## Metadata

* URL: [AST-184](https://linear.app/astralcareermatch/issue/AST-184/sub-rename-atlas-system-prompt)
* Identifier: [AST-184](https://linear.app/astralcareermatch/issue/AST-184/sub-rename-atlas-system-prompt)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Consult](https://linear.app/astralcareermatch/project/astral-consult-06e1069cc556). Sends content and prompts to an AI agent for analysis, saving the results for each evaluation and graduating those that pass.
* Created: 2026-02-18T22:25:44.749Z
* Updated: 2026-02-19T20:36:31.229Z

---

# Fetch Grades

**Scope:** Rename task keys score_get/score_do/score_like to consult_get/consult_do/consult_like. Update context_format to consult_get\_{index}, consult_do\_{index}, consult_like\_{index}. Replace stub response_schemas (task_success + reason) with schemas matching actual rubric output. Common shape: {jobid (str, optional), company (str, optional), title (str, optional), grades (list, required, items_schema: {vector: str required, grade: str required, reason: str required}), dealbreakers (str, optional), clarifications (str, optional), overall_assessment (str, optional), ja_notes (str, optional)}. All three tasks use the same grades key — vector names and count are config-driven in CONSULT_CONFIG, not in the response schema. Change consult_get system_prompt from job_analyst_grace.txt to ats_expert_atlas.txt.

**Layer:** src/utils/config.py (AGENT_CONFIG\["tasks"\])

## Metadata

* URL: [AST-185](https://linear.app/astralcareermatch/issue/AST-185/sub-agent-config-for-consult-tasks)
* Identifier: [AST-185](https://linear.app/astralcareermatch/issue/AST-185/sub-agent-config-for-consult-tasks)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Consult](https://linear.app/astralcareermatch/project/astral-consult-06e1069cc556). Sends content and prompts to an AI agent for analysis, saving the results for each evaluation and graduating those that pass.
* Created: 2026-02-18T22:25:45.731Z
* Updated: 2026-02-19T20:36:31.263Z

---

# Fetch Grades

**Scope:** Ensure each task's cached_blocks match what the rubric and task prompt actually need. GET: CANDIDATE_RESUME (resume_base.txt) + LINKEDIN_PROFILE (linkedinprofile.txt) — already correct. DO: add JOB_REQUIREMENTS label with candidate/job_requirements.txt to existing blocks. LIKE: add JOB_REQUIREMENTS (candidate/job_requirements.txt) + PRIVATE_HISTORY (candidate/private_history.txt); review whether CANDIDATE_PREFERENCES (preferences_template.txt) is still needed alongside private_history or is redundant.

**Cache strategy:** Each task escalates cached content. GET: resume + linkedin. DO: + job_requirements. LIKE: + private_history. JD and company vibes are always uncached live_content.

**Layer:** src/utils/config.py (AGENT_CONFIG\["tasks"\] cached_blocks)

## Metadata

* URL: [AST-186](https://linear.app/astralcareermatch/issue/AST-186/sub-align-cached-blocks-per-consult-task)
* Identifier: [AST-186](https://linear.app/astralcareermatch/issue/AST-186/sub-align-cached-blocks-per-consult-task)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Consult](https://linear.app/astralcareermatch/project/astral-consult-06e1069cc556). Sends content and prompts to an AI agent for analysis, saving the results for each evaluation and graduating those that pass.
* Created: 2026-02-18T22:25:47.106Z
* Updated: 2026-02-19T20:36:31.314Z

---

# Fetch Grades

**Scope:** GET (211_GET-(((SCORE))).txt): update voice/framing for Atlas (ATS expert) instead of Grace. Ensure it references cached block labels GET_RUBRIC, CANDIDATE_RESUME, LINKEDIN_PROFILE. DO (212_DO-(((SCORE))).txt): add reference to JOB_REQUIREMENTS cached block so rubric can use candidate strengths/weaknesses context. LIKE (213_LIKE-(((SCORE))).txt): replace {{{companies/<company>\_website.json}}} file reference with language indicating company website content is included in the job data section below; add reference to PRIVATE_HISTORY cached block.

**Layer:** data/agents/\_taskprompts/

## Metadata

* URL: [AST-187](https://linear.app/astralcareermatch/issue/AST-187/sub-update-task-prompt-files)
* Identifier: [AST-187](https://linear.app/astralcareermatch/issue/AST-187/sub-update-task-prompt-files)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Consult](https://linear.app/astralcareermatch/project/astral-consult-06e1069cc556). Sends content and prompts to an AI agent for analysis, saving the results for each evaluation and graduating those that pass.
* Created: 2026-02-18T22:25:48.809Z
* Updated: 2026-02-19T20:36:31.350Z

---

# Fetch Grades

**Scope:** Add \_prep_live_content(job, company=None) helper in [consult.py](<http://consult.py>). Obtains JD via tracker.get_job_data coat-check (always go through tracker — no end-runs around tracker to access job data). If company provided, obtains website_content via roster.get_company_data coat-check (transparently fetches if missing). If website_content fetch returns None (failure), \_prep_live_content calls tracker.transition_state to set job to NEED_WEBSITE_CONTENT and returns False. Otherwise assembles JD + optional company context as live_content string. Refactor consult_get(job), consult_do(job), consult_like(job, company) to use helper, call do_task with correct task_key, audit response via add_agent_response_entry immediately after do_task (before any grade interpretation), return result. Delete score_job_full (premature pipeline orchestration — belongs in CLI layer).

**Pattern per function:**

```python
async def consult_get(job: Dict) -> Dict:
    task_key = "consult_get"
    aid = job["astral_job_id"]
    live_content = await _prep_live_content(job)
    if not live_content:
        return {"success": False, "error": f"live_content prep failed for {aid}"}
    result = await do_task(task_key=task_key, live_content=live_content, index=aid)
    api_resp = result.get("api_response")
    request_id = getattr(api_resp, "id", None) if api_resp else None
    add_agent_response_entry(task_key=task_key, entity_type="job", entity_id=aid, raw_response=result.get("parsed_response"), request_id=request_id)
    return result
```

consult_do identical pattern, different task_key. consult_like takes (job, company), calls \_prep_live_content(job, company). For LIKE, \_prep_live_content returning False means website_content failed and state is already set to NEED_WEBSITE_CONTENT — consult_like just returns {success: False}, CLI continues batch.

**Testing:** GET and DO can be tested independently to verify the consult pattern. LIKE tested explicitly to verify culture_page scrape integration.

**Layer:** src/core/consult.py

## Metadata

* URL: [AST-188](https://linear.app/astralcareermatch/issue/AST-188/sub-prep-live-content-helper-and-refactor-consult-functions)
* Identifier: [AST-188](https://linear.app/astralcareermatch/issue/AST-188/sub-prep-live-content-helper-and-refactor-consult-functions)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Consult](https://linear.app/astralcareermatch/project/astral-consult-06e1069cc556). Sends content and prompts to an AI agent for analysis, saving the results for each evaluation and graduating those that pass.
* Created: 2026-02-18T22:25:49.818Z
* Updated: 2026-02-19T20:36:31.387Z

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
