# AST-981 — Stop writing/reading the standalone agent_responses table

**Linear:** [AST-981 — Stop writing/reading the standalone agent_responses table (Decommission table AGENT_RESPONSES)](https://linear.app/astralcareermatch/issue/AST-981/stop-writingreading-the-standalone-agent-responses-table-decommission)

**Parent:** [AST-975 — Decommission table AGENT_RESPONSES](https://linear.app/astralcareermatch/issue/AST-975/decommission-table-agent-responses) (AC reference only)

**Publish ref:** `origin/sub/AST-975/AST-981-stop-writing-standalone-agent-responses-table`

Removes every runtime and script path that inserts into, selects from, or deletes from the standalone `agent_responses` **table**, without inventing a replacement store. Durable history stays in `agent_data`; latest-per-task entity JSON refs stay via `append_agent_response`. Schema/bootstrap drop is sibling AST-982; docs/bible/test prose is sibling AST-983; entity-column retirement is sibling AST-984.

## UAT fitness

- **AC restored:** Parent AC 2: “A repo-wide search of product code under `src/`, `scripts/`, and `tests/` finds no remaining create/read/write of the standalone `agent_responses` **table** (entity-column name collisions are allowed only if Open question 1 keeps the columns).” Parent AC 3: “Successful `do_task` runs still persist durable history in `agent_data` and still behave correctly for dispatch/UAT without writing the retired table.”
- **Correct outcome:** After a successful `do_task`, `agent_data` RESPONSE/prompt blocks and entity-row latest-only `agent_responses` JSON refs still land; the standalone audit table is never written or read by product/script code.
- **Sibling check:** AST-982 still owns `_ensure_agent_responses_schema` / upsert-registry / CREATE TABLE / hard DROP. AST-983 owns bible/docs/test prose and remaining test mocks of `add_agent_response_entry`. AST-984 owns entity JSON column drop. This plan leaves those intact and only removes table I/O call sites.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Redirecting audit inserts into a new parallel store or into `agent_data` under a different shape would invent replacement persistence the epic forbids. Deleting entity-column `append_agent_response` would break statute `astral.batch.entity-agent-responses-latest-only` and is AST-984’s lane. Dropping CREATE/`_ensure_*` here would steal AST-982.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Remove `add_agent_response_entry` import; delete `_store_agent_response` and every call site | core |
| `src/data/database.py` | Delete `add_agent_response_entry`, `list_agent_responses`, `_derive_agent_status`; remove `DELETE FROM agent_responses` from candidate hard-delete / legacy migrate cascades; keep `_ensure_agent_responses_schema`, compress helpers, entity `append_agent_response`, and upsert-registry entry for AST-982 | data |
| `scripts/migrations/migrate_agent_data.py` | Retire script so it no longer SELECTs/JOINs the standalone `agent_responses` table (exit with clear “retired” message; no table SQL) | scripts |
| `scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py` | Docstring only: drop standalone-table name from “related records” list (no SQL today) | scripts |

**Out of scope (do not touch in this ticket):**

| Item | Owner |
|------|--------|
| `_ensure_agent_responses_schema`, `_UPSERT_*` registry keys, CREATE TABLE, header inventory line for the table | AST-982 |
| Mandate / Code Rules / Test Bible prose; `tests/**` edits | AST-983 / Betty |
| Entity JSON column upserts (`append_agent_response`, roster expand/dedupe) | AST-984 (keep live here) |
| `agent_data` block storage | unchanged |

**Betty note (not engineer commits):** Expect `tests/component/core/test_agent.py` (monkeypatches of `add_agent_response_entry` / `_store_agent_response`) and `tests/component/data/database/test_agent_responses.py` to need update or removal after this lands — engineer does not edit `tests/`.

## Stage 1: Stop core audit writes into the standalone table

**Done when:** `src/core/agent.py` has no import of `add_agent_response_entry`, no `_store_agent_response` function, and no call to either; successful and failure `do_task` paths still call `_store_response_block` / `append_agent_response` as they do today.

1. In `src/core/agent.py`, remove `add_agent_response_entry` from the `from src.data.database import (...)` list.
2. Delete the entire `_store_agent_response` function (Audit logging section, currently ~lines 1627–1654).
3. Delete every call site of `_store_agent_response` in `do_task` (failure path after provider fail; strict-envelope fail; validation fail branches; and the terminal success call after `append_agent_response`). Do not replace those calls with anything — durable storage is already `_store_response_block` + `append_agent_response`.
4. Confirm by search in `src/core/agent.py`: zero matches for `_store_agent_response` and `add_agent_response_entry`.

⚠️ **Decision:** Remove the helper entirely rather than making it a no-op stub. A stub would leave dead API surface and confuse the AST-982/983 sweep; the ticket forbids inventing a replacement store.

## Stage 2: Remove data-layer table insert/list/delete I/O (keep schema ensure)

**Done when:** `src/data/database.py` has no `INSERT INTO agent_responses`, no `SELECT … FROM agent_responses`, and no `DELETE FROM agent_responses`; `_ensure_agent_responses_schema` and its upsert-registry registration remain for AST-982; `append_agent_response` (entity JSON column) is unchanged.

1. In `src/data/database.py`, delete `_derive_agent_status` (only used by `add_agent_response_entry`).
2. Delete `add_agent_response_entry` entirely (function body including `INSERT INTO agent_responses`).
3. Delete `list_agent_responses` entirely (function body including `SELECT * FROM agent_responses`).
4. In candidate hard-delete (`delete_candidate` / equivalent cascade that builds the `for table, sql in (...)` list with an `agent_responses` DELETE), remove that tuple from the loop and remove the `"agent_responses": 0` key from the counts dict. Do not remove entity-table deletes.
5. In `_legacy_candidate_migrate_conn` phase A inline cascade, remove the SQL string `"DELETE FROM agent_responses WHERE entity_type = 'candidate' AND entity_id = ?"`. Leave the other cascade DELETEs.
6. Keep `_compress_payload` / `_decompress_payload` (shared by `agent_data`). Keep `_ensure_agent_responses_schema`, `_agent_responses_schema_ensured`, and the `"agent_responses"` entries in `_UPSERT_SCHEMA_ENSURE_FLAGS` / `_UPSERT_LAZY_SCHEMA_HANDLERS` for AST-982.
7. Leave the module header inventory bullet for `agent_responses` as-is (schema inventory → AST-982). Do not edit entity-column parse/update helpers on company/job/candidate.

⚠️ **Decision:** Leave schema ensure live until AST-982. Removing CREATE/`ensure` here would recreate the table on next upsert/bootstrap gap and steal sibling scope; removing only I/O satisfies “stop writing/reading” while the empty table can still exist until drop.

## Stage 3: Retire scripts that query the standalone table

**Done when:** No file under `scripts/` executes SQL against the standalone `agent_responses` table; `migrate_agent_data.py` cannot be run as a silent partial migrator.

1. In `scripts/migrations/migrate_agent_data.py`, replace runnable migration logic that SELECTs/JOINs `agent_responses` with a retired entrypoint: on CLI / `run_*` invocation, print a one-line message that the standalone-table → `agent_data` migration is retired under AST-981/AST-975 and `sys.exit(2)` (or raise `SystemExit`) **before** any DB open that hits that table. Remove or gut functions whose bodies contain `FROM agent_responses` / `JOIN agent_responses` so a future import cannot accidentally run that SQL. Do **not** rewrite the script to read entity JSON columns as a substitute audit source.
2. In `scripts/migrations/cleanup_duplicate_and_board_gaze_jobs.py` module docstring, change the “Related records (agent_data, agent_responses, …)” sentence to omit the standalone table (e.g. list `agent_data`, timesheets, `dispatch_ledger` only). No code change — that script does not DELETE from the table today.

⚠️ **Decision:** Retire `migrate_agent_data.py` rather than porting it onto entity columns. Parent Open question 2 accepts hard drop of historical standalone rows; durable content already lives in `agent_data`. Porting would invent a new migration path outside this ticket.

## Stage 4: Acceptance search (product/scripts)

**Done when:** The searches below show no remaining standalone-table create/read/write in `src/` or `scripts/` except AST-982-owned schema ensure/CREATE (and comments/docstrings that do not execute SQL). Entity-column identifiers may still appear.

1. From repo root, run (adjust if `rg` unavailable — same patterns):

```bash
rg -n "INSERT INTO agent_responses|DELETE FROM agent_responses|FROM agent_responses|JOIN agent_responses|INTO agent_responses" src scripts --glob '*.py'
rg -n "add_agent_response_entry|list_agent_responses|_store_agent_response|_derive_agent_status" src scripts --glob '*.py'
```

2. Expected: zero matches for insert/delete/from/join/into against the table in executable code; zero matches for the removed function names in `src/` / `scripts/`. Allowed leftovers: `_ensure_agent_responses_schema`, upsert-registry `"agent_responses"` keys, header inventory comment, entity-column `agent_responses` / `append_agent_response` / `dedupe_agent_responses_*`.
3. Manually sanity-check that `do_task` success path still contains `_store_response_block` and `append_agent_response` calls (entity + `agent_data` contract intact).

## Self-Assessment

**Scope:** Single-Component — core audit call removal plus data-layer table I/O deletion and one retired migration script; schema ensure and entity-column contract untouched.

**Conf:** high — call sites are localized (`_store_agent_response` → `add_agent_response_entry`; `list_agent_responses` only used from tests; candidate cascades are explicit SQL strings); sibling boundaries are named in the parent dispatch table.

**Risk:** Medium — forgetting a `_store_agent_response` branch or a cascade DELETE would leave silent table writes; removing `append_agent_response` by mistake would break latest-only entity refs. Mitigated by Stage 4 rg gates and explicit keep-list for entity helpers.

## Code Rules check

- §2.4.1 / `astral.batch.entity-agent-responses-latest-only`: preserved — `append_agent_response` and entity JSON columns stay.
- §2.4 batch / `agent_data`: unchanged — RESPONSE blocks remain the durable store.
- §1.3 DRY: delete duplicate audit path rather than wrapping it.
- §3.3 imports: remove unused `add_agent_response_entry` import with the call sites.
- §2.1 config: no new config keys.
- Layers: core stops calling data audit insert; data stops exposing table I/O; no UI changes.

## Review (build stub)

**Built:** `origin/sub/AST-975/AST-981-stop-writing-standalone-agent-responses-table` @ `24ecb0c`.

**Stages delivered:**
- Stage 1: `src/core/agent.py` — removed `add_agent_response_entry` import, `_store_agent_response`, and all call sites; `_store_response_block` + `append_agent_response` remain — `24ecb0c`.
- Stage 2: `src/data/database.py` — deleted `_derive_agent_status` / `add_agent_response_entry` / `list_agent_responses` and candidate cascade `DELETE`s against the standalone table; kept `_ensure_agent_responses_schema` + upsert registry + `append_agent_response` — `24ecb0c`.
- Stage 3: retired `scripts/migrations/migrate_agent_data.py` (exit 2 / SystemExit); docstring cleanup on `cleanup_duplicate_and_board_gaze_jobs.py` — `24ecb0c`.
- Stage 4: acceptance rg clean for table SQL + removed symbols in `src/`/`scripts/` (header inventory comment left for AST-982).

**Betty:** at **Code Complete** — update/remove `add_agent_response_entry` / `_store_agent_response` mocks in `tests/component/core/test_agent.py` and standalone-table cases in `tests/component/data/database/test_agent_responses.py`; keep entity-column `append_agent_response` coverage until AST-984.

## Radia review (code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-981
**Publish ref tip (pre-docs):** `0daf9ad024a532b75d8c4f613a880c4e5700f390`
**Overall:** DISCUSS

### What’s solid

- Stage 1–3 match the plan: `_store_agent_response` / `add_agent_response_entry` / `list_agent_responses` removed; candidate cascade `DELETE FROM agent_responses` gone; `migrate_agent_data.py` hard-retired (exit 2 / SystemExit) with no table SQL left.
- Durable path intact: `_store_response_block` + `append_agent_response` still on `do_task` success; `_ensure_agent_responses_schema` + upsert registry left for AST-982.
- Stage 4 rg on tip: no `INSERT`/`DELETE`/`FROM`/`JOIN`/`INTO agent_responses` executable table I/O under `src/`/`scripts/` (entity-column name collisions remain by design).
- Betty: one `test(AST-981)` + one `merge-tests(AST-981)` SHA; bible/tests updated without touching `src/` or plan features from Betty’s commit.

### Issues

**discuss (C4 straggler):** Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban` at plan time; this code sweep scores them in-scope on the three-dot diff (`docs/features/**`, `tests/**` / `docs/test-bible/**`). Substance: all three **conform** (plan doc is not a misplaced spike; single features file; engineer `code()` did not touch tests — Betty owns test tree). No product fix required; note for resolve-child acknowledgment.

**advisory:** Header inventory line still says `insert-only from add_agent_response_entry` — plan Stage 2/4 left inventory for AST-982; stale helper name in comment only.

### Recommended actions

1. Implementer: acknowledge the three C4 straggler **discuss** rows (no code change expected).
2. AST-982: drop ensure/CREATE/header inventory for the standalone table.
3. AST-983: broader mandate/bible prose sweep beyond Betty’s targeted bible updates here.

### Pattern conformance

none cited

### Plan adherence

Diff footprint matches Self-Assessment Scope (Single-Component) and sibling boundaries (no schema drop, no entity-column retirement, no invented replacement store). Stages 1–4 delivered; Betty coverage lands on publish-ref tip.

## Resolution

**Date:** 2026-07-25  
**Review tip:** `abb6972` (`docs(AST-981): Radia review — findings`)  
**Outcome:** DISCUSS → acknowledged; no fix-now; advancing to User Testing.

### Discuss (C4 straggler) — acknowledged

Radia flagged that Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` at plan time, while the code-rubric three-dot sweep scores them in-scope because the tip includes `docs/features/**`, `tests/**`, and `docs/test-bible/**`. Substance verdicts remain **conforms** for all three:

- Plan doc is a real features file (not a misplaced spike).
- Single features file for AST-981.
- Engineer `code(AST-981)` did not touch the test tree; Betty owns tests/bible via `test()` / `merge-tests`.

No product change for these discuss rows.

### Advisory — acknowledged (sibling owns)

Header inventory still names `add_agent_response_entry` — left for **AST-982** per plan Stage 2/4 (schema/ensure/header cleanup). Broader mandate/bible prose remains **AST-983**.

