# AST-1406 — Page refreshes and modals are closed (lost!)

<!-- linear-archive: AST-1406 archived 2026-09-09 -->

## Linear archive (AST-1406)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1406/page-refreshes-and-modals-are-closed-lost  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

While the local server is up, operators lose in-progress overlay work when the screen remounts, and they still have to refresh to see mutations and live status. That is not an acceptable product for a long-running SPA: a ten-minute edit in a modal must survive background session and data refresh, and toggles (Scheduled Actions AUTO/Dbg and the same class of controls elsewhere) must show their new state without an F5. This epic makes the running app stay live in place.

## Functional scope

The authenticated app stays mounted across background session revalidation. Extending or re-reading the session does not replace the working tree with a loading placeholder, close an overlay, or discard in-progress edits.

Operator mutations take effect in the current view. Toggles, run/stop, and other in-row actions show the new state without a browser refresh and without swapping the page for a loading gate.

Background status polls merge into the current view. They do not close overlays, reset scroll or section expand, or wipe draft fields the operator is editing.

Scheduled Actions is the named exemplar: AUTO, Dbg, Run/Stop, Avail, and last-run update in place on the same cadence the page already uses for thread status, without requiring a refresh.

## Architectural definition

* **Patterns to reuse** — `pattern.ui.admin-endpoint`: admin reads and mutators stay authenticated thin API; this epic does not invent new business rules in React. `pattern.ui.shared-button-roles`: in-row AUTO/Dbg/Run/Stop keep the existing labeled-button roles. `pattern.ui.dirty-leave-save-then-navigate` (proposed): do not overload it — that pattern is in-app route leave with Save, not overlay survival or live list refresh.
* **New patterns proposed** — `pattern.ui.in-place-live-refresh`: first paint may show a loading state; every later refetch (poll, post-mutation, session revalidation) merges into the current view without unmounting the page or overlays. Overlays own their draft independently of list refresh underneath. Existing silent refresh on Performance Monitor is the product shape to generalize. Flag for Archie before other work treats the id as catalog law.
* **Applicable statutes** — universal set (`orch.git.*`, `orch.pipeline.*`, `orch.roles.*`). Product: `astral.ui.frontend-file-placement`, `astral.ui.naming-conventions`, `astral.standards.dry-and-focused-functions` (one live-refresh shape, not a copy per page), `astral.standards.in-scope-only`, `astral.standards.names-not-ticket-ids`, `astral.standards.public-then-helpers`, `astral.layers.ui-config-driven-business-logic` (live update is presentation; eligibility stays API/config), `astral.idioms.require-auth-on-protected-endpoints`, `astral.standards.no-hardcoded-sets` if any new cadence constants are introduced. Frontend-only — no backend `debug=` contract on this epic.

## Boundaries

Does not disable Vite live-reload when frontend source files actually change (that is a rebuild, not idle-server refresh).

Does not add a websocket or server-push channel. Existing poll intervals stay; they must merge silently.

Does not persist overlay drafts across intentional close, route leave, log-off, or a hard browser reload the operator chooses. Modal discard-on-close and dirty-leave (AST-1315) stay as they are.

Does not change Stytch session duration or activity-extension cadence (AST-1372). Those values stay; the SPA must not tear down the tree when they fire.

Does not change log-off, which may reload to clear the session.

Does not change the local API server’s existing behavior of not restarting itself when Python files change on disk.

Does not change dispatch, scheduler, or task-run semantics — only how the UI shows them.

## Acceptance criteria

1. With the server running, an overlay open for longer than the activity-extension cadence still has its in-progress edits after that cadence fires. The page is not replaced by a loading placeholder.
2. Toggling AUTO or Dbg on Scheduled Actions shows the new on/off state in the same row without an F5 and without a full-page loading replacement.
3. After a Scheduled Actions Run completes, Avail and last-run update in place without an F5.
4. A background poll that fires while an overlay is open does not close the overlay or wipe its draft.
5. Manage Tasks (the overlay in this ticket’s log) and other authenticated list surfaces that currently replace themselves with a loading state on refetch after first paint follow the same in-place rule.
6. Log-off still clears the session. Vite still reloads when frontend source files change.

## Dependencies and blockers

none. Adjacent: AST-1372 (session extend) is already shipped — this epic must not regress it. AST-1315 dirty-leave is a different problem and is not a blocker.

## Open questions

none

## Proposed child tickets

#### 1!!!: **Keep the SPA mounted across session revalidation - Ada**

