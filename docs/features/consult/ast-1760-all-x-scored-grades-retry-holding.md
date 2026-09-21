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
