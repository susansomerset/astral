# AST-217 — Edit Context Lists

<!-- linear-archive: AST-217 archived 2026-06-03 -->

## Linear archive (AST-217)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-217/edit-context-lists  
**Status at archive:** Done  
**Project:** Astral Candidate  
**Assignee:** susan  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Five context screens where the candidate provides weighted lists of personal content that drive all downstream AI generation. Each screen maps to a candidate state. Lists are manually editable to start; AI interview generation (coatcheck) is a future enhancement explicitly out of scope here.

**Acceptance Criteria:**

**Shared Data Shape (all survey types):**
Each item in every survey array follows this structure:

* description: TEXT (natural language expression of the item)
* priority: INTEGER 1–5 (importance to candidate; 5 = highest)
* created_at, updated_at: TIMESTAMP

**Survey Screens and State Mapping:**

**Strengths (SURVEY_STRENGTHS):**

* Nav item unlocks when state = PROFILE_READY
* Candidate enters their professional superpowers
* Each item: what they're exceptionally good at, priority weight
* Clicking Strengths nav when state = PROFILE_READY transitions state → SURVEY_STRENGTHS

**Goals / Priorities (SURVEY_PRIORITIES):**

* Nav item unlocks when state = SURVEY_STRENGTHS
* Candidate enters ambitions, ideal job characteristics, career direction
* Each item: what they want from their next role, priority weight

**Deal Breakers (SURVEY_DEAL_BREAKERS):**

* Nav item unlocks when state = SURVEY_PRIORITIES
* Candidate enters hard nos: culture, comp, industry, role type, etc.
* Each item: what they will not accept, priority weight

**Backstory (SURVEY_DEAL_BREAKERS → SURVEY_BACKSTORY):**

* Nav item unlocks when state = SURVEY_DEAL_BREAKERS
* Maps to Candidate nav item "Backstory" (replaces "Experience" from Interface design)
* Each item describes a past role: what was loved, tolerated, and why they left
* Description convention (not enforced, surfaced as hint): "As <job title> at <company>, loved X, tolerated Y, left because Z"
* Priority reflects how formative/relevant that role was

**Base Resume (SURVEY_BASE_RESUME):**

* Nav item unlocks when state = SURVEY_BACKSTORY
* Candidate reviews and edits the structured resume sections parsed from their resume_raw
* Sections displayed as editable fields: resume_summary (textarea), resume_competencies, resume_experiences, resume_previous_experience, resume_education_certifications, resume_skills (each as list of editable items)
* Candidate corrects any parse errors or adds missing content
* This is the immutable source of truth for resume content — Artifacts assembly will pull from these fields, never from AI generation

**UI Pattern (all survey screens):**

* ListPage component showing current array items
* Columns: description (truncated), priority (1–5 badge), updated_at
* Add new item via Modal (description textarea + priority selector 1–5)
* Edit existing item via Modal (same fields, pre-populated)
* Delete item with confirmation
* Changes write directly to candidate_data array in candidate table via API
* Empty list is valid — no minimum required at this stage (completion gate is separate feature)

**State Transitions:**

* PROFILE_READY → SURVEY_STRENGTHS (on first click of Strengths nav)
* SURVEY_STRENGTHS → SURVEY_PRIORITIES (on first click of Goals nav)
* SURVEY_PRIORITIES → SURVEY_DEAL_BREAKERS (on first click of Deal Breakers nav)
* SURVEY_DEAL_BREAKERS → SURVEY_BACKSTORY (on first click of Backstory nav)
* SURVEY_BACKSTORY → SURVEY_BASE_RESUME (on first click of Base Resume nav)

**Future Enhancement (explicitly out of scope):**

* Coatcheck: if a survey array is empty, trigger a stateful AI interview to generate items for candidate review. Not built here. Empty array = empty list = manual entry only.

**Database:**

* candidate table: UPDATE candidate_data (merge array for relevant key), updated_at
* All reads/writes go through candidate_data JSON blob — no separate table

Subissues:
Wire Base Resume screen

**Scope:** De-stub Base Resume with sectioned editable resume fields -- different from other surveys.

* De-stub BaseResume.tsx
* Different from other surveys: displays parsed resume sections as editable fields, not a flat list
* Sections from candidate_data: resume_summary (textarea), resume_competencies (editable list), resume_experiences (editable list), resume_previous_experience (editable list), resume_education_certifications (editable list), resume_skills (editable list)
* Each list section: items can be added, edited, deleted inline
* Save writes all sections back to candidate_data via PUT /api/candidates/<id>/survey/base_resume
* DATA_SHAPES entry: candidates.detail.base_resume -- sectioned layout similar to profile
* This is the immutable source of truth for resume content -- Artifacts assembly pulls from here

**Layer:** ui/frontend/src/pages/Candidate/BaseResume.tsx, src/utils/config.py

## Metadata

