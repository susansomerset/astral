<!-- linear-archive: AST-832 archived 2026-07-22 -->

## Linear archive (AST-832)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-832/uat-anticipate-scan-chain-abort-at-build-artifactsfinalize-job-resume  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-788 — BUILD_ARTIFACTS substates do not graduate  
**Blocked by / blocks / related:** parent: AST-788

### Description

## What failed

Susan UAT on **origin/dev** (2026-06-27): **anticipate_scan** and **draft_cover_letter** Scheduled Actions show **Available > 0** but **Run** does not execute work.

Server log when running **anticipate_scan** (dispatch task id 5306, candidate **somerset**):

```
dispatcher._dispatch_one index 1/1 anticipate_scan -> task start
 | candidate_id=somerset available_count=1 entity_batch_id=anticipate_scan-... mode=CLICK run_next_chain=True entity_type='job' trigger_state='BUILD_ARTIFACTS'
Dispatching anticipate_scan — 1 available, batch anticipate_scan-...
artifact chain: dispatch row mismatch task_key=anticipate_scan job_state=BUILD_ARTIFACTS.finalize_job_resume
[anticipate_scan] thread exited and cleared from registry
```

Job remains at compound `BUILD_ARTIFACTS.finalize_job_resume`; chain aborts before `do_task`. **draft_cover_letter** never becomes eligible because jobs do not reach **CANDIDATE_REVIEW**.

## Expected

