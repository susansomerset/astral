# UAT: BUILD_ARTIFACTS chain completes but job does not graduate to CANDIDATE_REVIEW

**Linear:** [AST-844 — UAT: BUILD_ARTIFACTS chain completes but job does not graduate to CANDIDATE_REVIEW](https://linear.app/astralcareermatch/issue/AST-844/uat-build-artifacts-chain-completes-but-job-does-not-graduate-to-candidate)

**Parent (coordination only):** [AST-788 — BUILD_ARTIFACTS substates do not graduate](https://linear.app/astralcareermatch/issue/AST-788/build-artifacts-substates-do-not-graduate)

**Publish ref:** `origin/sub/AST-788/AST-844-uat-build-artifacts-chain-terminal-graduation` (origin only)

## Summary

Susan UAT on **origin/dev** after **AST-832** (2026-07-02): the BUILD_ARTIFACTS daisy-chain runs through terminal hop **`propose_application_responses`** (LLM success, `agent_performance.status=success`) but the job stays on **`BUILD_ARTIFACTS`** — no **`CANDIDATE_REVIEW`** transition, no **Ready** in Recommended Jobs.

Server log shows **`batch_id=propose_application_responses-<uuid>`** and **`in_run_next_chain=True`** — the scheduler dispatched the **terminal** hop row directly (or as a `run_next` child under that dispatch batch id).

**Root cause (confirmed):**

1. **`_resolve_chain_start_task_key`** only accepts `dispatch_task_key` values in **`resume_artifact_hop_task_keys()`** (six resume hops ending at **`finalize_job_resume`**). Cover-letter hops and **`propose_application_responses`** are in **`JOB_ARTIFACT_ENTRY_TASK_KEYS`** but **not** in that tuple → resolve returns **`None`** → **`_chain_dispatch_row_ok`** logs mismatch / skips → **`do_chain_for_job`** never runs → **no graduation**.

2. When the chain **does** enter via **`anticipate_scan`** and **`do_task`** walks **`run_next`** through cover hops to **`propose_application_responses`**, graduation **should** run in **`do_chain_for_job`** after **`do_task`** returns — but there is **no info-level log** on success (debug-only), so UAT logs look like a no-op even when graduation runs. This ticket fixes the **terminal-hop dispatch gap** (primary) and adds **observable graduation logging** (secondary).

**DB chain (reference):** `finalize_job_resume` → `draft_cover_letter` → … → `propose_application_responses` (empty `run_next`).

⚠️ **Decision:** Introduce **`build_artifacts_chain_task_keys()`** in **`config.py`**: **`JOB_ARTIFACT_ENTRY_TASK_KEYS` minus `draft_cover_letter`** (cover entry uses **`_run_craft_job_cover_letter_batch`**; all other artifact hops including cover **check/finalize** and **`propose_application_responses`** participate in BUILD_ARTIFACTS CHAIN). Replace **`resume_artifact_hop_task_keys()`** checks in **`_resolve_chain_start_task_key`** with this full set. Keep **`resume_artifact_hop_task_keys()`** for entry discovery and legacy compound naming only.

⚠️ **Decision:** After **`do_task`** succeeds in **`do_chain_for_job`**, call **`_chain_graduate_to_candidate_review`** only when the executed hop is **terminal** (no non-empty **`run_next`** on the **last** hop **`do_task` actually ran**). When **`start_key`** is chain-entry and **`do_task`** recurses through **`run_next`**, treat **`do_task` return** as terminal completion (existing single-call recursion) and graduate — same as today, but now reachable for **`propose_application_responses`** dispatch rows.

⚠️ **Decision:** Add **`logger.info`** on successful **`BUILD_ARTIFACTS` → `CANDIDATE_REVIEW`** transition in **`_chain_graduate_to_candidate_review`** (non-debug) so UAT/server logs show graduation without enabling debug.

**Out of scope:** Revert **AST-832**; compound **`JOB_STATES`** registry; **`run_next` graph** / agent_task seed edits; **`draft_cover_letter`** batch path; persist-gate logic change unless build proves gate false on Susan's repro job (then stop and comment).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add **`build_artifacts_chain_task_keys()`** | utils |
| `src/core/consult.py` | Full-chain hop set in **`_resolve_chain_start_task_key`**; terminal-hop graduation guard + info log | core |

**Tests:** Betty owns **`tests/`** — engineer does **not** edit test files. Stage 2 documents Betty manifest additions.

**Verify only (no change expected):**

| File | Role |
|------|------|
| `src/core/agent.py` | `do_task` + `run_next` recursion unchanged |
| `src/core/dispatcher.py` | Claim / **`run_consult_task`** routing unchanged |

---

## Stage 1: Full BUILD_ARTIFACTS chain hop registry

**Done when:** **`build_artifacts_chain_task_keys()`** returns cover hops + **`propose_application_responses`** and excludes **`draft_cover_letter`**; **`python3 -m py_compile src/utils/config.py`** passes.

1. In **`src/utils/config.py`**, after **`JOB_ARTIFACT_ENTRY_TASK_KEYS`** (~line 669), add:

   ```python
   def build_artifacts_chain_task_keys() -> frozenset[str]:
       """All consult hops in the BUILD_ARTIFACTS CHAIN except draft_cover_letter (separate batch)."""
       return frozenset(JOB_ARTIFACT_ENTRY_TASK_KEYS) - frozenset({"draft_cover_letter"})
   ```

2. `python3 -m py_compile src/utils/config.py`

**Ritual:** `code(AST-844): build_artifacts_chain_task_keys helper`

---

## Stage 2: Terminal-hop dispatch + graduation in consult

**Done when:** **`_resolve_chain_start_task_key(job, dispatch_task_key='propose_application_responses', …)`** returns **`propose_application_responses`** for flat **`BUILD_ARTIFACTS`** job; **`_chain_dispatch_row_ok`** returns **True**; **`do_chain_for_job`** calls **`_chain_graduate_to_candidate_review`** after successful terminal **`do_task`**; info log **`BUILD_ARTIFACTS chain graduated … → CANDIDATE_REVIEW`** emitted on success; **`python3 -m py_compile src/core/consult.py`** passes.

1. In **`src/core/consult.py`**, import **`build_artifacts_chain_task_keys`** from **`src.utils.config`**.

2. Replace the hop-membership guard in **`_resolve_chain_start_task_key`**:

   ```python
   if tk not in build_artifacts_chain_task_keys():
       return None
   ```

   (Keep **AST-832** legacy compound + chain-entry logic unchanged below that guard.)

3. Add helper above **`do_chain_for_job`**:

   ```python
   def _chain_hop_has_run_next(task_key: str) -> bool:
       from src.data.database import get_agent_task
       row = get_agent_task((task_key or "").strip()) or {}
       return bool((row.get("run_next") or "").strip())
   ```

4. In **`do_chain_for_job`**, after **`do_task`** returns success, before graduation:

   ```python
   if _chain_hop_has_run_next(start_key):
       return {"success": True, "chain_incomplete": True}
   ```

   ⚠️ **Decision:** When **`do_task`** recurses via **`run_next`**, the **outer** call returns only after the **terminal** inner hop completes — **`start_key`** may be **`anticipate_scan`** while the terminal hop is **`propose_application_responses`**. Use **`do_task` success + no `run_next` on `start_key` only when `start_key` is the dispatch row**; when **`start_key`** has **`run_next`**, rely on **`do_task` recursion** having completed the full chain and graduate (do **not** return early). Concretely: **only** apply the early-return when **`start_key == dispatch_task_key`** and **`_chain_hop_has_run_next(start_key)`** — mid-chain dispatch rows that intentionally run a single hop (AST-534) must not graduate.

   Replace step 4 with:

   ```python
   if start_key == dispatch_task_key and _chain_hop_has_run_next(start_key):
       return {"success": True, "chain_incomplete": True}
   ```

5. In **`_chain_graduate_to_candidate_review`**, after successful **`transition_job_state`**, add:

   ```python
   logger.info(
       "BUILD_ARTIFACTS chain graduated job=%s from_state=%s → CANDIDATE_REVIEW",
       astral_job_id,
       from_state,
   )
   ```

6. Manual verify on epic worktree:

   ```python
   from src.core import consult as c
   from src.utils.config import BUILD_ARTIFACTS_BASE_STATE

   job = {"state": BUILD_ARTIFACTS_BASE_STATE}
   assert c._resolve_chain_start_task_key(
       job, dispatch_task_key="propose_application_responses", candidate_id="somerset",
   ) == "propose_application_responses"
   assert c._chain_dispatch_row_ok(
       job, "propose_application_responses", BUILD_ARTIFACTS_BASE_STATE, "somerset",
   )
   ```

7. **Betty manifest (document only — do not edit tests):** Extend **`docs/test-bible/core/consult.md`** when Betty picks up **AST-844**:

   - **`_resolve_chain_start_task_key`**: flat **`BUILD_ARTIFACTS`** + **`propose_application_responses`** dispatch → returns that hop.
   - **`do_chain_for_job`**: mocked **`do_task`** success on terminal hop → **`transition_job_state(..., CANDIDATE_REVIEW)`** once.
   - **`do_chain_for_job`**: mocked **`do_task`** success on non-terminal hop with **`run_next`** when **`start_key == dispatch_task_key`** → **no** graduation.
   - Regression: **AST-832** chain-entry + legacy compound cases unchanged.

8. `python3 -m py_compile src/core/consult.py`

**Ritual:** `code(AST-844): terminal BUILD_ARTIFACTS hop dispatch and graduation logging`

---

## Self-Assessment

**Scope:** `minor` — One config helper + consult chain resolution/graduation path; no dispatcher or agent graph changes.

**Conf:** `high` — Repro log matches skipped **`propose_application_responses`** dispatch; local resolve returns **`None`** today; DB **`run_next`** confirms terminal hop.

**Risk:** `Medium` — Wrong early-return on **`chain_incomplete`** could block graduation for misconfigured mid-chain dispatch rows — guarded by **`start_key == dispatch_task_key`**.

---

## Self-Review (ASTRAL_CODE_RULES)

| Rule | OK? |
|------|-----|
| §1.3 DRY | Single **`build_artifacts_chain_task_keys()`** source; reuses AST-832 entry/legacy logic |
| §2.6 state machine | Graduation via **`tracker.transition_job_state`** only |
| §3.3 imports | Lazy **`get_agent_task`** in consult helper (existing pattern) |
| Boundaries | No **`JOB_STATES`** compound keys; no AST-832 revert |

No conflicts flagged.

---

## Review (build)

**Branch:** `origin/sub/AST-788/AST-844-uat-build-artifacts-chain-terminal-graduation`

**Commits:**
- `45d9388` — `code(AST-844): build_artifacts_chain_task_keys helper`
- `2f22240` — `code(AST-844): terminal BUILD_ARTIFACTS hop dispatch and graduation logging`

**Manual verify:** `_resolve_chain_start_task_key` + `_chain_dispatch_row_ok` accept `propose_application_responses` on flat `BUILD_ARTIFACTS` job.

---

## Resolution

**Date:** 2026-07-03  
**Radia review:** Clean — no fix-now items.

**Shipped:** `build_artifacts_chain_task_keys()` expands chain hop recognition to cover-letter hops + `propose_application_responses`; terminal-hop dispatch reaches `do_chain_for_job` graduation with info-level log; `_chain_single_hop_dispatch_only` narrows `chain_incomplete` to mid-hop resume rows (AST-534). Betty manifest 13/13 green.

**Publish tip:** `origin/sub/AST-788/AST-844-uat-build-artifacts-chain-terminal-graduation` @ `301715e` · §9a dev + ftr dry-run clean.
