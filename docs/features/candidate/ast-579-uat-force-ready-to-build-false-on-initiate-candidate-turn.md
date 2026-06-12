# AST-579 — UAT: Force ready_to_build false on initiate_candidate turn

**Linear:** https://linear.app/astralcareermatch/issue/AST-579/uat-force-ready-to-build-false-on-initiate-candidate-turn  
**Parent:** https://linear.app/astralcareermatch/issue/AST-539/candidate-intake-chat-session  
**Publish ref:** `sub/AST-539/AST-579-uat-force-ready-to-build-false-on-initiate-candidate-turn` (origin only)

## Summary

UAT bug: after opening Intake, **Generate Profile** can enable immediately because the model sometimes returns `ready_to_build: true` on the first (`initiate_candidate`) turn despite prompt instructions. Product rule (parent **AST-539** AC #2): **Generate Profile** must stay disabled until a later interview turn signals readiness — never on turn 1. Force `last_ready_to_build=False` in `create_intake_session_and_start` regardless of model JSON.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/intake.py` | Force `ready_to_build=False` on initiate turn persistence and DTO | core |
| `tests/component/core/test_intake.py` | Assert initiate turn ignores model `ready_to_build: true` | tests |

---

## Stage 1: Backend gate on initiate turn

**Done when:** `create_intake_session_and_start` always persists and returns `ready_to_build: false` / `can_build: false` even when `intake_initiate_candidate` model JSON has `ready_to_build: true`; assistant transcript entry on turn 1 also stores `ready_to_build: false`.

1. In `src/core/intake.py`, inside `create_intake_session_and_start`, immediately after line `turn = _validate_interview_turn(run["parsed_response"])`, add:
   ```python
   initiate_ready = False  # product rule: never ready on first turn (AST-539 AC #2)
   ```
2. In the same function, change the assistant `_append_transcript` call (currently passes `ready_to_build=turn["ready_to_build"]`) to pass `ready_to_build=initiate_ready` instead.
3. In the same function, change `database.update_intake_session(..., last_ready_to_build=turn["ready_to_build"], ...)` to `last_ready_to_build=initiate_ready`.
4. Do **not** change `_validate_interview_turn`, `post_intake_turn`, or `get_intake_session_dto` — follow-up turns must still propagate model `ready_to_build` normally.

⚠️ **Decision:** Clamp at persistence/DTO layer in `create_intake_session_and_start` rather than rewriting model JSON before validation. Keeps validation honest (model may still return `true`) while enforcing product gate in one place.

---

## Stage 2: Component test

**Done when:** `pytest tests/component/core/test_intake.py` passes and new test fails on current code, passes after Stage 1.

1. In `tests/component/core/test_intake.py`, inside `TestIntakeSessionFlow`, add `test_initiate_turn_forces_ready_to_build_false_when_model_returns_true`.
2. In that test, monkeypatch `intake_mod.do_task` (do not use `mock_do_task` fixture — it always returns `ready=False`) to return for `task_key == "intake_initiate_candidate"`:
   ```python
   {"success": True, "parsed_response": _interview_turn(ready=True, message="Ready already")}
   ```
3. Monkeypatch `get_agent_data_by_batch` → `[]`, `compute_batch_cost` → `0.0`, `save_candidate_data` → `MagicMock()` (same as sibling tests in this class).
4. Call `await intake_mod.create_intake_session_and_start("cand-1", "Resume text")`.
5. Assert `dto["ready_to_build"] is False` and `dto["can_build"] is False`.
6. Assert `dto["transcript"][-1]["ready_to_build"] is False` (assistant entry).
7. Load session row via `database.get_intake_session(dto["session_id"])` and assert `row["last_ready_to_build"] is False` (import `database` from `src.data` if not already imported in test file).

---

## Self-Assessment

**Scope:** `minor` — One function in `src/core/intake.py` plus one focused test; no API or UI changes.

**Conf:** `high` — Exact repro and fix location are specified in the ticket; pattern matches existing initiate persistence in the same function.

**Risk:** `low` — Only the first-turn readiness gate changes; `post_intake_turn` and build flow are untouched.

---

## ASTRAL_CODE_RULES self-review

| Rule | Assessment |
|------|------------|
| §1.3 DRY | No duplicate logic; single `initiate_ready` constant in one function. |
| §2.1 config | No new config; uses existing `INTAKE_CONFIG` session status only. |
| §2.4 batch | N/A — no batch changes. |
| §2.6 state machine | N/A — candidate state machine unchanged; intake session flags only. |
| §3.3 imports | No new imports expected. |
| §3.5 naming | Follows existing `last_ready_to_build` / `ready_to_build` naming. |

No conflicts — safe to implement as written.

---

## Review (build)

**Branch:** `origin/sub/AST-539/AST-579-uat-force-ready-to-build-false-on-initiate-candidate-turn`  
**Tip:** `21e780b0`  
**Built:** Stage 1 only — `initiate_ready = False` clamp in `create_intake_session_and_start` (transcript + `last_ready_to_build` + DTO). Stage 2 component test deferred to Betty per build-astral test-tree ban.

---

## Review

**Diff:** `origin/dev...origin/sub/AST-539/AST-579-uat-force-ready-to-build-false-on-initiate-candidate-turn` (publish tip `818a22bf`). AST-579 product scope: `f077308c` (`src/core/intake.py`), `7cefff08` (`tests/component/core/test_intake.py`).

### What's solid

- Plan fidelity: `initiate_ready = False` clamp applied at persistence/DTO layer exactly as Stage 1 specifies; `_validate_interview_turn`, `post_intake_turn`, and `get_intake_session_dto` untouched.
- Product rule enforced end-to-end on turn 1: assistant transcript row, `last_ready_to_build`, and DTO `ready_to_build` / `can_build` (via `get_intake_session_dto` reading `last_ready_to_build`) all stay false when model JSON says true.
- Component test matches Stage 2 checklist and pairs with `test_turn_appends_transcript_and_propagates_ready_to_build` — follow-up turns still honor model `ready_to_build`.
- **ASTRAL_CODE_RULES:** §1.3 DRY (single constant), §2.1 config (no new literals), §3.3 imports (none added), §3.5 naming — no layer, logging, or silent-failure concerns in the touched lines.

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| — | — | None |

### Recommended actions

| Action | Owner | Notes |
|--------|-------|-------|
| Proceed to `resolve-astral` | — | No fix-now or discuss items; happy path. |

---

## Resolution (2026-06-05)

**Review:** Radia @ `b20a19c2` — no fix-now, no discuss; product + test already match plan.

**Changes:** None — happy path. Plan doc only (this section).

**Verify:** Betty bible reconcile @ `b17f739a` (§7.13zq AST-550 + §7.13zr AST-578/579). Manifest green on `dev-ada` after merge (`test_initiate_turn_forces_ready_to_build_false_when_model_returns_true` + full `test_intake.py` — 10 passed). §9a dry-run clean vs `origin/dev` and `origin/ftr/ast-539-candidate-intake-chat-session`.
