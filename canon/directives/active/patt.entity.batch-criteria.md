---
id: patt.entity.batch-criteria
kind: pattern
scope: entity
point: >
  A claim's shape — which state, how many rows, what order, any score floor
  or recheck frequency — is criteria, sourced from dispatch_task, never a
  literal in the caller.
---

# Abstract

A claim is never "get some rows." It is a specific shape: this state (or
these states, once a retry companion is folded in), up to this many rows, in
this order, above this score floor, due for recheck if enough time has
passed since it was last checked. None of that shape is a literal in the code
that issues the claim — it is criteria, and criteria is data, sourced from
`dispatch_task` and read fresh on every tick. `patt.entity.batch-processing`
consumes whatever criteria this pattern produces; it does not know or care
where the criteria came from.

# Arc

1. `dispatch_task` **is the source.**  `trigger_state`, 
  `sort_by`, `batch_size`, `score_floor`, and `freq_hrs`  
   are row data, edited through the admin UI, read fresh by  
   `dispatcher._run_unified` on every tick for unclaimed entities.   
   Changing what a dispatch task claims requires a  row edit, not a deploy.  Furthermore, there is no VALIDATION of the dispatch_task records enforced by the code. Dispatch_tasks are validated through execution, not by code logic.
2. **Frequency and score floor are eligibility predicates, not a second query.** When 
  `freq_hrs` or score_floor are set, they are composed into  the same claim statement as one more condition —  `last_scan_at IS NULL OR last_scan_at < now - interval` — narrowing which  rows in the expanded state set were ever eligible this tick. It does not  add a second claim, a second lock, or a second release;   `batch-processing`'s claim/lock/release cycle is unmodified and  unaware the predicate exists. 
3. `batch_size` **and** `sort_by` **drain whatever criteria produced, unchanged.**
  However large the eligible pool — a plain state filter, or a state filter
   narrowed by frequency — the same knob drains it: `batch_size` rows per tick, in `sort_by` order. There is no separate "backlog management"  concept for a frequency-gated pool; it is the identical mechanism as any  other claim.  max_runs allows for very large pools to be processed in discrete chunks to allow other eligible task traffic to proceed without waiting until the whole queue is cleared.
4. **The row that stamps eligibility is the row that clears it.**
  `last_scan_at` is written by the caller on completion  
   (e.g.`update_company_last_scan_at`) — an ordinary post-processing write, not  
   part of the claim or the release step.

# Canonical implementation

- `batch claims using criteria must be consistent across all entities.  Criteria fields like state, latest_score, last_scan_at, etc., must exist for all entity tables.`

# When this doesn't apply

There are no exceptions to batch criteria.  state is required, all other criteria is optional.

Note: Entity type is derived by the selected task key, not editable directly (task_key is always entity-type-specific).  If the dispatch_task.task_key changes to a different entity type, the dispatch_task.entity_type changes with it. 
