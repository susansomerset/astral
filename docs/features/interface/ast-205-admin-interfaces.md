# AST-205 — Admin Interfaces

<!-- linear-archive: AST-205 archived 2026-06-03 -->

## Linear archive (AST-205)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-205/admin-interfaces  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** unassigned  
**Priority / estimate:** High / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Implement all six Admin screens. Admin is the interface for managing candidate-scoped content: the candidate record itself, and all AI-generated prompt content (agent prompts, task prompts, rubrics, analysis instructions, resume framework). These screens are prioritized before Candidate because they are needed to view and edit content as it migrates into the database.

**Screens:**

**Manage Candidates:** List Page. Each row is a candidate record. Columns: name, email, location, status. Bulk actions: none initially. Row action: open candidate detail (links to Candidate > Profile). Supports adding a new candidate via modal.

**Agent Prompts:** List Page. Each row is an agent prompt record keyed to a candidate. Columns: candidate, prompt label/name, last updated, approved status. Row action: open Modal to view/edit prompt content (long-form textarea). Bulk actions: none initially.

**Task Prompts:** List Page. Each row is a task prompt record. Columns: candidate, task key, prompt label, last updated. Row action: open Modal to view/edit. Note: task prompts reference candidate content by label; they do not contain candidate data directly.

**Rubrics:** List Page. Each row is a rubric (GET, DO, LIKE rubric content, keyed to candidate). Columns: candidate, rubric type, last updated, approved status. Row action: open Modal to view/edit.

**Analysis Instructions:** List Page. Each row is an analysis instructions block keyed to a candidate. Columns: candidate, instruction label, last updated, approved status. Row action: open Modal to view/edit.

**Resume Framework:** List Page. Each row is a resume framework record keyed to a candidate. Columns: candidate, section label, last updated, approved status. Row action: open Modal to view/edit full framework content.

**Acceptance Criteria:**

* All six screens implemented using ListPage and Modal components from Component Library
* Each screen fetches data from its Flask API endpoint
* Row-level edit via Modal with Save wiring to API (PUT/PATCH)
* Add new record supported where applicable (Manage Candidates minimum)
* Approved status field visible and toggleable where present
* All screens reachable via Admin nav links

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
