# AST-1522 — gap: meteorite_email land+archive test coverage (AST-1520)

<!-- linear-archive: AST-1522 archived 2026-09-09 -->

## Linear archive (AST-1522)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1522/gap-meteorite-email-landarchive-test-coverage-ast-1520  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1520 — Emailed job description parsed as HTML  
**Blocked by / blocks / related:** parent: AST-1520

### Description

## What this implements

Sibling gap child for orphaned bug AST-1520 / fix AST-1521. Betty fix-board REVISE: land `docs/test-bible/core/meteorite_email.md` coverage for no-subject JD→land+archive; retire/update Ruth html_links/subject_body/_ingest_link/ignored-empty tests that break once make-fix lands.

## Scope

### Component scope

* `docs/test-bible/core/meteorite_email.md` — bible entry for new land+archive repro paths.
* `tests/component/core/` — meteorite_email component tests Betty lands at qa-fix (exact file at qa-fix).

### Technical scope

* Test bible — **modified** meteorite_email manifest nodes for land_meteorite routing contract.
* Component tests — **new/modified** cases: no-subject JD text → land_meteorite + archive; update/remove legacy Ruth-path tests superseded by fix.

## Acceptance / Radia fix-now

- [X] [bug-repro] `TestAst1522NoSubjectJdLandsAndArchives` green on product tip
- [X] `TestAst1140RunMeteoriteEmailSelectedIds` retargeted `create_meteorite_job` → `land_meteorite`
- [X] `TestAst1213RuthLivePayload` removed; bible AST-1213 / AST-1294 / AST-1522 rows updated
- [X] Betty return manifest green: `TestAst1522NoSubjectJdLandsAndArchives` + `TestAst1140RunMeteoriteEmailSelectedIds` (4 passed @ `2bd215df` / resolve tip)

## Git branch (authoritative)

parent `ftr/AST-1520-emailed-job-description-parsed-as-html`, child `sub/AST-1520/AST-1522-gap-meteorite-email-tests`.

## QA test manifest

`origin/sub/AST-1520/AST-1522-gap-meteorite-email-tests` @ `75dad84f36559e07851b348ddee9f1194f096e2d` · Betty return `2bd215df` + resolve Resolution doc

1. **[bug-repro]: **`TestAst1522NoSubjectJdLandsAndArchives` — green on product tip (leave).
2. **Return (Review Posted / Radia fix-now): **`TestAst1140RunMeteoriteEmailSelectedIds` retargeted; `TestAst1213RuthLivePayload` removed; bible updated.
3. **Bible: **`docs/test-bible/core/meteorite_email.md` shasum `31a0f0ca6cf4950fe60f4b9348b502c7604eb1b1`

**Run:**

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_meteorite_email.py::TestAst1522NoSubjectJdLandsAndArchives \
  tests/component/core/test_meteorite_email.py::TestAst1140RunMeteoriteEmailSelectedIds \
  -q
```

— Betty

### Comments

#### katherine — 2026-08-27T03:30:01.299Z
`origin/sub/AST-1520/AST-1522-gap-meteorite-email-tests` @ `75dad84f36559e07851b348ddee9f1194f096e2d` · §9a clean · ftr dry-run clean

#### betty — 2026-08-27T03:28:21.944Z
`origin/sub/AST-1520/AST-1522-gap-meteorite-email-tests` @ `2bd215df` · Radia fix-now landed

#### katherine — 2026-08-27T03:25:34.204Z
[qa-handoff]
@Betty White

Radia fix-now on AST-1522 are all test-tree — engineer cannot touch `tests/` / `docs/test-bible/**`. Please land on `origin/sub/AST-1520/AST-1522-gap-meteorite-email-tests` (tip `494ab773` has AST-1521 product merge):

1. `TestAst1140RunMeteoriteEmailSelectedIds` — still monkeypatches/asserts `create_meteorite_job`; retarget to `land_meteorite` (same land+archive contract as AST-1521 / TestAst1522).
2. `TestAst1213RuthLivePayload` — dead (helpers `_ruth_live_parts` / `_format_ruth_live_body` deleted with Ruth-first path); remove the class and fix the matching `docs/test-bible/core/meteorite_email.md` row.

[bug-repro] `TestAst1522NoSubjectJdLandsAndArchives::test_no_subject_jd_text_lands_and_archives` already green against product tip — leave it.

When published, reassign Katherine and stay Review Posted so resolve-child can re-sync and advance.

#### radia — 2026-08-27T03:24:58.493Z
[code-rubric] REVIEW (Commit: 494ab773) stale TestAst1140 runner

Overall FIX-NOW. [bug-repro] OK. fix-now: (1) TestAst1140 still asserts create_meteorite_job — retarget to land_meteorite; (2) TestAst1213RuthLivePayload dead (helpers deleted) — remove + fix bible row. discuss: narrowed manifest only. Advisory: board asked broader coverage, only primary repro landed.

Next: Review Posted → resolve-child (test-tree → Betty [qa-handoff]).

#### katherine — 2026-08-27T03:20:45.922Z
`origin/sub/AST-1520/AST-1522-gap-meteorite-email-tests` @ `494ab7739de8d8deb2abadc48a4e10e622e1d7b2`

Merged AST-1521 @ `224b882b`. [bug-repro] `TestAst1522NoSubjectJdLandsAndArchives::test_no_subject_jd_text_lands_and_archives` green; manifest Run command green.

#### betty — 2026-08-27T03:12:06.225Z
[bug-repro]
`origin/sub/AST-1520/AST-1522-gap-meteorite-email-tests` @ `1ee08f4808f5079a928e1e37358494ceceee6218` · repro lands red, awaits fix

#### betty — 2026-08-27T03:10:07.260Z
[bug-repro]
`origin/sub/AST-1520/AST-1522-gap-meteorite-email-tests` @ `3c878db8fc94afd5b09f199b2b148031b7cf9e7a` · repro lands red, awaits fix

#### chuckles — 2026-08-27T03:03:09.014Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/meteorite_email.md — missing coverage + broken tests — no-subject JD→land+archive uncovered; Ruth html_links/subject_body/_ingest_link/ignored-empty expectations break

---

_Implementation detail may live in git history on `origin/dev`._
