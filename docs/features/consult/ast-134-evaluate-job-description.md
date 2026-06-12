# AST-134 — Evaluate Job Description

<!-- linear-archive: AST-134 archived 2026-06-03 -->

## Linear archive (AST-134)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-134/evaluate-job-description  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** susan  
**Priority / estimate:** Medium / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Per-job Consult function for dealbreaker screening of full job descriptions. Binary pass/fail gate — checks remote status, mission/domain, salary, role type, and W2 status. Only explicit dealbreakers fail; when in doubt, pass and let the scoring pipeline evaluate.

**Acceptance Criteria:**

**Function Signature:**

```python
async def evaluate_jd(job: Dict) -> Dict
```

**Live Content Assembly:**

Pulls the scraped job description and original thumbprint from job_data:

```python
async def evaluate_jd(job: Dict) -> Dict:
    live_content = build_jd_content(job)
    result = await do_task(
        task_key="evaluate_jd",
        live_content=live_content,
        index=job["astral_job_id"],
    )
    return result
```

**Live Content Sources:**

* job_data\["job_description"\]: Full JD text scraped by gatekeeper (step f)
* job_data\["raw_job_listing"\]: Original thumbprint for cross-reference context

**AI Response (from 102 rubric):**

Pass:

```json
{
    "verdict": "PASS",
    "notes": "Fully remote, $190k-$230k, patient care platform, cross-functional leadership.",
    "company_tenword": "<ten word company summary>",
    "job_summary": "<simple paragraph>"
}
```

Fail:

```json
{
    "verdict": "FAIL",
    "reason": "Hybrid/office requirement exceeds 1x per month",
    "notes": "Requires 2-3 days per week in SF office"
}
```

**Failure Reason Categories (exact strings per 102 rubric):**

* Defense/Military domain (auto-fail)
* Security/Cybersecurity domain (auto-fail)
* Crypto/Blockchain domain (auto-fail)
* Fintech for ultra-rich/corporate optimization
* Salary below threshold
* Pure IC engineering role
* Pure management role
* Heavy junior PM language (support/help/contribute)
* Hybrid/office requirement exceeds 1x per month
* Freelance/1099 without W2 path
* Mission egregiously harmful

Structured failure reasons enable pattern analysis and false-negative review.

**Caller Responsibilities (CLI/batch runner):**

* Save result to job_data via tracker.save_job_data
* Transition PASS to PASSED_JD
* Transition FAIL to FAILED_JD

**State Machine:**

* Input state: ADDED_JD_SCRAPE
* Pass: PASSED_JD
* Fail: FAILED_JD

**AGENT_CONFIG:**

New task definition:

* task_key: evaluate_jd
* Task prompt references 102_JD_RUBRIC
* response_schema: verdict, reason (when fail), notes, company_tenword (when pass), job_summary (when pass)
* response_format: json

**Layer:** src/core/consult.py

**Dependencies:**

* src/external/anthropic.py (do_task)
* AGENT_CONFIG evaluate_jd task definition
* Gatekeeper scrape (step f) must have populated job_data\["job_description"\]

# Evaluate Job Description

**Scope:** async def evaluate_jd(job: Dict) -> Dict; build_jd_content from job_data\["job_description"\] and job_data\["raw_job_listing"\]; do_task(task_key="evaluate_jd", ...).

**Layer:** src/core/consult.py

**Ref:** consult-features Function Signature; Live Content Assembly.

## Metadata

* URL: [AST-146](https://linear.app/astralcareermatch/issue/AST-146/sub-evaluate-jd-signature-and-live-content)
* Identifier: [AST-146](https://linear.app/astralcareermatch/issue/AST-146/sub-evaluate-jd-signature-and-live-content)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Consult](https://linear.app/astralcareermatch/project/astral-consult-06e1069cc556). Sends content and prompts to an AI agent for analysis, saving the results for each evaluation and graduating those that pass.
* Created: 2026-02-10T21:44:52.970Z
* Updated: 2026-02-20T01:28:41.657Z

---

# Evaluate Job Description

**Scope:** Pass: verdict, notes, company_tenword, job_summary; Fail: verdict, reason, notes. Enumerate exact failure reason strings per 102 rubric for pattern analysis.

**Ref:** consult-features AI Response; Failure Reason Categories.

## Metadata

* URL: [AST-147](https://linear.app/astralcareermatch/issue/AST-147/sub-response-schema-passfail-and-failure-reason-categories)
* Identifier: [AST-147](https://linear.app/astralcareermatch/issue/AST-147/sub-response-schema-passfail-and-failure-reason-categories)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Consult](https://linear.app/astralcareermatch/project/astral-consult-06e1069cc556). Sends content and prompts to an AI agent for analysis, saving the results for each evaluation and graduating those that pass.
* Created: 2026-02-10T21:44:54.085Z
* Updated: 2026-02-20T01:28:27.341Z

---

# Evaluate Job Description

**Scope:** Save to job_data; PASS to PASSED_JD, FAIL to FAILED_JD; input state ADDED_JD_SCRAPE.

**Ref:** consult-features Caller Responsibilities; State Machine.

## Metadata

* URL: [AST-148](https://linear.app/astralcareermatch/issue/AST-148/sub-caller-responsibilities-and-state-machine)
* Identifier: [AST-148](https://linear.app/astralcareermatch/issue/AST-148/sub-caller-responsibilities-and-state-machine)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Consult](https://linear.app/astralcareermatch/project/astral-consult-06e1069cc556). Sends content and prompts to an AI agent for analysis, saving the results for each evaluation and graduating those that pass.
* Created: 2026-02-10T21:44:55.149Z
* Updated: 2026-02-20T01:28:35.703Z

---

# Evaluate Job Description

**Scope:** New task evaluate_jd; 102_JD_RUBRIC; response_schema and response_format.

**Ref:** consult-features AGENT_CONFIG.

## Metadata

* URL: [AST-149](https://linear.app/astralcareermatch/issue/AST-149/sub-agent-config-evaluate-jd-task)
* Identifier: [AST-149](https://linear.app/astralcareermatch/issue/AST-149/sub-agent-config-evaluate-jd-task)
* Status: Done
* Priority: Medium
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Consult](https://linear.app/astralcareermatch/project/astral-consult-06e1069cc556). Sends content and prompts to an AI agent for analysis, saving the results for each evaluation and graduating those that pass.
* Created: 2026-02-10T21:44:56.231Z
* Updated: 2026-02-20T01:28:48.159Z

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
