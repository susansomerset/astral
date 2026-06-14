# Dispatch claim without score_floor on VALID_TITLE (Rebuild 586 — AST-617)

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-617/dispatch-claim-without-score-floor-on-valid-title-rebuild-586-git  
**Parent:** https://linear.app/astralcareermatch/issue/AST-600/rebuild-586-git-casualty  

**Publish ref (origin):** `sub/AST-600/AST-617-qualify-no-score-floor-valid-title-rebuild-586`  
**Parent integration ref:** `ftr/AST-600-rebuild-586-git-casualty`  

Restore the **AST-586** dispatch fix lost in git merges: separate **dispatch claim score-floor gating** from **task grading metadata** so **qualify_job_listings** on trigger **VALID_TITLE** claims jobs without **latest_score**, while post-score outcome triggers (**PASSED_JD**, **PASSED_DO**, **PASSED_GET**, **PASSED_LIKE**, etc.) still honor **score_floor**. Align Scheduled Actions admin rows and eligible-job counts with the same claim rules.

**Verified (plan time):** `dispatch_claim_uses_score_floor` and `dispatcher._trigger_state_scored` already use the claim helper on this branch. **Git casualty sites** still call `trigger_state_used_by_scored_dispatch_task` for claim/floor semantics in `src/data/database.py` (`count_eligible_for_dispatch_task`, schema backfill) and `src/ui/api/api_admin.py` (`_trigger_state_is_scored`, list/create/update, `dispatch_task_keys` fallback). Component tests from AST-586 already exist on the branch; Betty re-runs them at Code Complete.

**Reference plan:** `docs/features/interface/ast-586-qualify-no-score-floor-valid-title.md`

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | **Verify only** — `dispatch_claim_uses_score_floor` present; no edit unless missing | utils |
| `src/core/dispatcher.py` | **Verify only** — `_trigger_state_scored` delegates to claim helper; no edit unless regressed | core |
| `src/data/database.py` | `count_eligible_for_dispatch_task` + dispatch_task schema backfill use `dispatch_claim_uses_score_floor` | data |
| `src/ui/api/api_admin.py` | List/create/update dispatch rows + helpers: `is_scored` / `score_floor` / `available_count` align with claim helper | ui |

**Not in scope:** `score_floor_by_trigger_for_candidate` in `database.py` (iterates only `PASSED_SCORE_GATED_STATES` per AST-586), `src/core/consult.py`, `api_jobs.py`, React `AdminScheduledActions.tsx`.

**Tests (Betty at Code Complete — engineer does not edit `tests/` in build):** existing AST-586 manifest in `tests/component/utils/test_config.py`, `tests/component/core/test_dispatcher.py`, `tests/component/ui/api/test_api_admin.py`.

---

## Stage 1: Restore database and admin API claim-floor call sites

**Done when:** `dispatch_claim_uses_score_floor("VALID_TITLE")` is **False** and `dispatch_claim_uses_score_floor("PASSED_JD")` is **True** (config unchanged); `_run_unified` for `qualify_job_listings` + **VALID_TITLE** passes `score_floor=None` into claim (dispatcher unchanged); `count_eligible_for_dispatch_task` and admin list row for **VALID_TITLE** use claim helper (`is_scored=False`, `score_floor=None`); `python3 -m py_compile` passes on touched `.py` files.

1. **Verify** in `src/utils/config.py` (~1174): `dispatch_claim_uses_score_floor` exists with body matching AST-586 Stage 1 step 1 (membership in `PASSED_SCORE_GATED_STATES` + `_TRANSITION_STATES_USED_BY_SCORED_TASKS`; **VALID_TITLE** returns **False**). If missing or wrong, add/fix per AST-586 reference — otherwise **no edit**.

2. **Verify** in `src/core/dispatcher.py` (~61): `_trigger_state_scored` returns `dispatch_claim_uses_score_floor(trigger_state)`. If it still calls `trigger_state_used_by_scored_dispatch_task`, replace per AST-586 — otherwise **no edit**.

3. In `src/data/database.py`:
   - In the config import block (~76), add `dispatch_claim_uses_score_floor` to the import from `src.utils.config`. Keep `trigger_state_used_by_scored_dispatch_task` in the import if still used elsewhere (e.g. `score_floor_by_trigger_for_candidate` ~1554).
   - In `count_eligible_for_dispatch_task` (~5201), replace:
     ```python
     is_scored = trigger_state_used_by_scored_dispatch_task(state)
     ```
     with:
     ```python
     is_scored = dispatch_claim_uses_score_floor(state)
     ```
     Leave the following `floor = ...` line unchanged.
   - In dispatch_task schema backfill (~4890), replace:
     ```python
     if trigger_state_used_by_scored_dispatch_task(trigger_state):
     ```
     with:
     ```python
     if dispatch_claim_uses_score_floor(trigger_state):
     ```
   - **Do not** change `score_floor_by_trigger_for_candidate` (~1554) — it already gates on `PASSED_SCORE_GATED_STATES` only.

