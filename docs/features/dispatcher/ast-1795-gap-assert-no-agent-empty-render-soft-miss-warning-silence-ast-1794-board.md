# AST-1795 — Gap: assert no-agent empty_render soft-miss warning silence (AST-1794 board)

<!-- linear-archive: AST-1795 archived 2026-10-02 -->

## Linear archive (AST-1795)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1795/gap-assert-no-agent-empty-render-soft-miss-warning-silence-ast-1794  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1793 — Agent of n/a for dispatch task should not generate an error  
**Blocked by / blocks / related:** parent: AST-1793

### Description

## What this implements

Test/bible gap opened by fix-board on AST-1794: soft-miss return is covered (AST-1791/1792), but silence of the `no prompts to validate` / no-agent_id `logger.warning` is not asserted. Land coverage (and bible note) that the ValueError soft-miss path does not emit that warning, red before AST-1794 product and green after.

## Scope

### Component scope

* `tests/component/ui/api/test_api_admin.py` — **modified** — assert ValueError soft-miss path does not call `logger.warning` with the no-prompts / no-agent_id message (return still `empty_render: false`).
* `docs/test-bible/ui/api/api_admin.md` — **modified** — record AST-1794 warning-silence coverage under the AST-1780 / AST-1791 empty-render entry.

### Technical scope

* Admin dispatch empty-render tests — **new or revised test case(s)** asserting the soft-miss branch returns `empty_render: false` **and** does not emit the soft-miss warning; red on pre-AST-1794 tip, green after product silence lands.
* `docs/test-bible/ui/api/api_admin.md` — **modified bible entry** naming the new node id / pattern.

## Notes for planning

Sibling of AST-1794 (product silence warning). Board: `[board-betty] TESTS: REVISE` — docs/test-bible/ui/api/api_admin.md (TestAst1791NoPromptValueErrorEmptyRender) — missing coverage — ValueError soft-miss return covered; silence of `no prompts to validate` warning not asserted.

### Comments

#### radia — 2026-09-25T14:51:43.679Z
[code-rubric] PROCEED (Commit: 5c58dbe6) soft-miss silence repro OK

#### betty — 2026-09-25T14:48:07.019Z
[bug-repro]
`origin/sub/AST-1793/AST-1795-no-agent-empty-render-warning-tests` @ `ae302cb14e8c082d906d40f1c8a80f4d98ea5cf3` · repro lands red, awaits fix

#### joan — 2026-09-25T14:45:44.117Z
[board-joan]  CANON: OK

Test/bible-only gap — no product or canon edits. Silence assertion validates existing `stat.logging.warning` (pass path, Resolution #4); bible row is manifest only.

context_tokens≈16000

#### betty — 2026-09-25T14:45:09.157Z
[board-betty] TESTS: REVISE
What: docs/test-bible/ui/api/api_admin.md — missing coverage — soft-miss `no prompts to validate` warning silence still unasserted; planned [bug-repro] not landed

#### hedy — 2026-09-25T14:43:04.623Z
`origin/sub/AST-1793/AST-1795-no-agent-empty-render-warning-tests` @ `874ffc1da0f448c971aa68864b21a6caf854ad87` · assert warning silence

---

_Implementation detail may live in git history on `origin/dev`._
