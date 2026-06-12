# AST-509 — Add Middle name to the candidate profile

<!-- linear-archive: AST-509 archived 2026-06-03 -->

## Linear archive (AST-509)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-509/add-middle-name-to-the-candidate-profile  
**Status at archive:** Canceled  
**Project:** Astral Candidate  
**Assignee:** Susan Somerset  
**Priority / estimate:** No priority / —  
**Parent:** —  
**Blocked by / blocks / related:** children AST-510, AST-511 (both Canceled)

### Description

## Purpose

Candidates sometimes use a middle name on resumes, cover letters, and application forms. Astral today stores only first and last name on the candidate profile, so middle names cannot be recorded or reflected consistently in candidate-facing output. This feature adds middle name as a first-class profile field so identity data matches how candidates present themselves on job materials.

## Functional scope

* **Profile storage.** Middle name is stored on the candidate profile alongside first and last name. It persists with other profile contact fields in the candidate record.
* **Candidate Profile editing.** The Candidate Profile screen includes a middle name field in the contact/identity section. The candidate (or admin acting on their behalf) can enter, edit, clear, and save middle name through the same save flow as other profile fields.
* **Admin candidate management.** Create and edit flows for managing candidates expose middle name so admins can set it when onboarding a candidate without opening the full profile page.
* **Displayed full name.** When middle name is present, the product's displayed full name for the candidate includes it wherever the product already derives the candidate's display name from profile first and last name (for example resume and cover letter headers). When middle name is empty, display behavior is unchanged from today.
* **Prompt and artifact identity.** Middle name is available wherever the product resolves candidate identity from profile for generated content, consistent with how first and last name are used today.

## Boundaries

* Does not add suffixes, preferred names, maiden names, or other name variants beyond middle name.
* Does not change first or last name validation rules (first and last remain required where they are required today).
* Does not require middle name to be filled in; blank middle name is valid.
* Does not change candidate state machine transitions or nav gating.
* Does not redesign resume structure, cover letter templates, or unrelated profile fields.
* Automatic population of middle name from resume parsing is out of scope unless Susan answers otherwise in Open questions.
* Must not break existing candidates who have no middle name stored; they continue to behave as today.

## Acceptance criteria

1. A candidate profile can store a middle name value that round-trips through save and reload.
2. The Candidate Profile contact section shows a middle name field between first and last name (or in an equivalent logical position in that section).
3. Admin Manage Candidates create and edit flows include middle name and persist it on the candidate record.
4. When middle name is set, generated resume and cover letter output that shows the candidate's name from profile includes the middle name in the full displayed name.
5. When middle name is empty, name display and existing first/last-only behavior match current production behavior.
6. Existing candidates without a middle name require no migration action to continue working.

## Dependencies and blockers

None.

## Open questions

1. **Display format:** When middle name is present, should artifacts show the full middle name (`First Middle Last`) or an abbreviated form (`First M. Last`)?
   1. Use the whole middle name.
2. **Resume parsing:** Should saving profile with resume text attempt to populate middle name automatically from parsed resume content, or is manual entry only for this feature?
   1. Don't worry about resume parsing just yet.  let's just save the data

---

## Original brief

We need to track the middle name of our candidates.

### Comments

#### Chuckles Cursor — 2026-05-27T23:48:31.738Z

@susan Two open questions before dispatch:

1. **Display format:** When middle name is present, should artifacts show the full middle name (`First Middle Last`) or an abbreviated form (`First M. Last`)?
2. **Resume parsing:** Should saving profile with resume text attempt to populate middle name automatically from parsed resume content, or is manual entry only for this feature?

— Chuckles

#### Chuckles Cursor — 2026-05-27T23:50:39.485Z

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-509 (parent) | ftr/AST-509-add-middle-name-to-the-candidate-profile |
| AST-510 | sub/AST-509/AST-510-middle-name-profile-data-and-display-name |
| AST-511 | sub/AST-509/AST-511-middle-name-on-candidate-profile-and-admin |

AST-511 blockedBy AST-510.

— Chuckles

#### Chuckles Cursor — 2026-05-28T00:21:03.802Z

## Manual test steps

1. Restart the app if it is already running (local `dev` now includes AST-509).
2. **Candidate Profile:** Open Candidate → Profile. Confirm **Middle Name** appears between First and Last in Contact Information.
3. Enter a middle name, Save, reload the page — value persists.
4. Clear middle name, Save, reload — field is empty and first/last unchanged.
5. **Admin Manage Candidates:** Admin → Manage Candidates → Add Candidate. Confirm Middle Name field between First and Last; create a candidate with middle name set; confirm it saved.
6. Edit an existing candidate; change middle name; Save; reopen edit — value persisted.
7. Create with empty middle (first/last required) — should succeed.
8. **Resume header:** With middle name set on your test candidate, open a job with a generated resume and confirm the displayed name is **First Middle Last** (full middle, not abbreviated).
9. With middle blank, confirm resume name is still **First Last** only.

`origin/ftr/AST-509-add-middle-name-to-the-candidate-profile` @ `82979879` · local `dev` merged (§8). Child `sub/*` branches deleted.

— Chuckles

#### Chuckles Cursor — 2026-05-28T18:18:51.648Z

@susan Canceled per your request — AST-509 was a pipeline proof-of-concept, not a product ship.

**Linear:** AST-510 and AST-511 → **Canceled**; parent → **Canceled**.

**Git:** Reverted prep-uat merge on local `dev` (`31d74615`). Deleted `origin/ftr/AST-509-add-middle-name-to-the-candidate-profile`. Child `sub/*` were already deleted. **`origin/dev` unchanged** (never landed).

Agent worktrees (`dev-ada`, `dev-kath`, etc.) may still carry middle-name commits until each engineer merges `origin/dev` per integration line.

— Chuckles

---

**Canceled** 2026-05-28 — pipeline proof-of-concept; work never shipped to **`origin/dev`**. Child archives: `ast-510-middle-name-profile-data-and-display-name.md`, `ast-511-middle-name-on-candidate-profile-and-admin.md`.