* URL: [AST-232](https://linear.app/astralcareermatch/issue/AST-232/wire-base-resume-screen)
* Identifier: [AST-232](https://linear.app/astralcareermatch/issue/AST-232/wire-base-resume-screen)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Candidate](https://linear.app/astralcareermatch/project/astral-candidate-f048b61dbb2c). Process of reviewing, interviewing, revising and reformatting the candidate base resume and context files.
* Created: 2026-02-28T21:13:26.210Z
* Updated: 2026-03-01T22:10:59.553Z

---

# Survey ListPage component pattern and DATA_SHAPES

**Scope:** Add shared DATA_SHAPES entries for survey screens and establish the reusable survey page pattern.

* Shared approach for all survey screens (except Base Resume which has special layout)
* Add DATA_SHAPES entries to [config.py](<http://config.py>):
  * candidates.list.survey -- shared columns: description (truncated), priority (1-5 badge), updated_at
  * candidates.edit.survey -- shared fields: description (textarea), priority (select 1-5)
* No new React components -- reuse ListPage + Modal pattern already built
* Each survey page fetches shapes from /api/shapes/candidates and data from /api/candidates/<id>/survey/<key>

**Layer:** src/utils/config.py (DATA_SHAPES), ui/frontend/

## Metadata

* URL: [AST-229](https://linear.app/astralcareermatch/issue/AST-229/survey-listpage-component-pattern-and-data-shapes)
* Identifier: [AST-229](https://linear.app/astralcareermatch/issue/AST-229/survey-listpage-component-pattern-and-data-shapes)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Candidate](https://linear.app/astralcareermatch/project/astral-candidate-f048b61dbb2c). Process of reviewing, interviewing, revising and reformatting the candidate base resume and context files.
* Created: 2026-02-28T21:13:22.885Z
* Updated: 2026-03-01T22:11:00.878Z

---

# Wire Strengths, Goals, Deal Breakers screens

**Scope:** De-stub three survey pages using the shared survey ListPage + Modal pattern.

* De-stub three pages: Strengths.tsx, Goals.tsx, DealBreakers.tsx
* Each follows identical pattern: fetch shapes, fetch survey data, render ListPage, Modal for add/edit
* Delete with confirmation dialog
* State transition fires automatically on first page load (API handles it)
* All three screens use same survey DATA_SHAPES columns and edit fields

**Layer:** ui/frontend/src/pages/Candidate/

## Metadata

* URL: [AST-230](https://linear.app/astralcareermatch/issue/AST-230/wire-strengths-goals-deal-breakers-screens)
* Identifier: [AST-230](https://linear.app/astralcareermatch/issue/AST-230/wire-strengths-goals-deal-breakers-screens)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Candidate](https://linear.app/astralcareermatch/project/astral-candidate-f048b61dbb2c). Process of reviewing, interviewing, revising and reformatting the candidate base resume and context files.
* Created: 2026-02-28T21:13:23.898Z
* Updated: 2026-03-01T22:11:00.825Z

---

# Survey API endpoints

**Scope:** Add CRUD endpoints for survey arrays to candidate Blueprint with state transition on first access.

* Add to candidate Blueprint (ui/api/candidate.py):
  * GET /api/candidates/<id>/survey/<survey_key> -- returns array from candidate_data
  * POST /api/candidates/<id>/survey/<survey_key> -- append new item (description, priority, timestamps)
  * PUT /api/candidates/<id>/survey/<survey_key>/<idx> -- update item by index
  * DELETE /api/candidates/<id>/survey/<survey_key>/<idx> -- remove item by index
* Valid survey_key values: strengths, priorities, deal_breakers, backstory, base_resume
* State transition on first GET: if candidate is at prerequisite state for this survey, advance (e.g., first GET of strengths when state=PROFILE_READY transitions to SURVEY_STRENGTHS)
* Core function: update_survey_item(candidate_id, survey_key, action, data) in [candidate.py](<http://candidate.py>)

**Layer:** ui/api/candidate.py, src/core/candidate.py

## Metadata

* URL: [AST-228](https://linear.app/astralcareermatch/issue/AST-228/survey-api-endpoints)
* Identifier: [AST-228](https://linear.app/astralcareermatch/issue/AST-228/survey-api-endpoints)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Candidate](https://linear.app/astralcareermatch/project/astral-candidate-f048b61dbb2c). Process of reviewing, interviewing, revising and reformatting the candidate base resume and context files.
* Created: 2026-02-28T21:13:21.141Z
* Updated: 2026-03-01T22:11:00.911Z

---

# Wire Backstory screen and rename Experience

**Scope:** Rename Experience to Backstory in nav config and routes, de-stub with survey pattern.

* Rename "Experience" to "Backstory" in NAV_CONFIG ([config.py](<http://config.py>))
* Update route path from /candidate/experience to /candidate/backstory
* Update routes.tsx to match
* Rename/move page file if needed
* Same survey ListPage + Modal pattern as Strengths/Goals/Deal Breakers
* Hint text in description field: "As \[job title\] at \[company\], loved X, tolerated Y, left because Z"

**Layer:** ui/frontend/src/pages/Candidate/, src/utils/config.py, ui/frontend/src/routes.tsx

## Metadata

* URL: [AST-231](https://linear.app/astralcareermatch/issue/AST-231/wire-backstory-screen-and-rename-experience)
* Identifier: [AST-231](https://linear.app/astralcareermatch/issue/AST-231/wire-backstory-screen-and-rename-experience)
* Status: Done
* Priority: Medium
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Candidate](https://linear.app/astralcareermatch/project/astral-candidate-f048b61dbb2c). Process of reviewing, interviewing, revising and reformatting the candidate base resume and context files.
* Created: 2026-02-28T21:13:25.017Z
* Updated: 2026-03-01T22:11:00.469Z

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
