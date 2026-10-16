# AST-2146 — Coat-check JD self-heal guard tests + bible (test gap for AST-2145)

<!-- linear-archive: AST-2146 archived 2026-10-16 -->

## Linear archive (AST-2146)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2146/coat-check-jd-self-heal-guard-tests-bible-test-gap-for-ast-2145  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-2143 — [✅/Somerset] meteorite_grade_do COMPLETED: 1 error(s) / 36 processed | meteorite_grade_do-b93cbaa7-f72a-4e73-9a2a-4587898ad5f4  
**Blocked by / blocks / related:** parent: AST-2143

### Description

## What this implements

Test-tree and bible coverage for [AST-2145](https://linear.app/astralcareermatch/issue/AST-2145)'s coat-check self-heal guard: skip link-less jobs, and add a `transition=False` mode on `fetch_jd_batch` / `_apply_jd_gates`. Routed here from Betty's fix-board `[board-betty] TESTS: REVISE` on AST-2145, the same shape as AST-2057 for AST-2053. No product source change.

## Scope

## Component scope

* `tests/component/core/test_tracker.py` (modified).
  * Rewrite `TestGetJobData::test_self_heals_short_job_description` (no `job_link`, so the guard now skips the scrape) and `TestAst2133ComposeJobDescription::test_self_heal_writes_reference_then_returns_composed` (the fake `_fetch` must accept `transition=`, and the job needs a link).
  * Make `TestGetJobData::test_self_heal_failure_returns_none` exercise the exception branch again by giving the job a link.
  * Add repro coverage: the no-link guard returns `None`, logs one warning, and never awaits `fetch_jd_batch`; a heal from a downstream state such as `METEORITE_PASSED_JD` returns the composed JD and leaves state unchanged.
* `tests/component/core/test_gazer.py` (modified).
  * Update `TestAst2025FetchRelativeJdBatch::test_ac5_both_runners_call_shared_gate_helper`. Its exact-dict kwargs compare now sees `transition: True` on the `fetch_jd_batch` entry.
  * Add coverage for `transition=False`: no `transition_job_state` on any outcome (no link, scrape error, short, classified, pass); a classified result skips the reference save and returns False; a pass result keeps the reference.
* `docs/test-bible/core/tracker.md` (modified). The AST-2133 block records the no-link guard and the transition-safe heal.
* `docs/test-bible/core/gazer.md` (modified). The AST-2025 block records the `transition` keyword and the updated kwargs compare.

## Technical scope

* `tests/component/core/test_tracker.py`: three modified test functions and new repro test function(s), so the suite asserts the guarded, transition-safe self-heal instead of the old one.
* `tests/component/core/test_gazer.py`: one modified test function and new test function(s) for the `transition=False` branches of `fetch_jd_batch` and `_apply_jd_gates`.
* `docs/test-bible/core/tracker.md`, `docs/test-bible/core/gazer.md`: modified bible rows, so the bible matches the tests.

## Acceptance criteria

* The repro tests (no-link guard, downstream-state heal) pass on the AST-2145 tip and would have failed before it.
* The four named tests assert current behaviour and pass.
* Both bible blocks match.

## Boundaries

* No `src/` change. AST-2145 owns the product fix.
* Other pre-existing failures in `test_tracker.py` or `test_gazer.py` on ftr are out of scope.

## Notes for planning

Betty's verdict comment on AST-2145 (`[board-betty] TESTS: REVISE`) names the exact gaps. Doc to patch: `docs/features/gazer/ast-326-batch-scrape-jds-plan.md`, with a `## Bug: <this id>` block alongside AST-2145's. This ticket is blocked by AST-2145 so the tests run against the shipped fix on `ftr`.

## Git branch (authoritative)

Parent `ftr/AST-2143-jd-self-heal-no-link`; this child `sub/AST-2143/AST-2146-jd-self-heal-tests`. The registry is authoritative.

### Comments

#### radia — 2026-10-12T18:10:00.655Z
[code-rubric] PROCEED (Commit: d1aa98b68) bug-repro guard tests green

#### katherine — 2026-10-12T18:08:42.832Z
`origin/sub/AST-2143/AST-2146-jd-self-heal-tests` @ `d1aa98b68` · manifest green, [bug-repro] flip verified

- Item 1: `pytest test_tracker.py test_gazer.py` → 20 failed / 323 passed; the failure set is identical to the pre-fix baseline. AST-2146 `-k` selection → 23 passed.
- Item 2 ([bug-repro], run myself): `src/core/{gazer,tracker}.py` @ `1e11b4f57` → 4 failed ("not have been awaited. Awaited 1 times" / "not have been called. Called 1 times"); tip → 4 passed. Tree restored clean.
- Item 3: local `data/astral.db` has no `telescope_data` table before or after; nothing written to the live DB.

#### betty — 2026-10-12T18:07:03.239Z
[bug-repro]
`origin/sub/AST-2143/AST-2146-jd-self-heal-tests` @ `5c2e05444` · red pre-fix, green ftr tip

#### joan — 2026-10-12T18:03:40.828Z
[board-joan]  CANON: OK

#### betty — 2026-10-12T18:03:23.162Z
[board-betty] TESTS: OK
Covers every AST-2145 REVISE gap: revises the three broken tracker nodes (#1, #4 with the lengthened 250-char body per Katherine) and re-arms the exception branch in #2 (link + assert_awaited_once); revises the AC5 spy (#7: `transition: True` on j-abs only, absence pinned on j-rel, matches gazer.py ~490); adds the no-link guard repro (#3), still-short → None (#5), downstream heal with no state move (#6), and `transition=False` gazer coverage (#8a–d, including the classified skip-ref and default save→transition lock). Fixture assumptions checked against the AST-2145 tip: `_OK_JD`/`_vt`/`_kept`, the patch targets in gazer's namespace, `jd_min_chars` 200, `get_logger(__name__)`, and the guard placed after `job_data` coercion. Both bug-repro nodes would be red on pre-fix `08912b114`. No further test work before qa-fix lands it.

#### katherine — 2026-10-12T18:02:17.912Z
`origin/sub/AST-2143/AST-2146-jd-self-heal-tests` @ `73c1f32f1` · test delta planned for qa-fix

---

_Implementation detail may live in git history on `origin/dev`._
