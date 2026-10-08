<!-- linear-archive: AST-1760 archived 2026-10-07 -->

## Linear archive (AST-1760)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1760/all-x-scored-grades-retry-holding-when-job-analysis-comes-back-as-all  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1759 — When job analysis comes back as all X, retry  
**Blocked by / blocks / related:** parent: AST-1759

### Description

## What this implements

Owns the scored consult apply gate for all-literal-`X` complete sets and the raise-into-existing-fail-dest wiring so first strike retries and second strike technical-fails. Does **not** change binary all-`X` → fail, prompt copy, or invent new holdings.

## Citations

`patt.task.dispatch-retry`, `patt.entity.batch-processing`, `patt.entity.batch-criteria`, `astral.batch.claim-process-release`, `stat.logging.debug`

## Scope

`src/core/consult.py` — **modified** — gate all-literal-`X` on the scored apply / `_render_score` path into the existing batch fail-dest / retry routing (same family as incomplete grade sets); leave binary `_render_pass_fail` all-`X` → fail alone. | `src/core/consult.py` — new scored-path check after the complete-set gate (or equivalent raise site): when every grade row’s letter is literal `X`, raise into the caller’s existing bad-grades / process-failure path so `_consult_batch_fail_dest` picks primary → `retry_state` holding, holding → `error_state`. Must not return `pass_state` and must not land `fail_state` on first strike for this case. | `src/core/consult.py` — no change to `_render_pass_fail` all-literal-`X` → `fail_state`; no change to partial-`X` / counted-set scoring math; no new JOB_STATES / TASK_CONFIG holdings (reuse existing `*_RETRY` companions).

## Acceptance criteria

- [X] Replay a `meteorite_like` batch where one job’s decoded grades are a complete set of literal `X` and siblings have normal letters: the all-`X` job’s state is `METEORITE_PASSED_GET_RETRY` (not `METEORITE_PASSED_LIKE`, not `METEORITE_FAILED_LIKE` on first strike); siblings still reach pass or fail from ordinary scoring. **Fail if** the all-`X` job is `METEORITE_PASSED_LIKE` or `METEORITE_FAILED_LIKE` after that first apply.
- [X] From `METEORITE_PASSED_GET_RETRY`, a second all-literal-`X` apply lands `METEORITE_FAILED_TECHNICAL_LIKE` (existing second-strike fail-dest). **Fail if** the job remains on the retry holding or returns to `METEORITE_PASSED_GET` without technical fail.
- [X] Unit / component: scored apply with score floor `0.0` and every grade letter `X` never returns / transitions to that task’s `pass_state`. **Fail if** `_render_score` or apply returns `pass_state` for an all-literal-`X` set at floor `0.0`.
- [X] A complete set with at least one non-`X` letter still scores and may pass or fail under existing floor rules (partial-`X` unchanged). **Fail if** any single `X` among otherwise real grades forces the retry holding.
- [X] `_render_pass_fail` with all literal `X` still returns that task’s `fail_state` (binary path unchanged). **Fail if** binary all-`X` routes to a `*_RETRY` holding.

## Boundaries

- [X] Does **not** change binary `_render_pass_fail` all-literal-`X` → `fail_state`.
- [X] Does **not** invent new JOB_STATES / TASK_CONFIG holdings.
- [X] Does **not** change prompt / output-contract copy.
- [X] Does **not** change partial-`X` or mixed no-signal scoring math.

## Notes for planning

