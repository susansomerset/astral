# AST-373 — Table Data Upsert from JSON

<!-- linear-archive: AST-373 archived 2026-06-03 -->

## Linear archive (AST-373)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-373/table-data-upsert-from-json  
**Status at archive:** Done  
**Project:** Astral Administrator  
**Assignee:** susan  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Database content drifts between environments — admin prompts, candidate records, and anything else Susan maintains in SQLite. Today she can export query results as JSON from Data Management on one server but has no safe way to apply that payload on another. This feature adds a general-purpose, admin-only table upsert on the existing Data Management screen: pick any table, paste Copy Output JSON from a source environment, validate before write, and merge rows into the target without silent data loss.

## Functional scope

* **Replace the Backfill Culture Links block** on Data Management with a new **Table Upsert** section. The ad-hoc SQL query panel and schema browser remain unchanged.
* **Table selector:** A dropdown listing **every user table** in the database (same table list the schema browser uses). The component is table-agnostic — Susan chooses the target table; the feature does not hard-code an allowlist.
* **Update flow:** An **Update** button opens a modal with a large text area. Susan pastes JSON copied from Data Management’s **Copy Output** (the array produced by a `SELECT` on the source server for that same table).
* **Validate-then-apply:** Before any write, parse the JSON and validate the payload against the selected table’s structure (array of objects; column names must match the table; required key columns present; values compatible enough to attempt insert/update). If validation fails, show a clear error and **change nothing**.
* **Primary key required:** Upsert is only offered for tables that declare a primary key (single- or multi-column). Tables without a PK are rejected up front with a clear message — Susan fixes the schema separately (see note on **timesheets** below).
* **Upsert behavior (general):** For each validated row, insert if the row’s primary key is absent in the target, or update the existing row if the primary key matches. Single-column and **composite** primary keys are both supported — match on the full key.
* **Upsert behavior (agent_task exception):** When the selected table is **agent_task**, apply the versioning rules already used by Manage Tasks: unchanged historical rows in the paste are **no-ops**; new or changed content retires the prior active row and inserts a new current version. This is the one table-specific semantic the generic component must honor.
* **Foreign keys — all-or-nothing:** If any row would violate a foreign-key constraint in the target database, **cancel the entire job** and write **zero rows**. Susan fixes parent data or import order and retries.
* **Non-destructive merge:** Rows present in the target database but **not** included in the pasted JSON are left untouched. No table-wide replace, truncate, or delete-by-omission.
* **Feedback:** After submit, show a clear outcome — success with counts (inserted / updated / skipped no-ops) or a specific validation or constraint error. A failed validation or failed apply must not partially corrupt unrelated rows.

## Boundaries

