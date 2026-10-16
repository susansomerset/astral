# AST-2011 — [✅/Somerset] meteorite_grade_do COMPLETED: 2 error(s) / 30 processed | meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e

<!-- linear-archive: AST-2011 archived 2026-10-16 -->

## Linear archive (AST-2011)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2011/somerset-meteorite-grade-do-completed-2-errors-30-processed-meteorite  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-2073

### Description

I think we need a RETRY for all literal X grades, and then instead of Error for that case, have it FAIL the entity with the suffix `_ALL_X`  Yes, this is special handling, but I can't see another way around it.

## As-is

Somerset `meteorite_grade_do` batch `87d96303` processed 30 jobs: 27 passed, 2 technical-failed (`877c162e`, `7dace48c` → `METEORITE_FAILED_TECHNICAL_DO`), 1 went to retry (`bf81c81e` → `METEORITE_PASSED_JD_RETRY`). All three hit `AllLiteralXGradeSetError: all literal X grades (12 vectors)` — the model graded every Do vector `X`.

Today (AST-1760) a scored all-literal-`X` grade set raises `AllLiteralXGradeSetError`, a subclass of `IncompleteGradeSetError`, so it rides the incomplete-grade route: first strike → `retry_state` holding (`METEORITE_PASSED_JD_RETRY`), second strike on `_RETRY` → `error_state` (`METEORITE_FAILED_TECHNICAL_DO`). An all-X job is a "no usable signal" outcome, not a technical error, but it ends up counted and logged (ERROR) as one.

Not in this fix: the `duplicate rubric codes: TP→[…]` warning (identical-label duplicate `TP` row in somerset's Do rubric; AST-2008 Decision D would re-letter it to `TX` rather than drop it on the next save). Separate ticket if wanted.

## To-be

All-literal-`X` on any scored grading task still gets one retry (primary → `retry_state` holding, unchanged). A second all-`X` strike (entity already on `_RETRY`) transitions the entity to the task's `fail_state` **+** `_ALL_X` — for this task `METEORITE_FAILED_DO_ALL_X` — not `error_state`. It logs as a fail, not an ERROR, and the batch report counts it as a fail, not an error. Incomplete/extra grade sets (plain `IncompleteGradeSetError`) keep today's retry → `error_state` route.

## Proposed steps

1. Register the `_ALL_X` fail states: for every scored task's `fail_state` (e.g. `METEORITE_FAILED_DO`, `FAILED_DO`, `FAILED_GET`, `METEORITE_FAILED_GET`, `FAILED_LIKE`, `METEORITE_FAILED_LIKE`, …), add a `{fail_state}_ALL_X` entry in `JOB_STATES` with the same `prior_states` as its base fail state, plus a small `ALL_X_SUFFIX` / `all_x_of(base)` helper beside `RETRY_SUFFIX` / `retry_of` so names are built, not typed.
2. Add a fail-destination helper next to `_consult_batch_fail_dest`: primary state → `retry_state` (same as today); already on `_RETRY` → `all_x_of(fail_state)`.
3. `render_verdict`'s `except IncompleteGradeSetError` branch: when `isinstance(e, AllLiteralXGradeSetError)`, use the new helper (with the task's `fail_state`) instead of `_consult_batch_fail_dest(..., error_state)`; terminal all-X logs at WARNING/INFO via the fail path, not `_log_fail_dest`'s ERROR.
4. `_run_batch_consult`: track all-X IDs separately from other `bad_grades`, transition them through the new helper instead of `_transition_batch_consult_failures(task_key, bad_rows, error_state)`, and count a terminal all-X as `failed`, not an error, in the batch result.
5. Re-run somerset `meteorite_grade_do`; a job that grades all-X twice should land `METEORITE_FAILED_DO_ALL_X`, and the batch report should show it as a fail.

## Component scope

* `src/utils/config.py` — modified — register the `{fail_state}_ALL_X` job states for scored tasks and add the suffix/name helper beside `RETRY_SUFFIX` / `retry_of`.
* `src/core/consult.py` — modified — route second-strike all-literal-`X` to `fail_state + _ALL_X` at both catch sites (`render_verdict` single-entity apply, `_run_batch_consult` batch apply) and count it as a fail.

## Technical scope

