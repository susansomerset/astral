# AST-182 — Render Verdict

<!-- linear-archive: AST-182 archived 2026-06-03 -->

## Linear archive (AST-182)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-182/render-verdict  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** susan  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Extend render_verdict to support scored grading for the consult pipeline. F is always death (any F in any vector = fail_state). For non-F results, each vector has its own per-grade score table calibrated by importance. Scores are normalized to a ten-point scale as a percentage of total possible, with X-graded vectors excluded from both numerator and denominator. Includes CONSULT_CONFIG scoring entries, grade persistence, and CLI batch scripts for consult steps.

**Acceptance Criteria:**

**render_verdict Extension:**

render_verdict already handles grading_mode "binary" (PASS/F grades, any F = fail_state) for qualify_job_listings and evaluate_jd. Extend to support grading_mode "scored" for consult_get, consult_do, consult_like:

* Input: \[{vector, grade (A-F or X), reason}\] array from AI response
* F in ANY vector = instant death → fail_state (regardless of other scores)
* X in a vector = unable to assess → exclude that vector entirely from the calculation (removed from both numerator and denominator)
* If no F's: for each non-X vector, look up grade in that vector's grade_scores table. Sum actual scores (numerator). Sum A-values for non-X vectors (denominator = total possible). Score = (numerator / denominator) \* 10 → ten-point scale.
* Score compared against config-driven pass_threshold: >= threshold → pass_state, below → fail_state
* Return (to_state, score) tuple

**CONSULT_CONFIG Entries:**

Vectors are defined as an array of objects per task, each with a name and a grade_scores table. High-importance vectors have large A values, low-importance vectors have small A values, but F is always fatal regardless of importance:

```python
CONSULT_CONFIG = {
    "consult_get": {
        "input_state": "PASSED_JD",
        "pass_state": "PASSED_GET",
        "fail_state": "FAILED_GET",
        "batch_size": 10,
        "grading_mode": "scored",
        "vectors": [
            {"name": "TITLE_MATCH", "grade_scores": {"A": 50, "B": 40, "C": 20, "D": 5}},
            {"name": "YEARS_EXPERIENCE", "grade_scores": {"A": 30, "B": 20, "C": 10, "D": 2}},
            {"name": "INDUSTRY_FIT", "grade_scores": {"A": 10, "B": 8, "C": 4, "D": 0}},
            ...
        ],
        "pass_threshold": 6.0,
    },
    "consult_do": { ... },
    "consult_like": {
        ...
        "requires_company": True,
    },
}
```

Scoring example: if 3 vectors with A-values 50+30+10=90, and grades are A(50)+B(20)+X → X vector excluded, so numerator=70, denominator=80 (50+30), score = (70/80)\*10 = 8.75.

**Grade Persistence:**

After render_verdict, save full grade array + calculated numeric score to job_data:

* grades (the full \[{vector, grade, reason}\] array from the AI)
* score (the calculated ten-point numeric score)

Keyed by task: consult_get saves to get_grades + get_score, consult_do saves to do_grades + do_score, consult_like saves to like_grades + like_score.

**State Machine:**

| Function | Input State | Pass | Fail | Other |
| -- | -- | -- | -- | -- |
| consult_get | PASSED_JD | PASSED_GET | FAILED_GET | — |
| consult_do | PASSED_GET | PASSED_DO | FAILED_DO | — |
| consult_like | PASSED_DO | PASSED_LIKE | FAILED_LIKE | NEED_WEBSITE_CONTENT (website_content fetch failed — \_prep_live_content sets state via tracker, returns False, batch continues) |

**CLI Batch Scripts:**

h_ja_consult_get, i_ja_consult_do, k_ja_consult_like — Pattern B (per-job iteration) following evaluate_jd_batch.py template:

* \--batch-count parameter, run-until-empty loop
* Claim batch from input_state, iterate jobs, call consult function, render verdict, save + transition, release batch
* For k_ja_consult_like: fetch company record, consult_like calls \_prep_live_content which triggers website_content coat-check transparently