Citations as above. Reuse incomplete-grade fail-dest family (AST-1155). score_floor `0.0` on `meteorite_like` is the repro path that currently passes all-X into upshot.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1759-when-job-analysis-comes-back-as-all-x-retry`, child `sub/AST-1759/<this-id>-all-x-scored-grades-retry-holding`. Created at dispatch-parent.

## QA test manifest

1. Helper + subclass + empty/partial: `tests/component/core/test_consult.py::TestAst1760AllLiteralXRetry::test_require_not_all_literal_x_gate`
2. Fail-dest meteorite_like matrix: `tests/component/core/test_consult.py::TestAst1760AllLiteralXRetry::test_fail_dest_meteorite_like_matrix`
3. Floor 0.0 all-X never pass (AC3): `tests/component/core/test_consult.py::TestAst1760AllLiteralXRetry::test_apply_scored_all_x_never_pass_at_floor_zero`
4. Partial-X still scores (AC4): `tests/component/core/test_consult.py::TestAst1760AllLiteralXRetry::test_apply_scored_partial_x_still_scores`
5. Binary all-X fail (AC5): `tests/component/core/test_consult.py::TestAst1760AllLiteralXRetry::test_render_pass_fail_all_x_still_fail_state`
6. First strike holding (AC1): `tests/component/core/test_consult.py::TestAst1760AllLiteralXRetry::test_render_verdict_meteorite_like_all_x_first_strike`
7. Second strike technical (AC2): `tests/component/core/test_consult.py::TestAst1760AllLiteralXRetry::test_render_verdict_meteorite_like_all_x_second_strike`
8. Mixed batch sibling pass (AC1): `tests/component/core/test_consult.py::TestAst1760AllLiteralXRetry::test_batch_mixed_all_x_sibling_still_passes`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst1760AllLiteralXRetry \
  -q
```

**Bible path shasum:** `docs/test-bible/core/consult.md` @ `63da37797fba536fceb8ab9fe38c32d14361d56c  -` (`git show origin/sub/AST-1759/AST-1760-all-x-scored-grades-retry-holding:docs/test-bible/core/consult.md | shasum`)

### Comments

#### radia — 2026-09-21T20:52:57.105Z
[code-rubric] PROCEED (Commit: bb69043b) All-X retry holding clean

#### betty — 2026-09-21T20:49:19.691Z
`origin/sub/AST-1759/AST-1760-all-x-scored-grades-retry-holding` @ `85aaf439` · all-X retry coverage

#### joan — 2026-09-21T20:38:32.619Z
[plan-rubric] PROCEED (Commit: 6a4a891) raise before score, reuse fail-dest

#### hedy — 2026-09-21T20:36:31.969Z
`origin/sub/AST-1759/AST-1760-all-x-scored-grades-retry-holding` @ `6a4a8918102f17b97c711940fff1f65010686664` · plan ready

---

# AST-1760 — All-X scored grades → retry holding

