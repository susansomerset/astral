# AST-77 — Record State Transitions

<!-- linear-archive: AST-77 archived 2026-06-03 -->

## Linear archive (AST-77)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-77/record-state-transitions  
**Status at archive:** Done  
**Project:** Astral Tracker  
**Assignee:** susan  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Track job progression through evaluation pipeline with full state history. Records each state change with timestamp and batch context for complete job lifecycle traceability.

**Acceptance Criteria:**

**Input:**

* job_ids: List\[str\] (one or more astral_job_ids)
* to_state: str (new state to transition to)

**Validation:**

* Validate to_state exists in ASTRAL_CONFIG\["job_states"\]
* If invalid state: Raise ValueError
* Should never happen at runtime (QA-catchable bug)

**Processing:**
For each astral_job_id in job_ids:

1. Read current state and current batch_id from job table
2. Append to state_history: {"to_state": to_state, "timestamp": now, "batch_id": current_batch_id}
3. Update state = to_state
4. Update state_changed_at = now
5. Leave batch_id unchanged (cleared separately by clear_batch)

**Database Updates:**

* state: New state value
* state_changed_at: Timestamp of transition
* state_history: Append new entry to JSON array
* updated_at: now
* batch_id: UNCHANGED (released by clear_batch later)

**Transaction:**

* Single SQL transaction for all job_ids
* All-or-nothing atomic update
* If any job_id fails, entire batch rolls back

**State History Structure:**

```json
[
  {"to_state": "NEW", "timestamp": "2026-02-03T10:00:00Z", "batch_id": "uuid-from-gazer"},
  {"to_state": "PASSED_JOBLIST", "timestamp": "2026-02-03T10:05:00Z", "batch_id": "uuid-from-consult"},
  {"to_state": "ADDED_JD_SCRAPE", "timestamp": "2026-02-03T10:10:00Z", "batch_id": "uuid-from-consult"}
]
```

**Transition Validation:**

* Tracker does NOT validate state transitions
* Consult ensures valid transitions per state machine
* Tracker just records what Consult tells it

**State Machine (for reference only - not enforced by Tracker):**

All States:

* NEW, PASSED_JOBLIST, FAILED_JOBLIST, ADDED_JD_SCRAPE, ERROR_JD_SCRAPE
* PASSED_JD, FAILED_JD, PASSED_GET, FAILED_GET, PASSED_DO, FAILED_DO
* PASSED_LIKE, FAILED_LIKE

Valid Transitions:

* NEW → PASSED_JOBLIST | FAILED_JOBLIST
* PASSED_JOBLIST → ADDED_JD_SCRAPE | ERROR_JD_SCRAPE
* ADDED_JD_SCRAPE → PASSED_JD | FAILED_JD
* PASSED_JD → PASSED_GET | FAILED_GET
* PASSED_GET → PASSED_DO | FAILED_DO
* PASSED_DO → PASSED_LIKE | FAILED_LIKE

**Nomenclature:**

* PASS/FAIL: Agent evaluation decision (candidate fit)
* ERROR: Technical/system issues (scraping failed, bot block)
* ADDED: Data successfully obtained (no evaluation yet)

**Database:**

* job table: UPDATE state, state_changed_at, state_history, updated_at WHERE astral_job_id IN (...)

**Traceability:**

* Full job lifecycle visible in state_history
* Track which batch processed each transition
* Debug problematic jobs by reviewing history

# Record State Transitions

