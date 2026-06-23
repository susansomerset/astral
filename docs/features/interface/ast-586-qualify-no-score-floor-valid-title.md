<!-- linear-archive: AST-586 archived 2026-06-15 -->

## Linear archive (AST-586)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-586/uat-qualify-job-listings-dispatch-must-not-apply-score-floor-on-valid  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-547 — The JD score isn't appearing in the Recommended job list.  
**Blocked by / blocks / related:** parent: AST-547

### Description

## What failed

Susan cannot retest AST-547 JD score persistence: dispatching **qualify_job_listings** on **VALID_TITLE** applies **score_floor** gating (dispatcher defaults scored tasks to floor **1.0** when unset). **VALID_TITLE** jobs have no **latest_score** yet, so nothing is claimed.

## Expected

**qualify_job_listings** dispatch on **VALID_TITLE** claims eligible jobs without **score_floor** filter (task does not use dispatch score_floor for input-state claim).

## Repro

1. Configure dispatch **qualify_job_listings** with trigger **VALID_TITLE**.
2. Run dispatch — no jobs claimed / pipeline blocked.
3. Susan cannot reach **evaluate_jd** to verify **jd_score** save.

## Parent AC

AST-547 UAT: run qualify → evaluate_jd → confirm JD score on Recommended list.

## Boundaries