**Linear:** [AST-1760](https://linear.app/astralcareermatch/issue/AST-1760/all-x-scored-grades-retry-holding-when-job-analysis-comes-back-as-all-x)  
**Parent:** [AST-1759](https://linear.app/astralcareermatch/issue/AST-1759/when-job-analysis-comes-back-as-all-x-retry) — When job analysis comes back as all X, retry  
**Project:** Astral Consult  
**Publish ref:** `sub/AST-1759/AST-1760-all-x-scored-grades-retry-holding`

Scored Analysis apply currently treats a complete grade set of literal `X` as a normal score of `0.0`. When the dispatch score floor is `0.0` (`meteorite_like` and peers), that set passes into the next hop / upshot. This ticket gates all-literal-`X` on the scored apply path into the existing incomplete-grade fail-dest family (AST-1155): first strike → trigger `retry_state` holding, second strike → `error_state`. Binary `_render_pass_fail` all-`X` → `fail_state` stays unchanged. No new holdings, no prompt copy, no partial-`X` math change.

## UAT fitness

- **AC restored:** Parent AC1 — replay a `meteorite_like` batch where one job’s decoded grades are a complete set of literal `X` and siblings have normal letters: the all-`X` job’s state is `METEORITE_PASSED_GET_RETRY` (not `METEORITE_PASSED_LIKE`, not `METEORITE_FAILED_LIKE` on first strike); siblings still reach pass or fail from ordinary scoring. Parent AC2 — from `METEORITE_PASSED_GET_RETRY`, a second all-literal-`X` apply lands `METEORITE_FAILED_TECHNICAL_LIKE`.
- **Correct outcome:** An all-`X` scored Analysis job gets one more grading attempt on the existing `*_RETRY` holding, then technical-fails on second strike — it must not advance to upshot / next Analysis hop on the first all-`X` apply.
- **Sibling check:** This epic is a single child (monolith). Contracts that must still hold: binary `_render_pass_fail` all-literal-`X` → `fail_state` (AC5); partial-`X` / mixed no-signal scoring unchanged (AC4); incomplete/extra sets still raise `IncompleteGradeSetError` into the same fail-dest (AST-1155). Verify by not touching `_render_pass_fail`’s all-`X` branch, by requiring *every* letter to be literal `X` (not `_effective_no_signal_for_score`), and by subclassing the incompleteness error so existing catch sites stay live.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Raising `score_floor` above `0.0` for `meteorite_like`, or mapping all-`X` to `fail_state` on the scored path, would either change batch criteria (`patt.entity.batch-criteria` — floor stays dispatch_task-owned) or skip the retry holding. Floor-math “soft fail” (`score < floor`) also cannot catch `0.0` at floor `0.0`. The correct fix is raise-into-existing `_consult_batch_fail_dest`, same family as incomplete grades.

## Canon Scope (patterns read in full)

| id | role |
|----|------|
| `patt.task.dispatch-retry` | One more try via sibling `*_RETRY` holding; second strike terminal — no bespoke all-X queue |
| `patt.entity.batch-processing` | Per-entity process failure inside claim → process → release; siblings keep their own outcomes |
| `patt.entity.batch-criteria` | Claim shape / score floor stay dispatch_task-owned; do not invent a parallel floor rule for all-X |
| `astral.batch.claim-process-release` | Failure stays inside the claimed batch process path; no carve-out that skips release |
| `stat.logging.debug` | If a debug line names the all-literal-`X` route, use `logger.debug` (ContextVar-gated); do not wrap in `if debug` |

## Explicit scope gate

Ticket **Scope** names only `src/core/consult.py`: scored-path all-literal-`X` check after the complete-set gate (or equivalent raise site) → raise into existing bad-grades / process-failure path so `_consult_batch_fail_dest` picks primary → `retry_state`, holding → `error_state`. No `_render_pass_fail` change; no partial-`X` math change; no new `JOB_STATES` / `TASK_CONFIG` holdings. Every Files Changed row and Stage step below stays inside that Scope.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | All-literal-`X` scored-path gate + error type + debug line; wire after complete-set on scored apply | core |

## Stage 1: Scored all-literal-`X` → existing fail-dest

**Done when:** A complete scored grade set where every letter is literal `X` raises into the same caller paths as `IncompleteGradeSetError`, so `_consult_batch_fail_dest` sends primary → retry holding and holding → `error_state`. `_render_score` is never reached for that set on the scored apply path. Binary `_render_pass_fail` all-`X` still returns `fail_state`. A complete set with any non-`X` letter still scores under existing floor rules.

1. In `src/core/consult.py`, immediately after `class IncompleteGradeSetError`, add:

   ```python
   class AllLiteralXGradeSetError(IncompleteGradeSetError):
       """Complete scored grade set is all literal X — no usable signal (AST-1760)."""
   ```

   Subclass so existing `except IncompleteGradeSetError` in `render_verdict` and the `isinstance(e, IncompleteGradeSetError)` branch in `_run_batch_consult` catch all-`X` without new except clauses.

2. In `src/core/consult.py`, adjacent to `_require_complete_grade_set`, add:

   ```python
   def _require_not_all_literal_x(grades: list) -> None:
       """Raise AllLiteralXGradeSetError when every grade letter is literal X (non-empty set)."""
       if grades and all(isinstance(g, dict) and g.get("grade") == "X" for g in grades):
           raise AllLiteralXGradeSetError(
               f"_render_score: all literal X grades ({len(grades)} vectors)"
           )
   ```

   ⚠️ **Decision:** Gate on **letter `== "X"` only**, not `_effective_no_signal_for_score` (confidence-1). Parent / child AC4: a set with at least one non-`X` letter must still score; mixed no-signal must not force the retry holding.

   ⚠️ **Decision:** Require `grades` truthy before `all(...)` so an empty list does not vacuously raise (empty is already incomplete / empty-fail on other paths).

3. In `_apply_render_verdict_decoded_job`, in the `mode == "scored"` branch, **after** `_require_complete_grade_set(rubric_criteria, grades)` and **before** `to_state, score = _render_score(...)`, call `_require_not_all_literal_x(grades)`.

   ⚠️ **Decision:** Do **not** put this raise inside `_render_score` itself. `_render_score` is also used for informational scores on binary qualify / evaluate_jd and by `roster.py` prefilter (out of this ticket’s Files Changed). Raising from `_render_score` would either break binary all-`X` → `fail_state` (AC5) when evaluate_jd’s uncaught call aborts into `bad_grades`, or force out-of-scope roster edits. The scored Analysis apply path (`_apply_render_verdict_decoded_job` → `_consult_scored_dispatch_batch_encoded` / `render_verdict`) is the raise site named by Scope.

4. In `_run_batch_consult`’s `except Exception` on `process_fn`, when `isinstance(e, AllLiteralXGradeSetError)` (or keep the existing `IncompleteGradeSetError` branch — subclass is enough), emit a dedicated `logger.debug` line that names the all-literal-`X` route, Style-D sibling to incomplete-grade detail — e.g. include `func`, identifier, dest from `_consult_batch_fail_dest`, and that the reason is all literal `X`. Use `logger.debug` only (no `if debug` / no `logger.info("[DEBUG]")`) per `stat.logging.debug`. Reuse `_debug_incomplete_grade_set` only if its message shape stays honest; prefer a one-line `logger.debug("all literal X grade set …")` rather than overloading the incomplete-vector missing/unexpected fields with empty lists.

5. Do **not** edit `_render_pass_fail`’s `all(g.get("grade") == "X" for g in grades)` → `fail_state` branch. Do **not** add `JOB_STATES` / `TASK_CONFIG` keys. Do **not** change `_phase_score_breakdown` / counted-set math for partial-`X`. Do **not** change `score_floor` on any dispatch_task.

6. Smoke-check on the epic worktree (builder may use a one-off Python snippet under `debug/spikes/` if needed — never commit spikes):

   - `_consult_batch_fail_dest("METEORITE_PASSED_GET", "METEORITE_FAILED_TECHNICAL_LIKE")` → `METEORITE_PASSED_GET_RETRY`
   - `_consult_batch_fail_dest("METEORITE_PASSED_GET_RETRY", "METEORITE_FAILED_TECHNICAL_LIKE")` → `METEORITE_FAILED_TECHNICAL_LIKE`
   - `_require_not_all_literal_x([{"vector": "A", "grade": "X"}, {"vector": "B", "grade": "X"}])` raises `AllLiteralXGradeSetError`
   - `_require_not_all_literal_x([{"vector": "A", "grade": "X"}, {"vector": "B", "grade": "C"}])` does not raise
   - `_render_pass_fail` with all literal `X` still returns that task’s `fail_state`

**Commit:** `code(AST-1760): all-X scored grades → retry holding`

## Execution contract

- Execute steps in order; do not skip, reorder, or add files outside the Files Changed table.
- Ambiguity or codebase drift → stop, comment on parent AST-1759 with the Stage-blocked template, wait.
- Stage complete only after commit on epic worktree + `git push origin HEAD:sub/AST-1759/AST-1760-all-x-scored-grades-retry-holding`.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1760
**Overall:** APPROVED
**Corpus:** 2ac86c3f693409c364f8630a97198c8dbfa9c6f3
**Publish ref tip:** `6a4a8918102f17b97c711940fff1f65010686664`

## Canon scores

| id | grade | effort | one-line |
|----|-------|--------|----------|
| patt.task.dispatch-retry | A | | |
| patt.entity.batch-processing | A | | |
| patt.entity.batch-criteria | A | | |
| astral.batch.claim-process-release | A | | |
| stat.logging.debug | A | | |

## Traceability

AC1→Stage1(1–3, smoke fail-dest); AC2→Stage1(1–3, smoke holding→terminal); AC3→Stage1(2–3, Done-when); AC4→Stage1(2⚠,5); AC5→Stage1(3⚠,5, smoke)

## Findings

### acceptable

- **Location:** Plan — Estimate
- **Finding:** No formal self-assessment / conf block; only `Confirm Chuckles estimate: 2 — agree`.
- **Recommendation:** Acceptable for this slice; Betty owns AC3 unit/component verification at qa-child.

### discuss

- **Location:** Stage 1 step 4 vs `render_verdict` handler (~1464–1474)
- **Finding:** Dedicated all-literal-`X` `logger.debug` is scoped to `_run_batch_consult`; single-entity scored applies (`len(entities)==1` → `render_verdict`) would still hit `_debug_incomplete_grade_set` with incomplete-grade field shape if the engineer relies on the subclass-only path.
- **Recommendation:** On build, either add a parallel all-`X` debug branch in `render_verdict`'s `IncompleteGradeSetError` handler or implement step 4's preferred one-line `all literal X grade set …` in `_run_batch_consult` only — behavior is already correct via `_consult_batch_fail_dest`; message honesty is the only delta.

context_tokens≈42000

## Review stub (build)

**Publish ref:** `sub/AST-1759/AST-1760-all-x-scored-grades-retry-holding`  
**Tip:** `eec4856b`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `eec4856b` | All-X scored grades → retry holding |

## Radia review

[code-rubric]
**Ticket:** AST-1760
**Publish ref:** `bb69043b4749aab68c2327290e85ed2c0f07abcf`
**Corpus:** `2ac86c3f693409c364f8630a97198c8dbfa9c6f3`
**Overall:** CLEAN

## Canon scores

| id | grade | effort | one-line |
|----|-------|--------|----------|
| patt.task.dispatch-retry | A | | |
| patt.entity.batch-processing | A | | |
| patt.entity.batch-criteria | A | | |
| astral.batch.claim-process-release | A | | |
| stat.logging.debug | A | | |

## Column diff vs plan stage

(aligned)

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Location:** `src/core/consult.py` — `_run_batch_consult` `except Exception` (~1708–1731)
- **Finding:** `AllLiteralXGradeSetError` still flows through the existing `logger.exception` + `continue` path after the dedicated `logger.debug` line — same as `IncompleteGradeSetError` before batch fail-dest transition.
- **Recommendation:** Acceptable; matches AST-1155 batch bad-grade handling. No change required unless Susan wants all-literal-X to suppress the exception traceback in logs.

## What's solid

- Subclass + raise-site design reuses AST-1155 fail-dest wiring without new holdings or `score_floor` edits.
- Gate is correctly scoped to `_apply_render_verdict_decoded_job` scored branch (after complete-set, before `_render_score`); binary `_render_pass_fail` and informational `_render_score` callers stay untouched.
- Dedicated all-literal-X `logger.debug` branches land in both `render_verdict` and `_run_batch_consult` — closes Joan’s plan-stage discuss item.
- `TestAst1760AllLiteralXRetry` covers all eight manifest rows: gate, fail-dest matrix, floor-0 never-pass, partial-X scoring, binary AC5, first/second strike, mixed-batch sibling pass.

## Recommended actions

(none — artifact complete; Chuckles may advance to Review Posted)

---
