# AST-2003 — [✅/Somerset] evaluate_jd COMPLETED: 3 error(s) / 3 processed | evaluate_jd-dcb90fec-d23c-4a08-8535-42b9840e5b59

<!-- linear-archive: AST-2003 archived 2026-10-13 -->

## Linear archive (AST-2003)

**Archived:** 2026-10-13  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2003/somerset-evaluate-jd-completed-3-errors-3-processed-evaluate-jd  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** unassigned  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** duplicate: AST-2007

### Description

## As-is

Every somerset `evaluate_jd` batch hop fails (3/3 errors). The model returns grade segments `PM2A5` and `TP2A5` because the somerset rubric carries **three-character** vector codes `PM2` and `TP2` (alongside `PM` and `TP`). `_decode_payload` in `src/core/agent.py` only recognises `_GRADE_SEG` = two-letter code + grade letter + confidence digit, so those segments fall into `meta`. For the grades-only output type, that raises `unexpected trailing content in grades-only line` and fails the whole batch. The AST-1513 save guard (`_assert_unique_rubric_codes` in `src/core/candidate.py`) only checks that codes are **unique**, not that they are two letters, so `PM2`/`TP2` save cleanly. The guard's own fallback for a blank code, `V{nn}` (e.g. `V01`), is also three characters long.

Secondary, seen in the same line: `IDX5` (grade X with confidence 5). Even after the code fix, that job would still raise `grade X requires confidence digit 0`. **Out of scope for this bug** — not decided here.

## To-be

Rubric vector codes are **strictly two uppercase letters** (`^[A-Z]{2}$`) — no digits or symbols (Susan: Option A; mixing in numbers and symbols invites confusion). The decoder contract (`_GRADE_SEG`) stays unchanged. A rubric containing a code that isn't two letters, or a blank code, gets rejected at save time (`ValueError` → HTTP 400, naming the vector and the bad code), so it can't reach a dispatch run. The somerset rubric gets re-coded so that `PM2`/`TP2` become unique two-letter codes, and somerset `evaluate_jd` batches then decode with every vector graded.

## Proposed steps

1. In `src/core/candidate.py`, extend the rubric save guard beside `_assert_unique_rubric_codes` (in the `normalize_rubric_artifacts_on_save` path) so it rejects any code that doesn't match `^[A-Z]{2}$`. The error names the vector label and the offending code. Run the shape check before the uniqueness check, on the same uppercased value.
2. Remove the `V{nn}` fallback: a blank or missing code becomes a save-time `ValueError` naming the vector, instead of a three-character placeholder that would fail decode later.
3. Leave `_GRADE_SEG` and `_decode_payload` in `src/core/agent.py` unchanged — the two-letter wire format stays the single contract.
4. Data fix (ops, not product code): re-save the somerset rubric via Artifacts with unique two-letter codes in place of `PM2` and `TP2`. The new save guard proves the fix. Then re-run a somerset `evaluate_jd` batch and confirm it decodes.

## Component scope

* `src/core/candidate.py` — modified: the rubric save path (`normalize_rubric_artifacts_on_save` / `_assert_unique_rubric_codes`) gains two-letter code-shape validation and loses the three-character `V{nn}` fallback for blank codes.
* **Somerset rubric data** (`rubric_vector` rows via the Artifacts UI) — modified: re-code `PM2` / `TP2` to unique two-letter codes. This is a staging/prod ops change, not product code.

## Technical scope

* `src/core/candidate.py`: modified validation function (`_assert_unique_rubric_codes` or a sibling helper called from the same save path) that raises `ValueError` naming the vector when its code is blank or doesn't match `^[A-Z]{2}$`. That keeps bad codes out at save time instead of failing a dispatch run. There is no change to the decoder, no new table and no new field.

## Ancestor candidates

- [X] AST-1513 — Reject duplicate Do rubric codes (`docs/features/consult/ast-1513-reject-duplicate-do-rubric-codes-meteorite-grade-do-is-failing.md`). Added the uniqueness-only save guard and the `V{nn}` fallback; `PM2`/`TP2` most likely come from fixing data against it.
- [ ] AST-1510 — meteorite_grade_do is failing (`docs/features/consult/ast-1510-meteorite-grade-do-is-failing.md`). AST-1513's parent; the same somerset duplicate-code incident.
- [ ] AST-357 — Grade density / confidence (`docs/features/consult/ast-357-grade-density-confidence.md`). Origin of the `_GRADE_SEG` two-letter-code + letter + confidence-digit wire format.
- [ ] AST-378 — Runtime rubric validation (`docs/features/auditor/ast-378-runtime-rubric-validation.md`). Rubric validation home, if the shape check belongs there instead of on save.
- [ ] AST-723 — Rubric vector read/write cutover (`docs/features/auditor/ast-723-rubric-vector-read-write-cutover.md`). `rubric_vector` is the authority for codes.
- [ ] AST-816 — UAT compact vector reviews hydrate evaluate_jd (`docs/features/auditor/ast-816-uat-compact-vector-reviews-hydrate-evaluate-jd.md`). The `evaluate_jd` compact decode path.

