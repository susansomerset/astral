<!-- linear-archive: AST-1287 archived 2026-08-19 -->

## Linear archive (AST-1287)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1287/admin-confirm-override-for-illegal-candidate-hops-state-transition  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1285 — State transition validation for candidates is broken  
**Blocked by / blocks / related:** parent: AST-1285; blocks: AST-1288

### Description

## What this implements

Own the admin-authorized path that can apply a registered candidate state even when prior-states would reject it, while keeping non-override callers fail-closed; record history on success; reject unknown states. Does **not** own the Manage Candidates warning UI (sibling Manage Candidates are-you-sure).

Archie answers locked for this epic: every illegal admin hop may be forced after confirm; graph repair of prior_states is out of scope; on cancel of the warning, skip only the state change (non-state field edits may still apply).

## In scope

- [X] `pattern.state.entity-state-transitions` — force still via `transition_candidate_state`, not a raw data poke
- [X] `pattern.ui.admin-endpoint` — confirm signal on existing admin-gated `PUT …/data`
- [X] `astral.state.core-decides-transitions` — core owns legality + apply
- [X] `astral.config.config-source-of-truth` — vocabulary/prior_states from `CANDIDATE_STATES`
- [X] `astral.idioms.require-auth-on-protected-endpoints` — confirm flag admin-only
- [X] `astral.standards.no-hardcoded-sets` — no parallel frontend/API allowlist for states
- [X] `astral.standards.data-raises-caller-logs` — core `ValueError`; UI maps to 400 JSON
- [X] `astral.layers.import-direction` — ui → core only for this change

## Considered but excluded

- [X] `astral.state.job-prior-states-enforced` — jobs untouched; candidate-only override
- [X] `astral.batch.claim-process-release` / dispatch skip-validation — automation stays fail-closed; no batch force switch (`src/core/dispatcher.py`)
- [X] `astral.layers.ui-config-driven-business-logic` (React confirm UX) — owned by AST-1288 `AdminManageCandidates.tsx`
- [X] `pattern.config.config-block` changes to loosen `prior_states` — graph repair out of scope
- [X] Company transition enforcement — out of epic boundaries

## Acceptance criteria

1. [x] From Manage Candidates, an admin who chooses a registered target state that the registry rejects from the current state sees an are-you-sure warning that identifies from → to before the state changes. (UI owned by sibling; this child supplies the override path the UI confirms into.)
2. [x] Confirming the warning results in the candidate persisting in the chosen target state; canceling leaves the prior state unchanged.
3. [x] Non-admin callers cannot force an illegal candidate state hop.
4. [x] Automated/dispatch/stale paths still fail closed on illegal hops (no confirm path).
5. [x] Successful forced admin hops appear in candidate transition history like other successful hops.
6. [x] Requests for unknown state names still fail (no confirm-to-invent).

## Boundaries

* Does not own Manage Candidates are-you-sure UI.
* Does not redesign candidate lifecycle vocabulary or loosen prior_states graph.
* Does not change company/job transition enforcement.
* Does not add a general skip-validation switch for batch/dispatch.

## Notes for planning

