# AST-446 — Investigate suspicious local run of evaluate_jd: pre-agent JD readiness gate

**Linear:** [AST-446 — Investigate suspicious local run of evaluate_jd: pre-agent JD readiness gate](https://linear.app/astralcareermatch/issue/AST-446/investigate-suspicious-local-run-of-evaluate-jd-pre-agent-jd-readiness-gate)  
**Parent:** [AST-441](https://linear.app/astralcareermatch/issue/AST-441/investigate-suspicious-local-run-of-evaluate-jd)  
**Depends on:** [AST-445](https://linear.app/astralcareermatch/issue/AST-445/investigate-suspicious-local-run-of-evaluate-jd-findings-and-fix-plan) fix plan (§ Fix plan for AST-446 in findings doc)  
**Feature ref:** `sub/AST-441/AST-446-investigate-suspicious-local-run-of-evaluate-jd-pre-agent-jd-readiness-gate` (origin only)

## Summary

Phase 2 of **AST-441**: implement pre-agent JD readiness in `evaluate_jd_batch` so empty/short `job_description` never reaches `do_task`, not-ready jobs transition to **`PASSED_JOBLIST`** with `jd_readiness_skip` metadata, and repro batch shape (37 empty + 1 populated) no longer produces mass `ERROR_EVALUATE_JD` from agent omission.

---

## Execution contract

Do not change dispatcher claim rules. Implement fix plan from **AST-445** findings unless Susan overrides in **AST-445** comments before **Plan Approved**. If findings doc missing on branch, stop and 🛑 block on **AST-445**.

---

## Files changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `evaluate_jd` readiness keys; extend `PASSED_JOBLIST.prior_states` | utils |
| `src/core/consult.py` | Partition jobs in `evaluate_jd_batch`; skip agent for not-ready | core |
| `tests/test_evaluate_jd_readiness.py` | New: fixture batch 37 empty + 1 populated (mock `do_task`) | tests |

---

## Stage 1: Config + legal transition target

**Done when:** `CONSULT_CONFIG["evaluate_jd"]` includes readiness keys and `PASSED_JOBLIST` accepts transitions from `JD_READY` / `JD_READY_RETRY`.

1. In `src/utils/config.py`, under `CONSULT_CONFIG["evaluate_jd"]`, add:
   - `"min_jd_chars": 80`
   - `"not_ready_state": "PASSED_JOBLIST"`
2. In `JOB_STATES["PASSED_JOBLIST"]`, set `"prior_states": ["VALID_TITLE", "VALID_TITLE_RETRY", "JD_READY", "JD_READY_RETRY"]` (per AST-445 fix plan — required for repro batch).
3. Do **not** add a new named state in this ticket.

---

## Stage 2: Readiness gate in `evaluate_jd_batch`

**Done when:** Unit-level manual run shows skipped jobs never call `do_task`.

1. In `src/core/consult.py`, at top of `evaluate_jd_batch` (after `cfg = CONSULT_CONFIG[task_key]`):

```python
def _jd_ready(job: dict, min_chars: int) -> bool:
    jd = ((job.get("job_data") or {}).get("job_description") or "").strip()
    return len(jd) >= min_chars
```

2. Read `min_chars = cfg.get("min_jd_chars", 80)` and `not_ready_state = cfg.get("not_ready_state", "PASSED_JOBLIST")`.
3. Split `jobs` into `ready_jobs` and `not_ready_jobs`.
4. For each `not_ready_jobs` entry:
   - `aid = job["astral_job_id"]`
   - `tracker.save_job_data(aid, {"jd_readiness_skip": {"reason": "empty_or_short_jd", "chars": len(...), "batch_id": batch_id}})`
   - `_transition_job_state_for_task(task_key, [aid], not_ready_state, score=None)`
   - `logger.info("  %s -> %s [jd readiness skip]", title or aid, not_ready_state)`
5. If `not_ready_jobs` and `ready_jobs` both non-empty, only pass `ready_jobs` to existing `_run_batch_consult(...)` call (reuse inner `assemble`/`process` closures unchanged).
6. If `ready_jobs` is empty:
   - Return `{"success": True, "passed": 0, "failed": 0, "total": len(jobs), "skipped": len(not_ready_jobs)}` — **do not** call `_run_batch_consult`.
7. Merge `skipped` count into return dict when `_run_batch_consult` runs (add key on result dict).

⚠️ **Decision:** Not-ready jobs are **not** counted in `_run_batch_consult` `missing` / `ERROR_EVALUATE_JD` paths.

---

## Stage 3: Regression test

**Done when:** `pytest tests/test_evaluate_jd_readiness.py -q` passes.

1. Add `tests/test_evaluate_jd_readiness.py`:
   - Build 38 job dicts in `JD_READY_RETRY` shape: 37 with `job_data: {}` or empty `job_description`, 1 with `job_description` ≥ 80 chars.
   - Patch `do_task` (or `_run_batch_consult`'s `do_task`) to assert called once with `batch_size` 1 (or live_content contains only one JD block).
   - Patch `tracker.save_job_data` / `_transition_job_state_for_task` to capture transitions.
   - Assert 37 transitions to `PASSED_JOBLIST` (or configured `not_ready_state`), 0 to `ERROR_EVALUATE_JD`.
2. Follow existing async test style in repo (`pytest.mark.asyncio` if used elsewhere for consult).

---

## Stage 4: Repro verification

**Done when:** Linear comment records test command + result.

1. Run new pytest file.
2. If local DB still has repro batch, re-run dispatcher path or invoke `evaluate_jd_batch` in shell with same job set — confirm no mass `ERROR_EVALUATE_JD` on empty JDs.
3. Post Linear comment: AC 4–6 satisfied, link test file path.

---

## Self-Assessment

### Scope

**scope-Single-Component** — `evaluate_jd_batch` + config + one test module.

### Conf

**conf-high** — fix plan from **AST-445**; pattern is partition-before-call (same family as future qualify gate).

### Risk

**risk-Medium** — wrong `not_ready_state` could loop jobs through scrape/list; mitigated by using existing `PASSED_JOBLIST` and metadata blob.

---

## Self-review vs ASTRAL_CODE_RULES

- §2.6 state machine — extends `PASSED_JOBLIST.prior_states` only (no new state name).
- §2.1 config — thresholds in `CONSULT_CONFIG`.
- No claim-layer changes.

---

## Review

_Build stub — Radia appends findings at Review Posted._

## Radia review

**Reviewed:** `origin/dev`…`origin/sub/AST-441/AST-446-investigate-suspicious-local-run-of-evaluate-jd-pre-agent-jd-readiness-gate` @ `79da74cd`

### What's solid
| Area | Notes |
|------|--------|
| Gate | `min_jd_chars` / `not_ready_state` in `CONSULT_CONFIG`; `PASSED_JOBLIST.prior_states` extended; partition before `_run_batch_consult`; `jd_readiness_skip` metadata; no `do_task` when all not-ready. |
| Boundaries | No claim-layer changes; §2.6 transitions via `_transition_job_state_for_task`. |

### Issues
| Severity | Item |
|----------|------|
| **fix-now** | 0 |
| **discuss** | 1 — Plan Stage 3 **37 empty + 1 populated** mixed batch not on branch; `test_skips_short_jd_without_agent_call` proves skip path only. |
| **advisory** | 1 — Readiness reads in-memory `job_data.job_description` only (acceptable if claim path unchanged). |

### Recommended actions
| Action | Owner |
|--------|--------|
| Optional mixed-batch AC 6 test before Susan repro UAT | Betty / Susan |
| Cherry-pick doc commit | Ada |

## Resolution

**2026-05-22 — Review Posted → User Testing (Ada)**

- **fix-now:** none — gate matches AST-445 fix plan and plan Stages 1–2.
- **discuss:** AC 6 **37+1** fixture from plan Stage 3 not added (test-tree ban at build). Betty manifest covers short-JD skip + updated `TestEvaluateJdBatch` (80-char JD). Susan may request Betty add mixed-batch regression before parent **AST-441** UAT.
- **Product:** unchanged since `9a7cd012`; tests @ `79da74cd`.

---

## Revisions

```
Revision 1 — 2026-05-19
Driven by: Chuckles plan review (REVISE) on AST-446 — same PASSED_JOBLIST prior_states fix-now as AST-445.
Changes: Stage 1 now requires JOB_STATES prior_states extension before gate; defers to AST-445 fix plan table.
```
