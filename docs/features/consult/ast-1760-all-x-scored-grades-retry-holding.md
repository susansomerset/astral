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

## Bug: AST-2096 — All-X second strike → fail_state _ALL_X

**Linear:** [AST-2096](https://linear.app/astralcareermatch/issue/AST-2096) (`fix` child of orphaned mini-parent [AST-2011](https://linear.app/astralcareermatch/issue/AST-2011))  
**Publish ref:** `sub/AST-2011/AST-2096-all-x-fail-state` · parent ftr `ftr/AST-2011-meteorite-grade-do-all-x` (off `origin/dev`)  
**Explicit scope:** AST-2096 `## Scope` — `src/utils/config.py` (suffix/name helper beside `retry_of`; `{fail_state}_ALL_X` job states for scored tasks) and `src/core/consult.py` (new all-X fail-destination function; `render_verdict` + `_run_batch_consult` all-X branches; count as fail). Nothing else.  
**Canon Scope:** none cited on AST-2096 / AST-2011. This block changes only the second-strike branch of Stage 1 above. The first-strike route, binary all-X, and partial-X decisions stay as they are.

### As-is

A scored all-literal-`X` grade set raises `AllLiteralXGradeSetError`, which rides the `IncompleteGradeSetError` fail-dest family (Stage 1). First strike → `retry_state` holding. Second strike (entity already on `{trigger}_RETRY`) → `error_state` (`METEORITE_FAILED_TECHNICAL_DO` for `meteorite_grade_do`). It is logged at ERROR by `_log_fail_dest` and reported as an error: `pass:27 fail:0 error:2` in somerset batch `meteorite_grade_do-87d96303`, where jobs `877c162e` and `7dace48c` hit this route.

### To-be

First strike is unchanged (→ `retry_state` holding, WARNING, counted `retried`). Second all-`X` strike → the task's `fail_state` + `_ALL_X` (`METEORITE_FAILED_DO_ALL_X`). It is logged at WARNING like any fail verdict and counted as `failed`, not as an error, so the same batch would report `pass:27 fail:2 error:0`. Plain incomplete/extra grade sets (`IncompleteGradeSetError` that is not all-X) keep today's retry → `error_state` route. `_ALL_X` jobs list under Skipped, not Processing.

### Repro

Fixture (no DB — job row + decoded response), task `meteorite_grade_do`, candidate rubric with 12 Do vectors:

```python
job = {"astral_job_id": "job-x", "state": "METEORITE_PASSED_JD_RETRY", "astral_candidate_id": "c1"}
response_job = {"astral_job_id": "job-x", "grades": [{"vector": v, "grade": "X", "confidence": 1} for v in rubric_labels]}  # all 12 vectors
```

- Batch: `_run_batch_consult("meteorite_grade_do", …, [job], …)` with a `process_fn` that calls `_apply_render_verdict_decoded_job`. Today the job transitions to `METEORITE_FAILED_TECHNICAL_DO`, the result has `bad_grades == ["job-x"]` and `failed == 0`, and the dispatcher's normalizer reports `total_errors == 1`.
- Single entity: `render_verdict("meteorite_grade_do", "job-x", …)` with `do_task` returning the same row. Today it returns `{"success": False, "to_state": "METEORITE_FAILED_TECHNICAL_DO"}`, and the single-entity dispatch branch reports `total_errors == 1`.
- Same fixture with `state: "METEORITE_PASSED_JD"` (first strike) → `METEORITE_PASSED_JD_RETRY` today. This must stay that way.

### Root cause

Stage 1 deliberately made all-X a subclass of `IncompleteGradeSetError` so it reused `_consult_batch_fail_dest(entity_state, error_state)`. That function has only one terminal, `error_state`, so there is no way to land a verdict-level fail state on the second strike. Both catch sites (`render_verdict`'s `except IncompleteGradeSetError` and `_run_batch_consult`'s `process_fn` except → `bad_grades` → `_transition_batch_consult_failures(..., error_state)`) also treat every outcome as an error: `_log_fail_dest` logs ERROR for non-retry destinations, the batch never increments `failed`, and the single-entity path returns `success: False`. No `{fail_state}_ALL_X` state exists in `JOB_STATES`, so the transition validator would reject it anyway.

### Proposed change

**1. `src/utils/config.py` — suffix + name helper, directly after `retry_of` (before `retry_base`):**

```python
ALL_X_SUFFIX = "_ALL_X"


def all_x_of(base: str) -> str:
    """Second-strike all-literal-X terminal for a scored task's fail_state (AST-2096)."""
    return f"{base}{ALL_X_SUFFIX}"
```

**2. `src/utils/config.py` — explicit `JOB_STATES` rows, immediately after the `JOB_STATES = {…}` literal closes (before the `SOURCE_ENTITY_TYPES` block):**

```python
# AST-2096: second-strike all-literal-X terminal per scored grading task — explicit rows (no validator
# changes); priors copied from the base fail_state so {trigger}_RETRY is admitted via state_prior_states.
_ALL_X_BASES = list(dict.fromkeys(
    tc["fail_state"] for tc in TASK_CONFIG.values() if tc.get("grading_mode") == "scored"
))
JOB_STATES.update({all_x_of(b): {"prior_states": list(JOB_STATES[b]["prior_states"])} for b in _ALL_X_BASES})
ALL_X_FAIL_STATES = [all_x_of(b) for b in _ALL_X_BASES]
```

This yields exactly six rows today: `FAILED_DO_ALL_X`, `FAILED_GET_ALL_X`, `FAILED_LIKE_ALL_X`, `METEORITE_FAILED_DO_ALL_X`, `METEORITE_FAILED_GET_ALL_X`, `METEORITE_FAILED_LIKE_ALL_X`. Those are the six `grading_mode == "scored"` rows, the only tasks whose apply path reaches `_require_not_all_literal_x`. Each row's `prior_states` is its base row's, e.g. `["METEORITE_PASSED_JD"]`. `state_prior_states` then also admits `retry_of(p)`, so `METEORITE_PASSED_JD_RETRY → METEORITE_FAILED_DO_ALL_X` validates with no tracker/roster/database/admin change.

⚠️ **Decision — explicit rows, not an implicit suffix.** The ticket offered both. An implicit `_ALL_X` suffix like AST-1804's `_RETRY` would need `is_registered_state`/`state_prior_states`/`registered_base` and every consumer to learn a second suffix. Explicit rows keep the validator untouched.

⚠️ **Decision — derived from `TASK_CONFIG`, not typed out.** Consult builds the destination as `all_x_of(cfg["fail_state"])`. Deriving the rows from the same `fail_state` values means the state is registered by construction, so a new scored task cannot hit "not in allowed list" at runtime. `dict.fromkeys` keeps it duplicate-free, so `SKIPPED_STATES`' "Jobs lists overlap" assert stays safe if two alias rows ever share a `fail_state`.

**3. `src/utils/config.py` — `SKIPPED_STATES`: add `*ALL_X_FAIL_STATES,` after the `"METEORITE_FAILED_LIKE", "METEORITE_FAILED_TECHNICAL_LIKE",` line.**

⚠️ **Decision — in scope as part of "register the `{fail_state}_ALL_X` job states".** AST-1974 defines Processing as every job state not on the Ready/Review/Applied/Skipped lists. Without this line, terminal `_ALL_X` jobs would count and list as Processing (in flight), which contradicts "it's a fail". It also makes them Skipped-editable like their base fail states (`api_jobs` `editable = state in SKIPPED_STATES`) and excludes them from `CANDIDATE_SKIPPED.prior_states`, the same as the base fail states. **Not** added: `JOBS_SKIPPED_SECTION_ORDER`, `JOBS_SKIPPED_SECTION_LABELS`, `JOBS_SKIPPED_BULK_RETRY_TO_STATE`, and `JOBS_SKIPPED_GRADE_FIELD`. Those are UI polish outside declared scope, and the section-order/bulk-retry assert pair would force all of them at once. `JobsSkipped.tsx` already renders unmapped skipped states as their own section (`unmappedJobStates` / `legacyStateSectionLabel`). They get no bulk-Retry button until a follow-up maps them.

**4. `src/core/consult.py` — import `all_x_of` in the `from src.utils.config import (…)` block, beside `retry_base` / `retry_of`.**

**5. `src/core/consult.py` — new function directly after `_consult_batch_fail_dest`:**

```python
def _all_x_fail_dest(entity_state: Optional[str], fail_state: str) -> str:
    """AST-2096: all-literal-X — primary → retry holding (unchanged); *_RETRY → {fail_state}_ALL_X, a fail, not error_state."""
    return JOB_STATES.get((entity_state or "").strip(), {}).get("retry_state") or all_x_of(fail_state)
```

⚠️ **Decision — standalone, not a wrapper around `_consult_batch_fail_dest`.** In-flight AST-2086 (`sub/AST-2073/AST-2086-terminal-state-rename`) adds a required `task_key` parameter to `_consult_batch_fail_dest`. A new call to it here would merge cleanly as text and then raise `TypeError` at runtime. Reading `retry_state` directly is the same one-line rule with no coupling. All six scored trigger states (`PASSED_JD`, `PASSED_DO`, `CULTURE_READY`, `METEORITE_PASSED_JD`, `METEORITE_PASSED_DO`, `METEORITE_PASSED_GET`) have a `retry_state`. A `_RETRY` state has no `JOB_STATES` row, so it resolves to `{fail_state}_ALL_X`.

**6. `src/core/consult.py` — `render_verdict`, `except IncompleteGradeSetError as e:` block.** Replace the first line (`dest = _consult_batch_fail_dest(job.get("state"), error_state)`) with:

```python
        all_x = isinstance(e, AllLiteralXGradeSetError)
        dest = (_all_x_fail_dest(job.get("state"), cfg["fail_state"]) if all_x
                else _consult_batch_fail_dest(job.get("state"), error_state))
```

Change the existing `if isinstance(e, AllLiteralXGradeSetError):` debug test to `if all_x:`, leaving the debug line itself and the `else` `_debug_incomplete_grade_set` branch untouched. Then insert this **before** `_log_fail_dest(astral_job_id, dest, str(e))`:

```python
        if all_x and not retry_base(dest):
            # Second all-X strike is a fail verdict: WARNING, and success=True so the single-entity
            # dispatch tally counts it failed (to_state != pass_state), not an error (AST-2096).
            _warn_job(astral_job_id, dest, str(e))
            _transition_job_state_for_task(agent_task, [astral_job_id], dest)
            return {"success": True, "to_state": dest, "score": None, "grades": grades_dbg}
```

The remainder (`_log_fail_dest` → transition → `{"success": False, …}`) is unchanged and still serves first-strike all-X and every plain incomplete set. The only `render_verdict` caller (`run_dispatch_task` single-entity branch, `len(entities) == 1`) already maps `success: True` with a non-pass `to_state` to `total_failed: 1`, so it needs no edit.

**7. `src/core/consult.py` — `_run_batch_consult`, `except Exception as e:` around `process_fn`.** Move `bad_grades.add(aid)` from the first line of the except to just after the `if/elif` debug block, and add the terminal branch inside the existing `if isinstance(e, AllLiteralXGradeSetError):` arm, replacing its `dest = _consult_batch_fail_dest(...)` line:

```python
            if isinstance(e, AllLiteralXGradeSetError):
                dest = _all_x_fail_dest(input_job.get("state"), cfg["fail_state"])
                logger.debug(  # existing "all literal X grade set …" line, unchanged
                    ...
                )
                if not retry_base(dest):
                    # Second all-X strike is a fail verdict, not bad grades (AST-2096).
                    _warn_job(aid, dest, f"process_fn {type(e).__name__}: {e}")
                    _transition_job_state_for_task(task_key, [aid], dest)
                    failed += 1
                    continue
            elif isinstance(e, IncompleteGradeSetError):
                _debug_incomplete_grade_set(...)  # unchanged
            bad_grades.add(aid)
            _log_fail_dest(...)  # unchanged, as is the debug traceback line + continue
```

First-strike all-X still goes into `bad_grades` → `_transition_batch_consult_failures(task_key, bad_rows, error_state)` → the same `retry_state` holding, counted in `retried`. That keeps the result's `bad_grades`/`error`/`success` fields identical to today for first strike. Terminal all-X is excluded from `bad_grades`, so it counts in `failed`; the dispatcher's `errors = total − passed − failed − retried` drops it from the error count; and it is no longer listed in the result's `bad grades on N IDs` error string. `cfg` here is the orchestration row for `task_key`, which `_consult_scored_dispatch_batch_encoded` passes as `agent_tk`: `meteorite_grade_do` itself (no `agent_task`), so `cfg["fail_state"] == "METEORITE_FAILED_DO"`.

⚠️ **Decision — no grade save on terminal all-X.** `_require_not_all_literal_x` raises before `tracker.save_job_data`, the same as Stage 1. The all-X grade blob is not persisted to `{prefix}_grades`, which the declared scope does not ask for. A terminal all-X entity is now in `processed_ids`, so its RESPONSE row gets its entity tag (AST-984), the same as any other fail verdict.

**8. Smoke-check on the epic worktree** (one-off snippet; never commit spikes):

- `all_x_of("METEORITE_FAILED_DO") == "METEORITE_FAILED_DO_ALL_X"`, and `set(ALL_X_FAIL_STATES)` equals the six names above.
- `tracker.job_state_admits_transition("METEORITE_PASSED_JD_RETRY", "METEORITE_FAILED_DO_ALL_X")` and `("METEORITE_PASSED_JD", "METEORITE_FAILED_DO_ALL_X")` are both `True`.
- `_all_x_fail_dest("METEORITE_PASSED_JD", "METEORITE_FAILED_DO") == "METEORITE_PASSED_JD_RETRY"`; `_all_x_fail_dest("METEORITE_PASSED_JD_RETRY", "METEORITE_FAILED_DO") == "METEORITE_FAILED_DO_ALL_X"`.
- `"METEORITE_FAILED_DO_ALL_X" in SKIPPED_STATES` and `not in JOBS_PROCESSING_UI_SECTIONS` states; `import src.utils.config` passes all module asserts.
- `python -m py_compile src/utils/config.py src/core/consult.py` + repo lint before commit.

**Commit:** `code(AST-2096): all-X second strike → fail_state _ALL_X`

### Blast radius

- **AST-1760 tests that assert today's broken behavior** (Betty's, not ours): `TestAst1760AllLiteralXRetry::test_render_verdict_meteorite_like_all_x_second_strike` asserts `success is False` and `to_state == METEORITE_FAILED_TECHNICAL_LIKE`. It must change to `True` / `METEORITE_FAILED_LIKE_ALL_X`. `test_fail_dest_meteorite_like_matrix` tests `_consult_batch_fail_dest`, which is unchanged, so it still passes. `test_batch_mixed_all_x_sibling_still_passes` is first strike, where `bad_grades == ["job-x"]` and the holding are unchanged, so it still passes. A batch second-strike case does not exist yet.
- **AST-1155 incomplete-grade family:** it shares both catch sites. Non-all-X `IncompleteGradeSetError` keeps `_consult_batch_fail_dest` → `error_state` and `_log_fail_dest`. Only the `all_x` arms change.
- **AST-2073 / AST-2086 (in flight, terminal-state rename):** expect textual conflicts in `config.py`, since it adds helpers beside `retry_of` and touches `JOB_STATES`/`SKIPPED_STATES`, and in `consult.py` around `_consult_batch_fail_dest`. It keeps verdict names like `METEORITE_FAILED_DO`, so `_ALL_X` derivation is unaffected. The resolver adds `task_key` only to the pre-existing `_consult_batch_fail_dest` calls; `_all_x_fail_dest` takes none. Whichever lands second resolves.
- **Consumers of `JOB_STATES` keys** gain six terminal states with no UI label: `tracker._JOB_STATE_LIST`, `legal_job_successor_states` (Skipped edit targets), `api_admin` state list (`list(JOB_STATES.keys())`), and the Skipped page legacy-section fallback. No DB enum or CHECK constraint exists.
- **Dispatch report / Linear run titles:** terminal all-X moves from `error:` to `fail:` in the "task completed" line.

