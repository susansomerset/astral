# AST-866 — List Management Discipline

<!-- linear-archive: AST-866 archived 2026-07-29 -->

## Linear archive (AST-866)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-866/list-management-discipline  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** susan  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** duplicate: AST-883

### Description

We have a habit of using free-floating lists for data validation and ui controls. 

We must have a code standard that centralizes and enforces the use of single-source lists.

For example, if the UI shows a list of tasks, the API that provides that list must use the array in TASK_CONFIG.  The array can be filtered by the API based on attributes of the task, but it cannot create one-off lists of task keys.

To begin with, we need a full audit of the existing codebase looking for examples of lists and dicts that would fail this standard, and create related but separate parent tickets to discuss and agree to the resolution of each.  

The deliverable for this ticket is the update to the coding standards for Radia's use, where any exceptions would be flagged as a FIX NOW issue.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
