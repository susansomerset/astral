# AST-1519 — agent_task.json updates

<!-- linear-archive: AST-1519 archived 2026-09-09 -->

## Linear archive (AST-1519)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1519/agent-taskjson-updates  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Execution plan

1. Edit `data/admin/agent_task.json` on `$ASTRAL_MAIN` (`dev`): delete the row whose `task_key` is `parse_meteorite_email`.
2. For every remaining row whose `task_key` contains `meteorite`, set `task_group_order` to `4500` and `task_group_name` to `Meteorite Review` (includes keys already on that group and any still on Job Review / other groups).
3. Keep JSON valid and row shape unchanged aside from the remove + group fields above (no prompt/agent_id edits).
4. If `docs/uat-fixtures/AST-756/expected-agent_task.json` (or other committed twins of this catalog) must stay byte-aligned with the admin file, update those twins the same way.
5. Commit on `dev` and push `origin/dev`.

## Done when

* `parse_meteorite_email` is absent from `data/admin/agent_task.json`.
* Every remaining `task_key` containing `meteorite` has `task_group_order` `4500` and `task_group_name` `Meteorite Review`.
* Change is on `origin/dev`.

## Risks / open questions

* Literal “meteorite in the task_key” also hits `meteorite_email` (currently unassigned) and `craft_evaluate_meteorite_rubric` (currently Candidate Artifacts / 2000). Confirm those should move into Meteorite Review 4500, or name an exclude list before Todo implement.
  * Oooh, good catch!  Yes, meteorite_email goes to 4500, but craft_* stays put where it is.
* Removing `parse_meteorite_email` may still leave legacy references in code/config (`legacy_agent_task_key`); this task is catalog-only unless Susan widens scope.
  * That's okay.  I just want to stop having it crop up.
* Catalog twins under `docs/uat-fixtures/` may fail tests if not updated with the same edit.
  * We can fix the tests if/when we hit them.

---

## Original brief

Please update agent_task for the following points:

1. Remove "parse_meteorite_email"
2. For all tasks with "meteorite" in the task_key, set the group number to 4500 and the group name to "Meteorite Review"

commit and push to dev origin.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