* Does not change AST-560 **jd_score** persistence logic.
* Does not remove **score_floor** for **PASSED_JD** / consult dispatch steps that legitimately gate on prior scores.
* Fix likely in [**dispatcher.py**](<http://dispatcher.py>) claim path and/or admin **is_scored** defaults for **qualify_job_listings** input trigger.

### Comments

#### radia — 2026-06-05T23:24:37.248Z
**Review** — `origin/dev...origin/sub/AST-547/AST-586-qualify-no-score-floor-valid-title` @ `355ad566` (product); review doc @ `01d71102`.

### fix-now
None.

### discuss
None.

### advisory
- `score_floor_by_trigger_for_candidate` (`database.py` ~1554) still uses `trigger_state_used_by_scored_dispatch_task`; plan leaves it unchanged — loop is scoped to `PASSED_SCORE_GATED_STATES` only, so no claim-path regression.
- `JD_READY` (evaluate_jd input) also returns `dispatch_claim_uses_score_floor` **False** — same class of fix as `VALID_TITLE`; not ticket scope but correct for pre-score input triggers.

### What's solid
- `dispatch_claim_uses_score_floor` in `config.py` splits claim gating from grading metadata; legacy `trigger_state_used_by_scored_dispatch_task` preserved with tests documenting `VALID_TITLE` divergence.
- Call sites: `dispatcher._trigger_state_scored`, `count_eligible_for_dispatch_task`, schema backfill, `api_admin` list/create/update — all per plan.
- Boundaries held: no `consult.py` / jd_score persistence / frontend changes.
- Manifest §7.13zv tests cover config helper, dispatcher `score_floor=None` on VALID_TITLE claim, admin `is_scored`/`score_floor` shaping.

**Doc:** `docs/features/interface/ast-586-qualify-no-score-floor-valid-title.md` — Radia review section (Joan `01d71102`).

#### betty — 2026-06-05T23:21:43.046Z
## QA test manifest

**Publish ref:** `origin/sub/AST-547/AST-586-qualify-no-score-floor-valid-title` @ `355ad566`

**`docs/ASTRAL_TEST_BIBLE.md` shasum (publish ref):** `5e528f2e49dbaf1cbf139b3e5b322ace0c68950f`

1. **`tests/component/utils/test_config.py::TestAst586DispatchClaimScoreFloor`** — `dispatch_claim_uses_score_floor`: **VALID_TITLE** / **VALID_TITLE_RETRY** / **None** / **""** → **False**; **PASSED_JD** / **PASSED_JOBLIST** → **True**; legacy **`trigger_state_used_by_scored_dispatch_task("VALID_TITLE")`** still **True** (grading metadata unchanged).
2. **`tests/component/core/test_dispatcher.py::TestRunUnified::test_qualify_valid_title_claim_without_score_floor`** — **`qualify_job_listings`** + **VALID_TITLE** passes **`score_floor=None`** into **`get_new_job_batch`**.
3. **`tests/component/ui/api/test_api_admin.py::TestDispatchTasks`** — list row **VALID_TITLE** → **`is_scored=False`**, **`score_floor=None`**; create **VALID_TITLE** → **`score_floor=None`**; **PASSED_JOBLIST** still defaults **1.0**.
4. **`tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_trigger_state_helpers`** — **`dispatch_claim_uses_score_floor`** assertions.

**Bible:** **§7.13zv** (parent **AST-547**).

**Narrowed run:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst586DispatchClaimScoreFloor \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_qualify_valid_title_claim_without_score_floor \
  tests/component/ui/api/test_api_admin.py::TestDispatchTasks \
  tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_trigger_state_helpers
```

#### chuckles — 2026-06-05T23:18:47.496Z
**validate-plan: APPROVED**

Plan correctly separates `dispatch_claim_uses_score_floor` from task grading metadata; touches dispatcher/database/api_admin only; preserves PASSED_* consult floors. Boundaries match AST-586 ticket and parent UAT need.

— Chuckles

#### hedy — 2026-06-05T23:17:41.456Z
Plan: [ast-586-qualify-no-score-floor-valid-title.md](https://github.com/susansomerset/astral/blob/sub/AST-547/AST-586-qualify-no-score-floor-valid-title/docs/features/interface/ast-586-qualify-no-score-floor-valid-title.md)

**Scope:** `Single-Component` — new `dispatch_claim_uses_score_floor` in config plus claim/count/admin call-site swaps; no consult or frontend edits.

**Conf:** `high` — AST-549 ties VALID_TITLE to scored qualify defaults; `PASSED_SCORE_GATED_STATES` already documents which states should gate claim.

**Risk:** `Medium` — misclassified transition states could over/under-claim on PASSED_JOBLIST or consult paths; plan keeps membership to existing transition + PASSED_* sets only.

---

# UAT: qualify_job_listings dispatch must not apply score_floor on VALID_TITLE (AST-586)

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-586/uat-qualify-job-listings-dispatch-must-not-apply-score-floor-on-valid  
**Parent:** https://linear.app/astralcareermatch/issue/AST-547/the-jd-score-isnt-appearing-in-the-recommended-job-list  

**Publish ref (origin):** `sub/AST-547/AST-586-qualify-no-score-floor-valid-title`  
**Parent integration ref:** `ftr/AST-547-jd-score-recommended-list`  

Susan cannot retest AST-547 because **qualify_job_listings** dispatch on **VALID_TITLE** applies **score_floor** gating (default **1.0** when unset). Jobs at **VALID_TITLE** have no **latest_score** yet, so `claim_job_batch` filters them out (`latest_score IS NOT NULL AND latest_score >= ?`) and nothing is claimed. This ticket splits **dispatch claim gating** from **task grading metadata** so input-state rows (pre-score) do not use **score_floor**, while **PASSED_JD** / consult steps keep floor behavior.

**Verified (plan time):** `trigger_state_used_by_scored_dispatch_task("VALID_TITLE")` returns **True** because AST-549 walks schedulable defaults and matches `qualify_job_listings` (`scored: True`, default trigger **VALID_TITLE**). `dispatcher._run_unified` lines ~194–208 pass `score_floor=1.0` into `get_new_job_batch`. `PASSED_SCORE_GATED_STATES` in `config.py` (~1152) already documents consult claim floors (**PASSED_JD**, **PASSED_DO**, **PASSED_GET**, **PASSED_LIKE**) — **VALID_TITLE** is intentionally absent.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `dispatch_claim_uses_score_floor(trigger_state)`; document vs `trigger_state_used_by_scored_dispatch_task` | utils |
| `src/core/dispatcher.py` | Job claim path uses `dispatch_claim_uses_score_floor` for `score_floor` (not `trigger_state_used_by_scored_dispatch_task`) | core |
| `src/data/database.py` | `count_eligible_for_dispatch_task` and dispatch_task schema backfill use `dispatch_claim_uses_score_floor` | data |
| `src/ui/api/api_admin.py` | List/create/update dispatch rows: `is_scored` / `score_floor` / `available_count` align with claim helper | ui |

**Not in scope:** `src/core/consult.py` grading or **jd_score** persistence (AST-560), `api_jobs.py` skipped-list logic (already limits floors to `PASSED_SCORE_GATED_STATES`), frontend `AdminScheduledActions.tsx` (renders API `is_scored` / `score_floor` as returned).

**Tests (Betty at Code Complete — engineer does not edit `tests/` in build):** extend `tests/component/utils/test_config.py`, `tests/component/core/test_dispatcher.py`, `tests/component/ui/api/test_api_admin.py` per Stage 2.

---

## Stage 1: Claim-score-floor helper and call sites

**Done when:** `dispatch_claim_uses_score_floor("VALID_TITLE")` is **False**; `dispatch_claim_uses_score_floor("PASSED_JD")` is **True**; `_run_unified` for `qualify_job_listings` + **VALID_TITLE** passes `score_floor=None` into `get_new_job_batch`; admin list row for same trigger shows `is_scored=False` and `score_floor=None`; `python3 -m py_compile` passes on touched `.py` files.

1. In `src/utils/config.py`, immediately after `PASSED_SCORE_GATED_STATES` (~1152), add:

   ```python
   def dispatch_claim_uses_score_floor(trigger_state: Optional[str]) -> bool:
       """True when job claim should filter latest_score >= dispatch_task.score_floor.

       Distinct from trigger_state_used_by_scored_dispatch_task (task grading / TASK_CONFIG)
       and dispatch_task_key_is_scored (task_key catalog). Input triggers such as VALID_TITLE
       run a scored task but entities lack latest_score until that step completes (AST-586).
       """
       if trigger_state is None:
           return False
       ts = str(trigger_state).strip()
       if not ts or ts.endswith("_RETRY"):
           return False
       if ts in PASSED_SCORE_GATED_STATES:
           return True
       return ts in _TRANSITION_STATES_USED_BY_SCORED_TASKS
   ```

   Do **not** remove or change `trigger_state_used_by_scored_dispatch_task` in this ticket (other docs may reference it; claim paths switch to the new helper only).

2. In `src/core/dispatcher.py`:
   - Import `dispatch_claim_uses_score_floor` from `src.utils.config` (add to existing config import block).
   - Replace `_trigger_state_scored` body (~47–48) with:

     ```python
     def _trigger_state_scored(trigger_state: Optional[str], task_key: str) -> bool:
         return dispatch_claim_uses_score_floor(trigger_state)
     ```

     (`task_key` parameter stays for call-site symmetry; unused.)

   - No other logic changes in `_run_unified` — existing floor math (~194–195) already keys off `is_scored`.

3. In `src/data/database.py`:
   - Import `dispatch_claim_uses_score_floor` from `src.utils.config`.
   - In `count_eligible_for_dispatch_task` (~5200), replace `trigger_state_used_by_scored_dispatch_task(state)` with `dispatch_claim_uses_score_floor(state)` for the `is_scored` / `floor` calculation.
   - In dispatch_task schema backfill (~4889), replace `trigger_state_used_by_scored_dispatch_task(trigger_state)` with `dispatch_claim_uses_score_floor(trigger_state)` when defaulting `score_floor` to **1.0** for NULL rows.

   Leave `score_floor_by_trigger_for_candidate` unchanged — it already iterates only `PASSED_SCORE_GATED_STATES`.

4. In `src/ui/api/api_admin.py`:
   - Import `dispatch_claim_uses_score_floor`.
   - Change `_trigger_state_is_scored` (~530–532) to `return dispatch_claim_uses_score_floor(trigger_state)`.
   - In `list_dtasks` (~560), `create_dtask` (~640), `update_dtask` (~677): replace every `trigger_state_used_by_scored_dispatch_task(...)` used for **`is_scored` / `score_floor` / default floor** with `dispatch_claim_uses_score_floor(...)`.
   - In `dispatch_task_keys` (~618) for existing-row fallback `is_scored`, use `dispatch_claim_uses_score_floor(r.get("trigger_state"))` (task catalog path via `_dispatch_task_key_form_meta` keeps `dispatch_task_key_is_scored(task_key)` unchanged).

5. Run:

   ```bash
   python3 -m py_compile src/utils/config.py src/core/dispatcher.py src/data/database.py src/ui/api/api_admin.py
   ```

⚠️ **Decision:** Claim gating uses **outcome / post-score states** (`PASSED_SCORE_GATED_STATES` + `_TRANSITION_STATES_USED_BY_SCORED_TASKS`), not schedulable **input** triggers (`VALID_TITLE`, `JD_READY`). That matches the existing `PASSED_SCORE_GATED_STATES` comment and fixes qualify without removing floors on **PASSED_JD** consult dispatch.

---

## Stage 2: Betty manifest (Code Complete — not engineer build)

**Done when:** Betty posts manifest + bible lines; `test-astral` green on publish ref.

Engineer Linear comment at **Code Complete** (build stage end) lists these expected test deltas for Betty:

1. **`tests/component/utils/test_config.py`** — new class or methods:
   - `dispatch_claim_uses_score_floor("VALID_TITLE")` → **False**
   - `dispatch_claim_uses_score_floor("VALID_TITLE_RETRY")` → **False**
   - `dispatch_claim_uses_score_floor("PASSED_JD")` → **True**
   - `dispatch_claim_uses_score_floor("PASSED_JOBLIST")` → **True**
   - `dispatch_claim_uses_score_floor(None)` / `""` → **False**
   - Keep existing `trigger_state_used_by_scored_dispatch_task("VALID_TITLE")` test only if still documenting legacy helper; do not require it to match claim helper.

2. **`tests/component/core/test_dispatcher.py`** — new async test `test_qualify_valid_title_claim_without_score_floor`:
   - Task dict: `entity_type=job`, `trigger_state=VALID_TITLE`, `task_key=qualify_job_listings`, `batch_call_mode=1`, `batch_size=10`.
   - Mock `get_new_job_batch`; assert `claim.call_args.kwargs["score_floor"] is None`.

3. **`tests/component/ui/api/test_api_admin.py`** — adjust `test_trigger_state_helpers` / dispatch list tests:
   - Assert `dispatch_claim_uses_score_floor("VALID_TITLE")` is **False** (import from config).
   - If list mock includes a row `{task_key: qualify_job_listings, trigger_state: VALID_TITLE, ...}`, assert `is_scored is False` and `score_floor is None` after GET `/api/admin/dispatch_tasks`.
   - `PASSED_JOBLIST` / `PASSED_JD` rows still show `is_scored True` and default floor **1.0** when NULL.

---

## Self-Assessment

**Scope:** `Single-Component` — One new config helper plus four import/call-site swaps in dispatcher, database count/backfill, and admin API; no consult or UI component edits.

**Conf:** `high` — Root cause is traced to AST-549 input-trigger ↔ scored-task coupling; `PASSED_SCORE_GATED_STATES` already states the intended claim semantics.

**Risk:** `Medium` — Wrong membership in `dispatch_claim_uses_score_floor` would over-claim or under-claim jobs on **PASSED_JOBLIST** / **JD_READY** paths; mitigated by keeping logic aligned with `_TRANSITION_STATES_USED_BY_SCORED_TASKS` and existing `PASSED_SCORE_GATED_STATES` only.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Reuses `_TRANSITION_STATES_USED_BY_SCORED_TASKS` and `PASSED_SCORE_GATED_STATES`; no duplicate state lists. |
| §2.1 config | New helper lives in `config.py`; `score_floor` vs `pass_threshold` separation unchanged. |
| §2.4 batch | Claim still uses `score_floor` param on `get_new_job_batch`; only when to pass non-`None` changes. |
| §2.6 state machine | No transition changes; claim filter only. |
| §3.3 imports | data imports utils helper (allowed); ui imports utils (allowed). |
| §3.5 naming | `dispatch_claim_uses_score_floor` matches existing `dispatch_*` / `trigger_state_*` naming. |

No conflicts requiring `conf-!!-NONE`.

---

## Review (build)

**Branch:** `origin/sub/AST-547/AST-586-qualify-no-score-floor-valid-title`  
**Tip:** `1e5caaf1`  
**Built:** Stage 1 — `dispatch_claim_uses_score_floor` in config; claim/count/admin call sites use it instead of `trigger_state_used_by_scored_dispatch_task`. Stage 2 component tests deferred to Betty per build-astral test-tree ban.

**Betty manifest (Code Complete):**

1. `tests/component/utils/test_config.py` — `dispatch_claim_uses_score_floor` cases (VALID_TITLE False, PASSED_JD/PASSED_JOBLIST True, RETRY/None False).
2. `tests/component/core/test_dispatcher.py` — `test_qualify_valid_title_claim_without_score_floor` asserts `score_floor=None` on claim.
3. `tests/component/ui/api/test_api_admin.py` — list/helper tests for VALID_TITLE `is_scored=False`, `score_floor=None`; PASSED_JD/PASSED_JOBLIST still scored.

---

## Radia review (AST-586)

**Diff:** `origin/dev...origin/sub/AST-547/AST-586-qualify-no-score-floor-valid-title` @ `355ad566`  
**Reviewer:** Radia · **JOAN_SESSION** `5112d559-3ac6-4ff9-9a15-5ce5eb3ffcbf`

### What's solid

| Area | Notes |
|------|-------|
| Plan fidelity | `dispatch_claim_uses_score_floor` matches Stage 1 spec; four call-site swaps (dispatcher, database count/backfill, admin list/create/update) as planned. |
| Root cause | Correctly splits **claim gating** from `trigger_state_used_by_scored_dispatch_task` (grading / schedulable-default metadata). Legacy helper preserved; tests document divergence for `VALID_TITLE`. |
| Boundaries | No `consult.py`, `api_jobs.py`, or frontend edits — AST-560 / AST-547 scope respected. |
| §2.1 / §2.4 | `score_floor` applies only on post-score / transition triggers (`PASSED_SCORE_GATED_STATES` + `_TRANSITION_STATES_USED_BY_SCORED_TASKS`); input triggers `VALID_TITLE` and `JD_READY` correctly return False. |
| Tests | Manifest §7.13zv cases covered: config helper, dispatcher claim kwargs, admin list/create + helper assertions. |

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| — | — | No **fix-now** or **discuss** items. |

### Recommended actions

| Action | Owner | Notes |
|--------|-------|-------|
| Proceed to **resolve-astral** (none required) | Hedy | Happy path — no engineer changes from this review. |
| **Advisory** | — | `score_floor_by_trigger_for_candidate` still calls legacy `trigger_state_used_by_scored_dispatch_task` but iterates only `PASSED_SCORE_GATED_STATES` per plan — no behavior change. Optional future doc cross-link in `ASTRAL_CODE_RULES.md` §2.1 for `dispatch_claim_uses_score_floor`. |

---

## Resolution (2026-06-05)

**Reviewer:** Radia · **Publish ref:** `origin/sub/AST-547/AST-586-qualify-no-score-floor-valid-title`

No **fix-now** or **discuss** items — product shipped at `355ad566` with Radia review doc at `01d71102`. Resolve pass required no additional code changes.

**Verified on `dev-hedy`:**

- Betty manifest §7.13zv (10 tests): config helper, dispatcher `score_floor=None` on VALID_TITLE claim, admin list/create/helper — all green.
- §9a dry-run: publish ref merges cleanly into `origin/dev` and `origin/ftr/AST-547-jd-score-recommended-list`.

**Outcome:** Susan can retest AST-547 — **qualify_job_listings** on **VALID_TITLE** claims jobs without **score_floor** gating.

