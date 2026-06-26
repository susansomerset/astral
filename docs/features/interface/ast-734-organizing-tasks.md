# AST-734 — Organizing Tasks

<!-- linear-archive: AST-734 archived 2026-06-23 -->

## Linear archive (AST-734)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-734/organizing-tasks  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-735

### Description

## Purpose

Administrators organize dozens of agent tasks across pipeline stages. Today, group labels and sort order live in code-owned task configuration (`phase`, `seq`), which forces a deploy to reorder sections or rename groups on Manage Tasks and Scheduled Actions. Susan wants task grouping and ordering to be an admin-editable UI concern: stable `task_key` values still come from the product catalog, but human-readable names, group labels, and sort order are maintained in the Manage Tasks edit flow without validation overhead or parent-group entities. This keeps operational layout flexible while preserving config as the sole authority for which tasks exist and how they execute.

## Functional scope

* **Four metadata fields per catalog task:** Each task keyed in the product task catalog carries `task_group_order` (string, group sort key), `task_group_name` (string, collapsible section heading), `task_seq` (float, within-group sort key), and `task_name` (string, human-readable label for the task). Values persist on the agent task record and are global per `task_key` — never candidate-specific.
* **Database-only authority:** Admin APIs and UI read grouping metadata exclusively from persisted agent-task storage. After deploy, no code path reads `phase` or `seq` from TASK_CONFIG for grouping or sort.
* **One-time seed on deploy:** Migration copies today's organized config `phase` / `seq` into the new fields wherever they exist today; derive initial `task_group_name` from `phase`; map `task_group_order` from existing group ordering; use `task_key` as initial `task_name` where no separate name exists. Screens must not regress to empty grouping after deploy.
* **Catalog keys only:** The set of tasks shown and editable is exactly the keys defined in TASK_CONFIG. Operators cannot add, rename, or delete task keys from Manage Tasks or any other admin screen.
* **Edit in Manage Tasks popup only:** The four fields are editable only in the Manage Tasks task edit modal (same place operators already edit prompts and agent assignment). List views and other screens consume the stored values read-only.
* **No validation:** The product does not enforce consistency of group orders, duplicate sequence numbers, empty group names, or cross-task group alignment. Susan validates and corrects data manually in the admin UI.
* **Manage Tasks presentation:** Tasks render in collapsible groups (existing CollapsiblePanel behavior, including zero expanded sections). Sections sort by `task_group_order`; rows within a section sort by `task_seq`. Section headers show `task_group_name`. Row labels use `task_name` where a human-readable task label is shown. The numeric `task_seq` value is never displayed — sort only.
* **Scheduled Actions presentation:** Dispatch task lists use the same group metadata for sectioning and within-group order. Rows whose dispatch `task_key` aliases to a catalog key resolve metadata from that catalog key, consistent with existing dispatch-to-catalog resolution behavior.
* **Other admin sequence views:** Any admin UI that orders tasks by catalog sequence without using runtime timestamps uses the same four fields instead of config `phase` / `seq`.
* **Prompt and dispatch behavior unchanged:** Editing group metadata does not alter prompts, agents, run-next chains, dispatch eligibility, scheduler behavior, or execution order in the backend pipeline.

## Boundaries

