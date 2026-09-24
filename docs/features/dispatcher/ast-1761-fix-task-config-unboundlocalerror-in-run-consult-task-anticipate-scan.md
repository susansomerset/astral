# AST-1761 — fix: TASK_CONFIG UnboundLocalError in run_consult_task (anticipate_scan)

<!-- linear-archive: AST-1761 archived 2026-09-24 -->

## Linear archive (AST-1761)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1761/fix-task-config-unboundlocalerror-in-run-consult-task-anticipate-scan  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** katherine  
**Priority / estimate:** None / 1  
**Parent:** AST-1758 — dispatcher error for anticipate_scan  
**Blocked by / blocks / related:** parent: AST-1758

### Description

## What this implements

Remove the late `from src.utils.config import TASK_CONFIG` inside `run_consult_task`'s `resolve_website` company branch so module-level `TASK_CONFIG` stays bound for the job dispatch-chain `elif` (`anticipate_scan` / `contemplate_job`). Does not change resolve_website terminal_ok values or dispatch-chain routing logic beyond restoring the name binding.

## Scope

### Component scope

* `src/core/consult.py` — modified: drop the shadowing late import of `TASK_CONFIG` inside `run_consult_task`'s `resolve_website` branch so the dispatch-chain `elif` at \~2706 sees the module-level name.

### Technical scope

* `src/core/consult.py` / `run_consult_task` — modified function: delete the nested `from src.utils.config import TASK_CONFIG` (AST-1674 left it in the company `resolve_website` arm). That import marks `TASK_CONFIG` local for the whole function, so any path that hits `task_key in TASK_CONFIG` without executing that arm (job dispatch-chain triggers like `anticipate_scan`) raises UnboundLocalError. Module-level import already present — no new import, no new function.

## Proposed change

- [X] Delete nested `from src.utils.config import TASK_CONFIG` in `run_consult_task` `resolve_website` company arm
- [X] Leave `terminal_ok` lookup on module-level `TASK_CONFIG` unchanged
- [X] No edits to dispatch-chain `elif`, `roster.py`, or `config.py`

## Notes for planning

No ancestor checkbox checked on AST-1758 — plan from this Scope + parent As-is/To-be. Patch target (existing feature doc that introduced the late import; do not create a new plan doc): `docs/features/roster/ast-1674-resolve-website-company-dispatch-apply.md`. Append `## Bug: <this-id>` sections. Parent mini-epic: AST-1758.

### Comments

#### radia — 2026-09-21T21:06:48.713Z
[code-rubric] PROCEED (Commit: dea87209089c26a0ed85cf0b725e0411717b63bd) one-line import fix

CLEAN — [bug-repro] N/A (TESTS: OK board opt-out). What must still hold OK. Canon A across frozen list. No fix-now.

#### betty — 2026-09-21T21:02:45.621Z
[board-betty] TESTS: OK

#### joan — 2026-09-21T21:01:19.936Z
[board-joan]  CANON: OK
context_tokens≈12000

#### katherine — 2026-09-21T21:00:28.382Z
`origin/sub/AST-1758/AST-1761-fix-task-config-unboundlocal` @ `3c19358e2420df64a6177411a5be664b42eae35c` · plan-fix published

---

_Implementation detail may live in git history on `origin/dev`._