### What must still hold

- AC1 (AST-1760): primary-state all-X → `retry_state` holding (e.g. `METEORITE_PASSED_GET_RETRY`, `METEORITE_PASSED_JD_RETRY`), never `pass_state` or `fail_state`/`_ALL_X` on first strike; siblings in the batch still pass or fail on their own grades.
- AC3: scored all-X at floor `0.0` never returns or transitions to `pass_state`.
- AC4: a complete set with any non-`X` letter still scores under the existing floor rules (partial-X math untouched).
- AC5 / Boundary: `_render_pass_fail` binary all-X → bare `fail_state` (no `_ALL_X`, no retry) is unchanged.
- AST-1155: plain incomplete/extra grade sets keep primary → retry → `error_state`, logged at ERROR when terminal.
- AC2 is **superseded** by this bug: the second strike now lands `{fail_state}_ALL_X`, not `error_state`.
- `patt.task.dispatch-retry`: exactly one retry before terminal, with no new holding states.
- Module-load asserts in `config.py`: "Jobs lists overlap", Processing-sections exclusion, and skipped bulk-retry/section-order equality all still pass.


## Radia review — AST-2096 (review-fix)

[code-rubric]
**Ticket:** AST-2096
**Publish ref:** `a135a38e31c838f8d862bdaa89fe08fd355d1fbb` (`origin/sub/AST-2011/AST-2096-all-x-fail-state`)
**Corpus:** `2d1b73da19` (`canon/canon_clerk.py index`; `docs/canon-index.md` absent on publish ref)
**Overall:** CLEAN

