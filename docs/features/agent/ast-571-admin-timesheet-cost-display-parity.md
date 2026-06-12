# AST-571 — Admin timesheet cost display parity

**Parent:** [AST-569 — Timesheets for deepseek are inaccurate](https://linear.app/astralcareermatch/issue/AST-569/timesheets-for-deepseek-are-inaccurate)  
**Ticket:** [AST-571](https://linear.app/astralcareermatch/issue/AST-571/admin-timesheet-cost-display-parity-timesheets-for-deepseek-are-inaccurate)  
**Publish ref (origin):** `sub/AST-569/AST-571-admin-timesheet-cost-display`  
**Blocked by:** [AST-570](https://linear.app/astralcareermatch/issue/AST-570/deepseek-cost-math-mapping-and-backfill-timesheets-for-deepseek-are) (pricing/backfill on sibling sub ref)

After **AST-570** lands corrected `calc_cost_*` on DeepSeek rows, this ticket makes **Admin Agent Timesheets** (UI + CSV), **Execution History** batch cost, and **Batch Agent Data** modal totals all use one authoritative row total: the sum of the four stored `calc_cost_*` fields. No alternate formulas, no token-derived estimates, no changes to pricing math.

**Out of scope:** `DEEPSEEK_MODEL_PRICING`, usage mapping, backfill SQL (**AST-570**). Anthropic recording paths except regression-safe shared display helper.

## Authoritative row total (single formula)

For any timesheet row dict (API JSON, CSV enrichment, or TS row):

```
total_cost = calc_cost_cache_write + calc_cost_cache_read + calc_cost_no_cache_input + calc_cost_output
```

Treat missing/`None` as `0.0` before add. Do **not** sum token columns for dollars. Do **not** read `dispatch_ledger.total_cost` column in the DB for display — Execution History already overwrites with `sum_cost_by_batch` (same SQL sum as above).

⚠️ **Decision:** Python owns the canonical helper; API adds `total_cost` on every timesheet payload so CSV and JSON share one enrichment path; frontend uses API `total_cost` when present and falls back to the same four-key sum for tests/mocks.

### Parent acceptance anchor (AC 7)

For sampled DeepSeek rows after backfill (parent Original brief pro rows, e.g. `840f7662-a5de-44cd-ac2e-09fade0aca81`), UI row total and CSV `total_cost` must equal:

`calc_cost_cache_write + calc_cost_cache_read + calc_cost_no_cache_input + calc_cost_output`

from the API response (within display rounding: four decimal places in UI via existing `formatCell` / `fmtCost`).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/cost_calculator.py` | Add `CALC_COST_KEYS` tuple and `sum_calc_cost_components(row: dict) -> float`. | utils |
| `src/ui/api/api_admin.py` | `_enrich_timesheet_row(row)`; apply in `list_timesheets_all` and `export_timesheets_csv`; add `total_cost` to `_TIMESHEET_CSV_COLUMNS` and `_TIMESHEET_COLUMNS`. | ui |
| `src/ui/frontend/src/lib/timesheetCost.ts` | `CALC_COST_KEYS`, `sumCalcCostComponents(row)` — mirror Python keys. | ui |
| `src/ui/frontend/src/pages/AdminAgentTimesheets.tsx` | Import lib; add `total_cost` column; totals use `row.total_cost ?? sumCalcCostComponents(row)`. | ui |
| `src/ui/frontend/src/components/BatchAgentDataModal.tsx` | Replace inline cost sum with `sumCalcCostComponents`. | ui |
| `tests/component/utils/test_cost_calculator.py` | `TestSumCalcCostComponents` — zeros, partial None, parent brief pro row sample. | tests |
| `tests/component/ui/api/test_api_admin.py` | Extend `TestTimesheets` — assert `total_cost` on list + CSV. | tests |
| `tests/component/frontend/pages/test_AdminAgentTimesheets.test.tsx` | Assert `$ Total` column and footer cost matches sum of four components. | tests |
| `tests/component/ui/api/test_api_admin.py` or `tests/component/core/test_dispatcher.py` | `TestAst571LedgerCostUsesTimesheetSum` — ledger `total_cost` equals mocked `sum_cost_by_batch`. | tests |
| `docs/ASTRAL_TEST_BIBLE.md` | §7.13zza manifest (Betty adds in qa-astral). | docs |

## Pre-build integration (mandatory)

**Done when:** `dev-kath` has merge-clean gate vs `origin/dev` and includes **AST-570** product commits needed for meaningful DeepSeek parity checks.

1. On `dev-kath`: `git fetch origin && git merge origin/dev` (re-check `BEHIND=0`, `origin/dev` ancestor of `HEAD`).
2. `git merge origin/sub/AST-569/AST-570-deepseek-cost-math-mapping-backfill` (or `origin/ftr/ast-569-timesheets-deepseek-cost` if sibling already rolled up). Resolve conflicts only in files this ticket owns; commit merge on `dev-kath` if needed.
3. `git merge origin/sub/AST-569/AST-571-admin-timesheet-cost-display` before each publish commit (plan already on publish ref after plan-astral).

Do **not** change `src/external/deepseek.py`, `src/utils/config.py` pricing blocks, or `backfill_deepseek_agent_timesheet_costs` except merge conflict resolution that preserves **AST-570** behavior.

## Stage 1: Shared sum helper (Python)

**Done when:** `sum_calc_cost_components` is importable; unit test proves parent brief row `840f7662-…` total matches sum of four CSV cost fields.

1. In `src/utils/cost_calculator.py`, after existing cost helpers, add:

```python
CALC_COST_KEYS = (
    "calc_cost_cache_write",
    "calc_cost_cache_read",
    "calc_cost_no_cache_input",
    "calc_cost_output",
)

def sum_calc_cost_components(row: dict) -> float:
    """Row total spend from stored calc_cost_* only."""
```

   Implementation: `return sum(float(row.get(k) or 0) for k in CALC_COST_KEYS)`.

2. In `tests/component/utils/test_cost_calculator.py`, add class `TestSumCalcCostComponents`:
   - `test_empty_keys_zero`
   - `test_parent_brief_pro_row_840f7662` using literals from AST-569 description: `0.0`, `0.000311808`, `0.0071166`, `0.03751092` → expect `≈ 0.044939528` (use `pytest.approx`).

## Stage 2: Admin API enrichment + CSV column

**Done when:** `GET /api/admin/timesheets` and `GET /api/admin/timesheets/export` return each row with `total_cost` equal to `sum_calc_cost_components(row)`; CSV header includes `total_cost` after `calc_cost_output`.

1. In `src/ui/api/api_admin.py`, import `sum_calc_cost_components` from `src.utils.cost_calculator`.
2. Add:

```python
def _enrich_timesheet_row(row: dict) -> dict:
    out = dict(row)
    out["total_cost"] = sum_calc_cost_components(row)
    return out
```

3. In `list_timesheets_all`, after `rows = list_timesheets(...)`, set `rows = [_enrich_timesheet_row(r) for r in rows]` before `req_dict` branch and plain `jsonify`.
4. In `export_timesheets_csv`, same enrichment before `writer.writerows`.
5. Append `"total_cost"` to `_TIMESHEET_CSV_COLUMNS` immediately after `"calc_cost_output"`.
6. Append to `_TIMESHEET_COLUMNS`: `{"key": "total_cost", "label": "Total Cost", "type": "currency"}` after the four component cost columns.
7. In `tests/component/ui/api/test_api_admin.py`, class `TestTimesheets::test_list_and_export_timesheets`:
   - Change mock row to use `agent_req_id` (not `anthropic_req_id`) and non-zero `calc_cost_*`.
   - Assert `plain.get_json()[0]["total_cost"] == pytest.approx(0.1)` when components sum to `0.1`.
   - Assert exported CSV text contains header `total_cost` and data row includes formatted total.

## Stage 3: Frontend timesheet page + shared TS helper

**Done when:** Agent Timesheets table shows **$ Total** column; footer **Cost:** matches sum of displayed row totals; export unchanged (server CSV already has `total_cost`).

1. Create `src/ui/frontend/src/lib/timesheetCost.ts`:

```typescript
export const CALC_COST_KEYS = [
  "calc_cost_cache_write",
  "calc_cost_cache_read",
  "calc_cost_no_cache_input",
  "calc_cost_output",
] as const

export function sumCalcCostComponents(row: Record<string, unknown>): number {
  return CALC_COST_KEYS.reduce((s, k) => s + (Number(row[k]) || 0), 0)
}

export function rowTotalCost(row: Record<string, unknown>): number {
  const t = row.total_cost
  return typeof t === "number" && !Number.isNaN(t) ? t : sumCalcCostComponents(row)
}
```

2. In `AdminAgentTimesheets.tsx`:
   - Import `rowTotalCost`, `sumCalcCostComponents`.
   - Add interface field `total_cost?: number`.
   - Replace `totalCost(r)` body with `return rowTotalCost(r)`.
   - Insert column after `calc_cost_output`: `{ key: "total_cost", label: "$ Total", type: "currency" }`.
   - In `sum()` reducer, use `rowTotalCost(r)` instead of `totalCost(r)`.
3. In `BatchAgentDataModal.tsx`, import `sumCalcCostComponents`; in `sumTimesheets`, keep per-component accumulators; set `totalCost` line to `rows.reduce((s, r) => s + sumCalcCostComponents(r), 0)` instead of summing four accumulator fields (equivalent but single formula).
4. In `tests/component/frontend/pages/test_AdminAgentTimesheets.test.tsx`:
   - Add `total_cost: 0.1` to mock row (sum of `0.01+0.02+0.03+0.04`).
   - Assert `screen.getByText("$0.1000")` or matching formatted total in totals bar after load.
   - Assert table header **$ Total** present (`getByRole("columnheader", { name: "$ Total" })`).

## Stage 4: Execution History parity test (no product change expected)

**Done when:** Component test documents that `list_dispatch_ledger` sets `total_cost` from `sum_cost_by_batch` (already implemented in `src/core/dispatcher.py`).

1. Do **not** edit `AdminPerformanceMonitor.tsx` unless test proves `total_cost` missing from API (it should not).
2. In `tests/component/ui/api/test_api_admin.py` (class `TestDispatchLedger`) or new class `TestAst571DispatchLedgerCostParity`:
   - Monkeypatch `admin_mod.list_dispatch_ledger` to return `[{"batch_id": "b-deep", "total_cost": 0.044939528}]`.
   - Monkeypatch is unnecessary if testing dispatcher: prefer `tests/component/core/test_dispatcher.py` with monkeypatch on `_db_list_dispatch_ledger` returning one row and `_db_sum_cost_by_batch` returning `{"b-deep": 0.044939528}`; call `dispatcher.list_dispatch_ledger()`; assert `rows[0]["total_cost"] == 0.044939528`.
3. Add one-line comment in `src/core/dispatcher.py` above `r["total_cost"] = costs.get(...)`:

   `# Display total matches sum of agent_timesheets calc_cost_* (AST-571).`

## Stage 5: Manual UAT script (Susan)

**Done when:** Comment on **AST-571** with pass/fail after **AST-570** backfill on shared DB.

1. Open **Admin → Agent Timesheets**, filter `date_from=2026-06-03`, `date_to=2026-06-03`, `model_code=deepseek-v4-pro`.
2. For row `840f7662-a5de-44cd-ac2e-09fade0aca81`, confirm **$ Total** equals sum of four **$** component columns (four decimal places).
3. Export CSV; confirm `total_cost` column equals same value for that row.
4. Open **Execution History**, locate batch `draft_job_resume-f017d456-6ccb-4f90-82cc-364e1ec92c9f` (batch_id from parent CSV); confirm header total cost equals sum of timesheet rows for that batch (Batch Agent Data modal totals bar cross-check optional).

## Self-Assessment

**Scope:** `Single-Component` — Touches one admin API surface, two frontend pages, one shared TS lib, and a small pure Python helper; no schema or pricing changes.

**Conf:** `high` — Formula is fixed in parent AC 7 and already used in SQL `sum_cost_by_batch`; work is wiring and regression tests, dependent on **AST-570** data being correct.

**Risk:** `Medium` — Wrong display erodes spend trust, but blast radius is admin read paths only; Anthropic rows use the same sum and must stay unchanged in tests.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Plan compliance |
|------|-----------------|
| §1.3 DRY | Single `sum_calc_cost_components` / `sumCalcCostComponents`; API enrichment once. |
| §2.1 config | No new config keys. |
| §3.3 imports | `api_admin` imports `utils.cost_calculator` only (allowed ui→utils). |
| §3.5 naming | Page stays `AdminAgentTimesheets.tsx` in `pages/`; new helper in `lib/timesheetCost.ts`. |
| §3.6 spikes | No spike output; UAT uses live admin UI. |

No `conf-!!-NONE` conflicts.

## Execution contract

- Build **after** **AST-570** is on `dev-kath` (merge sibling sub ref in Pre-build).
- Stages 1→5 in order; one commit per stage on `dev-kath`; Joan `store-code-commit` to `origin/sub/AST-569/AST-571-admin-timesheet-cost-display` with `--session bae3ad87-8192-493e-9129-cf664a9afad5`.
- If API returns `total_cost` that disagrees with hand-sum of four components for a backfilled DeepSeek row, **stop** and comment on **AST-571** — do not patch pricing (**AST-570**).

## Review (build)

**Branch:** `origin/sub/AST-569/AST-571-admin-timesheet-cost-display`  
**Tip:** `4895fa848c59a0d4bc0e1cba23433037b616bc35` (Joan store-code-commit after stage 4)

**Stages shipped (product):**
1. `sum_calc_cost_components` + `CALC_COST_KEYS` in `src/utils/cost_calculator.py` (`a666d9fa` on publish ref `7953e0a8` ancestry)
2. `api_admin.py` — `_enrich_timesheet_row`, list/export `total_cost`, CSV/column metadata
3. `timesheetCost.ts`, `AdminAgentTimesheets.tsx`, `BatchAgentDataModal.tsx` — UI parity with API field
4. `dispatcher.py` — AST-571 comment on ledger `total_cost` assignment (behavior unchanged)

**Tests:** Betty at Code Complete (`qa-astral`) per plan Stages 2–4 component tests.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-569/AST-571-admin-timesheet-cost-display` (tip `af32280b`). AST-571-only commits after `merge(AST-570)` @ `8e959c5c` reviewed for plan fidelity.

### What's solid

- **AC 7 formula:** `sum_calc_cost_components` / `CALC_COST_KEYS` in `src/utils/cost_calculator.py`; API `_enrich_timesheet_row` on list + CSV; `timesheetCost.ts` mirrors keys; `AdminAgentTimesheets` footer and `$ Total` column use `rowTotalCost`; `BatchAgentDataModal` batch bar sums per-row via `sumCalcCostComponents` on enriched API rows.
- **Execution History:** No product change; `list_dispatch_ledger` already uses `sum_cost_by_batch` (SQL sum of four `calc_cost_*`). AST-571 comment + `test_ast571_ledger_total_cost_matches_timesheet_sum` document parity.
- **Layers (§3.3):** `api_admin` adds only `utils.cost_calculator` import; no new `data`/`external` from UI.
- **Scope (§5d):** AST-571-only diff does not edit pricing, DeepSeek mapping, or backfill — sibling **AST-570** present only via documented merge base.

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| discuss | `tests/component/core/test_dispatcher.py` `test_ast571_ledger_total_cost_matches_timesheet_sum` | Mock total `0.044939528` vs `test_parent_brief_pro_row_840f7662` sum `0.044939328` from parent CSV literals (~2e-7). Display paths use the same four-key sum; align test constant in **resolve-astral** if you want one golden value. |

### Recommended actions

| Action | Owner |
|--------|-------|
| Optional: set ledger test mock to `pytest.approx(0.044939328)` to match `TestSumCalcCostComponents::test_parent_brief_pro_row_840f7662` | Katherine / resolve-astral |
| Run plan Stage 5 manual UAT on backfilled DeepSeek rows after **AST-570** lands on shared DB | Susan |

## Resolution (2026-06-03)

**Radia review:** No fix-now items. Discuss item (ledger test mock `0.044939528` vs cost-calculator golden `0.044939328`, ~2e-7) reviewed — display paths use the same four-key sum; delta is test-fixture only, not a product defect. Left unchanged per resolve-astral §9 (no test-tree commits on resolve pass).

**Publish:** Resolution doc commit via Joan `store-resolve-commit` to `origin/sub/AST-569/AST-571-admin-timesheet-cost-display`.
