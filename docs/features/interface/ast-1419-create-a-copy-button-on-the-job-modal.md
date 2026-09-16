<!-- linear-archive: AST-1419 archived 2026-09-09 -->

## Linear archive (AST-1419)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1419/create-a-copy-button-on-the-job-modal  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

When a job misbehaves in the pipeline, Susan needs the stored job plus the actual agent hops that produced it — not a screen of ids and empty pointer rows — so she can paste one clipboard snapshot into a Linear ticket and see the full processing context.

## Functional scope

A labeled Copy control on the Job Detail modal (In Review and Skipped) and on the Recommended Job Report. Clicking it copies a diagnostic snapshot of that job to the clipboard.

The snapshot is the full stored job record: every field on the job, including the job-data blob as stored (agent data id pins remain ids in the job body, not the display-hydrated artifact bodies).

Every agent data id on that record is expanded in the snapshot into populated agent_data content for all configured block types for that hop. When a row is a content pointer (`ref_agent_data_id` set and local content null), the snapshot includes the referenced content, not the null.

After a successful copy, the control shows brief Copied feedback, then returns to Copy. A blocked clipboard write is silent.

Backend debug: when debug is on, the assembler logs what was found and recorded per job and per expanded agent data id — index headers and working detail, long block content truncated per the backend debug contract. No debug-logging requirement on the React control.

## Architectural definition

**Patterns to reuse**

* `pattern.ui.shared-button-roles` — labeled Copy is a neutral modal action (`btn secondary`), not a primary commit and not an icon-only control.
* `pattern.layers.import-discipline` — snapshot assembly lives behind the jobs API (ui → core → data); React only fetches and writes the clipboard.

No established pattern applies to the diagnostic snapshot shape itself.

**New patterns proposed**

none

**Applicable statutes**

* `astral.idioms.require-auth-on-protected-endpoints` — copy payload is a protected jobs route.
* `astral.layers.ui-config-driven-business-logic` — expansion rules and block-type set are resolved in the API/core, not reimplemented in React.
* `astral.layers.import-direction` — UI does not import data or external.
* `astral.standards.no-hardcoded-sets` — block types come from config, not an inline list.
* `astral.standards.debug-contract-gated` — assembler debug lines only when debug is on; contract shape (index headers, `|` detail, long-content truncation).
* `astral.standards.data-raises-caller-logs` — data raises; API returns JSON errors.
* `astral.standards.logging-via-utils` — backend logging through the utils logger.
* `astral.standards.in-scope-only` — Copy chrome and snapshot assembly only; no adjacent modal remediations.
* `astral.standards.dry-and-focused-functions` — reuse existing agent_data read/resolve paths; do not duplicate coat-check or display hydration.
* `astral.standards.no-cross-contamination` — stay in the layered tree.
* `astral.standards.public-then-helpers` — new assembler/API helpers grouped after public entrypoints.
* `astral.standards.names-not-ticket-ids` — domain names, not AST-1419 in symbols.
* `astral.standards.database-header-inventory` — read existing jobs and agent_data only; no new tables.
* `astral.config.config-source-of-truth` — block-type enum from config.
* `astral.ui.frontend-file-placement` — Copy control stays on the existing Job Detail and Recommended Job Report components.
* `astral.ui.naming-conventions` — snake_case jobs route; PascalCase components stay.

## Boundaries

Does not replace Copy Application Email or Copy LinkedIn on the Recommended Job Report — those stay; this is an additional diagnostic Copy.

Does not add Copy to Company Modal, Data Management, Execution History, or error toasts.

Does not change how agent_data is stored — pointer rows stay pointers; this is a read-time snapshot.

Does not change Skip, agent-story tabs, display hydration of artifact pins, or job state transitions.

Does not copy timesheets, dispatch ledger, or the company record.

Does not print or download a file — clipboard only.

## Acceptance criteria

1. Opening a job from In Review or Skipped shows a Copy control on the Job Detail modal. Opening a Recommended job shows the same Copy control on the Recommended Job Report.
2. Clicking Copy puts pretty-printed JSON of the full stored job record on the clipboard.
3. Every agent data id that appeared on the stored job is present in the snapshot as populated blocks covering all configured block types, not as a bare id.
4. For a hop whose agent_data row is a pointer (`ref_agent_data_id` set, local content null), the snapshot shows the referenced content, not null.
5. After a successful copy, the control reads Copied briefly, then Copy again.
6. Skip This Job, existing tabs, Copy Application Email, Copy LinkedIn, and the current job-detail display payload are unchanged.
7. An unauthenticated request for the copy payload is rejected.

## Dependencies and blockers

none

## Open questions

none

## Proposed child tickets

#### 1!: **Job copy snapshot payload - Ada**

Assembles the diagnostic snapshot for one job: full stored record plus populated agent_data for every id on that record, all configured block types, following content pointers so pointer rows are not null in the snapshot. Serves it on an authenticated jobs route. Does not own the modal button.

**Citations:** `pattern.layers.import-discipline`, `astral.idioms.require-auth-on-protected-endpoints`, `astral.layers.ui-config-driven-business-logic`, `astral.layers.import-direction`, `astral.standards.no-hardcoded-sets`, `astral.standards.debug-contract-gated`, `astral.standards.data-raises-caller-logs`, `astral.config.config-source-of-truth`

**Estimate:** 3

#### 2: **Job modal Copy control - Katherine**

Adds the labeled Copy button to the Job Detail modal (In Review and Skipped) and the Recommended Job Report. Fetches the snapshot from #1, writes it to the clipboard, shows Copied feedback. Does not own snapshot assembly. After #1.

**Citations:** `pattern.ui.shared-button-roles`, `astral.ui.frontend-file-placement`, `astral.ui.naming-conventions`, `astral.layers.ui-config-driven-business-logic`

**Estimate:** 2

**New patterns:** none

**Monolith check:** five functional capabilities, two children (payload vs chrome) — split is intentional.

---

## Original brief

Have it copy to clipboard the full content of the job record, AND replace the agent_data_id's with POPULATED (all block_types) from agent_data (not the null value of there's a ref_agent_data_id used), so that I can get all the context for a job to troubleshoot a processing issue.

### Comments

#### susan — 2026-08-17T17:12:19.655Z
Let's do both.

#### chuckles — 2026-08-17T17:07:18.923Z
@susan

1. Should this Copy control also appear on the Recommended Job Report (in addition to Job Detail on In Review / Skipped), or Job Detail only?

---

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/cd1f431953d0a110c5e7d8ca1de8ce45/d8f12059-e2a5-4783-9c4b-6f7ef90bb42d/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/cd1f431953d0a110c5e7d8ca1de8ce45/59f4f484-adce-49c7-90e0-e98f414328ae/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/49329727-082b-47ac-8486-2f1c7fb369ff/store.db` |
| Radia | review | `/home/susan/.cursor/chats/cd1f431953d0a110c5e7d8ca1de8ce45/868f0361-aa65-43f3-bb10-e9fcd194f7ec/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1419 (parent) | ftr/AST-1419-create-a-copy-button-on-the-job-modal |
| AST-1420 | sub/AST-1419/AST-1420-job-copy-snapshot-payload |
| AST-1421 | sub/AST-1419/AST-1421-job-modal-copy-control |

**Epic worktree:** `astral-AST-1419/` — one active sub checked out at a time.
