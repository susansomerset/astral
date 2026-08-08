# AST-1287 — Admin confirm-override for illegal candidate hops

**Linear:** [AST-1287](https://linear.app/astralcareermatch/issue/AST-1287/admin-confirm-override-for-illegal-candidate-hops-state-transition)
**Parent:** [AST-1285](https://linear.app/astralcareermatch/issue/AST-1285/state-transition-validation-for-candidates-is-broken) — State transition validation for candidates is broken
**Publish ref:** `sub/AST-1285/AST-1287-admin-confirm-override`

Admin operators need a core/API path that can apply a **registered** candidate state even when `CANDIDATE_STATES[*].prior_states` would reject the hop, after an explicit confirm signal. Non-override callers (dispatch, stale aging, unconfirmed admin saves) stay fail-closed. Successful forced hops use the same `transition_candidate_state` write + history path as legal hops. Unknown state names remain rejected. This ticket does **not** own the Manage Candidates are-you-sure UI (AST-1288); it supplies the override contract that UI confirms into.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | `IllegalCandidateTransition`; keyword-only `force` on `transition_candidate_state`; force skips prior_states only; INFO log on forced apply | core |
| `src/ui/api/api_candidate.py` | Admin `confirm_state_override`; same-state skip before transition; catch `IllegalCandidateTransition` for structured 400 | ui |

## Stages

### Stage 1: Core force path on `transition_candidate_state`

**Done when:** `transition_candidate_state(id, to_state, force=True)` applies a registered illegal hop and appends history; `force=False` (default) still raises `IllegalCandidateTransition` on illegal hops (including same-state when that hop is illegal under prior_states); unknown `to_state` raises plain `ValueError` even with `force=True`.

1. In `src/core/candidate.py`, near the transition helpers, add:

```python
class IllegalCandidateTransition(ValueError):
    """prior_states rejected this hop; API maps to illegal_candidate_transition."""

    def __init__(self, from_state: str, to_state: str):
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(
            f"Invalid candidate state transition: {from_state} -> {to_state}"
        )
```

2. Change `transition_candidate_state` signature to:

```python
def transition_candidate_state(
    candidate_id: str,
    to_state: str,
    *,
    force: bool = False,
) -> None:
```

3. Keep the existing candidate-not-found and unknown-state checks **before** any prior_states / force logic. Unknown `to_state` must still raise `ValueError(f"Unknown candidate state: {to_state}")` when `force=True` (not `IllegalCandidateTransition`).

4. Replace the current prior_states gate with:

```python
if not force and not _candidate_state_allowed(from_state, to_state):
    raise IllegalCandidateTransition(from_state, to_state)
```

When `force=True`, skip `_candidate_state_allowed` entirely (Archie: every illegal admin hop may be forced after confirm). Still require `to_state in CANDIDATE_STATES`.

   ⚠️ **Decision:** Do **not** add a same-state early-return in core. `X -> X` remains subject to prior_states for automation callers (fail-closed). Manage Candidates re-sends of the current state are handled only in the API (Stage 2).

5. On success (legal or forced), keep the existing path unchanged: `_append_candidate_state_history(...)`, `database.save_candidate(..., state=to_state, state_history=history)`, and `_start_candidate_reap_timer` when `to_state == "DELETED"`. Do **not** add a new history field for forced hops — AC requires forced hops to appear like other successful hops.

6. When `force=True` and the hop would have failed prior_states (i.e. `not _candidate_state_allowed(from_state, to_state)`), emit one INFO line via `src/utils/logging.py` (`get_logger` already used in this module, or add the existing module logger if present) naming `candidate_id`, `from_state`, and `to_state`. Do not log when force is true but the hop was already legal. No history-shape change.

7. Do **not** change any dispatch / stale / delete callers. They keep calling `transition_candidate_state(id, to_state)` with default `force=False` and stay fail-closed on illegal hops (including same-state when illegal).

### Stage 2: Admin API confirm signal + structured illegal error

**Done when:** An admin `PUT /api/candidates/<id>/data` with `confirm_state_override: true` and a registered illegal `state` persists that state (200) and records history; without the flag the same hop returns 400 with `code: "illegal_candidate_transition"` plus `from_state` / `to_state`; when `state` equals the candidate's current state the transition call is skipped (200, non-state fields still saved); non-admins cannot set state or the confirm flag (403); unknown states return 400 without that confirm code.

1. In `src/ui/api/api_candidate.py`, import `IllegalCandidateTransition` alongside `transition_candidate_state`.

2. In `update_candidate_data`, after `state_override = body.pop("state", None)`, also pop:

```python
confirm_override = body.pop("confirm_state_override", False)
```

Treat confirm as true only when the JSON value is strictly `True` (boolean). Any other value (missing, `false`, `"true"`, `1`) is false.

3. Extend the existing admin gate so non-admins cannot send the confirm flag either:

```python
if not g.user.get("is_admin") and (
    state_override is not None or api_key is not None or confirm_override is True
):
    return jsonify({"error": "Admin access required"}), 403
```

4. Keep the existing order: merge/save non-state body fields first, then apply state. That matches parent open question #3 (on cancel of the warning, skip only the state change — non-state fields from the first attempt may already be persisted).

5. When `state_override is not None`, load the candidate and **skip** the transition call when `state_override == (candidate or {}).get("state")` (no force, no error, no history). Manage Candidates always re-sends current state on edit save (`AdminManageCandidates.tsx`); this boundary-only skip keeps automation fail-closed while avoiding a false illegal-hop warning for name-only edits.

   ⚠️ **Decision:** Same-state skip lives only in `update_candidate_data`, not in `transition_candidate_state`. Global same-state idempotency would loosen prior_states for dispatch/stale/delete and is out of scope (parent open question #1 = No).

6. Otherwise call:

```python
transition_candidate_state(
    candidate_id,
    state_override,
    force=(confirm_override is True),
)
```

7. Exception mapping (still HTTP 400):

   - `except IllegalCandidateTransition as e:` return:

```python
return jsonify({
    "error": str(e),
    "code": "illegal_candidate_transition",
    "from_state": e.from_state,
    "to_state": e.to_state,
}), 400
```

   - `except ValueError as e:` (unknown state / not found / other): keep `{"error": str(e)}` **without** `code: "illegal_candidate_transition"` so AST-1288 does not offer confirm-to-invent.

8. When `confirm_override is True` and the hop is legal, behavior is identical to today’s successful path — force is a no-op when prior_states already allow the hop.

9. Do **not** edit `AdminManageCandidates.tsx` or any React file in this ticket. Document the sibling contract in a short comment above the state-transition block in `update_candidate_data`:

```python
# AST-1287 / AST-1288: illegal hops return code=illegal_candidate_transition
# with from_state/to_state; admin retry with confirm_state_override=true forces.
# Same-state in the PUT body is skipped here (not a core no-op).
```

#### Contract for AST-1288 (consumer; not implemented here)

- First save with illegal registered target, no confirm → 400 + `code` / `from_state` / `to_state` (non-state fields may already be saved).
- Cancel → do not retry with confirm; state unchanged.
- Confirm → `PUT` again with at least `{"state": "<to>", "confirm_state_override": true}` (admin auth).
- Legal hops → 200 with no warning signal.
- Same current state in payload → 200; transition not called.
- Unknown state → 400 without `illegal_candidate_transition` code.

## Self-Assessment

**Scope:** `Single-Component` — one core transition function (+ small exception type) and the existing admin candidate-data PUT; no React, no config registry redesign, no company/job transition changes.

**Conf:** `high` — reuses `transition_candidate_state` + admin `PUT …/data` from AST-970; force defaults false; same-state handled only at the admin API boundary so AC4 stays intact.

**Risk:** `Medium` — a bug that defaulted `force=True` or accepted confirm without admin would loosen automation and auth; missing the API same-state skip would spam AST-1288 warnings on every Manage Candidates edit.

## Rules self-review

| Rule | Status |
|------|--------|
| §1.3 DRY | Force path reuses the same history/save/reap success path; typed exception avoids duplicate legality checks in the API |
| §2.1 config | Legality still from `CANDIDATE_STATES.prior_states`; no hardcoded allowlists |
| §2.4 batch | Untouched |
| §2.6 state machine / `astral.state.core-decides-transitions` | Override still goes through core `transition_candidate_state`, not data-layer state write |
| §3.3 imports | ui → core only; no new data/external imports in API |
| §3.5 naming | `confirm_state_override` snake_case on API; `force` keyword on core |
| Auth (`astral.idioms.require-auth-on-protected-endpoints`) | Existing `@require_auth` + `is_admin` gate; confirm flag admin-only |
| Boundaries | No Manage Candidates UI; no prior_states graph repair; no company/job changes; no batch skip-validation switch; no core same-state loosening |

## Revisions

Revision 1 — 2026-08-08
Driven by: Joan `[plan-discuss] round=1 concern` — fix-now: same-state no-op in core loosens automation fail-closed (AC4); discuss: typed exception vs message-prefix contract; discuss: INFO on forced hop.
Changes: Removed core same-state early-return; skip same-state only in `update_candidate_data` before calling transition; raise/catch `IllegalCandidateTransition` instead of string-prefix matching; add INFO log when a forced apply bypasses prior_states.

## Review

**Publish ref:** `origin/sub/AST-1285/AST-1287-admin-confirm-override`  
**Tip:** `117f64c4`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `8cec790b` | `IllegalCandidateTransition` + `force=` on `transition_candidate_state` |
| 2 | `117f64c4` | Admin `confirm_state_override` + structured illegal-hop 400 |
