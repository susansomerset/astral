# AST-203 — Component Library

<!-- linear-archive: AST-203 archived 2026-06-03 -->

## Linear archive (AST-203)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-203/component-library  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** susan  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Build the reusable React + TypeScript UI component library that all Interface screens are assembled from. This is the foundation layer — all screen implementations depend on these components, so this feature must be completed first.

**Stack:** React + TypeScript. Built output served as static files from Flask. Hosted on Railway (single service: Flask API + React frontend + SQLite on persistent volume).

**Components to build:**

**ListPage:** Sortable, filterable table component with checkbox column for bulk actions. Supports configurable columns, sort direction toggle, filter/search input, and a bulk action toolbar that appears when one or more rows are selected. Used by: Companies Watch List, Ignored, Watch History, Gazer Issues, Jobs screens.

**Modal:** Single-record edit overlay. Accepts a form schema and renders appropriate inputs (text, textarea, select, toggle). Cancel and Save actions. Dismissable by Escape key or backdrop click. Used by: all List Page row-level edits.

**DetailsEditPage:** Full-page single-record editor for rich, multi-section content. Supports labeled sections, long-form text areas, and page-level Save/Cancel. Not a modal — renders at its own route. Used by: Candidate Profile.

**NavigationShell:** Sidebar layout with grouped nav links (Jobs, Companies, Candidate, Admin). Active route highlighting. Router outlet for page content. Top-level app wrapper that all pages render inside.

**Acceptance Criteria:**

* All four components built and typed in TypeScript
* Components are generic and accept props/config — no hardcoded screen-specific content
* NavigationShell renders with all nav groups and links from the Interface design (Jobs: Meteors, New, Skipped, Applied, Responded; Companies: Watch List, Gazer Issues, Ignored, Watch History; Candidate: Profile, Strengths, Goals, Deal Breakers, Experience, Base Resume; Admin: Manage Candidates, Agent Prompts, Task Prompts, Rubrics, Analysis Instructions, Resume Framework)
* React Router configured with placeholder routes for all nav destinations
* Flask serves the built React app at root; API routes live under /api/
* App loads and navigates without errors
* Railway deployment config in place (Procfile or railway.toml): web service + persistent volume mount for SQLite

# Component Library

**Scope:** Set up the React + TypeScript project with Vite, configure Flask to serve the built output, and prepare Railway deployment.

* Vite + React + TypeScript project setup
* Flask app serves built React output at root, API routes under /api/
* Flask catch-all route serves index.html for non-API paths (client-side routing)
* Railway deployment config: Procfile or railway.toml, persistent volume mount for SQLite
* Dev workflow: Vite dev server proxies /api/ to Flask during development

**Layer:** ui/ (new React project), Flask API server

## Metadata

* URL: [AST-209](https://linear.app/astralcareermatch/issue/AST-209/project-scaffolding-flask-integration-and-railway-deployment)
* Identifier: [AST-209](https://linear.app/astralcareermatch/issue/AST-209/project-scaffolding-flask-integration-and-railway-deployment)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Interface](https://linear.app/astralcareermatch/project/astral-interface-90277084a555). The user interface to combine all the features of Astral for independent candidate use.
* Created: 2026-02-28T15:05:02.064Z
* Updated: 2026-02-28T18:24:01.198Z

---

# Component Library

**Scope:** Build the NavigationShell layout component — sidebar with grouped nav sections and a main content area.

* Sidebar layout with 4 grouped nav sections: Jobs, Companies, Candidate, Admin
* Data-driven nav config: nav groups, links, and visibility driven by a config object (not hardcoded). Must support runtime flexibility for state-machine-dependent menu items (e.g., nav items that appear/hide based on candidate, company, or job state)
* Active route highlighting via React Router NavLink
* Router Outlet for page content area
* Top-level app wrapper (all pages render inside NavigationShell)

**Nav sections:**

* Jobs: Meteors, New, Skipped, Applied, Responded
* Companies: Watch List, Gazer Issues, Ignored, Watch History
* Candidate: Profile, Strengths, Goals, Deal Breakers, Experience, Base Resume
* Admin: Scheduled Actions, Performance Monitor, Agent Timesheets, Manage Candidates, Agent Prompts, Task Prompts, Consult Rubrics, Analysis Instructions, Resume Framework

**Layer:** ui/src/components/

## Metadata

* URL: [AST-210](https://linear.app/astralcareermatch/issue/AST-210/navigationshell-component)
* Identifier: [AST-210](https://linear.app/astralcareermatch/issue/AST-210/navigationshell-component)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Interface](https://linear.app/astralcareermatch/project/astral-interface-90277084a555). The user interface to combine all the features of Astral for independent candidate use.
* Created: 2026-02-28T15:05:03.226Z
* Updated: 2026-02-28T18:24:01.242Z

---

# Component Library

**Scope:** Build the generic ListPage component — a sortable, filterable table with checkbox selection and bulk actions.

* Sortable columns with direction toggle (click header to sort)
* Filter/search text input
* Checkbox column for row selection
* Bulk action toolbar (appears when 1+ rows selected, actions passed via props)
* Column config via props (no hardcoded screen content)
* Row click handler prop for opening Modal or navigating

**Layer:** ui/src/components/

## Metadata

* URL: [AST-211](https://linear.app/astralcareermatch/issue/AST-211/listpage-component)
* Identifier: [AST-211](https://linear.app/astralcareermatch/issue/AST-211/listpage-component)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Interface](https://linear.app/astralcareermatch/project/astral-interface-90277084a555). The user interface to combine all the features of Astral for independent candidate use.
* Created: 2026-02-28T15:05:04.242Z
* Updated: 2026-02-28T18:24:01.266Z

---

# Component Library

**Scope:** Build the generic Modal component — a single-record edit overlay dialog.

* Overlay dialog accepting a form schema prop
* Renders typed inputs: text, textarea, select, toggle
* Cancel and Save action buttons
* Dismissable via Escape key or backdrop click
* Fully generic — form fields driven by schema config

**Layer:** ui/src/components/

## Metadata

* URL: [AST-212](https://linear.app/astralcareermatch/issue/AST-212/modal-component)
* Identifier: [AST-212](https://linear.app/astralcareermatch/issue/AST-212/modal-component)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Interface](https://linear.app/astralcareermatch/project/astral-interface-90277084a555). The user interface to combine all the features of Astral for independent candidate use.
* Created: 2026-02-28T15:05:05.189Z
* Updated: 2026-02-28T18:24:01.297Z

---

# Component Library

**Scope:** Build the DetailsEditPage component — a full-page single-record editor.

* Full-page single-record editor (not a modal, renders at its own route)
* Labeled sections with long-form text areas
* Page-level Save and Cancel buttons
* Section config via props

**Layer:** ui/src/components/

## Metadata

* URL: [AST-213](https://linear.app/astralcareermatch/issue/AST-213/detailseditpage-component)
* Identifier: [AST-213](https://linear.app/astralcareermatch/issue/AST-213/detailseditpage-component)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Interface](https://linear.app/astralcareermatch/project/astral-interface-90277084a555). The user interface to combine all the features of Astral for independent candidate use.
* Created: 2026-02-28T15:05:06.408Z
* Updated: 2026-02-28T18:24:01.322Z

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