* **Any table, not any SQL:** Susan selects a table and pastes row JSON. No free-form SQL in the upsert path, no multi-table payloads, no arbitrary-table writes in one operation.
* **No export generation:** Susan continues to produce JSON via the existing SQL panel and Copy Output on the source server. This feature does not add export-to-file or repo-tracked snapshots (see [AST-381](https://linear.app/astralcareermatch/issue/AST-381/pushing-database-content-to-github)).
* **No delete/sync-down:** Omitted rows stay in the target DB. Susan handles cleanup manually if needed.
* **No environment automation:** Nothing runs on deploy, bootstrap, or scheduler tick.
* **No diff/diagnostic UI:** Comparison between environments (see [AST-438](https://linear.app/astralcareermatch/issue/AST-438/production-readiness-admin-prompt-and-rubric-diagnostic), done) is out of scope.
* **No PK schema fixes in this ticket:** Adding a primary key to a table that lacks one (e.g. **timesheets**, which today has `anthropic_req_id UNIQUE` but no PK) is out of scope here — Susan addresses that in a separate schema ticket.
* **Must not break:** Existing Data Management SQL execution, schema browser, Manage Agents, Manage Tasks, and runtime prompt resolution.
* **Admin-only:** Same authorization model as other Data Management operations.
* **Susan accepts operational risk:** Porting entity data (e.g. candidates) between environments is intentional; the tool does not enforce business rules beyond schema validation and database constraints.

## Acceptance criteria

 1. The Backfill Culture Links section is removed from Data Management; the Table Upsert section appears in its place.
 2. The table dropdown lists all user tables in the database (not a fixed allowlist).
 3. Clicking **Update** opens a modal with a large JSON text area and a confirm action to apply the upsert.
 4. Malformed JSON, a non-array payload, column mismatches, rows missing required primary-key fields, or a selected table with **no primary key** produce an error message and **zero rows changed**.
 5. For a generic table with a single-column primary key, pasting valid Copy Output JSON upserts all listed rows by primary key; rows not in the JSON remain unchanged.
 6. For a table with a **composite primary key**, upsert matches on the full key set.
 7. For **agent_task**, pasting Copy Output JSON that includes multiple version rows per **task_key** applies new/changed versions using existing Manage Tasks versioning semantics; unchanged historical rows are no-ops.
 8. If any pasted row would fail a foreign-key constraint, the entire operation is cancelled and **zero rows** are written.
 9. Susan can port a candidate (or any other table’s rows) from dev to prod by selecting that table, pasting Copy Output from the source, and seeing the rows merged in the target.
10. On success, Susan sees how many rows were inserted, updated, and skipped as no-ops.

## Dependencies and blockers

None. Data Management, the admin API, and the database schema browser already exist.

## Open questions

None.

---

## Original brief

Right now, the local database has updated admin-level prompt content (not candidate specific), and I need a way to export those prompts to a file that can then be imported in production and synched there so that agent performance is consistent across environments.

Actually, this is VERY SIMPLE, because I'm talking about the agent table and the agent_tasks tables.  There's no magic.

I want to update the Data Management screen to replace the backfill culture links section with a table select dropdown list and a "Update" button that leads to a popup for a large text input, into which I can paste the contents of "Copy Output" json from a select \* statement results from another server (e.g. local), and click "Update" to upsert the content.  Do not delete extant content not included in the JSON (that's easy cleanup and I'd rather not silently lose content.)

### Comments

#### chuckles — 2026-05-24T01:26:13.146Z
## Landed on origin/dev — Chuckles

- `origin/ftr/AST-373-table-data-upsert-from-json` was already merged on local `dev` (prep-uat @ `8c8f581f`); merge step was **Already up to date**
- Pushed `origin/dev` → tip **`5ecb689d`** (18 commits including AST-373 rollup + subsequent local prep-uat work)
- Deleted `origin/ftr/AST-373-table-data-upsert-from-json`
- Moved to **Done** (were PR Ready): **AST-373** (parent), **AST-464** (Ada), **AST-465** (Katherine)

**Engineers — merge before your next skill** (`orientation-astral` § Merge integration line):

```bash
git fetch origin
git checkout dev-<agent>
git merge origin/dev
```

Do **not** rebase `origin/dev` onto `dev-<agent>` unless Susan directs.

— Chuckles

#### chuckles — 2026-05-24T01:00:26.512Z
## UAT Ready — Chuckles

All 2 child branches merged into parent branch and child branches deleted.

Parent branch: `origin/ftr/AST-373-table-data-upsert-from-json` @ `91741763` (Betty rollup) → local `dev` @ `8c8f581f`

Merged in order:
  1. AST-464  Table Data Upsert from JSON — generic upsert data layer and core  (`sub/AST-373/AST-464-…` — deleted)
  2. AST-465  Table Data Upsert from JSON — Data Management UI and admin API  (`sub/AST-373/AST-465-…` — deleted)

Local `dev` already merged (prep-uat §8). **Restart the app** if it is running, then test.

Also fixed duplicate `boards_bp` registration in `src/ui/server.py` (startup crash).

**Engineers — after Susan runs finish-up and pushes `origin/dev`:** merge **`origin/dev`** into your integration branch: `git fetch origin && git checkout dev-<agent> && git merge origin/dev` — do **not** rebase unless Susan directs.

## Manual test steps

**Prerequisites:** Admin session; local `dev` checked out; app restarted (`python3 ./src/ui/server.py` or your usual start). Have Copy Output JSON from another env (or run SELECT on local first).

1. Open **Administrator → Data Management**. Confirm **Backfill Culture Links** is gone and **Table Upsert** appears (table dropdown + **Update** button).
2. Confirm the **ad-hoc SQL panel** and **schema browser** still work (unchanged).
3. **Table dropdown:** lists user tables (not a hard-coded allowlist). Pick **`agent`**.
4. On source (or same DB): run `SELECT * FROM agent` in SQL panel → **Copy Output**. Paste into Table Upsert modal → **Update**. Expect success with insert/update counts; rows merge by PK; rows not in JSON remain.
5. Repeat for **`agent_task`** with Copy Output that includes version history. Unchanged historical rows should be **no-ops**; new/changed content should version per Manage Tasks semantics.
6. **Validation — no writes:** paste malformed JSON → error, zero rows changed.
7. **Validation — no PK:** select **`timesheets`** (no PK) → clear rejection message, zero rows changed.
8. **FK all-or-nothing:** paste rows referencing missing parent FKs → entire job cancelled, zero rows written.
9. **Composite PK** (if you have a suitable table): upsert matches on full key set.
10. Success toast/summary shows inserted / updated / skipped no-op counts.

If testing fails on `dev`:
  `git reset --hard origin/dev`

— Chuckles

#### betty — 2026-05-24T00:53:11.045Z
Prep-uat merge conflict (**`docs/ASTRAL_TEST_BIBLE.md`**) resolved — **Betty**.

**What landed on **`origin/ftr/AST-373-table-data-upsert-from-json`**
1. **`merge(AST-464): integrate child into AST-373`** → **`7191d579`** (child layer integrated; ancestry includes **`3e22dec8`**).
2. **`merge(AST-465): integrate child into AST-373`** → **`91741763306755746b1325ef97737b670fde2d09`** (**`91741763`** short), with bible resolution:
   - **§7.13r:** kept **`origin/sub/.../465`** caveat + skipped-test wording (Betty bible sync lineage).
   - **§7.13u:** one section — **`AST-464`** core rows + **`AST-465`** Data Management / admin API row; heading labels **464 core + 465 UI/API** on parent **AST-373**.
   - **§7.13v AST-419** retained below **§7.13u**.
3. **Push:** **`394fa9bb..91741763`** on **`ftr/AST-373-table-data-upsert-from-json`**.

**Engineer hygiene:** doc-only **`1c5569e4`** on **`origin/sub/AST-373/AST-465-table-data-upsert-from-json-data-management-ui-and-admin-api`** — §7.13u heading matches the unified ftr wording (**`92d11069..1c5569e4`**).

@Chuckles please re-run **prep-uat** for **AST-373**. Sub branches left intact here per Betty scope.

#### chuckles — 2026-05-24T00:49:18.331Z
## do-all-the-things — run complete (resume)

**Parent:** AST-373
**Children:**
- AST-464 — generic upsert — data layer and core — **User Testing** — Ada
- AST-465 — Data Management UI and admin API — **User Testing** — Katherine

### Completed path (this resume)
- Katherine **test-astral** → **Tests Passed** (manifest green, publish tip `724310b9`)
- check-linear passes (all agents)
- Radia **review-astral** AST-465 → **Review Posted** (0 fix-now; doc `c58d18cb`)
- Katherine **resolve-astral** → **User Testing** (HTTP JSON parse advisory; publish `92d11069`)
- Betty **check-linear §5b** cleared earlier `[qa-handoff]` under merge integration line

### Stalled / needs Susan
- **prep-uat AST-373:** merge **AST-465** into parent **`ftr/AST-373-…`** failed — conflict in **`docs/ASTRAL_TEST_BIBLE.md`** after AST-464 merge (local only; origin parent branch not updated; **`sub/*` not deleted**)

### prep-uat
- **Failed** — bible conflict on second child merge. Re-run after Susan/Chuckles resolves and pushes parent branch.

### After finish-up (Susan)
- Engineers **merge** `origin/dev` into `dev-<agent>` per **orientation-astral § Merge integration line** — **not** rebase

### UAT preview (when prep-uat succeeds)
1. Admin → **Data Management** — Backfill Culture Links gone; **Table Upsert** section with table dropdown + **Update** modal
2. Paste Copy Output JSON from source env; confirm inserted/updated/skipped counts or clear error with zero rows changed
3. Try **agent** and **agent_task** tables; confirm agent_task versioning/no-op behavior
4. Confirm SQL panel + schema browser still work

— Chuckles

#### chuckles — 2026-05-24T00:49:13.859Z
prep-uat merge conflict — child branch **AST-465** conflicts with the parent branch after merging **AST-464** (local throwaway worktree only; **origin/ftr/AST-373-table-data-upsert-from-json** unchanged).

Conflict is in: **`docs/ASTRAL_TEST_BIBLE.md`**

@susan — please resolve and push to **`origin/ftr/AST-373-table-data-upsert-from-json`**, then re-run **prep-uat AST-373** or merge **AST-465** sub manually.

Child **`sub/*`** branches were **not** deleted (prep-uat stopped before push).

— Chuckles

#### betty — 2026-05-24T00:45:46.260Z
[check-linear]

- **§0a (`/Users/susan/chuckles/astral-betty`, `dev-betty`):** `git fetch origin` → `git checkout dev-betty` → **`git merge origin/dev`** (**merge integration line**, not rebase — per Susan). Completed cleanly (**already up to date** with `origin/dev`). Prior session’s **`[check-linear] blocked`** was tied to **`git rebase origin/dev`**; integration line today uses **merge** only.
- **Scope:** Parent **AST-373**, project **Astral Administrator**, no extra assigned ids. Full threads **AST-373**, **AST-464**, **AST-465**, plus **AST-374** / **AST-438** (same project hits from **`@betty`** search).
- **§2–§4:** Nothing new that **`@betty`**’s me or expects a Betty reply **after** the latest **`[check-linear]`** / **`Tests updated for [qa-handoff]`** baseline on **AST-465**. **AST-465** is **Tests Passed** (Katherine manifest comment); Katherine’s **`[qa-handoff]`** was already cleared (**Tests updated…** + publish **`724310b9`** in thread).
- **§5b:** **`list_issues`** **Tests Ready** + project **Astral Administrator** → **no rows**; no **`[qa-handoff]`** queue to clear in this session.
- **Tooling:** `list_issues` with **`assignee: me`** errored (**MCP JSON**); inbox used explicit ids + **`@betty`** team search (**51** hits) and this parent/project focus.

#### hedy — 2026-05-24T00:45:33.570Z
[check-linear]

- **§0a** (`/Users/susan/chuckles/astral-hedy`, `dev-hedy`): `git fetch origin` → `git checkout dev-hedy` → `git merge origin/dev` — **Already up to date** (no conflicts).
- **§0b `@hedy`** (`list_issues` **`query: "@hedy"`**, **Team Astral**, **`includeArchived: true`**, paginated): hit set includes **AST-414**, **AST-407**, **AST-453**, **AST-458**, **AST-463** (and related). **Astral Administrator**-scoped repeat of the same query returned **zero** extra rows. **§1** (**assignee = me**, **project: Astral Administrator**): MCP `list_issues` **assignee** filter failed JSON serialization from this client — hand-verified **AST-373** assignee is **Chuckles**; children **AST-464** / **AST-465** are **not** Hedy; **no** Hedy assignee backlog in this project for inbox.
- **§2–§4:** **`list_comments`** on **AST-373**, **AST-464**, **AST-465**, plus the **§0b** union above. **No** thread item that is (a) not by **Hedy**, (b) after the relevant latest **`[check-linear]`** / engineer baseline where applicable, and (c) **`@hedy`** or clearly expects **Hedy**’s reply. Latest **AST-373** note is Chuckles **do-all-the-things** wrap-up (**general** engineer integration wording; **no** `@hedy`).
- **§6:** Not invoking **`plan-astral`**, **`build-astral`**, **`test-astral`**, **`resolve-astral`**, **`qa-astral`**, or **`review-astral`** from this message.

#### chuckles — 2026-05-23T23:52:14.490Z
## do-all-the-things — run complete

**Parent:** AST-373
**Children:**
- AST-464 — generic upsert — data layer and core — **User Testing** — Ada
- AST-465 — Data Management UI and admin API — **Tests Ready** — Betty (reassigned from Katherine after `[qa-handoff]`)

### Completed path
- Dispatch (2 children), branches on origin
- Plans + Chuckles validation → **Plan Approved** (both)
- **AST-464:** build → qa → test → Radia review → resolve → **User Testing**
- **AST-465:** build (after AST-464 sub merge) → qa → scoped tests green; full `run_component_tests.sh` red due to **unrelated** `origin/dev` drift (`test_agent.py` / AST-455 signature mismatch) → **`[qa-handoff]`** to Betty

### Stalled / needs Susan
- **AST-465:** Full component suite fails on integration line — not AST-465 product code. Betty to fix manifest/bible or gate scoped runs; then Katherine **test-astral** → Radia **review-astral** → **User Testing**
- **dev-ada / dev-betty / dev-hedy:** rebase onto `origin/dev` conflicts noted in agent threads (AST-438 doc, `test_agent.py`) — engineers should **rebase** per orientation, not merge

### prep-uat
- **Skipped / failed gate:** AST-465 not **User Testing** — cannot merge `sub/*` → `ftr/AST-373` yet

### After finish-up (Susan)
- Engineers **rebase** `dev-<agent>` onto `origin/dev` per **orientation-astral § Rebase integration line** — **not** `git merge origin/dev`

— Chuckles

#### betty — 2026-05-23T23:38:26.128Z
[check-linear] blocked:

- **§0a (`astral-betty` / `dev-betty`):** `git fetch origin` + `git checkout dev-betty` + `git rebase origin/dev` failed on replay of `63471bc5` (test AST-450): **merge conflict in `tests/component/core/test_agent.py`**. Rebase aborted; branch restored to pre-rebase state.
- **Inbox pass (session project Astral Administrator, parent AST-373):** Read threads on **AST-373**, **AST-464**, **AST-465**, **AST-419**. No new comment `@betty` or direct question to Betty after my prior `[check-linear]` / `[qa-handoff]` baselines that required a thread fix in this pass.
- **Unblock §0a:** Resolve the conflict (or align `dev-betty` with `origin/dev` another way Susan directs), then re-run the integration rebase.

#### katherine — 2026-05-23T23:25:02.983Z
🛑 **AST-465 build preflight (plan § Preflight blocker / execution contract)**

Blocked before any implementation on **AST-465**.

**Checks run**
1. After `git fetch origin`, `origin/dev` has no `src/core/table_copy_upsert.py` and no `apply_copy_output_table_upsert` symbol in the tree.
2. `origin/sub/AST-373/AST-464-table-data-upsert-from-json-generic-upsert-data-layer-and-core` (fetched) has the same `src/core/` layout as baseline — **no** `table_copy_upsert` module; only the **ast-464** plan doc under `docs/features/administrator/` confirms the intended contract.
3. `origin/ftr/AST-373-table-data-upsert-from-json` also has **no** `table_copy_upsert` file.

**Impact**
- **AST-465** Stage 1 cannot add `from src.core.table_copy_upsert import apply_copy_output_table_upsert` — import would fail at runtime and `py_compile` would not create the module.

**What’s needed to proceed**
- Land **AST-464** implementation (the real `table_copy_upsert.py` + exported `apply_copy_output_table_upsert` with the agreed return shape) onto **`origin/dev`** (or explicitly merge the integration line that contains it) so Katherine’s preflight matches the plan excerpt, then re-run **build-astral** for **AST-465**.

**AST-465** stays **Plan Approved**; no branch work started.

#### chuckles — 2026-05-23T23:15:21.941Z
## Dispatch — Chuckles

Dispatched 2 child tickets from the approved definition.

| Ticket | Title | Assigned to | Branch | Blocked by |
|--------|-------|-------------|--------|------------|
| AST-464 | generic upsert — data layer and core | Ada | sub/AST-373/AST-464-table-data-upsert-from-json-generic-upsert-data-layer-and-core | — |
| AST-465 | Data Management UI and admin API | Katherine | sub/AST-373/AST-465-table-data-upsert-from-json-data-management-ui-and-admin-api | AST-464 |

Assignment rationale:
- Ada: data layer + core upsert engine, agent_task versioning, transactional FK handling
- Katherine: AdminDataManagement UI, admin API endpoint, remove backfill culture links
- Hedy: not assigned this dispatch

**Git (authoritative — ignore Linear `gitBranchName`):**
- Parent: `origin/ftr/AST-373-table-data-upsert-from-json`
- Children: `origin/sub/AST-373/AST-464-…`, `origin/sub/AST-373/AST-465-…`

— Chuckles

#### chuckles — 2026-05-23T22:52:10.181Z
All open questions resolved:
- Composite PK → upsert on the **full key**
- No PK → reject up front; schema fix is separate (**timesheets** is the offender today — `anthropic_req_id UNIQUE`, no PRIMARY KEY)
- FK failure → **cancel entire job**, zero rows written

No open questions remain. Ready for your approval — move to **Todo** + assign **Chuckles** when you want dispatch.

— Chuckles

#### chuckles — 2026-05-23T22:39:10.296Z
Scope expanded per your direction:
- Table dropdown lists **all user tables** — generic upsert, not an allowlist
- Validate JSON against selected table schema **before any write**; mismatch = error, zero rows changed
- **agent_task** keeps versioning/no-op semantics; everything else upserts by discovered primary key
- Candidate (and any table) porting dev → prod is explicitly in scope

Three open questions added (composite PKs, tables with no PK, FK failure handling).

— Chuckles

#### chuckles — 2026-05-23T22:34:53.445Z
Updated definition per your versioning note:
- **agent_task** import accepts full Copy Output (including old version rows); unchanged historical rows are **no-ops**
- New/changed content applies via existing Manage Tasks versioning (retire prior active, new row becomes current)
- Success feedback includes skipped no-op count

One open question remains: confirm v1 is **agent** + **agent_task** only.

— Chuckles

#### chuckles — 2026-05-23T22:29:12.720Z
Definition draft ready for review. Key decisions made:
- v1 scope limited to **agent** and **agent_task** upsert via pasted Copy Output JSON; Backfill Culture Links section replaced
- Non-destructive merge only — no deletes for rows omitted from the payload; separate from AST-381 repo snapshot work
- 2 open questions (agent_task versioning semantics on import; confirm no other tables in v1)

Please review the Description and comment with changes or approval.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
