# AST-2127 — Do rubric code + zero-grade decode tests + bible (test gap for AST-2126)

<!-- linear-archive: AST-2127 archived 2026-10-16 -->

## Linear archive (AST-2127)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2127/do-rubric-code-zero-grade-decode-tests-bible-test-gap-for-ast-2126  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-2112 — [✅/Somerset] meteorite_grade_do COMPLETED: 1 error(s) / 1 processed | meteorite_grade_do-3f837cd7-89e5-47f6-9ae1-e8aae7ee4284  
**Blocked by / blocks / related:** parent: AST-2112

### Description

## What this implements

Test gap for [AST-2126](https://linear.app/astralcareermatch/issue/AST-2126) (fix-board `[board-betty] TESTS: REVISE`), the fix for [AST-2112](https://linear.app/astralcareermatch/issue/AST-2112). Add a `[bug-repro]` for the production case: a 1-job `grade_do` reply with no `_GRADE_SEG` match (a `V01A3`-style reply or prose) goes through `_normalize_rubric_task_response`. It must fail on the pre-fix tree (silent `grades: []`) and pass once AST-2126 lands (one `decode_failures` entry per entity, carrying the raw reply). Also cover plan steps 1–4 (dispatch Invalid on bad codes, sync rejecting codes that aren't two uppercase letters, a combined missing+unknown reason, zero-segment `_decode_payload` notes lines). Revise the two candidate tests the fix breaks, and update the bible entries to match.

## Betty's verdict (verbatim)

> \[board-betty\] TESTS: REVISE
> What: docs/test-bible/core/candidate.md + core/consult.md + core/agent.md — 2 broken tests + no repro coverage — `test_candidate.py::…::test_uptick_is_pure_and_passes_non_dict_and_blank_codes` (blank now filled) and `…::test_duplicates_case_insensitive_sorted_and_blank_codes_ignored` (invalid-code check now fires before duplicates on ` tp`/`sa`/blank rows) break; no existing node covers the zero-grade letter-pipe → `decode_failures` path (§5, the production repro), the zero-segment `_decode_payload` notes line (§4), sync rejecting non-`[A-Z]{2}` codes (§2), `rubric_dispatch_error` invalid-code message (§1), or the combined missing+unknown reason (§3).
>
> Notes for qa-fix (not part of the verdict):
>
> * Guard tests that stay green, by plan: `test_agent.py::…::test_ast1996_notes_type_tail_is_not_a_decode_failure` (line has a segment), `test_consult.py` `missing vectors` / `unknown vectors` single-side matches (byte-identical), `test_api_candidate.py` V01 rubric-route tests (explicit stored codes, never via a blank-code fallback through sync — keep an eye on these if sync's raise is reached in any fixture path).
> * \[bug-repro\] candidate: the plan's Repro (`_normalize_rubric_task_response("grade_do", …)` with `V01A3` segments and with prose) → today returns `grades: []`; to-be returns `jobs: []` plus one `decode_failures` entry per entity carrying the raw reply.
> * Bible: `scripts/ci/ftr-merge-ready.sh` in the diff is outside the fix scope; no test impact.

## Citations

none. Test tree and bible only.

## Scope

### Component scope

* `tests/component/core/test_consult.py` (modified): `[bug-repro]` for `_normalize_rubric_task_response` zero-grade letter-pipe → `decode_failures`; combined missing+unknown reason from `_require_complete_grade_set`.
* `tests/component/core/test_agent.py` (modified): zero-segment notes line in `_decode_payload` becomes a decode failure. The AST-1996 notes-tail guard stays green.
* `tests/component/core/test_candidate.py` (modified): revise `test_uptick_is_pure_and_passes_non_dict_and_blank_codes` and `test_duplicates_case_insensitive_sorted_and_blank_codes_ignored`. Add the `rubric_dispatch_error` invalid-vector-code reason.
* `tests/component/data/database/test_rubric_vectors.py` (modified): `sync_rubric_vectors_from_criteria` rejects codes that aren't two uppercase letters, with no `V{idx}` fallback.
* `tests/component/ui/api/test_api_candidate.py` (modified, scope amended per AST-2127 fix-board): `TestAst2067CandidateVersionRoutes` `_seed_rubric` fixture codes `V01`/`V02` → valid 2-letter codes (incl. the `_RUB` route path and the `code=` history filter); assertions follow the rename, nothing skipped or loosened.
* `docs/test-bible/core/consult.md`, `docs/test-bible/core/agent.md`, `docs/test-bible/core/candidate.md`, `docs/test-bible/data/database/rubric_vectors.md`, `docs/test-bible/ui/api/api_candidate.md` (§ AST-2067) (modified): manifest lines for the new and revised tests.

### Technical scope

* Test files above: new and revised component tests only, with no product function change.
* Bible files above: modified sections, the manifest nodes for the new and revised tests.

## Boundaries

No product `src/` or `data/` change. The product fix is AST-2126. The test tree is Betty's (`qa-fix`). The engineer side is a plan marker plus `test-fix` verification.

## Git branch (authoritative)

Mini-parent `ftr/AST-2112-do-rubric-undecodable-codes`, child `sub/AST-2112/<this-ticket>-do-rubric-code-tests`. Created at bug-fix.

### Comments

#### radia — 2026-10-10T04:41:24.326Z
[code-rubric] PROCEED (Commit: ad3f0054a) Test gap locks AST-2126

Clean. There is no canon roster to score because the work is tests and bible only. `[bug-repro]` is OK: for both a `V01`-style reply and prose it asserts `jobs == []` plus exactly one `decode_failures` entry carrying the raw reply, and it fails on the pre-fix silent `grades: []` row. The `sync(dev)` restore dropped no dev tests. `## What must still hold` is OK. Full artifact: AST-1155 doc § Radia review — AST-2127 (F7).

#### hedy — 2026-10-10T04:40:13.318Z
`origin/sub/AST-2112/AST-2127-do-rubric-code-tests` @ `ad3f0054a` · test-fix green, nothing pushed

- **[bug-repro]** `test_consult.py::TestAst2126ZeroGradeRepliesAreDecodeFailures::test_bug_repro_one_job_zero_grades_is_decode_failure`: **2 failed** with `src/core/{consult,agent,candidate}.py` + `src/data/database.py` from `54e186b79` (silent `grades: []` row), then restored. **2 passed** on the tip.
- **Manifest item 2:** 42 passed.
- **Six-file no-regression run:** 94 failed / 1423 passed / 7 skipped. 93 failing ids are identical to the earlier environment baseline. The 94th, `test_api_candidate.py::TestCandidateRoutes::test_list_candidates_and_states` (`'PROSPECT'` in the states list), also fails with the `54e186b79` product files. No AST-2124/2125/2126/2127 node fails, and no renamed fixture node fails.
- **Scope gate:** the `ftr...sub` diff on `src/` and `data/` is entirely dev commits brought in by `sync(dev)` 4c2645474 (`0d01e20d2` AST-2124, AST-2114, AST-2115, AST-2105, AST-2106). The merge's `src/` and `data/` content equals git's clean auto-merge of its parents, and `ad3f0054a` touches no `src/` or `data/`. There is no AST-2127 product change.

#### betty — 2026-10-10T04:38:39.137Z
@Hedy Lamarr — re your [qa-handoff] (sync-child conflict): resolved and pushed. `origin/sub/AST-2112/AST-2127-do-rubric-code-tests` @ `ad3f0054a` (sync(dev) merge `4c2645474` + `test(AST-2127)` restore commit).

- Both sides kept: dev's AST-2124 `test_ast2124_letter_conf0_decodes_as_x0` (AST-2053 test dropped per dev) + `TestAst2125MissingRubricDescription` + bible § AST-2125, alongside the AST-2126/AST-2127 tests and bible § AST-2127 (chronological). `git diff origin/dev` on the three files shows only AST-2127 additions plus the planned fixture renames; no dev content dropped.
- `test_agent.py` + `test_consult.py`: 69 failed / 711 passed — the same 69 environment failures as before the merge; AST-2124/2125/2126 classes green (24 passed).
Ready for test-fix re-run.

#### hedy — 2026-10-10T04:35:14.488Z
[qa-handoff]
@Betty White — test-fix for AST-2127 is blocked at `sync-child.sh` (exit 3). The step that merges `origin/dev` into `sub/AST-2112/AST-2127-do-rubric-code-tests` @ `c3d8b0956` conflicts on test-tree files where both sides added tests at the same spot. Taking one side whole would drop the other side's tests, and engineers can't write combined test content, so I aborted the merge. Nothing was committed, and no tests ran.

**Where dev comes from:** `origin/dev` now carries the AST-2116 landing (`098b2d2aa`, #293), which includes AST-2124 and the AST-2125 tests.

**Conflicts:**
1. `tests/component/core/test_agent.py`, one hunk around line 281. HEAD adds `test_ast2126_notes_line_without_segments_is_decode_failure` and keeps `test_ast2053_letter_conf0_normalised_to_conf1`. Dev replaces that AST-2053 test with `test_ast2124_letter_conf0_decodes_as_x0` (letter-confidence 0 now decodes as X0, replacing AST-2053's conversion to confidence 1). Resolution needs Betty's AST-2126 test **plus** dev's AST-2124 test, with the AST-2053 test dropped per dev.
2. `tests/component/core/test_consult.py`, one hunk at the end of the file. HEAD appends the AST-2126 `[bug-repro]` block (`test_bug_repro_one_job_zero_grades_is_decode_failure` etc.); dev appends `class TestAst2125MissingRubricDescription`. Both need to stay.
3. `docs/test-bible/core/consult.md`, one hunk: AST-2127 and AST-2125 manifest sections collide. Keep both.
4. `docs/features/consult/ast-1155-incomplete-grades-retry-holding-never-technical-fail.md`, three hunks: the AST-2126/AST-2127 blocks collide with dev's appended blocks. This is not test-tree, but it sits in the same merge commit.

`src/core/agent.py` auto-merged cleanly; dev's AST-2124 letter-0 → X0 change sits next to AST-2126's zero-segment branch with no overlap.

**Ask:** land the `sync(dev)` merge on this sub, combining both sides in the four files, and push it. Then reassign to me. I'll re-run test-fix: repro red at `54e186b79` → green on the tip, your manifest, and the six-file baseline.

#### betty — 2026-10-10T04:32:46.030Z
[bug-repro]
`origin/sub/AST-2112/AST-2127-do-rubric-code-tests` @ `7e32d7bfa` · repro red pre-fix, green on tip

#### joan — 2026-10-10T04:25:48.499Z
[board-joan] CANON: OK

No statute or pattern needs to change. The work is tests and bible only, and it pins the AST-2126 contract that the board already cleared. Bible rows are coverage manifests, not corpus directives. Full findings: AST-1155 doc § Fix board — Joan (F2) — AST-2127.

#### betty — 2026-10-10T04:25:26.353Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/{consult,agent,candidate}.md + data/database/rubric_vectors.md + ui/api/api_candidate.md — repro + steps 1–4 uncovered, 29 stale nodes, plus 2 more broken nodes outside Scope — qa-fix lands the plan's §1–§6 as written, AND `tests/component/ui/api/test_api_candidate.py::TestAst2067CandidateVersionRoutes::{test_rubric_list_and_set_current_200, test_rubric_cross_code_uuid_400_current_unchanged}` break too: `_seed_rubric` (line ~3116) seeds `V01`/`V02` straight through `db.sync_rubric_vectors_from_criteria`, which now raises. The 5-file count missed them because this file wasn't in the run.

Notes for routing (not part of the verdict):
- Scope: `test_api_candidate.py` + `docs/test-bible/ui/api/api_candidate.md` § AST-2067 are not in AST-2127 `## Scope`. Same fixture-rename rule as plan §5 (`V01`→`VA`, `V02`→`VB`, including the `_RUB` route path `/rubric/do_rubric/V01` and the `code="V01"` history filter). Needs a scope amendment before qa-fix touches it.
- Other `sync_rubric_vectors_from_criteria` seeds in the test tree: `test_consult.py` lines 245/259/287 use `CR`/`MP`/`RC` (valid, unaffected). No other test-tree callers outside the plan's files.
- Baseline: plan §7 diffs a 5-file run. Ask test-fix to also run `tests/component/ui/api/test_api_candidate.py` (or the full `tests/component` narrowed run) so any other indirect sync path shows up.
- Plan's bar for §1–§6 matches every gap in my AST-2126 verdict; [bug-repro] node = plan §1 (`_normalize_rubric_task_response` zero-grade letter-pipe).

#### hedy — 2026-10-10T04:24:37.344Z
`origin/sub/AST-2112/AST-2127-do-rubric-code-tests` @ `7caaae194` · test bar, no product src

---

_Implementation detail may live in git history on `origin/dev`._