When the client session is extended or identity is re-read in the background, the authenticated tree stays mounted. Loading placeholders are only for first session resolution, not for later revalidation. Open overlays and in-progress edits survive the activity-extension cadence. Does not own list/toggle live update (that is #2 and #3). Does not change session duration or cadence values.
**Citations:** `pattern.ui.in-place-live-refresh` (proposed; this child is the session-shell half), `astral.idioms.require-auth-on-protected-endpoints`, `astral.ui.frontend-file-placement`, `astral.standards.dry-and-focused-functions`.
**Estimate: 3**

#### 2!: **In-place live updates on Scheduled Actions - Hedy**

After #1. Land proposed `pattern.ui.in-place-live-refresh` for Archie, using Performance Monitor’s silent refresh as the shape. Scheduled Actions AUTO, Dbg, Run/Stop, Avail, and last-run update in the current view without an F5 and without a loading-gate remount. An open add/edit overlay keeps its draft if the list refreshes underneath. Does not sweep other pages (that is #3).
**Citations:** `pattern.ui.in-place-live-refresh` (this child introduces it), `pattern.ui.admin-endpoint`, `pattern.ui.shared-button-roles`, `astral.standards.dry-and-focused-functions`, `astral.layers.ui-config-driven-business-logic`.
**Estimate: 5**

#### 3: **Apply silent refetch on remaining loading-gate surfaces - Katherine**

After #2. Same in-place rule on the other authenticated surfaces that currently replace themselves with a loading state on refetch after first paint, including Manage Tasks (the overlay in this ticket’s log). Operator Cancel/reset that currently reloads the browser (when there is no snapshot to restore) becomes an in-place reset instead. Does not invent a push channel. Does not retouch Scheduled Actions except to consume the shared shape.
**Citations:** `pattern.ui.in-place-live-refresh`, `astral.standards.dry-and-focused-functions`, `astral.standards.in-scope-only`, `astral.ui.frontend-file-placement`, `astral.ui.naming-conventions`.
**Estimate: 5**

**New patterns:** Child #2 authors `pattern.ui.in-place-live-refresh` (proposed). Child #1 and #3 reuse it. Archie approves the id before it is treated as catalog law.

**Monolith check:** Functional scope has 4 capabilities; 3 children. Split is intentional: session-shell unmount is a different slice from Scheduled Actions live update, which is the exemplar for the remaining loading-gate sweep.

---

## Original brief

```
127.0.0.1 - - [16/Aug/2026 20:04:48] "GET /api/admin/tasks?candidate_id=somerset HTTP/1.1" 200 -
Token {$VISIBLE_JD} resolved to empty (job_context, task=anticipate_scan)
Token {$ANALYSIS_JD} resolved to empty (job_context, task=anticipate_scan)
Token {$ANALYSIS_DO} resolved to empty (job_context, task=anticipate_scan)
Token {$ANALYSIS_GET} resolved to empty (job_context, task=anticipate_scan)
Token {$ANALYSIS_LIKE} resolved to empty (job_context, task=anticipate_scan)
127.0.0.1 - - [16/Aug/2026 20:04:48] "GET /api/admin/tasks?candidate_id=somerset HTTP/1.1" 200 -
127.0.0.1 - - [16/Aug/2026 20:04:58] "GET /api/admin/tasks/craft_like_rubric HTTP/1.1" 200 -
127.0.0.1 - - [16/Aug/2026 20:05:17] "GET /api/deploy_status HTTP/1.1" 200 -
127.0.0.1 - - [16/Aug/2026 20:05:17] "GET /api/deploy_status HTTP/1.1" 200 -
127.0.0.1 - - [16/Aug/2026 20:05:17] "GET /api/nav_config?candidate_id=somerset HTTP/1.1" 200 -
127.0.0.1 - - [16/Aug/2026 20:05:17] "GET /api/nav_config?candidate_id=somerset HTTP/1.1" 2
```

I just spent 10 minutes in a modal window on local, and the screen refreshed and I lost all my changes.  Please stop letting this happen.

STOP requiring a screen refresh for ANY reason when the server is running.  This includes toggling buttons on the scheduled_action page and other places.  We should not have to refresh the page to get realtime updates.

### Comments

#### chuckles — 2026-08-17T06:43:26.139Z
AST-1410 REVIEW — Radia needs discuss on sibling scope on publish ref.

#### chuckles — 2026-08-17T05:38:00.927Z
AST-1409 REVIEW — Radia: AST-1411 test commit on this child publish ref.

---

_Implementation detail may live in git history on `origin/dev`._
