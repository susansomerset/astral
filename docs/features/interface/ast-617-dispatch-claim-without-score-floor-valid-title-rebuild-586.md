<!-- linear-archive: AST-617 archived 2026-06-23 -->

## Linear archive (AST-617)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-617/dispatch-claim-without-score-floor-on-valid-title-rebuild-586-git  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-600 — Rebuild 586 (git casualty)  
**Blocked by / blocks / related:** parent: AST-600

### Description

## What this implements

Restore the **AST-586** dispatch fix lost in git merges: separate **dispatch claim score-floor gating** from **task grading metadata** so **qualify_job_listings** on trigger **VALID_TITLE** claims jobs without **latest_score**, while post-score outcome triggers (**PASSED_JD**, **PASSED_DO**, **PASSED_GET**, **PASSED_LIKE**, etc.) still honor **score_floor**. Align Scheduled Actions admin rows and eligible-job counts with the same claim rules.

Partial restoration may exist on **dev** (config helper + dispatcher claim path); **database** count/backfill and **admin API** paths must match.

## Acceptance criteria

1. With a dispatch task configured for **qualify_job_listings** + trigger **VALID_TITLE**, running dispatch claims at least one eligible **VALID_TITLE** job that has no **latest_score**.
2. The same configuration does not claim zero jobs solely because **latest_score** is null when jobs are otherwise eligible at **VALID_TITLE**.
3. Dispatch on **PASSED_JD** (and other post-score outcome triggers) still applies **score_floor** — jobs below floor are not claimed.
4. Scheduled Actions list shows **VALID_TITLE** / **qualify_job_listings** rows as not score-gated for claim; post-score rows still show scored/floor semantics consistent with claim behavior.
5. Component tests covering the AST-586 claim-floor contract pass on the merged branch.

## Boundaries

