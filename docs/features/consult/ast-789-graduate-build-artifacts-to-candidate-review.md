<!-- linear-archive: AST-789 archived 2026-07-22 -->

## Linear archive (AST-789)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-789/graduate-build-artifacts-chain-to-candidate-review-build-artifacts  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-788 — BUILD_ARTIFACTS substates do not graduate  
**Blocked by / blocks / related:** parent: AST-788

### Description

## What this implements

Fix the missing terminal graduation when the resume-artifact BUILD_ARTIFACTS daisy-chain completes successfully: after the final hop (`finalize_job_resume`), the job must leave `BUILD_ARTIFACTS.finalize_job_resume` and land in `CANDIDATE_REVIEW` in the same dispatch run. Preserve existing per-hop compound progression through intermediate `BUILD_ARTIFACTS.<task_key>` states; apply the same graduation whether dispatch enters at the first compound hop or a mid-chain compound `trigger_state` row, subject to existing resume-body persist gates.

## Acceptance criteria

1. Susan runs a BUILD_ARTIFACTS scheduled action for a job that completes the full resume artifact chain; the job's tracker state is `CANDIDATE_REVIEW`, not any `BUILD_ARTIFACTS.*` compound state.
2. The same job appears under **Ready** in Recommended Jobs UI sections (not **In Progress**).
3. A run that fails before `finalize_job_resume` succeeds, or fails resume-body persist gates, does **not** promote the job to `CANDIDATE_REVIEW` — it remains at the last successful compound state (or existing failure handling).
4. A mid-chain dispatch row whose run completes through `finalize_job_resume` graduates the same way as a first-hop entry.
5. Component or integration coverage demonstrates terminal graduation and a regression guard against jobs left at `BUILD_ARTIFACTS.finalize_job_resume` after a successful full chain.

## Boundaries

* Does not change hop order, task prompts, or `BUILD_CONFIG['resume_artifact_chain']['hop_task_keys']`.
* Does not change **Generate Artifacts** / **Cancel** on `RECOMMENDED`, cover-letter chain behavior, or Recommended Job modal actions beyond the job appearing in the correct UI section after graduation.
* Does not alter `draft_cover_letter` dispatch at `CANDIDATE_REVIEW`.
* Does not include one-time backfill for jobs already stuck in `BUILD_ARTIFACTS.finalize_job_resume`.
* Sibling scope: none — this ticket carries the full fix.

## Notes for planning

* Primary surfaces: artifact batch exit in consult, per-hop compound transitions in agent, `tracker.transition_job_state` / `JOB_STATES` prior_states for `CANDIDATE_REVIEW`.
* AST-595 compound states and AST-597 per-hop transitions are shipped — regression guard required.
* Debug: AST-538 Style D on touched `debug=` paths for terminal hop graduation outcome.

## Git branch (authoritative)

Per `orientation` **§ Branch law**: parent `ftr/AST-788-build-artifacts-substates-do-not-graduate`, child `sub/AST-788/<child-id>-graduate-build-artifacts-to-candidate-review`. Created at **dispatch-parent**. Engineers publish to `origin/<sub-ref>` — never Linear `gitBranchName` when it disagrees.

### Comments

#### chuckles — 2026-06-25T05:23:23.242Z
Cancelled — superseded by AST-788 CHAIN redesign; AST-789 product approach expunged from codebase per parent definition.

— Chuckles

#### radia — 2026-06-24T22:10:11.147Z
### Plan fidelity

**Ref:** `origin/dev...origin/sub/AST-788/AST-789-graduate-build-artifacts-to-candidate-review` @ `131dae4` (product); Radia doc @ `adecb4d`

**fix-now:** none

### What's solid

- Stage 1–2 implemented as specified: `_try_graduate_artifact_job_to_candidate_review` — fresh `get_job`, persist gate `job_has_persisted_resume_body(..., None)`, structured `(ok, reason)`; single `transition_job_state(..., "CANDIDATE_REVIEW")` in `consult.py`.
- Batch loop logs `reason=` + `entry_task_key=` on failure before claim release; cover-letter path preserved for `contemplate_job`.
- **§1.5.1:** Style D `debug_index` (`index 1/1`) + `debug_detail` on attempt/success/failure when `debug=True` only.
- **§2.4 / §2.6:** Graduation failure → `_artifact_entry_hop_failed`; transitions via `tracker` only; no `agent.py` graduation (AST-597 boundary).
- Betty manifest green: `TestAst789TerminalGraduation` + AST-371 persist-gate regression + AST-534 `get_job` mock fix.

