# AST-374 — Saving new Task dispatch record: 14 values for 13 columns
**Component:** administrator  
**Children:** — (single ticket)  
**Linear archived:** AST-374 2026-06-03  

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-05-01 12:12 | AST-374 | fix | `4510d6e6` | fix(ast-374): align save_dispatch_task INSERT with 13 dispatch_task columns. |
| 2026-05-06 13:55 | AST-374 | docs | `38faa33c` | docs(ast-374): Resolution after Radia review (fix on dev 4510d6e6) |

_The fix landed directly on `dev` as `4510d6e6`; the named feature branch `chuckles/ast-374-…` was never pushed to `origin` (see comments)._

## Epic — AST-374
_Archived: 2026-06-03 · Linear URL: https://linear.app/astralcareermatch/issue/AST-374/saving-new-task-dispatch-record-14-values-for-13-columns · Status at archive: Done · Project: Astral Administrator · Assignee: betty · Priority / estimate: None / —_

### Original brief

from the Admin scheduled actions page, when click Add Task, and I fill in the task dispatch to run locate_job_page, setting the input state as "NO_OPENINGS", and fill in the rest of the data, there's an error when I click save that says "14 values for 13 columns".

### Summary

From the admin scheduled-actions UI, adding a new dispatch task (e.g. `locate_job_page` with input state `NO_OPENINGS`) failed on save with SQLite **"14 values for 13 columns"** — `save_dispatch_task`'s `INSERT` column count did not match the bound value tuple.

#### Comments

##### susan — 2026-05-06T20:16:54.921Z

**Radia — review blocked (no branch to diff).** Linear lists `gitBranchName` `chuckles/ast-374-saving-new-task-dispatch-record-14-values-for-13-columns`, but that ref is **not** on `origin` from the review environment (`git ls-remote` / `origin/dev…origin/<branch>` has no match), so the branch could not be checked out or diffed. State: left **Code Complete** (no review posted). Push the feature branch (or correct the `gitBranchName`) and ping for a re-run. — Radia

##### susan — 2026-05-06T20:30:58.409Z

**Code review (Radia)** — used **local `dev`** commit **`4510d6e6`** because `git rev-parse chuckles/ast-374-…` failed (branch ref absent; per skill, an `origin/` feature ref is not required). **Counts:** fix-now **0** · discuss **0** · advisory **0**. **What's solid:** `save_dispatch_task` `INSERT` column list (13) now matches **13** placeholders and the 13-value bind tuple — fixes the reported SQLite "14 values for 13 columns" failure (**§2.4 / data-layer INSERT hygiene**). No combined feature doc was linked on the issue; findings stay here. — Radia

##### susan — 2026-05-06T20:55:21.354Z

Review feedback resolved. Branch `chuckles/ast-374-…` is ready for testing. Doc commit: `38faa33c` (combined plan + Resolution). INSERT fix already on `dev`: `4510d6e6`. — Betty

### Review (Radia, 2026-05-06)

- **Counts:** fix-now **0** · discuss **0** · advisory **0**
- **Finding:** `save_dispatch_task` `INSERT` lists **13** columns and **13** placeholders with a **13**-value bind tuple — matches `dispatch_task` schema (**§2.4 / INSERT hygiene**).
- **Note:** Radia reviewed the tree at **`4510d6e6`** on `dev` (feature ref was absent in her review environment).

### Resolution

**Date:** 2026-05-06 — Betty (`f-resolve-linear`)

- **Code:** Already on **`dev`** as **`4510d6e6`** — `fix(ast-374): align save_dispatch_task INSERT with 13 dispatch_task columns.`
- **This commit (`38faa33c`):** Adds the combined doc + Resolution only (no further code edits in the resolve pass).
- **Testing:** Re-save a new dispatch task from admin (same path as the report) and confirm the SQLite error is gone.

### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/data/database.py` | Align `save_dispatch_task` `INSERT` column list / placeholders / bind tuple to the 13 `dispatch_task` columns | `4510d6e6` (1 line) |

_Implementation detail may live in git history on `origin/dev`._
