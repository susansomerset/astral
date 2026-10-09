# AST-1899 — Add Save to candidate button

<!-- linear-archive: AST-1899 archived 2026-10-08 -->

## Linear archive (AST-1899)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1899/add-save-to-candidate-button  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 1  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The Session Resume Paste admin page (**Admin → Session Resume Paste**) already turns a pasted resume into structured base-resume JSON with Ruth, but the result dies in the browser: the only exits are View Parsed JSON and Open HTML. To make that parse the selected candidate's real base resume today, Susan has to re-key it section by section in Base Resume Content. This ticket adds one button that saves the parsed result as the selected candidate's current `base_resume` artifact. It goes through the same save path the Base Resume Content editor already uses, so versioning, validation and every downstream reader (craft, job drafting, print) behave exactly as if the resume had been typed into the editor.

## Functional scope

1. **Save to Candidate button.** The Session Resume Paste page gets a **Save to Candidate** button in its existing button row, right of **Open HTML**. It is enabled only when a candidate is selected and a successful parse is on the page. It is disabled while a parse, Open HTML, or a save is in flight, and reads **Saving…** during its own save.
2. **Saves as the candidate's base resume.** Clicking it saves the parsed base-resume sections as the selected candidate's current `base_resume` artifact through the existing candidate data save, with no confirm prompt. The save writes a new artifact row and sets earlier versions to `current = 0`, exactly as an editor save does. An identical body is a no-op, per the existing save rules.
3. **Parse's section layout replaces the candidate's.** The save also writes the parse's resume sections (titles, order, enabled flags, formats) as the candidate's resume structure, so every parsed section lands and none is dropped for being disabled in the candidate's old layout. The candidate's accent color is not a section setting and is kept.
4. **Experience comes across cleanly.** Each parsed experience job (company, title, dates, location, accomplishments) is saved exactly as parsed and opens in the Base Resume Content experience editor as a separate job with its accomplishments list intact. The parse and the save share one experience contract, so the page passes experience through untouched rather than reshaping it.
5. **Feedback.** Success shows a success toast naming the save. Failure shows the server's error message as an error toast and in the page's inline error line, and the parse stays on the page so Save can be retried.
6. **Page copy.** The intro line's "does not save to the database" becomes accurate: Parse and Open HTML still do not save; **Save to Candidate** writes the base resume and its section layout.

## Component scope

* `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx`: **modified**. New Save to Candidate button, save handler, busy state, and updated intro copy.

No backend file changes. The existing `PUT /api/candidates/<id>/data` route in `src/ui/api/api_candidate.py` already routes `artifacts.base_resume` through ingest, structure filter and the operative write (`save_candidate_data` on `candidate.artifacts.base_resume`). It is reused as-is, not modified.

Tests and test-bible pages (`tests/component/frontend/pages/test_AdminSessionResumePaste.test.tsx`, `docs/test-bible/frontend/pages.md`) belong to Betty in `qa-child`. No file is deleted.

**Out of scope:** any new admin route (no `/api/admin/session_resume/save`); `src/ui/api/api_admin.py` and `run_session_resume_parse` (parse stays response-only and not bound to the candidate); `ArtifactsBaseResumeContent.tsx` / `ArtifactEditor.tsx`; saving the pasted text as the candidate's original resume text (`context.raw_resume`); the Session Cover Letter page; and any schema change.

## Technical scope

* `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx`: new async save handler. With `selectedId` and `lastParse` present, it PUTs `/api/candidates/<selectedId>/data` with body `{ artifacts: { resume_structure: { sections: lastParse.resume_structure.sections }, base_resume: lastParse.base_resume } }`: sections only, no `accent_color`, so the existing route replaces the candidate's sections and keeps the accent (Functional scope 3). `base_resume` (experience job array included) is sent exactly as parsed, with no client-side reshaping or filtering (Functional scope 4). The route's existing ingest/filter then keys content to the parse's enabled sections. On a non-OK response it reads the JSON `error` (falling back to `HTTP <status>`) into the inline error line and an error toast. On OK it shows a success toast. New `saving` state disables all three existing buttons plus Save while in flight (and Save is disabled while `parsing` / `opening`). New `.btn secondary` button in the existing row, after Open HTML. The intro paragraph text is modified per Functional scope 6. `lastParse` / `pasteText` local-storage behavior is unchanged.

