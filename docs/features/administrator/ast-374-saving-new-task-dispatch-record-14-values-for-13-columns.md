<!-- linear-archive: AST-374 archived 2026-06-03 -->

## Linear archive (AST-374)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-374/saving-new-task-dispatch-record-14-values-for-13-columns  
**Status at archive:** Done  
**Project:** Astral Administrator  
**Assignee:** betty  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

from the Admin scheduled actions page, when click Add Task, and I fill in the task dispatch to run locate_job_page, setting the input state as "NO_OPENINGS", and fill in the rest of the data, there's an error when I click save that says "14 values for 13 columns".

### Comments

#### susan — 2026-05-06T20:55:21.354Z
Review feedback resolved. Branch `chuckles/ast-374-saving-new-task-dispatch-record-14-values-for-13-columns` is ready for testing. Doc commit: `38faa33c` (combined plan + Resolution). INSERT fix already on `dev`: `4510d6e6`.

— Betty

#### susan — 2026-05-06T20:30:58.409Z
**Code review (Radia)** — used **local `dev`** commit **`4510d6e6`** because **`git rev-parse chuckles/ast-374-saving-new-task-dispatch-record-14-values-for-13-columns`** failed (no `refs/heads/…` — branch ref absent in this repo; per skill, **origin/** feature ref is not required).

**Counts:** fix-now **0** · discuss **0** · advisory **0**

**What’s solid:** `save_dispatch_task` `INSERT` column list (13) now matches **13** placeholders and the 13-value bind tuple — fixes the reported SQLite “14 values for 13 columns” failure (**§2.4 / data-layer INSERT hygiene**).

**No combined feature doc** was linked on the issue; findings stay here.

— Radia

#### susan — 2026-05-06T20:16:54.921Z
**Radia — review blocked (no branch to diff)**

Linear lists `gitBranchName` `chuckles/ast-374-saving-new-task-dispatch-record-14-values-for-13-columns`, but that ref is **not** on `origin` from the review environment (`git ls-remote` / `origin/dev…origin/<branch>` has no match), so I could not check out the branch or produce `git diff origin/dev…HEAD`.

**State:** left **Code Complete** (no review posted).

Push the feature branch (or correct the `gitBranchName`) and ping for a re-run when ready.

— Radia

---

# AST-374 — Saving new Task dispatch record: 14 values for 13 columns

**Linear:** [AST-374](https://linear.app/astralcareermatch/issue/AST-374/saving-new-task-dispatch-record-14-values-for-13-columns)  
**Branch:** `<agent>/ast-374-saving-new-task-dispatch-record-14-values-for-13-columns`  
**Project:** Astral Administrator

## Summary

From the admin scheduled-actions UI, adding a new dispatch task (e.g. `locate_job_page` with input state `NO_OPENINGS`) failed on save with SQLite **“14 values for 13 columns”** — `save_dispatch_task` `INSERT` column count did not match the bound value tuple.

---

## Review (Radia, 2026-05-06)

- **Counts:** fix-now **0** · discuss **0** · advisory **0**
- **Finding:** `save_dispatch_task` `INSERT` lists **13** columns and **13** placeholders with a **13**-value bind tuple — matches `dispatch_task` schema (**§2.4 / INSERT hygiene**).
- **Note:** Radia reviewed tree at **`4510d6e6`** on `dev` (feature ref was absent in her review environment).

---

## Resolution

**Date:** 2026-05-06 — Betty (`f-resolve-linear`)

- **Code:** Already on **`dev`** as **`4510d6e6`** — `fix(ast-374): align save_dispatch_task INSERT with 13 dispatch_task columns.`
- **This commit:** Adds this combined doc + Resolution only (no further code edits in resolve pass).
- **Testing:** Re-save a new dispatch task from admin (same path as report) and confirm SQLite error is gone.

— Betty
