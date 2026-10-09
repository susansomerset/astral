# AST-1911 — Pin QC never-X rule and evaluate_jd QC prompt exception (test gap for AST-1910)

<!-- linear-archive: AST-1911 archived 2026-10-08 -->

## Linear archive (AST-1911)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1911/pin-qc-never-x-rule-and-evaluate-jd-qc-prompt-exception-test-gap-for  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 1  
**Parent:** AST-1898 — [✅/Abrams] evaluate_jd COMPLETED: 9 error(s) / 9 processed | evaluate_jd-3aebf350-898a-44d8-abf0-43ea2996f7db  
**Blocked by / blocks / related:** parent: AST-1898

### Description

## What this implements

Test gap from fix-board on AST-1910 (`[board-betty] TESTS: REVISE`). Nothing pins the QC "never X, grade F" rule in `EMBEDDED_EVALUATE_JD_CRITERIA` content, and nothing pins the `evaluate_jd` `cache_prompt` QC exception in `data/admin/agent_task.json`. The existing substring tests stay green after AST-1910's append-only edits, so without this the fix has no regression guard.

## Scope

### Component scope

* `tests/component/utils/test_config.py` (modified): extend `TestAst1084EvaluateJdCriteria` so QC `content` must carry the "Never grade Quality Check X" rule line, while `parse_trailing_grade_table_lines(qc["content"])` and `grade_descriptions` both still yield exactly A/B/C/F.
* `tests/component/core/test_repo_admin_json.py` (modified): pin the `evaluate_jd` row's `cache_prompt` QC exception (QC never X / grade F) alongside its existing X0 completeness text, in a catalog-row class shaped like the file's existing per-row `TestAst…CatalogRow` classes.
* `docs/test-bible/utils/config.md` (modified): bible entry for the new QC assertion under § AST-1084.
* `docs/test-bible/core/repo_admin_json.md` (modified): bible entry for the `evaluate_jd` QC-exception pin.

### Technical scope

* `tests/component/utils/test_config.py`: new or modified test function(s) in `TestAst1084EvaluateJdCriteria`. Repro-first: the QC-content assertion fails on `origin/dev` (no rule line) and passes on AST-1910's tip.
* `tests/component/core/test_repo_admin_json.py`: new test class/function asserting both QC-exception substrings are present in the `evaluate_jd` `cache_prompt`. It fails on `origin/dev` and passes on the tip.
* `docs/test-bible/utils/config.md`, `docs/test-bible/core/repo_admin_json.md`: new bible rows pointing at those tests.

## Acceptance criteria

1. Each new assertion fails on `origin/dev` and passes once AST-1910's product change is on the tip.
2. QC grades are still pinned to A/B/C/F (existing `test_qc_grades_abcdef_subset_and_descriptions` unchanged or strengthened, never loosened).
3. No product code changes on this ticket.

## Boundaries

Tests and bible only. The product/prompt change and the `docs/uat-fixtures/AST-756/expected-agent_task.json` lockstep mirror belong to sibling AST-1910, which lands on the mini-parent ftr first and reaches this sub via sync-child. The AST-756/AST-1773 byte-twin tests are already red on `origin/dev` (four rows drifted before this bug), so making them green is out of scope here; just do not make them worse.

## Notes for planning