* Does not change **jd_score** persistence or Recommended list rendering ([AST-560](https://linear.app/astralcareermatch/issue/AST-560)).
* Does not alter **pass_threshold** grading math, consult verdict logic, or job state transitions.
* Does not change React UI beyond what the admin API returns for dispatch task metadata.

## Notes for planning

Reference: `docs/features/interface/ast-586-qualify-no-score-floor-valid-title.md` (approved plan from original ship). Verify all four call-site layers (config helper, dispatcher, database count/backfill, admin API) before claiming done — **dev** may only have partial restoration.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/AST-600-rebuild-586-git-casualty`, child `sub/AST-600/<child-segment>`. Created at **dispatch-parent**.

### Comments

#### radia — 2026-06-14T04:08:00.875Z
**Diff:** `origin/dev...origin/sub/AST-600/AST-617-qualify-no-score-floor-valid-title-rebuild-586` @ `682474fd`  
**Plan doc:** [ast-617-dispatch-claim-without-score-floor-valid-title-rebuild-586.md](https://github.com/susansomerset/astral/blob/sub/AST-600/AST-617-qualify-no-score-floor-valid-title-rebuild-586/docs/features/interface/ast-617-dispatch-claim-without-score-floor-valid-title-rebuild-586.md) — § Review (Radia)

### fix-now

- **Sibling scope bleed (§5d / plan boundaries):** Publish ref includes **AST-601 AST-616** commits (`842b6dda`–`ef194b22`, merge at `ef194b22`) — `src/ui/api/api_candidate.py` (`GET /api/candidates/<id>/resume_structure`), `ArtifactsBaseResumeContent.tsx`, `docs/features/interface/ast-616-*.md`. AST-617 plan scopes **only** `database.py` count/backfill + `api_admin.py`; React/candidate API are out of scope. **Re-publish** `sub/AST-600/AST-617-*` without AST-616 commits before ftr merge (keep `6e5f2e17` + AST-617 plan/test merges).

### discuss

- **`ef194b22` intent:** Was merging `origin/sub/AST-601/AST-616-*` required for the test harness, or accidental during `merge-tests`? If intentional, confirm how AST-616 tracks to Done without this ticket absorbing AST-601 ship scope.

### advisory (AST-617 product — clean)

- **`database.py`:** `count_eligible_for_dispatch_task` + `_ensure_dispatch_task_schema` backfill now use `dispatch_claim_uses_score_floor`; `score_floor_by_trigger_for_candidate` (~1555) still uses `trigger_state_used_by_scored_dispatch_task` inside `PASSED_SCORE_GATED_STATES` loop — matches plan.
- **`api_admin.py`:** All five `is_scored` / floor call sites use claim helper; grading import removed from this file.
- **Config + dispatcher:** Already on `origin/dev` (no diff) — claim path aligned with AST-586/615.
- **Rules:** §2.1 claim vs grading split intact; §3.3 layer imports OK; no batch/state-machine changes.

#### betty — 2026-06-14T04:04:53.827Z
## QA test manifest

**Coverage class:** bible-backed existing (**§7.13zv** AST-586 + **§7.13zzc** AST-617 rebuild). No new test files — **AST-615** already landed claim-floor regression on **`origin/ftr/AST-600-rebuild-586-git-casualty`**; **AST-617** restores **`database.py`** + **`api_admin.py`** call sites covered by the same manifest.

1. **`tests/component/utils/test_config.py::TestAst586DispatchClaimScoreFloor`** — `dispatch_claim_uses_score_floor` (VALID_TITLE False; PASSED_JD / PASSED_JOBLIST True; RETRY / None / "" False).
2. **`tests/component/core/test_dispatcher.py::TestRunUnified::test_qualify_valid_title_claim_without_score_floor`** — `qualify_job_listings` + VALID_TITLE passes `score_floor=None` into `get_new_job_batch`.
3. **`tests/component/ui/api/test_api_admin.py::TestDispatchTasks`** — list/create/update: VALID_TITLE row `is_scored=False`, `score_floor=None`; PASSED_JOBLIST still scored with default floor 1.0.
4. **`tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_trigger_state_helpers`** — config helper imports assert claim vs grading metadata split.

**Run (narrow):**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst586DispatchClaimScoreFloor \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_qualify_valid_title_claim_without_score_floor \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks \
  tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_trigger_state_helpers
```

**Publish:** `origin/sub/AST-600/AST-617-qualify-no-score-floor-valid-title-rebuild-586` @ `2ad10c34` (`merge-tests(AST-617): origin/tests 45062446`).

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `f75773d01ae47523dd4939e808aacc1aa77bf1f2`

— Betty

#### hedy — 2026-06-14T04:00:43.052Z
Plan: [ast-617-dispatch-claim-without-score-floor-valid-title-rebuild-586.md](https://github.com/susansomerset/astral/blob/sub/AST-600/AST-617-qualify-no-score-floor-valid-title-rebuild-586/docs/features/interface/ast-617-dispatch-claim-without-score-floor-valid-title-rebuild-586.md) @ `2329248b`

**Scope:** `Single-Component` — restore AST-586 claim-floor call sites in `database.py` (count + schema backfill) and `api_admin.py`; config + dispatcher verified already correct on branch.

**Conf:** `high` — reuses shipped AST-586 helper and exact line-level swaps; plan-time grep confirms git-casualty sites.

**Risk:** `Medium` — count/admin mismatch if wrong helper left in place; mitigated by existing AST-586 component tests on branch.

Plan-time finding: `dispatch_claim_uses_score_floor` + dispatcher claim path present; `trigger_state_used_by_scored_dispatch_task` still used at database ~4890/5201 and api_admin ~532/560/618/640/677.

---

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

---

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-600/AST-617-qualify-no-score-floor-valid-title-rebuild-586` @ `2ad10c34`

### What's solid

| Area | Notes |
|------|-------|
| **Plan fidelity (AST-617)** | `database.py` import + `count_eligible_for_dispatch_task` (~5201) + schema backfill (~4890) use `dispatch_claim_uses_score_floor`; `score_floor_by_trigger_for_candidate` (~1555) unchanged per plan. |
| **Admin API** | `api_admin.py` — `_trigger_state_is_scored`, `list_dtasks`, `dispatch_task_keys`, `create_dtask`, `update_dtask` all swap to claim helper; grading import removed from this file. |
| **Config / dispatcher** | No diff vs `origin/dev` — claim helper + `_trigger_state_scored` already landed (AST-615 sibling). |
| **Rules (§2.1, §3.3)** | Claim vs grading metadata split preserved; data/ui → utils config imports allowed; no state-machine or batch-pattern drift. |

### Issues

| Severity | Location | Issue |
|----------|----------|-------|
| **fix-now** | Publish ref commits `842b6dda`–`ef194b22` | **Sibling scope bleed (§5d):** AST-601 **AST-616** product code on this AST-600 branch — `api_candidate.py` (`GET …/resume_structure`), `ArtifactsBaseResumeContent.tsx`, `ast-616` plan doc. AST-617 plan explicitly excludes React UI and candidate API beyond dispatch admin. Re-publish ref without AST-616 commits (or revert `ef194b22` and ancestors) before ftr merge. |
| **discuss** | `ef194b22` message | Was the AST-616 merge intentional for test harness? If so, confirm AST-616 tracking/merge-parent path so this ticket does not absorb another epic's ship. |

### Recommended actions (resolve-child)

| Action | Owner |
|--------|-------|
| Drop AST-616 commits from `sub/AST-600/AST-617-*` (keep `6e5f2e17` + plan/docs/test merges for AST-617 only) | Hedy |
| No code changes needed for AST-617 claim-floor call sites — implementation matches plan | — |
| After ref cleanup, re-run Betty §7.13zv manifest on cleaned tip | Hedy / Betty |

---

## Resolution (2026-06-13)

**Reviewer:** Radia · **Publish ref:** `origin/sub/AST-600/AST-617-qualify-no-score-floor-valid-title-rebuild-586`

**fix-now (scope bleed):** Rebuilt publish ref from `origin/ftr/AST-600-rebuild-586-git-casualty` + AST-617-only cherry-picks (`c5e54db3` plan → `252da4d6` code → Betty bible `ca7f6429`). Dropped commits `591cc4cd`–`ef194b22` (AST-616 plan/product + accidental `merge-tests` merge). Diff vs `ftr` is now `database.py`, `api_admin.py`, plan doc, and bible §7.13zzc only.

**discuss (`ef194b22`):** Accidental — Betty's `merge-tests` on `astral-tests` pulled `origin/sub/AST-601/AST-616-*` into this ref; not required for AST-617 harness (§7.13zv reuses existing component tests). AST-616 remains on its own publish ref under AST-601.

**Product:** No additional claim-floor code changes; implementation matched plan at `252da4d6`.

**Verify:** Betty §7.13zv manifest green on cleaned tip; §9a dry-run clean vs `origin/dev` and `origin/ftr/AST-600-rebuild-586-git-casualty`.
