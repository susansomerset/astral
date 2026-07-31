# AST-821 — Get prefilter_company to work

<!-- linear-archive: AST-821 archived 2026-07-22 -->

## Linear archive (AST-821)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-821/get-prefilter-company-to-work  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Susan is exercising the two-phase company prefilter pipeline (homepage scrape → **HOMEPAGE_READY** → batch evaluate) delivered under **AST-700** / **AST-701** / **AST-702**. Companies sitting in **HOMEPAGE_READY** should be claimed by the schedulable **prefilter** company dispatch task and graded through the batch prefilter runner, then advance to pass/fail terminal states per existing rubric semantics. Today every claimed company logs `run_company_task: unhandled input_state=HOMEPAGE_READY` and the batch reports errors only — zero prefilter progress. This ticket restores end-to-end prefilter dispatch so roster companies can move past homepage screening.

## Functional scope

* **HOMEPAGE_READY dispatch reaches batch prefilter.** When the schedulable **prefilter** company dispatch task claims companies in **HOMEPAGE_READY**, execution must reach the batch prefilter evaluate phase — not the legacy `run_company_task` fallthrough that has no **HOMEPAGE_READY** handler.
* **Per-company outcomes persist.** Each company in a prefilter batch receives an independent outcome: grades, score, notes, and link selections persisted per today's prefilter contract; state transitions to **PREFILTER_PASSED**, **PREFILTER_FAILED**, **NO_PREFILTER_JOBLISTS**, **WEBSITE_FOUND_RETRY**, **CANNOT_READ_WEBSITE**, or legacy **TO_WATCH** / **IGNORE** paths exactly as established by **AST-507**, **AST-718**, and **AST-700** — no new routing semantics.
* **Readiness gating preserved.** Companies without usable homepage content in **company_data** are not sent to the agent; they fail or skip with the same observable behavior as today's empty-scrape / readiness path.
* **Dispatch summary reflects real progress.** A batch with eligible **HOMEPAGE_READY** companies reports passed and/or failed counts matching actual state transitions — not 100% errors with no companies advancing.
* **Debug traceability (AST-538).** When **debug=True** on a prefilter dispatch batch, Susan can trace per-company batch prefilter index headers with decode outcome and persisted state; substantive detail lines follow the standard backend debug contract.

## Boundaries

* Does **not** change the **prefilter_company** rubric, encoded output shape, or decode contract (**AST-603**, **AST-697**).
* Does **not** change **fetch_website** scrape behavior or **HOMEPAGE_READY** ingestion (**AST-701**).
* Does **not** change post-prefilter locate / parse / select flows (**AST-716**–**721**, **AST-719**) beyond ensuring companies can reach those states.
* Does **not** alter job-side dispatch or consult batching patterns.
* Does **not** add UI beyond existing roster company state and dispatch visibility.
* Must **not** reintroduce monolithic **WEBSITE_FOUND** scrape+prefilter inside **run_company_task**.

## Acceptance criteria

1. Given companies in **HOMEPAGE_READY** with persisted **homepage_text** (and **nav_links** when required for link decode), running the **prefilter** scheduled dispatch task produces no `unhandled input_state=HOMEPAGE_READY` warnings.
2. Each company in the batch transitions to an appropriate terminal or retry state (**PREFILTER_PASSED**, **PREFILTER_FAILED**, **NO_PREFILTER_JOBLISTS**, **WEBSITE_FOUND_RETRY**, **CANNOT_READ_WEBSITE**, **TO_WATCH**, or **IGNORE**) — not stuck in **HOMEPAGE_READY** with dispatch errors.
3. Prefilter grades, score, notes, and link fields persist per company matching today's prefilter semantics for inflow vs legacy paths.
4. Companies without **homepage_text** are skipped or failed via the readiness path — not sent to the agent and not counted as unhandled routing errors.
5. Dispatch batch summary shows **total_processed > 0** and **total_errors** reflecting only genuine failures — not 100% errors when eligible companies exist.
6. With **debug=True**, Susan can trace each company's prefilter evaluate step via index headers and substantive detail lines.