4. In `src/ui/api/api_admin.py`:
   - Add `dispatch_claim_uses_score_floor` to the `src.utils.config` import block (~40–57). Keep `trigger_state_used_by_scored_dispatch_task` only if still referenced elsewhere in this file after edits (likely removable if unused).
   - Replace `_trigger_state_is_scored` body (~532):
     ```python
     return dispatch_claim_uses_score_floor(trigger_state)
     ```
   - In `list_dtasks` (~560), replace `trigger_state_used_by_scored_dispatch_task(row.get("trigger_state"))` with `dispatch_claim_uses_score_floor(row.get("trigger_state"))` for the `is_scored` assignment.
   - In `dispatch_task_keys` (~618), replace the fallback `"is_scored": trigger_state_used_by_scored_dispatch_task(r.get("trigger_state"))` with `dispatch_claim_uses_score_floor(r.get("trigger_state"))`. Leave `_dispatch_task_key_form_meta` using `dispatch_task_key_is_scored(task_key)` unchanged.
   - In `create_dtask` (~640), replace `trigger_state_used_by_scored_dispatch_task(data.get("trigger_state"))` with `dispatch_claim_uses_score_floor(data.get("trigger_state"))` for `is_scored`.
   - In `update_dtask` (~677), replace `trigger_state_used_by_scored_dispatch_task(trigger_state)` with `dispatch_claim_uses_score_floor(trigger_state)` for `is_scored`.
   - Remove unused `trigger_state_used_by_scored_dispatch_task` import if no remaining references in this file.

5. Run:

   ```bash
   python3 -m py_compile src/utils/config.py src/core/dispatcher.py src/data/database.py src/ui/api/api_admin.py
   ```

⚠️ **Decision:** Claim gating uses **outcome / post-score states** (`PASSED_SCORE_GATED_STATES` + `_TRANSITION_STATES_USED_BY_SCORED_TASKS`), not schedulable **input** triggers (`VALID_TITLE`, `JD_READY`). Same semantics as shipped AST-586; this ticket restores call sites lost in merge, not redesign.

---

## Stage 2: Betty manifest (Code Complete — not engineer build)

**Done when:** Betty posts manifest confirmation; `test-astral` green on publish ref.

Engineer Linear comment at **Code Complete** (build stage end): **no new test files required** — AST-586 component tests already on branch. Betty verifies:

1. **`tests/component/utils/test_config.py`** — `TestDispatchClaimUsesScoreFloor` (or equivalent): `VALID_TITLE` → **False**; `PASSED_JD` / `PASSED_JOBLIST` → **True**; RETRY / None → **False**.
2. **`tests/component/core/test_dispatcher.py`** — `test_qualify_valid_title_claim_without_score_floor`: mock claim receives `score_floor=None`.
3. **`tests/component/ui/api/test_api_admin.py`** — list/create/helper: **VALID_TITLE** row `is_scored=False`, `score_floor=None`; **PASSED_JOBLIST** / **PASSED_JD** still scored with default floor **1.0** when NULL.

If any test fails after Stage 1, fix product code only (not tests) unless manifest is wrong → `[qa-handoff]` to Betty.

---

## Self-Assessment

**Scope:** `Single-Component` — Two files edited (database count/backfill, admin API); config and dispatcher verified only; no consult or UI component edits.

**Conf:** `high` — AST-586 was shipped and reviewed; root cause and helper semantics unchanged; plan-time grep confirms exact lines to swap.

**Risk:** `Medium` — Wrong helper at count/admin paths would show incorrect `available_count` or persist wrong `score_floor` defaults while dispatcher claim might already be correct; mitigated by reusing AST-586 helper membership and existing component tests.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses existing `dispatch_claim_uses_score_floor`; no duplicate state lists. |
| §2.1 config | Claim helper in `config.py`; `score_floor` vs `pass_threshold` separation unchanged. |
| §2.4 batch | Claim/count still use `score_floor` param; only when to pass non-`None` changes at count/admin layers. |
| §2.6 state machine | No transition changes; claim filter and admin presentation only. |
| §3.3 imports | data/ui import utils helper (allowed). |
| §3.5 naming | Matches existing `dispatch_*` / `trigger_state_*` naming from AST-586. |

No conflicts requiring `conf-!!-NONE`.

---

## Review (build)

**Branch:** `origin/sub/AST-600/AST-617-qualify-no-score-floor-valid-title-rebuild-586`  
**Tip:** `6e5f2e17`  
**Built:** Stage 1 — `database.py` count/backfill and `api_admin.py` list/create/update use `dispatch_claim_uses_score_floor`; config + dispatcher verified unchanged. Stage 2 component tests deferred to Betty per build-child test-tree ban.

**Betty manifest (Code Complete):**

1. `tests/component/utils/test_config.py` — `dispatch_claim_uses_score_floor` cases (VALID_TITLE False, PASSED_JD/PASSED_JOBLIST True, RETRY/None False).
2. `tests/component/core/test_dispatcher.py` — `test_qualify_valid_title_claim_without_score_floor` asserts `score_floor=None` on claim.
3. `tests/component/ui/api/test_api_admin.py` — list/create/helper tests for VALID_TITLE `is_scored=False`, `score_floor=None`; PASSED_JD/PASSED_JOBLIST still scored.
