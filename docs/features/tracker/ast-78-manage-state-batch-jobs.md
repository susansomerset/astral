# AST-78 — Manage State Batch Jobs

<!-- linear-archive: AST-78 archived 2026-06-03 -->

## Linear archive (AST-78)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-78/manage-state-batch-jobs  
**Status at archive:** Done  
**Project:** Astral Tracker  
**Assignee:** susan  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Batch processing operations for efficient job pipeline processing. Implements claim → process → release pattern to prevent concurrent processing and enable parallel batch execution.

**Acceptance Criteria:**

**Functions:**

**get_new_batch(state, limit):**

Input:

* state: str (job state to claim, e.g., "NEW", "PASSED_JOBLIST")
* limit: int (maximum jobs to claim)

Processing:

1. Generate batch_id (UUID)
2. Claim N unclaimed jobs: WHERE state=? AND batch_id IS NULL LIMIT ?
3. Set batch_id and batch_created_at on claimed jobs
4. Fetch and return claimed jobs

Returns:

* Tuple\[str, List\[Dict\[str, Any\]\]\]
* (batch_id, jobs) where jobs is list of full job records

Database:

* job table: UPDATE batch_id, batch_created_at WHERE state=? AND batch_id IS NULL LIMIT ?
* job table: SELECT \* FROM job WHERE batch_id=?

**get_batch(batch_id):**

Input:

* batch_id: str (UUID of batch to retrieve)

Processing:

* Fetch all jobs with this batch_id

Returns:

* List\[Dict\[str, Any\]\] (list of full job records)

Database:

* job table: SELECT \* FROM job WHERE batch_id=?

**clear_batch(batch_id):**

Input:

* batch_id: str (UUID of batch to release)

Processing:

* Set batch_id=NULL and batch_created_at=NULL for all jobs in batch
* Allows jobs to be reclaimed by future batches if needed

Returns:

* int (count of jobs released)

Database:

* job table: UPDATE batch_id=NULL, batch_created_at=NULL WHERE batch_id=?

**Batch Processing Flow:**

Typical usage by Consult/Gazer:

```python
# 1. Claim batch
(batch_id, jobs) = tracker.get_new_batch("NEW", 50)

try:
    # 2. Process each job
    for job in jobs:
        result = await process_job(job)
        
        # 3. Update job data
        tracker.save_job_data(job["astral_job_id"], result)
        
    # 4. Transition states
    job_ids = [job["astral_job_id"] for job in jobs]
    tracker.transition_state(job_ids, "PASSED_JOBLIST")
    
finally:
    # 5. Release batch (always runs)
    tracker.clear_batch(batch_id)
```

**Batch Locking:**

* Jobs in batch keep batch_id through state transition
* Prevents double-processing by concurrent runs
* batch_id explicitly cleared at end (success or failure)

**Concurrency:**

* Multiple batches can run concurrently on different states
* Same state cannot be double-processed (batch_id IS NULL check)
* Failed batches can be retried (clear_batch releases jobs)

**No Maximum Batch Size:**

* No artificial limit on batch size
* Caller determines appropriate batch size
* Allows flexibility for different processing patterns

**Database:**

* job table: batch_id, batch_created_at columns for locking
* Uses WHERE batch_id IS NULL to find unclaimed jobs

**Pattern Consistency:**

* Follows same claim → process → release pattern as Roster
* Ensures consistent batch handling across codebase

# Manage State Batch Jobs

**Scope:** Claim a batch of unclaimed jobs for a given state.

**Input:** state (str, job state to claim e.g. NEW, PASSED_JOBLIST), limit (int, max jobs to claim). Validate state via validate_value(ASTRAL_CONFIG\["job_states"\], state) at entry; fail loudly if invalid.

**Processing:** Generate batch_id (UUID); claim N unclaimed jobs (WHERE state=? AND batch_id IS NULL LIMIT ?); set batch_id and batch_created_at on claimed jobs; fetch and return them.

**Returns:** Tuple\[str, List\[Dict\[str, Any\]\]\] — (batch_id, jobs) where jobs is list of full job records.

**Database:** job table UPDATE batch_id, batch_created_at WHERE state=? AND batch_id IS NULL LIMIT ?; SELECT \* FROM job WHERE batch_id=?

**Ref:** tracker-features.csv get_new_batch; ASTRAL_CODE_RULES 3c

## Metadata

