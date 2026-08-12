# AST-974 — Add a self-reference key to agent_data

<!-- linear-archive: AST-974 archived 2026-08-05 -->

## Linear archive (AST-974)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-974/add-a-self-reference-key-to-agent-data  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-360

### Description

## Purpose

`agent_data` is accumulating identical content blocks — Susan counts **533 rows for system prompts alone**. Each write currently stores a full copy even when the payload already exists. This epic adds a self-reference on `agent_data` so identical `block_data` reuses the **earliest** existing row instead of proliferating full content copies, while every write still leaves a metadata/audit row that SQL can use to trace what was sent.

## Functional scope

1. **Self-reference column.** `agent_data` gains a nullable self-reference key `ref_agent_data_id` that points at another `agent_data` row — the canonical **earliest** match for identical content. On that earliest/canonical row, `ref_agent_data_id` is always null (never self). Cycles and self-refs are rejected.
2. **Dedupe on write (metadata row always).** The write path always creates an `agent_data` row for the write (batch/entity/type/timing audit trail). It creates a **new full content row** only when no existing row has identical `block_data`. When a match exists, the new row stores `ref_agent_data_id` → earliest matching row’s id and does **not** store another full copy of the payload (empty/absent `block_data` on the audit row).
3. **Match key.** Identity for reuse is **exact** `block_data` **only**. `block_type` (and other columns) need not match the canonical row — the audit row may differ from its ref; space savings are the goal.
4. **Transparent read.** Callers that load agent content by id or by batch continue to receive the resolved plain-text content. When a row has `ref_agent_data_id` set, reads follow that reference so consumers do not need to know about dedupe.
5. **Backfill refs only.** A one-time operator-safe pass (dry-run + live) sets `ref_agent_data_id` on existing duplicate rows to their earliest twin. It does **not** clear, null, or delete any stored `block_data`. Susan will reclaim space separately via SQL + vacuum outside this epic.
6. **Debug traceability (backend).** When `debug=True` on touched write/read/backfill paths, log what was **found** (match vs new) and what was **recorded** (new row id and/or resolved canonical id) per step — index headers with universal `index N/M`, primary identifier, and outcome; working detail under `|`; long payloads truncated per the AST-538 / Code Rules contract. No UI debug requirements.

## Boundaries

* Does **not** delete, null out, or purge historical `block_data` (Susan-owned SQL + vacuum; adjacent retention remains **AST-360**).
* Does **not** change `agent_responses` latest-only semantics or entity-row ref arrays beyond continuing to store valid `agent_data` ids.
* Does **not** change BLOCK_TYPES, prompt assembly, or Anthropic call behavior — only how identical content is persisted and resolved.
* Does **not** introduce cross-layer logging in the data layer (data raises; callers log).
* Must not break existing batch/entity retrieval of agent blocks or timesheet/ledger correlation by batch.
* Compression of `block_data` remains a data-layer concern; identity matching is on the logical content callers already treat as plain text (not a second compression contract).

## Acceptance criteria

1. Schema includes nullable `ref_agent_data_id` on `agent_data`, applied via the project’s normal schema-ensure path so existing and new databases gain the column.
2. On every content write, an `agent_data` audit row is created; when identical `block_data` already exists, that row’s `ref_agent_data_id` points at the earliest match and the row does not store a second full content copy.
3. Writing content with no identical match creates a normal content row with `ref_agent_data_id` null.
4. The earliest/canonical content row always has `ref_agent_data_id` null; writes that would create a self-ref or cycle are rejected.
5. Matching for reuse uses exact `block_data` only (block_type may differ between audit row and ref).
6. Reading agent content (by id and by batch) returns the same plain-text payload whether the row holds content directly or references the earliest identical row.
7. Backfill dry-run + live sets refs on existing duplicates to earliest twins and leaves all `block_data` values unchanged.
8. With `debug=True` on touched backend write/read/backfill paths, a scannable per-index trail shows match-vs-new and the ids recorded/resolved; with `debug=False`, no new debug-contract noise.
9. Existing flows that store and later retrieve system/task/response blocks for a batch still succeed end-to-end after the change.

## Dependencies and blockers

none.

## Open questions

none.

## Proposed child tickets

