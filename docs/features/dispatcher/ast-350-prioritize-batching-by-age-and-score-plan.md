<!-- linear-archive: AST-350 archived 2026-06-03 -->

## Linear archive (AST-350)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-350/prioritize-batching-by-age-and-score  
**Status at archive:** Done  
**Project:** Astral Dispatcher  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Allow the batch fetch to grab the best possible jobs based on age and score (don't do oldest first)

### Comments

_No comments._

---

---
name: AST-350 Latest Score Column
overview: Add a `latest_score REAL` column to the job table, write through from every scoring stage, include score in state history metadata, and use it to sort batch claims (highest score first) for consult pipeline states.
todos:
  - id: schema
    content: Add latest_score REAL column via _ensure_job_schema migration, update save_job, whitelist in _JOB_BATCH_SORT_COLUMNS, update claim_job_batch ORDER BY for DESC NULLS LAST when sort_by == latest_score
    status: completed
  - id: tracker
    content: Add optional score param to transition_job_state, write to state_history entry and latest_score column
    status: completed
  - id: consult
    content: Pass score from render_verdict to transition_job_state; add _render_score call in evaluate_jd_batch and pass score to transition
    status: completed
  - id: config
    content: Update JOB_STATES batch_criteria sort_by to latest_score for PASSED_JD, PASSED_DO, PASSED_GET
    status: completed
  - id: compile-lint
    content: Run python3 -m py_compile on changed files and tsc --noEmit, then commit
    status: pending
isProject: false
---

# AST-350: Prioritize Batching by Age and Score

## What changes

### 1. Schema migration — `src/data/database.py`
- Add `latest_score REAL` to the job table via `_ensure_job_schema` (same ALTER TABLE pattern already used for other columns)
- Add `latest_score` to `_JOB_BATCH_SORT_COLUMNS` whitelist
- Add `latest_score` as an accepted parameter in `save_job`
- Support `sort_order` (default `"ASC"`) in `claim_job_batch` so config can request `DESC NULLS LAST`:

```python
_JOB_BATCH_SORT_COLUMNS = frozenset({"rowid", "created_at", "updated_at", "state_changed_at", "latest_score"})

order_clause = (
    f"ORDER BY {sort_by} DESC NULLS LAST"
    if sort_by == "latest_score"
    else f"ORDER BY {sort_by} ASC NULLS FIRST"
    if sort_by and sort_by in _JOB_BATCH_SORT_COLUMNS
    else "ORDER BY rowid"
)
```

### 2. State transition — `src/core/tracker.py`
- `transition_job_state` gains an optional `score: Optional[float]` param
- Writes `score` into the state_history entry: `{"to_state": ..., "timestamp": ..., "batch_id": ..., "score": score}`
- Also calls `database.save_job(..., latest_score=score)` when score is not None

### 3. Consult scoring write-through — `src/core/consult.py`
- `render_verdict` already computes `score` — pass it to `transition_job_state` (one-liner change)
- `evaluate_jd_batch`: after `_render_pass_fail`, also call `_render_score` on the grades and pass score to `transition_job_state` (score doesn't affect verdict, just gets recorded)
- Skip `qualify_job_listings` for now — it's a single batch API call with less granular per-job scoring

### 4. Batch sort config — `src/utils/config.py`
Update `JOB_STATES` batch_criteria for the three consult input states:

```python
"PASSED_JD":  {"batch_criteria": {"limit": 10, "sort_by": "latest_score"}},  # scored by evaluate_jd
"PASSED_DO":  {"batch_criteria": {"limit": 10, "sort_by": "latest_score"}},  # scored by consult_do
"PASSED_GET": {"batch_criteria": {"limit": 10, "sort_by": "latest_score"}},  # scored by consult_get
```

(The DESC/NULLS LAST behavior is implicit when `sort_by == "latest_score"` in the DB layer.)

## Files touched
- [`src/data/database.py`](src/data/database.py) — migration, save_job, claim_job_batch, whitelist
- [`src/core/tracker.py`](src/core/tracker.py) — transition_job_state score param
- [`src/core/consult.py`](src/core/consult.py) — render_verdict + evaluate_jd_batch score passthrough
- [`src/utils/config.py`](src/utils/config.py) — JOB_STATES sort_by for 3 states

## Not changed
- `qualify_job_listings` scoring (batch API, more complex — separate ticket if wanted)
- Any UI changes (existing `do_score`/`get_score` display in `api_jobs.py` is unaffected)
- Pass/fail logic anywhere — purely additive
