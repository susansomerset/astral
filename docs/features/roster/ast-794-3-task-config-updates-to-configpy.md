# AST-794 — 3 task_config updates to config.py

<!-- linear-archive: AST-794 archived 2026-07-22 -->

## Linear archive (AST-794)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-794/3-task-config-updates-to-configpy  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Repo-owned `agent_task.json` ([AST-782](https://linear.app/astralcareermatch/issue/AST-782/startup-repo-json-upsert-and-export-create-repo-json-files-for-agent)) already catalogs **fetch_jd** and omits **validate_title** and **gaze_board**, but runtime config and dispatch still expose **scrape_jd** and **validate_title** as schedulable task keys. That split confuses Scheduled Actions, Manage Tasks, and operator troubleshooting — Susan sees one name in repo JSON and another in the live pipeline. This epic aligns the config task-key registry with the repo catalog and finishes decommissioning board-era and pre-qualify task keys so one string flows from config through scheduling to execution.

## Functional scope

* **Rename scrape_jd → fetch_jd:** The JD scrape hop at job state **PASSED_JOBLIST** uses task key **fetch_jd** everywhere task keys are authoritative — config schedulable catalogs, dispatch admin defaults, dispatch row validation, runtime routing, Execution History, and timesheet attribution. Behavior of the hop (Playwright JD fetch, pass/fail states, error substates) is unchanged; only the key string and operator-facing labels align with repo **agent_task.json** ("Fetch Job Description").
* **Retire gaze_board:** **gaze_board** is fully removed from schedulable task catalogs and admin surfaces. Any surviving **dispatch_task** rows or stale references are migrated or purged idempotently. No new **gaze_board** content, seed paths, or operator docs (boards sunset — **AST-745** / **AST-765** / **AST-766**).
* **Retire validate_title as a task:** **validate_title** is not a schedulable task key, Manage Tasks catalog entry, or dispatch admin choice. Mechanical title-regex screening for **NEW** jobs (profile **title_patterns** → **VALID_TITLE** / **INVALID_TITLE**) continues as an inline pre-step before **qualify_job_listings** runs — not a separately scheduled hop Susan manages. **qualify_job_listings** remains the first AI-backed job-review task in the operator catalog.
* **Data migration:** Ship includes idempotent DB updates: existing **dispatch_task** rows stored as **scrape_jd** → **fetch_jd**; rows for **validate_title** and **gaze_board** removed or migrated per cutover rules under the same **(candidate_id, task_key, trigger_state)** constraint.
* **Repo JSON consistency:** Checked-in **data/admin/agent_task.json** stays authoritative; config schedulable keys match it after cutover (**fetch_jd** present; **validate_title** and **gaze_board** absent).

## Boundaries

* Does **not** rename job states (**VALID_TITLE**, **JD_READY**, **PASSED_JOBLIST**, etc.) or change grading prompts, rubrics, pass thresholds, or **pass_threshold** vs **score_floor** semantics.
* Does **not** revive Astral Boards, **board_search**, or **gaze_board** execution paths.
* Does **not** remove mechanical title screening logic — only retires **validate_title** as a standalone schedulable/admin task.
* Does **not** reorganize **TASK_CONFIG** file layout or grouping metadata (**AST-734** / [AST-572](https://linear.app/astralcareermatch/issue/AST-572/organization-of-tasks-and-dispatch-task-keys) scope).
* Must **not** reintroduce dispatch-only alias keys for these hops (**AST-736** alignment preserved for **grade\_*** and other catalog keys).

Per **ASTRAL_CODE_RULES** §2.1, schedulable keys remain config-driven; post-cutover admin saves using retired keys (**scrape_jd**, **validate_title**, **gaze_board**) fail validation with a clear error.

## Acceptance criteria

1. Susan can create and run a **fetch_jd** dispatch row at **PASSED_JOBLIST**; admin APIs and Scheduled Actions do not offer **scrape_jd** as a schedulable key.
2. After migration, zero **dispatch_task** rows have **task_key** in **{scrape_jd, validate_title, gaze_board}**; equivalent **fetch_jd** rows preserve scheduling fields (**freq_hrs**, **batch_size**, **debug**, **AUTO**, etc.).
3. **Manage Tasks** and repo **agent_task.json** list **fetch_jd** and do not list **validate_title** or **gaze_board**.
4. **NEW** jobs still reach **qualify_job_listings**: title-regex screening runs without a separate **validate_title** dispatch row; jobs with matching patterns advance to **VALID_TITLE** (or permissive pass when no patterns) before the qualify AI hop executes.
5. **fetch_jd** manual Run and AUTO dispatch behave as today's **scrape_jd** hop (JD text persisted, **JD_READY** / scrape-fail substates unchanged).
6. Admin **GET /api/admin/dispatch_tasks/task_keys** and Scheduled Actions grouping show **fetch_jd** with correct metadata; retired keys are rejected on save.

## Dependencies and blockers

* **Done prerequisites:** [AST-782](https://linear.app/astralcareermatch/issue/AST-782/startup-repo-json-upsert-and-export-create-repo-json-files-for-agent) (repo **agent_task.json** uses **fetch_jd**), **AST-745** / **AST-765** / **AST-766** (**gaze_board** and boards decommission).
* **Related, not blocking:** [AST-785](https://linear.app/astralcareermatch/issue/AST-785/uat-dispatch-task-rows-missing-from-scheduled-actions-ui-vet-inflow) (Scheduled Actions visibility — separate UAT fix).
* none otherwise.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| [AST-794](https://linear.app/astralcareermatch/issue/AST-794/3-task-config-updates-to-configpy) (parent) | ftr/ast-794-task-config-key-cutover |
| [AST-796](https://linear.app/astralcareermatch/issue/AST-796/config-schedulable-key-cutover-fetch-jd-and-retire-keys-3-task-config) | sub/AST-794/ast-796-config-schedulable-key-cutover-fetch-jd-retire-keys |
| [AST-797](https://linear.app/astralcareermatch/issue/AST-797/runtime-routing-db-migration-and-inline-validate-title-3-task-config) | sub/AST-794/ast-797-runtime-routing-db-migration-inline-validate-title |

**Epic worktree:** `astral-AST-794/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |

---

## Original brief

1. Please rename "scrape_jd" to "fetch_jd"
2. Completely remove the task for gaze_board
3. Remove validate_title as a task, please.
   | Betty | qa | 6325d71a-1a02-48e3-a57a-cb96d184404e |
   | Radia | review | f2756497-fd1b-4b0d-b777-8e19470fb5e4 |
   | Hedy | engineer | 5b2ae6c6-0115-4c36-845a-da8b48f0a322 |

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
