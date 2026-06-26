# AST-648 — Remove "Board Searches" and related references

<!-- linear-archive: AST-648 archived 2026-06-23 -->

## Linear archive (AST-648)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-648/remove-board-searches-and-related-references  
**Status at archive:** Done  
**Project:** Astral Boards  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Susan is cancelling the Astral Boards product initiative. The boards channel was built out on `dev` (saved searches, periodic `gaze_board`, ingest fork), but it will not ship as a candidate-facing capability for now. This epic removes **user-visible UI** for board searches so the app no longer advertises or exposes board management, while leaving backend tables, APIs, dispatch, and config **in place** for a possible future revival or a later full decommission pass.

## Functional scope

* **Candidate navigation:** Remove the **Board Searches** entry from the candidate sidebar so it no longer appears for any candidate state.
* **Board Searches screen:** Remove the candidate **Board Searches** management page from the routed application — users cannot open CRUD for saved board searches from the UI (create, edit, pause/resume, delete, craft/generate flows).
* **Residue copy:** Remove or retire any remaining **frontend** user-facing strings, headings, or empty states that refer to board searches or the boards channel as a product feature (limited to surfaces that would otherwise remain reachable after the nav and page removal).

## Boundaries

* **No backend rip-out:** Do not drop `board_search` tables, remove `/api/boards` routes, delete `BOARD_CONFIG`, disable `gaze_board` dispatch, or change ingest/tracker behavior for board-sourced jobs.
* **No data migration:** Existing `board_search` rows and board-sourced jobs remain in the database unchanged.
* **No scheduler changes** unless Susan explicitly approves hiding admin dispatch UI (see open questions).
* **No changes** to company-centric ingest, roster, consult, artifacts, or unrelated candidate pages.
* **Tests:** Updating or removing frontend/component tests that assert the Board Searches page or nav is expected as part of delivery; bible updates follow normal Betty handoff — not pre-specified here.

Per Code Rules §2.1, navigation visibility is config-driven via `NAV_CONFIG` and served through `/api/nav_config`; removing the feature from the UI must honor that pattern (not hard-coded sidebar exceptions).

## Acceptance criteria

1. With a logged-in user and any eligible candidate selected, the sidebar **does not** show **Board Searches**.
2. Navigating to the former board-searches URL **does not** render the Board Searches management UI (no list, no create/edit modal, no board picker).
3. All other candidate, company, artifacts, and admin pages load and behave as before this change.
4. Component test suite passes after board-search UI tests are updated or removed to match the new product surface.

## Dependencies and blockers

none.

## Open questions

1. Should **Admin → Scheduled Actions** continue to expose the `gaze_board` task (label/description as shown today), or should admin UI references to board dispatch be hidden/disabled as part of this epic?
   1. No.
2. For a bookmarked `/candidate/board_searches` URL, is a generic not-found acceptable, or should users be redirected to a specific candidate page (e.g. Profile)?
   1. Not necessary.

---

## Original brief

We are cancelling the Boards project, but we don't need a full rip-out at the moment.  Just remove UI references to it.

### Comments

#### chuckles — 2026-06-14T22:17:42.945Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-648 (parent) | ftr/ast-648-remove-board-searches-and-related-references |
| AST-649 | sub/AST-648/ast-649-remove-candidate-and-admin-board-search-ui |

**Epic worktree:** `astral-AST-648/` — one active sub checked out at a time.

**Parent:** AST-648

— Chuckles

#### chuckles — 2026-06-14T22:12:04.048Z
@susan Open questions on the Description — numbered list only:

1. Should **Admin → Scheduled Actions** continue to expose **`gaze_board`**, or hide/disable board dispatch in admin UI too?
2. Bookmarked **`/candidate/board_searches`**: generic not-found OK, or redirect somewhere specific?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
