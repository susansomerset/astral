---
id: pattern.state.entity-state-transitions
name: Entity state transitions
status: proposed
proposed_in: AST-913
approved_by: null
approved_at: null
canonical_refs:
  - path: src/core/tracker.py
    symbol: transition_job_state
  - path: src/core/candidate.py
    symbol: transition_candidate_state
  - path: src/utils/config.py
    symbol: JOB_STATES
  - path: docs/ASTRAL_CODE_RULES.md
    symbol: "§2.6"
related_statutes:
  - astral.state.no-daisy-chain-in-run
  - astral.state.core-decides-transitions
  - astral.state.job-prior-states-enforced
supersedes: null
superseded_by: null
---

# Problem

Entities must move between registered states without daisy-chaining a full pipeline in one run, and without the data layer choosing next states.

# Solution shape

Core decides the target state from config registries (`JOB_STATES` / company and candidate transition maps). Data and tracker accept the target as a parameter only. One dispatch cycle performs one transition step (except the documented `run_next` carve-out). Point at `canonical_refs` — do not paste large code into this catalog entry.

## When not to use

- Multi-step “finish the whole funnel” inside a single runner.
- Data-layer hardcoding of the next state.
- Treating runtime hop labels as registry keys outside the documented carve-out.
