# AST-1340 — Create a table called astral_artifacts

<!-- linear-archive: AST-1340 archived 2026-08-31 -->

## Linear archive (AST-1340)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1340/create-a-table-called-astral-artifacts  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** High / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Operators can lose a carefully authored Base Resume Content blob by clicking Regenerate when they meant Print. Candidate `artifacts.base_resume` alone is not enough as a durable prior copy. This epic adds a versioned `astral_artifacts` store (same current-flag discipline as agent-task edits) and writes the saved `base_resume` artifact into it on Save Base Resume so the last intentional save remains recoverable even if the live candidate blob is overwritten.

## Functional scope

* The product can store versioned artifact rows in a table named `astral_artifacts`, with entity identity (`entity_type`, `entity_id`), `artifact_type`, an artifact blob, a current flag, and the usual row identity / timestamps.
* When an operator successfully saves Base Resume Content for a candidate, the product also records that candidate’s `artifacts.base_resume` payload into `astral_artifacts` as `artifact_type` `base_resume` with `current = 1`, retiring any prior current row for the same entity + artifact type the way agent-task edits do.
* Prior (non-current) rows for that entity + artifact type remain in the table so a saved version is still preserved after a later overwrite of the live candidate artifact.
* This epic does not add UI to browse, restore, or print from `astral_artifacts`; preservation on Save is the deliverable.

## Architectural definition

* **Patterns to reuse** — `pattern.layers.import-discipline` (data-layer table + writers; core orchestrates Save; UI does not call data). No approved catalog pattern yet encodes the agent-task / rubric_vector `current=1` retire-and-insert versioning shape; this epic must follow that established product discipline without inventing a second versioning model.
* **New patterns proposed** — `pattern.data.versioned-current-row` (working name): versioned rows keyed by natural identity with exactly one `current=1` active row per key, retire prior on write, retain history. Proposed because `astral_artifacts` generalizes the agent_task / rubric_vector current-flag approach to entity-scoped artifact blobs. Flag for Archie approval before later epics depend on the catalog id.
* **Applicable statutes** — `astral.standards.database-header-inventory` (new table must appear in `database.py` header inventory); `astral.layers.import-direction` / `astral.layers.core-vs-external-bright-line` (write path stays data/core, not UI→data); `astral.standards.in-scope-only` (Save Base Resume + table only); `astral.standards.data-raises-caller-logs`; `astral.standards.no-cross-contamination`; `astral.docs.features-single-file-per-ticket`.

## Boundaries

* Does **not** wire Print, Regenerate, Generate, or any Artifacts UI to read or restore from `astral_artifacts` (Print remains AST-1314 / AST-1337).
* Does **not** change job-tailored resume / cover / suggested-response persistence, `agent_data`, or rubric_vector.
* Does **not** backfill historical `artifacts.base_resume` values into `astral_artifacts` for candidates who never Save after this ships — preservation starts at the next successful Save Base Resume.
* Does **not** make `astral_artifacts` the live editor source of truth; `candidate_data.artifacts.base_resume` remains what the Base Resume Content page reads and edits.
* Does **not** write `astral_artifacts` on craft hops / Generate / Regenerate — only on Save Base Resume for this epic (table shape may accept other `artifact_type`s later; this epic only wires `base_resume`).
* Must not break existing Base Resume Content save/load or Print-from-saved-content behavior.

## Acceptance criteria

1. Fresh and migrated databases expose an `astral_artifacts` table with entity identity, artifact type, artifact blob, current flag, UUID primary key, and created/updated timestamps, and the table is listed in the data-layer header inventory.
2. After a successful Save Base Resume for a candidate, exactly one `current = 1` row exists for that candidate + `artifact_type` `base_resume`, and its blob matches the saved `artifacts.base_resume` content.
3. A second successful Save for the same candidate retires the previous current row (`current = 0`) and inserts a new `current = 1` row; the retired row remains queryable in the table.
4. Overwriting live `artifacts.base_resume` without going through Save Base Resume (e.g. Regenerate) does not by itself clear or replace the last `current = 1` `astral_artifacts` row from the prior Save.
5. No new Artifacts UI controls are required to demonstrate the above (DB / API-level verification is enough for UAT of this epic).

## Dependencies and blockers

none. Adjacent Print epic AST-1314 / AST-1337 is User Testing and is not a blocker; this epic must not reopen Print wiring.

## Open questions

none

## Proposed child tickets

#### 1!: **astral_artifacts table and current-flag writers - Ada**

Owns creating `astral_artifacts` (ensure/migrate), header inventory update, and data-layer save/read helpers that retire prior `current=1` and insert the new current row for a given entity + artifact type — matching agent-task edit versioning. Does **not** wire Save Base Resume (child 2).
**Citations:** `pattern.layers.import-discipline`; proposed `pattern.data.versioned-current-row`; `astral.standards.database-header-inventory`; `astral.layers.import-direction`; `astral.standards.data-raises-caller-logs`
**Estimate: 5**

#### 2: **Save Base Resume writes base_resume snapshot - Katherine**

Owns calling the child-1 writer from the existing successful Save Base Resume path so `artifacts.base_resume` is recorded with `current = 1` for the candidate. Does **not** add restore/Print UI or change Generate/Regenerate writers. After #1.
**Citations:** `pattern.layers.import-discipline`; `astral.standards.in-scope-only`; `astral.layers.import-direction`
**Estimate: 2**

**New patterns:** Child 1 introduces the versioned current-row shape for `astral_artifacts`; downstream artifact types may reuse it once Archie approves the catalog entry.

**Monolith check:** Functional scope has 4 capability bullets; 2 children split schema/versioning vs Save wire — intentional, not a single mega-ticket.

---

## Original brief

Add a table with entity_type, entity_id, artifact_type, and a blob for the artifact, with a current flag, and the usual UUID, created_at, etc.  
Then, for Save Base Resume, save the artifacts.base_resume artifact type to that table wit the current flag = 1, as we do for editing agent tasks.  No need to wire it into the UI, I just want to know we are preserving it in case the candidate accidentally clicks Regenerate instead of Print.

### Comments

#### susan — 2026-08-14T18:22:11.364Z
\[bug\] So sorry, Chuckles!  I meant for the table to be named "artifacts", not "astral_artifacts" because we don't have that prefix for job or company, etc.

---

_Implementation detail may live in git history on `origin/dev`._
