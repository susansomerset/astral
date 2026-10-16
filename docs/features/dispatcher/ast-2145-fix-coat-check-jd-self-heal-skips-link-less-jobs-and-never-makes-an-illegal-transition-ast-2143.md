# AST-2145 — fix: coat-check JD self-heal skips link-less jobs and never makes an illegal transition (AST-2143)

<!-- linear-archive: AST-2145 archived 2026-10-16 -->

## Linear archive (AST-2145)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2145/fix-coat-check-jd-self-heal-skips-link-less-jobs-and-never-makes-an  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-2143 — [✅/Somerset] meteorite_grade_do COMPLETED: 1 error(s) / 36 processed | meteorite_grade_do-b93cbaa7-f72a-4e73-9a2a-4587898ad5f4  
**Blocked by / blocks / related:** parent: AST-2143; blocks: AST-2146

### Description

## What this implements

The `fix` child for orphaned bug [AST-2143](https://linear.app/astralcareermatch/issue/AST-2143) (somerset `meteorite_grade_do`, job `4d9d1c79` errored with `no live content`).

`get_job_data`'s coat-check self-heal fires on a job that has a short composed JD. It calls `fetch_jd_batch` even when the job has no `job_link` (nothing to scrape) and even when the job sits in a later task's state (`METEORITE_PASSED_JD`). There, `fetch_jd_batch`'s fetch-stage transitions (`ERROR_FETCH_JD_UNREADABLE` and the others) are illegal and raise `Invalid transition`. `get_job_data` swallows that, logs a misleading `self-heal failed` line, and returns `None`.

This fix covers two things:

* A short JD with no `job_link` skips the self-heal: one warning, then return the composed text or `None`.
* The self-heal can never attempt an illegal state transition.

A job with no usable JD still lands in its task's `error_state`, as it does today.

## Scope

## Component scope

* `src/core/tracker.py`: modified. `get_job_data` gets the no-`job_link` guard, and its self-heal call becomes transition-safe.
* `src/core/gazer.py`: modified, only if option 3(a) is picked. `fetch_jd_batch` gets a mode that keeps the capture without moving the job's state.

## Technical scope

* `src/core/tracker.py`: modified function `get_job_data`. It adds an early return when there is no `job_link` and calls the self-heal in a way that can't produce an illegal state transition. No new table and no new field.
* `src/core/gazer.py` (option 3(a) only): modified function `fetch_jd_batch`, which gains an opt-out of its state transitions. Without that, a downstream coat-check can't reuse the scrape-and-keep path safely.

## Boundaries

* Doesn't change `compose_job_description`, the `jd_min_chars` threshold, consult's `no live content` routing to `error_state`, or `fetch_jd_batch`'s behaviour for its own `fetch_jd` dispatch task.
* Doesn't touch the `AllLiteralXGradeSetError` or `grade X requires confidence digit 0` retries in the same log. Those are covered by AST-2011 and AST-2045.
* The production lookup of job `4d9d1c79` (is its JD a short meteorite preamble, or was it lost by the AST-2133 composed read?) is an ops check for Susan, not part of this child. If it shows a lost JD, that becomes a separate bug.

## Notes for planning

* Susan approved without choosing between the two transition-safe options in AST-2143's Proposed steps 3. **(a)** adds a no-transition single-job mode to `fetch_jd_batch` for the coat-check. **(b)** skips the self-heal when the job's current state isn't a prior state of the fetch-stage destinations. Pick one in the plan with a one-line why. (a) is cleaner, (b) is smaller. `src/core/gazer.py` is in scope only if you pick (a).
* Ancestor (checked by Susan): AST-326, Batch Scrape JDs. It was archived, so there's no live ticket. It made the `get_job_data` coat-check delegate to the batch fetch (`docs/features/gazer/ast-326-batch-scrape-jds-plan.md`). Most recent change on this path: AST-2133 (yours), `docs/features/foundation/ast-2133-composed-read-only-job-description.md`, which moved the self-heal trigger onto composed length.
* Full as-is, to-be and log are on [AST-2143](https://linear.app/astralcareermatch/issue/AST-2143).

## Git branch (authoritative)

Orphaned mini-parent: `ftr/AST-2143-jd-self-heal-no-link`, child `sub/AST-2143/AST-2145-jd-self-heal-guard`. Seeded off `origin/dev` by bug-fix.

### Comments

#### radia — 2026-10-12T18:00:49.885Z
[code-rubric] PROCEED (Commit: a17290ad3) transition-free coat-check heal

#### katherine — 2026-10-12T17:59:18.298Z
`origin/sub/AST-2143/AST-2145-jd-self-heal-guard` @ `a17290ad3` · lighter check (qa-fix routed to AST-2146)

`pytest tests/component/core/test_tracker.py tests/component/core/test_gazer.py` (astral-tests venv):
- pre-fix (`origin/ftr/AST-2143-jd-self-heal-no-link`): 20 failed / 314 passed
- tip: 23 failed / 311 passed
- Newly red on tip, exactly the 3 expected (AST-2146 owns):
  - `TestGetJobData::test_self_heals_short_job_description`
  - `TestAst2133ComposeJobDescription::test_self_heal_writes_reference_then_returns_composed`
  - `TestAst2025FetchRelativeJdBatch::test_ac5_both_runners_call_shared_gate_helper`
- The other 20 failures are identical on both trees (pre-existing, unrelated to this fix).

#### joan — 2026-10-12T17:56:02.980Z
[board-joan]  CANON: OK

#### betty — 2026-10-12T17:55:13.140Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/tracker.md § AST-2133 + core/gazer.md § AST-2025 — broken tests + missing coverage — (1) Blast radius confirmed: `test_tracker.py::TestGetJobData::test_self_heals_short_job_description` breaks (no job_link → guard skips scrape); `::test_self_heal_failure_returns_none` keeps passing but only through the guard, so the exception branch is no longer exercised; `::TestAst2133ComposeJobDescription::test_self_heal_writes_reference_then_returns_composed` breaks (fake `_fetch` rejects `transition=`, job has no link). (2) Blast radius missed one: `test_gazer.py::TestAst2025FetchRelativeJdBatch::test_ac5_both_runners_call_shared_gate_helper` does an exact-dict compare on the spy's kwargs, so `fetch_jd_batch` passing `transition=transition` adds `transition: True` to the j-abs entry and the compare fails. "gazer tests keep passing on the default" is wrong for this node. (3) No coverage exists for the repro: the no-link guard (returns None, one warning, `fetch_jd_batch` never awaited), `transition=False` in `fetch_jd_batch` / `_apply_jd_gates` (no `transition_job_state` on any outcome; classified result skips the ref save and returns False; pass result keeps the ref), and a downstream-state heal that returns the composed JD with state unchanged. Test-only, no product-scope question.

#### katherine — 2026-10-12T17:54:19.252Z
`origin/sub/AST-2143/AST-2145-jd-self-heal-guard` @ `08912b114` · option (a), transition-free self-heal

---

_Implementation detail may live in git history on `origin/dev`._
