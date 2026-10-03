# AST-1792 — Gap: no-prompt ValueError empty_render false test coverage (AST-1791 board)

<!-- linear-archive: AST-1792 archived 2026-10-02 -->

## Linear archive (AST-1792)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1792/gap-no-prompt-valueerror-empty-render-false-test-coverage-ast-1791  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1790 — Default validation to TRUE where no prompts or keys are involved  
**Blocked by / blocks / related:** parent: AST-1790

### Description

## What this implements

Test/bible gap opened by fix-board on AST-1791: no coverage that `_evaluate_dispatch_empty_render` / list-AUTO-Run path returns `empty_render: false` when prompt load raises ValueError (no agent_task / no prompts). AST-1780 tests only monkeypatch the eval helper. Land a \[bug-repro\] that fails against pre-fix product and passes after AST-1791, plus bible note.

## Proposed change

- [X] Betty `[bug-repro]` landed via qa-fix (`TestAst1791NoPromptValueErrorEmptyRender`) — engineer does not edit `tests/` / `docs/test-bible/**`
- [X] Product soft-miss → `empty_render: false` present on tip via sync from `ftr/AST-1790-…` (AST-1791 `code(AST-1791)`); no additional product delta on this gap child
- [X] Scope gate: no `api_admin.py` / `config.py` / React edits on AST-1792

## Scope

### Component scope

* `tests/component/ui/api/test_api_admin.py` (or the existing AST-1780 admin dispatch test module under astral-tests) — **modified** — add coverage for no-prompt / missing-agent_task ValueError soft-miss → `empty_render: false` on list enrich and AUTO/Run gates.
* `docs/test-bible/ui/api/api_admin.md` — **modified** — record AST-1791 / AST-1790 no-prompt ValueError soft-miss coverage under the AST-1780 entry.

### Technical scope

* Admin dispatch empty-render tests — **new or revised test case(s)** asserting ValueError from `_dispatch_empty_render_prompt_texts` / `_resolve_task_prompts` yields `empty_render: false` (and AUTO/Run allowed) without monkeypatching away the soft-miss branch; red on pre-fix tip, green after AST-1791.
* `docs/test-bible/ui/api/api_admin.md` — **modified bible entry** naming the new node id / pattern for Betty/qa-fix successors.

## Notes for planning

Sibling of AST-1791 (product soft-miss → pass). Board: `[board-betty] TESTS: REVISE` — docs/test-bible/ui/api/api_admin.md (AST-1780) — missing coverage — no-prompt ValueError soft-miss → empty_render false. qa-fix landed `[bug-repro]`; make-fix confirms product already on ftr/sync — no engineer product patch.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1790-default-validation-no-prompts`, child `sub/AST-1790/<this-id>-<slug>`.

### Comments

#### radia — 2026-09-25T01:37:21.144Z
[code-rubric] PROCEED (Commit: f63c09f0) bug-repro gap covered

#### betty — 2026-09-25T01:17:46.227Z
[bug-repro]
`origin/sub/AST-1790/AST-1792-no-prompt-valueerror-empty-render-tests` @ `965a1c0032dcf05ef067c7146db573173902ff6d` · repro lands red, awaits fix

#### joan — 2026-09-25T01:14:44.611Z
[board-joan]  CANON: OK

context_tokens≈12000

#### betty — 2026-09-25T01:14:01.318Z
[board-betty] TESTS: REVISE
What: docs/test-bible/ui/api/api_admin.md (AST-1780) — missing coverage — no-prompt ValueError soft-miss → empty_render false; AST-1780 still monkeypatches eval only

#### hedy — 2026-09-25T01:12:49.942Z
`origin/sub/AST-1790/AST-1792-no-prompt-valueerror-empty-render-tests` @ `34303a423b7d0cf941cda7ab8a85ce122b7c07a0` · test/bible gap planned

---

_Implementation detail may live in git history on `origin/dev`._
