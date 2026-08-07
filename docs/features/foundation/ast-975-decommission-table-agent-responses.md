# AST-975 — Decommission table AGENT_RESPONSES

<!-- linear-archive: AST-975 archived 2026-08-05 -->

## Linear archive (AST-975)

**Archived:** 2026-08-05  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-975/decommission-table-agent-responses  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

The product still maintains a standalone `agent_responses` **table** that duplicates content already stored in `agent_data` (and already indexed lightly on entity rows). That table adds schema surface, write paths, and confusion with the similarly named entity-table JSON columns — without being the live contract for latest-per-task references. This epic retires the **table** and every product/script/test reference to it so Astral has one clear persistence story for agent outputs.

## Functional scope

1. **Retire the standalone** `agent_responses` **table.** The database no longer creates, migrates, or inventories that table. Existing environments drop it on upgrade so production and local DBs match the canonical inventory.
2. **Remove all runtime and script usage of that table.** No core, data, UI, or maintenance path inserts into or reads from the standalone table after this epic. Call sites that only existed to feed the table are removed (not redirected into a new parallel store).
3. **Sweep references outside runtime.** Config comments, Code Rules / mandate prose that still treat the standalone table as live inventory, component/integration tests, and Test Bible language that assume the table exists are updated so they describe the surviving contract only.
4. **Entity-column decision (gated).** If Susan confirms in Open questions that entity-table `agent_responses` JSON columns on job / company / candidate should also go away, this epic includes dropping those columns and retiring every path that reads or upserts them — **only after** the Code Rules / statute that currently require latest-only entity refs are revised. If Susan keeps the columns, this epic leaves them and the latest-only upsert contract untouched.

## Boundaries