**Error Handling:**

* AI returns success=False: transition to fail_state (not an exception)
* \_prep_live_content returns False (website_content fetch failed): state already set to NEED_WEBSITE_CONTENT by \_prep_live_content via tracker — consult function returns {success: False}, CLI skips to next job
* Exception raised (network, API): log, skip job, continue batch
* Batch always released in finally block
* Failed jobs stay in current state for retry if exception prevented transition

**Logging:**

* Batch start: batch_id, state, jobs claimed
* Per-job: astral_job_id, score, pass/fail
* Batch end: passed/failed/error counts
* Loop end: total batches, total jobs processed

**Layer:** src/core/consult.py (render_verdict), src/utils/config.py (CONSULT_CONFIG), src/cli/ (CLI scripts)

**Dependencies:**

* Fetch Grades (functions must return validated grades before we can qualify them)
* src/core/tracker.py (save_job_data, transition_state, get_new_job_batch, clear_job_batch)

# Render Verdict

**Scope:** Add CONSULT_CONFIG entries for consult_get, consult_do, consult_like with: input_state, pass_state, fail_state, batch_size, grading_mode ("scored"), vectors (array of {name: str, grade_scores: {A: int, B: int, C: int, D: int}} objects — each vector defines its own score table calibrated by importance), pass_threshold (e.g. 6.0). F is always instant death regardless of vector. X excludes the vector from scoring entirely. High-importance vectors have large A values (e.g. A=50), low-importance vectors have small A values (e.g. A=10). The quantity of vectors is config-driven. For consult_like: requires_company=True. No magic numbers per ASTRAL_CODE_RULES 1.4.

Also add NEED_WEBSITE_CONTENT to JOB_STATES (from PASSED_DO) and job_state_transitions.

**Layer:** src/utils/config.py (CONSULT_CONFIG, JOB_STATES, TRACKER_CONFIG)

## Metadata

