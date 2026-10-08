# AST-1819 — Invalid button needs a tooltip listing the missing prompt tokens

<!-- linear-archive: AST-1819 archived 2026-10-07 -->

## Linear archive (AST-1819)

**Archived:** 2026-10-07  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1819/invalid-button-needs-a-tooltip-listing-the-missing-prompt-tokens  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** hedy  
**Priority / estimate:** None / 2  
**Parent:** AST-1817 — Invalid vs 0 Avail scheduled actions.  
**Blocked by / blocks / related:** parent: AST-1817

### Description

## Susan's comment (verbatim)

\[bug\] Add a tool tip to the Invalid button with a comma separated list of tokens that are missing for the prompt.

## As-is / To-be

* **As-is:** On Scheduled Actions, an invalid dispatch task (`empty_render`) shows a disabled **Invalid** button with no tooltip, so Susan can't see which prompt tokens failed to resolve.
* **To-be:** Hovering the Invalid button shows a tooltip with the missing prompt tokens as a comma-separated list (e.g. `FIRST_NAME, GET_RUBRIC`).

## Chuckles' diagnosis notes (for Susan to confirm)

* `api_admin.list_dtasks` already computes the token list (`_evaluate_dispatch_empty_render` → `empty_tokens`) but only puts the boolean `empty_render` on each row; the list is used for a log line and then dropped. So this needs `empty_tokens` added to each row in `src/ui/api/api_admin.py`, not just a frontend change. **That is outside AST-1817's approved scope**, which explicitly left `src/ui/api` untouched (AC 9). Confirming this bug approves widening that scope to add the one row field.
* Some invalid rows have **no** token list: `_evaluate_dispatch_empty_render` returns `empty_render: True, empty_tokens: []` when the prompts couldn't be validated. Proposed tooltip for that case: `Could not validate prompts`. Correct that wording here if you want something else.
* The disabled button has `pointer-events: none`, which blocks hover. The tooltip needs a wrapper element (or a pointer-events change) so it still shows while the button stays unclickable.

## Suggested engineer

Hedy (implemented sibling AST-1818)

## QA test manifest

Publish tip: `origin/sub/AST-1817/AST-1819-invalid-button-missing-token-tooltip` @ `57c3f343` (`merge-tests(AST-1819): origin/tests 4712b4a3`). Repro verified **red on the pre-fix tree**; green side is `test-fix`'s to confirm after `make-fix`.

1. **API** `[bug-repro]` (parent AC 12) — `tests/component/ui/api/test_api_admin.py::TestAst1780EmptyRenderListGatesForceOff::test_list_sets_empty_render_and_forces_auto_off` (asserts `empty_tokens == ["FIRST_NAME"]`) and `::test_list_empty_render_false_keeps_auto` (asserts `[]`). Pre-fix: `KeyError: 'empty_tokens'`.
2. **Frontend** `[bug-repro]` (parent AC 13) — `tests/component/frontend/pages/test_AdminScheduledActions.test.tsx` describe `AST-1819 Invalid tooltip lists missing tokens`: `wrapper title is the comma-separated token list…` and `empty token list falls back to 'Could not validate prompts'` (red pre-fix: no `title`); `no tooltip while the Invalid row is running…` is a guard (green pre-fix, must stay green).
3. **Regression** — the full `test_AdminScheduledActions*.test.tsx` suite (AST-1818 AC 1–8 must still hold); pre-fix it is 72/74, and the only reds are the two repro cases.

```bash
./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_admin.py::TestAst1780EmptyRenderListGatesForceOff -q
cd src/ui/frontend && npx vitest run --config vite.config.ts test_AdminScheduledActions
```

**Not in scope:** 5 pre-existing reds elsewhere in `test_api_admin.py` (AST-781, `TestDispatchTasks::test_list_dispatch_tasks_and_keys`, `TestApiAdminBranchGaps::test_dispatch_task_keys_db_row_adds_orphan_key`, AST-783, AST-1214). They are red without any AST-1819 edits.

**Bible shasums (publish tip):**

* `docs/test-bible/frontend/pages.md` — `b6de453b42ceadfcd4140b7dcdbcdeeff909b152`
* `docs/test-bible/ui/api/api_admin.md` — `3daa07dfa7e54331d556936d23128d90c89c8637`

### Comments

#### radia — 2026-09-27T05:17:32.849Z
[code-rubric] PROCEED (Commit: 4ef31239) Tooltip repro OK, holds OK

#### betty — 2026-09-27T05:12:57.442Z
[bug-repro]
`origin/sub/AST-1817/AST-1819-invalid-button-missing-token-tooltip` @ `57c3f343` · repro lands red, awaits fix

#### joan — 2026-09-27T05:10:29.087Z
[board-joan]  CANON: OK

#### betty — 2026-09-27T05:10:17.483Z
[board-betty] TESTS: REVISE
What: docs/test-bible/ui/api/api_admin.md (AST-1780) + docs/test-bible/frontend/pages.md (AST-1818) — missing coverage — no test asserts `list_dtasks` row `empty_tokens` (AST-1780 mocks return it, only `empty_render` asserted) and no Vitest checks the Invalid wrapper `title` (token list / `Could not validate prompts` / none while running); no existing test breaks (title on wrapper keeps button name Invalid).

#### hedy — 2026-09-27T05:09:23.948Z
`origin/sub/AST-1817/AST-1819-invalid-button-missing-token-tooltip` @ `6c12d339` · tooltip via wrapper title

---

_Implementation detail may live in git history on `origin/dev`._