* URL: [AST-95](https://linear.app/astralcareermatch/issue/AST-95/sub-get-new-batchstate-limit)
* Identifier: [AST-95](https://linear.app/astralcareermatch/issue/AST-95/sub-get-new-batchstate-limit)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Tracker](https://linear.app/astralcareermatch/project/astral-tracker-196303942ae1). Manages job data for multiple projects.
* Created: 2026-02-03T22:56:33.601Z
* Updated: 2026-02-06T00:02:06.303Z

---

# Manage State Batch Jobs

**Scope:** Retrieve all jobs in a batch.

**Input:** batch_id (str, UUID of batch to retrieve).

**Processing:** Fetch all jobs with this batch_id.

**Returns:** List\[Dict\[str, Any\]\] (list of full job records).

**Database:** job table SELECT \* FROM job WHERE batch_id=?

**Ref:** tracker-features.csv get_batch

## Metadata

* URL: [AST-96](https://linear.app/astralcareermatch/issue/AST-96/sub-get-batchbatch-id)
* Identifier: [AST-96](https://linear.app/astralcareermatch/issue/AST-96/sub-get-batchbatch-id)
* Status: Done
* Priority: Medium
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Tracker](https://linear.app/astralcareermatch/project/astral-tracker-196303942ae1). Manages job data for multiple projects.
* Created: 2026-02-03T22:56:35.147Z
* Updated: 2026-02-06T00:02:05.871Z

---

# Manage State Batch Jobs

**Scope:** Release a batch so jobs can be reclaimed.

**Input:** batch_id (str, UUID of batch to release).

**Processing:** Set batch_id=NULL and batch_created_at=NULL for all jobs in batch. Allows jobs to be reclaimed by future batches if needed.

**Returns:** int (count of jobs released).

**Database:** job table UPDATE batch_id=NULL, batch_created_at=NULL WHERE batch_id=?

**Ref:** tracker-features.csv clear_batch

## Metadata

* URL: [AST-97](https://linear.app/astralcareermatch/issue/AST-97/sub-clear-batchbatch-id)
* Identifier: [AST-97](https://linear.app/astralcareermatch/issue/AST-97/sub-clear-batchbatch-id)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Tracker](https://linear.app/astralcareermatch/project/astral-tracker-196303942ae1). Manages job data for multiple projects.
* Created: 2026-02-03T22:56:36.491Z
* Updated: 2026-02-06T00:02:06.345Z

---

# Manage State Batch Jobs

**Scope:** Data layer functions that implement batch claim/release. Primitives: set_batch_for_unclaimed(state, batch_id, limit), select_jobs_by_batch(batch_id), clear_batch(batch_id). Job table has batch_id, batch_created_at columns. Uses WHERE batch_id IS NULL to find unclaimed jobs.

**Code:** src/data/database.py (or src/data/tracker.py if split)

**Ref:** tracker-features.csv Database; ASTRAL_CODE_RULES 3c

## Metadata

* URL: [AST-98](https://linear.app/astralcareermatch/issue/AST-98/sub-data-layer-primitives-for-batch-operations)
* Identifier: [AST-98](https://linear.app/astralcareermatch/issue/AST-98/sub-data-layer-primitives-for-batch-operations)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Tracker](https://linear.app/astralcareermatch/project/astral-tracker-196303942ae1). Manages job data for multiple projects.
* Created: 2026-02-03T22:56:37.646Z
* Updated: 2026-02-06T00:02:06.380Z

---

# Manage State Batch Jobs

**Scope:** Document and implement semantics: jobs in batch keep batch_id through state transition; batch_id explicitly cleared at end (success or failure) via clear_batch; prevents double-processing (batch_id IS NULL check). Multiple batches can run concurrently on different states; same state cannot be double-processed; failed batches can be retried (clear_batch releases jobs). No artificial limit on batch size; caller determines. Pattern consistent with Roster (claim → process → release).

**Ref:** tracker-features.csv Batch Locking; Concurrency; No Maximum Batch Size; Pattern Consistency

## Metadata

* URL: [AST-99](https://linear.app/astralcareermatch/issue/AST-99/sub-batch-locking-and-concurrency-semantics)
* Identifier: [AST-99](https://linear.app/astralcareermatch/issue/AST-99/sub-batch-locking-and-concurrency-semantics)
* Status: Done
* Priority: Medium
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Tracker](https://linear.app/astralcareermatch/project/astral-tracker-196303942ae1). Manages job data for multiple projects.
* Created: 2026-02-03T22:56:39.805Z
* Updated: 2026-02-06T00:02:05.906Z

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
