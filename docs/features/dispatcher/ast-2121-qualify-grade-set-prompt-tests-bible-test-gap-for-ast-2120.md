# AST-2121 — qualify grade-set prompt tests + bible (test gap for AST-2120)

<!-- linear-archive: AST-2121 archived 2026-10-16 -->

## Linear archive (AST-2121)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2121/qualify-grade-set-prompt-tests-bible-test-gap-for-ast-2120  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 1  
**Parent:** AST-2108 — [✅/Johnson] qualify_job_listings COMPLETED: 5 error(s) / 21 processed | qualify_job_listings-11d238b6-ff14-4a1a-8f00-29542e2a2db7  
**Blocked by / blocks / related:** parent: AST-2108

### Description

## What this implements

Test gap for [AST-2120](https://linear.app/astralcareermatch/issue/AST-2120) (fix-board `[board-betty] TESTS: REVISE`), the fix for [AST-2108](https://linear.app/astralcareermatch/issue/AST-2108). Add a `[bug-repro]` that pins the qualify prompt's illustrative-code-count sentence, the metadata-only omit rule, and the shared `_ENCODED_GRADE_SET_COMPLETENESS` addition. It must fail on the pre-fix tree and pass once AST-2120 lands. Also resolve the already-red catalog-side AST-1154 marker test without re-adding a ticket id to the prompt. Update the bible entries to match.

## Betty's verdict (verbatim)

> \[board-betty\] TESTS: REVISE
> What: docs/test-bible/core/ + utils/ (AST-1154 blocks: `TestAst1154GradedTaskCompletenessPrompts`, `TestAst1154EncodedGradeSetCompleteness`) — missing repro coverage — no test catches the bug: every green AST-1154 test passes both before and after the fix, so nothing pins the illustrative-count sentence or the metadata-only omit rule.
>
> **Breaks nothing (checked against d911ce22b):** the plan keeps every pinned phrase intact (`GRADE SET COMPLETENESS (AST-1154)`, `{code}X0`, `never skip that segment`, `Every rubric vector code must appear exactly once per job line`, `never omit a code`). The constant stays absent from vet_meta/grades_json. No test pins the 7-code STEP 4 / COMPANY JOB IDENTIFIER examples, the old `Omit any data whose value is not stated` sentence, or exact `payload_instructions` text. The per-row catalog↔fixture `cache_prompt ==` lockstep tests cover `meteorite_email` / `evaluate_jd` / `stage_meteorite` / `qualify_meteorite`, not `qualify_job_listings`. The `qualify_job_listings` hits elsewhere in `test_repo_admin_json.py` are set-membership only.
>
> **Already red on the tip, not caused by this fix:** `test_marker_and_tighten_lines_on_graded_cache_prompts` (catalog marker stripped by c06eaefdf), `TestAst1494…::test_fixture_byte_identical_to_catalog`, and `TestAst1773…::test_fixture_catalog_byte_lockstep`.
>
> **qa-fix scope:**
>
> 1. Write a repro test that fails on the current tree and passes once the plan's § Proposed change lands. It checks the current `qualify_job_listings` `cache_prompt` for three things: the illustrative-code-count sentence is present, the metadata-only omit sentence (`never to grade segments`) is present, and `Omit any data whose value is not stated` is gone. It also checks that `_ENCODED_GRADE_SET_COMPLETENESS` (`their code count is not a template`) appears on exactly the four multi-vector types.
> 2. Decide what to do with the red catalog-side `test_marker_and_tighten_lines_on_graded_cache_prompts`. The plan's Blast radius hands this to Betty, and it is the existing check on this row's completeness contract. Do not re-add a ticket id to the prompt.

## Citations

none. Test tree and bible only.

## Scope

### Component scope

* `tests/component/core/test_repo_admin_json.py` (modified): the AST-1154 catalog prompt checks (`TestAst1154GradedTaskCompletenessPrompts`, incl. the red `test_marker_and_tighten_lines_on_graded_cache_prompts`). New `[bug-repro]` for the `qualify_job_listings` `cache_prompt` wording.
* `tests/component/utils/test_config.py` (modified): `TestAst1154EncodedGradeSetCompleteness`. Assert the added `_ENCODED_GRADE_SET_COMPLETENESS` sentence appears on exactly the four multi-vector output types.
* `docs/test-bible/core/repo_admin_json.md` (modified): AST-1154 block, manifest lines for the new/revised tests.
* `docs/test-bible/utils/config.md` (modified): AST-1154 block, manifest line for the shared-constant assertion.

### Technical scope

* `tests/component/core/test_repo_admin_json.py`: new test(s) plus a revised marker test in the AST-1154 class. They are prompt-text assertions on the repo catalog row, with no product function change.
* `tests/component/utils/test_config.py`: new or extended test in `TestAst1154EncodedGradeSetCompleteness`. It is a constant-text and output-type membership assertion.
* `docs/test-bible/core/repo_admin_json.md`, `docs/test-bible/utils/config.md`: modified sections, the manifest nodes for the new and revised tests.

## Boundaries

No product `src/` or `data/` change. The product fix is AST-2120. The test tree is Betty's (`qa-fix`). The engineer side is a plan marker plus `test-fix` verification. Do not touch the AST-756 fixture byte-identity tests (pre-existing red, out of scope).

## Git branch (authoritative)

Mini-parent `ftr/AST-2108-qualify-missing-grade-vectors`, child `sub/AST-2108/<this-ticket>-qualify-grade-set-tests`. Created at bug-fix.

### Comments

#### radia — 2026-10-10T02:41:55.769Z
[code-rubric] PROCEED (Commit: 9de72e3eb) Repro pins AST-2120 prompt bar

Clean. `astral.standards.names-not-ticket-ids` got an A. `[bug-repro]` is OK: the two new tests check the illustrative-count line, the metadata-only omit rule, and the shared constant on exactly the four multi-vector types. `## What must still hold` is OK, and nothing changed under src/ or data/. Full artifact: AST-1154 doc § Radia review — AST-2121 (F7).

#### betty — 2026-10-10T02:39:43.633Z
[bug-repro]
`origin/sub/AST-2108/AST-2121-qualify-grade-set-tests` @ `834f07a40` · red on 27cd7cbcf, green tip

Repro nodes + manifest: `docs/test-bible/utils/config.md` § AST-2121 · AST-2108 (`## QA test manifest`). Recorded in the bible, not the issue doc: the Betty hook blocks `docs/features/`.

#### joan — 2026-10-10T02:38:02.811Z
[board-joan] CANON: OK

No statute or pattern needs to change. The edits are tests and bible only. Moving the catalog marker assertion to the ticket-free `## GRADE SET COMPLETENESS` heading follows `astral.standards.names-not-ticket-ids`. Full findings: AST-1154 doc § Fix board — Joan (F2) — AST-2121.

#### betty — 2026-10-10T02:37:50.938Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/repo_admin_json.md + docs/test-bible/utils/config.md (AST-1154 blocks) — missing repro coverage + one stale red test — this ticket is entirely test-tree work, so qa-fix lands it, not make-fix. The plan's bar is sound as written.

**Checked read-only against the pre-fix base `27cd7cbcf` and the ftr tip `6ad17bcbb`:**
- All five new `qualify_job_listings` phrases and the removal of `Omit any data whose value is not stated` are False on the base and True on the tip, so item 1 works as a real `[bug-repro]`.
- `their code count is not a template` appears 0 times in `src/utils/config.py` on the base and once on the tip, so item 2 is a valid second repro node.
- `"AST-" not in prompt` is True on both trees. It's a regression guard only, as the plan says.
- `## GRADE SET COMPLETENESS` is present on all 7 graded catalog rows on both trees, so item 3's ticket-free catalog marker turns the stale red test green without weakening anything.
- The AST-756 fixture still carries `GRADE SET COMPLETENESS (AST-1154)` on all 7 rows, so leaving `test_fixture_graded_keys_carry_completeness_marker` as is stays correct.
- The bible manifests that list `TestAst1154GradedTaskCompletenessPrompts` exist at `repo_admin_json.md` ~274 / ~750 and `config.md` ~2608–2618. Class-level nodes pick up the new methods, and the config.md prose ("same AST-1154 marker") needs the rewording in item 4.

**No product change needed or allowed.** AST-756 byte-identity reds (`TestAst1494…`, `TestAst1773…`) stay out of scope.

#### ada — 2026-10-10T02:37:15.560Z
`origin/sub/AST-2108/AST-2121-qualify-grade-set-tests` @ `ef2ad8e6b` · repro bar, ticket-free marker

---

_Implementation detail may live in git history on `origin/dev`._
