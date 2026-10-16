# AST-2158 — [✅/Somerset] meteorite_grade_get COMPLETED: 1 error(s) / 4 processed | meteorite_grade_get-060a88ad-366e-411e-bfd3-258123d10839

<!-- linear-archive: AST-2158 archived 2026-10-16 -->

## Linear archive (AST-2158)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2158/somerset-meteorite-grade-get-completed-1-errors-4-processed-meteorite  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** unassigned  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Prior occurrences

* none found (4 searches) — `meteorite_grade_get · ERROR_METEORITE_GRADE_GET · decoded payload has no job row for this astral_job_id` (evidence: same-batch WARNING `meteorite_grade_get skipped — index 0 not in this batch`) — **novel**, first occurrence, diagnosed below.

## As-is

On the lone-job grade path (`run_consult_task` → `render_verdict`, one job per agent call — the log shows four separate `job consult completed` / LLM lines), the job's row is labelled with its batch-unique index from the dispatcher claim (`[index=NNN]`, AST-2093 — a lone row can be `024`, not always `000`), and decode binds the reply through `batch_index_map = {batch_index: job}`. In this batch the model answered with `000` for a job whose index was not 0. `agent._decode_payload` treated that as an unknown index, logged `skipped — index 0 not in this batch`, and dropped the line **without** recording a `decode_failure`. `render_verdict` then found no row and no decode failure for the job, fell through to its generic `_fail("decoded payload has no job row for this astral_job_id")`, and moved the job straight to the terminal `ERROR_METEORITE_GRADE_GET` — even though a real grade was returned and the same miss in the batch path is a retryable "omitted from response".

## To-be

A lone-job reply whose row can't be bound (unknown index, or no row at all) is handled like an omitted entity in the batch path: routed via `_consult_batch_fail_dest` (primary state → its retry holding; already-retry → error state), logged with an `omitted from response` style reason — not a hard error on the first miss. A wrong row index echoed by the model on a one-job call never lands a job in `ERROR_*` on its own.

## Proposed steps

1. In `render_verdict`, replace the final `_fail("decoded payload has no job row …")` fallback with the same retry routing the `decode_failures` branch right above it already uses (`_consult_batch_fail_dest` → `_log_fail_dest` → `_transition_job_state_for_task`), reason `omitted from response` (or the decode skip reason).
2. Leave `agent._decode_payload`'s unknown-index skip as-is (AST-2093's guard stays intact for multi-row batches).
3. Component test: lone `render_verdict` with `batch_index=24` and a reply line `000|…` → job lands in its retry holding, not `ERROR_METEORITE_GRADE_GET`; a second miss from the retry holding → error state.
4. Optional (Susan's call, not in scope unless checked): when `batch_index_map` holds exactly one entity and the reply has exactly one line, bind that line to the lone entity regardless of the echoed index — grades the job on the first call instead of spending a retry.

## Component scope

* `src/core/consult.py` — modified: `render_verdict`'s no-row fallback is where the lone-job miss is wrongly sent to the terminal error state; the retry router it should use already lives in the same file.

## Technical scope

* `src/core/consult.py` — modified function `render_verdict`: the "no `j0`, no matching `decode_failure`" branch routes through the existing batch fail-destination helper (retry holding first) instead of the hard `_fail`, so a model index mis-echo on a one-job call retries like an omitted batch entity. No new tables, fields, or states.

## Ancestor candidates

- [ ] [AST-2093](https://linear.app/astralcareermatch/issue/AST-2093) — batch-unique row index (Done, parent AST-2012); introduced non-zero lone-call indexes + `batch_index_map` on `render_verdict`; plan in `docs/features/agent/response-validation-layers.md` § Bug: AST-2093 ("What must still hold: retry-holding routing for missing or bad entities is unchanged" — this is the lone-call hole in that promise)
- [ ] [AST-2095](https://linear.app/astralcareermatch/issue/AST-2095) — AST-2093's test gap (Done); decode/assembly tests for the index map, no lone-call wrong-index case
- [ ] [AST-2012](https://linear.app/astralcareermatch/issue/AST-2012) — AST-2093's orphaned mini-parent (grade batch-unique index)
- [ ] AST-1996 — per-entity `decode_failures` → retry routing in `render_verdict` (named in code comments only; no feature doc found this round)

## Original report

```
2026-10-12 19:26:42  [INFO]  somerset | dispatch job task completed:
meteorite_grade_get pass:3 fail:0 error:1 (batch:
meteorite_grade_get-060a88ad-366e-411e-bfd3-258123d10839)
2026-10-12 19:26:42  [WARNING]  8b30ec4c-57cb-49ca-9481-3fecaf4539e1
-> ERROR_METEORITE_GRADE_GET [decoded payload has no job row for this
astral_job_id]
2026-10-12 19:26:42  [INFO]  2ec2b685-2ad6-49a7-9ba3-4c85eb909150 |
job consult completed: METEORITE_PASSED_GET (batch:
meteorite_grade_get-060a88ad-366e-411e-bfd3-258123d10839)
2026-10-12 19:26:42  [WARNING]  meteorite_grade_get skipped — index 0
not in this batch
  This line is not being graded
2026-10-12 19:26:42  [INFO]  LLM openrouter host=CoreWeave
task=meteorite_grade_get 10.8s stop=end_turn tokens in=7779 out=998
2026-10-12 19:26:42  [INFO]  a9112ac6-cc97-4e79-be42-327163a10e40 |
job consult completed: METEORITE_PASSED_GET (batch:
meteorite_grade_get-060a88ad-366e-411e-bfd3-258123d10839)
2026-10-12 19:26:42  [INFO]  LLM openrouter host=CoreWeave
task=meteorite_grade_get 9.8s stop=end_turn tokens in=673 out=944
2026-10-12 19:26:42  [INFO]  LLM openrouter host=CoreWeave
task=meteorite_grade_get 8.6s stop=end_turn tokens in=896 out=818
2026-10-12 19:26:42  [INFO]  924a7d47-c60c-4a86-a0e2-73bdea142053 |
job consult completed: METEORITE_PASSED_GET (batch:
meteorite_grade_get-060a88ad-366e-411e-bfd3-258123d10839)
2026-10-12 19:26:42  [INFO]  LLM openrouter host=CoreWeave
task=meteorite_grade_get 17.3s stop=end_turn tokens in=7708 out=1473
2026-10-12 19:26:42  [INFO]  somerset | dispatch job starting
meteorite_grade_get — 4 available (batch:
meteorite_grade_get-060a88ad-366e-411e-bfd3-258123d10839)
```

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
