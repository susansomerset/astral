# AST-1371 — Regenerate resume button does not appear for resumes with unsupported content

<!-- linear-archive: AST-1371 archived 2026-08-31 -->

## Linear archive (AST-1371)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1371/regenerate-resume-button-does-not-appear-for-resumes-with-unsupported  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 2  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

AST-1345 taught the product to refuse non-array `experience` with the operator message that says to regenerate — but on Artifacts → Base Resume Content that message can appear in the experience section while the header has no Regenerate control, so the operator is told to act and given no way to act. This epic closes that dead end: when unsupported resume structure is shown for experience on Base Resume Content, Regenerate is present and usable so Susan can craft a valid job-array experience without leaving the page or guessing state tricks.

## Functional scope

* On Artifacts → Base Resume Content, when the experience section shows the unsupported resume structure message (legacy string or any non-array experience shape), the page header shows a primary Regenerate control (Generate only if there is no existing base resume content to regenerate).
* Activating that control starts the same Base Resume craft path already used for Generate/Regenerate on that page (`craft_resume_base`), including the existing confirm modal when regenerating over content.
* After a successful regenerate that stores array-shaped experience, the unsupported message is gone and the experience job-array editor is usable again; Print and other emit paths keep their existing unsupported toast / no-tab behavior until that succeeds.
* While an artifacts daisy-chain request is in flight (states that already hide Generate/Regenerate today), this epic does not force the button back on; outside those in-flight states, the unsupported experience message must never be an unactionable dead end on Base Resume Content.

## Architectural definition

* **Patterns to reuse** — `pattern.ui.shared-button-roles` (Regenerate stays `btn` + `primary`, including in-flight busy); `pattern.config.config-block` (unsupported message and generate-state lists stay config-owned; do not hardcode the toast string or ad-hoc state sets in React).
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.layers.ui-config-driven-business-logic` (visibility/enablement from config/manifest, not one-off React state lists); `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.ui.frontend-file-placement` / `astral.ui.naming-conventions`; `astral.standards.in-scope-only`; `astral.standards.dry-and-focused-functions`; `astral.standards.names-not-ticket-ids`. Universal product-code set applies to any `src` touch.

## Boundaries

* Does **not** migrate or rewrite legacy string/non-array experience blobs into the job-array shape.
* Does **not** change the unsupported operator message text (config-owned `unsupported resume structure, please regenerate`) or reopen AST-1345 / AST-1349–1351 contract, toast, or no-emit rules.
* Does **not** change Admin Session Resume Paste, job Print Resume / Cover Letter, or Print placement on Base Resume Content beyond ensuring Regenerate is visible alongside existing header actions when required.
* Does **not** force Generate/Regenerate visible during REQUESTED_ARTIFACTS / chain in-flight states that already hide those controls by design (AST-1253).
* Does **not** redesign ArtifactEditor chrome, experience job-array happy-path editing, or daisy-chain hop UX.
* Must not break array-shaped experience editing, Print validate-then-blob, or generate confirm / in-flight button behavior for eligible candidates.

## Acceptance criteria

1. With a selected candidate whose saved `artifacts.base_resume.experience` is a legacy string or other non-array shape, opening Artifacts → Base Resume Content shows the unsupported resume structure message on the experience section **and** shows Regenerate in the page header (Generate only if there is no base resume content to regenerate).
2. Clicking that Regenerate control starts Base Resume craft (`craft_resume_base`) with the same confirm-when-regenerating behavior as today for eligible candidates.
3. After craft succeeds with array-shaped experience, the unsupported message is gone and the experience job-array editor is usable without a reload trick.
4. Candidates in artifacts-chain in-flight states that already hide Generate/Regenerate keep that hide; Print and other emit paths still toast unsupported and open no HTML tab until experience is array-shaped.
5. Candidates with valid job-array experience keep current Generate/Regenerate visibility and editor behavior (no regression).

## Dependencies and blockers

none (AST-1345 family Done on `dev`; this is a follow-on UI affordance gap).

## Open questions

none

## Proposed child tickets

#### 1: **Regenerate affordance when experience is unsupported - Katherine**

Owns making Regenerate (or Generate when empty) appear and work on Artifacts → Base Resume Content whenever the experience section shows the unsupported resume structure message, outside daisy-chain in-flight hide states — including any config/manifest generate-state escape hatch required so that message is never unactionable on this page. Does **not** migrate data, change the unsupported message literal, or reopen Print/no-emit core gates.
**Citations:** `pattern.ui.shared-button-roles`, `pattern.config.config-block`, `astral.layers.ui-config-driven-business-logic`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`, `astral.standards.in-scope-only`
**Estimate: 2**

Monolith check: Functional scope has 4 capabilities; single child is intentional — one inseparable Base Resume Content visibility + craft handoff slice for UAT.

---

## Original brief

Looking at a base_resume content that isn't structured as an array, I get the message of "unsupported format, please regenerate", but the Regenerate button does not actually appear in the header as expected.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