### advisory

- Plan **Risk HIGH / Conf Medium** — code hardens batch exit; Susan UAT should confirm resume chain reaches `finalize_job_resume` and job shows **Ready**. If still stuck, check warning for `persist_gate_failed` or `transition_failed:` (run with `debug=True` on graduation path for Style D detail).

**Review doc:** [`docs/features/consult/ast-789-graduate-build-artifacts-to-candidate-review.md`](https://github.com/susansomerset/astral/blob/sub/AST-788/AST-789-graduate-build-artifacts-to-candidate-review/docs/features/consult/ast-789-graduate-build-artifacts-to-candidate-review.md#radia-review-2026-06-24)

#### betty — 2026-06-24T22:07:03.943Z
## QA test manifest (AST-789)

**Publish:** `origin/sub/AST-788/AST-789-graduate-build-artifacts-to-candidate-review` @ `131dae4` (`merge-tests(AST-789): origin/tests 6410ea8`)

1. **Terminal graduation after finalize entry** — `tests/component/core/test_consult.py::TestAst789TerminalGraduation::test_artifact_entry_batch_graduates_after_finalize_hop_entry` — chain success + persist gate pass → single `transition_job_state(..., "CANDIDATE_REVIEW")` when `entry_task_key="finalize_job_resume"`; no cover letter.

2. **First-hop regression (anticipate_scan)** — `TestAst789TerminalGraduation::test_artifact_entry_batch_graduates_on_anticipate_scan_first_hop` — graduation still runs on non-terminal entry; `TestAst534DispatchTaskKeyHonesty::test_anticipate_scan_entry_skips_contemplate_job_and_cover_letter` revised for AST-789 fresh `get_job` requirement.

3. **Persist gate failure** — `TestAst371ResumeArtifactDispatch::test_artifact_entry_batch_empty_persist_releases_claim` — no `CANDIDATE_REVIEW`; `release_job_dispatch_claim` (AST-596 pattern).

4. **Transition failure** — `TestAst789TerminalGraduation::test_artifact_entry_batch_transition_failure_releases_claim` — `ValueError` from `transition_job_state` → warning path, no `passed`, claim released.

5. **Fresh persist gate** — `TestAst789TerminalGraduation::test_try_graduate_uses_fresh_persist_gate` — `job_has_persisted_resume_body(..., None)` (not claim snapshot).

6. **AST-597 regression (unchanged)** — `tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions`.

**Narrow run:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch \
  tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty \
  tests/component/core/test_consult.py::TestAst789TerminalGraduation \
  tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible:** `docs/test-bible/core/consult.md` @ `origin/sub/...` shasum `f3e4d6f94f9b9028d4c0c85762bb3b5745b6220f9634d39a054bfbe942cdfb18`

— Betty

#### hedy — 2026-06-24T22:04:47.265Z
## QA test manifest (AST-789)

**Publish ref:** `origin/sub/AST-788/AST-789-graduate-build-artifacts-to-candidate-review` @ `35326f8`

| # | Area | Test (new or extend) |
|---|------|----------------------|
| 1 | Terminal graduation after **finalize** entry | `tests/component/core/test_consult.py` — new `test_artifact_entry_batch_graduates_after_finalize_hop_entry`: mock chain success, persist gate pass, assert `transition_job_state(["job-x"], "CANDIDATE_REVIEW")` once when `entry_task_key="finalize_job_resume"` |
| 2 | Full-chain first-hop regression | Extend or duplicate AST-371 pattern with `entry_task_key="anticipate_scan"` — graduation still called |
| 3 | Persist gate failure | Assert **no** `CANDIDATE_REVIEW` transition; `release_job_dispatch_claim` called (AST-596 pattern) |
| 4 | Transition failure | Mock `transition_job_state` raising `ValueError` — assert warning path / no `passed` increment |
| 5 | AST-597 regression | `tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions` — no changes expected |

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch \
  tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty \
  tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions
```

#### hedy — 2026-06-24T22:03:03.006Z
**Plan doc:** [`docs/features/consult/ast-789-graduate-build-artifacts-to-candidate-review.md`](https://github.com/susansomerset/astral/blob/sub/AST-788/AST-789-graduate-build-artifacts-to-candidate-review/docs/features/consult/ast-789-graduate-build-artifacts-to-candidate-review.md) @ `73e2459`

**Self-assessment**
- **Scope:** Single-Component — `consult.py` terminal graduation helper + `_run_job_artifact_entry_batch` wiring only; no agent/config/dispatcher edits.
- **Conf:** Medium — batch-exit contract is established (AST-552/596/597); plan hardens fresh DB persist gate + transition error surfacing, but build must confirm which UAT failure mode fired before treating wiring as complete.
- **Risk:** HIGH — wrong graduation timing breaks Ready vs In Progress UX and candidate artifact gates; must not move CANDIDATE_REVIEW transition into `agent.py` per-hop path.

**Stages:** (1) `_try_graduate_artifact_job_to_candidate_review` helper with AST-538 Style D; (2) batch loop wiring + structured failure logging; (3) Betty manifest for finalize-hop graduation regression.

---

# Graduate BUILD_ARTIFACTS chain to CANDIDATE_REVIEW (BUILD_ARTIFACTS substates do not graduate)

**Linear:** [AST-789](https://linear.app/astralcareermatch/issue/AST-789/graduate-build-artifacts-chain-to-candidate-review-build-artifacts)  
**Parent:** [AST-788](https://linear.app/astralcareermatch/issue/AST-788/build-artifacts-substates-do-not-graduate) (AC reference only — do not expand epic scope)  
**Publish ref:** `origin/sub/AST-788/AST-789-graduate-build-artifacts-to-candidate-review`

Susan UAT: after a successful resume-artifact BUILD_ARTIFACTS daisy-chain, the job remains in **`BUILD_ARTIFACTS.finalize_job_resume`** instead of graduating to **`CANDIDATE_REVIEW`** (Recommended Jobs UI **Ready**). AST-595 compound states and AST-597 per-hop transitions are shipped; this ticket fixes the missing **terminal** step off the last compound state in the same dispatch run.

**Root cause (code on `origin/ftr/AST-788-build-artifacts-substates-do-not-graduate`):**

1. **Intended design (unchanged):** Per-hop success transitions advance through compound states via `agent._maybe_transition_resume_hop_progress`; the terminal hop **`finalize_job_resume`** has **`resume_artifact_next_compound_state(...) → None`**, so the job **stays** at **`BUILD_ARTIFACTS.finalize_job_resume`** until batch exit promotes to **`CANDIDATE_REVIEW`** (`consult._run_job_artifact_entry_batch`, AST-552 / AST-596 / AST-597 contract).
2. **Batch exit graduation exists** at `src/core/consult.py` ~1652–1658 but UAT jobs never leave the terminal compound state — one of these failure modes is occurring without Susan-visible signal:
   - **`transition_job_state([aid], "CANDIDATE_REVIEW")` raises `ValueError`** (caught, logged as warning, `_artifact_entry_hop_failed` releases claim, job state unchanged).
   - **`job_has_persisted_resume_body` returns False** after chain `success=True` (stale `get_job` row vs post-`finalize_job_resume` persist, or terminal hop did not persist structure-keyed body).
   - **Chain reports `success=True` without terminal hop completion** when `run_next` stops after `check_job_resume` per-hop transition already moved the job to the **`finalize_job_resume` compound label** (job looks “done” in UI section **In Progress** but batch exit correctly refuses graduation — fix is ensuring graduation runs when finalize actually completes, not moving graduation into `agent.py`).

**Out of scope:** hop order / prompts / `BUILD_CONFIG['resume_artifact_chain']['hop_task_keys']`; Generate Artifacts / Cancel on **RECOMMENDED**; cover-letter chain; `draft_cover_letter` at **CANDIDATE_REVIEW**; one-time backfill for jobs already stuck at **`BUILD_ARTIFACTS.finalize_job_resume`**; changes to AST-597 per-hop compound progression logic in `agent.py`.

**Related (context only):** [AST-595](../artifacts/ast-595-compound-build-artifacts-hop-states.md), [AST-596](../artifacts/ast-596-mid-chain-dispatch-claim-and-hop-failure-batch-release.md), [AST-597](../artifacts/ast-597-per-hop-transitions-and-agent-data-mid-chain-resume-need-to-pick-up-and-parse-daisy-chained-prompts-from-the-middle-using-agent_data-content.md), [AST-552](../artifacts/ast-552-build-artifacts-gate-and-structure-keyed-persistence.md).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Extract terminal graduation helper; harden `_run_job_artifact_entry_batch` success path; AST-538 Style D debug on graduation outcome | core |

No config, agent, dispatcher, tracker, UI, or test edits in this ticket (Betty owns test manifest at Code Complete).

---

## Stage 1: Terminal graduation helper in `consult.py`

**Done when:** A single private helper owns the terminal gate (persist check + state transition + debug), callable from the artifact batch loop only.

1. In `src/core/consult.py`, after `_artifact_entry_hop_failed` (~line 1621), add:

   ```python
   def _try_graduate_artifact_job_to_candidate_review(
       astral_job_id: str,
       *,
       debug: bool = False,
   ) -> tuple[bool, str]:
   ```

   Behavior (execute literally):

   - **Fresh row:** `row = tracker.get_job(astral_job_id)` — do **not** accept a stale claim-time `job` dict. If missing → return `(False, "job_not_found")`.
   - **Persist gate:** `tracker.job_has_persisted_resume_body(astral_job_id, None)` — pass **`None`** as `job` so the helper always re-reads DB (avoid false negative from claim snapshot).
   - If gate fails → return `(False, "persist_gate_failed")`.
   - **From-state (debug only):** `from_state = (row.get("state") or "").strip()`. When `debug`, emit Style D via `get_logger(__name__, debug_flag=True)`:
     - `debug_index(func="_try_graduate_artifact_job_to_candidate_review", index=1, total=1, identifier=astral_job_id, outcome="attempt")`
     - `debug_detail(f"from_state={from_state!r} persist_gate=pass")`
   - **Transition:** `tracker.transition_job_state([astral_job_id], "CANDIDATE_REVIEW")` inside `try/except ValueError as exc`:
     - On success → if `debug`: `debug_detail("graduation=CANDIDATE_REVIEW success")`; return `(True, "ok")`.
     - On `ValueError` → if `debug`: `debug_detail(f"graduation=failed error={exc!r} from_state={from_state!r}")`; return `(False, f"transition_failed:{exc}")`.

   ⚠️ **Decision:** Graduation stays in **`consult.py`** batch exit only (AST-597 boundary — do **not** call `transition_job_state(..., "CANDIDATE_REVIEW")` from `agent.py` after `finalize_job_resume`).

2. **`python3 -m py_compile src/core/consult.py`**

## Stage 2: Wire helper into `_run_job_artifact_entry_batch`

**Done when:** Full-chain and mid-chain dispatch entry both call the helper after `run_resume_artifact_chain_for_job` returns `success=True`; failure paths unchanged (AST-596).

1. In `_run_job_artifact_entry_batch` (~1625), replace the inline block:

   ```python
   row = tracker.get_job(aid) or job
   if not tracker.job_has_persisted_resume_body(aid, row):
       ...
   try:
       tracker.transition_job_state([aid], "CANDIDATE_REVIEW")
   except ValueError as exc:
       ...
   ```

   with:

   ```python
   ok, reason = _try_graduate_artifact_job_to_candidate_review(aid, debug=debug)
   if not ok:
       logger.warning(
           "[%s] terminal graduation failed reason=%s entry_task_key=%s",
           aid,
           reason,
           entry_task_key,
       )
       _artifact_entry_hop_failed(aid)
       errors += 1
       continue
   row = tracker.get_job(aid) or job
   ```

2. **Preserve** existing behavior after graduation:
   - `passed += 1`
   - When `entry_task_key == "contemplate_job"`: `await _run_cover_letter_for_job(aid, row, base_ctx, debug)` (unchanged).

3. **Do not change:**
   - Chain failure branch (`not r.get("success")`) — still `_artifact_entry_hop_failed` only, no `BUILD_FAILED`.
   - `_resume_artifact_dispatch_row_ok` / `run_consult_task` routing.
   - `JOB_ARTIFACT_ENTRY_TASK_KEYS`, `BUILD_CONFIG`, or compound `JOB_STATES`.

4. Grep `src/core/consult.py` for any remaining direct `transition_job_state(..., "CANDIDATE_REVIEW")` inside `_run_job_artifact_entry_batch` — there must be **one** call site (inside the helper only).

5. **`python3 -m py_compile src/core/consult.py`**

6. **`python3 -c "from src.core import consult; print('ok')"`**

## Stage 3: Verify compile + Betty handoff note

**Done when:** Product imports cleanly; Linear comment lists Betty manifest targets (no `tests/` edits in this ticket).

1. Post **Code Complete** comment for Betty with manifest targets:

   | # | Area | Test (new or extend) |
   |---|------|----------------------|
   | 1 | Terminal graduation after **finalize** entry | `tests/component/core/test_consult.py` — new `test_artifact_entry_batch_graduates_after_finalize_hop_entry`: mock chain success, persist gate pass, assert `transition_job_state(["job-x"], "CANDIDATE_REVIEW")` once when `entry_task_key="finalize_job_resume"` |
   | 2 | Full-chain first-hop regression | Extend or duplicate AST-371 pattern with `entry_task_key="anticipate_scan"` — graduation still called |
   | 3 | Persist gate failure | Assert **no** `CANDIDATE_REVIEW` transition; `release_job_dispatch_claim` called (AST-596 pattern) |
   | 4 | Transition failure | Mock `transition_job_state` raising `ValueError` — job stays unreleased logic unchanged; assert warning path / no `passed` increment |
   | 5 | AST-597 regression | `tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions` — no changes expected; include in narrow run |

   Narrow run command for Betty:

   ```bash
   ./scripts/testing/run_component_tests.sh \
     tests/component/core/test_consult.py::TestAst371ResumeArtifactDispatch \
     tests/component/core/test_consult.py::TestAst534DispatchTaskKeyHonesty \
     tests/component/core/test_agent.py::TestAst597MidChainResumeHydrationAndTransitions
   ```

2. Susan UAT note (Linear comment after Tests Passed, not in plan execution): confirm Manage Tasks resume chain **`run_next`** graph reaches **`finalize_job_resume`** terminal hop so batch exit runs after real finalize persist.

## Execution contract (for the developer agent)

- Execute stages in order. **Stop** on ambiguity — comment on **AST-788** parent with 🛑 template from **plan-child**.
- **Do not** edit `src/core/agent.py` per-hop transitions, `src/utils/config.py`, `src/core/dispatcher.py`, `src/core/tracker.py`, UI, or `tests/`.
- **Do not** add backfill / admin repair for stuck jobs.
- When `transition_failed:` reason appears in logs during build verification, **stop** and comment with observed `from_state` — do not patch `JOB_STATES` in this ticket.

Blocking questions use parent **AST-788**:

```
🛑 Stage N blocked: <one-line summary>
Step: <step number and text>
Issue: <what's ambiguous, missing, or broken>
Proposed resolutions: <2-3 options, or "need guidance">
```

## Self-Assessment

**Scope — `Single-Component`**  
One core module (`src/core/consult.py`) — terminal graduation helper and batch-loop wiring only; no config or agent hop changes.

**Conf — `Medium`**  
AST-552/596/597 established the batch-exit contract and the code path already exists inline; this ticket hardens persist read + transition error surfacing and adds debug, but build must confirm which failure mode UAT hit before treating the helper wiring as sufficient.

**Risk — `HIGH`**  
Incorrect graduation (promote without persist, or skip after success) breaks Recommended Jobs **Ready** vs **In Progress** UX and candidate-facing artifact gates; wrong fix in `agent.py` would double-transition or fight AST-597 per-hop states.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single `_try_graduate_artifact_job_to_candidate_review` replaces duplicated persist + transition logic in the batch loop. |
| §1.5.1 debug | Style D via `get_logger(..., debug_flag=debug)` on graduation attempt/outcome only when `debug=True`; production warning on failure uses existing `logger.warning`. |
| §2.1 config | No new config keys; `CANDIDATE_REVIEW` and compound states read-only via existing registry. |
| §2.4 batch | Failure still `_artifact_entry_hop_failed` (claim release); success graduation before optional cover-letter side effect. |
| §2.6 state machine | Transitions only through `tracker.transition_job_state` to **`CANDIDATE_REVIEW`**; no new states. |
| §3.3 imports | `consult.py` → `tracker` only; lazy `agent` import in batch helper unchanged. |
| §3.5 naming | `_try_graduate_*` prefix matches consult artifact batch private helpers. |

No unresolved conflicts with ASTRAL_CODE_RULES.

---

## Review (build)

**Built:** `origin/sub/AST-788/AST-789-graduate-build-artifacts-to-candidate-review` @ `35326f8`

Stage 1–2: `_try_graduate_artifact_job_to_candidate_review` — fresh DB persist gate (`job_has_persisted_resume_body(..., None)`), `CANDIDATE_REVIEW` transition, AST-538 Style D debug; `_run_job_artifact_entry_batch` calls helper with structured failure logging. Component tests deferred to Betty per build-child test-tree ban.

## Radia review (2026-06-24)

**Ref:** `origin/dev...origin/sub/AST-788/AST-789-graduate-build-artifacts-to-candidate-review` @ `131dae4`

### What's solid

- **Plan fidelity (Stage 1–2):** `_try_graduate_artifact_job_to_candidate_review` matches spec — fresh `tracker.get_job`, persist gate via `job_has_persisted_resume_body(..., None)`, structured `(ok, reason)` tuple, single `transition_job_state(..., "CANDIDATE_REVIEW")` call site (grep confirms one in `consult.py`).
- **Batch wiring:** `_run_job_artifact_entry_batch` calls helper after chain success; failure logs `reason=` + `entry_task_key=` before `_artifact_entry_hop_failed`; cover-letter side effect preserved for `contemplate_job`.
- **§1.5.1 debug (AST-538):** Style D `debug_index` (universal `index 1/1`) + `debug_detail` on attempt/success/failure when `debug=True`; no contract emission when `debug=False`.
- **§2.4 / §2.6:** Claim release on graduation failure unchanged; transitions only through `tracker.transition_job_state`; graduation stays in `consult.py` (AST-597 boundary honored).
- **Tests (Betty manifest):** `TestAst789TerminalGraduation` covers finalize entry, first-hop regression, transition failure + claim release, and fresh-persist `None` passthrough; persist-gate failure covered by existing `TestAst371ResumeArtifactDispatch::test_artifact_entry_batch_empty_persist_releases_claim`; `TestAst534DispatchTaskKeyHonesty` updated with `get_job` mock for post-helper refresh path.

### Issues

| Severity | Location | Finding |
| --- | --- | --- |
| **advisory** | Plan Self-Assessment | **Risk HIGH / Conf Medium** — code hardens the known batch-exit path; Susan UAT still needed to confirm which failure mode fired in production (`transition_failed:` vs `persist_gate_failed` vs chain-success-without-finalize). Not a code **fix-now**; watch logs on next resume-artifact run with `debug=True`. |

No **fix-now** or **discuss** items.

### Recommended actions

| Priority | Action |
| --- | --- |
| resolve-child | None — proceed to User Testing when parent lane clears. |
| UAT | Confirm Manage Tasks resume chain reaches `finalize_job_resume` terminal hop and job lands in **Ready** (`CANDIDATE_REVIEW`); if stuck, check warning for `reason=persist_gate_failed` or `reason=transition_failed:…`. |

## Resolution

**Resolved:** 2026-06-24 (Hedy)

Radia review @ `adecb4d` — **no fix-now** or **discuss** items. No product commits in resolve pass; publish ref unchanged at `adecb4d` (product @ `35326f8`, tests @ `131dae4`).

**§9a dry-run:** `origin/sub/AST-788/AST-789-graduate-build-artifacts-to-candidate-review` merges cleanly into `origin/dev` and `origin/ftr/AST-788-build-artifacts-substates-do-not-graduate`.

**Advisory accepted:** Susan UAT on parent AST-788 should confirm full chain graduation to **Ready**; use `debug=True` and graduation warning `reason=` if still stuck.
