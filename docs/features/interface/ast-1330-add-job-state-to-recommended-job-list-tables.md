# AST-1330 — add Job State to Recommended Job list tables

<!-- linear-archive: AST-1330 archived 2026-08-19 -->

## Linear archive (AST-1330)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1330/add-job-state-to-recommended-job-list-tables  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / 2  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

On the Recommended page, Meteorite jobs are lumped into one section regardless of pipeline progress, so Susan cannot tell which jobs already have artifact work requested, which are ready, and which she has not touched. Surfacing each job’s current state on the list rows restores that visibility without changing how sections are built.

## Functional scope

* Every Recommended list table row shows the job’s current state as the stored job-state string (for example `BUILD_ARTIFACTS`), using the state value already present on each list row.
* The State column is sortable within each section, consistent with peer sortable columns on the same tables (title, company, scores, Updated).

## Architectural definition

* **Patterns to reuse** — `no established pattern applies` for Recommended list column layout (no cataloged UI list-column pattern). Job state identity remains the config `JOB_STATES` registry string already carried on list rows; do not invent a parallel display enum. Related catalog context only: `pattern.state.entity-state-transitions` (state strings are registry keys — display them, do not redefine transitions).
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.standards.in-scope-only` (Recommended list tables only); `astral.standards.no-hardcoded-sets` (no inline state allowlists or label maps); `astral.config.config-source-of-truth` (display the stored `JOB_STATES` key, not a one-off UI vocabulary); `astral.ui.naming-conventions` (Recommended page / jobs list surface naming).

## Boundaries

* Does **not** regroup the Meteorites section by state, split sections, or change section membership rules.
* Does **not** change Skipped, In Review, or other job list pages (even where some already show state).
* Does **not** change the Recommended Job Modal, row actions, artifact generation, or job state transitions.
* Does **not** invent human-readable state labels or a new label map unless already provided by existing state-UI manifest config for this purpose — Susan’s example is the raw key.
* Does **not** change list API contracts beyond using fields already returned for Recommended rows.

## Acceptance criteria

1. On the Recommended page, every visible list section’s table includes a State column whose cell for each row is that job’s current state string (e.g. `BUILD_ARTIFACTS`).
2. Within the Meteorites section, rows with different states show different State cell values so in-progress vs ready vs untouched are distinguishable without opening a job.
3. Clicking the State column header sorts that section’s rows by state (toggle asc/desc like other sortable headers on the page).
4. Non-Meteorite Recommended sections still group as today; they also show State on each row (same string as the job’s state).
5. Opening a job report, skipping, and other existing row actions behave as before.

## Dependencies and blockers

none

## Open questions

none

## Proposed child tickets

#### 1: **Recommended list State column - Katherine**

Add a sortable State column to every Recommended list table that displays each row’s existing job state string. Does not own section regrouping, modal work, or other job list pages.
**Citations:** `astral.standards.in-scope-only`; `astral.standards.no-hardcoded-sets`; `astral.config.config-source-of-truth`; `astral.ui.naming-conventions`.
**Estimate:** 2

---

## Original brief

The Recommended page shows all of the Meteorites in one section, regardless of their different states.  I can't tell which jobs I have already requested artifacts for, which ones are ready, and which ones I haven't looked at yet.

Just add the job's current state (e.g. "BUILD_ARTIFACTS") to the rows so I can see where things are in progress/ready.

### Comments

#### chuckles — 2026-08-12T13:39:01.322Z
AST-1331 STALE(dev+1109) — @Katherine Johnson refresh sub (merge origin/dev + origin/ftr/AST-1330-add-job-state-to-recommended-job-list-tables) then republish before resolve.

#### chuckles — 2026-08-12T13:38:44.530Z
AST-1331 REVIEW — Radia: sibling AST-1334 test/bible on AST-1331 publish ref; Betty re-pin merge-tests.

---

_Implementation detail may live in git history on `origin/dev`._
