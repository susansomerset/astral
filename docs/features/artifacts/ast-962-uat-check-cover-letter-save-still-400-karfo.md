<!-- linear-archive: AST-962 archived 2026-08-02 -->

## Linear archive (AST-962)

**Archived:** 2026-08-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-962/uat-check-cover-letter-save-still-400-karfo  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-856 — check_cover_letter not recognized as a valid task_key  
**Blocked by / blocks / related:** parent: AST-856

### Description

## What failed

On staging after the first ship, saving a Scheduled Action with `task_key=check_cover_letter` still returns HTTP 400:

```
Astral error diagnostic
timestamp: 2026-07-23T18:10:33.974Z
message: Unknown or non-schedulable task_key: 'check_cover_letter'
route: /admin/scheduled_actions
astral_candidate_id: karfo
api_path: /api/admin/dispatch_tasks
http_method: POST
http_status: 400
response_body:
{
  "error": "Unknown or non-schedulable task_key: 'check_cover_letter'"
}
```

Susan reports the original issue is still occurring (candidate `karfo`).

## Expected

`POST /api/admin/dispatch_tasks` accepts `check_cover_letter` for any candidate (including `karfo`) without *Unknown or non-schedulable task_key* — same as any other registered task key visible in the picker. Misapplied trigger/entity should fail at first Run, not at Save for allowlist membership.

## Repro

1. Open `/admin/scheduled_actions` for candidate `karfo` (or any candidate).
2. Add/Save a dispatch row with `task_key=check_cover_letter` and a valid job trigger state from the form.
3. Observe HTTP 400 with `Unknown or non-schedulable task_key: 'check_cover_letter'`.

## Parent AC (quoted inline)

> 1. Susan can create a Scheduled Action dispatch row with `task_key=check_cover_letter` for candidate `somerset` without HTTP 400 — the error from the original brief no longer occurs.
> 2. Any other registered task key visible in the picker can be saved the same way (no *Unknown or non-schedulable task_key* for registered task keys).
> 3. A deliberately misconfigured row (wrong trigger state for the chosen task_key) is rejected or fails at **run** time, not at Save time — observable on first Run, not blocked at Save for merely being outside a separate schedulable allowlist.

## Boundaries

* This bug does **not** change: Manage Tasks / run_next authoring, dispatcher claim logic, Execution History UX, or chain choreography.
* May still block explicitly retired dispatch keys.

### Comments

#### radia — 2026-07-23T18:21:21.613Z
**Radia review — clean**

Diff: `origin/dev...origin/sub/AST-856/AST-962-uat-check-cover-letter-save-still-400-karfo` @ `028d7e9`

**Plan fidelity:** Stage 1 exact — mid-chain cover-letter hops default to `CANDIDATE_REVIEW` beside `draft_cover_letter`. No Save membership rework; `non-schedulable` still absent from `src/`.

**Rules:** §1.3 / §2.1 — one config helper branch. §2.4 / §2.6 / §5f / §5g N/A.

**fix-now / discuss:** none.

Review doc: https://github.com/susansomerset/astral/blob/028d7e96f4f60a526e0a345593c446bb134c40dc/docs/features/artifacts/ast-962-uat-check-cover-letter-save-still-400-karfo.md

#### betty — 2026-07-23T18:19:43.395Z
1. `./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst962CoverLetterMidHopDefaultTrigger \
  tests/component/utils/test_config.py::TestAst955RegisteredKeyDispatchAdminDefaults \
  tests/component/data/database/test_dispatch_tasks.py::TestAst962SaveDispatchTaskCoverLetterDefaults \
  -q`

2. **Broken / obsolete revised this pass:** `TestAst955RegisteredKeyDispatchAdminDefaults::test_check_cover_letter_without_override_raises_no_rule` → now defaults to `CANDIDATE_REVIEW` (no KeyError).

3. **Coverage:** mid-hop keys (`check_cover_letter` / `finalize_cover_letter` / `propose_application_responses`) default trigger + admin defaults without override; DB insert for `karfo` omits trigger and fills `CANDIDATE_REVIEW`; draft/grade_do regressions.

**Publish:** `origin/sub/AST-856/AST-962-uat-check-cover-letter-save-still-400-karfo` @ `db8cfcd` (`merge-tests(AST-962): origin/tests d32e2a6`)

**Bible shasum (publish tip):**
- `docs/test-bible/utils/config.md` `d2d70543b3b815a8eef4241ce75c55dde3bbf87d`
- `docs/test-bible/ui/api/api_admin.md` `c84ae63751efffe4551ec8ed77b4e2f74ee45aa9`
- `docs/test-bible/data/database/dispatch_tasks.md` `40b9c1f8e7cd36d0eeec2771113c94bc70b5d11d`

— Betty

#### ada — 2026-07-23T18:15:45.271Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-856/AST-962-uat-check-cover-letter-save-still-400-karfo/docs/features/artifacts/ast-962-uat-check-cover-letter-save-still-400-karfo.md