* URL: [AST-189](https://linear.app/astralcareermatch/issue/AST-189/sub-consult-config-consult-task-entries)
* Identifier: [AST-189](https://linear.app/astralcareermatch/issue/AST-189/sub-consult-config-consult-task-entries)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Consult](https://linear.app/astralcareermatch/project/astral-consult-06e1069cc556). Sends content and prompts to an AI agent for analysis, saving the results for each evaluation and graduating those that pass.
* Created: 2026-02-18T22:25:50.960Z
* Updated: 2026-02-19T22:08:52.793Z

---

# Render Verdict

**Scope:** render_verdict currently handles grading_mode "binary" (flat dict {category: "PASS"|"F"}, any F -> fail_state, else pass_state). Extend to support grading_mode "scored": input is \[{vector, grade (A-F or X), reason}\] array from AI response. Processing order: (1) validate vector names match config vectors exactly (catch agent creativity), (2) F in ANY vector = instant death → fail_state, (3) exclude X-graded vectors from calculation entirely, (4) for each non-X vector look up grade in that vector's grade_scores → sum = numerator, (5) sum A-values for non-X vectors → denominator (total possible), (6) score = (numerator / denominator) \* 10, (7) compare score against pass_threshold → pass_state or fail_state. Return (to_state, score) tuple.
**Layer:** src/core/consult.py (render_verdict), src/utils/config.py (reads CONSULT_CONFIG)

## Metadata

* URL: [AST-190](https://linear.app/astralcareermatch/issue/AST-190/sub-extend-render-verdict-for-scored-grading)
* Identifier: [AST-190](https://linear.app/astralcareermatch/issue/AST-190/sub-extend-render-verdict-for-scored-grading)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Consult](https://linear.app/astralcareermatch/project/astral-consult-06e1069cc556). Sends content and prompts to an AI agent for analysis, saving the results for each evaluation and graduating those that pass.
* Created: 2026-02-18T22:25:51.960Z
* Updated: 2026-02-19T22:08:52.831Z

---

# Render Verdict

**Scope:** After render_verdict returns (to_state, score), save the full grade array + calculated numeric score to job_data via tracker.save_job_data. Keyed by task: consult_get saves to get_grades + get_score, consult_do saves to do_grades + do_score, consult_like saves to like_grades + like_score. The grades value is the full \[{vector, grade, reason}\] array from the AI — preserved for audit. Call tracker.transition_state with to_state. Agent response audit already handled by Fetch Grades functions; this step adds the save + transition wrapper that the CLI calls.

**Layer:** src/core/consult.py, src/core/tracker.py (save_job_data, transition_state)

## Metadata

* URL: [AST-191](https://linear.app/astralcareermatch/issue/AST-191/sub-save-grades-and-score-to-job-data)
* Identifier: [AST-191](https://linear.app/astralcareermatch/issue/AST-191/sub-save-grades-and-score-to-job-data)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Consult](https://linear.app/astralcareermatch/project/astral-consult-06e1069cc556). Sends content and prompts to an AI agent for analysis, saving the results for each evaluation and graduating those that pass.
* Created: 2026-02-18T22:25:53.197Z
* Updated: 2026-02-19T22:08:52.873Z

---

# Render Verdict

**Scope:** Create h_ja_consult_get, i_ja_consult_do, k_ja_consult_like CLI scripts. Pattern B (per-job iteration) following evaluate_jd_batch.py template. Each script: --batch-count parameter (default no limit, run until empty), claim batch from CONSULT_CONFIG\[task\]\["input_state"\], iterate jobs, call consult function, render verdict, save grades + score, transition state, release batch in finally block. For k_ja_consult_like: fetch company record, pass to consult_like (website_content coat-check handles itself). If website_content fetch fails, \_prep_live_content already set NEED_WEBSITE_CONTENT state via tracker and returned False — consult_like returns {success: False}, CLI just logs and continues to next job. No special exception handling needed in CLI for this case. CLI imports core and utils only — never external, never data. Suppress HTTP logging at startup.

**Layer:** src/cli/

## Metadata

* URL: [AST-192](https://linear.app/astralcareermatch/issue/AST-192/sub-cli-scripts-for-consult-batch-processing)
* Identifier: [AST-192](https://linear.app/astralcareermatch/issue/AST-192/sub-cli-scripts-for-consult-batch-processing)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Consult](https://linear.app/astralcareermatch/project/astral-consult-06e1069cc556). Sends content and prompts to an AI agent for analysis, saving the results for each evaluation and graduating those that pass.
* Created: 2026-02-18T22:25:54.353Z
* Updated: 2026-02-19T22:08:52.904Z

---

# Render Verdict

**Scope:** AI returns success=False: transition to fail_state (not an exception). Exception raised (network, API): log error, skip job, continue batch. Batch always released in finally block. Failed jobs stay in current state for retry if exception prevented transition. Logging: batch start (batch_id, state, count claimed), per-job (astral_job_id, numeric score, pass/fail, brief notes), batch end (passed/failed/error counts), loop end (total batches, total jobs). Follows existing pattern from evaluate_jd_batch.py.

**Layer:** src/cli/

## Metadata

* URL: [AST-193](https://linear.app/astralcareermatch/issue/AST-193/sub-error-handling-and-logging-for-consult-clis)
* Identifier: [AST-193](https://linear.app/astralcareermatch/issue/AST-193/sub-error-handling-and-logging-for-consult-clis)
* Status: Done
* Priority: Medium
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Consult](https://linear.app/astralcareermatch/project/astral-consult-06e1069cc556). Sends content and prompts to an AI agent for analysis, saving the results for each evaluation and graduating those that pass.
* Created: 2026-02-18T22:25:55.372Z
* Updated: 2026-02-19T22:08:52.937Z

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
