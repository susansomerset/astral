# AST-2027 — Unblock AST-2024: approve installing ruff, or waive lint

<!-- linear-archive: AST-2027 archived 2026-10-16 -->

## Linear archive (AST-2027)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2027/unblock-ast-2024-approve-installing-ruff-or-waive-lint  
**Status at archive:** Archive  
**Project:** Astral Tracker  
**Assignee:** unassigned  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-2022

### Description

AST-2024's build is paused before its first commit. Your rule is to compile and lint before every commit, and the plan uses `ruff check` for lint. But no linter is installed in the epic worktree's environment: `ruff`, `flake8` and `pyflakes` are all missing. [AST-2023](https://linear.app/astralcareermatch/issue/AST-2023/telescope-click-then-capture-new-fetch-task-for-relative-job-link) shipped without linting.

Stage 1's edits to `src/utils/config.py` are done but not committed. They pass compile, the module import, AC 1 and the UI manifest check.

**Need one answer:**

1. Approve `pip install --user ruff` (then this applies to the whole epic), **or**
2. Waive lint for [AST-2024](https://linear.app/astralcareermatch/issue/AST-2024/relative-job-link-state-and-task-registration-new-fetch-task-for) (compile, import and AC checks only), **or**
3. Name a different linter.

Reply here; the agents will act on it. You don't need to install or push anything. Move this ticket to **Done** when you've answered. Neither [AST-2024](https://linear.app/astralcareermatch/issue/AST-2024/relative-job-link-state-and-task-registration-new-fetch-task-for) nor [AST-2022](https://linear.app/astralcareermatch/issue/AST-2022/new-fetch-task-for-relative-job-link) is assigned to you; this gate is the only thing blocking them.

### Comments

#### susan — 2026-10-08T03:39:44.038Z
1, approved.

---

_Implementation detail may live in git history on `origin/dev`._
