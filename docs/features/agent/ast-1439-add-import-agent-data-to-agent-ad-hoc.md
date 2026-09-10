# AST-1439 — Add "import agent data" to Agent Ad Hoc

<!-- linear-archive: AST-1439 archived 2026-09-09 -->

## Linear archive (AST-1439)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1439/add-import-agent-data-to-agent-ad-hoc  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Agent Ad Hoc can author a prompt from a catalog task, but it cannot pull a *past run* back onto the workbench. Operators who want to tweak something that already went to the model have to reconstruct it by hand from Execution History. This epic adds an import path: pick a stored `agent_data` run, load its prompt (and see its response if one exists), edit, and Test again — without rewriting the rows that were loaded. New Tests keep the existing `adhoc-<task_key>` audit label, including when the source run was itself an ad hoc Test.

## Functional scope

* **Pick a stored run.** Agent Ad Hoc shows a selection list of stored `agent_data` runs. Each row is one batch (not one block): timestamp, `entity_id`, and `task_key`. The list includes production hops and previous ad hoc Tests (`adhoc-*`). Newest first. No candidate filter, date filter, or display cap in this epic — the list is the table. When `debug=True` on the list path, logs show what was **found** and what was **recorded** per listed run (index header, timestamp / entity / task_key, outcome) using the AST-538 contract (`|` detail prefix; payloads >50 lines truncated 15 / omitted / 15). When `debug=False`, no new debug-contract lines.
* **Load copies into the session.** A Load control copies that batch’s prompt blocks into the seven Ad Hoc editors (System, Cache A–D, No Cache, User from the TASK block). Missing slots become empty so leftover editor text does not mix with the import. If a RESPONSE exists, it is shown with the existing agent_data panes for that batch. Load does not write `agent_data`. If the editors already have content, confirm replace the same way fetch-from-task does.
* **Edit and run without touching the source.** After Load, the operator edits and uses Preview / Test as today. Test does not send the imported response. Test writes a **new** batch. Source rows stay unchanged. Load sets the workbench task key to the source `task_key` with a single leading `adhoc-` stripped, so Test still records `adhoc-<task_key>` (AST-515) and does not double-prefix. That task-key update must not fetch catalog prompts over the imported editors. Load also restores the run’s `entity_id` into the session. Agent stays whatever the operator already selected (agent is not stored on `agent_data`).

## Architectural definition

* **Patterns to reuse**
  * `pattern.ui.admin-endpoint` — new list (and load, if not already covered by `GET /api/agent_data/<batch_id>`) is a thin authenticated admin route; React renders the resolved rows and does not query `agent_data` itself.
  * `pattern.ui.shared-button-roles` — Load is a labeled commit (`btn primary`); cancel on the replace-confirm is `btn secondary`; destructive-looking replace confirm matches the existing fetch-from-task pair.
  * `pattern.layers.import-discipline` — UI → core (or existing agent-data read helpers); core → data; no UI → data.
  * `pattern.config.config-block` — `BLOCK_TYPES` is the map from stored blocks onto editors and panes.
* **New patterns proposed** — none. Import is a workbench read of existing `agent_data` plus the existing Test writer.
* **Applicable statutes**
  * Universal set (`tier: universal`, `status: active`) — product epic.
  * `astral.idioms.require-auth-on-protected-endpoints` — new admin Ad Hoc routes stay authenticated (same family as current `/adhoc/*`).
  * `astral.layers.import-direction` / `astral.layers.ui-config-driven-business-logic` — list/load shaping in API/core; React renders.
  * `astral.standards.debug-contract-gated` — list found→recorded only when `debug=True`.
  * `astral.standards.dry-and-focused-functions` — reuse `GET /api/agent_data/<batch_id>` and `BatchAgentDataPanes` for block bodies and response display; do not fork a second inspector.
  * `astral.standards.in-scope-only` / `astral.standards.database-header-inventory` — `agent_data` only; no new table. A new list query still has to be a listed `agent_data` use.
  * `astral.standards.data-raises-caller-logs` / `astral.standards.logging-via-utils` — data raises; core/API logs.
  * `astral.standards.names-not-ticket-ids` / `astral.standards.no-hardcoded-sets` — domain names; block types from config.
  * `astral.ui.frontend-file-placement` / `astral.ui.naming-conventions` — stays on the existing Ad Hoc page; no nested page tree.
  * `astral.agent.do-task-delegation` — this is workbench import + existing `run_adhoc` Test, not a new `do_task` hop.

## Boundaries

* Does **not** edit, delete, or rewrite the loaded `agent_data` rows. Load is copy-into-editors only.
* Does **not** add filters, search, pagination, or a cap on the picker.
* Does **not** change Manage Tasks, production `do_task`, dispatch, `run_next`, Save As, or Execution History chrome.
* Does **not** add a Response editor tab. Response is display-only; Test ignores it.
* Does **not** persist which agent ran the source hop (not stored on `agent_data`).
* Does **not** snapshot historical live content as its own editor. Stored prompt blocks load as-is; Preview/Test then follow existing rules (including rebuilding live content from the **current** entity when a task and entity are selected). Clear the entity to send only the loaded text.
* Must **not** break: seven-segment editors (AST-1403), fetch-from-task, Preview modal, post-Test panes, Execution History `adhoc-<task_key>` rows, Preview-does-not-ledger.

