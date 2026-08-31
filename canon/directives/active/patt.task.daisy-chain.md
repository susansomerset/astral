---
id: patt.task.daisy-chain
kind: pattern
scope: task
point: >
  A multi-hop task keeps going inside one claim when it can, and resumes
  from its last completed hop — never from the start — when it can't.
---

# Abstract

Some tasks use context from the tasks that came before it (either immediately or through a chain).  We use daisy-chain to explicitly reference the c ontext for the entity. Running that as independent dispatch ticks would mean re-claiming, re-releasing, and re-paying the claim overhead between every hop, and would leave the row's state ambiguous between hops for anyone else looking at it. The fix is to let one claimed batch_id walk the whole chain itself when nothing stops it, and to leave an honest, resumable marker on the row when something does — so whichever worker claims it next resumes from the interruption, not from hop one.

# Arc

1. **A task names its own successor.** `run_next` on an `agent_task` row
  points at the next `task_key` in the chain. `_current_agent_task_run_next`
   is how a caller checks whether a chain continues from here.
2. **The chain walks itself inside one execution by default.** When a hop
  completes, `do_task` continues straight into the next hop without
   returning to the dispatcher — one claimed batch, one `batch_id`, however
   many hops it takes. `skip_daisy_chain` (a `dispatch_task` column, carried
   into `ctx["suppress_run_next"]`) is the one escape hatch: set, it forces
   a stop after exactly one hop instead of continuing.
3. **A stopped or interrupted chain marks its own position.** The entity's
  state is written as a compound hop label — `REQUESTED_ARTIFACTS.<hop>`
   for candidates — rather than snapped back to a plain state name.
   `parse_dispatch_hop_label` reads that label back into
   `(bare_trigger_state, hop)`.
4. **Reclaiming knows to look for mid-chain rows.** `is_dispatch_chain_trigger`
  recognizes a `trigger_state` as chain-bearing; when it does,
   `dispatch_chain_claim_states_for_row` expands the claim to include
   hop-labeled rows alongside the bare trigger state, so an interrupted row
   is claimable again on the next tick instead of stranded under a label no
   ordinary claim would match. `dispatch_chain_row_matches_job` then filters
   the claimed set down to rows actually at the hop this task_key handles.
5. **Every hop still reports through the one batch_id.** Hop boundaries are
  logged and ledgered (`_open_run_next_hop_ledger`,
   `_finalize_run_next_hop_ledger`) under the batch_id the outer claim
   minted — `patt.entity.batch-processing`'s audit-key role holds across
   every hop, not just the first one.

This pattern governs how a chain continues and resumes. It does not
re-describe claiming, locking, or releasing — those are
`patt.entity.batch-processing`'s, unmodified, no matter how many hops run
inside the claim they wrap.

# Canonical implementation

- Daisy-chains are a valid framework of task configuration.  No task-key-specific code is necessary or allowed for managing dispatch tasks as participants in daisy-chains.

# When this doesn't apply

- Single-hop tasks with no `run_next` configured — there is no chain to
continue or resume, only an ordinary claim.
- Mid-chain failure handling itself is not this pattern's concern — see
`patt.task.dispatch-retry` for what happens when a hop's *output* is invalid,
as distinct from the chain being interrupted mid-flight.