* Does **not** change `agent_data` block storage, compression, or the RESPONSE block type — that remains the durable prompt/response history.
* Does **not** implement [AST-974](https://linear.app/astralcareermatch/issue/AST-974/add-a-self-reference-key-to-agent-data) (`agent_data` self-reference / dedupe); that sibling may land independently.
* Does **not** invent a replacement audit table for the retired standalone table.
* Does **not** silently drop entity `agent_responses` columns while Code Rules §2.4.1 / statute `astral.batch.entity-agent-responses-latest-only` still mandate latest-only refs on entity rows — column removal requires Susan’s explicit answer and a mandate update.
* Does **not** reopen or edit Backlog sibling history (e.g. older duplicate-content tickets); this Discussion parent is the delivery vehicle.
* Must **not** break batch locking, `do_task` success paths, or any UI/API that today reads entity-row `agent_responses` refs into `agent_data` — unless Susan chooses column retirement and the mandate is updated first.

## Acceptance criteria

1. After deploy/bootstrap on a legacy DB that still had the standalone `agent_responses` table, that table is gone and is not recreated on subsequent starts.
2. A repo-wide search of product code under `src/`, `scripts/`, and `tests/` finds no remaining create/read/write of the standalone `agent_responses` **table** (entity-column name collisions are allowed only if Open question 1 keeps the columns).
3. Successful `do_task` runs still persist durable history in `agent_data` and still behave correctly for dispatch/UAT without writing the retired table.
4. Mandate docs and Test Bible text no longer list the standalone `agent_responses` table as live inventory; if entity columns remain, prose clearly distinguishes **table (retired)** vs **entity JSON column (live)**.
5. If Open question 1 answers “drop columns too”: entity tables no longer have `agent_responses` columns, no code path reads/writes them, and Code Rules / the latest-only statute are updated to match — and UAT confirms latest-per-task lookup still works via the approved replacement (or is explicitly retired).
6. If Open question 1 answers “keep columns”: entity latest-only upserts and lookups continue to work unchanged after the table is gone.

## Dependencies and blockers

* none for table decommission alone.
* Adjacent (not blocking): [AST-974](https://linear.app/astralcareermatch/issue/AST-974) — `agent_data` self-reference; share the same storage area but do not need to ship together.
* Historical note (not a Linear blocker): [AST-589](https://linear.app/astralcareermatch/issue/AST-589) was marked Duplicate for “unused” entity fields; current Code Rules still use entity-column `agent_responses` as latest-only refs — treat that Duplicate as superseded context, not permission to drop columns without answering Open question 1.

## Open questions

1. **Table only vs columns too:** Confirm this epic retires the standalone `agent_responses` **table** only and **keeps** the `agent_responses` JSON columns on job / company / candidate (current Code Rules §2.4.1 latest-only refs into `agent_data`). Or should we also drop those entity columns in this epic (requires Code Rules + statute revision and an explicit answer for how latest-per-task lookup works afterward)?
   1. If we can remove the empty columns as a separate child record, let's do it.  It's confusing to have them persist.
2. **Historical table rows:** Is a hard drop of any existing standalone-table rows acceptable (no export/archive), given durable content already lives in `agent_data`?
   1. Yes, hard drop.

## Proposed child tickets

Monolith check: Functional scope has 4 capabilities; children 1–3 cover the table path; child 4 only activates if Open question 1 chooses column retirement.

| # | Working title | What it delivers | Agent | Sequencing |
| -- | -- | -- | -- | -- |
| 1 | Stop writing/reading the standalone table | Removes all runtime/script call sites that insert into or query the standalone `agent_responses` table. Leaves entity-column latest-only behavior alone. Does not own schema drop. | Ada | — |
| 2 | Drop table from schema and existing DBs | Removes the table from the data-layer inventory/bootstrap/ensure path and drops it on upgrade so local and Railway DBs match. Does not own docs/test prose. | Hedy | after #1 |
| 3 | Docs, bible, and test sweep for table retirement | Updates mandate/config comments and tests so nothing still assumes the standalone table exists; keeps entity-column contract language accurate per Open question 1. | Katherine | after #2 |
| 4 | (Optional) Retire entity `agent_responses` columns | Only if Open question 1 says yes: drop columns on job/company/candidate, remove upsert/read paths, and update Code Rules + latest-only statute to the replacement contract. Explicitly does not ship if Susan keeps the columns. | Ada | after #3, only if OQ1 = drop columns |

**New patterns:** none expected for the table-only path. Column retirement (child #4) would introduce a mandate change — name the replacement lookup contract in the plan if activated.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| [AST-975](https://linear.app/astralcareermatch/issue/AST-975/decommission-table-agent-responses) (parent) | ftr/AST-975-decommission-table-agent-responses |
| [AST-981](https://linear.app/astralcareermatch/issue/AST-981/stop-writingreading-the-standalone-agent-responses-table-decommission) | sub/AST-975/AST-981-stop-writing-standalone-agent-responses-table |
| [AST-982](https://linear.app/astralcareermatch/issue/AST-982/drop-agent-responses-table-from-schema-and-existing-dbs-decommission) | sub/AST-975/AST-982-drop-agent-responses-table-schema |
| [AST-983](https://linear.app/astralcareermatch/issue/AST-983/docs-bible-and-test-sweep-for-agent-responses-table-retirement) | sub/AST-975/AST-983-docs-bible-test-sweep-agent-responses |
| [AST-984](https://linear.app/astralcareermatch/issue/AST-984/retire-entity-agent-responses-columns-decommission-table-agent) | sub/AST-975/AST-984-retire-entity-agent-responses-columns |

**Epic worktree:** `astral-AST-975/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | 2453fb79-ed7b-4e3c-9340-6c6675502c0d |
| Hedy | engineer | 5378bd76-d78d-49e0-b289-b79cfe8106b0 |
| Katherine | engineer | 14584d6b-d4e7-4940-99eb-1a2911b4d6fa |
| Betty | qa | ef073efe-4aa7-449f-9967-c0ce6a794056 |
| Radia | review | 15256be1-620f-4f70-933f-f3bebafecb10 |

---

## Original brief

Remove this table and all references to it in the code from the root directory, including scripts, tests, and src.

If possible, drop the columns agent_responses from the entity tables (job, company, candidate) where necessary.

### Comments

#### chuckles — 2026-07-28T01:09:01.600Z
[fix-uat] UAT fixes landed — ready for re-test

_No UAT bug children listed — prep-uat merge only._

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### chuckles — 2026-07-28T01:09:00.044Z
[fix-uat] No UAT bugs to file — wrong-ticket note withdrawn.

### Local UAT steps (AST-975)

**0. Staging / local tip**
- Local `dev` (and Railway staging) should include the prep-uat land for this epic.

**1. Standalone table gone (AC1)**
```sql
SELECT to_regclass('public.agent_responses');
-- expect NULL
```
On a DB that still had the table before upgrade: start the app / run bootstrap once, then re-check — table must not recreate.

**2. No leftover table I/O (AC2)**
From repo root on current `dev`:
```bash
rg -n "agent_responses" src scripts tests --glob '!**/test_bible/**'
```
Expect: no create/read/write of a standalone **table** named `agent_responses`. Entity-column language should already be retired (AST-984); latest refs use `list_entity_latest_agent_refs` / `agent_data.entity_id`.

**3. Durable history still works (AC3)**
Run one successful `do_task` / batch path you already use in UAT. Confirm a new RESPONSE (or equivalent) lands in `agent_data` and dispatch/UI still behaves — without any write to a standalone `agent_responses` table.

**4. Docs / bible (AC4)**
Spot-check Test Bible / mandate prose: standalone table described as **retired**, not live inventory.

**5. Entity columns + replacement lookup (AC5)**
```sql
SELECT column_name FROM information_schema.columns
WHERE table_name IN ('job','company','candidate')
  AND column_name = 'agent_responses';
-- expect 0 rows
```
Then confirm latest-per-task still works in the UI/API path that used to read those columns (via `list_entity_latest_agent_refs` / `agent_data.entity_id`).

**Out of scope here:** `ref_agent_data_id` fill rates → [AST-974](https://linear.app/astralcareermatch/issue/AST-974).

— Chuckles

#### susan — 2026-07-28T00:29:57.278Z
@chuckles Sorry, you're right.  I was commenting on the wrong ticket.

What are the test steps for this bug on local?

#### chuckles — 2026-07-28T00:28:56.604Z
[fix-uat] open question — @susan

Your note (`select count(*) from agent_data where ref_agent_data_id is not null` → 8 / 7703; suspected backfill script bug) is about **`ref_agent_data_id` / self-ref population**.

AST-975 boundaries say this epic does **not** implement [AST-974](https://linear.app/astralcareermatch/issue/AST-974) (`agent_data` self-reference / dedupe). None of AST-975’s acceptance criteria cover `ref_agent_data_id` fill rates.

Should I:
1. Treat this as **out of scope for AST-975** and move/file it under **AST-974**, or
2. Expand AST-975 AC to own the backfill script fix anyway?

Not filing a UAT bug under AST-975 until you pick.

— Chuckles

#### susan — 2026-07-28T00:28:01.296Z
@chuckles When I ran `select count(*) from agent_data where ref_agent_data_id is not null`, I got a count of 8 out of 7703.  I think the script to update the ref_agent_data_id has a bug in it.

#### chuckles — 2026-07-28T00:21:30.425Z
[refresh-ftr] blocked: attempt 1 — CONFLICT files:
- `docs/test-bible/README.md` → @Betty White
- `src/core/agent.py` → @Ada Lovelace
- `src/data/database.py` → @Ada Lovelace

Reconciling `origin/dev` into `origin/ftr/AST-975-decommission-table-agent-responses`. Push resolve to that ftr ref.

— Chuckles

#### chuckles — 2026-07-28T00:09:10.993Z
[datt] Betty Team thread rotated — prior `05d03d30-…` every `--resume` hit provider ActionRequiredError (cyber content). New Betty qa Thread `3aaf5baf-c2f7-4883-b6fa-dbddf298ebfc` (first-spawn qa AST-984).

— Chuckles

#### chuckles — 2026-07-27T23:15:00.424Z
[check-linear] In Progress — statute gate waived; best judgment on entity-column / hard-drop path

#### susan — 2026-07-27T21:33:27.906Z
@chuckles This ticket will be outside the scope of the statutes.  Please use best judgment.

#### chuckles — 2026-07-25T19:58:36.956Z
@susan AST-984 build paused at Archie statute gate (keep-id vs supersede for `astral.batch.entity-agent-responses-latest-only` / entity-column retirement). Draft on the child. AST-981–983 are User Testing on ftr; resume datt after you approve the statute path.

— Chuckles

#### chuckles — 2026-07-23T23:09:50.318Z
@susan

1. Table only (keep entity `agent_responses` JSON columns + latest-only statute), or drop those columns in this epic too (needs Code Rules/statute revision + how latest-per-task lookup works after)?
2. Hard-drop existing standalone-table rows OK (no archive), since durable content is in `agent_data`?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
