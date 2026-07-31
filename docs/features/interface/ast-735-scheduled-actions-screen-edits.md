# AST-735 — Scheduled Actions Screen Edits

<!-- linear-archive: AST-735 archived 2026-07-22 -->

## Linear archive (AST-735)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-735/scheduled-actions-screen-edits  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The Scheduled Actions admin screen lists per-candidate `dispatch_task` rows — scheduling knobs, AUTO, debug, and manual run/stop. Susan needs this screen organized **by task** (always grouped like Manage Tasks), with per-group AUTO coverage visible at a glance, richer filters for operational triage, and a table layout that stays readable when **Candidate → All** is selected (candidate column, availability, last run). Bulk copy of one candidate's dispatch suite to others is **out of scope here** — Susan will use Data Management for now; the deeper dispatch model change lives in a separate Backlog epic. This ticket delivers the Scheduled Actions UX refresh once [AST-734](https://linear.app/astralcareermatch/issue/AST-734) provides shared task-group metadata.

## Functional scope

* **Task-first grouping (via AST-734):** Collapsible sections use the same group labels, section order, and within-group task order as Manage Tasks (`task_group_order`, `task_group_name`, `task_seq` from Organizing Tasks). Rows are organized around tasks, not ad hoc per-candidate layout.
* **Per-group AUTO summary:** Each collapsible section header shows AUTO-on count versus total dispatch rows in that group after active filters (e.g. `3 / 12 AUTO`).
* **Expanded filters:** On-page filters for **Candidate**, **Floor range**, **AUTO**, **Debug**, **Freq**, **Min count**, **Batch size**, and **Run counts** (max runs / run-count fields as shown on the row today). Filters combine with each other and with task-group sections.
* **Table column layout:** Include a **Candidate** column. Show **Available** count (existing eligible-entity count for the row's trigger criteria); display **zero as "—"**. **Last run** is among the rightmost columns (with availability and candidate as the other right-side operational columns Susan specified).
* **Candidate → All presentation:** When **All** candidates is selected, retain the same task grouping and task order as the single-candidate view. For each task, show that task's scheduled rows across candidates, ordered **descending by available records to run** so the busiest work surfaces first.
* **AUTO audit view:** AUTO filter (AUTO on / all) works with **Candidate → All** so Susan can scan every AUTO-enabled scheduled action across candidates for premature firing.

## Boundaries

* **Blocked by** [AST-734](https://linear.app/astralcareermatch/issue/AST-734) — do not ship until Organizing Tasks lands; grouping reads admin task metadata from that epic, not config `phase`/`seq` alone.
* **No Apply Scheduled Actions** — no bulk clone modal, no LIVE_PROMPTS multi-select copy (Susan uses Data Management until the dispatch refactor epic).
* Does not implement the **Candidate Actions** matrix tab (task rows × candidate columns × per-cell AUTO) — separate Backlog epic.
* Does not change scheduler tick logic, dispatch claim/run behavior, or `dispatch_ledger` semantics.
* Does not add, remove, or rename `task_key` values.
* No backend debug-logging requirements (admin UI + supporting admin API only).
* Must not regress Stop All, Add Task, run/stop, per-row AUTO/Dbg toggles, edit modal, thread polling, or collapsible sections (zero expanded allowed).

## Acceptance criteria

1. After AST-734, Scheduled Actions sections match Manage Tasks grouping and task order for the same catalog keys.
2. Each section header shows AUTO-on count and total rows in that group under active filters.
3. Filters for Candidate, Floor range, AUTO, Debug, Freq, Min count, Batch size, and Run counts each narrow the table; combined filters intersect correctly.
4. Table shows Candidate column; Available displays **—** when zero; Last run is in the rightmost operational column group with Candidate and Available.
5. With **Candidate → All**, tasks stay grouped and ordered as in single-candidate view; rows for the same task sort descending by available count.
6. AUTO-on filter with **Candidate → All** lists only AUTO-enabled rows across all candidates.
7. Existing run/stop, Stop All, Add Task, edit modal, and polling behavior unchanged; component tests updated for layout, filters, and All-candidate sort.

## Dependencies and blockers

* [AST-734](https://linear.app/astralcareermatch/issue/AST-734) **Organizing Tasks** — must complete first (shared task group metadata and Manage Tasks grouping).

## Open questions

None.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-735 (parent) | ftr/AST-735-scheduled-actions-screen-edits |
| AST-751 | sub/AST-735/AST-751-scheduled-actions-filters-auto-summary |

**Epic worktree:** `astral-AST-735/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | 7ba211fc-00f1-42a2-94c5-2083e70d50b8 |
| Betty | qa | 93ef49f6-690c-48e0-8997-529cdb2f52c5 |
| Radia | review | 37bcb07a-cff1-4d93-b417-895c26d9c440 |

---

## Original brief

Align this screen to group EXACTLY as Manage tasks is organized. Let each unique task group by collapsible, and provide a summary of tasks set to auto compared to the total tasks in the group.

Also, add a button at the top of the screen for "Apply Scheduled Actions…" that gives me a popup of all the candidates in LIVE_PROMPTS, and let me select one or more candidates to apply the full suite of the current candidate's scheduled actions.

Also, give me the option of setting the new copied sets to Auto=TRUE or FALSE.  Early days I am going to want them to be FALSE, but as we harden the candidate onboarding process, we may want an auto on.

I also want to see a filter for ALL jobs where "Auto"=TRUE, and make sure I can select "ALL" candidates for the view, so I can see if there's anything squirrelly firing prematurely.

I think that's enough alsos for now.

### Comments

#### chuckles — 2026-06-23T19:30:48.133Z
[refresh-ftr] blocked: CONFLICT `docs/test-bible/frontend/pages.md` merging origin/dev into origin/ftr/AST-735-scheduled-actions-screen-edits.

@Betty White — resolve bible conflict on ftr and push; Chuckles will re-run refresh-ftr + prep-uat.

— Chuckles

#### chuckles — 2026-06-23T19:27:52.449Z
[merge-child] blocked: validate-sub-log — duplicate merge-tests(AST-751) (count=2); git pull merges on sub/AST-735/AST-751-scheduled-actions-filters-auto-summary.

@Betty White — republish clean sub from product tip @ 936edfc: one merge-tests(AST-751) only; no Merge remote-tracking branch commits on sub.

— Chuckles

#### chuckles — 2026-06-18T22:59:57.601Z
@susan

Pipeline paused at **test-child** (AST-751 **Tests Ready**): headless `agent` returns usage limit on Auto and composer-2.5-fast. Set a Spend Limit or resume after cycle reset (6/24). Reassign parent to Chuckles to continue from stage 8.

— Chuckles

#### chuckles — 2026-06-18T22:11:38.918Z
@susan **AST-735 dispatch blocked:** Linear **`blockedBy` AST-734** (Organizing Tasks) — not **Review Posted** / **User Testing** yet. Run **`do-all-the-things` AST-734** first, or remove the blocker if you want parallel dispatch.

— Chuckles

#### chuckles — 2026-06-18T22:11:00.836Z
@susan

Definition blocks dispatch until **AST-734** (Organizing Tasks) completes — AST-734 is still **Todo**, not shipped. Reassign Chuckles after AST-734 lands, or comment if you want parallel dispatch with `blockedBy` AST-734.

— Chuckles

#### chuckles — 2026-06-18T21:18:51.098Z
@susan

1. When a target candidate already has a row for the same `(task_key, trigger_state)` triple, should apply **skip** that row, **replace** the existing row's settings, or **abort** the whole operation with an error?
2. When **Candidate** filter is **All**, should **Apply Scheduled Actions** use the left-nav selected candidate as the copy source, or should the button stay disabled until a single candidate is scoped on the page?

— Chuckles

#### chuckles — 2026-06-18T21:18:49.598Z
@susan

1. **AST-734 sequencing:** Block this epic until Organizing Tasks lands, or ship grouping against today's catalog `phase`/`seq` and swap to `task_group_*` in a follow-up?
2. **Apply source when Candidate is All:** Require exactly one source candidate in the modal, disable Apply until the candidate filter pins one source, or another rule?
3. **Duplicate rows on copy:** When a target already has a row for the same `(task_key, trigger_state)`, should Apply skip, replace with source settings, or abort the whole operation?
4. **"ALL jobs" filter:** Confirm you mean every dispatch row with AUTO on (any entity type), not only rows whose entity type is job.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