**Scope:** Single-Component — default `_dispatch_trigger_state_for_task_key` for `check_cover_letter` / `finalize_cover_letter` / `propose_application_responses` → `CANDIDATE_REVIEW` so form meta + defaults resolve without override. AST-955 membership already on tip; quoted `non-schedulable` string absent from `origin/dev` `src/`.

**Conf:** Medium — tip cannot emit the diagnostic wording (AST-955); verified empty default-trigger gap still blocks one-click Save; staging may also have been stale.

**Risk:** low — three registered job keys get the same default Input State as `draft_cover_letter`; Save membership / dispatcher untouched.

---

# AST-962 — UAT: check_cover_letter Save still 400 (karfo)

- **Linear:** [AST-962](https://linear.app/astralcareermatch/issue/AST-962/uat-check-cover-letter-save-still-400-karfo)
- **Parent:** [AST-856](https://linear.app/astralcareermatch/issue/AST-856/check-cover-letter-not-recognized-as-a-valid-task-key)
- **Publish ref:** `origin/sub/AST-856/AST-962-uat-check-cover-letter-save-still-400-karfo`
- **UAT bug of:** AST-856 / first ship child **AST-955** — Susan staging re-test (`karfo`) still got HTTP 400

On staging after AST-955, Save with `task_key=check_cover_letter` for candidate `karfo` still returned `Unknown or non-schedulable task_key: 'check_cover_letter'`. Tip investigation: that exact error string is **gone** from `origin/dev` `src/` (AST-955 replaced it with `Unknown task_key`); Save membership is already `TASK_CONFIG`. Residual product gap: mid-chain cover-letter keys have `TASK_CONFIG.trigger_state: None` and **no** `_dispatch_trigger_state_for_task_key` rule, so Scheduled Actions form leaves Input State blank and `dispatch_task_admin_defaults("check_cover_letter")` (no override) still KeyErrors — Save only works when Susan manually picks a job state. This UAT plan hardens form/default trigger for those keys so Save succeeds with picker defaults for `karfo` (and any candidate), without reintroducing a schedulable allowlist.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Default trigger for cover-letter mid-chain keys in `_dispatch_trigger_state_for_task_key` | utils |

**Out of scope:** Manage Tasks / `run_next`, dispatcher claim, Execution History, frontend redesign, re-adding `DISPATCH_SCHEDULABLE_TASK_KEYS` as a Save gate, `tests/` / bible (Betty).

## Diagnosis (this branch tip)

1. `_dispatch_task_key_trigger_error` on tip returns `Unknown task_key` for unregistered keys — **not** `Unknown or non-schedulable` (AST-955). Grep of `origin/dev` `src/` finds **no** `non-schedulable` string.
2. `check_cover_letter` ∈ `TASK_CONFIG` with `entity_type=job`, `trigger_state=None`. `_dispatch_trigger_state_for_task_key("check_cover_letter")` raises `no rule for task_key`.
3. `_dispatch_task_key_form_meta` tries `dispatch_task_admin_defaults(task_key)` then `except KeyError: pass` — picker entry keeps empty `trigger_state`. Frontend Save POSTs `form.trigger_state` (often `""`) → API `trigger_state is required` **or** staging still running pre-AST-955 if deploy lagged (matches quoted diagnostic wording).
4. With explicit `trigger_state="CANDIDATE_REVIEW"`, tip defaults + membership already accept `check_cover_letter`.

⚠️ **Decision:** Do **not** treat this as “re-implement AST-955 membership.” Membership is already fixed on tip. Close the UAT gap by giving cover-letter mid-chain keys the same default Input State as `draft_cover_letter` (`CANDIDATE_REVIEW`) so form meta + `save_dispatch_task` without override succeed. If staging still served the old **non-schedulable** string, Chuckles **prep-uat** after this child reaches User Testing refreshes Railway from `origin/dev`.

## Stage 1: Default trigger for cover-letter mid-chain keys

**Done when:** `_dispatch_trigger_state_for_task_key("check_cover_letter") == "CANDIDATE_REVIEW"`; same for `finalize_cover_letter` and `propose_application_responses`. `dispatch_task_admin_defaults("check_cover_letter")` (no override) returns `entity_type=job`, `trigger_state=CANDIDATE_REVIEW`, non-empty `sort_by`, `batch_call_mode=0`. `draft_cover_letter` and `grade_do` defaults unchanged. `_dispatch_task_key_form_meta` / `GET …/task_keys` entry for `check_cover_letter` exposes non-empty `trigger_state` (via existing prefer-defaults path).

1. In `src/utils/config.py` `_dispatch_trigger_state_for_task_key`, immediately after the existing `draft_cover_letter` → `CANDIDATE_REVIEW` branch, add:

```python
if task_key in ("check_cover_letter", "finalize_cover_letter", "propose_application_responses"):
    return "CANDIDATE_REVIEW"
```

⚠️ **Decision:** Reuse `CANDIDATE_REVIEW` (same as `draft_cover_letter`) rather than `BUILD_ARTIFACTS` — cover-letter chain entry already schedules at candidate-review; mid-chain Save from Scheduled Actions should share that Input State. Do **not** add these keys to any schedulable frozenset (AST-960 deleted that inventory; AST-955 forbade dual allowlists).

2. Do **not** change `_dispatch_task_key_trigger_error`, `save_dispatch_task`, or frontend — form meta already prefers `dispatch_task_admin_defaults` when it resolves.

## Stage 2: Tip smoke (engineer, before Code Complete)

**Done when:** Against this worktree tip, Save acceptance for `check_cover_letter` no longer depends on a hand-picked Input State, and the old diagnostic string cannot be produced by the API helper.

1. Confirm `rg -n 'non-schedulable' src/` is empty on the tip after Stage 1.
2. In a Python REPL with the project venv:

```python
from src.utils.config import dispatch_task_admin_defaults, _dispatch_trigger_state_for_task_key
assert _dispatch_trigger_state_for_task_key("check_cover_letter") == "CANDIDATE_REVIEW"
d = dispatch_task_admin_defaults("check_cover_letter")
assert d["entity_type"] == "job" and d["trigger_state"] == "CANDIDATE_REVIEW"
```

3. Optional Flask/admin smoke (if local `launch.sh` up): `POST /api/admin/dispatch_tasks` with `candidate_id=karfo`, `task_key=check_cover_letter`, `trigger_state=CANDIDATE_REVIEW`, `min_count=1` → **201** (or 409 if row already exists — not 400 with non-schedulable / unknown).

**Betty note:** Extend AST-955 coverage for default-trigger-without-override on `check_cover_letter`; do not edit `tests/` here.

## Execution contract

- Stages in order; one `code(AST-962):` commit per product stage on the epic sub-branch; push to `origin/sub/AST-856/AST-962-uat-check-cover-letter-save-still-400-karfo`.
- Plan commit subject must start with **`plan(AST-962):`** (validate-sub-log vocabulary — not `docs(AST-962): plan`).
- No files outside the Files Changed table.
- Ambiguity / drift → stop, comment on parent AST-856 with blocking template.

## Self-Assessment

**Scope:** Single-Component — one `_dispatch_trigger_state_for_task_key` branch in `config.py` so form/defaults resolve for cover-letter mid-hops.

**Conf:** Medium — tip already lacks the quoted error string (AST-955); UAT may partly be stale staging, but empty default trigger is a verified tip gap that blocks one-click Save.

**Risk:** low — only default Input State for three registered job keys; claim/run behavior unchanged; retired-key and unknown-key Save paths untouched.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|--------|
| §1.3 DRY | Single helper branch next to existing `draft_cover_letter` rule — no parallel allowlist |
| §2.1 config | Trigger default lives in `config.py` |
| §2.4 / §2.6 | Untouched |
| §3.3 | Utils only |

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-856/AST-962-uat-check-cover-letter-save-still-400-karfo`  
**Tip:** `b3b016a`

**Stages delivered:**
- Stage 1 — `_dispatch_trigger_state_for_task_key` defaults `check_cover_letter` / `finalize_cover_letter` / `propose_application_responses` → `CANDIDATE_REVIEW`
- Stage 2 — tip smoke: defaults without override; `non-schedulable` absent from `src/`

**Betty:** default-trigger-without-override coverage for `check_cover_letter`.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-856/AST-962-uat-check-cover-letter-save-still-400-karfo` @ `db8cfcd`

### What's solid

| Area | Notes |
| --- | --- |
| Plan fidelity | Stage 1 exact: after `draft_cover_letter`, mid-hops `check_cover_letter` / `finalize_cover_letter` / `propose_application_responses` → `CANDIDATE_REVIEW`. No Save membership rework, no schedulable frozenset, no API/frontend churn. |
| UAT diagnosis | Tip already lacks `non-schedulable` in `src/`; residual gap was empty default trigger so form meta KeyError-swallowed blank Input State. Defaults-without-override now resolve; `_dispatch_task_key_form_meta` prefers `dispatch_task_admin_defaults` for `TASK_CONFIG` keys. |
| Scope / Self-Assessment | Single-Component utils branch; Conf Medium / Risk low match the three-line footprint. |
| Rules | §1.3 DRY / §2.1 config — one helper branch beside draft. §2.4 / §2.6 / §5f / §5g N/A. |
| Tests (Betty) | AST-955 override test flipped + AST-962 mid-hop class — out of Radia edit scope. |

### Issues

None (**fix-now** / **discuss**).

### Recommended actions

| Severity | Item |
| --- | --- |
| — | None. |

**Verdict:** Clean — `resolve-child` may proceed (no product fixes required beyond this `docs()` commit).

## Resolution (2026-07-23, resolve-child)

**Radia:** clean — **fix-now** / **discuss** none (`docs(AST-962): Radia review — clean` @ `028d7e9`).

**Product:** no code changes this pass. Stage 1 mid-hop `CANDIDATE_REVIEW` defaults from build remain the ship; Betty `merge-tests` @ `db8cfcd` unchanged.

**Outcome:** `resolve(AST-962): — clean` → **User Testing** (assignee Ada).
