<!-- linear-archive: AST-596 archived 2026-06-23 -->

## Linear archive (AST-596)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-596/mid-chain-dispatch-claim-and-hop-failure-batch-release-need-to-pick-up  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-593 — Need to pick up and parse daisy chained prompts from the middle using agent_data content  
**Blocked by / blocks / related:** parent: AST-593

### Description

## What this implements

Scheduled Actions and auto dispatch claim **BUILD_ARTIFACTS.<task_key>** jobs using the dispatch row's **task_key** as the mid-chain entry hop (not only chain entry at **contemplate_job**). On hop failure, release the job from the in-flight batch claim so the next tick can redispatch at the correct compound state without double-processing the same job.

## Acceptance criteria

2. Susan can dispatch a mid-chain Scheduled Action (e.g. `draft_job_resume` at **BUILD_ARTIFACTS.<matching state>**) for a job whose upstream hops already succeeded; the run starts at that hop. (dispatch half — claim + entry)
3. When hop *N* fails, the job is not left claimed in a batch that blocks redispatch on the next tick; a subsequent manual or auto dispatch at the correct entry task processes the job once.

## Boundaries

* Does not define compound states — blocked by sibling state/config ticket.
* Does not load **agent_data** into caller tokens — Ada sibling.
* Must not break **AST-534** honor-dispatch-task_key behavior for entry hops.

## Notes for planning

* `dispatch_tasks` row **trigger_state** must align with compound **JOB_STATES** keys.
* Consult artifact batch path (`_run_job_artifact_entry_batch`) must respect mid-chain entry + failure release.

## Git branch (authoritative)

Parent **ftr/AST-593-mid-chain-artifact-resume**, child **sub/AST-593/<child-id>-mid-chain-dispatch-claim-release**.

### Comments

#### radia — 2026-06-12T16:53:33.462Z
**Review** — `origin/dev...origin/sub/AST-593/AST-596-mid-chain-dispatch-claim-release` @ `b1db91a6`

### What's solid

- Plan stages 1–4 match the diff: **`release_job_dispatch_claim`** in **`tracker`**, pre-claim compound guard in **`dispatcher._run_unified`**, consult row validation + **`_artifact_entry_hop_failed`** on all three failure branches in **`_run_job_artifact_entry_batch`**.
- **`BUILD_FAILED`** and **`clear_job_artifact_resume_content`** removed from hop-failure paths; success path still gates **`CANDIDATE_REVIEW`** and **`contemplate_job`** cover letter (AST-534).
- **§2.4:** mismatch returns before claim; per-job lock release on failure; dispatcher **`finally`** **`clear_job_batch`** untouched.
- Betty manifest covers mismatch skip, mid-chain entry, hop-failure release, tracker delegation (**§7.13zm**).

### Issues

| Severity | Location | Finding |
| --- | --- | --- |
| **discuss** | `src/core/dispatcher.py` ~L166–177 | Inline **`resume_artifact_*`** import inside **`_run_unified`** (no lazy-load comment). Grandfathered by existing board_search pattern — optional hoist to module top in **resolve-astral**. |
| **advisory** | Epic integration | Sub tip needs **AST-595** helpers wherever merged for UAT; per-hop transitions / **`agent_data`** hydration are **AST-597**, not this ticket. |

**No fix-now.**

### Doc

Plan review blob: `docs/features/artifacts/ast-596-mid-chain-dispatch-claim-and-hop-failure-batch-release.md` @ `b1db91a6` (`docs(AST-596): Radia review — mid-chain claim release sign-off`).

**Hedy:** proceed **resolve-astral** (optional discuss item only).

#### betty — 2026-06-12T05:01:58.018Z
**Correction:** `docs/ASTRAL_TEST_BIBLE.md` shasum on `origin/sub/AST-593/AST-596-mid-chain-dispatch-claim-release` @ `78e3cd43` is `e56d17003f27e15f87f58513ff17c8fb2c2da523` (not `f804f594` — pre-reconcile).

— Betty

#### betty — 2026-06-12T05:01:35.479Z
## QA test manifest (AST-596)

