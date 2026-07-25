# Candidate state registry and transitions (Candidate state machine)

**Linear:** [AST-970](https://linear.app/astralcareermatch/issue/AST-970/candidate-state-registry-and-transitions-candidate-state-machine)  
**Parent:** [AST-871](https://linear.app/astralcareermatch/issue/AST-871/candidate-state-machine)  
**Publish ref:** `origin/sub/AST-871/AST-970-candidate-state-registry`

Replace the four-step candidate lifecycle (`NEW` → `PROFILE_READY` → `CONTEXT_READY` → `LIVE_PROMPTS` + `DELETED`) with a config-backed registry aligned to the job-style `prior_states` machine: full runtime vocabulary (no `PROSPECT`), stale/retry/error companions, `INACTIVE` + `DELETED` (DELETED starts a configured reap timer), and enforced transitions. Manual hops into topic-ready stages are allowed. Does **not** own transition history (AST-971), dispatch claim / scheduler wiring (AST-972), or legacy row / FK / consumer migration (AST-973).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Replace `CANDIDATE_STATES` with job-style registry (`prior_states`, companions, stale/reap metadata); remove `ASTRAL_CONFIG["candidate_state_transitions"]`; add `CANDIDATE_CONFIG` reap default; update config-local gates that assert membership (`NAV_CONFIG` visible keys, `build_state_ui_manifest` gen_states, `INFLOW_CONFIG` candidate search trigger) so `config.py` imports cleanly | utils |
| `src/core/candidate.py` | Rewrite `transition_candidate_state` to enforce `prior_states`; route `delete_candidate` through DELETED transition + reap timer start; create path uses `NEW_CANDIDATE`; retire auto hops to `PROFILE_READY` / `CONTEXT_READY`; add stale-aging helper; add reap-due helpers | core |
| `src/ui/api/api_system.py` | `_is_at_or_past` uses optional `progress_rank` on `CANDIDATE_STATES` (INACTIVE/DELETED do not unlock gated nav) | ui |
| `src/ui/api/api_candidate.py` | Admin state override goes through `transition_candidate_state` (fail closed); `/states` unchanged shape (list of keys) | ui |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Replace state-machine section with new vocabulary + prior_states pointer | docs |
| `docs/ASTRAL_CODE_RULES.md` | Update §2.1 `CANDIDATE_STATES` bullet and §2.6.3 Candidates narrative to the new registry (no parallel hardcoded sets) | docs |

**Out of scope (siblings):** history table/writes (AST-971); dispatcher claim of `REQUESTED_*` / invoking aging on a schedule (AST-972); DB row remap, `dispatch_task` FK remap, full nav/UI consumer sweep beyond config-local string updates listed above (AST-973).

## Stage 1: Config registry — vocabulary, prior_states, companions

**Done when:** `CANDIDATE_STATES` contains every runtime key below with `prior_states` / companion metadata; `ASTRAL_CONFIG["candidate_state_transitions"]` is gone; `python -c "from src.utils.config import CANDIDATE_STATES"` succeeds; `PROSPECT` is absent.

1. In `src/utils/config.py`, replace the `CANDIDATE_STATES` block (currently `NEW` / `PROFILE_READY` / `CONTEXT_READY` / `LIVE_PROMPTS` / `DELETED`) with the registry below. Preserve insertion order exactly as listed (happy path, then terminals). Every entry must include `progress_rank` (int) for nav gating.

```
# progress_rank: happy-path depth; companions share the primary's rank;
# INACTIVE/DELETED use -1 so they never satisfy "at or past" gates.

NEW_CANDIDATE              prior_states=None, progress_rank=0
INTAKE_INITIATED           prior_states=["NEW_CANDIDATE"], progress_rank=1
REQUIRED_TOPICS_READY      prior_states=["INTAKE_INITIATED", "REQUIRED_TOPICS_READY_STALE"],
                           stale_after_hours=72, stale_state="REQUIRED_TOPICS_READY_STALE",
                           progress_rank=2
REQUIRED_TOPICS_READY_STALE prior_states=["REQUIRED_TOPICS_READY"], progress_rank=2
ALL_TOPICS_READY           prior_states=["REQUIRED_TOPICS_READY", "REQUIRED_TOPICS_READY_STALE",
                                         "ALL_TOPICS_READY_STALE"],
                           stale_after_hours=72, stale_state="ALL_TOPICS_READY_STALE",
                           progress_rank=3
ALL_TOPICS_READY_STALE     prior_states=["ALL_TOPICS_READY"], progress_rank=3
REQUESTED_RESUME           prior_states=["ALL_TOPICS_READY", "ALL_TOPICS_READY_STALE",
                                         "REQUESTED_RESUME_RETRY"],
                           retry_state="REQUESTED_RESUME_RETRY",
                           error_state="REQUESTED_RESUME_ERROR",
                           progress_rank=4
REQUESTED_RESUME_RETRY     prior_states=["REQUESTED_RESUME"], progress_rank=4
REQUESTED_RESUME_ERROR     prior_states=["REQUESTED_RESUME", "REQUESTED_RESUME_RETRY"],
                           progress_rank=4
RESUME_READY               prior_states=["REQUESTED_RESUME", "REQUESTED_RESUME_RETRY",
                                         "RESUME_READY_STALE"],
                           stale_after_hours=168, stale_state="RESUME_READY_STALE",
                           progress_rank=5
RESUME_READY_STALE         prior_states=["RESUME_READY"], progress_rank=5
REQUESTED_ARTIFACTS        prior_states=["RESUME_READY", "RESUME_READY_STALE",
                                         "REQUESTED_ARTIFACTS_RETRY"],
                           retry_state="REQUESTED_ARTIFACTS_RETRY",
                           error_state="REQUESTED_ARTIFACTS_ERROR",
                           progress_rank=6
REQUESTED_ARTIFACTS_RETRY  prior_states=["REQUESTED_ARTIFACTS"], progress_rank=6
REQUESTED_ARTIFACTS_ERROR  prior_states=["REQUESTED_ARTIFACTS", "REQUESTED_ARTIFACTS_RETRY"],
                           progress_rank=6
ARTIFACTS_READY            prior_states=["REQUESTED_ARTIFACTS", "REQUESTED_ARTIFACTS_RETRY",
                                         "ARTIFACTS_READY_STALE"],
                           stale_after_hours=168, stale_state="ARTIFACTS_READY_STALE",
                           progress_rank=7
ARTIFACTS_READY_STALE      prior_states=["ARTIFACTS_READY"], progress_rank=7
ACTIVE_SEARCH              prior_states=["ARTIFACTS_READY", "ARTIFACTS_READY_STALE",
                                         "PAUSE_SEARCH"],
                           progress_rank=8
PAUSE_SEARCH               prior_states=["ACTIVE_SEARCH"], progress_rank=8
INACTIVE                   prior_states=None, progress_rank=-1
DELETED                    prior_states=None, progress_rank=-1,
                           reap_after_hours=720
```

⚠️ **Decision:** Align candidate enforcement to job-style `prior_states` on the registry (not a parallel `candidate_state_transitions` tuple list). Jobs already deleted `job_state_transitions`; candidates follow the same pattern so AST-971/972 can share mental model with `transition_job_state`.

⚠️ **Decision:** Stale hours are literals in config (72h topic-ready waits, 168h resume/artifacts ready waits; DELETED reap 720h / 30d). Susan did not specify numbers — these are product defaults / config knobs; change only in `config.py` later (no code change required).

⚠️ **Decision:** `INACTIVE` and `DELETED` use `prior_states=None` (unrestricted entry from any current state), matching unrestricted job terminal patterns. Disallowed hops still fail when `to_state` is missing from the registry.

⚠️ **Decision (stale→next edges):** Every waiting stage’s `*_STALE` companion must appear in the **next** happy-path state’s `prior_states` (not only recover-to-primary). Graph check: `REQUIRED_TOPICS_READY_STALE` → `ALL_TOPICS_READY`; `ALL_TOPICS_READY_STALE` → `REQUESTED_RESUME`; `RESUME_READY_STALE` → `REQUESTED_ARTIFACTS`; `ARTIFACTS_READY_STALE` → `ACTIVE_SEARCH`. No other waiting stages exist in this registry.

⚠️ **Decision (ERROR exits, v1):** `REQUESTED_RESUME_ERROR` / `REQUESTED_ARTIFACTS_ERROR` do **not** list forward priors into retry/ready. Escape is via unrestricted `INACTIVE` / `DELETED` only. AST-972 may propose `*_ERROR` → `*_RETRY` / re-request edges later; do not add them in AST-970.

⚠️ **Decision (AC#4 vs AST-972):** `age_stale_candidate_states` lands in this ticket; do **not** register a dispatch task or scheduler hook here — AST-972 owns invocation.

2. Add a small `CANDIDATE_CONFIG` dict immediately after `CANDIDATE_STATES` with a single key used as documentation/default mirror (do not fork per-state hours here):

```python
CANDIDATE_CONFIG = {
    # Per-state stale_after_hours / DELETED reap_after_hours live on CANDIDATE_STATES entries.
    # This block holds only cross-cutting candidate lifecycle knobs that are not per-state.
    "initial_state": "NEW_CANDIDATE",
}
```

3. Delete the entire `ASTRAL_CONFIG["candidate_state_transitions"]` key and its comment block (the three-tuple list under `# --- Candidate state machine`).

4. Config-local string updates required for import/assert coherence (not the full consumer sweep — that is AST-973):
   - `NAV_CONFIG`: change group `"visible": "LIVE_PROMPTS"` → `"ACTIVE_SEARCH"` (Jobs, Companies); `"visible": "CONTEXT_READY"` → `"RESUME_READY"` (Artifacts).
   - In `build_state_ui_manifest`, set `gen_states = ["RESUME_READY", "ACTIVE_SEARCH"]` (must remain keys ⊆ `CANDIDATE_STATES`).
   - `INFLOW_CONFIG["discovery"]["dispatch_trigger_state"]`: `"LIVE_PROMPTS"` → `"ACTIVE_SEARCH"` (candidate search-ready gate name only; AST-972 owns claim wiring).

5. Update the module header comment that lists `CANDIDATE_STATES` so it describes prior_states / companions, not the four-step list.

6. Add a module-level assert after `CANDIDATE_STATES` is defined:

```python
assert "PROSPECT" not in CANDIDATE_STATES
for _name, _cfg in CANDIDATE_STATES.items():
    assert "progress_rank" in _cfg, _name
    assert "prior_states" in _cfg, _name
    _stale = _cfg.get("stale_state")
    if _stale is not None:
        assert _stale in CANDIDATE_STATES and "stale_after_hours" in _cfg, _name
    _retry = _cfg.get("retry_state")
    if _retry is not None:
        assert _retry in CANDIDATE_STATES, _name
    _err = _cfg.get("error_state")
    if _err is not None:
        assert _err in CANDIDATE_STATES, _name
assert CANDIDATE_STATES["DELETED"].get("reap_after_hours", 0) > 0
assert CANDIDATE_CONFIG["initial_state"] in CANDIDATE_STATES
```

## Stage 2: Enforced transitions, DELETED reap start, stale aging helper

**Done when:** Illegal hops raise `ValueError`; happy-path and documented side-path hops succeed; entering `DELETED` records reap metadata from config; `age_stale_candidate_states` moves due waiting rows to their `stale_state`; create/delete/admin paths no longer write retired state names.

1. In `src/core/candidate.py`, add helpers next to the existing `_CANDIDATE_STATE_LIST` usage:

```python
def _candidate_prior_states(to_state: str):
    cfg = CANDIDATE_STATES.get(to_state)
    if cfg is None:
        raise ValueError(f"Unknown candidate state: {to_state}")
    return cfg.get("prior_states")

def _candidate_state_allowed(from_state: str, to_state: str) -> bool:
    prior = _candidate_prior_states(to_state)
    if prior is None:
        return True
    return from_state in prior
```

2. Rewrite `transition_candidate_state(candidate_id, to_state)`:
   - Load candidate; raise if missing.
   - If `to_state not in CANDIDATE_STATES`: raise `ValueError`.
   - If not `_candidate_state_allowed(from_state, to_state)`: raise `ValueError` with message `Invalid candidate state transition: {from} -> {to}`.
   - Call `database.save_candidate(candidate_id, state=to_state)`.
   - If `to_state == "DELETED"`: call `_start_candidate_reap_timer(candidate_id)` (step 3).
   - Do **not** write transition history here (AST-971).

3. Add `_start_candidate_reap_timer(candidate_id)`:
   - Read `hours = CANDIDATE_STATES["DELETED"]["reap_after_hours"]`.
   - Merge into `candidate_data`:

```python
{"lifecycle": {"reap_after_hours": hours, "reap_started_at": <UTC ISO8601 now>}}
```

   - Use existing `database.save_candidate(..., candidate_data=..., merge=True)`.
   - ⚠️ **Decision:** Persist reap start on `candidate_data.lifecycle` (no new SQL column). Due time is `reap_started_at + reap_after_hours`. Hard-delete executor and production purge of already-DELETED rows are AST-973; this ticket only starts the timer.

4. Add public helpers (no scheduler wiring):

```python
def candidate_reap_due_at(candidate: dict) -> Optional[datetime]:
    """Return UTC due datetime when state is DELETED and lifecycle.reap_started_at is set; else None."""

def is_candidate_reap_due(candidate: dict, *, now: Optional[datetime] = None) -> bool:
    """True when DELETED and now >= candidate_reap_due_at."""
```

5. Rewrite `delete_candidate(candidate_id)` to call `transition_candidate_state(candidate_id, "DELETED")` instead of bypassing validation. Because `DELETED.prior_states is None`, any current state may enter DELETED.

6. Create path (`initiate` / create currently `state="NEW"`): write `state=CANDIDATE_CONFIG["initial_state"]` (`NEW_CANDIDATE`).

7. In `parse_candidate_resume`: **remove** the block that transitions `NEW` → `PROFILE_READY`. After save of resume artifacts, leave state unchanged.
   ⚠️ **Decision:** Legacy auto-progress into `PROFILE_READY` is retired. Intake / operators move `NEW_CANDIDATE` → `INTAKE_INITIATED` (and later topic-ready) via explicit transitions; Topic Menu (AST-953) will later automate topic-ready.

8. Rewrite `check_context_complete(candidate_id)`:
   - Keep the four context-field completeness check.
   - **Do not** call `transition_candidate_state(..., "CONTEXT_READY")` (state retired).
   - Return `True` when all four fields are non-empty; `False` otherwise.
   - Remove `_CONTEXT_READY_IDX` / slice-based “already past CONTEXT_READY” short-circuit that indexes retired names. Optional: if `progress_rank` of current state is `>= CANDIDATE_STATES["ALL_TOPICS_READY"]["progress_rank"]` and current rank >= 0, return `True` without re-checking fields (context already accepted further along the path).

9. Add `age_stale_candidate_states(*, now: Optional[datetime] = None) -> int`:
   - Load all non-deleted candidates via existing list/get helpers (include only rows whose `state` is a key in `CANDIDATE_STATES` with both `stale_after_hours` and `stale_state`).
   - For each, if `state_changed_at` (or equivalent timestamp already on the row) is older than `stale_after_hours`, call `transition_candidate_state(id, stale_state)`.
   - Skip rows whose current state is already the stale companion.
   - Return count of successful transitions.
   - ⚠️ **Decision:** Aging logic lives in core here (AC #4). AST-972 owns calling this from dispatch/scheduler and claiming `REQUESTED_*` batches — do not register a dispatch task in this ticket.

10. In `src/ui/api/api_candidate.py`, when admin supplies `state` override, call `transition_candidate_state(candidate_id, state_override)` instead of `save_candidate_admin(..., state=...)`. On `ValueError`, return 400 with the error message. Non-state admin fields still use `save_candidate_admin`.

11. In `src/ui/api/api_system.py`, change `_is_at_or_past` to compare `progress_rank`:

```python
def _progress_rank(state: str) -> int:
    cfg = CANDIDATE_STATES.get(state) or {}
    return int(cfg.get("progress_rank", -1))

def _is_at_or_past(current_state: str, required_state: str) -> bool:
    return _progress_rank(current_state) >= _progress_rank(required_state) and _progress_rank(current_state) >= 0
```

Remove the old `_STATE_INDEX` enumeration if unused.

## Stage 3: Docs — data model + Code Rules narrative

**Done when:** `CANDIDATE_DATA_MODEL.md` and Code Rules §2.1 / §2.6.3 describe the new registry; no doc still teaches the four-step machine as current truth in those two places.

1. In `docs/features/candidate/CANDIDATE_DATA_MODEL.md`, replace the **State machine** section with:
   - Runtime keys listed in Stage 1 (explicitly: no `PROSPECT`).
   - Note that transitions are enforced via `CANDIDATE_STATES[*].prior_states` in `transition_candidate_state`.
   - Note manual topic-ready hops until AST-953.
   - Note DELETED reap: `candidate_data.lifecycle.reap_started_at` + `reap_after_hours` from registry.
   - Point legacy migration to AST-973.

2. In `docs/ASTRAL_CODE_RULES.md`:
   - §2.1 bullet **CANDIDATE_STATES**: replace the four-step description with “Candidate state registry; each entry has `prior_states` (list or `None`), optional `stale_after_hours`/`stale_state`, optional `retry_state`/`error_state`, `progress_rank`; `DELETED` carries `reap_after_hours`. No `PROSPECT`.”
   - §2.6.3 Candidates: replace the simple progression + `candidate_state_transitions` text with prior_states enforcement via `transition_candidate_state`, list the happy path `NEW_CANDIDATE` → … → `ACTIVE_SEARCH`, and note companions + INACTIVE/DELETED. Remove `CONTEXT_READY` / `check_context_complete` as the gate for a state transition (completeness helper may remain; it does not write state).

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — replaces the candidate state vocabulary and enforcement path in config + core + thin API/nav rank helper; docs updated to match. Sibling tickets still own history, dispatch claim, and legacy data migration.

**Conf:** `high` — mirrors existing `JOB_STATES` / `transition_job_state` patterns; ticket boundaries and parent AC are explicit; concrete registry and call-site rewrites are specified.

**Risk:** `HIGH` — wrong `prior_states` or premature removal of legacy auto-transitions can block onboarding or unlock nav incorrectly until AST-973 migrates rows; mitigated by fail-closed validation, `progress_rank` for INACTIVE/DELETED, and leaving DB remaps to AST-973.

## Code Rules self-review

| Rule | Result |
|------|--------|
| §1.3 DRY | Single registry in config; no duplicate transition tuple list |
| §2.1 config SSOT | All state names, stale hours, reap hours, initial state in config |
| §2.4 batch | No new batch claim APIs (AST-972) |
| §2.6 state machine | Core decides transitions; data layer still receives target state only; prior_states enforced in core like jobs |
| §3.3 imports | Helpers stay in `candidate.py` / `config.py`; no new cross-layer violations |
| §3.5 naming | UPPERCASE state keys; snake_case config keys |

No unresolved conflicts. Code Rules narrative update is Stage 3 (required so §2.6.3 does not contradict the shipped registry).

## Revisions

Revision 1 — 2026-07-23
Driven by: Joan `[plan-discuss] round=1 concern` fix-now — `ALL_TOPICS_READY.prior_states` omitted `REQUIRED_TOPICS_READY_STALE`, so happy path broke after stale aging.
Changes:
- Added `REQUIRED_TOPICS_READY_STALE` to `ALL_TOPICS_READY.prior_states`.
- Documented full stale→next graph check (four edges); no other missing edges found.
- Recorded Decisions for ERROR exits (v1 closed; AST-972 may extend), hour literals as config knobs, and AC#4 helper vs AST-972 scheduler ownership.

## Review

| Field | Value |
| -- | -- |
| Ticket | AST-970 |
| Publish ref | `origin/sub/AST-871/AST-970-candidate-state-registry` |
| Built | `5e0a8856678efff89a917a4d19e3de8bc56f6406` |
| Notes | Stages 1–3 implemented per plan (registry, transitions/reap/stale, docs). |

### Radia code-rubric.v1 (revision=1)

**Overall:** DISCUSS  
**Publish tip reviewed:** `5a75bdc87a52131c8041bc5c738612b18158efc3` (`origin/dev...origin/sub/AST-871/AST-970-candidate-state-registry`)

**What’s solid**
- Job-style `CANDIDATE_STATES` registry (no `PROSPECT`), `prior_states` enforcement, DELETED reap start on `candidate_data.lifecycle`, `age_stale_candidate_states` without scheduler wiring.
- Admin state override fail-closed via `transition_candidate_state`; `progress_rank` gates terminals.
- Sibling boundaries held (no history table, no dispatch claim, no legacy remap).

**Issues**
- **discuss (C4 straggler):** Joan excluded `astral.git.engineer-test-tree-ban` at plan time; Betty’s `test`/`merge-tests` land on the tip so the statute is in-scope. Substance **conforms** (engineers did not edit test-tree in `code` commits).
- **advisory:** `CANDIDATE_DATA_MODEL.md` context section still says four fields “gate the `CONTEXT_READY` state transition” while the State machine section is updated.

**Recommended actions**
- Engineer: acknowledge straggler / no product change required for it; optional one-line doc cleanup on the CONTEXT_READY leftover (or leave for AST-973 consumer sweep).

## Resolution

2026-07-24 — Radia code-rubric.v1 revision=1 (**DISCUSS**; fix-now none).

| Finding | Action |
| -- | -- |
| discuss — C4 `engineer-test-tree-ban` straggler | Acknowledged: Betty owns tip `tests/**` + bible; engineer `code`/`docs` commits did not touch test-tree. No product change. |
| advisory — `CONTEXT_READY` leftover in data-model context section | One-line cleanup in `CANDIDATE_DATA_MODEL.md`: completeness helper, not a state-transition gate. |
