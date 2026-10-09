---
id: patt.task.dispatch-retry
kind: pattern
scope: task
point: >
  A failed attempt gets one more try through a sibling retry state, folded
  into the ordinary claim — never a bespoke retry queue.
---

# Abstract

Sometimes the agents return malformed or invalid responses when answering a prompt.  This is not uncommon, and we must be prepared for it to happen without requiring special handling.  For ALL tasks in agent_task, we must try to process the entities at that trigger_state TWICE before transitioning the entity to an ERROR state.  This is done by simply adding a suffix ("_RETRY", to be specified in the task_config content, and including the exact state AND the state concatenated with the suffix to be included in the claim pool. 

Whenever the agent returns an invalid response for an entity, the caller must determine the state of the entity before transitioning either to RETRY or to ERROR.  The logic is self-explanatory.

# Arc

1. **A retry state is merely a suffixed trigger_state.** Data validation for a state to the retry state only appends the suffix to the trigger state.  No separate state instance exists for retry states.  
2. **Validation does not require a separate state for retry** States suffixed with the retry string are not required to have a match in the entity state machine, only a match for the root of the state (non-prefixed). Validation of state transitions state (non-suffixed).  Validation logic lives exclusively in the entity management components (tracker, roster, candidate).
3. **The claim expands to cover both.** The agent responsible for claiming the batch knows to include both the trigger_state and the suffixed trigger state in the get_new_batch call.
4. **First failure transitions to the retry companion, not back to the same state.** The entity state transition for "error" knows to check for the suffix in the trigger state before assigning the next state for the entity.  The error state is dictated in the task_config element, and all the entity state transition function is determine if it has already been retried once before going to that config-driven error state.  
4. **A second failure is terminal.** An entity record already with the retry suffixed state that fails again routes to a genuinely terminal error state instead of back into the retry loop. One retry, not an unbounded number — the routing function decides this by checking whether the *current* state is already a `_RETRY` state, not by counting attempts anywhere.
5. **A FAILURE DOES NOT PERSIST IN STATE** Under no circumstances does a failure remain in the same state.  Only passing states can remain in state (e.g. "WATCH" and "NO_OPENINGS")

# Canonical implementation
The retry suffix is universal, configured as a string element in astral_config, where other general-use strings are defined.


# When this doesn't apply

- **Pre-provider data failure — empty runtime tokens.** When `do_task` finds a
  token in the outgoing prompt that resolves empty, the prompt is never sent and
  the result carries `empty_tokens`. The fault is in our data, not the agent's
  response, so a retry would render the same blank prompt. That entity skips
  the `_RETRY` companion and goes **straight** to the task's configured
  `error_state` — mid-chain hops included. When the configured `error_state` is
  itself a `_RETRY` holding, or the flow configures none, it goes to the
  terminal error state that flow already uses (e.g. `FAILED_TECHNICAL`). Arc 5
  still holds: the entity never stays in its trigger, hop-label or input state.
- **Pre-attempt provider gate — failed per-batch host probe.** On a server that
  probes for a host before a batch's first call, a failed probe (no host named,
  an error body, an exception, a cancelled probe — anything but an exhausted
  rate limit) means no entity prompt is sent. Nothing was attempted for the
  entity, so there is no failure to retry or to error: every entity in the batch
  keeps its current loop-eligible state, takes no `_RETRY` hop and no
  `error_state`, and is counted held, not errored. Dispatch stops the run and
  releases the claim; the next round claims the same entities under a new batch
  and probes again. Arc 5 is not broken — no failed attempt stays in state,
  because none was made. An exhausted rate limit on the probe is not this
  exemption; it stops the batch as a rate-limit outage.
- Every other failed attempt: THIS PATTERN ALWAYS APPLIES (even with
  daisy-chain tasks.)
