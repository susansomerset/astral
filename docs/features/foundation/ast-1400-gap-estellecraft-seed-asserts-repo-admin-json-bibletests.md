# AST-1400 — Gap: Estelle/craft seed asserts (repo_admin_json bible/tests)

<!-- linear-archive: AST-1400 archived 2026-08-31 -->

## Linear archive (AST-1400)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1400/gap-estellecraft-seed-asserts-repo-admin-json-bibletests  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1398 — Update agent.json and agent_task.json  
**Blocked by / blocks / related:** parent: AST-1398

### Description

## What this implements

Close the test/bible gap flagged by fix-board `[board-betty] TESTS: REVISE` on AST-1399: add coverage in `docs/test-bible/core/repo_admin_json.md` (and matching component tests) that pins Estelle repo columns (temperature 0, max_tokens 384000, §1 content) and craft_do_rubric / craft_like_rubric attachment uuids and prompt lengths from the AST-1398 export.

## Acceptance criteria

- [X] Bible + tests pin Estelle `data/admin/agent.json` repo columns named in Betty's board verdict (temp 0, max_tokens 384000, §1 content).
- [X] Bible + tests pin `craft_do_rubric` / `craft_like_rubric` attachment uuids and prompt lengths.
- [X] A repro-shaped case exists that fails against pre-fix seed and passes once AST-1399's seed lands.
- [X] Publish to this child's `sub/*` only.

## Proposed change

- [X] `TestAst1400EstelleCraftSeedPins` on this sub (Betty `test(AST-1400)` / `merge-tests(AST-1400)`).
- [X] `[bug-repro]` `test_estelle_and_craft_match_ast1399_export` green (ftr AST-1399 seed already ancestor; no product glue).
- [X] `test_craft_do_like_fixture_lockstep` green.
- [X] No `data/admin/**` or `src/` on this child's own commits.
- [X] Vocabulary `code(AST-1400):` on the sub log for `validate-sub-log`.

## Boundaries

* Does not re-implement the product/seed fix on AST-1399; lands test/bible work only.
* Does not change canon (Joan board was CANON: OK).

## Notes for planning

* Source verdict: AST-1399 `[board-betty] TESTS: REVISE` — docs/test-bible/core/repo_admin_json.md.
* Sibling fix child: AST-1399. Ancestor doc: docs/features/foundation/ast-756-create-repo-json-files-for-agent-and-agent-task.md.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1398-update-agent-and-agent-task-json`, child `sub/AST-1398/AST-1400-gap-estelle-craft-seed-asserts`. Created at bug-fix.

## QA test manifest

1. **\[bug-repro\]** `tests/component/core/test_repo_admin_json.py::TestAst1400EstelleCraftSeedPins::test_estelle_and_craft_match_ast1399_export` — red on `origin/dev` Estelle `temperature` `0.3`; green on AST-1399 seed.
2. `tests/component/core/test_repo_admin_json.py::TestAst1400EstelleCraftSeedPins::test_craft_do_like_fixture_lockstep`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst1400EstelleCraftSeedPins \
  -q
```

`docs/test-bible/core/repo_admin_json.md` shasum `2c8cc628e3de8140e1e20df2ad120191f48bcee2` on `origin/sub/AST-1398/AST-1400-gap-estelle-craft-seed-asserts`.

### Comments

#### radia — 2026-08-16T07:56:56.363Z
[code-rubric] REVIEW (Commit: 8d2c1f97) gap pins repro OK

#### betty — 2026-08-16T07:49:48.479Z
[bug-repro]
`origin/sub/AST-1398/AST-1400-gap-estelle-craft-seed-asserts` @ `8d2c1f97c0ba5b9b4c0cb36f99f95aa41bbd92ea` · repro lands red, awaits fix

#### joan — 2026-08-16T07:43:14.383Z
[board-joan]  CANON: OK

#### betty — 2026-08-16T07:42:58.534Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/repo_admin_json.md — missing coverage — no TestAst1400EstelleCraftSeedPins pinning Estelle temp/max_tokens/§1 content or craft_do/like attachment uuids and prompt lengths

#### ada — 2026-08-16T07:41:32.924Z
`origin/sub/AST-1398/AST-1400-gap-estelle-craft-seed-asserts` @ `a45c79eb` · pin Estelle craft asserts

---

_Implementation detail may live in git history on `origin/dev`._