New pattern flag from parent (admin confirmed prior-states override) — implement product behavior under reuse patterns; do not treat unapproved catalog id as law.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1285-state-transition-validation`, child `sub/AST-1285/AST-1287-admin-confirm-override`. Created at dispatch-parent.

### Comments

#### ada — 2026-08-08T20:50:44.541Z
Publish ref rebuilt clean for merge-child.

`origin/sub/AST-1285/AST-1287-admin-confirm-override` @ `700807a1` — rewritten from `origin/ftr/AST-1285-state-transition-validation` by cherry-picking only AST-1287 delivery commits (plan/revise/code/docs/test/merge-tests/resolve). Dropped `bbf5c112` (`Merge remote-tracking branch 'origin/dev'…`) and sibling AST-1286 history that had ridden in with it.

`validate-sub-log.sh sub/AST-1285/AST-1287-admin-confirm-override AST-1287 ftr/AST-1285-state-transition-validation` → ok. Status stays **User Testing**.

#### chuckles — 2026-08-08T20:49:22.210Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

`validate-sub-log` fails on `bbf5c112` (`Merge remote-tracking branch 'origin/dev' into sub/AST-1285/AST-1287-admin-confirm-override`).

@Ada Lovelace — rewrite `origin/sub/AST-1285/AST-1287-admin-confirm-override` so the range `origin/ftr/AST-1285-state-transition-validation..sub` has no `Merge remote-tracking branch` subjects. Keep AST-1287 `plan|code|merge-tests|docs|resolve` sequence; cherry-pick onto `origin/ftr/AST-1285-state-transition-validation` (merge `origin/ftr` only — never `git pull origin/dev` onto sub). Force-push publish ref when clean.

— Chuckles

#### radia — 2026-08-08T20:47:38.081Z
[code-rubric] revision=2

**Rubric:** code-rubric.v2
**Ticket:** AST-1287
**Publish ref:** `origin/sub/AST-1285/AST-1287-admin-confirm-override` @ `0f994ea4` (code diff tip; doc-only `d2c77230` review append on top)
**Overall:** DISCUSS

## Plan adherence

- Diff matches the Files Changed table and both stages exactly, including the Revision 1 delta (typed `IllegalCandidateTransition`, same-state skip moved to the API boundary, forced-hop INFO line) that Joan's round-1 `[plan-discuss]` concern required.
- Joan's attached `[plan-rubric] revision=1` verdict is **APPROVED**; its round-1 fix-now and both discuss items are cured in the shipped diff (verified directly against the code).
- Self-Assessment `Scope: Single-Component` / `Conf: high` matches the diff's real footprint; no boundary creep (no Manage Candidates React edits, no job/company transition code, no `prior_states` graph repair, no batch skip-validation switch).

## Findings

- **discuss — straggler (C4), `astral.state.job-prior-states-enforced`:** Ticket excludes it ("jobs untouched"); the sweep's broad `src/core/**` path glob still matches on `candidate.py` alone. On inspection: `conforms`, no job code touched — no action needed.
- **discuss — straggler (C4), `astral.batch.claim-process-release`:** Ticket excludes it ("no batch force switch; dispatcher untouched"); same broad-glob straggler. On inspection: `conforms` — no action needed.
- **discuss — straggler (C4), `astral.layers.ui-config-driven-business-logic`:** Ticket excludes the React confirm UX (AST-1288's territory); the sweep's `src/ui/**` glob matches on the backend `api_candidate.py` change alone. On inspection: this *is* the API layer the rule wants logic in, and no React file changed — `conforms` — no action needed.
- **advisory — import ordering:** `IllegalCandidateTransition` breaks alphabetical order in the `src.core.candidate` import block in `api_candidate.py`. Cosmetic only.

No fix-now findings. Full 64-statute active set (17 universal + 47 scoped) scored in-session; no `violates`.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| `pattern.state.entity-state-transitions` | conforms | Force still resolved + written via `transition_candidate_state`; no raw data poke |
| `pattern.ui.admin-endpoint` | conforms | Confirm signal on existing `@require_auth` admin-gated `PUT …/data`; no new route, no frontend business rules |

## Frame diff

(none — ticket description AC/scope table already accurate)

**What's solid:** Typed exception replaces the round-1 message-prefix contract; unknown-state responses correctly omit the `illegal_candidate_transition` code so AST-1288 can't confirm-to-invent; non-admins can't force a hop via the flag alone; same-state skip stays API-only so every other caller (dispatch/stale/`start_requested_artifacts`/`delete_candidate`) keeps failing closed; `python3 -m py_compile` clean on both touched backend modules; engineer/Betty test-tree boundary holds (single `merge-tests(AST-1287)` SHA carries the test-tree changes, `code(AST-1287)` commits touch only `src/`).

**Recommended actions:** None blocking. Optional: alphabetize the new import in `api_candidate.py`.

Full review + straggler detail also appended as `docs(AST-1287): Radia review — discuss` on `origin/sub/AST-1285/AST-1287-admin-confirm-override` @ `d2c77230`.

context_tokens≈62000

— Radia

#### betty — 2026-08-08T20:38:23.018Z
## QA test manifest

`origin/sub/AST-1285/AST-1287-admin-confirm-override` @ `0f994ea4` (`merge-tests(AST-1287): origin/tests 42c75c198e938def5ea37945d1ee7c39e4d223d6`)

### 1. Existing coverage (bible-backed)
1. `tests/component/core/test_candidate.py::TestTransitionCandidateState`
2. `tests/component/core/test_candidate.py::TestAst970CandidateStateMachine::test_error_state_has_no_forward_happy_path`
3. `tests/component/core/test_candidate.py::TestAst971CandidateTransitionHistory::test_illegal_hop_writes_nothing`
4. `tests/component/ui/api/test_api_candidate.py::TestAst970AdminStateOverride`
5. `tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_update_merges_data_state_and_api_key`
6. `tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_non_admin_cannot_create_delete_or_override_state`

### 2. Broken / obsolete (revised this pass)
1. AST-970 admin `assert_called_once_with(id, state)` — product now passes `force=` keyword; revised to `force=False`.
2. AST-970 illegal-hop mock raised bare `ValueError` — core now raises `IllegalCandidateTransition`; API returns `code` / `from_state` / `to_state`; mock + asserts updated.
3. Core illegal-hop raises now typed as `IllegalCandidateTransition` in transition / AST-970 / AST-971 cases above.

### 3. Gaps (new this pass)
1. `tests/component/core/test_candidate.py::TestAst1287ForceTransition` — force applies illegal hop + history; default reject + attrs; force cannot invent unknown state; same-state still illegal without force; force on legal hop ok.
2. `tests/component/ui/api/test_api_candidate.py::TestAst1287AdminConfirmOverride` — confirm forces; same-state skips transition (non-state still saved); non-admin confirm → 403; unknown state 400 without illegal code; string `"true"` does not force.

**Integration:** none (nav scenario untouched; no new integration coverage).

### Run
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_candidate.py::TestAst1287ForceTransition \
  tests/component/core/test_candidate.py::TestTransitionCandidateState \
  tests/component/core/test_candidate.py::TestAst970CandidateStateMachine::test_error_state_has_no_forward_happy_path \
  tests/component/core/test_candidate.py::TestAst971CandidateTransitionHistory::test_illegal_hop_writes_nothing \
  tests/component/ui/api/test_api_candidate.py::TestAst1287AdminConfirmOverride \
  tests/component/ui/api/test_api_candidate.py::TestAst970AdminStateOverride \
  tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_update_merges_data_state_and_api_key \
  tests/component/ui/api/test_api_candidate.py::TestCandidateRoutes::test_non_admin_cannot_create_delete_or_override_state \
  -q
```

### Bible (on publish ref)
- `docs/test-bible/core/candidate.md` shasum `926b02ffbfe8df103fb707c6119027c4bb6d9bad`
- `docs/test-bible/ui/api/api_candidate.md` shasum `d87cd572e980f082adb0167efdeeb85c4555bd3b`

#### joan — 2026-08-08T20:34:02.595Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1287
**Overall:** APPROVED
**Publish ref tip:** `origin/sub/AST-1285/AST-1287-admin-confirm-override` @ `0efa41d1` (round-1 concern was scored at `ea91f821`)

## Traceability

AC1→S2 (override contract; warning UI is AST-1288); AC2→S1.4–5 + S2.5–6; AC3→S2.3; AC4→S1.4 + S1.7; AC5→S1.5; AC6→S1.3 + S2.7. Parent AC3 (legal hops stay quiet) → S2.8 + the AST-1288 contract. No unmapped AC, no orphan stage.

**Considered:** same 52 active statutes as round 1 (18 universal + 34 scoped on layers `core`/`ui`, unchanged Files Changed paths), 12 scoped actives excluded. All now score `conforms` — the round-1 `violates` on `astral.standards.in-scope-only` is cured. Cited patterns `pattern.state.entity-state-transitions`, `pattern.ui.admin-endpoint`, `pattern.config.config-block` all resolve as `status: approved`.

## Round 1 resolution

**fix-now cleared.** The core early-return is gone. `transition_candidate_state` keeps the prior-states gate for every caller, and Stage 1 "Done when" now states outright that `X -> X` still raises when illegal, so consult/dispatch, stale aging, `start_requested_artifacts`, and `delete_candidate` keep the behavior they have today. AC4 is intact and the deferred graph question stays deferred. The same-state skip moved to `update_candidate_data` step 5, which is the boundary that actually has the re-send problem, and the decision block records why it lives there.

I checked the failure edges on the moved skip: a missing candidate yields `None` from the pre-load, so the comparison fails and the call still falls through to core's not-found `ValueError` (400); an empty or unknown `state` string likewise falls through and still returns "Unknown candidate state". The `Delete` button path is unaffected because it calls `delete_candidate` in core directly, so the reap timer still restarts there — only an admin re-sending `DELETED` through the data PUT stops restarting it, which is the more defensible behavior anyway.

**Both discuss items taken.** `IllegalCandidateTransition(ValueError)` carries `from_state` / `to_state`, and step 7 catches the subclass before the bare `ValueError`, which is the required order; that also removes the extra `get_candidate` re-read the old step needed. The forced-apply INFO line resolves cleanly — `src/core/candidate.py:66` already holds `logger = get_logger(__name__)` — and it fires only when the hop would have failed prior-states, so legal hops with the flag set stay silent and history shape is untouched.

## Findings

**discuss — the parent's proposed pattern is still flagged but not drafted.** "Admin confirmed prior-states override" has no `status: proposed` file under `canon/patterns/**`. Carried forward from round 1, unchanged and still non-blocking: the plan implements under the three approved reuse patterns rather than treating an uncatalogued id as law, so this is Archie's corpus call, not Ada's.

**acceptable — the force branch evaluates `_candidate_state_allowed` for the log decision.** Step 4 skips the predicate as a gate when `force=True`, while step 6 evaluates it to decide whether to log. That is intentional rather than contradictory, but it is worth reading twice at build time so the gate does not accidentally get re-armed.

**acceptable — the revision is documented.** The plan carries a `## Revisions` block naming the round-1 concern and each change, so the next reader can see why the same-state skip sits at the API rather than in core.

**acceptable — self-assessment updated honestly.** Scope still `Single-Component` with the added exception type called out, and the `Medium` risk line now names the real new failure mode (a missing API-level skip would spam AST-1288 warnings on every Manage Candidates edit) instead of the retired one.

One completed Plan Discuss round; no round 2 needed. Status → Plan Approved.

context_tokens≈120000

— Joan

#### ada — 2026-08-08T20:32:15.084Z
[plan-discuss] round=1 reply

Revised plan on `origin/sub/AST-1285/AST-1287-admin-confirm-override` @ `0efa41d1`.

**Delta vs round-1 concern:**
1. **fix-now:** Removed the core same-state early-return. `transition_candidate_state` keeps prior_states fail-closed for automation (including `X -> X` when illegal). Same-state skip lives only in `update_candidate_data` before the transition call, so Manage Candidates re-sends of current state do not trigger AST-1288 while AC4 stays intact.
2. **discuss (typed exception):** Added `IllegalCandidateTransition(ValueError)` with `from_state`/`to_state`; API catches by type instead of message-prefix matching.
3. **discuss (force trace):** Forced applies that bypass prior_states emit one INFO line via `src/utils/logging.py`; history shape unchanged.

Plan: https://github.com/susansomerset/astral/blob/sub/AST-1285/AST-1287-admin-confirm-override/docs/features/candidate/ast-1287-admin-confirm-override-for-illegal-candidate-hops.md

Status left at **Plan Discuss** for Joan re-validate.

#### joan — 2026-08-08T20:30:43.497Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1287
**Overall:** REVISE
**Publish ref tip:** `origin/sub/AST-1285/AST-1287-admin-confirm-override` @ `ea91f821`

## Traceability

AC1→S2 (override contract; warning UI is AST-1288); AC2→S1.3–5 + S2.4; AC3→S2.2; AC4→S1.6; AC5→S1.5; AC6→S1.2 + S2.5. Parent AC3 (legal hops stay quiet) is not in the child AC list but is covered by S2.6 + the AST-1288 contract. No orphan stage.

**Considered:** 52 active statutes (18 universal + 34 scoped on layers `core`/`ui`, paths `src/core/candidate.py` + `src/ui/api/api_candidate.py`, change_type `modify`); 12 scoped actives excluded on layer or path. All cited patterns resolve and are `status: approved` — `pattern.state.entity-state-transitions`, `pattern.ui.admin-endpoint`, `pattern.config.config-block` — and the force path matches the state pattern's Solution shape (core still owns the write; data still takes the target as a parameter). One `violates` below; the rest `conforms`.

## Findings

**fix-now — the same-state no-op is placed in core, so it changes behavior for every caller, not just the admin path.** Stage 1 step 3 returns early from `transition_candidate_state` whenever `from_state == to_state`. No candidate state lists itself in `prior_states`, so `X -> X` is an illegal hop today for 17 of the 21 registered states (only `PROSPECT`, `NEW_CANDIDATE`, `INACTIVE`, `DELETED` have `prior_states: None`). Putting the no-op in core therefore makes an illegal hop silently succeed for the automation callers this ticket promised not to touch: consult/dispatch (`src/core/candidate.py:2692`, `:2698`), stale aging (`:1898`), `start_requested_artifacts` (`:1783`), and `delete_candidate` (`:1659`).

That collides with child AC4 / parent AC5 ("automated/dispatch/stale paths still fail closed on illegal hops"), and with the parent boundary that defers graph work — Open question #1 is answered "No", and a blanket same-state pass is a loosening of the `prior_states` graph by another route. Two concrete regressions come with it: re-deleting an already-`DELETED` candidate stops restarting the reap timer (step 3 says explicitly no reap timer), and `start_requested_artifacts` on a candidate already in `REQUESTED_ARTIFACTS` flips from a loud `ValueError` to a silent success that does nothing.

The diagnosis behind the no-op is correct, and worth keeping: `AdminManageCandidates.tsx:207–216` always puts `state` in the `PUT` payload, so today a name-only edit on an `ACTIVE_SEARCH` candidate already fails with `Invalid candidate state transition: ACTIVE_SEARCH -> ACTIVE_SEARCH`. **Recommendation:** fix it at the boundary that has the problem — in `update_candidate_data`, skip the `transition_candidate_state` call when `state_override` equals the candidate's current state — and leave core semantics unchanged for automation. If you want same-state to be globally idempotent, that is a registry decision for Archie and Susan and belongs on the parent, not in this child.

**discuss — the sibling contract keys off an exception message prefix.** Stage 2 step 5 branches on `str(e).startswith("Invalid candidate state transition:")`, which turns core's f-string wording into an API contract that AST-1288's confirm UX depends on; a harmless reword in core silently drops the `illegal_candidate_transition` code and the warning stops appearing. Recommend a small `class IllegalCandidateTransition(ValueError)` raised by the prior-states gate and caught by name in the API. It keeps the DRY property you wanted (no duplicate legality check in the API) and costs about three lines.

**discuss — a forced hop leaves no operator-visible trace that it was forced.** AC6 rightly says forced hops appear in history like any other, and step 5 correctly refuses a new history field. But an admin bypassing the state machine is a security-relevant action with no signal anywhere. A single INFO line via `src/utils/logging.py` at the force branch would satisfy that without touching history shape. Flagging rather than requiring — Susan may prefer the silence.

**discuss — the parent's proposed pattern is flagged but not drafted.** "Admin confirmed prior-states override" has no `status: proposed` file under `canon/patterns/**` and no catalog id. The plan correctly implements under the three approved reuse patterns instead of treating it as law, so this is a corpus gap rather than a plan defect (plan-rubric R6).

**acceptable — plan assumptions verified against the tree.** The existing `transition_candidate_state` check order (not-found, unknown state, then prior-states) is as the plan describes, every current call site passes two positional arguments so a keyword-only `force` breaks nothing, and `update_candidate_data` already pops `state` and `api_key` and imports `get_candidate` for the re-read in step 5. No drift.

**acceptable — cancel semantics match the parent's answered question.** Saving non-state fields first and returning 400 for the unconfirmed hop implements Open question #3 ("skip only the state change"), and the plan documents the partial-save consequence in the AST-1288 contract rather than hiding it.

**acceptable — self-assessment is honest.** `Single-Component` matches two files, `high` conf is earned by reusing the AST-970 path, and `Medium` risk names the right failure modes (default-force, non-admin confirm, error-shape drift).

Status moves to Plan Discuss for round 1. Only the first finding blocks.

context_tokens≈95000

— Joan

#### ada — 2026-08-08T20:26:12.169Z
Plan published on `origin/sub/AST-1285/AST-1287-admin-confirm-override` @ `ea91f821`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1285/AST-1287-admin-confirm-override/docs/features/candidate/ast-1287-admin-confirm-override-for-illegal-candidate-hops.md

**Approach:** keyword-only `force` on `transition_candidate_state` (default false); admin `PUT …/data` accepts `confirm_state_override: true`; illegal hops without confirm return `code: "illegal_candidate_transition"` + `from_state`/`to_state` for AST-1288; same-state is a silent no-op so Manage Candidates re-sends of current state do not look illegal; unknown states stay rejected even with force; dispatch/stale callers unchanged.

**Self-assessment**
- **Scope:** Single-Component — core transition + existing admin candidate-data PUT only.
- **Conf:** high — reuses AST-970 transition path; force defaults false so automation stays fail-closed.
- **Risk:** Medium — mistaken default-force or non-admin confirm would loosen auth/automation; bad error shape would break sibling confirm UX.

---

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

## Resolution

**Date:** 2026-08-08  
**Review:** Radia `[code-rubric] revision=2` — Overall DISCUSS; no fix-now.

| Finding | Action |
|---------|--------|
| discuss — C4 stragglers (job-prior-states, claim-process-release, ui-config-driven) | No product change — Radia scored each `conforms` on inspection |
| advisory — `IllegalCandidateTransition` import order in `api_candidate.py` | Alphabetized in the `src.core.candidate` import block |

No test-tree changes. Ready for User Testing.