## Original report

2026-10-06 05:19:39  \[INFO\]  somerset | dispatch job starting
evaluate_jd — 3 available (batch:
evaluate_jd-dcb90fec-d23c-4a08-8535-42b9840e5b59)
2026-10-06 05:20:15  \[INFO\]  somerset | dispatch job task completed:
evaluate_jd pass:0 fail:0 error:3 (batch:
evaluate_jd-dcb90fec-d23c-4a08-8535-42b9840e5b59)
2026-10-06 05:20:15  \[ERROR\]  94d54301-a3fb-4b09-a974-2911c3006c6f ->
ERROR_EVALUATE_JD \[\[evaluate_jd\] unexpected trailing content in
grades-only line:
'000|AGX0|AIA5|CFB4|CRX0|DCA5|DEA5|DKX0|DLB4|DSB5|DTA5|ECA5|EFA5|EMA5|EOA5|ETB4|IDX5|KWA5|LEB4|LGA5|LOA5|MLA5|MWA5|ORA5|PMA5|PM2A5|REA5|RGX0|RRA5|SAA5|SBA5|SCA5|SRA5|SSA5|TCA5|TDA5|TLA5|TPA5|TP2A5|TZA5|YEA5|QCA5|GCA4'\]
2026-10-06 05:20:15  \[ERROR\]  721abb53-9020-4dd6-a7be-7f159f15197b ->
ERROR_EVALUATE_JD \[\[evaluate_jd\] unexpected trailing content in
grades-only line:
'000|AGX0|AIA5|CFB4|CRX0|DCA5|DEA5|DKX0|DLB4|DSB5|DTA5|ECA5|EFA5|EMA5|EOA5|ETB4|IDX5|KWA5|LEB4|LGA5|LOA5|MLA5|MWA5|ORA5|PMA5|PM2A5|REA5|RGX0|RRA5|SAA5|SBA5|SCA5|SRA5|SSA5|TCA5|TDA5|TLA5|TPA5|TP2A5|TZA5|YEA5|QCA5|GCA4'\]
2026-10-06 05:20:15  \[ERROR\]  239cbaf5-491a-4a3c-a562-584904404308 ->
ERROR_EVALUATE_JD \[\[evaluate_jd\] unexpected trailing content in
grades-only line:
'000|AGX0|AIA5|CFB4|CRX0|DCA5|DEA5|DKX0|DLB4|DSB5|DTA5|ECA5|EFA5|EMA5|EOA5|ETB4|IDX5|KWA5|LEB4|LGA5|LOA5|MLA5|MWA5|ORA5|PMA5|PM2A5|REA5|RGX0|RRA5|SAA5|SBA5|SCA5|SRA5|SSA5|TCA5|TDA5|TLA5|TPA5|TP2A5|TZA5|YEA5|QCA5|GCA4'\]
2026-10-06 05:20:15  \[ERROR\]
evaluate_jd_batch_evaluate_jd-dcb90fec-d23c-4a08-8535-42b9840e5b59 |
evaluate_jd
  ValueError: \[evaluate_jd\] unexpected trailing content in grades-only
line: '000|AGX0|AIA5|CFB4|CRX0|DCA5|DEA5|DKX0|DLB4|DSB5|DTA5|ECA5|EFA5|EMA5|EOA5|ETB4|IDX5|KWA5|LEB4|LGA5|LOA5|MLA5|MWA5|ORA5|PMA5|PM2A5|REA5|RGX0|RRA5|SAA5|SBA5|SCA5|SRA5|SSA5|TCA5|TDA5|TLA5|TPA5|TP2A5|TZA5|YEA5|QCA5|GCA4'
  Returning this hop as failed
Traceback (most recent call last):
  File "/app/src/core/agent.py", line 2541, in do_task
    parsed = \_normalize_rubric_task_response(task_key, task_config,
parsed, ctx or {})
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/consult.py", line 761, in \_normalize_rubric_task_response
    decoded = \_decode_payload(task_key, output_type, text, ctx or {})
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/core/agent.py", line 335, in \_decode_payload
    raise ValueError(f"\[{task_key}\] unexpected trailing content in
grades-only line: {line!r}")
ValueError: \[evaluate_jd\] unexpected trailing content in grades-only
line: '000|AGX0|AIA5|CFB4|CRX0|DCA5|DEA5|DKX0|DLB4|DSB5|DTA5|ECA5|EFA5|EMA5|EOA5|ETB4|IDX5|KWA5|LEB4|LGA5|LOA5|MLA5|MWA5|ORA5|PMA5|PM2A5|REA5|RGX0|RRA5|SAA5|SBA5|SCA5|SRA5|SSA5|TCA5|TDA5|TLA5|TPA5|TP2A5|TZA5|YEA5|QCA5|GCA4'
2026-10-06 05:20:15  \[INFO\]  LLM openrouter host=DekaLLM
task=evaluate_jd 33.1s stop=end_turn tokens in=25485 out=1414

```
```

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
