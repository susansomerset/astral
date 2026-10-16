# AST-2116 — [✅/Somerset] meteorite_grade_do COMPLETED: 1 error(s) / 2 processed | meteorite_grade_do-8c5dd940-9dac-4833-a057-43ac09c2091d

<!-- linear-archive: AST-2116 archived 2026-10-16 -->

## Linear archive (AST-2116)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2116/somerset-meteorite-grade-do-completed-1-errors-2-processed-meteorite  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Prior occurrences

* `meteorite_grade_do · hydrate ValueError · No rubric description for vector <V> grade <G>` (evidence: Somerset Do rubric, vector `Process & Systems Design`, grade **F**) — **novel**, diagnosed below. Related (archived and trashed in Linear, so no relation link is possible; see `docs/features/dispatcher/ast-1898-abrams-evaluate-jd-completed-9-errors-9-processed-evaluate-jd-3aebf350-898a-44d8-abf0-43ea2996f7db.md`): AST-1898 has the same message but different evidence (`evaluate_jd`, embedded Quality Check, grade X; fixed by forbidding X for QC). It does not cover this one.

## As-is

The Somerset `meteorite_grade_do` batch `meteorite_grade_do-8c5dd940-…` graded 2 jobs. The model graded Somerset's Do-rubric vector **Process & Systems Design** as **F**. `_lookup_rubric_reason_for_grade` in `src/core/consult.py` found the vector but no F description (there was neither an F row in `grade_descriptions` nor an F line in the trailing grade table), so it raised `ValueError`.

Hydrate runs **once for the whole batch** (`_hydrate_response_jobs_grade_reasons`, called from the batch consult path in `consult.py`). One missing description therefore throws the **entire batch** into `_transition_batch_consult_failures` with `error_state`, which is the error/retry route. Both jobs failed, including whichever one didn't carry the bad grade. The first job went to `METEORITE_PASSED_JD_RETRY`, and the second (already on its retry) went terminal at `METEORITE_FAILED_TECHNICAL_DO`. A retry can never succeed, because the rubric row still has no F text.