## Fix-specific checks

**`[bug-repro]`:** OK — Betty F4 + manifest `docs/test-bible/core/consult.md` § AST-2096 pin **To-be** (not tautologies):

| # | Test | Pin |
|---|------|-----|
| 1 | `TestAst1760AllLiteralXRetry::test_render_verdict_meteorite_like_all_x_second_strike` | `success True`, `to_state == METEORITE_FAILED_LIKE_ALL_X`, transition not `error_state` |
| 2 | `…::test_batch_all_x_second_strike_counts_failed` | `failed==1`, `retried==1`, `passed==1`, `bad_grades==["job-x1"]`, `job-x2` → `METEORITE_FAILED_LIKE_ALL_X`, no `error_state` transition |
| 3–5 | `TestAst2096AllXFailStates` (3) | six rows, priors = base, `all_x_of` / `ALL_X_FAIL_STATES` derived from scored `fail_state`s, `SKIPPED` + processing excluded |

`TestAst1808RetryRegistryPurge::test_prior_snapshot_pinned` AST-2096 block matches Hedy’s qa-handoff values (post–Betty merge-tests). Pre-fix failure mode matches **Root cause** / **As-is** (`success False`, `error_state`, `failed==0`, missing `_ALL_X` rows).

**`## What must still hold`:** OK — traced against `origin/ftr/AST-2011-meteorite-grade-do-all-x...origin/sub/...` product diff (`src/utils/config.py`, `src/core/consult.py` only):

