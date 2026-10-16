# AST-2120 — fix: every qualify grade line carries the full rubric code set (AST-2108)

<!-- linear-archive: AST-2120 archived 2026-10-16 -->

## Linear archive (AST-2120)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2120/fix-every-qualify-grade-line-carries-the-full-rubric-code-set-ast-2108  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-2108 — [✅/Johnson] qualify_job_listings COMPLETED: 5 error(s) / 21 processed | qualify_job_listings-11d238b6-ff14-4a1a-8f00-29542e2a2db7  
**Blocked by / blocks / related:** parent: AST-2108

### Description

## What this implements

Fix for [AST-2108](https://linear.app/astralcareermatch/issue/AST-2108): `qualify_job_listings` encoded grade lines must carry one segment for **every** code in the candidate's live joblist rubric. Johnson's batches keep leaving out `Full-Time W2 Employment` / `Minimum Base Salary`, which sends well-graded listings to `NEW_RETRY` and then `ERROR_QUALIFY_JOB_LISTINGS`. Recurred as [AST-2109](https://linear.app/astralcareermatch/issue/AST-2109) and [AST-2111](https://linear.app/astralcareermatch/issue/AST-2111) (both duplicates of AST-2108).

## Ancestor (Susan-approved)

AST-1154: rubric completeness contracts for all graded tasks (`docs/features/consult/ast-1154-rubric-completeness-contracts-all-graded-tasks.md`). It owns the "every rubric code must appear, X0 when silent" prompt contract that the model isn't following here. The AST-1154 Linear ticket is archived, so there is no live ticket to link. Patch that doc.

## As-is

For 9 of 21 jobs in batch `qualify_job_listings-11d238b6…`, the model's encoded lines had rubric codes **missing**. Eight lines were missing both `Full-Time W2 Employment` and `Minimum Base Salary`, and one was missing only `Full-Time W2 Employment`. `_require_complete_grade_set` (`src/core/consult.py`) raised `IncompleteGradeSetError: _render_score: missing vectors […]`. Under AST-1155 routing, that sends a job to `NEW_RETRY` on the first strike and to `ERROR_QUALIFY_JOB_LISTINGS` on the second. The routing is correct. The completeness contract is already in the prompt three times, and the model still omits the same codes.

Two hypotheses from bug-find, still unconfirmed:

1. **The model stops after a fixed number of codes.** Every grade example in the qualify prompt and in the `grades_encoded_meta` payload instructions has exactly 7 segments. A rubric with more than 7 vectors whose last codes are these two would be cut at the tail.
2. **"Omit unstated data" is being applied to grades.** `## EXTRACT METADATA` says "Omit any data whose value is not stated — do NOT guess or infer" (its example is `salary_range`). The model may be applying that rule to salary and W2 grade vectors instead of emitting `X0`.

## To-be

Every `qualify_job_listings` line carries one grade segment per live-rubric code, however many there are. Unstated salary or employment type grades `{code}X0` and is never omitted.

## Proposed steps

1. Confirm which hypothesis applies (read-only): check Johnson's `rubric_vector` rows for owner `qualify_job_listings` (count, order, codes, created dates) and the stored response block for this batch.
2. Hypothesis 1: say in the qualify `cache_prompt` that the examples are illustrative, with one segment per rubric code, in rubric order, as many as the rubric lists. If the shared examples are the anchor, add the same sentence to `_ENCODED_GRADE_SET_COMPLETENESS`.
3. Hypothesis 2: limit "Omit any data whose value is not stated" to metadata key/value pairs only, and add that salary and employment-type vectors are still graded, with `X0` when unstated.
4. Sync the prompt row to the DB. Optionally reset the 5 errored jobs to `NEW`.

## Citations

none. `plan-fix` resolves Canon Scope from the touched files.

## Scope

### Component scope

`data/admin/agent_task.json` (modified) holds the `qualify_job_listings` row's `cache_prompt`, which contains the 7-code grade examples and the "omit unstated data" metadata rule. Both hypotheses are fixed here.

`src/utils/config.py` (modified only if step 1 points at the shared payload instructions) holds `_ENCODED_GRADE_SET_COMPLETENESS` and the `grades_encoded_meta` 7-code examples injected through `{$OUTPUT_INSTRUCTIONS}`.

`src/core/consult.py` (expected unchanged) does the completeness check and retry/error routing (`_require_complete_grade_set`, `_run_batch_consult`). That code is correct and is listed so `plan-fix` can confirm it stays untouched.

### Technical scope

`data/admin/agent_task.json`: prompt-text change only on the `qualify_job_listings` row. The grade examples get a variable-length clarification, and/or the metadata "omit" rule is limited to key/value pairs. No schema, table, or field changes.

`src/utils/config.py` (conditional): modified constant `_ENCODED_GRADE_SET_COMPLETENESS`, one added sentence saying the segment count follows the rubric, not the examples. That carries the fix to every `grades_encoded*` task that shares it. No new functions.

## Git branch (authoritative)

Bug mini-parent `ftr/AST-2108-qualify-missing-grade-vectors`, child `sub/AST-2108/<this-ticket>-qualify-missing-grade-vectors`. Registry: `epic_registry.py show AST-2108`.

### Comments

#### radia — 2026-10-10T02:35:48.177Z
[code-rubric] PROCEED (Commit: f47d996b2) Prompt copy closes both hypotheses

Clean. Every scored statute got an A (seed agent tables, config source of truth, names not ticket ids). `## What must still hold` is OK. `[bug-repro]` is not applicable because that coverage is on [AST-2121](https://linear.app/astralcareermatch/issue/AST-2121). Full artifact: AST-1154 doc § Radia review — AST-2120 (F7).

#### joan — 2026-10-10T02:32:07.065Z
[board-joan] CANON: OK

No statute or pattern needs to change. The edits to the qualify prompt and `_ENCODED_GRADE_SET_COMPLETENESS` fit `astral.seed.agent-tables-in-repo-json`, `astral.config.config-source-of-truth`, and `astral.standards.names-not-ticket-ids`. `consult.py` validation is untouched. Full findings: AST-1154 doc § Fix board — Joan (F2), commit `8f82746ea`.

#### betty — 2026-10-10T02:31:32.487Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/ + utils/ (AST-1154 blocks: `TestAst1154GradedTaskCompletenessPrompts`, `TestAst1154EncodedGradeSetCompleteness`) — missing repro coverage — no test catches the bug: every green AST-1154 test passes both before and after the fix, so nothing pins the illustrative-count sentence or the metadata-only omit rule.

**Breaks nothing (checked against d911ce22b):** the plan keeps every pinned phrase intact (`GRADE SET COMPLETENESS (AST-1154)`, `{code}X0`, `never skip that segment`, `Every rubric vector code must appear exactly once per job line`, `never omit a code`). The constant stays absent from vet_meta/grades_json. No test pins the 7-code STEP 4 / COMPANY JOB IDENTIFIER examples, the old `Omit any data whose value is not stated` sentence, or exact `payload_instructions` text. The per-row catalog↔fixture `cache_prompt ==` lockstep tests cover `meteorite_email` / `evaluate_jd` / `stage_meteorite` / `qualify_meteorite`, not `qualify_job_listings`. The `qualify_job_listings` hits elsewhere in `test_repo_admin_json.py` are set-membership only.

**Already red on the tip, not caused by this fix:** `test_marker_and_tighten_lines_on_graded_cache_prompts` (catalog marker stripped by c06eaefdf), `TestAst1494…::test_fixture_byte_identical_to_catalog`, and `TestAst1773…::test_fixture_catalog_byte_lockstep`.

**qa-fix scope:**
1. Write a repro test that fails on the current tree and passes once the plan's § Proposed change lands. It checks the current `qualify_job_listings` `cache_prompt` for three things: the illustrative-code-count sentence is present, the metadata-only omit sentence (`never to grade segments`) is present, and `Omit any data whose value is not stated` is gone. It also checks that `_ENCODED_GRADE_SET_COMPLETENESS` (`their code count is not a template`) appears on exactly the four multi-vector types.
2. Decide what to do with the red catalog-side `test_marker_and_tighten_lines_on_graded_cache_prompts`. The plan's Blast radius hands this to Betty, and it is the existing check on this row's completeness contract. Do not re-add a ticket id to the prompt.

#### ada — 2026-10-10T02:30:12.536Z
`origin/sub/AST-2108/AST-2120-qualify-missing-grade-vectors` @ `d911ce22b` · closes both hypotheses, prompt-only

---

_Implementation detail may live in git history on `origin/dev`._
