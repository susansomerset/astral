# AST-2108 — [✅/Johnson] qualify_job_listings COMPLETED: 5 error(s) / 21 processed | qualify_job_listings-11d238b6-ff14-4a1a-8f00-29542e2a2db7

<!-- linear-archive: AST-2108 archived 2026-10-16 -->

## Linear archive (AST-2108)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2108/johnson-qualify-job-listings-completed-5-errors-21-processed-qualify  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Prior occurrences

* `qualify_job_listings · IncompleteGradeSetError · _render_score: missing vectors [<rubric labels>]`, evidence: the model's encoded lines leave out the same two Johnson joblist-rubric vectors (`Full-Time W2 Employment`, and in 8 of 9 cases also `Minimum Base Salary`). **Novel**, diagnosed below.
* none found (3 searches). I opened AST-2014, AST-2015, AST-2019, AST-2020, and AST-2021, and none of them covers this. AST-2014 and AST-2015 are whole-hop envelope or decode failures. AST-2019 and AST-2020 are empty `RUBRIC_VECTORS`. AST-2021 is a `|` inside a job title shifting `job_link`. One search hit I didn't open, because I ran out of lookups: [AST-1885](https://linear.app/astralcareermatch/issue/AST-1885) (Canceled, Abrams `qualify_job_listings`, 2026-09-29, 50/50 errors, matched on "missing vectors"). If it turns out to be the same thing, this ticket is a duplicate of it.
* Not treated as a failure: 12 jobs went `NEW_RETRY [omitted from response]` (whole listings dropped). That's a first-strike warning only, and it's the same retry-once behavior AST-2014/AST-2015 already discussed.

## As-is

A Johnson `qualify_job_listings` batch (`qualify_job_listings-11d238b6…`, 2026-10-09 06:13) processed 21 jobs: 0 pass, 0 fail, 5 errors. For 9 of the jobs, the model returned encoded grade lines with rubric codes **missing**. Eight lines were missing both `Full-Time W2 Employment` and `Minimum Base Salary`, and one was missing only `Full-Time W2 Employment`. `_require_complete_grade_set` in `src/core/consult.py` raised `IncompleteGradeSetError: _render_score: missing vectors […]` for each of them. AST-1155's routing then did its job:

* the 4 jobs on their first strike went to `NEW_RETRY`;
* the 5 jobs already in retry holding went to the terminal `ERROR_QUALIFY_JOB_LISTINGS`.

The routing works as designed. The problem is upstream: the model keeps leaving out the same two codes, even though the prompt already carries AST-1154's completeness contract three times (STEP 4, `## GRADE SET COMPLETENESS`, and `_ENCODED_GRADE_SET_COMPLETENESS` in `{$OUTPUT_INSTRUCTIONS}`). Because the same two codes go missing on every bad line, this looks systematic, not random. There's no `duplicate rubric codes` warning in the log, and one line is missing only one of the two codes, so a code collision in `_vector_labels_map` is unlikely.

Two hypotheses, which I can't tell apart without the DB or the stored response block:

1. **The model stops after a fixed number of codes.** Every grade example the model sees has exactly **7** segments (`ERA4|MEA4|PGF4|WAA3|MWA3|KOA4|QCA5` in STEP 4 and in the COMPANY JOB IDENTIFIER example, plus three 7-code lines in the `grades_encoded_meta` payload instructions in `src/utils/config.py`). If Johnson's joblist rubric has more than 7 vectors, with `Minimum Base Salary` and `Full-Time W2 Employment` as the last two in that order, a model copying the example length would drop exactly these codes. That also explains the one line missing only `Full-Time W2 Employment` (only the last code dropped).
2. **"Omit unstated data" is being applied to grades.** The `## EXTRACT METADATA` section says "Omit any data whose value is not stated — do NOT guess or infer", and its example uses `salary_range`. Salary and W2/employment type are exactly what a job-board listing usually doesn't state. The model may be applying the metadata "omit" rule to these two grade vectors instead of emitting `X0`.

Neither recent prompt edit introduced this. `2ea8ca006` changed STEP 3 and fixed a typo. `f3897829d` (AST-2089) made the job ID best-effort. Neither touched the grade examples or the "omit" line. A rubric change on Johnson's side (these two vectors added recently) would make either hypothesis show up now.

## To-be

Every `qualify_job_listings` line carries one grade segment for **every** code in the candidate's live joblist rubric, however many vectors there are. When a listing doesn't state salary or employment type, the vector is graded `{code}X0`, not omitted. Johnson's batches stop sending well-graded listings to retry and then to `ERROR_QUALIFY_JOB_LISTINGS` for missing codes.

## Proposed steps

