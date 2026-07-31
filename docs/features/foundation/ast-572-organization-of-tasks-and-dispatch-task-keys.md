# AST-572 — Organization of tasks and dispatch task keys

<!-- linear-archive: AST-572 archived 2026-07-22 -->

## Linear archive (AST-572)

**Archived:** 2026-07-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-572/organization-of-tasks-and-dispatch-task-keys  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-735

### Description

## Purpose

Susan reopened a legacy dispatch-administration wish list for a **per-bullet traceability audit**. That audit is **approved**: seven of eight original bullets are **done**, **superseded**, or **owned by in-flight epics** (**AST-736**, **AST-735/751**). Susan confirmed companion-state retry claim is sufficient (**AST-741/745**), accepts DB task-group metadata over config `phase`/`seq` (**AST-734/740**), and wants **one remaining deliverable** from this parent: a **Section/Group filter** on Scheduled Actions (original bullet 5). This parent ships that filter; it does not re-implement work already assigned elsewhere.

## Functional scope

**Audit resolutions (Susan approved 2026-06-23)**

1. **Task-key alignment and phase/sequence metadata** — **In flight under AST-736** (children AST-747, AST-748, AST-749). Grouping metadata from **AST-734**; config `phase`/`seq` retirement under **AST-740**.
2. **Dynamic input-state lookup** — **Done** (**AST-484**, `GET /api/admin/dispatch_tasks/state_options`).
3. **Retry without separate** `*_RETRY` **dispatch rows** — **Done** (**AST-741/745** companion-state claim). Susan: no Retry toggle UI needed.
4. **Sort by phase/section** — **Done** via DB `task_group_order` / `task_group_name` / `task_seq` (**AST-734**).
5. **Filter by section on Scheduled Actions** — **This parent.** Susan wants a dedicated **Section/Group** filter control (Task dropdown + collapsible sections alone are not enough).
6. **Candidate Selected/All filter** — **Done under AST-735/751** (All-candidate mode with task grouping preserved).
7. **Reorganize TASK_CONFIG by phase/seq** — **Superseded** by **AST-734/740** (Susan prefers DB-editable grouping).
8. **Code-review gate for config phase/seq** — **Superseded** (same decision).

**In-scope capability for this parent**

* **Section/Group filter on Scheduled Actions:** Operators can narrow the table to one task group (`task_group_name` / section) from a filter control on the Scheduled Actions screen. Filter combines with existing Candidate, Task, and operational filters. Collapsible section layout and task order stay aligned with Manage Tasks (**AST-734** metadata).

## Boundaries

* Does not implement consult→grade alias cutover (**AST-736**), All-candidate layout (**AST-735/751**), or retry row seeding (**AST-741/745**).
* Does not add a Retry toggle on dispatch rows (Susan declined).
* Does not reorganize `TASK_CONFIG` or add config `phase`/`seq` review gates.
* Does not change scheduler tick logic, dispatch claim/run behavior, or `dispatch_ledger`.
* Admin UI + supporting admin API only — no backend debug-logging requirements.

## Acceptance criteria

1. Scheduled Actions exposes a **Section/Group** filter listing distinct `task_group_name` values (plus an All option) derived from the same task metadata Manage Tasks uses.
2. Selecting a section/group shows only dispatch rows whose `task_key` belongs to that group; combined with Candidate, Task, and operational filters, filters intersect correctly.
3. With **Candidate → All**, section filter still works and task grouping/order within visible sections matches single-candidate view.
4. Audit matrix bullets 1–4 and 6–8 remain satisfied by cited tickets; Susan can verify in Linear without regression from this ship.

## Dependencies and blockers

* **AST-734** Organizing Tasks — task-group metadata authority (User Testing).
* **AST-735/751** Scheduled Actions refresh — filter bar and All-candidate layout should land first or in parallel so section filter builds on the current screen (**AST-751** Tests Passed).

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-572 (parent) | ftr/AST-572-organization-tasks-dispatch-keys |
| AST-768 | sub/AST-572/AST-768-scheduled-actions-section-group-filter |

**Epic worktree:** `astral-AST-572/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | eec6ba13-946d-458f-bac5-31089da5062a |
| Betty | qa | 881fb60b-2c69-4299-b3b1-f7208dedff79 |
| Radia | review | 33443f88-7e4b-440e-9f2d-e6998352e94e |

---

## Original brief

<blows dust off backlog issue>
Chuckles, we have done *most* of these things already, I believe, but I want you to confirm for each bullet point below how and by which ticket the stated requirement is addressed…

Original description:

As the platform expands, the dispatch management is getting really clumsy and confusing.

* use the task_config element in [config.py](<http://config.py>) to map the task keys to their agent counterparts (e.g. "grade_" vs. "consult_") so that 100% of dispatch tasks are given a phase and sequence.
* Add a dynamic lookup for input state that is limited to the expected states.
* Replace the two separate "_RETRY" dispatch jobs and just have a Retry flag on the task dispatch record, so that the claim gets both states of "<state>" and "<state>_RETRY"
* Always sort the tasks/dispatch lists by phase and section.
* Add filters by section to the Scheduled Actions screen
* Add a candidate filter of "Selected" or "All" on the Scheduled Actions screen.
* REORGANIZE [CONFIG.PY](<http://CONFIG.PY>) SO THAT TASK_CONFIG IS ALWAYS IN THE PHASE AND SEQUENCE ORDER.  Add comment headers for each phase.
* In code review, do not allow Tasks to exist in [config.py](<http://config.py>) without a phase and sequence assigned (currently 8 without them). This will make it easier for me to move them where they should go within the [config.py](<http://config.py>) file without having to type everything out.

### Comments

#### chuckles — 2026-06-23T20:07:07.098Z
[merge-child] blocked: `validate-sub-log.sh` — git pull merge commits on `origin/sub/AST-572/AST-768-scheduled-actions-section-group-filter` (Merge remote-tracking branch … into tests in merge-tests history).

@Betty White — republish clean `merge-tests(AST-768)` from ftr tip (no pull merges in sub log range). @Katherine Johnson — standby if product republish needed after Betty lands tests tip.

— Chuckles

#### chuckles — 2026-06-23T19:26:41.578Z
@susan

1. Bullet 3 — is companion-state claim (AST-741/745) enough, or do you still want a Retry toggle on each dispatch row?
2. Bullet 5 — Task filter + collapsible sections enough, or add a Section/Group filter?
3. Bullets 7–8 — OK to close as superseded by AST-734/740 (DB task_group_* metadata)?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