## Dependencies and blockers

* **AST-701** (**fetch_website** → **HOMEPAGE_READY**) — prerequisite pipeline stage; Susan's repro assumes companies are already **HOMEPAGE_READY**.
* **AST-702** / **AST-700** (batch prefilter pipeline and consult routing) — architectural baseline; this ticket closes the UAT gap where dispatch does not reach the batch runner.
* **AST-718** (post-prefilter PJL routing) — sibling in User Testing; defines expected **PREFILTER_PASSED** / **NO_PREFILTER_JOBLISTS** behavior once prefilter runs; not a blocker to fixing routing.
* **AST-707** / **AST-708** (embedded RC grade hydration) — already addressed on dev; reopen only if hydration failures still block AC 2–3 after routing is fixed.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-821 (parent) | ftr/AST-821-get-prefilter-company-to-work |
| AST-823 | sub/AST-821/ast-823-homepage-ready-prefilter-consult-routing |
| AST-825 | sub/AST-821/ast-825-uat-prefilter-dispatch-task-group-metadata |

**Epic worktree:** `astral-AST-821/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Hedy | engineer | 85836d03-a849-4b54-a4da-91860ab4bd5f |
| Katherine | engineer | 264283e8-8e1a-4337-b38a-f0b22b0d4e14 |
| Betty | qa | b2f89820-8803-447a-9ace-676f40db282f |
| Radia | review | 3701d511-af3c-4e83-991c-e07992361780 |

---

## Original brief

When I run now, for "HOMEPAGE_READY", I get 100% errors like this:

```
6/25/26, 8:15:33 PM	WARNING	src.core.roster	run_company_task: unhandled input_state=HOMEPAGE_READY for stripe
6/25/26, 8:15:33 PM	WARNING	src.core.roster	run_company_task: unhandled input_state=HOMEPAGE_READY for stripe
6/25/26, 8:15:33 PM	WARNING	src.core.roster	run_company_task: unhandled input_state=HOMEPAGE_READY for stripe
6/25/26, 8:15:33 PM	WARNING	src.core.roster	run_company_task: unhandled input_state=HOMEPAGE_READY for stripe
```

### Comments

#### chuckles — 2026-06-26T18:24:07.235Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-825** | prefilter dispatch task missing task_group metadata in Scheduled Actions JSON |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-825** — _prefilter dispatch task missing task_group metadata in Scheduled Actions JSON_
- **Issue reported:** In Scheduled Actions / dispatch admin JSON (`GET /api/admin/dispatch_tasks/task_keys`), the schedulable `prefilter` task key appears without `task_group_order`, `task_group_name`, `task_seq`, and related grouping metadata (empty or missing vs sibling company roster keys). Susan s
- **Should now:** `prefilter` in `task_keys` (and any dispatch-row JSON that surfaces grouping) carries the same **C. Company Roster** grouping metadata as other company-roster dispatch keys, with sequence ordering **after** `fetch_website` **and before** `fetch_job_pages` in the Company Roster se
- **Quick check (this fix only):**
  1. Open admin **Scheduled Actions** (or `GET /api/admin/dispatch_tasks/task_keys`) on staging after AST-821 ship.
  2. Inspect the `prefilter` entry in the JSON response.
  3. Observe missing/empty `task_group_*` fields while `fetch_website` and `fetch_job_pages` show **C. Company Roster** grouping and correct relative order.
  4. Confirm `prefilter` row does not appear between `fetch_website` and `fetch_job_pages` in the Company Roster group.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### susan — 2026-06-26T18:13:13.926Z
For some reason, prefilter is not properly populated in the json data, it appears without the task_group\_\* settings.  It should fall between fetch_website and fetch_job_pages in the sequencing in the Company Roster group.

---

_Implementation detail may live in git history on `origin/dev`._
