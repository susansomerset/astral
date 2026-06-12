# AST-140 — Add ADDED_JD_SCRAPE to Job State Machine

<!-- linear-archive: AST-140 archived 2026-06-03 -->

## Linear archive (AST-140)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-140/add-added-jd-scrape-to-job-state-machine  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** susan  
**Priority / estimate:** High / 1  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Add the ADDED_JD_SCRAPE state to JOB_STATES and update job_state_transitions in [config.py](<http://config.py>). This state represents a job whose full description has been scraped by the gatekeeper (step f) and is ready for AI evaluation (step g).

**Acceptance Criteria:**

**JOB_STATES update:**

```python
JOB_STATES = {
    "NEW": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
    "PASSED_JOBLIST": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
    "FAILED_JOBLIST": {},
    "ADDED_JD_SCRAPE": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
    "FAILED_TECHNICAL": {},
    "PASSED_JD": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
    "FAILED_JD": {},
    ...
}
```

**job_state_transitions update:**

```python
("PASSED_JOBLIST", "ADDED_JD_SCRAPE"),   # gatekeeper scrape success
("PASSED_JOBLIST", "FAILED_TECHNICAL"),   # gatekeeper scrape failure
("ADDED_JD_SCRAPE", "PASSED_JD"),         # AI evaluation pass
("ADDED_JD_SCRAPE", "FAILED_JD"),         # AI evaluation fail
```

**Removes:**

* ("PASSED_JOBLIST", "PASSED_JD") — no longer a direct transition
* ("PASSED_JOBLIST", "FAILED_JD") — no longer a direct transition

**Context:**
Previously PASSED_JOBLIST to PASSED_JD was a single step. With the gatekeeper scrape (step f) separated from AI evaluation (step g), we need an intermediate state to track which jobs have been scraped and are ready for JD evaluation vs. still waiting for scrape.

**Layer:** src/utils/config.py

# Add ADDED_JD_SCRAPE to Job State Machine

**Scope:** Add ADDED_JD_SCRAPE with batch_criteria; add (PASSED_JOBLIST, ADDED_JD_SCRAPE), (PASSED_JOBLIST, FAILED_TECHNICAL), (ADDED_JD_SCRAPE, PASSED_JD), (ADDED_JD_SCRAPE, FAILED_JD); remove (PASSED_JOBLIST, PASSED_JD) and (PASSED_JOBLIST, FAILED_JD).

**Ref:** consult-features JOB_STATES update; job_state_transitions; Context.

## Metadata

* URL: [AST-169](https://linear.app/astralcareermatch/issue/AST-169/sub-job-states-and-job-state-transitions)
* Identifier: [AST-169](https://linear.app/astralcareermatch/issue/AST-169/sub-job-states-and-job-state-transitions)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Infrastructure](https://linear.app/astralcareermatch/project/astral-infrastructure-8a6fd1dff6b8).
* Created: 2026-02-10T21:45:26.320Z
* Updated: 2026-02-20T01:27:29.976Z

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
