# AST-1884 — [✅/Somerset] evaluate_meteorite COMPLETED: 1 error(s) / 1 processed | evaluate_meteorite-ee5b6a08-bbed-4025-bfbf-43c854270119

<!-- linear-archive: AST-1884 archived 2026-10-16 -->

## Linear archive (AST-1884)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1884/somerset-evaluate-meteorite-completed-1-errors-1-processed-evaluate  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

`evaluate_meteorite` (Somerset, DeepSeek, batch of 1) returned `000|DEC35|ECC35|EFA45|LED45|MLA45|MWB45|ORX0|PMC35|PVX0|SFX0|TCC35|QCB45|GCB35`. Every non-X segment carries **two** trailing digits (`C35`, `A45`) instead of the single confidence digit the `grades_encoded` output instructions require ("Each grade segment is exactly 4 characters"). `_GRADE_SEG` in `src/core/agent.py` correctly refuses those 5-char tokens, they fall into `meta`, and because `grades_encoded` is grades-only `_decode_payload` raises `ValueError: unexpected trailing content in grades-only line`. That exception fails the **entire hop**, so the job lands in the error state `METEORITE_ERROR_EVALUATE_JD` — a technical-fail for what is really a model formatting slip. In a larger batch, one malformed line would take every job in the batch down with it.

## To-be

A model format slip on an encoded grade line is treated as a retryable per-entity miss, not a technical error: the affected job goes to its retry holding state (same philosophy as AST-1155 — technical-fail states are reserved for true infra failures), and other well-formed lines in the same batch still decode and apply. No silent coercion of ambiguous confidence values (`35` could mean 3 or 5 — guessing would write a wrong grade).

## Proposed steps

1. In `_decode_payload`, stop raising for the whole payload when one line has non-grade trailing content (grades-only types); record that line's entity as a decode failure and keep decoding the rest.
2. In the consult apply path, route those per-entity decode failures to the task's retry holding state (AST-1155 `_consult_batch_fail_dest` / `JOB_STATES.retry_state` route), not `error_state`.
3. Confirm the meteorite twin (`evaluate_meteorite`) has a retry holding state configured; add one if missing.
4. Component tests: a two-line batch where line 0 is `DEC35`-malformed and line 1 is clean → line 1 applies, line 0's job lands in retry holding; the existing grades-only strictness (no coercion) still holds.

## Component scope

* `src/core/agent.py` — modified — `_decode_payload` currently raises on the first malformed line and kills the batch; it needs to isolate the bad line instead.
* `src/core/consult.py` — modified — `_normalize_rubric_task_response` / scored apply path must carry per-entity decode failures through to the retry destination rather than a hop-level error.
* `src/utils/config.py` — modified only if `evaluate_meteorite` / meteorite job states lack a retry holding destination for this trigger.
* `tests/component/core/test_agent.py` — modified — decode isolation regression (test tree is Betty's; listed so the fix lane knows it is in play).
* `tests/component/core/test_consult.py` — modified — retry-holding routing regression for a malformed encoded line (Betty's tree, same note).

## Technical scope

* `src/core/agent.py`: modified function — `_decode_payload` returns successfully decoded rows plus a list of failed positions/reasons for grades-only lines with trailing content, instead of raising `ValueError` for the whole payload.
* `src/core/consult.py`: modified function(s) — the rubric-response normalize/apply path consumes the failed-position list and sends those entities down the existing retry-holding route (AST-1155), leaving the rest of the batch to apply normally.
* `src/utils/config.py`: possibly a new/modified retry-state field on the meteorite JD job states or `evaluate_meteorite` TASK_CONFIG, only if the retry destination does not already exist.

## Ancestor candidates

- [X] AST-1155 — Incomplete grades → retry holding, never technical fail (`docs/features/consult/ast-1155-incomplete-grades-retry-holding-never-technical-fail.md`) — same "model slip should retry, not technical-fail" contract; this bug is the malformed-segment case it didn't cover (it explicitly excluded `agent.py` decode).
- [ ] AST-483 — Normalize grades segment whitespace in agent decode (`docs/features/boards/ast-483-normalize-grades-segment-whitespace-in-agent-decode.md`) — owns the `_decode_payload` classification loop and the "do not widen `_GRADE_SEG`" decision.
- [ ] AST-1513 — Reject duplicate Do rubric codes (`docs/features/consult/ast-1513-reject-duplicate-do-rubric-codes-meteorite-grade-do-is-failing.md`) — most recent `_decode_payload` strictness change on a meteorite twin, routed via the AST-1155 retry path.
- [ ] AST-357 — Grade density / confidence (`docs/features/consult/ast-357-grade-density-confidence.md`) — defines the 4-char `{code}{grade}{conf}` segment contract the model broke.

## Original report

```
2026-09-29 20:00:54  [INFO]  somerset | dispatch job starting
evaluate_meteorite — 1 available (batch: evaluate_meteorite-ee5b6a08-bbed-4025-bfbf-43c854270119)
2026-09-29 20:01:00  [INFO]  somerset | dispatch job task completed: evaluate_meteorite pass:0 fail:0 error:1 (batch: evaluate_meteorite-ee5b6a08-bbed-4025-bfbf-43c854270119)
2026-09-29 20:01:00  [ERROR]  00f39bbe-cadc-4950-b116-7c9342f0e88e -> METEORITE_ERROR_EVALUATE_JD [[evaluate_meteorite] unexpected trailing content in grades-only line: '000|DEC35|ECC35|EFA45|LED45|MLA45|MWB45|ORX0|PMC35|PVX0|SFX0|TCC35|QCB45|GCB35']
2026-09-29 20:01:00  [ERROR]  evaluate_meteorite_batch_evaluate_meteorite-ee5b6a08-bbed-4025-bfbf-43c854270119 | evaluate_meteorite
  ValueError: [evaluate_meteorite] unexpected trailing content in grades-only line: '000|DEC35|ECC35|EFA45|LED45|MLA45|MWB45|ORX0|PMC35|PVX0|SFX0|TCC35|QCB45|GCB35'
  Returning this hop as failed
Traceback (most recent call last):
  File "/app/src/core/agent.py", line 2463, in do_task
    parsed = _normalize_rubric_task_response(task_key, task_config, parsed, ctx or {})
  File "/app/src/core/consult.py", line 761, in _normalize_rubric_task_response
    decoded = _decode_payload(task_key, output_type, text, ctx or {})
  File "/app/src/core/agent.py", line 339, in _decode_payload
    raise ValueError(f"[{task_key}] unexpected trailing content in grades-only line: {line!r}")
ValueError: [evaluate_meteorite] unexpected trailing content in grades-only line: '000|DEC35|ECC35|EFA45|LED45|MLA45|MWB45|ORX0|PMC35|PVX0|SFX0|TCC35|QCB45|GCB35'
2026-09-29 20:01:00  [INFO]  LLM deepseek task=evaluate_meteorite 3.6s stop=end_turn tokens in=1223 out=184
```

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
