# AST-101 — Claim Company Batches

<!-- linear-archive: AST-101 archived 2026-06-03 -->

## Linear archive (AST-101)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-101/claim-company-batches  
**Status at archive:** Done  
**Project:** Astral Gazer  
**Assignee:** susan  
**Priority / estimate:** High / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Batch processing for WATCH companies with intelligent prioritization. Claims companies ready for scanning, prioritizing never-scanned companies first, then oldest scans. All companies in a Gazer run share a single batch_id for audit trail and lineage tracking.

**Acceptance Criteria:**

**Layer split:** Core owns orchestration; data layer exposes primitives only (no batch_id generation in data).

**Core (e.g. src/core/gazer.py):**

```python
get_new_company_batch(
    state: str,
    limit: int,
    sort_by: str = "updated_at"
) -> Tuple[str, List[Dict]]
```

Generates batch_id (UUID), calls data claim_company_batch(batch_id, state, limit, sort_by), then get_company_batch(batch_id), returns (batch_id, companies).

**Data (src/data/database.py):** Naming uses company_batch (entity first). get_new\_\* breaks down to claim + get.

* claim_company_batch(batch_id, state, limit, sort_by?) — set batch_id, batch_created_at on up to limit rows where state=? AND batch_id IS NULL; ORDER BY sort_by (e.g. last_scan_at ASC NULLS FIRST); stale interval from config.
* get_company_batch(batch_id) -> List\[Dict\] (no state/limit)
* clear_company_batch(batch_id) — set batch_id and batch_created_at NULL for batch

**Input (core):**

* state: str (company state to claim, e.g. WATCH); validate against config
* limit: int (max companies to claim, 0 = unlimited)
* sort_by: str (column to sort by, default updated_at)

**Query logic (inside claim_company_batch):**

```sql
WHERE state = ? AND batch_id IS NULL
AND (last_scan_at IS NULL OR last_scan_at < (now - interval '? hours'))
ORDER BY {sort_by} ASC NULLS FIRST
LIMIT ?  -- Null if limit=0
```

**Returns (core):** (batch_id, companies) where companies is list of full company records.

**Prioritization:**

* NULLS FIRST ensures never-scanned companies (last_scan_at IS NULL) process first
* Then oldest last_scan_at next
* Recently scanned companies naturally excluded by stale threshold

**Configuration:**

```python
"gazer": {
    "scan_state": "WATCH",
    "sort_key": "last_scan_at",
    "max_companies_per_run": 100,  # 0 = unlimited
    "scan_interval_hours": 24,
    "concurrent_batch_size": 5
}
```

**Gazer Execution Pattern:**

```python
config = ASTRAL_CONFIG["gazer"]
# Core: get a new batch (generates batch_id, calls data claim_company_batch + get_company_batch)
batch_id, companies = core.get_new_company_batch(
    state=config["scan_state"],
    limit=config["max_companies_per_run"],
    sort_by=config["sort_key"]
)

# Process companies in concurrent chunks
chunk_size = config["concurrent_batch_size"]
for chunk in chunks(companies, chunk_size):
    await asyncio.gather(*[scan_company(c, batch_id) for c in chunk])

# Release batch (data primitive)
database.clear_company_batch(batch_id)
```

**Batch Locking:**

* Single batch_id for entire Gazer run (not per chunk)
* Prevents concurrent processing of same companies
* batch_id explicitly cleared at end (success or failure)

**Database (data layer only):**

* claim_company_batch(batch_id, state, limit, sort_by?): UPDATE company SET batch_id, batch_created_at WHERE state=? AND batch_id IS NULL AND criteria ORDER BY sort_by
* get_company_batch(batch_id): SELECT \* FROM company WHERE batch_id=?
* clear_company_batch(batch_id): UPDATE company SET batch_id=NULL, batch_created_at=NULL WHERE batch_id=?

**Concurrency:**

* Multiple Gazer runs won't double-process (batch_id IS NULL check)
* Within run: process companies concurrently in chunks (Playwright concurrency limit)

**State Machine Integration:**

