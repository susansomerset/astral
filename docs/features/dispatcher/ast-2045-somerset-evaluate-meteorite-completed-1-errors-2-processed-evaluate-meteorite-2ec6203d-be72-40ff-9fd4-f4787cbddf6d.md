# AST-2045 — [✅/Somerset] evaluate_meteorite COMPLETED: 1 error(s) / 2 processed | evaluate_meteorite-2ec6203d-be72-40ff-9fd4-f4787cbddf6d

<!-- linear-archive: AST-2045 archived 2026-10-16 -->

## Linear archive (AST-2045)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2045/somerset-evaluate-meteorite-completed-1-errors-2-processed-evaluate  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

`evaluate_meteorite` (Somerset, provider openrouter/Nebius) returned the line `000|CFC0|ECD5|EHA5|MLB4|MUA3|RWD5|SSC0|TCC0|TPB3|QCA5|GCB4` for job `a9112ac6-…`. Three segments, `CFC0`, `SSC0` and `TCC0`, carry a letter grade with confidence **0**, which the contract only allows on `X`. `_decode_payload` (`src/core/agent.py`, encoded grades loop) records it as a per-line `decode_failures` entry ([AST-1996](https://linear.app/astralcareermatch/issue/AST-1996/isolate-malformed-encoded-grade-lines-per-entity-retry-not-hop-error) isolation works: the other job in the batch passed). `_run_batch_consult` then routes the job through `_consult_batch_fail_dest`. The job was already in the retry holding (`retry_of("METEORITE_QUALIFIED")`), so it went terminal to `METEORITE_ERROR_EVALUATE_JD`, and the batch finished with `1 error(s) / 2 processed`.

The routing is behaving as designed. The defect is that the model keeps writing `{letter}0`, apparently to mean "no signal", on both attempts. A job whose grades are otherwise usable dies after two strikes.

## To-be

The encoded-grade decoder accepts a letter grade with confidence 0 (`{A-F}0`) as a sanctioned slip. It normalises the segment to `{letter}1` instead of recording a `decode_failures` entry. The line decodes, and the job scores and moves on in the same pass. The statute records this as the one allowed exception to the confidence bounds.

## Proposed steps

**Susan picked option B only** (decoder normalisation, no prompt change).

1. In `_decode_payload`'s encoded (non-vet) grades loop, when a segment has a letter other than `X` and confidence 0, rewrite its confidence to 1 and keep the letter. Do not add a `decode_failures` entry.
   * **Why** `{letter}1` **and not** `X0`**:** both score as no signal (`_effective_no_signal_for_score` treats literal `X` and confidence 1 the same, and `CONFIDENCE_MULTIPLIERS[1] = 0.0`). `{letter}1` keeps the model's letter for display. It also never produces a QC `X`, which AST-1910 forbids, and it doesn't push a line toward `AllLiteralXGradeSetError`. An `F0` becomes `F1`, which is no signal under the statute rather than a dealbreaker, so no false fails.
2. Keep every other confidence check as it is today: `X` with nonzero confidence is still a `decode_failures` line, and the vet path (`grades_encoded_vet_meta`) still rejects confidence 0. The vet path is out of scope.
3. Amend `astral.agent.confidence-bounds` to state that the encoded decoder normalises `{A-F}0` to `{A-F}1`, so the coercion is law rather than a silent bypass. This is a statute edit and needs Archie's approval.
4. Re-dispatch the stranded job `a9112ac6-…`. `METEORITE_ERROR_EVALUATE_JD` is already a prior state of `METEORITE_QUALIFIED`, so this is an operator nudge with no code change.

## Component scope

* `src/core/agent.py` (modified). `_decode_payload`'s encoded grades loop holds the non-X `conf_d not in 1..5` rejection that sent this job to error. That branch becomes a normalisation for confidence 0.
* `canon/directives/draft/stat.agent.confidence-bounds.md` (modified). The statute that today says letter grades carry confidence 1–5 gains the one sanctioned `{A-F}0 → {A-F}1` decoder exception.

## Technical scope

* `src/core/agent.py`: modified function `_decode_payload`. In the per-segment confidence check, a non-X segment with confidence 0 is appended as a grade row with confidence 1 instead of setting the bad-line reason. A model writing "no signal" with a letter then costs no retry strike. Confidence 6–9 on a letter, and `X` with nonzero confidence, keep today's `decode_failures` handling.
* `canon/directives/draft/stat.agent.confidence-bounds.md`: modified statute statement plus a conforming example, so reviewers (Joan/Radia) score the coercion as compliant rather than as a breach of the 1–5 bound.

## Ancestor candidates

- [X] AST-1996: isolate a malformed grades-only encoded line and route the entity via retry/error (`docs/features/consult/ast-1155-incomplete-grades-retry-holding-never-technical-fail.md`, [AST-1996](https://linear.app/astralcareermatch/issue/AST-1996/isolate-malformed-encoded-grade-lines-per-entity-retry-not-hop-error) patch). Owns the exact `non-X grade requires confidence 1-5` `decode_failures` path this job hit.
- [ ] AST-1910: forbid QC X grade, and its "confidence 1–5, never 0" prompt line (`docs/features/interface/ast-1084-config-constant-jd-vectors.md`). The same failure class on the `QCF0` side, fixed by prompt text.
- [ ] AST-1154: rubric-completeness contracts for all graded tasks (`docs/features/consult/ast-1154-rubric-completeness-contracts-all-graded-tasks.md`). Owns `_ENCODED_GRADE_SET_COMPLETENESS`, the shared "emit `{code}X0`" text.
- [ ] AST-1155: incomplete grades go to retry holding, never technical fail (`docs/features/consult/ast-1155-incomplete-grades-retry-holding-never-technical-fail.md`). Owns the primary → retry → terminal routing that took this job to `METEORITE_ERROR_EVALUATE_JD`.

---

## Original report

```
2026-10-08 18:18:32  [INFO]  somerset | dispatch job starting
evaluate_meteorite — 2 available (batch:
evaluate_meteorite-2ec6203d-be72-40ff-9fd4-f4787cbddf6d)
2026-10-08 18:18:39  [ERROR]  a9112ac6-cc97-4e79-be42-327163a10e40 ->
METEORITE_ERROR_EVALUATE_JD [decode: [evaluate_meteorite] non-X grade
requires confidence 1-5, got 0 in segment 'CFC0' (line
'000|CFC0|ECD5|EHA5|MLB4|MUA3|RWD5|SSC0|TCC0|TPB3|QCA5|GCB4')]
2026-10-08 18:18:39  [INFO]  LLM openrouter host=Nebius
task=evaluate_meteorite 1.9s stop=end_turn tokens in=4213 out=76
2026-10-08 18:18:46  [INFO]  somerset | dispatch job task completed:
evaluate_meteorite pass:1 fail:0 error:1 (batch:
evaluate_meteorite-2ec6203d-be72-40ff-9fd4-f4787cbddf6d)
2026-10-08 18:18:46  [INFO]  8f127619-7c88-4214-bc9d-5b2ae1361a76 |
job consult completed: METEORITE_PASSED_JD (batch:
evaluate_meteorite-2ec6203d-be72-40ff-9fd4-f4787cbddf6d)
2026-10-08 18:18:46  [INFO]  LLM openrouter host=Nebius
task=evaluate_meteorite 1.5s stop=end_turn tokens in=1026 out=172
```

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
