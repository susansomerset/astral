# AST-736 — Task keys vs. dispatch task keys

<!-- linear-archive: AST-736 archived 2026-06-23 -->

## Linear archive (AST-736)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-736/task-keys-vs-dispatch-task-keys  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-572

### Description

## Purpose

Susan schedules and troubleshoots pipeline work through `dispatch_task.task_key`. Since **AST-534**, the row's `task_key` already drives execution — but a consult/grade alias layer still gives graded consult steps a second dispatch-only name (`consult_do`, `consult_get`, `consult_like`) while `TASK_CONFIG` uses `grade_do`, `grade_get`, and `grade_like`. That split made sense when consult routing was inferred from `trigger_state`; it now creates confusion (e.g. `consult_do` rows bucketed against `grade_do` phase metadata in Scheduled Actions) while roster already schedules distinct hops under their real task keys at shared `trigger_state`. **TASK_CONFIG keys are the fulcrum between frontend and backend** — this epic retires dispatch-only aliases so Susan sees one task key from config through scheduling to runtime, with no parallel vocabulary where a TASK_CONFIG entry already exists.

## Functional scope

* **Universal task-key alignment:** For every schedulable task that runs through `TASK_CONFIG`, the `dispatch_task.task_key`, admin create/edit, schedulable-key validation, and AUTO/manual Run use the same string as the `TASK_CONFIG` index — not a dispatch-only alias. Primary work: replace `consult_do`, `consult_get`, and `consult_like` with `grade_do`, `grade_get`, and `grade_like`.
* **Config alignment:** Remove or collapse the consult→grade dispatch alias map (`resolve_dispatch_task_config_key` indirection for those three keys) so schedulable defaults, entity/trigger rules, batch-call-mode grouping, and scored-trigger helpers key off the same `task_key` strings as `TASK_CONFIG` and Manage Tasks. Confirm no other alias map is required to satisfy universal alignment.
* **Admin surfaces:** Scheduled Actions, dispatch task modals, and `GET /api/admin/dispatch_tasks/task_keys` expose phase, sequence, and labels for `grade_*` keys directly — no resolve step for a parallel dispatch-only name.
* **Runtime honesty:** Dispatcher, consult entry, Execution History per-hop Task column, and timesheet/task attribution record `grade_*` for those three steps (first hop and batch paths).
* **Data migration:** Ship includes an automatic, idempotent DB rename of existing per-candidate rows stored as `consult_*` → `grade_*` under the same `(candidate_id, task_key, trigger_state)` triple-unique constraint, including `_RETRY` companion `trigger_state` rows where present.
* **Hard cutover:** After ship, no runtime or admin path accepts retired `consult_*` keys as input — single-release rename, no read-time compat layer.
* **Documentation:** Product rules and operator docs describe one task key for graded consult steps; remove guidance that treats `consult_*` as the schedulable name.

## Boundaries