1. **Confirm which hypothesis applies (read-only):** pull Johnson's current `rubric_vector` rows for owner `qualify_job_listings`. Check the vector count, the order, the codes for the two missing vectors, and when they were created. Then pull the stored response block for this batch (`_store_response_block`, index `qualify_job_listings_batch_qualify_job_listings-11d238b6…`) to see the raw encoded lines. If the codes are absent from the tail, it's hypothesis 1. If they're absent from the middle and the lines carry `salary_range`-style metadata, it's hypothesis 2.
2. **Hypothesis 1 fix:** in the `qualify_job_listings` `cache_prompt` (`data/admin/agent_task.json`), make the examples say they're illustrative and that a line carries **one segment per rubric code, in rubric order, as many as the rubric lists**. If the 7-code examples in `grades_encoded_meta` (`src/utils/config.py`) are the anchor, add the same sentence to `_ENCODED_GRADE_SET_COMPLETENESS`.
3. **Hypothesis 2 fix:** in `## EXTRACT METADATA`, limit "Omit any data whose value is not stated" to metadata key/value pairs only, and add a line that vectors about salary or employment type are still graded, with `X0` when unstated.
4. Sync the prompt row to the DB the usual way, then optionally reset the 5 `ERROR_QUALIFY_JOB_LISTINGS` jobs from this batch (`d1a4ad6c…`, `2595edb2…`, `02b00d9b…`, `3b3efc56…`, `a995bac1…`) to `NEW` as a one-off data fix.
5. **Open for Susan:** should a rubric over a certain size get a code-side guard (for example, a prompt token that renders the expected code count or code list per line)? Or is a prompt-copy fix enough? I'd start with prompt copy only.

## Component scope

`data/admin/agent_task.json` (modified) holds the `qualify_job_listings` row's `cache_prompt`, which contains the 7-code grade examples and the "omit unstated data" metadata rule. Both hypotheses are fixed here.

`src/utils/config.py` (modified only if step 1 points at the shared payload instructions) holds `_ENCODED_GRADE_SET_COMPLETENESS` and the `grades_encoded_meta` 7-code examples injected through `{$OUTPUT_INSTRUCTIONS}`.

`src/core/consult.py` (expected unchanged) does the completeness check and retry/error routing (`_require_complete_grade_set`, `_run_batch_consult`). That code is correct and is listed so `plan-fix` can confirm it stays untouched.

## Technical scope

`data/admin/agent_task.json`: prompt-text change only on the `qualify_job_listings` row. The grade examples get a variable-length clarification, and/or the metadata "omit" rule is limited to key/value pairs. No schema, table, or field changes.

`src/utils/config.py` (conditional): modified constant `_ENCODED_GRADE_SET_COMPLETENESS`, one added sentence saying the segment count follows the rubric, not the examples. That carries the fix to every `grades_encoded*` task that shares it. No new functions.

## Ancestor candidates

- [X] AST-1154: rubric completeness contracts for all graded tasks (`docs/features/consult/ast-1154-rubric-completeness-contracts-all-graded-tasks.md`). Owns the "every rubric code must appear, X0 when silent" prompt contract that the model isn't following here. This is the direct ancestor for a prompt-side fix.
- [ ] AST-1155: incomplete grades go to retry holding, never technical fail (`docs/features/consult/ast-1155-incomplete-grades-retry-holding-never-technical-fail.md`). Owns the `missing vectors` gate and the retry-then-error routing seen in this log. It's working as designed and is context for why 5 jobs ended at ERROR.
- [ ] AST-1760: all-X scored grades go to retry holding (`docs/features/consult/ast-1760-all-x-scored-grades-retry-holding.md`). A sibling `IncompleteGradeSetError` path, relevant if the fix pushes the model toward heavier `X0` use.
- [ ] AST-378: runtime rubric validation (`docs/features/auditor/ast-378-runtime-rubric-validation.md`). The live-rubric-vs-grades validation lineage, relevant if step 5's code-side guard is wanted.
- [ ] AST-1885: possible prior occurrence (Canceled, 2026-09-29), not opened this round. Check this box if you want me to open it next round.

## Original report