## Architectural definition

* **Patterns to reuse:**
  * `patt.artifact.write-operative`: Save lands as a new current `base_resume` version (prior retired, identical-body no-op) through the existing entity save path, never an in-place update or a new write path. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.artifact.write-operative.md>)
  * `patt.artifact.ui-consistency` (Implementation §5, Save contract only): persist through the existing candidate data API with `{ artifacts: { base_resume: … } }`, with no parallel storage key and no client `artifact_id`. The editor-component part of the pattern does not apply; the pattern's own Exceptions list session paste as a non-editor form. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.artifact.ui-consistency.md>)
* **New patterns proposed:** none.
* **Applicable statutes:**
  * `astral.standards.dry-and-focused-functions`: reuse the existing candidate save route and its ingest/filter logic. Do not duplicate structure filtering or base-resume shaping in React. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.dry-and-focused-functions.md>)
  * `astral.layers.ui-config-driven-business-logic`: section normalization, content filtering and experience validation stay server-side in the existing save route. The page carries no section-id list or experience field list of its own. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/layers/astral.layers.ui-config-driven-business-logic.md>)
  * `astral.standards.in-scope-only`: one page file changes. No backend, route, or editor edits ride along. [current file](<https://github.com/susansomerset/astral/blob/dev/canon/statutes/astral/standards/astral.standards.in-scope-only.md>)

## Acceptance criteria

1. **Button present and gated.** In `test_AdminSessionResumePaste.test.tsx`, **Save to Candidate** renders as the fourth button in the row (after Open HTML). It is disabled with no selected candidate, disabled with no `lastParse`, and disabled while Parse or Open HTML is in flight. It is enabled once a successful parse exists and a candidate is selected. Fail = missing, wrong position, or enabled in any of those disabled cases.
2. **Correct request.** Clicking Save sends exactly one `PUT /api/candidates/<selectedId>/data` whose JSON body is `{"artifacts":{"resume_structure":{"sections":<lastParse.resume_structure.sections>},"base_resume":<lastParse.base_resume>}}`. `base_resume` deep-equals `lastParse.base_resume`, and there is no `accent_color` or `artifact_id` key. Fail = a different route, a POST, a reshaped `base_resume`, extra keys, or a request to any `/api/admin/session_resume/*` save route.
3. **Persists as current base resume.** In UAT, parse a resume with candidate X selected, click Save, then open **Base Resume Content** for X: every parsed section appears with its parsed body. `SELECT COUNT(*) FROM artifacts WHERE entity_type='candidate' AND entity_id='<X>' AND artifact_type='base_resume' AND current=1` returns 1, and the prior current row (if any) now has `current=0`. Fail = editor shows the old resume, two current rows, or the prior row was updated in place.
4. **Layout replaced, accent kept.** After Save, X's section titles/order/enabled flags on Base Resume Content match `lastParse.resume_structure.sections`, and X's accent color is unchanged from before Save. Fail = X's old layout survives, a parsed section is missing, or the accent color changed.
5. **Experience clean.** After Save, `GET /api/candidates/<X>` returns `candidate_data.artifacts.base_resume.experience` deep-equal to `lastParse.base_resume.experience` (same job count, order, and `company`/`title`/`dates`/`location`/`accomplishments` values). The Base Resume Content experience editor shows one job per entry, with accomplishments as separate list items. Fail = a job is missing, merged, or reordered, a field is blank, accomplishments are collapsed into one string, or experience is absent.
6. **Feedback.** On 200, a success toast shows. On a mocked 400 `{"error":"boom"}`, the error toast and inline error both read `boom`, and **Save to Candidate** is enabled again with `lastParse` still present. Fail = no toast, generic message instead of the server's, or parse cleared.
7. **No backend change.** `git diff origin/dev...<ftr> --stat -- src/ui/api src/core src/data src/utils` is empty, and `grep -n "session_resume/save" -r src/` returns nothing. Fail = any backend diff or a new save route.
8. **Copy accurate.** The page intro no longer claims the page never saves: `grep -n "does not save to the database" src/ui/frontend/src/pages/AdminSessionResumePaste.tsx` returns nothing, and the intro names Save to Candidate as the one action that writes. Fail = old sentence remains.

## Open questions

None.

## Proposed child tickets

#### 1: **Save to Candidate on Session Resume Paste - Hedy**

Adds the **Save to Candidate** button to the Session Resume Paste page. It saves the last parse as the selected candidate's current base resume through the existing candidate data save, with busy/disabled states, toasts, and corrected intro copy. It does not touch the backend, the parse route, or the Base Resume Content editor.
**Citations:** `patt.artifact.write-operative`, `patt.artifact.ui-consistency` (§5 save contract), `astral.standards.dry-and-focused-functions`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.in-scope-only`.
**Scope:**

* `src/ui/frontend/src/pages/AdminSessionResumePaste.tsx`: new async save handler. With `selectedId` and `lastParse` present, it PUTs `/api/candidates/<selectedId>/data` with body `{ artifacts: { resume_structure: { sections: lastParse.resume_structure.sections }, base_resume: lastParse.base_resume } }`: sections only, no `accent_color`, so the existing route replaces the candidate's sections and keeps the accent (Functional scope 3). `base_resume` (experience job array included) is sent exactly as parsed, with no client-side reshaping or filtering (Functional scope 4). The route's existing ingest/filter then keys content to the parse's enabled sections. On a non-OK response it reads the JSON `error` (falling back to `HTTP <status>`) into the inline error line and an error toast. On OK it shows a success toast. New `saving` state disables all three existing buttons plus Save while in flight (and Save is disabled while `parsing` / `opening`). New `.btn secondary` button in the existing row, after Open HTML. The intro paragraph text is modified per Functional scope 6. `lastParse` / `pasteText` local-storage behavior is unchanged.

Estimate: 1

**New patterns:** none.

**Monolith check:** Functional scope has 6 items and there is 1 child. That is intentional: all six are one button's behavior on one page file, with no backend or shared-component layer to split along.

**Scope partition check:** `AdminSessionResumePaste.tsx` → #1. The single Component scope file is claimed exactly once.

---

## Original brief

In resume paste tool, add a button to save the parsed resume as the base_resume artifact for the selected candidate.

### Comments

#### chuckles — 2026-10-01T00:33:26.756Z
AST-1908 blocked at qa-child publish — Betty needs a call on test delivery (origin/tests carries AST-1902 backend code that would break AC7; tests-clean-base marker missing). Options are in her comment on AST-1908.

#### chuckles — 2026-09-30T22:00:56.660Z
@susan

1. **Disabled sections.** Parse builds against the default section layout, not the candidate's. Saving only `base_resume` (the recommended default) keeps the candidate's titles, order and enabled flags, but silently drops parsed content for any section the candidate has disabled. The alternative is to also send the parse's `resume_structure`, which keeps all parsed content but resets the candidate's section layout to the defaults. Keep the candidate's layout (recommended), or replace it with the parse's?
2. **Overwrite confirm.** The prior base resume is retired, not deleted, but there is no UI to restore it. Should Save ask "Replace <candidate>'s base resume?" first when the candidate already has one, or save straight away?

---

_Implementation detail may live in git history on `origin/dev`._
