# AST-139 — Retrofit Batch-Count to Existing CLIs

<!-- linear-archive: AST-139 archived 2026-06-03 -->

## Linear archive (AST-139)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-139/retrofit-batch-count-to-existing-clis  
**Status at archive:** Done  
**Project:** Astral Dispatcher  
**Assignee:** susan  
**Priority / estimate:** Medium / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Add batch-count parameter and run-until-empty loop to existing CLI scripts. Enables cron-friendly execution where a single invocation processes all available records.

**Acceptance Criteria:**

**CLI scripts to update:**

* a_ja_prefilter
* b_gk_locate_job_page
* c_gk_parse_job_list
* d_gk_gaze_job_lists

**Behavior:**

* \--batch-count N: run up to N batches
* No flag: run until no records left (default for cron)
* \--batch-count 1: run one batch (manual/testing, preserves current behavior)

**Pattern:**
Same outer loop as Consult Batch Runner:

```python
batches_run = 0
while True:
    if batch_count and batches_run >= batch_count:
        break
    (batch_id, entities) = get_new_batch(...)
    if not entities:
        break
    try:
        process(entities)
    finally:
        clear_batch(batch_id)
    batches_run += 1
```

**Note:** Each CLI already has its own processing logic. This issue only adds the outer loop and CLI parameter — no changes to the processing internals.

**Layer:** src/cli/

# Retrofit Batch-Count to Existing CLIs

**Scope:** a_ja_prefilter, b_gk_locate_job_page, c_gk_parse_job_list, d_gk_gaze_job_lists: --batch-count N, same outer loop as Consult Batch Runner; no change to processing internals.

**Ref:** consult-features Behavior; Pattern; ASTRAL_CODE_RULES 2.4.

## Metadata

* URL: [AST-168](https://linear.app/astralcareermatch/issue/AST-168/sub-add-batch-count-and-run-until-empty-to-prefilter-and-gatekeeper)
* Identifier: [AST-168](https://linear.app/astralcareermatch/issue/AST-168/sub-add-batch-count-and-run-until-empty-to-prefilter-and-gatekeeper)
* Status: Done
* Priority: Medium
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Infrastructure](https://linear.app/astralcareermatch/project/astral-infrastructure-8a6fd1dff6b8).
* Created: 2026-02-10T21:45:25.044Z
* Updated: 2026-02-20T01:27:23.894Z

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
