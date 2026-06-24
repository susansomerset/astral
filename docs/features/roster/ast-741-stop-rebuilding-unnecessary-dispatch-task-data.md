# AST-741 — Stop rebuilding unnecessary dispatch_task data

<!-- linear-archive: AST-741 archived 2026-06-23 -->

## Linear archive (AST-741)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-741/stop-rebuilding-unnecessary-dispatch-task-data  
**Status at archive:** Done  
**Project:** Astral Roster  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Susan is deleting dispatch rows whose trigger state ends in `_RETRY`, and they reappear after a server restart. That undermines deliberate admin curation of what runs on the scheduler. This epic makes automatic task-table writes predictable: stop re-creating rows Susan removed, and deliver a complete inventory of every code path that inserts, updates, or deletes rows in `agent_task` and `dispatch_task` so future changes do not surprise her.

## Functional scope

* **Stop automatic separate** `*_RETRY` **dispatch_task rows.** On process start and on lazy schema ensure, the system must not insert additional `dispatch_task` rows whose `trigger_state` is a retry holding state (e.g. `VALID_TITLE_RETRY`, `JD_READY_RETRY`, `WEBSITE_FOUND_RETRY`). Susan's explicit deletes must survive restart.

  **What "automatic row seeding" means:** a legacy startup/schema path that `INSERT OR IGNORE`s extra dispatch rows — one per candidate per base task — with `trigger_state` set to the companion `*_RETRY` state. That is **not** the same as dispatch **claim** behavior: a single primary row (`trigger_state=VALID_TITLE`) already counts and processes entities in both `VALID_TITLE` and `VALID_TITLE_RETRY` via companion-state claim logic, with error-case routing driven by the entity's `_RETRY` state. This epic removes the redundant extra rows; it preserves the one-row-per-primary-state model Susan described.
* **Stop automatic** `gaze_board` **dispatch_task seeding.** `gaze_board` is decommissioned. Remove automatic companion-row creation for it; do not add or extend `gaze_board` task content as part of this work.
* **Inventory of task-table writers.** Produce and check in `debug/startup_db_inventory.md` listing every code action that mutates `agent_task` or `dispatch_task` content: what triggers it (startup bootstrap, first DB access, admin API, one-time migrations, manual ops scripts), whether it is idempotent, and whether it can recreate deleted rows. Group by automatic vs operator-initiated.
* **Preserve intentional operator control.** Susan can still create, edit, and delete dispatch rows and agent task versions through Manage Dispatch / Manage Tasks. Automatic paths must not override those choices on restart.
* **Preserve primary dispatch scheduling.** Primary-state dispatch rows, scheduler tick behavior, companion trigger-state claim logic, and `_RETRY` error-case routing must keep working without separate `*_RETRY` dispatch rows.

## Boundaries

* Surgical fix only — does not implement retry-flag UI, config phase reorganization, or Scheduled Actions filters (future Backlog work).
* Does not change job or company state machines, retry holding state definitions in config, or consult failure routing (`VALID_TITLE` → `VALID_TITLE_RETRY`, etc.).
* Does not remove `sync_agent_tasks` blank-row inserts for wholly missing `TASK_CONFIG` keys unless the inventory shows they cause the same delete-then-reappear problem.
* Does not redesign the admin UI for dispatch or agent tasks.
* Does not include AST-381 snapshot export/import as an automatic startup path.
* Does not alter `dispatch_ledger` or other tables — inventory covers only `agent_task` and `dispatch_task`.
* `gaze_board`: decommission only — no new prompts, features, or documentation for that task key beyond removing its automatic seed path.
* Must not break one-time schema migrations that upgrade column layout; only stop recurring re-seed of rows Susan may have deleted.

## Acceptance criteria

1. Susan deletes all `*_RETRY` `dispatch_task` rows for a candidate, restarts the server, and those rows are still absent.
2. Primary dispatch rows for the same `task_key` continue to claim and process entities in the companion retry holding state (e.g. jobs in `VALID_TITLE_RETRY` still process when `qualify_job_listings` is scheduled on `VALID_TITLE`).
3. No automatic path re-inserts `gaze_board` dispatch rows on restart or schema ensure.
4. `debug/startup_db_inventory.md` lists every mutating code path for `agent_task` and `dispatch_task`, tagged automatic vs manual, with enough detail that Susan can tell which paths may recreate deleted rows.
5. No automatic writer re-inserts deleted `*_RETRY` dispatch rows on restart or lazy schema ensure.
6. Manage Dispatch and Manage Tasks still create, update, and delete rows as today.

## Dependencies and blockers

none.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-741 (parent) | ftr/ast-741-stop-dispatch-retry-seed |
| AST-745 | sub/AST-741/AST-745-stop-dispatch-retry-seed |

**Epic worktree:** `astral-AST-741/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Hedy | engineer | 46021daf-ee5f-40ad-a7ad-1bc4913de0bc |
| Betty | qa | 4837b62d-9e02-4a78-a8f2-27631b5d843b |

---

## Original brief

I keep finding dispatch tasks with "_RETRY" in their trigger state.  I deleted those recently but I think they're getting re-inserted when the server restarts.

Please stop doing that, and make me a list of all the code actions (e.g. at startup) that affect content in the agent _task and the dispatch _task tables.

### Comments

#### chuckles — 2026-06-23T19:02:08.430Z
[merge-child] blocked: `validate-sub-log` — git pull merge on `origin/sub/AST-741/AST-745-stop-dispatch-retry-seed` (`Merge remote-tracking branch … into tests`). Sub log also carries AST-747 / AST-751 commits — republish clean AST-745-only stack from `origin/ftr/ast-741-stop-dispatch-retry-seed` before rollup.

@Betty White — tests-tree merge hygiene on sub ref.
@Hedy Lamarr — republish `sub/AST-741/AST-745-stop-dispatch-retry-seed` if Betty cannot reconcile.

— Chuckles

#### chuckles — 2026-06-18T22:54:42.104Z
@susan

Headless `agent` hit monthly Auto usage limit during **test-child** (AST-745 Tests Ready). Build + qa complete; need spend-limit bump or fixed model slug to resume pipeline at stage 8.

— Chuckles

#### chuckles — 2026-06-18T22:28:57.070Z
@susan

1. Inventory home: is a plan doc under `docs/features/roster/` sufficient, or should a short summary also land somewhere you check routinely (e.g. Code Rules admin/data section)?

— Chuckles

#### chuckles — 2026-06-18T22:23:36.741Z
@susan

1. After automatic `*_RETRY` row seeding stops, is the intended model **primary row only** (companion retry states claimed via existing dispatch trigger-state logic, no separate retry rows unless you add them manually), or should specific retry dispatch rows remain opt-in via admin only?
2. Should automatic `gaze_board` companion row seeding (copied from `gaze` / `board_search` on schema ensure) stay as-is, be removed in this epic, or split to a follow-up ticket?

— Chuckles

#### chuckles — 2026-06-18T22:23:18.742Z
@susan — three product calls before dispatch:

1. **Scope of automatic inserts:** Stop `_RETRY` companion re-insert only, or also stop other automatic dispatch inserts (e.g. `gaze_board` companion rows cloned from `gaze` / `board_search`) in the same pass?
2. **Relationship to AST-572:** Surgical fix here (stop re-insert; you manage rows manually), or hold until AST-572 is approved and implement the retry-flag model instead of companion rows?
3. **Inventory home:** Is a plan doc under `docs/features/roster/` sufficient, or should a short summary also land somewhere you check routinely (e.g. Code Rules admin/data section)?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