* Only claims companies in configured state (default: WATCH)
* Does not transition states (that's Scrape/Track responsibility)
* Follows same claim → process → release pattern as Roster and Tracker

**Traceability:**

* batch_id enables lineage tracking across company_job_scan records
* All scans from single run share same batch_id

# Claim Company Batches

**Scope:** Define the **core** orchestration function for claiming a new batch of companies.

**Layer:** Core (e.g. src/core/gazer.py). Data layer does not generate batch_id; core does.

**Signature:**

```python
get_new_company_batch(
    state: str,
    limit: int,
    sort_by: str = "updated_at"
) -> Tuple[str, List[Dict]]
```

**Behavior:** Generate batch_id (UUID); call data claim_company_batch(batch_id, state, limit, sort_by); call data get_company_batch(batch_id); return (batch_id, companies).

**Input:** state (validate against ASTRAL_CONFIG\["company_states"\] only), limit (0 = unlimited), sort_by. **Returns:** (batch_id, companies). No hardcoded state strings.

**Ref:** gazer-features.csv Claim Company Batches; ASTRAL_CODE_RULES 2b, 3c

## Metadata

* URL: [AST-105](https://linear.app/astralcareermatch/issue/AST-105/sub-get-new-company-batch-signature-and-contract-core)
* Identifier: [AST-105](https://linear.app/astralcareermatch/issue/AST-105/sub-get-new-company-batch-signature-and-contract-core)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:29.428Z
* Updated: 2026-02-10T00:37:40.112Z

---

# Claim Company Batches

**Scope:** Implement the query inside **data** claim_company_batch(batch_id, state, limit, sort_by?): only update rows where batch_id was previously null; ORDER BY sort_by (e.g. last_scan_at ASC NULLS FIRST).

**WHERE:** state = ? AND batch_id IS NULL AND (last_scan_at IS NULL OR last_scan_at < now - interval). Stale threshold (interval) must come from config (e.g. scan_interval_hours)—explicit from config, no magic number.

**ORDER BY:** sort_by ASC NULLS FIRST (never-scanned first, then oldest). **LIMIT:** from param; null if limit=0.

**Processing:** UPDATE company SET batch_id, batch_created_at on matching rows. Data layer does not generate batch_id; caller (core) passes it in. Naming: company_batch (entity first).

**Ref:** gazer-features.csv Query Logic; Prioritization; ASTRAL_CODE_RULES 2b

## Metadata

* URL: [AST-106](https://linear.app/astralcareermatch/issue/AST-106/sub-query-logic-and-prioritization-inside-claim-company-batch)
* Identifier: [AST-106](https://linear.app/astralcareermatch/issue/AST-106/sub-query-logic-and-prioritization-inside-claim-company-batch)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:30.523Z
* Updated: 2026-02-10T00:37:40.020Z

---

# Claim Company Batches

**Scope:** Data layer functions for company batches. Naming: company_batch / job_batch (entity first). Core get_new\_\* breaks down to claim + get at data layer; no redundancy.

**Company table primitives:**

* claim_company_batch(batch_id, state, limit, sort_by?) — set batch_id, batch_created_at on up to limit rows where state=? AND batch_id IS NULL; ORDER BY sort_by (query/order/limit as in Query logic subissue)
* get_company_batch(batch_id) -> List\[Dict\] (no state/limit)
* clear_company_batch(batch_id) — set batch_id and batch_created_at NULL for that batch

**Job table (parallel pair):** claim_job_batch(batch_id, state, limit, sort_by?), get_job_batch(batch_id), clear_job_batch(batch_id).

**Code:** src/data/database.py. Data never generates batch_id.

**Ref:** gazer-features.csv Database; GAZER_FEATURES_VS_ASTRAL_CODE_RULES.md #1

## Metadata

* URL: [AST-107](https://linear.app/astralcareermatch/issue/AST-107/sub-data-layer-primitives-claim-company-batch-get-company-batch-clear)
* Identifier: [AST-107](https://linear.app/astralcareermatch/issue/AST-107/sub-data-layer-primitives-claim-company-batch-get-company-batch-clear)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:31.535Z
* Updated: 2026-02-10T00:37:39.942Z

---

# Claim Company Batches

**Scope:** Config-driven gazer settings for claim and run.

**Config keys (example):**

* scan_state (e.g. WATCH)
* sort_key (e.g. last_scan_at)
* max_companies_per_run (0 = unlimited)
* scan_interval_hours
* concurrent_batch_size

**Usage:** Gazer reads config; no magic numbers. Same pattern as Roster/Tracker config.

**Ref:** gazer-features.csv Configuration; ASTRAL_CODE_RULES 2b

## Metadata

* URL: [AST-108](https://linear.app/astralcareermatch/issue/AST-108/sub-gazer-config-for-scan-and-batch)
* Identifier: [AST-108](https://linear.app/astralcareermatch/issue/AST-108/sub-gazer-config-for-scan-and-batch)
* Status: Done
* Priority: Medium
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:32.523Z
* Updated: 2026-02-10T00:37:39.885Z

---

# Claim Company Batches

**Scope:** Orchestration: claim batch (core), process in chunks, release batch (data).

**Flow:** core.get_new_company_batch(state, limit, sort_by) → (batch_id, companies); process companies in concurrent chunks (asyncio.gather); then data.clear_company_batch(batch_id) on exit (success or failure).

**Semantics:** Single batch_id for entire run; prevents double-processing. Release always so companies can be retried if needed.

**Ref:** gazer-features.csv Gazer Execution Pattern; Batch Locking

## Metadata

* URL: [AST-109](https://linear.app/astralcareermatch/issue/AST-109/sub-gazer-execution-pattern-and-batch-lifecycle)
* Identifier: [AST-109](https://linear.app/astralcareermatch/issue/AST-109/sub-gazer-execution-pattern-and-batch-lifecycle)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Gazer](https://linear.app/astralcareermatch/project/astral-gazer-2d63c1c27d8b). Parse known job sites for job metadata to save to the database.
* Created: 2026-02-06T00:48:33.505Z
* Updated: 2026-02-10T00:37:39.793Z

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
