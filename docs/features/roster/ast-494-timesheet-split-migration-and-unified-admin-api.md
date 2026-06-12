# AST-494 — Timesheet split, migration, and unified admin API

**Parent:** [AST-491 — Support other ai models: DeepSeek](https://linear.app/astralcareermatch/issue/AST-491/support-other-ai-models-deepseek)  
**Depends on:** [AST-493](https://linear.app/astralcareermatch/issue/AST-493/deepseek-client-and-provider-dispatch-routing-support-other-ai-models) (`record_timesheet` payload shape aligned with token fields)  
**Publish ref (origin):** `sub/AST-491/AST-494-timesheet-split-migration-and-unified-admin-api`  
**Ticket:** [AST-494](https://linear.app/astralcareermatch/issue/AST-494/timesheet-split-migration-and-unified-admin-api-support-other-ai-models)

Renames persisted Anthropic ledger table **`timesheets` → `anthropic_timesheets`** (column **`anthropic_req_id` UNIQUE** unchanged). Adds **`agent_timesheets`**, same columns except **`anthropic_req_id` renamed to `agent_req_id`** (still UNIQUE per call id). Migrates historical rows once: **`INSERT INTO agent_timesheets SELECT ...`** mapping **`anthropic_req_id AS agent_req_id`**, preserving all other columns. New writes dual-path: every Anthropic-completion row inserts **`agent_timesheets`** plus a mirror **`INSERT` into `anthropic_timesheets`** (same payloads) so Anthropic retains a dedicated ledger; DeepSeek completions insert **`agent_timesheets` only**.

Updates **`database._add_timesheet_entry`** signature kwargs to **`agent_req_id`** (stop using **`anthropic_req_id`** in Python kwargs). **`core/timesheets.record_timesheet_entry`** gains **`provider: str`** (**`"anthropic"`** or **`"deepseek"`**), literal strings defined once in **`config.py`** (**`ALLOWED_TIMESHEET_PROVIDERS` tuple**) to avoid magic duplication. **`src/external/anthropic.py`** and **`src/external/deepseek.py`** call **`record_timesheet_entry`** with **`agent_req_id=response.id`** and **`provider`** set appropriately. Admin **`list_timesheets` / CSV / export`** and **`AdminAgentTimesheets.tsx`** pivot primary key **`idField`** plus column metadata from **`anthropic_req_id`** to **`agent_req_id`**.

Audits **`scripts/migrations/migrate_agent_data.py`**: replaces joins against **`timesheets`** with **`agent_timesheets`** keyed by **`agent_req_id`** (or **`anthropic_timesheets`** only where script semantics are Anthropic-only — read script header and pick one deterministic rule; attach note in Linear if ambiguous).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Tuple `ALLOWED_TIMESHEET_PROVIDERS = ("anthropic", "deepseek")` (exact strings reused by data layer validators). | utils |
| `src/data/database.py` | Migrate/rename **`timesheets` → `anthropic_timesheets`** when legacy name exists. Create **`agent_timesheets`** DDL mirroring **`anthropic_timesheets`** with **`agent_req_id`**. One-time **`INSERT`** from **`anthropic_timesheets`**. Implement **`_add_timesheet_entry`**: validates provider against config tuple; **`INSERT`** into **`agent_timesheets`** always; second **`INSERT` into `anthropic_timesheets`** only when **`provider == "anthropic"`**. Rewrite **`list_timesheets`** **`FROM agent_timesheets`**. Refresh module header inventory (two ledger tables). | data |
| `src/core/timesheets.py` | Thread **`provider`** into **`_add_timesheet_entry`**. | core |
| `src/external/anthropic.py` | Timesheet kwargs: **`agent_req_id`**, pass **`provider="anthropic"`** via **`record_timesheet_entry`** (or direct kwargs mirroring shim). | external |
| `src/external/deepseek.py` | Same with **`provider="deepseek"`**. | external |
| `src/ui/api/api_admin.py` | `_TIMESHEET_COLUMNS`, filters, CSV header keys: **`agent_req_id`** instead of **`anthropic_req_id`**. | ui |
| `src/ui/frontend/src/pages/AdminAgentTimesheets.tsx` | Types, `idField`, column defs for unified store. | ui |
| `scripts/migrations/migrate_agent_data.py` | SQL table/column rename fallout. | scripts |
| `tests/component/data/database/test_timesheets.py` | Migration assertions + dual-write. | tests |
| `tests/component/core/test_timesheets.py` | Provider routing. | tests |
| `tests/component/ui/api/test_api_admin.py` | Response shape uses `agent_req_id`. | tests |
| `tests/component/frontend/pages/test_AdminAgentTimesheets.test.tsx` | Fixtures use `agent_req_id`. | tests |

## Stage 1: Schema migration (idempotent)

**Done when:** Fresh DB obtains both tables without legacy **`timesheets`** name; upgrading DB retains row counts (**`COUNT(*)` parity pre/post**) for Anthropic ledger.

1. **`ALTER TABLE timesheets RENAME TO anthropic_timesheets`** guarded by PRAGMA (only if **`timesheets` exists AND **`anthropic_timesheets` absent**).

2. Create **`agent_timesheets`** explicitly (no **`CREATE TABLE AS SELECT`** — preserve indexes/UNIQUE). Column order parity with **`anthropic_timesheets`** minus rename.

3. Backfill **`INSERT OR IGNORE`** from **`anthropic_timesheets`** if **`agent_timesheets` empty**.

## Stage 2: Write pipeline

**Done when:** Mocked anthropic **`record`** yields two SQLite rows identical except table name/id column key; mocked deepseek yields one **`agent_timesheets`** row only.

1. Implement **`database._add_timesheet_entry(agent_req_id, ..., provider)`** branching.

2. Update **`external`** modules to renamed kwargs + provider literal.

## Stage 3: Read/export surfaces

**Done when:** Admin UI lists unified rows spanning historical Anthropic IDs and DeepSeek IDs; CSV export aligns.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — Migrates persisted finance data and public admin API shapes.

**Conf:** `Medium` — SQLite migration ordering + UNIQUE constraints demand careful pragma checks.

**Risk:** `HIGH` — Botched migrate drops **`UNIQUE`** or duplicates rows silently.

## Self-review vs ASTRAL_CODE_RULES

- §1.1: Header inventory describes both **`anthropic_timesheets`** & **`agent_timesheets`** exclusively (no orphaned **`timesheets`**).
- §2.1 Provider literals enumerated in **`config`** (no inline sets sprinkled).
- §3.2 UI consumes API field rename only — no duplicated provider logic in React.

## Execution contract

Plan commits **`docs(AST-494): ...`** cherry-picked to `origin/sub/AST-491/AST-494-timesheet-split-migration-and-unified-admin-api` via detached `/tmp`.

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-491/AST-494-timesheet-split-migration-and-unified-admin-api`  
**feat(AST-494) ledger (original ship):** `56a56f68` (**anthropic_timesheets + agent_timesheets, migrate, unified admin/query**)  
**Prerequisite merged:** AST-493 @ `818cb1c0` (DeepSeek client + routing + `_add_timesheet_entry` semantics)  
**Integration patch:** `0f937208` (**boards admin API parity** with `dev-ada`)

## Review

**Reviewer:** Radia. **Diff:** `origin/dev`…[`origin/sub/AST-491/AST-494-timesheet-split-migration-and-unified-admin-api`](https://github.com/susansomerset/astral/tree/sub/AST-491/AST-494-timesheet-split-migration-and-unified-admin-api). **Code tip:** `e389376d8f5fa7e01322a73d629100bbf025d434`.

### What's solid

- Ledger split matches parent intent: rename legacy `timesheets` → `anthropic_timesheets`, add `agent_timesheets` with `agent_req_id`, backfill, dual-write on Anthropic, single-write on DeepSeek.
- Reads (`list_timesheets`, batch cost aggregation, admin/API + `AdminAgentTimesheets.tsx`) pivot through the unified table and renamed id field consistently with plan.
- Provider literal validation via `ALLOWED_TIMESHEET_PROVIDERS` avoids magic strings scattered outside config.

### Issues / notes

| Severity | Topic | Location | Note |
|----------|-------|----------|------|
| advisory | Migration hygiene | `_ensure_timesheets_schema` | Happy path guarded; worth a quick COUNT sanity check after first prod migrate (historical parity) — already implicit in QA. |

### Recommended actions

| Priority | Action |
|----------|--------|
| None | — |

## Resolution — 2026-05-26

- Radia **`review-astral`**: **advisory** only (post-migrate row-count sanity); **no fix-now** or **discuss**. Product and Betty’s timesheet manifests already cover parity and **`agent_req_id`** contract. Ops note retained for first production migrate. Publish tip **`e389376d8f5fa7e01322a73d629100bbf025d434`** on **`origin/sub/AST-491/AST-494-timesheet-split-migration-and-unified-admin-api`**.
- **§9a** dry-runs vs **`origin/dev`** and **`origin/ftr/AST-491-support-other-ai-models-deepseek`** clean before **`User Testing`**.