* Does **not** rename `TASK_CONFIG` entries or change grading prompts, pass/fail states, encoded batch behavior, or `pass_threshold` vs `score_floor` semantics.
* Does **not** change `trigger_state` claim rules, triple-unique schema, or roster TO_WATCH multi-row pattern — only the consult/grade alias layer.
* Does **not** implement [AST-572](https://linear.app/astralcareermatch/issue/AST-572/organization-of-tasks-and-dispatch-task-keys) scope (Retry flag on dispatch rows, Scheduled Actions filters, `TASK_CONFIG` file reorganization, code-review phase/seq gate). [AST-572](https://linear.app/astralcareermatch/issue/AST-572/organization-of-tasks-and-dispatch-task-keys) adds display/organization metadata to the dispatch table; this epic trues up key alignment only — separate decisions, no overlap.
* Does **not** collapse keys where dispatch and catalog names already match (`evaluate_jd`, `qualify_job_listings`, artifact entry keys, roster/gazer orchestration keys that have no TASK_CONFIG entry).
* Must **not** reintroduce consult routing from `trigger_state` maps (**AST-534** behavior preserved).

Per **ASTRAL_CODE_RULES** §2.1, schedulable keys remain config-driven; missing config stays crash-worthy — no parallel dispatch seed vocabulary.

## Acceptance criteria

1. Susan can create and run a `grade_do` dispatch row at `PASSED_JD` (and `PASSED_JD_RETRY` where used) with no `consult_do` row or alias required.
2. After migration, existing environments show **zero** `dispatch_task` rows with `task_key` in `{consult_do, consult_get, consult_like}`; equivalent `grade_*` rows preserve scheduling fields (`freq_hrs`, `batch_size`, `debug`, `AUTO`, etc.).
3. Manual Run and AUTO dispatch for those rows execute the same graded consult batches as today; Execution History first-hop Task column shows `grade_do` / `grade_get` / `grade_like`.
4. Scheduled Actions phase grouping and sequence order for the three graded consult tasks match `TASK_CONFIG` without `(unassigned)` buckets caused by alias resolution.
5. Admin API rejects new saves using retired `consult_*` keys with a clear validation error; no read-time alias accepts them post-cutover; `GET /api/admin/dispatch_tasks/task_keys` lists `grade_*` with correct phase/seq/trigger defaults.
6. `ASTRAL_CODE_RULES` dispatch pipeline table and test bible consult/dispatch sections reference `grade_*` only for those steps (no operator-facing `consult_*` schedulable names).

## Dependencies and blockers

* **Done prerequisites:** **AST-534** (row `task_key` drives consult/artifact entry), **AST-535** (triple unique + roster row routing), **AST-549** (config-derived dispatch admin defaults).
* **Related, not blocking:** [AST-572](https://linear.app/astralcareermatch/issue/AST-572/organization-of-tasks-and-dispatch-task-keys) (Backlog — dispatch admin organization metadata; separate from key alignment).
* **none** otherwise.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-736 (parent) | ftr/ast-736-task-keys-vs-dispatch-task-keys |
| AST-747 | sub/AST-736/AST-747-config-schedulable-keys-retire-consult-aliases |
| AST-748 | sub/AST-736/AST-748-db-migration-consult-dispatch-runtime-cutover |
| AST-749 | sub/AST-736/AST-749-admin-dispatch-task-keys-scheduled-actions |

**Epic worktree:** `astral-AST-736/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | 2ac79957-347f-48be-b70c-4f86ace12332 |
| Hedy | engineer | 0e636a61-6761-423c-abe9-d75ca3bc08d0 |
| Katherine | engineer | 6828a810-afbf-4006-8e64-d98f8c1286af |
| Betty | qa | d31811d0-445d-443e-84eb-2b5bb351b2dd |
| Radia | review | bb084614-c057-46bb-8c88-5c2eba495b2e |

---

## Original brief

I cannot see any value in maintaining a discrete set of dispatch task id's ("consult_do", e.g.)

I want us to just use task_key when scheduling jobs, now that we have decoupled the find_job_page processing to be multiple hops.

Can you think of any reason we would want to maintain that wrapper framework?

### Comments

#### chuckles — 2026-06-23T19:27:38.490Z
[merge-child] blocked: validate-sub-log — git pull merge commits in sub/AST-736/AST-747 range (bb012bf, 1ae1181, …). @Ada Lovelace republish sub from origin/ftr/ast-736-task-keys-vs-dispatch-task-keys with canonical plan|code|merge-tests|test|docs|resolve sequence only.
— Chuckles

#### susan — 2026-06-19T01:22:50.008Z
it looks like the subissues of this issue are marked as blocked by a ticket in the backlog.  You need to correct their understanding that this is an intermediate step before we tackle the refactor ticket.

#### chuckles — 2026-06-18T22:56:07.853Z
@susan Headless agent CLI hit Ultra usage limit before AST-747 test-child — resume datt after spend limit resets (6/24) or set Spend Limit / switch model off Auto.
— Chuckles

#### chuckles — 2026-06-18T21:21:43.591Z
@susan — three open questions on the Description need your call before dispatch:

1. **Migration operator path:** automatic idempotent DB rename on deploy, or Table Upsert / admin scripts only?
2. **Hard cutover vs read-time alias:** zero runtime/admin acceptance of `consult_*` after ship, or temporary compat?
3. **AST-572 relationship:** supersede the consult/grade mapping bullet here, or keep AST-572 as a separate follow-on?

— Chuckles

#### chuckles — 2026-06-18T21:20:56.619Z
@susan Open questions on the definition (see Description):

1. Non-agent hops (`validate_title`, `scrape_jd`, `fetch_website`, `fetch_job_pages`, `select_job_page`, `parse_job_list`) — operation-style keys vs TASK_CONFIG entries?
2. Historical `dispatch_ledger` — leave legacy alias strings or backfill?
3. Migration — in-place SQL rename on deploy vs dual-read window?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