```
2026-10-09 06:12:23  [INFO]  johnson | dispatch job starting
qualify_job_listings — 21 available (batch:
qualify_job_listings-11d238b6-ff14-4a1a-8f00-29542e2a2db7)
2026-10-09 06:13:09  [INFO]  johnson | dispatch job task completed:
qualify_job_listings pass:0 fail:0 error:5 (batch:
qualify_job_listings-11d238b6-ff14-4a1a-8f00-29542e2a2db7)
2026-10-09 06:13:09  [INFO]  johnson | dispatch job stopping
qualify_job_listings — 17 remaining after 1 run(s)
2026-10-09 06:13:09  [WARNING]  4d64ec5a-3872-4e33-955e-58cdd0bf8219
-> NEW_RETRY [process_fn IncompleteGradeSetError: _render_score:
missing vectors ['Full-Time W2 Employment']]
2026-10-09 06:13:09  [INFO]  LLM openrouter host=Parasail
task=qualify_job_listings 5.0s stop=end_turn tokens in=3379 out=155
2026-10-09 06:13:09  [WARNING]  b8ab9cb4-6c75-4777-9718-0092a2f5cc57
-> NEW_RETRY [process_fn IncompleteGradeSetError: _render_score:
missing vectors ['Full-Time W2 Employment', 'Minimum Base Salary']]
2026-10-09 06:13:09  [WARNING]  526aa1ec-eb84-4141-9bb9-01240c920593
-> NEW_RETRY [process_fn IncompleteGradeSetError: _render_score:
missing vectors ['Full-Time W2 Employment', 'Minimum Base Salary']]
2026-10-09 06:13:09  [WARNING]  ef714ec9-12d7-46bf-993f-a78f995000c4
-> NEW_RETRY [process_fn IncompleteGradeSetError: _render_score:
missing vectors ['Full-Time W2 Employment', 'Minimum Base Salary']]
2026-10-09 06:13:09  [ERROR]  d1a4ad6c-f8e6-4f71-b410-4beb10b3bfde ->
ERROR_QUALIFY_JOB_LISTINGS [process_fn IncompleteGradeSetError:
_render_score: missing vectors ['Full-Time W2 Employment', 'Minimum
Base Salary']]
2026-10-09 06:13:09  [ERROR]  2595edb2-bb56-4532-ba93-aa868ec83156 ->
ERROR_QUALIFY_JOB_LISTINGS [process_fn IncompleteGradeSetError:
_render_score: missing vectors ['Full-Time W2 Employment', 'Minimum
Base Salary']]
2026-10-09 06:13:09  [ERROR]  02b00d9b-aa01-47e2-a022-a1c681d1b523 ->
ERROR_QUALIFY_JOB_LISTINGS [process_fn IncompleteGradeSetError:
_render_score: missing vectors ['Full-Time W2 Employment', 'Minimum
Base Salary']]
2026-10-09 06:13:09  [ERROR]  3b3efc56-d464-4110-a3b3-1000b13b25dc ->
ERROR_QUALIFY_JOB_LISTINGS [process_fn IncompleteGradeSetError:
_render_score: missing vectors ['Full-Time W2 Employment', 'Minimum
Base Salary']]
2026-10-09 06:13:09  [ERROR]  a995bac1-9041-4b94-9c08-8b1f9d950b14 ->
ERROR_QUALIFY_JOB_LISTINGS [process_fn IncompleteGradeSetError:
_render_score: missing vectors ['Full-Time W2 Employment', 'Minimum
Base Salary']]
2026-10-09 06:13:09  [WARNING]  14424168-f515-45fd-9bb1-01a40889a411
-> NEW_RETRY [omitted from response]
2026-10-09 06:13:09  [WARNING]  e1c76d18-996b-47d9-956b-1262efc1ec47
-> NEW_RETRY [omitted from response]
2026-10-09 06:13:09  [WARNING]  7c9b9da7-207d-4ad9-8161-b5bb33e7e157
-> NEW_RETRY [omitted from response]
2026-10-09 06:13:09  [WARNING]  099d9978-a4af-4106-bdf4-ea5653b345ae
-> NEW_RETRY [omitted from response]
2026-10-09 06:13:09  [WARNING]  cc76614f-1df2-4126-a847-72643b627ba1
-> NEW_RETRY [omitted from response]
2026-10-09 06:13:09  [WARNING]  dfe61283-1ad1-4319-b804-790965e88d75
-> NEW_RETRY [omitted from response]
2026-10-09 06:13:09  [WARNING]  db78e08a-8cbe-44e5-9189-3efb3243a6b4
-> NEW_RETRY [omitted from response]
2026-10-09 06:13:09  [WARNING]  7eb558b0-4c89-4305-b0b7-6d3818cabd2b
-> NEW_RETRY [omitted from response]
2026-10-09 06:13:09  [WARNING]  87a81de2-f1a4-44fa-bbb4-2b1c7f955281
-> NEW_RETRY [omitted from response]
2026-10-09 06:13:09  [WARNING]  bd4a1494-2353-4678-b13f-934d12f3e6d9
-> NEW_RETRY [omitted from response]
2026-10-09 06:13:09  [WARNING]  54b42348-7409-4991-ad9c-09bad1b3a6c7
-> NEW_RETRY [omitted from response]
2026-10-09 06:13:09  [WARNING]  ac2f3b3d-8d0e-4ca2-8aa1-c4bb8118e40e
-> NEW_RETRY [omitted from response]
2026-10-09 06:13:09  [INFO]  LLM openrouter host=Parasail
task=qualify_job_listings 32.4s stop=end_turn tokens in=19645 out=1043
```

### Comments

#### chuckles — 2026-10-09T06:54:19.750Z
Recurred: [AST-2111](https://linear.app/astralcareermatch/issue/AST-2111) — qualify_job_listings-3ef18c5d-09b6-4b0e-ac63-bb93c2269704, 2026-10-09 06:52:33.

#### chuckles — 2026-10-09T06:21:29.699Z
Recurred: [AST-2109](https://linear.app/astralcareermatch/issue/AST-2109) — qualify_job_listings-1fffa4b2-f8e7-42d7-a442-458404a84652, 2026-10-09 06:20:00.

---

_Implementation detail may live in git history on `origin/dev`._
