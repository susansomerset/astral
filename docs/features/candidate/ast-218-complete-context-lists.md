# AST-218 — Complete Context Lists

<!-- linear-archive: AST-218 archived 2026-06-03 -->

## Linear archive (AST-218)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-218/complete-context-lists  
**Status at archive:** Done  
**Project:** Astral Candidate  
**Assignee:** susan  
**Priority / estimate:** High / 2  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Completion gate that verifies all survey arrays are populated before advancing the candidate to CONTENT_READY. Surfaces a clear checklist so the candidate knows exactly what remains.

**Acceptance Criteria:**

**Completion Requirements:**
All five of the following candidate_data arrays must be non-empty:

* strengths (at least 1 item)
* priorities (at least 1 item)
* deal_breakers (at least 1 item)
* backstory (at least 1 item)
* resume_experiences (at least 1 item — proxy for base resume completeness)

**UI:**

* Completion status visible on each survey screen (e.g. green checkmark when array is non-empty)
* Summary checklist surfaced on Base Resume screen (final survey screen) showing status of all five
* "Ready for Astral" confirm button on Base Resume screen, enabled only when all five are complete
* On confirm: state → CONTENT_READY, success message, Build Consult Prompts triggered automatically

**State Transition:**

* SURVEY_BASE_RESUME → CONTENT_READY (on candidate confirmation with all arrays non-empty)
* CONTENT_READY triggers Build Consult Prompts (see next feature)

**Validation:**

* Server-side check on confirm: re-verify all arrays non-empty before accepting state transition
* Client-side check: disable confirm button if any array is empty (UX guard, not security)

**Database:**

* candidate table: UPDATE state = CONTENT_READY, state_changed_at, updated_at

# Complete Context Lists

**Scope:** Build shared completion gate pattern in core/candidate.py for both survey and prompt gates, with API endpoints.

* Core functions in src/core/candidate.py:
  * check_completion_gate(candidate_id, gate_type) -- returns status dict with per-item checklist
  * complete_gate(candidate_id, gate_type) -- validates all items present, transitions state
* Gate types:
  * survey: checks strengths, priorities, deal_breakers, backstory, resume_experiences all non-empty; transitions SURVEY_BASE_RESUME -> CONTENT_READY; triggers background prompt generation on success
  * prompts: checks all required agent_content rows exist for candidate; checks rubric rows (GET/DO/LIKE) approved; transitions CONTENT_READY -> LIVE_PROMPTS
* API endpoints in candidate Blueprint:
  * GET /api/candidates/<id>/gates/<gate> -- returns checklist status
  * POST /api/candidates/<id>/gates/<gate> -- validate and advance
* Server-side validation before accepting any transition

**Layer:** src/core/candidate.py, ui/api/candidate.py

## Metadata

* URL: [AST-233](https://linear.app/astralcareermatch/issue/AST-233/completion-gate-logic-shared-backend)
* Identifier: [AST-233](https://linear.app/astralcareermatch/issue/AST-233/completion-gate-logic-shared-backend)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Candidate](https://linear.app/astralcareermatch/project/astral-candidate-f048b61dbb2c). Process of reviewing, interviewing, revising and reformatting the candidate base resume and context files.
* Created: 2026-02-28T21:13:27.647Z
* Updated: 2026-03-01T22:11:05.105Z

---

# Complete Context Lists

**Scope:** Add completion checklist and confirm button to Base Resume page.

* Green checkmarks per survey section on Base Resume page
* Summary checklist showing all 5 survey statuses (fetched from /api/candidates/<id>/gates/survey)
* "Ready for Astral" confirm button, enabled only when all 5 complete
* On confirm: calls POST /api/candidates/<id>/gates/survey, shows success message
* Client-side disabled state is UX guard only; server validates

**Layer:** ui/frontend/src/pages/Candidate/BaseResume.tsx

## Metadata

* URL: [AST-234](https://linear.app/astralcareermatch/issue/AST-234/completion-ui-on-base-resume-screen)
* Identifier: [AST-234](https://linear.app/astralcareermatch/issue/AST-234/completion-ui-on-base-resume-screen)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Candidate](https://linear.app/astralcareermatch/project/astral-candidate-f048b61dbb2c). Process of reviewing, interviewing, revising and reformatting the candidate base resume and context files.
* Created: 2026-02-28T21:13:28.672Z
* Updated: 2026-03-01T22:11:05.073Z

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