* Does not introduce parent group records, group CRUD APIs, or referential validation between tasks and groups.
* Does not add, remove, or rename task keys from the UI.
* Does not validate `task_group_order`, `task_group_name`, `task_seq`, or `task_name` beyond basic type/presence needed to save (no business rules about correct ordering).
* Does not display `task_seq` as a visible column or inline number in list UIs.
* Does not change how dispatch runs, claims batches, or orders work by timestamp or ledger.
* Does not require debug-logging changes (admin UI only).
* Must not break existing Manage Tasks edit/save for prompts, agents, and run-next; collapsible sections and Scheduled Actions table behaviors (filters, run/stop, modals) remain intact.
* **Config cleanup in scope:** Remove `phase` and `seq` from every TASK_CONFIG entry in [config.py](<http://config.py>) as part of this epic — no orphaned keys, no dual sources, no confusion about where grouping lives.

## Acceptance criteria

1. Deploy seed copies existing config `phase` / `seq` into the new DB fields for all catalog tasks that had them; initial `task_name` populated where appropriate.
2. Every catalog task key appears on Manage Tasks with stored `task_group_order`, `task_group_name`, `task_seq`, and `task_name`.
3. Manage Tasks edit modal exposes all four fields; saving persists them; reopening the modal shows saved values.
4. Manage Tasks list groups tasks into collapsible sections ordered by `task_group_order`; within each section, rows order by `task_seq`; section titles show `task_group_name`; no visible `task_seq` column or number.
5. Scheduled Actions groups and sorts dispatch rows using DB metadata (including alias keys resolving to catalog metadata).
6. Task keys cannot be created or deleted from Manage Tasks; keys absent from the catalog do not appear as new editable rows.
7. Invalid or inconsistent group data can be saved without server-side rejection (Susan verifies manually).
8. `phase` and `seq` are removed from TASK_CONFIG; grep confirms no runtime read of those keys for UI grouping or sort.
9. Existing component tests for Manage Tasks and Scheduled Actions are updated where grouping/sort expectations change; no regressions to edit-modal prompt save or dispatch row actions.

## Dependencies and blockers

* AST-567 (Done) — Scheduled Actions already uses phase-grouped sections and dispatch→catalog mapping; this feature swaps the metadata source to DB.
* None blocking start.

## Open questions

None.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-734 (parent) | ftr/AST-734-organizing-tasks |
| AST-738 | sub/AST-734/AST-738-task-grouping-metadata-storage-and-seed |
| AST-739 | sub/AST-734/AST-739-admin-ui-task-grouping-from-db-metadata |
| AST-740 | sub/AST-734/AST-740-remove-phase-and-seq-from-task-config |

**Epic worktree:** `astral-AST-734/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Hedy | engineer | 551da783-6dcf-4059-9cd9-00c45a3603c9 |
| Katherine | engineer | 7ba211fc-00f1-42a2-94c5-2083e70d50b8 |
| Ada | engineer | 858a9df4-a707-4700-9b74-130726d169d2 |
| Betty | qa | 93ef49f6-690c-48e0-8997-529cdb2f52c5 |
| Radia | review | 37bcb07a-cff1-4d93-b417-895c26d9c440 |

---

## Original brief

The grouping and ordering of tasks is a UI concern, not a config concern.  Let's create "task_group_order" (string), "task_group_name" (string), "task_seq" (float), "task_name" (string, human-readable).  These fields are changeable in the Manage Tasks popup only.  DO NOT ADD VALIDATION, let me figure out when the group orders are wrong for different tasks.  In other words, I will manually validate this data in the admin screen, rather than adding overhead of parent group records, etc.  We'll probably adopt those later, but not in scope for this ticket.

Do not display the sequence number of the task when displaying, just organize them in that sort order.

Task keys are drawn ONLY from the [config.py](<http://config.py>) file from the array found in TASK_CONFIG, and cannot be added, changed or deleted from the Manage Tasks screen, but the metadata described above shall dictate the UI rendering for the Manage Tasks page as well as the Scheduled Actions page and anywhere else in the UI we are tracking task sequences without runtime timestamp data.

Task Groups remain collapsible as currently designed.

### Comments

#### chuckles — 2026-06-18T21:16:46.864Z
@susan Open questions (see Description):

1. One-time seed from today's config `phase` / `seq`, or start empty for manual entry?
2. Global per `task_key`, or candidate-specific?
3. Remove `phase` / `seq` from config in this epic, or follow-up?

— Chuckles

#### chuckles — 2026-06-18T21:14:23.986Z
@susan

1. Should deploy include a one-time seed copying current TASK_CONFIG **phase** / **seq** (and derived group labels) into the new columns, or should rows start empty for you to fill manually?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