**Publish ref:** `origin/sub/AST-593/AST-596-mid-chain-dispatch-claim-release` @ `78e3cd43`

**Bible:** `docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `f804f5943d85f3b572fd836e1288346d9df91e8f`

### Manifest (run in order)

1. `tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch` — compound trigger routing; hop failure releases claim (no `BUILD_FAILED`, no resume wipe); terminal success unchanged
2. `tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty` — mid-chain `draft_job_resume` + matching compound `trigger_state`; mismatch returns zero summary
3. `tests/component/core/test_consult.py::TestAst596MidChainDispatchClaimRelease::test_release_job_dispatch_claim_delegates_to_database`
4. `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast534_forwards_dispatch_task_key_to_consult` — compound `trigger_state` + resume hop `task_key` forwards to consult
5. `tests/component/core/test_dispatcher.py::TestRunUnified::test_ast596_resume_hop_mismatch_skips_claim` — mismatch skips claim/consult (`_SUMMARY_ZERO`)

### Narrow run

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch \
  tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty \
  tests/component/core/test_consult.py::TestAst596MidChainDispatchClaimRelease \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast534_forwards_dispatch_task_key_to_consult \
  tests/component/core/test_dispatcher.py::TestRunUnified::test_ast596_resume_hop_mismatch_skips_claim
```

### Test deltas (this pass)

- **Revised:** `test_artifact_entry_batch_errors_skip_cover_letter`, `test_artifact_entry_batch_empty_persist_releases_claim` — expect `release_job_dispatch_claim`, not `BUILD_FAILED` / resume wipe
- **Revised:** AST-534 / AST-371 consult routes use compound `BUILD_ARTIFACTS.<task_key>` trigger states (AST-595 dependency)
- **Revised:** `test_ast534_forwards_dispatch_task_key_to_consult` uses compound trigger state
- **Added:** mid-chain compound trigger + dispatch/consult mismatch guards; tracker helper smoke

### Publish SHAs (Joan)

| Commit | Subject | On publish ref |
| --- | --- | --- |
| `054841bc` | `test(AST-596): mid-chain dispatch claim and hop failure release manifest` | yes |
| `78e3cd43` | `docs(AST-596): test bible §7.13zv–§7.13zz including dispatch claim row` | yes (bible reconcile — sub tip lacked §7.13zv–§7.13zz; appended before Appendix A) |

— Betty

