# AST-1882 — gap: tests for Reality Check as persisted default prefilter vector (AST-1881 board)

<!-- linear-archive: AST-1882 archived 2026-10-07 -->

## Linear archive (AST-1882)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1882/gap-tests-for-reality-check-as-persisted-default-prefilter-vector-ast  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1876 — [✅/Johnson] prefilter_company COMPLETED: 50 error(s) / 50 processed | prefilter_company-6e5f321d-aa8d-4a68-94eb-3efa041a59bd  
**Blocked by / blocks / related:** parent: AST-1876

### Description

## What this implements

Test gap from \[board-betty\] TESTS: REVISE on AST-1881. One existing test breaks under the fix, and the new RC lifecycle has no coverage.

* **Broken:** `tests/component/utils/test_config.py::TestAst707EmbeddedPrefilterConfig::test_embedded_rc_registry` asserts the old "real vs fraudulent" RC wording and the grade list that includes E. The fix switches RC to the company-site scale (A/B/C/D/F/X, no E). Update it to the new contract.
* **New coverage, including a** `[bug-repro]` **that is red on the pre-fix product and green once AST-1881 lands:**
  * The shipped `prefilter_company` `cache_prompt` in `data/admin/agent_task.json` has no hand-written Reality Check block and still contains `{$RUBRIC_VECTORS}`. This is the repro.
  * RC is merged on the save path (`apply_rubric_vectors_save`, owner `prefilter_company`), on craft persist (`_persist_craft_dispatch_success`, artifact `company_prefilter`), and on craft generate (`craft_prefilter_rubric`), so it's stored in `rubric_vector`. Follow the pattern of the AST-1085 QC/GC tests in `test_candidate.py` (around lines 3745–3833).
* **Still passing (checked by Betty, no change needed):** `test_consult.py::TestRubricLookup::test_matches_criterion_by_code`, `test_roster.py::TestAst707EmbeddedRcBatchHydration`, `test_candidate.py::TestAst723RubricVectorsCutover::test_prefilter_merges_embedded_rc_from_table`.

## Scope

### Component scope

* `tests/component/utils/test_config.py` (modified): update `test_embedded_rc_registry` to the company-site RC scale.
* `tests/component/core/test_candidate.py` (modified): RC merge-and-store on save, craft persist, and craft generate, mirroring the AST-1085 QC/GC tests.
* A prompt-data test for `data/admin/agent_task.json` (Betty picks the file): the repro that the `prefilter_company` prompt has no hand-written Reality Check block and keeps `{$RUBRIC_VECTORS}`.
* `docs/test-bible/utils/config.md`, `docs/test-bible/core/candidate.md` (modified): bible entries for the changed and new coverage.

### Technical scope

* Config tests: one modified test function (new RC content and grade list).
* Candidate tests: new test function(s) for each merge path.
* Prompt-data test: new test function; this is the `[bug-repro]`, red before AST-1881's change and green after.
* Test bible: modified entries naming the coverage.

## Boundaries

Test and bible only; product code stays on AST-1881. Betty lands the tests (engineers are banned from the test tree). No limits or caps.

## Notes for planning

Board verdict: \[board-betty\] TESTS: REVISE on AST-1881 (see that comment). Plan doc: docs/features/consult/ast-707-uat-batch-prefilter-embedded-rc-vector-hydration.md (AST-1881's plan-fix section; Joan CANON: OK).

## Git branch (authoritative)

Parent `ftr/AST-1876-prefilter-rc-default-vector`, child `sub/AST-1876/AST-1882-prefilter-rc-default-vector-tests`.

### Comments

#### radia — 2026-09-29T20:10:19.584Z
[code-rubric] PROCEED (Commit: dcea82e5) Gap tests + repro OK

#### hedy — 2026-09-29T20:09:16.643Z
`origin/sub/AST-1876/AST-1882-prefilter-rc-default-vector-tests` @ `dcea82e5` · [bug-repro] red→green confirmed

- `[bug-repro]` `TestAst1881PrefilterRcDefaultVector::test_prefilter_prompt_has_no_hand_written_reality_check`: **red** on `origin/dev` product with this tip's tests (`'Reality Check' not in cache_prompt` fails), **green** on this tip.
- Manifest (5 nodes from `docs/test-bible/core/candidate.md` AST-1881 block): 15 passed.
- Touched-module sweep (`test_config.py`, `test_candidate.py`, `-k "Ast707 or Ast1881 or Rubric or prefilter"` over `test_consult.py` / `test_roster.py`), tip vs `origin/dev`, one tree at a time with separate `ASTRAL_DB_DIR`: identical failure sets (61, all pre-existing), tip +6 passing. No new failures.

#### betty — 2026-09-29T20:06:09.274Z
[bug-repro]
`origin/sub/AST-1876/AST-1882-prefilter-rc-default-vector-tests` @ `b6968441` · repro red on dev, green on ftr

#### joan — 2026-09-29T20:02:19.382Z
[board-joan]  CANON: OK

#### betty — 2026-09-29T20:01:58.544Z
[board-betty] TESTS: REVISE
What: no bible entry yet (plan targets `docs/test-bible/core/candidate.md`) — `[bug-repro]` assert is wrong — `test_prefilter_prompt_has_no_hand_written_reality_check` asserts `cp.count("{$RUBRIC_VECTORS}") == 1`, but the `prefilter_company` `cache_prompt` has two occurrences both before and after the fix (the second is in `## GRADE SET COMPLETENESS (AST-1154)`: "Every rubric vector code in {$RUBRIC_VECTORS} …"). Checked on `origin/ftr/AST-1876-prefilter-rc-default-vector` @ `6e35dfbf`: count is 2. The test would stay red after the fix. Replace the count check with the rubric-section substring `"**Your Rubric for evaluation:**\n\n{$RUBRIC_VECTORS}\n\n### POSSIBLE_JOBLIST_LINKS" in cp`. That's red on `origin/dev`, where the RC block sits between the header and the token, and green on `6e35dfbf`. Keep the two `not in` asserts.

Everything else covers my AST-1881 REVISE: the registry test is rewritten to the A/B/C/D/F/X scale, and there's save / craft generate / craft persist coverage (b–f) plus the bible rows. On `6e35dfbf` I checked the helper name, owner/artifact mapping (`company_prefilter`→`prefilter_company`, `craft_prefilter_rubric`→`company_prefilter`) and all five mirrored AST-1085 siblings. They match the plan.

— Betty

#### hedy — 2026-09-29T20:00:34.583Z
`origin/sub/AST-1876/AST-1882-prefilter-rc-default-vector-tests` @ `298e4e98` · RC test gap planned

---

_Implementation detail may live in git history on `origin/dev`._
