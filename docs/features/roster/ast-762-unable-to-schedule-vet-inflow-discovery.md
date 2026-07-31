# AST-762 — Unable to schedule 'vet_inflow_discovery'

<!-- linear-archive: AST-762 archived 2026-07-22 -->

## Linear archive (AST-762)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-762/unable-to-schedule-vet-inflow-discovery  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Susan cannot add a Scheduled Actions row for `vet_inflow_discovery`: save fails with **not schedulable**, and Add Task previews **entity type candidate** instead of **company**. She needs this roster inflow vet step schedulable as **company** dispatch (default trigger state **NEW**) so admin can configure and run it like other dispatch tasks. Vet-before-ingest is intentional — rejected discovery links are recorded on company rows so URL dedupe catches them on future scrapes.

## Functional scope

* `vet_inflow_discovery` is a valid schedulable `dispatch_task` key — Add Task save succeeds without a schedulability error.
* Dispatch defaults and Add Task modal show **entity type company** and default **trigger state NEW** (not candidate). Susan's rationale: `inflow_discovery` consumes candidate search-term data to create and update **company** records; the vet step's dispatch surface is company-scoped.
* Scheduled rows claim companies in **NEW** for vet work; dispatch wiring matches other company roster tasks.
* `inflow_discovery` ingest continues to create new company records in **NEW** — no regression to that state assignment.
* Rejected or ignored inflow discovery hits continue to be recorded on company data for dedupe on later runs.
* Existing schedulable roster inflow tasks (`inflow_discovery`, `inflow_resolve_website`) keep current behavior unless a consistency fix for this key requires a minimal shared adjustment.

## Boundaries

* Does not change vetting prompts, LLM response schemas, or ingest dedupe rules beyond what scheduling wiring requires.
* Does not rework the roster inflow company state machine beyond using **NEW** as the default claim trigger for this dispatch key (existing **WEBSITE_FOUND** / **NO_WEBSITE** paths unchanged).
* Does not add or change debug logging on inflow paths (AST-538 / AST-557 / AST-621 territory).
* Does not alter unrelated dispatch tasks, scheduler tick rate, or AUTO/Run controls outside `vet_inflow_discovery` scheduling.
* Admin **Task Prompts** agent assignment for `vet_inflow_discovery` remains a separate prerequisite for the LLM vet step — out of scope unless Susan expands.

## Acceptance criteria

1. Susan can complete Add Task for `vet_inflow_discovery` without a **not schedulable** error on save.
2. Entity type shown in Add Task and stored on the saved row is **company**; default trigger state is **NEW**.
3. Manual Run and AUTO dispatch `vet_inflow_discovery` against **NEW** companies claim the correct pool and execute vet work.
4. `inflow_discovery` ingest still creates new company records in **NEW** (existing behavior preserved).
5. Rejected discovery links still land on company records for dedupe (relevant tests stay green).
6. Regression: existing `inflow_discovery` and `inflow_resolve_website` scheduled rows still save, display, and dispatch correctly.

## Dependencies and blockers

None. Related shipped context: **AST-505** (roster inflow Phase 1 — CSE → vet → ingest pipeline), **AST-549** (`DISPATCH_SCHEDULABLE_TASK_KEYS` and `dispatch_task_admin_defaults`).

## Open questions

None.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-762 (parent) | ftr/ast-762-vet-inflow-discovery-schedulable |
| AST-774 | sub/AST-762/AST-774-vet-inflow-discovery-schedulable-company-dispatch |

**Epic worktree:** `astral-AST-762/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |

---

## Original brief

dispatch_task task_key not schedulable: 'vet_inflow_discovery'

Also, when I selected the vet_inflow_discovery in the Add Scheduled Task modal, it said the entity was "candidate", but it should be "company".

### Comments

#### chuckles — 2026-06-23T21:10:13.029Z
[merge-child] blocked: duplicate merge-tests(AST-774) on sub — count=2 (amend on tests, one merge-tests only)

@Betty White — fix sub publish log on AST-774 publish ref, then Chuckles re-runs merge-child.

— Chuckles

#### chuckles — 2026-06-23T19:59:13.642Z
@susan

1. Which company **trigger state** should be the default for **`vet_inflow_discovery`** scheduled rows and claim eligibility?

— Chuckles

#### chuckles — 2026-06-23T19:49:46.172Z
@susan

1. Should **`vet_inflow_discovery`** become its own schedulable dispatch task, or should Scheduled Actions stop offering it and point admin to **`inflow_discovery`** (CSE → vet → ingest) or **`inflow_resolve_website`** (company website resolution)?
2. If **`vet_inflow_discovery`** must be schedulable: is entity type **`company`** (per your brief) or **`candidate`** (current inflow batch scope), and which trigger state should define claim eligibility?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