- **AC1:** First-strike all-X still routes via `retry_state` / `bad_grades` (`test_batch_all_x_second_strike_counts_failed` job-x1; existing first-strike + mixed-batch tests untouched).
- **AC3 / AC4 / AC5:** No change to floor scoring, partial-X math, or `_render_pass_fail` binary all-X path (`test_render_pass_fail_all_x_still_fail_state` not in product diff).
- **AST-1155:** Non–`AllLiteralXGradeSetError` still uses `_consult_batch_fail_dest` + `_log_fail_dest` in both catch sites.
- **`patt.task.dispatch-retry` (plan contract):** `_all_x_fail_dest` = primary `retry_state` or terminal `all_x_of(fail_state)`; no extra holding states.
- **Config asserts:** `ALL_X_FAIL_STATES` on `SKIPPED_STATES`; rows derived with `dict.fromkeys` from scored `fail_state`s.

## Canon scores

(no frozen canon list on Linear Description or plan-fix **Canon Scope: none cited** — fix-lane empty scored set; not §5.3 ESCALATE because scope was explicitly declared empty on AST-2096 / AST-2011)

## Column diff vs plan stage

no plan-stage scores attached (Joan `[board-joan] CANON: OK` at F2 only; no F3 `validate-plan` per-id column)

## Frame diff

