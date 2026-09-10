# AST-1403 — Update Adhoc Agent to mirror new task structure

<!-- linear-archive: AST-1403 archived 2026-09-09 -->

## Linear archive (AST-1403)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1403/update-adhoc-agent-to-mirror-new-task-structure  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** High / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The Agent Ad Hoc workbench still authors prompts as the old three-slot layout (User / Cache / NoCache), while Manage Tasks and production `do_task` already use the seven-segment model (System, Cache A–D, No Cache, User). Operators cannot edit or save the new slots from Ad Hoc, Preview sits inline at the bottom of the page, and the Test result is a dumped text pane instead of the same agent_data block tabs used everywhere else. This epic brings Ad Hoc to parity with the current task structure so a workbench round-trip — load, edit, preview, test, save, inspect stored blocks — matches what production stores and what Execution History already shows.

## Functional scope

* **Seven-segment editors.** Agent Ad Hoc prompt inputs match Manage Tasks: System Prompt, Cache Block A, Cache Block B, Cache Block C, Cache Block D, No Cache Block, User Prompt. Loading a task fills every segment from that task’s saved content. Empty System at Preview and Test follows the same production rule as Manage Tasks: an empty System segment is filled from the selected agent’s content. Live content is not an editor; it still comes from the selected entity and appears in Preview when an entity is chosen.
* **Save maps to the real columns.** Save As writes each editor into the matching `agent_task` segment (System → system, Cache A → cache A, B–D → cache B–D, No Cache → no-cache, User → user). Overwrite confirmation treats any of the seven segments as existing content. Saving does not invent extra columns or remap Cache A into B–D.
* **Preview Prompt is a modal.** Preview Prompt opens a scrollable modal (same family as Manage Tasks preview), not an inline block at the bottom of the page. The modal shows the resolved seven segments plus live content, with empty slots visible as empty.
* **Test shows agent_data panes.** After Test, the workbench shows the standard agent_data tabbed panes (System, Cache A–D, No Cache, Task, Response — same order and meaning as Execution History). A dumped response text block at the bottom of the page is not the inspection surface. Timesheet/cost for that run remains visible with those panes.
* **Ad hoc Test persists complete blocks.** A workbench Test stores prompt and response blocks in `agent_data` for that run: System, each non-empty Cache A–D, No Cache (including live content when present), Task (user), and Response. Empty segments are omitted. Preview does not write `agent_data`. When `debug=True`, the store path logs what was **found** and what was **recorded** per block (index header, block type, outcome, identifier) using the AST-538 contract (`|` detail prefix; long payloads truncated 15 / omitted / 15). When `debug=False`, no new debug-contract lines.

## Architectural definition

* **Patterns to reuse**
  * `pattern.ui.admin-endpoint` — Ad Hoc preview/test/save stay thin admin routes; segment resolve and persist stay out of React.
  * `pattern.ui.shared-button-roles` — Preview, Test, Save As, modal dismiss keep the shared labeled-button roles (Preview is secondary; Test is the commit).
  * `pattern.ui.icon-control` — modal close uses the shared icon-control, not a one-off × style.
  * `pattern.layers.import-discipline` — UI calls core/admin helpers; core writes `agent_data`; no UI → data.
  * `pattern.config.config-block` — `BLOCK_TYPES` remains the source of truth for stored block names and display order.
* **New patterns proposed** — none. This is Ad Hoc catching up to the AST-453 seven-segment model and the existing Execution History agent_data panes.
* **Applicable statutes**
  * Universal set (`tier: universal`, `status: active`) — product epic.
  * `astral.agent.do-task-delegation` — production hops stay on `do_task`; Ad Hoc remains the workbench runner (`run_adhoc` / workbench wrapper), but its segment assembly and `agent_data` writes must match the seven-segment helper production already uses. Do not fold Test into `do_task` (that would impose production schema validation on the workbench; AST-1394 already forbids overlaying type errors on a successful Test).
  * `astral.config.config-source-of-truth` — block types and task segment names from config, not a parallel Ad Hoc enum.
  * `astral.standards.debug-contract-gated` — store/debug lines only when `debug=True`.
  * `astral.standards.dry-and-focused-functions` — reuse seven-segment assemble/store and the existing agent_data pane component; do not fork a second block model.
  * `astral.standards.no-hardcoded-sets` — display order follows `BLOCK_TYPES`, not a page-local list that drifts.
  * `astral.layers.import-direction` / `astral.layers.ui-config-driven-business-logic` — token resolve and persist in core/API; React renders.
  * `astral.standards.in-scope-only` / `astral.standards.database-header-inventory` — no new tables; existing `agent_task` seven columns and `agent_data` only.
  * `astral.patterns.require-auth-on-protected-endpoints` — admin Ad Hoc routes stay authenticated.
  * `astral.ui.frontend-file-placement` / `astral.ui.naming-conventions` — Ad Hoc page and shared modal/pane components stay in the established UI layout.
  * `astral.standards.logging-via-utils` / `astral.standards.data-raises-caller-logs` — data layer still raises; core logs store failures.

## Boundaries

* Does **not** change Manage Tasks, production `do_task` assembly, dispatch, or `run_next` chain tokens.
* Does **not** add or rename `agent_task` columns (Cache A remains the existing cache slot; B–D already exist).
* Does **not** re-do AST-1392 / AST-1393 / AST-1394 (success body stringify and Test overlay). Those stay landed; this epic is the remaining seven-segment + inspection gap.
* Does **not** send Ad Hoc Test through `do_task` schema/grade validation. A successful provider reply still displays; persist still stores text.
* Does **not** author prompt copy for any product task, and does not change seed rows.
* Does **not** replace Execution History; it reuses the same agent_data tabbed panes on the workbench after Test.
* Must **not** break: pure ad hoc (no task key), entity picker / batch-first-N, token resolve, timesheets, Execution History rows with `adhoc-<task_key>`, Preview-does-not-ledger.

