# Astral Interface

The web application layer. Interface is a React + TypeScript frontend served by a Flask API backend. It presents the candidate's job search data — companies, jobs, artifacts, profile — and provides admin tools for managing the system. Everything the user sees and interacts with flows through this project.

## Role in the System

Interface is the consumer of everything the other projects produce. Roster qualifies companies, Gazer scans them, Consult evaluates jobs and builds artifacts, Dispatcher schedules the work — and Interface is where all of that becomes visible and actionable for the user. It doesn't perform any of that work itself; it renders the results and provides controls to manage the pipeline.

## The Component Library

The frontend is built on a small set of reusable components that enforce visual and behavioral consistency across pages. Pages are thin compositions — they declare what data to fetch, which columns or fields to show, and what actions are available, then delegate rendering to the component library. A page that needs a filterable, sortable table uses `ListPage`. A page that needs a form uses `DetailsEditPage` and `FormFields`. A page that needs a detail overlay uses `Modal` with the appropriate detail component.

The component library handles layout, interaction, and styling. Individual pages should contain no CSS, no layout logic, and no widget construction — only the configuration of what to show and how to respond to user actions.

## What Belongs in the UI vs. the API

The frontend is deliberately "dumb." It renders what the API gives it and sends back what the user does. All business logic — visibility rules, state-based filtering, conditional enablement, data shaping — lives in the API layer, driven by config.

When a sidebar nav item should be hidden because the candidate hasn't reached a certain state, that decision is made in the API (resolved from `NAV_CONFIG` against the candidate's current state) and the frontend renders the resolved structure. When a job list should only show recommended jobs, the API filters by state before responding. The frontend never compares states, checks conditions, or duplicates logic that the API already owns.

This principle exists for a reason: the config system is the single source of truth for states, transitions, and business rules. If the frontend starts hardcoding state comparisons, those rules now live in two places — Python config and TypeScript components — and they will drift.

## API Layer Rules

The API layer (`src/ui/api/`) is organized as Flask Blueprints, one module per domain. For all non-admin endpoints, the API is a thin wrapper:

- It receives the HTTP request and authenticates via `@require_auth`
- It calls into core modules (Roster, Consult, Tracker, etc.) for any domain operations
- It calls into the data layer only for reads (queries, lists, lookups)
- It returns JSON responses with consistent error shapes
- It never imports from `src/external/` directly — external service access (Anthropic, Playwright) is always mediated through core

The API layer is the boundary where the layer rules are enforced. The frontend talks to the API. The API talks to core and data. Core talks to Foundation. This chain is not optional.

## Admin Pages

Admin pages (agents, tasks, dispatch, timesheets, cost reconciliation, ad-hoc tools, data management) are explicitly over-powered. The admin API module is authorized to break the normal layer rules — it may call data layer functions directly, bypass core orchestration, and perform operations that non-admin endpoints cannot.

This is a pragmatic exception: admin tools need low-level access for system management, debugging, and configuration that doesn't fit the normal domain workflow. The exception applies **only at the API layer** — admin pages in the React frontend still follow the same rule as every other page: they call the API and render the response. The frontend never calls core, data, or external directly, regardless of whether the page is admin or not.