## Acceptance criteria

1. Agent Ad Hoc shows a selection list whose rows are stored `agent_data` batches. Each visible row has timestamp, `entity_id`, and `task_key`. A production hop and an earlier Ad Hoc Test (`adhoc-<task_key>`) both appear. Newest first.
2. Load on a batch that has System + Cache A + User + Response fills those three editors, leaves Cache B–D and No Cache empty if those blocks were absent, and shows the stored Response in the existing agent_data panes for **that** batch. The source `agent_data` row contents are unchanged after Load.
3. After Load, editing User and running Test creates a **new** `agent_data` batch (new `batch_id`). The imported batch’s prompt and response blocks are bit-for-bit the same as before Test. The new ledger/task label is `adhoc-<task_key>` with a single `adhoc-` prefix even when the imported run was already `adhoc-<task_key>`.
4. Load of a run whose `task_key` is `evaluate_jd` (or `adhoc-evaluate_jd`) does not replace the imported editor text with catalog `agent_task` prompts for that key.
5. Load of a run that has an `entity_id` leaves that id selected for the next Preview/Test. Preview/Test still require an agent, same as today.
6. Load with dirty editors asks to replace (Yes / Cancel). Cancel leaves editors and panes as they were.
7. When `debug=True` on the list path, logs show a per-run index header plus found → recorded detail; when `debug=False`, listing adds no new debug-contract lines.

## Dependencies and blockers

* **AST-1403** (User Testing) — seven-segment Ad Hoc workbench, Preview modal, post-Test agent_data panes. This epic attaches to that page.
* **AST-514 / AST-515** (Done) — Test already writes ledger + `agent_data` as `adhoc-<task_key>`. This epic consumes that label; it does not invent a second one.

none blocking start (AST-1403 is already on `origin/dev`).

## Open questions

none

## Proposed child tickets

#### 1!: **Ad Hoc import list and load payload - Ada**

Own the read path: an authenticated admin list of `agent_data` runs (one row per batch: timestamp, `entity_id`, `task_key`, plus whatever identity Load needs — typically `batch_id`), including `adhoc-*` rows, newest first, no filter/cap. Load payload is that batch’s prompt blocks (and RESPONSE if present), via existing agent_data read helpers where they already return the blocks. When `debug=True`, list logs found → recorded per run. Does **not** own the picker chrome or editor mapping (#2). Does **not** change Test persist except as needed so a workbench task key of `adhoc-foo` still stores as `adhoc-foo` rather than `adhoc-adhoc-foo` (strip one leading `adhoc-` before applying the AST-515 prefix, or equivalent).
**Citations:** `pattern.ui.admin-endpoint`, `pattern.layers.import-discipline`, `pattern.config.config-block`, `astral.idioms.require-auth-on-protected-endpoints`, `astral.standards.debug-contract-gated`, `astral.standards.database-header-inventory`, `astral.standards.data-raises-caller-logs`
**Estimate: 3**

#### 2: **Ad Hoc import picker and Load - Hedy**

After #1. Agent Ad Hoc grows the selection list and a Load button. Load fills the seven editors from the payload (TASK → User; missing slots empty), shows RESPONSE via existing `BatchAgentDataPanes` for that batch, restores `entity_id`, sets the workbench task key with a single `adhoc-` stripped, and does **not** run fetch-from-task over the imported text. Dirty-editor replace confirm matches fetch-from-task. Does **not** own the list query (#1). Does **not** change Save As, Preview modal, or production `do_task`.
**Citations:** `pattern.ui.shared-button-roles`, `pattern.config.config-block`, `astral.ui.frontend-file-placement`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.dry-and-focused-functions`
**Estimate: 3**

---

## Original brief

Give me a selection list of timestamp, entity_id, and task_key from the agent_data table, and an "load" button, which will load the prompt content (with response, if we have one), and allow me to edit and run the prompt (ignoring the response) in the ad hoc session without changing the originally loaded agent_data content.  Include previous adhoc data from agent data, just add "adhoc-<task_key>"

### Comments

#### chuckles — 2026-08-24T21:50:14.919Z
[thread-missing] Cursor chat `295539a4-1c66-4658-8bcb-49ae3a6c50ed` has no local `store.db` on **not-chuckles** (expected `/home/susan/.cursor/chats/40f37617870e538aada0246cb9f8c346/295539a4-1c66-4658-8bcb-49ae3a6c50ed/store.db`; blob-search also empty).

Minting a **new** conversation on this host and continuing (history from the old UUID is not recovered).

Replacement UUID: `ec6e0ee2-7688-4695-ab12-d31c98c6a1f8`.

Watcher rule `datt` on `AST-1439` (Thread owner `AST-1439`).

---

_Implementation detail may live in git history on `origin/dev`._
