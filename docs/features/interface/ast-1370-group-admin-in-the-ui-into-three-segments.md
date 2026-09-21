# AST-1370 — Group admin in the UI into three segments

<!-- linear-archive: AST-1370 archived 2026-08-31 -->

## Linear archive (AST-1370)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1370/group-admin-in-the-ui-into-three-segments  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The left-nav Admin section is one long undifferentiated list. Operators hunting day-to-day ops, agent/task admin, or tooling screens have to scan the whole pile. This epic splits that single Admin group into three clear segments so the sidebar matches how Susan already thinks about the work.

## Functional scope

* Replace the single **Admin** sidebar group with three top-level segments labeled **Operations**, **Admin**, and **Tools**, in that order after the existing non-admin groups (Jobs / Companies / Artifacts / Candidate stay as they are).
* **Operations** contains, in this order: Scheduled Actions, Execution History, Vector Feedback, Manage Email, Manage Slack, Manage Candidates.
* **Admin** contains, in this order: Manage Agents, Manage Tasks, Scheduled Queries, Agent Timesheets.
* **Tools** contains, in this order: Data Management, Agent Ad Hoc, Cost Reconciliation, Resume Paste, Cover Letter Paste (nav labels use these shorter names; destinations stay the existing admin routes for those screens).
* All three segments remain admin-only: non-admin users continue to see none of them, same as today’s single Admin group.
* Existing admin page routes and screen behavior are unchanged — this epic regroups and relabels navigation only.

## Architectural definition

* **Patterns to reuse** — `pattern.config.config-block`: `NAV_CONFIG` remains the sole source of sidebar group labels, item labels, order, and paths; the frontend keeps rendering the resolved `/api/nav_config` structure with no extra grouping logic.
* **New patterns proposed** — none. Prefer extending the existing config-driven nav + non-admin omit path over inventing a second nav taxonomy. If the current hard-coded omit of the literal group label `Admin` is replaced, the admin-only group set must live in config (not a magic list in the API layer).
* **Applicable statutes** — universal set (product change); `astral.config.config-source-of-truth` (nav structure and admin-only group membership from config); `astral.standards.no-hardcoded-sets` (do not leave a hard-coded three-label omit list in the API); `astral.layers.ui-config-driven-business-logic` (React does not invent segment membership); `astral.standards.in-scope-only` (nav regroup only); `astral.ui.naming-conventions` (snake_case paths unchanged); `astral.idioms.require-auth-on-protected-endpoints` (admin routes stay admin-gated).

## Boundaries

* Does **not** redesign admin page layouts, tables, modals, or APIs.
* Does **not** change Jobs / Companies / Artifacts / Candidate groups, visibility gates, badges/counts, expand/collapse chrome, responsive hamburger shell (AST-1286), or pinned logo/candidate chrome (AST-1369).
* Does **not** add, remove, or rename admin URL paths — only sidebar group membership and display labels for the paste items.
* Does **not** change who is an admin or how `is_admin` is resolved.
* Must not break non-admin nav: Operations and Tools must not appear for non-admins after the single Admin label is retired as the omit key.

## Acceptance criteria

* An admin user sees exactly three admin-facing sidebar groups — **Operations**, **Admin**, **Tools** — with the item lists and order in Functional scope, and no leftover single catch-all Admin group that still holds those items.
* Nav labels for the paste screens read **Resume Paste** and **Cover Letter Paste**; clicking them opens the same screens as today’s Session Resume Paste / Session Cover Letter routes.
* A non-admin user sees zero of Operations, Admin, or Tools (and still cannot open those admin routes via the existing admin route gate).
* Jobs / Companies / Artifacts / Candidate groups still resolve and render as before for the same candidate state.
* Wide and narrow left-nav shell behavior (drawer, hamburger, pinned chrome, deploy footer rules) is unchanged aside from the new group labels appearing in the scrollable nav body.

## Dependencies and blockers

none.

## Open questions

none.

## Proposed child tickets

#### 1: **Three-segment admin nav - Ada**

One vertical slice: regroup `NAV_CONFIG` into Operations / Admin / Tools with Susan’s membership, order, and paste labels; update the non-admin nav omit so all three segments stay admin-only via config (not a hard-coded API label list); leave routes, pages, and shell chrome alone. Intentionally single child — regroup and omit must ship together or Operations/Tools leak to non-admins.
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.layers.ui-config-driven-business-logic`.
**Estimate: 3**

---

## Original brief

Operations:

* Scheduled Actions
* Execution History
* Vector Feedback
* Manage Email
* Manage Slack
* Manage Candidates

Admin:

* Manage Agents
* Manage Tasks
* Scheduled Queries
* Agent Timesheets

Tools:

* Data Management
* Agent Ad Hoc
* Cost Reconciliation
* Resume Paste
* Cover Letter Paste

### Comments

#### chuckles — 2026-08-15T01:31:41.724Z
AST-1386 REVIEW — merge-child blocked; recalling Betty for missing test(AST-1386): subject after squash-style merge-tests.

---

_Implementation detail may live in git history on `origin/dev`._
