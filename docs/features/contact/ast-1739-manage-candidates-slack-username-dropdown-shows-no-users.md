# AST-1739 — Manage Candidates Slack username dropdown shows no users

<!-- linear-archive: AST-1739 archived 2026-09-24 -->

## Linear archive (AST-1739)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1739/manage-candidates-slack-username-dropdown-shows-no-users  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** AST-1636 — Bind new Slack contacts to existing candidates by metadata before creating a prospect  
**Blocked by / blocks / related:** parent: AST-1636

### Description

## Susan report (verbatim)

\[bug\] When I open the Manage Candidate modal, when I click on the Slack username dropdown, I expect to see a list of all users on the astral slack workspace, but I don't see any. Thus, I am unable to assign known users to their candidate records.

## As-is

On Manage Candidates add/edit, the Slack username dropdown opens empty — no selectable Slack users — so known workspace users cannot be bound to candidate records.

## To-be

The Slack username dropdown lists the unbound Slack users available for binding (workspace posters not already on a candidate) so an admin can assign a known Slack identity to the candidate.

## Suggested engineer

Hedy Lamarr (AST-1668 unbound list + admin GET; empty dropdown most likely empty/failed pool from Contact API — Katherine AST-1669 owns the dropdown UI surface if the GET is fine).

## Parent

AST-1636

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