**Scope:** [config.py](<http://config.py>) exposes a single generic validate function (e.g. validate_value(allowed_list, value)) that checks value is in allowed_list. If not → raise ValueError (fail loudly). Should never be a runtime issue (QA-catchable). No per-state-type functions (e.g. no validate_job_state, validate_company_state); one function, caller supplies the list.

**Usage:** Caller gets the allowed list from config and passes it: e.g. validate_value(ASTRAL_CONFIG\["job_states"\], to_state). The calling function knows from the config file which list to use.

**Code:** src/utils/config.py

**Ref:** tracker-features.csv Validation; ASTRAL_CODE_RULES 2b

## Metadata

* URL: [AST-91](https://linear.app/astralcareermatch/issue/AST-91/sub-configpy-validate-valuelist-value)
* Identifier: [AST-91](https://linear.app/astralcareermatch/issue/AST-91/sub-configpy-validate-valuelist-value)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Tracker](https://linear.app/astralcareermatch/project/astral-tracker-196303942ae1). Manages job data for multiple projects.
* Created: 2026-02-03T22:56:28.737Z
* Updated: 2026-02-06T00:02:06.234Z

---

# Record State Transitions

**Scope:** For each job_id: read current batch_id from job table; append to state_history one entry {"to_state": to_state, "timestamp": now, "batch_id": current_batch_id}; update state = to_state, state_changed_at = now, updated_at = now; leave batch_id unchanged.

**Processing:** For all job_ids in one call: single SQL transaction; all-or-nothing. If any job_id fails, entire batch rolls back.

**Database:** job table UPDATE state, state_changed_at, state_history, updated_at WHERE astral_job_id IN (...). batch_id not modified (cleared separately by clear_batch).

**Code:** src/data/database.py (or src/data/tracker.py if split)

**Ref:** tracker-features.csv Processing; Database Updates; Database

## Metadata

* URL: [AST-92](https://linear.app/astralcareermatch/issue/AST-92/sub-data-layer-primitive-append-state-history-and-update-state)
* Identifier: [AST-92](https://linear.app/astralcareermatch/issue/AST-92/sub-data-layer-primitive-append-state-history-and-update-state)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Tracker](https://linear.app/astralcareermatch/project/astral-tracker-196303942ae1). Manages job data for multiple projects.
* Created: 2026-02-03T22:56:29.864Z
* Updated: 2026-02-06T00:02:06.265Z

---

# Record State Transitions

**Scope:** Single SQL transaction for all job_ids in the transition call. All-or-nothing atomic update. If any job_id fails (e.g. not found), entire batch rolls back.

**Ref:** tracker-features.csv Transaction

## Metadata

* URL: [AST-93](https://linear.app/astralcareermatch/issue/AST-93/sub-transaction-atomicity-for-multiple-job-ids)
* Identifier: [AST-93](https://linear.app/astralcareermatch/issue/AST-93/sub-transaction-atomicity-for-multiple-job-ids)
* Status: Done
* Priority: Medium
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Tracker](https://linear.app/astralcareermatch/project/astral-tracker-196303942ae1). Manages job data for multiple projects.
* Created: 2026-02-03T22:56:31.204Z
* Updated: 2026-02-06T00:02:05.799Z

---

# Record State Transitions

**Scope:** state_history is a JSON array; each appended entry has: to_state, timestamp, batch_id (the job's current batch_id at transition time). Enables full job lifecycle visibility and which batch processed each transition.

**Note:** State machine (valid transitions, nomenclature) is for reference only; not enforced by Tracker.

**Ref:** tracker-features.csv State History Structure; Traceability

## Metadata

* URL: [AST-94](https://linear.app/astralcareermatch/issue/AST-94/sub-state-history-entry-shape-and-traceability)
* Identifier: [AST-94](https://linear.app/astralcareermatch/issue/AST-94/sub-state-history-entry-shape-and-traceability)
* Status: Done
* Priority: Medium
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Tracker](https://linear.app/astralcareermatch/project/astral-tracker-196303942ae1). Manages job data for multiple projects.
* Created: 2026-02-03T22:56:32.385Z
* Updated: 2026-02-06T00:02:05.831Z

---

# Record State Transitions

**Scope:** Define function signature and input contract.

**Input:**

* job_ids: List\[str\] (one or more astral_job_ids)
* to_state: str (new state to transition to)

**Validation:** Call config validate function at entry (see subissue). If state invalid → fail loudly (ValueError). Should never be a runtime issue (QA-catchable). Tracker does NOT validate state machine transitions (Consult does); Tracker just records what Consult tells it.

**Ref:** tracker-features.csv Record State Transitions Input; Validation; Transition Validation

## Metadata

* URL: [AST-90](https://linear.app/astralcareermatch/issue/AST-90/sub-transition-state-signature-and-contract)
* Identifier: [AST-90](https://linear.app/astralcareermatch/issue/AST-90/sub-transition-state-signature-and-contract)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Tracker](https://linear.app/astralcareermatch/project/astral-tracker-196303942ae1). Manages job data for multiple projects.
* Created: 2026-02-03T22:56:27.550Z
* Updated: 2026-02-06T00:02:06.202Z

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