* **AC 5:** Mid-chain resume from `BUILD_ARTIFACTS*` (including `BUILD_ARTIFACTS.finalize_job_resume`) runs remaining CHAIN hops via `do_chain_for_job` and graduates to **CANDIDATE_REVIEW** — not `dispatch row mismatch` abort.
* Scheduler **Run** for a BUILD_ARTIFACTS CHAIN task with **available_count > 0** executes the chain (or the correct hop for the job's legacy compound state), not immediate no-op exit.
* After graduation, **draft_cover_letter** dispatch works for jobs in **CANDIDATE_REVIEW**.

## Repro

1. Pull **origin/dev**; use candidate **somerset** (or any job at `BUILD_ARTIFACTS.finalize_job_resume` with chain prerequisites).
2. Admin → **Scheduled Actions** → **anticipate_scan** — confirm **Available > 0**.
3. Click **Run**; watch server log.
4. Observe `artifact chain: dispatch row mismatch task_key=anticipate_scan job_state=BUILD_ARTIFACTS.finalize_job_resume` and thread exit with no state change.
5. Confirm **draft_cover_letter** still does not fire for jobs blocked in BUILD_ARTIFACTS compound states.

## Parent AC (quoted inline)

> 5. Mid-chain resume from `BUILD_ARTIFACTS*` completes remaining hops and graduates without manual repair.

## Boundaries

* Does **not** reintroduce compound `JOB_STATES` or AST-789 graduation helper.
* Does **not** change **AST-806** merge-ticket-log / deploy tooltip wiring.
* Fix `_resolve_chain_start_task_key` **/** `_chain_dispatch_row_ok` **/ eligibility** so legacy compound job states resume the correct hop — not reject valid scheduler claims.

### Comments

#### chuckles — 2026-06-27T19:34:15.120Z
### Plan fidelity

- **`_chain_entry_dispatch_task_key`** helper matches plan — delegates to **`_build_artifacts_chain_entry_task_key`** with **`ValueError`** / empty-candidate fallback to **`resume_artifact_hop_task_keys()[0]`**.
- **`_resolve_chain_start_task_key`**: legacy compound branch now accepts hop-specific **or** chain-entry **`dispatch_task_key`**; flat **`BUILD_ARTIFACTS`** base-state path unchanged.
- **`_chain_dispatch_row_ok`** untouched — mismatch log path fixed via resolver only. Scope stays **`src/core/consult.py`**; no dispatcher/config/UI drift.

### ASTRAL_CODE_RULES

- **§1.3 DRY:** entry detection reuses existing **`_build_artifacts_chain_entry_task_key`**; no duplicate graph walk.
- **§2.6 state machine:** read-only legacy compound hop; graduation still via existing **`do_chain_for_job`** / **`do_task`** **`run_next`** — no ad hoc state writes.
- **§3.3 imports:** core-only change; lazy agent import in **`do_chain_for_job`** unchanged.
- **§5f / §5g:** N/A — no new debug-contract emission or external-layer edits.
- **Boundaries:** no compound **`JOB_STATES`** reintroduction; **AST-806** / **AST-828** scope not smuggled.

### Tests / manifest

- Betty manifest + **`TestAst803ChainHelpers`** / **`TestAst371ResumeArtifactDispatch`** cover chain-entry at **`finalize_job_resume`**, **`_chain_dispatch_row_ok`**, and batch non-skip — 7/7 green on publish ref.

### Advisory

- **`docs/test-bible/utils/config.md`**: stray **`---`** removed (formatting only; no manifest change).

**Diff:** `origin/dev...origin/sub/AST-788/AST-832-uat-anticipate-scan-chain-abort-at-build-artifacts-finalize-job-resume` (1 code commit + Betty test/bible).

— Radia

#### betty — 2026-06-27T19:33:30.504Z
**Bible shasum correction:** `docs/test-bible/core/consult.md` → `e7de7908de846bd7f1a40651123b796f16576c3f` (on publish ref @ `6f902ba`).

#### betty — 2026-06-27T19:33:27.123Z
## QA test manifest (AST-832)

1. **Chain-entry mid-chain resume (UAT fix):**
   - `TestAst803ChainHelpers::test_chain_entry_resolves_legacy_finalize_job_resume`
   - `TestAst803ChainHelpers::test_chain_entry_resolves_with_candidate_entry_discovery`
   - `TestAst803ChainHelpers::test_chain_entry_dispatch_row_ok_for_legacy_finalize_hop`
   - `TestAst371ResumeArtifactDispatch::test_chain_batch_runs_legacy_compound_chain_entry_dispatch`

2. **Regression:** `TestAst803ChainHelpers::test_legacy_compound_job_state_resolves_start_key` (hop-specific row unchanged).

```bash
.venv/bin/python -m pytest \
  tests/component/core/test_consult.py::TestAst803ChainHelpers \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch::test_chain_batch_runs_legacy_compound_chain_entry_dispatch \
  -q
```

**Publish:** `origin/sub/AST-788/AST-832-uat-anticipate-scan-chain-abort-at-build-artifacts-finalize-job-resume` @ `6f902ba` (`merge-tests(AST-832): origin/tests 217b67e`)

**Bible shasum:** `docs/test-bible/core/consult.md` → `316451e20ca0201fe75a83caaa05983f0d702a55`

— Betty

#### ada — 2026-06-27T19:31:36.390Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-788/AST-832-uat-anticipate-scan-chain-abort-at-build-artifacts-finalize-job-resume/docs/features/consult/ast-832-uat-anticipate-scan-chain-abort-at-build-artifacts-finalize-job-resume.md

Single stage: fix `_resolve_chain_start_task_key` so chain-entry dispatch (`anticipate_scan` + `BUILD_ARTIFACTS` trigger) resumes from job's legacy compound hop (`finalize_job_resume`) instead of `dispatch row mismatch` abort. AST-534 hop-specific rows unchanged.

**Scope:** minor — `consult.py` only.
**Conf:** high — log matches code; root cause reproduced in `_resolve_chain_start_task_key`.
**Risk:** Medium — BUILD_ARTIFACTS scheduler path; entry detection uses existing `_build_artifacts_chain_entry_task_key`.

---

# UAT: anticipate_scan chain abort at BUILD_ARTIFACTS.finalize_job_resume (draft_cover_letter blocked)

**Linear:** [AST-832 — UAT: anticipate_scan chain abort at BUILD_ARTIFACTS.finalize_job_resume](https://linear.app/astralcareermatch/issue/AST-832/uat-anticipate-scan-chain-abort-at-build-artifacts-finalize-job)

**Parent (coordination only):** [AST-788 — BUILD_ARTIFACTS substates do not graduate](https://linear.app/astralcareermatch/issue/AST-788/build-artifacts-substates-do-not-graduate)

**Publish ref:** `origin/sub/AST-788/AST-832-uat-anticipate-scan-chain-abort-at-build-artifacts-finalize-job-resume` (origin only)

## Summary

Susan UAT on **origin/dev** (2026-06-27): **anticipate_scan** Scheduled Action shows **Available > 0** but **Run** exits immediately. Log:

```
artifact chain: dispatch row mismatch task_key=anticipate_scan job_state=BUILD_ARTIFACTS.finalize_job_resume
```

Job stays at legacy compound **`BUILD_ARTIFACTS.finalize_job_resume`**; **`draft_cover_letter`** never becomes eligible because jobs do not reach **CANDIDATE_REVIEW**.

**Root cause (confirmed):** `_resolve_chain_start_task_key` in `src/core/consult.py` returns the legacy hop only when **`dispatch_task_key == legacy_hop`**. Scheduler **Run** uses the **chain-entry** dispatch row (`anticipate_scan`, `trigger_state=BUILD_ARTIFACTS`, `run_next_chain=True`). For a job already at **`BUILD_ARTIFACTS.finalize_job_resume`**, `legacy_hop="finalize_job_resume"` but `dispatch_task_key="anticipate_scan"` → **`None`** → `_chain_dispatch_row_ok` logs mismatch and `_run_build_artifacts_chain_batch` skips the job (zero work, thread exits).

**AST-534 honesty preserved:** Hop-specific dispatch rows (`dispatch_task_key` matches compound hop) still start at that hop. Chain-entry rows (`dispatch_task_key == _build_artifacts_chain_entry_task_key(candidate_id)`) resume from the job's legacy compound hop when present.

⚠️ **Decision:** Use **`_build_artifacts_chain_entry_task_key(candidate_id)`** to detect chain-entry dispatch rows — do not treat every `anticipate_scan` dispatch as entry (candidate may have multiple BUILD_ARTIFACTS rows). When `candidate_id` is empty, fall back to **`dispatch_task_key == resume_artifact_hop_task_keys()[0]`** (same fallback as entry discovery) so company-derived candidate resolution in `do_chain_for_job` still works after ctx hydration.

⚠️ **Decision:** **`do_task`** already walks **`run_next`** internally — no change to **`do_chain_for_job`** hop loop. For **`finalize_job_resume`** (terminal hop), one **`do_task`** call + graduation is correct.

**Out of scope:** Reintroducing compound **`JOB_STATES`** or AST-789 graduation; **AST-806** merge-ticket-log wiring; **`draft_cover_letter`** claim validation (**AST-828** on **AST-752**); dispatch_task / `run_next` graph edits.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Fix `_resolve_chain_start_task_key` for chain-entry + legacy compound mid-chain resume | core |

**Tests:** Betty owns **`tests/`** — engineer does **not** edit test files. Stage 1 documents Betty manifest additions.

**Verify only (no change expected):**

| File | Role |
|------|------|
| `src/core/dispatcher.py` | Already claims `build_artifacts_claim_states()` for flat `BUILD_ARTIFACTS` trigger |
| `src/core/agent.py` | `do_task` + `run_next` unchanged |
| `src/utils/config.py` | `legacy_build_artifacts_hop` unchanged |

---

## Stage 1: Chain-entry mid-chain resume in `_resolve_chain_start_task_key`

**Done when:** `_resolve_chain_start_task_key` returns **`finalize_job_resume`** for job state **`BUILD_ARTIFACTS.finalize_job_resume`** with `dispatch_task_key="anticipate_scan"` and chain-entry candidate dispatch rows; existing **`test_legacy_compound_job_state_resolves_start_key`** behavior unchanged; `python3 -m py_compile src/core/consult.py` passes.

1. In `src/core/consult.py`, replace **`_resolve_chain_start_task_key`** body (keep signature) with:

   ```python
   def _resolve_chain_start_task_key(
       job: Dict[str, Any],
       *,
       dispatch_task_key: str,
       candidate_id: str,
   ) -> Optional[str]:
       tk = (dispatch_task_key or "").strip()
       if tk not in resume_artifact_hop_task_keys():
           return None
       job_state = (job.get("state") or "").strip()
       legacy_hop = legacy_build_artifacts_hop(job_state)
       if legacy_hop:
           if tk == legacy_hop:
               return legacy_hop
           entry = _chain_entry_dispatch_task_key(candidate_id)
           if tk == entry:
               return legacy_hop
           return None
       if job_state == BUILD_ARTIFACTS_BASE_STATE:
           return tk
       return None
   ```

2. Add helper immediately above **`_resolve_chain_start_task_key`**:

   ```python
   def _chain_entry_dispatch_task_key(candidate_id: str) -> str:
       cid = (candidate_id or "").strip()
       if cid:
           try:
               return _build_artifacts_chain_entry_task_key(cid)
           except ValueError:
               return resume_artifact_hop_task_keys()[0]
       return resume_artifact_hop_task_keys()[0]
   ```

3. **Do not** change **`_chain_dispatch_row_ok`** — it already delegates to **`_resolve_chain_start_task_key`**.

4. Manual verify on epic worktree:

   ```python
   from src.core import consult as c
   from src.utils.config import resume_artifact_compound_state

   job = {"state": resume_artifact_compound_state("finalize_job_resume")}
   assert c._resolve_chain_start_task_key(
       job, dispatch_task_key="anticipate_scan", candidate_id="somerset",
   ) == "finalize_job_resume"
   assert c._chain_dispatch_row_ok(
       job, "anticipate_scan", "BUILD_ARTIFACTS", "somerset",
   )
   ```

5. **Betty manifest (document only — do not edit tests):** Add to `docs/test-bible/core/consult.md` when Betty picks up **AST-832**:

   - `_resolve_chain_start_task_key`: legacy compound job + chain-entry `dispatch_task_key` (`anticipate_scan`) → returns compound hop (`finalize_job_resume`).
   - `_chain_dispatch_row_ok`: same scenario returns **True** (no mismatch skip).
   - Regression: hop-specific row (`dispatch_task_key == legacy_hop`) still returns that hop.

   Suggested pytest: extend `TestAst803ChainHelpers` in `tests/component/core/test_consult.py`.

6. `python3 -m py_compile src/core/consult.py`

**Ritual:** `code(AST-832): chain-entry mid-chain resume for legacy BUILD_ARTIFACTS compound states`

---

## Self-Assessment

**Scope:** `minor` — Single function + small helper in `src/core/consult.py`; no config, dispatcher, or UI layers.

**Conf:** `high` — Log line matches code path; AST-803 plan Stage 5.4 intended chain-entry + legacy resume; existing test covers hop-specific match only.

**Risk:** `Medium` — BUILD_ARTIFACTS scheduler path only; wrong entry detection could start wrong hop — mitigated by `_build_artifacts_chain_entry_task_key` + AST-534 hop-specific branch.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | OK? |
|------|-----|
| §1.3 DRY | Reuses `_build_artifacts_chain_entry_task_key`; no duplicate entry logic |
| §2.6 state machine | No new states; legacy compound read-only |
| §3.3 imports | Core consult only; lazy agent import unchanged in `do_chain_for_job` |
| Boundaries | No compound `JOB_STATES` keys; no AST-806 / AST-828 scope |

No conflicts flagged.

---

## Review (build)

**Branch:** `origin/sub/AST-788/AST-832-uat-anticipate-scan-chain-abort-at-build-artifacts-finalize-job-resume`

**Commits:**
- `9acf0e6` — `code(AST-832): chain-entry mid-chain resume for legacy BUILD_ARTIFACTS compound states`

**Manual verify:** `_resolve_chain_start_task_key` + `_chain_dispatch_row_ok` return `finalize_job_resume` for `BUILD_ARTIFACTS.finalize_job_resume` job with `anticipate_scan` chain-entry dispatch.

---

## Resolution

**Date:** 2026-06-27  
**Radia review:** Clean — no fix-now items.

**Shipped:** `_chain_entry_dispatch_task_key` + `_resolve_chain_start_task_key` fix so chain-entry dispatch (`anticipate_scan`) resumes from legacy compound job state (`finalize_job_resume`) instead of `dispatch row mismatch` abort. AST-534 hop-specific rows unchanged. Betty manifest 7/7 green.

**Publish tip:** `origin/sub/AST-788/AST-832-uat-anticipate-scan-chain-abort-at-build-artifacts-finalize-job-resume` @ `6f902ba` · §9a dev + ftr dry-run clean.