| # | Working title | What it delivers | Agent | Sequencing |
| -- | -- | -- | -- | -- |
| 1 | agent_data self-ref + dedupe write/read | Schema for `ref_agent_data_id`; write always creates audit row; on identical `block_data` sets ref → earliest and omits duplicate payload; read resolves refs; canonical refs stay null; debug found/recorded on touched backend paths. Does **not** own historical backfill (#2). | Ada | — |
| 2 | Backfill ref_agent_data_id on existing duplicates | One-time operator-safe dry-run + live pass that sets `ref_agent_data_id` to earliest twin for duplicate `block_data` rows. Does **not** clear or delete any `block_data`. Does **not** change runtime write/read (#1). | Hedy | after #1 |

**Monolith check:** Functional scope has 6 capabilities; 2 children (runtime + backfill-refs-only) — intentional split so space reclaim stays Susan-owned SQL outside the epic.

**New patterns:** Content-addressed self-reference on `agent_data` (`ref_agent_data_id` → earliest identical block; audit rows may omit payload). Child #1 introduces it; child #2 applies refs to legacy duplicates without content clearing.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-974 (parent) | ftr/AST-974-add-a-self-reference-key-to-agent-data |
| AST-977 | sub/AST-974/AST-977-agent-data-self-ref-dedupe-write-read |
| AST-978 | sub/AST-974/AST-978-backfill-ref-agent-data-id-duplicates |

**Epic worktree:** `astral-AST-974/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | 34ca2e6f-cee1-4e05-8c41-0e82acedbe47 |
| Hedy | engineer | 7a5f3593-4912-43ac-8882-14fb3bebd92d |
| Betty | qa | b1b13c4b-e7a9-465e-92d4-b32df5c80c10 |
| Radia | review | 09d32266-3eef-4910-aa1c-67312e0846e4 |

---

## Original brief

We have 533 records in agent_data for system prompts alone.

Let's create a function that will only create a new record in agent_data when there is not already a record in agent_data where the block_data is identical to the content being stored, and if there is a match found, take the EARLIEST case of that block record and use the record's agent_data_ID to store in a new column called "ref_agent_data_id".

### Comments

#### chuckles — 2026-07-25T19:09:22.955Z
[refresh-ftr] blocked: merge origin/dev into origin/ftr/AST-974-add-a-self-reference-key-to-agent-data

CONFLICT files:
- docs/test-bible/data/database/agent_data.md → @Betty White
- tests/component/data/database/test_agent_data.py → @Betty White

Resolve on ftr (or astral-tests then land to ftr), push origin/ftr/…, Chuckles re-runs refresh-ftr.

— Chuckles

#### chuckles — 2026-07-25T19:07:33.694Z
[merge-child] blocked: AST-978 validate-sub-log
```
BLOCKED: missing plan(AST-978): on origin/sub/AST-974/AST-978-backfill-ref-agent-data-id-duplicates

```
@Hedy Lamarr — rewrite/republish sub clean vs ftr (no Merge remote-tracking branch). — Chuckles

#### chuckles — 2026-07-24T01:13:50.888Z
[merge-child] blocked: AST-977 `origin/sub/AST-974/AST-977-agent-data-self-ref-dedupe-write-read` fails `validate-sub-log` — git pull merges on sub:

- `Merge remote-tracking branch 'origin/dev' into sub/…`
- `Merge remote-tracking branch 'origin/sub/…' into sub/…`

@Ada Lovelace — rewrite/republish sub so the range vs `origin/ftr/AST-974-add-a-self-reference-key-to-agent-data` has no `Merge remote-tracking branch` subjects; keep plan/code/merge-tests/test/docs/resolve sequence. Use `git fetch` + `git merge origin/ftr/…` (not pull). Then Chuckles re-runs merge-child.

— Chuckles

#### chuckles — 2026-07-24T01:07:07.104Z
[datt-trace] **end** spawn=`2e21f6ea` — **DONE** **Radia** role=review `review-child` on `AST-977`
- parent: `AST-974`
- exit: `0` · elapsed: `228s`

— Chuckles

#### chuckles — 2026-07-24T01:03:18.658Z
[datt-trace] **start** spawn=`2e21f6ea` — **IN FLIGHT** spawning **Radia** role=review `review-child` on `AST-977`
- parent: `AST-974`
- AGENT_SESSION: `09d32266-3eef-4910-aa1c-67312e0846e4`

— Chuckles

#### chuckles — 2026-07-24T01:02:47.809Z
[datt-trace] **end** spawn=`b876b21b` — **DONE** **Ada** role=engineer `check-linear` on `AST-977, AST-978`
- parent: `AST-974`
- exit: `0` · elapsed: `20s`

— Chuckles

#### chuckles — 2026-07-24T01:02:26.795Z
[datt-trace] **start** spawn=`b876b21b` — **IN FLIGHT** spawning **Ada** role=engineer `check-linear` on `AST-977, AST-978`
- parent: `AST-974`
- AGENT_SESSION: `34ca2e6f-cee1-4e05-8c41-0e82acedbe47`

— Chuckles

#### chuckles — 2026-07-24T01:02:23.740Z
[datt-trace] **end** spawn=`a147b064` — **DONE** **Betty** role=qa `check-linear` on `AST-977, AST-978`
- parent: `AST-974`
- exit: `0` · elapsed: `129s`

— Chuckles

#### chuckles — 2026-07-24T01:00:13.439Z
[datt-trace] **start** spawn=`a147b064` — **IN FLIGHT** spawning **Betty** role=qa `check-linear` on `AST-977, AST-978`
- parent: `AST-974`
- AGENT_SESSION: `b1b13c4b-e7a9-465e-92d4-b32df5c80c10`

— Chuckles

#### chuckles — 2026-07-24T00:59:28.626Z
[datt-trace] **end** spawn=`28f3a322` — **DONE** **Ada** role=engineer `test-child` on `AST-977`
- parent: `AST-974`
- exit: `0` · elapsed: `68s`

— Chuckles

#### chuckles — 2026-07-24T00:58:19.397Z
[datt-trace] **start** spawn=`28f3a322` — **IN FLIGHT** spawning **Ada** role=engineer `test-child` on `AST-977`
- parent: `AST-974`
- AGENT_SESSION: `34ca2e6f-cee1-4e05-8c41-0e82acedbe47`

— Chuckles

#### chuckles — 2026-07-24T00:19:38.082Z
[datt-trace] **start** spawn=`b4dfa113` — **IN FLIGHT** spawning **Betty** role=qa `qa-child` on `AST-977`
- parent: `AST-974`
- AGENT_SESSION: `b1b13c4b-e7a9-465e-92d4-b32df5c80c10`
- status: agent process starting now (waiting on subprocess)
- Active: set `Betty` on each child, then `agent` + `wait`

— Chuckles

#### chuckles — 2026-07-24T00:15:12.403Z
[datt-trace] **end** spawn=`6fc8c704` — **DONE** **Ada** role=engineer `check-linear` on `AST-977, AST-978`
- parent: `AST-974`
- exit: `0` · elapsed: `27s`
- Active: clear each child after wait

— Chuckles

#### chuckles — 2026-07-24T00:14:44.259Z
[datt-trace] **start** spawn=`6fc8c704` — **IN FLIGHT** spawning **Ada** role=engineer `check-linear` on `AST-977, AST-978`
- parent: `AST-974`
- AGENT_SESSION: `34ca2e6f-cee1-4e05-8c41-0e82acedbe47`
- status: agent process starting now (waiting on subprocess)
- Active: set `Ada` on each child, then `agent` + `wait`

— Chuckles

#### chuckles — 2026-07-24T00:14:33.398Z
[datt-trace] **end** spawn=`c2da35a0` — **DONE** **Joan** role=validate `validate-plan` on `AST-977`
- parent: `AST-974`
- exit: `0` · elapsed: `223s`
- Active: clear each child after wait

— Chuckles

#### chuckles — 2026-07-24T00:07:42.840Z
[datt-trace] **start** — spawning **Joan** role=validate `validate-plan` on `AST-977`
- parent: `AST-974`
- AGENT_SESSION: `2f96bb3a-9e52-4b2a-80a0-b832afadc55f`
- Active: set `Joan` on each child, then `agent` + `wait`

— Chuckles

#### chuckles — 2026-07-24T00:07:25.684Z
[datt-trace] **end** — **Ada** role=engineer `plan-child` on `AST-977`
- parent: `AST-974`
- exit: `127` · elapsed: `?`
- Active: clear each child after wait

— Chuckles

#### chuckles — 2026-07-24T00:04:10.433Z
[datt-trace] **start** — spawning **Ada** role=engineer `plan-child` on `AST-977`
- parent: `AST-974`
- AGENT_SESSION: `34ca2e6f-cee1-4e05-8c41-0e82acedbe47`
- Active: set `Ada` on each child, then `agent` + `wait`

— Chuckles

#### chuckles — 2026-07-23T23:02:31.593Z
@susan

1. Write shape on match: (A) no new row — return/use earliest id only, or (B) metadata/audit row with `ref_agent_data_id` → earliest content and empty/absent `block_data`?
2. Match key: exact `block_data` only, or also same `block_type` (and/or other columns)?
3. Backfill existing duplicates in this epic, or stop new duplication only?
4. Canonical/earliest row: `ref_agent_data_id` always null (never self); reject cycles/self-refs?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
