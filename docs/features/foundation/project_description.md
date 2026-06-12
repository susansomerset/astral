# Astral Foundation

The shared infrastructure that every Astral project sits on top of. Foundation owns the database, the AI integration, the browser automation, the configuration system, and the utility layer. It contains no business logic — it provides primitives that Roster, Gazer, Consult, Dispatcher, and the UI all compose into their own workflows.

## Role in the System

Every user-facing feature eventually bottoms out in Foundation. When Roster prefilters a company, the AI call goes through Foundation's Anthropic layer. When Gazer scrapes a job page, it uses Foundation's Playwright layer. When Consult grades a job, the result is stored through Foundation's database layer. The configuration system is the single source of truth for state machines, model pricing, task definitions, and prompt resolution — no project hardcodes these values.

Foundation's job is to be boring and reliable. If a core module needs to call Claude, it calls `do_task()` and gets back validated, schema-checked JSON. If it needs to scrape a page, it gets a browser context, navigates, and gets back clean DOM. If it needs to persist data, it calls a save function and gets back a success/failure signal. The complexity of retries, caching, prompt construction, cookie dismissal, cost tracking, and audit logging is invisible to the caller.

## What It Touches

- **Roster** uses the database layer for company state management and batch claiming, the Anthropic layer for prefilter and job page selection, and the Playwright layer for web scraping and DOM extraction.
- **Gazer** uses the Playwright layer for job page scraping and pagination, the database layer for scan audit recording and batch lifecycle, and inherits parse logic from Roster.
- **Consult** uses the Anthropic layer for job evaluation and grading, the database layer for job and candidate data, and the config system for scoring rubrics and task definitions.
- **Dispatcher** uses the database layer for task scheduling and execution ledger, and orchestrates calls into Roster, Gazer, and Consult via their core modules.
- **Interface** reads from the database layer for all UI data, and uses the Anthropic layer's preview function for prompt rendering in the admin tools.
- **Administrator** manages agents, tasks, and dispatch configuration — all persisted through Foundation's database and validated against Foundation's config.

## Design Principles

- **Config as source of truth** — State lists, model pricing, task schemas, and transition rules live in config. If it's a magic number or a hardcoded list, it belongs in Foundation's config, not in a core module.
- **Layer isolation** — Core modules import from Foundation. Foundation never imports from core. The database layer is deliberately "dumb" — it records what callers pass, with no outcome branching or business logic.
- **Universal response envelope** — Every AI call returns a `status`/`failure_note` wrapper via `BASE_SCHEMA`, so agents can signal failure cleanly and callers don't have to guess whether an empty result is a success or a problem.
- **Audit by default** — Every API call is logged to timesheets (cost) and agent_responses (full request/response). Every state change is appended to state_history. Every scan is recorded to the scan audit table. Traceability is not optional.

## Key Files

- `src/data/database.py` — all database operations
- `src/external/anthropic.py` — Claude API integration
- `src/external/playwright.py` — browser automation
- `src/utils/config.py` — configuration constants and helpers
- `src/utils/cost_calculator.py` — API cost calculation
- `src/utils/formatting.py` — prompt formatting utilities
- `src/utils/logging.py` — application logging