## Acceptance criteria

1. With a task that has distinct text in System and Cache A–D, loading it on Agent Ad Hoc shows each segment in the matching editor. Save As to that task (or another) and reload in Manage Tasks shows the same seven strings in the same slots.
2. A task whose only cache content is in Cache B (Cache A empty) round-trips through Ad Hoc load → Save As without moving that text into Cache A.
3. Preview Prompt opens a scrollable modal. The page body does not grow an inline resolved-preview block. The modal has tabs for System, Cache A–D, No Cache, User, and Live Content; resolved text matches what Test will send for those slots.
4. After a successful Test, the workbench shows agent_data tabs for that run (System, each stored Cache A–D, No Cache, Task, Response). Response is the stored Response block, not a separate dumped pane. Preview alone does not create or refresh those panes from a new batch.
5. For a Test whose editors have System + Cache A + Cache C + User populated (B and D empty), `agent_data` for that batch contains SYSTEM, CACHE_A, CACHE_C, TASK, and RESPONSE, and does not contain empty CACHE_B or CACHE_D rows. Opening the same batch from Execution History shows the same blocks.
6. Empty System in the editors still sends the selected agent’s content at Preview and Test (production fallback); Save As with empty System leaves `system_prompt` empty on the row.
7. When `debug=True` on a Test that stores multiple blocks, logs show a per-block index header plus found → recorded detail; when `debug=False`, that Test adds no new debug-contract lines.

## Dependencies and blockers

* **AST-453 / AST-454 / AST-456** (Done) — seven-segment `agent_task` persistence and Manage Tasks UI. This epic consumes that shape; it does not re-specify it.
* **AST-514 / AST-515** (Done) — Ad Hoc Test already writes ledger + `agent_data`; this epic completes the missing slots and the workbench inspection surface.
* **AST-1392 / AST-1393 / AST-1394** (Done) — RESPONSE stringify for object payloads. Do not regress.
* **AST-1290 / AST-1294** (User Testing) — html_links completeness; no shared scope.

none blocking start.

## Open questions

none

## Proposed child tickets

#### 1!!!: **Ad Hoc seven-segment resolve, assemble, persist - Ada**

Own the backend path: preview and test accept all seven segments; token-resolve each; assemble and send Cache A–D as separate cached blocks (empty omitted); workbench Test stores those blocks plus No Cache / Task / Response; Test response includes enough identity for the workbench to load that run’s agent_data panes. Save As already has columns — this child must not drop B–D on the way through preview/test/store. Does **not** own React editors, the preview modal, or the on-page agent_data panes (those are #2 / #3).
**Citations:** `pattern.ui.admin-endpoint`, `pattern.layers.import-discipline`, `pattern.config.config-block`, `astral.agent.do-task-delegation`, `astral.standards.debug-contract-gated`, `astral.config.config-source-of-truth`, `astral.standards.dry-and-focused-functions`
**Estimate: 5**

#### 2!: **Ad Hoc seven-segment editors and save - Hedy**

After #1. Agent Ad Hoc editors match Manage Tasks’ seven segments; fetch-from-task and Save As read/write all seven columns; overwrite/has-content treats any populated segment as content; Preview and Test requests send all seven fields. Does **not** own the preview modal chrome or the post-Test agent_data panes (#3).
**Citations:** `pattern.ui.shared-button-roles`, `pattern.config.config-block`, `astral.layers.ui-config-driven-business-logic`, `astral.ui.frontend-file-placement`, `astral.standards.no-hardcoded-sets`
**Estimate: 3**

#### 3: **Ad Hoc preview modal and agent_data panes - Katherine**

After #2. Preview Prompt opens the shared scrollable modal with seven-segment + live-content tabs (no inline preview at the bottom). After Test, the workbench shows the same agent_data tabbed panes as Execution History for that run (including timesheet/cost already shown there). Does **not** change how blocks are stored (#1) or which editors exist (#2).
**Citations:** `pattern.ui.shared-button-roles`, `pattern.ui.icon-control`, `pattern.config.config-block`, `astral.ui.frontend-file-placement`, `astral.standards.dry-and-focused-functions`
**Estimate: 2**

---

## Original brief

Currently the Adhoc Agent does not support System, Cache A, etc..  
he 
Please update it so that the inputs are identical, and saving the task to the agent_tasks table correctly puts the content blocks where they should go.

Also please make the "Preview Prompt" a scrollable modal popup, rather than displaying at the bottom of the screen, and instead, display our standard tabbed panes of agent_data for the ad hoc response.

Confirm that the agent_data is successfully saved from ad hoc calls, as well (I was having some spotty coverage when testing earlier).

### Comments

#### chuckles — 2026-08-17T06:11:36.326Z
AST-1413 STALE(dev+88) — @Katherine Johnson refresh sub/* (merge origin/dev + origin/ftr/AST-1403-update-adhoc-agent-to-mirror-new-task-structure) then republish.

#### chuckles — 2026-08-17T05:55:29.982Z
AST-1412 REVIEW — merge-child blocked; recalling Hedy for `Merge remote-tracking branch` on the sub tip.

#### chuckles — 2026-08-17T04:44:30.078Z
AST-1411 estimate 5→3 — wiring onto existing seven-segment assemble/store helpers

---

_Implementation detail may live in git history on `origin/dev`._
