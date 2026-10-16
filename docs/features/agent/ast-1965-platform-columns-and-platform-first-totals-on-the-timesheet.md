<!-- linear-archive: AST-1965 archived 2026-10-08 -->

## Linear archive (AST-1965)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1965/platform-columns-and-platform-first-totals-on-the-timesheet-query-llm  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1963 — Query LLM Platform for Timesheet Data to Finish Batch  
**Blocked by / blocks / related:** parent: AST-1963; blocks: AST-1966

### Description

## What this implements

Adds the platform columns to `agent_timesheets` and their writer, lets unpriced SKUs be recorded, and makes `sum_cost_by_batch` prefer platform cost. Does **not** call OpenRouter (#1) or start reconciles (#3).

## Citations

`patt.entity.batch-processing`.

## Scope

* `src/data/database.py` — **modified**. Platform columns on `agent_timesheets`, a writer for them, `_add_timesheet_entry` accepts an unpriced SKU, `sum_cost_by_batch` prefers platform cost.
  * **New columns** on `agent_timesheets` — platform cost (nullable; null = not reconciled), native prompt / completion / cached / reasoning token counts, serving host, reconcile timestamp. Added by `_ensure_timesheets_schema` for existing databases and by `_create_agent_timesheets_table` for new ones.
  * **New writer** — sets one row's platform columns by `agent_req_id`.
  * **Modified function** `_add_timesheet_entry` — no longer refuses a SKU the catalog doesn't price (the server id check stays).
  * **Modified function** `sum_cost_by_batch` — per row, platform cost when present, else the sum of `calc_cost_*`.
* `tests/component/data/database/test_timesheets.py`, `docs/test-bible/data/database/timesheets.md` — **modified**.

## Acceptance criteria

"Stubbed lookup" = the component-test stub of the OpenRouter generation-stats HTTP call.

3. **Unpriced calls still get a row.**
   * **Check (**`test_llm_compat.py`**):** with catalog pricing stubbed to raise, a successful call invokes `record_timesheet` once, with `calc_cost_*` all 0 and the response's token counts. (`test_timesheets.py`, database): `_add_timesheet_entry` with a SKU the catalog doesn't price returns `True` and the row exists.
   * **Fails if:** `record_timesheet` isn't called, or the insert is refused.
   * **This child:** the `_add_timesheet_entry` half (database test). The `llm_compat` half is #3.
4. **Calculated cost is never overwritten.**
   * **Check (database test):** after the platform writer runs, the row's four `calc_cost_*` and existing token columns equal what was inserted, and the platform cost, native counts, host and timestamp equal what was written.
   * **Fails if:** any original column changed or a platform column is null.
5. **Platform cost wins in the total.**
   * **Check (database test):** a batch with two rows, one reconciled (calc 0.01, platform 0.03) and one not (calc 0.02): `sum_cost_by_batch([batch])` returns `0.05`.
   * **Fails if:** it returns 0.03 (calc only) or anything other than 0.05.

## Boundaries

* Does **not** call OpenRouter (#1 Model routing type and lookup - Hedy) or start reconciles / refresh the ledger (#3 Background reconcile - Ada).
* Does **not** change `calc_cost_*` math or `backfill_agent_timesheet_costs`.

## Notes for planning

* Cite `patt.entity.batch-processing` — parent Architectural definition has the links.
* Platform facts (parent § Platform research): OpenRouter `GET /api/v1/generation?id=<gen-id>`, bearer key; `total_cost`, `native_tokens_prompt` / `_completion` / `_cached` / `_reasoning`, `provider_name`; stats can lag the response by a few seconds.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### radia — 2026-10-04T02:28:09.782Z
[code-rubric] PROCEED (Commit: 7470f49c9) platform columns and totals

#### betty — 2026-10-04T02:25:43.629Z
`origin/sub/AST-1963/AST-1965-timesheet-platform-columns` @ `7470f49c9` · platform columns tests ready

#### joan — 2026-10-04T02:20:19.263Z
[plan-rubric] PROCEED (Commit: 283783775) platform columns and totals

#### katherine — 2026-10-04T02:19:10.332Z
`origin/sub/AST-1963/AST-1965-timesheet-platform-columns` @ `283783775` · plan ready, two stages

---

# AST-1965 — Platform columns and platform-first totals on the timesheet

- **Ticket:** [AST-1965](https://linear.app/astralcareermatch/issue/AST-1965) · **Parent:** [AST-1963](https://linear.app/astralcareermatch/issue/AST-1963) Query LLM Platform for Timesheet Data to Finish Batch
- **Publish ref:** `sub/AST-1963/AST-1965-timesheet-platform-columns` (origin only)
- **Canon Scope:** `patt.entity.batch-processing`

`agent_timesheets` gains seven nullable platform columns: billed cost, the four native token counts, serving host, and reconcile time. A null `platform_cost` means "not reconciled". Existing databases get them through `_ensure_timesheets_schema`, new ones through `_create_agent_timesheets_table`; both read one column tuple. A new writer, `update_timesheet_platform`, sets those columns on one row by `agent_req_id` and touches nothing else. `_add_timesheet_entry` stops refusing a SKU the catalog doesn't price, but the server id check stays. `sum_cost_by_batch` counts each row's `platform_cost` when present and the sum of its `calc_cost_*` otherwise, so platform cost wins in every batch total that reads it (`dispatcher.get_dispatch_ledger`, `agent.py`). This ticket does **not** call OpenRouter (AST-1964, Hedy, already on ftr), start reconciles, refresh the ledger, or change `llm_compat` (AST-1966, Ada). It also does not change `calc_cost_*` math or `backfill_agent_timesheet_costs`.

## Scope gate

The only product file below is `src/data/database.py`, which this ticket's `## Scope` names. Every change is one of the kinds its Technical scope lists:
- new columns on `agent_timesheets`, added by `_ensure_timesheets_schema` and `_create_agent_timesheets_table`
- a new writer by `agent_req_id`
- a modified `_add_timesheet_entry` (unpriced SKU accepted, server check kept)
- a modified `sum_cost_by_batch` (platform cost preferred)

The module-docstring inventory line and the now-unused `get_sku_pricing` import are edits inside the same file that these changes force. `tests/component/data/database/test_timesheets.py` and `docs/test-bible/data/database/timesheets.md` are listed in Scope but belong to Betty (`qa-child`). No test-tree edits happen here.

## AC boundaries

| AC (child #) | Check | Closed here by | Closes on ftr after |
|----|-------|----------------|---------------------|
| 3 | `_add_timesheet_entry` with a SKU the catalog doesn't price returns `True` and the row exists | Stage 2 step 1 | The `llm_compat` half is AST-1966 |
| 4 | After the writer runs, the four `calc_cost_*` and the existing token columns are unchanged; the platform cost, native counts, host and timestamp equal what was written | Stage 1 steps 1–4 | — |
| 5 | Batch with a reconciled row (calc 0.01, platform 0.03) and an unreconciled row (calc 0.02): `sum_cost_by_batch` returns `0.05` | Stage 2 step 2 | — |
| Parent AC 1 grep | `rg -n '"openrouter"' src/data/database.py` returns nothing | Both stages' Done-when (no literal added) | — |

## Test impact (for Betty, `qa-child`)

- `TestAst1878TimesheetCatalogValidation::test_rejects_sku_not_priced_on_server` asserts `ValueError("Unknown SKU …")` for `claude-sonnet-4-6` on `deepseek` and `__no_sku__` on `anthropic`. This ticket deliberately reverses that (parent decision: "Unpriced rows get written"). Both calls will now return `True` and write a row. An **unknown server id** still raises `ValueError("Invalid timesheet provider …")`.
- `TestSumCostByBatch` keeps passing for rows with no platform cost (null `platform_cost` falls back to the calc sum).
- Tests that build a table from the old DDL and then call `_ensure_timesheets_schema` will see the seven columns appended. The `_timesheets_schema_ensured` reset already exists in the `data`, `core`, `ui` and `integration` conftests.

## Contract for AST-1966 (Ada): names used by the sibling

- `update_timesheet_platform(agent_req_id, platform_cost, native_tokens_prompt, native_tokens_completion, native_tokens_cached, native_tokens_reasoning, host) -> int` returns the number of rows updated (0 when `agent_req_id` matches nothing). It stamps `platform_reconciled_at` itself. Callers pass `get_generation_stats`' success dict field by field: `stats["total_cost"]`, `stats["native_tokens_prompt"]`, `stats["native_tokens_completion"]`, `stats["native_tokens_cached"]`, `stats["native_tokens_reasoning"]`, `stats["provider_name"]`.
- `sum_cost_by_batch(batch_ids)` keeps its signature and `{batch_id: total}` return. It is platform-first per row, so the closed-ledger refresh in AST-1966 just calls it again.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | `_AGENT_TIMESHEET_PLATFORM_COLUMNS` tuple; `_create_agent_timesheets_table` appends it; `_ensure_timesheets_schema` ALTERs missing ones; new `update_timesheet_platform`; `_add_timesheet_entry` drops the catalog-pricing gate (and the `get_sku_pricing` import); `sum_cost_by_batch` uses `COALESCE(platform_cost, calc sum)`; inventory docstring line for `agent_timesheets` | data |

## Stage 1: Platform columns and their writer

**Done when:** a fresh database and a pre-existing `agent_timesheets` table both have the seven platform columns. `update_timesheet_platform` sets them on one row and leaves every `calc_cost_*` and token column as inserted. Both commands below succeed, and `rg -n '"openrouter"' src/data/database.py` returns nothing.

```bash
ASTRAL_DB_DIR=$(mktemp -d) python3 -c "
import src.data.database as d
assert d._add_timesheet_entry('r1','t','claude-sonnet-4-6','c','b1',1,3,4,5,6,10,7,0.01,0.02,0.03,0.04,provider='anthropic')
assert d.update_timesheet_platform('r1',0.5,11,12,13,14,'DeepInfra')==1
assert d.update_timesheet_platform('nope',0.5,1,1,1,1,'x')==0
r=d.list_timesheets(batch_id='b1')[0]
assert (r['cache_write_tokens'],r['cache_read_tokens'],r['no_cache_prompt_tokens'],r['no_cache_live_tokens'],r['total_no_cache_input_tokens'],r['total_output_tokens'])==(3,4,5,6,10,7)
assert (r['calc_cost_cache_write'],r['calc_cost_cache_read'],r['calc_cost_no_cache_input'],r['calc_cost_output'])==(0.01,0.02,0.03,0.04)
assert (r['platform_cost'],r['native_tokens_prompt'],r['native_tokens_completion'],r['native_tokens_cached'],r['native_tokens_reasoning'],r['host'])==(0.5,11,12,13,14,'DeepInfra')
assert r['platform_reconciled_at']
"
ASTRAL_DB_DIR=$(mktemp -d) python3 -c "
import sqlite3, src.data.database as d
c=sqlite3.connect(':memory:'); c.row_factory=sqlite3.Row
c.execute('CREATE TABLE agent_timesheets (agent_req_id TEXT UNIQUE, created_at TIMESTAMP)')
c.execute('CREATE TABLE anthropic_timesheets (anthropic_req_id TEXT UNIQUE)')
d._ensure_timesheets_schema(c)
cols=[r[1] for r in c.execute('PRAGMA table_info(agent_timesheets)')]
assert cols[-7:]==[n for n,_ in d._AGENT_TIMESHEET_PLATFORM_COLUMNS], cols
"
```

1. **Column tuple.** In `src/data/database.py`, directly above `def _create_anthropic_timesheets_table`, add:

   ```python
   # AST-1965: platform-billed facts per call (OpenRouter generation stats). Nullable; platform_cost NULL = not
   # reconciled. Appended after created_at so new and migrated tables share one PRAGMA column order.
   _AGENT_TIMESHEET_PLATFORM_COLUMNS = (
       ("platform_cost",            "REAL"),
       ("native_tokens_prompt",     "INTEGER"),
       ("native_tokens_completion", "INTEGER"),
       ("native_tokens_cached",     "INTEGER"),
       ("native_tokens_reasoning",  "INTEGER"),
       ("host",                     "TEXT"),
       ("platform_reconciled_at",   "TIMESTAMP"),
   )
   ```

   ⚠️ **Decision:** The column names mirror the producer and the neighbouring table, so nothing needs translating. `native_tokens_*` are `get_generation_stats`' own keys. `host` matches `dispatch_ledger.host` (AST-1960, "served LLM host"). `platform_cost` / `platform_reconciled_at` say which source they come from. Rejected alternatives: `serving_host` / `provider_name` (a third name for the same fact) and a `platform_` prefix on the token columns (would rename the lookup's keys). No defaults: `NULL` is the "not reconciled" signal, and a `DEFAULT 0` would read as "platform billed $0".

2. **New tables.** In `_create_agent_timesheets_table`, change `conn.execute("""` to `conn.execute(f"""`. Change the `created_at` line from `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP` to `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,` and add directly below it, inside the parentheses:

   ```python
               {', '.join(f'{name} {col_def}' for name, col_def in _AGENT_TIMESHEET_PLATFORM_COLUMNS)}
   ```

   Use single quotes inside the braces exactly as shown. Same-quote nesting inside an f-string only parses on Python ≥ 3.12.

   Leave `_create_anthropic_timesheets_table` unchanged. The Anthropic mirror does not get platform columns (Scope names `agent_timesheets` only).

   ⚠️ **Decision:** Both paths read one tuple, so CREATE and ALTER cannot drift. Rejected alternative: spelling the seven columns literally in the CREATE as well (two copies to keep in sync).

3. **Existing tables.** In `_ensure_timesheets_schema`, directly after the block

   ```python
       if not _table_exists(conn, "agent_timesheets"):
           _create_agent_timesheets_table(conn)
           conn.commit()
   ```

   insert (same idiom as the `dispatch_ledger` migration list):

   ```python
       # AST-1965: platform columns on pre-existing agent_timesheets. DDL only — old rows stay NULL (unreconciled).
       existing = {row[1] for row in conn.execute("PRAGMA table_info(agent_timesheets)").fetchall()}
       for col, col_def in _AGENT_TIMESHEET_PLATFORM_COLUMNS:
           if col not in existing:
               conn.execute(f"ALTER TABLE agent_timesheets ADD COLUMN {col} {col_def}")
       conn.commit()
   ```

   The one-shot Anthropic backfill below it names its columns explicitly, so it stays as is.

4. **Writer.** Directly after `_add_timesheet_entry` (before `def backfill_agent_timesheet_costs`), add:

   ```python
   def update_timesheet_platform(
       agent_req_id: str,
       platform_cost: float,
       native_tokens_prompt: Optional[int],
       native_tokens_completion: Optional[int],
       native_tokens_cached: Optional[int],
       native_tokens_reasoning: Optional[int],
       host: Optional[str],
   ) -> int:
       """Set one agent_timesheets row's platform columns by agent_req_id; stamps platform_reconciled_at.
       Never touches calc_cost_* or the original token columns. Returns rowcount (0 when no row matches)."""
       def _with_conn() -> int:
           conn = _get_connection()
           try:
               _ensure_timesheets_schema(conn)
               cur = conn.execute(
                   """
                   UPDATE agent_timesheets
                   SET platform_cost = ?, native_tokens_prompt = ?, native_tokens_completion = ?,
                       native_tokens_cached = ?, native_tokens_reasoning = ?, host = ?,
                       platform_reconciled_at = ?
                   WHERE agent_req_id = ?
                   """,
                   (
                       platform_cost, native_tokens_prompt, native_tokens_completion,
                       native_tokens_cached, native_tokens_reasoning, host,
                       _utc_now(), agent_req_id,
                   ),
               )
               conn.commit()
               return cur.rowcount
           except Exception:
               conn.rollback()
               raise
           finally:
               conn.close()
       return _run_with_retry(_with_conn)
   ```

   ⚠️ **Decision:** Explicit positional parameters, not `**kwargs` plus an allowlist like `update_company`. This writer sets exactly one fixed column set, so an allowlist would only add lines. The writer stamps `platform_reconciled_at` with the module's `_utc_now()`, the same as every other writer here, so the caller doesn't supply a clock. It returns rowcount rather than a bool, the same as `update_company` / `update_agent`. A DB error raises after rollback, the same as `backfill_agent_timesheet_costs`. Catching it and logging is AST-1966's background handler's job.

5. **Inventory docstring.** In the module docstring, replace the `agent_timesheets` line with:

   ```
   - agent_timesheets — Unified token/cost ledger for all LLM providers: agent_req_id TEXT UNIQUE (vendor request id), same metric columns as anthropic_timesheets, plus nullable platform columns (AST-1965: platform_cost — NULL = not reconciled, native_tokens_prompt/_completion/_cached/_reasoning, host, platform_reconciled_at) set by update_timesheet_platform; sum_cost_by_batch prefers platform_cost per row.
   ```

6. `python3 -m py_compile src/data/database.py`, then run the two Done-when commands above.

## Stage 2: Unpriced SKUs recorded, platform-first totals

**Done when:** `_add_timesheet_entry` writes a row for a SKU the catalog doesn't price, but still raises on an unknown server id. `sum_cost_by_batch` returns `0.05` for the AC 5 batch. The command below succeeds, `rg -n "get_sku_pricing" src/data/database.py` returns nothing, and `rg -n '"openrouter"' src/data/database.py` returns nothing.

```bash
ASTRAL_DB_DIR=$(mktemp -d) python3 -c "
import pytest, src.data.database as d
assert d._add_timesheet_entry('u1','t','__no_sku__','c','bu',1,0,0,0,0,10,5,0.0,0.0,0.0,0.0,provider='anthropic') is True
assert [r['agent_req_id'] for r in d.list_timesheets(batch_id='bu')]==['u1']
with pytest.raises(ValueError, match='Invalid timesheet provider'):
    d._add_timesheet_entry('u2','t','x','c','bu',1,0,0,0,0,0,0,0.0,0.0,0.0,0.0,provider='__nope__')
assert d._add_timesheet_entry('a','t','claude-sonnet-4-6','c','b5',1,0,0,0,0,10,5,0.0,0.0,0.01,0.0,provider='anthropic')
assert d._add_timesheet_entry('b','t','claude-sonnet-4-6','c','b5',1,0,0,0,0,10,5,0.0,0.0,0.02,0.0,provider='anthropic')
assert d.sum_cost_by_batch(['b5'])['b5']==pytest.approx(0.03)
d.update_timesheet_platform('a',0.03,1,1,0,0,'DeepInfra')
assert d.sum_cost_by_batch(['b5'])['b5']==pytest.approx(0.05)
"
```

1. **Unpriced SKU accepted.** In `_add_timesheet_entry`, delete these three lines:

   ```python
       if model_code:
           # Ledger row must name a SKU the catalog prices on this server (raises ValueError otherwise).
           get_sku_pricing(model_code, provider)
   ```

   Keep the `if provider not in ALLOWED_TIMESHEET_PROVIDERS: raise ValueError(...)` check above them unchanged. Replace the function docstring with:

   ```python
       """Anthropic completions mirror into anthropic_timesheets + agent_timesheets; other providers use agent_timesheets only.
       Server id must be a catalog server (ValueError otherwise); the SKU need not be catalog-priced (AST-1965)."""
   ```

   Remove `get_sku_pricing,` from the `from src.utils.config import (...)` block at the top of the module (line 76 today). This was its only use in the file.

2. **Platform-first total.** In `sum_cost_by_batch`, replace the SELECT's sum expression

   ```sql
   SUM(calc_cost_cache_write + calc_cost_cache_read + calc_cost_no_cache_input + calc_cost_output) AS total
   ```

   with

   ```sql
   SUM(COALESCE(platform_cost, calc_cost_cache_write + calc_cost_cache_read + calc_cost_no_cache_input + calc_cost_output)) AS total
   ```

   and replace its docstring with `"""Return {batch_id: total_cost} for the given batch IDs — per row, platform_cost when reconciled, else the calc_cost_* sum."""`.

   ⚠️ **Decision:** Prefer platform cost per row inside the SQL with `COALESCE`, not by fetching rows and summing in Python. One statement keeps the existing signature, grouping and callers (`dispatcher.get_dispatch_ledger`, `agent.py`) untouched. Rejected alternatives: a separate "platform total" function (callers would have to choose, and the parent decision says platform wins in **every** total), and a SQL view (a new schema object Scope doesn't name).

3. `python3 -m py_compile src/data/database.py`, then run the Done-when command and both `rg` checks.

## Execution contract

The plan is binding. Run steps in order within each stage, and stages in order. Do not add files, columns, functions or dependencies that aren't listed here. If a step is ambiguous, a referenced line has drifted, or a Done-when command fails when run literally: stop, post `🛑 Stage N blocked: …` on [AST-1963](https://linear.app/astralcareermatch/issue/AST-1963), and wait. Each stage ends in one `code(AST-1965): …` commit on the epic worktree, published with `git push origin HEAD:sub/AST-1963/AST-1965-timesheet-platform-columns`.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1965
**Overall:** APPROVED
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Publish ref:** `sub/AST-1963/AST-1965-timesheet-platform-columns` @ `283783775`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-processing | A | | |

## Traceability

AC3→Stage 2 step 1 (`_add_timesheet_entry` / unpriced SKU); AC4→Stage 1 steps 1–4 (`update_timesheet_platform` + schema); AC5→Stage 2 step 2 (`sum_cost_by_batch` COALESCE). Parent AC 1 grep boundary noted in plan AC table; AC 4–8 and reconcile/ledger work correctly deferred to AST-1966.

## Findings

### acceptable — Definition fidelity

- **Location:** Scope gate / Boundaries (plan intro)
- **Finding:** Single product file `database.py`; no OpenRouter calls, reconcile, `llm_compat`, or ledger refresh; matches child `## Scope` and parent partition for ticket #2.
- **Recommendation:** None.

### acceptable — Sibling contract

- **Location:** `## Contract for AST-1966`
- **Finding:** Writer signature, rowcount semantics, `platform_reconciled_at` ownership, and field mapping from `get_generation_stats` align with AST-1964 contract and parent Technical scope.
- **Recommendation:** None.

### acceptable — Betty handoff

- **Location:** `## Test impact`
- **Finding:** Explicit reversal of `test_rejects_sku_not_priced_on_server` expectations and schema-reset note for conftests — appropriate for qa-child, not a plan gap.
- **Recommendation:** None.

### discuss — Canon Scope gap (not scored)

- **Location:** Stage 2 step 2 (`sum_cost_by_batch`)
- **Finding:** `stat.data.batch-id-first` may govern batch-keyed reads/writes in data; parent locked only `patt.entity.batch-processing` for this child. Plan still honors batch_id grouping and existing callers (`dispatcher`, `agent.py`).
- **Recommendation:** Archie may amend Canon Scope at Discussion if batch-id-first enforcement is desired on this pass; not required to proceed.

### acceptable — Implementation binding

- **Location:** Stage 1 step 2 (f-string CREATE)
- **Finding:** Python ≥3.12 nested-quote note matches CI (`python-version: '3.12'`) and existing f-string DDL in `database.py`.
- **Recommendation:** None.

context_tokens≈42000

`[plan-rubric] PROCEED (Commit: 283783775) platform columns and totals`

## Review

- **Branch:** `sub/AST-1963/AST-1965-timesheet-platform-columns`
- **Build commits:** `2c63ad738` (Stage 1 platform columns + `update_timesheet_platform`) · `eaf0bec10` (Stage 2 unpriced SKU + platform-first `sum_cost_by_batch`)
- **Build notes:** Both stages executed as written, and every Done-when command passed. Neither the `rg -n '"openrouter"'` check nor the `rg -n "get_sku_pricing"` check on `src/data/database.py` finds anything. `py_compile` is clean; no Python linter is installed on this host. The INSERT/UPDATE re-audit is clean: every `agent_timesheets` insert/update names its columns, so appended columns don't shift any `?` tuple. `test_timesheets.py` run: 7 passed, 1 failed. The failure is `TestAst1878TimesheetCatalogValidation::test_rejects_sku_not_priced_on_server`, the expected reversal flagged in § Test impact. `validate-sub-log.sh --stage=build`: ok. Edits were applied by a shell script with exact one-match string replacement, because `.cursorignore`'s `data/` pattern also matches `src/data/` and blocks the IDE edit tools on `database.py`. The content is exactly the plan's. No deviations.

## Radia review

[code-rubric]
**Ticket:** AST-1965
**Publish ref:** `7470f49c92a7ebb67932b650e0b3899e4fcc1873` (`origin/sub/AST-1963/AST-1965-timesheet-platform-columns`)
**Corpus:** e1f2699fad44e4083e39a9a066cc87cae494ad51
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-processing | A | | |

## Column diff vs plan stage

(aligned) — Joan **A** on `patt.entity.batch-processing`; code review **A** on the same id.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Sibling stacked ref:** `origin/dev...origin/sub/AST-1963/AST-1965-timesheet-platform-columns` also carries AST-1964 product/tests/docs (`config.py`, `openrouter.py`, `test_config.py`, `test_openrouter.py`, AST-1964 plan/review). Expected sub-branch stacking / `merge-tests`, not AST-1965 scope creep. **This review’s plan fidelity and canon pass target Katherine’s `database.py` + timesheet tests** (`2c63ad738`, `eaf0bec10`, `060a9a8dd`).
- **Canon Scope (off-list, not scored):** Joan flagged `stat.data.batch-id-first` at plan for `sum_cost_by_batch`; frozen list is only `patt.entity.batch-processing`. Implementation keeps `batch_id IN (...)` grouping and caller contract. **Default:** unchanged — no resolve-child change unless Archie adds the statute at Discussion.
- **Plan fidelity:** Stage 1–2 match issue doc — `_AGENT_TIMESHEET_PLATFORM_COLUMNS`, shared CREATE/ALTER paths, `update_timesheet_platform` (rowcount, `_utc_now()` stamp, no calc/token touch), SKU gate removed with server check kept, `COALESCE(platform_cost, calc sum)` in `sum_cost_by_batch`, `get_sku_pricing` import removed.
- **AC grep:** `'"openrouter"'` and `get_sku_pricing` absent from `src/data/database.py` on tip.
- **SQL bind audit (`update_timesheet_platform`):** seven `SET` placeholders + `WHERE agent_req_id = ?` matches eight-value bind tuple (cost, four natives, host, reconciled_at, id). INSERT path unchanged column list per build notes.
- **Estimate:** Confirm **2** — single product file + Betty tests/bible fits.
- **Betty:** `test_rejects_sku_not_priced_on_server` reversed per plan § Test impact; AC 3 db half, AC 4/5, migration/idempotency, and `platform_cost = 0.0` COALESCE edge covered in `test_timesheets.py`.

## What's solid

- Platform columns nullable with shared tuple for CREATE and ALTER — no drift between new and migrated DBs.
- Writer isolation preserves calc and legacy token columns; Ada contract (`update_timesheet_platform` signature, field mapping, rowcount) matches plan § Contract for AST-1966.
- `sum_cost_by_batch` implements parent “platform wins” per row while preserving batch-keyed aggregation (`patt.entity.batch-processing` audit/cost section).

## Recommended actions (downstream — not for Radia)

- Chuckles: append artifact, `docs(AST-1965): Radia review — clean`, post slim upshot `--as radia`, **Review Posted** → datt **PROCEED** to **User Testing** (no resolve-child for canon).
- When merging siblings on ftr, ensure AST-1964 and AST-1965 reviews both posted before UT rollup — ref already contains both children’s code.

context_tokens≈38000

`[code-rubric] PROCEED (Commit: 7470f49c9) platform columns and totals`