(none)

## Findings

### discuss

- **Location:** Linear Description — Canon Scope  
  **Finding:** No frozen directive ids; plan **What must still hold** cites `patt.task.dispatch-retry` as behavioral contract only.  
  **Recommendation:** No scope amendment unless Archie wants explicit ids on every fix bug.  
  **Default:** Proceed on empty scored set; dispatch-retry behavior verified in fix-specific §5.2.

### advisory

- **Location:** `git diff origin/ftr/AST-2011-meteorite-grade-do-all-x...origin/sub/AST-2011/AST-2096-all-x-fail-state`  
  **Finding:** Full three-dot diff is 72 files (+6792 lines), mostly `docs/features/**` (66 paths) from `merge-tests(AST-2096)` / `origin/tests` carry — expected per `review-child` §5.4 sibling test/bible carry. **Product scope:** 2 `src/**` files only; tests `test_consult.py`, `test_config.py`.

- **Location:** Plan **Repro** vs tests  
  **Finding:** Repro narrative uses `meteorite_grade_do`; `[bug-repro]` uses `meteorite_like` (same scored `_all_x_fail_dest` / `cfg["fail_state"]` path).  
  **Recommendation:** No product gap; optional follow-up test on `meteorite_grade_do` only if Susan wants somerset task name parity in tests.