Gap child filed by bug-fix from Betty's `[board-betty] TESTS: REVISE` on AST-1910. Read that comment. Plan section home: `docs/features/interface/ast-1084-config-constant-jd-vectors.md` (same doc as AST-1910's `## Bug:` block).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1898-evaluate-jd-qc-forbid-x`, child `sub/AST-1898/<child-segment>`. Created at bug-fix gap dispatch.

### Comments

#### radia — 2026-10-02T04:28:19.518Z
[code-rubric] PROCEED (Commit: c18e32c9) QC never-X tests pinned

#### ada — 2026-10-02T04:27:09.573Z
`origin/sub/AST-1898/AST-1911-pin-qc-never-x-tests` @ `c18e32c9` · Tests Passed (no new commits)

**[bug-repro] flip verified.** With origin/dev's `src/utils/config.py` and `data/admin/agent_task.json` swapped in, all 3 tests fail for the root-cause reasons: QC line 2 is the A row, the catalog lacks the STEP 3 exception, and the fixture row no longer matches the catalog. After restoring (tree clean), all 3 pass:
- `test_config.py::TestAst1084EvaluateJdCriteria::test_qc_content_forbids_x_and_grade_table_stays_abcf`
- `test_repo_admin_json.py::TestAst1910EvaluateJdQcNeverXPrompt` (2 tests)

**Manifest** (bible `docs/test-bible/core/repo_admin_json.md` § AST-1911): 8 passed.

**`test_config.py` + `test_repo_admin_json.py` in full, same worktree and runner (`/home/susan/astral-AST-1851/.venv/bin/python`):**
- this sub: 39 failed / 605 passed / 18 skipped
- `origin/ftr/AST-1898-evaluate-jd-qc-forbid-x`: 39 failed / 602 passed / 18 skipped
- The failure sets are identical, with 0 new. The 3 extra passes are the AST-1911 tests. The 39 are pre-existing on ftr.

Carry tests from origin/tests (AST-1895 / 1916 / 1917 / 1920 / 1908 / 1909): not run separately. Anything of theirs inside these two files is already covered by the comparison above.

#### ada — 2026-10-02T04:26:13.874Z
`origin/sub/AST-1898/AST-1911-pin-qc-never-x-tests` @ `c18e32c9` · Code Complete (no product src). Test gap only: the AST-1910 fix is on the tip via ftr. Betty's 3 new tests plus the existing QC/completeness tests: 8 passed on the synced tip.

#### betty — 2026-10-02T04:25:15.722Z
[bug-repro]
`origin/sub/AST-1898/AST-1911-pin-qc-never-x-tests` @ `0b2d5bb27` · repro red pre-fix, green on tip

Stacked (AST-1910 already on ftr): red was proven by swapping in origin/dev's `src/utils/config.py` + `data/admin/agent_task.json` → all 3 new tests fail for the root-cause reason (QC line 2 is the A row; catalog lacks both QC exception strings; fixture≠catalog row). Synced tip + merged sub: 8 passed. test-fix confirms green; manifest + node ids in `docs/test-bible/core/repo_admin_json.md` § AST-1911.

#### chuckles — 2026-10-02T04:20:00.957Z
[check-linear] Plan Discuss — the tests-gate blocker is gone: after the AST-1919 scrub, `validate-tests-branch.sh` passes on `origin/tests` (`7c9610031`). Betty's repro `f0000cf10` is safe on local `betty-bak/tests-pre-AST-1916-20261001`, but it isn't on `origin/tests` yet.

What's stuck now is the watcher. Parent AST-1898 still carries **Active/chuckles**, but no session is running, so `[bug-fix]` treats it as busy and won't resume it. This child has no `Bug` label, so assigning it to Chuckles won't wake anything either. Check-linear isn't allowed to touch Active.

@susan to kick it: clear **Active/chuckles** on AST-1898. The next poll resumes the wave loop, and Betty publishes `f0000cf10` through qa-fix.

#### susan — 2026-10-02T04:17:07.197Z
@chuckles What is blocking this?  Please unblock it and kick the datt job?

#### joan — 2026-10-01T00:26:49.421Z
[board-joan]  CANON: OK

#### betty — 2026-10-01T00:26:35.722Z
[board-betty] TESTS: REVISE
What: no bible entry (docs/test-bible/utils/config.md § AST-1084 + docs/test-bible/core/repo_admin_json.md, new § AST-1911) — missing coverage — this ticket is the test gap itself: add `TestAst1084EvaluateJdCriteria::test_qc_content_forbids_x_and_grade_table_stays_abcf` + `TestAst1910EvaluateJdQcNeverXPrompt` (2 methods) as planned; qa-fix lands them, no product change.

Pre-checked on tip 67f5838c: both prompt strings occur exactly once in catalog `evaluate_jd`, fixture row carries both and is object-equal to catalog, QC rule line sits between header and A row, `parse_trailing_grade_table_lines` returns `{"grade": ...}` dicts, `json`/`Path` already imported in test_repo_admin_json. Plan is buildable as written.

#### ada — 2026-10-01T00:25:56.281Z
`origin/sub/AST-1898/AST-1911-pin-qc-never-x-tests` @ `67f5838c` · pin QC never-X tests

---

_Implementation detail may live in git history on `origin/dev`._
