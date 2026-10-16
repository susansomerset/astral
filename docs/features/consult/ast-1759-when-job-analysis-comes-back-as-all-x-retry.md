# AST-1759 — When job analysis comes back as all X, retry

<!-- linear-archive: AST-1759 archived 2026-10-07 -->

## Linear archive (AST-1759)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1759/when-job-analysis-comes-back-as-all-x-retry  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** chuckles  
**Priority / estimate:** High / 2  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Scored job Analysis can return a complete grade set that is entirely literal `X` (no usable signal). Today that set still scores `0.0` and, when the dispatch score floor is `0.0` (notably `meteorite_like`), the job **passes** into the next hop — including `meteorite_upshot` — instead of being treated as a bad apply. Operators then see an all-`X` job for which the model effectively graded nothing. This epic makes all-literal-`X` on scored consult apply retry the same way process / incomplete-grade failures already do, so the job gets one more grading attempt before technical fail.

## Functional scope

* On any scored Analysis grading apply (`grading_mode` scored — company Do/Get/Like and meteorite twins including `meteorite_like`), a **complete** grade set where **every** grade letter is literal `X` is a recoverable apply failure, not a pass and not a permanent scored fail.
* Those jobs take the existing first-strike retry holding for the trigger state (same destination path as process / incomplete-grade errors via `_consult_batch_fail_dest`). They must not advance to the next Analysis hop or upshot on that attempt.
* Partial-`X` sets and mixed no-signal rows (e.g. confidence-1 alongside real letters) keep today’s scored behavior. Binary grading’s all-literal-`X` → `fail_state` path is unchanged.

## Component scope

* `src/core/consult.py` — **modified** — gate all-literal-`X` on the scored apply / `_render_score` path into the existing batch fail-dest / retry routing (same family as incomplete grade sets); leave binary `_render_pass_fail` all-`X` → fail alone.

## Technical scope

* `src/core/consult.py` — new scored-path check after the complete-set gate (or equivalent raise site): when every grade row’s letter is literal `X`, raise into the caller’s existing bad-grades / process-failure path so `_consult_batch_fail_dest` picks primary → `retry_state` holding, holding → `error_state`. Must not return `pass_state` and must not land `fail_state` on first strike for this case.
* `src/core/consult.py` — no change to `_render_pass_fail` all-literal-`X` → `fail_state`; no change to partial-`X` / counted-set scoring math; no new JOB_STATES / TASK_CONFIG holdings (reuse existing `*_RETRY` companions).

## Architectural definition

* **Patterns to reuse**
  * `patt.task.dispatch-retry` — one more try through the sibling retry holding, folded into ordinary claim; no bespoke all-X queue. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.task.dispatch-retry.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.task.dispatch-retry.md>)
  * `patt.entity.batch-processing` — per-entity process failure inside claim → process → release; siblings in the same batch keep their own outcomes. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.entity.batch-processing.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.entity.batch-processing.md>)
  * `patt.entity.batch-criteria` — claim shape / score floor stay dispatch_task-owned; this epic does not invent a parallel floor rule for all-X. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.entity.batch-criteria.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.entity.batch-criteria.md>)
* **New patterns proposed:** none
* **Applicable statutes**
  * `astral.batch.claim-process-release` — failure stays inside the claimed batch process path; no carve-out that skips release. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.batch.claim-process-release.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.batch.claim-process-release.md>)
  * `stat.logging.debug` — if a debug branch names the all-literal-`X` route, keep it Style-D / debug-gated like sibling incomplete-grade detail. [https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>)

## Acceptance criteria

1. Replay a `meteorite_like` batch where one job’s decoded grades are a complete set of literal `X` and siblings have normal letters: the all-`X` job’s state is `METEORITE_PASSED_GET_RETRY` (not `METEORITE_PASSED_LIKE`, not `METEORITE_FAILED_LIKE` on first strike); siblings still reach pass or fail from ordinary scoring. **Fail if** the all-`X` job is `METEORITE_PASSED_LIKE` or `METEORITE_FAILED_LIKE` after that first apply.
2. From `METEORITE_PASSED_GET_RETRY`, a second all-literal-`X` apply lands `METEORITE_FAILED_TECHNICAL_LIKE` (existing second-strike fail-dest). **Fail if** the job remains on the retry holding or returns to `METEORITE_PASSED_GET` without technical fail.
3. Unit / component: scored apply with score floor `0.0` and every grade letter `X` never returns / transitions to that task’s `pass_state`. **Fail if** `_render_score` or apply returns `pass_state` for an all-literal-`X` set at floor `0.0`.
4. A complete set with at least one non-`X` letter still scores and may pass or fail under existing floor rules (partial-`X` unchanged). **Fail if** any single `X` among otherwise real grades forces the retry holding.
5. `_render_pass_fail` with all literal `X` still returns that task’s `fail_state` (binary path unchanged). **Fail if** binary all-`X` routes to a `*_RETRY` holding.

## Open questions

none

## Proposed child tickets

#### 1: **All-X scored grades → retry holding - Hedy**

Owns the scored consult apply gate for all-literal-`X` complete sets and the raise-into-existing-fail-dest wiring so first strike retries and second strike technical-fails. Does **not** change binary all-`X` → fail, prompt copy, or invent new holdings.
**Citations:** `patt.task.dispatch-retry`, `patt.entity.batch-processing`, `patt.entity.batch-criteria`, `astral.batch.claim-process-release`, `stat.logging.debug`
**Scope:** `src/core/consult.py` — **modified** — gate all-literal-`X` on the scored apply / `_render_score` path into the existing batch fail-dest / retry routing (same family as incomplete grade sets); leave binary `_render_pass_fail` all-`X` → fail alone. | `src/core/consult.py` — new scored-path check after the complete-set gate (or equivalent raise site): when every grade row’s letter is literal `X`, raise into the caller’s existing bad-grades / process-failure path so `_consult_batch_fail_dest` picks primary → `retry_state` holding, holding → `error_state`. Must not return `pass_state` and must not land `fail_state` on first strike for this case. | `src/core/consult.py` — no change to `_render_pass_fail` all-literal-`X` → `fail_state`; no change to partial-`X` / counted-set scoring math; no new JOB_STATES / TASK_CONFIG holdings (reuse existing `*_RETRY` companions).
**Estimate: 2**

Monolith: two functional capabilities, one inseparable vertical slice (detect + route must ship together for UAT).

---

## Original brief

When I ran a job through meteorite_like, it processed 4 jobs, 3 were fine with grades, and one for some reason was all "X", but it passed through to upshot anyway.  Let's retry jobs in the case of all X, like we do with error.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
