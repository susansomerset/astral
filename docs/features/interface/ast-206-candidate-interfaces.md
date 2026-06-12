# AST-206 — Candidate Interfaces

<!-- linear-archive: AST-206 archived 2026-06-03 -->

## Linear archive (AST-206)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-206/candidate-interfaces  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** unassigned  
**Priority / estimate:** Medium / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Implement all six Candidate screens. These screens are the primary interface for viewing and editing the candidate's profile and content — the human-facing side of what Astral Candidate generates and maintains.

**Screens:**

**Profile:** DetailsEditPage. Single candidate record. Fields: name, address, email, phone, location. Full-page edit with Save/Cancel. This is the one Details Edit Page in the application.

**Strengths:** Modal-backed List Page. Each row is a candidate strength entry. Columns: strength label, summary, approved status. Row action: open Modal to view/edit full content.

**Goals:** Modal-backed List Page. Each row is a goal entry. Columns: goal label, summary, approved status. Row action: open Modal to view/edit.

**Deal Breakers:** Modal-backed List Page. Each row is a deal breaker entry. Columns: label, summary, approved status. Row action: open Modal to view/edit.

**Experience:** Modal-backed List Page. Each row is an experience entry (role, company, period). Columns: title, company, dates, approved status. Row action: open Modal to view/edit full experience detail.

**Base Resume:** DetailsEditPage or full-screen Modal (Chuckles to decide based on content length). Displays the candidate's assembled base resume content. Editable. Save wired to API.

**Acceptance Criteria:**

* All six screens implemented using ListPage, Modal, and DetailsEditPage components from Component Library
* Profile screen uses DetailsEditPage; content saves correctly via API
* List-backed screens (Strengths, Goals, Deal Breakers, Experience) fetch and display records from API
* Row-level edit via Modal with Save wiring
* Approved status visible and toggleable where present
* All screens reachable via Candidate nav links

### Comments

#### susan — 2026-03-04T01:01:25.367Z
Descoping Base Resume for now.

---

_Implementation detail may live in git history on `origin/dev`._
