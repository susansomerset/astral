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

## Radia review

[code-rubric] revision=2

**Rubric:** code-rubric.v2
**Publish ref tip:** `0f994ea4`
**Overall:** DISCUSS

**Full-set sweep:** all 64 active statutes scored in-session (17 universal + 47 scoped) against `git diff origin/dev...origin/sub/AST-1285/AST-1287-admin-confirm-override`. No `violates`. Three benign stragglers (C4) below — all resolve to `conforms` on inspection, none block.

**What's solid:** `IllegalCandidateTransition(ValueError)` replaces the round-1 message-prefix contract per Joan's plan-discuss finding, and the API catches the subclass before the bare `ValueError` (correct order — `except IllegalCandidateTransition` before `except ValueError`). `force=True` still routes through `transition_candidate_state` and the same history/save/reap path — no raw data poke (`pattern.state.entity-state-transitions` intact). Unknown `to_state` raises plain `ValueError` even with `force=True`, so AST-1288 can't confirm-to-invent (`code` key absent from that response body per the new test). The admin gate (`is_admin`) now also covers `confirm_state_override`, so non-admins can't force a hop by sending the flag alone. Same-state skip lives only in `update_candidate_data` (API boundary), matching Joan's fix-now resolution — core stays fail-closed for every other caller (dispatch/stale/`start_requested_artifacts`/`delete_candidate`), confirmed by `TestAst1287ForceTransition::test_same_state_illegal_without_force`. The forced-bypass `logger.info` line is gated correctly (`force and not allowed` only — silent on already-legal hops) and ties to the in-code comment + Joan's plan-rubric sign-off (justification chain per C6 §5b). `python3 -m py_compile` clean on both touched backend modules. Engineer/Betty test-tree boundary holds — `code(AST-1287)` commits touch only `src/`; the `test(AST-1287)` commit (merged in via the single `merge-tests(AST-1287)` SHA) touches only `tests/` + `docs/test-bible/`. Test coverage matches every plan "Done when" branch (force+history, default-reject, unknown-state-even-with-force, same-state-illegal-without-force, force-on-legal-hop, confirm-forces, same-state-skip, non-admin-403, unknown-state-400-no-code, string-`"true"`-does-not-force).

**Findings**

- **discuss — straggler (C4), `astral.state.job-prior-states-enforced`:** Ticket's Considered-but-excluded list marks this out of scope ("jobs untouched; candidate-only override"), but the sweep's `applies_when.paths: ["src/core/**", ...]` glob matches on `src/core/candidate.py` alone, so it scores in-scope rather than `not-applicable`. On inspection: no job-transition code touched — `conforms`, no action needed.
- **discuss — straggler (C4), `astral.batch.claim-process-release`:** Same shape — ticket excludes it ("no batch force switch; `dispatcher.py` untouched"), sweep's broad `src/core/**` glob still matches. On inspection: no batch/dispatch code touched — `conforms`, no action needed.
- **discuss — straggler (C4), `astral.layers.ui-config-driven-business-logic`:** Ticket excludes the React confirm UX (AST-1288's territory), sweep's `src/ui/**` glob matches on the backend `api_candidate.py` change alone. On inspection: this *is* the API layer the rule wants business logic resolved in, and no React file changed — `conforms`, no action needed.
- **advisory — import ordering:** `IllegalCandidateTransition` is inserted between `start_requested_artifacts` and `transition_candidate_state` in the `src.core.candidate` import block in `api_candidate.py`, breaking the otherwise-alphabetical order (capital `I` out of sequence with the surrounding lowercase names). Cosmetic only; not a statute violation.

**Pattern conformance:**

| id | verdict | one-line |
|----|---------|----------|
| `pattern.state.entity-state-transitions` | conforms | Force still resolved + written via `transition_candidate_state`; data/history path unchanged |
| `pattern.ui.admin-endpoint` | conforms | Confirm signal added to the existing `@require_auth` admin-gated `PUT …/data`; no new route, no frontend business rules |

**Plan adherence:** Diff matches the Files Changed table and both stages exactly, including the Revision 1 delta (typed exception, API-boundary same-state skip, forced-hop INFO line) that Joan's round-1 `[plan-discuss]` concern required. Self-Assessment `Scope: Single-Component` / `Conf: high` matches the diff's real footprint; no `!!-NONE` conflict. Joan's plan-rubric verdict (`[plan-rubric] revision=1`, **Overall: APPROVED**) is attached on the Linear issue — its round-1 `fix-now` and both `discuss` items are cured in the shipped diff (verified above), and its remaining `discuss` (uncatalogued "admin confirmed prior-states override" pattern) is Archie's corpus call, not a block here.

**Cross-ticket boundary:** No Manage Candidates React edits (AST-1288 untouched as planned); no job/company transition code; no `prior_states` graph repair; no batch/dispatch skip-validation switch.

## Frame diff

(none — ticket description AC/scope table already accurate)

context_tokens≈58000

— Radia