#### hedy — 2026-06-11T23:46:38.353Z
Plan: [`docs/features/artifacts/ast-596-mid-chain-dispatch-claim-and-hop-failure-batch-release.md`](https://github.com/susansomerset/astral/blob/sub/AST-593/AST-596-mid-chain-dispatch-claim-release/docs/features/artifacts/ast-596-mid-chain-dispatch-claim-release.md) @ `origin/sub/AST-593/AST-596-mid-chain-dispatch-claim-release` @ `1fc82c99`

**Scope — Single-Component:** `consult.py`, `dispatcher.py`, and `tracker.py` only — compound-state claim guard, per-job batch release on hop failure, no `BUILD_FAILED` on daisy-chain failures.

**Conf — Medium:** AST-534 entry wiring exists; this adds AST-595-dependent claim alignment and failure release. Build blocked until Katherine's compound states land.

**Risk — HIGH:** Stuck `batch_id` or wrong claim guard blocks mid-chain redispatch; removing `BUILD_FAILED` without immediate lock release strands jobs.

Betty delta noted in plan Stage 4 (consult + dispatcher tests for no `BUILD_FAILED`, batch release, mismatch guard).

---

# Mid-chain dispatch claim and hop failure batch release

**Linear:** [AST-596](https://linear.app/astralcareermatch/issue/AST-596/mid-chain-dispatch-claim-and-hop-failure-batch-release-need-to-pick-up)  
**Parent:** [AST-593](https://linear.app/astralcareermatch/issue/AST-593/need-to-pick-up-and-parse-daisy-chained-prompts-from-the-middle-using)  
**Publish ref (origin):** `sub/AST-593/AST-596-mid-chain-dispatch-claim-release`

## Summary

After **AST-595** compound **`BUILD_ARTIFACTS.<task_key>`** states land, Scheduled Actions and auto dispatch must **claim jobs in the matching compound state** and start **`run_resume_artifact_chain_for_job`** at the dispatch row's **`task_key`** (AST-534 entry path — preserve). When a resume artifact daisy-chain hop fails, the job must **not** transition to **`BUILD_FAILED`**, must **not** wipe partial artifact progress, and must **release its per-job batch lock immediately** so the next scheduler tick can redispatch at the correct entry hop without double-claiming the same row.

This ticket owns **dispatch claim alignment + consult artifact-batch failure release only**. Per-hop success transitions and **`agent_data`** caller hydration are **AST-597** (Ada). Compound **`JOB_STATES`** registry is **AST-595** (Katherine).

## Prerequisite gate (mandatory before Stage 1)

**AST-595 must be merged** onto **`dev-hedy`** (and present on **`origin/ftr/AST-593-mid-chain-artifact-resume`**) before implementation begins.

Verify at build start:

```bash
python3 -c "from src.utils.config import resume_artifact_compound_state, resume_artifact_hop_task_keys; print(resume_artifact_compound_state(resume_artifact_hop_task_keys()[0]))"
```

Expected output shape: **`BUILD_ARTIFACTS.anticipate_scan`** (first hop key from **`BUILD_CONFIG['resume_artifact_chain']['hop_task_keys']`**).

If helpers or compound states are missing: **stop**, comment on **AST-596** naming **AST-595**, do not patch config here.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Resume-artifact dispatch row validation; mid-chain failure path (no **`BUILD_FAILED`**, per-job batch release); preserve AST-534 entry + terminal **`CANDIDATE_REVIEW`** on full-chain success | core |
| `src/core/dispatcher.py` | Pre-claim guard: resume hop **`task_key`** must match compound **`trigger_state`** | core |
| `src/core/tracker.py` | Thin **`release_job_dispatch_claim(astral_job_id)`** wrapper over **`clear_job_batch_lock`** | core |

**Out of scope (sibling tickets — do not touch):**

| Ticket | Owner | Work |
|--------|-------|------|
| **AST-595** | Katherine | Compound **`JOB_STATES`**, **`hop_task_keys`**, **`dispatch_task_admin_defaults`** compound **`trigger_state`** |
| **AST-597** | Ada | Per-hop success **`transition_job_state`**; **`agent_data`** caller hydration in **`do_task`** / chain resume |
| **AST-592** | — | **`draft_job_resume`** validation bug |
| **`tests/`**, **`docs/ASTRAL_TEST_BIBLE.md`** | Betty | Test deltas after Code Complete |

## Stage 1: Per-job dispatch claim release helper (`tracker.py`)

**Done when:** Consult can release one job's batch lock without clearing the whole dispatch batch or transitioning state.

1. In `src/core/tracker.py`, after **`clear_job_batch`**, add:

   ```python
   def release_job_dispatch_claim(astral_job_id: str) -> None:
       """Clear batch_id lock on one job so the next dispatch tick can reclaim (AST-596)."""
       database.clear_job_batch_lock(astral_job_id)
   ```

2. Do **not** change **`cancel_artifact_build`** — it already calls **`clear_job_batch_lock`** when **`batch_id`** is set; this helper is for hop-failure paths inside consult.

## Stage 2: Dispatch row ↔ compound state guard (`dispatcher.py`)

**Done when:** A resume-artifact Scheduled Action row whose **`task_key`** and **`trigger_state`** disagree never claims jobs; consult is not invoked with a mismatched pair.

1. At top of **`_run_unified`** in `src/core/dispatcher.py`, after resolving **`dispatch_task_key`** and **`input_state`**, add validation when **`entity_type == "job"`**:

   ```python
   from src.utils.config import resume_artifact_compound_state, resume_artifact_hop_task_keys

   if dispatch_task_key in resume_artifact_hop_task_keys():
       expected = resume_artifact_compound_state(dispatch_task_key)
       if (input_state or "").strip() != expected:
           _sched_log.warning(
               "dispatch row mismatch: task_key=%s expects trigger_state=%s got %s — skipping claim",
               dispatch_task_key,
               expected,
               input_state,
           )
           return dict(_SUMMARY_ZERO)
   ```

2. Leave existing claim path unchanged: **`get_new_job_batch(input_state, ...)`** still uses the dispatch row's **`trigger_state`** (now compound **`BUILD_ARTIFACTS.<task_key>`** after AST-595). **`dispatch_task_key`** continues to forward to consult (AST-534).

   ⚠️ **Decision:** Mismatch is a **configuration error** on the **`dispatch_tasks`** row — fail closed (zero summary) rather than claim on wrong state or run wrong hop.

## Stage 3: Consult artifact batch — mid-chain failure release (`consult.py`)

**Done when:** Hop failure leaves job state unchanged, releases batch lock per failed job, never calls **`BUILD_FAILED`** for resume artifact chain hops; full-chain success still lands **`CANDIDATE_REVIEW`** when terminal resume body persists; AST-534 **`first_task_key`** entry unchanged.

1. In `src/core/consult.py`, import from config (module level, with existing config imports):

   ```python
   from src.utils.config import (
       resume_artifact_compound_state,
       resume_artifact_hop_task_keys,
       parse_resume_artifact_hop,
   )
   ```

2. Add module-level helper immediately above **`_run_job_artifact_entry_batch`**:

   ```python
   def _resume_artifact_dispatch_row_ok(entry_task_key: str, input_state: str) -> bool:
       tk = (entry_task_key or "").strip()
       if tk not in resume_artifact_hop_task_keys():
           return True  # not a resume hop row — caller handles elsewhere
       expected = resume_artifact_compound_state(tk)
       got = (input_state or "").strip()
       if got != expected:
           logger.warning(
               "artifact entry: task_key=%s expects trigger_state=%s got %s",
               tk,
               expected,
               got,
           )
           return False
       return True
   ```

3. At the start of **`run_consult_task`**, in the job branch after resolving **`task_key`**, before routing to **`_run_job_artifact_entry_batch`**:

   ```python
   if task_key in _JOB_ARTIFACT_ENTRY_KEYS and not _resume_artifact_dispatch_row_ok(task_key, input_state):
       return zero
   ```

4. Refactor **`_run_job_artifact_entry_batch`** failure handling. Replace both **`BUILD_FAILED`** transition blocks (chain **`success`** false, and empty terminal persist after **`success`**) with a shared per-job failure helper:

   ```python
   def _artifact_entry_hop_failed(aid: str) -> None:
       tracker.release_job_dispatch_claim(aid)
   ```

   **Chain hop failure** (`not r.get("success")`):

   - Call **`_artifact_entry_hop_failed(aid)`**
   - **Do not** call **`tracker.transition_job_state(..., "BUILD_FAILED")`**
   - **Do not** call **`tracker.clear_job_artifact_resume_content(aid)`**
   - **`errors += 1`**; **`continue`**

   **Terminal persist gate failure** (chain succeeded but **`not tracker.job_has_persisted_resume_body(aid, row)`**):

   - Call **`_artifact_entry_hop_failed(aid)`**
   - **Do not** transition to **`BUILD_FAILED`**
   - **Do not** clear resume content
   - **`errors += 1`**; **`continue`**

   ⚠️ **Decision:** Susan's parent answer — daisy-chain jobs **stay in the last happy compound state** on hop failure; **`BUILD_FAILED`** is removed from this path. Partial **`resume_content`** from upstream hops must survive for mid-chain retry (**AST-597** reuse).

5. **Success path — unchanged semantics:**

   - When chain succeeds **and** **`job_has_persisted_resume_body`**: **`transition_job_state([aid], "CANDIDATE_REVIEW")`** (terminal gate, AST-552).
   - When **`entry_task_key == "contemplate_job"`**: still **`await _run_cover_letter_for_job(...)`** after **`CANDIDATE_REVIEW`** (AST-534).
   - **`run_resume_artifact_chain_for_job(..., first_task_key=entry_task_key)`** — no change to entry hop wiring.

6. **CANDIDATE_REVIEW transition failure** (existing **`except ValueError`** around terminal transition):

   - Replace **`BUILD_FAILED`** recovery with **`_artifact_entry_hop_failed(aid)`** only
   - **Do not** clear resume content
   - **`errors += 1`**; **`continue`**

7. Grep **`src/core/consult.py`** for remaining **`BUILD_FAILED`** in **`_run_job_artifact_entry_batch`** — there must be **zero** after this stage.

## Stage 4: Verify compile + manual claim smoke

**Done when:** Touched modules import cleanly; manual reasoning confirms claim + release paths.

1. **`python3 -m py_compile src/core/consult.py src/core/dispatcher.py src/core/tracker.py`**

2. **`python3 -c "from src.core import consult, dispatcher, tracker; print('ok')"`**

3. Linear comment for Betty (**post Code Complete**): update **`tests/component/core/test_consult.py`**:
   - **`test_artifact_entry_batch_errors_skip_cover_letter`**: expect **no** **`BUILD_FAILED`** transition; expect **`release_job_dispatch_claim`** (or **`clear_job_batch_lock`**) called
   - **`test_artifact_entry_batch_empty_persist_build_failed`**: rename/repurpose — expect **no** **`BUILD_FAILED`**; batch lock released
   - Add **`test_mid_chain_compound_trigger_claims_matching_entry`**: dispatch row **`task_key=draft_job_resume`**, **`trigger_state=BUILD_ARTIFACTS.draft_job_resume`** routes to artifact entry with that **`first_task_key`**
   - Add **`test_dispatch_row_mismatch_skips_artifact_entry`**: mismatched **`task_key` / `trigger_state`** returns zero summary without calling chain helper
   - Extend **`tests/component/core/test_dispatcher.py`**: mismatch guard returns **`_SUMMARY_ZERO`** without claim

   Manifest narrow run (Betty):

   ```bash
   ./scripts/testing/run_component_tests.sh \
     tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch \
     tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty \
     tests/component/core/test_dispatcher.py::TestRunUnified
   ```

## Execution contract (for the developer agent)

- Execute stages in order. **Stop** if AST-595 helpers are missing (**Prerequisite gate**).
- Do **not** edit **`src/utils/config.py`** compound state registry (**AST-595**).
- Do **not** edit **`src/core/agent.py`** per-hop transitions or **`agent_data`** hydration (**AST-597**).
- Do **not** edit **`tests/`** — post **[qa-handoff]** manifest in Linear comment if tests fail.
- When a step references a function that does not exist after AST-595 merge, **stop** and comment on **AST-596** — do not invent alternate state encoding.
- Complete each stage with one commit on **`dev-hedy`**, then Joan **`store-code-commit`** per **build-astral**.

Blocking questions use parent **AST-593** thread:

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

## Self-Assessment

**Scope — `Single-Component`**  
Three core modules only (**`consult.py`**, **`dispatcher.py`**, **`tracker.py`**) — dispatch claim guard, artifact-batch failure release, and a one-line tracker helper; no config, agent, UI, or data-layer schema changes.

**Conf — `Medium`**  
AST-534 entry wiring already exists; this ticket adds compound-state claim alignment and removes **`BUILD_FAILED`** from the daisy-chain failure path. Sequencing depends on AST-595 landing first; interaction with AST-597 per-hop success transitions is bounded (failure path must not assume transitions Ada owns).

**Risk — `HIGH`**  
Wrong claim guard or missing per-job batch release blocks mid-chain redispatch or double-processes jobs; removing **`BUILD_FAILED`** without releasing **`batch_id`** leaves jobs stuck until manual cancel.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| §2.1 config | Compound state strings read via **`resume_artifact_*`** helpers only — no new literals in core. |
| §2.4 batch processing | Per-job **`release_job_dispatch_claim`** on failure; dispatcher **`finally`** **`clear_job_batch`** unchanged for whole-batch cleanup. |
| §2.6 state machine | No new transitions defined here; hop failure = **no** state change; terminal **`CANDIDATE_REVIEW`** preserved on full success. |
| §1.3 DRY | Shared **`_artifact_entry_hop_failed`** for both failure branches in artifact batch loop. |
| §3.3 imports | Config helpers imported in **`consult`** / **`dispatcher`**; tracker wrapper keeps **`database`** access in tracker layer. |
| §3.5 naming | **`release_job_dispatch_claim`** mirrors cancel-build batch release semantics. |

No unresolved conflicts requiring **`conf-!!-NONE`**.

## Review

**Built:** `dev-hedy` → `origin/sub/AST-593/AST-596-mid-chain-dispatch-claim-release` @ `78e3cd43`.

**Product commits:** `3700c8b0` tracker `release_job_dispatch_claim`; `1367c0c7` dispatcher pre-claim compound-state guard; `ff493dba` consult hop failure batch release (no `BUILD_FAILED`, no resume wipe).

**Betty delta (tests):** `tests/component/core/test_consult.py` — artifact entry failure releases batch lock, no `BUILD_FAILED`; `tests/component/core/test_dispatcher.py` — mismatch `task_key`/`trigger_state` skips claim; tracker helper smoke.

### Radia review (`origin/dev...origin/sub/AST-593/AST-596-mid-chain-dispatch-claim-release`)

#### What's solid

- Plan fidelity: all four stages land in the three scoped core modules only; **`BUILD_FAILED`** and **`clear_job_artifact_resume_content`** are gone from **`_run_job_artifact_entry_batch`** failure paths; success path still gates **`CANDIDATE_REVIEW`** + **`contemplate_job`** cover letter (AST-534).
- **§2.4 batch pattern:** pre-claim mismatch guard returns before **`get_new_job_batch`**; per-hop failure calls **`release_job_dispatch_claim`**; dispatcher **`finally`** **`clear_job_batch`** unchanged for whole-batch cleanup.
- **§2.1 / §2.6:** compound state strings come only from **`resume_artifact_*`** config helpers — no new literals; hop failure leaves state unchanged for AST-597 to pick up.
- Defense in depth: duplicate row validation in **`dispatcher._run_unified`** and **`consult.run_consult_task`** matches the plan’s fail-closed config-error posture.
- Betty manifest (**§7.13zm** bible) covers mismatch skip, mid-chain entry, hop-failure release, and tracker delegation.

#### Issues

| Severity | Location | Finding |
| --- | --- | --- |
| **discuss** | `src/core/dispatcher.py` ~L166–177 | Function-scoped **`from src.utils.config import resume_artifact_*`** inside **`_run_unified`** (no lazy-load comment). Same file already uses inline config imports for board_search — acceptable grandfather, but hoisting next to the module-level config block would satisfy **§1.2 / B1** without behavior change. Optional in **`resolve-astral`**. |
| **advisory** | Epic integration | Sub tip assumes **AST-595** compound helpers exist wherever this branch is merged for UAT; per-hop success transitions and **`agent_data`** hydration remain **AST-597** — do not expect mid-chain state advancement from this ticket alone. |

No **fix-now** items.

#### Recommended actions

| Action | Owner | Notes |
| --- | --- | --- |
| Proceed **`resolve-astral`** | Hedy | Optional: hoist **`resume_artifact_*`** imports to module top in **`dispatcher.py`**. |
| Parent UAT | Susan | Exercise mid-chain Scheduled Action after **AST-595** + **AST-597** on **`ftr/AST-593-*`**. |
| Sibling scope | Ada / Katherine | **AST-597** transitions + caller hydration; **AST-595** compound registry — unchanged here. |

## Resolution

**2026-06-12 — resolve-astral (Hedy):** Radia **Review Posted** — no **fix-now** items. Optional **discuss** (hoist **`resume_artifact_*`** imports in **`dispatcher.py`**) already satisfied on **`dev-hedy`** / publish ref via module-level imports (**`trigger_state_used_by_scored_dispatch_task`** block retained from **`origin/dev`**). **§9a:** **`fix(AST-596): align dispatcher and bible with origin/dev for §9a merge`** reconciles publish ref with central **`origin/dev`** so **`prep-uat`** / **`finish-up`** merge paths stay clean; **`origin/ftr/AST-593-mid-chain-artifact-resume`** dry-run already clean. **Advisory** (AST-595 helpers on epic branch, AST-597 transitions) unchanged — parent UAT after siblings land.