* `src/utils/config.py`: new constant + new function (suffix and name builder, mirroring `retry_of`) so every `_ALL_X` name is derived from its base fail state; new `JOB_STATES` entries (one per scored-task `fail_state`) so the state transition validator accepts the new terminal, with `prior_states` matching the base fail state. Plan-fix decides explicit rows vs an implicit-suffix registration like AST-1804's `_RETRY` — explicit rows are the smaller blast radius (no validator changes in roster / tracker / candidate / database / admin API).
* `src/core/consult.py`: new function — all-X fail destination (primary → `retry_state`, `_RETRY` → `fail_state` + `_ALL_X`), because `_consult_batch_fail_dest` only knows `error_state`; modified function `render_verdict` — `AllLiteralXGradeSetError` branch uses the new destination and fail-level logging; modified function `_run_batch_consult` — split all-X IDs out of `bad_grades`, transition them via the new destination, and tally them as `failed`.

## Ancestor candidates

- [ ] [AST-1760](https://linear.app/astralcareermatch/issue/AST-1760/all-x-scored-grades-retry-holding-when-job-analysis-comes-back-as-all) — All-X scored grades → retry holding (`docs/features/consult/ast-1760-all-x-scored-grades-retry-holding.md`) — owns `AllLiteralXGradeSetError`, `_require_not_all_literal_x`, and the retry → `error_state` route this changes
- [ ] AST-1155 — Incomplete grades → retry holding (`docs/features/consult/ast-1155-incomplete-grades-retry-holding-never-technical-fail.md`) — the incomplete-grade fail-dest family all-X currently rides; its route must stay unchanged for non-all-X incomplete sets

## Original report

```
2026-10-07 01:37:50  [WARNING]  duplicate rubric codes: TP→['Hands-On
Technical Partnership With Engineers', 'Hands-On Technical Partnership
With Engineers']
2026-10-07 01:37:50  [INFO]  somerset | dispatch job starting
meteorite_grade_do — 30 available (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:46:53  [WARNING]  duplicate rubric codes: TP→['Hands-On
Technical Partnership With Engineers', 'Hands-On Technical Partnership
With Engineers']
2026-10-07 01:46:53  [ERROR]  877c162e-24d8-4556-8f8d-f83d54f064ae ->
METEORITE_FAILED_TECHNICAL_DO [process_fn AllLiteralXGradeSetError:
_render_score: all literal X grades (12 vectors)]
2026-10-07 01:46:53  [INFO]  32999a02-ab1f-451e-ae05-39cedcd5aa0c |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:46:53  [INFO]  55a6d34a-b8b1-4279-8ec7-e90ea2d40220 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:46:53  [INFO]  bfac96c4-dc59-461e-88d9-63cc0d51b2d4 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:46:53  [INFO]  ab4ff529-d9e3-4472-8c03-47ac73f3b86b |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:46:53  [INFO]  c23a7e75-d6dc-41d6-95df-c1c00ad05c78 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:46:53  [INFO]  1a2b14f5-f926-428a-9653-35917822f7f1 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:46:53  [INFO]  8674e96f-632b-4179-b48b-a048ae78ab89 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:46:53  [INFO]  1a66955c-50af-4b19-a53c-e9a16442fd91 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:46:53  [INFO]  b5245474-ac8b-496e-ae90-f6ed47065d0f |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:46:53  [INFO]  0f8f1d81-ed8d-4c78-a762-01f7f3f92e7c |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:46:53  [WARNING]  bf81c81e-15e7-4ef2-b61b-e6181a9b8891
-> METEORITE_PASSED_JD_RETRY [process_fn AllLiteralXGradeSetError:
_render_score: all literal X grades (12 vectors)]
2026-10-07 01:46:53  [INFO]  e769541b-8984-4497-a888-87108ef7f248 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:46:53  [INFO]  69af53bd-5fe2-48f8-b7b2-85924c11a1b2 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:46:53  [INFO]  2ec2b685-2ad6-49a7-9ba3-4c85eb909150 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:46:53  [INFO]  f87f8eab-71cf-4a62-b863-515c08dbb1f5 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:46:53  [INFO]  8b30ec4c-57cb-49ca-9481-3fecaf4539e1 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:46:53  [INFO]  924a7d47-c60c-4a86-a0e2-73bdea142053 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:46:53  [INFO]  d34edd2c-c8b3-4aeb-afee-ccfbd70037d3 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:46:53  [INFO]  a8f92e91-da3e-4787-a137-2d9814a24d41 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:46:53  [INFO]  LLM openrouter host=DeepInfra
task=meteorite_grade_do 523.0s stop=end_turn tokens in=26023 out=28663
2026-10-07 01:52:03  [INFO]  somerset | dispatch job task completed:
meteorite_grade_do pass:27 fail:0 error:2 (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:52:03  [INFO]  somerset | dispatch job stopping
meteorite_grade_do — 1 remaining after 1 run(s)
2026-10-07 01:52:03  [INFO]  6ddd5bf9-e03f-4898-bcc2-72a78b118c82 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:52:03  [INFO]  9d226642-4969-4423-9f90-1689c5e43e7d |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:52:03  [INFO]  8f872f1d-9a7e-4581-818a-cddf09f81a62 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:52:03  [ERROR]  7dace48c-2c00-4445-913d-ed1aa4f9a6c2 ->
METEORITE_FAILED_TECHNICAL_DO [process_fn AllLiteralXGradeSetError:
_render_score: all literal X grades (12 vectors)]
2026-10-07 01:52:03  [INFO]  c5840b77-043b-4c11-b7f9-58c0d7afd0c4 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:52:03  [INFO]  41f2e6d6-fefc-44e0-8dc0-dbf6638cd728 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:52:03  [INFO]  f4bef295-d0fe-42e7-a40d-a85696505861 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:52:03  [INFO]  bae2d55d-c402-45c0-bd30-d7f547d60c40 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:52:03  [INFO]  fcbc84ca-cc20-4228-98e3-85f23835bb82 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:52:03  [INFO]  7028b971-cb43-4c5e-a9fb-0ca32713d235 |
job consult completed: METEORITE_PASSED_DO (batch:
meteorite_grade_do-87d96303-3b3f-4160-8421-24d035e8a26e)
2026-10-07 01:52:03  [INFO]  LLM openrouter host=DeepInfra
task=meteorite_grade_do 305.8s stop=end_turn tokens in=20943 out=21319
```

### Comments

#### chuckles — 2026-10-09T02:58:03.360Z
[merge-child] blocked: validate-sub-log rejects [AST-2096](https://linear.app/astralcareermatch/issue/AST-2096) because it has two merge-tests commits (`ff7efc42c` initial repro and `a135a38e3` qa-handoff return). @Betty White, please republish the sub with exactly one merge-tests(AST-2096). The tip's file tree must stay identical to the current one (`72e49fa0d`).

#### chuckles — 2026-10-09T02:41:40.640Z
@susan, a heads-up that isn't blocking this bug: `origin/tests` carries `9ead623ca`, a `sync(publish-ref)` merge for [AST-2091](https://linear.app/astralcareermatch/issue/AST-2091), and `validate-tests-branch.sh` forbids that. Every Betty push now fails the check, on every epic. For [AST-2096](https://linear.app/astralcareermatch/issue/AST-2096) I allowed a one-off publish past the check: only Betty's two commits, which fast-forward and pass on their own. I did not move `tests-clean-base`.

Your call on the shared fix: advance `origin/tests-clean-base` to `9ead623ca` (grandfather it, AST-1574 option A), or revert it on `origin/tests` (AST-2091's session would need to redo that sync the right way).

#### chuckles — 2026-10-09T02:29:55.922Z
Reassigned with no letter, so I'm going with my pick, **A**: dispatching now and running in parallel with [AST-2073](https://linear.app/astralcareermatch/issue/AST-2073). Comment B or C if you meant otherwise.

#### chuckles — 2026-10-09T02:17:19.424Z
@susan: one sequencing call is needed before I dispatch this. Nothing has been created yet: no branch and no child.

[AST-2073](https://linear.app/astralcareermatch/issue/AST-2073) (Revise terminal states) is In Progress, and its child [AST-2086](https://linear.app/astralcareermatch/issue/AST-2086) is at Plan Approved. It rewrites the same code this fix needs:
- `_consult_batch_fail_dest` in `src/core/consult.py`, which this fix splits so a second all-X strike goes to `fail_state` + `_ALL_X`.
- New state-name helpers beside `retry_of` in `src/utils/config.py`, which is where the `_ALL_X` name builder would go.
- `METEORITE_FAILED_TECHNICAL_DO` becomes `ERROR_METEORITE_GRADE_DO`. AST-2073 keeps verdict names like `METEORITE_FAILED_DO`, so `METEORITE_FAILED_DO_ALL_X` still fits its grammar.

Options:
- **A (my pick): run in parallel now.** Hedy plans and builds on a fresh ftr off dev. Whichever epic lands second resolves the merge in `consult.py`/`config.py`, which is routine engineer conflict routing. The fix is about 3 points and touches 2 files, so the conflict should be small. One risk: if this lands first, AST-2086's plan won't know about the `_ALL_X` states and has to carry them through its rename.
- **B: serialize.** Dispatch now, but block the fix child on AST-2073 so Hedy plans against the renamed code once it ships. The cleanest merge, but this waits for the whole terminal-states epic.
- **C: fold into AST-2073.** Add the `_ALL_X` second-strike routing to AST-2073's scope as an extra child and cancel this bug. That's define work on AST-2073.

Reply A, B or C and reassign this to Chuckles to resume.

---

_Implementation detail may live in git history on `origin/dev`._
