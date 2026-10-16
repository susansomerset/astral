# AST-2229 — Forward-only readiness advancement

- **Linear:** [AST-2229](https://linear.app/astralcareermatch/issue/AST-2229)
- **Parent:** [AST-2225](https://linear.app/astralcareermatch/issue/AST-2225) — Revise candidate ui and candidate states
- **Publish ref:** `origin/sub/AST-2225/AST-2229-readiness-advancement`

After AST-2228’s stage vocabulary, add a scheduled presence/readiness evaluate that advances a candidate **forward only** when the next happy-path hop’s pieces are present, expose an incomplete-profile signal for nav siblings, and wire that evaluate into the dispatcher tick beside stale aging — so landing in a claimable `trigger_state` lets existing dispatch claim that state (never a stage integer).

## UAT fitness

- **AC restored:** Parent AC 11–13 (this child’s partition): (11) Incomplete Profile alert — core signal half: incomplete → signal true (UI yellow is #4); complete → false; missing pieces never lower `state`. (12) Forward scheduled advance — core readiness entrypoint invoked from dispatcher tick; fixture with next-hop readiness advances via `transition_candidate_state`; no demote path. (13) Dispatch state-bound — after advance into a claimable state, claim uses that `trigger_state` (workers never key off stage integers).
- **Correct outcome:** On each tick, candidates whose next hop’s pieces are present move one legal step forward (e.g. into `PROFILE_READY` / `CONTEXT_READY` / `REQUESTED_RESUME` / `REQUESTED_ARTIFACTS` / `ACTIVE_SEARCH`); incomplete profile only raises a boolean signal; dispatch continues to claim real registry states.
- **Sibling check:** #1 (AST-2228) owns vocabulary / `candidate_stage` / topic migrate — consumed, not redefined. #3/#4 own nav API + yellow UI chrome — they call `incomplete_profile`; this ticket does not touch `api_system.py` / frontend. Stale aging (`age_stale_candidate_states`) stays behaviorally unchanged aside from call order on the tick. Verified by Files Changed = `candidate.py` + `dispatcher.py` only.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Demoting `state` when profile/context pieces disappear (or gating advance on `stage` integers / inventing stage-integer `trigger_state`s) would fail AC 11–13 and `astral.dispatch.entity-state-bound`. Symptom-only: wiring an alert without a tick-invoked advance entrypoint fails AC 12.

## Explicit scope gate

Ticket **## Scope** names only:

- `src/core/candidate.py` — readiness/advance + incomplete-profile signal
- `src/core/dispatcher.py` — tick wiring

Every Files Changed row and every stage step below stays inside that list. No `config.py`, `database.py`, `api_system.py`, frontend, or `CANDIDATE_DATA_MODEL.md`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | `check_profile_complete`, `incomplete_profile`, readiness hop table + `advance_candidate_readiness`; no demote path | core |
| `src/core/dispatcher.py` | `_tick_loop` calls `advance_candidate_readiness` after `age_stale_candidate_states` | core |

## Canon (this ticket)

Read in full (patterns / placement statutes named on the ticket):

- `patt.entity.batch-processing` — claim→process→release **if** readiness batch-claims; this plan **does not** batch-claim (see Decision below).
- `patt.entity.batch-criteria` — claim shape stays criteria/config-sourced when claiming; N/A for the list-scan path chosen here.
- `patt.task.dispatch-retry` — request/retry companions stay ordinary claim states; readiness must not invent a parallel retry queue or skip dispatch’s `_RETRY` grammar.
- `astral.batch.claim-process-release` — pool claim parity when claiming; N/A for list-scan (same shape as `age_stale_candidate_states`).
- `astral.dispatch.entity-state-bound` — advance targets are real `CANDIDATE_STATES` / `CANDIDATE_STAGE_DISPATCH` `trigger_state` strings; never stage integers.
- `stat.logging.info.dispatcher` — readiness is **not** a dispatch task; do not emit task-completed lines for it.
- `stat.logging.info.entity` — each successful readiness advance emits one entity info line.

All other ids: id-only.

## Prerequisite (build, not this ticket’s Scope)

- **AST-2228 on tip:** `PROFILE_READY` / `CONTEXT_READY` registered, topic keys gone, `candidate_stage` / `migrate_retired_topic_candidate_states` present, `check_context_complete` keyed off `CONTEXT_READY`.
- **Importable registry:** `from src.utils.config import CANDIDATE_STATES` must succeed. After merging `origin/dev` (AST-2221 `BASE_RESUME_CHAIN_ERROR_STATES`) with AST-2228’s stage rewrite, those resume-chain `ERROR_*` entries can lack `"stage"`. That is **#1 vocabulary** (resume-request errors → stage **3** per parent Functional scope). If still broken at build start → stop and comment on parent AST-2225; **do not** edit `config.py` under AST-2229.

## Stage 1: Profile signal + readiness advance (`candidate.py`)

**Done when:** `incomplete_profile` reflects missing required profile pieces without writing state; `advance_candidate_readiness` advances exactly the locked forward hops when predicates pass, never demotes, never targets stage integers; `age_stale_candidate_states` behavior unchanged.

1. In `src/core/candidate.py`, near `check_context_complete` / `age_stale_candidate_states`, add:

   ```python
   def check_profile_complete(candidate_id: str) -> bool:
       """True when required Profile pieces are present (no state write)."""
   ```

   Implementation rules:
   - Load via `database.get_candidate`; missing row → `False`.
   - Required pieces (⚠️ **Decision** below): stripped non-empty `first` **and** `last` on the row, and stripped non-empty `candidate_data.contact.contact_email`.
   - **No** progress_rank / stage short-circuit — pieces disappearing must still report incomplete (AC 11 edge case).
   - Do not require pronouns, phone, or other contact keys.

2. Add:

   ```python
   def incomplete_profile(candidate_id: str) -> bool:
       """True when required Profile pieces are missing (alert signal for nav siblings)."""
   ```

   Implementation: `return not check_profile_complete(candidate_id)` (missing candidate → `True` is wrong for “alert on Profile”; return `False` when the row is missing so callers do not paint a ghost). Prefer: missing row → `False`; incomplete pieces → `True`.

3. Add a module-private forward-hop table (constant dict or tuple of rows) mapping **from base state → (to_state, predicate_name)**. Locked hops only:

   | From (registered base) | To | Predicate |
   |------------------------|----|-----------|
   | `INTAKE_INITIATED` | `PROFILE_READY` | `check_profile_complete(cid)` |
   | `PROFILE_READY` | `CONTEXT_READY` | `check_context_complete(cid)` |
   | `CONTEXT_READY` | `REQUESTED_RESUME` | non-empty stripped `candidate_data.context.raw_resume` |
   | `RESUME_READY` | `REQUESTED_ARTIFACTS` | `load_pilot_base_resume_for_candidate(cid)` is not `None` and body is non-empty when string-like |
   | `RESUME_READY_STALE` | `REQUESTED_ARTIFACTS` | same base_resume predicate |
   | `ARTIFACTS_READY` | `ACTIVE_SEARCH` | always (arrival already means craft passed) |
   | `ARTIFACTS_READY_STALE` | `ACTIVE_SEARCH` | always |

   ⚠️ **Decision:** No scheduled hops from `NEW_CANDIDATE` / `PROSPECT` / `REQUESTED_*` / `*_RETRY` / `ERROR_*` / `ACTIVE_SEARCH` / `PAUSE_SEARCH` / `INACTIVE` / `DELETED`. Intake and dispatch/craft own those. Stale companions for resume/artifacts **do** forward into the next claimable/search state (forward-only; not a demote).

   ⚠️ **Decision:** Do **not** batch-claim candidates for readiness. Mirror `age_stale_candidate_states`: `list_candidates(include_deleted=False)` scan. Scope excludes `database.py` / `config.py` (no new claim criteria). Parent canon says claim-process-release **if** readiness batch-claims — we choose the stale-aging peer path instead.

4. Add:

   ```python
   def advance_candidate_readiness() -> int:
       """Forward-only presence advance. Returns count of successful transitions."""
   ```

   Implementation rules:
   - Iterate `list_candidates(include_deleted=False)`.
   - Resolve `base = registered_base(CANDIDATE_STATES, state)`; skip if unknown / no hop row for `base` (and for non-base exact keys like `RESUME_READY_STALE`, match the from column exactly — prefer exact `state` key in the hop table over base when both could apply).
   - Evaluate predicate; if false → continue (no state write).
   - `to_state` must be a key in `CANDIDATE_STATES`. If `to_state` is a `CANDIDATE_STAGE_DISPATCH` `trigger_state`, that is intentional (AC 13) — do not also write stage integers anywhere.
   - Call `transition_candidate_state(cid, to_state)` **without** `force` (priors must already allow the hop).
   - On `IllegalCandidateTransition` / `ValueError`, skip and continue (do not raise out of the sweep).
   - **Demote ban:** before transitioning, assert `candidate_stage(to_state) >= candidate_stage(from_state)` when both resolve; if somehow lower, skip (never call transition). Same-stage forward (e.g. stale → request at stage 4) is allowed when `to` stage ≥ `from` stage.
   - On each success, emit one `logger.info` per `stat.logging.info.entity`:
     `{cid} | candidate readiness_advance: {from_state} -> {to_state} (batch: -)`
   - Return the success count.
   - Do **not** call `transition_candidate_state` toward any lower stage; do **not** clear or rewrite profile/context data.

5. Do **not** modify `age_stale_candidate_states` / `migrate_retired_topic_candidate_states` / `transition_candidate_state` legality beyond calling them. Do **not** add nav/API surfaces.

## Stage 2: Dispatcher tick wiring (`dispatcher.py`)

**Done when:** Every scheduler tick invokes `advance_candidate_readiness` after stale aging and before due AUTO spawn; failures in readiness do not kill the tick loop.

1. In `src/core/dispatcher.py` `_tick_loop`, immediately after the existing late-import call to `age_stale_candidate_states()` (and before `database.run_due_scheduled_queries()`), late-import and call `advance_candidate_readiness` the same way:

   ```python
   from src.core.candidate import age_stale_candidate_states, advance_candidate_readiness
   age_stale_candidate_states()
   advance_candidate_readiness()
   ```

   (Keep a single late-import block; add `advance_candidate_readiness` to that import.)

2. Wrap only if the surrounding `try` already covers the tick body (it does) — do **not** add a nested swallow that hides bugs. Do **not** emit `stat.logging.info.dispatcher` task-completed lines for readiness.

3. Do **not** change claim/spawn logic, `CANDIDATE_STAGE_DISPATCH` consumption, or AUTO caps.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Execution contract

- Follow stages in order; one commit per stage on the epic worktree; push each to `origin/sub/AST-2225/AST-2229-readiness-advancement`.
- Do not add files outside **Files Changed**.
- On ambiguity or codebase drift → stop and comment on parent AST-2225 with the Stage N blocked template; do not improvise.
- Build precondition: registry import + AST-2228 APIs present (see Prerequisite).

## Joan validate

[plan-rubric]
**Ticket:** AST-2229
**Overall:** APPROVED
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Publish ref tip:** `c6d6996c8f7d934aaeb5ca31376bff01ac430efe` (`origin/sub/AST-2225/AST-2229-readiness-advancement`)

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-processing | A | | |
| patt.entity.batch-criteria | X | | No dispatch_task-shaped claim; list-scan advance only |
| patt.task.dispatch-retry | A | | |
| astral.batch.claim-process-release | X | | No pool claim; stale-aging peer path documented |
| astral.dispatch.entity-state-bound | A | | |
| stat.logging.info.dispatcher | A | | |
| stat.logging.info.entity | B | | |

## Traceability

AC11 → Stage 1 (`check_profile_complete`, `incomplete_profile`; no state write on missing pieces). AC12 → Stage 1 (`advance_candidate_readiness`) + Stage 2 (`_tick_loop` after `age_stale_candidate_states`). AC13 → Stage 1 hop targets (`REQUESTED_RESUME`, `REQUESTED_ARTIFACTS`, `ACTIVE_SEARCH`); no stage-integer triggers; dispatch claim unchanged in `dispatcher.py`. Parent AC 1–10 → N/A — registry/nav/shell (#1, #3, #4). Parent AC 5–10 → N/A — same.

## Findings

### discuss
- **Location:** Stage 1 step 1–2 — `check_profile_complete` / `incomplete_profile`
- **Finding:** Required Profile pieces are fixed to `first` + `last` + `contact_email`, while parent AC 11 says “required Profile pieces” without enumerating them and epic UI text implies broader Profile-section content (sibling #3/#4 consume this signal for yellow chrome).
- **Recommendation:** Before build, confirm with #3 that `incomplete_profile` alone is the API contract for yellow Profile, or document that context completeness stays on `check_context_complete` / a later API flag. If Susan intends yellow for missing bio/context fields at stage 2+, narrow name/email-only signal may under-deliver AC 11’s “Profile pieces” wording.

### discuss
- **Location:** Stage 1 step 4 — entity log line
- **Finding:** Planned shape `candidate readiness_advance: {from} -> {to}` is id-pipe with `batch: -` but uses a custom event token instead of the statute’s canonical `candidate state: {from} -> {to}`.
- **Recommendation:** At implement time, prefer the existing `state` event (still one line per advance) unless ops explicitly want a separate grep token.

### acceptable
- **Location:** Prerequisite — AST-2228 / registry import
- **Finding:** Build depends on #1 vocabulary (`candidate_stage`, revived states, topic migrate); plan correctly blocks `config.py` edits here and tells engineer to stop on parent if registry import fails.
- **Recommendation:** `merge-child` / build order should land #1 before #2; no plan revision required.

### acceptable
- **Location:** Stage 1 step 3 — no batch claim
- **Finding:** Explicit Decision mirrors `age_stale_candidate_states` list scan rather than pool claim — consistent with scope (no `database.py`) and parent “if batch-claims” wording on batch statutes.
- **Recommendation:** None.

**R6 (summary):** Scope gate holds (`candidate.py` + `dispatcher.py` only). Forward-only hops, demote ban via `candidate_stage`, no `REQUESTED_*` / `*_RETRY` / `ERROR_*` scheduled hops, tick order after stale aging matches parent pipeline table. Sibling boundaries respected. Estimate confirm 5 is plausible.

context_tokens≈58000
