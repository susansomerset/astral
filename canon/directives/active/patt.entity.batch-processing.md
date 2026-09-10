---
id: patt.entity.batch-processing
kind: pattern
scope: entity
point: >
  Claim a batch under one id, process only those rows, always release.
---

# Abstract

Several dispatch workers draw from the same queue of entity rows. Without a lock, two of them may claim the same entity and it would be processed twice, simultaneously. Meanwhile, with a lock that is never released, a crashed run leaves rows claimed forever and the queue quietly drains to nothing. The batch id is both the lock and the audit trail — one id covers one claim, and every row it touched can be found and released by it. This holds even when a claim returns exactly one row: `batch_id` is what stops a concurrent
poll on another server from grabbing that same row mid-process, and it is the
join key every `agent_data` row written during the batch relies on to be reconstructed later. Locking is the reason the id exists; the join key is a consequence of having it, not a separate justification for skipping it on a small claim.

# Arc

1. **Entity Core mints the batch id.** One id per claim, generated as
  `f"{context}-{uuid4()}"` when the caller does not supply one. The caller owns  it for the whole cycle.  
2. **Core passes claim criteria through unmodified.** Which state, how many
   rows, what order, any score floor or recheck frequency — sourcing that
   shape is `patt.entity.batch-criteria`'s concern, not this one's. This
   pattern only guarantees that whatever criteria it's handed is claimed
   atomically, under one id.
3. **Dispatcher determines if there are eligible entity records before running task.** Dispatcher calls the corresponding entity core component (e.g., tracker) to claim the batch with the criteria provided.  If the batch claim returns empty, the dispatch task does not fire.
4. **Data claims, and never claims more than it was told to.** Up to
   `batch_size` *unclaimed* rows matching whatever criteria it was handed
   get `batch_id` and `batch_created_at` stamped in one statement. Returns
   the count. Data chooses nothing — every parameter arrives already
   resolved by the caller. `batch_size` is not a soft target: nothing
   widens a single claim beyond it, under any circumstance, because the
   scheduler's own `max_runs` bound depends on every claim actually being
   one `batch_size`-sized bite. A claim that silently grabs more starves
   every other task waiting its turn on the same tick — it is not a bigger
   version of the same claim, it is a violation of the bound the rest of
   the system is relying on.
5. **Core processes only by batch_id** Not a re-query, no primary keys.
6. **Core releases in** `finally`**.** `clear_*_batch(batch_id)` nulls the lock on every row carrying that id, on every exit path including exceptions. A release that claimed nothing is a harmless no-op returning `0`.

# Batch ID as Audit key

Claiming/locking is not the only job `batch_id` does. The same value is the join key
that reconstructs what happened during a batch, and it keeps working after the
claim itself has been released:

- **State history.** Every `state_history` entry stamps the `batch_id` that
was active at the transition, on top of whatever the entity row's own
`batch_id` column holds — see the history append in `src/core/tracker.py`
(job) and its peer in `src/core/roster.py` (company). This is how a state
change traces back to the run that caused it, long after that run's claim
has cleared.
- `agent_data`**.** Every LLM call and generated artifact written during a
batch carries that batch's `batch_id` on its `agent_data` row.
`database.get_agent_data_by_batch(batch_id)` is the read side — it is how
`tracker.py` reconstructs prior hop blocks for a chained dispatch, and it
works whether or not the batch is still claimed.
- **Dispatch ledger and cost.** `dispatch_ledger` and `agent_timesheets` rows
are keyed by `batch_id`. `dispatcher.get_dispatch_ledger` and
`_db_sum_cost_by_batch` read by that key, which is why cost can still be
summed for a batch well after `clear_*_batch` has released the rows.
- **Cross-request correlation.** `src/utils/logging.py::log_batch_id` is a
contextvar the dispatcher sets at batch start. Flows outside the claim cycle
itself — e.g. the UI-triggered generate endpoints in `candidate.py` — read it
to correlate a request against the batch's cost and response rows.

This does not change the Arc above: release still happens the instant
processing ends, on every exit path. The audit trail outlives the lock by
design — the entity row's `batch_id` column is nulled on release, but every row
written *during* the batch (`state_history` entries, `agent_data` rows, ledger
and timesheet rows) keeps its own permanent copy of the id. Losing the lock is
not losing the trail.

# Canonical implementation

Implementation of this pattern must be consistent across entities without variations, following consistent naming conventions and call stacks.

# Data coupling

Every entity table backing a claim queue carries `batch_id` and `batch_created_at` as **root columns**, because the claim filters on them. Every other dimension of what gets claimed is `patt.entity.batch-criteria`'s concern; this pattern only owns the lock columns.

# Configuration

`batch_id` is not stored on `dispatch_task` — only on the entity row (during
the claim) and on `dispatch_ledger` (permanently). Where the rest of a
claim's shape comes from — `dispatch_task`, a state registry, whatever —
is `patt.entity.batch-criteria`'s concern; this pattern receives criteria as
opaque parameters and does not care about their source.

# Related Directives

- `patt.entity.batch-criteria`
- `stat.data.batch-id-first`
- `stat.core.entity-save`

# When this doesn't apply

- Read-only queries that never mutate the rows they read.
- One-off admin scripts that intentionally bypass dispatch locking.
- UI-driven actions: UI writes do not acquire a batch claim themselves — a
  bulk write from the UI, or a UI-triggered "run these now" that hands off
  to the real dispatcher claim, is not required to mint its own `batch_id`.
  Neither frontend nor API code implement their own version of claiming or
  running a task; if real task work needs to happen, it goes through the
  dispatcher's own claim, not a hand-rolled loop in the API layer.

  This is not the same as saying UI writes are risk-free. A UI write can
  still land on a row an active batch currently has locked, and what should
  happen then — warn, block, or offer to force-clear the batch so the row
  isn't stuck — is a real concern. It is out of scope for this pattern,
  which governs the claim/lock/release cycle itself and says nothing about
  how a non-claiming writer should behave when it collides with one. That
  belongs to a separate, not-yet-drafted pattern.

# Notes

`database.claim_job_batch`'s `claim_cap` parameter — set from
`count_eligible_for_dispatch_task` when a job task_key is in
`_CHUNK_EXHAUST_CONSULT_JOB_KEYS` (AST-502) — currently overrides `batch_size`
with the full eligible backlog count for a single claim. That was built
deliberately, to optimize model-call cost and prompt-cache reuse on large
qualify/evaluate/grade backlogs (AST-500/501/502), a real requirement at the
time. It is a known, confirmed violation of the invariant in Arc step 4 as of
this writing: it widens a single claim past `batch_size`, which defeats the
tick-fairness `max_runs` exists to provide — the first iteration of a
`max_runs`-bounded loop can claim an entire backlog and starve every other
task waiting on the same tick, regardless of what `max_runs` was set to. Not
yet corrected in code.