Confidence-0 handling today: the encoded decoder (`_decode_payload` in `src/core/agent.py`, added by [AST-2053](https://linear.app/astralcareermatch/issue/AST-2053/fix-normalise-letter-grade-confidence-0-to-1-in-encoded-grade-decode)) rewrites a letter with confidence 0 (`{A-F}0`) to the same letter with confidence 1. That is the sanctioned slip in statute `astral.agent.confidence-bounds`. So an `F0` from the model is kept as `F1` and still goes to hydrate looking for an F description.

## To-be

Susan's rule (2026-10-10), applied to **every** rubric-graded hydrate site (job consult and company prefilter alike):

* **Missing text, confidence > 0.** If the rubric vector has no text for the grade given (e.g. F), add a **warning** to the log and **fail** that individual entity for that task run, using the task's `fail_state`: `METEORITE_FAILED_DO` for `meteorite_grade_do`, `PREFILTER_FAILED` for `prefilter_company`, and so on. It is not an error and not a retry. Other entities in the same batch are unaffected and apply normally.
* **Confidence 0 on any letter.** Treat it as **X** (X0). This replaces AST-2053's `{letter}0 → {letter}1` rewrite.
* **X is always "no signal".** This holds whether or not the vector's rubric has an X row. X never fails hydrate. Its reason is the rubric's X text when one exists, otherwise a fixed "no signal" reason.

Hydrate never invents a reason or maps one letter to another to paper over a missing letter grade. The only exception is that X0 is always readable. As a side effect, AST-1910's embedded Quality Check X no longer errors in hydrate. AST-1910's prompt rule that QC is never X still stands; nothing here removes it.

**Decisions (Susan, 2026-10-10):**

1. X is read as "no signal" whether or not it is explicit in the rubric.
2. Reach: all rubric grades, so every hydrate call site is in scope.
3. Amending statute `astral.agent.confidence-bounds` is approved.

## Proposed steps

1. **X never raises.** In `_lookup_rubric_reason_for_grade` (`src/core/consult.py`), X returns the rubric's X text if present, else a fixed "no signal" reason.
2. **Per-entity hydrate.** Make hydrate per entity instead of per batch. Any entity with a missing-description letter grade (confidence > 0) is pulled out with a warning naming the vector and letter, then transitioned to its task's `fail_state`. The rest of the batch carries on through normal apply. This applies to these sites:
   * Job consult batch path (`consult.py`; today the whole batch goes to `error_state`).
   * Single-row job apply, `_apply_render_verdict_decoded_job` (today it raises).
   * Company prefilter batch path in `src/core/roster.py` (today the whole batch goes through `_transition_prefilter_batch_failures` with `fail_class="hydrate"`).
   * Single-company prefilter apply, `_apply_prefilter_decoded_company_outcome` (today it raises).
3. **Confidence 0 → X0.** In `_decode_payload`'s non-vet encoded loop (`src/core/agent.py`), rewrite `{letter}0` to `X0` instead of `{letter}1`. The vet branch (`grades_encoded_vet_meta`) is unchanged, since it uses one fixed `LT` vector, not a rubric.
4. **Statute.** Amend `astral.agent.confidence-bounds` (letter0 → X0; X is always no-signal). Betty updates the AST-2053 entry in `docs/test-bible/core/agent.md` and adds coverage.
5. **Ops, separate from the code fix:** give Somerset's Process & Systems Design vector an F row on Artifacts → Do Job Criteria, so a real F is described rather than failed. Then re-run the two jobs.

## Component scope

* `src/core/consult.py`: modified. X hydrate never raises. The job batch consult path and the single-row apply path fail only the affected entity (with a warning) on a missing letter-grade description, instead of erroring or retrying the batch.
* `src/core/roster.py`: modified. The company prefilter batch path and the single-company apply path get the same per-entity fail routing. The prefilter notes builder (which already returns `None` on a hydrate `ValueError`) is checked for consistency.
* `src/core/agent.py`: modified. `_decode_payload` maps letter grades with confidence 0 to X0 instead of letter-with-confidence-1.
* `canon/directives/draft/stat.agent.confidence-bounds.md`: modified. This is the live statute text AST-2053 amended. Letter0 → X0 replaces the letter0 → letter1 sanctioned slip, and X is stated as always no-signal.
* `canon/statutes/astral/agent/astral.agent.confidence-bounds.md`: modified. This harvest copy of the same statute id gets the same statement, so the two copies don't disagree.
* `tests/component/core/test_consult.py`, `tests/component/core/test_agent.py`, `docs/test-bible/core/agent.md`, plus roster prefilter tests (Betty's tree): modified. Coverage for:
  * per-entity fail on a missing description, with batch siblings still applying;
  * X hydrating with no X row;
  * letter0 → X0.

## Technical scope

* `src/core/consult.py`:
  * **Lookup:** `_lookup_rubric_reason_for_grade` gets an X fallback reason.
  * **Hydrate helpers:** they report which entities have a missing description instead of raising once for the batch.
  * **Batch consult caller:** routes those entities to `fail_state` through the existing state-transition helper, with one warning log per entity, and lets the rest apply.
  * **Single-row apply:** `_apply_render_verdict_decoded_job` routes the same condition to fail instead of raising.
  * **Why:** today one missing row errors and retries every job in the batch, and a retry can't fix missing rubric text.
* `src/core/roster.py`: modified functions at the company prefilter batch hydrate site and in `_apply_prefilter_decoded_company_outcome`. Same per-entity routing to the prefilter `fail_state`, because the rule covers all rubric grades.
* `src/core/agent.py`: one-branch change in the non-vet encoded loop of `_decode_payload`, so confidence 0 on a letter becomes X0, per Susan's rule.
* `canon/directives/draft/stat.agent.confidence-bounds.md` and `canon/statutes/astral/agent/astral.agent.confidence-bounds.md`: the same text amendment to the sanctioned-slip rule in both copies of `astral.agent.confidence-bounds`. No code.

## Ancestor candidates

- [X] [AST-2053](https://linear.app/astralcareermatch/issue/AST-2053) — fix: normalise letter-grade confidence 0 to 1 in encoded grade decode (Done, Hedy; parent [AST-2045](https://linear.app/astralcareermatch/issue/AST-2045/somerset-evaluate-meteorite-completed-1-errors-2-processed-evaluate)). Owns the exact decode branch Susan's X0 rule replaces. No feature doc in `docs/features/`; it's described in `docs/test-bible/core/agent.md`.
- [ ] AST-1063 — job-carried rubric hydration for list columns (`docs/features/interface/ast-1063-job-carried-rubric-hydration-for-list-columns.md`): owns the hydrate/snapshot path being made per-entity
- [ ] AST-1154 — rubric completeness contracts, all graded tasks (`docs/features/consult/ast-1154-rubric-completeness-contracts-all-graded-tasks.md`): owns the `astral.agent.confidence-bounds` "silence → X0" contract; its sibling AST-1155 owns consult retry routing
- [ ] [AST-1513](<https://linear.app/astralcareermatch/issue/AST-1513/reject-duplicate-do-rubric-codes-meteorite-grade-do-is-failing>) — reject duplicate Do rubric codes, meteorite_grade_do failing (`docs/features/consult/ast-1513-reject-duplicate-do-rubric-codes-meteorite-grade-do-is-failing.md`): same candidate, task, and rubric-data shape
- [ ] AST-1910 — forbid X grade for Quality Check (`docs/features/dispatcher/ast-1910-forbid-x-grade-for-quality-check-in-evaluate-jd-qc-hydrate-error.md`): earlier hydrate-strict decision; precedent only
- [ ] [AST-2091](https://linear.app/astralcareermatch/issue/AST-2091) — block Auto/Run on duplicate or empty rubric (User Testing, Hedy). Demoted: Susan's rule handles this at grade time, not with a dispatch preflight.

---

## Original report

```
2026-10-09 22:15:48  [INFO]  somerset | dispatch job task completed:
meteorite_grade_do pass:0 fail:0 error:1 (batch:
meteorite_grade_do-8c5dd940-9dac-4833-a057-43ac09c2091d)
2026-10-09 22:15:48  [WARNING]  1fea8e7e-33f2-4ffa-be71-94ada9e6ce7d
-> METEORITE_PASSED_JD_RETRY [hydrate: No rubric description for
vector 'Process & Systems Design' grade F]
2026-10-09 22:15:48  [ERROR]  2903fb71-4056-4c9b-9d9d-ef4090018ebb ->
METEORITE_FAILED_TECHNICAL_DO [hydrate: No rubric description for
vector 'Process & Systems Design' grade F]
2026-10-09 22:15:48  [INFO]  LLM openrouter host=Parasail
task=meteorite_grade_do 5.2s stop=end_turn tokens in=9245 out=130
2026-10-09 22:15:48  [INFO]  somerset | dispatch job starting
meteorite_grade_do — 2 available (batch:
meteorite_grade_do-8c5dd940-9dac-4833-a057-43ac09c2091d)
```

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
