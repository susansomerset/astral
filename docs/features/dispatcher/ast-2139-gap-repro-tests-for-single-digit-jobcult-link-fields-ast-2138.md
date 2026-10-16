# AST-2139 — gap: repro tests for single-digit JOB:/CULT: link fields (AST-2138)

<!-- linear-archive: AST-2139 archived 2026-10-16 -->

## Linear archive (AST-2139)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2139/gap-repro-tests-for-single-digit-jobcult-link-fields-ast-2138  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 1  
**Parent:** AST-2136 — Prefilter errors  
**Blocked by / blocks / related:** parent: AST-2136

### Description

## What this implements

Test gap for [AST-2138](https://linear.app/astralcareermatch/issue/AST-2138), from fix-board `[board-betty] TESTS: REVISE`. Add the repro coverage that would have caught AST-2136. No existing test exercises a single-digit `JOB:0`–`JOB:5` link field (the current `JOB:` tests only use `JOB:16`), so nothing fails before the fix and passes after it.

## Scope

Test tree and bible only, as named in Betty's board verdict:

* Bible: `docs/test-bible/core/agent.md`, `docs/test-bible/core/consult.md`.
* Repro (`[bug-repro]`): `000|RCA5|HEA5|MLA3|PFA5|SOA5|JOB:3|CULT:7,27` decodes to the five rubric grades with `possible_job_links == [3]` and `culture_links_to_explore == [7, 27]`, and no `JO` grade. It fails on the pre-fix tree and passes once AST-2138 lands.
* `JOB:1|CULT:[]` decodes to `possible_job_links == [1]`.
* `_should_decode_as_encoded_line("000|JOB:3|CULT:7")` is `False`.

## Boundaries

No product `src/` changes (AST-2138 owns them). Existing AST-483 whitespace, routing, `JOB:16` and `test_consult.py` \~L2374 tests stay as they are. Betty's board found none of them broken by the plan.

## Notes for planning

AST-2138's plan section: `docs/features/consult/ast-697-prefilter-link-set-schema-and-bracket-decode.md` (AST-2138 section). Add a section for this ticket there. Betty lands the tests (qa-fix); engineers never edit `tests/`.

## Git branch (authoritative)

Parent `ftr/AST-2136-job-link-prefix-decode`, child `sub/AST-2136/AST-2139-job-link-prefix-tests`. Created at bug-fix.

### Comments

#### radia — 2026-10-12T15:01:17.978Z
[code-rubric] PROCEED (Commit: ad3659514) bug-repro pins JOB guard

#### betty — 2026-10-12T14:55:50.417Z
[bug-repro]
`origin/sub/AST-2136/AST-2139-job-link-prefix-tests` @ `b53e52949` · repro red pre-fix, green post-fix

Repro node: `tests/component/core/test_agent.py::TestAst2138JobLinkPrefixNotGrade::test_single_digit_job_link_is_meta_not_grade[3]` (class: 8 tests, (a) n=0–5, (b) `JOB:1|CULT:[]`, (c) routing). Red on `a1af5cf6a` 8/8 (extra `JO` grade / routes as encoded); green 8/8 on synced tip (AST-2138 already on ftr @ 660919af4). test_agent.py failure set identical pre/post (46 pre-existing, stale `astral_job_id` fixtures — out of scope). Bible: core/consult.md + core/agent.md `### AST-2138 · AST-2136`.

Note: astral-AST-2136 had no betty hook seeded (falls back to shared engineer hook); used a worktree-scoped betty hook for this commit only, then removed it.

#### joan — 2026-10-12T14:52:20.168Z
[board-joan]  CANON: OK

#### betty — 2026-10-12T14:52:02.553Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/agent.md + core/consult.md (no AST-2138 entry) — missing coverage — this ticket *is* the test work: new `TestAst2138JobLinkPrefixNotGrade` in tests/component/core/test_agent.py ((a) JOB:0–5 parametrized, (b) JOB:1|CULT:[], (c) `_should_decode_as_encoded_line("000|JOB:3|CULT:7") is False`) + bible rows, landed by qa-fix as written in the plan.

Notes for qa-fix: use the company-shaped ctx (`company_id`, `["companies"]`). Don't reuse `_batch_entities` / `_prefilter_decode_ctx`, which build `astral_job_id` rows. AST-2138 is already on ftr @ 660919af4, so after sync-child the sub tip is post-fix; show red against `a1af5cf6a` (pre-fix) separately. No existing test needs editing.

#### hedy — 2026-10-12T14:50:38.222Z
`origin/sub/AST-2136/AST-2139-job-link-prefix-tests` @ `4594903b7` · JOB:0-5 repro rows for Betty

---

_Implementation detail may live in git history on `origin/dev`._
