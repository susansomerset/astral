# AST-1314 — Add a Print button to Base Resume Content

<!-- linear-archive: AST-1314 archived 2026-08-31 -->

## Linear archive (AST-1314)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1314/add-a-print-button-to-base-resume-content  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 2  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Operators author and save a candidate’s Base Resume Content, but they cannot open a print-ready HTML preview from that page the way they already can from Admin Session Resume Paste. This epic adds a Print control on Base Resume Content so Susan can verify structure, section formats, accent, and body content via browser Print → PDF before relying on job-tailored Print Resume elsewhere.

## Functional scope

* With a candidate selected on Artifacts → Base Resume Content, a Print control is available when that candidate has printable base resume content.
* Activating Print opens a new browser tab with print-ready HTML rendered from the selected candidate’s saved base resume content and resume structure — the same operator outcome as Session Resume Paste’s Open HTML flow (HTML tab, then browser Print → PDF). No job id is required.
* Failed or empty HTML never opens a blank/broken tab as if success occurred; the Base Resume Content page surfaces a clear error instead.
* Print uses last-saved candidate base resume content and structure (not an unsaved in-editor draft buffer).

## Architectural definition

* **Patterns to reuse** — `pattern.ui.shared-button-roles` (Print is a neutral alternate labeled control: `btn` + `secondary`, not a one-off style); Session Resume Paste’s established Open-HTML → new-tab operator flow (error-check response before opening a tab). Prefer the existing authenticated candidate base HTML surface (`/candidate/resume/base` + `build_base_resume`) as the candidate-bound sibling to Admin Session Resume Paste’s in-memory HTML path — do not invent a third emit pipeline.
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.idioms.require-auth-on-protected-endpoints` (reuse/require auth on any HTML surface touched); `astral.ui.frontend-file-placement` / `astral.ui.naming-conventions` (page/control placement and names); `astral.layers.ui-config-driven-business-logic` (UI stays thin; emit stays in core builder); `astral.standards.in-scope-only`; `astral.standards.dry-and-focused-functions`; `astral.standards.names-not-ticket-ids`. Universal product-code set applies to any src touch.

## Boundaries

* Does **not** change Admin Session Resume Paste, its parse API, or admin-only `POST /api/admin/session_resume/html`.
* Does **not** change job Print Resume / Print Cover Letter on the Recommended Job Report (`/candidate/resume/<job_id>`, `/candidate/cover/<job_id>`).
* Does **not** generate server-side PDF; operator uses browser Print → PDF from the HTML tab.
* Does **not** print unsaved editor buffer state; Save first, then Print.
* Does **not** own craft/parse hops, structure catalog changes, or Highlights-required work (**AST-1326** and children).
* Does **not** alter cover-letter emit or Session Cover Letter.

## Acceptance criteria

1. On Base Resume Content with a selected candidate that has saved printable base resume content, Susan can activate Print and get a new tab of print-ready HTML for that candidate’s base resume (structure order, section titles/formats, accent as already emitted by the base-resume builder).
2. Susan can use the browser’s Print → PDF from that tab without needing a job id or leaving Artifacts for Session Resume Paste.
3. With no candidate selected, or when base resume content is missing/unusable, Print is unavailable or fails with a clear on-page error — and no blank HTML tab opens.
4. A failed HTML response never opens a success-looking blank/broken tab.
5. Job Print Resume / Print Cover Letter and Session Resume Paste behavior are unchanged.

## Dependencies and blockers

none. Candidate base HTML emit (`build_base_resume` / `/candidate/resume/base`) and format-aware section emit (**AST-1304**) already exist. **AST-1326** (Highlights required) is adjacent authoring work, not a blocker for Print.

## Open questions

none

## Proposed child tickets

#### 1: **Print control on Base Resume Content - Katherine**

Wire a Print control on Artifacts → Base Resume Content for the selected candidate. On success, open print-ready HTML in a new tab using the same operator flow as Session Resume Paste Open HTML (validate response, then open tab; no blank tab on failure). Source is the candidate’s saved base resume content via the existing candidate-bound base HTML path — not Admin session paste and not job-tailored resume routes. Does **not** own emit pipeline changes beyond wiring, Session Resume Paste, or job Print controls.
**Citations:** `pattern.ui.shared-button-roles`; `astral.idioms.require-auth-on-protected-endpoints`; `astral.ui.frontend-file-placement`; `astral.layers.ui-config-driven-business-logic`; `astral.standards.in-scope-only`
**Estimate: 2**

Monolith check: Functional scope has four bullets but one inseparable UI wire to an existing emit surface — single child intentional.

---

## Original brief

Use the same method as is used in the Session Resume Paste, but use the candidate's base resume content.

### Comments

#### susan — 2026-08-12T17:46:30.383Z
\[bug\]

When adding buttons to a page, or any UI additions or changes, consider in the planning process the appropriate location, if not specified, to make that change or to put that button.   In this case, the button was placed at the top of the screen, unstyled like the others, etc.

Meanwhile, put the Print button next to the Regenerate button, please.

#### susan — 2026-08-12T17:40:17.616Z
\[bug\]

Clicking the button while looking at the base_resume I'm looking at generates an error:

```
Astral error diagnostic
timestamp: 2026-08-12T17:40:04.654Z
message: Candidate missing artifacts.base_resume
route: /artifacts/base_resume_content
astral_candidate_id: abrams
```

---

_Implementation detail may live in git history on `origin/dev`._