- **Location:** `test_render_verdict_meteorite_like_all_x_second_strike`  
  **Finding:** Manifest item 1 is `[bug-repro]` by bible § AST-2096; first-line `[bug-repro]` tag is on the batch test / `TestAst2096AllXFailStates` class, not that method’s docstring.  
  **Recommendation:** Cosmetic tag alignment only; assertions are substantive.

## Plan fidelity (§5.4)

Isolated fix diff matches plan-fix **Proposed change** items 1–7: `all_x_of` + six explicit `JOB_STATES` rows + `SKIPPED_STATES`; standalone `_all_x_fail_dest` (no `_consult_batch_fail_dest` call — correct for AST-2086 signature overlap); `render_verdict` terminal branch (`success True`, `_warn_job`); `_run_batch_consult` `failed += 1` / exclude from `bad_grades`. Estimate **3** fits footprint.

## What's solid

- AST-2086 merge hazard explicitly avoided on `_consult_batch_fail_dest`.
- Board bar (Betty TESTS: REVISE) cleared: second-strike batch + config registration + rewritten AC2 single-entity test + AST-1808 snapshot block.

## Chuckles — post-review branching

**PROCEED** + C7 complete + **normal parent** (AST-2011 live; base `origin/ftr/AST-2011-meteorite-grade-do-all-x`) → **Review Posted** → `do-all-the-things` §3h clean-review shortcut → **User Testing**; **resolve-child** skipped.

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Hedy | engineer | `/home/susan/.cursor/chats/43025b8c4a19e7411f07250508c2eca8/d8a76966-63be-4ee2-875d-68b53de494ea/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/49c697b1-a701-46cf-b24a-ec979fec4f42/store.db` |
| Radia | review | `/home/susan/.cursor/chats/43025b8c4a19e7411f07250508c2eca8/fe318551-58e6-4d91-8cff-dff825bf1a52/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-2011 (parent) | ftr/AST-2011-meteorite-grade-do-all-x |
| AST-2096 | sub/AST-2011/AST-2096-all-x-fail-state |

**Epic worktree:** `astral-AST-2011/` — one active sub checked out at a time.
